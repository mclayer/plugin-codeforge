#!/usr/bin/env python3
"""check_salvage_bundle.py — salvage 번들 · side-effect 원장 · 착지 직전 스캔 SSOT (CFP-2984 Phase 2).

ADR-061 §결정 1: Python entry-point + thin bash wrapper(scripts/check-salvage-bundle.sh).

정본(SSOT) — 본 모듈은 아래 문서의 규범을 **구현만** 하며 재정의하지 않는다:
  - ADR-179 §결정 2      : salvage 번들 = reference-first 얇은 인덱스(하한 3-tuple + ④~⑨)
  - ADR-179 §결정 2-U    : **번들 필드 allowlist = 닫힌 10 필드**(열거 밖 1건이라도 위반)
  - ADR-179 §결정 3      : 무결성 축 `usable`|`suspect` — 미태깅 = fail-closed
  - ADR-179 §결정 4      : external side-effect 술어 + dedup(`intent_key` canonical sha256)
  - ADR-179 §결정 8      : degrade 사다리 + **재시도 예산 0**(저장 실패 시 종료코드 ≠ 0)
  - Story CFP-2984 §7.12-B/B1/B2 : 착지 직전 스캔 7행 계약(정의역 = 착지 객체 그래프)
  - Story CFP-2984 §7.12-G S-10  : 참조형 = **4 조건 AND** 구문 술어
  - Change Plan §11.6    : intent_key = sha256(canonical_json({op, target, body_digest}))

mode (정확히 1개 필수 — 아님 exit 2):
  --validate       --bundle <path>
  --store          --bundle <path> --out <path>
  --dedup          --ledger <path> --intents <path>
  --land           --worktree <dir> --branch <name> [--remote <r>] [--sha <SHA>]
  --pre-push-scan  --worktree <dir> [--sha <SHA>]

exit code (3분기 — `2` 를 성공으로 접지 않는다):
  0 = PASS  /  1 = 위반·fail-closed·판정 불가·저장 실패  /  2 = usage error

정직 천장(ADR-119 / ADR-179 §결정 9):
  - 스캔 엔진 = `redact_dev_process_content.redact()` **재사용**(신규 정규식 0건). 그 모듈이
    자기 docstring 에서 선언한 bounded-degradation 천장을 **그대로 상속**한다 — "secret·PII 유출 0"
    을 단정하지 않는다. 보장 = "스캔 미통과 상태로 본 경로를 통과한 착지가 0건".
  - `wip_summary`(allowlist ③)에 대한 AC-31 기계 보장 = **0** (ADR-179 §결정 2-U 닫힘 규칙 3 이
    "③ 내용 통제는 AC-32 단독 위임" 을 명시) — 본 모듈은 ③ 에 참조형 술어를 적용하지 않는다.
  - `empty_reason` 은 ADR 이 값공간을 `enum` 으로 **명명만** 하고 멤버를 열거하지 않았다. 따라서
    멤버십은 미강제이며 enum-**형태**(소문자 토큰)만 강제한다. 이 사실을 여기 declare 한다.
"""

import argparse
import hashlib
import json
import os
import pathlib
import re
import subprocess
import sys
import time
import unicodedata

# Windows cp949 회피 (ADR-061 portability 정합)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

EXIT_PASS = 0
EXIT_VIOLATION = 1
EXIT_USAGE = 2
# 저장 실패 종료코드 — **성공을 보고하지 않는다** (AC-4 / §8.2-E INV-T2).
STORE_FAILURE_EXIT = EXIT_VIOLATION
# 프로세스 기동 실패 sentinel — git 이 낼 수 없는 값. `_git()` 이 OSError 를 이 rc 로 접어
# 호출부가 **designed fail-closed**(SCAN_RESULT/PUSH 토큰 출력)로 처리하게 한다 (S-10).
EXIT_PROC_SPAWN_FAILED = 199

# ─────────────────────── ADR-179 §결정 2-U — allowlist (닫힌 집합) ────────────────────
# ⑧ 은 `empty_reason` + `failed_at` 2 키가 한 entry 이므로 실 키 수 = 11.
ALLOWLIST_FIELDS = (
    "branch",              # ① 참조형
    "last_commit_sha",     # ② 참조형
    "wip_summary",         # ③ 제한 원문 — 유일 예외(참조형 술어 적용 제외)
    "unfinished",          # ④ 항목 목록(참조형 원소)
    "resume_point",        # ⑤ 참조형
    "side_effect_ledger",  # ⑥ 닫힌 스키마(자유 텍스트 0)
    "integrity_tag",       # ⑦ 조각별 enum
    "empty_reason",        # ⑧-a 조건부 required
    "failed_at",           # ⑧-b 조건부 required
    "producer",            # ⑨ roster 실명 + story_key + KST 실측 시각
    "notes_ref",           # ⑩ 참조형 — 진행 노트 sidecar 포인터
)

# 조각 1+ 인 번들의 required (ADR-179 §결정 2 하한 3-tuple + ④~⑦·⑨ / ⑧ 은 조건부 / ⑩ 은 optional)
REQUIRED_NONEMPTY = (
    "branch",
    "last_commit_sha",
    "wip_summary",
    "unfinished",
    "resume_point",
    "side_effect_ledger",
    "integrity_tag",
    "producer",
)
# 조각 0 인 번들의 required — 빈 번들 ≠ 생성 실패 (AC-1)
REQUIRED_EMPTY = ("empty_reason", "failed_at")

