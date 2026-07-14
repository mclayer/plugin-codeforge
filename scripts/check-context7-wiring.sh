#!/usr/bin/env bash
# check-context7-wiring.sh — CFP-2672 / ADR-124 Amendment 2 presence-lint.
#
# Execution-backed AC verification for context7 능동 배선 (fail-open, 권장 tier 유지).
# presence + negative-presence + keep-invariant. Exit 1 on any FAIL. positive checks +
# fail-closed keep-invariant; negative-presence checks are presence-scoped and guarded
# by target-existence assertions (대상 부재 = FAIL, not spurious 0-hit PASS).
#
# NOTE: This is a standalone verification script, NOT a required CI gate — wiring it
# into .github/workflows/ would itself violate AC-3 (context7 must be CI-invisible).
set -uo pipefail
ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"

fail=0
pass() { printf 'PASS  %s\n' "$1"; }
bad()  { printf 'FAIL  %s\n' "$1"; fail=1; }

# count matching FILES (grep -l); args: pattern glob...
files_with() { grep -lE "$1" "${@:2}" 2>/dev/null | wc -l | tr -d ' '; }
# count matching LINES; args: pattern paths...
lines_with() { grep -rInE "$1" "${@:2}" 2>/dev/null | wc -l | tr -d ' '; }

echo "== CFP-2672 context7 wiring lint (ADR-124 Amendment 2) =="

# ---------- AC-1: 능동 배선 문구 존재 (design authoring 11 / req-review / design-checklist / develop authoring 4) ----------
n_design=$(files_with 'context7 MCP' plugins/codeforge-design/agents/*.md)
[ "$n_design" = "11" ] && pass "AC-1 design authoring agents wired (11/11)" \
  || bad "AC-1 design authoring agents wired: got $n_design, want 11"

n_reqrev=$(lines_with 'context7' plugins/codeforge-review/agents/RequirementsReviewPLAgent.md)
[ "$n_reqrev" -ge 1 ] && pass "AC-1 RequirementsReviewPLAgent wired (hits=$n_reqrev)" \
  || bad "AC-1 RequirementsReviewPLAgent not wired"

n_dcheck=$(lines_with 'context7' plugins/codeforge-review/templates/review-checklists/design.md)
[ "$n_dcheck" -ge 1 ] && pass "AC-1 design-review checklist wired (hits=$n_dcheck)" \
  || bad "AC-1 design-review checklist not wired"

n_dev=$(files_with 'context7 MCP' plugins/codeforge-develop/agents/*.md)
[ "$n_dev" = "4" ] && pass "AC-1 develop authoring agents wired (4/4, DeveloperPLAgent excluded)" \
  || bad "AC-1 develop authoring agents wired: got $n_dev, want 4"

# ---------- AC-5: firsthand 검증 상속 (context7 co-located with firsthand/외부 워커/출처) ----------
miss5=0
for f in plugins/codeforge-design/agents/ArchitectAgent.md \
         plugins/codeforge-develop/agents/DeveloperAgent.md \
         plugins/codeforge-review/agents/RequirementsReviewPLAgent.md; do
  h=$(grep -cE 'context7.*(firsthand|외부 워커|출처)' "$f")
  [ "$h" -ge 1 ] || { miss5=1; echo "   (AC-5 missing firsthand co-location in $f)"; }
done
[ "$miss5" = "0" ] && pass "AC-5 firsthand 검증 상속 문구 co-located" \
  || bad "AC-5 firsthand 검증 상속 문구 누락"

# ---------- AC-6: code-review 대칭 (negative + keep-invariant) ----------
# (i) code-review workers must have NO context7 active wiring
#     target-existence guard first (fail-closed, AC-6ii 패턴 미러): 파일 부재 = FAIL
for f in plugins/codeforge-review/agents/ClaudeReviewAgent.md plugins/codeforge-review/agents/CodexReviewAgent.md; do
  [ -f "$f" ] || bad "AC-6 target missing (fail-closed): $f"
done
n_cr=$(lines_with 'context7' plugins/codeforge-review/agents/ClaudeReviewAgent.md plugins/codeforge-review/agents/CodexReviewAgent.md)
[ "$n_cr" = "0" ] && pass "AC-6 code-review workers NOT wired (context7 hits=0)" \
  || bad "AC-6 code-review workers unexpectedly mention context7 (hits=$n_cr)"
# (ii) keep-invariant: lane=code 전면 금지 line intact (장식-tolerant regex, §8.2(ii))
n_keep=$(grep -cE 'lane=code.*전면 금지' plugins/codeforge-review/CLAUDE.md)
[ "$n_keep" = "1" ] && pass "AC-6 keep-invariant 'lane=code 전면 금지' intact (line count=1)" \
  || bad "AC-6 keep-invariant broken: 'lane=code.*전면 금지' count=$n_keep, want 1"

# ---------- AC-4: 필수 의존성 미추가 (root CLAUDE.md must not mention context7) ----------
n_dep=$(grep -cE 'context7' CLAUDE.md)
[ "$n_dep" = "0" ] && pass "AC-4 root CLAUDE.md 필수 의존성 context7 미추가 (hits=0)" \
  || bad "AC-4 root CLAUDE.md unexpectedly mentions context7 (hits=$n_dep)"

# ---------- AC-3: CI-invisible (no context7 check in any workflow) ----------
# target-existence guard first (fail-closed): 디렉터리 부재 = FAIL, not spurious 0-hit PASS
[ -d .github/workflows ] || bad "AC-3 scan target missing (fail-closed): .github/workflows/"
n_wf=$(lines_with 'context7' .github/workflows)
[ "$n_wf" = "0" ] && pass "AC-3 .github/workflows/ context7 부재 (CI-invisible, hits=0)" \
  || bad "AC-3 .github/workflows/ unexpectedly references context7 (hits=$n_wf)"

# ---------- AC-7: rename-tolerant (no hardcoded old tool name) ----------
# target-existence guard first (fail-closed): 스캔 대상 경로 부재 = FAIL, not spurious 0-hit PASS
for d in plugins docs archive; do
  [ -d "$d" ] || bad "AC-7 scan target missing (fail-closed): $d/"
done
n_old=$(lines_with 'get-library-docs' plugins docs archive)
[ "$n_old" = "0" ] && pass "AC-7 rename-tolerant: 구명 'get-library-docs' 하드코딩 부재 (hits=0)" \
  || bad "AC-7 old tool name 'get-library-docs' hardcoded (hits=$n_old)"

# ---------- AC-8: ADR-124 Amendment 2 기록 + docs cross-ref ----------
n_adr=$(grep -cE '^## Amendment 2 ' archive/adr/ADR-124-external-knowledge-provisioning-model.md)
[ "$n_adr" -ge 1 ] && pass "AC-8 ADR-124 'Amendment 2' section present" \
  || bad "AC-8 ADR-124 Amendment 2 section missing"
for d in docs/orchestrator-playbook.md docs/consumer-guide.md; do
  h=$(grep -cE 'context7.*(fail-open|필수)|(fail-open|필수).*context7' "$d")
  [ "$h" -ge 1 ] && pass "AC-8 cross-ref present in $d (hits=$h)" \
    || bad "AC-8 cross-ref (context7 + fail-open/필수) missing in $d"
done

echo "== $( [ "$fail" = "0" ] && echo 'ALL GREEN' || echo 'FAILURES DETECTED' ) =="
exit "$fail"
