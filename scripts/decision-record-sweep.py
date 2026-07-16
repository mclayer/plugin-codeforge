#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
scripts/decision-record-sweep.py
CFP-2698 / Epic #2696 (canary artifact D6, Story A TOOL ROBUSTENING) — decision-record
일괄 정정/효력박탈/삭제 스윕 CLI 오케스트레이터.

목적:
  oracle(`decision_record_disposition`) 의 census + `dated_block_mapper` 의 per-block dated
  provider + `reference_integrity_guard` 의 4-check guard 를 엮어, `sweep_executor` 의
  plan/apply 를 실행하는 얇은 CLI. 본 파일 자체는 로직을 갖지 않는다(logic-free wrapper) —
  전 로직은 `scripts/lib/{decision_record_disposition,dated_block_mapper,
  reference_integrity_guard,sweep_executor}.py` 에 있다.

모드(`--mode`):
  plan  — 조치 계획(JSON) 출력. 편집 없음.
  guard — plan 을 계산하되 guard 검증 결과 중심 view(action∈{correct,strip,delete} 만,
          file/line/action/guard_pass/rationale)로 출력. 편집 없음.
  apply — plan 계산 후 실제 파일 편집(batch-by-file, per-batch guard 재검증) 수행.
          `--live-contexts` 필수(live_count 산출 — correct 치환값의 근거).

corpus 지정: positional `files`(구체 파일 목록) 와 `--census-from`(디렉터리, 재귀 walk 하여
  `.md` 수집) 는 병용 가능 — 합쳐서 census 대상이 된다. exclusion(`--exclude-file`/
  `--exclude-line`) 은 census 결과(manifest) 에서 caller 가 지정한 파일/라인을 제거한다
  (엔진에 신원 하드코딩 0 — 배제는 CLI 층의 데이터일 뿐).

resource-safety honest-ceiling (ADR-082 §결정 16):
  본 CLI 의 디렉터리 walk·파일 census 는 corpus 크기에 선형(bounded)이나, 임의 입력 무해를
  단정하지 않는다 — bounded degradation 만 주장한다.
