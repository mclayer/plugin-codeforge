#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_story_read_surface_mutants.py — CFP-2986 Phase 2 §8.2 mutant 배터리 + §8.3 경계 조건.

본 파일이 이 Story 의 **핵심 계약**이다. 배터리는 자기 자신에게도 적용된다 (§8.4a):
  ① 지정 mutant RED  ② 형제 site 회귀 0  ③ 검출 정의역 비축소(mutant 축 ∧ 정의역 로스터 축)
  ④ 무변경 정본 GREEN (최소 통과선)

C-6 (최우선): 설계 하네스는 오라클을 `if False:` 로 통째 무력화해도 23/23 GREEN · exit 0 이었다.
원인 = 배터리가 **boolean 만 assert 하고 위반 개수를 안 봤다.** 그래서 본 배터리는
  · 위반 **개수(count)** 와 per-mutant **판정 벡터**를 assert 하고
  · `M-SUTURE` 를 실제 소스 변형으로 주입해 **배터리 자신이 RED 가 되는지** 실행 확인한다.
이것이 GREEN 이면 배터리는 무의미하다.

QADev 경계: 본 파일은 테스트만 작성. production 코드(scripts/**) READ-ONLY.
"""

from __future__ import annotations

import ast
import inspect
import re
import tokenize
from io import StringIO

import yaml

import _story_read_surface_fixtures as FX
import test_story_read_surface as NT

THETA = 4096


def engine():
    return NT.engine()


# ---------------------------------------------------------------------------
# 배터리 전건 — 대조군 GREEN ∧ 주입 RED, 개수 + 벡터
# ---------------------------------------------------------------------------

def test_battery_admission_rule_holds_for_every_mutant():
    """§8.2 admission rule — 대조군이 이미 RED 인 mutant 는 등가 mutant 이므로 계상 금지."""
    results = FX.run_battery(engine())
    print(FX.format_report(results))
    bad = {mid: r["control"] for mid, r in results.items()
           if not mid.startswith("_") and r["control"] == "RED"}
    assert not bad, (
        "등가 mutant 검출 — 미주입 대조군이 이미 RED 다. "
        "이 상태에서 '검출했다' 고 선언하면 §8.2 자기 admission rule 위반이다: " + str(bad)
    )


def test_battery_per_domain_vector_not_global_scalar():
    """C-7 / C-13 — 전역 개수·전역 집합 대조는 양방향으로 우회된다. (셀ID → 값) 매핑을 정의역별로."""
    eng = engine()
    results = FX.run_battery(eng)

    # C-13 정의역 **간** 상쇄: 전역 집합은 불변인데 정의역별 분해는 RED 여야 한다.
    cross = results["M-CARD-CROSS"]
    assert cross["injected_red_count"] == 2, (
        f"M-CARD-CROSS 위반 개수 실측 {cross['injected_red_count']} != 2"
    )
    assert cross["vector"] == ["CP_S81_RTM:leg1", "CP_S81_RTM:leg2"]

    # 같은 주입을 **전역 집합**으로 재면 GREEN 이 된다 — 전역형이 왜 무력한지의 실증.
    bl = FX.build_baseline()
    ctx = FX.ctx_card_cross()
    resolve = FX.resolve_file_factory(eng, ctx)
    union_declared, union_actual = set(), set()
    for name in FX.ENFORCED_DOMAINS:
        dom = bl["domains"][name]
        union_declared |= set(dom["expected"])
        union_actual |= set(eng.extract_domain(dom, resolve(dom)))
    assert union_declared == union_actual, (
        "전역 집합 대조가 M-CARD-CROSS 를 잡아버렸다 — fixture 가 C-13 형상을 재현하지 못한다"
    )

    # C-7 정의역 **내** 보상 쌍: 개수 보존이라 cardinality 단독으로는 잡히지 않는다.
    inside = results["M-CARD-IN"]
    assert inside["vector"] == ["CP_S81_RTM:leg1"], (
        f"M-CARD-IN 이 leg1 단독이 아니다 — 실측 {inside['vector']}. "
        "leg2 가 같이 반응하면 leg1 의 load-bearing 을 증명할 수 없다."
    )


def test_leg_three_way_independent_falsification():
    """leg 3항 각각을 **단독으로** RED 로 만드는 mutant 가 실재해야 한다.

    어느 leg 을 제거해도 로스터가 통과하면 그 leg 은 강제되지 않는다.
    """
    results = FX.run_battery(engine())
    table = {
        "leg1": ("M-CARD-IN", ["CP_S81_RTM:leg1"]),
        "leg2": ("M-DUP-ROW", ["CP_S81_RTM:leg2"]),
        "leg3": ("M-CARD-VALUE", ["CORPUS:leg3"]),
    }
    for leg, (mid, expected_vec) in table.items():
        r = results[mid]
        assert r["control"] == "GREEN", f"{leg} falsifier {mid} 대조군이 RED (등가 mutant)"
        assert r["injected_red_count"] == 1, (
            f"{leg} 독립 반증 실패 — {mid} 위반 개수 {r['injected_red_count']} != 1"
        )
        assert r["vector"] == expected_vec, (
            f"{leg} 가 단독 RED 가 아니다 — {mid} 벡터 실측 {r['vector']} 기대 {expected_vec}"
        )


def test_deferred_domains_emit_undetermined_not_green():
    """§11.5 — `status: deferred` 는 GREEN 이 아니라 `UNDETERMINED` 다 (4번째 born-broken 차단)."""
    eng = engine()
    v = FX.run_inv_s3(eng, FX.canonical_ctx())
    und = FX.undetermined_domains(v)
    assert und >= set(FX.DEFERRED_DOMAINS), (
        f"deferred 4 정의역이 UNDETERMINED 로 방출되지 않았다 — 실측 {sorted(und)}. "
        "조용히 건너뛰면 §8.4 자신의 '파싱 실패 = 결손' 을 위반하고, "
        "enforced 로 두면 Phase 2 실체화 전까지 무조건 RED(born-broken)가 된다."
    )
    green = {getattr(x, "domain", None) for x in v if getattr(x, "status", None) == "PASS"}
    assert not (set(FX.DEFERRED_DOMAINS) & green), (
        f"deferred 정의역이 GREEN 으로 계상됐다 — {sorted(set(FX.DEFERRED_DOMAINS) & green)}"
    )


# ---------------------------------------------------------------------------
# ★ C-6 — M-SUTURE: self-test 가 봉합 제거를 잡아야 한다
# ---------------------------------------------------------------------------

def _battery_signature(eng):
    """배터리 판정을 단일 비교 가능 값으로 접는다 (개수 + 벡터 + 판정)."""
    try:
        res = FX.run_battery(eng)
    except Exception as exc:  # noqa: BLE001 - 예외도 '검출' 이다
        return ("EXCEPTION", type(exc).__name__, str(exc)[:200])
    return tuple(sorted(
        (mid, r["control"], r["injected"], r["control_red_count"],
         r["injected_red_count"], tuple(r["vector"]), r["verdict"])
        for mid, r in res.items() if not mid.startswith("_")
    ))


def _battery_signature_boolean_only(eng):
    """C-6 대조군 — **boolean 만** 보는 종전 배터리 형태(개수·벡터 미포함).

    설계 하네스가 봉합을 통째 놓친 것이 정확히 이 형태였다. 두 signature 의 검출력 차이를
    같은 실행에서 보여, 개수·벡터 요건이 장식이 아니라 load-bearing 임을 실증한다.
    """
    try:
        res = FX.run_battery(eng)
    except Exception as exc:  # noqa: BLE001
        return ("EXCEPTION", type(exc).__name__)
    return tuple(sorted((mid, r["control"], r["injected"])
                        for mid, r in res.items() if not mid.startswith("_")))


def _family_outcomes(eng):
    """불변식 family 별로 배터리가 관측한 status 집합 — 상수 판정(다양성 1) 탐지용."""
    out = {}
    for ctx, kw in ((FX.canonical_ctx(), {}), (FX.split_ctx(), {}),
                    (FX.ctx_e4_compensating_move(), {}),
                    (FX.ctx_e4_compensating_move(), {"reason_code": "AUTHORED_CONSOLIDATION"}),
                    (FX.ctx_e4_compensating_move(), {"reason_code": "자유서술"}),
                    (FX.ctx_append_ctl(1000), {})):
        for v in FX.run_inv_s2(eng, ctx, **kw):
            out.setdefault(v.name, set()).add(v.status)
    for ctx in (FX.canonical_ctx(), FX.split_ctx(), FX.ctx_e2_zwsp(), FX.ctx_dangling()):
        for v in FX.run_inv_s1(eng, ctx):
            out.setdefault(v.name, set()).add(v.status)
        for v in FX.run_inv_s3(eng, ctx):
            out.setdefault(v.name, set()).add(v.status)
        for v in FX.run_inv_s6(eng, ctx):
            out.setdefault(v.name, set()).add(v.status)
        for v in FX.run_anchor(eng, ctx):
            out.setdefault(v.name, set()).add(v.status)
    exp = {FX.STORY_PATH, FX.child_path(FX.SPLIT_ID)}
    for args in ((exp, exp, exp, 2, exp), (exp, {FX.STORY_PATH}, exp, 2, exp)):
        for v in eng.check_scan_domain(set(args[0]), set(args[1]), set(args[2]),
                                       args[3], carrier_set=set(args[4])):
            out.setdefault(v.name, set()).add(v.status)
    return out


def _battery_mismatches(eng):
    try:
        res = FX.run_battery(eng)
    except Exception as exc:  # noqa: BLE001
        return {"__exception__": f"{type(exc).__name__}: {exc}"}
    return {mid: r["verdict"] for mid, r in res.items()
            if not mid.startswith("_") and r["verdict"] != "기대일치"}


def test_suture_removal_is_detected_by_this_battery(tmp_path):
    """M-SUTURE — 게이트 판정 줄을 `if False:` 로 무력화하면 **본 배터리가 RED 가 되어야** 한다.

    site 별로 하나씩 봉합하고, 잡히지 않은 site 를 전부 열거해 실패시킨다.
    (site 하나가 안 잡히면 그 판정 경로는 dark path 다 — 미실행을 GREEN 으로 계상 금지.)
    """
    src = FX.engine_source()
    sites = FX.suture_sites(src)
    assert sites, (
        "M-SUTURE 주입 지점 0 — 엔진 `check_inv_*` 안에 RED 방출 `if` 판정이 없다. "
        "판정이 없는 게이트는 hollow 다."
    )

    pristine = engine()
    base_sig = _battery_signature(pristine)
    assert not _battery_mismatches(pristine), (
        "무변형 엔진에서 배터리가 이미 불일치 — M-SUTURE 판정의 전제가 성립하지 않는다"
    )

    # --- (1) §8.10 dark-path 술어 — 각 판정 site 의 조건이 참이 된 적이 있는가 ---------
    probed_path = FX.write_engine_variant(tmp_path, FX.make_probed_source(src), "probed")
    probed = FX.load_engine(probed_path, tag="probed")
    FX.run_battery(probed)
    probe = dict(getattr(probed, "_CFP_PROBE", {}))
    dark = [s for s in sites if probe.get(f"{s[0]}:{s[1]}", (0, 0))[0] == 0]
    print(f"\n[§8.10 dark-path] 판정 site {len(sites)}건 — "
          f"강제 진입 fixture 보유 {len(sites) - len(dark)} / dark {len(dark)}")
    for fn, ln in sites:
        hit, tot = probe.get(f"{fn}:{ln}", (0, 0))
        print(f"  {'DARK' if hit == 0 else ' OK '} {fn}:{ln}  참 {hit}회 / 평가 {tot}회")
    assert not dark, (                                          # ← §8.10 측정 assertion
        "강제 진입 fixture 가 없는 판정 경로(dark path)가 있다 — 미실행을 GREEN 으로 계상 금지:\n  "
        + "\n  ".join(f"{fn}:{ln}" for fn, ln in dark)
    )

    # --- (2) site 별 봉합 — 검출 / 형제 leg 에 의해 중복 커버 ---------------------------
    base_bool = _battery_signature_boolean_only(pristine)
    undetected, detected, bool_only_detected = [], [], []
    for idx, site in enumerate(sites):
        mutated_src = FX.make_sutured_source(src, target=site)
        path = FX.write_engine_variant(tmp_path, mutated_src, f"suture_{idx}")
        try:
            mut = FX.load_engine(path, tag=f"suture_{idx}")
        except Exception as exc:  # noqa: BLE001 - 로드 실패도 검출이다
            detected.append((site, f"load-failure: {type(exc).__name__}"))
            bool_only_detected.append(site)
            continue
        mism = _battery_mismatches(mut)
        if _battery_signature(mut) != base_sig or mism:
            detected.append((site, f"mismatches={list(mism)[:6]}"))
        else:
            undetected.append(site)
        if _battery_signature_boolean_only(mut) != base_bool:
            bool_only_detected.append(site)

    print(f"\n[M-SUTURE] site {len(sites)}건 — 단독 검출 {len(detected)} / 중복 커버 {len(undetected)}")
    for site, why in detected:
        print(f"  검출     {site[0]}:{site[1]}  {why}")
    for site in undetected:
        print(f"  중복커버 {site[0]}:{site[1]}  ← 형제 leg 이 같은 mutant 를 잡는다(게이트 약화 0)")

    # C-6 대조 — boolean 만 보는 종전 형태는 몇 건을 놓치는가.
    det_sites = {s for s, _w in detected}
    bool_sites = set(bool_only_detected)
    print(f"[C-6 대조] 개수·벡터 signature 검출 {len(det_sites)} vs "
          f"boolean-only signature 검출 {len(bool_sites)} "
          f"— boolean-only 가 놓치는 site {sorted(det_sites - bool_sites)}")
    # 진부분집합(`<`) — 종전 subset(`<=`) 은 두 집합이 **같아도** 통과해서, signature 를
    # boolean-only 로 되돌려도 무검출이었다. C-6 처방(개수·벡터)이 load-bearing 이라는
    # 주장은 "개수·벡터가 boolean 보다 **실제로 더 잡는다**" 로만 성립한다.
    # `<` 는 종전 취지(boolean 이 더 잡으면 signature 구성 오류)를 포함한다.
    assert bool_sites < det_sites, (                 # ← C-6 측정 assertion (개수·벡터 우위)
        "개수·벡터 signature 가 boolean-only 보다 더 잡지 못한다 — C-6 처방이 장식이 됐다 "
        f"(개수·벡터 전용 검출 {sorted(det_sites - bool_sites)} / "
        f"boolean 전용 검출 {sorted(bool_sites - det_sites)})"
    )

    # 판정 family 별 판정 — 단독 검출이 원칙이되, **기법의 정직한 한계**를 분리 기록한다.
    #   `if False:` 치환은 **조건부 판정 줄**만 무력화한다. 어떤 family 는 판정이 조건 밖
    #   무조건 `return RED` 로 떨어지므로(fallthrough) 조건 하나를 죽여도 RED-ness 가 보존된다
    #   — 이는 배터리 공백이 아니라 **변이 연산자의 사정거리 밖**이다. 그런 family 는
    #   대신 **결과 다양성**(같은 family 가 배터리에서 2개 이상 서로 다른 status 를 낸다)으로
    #   비공허성을 확정한다. 다양성이 1이면 그 family 는 사실상 상수 함수이므로 실패시킨다.
    fams = {fn for fn, _ln in sites}
    detected_fams = {fn for (fn, _ln), _w in detected}
    NAME_OF_FAMILY = {"check_inv_s1": "INV-S1", "check_inv_s2": "INV-S2",
                      "check_inv_s3": "INV-S3", "check_inv_s6": "INV-S6",
                      "check_anchor_integrity": "INV-ANCHOR", "check_scan_domain": "O5"}
    outcomes = _family_outcomes(pristine)
    undetected_fams = sorted(fams - detected_fams)
    for fam in undetected_fams:
        seen = outcomes.get(NAME_OF_FAMILY.get(fam, fam), set())
        print(f"  [fallthrough-equivalent] {fam} — 조건 봉합이 RED-ness 를 바꾸지 못함 "
              f"(무조건 return 경로 존재). 결과 다양성 = {sorted(seen)}")
        assert len(seen) >= 2, (                                # ← C-6 측정 assertion (대체 축)
            f"판정 family {fam} 은 조건 봉합으로도 안 잡히고 결과 다양성도 {sorted(seen)} 뿐이다 "
            "— 사실상 상수 판정이므로 배터리가 이 family 를 강제하지 못한다.")
    assert detected_fams, (                                     # ← C-6 측정 assertion
        "봉합 제거가 배터리에 단 한 건도 잡히지 않는다 — 배터리 무의미")

    # --- (3) 전 판정 동시 봉합 — C-6 의 실물 시나리오 (23/23 GREEN · exit 0 이었던 그것) ---
    all_src = FX.make_sutured_source(src, target=None)
    all_path = FX.write_engine_variant(tmp_path, all_src, "suture_all")
    try:
        mut_all = FX.load_engine(all_path, tag="suture_all")
    except Exception as exc:  # noqa: BLE001 - 로드 실패 = 검출
        print(f"[M-SUTURE:all] load-failure = 검출 ({type(exc).__name__})")
        return
    all_mism = _battery_mismatches(mut_all)
    print(f"[M-SUTURE:all] 전 site 무력화 시 배터리 불일치 {len(all_mism)}건: {sorted(all_mism)[:8]}")
    assert _battery_signature(mut_all) != base_sig and all_mism, (
        "전 판정 site 를 `if False:` 로 무력화했는데 배터리가 전건 GREEN 이다 — 배터리 무의미"
    )


# ---------------------------------------------------------------------------
# M-COMMENT — 실행 오라클 (기대값은 주석이 아니라 선언 파일에)
# ---------------------------------------------------------------------------

def _engine_comments(src: str):
    out = []
    for tok in tokenize.generate_tokens(StringIO(src).readline):
        if tok.type == tokenize.COMMENT:
            out.append((tok.start[0], tok.string))
    return out


def test_comment_is_not_a_load_bearing_expected_value_carrier(tmp_path):
    """M-COMMENT — 판정에 쓰이는 기대값이 주석에 살아 있으면 안 된다.

    3 leg (짝 없는 GREEN 을 통과로 계상하지 않기 위한 positive control 포함):
      A 구조 — baseline 선언 기대값이 엔진 **주석**에 중복 등장하지 않는다 (이중 원본 금지)
      B 거동 — 남은 주석을 변조해도 `run(gate, fixture)` 3-tuple 이 불변이다
      C 대조 — **선언 파일**의 같은 값을 변조하면 3-tuple 이 **변한다** (하네스 비맹목 증명)
    """
    eng = engine()
    src = FX.engine_source()
    comments = _engine_comments(src)

    # 정의역 = **판별력 있는** 선언값만. 1 자리 정수(1·9·10 등)는 산문 어디에나 나타나
    # 거짓 양성을 만들므로 제외하고, 정의역별 분해값(C-13 의 실물)에 협착한다.
    declared_values = {v for v in FX.CORPUS_EXPECTED.values() if "." in v}
    declared_values |= {str(v) for v in FX.DECLARED_CARDINALITY.values() if int(v) >= 13}
    declared_values |= {"104"}

    # leg A — 선언 기대값이 주석에 중복 등장하면 이중 원본(=drift 원본)이다.
    offenders = []
    for lineno, text in comments:
        for val in sorted(declared_values):
            if re.search(rf"(?<![\w.]){re.escape(val)}(?![\w.])", text):
                offenders.append(f"L{lineno}: {text.strip()[:80]} (값 {val})")
                break
    assert not offenders, (
        "판정 기대값이 엔진 주석에 살아 있다 — 기대값은 코드가 읽는 **선언 파일**에 있어야 한다 "
        "(C-13 의 직접 교훈: 정의역별 분해값이 주석에만 존재했다):\n  " + "\n  ".join(offenders)
    )

    # leg C — positive control: 선언 파일 값을 바꾸면 판정이 **반드시** 바뀐다.
    #   `run(gate, fixture)` = (rc, stdout, stderr) 3-tuple 캡처 (§8.2 M-COMMENT 실행 오라클).
    ctx = FX.split_ctx()
    clean_bl = FX.build_baseline(deferred=False)
    rc_b, out_b, err_b, _ = NT.gate_run(tmp_path / "base", ctx, eng, baseline=clean_bl)
    base_obs = (rc_b, out_b, err_b)

    mutated_bl = FX.build_baseline(deferred=False)
    mutated_bl["domains"]["CORPUS"]["expected"]["S4.KB"] = "9.85"
    rc_m, out_m, err_m, _ = NT.gate_run(tmp_path / "mut", ctx, eng, baseline=mutated_bl)
    mut_obs = (rc_m, out_m, err_m)

    assert mut_obs != base_obs, (                              # ← M-COMMENT leg C 측정
        "선언 파일의 기대값을 바꿨는데 (rc, stdout, stderr) 3-tuple 이 동일하다 — "
        "하네스가 기대값 변화를 아예 관측하지 못한다. leg A/B 의 GREEN 은 무의미해진다."
    )
    assert rc_b == eng.EXIT_PASS and rc_m == eng.EXIT_FAIL, (
        f"선언값 오염이 판정을 뒤집지 못했다 — base rc={rc_b} / mutated rc={rc_m}"
    )

    # leg B — 남은 주석(있다면) 변조는 거동 불변이어야 한다.
    if comments:
        lineno, text = comments[0]
        lines = src.splitlines(keepends=True)
        lines[lineno - 1] = lines[lineno - 1].replace(text, "# MUTATED-COMMENT-CFP2986")
        mutated_src = "".join(lines)
        assert ast.dump(ast.parse(mutated_src)) == ast.dump(ast.parse(src)), (
            "주석 변조가 실행 코드 AST 를 바꿨다 — 변조가 주석 1건에 국한되지 않았다"
        )
        path = FX.write_engine_variant(tmp_path, mutated_src, "comment_mut")
        mut_eng = FX.load_engine(path, tag="comment_mut")
        assert _battery_signature(mut_eng) == _battery_signature(eng), (
            f"주석 L{lineno} 변조가 판정을 바꿨다 — 안전장치가 주석에 기대고 있다"
        )


# ---------------------------------------------------------------------------
# M-REGISTRY / M-UNIT / M-MARGIN / M-PREEXIST 개별 규율
# ---------------------------------------------------------------------------

def test_empty_registry_emits_undetermined_not_green(tmp_path):
    """M-REGISTRY — 빈 read-declaration registry (`d = N`) ⇒ UNDETERMINED. GREEN 으로 뭉개면 결함."""
    eng = engine()
    partial = FX.build_registry({FX.READER_ROSTER[0]: ["9"]},
                                carries={FX.child_path(FX.SPLIT_ID): ["9"]})
    rc, out, err, summary = NT.gate_run(tmp_path, FX.split_ctx(), eng, registry=partial)
    assert rc != eng.EXIT_PASS, (
        f'빈 registry 에서 rc=EXIT_PASS — "절감 0"(판정)과 "판정 불가"를 같은 rc 로 뭉쳤다. '
        f"day-1 에 AC-1 이 공허 통과하고 AC-5 는 원리적으로 충족 불가가 된다."
    )
    assert rc == eng.EXIT_UNDETERMINED, f"rc={rc}, 기대 {eng.EXIT_UNDETERMINED}. stderr={err[:300]}"
    assert "deferred=" in out, f"§7.4a O5 `deferred=` 필드 부재 — stdout={out[:300]}"


def test_m_unit_is_equivalent_mutant_on_flat_fixture():
    """M-UNIT 특칙 — `FX-FLAT` 단독 실행으로 "단위를 검증했다" 고 선언하는 것을 금지한다."""
    eng = engine()
    flat, split = FX.fx_flat(), FX.fx_split()

    # FX-FLAT: read_cost 와 자식포함총합이 단조 배수 ⇒ 순위·판정이 안 바뀐다 (등가 mutant).
    assert FX.engine_read_cost(eng, flat) == 8 * FX.total_including_children(flat)
    # FX-SPLIT: 관계가 깨진다 ⇒ 술어 치환이 판정을 바꾼다 (판별력 O).
    assert FX.engine_read_cost(eng, split) != 8 * FX.total_including_children(split)
    assert FX.engine_read_cost(eng, split) - FX.total_including_children(split) == 7000


def test_margin_requires_paired_positive_control():
    """M-MARGIN — GREEN 기대라 단독 검출력 0. 같은 실행 안 RED-기대 mutant 와 **쌍으로만** 판정."""
    results = FX.run_battery(engine())
    margin = results["M-MARGIN"]
    paired = results["M-E4"]

    assert paired["injected_red_count"] > 0, (
        "짝(M-E4)의 RED 가 없다 — M-MARGIN 은 **판정 불가**로 기록해야 하며 GREEN 으로 계상 금지"
    )
    assert margin["injected_red_count"] == 0, (
        f"M-MARGIN 이 false RED — 구간 내부 무관 삽입은 GREEN 유지여야 한다 "
        f"(실측 RED {margin['injected_red_count']}, 벡터 {margin['vector']})"
    )
    assert margin["verdict"] == "기대일치"


def test_judgment_surface_is_baseline_not_diff():
    """M-PREEXIST — 선행 오염은 차분면에서 **영구 무장해제**된다. 판정면 = baseline artifact."""
    eng = engine()
    results = FX.run_battery(eng)
    r = results["M-PREEXIST"]

    assert r["injected_red_count"] >= 1, (
        "PR2(정상 편집, 오염 잔존)에서 baseline 면이 RED 를 유지하지 못했다 — "
        "판정면 선택이 강제되지 않는다"
    )
    assert "GREEN" in (r.get("note") or ""), (
        f"차분면이 PR2 에서 GREEN 이 아니면 판정면 선택의 load-bearing 이 실증되지 않는다 "
        f"— note={r.get('note')}"
    )


# ---------------------------------------------------------------------------
# 자문 3방향 전건 — 제거 / 주입 / 표기 등가변형
# ---------------------------------------------------------------------------

def test_three_advisory_axes_all_executed():
    """자문 3방향 전건 이행 — ① 제거 ② 주입 ③ 표기 등가변형. ③ 이 반복 누출됐다."""
    results = FX.run_battery(engine())

    # ① 제거 축 — span_anchor 느슨화(M-ANCHOR-LOOSE). 정의역별로 갈린다 (과대 선언 금지).
    loose = results["M-ANCHOR-LOOSE"]
    assert loose["control"] == "GREEN" and loose["injected_red_count"] == 3
    assert loose["vector"] == ["CORPUS:leg1", "CORPUS:leg2", "CORPUS:leg3"], (
        f"제거 축 — CORPUS 에서만 RED 여야 한다(§5.3 은 표가 하나뿐이라 앵커가 vacuous). "
        f"실측 {loose['vector']}"
    )

    # ② 주입 축 — M-FENCE-INJECT R4 재구성본. 대조군 GREEN ∧ 주입 RED 로 admission rule 충족.
    fence = results["M-FENCE-INJECT"]
    matrix = fence["fence_matrix"]
    assert matrix["fence_aware=False,inject=False"] == "GREEN", (
        "주입 축 대조군이 이미 RED = 등가 mutant (R4 F-2 가 정확히 이것을 무효 판정했다)"
    )
    assert matrix["fence_aware=False,inject=True"] == "RED"
    assert matrix["fence_aware=True,inject=False"] == "GREEN"
    assert matrix["fence_aware=True,inject=True"] == "GREEN", (
        f"fence_aware:true 에서도 주입이 RED 면 fence-aware 가 작동하지 않는다 — {matrix}"
    )

    # ③ 표기 등가변형 축 — GREEN 유지. 실행 커버 2 계열에 **한정** 선언한다 (§8.12 축 B-3).
    equiv = results["M-EQUIV"]
    assert equiv["injected_red_count"] == 0, (
        f"표기 등가변형(RTM 헤더 공백 · §5.3 셀 padding)이 false RED — 실측 {equiv['vector']}"
    )


# ---------------------------------------------------------------------------
# INV-S1 3-leg 분해 축 (CP §8.2 신설 6종) — 양성 4 ∧ 대조군 2
# ---------------------------------------------------------------------------

# CP §8.2 표 + 설계 firsthand 실측치를 실행 가능한 기대값으로 고정한다.
#   {mutant: (소실 줄수, 신규 줄수, 기대 RED 벡터)}
LOSS_AXIS_EXPECTED = {
    "M-LOSS-LINE":      (1, 0, ["9:A"]),
    "M-LOSS-MUTATE":    (3, 3, ["9:A"]),
    "M-LOSS-NOTATION":  (2, 5, ["9:A"]),   # 3건 주입 중 1건 다중도 흡수 (CP §8.2 = 소실 2)
    "M-LOSS-MASK":      (1, 2000, ["9:A"]),
    "M-SPLIT-GROW-CTL": (0, 160, []),
    "M-MIDSPLIT-CTL":   (0, 0, []),
}
LOSS_AXIS_CTX = {
    "M-LOSS-LINE": FX.ctx_loss_line,
    "M-LOSS-MUTATE": FX.ctx_loss_mutate,
    "M-LOSS-NOTATION": FX.ctx_loss_notation,
    "M-LOSS-MASK": FX.ctx_loss_mask,
    "M-SPLIT-GROW-CTL": FX.ctx_split_grow_ctl,
    "M-MIDSPLIT-CTL": FX.ctx_midsplit_ctl,
}


def test_inv_s1_loss_axis_positive_and_control_pair():
    """CP §8.2 신설 6종 — 양성 4(leg-A RED) ∧ 대조군 2(GREEN)를 **쌍으로** 확정한다.

    "RED 였다" 는 boolean 은 부족하다 (C-6). **소실 줄 수**가 주입량과 일치해야 그 판정이
    실제로 *그 주입을* 본 것임이 증명된다. 그래서 값을 **독립 관측면 2개**로 잰다:
      · 관측면 ① — 엔진 원시 함수 재계산 (`reassemble` → `s1_lines` → `_multiset_diff`)
      · 관측면 ② — `check_inv_s1` verdict detail 이 **선언한** 수치
    둘이 어긋나면 어느 한쪽이 틀린 것이므로 그 불일치 자체를 실패로 잡는다.
    """
    eng = engine()
    for mid, (want_lost, want_gained, want_vec) in LOSS_AXIS_EXPECTED.items():
        ctx = LOSS_AXIS_CTX[mid]()
        verdicts = FX.run_inv_s1(eng, ctx)
        lost, gained = FX.s1_leg_a_lost(eng, ctx, "9")

        # 관측면 ① — 원시 재계산
        assert (len(lost), len(gained)) == (want_lost, want_gained), (   # ← 값 측정 assertion
            f"{mid} §9 (소실, 신규) 실측 ({len(lost)}, {len(gained)}) != "
            f"기대 ({want_lost}, {want_gained}). construction={ctx['construction']}")

        # 관측면 ② — 엔진이 선언한 수치와 교차 검증
        assert FX.reported_lost(verdicts) == want_lost, (
            f"{mid} 엔진 선언 소실 {FX.reported_lost(verdicts)} != 재계산 {want_lost} "
            "— 두 관측면이 어긋난다")
        assert FX.reported_gained(verdicts) == want_gained, (
            f"{mid} 엔진 선언 신규 {FX.reported_gained(verdicts)} != 재계산 {want_gained}")

        # 판정 벡터 — 차단 축은 leg-A 단독이어야 한다 (leg-B/C 는 SIGNAL 이라 rc 무영향)
        assert sorted(f"{d}:{l}" for d, l in FX.red_vector(verdicts)) == want_vec, (
            f"{mid} RED 벡터 실측 {sorted(FX.red_vector(verdicts))} != 기대 {want_vec}")

    # 대조군 GREEN 이 **미발화·미호출의 GREEN 이 아님**을 같은 실행에서 증명한다.
    #   M-SPLIT-GROW-CTL — 정의역 안 성장이 leg-B SIGNAL 로 실제 관측된 채 leg-A 는 PASS
    grow = FX.run_inv_s1(eng, FX.ctx_split_grow_ctl())
    assert any(v.status == "SIGNAL" and v.domain == "9" and v.leg == "B" for v in grow), (
        f"대조군 성장이 관측되지 않았다 — GREEN 이 공허하다. {FX.status_vector(grow)}")
    #   M-MIDSPLIT-CTL — 기각안(prefix·부분수열 술어) 반례. 순서는 뒤집히되 차단되지 않는다.
    mid_v = FX.run_inv_s1(eng, FX.ctx_midsplit_ctl())
    assert any(v.status == "SIGNAL" and v.domain == "9" and v.leg == "C" for v in mid_v), (
        f"절-중간 분할인데 leg-C 순서 SIGNAL 이 없다 — 기각안 반례가 성립하지 않는다. "
        f"{FX.status_vector(mid_v)}")
    assert FX.red_count(mid_v) == 0, (
        "순서를 차단 축에 두었다면 이 정상 이동이 false RED 였다 — leg-C 는 비차단이어야 한다")


def test_loss_axis_three_advisory_directions():
    """손실 축 3방향 자문 — ① 제거 ② 주입 ③ 표기 등가변형. 셋 다 **실행**으로 이행한다.

    ③ 이 반복 누출됐다. 여기서는 표기 등가변형(선행 공백 2칸)이 leg-A RED 라는 것과,
    그 판정에서 **1건이 흡수되는 원인이 표기가 아니라 다중도**라는 것까지 반증한다.
    """
    eng = engine()

    # ① 제거 축 — 자식 본문에서 1줄 삭제 ⇒ leg-A RED (소실 1)
    rm = FX.run_inv_s1(eng, FX.ctx_loss_line())
    assert FX.red_count(rm) == 1 and FX.reported_lost(rm) == 1

    # ② 주입 축 — 자식 본문에 정상 저작 append ⇒ leg-A PASS ∧ leg-B SIGNAL (GREEN)
    inj = FX.run_inv_s1(eng, FX.ctx_split_grow_ctl())
    assert FX.red_count(inj) == 0 and FX.reported_gained(inj) == FX.SPLIT_GROW_NEW_LINES

    # ②' 위장 주입 — 삭제 1 + 대량 append. **성장은 손실을 덮지 못한다.**
    mask = FX.run_inv_s1(eng, FX.ctx_loss_mask())
    assert FX.red_count(mask) == 1, (
        f"신규 {FX.reported_gained(mask)}줄이 소실 1줄을 덮어버렸다 — 두 축이 분리되지 않았다")
    assert FX.reported_lost(mask) == 1 and FX.reported_gained(mask) == FX.LOSS_MASK_NEW_LINES

    # ③ 표기 등가변형 축 — 선행 공백 2칸. `INV_S1_CANON = trailing_newline_only` 이므로
    #    들여쓰기는 정규화되지 않고 **원 줄 소실**로 계상된다 (설계 의도, CP §8.2 = RED).
    notation = FX.run_inv_s1(eng, FX.ctx_loss_notation(inject=True))
    assert FX.red_count(notation) == 1 and FX.reported_lost(notation) == 2

    #    ③-a 무주입 대조군 — 같은 형상(성장 동반)에서 주입만 빼면 GREEN
    ctl = FX.run_inv_s1(eng, FX.ctx_loss_notation(inject=False))
    assert FX.red_count(ctl) == 0 and FX.reported_lost(ctl) == 0, (
        f"표기 등가변형 대조군이 이미 RED = 등가 mutant. {FX.status_vector(ctl)}")

    #    ③-b 흡수 원인 반증 — 주입 3건인데 소실이 2인 이유가 **표기** 때문이라면,
    #        성장을 빼도 여전히 2 여야 한다. 실제로는 3 이 된다 ⇒ 원인은 **다중도**다.
    lost_grow, _g = FX.s1_leg_a_lost(eng, FX.ctx_loss_notation(inject=True, growth=True), "9")
    lost_flat, _g2 = FX.s1_leg_a_lost(eng, FX.ctx_loss_notation(inject=True, growth=False), "9")
    assert (len(lost_grow), len(lost_flat)) == (2, 3), (   # ← 흡수 귀속 측정 assertion
        f"흡수 귀속 반증 실패 — 성장 동반 소실 {len(lost_grow)} / 성장 없음 소실 {len(lost_flat)}, "
        f"기대 (2, 3)")
    assert FX.NOTATION_BOILER in lost_flat and FX.NOTATION_BOILER not in lost_grow, (
        f"흡수된 줄이 고다중도 boilerplate `{FX.NOTATION_BOILER}` 가 아니다 — "
        f"성장 동반 소실 목록 {lost_grow} / 성장 없음 {lost_flat}")


# ---------------------------------------------------------------------------
# 미닫힌 fence 축 (INV-ANCHOR) — 양성 3 ∧ 음성 2, 3방향 자문
# ---------------------------------------------------------------------------

# 주입 위치별 **구조 판별자** — (가시 앵커, 부모 섹션 수, 부모 EOF 미닫힘, 자식 §9 EOF 미닫힘).
#   "셋 다 RED" 만 보면 셋이 **같은 이유로** RED 여도 통과한다(축이 하나뿐인데 셋으로 보이는
#   상태). 붕괴 시작점이 실제로 다르다는 것을 이 벡터가 값으로 고정한다.
FENCE_AXIS_EXPECTED = {
    "M-FENCE-UNCLOSED-CHILD":     (4, 11, False, True),
    "M-FENCE-UNCLOSED-PARENT":    (2,  9, True,  False),
    "M-FENCE-UNCLOSED-OUTDOMAIN": (0,  7, True,  False),
}
FENCE_AXIS_CTX = {
    "M-FENCE-UNCLOSED-CHILD": FX.ctx_fence_unclosed_child,
    "M-FENCE-UNCLOSED-PARENT": FX.ctx_fence_unclosed_parent,
    "M-FENCE-UNCLOSED-OUTDOMAIN": FX.ctx_fence_unclosed_outdomain,
}


def test_fence_unclosed_axis_positive_and_negative_pair():
    """미닫힌 fence 축 — 양성 3(RED) ∧ 음성 2(GREEN)를 **쌍으로** 확정한다.

    음성 2 = 닫힌 fence(M-E3) + 무주입 `split_ctx`. 신설하지 않고 재사용한다.
    양성 3 은 주입 **위치**가 달라야 축이 셋이므로, 구조 판별자 벡터까지 값으로 잰다.
    """
    eng = engine()

    # 음성 2 — 이 둘이 GREEN 이어야 양성 RED 가 '아무거나 다 RED' 가 아님이 성립한다.
    base = FX.split_ctx()
    assert FX.red_count(FX.run_anchor(eng, base)) == 0, "무주입 대조군이 이미 RED = 등가 mutant"
    e3 = FX.run_anchor(eng, FX.ctx_e3_fence_phantom())
    assert FX.red_count(e3) == 0, (                       # ← 음성 대조군 측정 assertion
        f"**닫힌** fence 가 앵커 축에서 RED — 미닫힘이 아니라 펜스 존재 자체를 잡고 있다. "
        f"{FX.status_vector(e3)}")
    assert not eng.fence_unclosed_at_eof(
        FX.ctx_e3_fence_phantom()["children"][FX.child_path(FX.SPLIT_ID)]), (
        "M-E3 자식이 EOF 미닫힘이면 음성 대조군 자격이 없다")
    assert len(eng.parse_anchors(base["story_after"])) == 4, "무주입 정본 가시 앵커가 4 가 아니다"

    # 양성 3 — RED 1건씩 ∧ 붕괴 시작점이 서로 다름
    for mid, (want_vis, want_secs, want_p, want_c) in FENCE_AXIS_EXPECTED.items():
        ctx = FENCE_AXIS_CTX[mid]()
        story, child9 = ctx["story_after"], ctx["children"][FX.child_path(FX.SPLIT_ID)]
        verdicts = FX.run_anchor(eng, ctx)

        assert FX.red_count(verdicts) == 1, (             # ← 양성 측정 assertion
            f"{mid} RED {FX.red_count(verdicts)}건 (기대 1) — EOF 미닫힘 leg 은 1건 방출 후 "
            f"즉시 return 해야 한다. {FX.status_vector(verdicts)}")
        got = (len(eng.parse_anchors(story)), len(eng.split_sections(story)),
               eng.fence_unclosed_at_eof(story), eng.fence_unclosed_at_eof(child9))
        assert got == (want_vis, want_secs, want_p, want_c), (   # ← 축 분리 측정 assertion
            f"{mid} 구조 판별자 실측 {got} != 기대 "
            f"{(want_vis, want_secs, want_p, want_c)} — 주입 위치가 설계와 다르다. "
            f"construction={ctx['construction']}")

        # ★ "앵커 0건 = 앵커 없음" 이 아니라 **파싱 붕괴**임을 같은 문서로 반증한다.
        #   fence-aware 를 끄면 가려졌던 앵커가 4건 그대로 나온다 ⇒ 실재하는데 안 보였을 뿐.
        assert len(eng.parse_anchors(story, False)) == 4, (
            f"{mid} — fence-aware 를 꺼도 앵커가 4건이 아니다. 마스킹이 아니라 문서 자체가 "
            f"달라졌다는 뜻이므로 이 fixture 는 미닫힘 축을 재지 않는다")

    # 붕괴 시작점 3종이 실제로 **서로 다른 형상**인지 (동형 3종 방지)
    shapes = {mid: FENCE_AXIS_EXPECTED[mid] for mid in FENCE_AXIS_EXPECTED}
    assert len(set(shapes.values())) == 3, f"주입 위치 3종이 동형이다 — 축이 하나뿐: {shapes}"


def test_fence_unclosed_axis_three_advisory_directions():
    """미닫힌 fence 축 3방향 자문 — ① 제거 ② 주입 ③ 표기 등가변형. 셋 다 **실행**으로 이행한다.

    ① 제거를 두 채널로 각각 이행한다. 한 채널만으로는 "이 RED 가 정확히 그 leg 때문" 이라는
       귀속이 서지 않는다.
         (a) `fence_aware=False` — 엔진 내장 우회 스위치. leg 의 `and` 앞항을 끈다.
         (b) site 봉합 — `check_anchor_integrity` 안 RED 판정 site 를 하나씩 `if False:` 로
             죽여, **EOF 미닫힘 site 하나만** 3종을 GREEN 으로 되돌린다는 것까지 본다
             (형제 site 를 죽여도 GREEN 이 되면 귀속이 틀린 것이다).
    ★ (a) 는 진단용 스위치이지 안전 모드가 아니다 — 끄면 판정만 사라지고 실제 파싱 붕괴
       위험은 그대로다. 여기서는 "무엇이 RED 를 만들었는가" 의 귀속에만 쓴다.
    """
    eng = engine()

    def anchor_with(engine_mod, ctx, fence_aware=True):
        out = list(engine_mod.check_anchor_integrity(
            ctx["story_after"], label=FX.STORY_PATH, fence_aware=fence_aware))
        for path in sorted(ctx["children"]):
            out.extend(engine_mod.check_anchor_integrity(
                ctx["children"][path], label=path, fence_aware=fence_aware))
        return out

    # ② 주입 축 — 봉합 상태에서 3종 RED (양성)
    for mid, ctx_fn in FENCE_AXIS_CTX.items():
        assert FX.red_count(anchor_with(eng, ctx_fn())) == 1, f"{mid} 주입이 RED 가 아니다"

    # ① 제거 채널 (a) — fence-aware 를 끄면 3종이 GREEN 으로 **돌아와야** 한다.
    for mid, ctx_fn in FENCE_AXIS_CTX.items():
        off = anchor_with(eng, ctx_fn(), fence_aware=False)
        assert FX.red_count(off) == 0, (                  # ← 제거 축 측정 assertion
            f"{mid} — fence-aware 를 껐는데도 RED. 이 RED 의 원인이 EOF 미닫힘 leg 이 아니라 "
            f"형제 앵커 규칙(미쌍·중복·오형식)이라는 뜻이다. {FX.status_vector(off)}")

    # ③ 표기 등가변형 축 — 펜스 표기를 바꿔도 판정이 유지되는가.
    #    `~~~` / 4-backtick / 언어태그 유무 / 들여쓰기 — 표기를 갈아끼우면 빠져나가는 게이트를 배제.
    for label, fence in (
        ("tilde ~~~", "~~~text\n미닫힌 tilde 펜스.\n"),
        ("4-backtick", "````\n미닫힌 4-backtick 펜스.\n"),
        ("언어태그 없음", "```\n미닫힌 무태그 펜스.\n"),
        ("언어태그 bash", "```bash\necho 미닫힌 bash 펜스\n"),
        ("들여쓴 펜스", "   ```yaml\n   미닫힌 들여쓴 펜스.\n"),
    ):
        for mid, ctx_fn in FENCE_AXIS_CTX.items():
            ctx = _refence(ctx_fn(), fence)
            assert FX.red_count(FX.run_anchor(eng, ctx)) == 1, (  # ← 등가변형 측정 assertion
                f"{mid} / {label} — 펜스 표기를 바꾸자 판정이 사라졌다. 표기만 갈아끼우면 "
                f"통과하는 게이트다")


def _refence(ctx, fence: str):
    """fixture 의 정본 펜스 표기를 등가 표기로 치환한다 (주입 **위치**는 보존)."""
    story = ctx["story_after"].replace(FX.UNCLOSED_FENCE, fence, 1)
    kids = {p: t.replace(FX.UNCLOSED_FENCE, fence, 1) for p, t in ctx["children"].items()}
    changed = (story != ctx["story_after"]) or any(
        kids[p] != ctx["children"][p] for p in kids)
    if not changed:                       # 무음 no-op 치환 = 등가변형을 안 잰 것과 같다
        raise AssertionError("정본 펜스 리터럴을 찾지 못해 표기 치환이 no-op 이 됐다")
    return ctx.copy_with(story_after=story, children=kids)


def test_fence_unclosed_removal_is_attributable_to_the_eof_leg(tmp_path):
    """① 제거 채널 (b) — **어느 site 를 죽였을 때** 3종이 GREEN 으로 돌아오는가.

    `check_anchor_integrity` 안 RED 판정 site 를 하나씩 봉합한다. 3종을 전부 GREEN 으로
    되돌리는 site 가 **정확히 하나**여야 귀속이 선다. 여러 site 가 그렇다면 판정이 중복
    경로에 얹혀 있다는 뜻이고, 하나도 없다면 이 RED 는 봉합 대상 밖에서 나온 것이다.
    """
    src = FX.engine_source()
    sites = [s for s in FX.suture_sites(src) if s[0] == "check_anchor_integrity"]
    assert len(sites) >= 2, f"`check_anchor_integrity` 판정 site 가 {len(sites)}건 — 대조 불가"

    killers = []
    for idx, site in enumerate(sites):
        path = FX.write_engine_variant(
            tmp_path, FX.make_sutured_source(src, target=site), f"anchor_suture_{idx}")
        mut = FX.load_engine(path, tag=f"anchor_suture_{idx}")
        reds = {mid: FX.red_count(FX.run_anchor(mut, fn()))
                for mid, fn in FENCE_AXIS_CTX.items()}
        print(f"  suture {site[0]}:{site[1]} -> 미닫힘 3종 red={reds}")
        if all(v == 0 for v in reds.values()):
            killers.append(site)

    assert len(killers) == 1, (                           # ← 귀속 측정 assertion
        f"3종을 전부 GREEN 으로 되돌리는 site 가 {len(killers)}건 (기대 1) — {killers}. "
        "0 이면 이 RED 의 원인이 봉합 대상 밖이고, 2+ 면 판정이 중복 경로에 얹혀 있다.")


def test_before_ref_children_are_resolved_separately():
    """`children_before` 는 장식이 아니다 — 양성 ∧ 음성 쌍으로 load-bearing 을 반증한다.

    before-ref 에도 §9 앵커가 있는 형상(재분할)에서만 이 인자가 판정에 들어간다.
      · 음성(종전 경로, `children_before=None`) — 양변을 **같은 (손실된) 자식**으로 재조립
        하므로 손실이 상쇄돼 digest 동일 ⇒ fast-path PASS. leg-A 가 **정확히 공허**해진다.
      · 양성(선언) — L 이 before 의 실제 내용이 되어 소실이 드러난다.
    이 쌍이 없으면 "자식을 각 ref 에서 따로 해결한다" 는 배선이 미호출이어도 아무도 모른다.
    """
    eng = engine()
    n_lost = 2
    ctx, victims = FX.ctx_resplit_child_loss(n_lost)
    assert len(victims) == n_lost

    # 전제 — 재분할이라 anchor_delta 가 §9 를 포함하고 **양쪽에** 앵커가 있다.
    delta = eng.anchor_delta(ctx["story_before"], ctx["story_after"])
    assert "9" in eng.sections_of(delta), f"재분할 fixture 가 §9 를 발화시키지 못한다 — {delta}"
    b_sec = eng.split_sections(ctx["story_before"])["9"]
    a_sec = eng.split_sections(ctx["story_after"])["9"]
    assert eng.has_split_markers(b_sec) and eng.has_split_markers(a_sec), (
        "before/after 양쪽에 앵커가 있어야 before-ref 자식이 판정에 들어간다")

    kids_after = FX.children_by_section(eng, ctx)
    kids_before = FX.children_before_by_section(eng, ctx)
    assert kids_before is not None, "fixture 가 children_before 를 선언하지 않았다"

    # 음성 — 종전 경로(4번째 인자 None)는 손실을 통째로 놓친다.
    legacy = eng.check_inv_s1(ctx["story_before"], ctx["story_after"], kids_after, None)
    assert FX.red_count(legacy) == 0, (
        f"음성 대조가 성립하지 않는다 — 종전 경로가 이미 RED 면 신설 인자의 이득을 "
        f"보일 수 없다. {FX.status_vector(legacy)}")

    # 양성 — before-ref 자식을 따로 해결하면 소실 n_lost 줄이 드러난다.
    declared = FX.run_inv_s1(eng, ctx)
    assert FX.red_count(declared) == 1, (                    # ← children_before 측정 assertion
        f"before-ref 자식 분리 해결이 소실을 드러내지 못했다. {FX.status_vector(declared)}")
    assert FX.reported_lost(declared) == n_lost, (
        f"소실 실측 {FX.reported_lost(declared)} != 삭제한 {n_lost}줄")
    lost, _gained = FX.s1_leg_a_lost(eng, ctx, "9")
    assert sorted(lost) == sorted(victims), (
        f"소실로 보고된 줄이 실제 삭제한 줄과 다르다 — 실측 {lost} / 삭제 {victims}")


# ---------------------------------------------------------------------------
# §8.3 경계 조건 11행
# ---------------------------------------------------------------------------

def _pair_move(n_bytes: int, extra_append: int = 0):
    """§9 에서 n_bytes 를 §7 로 옮기고 extra_append 만큼 총량을 늘린다."""
    pad = "P" * n_bytes
    before = NT.mini_story({"9": pad + "base", "7": "x"})
    after = NT.mini_story({"9": "base", "7": "x" + pad + "q" * extra_append})
    return before, after


def test_boundary_row1_theta_move_exact_and_off_by_one():
    """§8.3 행 1 — 임계값 정확 / ±1 에서 판정이 반전한다."""
    eng = engine()
    at = FX.red_count(eng.check_inv_s2(*_pair_move(THETA), THETA, None))
    under = FX.red_count(eng.check_inv_s2(*_pair_move(THETA - 1), THETA, None))
    assert at >= 1, f"θ_move 정확({THETA} B) 이동이 RED 가 아니다"
    assert under == 0, f"θ_move−1({THETA - 1} B) 이동이 RED — 경계 반전 실패"


def test_boundary_row2_marker_absent_duplicate_unpaired_malformed():
    """§8.3 행 2 — 마커 부재·중복·미쌍·오형식 = FAIL."""
    eng = engine()
    base = FX.split_ctx()

    unpaired = base["story_after"].replace(
        f"<!-- cfp-split:end id={FX.SPLIT_ID} -->\n", "")
    dup = base["story_after"].replace(
        f"<!-- cfp-split:begin section=9 id={FX.SPLIT_ID} -->",
        f"<!-- cfp-split:begin section=9 id={FX.SPLIT_ID} -->\n"
        f"<!-- cfp-split:begin section=9 id={FX.SPLIT_ID} -->", 1)
    malformed = base["story_after"].replace(
        f"<!-- cfp-split:begin section=9 id={FX.SPLIT_ID} -->",
        "<!-- cfp-split:begin section=9 -->", 1)

    assert FX.red_count(FX.run_anchor(eng, base)) == 0, "정상 앵커 대조군이 RED"
    for label, text in (("미쌍", unpaired), ("중복", dup), ("오형식", malformed)):
        ctx = base.copy_with(story_after=text)
        red = FX.red_count(FX.run_anchor(eng, ctx))
        assert red >= 1, f"앵커 {label} 이 RED 가 아니다 (3속성 = 명시 ∧ 쌍 ∧ 유일)"


def test_boundary_row3_grandfather_registered_and_new(tmp_path):
    """§8.3 행 3 — grandfather 등재 / 미등재(신규 → DEFAULT_CEILING) 각각 정의된 경로."""
    eng = engine()
    p = NT._write_baseline(tmp_path / "b.yaml", FX.build_baseline(), eng)
    bl = eng.load_baseline(str(p))
    assert eng.ceiling_for("CFP-2986", bl) == FX.CARRIER_CEILING
    assert eng.ceiling_for("CFP-0000", bl) == FX.DEFAULT_CEILING


def test_boundary_row4_empty_file_is_deficit_not_silent_pass():
    """§8.3 행 4 — 빈 파일은 정의된 처리(결손)여야 하고 조용한 skip 이 아니다."""
    eng = engine()
    assert eng.split_sections("") == {} or eng.split_sections("") == dict()

    ctx = FX.canonical_ctx().copy_with(story_after="", cp_after="")
    verdicts = FX.run_inv_s3(eng, ctx)
    assert FX.red_count(verdicts) >= len(FX.ENFORCED_DOMAINS), (
        f"빈 파일에서 enforced 4 정의역이 모두 결손(RED)으로 드러나지 않았다 — "
        f"실측 RED {FX.red_count(verdicts)}, 벡터 {sorted(FX.red_vector(verdicts))}"
    )


def test_boundary_row5_dangling_and_self_pointer():
    """§8.3 행 5 — 자식 파일 부재(dangling) / 자기 포인터 = FAIL."""
    eng = engine()
    assert FX.red_count(FX.run_inv_s1(eng, FX.ctx_dangling())) >= 1, "dangling pointer 미검출"
    assert FX.red_count(FX.run_inv_s1(eng, FX.ctx_self_pointer())) >= 1, (
        "자기 포인터(child == parent)가 검출되지 않았다 — E-7"
    )


def test_boundary_row6_pure_append_no_split_is_green():
    """§8.3 행 6 — **분할 없는** 순수 append 대조군 (P1-5 born-broken). false RED 0.

    fixture `ctx_append_ctl`(`_story_read_surface_fixtures.py:1100`)은 before/after 를 둘 다
    `build_story()` 기본값(`split_9`/`split_10` = False, children 없음)으로 만든다 ⇒ 앵커가
    아예 없어 `anchor_delta = ∅`. 따라서 본 테스트가 실제로 재는 속성은 "**앵커 변동이 없는**
    순수 append 에서 INV-S1 미발화 ∧ INV-S2 발화 후 GREEN" 이지 "분할된 섹션에 append" 가
    아니다 (구명 `test_boundary_row6_append_into_split_section_is_green` — R5 F-CR-R5-4 개명).
    분할 커밋 ∧ 분할 섹션(§9) append 형상은 행 8
    (`test_boundary_row8_anchor_delta_with_total_growth`)이 덮는다.
    """
    eng = engine()
    ctx = FX.ctx_append_ctl(1000)
    s1 = FX.run_inv_s1(eng, ctx)
    s2 = FX.run_inv_s2(eng, ctx)
    assert FX.red_count(s1) == 0 and not any(getattr(v, "fired", False) for v in s1), (
        "순수 append 는 anchor_delta = ∅ 이라 INV-S1 이 미발화여야 한다"
    )
    assert FX.red_count(s2) == 0, f"순수 append 가 false RED: {FX.status_vector(s2)}"
    assert any(getattr(v, "fired", False) for v in s2), (
        "INV-S2 미발화를 통과로 계상 금지 — 발화 후 GREEN 이어야 한다 (R2 P1-E)"
    )


def test_boundary_row7_reverse_split_preserves_digest():
    """§8.3 행 7 — 역분할(자식 → parent 회수)은 INV-S1 발화 ∧ digest 보존 시 GREEN."""
    eng = engine()
    fwd = FX.split_ctx()
    rev = fwd.copy_with(story_before=fwd["story_after"], story_after=fwd["story_before"])
    v = FX.run_inv_s1(eng, rev)
    assert any(getattr(x, "fired", False) for x in v), "역분할에서 INV-S1 미발화"
    assert FX.red_count(v) == 0, (
        f"역분할이 무손실인데 RED — {FX.status_vector(v)}"
    )


def test_boundary_row8_anchor_delta_with_total_growth():
    """§8.3 행 8 — 앵커 델타 ∧ 총량 증가 동시 발생: INV-S1 발화(분할분만) ∧ INV-S2 미발화.

    ★ 성장은 **`sections(anchor_delta)` 안**(§9)에 주입한다. 종전 fixture 는 §7 에 넣었는데
      §7 ∉ sections(anchor_delta) = {9, 10} 이라 `red_count(s1) == 0` 이 자기 docstring
      ("분할분만 판정")에 대해 **공허**했다 — "검사 정의역 밖이라 안 걸린 것"과 "정의역
      안인데 안 걸린 것"이 같은 GREEN 으로 뭉개졌다. 아래 (a) leg-B SIGNAL assert 가 그
      공허성을 닫고, (c) 대조가 종전 배치에서는 그 SIGNAL 이 실제로 없음을 보인다.
    """
    eng = engine()
    ctx = FX.split_ctx()
    grown = FX.build_story(split_9=True, split_10=True, section_9_extra="w" * 5000)
    ctx = ctx.copy_with(story_after=grown)

    s1 = FX.run_inv_s1(eng, ctx)
    s2 = FX.run_inv_s2(eng, ctx)
    assert any(getattr(v, "fired", False) for v in s1), "INV-S1 미발화 (anchor_delta ≠ ∅)"

    # (a) 비공허 실증 — 주입한 성장이 **검사 정의역 안**에서 실제로 관측됐다.
    delta_sections = eng.sections_of(eng.anchor_delta(ctx["story_before"], ctx["story_after"]))
    assert "9" in delta_sections, f"성장 주입 섹션 §9 가 anchor_delta 밖 — {sorted(delta_sections)}"
    grown_signal = [v for v in s1 if getattr(v, "status", None) == "SIGNAL"
                    and getattr(v, "domain", None) == "9" and getattr(v, "leg", None) == "B"]
    assert grown_signal, (                                   # ← 행 8 비공허 측정 assertion
        f"§9(= anchor_delta 섹션) 안에 5,000 B 를 append 했는데 leg-B SIGNAL 이 없다 — "
        f"성장이 검사 정의역에 들어가지 않았거나 관측되지 않았다. {FX.status_vector(s1)}")
    lost, gained = FX.s1_leg_a_lost(eng, ctx, "9")
    assert (len(lost), len(gained)) == (0, 1), (
        f"§9 성장 실측 (소실, 신규) = ({len(lost)}, {len(gained)}) — 기대 (0, 1)")

    # (b) 본 명제 — 정의역 **안**의 성장인데도 차단 축(leg-A)은 PASS 다.
    assert FX.red_count(s1) == 0, (
        f"분할분 판정만 해야 하는데 §9 정상 저작까지 RED — {FX.status_vector(s1)}")

    # (c) 대조 — 같은 5,000 B 를 정의역 **밖**(§7)에 두면 SIGNAL 이 아예 사라진다.
    #     종전 fixture 가 정확히 이 상태였고, 그래서 (b) 가 공허했다.
    outside = ctx.copy_with(story_after=FX.build_story(
        split_9=True, split_10=True, section_7_extra="w" * 5000))
    s1_out = FX.run_inv_s1(eng, outside)
    assert not [v for v in s1_out if getattr(v, "status", None) == "SIGNAL"], (
        f"정의역 밖 성장에서도 SIGNAL 이 나오면 (a) 의 SIGNAL 이 §9 성장 때문임을 "
        f"증명할 수 없다 — {FX.status_vector(s1_out)}")
    assert FX.red_count(s1_out) == 0

    assert not any(getattr(v, "fired", False) for v in s2), (
        "발화 조건이 anchor_delta 로 상보 분할돼야 한다 — INV-S2 가 같이 발화했다"
    )


def test_boundary_row9_registry_coverage_extremes(tmp_path):
    """§8.3 행 9 — `d = N` / `d = 0` 양 극단이 각각 정의된 경로로 방출된다."""
    eng = engine()
    readers = list(FX.READER_ROSTER)
    fx = FX.fx_split()

    # d = N (빈 registry — 보수 default) ⇒ 절감 상한 0 이 **명시 방출**
    cost_dn = eng.read_cost(fx["parent_bytes"], fx["children"], readers, {})
    baseline_cost = 8 * fx["parent_bytes"] + 8 * 50000
    assert cost_dn == baseline_cost, f"d=N 실측 {cost_dn} != {baseline_cost}"
    assert eng.coverage(readers, {}) == 0.0

    # d = 1 (등재 완전) ⇒ 절감 발생
    assert FX.engine_read_cost(eng, fx) == 58000
    assert eng.coverage(readers, fx["registry"]) == 1.0

    partial = FX.build_registry({FX.READER_ROSTER[0]: ["9"]},
                                carries={FX.child_path(FX.SPLIT_ID): ["9"]})
    rc, _o, _e, sm = NT.gate_run(tmp_path, FX.split_ctx(), eng, registry=partial)
    assert rc == eng.EXIT_UNDETERMINED
    assert NT.verdicts_of(sm, "READ-COST", "UNDETERMINED")


def test_boundary_row10_move_with_total_growth_both_sides():
    """§8.3 행 10 — 이동 ∧ 총량 증가: append 64 B / 65 B **양측에서 동일 판정** (R2 P0-A)."""
    eng = engine()
    r64 = FX.red_count(eng.check_inv_s2(*_pair_move(THETA, 64), THETA, None))
    r65 = FX.red_count(eng.check_inv_s2(*_pair_move(THETA, 65), THETA, None))
    assert r64 >= 1 and r65 >= 1, (
        f"θ_total conjunct 가 살아 있다 — append 64 B RED {r64} / 65 B RED {r65}. "
        "종전 술어는 정확히 65 B 부터 사각으로 빠져나갔다."
    )
    assert r64 == r65


def test_boundary_row11_mixed_edit_is_signal_not_block():
    """§8.3 행 11 — 정상 혼합 편집(감소 ∧ 증가)은 발화하되 `reason_code` 로 **신호 강등**."""
    eng = engine()
    before = NT.mini_story({"9": "M" * 12000, "7": "x"})
    after = NT.mini_story({"9": "M" * 6000, "7": "x" + "N" * 9000})

    plain = eng.check_inv_s2(before, after, THETA, None)
    assert any(getattr(v, "fired", False) for v in plain), "혼합 편집이 미발화"
    assert FX.red_count(plain) >= 1, (
        "혼합 편집은 술어상 FIRED/RED 다 — false-positive 축의 실물이며 숨기지 않는다 (§8.12 축 B-1)"
    )

    degraded = eng.check_inv_s2(before, after, THETA, "AUTHORED_CONSOLIDATION")
    assert FX.red_count(degraded) == 0, (
        f"폐쇄 enum `AUTHORED_CONSOLIDATION` 선언 시 비차단 **신호**로 강등돼야 한다 — "
        f"{FX.status_vector(degraded)}"
    )
    assert any(getattr(v, "status", None) == "SIGNAL" for v in degraded), (
        "강등 결과가 SIGNAL 이 아니다 — 차단 0, 관측은 유지여야 한다"
    )

    # 폐쇄 enum 밖 자유서술은 강등되지 않는다.
    freeform = eng.check_inv_s2(before, after, THETA, "그냥 정리했음")
    assert FX.red_count(freeform) >= 1, (
        "`reason_code` 가 폐쇄 enum 이 아니면 자유서술로 무력화가 가능해진다"
    )


def _reassembled_bytes(eng, ctx, ref: str) -> int:
    """`ref` ∈ {before, after} 의 **재조립 총량**(parent ∪ children) 바이트.

    INV-S2 가 보지 **않는** 축이다 — 행 12 의 두 arm 이 서로 다른 위협을 실제로 담고 있음을
    이 값으로만 증명할 수 있다. 이것이 없으면 두 fixture 를 같은 것으로 만들어도 테스트가
    통과해버린다(내 하네스 자신의 born-broken 구멍).
    """
    if ref == "before":
        kids = FX.children_before_by_section(eng, ctx) or FX.children_by_section(eng, ctx)
        return len(eng.reassemble_document(ctx["story_before"], kids).encode("utf-8"))
    return len(eng.reassemble_document(
        ctx["story_after"], FX.children_by_section(eng, ctx)).encode("utf-8"))


def test_boundary_row12_settled_split_donor_is_invisible_yet_fired():
    """§8.3 행 12 — 분할 **정착** 후 INV-S2 는 **발화하되** 자식 쪽 donor 를 못 본다.

    3-arm 을 **한 실행**에 둔다. 단독 arm 은 배선을 닫지 못한다:
      ⓐ 양성(미분할 보상 이동 → RED)이 없으면 ⓑⓒ 의 침묵은 「사각이라 조용한 것」과
        「검사가 죽어서 조용한 것」이 구별되지 않는다. 그래서 같은 실행에 둔다.
      ⓑ 음성(분할 정착 보상 이동)은 `donors == 0` 으로 **기전을 이름으로 고정**한다.
      ⓒ 대조군(분할 정착 순수 성장)은 false RED 0 을 고정한다.

    ★ born-broken 함정 — 판정을 `red_count == 0`(GREEN)으로 적으면 **태어날 때부터 무력**하다.
      `NOT_FIRED` 도 `red_count = 0` 이므로, INV-S2 를 분할 파일에서 통째로 끄는 변형(발화
      가드를 `anchor_delta` → `has_split_markers(after_text)` 로 바꾸는, 「분할 파일은 INV-S1
      소관」이라는 흔한 오해의 코드화)에서 pristine 과 변형이 **똑같이 0** 을 낸다 [실행 확인
      — 그 변형에 대해 기존 mutant 4-field 전건 불변인 반면 ⓑⓒ 만 `fired` True → False 로
      반전]. 그래서 **`fired is True` 를 명시 assert** 한다. 행 6 이 *"미발화를 통과로 계상
      금지"* 로 세운 규율의 동일 적용이며 새 규칙이 아니다.

    종전 로스터에는 「`anchors(before) > 0` ∧ INV-S2 발화」 교차가 **공집합**이어서 이 셀이
    한 번도 실행된 적이 없었다 — 아래 (0) 이 그 교차를 채운다. 엔진은 **무변경**이다.
    """
    eng = engine()
    pos = FX.ctx_e4_compensating_move()          # ⓐ 미분할 보상 이동 (= 기존 M-E4 재사용)
    neg = FX.ctx_settled_move()                  # ⓑ 분할 정착 보상 이동
    ctl = FX.ctx_settled_grow_ctl()              # ⓒ 분할 정착 순수 성장

    v_pos, v_neg, v_ctl = (FX.run_inv_s2(eng, c) for c in (pos, neg, ctl))

    # (0) 전제 — ⓑⓒ 는 **분할 정착** 상태다(before 에도 앵커) ∧ `anchor_delta = ∅`.
    #     이 둘이 동시에 참이어야 INV-S2 가 발화한 뒤의 거동을 볼 수 있고, 종전 로스터가
    #     비워 두었던 바로 그 교차다. ⓐ 는 대조를 **분할 상태 하나로만** 가르기 위해 앵커 0.
    assert len(eng.parse_anchors(pos["story_before"])) == 0, "ⓐ 는 미분할이어야 한다"
    for label, ctx in (("ⓑ", neg), ("ⓒ", ctl)):
        n_before = len(eng.parse_anchors(ctx["story_before"]))
        assert n_before > 0, (
            f"{label} before 에 앵커가 없다 — 분할 **커밋**이지 **정착** 상태가 아니다. "
            f"이러면 종전처럼 교차가 다시 공집합이 된다 (실측 anchors(before)={n_before})")
        assert not eng.anchor_delta(ctx["story_before"], ctx["story_after"]), (
            f"{label} anchor_delta ≠ ∅ — INV-S2 가 early return 해 A-7② 셀로 새어나간다")

    # (1) ⓐ 양성 — 검사는 **살아 있다**. donor(§9)가 이름으로 보고된다.
    assert FX.s2_fired(v_pos) is True, "ⓐ INV-S2 미발화 — 양성 arm 이 성립하지 않는다"
    assert FX.red_count(v_pos) >= 1, (
        f"ⓐ 미분할 보상 이동이 RED 가 아니다 — 검사가 죽었다면 ⓑⓒ 의 침묵은 무의미하다. "
        f"{FX.status_vector(v_pos)}")
    pos_detail = " ".join(getattr(x, "detail", "") or "" for x in v_pos)
    assert "('9', '7')" in pos_detail, (
        f"ⓐ 의 donor↔taker 페어가 §9→§7 로 특정되지 않았다 — {pos_detail!r}")

    # (2) ⓑ 음성 — **발화한다.** 그런데 donor 가 0 이다. 이것이 사각의 실체다.
    assert FX.s2_fired(v_neg) is True, (                  # ← 행 12 born-broken 차단 assertion
        "ⓑ INV-S2 미발화 — `red_count == 0` 으로 적었다면 여기서 통과했을 자리다. "
        "미발화를 통과로 계상 금지 (행 6 동일 규율)")
    assert FX.red_count(v_neg) == 0, (
        f"ⓑ 가 RED — 본 셀은 **의도적 미커버**로 확정된 거동이다. RED 로 바뀌었다면 "
        f"정의역이 넓어진 것이므로 ADR-180 R6 결정의 **의식적 재결정**이 필요하다. "
        f"{FX.status_vector(v_neg)}")
    dt_neg = FX.s2_donor_taker(v_neg)
    assert dt_neg is not None, f"ⓑ 가 (donors, takers) 를 방출하지 않았다 — {FX.status_vector(v_neg)}"
    donors, takers = dt_neg
    assert donors == 0, (                                 # ← 기전을 이름으로 고정
        f"ⓑ donors={donors} — 0 이 아니면 parent-only 정의역이 아니다(자식 재조립 도입 등). "
        f"정의역이 바뀌었다면 축 B-1 false-positive 교환비(미측정)와 함께 재결정하라")
    assert takers >= 1, (
        f"ⓑ takers={takers} — taker 마저 0 이면 이동 자체가 θ_move 미만이라 본 arm 이 "
        f"**공허**하다(사각이 아니라 임계 미달을 재고 있다)")

    # (3) ⓒ 대조군 — 분할 정착 상태의 정상 저작에 false RED 0.
    assert FX.s2_fired(v_ctl) is True, "ⓒ INV-S2 미발화 — 미발화를 통과로 계상 금지"
    assert FX.red_count(v_ctl) == 0, (
        f"ⓒ 분할 정착 후 정상 성장이 false RED — {FX.status_vector(v_ctl)}")

    # (4) 비공허 실증 — ⓑⓒ 가 **서로 다른 위협**을 실제로 담고 있는가.
    #     엔진이 보지 않는 축(재조립 총량)으로만 판별된다. 이 assert 가 없으면 두 fixture 를
    #     같은 것으로 만들어도 (2)(3) 이 통과해 본 테스트가 통째로 공허해진다.
    neg_delta = _reassembled_bytes(eng, neg, "after") - _reassembled_bytes(eng, neg, "before")
    ctl_delta = _reassembled_bytes(eng, ctl, "after") - _reassembled_bytes(eng, ctl, "before")
    assert neg_delta == 0, (
        f"ⓑ 재조립 총량 Δ = {neg_delta} — 0 이어야 **순수 이동**(= M-E4 와 동일 위협)이다. "
        f"0 이 아니면 이동이 아니라 편집이라 사각의 실물이 아니다")
    assert ctl_delta > 0, (
        f"ⓒ 재조립 총량 Δ = {ctl_delta} — 양수여야 **순수 성장**이다. 0 이면 ⓑ 와 같은 "
        f"fixture 이고 대조군이 성립하지 않는다")

    # (5) 사각의 진술 — 위협이 정반대인데 엔진 판정이 **완전히 같다**.
    #     parent-only 정의역이 두 형상을 구별하지 못한다는 사실을 값으로 고정한다.
    fold = lambda v: (FX.s2_fired(v), FX.red_count(v), FX.s2_donor_taker(v),
                      tuple(sorted(getattr(x, "status", "") for x in v)))
    assert fold(v_neg) == fold(v_ctl), (
        f"ⓑⓒ 판정이 갈렸다 — parent-only 정의역이 넓어졌다는 뜻이므로 본 셀의 "
        f"「의도적 미커버」 결정을 재검토하라. ⓑ={fold(v_neg)} / ⓒ={fold(v_ctl)}")
    assert fold(v_pos) != fold(v_neg), (
        "ⓐⓑ 판정이 같다 — 분할 정착 여부가 판정을 가르지 않는다면 본 행이 재는 사각이 없다")


# ---------------------------------------------------------------------------
# §8.4a 봉합 후 검증 4항 — 배터리 자기적용
# ---------------------------------------------------------------------------

def test_post_suture_verification_four_axes():
    """§8.4a — ① 지정 mutant RED ② 형제 회귀 0 ③ 검출 정의역 비축소(2축) ④ 무변경 정본 GREEN."""
    eng = engine()
    results = FX.run_battery(eng)

    # ① 지정 mutant RED
    #    FIX Iter 14 — INV-S1 3-leg 분해 축의 **양성 4종**(leg-A 손실)을 추가 등재.
    #    M-E3 는 여기서 **빠졌다**: pure-append 라 손실 축에서 M-SPLIT-GROW-CTL 과 동형이고,
    #    종전 RED 는 whole-digest 술어의 무특이성 산물(= 검출 특이성 0)이었다. 판정 문면
    #    SSOT = `_story_read_surface_fixtures.run_battery` 의 M-E3 블록 주석(축 분리 확정).
    #    이어서 미닫힌 fence 축의 **양성 3종**을 추가 등재한다 — M-E3 가 담당하지 **않는**
    #    실 파서 위협(EOF 미닫힘)이 그 3종이다.
    must_red = ["M-CARD-IN", "M-CARD-VALUE", "M-CARD-CROSS", "M-S3-NOSPLIT", "M-DUP-ROW",
                "M-SEC5", "M-ANCHOR-LOOSE", "M-GLOBALRULE", "M-DOMAIN",
                "M-PREEXIST", "M-E1", "M-E2", "M-E4", "M-MIX-min",
                "M-DEPTH2", "M-DANGLING",
                "M-ANCHOR-MALFORMED", "M-ANCHOR-UNPAIRED", "M-ANCHOR-DUP", "M-SELFPTR",
                # 앵커 dark-site 판별자 2종 — 각 방출 site 를 단독 통제한다.
                "M-ANCHOR-NOID-BOTH", "M-ANCHOR-ORPHAN-END",
                "M-LOSS-LINE", "M-LOSS-MUTATE", "M-LOSS-NOTATION", "M-LOSS-MASK",
                "M-FENCE-UNCLOSED-CHILD", "M-FENCE-UNCLOSED-PARENT",
                "M-FENCE-UNCLOSED-OUTDOMAIN"]
    not_red = [m for m in must_red if results[m]["injected_red_count"] == 0]
    assert not not_red, f"① 지정 mutant 중 RED 미달: {not_red}"

    # ② 형제 회귀 0 — GREEN 기대 mutant 는 RED 로 넘어가지 않는다
    #    FIX Iter 14 — 대조군 2종(M-SPLIT-GROW-CTL / M-MIDSPLIT-CTL) + M-E3(실측 재등재) 추가.
    #    M-E3 는 미닫힘 축 양성 3종의 **음성 대조군**이기도 하다 (닫힌 fence = 무해).
    must_green = ["M-EQUIV", "M-MARGIN", "M-APPEND-CTL-1000", "M-APPEND-CTL-50000",
                  "M-BASIS-RAW", "M-SPLIT-GROW-CTL", "M-MIDSPLIT-CTL", "M-E3",
                  "M-SETTLED-MOVE", "M-SETTLED-GROW-CTL"]
    regressed = [m for m in must_green if results[m]["injected_red_count"] != 0]
    assert not regressed, f"② 형제 회귀 발생(false RED): {regressed}"

    # ①②의 **쌍 요건** — 양성만/음성만으로는 배선이 닫히지 않는다.
    #    양성 단독: 배선을 비공백 상수로 바꾸면 검사 미호출인데 대조군이 통과한다.
    #    음성 단독: 확대(성장) 방향에 무력하다.
    loss_axis_pos = {"M-LOSS-LINE", "M-LOSS-MUTATE", "M-LOSS-NOTATION", "M-LOSS-MASK"}
    loss_axis_ctl = {"M-SPLIT-GROW-CTL", "M-MIDSPLIT-CTL"}
    assert loss_axis_pos <= set(must_red) and loss_axis_ctl <= set(must_green), (
        "INV-S1 손실 축의 양성 ∧ 음성 쌍 중 한쪽만 등재됐다 — 배선이 닫히지 않는다")

    #    미닫힌 fence 축도 같은 쌍 요건을 진다. 음성은 **신설하지 않았다**:
    #    닫힌 fence(M-E3) + 무주입 대조군(`control` 열)이 그 자리다 — 양성 3 ∧ 음성 2.
    fence_axis_pos = {"M-FENCE-UNCLOSED-CHILD", "M-FENCE-UNCLOSED-PARENT",
                      "M-FENCE-UNCLOSED-OUTDOMAIN"}
    assert fence_axis_pos <= set(must_red) and "M-E3" in must_green, (
        "미닫힌 fence 축의 양성 ∧ 음성 쌍 중 한쪽만 등재됐다 — 배선이 닫히지 않는다")

    #    §8.3 행 12(분할 정착 후 INV-S2)도 같은 쌍 요건을 진다. 양성은 **신설하지 않았다**:
    #    M-E4(미분할 보상 이동, must_red)가 그 자리를 겸한다 — 양성 1 ∧ 음성 2.
    #    ★ 정직 고지: 이 세 레코드는 전부 `red_count` 축이라, INV-S2 를 분할 파일에서 끄는
    #      변형을 **이 축만으로는 못 잡는다**(음성 2종이 NOT_FIRED 로 바뀌어도 0 은 0).
    #      그 변형을 잡는 유일한 측정면은 `test_boundary_row12_*` 의 `fired is True` 다.
    settled_axis_ctl = {"M-SETTLED-MOVE", "M-SETTLED-GROW-CTL"}
    assert settled_axis_ctl <= set(must_green) and "M-E4" in must_red, (
        "분할 정착 축(§8.3 행 12)의 양성 ∧ 음성 쌍 중 한쪽만 등재됐다 — 배선이 닫히지 않는다")

    for mid in loss_axis_pos | loss_axis_ctl | fence_axis_pos | settled_axis_ctl | {"M-E3"}:
        assert results[mid]["control"] == "GREEN", (
            f"{mid} 대조군이 이미 RED — 등가 mutant (admission rule 위반)")

    # ③ 검출 정의역 비축소 — 두 축 모두
    #    (a) mutant 로스터 축: 배터리가 산출하는 mutant 전건이 선언 로스터와 일치.
    #        ①은 "등재된 mutant 가 RED 인가"만 본다. 등록 줄 자체를 지우면 ①은 전건 통과한 채
    #        로스터만 조용히 줄어든다 — 그 회피 경로를 막는 것이 이 축이다.
    roster = {m for m in results if not m.startswith("_")}
    assert roster == FX.DECLARED_MUTANT_IDS, (       # ← §8.4a ③ (a) 측정 assertion
        f"③ mutant 로스터 축 붕괴 — 누락 {sorted(FX.DECLARED_MUTANT_IDS - roster)} / "
        f"초과 {sorted(roster - FX.DECLARED_MUTANT_IDS)}"
    )
    #    (b) 정의역 로스터 축: enforced 4/4 추출 성립 (하나라도 0 이면 정의역 붕괴)
    ctx = FX.canonical_ctx()
    resolve = FX.resolve_file_factory(eng, ctx)
    extracted = {}
    for name in FX.ENFORCED_DOMAINS:
        dom = ctx["baseline"]["domains"][name]
        extracted[name] = len(eng.extract_domain(dom, resolve(dom)))
    assert extracted == FX.DECLARED_CARDINALITY, (   # ← §8.4a ③ (b) 측정 assertion
        f"③ 정의역 로스터 축 붕괴 — 실측 {extracted} 기대 {FX.DECLARED_CARDINALITY}"
    )

    # ④ 무변경 정본 GREEN (최소 통과선) — 전 불변식 동시 적용
    assert FX.red_count(FX.run_inv_s1(eng, ctx)) == 0
    assert FX.red_count(FX.run_inv_s2(eng, ctx)) == 0
    assert FX.red_count(FX.run_inv_s3(eng, ctx)) == 0
    assert FX.red_count(FX.run_inv_s6(eng, ctx)) == 0


def test_evidence_records_carry_construction_field():
    """C-28 — 각 mutant 결과 레코드는 5-tuple {값, 트리 SHA, 매체, 정의역, construction} 이다.

    construction 부재로 설계리뷰 최종 라운드에서 peer 2명이 임의 줄정렬 suffix 를 못 보고 오판했다.
    """
    results = FX.run_battery(engine())
    report = FX.format_report(results)
    print(report)

    for mid, r in results.items():
        if mid.startswith("_"):
            continue
        for key in ("control_red_count", "injected_red_count", "tree_sha",
                    "media", "domain", "construction"):
            assert key in r, f"{mid} 레코드에 `{key}` 필드 부재"
        assert r["media"] == "LF", f"{mid} 매체가 LF 가 아니다 — {r['media']}"
        assert r["construction"] and len(r["construction"]) >= 20, (
            f"{mid} construction 필드가 비었거나 너무 짧다 — "
            f"'어느 바이트 구간을 어떻게 구성했는가' 가 기술돼야 한다: {r['construction']!r}"
        )
        assert r["tree_sha"], f"{mid} 기준 트리 SHA 부재"
    assert "construction:" in report


# ---------------------------------------------------------------------------
# 매체 규약 — fixture **전수** sweep (커버리지 ∧ 양성 ∧ 음성)
# ---------------------------------------------------------------------------

# 무인자로 부를 수 없는 fixture 의 대표 인자. 여기 없는 인자-필요 fixture 는 **조용히
# 건너뛰지 않고** 아래 커버리지 assert 에서 RED 가 된다 (미호출을 GREEN 으로 계상 금지).
_FIXTURE_ARGS = {
    "build_child": [(("9", FX.SPLIT_ID, FX.SECTION_9_BODY), {})],
    "ctx_append_ctl": [((1000,), {})],
    "ctx_fence": [((), {"fence_aware": aware, "inject": inject})
                  for aware in (False, True) for inject in (False, True)],
}


def _fixture_names():
    """정의역 = `dir(FX)` 의 `build_`/`ctx_` 접두 callable **전건** — 동적 산출.

    고정 목록을 하드코딩하지 않는다. 목록을 적어두면 그 목록이 곧 검사에서 빠지는 통로가
    되고(이 Story 의 반복 교훈: 열거를 정본으로 두지 말고 **재현 규칙**을 정본으로),
    fixture 가 늘 때 정의역이 따라 늘지 않는다.
    """
    return sorted(n for n in dir(FX)
                  if (n.startswith("build_") or n.startswith("ctx_"))
                  and callable(getattr(FX, n)))


def _required_params(fn):
    sig = inspect.signature(fn)
    return [p for p in sig.parameters.values()
            if p.default is p.empty
            and p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD, p.KEYWORD_ONLY)]


def _iter_texts(obj, path):
    """fixture 반환값을 재귀 순회해 (경로, 문자열) 을 방출한다.

    str / dict / list / tuple 을 하강한다. `FX.Ctx` 는 `dict` 서브클래스이므로 dict 분기로
    들어간다(전용 분기 불필요). 경로를 함께 내보내 위반 시 **어느 fixture 의 어느 키**인지
    지목할 수 있게 한다.
    """
    if isinstance(obj, str):
        yield path, obj
    elif isinstance(obj, dict):
        for key, val in obj.items():
            yield from _iter_texts(val, f"{path}[{key!r}]")
    elif isinstance(obj, (list, tuple)):
        for idx, val in enumerate(obj):
            yield from _iter_texts(val, f"{path}[{idx}]")


def _cr_offenders(pairs):
    """CR 판정 술어 — 계수는 `FX.count_cr` 재사용(중복 구현 금지).

    실 정의역과 음성 대조군이 **같은 함수**를 타야 "대조군이 잡은 술어" 와 "본 판정이 쓴 술어"
    가 같다는 것이 성립한다.
    """
    return [(p, FX.count_cr(t)) for p, t in pairs if FX.count_cr(t)]


def _sweep_all_fixtures():
    """전 fixture 를 호출해 (호출 성공 이름 집합, [(경로, 텍스트)]) 를 낸다."""
    called, texts = set(), []
    for name in _fixture_names():
        fn = getattr(FX, name)
        if _required_params(fn):
            calls = _FIXTURE_ARGS.get(name)
            if calls is None:
                continue          # 미등재 = 미호출. 커버리지 assert 가 이것을 RED 로 잡는다.
        else:
            calls = [((), {})]
        for idx, (args, kwargs) in enumerate(calls):
            label = name if len(calls) == 1 else f"{name}#{idx}"
            texts.extend(_iter_texts(fn(*args, **kwargs), label))
        called.add(name)
    return called, texts


def test_fixture_media_is_lf_with_zero_raw_cr():
    """매체 규약 — **전** fixture 가 LF 고정(raw CR 0). 정의역은 고정 표본이 아니라 동적 산출이다.

    정의역 = `dir(FX)` 의 `build_`/`ctx_` 접두 callable 전건. 무인자는 그대로 호출하고,
    인자가 필요한 것은 `_FIXTURE_ARGS` 의 대표 인자로 호출한 뒤, 반환값(str/dict/list/tuple —
    `Ctx` 는 dict 서브클래스)을 **재귀 순회**해 모든 문자열을 `FX.count_cr` 로 센다. 기수를
    본문에 고정하지 않는다 — 세는 **규칙**만 고정하고 값은 실행이 산출한다.
    (종전 이 테스트는 4 표본만 보면서 이름·docstring 으로 "전 fixture" 를 주장했다.)

    ★ 전수 sweep 은 **조용히 0건을 수집해도 통과**한다(hollow oracle). 그래서 3축을 함께 건다:
      · 커버리지 — 열거된 이름이 **전건** 호출됐는가 (인자 recipe 누락분을 건너뛰면 RED)
      · 양성(자기보호) — 호출 fixture 수·수집 텍스트 수가 비어있지 않은가 (배선 절단 시 RED)
      · 음성(판별력) — CR 을 심은 객체에 **같은 술어**를 적용하면 검출되는가 (항진명제가 아님)
    """
    names = _fixture_names()
    called, texts = _sweep_all_fixtures()
    print(f"\n[매체 규약] fixture 열거 {len(names)}기 / 호출 {len(called)}기 / "
          f"수집 텍스트 {len(texts)}건")

    # 커버리지 — 인자 recipe 가 없어 건너뛴 fixture 가 있으면 정의역이 조용히 좁아진 것이다.
    assert called == set(names), (                      # ← 커버리지 측정 assertion
        f"fixture 정의역 협착 — 열거 {len(names)}기 중 미호출 "
        f"{sorted(set(names) - called)}. 인자가 필요한 신규 fixture 는 `_FIXTURE_ARGS` 에 대표 "
        "인자를 등재할 것 (건너뛰기는 미검사를 '위반 0' 으로 계상하는 것과 같다)."
    )

    # 양성 대조군(자기보호) — 하한이지 값 고정이 아니다. 배선이 끊겨 0건이 되면 RED.
    assert len(called) >= 40, (                         # ← 양성 대조군 측정 assertion
        f"호출 성공 fixture {len(called)}기 — sweep 배선이 끊겼다(빈 정의역은 무엇도 못 잡는다)")
    assert len(texts) >= 1000, (                        # ← 양성 대조군 측정 assertion
        f"수집 텍스트 {len(texts)}건 — 재귀 순회가 하강하지 못했다. "
        "0건 수집도 '위반 0' 으로 통과하므로 이 하한이 없으면 검사 전체가 공허해진다.")

    # 음성 대조군(판별력) — 같은 술어가 CR 을 실제로 잡는가. 중첩 안에 심어 하강까지 함께 반증.
    poisoned = {"outer": [{"inner": "정상 줄\n"}, {"inner": "CR 섞인 줄\r\n"}]}
    caught = _cr_offenders(_iter_texts(poisoned, "negctl"))
    assert [n for _p, n in caught] == [1], (            # ← 음성 대조군 측정 assertion
        f"음성 대조군 미검출 — 술어가 항진명제다(무엇을 넣어도 위반 0). 실측 {caught}")
    assert caught[0][0] == "negctl['outer'][1]['inner']", (
        f"검출 경로가 주입 위치를 지목하지 못한다 — 실측 {caught[0][0]}")

    # 본 판정 — 전수 정의역에 raw CR 0.
    offenders = _cr_offenders(texts)
    assert not offenders, (                             # ← 매체 규약 측정 assertion
        "fixture 에 raw CR 혼입 — 매체 규약(LF 고정) 위반:\n  "
        + "\n  ".join(f"{p}: CR {n}건" for p, n in offenders[:10])
    )
