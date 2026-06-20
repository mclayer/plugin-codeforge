#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/lib/check_deferred_followup_reconcile.py
CFP-2381 / ADR-060 Amendment 18 §결정 32 — deferred-followup reconcile 게이트 (warning tier)

§결정 19 (Amendment 6) 가 `recurrence.promotion_trigger: auto_blocking` 을 "별도 carrier 가
승격 평가 의무" 로 선언했으나 carrier 발의 자체를 강제하는 mechanical forcing function 부재.
본 게이트가 "임계 초과 + auto_blocking + 전용 carrier 부재" entry 를 자동 검출 + 강제 action 3택.

Usage:
  python3 check_deferred_followup_reconcile.py check [--registry <path>] [--repo-root <path>]
  python3 check_deferred_followup_reconcile.py resolve --command "<detect_command 값>"
    → 닫힌집합 resolve 결과 진단 출력 (test/디버그용)

Exit codes (ADR-060 §결정 15 3-tier — warning tier):
  0 = PASS (FLAG 0 — INFO/UNRESOLVED 만 있어도 advisory)
  1 = FLAG 1+ (warning emit — continue-on-error 로 비차단, advisory only)
  2 = SETUP error (registry 부재 / yaml parse 실패 / python3 의존성)

검출 1급 firing 조건 (§32.B — 3-AND, status-agnostic):
  flag(entry) := (recurrence.count >= recurrence.threshold)
              AND (recurrence.promotion_trigger == "auto_blocking")
              AND carrier_absent(entry)

carrier_absent(entry) := NOT exists(resolve_path(entry.detect_command))
                      OR NOT exists(resolve_path(entry.workflow))     # OR 결합

Prior art (worktree 실존 확인 — ADR-119):
  scripts/lib/check_governance_drift.py  (registry PyYAML 파싱 + advisory exit + bash thin wrapper)
  scripts/check-increment-justification.sh  (trigger-path 감지 presence-grep)
  .github/workflows/operational-outcome-signal-lint.yml  (self-validation test job in-workflow)

