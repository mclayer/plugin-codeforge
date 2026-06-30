"""
scripts/lib/fix_replay_disposition.py
CFP-2480 (Epic CFP-2476 E3) — FIX ground-truth replay close-gate disposition 결정 SSOT (순수 함수)

기능:
  FIX "수정됨" 닫기 시점에, 원 finding 을 정당화한 reproducer 재실행 결과(packet)를
  입력받아 close 허용/거부 disposition 을 결정론적으로 산출하는 *순수 함수* SSOT.
  Orchestrator(§10 FIX Ledger writer monopoly)가 close 판정을 본 함수에 위임(SSOT)하고,
  discriminating test (tests/scripts/test-check-fix-replay-disposition.sh)가 INV-FR1~5 +
  INV-FR-FLAKY-1~3 별 RED→GREEN 변별을 강제 검증한다 (anti-theater / mutation-kill).

  regex-free, deterministic, 외부 의존 0 (stdlib json/argparse/sys 만).

  Story A(check_merge_gate_disposition.py) + Story B(check_mutation_disposition.py)
  패턴 답습 — 단, disposition axis 가 다르다:
    A = merge-time fail-mode disposition (PASS/BLOCKED/DEGRADED_PASS, ADR-070 §결정 D7)
    B = mutation surviving-mutant disposition (hollow_gate_verified/undetermined/
        rejected_false_positive, ADR-070 §결정 D8)
    본 파일 = FIX-close replay disposition (PASS/falsified/replay-impossible/undetermined,
        ADR-070 §결정 D9 3-상태의 FIX-close 시점 적용 — fix-event-v1 v1.4 replay_verdict).
  세 axis 는 disjoint.

── 입력 (JSON, stdin 또는 fixture 파일 인자) ──
  {
    "findings": [
      {
        "id": "<finding 식별자>",
        "reproducer_present": bool,            # F-2: reproducer_command 가 finding 생성 시점에 기록되었는가
        "reproducible": bool,                  # 실행 가능 명령으로 환원 가능한 finding 인가
                                               #   (false = 코드 P1 가독성 등 환원불가 → replay-impossible)
        "replay_impossible_reason": "<사유>"|null,  # reproducible=false 시 사유 (INV-FR2 — silent 면제 차단)
        "replay_runs": ["green"|"red", ...],   # 원 reproducer 다회 재실행 결과 (INV-FR-FLAKY: 결정론 확인)
        "deterministic_runs_required": int,    # 결정론 확인 의무 횟수 (하드코딩 금지 — 설정값, §8 Perf Baseline)
        "pl_falsified": bool,                  # F-4: 실행자≠판정자 — PL/Orchestrator 직접 재현 falsify 통과
        "base_sha_present": bool,              # InfraOp SHA-pin — reproduce-before-fix 결정론 기준 동반
        "reproducer_command_value": "<명령>"|null  # (선택) reproducer_command 실 명령 문자열.
                                               #   제공 시 INV-SEC-1 content schema 강제 (repo-relative 게이트/테스트
                                               #   호출만, raw shell·URL·절대경로·secret 거부 — THR-E3-2 stored-command
                                               #   injection 차단). reproducer_present=true + 값 제공 시 검증 (SETUP error
                                               #   exit 2 시 schema 위반). 미제공 = boolean present 검사만 (backward-compat).
      },
      ...
    ],
    "codex_available": bool                    # fail-mode (B)축: false = Codex 미가용 (replay 실행 자체 불가)
  }

── 출력 disposition enum (fix-event-v1 v1.4 replay_verdict — ADR-070 §결정 D9 3-상태 정합 매핑) ──
  "PASS"               — 반증 통과. 원 reproducer 가 결정론적으로 GREEN 재현 + PL falsify 통과 →
                         close 허용 (F-1 Retest GREEN). (D9 inverse — 모순 해소가 verified)
  "falsified"          — 여전히 RED. 원 reproducer 가 결정론적으로 RED 재현 → close 거부
                         (수정이 실제로 안 됨 — fail-mode (A)축 fail-closed, degrade 없음).
  "replay-impossible"  — 실행 가능 명령으로 환원 불가한 finding (코드 P1 등). replay 면제하되
                         사유 명시 의무 (INV-FR2 — silent 면제 차단). close 별도 경로(사람 검토).
  "undetermined"       — flaky 의심 (다회 재실행 mixed 또는 결정론 횟수 미충족) — 자동 PASS/falsified
                         금지, 보류 (quarantine). false-GREEN(부당close)+false-RED(max-FIX 부당소진)
                         양방향 차단 (D9(b) 동형).

── disposition 결정 규칙 (Story §8 invariant SSOT — ADR-070 §결정 D9 / fix-event-v1 v1.4) ──
  INV-FR1 (close=Retest GREEN 만 — F-1):
    PASS disposition 은 원 reproducer 가 GREEN 재현 + 결정론 확인 + PL falsify 통과 시만.
    falsified(RED) finding 은 close 허용 disposition(PASS) 불가.
  INV-SEC-1 (reproducer_command content schema 강제 — THR-E3-2 stored-command injection 차단):
    reproducer_command_value 제공 시 = repo-relative 게이트/테스트 호출만 허용
    (bash scripts/check-*.sh / pytest tests/... / python scripts/... / node ... 형태).
    raw shell 메타문자(; | && ` $( > <)·URL·절대경로·secret-shaped(--token 등) 거부 =
    SETUP error(ValueError, exit 2). disposition 분기보다 앞선 입력검증 단계
    (content 검증 = 입력 형식 검증이지 disposition 판정 아님). INV-SEC-1 = §7.5 SecurityArch
    PII/secret/credential 금지 + §7.6 THR-E3-2 stored-command injection vector 차단의 코드 enforcement.
  INV-FR2 (replay-impossible silent 면제 차단 — F-2):
    reproducible=false 인 finding 은 replay-impossible disposition 이되,
    replay_impossible_reason 동반 의무. 사유 부재 = SETUP error(ValueError, exit 2) —
    silent 면제 경로 0.
  INV-FR3 (reproducer 부재 → close 불가 — F-2):
    reproducible=true 이나 reproducer_present=false (또는 base_sha_present=false) =
    replay 불능 → PASS 불가 (undetermined 보류, 자동 close 금지).
  INV-FR4 (provenance 동반 — Story A INV-G4 동형):
    모든 disposition 은 provenance metadata 를 동반 반환한다. artifact 없이 close(PASS) 경로 0.
  INV-FR5 (실행자 ≠ 판정자 — F-4):
    pl_falsified=false 인 finding 은 PASS 불가 (Codex replay 보고만으로 close 금지 →
    undetermined 보류). PL 직접 재현 falsify 통과 시만 PASS.

  INV-FR-FLAKY-1 (false-GREEN 차단 — 다회 확인 후만 close, 1회 GREEN 금지):
    replay_runs 가 deterministic_runs_required 미만 = 결정론 미확인 → undetermined.
    (1회 GREEN 으로 close = §1 목적 정면 훼손, 최위험.)
  INV-FR-FLAKY-2 (false-RED 차단 — mixed → quarantine, max-FIX 부당소진 방지):
    replay_runs 가 green/red 혼재 (mixed) → undetermined (quarantine). falsified 단정 금지
    (flaky 가 max-FIX 3/3 부당 소진하지 않게 — replay 는 max-FIX 카운터와 disjoint).
  INV-FR-FLAKY-3 (전부 green AND 충분 횟수 AND pl_falsified → PASS / 전부 red AND 충분 횟수 → falsified):
    replay_runs 가 충분 횟수 전부 green + pl_falsified=true → PASS.
    replay_runs 가 충분 횟수 전부 red → falsified (PL falsify 무관 — RED 는 close 거부 정답).

  우선순위 (각 finding 별 독립 판정):
    INV-SEC-1 (reproducer content schema — 입력검증, disposition 판정보다 앞) →
    INV-FR2 (replay-impossible) → INV-FR3 (reproducer/SHA 부재) → INV-FR-FLAKY-1 (횟수 미충족)
    → INV-FR-FLAKY-2 (mixed) → INV-FR-FLAKY-3 (all-red=falsified / all-green) → INV-FR5 (PL falsify).
    INV-SEC-1 = SETUP error 라 disposition 분기보다 앞선 입력검증 단계 (모든 finding 의 reproducer
    content 를 finding loop 진입 직전 일괄 검증). 그 다음 환원 불가가 최우선(replay 자체 부적용),
    그 다음 reproducer 전제, 그 다음 flaky 필터, 마지막으로 결정론 확정 후 PL falsify 게이트.

── fail-mode (B)축 — Codex 미가용 (replay 실행 자체 불가) ──
  codex_available=false → lane-time `fail_open_then_record_with_marker`
    (marker `[fix-replay-fallback: fail-mode=codex_unavailable, disposition=open]` 기록 후 진행).
  fail-mode (A)축(replay-verdict = 여전히 RED)의 fail-closed(falsified, 닫기 거부)와 disjoint:
    (A) = 수정이 실제로 안 됨 → 닫기 거부가 정답 (degrade 없음, fail-open reject)
    (B) = replay 실행 자체 불가 → 영구보류=delivery 마비 → lane-time fail-open + marker
  (merge-time #7 의 fail-closed-then-bounded-degrade 와 다름 — #7 degrade 는 (B)축용,
   FIX replay (A)축은 degrade 대상 아님. ADR-070 Amd9/10/11 §D7/D8/D9 동형.)

── 출력 형식 ──
  stdout: JSON {"dispositions": [{"id", "disposition"}], "provenance": {...}}  (INV-FR4)
  exit:   0 = close-허용 계열 없음 차단 (PASS 0 / 전부 replay-impossible·undetermined) +
              codex 미가용 fail-open — 정상 진행 신호
          1 = close 거부(falsified) 1+ 검출 — 테스트용 보류 신호(non-zero)
          2 = SETUP error (입력 malformed / reason 부재 / 파일 read 실패 / JSON decode 실패)
  (테스트는 disposition 문자열을 직접 assert 하여 exit code 모호성을 회피한다.)

Exit-code 3-tier (ADR-060 §결정 15 동형):
  0 = 닫기 거부 trigger 없음 (PASS/impossible/undetermined/fail-open) / 1 = falsified 검출 / 2 = SETUP

Prior art: scripts/lib/check_merge_gate_disposition.py (CFP-2458) +
  scripts/lib/check_mutation_disposition.py (CFP-2464 — undetermined 3-상태 + lane-time fail-open).
naming: fix_replay_* (scripts/lib/replay_spawn_event.py = agent-spawn cost replay 와 충돌 회피).
"""

