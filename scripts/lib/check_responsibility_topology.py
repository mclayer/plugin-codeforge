#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
scripts/lib/check_responsibility_topology.py
CFP-2422 / ADR-131 §결정 3/4 (Epic CFP-2418 Story 2) — cross-repo 책임 배치
메타불변식 게이트 Python SSOT lint engine (warning tier, exit 3-tier).

consumer overlay `project.yaml` 의 `repo_topology` 섹션(별도 yaml 파일 아님 —
S1/CFP-2419 가 docs/project-config-schema.md 에 신설)을 읽어 cross-repo 책임 배치
메타불변식(ADR-131 §결정2)을 구조적 사실로 hard-block 한다 (기계 판정 — 의미정합은
리뷰어 attestation, ADR-131 §결정4 / ADR-119 검사연극 금지).

검사 (change-plan §3.1 SSOT — exit 3-tier):
  1. layer 분리 게이팅 (fail-open — unconditional, ADR-131 §결정2 verbatim / change-plan §3.6):
     · repo_topology 섹션 미주입            → PASS (exit 0) + honest ::notice::
     · repo_topology.applicable == false    → PASS (exit 0) + honest ::notice::
     · applicable == true + responsibilities 빈 맵 → 스키마 유효성만, 정책 공백 PASS (exit 0) + notice
     ※ 위 3상태 = "정책값 공백" layer = consumer 정책 미주입 (ADR-130 fail-closed 와 다른 LAYER).
  2. 스키마 유효성 (setup-error 게이팅 — exit 2):
     · yaml.safe_load 파싱 실패                              → exit 2 (SETUP·ENV)
     · responsibilities[] 항목 필수필드(responsibility / owner_repo / rationale /
       linked_artifact[≥1]) 키 부재 또는 malformed(타입 위반)  → exit 2 (스키마 무효 = 메타불변식④ SETUP)
     ※ SS-1 경계 (change-plan §8.3): owner_repo 키 부재/malformed = exit2(여기) /
       owner_repo 키 존재 + 빈 리스트(0 entry) = exit1(고아, 아래 3-(a)).
  3. 메타불변식 구조 hard-block (exit 1 — applicable:true + 유효 스키마일 때만 도달):
     (a) 고아 (메타불변식②) — owner_repo well-formed 빈 리스트(0 entry) = 주인없는 책임 → exit 1
     (b) 중복소유 (메타불변식③) — 동일 responsibility 가 N≥2 owner_repo → exit 1
         (동일 책임·동일 레포 2회 선언 = 정규화(set dedup) 후 단일소유면 PASS — 중복선언 ≠ 중복소유)
     (c) 거친파생 (집합 단위) — declared_owner_repos 집합 ≠ actual_changed_repos 집합 →
         exit 1 + 양방향 차집합(declared\actual, actual\declared) 각각 출력

actual_changed_repos 도출 (change-plan §3.2 — offline-first):
  · production 경로: `--changed-repos` 미지정 시 `git diff --name-only` 기반 도출 (gh api 0).
  · fixture/test 경로: `--changed-repos <r1,r2,...>` CLI sentinel 주입 (git diff 우회 — 결정성).
  · 거친파생(c)·고아(a)는 actual_changed_repos 가 비어 있으면 (단일레포 wrapper-self / 변경
    레포 미감지) 비교 비대상 — 정책 공백과 동형 fail-open (false-PASS 아닌 honest no-op).

graceful-degradation (change-plan §3.6 / §7.5-FO — 2-tier 엄격 분리):
  data-absence(A) = fail-open(exit 0, honest ::notice:: — silent default 아님):
    repo_topology 미주입 / applicable:false / 빈맵 = consumer 정책 미주입 layer.
  setup-error(B) = fail-closed(exit 2):
    yaml 파싱 실패 / read 권한 거부 / 스키마 무효 / CLI 인자 형식 오류 = 검증 로직 못 돎.

offline-first (gh 불요 — 입력 전부 repo 내 파일 + git diff). ReDoS-safe (set 비교 = regex-free;
보조 regex 부재). read-only (verifier — write 0).

