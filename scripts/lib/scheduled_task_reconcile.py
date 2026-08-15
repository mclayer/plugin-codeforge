#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# scheduled_task_reconcile.py — 로컬 스케줄 작업 reconcile CLI (관측 → dedup → 채널 발화)
#
# Carrier: CFP-2949 Phase 2 (구현) — Routines/스케줄 작업 채택.
#
# ── 소유 범위 (전 과정 단일 소유) ──────────────────────────────────────────────────
#   스캐너 observe-only 호출 → dedup 키 유도 → 보고 채널 조회 → 신규분 필터
#     → 사실 3-tuple + sentinel + trailer 렌더 → 보고 채널 발화 → heartbeat 기록
#   ★ 발화(GitHub 코멘트 append)까지 본 CLI 가 소유한다. LLM 세션은 채널에 쓰지 않는다.
#
# ── 비협상 불변식 ────────────────────────────────────────────────────────────────
#   INV-A  삭제 0 — 본 모듈은 어떤 삭제 코드경로도 진입하지 않는다.
#          · discovery = discover→classify→judge 3단만 (run_scan/execute 미호출).
#          · scratch-ttl = GC_DRY_RUN=1 강제 후 run() (호출시점 판독 L146 — 실 삭제 미도달).
#          · temp = observe_temp() 만 (main()/_stage2_delete 미호출).
#          os.remove/shutil.rmtree/safe_remove 직접 호출 0.
#   INV-B  상태 무의존 reconcile — 대상은 g(현재 상태)이지 f(tick)이 아니다. 매 실행이
#          현재 잔재 전량을 재관측한다. cursor·watermark·"이 tick 담당 구간" 개념 부재.
#   INV-C  dedup 상태 저장소 = append-only 보고 채널 자신. 로컬 dedup 상태 파일 0
#          (그 파일이 자기 잔재가 되는 자기참조 회피). 키는 저장 아닌 대상에서 유도.
#   INV-D  읽기 표면 축소 — 채널에서 취하는 것 = 코멘트 메타데이터 + 자기 마커 코멘트의
#          key 라인 매치분뿐. 마커 미매치 코멘트 본문은 그 자리에서 폐기. 외부 저작
#          문자열이 산출에 도달하는 경로 0 (키 집합은 멤버십 판정에만 쓰이고 출력 0).
#   INV-E  verdict 어휘 0 — 산출(본문·DONE·stderr)은 `선언값 · 실측값 · 불일치` 사실만.
#          하위 스크립트 출력의 verdict 어휘 줄은 인용 금지, 수치 필드만 재서술.
#   INV-F  exit code 항상 0 — exit code 를 성공/실패 신호로 쓰지 않는다(advisory).
#
# ── 정직 천장 (ADR-119 / ADR-168 §결정 16 Layer 1) ─────────────────────────────────
#   본 모듈 정규식은 리터럴 alternation + anchor + 단일 라인 대상으로 작성하나,
#   임의·적대적 입력에 대한 무해성을 단정하지 않는다("ReDoS-safe" 무증거 단정 금지).
#   보장 = bounded degradation (임의 입력 무해 아님). 실증 = 보안테스트 lane 복잡도 self-test.

from __future__ import annotations

import argparse
import contextlib
import hashlib
import io
import json
import os
import re
import shlex
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

# 사이블링 import 를 위한 self-dir path 보정 (thin-wrapper 이외 호출 경로 방어).
_SELF_DIR = os.path.dirname(os.path.abspath(__file__))
if _SELF_DIR not in sys.path:
    sys.path.insert(0, _SELF_DIR)

# Windows cp949 stdout/stderr 인코딩 차단 (ADR-061 portability — lib/ 관용).
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# 재사용 자산 (ADR-140 reuse-before-write — 경로 정규화/redaction/git 포트/스캐너 재구현 0).
import check_orphan_worktree_classify as base            # noqa: E402  경로·redaction·age·git 포트
import check_workspace_residue_discovery as discovery    # noqa: E402  discover/classify/judge
import check_harness_temp_residue as temp_axis           # noqa: E402  observe_temp (삭제 0)
import check_codeforge_scratch_ttl as scratch_axis       # noqa: E402  run() (GC_DRY_RUN=1 강제)


# ═══════════════════════════════ 계약 상수 ═══════════════════════════════════════
SCRIPT_NAME = "scheduled-task"
SENTINEL = "[scheduled-task-observe]"          # 고정 sentinel prefix (마커 1종)
TRAILER = "[scheduled-task-run]"               # 태스크·run 참조 trailer (마커 2종)
VERDICT_LEXICON = ("PASS", "FAIL", "OK", "정상", "문제없음")

GC_STATE_DIR = os.path.join(os.path.expanduser("~"), ".claude", "worktree-gc-state")
HEARTBEAT_FILE = os.path.join(GC_STATE_DIR, "scheduled-task-last-run.epoch")
STOP_FLAG_LOCAL = os.path.join(GC_STATE_DIR, "scheduled-task.disabled")      # F2
STOP_FLAG_REPO_RELPATH = os.path.join(".codeforge", "post-merge-automation.disabled")  # F1
GH_BIN_ENV = "STR_GH_BIN"      # 단일 바이너리 또는 공백분리 명령 (stub 주입 — DIR_GH_BIN 선례)

# env fallback 키 (CLI 인자 부재 시).
ENV_CHANNEL = "SCHEDULED_TASK_CHANNEL"
ENV_TASK_NAME = "SCHEDULED_TASK_NAME"
ENV_RUN_ID = "SCHEDULED_TASK_RUN_ID"

# heartbeat 경로 override 키 — **테스트 격리 seam**(신규 기능 아님).
#   HEARTBEAT_FILE 은 import 시점 expanduser("~") 로 확정되므로 HOME override 로는 격리 불가.
#   subprocess 로 CLI 를 호출하는 테스트가 실 사용자 상태를 오염시키지 않도록 이 키를 준다.
ENV_HEARTBEAT_FILE = "SCHEDULED_TASK_HEARTBEAT_FILE"

# 1회 발화 본문에 싣는 사실 줄 상한 (코멘트 크기 bound). 초과분은 무손실 —
#   다음 실행이 현재 상태를 재관측해 남은 신규분을 발화한다(INV-B 상태 무의존 자기치유).
MAX_FACT_LINES = 50

# gh 서브프로세스 timeout (초) — base._gh(30) 대비 채널 왕복 여유.
GH_TIMEOUT = 60

# dedup 키 길이 상한 (INV-D 읽기 표면 축소 — 비정상 장문 폐기).
#   ★ **대칭 적용**(D3 라운드트립): 역추출(fetch_existing_keys)에서만 상한을 걸면 상한
#     초과 키는 채널에 실려도 절대 재수집되지 않아 **매 실행 중복 발화**가 된다(무한 재발화).
#     그래서 정방향 렌더(dedup_key)도 같은 상한을 지켜 **경계화한 키**를 발화한다.
_MAX_KEY_LEN = 512
_KEY_BOUND_PREFIX = 480        # 경계화 키의 앞부분 보존 길이 (식별 가독성 유지)
_KEY_BOUND_DIGEST = 8          # 전체 키 sha256 앞 8-hex (앞부분 동일 장문 구별)

# 보존 사유 중 "규약이 기대하는 상태"(= 불일치 아님)로 계산하는 enum.
#   unregistered-location / None 은 정당 사유가 아니다(잔존 자체가 규약 이탈 신호).
_JUSTIFIED_REASONS = frozenset({
    "pin", "locked", "dirty", "network-inconclusive", "temp-git-worktree",
})


