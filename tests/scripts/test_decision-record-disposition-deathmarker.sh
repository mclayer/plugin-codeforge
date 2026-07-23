#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# tests/scripts/test_decision-record-disposition-deathmarker.sh
# CFP-2799 / Epic #2696 B(#2698) gray-zone 완결 — death-marker/amendment oracle 확장의
#   discriminating self-test (Change Plan §8.B born-broken 봉인, 비협상).
#
# 목적(mutation-kill = born-hollow 회피): 신규 detection 축(sibling + DBM-3 broaden + census DI)이
#   "축-완전(load-bearing)"임을 실 소스 monkeypatch 로 실증(복사본 아님, 양방향 KILL).
#   대상: scripts/lib/decision_record_disposition_deathmarker.py (sibling)
#         scripts/lib/dated_block_mapper.py                       (DBM-3 4-detector)
#         scripts/lib/decision_record_disposition.py              (census DI)
#         scripts/lib/sweep_executor.py                           (delete-gap seal)
#         scripts/decision-record-sweep.py                        (composition root exclusion)
#
# born-alive: 각 case = 독립 python 프로세스(fresh interpreter) → monkeypatch 오염 0(flip 이 진짜).
#   어떤 assertion 도 `|| true` 로 mask 하지 않는다(ADR-060 Amd22 exit-masking 금지). exit 1 = FAIL.
#
# anti-overfit(비협상): fixture = 대표 literal(ASCII/영문 death 어휘 — heredoc mangle-free),
#   파일 신원 하드코딩 0. 정직 천장(ADR-119/ADR-151 §결정7): 축 load-bearing + 계약 verdict 까지만
#   실증 — "death 오라클이 모든 실세계 stale 을 완전 분류한다"는 hard-claim 하지 않는다.
#
# ── Change Plan §8.B 매핑 ─────────────────────────────────────────────────────
#  Part A  baseline verdict(5): death candidate / census pl_review_bucket / homonym-reject /
#          dated 보존 / delete-eligible marker skip(seal) — 원본 GREEN.
#  Part B  mutation-kill(6, real-source monkeypatch): M1 under-detect / M2 over-detect /
#          M3 amendment_log-off / M4 bare-xref dated-force / M5 census-dispatch-off /
#          M6 #2698 exclusion-off — 각 축 ablate 시 verdict flip(RED).
#  Part C  positive-control: bare-xref NOT dated + sunset_justification NOT death + INV-R2 byte-unchanged.
#  Part D  guard FIX iter1 회귀(SecurityTestPL P2×2, reference_integrity_guard.py:234): D1 case-fix
#          (CWE-178 dead-branch → ADR argv body_parsed True) + D2 ReDoS-bound(CWE-1333 → <2.0s, real-source).
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail
export LC_ALL=C.UTF-8
export LANG=C.UTF-8
export PYTHONIOENCODING=utf-8

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
LIB="${REPO_ROOT}/scripts/lib"
SIB="${LIB}/decision_record_disposition_deathmarker.py"
DBM="${LIB}/dated_block_mapper.py"
ORACLE="${LIB}/decision_record_disposition.py"
SWEEP="${LIB}/sweep_executor.py"

PY="${PYTHON:-python}"
command -v "$PY" >/dev/null 2>&1 || PY="python3"
command -v "$PY" >/dev/null 2>&1 || { echo "FAIL: python/python3 부재"; exit 1; }

# module-existence guard (부재 = DeveloperAgent 미구현 노출, silent skip 금지)
for m in "$SIB" "$DBM" "$ORACLE" "$SWEEP"; do
  [ -f "$m" ] || { echo "FAIL: 모듈 부재: $m (구현 미완 — PL 재실행 필요)"; exit 1; }
done

WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
export CFP2799_REPO="$REPO_ROOT"

PASS=0
FAIL=0
run_case() {
  # $1=label  $2=python-file ; python 이 exit 0 이면 pass, 아니면 fail(마스킹 없음).
  local label="$1" pyf="$2"
  if "$PY" "$pyf" >/dev/null 2>"${WORK}/err.txt"; then
    PASS=$((PASS+1)); echo "  ok  : $label"
  else
    FAIL=$((FAIL+1)); echo "  FAIL: $label"; sed 's/^/        /' "${WORK}/err.txt"
  fi
}

