#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# tier: [observability]
# emit_branch_heartbeat.py — CFP-2772 Phase 2: per-branch liveness heartbeat emit (agent-emit 스타일)
#
# 설계 SSOT: ADR-164 §결정 3(per-branch pinned 코멘트 + microformat) / §결정 5(monotonic seq 3-state,
#   durable read-back+1, F-6 seq=0 reset 금지) / §결정 8(bounded 3-tuple + 14-rule redaction floor 상속)
#   + internal-docs change-plan cfp-2772 §5 / §11.6(idempotency).
#
# 책임 (D1 emit):
#   병렬/백그라운드 브랜치 세션이 자기 정체(branch_key = git ref 파생 slug)를 아는 지점에서 coarse
#   liveness tick 을 emit 한다. per-branch strictly-monotonic seq(durable read-back+1)를 얹어,
#   외부 watchdog 가 seq strict-advance = 유일 "live" 증거(clock-무관, replay 위조 불가)로 판정하게 한다.
#   본문은 heartbeat-format.sh(단일 포맷 SSOT)를 호출해 생성 — split-brain 방지(포맷 문자열 복제 금지).
#
# 경계:
#   본 스크립트는 Jira/MCP 를 호출하지 않는다. 생성한 코멘트 본문을 stdout 으로 내보내고, 실제
#   addComment(Jira 도달)은 jira-progress-mirror skill / Orchestrator(ADR-099 narrow-allow addComment)가
#   소비한다. → 무자격 3자 emit 표면 부재(§7 T-HB-2).
#
# record-only / non-blocking / exit-0 ALWAYS (ADR-115 / AC-8):
#   어떤 내부 오류도 브랜치의 실제 작업 흐름을 block 하지 않는다 — 실패 시 stderr note + exit 0.
#   observability 가 개발 흐름을 절대 차단하지 않는다.
#
# PAYLOAD ALLOW-LIST (AC-2): 본문은 {branch_key, seq, story, lane, ts, state} 만 담는다 — tool call /
#   prompt / diff / telemetry 미포함. bounded 3-tuple construction(format SSOT)이 free-form 을 구조적
#   차단(경로/이메일/자격증명 인코딩 불능). 14-rule redaction floor 는 개념적으로 상속(ADR-043/AC-8).

import argparse
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

# Windows cp949 stdout/stderr 인코딩 차단 (ADR-061 portability)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

SCRIPT_NAME = "emit_branch_heartbeat"

# heartbeat-format.sh (마이크로포맷 단일 SSOT) 경로 — scripts/lib/ → scripts/jira-channel/
_FORMAT_SCRIPT = Path(__file__).resolve().parent.parent / "jira-channel" / "heartbeat-format.sh"

# branch_key slug charset (git ref 파생 · caller override 수용 게이트) — format SSOT 와 동일.
_SLUG_RE = re.compile(r"^[a-z0-9-]+$")

# 기본 ledger dir (gitignored `.claude/ledger/` 하위) — restart 생존 per-branch seq durable state.
_DEFAULT_LEDGER_SUBPATH = os.path.join(".claude", "ledger", "heartbeat")

# probe 모드: 순수 stdout, seq 파일 포함 side-effect 0.
_PROBE_ENV = "CBL_SKIP_ISSUE_CREATE"


def _warn(msg: str) -> None:
    sys.stderr.write(f"[{SCRIPT_NAME}] WARN: {msg}\n")


def _is_wsl_relay(path: str) -> bool:
    """Windows WSL 릴레이(System32\\bash.exe) / Store alias(WindowsApps) 판별 — POSIX bash 아님."""
    n = path.replace("\\", "/").lower()
    return "/windows/system32/" in n or "/windowsapps/" in n


def _resolve_bash() -> str:
    """POSIX bash 절대경로 해석 (cross-platform). ★ 바 'bash' 를 subprocess 에 넘기면 Windows
    CreateProcess 탐색순서상 System32\\bash.exe(WSL 릴레이)가 PATH 의 Git Bash 보다 먼저 잡혀
    execvpe(/bin/bash) 실패 → 절대경로로 회피. Linux/CI 는 shutil.which('bash')=/usr/bin/bash 그대로."""
    override = os.environ.get("CFP_BASH")
    if override and os.path.exists(override):
        return override
    w = shutil.which("bash")
    if w and not _is_wsl_relay(w):
        return w
    for c in (
        r"C:\Program Files\Git\usr\bin\bash.exe",
        r"C:\Program Files\Git\bin\bash.exe",
        r"C:\Program Files (x86)\Git\usr\bin\bash.exe",
        "/usr/bin/bash", "/bin/bash",
    ):
        if os.path.exists(c):
            return c
    return w or "bash"  # last resort (Linux where bare bash works)


