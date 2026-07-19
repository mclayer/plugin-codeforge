#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
scripts/lib/check_lane_entry_ownership.py
CFP-2761 §5.2 / ADR-085 §결정3 + ADR-073 Amendment 2 (4th source) — lane-entry ownership verify.
HOOK-ONLY (workflow:null) — CI 워크플로 게이트 아님, hook 경유 advisory 검증 (warning tier).

**derive-from-ambient** (CFP-2761 구현-리뷰 FIX / Change Plan #2108 ArchitectPL design-decided).
이전 계약은 `--lane`/`--git-identity` required=True 를 강제해 hook(`bash ... || true`, no args)에서
argparse exit 2 → `|| true` swallow → hollow(로직 미도달)였다. 신 계약은 세션 상태를 ambient git 에서
스스로 도출하고, 도출 실패는 **honest-degrade**(가시적 stdout "확인 불가" line + exit 0)로 처리한다.
NEVER silent-green, NEVER `|| true`.

6-step derive-from-ambient:
  1. git-identity  — `--git-identity` 주입 시 그대로(fixture override), 아니면 ambient
     `git -C <repo-root> config user.name`(fallback `user.email`) 도출. 도출 불가 → honest-degrade.
  2. branch → CFP key — `git -C <repo-root> rev-parse --abbrev-ref HEAD` → `cfp-<N>`(대소문자 무시)
     파싱 → CFP key. detached HEAD / non-CFP branch → honest-degrade.
  3. Story locate — `--sessions-file` 주입 시 그대로 사용(fixture override, locate skip). 아니면
     `--internal-docs-root DIR` 아래 `wrapper/stories/CFP-<N>.md` locate(optional; 미지정/부재 →
     honest-degrade).
  4. active_sessions[] read — Story frontmatter(YAML) 또는 sessions-file(JSON/YAML)에서
     `active_sessions[].git_identity` 값 수집. block 부재 → honest-degrade.
  5. ownership-presence — git-identity ∈ active_sessions[].git_identity ?
       present  → clean advisory line (exit 0).
       absent   → `::warning::lane-entry-ownership-verify: lane-entry identity=<id> CFP-<N> —
                  active_sessions ownership 부재 (re-adjudication candidate)` (exit 0).
  6. honest-degrade — 위 ambient 도출 실패(no git-identity / detached / non-CFP branch /
     Story·active_sessions 부재 / sessions-file 부재) 시 가시적 stdout line
     `lane-entry-ownership-verify: 확인 불가 (<reason>) — advisory honest no-op` + exit 0.

fixture-injection (deterministic self-test): `--git-identity` AND `--sessions-file` 둘 다 주입 시
  git/Story ambient 를 건너뛰고 결정적으로 ownership-presence 를 평가한다(present/absent 주입 가능).
  둘 다 부재 시 ambient live 경로. (각 인자는 step-level override 로 부분 주입도 가능.)

scope = **ownership-presence subset** — 진입 세션 git-identity 가 Story active_sessions 소유 레지스트리에
  기록돼 있는지의 presence 검증만 한다. full 4-step 동시-소유 polling(동일 lane concurrent distinct
  owner coordination 등)은 **parallel-work-sentinel 과 disjoint** — 본 hook 은 그 축을 중복 커버하지
  않는다(no double-coverage). `--lane` 은 이제 informational only(lane-entry 자체가 trigger, 검증
  essence = ownership-presence 이며 entry_phase 필터링 없음).

DoS guard (§8.6, ADR-082 Amendment 38 resource-safety): Story/sessions-file bounded read(byte cap),
  frontmatter 구조 파싱만(재귀 없음), O(n) entry iterate. bounded degradation — 임의 입력 무해 아님.

CLI 계약 (ADR-061 house style — 고정, hook + self-test 소비; 전 인자 optional):
  bash scripts/check-lane-entry-ownership.sh [--repo-root DIR] [--lane NAME] [--git-identity ID]
       [--sessions-file FILE] [--internal-docs-root DIR]

Exit codes (ADR-060 §결정5 tri-tier — warning tier, advisory NEVER blocks):
  0 = clean(owner 정합) OR warning finding 방출 OR honest-degrade("확인 불가").
      finding 은 STDOUT 에 `::warning::lane-entry-ownership-verify: <detail>` 로 surface.
  2 = `--sessions-file` 이 명시됐고 파일이 **존재하나 파싱 불가**(TC-UNKNOWN fail-closed). 그 외
      required-arg 미스로 인한 exit 2 는 없음(전 인자 optional). 파일 부재는 honest-degrade(exit 0).
  3 = 미사용.
  1 = strict-tier 미사용 (warning tier).

ADR refs: CFP-2761 §5.2 (carrier) / ADR-085 §결정3 (lane-entry ownership) / ADR-073 Amendment 2
  (polling 4th source) / ADR-060 §결정5 (warning tri-tier) / ADR-082 Amendment 38 §8.6
  (resource-safety) / ADR-061 §결정1 (Python SSOT + thin wrapper).
"""

import argparse
import json
import os
import re
import subprocess
import sys

# Windows cp949 stdout/stderr 인코딩 차단 — UTF-8 강제 (ADR-061 portability 답습).
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
    except Exception:
        pass

CHECK_NAME = "lane-entry-ownership-verify"

MAX_READ_BYTES = 4 * 1024 * 1024  # Story/sessions-file 상한 4MB (§8.6 bounded read).

# 브랜치명 → CFP key 파서 (대소문자 무시; cfp-<N>[-slug] 앞자리 0 흡수).
_CFP_BRANCH_RE = re.compile(r"^cfp-0*([0-9]{1,8})(?:-|$)", re.IGNORECASE)


# ─────────────────────── ambient git 조회 ────────────────────────────────────────

def _git(repo_root, args):
    """git -C <repo_root> <args> 실행 → stdout(str) 또는 None (실패/비-repo)."""
    try:
        result = subprocess.run(
            ["git", "-C", repo_root] + args,
            capture_output=True, text=True, timeout=15,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if result.returncode != 0:
        return None
    return result.stdout


def _derive_git_identity(repo_root):
    """ambient git identity 도출: user.name 우선, fallback user.email. 없으면 None."""
    name = _git(repo_root, ["config", "user.name"])
    if name and name.strip():
        return name.strip()
    email = _git(repo_root, ["config", "user.email"])
    if email and email.strip():
        return email.strip()
    return None


def _derive_branch(repo_root):
    """현재 HEAD 브랜치명. git 부재/비-repo → None. detached HEAD → 'HEAD'."""
    branch = _git(repo_root, ["rev-parse", "--abbrev-ref", "HEAD"])
    if branch is None:
        return None
    branch = branch.strip()
    return branch or None


def _parse_cfp_key(branch):
    """브랜치명 → 'CFP-<N>'. cfp- 접두 아니면(detached 'HEAD' 포함) None."""
    if not branch:
        return None
    m = _CFP_BRANCH_RE.match(branch)
    if not m:
        return None
    return "CFP-%s" % m.group(1)


# ─────────────────────── active_sessions 파싱 (bounded) ──────────────────────────

def _yaml_load(text):
    """yaml.safe_load 래퍼. yaml 미설치/파싱 실패 → 'ERR' sentinel."""
    try:
        import yaml
    except ImportError:
        return "ERR"
    try:
        return yaml.safe_load(text)
    except Exception:
        return "ERR"


def _parse_structured(raw):
    """raw → (data, error_bool). YAML frontmatter(Story .md) 우선, 아니면 JSON→YAML whole-doc."""
    # (a) YAML frontmatter: 첫 줄 '---' ... 닫는 '---'/'...'.
    if raw.startswith("---"):
        lines = raw.splitlines()
        if lines and lines[0].strip() == "---":
            end = next(
                (i for i in range(1, len(lines)) if lines[i].strip() in ("---", "...")),
                None,
            )
            if end is not None:
                fm = _yaml_load("\n".join(lines[1:end]))
                if fm == "ERR":
                    return None, True
                return fm, False
    # (b) whole-doc: JSON 우선, 실패 시 YAML.
    try:
        return json.loads(raw), False
    except (ValueError, TypeError):
        pass
    y = _yaml_load(raw)
    if y == "ERR":
        return None, True
    return y, False


def _extract_active_sessions(path):
    """Story frontmatter 또는 sessions-file 에서 active_sessions entry list 추출.

    반환:
      "PARSE_ERROR" — 파일 존재하나 구조 파싱 불가.
      None          — 파싱 성공했으나 active_sessions block 부재.
      list[dict]    — active_sessions entry list (빈 list 가능).
    """
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            raw = f.read(MAX_READ_BYTES)
    except OSError:
        return "PARSE_ERROR"

    data, err = _parse_structured(raw)
    if err:
        return "PARSE_ERROR"

    if isinstance(data, list):
        entries = data
    elif isinstance(data, dict):
        if "active_sessions" not in data:
            return None
        entries = data.get("active_sessions")
    else:
        # None/scalar/str → active_sessions 도달 불가 = block 부재.
        return None

    if entries is None:
        return None
    if not isinstance(entries, list):
        return "PARSE_ERROR"
    # entry 는 dict 만 (비-dict 는 무시 — 방어).
    return [e for e in entries if isinstance(e, dict)]


def _collect_identities(entries):
    """active_sessions entry list → {git_identity} set (str)."""
    ids = set()
    for e in entries:
        v = e.get("git_identity")
        if v is not None:
            ids.add(str(v))
    return ids


# ─────────────────────── honest-degrade ──────────────────────────────────────────

def _degrade(reason):
    """가시적 stdout '확인 불가' line + exit 0 (NEVER silent-green, NEVER `|| true`)."""
    print(
        "%s: 확인 불가 (%s) — advisory honest no-op" % (CHECK_NAME, reason)
    )
    return 0


def _cfp_label(cfp_key):
    """warning/clean line 용 CFP 라벨. ambient 미도출(fixture 주입) 시 fallback."""
    return cfp_key if cfp_key else "CFP-(sessions-file 주입)"


def _lane_suffix(lane):
    """--lane informational suffix (주입 시에만)."""
    return " [lane=%s]" % lane if lane else ""


# ─────────────────────── main ────────────────────────────────────────────────────

def main(argv):
    parser = argparse.ArgumentParser(
        prog="check_lane_entry_ownership.py",
        description="lane-entry ownership-presence verify (derive-from-ambient, HOOK-ONLY, warning tier).",
    )
    parser.add_argument("--repo-root", default=None, help="ambient git 조회 루트 (기본 = 자동 탐지).")
    parser.add_argument("--lane", default=None, help="진입 lane 이름 (informational only).")
    parser.add_argument("--git-identity", default=None, help="진입 세션 git identity (fixture override; 부재 시 ambient 도출).")
    parser.add_argument("--sessions-file", default=None, help="active_sessions source (fixture override; JSON/YAML/frontmatter).")
    parser.add_argument("--internal-docs-root", default=None, help="internal-docs 루트 (ambient Story locate 용).")
    try:
        args = parser.parse_args(argv[1:])
    except SystemExit:
        return 2  # usage/argparse 오류 (unknown flag 등) — required-arg 미스는 없음(전 optional).

    repo_root = args.repo_root
    if repo_root is None:
        repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    repo_root = os.path.abspath(repo_root)

    # ── Step 1: git-identity (주입 override → ambient) ──
    if args.git_identity is not None:
        git_identity = args.git_identity
    else:
        git_identity = _derive_git_identity(repo_root)
        if not git_identity:
            return _degrade("git-identity 도출 불가 (git config user.name/user.email 부재/비-repo)")

    # ── Step 2+3: sessions source 결정 (sessions-file 주입 override → ambient locate) ──
    if args.sessions_file is not None:
        # sessions-file override: Story locate + branch 도출 skip (fixture 결정성).
        cfp_key = None
        sessions_path = args.sessions_file
        explicit_file = True
    else:
        # ambient: branch → CFP key → Story locate.
        branch = _derive_branch(repo_root)
        if branch is None:
            return _degrade("branch 도출 불가 (git 부재/비-repo)")
        cfp_key = _parse_cfp_key(branch)
        if cfp_key is None:
            reason = "detached HEAD" if branch == "HEAD" else "non-CFP branch: %s" % branch
            return _degrade("branch→CFP key 도출 불가 (%s)" % reason)
        if args.internal_docs_root is None:
            return _degrade(
                "Story locate 불가 (--internal-docs-root 미지정, %s active_sessions 미도달)" % cfp_key
            )
        sessions_path = os.path.join(
            args.internal_docs_root, "wrapper", "stories", "%s.md" % cfp_key
        )
        explicit_file = False
        if not os.path.isfile(sessions_path):
            return _degrade("Story 파일 부재 (%s)" % sessions_path)

    # ── Step 4: active_sessions read ──
    if explicit_file and not os.path.isfile(sessions_path):
        # 명시 sessions-file 이 아예 부재 = honest-degrade (파싱 불가 아님 → exit 2 아님).
        return _degrade("sessions-file 부재: %s" % sessions_path)

    parsed = _extract_active_sessions(sessions_path)
    if parsed == "PARSE_ERROR":
        if explicit_file:
            # 명시 sessions-file 이 존재하나 파싱 불가 = TC-UNKNOWN fail-closed (exit 2).
            print(
                "::error::%s: sessions-file 파싱 불가(frontmatter/JSON/YAML): %s (TC-UNKNOWN fail-closed)"
                % (CHECK_NAME, sessions_path),
                file=sys.stderr,
            )
            return 2
        # ambient-located Story 파싱 불가 = honest-degrade (advisory NEVER blocks).
        return _degrade("active_sessions 파싱 불가 (%s)" % sessions_path)
    if parsed is None:
        return _degrade("active_sessions 부재 (%s)" % sessions_path)

    # ── Step 5: ownership-presence ──
    identities = _collect_identities(parsed)
    ownership_present = git_identity in identities
    if not ownership_present:
        print(
            "::warning::%s: lane-entry identity=%s %s — active_sessions ownership 부재 "
            "(re-adjudication candidate)%s"
            % (CHECK_NAME, git_identity, _cfp_label(cfp_key), _lane_suffix(args.lane))
        )
        return 0
    print(
        "%s: lane-entry identity=%s %s — active_sessions ownership 정합 (advisory)%s"
        % (CHECK_NAME, git_identity, _cfp_label(cfp_key), _lane_suffix(args.lane))
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