# ── 공유 헬퍼 python prologue (import + fixture literal, ASCII 영문 death 어휘) ──
cat > "${WORK}/_pre.py" <<'PYPRE'
# -*- coding: utf-8 -*-
import os, sys, tempfile
REPO = os.environ["CFP2799_REPO"]
sys.path.insert(0, os.path.join(REPO, "scripts", "lib"))
import dated_block_mapper as dbm
import decision_record_disposition as oracle
import decision_record_disposition_deathmarker as dm
import sweep_executor as sx

LIVE_DEATH = "this legacy rule is deprecated and no longer applies"      # 영문 death 어휘(ASCII)
HOMONYM = "sunset_justification: audit reason for the evidence gate"      # homonym field name
BARE_XREF_DOC = ("---\ntitle: t\namendments:\n  - ADR-033\n  - ADR-041\n---\n# D\n\n"
                 "## Amendment 1\n\nsome amendment body line here\n")
AMENDMENT_LOG_DOC = ("---\ntitle: t\namendment_log:\n  - entry: x\n---\n# D\n\n"
                     "## Amendment 1\n\nthis amendment line is deprecated per the log\n")

def write(name, text):
    d = tempfile.mkdtemp()
    p = os.path.join(d, name)
    open(p, "w", encoding="utf-8", newline="\n").write(text)
    return d, p

def die(msg):
    sys.stderr.write("ASSERT-FAIL: %s\n" % msg); sys.exit(1)
PYPRE

# ═════════════════════════ Part A — baseline verdicts (원본 GREEN) ═════════════════════════
echo "── Part A: baseline verdicts ──"

export CFP2799_PRE="${WORK}/_pre.py"

cat > "${WORK}/a_death_candidate.py" <<'PY'
import os
exec(open(os.environ["CFP2799_PRE"], encoding="utf-8").read())
if not dm._is_deathmarker_candidate(LIVE_DEATH): die("baseline: live death 는 candidate 여야")
if dm._is_deathmarker_candidate(HOMONYM): die("baseline: sunset_justification 은 candidate 아님")
print("ok")
PY
run_case "A1 death candidate + homonym reject" "${WORK}/a_death_candidate.py"

cat > "${WORK}/a_census_bucket.py" <<'PY'
import os
exec(open(os.environ["CFP2799_PRE"], encoding="utf-8").read())
d, p = write("a.md", "# D\n\n" + LIVE_DEATH + "\n")
dc = dm.build_domain_classifiers()
rep = oracle._census_over_files([p], domain_classifiers={"deathmarker": dc["deathmarker"]})
if "pl_review_bucket" not in rep: die("census 반환에 pl_review_bucket key 부재")
if len(rep["pl_review_bucket"]) < 1: die("baseline: live death → pl_review_bucket surface 여야")
if rep["needs_disposition"] != []: die("baseline: death domain 은 no-blind-apply(needs 미투입)")
print("ok")
PY
run_case "A2 census pl_review_bucket + no-blind-apply" "${WORK}/a_census_bucket.py"

cat > "${WORK}/a_dated_preserve.py" <<'PY'
import os
exec(open(os.environ["CFP2799_PRE"], encoding="utf-8").read())
r = dm.classify_deathmarker(LIVE_DEATH, dated_context=True)
if r["disposition"] != oracle.DISPOSITION_NO_ACTION: die("dated death → no_action")
if r["pl_review"] is not False: die("dated death → pl_review False(보존, 회부 불요)")
if r["disposition"] not in dm.DISPOSITIONS: die("5-enum 밖")
print("ok")
PY
run_case "A3 dated death 보존(no_action, pl_review False)" "${WORK}/a_dated_preserve.py"

cat > "${WORK}/a_delete_seal.py" <<'PY'
import os
exec(open(os.environ["CFP2799_PRE"], encoding="utf-8").read())
# delete-eligible + marker-bearing 라인 → apply 가 삭제하지 말아야(SecurityArch P1 seal).
marker_line = "some dead rule text" + sx._DEATH_MARKER
d, p = write("s.md", "# D\n\n" + marker_line + "\n")
before = open(p, "rb").read()
plan = [{"file": "s.md", "line": 3, "action": "delete", "guard_pass": True,
         "disposition": "delete", "rationale": "x"}]
