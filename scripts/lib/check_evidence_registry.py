#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""scripts/lib/check_evidence_registry.py
CFP-881 / ADR-060 Amendment 26 — evidence-checks-registry.yaml 구조 무결성 게이트 (warning-tier).

grep/awk 가 아니라 Python ``yaml.safe_load`` 로 ``docs/evidence-checks-registry.yaml``
(governance enforcement tier SSOT)를 파싱해 구조 무결성을 검증한다. CFP-583
``workflow-yaml-parse`` 와 동일한 ADR-060 warning→blocking 승격 프레임 답습 (blocking 승격은
별도 후속 CFP scope-out).

3계층 검증 모델 (파싱 성공은 필요조건이지 충분조건 아님):
  A 문법  — ``yaml.safe_load`` 파싱 성공 (tab 들여쓰기 / 문법 결함 → ScannerError → FAIL, AC-1)
  B 스키마 — (b) 최상위 allowlist 4종 exact + entries=list + 각 entry=name(non-empty str)-dict
             + current_tier ∈ enum4(case-sensitive) · (f) name 전역 unique (AC-2/3/4/13)
  C 중복키 — collecting ``_UniqueKeyLoader``(SafeLoader 상속, construct_mapping override)로
             (entry-name, key) dup locus 를 열거·surface (safe_load silent last-wins, AC-11/12)

계층 독립성: 상위가 하위를 대체 못 함 — A는 col-0 orphan 을 흡수, B는 중복키를 놓침
(dict 이미 붕괴), C는 collecting loader 로만 열거. 세 계층 모두 필요.

정직 상한 (ADR-151 §결정7 상속): 본 게이트는 구조(structure)만 검증한다 — tier 값의 정책
적절성(policy-correctness)이나 anomaly/inventory drift(ADR-060 §결정25 직교)는 검증하지 않는다.
exact-key 중복만 포착(semantic 중복 미검출). ``safe_load`` 는 alias 를 materialize 하므로
alias-bomb 은 bounded degradation(면역 아님, ADR-082 Amд38). "완전 봉인"·"DoS-safe" hard-claim 부재.

loader-safety 3 invariant (ADR-070/ADR-082 §7.2):
  (1) base = ``yaml.SafeLoader`` 유지 (Loader/FullLoader/UnsafeLoader swap 금지)
  (2) override 는 add_constructor 0 (dup-key guard + super().construct_mapping delegation 만)
  (3) key 는 ``self.construct_object(key_node)`` (안전 registry) 경유
  → ``!!python/object/apply`` 등 임의객체 tag = ConstructorError BLOCKED (AC-14, F-SEC).

Exit code 3-tier (ADR-060 Amendment 2 §결정 15):
  0 = PASS (구조 무결)
  1 = validation FAIL (A/B/C/(f) 위반 — dup-key surface 포함, ScannerError 포함)
  2 = meta-error (registry 파일 부재 / PyYAML·python 부재[.sh pre-guard])

Usage:
  python3 check_evidence_registry.py [--registry <path>]
    default registry = <GITHUB_WORKSPACE|.>/docs/evidence-checks-registry.yaml

reuse-before-write (ADR-061 / RefactorAgent): ``load_registry_entries`` +
``DEFAULT_REGISTRY_REL`` 를 check_deferred_followup_reconcile 에서 import 재사용
(별도 registry loader·path 리터럴 유입 금지). ``_UniqueKeyLoader`` = 본 파일 유일 소비자
(repo 전역 dup-key loader 0건 — 2nd consumer 발생 시 scripts/lib/ 승격, 조기 추상화 회피).

