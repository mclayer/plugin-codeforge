#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""S-5 proof-reference — `check_spawn_event_schema._strip_fenced_blocks` 평탄화 회귀 방어.

보안 lane iter1 S-5 로 fence 제거 정규식이 평탄화됐다:

    구: (?ms)^```.*?^```\\s*?$
    신: (?ms)^```[^\\n]*\\n.*?^```[^\\n]*$

구 패턴은 **닫는 fence 뒤에 언어 태그**(```yaml)가 오는 실계약 형상에서 `\\s*?$` 가 매칭에
실패하고, 그 실패마다 lazy `.*?` 가 다음 후보로 확장되며 재탐색을 반복했다. 결과는 두 가지
동시 손상이다 — ① **기능**: 언어 태그가 붙은 닫는 fence 를 아예 못 지워 예시 표의 행이
필드 파싱에 섞인다(오탐), ② **자원**: 입력 길이에 대해 초선형으로 악화된다(lint 은 CI 에서
임의 크기의 계약 문서를 읽는다).

승격 이유: 그 대조가 일회성 임시 스크립트에만 있었다. 임시 스크립트는 다음 사람이 되돌릴 때
아무 저항도 하지 않으므로, **되돌리면 RED 가 되는 자산**으로 고정한다.

★honest-ceiling (ADR-151 §결정7 / 본 agent resource-safety claim 규율):
  본 파일은 "ReDoS-safe" 도 "catastrophic backtracking 0" 도 **주장하지 않는다**. 신 패턴의
  lazy `.*?` 는 미종결 fence 에서 여전히 EOF 까지 전방 스캔한다(입력당 bounded degradation —
  임의 입력 무해가 아님). 제거된 것은 `\\s*?$` 실패에서 오던 **반복 재탐색** 하나이며,
  아래 wall-clock 상한이 그 제거의 proof-reference 다(검출력 봉인 주장 아님).

측정 맥락 (작성 시점 실측, 참고값 — assert 대상 아님):
    언어태그 fence n=100/200/400/800/1600  →  구: 0.010 / 0.052 / 0.194 / 0.570 / 1.837s
                                              신: 0.00024 / 0.00025 / 0.00046 / 0.00076 / 0.0009s
    bare fence 계열은 신·구 동일(~1x) — 이번 변경은 언어태그 축에만 작용한다.

규율: production 정규식을 테스트 안에 **재구현하지 않는다** — 실제 `_strip_fenced_blocks`
함수를 import 해 호출한다(tautology 금지, `test_check-semantic-staleness-sentinel-redos.sh`
선례). 아래 `_LEGACY_PATTERN` 만 예외로 하드코딩하는데, 이것은 production 사본이 아니라
**동결된 과거 baseline**(비교 기준)이기 때문이다.
"""

from __future__ import annotations

import re
import time

import check_spawn_event_schema as schema  # tests/scripts/conftest.py 가 scripts/lib 주입

# 동결된 과거 패턴 — production 사본 아님(비교 기준선). 갱신 금지.
_LEGACY_PATTERN = re.compile(r"(?ms)^```.*?^```\s*?$")

_F = "`" * 3  # fence 리터럴 (소스 안 triple-backtick 혼동 회피)

REPO_ROOT_CONTRACT_REL = ("docs", "inter-plugin-contracts", "spawn-event-v1.md")


def _section2_fixture(closing_tag):
    """§2 형상 fixture — fenced **예시 표**가 실 필드 표와 섞여 있는 실제 계약 배치.

    closing_tag="yaml" 이면 닫는 fence 가 ```yaml (S-5 결함이 드러나는 실계약 형상),
    "" 이면 bare 닫는 fence (신·구가 합치하는 대조 형상).
    """
    return (
        "## 2. Schema (2개 필드)\n\n"
        "| 필드 | 타입 |\n|---|---|\n"
        "| `event_id` | string |\n"
        "| `story_key` | string |\n\n"
        "예시:\n\n"
        + _F + "yaml\n"
        "| `EXAMPLE_ONLY` | header |\n"
        "| `NOT_A_FIELD` | header |\n"
        + _F + closing_tag + "\n\n"
        "## 2.1 self-context\n"
        "| `other_record` | string |\n"
    )


# ─────────────── ① 기능: 언어태그 닫는 fence 도 예시 표를 걷어낸다 ───────────────


def test_fence_strip_excludes_example_rows_when_closing_fence_has_language_tag():
    """(disc) 닫는 fence 에 언어 태그가 붙어도 예시 표 행이 **필드로 새지 않는다**.

    이것이 S-5 의 기능 축이다. 구 패턴은 이 형상에서 fence 를 통째로 못 지워
    `EXAMPLE_ONLY`/`NOT_A_FIELD` 가 §2 필드 목록에 섞여 들어갔다 — 계약 lint 이
    "선언 개수와 실제 개수가 다르다" 며 엉뚱한 곳을 가리키게 된다.
    discriminating: 정규식을 구 패턴으로 되돌리면 예시 2행이 유입돼 RED.
    """
    parsed = [name for name, _ in schema.parse_section2_fields(_section2_fixture("yaml"))]

    # 측정 assertion (a): 실 필드 2개만 — 예시 행 유입 0
    assert parsed == ["event_id", "story_key"], (
        f"fenced 예시 표가 필드 파싱에 유입됨(또는 실 필드 소실) — got {parsed!r}. "
        f"닫는 fence 의 언어 태그를 처리하지 못하는 패턴으로 회귀했을 가능성."
    )
    # (b): 예시 전용 토큰이 어떤 형태로도 남지 않았다
    for leaked in ("EXAMPLE_ONLY", "NOT_A_FIELD"):
        assert leaked not in parsed, f"예시 전용 행 {leaked!r} 이 필드로 승격됨"


def test_legacy_pattern_would_leak_example_rows_baseline():
    """(baseline 대조) 동결된 구 패턴은 같은 fixture 에서 **실제로 샌다** — 위 테스트가 vacuous 아님.

    "고쳤다" 를 주장하려면 고치기 전이 실제로 틀렸음을 같은 자리에서 보여야 한다.
    이 테스트가 통과한다는 것은 fixture 가 결함을 재현하는 형상이라는 뜻이고, 따라서
    바로 위 테스트의 통과가 우연이 아님을 보증한다.
    """
    fixture = _section2_fixture("yaml")
    section2 = schema._extract_section(fixture, r"(?m)^##\s*2\.\s", r"(?m)^##\s*2\.1")
    legacy_stripped = _LEGACY_PATTERN.sub("", section2)
    legacy_names = [
        m.group(1) for m in re.finditer(r"(?m)^\|\s*`([^`|]+)`\s*\|([^|]*)\|", legacy_stripped)
    ]

    # 측정 assertion: 구 패턴에서는 예시 행이 필드로 새어 들어온다 (결함 재현 확인)
    assert "EXAMPLE_ONLY" in legacy_names and "NOT_A_FIELD" in legacy_names, (
        f"구 패턴이 이 fixture 에서 새지 않음 — fixture 가 S-5 결함 형상을 재현하지 못한다"
        f"(위 disc 테스트가 vacuous 해짐). legacy_names={legacy_names!r}"
    )


# ─────────────── ② 동등성: 기존 형상에서는 신·구가 같은 결과 ───────────────


_EQUIVALENCE_CORPUS = {
    "no-fence": "| `a` | int |\n| `b` | str |\n",
    "single-bare": "before\n" + _F + "\n| `x` | int |\n" + _F + "\nafter\n",
    "multi-bare": "a\n" + _F + "\nq\n" + _F + "\nb\n" + _F + "\nr\n" + _F + "\nc\n",
    "table-inside": "## 2\n| `real` | int |\n" + _F + "\n| `ex` | header |\n" + _F
                    + "\n| `real2` | str |\n",
    "no-trailing-newline": "x\n" + _F + "\ny\n" + _F,
    "unterminated-fence": "x\n" + _F + "yaml\ny\nz\n",
    "indented-fence": "x\n   " + _F + "\ny\n   " + _F + "\nz\n",
    "blank-lines-in-block": "a\n" + _F + "\n\n\n" + _F + "\nb\n",
}


def test_fence_strip_matches_legacy_on_pre_existing_shapes():
    """(reg) bare fence / 미종결 / 들여쓰기 등 **기존 형상**에서는 신·구 결과가 byte-exact 동일.

    평탄화는 언어태그 축만 고치는 것이고, 그 밖의 문서에서 결과가 달라지면 조용한
    파싱 회귀가 된다(예시 표가 아니라 실 필드를 지워버리는 쪽이 더 위험하다).
    """
    diverged = {}
    for name, text in _EQUIVALENCE_CORPUS.items():
        new = schema._strip_fenced_blocks(text)
        old = _LEGACY_PATTERN.sub("", text)
        if new != old:
            diverged[name] = (old, new)

    # 측정 assertion: 기존 형상 전건 동일 (변경 영향면이 언어태그 축에 한정됨)
    assert not diverged, (
        f"평탄화가 기존 fence 형상의 결과를 바꿨다 — 영향면이 언어태그 축을 넘었다: "
        f"{ {k: (v[0][:60], v[1][:60]) for k, v in diverged.items()} }"
    )


def test_real_contract_section2_field_count_matches_declaration(request):
    """(reg) 실 계약 문서 §2 파싱 결과가 선언 개수와 여전히 일치 — 파이프라인 무손상.

    합성 fixture 만으로는 "실제 계약에서도 잘 도는가" 를 말할 수 없다. 개수를 상수로
    박지 않고 **문서가 스스로 선언한 값**과 대조한다(계약이 23→24 로 늘어도 유효).
    """
    repo_root = request.config.rootpath
    contract = repo_root.joinpath(*REPO_ROOT_CONTRACT_REL)
    assert contract.is_file(), f"계약 문서 부재: {contract}"

    text = contract.read_text(encoding="utf-8")
    _, body = schema._split_frontmatter(text)
    parsed = schema.parse_section2_fields(body)
    declared = schema.parse_declared_field_count(body)

    assert declared, f"§2 heading 이 field 개수를 선언하지 않음 — 대조 기준 부재 (declared={declared!r})"
    # 측정 assertion: 실 계약에서 파싱 개수 == 선언 개수
    assert len(parsed) == declared, (
        f"실 계약 §2 파싱 {len(parsed)}개 != 선언 {declared}개 — fence 제거/표 파싱 회귀. "
        f"parsed={[n for n, _ in parsed]!r}"
    )


# ─────────────── ③ 자원: 언어태그 fence 가 많아도 시간이 터지지 않는다 ───────────────

# 상한은 **머신 의존이 아니도록 넉넉히** 잡는다: 평탄화본은 이 입력에서 ~0.002s 라
# 2.0s 는 약 1000배 여유다(flaky 0). 구 패턴은 같은 입력에서 초 단위(n=1600 에서 1.8s,
# 초선형이므로 n=3200 은 그 몇 배)로 이 상한을 확실히 넘는다 — 되돌리면 RED.
_PERF_FENCE_COUNT = 3200
_PERF_CEILING_SECONDS = 2.0


def test_fence_strip_completes_within_bounded_time_on_language_tagged_fences():
    """(proof-ref) 언어태그 fence 가 많은 입력에서 fence 제거가 **합리적 시간 안에** 끝난다.

    비율(907배 등)은 머신마다 달라 assert 하지 않는다 — 병리적 재탐색이 되살아났는지만
    넉넉한 wall-clock 상한으로 잡는다. 이 상한이 production 주석의 resource-safety 서술에
    대한 proof-reference 다.
    ★주장 범위: "임의 입력에 대해 안전" 이 아니라 "이 형상에서 bounded" 까지만(honest-ceiling).
    """
    payload = (_F + "yaml\n" + "x" * 40 + "\n" + _F + "yaml\n") * _PERF_FENCE_COUNT
    # fixture 실재 확인 (vacuous 방지): 실제로 큰 입력이고 언어태그 fence 형상이다
    assert len(payload) > 100_000, f"perf fixture 가 너무 작음: {len(payload)} chars"

    started = time.perf_counter()
    stripped = schema._strip_fenced_blocks(payload)
    elapsed = time.perf_counter() - started

    # 측정 assertion (a): 넉넉한 상한 안에 완료 (병리적 재탐색 재발 시 초과)
    assert elapsed < _PERF_CEILING_SECONDS, (
        f"언어태그 fence {_PERF_FENCE_COUNT}개({len(payload)} chars) 제거에 {elapsed:.3f}s 소요 — "
        f"상한 {_PERF_CEILING_SECONDS}s 초과. `\\s*?$` 실패-후-재탐색 경로가 되살아났을 가능성."
    )
    # (b): 빨라진 대신 일을 안 한 것이 아님 — fence 가 실제로 제거됐다
    assert _F not in stripped, "fence 가 제거되지 않았다 — 상한 통과가 no-op 때문일 수 있음"
    assert stripped.strip() == "", (
        f"전량 fence 입력인데 잔여물이 남음: {stripped[:120]!r}"
    )