TAG_ENUM = ("usable", "suspect")                       # ADR-179 §결정 3
OP_ENUM = (                                            # Change Plan §11.6 closed enum
    "issue_create", "pr_create", "comment_add",
    "review_submit", "label_add", "merge", "push",
)
STATUS_ENUM = ("intended", "applied", "unknown")       # ADR-179 §결정 4 (3-state)

PRODUCER_KEYS = ("agent_type", "story_key", "produced_at")
LEDGER_ROW_REQUIRED = ("op", "target_ref", "executed_at", "status")
LEDGER_ROW_OPTIONAL = ("body_digest",)
INTENT_KEYS = ("op", "target", "body")

# K3 — 휘발 필드 **명시 열거**. 열거 밖 필드를 조용히 제외하면 서로 다른 intent 가 접힌다
#      (Change Plan §8.5.3). 확장은 계획 변경 사항이지 코드 재량이 아니다.
VOLATILE_KEYS = (
    "created_at",    # 생성 시각
    "executed_at",   # 생성 시각(원장 row 기록 시각)
    "retry_count",   # 재시도 카운터
    "nonce",         # nonce
    "session_id",    # 세션 id
)

# 선두 sentinel — `scripts/jira-channel/echo-guard.sh:17` CF_ORCH_SENTINEL 과 byte-동일
CF_ORCH_SENTINEL = "⟦cf-orch⟧"

# ─────────────────────── S-10 참조형 술어 (4 조건 AND · 구문만) ───────────────────────
REF_MAX_LEN = 512        # ② 길이
REF_MAX_SPACES = 1       # ③ 공백

_REF_FORMS = (
    re.compile(r"[^\s:]+(?: [^\s:]+)?(?::\d+(?:-\d+)?)?"),  # path[:line[-line]]
    re.compile(r"[^\s:@]+@[0-9a-fA-F]{7,40}"),              # branch@<7~40hex>
    re.compile(r"blob:sha256:[0-9a-fA-F]{64}"),             # blob:sha256:<64hex>
    re.compile(r"[0-9a-fA-F]{40}"),                         # <40hex>
    re.compile(r"#\d+"),                                    # #<digits>
)

_RE_ISO_TS = re.compile(
    r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?(?:Z|[+-]\d{2}:\d{2})"
)
_RE_ENUM_TOKEN = re.compile(r"[a-z][a-z0-9_]{0,63}")
_RE_SHA256_HEX = re.compile(r"[0-9a-fA-F]{64}")


def is_reference_form(value):
    """S-10 참조형 술어 — 4 조건 AND. 하나라도 불충족 = 원문형.

    ★ 값 **구문**만 본다. "이 값이 의미상 참조인가" 는 판정하지 않는다(AC-5 강등 함정 회피).
    """
    if not isinstance(value, str) or value == "":
        return False
    if "\n" in value or "\r" in value:                                  # ① 개행 0
        return False
    if len(value) > REF_MAX_LEN:                                        # ② 길이 ≤ 512
        return False
    if sum(1 for ch in value if ch.isspace()) > REF_MAX_SPACES:         # ③ 공백 ≤ 1
        return False
    for rx in _REF_FORMS:                                               # ④ 닫힌 형태집합
        if rx.fullmatch(value):
            return True
    return False


def norm_enum(value):
    """enum 정규화 — 대소문자·주변 공백 흡수 후 대조(§5.3.2 AC-2 ③ 축)."""
    if not isinstance(value, str):
        return None
    return value.strip().lower()


def _is_ts(value):
    return isinstance(value, str) and bool(_RE_ISO_TS.fullmatch(value))


# ─────────────────────── 번들 검증 ────────────────────────────────────────────────────
def _check_ref_field(obj, key, out, required=True):
    if key not in obj:
        if required:
            out.append("required 필드 결손: %s" % key)
        return
    if not is_reference_form(obj[key]):
        out.append("참조형 술어 위반(원문형으로 분류됨): %s" % key)


def _check_fragments(frags, out):
    """⑦ integrity_tag — 조각별 `usable`|`suspect` **정확히 하나**. 미태깅 = fail-closed."""
    if not isinstance(frags, list):
        out.append("integrity_tag: 배열이어야 한다")
        return []
    for idx, frag in enumerate(frags):
        if not isinstance(frag, dict):
            out.append("integrity_tag[%d]: 객체여야 한다" % idx)
            continue
        extra = sorted(set(frag) - {"ref", "tag"})
        if extra:
            out.append("integrity_tag[%d]: 닫힌 스키마 밖 키 %s" % (idx, extra))
        if "ref" not in frag:
            out.append("integrity_tag[%d]: ref 결손" % idx)
        elif not is_reference_form(frag["ref"]):
            out.append("integrity_tag[%d].ref: 참조형 술어 위반" % idx)
        if "tag" not in frag:
            # ADR-179 §결정 3 = 미태깅은 `suspect` 로 fail-closed 취급하며,
            # AC-2(미태깅 0건) 기준으로 **유효 번들이 아니다**.
            out.append("integrity_tag[%d]: 미태깅 조각 — fail-closed(suspect 취급)" % idx)
        elif norm_enum(frag["tag"]) not in TAG_ENUM:
            out.append("integrity_tag[%d].tag: 값공간 밖(%r)" % (idx, frag["tag"]))
    return frags


