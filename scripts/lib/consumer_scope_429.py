#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# consumer_scope_429.py — 429 incident 채널 전용 scope 판별자 (Change Plan §7.3 P0 이행체 / §5 #18)
#
# Carrier: CFP-2967 Phase 2 (구현) — Change Plan §7.3 / §11.8 잔여(술어 미확정) 확정분.
#
# 왜 전용 판별자인가 (기존 판별자 재사용 금지 — Change Plan §7.3 ★ P0):
#   `dev_process_capture_activation.py:58 resolve_consumer_scope()` → `append_dev_process_event`
#   `_norm_consumer_scope` 의 실 판정식은 **CLAUDE_PROJECT_DIR basename 문자열 휴리스틱**이다
#   (동 파일 :31 자기 자백 verbatim: "checkout-identity 파생은 CLAUDE_PROJECT_DIR basename
#   휴리스틱(wave-1 SSOT)"). 그것을 ADR-140 reuse-before-write 명목으로 재사용하면 §7.3 의
#   "env·config bool 로 판별 금지"(consumer 가 설정 가능 = 프라이버시 게이트 우회면)를 정면
#   위반한다. dev-process 채널은 오분류 피해가 host-local blob 에 갇히지만, 429 채널은
#   **repo-tracked 공개 착지면**(docs/kpi/**, mclayer/plugin-codeforge = PUBLIC)이라
#   오분류 = consumer telemetry 가 consumer repo 에 커밋 = ADR-043 §결정 1 trust 위반 그 자체다.
#
# 판정식 (술어 본문 — Phase 2 확정):
#   is_wrapper_checkout(root) := (A) <root>/.claude-plugin/plugin.json 이 정규 파일이고
#                                    JSON object 로 파싱되며 그 "name" == "codeforge"
#                               ∧ (B) <root>/archive/adr/ADR-043-*.md 정규 파일이 1개 이상 실재
#   둘 다 참일 때만 "wrapper". 그 밖 전부(부재·일부만 실재·파싱 실패·타입 불일치·예외) = "consumer".
#
# 불변식 (절대 위반 금지):
#   - **env 미consult**: 본 모듈은 os.environ 을 읽지 않는다. CLAUDE_PROJECT_DIR 을 wrapper
#     basename 으로 위조해도 판별 결과는 불변이다 (판정 입력 = 인자로 받은 repo 루트의
#     **파일시스템 사실**뿐). 호출자가 후보 루트를 env 로 *찾는* 것과, 판별을 env 값으로
#     *하는* 것은 다른 층이며 후자만 금지 대상이다.
#   - **fail-closed**: 불확정 ⇒ consumer floor. 신원 자산이 일부만 실재해도 consumer.
#     (가용성 축 fail-open 과 반대 방향 — 프라이버시 축은 fail-closed. Change Plan §7.4)
#   - 부작용 0: 파일 write·mkdir·subprocess·네트워크·동적 import 경로 부재. 읽기 전용.
#   - stdlib only. repo walk 아님 — (A) plugin.json 1회 bounded read + (B) archive/adr
#     **단일 디렉터리 non-recursive glob**(하위 재귀 0). 트리 순회 없음.
#
# 정직 천장 (ADR-119):
#   본 판별자는 "wrapper 체크아웃인가"를 **tracked 신원 자산 동시 실재**로 근사한다. 공격자가
#   자기 repo 에 두 자산을 복제하면 wrapper 로 판정된다 — 이는 자기 소유 체크아웃에 자기
#   telemetry 를 쓰는 것이라 본 위협모델(consumer telemetry 의 비의도 공개 착지)의 피해와
#   다르나, **무오류 탐지를 단정하지 않는다**. 방어 대상은 "우연·부주의한 오분류"이지
#   "의도적 신원 위조" 가 아니다.

import json
import os
from pathlib import Path

# ── wrapper 신원 자산 (tracked · repo 고유) ───────────────────────────────────
# (A) plugin manifest — name 값이 정확히 이 토큰일 때만 인정 (부분일치·대소문자 완화 금지:
#     완화는 곧 위조 표면 확대).
_PLUGIN_MANIFEST_RELPATH = (".claude-plugin", "plugin.json")
_WRAPPER_PLUGIN_NAME = "codeforge"

