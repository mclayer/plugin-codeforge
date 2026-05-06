#!/usr/bin/env bash
# scripts/next-phase.sh — phase label transition logic
# Args: $1 = current phase label (e.g., "phase:설계-리뷰")
#       $2 = phase string (Phase1 | Phase2)
# Output: next phase label (stdout)
# Exit code: 0 on success, 1 on unknown input

set -euo pipefail

CURRENT_PHASE="${1:-}"
PR_PHASE="${2:-}"

if [[ -z "$CURRENT_PHASE" || -z "$PR_PHASE" ]]; then
    echo "Usage: $0 <current_phase_label> <Phase1|Phase2>" >&2
    exit 1
fi

case "$CURRENT_PHASE" in
    "phase:요구사항")
        echo "phase:설계"
        ;;
    "phase:설계")
        echo "phase:설계-리뷰"
        ;;
    "phase:설계-리뷰")
        # Phase 1 PR merge: 설계-리뷰 → 구현
        echo "phase:구현"
        ;;
    "phase:구현")
        echo "phase:구현-리뷰"
        ;;
    "phase:구현-리뷰")
        echo "phase:구현-테스트"
        ;;
    "phase:구현-테스트")
        echo "phase:보안-테스트"
        ;;
    "phase:보안-테스트")
        if [[ "$PR_PHASE" == "Phase2" ]]; then
            echo "phase:완료"
        else
            echo "phase:보안-테스트"
        fi
        ;;
    "phase:완료")
        echo "phase:완료"
        ;;
    *)
        echo "Unknown phase: $CURRENT_PHASE" >&2
        exit 1
        ;;
esac
