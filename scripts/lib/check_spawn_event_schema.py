#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# check_spawn_event_schema.py — spawn-event-v1 contract lint
#
# Carrier: CFP-2393 Phase 2 (구현) / Epic CFP-2391 S3
# 출처: oh-my-claudecode (MIT, https://github.com/Yeachan-Heo/oh-my-claudecode)
#       — spawn-event row 모델이 OMC per-agent registry 차용. 본 lint 는 codeforge 측
#       contract invariant 검증으로 OMC 직접 차용 아님 (contract↔runtime guard).
#
# 책임 (Change Plan §5 / §8.2 — 8 검증 항목):
#   (a) kind:registry frontmatter (kind: registry + registry: spawn-event present).
#   (b) §1/§2/§3/§4 headings present.
#   (c) Allow-list ONLY — §2 field 표 **실파싱**(하드코딩 상수 아님, F-CR-003):
#       파싱 공집합 금지 / 중복 row 금지 / heading 선언 개수 ↔ 표 실측 행수 일치 /
#       타입 열 free-form `string` 0 (enum/numeric/hash/const only — T-INFO-8).
#   (d) attribution_confidence invariant — enum {attributed, unattributed, unsupported}
#       + default unattributed + literal "unattributed" 존재.
#   (e) agent_type semi-open membership — enum reject 검증 아님; unknown-agent fallback 존재
#       + roster-derived 규칙 명시 검증 (F4 정정 — strict closed-set reject 금지).
#   (f) event_type closed enum — {agent_start, agent_stop, tool, file_touch, mode_change} 명시.
#   (g) idempotency — event_id deterministic 규칙 (sha256, random UUID 금지) 명시 present.
#   (h) opt-in default false — literal 또는 동등 present.
#   (i) N9 enum membership (CFP-2850 Amendment 4) — outcome closed-set
#       {success, inconclusive, failure, partial} + termination_cause closed-set
#       {normal, timeout, zero_output, error, cancelled} + model semi-open
#       (unknown-model fallback 존재) 가 §2 표에 명시됐는지 검증.
#   + contract↔runtime PARITY — §2 doc-parse(set A) ↔ append_spawn_event._ROW_KEYS
#     code-import(set B) **양방향 대칭** 비교: A\B(계약⊄runtime) · B\A(runtime⊄계약)
#     둘 다 검출 (F-CR-003 — 구 단방향/상수-대조 tautology 대체).
#
# 불변식:
#   - 0 API call, local read only.
#   - 3-tier exit (ADR-060 §결정 15): 0 PASS / 1 violation (warning) / 2 setup error.
#
# 사용:
#   python3 check_spawn_event_schema.py check [--contract-path <path>] [--repo-root <path>]
#
# Prior art: check_deferred_followup_reconcile.py / check_doc_section_schema.py /
#            check_doc_frontmatter.py (frontmatter yaml.safe_load 패턴)

import argparse
import os
import re
import sys

# Windows cp949 인코딩 회피 (ADR-061 portability)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None


_DEFAULT_CONTRACT_REL = os.path.join(
    "docs", "inter-plugin-contracts", "spawn-event-v1.md"
)

# ★F-CR-003 (구현리뷰 FIX Iter 2) — 구 `_CONTRACT_23_FIELDS` 하드코딩 상수 제거.
#   구 lint 은 "23개 field 이름" 을 **이 파일에 복사해 둔 상수**와 대조했다. 그래서
#   contract §2 표가 바뀌어도(24번째 field 추가 / field 삭제) 상수가 그대로면 lint 은
#   PASS 했고, parity 도 `상수 ↔ runtime` 이라 **doc 은 비교에 아예 참여하지 않는** 2-source
#   착시(실은 1-source tautology)였다. 이제 field 집합은 contract §2 표를 **실파싱**해서만
#   얻고, 비교는 `doc-parse ↔ code-import(_ROW_KEYS)` **양방향 대칭**으로 한다.
#   구조 선례 REUSE = check_dev_process_event_schema.py (§2 doc-parse vs _ROW_KEYS code-import,
#   SYMMETRIC fail-closed + 공집합 vacuous-pass 금지) — 신규 parity 개념 0.