res = sx.apply(plan, repo_root=d, live_count=1)
after = open(p, "rb").read()
if before != after: die("delete-gap seal: marker-bearing 라인이 guard_pass 여도 삭제되면 안 됨")
if res["applied"]["delete"] != 0: die("delete count 0 이어야(seal skip)")
print("ok")
PY
run_case "A4 delete-gap seal(marker-bearing delete skip, SecurityArch P1)" "${WORK}/a_delete_seal.py"

# ═════════════════════════ Part B — mutation-kill (real-source, flip RED) ═════════════════════════
echo "── Part B: mutation-kill (real-source monkeypatch) ──"

cat > "${WORK}/m1_under.py" <<'PY'
import os
exec(open(os.environ["CFP2799_PRE"], encoding="utf-8").read())
d, p = write("m.md", "# D\n\n" + LIVE_DEATH + "\n")
dm._is_deathmarker_candidate = lambda line: False           # MUTANT: 상시 False(under-detect)
dc = dm.build_domain_classifiers()
rep = oracle._census_over_files([p], domain_classifiers={"deathmarker": dc["deathmarker"]})
# KILL: candidate 소멸 → live death 가 더는 surface 안 됨(baseline 은 surface 했다).
if len(rep["pl_review_bucket"]) != 0:
    die("under-detect mutant 인데 여전히 surface — candidate 축 미검출력(KILL 실패)")
print("killed")
PY
run_case "M1 under-detect KILL (_is_deathmarker_candidate→False)" "${WORK}/m1_under.py"

cat > "${WORK}/m2_over.py" <<'PY'
import os
exec(open(os.environ["CFP2799_PRE"], encoding="utf-8").read())
d, p = write("m.md", "# D\n\n" + HOMONYM + "\n")   # homonym-only 문서(baseline: 후보 아님 → 미surface)
dm._is_deathmarker_candidate = lambda line: True            # MUTANT: 상시 True(over-detect)
dc = dm.build_domain_classifiers()
rep = oracle._census_over_files([p], domain_classifiers={"deathmarker": dc["deathmarker"]})
# KILL: homonym(sunset_justification) 이 flagged 됨(baseline 은 reject 로 미surface).
lines = {e["line"] for e in rep["pl_review_bucket"]}
if 3 not in lines:
    die("over-detect mutant 인데 homonym 이 flagged 안 됨 — prefilter 축 미load-bearing(KILL 실패)")
print("killed")
PY
run_case "M2 over-detect KILL (_is_deathmarker_candidate→True, homonym flagged)" "${WORK}/m2_over.py"

cat > "${WORK}/m3_amendlog.py" <<'PY'
import os
exec(open(os.environ["CFP2799_PRE"], encoding="utf-8").read())
d, p = write("adr.md", AMENDMENT_LOG_DOC)
# baseline provider: amendment_log → Amendment region dated → death 라인 보존(미surface).
dbm._has_amendment_log_key = lambda text: False             # MUTANT: amendment_log detector off
prov = dbm.make_dated_provider(d)
dc = dm.build_domain_classifiers()
rep = oracle._census_over_files([p], dated_provider=prov,
                                domain_classifiers={"deathmarker": dc["deathmarker"]})
# death 라인(Amendment region 안)이 undated 로 뒤집혀 pl_review 로 surface(=INV-R2 라인 편집대상 flip).
if len(rep["pl_review_bucket"]) == 0:
    die("amendment_log-off mutant 인데 region 이 여전히 dated — detector 미load-bearing(KILL 실패)")
print("killed")
PY
run_case "M3 amendment_log-off KILL (dated region 붕괴→INV-R2 라인 flip)" "${WORK}/m3_amendlog.py"

cat > "${WORK}/m4_barexref.py" <<'PY'
import os
exec(open(os.environ["CFP2799_PRE"], encoding="utf-8").read())
# baseline: bare-xref 문서 → NOT dated(AC-11). MUTANT: bare_xref 를 OR 에 강제 포함.
_od, _os, _ol, _ob = (dbm._is_dict_date_amendments, dbm._is_self_slug_amendments,
                      dbm._has_amendment_log_key, dbm._is_bare_xref_amendments)
dbm._has_dated_amendments_frontmatter = (
    lambda text: _od(text) or _os(text) or _ol(text) or _ob(text))   # MUTANT: bare_xref OR 강제
dated = dbm.dated_line_numbers(BARE_XREF_DOC)
# KILL: bare-xref 문서가 dated 로 뒤집힘(baseline 은 empty → AC-11 flip).
if dated == set():
    die("bare-xref dated-force mutant 인데 여전히 NOT dated — OR-제외가 미load-bearing(KILL 실패)")
