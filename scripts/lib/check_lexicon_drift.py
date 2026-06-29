#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
scripts/lib/check_lexicon_drift.py
CFP-2453 / ADR-091 Amendment 3 — consumer application-BC 단어 사전(lexicon) drift 검출 게이트
Python SSOT lint engine (warning tier, exit 3-tier).

archetype = scripts/lib/check_responsibility_marker_drift.py (CFP-2428 / ADR-131 Amendment 1) 의
1:1 clone (established 패턴 복제, parallel novel system 아님 — Story §1 제약 / ADR-131 Amd1 선례).
구조 verbatim 재사용: argparse --root / stdout·stderr UTF-8 reconfigure / yaml.safe_load /
3-tier exit / data-absence fail-open + honest ::notice:: / _discover_root 2-level up.
lexicon-specific 차이 = drift-rule predicate 만 (Change Plan §3.1).

입력 source = consumer repo 의 `docs/domain-knowledge/domain/<area>/lexicon.md` (responsibility-marker
의 project.yaml repo_topology 와 달리 lexicon.md frontmatter `kind: lexicon_relation` entry 집합).

기대 lexicon.md frontmatter shape (template plugins/codeforge-requirements/templates/domain-knowledge.md
`kind: lexicon_relation` sibling section 과 byte-consistent):
  ---
  kind: lexicon_relation
  title: <...>
  area: <area>
  topic_slug: lexicon
  status: active
  updated: YYYY-MM-DD
  relations:
    - term: <표기>
      relation: homonym | synonym | antonym
      conflict_with: <충돌 대상 term>          # relation=homonym/antonym 시
      usage_citations:                          # 1급 필드 (D5 forcing function)
        - "<file:line 또는 동등>"
      definition: <의미 정의>
    - ...
  ---

drift 구조 surface (Change Plan §3.1 — exit 1):
  (a) collision-candidate — 같은 surface-token(`term`)이 2+ entry 에 서로 다른 distinguishing
      meaning(서로 다른 definition) 으로 출현하는데 homonym 2-entry explicit-separate 구조(상호
      conflict_with 참조)로 선언되지 않음 → exit 1 ::warning:: collision-candidate.
      · ADR-091 §결정3 2-entry explicit-separate 전제: homonym 충돌쌍은 각각 별 entry + 상호
        conflict_with. 이 구조로 명시 선언된 동음이의 쌍은 collision 아님(정상 분리). 미선언
        중복 surface = collision-candidate (사람이 분리 의도했는지 기계는 모름 → WARN surface).
  (b) citation presence — relation=homonym entry 가 usage_citations 0건(부재/빈 리스트)
      → exit 1 ::warning:: citation-absent. **presence-check 만** (인용 의미 적합성 = DomainAgent abstain).
  (c) data-absence fail-open — lexicon.md 1개도 부재 → exit 0 + honest ::notice:: (silent exit 0 아님).

setup-error 게이팅 (exit 2 — fail-closed):
  · PyYAML 부재 / yaml.safe_load 파싱 실패 / read 권한 거부
  · entry 필수필드(term / relation) 키 부재 또는 malformed(타입 위반) / relation enum 위반
  · usage_citations 가 list 아님(지정 시)

PASS (exit 0):
  · lexicon.md 1+ 존재 + collision 0 + homonym entry 전수 citation 보유 → honest PASS marker.

decoupling 불변식 I-LEX-1 (Change Plan §3.1): lint = mechanical structure-check **only**
  (collision-candidate surface + citation presence). semantic homonym 판정("정말 다른 의미인가")
  = DomainAgent abstain (ADR-119). I-LEX-2: 자동 rename/action 0 (qualifier 권고).

honest-classification 의무 (Change Plan §8.4): data-absence/fail-open marker = PASS marker 와
  **구분되는 다른 문자열** (discriminating — fail-open ≠ valid-PASS). data-absence = ::notice::,
  valid-PASS = 평문 PASS line.

graceful-degradation (archetype 동형 2-tier 엄격 분리):
  data-absence(A) = fail-open(exit 0, honest ::notice:: — silent default 아님): lexicon.md 부재.
  setup-error(B) = fail-closed(exit 2): yaml 파싱 실패 / read 권한 거부 / 스키마 무효 / CLI 인자 형식 오류.

offline-first (gh 불요 — 입력 전부 repo 내 파일). ReDoS-safe (set/dict 비교 = regex-free).
read-only (verifier — write 0).

Usage:
  python3 check_lexicon_drift.py [--root <repo-root>]
    → repo-root 의 docs/domain-knowledge/domain/**/lexicon.md scan.
    --root 미지정 시: __file__ 기준 2-level up (scripts/lib/ -> scripts/ -> repo root).

