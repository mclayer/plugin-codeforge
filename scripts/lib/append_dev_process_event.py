#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# tier: [measurement]
# append_dev_process_event.py — dev-process-event-v1 index-tier row append primitive (SCHEMA SSOT)
#
# Carrier: CFP-2687 Phase 2 (구현) / Epic #2686 Story A (선행 substrate)
# SSOT: docs/inter-plugin-contracts/dev-process-event-v1.md §2 (index schema)
#       + ADR-155 §결정 1/4/5 + change-plan §3/§7.4.1/§11.6
#
# 책임:
#   - dev-process-event-v1 §2 index-tier row (allow-list clean) 를 append-only JSONL 로 write.
#   - 본 파일의 `_ROW_KEYS` = 계약 §2 index 필드 목록의 EXTERNAL code anchor (parity SSOT).
#     wave-2 parity self-test 가 계약 §2 table(동적 파싱) vs `_ROW_KEYS`(하드코딩 code anchor)
#     를 대조한다 (doc vs code, born-drift = FAIL). `_ROW_KEYS` != §2 = 계약 위반.
#
# 필수 불변식 (계약 §2 / change-plan §7.4.1 — 절대 위반 금지):
#   - content-blind: append_event 는 allow-list 필드(enum/numeric/hash/상관ID/blob-ref/emit_source)
#     만 수용한다. free-form content 본문은 절대 수령·저장하지 않는다 — allow-list 밖 kwarg = drop
#     (row 자체가 content 를 담는 경로가 구조적으로 부재).
#   - cross-platform kernel-atomic single-row append (H1 완료행 clobber 봉인): 공유 primitive
#     append_spawn_event._append_jsonl_row **재사용**(POSIX O_APPEND / Windows FILE_APPEND_DATA —
#     ADR-155 Amendment 1). read-modify-write(append_stop_event._atomic_append = O(n) +
#     lost-update) 패턴 **복사 금지**.
#   - event_id = deterministic sha256 (random UUID 금지 — §11.6). 동일 논리 이벤트 → 동일 event_id
#     (at-least-once idempotent, read-time dedup key). timestamp 는 event_id 산입 제외 (재시도 멱등).
#   - timestamp = UTC Z strict 저장 (KST 표시는 표현 계층 — ADR-079). monotonic 이 필요하면
#     caller 가 prev_timestamp_utc 를 주입 → MAX(prev+1ms). 본 primitive 는 원장을 read 하지 않는다
#     (O_APPEND-pure 유지 — read-modify-write 회피).
#   - session_id / 원 식별자는 sha256 만 (raw 저장 금지). append_stop_event.py line 73 raw
#     session_id 패턴 **복사 금지** (T-DPE-6).
#   - non-blocking: 어떤 실패도 caller flow 로 raise 하지 않는다 — graceful degrade + return None,
#     caller 는 exit-0 semantics 유지 (ADR-115).
#   - 0 API call — local I/O only.
#
# ★정직 (append 원자성 2축 분리 — change-plan §7.4.1 / ADR-155 Amendment 1):
#   [clobber 축 — 봉인됨] 완료행 lost-update(clobber)는 공유 primitive
#   append_spawn_event._append_jsonl_row 가 cross-platform kernel-atomic single-row append
#   (POSIX O_APPEND / Windows FILE_APPEND_DATA)로 봉인 — 2-writer 경합 완료행 clobber-free.
#   ("kernel-atomic 미주장" 이전 표기는 clobber 축에서 철회 — MSVCRT lseek-then-write 버그 수리 후
#   실제 kernel-atomic). 보장 scope = local NTFS/POSIX 정규파일 + row당 단일-write.
#   [torn 축 — 무주장 잔존] network share(SMB/NFS) 제외 + torn(multi-sector interleave)은 별개
#   무주장: single-write O_APPEND 는 offset-append clobber-free 이나 임의 크기 non-interleave 는
#   보장하지 않는다(pubs.opengroup.org write.html) — 무-interleave 는 small-row 불변식(<4KB,
#   index=blob-ref only 이므로 작음)에 의해 bounded 될 뿐이다. torn no-interleave 증명 = Phase 2
#   StatefulTest.
#
# ★activation gate 경계 (INV-8b / α 비대칭 — 계약 §telemetry-activation):
#   본 primitive 는 **gate-free mechanism** 이다. telemetry 활성 정책(wrapper always-on /
#   consumer opt-in default-false)과 redact→capture_blob→append_event(INV-8b) orchestration 은
#   HOOK/emit 계층(HookDev, wave 2) 소관이다. 본 primitive 는 이미 계산된 blob_ref(str) 를
#   수령할 뿐 redaction·blob write·활성 판정을 스스로 수행하지 않는다.

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Windows cp949 인코딩 회피: stdout/stderr UTF-8 강제 (ADR-061 portability)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# ── O_APPEND primitive 재사용 (ADR-140 hygiene: reuse-before-write) ──
# append_spawn_event._append_jsonl_row = O_APPEND per-row single-write (H1).
# read-modify-write(_atomic_append) 재구현 금지 — 기존 검증된 primitive 호출.
try:
    from append_spawn_event import _append_jsonl_row
except Exception:  # pragma: no cover — import path fallback
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from append_spawn_event import _append_jsonl_row


_SCHEMA_VERSION = "dev-process-event-v1"


