"""test_adr182_review_domain_separation_contract.py — ADR-182 판정 계약 검증.

CFP-2999 Phase 2 (구현·검증) / Change Plan §8.1 RTM (13 AC zero-drop) + 가드 3종.
Under test: archive/adr/ADR-182-review-domain-write-domain-separation.md

계약 tier (Change Plan §8.12 정직 천장 승계):
  · 13 AC named test = 문서-파싱 presence assert — 기계 라벨 상한 = presence.
    검출력·의미 완결성은 비강제 (CEILING_DISCLOSURE — "완전 봉인" 주장 금지).
  · probe 판정 정의역 = RTM 판정원이 지정한 「§결정 N 절 slice」 (구현리뷰 iter1
    F-CR1-01 정산 — 술어 정의역 = 주장 정의역. 문서-전역 substring 협착 금지:
    절 밖 동일 문자열이 절-국소 소멸을 가리는 경로 차단).
  · 가드 3종 = 오라클 자기방어 (RTM 비매핑):
      - test_adr182_clause_probe_red_on_removed_clause — 3축 동시 실증:
        ⑴ 미주입 대조군 GREEN (실 문서 probe 전건 통과)
        ⑵ 전역 mutant RED (앵커 전 출현 제거 사본 — 유지 축)
        ⑶ 절-국소 mutant RED (주장 §결정 절 안의 출현만 제거한 사본 — F-CR1-01 ③.
           전역 축과 서로 맹점 보완: probe 가 전역 탐색으로 퇴행하면 본 축이 RED)
        + count==1 구조적 backstop (F-CR1-01 ④ — 앵커 다중 출현 희석 재발을 형태로
        봉인. 재발 시 처방 = 검사 완화가 아니라 앵커의 절-유일 형태 정밀화).
        mutant 는 in-memory 사본 + pytest tmp_path 스크래치 — repo 오염 0.
      - test_cfp2999_story_section5_resolves_to_real_section:
        이의 A (§1 verbatim 내부 헤딩 shadowing → first-match slicing vacuous) 회귀.
        Story 파일은 internal-docs repo 소재 — `CFP2999_STORY_PATH` env 주입 시 실행,
        미주입 시 정직 skip (게이트 slicing 정정 = 후속 배선 Story — ADR-182 §편입 지시 5항).
      - test_ac_source_enum_matches_contract_enum:
        이의 B (`source: analyst` ∉ 계약 enum — internal-docs `9a25c46a` 기정정) 회귀.
        presence 가 아니라 실행 검증 — validate_ac_record 가 결함 값을 실제로 기각하는지
        양성(기각) ∧ 음성(정상 값 통과) 쌍으로 assert.

오라클 규율 (Change Plan §8.2.1):
  · 본 파일의 문면 대조는 Python str 연산 (locale 무관 — 엔진 pin 축과 disjoint).
    census 재실행은 하지 않는다 — ADR-182 §결정 0 이 엔진 pin (`git grep` byte-mode /
    `LC_ALL=C`) 을 성문했는지의 presence 만 검사 (AC-0 앵커).
  · 좌표 파생 정수 금지 — 본 파일의 유일 수치 상수는 ADR-182 §결정 5 표의
    3-상태 계약 (스펙 상수, 좌표 비파생).

CI 실행 채널 (F-CR1-02 정산): `.github/workflows/cfp2999-adr182-contract-test.yml`
  — on.paths {ADR-182, 본 파일} + push(main), day-1 hard-fail · non-required
  (branch protection 8-tuple 무접촉).

부재 처리 (ADR-178 test 선례 동형 — 무조건 skip 은 false-negative 채널):
  · `ADR182_PATH` 명시 지정인데 부재 → fail (명시 요청의 setup error)
  · wrapper home(`archive/adr/` 실재)인데 부재 → fail (조용한 소멸 차단)
  · `archive/adr/` 자체가 없음 = consumer 환경 → skip (정직한 degradation)
"""

from __future__ import annotations

import os
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent

# ADR-182 §결정 5 transition 표의 상태 행 수 — 스펙 상수 (신규/진행중·BLOCKED/완료).
# 재현: ADR-182 §결정 5 표의 데이터 행 (`| **…** |` 로 시작하는 행) 수와 일치해야 한다.
EXPECTED_TRANSITION_STATE_ROWS = 3


