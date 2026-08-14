"""test_hook_spawn_census.py — 체인 Bash 훅 7종 호출당 프로세스 계보 census (정본 ==33).

계약 SSOT: Story CFP-2939 §8 T-D11 (census 호출당 프로세스 계보) / ArchitectPL verdict.

==== 계약식 (정본 — 불변) ====

    census(hook) = 2 (기동 계층: run-hook.cmd + bash)
                 + count_exec_sites(훅 텍스트 ⊕ source 로 편입된 wrapper 텍스트)

    count_exec_sites = raw_sites − CONDITIONAL_EXCLUDED (Layer 1 − Layer 2)

per-hook 정본 (census, 기동 2 포함):
    cross-repo-gh-safety                7
    repo-confinement                    5
    git-branch-delete-merge-gate        4
    worktree-location-guard             5
    pretooluse-bash-description-inject  4
    pretooluse-dev-process-capture      4
    posttooluse-dev-process-capture     4
                                       ── total 33

==== 2-layer 구조 (블록 깊이 추적 휴리스틱 미도입) ====

Layer 1 (기계적 raw parse) — 문맥 무지(context-free). 조건부/무조건 구분을 하지 않는다.
Layer 2 (명시 제외 표 CONDITIONAL_EXCLUDED) — 조건부 경로 site 를 file·token·포함-라인
  substring·사유 4-tuple 로 pin. 각 항목은 실제 site 와 **정확히 1:1** 로 매칭돼야 하며
  (미발견 = FAIL), 매칭 실패 시 제외가 조용히 증발하지 않고 테스트가 깨진다.

블록 깊이 추적(if/{} 중첩 파싱)은 도입하지 않는다 — 파서가 정본을 스스로 재정의하며
진동한 이력이 있어, "기계 파싱은 문맥 무지 + 편차는 명시 표" 2-layer 가 확정 방식이다.

==== Layer 1 계수 정의역 (domain) ====

(a) top-level command substitution `$(...)` — 균형 괄호 스캔으로 span 추출 후
    파이프 `|` 로 분해해 세그먼트별 1 site.
    · 중첩 `$( ... $(...) ... )` = 외곽 1 site (내부 미하강). 예: `$(cd "$(dirname "$0")" && pwd)` = 1
    · `&&` 는 분해하지 않음 (같은 substitution 의 연쇄 = 1 계보 단위로 취급)
    · `||` 는 `|` split 의 부수효과로 분해됨 → fallback 세그먼트가 별 site 로 잡히고,
      실행되지 않는 상시 경로 밖 fallback 은 Layer 2 에서 제외된다.
(b) 변수 간접 호출 `"$PY"` / `"$PYTHON_CMD"` (뒤에 공백이 오는 형태).

==== 정의역 밖 (한계 — 정직 선언) ====

- `$(...)` 밖 top-level 파이프라인의 리터럴 명령 (예: cross-repo-gh-safety 의
  `printf ... | grep -Eq ...` if-조건, `>&2 cat <<'BLOCKMSG'`) = **미계수**.
- wrapper 의 리터럴 `exec python3 "${PYTHON_SSOT}"` 같은 고정 이름 명령 = **미계수**
  (변수 간접 호출만 (b) 로 계수).
- 중첩 substitution 내부의 실제 fork (`$(dirname ...)`) = 외곽에 흡수돼 미분해.
- 동적 전개(`cmd="ls"; $($cmd)`) · eval · 런타임 생성 명령 = 정적 파싱 원리상 미검출.
- 따라서 본 수치는 "실제 프로세스 총수"가 아니라 **선언된 정의역 안의 계보 지표**다.
  ratchet(회귀 감지) 목적에는 충분하되, 절대 프로세스 수로 인용하면 안 된다.

==== source 편입 (④a fork 제거 대응) ====

repo-confinement / worktree-location-guard 는 CFP-2965 S10 ④a 로 `bash "${SCRIPT}"`
fork 를 `source "${SCRIPT}"` 로 바꿨다. source 는 같은 셸에서 실행되므로 wrapper 의
exec site 가 훅 자신의 계보에 합류한다 → wrapper 텍스트를 계수 정의역에 편입한다.
편입은 하드코딩이 아니라 훅 텍스트의 `source "${VAR}"` 라인 + `VAR="..."` 대입을
실제로 파싱해 해석하며, source 라인 실재는 test_sourced_wrapper_integration 이 assert 한다.

==== 한계: presence ≠ truth ====

본 테스트는 정적 텍스트 계수의 **일관성**만 강제한다. 계수 정의가 런타임 프로세스
실측과 일치함을 증명하지 않는다 (실측 축 = tests/perf/reports/cfp2965-comparison.md).
"""