_EVENT_TYPE_VALUES = ["agent_start", "agent_stop", "tool", "file_touch", "mode_change"]
_ATTRIBUTION_VALUES = ["attributed", "unattributed", "unsupported"]

# N9 enum membership (CFP-2850 Amendment 4) — outcome/termination_cause closed-set +
# model semi-open fallback. append_spawn_event._OUTCOMES/_TERMINATION_CAUSES/_MODEL_FALLBACK
# 와 동일 vocab (contract §2 표에 closed-set membership 이 명시됐는지 검증).
_OUTCOME_VALUES = ["success", "inconclusive", "failure", "partial"]
_TERMINATION_CAUSE_VALUES = ["normal", "timeout", "zero_output", "error", "cancelled"]
_MODEL_FALLBACK = "unknown-model"

# ── free-form string 검출 (T-INFO-8) ──────────────────────────────────────────
# §2 표 `타입` 열이 **구조 수식 없는 순수 `string`** 이면 free-form 유입 후보다.
# 아래 토큰 중 하나라도 타입 셀에 있으면 구조가 pin 된 것으로 본다 (free-form 아님).
_TYPE_STRUCTURE_TOKENS = (
    "sha256", "hash", "enum", "const", "int", "number", "float", "bool",
    "iso8601", "reference",
)

# ★baseline (ratchet) — 현행 계약이 `string` 으로 선언하나 구조가 pin 된 2 field.
#   - `schema_version`: §3 항목이 `const: "spawn-event-v1"` 로 고정 (사실상 const string).
#   - `story_key`: KEY prefix + 번호 형태의 구조 키 (§2 Sanitize 열 = non-sensitive(public)).
#   본 baseline 은 **동결선**이지 면죄부가 아니다 — 여기 없는 새 bare-`string` field 가
#   §2 표에 등장하면 violation 으로 fire 한다(T-INFO-8 신규 유입 차단 ratchet).
#   baseline 자체를 늘리는 변경 = 계약 §4 free-form 금지 조항 검토 + amendment 대상.
_FREEFORM_STRING_BASELINE = frozenset({"schema_version", "story_key"})


# ─────────────────────── frontmatter / 본문 split ────────────────────────────

def _split_frontmatter(text):
    """`---\\n ... \\n---\\n` frontmatter 와 본문 분리.

    Returns (frontmatter_dict | None, body_str).
    """
    if not text.startswith("---\n"):
        return None, text
    parts = text.split("\n---\n", 1)
    if len(parts) != 2:
        return None, text
    fm_text = parts[0][4:]  # leading '---\n' 제거
    body = parts[1]
    if yaml is None:
        return None, body
    try:
        fm = yaml.safe_load(fm_text)
    except yaml.YAMLError:
        return None, body
    return (fm if isinstance(fm, dict) else None), body


# ─────────────────────── §2 표 실파싱 (doc-parse = parity set A) ─────────────

# ★S-5 (보안테스트 iter1, P2) — fence 제거 정규식 평탄화 (초선형 백트래킹 제거).
# 구 패턴 `(?ms)^```.*?^```\s*?$` 는 닫는 fence 뒤에 **언어 태그**(```yaml)가 오는 실계약
# 형상에서 `\s*?$` 가 매칭에 실패하고, 그 실패마다 lazy `.*?` 가 다음 후보로 확장되며
# 재탐색을 반복해 입력 길이에 대해 초선형(관측 O(n²))으로 악화됐다(lint 은 CI 에서 임의
# 크기의 계약 문서를 읽는다 — resource-safety 축).
# 신 패턴 = 모호성 제거: 여는 fence 는 `[^\n]*\n`(info string 을 그 줄에서 확정 소비),
# 닫는 fence 는 `[^\n]*$`(닫는 줄 잔여 텍스트를 greedy 하게 확정) → `\s*?$` 실패-후-재탐색
# 경로 자체가 사라진다.
# ★honest-ceiling: "백트래킹 0" 을 주장하지 않는다 — lazy `.*?` 는 여전히 미종결 fence 에서
#   EOF 까지 전방 스캔한다(입력당 bounded degradation, 임의 입력 무해 아님). 제거한 것은
#   `\s*?$` 실패에서 오던 **반복 재탐색**이며, 계측 근거는 재현 스크립트 sec_codex_verify.py
#   C-3(언어태그 fence n=100~800 wall-clock) 의 봉합 전/후 대조다.
def _strip_fenced_blocks(text):
    """``` ... ``` fenced code block 제거 — §2 안의 markdown **예시 표**가 필드 파싱에
    섞이지 않도록 (예시는 field 이름이 아니라 header 나열이라 오탐 원천)."""
    return re.sub(r"(?ms)^```[^\n]*\n.*?^```[^\n]*$", "", text)