def _get_adr_path() -> Path:
    """ADR-182 파일 위치. env override 가능 (mutant 실증용 seam — ADR-178 선례 동형)."""
    env_path = os.environ.get("ADR182_PATH")
    if env_path:
        return Path(env_path)
    return REPO_ROOT / "archive" / "adr" / "ADR-182-review-domain-write-domain-separation.md"


def _is_wrapper_home() -> bool:
    """wrapper home 판별 — ADR 저장 디렉터리 실재 여부 (ADR-178 test 선례 동형)."""
    return (REPO_ROOT / "archive" / "adr").is_dir()


def _load_adr(path: Path) -> str:
    return path.read_text(encoding="utf-8")


@pytest.fixture
def adr182_content() -> str:
    """ADR-182 전문 로드 — 부재 시 fail/skip 분기는 모듈 docstring 계약."""
    adr_path = _get_adr_path()
    if not adr_path.exists():
        if os.environ.get("ADR182_PATH"):
            pytest.fail(f"ADR182_PATH 명시 지정인데 파일 부재: {adr_path}")
        if _is_wrapper_home():
            pytest.fail(
                f"wrapper home 인데 ADR-182 부재: {adr_path} — "
                "여기서 부재 = 결함 (skip 하면 13 AC 가 조용히 소멸)"
            )
        pytest.skip("consumer 환경 (archive/adr/ 부재) — 정직한 degradation")
    return _load_adr(adr_path)


def _decision_section_span(content: str, n: int) -> tuple[int, int]:
    """§결정 N 절의 (start, end) 문자 span.

    종료 lookahead = 다음 h1~h3 헤딩 또는 EOF (F-CR1-03 정산 — h3 한정이던
    구판 `(?=^### |\\Z)` 는 h2 경계 미인식 latent 과포획 채널).
    """
    m = re.search(
        rf"^### §결정 {n} — .*?(?=^#{{1,3}} |\Z)",
        content,
        flags=re.MULTILINE | re.DOTALL,
    )
    assert m, f"§결정 {n} 절 슬라이스 실패"
    return m.span()


def _decision_section(content: str, n: int) -> str:
    s, e = _decision_section_span(content, n)
    return content[s:e]