# ═══════════════════════════════ 정규식 ═══════════════════════════════════════════
# verdict 어휘 검출 — ASCII 토큰은 word-boundary(부분어 오탐 회피: passport/okay 미매치),
#   비-ASCII(한글)는 단어 경계 개념 부재라 substring. 리터럴 alternation(중첩 quantifier 0).
#   정직 천장: bounded degradation 보장이지 임의 입력 무해 단정 아님(ADR-168 §결정 16).
_ASCII_LEXICON = tuple(t for t in VERDICT_LEXICON if t.isascii())
_NONASCII_LEXICON = tuple(t for t in VERDICT_LEXICON if not t.isascii())
_LEXICON_RE = re.compile(
    "|".join(
        ([r"\b(?:%s)\b" % "|".join(re.escape(t) for t in _ASCII_LEXICON)] if _ASCII_LEXICON else [])
        + [re.escape(t) for t in _NONASCII_LEXICON]
    ),
    re.IGNORECASE,
)
# ── verdict 어휘 변환: **손실 삭제 → 무손실 가역 이스케이프** (구현리뷰 iter5 F-CR5-03) ──
#   구판은 매치 토큰을 `<제거>` 로 **삭제 치환**했다. 이 변환은 단사가 아니라서
#   `…/cfp-100-pass` 와 `…/cfp-100-fail` 이 **같은 문자열**(`…/cfp-100-<제거>`)로 붕괴했고,
#   `_safe_text` 가 `dedup_key` 에도 걸리므로 두 잔재가 **한 키**를 공유해 한쪽이 영구
#   억제됐다(공격자 없이 경로 문자열만으로 성립하는 런타임 결함). 표시 축도 같이 뭉개져
#   운영자가 잔재 위치를 특정할 수 없었다.
#
#   식별 축과 표시 축을 **분리하지 않는다** — 분리하면 D3 라운드트립 계약(키가 채널 본문에
#   실려 `fetch_existing_keys` 가 되추출)이 깨진다. 대신 변환 자체를 무손실로 바꾼다.
#
#   변환 규칙 (2단, 결정론):
#     ① 이스케이프 도입자 자신을 먼저 이스케이프: `%` → `%%`
#     ② 매치 토큰의 첫 글자와 나머지 사이에 `%-` 삽입: `PASS` → `P%-ASS` / `정상` → `정%-상`
#   성질:
#     (a) **단사** — `unscrub_verdict_tokens` 가 좌역원이다(왕복 property 검사로 결박).
#     (b) **구성상 lexicon-free** — ②가 모든 매치를 쪼개고, ①②는 문자를 **삽입만** 하므로
#         새 substring 매치를 만들 수 없다. ASCII 토큰의 `\b` 경계도 새로 만들지 못한다:
#         삽입된 `%`·`-` 는 토큰 첫 글자 **바로 뒤**에 오는데, 어느 토큰도 `[1:]` 가
#         다른 토큰으로 시작하지 않는다(ASS/AIL/K/상/제없음).
#     (c) **결정론** — 정규식 스캔 순서만으로 결정된다(상태·난수 0).
#   대가 (선언 — 은폐 금지):
#     · 도입기 채널의 기존 키 중 어휘를 포함하던 것은 **1회 바뀌어 그 항목이 1회 재발화**한다
#       (`_MAX_KEY_LEN` 경계화 도입 때와 동형 대가, 도입기 채널 이력이 사실상 비어 수용).
#     · 영향 경로의 가독성이 소폭 떨어진다(`cfp-100-p%%-ass`). 단 **위치 특정은 가능**해졌다 —
#       구판은 `<제거>` 라 어떤 어휘였는지조차 복원 불가였다.
#     · `_safe_text` 가 scrub 를 sanitize 앞뒤로 **두 번** 걸므로 `%` 가 두 번 escape 돼
#       `%%-` 형태가 된다(합성도 단사이므로 계약은 유지, 되돌리려면 unscrub 2회).
#   실측 확인: `base.sanitize` 는 `%`·`-` 를 재변형하지 않는다(9 케이스 왕복 동일 — 확인 안
#   됐다면 이 방식을 쓰지 않고 키 해시 접미 폴백으로 갔어야 한다).
_ESC_CHAR = "%"
_ESC_DOUBLED = "%%"
_LEXICON_ESCAPE = "%-"

# ── 마크다운 무해화 (보안테스트 F-SEC-4 — 방어심층) ────────────────────────────────
#   실측(보안 lane): `` `rm -rf ~` `` · `@mclayer` · `](evil.example)` 가 채널 본문에
#   **원문 그대로** 착지했고, `@name` 은 **실 알림**을, `#NNNN` 은 **역참조 백링크**를
#   만들었다. 즉 관측 대상의 *이름*이 보고 채널의 **구조**를 바꿀 수 있었다.
#
#   ★ 도달성 정직 표기 (과장 금지): 현 입력원은 `~/.claude/worktrees/<repo>` 1-level
#     listdir(= repo 명)과 로컬 temp 슬러그뿐이라 **원격 공격자 통제 불가**다 — HOME 쓰기
#     권한자만 심을 수 있고 그는 이미 동일 신뢰도메인이다. **지금은 방어심층**이며,
#     branch 명(depth 2)·PR 제목 등 덜 신뢰되는 이름원이 유입되면 즉시 live 가 된다.
#
#   변환 2종 (둘 다 **삽입만** 한다 — 삭제 0, 따라서 단사):
#     ① 활성 구성자 백슬래시 이스케이프: ``\ ` * _ [ ] < > & !``
#        (도입자 `\` 를 **먼저** 이스케이프해야 `\[` 입력이 `\\[` 로 되살아나지 않는다.)
#     ② 인접 파괴: `@`+영숫자 / `#`+숫자 사이에 `%-` 삽입 — `@%-name` · `#%-2949`.
#        mention·이슈참조는 **인접**이 조건이므로, 렌더러의 이스케이프 해석에 기대지 않고
#        인접 자체를 끊는다(렌더러 무관하게 성립하는 축). 알파벳은 `_LEXICON_ESCAPE` 와
#        같은 것을 쓴다 — 이미 `%` 는 ①단계 scrub 가 `%%` 로 doubling 해 두므로 `%-` 는
#        **삽입 표식으로만** 등장한다(모호성 0).
#
#   호출 위치 = `_safe_text` 의 **맨 끝** (load-bearing):
#     · `_mask_workspace_prefix` 는 workspace 루트를 **리터럴 find** 한다. 앞에서
#       `\`→`\\` 를 걸면 Windows 경로가 어긋나 그 마스킹이 통째로 실패한다.
#     · `_DRIVE_RE`/잔여 가드는 `[\\/]` 를 본다. 앞에서 `\` 를 삽입하면 `X:[` 같은
#       무관한 형상이 드라이브로 **오탐**돼 필드가 통째 접힌다(가드가 아니라 자해).
#     ⇒ 정규화가 **원문 경로**를 보고 끝낸 뒤에 무해화한다.
#
#   D3 라운드트립 무손상: 무해화는 `_safe_text` **안**에 있으므로 `dedup_key` 와 렌더
#     본문의 key 필드가 **같은 값**을 쓴다. 식별 축과 표시 축을 분리하지 않는다는 기존
#     결정(위 `_LEXICON_ESCAPE` 절)과 같은 이유다.
#
#   대가 (선언 — 은폐 금지):
#     · 도입기 채널의 기존 키 중 활성 구성자를 포함하던 것은 1회 바뀌어 **그 항목이 1회
#       재발화**한다(`_MAX_KEY_LEN` 경계화·어휘 이스케이프 도입 때와 동형 대가).
#     · stderr 경고도 같은 파이프라인을 타므로 `\[Errno 13\]` 처럼 보인다. 파이프라인을
#       둘로 쪼개면 `dedup_key` 와 본문이 갈라질 위험이 생기므로 단일 경로를 유지한다.
#
#   무해화하지 **않는** 것 (선언된 잔여 — "전부 막았다" 금지):
#     · `~` — `~~` 짝이 있어야 strikethrough 가 되고, 홈-상대 표기(`~/.claude/...`)의
#       가독성이 load-bearing 이다. 표시 축 cosmetic 잔여.
#     · `|` — 본문에 표 구분행이 없어 표가 성립하지 않는다. 표시 축 cosmetic 잔여.
#     · `(` `)` — 링크는 `]` 가 이스케이프되면 성립하지 않는다(짝 구성자 제거로 무력화).
#     · 줄머리 구성자(`-` `+` `.` `#` 표제) — 필드는 제어문자 strip 으로 **단일 줄**이고
#       본문 중간에 삽입되므로 줄머리에 설 수 없다.
#     · 렌더러가 실제로 무엇을 그리는지는 **단정하지 않는다**(ADR-119). 본 모듈이 재는
#       것은 산출 문자열의 형상뿐이다 — 활성 구성자를 남기지 않았는가.
#     · Windows 는 `*` `:` `<` `>` `|` 를 파일명에서 거부한다 ⇒ 그 문자군은 **이 호스트의
#       실 파일명 축에서 미측정**이다. POSIX consumer 에서는 전부 합법이라 표면이 넓다.
_MD_ACTIVE_CHARS = "\\`*_[]<>&!"
_MD_ACTIVE_RE = re.compile(r"[\\`*_\[\]<>&!]")
_MD_MENTION_RE = re.compile(r"@(?=[A-Za-z0-9])")     # mention 은 `@`+영숫자 인접이 조건
_MD_ISSUEREF_RE = re.compile(r"#(?=[0-9])")          # 이슈 참조는 `#`+숫자 인접이 조건

