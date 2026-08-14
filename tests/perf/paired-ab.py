#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""paired-ab.py — CFP-2965 Plane A paired-interleaved A/B 러너 (run-local 1회성).

CP §8.3 Plane A 프로토콜 이행 도구:
  · paired interleaved ABAB (블록 순차 금지 — 시간대 변동 교락 회피)
  · n≥30 쌍 · 쌍차 부호순위(Wilcoxon signed-rank, 정규근사) + 부호 검정
  · 훅 식별자 / 소요 / exit code 만 기록 (R-1: command 원문·인자 기록 금지)

두 개의 plugin-root 트리(A=before, B=after)를 같은 payload 로 번갈아 실행해
쌍(pair) 단위로 소요를 기록한다. 원장 오염 회피를 위해 CLAUDE_PROJECT_DIR 는
arm 별 sandbox 로 격리한다 (driver.sh 관례 답습).

사용:
  python tests/perf/paired-ab.py --a <rootA> --b <rootB> --pairs 30 \\
      --a-label before --b-label after --out <csv> [--hooks h1,h2] [--chain]
"""

from __future__ import annotations

import argparse
import json
import math
import os
import shutil
import statistics
import subprocess
import time
from pathlib import Path

BASH = shutil.which("bash") or r"C:\Program Files\Git\bin\bash.exe"

# Bash 체인 훅 7종 (골든 corpus 정의역과 동일 순서)
CHAIN_HOOKS = [
    "cross-repo-gh-safety",
    "repo-confinement",
    "git-branch-delete-merge-gate",
    "worktree-location-guard",
    "pretooluse-bash-description-inject",
    "pretooluse-dev-process-capture",
    "posttooluse-dev-process-capture",
]

# 훅별 payload (posttooluse 만 PostToolUse 형)
PAYLOAD_FOR = {"posttooluse-dev-process-capture": "payload-post.json"}
DEFAULT_PAYLOAD = "payload-sub.json"

BYPASS_ENVS = [
    "BYPASS_CROSS_REPO_GH_SAFETY", "BYPASS_REPO_CONFINEMENT",
    "BYPASS_BRANCH_DELETE_MERGE_GATE", "BYPASS_WORKTREE_LOCATION_GUARD",
    "BYPASS_CODEFORGE_BASH_DESCRIPTION_INJECT",
]


def _env_for(root: Path, sandbox: Path) -> dict:
    env = dict(os.environ)
    for k in BYPASS_ENVS:
        env.pop(k, None)
    env["CLAUDE_PLUGIN_ROOT"] = str(root)
    env["CLAUDE_PROJECT_DIR"] = str(sandbox)
    return env


def _run_once(root: Path, sandbox: Path, hook: str, payload: bytes) -> tuple[float, int]:
    """훅 1회 실행 → (elapsed_ms, exit_code). stdout/stderr 는 버리고 기록하지 않는다 (R-1)."""
    t0 = time.perf_counter()
    proc = subprocess.run(
        [BASH, str(root / "hooks" / hook)],
        input=payload, capture_output=True, env=_env_for(root, sandbox),
    )
    return (time.perf_counter() - t0) * 1000.0, proc.returncode


def _run_chain(root: Path, sandbox: Path, payloads: dict) -> float:
    """체인 7종 순차 총 wall(ms) — 1회."""
    t0 = time.perf_counter()
    for hook in CHAIN_HOOKS:
        subprocess.run(
            [BASH, str(root / "hooks" / hook)],
            input=payloads[hook], capture_output=True, env=_env_for(root, sandbox),
        )
    return (time.perf_counter() - t0) * 1000.0


# ── 통계 (외부 의존 0 — stdlib) ────────────────────────────────────────────

def _pctl(xs: list[float], q: float) -> float:
    """nearest-rank 백분위 (q=0.9 → p90)."""
    if not xs:
        return float("nan")
    s = sorted(xs)
    k = max(1, math.ceil(q * len(s)))
    return s[k - 1]


def _sign_test_p(diffs: list[float]) -> tuple[int, int, float]:
    """부호 검정 — (음수 개수, 양수 개수, 양측 p). 0 차는 제외."""
    neg = sum(1 for d in diffs if d < 0)
    pos = sum(1 for d in diffs if d > 0)
    n = neg + pos
    if n == 0:
        return neg, pos, 1.0
    k = min(neg, pos)
    tail = sum(math.comb(n, i) for i in range(0, k + 1)) / (2 ** n)
    return neg, pos, min(1.0, 2 * tail)


def _wilcoxon_signed_rank_z(diffs: list[float]) -> tuple[float, float]:
    """Wilcoxon 부호순위 정규근사 — (z, 양측 p). 동점 평균순위·연속성 보정 적용."""
    nz = [d for d in diffs if d != 0]
    n = len(nz)
    if n < 5:
        return float("nan"), float("nan")
    order = sorted(range(n), key=lambda i: abs(nz[i]))
    ranks = [0.0] * n
    i = 0
    tie_groups: list[int] = []
    while i < n:
        j = i
        while j + 1 < n and abs(nz[order[j + 1]]) == abs(nz[order[i]]):
            j += 1
        avg = (i + j + 2) / 2.0          # 1-based 평균 순위
        for k in range(i, j + 1):
            ranks[order[k]] = avg
        tie_groups.append(j - i + 1)
        i = j + 1
    w_pos = sum(r for r, d in zip(ranks, nz) if d > 0)
    w_neg = sum(r for r, d in zip(ranks, nz) if d < 0)
    w = min(w_pos, w_neg)
    mu = n * (n + 1) / 4.0
    tie_corr = sum(t ** 3 - t for t in tie_groups) / 48.0
    sigma = math.sqrt(n * (n + 1) * (2 * n + 1) / 24.0 - tie_corr)
    if sigma == 0:
        return float("nan"), float("nan")
    z = (w - mu + 0.5) / sigma
    p = math.erfc(abs(z) / math.sqrt(2))
    return z, p


def summarize(label: str, a_ms: list[float], b_ms: list[float]) -> dict:
    diffs = [b - a for a, b in zip(a_ms, b_ms)]
    neg, pos, p_sign = _sign_test_p(diffs)
    z, p_w = _wilcoxon_signed_rank_z(diffs)
    return {
        "target": label,
        "pairs": len(diffs),
        "a_median": round(statistics.median(a_ms), 1),
        "b_median": round(statistics.median(b_ms), 1),
        "a_p90": round(_pctl(a_ms, 0.9), 1),
        "b_p90": round(_pctl(b_ms, 0.9), 1),
        "diff_median": round(statistics.median(diffs), 1),
        "diff_p90": round(_pctl(diffs, 0.9), 1),
        "p90_delta": round(_pctl(b_ms, 0.9) - _pctl(a_ms, 0.9), 1),
        "neg": neg, "pos": pos,
        "p_sign": round(p_sign, 6),
        "wilcoxon_z": None if math.isnan(z) else round(z, 3),
        "p_wilcoxon": None if math.isnan(p_w) else round(p_w, 6),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--a", required=True, help="arm A plugin root (before)")
    ap.add_argument("--b", required=True, help="arm B plugin root (after)")
    ap.add_argument("--a-label", default="A")
    ap.add_argument("--b-label", default="B")
    ap.add_argument("--a-sandbox", required=True)
    ap.add_argument("--b-sandbox", required=True)
    ap.add_argument("--pairs", type=int, default=30)
    ap.add_argument("--hooks", default=",".join(CHAIN_HOOKS))
    ap.add_argument("--chain", action="store_true", help="체인 7종 순차 wall 도 측정")
    ap.add_argument("--payload-dir", required=True)
    ap.add_argument("--out", required=True, help="raw csv 경로")
    args = ap.parse_args()

    a_root, b_root = Path(args.a), Path(args.b)
    a_sb, b_sb = Path(args.a_sandbox), Path(args.b_sandbox)
    pdir = Path(args.payload_dir)
    hooks = [h for h in args.hooks.split(",") if h]

    payloads = {h: (pdir / PAYLOAD_FOR.get(h, DEFAULT_PAYLOAD)).read_bytes() for h in CHAIN_HOOKS}

    # warmup (측정 제외) — 첫 실행 디스크 캐시 비대칭 제거
    for h in hooks:
        for _ in range(2):
            _run_once(a_root, a_sb, h, payloads[h])
            _run_once(b_root, b_sb, h, payloads[h])

    raw = open(args.out, "w", encoding="utf-8", newline="\n")
    raw.write("target,pair,arm,elapsed_ms,exit_code\n")

    results = []
    for h in hooks:
        a_ms, b_ms = [], []
        for i in range(1, args.pairs + 1):
            # ABAB interleaved — 쌍 안에서 인접 실행 (시간대 변동 공통화)
            ta, rca = _run_once(a_root, a_sb, h, payloads[h])
            tb, rcb = _run_once(b_root, b_sb, h, payloads[h])
            a_ms.append(ta); b_ms.append(tb)
            raw.write(f"{h},{i},{args.a_label},{ta:.2f},{rca}\n")
            raw.write(f"{h},{i},{args.b_label},{tb:.2f},{rcb}\n")
        results.append(summarize(h, a_ms, b_ms))

    if args.chain:
        a_ms, b_ms = [], []
        for i in range(1, args.pairs + 1):
            ta = _run_chain(a_root, a_sb, payloads)
            tb = _run_chain(b_root, b_sb, payloads)
            a_ms.append(ta); b_ms.append(tb)
            raw.write(f"CHAIN-seq7,{i},{args.a_label},{ta:.2f},0\n")
            raw.write(f"CHAIN-seq7,{i},{args.b_label},{tb:.2f},0\n")
        results.append(summarize("CHAIN-seq7", a_ms, b_ms))

    raw.close()
    print(json.dumps({"a_label": args.a_label, "b_label": args.b_label,
                      "results": results}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