def _run(cmd: list) -> tuple:
    """subprocess 실행 → (rc, stdout, stderr). 실패는 raise 하지 않고 (rc, ...) 로 반환."""
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
        return r.returncode, r.stdout, r.stderr
    except FileNotFoundError as exc:
        return 127, "", str(exc)
    except Exception as exc:  # pragma: no cover — 방어적 non-blocking
        return 1, "", str(exc)


def _slugify(raw: str) -> str:
    """git ref short-name → slug: lowercase → non-[a-z0-9-]→'-' → 연속 '-' 축약 → 양끝 '-' strip."""
    s = raw.strip().lower()
    s = re.sub(r"[^a-z0-9-]+", "-", s)
    s = re.sub(r"-{2,}", "-", s)
    s = s.strip("-")
    return s


def derive_branch_key(override):
    """branch_key 도출. override 는 이미 slug charset 이면만 수용(git ref name — free-text 아님),
    아니면 무시하고 git rev-parse 파생으로 fallback(non-blocking). 도출 실패 → None."""
    if override:
        if _SLUG_RE.match(override):
            return override
        _warn(f"--branch override '{override}' 는 slug charset(^[a-z0-9-]+$) 아님 — 무시하고 git 파생 fallback")
    rc, out, err = _run(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    if rc != 0 or not out.strip():
        _warn(f"git rev-parse 실패(rc={rc}) — branch_key 도출 불가: {err.strip()[:120]}")
        return None
    slug = _slugify(out)
    if not slug:
        _warn(f"branch ref '{out.strip()}' slugify 결과 공백 — branch_key 도출 불가")
        return None
    return slug


def _seq_file(ledger_dir: Path, slug: str) -> Path:
    return ledger_dir / f"{slug}.seq"


def read_durable_seq(seq_path: Path):
    """durable seq read-back. 반환 (last_durable:int, ok:bool).
    - 파일 부재 → (0, True): 최초 emit(seq=1).
    - 파일 존재·정수 → (n, True).
    - 파일 존재·손상/판독불능/비정수 → (None, False): F-6 — seq=0 reset 금지, emit 억제(false-fresh 방지)."""
    # ledger 디렉터리 접근 불가(예: 권한 0o444 no-exec → os.stat EACCES; Path.exists() 는 EACCES 를
    # _ignore_error 하지 않고 re-raise) 는 "최초 emit(부재)" 로 degrade — body 는 내보내되(AC-8 non-blocking
    # 우선) seq=1 best-effort. false-fresh 아님: durable write 도 실패해 다음 emit 이 seq 재산정하고,
    # 실제 prior seq 가 있었다면 watchdog 이 seq-regress → unknown 으로 흡수(§결정 5). 크로스플랫폼:
    # Windows 는 dir chmod 무시라 이 경로 미도달(로컬 false-GREEN), Linux/CI 에서 발현 → 방어 필수.
    try:
        exists = seq_path.exists()
    except OSError as exc:
        _warn(f"seq 경로 접근 불가 {seq_path}: {exc} — 최초 emit 취급(seq=1), body 내보냄(non-blocking)")
        return 0, True
    if not exists:
        return 0, True
    try:
        raw = seq_path.read_text(encoding="utf-8").strip()
    except Exception as exc:
        _warn(f"seq 파일 판독불능 {seq_path}: {exc} — seq=0 reset 금지(F-6), emit 억제")
        return None, False
    if not re.match(r"^[0-9]+$", raw):
        _warn(f"seq 파일 손상(비정수) {seq_path}: '{raw[:40]}' — seq=0 reset 금지(F-6), emit 억제")
        return None, False
    return int(raw), True


def write_durable_seq(seq_path: Path, seq: int) -> bool:
    """seq durable write (temp+rename atomic, \\n 개행 CRLF-safe). 실패 → False(non-blocking)."""
    try:
        seq_path.parent.mkdir(parents=True, exist_ok=True)
        tmp = seq_path.with_name(f"{seq_path.name}.tmp.{os.getpid()}")
        with open(tmp, "w", encoding="utf-8", newline="\n") as f:
            f.write(f"{seq}\n")
        os.replace(tmp, seq_path)
        return True
    except Exception as exc:
        _warn(f"seq durable write 실패 {seq_path}: {exc}")
        return False


def _resolve_ledger_dir(explicit):
    """ledger-dir 결정: 명시값 우선 → CLAUDE_PROJECT_DIR → git toplevel → cwd, 하위 .claude/ledger/heartbeat/."""
    if explicit:
        return Path(explicit)
    base = os.environ.get("CLAUDE_PROJECT_DIR")
    if not base:
        rc, out, _ = _run(["git", "rev-parse", "--show-toplevel"])
        base = out.strip() if rc == 0 and out.strip() else os.getcwd()
    return Path(base) / _DEFAULT_LEDGER_SUBPATH


def _now_iso() -> str:
    """UTC now ISO8601 (Z suffix, 초 단위) — format SSOT ts 계약과 동일 형식."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def build_body(branch_key: str, seq: int, story: str, lane: str, ts: str, state: str):
    """heartbeat-format.sh(포맷 SSOT) 호출로 본문 생성. 반환 (body:str, ok:bool).
    포맷 실패(bounded 3-tuple/enum 위반 등) → (None, False): seq 미소비(persist 하지 않음)."""
    if not _FORMAT_SCRIPT.exists():
        _warn(f"format SSOT 부재 {_FORMAT_SCRIPT} — emit 억제")
        return None, False
    rc, out, err = _run([_resolve_bash(), str(_FORMAT_SCRIPT), branch_key, str(seq), story, lane, ts, state])
    if rc != 0 or not out.strip():
        _warn(f"heartbeat-format.sh 실패(rc={rc}): {err.strip()[:200]}")
        return None, False
    return out.rstrip("\n"), True


def main() -> int:
    parser = argparse.ArgumentParser(
        prog=SCRIPT_NAME,
        description="CFP-2772 per-branch liveness heartbeat emit (non-blocking, exit 0 always)",
    )
    parser.add_argument("--story", required=True, help="Story KEY (예: CFP-2772)")
    parser.add_argument("--lane", required=True, help="lane 토큰(예: 구현, 설계리뷰)")
    parser.add_argument("--state", default="active",
                        help="state_tag: active|waiting-external[:<reason>]|idle-yield (기본 active)")
    parser.add_argument("--branch", default=None,
                        help="branch slug override — ^[a-z0-9-]+$ 일 때만 수용(git ref name), 아니면 무시+git 파생")
    parser.add_argument("--ledger-dir", default=None,
                        help="seq durable state dir (기본 <repo>/.claude/ledger/heartbeat/)")
    args = parser.parse_args()

    probe = os.environ.get(_PROBE_ENV) == "1"

    # --- branch_key 도출 (도출 불가 → non-blocking exit 0, emit 억제) ---
    branch_key = derive_branch_key(args.branch)
    if not branch_key:
        _warn("branch_key 미확정 — heartbeat emit 억제(non-blocking exit 0)")
        return 0

    # --- durable seq read-back+1 (F-6: 손상 파일 → seq=0 reset 금지, emit 억제) ---
    ledger_dir = _resolve_ledger_dir(args.ledger_dir)
    seq_path = _seq_file(ledger_dir, branch_key)
    last_durable, ok = read_durable_seq(seq_path)
    if not ok:
        # 손상 seq 파일: 신뢰할 seq 를 만들 수 없다 → 파일 무접촉(reset 금지), emit 억제.
        # → watchdog 는 fresh heartbeat 부재/frozen 로 unknown/stalled 판정(fail-safe, never false-fresh).
        _warn("durable seq 판독 실패 — 파일 무접촉(F-6), heartbeat emit 억제(non-blocking exit 0)")
        return 0
    seq = last_durable + 1  # never 0 (부재 시 last_durable=0 → seq=1)

    ts = _now_iso()

    # --- 본문 생성 (포맷 SSOT 호출; 실패 시 seq 미소비) ---
    body, ok = build_body(branch_key, seq, args.story, args.lane, ts, args.state)
    if not ok:
        _warn("본문 생성 실패 — seq 미소비, heartbeat emit 억제(non-blocking exit 0)")
        return 0

    # --- seq durable persist (probe 모드 = side-effect 0, 미persist) ---
    if not probe:
        if not write_durable_seq(seq_path, seq):
            # persist 실패해도 body 는 이미 유효 → 내보내되 다음 emit 이 같은 seq 재사용(중복=idempotent,
            # watchdog 는 seq== 로 취급, false progress 없음). non-blocking 유지.
            _warn("seq persist 실패 — body 는 내보냄(다음 emit seq 재사용 가능, non-blocking)")

    # --- stdout: 코멘트 본문(= relay skill/Orchestrator 가 소비) ---
    sys.stdout.write(body + "\n")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except Exception as exc:  # pragma: no cover — 최종 non-blocking 안전망(exit 0 always)
        sys.stderr.write(f"[{SCRIPT_NAME}] WARN: unexpected — {exc}\n")
        sys.exit(0)
