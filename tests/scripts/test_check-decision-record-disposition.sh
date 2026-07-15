#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# tests/scripts/test_check-decision-record-disposition.sh
# CFP-2697 / Epic #2696 (canary artifact D6) — decision-record disposition oracle +
#   reference-integrity guard 의 TDD self-test (Change Plan §8.1 Test Contract 이행).
#
# 목적(mutation-kill = born-hollow 회피): 두 pure 모듈이 "축-완전(axis-complete)"임을 실증한다.
#   oracle = scripts/lib/decision_record_disposition.py  (classify + 3 ablatable axis fn)
#   guard  = scripts/lib/reference_integrity_guard.py    (run_guard 4-check conjunction)
#   두 모듈은 read-only reference — 본 self-test 는 어느 production 코드도 수정하지 않는다.
#
# born-alive: 실제 python 프로세스로 두 모듈을 import·구동하고 실 assertion 을 돌린다.
#   각 case = 독립 python 프로세스(fresh interpreter) → monkeypatch(ablation) 오염 0 (flip 이 진짜).
#   exit 0 = 전 case pass / exit 1 = 1건이라도 fail. 어떤 assertion 줄도 `|| true` 로 mask 하지 않는다.
#
# anti-overfit(비협상): fixture 는 대표 literal 문자열(장르 exercise)이지 fixture-신원(file==X) 아님.
#   oracle 은 라인 FEATURE(referent·tense·cardinal 축)로만 판정 — 본 self-test 도 신원 하드코딩 0.
#
# ── Change Plan §8.1 매핑 ─────────────────────────────────────────────────────
#  Part A  5-fixture replay (exact-match 5/5 mandatory): P-1/2/3→correct, N-1 homonym→no_action,
#          N-2 dated→no_action. 어느 mismatch = D6_RED(canary death) = 즉시 FAIL.
#  Part B  mutation-kill (3 axes = 3 killing mutants, mandatory floor): 축을 하나씩 ablate 하면
#          verdict 가 wrong 값으로 flip 함을 assert (positive-control — 축 load-bearing 실증).
#          M1 referent-blind / M2 tense-blind / M3 cardinal-blind.
#  Part C  M4 anti-overfit(perturbation stable) + M5 structural-guard conjunction gates.
#
# 정직 천장(ADR-119): 본 self-test 는 축 load-bearing(mutation-kill) + 계약 verdict 일치까지 실증한다.
#   "oracle 이 모든 실세계 decision-record 를 완전 분류한다"는 hard-claim 은 하지 않는다(검출력 봉인 주장 X).
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail
export LC_ALL=C.UTF-8
export LANG=C.UTF-8
export PYTHONIOENCODING=utf-8

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
LIB="${REPO_ROOT}/scripts/lib"
ORACLE="${LIB}/decision_record_disposition.py"
GUARD="${LIB}/reference_integrity_guard.py"

PY="${PYTHON:-python}"
command -v "$PY" >/dev/null 2>&1 || PY="python3"
if ! command -v "$PY" >/dev/null 2>&1; then
  echo "✗ FAIL: python/python3 부재 — oracle self-test 실행 불가"
  exit 1
fi

# ── module-existence guard (read-only reference; 부재 = sibling-dependency 노출, silent skip 금지) ──
[ -f "$ORACLE" ] || { echo "✗ FAIL: oracle 모듈 부재: $ORACLE (DeveloperAgent 미구현 — PL 재실행 필요)"; exit 1; }
[ -f "$GUARD" ]  || { echo "✗ FAIL: guard 모듈 부재: $GUARD (DeveloperAgent 미구현 — PL 재실행 필요)"; exit 1; }

