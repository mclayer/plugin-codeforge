#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# dev_process_blob_store.py — dev-process-event-v1 content-addressed evidence-blob-store
#
# Carrier: CFP-2687 Phase 2 (구현) / Epic #2686 Story A — dev-process observability substrate
# 설계 SSOT: ADR-155 §결정 5(INV-8a/8b) + §결정 6(retention 3-tier / tombstone / GC)
#           + change-plan 2026-07-15-cfp-2687 §7.4.2(blob GC) / §11.2(AC-10∧AC-25 화해)
#           + Story CFP-2687 §5.3 AC-8/9/25 + §5.4 엣지케이스(blob hash 기준/cross-host/spill).
#
# 책임(2계층 중 blob 표면 — index tier 는 append_dev_process_event.py 소유):
#   - capture_blob: redaction-선행 → hash-over-redacted → content-addressed blob write.
#   - deref_blob: redacted bytes 조회(cold-evict 시 None — silent-corrupt 금지). FROZEN name.
#   - prune_blobs: off-hot-path grace-period GC + tombstone(append-only blob-evicted 증거).
#   - warm_compress_blob: content-preserving hash-verified transform(hash(decompressed)==blob_ref).
#
# ★INV-8a (비협상, T-DPE-1 redaction-order + T-DPE-2 hash-over-redacted):
#     (1) redact(raw) in-memory — 원본은 disk 미접촉
#     (2) blob_ref = sha256(REDACTED bytes)  ← NEVER raw (hash-over-unredacted = confirmation oracle)
#     (3) REDACTED bytes 를 content-addressed blob 로 write
# ★INV-8b (T-DPE-5 blob-before-index): blob write → THEN index row(blob_ref).
#     본 모듈은 INV-8b 의 "blob write" 절반만 보장한다 — capture_blob 반환 前 blob 이
#     완결 write+반환됨. index row 는 CALLER(hook/emit layer)가 반환 후에 기록한다.
#     ∴ index 기록은 본 모듈 책임 아님(호출자 계약). 역순 기록 = dangling evidence chain.
#
# T-DPE-7 host-local: dedup = intra-store only(같은 blob_ref → 파일 재사용). cross-host 공유/
#   exfiltration 금지 — 0-API, 로컬 파일 I/O only.
#
# graceful degradation(ADR-115): capture 실패 = non-blocking. 어떤 예외도 raise 하지 않고
#   (None, audit) 반환(원 실행 흐름 차단 금지, exit-0 등가).
#
# ── 정직 천장(ADR-119) ─────────────────────────────────────────────────────────────
#   본 모듈은 write 원자성에 대해 "kernel-level" 류 단정을 하지 않는다. os.replace 는
#   동일 filesystem 안 rename semantics 이며(POSIX rename / Windows MoveFileEx) torn-write
#   회피를 위한 write-temp-then-rename 만 제공한다. redaction pass 의 무해성 단정도 없음
#   (redact_dev_process_content 의 bounded-degradation 상속, 실증 = Phase 2 SecurityTest).

import gzip
import hashlib
import json
import os
import sys
import tempfile
import time
from pathlib import Path

# Windows cp949 회피(ADR-061)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# redaction 선행(INV-8a step 1) — 동일 scripts/lib. import 실패 시 path fallback.
try:
    from redact_dev_process_content import redact
except Exception:  # pragma: no cover — import path fallback
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from redact_dev_process_content import redact


# ─────────────────────── 상수(proposal, tunable — 수치 lock-in 금지, empirical Phase 2) ──
_STORE_REL = os.path.join(".claude-work", "dev-process")   # store root(project 상대)
_BLOBS_DIR = "blobs"                                        # hot tier loose blob
_WARM_DIR = "warm"                                          # warm tier 압축 pack(.gz)
_TOMBSTONE_LEDGER = "blob-evicted.jsonl"                    # append-only eviction 증거

BLOB_SIZE_CAP = 8 * 1_048_576      # 8 MiB — 단일 blob byte 상한(초과 시 truncate-with-marker)
MIN_CAPTURE_BYTES = 1              # 이 미만(=빈 내용) → blob 미생성(index blob-less)
GC_GRACE_DAYS = 14                 # grace-period prune 기본 2주(proposal, git-gc pruneExpire 차용)

_BLOB_TRUNC_MARKER = b"\n[BLOB-BOUND:size-cap-truncated]\n"
_SHA256_HEX_LEN = 64


# ─────────────────────── path helpers ──────────────────────────────────────────────
def _default_root():
    """store root = ${CLAUDE_PROJECT_DIR}/.claude-work/dev-process (미설정 시 상대)."""
    proj = os.environ.get("CLAUDE_PROJECT_DIR", "") or "."
    return Path(proj) / _STORE_REL


def _resolve_root(root):
    return _default_root() if root is None else Path(root)


def _is_valid_ref(blob_ref):
    """blob_ref = 64-hex sha256 만 허용(path traversal 차단)."""
    if not isinstance(blob_ref, str) or len(blob_ref) != _SHA256_HEX_LEN:
        return False
    return all(c in "0123456789abcdef" for c in blob_ref)


