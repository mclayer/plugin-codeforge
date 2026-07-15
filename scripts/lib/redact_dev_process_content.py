#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# redact_dev_process_content.py — dev-process-event-v1 capture-time redaction (INV-8 floor)
#
# Carrier: CFP-2687 Phase 2 (구현) / Epic #2686 Story A — dev-process observability substrate
# 설계 SSOT: ADR-155 §결정 5(INV-8a/8b) + ADR-043 Amendment 4(privacy 계약 상속·확장)
#           + change-plan 2026-07-15-cfp-2687 §7.2(blob deny-pattern) / §7.3(audit) / §7.5(bound)
#           + Story CFP-2687 §5.3 AC-12/13/14 + §5.4 엣지케이스.
#
# 책임:
#   - evidence-blob-store 에 저장되기 前(capture-time) rich content 를 in-memory redact.
#   - denylist + pattern 기반: 토큰/API key/쿠키/Authorization·Cookie 헤더/cloud-key/
#     절대·home-prefixed 경로 → REDACT. repo-relative 경로는 보존(diff 진단 신호=public,
#     무차별 redact=noise false-negative 실패원인 소실, Story §5.4).
#   - env dump·자격증명 subprocess 출력 = 통째 제외(drop/redact whole).
#   - session_id = sha256 만(raw 미저장 — append_stop_event.py:73 raw session_id BUG 미복사).
#
# ADR-043 §결정 3 deny-regex 6종 상속 + Amendment 4 §결정 3 7번째(경로) 추가:
#   1 api_key_credential / 2 github_pat / 3 github_fine_grained_pat /
#   4 kr_rrn(주민번호) / 5 email / 6 hex_high_entropy  (← 상속 6종)
#   7 abs_or_home_path  (← Amd4 신규)  + auth/cookie header / cloud_key / private_key /
#   env_dump / credential_subprocess / session_id  (← Amd4 §D + §7.2 net-new 표면)
#
# audit(T-DPE-8 — audit-oracle 역전 차단):
#   {"redaction_applied": bool, "redaction_count": int, "redaction_rules_fired": [rule enum]}
#   매칭된 secret 원문/hash 는 audit 에 절대 미기록 — 규칙명 + 횟수만. mandatory-on-fire.
#
# born-safe bound(T-DPE-10):
#   byte-cap + line-cap + coarse parse-timeout. over-cap 입력 → bounded truncation, non-blocking.
#
# ── 정직 천장(ADR-119 / CFP-2635·2646 self-ref 선례) ──────────────────────────
#   본 모듈은 임의·적대적 입력에 대한 무해성을 단정하지 않는다. nested quantifier 를
#   실무상 회피하나(선형 성향 regex 선호), 보장하는 것은 byte/line/timeout cap 을 통한
#   bounded degradation 뿐이며 임의 입력에 대해 immune 하지 않다. 실증 = Phase 2 SecurityTest.
#   (∴ "immune"·"proof-by-construction" 류 단정 없음 — 계약 §7.5 honest-ceiling 정합.)
#
# 계약 property: redact(redact(x)) == redact(x) (idempotent).
# 사용: from redact_dev_process_content import redact ; redacted, audit = redact(raw)

import hashlib
import math
import re
import sys
import time
from collections import Counter

# Windows cp949 회피: 직접 실행 시 stdout/stderr UTF-8 (ADR-061 portability 정합)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


# ─────────────────────── born-safe bound 상수 (proposal, tunable — 수치 lock-in 금지) ───
# empirical 확정 = Phase 2 SecurityTest. 아래는 born-safe 기본값(proposal).
BYTE_CAP = 1_048_576          # 1 MiB — redaction pass 입력 byte 상한
LINE_CAP = 20_000             # 라인 수 상한
PARSE_TIMEOUT_S = 2.0         # redaction pass coarse wall-clock deadline (초)

# cloud-key entropy 임계(gitleaks 차용 보강 — Shannon bits/char) + generic 토큰 최소 길이
CLOUD_ENTROPY_MIN = 4.0
CLOUD_GENERIC_MIN_LEN = 40

# env-dump whole-content 판정 임계(conservative — 일반 diff 오탐 회피)
ENV_DUMP_MIN_LINES = 8
ENV_DUMP_MIN_RATIO = 0.6

# session_id → sha256 truncate 길이(hex). 12 < 32 이라 hex_high({32,}) self-match 회피
#  → idempotence 보존. audit_trail_pii_redact.py hex[:12] 선례 답습.
_SID_HEX_LEN = 12

# 경계 마커(redaction rule 아님 — bound 표식). 재실행 시 재매칭 불가한 형태.
_TRUNC_MARKER = "\n[REDACT-BOUND:truncated]\n"