# ── 공유 fixture 모듈 (대표 literal 문자열 — 단일 정의, 그룹 간 drift 0) ──────────
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
cat > "${WORK}/cfp2697_fixtures.py" <<'PYFIX'
# -*- coding: utf-8 -*-
# 대표 literal(장르 exercise). fixture-신원 하드코딩 0 — oracle 은 라인 FEATURE 로만 판정.
FIX = {
    # P-* (positive → correct): referent=bp-context-count ∧ present-normative ∧ cardinal embed.
    "P-1": "현재 required_status_checks contexts 목록은 6-tuple 이며 이 값은 불변이다",
    "P-2": "branch protection 의 6-tuple 불변 원칙 자체는 폐기 대상이 아니다",          # phantom principle wrapper
    "P-3": "branch protection 6-tuple contexts 무변경 유지",                             # scope-fusion
    # N-* (KILLER negatives → no_action). ★ cardinal_bound=True 로 구성 —
    #   그래야 referent/tense 축 ablation 이 verdict 를 flip(축 load-bearing 실증 가능).
    "N-1": "branch protection 로그의 latency metric 3-tuple 은 불변 baseline",           # homonym (metric tuple)
    "N-2": "2026-07-12 당시 required contexts 6-tuple 불변 확정 (live=6-tuple, HELD)",    # dated history
    # D-1 (FIX F2 loosen-discriminator): 서술형 bp(도메인토큰+cardinal, 진성 규범 토큰 부재) → no_action.
    #   cardinal_bound 축 하나가 correct 밖으로 막는다 → axis_cardinal_bound→True(loosen)면 correct 로 flip.
    #   (F3 regression 겸: "required" 단독으로 normative-side 충족 못 함을 실증.)
    "D-1": "phase-gate-mergeable 의 required contexts 는 현재 7-tuple 로 구성된다",
}
EXP = {"P-1": "correct", "P-2": "correct", "P-3": "correct", "N-1": "no_action", "N-2": "no_action", "D-1": "no_action"}

# M4 perturbation: 부수 토큰만 교체(장르 feature 보존) → verdict 불변 = 일반화(암기 아님).
PERT = {
    "P-1~": ("참고로 wrapper 의 required_status_checks contexts 세트는 7-tuple 이고 그 값은 불변 원칙이다", "correct"),
    "N-1~": ("시스템 branch protection 대시보드의 p95 latency metric 5-tuple 는 불변 기준선", "no_action"),
    "N-2~": ("2025-11-03 시점 required contexts 6-tuple 불변 서술 (live=6-tuple, 잔존)", "no_action"),
}
PYFIX

PASS=0
FAIL=0

# run_py <name>  (heredoc = python 본문; argv = LIB WORK). exit 0 → PASS / else → FAIL.
run_py() {
  local name="$1"
  echo "── ${name} ──"
  if "$PY" - "$LIB" "$WORK"; then
    PASS=$((PASS + 1)); echo "  [${name}] RESULT: PASS"
  else
    FAIL=$((FAIL + 1)); echo "  [${name}] RESULT: FAIL"
  fi
}

# ═════════════════════════════════════════════════════════════════════════════
# born-alive sanity — 두 모듈 import + axis fn / run_guard callable + enum presence
# ═════════════════════════════════════════════════════════════════════════════
run_py "born-alive" <<'PY'
import sys
LIB, WORK = sys.argv[1], sys.argv[2]
sys.path.insert(0, WORK); sys.path.insert(0, LIB)
import decision_record_disposition as m
import reference_integrity_guard as g
ok = True
for fn in ("classify", "axis_referent", "axis_tense", "axis_cardinal_bound", "axis_phantom_enforcement"):
    if not callable(getattr(m, fn, None)):
        print("  born-alive: oracle.%s 미존재/uncallable" % fn); ok = False
if not callable(getattr(g, "run_guard", None)):
    print("  born-alive: guard.run_guard uncallable"); ok = False
for c in ("REFERENT_BP_CONTEXT_COUNT", "REFERENT_OTHER", "REFERENT_ABSENT"):
    if not hasattr(m, c):
        print("  born-alive: referent enum %s 부재" % c); ok = False
