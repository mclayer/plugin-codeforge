#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# CFP-91 (CFP-84 follow-up) — Story file section schema lint
# CFP-478 / ADR-061 §결정 1 + Amendment 1 §결정 6.A — heredoc Python 외부 .py split
# MTD-1326 — PR 변경파일-only lint(three-dot merge-base 귀속) + baseline 동결·ratchet + 전량 raw 보존
#
# trap_priority: rel path POSIX normalization + mode_preserve (100755)
#
# Validates docs/stories/*.md against templates/story-page-structure.md schema:
# - Implementation Story (type: story OR no type field) = strict mode (§1-§11 의무, §12-§13 optional)
# - Epic Story (type: epic) = condensed mode allowed
#
# CLI 3-모드 (상호배타 — MTD-1326):
#   (무인자)             전량 raw lint — baseline 미적용 (workflow_dispatch·로컬, 현행 동작 보존)
#   --pr-base REF        PR 모드 — three-dot(merge-base) 변경파일 귀속 + baseline/ratchet
#   --write-baseline     전량 실측 → docs/stories/schema-baseline.txt 재생성 (AC-3)
#
# Usage / exit code / semantics 상세: scripts/check-story-section-schema.sh header.
import argparse
import re
import subprocess
import sys
from pathlib import Path

# Windows cp949 stdout encoding 차단 (CFP-1393 F8-FU / ADR-061 standardize)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# MTD-1326 root-anchoring — sh wrapper 의 무인자-cd semantics 비의존 (임의 cwd 직접 호출 안전).
# 모든 경로·git 호출을 repo root 에 고정한다.
REPO_ROOT = Path(__file__).resolve().parents[2]
STORIES_DIR = REPO_ROOT / "docs" / "stories"
BASELINE_REL = "docs/stories/schema-baseline.txt"
BASELINE_PATH = REPO_ROOT / "docs" / "stories" / "schema-baseline.txt"

# lint 대상 귀속 범위 = linter glob 과 동일(top-level *.md 비재귀) — 게이트-대상 일치 (§5.1 D4)
STORY_REL_PATTERN = re.compile(r"^docs/stories/[^/]+\.md$")

BASELINE_HEADER = (
    "# story-section-schema baseline — MTD-1326 (감소 단조 ratchet)\n"
    "# 신규 entry 추가 = CI RED (AC-7a) · 파일 전체 클린 시 entry 제거 권장 (AC-7b advisory)\n"
    "# 재생성(병합 직전 재실측 — AC-3): bash scripts/check-story-section-schema.sh --write-baseline\n"
)

# 강제 섹션 (Implementation Story strict, §12+§13 optional)
# CFP-2293 fix: heading 의 § 기호는 선택적(§?). story-init renderer
#   (workflow_story_init_render_story.py) 는 `## N.`(§ 없음) 헤딩을 생성하고 기존 consumer
#   story 전부 동일 형식이므로 linter 도 `## N.` / `## §N.` 양쪽을 수용한다 (renderer↔linter
#   컨벤션 정합). § anchor 뒤 [\.\s] 가 §1 vs §10/§11 prefix 충돌을 차단한다.
STRICT_REQUIRED = [
    ("§1", r"^##\s*§?1[\.\s]"),
    ("§2", r"^##\s*§?2[\.\s]"),
    ("§3", r"^##\s*§?3[\.\s]"),
    ("§4", r"^##\s*§?4[\.\s]"),
    ("§5", r"^##\s*§?5[\.\s]"),
    ("§6", r"^##\s*§?6[\.\s]"),
    ("§7", r"^##\s*§?7[\.\s]"),
    ("§8", r"^##\s*§?8[\.\s]"),
    ("§9", r"^##\s*§?9[\.\s]"),
    ("§10", r"^##\s*§?10[\.\s]"),
    ("§11", r"^##\s*§?11[\.\s]"),
]