from __future__ import annotations

import re
from collections import namedtuple
from pathlib import Path
from typing import Dict, List, Tuple

WORKTREE_ROOT = Path(__file__).resolve().parent.parent.parent
HOOKS_DIR = WORKTREE_ROOT / "hooks"

# 기동 계층 상수 — hooks.json 구조 기반 (run-hook.cmd + bash). 훅 텍스트에 나타나지 않음.
LAUNCH_LAYER = 2

# 대상 = 체인 Bash 훅 7종
CHAIN_HOOKS = [
    "cross-repo-gh-safety",
    "repo-confinement",
    "git-branch-delete-merge-gate",
    "worktree-location-guard",
    "pretooluse-bash-description-inject",
    "pretooluse-dev-process-capture",
    "posttooluse-dev-process-capture",
]

# ============================================================
# 정본 계약 (ArchitectPL verdict — 불변 oracle)
# 이 표는 파서 산출에 맞춰 조정하지 않는다. 불일치 = 파서/제외표를 고친다.
# ============================================================
CANONICAL_CENSUS: Dict[str, int] = {
    "cross-repo-gh-safety": 7,
    "repo-confinement": 5,
    "git-branch-delete-merge-gate": 4,
    "worktree-location-guard": 5,
    "pretooluse-bash-description-inject": 4,
    "pretooluse-dev-process-capture": 4,
    "posttooluse-dev-process-capture": 4,
}
CANONICAL_TOTAL = 33


# ============================================================
# Layer 2: 조건부 제외 표 (명시 제외 — auditable, 1:1 pin)
#
# 각 항목 = (파일명, 토큰, 포함-라인 substring, 사유)
#   · 파일명 = site 가 실재하는 파일 (훅 또는 source 로 편입된 wrapper)
#   · 토큰   = site 의 선두 명령어 (변수 간접 호출은 `$PY` / `$PYTHON_CMD`)
#   · substring = 그 site 를 포함하는 라인의 판별용 부분 문자열
#   · 사유   = 왜 상시 경로가 아닌가
#
# 분류 (3 범주):
#   [A] bypass audit 블록 내부 — BYPASS_* 가 설정된 세션에서만 실행
#   [B] `||` 오류/fallback 경로 — 선행 명령 실패 시에만 실행
#   [C] test 문맥 — 실행 site 가 아님 (Layer 1 변수 패턴의 false-positive)
#
# ★ [C] 는 packet 이 예시한 3 범주(bypass / delete 분기 / 오류 경로) 와 별개 범주다.
#   임의 제외가 아니라 **실행되지 않는 것이 실물로 확인되는 항목**이라 제외한다:
#   `if [ -z "$PYTHON_CMD" ]; then` 은 변수를 test 하는 조건식이지 호출이 아니다.
#   (동시에 python 부재 fail-open 분기의 가드이기도 하다.)
#   이 1건은 DeveloperPL 보고에 명시 flag 한다 — 은닉 제외 아님.
# ============================================================
CONDITIONAL_EXCLUDED: List[Tuple[str, str, str, str]] = [
    # ── cross-repo-gh-safety: raw 7 → 5 ────────────────────────────────────────
    ("cross-repo-gh-safety", "date", "guard suppressed at %s",
     "[A] BYPASS_CROSS_REPO_GH_SAFETY=1 audit 블록 내부"),
    ("cross-repo-gh-safety", "true", 'PAYLOAD="$(cat 2>/dev/null || true)"',
     "[B] payload 판독 실패 시에만 실행되는 `|| true` fallback"),

    # ── git-branch-delete-merge-gate: raw 4 → 2 ───────────────────────────────
    ("git-branch-delete-merge-gate", "date", "gate suppressed at %s",
     "[A] BYPASS_BRANCH_DELETE_MERGE_GATE=1 audit 블록 내부"),
    ("git-branch-delete-merge-gate", "echo", "gate suppressed at %s",
     "[B] 같은 bypass 블록 내 date 실패 시에만 실행되는 `|| echo unknown` fallback"),

    # ── pretooluse-bash-description-inject: raw 5 → 2 ─────────────────────────
    ("pretooluse-bash-description-inject", "date", "description injection suppressed at %s",
     "[A] BYPASS_CODEFORGE_BASH_DESCRIPTION_INJECT=1 audit 블록 내부"),
    ("pretooluse-bash-description-inject", "true", 'PAYLOAD="$(cat 2>/dev/null || true)"',
     "[B] payload 판독 실패 시에만 실행되는 `|| true` fallback"),
    ("pretooluse-bash-description-inject", "$PYTHON_CMD", 'if [ -z "$PYTHON_CMD" ]',
     "[C] python 부재 fail-open 분기의 test 조건식 — 호출 site 아님"),
]