# ─────────────────────── 닫힌집합 enum (계약 §2/§3) ───────────────────────

# event_type closed enum (8종 — 계약 §3 / AC-2/6). lane_transition 최소 = ADR-038 6-point.
_EVENT_TYPES = {
    "lane_transition", "prompt_input", "tool_call", "verdict",
    "diff", "defect_finding", "fix_transition", "final_artifact",
}

# emit_source discriminator (§결정 4 — single-stream JOIN 보존)
_EMIT_SOURCES = {"hook", "agent"}

# lane_label closed enum (11값 — label-registry-v2 정합: 10 lane + 없음). spawn-event 정합.
_LANE_LABELS = {
    "요구사항", "요구사항-리뷰", "설계", "설계-리뷰", "구현", "구현-리뷰",
    "구현-테스트", "보안-테스트", "배포", "배포-리뷰", "없음",
}
_LANE_FALLBACK = "없음"

# defect_family CLOSED-7 (taxonomy 4-tuple 중 CLOSED 축 — §결정 3)
_DEFECT_FAMILIES = {
    "correctness", "security", "performance", "design-boundary",
    "test-gap", "doc-integrity", "process-discipline",
}

# defect_type SEMI-OPEN — review-verdict-v4 type-derived ∪ unknown-type (fallback)
_DEFECT_TYPE_FALLBACK = "unknown-type"

# time_to_detection DERIVED measure — 도입점 불명 sentinel
_TTD_UNATTRIBUTED = "unattributed"

# consumer_scope closed enum (ADR-163 §결정 9 isolation marker)
_CONSUMER_SCOPES = {"wrapper", "consumer"}

# ★ CFP-2985 D-12 — root_cause_class CLOSED-6.
#   값공간 ≡ fix-event-v1 v1.6 `원인 판정` enum (계약 §4.2 값공간 선언).
#   ★ INV-R: `defect_family`(결함 class 축)와 **교차 집계 금지** — 본 enum 은 재진입 라우팅 축이다.
_ROOT_CAUSE_CLASSES = {
    "설계", "구현", "요구사항", "환경", "설계-리뷰", "구현-리뷰",
}

# ★ CFP-2985 D-16(적재 술어) — anchor_id 닫힌 형식 2종 (계약 §4.2 J-2 전건).
#   `§<section-ref>` (권장) ∪ `<repo-relative path>:<line>`. bounded token 상한.
_ANCHOR_ID_MAXLEN = 200

# redaction_rules_fired closed enum (audit — 규칙명만, 매칭 secret 원문/hash 절대 미기록 T-DPE-8)
# ★SSOT = redact_dev_process_content.RULE_NAMES — audit dict 의 producer 가 소유하는 rule 어휘.
#   본 consumer 는 producer 어휘를 그대로 import 해 gate (ADR-140 DRY — 복붙 drift 차단).
#   과거 하이픈 축약형(credential/gh-pat/…)은 stop-event §3.2 placeholder 파생 = dev-process
#   design-SSOT(ADR-043 Amd4 snake_case) 와 drift → producer 어휘로 정합(HookDev 교차검증).
try:
    from redact_dev_process_content import RULE_NAMES as _REDACTION_RULES
except Exception:  # pragma: no cover — sibling 미착지 시 fidelity 보존 fallback (redact.RULE_NAMES 동일 유지 의무)
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from redact_dev_process_content import RULE_NAMES as _REDACTION_RULES
    except Exception:
        _REDACTION_RULES = frozenset({
            "api_key_credential", "github_pat", "github_fine_grained_pat", "kr_rrn",
            "email", "hex_high_entropy", "abs_or_home_path", "authorization_header",
            "cookie_header", "cloud_key", "private_key_block", "session_id",
            "env_dump_excluded", "credential_subprocess_excluded",
        })


# ─────────────────────── 20 index 필드 정확 키 순서 (parity SSOT) ─────────────────────
# (이력: 19→18 [CFP-2687] → 18→20 [CFP-2985 D-12 — root_cause_class · anchor_id 말미 append])
# ★★ 계약 dev-process-event-v1.md §2 index schema table 과 EXACTLY 일치해야 한다.
#     wave-2 parity self-test = 계약 §2(동적 파싱) vs 본 tuple(하드코딩 code anchor) 대조.
#     순서·멤버 born-drift = FAIL. 필드 추가/삭제/순서변경 = 계약 amendment 의무.
_ROW_KEYS = (
    "event_id",                 # sha256 — deterministic idempotency invariant
    "schema_version",           # const "dev-process-event-v1"
    "event_type",               # enum (8 closed)
    "emit_source",              # enum {hook, agent}
    "timestamp_utc",            # UTC Z strict (저장) / KST 표시
    "story_key",                # 상관 ID (freeze) — public non-sensitive
    "lane_label",               # 상관 ID (freeze) — lane enum
    "consumer_scope",           # enum {wrapper, consumer} — α 비대칭 isolation marker
    "defect_id",                # 상관 ID (freeze) — sha256 | null (defect/fix events)
    "fix_id",                   # 상관 ID (freeze) — per-defect attempt unit | null (fix events)
    "blob_ref",                 # sha256(REDACTED bytes) | null — evidence-blob-store 참조 (INV-8a)
    "redaction_applied",        # bool — audit
    "redaction_count",          # int — audit
    "redaction_rules_fired",    # closed enum array — audit (규칙명만, T-DPE-8)
    "defect_family",            # enum CLOSED-7 | null (defect events)
    "defect_type",              # SEMI-OPEN (verdict-v4 ∪ unknown-type) | null (defect events)
    "time_to_detection",        # DERIVED measure (ordinal/ts-delta/unattributed) | null (defect events)
    "detecting_lane",           # enum (lane_label) | null (defect events)
    "root_cause_class",         # ★CFP-2985 D-12 — enum CLOSED-6 | null (fix_transition 등)
    "anchor_id",                # ★CFP-2985 D-12 — 닫힌 형식 상관 위치 | null (INV-R 정의역 밖)
)