# ─────────────────────── closed enum rule 이름 (audit allow-set) ────────────────────
RULE_ENV_DUMP = "env_dump_excluded"
RULE_CRED_SUBPROC = "credential_subprocess_excluded"
RULE_PRIVATE_KEY = "private_key_block"
RULE_AUTH_HEADER = "authorization_header"
RULE_COOKIE_HEADER = "cookie_header"
RULE_ABS_PATH = "abs_or_home_path"
RULE_SESSION_ID = "session_id"
RULE_GITHUB_PAT = "github_pat"
RULE_GITHUB_FGPAT = "github_fine_grained_pat"
RULE_CLOUD_KEY = "cloud_key"
RULE_API_KEY = "api_key_credential"
RULE_KR_RRN = "kr_rrn"
RULE_EMAIL = "email"
RULE_HEX = "hex_high_entropy"

RULE_NAMES = frozenset({
    RULE_ENV_DUMP, RULE_CRED_SUBPROC, RULE_PRIVATE_KEY, RULE_AUTH_HEADER,
    RULE_COOKIE_HEADER, RULE_ABS_PATH, RULE_SESSION_ID, RULE_GITHUB_PAT,
    RULE_GITHUB_FGPAT, RULE_CLOUD_KEY, RULE_API_KEY, RULE_KR_RRN,
    RULE_EMAIL, RULE_HEX,
})


def _ph(rule):
    """redaction placeholder — 재매칭 불가 형태(idempotence 보존). secret 미포함."""
    return "[REDACTED:%s]" % rule


# ─────────────────────── compiled patterns ────────────────────────────────────────
# (선형 성향 우선 — negated-class 단일 quantifier. inherited 6 = ADR-043 §결정 3 verbatim.)

# 상속 6종 (ADR-043 §결정 3 표)
_RE_API_KEY = re.compile(
    r"(?i)(api[_-]?key|secret|token|password|bearer)\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{16,}"
)
_RE_GITHUB_PAT = re.compile(r"ghp_[A-Za-z0-9]{36}")
_RE_GITHUB_FGPAT = re.compile(r"github_pat_[A-Za-z0-9_]{82}")
_RE_KR_RRN = re.compile(r"\d{6}[-\s]?\d{7}")
_RE_EMAIL = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")
_RE_HEX = re.compile(r"[a-f0-9]{32,}")

# 7번째 (Amd4) — 절대/home-prefixed 경로만. repo-relative(선행 `/`·drive 없음)는 보존.
#   · Windows drive:      X:\... (단일 negated-class star, nested quantifier 없음)
#   · POSIX home:         /home /Users /root ...
#   · git-bash mount:     /c/Users... (단일 letter drive + 디렉터리 세그먼트)
#     ★F-CR-002 tighten: URL host 뒤 경로(https://h/a/b/c)·HTTP 요청경로(/v/1/users)는
#       진단 신호(secret 아님)이므로 보존 — 2개 판별축으로 실제 mount 만 좁게 매칭:
#       (1) 선행 host-char(영숫자·`.`) 부재 negative lookbehind → URL host 뒤 경로 배제
#       (2) 2nd-level 세그먼트가 letter 로 시작 → `/v/1/...`(digit 2nd-level) 요청경로 배제
#       (/c/Users·/c/workspace 등 실 mount 는 무손상 redact 유지.)
_RE_ABS_PATH = re.compile(
    r"[A-Za-z]:\\[^\s'\"]*"
    r"|/(?:home|Users|root)[^\s'\"]*"
    r"|(?<![A-Za-z0-9.])/[a-zA-Z]/[A-Za-z][^\s'\"]*"
)

# Authorization 헤더 — scheme + 단일 토큰만(라인 전체 greedy 소비 회피 → 병기된 다른
#  신호[경로 등] 오버-redact 방지, Story §5.4 noise false-negative 정합).
_RE_AUTH_HEADER = re.compile(
    r"(?i)authorization\s*:\s*(?:bearer|basic|digest|negotiate|token)?\s*[A-Za-z0-9._+/=\-]{3,}"
)
# Cookie/Set-Cookie 헤더 — 라인 지향(헤더 dump). 라인 끝까지.
_RE_COOKIE_HEADER = re.compile(r"(?im)^(\s*(?:set-)?cookie)\s*:\s*[^\r\n]+$")

# session_id 명시 대입형만 → sha256(truncate) 치환. 전체 매치 치환(=재매칭 불가).
_RE_SESSION_ID = re.compile(
    r"(?i)session[_-]?id\s*[:=]\s*['\"]?([A-Za-z0-9_\-]{6,})['\"]?"
)