# ── probe 명세: AC-id → (RTM 판정원 §결정 N, load-bearing 문면 앵커 목록) ──
# probe 판정 정의역 = 해당 §결정 절 slice (F-CR1-01 ② — RTM 판정원 결속).
# 각 앵커는 문서-전역 유일 (가드 1 count==1 backstop) ∧ 절 내 소재 — 다중 출현이던
# 2건은 절-유일 형태로 정밀화 (AC-1c 본문 side 행 / AC-2c 판정원 ② 항).
PROBE_SPECS: dict[str, dict] = {
    "AC-0": {
        "section": 0,
        "anchors": [
            "### §결정 0 — 심사 정의역 정본 = Story §1-§6 단일값 (AC-0 선결)",
            "(표기 정본 = `§1-§6`)",
            "**3-bucket 전건 분류 (28/28 종결 — 미분류 잔량 0)**",
            "census·통제 fixture 공히 `git grep`(byte-mode, locale 무관) 또는 `LC_ALL=C grep` 로 실행한다",
            "**좌표 유효 범위 = @4b30b860 한정**",
            "NF4-04: bucket C 수신자 = 본 ADR",
        ],
    },
    "AC-1a": {
        "section": 1,
        "anchors": [
            "**분리를 채택한다.**",
            "**메타-텍스트 3종 (closed-enum)**",
            "**FIX 회차 마커**",
            "**census·측정 기록**",
            "**회귀 방지 규율**",
        ],
    },
    "AC-1b": {
        "section": 1,
        "anchors": [
            "**본문 정정 write 는 §2-§6 에 잔존한다**",
            "**이관 목적지 = 신규 증적 전용 monopoly 섹션**",
            "이관 목적지 3안 중 (c)",
            "§9 부적격",
            "§10 부적격",
        ],
    },
    "AC-1c": {
        "section": 1,
        "anchors": [
            "**cross-ref 양방향 요건 (AC-1c — 추적성 보상, 무보상 통과 차단)**",
            "`{finding-id, 대상 섹션 heading 앵커, 정정 커밋 SHA}`",
            "**라인 번호 등 좌표 파생 정수는 금지**",
            "- **본문 side** = Story 골격에 고정 포인터 1줄",
        ],
    },
    "AC-2a": {
        "section": 2,
        "anchors": [
            "**PASS 조건을 severity-gated exit 로 정밀화한다.**",
            "PASS = P0 0 ∧ P1 0 ∧ 직전 회차 finding 전건 처분 종결",
            "**도달 가능성 근거**",
        ],
    },
    "AC-2b": {
        "section": 2,
        "anchors": [
            "**MTD-1944 13회차 시뮬레이션 (AC-2b — §1 문면만으로 수행)**",
            "**PASS 불성립 (P1 1건) — 판별 가능**",
            "**판별 범위 분할 (정직 천장 승계)**",
            "6건 중 5건 미분류",
        ],
    },
    "AC-2c": {
        "section": 2,
        "anchors": [
            "**처분 판정원 (AC-2c)**",
            "리뷰 PL 보고서의 처분 표",
            "② fix-event-v1 v1.4 `replay_verdict`",
            "②의 실배선 = B(CFP-2985) 편입",
        ],
    },
    "AC-3a": {
        "section": 3,
        "anchors": [
            "**RESET 정당화에 positive 기재 의무를 신설한다.**",
            "「**구조 변경** (corrective action",
            "「**술어 개선** (correction",
            "**술어 개선 단독으로는 동일 카운터 내 재-RESET 불가.**",
            "**기재 위치** = §10 FIX Ledger RESET row 신규 column",
        ],
    },
    "AC-3b": {
        "section": 3,
        "anchors": [
            "**판별 불가 분기 (AC-3b)**",
            "**RESET 불허 — ESCALATE**",
            "판별 불가를 RESET 통과 경로로 쓸 수 없다",
        ],
    },
    "AC-4a": {
        "section": 4,
        "anchors": [
            "**적용을 채택한다.**",
            "**적용 범위 boolean 판정만**",
            "적용 정의역에 §9·§10 원장을 포함한다",
            "**원장을 심사 정의역에 편입하지 않는 조건 하에서만** 적용한다",
            "**수신자 = §9/§10 write 주체 전원**",
        ],
    },
    "AC-5a": {
        "section": 5,
        "anchors": [
            "### §결정 5 — 소급 transition 3-상태 (요청 5 — AC-5a/5b/5c)",
            "| **신규** (본 판정 확정 후 개시) |",
            "| **진행중·BLOCKED** (MTD-1944 포함) |",
            "| **완료** |",
        ],
    },
    "AC-5b": {
        "section": 5,
        "anchors": [
            "**MTD-1944 조항 (AC-5b)**",
            "**14회차부터 신 exit 조건 적용**",
            "기존 RESET 5회 유효 보존",
            "**max-FIX 카운터 2/3 동결값 이월 — 재산정 금지**",
        ],
    },
    "AC-5c": {
        "section": 5,
        "anchors": [
            "**조정 규칙 (AC-5c — 사전 명문화)**",
            "① 완료 Story 제외",
            "② 기존 RESET 마커 유효",
            "③ 신규 마커부터 신 규칙",
            "완료 Story 전수 재스캔은 발의하지 않는다",
        ],
    },
}


def _probe(content: str, ac_id: str) -> list[str]:
    """AC probe 실행 — RTM 판정원 §결정 절 slice 안에서 탐색, 부재 앵커 목록 반환.

    정의역 한정 (F-CR1-01 ②): 절 slice 실패 시 전 앵커 부재로 보고 (fail-closed —
    절 자체가 사라지면 그 AC 의 판정원이 소멸한 것).
    """
    spec = PROBE_SPECS[ac_id]
    try:
        section = _decision_section(content, spec["section"])
    except AssertionError:
        return list(spec["anchors"])  # 절 소멸 = 전 앵커 부재 (fail-closed)
    return [a for a in spec["anchors"] if a not in section]


def _assert_probe(content: str, ac_id: str) -> None:
    missing = _probe(content, ac_id)
    assert not missing, (
        f"{ac_id} load-bearing 앵커가 §결정 {PROBE_SPECS[ac_id]['section']} 절에 부재: {missing}"
    )