def _check_ledger_rows(rows, out, label="side_effect_ledger"):
    if not isinstance(rows, list):
        out.append("%s: 배열이어야 한다" % label)
        return
    allowed = set(LEDGER_ROW_REQUIRED) | set(LEDGER_ROW_OPTIONAL)
    for idx, row in enumerate(rows):
        tag = "%s[%d]" % (label, idx)
        if not isinstance(row, dict):
            out.append("%s: 객체여야 한다" % tag)
            continue
        extra = sorted(set(row) - allowed)
        if extra:
            out.append("%s: 닫힌 스키마 밖 키 %s (자유 텍스트 0)" % (tag, extra))
        for key in LEDGER_ROW_REQUIRED:
            if key not in row:
                out.append("%s: required 필드 결손 %s" % (tag, key))
        if "op" in row and norm_enum(row["op"]) not in OP_ENUM:
            out.append("%s.op: 값공간 밖(%r)" % (tag, row["op"]))
        if "status" in row and norm_enum(row["status"]) not in STATUS_ENUM:
            out.append("%s.status: 값공간 밖(%r)" % (tag, row["status"]))
        if "executed_at" in row and not _is_ts(row["executed_at"]):
            out.append("%s.executed_at: ISO 8601 시각 아님" % tag)
        if "target_ref" in row and not is_reference_form(row["target_ref"]):
            out.append("%s.target_ref: 참조형 술어 위반" % tag)
        if "body_digest" in row and not (
            isinstance(row["body_digest"], str)
            and _RE_SHA256_HEX.fullmatch(row["body_digest"])
        ):
            out.append("%s.body_digest: sha256 hex 아님" % tag)


def validate_bundle(bundle):
    """번들 1건 → 위반 문자열 목록(빈 목록 = PASS)."""
    out = []
    if not isinstance(bundle, dict):
        return ["번들 최상위는 객체여야 한다"]

    # (1) allowlist 차집합 = 공집합 (AC-31)
    unknown = sorted(set(bundle) - set(ALLOWLIST_FIELDS))
    if unknown:
        out.append("allowlist 차집합 비공집합 — 열거 밖 필드 %s (ADR-179 §결정 2-U)" % unknown)

    # (2) 조각 태깅 (AC-2 / INV-T1)
    frags = []
    if "integrity_tag" in bundle:
        frags = _check_fragments(bundle["integrity_tag"], out)
    is_empty = not isinstance(frags, list) or len(frags) == 0

    # (3) required 분기 — 빈 번들 ≠ 생성 실패 (AC-1)
    if is_empty:
        for key in REQUIRED_EMPTY:
            if key not in bundle:
                out.append("빈 번들 required 필드 결손: %s (빈 번들 ≠ 생성 실패)" % key)
        if "empty_reason" in bundle:
            if not (isinstance(bundle["empty_reason"], str)
                    and _RE_ENUM_TOKEN.fullmatch(bundle["empty_reason"])):
                out.append("empty_reason: enum 형태(소문자 토큰) 아님")
        if "failed_at" in bundle and not _is_ts(bundle["failed_at"]):
            out.append("failed_at: ISO 8601 시각 아님")
    else:
        for key in REQUIRED_NONEMPTY:
            if key not in bundle:
                out.append("required 필드 결손: %s" % key)
        for key in REQUIRED_EMPTY:
            if key in bundle:
                out.append("%s: 조각 1+ 번들에는 부재해야 한다(빈 번들 전용 필드)" % key)

    # (4) 값 형태 분류 — 참조형 필드 (③ wip_summary 는 **적용 제외**)
    #     presence 는 (3) 이 이미 보므로 여기서는 값 형태만 본다(중복 보고 회피).
    for key in ("branch", "last_commit_sha", "resume_point"):
        _check_ref_field(bundle, key, out, required=False)
    if "notes_ref" in bundle:
        _check_ref_field(bundle, "notes_ref", out, required=False)
    if "unfinished" in bundle:
        if not isinstance(bundle["unfinished"], list):
            out.append("unfinished: 배열이어야 한다")
        else:
            for idx, item in enumerate(bundle["unfinished"]):
                if not is_reference_form(item):
                    out.append("unfinished[%d]: 참조형 술어 위반(원문형)" % idx)

    # (5) ③ wip_summary — AC-31 기계 보장 0. 타입·비공백만 본다.
    if "wip_summary" in bundle:
        if not isinstance(bundle["wip_summary"], str) or bundle["wip_summary"].strip() == "":
            out.append("wip_summary: 비어있지 않은 문자열이어야 한다")

    # (6) ⑥ 원장 / ⑨ producer
    if "side_effect_ledger" in bundle:
        _check_ledger_rows(bundle["side_effect_ledger"], out)
    if "producer" in bundle:
        producer = bundle["producer"]
        if not isinstance(producer, dict):
            out.append("producer: 객체여야 한다")
        else:
            extra = sorted(set(producer) - set(PRODUCER_KEYS))
            if extra:
                out.append("producer: 닫힌 스키마 밖 키 %s" % extra)
            for key in PRODUCER_KEYS:
                if key not in producer:
                    out.append("producer: required 필드 결손 %s" % key)
            for key in ("agent_type", "story_key"):
                if key in producer and not is_reference_form(producer[key]):
                    out.append("producer.%s: 참조형 술어 위반" % key)
            if "produced_at" in producer and not _is_ts(producer["produced_at"]):
                out.append("producer.produced_at: ISO 8601 시각 아님")

    return out