# ============================================================ Layer 1: 기계적 raw parse

ExecSite = namedtuple("ExecSite", "file_name line_no kind token text line_text")

# 변수 간접 호출 패턴 — `"$PY"` / `"$PYTHON_CMD"` (뒤 공백)
_VAR_EXEC_RE = re.compile(r'"?\$(?:PY|PYTHON_CMD)"(?=\s)')

# `source "${SCRIPT}"` / `. "${SCRIPT}"` 라인
_SOURCE_LINE_RE = re.compile(r'^\s*(?:source|\.)\s+"?\$\{?([A-Za-z_][A-Za-z0-9_]*)\}?"?\s*$')


def extract_command_substitutions(line: str) -> List[str]:
    """한 줄에서 **top-level** `$(...)` span 의 내부 텍스트를 균형 괄호로 추출.

    중첩 `$( ... $(...) ... )` 는 외곽 span 만 반환하고 내부로 하강하지 않는다
    (스캔 커서를 외곽 span 끝으로 점프시켜 내부 `$(` 를 건너뛴다).

    균형 스캔이 필요한 이유(naive `\\$\\([^)]*\\)` 로는 부족):
      cross-repo-gh-safety:55 의 sed 스크립트는 `\\(...\\)` 를 포함해 첫 `)` 에서
      span 이 조기 절단되고, 뒤따르는 `| sed | head` 파이프 단이 통째로 증발한다.
      (절단 상태에서는 그 줄에 파이프 단을 추가해도 계수가 변하지 않아 mutant 가
       생존한다 — 즉 계수기의 판별력 자체가 무너진다.)
    """
    spans: List[str] = []
    i, n = 0, len(line)
    while i < n - 1:
        if line[i] == "$" and line[i + 1] == "(":
            depth = 1
            j = i + 2
            while j < n and depth > 0:
                if line[j] == "(":
                    depth += 1
                elif line[j] == ")":
                    depth -= 1
                j += 1
            if depth != 0:
                break  # 미종결 span (여러 줄 확장) → 계수 포기
            spans.append(line[i + 2:j - 1])
            i = j
            continue
        i += 1
    return spans


def _sites_in_line(file_name: str, line_no: int, line: str) -> List[ExecSite]:
    sites: List[ExecSite] = []

    for inner in extract_command_substitutions(line):
        if not inner:
            continue
        if inner.startswith("{") and inner.endswith("}"):
            continue  # `${...}` 변수 전개 — 호출 아님
        for seg in inner.split("|"):
            seg = seg.strip()
            if not seg:
                continue
            if seg.startswith("(") or seg.startswith(">") or seg.startswith("2"):
                continue  # 서브셸 그룹 / 리다이렉트 전용 세그먼트
            token = seg.split()[0].strip("\"'")
            sites.append(ExecSite(file_name, line_no, "CS", token, seg, line))

    for m in _VAR_EXEC_RE.finditer(line):
        token = m.group(0).strip('"')
        sites.append(ExecSite(file_name, line_no, "VAR", token, m.group(0), line))

    return sites


def _raw_sites_in_file(path: Path) -> List[ExecSite]:
    text = path.read_text(encoding="utf-8", errors="replace")
    sites: List[ExecSite] = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        sites.extend(_sites_in_line(path.name, line_no, line))
    return sites


def resolve_sourced_files(hook_path: Path) -> List[Tuple[str, str, Path]]:
    """훅 텍스트의 `source "${VAR}"` 를 실제 파일 경로로 해석.

    Returns: [(변수명, 원문 대입값, 해석된 절대경로), ...]  (없으면 빈 리스트)
    """
    text = hook_path.read_text(encoding="utf-8", errors="replace")
    resolved: List[Tuple[str, str, Path]] = []

    for line in text.splitlines():
        m = _SOURCE_LINE_RE.match(line)
        if not m:
            continue
        var = m.group(1)
        assign = re.search(r'^\s*%s="([^"]+)"\s*$' % re.escape(var), text, re.M)
        assert assign is not None, (
            f"{hook_path.name}: `source \"${{{var}}}\"` 는 있으나 {var}=\"...\" 대입을 찾지 못함 "
            f"— 편입 대상 해석 불가 (계수 정의역 누락 위험)"
        )
        raw_value = assign.group(1)
        # `${REPO_ROOT}/scripts/x.sh` → 마지막 `}` 뒤 tail 을 repo 루트 기준 상대경로로
        tail = raw_value.split("}")[-1].lstrip("/")
        resolved.append((var, raw_value, WORKTREE_ROOT / tail))

    return resolved