import argparse
import json
import sys
from typing import Any

# Windows cp949 stdout encoding 차단 (CFP-1393 F8-FU / ADR-061 standardize)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
SCRIPT_NAME = "fix_replay_disposition"

# disposition enum (fix-event-v1 v1.4 replay_verdict — ADR-070 §결정 D9 정합)
PASS = "PASS"
FALSIFIED = "falsified"
REPLAY_IMPOSSIBLE = "replay-impossible"
UNDETERMINED = "undetermined"

# lane-time fail-open marker (fail-mode (B)축 — Codex 미가용)
_FAIL_OPEN_MARKER = "fix-replay-fallback"

_VALID_RUN_RESULTS = frozenset({"green", "red"})

# ── INV-SEC-1: reproducer_command content schema (THR-E3-2 stored-command injection 차단) ──
#   repo-relative 게이트/테스트 호출만 허용 — 알려진 runner 로 시작하는 명령.
#   regex-free 우선 (stdlib only). 거부는 set membership / startswith / substring 만 (ReDoS-safe).
_ALLOWED_RUNNERS = frozenset({"bash", "sh", "pytest", "python", "python3", "node", "npm", "npx"})

# raw shell 메타문자 (명령 연쇄 / 파이프 / 리다이렉트 / command substitution) — INV-SEC-1 거부.
_SHELL_METACHARS = (";", "|", "&", "`", "$(", "${", ">", "<", "\n", "\r", "\\")