# storage path (append_spawn_event 관례 재사용 — .claude/ledger/ per-channel basename 고정)
_LEDGER_BASENAME = "dev-process-event.jsonl"
_DEFAULT_PARENT_REL = os.path.join(".claude", "ledger")


# ─────────────────────── hash 유틸 (raw 저장 금지) ───────────────────────────

def _sha256(value):
    """문자열 sha256 hex digest. None/빈 값 → 빈 문자열 sha256 (안정 결정성)."""
    if value is None:
        value = ""
    return hashlib.sha256(str(value).encode("utf-8")).hexdigest()


def _is_sha256_hex(value):
    """64-hex lowercase sha256 형태 검증 (blob_ref / hashed-ID 형식 게이트)."""
    if not isinstance(value, str):
        return False
    s = value.strip().lower()
    return len(s) == 64 and all(c in "0123456789abcdef" for c in s)


# ─────────────────────── deterministic event_id (random UUID 금지 — §11.6) ─────────────

def compute_event_id(event_type, emit_source, story_key="", lane_label="",
                     consumer_scope="", defect_id=None, fix_id=None,
                     blob_ref=None, seq=""):
    """deterministic event_id = sha256(canonical identity composite).

    동일 논리 이벤트 → 동일 event_id (at-least-once idempotent, read-time dedup key).
    **timestamp 는 산입 제외** — 같은 논리 이벤트의 재시도(다른 wall-clock)가 동일 id 를 유지해
    멱등해야 하기 때문(§11.6). defect_id 는 이미 sha256(family‖type‖location) 이라 taxonomy 세부를
    포섭하므로 defect_family/type/detecting_lane 은 별도 산입 불요. random UUID 절대 금지.

    seq = 필드값이 동일한 별개 논리 이벤트를 caller 가 구분하기 위한 disambiguator
          (spawn-event spawn_seq 선례). 미지정이면 "".
    """
    parts = [
        _SCHEMA_VERSION,
        "" if event_type is None else str(event_type),
        "" if emit_source is None else str(emit_source),
        "" if story_key is None else str(story_key),
        "" if lane_label is None else str(lane_label),
        "" if consumer_scope is None else str(consumer_scope),
        "" if defect_id is None else str(defect_id),
        "" if fix_id is None else str(fix_id),
        "" if blob_ref is None else str(blob_ref),
        "" if seq is None else str(seq),
    ]
    composite = "||".join(parts)
    return hashlib.sha256(composite.encode("utf-8")).hexdigest()


# ─────────────────────── UTC Z strict timestamp (저장) ───────────────────────