# ── 13 AC named tests (Change Plan §8.1 RTM 후보명 그대로 — Hop3 ast 대상) ──


def test_adr182_review_domain_canonical_single_value(adr182_content):
    """AC-0: 심사 정의역 정본 = §1-§6 단일값 + 3-bucket 전건 종결 + 엔진 pin + 좌표 한정."""
    _assert_probe(adr182_content, "AC-0")


def test_adr182_domain_separation_verdict_present(adr182_content):
    """AC-1a: 분리 채택 verdict + 메타-텍스트 closed-enum 3종 (마커·census·규율)."""
    _assert_probe(adr182_content, "AC-1a")


def test_adr182_separation_scope_and_destination(adr182_content):
    """AC-1b: 본문 정정 write §2-§6 잔존 + 이관 목적지 = 신규 monopoly 섹션 (§9/§10 부적격)."""
    _assert_probe(adr182_content, "AC-1b")


def test_adr182_crossref_bidirectional_format(adr182_content):
    """AC-1c: cross-ref 형식 리터럴 — row 필수 3필드 + 본문 고정 포인터 + 좌표 정수 금지."""
    _assert_probe(adr182_content, "AC-1c")


def test_adr182_exit_condition_verdict_and_reachability(adr182_content):
    """AC-2a: severity-gated exit 채택 + PASS 조건 문면 + 도달 가능성 근거."""
    _assert_probe(adr182_content, "AC-2a")


def test_adr182_exit_simulation_decidable_split(adr182_content):
    """AC-2b: MTD-1944 시뮬레이션 + PASS 불성립 판별 + 판별 범위 분할 (미분류 정직 기재).

    함정 (Change Plan §8.1): "판별 불가가 정상 결과인 항" 의 인정 문면 (6건 중 5건 미분류)
    presence 를 assert 한다 — "전항 충족" 단정을 요구하면 그 자체가 정직 천장 위반.
    """
    _assert_probe(adr182_content, "AC-2b")


def test_adr182_disposition_source_and_closed_criterion(adr182_content):
    """AC-2c: 처분 판정원 2종 (처분 표 + replay_verdict) — B 소유면은 참조만 (배선 지정 문면)."""
    _assert_probe(adr182_content, "AC-2c")


def test_adr182_reset_axis_obligation_and_location(adr182_content):
    """AC-3a: RESET 2치 분류 기재 의무 + 자격 조건 + 기재 위치 (§10 RESET row column)."""
    _assert_probe(adr182_content, "AC-3a")


def test_adr182_reset_undecidable_branch(adr182_content):
    """AC-3b: 판별 불가 → RESET 불허·ESCALATE 분기."""
    _assert_probe(adr182_content, "AC-3b")


def test_adr182_ledger_derivation_scope_and_boundary(adr182_content):
    """AC-4a: 원장 파생화 적용 boolean true + 심사 정의역 비편입 경계 + 수신자 전원."""
    _assert_probe(adr182_content, "AC-4a")


def test_adr182_transition_rule_three_states(adr182_content):
    """AC-5a: transition 3-상태 표 — fail-closed (3행 결정론, 1개 상태 누락 = born-broken).

    presence 앵커에 더해 §결정 5 표의 데이터 행 수 = 3 을 구조적으로 assert 한다
    (Change Plan §8.1 "표 형태 강제" — 상태 행 추가·삭제 양방향 검출).
    슬라이스 = 공유 helper (h1~h3 종료 lookahead — F-CR1-03 정산).
    """
    _assert_probe(adr182_content, "AC-5a")
    section = _decision_section(adr182_content, 5)
    state_rows = [ln for ln in section.splitlines() if re.match(r"^\| \*\*", ln)]
    assert len(state_rows) == EXPECTED_TRANSITION_STATE_ROWS, (
        f"transition 표 상태 행 수 {len(state_rows)} ≠ 스펙 상수 "
        f"{EXPECTED_TRANSITION_STATE_ROWS} (신규/진행중·BLOCKED/완료): {state_rows}"
    )


def test_adr182_mtd1944_resume_clause(adr182_content):
    """AC-5b: MTD-1944 재개 조항 — 14회차 신 exit + RESET 5회 유효 + 카운터 2/3 동결 이월."""
    _assert_probe(adr182_content, "AC-5b")


