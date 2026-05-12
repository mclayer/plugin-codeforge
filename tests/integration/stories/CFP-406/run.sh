#!/usr/bin/env bash
# run.sh — CFP-406 lane-evidence-check regex EOF anchor fix integration harness
#
# Story:        codeforge-internal-docs:wrapper/stories/CFP-406.md
# Change Plan:  codeforge-internal-docs:wrapper/change-plans/cfp-406-lane-evidence-regex.md §8.6
# Phase 1 PR:   mclayer/plugin-codeforge#416 (merged 5ce7944)
#
# 목적: Phase 1 의 regex fix 가 3 fixture 시나리오에 대해 의도된 동작을 하는지 검증.
#   OLD regex: /^## Lane evidence\s*$([\s\S]*?)(?=^## |\z)/m       (\z literal-z fallback bug)
#   NEW regex: /^## Lane evidence\s*$([\s\S]*?)(?=^## |$(?![\s\S]))/m
#
# 동작:
#   1) Node.js 20 runtime 으로 fixture 3종 × {OLD, NEW} regex 6 case 실행
#   2) `## Lane evidence` block 추출 + 7-row row count 산정
#   3) workflow JS line 113-155 의 expected outcome (PASS / action_required) 매핑 후 assert
#   4) expected vs actual 비교 → exit code 0 (PASS) / 1 (FAIL)
#
# Expected matrix (Story §8.6 + Change Plan §8.6 정합):
#   Fixture 1 (EOF 종결, footer 없음): OLD=action_required (버그 재현)  | NEW=success (PASS)
#   Fixture 2 (`## Notes` footer):     OLD=success      | NEW=success    (회귀 방지)
#   Fixture 3 (3-row + `## Notes`):    OLD=action_required (row 검증 실패) | NEW=action_required (동일)
#
# Usage:
#   bash tests/integration/stories/CFP-406/run.sh           # default verbose
#   bash tests/integration/stories/CFP-406/run.sh --quiet   # summary only
#
# Exit code:
#   0 = 모든 fixture×regex case expected outcome 일치 (PASS)
#   1 = 1건 이상 mismatch (FAIL)
#   2 = pre-flight 실패 (Node.js 부재 / fixture 파일 부재 등)

set -uo pipefail

QUIET=0
if [ "${1:-}" = "--quiet" ]; then QUIET=1; fi

log()     { [ $QUIET -eq 0 ] && printf '%s\n' "$1"; return 0; }
log_err() { printf '%s\n' "$1" >&2; }

# Pre-flight: Node.js 20+ 확인
if ! command -v node >/dev/null 2>&1; then
    log_err "[ABORT] node 미설치 — Node.js 20 (GitHub Actions runtime 등가) 필요"
    exit 2
fi
NODE_MAJOR="$(node -e 'process.stdout.write(String(process.versions.node.split(".")[0]))' 2>/dev/null || echo 0)"
if [ "$NODE_MAJOR" -lt 20 ]; then
    log_err "[ABORT] Node.js >= 20 필요 (현재 v${NODE_MAJOR}). GitHub Actions actions/github-script@v7 = Node.js 20"
    exit 2
fi
log "[PRE] Node.js v$(node -v) — OK"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Fixture 파일 존재 확인
for f in fixture-1-block-ends-eof.md fixture-2-block-with-footer.md fixture-3-missing-rows.md; do
    if [ ! -f "$SCRIPT_DIR/$f" ]; then
        log_err "[ABORT] fixture 파일 부재: $SCRIPT_DIR/$f"
        exit 2
    fi
done
log "[PRE] fixture 3종 존재 확인"

# Expected matrix:
#   <fixture>:<regex>=<expected_outcome>
#   outcome ∈ {success, action_required}
#
# Source of truth: Story §8.6 (Iter 2 RESOLVED) + Change Plan §8.6 Fixture 표.
declare -A EXPECTED=(
    ["1:OLD"]="action_required"   # block 추출 실패 (\z literal-z fallback)
    ["1:NEW"]="success"            # 7-row 매칭 PASS
    ["2:OLD"]="success"            # footer 로 lookahead 발동 → 7-row PASS
    ["2:NEW"]="success"            # 동일 PASS (회귀 방지)
    ["3:OLD"]="action_required"   # block 추출 성공 → row 검증 실패 (3 rows < 7)
    ["3:NEW"]="action_required"   # 동일 (fix scope 외)
)

