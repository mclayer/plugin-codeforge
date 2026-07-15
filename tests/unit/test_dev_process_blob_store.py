"""test_dev_process_blob_store.py — content-addressed evidence-blob-store suite.

CFP-2687 Phase 2. Change Plan §7.1 (INV-8a/8b) + §11.2 (AC-10∧AC-25 화해) + Story AC-8/9/25.
Under test: scripts/lib/dev_process_blob_store.py

불변식:
  · INV-8a (T-DPE-2): blob_ref == sha256(REDACTED bytes) AND blob_ref != sha256(raw)
    (hash-over-redacted — hash-over-raw 면 confirmation oracle). CORE.
  · intra-store dedup (T-DPE-7): 동일 content → 동일 blob_ref, 단일 파일.
  · tombstone: cold-evict 시 deref → None (silent-corrupt 금지), tombstone 증거 append-only.
  · hash-verified transform: warm 압축 → decompress hash == blob_ref, 손상 시 deref None.
  · graceful degrade: None/too-small → (None, audit), no raise.
"""

from __future__ import annotations

import gzip
import hashlib
import json

import pytest

import dev_process_blob_store as bs
import redact_dev_process_content as rd


SECRET = "ABCDEFGHIJKLMNOP1234"
RAW_WITH_SECRET = "prompt body token=" + SECRET + " and more text to store as evidence"


# ══════════════════════════════════════════════════════════════════════════════
# § INV-8a — hash-over-redacted (T-DPE-2 confirmation-oracle 봉인) — CORE
# ══════════════════════════════════════════════════════════════════════════════
class TestInv8aHashOverRedacted:
    def test_blob_ref_is_sha256_of_redacted_not_raw(self, tmp_path):
        blob_ref, audit = bs.capture_blob(RAW_WITH_SECRET, root=str(tmp_path))
        assert blob_ref is not None

        redacted, _ = rd.redact(RAW_WITH_SECRET)
        expect_redacted = hashlib.sha256(redacted.encode("utf-8")).hexdigest()
        forbidden_raw = hashlib.sha256(RAW_WITH_SECRET.encode("utf-8")).hexdigest()

        assert blob_ref == expect_redacted, "blob_ref 가 sha256(REDACTED) 아님 (INV-8a 위반)"
        assert blob_ref != forbidden_raw, "blob_ref == sha256(raw) — confirmation oracle (T-DPE-2)"
        assert audit["redaction_applied"] is True

    def test_blob_on_disk_contains_no_secret(self, tmp_path):
        blob_ref, _ = bs.capture_blob(RAW_WITH_SECRET, root=str(tmp_path))
        data = bs.deref_blob(blob_ref, root=str(tmp_path))
        assert data is not None
        assert SECRET.encode() not in data, "redacted blob 에 원문 secret 잔존"
        # deref bytes 의 hash == blob_ref (content-addressed 무결성)
        assert hashlib.sha256(data).hexdigest() == blob_ref

    def test_negative_control_raw_hash_differs_from_redacted_hash(self):
        """[negative control] secret 있는 입력에서 sha256(raw) != sha256(redacted).

        이 부등식이 성립해야 INV-8a assertion 이 discriminating (hash-over-raw 를 잡음)."""
        redacted, _ = rd.redact(RAW_WITH_SECRET)
        assert redacted != RAW_WITH_SECRET  # redaction 이 실제로 무언가 바꿈
        assert (hashlib.sha256(RAW_WITH_SECRET.encode()).hexdigest()
                != hashlib.sha256(redacted.encode()).hexdigest())


# ══════════════════════════════════════════════════════════════════════════════
# § intra-store dedup (T-DPE-7)
# ══════════════════════════════════════════════════════════════════════════════
class TestIntraStoreDedup:
    def test_same_content_same_ref_single_file(self, tmp_path):
        r1, _ = bs.capture_blob("identical evidence payload", root=str(tmp_path))
        r2, _ = bs.capture_blob("identical evidence payload", root=str(tmp_path))
        assert r1 == r2
        # root=tmp_path → 저장소 루트가 곧 tmp_path (dev-process 서브디렉터리는 DEFAULT root 전용)
        blob_files = [p for p in (tmp_path / "blobs").rglob("*") if p.is_file()]
        assert len(blob_files) == 1, f"dedup 실패 — {len(blob_files)} 파일 (1 기대)"

    def test_distinct_content_distinct_ref(self, tmp_path):
        r1, _ = bs.capture_blob("evidence payload ONE", root=str(tmp_path))
        r2, _ = bs.capture_blob("evidence payload TWO", root=str(tmp_path))
        assert r1 != r2


