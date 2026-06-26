#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
scripts/lib/check_responsibility_marker_drift.py
CFP-2428 / ADR-131 Amendment 1 (Epic CFP-2418 deferred FU) — declared-marker layer
(L1 코드→책임) drift 검출 게이트 Python SSOT lint engine (warning tier, exit 3-tier).

consumer overlay `project.yaml` 의 `repo_topology.responsibility_markers` 섹션(별도 yaml 파일
아님 — CFP-2428 가 docs/project-config-schema.md 에 sibling 신설)을 읽어, 선언마커(L1)가 상위
토폴로지(L2 responsibilities[]) 및 실제 파일시스템(L3)과 transitive 일관성을 유지하는지 *구조적
으로만* 대조하고 drift 3종을 warning 으로 surface 한다 (기계 = 구조 대조 only, 의미정합은 리뷰어
attestation — ADR-131 §결정4 / ADR-119 검사연극 금지).

3-layer transitive 일관성 모델 (change-plan §3.0):
  L1 코드→책임   responsibility_markers[]            (사람 선언, per-repo)  — 본 게이트 신설
  L2 책임→레포   responsibilities[]                  (사람 선언, overlay)   — CFP-2422 (L2 게이트)
  L3 실제 위치   파일시스템 실제 경로 존재           (기계 관측 fs-stat)
  join-key = responsibility 단일 namespace (byte-identical 계약) — L1·L2 묶는 유일 연결고리.
  drift = 이 키 기준 set 대조 (의미 추론 0 — 문자열 매칭).

검사 (change-plan §3.2 SSOT — exit 3-tier):
  1. layer 분리 게이팅 (fail-open — unconditional, ADR-131 §결정2 동형 / change-plan §3.2):
     · repo_topology 섹션 미주입                       → PASS (exit 0) + honest ::notice::
     · repo_topology.applicable != true                 → PASS (exit 0) + honest ::notice::
     · responsibility_markers 미주입                    → PASS (exit 0) + honest ::notice::
     · applicable:true + responsibility_markers 빈 맵    → 스키마 유효성만, 정책 공백 PASS (exit 0) + notice
     ※ 위 = "정책값 공백" layer = consumer 정책 미주입 (ADR-130 fail-closed 와 다른 LAYER).
  2. 스키마 유효성 (setup-error 게이팅 — exit 2):
     · yaml.safe_load 파싱 실패                                  → exit 2 (SETUP·ENV)
     · responsibility_markers[] 항목 필수필드(path / responsibility) 키 부재 또는
       malformed(타입 위반)                                      → exit 2 (스키마 무효 = SETUP)
       (repo 는 선택 — 지정 시 non-empty str, 부재 tolerate)
  3. drift 구조 surface (exit 1 — applicable:true + 유효 스키마일 때만 도달):
     (a) unmarked     — L2 책임 R 이 L1 manifest 에 entry 0 (set-diff
                        {responsibilities.responsibility} − {markers.responsibility} ≠ ∅) → exit 1
     (b) 불일치       — repo 지정된 marker entry 의 marker.repo ≠ topology.owner_repo[R]
                        (문자열 동등; owner_repo string/list 정규화 후 비교) → exit 1
     (c) stale        — marker entry path/glob 이 fs 에 부재 (os.path.exists / glob.glob 0건) → exit 1
     + 역방향 고아    — marker.responsibility 가 L2 topology 에 없음 = informational ::notice:: 만
                        (warning 아님, drift 카운트 0 — micro-decision ③ falsify)

exit 매트릭스 (falsifiable — change-plan §3.2, L2 게이트 동형 5상태):
  responsibility_markers 미주입            → 0  (fail-open PASS + honest ::notice::)
  repo_topology.applicable != true         → 0  (fail-open PASS + honest ::notice::)
  applicable:true + responsibility_markers 빈 맵 → 0 (fail-open PASS, 스키마 유효성만)
  manifest malformed(필수필드 부재·yaml 파싱 실패) → 2 (setup-error fail-closed)
  drift 위반 (a/b/c 1+) 검출                → 1  (warning, continue-on-error 라 merge 비차단)

graceful-degradation (change-plan §7.1 / §3.2 — 2-tier 엄격 분리):
  data-absence(A) = fail-open(exit 0, honest ::notice:: — silent default 아님):
    repo_topology 미주입 / applicable!=true / markers 미주입 / 빈맵 = consumer 정책 미주입 layer.
  setup-error(B) = fail-closed(exit 2):
    yaml 파싱 실패 / read 권한 거부 / 스키마 무효 / CLI 인자 형식 오류 = 검증 로직 못 돎.

