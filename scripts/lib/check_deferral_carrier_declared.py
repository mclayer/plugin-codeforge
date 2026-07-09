#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
scripts/lib/check_deferral_carrier_declared.py
CFP-2591 Phase 2 / ADR-060 §결정 6 — deferral carrier declared (no-TBD) lint (warning tier)

deferred-followup 을 남길 때 carrier 를 미해결 placeholder (`deferred_followup_cfp: TBD` /
`CFP-TBD` / unwired `FU-N-N` 마커) 로 남기면 forcing function 이 걸릴 대상 자체가 사라진다
(silent debt). 본 lint 가 governance surface 전반에서 그 placeholder 를 grep-기반 mechanical
검출 + baseline new-only grandfather subtract (Clean-as-You-Code).

(a) registry FLAG 는 sibling gate check_deferred_followup_reconcile.py 소관. 본 (b) lint 는
비-registry declaration surface (문서/워크플로/스킬 안 placeholder carrier) 소관 — 두 축 disjoint.

named-carrier level-1 handoff (§7.3.1 D5): `deferred_followup_cfp: CFP-<n>` (실 CFP 번호) 는
그 번호가 registry 텍스트에 carrier/sibling 로 등장하는지 read-only membership 검사만 한다
(wiring 완결 검증은 (a) 위임 — membership 에서 정지). 미등장 → FLAG (registration_absent).

honest forcing ceiling: 본 lint 는 hard block 을 주장하지 않는다 — exit 1 = advisory 표식,
실 차단은 워크플로 continue-on-error 소관 (admin 우회 가능, NEW count 로 관측만).

Usage:
  python3 check_deferral_carrier_declared.py check [--repo-root <path>] [--paths <glob> ...]
                                                   [--baseline <path>]
    → in-scope 경로 전수 scan, NEW 1+ 면 exit 1 (warning), NEW 0 면 exit 0

Exit codes (ADR-060 §결정 15 3-tier — warning tier):
  0 = PASS (NEW 0)
  1 = NEW 1+ (`::warning::check-deferral-carrier-declared: FLAG ...` emit — continue-on-error 로 비차단)
  2 = SETUP error (검사 경로 부재 / --baseline 명시인데 missing·malformed / 파일 read 실패)

검출 1급 firing 조건:
  flag(line) := detect_token_match(line) AND NOT allowlist_match(line)
  grandfather (--baseline 제공+존재): (relpath, token) 이 baseline declaration_surfaces 에
    (동일 relpath + token substring 매치) 하면 subtract.

ReDoS-safe (ADR-061 Amd3 CodeQL guard):
  - line-by-line scan (multi-line backtracking regex 0).
  - anchored bounded-quantifier regex. counterfactual 축의 sequential `.*` 2연속
    (quadratic backtracking) 은 bounded `.{0,200}` + allowlist_match 진입 전 line-length
    cap (len(line) > _COUNTERFACTUAL_MAX_LINE → 축 skip) 으로 상수/선형 시간 강제
    (CFP-2591 Phase 2 — before: 64KB 6.3s quadratic / after: 1MB <1ms 상수).

Prior art (worktree 실존 확인 — ADR-119):
  scripts/lib/check_lane_count_ssot.py  (line-by-line scan + git ls-files walk + 5축 allowlist +
    SELF_EXCLUDE + ReDoS-safe + exit 3-tier — verbatim copy-inherit, allowlist content 만 재작성)
  scripts/lib/check_deferred_followup_reconcile.py  (carrier-resolution triplet + baseline loader/digest)

