#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_story_read_surface.py — CFP-2986 Phase 2 §8.1 RTM 명명 테스트 15건 + 매체 규약 1건.

Change Plan `cfp-2986-story-growth-axis-externalization.md` §8.1 RTM 이 정본이다.
함수명 15건은 **repo 유일**이어야 하고 (ac-traceability Hop3 가 `ast.FunctionDef` 로 resolve),
각 함수는 실제 측정 assertion 을 보유해야 한다 — 심볼 존재만으로는 dead test 위 GREEN 이 가능하다.

QADev 경계: 본 파일은 테스트만 작성. production 코드(scripts/**) READ-ONLY.

엔진 미착지 시 본 suite 는 **명시 실패**한다 (skip 금지 — 미실행을 GREEN 으로 계상하지 않는다, §8.10).
"""

from __future__ import annotations

import ast
import inspect
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

import _story_read_surface_fixtures as FX

# ---------------------------------------------------------------------------
# 엔진 로딩 — 미착지는 skip 이 아니라 collection-time 실패로 드러난다.
# ---------------------------------------------------------------------------
ENGINE = None
ENGINE_LOAD_ERROR = None
try:
    ENGINE = FX.load_engine()
except FX.EngineMissing as exc:  # pragma: no cover - RED 상태 경로
    ENGINE_LOAD_ERROR = str(exc)


def engine():
    if ENGINE is None:
        raise AssertionError(
            "엔진 미착지 — RED. skip 하지 않는다 (미실행을 GREEN 으로 계상 금지).\n"
            + str(ENGINE_LOAD_ERROR))
    return ENGINE


CLI = FX.REPO_ROOT / "scripts" / "lib" / "check_story_read_surface.py"
O5_PREFIX = "::notice::story-read-cost"


# ---------------------------------------------------------------------------
# CLI 하네스 — 게이트는 **ref 기반**이므로 임시 git repo 를 만들어 구동한다.
# (작업트리 직접 스캔 금지 — 게이트는 `git archive` 로만 코퍼스를 읽는다, §4.2.2a 매체 규약)
# ---------------------------------------------------------------------------

def _git(repo, *args) -> str:
    proc = subprocess.run(["git", "-C", str(repo), *args],
                          capture_output=True, text=True, encoding="utf-8", timeout=120)
    assert proc.returncode == 0, f"git {args} 실패 rc={proc.returncode}\n{proc.stderr}"
    return proc.stdout


def _write_baseline(path, obj, eng) -> Path:
    """baseline YAML 기록 + `content_digest` 자기해시 결박 (수기 편집 시 비정상 종료)."""
    text = yaml.safe_dump(obj, allow_unicode=True, sort_keys=False)
    digest = eng.baseline_self_digest(text)
    text = re.sub(r"^content_digest:.*$", f"content_digest: {digest}", text, flags=re.M)
    FX.write_lf(path, text)
    return Path(path)


def make_repo(tmp_path, ctx, *, drop_child=None, self_pointer=False):
    """before/after 2 커밋짜리 임시 코퍼스 repo. 반환 = (repo_path, before_sha)."""
    repo = Path(tmp_path) / "repo"
    repo.mkdir(parents=True, exist_ok=True)
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "qa@example.invalid")
    _git(repo, "config", "user.name", "qa")
    _git(repo, "config", "core.autocrlf", "false")
    _git(repo, "config", "commit.gpgsign", "false")

    FX.write_lf(repo / FX.STORY_PATH, ctx["story_before"])
    FX.write_lf(repo / FX.CP_PATH, ctx["cp_before"])
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "before")
    before_sha = _git(repo, "rev-parse", "HEAD").strip()

    FX.write_lf(repo / FX.STORY_PATH, ctx["story_after"])
    FX.write_lf(repo / FX.CP_PATH, ctx["cp_after"])
    for path, text in ctx["children"].items():
        if drop_child and path.endswith(f"{drop_child}.md"):
            continue
        FX.write_lf(repo / path, text)
    if self_pointer:
        FX.write_lf(repo / FX.child_path(FX.SPLIT_ID),
                    FX.build_child("9", FX.SPLIT_ID, ctx["story_after"]))
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "--allow-empty", "-m", "after")
    return repo, before_sha


def run_cli(repo, before_sha, baseline_path, registry_path, *, extra=()):
    if not CLI.exists():
        raise AssertionError(f"CLI 미착지: {CLI}")
    cmd = [sys.executable, str(CLI), "--repo-root", str(repo),
           "--before-ref", before_sha, "--after-ref", "HEAD",
           "--baseline", str(baseline_path), "--registry", str(registry_path),
           "--json", *extra]
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", timeout=300)
    summary = None
    for line in (proc.stdout or "").splitlines():
        if line.startswith("{"):
            try:
                summary = json.loads(line)
            except json.JSONDecodeError:
                pass
    return proc.returncode, proc.stdout or "", proc.stderr or "", summary


def gate_run(tmp_path, ctx, eng, *, baseline=None, registry=None, drop_child=None,
             self_pointer=False, extra=()):
    """fixture ctx → 임시 repo → CLI 실행. 반환 = (rc, stdout, stderr, summary)."""
    repo, before_sha = make_repo(tmp_path, ctx, drop_child=drop_child, self_pointer=self_pointer)
    bl = baseline if baseline is not None else ctx["baseline"]
    bl_path = _write_baseline(Path(tmp_path) / "baseline.yaml", bl, eng)
    reg = registry if registry is not None else FX.build_registry(
        {r: ["9"] for r in FX.READER_ROSTER},
        carries={FX.child_path(FX.SPLIT_ID): ["9"], FX.child_path(FX.SPLIT_ID_S10): ["10"]})
    reg_path = Path(tmp_path) / "registry.yaml"
    FX.write_lf(reg_path, yaml.safe_dump(reg, allow_unicode=True, sort_keys=False))
    return run_cli(repo, before_sha, bl_path, reg_path, extra=extra)


def verdicts_of(summary, name=None, status=None):
    out = summary["verdicts"] if summary else []
    if name:
        out = [v for v in out if v["name"] == name]
    if status:
        out = [v for v in out if v["status"] == status]
    return out


# ===========================================================================
# AC-1 — 실읽기량 비증가
# ===========================================================================

def test_read_surface_not_increased():
    """AC-1: 분할 개입 후 `read_cost` 가 증가하지 않는다.

    5-tuple: 값 408,000 → 58,000 B / tree = synthetic fixture / 매체 LF /
    정의역 = FX-SPLIT 대 FX-FLAT 1쌍 / construction = `fx_split()` docstring.
    """
    eng = engine()
    flat, split = FX.fx_flat(), FX.fx_split()
    before_cost = FX.engine_read_cost(eng, flat)
    after_cost = FX.engine_read_cost(eng, split)

    assert before_cost == 408000, f"FX-FLAT read_cost 실측 {before_cost} != 408,000"
    assert after_cost == 58000, f"FX-SPLIT read_cost 실측 {after_cost} != 58,000"
    assert after_cost <= before_cost                       # ← AC-1 측정 assertion
    assert before_cost - after_cost == 350000, (
        "절감 Δ = −(N−d)×bytes(child) = −(8−1)×50,000 = −350,000 B 여야 한다")

    # 판별 대조군 — 순수 append 는 read_cost 를 **증가**시켜야 한다 (술어가 항등이 아님).
    grown_cost = eng.read_cost(flat["parent_bytes"] + 1000, {}, flat["readers"], flat["registry"])
    assert grown_cost > before_cost, (
        f"순수 append 가 read_cost 를 증가시키지 못하면 AC-1 은 공허하다 "
        f"(실측 {grown_cost} vs {before_cost})")


# ===========================================================================
# AC-2 — 정보 무손실 (pure move digest)
# ===========================================================================

def test_pure_move_digest_preserved():
    """AC-2: `digest(before.§n) == digest(strip_stub(after.§n) ∪ children[n])`."""
    eng = engine()
    ctx = FX.split_ctx()
    verdicts = FX.run_inv_s1(eng, ctx)

    assert FX.red_count(verdicts) == 0, (                  # ← AC-2 측정 assertion
        f"순수 이동인데 INV-S1 RED {FX.red_count(verdicts)}건: {FX.status_vector(verdicts)}")
    assert any(v.fired for v in verdicts), (
        "분할 커밋(anchor_delta ≠ ∅)인데 INV-S1 미발화 — 미발화는 통과 계상이 아니다")
    delta = eng.anchor_delta(ctx["story_before"], ctx["story_after"])
    assert eng.sections_of(delta) >= {"9", "10"}, (
        f"anchor_delta 섹션 = {eng.sections_of(delta)} — §9·§10 을 포함해야 한다")

    # 변형(정보 손실) 주입 시 반드시 RED — 술어가 항진이 아님을 같은 실행에서 보인다.
    assert FX.red_count(FX.run_inv_s1(eng, FX.ctx_e2_zwsp())) >= 1, (
        "U+200B 3 B 주입에도 GREEN 이면 digest 술어가 항진이다")


# ===========================================================================
# AC-4 — §1~§11 헤더 존재
# ===========================================================================

def test_sections_1_to_11_headers_present():
    """AC-4: 분할 전·후 모두 §1~§11 헤더가 parent 에 남는다 (stub 은 non-empty)."""
    eng = engine()
    ctx = FX.split_ctx()
    want = {str(i) for i in range(1, 12)}

    before = eng.split_sections(ctx["story_before"])
    after = eng.split_sections(ctx["story_after"])
    assert want <= set(before), f"분할 전 결손 섹션 {sorted(want - set(before))}"
    assert want <= set(after), f"분할 후 결손 섹션 {sorted(want - set(after))}"   # ← AC-4 측정

    for sec in ("9", "10"):
        stub = after[sec]
        assert stub.strip(), f"§{sec} stub 이 비어 있다 (non-empty 의무 — §3.4)"
        assert "cfp-split:begin" in stub and "cfp-split:end" in stub
        assert eng.strip_stub(stub).strip().startswith("## §"), (
            f"§{sec} stub 제거 후 헤더가 남지 않는다 (구조 파손)")

    # fence-aware — 코드펜스 안 `## §9.` 는 섹션을 만들지 않는다.
    fenced = FX.build_story(section_4_kwargs={"fence_inject_heading": True})
    assert set(eng.split_sections(fenced, True)) >= want, (
        "fence-aware 슬라이서가 펜스 안 phantom heading 에 속아 섹션 로스터가 붕괴했다")


# ===========================================================================
# AC-5 — 실읽기량 절감은 **측정됐을 때만** 인정
# ===========================================================================

def test_read_surface_reduction_measured(tmp_path):
    """AC-5: coverage < COVERAGE_FLOOR 이면 절감 주장 금지 — `UNDETERMINED` 방출."""
    eng = engine()
    readers = list(FX.READER_ROSTER)

    full = eng.coverage(readers, FX.build_registry())
    empty = eng.coverage(readers, {})
    assert full == 1.0, f"전원 등재 coverage 실측 {full} != 1.0"      # ← AC-5 측정 assertion
    assert empty == 0.0, f"빈 registry coverage 실측 {empty} != 0.0"

    # d = N (빈 registry 보수 default) ⇒ 절감 Δ = 0 — "절감 0"(판정)이 아니라 **판정 불가**여야 한다.
    fx = FX.fx_split()
    cost_dn = eng.read_cost(fx["parent_bytes"], fx["children"], readers, {})
    assert cost_dn == 8 * 1000 + 8 * 50000 == 408000, (
        f"d=N 보수 default 미적용 — 실측 {cost_dn}, 기대 408,000")

    # 게이트 축 — coverage 미달이면 READ-COST 가 UNDETERMINED 를 **명시 방출**한다.
    partial = FX.build_registry({FX.READER_ROSTER[0]: ["9"]},
                                carries={FX.child_path(FX.SPLIT_ID): ["9"]})
    rc, out, err, summary = gate_run(tmp_path, FX.split_ctx(), eng, registry=partial)
    assert summary is not None, f"--json 요약 부재. stdout={out[:400]} stderr={err[:400]}"
    und = verdicts_of(summary, "READ-COST", "UNDETERMINED")
    assert und, (
        f'coverage {summary["coverage"]} < floor {summary["coverage_floor"]} 인데 '
        f'READ-COST UNDETERMINED 미방출 — "절감 0"(GREEN)으로 뭉개면 AC-5 는 '
        f"원리적으로 충족 불가가 된다. verdicts={[v['name'] + ':' + v['status'] for v in summary['verdicts']]}")
    assert rc == eng.EXIT_UNDETERMINED, f"rc={rc}, 기대 {eng.EXIT_UNDETERMINED}"
    assert summary["coverage"] < summary["coverage_floor"]


# ===========================================================================
# AC-7 — append-heavy 섹션 외부화
# ===========================================================================

def test_append_heavy_section_externalized():
    """AC-7: §9·§10 본문이 parent 밖(자식)에 있고 parent 에는 stub 만 남는다."""
    ctx = FX.split_ctx()
    marker9 = "§9 verdict 서술 행 — 결정적 filler. #0399"
    marker10 = "§10 원장 서술 행 — 결정적 filler. #0119"

    assert marker9 not in ctx["story_after"], "§9 본문이 parent 에 잔존한다"
    assert marker10 not in ctx["story_after"], "§10 본문이 parent 에 잔존한다"
    assert marker9 in ctx["children"][FX.child_path(FX.SPLIT_ID)]
    assert marker10 in ctx["children"][FX.child_path(FX.SPLIT_ID_S10)]

    parent_before = len(ctx["story_before"].encode("utf-8"))
    parent_after = len(ctx["story_after"].encode("utf-8"))
    assert parent_after < parent_before                    # ← AC-7 측정 assertion
    moved = parent_before - parent_after
    assert moved > 10000, (
        f"외부화 이동량 실측 {moved} B — §9+§10 성장축이 실제로 나가지 않았다")


# ===========================================================================
# AC-8 — grandfather baseline 안정 식별자 키
# ===========================================================================

def test_grandfather_baseline_stable_key(tmp_path):
    """AC-8: ceiling 조회 키 = story_key(안정 식별자). 미등재 = 면제 아니라 default_ceiling."""
    eng = engine()
    bl_path = _write_baseline(tmp_path / "baseline.yaml", FX.build_baseline(), eng)
    bl = eng.load_baseline(str(bl_path))

    assert eng.ceiling_for("CFP-2986", bl) == FX.CARRIER_CEILING     # ← AC-8 측정 assertion
    assert eng.ceiling_for("CFP-9999", bl) == FX.DEFAULT_CEILING, (
        "미등재 Story 가 default_ceiling 을 적용받지 않으면 "
        "확정 1(신규 + touched ratchet)이 신규 축에서 공허해진다")
    assert eng.ceiling_for("CFP-9999", bl) not in (None, 0, float("inf")), (
        "`entries` 미등재를 '제한 없음' 으로 읽는 구현 금지")

    # 키는 파일 경로가 아니라 안정 식별자다 (E-6 새 경로로 복사 방어).
    assert eng.ceiling_for("CFP-2986", bl) == eng.ceiling_for("CFP-2986", bl)

    # baseline 수기 편집 = content_digest 불일치로 비정상 종료 (E-5 자가 상향 차단)
    tampered = bl_path.read_text(encoding="utf-8").replace(
        f"default_ceiling: {FX.DEFAULT_CEILING}", "default_ceiling: 999999999")
    tpath = tmp_path / "tampered.yaml"
    FX.write_lf(tpath, tampered)
    with pytest.raises(ValueError):
        eng.load_baseline(str(tpath))

    # default_ceiling 미정의 baseline = 배선 금지 (fail-closed)
    bad = FX.build_baseline()
    del bad["default_ceiling"]
    bad_path = _write_baseline(tmp_path / "bad.yaml", bad, eng)
    with pytest.raises(ValueError):
        eng.load_baseline(str(bad_path))


# ===========================================================================
# AC-10 — 자기적용 (carrier 통과)
# ===========================================================================

def test_self_application_carrier_passes(tmp_path):
    """AC-10: 무변경 정본 carrier 에 전 불변식 동시 적용 시 GREEN (§8.4a ④ 최소 통과선).

    라벨 규율: INV-S1 **미발화**는 통과 계상이 아니다 / INV-S2 는 **발화-GREEN** /
    INV-S3 는 enforced 4 정의역 GREEN + deferred 4 정의역 UNDETERMINED.
    통과선 = `violations == 0`. rc 는 deferred 4건 때문에 계약상 3 이며 0 이 아니다.
    """
    eng = engine()
    ctx = FX.canonical_ctx()

    s1, s2 = FX.run_inv_s1(eng, ctx), FX.run_inv_s2(eng, ctx)
    s3, s6 = FX.run_inv_s3(eng, ctx), FX.run_inv_s6(eng, ctx)

    assert FX.red_count(s1) == 0, f"INV-S1 RED: {FX.status_vector(s1)}"
    assert not any(v.fired for v in s1), (
        "무변경 정본은 anchor_delta = ∅ 이므로 INV-S1 은 정의상 미발화여야 한다")
    assert FX.red_count(s2) == 0, f"INV-S2 RED: {FX.status_vector(s2)}"
    assert any(v.fired for v in s2), (
        "INV-S2 는 발화-GREEN 이어야 한다 (미발화를 통과로 계상 금지 — R4 P2 라벨 정정)")
    assert FX.red_count(s3) == 0, f"INV-S3 RED: {FX.status_vector(s3)}"   # ← AC-10 측정
    assert FX.red_count(s6) == 0, f"INV-S6 RED: {FX.status_vector(s6)}"

    green = {v.domain for v in s3 if v.status == "PASS"}
    assert set(FX.ENFORCED_DOMAINS) <= green, (
        f"enforced 정의역 4/4 GREEN 미달 — 실측 GREEN {sorted(green)}")
    assert FX.undetermined_domains(s3) >= set(FX.DEFERRED_DOMAINS), (
        f"deferred 정의역은 GREEN 이 아니라 UNDETERMINED 여야 한다 "
        f"— 실측 {sorted(FX.undetermined_domains(s3))}")

    # 게이트 전 경로 동시 구동 — carrier 가 자기 규칙을 통과한다.
    rc, out, err, summary = gate_run(tmp_path, FX.split_ctx(), eng)
    assert summary is not None, f"stdout={out[:400]} stderr={err[:400]}"
    assert summary["violations"] == 0, (
        f"carrier 위반 {summary['violations']}건: "
        f"{[v['detail'] for v in summary['verdicts'] if v['status'] == 'RED']}")
    assert summary["deferred"] >= 4, "deferred 정의역이 UNDETERMINED 로 계상되지 않았다"
    assert rc == eng.EXIT_UNDETERMINED, (
        f"deferred 4정의역 보유 baseline 의 계약상 rc = 3 (UNDETERMINED). 실측 {rc}")

    # deferred 를 전건 enforced 로 올리면 같은 carrier 가 rc=0 에 도달한다 (승격 사전조건).
    rc2, _o2, _e2, sm2 = gate_run(tmp_path / "promoted", FX.split_ctx(), eng,
                                  baseline=FX.build_baseline(deferred=False))
    assert sm2 is not None and sm2["violations"] == 0
    assert rc2 == eng.EXIT_PASS, f"전 정의역 enforced 인데 rc={rc2} (기대 0)"


# ===========================================================================
# AC-11 — 파생 뷰는 재생성 가능하되 유일 원본이 아니다
# ===========================================================================

def test_derived_view_regenerable_and_not_sole_source():
    """AC-11: 자식으로부터 원문을 재생성할 수 있고, parent 단독으로는 불가능하다.

    **재생성의 정의역 = 섹션 단위 `reassemble` + `content_canon`** (INV-S1 이 판정에 쓰는 그 정의).
    문서 전체 `reassemble_document` 는 **바이트 무손실이 아니다** — 재조립 섹션마다 말미 빈 줄
    1개를 흡수한다 [실측: 본 fixture 에서 20,486 → 20,484 B, Δ = −2 B = 재조립 섹션 2개 × 1 B,
    정의역 = split fixture 1건, 매체 LF]. 따라서 재조립은 **추출 정의역** 용도이며 rollback 경로가
    아니다 (§11.3 rollback = `git revert`). 이 한정을 넘겨 "바이트 동일 복원" 을 주장하지 않는다.
    """
    eng = engine()
    ctx = FX.split_ctx()
    kids = FX.children_by_section(eng, ctx)
    before_secs = eng.split_sections(ctx["story_before"])
    after_secs = eng.split_sections(ctx["story_after"])

    for sec in ("9", "10"):
        regenerated = eng.reassemble(after_secs[sec], kids[sec])
        assert eng.digest(eng.content_canon(regenerated)) == \
            eng.digest(eng.content_canon(before_secs[sec])), (   # ← AC-11 측정 assertion
            f"§{sec} 재조립본 digest 가 원문과 다르다 — 순수 이동이 아니다")

    # 문서 전체 재조립은 내용을 전건 보유한다 (정보 손실 0 — 공백 정규화만 발생).
    doc = eng.reassemble_document(ctx["story_after"], kids)
    for marker in ("§9 verdict 서술 행 — 결정적 filler. #0399",
                   "§10 원장 서술 행 — 결정적 filler. #0119"):
        assert marker in doc, f"재조립 문서에 {marker!r} 부재 — 정보 손실"
    lost = len(ctx["story_before"].encode("utf-8")) - len(doc.encode("utf-8"))
    assert lost == 2, (
        f"재조립 손실 실측 {lost} B — 기대 2 B(재조립 섹션 2개 × 말미 빈 줄 1 B). "
        "값이 다르면 공백 정규화 이상의 손실이 생긴 것이다")

    # 자식 없이는 재생성 불가 — 조용한 skip 이 아니라 결손으로 드러나야 한다.
    with pytest.raises(Exception):
        eng.reassemble_document(ctx["story_after"], {})
    assert len(ctx["story_after"].encode("utf-8")) < len(ctx["story_before"].encode("utf-8")), (
        "parent 단독이 원문보다 작지 않으면 '유일 원본이 아니다' 주장이 공허하다")


# ===========================================================================
# AC-12 — 인덱스 깊이 ≤ 1
# ===========================================================================

def test_index_depth_not_exceeding_one():
    """AC-12 / INV-S6: 자식 안 split 마커 부재. 깊이 2 는 RED."""
    eng = engine()
    flat = FX.run_inv_s6(eng, FX.split_ctx())
    nested = FX.run_inv_s6(eng, FX.ctx_nested_child())

    assert FX.red_count(flat) == 0, f"깊이 1 대조군이 RED: {FX.status_vector(flat)}"
    assert FX.red_count(nested) >= 1, (                      # ← AC-12 측정 assertion
        "자식 안 `cfp-split:begin` 앵커(깊이 2)를 검출하지 못했다")
    assert any(v.fired for v in nested)


# ===========================================================================
# AC-15 — 크기 판정은 신호이지 차단이 아니다
# ===========================================================================

def test_size_verdict_is_signal_not_block(tmp_path):
    """AC-15 / §3.6: "너무 큰가" = 비차단 SIGNAL / "정보를 잃었는가" = fail-closed."""
    eng = engine()
    tiny = FX.build_baseline(deferred=False)
    tiny["default_ceiling"] = 1
    tiny["entries"] = [{"story_key": "CFP-2986", "ceiling": 1}]

    rc, out, err, summary = gate_run(tmp_path / "sig", FX.split_ctx(), eng, baseline=tiny)
    assert summary is not None, f"stdout={out[:400]} stderr={err[:400]}"
    signal = verdicts_of(summary, "READ-COST", "SIGNAL")
    assert signal, (
        f"ceiling 1 B 초과인데 SIGNAL 미방출 — "
        f"{[(v['name'], v['status']) for v in summary['verdicts']]}")
    assert summary["violations"] == 0, "크기 초과가 위반으로 계상됐다"
    assert rc == eng.EXIT_PASS, (                            # ← AC-15 측정 assertion
        f"크기 축은 **비차단 신호**여야 한다 (ADR-058 §결정 5 count cap 거부 회피). 실측 rc={rc}")

    # 대조 — 정보 손실 축은 같은 실행 계층에서 fail-closed 여야 한다.
    rc2, _o, _e, sm2 = gate_run(tmp_path / "loss", FX.split_ctx(), eng,
                                baseline=FX.build_baseline(deferred=False),
                                drop_child=FX.SPLIT_ID)
    assert rc2 == eng.EXIT_FAIL, f"dangling pointer 인데 rc={rc2} (기대 {eng.EXIT_FAIL})"
    assert sm2 and sm2["violations"] >= 1


# ===========================================================================
# AC-17 — mutant RED ∧ 대조군 GREEN
# ===========================================================================

def test_mutant_red_and_control_green():
    """AC-17: §8.2 mutant 로스터 전건 — 주입 RED ∧ 미주입 대조군 GREEN.

    판정은 **boolean 단독 금지** — 위반 개수(count) ∧ per-mutant 판정 벡터를 assert 한다 (C-6).
    """
    eng = engine()
    results = FX.run_battery(eng)
    print(FX.format_report(results))

    mismatched = {mid: r for mid, r in results.items()
                  if not mid.startswith("_") and r["verdict"] != "기대일치"}
    assert not mismatched, (                                  # ← AC-17 측정 assertion
        "mutant 기대 불일치:\n" + "\n".join(
            f"  {mid}: {r['verdict']} | 대조군 RED {r['control_red_count']} / "
            f"주입 RED {r['injected_red_count']} / 벡터 {r['vector']} / "
            f"construction={r['construction']}" for mid, r in mismatched.items()))

    # admission rule — 대조군이 이미 RED 인 mutant 는 등가 mutant 이므로 계상 금지.
    equivalent = {mid for mid, r in results.items()
                  if not mid.startswith("_") and r["control"] == "RED"}
    assert not equivalent, f"등가 mutant(대조군 이미 RED) 계상 금지 — {sorted(equivalent)}"

    # 위반 **개수** 벡터 — boolean 만 보면 봉합 제거를 놓친다 (C-6).
    expected_red_counts = {
        "M-CARD-IN": 1, "M-CARD-VALUE": 1, "M-CARD-CROSS": 2, "M-S3-NOSPLIT": 2,
        "M-DUP-ROW": 1, "M-EQUIV": 0, "M-PREEXIST": 1,
        "M-APPEND-CTL-1000": 0, "M-APPEND-CTL-50000": 0, "M-MARGIN": 0, "M-BASIS-RAW": 0,
    }
    actual = {k: results[k]["injected_red_count"] for k in expected_red_counts}
    assert actual == expected_red_counts, (
        f"위반 개수 벡터 불일치\n  기대 {expected_red_counts}\n  실측 {actual}")

    # leg 3항 독립 반증 — 각 leg 이 **단독으로** RED 를 내는 mutant 가 실재해야 한다.
    assert results["M-CARD-IN"]["vector"] == ["CP_S81_RTM:leg1"]
    assert results["M-DUP-ROW"]["vector"] == ["CP_S81_RTM:leg2"]
    assert results["M-CARD-VALUE"]["vector"] == ["CORPUS:leg3"]


# ===========================================================================
# AC-18 — 형제 site 회귀 0
# ===========================================================================

def test_sibling_site_no_regression():
    """AC-18: 한 정의역 주입이 형제 정의역을 오염시키지 않고, 전역 주입은 형제 전건에서 검출된다."""
    eng = engine()

    # (a) 단일 site 주입 — 형제 정의역은 GREEN 유지 (부수 RED 0)
    single = FX.red_vector(FX.run_inv_s3(eng, FX.ctx_card_in()))
    assert single == frozenset({("CP_S81_RTM", "leg1")}), (
        f"단일 site 주입이 형제 정의역까지 흔들었다 — 실측 {sorted(single)}")

    # (b) 전역 주입 M-GLOBAL — AC-11 → AC-99 를 **형제 site 양쪽**에서 검출
    glob = FX.red_domains(FX.run_inv_s3(eng, FX.ctx_global_sibling()))
    assert "CP_S81_RTM" in glob                               # ← AC-18 측정 assertion
    assert "STORY_S53_AC_TABLE" in glob, (
        f"형제 site(Story §5.3)에서 회귀 검출 실패 — 실측 {sorted(glob)}")

    # (c) 대조군 — 무변경 정본은 두 site 모두 GREEN
    assert FX.red_count(FX.run_inv_s3(eng, FX.canonical_ctx())) == 0


# ===========================================================================
# AC-19 — 규칙에 섹션 하드코딩 없음
# ===========================================================================

def mini_story(bodies: dict) -> str:
    parts = ["---", "story: CFP-2986", "---", ""]
    for n in range(1, 12):
        parts += [f"## §{n}. 제목", "", bodies.get(str(n), "본문."), ""]
    return "\n".join(parts)


def test_rule_has_no_section_hardcoding():
    """AC-19: 규칙이 섹션 **이름**이 아니라 성질을 참조한다 — 거동 축 + 소스 축 2 leg."""
    eng = engine()

    # leg (a) 거동 — §9→§7 이 아닌 §6→§5 보상 이동도 동일하게 RED 여야 한다.
    pad = "z" * 8192
    r97 = FX.red_count(eng.check_inv_s2(
        mini_story({"9": pad, "7": "본문."}), mini_story({"9": "본문.", "7": pad}), 4096, None))
    r65 = FX.red_count(eng.check_inv_s2(
        mini_story({"6": pad, "5": "본문."}), mini_story({"6": "본문.", "5": pad}), 4096, None))
    assert r97 >= 1, "§9→§7 보상 이동이 RED 가 아니다 (대조 성립 불가)"
    assert r65 == r97, (                                      # ← AC-19 측정 assertion
        f"섹션 번호에 따라 판정이 갈린다 — §9→§7 RED {r97} vs §6→§5 RED {r65}. "
        "규칙이 섹션 이름에 하드코딩돼 있다.")

    # leg (b) 소스 — 판정 함수 안에 섹션 번호 리터럴 비교 금지.
    tree = ast.parse(FX.engine_source())
    banned = {"9", "10", "§9", "§10", 9, 10}
    offenders = []
    for fn in ast.walk(tree):
        if not isinstance(fn, ast.FunctionDef) or not fn.name.startswith("check_"):
            continue
        for node in ast.walk(fn):
            if isinstance(node, ast.Compare):
                for c in ast.walk(node):
                    if isinstance(c, ast.Constant) and c.value in banned:
                        offenders.append(f"{fn.name}:{c.lineno} → {c.value!r}")
    assert not offenders, (
        "판정 함수에 섹션 번호 리터럴 비교가 있다 (성질 레지스트리 참조여야 한다): "
        + "; ".join(offenders))


# ===========================================================================
# AC-20 — 위반 fixture 는 non-zero exit
# ===========================================================================

def test_violation_fixture_exits_nonzero(tmp_path):
    """AC-20: anti-hollow — 정보 손실 fixture 는 rc≠0, 대조군은 rc=0. O5 값 방출 동반."""
    eng = engine()
    clean = FX.build_baseline(deferred=False)

    rc_ok, out_ok, err_ok, sm_ok = gate_run(tmp_path / "ctl", FX.split_ctx(), eng, baseline=clean)
    assert rc_ok == eng.EXIT_PASS, (
        f"대조군 rc={rc_ok} (기대 0). "
        f"RED={[v['detail'] for v in (sm_ok or {}).get('verdicts', []) if v['status'] == 'RED']} "
        f"stderr={err_ok[:300]}")

    rc_bad, out_bad, _e, sm_bad = gate_run(tmp_path / "viol", FX.split_ctx(), eng,
                                           baseline=clean, drop_child=FX.SPLIT_ID)
    assert rc_bad != 0, (                                     # ← AC-20 측정 assertion
        f"dangling pointer fixture 가 rc=0 으로 통과했다 (hollow gate). stdout={out_bad[:400]}")
    assert rc_bad == eng.EXIT_FAIL
    assert sm_bad and sm_bad["violations"] >= 1

    # §7.4a O5 — exit code 만으로는 "위반 0" 과 "스캔 0" 을 구별할 수 없다. 값 방출 의무.
    for label, out, sm in (("대조군", out_ok, sm_ok), ("위반", out_bad, sm_bad)):
        assert O5_PREFIX in out, f"{label} O5 방출 부재 — stdout={out[:400]}"
        line = next(l for l in out.splitlines() if l.startswith(O5_PREFIX))
        for key in ("scanned_count=", "violations=", "deferred=", "domain=", "tree="):
            assert key in line, f"{label} O5 필드 `{key}` 부재 — line={line}"
        assert sm["scanned_count"] > 0, (
            f"{label} scanned_count=0 — GREEN 이 아니라 조사 대상이다 (정의역 붕괴 의심)")


# ===========================================================================
# AC-21 — 측정 단위 정합 (M-UNIT — FX-SPLIT 위에서만 선언)
# ===========================================================================

def test_metric_unit_matches_declared_quantity():
    """AC-21: 술어 = **실읽기 바이트**. 자식포함총합/줄수 치환은 FX-SPLIT 에서 판정을 바꾼다.

    FX-FLAT 은 `read_cost = 8 × 자식포함총합` 인 **단조 배수**라 M-UNIT 이 등가 mutant 로
    전락한다 — 그래서 FX-FLAT 단독 선언을 금지하고 FX-SPLIT 을 필수로 둔다.
    """
    eng = engine()
    split, flat = FX.fx_split(), FX.fx_flat()
    rc_split, rc_flat = FX.engine_read_cost(eng, split), FX.engine_read_cost(eng, flat)
    sub_split, sub_flat = FX.total_including_children(split), FX.total_including_children(flat)

    assert (rc_split, sub_split) == (58000, 51000)            # ← AC-21 측정 assertion
    assert (rc_flat, sub_flat) == (408000, 51000)

    # FX-FLAT — 단조 배수 ⇒ 판별력 0 (등가 mutant). 여기서 단위를 "검증했다" 고 선언 금지.
    assert rc_flat == 8 * sub_flat, (
        "FX-FLAT 이 단조 배수가 아니면 M-UNIT 특칙의 전제가 무너진다")
    # FX-SPLIT — 단조 배수 관계가 깨진다 ⇒ 치환이 판정을 바꾼다 (판별력 O).
    assert rc_split != 8 * sub_split
    assert rc_split - sub_split == 7000, (
        f"FX-SPLIT 판별 차 실측 {rc_split - sub_split} != 7,000 B")

    # 줄수 대리 단위도 두 fixture 를 구별하지 못한다 (분할 개입에 무감).
    assert FX.line_count_metric(split) == FX.line_count_metric(flat), (
        "줄수 단위가 분할을 구별하면 M-UNIT 술어 선정이 틀린 것이다")
    assert rc_split != rc_flat, "실읽기 바이트 술어가 분할 개입을 구별하지 못한다"


# ===========================================================================
# §8.4 매체 규약 — `git archive`(LF) 만, 작업트리 직접 스캔 금지
# ===========================================================================

def test_gate_uses_archive_not_worktree():
    """§8.4 매체 규약: 바이트 획득 = `git archive` 추출(LF 고정). 작업트리 스캔 금지.

    §4.2.2a 가 작업트리 직접 스캔을 금지하므로 게이트가 이를 어기면 Story 자신의 규약 위반이다.
    """
    eng = engine()

    # (a) 소스 — `git_archive_bytes` 가 실제로 `git archive` 를 호출하고 작업트리를 읽지 않는다.
    src = inspect.getsource(eng.git_archive_bytes)
    assert '"archive"' in src or "'archive'" in src, (
        "`git_archive_bytes` 가 `git archive` 를 쓰지 않는다")
    assert "read_text" not in src and "read_bytes" not in src, (
        "`git_archive_bytes` 가 작업트리 파일을 직접 읽는다 (매체 규약 위반)")
    assert eng.CORPUS_ACCESS_MEDIUM == "git_archive"

    # (b) 거동 — 실 repo 에서 추출한 바이트에 raw CR 이 0 이어야 한다 (LF 고정).
    head = FX.repo_head_sha()
    assert head != "unavailable", "repo HEAD 조회 실패 — 매체 규약 실측 불가"
    data = eng.git_archive_bytes(str(FX.REPO_ROOT), "HEAD", "requirements.txt")
    assert isinstance(data, (bytes, bytearray)), "git_archive_bytes 반환형이 bytes 가 아니다"
    assert FX.count_cr(data) == 0, (                          # ← 매체 규약 측정 assertion
        f"`git archive` 추출물에 raw CR {FX.count_cr(data)}개 — LF 고정 위반 "
        f"(tree={head}, 정의역 = requirements.txt 1건)")
    assert b"pyyaml" in data.lower(), "추출 내용이 requirements.txt 가 아니다"

    # (c) 서명 — `read_cost` 는 바이트를 **인자로** 받는다 ⇒ 스스로 작업트리를 스캔할 수 없다.
    params = list(inspect.signature(eng.read_cost).parameters)
    assert params[:1] == ["parent_bytes"], f"`read_cost` 첫 인자 실측 {params}"

    # (d) fixture 자신도 매체 규약을 지킨다 (CRLF 오염 0).
    for name, text in (("story", FX.build_story()), ("cp", FX.build_cp())):
        assert FX.count_cr(text) == 0, f"{name} fixture 에 raw CR 혼입"