# Epic condensed required (의무) + 결합/N/A 의무
EPIC_REQUIRED = [
    ("§1", r"^##\s*§?1[\.\s]"),
    ("§3", r"^##\s*§?3[\.\s]"),
    ("§7", r"^##\s*§?7[\.\s]"),
    ("§11", r"^##\s*§?11[\.\s]"),
    ("§12", r"^##\s*§?12[\.\s]"),
]
EPIC_NA_REQUIRED = ["§8", "§10"]  # N/A 명시 의무

# 결합 허용 patterns (Epic only) — 예: "5-6", "§5-6", "§5-§6" (§ 선택적, CFP-2293)
COMBINED_PATTERN = re.compile(r"^##\s*§?(\d+)\s*[-–]\s*§?(\d+)[\.\s]")

# N/A 시작 감지 (MTD-1592 F-CLR-1). "N/A" 로 시작하나 substantive 사유(\w) 부재 = bare N/A.
# 구분자 무관(— · - · ( · : · 공백 전부 허용) — 정상 N/A(`N/A — 사유`·`N/A (docs-only)`) 는 통과,
# bare("N/A" 단독·"N/A —" 사유0)만 포착. 실내용(N/A 미시작·표·산문) 은 검사 대상 아님.
_NA_START = re.compile(r"(?i)^n/a\b")


def _bare_na(line):
    s = line.strip()
    m = _NA_START.match(s)
    if not m:
        return False
    return not re.search(r"\w", s[m.end():])

# Frontmatter type field
TYPE_PATTERN = re.compile(r"^type:\s*(\S+)\s*$", re.MULTILINE)


def lint_story_file(f, rel):
    """단일 story 파일 lint — 규칙 로직 현행 무변경 (MTD-1326 순수 함수 추출).

    Returns (errors, warnings) — 각각 formatted 메시지 list. 빈 파일 = ([], [warning])
    (MTD-1592 F-CLR-2 — 종전 None 무소음 skip 제거). None 은 더 이상 반환하지 않음
    (caller `if res is None` 가드는 방어적 유지·현 도달불가).
    메시지 문자열·판정 순서는 종전 inline 루프와 동일 보존 (golden 비교 가능).
    """
    text = f.read_text(encoding="utf-8")
    if not text.strip():
        # MTD-1592 F-CLR-2: 빈 story 파일 = 명시 warning (종전 무소음 skip 제거).
        # error 아님 → exit 불변·checked 포함.
        return ([], [f"⚠️  {rel}: 빈 story 파일 (내용 없음)"])

    errors = []
    warnings = []

    # Frontmatter parse
    fm_match = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not fm_match:
        warnings.append(f"⚠️  {rel}: frontmatter 부재 — schema 추론 불가 (skip)")
        return errors, warnings
    fm = fm_match.group(1)
    type_match = TYPE_PATTERN.search(fm)
    story_type = type_match.group(1).strip() if type_match else "story"  # default = implementation

    # Heading scan
    headings = re.findall(r"^##\s.*$", text, re.MULTILINE)
    body = "\n".join(headings)

    # Combined section detection — Epic only allowed
    combined_sections = set()
    for line in headings:
        m = COMBINED_PATTERN.match(line)
        if m:
            a, b = int(m.group(1)), int(m.group(2))
            combined_sections.add(a)
            combined_sections.add(b)
            if story_type != "epic":
                errors.append(f"❌ {rel}: combined heading '{line.strip()}' = Implementation Story 에서 금지 (Epic Story `type: epic` 만 허용, CFP-84)")

    if story_type == "epic":
        # Epic condensed mode
        for sec, pat in EPIC_REQUIRED:
            sec_num = int(sec.replace("§", ""))
            if sec_num in combined_sections:
                continue  # combined heading covers it
            if not re.search(pat, body, re.MULTILINE):
                errors.append(f"❌ {rel}: Epic Story 의 §{sec_num} (mandatory) 누락 (CFP-84 Epic condensed mode)")

        # N/A 명시 의무 (§8, §10)
        for sec_str in EPIC_NA_REQUIRED:
            sec_num = int(sec_str.replace("§", ""))
            if sec_num in combined_sections:
                continue
            sec_pat = re.compile(rf"^##\s*§?{sec_num}[\.\s].*?(?=^##|\Z)", re.MULTILINE | re.DOTALL)
            sec_match = sec_pat.search(text)
            if not sec_match:
                errors.append(f"❌ {rel}: Epic Story 의 §{sec_num} N/A 명시 의무 (단순 omit 거부 — CFP-84 N/A 형식)")
            else:
                content_lines = [l for l in sec_match.group(0).split("\n")[1:] if l.strip()]
                if content_lines and _bare_na(content_lines[0]):
                    errors.append(f"❌ {rel}: Epic Story 의 §{sec_num} N/A 사유 누락 (bare 'N/A' — CFP-84 사유 명시 의무)")

    else:
        # Implementation Story strict mode
        for sec, pat in STRICT_REQUIRED:
            sec_num = int(sec.replace("§", ""))
            if not re.search(pat, body, re.MULTILINE):
                errors.append(f"❌ {rel}: Implementation Story 의 §{sec_num} 누락 (strict mode — CFP-84)")

    return errors, warnings