ADR refs: ADR-060 §결정 6 / ADR-061 / ADR-127
"""

import argparse
import os
import re
import subprocess
import sys

# carrier-resolution / baseline loader triplet 재사용 (동일 scripts/lib/ 디렉토리, __name__ guard
# 안전 — 신규 shared lib 추출 금지, consumer 2개 = YAGNI). import 실패해도 (b) lint 자체 동작 무관.
try:
    from check_deferred_followup_reconcile import load_baseline  # noqa: F401
except ImportError:
    load_baseline = None

# Windows cp949 인코딩 문제 회피: stdout/stderr 를 UTF-8 강제 (ADR-061 portability)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


# ─────────────────────── 검사 / 제외 경로 (lane-count 답습) ──────────────────────

# 검사 대상 경로 glob (git ls-files 인자). docs/·CLAUDE.md·plugins/·scripts/·templates/·plugin.json.
DEFAULT_SCAN_GLOBS = [
    "docs",
    "CLAUDE.md",
    "plugins",
    "scripts",
    "templates",
    ".claude-plugin/plugin.json",
]

# 제외 경로 prefix — ADR history 의 CFP-TBD illustration 전부 자연 제외.
EXCLUDE_PATH_PREFIXES = (
    "archive/adr/",
    "docs/cross-repo-patches/",
)

# 본 lint 자기 자신 + carrier + 테스트 + workflow + baseline (§7.3.3 self-scan boundary — 필수).
#   docstring/코드 안 예시 토큰(CFP-TBD 등)이 자기 자신을 검출하지 않도록.
SELF_EXCLUDE_PATHS = (
    "scripts/lib/check_deferral_carrier_declared.py",
    "scripts/check-deferral-carrier-declared.sh",
    "scripts/test-check-deferral-carrier-declared.sh",
    # sibling gate self-test — embeds (b) tokens (`deferred_followup_cfp: TBD`,
    # FU-*) as GE-3/BT cross-fixtures. fixture source, not a governance
    # declaration surface (§7.3.3 self-scan boundary — CFP-2591).
    "scripts/test-check-deferred-followup-reconcile.sh",
    ".github/workflows/deferral-carrier-declared.yml",
    "docs/deferred-followup-baseline.yaml",
)

# named-carrier membership 검사용 registry (read-only).
DEFAULT_REGISTRY_REL = os.path.join("docs", "evidence-checks-registry.yaml")


# ─────────────────────── 검출 정규식 (ReDoS-safe, anchored, bounded) ─────────────

# TBD carrier: `deferred_followup_cfp: TBD` (미해결 placeholder).
_RE_TBD_CARRIER = re.compile(r"deferred_followup_cfp:\s{0,3}TBD")
# CFP-TBD placeholder.
_RE_CFP_TBD = re.compile(r"\bCFP-TBD\b")
# unwired FU 마커: `FU-1523-1` 류 (bounded quantifier, nested 0).
_RE_FU_MARKER = re.compile(r"\bFU-\d{1,6}-\d{1,3}\b")
# named-carrier level-1 handoff: `deferred_followup_cfp: CFP-<n>` (실 CFP 번호 참조).
_RE_NAMED_CARRIER = re.compile(r"deferred_followup_cfp:\s{0,3}(CFP-\d+)")


def detect_line(line, registry_text):
    """
    line 에서 첫 detect 토큰을 (token, kind) 로 반환, 없으면 None.

    우선순위: TBD carrier → CFP-TBD → FU marker → named-carrier(membership).
    named-carrier 는 CFP 번호가 registry 텍스트에 등장하면 면제(None), 미등장 시 FLAG
    (kind=registration-absent). registry 미로드(None) 이면 named-carrier 분지 skip.
    """
    m = _RE_TBD_CARRIER.search(line)
    if m:
        return (m.group(0), "tbd-carrier")
    m = _RE_CFP_TBD.search(line)
    if m:
        return (m.group(0), "cfp-tbd")
    m = _RE_FU_MARKER.search(line)
    if m:
        return (m.group(0), "fu-marker")
    m = _RE_NAMED_CARRIER.search(line)
    if m:
        cfp = m.group(1)
        if registry_text is not None and cfp in registry_text:
            return None  # membership 충족 → 면제 (wiring 완결은 (a) 위임)
        return (cfp, "registration-absent")
    return None


# ─────────────────────── allowlist 5축 (lane-count 축 답습, 토큰 재작성) ───────────

# 축 history/changelog: last_updated / 주석(#) 라인 / date / source_section / 주석 내 인용.
_RE_ALLOW_LAST_UPDATED = re.compile(r"^\s{0,8}last_updated:")
_RE_ALLOW_COMMENT_LINE = re.compile(r"^\s{0,8}#")
_RE_ALLOW_DATE = re.compile(r"^\s{0,8}date:")
_RE_ALLOW_SOURCE_SECTION = re.compile(r"source_section:")
# (구 _RE_ALLOW_COMMENT_QUOTE 제거 — CFP-2591 Phase 2: _RE_ALLOW_COMMENT_LINE(`^\s{0,8}#`) 이
#  strict-dominate 하는 unreachable dead regex 였음. comment-line 축이 먼저 `history-comment-line`
#  면제를 반환 → quote 분지 도달 불가 (커버리지 무손실). 자체 `.*"[^"]*...[^"]*"` 도 ReDoS 소지.)

# 축 negation: 토큰 인접(window) 에 부정 마커 (`TBD 금지` 등).
_RE_ALLOW_NEGATION = re.compile(r"금지|말 것|아니|하지 마")
_NEGATION_WINDOW = 12

# 축 counterfactual: 가정 조건절 `만약 ... (TBD|CFP-TBD) ... (blind|된다|위험|무너|silent)`.
#   ★ReDoS 봉합 (CFP-2591 Phase 2): sequential unbounded `.*` 2연속 → quadratic backtracking
#   (실측 64KB=6.3s). bounded `.{0,200}` 로 치환 + allowlist_match 진입 전 len(line) cap 이중 방어.
_COUNTERFACTUAL_MAX_LINE = 512
_RE_ALLOW_COUNTERFACTUAL = re.compile(
    r"만약.{0,200}(?:TBD|CFP-TBD).{0,200}(?:blind|된다|위험|무너|silent)"
)

# 축 path/within-line: 토큰 인접(window) 에 `.sh`/`.py`/`.yml`/`.yaml` 파일경로 참조 (over-broad 금지).
#   ★F-QA-1 봉합 (CFP-2591 Phase 2): 존재-blind → 존재-인지. 인접 경로가 repo_root 기준 실존
#   파일로 resolve 될 때만 면제 (부재 경로 지목 = FLAG). sibling gate(a) _path_exists 대칭 —
#   "미배선 FU → 부재 script 인접 지목" self-defeat 봉합.
_RE_ALLOW_PATH_REF = re.compile(r"[\w./-]+\.(?:sh|py|yml|yaml)\b")
_PATH_CTX_WINDOW = 40


def _path_exists(repo_root, rel_path):
    """인접 경로가 repo_root 기준 실존 파일/디렉터리로 resolve 되는지 (gate(a) _path_exists 대칭)."""
    return os.path.exists(os.path.join(repo_root, rel_path))


def _adjacent(line, token, window):
    """토큰 위치 ±window 문자열 발췌 (인접 판정용). 토큰 미발견 시 전체 line."""
    idx = line.find(token)
    if idx < 0:
        return line
    lo = max(0, idx - window)
    hi = min(len(line), idx + len(token) + window)
    return line[lo:hi]


def allowlist_match(line, token, repo_root):
    """
    line 이 allowlist 축 중 1+ 에 해당하면 면제 사유 문자열 반환, 아니면 None.
    (self 축은 collect 단계 SELF_EXCLUDE_PATHS 로 이미 제외.)

    repo_root: path/within-line 축 존재-인지 판정용 (인접 경로 실존 resolve 검사 — F-QA-1).
    """
    # history/changelog
    if _RE_ALLOW_LAST_UPDATED.match(line):
        return "history-last_updated"
    if _RE_ALLOW_COMMENT_LINE.match(line):
        return "history-comment-line"
    if _RE_ALLOW_DATE.match(line):
        return "history-date"
    if _RE_ALLOW_SOURCE_SECTION.search(line):
        return "history-source_section"

    # negation (토큰 인접)
    if _RE_ALLOW_NEGATION.search(_adjacent(line, token, _NEGATION_WINDOW)):
        return "negation (부정 토큰 인접 — carrier 단언 아님)"

    # counterfactual (가정 조건절) — line-length cap 로 sequential `.*` quadratic backtracking 차단.
    if len(line) <= _COUNTERFACTUAL_MAX_LINE and _RE_ALLOW_COUNTERFACTUAL.search(line):
        return "counterfactual (가정 조건절 '만약 ... TBD ... 위험')"

    # path/within-line (토큰 인접 파일경로 참조 — 존재-인지: 실존 파일 resolve 시만 면제, F-QA-1).
    window = _adjacent(line, token, _PATH_CTX_WINDOW)
    for m in _RE_ALLOW_PATH_REF.finditer(window):
        if _path_exists(repo_root, m.group(0)):
            return "path-within-line (인접 실존 파일경로 참조 문맥)"

    return None


# ─────────────────────── 단일 파일 scan ──────────────────────────────────────────

def scan_file(abs_path, rel_path, registry_text, repo_root):
    """
    파일 1개를 line-by-line scan. (flag(line) := detect AND NOT allowlist)

    repo_root: allowlist path/within-line 축 존재-인지 판정용 (F-QA-1).
    Returns: list of (rel_path, line_num, token, context_excerpt)
    Raises: OSError (read 실패 → 호출부가 SETUP exit 2 처리)
    """
    findings = []
    with open(abs_path, encoding="utf-8", errors="replace") as f:
        for line_num, raw_line in enumerate(f, start=1):
            line = raw_line.rstrip("\n")
            hit = detect_line(line, registry_text)
            if hit is None:
                continue
            token, _kind = hit
            if allowlist_match(line, token, repo_root) is not None:
                continue  # 면제
            ctx = line.strip()
            if len(ctx) > 100:
                ctx = ctx[:97] + "..."
            findings.append((rel_path, line_num, token, ctx))
    return findings


# ─────────────────────── 경로 수집 (git ls-files, lane-count 답습) ────────────────

def collect_files(repo_root, globs):
    """
    git ls-files <globs...> 결과에서 제외 경로/self 제외 후 검사 대상 파일 목록 반환.
    git 미가용 시 os.walk fallback.
    """
    rel_paths = _git_ls_files(repo_root, globs)
    if rel_paths is None:
        rel_paths = _walk_files(repo_root, globs)

    out = []
    for rp in rel_paths:
        rp_norm = rp.replace("\\", "/")
        if any(rp_norm.startswith(pfx) for pfx in EXCLUDE_PATH_PREFIXES):
            continue
        if rp_norm in SELF_EXCLUDE_PATHS:
            continue
        if not _is_text_candidate(rp_norm):
            continue
        out.append(rp_norm)
    return sorted(set(out))


def _is_text_candidate(rel_path):
    text_suffixes = (
        ".md", ".yaml", ".yml", ".tsv", ".json", ".sh", ".py", ".txt", ".mjs"
    )
    base = os.path.basename(rel_path)
    if base == "CLAUDE.md":
        return True
    return rel_path.endswith(text_suffixes)


def _git_ls_files(repo_root, globs):
    """git ls-files <globs> 결과 목록 반환. git 실패 시 None."""
    try:
        result = subprocess.run(
            ["git", "ls-files"] + list(globs),
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=True,
            encoding="utf-8",
            errors="replace",
        )
        return [l.strip() for l in result.stdout.splitlines() if l.strip()]
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def _walk_files(repo_root, globs):
    """git 미가용 fallback — globs 를 디렉터리/파일 prefix 로 해석해 os.walk."""
    collected = []
    for g in globs:
        target = os.path.join(repo_root, g)
        if os.path.isfile(target):
            collected.append(g.replace("\\", "/"))
            continue
        if os.path.isdir(target):
            for dirpath, _dirnames, filenames in os.walk(target):
                for fn in filenames:
                    abs_p = os.path.join(dirpath, fn)
                    rel_p = os.path.relpath(abs_p, repo_root).replace("\\", "/")
                    collected.append(rel_p)
    return collected


def _load_registry_text(repo_root):
    """named-carrier membership 검사용 registry 전체 텍스트 (없으면 None → 분지 skip)."""
    path = os.path.join(repo_root, DEFAULT_REGISTRY_REL)
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            return f.read()
    except OSError:
        return None


def scan_repo(repo_root, globs=None):
    """
    repo 전체를 scan 해 (rel_path, line_num, token, context) finding 리스트 반환 (grandfather 미적용).

    gen tool(gen_deferred_followup_baseline.generate) + cmd_check 공유 SSOT — 동일 detection/
    allowlist 경로 보장 (baseline round-trip 결정성). files 정렬 + line 순서 → 결정적.
    """
    globs = list(globs) if globs else DEFAULT_SCAN_GLOBS
    files = collect_files(repo_root, globs)
    registry_text = _load_registry_text(repo_root)
    findings = []
    for rel in files:
        abs_p = os.path.join(repo_root, rel)
        findings.extend(scan_file(abs_p, rel, registry_text, repo_root))
    return findings


# ─────────────────────── grandfather (new-only) ──────────────────────────────────

def _is_grandfathered(finding, surfaces):
    """
    finding (rel, line, token, ctx) 이 baseline declaration_surfaces 에 (동일 relpath + token
    substring 매치) 하면 True. line-number 미대조 (surface line-drift tolerant).
    """
    rel, _line, token, _ctx = finding
    for s in surfaces:
        if not isinstance(s, dict):
            continue
        loc = str(s.get("locator", ""))
        s_rel = loc.rsplit(":", 1)[0] if ":" in loc else loc
        s_tok = str(s.get("token", ""))
        if s_rel == rel and token in s_tok:
            return True
    return False


# ─────────────────────── 출력 (lane-count `::warning::` 답습) ──────────────────────

def _emit_flag(finding):
    rel_path, line_num, token, ctx = finding
    print(
        "::warning::check-deferral-carrier-declared: FLAG — "
        "%s:%d / token=\"%s\" / context=\"%s\""
        % (rel_path, line_num, token, ctx)
    )


_ACTION_GUIDE = (
    "[deferral-carrier-declared] deferred-followup 을 미해결 placeholder(TBD/CFP-TBD/unwired FU-N-N)\n"
    "로 남기면 forcing function 대상이 소멸 (silent debt). (warning mode — merge 비차단, advisory):\n"
    "  ① 실 carrier CFP/FU 를 발급해 placeholder 를 확정 번호로 치환 (deferred_followup_cfp: CFP-<n>)\n"
    "  ② named-carrier 는 evidence-checks-registry.yaml 에 carrier/sibling 로 등장시켜 membership 충족\n"
    "  ③ 미결 항목 자체를 폐기 (de-bloat)\n"
    "honest forcing ceiling: exit 1 = advisory 표식 — 실 차단은 워크플로 continue-on-error 소관.\n"
    "근거: ADR-060 §결정 6 (deferred-followup no-TBD lint) — placeholder carrier 유입 차단."
)


# ─────────────────────── 서브커맨드: check ───────────────────────────────────────

def cmd_check(args):
    repo_root = args.repo_root or "."
    globs = args.paths if args.paths else DEFAULT_SCAN_GLOBS

    files = collect_files(repo_root, globs)
    if not files:
        print(
            "[codeforge-deferral-carrier-declared-infra-error] check-deferral-carrier-declared: "
            "검사 경로 0개 (in-scope glob 매칭 파일 부재) — repo-root/glob 확인",
            file=sys.stderr,
        )
        return 2

    registry_text = _load_registry_text(repo_root)
    all_findings = []
    for rel_path in files:
        abs_path = os.path.join(repo_root, rel_path)
        try:
            all_findings.extend(scan_file(abs_path, rel_path, registry_text, repo_root))
        except OSError as exc:
            print(
                "[codeforge-deferral-carrier-declared-infra-error] check-deferral-carrier-declared: "
                "파일 read 실패: %s (%s)" % (rel_path, exc),
                file=sys.stderr,
            )
            return 2

    # ── baseline grandfather 분기 ────────────────────────────────────────────
    baseline_explicit = args.baseline is not None
    grandfathered_n = 0
    if baseline_explicit:
        if not os.path.isfile(args.baseline):
            print(
                "[codeforge-deferral-carrier-declared-infra-error] check-deferral-carrier-declared: "
                "--baseline 명시 경로 부재 (fail-loud): %s" % args.baseline,
                file=sys.stderr,
            )
            return 2
        try:
            baseline = _load_baseline_local(args.baseline)
        except (ValueError, OSError) as e:
            print(
                "[codeforge-deferral-carrier-declared-infra-error] check-deferral-carrier-declared: "
                "baseline malformed (%s): %s" % (args.baseline, e),
                file=sys.stderr,
            )
            return 2
        surfaces = baseline.get("declaration_surfaces") or []
        new_findings = [f for f in all_findings if not _is_grandfathered(f, surfaces)]
        grandfathered_n = len(all_findings) - len(new_findings)
    else:
        # --baseline 미지정 → pure detection (전건 report, grandfather 없음)
        new_findings = all_findings

    for finding in new_findings:
        _emit_flag(finding)

    if new_findings:
        print("")
        print(_ACTION_GUIDE)
        print("")

    print(
        "check-deferral-carrier-declared: NEW %d / GRANDFATHERED %d / DETECTED %d "
        "(warning tier — continue-on-error 로 비차단, advisory)"
        % (len(new_findings), grandfathered_n, len(all_findings))
    )
    return 1 if new_findings else 0


def _load_baseline_local(path):
    """
    baseline yaml 로드 (top-level mapping). reconcile 모듈 load_baseline 재사용 가능 시 그것을,
    아니면 로컬 yaml 로. (yaml.YAMLError 는 ValueError 계열로 상위에서 처리 안 되므로 여기서 매핑.)
    """
    if load_baseline is not None:
        try:
            return load_baseline(path)
        except Exception as e:  # yaml.YAMLError 포함 — malformed 통일 매핑
            raise ValueError(str(e))
    import yaml  # fallback (reconcile import 실패 시)
    try:
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise ValueError(str(e))
    if not isinstance(data, dict):
        raise ValueError("baseline top-level 이 mapping 아님")
    return data


# ─────────────────────── main ────────────────────────────────────────────────────

def main(argv):
    parser = argparse.ArgumentParser(
        description="deferral carrier declared (no-TBD) lint (CFP-2591 / ADR-060 §결정 6)"
    )
    subparsers = parser.add_subparsers(dest="command")

    check_p = subparsers.add_parser("check", help="in-scope 경로 전수 scan (new-only grandfather)")
    check_p.add_argument(
        "--repo-root", default=".",
        help="git repo root 경로 (default: 현재 디렉터리)",
    )
    check_p.add_argument(
        "--paths", nargs="*", default=None,
        help="검사 대상 glob 재정의 (default: docs/·CLAUDE.md·plugins/·scripts/·templates/·plugin.json)",
    )
    check_p.add_argument(
        "--baseline", default=None,
        help="baseline yaml 경로 (제공+존재 → grandfather subtract). 명시인데 missing/malformed → exit 2. "
             "미지정 → pure detection (전건 report).",
    )

    args = parser.parse_args(argv[1:])

    # 인자 없으면 check default (thin wrapper 가 보장하나 이중 안전)
    if args.command is None:
        args.command = "check"
        args.repo_root = "."
        args.paths = None
        args.baseline = None

    if args.command == "check":
        return cmd_check(args)

    parser.print_help(sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