def test_adr182_recount_rule_predeclared(adr182_content):
    """AC-5c: 조정 규칙 3항 사전 명문화 + 완료 Story 전수 재스캔 발의 금지."""
    _assert_probe(adr182_content, "AC-5c")


# ── 가드 3종 (RTM 비매핑 — 오라클 자기방어) ──


def _section_local_mutant(content: str, section_n: int, anchor: str) -> str:
    """주장 §결정 절 안의 앵커 출현만 제거한 사본 (절 밖 출현은 보존 — F-CR1-01 ③)."""
    s, e = _decision_section_span(content, section_n)
    return content[:s] + content[s:e].replace(anchor, "") + content[e:]


def test_adr182_clause_probe_red_on_removed_clause(adr182_content, tmp_path):
    """가드 1: 3축 대조군 — 미주입 GREEN ∧ 전역 mutant RED ∧ 절-국소 mutant RED + count==1.

    ⑴ 미주입 대조군 GREEN: 실 ADR 문서가 13 AC probe 전건 통과.
    ⑵ count==1 backstop (F-CR1-01 ④): 앵커 전건 문서-전역 출현 1회 — 다중 출현
       희석 (절 밖 동일 문자열이 절-국소 소멸을 가리는 형태) 재발을 형태로 봉인.
    ⑶ 전역 mutant RED (유지 축): 앵커 전 출현 제거 사본에서 해당 probe 실패.
    ⑷ 절-국소 mutant RED (F-CR1-01 ③): 주장 §결정 절 안의 출현만 제거한 사본에서
       해당 probe 실패 — probe 가 문서-전역 substring 탐색으로 퇴행하면 (절 밖
       출현이 남아 있는 한) 본 축이 RED 로 반증한다. 전역 축과 서로 맹점 보완.
    스크래치 사본: 대표 mutant 1본은 tmp_path (repo 밖 스크래치) 파일로도 실증 —
      로더 seam (`_load_adr`) 경유 경로 동일성 확인. repo 오염 0.
    """
    # ⑴ 미주입 대조군 GREEN (전건)
    for ac_id in PROBE_SPECS:
        assert not _probe(adr182_content, ac_id), f"대조군 GREEN 실패: {ac_id}"

    for ac_id, spec in PROBE_SPECS.items():
        for anchor in spec["anchors"]:
            # ⑵ count==1 구조적 backstop (문서-전역)
            n_occ = adr182_content.count(anchor)
            assert n_occ == 1, (
                f"{ac_id} 앵커 문서-전역 출현 {n_occ}회 (1회 계약 위반 — 다중 출현 희석 "
                f"채널. 처방 = 앵커의 절-유일 형태 정밀화): {anchor!r}"
            )
            # ⑶ 전역 mutant RED (in-memory 스크래치 사본)
            g_mutant = adr182_content.replace(anchor, "")
            assert _probe(g_mutant, ac_id), (
                f"전역 mutant GREEN — probe 미배선 결함: {ac_id} 앵커 제거에도 통과: {anchor!r}"
            )
            # ⑷ 절-국소 mutant RED (주장 절 안 출현만 제거 — 절 밖 보존)
            l_mutant = _section_local_mutant(adr182_content, spec["section"], anchor)
            assert _probe(l_mutant, ac_id), (
                f"절-국소 mutant GREEN — probe 정의역이 주장 절 밖으로 협착: "
                f"{ac_id} §결정 {spec['section']} 절 내 제거에도 통과: {anchor!r}"
            )

    # 대표 mutant 1본 — tmp_path 스크래치 파일 + 로더 경유 (repo 오염 0)
    rep_spec = PROBE_SPECS["AC-1a"]
    rep_anchor = rep_spec["anchors"][0]
    mutant_file = tmp_path / "adr182_mutant.md"
    mutant_file.write_text(
        _section_local_mutant(adr182_content, rep_spec["section"], rep_anchor),
        encoding="utf-8",
        newline="\n",
    )
    assert _probe(_load_adr(mutant_file), "AC-1a"), "파일 mutant RED 실패 (로더 seam)"


