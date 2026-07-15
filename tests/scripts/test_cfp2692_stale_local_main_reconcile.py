#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tests/scripts/test_cfp2692_stale_local_main_reconcile.py
CFP-2692 Phase 2 self-test — `stale-local-main-checkout-divergence-check` registry entry
reconcile 봉인 (Change Plan §8.1 Test Contract SSOT 이행).

대상 reconcile: dangling workflow 참조 → workflow:null 정정 + promotion_trigger
auto_blocking→advisory truth-correction (ADR-119 정직) + baseline gate_flag drop.
본 self-test 는 그 산출물을 실 reconcile 모듈로 **실 import·실 구동** 하여 봉인한다
(재구현 0 — R.classify_entry / R.load_baseline / R.baseline_tamper_reasons /
G.collect_gate_flags 재사용, ADR-140 hygiene).

정직 천장 (honest ceiling):
  · O1 의 None 은 grandfather 층이 아니라 pre-grandfather 층(workflow:null → skip →
    carrier 실존)에서 구동된다. positive-control(FLAG) + isolation(INFO) 로 oracle liveness
    를 실증 → "항상 None" tautology 차단.
  · O2 tamper-axis 만 O1 과 완전 독립. drop-axis 는 classify substrate 를 O1 과 공유.
  · structural(AC-8)/AC-7 은 review/field-shape tier — "완전 봉인" hard-claim 하지 않는다.

★X1 금지 (self-ref 최고위험): subprocess exit-code 를 어떤 oracle 로도 쓰지 않는다.
  grandfather-mask 로 reconcile 0줄에도 exit0 = false-GREEN 이므로, 모든 판정 =
  classify/tamper/필드값 직접 확인. 본 파일은 subprocess 를 fork 하지 않는다.

exit-masking/mock-seam (ADR-060 Amд22): 본 self-test 는 pytest(python) — 전 판정이
  `assert` = fail-loud. shell `cmd || true` exit-masking·mock-seam env 미해당.