def iter_story_files():
    """linter glob — top-level docs/stories/*.md, .gitkeep 제외, sorted."""
    for f in sorted(STORIES_DIR.glob("*.md")):
        if f.name == ".gitkeep":
            continue
        yield f, f.relative_to(REPO_ROOT).as_posix()


def scan_stories():
    """전량 quiet scan — [(rel, errors, warnings)] (checked 파일만)."""
    results = []
    for f, rel in iter_story_files():
        res = lint_story_file(f, rel)
        if res is None:
            continue
        results.append((rel, res[0], res[1]))
    return results


def stories_dir_missing():
    if not STORIES_DIR.exists():
        print("ℹ️  docs/stories/ 부재 — lint skip (plugin repo or pre-init consumer)")
        return True
    return False


def print_summary(checked, errors, warnings):
    print(f"\nChecked {checked} story file(s) — errors: {errors}, warnings: {warnings}")


def _git(*args):
    """git 호출 — repo root 고정(-C). 실패는 returncode 로 관측 (degraded 판정 입력)."""
    try:
        return subprocess.run(
            ["git", "-C", str(REPO_ROOT)] + list(args),
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
    except OSError as e:
        cp = subprocess.CompletedProcess(args, 127)
        cp.stdout = ""
        cp.stderr = str(e)
        return cp


def parse_baseline(text):
    """baseline 파싱 (§3.3) — (entries set, warn 메시지 list).

    '#' 시작·공백 행 무시 · 유효 entry = docs/stories/ top-level .md 상대경로
    (그 외 = ::warning + 무시) · 중복 = dedupe + ::warning.
    """
    entries = set()
    warns = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if not STORY_REL_PATTERN.match(line):
            warns.append(f"::warning::baseline 비정형 행 무시 — {line}")
            continue
        if line in entries:
            warns.append(f"::warning::baseline 중복 entry — {line}")
            continue
        entries.add(line)
    return entries, warns


def load_head_baseline():
    """HEAD(working tree) 판 baseline 로드 — (entries, printed-warning count)."""
    if not BASELINE_PATH.exists():
        print(f"ℹ️  baseline 부재 — 빈 집합으로 진행 ({BASELINE_REL})")
        return set(), 0
    entries, warns = parse_baseline(BASELINE_PATH.read_text(encoding="utf-8"))
    for w in warns:
        print(w)
    return entries, len(warns)


def mode_raw():
    """무인자 = 전량 raw — 현행 동작·출력 보존 (AC-5). baseline 로직 일절 미적용."""
    if stories_dir_missing():
        return 0
    checked = 0
    errors = 0
    warnings = 0
    for f, rel in iter_story_files():
        res = lint_story_file(f, rel)
        if res is None:
            continue
        checked += 1
        errs, warns = res
        for m in errs:
            print(m)
        for m in warns:
            print(m)
        errors += len(errs)
        warnings += len(warns)
    print_summary(checked, errors, warnings)
    return 1 if errors > 0 else 0


def mode_write_baseline():
    """전량 실측 → baseline 재생성 (AC-3 — 병합 직전 재실측의 유일 권위 도구). 멱등."""
    if stories_dir_missing():
        return 0
    results = scan_stories()
    violating = sorted(rel for rel, errs, _w in results if errs)
    total = sum(len(errs) for _rel, errs, _w in results)
    content = BASELINE_HEADER + "".join(e + "\n" for e in violating)
    with open(BASELINE_PATH, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(content)
    print(f"ℹ️  baseline 재생성 — {len(violating)} 파일 / {total} 건 → {BASELINE_REL}")
    return 0


def mode_degraded(reason):
    """degraded fallback (§5.1) — 귀속 판정 불가 시: loud ::warning 후 전량+baseline.

    baseline 등재 파일의 위반 = exit 제외(suppressed 건수 ℹ️) · 비-baseline 위반 = RED.
    한계(정직 기록): degraded 중 AC-4(touched 강제)·AC-7a(ratchet) 판정 불가 — 희귀 경로.
    """
    print(f"::warning::PR diff 귀속 실패({reason}) — degraded 전량+baseline 모드")
    warnings_count = 1
    head_entries, w = load_head_baseline()
    warnings_count += w
    results = scan_stories()
    checked = 0
    errors = 0
    suppressed = 0
    residual_files = 0
    residual_viols = 0
    for rel, errs, warns in results:
        checked += 1
        for m in warns:
            print(m)
        warnings_count += len(warns)
        if rel in head_entries:
            if errs:
                suppressed += len(errs)
                residual_files += 1
                residual_viols += len(errs)
        else:
            for m in errs:
                print(m)
            errors += len(errs)
    if suppressed:
        print(f"ℹ️  degraded — baseline 등재 위반 {suppressed}건 exit 제외 (suppressed)")
    print(f"ℹ️  baseline 잔존: {residual_files} 파일 / {residual_viols} 건 (entry {len(head_entries)}건)")
    print_summary(checked, errors, warnings_count)
    return 1 if errors > 0 else 0


def mode_pr(base_ref):
    """PR 모드 (§3.2) — three-dot(merge-base) 귀속 + baseline/ratchet. 단일 전량-quiet-scan 후 분류."""
    if stories_dir_missing():
        return 0

    # step 1 — merge-base (실패 = degraded §5.1)
    mb = _git("merge-base", base_ref, "HEAD")
    if mb.returncode != 0 or not mb.stdout.strip():
        return mode_degraded(f"merge-base 실패: {base_ref}")
    merge_base = mb.stdout.strip()

    # step 2 — three-dot diff 귀속 (AC-8): A/M=target · R=신경로만 · D=미린트
    diff = _git("diff", "--name-status", "-M", f"{base_ref}...HEAD")
    if diff.returncode != 0:
        return mode_degraded(f"three-dot diff 실패: {base_ref}")
    targets = set()
    baseline_in_diff = False
    for line in diff.stdout.splitlines():
        if not line.strip():
            continue
        parts = line.split("\t")
        status = parts[0]
        if status.startswith("R") and len(parts) >= 3:
            old_path, path = parts[1], parts[2]  # rename = 신경로만 target (AC-8)
            if old_path == BASELINE_REL:
                baseline_in_diff = True
        elif len(parts) >= 2:
            path = parts[1]
        else:
            continue
        if path == BASELINE_REL:
            baseline_in_diff = True
        if status.startswith("D"):
            continue  # 삭제 파일 미린트 (AC-8 — 부재 파일 크래시 방지)
        if STORY_REL_PATTERN.match(path):
            targets.add(path)

    errors = 0
    warnings_count = 0

    # step 3 — baseline 로드: HEAD 판 + merge-base 판(git show) + 경로 이력 검사 [FIX-2]
    head_entries, w = load_head_baseline()
    warnings_count += w
    bootstrap = False
    base_entries = set()
    show = _git("show", f"{merge_base}:{BASELINE_REL}")
    if show.returncode == 0:
        base_entries, _base_warns = parse_baseline(show.stdout)
    else:
        # merge-base 판 부재 — 경로 이력 검사: 이력 실재 = 과거 도입-후-삭제 → base ∅ (bootstrap 불인정)
        lg = _git("log", "-n", "1", "--format=%H", merge_base, "--", BASELINE_REL)
        if lg.returncode != 0:
            return mode_degraded("baseline 경로 이력 검사 실패")
        if not lg.stdout.strip():
            bootstrap = True  # 진짜 최초 도입 — 리포 이력상 1회 소진 (AC-7a bootstrap)

    # step 4 — ratchet (AC-7a): baseline 파일이 diff 에 포함된 경우
    if baseline_in_diff:
        if bootstrap:
            print("ℹ️  baseline bootstrap — 최초 도입 인정 (merge-base 판 부재 + 경로 이력 0건, 리포 이력상 1회)")
        else:
            for e in sorted(head_entries - base_entries):
                print(f"❌ {BASELINE_REL}: baseline 신규 entry 금지 (ratchet — AC-7a) — {e}")
                errors += 1

    # step 5 — 전 파일 quiet 1-pass 후 분류
    results = scan_stories()
    by_rel = {rel: (errs, warns) for rel, errs, warns in results}
    checked = 0
    for rel, errs, warns in results:
        if rel in targets:
            # target 위반 → RED (baseline 등재 무관 — AC-2 신규 + AC-4 touched=파일 전체 클린 단일 규칙)
            checked += 1
            for m in errs:
                print(m)
            for m in warns:
                print(m)
            errors += len(errs)
            warnings_count += len(warns)

    # baseline entry 잔존 실측 + stale advisory (AC-7b)
    residual_files = 0
    residual_viols = 0
    for e in sorted(head_entries):
        if e in by_rel and by_rel[e][0]:
            residual_files += 1
            residual_viols += len(by_rel[e][0])
        else:
            print(f"::warning::baseline stale entry — {e} 클린/부재 — 제거 권장 (AC-7b)")
            warnings_count += 1

    # 비-target·비-baseline 위반 (과거 누수분) — fail-loud 누수 감시 advisory (§2.4, exit 무영향)
    leak = sum(len(errs) for rel, errs, _w in results
               if rel not in targets and rel not in head_entries and errs)
    if leak:
        print(f"::warning::비-baseline 미변경 위반 {leak}건 — 누수 감시 advisory (exit 무영향)")
        warnings_count += 1

    # step 6 — AC-6 fail-loud: 매 PR-모드 런 무조건 실측 출력
    print(f"ℹ️  baseline 잔존: {residual_files} 파일 / {residual_viols} 건 (entry {len(head_entries)}건)")

    # step 7 — summary + exit
    print_summary(checked, errors, warnings_count)
    return 1 if errors > 0 else 0


def _nonempty_ref(s):
    # MTD-1592 F-CLR-3: --pr-base 빈/공백 REF 명시 거부 (종전 falsy fallthrough → 조용한 mode_raw 차단).
    if not s.strip():
        raise argparse.ArgumentTypeError("--pr-base REF 는 비어있을 수 없음")
    return s


def main():
    parser = argparse.ArgumentParser(
        description="Story file section schema lint (CFP-91 / MTD-1326)")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--pr-base", metavar="REF", type=_nonempty_ref,
                       help="PR 모드 — three-dot(merge-base) 변경파일 귀속 + baseline ratchet")
    group.add_argument("--write-baseline", action="store_true",
                       help="전량 실측 → docs/stories/schema-baseline.txt 재생성 (AC-3)")
    args = parser.parse_args()
    if args.write_baseline:
        return mode_write_baseline()
    if args.pr_base:
        return mode_pr(args.pr_base)
    return mode_raw()


if __name__ == "__main__":
    sys.exit(main())