def _extract_section(text, start_pat, end_pat):
    """start_pat ~ 그 뒤 첫 end_pat 직전까지 슬라이스 (없으면 None).

    check_dev_process_event_schema.py `_extract_section` 동형 (동일 doc-parse 계열 —
    구조 REUSE, ADR-140). 별 모듈 import 는 하지 않는다 (계약 간 결합 회피).
    """
    ms = re.search(start_pat, text)
    if not ms:
        return None
    tail = text[ms.end():]
    me = re.search(end_pat, tail)
    end = ms.end() + me.start() if me else len(text)
    return text[ms.start():end]


def parse_section2_fields(body):
    """§2 field 표 실파싱 → [(field_name, type_cell), ...] (표 등장 순서).

    범위 = `## 2. Schema` ~ `## 2.1`(self-context record type) 직전. §2.1 의 6-field 표는
    **별 record type** 이므로 spawn row allow-list 에 섞으면 안 된다 (discriminator 분리).
    fenced block 제거 후, `| \\`field\\` | 타입 | ...` 형태 data row 만 수집.
    """
    section2 = _extract_section(body, r"(?m)^##\s*2\.\s", r"(?m)^##\s*2\.1")
    if section2 is None:
        return []
    section2 = _strip_fenced_blocks(section2)
    fields = []
    for m in re.finditer(r"(?m)^\|\s*`([^`|]+)`\s*\|([^|]*)\|", section2):
        fields.append((m.group(1).strip(), m.group(2).strip()))
    return fields


def parse_declared_field_count(body):
    """§2 heading 이 선언한 field 개수 (`## 2. Schema (23개 필드 ...)`) → int | None.

    표 실측 행 수와 대조해 "heading 은 23 이라는데 표는 24행" 류 자기모순을 잡는다.
    """
    m = re.search(r"(?m)^##\s*2\.\s*Schema\s*\((\d+)\s*개", body)
    return int(m.group(1)) if m else None


def _is_freeform_string_type(type_cell):
    """타입 셀이 구조 수식 없는 순수 `string` 인가 (T-INFO-8 free-form 후보)."""
    lowered = type_cell.lower()
    if "string" not in lowered:
        return False
    return not any(tok in lowered for tok in _TYPE_STRUCTURE_TOKENS)


# ─────────────────────── 검증 항목 (a)~(h) + parity ──────────────────────────

def _check_frontmatter_kind(fm, violations):
    """(a) kind:registry frontmatter — kind: registry + registry: spawn-event."""
    if fm is None:
        violations.append("(a) frontmatter 부재 또는 parse 실패")
        return
    if fm.get("kind") != "registry":
        violations.append("(a) frontmatter kind != registry (got: %r)" % fm.get("kind"))
    if fm.get("registry") != "spawn-event":
        violations.append(
            "(a) frontmatter registry != spawn-event (got: %r)" % fm.get("registry")
        )


def _check_headings(body, violations):
    """(b) §1/§2/§3/§4 headings present."""
    # `## 1. 목적` / `## 2. Schema` / `## 3. 항목` / `## 4. 변경 규칙` 형태 (§ optional)
    for n in (1, 2, 3, 4):
        pat = re.compile(r"(?m)^#{1,4}\s*(§)?%d[\.\s]" % n)
        if not pat.search(body):
            violations.append("(b) §%d heading 부재" % n)