def collect_raw_sites(hook_name: str) -> List[ExecSite]:
    """훅 + source 편입 wrapper 의 raw exec site 전수 (Layer 1)."""
    hook_path = HOOKS_DIR / hook_name
    assert hook_path.is_file(), f"census 대상 훅 부재: {hook_path}"

    sites = _raw_sites_in_file(hook_path)
    for _var, raw_value, sourced in resolve_sourced_files(hook_path):
        assert sourced.is_file(), (
            f"{hook_name}: source 대상 {raw_value} → {sourced} 실재하지 않음 "
            f"(편입 정의역 파손)"
        )
        sites.extend(_raw_sites_in_file(sourced))
    return sites


# ============================================================ Layer 2: 명시 제외 적용

def _entry_matches(site: ExecSite, entry: Tuple[str, str, str, str]) -> bool:
    exc_file, exc_token, exc_substring, _reason = entry
    return (
        site.file_name == exc_file
        and site.token == exc_token
        and exc_substring in site.line_text
    )


def apply_exclusions(sites: List[ExecSite]) -> Tuple[List[ExecSite], List[ExecSite]]:
    """(kept, excluded) 로 분리. 표에 없는 site 는 전부 kept."""
    excluded = [s for s in sites if any(_entry_matches(s, e) for e in CONDITIONAL_EXCLUDED)]
    kept = [s for s in sites if s not in excluded]
    return kept, excluded


def count_exec_sites(hook_name: str) -> int:
    """count = raw − excluded (기동 계층 미포함)."""
    kept, _excluded = apply_exclusions(collect_raw_sites(hook_name))
    return len(kept)


def census(hook_name: str) -> int:
    """census(hook) = 2 (기동) + count_exec_sites."""
    return LAUNCH_LAYER + count_exec_sites(hook_name)


def collect_census() -> Dict[str, int]:
    return {name: census(name) for name in CHAIN_HOOKS}


# ============================================================ 테스트

def test_sourced_wrapper_integration():
    """source 로 편입되는 wrapper 가 실재하고, 그 exec site 가 정의역에 들어온다.

    ④a(`bash "${SCRIPT}"` fork 제거 → `source`) 로 wrapper 는 같은 셸에서 실행되므로
    wrapper 의 계보가 훅 자신의 계보다. 편입 누락 시 census 가 과소계상된다.
    """
    expected_sourcing = {
        "repo-confinement": "scripts/check-repo-confinement.sh",
        "worktree-location-guard": "scripts/check-worktree-location-guard.sh",
    }

    for hook_name, expected_tail in expected_sourcing.items():
        hook_path = HOOKS_DIR / hook_name
        text = hook_path.read_text(encoding="utf-8", errors="replace")

        # (1) source 라인 실재 assert — 편입 근거가 실물에 있어야 한다
        source_lines = [
            (i, ln) for i, ln in enumerate(text.splitlines(), 1)
            if _SOURCE_LINE_RE.match(ln)
        ]
        assert source_lines, (
            f"{hook_name}: `source \"${{SCRIPT}}\"` 라인 미발견 — wrapper 편입 근거 부재. "
            f"훅이 fork 방식(`bash \"${{SCRIPT}}\"`)으로 되돌아갔다면 편입 규칙 자체를 재검토해야 한다."
        )

        # (2) 해석 결과가 기대 wrapper 이고 실재
        resolved = resolve_sourced_files(hook_path)
        assert len(resolved) == 1, f"{hook_name}: source 대상 1개 기대, 실제 {len(resolved)}"
        _var, _raw, path = resolved[0]
        assert path.is_file(), f"{hook_name}: 해석된 source 대상 부재: {path}"
        assert path.as_posix().endswith(expected_tail), (
            f"{hook_name}: source 대상 불일치 — 기대 tail {expected_tail}, 실제 {path.as_posix()}"
        )

        # (3) wrapper site 가 실제로 편입됐는지 (파일명 기준 존재 확인)
        wrapper_sites = [s for s in collect_raw_sites(hook_name) if s.file_name == path.name]
        assert wrapper_sites, (
            f"{hook_name}: wrapper {path.name} 의 exec site 가 0 — 편입이 계수에 도달하지 않음"
        )