offline-first (gh 불요 — 입력 전부 repo 내 파일 + fs-stat). ReDoS-safe (set 비교 = regex-free).
read-only (verifier — write 0). stale(c) = fs only (gh 0), L2 게이트의 git diff 는 본 게이트 비사용
  (drift 는 manifest↔fs/topology 대조라 변경레포 집합 불요).

Usage:
  python3 check_responsibility_marker_drift.py [--root <repo-root>]
    → repo-root 의 consumer overlay project.yaml repo_topology.responsibility_markers scan.
    --root 미지정 시: __file__ 기준 2-level up (scripts/lib/ -> scripts/ -> repo root).

Exit codes (ADR-060 §결정 5 3-tier — warning tier):
  0 = PASS (drift 0) OR data-absence honest no-op (fail-open)
  1 = drift 위반 1+ (unmarked/불일치/stale — workflow continue-on-error 로 비차단, advisory)
  2 = SETUP error (yaml 파싱 실패 / 스키마 무효 / read 권한 거부 / CLI 인자 형식 오류) — fail-closed

ADR refs: ADR-131 Amendment 1 (carrier — declared-marker layer L1 + drift 3종 + 기계/사람 분리) /
  ADR-131 §결정2 (layer 대조 — fail-open ≠ fail-closed) / ADR-130 §결정2 (layer 분리) /
  ADR-060 §결정 5/6 (warning-tier evidence framework) / ADR-061 §결정 1 (Python SSOT + thin wrapper) /
  ADR-119 (검사연극 금지). disjoint from CFP-2422 (L1 marker vs L2 topology — 같은 부모, 검사 명제 비중첩).