ADR refs: ADR-060 Amendment 18 §결정 32 / ADR-061 / ADR-005 / ADR-127
"""

import argparse
import os
import re
import sys

import yaml

# Windows cp949 인코딩 문제 회피: stdout/stderr 를 UTF-8 강제 (ADR-061 portability)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


DEFAULT_REGISTRY_REL = os.path.join("docs", "evidence-checks-registry.yaml")

# 닫힌집합 — 지원 단일 interpreter (§32.B 표 1행). `sh` = 정당한 POSIX shell (F-CR-2381-1).
_INTERPRETERS = {"bash", "sh", "python", "python3"}

# 닫힌집합 — 경로 token 으로 인정하는 확장자 (§32.B + §7.2)
_PATH_SUFFIXES = (".sh", ".py", ".yml", ".yaml")

# prose/null 마커 — detect_command 축 검사 제외 (§32.B 표 2행, false-positive 차단)
#   "workflow inline — ...", "github-actions-runtime" 등 파일 경로 아님.
#   resolve 결과 kind="skip" 로 분류.


# ─────────────────────── resolve (닫힌집합 + fail-loud) ──────────────────────

def resolve_command(raw):
    """
    detect_command 문자열을 닫힌집합 규칙으로 분해해 단일 경로 token 을 추출.

    Returns dict:
      {"kind": "path",       "path": "<rel path>"}   — resolve 성공 (carrier_absent 판정 입력)
      {"kind": "skip",       "reason": "<...>"}        — 경로 미보유 (검사 제외, §32.B 표 2행)
      {"kind": "unresolved", "reason": "<...>"}        — 복합·모호 (fail-loud, §32.B 표 3행)

    닫힌집합 규칙 (§32.B):
      - None / 빈문자열 / prose 마커 (interpreter 로 시작 안 함, 경로 확장자 token 없음) → skip
      - `bash -c '...'` (interpreter 직후 `-c` 옵션) → unresolved (복합)
      - `A.sh && B.sh` / `;` / `|` (shell 연산자 다중 파일) → unresolved (복합)
      - 단일 interpreter + 단일 경로 token (env-prefix `VAR=x` / flag 뒤따름 허용) → path
      - interpreter 매칭됐는데 경로 token 없음 → unresolved (모호)
      - interpreter 미매칭이나 경로 확장자 token 1개만 존재 → path (관용 — token 직접 지목)
      - interpreter 미매칭 + 경로 token 0개 → skip (prose)
    """
    if raw is None:
        return {"kind": "skip", "reason": "null"}
    s = str(raw).strip()
    if not s:
        return {"kind": "skip", "reason": "empty"}

    # 복합·모호 1: shell 연산자 (다중 명령 / 다중 파일) → fail-loud
    #   `&&` / `||` / `;` / pipe `|` 발견 시 단일 파일 단정 불가.
    #   pipe 는 무공백 `A.sh|B.sh` 도 잡음 (F-CR-2381-2 — 공백 의존 regex false-negative 차단,
    #   &&·;·pipe 와 일관). bare `|` 1개라도 = 다중 명령 → UNRESOLVED.
    if re.search(r"&&|;|\|", s):
        return {"kind": "unresolved", "reason": "shell-operator (다중 명령/파일)"}

    tokens = s.split()

    # env-prefix 제거: 선행 `VAR=value` 토큰 skip (§32.B — env-prefix 인자 무시)
    idx = 0
    while idx < len(tokens) and _is_env_assignment(tokens[idx]):
        idx += 1
    rest = tokens[idx:]

    if not rest:
        return {"kind": "skip", "reason": "env-only (명령 token 없음)"}

    head = rest[0]

    # interpreter 매칭 분기
    if head in _INTERPRETERS:
        args = rest[1:]
        # 복합·모호 2: `bash -c '...'` inline 명령 → fail-loud
        if args and args[0] == "-c":
            return {"kind": "unresolved", "reason": "interpreter -c inline 명령"}
        # 단일 경로 token 추출 (flag / env-prefix `${VAR}` 인자 무시 — 경로 token 만)
        path_tokens = [t for t in args if _is_path_token(t)]
        if len(path_tokens) == 1:
            return {"kind": "path", "path": path_tokens[0]}
        if len(path_tokens) == 0:
            return {"kind": "unresolved", "reason": "interpreter 직후 경로 token 부재"}
        # 2+ 경로 token = 복합 → fail-loud
        return {"kind": "unresolved",
                "reason": "interpreter 뒤 경로 token 다중 (%d개)" % len(path_tokens)}

    # interpreter 미매칭 — prose 또는 직접 경로 지목
    path_tokens = [t for t in rest if _is_path_token(t)]
    if len(path_tokens) == 0:
        # "workflow inline — ...", "github-actions-runtime" 등 prose → skip
        return {"kind": "skip", "reason": "prose 마커 (경로 token 부재)"}
    if len(path_tokens) == 1:
        return {"kind": "path", "path": path_tokens[0]}
    return {"kind": "unresolved",
            "reason": "interpreter 미매칭 + 경로 token 다중 (%d개)" % len(path_tokens)}


def _is_env_assignment(token):
    """`VAR=value` 형태 env-prefix 토큰 여부 (경로 token 아닐 때만)."""
    if "=" not in token:
        return False
    # 경로 token (확장자 보유) 은 env-prefix 아님
    if _is_path_token(token):
        return False
    name = token.split("=", 1)[0]
    return bool(re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name))


def _is_path_token(token):
    """경로 token 여부 — 닫힌집합 확장자로 끝나는 token (flag/`${VAR}` 인자 제외)."""
    if token.startswith("-"):
        return False
    # `${VAR}` 류 변수 인자는 경로 token 아님 (env-prefix 인자 무시)
    if "${" in token or token.startswith("$"):
        return False
    return token.endswith(_PATH_SUFFIXES)


# ─────────────────────── workflow 2-root parity resolve (§32.B) ──────────────

def resolve_workflow_field(raw):
    """
    workflow field 값을 verbatim 파일 경로로 해석.

    Returns dict:
      {"kind": "path",  "paths": [<rel path>, ...]}  — 확인 대상 경로 목록 (2-root parity 포함)
      {"kind": "skip",  "reason": "<...>"}             — 경로 미보유 (null/prose, 검사 제외)

    2-root parity (§32.B):
      값이 `templates/github-workflows/<f>.yml` 이면 ADR-005 byte-parity 의무상
      self-app `.github/workflows/<f>.yml` 도 동반 실존해야 하므로 둘 다 확인.
      값이 `.github/workflows/<f>.yml` single-root 이면 그 경로만 확인.
    """
    if raw is None:
        return {"kind": "skip", "reason": "null"}
    s = str(raw).strip()
    if not s:
        return {"kind": "skip", "reason": "empty"}

    # workflow field 는 verbatim 경로 — 단일 token 이어야 함.
    # prose 마커 (공백 포함 자유 텍스트 + 경로 확장자 token 부재) → skip
    if not s.endswith((".yml", ".yaml")):
        return {"kind": "skip", "reason": "prose/non-path workflow value"}

    paths = [s]
    tpl_prefix = "templates/github-workflows/"
    if s.startswith(tpl_prefix):
        basename = s[len(tpl_prefix):]
        self_app = ".github/workflows/" + basename
        paths.append(self_app)  # 2-root parity (template + self-app 둘 다 확인)

    return {"kind": "path", "paths": paths}


# ─────────────────────── carrier_absent 판정 (§7.2 OR 결합) ──────────────────

def carrier_absent(entry, repo_root):
    """
    carrier_absent(entry) := NOT exists(detect_command path) OR NOT exists(workflow path)

    Returns dict:
      {"absent": bool, "absent_axes": [<...>], "unresolved": [<axis: reason>, ...],
       "detail": {"detect_command": <resolve dict>, "workflow": <resolve dict>}}

    - 검사 제외 (skip) 축은 carrier_absent 판정 입력 아님 (§32.B — 경로 미보유).
    - unresolved 축은 carrier_absent True/False 단정 금지 (fail-loud, §32.B 표 3행).
      → unresolved 가 1+ 면 해당 entry 는 UNRESOLVED 로 별도 분류 (FLAG/PASS 단정 금지).
    """
    dc_resolve = resolve_command(entry.get("detect_command"))
    wf_resolve = resolve_workflow_field(entry.get("workflow"))

    absent_axes = []
    unresolved = []

    # detect_command 축
    if dc_resolve["kind"] == "path":
        if not _path_exists(repo_root, dc_resolve["path"]):
            absent_axes.append("detect_command:%s" % dc_resolve["path"])
    elif dc_resolve["kind"] == "unresolved":
        unresolved.append("detect_command:%s" % dc_resolve["reason"])
    # kind == skip → 검사 제외 (입력 아님)

    # workflow 축
    if wf_resolve["kind"] == "path":
        missing = [p for p in wf_resolve["paths"] if not _path_exists(repo_root, p)]
        if missing:
            absent_axes.append("workflow:%s" % ",".join(missing))
    # workflow skip → 검사 제외 (입력 아님)

    return {
        "absent": bool(absent_axes),
        "absent_axes": absent_axes,
        "unresolved": unresolved,
        "detail": {"detect_command": dc_resolve, "workflow": wf_resolve},
    }


def _path_exists(repo_root, rel_path):
    return os.path.exists(os.path.join(repo_root, rel_path))


# ─────────────────────── entry 분류 (§7.4 algorithm) ─────────────────────────

def classify_entry(entry, repo_root):
    """
    단일 entry 를 §7.4 algorithm 에 따라 분류.

    Returns one of:
      None        — 검출 모집단 제외 (recurrence/threshold 미보유 / count<threshold /
                     promotion_trigger 무관 / carrier 실존)
      dict("FLAG") — auto_blocking + over-threshold + carrier-absent (1급 firing, 강제 3택)
      dict("INFO") — advisory + over-threshold + carrier-absent (secondary, 강제 미요구)
      dict("UNRESOLVED") — carrier_absent 단정 불가 (fail-loud, reviewer 수동 판정)
    """
    rec = entry.get("recurrence")
    if not isinstance(rec, dict):
        return None
    if "threshold" not in rec or rec.get("threshold") is None:
        return None  # threshold 미정의 → count 비교 불가 → 검출 제외
    count = rec.get("count", 0)
    threshold = rec.get("threshold")
    try:
        if int(count) < int(threshold):
            return None
    except (TypeError, ValueError):
        return None

    pt = rec.get("promotion_trigger")
    if pt not in ("auto_blocking", "advisory"):
        return None  # warning_tier_initial / none / 기타 → "should-be-blocking" 신호 아님

    ca = carrier_absent(entry, repo_root)

    # fail-loud: unresolved 축이 있으면 carrier_absent 단정 금지 → UNRESOLVED 분류
    if ca["unresolved"]:
        return {
            "tier": "UNRESOLVED",
            "name": entry.get("name", "<unnamed>"),
            "count": count,
            "threshold": threshold,
            "promotion_trigger": pt,
            "unresolved": ca["unresolved"],
            "absent_axes": ca["absent_axes"],
        }

    if not ca["absent"]:
        return None  # carrier 실존 → 자연 PASS (self-entry 포함)

    return {
        "tier": "FLAG" if pt == "auto_blocking" else "INFO",
        "name": entry.get("name", "<unnamed>"),
        "count": count,
        "threshold": threshold,
        "promotion_trigger": pt,
        "absent_axes": ca["absent_axes"],
    }


# ─────────────────────── 출력 (§32.D 강제 action 3택) ────────────────────────

def _emit_flag(item):
    paths = "; ".join(item["absent_axes"])
    print(
        "::warning::check-deferred-followup-reconcile: FLAG — "
        "entry=%s count=%s/%s promotion_trigger=%s absent=[%s]"
        % (item["name"], item["count"], item["threshold"],
           item["promotion_trigger"], paths)
    )


def _emit_info(item):
    paths = "; ".join(item["absent_axes"])
    print(
        "::notice::check-deferred-followup-reconcile: INFO (secondary) — "
        "entry=%s count=%s/%s promotion_trigger=advisory absent=[%s]"
        % (item["name"], item["count"], item["threshold"], paths)
    )


def _emit_unresolved(item):
    reasons = "; ".join(item["unresolved"])
    print(
        "::warning::check-deferred-followup-reconcile: UNRESOLVED (fail-loud, 수동 판정) — "
        "entry=%s count=%s/%s promotion_trigger=%s 사유=[%s]"
        % (item["name"], item["count"], item["threshold"],
           item["promotion_trigger"], reasons)
    )


_ACTION_GUIDE = (
    "[deferred-followup-reconcile] 강제 action 3택 (warning mode — merge 비차단, advisory):\n"
    "  ① 배선 carrier (script + workflow) 발의 — #1602 5-element 템플릿 사용\n"
    "  ② tier-downgrade-justification: 근거 강등 — check-tier-downgrade-guard.sh 마커 패턴\n"
    "     (auto_blocking → none/advisory 의도적 강등 + 근거 명시)\n"
    "  ③ 폐기 — entry 제거 (de-bloat)\n"
    "근거: ADR-060 Amendment 18 §결정 32 — §결정 19 auto_blocking 라벨의 mechanical forcing function."
)


# ─────────────────────── 서브커맨드: check ───────────────────────────────────

def cmd_check(args):
    repo_root = args.repo_root or "."
    registry_path = args.registry or os.path.join(repo_root, DEFAULT_REGISTRY_REL)

    try:
        with open(registry_path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except FileNotFoundError:
        print(
            "[codeforge-evidence-registry-infra-error] check-deferred-followup-reconcile: "
            "registry file not found: %s" % registry_path,
            file=sys.stderr,
        )
        sys.exit(2)
    except yaml.YAMLError as e:
        print(
            "[codeforge-evidence-registry-infra-error] check-deferred-followup-reconcile: "
            "registry YAML parse error: %s" % e,
            file=sys.stderr,
        )
        sys.exit(2)

    if not isinstance(data, dict):
        print(
            "[codeforge-evidence-registry-infra-error] check-deferred-followup-reconcile: "
            "registry root 가 mapping 아님",
            file=sys.stderr,
        )
        sys.exit(2)

    entries = data.get("entries", [])
    if not isinstance(entries, list):
        print(
            "[codeforge-evidence-registry-infra-error] check-deferred-followup-reconcile: "
            "entries[] 가 list 아님",
            file=sys.stderr,
        )
        sys.exit(2)

    flags = []
    infos = []
    unresolveds = []

    for entry in entries:
        if not isinstance(entry, dict):
            continue
        result = classify_entry(entry, repo_root)
        if result is None:
            continue
        if result["tier"] == "FLAG":
            flags.append(result)
        elif result["tier"] == "INFO":
            infos.append(result)
        elif result["tier"] == "UNRESOLVED":
            unresolveds.append(result)

    # 출력
    for item in flags:
        _emit_flag(item)
    for item in infos:
        _emit_info(item)
    for item in unresolveds:
        _emit_unresolved(item)

    if flags:
        print("")
        print(_ACTION_GUIDE)
        print("")
        print(
            "check-deferred-followup-reconcile: FLAG %d / INFO %d / UNRESOLVED %d "
            "(warning tier — continue-on-error 로 비차단, advisory only)"
            % (len(flags), len(infos), len(unresolveds))
        )
        sys.exit(1)

    print(
        "check-deferred-followup-reconcile: PASS — FLAG 0 (INFO %d / UNRESOLVED %d) "
        "across %d entries (warning tier)"
        % (len(infos), len(unresolveds), len(entries))
    )
    sys.exit(0)


# ─────────────────────── 서브커맨드: resolve (test/디버그) ────────────────────

def cmd_resolve(args):
    """detect_command 문자열 닫힌집합 resolve 결과 진단 출력 (test/디버그용)."""
    result = resolve_command(args.cmd_str)
    print("kind=%s" % result["kind"])
    if result["kind"] == "path":
        print("path=%s" % result["path"])
    else:
        print("reason=%s" % result["reason"])
    sys.exit(0)


# ─────────────────────── main ────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="deferred-followup reconcile 게이트 (CFP-2381 / ADR-060 §결정 32)"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    check_p = subparsers.add_parser("check", help="registry scan + carrier-부재 검출")
    check_p.add_argument(
        "--registry", default=None,
        help="registry yaml 경로 (default: <repo-root>/docs/evidence-checks-registry.yaml)",
    )
    check_p.add_argument(
        "--repo-root", default=".",
        help="repo root 경로 (default: 현재 디렉터리)",
    )

    resolve_p = subparsers.add_parser("resolve", help="detect_command 닫힌집합 resolve 진단")
    # dest=cmd_str — subparser dest="command" 덮어쓰기 회피 (F-CR-2381-3: --command 가 args.command
    #   ("resolve") 를 clobber 해 resolve 분기 미진입하던 broken-as-written 정정).
    resolve_p.add_argument("--command", dest="cmd_str", required=True,
                           help="detect_command 값 문자열")

    args = parser.parse_args()

    if args.command == "check":
        cmd_check(args)
    elif args.command == "resolve":
        cmd_resolve(args)


if __name__ == "__main__":
    main()