def _blob_path(root, blob_ref):
    """content-addressed 경로 — blobs/<ref[:2]>/<ref> (loose blob = hot tier)."""
    return _resolve_root(root) / _BLOBS_DIR / blob_ref[:2] / blob_ref


def _warm_path(root, blob_ref):
    """warm tier 압축 pack 경로 — warm/<ref[:2]>/<ref>.gz."""
    return _resolve_root(root) / _WARM_DIR / blob_ref[:2] / (blob_ref + ".gz")


def _chmod_600(path):
    """0600(Unix). Windows = ACL 영역 외 no-op."""
    try:
        os.chmod(str(path), 0o600)
    except (OSError, AttributeError):
        pass


def _atomic_write_bytes(path, data):
    """write-temp-then-rename — torn-write(부분 blob) 회피. 0600. newline 변환 없음(bytes)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=".blob-tmp-")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
        _chmod_600(tmp)
        os.replace(tmp, str(path))
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise
    _chmod_600(path)


# ─────────────────────── public: capture_blob (INV-8a) ─────────────────────────────
def capture_blob(raw, root=None):
    """
    rich content 를 evidence blob 로 capture. INV-8a 순서 강제.

    Returns (blob_ref: str | None, audit: dict).
      · blob_ref = sha256(REDACTED bytes) hex (NEVER raw — T-DPE-2 oracle 봉인).
      · 빈/too-small 내용 → (None, audit)  (index blob-less 유지).
      · 실패 → (None, audit)  (graceful degrade, non-blocking — 예외 raise 안 함).

    ★INV-8b: 본 함수는 blob 이 write+반환됨만 보장. index row 는 CALLER 가 반환 後 기록.
    """
    # raw 사전 판정(빈 내용은 redaction 불요 — INV-8a 원본 disk 미접촉과 무저촉)
    if raw is None:
        return None, {"redaction_applied": False, "redaction_count": 0,
                      "redaction_rules_fired": []}

    try:
        # (1) redact — in-memory, 원본 disk 미접촉 (INV-8a step 1)
        redacted, audit = redact(raw)

        # too-small → blob 미생성
        redacted_bytes = redacted.encode("utf-8", errors="replace")
        if len(redacted_bytes) < MIN_CAPTURE_BYTES:
            return None, audit

        # size-cap + spill(bounded truncate-with-marker) — hash 는 최종 write bytes 기준
        if len(redacted_bytes) > BLOB_SIZE_CAP:
            redacted_bytes = redacted_bytes[:BLOB_SIZE_CAP] + _BLOB_TRUNC_MARKER

        # (2) blob_ref = sha256(REDACTED bytes) — NEVER raw (INV-8a step 2)
        blob_ref = hashlib.sha256(redacted_bytes).hexdigest()

        # (3) content-addressed write(REDACTED). dedup = intra-store only(T-DPE-7):
        #     같은 blob_ref 파일 존재 → 재사용(재write 안 함, cross-host 공유 없음).
        path = _blob_path(root, blob_ref)
        if not path.exists():
            _atomic_write_bytes(path, redacted_bytes)

        return blob_ref, audit
    except Exception as exc:
        # graceful degradation(ADR-115) — capture 실패는 원 흐름 차단 금지
        sys.stderr.write("[dev-process-blob] WARN: capture_blob failed — %s\n" % exc)
        return None, {"redaction_applied": False, "redaction_count": 0,
                      "redaction_rules_fired": []}


# ─────────────────────── public: deref_blob (FROZEN name) ──────────────────────────
def deref_blob(blob_ref, root=None):
    """
    blob_ref 로 redacted bytes 조회. FROZEN name — query_dev_process_event.py import 대상.

    Returns bytes | None.
      · hot(loose) 존재 → bytes.
      · warm(.gz) 존재 → decompress + hash 재검증(hash(decompressed)==blob_ref) 후 bytes.
      · cold-evict/부재 → None (silent 404 아닌 부재 신호 — 상위 reader 가 tombstone 조회 가능).
      · 무결성 실패(sha256 불일치) → None (절대 silent-corrupt 금지 — 잘못된 bytes 반환 안 함).
    """
    if not _is_valid_ref(blob_ref):
        return None
    try:
        # hot tier
        hot = _blob_path(root, blob_ref)
        if hot.exists():
            data = hot.read_bytes()
            return data if hashlib.sha256(data).hexdigest() == blob_ref else None

        # warm tier — content-preserving hash-verified transform 역변환
        warm = _warm_path(root, blob_ref)
        if warm.exists():
            data = gzip.decompress(warm.read_bytes())
            return data if hashlib.sha256(data).hexdigest() == blob_ref else None

        # cold-evict/부재
        return None
    except Exception as exc:
        sys.stderr.write("[dev-process-blob] WARN: deref_blob failed — %s\n" % exc)
        return None


# ─────────────────────── public: warm_compress_blob (content-preserving) ────────────
def warm_compress_blob(blob_ref, root=None):
    """
    hot(loose) → warm(.gz) content-preserving hash-verified transform(ADR-155 §결정 6).

    decompress 시 byte-identical redacted 복원 + hash(decompressed)==blob_ref 재검증에
    성공한 뒤에만 loose 제거. 검증 실패 → loose 보존(transform abort, 증거 손실 0).
    index row 는 절대 rewrite 하지 않는다(불변 anchor = blob_ref, git loose→pack 동형).

    Returns bool (transform 성공 여부). non-blocking(예외 → False).
    """
    if not _is_valid_ref(blob_ref):
        return False
    try:
        hot = _blob_path(root, blob_ref)
        if not hot.exists():
            return False
        data = hot.read_bytes()
        # hot 자체 무결성 선검증(오염 blob 을 warm 으로 옮기지 않음)
        if hashlib.sha256(data).hexdigest() != blob_ref:
            return False

        packed = gzip.compress(data)
        # ★재검증: decompress → hash == blob_ref 성공해야만 warm 확정
        if hashlib.sha256(gzip.decompress(packed)).hexdigest() != blob_ref:
            return False

        warm = _warm_path(root, blob_ref)
        _atomic_write_bytes(warm, packed)

        # warm 확정 후에만 loose 제거(hash-verified transform 성공 gate)
        try:
            os.unlink(str(hot))
        except OSError:
            pass
        return True
    except Exception as exc:
        sys.stderr.write("[dev-process-blob] WARN: warm_compress_blob failed — %s\n" % exc)
        return False


# ─────────────────────── public: prune_blobs (off-hot-path GC + tombstone) ─────────
def _emit_tombstone(root, blob_ref, tier, now):
    """append-only blob-evicted 증거(index blob_ref 는 절대 null 안 함 — 별 sidecar ledger)."""
    ledger = _resolve_root(root) / _TOMBSTONE_LEDGER
    ledger.parent.mkdir(parents=True, exist_ok=True)
    row = {
        "schema": "blob-evicted-v1",
        "blob_ref": blob_ref,
        "evicted_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now)),
        "tier": tier,
        "reason": "gc-grace-prune",
    }
    line = (json.dumps(row, ensure_ascii=False) + "\n").encode("utf-8")
    fd = os.open(str(ledger), os.O_APPEND | os.O_CREAT | os.O_WRONLY, 0o600)
    try:
        os.write(fd, line)
    finally:
        os.close(fd)
    _chmod_600(ledger)


def prune_blobs(reachable_refs=None, grace_days=GC_GRACE_DAYS, now=None, root=None):
    """
    off-hot-path grace-period GC(capture hook 에서 절대 호출 금지 — record-only INV).
    tier-scoped: hot(blobs/loose) + warm(warm/*.gz) 양 tier 를 동일 규칙으로 prune.

    GC 적격 = 참조 row 전부 cold(≡ reachable_refs 미포함) ∧ blob mtime 이 grace 초과.
    evict 시 tombstone(append-only blob-evicted 증거) emit 후 blob 파일 물리 삭제.
    index blob_ref 는 절대 null 하지 않는다(append-only — 상위 reader 는 tombstone 도달).

    ★안전 gate: reachable_refs 가 None 이면 reachability 판정 불가 → 아무것도 evict 안 함
      (참조 중 blob 오삭제 차단). 명시적으로 set 을 넘길 때만 미참조 blob 이 evict 대상.

    Returns dict {"scanned", "evicted", "retained", "skipped_no_reachability"}.
    """
    now = time.time() if now is None else now
    cutoff = now - grace_days * 86400
    result = {"scanned": 0, "evicted": 0, "retained": 0, "skipped_no_reachability": False}

    # (파일경로, tier, blob_ref) — hot=파일명 그대로, warm=.gz 확장 제거
    def _iter_tiers():
        hot_root = _resolve_root(root) / _BLOBS_DIR
        warm_root = _resolve_root(root) / _WARM_DIR
        if hot_root.exists():
            for p in hot_root.rglob("*"):
                if p.is_file():
                    yield p, "hot", p.name
        if warm_root.exists():
            for p in warm_root.rglob("*.gz"):
                if p.is_file():
                    yield p, "warm", p.name[:-3]  # strip ".gz"

    try:
        if reachable_refs is None:
            # reachability 미제공 → evict 금지(scan-only, 안전)
            result["skipped_no_reachability"] = True
            for _p, _tier, _ref in _iter_tiers():
                result["scanned"] += 1
                result["retained"] += 1
            return result

        reachable = set(reachable_refs)
        for p, tier, ref in _iter_tiers():
            result["scanned"] += 1
            # 참조 중이거나 grace 이내 → 보존
            if ref in reachable or not _is_valid_ref(ref):
                result["retained"] += 1
                continue
            try:
                mtime = p.stat().st_mtime
            except OSError:
                result["retained"] += 1
                continue
            if mtime > cutoff:
                result["retained"] += 1
                continue
            # evict — tombstone 선기록(증거) → 물리 삭제
            _emit_tombstone(root, ref, tier=tier, now=now)
            try:
                os.unlink(str(p))
                result["evicted"] += 1
            except OSError:
                result["retained"] += 1
        return result
    except Exception as exc:
        sys.stderr.write("[dev-process-blob] WARN: prune_blobs failed — %s\n" % exc)
        return result