def test_conditional_exclusion_entries_each_match_exactly_one_site():
    """제외 표의 모든 항목이 실제 site 와 정확히 1:1 로 매칭 (미발견 = FAIL).

    이 assert 가 없으면 제외 항목이 코드 변화로 조용히 증발해도(=제외가 no-op 이 돼도)
    총합이 우연히 맞는 한 통과해버린다 — 제외 표가 감사 가능해지려면 각 항목이
    실물 site 를 정확히 하나 지목함을 강제해야 한다.
    """
    all_sites: List[ExecSite] = []
    for hook_name in CHAIN_HOOKS:
        all_sites.extend(collect_raw_sites(hook_name))

    for entry in CONDITIONAL_EXCLUDED:
        exc_file, exc_token, exc_substring, reason = entry
        hits = [s for s in all_sites if _entry_matches(s, entry)]
        assert len(hits) == 1, (
            f"제외 항목이 정확히 1개 site 와 매칭되지 않음: "
            f"file={exc_file} token={exc_token!r} substring={exc_substring!r} 사유={reason} "
            f"→ 매칭 {len(hits)}건 {[(h.file_name, h.line_no, h.text[:40]) for h in hits]}"
        )


def test_exclusion_table_has_no_unused_or_duplicate_entries():
    """제외 표에 중복 항목이 없고, 표 크기가 raw−kept 총합과 일치."""
    assert len(CONDITIONAL_EXCLUDED) == len(set(CONDITIONAL_EXCLUDED)), "제외 표 중복 항목 존재"

    total_raw = 0
    total_excluded = 0
    for hook_name in CHAIN_HOOKS:
        raw = collect_raw_sites(hook_name)
        _kept, excluded = apply_exclusions(raw)
        total_raw += len(raw)
        total_excluded += len(excluded)

    assert total_excluded == len(CONDITIONAL_EXCLUDED), (
        f"제외 적용 건수({total_excluded}) ≠ 표 항목 수({len(CONDITIONAL_EXCLUDED)}) "
        f"— 표 항목이 다중 매칭되거나 미적용됨"
    )
    assert total_raw - total_excluded == CANONICAL_TOTAL - LAUNCH_LAYER * len(CHAIN_HOOKS), (
        f"raw({total_raw}) − excluded({total_excluded}) 가 정본 exec site 합과 불일치"
    )


def test_census_per_hook_matches_canonical():
    """Assert ①: 훅별 census 가 ArchitectPL 정본 분해표와 일치 (7/5/4/5/4/4/4)."""
    actual = collect_census()
    assert actual == CANONICAL_CENSUS, (
        "per-hook census 불일치 (정본은 불변 — 파서/제외표를 고칠 것):\n"
        + "\n".join(
            f"  {name}: 정본 {CANONICAL_CENSUS[name]} vs 실측 {actual.get(name)}"
            for name in CHAIN_HOOKS
            if actual.get(name) != CANONICAL_CENSUS[name]
        )
    )


def test_census_total_ratchet():
    """Assert ②: 전체 census == 33 (ratchet).

        2×7 (기동 14) + exec sites 19 = 33
    """
    actual = collect_census()
    total = sum(actual.values())
    assert total == CANONICAL_TOTAL, (
        f"total census: 정본 {CANONICAL_TOTAL}, 실측 {total}. 분해: {actual}"
    )


def test_subshell_fork_count_non_increasing():
    """INV-S1: 프로세스 계보 비증가.

    S4/S10 경량화 이후 계보는 33 이 상한이다. 신규 exec site 가 유입되면
    (조건부 경로가 아닌 한) 이 assert 가 먼저 깨진다.
    """
    total = sum(collect_census().values())
    assert total <= CANONICAL_TOTAL, (
        f"프로세스 계보 ratchet 초과: {total} > {CANONICAL_TOTAL} (INV-S1 위반)"
    )