# URL scheme — 네트워크 fetch vector 거부 (network-off invariant).
_URL_SCHEMES = ("http://", "https://", "ftp://", "file://", "ssh://", "git://")

# secret-shaped token — INV-SEC-1 PII/secret/credential 금지.
_SECRET_TOKENS = ("--token", "--password", "--passwd", "--secret", "--apikey", "--api-key",
                  "apikey=", "api_key=", "password=", "token=", "secret=")

# ── F-CR-CL-001 hardening (구현리뷰 P2 — declaration↔enforcement self-gap 해소) ──
#   runner 뒤 inline-code 실행 플래그 = repo-relative 게이트/테스트 호출 아닌 *임의 코드 실행* vector
#   (raw shell free-string reproducer anti-pattern, concept fix-ground-truth-replay.md). 거부.
#   예: `python -c <code>` / `node -e <code>` / `sh -c <code>` / `python -i` / `--command` / `--eval`.
_INLINE_EXEC_FLAGS = frozenset({"-c", "-e", "-i", "--command", "--eval"})

# repo prefix 화이트리스트 — repo-relative path 는 알려진 top-level dir 로 시작 의무 (path 인자 한정).
#   `..` traversal 거부 + 본 prefix 미시작 path 거부 (over-block 회피 위해 path-shaped 인자만 검사).
_REPO_PATH_PREFIXES = ("scripts/", "tests/", "docs/", "archive/", "plugins/", "skills/", "templates/")