# Node.js helper inline — fixture body 를 stdin 으로 받고 regex 종류 + 결과 JSON 출력
run_case() {
    local fixture_path="$1"
    local regex_kind="$2"  # OLD | NEW

    REGEX_KIND="$regex_kind" node --input-type=module -e '
        import { readFileSync } from "node:fs";
        const kind = process.env.REGEX_KIND;
        const body = readFileSync(0, "utf8");

        // OLD regex — Phase 1 fix 전 (V8 에서 \z = literal-z fallback)
        // NEW regex — Phase 1 fix 후 (PR #416, ECMAScript 정합 EOF anchor)
        const OLD = /^## Lane evidence\s*$([\s\S]*?)(?=^## |\z)/m;
        const NEW = /^## Lane evidence\s*$([\s\S]*?)(?=^## |$(?![\s\S]))/m;
        const re = kind === "OLD" ? OLD : NEW;

        const m = body.match(re);
        if (!m) {
            // workflow line 114-128 정합 — block 추출 실패 → action_required
            console.log(JSON.stringify({ matched: false, rows: 0, outcome: "action_required", reason: "block 추출 실패" }));
            process.exit(0);
        }

        // workflow line 130-155 정합 — 7-row valid format 검증
        const blockBody = m[1];
        const requiredLanes = ["요구사항", "설계", "설계-리뷰", "구현", "구현-리뷰", "구현-테스트", "보안-테스트"];
        const rowRegex = /^-\s*([^:]+):\s*(PASS|SKIPPED|FIX|ESCALATED|BYPASS)/gm;
        const foundLanes = new Set();
        let r;
        while ((r = rowRegex.exec(blockBody)) !== null) {
            foundLanes.add(r[1].trim());
        }
        const missing = requiredLanes.filter(l => !foundLanes.has(l));
        const outcome = missing.length > 0 ? "action_required" : "success";
        const reason = missing.length > 0
            ? "row 검증 실패 (" + missing.length + "/7 missing: " + missing.join(",") + ")"
            : "7-row 매칭 PASS";
        console.log(JSON.stringify({ matched: true, rows: foundLanes.size, outcome, reason }));
    ' < "$fixture_path"
}

# Run cases
declare -i fail_count=0
declare -i pass_count=0

run_one() {
    local idx="$1"
    local fixture_file="$2"
    local kind="$3"
    local key="${idx}:${kind}"
    local exp="${EXPECTED[$key]}"

    local result
    result="$(run_case "$SCRIPT_DIR/$fixture_file" "$kind")"

    local actual reason
    actual="$(printf '%s' "$result" | node -e '
        let d = "";
        process.stdin.on("data", c => d += c);
        process.stdin.on("end", () => { try { console.log(JSON.parse(d).outcome); } catch (e) { console.log("parse-error"); } });
    ')"
    reason="$(printf '%s' "$result" | node -e '
        let d = "";
        process.stdin.on("data", c => d += c);
        process.stdin.on("end", () => { try { console.log(JSON.parse(d).reason); } catch (e) { console.log(""); } });
    ')"

    if [ "$actual" = "$exp" ]; then
        pass_count=$((pass_count + 1))
        log "  [PASS] fixture $idx × $kind → outcome=$actual ($reason)"
    else
        fail_count=$((fail_count + 1))
        log_err "  [FAIL] fixture $idx × $kind → expected=$exp actual=$actual ($reason)"
    fi
}

log ""
log "=== CFP-406 lane-evidence regex EOF anchor fix — fixture 3 × regex 2 = 6 case ==="

log ""
log "[Fixture 1] block 종결 EOF — footer 없음 (본 fix 핵심 invariant)"
run_one 1 fixture-1-block-ends-eof.md OLD
run_one 1 fixture-1-block-ends-eof.md NEW

log ""
log "[Fixture 2] block 종결 다음 \`## Notes\` section — 회귀 방지"
run_one 2 fixture-2-block-with-footer.md OLD
run_one 2 fixture-2-block-with-footer.md NEW

log ""
log "[Fixture 3] 7-row 일부 누락 + \`## Notes\` trailing — 본 fix scope 외"
run_one 3 fixture-3-missing-rows.md OLD
run_one 3 fixture-3-missing-rows.md NEW

log ""
log "=== Summary: ${pass_count} PASS / ${fail_count} FAIL (총 6 case) ==="

if [ $fail_count -gt 0 ]; then
    log_err ""
    log_err "Story §8.6 expected outcome 매트릭스와 불일치 — Change Plan §8.6 + Iter 2 RESOLVED 검증 SSOT 참조"
    exit 1
fi

exit 0
