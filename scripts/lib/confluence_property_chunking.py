#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# CFP-2829 S2 (leg A) — content property 무손실 multi-key chunking (AC-1 / AC-11).
#   RC-1 재조립 oracle(wrapper/spikes/cfp-2807-s0/rc1_reassembly_oracle.py) production 승격.
#   interface-freeze: confluence-sync-3anchor.py 0줄 변경 — _normalize_markdown 은 importlib 동적 로드 재사용.
"""content property 무손실 multi-key chunking + manifest 재조립.

계약 (Change Plan §3.4 / §4 chunking DTO / AC-11):
  Confluence content property = "no more than 32KB of JSON-encoded data" per key
  (source: developer.atlassian.com confluence-entity-properties + community 14124 —
   JSON-encoded 단위, raw 아님. char/byte 여부 공식 미확정 → CONSERVATIVE 28KB 마진).
  Atlassian-native chunk ordering/hash 표준 부재 → self-impose manifest(§6.1 gap 'chunking 표준').

저장 구조 (dict — property key → value):
  {
    "__manifest": {                       # MANIFEST_KEY — 무결성 검증 anchor
        "chunk_count":     N,             # 전체 chunk 개수
        "total_sha256":    "<hex>",       # raw(pre-base64) canonical 전체 sha256
        "per_chunk_sha256": ["<hex>", ...] # 각 raw chunk sha256 (ordered)
    },
    "__chunk_0": "<base64 str>",          # ordered, 0-based
    "__chunk_1": "<base64 str>",
    ...
  }

base64 인코딩 결정 (스파이크 byte-contract ↔ JSON 저장 정합):
  스파이크는 raw byte-split(data[i:i+budget]) 를 byte-concat-then-decode 로 재조립한다
  (chunk 경계가 UTF-8 multi-byte 를 가를 수 있음 — 스파이크 PART2 계약). 그러나 raw byte
  chunk 는 JSON string value 로 직접 저장 불가(불완전 UTF-8). 따라서 각 chunk value 는
  **base64 인코딩**(JSON-safe ASCII)한다. sha256 은 **raw(pre-base64) bytes** 위에서 계산 —
  스파이크의 byte-concat 무결성 계약을 그대로 보존한다.

budget 준수 (pre-flight, §7.R2 AC-2/AC-3):
  budget = base64 인코딩 후 **JSON-encoded byte**(len(json.dumps(v, ensure_ascii=False).encode()))
  기준. base64 는 4/3 팽창 + JSON quote 2 byte 를 더하므로 raw chunk 크기를 그만큼 축소한다.
  measurement-basis 미확정 동안 CONSERVATIVE_BUDGET(28KB) 보수 — 실측 후 상향(AC-11 declared).

manifest-last 저장 계약 (§7.R2 IO-6, EC-3):
  실 저장(leg B) 순서 = 전 __chunk_{n} write **후** 마지막에 __manifest(commit marker).
  reader(reassemble)는 manifest 부재 / total_sha256 불일치 → **fail-closed**(부분 데이터 노출 0).
  본 모듈은 순수 chunk/reassemble 로직만 — 저장 순서 집행은 leg B(confluence_property_rest) 소관.

anchor-A 보존 (O2):
  reassemble(chunk(x)) 는 x 와 raw-byte identical → _normalize_markdown 후 sha256(anchor A) 동일.
"""
import base64
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

# Windows cp949 stdout 차단 (confluence_forward_sync.py L60-64 패턴 — Windows CI false-oracle 방지).
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# ── 상수 ──────────────────────────────────────────────────────────────────
CONSERVATIVE_BUDGET = 28672   # 28KB JSON-encoded byte 보수 (measurement-basis 미확정 마진).
MANIFEST_KEY = "__manifest"
_CHUNK_KEY_PREFIX = "__chunk_"


def chunk_key(n: int) -> str:
    """chunk index → property key (0-based, ordered)."""
    return f"{_CHUNK_KEY_PREFIX}{n}"