print("killed")
PY
run_case "M4 bare-xref dated-force KILL (AC-11 flip)" "${WORK}/m4_barexref.py"

cat > "${WORK}/m5_dispatch.py" <<'PY'
import os
exec(open(os.environ["CFP2799_PRE"], encoding="utf-8").read())
d, p = write("m.md", "# D\n\n" + LIVE_DEATH + "\n")
# MUTANT: census dispatch off(domain_classifiers 미주입) → candidate 라우팅 소멸.
rep = oracle._census_over_files([p], domain_classifiers=None)
# KILL: pl_review_bucket 비어야(dispatch 축 load-bearing — 있으면 death 가 cardinal path 로 샜다는 것).
if rep["pl_review_bucket"] != []:
    die("dispatch-off mutant 인데 death 가 여전히 surface — census DI 미load-bearing(KILL 실패)")
print("killed")
PY
run_case "M5 census-dispatch-off KILL (domain 라우팅 소멸)" "${WORK}/m5_dispatch.py"

cat > "${WORK}/m6_exclusion.py" <<'PY'
import os
exec(open(os.environ["CFP2799_PRE"], encoding="utf-8").read())
import importlib.util
cli = os.path.join(REPO, "scripts", "decision-record-sweep.py")
spec = importlib.util.spec_from_file_location("drs", cli)
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
manifest = [{"file": "x.md", "line": 3}]
with_excl = mod._apply_exclusions(list(manifest), None, ["x.md:3"])
without_excl = mod._apply_exclusions(list(manifest), None, None)   # MUTANT: exclusion off
# KILL: baseline(exclusion) → 제외되어 empty; off → 재처리(non-empty) = AC-6 flip.
if with_excl != []:
    die("exclusion 인데 라인이 제외 안 됨(baseline 붕괴)")
if without_excl == []:
    die("exclusion-off mutant 인데도 empty — _apply_exclusions 미load-bearing(KILL 실패)")
print("killed")
PY
run_case "M6 #2698 exclusion-off KILL (AC-6 재처리 flip)" "${WORK}/m6_exclusion.py"

# ═════════════════════════ Part C — positive-control ═════════════════════════
echo "── Part C: positive-control ──"

cat > "${WORK}/c_homonym.py" <<'PY'
import os
exec(open(os.environ["CFP2799_PRE"], encoding="utf-8").read())
if dbm._is_bare_xref_amendments(BARE_XREF_DOC) is not True: die("bare-xref 판별자 True 여야")
if dbm._has_dated_amendments_frontmatter(BARE_XREF_DOC) is not False: die("bare-xref → NOT dated(AC-11)")
if dm._is_deathmarker_candidate(HOMONYM): die("sunset_justification → death 후보 아님")
print("ok")
PY
run_case "C1 homonym-reject positive-control (bare-xref NOT dated / sunset_justification NOT death)" "${WORK}/c_homonym.py"

cat > "${WORK}/c_invr2.py" <<'PY'
import os
exec(open(os.environ["CFP2799_PRE"], encoding="utf-8").read())
d, p = write("adr.md", AMENDMENT_LOG_DOC)
before = open(p, "rb").read()
prov = dbm.make_dated_provider(d)
rep = oracle._census_over_files([p], dated_provider=prov)   # cardinal path
manifest = [{"file": "adr.md", "line": e["line"]} for e in rep["needs_disposition"] if "line" in e]
plan = sx.plan(manifest, repo_root=d, live_required_contexts={"a"})
sx.apply(plan, repo_root=d, live_count=1)
after = open(p, "rb").read()
if before != after: die("INV-R2: dated amendment_log 라인 apply 후 byte 변경 — 불가침 위반")
print("ok")
PY
run_case "C2 INV-R2 positive-control (dated amendment_log byte-unchanged)" "${WORK}/c_invr2.py"

# ═════════════════════════ Part D — guard FIX iter1 회귀 (SecurityTestPL P2×2, line 234) ═════════════════════════
echo "── Part D: reference_integrity_guard check_parser_scan FIX 회귀 ──"