# ── 경로 정규화 마스크 (AC-13 "홈·workspace 상대 표기") ─────────────────────────────
#   base.relativize_path 는 (a) HOME 접두 (b) 현 사용자명 세그먼트만 처리한다 —
#   HOME **밖** 경로(workspace-root / 타 사용자 홈 / 타 드라이브)는 무처리로 남는다.
#   공유 자산(check_orphan_worktree_classify)은 타 소비자 blast radius 때문에 수정하지
#   않고, 본 모듈 **지역 정규화층**으로 sanitize 통과 후 잔존분만 3단 처리한다.
_MASK_WORKSPACE = "<workspace>"
_MASK_USER_HOME = "<user-home>"
_MASK_DRIVE = "<drive>"
_MASK_UNNORMALIZED = "<미정규화-경로-제거>"

# 2단 — 잔존 `X:\Users\<name>` / `/Users/<name>` / `/home/<name>` (임의 사용자명).
#   뒤 구분자는 소비하지 않는다(원문 구분자 보존). 이름 세그먼트 bounded {1,64}.
_USER_HOME_RE = re.compile(r"(?i)(?:[A-Za-z]:)?[\\/](?:Users|home)[\\/][^\\/]{1,64}")

# 3단 — 그래도 남는 드라이브 문자 `X:\` / `X:/`. 선행 영숫자 배제로 `http://` 오탐 차단.
_DRIVE_RE = re.compile(r"(?<![A-Za-z0-9])[A-Za-z]:([\\/])")

# 최종 잔여 가드(fail-closed) — 3단 후에도 남으면 필드 통째 치환. 부분 성공 통과 금지.
_RESIDUAL_DRIVE_RE = re.compile(r"[A-Za-z]:[\\/]")
_RESIDUAL_USERROOT_RE = re.compile(r"(?i)[\\/](?:Users|home)[\\/]")

# 사실 줄에서 dedup 키 추출 — key= 는 줄 끝 필드라 **EOL 까지 원문 그대로** 포획한다.
#   ★ D3 라운드트립 계약 (역추출(render_fact_tuple(o)) == dedup_key(o)) 봉합 — 이전 판본
#     `^\s*-\s.*·\s*key=(.+?)\s*$` 의 두 결함:
#     ① 후행 `\s*$` 가 키의 **후행 공백을 절단**했다 → 공백으로 끝나는 키가 라운드트립 실패
#        (매 실행 중복 발화). → 후행 anchor 제거, `(.+)$` 로 EOL 까지 원문 포획.
#     ② greedy `.*` 가 **마지막** ` · key=` 를 골랐다 → 관측 경로에 `· key=` 를 매립하면
#        추출값이 그 뒤 문자열로 바뀌어 **임의 키 주입**이 성립했다(그 형상이 실 discover 를
#        통과함이 실측 확인됨). → non-greedy `.*?` 로 **첫** ` · key=` (= 렌더가 붙인 진짜
#        필드)를 고정한다.
#   ★ 정직 잔여: 첫 매치 고정이라 `선언`·`실측` 필드 자체에 `· key=` 가 섞이면 추출이
#     그 지점을 잡는다. 본 모듈이 채우는 두 필드는 도메인 enum·수치 서술이라 현 경로에는
#     유입원이 없으나, "임의 입력 무해" 를 단정하지 않는다(ADR-168 §결정 16 bounded degradation).
_FACT_KEY_RE = re.compile(r"^\s*-\s.*?·\s*key=(.+)$")

# 보고 채널 지정 형식: owner/repo#N (anchored, bounded).
_CHANNEL_RE = re.compile(r"^([A-Za-z0-9._-]{1,100}/[A-Za-z0-9._-]{1,100})#(\d{1,9})$")

# 하위 스크립트(scratch-ttl) 출력 수치 필드 — verdict 어휘 없는 숫자만 재서술한다.
_SCRATCH_DONE_RE = re.compile(r"\[scratch-ttl\]\s+DONE:\s+purged=(\d+)\s+kept=(\d+)")
_SCRATCH_WOULD_RE = re.compile(r"would_purge=(\d+)")


# ═══════════════════════════════ dataclasses ═══════════════════════════════════════
@dataclass
class Observation:
    cls: str          # "worktree" | "scratch" | "temp" | "orphan"
    display_path: str  # 홈 상대 표기 (relativize_path 통과분)
    declared: str     # 선언값 — 해당 도메인 규약이 기대하는 상태
    measured: str     # 실측값 — 관측된 사실 (reason·age 등)
    mismatch: bool    # 불일치 여부


@dataclass
class StopDecision:
    halted: bool
    reasons: list = field(default_factory=list)   # ["F1"] / ["F2"] / ["F1","F2"] / ["read-failure"]


# ═══════════════════════════════ 공통 내부 헬퍼 ═════════════════════════════════════
def _field(obs, name, default=""):
    """Observation dataclass / dict 양쪽에서 필드 판독 (호출자 형태 결합 완화)."""
    if isinstance(obs, dict):
        return obs.get(name, default)
    return getattr(obs, name, default)


def _scrub_verdict_tokens(s):
    """verdict 어휘를 **무손실·가역 이스케이프**로 무력화 (INV-E 산출 강제).

    줄 제거(filter_verdict_lines)와 달리 관측 사실을 잃지 않으면서 어휘만 없앤다 —
    경로·태스크명 등 우리가 통제하지 못하는 입력에 어휘가 섞여도 산출 어휘 0 을 보장.

    ★ 구판의 삭제 치환(`<제거>`)은 **비단사**였다 — `…-pass` / `…-fail` 이 같은 문자열로
      붕괴해 `dedup_key` 가 두 잔재를 한 키로 합쳤다(F-CR5-03). 규칙·성질·대가는 모듈
      상단 `_LEXICON_ESCAPE` 주석이 SSOT. 좌역원 = `unscrub_verdict_tokens`."""
    if not isinstance(s, str):
        s = "" if s is None else str(s)
    s = s.replace(_ESC_CHAR, _ESC_DOUBLED)
    return _LEXICON_RE.sub(
        lambda m: m.group(0)[0] + _LEXICON_ESCAPE + m.group(0)[1:], s
    )


def unscrub_verdict_tokens(s) -> str:
    """`_scrub_verdict_tokens` 의 **좌역원** — 단사성의 실행 가능한 증거.

    `unscrub(scrub(x)) == x` 가 모든 문자열에서 성립한다(fuzz 코퍼스 property 로 결박).
    좌역원이 존재하므로 scrub 는 단사다.

    ★ 정직 천장 (구현리뷰 iter6 F-CR6-04 — 형제 테스트 문면 재사용):
      여기서 재는 것은 **어휘 변환** 축의 단사성이다. `_safe_text` 전체는 단사가
      **아니다** — `_normalize_paths` 의 fail-closed 경로가 여러 입력을
      `<미정규화-경로-제거>` 하나로 접는다. 그 붕괴는 "정규화 실패 = 위치 미공개"
      라는 **선언된 보안 선택**이지 본 결함과 다른 축이며, 본 함수는 그 축을
      단사라고 주장하지 않는다.
      ⇒ 따라서 "서로 다른 두 잔재 경로가 같은 `dedup_key` 로 붕괴할 수 없다" 는
        **여기서 연역되지 않는다**. `dedup_key` 는 `_safe_text` 를 통과하므로 위
        붕괴를 그대로 물려받는다(실측: `/srv/home/` · `/var/home/` · `/a/Users/`
        세 경로가 전부 `orphan:<미정규화-경로-제거>` 한 키가 된다).
        어휘 변환이 되돌린 것은 **어휘만 다른 경로 쌍**의 붕괴다(F-CR5-03 형상).

    스캔 계약: scrub 산출에서 `%` 는 **항상 2글자 단위의 첫 글자**다
    (`%%` = 원문 `%` / `%-` = 삽입된 분리자). 그래서 좌→우 단일 스캔이 모호하지 않다.
    임의 입력(스크럽 산출이 아닌 문자열)에 대해서는 짝 없는 `%` 를 그대로 보존한다."""
    if not isinstance(s, str):
        s = "" if s is None else str(s)
    out = []
    i, n = 0, len(s)
    while i < n:
        c = s[i]
        if c == _ESC_CHAR and i + 1 < n:
            nxt = s[i + 1]
            if nxt == _ESC_CHAR:
                out.append(_ESC_CHAR)
                i += 2
                continue
            if nxt == _LEXICON_ESCAPE[1]:
                i += 2
                continue
        out.append(c)
        i += 1
    return "".join(out)