Usage:
  python3 check_responsibility_topology.py [--root <repo-root>] [--changed-repos <r1,r2,...>]
    → repo-root 의 consumer overlay project.yaml repo_topology scan.
    --root 미지정 시: __file__ 기준 2-level up (scripts/lib/ -> scripts/ -> repo root).
    --changed-repos 미지정 시: git diff --name-only 로 변경 레포 도출 (production).

Exit codes (ADR-060 §결정 5 3-tier — warning tier):
  0 = PASS (메타불변식 위반 0) OR data-absence honest no-op (fail-open)
  1 = 메타불변식 위반 1+ (고아/중복소유/거친파생 — workflow continue-on-error 로 비차단, advisory)
  2 = SETUP error (yaml 파싱 실패 / 스키마 무효 / read 권한 거부 / CLI 인자 형식 오류) — fail-closed

ADR refs: ADR-131 §결정 2/3/4 (carrier — 메타불변식 4종 + 게이트 hard-block + 기계/사람 분리) /
  ADR-130 §결정 2 (layer 대조 — fail-open ≠ fail-closed) / ADR-060 §결정 5/6 (warning-tier
  evidence framework) / ADR-061 §결정 1 (Python SSOT + thin wrapper) / ADR-119 (검사연극 금지).
"""

import argparse
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # PyYAML 부재 = setup-error (B), main 에서 처리
    yaml = None

# Windows cp949 인코딩 문제 회피: stdout/stderr 를 UTF-8 강제 (ADR-061 portability)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


# ─────────────── consumer overlay project.yaml 후보 경로 (repo-root 기준) ──────────────────────
# consumer overlay 의 표준 위치. 첫 실존 후보를 입력 source 로 채택 (data-absence 분기 = 전부 부재).
_OVERLAY_CANDIDATES = [
    ".claude/_overlay/project.yaml",
    ".claude/_overlay/project.yml",
    "project.yaml",
    "project.yml",
]


# ─────────────── 입력 source 해석 ──────────────────────────────────────────────────────────

def _resolve_overlay(root):
    """첫 실존 consumer overlay project.yaml 경로(Path) 반환, 부재 시 None (data-absence)."""
    for rel in _OVERLAY_CANDIDATES:
        cand = root / rel
        if cand.is_file():
            return cand
    return None


def _derive_changed_repos(root, changed_repos_arg):
    """
    actual_changed_repos 집합 도출 (change-plan §3.2 — offline-first).

    · changed_repos_arg 지정(fixture sentinel): comma-split → set (production git diff 우회).
    · 미지정(production): git diff --name-only origin/main...HEAD 기반 → 변경 레포 집합.
      단일레포 wrapper-self = 변경 파일 전부 현 repo → 현 repo 1개 또는 빈 집합(미감지).
      git 미설치/실패 = 빈 집합(honest no-op — 거친파생 비교 비대상, false-PASS 아님).

    Returns: (repos:set[str], note:str|None) — note 는 honest 분류용 ::notice:: 메시지.
    """
    if changed_repos_arg is not None:
        repos = {r.strip() for r in changed_repos_arg.split(",") if r.strip()}
        return repos, None

    # production: git diff 기반. 단일레포면 '현 repo' 식별자 부재 → 거친파생 비교는 빈 집합으로 no-op.
    try:
        # base 후보: origin/main...HEAD (merge-base). 실패 시 빈 diff.
        result = subprocess.run(
            ["git", "-C", str(root), "diff", "--name-only", "origin/main...HEAD"],
            capture_output=True,
            text=True,
            timeout=30,
        )
    except (OSError, subprocess.SubprocessError):
        return set(), (
            "::notice::check-responsibility-topology: actual_changed_repos 도출 — git 미설치/"
            "실패. 거친파생(c)·고아(a) actual-side 비교 비대상 (honest no-op, false-PASS 아님)."
        )
    if result.returncode != 0:
        return set(), (
            "::notice::check-responsibility-topology: actual_changed_repos 도출 — git diff "
            "비정상 종료(rc=%d). actual-side 비교 비대상 (honest no-op)." % result.returncode
        )
    # 단일레포 wrapper-self: 변경 파일은 전부 현 repo 소속 → cross-repo 변경집합 감지 본 Story 범위 외
    # (change-plan §3.2 Out-of-Scope). production 에선 actual-side 빈 집합 = 거친파생 no-op.
    return set(), (
        "::notice::check-responsibility-topology: actual_changed_repos = 단일레포 git diff 기반 "
        "(cross-repo 변경집합 감지 = 본 Story 범위 외, change-plan §3.2). actual-side 비교 비대상."
    )


# ─────────────── 스키마 유효성 (메타불변식④ — exit 2 SETUP) ──────────────────────────────────

def _validate_schema(responsibilities):
    """
    responsibilities[] 각 항목 필수필드 well-formedness 검사 (SS-1a/SS-2/SS-3 = exit 2).

    SS-1 경계 (change-plan §8.3): owner_repo 키 부재/malformed = 여기서 exit2.
      owner_repo 키 존재 + 빈 리스트(0 entry) = well-formed → 여기 통과 → 고아(exit1) 으로 위임.

    Returns: error_message|None — None 이면 스키마 유효(다음 단계 진행).
    """
    if not isinstance(responsibilities, list):
        return (
            "::error::check-responsibility-topology: setup-error — responsibilities 가 list 아님 "
            "(type=%s). 스키마 무효 = 메타불변식④ SETUP (fail-closed exit 2)." % type(responsibilities).__name__
        )

    for idx, item in enumerate(responsibilities):
        if not isinstance(item, dict):
            return (
                "::error::check-responsibility-topology: setup-error — responsibilities[%d] 가 "
                "map 아님 (type=%s). 스키마 무효 (exit 2)." % (idx, type(item).__name__)
            )

        # responsibility — required string
        resp = item.get("responsibility")
        if not isinstance(resp, str) or not resp.strip():
            return (
                "::error::check-responsibility-topology: setup-error — responsibilities[%d].responsibility "
                "키 부재 또는 비-string (스키마 무효, exit 2)." % idx
            )

        # owner_repo — required. SS-1 경계: 키 부재 또는 malformed(비-string·비-list) = exit2.
        #   키 존재 + 빈 리스트 = well-formed → 통과(고아 exit1 로 위임).
        if "owner_repo" not in item:
            return (
                "::error::check-responsibility-topology: setup-error — responsibilities[%d] (책임 '%s') "
                "owner_repo 키 부재 (SS-1a — 스키마 무효 = 메타불변식④ SETUP, exit 2)." % (idx, resp)
            )
        owner = item["owner_repo"]
        # owner_repo 허용 형태: string(정확히 1 소유) 또는 list[string](0=고아, 1=정상, N≥2=중복소유).
        #   string/list 외 타입(int/dict/None 등) = malformed = exit2.
        if not isinstance(owner, (str, list)):
            return (
                "::error::check-responsibility-topology: setup-error — responsibilities[%d] (책임 '%s') "
                "owner_repo malformed (type=%s, string/list 아님 = SS-1a 스키마 무효, exit 2)."
                % (idx, resp, type(owner).__name__)
            )
        if isinstance(owner, list) and any(not isinstance(o, str) for o in owner):
            return (
                "::error::check-responsibility-topology: setup-error — responsibilities[%d] (책임 '%s') "
                "owner_repo list 안 비-string 항목 (malformed = SS-1a 스키마 무효, exit 2)." % (idx, resp)
            )

        # rationale — required string (SS-3)
        rationale = item.get("rationale")
        if not isinstance(rationale, str) or not rationale.strip():
            return (
                "::error::check-responsibility-topology: setup-error — responsibilities[%d] (책임 '%s') "
                "rationale 키 부재 또는 비-string (SS-3 — 필수필드 결손, 스키마 무효 exit 2)." % (idx, resp)
            )

        # linked_artifact — required list, ≥1 (SS-2)
        linked = item.get("linked_artifact")
        if not isinstance(linked, list) or len(linked) < 1:
            return (
                "::error::check-responsibility-topology: setup-error — responsibilities[%d] (책임 '%s') "
                "linked_artifact 키 부재 또는 0개 (SS-2 — ≥1 필수 위반, 스키마 무효 exit 2)." % (idx, resp)
            )
        if any(not isinstance(a, str) or not a.strip() for a in linked):
            return (
                "::error::check-responsibility-topology: setup-error — responsibilities[%d] (책임 '%s') "
                "linked_artifact 안 비-string/빈 항목 (malformed, 스키마 무효 exit 2)." % (idx, resp)
            )

    return None


# ─────────────── 메타불변식 구조 hard-block (exit 1) ─────────────────────────────────────────

def _owner_list(item):
    """owner_repo 를 정규화 list 로 (string → [string], list → list)."""
    owner = item["owner_repo"]
    if isinstance(owner, str):
        return [owner] if owner.strip() else []
    return list(owner)  # list (스키마 유효성 통과 후 — 전부 string)


def _check_metainvariants(responsibilities, actual_changed_repos):
    """
    (a)고아 (b)중복소유 (c)거친파생 검사. Returns: (messages[], violations:int).
    """
    messages = []
    violations = 0
    declared_owner_repos = set()

    for item in responsibilities:
        resp = item["responsibility"]
        owners = _owner_list(item)
        # 정규화(set dedup) — 동일 책임·동일 레포 2회 선언(중복선언) ≠ 중복소유 (change-plan §3.1)
        unique_owners = set(owners)

        # (a) 고아 (메타불변식②): owner_repo well-formed 빈 리스트(0 entry) = 주인없는 책임.
        #   SS-1b 경계 — 키 부재(SS-1a)는 _validate_schema 가 이미 exit2 처리. 여기는 빈 리스트만.
        if len(unique_owners) == 0:
            violations += 1
            messages.append(
                "::warning::check-responsibility-topology: FAIL (a)고아 — 책임 '%s' 의 owner_repo 가 "
                "빈 리스트(0 entry) = 주인없는 책임 (메타불변식②, SS-1b — 키는 well-formed 하나 소유 선언 "
                "부재). hint: repo_topology.responsibilities[].owner_repo 에 정확히 1 소유레포 등재." % resp
            )
            continue  # 고아 = owner 0 → 중복소유·declared 집합 기여 0

        # (b) 중복소유 (메타불변식③): 동일 responsibility 가 N≥2 distinct owner_repo.
        if len(unique_owners) >= 2:
            violations += 1
            messages.append(
                "::warning::check-responsibility-topology: FAIL (b)중복소유 — 책임 '%s' 가 N=%d "
                "owner_repo 에 소유됨 (충돌 레포: %s) = 중복소유 (메타불변식③, 정확히 1 위반). "
                "hint: 단일 소유레포로 통합." % (resp, len(unique_owners), ", ".join(sorted(unique_owners)))
            )

        declared_owner_repos |= unique_owners

    # (c) 거친파생 (집합 단위): declared_owner_repos 집합 ≠ actual_changed_repos 집합.
    #   actual_changed_repos 빈 집합(단일레포 production / 미감지) = 비교 비대상 (honest no-op).
    if actual_changed_repos:
        declared_only = declared_owner_repos - actual_changed_repos
        actual_only = actual_changed_repos - declared_owner_repos
        if declared_only or actual_only:
            violations += 1
            messages.append(
                "::warning::check-responsibility-topology: FAIL (c)거친파생 — declared 소유레포 집합 ≠ "
                "actual 변경레포 집합 (양방향 차집합). declared\\actual = {%s} (소유 선언했으나 미변경) / "
                "actual\\declared = {%s} (변경했으나 소유 선언 부재). hint: repo_topology 갱신 또는 "
                "변경 범위 정합." % (
                    ", ".join(sorted(declared_only)) or "∅",
                    ", ".join(sorted(actual_only)) or "∅",
                )
            )

    return messages, violations


# ─────────────── 메인 검증 ───────────────────────────────────────────────────────────────────

def check_topology(root, changed_repos_arg):
    """
    root(repo root Path) 의 consumer overlay repo_topology 메타불변식 검증.

    Returns: (exit_code, messages[])
      exit_code: 0=PASS or data-absence no-op / 1=violation / 2=setup-error
    """
    # ── data-absence(A): consumer overlay project.yaml 자체 부재 = fail-open EXIT 0 ──
    overlay_path = _resolve_overlay(root)
    if overlay_path is None:
        return 0, [
            "::notice::check-responsibility-topology: data-absence — consumer overlay project.yaml "
            "부재 (후보: %s). repo_topology 미주입 = 정책값 공백 layer(ADR-130 fail-closed 와 다른 "
            "LAYER) = 검증 비대상. honest no-op EXIT 0 (silent default 아님)." % ", ".join(_OVERLAY_CANDIDATES)
        ]

    # ── overlay read (read 권한 거부 = setup-error B = EXIT 2) ──
    try:
        overlay_text = overlay_path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return 2, [
            "::error::check-responsibility-topology: setup-error — overlay read 실패: %s "
            "(검증 로직 실행 불가 = 결과 불명, fail-closed EXIT 2)." % exc
        ]

    # ── yaml.safe_load 파싱 (실패 = setup-error B = EXIT 2 = SS-4) ──
    if yaml is None:
        return 2, [
            "::error::check-responsibility-topology: setup-error — PyYAML 미설치 "
            "(yaml.safe_load 불가, fail-closed EXIT 2)."
        ]
    try:
        doc = yaml.safe_load(overlay_text)
    except yaml.YAMLError as exc:
        return 2, [
            "::error::check-responsibility-topology: setup-error — yaml.safe_load 파싱 실패 (SS-4): %s "
            "(fail-closed EXIT 2)." % exc
        ]

    if doc is None or not isinstance(doc, dict):
        # 빈 overlay / scalar overlay = repo_topology 섹션 부재와 동형 = data-absence
        return 0, [
            "::notice::check-responsibility-topology: data-absence — overlay 가 빈 문서 또는 비-map. "
            "repo_topology 미주입 = 정책 공백 layer = 검증 비대상. honest no-op EXIT 0."
        ]

    # ── layer 분리 게이팅 (fail-open — repo_topology 미주입 / applicable:false / 빈맵) ──
    topo = doc.get("repo_topology")
    if topo is None:
        return 0, [
            "::notice::check-responsibility-topology: data-absence — repo_topology 섹션 미주입. "
            "정책값 공백 layer(consumer opt-in 무손상, ADR-131 §결정2) = 검증 비대상. "
            "honest no-op EXIT 0 (silent default 아님)."
        ]
    if not isinstance(topo, dict):
        return 2, [
            "::error::check-responsibility-topology: setup-error — repo_topology 가 map 아님 "
            "(type=%s). 스키마 무효 (fail-closed EXIT 2)." % type(topo).__name__
        ]

    applicable = topo.get("applicable", False)
    if applicable is not True:
        # applicable:false 또는 미지정 → fail-open. (true 외 모든 값 = opt-in 미활성)
        return 0, [
            "::notice::check-responsibility-topology: data-absence — repo_topology.applicable != true "
            "(value=%r). consumer 정책 opt-in 미활성 = 정책 공백 layer = 검증 비대상. "
            "honest no-op EXIT 0." % applicable
        ]

    # applicable == true → responsibilities 검사 대상.
    responsibilities = topo.get("responsibilities")
    if responsibilities is None or (isinstance(responsibilities, list) and len(responsibilities) == 0):
        # applicable:true + 빈 맵 = 스키마 유효성만 검사·정책 내용 공백 PASS (change-plan §3.6 EC-2).
        return 0, [
            "::notice::check-responsibility-topology: data-absence — repo_topology.applicable=true 이나 "
            "responsibilities 빈 맵. 스키마 유효성만 검사·정책 내용 공백 = PASS (정책값 미주입 layer, "
            "ADR-131 §결정2 EC-2). honest no-op EXIT 0."
        ]

    # ── 스키마 유효성 (메타불변식④ — exit 2 SETUP) ──
    schema_err = _validate_schema(responsibilities)
    if schema_err is not None:
        return 2, [schema_err]

    # ── actual_changed_repos 도출 (offline-first — git diff 또는 sentinel) ──
    actual_changed_repos, derive_note = _derive_changed_repos(root, changed_repos_arg)

    # ── 메타불변식 구조 hard-block (a)고아 (b)중복소유 (c)거친파생 (exit 1) ──
    messages, violations = _check_metainvariants(responsibilities, actual_changed_repos)
    if derive_note:
        messages.insert(0, derive_note)

    if violations:
        messages.append("")
        messages.append(_ACTION_GUIDE)
        messages.append("")
        messages.append(
            "check-responsibility-topology: FAIL %d "
            "(warning tier — continue-on-error 로 비차단, advisory only)" % violations
        )
        return 1, messages

    messages.append(
        "check-responsibility-topology: PASS — cross-repo 책임 배치 메타불변식 OK "
        "((a)고아 0 / (b)중복소유 0 / (c)거친파생 0, applicable:true %d 책임 전수 PASS, warning tier)"
        % len(responsibilities)
    )
    return 0, messages


_ACTION_GUIDE = (
    "[responsibility-topology] 강제 action 2택 (warning mode — merge 비차단, advisory):\n"
    "  ① FAIL 항목별 hint 에 따라 consumer overlay repo_topology.responsibilities[] 정합 복원:\n"
    "     - (a)고아: owner_repo 에 정확히 1 소유레포 등재 (빈 리스트 = 주인없는 책임)\n"
    "     - (b)중복소유: 동일 responsibility 의 N≥2 owner_repo 를 단일 소유레포로 통합\n"
    "     - (c)거친파생: declared 소유레포 집합 ↔ actual 변경레포 집합 정합 (repo_topology 갱신)\n"
    "  ② hotfix-bypass:responsibility-topology label + audit comment\n"
    "     (check-bypass-audit-comment.sh 마커 패턴)\n"
    "근거: ADR-131 §결정 3/4 (CFP-2422, Epic CFP-2418 Story 2) — cross-repo 책임 배치 메타불변식 "
    "게이트. 기계(구조 hard-block — 고아/중복/거친파생) vs 사람(의미정합 attestation — review-"
    "responsibility 매트릭스 행 (d)) 판정 분리. 의미정합('올바른 레포인가')은 리뷰어 위임 "
    "(GitHub CODEOWNERS 동형 — 구조 매칭만 강제, owner 적절성은 리뷰어, ADR-119 검사연극 금지)."
)


# ─────────────── main ──────────────────────────────────────────────────────────────────────

def _discover_root():
    # __file__ = <repo_root>/scripts/lib/check_responsibility_topology.py
    return Path(__file__).resolve().parent.parent.parent


def main(argv):
    parser = argparse.ArgumentParser(
        description="cross-repo 책임 배치 메타불변식 게이트 (CFP-2422 / ADR-131)",
        add_help=True,
    )
    parser.add_argument(
        "--root",
        metavar="PATH",
        default=None,
        help="repo root (default: __file__ 기준 2-level up)",
    )
    parser.add_argument(
        "--changed-repos",
        metavar="r1,r2,...",
        default=None,
        help="actual_changed_repos sentinel (comma-separated). 미지정 시 git diff 도출 (production).",
    )
    try:
        args = parser.parse_args(argv[1:])
    except SystemExit:
        # argparse 형식 오류 = setup-error (B) = EXIT 2
        return 2

    root = Path(args.root).resolve() if args.root else _discover_root()

    if not root.is_dir():
        print(
            "::error::check-responsibility-topology: setup-error — repo root not a dir: %s "
            "(fail-closed EXIT 2)." % root,
            file=sys.stderr,
        )
        return 2

    exit_code, messages = check_topology(root, args.changed_repos)
    for msg in messages:
        print(msg)
    return exit_code


if __name__ == "__main__":
    sys.exit(main(sys.argv))