cat > "${WORK}/d_casefix.py" <<'PY'
import os
exec(open(os.environ["CFP2799_PRE"], encoding="utf-8").read())
import re
import reference_integrity_guard as g
# (P2-② CWE-178 case dead-branch 재현 + 정정) — line=raw.lower(), base=ADR-NNN(대문자).
base = "ADR-127-foo.md"
argv_low = "python scripts/decision-record-sweep.py archive/adr/adr-127-foo.md"
old_hit = re.search(r"(python|bash|sh|\./)\S*.*" + re.escape(base), argv_low) is not None
bl = base.lower(); pos = argv_low.find(bl)
new_hit = pos != -1 and any(t in argv_low[:pos] for t in ("python", "bash", "sh", "./"))
if old_hit is not False:
    die("case-bug 재현 실패 — 구 regex 가 lowercased line 에서 uppercase base 로 dead 여야")
if new_hit is not True:
    die("case-fix 실패 — 수정 로직이 ADR argv 라인을 감지해야")
# real-source end-to-end: 수정된 check_parser_scan 가 ADR argv 라인 감지(body_parsed True).
d = tempfile.mkdtemp()
os.makedirs(os.path.join(d, "scripts")); os.makedirs(os.path.join(d, "archive", "adr"))
open(os.path.join(d, "archive", "adr", "ADR-127-foo.md"), "w", encoding="utf-8", newline="\n").write("# ADR-127\nbody\n")
open(os.path.join(d, "scripts", "runner.sh"), "w", encoding="utf-8", newline="\n").write(
    "#!/bin/bash\npython tool.py archive/adr/ADR-127-foo.md\n")
res = g.check_parser_scan({"file": "archive/adr/ADR-127-foo.md"}, d)
if res["body_parsed"] is not True:
    die("real-source check_parser_scan ADR argv 미감지 — case dead-branch 잔존(mutation: base.lower() 제거 시 RED)")
print("ok")
PY
run_case "D1 case-fix (CWE-178 dead-branch → ADR argv body_parsed True, real-source)" "${WORK}/d_casefix.py"

cat > "${WORK}/d_redos.py" <<'PY'
import os
exec(open(os.environ["CFP2799_PRE"], encoding="utf-8").read())
import re, time
import reference_integrity_guard as g
# (P2-① CWE-1333) real-source ReDoS-bound: 64KB no-ws repeat-anchor corpus 라인 → bounded.
#   수정본(linear substring) = ms. revert(`\S*.*` regex) = super-linear backtracking → 초과 RED.
d = tempfile.mkdtemp()
os.makedirs(os.path.join(d, "scripts")); os.makedirs(os.path.join(d, "archive", "adr"))
open(os.path.join(d, "archive", "adr", "ADR-127-foo.md"), "w", encoding="utf-8", newline="\n").write("# ADR-127\nbody\n")
open(os.path.join(d, "scripts", "patho.sh"), "w", encoding="utf-8", newline="\n").write(
    "python " + "adr-" * 16000 + "\n")  # ~64KB non-ws repeat-anchor, full base 부재
t0 = time.perf_counter(); g.check_parser_scan({"file": "archive/adr/ADR-127-foo.md"}, d); scan_t = time.perf_counter() - t0
if scan_t >= 2.0:
    die("check_parser_scan adversarial corpus 시간 초과(%.3fs>=2.0s) — ReDoS 잔존(revert 감지)" % scan_t)
# 참조(informational, non-asserted): 구 vulnerable regex 의 super-linear 특성 문서화(소입력).
old = re.compile(r"(python|bash|sh|\./)\S*.*" + re.escape("ADR-127-foo.md"))
ref = "python" + "adr-" * 2000
t0 = time.perf_counter(); old.search(ref); old_t = time.perf_counter() - t0
print("ok scan=%.4fs(bound 2.0s) ref_old_regex(2406ch)=%.4fs(super-linear class)" % (scan_t, old_t))
PY
run_case "D2 ReDoS-bound (CWE-1333 super-linear → check_parser_scan <2.0s, real-source)" "${WORK}/d_redos.py"

# ── verdict ──
echo ""
echo "SUMMARY: pass=${PASS} fail=${FAIL}"
if [ "$FAIL" -ne 0 ]; then
  echo "RESULT: FAIL (born-broken 봉인 위반 — mutation-kill/baseline 불일치)"
  exit 1
fi
echo "RESULT: PASS (baseline GREEN ∧ 6 mutation-kill RED-flip ∧ positive-control)"
exit 0