"""
import os
import sys
import tempfile

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(REPO_ROOT, "scripts", "lib"))

import check_deferred_followup_reconcile as R  # noqa: E402  (재사용 SSOT — 재구현 금지)
import gen_deferred_followup_baseline as G  # noqa: E402  (collect_gate_flags 재사용)

REGISTRY = os.path.join(REPO_ROOT, "docs", "evidence-checks-registry.yaml")
BASELINE = os.path.join(REPO_ROOT, "docs", "deferred-followup-baseline.yaml")
ENTRY_NAME = "stale-local-main-checkout-divergence-check"


# ─────────────────────── helper (재사용 로더 — 재구현 0) ──────────────────────

def _live_entry():
    """live registry 에서 대상 entry 로드 (R.load_registry_entries 재사용)."""
    entries = R.load_registry_entries(REGISTRY)
    matches = [e for e in entries if e.get("name") == ENTRY_NAME]
    assert matches, "registry 에 %s entry 부재 (설계 전제 위반)" % ENTRY_NAME
    return matches[0]


def _hermetic_fixture_entry(promotion_trigger):
    """hermetic fixture entry (inline) — workflow 축 참조 보유, detect_command 축 참조 보유.

    실제 carrier 실존/부재는 repo_root(hermetic tmpdir) 에 파일을 놓느냐로 결정된다.
    """
    return {
        "name": ENTRY_NAME,
        "detect_command": "bash scripts/check-stale-local-main-checkout.sh",
        "workflow": "templates/github-workflows/stale-local-main-checkout-divergence-check.yml",
        "recurrence": {
            "count": 8,
            "threshold": 3,
            "promotion_trigger": promotion_trigger,
        },
    }


def _make_carrier_repo(tmp):
    """hermetic repo_root 구성:
      · scripts/check-stale-local-main-checkout.sh 생성 → detect_command 축 EXISTS(not absent).
      · templates/github-workflows/...yml 는 **미생성** → workflow 축 absent 유지.
    → carrier_absent(workflow) True → over-threshold + promotion_trigger 에 따라 FLAG/INFO.

    NOTE: 아래 open("w") 는 tempfile 내 **runtime 임시 파일**(git 밖, CRLF 게이트 대상 아님)
    이며 존재 여부만 os.path.exists 로 검사된다 — 내용/개행은 판정 무관.
    """
    os.makedirs(os.path.join(tmp, "scripts"))
    sh_path = os.path.join(tmp, "scripts", "check-stale-local-main-checkout.sh")
    with open(sh_path, "w", encoding="utf-8") as f:
        f.write("#!/usr/bin/env bash\n")  # 존재만 필요 — 내용 무관
    return tmp


# ─────────────────────── O1 main (§8.1 #1) ──────────────────────────────────

def test_o1_reconciled_entry_classify_none():
    """O1 main — reconciled entry 는 검출 모집단 제외(classify None), grandfather-immune.

    근거: workflow:null → R.resolve_workflow_field(None)={"kind":"skip"} → carrier_absent
    workflow 축 입력 아님. detect_command `.sh` EXISTS → detect_command 축 not absent.
    → carrier 실존 → classify None(자연 PASS). baseline 미참조 = pre-grandfather 층에서
    discriminate(grandfather gate_flags 안 봐도 None).
    """
    entry = _live_entry()
    assert R.classify_entry(entry, REPO_ROOT) is None


# ─────────────────────── O1 positive control (§8.1 #2) ──────────────────────

def test_o1_positive_control_flag():
    """O1 positive control — classify_entry oracle liveness 증명(항상 None tautology 차단).

    hermetic repo: `.sh` present(detect_command 축 EXISTS) + workflow yml 미생성(workflow 축
    absent). fixture promotion_trigger=auto_blocking + over-threshold → carrier-absent(workflow)
    → FLAG. 이 test 가 FLAG 를 실 관측함으로써 test_o1_* 의 None 이 "oracle 이 죽어 항상 None"
    이 아니라 실 분류 결과(discriminating)임을 입증.
    """
    with tempfile.TemporaryDirectory() as tmp:
        _make_carrier_repo(tmp)
        res = R.classify_entry(_hermetic_fixture_entry("auto_blocking"), tmp)
        assert res is not None and res["tier"] == "FLAG"


# ─────────────────────── O1 isolation (§8.1 #3) ─────────────────────────────

def test_o1_isolation_advisory_absent_info_not_none():
    """O1 isolation — advisory + carrier-absent → INFO(not None). causal claim executable.

    동일 hermetic repo(workflow absent, `.sh` present)에서 promotion_trigger 만 advisory.
    → INFO(not None). 따라서 O1 main 의 None 은 **advisory 다운그레이드가 구동하지 않음** —
    workflow:null(skip → carrier 실존)이 None 을 구동한다. advisory 는 INV-REG-1 overclaim
    제거용(semantic truth-correction)이며 게이트 강제 아님(honest ceiling): advisory 라 해도
    carrier-absent 면 여전히 INFO 로 관측됨을 실증(advisory 가 detection 을 끄지 않는다).
    """
    with tempfile.TemporaryDirectory() as tmp:
        _make_carrier_repo(tmp)
        res = R.classify_entry(_hermetic_fixture_entry("advisory"), tmp)
        assert res is not None and res["tier"] == "INFO"


# ─────────────────────── O2 (§8.1 #4) — 독립 축 ─────────────────────────────

def test_o2_baseline_entry_dropped_and_untampered():
    """O2 — baseline drop-axis + tamper-axis(독립).

    drop: reconcile 후 classify→None → gen 이 gate_flags 에서 drop → persisted baseline
      gate_flags 에 ENTRY_NAME 부재. (G.collect_gate_flags 재생성으로도 executable 확증 —
      live registry → gate_flags 에도 ENTRY drop.)
    tamper(O1 과 완전 독립 축): provenance present + content_digest 재계산 일치 = hand-edit 부재.
    honest ceiling: drop-axis 는 classify substrate 를 O1 과 공유 — tamper-axis 만 완전 독립.
    """
    b = R.load_baseline(BASELINE)
    names = [g.get("name") for g in (b.get("gate_flags") or [])]
    assert ENTRY_NAME not in names
    # gen 재생성 executable 확증: live registry → collect_gate_flags 도 ENTRY drop(classify None).
    regen_names = [
        g["name"]
        for g in G.collect_gate_flags(R.load_registry_entries(REGISTRY), REPO_ROOT)
    ]
    assert ENTRY_NAME not in regen_names
    # tamper-axis (완전 독립 — provenance 필드 present + content_digest 재계산 일치)
    assert R.baseline_tamper_reasons(b) == []


# ─────────────────────── AC-7 (§8.1 #5) — field-scoped ──────────────────────

def test_ac7_dangling_workflow_field_scoped_zero():
    """AC-7 — dangling workflow 참조 field-scoped zero (★repo-wide grep 절대 금지).

    scope = (a) live registry entry 의 `workflow:` 필드값 + (b) baseline gate_flag 한정.
      · (a) registry workflow 필드 null → dangling 아님.
      · (b) baseline gate_flag drop → dangling 아님.
    archive/adr/** ADR 이력 prose 안 workflow 경로 문자열은 dangling 아님(prose 인용) →
    grep-scope 제외. 순진한 repo-wide grep = false-RED(CFP-2673/2659 패턴). 본 test 는
    **어떤 repo-wide grep 도 수행하지 않는다** — field 값 직접 확인만.
    """
    entry = _live_entry()
    assert entry.get("workflow") is None
    b = R.load_baseline(BASELINE)
    assert ENTRY_NAME not in [g.get("name") for g in (b.get("gate_flags") or [])]


# ─────────────────────── structural closure (§8.1 #6) — declared/AC-8 ───────

def test_structural_closure_reconcile_shape():
    """구조 assertion (declared, AC-8, review-tier) — reconcile 산출물 field-shape.

    honest ceiling: auto_blocking→advisory 는 O1 의 None 을 구동하지 않는다(workflow:null 이
    구동) — 본 test 는 review/structural-tier 의 field-shape 확인이며 "완전 봉인" hard-claim
    아님. tier-downgrade-justification 존재는 truth-correction 근거 surface 를 확인한다.
    """
    entry = _live_entry()
    assert entry.get("workflow") is None
    assert entry["recurrence"]["promotion_trigger"] == "advisory"
    assert "tier-downgrade-justification" in entry


# ─────────────────────── fallback harness (pytest 우선) ──────────────────────

if __name__ == "__main__":
    # pytest 우선(`python -m pytest`). pytest 미설치 fallback — 각 test 직접 호출.
    _fns = [
        test_o1_reconciled_entry_classify_none,
        test_o1_positive_control_flag,
        test_o1_isolation_advisory_absent_info_not_none,
        test_o2_baseline_entry_dropped_and_untampered,
        test_ac7_dangling_workflow_field_scoped_zero,
        test_structural_closure_reconcile_shape,
    ]
    _failed = 0
    for _fn in _fns:
        try:
            _fn()
            print("PASS %s" % _fn.__name__)
        except AssertionError as _e:
            _failed += 1
            print("FAIL %s: %s" % (_fn.__name__, _e))
    sys.exit(1 if _failed else 0)
