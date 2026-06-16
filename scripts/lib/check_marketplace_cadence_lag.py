#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/lib/check_marketplace_cadence_lag.py
CFP-2310 S3 (#2313) — Arc B 발행 cadence lag detect + Issue 자동생성 (advisory, warning tier)

main↔marketplace version drift 자동 감지. 9-plugin roster 각각의
  repo main plugin.json version  ↔  mclayer/marketplace marketplace.json version
을 비교해 lag(불일치)을 감지하고, lag 시 dedup 된 Issue 를 자동 발행한다.

★ scope (Epic #2310 U5): **detect + alert only**. 실 sync PR 자동생성 절대 금지.
  marketplace 선행 merge ordering(ADR-063 §결정 2)은 Orchestrator 책임으로 유지
  (ADR-063 Amendment 12). 본 모듈은 sync PR 생성 로직을 포함하지 않는다.

Usage:
  python3 check_marketplace_cadence_lag.py check [--repo-root <path>] [--dry-run]
  python3 check_marketplace_cadence_lag.py check --marketplace-json <path> [...]   # local override (test)
  python3 check_marketplace_cadence_lag.py roster [--repo-root <path>]
  python3 check_marketplace_cadence_lag.py signature --plugin <name> --direction <dir>

Roster (A2-9 authoritative — 디렉터리 enumeration, ~/.claude cache 비의존):
  {codeforge}(wrapper root .claude-plugin/plugin.json)
    ∪ {plugins/codeforge-*/.claude-plugin/plugin.json}
  CI runner 안전 — repo 파일만 읽음 (installed cache 경로 미사용).

Dedup signature (D4 — governance-drift 답습, 최대 함정 회피):
  sha256("marketplace-cadence-lag|<plugin>|<direction>") | first 16 chars
  ★ version 값 절대 제외 — 포함 시 sync 진척마다 signature 변동 → dedup 무력화 → 이슈 폭주.
  direction ∈ {main-ahead, marketplace-ahead} — 같은 plugin 이 같은 방향으로 계속
  lag 인 한 signature 불변 → 단일 open Issue 로 수렴.

Exit codes (ADR-060 §결정 15 3-tier — warning tier 답습):
  0 = PASS (lag 0 / lag 감지 + Issue auto-create 성공 — advisory, 비차단)
  1 = (reserved, 미사용)
  2 = SETUP error (missing dependency / 401 auth / marketplace fetch 실패)

Test override env:
  MLD_SKIP_ISSUE_CREATE=1   — Issue auto-create 차단 (dry-run / self-test mode)
  CBL_SKIP_ISSUE_CREATE=1   — (governance-drift 공유 컨벤션 답습) 동일 효과
  MLD_MOCK_401=1            — 401 fail-closed 강제 (PAT 인증 실패 mock)
  MLD_MOCK_429=1            — 429 fail-open 강제 (rate limit — skip run)

Prior art:
  scripts/lib/check_governance_drift.py (CFP-2061-S4 / ADR-060 §결정 31) — issue create + dedup + mock
  scripts/check-marketplace-parity.sh   (CFP-50 / ADR-016) — marketplace.json fetch 패턴
  scripts/check-plugin-version-bump-self.sh (CFP-2310 S2 / ADR-037 Amd 2) — 9-plugin roster enumeration

ADR refs: ADR-063(3-way atomic / §결정 2 ordering / Amd 12 Orchestrator sync) ·
          ADR-016(marketplace mirror) · ADR-066(단일 PAT) · ADR-060/061(warning tier + python entry) ·
          ADR-083(consumer-applicability: wrapper-self 전용) · ADR-037 Amd 2(9-plugin roster).
"""

import argparse
import glob
import hashlib
import json
import os
import subprocess
import sys

# Windows cp949 인코딩 회피 — stdout/stderr UTF-8 강제 (ADR-061 portability)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


REPO = "mclayer/plugin-codeforge"
MARKETPLACE_REPO = "mclayer/marketplace"
MARKETPLACE_PATH = ".claude-plugin/marketplace.json"
WRAPPER_NAME = "codeforge"
LABEL_LAG = "codeforge-improvement"
# 안정 검색 키 — title 에 inject 되며 dedup body 의 signature 와 함께 active-open 검색에 사용.
SIG_PREFIX = "mp-lag-sig"


# ─────────────────────── test mock 처리 (governance-drift 답습) ───────────────

def _handle_mocks():
    """Test override env 처리. 401/429 mock 트리거. None = 계속 진행."""
    if os.environ.get("MLD_MOCK_401", "") == "1":
        print(
            "[codeforge-cadence-infra-error] check-marketplace-cadence-lag: "
            "401 Unauthorized (mock) — PAT 인증 실패 "
            "(ADR-066 CODEFORGE_CROSS_REPO_PAT 확인 필요)",
            file=sys.stderr,
        )
        sys.exit(2)

    if os.environ.get("MLD_MOCK_429", "") == "1":
        print(
            "::warning::check-marketplace-cadence-lag: 429 Too Many Requests (mock) "
            "— rate limit, skipping run (fail-open)"
        )
        sys.exit(0)


def _should_skip_issue_create():
    """Issue create 차단 여부 (dry-run / self-test mode)."""
    return (
        os.environ.get("MLD_SKIP_ISSUE_CREATE", "") == "1"
        or os.environ.get("CBL_SKIP_ISSUE_CREATE", "") == "1"
    )


# ─────────────────────── roster enumeration (A2-9 authoritative) ──────────────

def discover_roster(repo_root):
    """
    9-plugin roster = {codeforge}(wrapper root) ∪ {plugins/codeforge-*/ 디렉터리}.
    각 entry → (plugin_name, plugin_json_abs_path).
    plugin.json name 우선, 결손 시 디렉터리명 (S2 discover_roster 답습).
    ~/.claude/plugins/cache 비의존 — repo 파일만 읽음 (CI runner 안전, A2-9 decoupling).
    """
    roster = []

    # (1) wrapper root
    wrapper_pj = os.path.join(repo_root, ".claude-plugin", "plugin.json")
    roster.append((WRAPPER_NAME, wrapper_pj))

    # (2) lane plugins — 디렉터리 실측 enumeration (정렬: 결정적 출력)
    pattern = os.path.join(repo_root, "plugins", "codeforge-*")
    for d in sorted(glob.glob(pattern)):
        if not os.path.isdir(d):
            continue
        pj = os.path.join(d, ".claude-plugin", "plugin.json")
        name = os.path.basename(d.rstrip("/"))
        if os.path.isfile(pj):
            try:
                with open(pj, encoding="utf-8") as f:
                    data = json.load(f)
                name = data.get("name") or name
            except (OSError, json.JSONDecodeError):
                pass
        roster.append((name, pj))

    return roster


def _read_local_version(plugin_json_path):
    """repo main plugin.json 의 version 읽기. 결손/파싱오류 = None."""
    try:
        with open(plugin_json_path, encoding="utf-8") as f:
            data = json.load(f)
        v = data.get("version")
        return v if v else None
    except (OSError, json.JSONDecodeError):
        return None


# ─────────────────────── marketplace.json fetch ──────────────────────────────

def _run_gh(args, check=True):
    """gh CLI 호출 wrapper — stdout 반환."""
    result = subprocess.run(
        ["gh"] + args,
        capture_output=True,
        text=True,
        check=check,
        encoding="utf-8",
        errors="replace",
    )
    return result.stdout.strip()


def fetch_marketplace_versions(marketplace_json_override=None):
    """
    marketplace.json 의 plugins[] → {name: version} dict 반환.
    override path 제공 시 local 파일 (test mode), 없으면 gh api 로 fetch (PAT read-only, ADR-066).
    fetch/parse 실패 = SETUP error (exit 2, fail-loud).
    """
    raw = None
    if marketplace_json_override:
        if not os.path.isfile(marketplace_json_override):
            print(
                f"[codeforge-cadence-infra-error] check-marketplace-cadence-lag: "
                f"marketplace override path not found: {marketplace_json_override}",
                file=sys.stderr,
            )
            sys.exit(2)
        try:
            with open(marketplace_json_override, encoding="utf-8") as f:
                raw = f.read()
        except OSError as e:
            print(
                f"[codeforge-cadence-infra-error] check-marketplace-cadence-lag: "
                f"marketplace override read error: {e}",
                file=sys.stderr,
            )
            sys.exit(2)
    else:
        # gh api repos/mclayer/marketplace/contents/.claude-plugin/marketplace.json
        #   --jq .content → base64 → decode (check-marketplace-parity.sh 답습)
        try:
            import base64
            content_b64 = _run_gh([
                "api",
                f"repos/{MARKETPLACE_REPO}/contents/{MARKETPLACE_PATH}",
                "--jq", ".content",
            ])
            raw = base64.b64decode(content_b64).decode("utf-8", errors="replace")
        except (subprocess.CalledProcessError, ValueError, OSError) as e:
            print(
                f"[codeforge-cadence-infra-error] check-marketplace-cadence-lag: "
                f"marketplace.json fetch 실패 ({MARKETPLACE_REPO}): {e}",
                file=sys.stderr,
            )
            sys.exit(2)

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        print(
            f"[codeforge-cadence-infra-error] check-marketplace-cadence-lag: "
            f"marketplace.json parse error: {e}",
            file=sys.stderr,
        )
        sys.exit(2)

    versions = {}
    for entry in data.get("plugins", []):
        name = entry.get("name")
        ver = entry.get("version")
        if name:
            versions[name] = ver
    return versions


# ─────────────────────── version 비교 + lag 판정 ─────────────────────────────

def _semver_parts(v):
    """'a.b.c' → (a, b, c) int tuple. 파싱 실패 = None."""
    if not v:
        return None
    parts = v.split(".")
    if len(parts) != 3:
        return None
    try:
        return tuple(int(p) for p in parts)
    except ValueError:
        return None


def _direction(main_v, market_v):
    """
    main vs marketplace version 비교 → direction 문자열.
      'in-sync'            — 동일 (lag 없음)
      'main-ahead'         — main > marketplace (= 발행 cadence lag, marketplace sync 누락. 갭② 재발 형태)
      'marketplace-ahead'  — marketplace > main (역방향 drift, 비정상)
      'unparseable'        — 둘 중 하나 semver 파싱 실패 (보수: lag 로 보고)
    """
    if main_v == market_v:
        return "in-sync"
    mp = _semver_parts(main_v)
    kp = _semver_parts(market_v)
    if mp is None or kp is None:
        return "unparseable"
    if mp > kp:
        return "main-ahead"
    if kp > mp:
        return "marketplace-ahead"
    return "in-sync"


def check_lag(roster, market_versions):
    """
    roster (name, pj) × market_versions → lag list.
    Returns: list of {plugin, main_version, marketplace_version, direction, signature}
    direction='in-sync' 는 lag 아님 (제외). 그 외(main-ahead/marketplace-ahead/unparseable/missing)
    = lag 로 보고.
    """
    lags = []
    for name, pj in roster:
        main_v = _read_local_version(pj)
        market_v = market_versions.get(name)

        if main_v is None:
            # repo plugin.json 결손/파싱불가 = 인프라 결함 (보수 보고)
            direction = "main-missing"
        elif market_v is None:
            # marketplace 미등록 = 등록 누락 lag (ADR-016 mirror 위반)
            direction = "marketplace-missing"
        else:
            direction = _direction(main_v, market_v)

        if direction == "in-sync":
            continue

        lags.append({
            "plugin": name,
            "main_version": main_v if main_v is not None else "(missing)",
            "marketplace_version": market_v if market_v is not None else "(missing)",
            "direction": direction,
            "signature": compute_signature(name, direction),
        })
    return lags


# ─────────────────────── dedup signature (D4 — 함정 회피 핵심) ────────────────

def compute_signature(plugin, direction):
    """
    sha256("marketplace-cadence-lag|<plugin>|<direction>") — first 16 chars.
    ★ version 값 절대 제외 — 포함 시 sync 진척/bump 마다 signature 변동 → dedup 무력화 (D4).
    governance-drift compute_signature 답습 (current_val 제외 원칙 동일).
    """
    raw = f"marketplace-cadence-lag|{plugin}|{direction}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


# ─────────────────────── 이슈 dedup 검색 + create ────────────────────────────

def check_dedup_issue(sig):
    """
    signature 로 active open Issue 검색. 존재하면 True (dedup skip).
    governance-drift check_dedup_issue 답습 — body 안 'mp-lag-sig: <sig>' 검색.
    """
    try:
        raw = _run_gh([
            "issue", "list",
            "--repo", REPO,
            "--label", LABEL_LAG,
            "--state", "open",
            "--search", f'"{SIG_PREFIX}: {sig}"',
            "--limit", "1",
            "--json", "number,title",
            "--jq", ".[0].number // empty",
        ])
        return bool(raw.strip())
    except subprocess.CalledProcessError:
        # 검색 실패 시 보수적으로 dedup 미적용 (create 진행) — at-least-once
        return False


def create_lag_issue(lag_item, dry_run=False):
    """
    cadence lag Issue 발행 — detect+alert only (sync PR 생성 절대 없음, Epic #2310 U5).
    dry_run=True 또는 MLD_SKIP_ISSUE_CREATE=1 / CBL_SKIP_ISSUE_CREATE=1 시 실제 create 없이 print.
    """
    plugin = lag_item["plugin"]
    sig = lag_item["signature"]
    main_v = lag_item["main_version"]
    market_v = lag_item["marketplace_version"]
    direction = lag_item["direction"]

    title = (
        f"[MARKETPLACE-LAG] {plugin}: main={main_v} ≠ marketplace={market_v} "
        f"({direction})"
    )
    body = (
        f"## 발행 cadence lag 감지 (Arc B — CFP-2310 S3)\n\n"
        f"**Plugin**: `{plugin}`\n"
        f"**Repo main plugin.json**: `{main_v}`\n"
        f"**marketplace.json**: `{market_v}`\n"
        f"**Direction**: `{direction}`\n\n"
        f"### 조치 (수동 — Orchestrator 책임)\n\n"
        f"main↔marketplace version drift 가 감지됐다. 본 알림은 **detect + alert 전용**이다.\n"
        f"실 sync PR 은 **자동 생성하지 않는다** — marketplace 선행 merge ordering "
        f"(ADR-063 §결정 2) 보존 의무 때문이다. Orchestrator 가 같은 Story 안 sync PR 을 "
        f"열어 정합한다 (ADR-063 Amendment 12):\n\n"
        f"- `main-ahead`: marketplace 에 누락된 bump 를 sync PR 로 반영 (marketplace 선행 merge).\n"
        f"- `marketplace-ahead`: 역방향 drift — main bump 누락 여부 점검.\n"
        f"- `*-missing`: roster/marketplace 등록 누락 (ADR-016 mirror 위반) 점검.\n\n"
        f"{SIG_PREFIX}: {sig}\n\n"
        f"---\n"
        f"Source: `scripts/lib/check_marketplace_cadence_lag.py` "
        f"(CFP-2310 S3 / ADR-063 §결정 2 ordering 보존)"
    )

    if dry_run or _should_skip_issue_create():
        print(f"[DRY-RUN] would create issue: {title}")
        print(f"  {SIG_PREFIX}: {sig}")
        return

    try:
        _run_gh([
            "issue", "create",
            "--repo", REPO,
            "--label", LABEL_LAG,
            "--title", title,
            "--body", body,
        ], check=True)
        print(f"[marketplace-cadence-lag] Issue created: {title}")
    except subprocess.CalledProcessError as e:
        # non-fatal — 다음 cron 실행이 재시도 (at-least-once)
        print(f"  -> Issue create failed (non-fatal, will retry on next run): {e}")


# ─────────────────────── 의존성 검사 ─────────────────────────────────────────

def _check_deps():
    """gh CLI 확인 (marketplace fetch + issue create 에 필요)."""
    try:
        subprocess.run(["gh", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print(
            "[codeforge-cadence-infra-error] check-marketplace-cadence-lag: "
            "gh CLI not installed or not in PATH",
            file=sys.stderr,
        )
        sys.exit(2)


# ─────────────────────── 서브커맨드: check ───────────────────────────────────

def cmd_check(args):
    """메인 check — roster 측정 + marketplace fetch + lag 판정 + Issue 발행 (dedup)."""
    _handle_mocks()

    repo_root = args.repo_root or "."
    roster = discover_roster(repo_root)

    # marketplace fetch — override(test) 없으면 gh api 필요 → 의존성 확인
    if not args.marketplace_json and not (args.dry_run or _should_skip_issue_create()):
        _check_deps()
    elif not args.marketplace_json:
        # dry-run 이어도 marketplace fetch 자체엔 gh 필요
        _check_deps()

    market_versions = fetch_marketplace_versions(args.marketplace_json)

    lags = check_lag(roster, market_versions)

    if not lags:
        print(
            f"check-marketplace-cadence-lag: PASS - 0 lag across "
            f"{len(roster)} plugins (main↔marketplace in-sync)"
        )
        sys.exit(0)

    issues_created = 0
    issues_dedup = 0

    for lag in lags:
        print(
            f"::warning::check-marketplace-cadence-lag: LAG detected — "
            f"plugin={lag['plugin']} main={lag['main_version']} "
            f"marketplace={lag['marketplace_version']} "
            f"direction={lag['direction']} {SIG_PREFIX}={lag['signature']}"
        )

        if not (args.dry_run or _should_skip_issue_create()):
            if check_dedup_issue(lag["signature"]):
                print(
                    f"  -> dedup: active Issue already exists "
                    f"for {SIG_PREFIX} {lag['signature']} — skipping create"
                )
                issues_dedup += 1
                continue

        create_lag_issue(lag, dry_run=args.dry_run)
        issues_created += 1

    print(
        f"check-marketplace-cadence-lag: WARNING - {len(lags)} lag(s) detected. "
        f"Issues created: {issues_created}, dedup skip: {issues_dedup} "
        f"(warning tier — detect+alert only, ADR-063 Amd 12). "
        f"실 sync PR = Orchestrator 책임 (자동 생성 안 함)."
    )

    # advisory — lag 감지해도 exit 0 (warning tier, PR 게이트 아님). setup error 만 exit 2.
    sys.exit(0)


# ─────────────────────── 서브커맨드: roster ──────────────────────────────────

def cmd_roster(args):
    """roster enumeration 출력 (self-test / 검증용) — '<name>\\t<main_version>' 줄."""
    repo_root = args.repo_root or "."
    roster = discover_roster(repo_root)
    for name, pj in roster:
        v = _read_local_version(pj)
        print(f"{name}\t{v if v is not None else '(missing)'}")
    sys.exit(0)


# ─────────────────────── 서브커맨드: signature ───────────────────────────────

def cmd_signature(args):
    """signature 출력 (D4 version-제외 검증용)."""
    print(compute_signature(args.plugin, args.direction))
    sys.exit(0)


# ─────────────────────── main ────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="발행 cadence lag detect — main↔marketplace version drift "
                    "+ Issue 자동생성 (CFP-2310 S3)"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # check
    check_p = subparsers.add_parser("check", help="lag 측정 + 판정 + Issue 발행 (dedup)")
    check_p.add_argument("--repo-root", default=".", help="git repo root (default: 현재 디렉터리)")
    check_p.add_argument("--dry-run", action="store_true", help="Issue 실제 생성 없이 결과만 출력")
    check_p.add_argument(
        "--marketplace-json", default=None,
        help="local marketplace.json override (test mode — gh api fetch 우회)",
    )

    # roster
    roster_p = subparsers.add_parser("roster", help="roster enumeration 출력")
    roster_p.add_argument("--repo-root", default=".", help="git repo root")

    # signature
    sig_p = subparsers.add_parser("signature", help="dedup signature 출력")
    sig_p.add_argument("--plugin", required=True)
    sig_p.add_argument("--direction", required=True)

    args = parser.parse_args()

    if args.command == "check":
        cmd_check(args)
    elif args.command == "roster":
        cmd_roster(args)
    elif args.command == "signature":
        cmd_signature(args)


if __name__ == "__main__":
    main()