print("  born-alive: 두 모듈 import + 3 ablatable axis fn + run_guard callable" if ok else "  born-alive: DEFECT")
sys.exit(0 if ok else 1)
PY

# ═════════════════════════════════════════════════════════════════════════════
# Part A — 5-fixture replay (exact-match 5/5 mandatory; mismatch = D6_RED canary death)
# ═════════════════════════════════════════════════════════════════════════════
run_py "A: 5-fixture replay" <<'PY'
import sys
LIB, WORK = sys.argv[1], sys.argv[2]
sys.path.insert(0, WORK); sys.path.insert(0, LIB)
import decision_record_disposition as m
import cfp2697_fixtures as F
ok = True
for k in ("P-1", "P-2", "P-3", "N-1", "N-2"):
    got = m.classify(F.FIX[k])["disposition"]
    exp = F.EXP[k]
    flag = "OK" if got == exp else "D6_RED-MISMATCH(canary death)"
    print("  A %-4s expect=%-11s actual=%-11s %s" % (k, exp, got, flag))
    if got != exp:
        ok = False
sys.exit(0 if ok else 1)
PY

# ═════════════════════════════════════════════════════════════════════════════
# Part B — mutation-kill (3 축 = 3 killing mutants; ablate → verdict flip = 축 load-bearing)
# ═════════════════════════════════════════════════════════════════════════════
# M1 referent-blind — axis_referent 를 상시 in-scope(bp-context-count)로 ablate.
#   N-1 homonym 이 이제 correct 로 MISCLASSIFY 되어야 함(no_action → 이탈). 안 flip = referent 축 decorative.
run_py "B/M1: referent-blind (N-1 homonym)" <<'PY'
import sys
LIB, WORK = sys.argv[1], sys.argv[2]
sys.path.insert(0, WORK); sys.path.insert(0, LIB)
import decision_record_disposition as m
import cfp2697_fixtures as F
n1 = F.FIX["N-1"]
before = m.classify(n1)["disposition"]                                   # 실 axis_referent
m.axis_referent = lambda *a, **k: m.REFERENT_BP_CONTEXT_COUNT            # ablate → 항상 in-scope
after = m.classify(n1)["disposition"]
killed = (before == "no_action") and (after != "no_action")
print("  M1 referent-blind: N-1 before=%s after=%s (flip=%s)" % (before, after, before != after))
print("  M1 verdict: %s" % ("KILLED — referent 축 load-bearing (ablation flips no_action→%s)" % after
                            if killed else "SURVIVED — referent 축 decorative(FAIL)"))
sys.exit(0 if killed else 1)
PY

# M2 tense-blind — axis_tense 를 상시 not-dated(False)로 ablate.
#   N-2 dated 가 이제 correct 로 MISCLASSIFY 되어야 함(보존 → 이탈). 안 flip = tense 축 decorative.
run_py "B/M2: tense-blind (N-2 dated)" <<'PY'
import sys
LIB, WORK = sys.argv[1], sys.argv[2]
sys.path.insert(0, WORK); sys.path.insert(0, LIB)
import decision_record_disposition as m
import cfp2697_fixtures as F
n2 = F.FIX["N-2"]
before = m.classify(n2)["disposition"]                                   # 실 axis_tense (dated=True)
m.axis_tense = lambda *a, **k: False                                     # ablate → present-normative 취급
after = m.classify(n2)["disposition"]
killed = (before == "no_action") and (after == "correct")
print("  M2 tense-blind: N-2 before=%s after=%s (flip=%s)" % (before, after, before != after))
print("  M2 verdict: %s" % ("KILLED — tense 축 load-bearing (ablation flips no_action→%s)" % after
                            if killed else "SURVIVED — tense 축 decorative(FAIL)"))
sys.exit(0 if killed else 1)
PY