def _format_utc_z_ms(dt):
    """aware UTC datetime → millisecond-precision UTC Z (3 fractional digits).

    예: 2026-07-15T04:12:33.481Z. Python %f 는 microsecond(6자리)라 //1000 으로 ms 3자리 절삭.
    """
    return dt.strftime("%Y-%m-%dT%H:%M:%S.") + "%03dZ" % (dt.microsecond // 1000)


def _parse_utc_z(value):
    """UTC Z timestamp parse — ms 또는 초 해상도 모두 관용 → aware dt | None.

    'Z' suffix 를 '+00:00' 로 치환 후 fromisoformat (초/ms/µs 소수점 관용). naive → UTC 승격.
    """
    if not value:
        return None
    s = str(value).strip()
    try:
        iso = s[:-1] + "+00:00" if s.endswith("Z") else s
        dt = datetime.fromisoformat(iso)
    except (TypeError, ValueError):
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def _utc_z_now():
    """UTC Z strict, **millisecond precision** — 2026-07-15T04:12:33.481Z.

    형식 = %Y-%m-%dT%H:%M:%S.%fZ (3-digit ms). +00:00 / bare datetime 불허.
    저장 layer = UTC Z 강제 (stop=KST vs spawn=UTC 괴리 봉인은 **timezone** 축 — change-plan §7.4
    clock; precision 은 별개로 ms 유지해 MAX(prev+1ms) 단조 directive 지원). 표시 layer = KST(ADR-079).
    """
    return _format_utc_z_ms(datetime.now(timezone.utc))


def _utc_z_monotonic(prev_timestamp_utc):
    """monotonic UTC Z (ms) — caller 가 prev 를 주입하면 MAX(now, prev+1ms) 로 단조 보장.

    ★본 primitive 는 원장을 read 하지 않는다 (O_APPEND-pure). prev 는 caller/emit 계층이
    직전 timestamp 를 알 때만 주입한다 — 미주입 시 wall-clock now (일반 경로).
    tie-break = **+1ms** (change-plan §7.4 / Story §7.3 design literal). prev 가 초 해상도여도 관용 파싱.
    """
    now = _utc_z_now()
    if not prev_timestamp_utc:
        return now
    prev = _parse_utc_z(prev_timestamp_utc)
    if prev is None:
        return now
    now_dt = _parse_utc_z(now)
    if now_dt is None or now_dt <= prev:
        return _format_utc_z_ms(prev + timedelta(milliseconds=1))
    return now


# ─────────────────────── enum 정규화 (graceful) ──────────────────────────────

def _norm_enum(raw, allowed, fallback=None):
    """closed enum 정규화 — 멤버면 그대로, 아니면 fallback. None 유지."""
    if raw is None:
        return fallback
    s = str(raw).strip()
    if not s:
        return fallback
    return s if s in allowed else fallback


def _norm_lane_label(raw):
    """lane_label — 미매칭 → '없음' fallback (reject 안 함, graceful)."""
    return _norm_enum(raw, _LANE_LABELS, _LANE_FALLBACK)


def _norm_consumer_scope(raw):
    """consumer_scope — 미지정/미매칭 → CLAUDE_PROJECT_DIR basename 휴리스틱 → wrapper.

    (append_spawn_event._normalize_consumer_scope 와 동일 휴리스틱 — α 비대칭 isolation.)
    """
    if raw is not None:
        s = str(raw).strip()
        if s in _CONSUMER_SCOPES:
            return s
    proj_dir = os.environ.get("CLAUDE_PROJECT_DIR", "")
    if proj_dir:
        base = os.path.basename(os.path.normpath(proj_dir)).lower()
        if "plugin-codeforge" in base or base == "codeforge":
            return "wrapper"
        return "consumer"
    return "wrapper"


def _norm_defect_family(raw):
    """defect_family — CLOSED-7 이면 그대로, 아니면 None (non-defect event = null)."""
    return _norm_enum(raw, _DEFECT_FAMILIES, None)


def _norm_root_cause_class(raw):
    """root_cause_class — CLOSED-6 이면 그대로, 아니면 None (§4.2 값공간 선언).

    ★ 경계 분담 (정직 선언): **적재 경계는 값공간(closed enum)만** 본다.
      표기 변형(장식·공백·대소문자) 흡수는 **집계 층**
      (`aggregate_dev_process_event._norm_root_cause_value`, D-13) 책임이며,
      그 층은 본 primitive 를 거치지 않고 원장에 들어온 행(§10 표 파생 등)도 본다.
      두 층은 정의역이 다르므로 같은 술어의 중복이 아니다.
    ★ 비-멤버 → None 은 `_norm_defect_family` 와 동일한 graceful 계약이다
      (reject 아닌 흡수 — record-only, ADR-115).
    """
    return _norm_enum(raw, _ROOT_CAUSE_CLASSES, None)


def _norm_anchor_id(raw):
    """anchor_id — 닫힌 형식 2종만 적재. 그 외(Story-scoped 포함) → None.

    ★ 왜 술어가 필요한가 (계약 §4.2 J-2): index tier 의 "free-form string content field
      도입 금지" 를 회피하는 **전건이 형식 술어의 실재**다. 술어 없이 string 필드를 두면
      그 판정이 무효가 된다 — 즉 본 함수는 선택이 아니라 필드 도입의 조건이다.
    ★ Story-scoped 형상(`cfp-<digits>-…`) 거부 근거 (Change Plan §3.4 처분 1):
      `pattern_count` = 같은 (anchor_id, root_cause_class) 를 공유하는 distinct story_key 수.
      anchor 에 Story key 가 접두되면 group 당 story_key 가 정의상 1 → `pattern_count ≡ 1`
      고정. 조용히 섞이면 값이 아니라 **형식이 집계를 지배**한다.
    ★ 정직 잔여 (`declared`): (a) `<path>:<line>` 은 커밋 간 drift 한다 —
      계약은 anchor_id 안정성을 **보증하지 않는다**(§4.2 J-1: 상관 ID freeze 4종 미편입).
      (b) 거부 대상 접두는 현행 Story KEY(`cfp`) 한정이며 타 KEY 접두 일반화는 미착지.
    ★ 정규식 미사용 (모듈 관례 — self-test 국소 import 외 module-level `re` 0).
    """
    if raw is None:
        return None
    s = str(raw).strip()
    if not s or len(s) > _ANCHOR_ID_MAXLEN:
        return None
    low = s.casefold()
    if low.startswith("cfp-"):                    # ⓑ 기각 형상 — Story-scoped
        tail = low[4:]
        if tail and tail[0].isdigit():
            return None
    if s.startswith("§"):                          # ⓐ 권장 형식 — §<section-ref>
        return s if len(s) > 1 else None
    if ":" in s:                                   # ⓑ <repo-relative path>:<line>
        path_part, _, line_part = s.rpartition(":")
        if (path_part and line_part.isdigit()
                and not path_part.startswith("/") and ":" not in path_part):
            return s
    return None


def _norm_defect_type(raw, is_defect_event):
    """defect_type — SEMI-OPEN. 값 있으면 bounded token 으로 수용, 없으면:
       defect event → unknown-type fallback / 그 외 → None.
    (agent_type semi-open 선례 — 미등재 값 reject 아닌 흡수, free-form leak 은 emit 계층 책임.)
    """
    if raw is None or (isinstance(raw, str) and not raw.strip()):
        return _DEFECT_TYPE_FALLBACK if is_defect_event else None
    return str(raw).strip()


def _norm_time_to_detection(raw):
    """time_to_detection — DERIVED measure. numeric(ordinal/ts-delta) | 'unattributed' | None."""
    if raw is None:
        return None
    if isinstance(raw, (int, float)) and not isinstance(raw, bool):
        return raw
    s = str(raw).strip()
    if not s:
        return None
    if s == _TTD_UNATTRIBUTED:
        return _TTD_UNATTRIBUTED
    try:
        f = float(s)
        return int(f) if f.is_integer() else f
    except ValueError:
        return _TTD_UNATTRIBUTED


def _norm_blob_ref(raw):
    """blob_ref — 계약 형식 = bare 64-hex sha256(REDACTED). 미부합 → None (graceful).

    ★INV-8a 는 blob store(sibling) 가 hash-over-redacted 를 보장한다. 본 primitive 는 이미
    계산된 blob_ref 형식만 게이트한다 (raw 여부는 store 계약이 봉인).
    """
    if raw is None:
        return None
    return raw.strip().lower() if _is_sha256_hex(raw) else None


def _norm_hashed_id(raw):
    """defect_id / fix_id — 상관 ID. 64-hex 이면 그대로, 비어있으면 None,
       그 외 문자열은 sha256 처리(raw 식별자 저장 방지 — content-blind).
    """
    if raw is None:
        return None
    s = str(raw).strip()
    if not s:
        return None
    if _is_sha256_hex(s):
        return s.lower()
    return _sha256(s)


def _norm_redaction_rules(raw):
    """redaction_rules_fired — closed enum array. 미등재 규칙명 drop (allow-list-clean).
       매칭 secret 원문/hash 는 애초에 여기 도달 불가 (규칙명만 — T-DPE-8).
    """
    if not raw:
        return []
    if isinstance(raw, str):
        raw = [raw]
    out = []
    for item in raw:
        if isinstance(item, str) and item.strip() in _REDACTION_RULES:
            out.append(item.strip())
    return out


def _coerce_int(value, default=0):
    if value is None:
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


# ─────────────────────── row 구성 + append (content-blind) ────────────────────

def build_row(**index_fields):
    """dev-process-event-v1 §2 index row dict 구성 (allow-list ONLY — content-blind SSOT).

    allow-list(_ROW_KEYS) 밖 kwarg 은 **drop** (free-form content 유입 구조적 차단).
    required enum(event_type / emit_source) 미부합 → None 반환 (malformed row 회피).
    """
    event_type = _norm_enum(index_fields.get("event_type"), _EVENT_TYPES, None)
    emit_source = _norm_enum(index_fields.get("emit_source"), _EMIT_SOURCES, None)
    if event_type is None or emit_source is None:
        # required closed enum 미부합 = malformed → 기록 거부 (graceful, allow-list-clean 보존)
        print(
            "[codeforge-dev-process-event] WARN: invalid event_type/emit_source "
            "(event_type=%r emit_source=%r) — row 미기록"
            % (index_fields.get("event_type"), index_fields.get("emit_source")),
            file=sys.stderr,
        )
        return None

    is_defect_event = event_type in ("defect_finding", "fix_transition")

    story_key = index_fields.get("story_key")
    story_key = str(story_key).strip() if story_key else ""
    lane_label = _norm_lane_label(index_fields.get("lane_label"))
    consumer_scope = _norm_consumer_scope(index_fields.get("consumer_scope"))
    defect_id = _norm_hashed_id(index_fields.get("defect_id"))
    fix_id = _norm_hashed_id(index_fields.get("fix_id"))
    blob_ref = _norm_blob_ref(index_fields.get("blob_ref"))

    redaction_applied = bool(index_fields.get("redaction_applied", False))
    redaction_rules_fired = _norm_redaction_rules(index_fields.get("redaction_rules_fired"))
    # redaction_count — caller 주입 우선, 미주입 시 rules_fired 길이로 보정
    rc_raw = index_fields.get("redaction_count")
    redaction_count = _coerce_int(rc_raw, len(redaction_rules_fired))

    defect_family = _norm_defect_family(index_fields.get("defect_family"))
    defect_type = _norm_defect_type(index_fields.get("defect_type"), is_defect_event)
    time_to_detection = _norm_time_to_detection(index_fields.get("time_to_detection"))
    detecting_lane = _norm_enum(index_fields.get("detecting_lane"), _LANE_LABELS, None)
    root_cause_class = _norm_root_cause_class(index_fields.get("root_cause_class"))
    anchor_id = _norm_anchor_id(index_fields.get("anchor_id"))

    # timestamp — caller 가 prev 주입 시 monotonic, 아니면 wall-clock UTC Z
    timestamp_utc = _utc_z_monotonic(index_fields.get("prev_timestamp_utc"))

    event_id = compute_event_id(
        event_type, emit_source, story_key, lane_label, consumer_scope,
        defect_id, fix_id, blob_ref, seq=index_fields.get("seq", ""),
    )

    row = {
        "event_id": event_id,
        "schema_version": _SCHEMA_VERSION,
        "event_type": event_type,
        "emit_source": emit_source,
        "timestamp_utc": timestamp_utc,
        "story_key": story_key,
        "lane_label": lane_label,
        "consumer_scope": consumer_scope,
        "defect_id": defect_id,
        "fix_id": fix_id,
        "blob_ref": blob_ref,
        "redaction_applied": redaction_applied,
        "redaction_count": redaction_count,
        "redaction_rules_fired": redaction_rules_fired,
        "defect_family": defect_family,
        "defect_type": defect_type,
        "time_to_detection": time_to_detection,
        "detecting_lane": detecting_lane,
        "root_cause_class": root_cause_class,
        "anchor_id": anchor_id,
    }
    # 방어적 정합: row 키 == _ROW_KEYS (순서·멤버) — 구성 오류 조기 검출
    assert tuple(row.keys()) == _ROW_KEYS, "build_row key drift vs _ROW_KEYS"
    return row


def _resolve_ledger_path(ledger_path=None):
    """ledger path 결정 — --ledger-path 명시 override 우선, 아니면 default.

    default = ${CLAUDE_PROJECT_DIR}/.claude/ledger/dev-process-event.jsonl
    (append_spawn_event 의 .claude/ledger/ per-channel basename 관례 재사용.)
    """
    if ledger_path:
        return Path(ledger_path)
    proj_dir = os.environ.get("CLAUDE_PROJECT_DIR", "") or "."
    return Path(proj_dir) / _DEFAULT_PARENT_REL / _LEDGER_BASENAME


def append_event(ledger_path=None, **index_fields):
    """dev-process-event-v1 index row 1개를 JSONL 로 append → event_id 반환 (실패 시 None).

    content-blind: allow-list(_ROW_KEYS) 필드만 수용. free-form content 는 수령·저장하지 않는다.
    blob_ref 는 **이미 계산된 str** 로 수령한다 (redaction·blob write 는 sibling/emit 계층 소관).
    non-blocking: 어떤 실패도 raise 하지 않는다 — graceful degrade + return None (caller exit-0).

    ★append 원자성 2축 (change-plan §7.4.1 / ADR-155 Amd1): 완료행 clobber 축은 공유 primitive
      _append_jsonl_row 의 cross-platform kernel-atomic append(POSIX O_APPEND / Windows
      FILE_APPEND_DATA)로 봉인(clobber-free, local NTFS/POSIX 단일-write scope). torn(multi-sector
      interleave) 축은 별개 무주장 — small-row 불변식(<4KB, index=blob-ref only)으로 bounded,
      증명 = Phase 2 StatefulTest.
    """
    try:
        row = build_row(**index_fields)
        if row is None:
            return None
        path = _resolve_ledger_path(ledger_path)
        _append_jsonl_row(path, row)  # 재사용 — O_APPEND per-row, 0600
        return row["event_id"]
    except Exception as exc:  # graceful degradation — 어떤 예외도 exit-0 semantics
        print(
            "[codeforge-dev-process-event] WARN: append failed — %s" % exc,
            file=sys.stderr,
        )
        return None


# ─────────────────────── self-test (execution-backed, hollow 금지) ─────────────

def _self_test():
    """round-trip + 불변식 execution-backed 검증. presence-grep false-oracle 금지."""
    import tempfile
    import re

    failures = []

    def check(cond, msg):
        if not cond:
            failures.append(msg)

    # ── parity guard: build_row 키 순서 == _ROW_KEYS, 길이 20 (CFP-2985 D-12) ──
    check(len(_ROW_KEYS) == 20, f"_ROW_KEYS 길이 {len(_ROW_KEYS)} != 20")
    check(len(set(_ROW_KEYS)) == len(_ROW_KEYS), "_ROW_KEYS 중복 키 존재")

    tmpdir = tempfile.mkdtemp(prefix="dev-process-selftest-")
    ledger = os.path.join(tmpdir, "dev-process-event.jsonl")

    # ── 케이스 1: agent-emit lane_transition round-trip ──
    eid1 = append_event(
        ledger_path=ledger,
        event_type="lane_transition", emit_source="agent",
        story_key="CFP-2687", lane_label="구현", consumer_scope="wrapper",
        redaction_applied=False, redaction_count=0,
        content="THIS FREE-FORM SHOULD BE DROPPED",  # allow-list 밖 — content-blind
        transcript_path="/home/user/secret",          # allow-list 밖 — drop
    )
    check(eid1 is not None and len(eid1) == 64, f"[c1] event_id 부적합: {eid1!r}")

    with open(ledger, encoding="utf-8") as f:
        rows = [json.loads(ln) for ln in f if ln.strip()]
    check(len(rows) == 1, f"[c1] row count {len(rows)} != 1")
    r1 = rows[0]
    check(tuple(r1.keys()) == _ROW_KEYS, "[c1] row 키 순서 != _ROW_KEYS (parity)")
    # content-blindness: allow-list 밖 키 미유입
    check("content" not in r1 and "transcript_path" not in r1,
          "[c1] free-form content 유입 (content-blind 위반)")
    check(r1["schema_version"] == _SCHEMA_VERSION, "[c1] schema_version 불일치")
    check(r1["timestamp_utc"].endswith("Z"), "[c1] timestamp_utc UTC Z strict 아님")
    check(bool(re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$", r1["timestamp_utc"])),
          f"[c1] timestamp_utc ms-precision UTC Z 형식 아님: {r1['timestamp_utc']}")
    check(r1["lane_label"] == "구현", "[c1] lane_label 손상")
    check(r1["defect_id"] is None and r1["fix_id"] is None, "[c1] non-defect defect_id/fix_id != null")

    # ── 케이스 2: event_id 결정성 (동일 논리 이벤트 = 동일 id, timestamp 무관) ──
    idA = compute_event_id("verdict", "agent", "CFP-2687", "구현-리뷰", "wrapper", seq="1")
    idB = compute_event_id("verdict", "agent", "CFP-2687", "구현-리뷰", "wrapper", seq="1")
    idC = compute_event_id("verdict", "agent", "CFP-2687", "구현-리뷰", "wrapper", seq="2")
    check(idA == idB, "[c2] 동일 논리 이벤트 event_id 불일치 (결정성 위반)")
    check(idA != idC, "[c2] seq 다른데 event_id 동일 (disambiguation 실패)")

    # ── 케이스 3: defect_finding taxonomy + redaction audit ──
    eid3 = append_event(
        ledger_path=ledger,
        event_type="defect_finding", emit_source="agent",
        story_key="CFP-2687", lane_label="설계-리뷰",
        defect_id="a" * 64, defect_family="design-boundary",
        defect_type="boundary-completeness", time_to_detection=2,
        detecting_lane="설계-리뷰",
        blob_ref="b" * 64,
        redaction_applied=True, redaction_count=2,
        # 실 producer(redact_dev_process_content) 어휘 + 미등재 1개(drop 대상)
        redaction_rules_fired=["api_key_credential", "abs_or_home_path", "NOT-A-RULE"],
    )
    check(eid3 is not None, "[c3] defect_finding append 실패")
    with open(ledger, encoding="utf-8") as f:
        rows = [json.loads(ln) for ln in f if ln.strip()]
    r3 = rows[-1]
    check(r3["defect_family"] == "design-boundary", "[c3] defect_family 손상")
    check(r3["defect_type"] == "boundary-completeness", "[c3] defect_type 손상")
    check(r3["time_to_detection"] == 2, "[c3] time_to_detection 손상")
    check(r3["detecting_lane"] == "설계-리뷰", "[c3] detecting_lane 손상")
    check(r3["blob_ref"] == "b" * 64, "[c3] blob_ref 손상")
    check(r3["redaction_applied"] is True and r3["redaction_count"] == 2, "[c3] audit 손상")
    check(r3["redaction_rules_fired"] == ["api_key_credential", "abs_or_home_path"],
          f"[c3] redaction_rules 미등재 drop 실패: {r3['redaction_rules_fired']}")
    # ★producer 어휘 정합(fail-loud, 양방향 EQUALITY): append enum == redact.RULE_NAMES.
    #   미래에 누군가 _REDACTION_RULES 를 divergent 하드코딩으로 바꾸면 여기서 RED (silent 드리프트 차단).
    from redact_dev_process_content import RULE_NAMES as _PROD_RULES
    check(set(_REDACTION_RULES) == set(_PROD_RULES),
          f"[c3] append._REDACTION_RULES != redact.RULE_NAMES (audit enum 드리프트) — "
          f"append_only={sorted(set(_REDACTION_RULES) - set(_PROD_RULES))} "
          f"redact_only={sorted(set(_PROD_RULES) - set(_REDACTION_RULES))}")
    # 실 producer 이름 non-email 통과 (PL 지정 reproducer): abs path + token → 이름 보존 (not [])
    check(_norm_redaction_rules(["abs_or_home_path", "github_pat"]) == ["abs_or_home_path", "github_pat"],
          "[c3] non-email rule 이름이 index 진입 전 drop 됨 (AC-14/T-DPE-8 fidelity 위반)")

    # ── 케이스 4: invalid required enum → None (malformed 회피) ──
    eid4 = append_event(
        ledger_path=ledger, event_type="NONSENSE", emit_source="agent",
    )
    check(eid4 is None, "[c4] invalid event_type 에도 row 기록됨 (allow-list-clean 위반)")
    eid4b = append_event(
        ledger_path=ledger, event_type="verdict", emit_source="telepathy",
    )
    check(eid4b is None, "[c4] invalid emit_source 에도 row 기록됨")

    # ── 케이스 5: raw id sha256 처리 (raw 저장 금지 — content-blind) ──
    eid5 = append_event(
        ledger_path=ledger, event_type="fix_transition", emit_source="agent",
        story_key="CFP-2687", lane_label="구현",
        defect_id="raw-defect-summary-with-location", fix_id="attempt-1",
    )
    with open(ledger, encoding="utf-8") as f:
        rows = [json.loads(ln) for ln in f if ln.strip()]
    r5 = rows[-1]
    check(_is_sha256_hex(r5["defect_id"]), "[c5] raw defect_id 가 sha256 처리 안 됨")
    check(_is_sha256_hex(r5["fix_id"]), "[c5] raw fix_id 가 sha256 처리 안 됨")

    # ── 케이스 7 (★CFP-2985 D-12/D-16): root_cause_class · anchor_id 적재 경계 ──
    #   양성 ∧ 음성 공존 — 수용만 보면 술어가 상시 참이어도 통과한다(판별력 0).
    eid7 = append_event(
        ledger_path=ledger, event_type="fix_transition", emit_source="agent",
        story_key="CFP-2985", lane_label="구현-리뷰",
        root_cause_class="설계-리뷰", anchor_id="§5.3",
    )
    check(eid7 is not None, "[c7] 신규 2 필드 정상값에 row 미기록")
    with open(ledger, encoding="utf-8") as f:
        rows = [json.loads(ln) for ln in f if ln.strip()]
    r7 = rows[-1]
    check(tuple(r7.keys()) == _ROW_KEYS, "[c7] row 키 순서 != _ROW_KEYS (20-field parity)")
    check(r7["root_cause_class"] == "설계-리뷰", f"[c7] CLOSED-6 멤버 손상: {r7['root_cause_class']!r}")
    check(r7["anchor_id"] == "§5.3", f"[c7] §<section-ref> 형식 거부됨: {r7['anchor_id']!r}")
    # 음성 leg — 값공간 밖 / Story-scoped 형상은 적재되지 않는다
    check(_norm_root_cause_class("설계-리뷰-리뷰") is None, "[c7] CLOSED-6 밖 값이 적재됨")
    check(_norm_root_cause_class("**설계**") is None,
          "[c7] 장식 변형이 적재 경계를 통과 — 표기 흡수는 집계 층 책임(D-13)이며 여기선 비-멤버다")
    check(_norm_root_cause_class(None) is None, "[c7] None 이 값으로 바뀜")
    check(_norm_anchor_id("cfp-2985-requirements-divergence-1") is None,
          "[c7] Story-scoped anchor 가 적재됨 — pattern_count 가 정의상 1 로 고정된다(§3.4)")
    check(_norm_anchor_id("CFP-2985-foo") is None, "[c7] 대문자 Story-scoped 형상 미거부")
    check(_norm_anchor_id("docs/inter-plugin-contracts/fix-event-v1.md:81")
          == "docs/inter-plugin-contracts/fix-event-v1.md:81", "[c7] <path>:<line> 형식 거부됨")
    check(_norm_anchor_id("/etc/passwd:1") is None, "[c7] 절대경로 anchor 가 적재됨")
    check(_norm_anchor_id("자유 서술 텍스트") is None, "[c7] free-form 문자열이 적재됨 (J-2 위반)")
    check(_norm_anchor_id("§" + "x" * 300) is None, "[c7] bounded token 상한 미작동")
    # ★ 판별력 대조 — 두 필드가 allow-list 밖 kwarg 처럼 drop 되지 않음을 별 축으로 고정
    check("root_cause_class" in r7 and "anchor_id" in r7, "[c7] 신규 필드가 row 에서 소실")

    # ── 케이스 6: monotonic timestamp (prev 주입 시 MAX(prev+1ms) — design literal) ──
    ts = _utc_z_monotonic("2099-01-01T00:00:00.500Z")
    check(ts == "2099-01-01T00:00:00.501Z", f"[c6] monotonic +1ms 미보장: {ts}")
    # 초 해상도 prev 도 관용 파싱 → +1ms
    ts_sec = _utc_z_monotonic("2099-01-01T00:00:00Z")
    check(ts_sec == "2099-01-01T00:00:00.001Z", f"[c6] 초해상도 prev +1ms 실패: {ts_sec}")

    # cleanup
    try:
        os.remove(ledger)
        os.rmdir(tmpdir)
    except OSError:
        pass

    if failures:
        print("[append_dev_process_event --self-test] FAIL")
        for m in failures:
            print("  - " + m)
        return 1

    print(
        "[append_dev_process_event --self-test] PASS "
        f"(_ROW_KEYS={len(_ROW_KEYS)} fields; round-trip OK; content-blind OK; "
        f"event_id 결정성 OK; taxonomy+audit OK; invalid-enum→None OK; "
        f"raw-id→sha256 OK; monotonic OK; root_cause_class/anchor_id 적재 경계 OK)"
    )
    return 0


# ─────────────────────── CLI ──────────────────────────────────────────────────────

def _build_parser():
    p = argparse.ArgumentParser(
        description="dev-process-event-v1 index row append (CFP-2687 Phase 2 / Epic #2686 A)"
    )
    p.add_argument("--self-test", action="store_true", help="execution-backed self-test")
    p.add_argument("--print-row-keys", action="store_true",
                   help="_ROW_KEYS 를 1줄씩 출력 (parity self-test anchor)")
    p.add_argument("--ledger-path", default="", help="ledger jsonl full path override (test/직접)")
    p.add_argument("--event-type", default=None, help="event_type closed enum (8종)")
    p.add_argument("--emit-source", default=None, help="emit_source enum {hook, agent}")
    p.add_argument("--story-key", default="", help="story_key — e.g. CFP-2687")
    p.add_argument("--lane-label", default="", help="lane_label closed enum (미매칭 → 없음)")
    p.add_argument("--consumer-scope", default=None, help="consumer_scope {wrapper, consumer}")
    return p


def main():
    args = _build_parser().parse_args()
    if args.self_test:
        return _self_test()
    if args.print_row_keys:
        for k in _ROW_KEYS:
            print(k)
        return 0
    # graceful degradation — 어떤 예외도 exit 0 (record-only, ADR-115)
    eid = append_event(
        ledger_path=(args.ledger_path or None),
        event_type=args.event_type,
        emit_source=args.emit_source,
        story_key=args.story_key,
        lane_label=args.lane_label,
        consumer_scope=args.consumer_scope,
    )
    if eid:
        print(eid)
    return 0


if __name__ == "__main__":
    sys.exit(main())