# (B) wrapper 고유 ADR — telemetry privacy policy ADR 자체. slug rename 내성을 위해 번호
#     prefix glob 을 쓴다(ADR renumber 선례 실재 — CFP-2566). 미매치는 fail-closed 방향
#     (wrapper → consumer 낙하 = telemetry 유실이지 유출 아님)이라 안전한 오류다.
_ADR_DIR_RELPATH = ("archive", "adr")
_WRAPPER_ADR_GLOB = "ADR-043-*.md"

# plugin.json bounded read 상한. 현행 실측 파일 = 113 KiB(description 누적)이라 약 36배 여유.
# **정직 표기**: 이것은 bounded degradation 이지 임의 입력에 대한 무해 보장이 아니다
# (상한 초과 시 판정을 시도하지 않고 consumer floor 로 낙하한다 — over-claim 금지).
_MAX_MANIFEST_BYTES = 4 * 1024 * 1024

SCOPE_WRAPPER = "wrapper"
SCOPE_CONSUMER = "consumer"


def _manifest_declares_wrapper(root):
    """(A) <root>/.claude-plugin/plugin.json 의 name 이 wrapper 토큰인가. 예외 = False."""
    try:
        manifest = root.joinpath(*_PLUGIN_MANIFEST_RELPATH)
        if not manifest.is_file():
            return False
        if manifest.stat().st_size > _MAX_MANIFEST_BYTES:
            return False  # bounded read 상한 초과 → 판정 불가 → fail-closed
        with open(str(manifest), "r", encoding="utf-8") as fh:
            data = json.load(fh)
        if not isinstance(data, dict):
            return False
        return data.get("name") == _WRAPPER_PLUGIN_NAME
    except Exception:
        return False  # 파싱 실패·권한 오류·인코딩 오류 전부 불확정 = fail-closed


def _wrapper_adr_present(root):
    """(B) <root>/archive/adr/ADR-043-*.md 정규 파일 1개 이상 실재하는가. 예외 = False."""
    try:
        adr_dir = root.joinpath(*_ADR_DIR_RELPATH)
        if not adr_dir.is_dir():
            return False
        for candidate in adr_dir.glob(_WRAPPER_ADR_GLOB):  # non-recursive (rglob 아님)
            if candidate.is_file():
                return True
        return False
    except Exception:
        return False


def is_wrapper_checkout(repo_root):
    """repo 루트가 wrapper 체크아웃인가 — 신원 자산 (A) ∧ (B) 동시 실재.

    Args:
        repo_root: 판정 대상 repo 루트 (str | os.PathLike). None·빈값 = False.

    Returns:
        bool — True 는 (A) ∧ (B) 동시 성립일 때만. 그 밖 전부 False (fail-closed).
    """
    if repo_root is None:
        return False
    try:
        raw = os.fspath(repo_root)
    except (TypeError, ValueError):
        return False
    if isinstance(raw, bytes):
        try:
            raw = raw.decode("utf-8")
        except UnicodeDecodeError:
            return False
    # ★ 빈 문자열 방어 (구현 중 firsthand 검출): Path("") 는 Path(".") 로 붕괴해 **cwd** 를
    # 가리킨다. wrapper 체크아웃 안에서 실행되면 빈 루트가 조용히 wrapper 로 판정돼
    # fail-closed 가 뚫린다. 문자열 단계에서 먼저 거른다 (Path 변환 후 검사로는 늦다).
    if not str(raw).strip():
        return False
    try:
        root = Path(raw)
    except (TypeError, ValueError):
        return False
    try:
        if not root.is_dir():
            return False
    except Exception:
        return False

    # 일부만 실재 = 불확정 = consumer (and 결합 — or 로 완화 금지).
    return _manifest_declares_wrapper(root) and _wrapper_adr_present(root)


def resolve_429_scope(repo_root):
    """429 채널 scope 판정 — 'wrapper' | 'consumer'. 불확정 ⇒ consumer floor.

    env·config 를 일절 consult 하지 않는다 (§7.3 — `resolve_consumer_scope()` 재사용 금지).
    """
    return SCOPE_WRAPPER if is_wrapper_checkout(repo_root) else SCOPE_CONSUMER


def tracked_write_allowed(repo_root):
    """공개 tracked 경로(docs/kpi/**) write 자격 — publication authorization (§7.2.a Authz (ii))."""
    return resolve_429_scope(repo_root) == SCOPE_WRAPPER