def _validate_reproducer_command(value: str) -> None:
    """INV-SEC-1: reproducer_command content schema 강제 (THR-E3-2 stored-command injection 차단).

    허용 (PASS schema): repo-relative 게이트/테스트 호출 — 알려진 runner 로 시작 +
      repo-relative path (알려진 top-level dir 시작, 절대경로/Windows drive/`..` traversal 금지).
      예: `bash scripts/check-*.sh`, `pytest tests/...`, `python scripts/...`, `node templates/...`.
    거부 (SETUP error → ValueError → CLI exit 2, TC-6 ValueError 동형):
      raw shell 메타문자(명령 연쇄/파이프/리다이렉트/command substitution) / URL /
      절대경로(POSIX `/` 시작 또는 Windows `C:\\`) / secret-shaped 토큰 /
      **runner 직후 inline-code 실행 플래그(`-c`/`-e`/`-i`/`--command`/`--eval` — 임의 코드 실행 vector,
      F-CR-CL-001)** / **`..` path traversal** / **알려진 repo prefix 미시작 path**.

    regex-free / stdlib only — startswith / substring membership 만 (ReDoS-safe anchored simple).

    Args:
        value: reproducer_command 실 명령 문자열.

    Raises:
        ValueError: schema 위반 (CLI 가 exit 2 SETUP error 로 변환 — TC-6 reason-부재 동형).
    """
    if not isinstance(value, str) or not value.strip():
        raise ValueError(
            "reproducer_command schema 위반: 빈 명령 — repo-relative 게이트/테스트 호출만 "
            "(INV-SEC-1 / THR-E3-2)"
        )
    cmd = value.strip()
    low = cmd.lower()

    # ① raw shell 메타문자 (명령 연쇄 / 파이프 / 리다이렉트 / command substitution) 거부
    for meta in _SHELL_METACHARS:
        if meta in cmd:
            raise ValueError(
                f"reproducer_command schema 위반: raw shell 메타문자 '{meta}' (명령 연쇄/파이프/"
                "리다이렉트 금지) — repo-relative 게이트/테스트 호출만 (INV-SEC-1 / THR-E3-2)"
            )

    # ② URL (네트워크 fetch vector) 거부
    for scheme in _URL_SCHEMES:
        if scheme in low:
            raise ValueError(
                f"reproducer_command schema 위반: URL scheme '{scheme}' (network fetch 금지) — "
                "repo-relative 게이트/테스트 호출만 (INV-SEC-1 / THR-E3-2)"
            )

    # ③ secret-shaped 토큰 (PII/secret/credential) 거부
    for tok in _SECRET_TOKENS:
        if tok in low:
            raise ValueError(
                f"reproducer_command schema 위반: secret-shaped 토큰 '{tok}' (credential 금지) — "
                "repo-relative 게이트/테스트 호출만 (INV-SEC-1 / THR-E3-2)"
            )

    # ④ runner + path 검증: 첫 토큰 = 알려진 runner, 이후 토큰 = repo-relative path (절대경로 금지)
    tokens = cmd.split()
    runner = tokens[0]
    if runner not in _ALLOWED_RUNNERS:
        raise ValueError(
            f"reproducer_command schema 위반: 알려지지 않은 runner '{runner}' "
            f"(허용: {sorted(_ALLOWED_RUNNERS)}) — repo-relative 게이트/테스트 호출만 "
            "(INV-SEC-1 / THR-E3-2)"
        )
    # ⑤ F-CR-CL-001: runner 직후 inline-code 실행 플래그 거부 (임의 코드 실행 vector 차단).
    #   `python -c <code>` / `node -e <code>` / `sh -c <code>` = repo-relative 게이트/테스트 호출 아님.
    #   첫 인자(runner 직후)가 inline-exec 플래그면 reject (게이트/테스트는 path 인자로 시작).
    if len(tokens) >= 2 and tokens[1] in _INLINE_EXEC_FLAGS:
        raise ValueError(
            f"reproducer_command schema 위반: inline-code 실행 플래그 '{tokens[1]}' "
            "(임의 코드 실행 vector — repo-relative 게이트/테스트 호출만, raw free-string reproducer 금지) "
            "(INV-SEC-1 / THR-E3-2 / F-CR-CL-001)"
        )

    for arg in tokens[1:]:
        # F-CR-CL-001: `..` path traversal 거부 (repo 외부 escape vector).
        if ".." in arg.split("/") or ".." in arg.split("\\"):
            raise ValueError(
                f"reproducer_command schema 위반: '..' path traversal '{arg}' (repo escape 금지) — "
                "repo-relative path 만 (INV-SEC-1 / THR-E3-2 / F-CR-CL-001)"
            )
        # POSIX 절대경로 (`/` 시작) 또는 Windows drive 절대경로 (`C:\` / `C:/`) 거부
        if arg.startswith("/"):
            raise ValueError(
                f"reproducer_command schema 위반: 절대경로 '{arg}' (POSIX absolute) — "
                "repo-relative path 만 (INV-SEC-1 / THR-E3-2)"
            )
        if len(arg) >= 3 and arg[1] == ":" and arg[2] in ("\\", "/"):
            raise ValueError(
                f"reproducer_command schema 위반: 절대경로 '{arg}' (Windows drive) — "
                "repo-relative path 만 (INV-SEC-1 / THR-E3-2)"
            )
        # ⑥ F-CR-CL-001: path-shaped 인자 (separator 포함) 는 알려진 repo prefix 시작 의무.
        #   over-block 회피: flag(`-`/`--`) 와 separator 없는 단순 토큰(예: pytest node-arg)은 비검사.
        is_path_shaped = ("/" in arg or "\\" in arg)
        if is_path_shaped and not arg.startswith("-"):
            if not arg.startswith(_REPO_PATH_PREFIXES):
                raise ValueError(
                    f"reproducer_command schema 위반: repo prefix 미시작 path '{arg}' "
                    f"(허용 prefix: {list(_REPO_PATH_PREFIXES)}) — repo-relative 게이트/테스트 호출만 "
                    "(INV-SEC-1 / THR-E3-2 / F-CR-CL-001)"
                )