# cloud-key 구조 패턴(gitleaks 차용) — AWS/GCP/Slack. + 아래 entropy-gated generic 병행.
_RE_CLOUD_STRUCT = re.compile(
    r"A(?:KIA|SIA)[0-9A-Z]{16}"          # AWS access key id
    r"|AIza[0-9A-Za-z_\-]{35}"           # Google API key
    r"|xox[baprs]-[0-9A-Za-z\-]{10,}"    # Slack token
)
_RE_CLOUD_GENERIC = re.compile(r"[A-Za-z0-9/+=_\-]{%d,}" % CLOUD_GENERIC_MIN_LEN)

# PEM private key block(block-level)
_RE_PRIVATE_KEY = re.compile(
    r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----.*?-----END [A-Z0-9 ]*PRIVATE KEY-----",
    re.DOTALL,
)

# env dump 판정용 라인 대입 signature
_RE_ENV_ASSIGN = re.compile(r"^\s*[A-Za-z_][A-Za-z0-9_]*=[^=\r\n]")
# 자격증명 subprocess 출력 signature(aws credentials/`aws configure list`)
_RE_CRED_SIG = re.compile(r"(?i)aws_secret_access_key|aws_session_token")


# ─────────────────────── audit accumulator (secret 원문/hash 절대 미기록) ─────────────
class _Audit:
    """T-DPE-8 정합 — 규칙명 + 횟수만. 매칭 secret 원문/hash 는 절대 담지 않는다."""

    def __init__(self):
        self.count = 0
        self.rules = set()

    def fire(self, rule, n=1):
        if n <= 0:
            return
        # 방어: closed enum 외 rule 이름 유입 차단(오탈자·오염 시 조용히 무시).
        if rule not in RULE_NAMES:
            return
        self.count += n
        self.rules.add(rule)

    def to_dict(self):
        return {
            "redaction_applied": self.count > 0,
            "redaction_count": self.count,
            "redaction_rules_fired": sorted(self.rules),
        }


# ─────────────────────── helpers ───────────────────────────────────────────────────
def _shannon_entropy(s):
    """Shannon entropy(bits/char). 빈 문자열 → 0.0."""
    if not s:
        return 0.0
    n = len(s)
    return -sum((c / n) * math.log2(c / n) for c in Counter(s).values())


def _sha256_hex12(value):
    """session_id → sha256 truncate(12 hex). raw 미저장 — hex12(<32)이라 hex_high self-match 회피."""
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:_SID_HEX_LEN]


def _apply_bounds(text):
    """byte-cap → line-cap 순 bounded truncation(non-blocking). bound 마커는 redaction 아님."""
    truncated = False
    data = text.encode("utf-8", errors="replace")
    if len(data) > BYTE_CAP:
        text = data[:BYTE_CAP].decode("utf-8", errors="ignore")
        truncated = True
    lines = text.split("\n")
    if len(lines) > LINE_CAP:
        text = "\n".join(lines[:LINE_CAP])
        truncated = True
    if truncated:
        text = text + _TRUNC_MARKER
    return text


def _sub_count(pattern, repl_str, text):
    """re.sub + 실제 치환 횟수. repl_str = 정적 placeholder 문자열."""
    new_text, n = pattern.subn(lambda _m: repl_str, text)
    return new_text, n


# ─────────────────────── whole-content 제외(early return 신호) ────────────────────────
def _looks_like_env_dump(text):
    """env dump 판정 — 대입형 라인이 다수 + 비율 지배적일 때만(conservative)."""
    non_empty = [ln for ln in text.split("\n") if ln.strip()]
    if len(non_empty) < ENV_DUMP_MIN_LINES:
        return False
    assign = sum(1 for ln in non_empty if _RE_ENV_ASSIGN.match(ln))
    return assign >= ENV_DUMP_MIN_LINES and (assign / len(non_empty)) >= ENV_DUMP_MIN_RATIO


def _looks_like_credential_subprocess(text):
    """자격증명 subprocess 출력 signature — aws secret/session token 존재."""
    return _RE_CRED_SIG.search(text) is not None


# ─────────────────────── 개별 redaction 단계 ─────────────────────────────────────────
def _redact_private_key(text, audit):
    text, n = _sub_count(_RE_PRIVATE_KEY, _ph(RULE_PRIVATE_KEY), text)
    audit.fire(RULE_PRIVATE_KEY, n)
    return text


def _redact_headers(text, audit):
    text, n = _sub_count(_RE_AUTH_HEADER, "Authorization: " + _ph(RULE_AUTH_HEADER), text)
    audit.fire(RULE_AUTH_HEADER, n)
    text, n = _RE_COOKIE_HEADER.subn(r"\1: " + _ph(RULE_COOKIE_HEADER), text)
    audit.fire(RULE_COOKIE_HEADER, n)
    return text