def test_cfp2999_story_section5_resolves_to_real_section():
    """가드 2 (이의 A 회귀): Story `## 5.` 헤딩 shadowing 하에서 실 §5 해석 판별.

    Story §1 verbatim 이 `## 5.` 등 h2 헤딩을 내포해 first-match slicing 이
    §1 내부 조각을 오선택 (vacuous PASS 기전 — ADR-182 정직 천장 / Change Plan §8.0).
    본 가드의 판별 쌍:
      양성: last-match slicing → 실 §5 (AC 표 `### 5.3` 포함) 도달.
      음성: first-match slicing → `### 5.3` 부재 (shadowing 실재 — 오선택 실증).

    Story 파일 = internal-docs repo 소재 (wrapper CI 비가시) → `CFP2999_STORY_PATH`
    env 주입 시 실행, 미주입 시 정직 skip. CI 상시 배선 = 게이트 slicing 정정과
    함께 후속 배선 Story (ADR-182 §편입 지시 5항) — 여기서는 심볼·로직을 선저작.
    """
    story_path = os.environ.get("CFP2999_STORY_PATH")
    if not story_path:
        pytest.skip(
            "CFP2999_STORY_PATH 미주입 — Story 파일은 internal-docs 소재. "
            "CI 상시 배선 = 후속 배선 Story (ADR-182 §편입 지시 5항)"
        )
    content = Path(story_path).read_text(encoding="utf-8")
    lines = content.splitlines()
    h2_5 = [i for i, ln in enumerate(lines) if re.match(r"^## 5\.", ln)]
    assert len(h2_5) >= 2, f"shadowing 전제 붕괴 — `## 5.` 헤딩 {len(h2_5)}개 (2+ 기대)"

    def _slice_from(idx: int) -> str:
        end = next(
            (j for j in range(idx + 1, len(lines)) if re.match(r"^## ", lines[j])),
            len(lines),
        )
        return "\n".join(lines[idx:end])

    first_sec = _slice_from(h2_5[0])
    last_sec = _slice_from(h2_5[-1])
    # 양성: last-match = 실 §5 (AC 표 보유)
    assert "### 5.3" in last_sec and "| AC-0 |" in last_sec, (
        "last-match 가 실 §5 (AC 표) 에 도달하지 못함"
    )
    # 음성: first-match = §1 verbatim 내부 조각 (AC 표 부재 — 오선택 실증)
    assert "### 5.3" not in first_sec, (
        "first-match 조각에 AC 표 존재 — shadowing 오선택 전제가 깨짐 (재판정 필요)"
    )


def test_ac_source_enum_matches_contract_enum():
    """가드 3 (이의 B 회귀): AC source 계약 enum 정합 + 결함 값 실행 기각.

    이의 B: Story §5.3 `source: analyst` 4건 ∉ 계약 enum — internal-docs `9a25c46a`
    기정정. 본 가드는 wrapper 측 계약 (`scripts/lib/ac_id.py`) 이 결함 값을 실제로
    기각하는지 실행으로 고정한다 (presence 상한 초과 — 양성 ∧ 음성 쌍):
      양성(기각): source="analyst" → 'source' enum 위반 메시지 발생 (술어 =
        `"'source'" in v and "enum" in v` — F-CL-004 정산: 다른 필드 메시지의
        무관 'source' 포함 오탐 경로 봉인, 양성/음성 술어 대칭화).
      음성(통과): source="derived"/"user" → 'source' 위반 0.
    """
    import ac_id  # conftest 가 scripts/lib 를 sys.path 주입

    assert set(ac_id.SOURCE_ENUM) == {"user", "derived"}, (
        f"계약 enum 이탈: {ac_id.SOURCE_ENUM} (ADR-145 §결정1(i) — user/derived 2값)"
    )
    assert "analyst" not in ac_id.SOURCE_ENUM

    base = {"id": "AC-0", "statement": "x", "tier": "normative"}
    # 양성: 결함 값 기각 (enum 위반 메시지로 좁힘 — F-CL-004)
    bad = ac_id.validate_ac_record({**base, "source": "analyst"})
    assert any("'source'" in v and "enum" in v for v in bad), (
        f"결함 값 'analyst' 미기각 (또는 메시지 형식 이탈): {bad}"
    )
    # 음성: 계약 값 통과
    for ok_val in ac_id.SOURCE_ENUM:
        ok = ac_id.validate_ac_record({**base, "source": ok_val})
        assert not any("'source'" in v for v in ok), f"정상 값 {ok_val} 오기각: {ok}"