def _neutralize_markdown(s):
    """마크다운 활성 구성자 무해화 (F-SEC-4). 규칙·상한 SSOT = 모듈 상단 `_MD_ACTIVE_CHARS` 절.

    삽입만 하고 삭제하지 않는다. 좌역원 = `unneutralize_markdown`.
    (단사성이 load-bearing 인 이유: 이 함수는 `_safe_text` 안에 있어 `dedup_key` 에도
     걸린다. 비단사 변환이면 서로 다른 두 잔재가 한 키로 붕괴해 한쪽이 영구 억제된다 —
     F-CR5-03 이 정확히 그 형상이었다.)

    ★ 단사성의 **정의역** (선언을 코드보다 넓게 쓰지 않는다 — 이 Story 의 반복 결함 class):
      단사는 **어휘 스크럽 산출**(= 실 파이프라인에서 이 함수가 받는 값) 위에서 성립하며
      임의 문자열 위에서는 **성립하지 않는다**. 반례: `#1` 과 `#%-1` 은 둘 다 `#%-1` 로
      간다(전자는 삽입, 후자는 `#` 뒤가 숫자가 아니라 무삽입).
      실 경로에서 그 반례가 불가능한 이유: `@%-`·`#%-` 는 스크럽 산출에 존재할 수 없다 —
      스크럽은 `%-` 를 lexicon 토큰 **첫 글자 뒤**에만 넣고(앞 글자는 P/F/O/정/문),
      원문의 `%` 는 같은 단계에서 `%%` 로 doubling 된다(입력 `#%-1` → 스크럽 `#%%-1`).
      결박 = `test_scheduled_task_output_hardening.py::…::test_neutralization_is_injective_over_corpus`
      (그 반례 쌍을 케이스에 명시적으로 포함해 정의역 경계를 고정한다)."""
    if not isinstance(s, str):
        s = "" if s is None else str(s)
    s = _MD_ACTIVE_RE.sub(lambda m: "\\" + m.group(0), s)
    s = _MD_MENTION_RE.sub("@" + _LEXICON_ESCAPE, s)
    s = _MD_ISSUEREF_RE.sub("#" + _LEXICON_ESCAPE, s)
    return s


def unneutralize_markdown(s) -> str:
    """`_neutralize_markdown` 의 **좌역원** — 단사성의 실행 가능한 증거.

    `unneutralize(neutralize(x)) == x` (property 로 결박). 좌역원이 존재하므로 단사다.

    ★ 정의역: **`_neutralize_markdown` 의 산출**이다(`unscrub_verdict_tokens` 와 동일한
      정직 표기). 임의 문자열에 대한 전역 역함수를 주장하지 않는다 — 예컨대 손으로 쓴
      `#%-5` 는 무해화가 만든 삽입이 아니지만 여기서는 삽입으로 읽힌다. 실 파이프라인에서
      그 형상이 무해화 **이전**에 존재할 수 없는 이유: `%-` 는 어휘 스크럽이 lexicon 토큰
      첫 글자 뒤에만 넣고, 원문의 `%` 는 그 단계에서 이미 `%%` 로 doubling 된다.

    용도: (a) 단사성 property (b) 경로 누출 오라클이 **무해화 이전 문자열**을 정의역으로
      삼을 수 있게 한다 — 이스케이프가 만든 `\\` 를 경로 구분자로 오독하지 않도록."""
    if not isinstance(s, str):
        s = "" if s is None else str(s)
    out = []
    i, n = 0, len(s)
    while i < n:
        c = s[i]
        if c == "\\" and i + 1 < n and s[i + 1] in _MD_ACTIVE_CHARS:
            out.append(s[i + 1])
            i += 2
            continue
        if c in "@#" and s[i + 1:i + 3] == _LEXICON_ESCAPE:
            out.append(c)
            i += 3
            continue
        out.append(c)
        i += 1
    return "".join(out)


# ── 경로 정규화층 (AC-13 이행 — 홈 축은 base 재사용, workspace/타사용자/드라이브 축만 지역) ──
_workspace_prefix_cache = None       # None = 미해소 (tuple = 해소 완료, () 포함)


def _set_workspace_prefixes(paths):
    """workspace 스캔 루트 등록 — 이미 scan_roots 를 계산한 지점이 권위값을 주입한다
    (추가 subprocess 0). repo_root 기준이라 cwd 변동에 흔들리지 않는다."""
    global _workspace_prefix_cache
    out = []
    for p in paths or []:
        if not p:
            continue
        try:
            out.append(os.path.abspath(os.path.expanduser(p)))
        except (OSError, ValueError):
            continue
    _workspace_prefix_cache = tuple(out)


def _workspace_prefixes():
    """등록값 우선. 미등록(직접 render 호출 등)이면 1회 lazy 해소 후 memoize.

    ★ 미해소여도 불변식은 3단(`<drive>`)이 지킨다 — 1단은 가독성 개선이지 가드가 아니다."""
    global _workspace_prefix_cache
    if _workspace_prefix_cache is None:
        try:
            _set_workspace_prefixes([s["path"] for s in discovery.default_scan_roots(None)
                                     if s.get("source") == "workspace-root"])
        except Exception:   # noqa: BLE001 — 해소 실패해도 3단 가드로 충분
            _workspace_prefix_cache = ()
    return _workspace_prefix_cache


def _current_user_residual_re():
    """현 사용자명 잔존 검사 — **경로 세그먼트 경계**로 한정한다.

    ★ 문면상의 '사용자명 1건이라도 잔존' 을 무경계 substring 으로 읽으면, 흔한 이름
      (dev/temp/git 등)일 때 `보존사유=temp-git-worktree` 같은 **비경로 필드까지 전량**
      `<미정규화-경로-제거>` 로 뭉개져 보고 자체가 무용해진다(가드가 아니라 자해).
      사용자명 누출은 정의상 경로 세그먼트로 일어나므로 경계 한정이 검출력 손실 0."""
    user = os.path.basename(os.path.expanduser("~"))
    if not user:
        return None
    return re.compile(r"(?i)(?:^|[\\/])%s(?:$|[\\/])" % re.escape(user))


def _mask_workspace_prefix(s):
    """1단 — workspace 스캔 루트 접두를 `<workspace>` 로. 구분자 원문 보존(길이 동일 치환)."""
    for p in _workspace_prefixes():
        for variant in (p, p.replace("/", "\\"), p.replace("\\", "/")):
            idx = s.lower().find(variant.lower())
            if idx >= 0:
                return s[:idx] + _MASK_WORKSPACE + s[idx + len(variant):]
    return s


def _normalize_paths(s):
    """sanitize 통과 **후** 잔존 절대경로 3단 정규화 + 최종 잔여 가드(fail-closed).

    1단 workspace 루트 → <workspace> / 2단 타 사용자 홈 → <user-home> / 3단 드라이브 → <drive>.
    3단 후에도 드라이브·Users|home 루트·현 사용자명이 남으면 필드 통째 `<미정규화-경로-제거>`
    (부분 성공을 통과로 렌더하지 않는다). 기존 마스크 토큰(`~` `<user>` `<...>`)은 어느 패턴에도
    매치하지 않아 이중 치환이 발생하지 않는다."""
    if not s:
        return s
    s = _mask_workspace_prefix(s)
    s = _USER_HOME_RE.sub(_MASK_USER_HOME, s)
    s = _DRIVE_RE.sub(_MASK_DRIVE + r"\1", s)
    if _RESIDUAL_DRIVE_RE.search(s) or _RESIDUAL_USERROOT_RE.search(s):
        return _MASK_UNNORMALIZED
    user_re = _current_user_residual_re()
    if user_re is not None and user_re.search(s):
        return _MASK_UNNORMALIZED
    return s


