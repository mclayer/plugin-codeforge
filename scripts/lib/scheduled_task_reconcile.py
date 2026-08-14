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

# 외부 저작 코멘트에서 취하는 dedup 키 길이 상한 (INV-D 읽기 표면 축소 — 비정상 장문 폐기).
_MAX_KEY_LEN = 512

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
_LEXICON_PLACEHOLDER = "<제거>"

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

# 사실 줄에서 dedup 키 추출 — key= 는 줄 끝 필드라 EOL 까지 포획(경로에 구분자가 섞여도
#   재유도값과 일치). greedy `.*` 가 마지막 ` · key=` 를 고르게 한다.
_FACT_KEY_RE = re.compile(r"^\s*-\s.*·\s*key=(.+?)\s*$")

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
    """verdict 어휘 토큰을 placeholder 로 치환 (INV-E 산출 강제).

    줄 제거(filter_verdict_lines)와 달리 관측 사실을 잃지 않으면서 어휘만 없앤다 —
    경로·태스크명 등 우리가 통제하지 못하는 입력에 어휘가 섞여도 산출 어휘 0 을 보장."""
    if not isinstance(s, str):
        s = "" if s is None else str(s)
    return _LEXICON_RE.sub(_LEXICON_PLACEHOLDER, s)


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
      쓴다(D3 라운드트립 계약). 정규화층을 호출부로 빼면 그 계약이 깨진다."""
    return _scrub_verdict_tokens(_normalize_paths(base.sanitize(_scrub_verdict_tokens(s))))


def _warn(msg):
    """advisory stderr 보고 (non-blocking). 본문과 동일 정규화 통과 — INV-E."""
    print("[%s] %s" % (SCRIPT_NAME, _safe_text(msg)), file=sys.stderr)


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
      다음 실행의 재유도값이 정확히 일치해 dedup 이 성립한다(roundtrip 계약)."""
    cls = _safe_text(_field(obs, "cls"))
    path = _safe_text(_field(obs, "display_path"))
    return "%s:%s" % (cls, path)


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
            _warn("관측 축 실패 (non-blocking, axis=%s): %s"
                  % (name, base.strip_control(str(e))[:160]))

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
    """★ CLI 가 관측 사이클을 실제로 돌고 정상 종료한 경로에서만 호출.
    원자적 write(임시파일 → os.replace).

    상태 디렉터리는 codeforge-scratch **밖**(worktree-gc-state)이라 자기 TTL 대상이 아니다.
    이 파일은 dedup 상태가 아니라 생존 신호다(INV-C 무손상 — 관측 대상 판정에 미사용).

    ★ 대상 경로는 **호출 시점** 판독 — path 인자 → env ENV_HEARTBEAT_FILE → HEARTBEAT_FILE.
      HEARTBEAT_FILE 은 import 시점 상수라 그것만 쓰면 subprocess 테스트가 실 사용자 파일을
      갱신한다(= 관측자 생존 신호 위조). env 축은 그 격리 seam 이며, 둘 다 부재 시 동작은
      기존과 동일하다."""
    target = path or (os.environ.get(ENV_HEARTBEAT_FILE) or "").strip() or HEARTBEAT_FILE
    n = base.now_epoch() if now is None else int(now)
    tmp = "%s.tmp" % target
    try:
        parent = os.path.dirname(target)
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
            fh.write("%d\n" % n)
        os.replace(tmp, target)
    except OSError as e:
        _warn("heartbeat 기록 실패 (non-blocking): %s" % base.strip_control(str(e))[:120])
        try:
            if os.path.exists(tmp):
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
      5) heartbeat 는 관측 사이클을 실제로 돈 종료 경로에서만 기록 — **--dry-run 제외**.
         (dry-run 은 부수효과 0 계약이며 보고 사이클 미완결이라 생존 신호 근거가 없다.)"""
    args = _build_parser().parse_args(argv)
    repo_root = args.repo_root or _git_toplevel() or os.getcwd()

    # (1) 정지 플래그 — 스캐너 호출 전 (halted ⇒ 채널 발화 0 ∧ 스캐너 미호출)
    stop = read_stop_flags(repo_root=repo_root)
    if stop.halted:
        _warn("정지 플래그 감지 (%s) — 스캐너 미호출 · 채널 미접촉"
              % ",".join(stop.reasons or ["unknown"]))
        write_heartbeat()
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
    """항상 0 반환 (exit code 를 오라클로 쓰지 않는 관례 상속 — INV-F)."""
    try:
        run(argv)
    except SystemExit:
        # argparse 의 usage/에러 종료도 advisory 계약(항상 0)으로 흡수
        # (scratch-ttl GAP3 선례 — argparse exit(2) 가 fail-open 불변식을 깨지 않게).
        return 0
    except Exception as e:   # noqa: BLE001 — 어떤 실패도 DONE 마커 + exit 0
        _warn("최상위 예외 (non-blocking): %s" % base.strip_control(str(e))[:160])
        _emit_done(0, 0, 0, 0)
    return 0


if __name__ == "__main__":
    sys.exit(main())