def _redact_session_id(text, audit):
    """session_id 대입형 → sha256(hex12) 치환. 전체 매치 치환 = 재매칭 불가."""
    counter = {"n": 0}

    def _repl(m):
        counter["n"] += 1
        return "[REDACTED-SESSION:%s]" % _sha256_hex12(m.group(1))

    text = _RE_SESSION_ID.sub(_repl, text)
    audit.fire(RULE_SESSION_ID, counter["n"])
    return text


def _redact_cloud_generic(text, audit):
    """entropy-gated generic — 40+ 연속 토큰 중 고엔트로피만(오탐 회피). specific 룰 後 최종망.

    구체 룰(github_pat/api_key/hex 등)이 먼저 redact 하도록 pipeline 최후미에 배치 —
    full-length ghp 토큰(정확히 40자) 등이 generic catch-all 에 shadow 되어 audit 오귀속되는
    것을 방지(구체 룰 우선 → audit fidelity)."""
    counter = {"n": 0}

    def _repl(m):
        tok = m.group(0)
        if _shannon_entropy(tok) >= CLOUD_ENTROPY_MIN:
            counter["n"] += 1
            return _ph(RULE_CLOUD_KEY)
        return tok

    text = _RE_CLOUD_GENERIC.sub(_repl, text)
    audit.fire(RULE_CLOUD_KEY, counter["n"])
    return text


# (pattern, rule) 순서 — abs_path 는 token 룰 前(전체 경로 원자 redact),
#  github/cloud-struct/api 등 특정 prefix 룰은 hex/email/generic 前(구체 우선).
def _redact_patterns(text, audit, deadline):
    steps = [
        (_RE_ABS_PATH, RULE_ABS_PATH),
        (_RE_GITHUB_PAT, RULE_GITHUB_PAT),
        (_RE_GITHUB_FGPAT, RULE_GITHUB_FGPAT),
        (_RE_CLOUD_STRUCT, RULE_CLOUD_KEY),   # 구조 cloud-key(AWS/GCP/Slack) — 구체 prefix
        (_RE_API_KEY, RULE_API_KEY),
        (_RE_KR_RRN, RULE_KR_RRN),
        (_RE_EMAIL, RULE_EMAIL),
        (_RE_HEX, RULE_HEX),
    ]
    for pattern, rule in steps:
        if time.monotonic() > deadline:
            break  # coarse parse-timeout — 남은 룰 중단(bounded degradation, non-blocking)
        text, n = _sub_count(pattern, _ph(rule), text)
        audit.fire(rule, n)
    return text


# ─────────────────────── public: redact ─────────────────────────────────────────────
def redact(raw):
    """
    dev-process rich content capture-time redaction.

    Returns (redacted_text: str, audit: dict).
      audit = {"redaction_applied": bool, "redaction_count": int,
               "redaction_rules_fired": [<closed enum rule 이름>]}
    audit 는 규칙명 + 횟수만 담는다(T-DPE-8 — secret 원문/hash 절대 미기록).

    born-safe bound: byte/line cap + coarse parse-timeout(non-blocking).
    property: redact(redact(x)) == redact(x) (idempotent).

    ── 정직 천장(ADR-119): 임의·적대적 입력 무해성은 단정하지 않는다. 보장 = byte/line/
       timeout cap 기반 bounded degradation 뿐(immune 아님). 실증 = Phase 2 SecurityTest.
    """
    audit = _Audit()
    text = raw if isinstance(raw, str) else ("" if raw is None else str(raw))

    # 1) born-safe bound(bound 마커는 redaction rule 아님 → count 미증가)
    text = _apply_bounds(text)

    deadline = time.monotonic() + PARSE_TIMEOUT_S

    # 2) whole-content 제외(early return) — env dump / 자격증명 subprocess 출력은 통째 drop
    if _looks_like_env_dump(text):
        audit.fire(RULE_ENV_DUMP, 1)
        return _ph(RULE_ENV_DUMP), audit.to_dict()
    if _looks_like_credential_subprocess(text):
        audit.fire(RULE_CRED_SUBPROC, 1)
        return _ph(RULE_CRED_SUBPROC), audit.to_dict()

    # 3) block-level → header → session_id → 구체 pattern → generic cloud(최종망)
    text = _redact_private_key(text, audit)
    if time.monotonic() <= deadline:
        text = _redact_headers(text, audit)
    if time.monotonic() <= deadline:
        text = _redact_session_id(text, audit)
    text = _redact_patterns(text, audit, deadline)
    if time.monotonic() <= deadline:
        text = _redact_cloud_generic(text, audit)

    return text, audit.to_dict()