def test_discriminating_mutant_validation():
    """discriminating 실증: transient mutant 3종 → RED → revert → GREEN.

    계수기가 "새 exec 유입"을 실제로 판별하는지 3가지 도입 형태로 반증한다.
    (아래 관측은 실수행 기록 — 시각·위치·rc·출력 발췌)

    [실수행 기록 — 2026-08-14 09:59~10:00 KST, worktree cfp-2965-phase2 @ a88d1bdc3]
    각 mutant 는 transient (추가 → RED 실측 → 즉시 `git checkout --` revert → GREEN 재확인).
    revert 후 `git diff --stat HEAD -- hooks/ scripts/` = 본 테스트 파일 외 0 (실물 확인).

    ① 신규 top-level `$(dirname ...)` 유입
       위치: hooks/posttooluse-dev-process-capture:23 (DIR= 다음 줄)
             `MUTANT_A_DIR="$(dirname "$0")"`
       관측: pytest 5 failed / 3 passed. posttooluse-dev-process-capture 4→5, total 33→34.
             `AssertionError: total census: 정본 33, 실측 34`
       revert 후: rc=0, 8 passed.

    ② 기존 top-level 파이프라인 행에 sed 단 추가  ★ 균형 괄호 스캔의 load-bearing 실증
       위치: hooks/cross-repo-gh-safety:55 — `... | head -1)` → `... | head -1 | sed 's/MUTANTB//')`
       관측: pytest rc=1, 5 failed / 3 passed. cross-repo-gh-safety 7→8, total 33→34.
       ★ 같은 변조 행에 구 naive 정규식(`\\$\\([^)]*\\)`)을 적용하면 사이트 수가
         변조 전과 동일한 2 (sed 스크립트 안 `\\)` 에서 span 조기 절단 → 뒤 파이프 단 증발)
         = **mutant 생존**. 현 balanced 스캔은 5 로 관측 = **mutant 사살**.
         즉 이 계수기의 판별력은 균형 괄호 추출에 의존하며, 구 규칙에서는
         "총합이 우연히 정본과 일치하나 새 exec 을 못 잡는" 상태였다.
       revert 후: rc=0, 8 passed.

    ③ 변수 간접 호출 `"$PY" -c 'pass'` 행 추가
       위치: hooks/pretooluse-dev-process-capture:33 (실 호출 행 직전)
       관측: pytest rc=1, 5 failed / 3 passed. pretooluse-dev-process-capture 4→5, total 33→34.
       revert 후: rc=0, 8 passed.

    ④ (보조) 제외 표가 no-op 이 아님을 반증 — 표 항목의 포함-라인 substring 을
       `guard suppressed at %s` → `...%sZZZ` 로 변조하면 매칭이 0 이 되어
       test_conditional_exclusion_entries_each_match_exactly_one_site 가 먼저 FAIL (rc=1).
       원복 시 rc=0. 제외가 조용히 증발하면 통과하지 못한다.

    현 상태(모든 mutant revert 완료)에서는 정본 33 이어야 한다.
    """
    total = sum(collect_census().values())
    assert total == CANONICAL_TOTAL, (
        f"mutant 잔존 의심: total {total} ≠ {CANONICAL_TOTAL} — transient mutant 가 "
        f"revert 되지 않았거나 훅에 실변경이 유입됨"
    )


def test_census_limitations_declared():
    """한계 선언이 모듈 docstring 에 실재 (정직성 assert).

    수치만 남고 "무엇을 세지 않는지" 선언이 사라지면 census 가 절대 프로세스 수로
    오인용된다 — 선언 문자열의 실재를 테스트로 고정한다 (presence 고정이지
    참됨 증명 아님).
    """
    doc = __doc__ or ""
    required = [
        "정의역 밖",
        "미계수",
        "동적 전개",
        "실제 프로세스 총수",
        "presence ≠ truth",
    ]
    missing = [t for t in required if t not in doc]
    assert not missing, f"한계 선언 누락: {missing}"


# ============================================================ 보조 (수동 실행)

if __name__ == "__main__":
    census_map = collect_census()
    print("Chain Bash Hooks — 호출당 프로세스 계보 census")
    for name in CHAIN_HOOKS:
        raw = collect_raw_sites(name)
        kept, excluded = apply_exclusions(raw)
        print(f"  {name}: raw {len(raw)} − excl {len(excluded)} = {len(kept)} "
              f"+ {LAUNCH_LAYER} (기동) = {census_map[name]} "
              f"(정본 {CANONICAL_CENSUS[name]})")
        for s in excluded:
            print(f"      [EXCL] {s.file_name}:{s.line_no} {s.token}")
    print(f"  TOTAL = {sum(census_map.values())} (정본 {CANONICAL_TOTAL})")