def _safe_text(s):
    """산출 문자열 공통 정규화 — 산출 경로 전 지점이 이 함수를 통과한다.

    scrub → sanitize(경로 상대화 + secret redact + 제어문자 strip) → 경로 정규화 → scrub.
    ★ scrub 를 sanitize **앞뒤로** 두 번 건다: 제어문자 strip 이 토큰을 이웃 문자에
      용접(`"task\\nOK"` → `"taskOK"`)하면 word-boundary 가 사라져 뒤늦은 scrub 가
      놓친다 — strip 이전에 한 번 걸어 경계가 살아있을 때 잡는다(실측 반증으로 확인).
    ★ 제어문자 strip 이 개행까지 제거하므로 **단일 필드에만** 적용한다
      (조립된 여러 줄 본문에 적용하면 줄이 뭉개짐 — render_report 는 필드 단위 적용).
    ★ 경로 정규화가 이 파이프라인 **안**에 있어야 dedup_key 와 렌더 본문이 같은 값을
      쓴다(D3 라운드트립 계약). 정규화층을 호출부로 빼면 그 계약이 깨진다.
    ★ 마크다운 무해화(F-SEC-4)는 **맨 끝**이다 — 앞에 두면 삽입된 `\\` 가 경로 정규화의
      리터럴 find 와 `[\\/]` 매칭을 교란해 마스킹이 실패하거나 과잉 접힘이 된다.
      같은 이유로 무해화도 이 파이프라인 **안**에 있어야 D3 계약이 유지된다."""
    return _neutralize_markdown(
        _scrub_verdict_tokens(_normalize_paths(base.sanitize(_scrub_verdict_tokens(s)))))


def _warn(msg, detail=None):
    """advisory stderr 보고 (non-blocking). 본문과 동일 정규화 통과 — INV-E.

    ★ 두 인자를 **각각 따로** `_safe_text` 에 통과시킨다 (구현리뷰 iter6 F-CR6-06).
      한 문자열로 합쳐 넘기면 `_normalize_paths` 의 fail-closed 가 **필드 통째**를
      `<미정규화-경로-제거>` 로 접기 때문에, 가변 경로 한 조각이 정적 사실 문구까지
      같이 지운다 — 실측: 8워커 실행에서 경고 3694줄이 전부 `[scheduled-task]
      <미정규화-경로-제거>` 였고, "heartbeat 기록 실패" 라는 **사실도 사유도** 남지
      않았다(하필 그 실패가 F-CR6-03 진단의 유일 신호였다).
      필드를 나누면 경로 없는 `msg` 는 정규화를 그대로 통과하고 `detail` 만 접힌다.

    ★ INV-E 는 약화되지 않는다 — **두 필드 모두** 어휘 스크럽·경로 정규화를 통과한다.
      `msg` 를 마스킹 면제하는 것이 아니라 **별도 필드로 재는** 것뿐이다. 따라서
      `msg` 에 경로를 넣으면 여전히 통째로 접힌다(호출부는 정적 문구만 넣는다).
    """
    line = "[%s] %s" % (SCRIPT_NAME, _safe_text(msg))
    if detail is not None:
        line = "%s: %s" % (line, _safe_text(detail))
    print(line, file=sys.stderr)


def _emit_done(observed, new, posted, halted):
    """stdout 마지막 줄 출력 계약 (기존 [scratch-ttl]/[residue-scan] 관례 상속).

    ★ 이 줄에 verdict 어휘 0 (INV-E)."""
    print("[%s] DONE: observed=%d new=%d posted=%d halted=%d"
          % (SCRIPT_NAME, observed, new, posted, halted))


def _kst_iso(now=None):
    """KST(+09:00) ISO 8601 — 로컬 TZ 무관 결정론(CI/Git Bash UTC gotcha 회피)."""
    n = base.now_epoch() if now is None else int(now)
    return datetime.fromtimestamp(n, tz=timezone(timedelta(hours=9))).isoformat(timespec="seconds")