# M3 cardinal-blind — axis_cardinal_bound 를 상시 no-cardinal(False)로 ablate.
#   P-1/2/3 가 이제 no_action 으로 MISCLASSIFY 되어야 함(correct → 이탈). 안 flip = cardinal 축 decorative.
run_py "B/M3: cardinal-blind (P-1/2/3)" <<'PY'
import sys
LIB, WORK = sys.argv[1], sys.argv[2]
sys.path.insert(0, WORK); sys.path.insert(0, LIB)
import decision_record_disposition as m
import cfp2697_fixtures as F
ks = ("P-1", "P-2", "P-3")
before = {k: m.classify(F.FIX[k])["disposition"] for k in ks}            # 실 axis_cardinal_bound
m.axis_cardinal_bound = lambda *a, **k: False                            # ablate → no-cardinal
after = {k: m.classify(F.FIX[k])["disposition"] for k in ks}
ok = True
for k in ks:
    flip = (before[k] == "correct") and (after[k] == "no_action")
    print("  M3 cardinal-blind: %s before=%s after=%s flip=%s" % (k, before[k], after[k], flip))
    if not flip:
        ok = False
print("  M3 verdict: %s" % ("KILLED — cardinal 축 load-bearing across P-1/2/3"
                            if ok else "SURVIVED — cardinal 축 decorative(FAIL)"))
sys.exit(0 if ok else 1)
PY

# M3b MUTANT-D cardinal-loosen — axis_cardinal_bound 를 상시 True(과잉허용)로 ablate.
#   (FIX F2: mutation battery 대칭 — M3 은 →False(과잉거부)만, 이 case 는 →True(loosen)를 KILL.)
#   서술형 bp 라인 D-1 이 이제 no_action → correct 로 MISCLASSIFY 되어야 함. 안 flip = self-test hollow.
run_py "B/M3b: cardinal-loosen (MUTANT-D, D-1)" <<'PY'
import sys
LIB, WORK = sys.argv[1], sys.argv[2]
sys.path.insert(0, WORK); sys.path.insert(0, LIB)
import decision_record_disposition as m
import cfp2697_fixtures as F
d1 = F.FIX["D-1"]
before = m.classify(d1)["disposition"]                                   # 실 axis_cardinal_bound → no_action
m.axis_cardinal_bound = lambda *a, **k: True                             # MUTANT-D: 과잉허용(loosen)
after = m.classify(d1)["disposition"]
killed = (before == "no_action") and (after == "correct")
print("  M3b cardinal-loosen: D-1 before=%s after=%s (flip=%s)" % (before, after, before != after))
print("  M3b verdict: %s" % ("KILLED — loosen-mutant 이 correct 로 flip(cardinal 축 대칭 load-bearing)"
                            if killed else "SURVIVED — loosen-mutant 생존(self-test hollow, FAIL)"))
sys.exit(0 if killed else 1)
PY

# ═════════════════════════════════════════════════════════════════════════════
# Part C / M4 — anti-overfit: 부수 토큰 교체 후 verdict 불변 = 일반화(암기 아님)
# ═════════════════════════════════════════════════════════════════════════════
run_py "C/M4: perturbation stable (anti-overfit)" <<'PY'
import sys
LIB, WORK = sys.argv[1], sys.argv[2]
sys.path.insert(0, WORK); sys.path.insert(0, LIB)
import decision_record_disposition as m
import cfp2697_fixtures as F
ok = True
for k, (text, exp) in F.PERT.items():
    got = m.classify(text)["disposition"]
    flag = "OK" if got == exp else "OVERFIT-MISMATCH"
    print("  M4 perturb %-5s expect=%-11s actual=%-11s %s" % (k, exp, got, flag))
    if got != exp:
        ok = False
print("  M4 verdict: %s (부수-토큰 perturbation 하 verdict 안정 = FEATURE 일반화, fixture-신원 암기 아님)"
      % ("PASS" if ok else "FAIL"))
sys.exit(0 if ok else 1)
PY