# ══════════════════════════════════════════════════════════════════════════════
# § tombstone — cold-evict 시 deref None (silent-corrupt 금지) + 증거 append-only
# ══════════════════════════════════════════════════════════════════════════════
class TestTombstone:
    def test_evict_records_tombstone_and_deref_none(self, tmp_path):
        import time
        blob_ref, _ = bs.capture_blob("evict me eventually", root=str(tmp_path))
        assert bs.deref_blob(blob_ref, root=str(tmp_path)) is not None
        # 미참조(reachable=set()) + now 를 미래로 강제 → grace 초과 확정 (timing flake 제거)
        result = bs.prune_blobs(reachable_refs=set(), grace_days=0,
                                now=time.time() + 3600, root=str(tmp_path))
        assert result["evicted"] == 1, f"evict 안 됨: {result}"
        # deref → None (잘못된 bytes 반환 아님 — silent-corrupt 금지)
        assert bs.deref_blob(blob_ref, root=str(tmp_path)) is None
        # tombstone 증거 append-only (root=tmp_path 저장소 루트 직하)
        tomb = tmp_path / "blob-evicted.jsonl"
        assert tomb.exists()
        rows = [json.loads(ln) for ln in tomb.read_text(encoding="utf-8").splitlines() if ln.strip()]
        assert any(r["blob_ref"] == blob_ref and r["schema"] == "blob-evicted-v1" for r in rows)

    def test_prune_none_reachability_evicts_nothing(self, tmp_path):
        """안전 gate — reachable_refs=None 이면 evict 0 (참조 blob 오삭제 차단)."""
        blob_ref, _ = bs.capture_blob("do not evict", root=str(tmp_path))
        result = bs.prune_blobs(reachable_refs=None, grace_days=0, root=str(tmp_path))
        assert result["skipped_no_reachability"] is True
        assert result["evicted"] == 0
        assert bs.deref_blob(blob_ref, root=str(tmp_path)) is not None

    def test_reachable_blob_not_evicted(self, tmp_path):
        blob_ref, _ = bs.capture_blob("still referenced", root=str(tmp_path))
        result = bs.prune_blobs(reachable_refs={blob_ref}, grace_days=0, root=str(tmp_path))
        assert result["evicted"] == 0
        assert bs.deref_blob(blob_ref, root=str(tmp_path)) is not None


# ══════════════════════════════════════════════════════════════════════════════
# § hash-verified transform (AC-10∧AC-25 화해 — warm 압축 content-preserving)
# ══════════════════════════════════════════════════════════════════════════════
class TestHashVerifiedTransform:
    def test_warm_compress_preserves_content_and_hash(self, tmp_path):
        blob_ref, _ = bs.capture_blob("warm tier evidence payload", root=str(tmp_path))
        before = bs.deref_blob(blob_ref, root=str(tmp_path))
        assert bs.warm_compress_blob(blob_ref, root=str(tmp_path)) is True
        # hot loose 제거됨 (root=tmp_path 저장소 루트 직하)
        hot = tmp_path / "blobs" / blob_ref[:2] / blob_ref
        assert not hot.exists()
        # warm .gz 존재
        warm = tmp_path / "warm" / blob_ref[:2] / (blob_ref + ".gz")
        assert warm.exists()
        # deref 는 여전히 동일 bytes + hash == blob_ref
        after = bs.deref_blob(blob_ref, root=str(tmp_path))
        assert after == before
        assert hashlib.sha256(after).hexdigest() == blob_ref

    def test_tampered_warm_blob_deref_returns_none(self, tmp_path):
        """warm .gz 가 변조되면 hash 재검증 실패 → deref None (잘못된 bytes 반환 금지)."""
        blob_ref, _ = bs.capture_blob("integrity guarded payload", root=str(tmp_path))
        assert bs.warm_compress_blob(blob_ref, root=str(tmp_path)) is True
        warm = tmp_path / "warm" / blob_ref[:2] / (blob_ref + ".gz")
        # 다른 내용으로 변조된 .gz 로 덮어씀
        warm.write_bytes(gzip.compress(b"TAMPERED DIFFERENT CONTENT"))
        assert bs.deref_blob(blob_ref, root=str(tmp_path)) is None


# ══════════════════════════════════════════════════════════════════════════════
# § graceful degrade
# ══════════════════════════════════════════════════════════════════════════════
class TestGracefulDegrade:
    def test_none_input_returns_none_no_raise(self, tmp_path):
        ref, audit = bs.capture_blob(None, root=str(tmp_path))
        assert ref is None
        assert audit["redaction_applied"] is False

    def test_empty_input_no_blob(self, tmp_path):
        ref, _ = bs.capture_blob("", root=str(tmp_path))
        assert ref is None

    def test_deref_invalid_ref_none(self, tmp_path):
        assert bs.deref_blob("not-a-valid-ref", root=str(tmp_path)) is None
        assert bs.deref_blob("z" * 64, root=str(tmp_path)) is None  # 부재 ref