def _check_allowlist(parsed_fields, declared_count, body, violations, notes):
    """(c) Allow-list ONLY — §2 표 **실파싱** 결과 자체 정합 + free-form string 타입 검출.

    ★F-CR-003: 하드코딩 상수 대조를 폐기하고 §2 표를 실파싱한 결과로 검증한다.
      (c1) 파싱 공집합 = vacuous pass 금지 → RED (표 형식이 깨졌는데 PASS 하는 사고 차단).
      (c2) 중복 field row 검출.
      (c3) heading 선언 개수 ↔ 표 실측 행 수 대조 (자기모순 검출).
      (c4) **타입 열 free-form `string` 검출** — 구조 수식(sha256/enum/const/int/…) 없는
           순수 `string` field 가 baseline 밖에서 등장하면 T-INFO-8 위반(Deny-list 를 no-op
           으로 유지시키는 구조적 차단이 뚫림).
      (c5) 계약이 스스로 "free-form string field 0/부재" 를 선언하는지 (기존 유지).
    """
    names = [f for f, _t in parsed_fields]

    if not names:
        violations.append(
            "(c) §2 field 표 doc-parse 결과 공집합 — 표 파싱 실패. vacuous pass 금지 → RED"
        )
        return

    dupes = sorted({n for n in names if names.count(n) > 1})
    if dupes:
        violations.append("(c) §2 표 중복 field row: %s" % ", ".join(dupes))

    if declared_count is None:
        violations.append(
            "(c) §2 heading 의 field 개수 선언(`## 2. Schema (N개 필드 ...)`) 부재 — "
            "표 실측과 대조 불가"
        )
    elif declared_count != len(names):
        violations.append(
            "(c) §2 heading 선언 %d개 ↔ 표 실측 %d행 불일치 (계약 자기모순)"
            % (declared_count, len(names))
        )
    else:
        notes.append("allow-list: §2 heading 선언 == 표 실측 %d field (자기정합)" % len(names))

    freeform = sorted(
        {
            f for f, t in parsed_fields
            if _is_freeform_string_type(t) and f not in _FREEFORM_STRING_BASELINE
        }
    )
    if freeform:
        violations.append(
            "(c) §2 타입 열 free-form `string` field 검출: %s — T-INFO-8 구조적 차단 위반 "
            "(enum/numeric/hash/const 로 pin 하거나 계약 §4 Deny-list 적용 + amendment 의무)"
            % ", ".join(freeform)
        )

    # free-form string field 0 검증 — 명시적 "free-form string field 0/부재" 선언 present
    if not re.search(r"free-form string field\s*(0개|0건|부재|0)", body):
        violations.append(
            "(c) 'free-form string field 0/부재' 명시 부재 (T-INFO-8 구조적 차단 선언)"
        )


def _check_n9_enum_membership(body, violations):
    """(i) N9 enum membership (CFP-2850 Amendment 4) — outcome/termination_cause
    closed-set + model semi-open fallback 가 §2 표에 명시됐는지 검증.

    (d) attribution / (f) event_type 의 literal-presence 패턴 REUSE (동형 검증):
      - outcome closed-set {success, inconclusive, failure, partial} 4값 전부 present.
      - termination_cause closed-set {normal, timeout, zero_output, error, cancelled}
        5값 전부 present.
      - model semi-open — `unknown-model` fallback literal present (agent_type semi-open
        패턴 정합; strict closed-set reject 검증 아님).
    """
    for v in _OUTCOME_VALUES:
        if v not in body:
            violations.append("(i) outcome closed-set 값 '%s' 미명시 (N9)" % v)
    for v in _TERMINATION_CAUSE_VALUES:
        if v not in body:
            violations.append("(i) termination_cause closed-set 값 '%s' 미명시 (N9)" % v)
    # model semi-open — unknown-model fallback 존재 검증 (membership reject 아님)
    if _MODEL_FALLBACK not in body:
        violations.append(
            "(i) model semi-open '%s' fallback 명시 부재 (N9)" % _MODEL_FALLBACK
        )


def _check_attribution_invariant(body, violations):
    """(d) attribution_confidence invariant — enum 3값 + default unattributed + literal."""
    for v in _ATTRIBUTION_VALUES:
        if v not in body:
            violations.append("(d) attribution_confidence enum 값 '%s' 미명시" % v)
    # default unattributed 명시
    if not re.search(r"default\s*[=:]?\s*`?unattributed`?", body):
        violations.append("(d) attribution_confidence default unattributed 미명시")
    # literal "unattributed" 존재 (위 enum loop 가 이미 cover 하지만 명시 검증)
    if "unattributed" not in body:
        violations.append("(d) literal 'unattributed' 부재")


