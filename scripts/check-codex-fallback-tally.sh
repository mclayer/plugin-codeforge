#!/usr/bin/env bash
# check-codex-fallback-tally.sh
# CFP-1368 / ADR-052 Amendment 14 — codex-fallback-subclass-tally mechanical wire
# ADR-060 Amendment 14 §결정 28 — dual-binding enforcement source (ADR-052/070/081 declaration + ADR-060 enforcement)
#
# Thin bash wrapper — ADR-061 §결정 1 정합 (Python entry-point + thin wrapper 분리).
# CFP-583 BODY heredoc anti-pattern 차단 (script body = exec python3 단일 호출).
#
# Tallies [codex-sandbox-fallback: <fail-mode>] and [codex-substitution-scope-declared: <scope-enum>]
# markers from Story §10 and checks per-enum count against threshold.
# warning tier (continue-on-error) — exit 1 does NOT block PR merge.
#
# Usage:
#   bash scripts/check-codex-fallback-tally.sh \
#     --jsonl-file docs/kpi/codex-fallback-tally.jsonl \
#     --story-file docs/stories/CFP-NNN.md \
#     [--carrier-story CFP-NNN] \
#     [--dry-run]
#
# Exit codes (ADR-060 §결정 15 3-tier): 0=PASS | 1=WARNING | 2=META-ERROR
#
# SecurityArch TH-2: set +x guard — no PAT/secret echoed to stdout/stderr.
set +x  # SecurityArch TH-2: no debug trace (PAT guard)
set -euo pipefail
exec python3 "$(dirname "$0")/lib/check_codex_fallback_tally.py" "$@"