"""

import argparse
import glob as globmod
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
# CFP-2422 _OVERLAY_CANDIDATES 동일 (동일 overlay project.yaml — 신규 경로 0).
_OVERLAY_CANDIDATES = [
    ".claude/_overlay/project.yaml",
    ".claude/_overlay/project.yml",
    "project.yaml",
    "project.yml",
]


# ─────────────── 입력 source 해석 (CFP-2422 _resolve_overlay 동형 재사용) ────────────────────

def _resolve_overlay(root):
    """첫 실존 consumer overlay project.yaml 경로(Path) 반환, 부재 시 None (data-absence)."""
    for rel in _OVERLAY_CANDIDATES:
        cand = root / rel
        if cand.is_file():
            return cand
    return None


# ─────────────── 스키마 유효성 (setup-error — exit 2) ──────────────────────────────────────────

def _validate_marker_schema(markers):
    """
    responsibility_markers[] 각 항목 필수필드 well-formedness 검사 (exit 2 SETUP).

    필수: path / responsibility (non-empty str). 선택: repo (지정 시 non-empty str).
    L2 _validate_schema 패턴 동형 — 필수필드 부재·타입 위반 = 스키마 무효 = exit2.

    Returns: error_message|None — None 이면 스키마 유효(다음 단계 진행).
    """
    if not isinstance(markers, list):
        return (
            "::error::check-responsibility-marker-drift: setup-error — responsibility_markers 가 list "
            "아님 (type=%s). 스키마 무효 (fail-closed exit 2)." % type(markers).__name__
        )

    for idx, item in enumerate(markers):
        if not isinstance(item, dict):
            return (
                "::error::check-responsibility-marker-drift: setup-error — responsibility_markers[%d] 가 "
                "map 아님 (type=%s). 스키마 무효 (exit 2)." % (idx, type(item).__name__)
            )

        # path — required string
        path_val = item.get("path")
        if not isinstance(path_val, str) or not path_val.strip():
            return (
                "::error::check-responsibility-marker-drift: setup-error — responsibility_markers[%d].path "
                "키 부재 또는 비-string (스키마 무효, exit 2)." % idx
            )

        # responsibility — required string (join-key)
        resp = item.get("responsibility")
        if not isinstance(resp, str) or not resp.strip():
            return (
                "::error::check-responsibility-marker-drift: setup-error — responsibility_markers[%d] "
                "(path '%s') responsibility 키 부재 또는 비-string (join-key 필수, 스키마 무효 exit 2)."
                % (idx, path_val)
            )

        # repo — optional. 지정 시 non-empty string (malformed = exit2).
        if "repo" in item:
            repo_val = item["repo"]
            if not isinstance(repo_val, str) or not repo_val.strip():
                return (
                    "::error::check-responsibility-marker-drift: setup-error — responsibility_markers[%d] "
                    "(path '%s') repo malformed (지정 시 non-empty string 의무, exit 2)." % (idx, path_val)
                )

    return None


# ─────────────── owner_repo 정규화 (L2 string/list → 비교용 set) ─────────────────────────────

def _owner_repos_for(responsibilities, resp_key):
    """
    L2 responsibilities 에서 join-key=resp_key 의 owner_repo 집합(정규화 set[str]) 반환.
    owner_repo 는 string(1) 또는 list[string](0/1/N) 허용 — set 으로 정규화.
    resp_key 가 topology 에 없으면 빈 set (역방향 고아 — 호출부에서 별 처리).
    """
    owners = set()
    for item in responsibilities:
        if not isinstance(item, dict):
            continue
        if item.get("responsibility") != resp_key:
            continue
        owner = item.get("owner_repo")
        if isinstance(owner, str):
            if owner.strip():
                owners.add(owner)
        elif isinstance(owner, list):
            owners |= {o for o in owner if isinstance(o, str) and o.strip()}
    return owners


# ─────────────── drift 구조 surface (exit 1) ────────────────────────────────────────────────

def _check_marker_drift(markers, responsibilities, root):
    """
    (a)unmarked (b)불일치 (c)stale + 역방향 고아 검사. Returns: (messages[], violations:int).

    의미 추론 0 — 전부 관측 가능 구조적 사실(set-diff / 문자열동등 / fs-stat).
    """
    messages = []
    violations = 0

    topology_resps = {
        item.get("responsibility")
        for item in responsibilities
        if isinstance(item, dict) and isinstance(item.get("responsibility"), str)
    }
    marker_resps = {m["responsibility"] for m in markers}

    # (a) unmarked: L2 책임 R 이 L1 manifest 에 entry 0 (set-diff topology − markers).
    unmarked = topology_resps - marker_resps
    if unmarked:
        violations += 1
        messages.append(
            "::warning::check-responsibility-marker-drift: FAIL (a)unmarked — 토폴로지 책임이 marker "
            "manifest 에 미마킹 (책임: %s). hint: repo_topology.responsibility_markers[] 에 해당 책임의 "
            "코드 경로/모듈 entry 등재 (path + responsibility join-key)."
            % ", ".join(sorted(unmarked))
        )

    # (b) 불일치 + (c) stale + 역방향 고아 — entry 별 순회.
    mismatch_msgs = []
    stale_msgs = []
    reverse_orphans = []
    for m in markers:
        resp = m["responsibility"]
        path_val = m["path"]

        # 역방향 고아: marker.responsibility 가 L2 topology 에 없음 = ::notice:: 만 (warning 아님).
        if resp not in topology_resps:
            reverse_orphans.append((path_val, resp))

        # (b) 불일치: repo 지정된 entry 한정 — marker.repo ≠ owner_repo[R] (문자열 동등).
        #   join-key 가 topology 에 있을 때만 의미 있음 (없으면 역방향 고아로 surface, (b) 비대상).
        if "repo" in m and resp in topology_resps:
            owners = _owner_repos_for(responsibilities, resp)
            if owners and m["repo"] not in owners:
                mismatch_msgs.append(
                    "::warning::check-responsibility-marker-drift: FAIL (b)불일치 — marker(path '%s', 책임 "
                    "'%s')의 repo '%s' ≠ topology.owner_repo[%s] {%s} (문자열 동등 위반). hint: marker.repo 를 "
                    "토폴로지 소유레포로 정합 또는 토폴로지 owner_repo 갱신."
                    % (path_val, resp, m["repo"], resp, ", ".join(sorted(owners)))
                )

        # (c) stale: path/glob 이 fs 에 부재 (offline-first fs-stat).
        if not _path_exists(root, path_val):
            stale_msgs.append(
                "::warning::check-responsibility-marker-drift: FAIL (c)stale — marker(책임 '%s') path/glob "
                "'%s' 가 fs 에 부재 (이동·소멸 코드). hint: 경로 갱신 또는 stale entry 제거."
                % (resp, path_val)
            )

    if mismatch_msgs:
        violations += 1
        messages.extend(mismatch_msgs)
    if stale_msgs:
        violations += 1
        messages.extend(stale_msgs)

    # 역방향 고아 = informational ::notice:: (warning 아님, drift 카운트 0 — micro-decision ③).
    for path_val, resp in reverse_orphans:
        messages.append(
            "::notice::check-responsibility-marker-drift: 역방향 고아 — marker(path '%s')의 책임 '%s' 가 "
            "L2 토폴로지 responsibilities[] 에 없음 (manifest 가 토폴로지보다 앞서 마킹 가능 = 정상 진행 중). "
            "informational only — warning/drift 아님 (micro-decision ③)." % (path_val, resp)
        )

    return messages, violations


def _path_exists(root, path_val):
    """
    marker path/glob 이 fs 에 실존하는지 (offline-first fs-stat).
    · glob 메타문자(* ? [) 포함 = glob.glob (recursive) 매칭 1+ 이면 존재.
    · 일반 경로 = os.path.exists.
    """
    target = path_val
    if any(ch in target for ch in ("*", "?", "[")):
        pattern = str(root / target)
        matches = globmod.glob(pattern, recursive=True)
        return len(matches) > 0
    return (root / target).exists()


# ─────────────── 메인 검증 ───────────────────────────────────────────────────────────────────

def check_marker_drift(root):
    """
    root(repo root Path) 의 consumer overlay responsibility_markers drift 검증.

    Returns: (exit_code, messages[])
      exit_code: 0=PASS or data-absence no-op / 1=drift / 2=setup-error
    """
    # ── data-absence(A): consumer overlay project.yaml 자체 부재 = fail-open EXIT 0 ──
    overlay_path = _resolve_overlay(root)
    if overlay_path is None:
        return 0, [
            "::notice::check-responsibility-marker-drift: data-absence — consumer overlay project.yaml "
            "부재 (후보: %s). repo_topology 미주입 = 정책값 공백 layer = 검증 비대상. honest no-op EXIT 0 "
            "(silent default 아님)." % ", ".join(_OVERLAY_CANDIDATES)
        ]

    # ── overlay read (read 권한 거부 = setup-error B = EXIT 2) ──
    try:
        overlay_text = overlay_path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return 2, [
            "::error::check-responsibility-marker-drift: setup-error — overlay read 실패: %s "
            "(검증 로직 실행 불가 = 결과 불명, fail-closed EXIT 2)." % exc
        ]

    # ── yaml.safe_load 파싱 (실패 = setup-error B = EXIT 2) ──
    if yaml is None:
        return 2, [
            "::error::check-responsibility-marker-drift: setup-error — PyYAML 미설치 "
            "(yaml.safe_load 불가, fail-closed EXIT 2)."
        ]
    try:
        doc = yaml.safe_load(overlay_text)
    except yaml.YAMLError as exc:
        return 2, [
            "::error::check-responsibility-marker-drift: setup-error — yaml.safe_load 파싱 실패: %s "
            "(fail-closed EXIT 2)." % exc
        ]

    if doc is None or not isinstance(doc, dict):
        return 0, [
            "::notice::check-responsibility-marker-drift: data-absence — overlay 가 빈 문서 또는 비-map. "
            "repo_topology 미주입 = 정책 공백 layer = 검증 비대상. honest no-op EXIT 0."
        ]

    # ── layer 분리 게이팅 (fail-open — repo_topology 미주입 / applicable!=true) ──
    topo = doc.get("repo_topology")
    if topo is None:
        return 0, [
            "::notice::check-responsibility-marker-drift: data-absence — repo_topology 섹션 미주입. "
            "정책값 공백 layer(consumer opt-in 무손상, ADR-131 §결정2) = 검증 비대상. honest no-op EXIT 0."
        ]
    if not isinstance(topo, dict):
        return 2, [
            "::error::check-responsibility-marker-drift: setup-error — repo_topology 가 map 아님 "
            "(type=%s). 스키마 무효 (fail-closed EXIT 2)." % type(topo).__name__
        ]

    applicable = topo.get("applicable", False)
    if applicable is not True:
        return 0, [
            "::notice::check-responsibility-marker-drift: data-absence — repo_topology.applicable != true "
            "(value=%r). consumer 정책 opt-in 미활성 = 정책 공백 layer = 검증 비대상. honest no-op EXIT 0."
            % applicable
        ]

    # ── responsibility_markers 미주입 / 빈맵 = fail-open EXIT 0 ──
    markers = topo.get("responsibility_markers")
    if markers is None or (isinstance(markers, list) and len(markers) == 0):
        return 0, [
            "::notice::check-responsibility-marker-drift: data-absence — repo_topology.applicable=true 이나 "
            "responsibility_markers 미주입 또는 빈 맵. marker layer(L1) 정책 공백 = PASS (스키마 유효성만, "
            "ADR-131 §결정2 동형). honest no-op EXIT 0 (silent default 아님)."
        ]

    # ── 스키마 유효성 (setup-error — exit 2) ──
    schema_err = _validate_marker_schema(markers)
    if schema_err is not None:
        return 2, [schema_err]

    # ── responsibilities(L2) 도출 — 없으면 빈 list (전부 unmarked 0 + 전부 역방향 고아 가능) ──
    responsibilities = topo.get("responsibilities")
    if not isinstance(responsibilities, list):
        responsibilities = []

    # ── drift 구조 surface (a)unmarked (b)불일치 (c)stale + 역방향 고아 (exit 1) ──
    messages, violations = _check_marker_drift(markers, responsibilities, root)

    if violations:
        messages.append("")
        messages.append(_ACTION_GUIDE)
        messages.append("")
        messages.append(
            "check-responsibility-marker-drift: FAIL %d "
            "(warning tier — continue-on-error 로 비차단, advisory only)" % violations
        )
        return 1, messages

    messages.append(
        "check-responsibility-marker-drift: PASS — declared-marker drift OK "
        "((a)unmarked 0 / (b)불일치 0 / (c)stale 0, applicable:true %d marker 전수 PASS, warning tier)"
        % len(markers)
    )
    return 0, messages


_ACTION_GUIDE = (
    "[responsibility-marker-drift] 강제 action 2택 (warning mode — merge 비차단, advisory):\n"
    "  ① FAIL 항목별 hint 에 따라 consumer overlay repo_topology.responsibility_markers[] 정합 복원:\n"
    "     - (a)unmarked: 토폴로지 책임의 코드 경로/모듈을 marker manifest 에 등재 (path + responsibility join-key)\n"
    "     - (b)불일치: marker.repo 를 토폴로지 owner_repo 로 정합 (또는 토폴로지 갱신)\n"
    "     - (c)stale: 이동·소멸 코드 경로를 갱신 또는 stale entry 제거\n"
    "  ② hotfix-bypass:responsibility-marker-drift label + audit comment\n"
    "     (check-bypass-audit-comment.sh 마커 패턴 — warning-tier 비차단이라 통상 불요)\n"
    "근거: ADR-131 Amendment 1 (CFP-2428, Epic CFP-2418 deferred FU) — declared-marker layer(L1 코드→책임) "
    "drift 게이트. 기계(구조 대조 — unmarked/불일치/stale) vs 사람(의미정합 attestation — review-"
    "responsibility 매트릭스 행 (d)) 판정 분리. 의미정합('R 이 *의미상* 옳은 레포인가')은 리뷰어 위임 "
    "(GitHub CODEOWNERS 동형 — 구조 매칭만 강제, owner 적절성은 리뷰어, ADR-119 검사연극 금지)."
)


# ─────────────── main ──────────────────────────────────────────────────────────────────────

def _discover_root():
    # __file__ = <repo_root>/scripts/lib/check_responsibility_marker_drift.py
    return Path(__file__).resolve().parent.parent.parent


def main(argv):
    parser = argparse.ArgumentParser(
        description="declared-marker layer(L1) drift 게이트 (CFP-2428 / ADR-131 Amendment 1)",
        add_help=True,
    )
    parser.add_argument(
        "--root",
        metavar="PATH",
        default=None,
        help="repo root (default: __file__ 기준 2-level up)",
    )
    try:
        args = parser.parse_args(argv[1:])
    except SystemExit:
        # argparse 형식 오류 = setup-error (B) = EXIT 2
        return 2

    root = Path(args.root).resolve() if args.root else _discover_root()

    if not root.is_dir():
        print(
            "::error::check-responsibility-marker-drift: setup-error — repo root not a dir: %s "
            "(fail-closed EXIT 2)." % root,
            file=sys.stderr,
        )
        return 2

    exit_code, messages = check_marker_drift(root)
    for msg in messages:
        print(msg)
    return exit_code


if __name__ == "__main__":
    sys.exit(main(sys.argv))