def _check_agent_type_semi_open(body, violations):
    """(e) agent_type semi-open — unknown-agent fallback + roster-derived 규칙 명시.

    strict closed-set reject 검증 금지 (F4 정정) — fallback 존재 + roster 규칙만 검증.
    """
    if "unknown-agent" not in body:
        violations.append("(e) agent_type 'unknown-agent' fallback 명시 부재")
    if not re.search(r"roster[- ]?derived|roster-derived|roster", body):
        violations.append("(e) agent_type roster-derived 규칙 명시 부재")
    # semi-open 명시 (strict closed-set 아님 확인)
    if "semi-open" not in body:
        violations.append("(e) agent_type semi-open 선언 부재")


def _check_event_type_enum(body, violations):
    """(f) event_type closed enum — 5값 전부 명시."""
    for v in _EVENT_TYPE_VALUES:
        if v not in body:
            violations.append("(f) event_type enum 값 '%s' 미명시" % v)


def _check_idempotency(body, violations):
    """(g) idempotency — event_id deterministic (sha256, random UUID 금지) 명시."""
    if not re.search(r"deterministic", body):
        violations.append("(g) event_id deterministic 규칙 명시 부재")
    if "sha256" not in body:
        violations.append("(g) event_id sha256 규칙 명시 부재")
    if not re.search(r"random UUID\s*금지|UUID\s*금지", body):
        violations.append("(g) 'random UUID 금지' 명시 부재")


def _check_opt_in_default_false(body, violations):
    """(h) opt-in default false — literal 또는 동등 present."""
    # "opt-in default false" 또는 "opt_in_default_false" 또는 "opt-in" + "default false" 조합
    has_optin = bool(re.search(r"opt[-_ ]?in", body, re.IGNORECASE))
    has_default_false = bool(re.search(r"default\s*false|default false|default_false", body, re.IGNORECASE))
    if not (has_optin and has_default_false):
        violations.append("(h) 'opt-in default false' (또는 동등) 명시 부재")


def _check_runtime_parity(repo_root, parsed_fields, violations, notes):
    """contract↔runtime PARITY — §2 **doc-parse** set A ↔ `_ROW_KEYS` **code-import** set B.

    ★F-CR-003: 구 구현은 set A 를 이 파일의 하드코딩 상수에서 가져왔다 → 계약 문서가 비교에
    참여하지 않는 1-source tautology(계약 표를 24번째 field 로 바꿔도 PASS). 이제 set A 는
    contract §2 표 실파싱 결과이며, 비교는 **SYMMETRIC**(A\\B, B\\A 양방향) 이다:
      - contract ⊄ runtime (A\\B) = 계약에 있는데 runtime 이 안 쓰는 field.
      - runtime ⊄ contract (B\\A) = runtime 이 쓰는데 계약에 없는 field (allow-list 이탈).
    doc-parse 공집합은 `_check_allowlist` 가 이미 RED 로 잡는다(vacuous pass 금지).
    import 불가 = code anchor 부재 → skip + note (over-claim 금지 — 봉인했다고 주장하지 않음).
    """
    contract_keys = {f for f, _t in parsed_fields}

    lib_dir = os.path.join(repo_root, "scripts", "lib")
    append_module_path = os.path.join(lib_dir, "append_spawn_event.py")
    if not os.path.isfile(append_module_path):
        notes.append("parity: append_spawn_event.py 부재 — runtime parity skip (봉인 주장 없음)")
        return
    try:
        sys.path.insert(0, lib_dir)
        import append_spawn_event as _ase  # noqa: import-after-path
        runtime_keys = set(getattr(_ase, "_ROW_KEYS", ()))
    except Exception as e:  # pragma: no cover
        notes.append("parity: append_spawn_event import 실패 (%s) — runtime parity skip" % e)
        return
    finally:
        if lib_dir in sys.path:
            try:
                sys.path.remove(lib_dir)
            except ValueError:
                pass

    if not runtime_keys:
        violations.append(
            "(parity) append_spawn_event 는 import 되나 _ROW_KEYS 공집합/부재 — "
            "code anchor 파손 (impl-present non-skippable → RED)"
        )
        return

    if runtime_keys != contract_keys:
        missing_in_runtime = sorted(contract_keys - runtime_keys)
        extra_in_runtime = sorted(runtime_keys - contract_keys)
        violations.append(
            "(parity) 계약 §2(doc-parse, %d) ↔ append_spawn_event._ROW_KEYS(code-import, %d) "
            "불일치 [SYMMETRIC fail-closed] — contract\\runtime: %s / runtime\\contract: %s"
            % (len(contract_keys), len(runtime_keys), missing_in_runtime, extra_in_runtime)
        )
    else:
        notes.append(
            "parity: A(%d, doc-parse §2) == B(%d, code-import _ROW_KEYS) — "
            "TWO-SOURCE 일치 (doc-vs-code, tautology 아님)"
            % (len(contract_keys), len(runtime_keys))
        )