# ---------------------------------------------------------------------------
# 순수 결정 함수 (SSOT) — 부수효과 0, 입력 dict → (dispositions, provenance) 튜플
# ---------------------------------------------------------------------------
def decide_replay_disposition(packet: dict) -> tuple[list[dict], dict]:
    """FIX-close replay 재실행 결과 → (dispositions, provenance) 결정.

    순수 함수 — I/O / 전역 상태 / 시간 의존 0. 같은 입력 → 항상 같은 출력.
    INV-FR1~5 + INV-FR-FLAKY-1~3 의 단일 출처.

    Args:
        packet: 입력 dict (findings / codex_available).

    Returns:
        (dispositions_list, provenance_dict).
        dispositions_list = [{"id", "disposition"}] (finding 별 독립 판정).
        provenance 는 INV-FR4 — 모든 경로에 동반 (artifact 없이 close 경로 0).

    Raises:
        ValueError: 입력 malformed / replay-impossible reason 부재 (CLI 가 exit 2 변환).
    """
    if not isinstance(packet, dict):
        raise ValueError("packet must be a JSON object")

    codex_available = packet.get("codex_available", True)
    if not isinstance(codex_available, bool):
        raise ValueError("codex_available must be a boolean")

    findings = packet.get("findings", [])
    if not isinstance(findings, list):
        raise ValueError("findings must be a list")

    # ── fail-mode (B)축 — Codex 미가용 → lane-time fail-open ──
    #   replay 실행 자체 불가 → 영구보류=delivery 마비 → marker 기록 후 lane 진행.
    #   fail-mode (A)축(falsified, 닫기 거부)과 disjoint — (A)=수정 안 됨/(B)=실행 불가.
    if codex_available is False:
        provenance = _provenance(
            rule="fail-open(B)/codex_unavailable",
            reason=(
                "codex_available=false → lane-time fail-open "
                f"(marker `[{_FAIL_OPEN_MARKER}: fail-mode=codex_unavailable, disposition=open]` "
                "기록 후 lane 진행, replay 미수행 — (A)축 falsified[닫기 거부]와 disjoint)"
            ),
            findings_attempted=len(findings),
            pass_count=0,
            falsified_count=0,
            impossible_count=0,
            undetermined_count=0,
            codex_available=False,
            fail_open=True,
        )
        return [], provenance

    # ── finding 별 독립 disposition 판정 ──
    dispositions: list[dict] = []
    pass_count = 0
    falsified_count = 0
    impossible_count = 0
    undetermined_count = 0

    for f in findings:
        if not isinstance(f, dict):
            raise ValueError("each finding must be a JSON object")

        # ── INV-SEC-1 입력검증 (disposition 판정보다 앞): reproducer_command content schema ──
        #   reproducer_command_value 제공 시 repo-relative 게이트/테스트 호출 schema 강제.
        #   reproducer_present=true 인데 값 제공 → schema 위반 시 SETUP error (THR-E3-2 차단).
        repro_value = f.get("reproducer_command_value")
        if repro_value is not None:
            _validate_reproducer_command(repro_value)

        disposition = _decide_one(f)
        dispositions.append({"id": f.get("id"), "disposition": disposition})

        if disposition == PASS:
            pass_count += 1
        elif disposition == FALSIFIED:
            falsified_count += 1
        elif disposition == REPLAY_IMPOSSIBLE:
            impossible_count += 1
        else:  # UNDETERMINED
            undetermined_count += 1

    provenance = _provenance(
        rule="INV-FR1..5/FLAKY-1..3",
        reason=(
            f"finding {len(findings)}건 판정 → PASS={pass_count} / "
            f"falsified={falsified_count} / replay-impossible={impossible_count} / "
            f"undetermined={undetermined_count}"
        ),
        findings_attempted=len(findings),
        pass_count=pass_count,
        falsified_count=falsified_count,
        impossible_count=impossible_count,
        undetermined_count=undetermined_count,
        codex_available=True,
        fail_open=False,
    )
    return dispositions, provenance