# ─────────────────────── 입력 로드 (INV-T5 — 부분 기록 번들 fail-closed) ──────────────
def _load_json(path, label):
    p = pathlib.Path(path)
    if not p.is_file():
        return None, ["%s: 입력 부재 — fail-closed (%s)" % (label, p.name)]
    try:
        raw = p.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        return None, ["%s: 판독 실패 — fail-closed (%s)" % (label, type(exc).__name__)]
    try:
        return json.loads(raw), []
    except ValueError as exc:
        return None, [
            "%s: JSON 파싱 실패 — 부분 기록·손상 입력을 유효로 판독하지 않는다 (INV-T5): %s"
            % (label, exc)
        ]


def _emit(violations, head):
    for v in violations:
        print("::salvage-violation:: %s" % v)
    if violations:
        print("%s: FAIL (violations=%d)" % (head, len(violations)))
        return EXIT_VIOLATION
    print("%s: PASS" % head)
    return EXIT_PASS


def cmd_validate(bundle_path):
    obj, errs = _load_json(bundle_path, "bundle")
    if errs:
        return _emit(errs, "SALVAGE_VALIDATE")
    return _emit(validate_bundle(obj), "SALVAGE_VALIDATE")


# ─────────────────────── store — 단일 시도 후 degrade (ADR-179 §결정 8 · 재시도 예산 0) ─
def _store_attempt(out_path, payload):
    """단 하나의 저장 시도. **마커를 시도 본문 안에서** emit 하므로 재시도가 삽입되면
    마커가 그 횟수만큼 증가한다(AC-33 computed 오라클의 관측면)."""
    print("::salvage-store-attempt::")
    with open(out_path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(payload)


def cmd_store(bundle_path, out_path):
    obj, errs = _load_json(bundle_path, "bundle")
    if errs:
        return _emit(errs, "SALVAGE_STORE")
    violations = validate_bundle(obj)
    if violations:
        return _emit(violations, "SALVAGE_STORE")

    frags = obj.get("integrity_tag") or []
    payload = json.dumps(obj, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    try:
        _store_attempt(out_path, payload)
    except OSError as exc:
        # F3 종점 — 손실 범위만 명시한 사고 레코드. 외부 의존 0·네트워크 0.
        # ★ 재시도·대기 **없음**(예산 0). 여기서 backoff 를 재적용하면 축1 이 축2 를 악화시킨다.
        record = {
            "record": "salvage-store-incident",
            "stored": False,
            "attempts": 1,
            "retry_budget": 0,
            "degrade": "F3",
            "reason_class": type(exc).__name__,
            "unrecoverable_scope": {
                "out_basename": os.path.basename(str(out_path)),
                "fragments_total": len(frags) if isinstance(frags, list) else 0,
                "fragments_unstored": len(frags) if isinstance(frags, list) else 0,
                "bundle_basename": os.path.basename(str(bundle_path)),
            },
        }
        print("::salvage-incident:: %s" % json.dumps(record, ensure_ascii=False, sort_keys=True))
        print("SALVAGE_STORE: FAIL (stored=false)")
        return STORE_FAILURE_EXIT
    print("SALVAGE_STORE: PASS")
    return EXIT_PASS


# ─────────────────────── dedup (ADR-179 §결정 4 / Change Plan §11.6 · §8.5.3 K1~K5) ────
def canonical_json(obj):
    """K2 — canonical form = 키 사전순 + 최소 구분자 + non-ASCII 보존."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def strip_volatile(obj):
    """K3 — 휘발 필드 **명시 열거** 제외(열거 밖 조용한 제외 금지)."""
    if isinstance(obj, dict):
        return {k: strip_volatile(v) for k, v in obj.items() if k not in VOLATILE_KEYS}
    if isinstance(obj, list):
        return [strip_volatile(v) for v in obj]
    return obj


_RE_GH_URL = re.compile(
    r"https?://github\.com/([^/\s]+/[^/\s]+)/(?:issues|pull)/(\d+)/?"
)
_RE_OWNER_REPO_NUM = re.compile(r"([^/\s#]+/[^/\s#]+)#(\d+)")


def canon_target(target):
    """표기 등가변형 흡수 — URL · `owner/repo#N` · 좌표 dict 를 단일 문자열로 환원."""
    if isinstance(target, dict):
        clean = strip_volatile(target)
        repo = clean.get("repo")
        if not isinstance(repo, str):
            raise ValueError("target.repo 결손 또는 문자열 아님")
        if "number" in clean and clean["number"] is not None:
            return "%s#%s" % (unicodedata.normalize("NFC", repo), clean["number"])
        if "ref" in clean and clean["ref"] is not None:
            return "%s@%s" % (unicodedata.normalize("NFC", repo),
                              unicodedata.normalize("NFC", str(clean["ref"])))
        raise ValueError("target 좌표에 number 도 ref 도 없다")
    if isinstance(target, str):
        value = unicodedata.normalize("NFC", target.strip())
        m = _RE_GH_URL.fullmatch(value)
        if m:
            return "%s#%s" % (m.group(1), m.group(2))
        m = _RE_OWNER_REPO_NUM.fullmatch(value)
        if m:
            return "%s#%s" % (m.group(1), m.group(2))
        return value
    raise ValueError("target 은 문자열 또는 좌표 객체여야 한다")


def _normalize_body_text(text):
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    stripped = text.lstrip()
    if stripped.startswith(CF_ORCH_SENTINEL):           # 선두 sentinel 제거
        stripped = stripped[len(CF_ORCH_SENTINEL):].lstrip()
        text = stripped
    lines = [ln.rstrip() for ln in text.split("\n")]
    return unicodedata.normalize("NFC", "\n".join(lines).strip())


def body_digest(body):
    if body is None:
        return None
    if isinstance(body, str):
        material = _normalize_body_text(body)
    else:
        material = canonical_json(strip_volatile(body))
        material = unicodedata.normalize("NFC", material)
    return hashlib.sha256(material.encode("utf-8")).hexdigest()


def intent_key(op, target, digest):
    """K1·K2·K4 — sha256(canonical_json({op, target, body_digest}))."""
    payload = {"op": norm_enum(op), "target": canon_target(target), "body_digest": digest}
    return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()


def _rows_of(ledger):
    if isinstance(ledger, dict) and isinstance(ledger.get("rows"), list):
        return ledger["rows"]
    if isinstance(ledger, list):
        return ledger
    return None


def cmd_dedup(ledger_path, intents_path):
    ledger, errs = _load_json(ledger_path, "ledger")
    if errs:
        return _emit(errs, "SALVAGE_DEDUP")
    rows = _rows_of(ledger)
    if rows is None:
        return _emit(["ledger: rows 배열을 찾을 수 없다 — fail-closed"], "SALVAGE_DEDUP")

    violations = []
    _check_ledger_rows(rows, violations, label="ledger.rows")
    if violations:
        return _emit(violations, "SALVAGE_DEDUP")

    applied = set()
    for row in rows:
        if norm_enum(row.get("status")) != "applied":
            continue
        try:
            applied.add(intent_key(row.get("op"), row.get("target_ref"), row.get("body_digest")))
        except ValueError as exc:
            return _emit(["ledger row 키 산출 실패 — fail-closed: %s" % exc], "SALVAGE_DEDUP")

    intents, errs = _load_json(intents_path, "intents")
    if errs:
        return _emit(errs, "SALVAGE_DEDUP")
    if not isinstance(intents, list):
        return _emit(["intents: 배열이어야 한다 — fail-closed"], "SALVAGE_DEDUP")

    allowed = set(INTENT_KEYS) | set(VOLATILE_KEYS)
    suppressed = executed = 0
    decisions = []
    for idx, intent in enumerate(intents):
        if not isinstance(intent, dict):
            return _emit(["intents[%d]: 객체여야 한다 — fail-closed" % idx], "SALVAGE_DEDUP")
        extra = sorted(set(intent) - allowed)
        if extra:
            # K3 — 열거 밖 필드를 조용히 제외하면 서로 다른 intent 가 접힌다.
            return _emit(
                ["intents[%d]: 휘발 열거 밖 미지 필드 %s — fail-closed" % (idx, extra)],
                "SALVAGE_DEDUP",
            )
        if norm_enum(intent.get("op")) not in OP_ENUM:
            return _emit(["intents[%d].op: 값공간 밖 — fail-closed" % idx], "SALVAGE_DEDUP")
        try:
            key = intent_key(intent.get("op"), intent.get("target"), body_digest(intent.get("body")))
        except ValueError as exc:
            return _emit(["intents[%d]: 키 산출 실패 — fail-closed: %s" % (idx, exc)],
                         "SALVAGE_DEDUP")
        # K5 — 정확 일치만(유사도·prefix 금지).
        if key in applied:
            decision = "suppressed"
            suppressed += 1
        else:
            decision = "execute"
            executed += 1
        decisions.append((idx, decision, key))

    for idx, decision, key in decisions:
        print("::salvage-dedup:: index=%d decision=%s intent_key=%s" % (idx, decision, key))
    print("SALVAGE_DEDUP: PASS (suppressed=%d executed=%d)" % (suppressed, executed))
    return EXIT_PASS


# ─────────────────────── 착지 직전 스캔 + push (Story §7.12-B 7행 계약) ────────────────
_RE_MISSING_DANGLING = re.compile(
    r"^[0-9a-f]{40,64} (missing|dangling)$", re.MULTILINE
)

# ★★ 차단 판정 룰 집합 (설계 §7.12-D 문면으로부터의 **선언된 이탈** — 근거 = firsthand 실측)
#
# §7.12-D 는 `audit["redaction_applied"] is True ⇒ 스캔 미통과` 로 적었으나, 그 술어를 문자
# 그대로 배선하면 **secret 이 0 인 clean 번들도 100% 차단**된다(born-RED = 정상 착지 전면 봉쇄).
# 실측(임시 repo, 정리 완료 — 착지 객체 3개: commit/tree/blob):
#   commit 객체 → ['email', 'hex_high_entropy']   (author identity + parent/tree OID — 항상 발화)
#   blob(clean 번들) → ['hex_high_entropy', 'kr_rrn']
#     · hex_high_entropy = `_RE_HEX [a-f0-9]{32,}` 가 ADR-179 §결정 2-U 가 **요구하는** 값
#       (`last_commit_sha` 40hex · `blob:sha256:<64hex>` · `branch@<hex>`)에 발화 —
#       **스키마가 요구하는 값이 스스로 게이트를 RED 로 만든다.**
#     · kr_rrn = `\d{6}[-\s]?\d{7}` 가 sha256 안의 13자리 연속 숫자 런에 발화(구조적 오탐).
#
# ⇒ 차단 판정은 **secret-class 9룰**로 좁힌다. 나머지(email · kr_rrn · hex_high_entropy ·
#   abs_or_home_path · session_id)는 **advisory 관측 라인**으로 남겨 정보 손실 0.
#
# ★ 정직 천장(over-claim 금지): 스캔 통과 = "착지 객체에서 **secret-class 9룰 미발화**" 이지
#   "secret·PII 없음" 이 **아니다**. 특히 §7.12-F F-2 가 "PII 2종(kr_rrn·email)은 덮인다" 고
#   적은 커버는 **차단 축에서는 성립하지 않는다**(관측 축으로 강등) — 이 이탈은 DevPL 경유
#   Architect 회부 대상으로 declare 한다.
SCAN_BLOCKING_RULES = (
    "private_key_block",
    "authorization_header",
    "cookie_header",
    "github_pat",
    "github_fine_grained_pat",
    "cloud_key",
    "api_key_credential",
    "env_dump_excluded",
    "credential_subprocess_excluded",
)


class _IntegrityUnresolved(Exception):
    pass


def _git(worktree, args, stdin_bytes=None):
    """★ 비협상 ① — `git` **모든** 호출에 `-C <worktree>`.
    `cat-file` 이 CWD object DB 를 읽으면 다른 repo CWD 에서 rc=0 · hit 0 으로 조용히 통과한다
    (Story §7.12-B1 G2/G3 실측). 첫 명령에 `-C` 를 쓴다는 것 자체가 CWD ≠ worktree 전제의 증거다.
    ★ 비협상 ② — **프로세스 기동 실패(`OSError`)를 designed fail-closed 로 접는다.**
    미포착이면 예외가 호출부를 뚫고 나가 `SCAN_RESULT`/`PUSH` 토큰이 **하나도 출력되지 않는다**.
    그때 종료코드 1 은 Python 미처리 예외 값이 `EXIT_VIOLATION` 과 **우연히 같은 것**이지
    "차단했다"는 판정이 아니다 — **"막았다"와 "터졌다"가 출력으로 구별돼야 한다**
    (S-10 실측: 실 worktree argv 56,478 B > Windows CreateProcess ≈32 KB → WinError 206).
    """
    try:
        proc = subprocess.run(
            ["git", "-C", str(worktree)] + list(args),
            input=stdin_bytes,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except OSError as spawn_exc:  # 변수명 구별 — 기존 self-test 앵커(`as exc:`) 유일성 보존
        # rc=EXIT_PROC_SPAWN_FAILED 는 git 이 낼 수 없는 값 — 호출부가 "판정 불가"로 접는다.
        return EXIT_PROC_SPAWN_FAILED, b"", ("프로세스 기동 실패: %s" % spawn_exc).encode("utf-8")
    return proc.returncode, proc.stdout, proc.stderr


def _parse_batch(data):
    """`cat-file --batch` 스트림을 객체 단위로 분해(size 헤더 기반 정확 분할)."""
    out = []
    i = 0
    total = len(data)
    while i < total:
        nl = data.find(b"\n", i)
        if nl < 0:
            raise _IntegrityUnresolved("batch 스트림 절단")
        header = data[i:nl].decode("utf-8", "replace")
        i = nl + 1
        parts = header.split(" ")
        if len(parts) == 2 and parts[1] in ("missing", "dangling"):
            raise _IntegrityUnresolved(header)
        if len(parts) != 3 or not parts[2].isdigit():
            raise _IntegrityUnresolved("batch 헤더 파싱 불가")
        size = int(parts[2])
        out.append((parts[0], parts[1], data[i:i + size]))
        i += size
        if data[i:i + 1] == b"\n":
            i += 1
    return out


def _scan_blob(text, redact_mod):
    """detect 모드 재사용 — 신규 정규식 0건. → (verdict, blocking[], advisory[])

    ★ F-3 fail-open 대응: 탐지기는 parse-timeout 시 **남은 룰을 중단**하고 그 사실을 audit 에
    싣지 않는다 ⇒ `redaction_applied == False` 가 "안전" 이 아니라 "검사 미완" 일 수 있다.
    포화(`elapsed >= PARSE_TIMEOUT_S`, 하한 대조) · 입력 cap 초과 = **판정 불가**(통과 아님).
    """
    encoded = text.encode("utf-8", "replace")
    if len(encoded) > redact_mod.BYTE_CAP:
        return "undecidable", [], []
    if text.count("\n") + 1 > redact_mod.LINE_CAP:
        return "undecidable", [], []
    started = time.monotonic()
    _, audit = redact_mod.redact(text)
    elapsed = time.monotonic() - started
    if elapsed >= redact_mod.PARSE_TIMEOUT_S:
        return "undecidable", [], []
    fired = list(audit.get("redaction_rules_fired") or [])
    blocking = [r for r in fired if r in SCAN_BLOCKING_RULES]
    advisory = [r for r in fired if r not in SCAN_BLOCKING_RULES]
    return ("finding" if blocking else "clean"), blocking, advisory


def _import_redactor():
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import redact_dev_process_content as redact_mod  # noqa: E402
    return redact_mod


def cmd_land(worktree, remote, branch, sha, do_push):
    wt = pathlib.Path(worktree)
    if not wt.is_dir():
        print("SCAN_RESULT: integrity-unresolved")
        print("PUSH: skipped")
        print("::salvage-violation:: worktree 디렉터리 부재 — fail-closed")
        return EXIT_VIOLATION

    # 2 — 착지 후보를 SHA 로 고정
    if not sha:
        rc, out, err = _git(wt, ["rev-parse", "HEAD"])
        if rc != 0:
            print("SCAN_RESULT: integrity-unresolved")
            print("PUSH: skipped")
            print("::salvage-violation:: rev-parse HEAD 실패 (rc=%d)" % rc)
            return EXIT_VIOLATION
        sha = out.decode("utf-8", "replace").strip()

    # 2.5 — ★ 비협상 ② (S-P1-1): 스캔 정의역 ⊇ push 전송 집합.
    #   baseline 을 push 대상과 **동일 remote** 로 묶고, remote-tracking ref 를 원격 실보유와
    #   맞춘다. 둘 중 하나라도 어긋나면 스캔이 제외한 객체가 그대로 전송된다:
    #     E5 = baseline(origin) ≠ push(pub)      → origin 에만 있던 객체 무검사 전송
    #     E4 = phantom refs/remotes/<r>/* 잔존   → 로컬 ref 가 원격 실보유와 괴리
    #   `--prune` 이 필수다. 평범한 `fetch` 는 phantom 을 제거하지 못한다(실측).
    #   fetch 실패 = baseline 확정 불가 ⇒ **fail-closed**(무검사 통과 금지). `--land` 는
    #   어차피 push 하므로 네트워크를 전제해도 정의역이 좁아지지 않는다.
    #   ★ R3 정정: `fetch --prune` 에 기대지 않는다. prune 은 `remote.<r>.fetch` refspec 의
    #   **destination 범위**만 청소하는데(`--single-branch` clone 이면 그게 ref 하나),
    #   `--not --remotes=<r>` 은 `refs/remotes/<r>/*` **전체**를 센다 — 정적 정의역 불일치라
    #   prune 이 rc=0 으로 성공해도 손대지 못한 ref 가 baseline 에 계상돼 그 객체가 스캔에서
    #   빠진다. "명령의 성공"을 "속성의 성립"으로 추론하는 형태를 여기서 끊는다.
    #   ⇒ baseline 을 **원격 실 ref**(`ls-remote`)에서 직접 구성한다 — 로컬 스냅샷 추론 제거.
    rc, lsr, err = _git(wt, ["ls-remote", remote])
    if rc != 0:
        print("SCAN_RESULT: integrity-unresolved")
        print("PUSH: skipped")
        print("::salvage-violation:: baseline 확정 불가 — `git ls-remote %s` 실패 (rc=%d). "
              "원격 실보유 ref 를 확인할 수 없어 fail-closed." % (remote, rc))
        return EXIT_VIOLATION

    remote_oids = []
    _seen = set()
    for ln in lsr.decode("utf-8", "replace").splitlines():
        tok = ln.split("\t", 1)[0].strip()
        if len(tok) == 40 and all(c in "0123456789abcdef" for c in tok) and tok not in _seen:
            _seen.add(tok)
            remote_oids.append(tok)

    # 로컬에 없는 원격 OID 는 제외 대상에서 뺀다 — `--not <unknown>` 은 rev-list 를 죽인다.
    # 덜 제외 = 더 많이 스캔 = **안전 방향**(놓침이 아니라 과검사).
    present = []
    if remote_oids:
        rc, chk, err = _git(wt, ["cat-file", "--batch-check"],
                            ("\n".join(remote_oids) + "\n").encode("utf-8"))
        if rc == 0:
            for ln in chk.decode("utf-8", "replace").splitlines():
                parts = ln.split()
                if len(parts) >= 2 and parts[1] != "missing":
                    present.append(parts[0])

    # 3 — OID 목록 1회 고정 (4·5 가 **동일 집합**을 본다). baseline = 원격 실보유분만 제외.
    #   ★ S-10: 제외 집합을 **argv 가 아니라 stdin** 으로 넘긴다. 실 repo 는 원격 ref 가
    #   1000+ 라 `--not <OID×N>` argv 가 56 KB 를 넘겨 Windows CreateProcess(≈32 KB)를 깨뜨렸고,
    #   그때 예외가 탈출해 SCAN_RESULT/PUSH 토큰이 **0개** 출력됐다(감사면 사망).
    #   `rev-list --stdin` 은 `<sha>` 와 `^<oid>` 를 개행 구분으로 받으므로 argv 가 상수 크기다.
    rl_stdin = sha + "\n" + "".join("^%s\n" % o for o in present)
    rc, out, err = _git(wt, ["rev-list", "--objects", "--stdin"],
                        rl_stdin.encode("utf-8"))
    if rc != 0:
        print("SCAN_RESULT: integrity-unresolved")
        print("PUSH: skipped")
        print("::salvage-violation:: rev-list 실패 (rc=%d)" % rc)
        return EXIT_VIOLATION
    oids = [ln.split(" ", 1)[0] for ln in out.decode("utf-8", "replace").splitlines() if ln.strip()]

    if oids:
        stdin_bytes = ("\n".join(oids) + "\n").encode("utf-8")

        # 4 — 무결성: **헤더 전용 스트림**(--batch-check) ∧ 행 앵커. missing|dangling ⇒ fail-closed.
        #     `--batch` 를 쓰면 blob 내용이 같은 스트림에 섞여 평범한 문면이 가드를 오발화한다.
        rc, chk, err = _git(wt, ["cat-file", "--batch-check"], stdin_bytes)
        if rc != 0 or _RE_MISSING_DANGLING.search(chk.decode("utf-8", "replace")):
            print("SCAN_RESULT: integrity-unresolved")
            print("PUSH: skipped")
            print("::salvage-violation:: cat-file --batch-check 무결성 판정 불가 (rc=%d)" % rc)
            return EXIT_VIOLATION

        # 5 — 내용 스트림
        rc, batch, err = _git(wt, ["cat-file", "--batch"], stdin_bytes)
        if rc != 0:
            print("SCAN_RESULT: integrity-unresolved")
            print("PUSH: skipped")
            print("::salvage-violation:: cat-file --batch 실패 (rc=%d)" % rc)
            return EXIT_VIOLATION

        # 6 — 스캔. 미통과·판정 불가면 push 미도달.
        try:
            objects = _parse_batch(batch)
        except _IntegrityUnresolved as exc:
            print("SCAN_RESULT: integrity-unresolved")
            print("PUSH: skipped")
            print("::salvage-violation:: %s" % exc)
            return EXIT_VIOLATION

        redact_mod = _import_redactor()
        # 룰 이름 drift 가드 — 차단 집합이 탐지기 값공간 밖으로 미끄러지면 조용한 무검사가 된다.
        known = getattr(redact_mod, "RULE_NAMES", None)
        if known is not None:
            drifted = [r for r in SCAN_BLOCKING_RULES if r not in known]
            if drifted:
                print("SCAN_RESULT: undecidable")
                print("PUSH: skipped")
                print("::salvage-violation:: 차단 룰 이름 drift %s — fail-closed" % drifted)
                return EXIT_VIOLATION

        findings = 0
        undecidable = 0
        for oid, otype, content in objects:
            verdict, blocking, advisory = _scan_blob(
                content.decode("utf-8", "replace"), redact_mod)
            if advisory:
                print("::salvage-scan-advisory:: %s (%s) rules=%s — 비차단 관측"
                      % (oid[:12], otype, ",".join(sorted(set(advisory)))))
            if verdict == "finding":
                findings += 1
                print("::salvage-violation:: 스캔 미통과 객체 %s (%s) rules=%s"
                      % (oid[:12], otype, ",".join(sorted(set(blocking)))))
            elif verdict == "undecidable":
                undecidable += 1
                print("::salvage-violation:: 판정 불가 객체 %s (%s) — 통과로 접지 않는다"
                      % (oid[:12], otype))
        if undecidable:
            print("SCAN_RESULT: undecidable")
            print("PUSH: skipped")
            return EXIT_VIOLATION
        if findings:
            print("SCAN_RESULT: finding")
            print("PUSH: skipped")
            return EXIT_VIOLATION

    print("SCAN_RESULT: clean")

    # 7 — 스캔한 **그 SHA** 만 나간다 (재기록 mutant 는 다른 SHA 가 되므로 구조적으로 배제).
    if not do_push:
        print("PUSH: skipped")
        return EXIT_PASS
    rc, out, err = _git(wt, ["push", remote, "%s:refs/heads/%s" % (sha, branch)])
    if rc != 0:
        print("PUSH: skipped")
        print("::salvage-violation:: push 실패 (rc=%d)" % rc)
        return EXIT_VIOLATION
    print("PUSH: done")
    return EXIT_PASS


# ─────────────────────── CLI ──────────────────────────────────────────────────────────
def _fail_usage(message):
    sys.stderr.write("[salvage-usage-error] %s\n" % message)
    sys.exit(EXIT_USAGE)


def build_parser():
    ap = argparse.ArgumentParser(
        prog="check-salvage-bundle",
        description="salvage 번들 · side-effect 원장 · 착지 직전 스캔 (CFP-2984)",
    )
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--validate", action="store_true", help="번들 스키마·allowlist 검증")
    mode.add_argument("--store", action="store_true", help="번들 저장 1회 시도(재시도 0)")
    mode.add_argument("--dedup", action="store_true", help="side-effect intent dedup 판정")
    mode.add_argument("--land", action="store_true", help="착지 직전 스캔 + push (L1 단일 경로)")
    mode.add_argument("--pre-push-scan", dest="pre_push_scan", action="store_true",
                      help="착지 직전 스캔만(push 미도달)")
    ap.add_argument("--bundle")
    ap.add_argument("--out")
    ap.add_argument("--ledger")
    ap.add_argument("--intents")
    ap.add_argument("--worktree")
    ap.add_argument("--remote", default="origin")
    ap.add_argument("--branch")
    ap.add_argument("--sha")
    return ap


def main(argv=None):
    args = build_parser().parse_args(argv)
    if args.validate:
        if not args.bundle:
            _fail_usage("--validate 는 --bundle <path> 필수")
        return cmd_validate(args.bundle)
    if args.store:
        if not args.bundle or not args.out:
            _fail_usage("--store 는 --bundle <path> --out <path> 필수")
        return cmd_store(args.bundle, args.out)
    if args.dedup:
        if not args.ledger or not args.intents:
            _fail_usage("--dedup 는 --ledger <path> --intents <path> 필수")
        return cmd_dedup(args.ledger, args.intents)
    if args.land:
        if not args.worktree or not args.branch:
            _fail_usage("--land 는 --worktree <dir> --branch <name> 필수")
        return cmd_land(args.worktree, args.remote, args.branch, args.sha, True)
    if args.pre_push_scan:
        if not args.worktree:
            _fail_usage("--pre-push-scan 는 --worktree <dir> 필수")
        return cmd_land(args.worktree, args.remote, args.branch, args.sha, False)
    _fail_usage("mode 미지정")
    return EXIT_USAGE


if __name__ == "__main__":
    sys.exit(main())
