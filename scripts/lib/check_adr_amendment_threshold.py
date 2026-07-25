#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
scripts/lib/check_adr_amendment_threshold.py
CFP-2812 / ADR-167(adr-amendment-compaction-ratchet) / ADR-060 — ADR amendment 누적 임계 재제정(compaction) ratchet lint

목적 (Change Plan §3 D1~D11):
  ADR corpus 의 append-only 누적 부채에 대해 재제정(compaction) ratchet 을 기계 판정한다.
  - --mode threshold : effective_count(max(본문 헤딩, frontmatter entry 합산)) >= N 인 ADR 을 grandfather
                       baseline 과 대조 — 도입 시점 관측 누적(grandfathered)은 GREEN, 신규 누적분은 RED.
  - --mode parity    : 신규 amendment 의 frontmatter 기재 여부(heading↔fm drift, forward-only) + 신규 entry
                       의 `reinterpretation:` marker presence/consistency 판정.
  - --write-baseline : 도입 시점 corpus 전수 스캔 → effective_count >= N 인 ADR 을 grandfathered_at 로 동결 write.

honest ceiling (ADR-082 §결정 16 / ADR-119 §결정 6 / ADR-136 정직 천장 — Change Plan D5/D10):
  기계 게이트가 보증하는 것은 (a) count 산식 판정 (b) marker presence/type consistency (c) baseline 무결성
  검사까지다. 재해석 여부의 의미 판정 / prose-only 본문 편집(양 표면 미기재) / 재제정 의미 무변경(semantic
  fidelity) 은 기계화 불가 — 리뷰 판정 축(인간)의 몫이다. "모든 재해석 기계 검출"·"stale drift 재발 근절"
  류 hard-claim 은 하지 않는다.

resource 정직 (ADR-082 §결정 16 — Change Plan D10, honest-downgrade):
  born-safe bound 4-axis: (1) path filter = archive/adr/ADR-*.md anchored + ADR-RESERVATION.md EXEMPT
  (2) bounded-quantifier regex — 헤딩 매칭 `^#{2,4}\s{0,80}Amendment` (무제한 quantifier 미사용)
  (3) per-file 물리 라인 length truncate (MAX_PHYSICAL_LINE_LEN) (4) total-work bound — 166 파일 유한 corpus 1-shot.
  본 bound 은 bounded degradation 정직 천장 — 임의 입력 무해 단정 아님(honest ceiling). "ReDoS-safe" 류
  안전성 hard-claim 은 paired proof-ref(복잡도 회귀 self-test) 동반 없이는 하지 않는다.

fail-closed 파싱 (Change Plan D9 — sunset 게이트 divergence):
  - pyyaml 부재 → `::error` + exit 1 (침묵 GREEN skip 상속 거부 — hollow gate 미유입).
  - yaml.YAMLError / frontmatter 구획 추출 실패 / 미지 구조 → violation(RED). `or {}` fallback 미상속.
  - yaml.safe_load 강제 (yaml.load / full_load 금지 — `!!python/object` 역직렬화 경로 미허용).

CLI 계약 (thin wrapper scripts/check-adr-amendment-{threshold,parity}.sh SSOT):
  bash scripts/check-adr-amendment-threshold.sh                 → 무인자 threshold (archive/adr/ADR-*.md glob)
  bash scripts/check-adr-amendment-threshold.sh <ADR paths...>  → 명시 ADR 만 threshold
  bash scripts/check-adr-amendment-threshold.sh --write-baseline → baseline 동결 write (single writer)
  bash scripts/check-adr-amendment-parity.sh                    → 무인자 parity (forward-only, merge-base delta)

Exit codes:
  0 = PASS (violation 0)
  1 = violation >=1 (임계 초과 신규분 / baseline 무결성 위반 / heading-only drift / marker 미기재·비-boolean / 파싱 실패)