def _decide_one(f: dict) -> str:
    """단일 finding → disposition 판정.

    우선순위 (INV-FR2 → INV-FR3 → INV-FR-FLAKY-1 → INV-FR-FLAKY-2 → INV-FR-FLAKY-3 → INV-FR5):
      1. reproducible=false → replay-impossible (reason 의무 — INV-FR2)
      2. reproducer_present=false OR base_sha_present=false → undetermined (replay 불능 — INV-FR3)
      3. replay_runs 횟수 < deterministic_runs_required → undetermined (1회 GREEN 금지 — FLAKY-1)
      4. replay_runs mixed (green+red 혼재) → undetermined (quarantine — FLAKY-2)
      5. replay_runs 전부 red → falsified (닫기 거부 — RED 는 PL falsify 무관, FLAKY-3 / (A)축)
      6. replay_runs 전부 green AND pl_falsified=true → PASS (close 허용 — F-1/FLAKY-3/INV-FR5)
         replay_runs 전부 green AND pl_falsified!=true → undetermined (PL 미falsify — INV-FR5)
    """
    reproducible = f.get("reproducible")

    # ── INV-FR2 (최우선): 환원 불가 finding → replay-impossible (silent 면제 차단) ──
    if reproducible is False:
        reason = f.get("replay_impossible_reason")
        if not (isinstance(reason, str) and reason.strip()):
            raise ValueError(
                "reproducible=false finding 은 replay_impossible_reason(비어있지 않은 string) "
                "의무 — silent 면제 차단 (INV-FR2)"
            )
        return REPLAY_IMPOSSIBLE

    # 여기 도달 = reproducible=true (또는 누락 — 아래 전제 가드가 흡수)

    # ── INV-FR3: reproducer / base SHA 부재 → replay 불능 → undetermined (자동 close 금지) ──
    if f.get("reproducer_present") is not True:
        return UNDETERMINED  # reproducer_command 미기록 (F-2 reproduce-before-fix 위반)
    if f.get("base_sha_present") is not True:
        return UNDETERMINED  # base SHA-pin 부재 (결정론 기준 부재)

    # ── replay_runs 결정론 확인 (FLAKY-1/2/3) ──
    runs = f.get("replay_runs")
    required = f.get("deterministic_runs_required")
    if not isinstance(runs, list) or not isinstance(required, int) or required < 1:
        # replay_runs 미수집 또는 결정론 횟수 미설정 = 확정 불가 → undetermined 안전 강등
        return UNDETERMINED
    for r in runs:
        if r not in _VALID_RUN_RESULTS:
            return UNDETERMINED  # 비정상 run 결과 (확정 불가)

    # INV-FR-FLAKY-1: 횟수 미충족 → undetermined (1회 GREEN close 금지, false-GREEN 차단)
    if len(runs) < required:
        return UNDETERMINED

    all_green = all(r == "green" for r in runs)
    all_red = all(r == "red" for r in runs)

    # INV-FR-FLAKY-2: mixed (green+red 혼재) → undetermined (quarantine, false-RED max-FIX 보호)
    if not all_green and not all_red:
        return UNDETERMINED

    # INV-FR-FLAKY-3 (all-red): 충분 횟수 전부 RED → falsified (닫기 거부, (A)축 fail-closed)
    #   RED 는 수정이 실제로 안 됨 → PL falsify 무관하게 close 거부가 정답.
    if all_red:
        return FALSIFIED

    # 여기 도달 = all_green (충분 횟수 전부 GREEN — Retest GREEN 후보)

    # ── INV-FR5: 실행자 ≠ 판정자 — PL 직접 재현 falsify 통과 시만 PASS ──
    if f.get("pl_falsified") is not True:
        return UNDETERMINED  # Codex replay 보고만으로 close 금지 (보류)

    # INV-FR1/FLAKY-3: all-green + 충분 횟수 + PL falsify → PASS (close 허용)
    return PASS