ADR refs: ADR-060 / ADR-151 / ADR-061 / ADR-082 Amд38 / ADR-005 / ADR-119 / ADR-127
"""

import argparse
import os
import sys

import yaml

# 재사용 SSOT import (sys.path.insert — gen_deferred_followup_baseline.py 관용구 답습).
# check_deferred_followup_reconcile.py 는 동일 scripts/lib/ 디렉터리에 위치.
_LIB_DIR = os.path.dirname(os.path.abspath(__file__))
if _LIB_DIR not in sys.path:
    sys.path.insert(0, _LIB_DIR)

from check_deferred_followup_reconcile import (  # noqa: E402  reuse-before-write
    DEFAULT_REGISTRY_REL,
    load_registry_entries,
)

# Windows cp949 인코딩 회피: stdout/stderr 를 UTF-8 강제 (ADR-061 portability — 한글 entry
# name/description print 시 mojibake 차단).
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


# ─────────────────────── 스키마 상수 (closed-set) ────────────────────────────

# (b) 최상위 key allowlist — 정확히 이 4종만 허용 (col-0 orphan = allowlist 이탈로 검출)
ALLOWED_TOP_KEYS = {"schema_version", "introduced_by", "last_updated", "entries"}

# current_tier enum (case-sensitive) — 계약 evidence-check-registry-v1 §3
TIER_ENUM = {"warning", "blocking-on-pr", "blocking-on-merge", "hotfix-bypass"}


# ─────────────────────── collecting UniqueKeyLoader (계층 C) ──────────────────

class _UniqueKeyLoader(yaml.SafeLoader):
    """SafeLoader 상속 collecting loader — mapping node 마다 exact-key 중복을 (entry-name, key)
    tuple 로 열거·수집 (raise-on-first 아님 — 전 locus 열거·entry 귀속 위해 collecting; §3.2).

    loader-safety invariant: base = SafeLoader 유지, add_constructor 0, key 는
    construct_object 경유 → 임의객체 tag(!!python/object/apply 등)는 stock SafeLoader
    동일하게 ConstructorError 로 차단 (construct_mapping 은 key/value pairing 만 관장 —
    tag-safety layer 무손상).

    line-number 기반 locus-id 금지 (무관 편집 churn = born-brittle) — entry-name 귀속.
    """

    def __init__(self, stream):
        super().__init__(stream)
        # dup locus 수집 버킷 — get_single_data() 후 loader 인스턴스에서 읽는다.
        self.duplicate_loci = []

    def construct_mapping(self, node, deep=False):
        # 이 mapping node 수준의 exact-key 중복 검출 (sibling 스캔).
        entry_name = self._sibling_name(node)
        seen = set()
        for key_node, _value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            # 해시 불가 key 는 super 가 별도 처리 — 여기서는 dup 판정만.
            try:
                if key in seen:
                    self.duplicate_loci.append((entry_name, key))
                else:
                    seen.add(key)
            except TypeError:
                # unhashable key (drop — super().construct_mapping 이 ConstructorError 처리)
                pass
        # 실제 dict 구성 + tag-safety 는 stock SafeLoader 에 위임 (last-wins, 안전).
        return super().construct_mapping(node, deep=deep)

    @staticmethod
    def _sibling_name(node):
        """동일 mapping node 안 ``name:`` scalar 값 (entry-name 귀속). 부재 시 None."""
        for key_node, value_node in node.value:
            if (
                getattr(key_node, "value", None) == "name"
                and isinstance(value_node, yaml.ScalarNode)
            ):
                return value_node.value
        return None


def _parse_unique(path):
    """registry 를 collecting ``_UniqueKeyLoader`` 로 파싱.

    Returns: (data, dup_loci) — data = 전체 top-level 문서, dup_loci = 정렬된 고유
    (entry-name, key) 리스트.
    Raises: yaml.YAMLError (ScannerError/ParserError/ConstructorError 포함) / OSError.
    """
    with open(path, encoding="utf-8") as f:
        loader = _UniqueKeyLoader(f)
        try:
            data = loader.get_single_data()
        finally:
            dup = list(loader.duplicate_loci)
            loader.dispose()
    dup_loci = sorted(set(dup), key=lambda t: (str(t[0]), str(t[1])))
    return data, dup_loci


# ─────────────────────── 계층 B: 스키마 단정 (pure — file IO 0) ────────────────

def validate_registry(data):
    """파싱된 top-level 문서(data)에 계층 B 스키마 단정을 적용해 problem 문자열 리스트 반환.

    순수 함수 (file IO 0) — self-test 가 hand-built dict 로 직접 구동. 빈 리스트 = 계층 B PASS.

    검사: (b) 최상위 allowlist 이탈(orphan) / entries=list / 각 entry=name(non-empty str)-dict
          / current_tier enum(case-sensitive, 존재 시) · (f) name 전역 unique
          · vacuous(entries 부재/빈) non-PASS.
    dup-key(계층 C)는 load_and_validate 가 loader 결과로 별도 병합 (data-only 로는 불가).
    """
    problems = []

    if not isinstance(data, dict):
        problems.append(
            "최상위 문서가 mapping(dict) 아님 (None/scalar/list-top — vacuous 포함): %s"
            % type(data).__name__
        )
        return problems

    # (b) 최상위 allowlist — 이탈 키 = col-0 orphan 승격 의심
    for key in sorted(k for k in data.keys() if k not in ALLOWED_TOP_KEYS):
        problems.append(
            "최상위 allowlist 이탈 키 (col-0 orphan 의심 — allowlist=%s): %s"
            % (sorted(ALLOWED_TOP_KEYS), key)
        )

    if "entries" not in data:
        problems.append("최상위 entries 키 부재 (vacuous-PASS 회피 — validated 0 entries)")
        return problems

    entries = data["entries"]
    if not isinstance(entries, list):
        problems.append("entries 가 list 아님 (type=%s)" % type(entries).__name__)
        return problems

    if len(entries) == 0:
        problems.append("entries 빈 리스트 (vacuous-PASS 회피 — validated 0 entries)")
        return problems

    # per-entry 단정 + (f) name 전역 unique
    seen_names = {}
    for idx, entry in enumerate(entries):
        loc = "entries[%d]" % idx
        if not isinstance(entry, dict):
            problems.append("%s 가 mapping(dict) 아님 (type=%s)" % (loc, type(entry).__name__))
            continue

        name = entry.get("name")
        if "name" not in entry:
            problems.append("%s 에 name 키 부재" % loc)
        elif not isinstance(name, str) or name.strip() == "":
            problems.append("%s name 이 non-empty str 아님 (값=%r)" % (loc, name))
        else:
            if name in seen_names:
                problems.append(
                    "entry name 전역 중복: %r (entries[%d] ↔ entries[%d])"
                    % (name, seen_names[name], idx)
                )
            else:
                seen_names[name] = idx

        # current_tier enum (존재 시 — case-sensitive). 부재는 AC-4 밖(over-validation 회피).
        if "current_tier" in entry:
            tier = entry["current_tier"]
            if tier not in TIER_ENUM:
                problems.append(
                    "%s (name=%s) current_tier enum 이탈 (case-sensitive, enum=%s): %r"
                    % (loc, name, sorted(TIER_ENUM), tier)
                )

    return problems


# ─────────────────────── Result + load_and_validate ──────────────────────────

class RegistryResult:
    """게이트 판정 결과 컨테이너 — main() 이 exit code 3-tier 로 매핑."""

    def __init__(self):
        self.meta_message = None   # 설정 시 exit 2 (meta-error)
        self.parse_error = None    # 설정 시 exit 1 (문법/construct 실패)
        self.problems = []         # 계층 B schema problem 리스트 → 비어있지 않으면 exit 1
        self.dup_loci = []         # (entry-name, key) — 계층 C surface → 비어있지 않으면 exit 1
        self.entry_count = 0
        self.data = None

    @property
    def ok(self):
        return (
            self.meta_message is None
            and self.parse_error is None
            and not self.problems
            and not self.dup_loci
        )

    @property
    def exit_code(self):
        if self.meta_message is not None:
            return 2
        if self.parse_error is not None or self.problems or self.dup_loci:
            return 1
        return 0


def _one_line(exc):
    return " ".join(str(exc).split())


def load_and_validate(path):
    """registry 파일 경로를 파싱·검증해 RegistryResult 반환.

    - 파일 부재 → meta-error (exit 2).
    - 문법/construct 실패(tab ScannerError/AC-1, python tag ConstructorError) → parse_error (exit 1).
    - 계층 B schema 위반 + 계층 C dup-key surface → problems/dup_loci (exit 1).
    """
    result = RegistryResult()

    # 계층 A + 기본 구조 gate — 재사용 load_registry_entries (established 오류 taxonomy).
    try:
        load_registry_entries(path)
    except FileNotFoundError:
        result.meta_message = "registry 파일 부재: %s" % path
        return result
    except yaml.YAMLError as exc:
        # ScannerError(tab/AC-1) / ConstructorError(python tag) 등 malformed content
        result.parse_error = "registry YAML parse/construct 실패: %s" % _one_line(exc)
        return result
    except ValueError:
        # root 가 dict 아님 / entries 가 list 아님 — validate_registry 가 상세 problem 방출.
        # (full-parse 로 fall-through)
        pass

    # 계층 B + C — full-document collecting 파싱.
    try:
        data, dup_loci = _parse_unique(path)
    except yaml.YAMLError as exc:
        result.parse_error = "registry YAML parse/construct 실패: %s" % _one_line(exc)
        return result

    result.data = data
    result.dup_loci = dup_loci
    result.problems = validate_registry(data)
    entries = data.get("entries") if isinstance(data, dict) else None
    result.entry_count = len(entries) if isinstance(entries, list) else 0
    return result


# ─────────────────────── main (exit 3-tier 매핑) ─────────────────────────────

def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    parser = argparse.ArgumentParser(
        description="evidence-checks-registry.yaml 구조 무결성 게이트 "
        "(CFP-881 / ADR-060 Amendment 26 — yaml.safe_load strict-verify, warning-tier)"
    )
    parser.add_argument(
        "--registry",
        default=None,
        help="registry yaml 경로 (default: <GITHUB_WORKSPACE|.>/docs/evidence-checks-registry.yaml)",
    )
    args = parser.parse_args(argv)

    root = os.environ.get("GITHUB_WORKSPACE", ".")
    registry_path = args.registry or os.path.join(root, DEFAULT_REGISTRY_REL)

    result = load_and_validate(registry_path)

    if result.meta_message is not None:
        print(
            "::error::evidence-registry-structure meta-error — %s (PyYAML/python 부재 = .sh pre-guard)"
            % result.meta_message,
            file=sys.stderr,
        )
        return 2

    if result.parse_error is not None:
        print(
            "::error::evidence-registry-structure FAIL — %s" % result.parse_error,
            file=sys.stderr,
        )

    for entry_name, key in result.dup_loci:
        print(
            "::error::evidence-registry-structure duplicate-key — entry=%s key=%s "
            "(safe_load silent last-wins — collecting UniqueKeyLoader surface)"
            % (entry_name, key),
            file=sys.stderr,
        )

    for problem in result.problems:
        print("::error::evidence-registry-structure — %s" % problem, file=sys.stderr)

    verdict = "PASS" if result.ok else "FAIL"
    print(
        "evidence-registry-structure %s — validated %d entries" % (verdict, result.entry_count)
    )
    return result.exit_code


if __name__ == "__main__":
    sys.exit(main())