ADR refs: ADR-167(adr-amendment-compaction-ratchet) §결정 1~8 / ADR-060 (게이트 tier host) / ADR-145
  (forward-only+grandfather) / ADR-153 (baseline 은퇴 선례) / ADR-082 §결정 16 (resource 정직) /
  ADR-119·ADR-136 (honest ceiling) / ADR-061 (Python SSOT + thin wrapper) / ADR-005 (byte-parity workflow 쌍).
"""

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

# Windows console (cp949) 호환 — UTF-8 강제 (check_adr_sunset_criteria.py:10-16 답습).
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# fail-closed: pyyaml 부재 = 명시 fail (sunset 게이트의 sys.exit(0) skip 상속 거부 — Change Plan D9).
try:
    import yaml
except ImportError:
    print(
        "::error::check-adr-amendment-threshold: pyyaml 미설치 — fail-closed exit 1 "
        "(침묵 GREEN skip 미상속, hollow gate 미유입). workflow 는 pip install pyyaml step 보유.",
        file=sys.stderr,
    )
    sys.exit(1)

# ─────────────────────── 상수 (SSOT) ────────────────────────────────────────────
# N 의 operational SSOT — 단일 리터럴 1곳 (다표면 복제 금지 — Change Plan D1 / §결정 2).
THRESHOLD_N = 10

DEFAULT_BASELINE_REL = "docs/adr-amendment-threshold-baseline.yaml"
ADR_GLOB = "archive/adr/ADR-*.md"
EXEMPT_NAMES = {"ADR-RESERVATION.md"}  # ADR governance 레지스트리 — real ADR 아님, 게이트 EXEMPT.

# born-safe bound (Change Plan D10): per-physical-line length truncate 축 (bounded degradation — 정직 천장).
MAX_PHYSICAL_LINE_LEN = 8192

# 본문 헤딩 Amendment 매칭 — bounded quantifier `\s{0,80}` (무제한 quantifier 미사용, D10).
HEADING_RE = re.compile(r"^#{2,4}\s{0,80}Amendment", re.MULTILINE)
# frontmatter 구획 추출 (선례 check_adr_sunset_criteria.py:70 답습).
FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
# ADR 식별키 추출 (파일명 `ADR-082-slug.md` → `ADR-082`).
ADR_ID_RE = re.compile(r"^(ADR-\d+)")
# archive/adr anchored path 매칭 (Windows backslash → forward slash 정규화 후).
ADR_PATH_RE = re.compile(r"(?:^|/)archive/adr/ADR-[^/]+\.md$")


# ══════════════════════ 순수 함수 6종 (Change Plan D2 — 파일시스템 무접촉) ══════════
# 아래 6종은 QADev self-test 가 python 레벨로 직접 fixture 주입한다 (AC-3 mutation-kill).

def count_heading_amendments(body: str) -> int:
    """본문 헤딩 `^#{2,4}\\s{0,80}Amendment` 매치 수 (bounded quantifier — D10)."""
    return len(HEADING_RE.findall(body))


def count_frontmatter_entries(fm: dict) -> int:
    """frontmatter amendment_log 배열 길이 + amendments 배열 길이 **양 키 합산** (first-key-wins 아님).

    각 키가 list 일 때만 len 가산 — 값이 list 아니면 0 취급 (Change Plan D2). 파싱 실패의 fail-closed
    판정은 orchestration 층(_extract_frontmatter) 소관이며, 본 함수는 dict 를 전제로 배열 길이만 합산한다.
    """
    total = 0
    for key in ("amendment_log", "amendments"):
        val = fm.get(key)
        if isinstance(val, list):
            total += len(val)
    return total


def effective_count(heading_n: int, fm_n: int) -> int:
    """effective = max(heading count, frontmatter entry 합산) — 단일 표면 하향으로 count 무력화 미성립."""
    return max(heading_n, fm_n)


def check_threshold(effective: int, adr_id: str, baseline: dict, threshold_n: int) -> list[str]:
    """임계 판정 4분기 (violation 문자열 list 반환, 빈 list = GREEN) — Change Plan D6.

    baseline = {adr_id: grandfathered_at} 맵.
      (0) effective < threshold_n            → GREEN (누적 미달)
      (i)   baseline 미등재                   → RED (신규 임계 초과)
      (ii)  effective > grandfathered_at      → RED (grandfathered_at 초과 신규 누적분 — 재제정 의무)
      (iii) effective == grandfathered_at     → GREEN
      (iv)  effective < grandfathered_at      → RED (baseline 동조 shrink 요구 — --write-baseline 재실행)
    """
    if effective < threshold_n:
        return []
    if adr_id not in baseline:
        return [
            f"{adr_id}: baseline 미등재 — 신규 임계 초과 "
            f"(effective_count={effective} >= N={threshold_n}, 재제정 의무 트리거)"
        ]
    grandfathered_at = baseline[adr_id]
    if effective > grandfathered_at:
        return [
            f"{adr_id}: grandfathered_at({grandfathered_at}) 초과 신규 누적분 "
            f"(effective_count={effective}) — 재제정 의무 (grandfather 면제 아님)"
        ]
    if effective == grandfathered_at:
        return []
    return [
        f"{adr_id}: baseline 동조 shrink 요구 "
        f"(effective_count={effective} < grandfathered_at={grandfathered_at}) — "
        f"bash scripts/check-adr-amendment-threshold.sh --write-baseline 재실행"
    ]


def check_parity(heading_n: int, fm_n: int) -> list[str]:
    """heading↔fm drift 판정 (discrete). heading-only amendment 신호 = heading_n > fm_n → RED.

    NOTE: forward-only(신규 delta) 판정은 orchestration 이 merge-base 대비 delta 로 적용한다. 본 순수 함수는
    주어진 (heading_n, fm_n) 쌍의 drift 만 판정 — fm_n >= heading_n 은 heading-only drift 아님 (GREEN).
    """
    if heading_n > fm_n:
        return [
            f"heading-only amendment drift — 본문 헤딩({heading_n}) > frontmatter entry({fm_n}), "
            f"신규 헤딩의 frontmatter 기재 누락 (forward-only 기재 의무)"
        ]
    return []


def check_marker_presence(entry: dict) -> list[str]:
    """신규 frontmatter amendment entry 의 `reinterpretation:` marker presence/consistency (Change Plan D5).

    미기재 → RED. 값이 YAML boolean 아님 → RED. 값 True 자체는 fail 아님 (::warning 신호는 orchestration 소관).
    """
    if "reinterpretation" not in entry:
        return ["reinterpretation marker 미기재 (신규 amendment entry 필수 필드 — AC-4)"]
    val = entry["reinterpretation"]
    if not isinstance(val, bool):
        return [f"reinterpretation 비-boolean ({val!r}) — YAML boolean 필수"]
    return []


# ══════════════════════ orchestration (top-level — 순수 함수 밖) ═══════════════════

def _adr_id_from_name(name: str):
    """파일명에서 ADR 식별키 추출 (`ADR-082-slug.md` → `ADR-082`). 미매치 → None."""
    m = ADR_ID_RE.match(name)
    return m.group(1) if m else None


def _norm(path) -> str:
    """Windows backslash → forward slash 정규화 (선례 check_adr_sunset_criteria.py:59 답습)."""
    return str(path).replace("\\", "/")


def _is_adr_candidate(path: Path) -> bool:
    """archive/adr anchored ADR-*.md 후보 여부 (RESERVATION 포함 — census candidate 집계용, exempt 前)."""
    return bool(ADR_PATH_RE.search(_norm(path))) and path.name.startswith("ADR-")


def _extract_frontmatter(text: str, rel: str):
    """(fm_dict, error_msg) 반환 — 성공 시 error_msg=None. fail-closed (Change Plan D9)."""
    m = FRONTMATTER_RE.match(text)
    if not m:
        return None, f"{rel}: frontmatter 구획 추출 실패 (--- 구획 부재)"
    try:
        fm = yaml.safe_load(m.group(1))  # safe_load 강제 — !!python/object 역직렬화 미허용.
    except yaml.YAMLError as e:
        return None, f"{rel}: frontmatter YAML 파싱 실패 ({e})"
    if fm is None:
        return {}, None  # 빈 frontmatter = 유효 (amendment 0)
    if not isinstance(fm, dict):
        return None, f"{rel}: frontmatter 구조 미지 (dict 아님: {type(fm).__name__})"
    return fm, None


def _read_text(path: Path) -> str:
    """파일 읽기 + per-physical-line length truncate (born-safe bound T-3 — bounded degradation, D10)."""
    raw = path.read_text(encoding="utf-8", errors="replace")
    if len(raw) <= MAX_PHYSICAL_LINE_LEN:
        return raw
    truncated = []
    for line in raw.splitlines(keepends=True):
        if len(line) > MAX_PHYSICAL_LINE_LEN:
            line = line[:MAX_PHYSICAL_LINE_LEN] + "\n"
        truncated.append(line)
    return "".join(truncated)


def _scan_adr(path: Path, rel: str) -> dict:
    """단일 ADR 스캔 → {adr_id, heading_n, fm_n, effective, fm, error}. error 있으면 나머지 None."""
    try:
        text = _read_text(path)
    except OSError as e:
        return {"rel": rel, "error": f"{rel}: 파일 읽기 실패 ({e})"}
    fm, err = _extract_frontmatter(text, rel)
    if err:
        return {"rel": rel, "error": err}
    m = FRONTMATTER_RE.match(text)
    body = text[m.end():] if m else text
    heading_n = count_heading_amendments(body)
    fm_n = count_frontmatter_entries(fm)
    return {
        "rel": rel,
        "adr_id": _adr_id_from_name(path.name),
        "heading_n": heading_n,
        "fm_n": fm_n,
        "effective": effective_count(heading_n, fm_n),
        "fm": fm,
        "error": None,
    }


def _resolve_paths(repo_root: str, argv_paths):
    """positional 지정 시 그 경로, 아니면 archive/adr/ADR-*.md glob (정렬)."""
    if argv_paths:
        return [Path(p) for p in argv_paths]
    return sorted(Path(repo_root).glob(ADR_GLOB))


# ─────────────────────── git merge-base helper (forward-only / B-1) ──────────────
# 전 git 연산은 실패 시 None 반환 (fail-safe — census 명시 skip, crash 0).

def _run_git(repo_root: str, args):
    try:
        r = subprocess.run(
            ["git"] + args,
            cwd=repo_root,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
        )
    except Exception:
        return None
    if r.returncode != 0:
        return None
    return r.stdout


def _merge_base(repo_root: str, base_ref):
    candidates = []
    if base_ref:
        candidates.append(base_ref)
    env_base = os.environ.get("GITHUB_BASE_REF")
    if env_base:
        candidates.append(f"origin/{env_base}")
    candidates += ["origin/main", "main"]
    for ref in candidates:
        out = _run_git(repo_root, ["merge-base", ref, "HEAD"])
        if out and out.strip():
            return out.strip()
    return None


def _git_show(repo_root: str, ref: str, rel_path: str):
    return _run_git(repo_root, ["show", f"{ref}:{rel_path}"])


def _threshold_n_at(repo_root: str, ref: str):
    """merge-base 시점 스크립트의 THRESHOLD_N 리터럴 (N 하향 재산정 예외 판정용). 미취득 → None."""
    src = _git_show(repo_root, ref, "scripts/lib/check_adr_amendment_threshold.py")
    if not src:
        return None
    m = re.search(r"^THRESHOLD_N\s*=\s*(\d+)", src, re.MULTILINE)
    return int(m.group(1)) if m else None


# ─────────────────────── baseline load / write ──────────────────────────────────

def _parse_baseline_data(data):
    """yaml.safe_load 결과 → (baseline_map, entries_list, error). fail-closed."""
    if data is None:
        return {}, [], None
    if not isinstance(data, dict):
        return {}, [], f"baseline 구조 미지 (dict 아님: {type(data).__name__})"
    entries = data.get("entries", [])
    if entries is None:
        entries = []
    if not isinstance(entries, list):
        return {}, [], "baseline entries 가 list 아님"
    bmap = {}
    for e in entries:
        if not isinstance(e, dict) or "adr" not in e or "grandfathered_at" not in e:
            return {}, [], f"baseline entry 구조 미지 ({e!r})"
        adr = str(e["adr"]).strip()
        gf = e["grandfathered_at"]
        if isinstance(gf, bool) or not isinstance(gf, int):
            return {}, [], f"baseline grandfathered_at 정수 아님 ({adr}: {gf!r})"
        bmap[adr] = gf
    return bmap, entries, None


def load_baseline_file(path: str):
    """baseline 파일 로드 → (baseline_map, entries_list, error). 부재 = 빈 맵(error None)."""
    if not os.path.isfile(path):
        return {}, [], None
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        return {}, [], f"baseline YAML 파싱 실패 ({e})"
    except OSError as e:
        return {}, [], f"baseline 읽기 실패 ({e})"
    return _parse_baseline_data(data)


def load_baseline_text(text: str):
    """baseline 문자열(merge-base git show 결과) 로드 → (baseline_map, entries_list, error)."""
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as e:
        return {}, [], f"baseline YAML 파싱 실패 ({e})"
    return _parse_baseline_data(data)


def write_baseline(path: str, corpus_scans):
    """도입 시점 corpus 전수 스캔 → effective_count >= N 인 ADR 을 grandfathered_at 로 동결 write.

    entry = {adr, grandfathered_at: effective_count}, adr 오름차순 정렬(determinism). single writer.
    """
    picked = [
        (s["adr_id"], s["effective"])
        for s in corpus_scans
        if s.get("error") is None and s.get("adr_id") and s["effective"] >= THRESHOLD_N
    ]
    picked.sort(key=lambda t: (int(re.sub(r"\D", "", t[0]) or 0), t[0]))

    header = [
        "# docs/adr-amendment-threshold-baseline.yaml — GENERATED by "
        "scripts/lib/check_adr_amendment_threshold.py --write-baseline (CFP-2812)",
        "# DO NOT EDIT BY HAND. Regenerate: bash scripts/check-adr-amendment-threshold.sh --write-baseline",
        "# grandfather = 도입 시점 corpus effective_count(max(헤딩, fm 합산)) >= THRESHOLD_N 동결 → "
        "forward-only 신규 누적분만 재제정 의무 (ADR-060 §결정 6 / ADR-145 forward-only+grandfather).",
        "# 무결성: B-1 단조 비증가(entry 값 증가·추가 금지, N 하향 재산정 예외) + B-2 ceiling sanity"
        "(grandfathered_at <= 현재 스캔값 + dangling entry 검출). 단조 shrink → 공집합 도달 시 은퇴(ADR-153).",
        "schema_version: '1.0'",
        "generated_by: CFP-2812",
        "basis: ADR-167(adr-amendment-compaction-ratchet) §결정 5 — 도입 시점 corpus effective_count "
        "(max(본문 헤딩, frontmatter entry 합산)) >= THRESHOLD_N 관측치 동결 (별도 리터럴 목록 금지 — "
        "산식↔baseline 소스 동일성 invariant, AC-2).",
        "entries:",
    ]
    lines = list(header)
    if not picked:
        # 빈 baseline (공집합) — flow-empty 로 표기.
        lines[-1] = "entries: []"
    else:
        for adr, gf in picked:
            lines.append(f"- adr: {adr}")
            lines.append(f"  grandfathered_at: {gf}")

    body = "\n".join(lines) + "\n"
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:  # LF 고정 (CRLF gotcha 회피).
        f.write(body)
    return len(picked)


def _locate_adr_file(repo_root: str, adr_id: str):
    """baseline entry 의 ADR 파일 실재 확인 (B-2 dangling 검사). archive/adr/{adr_id}-*.md glob."""
    base = Path(repo_root) / "archive" / "adr"
    matches = sorted(base.glob(f"{adr_id}-*.md"))
    if matches:
        return matches[0]
    exact = base / f"{adr_id}.md"
    return exact if exact.is_file() else None


# ─────────────────────── baseline 무결성 B-1 / B-2 ───────────────────────────────

def b2_ceiling_sanity(repo_root: str, baseline_entries) -> list:
    """B-2 (매 실행 무조건): 전 entry grandfathered_at <= 현재 스캔값 + entry ADR 파일 실재 — D6."""
    violations = []
    for e in baseline_entries:
        adr = str(e["adr"]).strip()
        gf = e["grandfathered_at"]
        adr_file = _locate_adr_file(repo_root, adr)
        if adr_file is None:
            violations.append(
                f"B-2 dangling entry: baseline {adr} 의 ADR 파일 부재 — 퇴역 시 항목 제거 필요 (AC-8)"
            )
            continue
        rel = _norm(os.path.relpath(str(adr_file), repo_root))
        scan = _scan_adr(adr_file, rel)
        if scan.get("error"):
            violations.append(f"B-2: {scan['error']}")
            continue
        if gf > scan["effective"]:
            violations.append(
                f"B-2 ceiling 위반: baseline {adr} grandfathered_at={gf} > 현재 스캔값="
                f"{scan['effective']} (손편집 인플레이트 시그니처)"
            )
    return violations


def b1_monotone_seal(repo_root: str, current_map: dict, corpus_effective: dict, base_ref):
    """B-1 (PR context): merge-base baseline 대비 단조 비증가 — (violations, skip_reason). D6."""
    mb = _merge_base(repo_root, base_ref)
    if mb is None:
        return [], "merge-base 미취득 (로컬/최초 — B-1 skip)"
    base_text = _git_show(repo_root, mb, DEFAULT_BASELINE_REL)
    if base_text is None:
        return [], "merge-base baseline 파일 부재 (신규 도입 — B-1 skip)"
    base_map, _base_entries, err = load_baseline_text(base_text)
    if err:
        return [f"B-1: merge-base baseline 파싱 실패 ({err})"], None

    n_base = _threshold_n_at(repo_root, mb)
    n_lowered = n_base is not None and n_base > THRESHOLD_N

    violations = []
    for adr, cur_gf in current_map.items():
        if adr in base_map:
            if cur_gf > base_map[adr]:
                violations.append(
                    f"B-1 단조 위반: {adr} grandfathered_at {base_map[adr]}→{cur_gf} 증가 "
                    f"(baseline 손편집 인플레이트 시그니처)"
                )
        else:
            # entry 신규 추가 — 유일 예외 = N 하향 재산정 시 grandfathered_at == 현재 스캔값.
            allowed = n_lowered and cur_gf == corpus_effective.get(adr)
            if not allowed:
                violations.append(
                    f"B-1 단조 위반: {adr} baseline entry 신규 추가 "
                    f"(N 하향 재산정 예외 미해당 — 신규 초과분 legacy 위장 시그니처)"
                )
    return violations, None


# ─────────────────────── mode: threshold ────────────────────────────────────────

def run_threshold(repo_root: str, paths, baseline_path: str, base_ref) -> int:
    violations = []
    adr_candidates = 0
    scans = []

    for p in paths:
        if _is_adr_candidate(p) and p.exists():
            adr_candidates += 1
        if p.name in EXEMPT_NAMES:
            continue
        if not p.name.startswith("ADR-"):
            continue
        if not p.exists():
            violations.append(f"{_norm(p)}: file 부재")
            continue
        rel = _norm(os.path.relpath(str(p), repo_root))
        scan = _scan_adr(p, rel)
        if scan.get("error"):
            violations.append(scan["error"])
            continue
        scans.append(scan)

    files_checked = len(scans)
    corpus_effective = {s["adr_id"]: s["effective"] for s in scans if s["adr_id"]}

    # baseline load (fail-closed).
    baseline_map, baseline_entries, berr = load_baseline_file(baseline_path)
    if berr:
        violations.append(f"baseline: {berr}")

    # 임계 판정 (per-ADR).
    for s in scans:
        if not s["adr_id"]:
            continue
        violations.extend(check_threshold(s["effective"], s["adr_id"], baseline_map, THRESHOLD_N))

    # B-2 ceiling sanity (매 실행 무조건).
    violations.extend(b2_ceiling_sanity(repo_root, baseline_entries))

    # B-1 단조 seal (PR context — merge-base 대비).
    b1_violations, b1_skip = b1_monotone_seal(repo_root, baseline_map, corpus_effective, base_ref)
    violations.extend(b1_violations)

    _print_census("threshold", adr_candidates, files_checked, extra=(f"B-1: {b1_skip}" if b1_skip else "B-1: 적용"))
    return _emit(violations, "threshold")


# ─────────────────────── mode: parity ───────────────────────────────────────────

def _fm_lists(fm: dict):
    """fm 에서 amendment_log / amendments 리스트 추출 (list 아니면 빈 리스트)."""
    log = fm.get("amendment_log")
    amd = fm.get("amendments")
    return (log if isinstance(log, list) else []), (amd if isinstance(amd, list) else [])


def run_parity(repo_root: str, paths, base_ref) -> int:
    violations = []
    warnings = []
    adr_candidates = 0
    files_checked = 0

    mb = _merge_base(repo_root, base_ref)
    mb_note = "merge-base 미취득 (forward-only delta=0 — 소급 판정 skip)" if mb is None else f"merge-base={mb[:12]}"

    for p in paths:
        if _is_adr_candidate(p) and p.exists():
            adr_candidates += 1
        if p.name in EXEMPT_NAMES:
            continue
        if not p.name.startswith("ADR-"):
            continue
        if not p.exists():
            violations.append(f"{_norm(p)}: file 부재")
            continue
        rel = _norm(os.path.relpath(str(p), repo_root))
        scan = _scan_adr(p, rel)
        if scan.get("error"):
            violations.append(scan["error"])
            continue
        files_checked += 1

        # merge-base 시점 counts (forward-only base). 미취득/신규파일 → base = current (delta 0).
        base_heading, base_fm_n = scan["heading_n"], scan["fm_n"]
        base_log_len, base_amd_len = _fm_lists(scan["fm"])
        base_log_len, base_amd_len = len(base_log_len), len(base_amd_len)
        if mb is not None:
            base_text = _git_show(repo_root, mb, rel)
            if base_text is not None:
                base_body_m = FRONTMATTER_RE.match(base_text)
                base_body = base_text[base_body_m.end():] if base_body_m else base_text
                base_heading = count_heading_amendments(base_body)
                base_fm, base_err = _extract_frontmatter(base_text, rel)
                if base_err or base_fm is None:
                    base_fm = {}
                base_log_len2, base_amd_len2 = _fm_lists(base_fm)
                base_fm_n = len(base_log_len2) + len(base_amd_len2)
                base_log_len, base_amd_len = len(base_log_len2), len(base_amd_len2)

        # (1) heading↔fm parity — forward-only delta 쌍에 순수 함수 적용.
        delta_heading = scan["heading_n"] - base_heading
        delta_fm = scan["fm_n"] - base_fm_n
        for v in check_parity(delta_heading, delta_fm):
            violations.append(f"{rel}: {v}")

        # (2) 신규 entry marker presence — append-only 후행 delta 가 신규 entry.
        cur_log, cur_amd = _fm_lists(scan["fm"])
        new_entries = cur_log[base_log_len:] + cur_amd[base_amd_len:]
        for idx, entry in enumerate(new_entries):
            if not isinstance(entry, dict):
                violations.append(f"{rel}: 신규 amendment entry 구조 미지 (dict 아님: {entry!r})")
                continue
            for v in check_marker_presence(entry):
                violations.append(f"{rel} 신규 entry[{idx}]: {v}")
            if entry.get("reinterpretation") is True:
                warnings.append(
                    f"{rel} 신규 entry[{idx}]: reinterpretation: true 관측 — "
                    f"재제정 의무 트리거 (리뷰 판정 축)"
                )

    for w in warnings:
        print(f"::warning::check-adr-amendment-parity: {w}")

    _print_census("parity", adr_candidates, files_checked, extra=mb_note)
    return _emit(violations, "parity")


# ─────────────────────── 출력 (census / verdict) ─────────────────────────────────

def _print_census(mode: str, adr_candidates: int, files_checked: int, extra: str = ""):
    """census 노출 의무 (scope=∅ vacuous-PASS 봉인 — Change Plan D11 / sunset 게이트 census 답습)."""
    tail = f" [{extra}]" if extra else ""
    print(
        f"check-adr-amendment-{mode}: census adr_candidates={adr_candidates} "
        f"files_checked={files_checked} (candidates = discovered ADR surface, anti-vacuity floor){tail}"
    )


def _emit(violations, mode: str) -> int:
    if violations:
        print(f"\n::error::check-adr-amendment-{mode}: violation {len(violations)}건:", file=sys.stderr)
        for v in violations:
            print(f"  - {v}", file=sys.stderr)
        return 1
    print(f"✓ check-adr-amendment-{mode}: violation 0건 — PASS")
    return 0


# ─────────────────────── main ────────────────────────────────────────────────────

def main(argv) -> int:
    parser = argparse.ArgumentParser(
        prog="check_adr_amendment_threshold.py",
        description="ADR amendment 누적 임계 재제정 ratchet lint (warning tier — CFP-2812 / ADR-060).",
    )
    parser.add_argument("--mode", choices=("threshold", "parity"), required=True, help="판정 모드.")
    parser.add_argument("--write-baseline", action="store_true", help="도입 시점 corpus 를 baseline 으로 동결 write.")
    parser.add_argument("--baseline", default=None, help="baseline 경로 override (기본 = docs/adr-amendment-threshold-baseline.yaml).")
    parser.add_argument("--repo-root", default=None, help="repo 루트 (기본 = cwd — thin wrapper 가 cd).")
    parser.add_argument("--base-ref", default=None, help="forward-only / B-1 merge-base ref override.")
    parser.add_argument("paths", nargs="*", help="검증할 ADR 경로 (무인자 = archive/adr/ADR-*.md glob).")
    try:
        args = parser.parse_args(argv[1:])
    except SystemExit:
        return 2

    repo_root = os.path.abspath(args.repo_root or os.getcwd())
    baseline_path = args.baseline or os.path.join(repo_root, DEFAULT_BASELINE_REL)

    # --write-baseline: 도입 시점 corpus 전수 스캔 → 동결 write (mode 무관 단일 writer).
    if args.write_baseline:
        paths = _resolve_paths(repo_root, args.paths)
        scans = []
        for p in paths:
            if p.name in EXEMPT_NAMES or not p.name.startswith("ADR-") or not p.exists():
                continue
            rel = _norm(os.path.relpath(str(p), repo_root))
            scan = _scan_adr(p, rel)
            if scan.get("error"):
                print(f"⚠ write-baseline: {scan['error']} — skip", file=sys.stderr)
                continue
            scans.append(scan)
        n = write_baseline(baseline_path, scans)
        print(
            f"check-adr-amendment-threshold: baseline written {baseline_path} — "
            f"{n} ADR grandfathered (effective_count >= N={THRESHOLD_N}) over {len(scans)} ADR scanned"
        )
        return 0

    paths = _resolve_paths(repo_root, args.paths)
    if args.mode == "threshold":
        return run_threshold(repo_root, paths, baseline_path, args.base_ref)
    return run_parity(repo_root, paths, args.base_ref)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