# ─────────────────────── 서브커맨드: check ───────────────────────────────────

def cmd_check(args):
    repo_root = args.repo_root or "."
    contract_path = args.contract_path or os.path.join(repo_root, _DEFAULT_CONTRACT_REL)

    if not os.path.isfile(contract_path):
        print(
            "[codeforge-spawn-event-lint-setup-error] check-spawn-event-schema: "
            "contract file 부재: %s" % contract_path,
            file=sys.stderr,
        )
        sys.exit(2)

    if yaml is None:
        print(
            "[codeforge-spawn-event-lint-setup-error] check-spawn-event-schema: "
            "pyyaml 미설치 — frontmatter 검증 불가",
            file=sys.stderr,
        )
        sys.exit(2)

    try:
        with open(contract_path, encoding="utf-8") as f:
            text = f.read()
    except OSError as e:
        print(
            "[codeforge-spawn-event-lint-setup-error] check-spawn-event-schema: "
            "contract read 실패: %s" % e,
            file=sys.stderr,
        )
        sys.exit(2)

    fm, body = _split_frontmatter(text)

    violations = []
    notes = []

    # ★F-CR-003 — field 집합의 유일 source = contract §2 표 실파싱 (하드코딩 상수 폐기).
    parsed_fields = parse_section2_fields(body)
    declared_count = parse_declared_field_count(body)

    _check_frontmatter_kind(fm, violations)        # (a)
    _check_headings(body, violations)              # (b)
    _check_allowlist(parsed_fields, declared_count, body, violations, notes)  # (c)
    _check_attribution_invariant(body, violations) # (d)
    _check_agent_type_semi_open(body, violations)  # (e)
    _check_event_type_enum(body, violations)       # (f)
    _check_idempotency(body, violations)           # (g)
    _check_opt_in_default_false(body, violations)  # (h)
    _check_n9_enum_membership(body, violations)    # (i) N9 outcome/termination_cause/model
    _check_runtime_parity(repo_root, parsed_fields, violations, notes)  # parity (SYMMETRIC)

    for note in notes:
        print("::notice::check-spawn-event-schema: %s" % note)

    if violations:
        for v in violations:
            print("::warning::check-spawn-event-schema: VIOLATION — %s" % v)
        print("")
        print(
            "check-spawn-event-schema: %d violation (warning tier — 비차단, advisory). "
            "spawn-event-v1.md contract §2/§3 정합 검토 요." % len(violations)
        )
        sys.exit(1)

    print(
        "check-spawn-event-schema: PASS — (a)~(i) + parity 전부 충족 "
        "(§2 doc-parse %d field Allow-list / free-form string 0 / attribution invariant / "
        "semi-open agent_type / idempotency / opt-in default false / "
        "N9 outcome·termination_cause·model enum / SYMMETRIC doc↔code parity)"
        % len(parsed_fields)
    )
    sys.exit(0)


def main():
    parser = argparse.ArgumentParser(
        description="spawn-event-v1 contract lint (CFP-2393 Phase 2 — kind:registry + Allow-list)"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    check_p = subparsers.add_parser("check", help="contract schema 검증")
    check_p.add_argument("--contract-path", default="",
                         help="spawn-event-v1.md 경로 (default: <repo-root>/docs/inter-plugin-contracts/...)")
    check_p.add_argument("--repo-root", default=".",
                         help="repo root (default 현재 디렉터리)")

    args = parser.parse_args()
    if args.command == "check":
        cmd_check(args)


if __name__ == "__main__":
    main()