"""

import argparse
import json
import os
import sys

_LIB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib")
if _LIB_DIR not in sys.path:
    sys.path.insert(0, _LIB_DIR)

import decision_record_disposition as _oracle  # noqa: E402
import dated_block_mapper  # noqa: E402
import sweep_executor  # noqa: E402


def _collect_corpus_files(census_from, positional_files):
    """positional files(구체 파일) + census_from(디렉터리, 재귀 walk `.md` 수집) 합집합,
    순서 보존 de-dup(경로 구분자 정규화 후 비교)."""
    files = []
    if positional_files:
        files.extend(positional_files)
    if census_from:
        for base in census_from:
            if os.path.isdir(base):
                for root, _dirs, names in os.walk(base):
                    for name in names:
                        if name.lower().endswith(".md"):
                            files.append(os.path.join(root, name))
            elif os.path.isfile(base):
                files.append(base)
    seen = set()
    out = []
    for f in files:
        norm = f.replace("\\", "/")
        if norm not in seen:
            seen.add(norm)
            out.append(f)
    return out


def _apply_exclusions(manifest, exclude_files, exclude_lines):
    """caller 지정 `--exclude-file`/`--exclude-line` 으로 manifest 필터
    (엔진 자체는 fixture 신원 하드코딩 0 유지 — 배제는 CLI 층 데이터)."""
    ef = set((p or "").replace("\\", "/") for p in (exclude_files or []))
    el = set(exclude_lines or [])
    out = []
    for item in manifest:
        norm_file = item["file"].replace("\\", "/")
        key = "%s:%s" % (norm_file, item["line"])
        if norm_file in ef or key in el:
            continue
        out.append(item)
    return out


def _build_manifest(files, live_required_contexts, dated_provider):
    """corpus 파일들을 oracle census 로 스캔 → needs_disposition 항목을 {file,line} manifest 로
    축약(census 자체가 산출하는 disposition/reason/text 는 sweep_executor.plan() 이 재계산)."""
    report = _oracle._census_over_files(
        files,
        live_required_contexts=live_required_contexts,
        dated_provider=dated_provider,
    )
    manifest = []
    for entry in report.get("needs_disposition", []):
        if "line" in entry:
            manifest.append({"file": entry["file"], "line": entry["line"]})
    return manifest


def _main(argv=None):
    ap = argparse.ArgumentParser(
        description="decision-record 일괄 정정/효력박탈/삭제 스윕 CLI (plan/guard/apply)."
    )
    ap.add_argument("--mode", choices=["plan", "guard", "apply"], default="plan")
    ap.add_argument(
        "--live-contexts",
        help="현행 required-context 집합 — comma-separated 목록 또는 파일 경로"
        "(줄당 1개 또는 JSON 리스트)",
    )
    ap.add_argument(
        "--census-from",
        nargs="+",
        default=None,
        help="census 대상 디렉터리(재귀 walk, `.md` 수집) — positional files 와 병용 가능",
    )
    ap.add_argument(
        "--exclude-file",
        action="append",
        default=None,
        help="manifest 에서 제외할 파일(repo-relative) — 반복 가능",
    )
    ap.add_argument(
        "--exclude-line",
        action="append",
        default=None,
        help="manifest 에서 제외할 file:line — 반복 가능",
    )
    ap.add_argument("--repo-root", default=".", help="스캔/편집 루트(기본 CWD)")
    ap.add_argument("files", nargs="*", help="census 대상 구체 파일 목록(선택)")
    args = ap.parse_args(argv)

    repo_root = args.repo_root
    live_required_contexts = _oracle._parse_live_contexts_arg(args.live_contexts)
    dated_provider = dated_block_mapper.make_dated_provider(repo_root)

    corpus_files = _collect_corpus_files(args.census_from, args.files)
    manifest = _build_manifest(corpus_files, live_required_contexts, dated_provider)
    manifest = _apply_exclusions(manifest, args.exclude_file, args.exclude_line)

    plan_records = sweep_executor.plan(
        manifest,
        repo_root=repo_root,
        live_required_contexts=live_required_contexts,
        dated_provider=dated_provider,
    )

    action_counts = {}
    for rec in plan_records:
        action_counts[rec["action"]] = action_counts.get(rec["action"], 0) + 1

    if args.mode == "plan":
        print(json.dumps(plan_records, ensure_ascii=False, indent=2))
        sys.stderr.write(
            "PLAN SUMMARY: total=%d by_action=%s\n" % (len(plan_records), action_counts)
        )
        return 0

    if args.mode == "guard":
        guard_view = [
            {
                "file": r["file"],
                "line": r["line"],
                "action": r["action"],
                "guard_pass": r["guard_pass"],
                "rationale": r["rationale"],
            }
            for r in plan_records
            if r["action"] in ("correct", "strip", "delete")
        ]
        print(json.dumps(guard_view, ensure_ascii=False, indent=2))
        fail_count = sum(1 for r in guard_view if r["guard_pass"] is False)
        sys.stderr.write(
            "GUARD SUMMARY: checked=%d fail=%d by_action=%s\n"
            % (len(guard_view), fail_count, action_counts)
        )
        return 0

    # apply
    if live_required_contexts is None:
        sys.stderr.write("ERROR: --mode apply 는 --live-contexts 필요(live_count 산출 불가)\n")
        return 2
    live_count = len(live_required_contexts)
    result = sweep_executor.apply(plan_records, repo_root=repo_root, live_count=live_count)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.stderr.write(
        "APPLY SUMMARY: applied=%s skipped=%d surfaced=%d\n"
        % (result["applied"], result["skipped"], len(result["surfaced"]))
    )
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass
    sys.exit(_main())