# ── _normalize_markdown 재사용 (interface-freeze: 3anchor.py 0줄, importlib 동적 로드 — R-2) ──
def _load_normalize_markdown():
    """confluence-sync-3anchor.py(하이픈 파일)에서 _normalize_markdown 동적 로드.

    하이픈 파일명은 일반 import 문법 불가 → importlib.util.spec_from_file_location.
    3anchor.py 는 module-level 에서 creds(ATLASSIAN_*) 를 읽지 않으므로 로드는 creds-free (R-1 정합).
    """
    anchor_path = Path(__file__).resolve().parent.parent / "confluence-sync-3anchor.py"
    spec = importlib.util.spec_from_file_location("_cfp2829_threeanchor_chunking", anchor_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod._normalize_markdown


_normalize_markdown = _load_normalize_markdown()


class ChunkIntegrityError(ValueError):
    """재조립 무결성 위반 (manifest 부재 / hash 불일치 / chunk 누락) — fail-closed 신호."""


# ── 무결성/anchor helper ────────────────────────────────────────────────────
def _sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def anchor_a(content: bytes) -> str:
    """anchor A = sha256(정규화 markdown) hex (3anchor.py _sha256_of_file 동형, O2 검증용)."""
    return _sha256_hex(_normalize_markdown(content))


def json_encoded_size(value) -> int:
    """value 를 JSON-encoded(ensure_ascii=False, UTF-8) 했을 때의 byte 길이.

    pre-flight budget 측정 helper (§7.R2 AC-2 — PUT 전 크기 검사). property 저장은
    JSON-encoded byte 기준이므로 raw byte 길이가 아닌 이 값이 32KB 천장 대상.
    """
    return len(json.dumps(value, ensure_ascii=False).encode("utf-8"))


def _raw_budget_for(budget: int) -> int:
    """base64 인코딩 + JSON quote(2B) 후 json_encoded_size <= budget 을 만족하는 최대 raw chunk byte.

    base64(R bytes) = 4*ceil(R/3) chars(=bytes, ASCII) + JSON quote 2. 3의 배수로 맞춰
    ceil 팽창을 제거하고 2B 마진을 남긴다. budget 이 너무 작으면 ValueError.
    """
    if budget <= 0:
        raise ValueError("budget must be positive")
    raw = ((budget - 2) // 4) * 3
    if raw < 1:
        raise ValueError(f"budget={budget} too small for base64 chunking (raw_budget={raw})")
    return raw


# ── chunk / reassemble ──────────────────────────────────────────────────────
def chunk(canonical: bytes, budget: int = CONSERVATIVE_BUDGET) -> dict:
    """canonical bytes → {"__manifest": {...}, "__chunk_0": <b64>, ...} 저장 dict.

    - raw byte split(스파이크 data[i:i+raw_budget]) → 각 chunk base64 인코딩.
    - sha256(total/per-chunk) = raw(pre-base64) bytes 위.
    - 빈 입력 = 단일 빈 chunk(chunk_count=1, __chunk_0="").
    - budget 준수: 각 chunk 의 json_encoded_size <= budget (defensive assert).
    """
    if not isinstance(canonical, (bytes, bytearray)):
        raise TypeError("canonical must be bytes")
    canonical = bytes(canonical)
    raw_budget = _raw_budget_for(budget)

    if len(canonical) == 0:
        raw_chunks = [b""]
    else:
        raw_chunks = [canonical[i:i + raw_budget] for i in range(0, len(canonical), raw_budget)]

    properties: dict = {}
    per_chunk_sha256 = []
    for n, raw in enumerate(raw_chunks):
        b64 = base64.b64encode(raw).decode("ascii")
        # defensive: base64+JSON 인코딩 후 budget 준수 확인 (raw_budget 산출 정확성 self-guard).
        enc = json_encoded_size(b64)
        if enc > budget:
            raise ChunkIntegrityError(
                f"chunk {n} json_encoded_size={enc} > budget={budget} (raw_budget 산출 오류)"
            )
        properties[chunk_key(n)] = b64
        per_chunk_sha256.append(_sha256_hex(raw))

    properties[MANIFEST_KEY] = {
        "chunk_count": len(raw_chunks),
        "total_sha256": _sha256_hex(canonical),
        "per_chunk_sha256": per_chunk_sha256,
    }
    return properties


def reassemble(properties: dict) -> bytes:
    """저장 dict → raw canonical bytes 복원 (전 검증 통과 시에만, 불일치=fail-closed).

    검증(EC-3 / IO-6 — 부분 데이터 노출 0):
      1) __manifest 존재 + 필수 필드.
      2) chunk_count == len(per_chunk_sha256).
      3) 각 __chunk_{n} 존재 + base64 decode 후 sha256 == per_chunk_sha256[n].
      4) ordered byte-concat.
      5) sha256(concat) == total_sha256.
    어느 단계라도 실패 시 ChunkIntegrityError raise (부분 결과 반환 절대 금지).
    """
    if not isinstance(properties, dict):
        raise ChunkIntegrityError("properties must be a dict")

    manifest = properties.get(MANIFEST_KEY)
    if manifest is None:
        raise ChunkIntegrityError("manifest 부재 (__manifest) — fail-closed")
    if not isinstance(manifest, dict):
        raise ChunkIntegrityError("manifest 형식 오류 (dict 아님)")

    try:
        chunk_count = manifest["chunk_count"]
        total_sha256 = manifest["total_sha256"]
        per_chunk_sha256 = manifest["per_chunk_sha256"]
    except KeyError as e:
        raise ChunkIntegrityError(f"manifest 필수 필드 누락 — {e}")

    if not isinstance(chunk_count, int) or chunk_count < 0:
        raise ChunkIntegrityError(f"chunk_count 형식 오류 — {chunk_count!r}")
    if not isinstance(per_chunk_sha256, list) or len(per_chunk_sha256) != chunk_count:
        raise ChunkIntegrityError(
            f"per_chunk_sha256 길이({len(per_chunk_sha256) if isinstance(per_chunk_sha256, list) else 'N/A'}) "
            f"!= chunk_count({chunk_count})"
        )

    parts = []
    for n in range(chunk_count):
        key = chunk_key(n)
        if key not in properties:
            raise ChunkIntegrityError(f"chunk 누락 — {key}")
        try:
            raw = base64.b64decode(properties[key], validate=True)
        except (ValueError, TypeError) as e:
            raise ChunkIntegrityError(f"{key} base64 decode 실패 — {e}")
        if _sha256_hex(raw) != per_chunk_sha256[n]:
            raise ChunkIntegrityError(f"{key} per-chunk sha256 불일치 — fail-closed")
        parts.append(raw)

    canonical = b"".join(parts)
    if _sha256_hex(canonical) != total_sha256:
        raise ChunkIntegrityError("total_sha256 불일치 — 재조립 무결성 실패, fail-closed")
    return canonical


# ── CLI (self round-trip demo — cp949 guard 검증용) ─────────────────────────
def main(argv=None) -> int:
    import argparse
    p = argparse.ArgumentParser(
        prog="confluence_property_chunking.py",
        description="content property 무손실 multi-key chunking round-trip demo (CFP-2829 S2 AC-11).",
    )
    p.add_argument("--budget", type=int, default=CONSERVATIVE_BUDGET, help="chunk budget (JSON-encoded byte).")
    p.add_argument("--file", default=None, help="round-trip 대상 파일 (미지정 시 내장 샘플).")
    args = p.parse_args(argv)

    if args.file:
        data = Path(args.file).read_bytes()
    else:
        data = ("한국어 정본 블롭 무결성 검증 sample.\n" * 2000).encode("utf-8")

    props = chunk(data, args.budget)
    n = props[MANIFEST_KEY]["chunk_count"]
    restored = reassemble(props)
    ok = restored == data and anchor_a(restored) == anchor_a(data)
    print(json.dumps({
        "input_bytes": len(data),
        "budget": args.budget,
        "chunk_count": n,
        "roundtrip_identity": restored == data,
        "anchor_a_preserved": anchor_a(restored) == anchor_a(data),
        "verdict": "PASS" if ok else "FAIL",
    }, ensure_ascii=False))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
