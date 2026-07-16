#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# CFP-2704 Phase 2 — superpowers-allow status-aware 판정 lib.
# ADR-122 회귀 방지 gate 의 archive/adr 파티션 status-aware 계층:
#   - retired(superseded/deprecated) ADR → EXEMPT (이력 보존, scan 대상 밖)
#   - live/unknown ADR → 13-signature frozen baseline grandfather 차감 후 잔존만 위반
#   bash wrapper(scripts/check-no-superpowers.sh)가 archive/adr grep-hit 라인
#   (path:lineno:content)을 stdin 으로 위임 → 본 모듈은 잔존 위반만 stdout,
#   항상 exit 0 (bash 가 최종 exit 집계).
# 재사용(ADR-140): scripts/lib/check_doc_frontmatter.py 의 fence-parse(text.split("\n---\n",1)[0][4:])
#   / _cat_sanitize_echo / stdout reconfigure(L15-19) / yaml ImportError fail-open 패턴 미러.
import sys
from pathlib import Path

# Windows cp949 stdout encoding 차단 (check_doc_frontmatter.py L15-19 미러)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

try:
    import yaml
except ImportError:
    yaml = None  # fail-open (parse_status → None)

# ─────────────────────────────────────────────────────────────────────────────
# FROZEN_SUPERPOWERS_BASELINE — live/unknown ADR 대상 13-signature grandfather.
#   base 702593e9 worktree 실측 census 와 byte-exact (drift 금지). 순수 module-level
#   set 리터럴 (ast.literal_eval-able; frozenset(...) call-wrap 금지, 동적 생성 금지 —
#   self-test 가 source ast-extract 로 13-set 검증).
# ─────────────────────────────────────────────────────────────────────────────
FROZEN_SUPERPOWERS_BASELINE = {
    ("archive/adr/ADR-017-skill-override-path-enforcement.md", "superpowers:brainstorming"),
    ("archive/adr/ADR-017-skill-override-path-enforcement.md", "superpowers:writing-plans"),
    ("archive/adr/ADR-027-consumer-adoption-protocol.md", "superpowers:brainstorming"),
    ("archive/adr/ADR-035-codeforge-agent-teams-epic-architecture.md", "superpowers:using-git-worktrees"),
    ("archive/adr/ADR-044-phase-scoped-sequential-team.md", "superpowers:using-git-worktrees"),
    ("archive/adr/ADR-064-decision-principle-mandate.md", "superpowers:brainstorming"),
    ("archive/adr/ADR-064-decision-principle-mandate.md", "superpowers:writing-plans"),
    ("archive/adr/ADR-073-orchestrator-verify-before-assert.md", "superpowers:subagent-driven-development"),
    ("archive/adr/ADR-073-orchestrator-verify-before-assert.md", "superpowers:writing-plans"),
    ("archive/adr/ADR-082-write-time-self-write-verification-mandate.md", "superpowers:subagent-driven-development"),
    ("archive/adr/ADR-085-multi-session-collaboration-protocol.md", "superpowers:writing-plans"),
    ("archive/adr/ADR-122-superpowers-dependency-removal.md", "superpowers:brainstorming"),
    ("archive/adr/ADR-122-superpowers-dependency-removal.md", "superpowers:writing-plans"),
}

RETIRED_STATUSES = {"superseded", "deprecated"}
LIVE_STATUSES = {"accepted", "proposed", "active", "adopted"}


def parse_status(md_path):
    # frontmatter-fence scoped status 추출. CRLF tolerant. 부재/미설치/parse실패/비-str → None.
    text = Path(md_path).read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")
    if not text.startswith("---\n"):
        return None
    if yaml is None:
        return None  # pyyaml 미설치 fail-open
    try:
        fm = yaml.safe_load(text.split("\n---\n", 1)[0][4:])
    except Exception:
        return None
    if not isinstance(fm, dict):
        return None
    raw = fm.get("status")
    if not isinstance(raw, str):
        return None
    # inline 주석 절삭 + strip + casefold (body 중복 status 는 fence scoping 으로 자동 배제)
    folded = raw.split("#", 1)[0].strip().casefold()
    return folded or None


def classify_status(folded):
    # None/미지 문자열 → unknown, retired 계열 → retired, live 계열 → live.
    if folded is None:
        return "unknown"
    if folded in RETIRED_STATUSES or folded.startswith("superseded by"):
        return "retired"
    if folded in LIVE_STATUSES:
        return "live"
    return "unknown"


def decide(file_posix, token, folded_status):
    # 판정순서 = classify → (retired: exempt) / (live·unknown: baseline-filter).
    cls = classify_status(folded_status)
    if cls == "retired":
        return ("exempt_retired", f"retired ADR (status={folded_status}) — 이력 보존 EXEMPT")
    # live·unknown 공통 baseline-filter (scan→baseline 후행, born-red 방지):
    #   unknown+baseline-hit 도 여기서 exempt_grandfather.
    if (file_posix, token) in FROZEN_SUPERPOWERS_BASELINE:
        return ("exempt_grandfather", "13-signature frozen baseline grandfather")
    if cls == "unknown":
        return ("scan_unknown_violation", "status-unknown baseline-miss — fail-closed scan")
    return ("violation", "live ADR baseline-miss — 라이브 superpowers 재유입")


def sanitize_echo(value):
    # author-controlled 값 GHA annotation-injection 방어 (_cat_sanitize_echo 미러, ≤80):
    # CR/LF→공백(단일 라인), leading ':' neutralize, ≤80 truncate.
    s = str(value).replace("\r", " ").replace("\n", " ").lstrip(":")
    return s[:80]


if __name__ == "__main__":
    import re

    pat = re.compile(r"superpowers:[a-z][a-z0-9-]+")
    status_cache = {}
    violations = []
    for line in sys.stdin:
        parts = line.rstrip("\n").split(":", 2)
        if len(parts) < 3:
            continue
        file_raw, lineno, content = parts
        file_posix = file_raw[2:] if file_raw.startswith("./") else file_raw
        if not file_posix.startswith("archive/adr/"):
            continue
        if file_posix not in status_cache:
            status_cache[file_posix] = parse_status(Path(file_posix))
        folded = status_cache[file_posix]
        for token in pat.findall(content):
            verdict, reason = decide(file_posix, token, folded)
            if verdict in ("violation", "scan_unknown_violation"):
                out = f"{sanitize_echo(file_posix)}:{lineno}: {sanitize_echo(token)} [{verdict}]" + (
                    " [status-unknown fail-closed scan]" if verdict == "scan_unknown_violation" else ""
                )
                violations.append(out)
    for v in violations:
        print(v)
    sys.exit(0)