def _provenance(
    *,
    rule: str,
    reason: str,
    findings_attempted: int,
    pass_count: int,
    falsified_count: int,
    impossible_count: int,
    undetermined_count: int,
    codex_available: bool,
    fail_open: bool,
) -> dict:
    """INV-FR4 — disposition 동반 provenance metadata 구성.

    모든 경로가 본 함수를 거쳐 artifact 를 동반 — artifact 없이 close(PASS) 반환 경로 0.
    """
    return {
        "script": SCRIPT_NAME,
        "rule": rule,
        "reason": reason,
        "findings_attempted": findings_attempted,
        "pass_count": pass_count,
        "falsified_count": falsified_count,
        "impossible_count": impossible_count,
        "undetermined_count": undetermined_count,
        "codex_available": codex_available,
        "fail_open": fail_open,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def _read_input(path: str | None) -> str:
    """fixture 파일 인자가 있으면 파일에서, 없으면 stdin 에서 raw JSON 읽기."""
    if path:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return sys.stdin.read()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog=SCRIPT_NAME,
        description="FIX ground-truth replay close-gate disposition SSOT (CFP-2480)",
    )
    parser.add_argument(
        "fixture",
        nargs="?",
        default=None,
        help="입력 JSON 파일 경로 (미지정 시 stdin 에서 읽음)",
    )
    args = parser.parse_args(argv)

    # ── 입력 read + parse (SETUP error = exit 2) ──
    try:
        raw = _read_input(args.fixture)
    except OSError as exc:
        print(
            json.dumps({"error": f"입력 파일 read 실패: {exc}", "exit_code": 2}),
            file=sys.stderr,
        )
        return 2

    try:
        packet = json.loads(raw)
    except json.JSONDecodeError as exc:
        print(
            json.dumps({"error": f"JSON decode 실패: {exc}", "exit_code": 2}),
            file=sys.stderr,
        )
        return 2

    # ── 결정 (malformed 입력 / reason 부재 = ValueError → exit 2 SETUP error) ──
    try:
        dispositions, provenance = decide_replay_disposition(packet)
    except ValueError as exc:
        print(
            json.dumps({"error": f"입력 malformed: {exc}", "exit_code": 2}),
            file=sys.stderr,
        )
        return 2

    # ── 출력 (INV-FR4 — provenance artifact 동반) ──
    print(json.dumps({"dispositions": dispositions, "provenance": provenance}))

    # ── exit code (3-tier): falsified 1+ 면 닫기 거부 신호 (non-zero) ──
    if provenance["falsified_count"] > 0:
        return 1  # close 거부(falsified) 검출 (보류 계열 신호)
    return 0  # 닫기 거부 trigger 없음 (PASS / impossible / undetermined / fail-open)


if __name__ == "__main__":
    sys.exit(main())