# ═════════════════════════════════════════════════════════════════════════════
# Part C / M5 — structural-guard conjunction gates (rubber-stamp 아님 실증)
#   delete 는 4-check(¬parse ∧ inbound=0 ∧ external-id-safe ∧ structure-intact) 전부여야 pass.
#   각 conjunct 를 독립 위반시켜 pass=false + strip_normativity 강등을 assert(hermetic temp repo).
# ═════════════════════════════════════════════════════════════════════════════
run_py "C/M5: guard conjunction gates" <<'PY'
import sys, os, tempfile
LIB, WORK = sys.argv[1], sys.argv[2]
sys.path.insert(0, WORK); sys.path.insert(0, LIB)
import reference_integrity_guard as g

def build(files):
    root = tempfile.mkdtemp(prefix="cfp2697_g_")
    for rel, content in files.items():
        p = os.path.join(root, *rel.split("/"))
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(content)
    return root

ok = True

# (1) delete FAILS — external-id 가 required-context workflow 에 인용됨 → external_id_safe=False.
root = build({".github/workflows/phase-gate-mergeable.yml": "jobs:\n  x:\n    steps:\n      - run: echo ADR-777\n"})
r = g.run_guard({"file": "docs/foo.md", "external_ids": ["ADR-777"], "row": None}, "delete", repo_root=root)
c1 = (r["pass"] is False) and (r.get("recommend") == "strip_normativity") \
     and (r["delete_conjunction"]["external_id_safe"] is False)
print("  M5.1 delete + external-id-cited: pass=%s recommend=%s external_id_safe=%s -> %s"
      % (r["pass"], r.get("recommend"), r["delete_conjunction"]["external_id_safe"], "OK" if c1 else "FAIL"))
ok = ok and c1

# (2) delete FAILS — inbound_count>0 (다른 곳이 이 row 를 인용) → no_inbound=False.
root = build({"archive/other.md": "여기 어딘가 §결정 42 를 언급"})
r = g.run_guard({"file": "docs/bar.md", "body": "이 문장은 §결정 42 를 인용한다", "row": None}, "delete", repo_root=root)
c2 = (r["pass"] is False) and (r.get("recommend") == "strip_normativity") \
     and (r["delete_conjunction"]["no_inbound"] is False)
print("  M5.2 delete + inbound>0: pass=%s recommend=%s no_inbound=%s -> %s"
      % (r["pass"], r.get("recommend"), r["delete_conjunction"]["no_inbound"], "OK" if c2 else "FAIL"))
ok = ok and c2

# (3) clean delete — parse 0 ∧ inbound 0 ∧ external-id 0 ∧ structure intact → pass=true.
root = build({"docs/keep.md": "unrelated"})
r = g.run_guard({"file": "docs/clean.md",
                 "body": "이 라인은 branch protection 6-tuple 무변경 서술만 있고 외부 id 없음",
                 "row": None}, "delete", repo_root=root)
c3 = (r["pass"] is True)
print("  M5.3 clean delete: pass=%s -> %s" % (r["pass"], "OK" if c3 else "FAIL"))
ok = ok and c3

print("  M5 verdict: %s (4-check conjunction 이 실제로 gate — rubber-stamp 아님)" % ("PASS" if ok else "FAIL"))
sys.exit(0 if ok else 1)
PY

# ─────────────────────────────────────────────────────────────────────────────
# Summary
# ─────────────────────────────────────────────────────────────────────────────
echo ""
echo "============================================================"
echo "CFP-2697 D6 self-test — decision-record disposition oracle + reference-integrity guard"
echo "============================================================"
echo "PASS: ${PASS} / FAIL: ${FAIL} / TOTAL: $((PASS + FAIL))"
echo ""

if [ "${FAIL}" -eq 0 ]; then
  echo "✓ 전 case pass — Part A(5/5 replay) + Part B(M1/M2/M3 mutation-kill) + Part C(M4 perturb, M5 guard)"
  exit 0
else
  echo "✗ ${FAIL} case FAIL — mutation SURVIVED 또는 verdict mismatch(born-hollow / D6_RED)"
  exit 1
fi
