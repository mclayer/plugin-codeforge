#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
scripts/lib/check_whitelist_manifest_3way.py
CFP-2412 / ADR-130 §결정 3/5 (Epic CFP-2394 Story D) — whitelist↔manifest↔
templates/github-workflows 3-way 일관성 게이트 Python SSOT lint engine (warning tier)

consumer-applicability whitelist(templates/scripts/consumer_applicable_workflows.txt 28) ↔
배포 source(templates/github-workflows/<name>.{yml,yaml}) ↔ closure manifest
(templates/consumer-scripts.manifest 49) 의 삼각 일관성(triangle invariant) 검증.

기존 두 게이트는 삼각형의 한 변(check-consumer-scripts-manifest.sh = manifest entry 내부 정합)·
한 점(mirror-dependency-closure.py = closure depth-1)만 강제 — 3-way cross-table 표면은 어디서도
강제되지 않았다. 본 게이트(D)가 그 cross-table 을 채운다.

3 변(방향) + depth-2 하위 (change-plan §3.1 SSOT):
  방향1 (전수 — applicability → 배포 source 실존):
    whitelist 28 각 <name> → templates/github-workflows/<name>.{yml,yaml} 실존, miss=FAIL(real-dead).
    .github/workflows/<name> 부재는 무관 (consumer-only 정상 분기, silent-harm 차단). AC-1/2/3/4.
    양 확장자 glob 필수 (.yml + .yaml). case-exact (Linux CI case-sensitive). AC-1.
  방향2 (manifest→whitelist 부분집합·방향성 — closure → applicability 함의):
    manifest 의 :dep_workflow 부착 entry → 그 workflow basename 이 whitelist membership 또는
    plugin-only(template 실존) 분류 정합. dep_workflow 미부착 entry(script-only/shared/data) 를
    bijection 매핑하면 phantom FAIL — 방향성 함의만, 역방향 강제 금지. AC-5/7.
  방향3 (whitelist→manifest coverage — applicability → closure 등재완전성) ★ 진짜 3-way 완성 변:
    whitelist 28 각 workflow 의 hard-block closure 자산 = (a) yml run: 블록이 직접 호출하는 1-hop
    dep script(scripts/check-*.sh / templates/scripts/*.py — AM-3 패턴) 이 manifest 에 등재됐나
    전수 검사. 미등재=FAIL. AC-6 / UC-3. mirror-dependency-closure.py AM-3 동형 run:-block-aware
    추출 (on.paths 필터 안 dep 토큰은 closure 가 아니므로 false-FAIL 회피 — run: 블록만).
  depth-2 등재완전성 (hard-exit 데이터 dep — 방향3 의 depth-2 하위 강제):
    hard-exit 데이터 dep(yml→.sh→.tsv) 의 script·data 모두 manifest 등재 검사. AC-8/9.
    확정 chain: bootstrap-labels.yml → bash scripts/bootstrap-labels.sh → base-labels.tsv hard-exit
    (bootstrap-labels.sh:88-90 `if [ ! -f "$BASE_LABELS_TSV" ]; then ... exit 1`). .tsv 비패턴 →
    mirror closure(AM-2 depth-1 + 2패턴 .sh/.py)만이라 구조적 미포착 → D 가 보강.

graceful-degradation (change-plan §3.5 — ADR-130 §결정4/L102 정합):
  data-absence(A) = fail-open(exit 0, honest 분류 동반):
    whitelist txt / manifest / templates dir 자체 부재 = 검증할 3-way 가 애초에 성립 안 함 =
    검증 비대상(일관성 위반 아님) → honest 로그 + no-op EXIT 0.
    "그냥 부재면 통과" silent default 아님 — 각 부재 케이스가 왜 검증 비대상인지 명시 로그.
    path-filter/`on.paths` skip 금지(required check Pending trap 차단, §결정4) — 스크립트가
    내부에서 data-absence 를 EXIT 0 처리 (워크플로 `if:` skip 아님).
  setup-error(B) = fail-closed(exit 2):
    python3 미설치(thin wrapper 처리) / read 권한 거부 / 입력 인자 형식 오류 = 검증 로직이 못 돎 =
    결과 불명 → 환경 오류 정직 노출 EXIT 2.

offline-first (gh 불요 — 3 소스 전부 repo 내 파일). ReDoS-safe (anchored bounded quantifier, nested 0).
A/B/C read-only (verifier — manifest/whitelist/templates 에 데이터 write 0).

Usage:
  python3 check_whitelist_manifest_3way.py [--root <repo-root>]
    → repo-root 의 3 소스 scan, 위반 1+ 면 exit 1 (warning), 0 면 exit 0,
      data-absence 면 exit 0 (honest no-op), setup-error 면 exit 2.
    --root 미지정 시: __file__ 기준 2-level up (scripts/lib/ -> scripts/ -> repo root).

Exit codes (ADR-060 §결정 5 3-tier — warning tier):
  0 = PASS (violation 0) OR data-absence honest no-op
  1 = violation 1+ (warning emit — workflow continue-on-error 로 비차단, advisory only)
  2 = SETUP error (입력 인자 형식 오류 / read 권한 거부)

ADR refs: ADR-130 §결정 3/4/5/5-A/6/9 (carrier) / ADR-083 §결정 5 (8 invariant 계승) /
  ADR-060 §결정 5/6 (warning-tier evidence framework) / ADR-061 §결정 1 (Python SSOT + thin wrapper) /
  CFP-898 mirror-dependency-closure.py AM-1~4 (run:-block AM-3 extraction 동형 재사용)
"""

import argparse
import re
import sys
from pathlib import Path

# Windows cp949 인코딩 문제 회피: stdout/stderr 를 UTF-8 강제 (ADR-061 portability)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


# ─────────────── 3 소스 상대경로 (repo-root 기준) ──────────────────────────────────────────
WHITELIST_REL = "templates/scripts/consumer_applicable_workflows.txt"
MANIFEST_REL = "templates/consumer-scripts.manifest"
TEMPLATES_DIR_REL = "templates/github-workflows"

# ─────────────── AM-3 closure-asset dependency patterns (mirror-dependency-closure.py 동형) ──
# 1-hop dep script 자산만 (방향3 closure-asset). bounded quantifier — nested 절대 금지 (ReDoS-safe).
_DEP_PATTERNS = [
    re.compile(r"\bscripts/check-[a-z0-9-]+\.sh\b"),
    re.compile(r"\btemplates/scripts/[a-z0-9-]+\.py\b"),
]

# YAML comment line (선두 whitespace 후 #) — dep 추출 제외 (mirror closure.py _YAML_COMMENT_LINE 동형)
_YAML_COMMENT_LINE = re.compile(r"^\s*#")

# depth-2 hard-exit 데이터 dep chain (change-plan §3.1 확정 chain).
# (workflow_basename, invoking_script_rel, hard_exit_data_rel) — script·data 모두 manifest 등재 검사.
# bootstrap-labels.sh:88-90 hard-exit on base-labels.tsv (.tsv 비패턴 → mirror closure 미포착).
_DEPTH2_HARD_EXIT_CHAINS = [
    (
        "bootstrap-labels.yml",
        "scripts/bootstrap-labels.sh",
        "templates/labels/base-labels.tsv",
    ),
]


# ─────────────── 입력 파싱 (line-by-line, comment/blank skip) ──────────────────────────────

def _parse_whitelist(text):
    """whitelist txt → workflow basename(확장자 포함) list. 주석/빈줄 skip (F7 정합)."""
    names = []
    for raw in text.splitlines():
        s = raw.strip()
        if not s or s.startswith("#"):
            continue
        names.append(s)
    return names


def _parse_manifest(text):
    """
    manifest → (script_path, dep_workflow_or_None) list. 주석/빈줄 skip.
    format: <script-path>[:<dependent-workflow-path>] (≤1 colon, check-consumer-scripts-manifest.sh 정합).
    """
    entries = []
    for raw in text.splitlines():
        s = raw.strip()
        if not s or s.startswith("#"):
            continue
        if ":" in s:
            script_path, dep_workflow = s.split(":", 1)
            dep_workflow = dep_workflow if dep_workflow else None
        else:
            script_path, dep_workflow = s, None
        entries.append((script_path, dep_workflow))
    return entries


def _extract_run_block_deps(yml_path):
    """
    yml 의 run: 블록 안 1-hop dep script 자산 추출 (AM-3 run:-block-aware, mirror closure.py 동형).

    on.pull_request.paths 필터 / 주석 안 dep 토큰은 closure 가 아니므로 제외 (run: 블록만 scan).
    AM-1 regex_primary (PyYAML 무의존) + AM-2 transitive_depth_limit=1.
    """
    try:
        text = yml_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []  # caller 가 setup-error vs data-absence 판단 — 여기선 빈 list

    deps = []
    in_run_block = False
    run_indent = None

    for line in text.splitlines():
        stripped = line.rstrip()

        # 순수 YAML 주석 줄 skip (AM-1 regex_primary filter)
        if _YAML_COMMENT_LINE.match(stripped):
            continue

        # run: key 감지 (scalar 또는 block scalar). `- run:` list item 도 지원.
        run_match = re.match(r"^(\s+(?:-\s+)?)run:\s*", stripped)
        if run_match is None:
            run_match = re.match(r"^((?:-\s+)?)run:\s*", stripped)

        if run_match:
            in_run_block = True
            prefix = run_match.group(1)
            run_indent = len(re.match(r"^\s*", prefix).group(0))
            inline_val = stripped[run_match.end():]
            if inline_val and not inline_val.lstrip().startswith("|"):
                for pat in _DEP_PATTERNS:
                    for m in pat.finditer(inline_val):
                        deps.append(m.group(0))
            continue

        if in_run_block:
            if not stripped:
                continue  # block scalar 안 빈줄 허용
            line_indent = len(stripped) - len(stripped.lstrip())
            if stripped.lstrip().startswith("|"):
                continue  # block scalar indicator 줄
            if run_indent is not None and line_indent > run_indent:
                for pat in _DEP_PATTERNS:
                    for m in pat.finditer(stripped):
                        deps.append(m.group(0))
            else:
                in_run_block = False
                run_indent = None

    return list(dict.fromkeys(deps))  # dedup, 순서 보존


def _list_templates(templates_dir):
    """templates_dir 의 실제 파일명 set (case-exact). 1회 listdir 후 caching 용 — 호출처가 set 보유."""
    try:
        return {p.name for p in templates_dir.iterdir() if p.is_file()}
    except OSError:
        return set()


def _resolve_template(template_names, base):
    """base name(확장자 stripped) → <base>.{yml,yaml} case-exact 실존 여부 → 파일명 또는 None.

    case-exact 매칭 (Linux CI case-sensitive — F9). Path.is_file() 은 Windows/macOS 에서
    case-insensitive 라 cross-platform 결정성 미보장 → 실제 디렉터리 파일명 set 과 exact 비교.
    template_names = _list_templates(templates_dir) 결과 (case-exact 파일명 set).
    """
    for ext in (".yml", ".yaml"):
        cand = base + ext
        if cand in template_names:
            return cand
    return None


def _strip_ext(name):
    if name.endswith(".yml"):
        return name[:-4]
    if name.endswith(".yaml"):
        return name[:-5]
    return name


# ─────────────── 3-way 검증 (방향1/2/3 + depth-2) ──────────────────────────────────────────

def check_3way(root):
    """
    root(repo root Path) 의 3 소스 3-way 일관성 검증.

    Returns: (exit_code, messages[])
      exit_code: 0=PASS or data-absence no-op / 1=violation / 2=setup-error
    """
    whitelist_path = root / WHITELIST_REL
    manifest_path = root / MANIFEST_REL
    templates_dir = root / TEMPLATES_DIR_REL

    # ── data-absence(A) = fail-open EXIT 0 (honest 분류, 각 부재 사유 명시) ──
    # silent default 아님 — "왜 검증 비대상인지" 명시 로그 후 no-op (path-filter skip 금지, §결정4).
    if not whitelist_path.is_file():
        return 0, [
            "::notice::check-whitelist-manifest-3way: data-absence — whitelist 부재 "
            "(%s). 검증할 3-way 가 성립 안 함(applicability SSOT 부재) = 검증 비대상. "
            "honest no-op EXIT 0 (silent default 아님 — path-filter skip 금지, ADR-130 §결정4)."
            % WHITELIST_REL
        ]
    if not manifest_path.is_file():
        return 0, [
            "::notice::check-whitelist-manifest-3way: data-absence — manifest 부재 "
            "(%s). 검증할 closure SSOT 부재 = 검증 비대상. honest no-op EXIT 0."
            % MANIFEST_REL
        ]
    if not templates_dir.is_dir():
        return 0, [
            "::notice::check-whitelist-manifest-3way: data-absence — templates dir 부재 "
            "(%s). 배포 source 채널 부재 = 검증 비대상. honest no-op EXIT 0."
            % TEMPLATES_DIR_REL
        ]

    # ── 3 소스 read (read 권한 거부 등 = setup-error B = EXIT 2) ──
    try:
        whitelist_text = whitelist_path.read_text(encoding="utf-8", errors="replace")
        manifest_text = manifest_path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return 2, [
            "::error::check-whitelist-manifest-3way: setup-error — 3 소스 read 실패: %s "
            "(검증 로직 실행 불가 = 결과 불명, fail-closed EXIT 2)." % exc
        ]

    whitelist = _parse_whitelist(whitelist_text)
    manifest_entries = _parse_manifest(manifest_text)

    # case-exact 파일명 set (방향1/2/3 매칭 — Linux CI case-sensitive 결정성, F9)
    template_names = _list_templates(templates_dir)
    # manifest 등재 script-path set (방향3·depth-2 coverage 검사용)
    registered_scripts = {sp for sp, _dep in manifest_entries}
    # whitelist basename set (방향2 membership 검사용)
    whitelist_set = set(whitelist)

    messages = []
    violations = 0

    # ── 방향1: whitelist → templates/github-workflows 실존 (전수, miss=FAIL) ──
    for name in whitelist:
        base = _strip_ext(name)
        tpl = _resolve_template(template_names, base)
        if tpl is None:
            violations += 1
            messages.append(
                "::warning::check-whitelist-manifest-3way: FAIL dir=1 (real-dead) — "
                "whitelist '%s' → templates/github-workflows/%s.{yml,yaml} 부재. "
                "applicability whitelist 항목의 배포 source 부재 = consumer mirror 시 phantom. "
                "hint: templates 채널에 workflow 추가 또는 whitelist 에서 제거." % (name, base)
            )

    # ── 방향2: manifest dep_workflow → whitelist membership 또는 plugin-only(template 실존) ──
    for script_path, dep_workflow in manifest_entries:
        if not dep_workflow:
            continue  # dep_workflow 미부착 entry = 방향성 함의 비대상 (bijection 역강제 금지 — phantom 차단)
        dep_base_name = Path(dep_workflow).name  # templates/github-workflows/foo.yml → foo.yml
        in_whitelist = dep_base_name in whitelist_set
        tpl = _resolve_template(template_names, _strip_ext(dep_base_name))
        plugin_only = (not in_whitelist) and (tpl is not None)
        if not in_whitelist and not plugin_only:
            violations += 1
            messages.append(
                "::warning::check-whitelist-manifest-3way: FAIL dir=2 (phantom dep) — "
                "manifest entry '%s' 의 dep_workflow '%s' 가 whitelist membership 도 "
                "plugin-only(template 실존) 도 아님. closure→applicability 함의 위반. "
                "hint: dep_workflow 의 template 실존 확인 또는 whitelist 등재." % (script_path, dep_workflow)
            )

    # ── 방향3: whitelist workflow 의 1-hop closure 자산(run: 블록 dep) manifest 등재 (전수) ──
    for name in whitelist:
        base = _strip_ext(name)
        tpl_name = _resolve_template(template_names, base)
        if tpl_name is None:
            continue  # 방향1 이 이미 FAIL 처리 — 중복 카운트 회피
        deps = _extract_run_block_deps(templates_dir / tpl_name)
        for dep in deps:
            if dep not in registered_scripts:
                violations += 1
                messages.append(
                    "::warning::check-whitelist-manifest-3way: FAIL dir=3 (closure-asset unregistered) — "
                    "whitelist workflow '%s' 의 hard-block closure 자산 '%s' (run: 블록 1-hop dep) 가 "
                    "manifest 미등재. consumer degraded-mode 에서 runtime hard-exit silent-harm. "
                    "hint: manifest 에 `%s` 를 등재하라 (Bazel strict-deps 동형)." % (name, dep, dep)
                )

    # ── depth-2: hard-exit 데이터 chain (script·data 모두 manifest 등재) ──
    for wf_base, invoking_script, hard_exit_data in _DEPTH2_HARD_EXIT_CHAINS:
        # 본 chain 의 workflow 가 whitelist 에 있을 때만 강제 (consumer-applicable 한정)
        if wf_base not in whitelist_set:
            continue
        for asset in (invoking_script, hard_exit_data):
            if asset not in registered_scripts:
                violations += 1
                messages.append(
                    "::warning::check-whitelist-manifest-3way: FAIL depth=2 (hard-exit data unregistered) — "
                    "whitelist workflow '%s' 의 hard-exit chain 자산 '%s' 가 manifest 미등재. "
                    "yml→.sh→데이터 hard-exit dep (mirror closure depth-1 구조적 미포착). "
                    "hint: manifest 에 `%s` 를 등재하라 (declare-or-forbid)." % (wf_base, asset, asset)
                )

    if violations:
        messages.append("")
        messages.append(_ACTION_GUIDE)
        messages.append("")
        messages.append(
            "check-whitelist-manifest-3way: FAIL %d "
            "(warning tier — continue-on-error 로 비차단, advisory only)" % violations
        )
        return 1, messages

    messages.append(
        "check-whitelist-manifest-3way: PASS — 3-way 일관성 OK "
        "(방향1 whitelist→templates / 방향2 manifest→whitelist / 방향3 whitelist→manifest closure "
        "/ depth-2 hard-exit 데이터 전수 PASS, warning tier)"
    )
    return 0, messages


_ACTION_GUIDE = (
    "[whitelist-manifest-3way] 강제 action 2택 (warning mode — merge 비차단, advisory):\n"
    "  ① FAIL 항목별 hint 에 따라 3 소스(whitelist / templates/github-workflows / manifest) 정합 복원:\n"
    "     - 방향1: templates 채널에 workflow 추가 또는 whitelist 에서 제거\n"
    "     - 방향2: dep_workflow 의 template 실존 확인 또는 whitelist 등재\n"
    "     - 방향3/depth-2: manifest 에 누락 closure 자산 등재 (declare-or-forbid)\n"
    "  ② hotfix-bypass:whitelist-manifest-3way label + audit comment\n"
    "     (check-bypass-audit-comment.sh 마커 패턴)\n"
    "근거: ADR-130 §결정 3/5 (CFP-2412, Epic CFP-2394 Story D) — whitelist↔manifest↔templates "
    "3-way 일관성 게이트. 기존 check-consumer-scripts-manifest.sh(entry 내부 lint) + "
    "mirror-dependency-closure.py(closure depth-1) 와 책임축 disjoint (D=cross-table 3-way)."
)


# ─────────────── main ──────────────────────────────────────────────────────────────────────

def _discover_root():
    # __file__ = <repo_root>/scripts/lib/check_whitelist_manifest_3way.py
    return Path(__file__).resolve().parent.parent.parent


def main(argv):
    parser = argparse.ArgumentParser(
        description="whitelist↔manifest↔templates 3-way 일관성 게이트 (CFP-2412 / ADR-130)",
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
            "::error::check-whitelist-manifest-3way: setup-error — repo root not a dir: %s "
            "(fail-closed EXIT 2)." % root,
            file=sys.stderr,
        )
        return 2

    exit_code, messages = check_3way(root)
    for msg in messages:
        print(msg)
    return exit_code


if __name__ == "__main__":
    sys.exit(main(sys.argv))
