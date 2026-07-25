#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# CFP-2829 S2 (leg A) — structure-gate-bridge (AC-2 / AC-6, §3.6 / §7.R R-3).
"""backward substrate 산출 markdown 을 기존 구조게이트로 PR 오픈 전 사전검증하는 bridge.

interface-freeze (§3.6 / R-3):
  대상 게이트 = scripts/lib/check_doc_frontmatter.py + scripts/lib/check_doc_section_schema.py.
  두 파일 = top-level 실행 스크립트(path.rglob 순회 → exit 1 on warning)라 clean import 불가 →
  **subprocess 호출**(import 아님). 게이트 스크립트 라인 변경 0 (8-tuple 게이트 코드 무손상).

방법:
  candidate 를 canonical 상대경로(rel_path)로 temp staging-tree 에 write → 그 dir 을 cwd 로
  두 게이트 subprocess 실행. 게이트는 자신의 REQUIRED prefix 하위만 rglob 하므로 —
  게이트-有 doc_type 은 검사되고 게이트-無 doc_type 은 자연 pass-through(uniform semantics).

fail-closed (AC-6, option (b)):
  어느 게이트라도 non-zero → False(차단). 게이트 실행 자체 실패(exception)도 False(fail-closed).
  **fail-open escape hatch 부재** — 우회 경로 0.

INV-T2 (§3.6 / R-2):
  candidate 는 hash/gate 전 반드시 _normalize_markdown 통과(자체 normalization bypass 금지).
  _normalize_markdown 은 confluence_property_chunking(→ 3anchor.py importlib) 재사용.

doc_type coverage 비대칭 정직 declare (R-3 — uniform 구조검증 주장 금지):
  게이트-有  = adr / change-plans / domain-knowledge (REQUIRED frontmatter + REQUIRED_SECTIONS).
  게이트-無  = architecture(Living Arch) / orchestrator-playbook / consumer-guide /
              confluence-mirror-playbook  → structure-gate-bridge pass-through(구조 무검증).
  ★ architecture_doc·orchestrator_playbook = 구조게이트+CODEOWNERS 이중 무방비(§2 AS-IS) →
    미분류/무게이트 doc_type sync 공백 boundary 확정 = S3/S4 게이트 lane 이월.
"""
import os
import subprocess
import sys
import tempfile
from pathlib import Path

# Windows cp949 stdout 차단 (forward_sync L60-64 패턴).
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# ── _normalize_markdown 재사용 (INV-T2 — chunking 모듈 경유, 3anchor.py 0줄 변경) ──
_LIB_DIR = Path(__file__).resolve().parent / "lib"
if str(_LIB_DIR) not in sys.path:
    sys.path.insert(0, str(_LIB_DIR))
from confluence_property_chunking import _normalize_markdown  # noqa: E402

# ── 대상 게이트 스크립트 경로 (interface-freeze — subprocess 호출) ──
_GATE_SCRIPTS = (
    _LIB_DIR / "check_doc_frontmatter.py",
    _LIB_DIR / "check_doc_section_schema.py",
)

# 게이트-有 doc_type prefix (정직 declare — 판정 authority 는 게이트 스크립트 자체, 본 집합은 문서용).
GATED_DOC_TYPES = ("adr", "change_plan", "domain_knowledge")
UNGATED_MIRROR_DOC_TYPES = (
    "architecture_doc",
    "orchestrator_playbook",
    "consumer_guide",
    "confluence_mirror_playbook",
)


def _run_gate(script: Path, staging_dir: Path) -> bool:
    """게이트 스크립트를 staging_dir cwd 로 subprocess 실행. exit 0 → True(pass).

    실행 자체 실패(python 부재 등)/exception → False(fail-closed, AC-6 안전측).
    """
    env = dict(os.environ)
    env["PYTHONUTF8"] = "1"          # Windows cp949 harness crash 방지 (firsthand 교훈).
    env["PYTHONIOENCODING"] = "utf-8"
    try:
        result = subprocess.run(
            [sys.executable, str(script)],
            cwd=str(staging_dir),
            capture_output=True,
            env=env,
            check=False,
        )
    except (OSError, ValueError):
        return False
    return result.returncode == 0


def verify_substrate(candidate_bytes: bytes, doc_type: str, rel_path: str) -> bool:
    """backward substrate candidate 를 구조게이트로 사전검증 (True=통과 / False=차단).

    candidate_bytes → _normalize_markdown(INV-T2) → staging-tree(rel_path) write →
    두 게이트 subprocess. 어느 게이트라도 fail → False(fail-closed, AC-6 escape hatch 0).

    doc_type = doc-locations doc_type 명(게이트-無 doc_type 은 자연 pass-through, R-3 정직 declare).
    rel_path = repo-relative canonical 경로(예: 'docs/change-plans/foo.md') — 게이트 prefix 판정 기준.
    """
    if not isinstance(candidate_bytes, (bytes, bytearray)):
        raise TypeError("candidate_bytes must be bytes")
    rel = rel_path.replace("\\", "/").lstrip("/")
    if not rel:
        return False

    normalized = _normalize_markdown(bytes(candidate_bytes))

    with tempfile.TemporaryDirectory(prefix="cfp2829-gate-") as td:
        staging = Path(td)
        target = staging / rel
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(normalized)
        except OSError:
            return False

        for script in _GATE_SCRIPTS:
            if not script.exists():
                # 게이트 스크립트 부재 = 방어 불가 → fail-closed (AC-6 안전측).
                return False
            if not _run_gate(script, staging):
                return False
    return True


def main(argv=None) -> int:
    """CLI: candidate 파일을 구조게이트로 검증. exit 0=통과 / 1=차단."""
    import argparse
    p = argparse.ArgumentParser(
        prog="confluence_backward_gate.py",
        description="backward substrate structure-gate-bridge (CFP-2829 S2 AC-2/AC-6).",
    )
    p.add_argument("--candidate", required=True, help="검증 대상 markdown 파일 경로.")
    p.add_argument("--rel-path", required=True, help="repo-relative canonical 경로(게이트 prefix 판정).")
    p.add_argument("--doc-type", default="", help="doc-locations doc_type 명(게이트-無=pass-through).")
    args = p.parse_args(argv)

    data = Path(args.candidate).read_bytes()
    ok = verify_substrate(data, args.doc_type, args.rel_path)
    print(f"structure-gate-bridge: {'PASS' if ok else 'BLOCKED'} (rel_path={args.rel_path}, doc_type={args.doc_type or 'N/A'})")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