Exit codes (ADR-060 §결정 5 3-tier — warning tier):
  0 = PASS (drift 0) OR data-absence honest no-op (fail-open)
  1 = drift 위반 1+ (collision-candidate / citation-absent — workflow continue-on-error 로 비차단, advisory)
  2 = SETUP error (yaml 파싱 실패 / 스키마 무효 / read 권한 거부 / CLI 인자 형식 오류) — fail-closed

ADR refs: ADR-091 Amendment 3 (carrier — consumer scope 승격 + INV-R6 BC-vocabulary-scope separation +
  INV-5 application-BC usage_citations 확장) / ADR-131 Amendment 1 (archetype 선례 — responsibility-marker-drift
  clone) / ADR-060 §결정 5/6 (warning-tier evidence framework) / ADR-061 §결정 1 (Python SSOT + thin wrapper) /
  ADR-119 (검사연극 금지 + abstention).
"""

import argparse
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # PyYAML 부재 = setup-error (B), main 에서 처리
    yaml = None

# Windows cp949 인코딩 문제 회피: stdout/stderr 를 UTF-8 강제 (ADR-061 portability)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


_LEXICON_GLOB = "docs/domain-knowledge/domain/**/lexicon.md"
_RELATION_ENUM = {"homonym", "synonym", "antonym"}

# honest-classification marker SSOT — PASS marker 와 fail-open marker 구분 의무 (Change Plan §8.4).
_PASS_MARKER = "lexicon drift OK"


# ─────────────── lexicon.md 후보 경로 해석 ──────────────────────────────────────────────────
def _resolve_lexicon_files(root):
    """root 하위 docs/domain-knowledge/domain/**/lexicon.md 전부(Path list) 반환, 부재 시 빈 list."""
    return sorted(root.glob(_LEXICON_GLOB))


# ─────────────── frontmatter 파싱 (setup-error — exit 2) ───────────────────────────────────
def _parse_frontmatter(path):
    """
    lexicon.md 의 leading `---\\n ... \\n---` frontmatter 를 yaml.safe_load.

    Returns: (doc|None, error_message|None).
      error_message 가 not None 이면 setup-error (exit 2).
    """
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return None, (
            "::error::check-lexicon-drift: setup-error — lexicon.md read 실패 (%s): %s "
            "(검증 로직 실행 불가, fail-closed exit 2)." % (path, exc)
        )

    if not text.startswith("---\n"):
        return None, (
            "::error::check-lexicon-drift: setup-error — lexicon.md (%s) frontmatter 부재 "
            "(leading '---' 없음, 스키마 무효 fail-closed exit 2)." % path
        )

    # 첫 '---' 이후 다음 '\n---\n' 까지가 frontmatter (archetype split 동형).
    parts = text.split("\n---\n", 1)
    fm_text = parts[0][4:]  # leading '---\n' 제거
    try:
        doc = yaml.safe_load(fm_text)
    except yaml.YAMLError as exc:
        return None, (
            "::error::check-lexicon-drift: setup-error — lexicon.md (%s) yaml.safe_load 파싱 "
            "실패: %s (fail-closed exit 2)." % (path, exc)
        )

    if not isinstance(doc, dict):
        return None, (
            "::error::check-lexicon-drift: setup-error — lexicon.md (%s) frontmatter 가 map 아님 "
            "(type=%s, 스키마 무효 fail-closed exit 2)." % (path, type(doc).__name__)
        )
    return doc, None


# ─────────────── entry 스키마 유효성 (setup-error — exit 2) ─────────────────────────────────
def _validate_relations_schema(relations, path):
    """
    relations[] 각 entry 필수필드 well-formedness 검사 (exit 2 SETUP).

    필수: term / relation(enum). 선택: conflict_with(str) / usage_citations(list) / definition(str).
    Returns: error_message|None — None 이면 스키마 유효.
    """
    if not isinstance(relations, list):
        return (
            "::error::check-lexicon-drift: setup-error — lexicon.md (%s) relations 가 list 아님 "
            "(type=%s, 스키마 무효 exit 2)." % (path, type(relations).__name__)
        )

    for idx, item in enumerate(relations):
        if not isinstance(item, dict):
            return (
                "::error::check-lexicon-drift: setup-error — lexicon.md (%s) relations[%d] 가 "
                "map 아님 (type=%s, 스키마 무효 exit 2)." % (path, idx, type(item).__name__)
            )

        term = item.get("term")
        if not isinstance(term, str) or not term.strip():
            return (
                "::error::check-lexicon-drift: setup-error — lexicon.md (%s) relations[%d].term "
                "키 부재 또는 비-string (스키마 무효 exit 2)." % (path, idx)
            )

        relation = item.get("relation")
        if not isinstance(relation, str) or relation not in _RELATION_ENUM:
            return (
                "::error::check-lexicon-drift: setup-error — lexicon.md (%s) relations[%d] "
                "(term '%s') relation 키 부재 또는 enum 위반 (허용: homonym/synonym/antonym, "
                "스키마 무효 exit 2)." % (path, idx, term)
            )

        # usage_citations — optional. 지정 시 list 의무 (malformed = exit2).
        if "usage_citations" in item and item["usage_citations"] is not None:
            if not isinstance(item["usage_citations"], list):
                return (
                    "::error::check-lexicon-drift: setup-error — lexicon.md (%s) relations[%d] "
                    "(term '%s') usage_citations 가 list 아님 (지정 시 list 의무, exit 2)."
                    % (path, idx, term)
                )

    return None


# ─────────────── drift 구조 surface (exit 1) ────────────────────────────────────────────────
def _check_lexicon_drift(relations, path):
    """
    (a) collision-candidate + (b) citation presence 검사. Returns: (messages[], violations:int).

    의미 추론 0 — 전부 관측 가능 구조적 사실(dict group-by surface / list 길이).
    """
    messages = []
    violations = 0

    # surface-token(term) 별 grouping.
    by_term = {}
    for item in relations:
        by_term.setdefault(item["term"], []).append(item)

    # (a) collision-candidate: 같은 term 이 2+ entry 에 서로 다른 definition 으로 출현하는데
    #     homonym 2-entry explicit-separate(상호 conflict_with) 구조로 선언되지 않음.
    collision_terms = []
    for term, entries in by_term.items():
        if len(entries) < 2:
            continue
        # 서로 다른 distinguishing meaning 인가 (definition 집합 크기 2+).
        defs = {e.get("definition") for e in entries}
        if len(defs) < 2:
            continue  # 같은 의미 중복 표기 = collision 아님 (의미 동일).
        # homonym explicit-separate 선언 여부 = reciprocal 정합 (CR-F1 — 단순 presence 아닌 상호 참조).
        #   ADR-091 §결정3 전제: 동음이의 충돌쌍은 각 의미를 별 entry + relation:homonym + **상호**
        #   conflict_with 로 명시 분리. 단일 surface-token group 의 정상 separate = 모든 entry 가
        #   homonym + conflict_with 가 같은 group 의 term(여기선 공유 surface = term 자신)을 가리킴.
        #   conflict_with 가 group 밖 비-상호 term(phantom/오타)을 가리키면 separate 의도 미성립
        #   → collision-candidate fall-through (presence-only 거짓-부정 차단, structure-check only).
        all_homonym = all(e.get("relation") == "homonym" for e in entries)
        reciprocal = all_homonym and all(
            isinstance(e.get("conflict_with"), str) and e.get("conflict_with") == term
            for e in entries
        )
        if reciprocal:
            continue  # 정상 explicit-separate homonym pair (상호 conflict_with) — collision 아님.
        collision_terms.append(term)

    if collision_terms:
        violations += 1
        messages.append(
            "::warning::check-lexicon-drift: FAIL (a)collision-candidate — 같은 표기(term)가 서로 "
            "다른 의미로 다중 출현하나 homonym 2-entry explicit-separate(상호 conflict_with) 구조 "
            "미선언 (term: %s, in %s). hint: ADR-091 §결정3 동음이의 2-entry separate — 각 의미를 "
            "별 entry + relation:homonym + 상호 conflict_with 로 명시 분리 (semantic 판정은 DomainAgent)."
            % (", ".join(sorted(collision_terms)), path.name)
        )

    # (b) citation presence: relation=homonym entry 가 usage_citations 0건.
    missing_cite = []
    for item in relations:
        if item.get("relation") != "homonym":
            continue
        cites = item.get("usage_citations")
        if not isinstance(cites, list) or len(cites) == 0:
            missing_cite.append(item["term"])

    if missing_cite:
        violations += 1
        messages.append(
            "::warning::check-lexicon-drift: FAIL (b)citation-absent — homonym entry 가 usage_citations "
            "0건 (term: %s, in %s). hint: D5 forcing function — 동음이의어 entry 는 사용처 인용(file:line "
            "또는 동등) 1+ 보유 의무 (ADR-091 §결정7 vocabulary theater 차단). presence-check only — "
            "인용 의미 적합성은 DomainAgent (ADR-119 abstain)."
            % (", ".join(sorted(set(missing_cite))), path.name)
        )

    return messages, violations


# ─────────────── 메인 검증 ───────────────────────────────────────────────────────────────────
def check_lexicon_drift(root):
    """
    root(repo root Path) 의 lexicon.md drift 검증.

    Returns: (exit_code, messages[])
      exit_code: 0=PASS or data-absence no-op / 1=drift / 2=setup-error
    """
    # ── data-absence(A): lexicon.md 1개도 부재 = fail-open EXIT 0 ──
    lexicon_files = _resolve_lexicon_files(root)
    if not lexicon_files:
        return 0, [
            "::notice::check-lexicon-drift: data-absence — lexicon.md 부재 "
            "(glob: %s). consumer application-BC 어휘 사전 미생성 = 검증 비대상 (bootstrap 미실행 "
            "또는 비-대상 repo). honest no-op EXIT 0 (silent default 아님)." % _LEXICON_GLOB
        ]

    # ── PyYAML 부재 = setup-error B = EXIT 2 ──
    if yaml is None:
        return 2, [
            "::error::check-lexicon-drift: setup-error — PyYAML 미설치 "
            "(yaml.safe_load 불가, fail-closed EXIT 2)."
        ]

    all_messages = []
    total_violations = 0

    for path in lexicon_files:
        doc, err = _parse_frontmatter(path)
        if err is not None:
            return 2, [err]  # setup-error 즉시 fail-closed.

        relations = doc.get("relations")
        if relations is None:
            # frontmatter 는 유효하나 relations 미주입 = 정책 공백(빈 사전) = PASS layer.
            all_messages.append(
                "::notice::check-lexicon-drift: lexicon.md (%s) relations 미주입 (빈 사전) — "
                "스키마 유효성만, 정책 공백 PASS." % path.name
            )
            continue

        schema_err = _validate_relations_schema(relations, path)
        if schema_err is not None:
            return 2, [schema_err]  # setup-error 즉시 fail-closed.

        msgs, viol = _check_lexicon_drift(relations, path)
        all_messages.extend(msgs)
        total_violations += viol

    if total_violations:
        all_messages.append("")
        all_messages.append(_ACTION_GUIDE)
        all_messages.append("")
        all_messages.append(
            "check-lexicon-drift: FAIL %d "
            "(warning tier — continue-on-error 로 비차단, advisory only)" % total_violations
        )
        return 1, all_messages

    all_messages.append(
        "check-lexicon-drift: PASS — %s ((a)collision-candidate 0 / (b)citation-absent 0, "
        "%d lexicon.md 전수 PASS, warning tier)" % (_PASS_MARKER, len(lexicon_files))
    )
    return 0, all_messages


_ACTION_GUIDE = (
    "[lexicon-drift] 강제 action 2택 (warning mode — merge 비차단, advisory):\n"
    "  ① FAIL 항목별 hint 에 따라 lexicon.md 정합 복원:\n"
    "     - (a)collision-candidate: 같은 표기 다중 의미를 별 entry + relation:homonym + 상호 conflict_with "
    "로 explicit-separate 분리 (ADR-091 §결정3). semantic 판정은 DomainAgent.\n"
    "     - (b)citation-absent: homonym entry 에 usage_citations(file:line 또는 동등) 1+ 추가 "
    "(D5 forcing function — ADR-091 §결정7).\n"
    "  ② hotfix-bypass:lexicon-drift label + audit comment (warning-tier 비차단이라 통상 불요)\n"
    "근거: ADR-091 Amendment 3 (CFP-2453) — consumer application-BC 단어 사전 drift 게이트. 기계(구조 "
    "대조 — collision-candidate surface + citation presence) vs 사람(의미정합 — DomainAgent semantic) "
    "판정 분리. 동음이의 semantic 판정('정말 다른 의미인가')은 DomainAgent 위임 (ADR-119 검사연극 금지 + "
    "abstention). I-LEX-2: 자동 rename/리네이밍 강제 0 (qualifier 권고)."
)


# ─────────────── main ──────────────────────────────────────────────────────────────────────
def _discover_root():
    # __file__ = <repo_root>/scripts/lib/check_lexicon_drift.py
    return Path(__file__).resolve().parent.parent.parent


def main(argv):
    parser = argparse.ArgumentParser(
        description="consumer application-BC lexicon drift 게이트 (CFP-2453 / ADR-091 Amendment 3)",
        add_help=True,
    )
    parser.add_argument(
        "--root",
        metavar="PATH",
        default=None,
        help="repo root (default: __file__ 기준 2-level up)",
    )
    try:
        args = parser.parse_args(argv[1:])
    except SystemExit:
        # argparse 형식 오류 = setup-error (B) = EXIT 2
        return 2

    root = Path(args.root).resolve() if args.root else _discover_root()

    if not root.is_dir():
        print(
            "::error::check-lexicon-drift: setup-error — repo root not a dir: %s "
            "(fail-closed EXIT 2)." % root,
            file=sys.stderr,
        )
        return 2

    exit_code, messages = check_lexicon_drift(root)
    for msg in messages:
        print(msg)
    return exit_code


if __name__ == "__main__":
    sys.exit(main(sys.argv))