def _days(seconds):
    return int((seconds or 0) // 86400)


def _parse_channel(channel):
    """`owner/repo#N` → (owner/repo, "N"). 형식 위반 → None."""
    if not isinstance(channel, str):
        return None
    m = _CHANNEL_RE.match(channel.strip())
    if not m:
        return None
    return (m.group(1), m.group(2))


def _gh(args, timeout=GH_TIMEOUT):
    """gh 포트 — GH_BIN_ENV override (단일 바이너리 또는 공백분리 명령). 실패 → None.

    base._gh 형상 상속 + shlex 토큰화(DIR_GH_BIN 선례) — shell=False 유지, env 는 신뢰 입력.
    posix=(os.name != 'nt') — Windows 경로 backslash 가 escape 로 소거되지 않게(C:\\... 보존)."""
    raw = (os.environ.get(GH_BIN_ENV, "") or "").strip()
    cmd = shlex.split(raw, posix=(os.name != "nt")) if raw else ["gh"]
    if not cmd:
        cmd = ["gh"]
    try:
        return subprocess.run(
            cmd + [str(a) for a in args],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            shell=False,
            env=base._subprocess_env(),   # MSYS_NO_PATHCONV=1 (경로 변환 오염 차단)
        )
    except (OSError, subprocess.SubprocessError):
        return None


def _git_toplevel(cwd=None):
    """cwd 의 git toplevel (--repo-root 기본값). 실패 → None."""
    cp = base._git(["rev-parse", "--show-toplevel"], cwd=cwd)
    if cp is None or cp.returncode != 0:
        return None
    out = (cp.stdout or "").strip()
    return out or None


# ═══════════════════════ 순수 함수 축 (I/O 0 — fuzz/property 대상) ═══════════════════
def dedup_key(obs) -> str:
    """dedup 키 = class + 홈-상대 경로. 저장하지 않고 대상에서 유도한다 (INV-C).

    ★ 렌더와 **동일 정규화**(_safe_text)를 통과시킨다 — 그래야 채널에 실린 key 문자열과
      다음 실행의 재유도값이 정확히 일치해 dedup 이 성립한다(roundtrip 계약).

    ★ 길이 상한 **대칭 적용** (D3 라운드트립 봉합): 역추출(fetch_existing_keys)이
      `_MAX_KEY_LEN` 초과 키를 폐기하므로, 정방향도 같은 상한 안의 **경계화 키**를
      발화해야 계약이 성립한다. 초과 시 `앞 480자 + '~' + 전체 키 sha256 8-hex`
      (총 489자 ≤ 상한). 앞부분이 같고 뒤만 다른 장문 경로는 8-hex 가 구별한다.

    ★ 대가 (선언된 상한, 결함 아님):
      · 8-hex 이므로 앞 480자 동일 + 해시 충돌 시 두 잔재가 한 키로 합쳐질 확률이 0 은
        아니다(≈2^-32 per collision pair).
      · 본 규칙 도입으로 **상한 초과 잔재의 키가 바뀐다** → 그 항목만 1회 재발화한다.
        도입기 채널 이력이 사실상 비어 있어 수용한 대가다."""
    cls = _safe_text(_field(obs, "cls"))
    path = _safe_text(_field(obs, "display_path"))
    raw = "%s:%s" % (cls, path)
    if len(raw) <= _MAX_KEY_LEN:
        return raw
    digest = hashlib.sha256(raw.encode("utf-8", "replace")).hexdigest()[:_KEY_BOUND_DIGEST]
    return "%s~%s" % (raw[:_KEY_BOUND_PREFIX], digest)


def contains_verdict_lexicon(text) -> bool:
    """verdict 어휘 포함 여부. ASCII 는 word-boundary, 한글은 substring."""
    if not isinstance(text, str):
        text = "" if text is None else str(text)
    return _LEXICON_RE.search(text) is not None


def filter_verdict_lines(text) -> str:
    """verdict 어휘가 포함된 줄은 제거한다(인용 금지). 수치 필드만 남긴다.

    용도 = 하위 스크립트 출력을 그대로 인용하지 않기 위한 줄 단위 게이트 + 렌더 backstop.
    ★ sentinel/trailer 에는 적용하지 않는다 — 마커 줄이 사라지면 자기 코멘트 식별이
      깨져(INV-D) 영구 재발화가 되므로, 마커 줄은 _safe_text 토큰 치환으로만 보증한다."""
    if not isinstance(text, str):
        text = "" if text is None else str(text)
    return "\n".join(ln for ln in text.splitlines() if not contains_verdict_lexicon(ln))


def render_fact_tuple(obs) -> str:
    """`선언값 · 실측값 · 불일치` 사실 3-tuple 1줄. verdict 어휘 0.

    key 는 줄 끝 식별 필드 — 경로를 별도 필드로 중복 표기하지 않는다(키가 class:경로)."""
    declared = _safe_text(_field(obs, "declared"))
    measured = _safe_text(_field(obs, "measured"))
    mismatch = "Y" if bool(_field(obs, "mismatch", False)) else "N"
    return "- 선언=%s · 실측=%s · 불일치=%s · key=%s" % (declared, measured, mismatch, dedup_key(obs))


def render_report(observations, task_name, run_id, now=None) -> str:
    """sentinel 1줄 + 사실 3-tuple 본문 + trailer 1줄. 전 문자열 sanitize 통과.

    ★ sanitize 는 **필드 단위**로만 적용한다(제어문자 strip 이 개행을 지우므로 조립본에
      적용 금지). 본문 줄은 조립 후 filter_verdict_lines backstop 을 한 번 더 통과한다."""
    facts = [render_fact_tuple(o) for o in (observations or [])]
    body = filter_verdict_lines("\n".join(facts))
    kept = [ln for ln in body.splitlines() if ln.strip()]
    head = "%s items=%d (사실 관측 — 선언·실측·불일치)" % (SENTINEL, len(kept))
    trailer = "%s task=%s run=%s at=%s" % (
        TRAILER,
        _safe_text(task_name or "unknown"),
        _safe_text(run_id or "unknown"),
        _kst_iso(now),
    )
    parts = [head]
    if kept:
        parts.extend(kept)
    parts.append(trailer)
    return "\n".join(parts)


# ═══════════════════════════════ 관측 축 ═══════════════════════════════════════════
def _observe_workspace_residue(repo_root=None, scan_roots=None):
    """worktree/orphan 축 — discovery 스캐너 discover→classify→judge **3단만** 호출.

    ★ run_scan()/execute() 미호출 (INV-A) — run_scan 은 내부에서 execute(삭제)를 부른다.
    temp source 는 제외한다: temp 축 단일 소스 = observe_temp() (이중 계상 회피)."""
    roots = scan_roots if scan_roots is not None else discovery.default_scan_roots(repo_root)
    roots = [r for r in (roots or []) if r.get("source") != "temp"]
    # 경로 정규화 1단의 권위값 등록 (repo_root 기준 — 추가 subprocess 0, AC-13).
    _set_workspace_prefixes([r.get("path") for r in roots if r.get("source") == "workspace-root"])
    if not roots:
        return []
    candidates = discovery.discover(roots, repo_root=repo_root)
    classified = discovery.classify(candidates)
    verdicts = discovery.judge(classified)

    out = []
    threshold = base.STALE_DAYS * 86400
    for v in verdicts:
        cls = "worktree" if v.source == "worktrees-base" else "orphan"
        reason = v.reason or "none"
        age = v.age or 0
        justified = (reason in _JUSTIFIED_REASONS) or reason.startswith("unpushed-")
        mismatch = (age > threshold) and not justified
        out.append(Observation(
            cls=cls,
            display_path=base.relativize_path(v.path),
            declared="완결 직후 정리 (age<=%dd 또는 명시 보존 사유 보유)" % base.STALE_DAYS,
            measured="age=%dd 보존사유=%s source=%s" % (_days(age), reason, v.source),
            mismatch=mismatch,
        ))
    return out


def _observe_scratch(scratch_root=None):
    """scratch 축 — check_codeforge_scratch_ttl.run() 을 **GC_DRY_RUN=1 강제** 후 호출.

    ★ run() 은 GC_DRY_RUN 을 호출 시점에 판독한다(L146) → dry-run 경로에서 os.remove 미도달
      (INV-A). env 는 호출 전후로 저장·복원한다.
    프로그램적 소비 표면이 stdout/stderr 텍스트뿐이라 in-process 캡처 후 **수치 필드만**
      파싱한다(줄 인용 0 — INV-E). DONE(purged/kept) + DRY_RUN 요약(would_purge) 양쪽을
      읽는 이유: dry-run 에서 purged 는 구조적으로 항상 0 이라 DONE 단독으로는 TTL 초과
      잔존을 분별할 수 없다(불일치가 항상 N 이 되는 hollow 판정 회피)."""
    root = scratch_root or scratch_axis._scratch_root()

    prev_dry = os.environ.get("GC_DRY_RUN")
    orig_root_fn = scratch_axis._scratch_root
    out_buf, err_buf = io.StringIO(), io.StringIO()
    try:
        os.environ["GC_DRY_RUN"] = "1"          # ★ 실 삭제 차단 (INV-A)
        if scratch_root is not None:
            scratch_axis._scratch_root = lambda: root   # 테스트 주입 seam (재구현 0)
        with contextlib.redirect_stdout(out_buf), contextlib.redirect_stderr(err_buf):
            scratch_axis.run()
    finally:
        scratch_axis._scratch_root = orig_root_fn
        if prev_dry is None:
            os.environ.pop("GC_DRY_RUN", None)
        else:
            os.environ["GC_DRY_RUN"] = prev_dry

    stdout_txt, stderr_txt = out_buf.getvalue(), err_buf.getvalue()
    purged = kept = would = 0
    m = _SCRATCH_DONE_RE.search(stdout_txt)
    if m:
        purged, kept = int(m.group(1)), int(m.group(2))
    m2 = _SCRATCH_WOULD_RE.search(stderr_txt)
    if m2:
        would = int(m2.group(1))

    ttl_days = scratch_axis._ttl_seconds() / 86400.0
    return [Observation(
        cls="scratch",
        display_path=base.relativize_path(root),
        declared="loose 파일 TTL<=%gd 이내 회수" % ttl_days,
        measured="TTL초과=%d 보존=%d 삭제집행=%d(관측전용)" % (would, kept, purged),
        mismatch=would > 0,
    )]


def _observe_temp(temp_root=None, now=None):
    """temp 축 — observe_temp() **만** 호출 (main()/_stage2_delete 미호출 — INV-A).

    TEMP_GC_DELETE_ENABLED 는 import-time 상수라 env 로 바뀌지 않으며, 본 축은 그 상수를
    건드리지 않고 관측 함수만 쓰므로 정의상 무관하다."""
    obs = temp_axis.observe_temp(temp_root=temp_root, now=now)
    if not obs.get("exists"):
        return []
    out = []
    threshold = base.STALE_DAYS * 86400
    for e in obs.get("entries") or []:
        age = e.get("age") or 0
        preserve = bool(e.get("preserve"))
        reason = e.get("reason") or "none"
        mb = (e.get("size") or 0) / (1024.0 * 1024.0)
        out.append(Observation(
            cls="temp",
            display_path=base.relativize_path(e.get("path") or obs.get("root") or ""),
            declared="세션 종료 후 잔존 age<=%dd (회수 미배선 — 관측전용)" % base.STALE_DAYS,
            measured="age=%dd files=%d size=%.1fMB kind=%s 보존사유=%s"
                     % (_days(age), int(e.get("files") or 0), mb,
                        "git" if e.get("is_git") else "loose", reason),
            mismatch=(age > threshold) and not preserve,
        ))
    return out


def collect_observations(repo_root=None, scan_roots=None, scratch_root=None,
                         temp_root=None, now=None) -> list:
    """스캐너 3종을 관측-only 로 호출해 Observation 목록 산출.

    ★ 파라미터는 테스트 주입용이며 None 이면 프로덕션 기본값.
    축 격리 — 한 축의 예외가 다른 축을 abort 시키지 않는다(부분 관측이 무관측보다 낫다).
    동일 키 중복은 최초 1건만 남긴다(입력 순서 보존)."""
    collected = []
    axes = (
        ("workspace", lambda: _observe_workspace_residue(repo_root=repo_root, scan_roots=scan_roots)),
        ("scratch", lambda: _observe_scratch(scratch_root=scratch_root)),
        ("temp", lambda: _observe_temp(temp_root=temp_root, now=now)),
    )
    for name, fn in axes:
        try:
            collected.extend(fn() or [])
        except Exception as e:   # noqa: BLE001 — advisory, 축 격리
            # 정적 사실 문구 + axis(폐쇄 식별자)는 msg, 예외 원문은 detail —
            #   예외에 경로가 섞여도 "어느 축이 실패했다" 는 사실은 남는다(F-CR6-06).
            _warn("관측 축 실패 (non-blocking, axis=%s)" % name,
                  base.strip_control(str(e))[:160])

    seen = set()
    unique = []
    for o in collected:
        k = dedup_key(o)
        if k in seen:
            continue
        seen.add(k)
        unique.append(o)
    return unique


# ═══════════════════════════════ 정지 축 (fail-closed) ═══════════════════════════════
def read_stop_flags(repo_root=None, local_flag=None) -> StopDecision:
    """정지 = F1 ∨ F2 ∨ 판독실패. 예외 발생 시 halted=True (fail-closed).

    F1 = <repo_root>/.codeforge/post-merge-automation.disabled (repo 축)
    F2 = ~/.claude/worktree-gc-state/scheduled-task.disabled   (로컬 축)"""
    reasons = []
    try:
        root = repo_root or os.getcwd()
        if os.path.exists(os.path.join(root, STOP_FLAG_REPO_RELPATH)):
            reasons.append("F1")
        if os.path.exists(local_flag or STOP_FLAG_LOCAL):
            reasons.append("F2")
    except Exception:   # noqa: BLE001 — 판독 자체 실패 = 정지(fail-closed)
        return StopDecision(halted=True, reasons=["read-failure"])
    return StopDecision(halted=bool(reasons), reasons=reasons)


# ═══════════════════════════════ 채널 축 (발화 주체) ═══════════════════════════════
def fetch_existing_keys(channel, gh=None):
    """채널 코멘트 전량 조회 → 자기 마커 라인 정규식 매치분에서 dedup 키 추출.

    ★ 매치 실패 코멘트의 본문 텍스트는 그 자리에서 폐기 — 반환값에 절대 싣지 않는다.
    ★ 반환값은 dedup 키 집합뿐이며 외부 저작 문자열이 산출에 실리지 않는다.
    조회 실패 = None 반환 (fail-closed 신호).

    형상 = post-merge-followup.yml L207-216 (전량 조회 → marker grep → skip) 의 python 상속.
    --jq 대신 python json 파싱 — stub 주입 표면을 단순화(jq 의존 0)."""
    parsed = _parse_channel(channel)
    if parsed is None:
        return None
    owner_repo, number = parsed
    runner = gh or _gh
    cp = runner(["issue", "view", number, "--repo", owner_repo, "--json", "comments"])
    if cp is None or getattr(cp, "returncode", 1) != 0:
        return None
    try:
        data = json.loads(getattr(cp, "stdout", "") or "")
    except (ValueError, TypeError):
        return None

    if isinstance(data, dict):
        comments = data.get("comments") or []
    elif isinstance(data, list):
        comments = data
    else:
        return None

    keys = set()
    for c in comments:
        body = c.get("body") if isinstance(c, dict) else None
        if not isinstance(body, str) or SENTINEL not in body:
            continue     # 자기 마커 미보유 = 외부 저작 → 본문 즉시 폐기 (INV-D)
        for line in body.splitlines():
            m = _FACT_KEY_RE.match(line)
            if not m:
                continue
            k = m.group(1)
            if k and len(k) <= _MAX_KEY_LEN:
                keys.add(k)
        # body 지역 참조는 여기서 소멸 — 반환값은 키 집합뿐(멤버십 판정 전용).
    return keys


def post_report(channel, body, gh=None) -> bool:
    """gh 서브프로세스로 코멘트 append. 성공 True.

    본문은 --body-file 로 전달한다 — argv 경유 시 Windows 한글 mangling 이 발생한다
    (repo 기지 gotcha). 임시파일은 finally 에서 반드시 제거(자기 잔재 0)."""
    parsed = _parse_channel(channel)
    if parsed is None:
        return False
    owner_repo, number = parsed
    runner = gh or _gh
    text = body if isinstance(body, str) else ("" if body is None else str(body))
    tmp_path = None
    try:
        fd, tmp_path = tempfile.mkstemp(prefix="scheduled-task-report-", suffix=".md")
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
        cp = runner(["issue", "comment", number, "--repo", owner_repo, "--body-file", tmp_path])
        return cp is not None and getattr(cp, "returncode", 1) == 0
    except OSError:
        return False
    finally:
        if tmp_path:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass


# ═══════════════════════════════ heartbeat ═══════════════════════════════════════
def write_heartbeat(now=None, path=None) -> None:
    """★ 기록 조건 = **`collect_observations()` 가 실제로 호출·반환된 종료 경로**에서만 호출.

    ── write 가 보장하는 것 / 보장하지 않는 것 (구현리뷰 iter6 F-CR6-03 로 축소) ──────
    보장 O:
      · **판독자가 보는 파일은 항상 완결된 값** — 임시파일에 전량 기록 후 `os.replace`
        (같은 디렉터리 rename). 부분 기록 상태가 target 이름으로 노출되지 않는다.
      · **동시 writer 간 임시파일 충돌 0** — 임시명을 `tempfile.mkstemp` 로 **호출마다
        고유**하게 딴다. 구판은 `"%s.tmp" % target` 라 대상 경로만으로 결정됐고, 그래서
        동시 writer 전원이 **같은 임시파일**을 열어 서로의 기록을 덮었다(실측: 8워커
        4000 write 중 3694건이 OSError 로 실패, W=4·폴러 0 에서도 600 중 247건 실패).
    보장 X (over-claim 금지):
      · **write 성공 자체는 보장하지 않는다.** Windows 에서 판독 핸들이 열려 있으면
        `os.replace` 가 여전히 실패할 수 있고, 그 경우 예외를 삼키고 **이전 값을 유지**한다
        (advisory 계약 — 호출자를 막지 않는다). 즉 "원자적" 은 *일단 바뀌면 통째로
        바뀐다* 는 뜻이지 *반드시 바뀐다* 는 뜻이 아니다.
      · mkstemp 의 고유성은 **같은 디렉터리 안**에서 성립한다(O_EXCL). 대상 디렉터리를
        여러 호스트가 공유하는 형상은 정의역 밖이다.

    ★ 조건이 "정상 종료" 가 아니라 "관측을 실제로 돌았는가" 인 이유 (load-bearing):
      heartbeat 는 **관측자 생존 신호**다. 스캐너를 한 번도 부르지 않고 끝난 실행이
      fresh 기록을 남기면 watchdog 이 구조적 false-negative(관측자가 죽었는데 살아
      있다고 보고)가 된다 — ADR-172 §결정 6.
      · 기록 O (5경로, 전부 관측 사이클 완주): 관측 0건 · 채널 미지정 · 채널 조회 실패 ·
        신규 0건 · 정상 발화
      · 기록 X (2경로, 관측 미도달·사이클 미완결): 정지(F1∨F2∨판독실패) · --dry-run

    상태 디렉터리는 codeforge-scratch **밖**(worktree-gc-state)이라 자기 TTL 대상이 아니다.
    이 파일은 dedup 상태가 아니라 생존 신호다(INV-C 무손상 — 관측 대상 판정에 미사용).

    ★ 대상 경로는 **호출 시점** 판독 — path 인자 → env ENV_HEARTBEAT_FILE → HEARTBEAT_FILE.
      HEARTBEAT_FILE 은 import 시점 상수라 그것만 쓰면 subprocess 테스트가 실 사용자 파일을
      갱신한다(= 관측자 생존 신호 위조). env 축은 그 격리 seam 이며, 둘 다 부재 시 동작은
      기존과 동일하다."""
    target = path or (os.environ.get(ENV_HEARTBEAT_FILE) or "").strip() or HEARTBEAT_FILE
    n = base.now_epoch() if now is None else int(now)
    tmp = None
    try:
        parent = os.path.dirname(target)
        if parent:
            os.makedirs(parent, exist_ok=True)
        # ★ 임시명은 **writer 고유** — `dir` 를 target 과 같은 디렉터리로 고정해야
        #   `os.replace` 가 같은 파일시스템 안 rename 으로 성립한다(EXDEV 회피).
        fd, tmp = tempfile.mkstemp(prefix=os.path.basename(target) + ".",
                                   suffix=".tmp", dir=parent or ".")
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as fh:
            fh.write("%d\n" % n)
        os.replace(tmp, target)
    except OSError as e:
        _warn("heartbeat 기록 실패 (non-blocking)", base.strip_control(str(e))[:120])
        try:
            if tmp and os.path.exists(tmp):
                os.unlink(tmp)     # 자기 잔재 0 (임시파일 회수)
        except OSError:
            pass


# ═══════════════════════════════ 진입점 ═══════════════════════════════════════════
def _build_parser():
    ap = argparse.ArgumentParser(
        prog="scheduled_task_reconcile.py",
        description="로컬 스케줄 작업 reconcile — 잔재 관측 후 보고 채널에 사실만 append "
                    "(삭제 0, advisory, always exit 0)")
    ap.add_argument("--repo-root", default=None, help="repo 루트 (기본 = cwd 의 git toplevel)")
    ap.add_argument("--channel", default=None,
                    help="보고 채널 owner/repo#N (env %s fallback)" % ENV_CHANNEL)
    ap.add_argument("--task-name", default=None,
                    help="trailer task= 값 (env %s fallback, 부재 시 unknown)" % ENV_TASK_NAME)
    ap.add_argument("--run-id", default=None,
                    help="trailer run= 값 (env %s fallback, 부재 시 unknown)" % ENV_RUN_ID)
    ap.add_argument("--dry-run", action="store_true",
                    help="발화 대신 렌더 본문을 stdout 출력 (채널 미접촉)")
    return ap


def run(argv=None) -> int:
    """실행 순서 불변식 (load-bearing):
      1) 정지 플래그 판독 **먼저** — halted 면 스캐너 미호출 · 채널 미접촉 (§8.10.1).
      2) 관측 — 0건이면 무발화가 정답(빈 보고 금지).
      3) 채널 조회 — None(조회 실패) 이면 fail-closed 무발화(누락은 다음 실행이 자기치유).
      4) 신규 키만 필터 → 렌더 → 발화.
      5) heartbeat 는 **collect_observations() 가 실제로 호출·반환된 종료 경로**에서만
         기록한다 — **정지(F1∨F2∨판독실패) 제외 · --dry-run 제외**.
         · 정지: 스캐너를 아예 부르지 않으므로(위 1) 관측자 생존의 근거가 없다.
           정지 중 기록하면 watchdog 이 "관측자 생존" 으로 오독한다(ADR-172 §결정 6).
         · dry-run: 부수효과 0 계약이며 보고 사이클 미완결이라 생존 신호 근거가 없다.
         · 나머지 5경로(관측 0건 · 채널 미지정 · 채널 조회 실패 · 신규 0건 · 정상 발화)는
           사이클을 완주했으므로 그대로 기록한다."""
    args = _build_parser().parse_args(argv)
    repo_root = args.repo_root or _git_toplevel() or os.getcwd()

    # (1) 정지 플래그 — 스캐너 호출 전 (halted ⇒ 채널 발화 0 ∧ 스캐너 미호출)
    stop = read_stop_flags(repo_root=repo_root)
    if stop.halted:
        _warn("정지 플래그 감지 (%s) — 스캐너 미호출 · 채널 미접촉 · heartbeat 미기록"
              % ",".join(stop.reasons or ["unknown"]))
        # ★ heartbeat 미기록 — 스캐너를 부르지 않았으므로 관측자 생존의 근거가 없다.
        #   여기서 기록하면 정지된 관측자가 매 tick fresh 생존 신호를 남겨 watchdog 이
        #   구조적 false-negative 가 된다 (ADR-172 §결정 6 / ArchitectPL 설계 판정).
        _emit_done(0, 0, 0, 1)
        return 0

    channel = args.channel or os.environ.get(ENV_CHANNEL) or ""
    task_name = args.task_name or os.environ.get(ENV_TASK_NAME) or "unknown"
    run_id = args.run_id or os.environ.get(ENV_RUN_ID) or "unknown"

    # (2) 관측 — 매 실행이 현재 상태 전량을 재관측 (INV-B, cursor 부재)
    observations = collect_observations(repo_root=repo_root)
    observed = len(observations)

    if not observations:
        _warn("관측 0건 — 무발화 (빈 보고 금지)")
        write_heartbeat()
        _emit_done(0, 0, 0, 0)
        return 0

    # --dry-run: 채널 미접촉 (조회조차 하지 않는다) — 렌더 본문만 stdout
    #   ★ heartbeat 미기록 — dry-run 은 부수효과 0 계약이고, 보고 사이클을 완결하지
    #     않으므로 생존 신호의 산출 근거가 없다. 여기서 기록하면 관측 사이클을 돌지
    #     않은 실행이 fresh 생존 신호를 남겨 watchdog 이 구조적 false-negative
    #     (관측자가 죽었는데 살아 있다고 보고)가 된다 — ADR-172 §결정 6.
    if args.dry_run:
        print(render_report(observations, task_name, run_id))
        _emit_done(observed, observed, 0, 0)
        return 0

    if not channel:
        _warn("보고 채널 미지정 (--channel / %s 부재) — 발화 0, 관측 %d건 미보고 (정직 중단)"
              % (ENV_CHANNEL, observed))
        write_heartbeat()
        _emit_done(observed, 0, 0, 0)
        return 0

    # (3) 채널 조회 — dedup 상태 저장소 = append-only 채널 자신 (INV-C)
    existing = fetch_existing_keys(channel)
    if existing is None:
        # 문구에 verdict 어휘(FAIL)를 쓰지 않는다 — _safe_text 스크럽이 자기 진단문까지
        #   치환해 가독성을 해치므로, 출력 문자열은 애초에 어휘 없는 한글로 쓴다(INV-E).
        _warn("채널 조회 실패 — 차단측 고정으로 무발화 (누락분은 다음 실행 재관측으로 자기치유)")
        write_heartbeat()
        _emit_done(observed, 0, 0, 0)
        return 0

    # (4) 신규분만 발화
    fresh = [o for o in observations if dedup_key(o) not in existing]
    if not fresh:
        _warn("신규 0건 — 무발화 (관측 %d건 전량 기보고)" % observed)
        write_heartbeat()
        _emit_done(observed, 0, 0, 0)
        return 0

    to_post = fresh[:MAX_FACT_LINES]
    if len(fresh) > len(to_post):
        _warn("신규 %d건 중 %d건만 이번 본문에 적재 (상한 %d) — 잔여분은 다음 실행 재관측"
              % (len(fresh), len(to_post), MAX_FACT_LINES))
    body = render_report(to_post, task_name, run_id)
    ok = post_report(channel, body)
    if not ok:
        _warn("채널 발화 실패 — 다음 실행 재시도 (상태 무의존이라 재관측으로 복구)")

    # (5) heartbeat
    write_heartbeat()
    _emit_done(observed, len(fresh), 1 if ok else 0, 0)
    return 0


def main(argv=None) -> int:
    """항상 0 반환 (exit code 를 오라클로 쓰지 않는 관례 상속 — INV-F).

    ★ 종료 신호 계약: **모든 종료 경로가 DONE 줄 정확히 1개**를 남긴다.
      INV-F 가 rc 를 오라클에서 배제했으므로 관측 가능한 종료 신호는 DONE 줄 하나뿐이다.
      그 줄이 없는 종료 경로는 "돌았는데 아무것도 못 봤다" 와 "기동조차 못 했다" 가
      구별되지 않는다 — 관측자 자신이 무음이 되는 형상이다."""
    try:
        run(argv)
    except SystemExit:
        # argparse 의 usage/에러 종료도 advisory 계약(항상 0)으로 흡수
        # (scratch-ttl GAP3 선례 — argparse exit(2) 가 fail-open 불변식을 깨지 않게).
        #
        # ★ DONE 마커를 **이 경로에서도** 낸다 (보안테스트 F-SEC-3).
        #   실측: `--nonexistent-flag` · `--channel`(값 누락) 은 rc=0 인데 stdout 이 빈
        #   문자열이었다 — 유일 오라클인 DONE 마커가 사라져 호출자(스케줄 작업 러너)가
        #   "관측 0건" 과 "인자 오류로 미기동" 을 분별할 수 없었다. rc 는 0 그대로 둔다
        #   (INV-F 무손상 — rc 를 신호로 승격하지 않는다).
        #   `--help`(SystemExit(0)) 도 같은 줄을 낸다: 분기를 code 로 가르면 "DONE 은
        #   항상 1줄" 이라는 단순 불변식이 깨져 오라클이 다시 조건부가 된다.
        _warn("인자 파싱 단계에서 종료 — 관측 미수행 (advisory, 항상 exit 0)")
        _emit_done(0, 0, 0, 0)
        return 0
    except Exception as e:   # noqa: BLE001 — 어떤 실패도 DONE 마커 + exit 0
        _warn("최상위 예외 (non-blocking)", base.strip_control(str(e))[:160])
        _emit_done(0, 0, 0, 0)
    return 0


if __name__ == "__main__":
    sys.exit(main())
