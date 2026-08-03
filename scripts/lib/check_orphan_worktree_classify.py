#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# check_orphan_worktree_classify.py — orphan 3축 분류 순수 판정 (AC-12) + gc-residue 공통 substrate
#
# Carrier: CFP-2822 Phase 2 (구현) — 세션 잔재 발견 스캐너 (ADR-169 §결정 3)
# 설계 SSOT: change-plan cfp-2822 §3.2③ / §3.5 flat sibling / §7.1 TB-3 6-guard /
#           §7.3 삭제 authz / §7.5 redaction / Story AC-12 / INV-1·2·3·9.
#
# 두 책임(§3.5 flat sibling — subpackage 신설 금지, ADR-040:1087 "scripts/lib/ 공통추출" 실현):
#   [Section A] gc-residue 공통 substrate — git/gh 포트, is_dirty(path, ignore_re),
#     age, redaction/sanitize, 경로 정규화 _norm 3단, TB-3 6-guard safe_remove,
#     등록 worktree subprocess 위임(anti-corruption). File 1/3/4 가 import 하는 base
#     (사이클 없음 — 본 모듈은 stdlib + redact_dev_process_content 만 import).
#   [Section B] orphan 3축 분류 순수 판정 + 보존 판정(상태 신호 한정) + stray checkout census.
#
# is_dirty(path, ignore_re) 위치 = 본 모듈 (Refactor I-1 — bash is_worktree_dirty 2 카피의
#   최초 Python 추출, 3번째 인라인 카피 아님). Dev-Guards 가 별도 common 모듈을 선호하면
#   1-파일 relocation 가능(음의 결합 없음).
#
# 비협상 불변식 이식:
#   INV-1  dirty/unpushed/locked/pin/INCONCLUSIVE → 자동삭제 금지 (judge_orphan).
#   INV-2  판정불능 → 항상 KEEP "network-inconclusive" (판정 못하니 삭제 절대 금지).
#   INV-3  보존 = 사유 + 나이 동반 (Verdict-like tuple 항상 reason+age).
#   TB-3   filesystem-direct 삭제(safe_remove)에만 파괴표면 가드 6종. 등록 worktree=git-mediated.
#
# ── 정직 천장 (ADR-119 / ADR-168 §결정 16 (구 ADR-082 §결정 16, 재제정 CFP-2840) Layer 1) ────────────────────────────────
#   본 모듈의 정규식은 bounded quantifier + anchor 로 작성하나, 임의·적대적 입력 무해성을
#   단정하지 않는다("ReDoS-safe" 무증거 단정 금지). 보장 = bounded degradation.
#   실증(취약입력 wall-clock 상한) = Phase 2 SecurityTest 복잡도 self-test. (§7.6 T-REGEX)

from __future__ import annotations

import fnmatch
import hashlib
import os
import re
import subprocess
import sys

# Windows cp949 stdout/stderr 인코딩 차단 (ADR-061 portability — lib/ 관용).
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# 사이블링·SSOT import 를 위한 self-dir path 보정 (thin-wrapper 이외 호출 경로 방어).
_SELF_DIR = os.path.dirname(os.path.abspath(__file__))
if _SELF_DIR not in sys.path:
    sys.path.insert(0, _SELF_DIR)

# §7.5 redaction SSOT 재사용 (secret 패턴 3번째 카피 금지). import 실패 시 **fail-closed** fallback
#   (F-SEC-004): raw 반환(fail-open) 금지 — 손상/부분배포에서 SSOT 부재 시 최소 built-in 으로
#   고신뢰 구조 secret(github PAT/AWS/GCP/Slack/PEM/generic token 대입)만 obliterate 후 반환.
#   비대칭 해소: _RE_CLOUD_STRUCT import 실패 fail-closed(obliterate)와 대칭. non-match = 원문 보존
#   (benign 경로 over-redact 회피). 최소 set = honest-ceiling — SSOT 전 rule(cookie/session_id/
#   env_dump 등) 미포함, 고신뢰 구조 토큰만 방어(ADR-119, 임의입력 무해 단정 아님).
try:
    from redact_dev_process_content import redact as _redact_secrets  # type: ignore
except Exception:  # pragma: no cover - defensive
    _FALLBACK_SECRET_RES = (
        re.compile(r"ghp_[A-Za-z0-9]{36}"),                       # github PAT
        re.compile(r"github_pat_[A-Za-z0-9_]{82}"),               # github fine-grained PAT
        re.compile(r"A(?:KIA|SIA)[0-9A-Z]{16}"),                  # AWS access key id
        re.compile(r"AIza[0-9A-Za-z_\-]{35}"),                    # Google API key
        re.compile(r"xox[baprs]-[0-9A-Za-z\-]{10,}"),             # Slack token
        re.compile(
            r"(?i)(?:api[_-]?key|secret|token|password|bearer)\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{16,}"
        ),                                                        # generic 대입형 credential
        re.compile(
            r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----.*?-----END [A-Z0-9 ]*PRIVATE KEY-----",
            re.DOTALL,
        ),                                                        # PEM private key block
    )

    def _redact_secrets(raw):  # type: ignore
        """import 실패 fail-closed fallback (F-SEC-004). 최소 built-in 고신뢰 구조 secret
        obliterate. 매치 시 audit 에 'fallback_builtin_redact'(high-conf, path-오탐 rule 아님)
        보고 → sanitize 가 obliterate 반환. non-match = 원문 보존(benign 경로 over-redact 회피)."""
        s = raw if isinstance(raw, str) else ("" if raw is None else str(raw))
        fired = False
        for _rx in _FALLBACK_SECRET_RES:
            s, _n = _rx.subn("[REDACTED:fallback]", s)
            if _n:
                fired = True
        audit = {"redaction_rules_fired": ["fallback_builtin_redact"]} if fired else {}
        return (s, audit)

# 구조 cloud key(AWS/GCP/Slack) 전용 컴파일 패턴 재사용 (secret 패턴 3번째 카피 금지 — ADR-140
#   reuse-before-write). sanitize 가 audit 상 이름이 모호한 'cloud_key'(구조 real 키와
#   entropy-gated generic 40+런[forward-slash 경로 오탐]이 redact SSOT 에서 동일 rule 이름을
#   공유 — L282/L297)를 **구조 패턴 실발화로만** 확정(disambiguate)하기 위해 사용한다.
#   None(import 실패) = disambiguator 부재 → sanitize 가 cloud_key 를 fail-closed(obliterate)로
#   처리(구조 cloud key leak 0 우선; 이 degraded 경로는 방어용, benign 경로 과-redact 만 감수).
try:
    from redact_dev_process_content import _RE_CLOUD_STRUCT  # type: ignore
except Exception:  # pragma: no cover - defensive
    _RE_CLOUD_STRUCT = None  # type: ignore


# ═══════════════════════════════ 상수 ═══════════════════════════════════════════
SCRIPT_NAME = "orphan-classify"

# 삭제 authz age 문턱 (기존 STALE_DAYS 관행 상속 — 신규 env 아님, stale.sh 동형).
STALE_DAYS = int(os.environ.get("STALE_DAYS", "7") or "7")

# is_dirty untracked 무시 패턴 기본값 (파라미터 default — GC_TEMP_IGNORE_RE 는
#   §3.6 가드-무력화 env 라 production 미노출: env 대신 인자로만 주입).
DEFAULT_IGNORE_RE = r"^\?\? (\.tmp|marketplace-snapshot\.json)"

# 사용자 명시 보존 마커 (ADR-169 §결정 3 "보존 예외 = 명시 마커"). 존재 시 pin KEEP.
PIN_MARKERS = (".gc-keep", ".residue-keep")

# git/gh 포트 override (stub 주입 — 기존 GC_GIT_BIN/GC_GH_BIN 관행 상속).
GC_GIT_BIN = os.environ.get("GC_GIT_BIN", "git")
GC_GH_BIN = os.environ.get("GC_GH_BIN", "gh")

# 파괴적 동작 preview (기존 GC_DRY_RUN 재사용 — 신규 이름 X, ModuleArch §7.2).
GC_DRY_RUN = os.environ.get("GC_DRY_RUN", "") == "1"

# clone-name 휴리스틱 (stray-scratch-leak 답습). born-safe: anchored + bounded {2,8}, 선형.
_CLONE_DIR_RE = re.compile(r"^[A-Za-z]{2,8}[0-9]+-.{1,200}$")

# workspace-root stray worktree 이름 패턴 (`_wt-*` 류 + flat cfp-NNN 류).
_WORKSPACE_STRAY_GLOBS = ("_wt-*", "wt-*", "cfp-*", "*-worktree", "*-wt")

# 제어문자 strip (CR/LF/TAB/C0/DEL — §7.5 로그 인젝션 방지).
_CTRL_RE = re.compile(r"[\x00-\x08\x09\x0a\x0b\x0c\x0d\x0e-\x1f\x7f]")


# ═══════════════════ Section A — gc-residue 공통 substrate ═══════════════════════

def _subprocess_env():
    """git/gh subprocess env — MSYS_NO_PATHCONV=1 강제 (TB-3 (4) 경로 변환 오염 차단)."""
    env = dict(os.environ)
    env["MSYS_NO_PATHCONV"] = "1"
    env.setdefault("LC_ALL", "C.UTF-8")
    return env


def _run(argv, cwd=None, timeout=30):
    """subprocess 실행 → CompletedProcess-유사 (returncode, stdout, stderr). 실패=예외 흡수."""
    try:
        return subprocess.run(
            argv,
            cwd=cwd,
            env=_subprocess_env(),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )
    except (OSError, subprocess.SubprocessError):
        return None


def _git(args, cwd=None, timeout=30):
    """git 포트 — GC_GIT_BIN override. None=실행 불가(포트 격리, hexagonal)."""
    return _run([GC_GIT_BIN, *args], cwd=cwd, timeout=timeout)


def _gh(args, cwd=None, timeout=30):
    """gh 포트 — GC_GH_BIN override. None=실행 불가. (독립 clone/orphan 은 gh-merged 판정 안 함.)"""
    return _run([GC_GH_BIN, *args], cwd=cwd, timeout=timeout)


def now_epoch():
    import time
    return int(time.time())


def path_mtime_epoch(path):
    """mtime epoch (초). 접근 불가 → None."""
    try:
        return int(os.stat(path).st_mtime)
    except OSError:
        return None


def age_seconds(path, now=None):
    """age = now_epoch - mtime_epoch (절대 epoch 뺄셈, TZ-독립). 미래 mtime → max(0,...) clamp.

    mtime 판정 불가 → None (age 미상 = 삭제 근거 불충분, 호출자가 보수 처리)."""
    mt = path_mtime_epoch(path)
    if mt is None:
        return None
    n = now_epoch() if now is None else now
    return max(0, n - mt)


def age_days(path, now=None):
    a = age_seconds(path, now=now)
    return None if a is None else a / 86400.0


def is_dirty(path, ignore_re=DEFAULT_IGNORE_RE):
    """working tree 가 dirty 인가 (data-loss 가드 — INV-1).

    Refactor I-1: bash is_worktree_dirty 2 카피의 Python 추출 (3번째 인라인 카피 아님).
    판정: `git -C <path> status --porcelain` 에서 ignore_re 매치 untracked 줄만 무시.
      · status 실패(dir 부재/비-git/접근불가) → 보수적 dirty=True (보존 = 삭제 안 함).
      · 남는 변경 0 → clean=False.
    ignore_re = 파라미터 (GC_TEMP_IGNORE_RE 는 production 미노출, test/caller 주입만)."""
    if not path or not os.path.isdir(path):
        return True  # 보수적 dirty
    cp = _git(["-C", path, "status", "--porcelain"], cwd=path)
    if cp is None or cp.returncode != 0:
        return True  # status 실패 = 보수적 dirty (data-loss 가드)
    porcelain = cp.stdout or ""
    if not porcelain.strip():
        return False
    try:
        pat = re.compile(ignore_re)
    except re.error:
        pat = re.compile(DEFAULT_IGNORE_RE)
    for line in porcelain.splitlines():
        if not line.strip():
            continue
        if not pat.search(line):
            return True  # 무시대상 아닌 변경 존재 = dirty
    return False


def unpushed_count(path):
    """로컬 전용(어느 remote 에도 없는) commit 수 (독립 clone unpushed 판정).

    반환: (count:int, inconclusive:bool).
      · remote 미설정 → push 상태 판정 불가 → inconclusive=True (INV-2 → KEEP).
      · git 실패 → inconclusive=True.
      · remote 존재 → `git log HEAD --branches --tags --not --remotes --oneline` 라인 수.

    F-CR-002 fix: 도달성 positive ref 에 **HEAD 포함**(+ --tags). 종전 `--branches` 단독은
      detached HEAD 위의 local commit 을 어느 branch 도 포함 안 해 미포착 → unpushed=0 오판 →
      독립 clone(detached+local commit)이 REMOVE 로 data-loss(도메인 class 9 회귀). HEAD 추가로
      detached local commit 도 포착. over-preserve 아님: `--not --remotes` 가 remote 도달분을
      계속 제외하므로 clean+pushed(detached at pushed HEAD 포함)는 여전히 0 → 삭제 가능(AC-12)."""
    if not path or not os.path.isdir(path):
        return (0, True)
    remotes = _git(["-C", path, "remote"], cwd=path)
    if remotes is None or remotes.returncode != 0:
        return (0, True)
    if not (remotes.stdout or "").strip():
        return (0, True)  # remote 없음 → push 여부 판정 불가 → 보존
    cp = _git(["-C", path, "log", "HEAD", "--branches", "--tags", "--not", "--remotes", "--oneline"], cwd=path)
    if cp is None or cp.returncode != 0:
        return (0, True)
    lines = [ln for ln in (cp.stdout or "").splitlines() if ln.strip()]
    return (len(lines), False)


def stash_count(path):
    """git stash 개수. git 실패 → (0, True inconclusive)."""
    if not path or not os.path.isdir(path):
        return (0, False)
    cp = _git(["-C", path, "stash", "list"], cwd=path)
    if cp is None or cp.returncode != 0:
        return (0, True)
    lines = [ln for ln in (cp.stdout or "").splitlines() if ln.strip()]
    return (len(lines), False)


def locked_signal(path):
    """`git worktree lock` 된 linked worktree 인가 (INV-1 보존 신호 — 자동삭제 금지, E4 자동 unlock 기각).

    F-CR-001 fix: 종전 orphan_state_signals/judge_orphan 은 locked 신호를 미검사(docstring 만
      언급) → git worktree lock 한 clean+pushed+aged worktree 가 REMOVE 판정 = locked 삭제
      (INV-1/AC-12 위반, 등록경로 check-worktree-stale.sh 는 KEEP 하는데 orphan 경로만 비대칭).

    판정원 = `git -C <path> worktree list --porcelain` 에서 path 자신 record 의 `locked` flag
      (등록경로 check-worktree-stale.sh L323~ `"locked"*` 와 **동일 porcelain 소스** — 양 삭제
      경로 보존신호 enum parity). 반환:
        · True  — locked 확정 → judge KEEP(사유 "locked").
        · False — non-locked 확정(목록에 있으나 locked flag 부재, 또는 독립 clone main worktree
                  = lock 불가라 목록 부재 시도 non-locked 확정) → 다른 신호로 판정 진행.
        · None  — 판정불능(git 실패/예외) → 호출자 INCONCLUSIVE→KEEP fail-safe(INV-2)."""
    if not path or not os.path.isdir(path):
        return None  # 판정불능 → fail-safe
    cp = _git(["-C", path, "worktree", "list", "--porcelain"], cwd=path)
    if cp is None or cp.returncode != 0:
        return None  # 판정불능 (INV-2)
    target = _norm(path)
    cur_path = None
    cur_locked = False
    for line in (cp.stdout or "").splitlines():
        if line.startswith("worktree "):
            # 새 record 시작 — 이전 record flush (stale.sh flush_record 동형)
            if cur_path is not None and _norm(cur_path) == target:
                return cur_locked
            cur_path = line[len("worktree "):].strip()
            cur_locked = False
        elif line == "locked" or line.startswith("locked "):
            cur_locked = True  # `locked` 단독 또는 `locked <reason>` 양형 (stale.sh "locked"* 동형)
        elif not line.strip():
            # record 경계 flush
            if cur_path is not None and _norm(cur_path) == target:
                return cur_locked
            cur_path = None
            cur_locked = False
    # 마지막 record flush (trailing 빈 줄 없을 수 있음)
    if cur_path is not None and _norm(cur_path) == target:
        return cur_locked
    return False  # 목록에 path 부재 = locked 아님 확정 (독립 clone main worktree 등)


def has_pin_marker(path):
    """사용자 명시 보존 마커(.gc-keep/.residue-keep) 존재 여부."""
    if not path or not os.path.isdir(path):
        return False
    return any(os.path.exists(os.path.join(path, m)) for m in PIN_MARKERS)


def has_git_dir(path):
    """.git (dir 또는 gitfile) 존재 — clone/worktree/export vs 빈 껍데기 구분."""
    if not path or not os.path.isdir(path):
        return False
    return os.path.exists(os.path.join(path, ".git"))


# ── redaction/sanitize (§7.5 마스킹 3지점) ────────────────────────────────────────
def strip_control(s):
    """제어문자 strip (§7.5 control-char strip — 로그 인젝션 방지)."""
    if not isinstance(s, str):
        s = str(s)
    return _CTRL_RE.sub("", s)


def relativize_path(p):
    """★A 절대경로 → HOME 상대 + <user> 치환 (경로 노출 완화)."""
    if not isinstance(p, str):
        p = str(p)
    home = os.path.expanduser("~")
    out = p
    # normcase 비교로 case-insensitive(Windows) 접두 치환
    if os.path.normcase(out).startswith(os.path.normcase(home)):
        out = "~" + out[len(home):]
    # HOME 밖 절대경로에 남은 user 세그먼트 masking (best-effort)
    user = os.path.basename(home)
    if user:
        out = re.sub(r"(?i)([\\/])" + re.escape(user) + r"(?=[\\/])", r"\1<user>", out)
    return out


# obliterate 트리거에서 제외하는 규칙 (경로 오탐원 + 상대화 대상). 문자열 비교로 판정 —
#   redact SSOT 의 rule enum(RULE_NAMES)에 결합하지 않는다(cross-consumer blast-radius 회피).
#   abs_or_home_path : ★A relativize_path 로 이미 정보성 보존(상대화) → 전량 obliterate 대상 아님.
#   email            : §7.5 Internal 분류(상대화 대상) — 기존 계약(- {email}) 유지.
#   cloud_key        : 이름 모호 — 구조 cloud key(AWS/GCP/Slack, real)와 generic entropy 40+런
#                      (forward-slash 경로 오탐)이 redact SSOT 에서 동일 rule 이름 공유(L282/297).
#                      → 이름만으로 obliterate 하면 POSIX benign 경로가 뭉개짐. 구조 발화는
#                      _RE_CLOUD_STRUCT 로 sanitize 안에서 별도 확정(leak 0), generic-only 는 보존.
#   hex_high_entropy : 32+ hex generic 오탐(git object/sha 디렉터리·dedup key_hash 64hex 등) → 배제.
_PATH_FALSE_POSITIVE_RULES = frozenset({
    "abs_or_home_path", "email", "cloud_key", "hex_high_entropy",
})


def sanitize(s):
    """★A+★B 통합 — 경로 상대화(정보 보존) + 실 secret 발화 시에만 obliterate + control-char strip.
    ★A: 절대경로 → ~ / <user> 치환 (informative, §7.5 절대경로=Internal 상대화).
    ★B: env/파일내용이 섞여 실 secret(토큰/키/헤더/session_id 등) 발화 시에만 SSOT obliterate.
    ★C: diff/파일내용은 애초에 사유 문자열에 미포함(건수·나이·클래스만) — 호출부 계약.
    → workspace 절대경로(non-secret) 는 상대화만, 실 토큰 임베드 시에만 전량 redact.

    cross-platform 경로 오탐 fix (GAP1 — CFP-2822 Phase 2 Wave1 gap):
      redact SSOT 의 generic cloud_key(entropy-gated `[A-Za-z0-9/+=_-]{40,}`, forward-slash `/`
      포함) + hex_high_entropy 는 POSIX benign 경로(`~/.claude/worktrees/<repo>/<branch>`)를
      40+ 연속런으로 secret 오탐한다(Windows 는 normpath backslash `\\` 세그먼트 분절로 우연히
      회피 — POSIX/Linux/macOS consumer 는 live 결함, obliterate 시 어느 잔재인지 식별 불가).
      → 이름만으로 obliterate 트리거 잡지 않는다(_PATH_FALSE_POSITIVE_RULES 제외). 진짜 구조
      cloud key(AWS/GCP/Slack)는 _RE_CLOUD_STRUCT 실발화로만 확정. github_pat/api_key/auth·cookie
      헤더/PEM/session_id/RRN/env_dump/cred_subprocess 등 고신뢰 구조 규칙은 종전대로 obliterate.

    정직 천장(ADR-119): 구조 prefix 없는 bare high-entropy blob(generic/hex 만 매칭)은 sanitize
      가 obliterate 하지 않는다 — must-obliterate 목록(전부 구조 규칙)에 없고, 호출부 계약(★C)상
      사유 문자열은 경로+enum 만이라 유입 경로가 아니다(capture-time redact 가 1차 방어). benign
      경로 보존과 동일 generic 규칙을 공유하는 내재적 tension 을 정직 수용."""
    if not isinstance(s, str):
        s = "" if s is None else str(s)
    s = relativize_path(s)
    s = strip_control(s)
    try:
        red, audit = _redact_secrets(s)
        fired = set(audit.get("redaction_rules_fired", []))
        # (1) 경로 오탐 없는 고신뢰 구조 secret 규칙 1+ 발화 → 전량 obliterate(계정탈취 방지 우선).
        high_conf = fired - _PATH_FALSE_POSITIVE_RULES
        if high_conf and isinstance(red, str):
            return red
        # (2) 'cloud_key' 는 이름 모호 → 구조 패턴(AWS/GCP/Slack) 실발화로만 real 확정(leak 0).
        #     generic entropy 40+런(forward-slash benign 경로 오탐)은 구조 매칭 실패 → 보존(fall-through).
        #     _RE_CLOUD_STRUCT is None(disambiguator import 실패) = fail-closed obliterate(leak 0 우선).
        if "cloud_key" in fired and isinstance(red, str):
            if _RE_CLOUD_STRUCT is None or _RE_CLOUD_STRUCT.search(s):
                return red
    except Exception:  # pragma: no cover - defensive (redaction 실패해도 non-blocking)
        pass
    return s


# ── 경로 정규화 + TB-3 6-guard (§7.1.3 / §7.6 T-DEL-1/2) ─────────────────────────
def _norm(path):
    """normcase(normpath(realpath())) 3단 조합 (repo-confinement _norm 동형).
    realpath = symlink/junction 해소 + UNC/8.3 흡수, normcase = case 일관(CFP-2799
    case-dead-branch 이식 금지: 비교 양변 동일 정규화)."""
    try:
        rp = os.path.realpath(path)
    except OSError:
        rp = path
    return os.path.normcase(os.path.normpath(rp))


def is_within_root(path, root):
    """path 가 root 의 진짜 하위(root 자신 아님)인지 — fail-closed 경로 봉쇄.
    문자열 prefix 매칭 금지 → _norm 3단 후 세그먼트 경계(os.sep) 포함 판정."""
    try:
        np = _norm(path)
        nr = _norm(root)
    except Exception:
        return False  # fail-closed
    if not np or not nr:
        return False
    if np == nr:
        return False  # root 자신 삭제 금지
    return np.startswith(nr + os.sep)


def is_symlink_or_reparse(path):
    """symlink/junction/reparse-point 여부 (TB-3 (2) — 삭제 대상 원천 제외)."""
    try:
        if os.path.islink(path):
            return True
    except OSError:
        return True  # 판정 불가 → 보수적 제외
    # Windows reparse-point (junction 은 islink 로 안 잡힐 수 있음)
    try:
        st = os.lstat(path)
        attrs = getattr(st, "st_file_attributes", 0)
        FILE_ATTRIBUTE_REPARSE_POINT = 0x400
        if attrs & FILE_ATTRIBUTE_REPARSE_POINT:
            return True
    except (OSError, AttributeError):
        pass
    return False


def safe_remove(path, allowed_roots, dry_run=None, recheck_inv1=False):
    """TB-3 filesystem-direct 삭제 — 파괴표면 가드 6종 강제.

    가드 6종 (§7.1.3 / §7.6):
      (1) realpath 강제 해소 후 표준 prefix 재검증 (is_within_root 안 _norm realpath).
      (2) junction/symlink/reparse-point 삭제대상 제외 (거부).
      (3) normcase+normpath+realpath allowlist fail-closed (문자열 prefix 매칭 금지).
      (4) MSYS_NO_PATHCONV=1 강제 (_subprocess_env — git 경로 오염 차단; 순수 os 삭제엔 무해).
      (5) 변수 인용 + 빈변수 가드 (Python: 빈/공백/상대경로 거부).
      (6) filesystem-direct 전용 (등록 worktree=git-mediated 은 discover 에서 제외 — 여기 미도달).

    IDEM-3 double-delete 0: 삭제 직전 존재 재확인 + 이미-부재 = no-op 성공 + graceful.
    recheck_inv1 (F-SEC-002 TOCTOU): True 면 실 삭제 직전 judge_orphan 재호출로 INV-1 보존
      신호(dirty/unpushed/locked/pin/stash/INCONCLUSIVE)를 재검사 — 판정 직후 상태 변화 시
      삭제 ABORT(KEEP 방향). IDEM-3 존재 재확인과 별개 layer(존재≠상태). 기존 judge 로직
      재사용(별 신설 0). git_exists 는 path 로 재도출(source 는 judge_orphan 미사용).
    반환: (removed:bool, note:str). note = 사유 요약 (secret/절대경로 미포함 — sanitize).
    """
    dr = GC_DRY_RUN if dry_run is None else dry_run

    # (5) 빈변수 가드
    if not path or not str(path).strip():
        return (False, "guard-reject: empty-path")
    if not os.path.isabs(path):
        return (False, "guard-reject: not-absolute")

    # (2) symlink/junction/reparse 거부
    if is_symlink_or_reparse(path):
        return (False, "guard-reject: symlink-or-reparse")

    # (1)(3) allowlist fail-closed — 어느 allowed_root 의 진짜 하위여야 함
    if not any(is_within_root(path, r) for r in (allowed_roots or [])):
        return (False, "guard-reject: outside-allowlist")

    # IDEM-3: 존재 재확인 (이미 사라짐 = no-op 성공, double-delete 0)
    if not os.path.exists(path):
        return (False, "skip: already-absent")

    if dr:
        return (False, "dry-run: would-remove")

    # (F-SEC-002) 실 삭제 직전 INV-1 재검증 — 판정~삭제 사이 상태 변화(dirty/unpushed/locked/
    #   pin/stash/INCONCLUSIVE 신규 발생) 시 삭제 ABORT. 기존 judge_orphan 재사용(별 신설 0).
    #   IDEM-3(존재 재확인)와 별개 layer. judge_orphan 은 source 미사용 → git_exists 만 재도출.
    if recheck_inv1:
        try:
            decision, _r, _a = judge_orphan(path, None, has_git_dir(path))
        except Exception:  # pragma: no cover - defensive: 재검증 실패 = 보수적 ABORT
            return (False, "abort: toctou-recheck-failed")
        if decision != "REMOVE":
            return (False, "abort: toctou-state-changed")

    # graceful filesystem-direct 삭제
    try:
        import shutil
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)
        return (True, "removed")
    except OSError as e:
        return (False, "remove-failed: %s" % strip_control(str(e))[:120])


# ── 등록 worktree 축 = 기존 스크립트 subprocess 위임 (anti-corruption) ─────────────
def list_registered_worktrees(repo_root=None):
    """`git worktree list --porcelain` 위임 → 등록 worktree path 집합 (_norm 정규화).

    파싱 로직 재구현 금지 (ModuleArch §13(3) circular import 원천차단) — path 라인만 추출.
    실패 → 빈 set (등록 판정 불능 시 discover 가 보수 처리)."""
    cp = _git(["-C", repo_root or ".", "worktree", "list", "--porcelain"], cwd=repo_root)
    if cp is None or cp.returncode != 0:
        return set()
    roots = set()
    for line in (cp.stdout or "").splitlines():
        if line.startswith("worktree "):
            p = line[len("worktree "):].strip()
            if p:
                roots.add(_norm(p))
    return roots


def registered_main_worktree(repo_root=None):
    """`git worktree list --porcelain` 첫 entry = main checkout path (정규화 전 원본)."""
    cp = _git(["-C", repo_root or ".", "worktree", "list", "--porcelain"], cwd=repo_root)
    if cp is None or cp.returncode != 0:
        return None
    for line in (cp.stdout or "").splitlines():
        if line.startswith("worktree "):
            return line[len("worktree "):].strip()
    return None


def key_hash(abs_path, reason_class):
    """재알림 dedup key = sha256(abs_path|reason_class) (§3.4)."""
    raw = "%s|%s" % (abs_path or "", reason_class or "")
    return hashlib.sha256(raw.encode("utf-8", errors="replace")).hexdigest()


# ═══════════════════ Section B — orphan 3축 분류 + 보존 판정 ═══════════════════════

def matches_residue_pattern(name, source):
    """discover 후보 필터 — 임의 dir 아닌 잔재 의심 이름만 (born-broken glob 방어).
    source 별: workspace-root=_wt-*/cfp-* 류 / home-direct=clone 휴리스틱(.git 별도 확인)."""
    if source == "workspace-root":
        return any(fnmatch.fnmatch(name, g) for g in _WORKSPACE_STRAY_GLOBS)
    if source == "home-direct":
        return bool(_CLONE_DIR_RE.match(name))
    # worktrees-base 하위는 전량 후보 (등록부 cross-check 로 제외)
    return True


def classify_orphan(path, source):
    """3축 분류 순수 판정 (AC-12) — 분류 신호로만, 삭제 여부 미결정.

    반환 dict: {path, source, registered(bool), git_exists(bool), needs_state_check(bool)}.
      · registered = 등록 worktree 집합 대조는 orchestrator(discover)가 수행 →
        여기선 False 고정(미등록 후보만 도달). git_exists = .git 유무.
      · needs_state_check = git_exists (git 보유 시 상태검사 필요, 빈껍데기는 age-only)."""
    git_exists = has_git_dir(path)
    return {
        "path": path,
        "source": source,
        "registered": False,
        "git_exists": git_exists,
        "needs_state_check": git_exists,
    }


def orphan_state_signals(path):
    """orphan/clone 상태 신호 수집 (독립 clone/미등록 git dir — gh-merged 판정 안 함,
    Refactor I-2 merged_pr_head 재사용 금지: PR lifecycle 부재). dirty/unpushed/stash 만."""
    dirty = is_dirty(path)
    up_count, up_inconc = unpushed_count(path)
    st_count, st_inconc = stash_count(path)
    pin = has_pin_marker(path)
    locked = locked_signal(path)  # True(locked)/False(non-locked)/None(판정불능)
    return {
        "dirty": dirty,
        "unpushed": up_count,
        "stash": st_count,
        "pin": pin,
        "locked": locked is True,
        # locked 판정불능(None) → INCONCLUSIVE 합류(INV-2 fail-safe KEEP). 정상 git repo 는
        #   worktree list 성공 → True/False 확정이라 기존 REMOVE 케이스 회귀 없음.
        "inconclusive": up_inconc or st_inconc or (locked is None),
        "age": age_seconds(path),
    }


def judge_orphan(path, source, git_exists):
    """orphan 보존/삭제 판정 (INV-1/2/3 이식). 순수 함수 (삭제 syscall 0 — orchestrator execute 소관).

    반환 (decision:'KEEP'|'REMOVE', reason:str|None, age:int|None).
    보존 트리거 = 상태 신호(dirty/unpushed/locked/pin/INCONCLUSIVE) 1+ 양성 또는
      판정불능 fail-safe 보존 + 메타파일 사유. 등록·존재 여부 자체 ≠ 보존 사유(AC-12 핵심).
    """
    age = age_seconds(path)
    age_ok = (age is not None) and (age > STALE_DAYS * 86400)

    # (0) pin 마커 (등록/존재 무관 — 명시 보존 예외)
    if has_pin_marker(path):
        return ("KEEP", "pin", age)

    if git_exists:
        sig = orphan_state_signals(path)
        # (INV-2) 판정불능 → 항상 KEEP (삭제 절대 금지)
        if sig["inconclusive"]:
            return ("KEEP", "network-inconclusive", age)
        # (INV-1) 상태 신호 1+ → 보존
        if sig["dirty"]:
            return ("KEEP", "dirty", age)
        if sig.get("locked"):
            # (F-CR-001) git worktree lock → 명시 보존 (자동 unlock/force-remove 금지, E4)
            return ("KEEP", "locked", age)
        if sig["unpushed"] > 0:
            return ("KEEP", "unpushed-%d" % sig["unpushed"], age)
        if sig["stash"] > 0:
            # stash = 미커밋 로컬 작업 상태 → dirty 계열 보존 (enum: dirty)
            return ("KEEP", "dirty", age)
        # 전부 음성 + assessable — 독립 clone/미등록 git dir
        if not age_ok:
            # 나이 미도달 → 보수 보존 (mtime 단독 삭제 금지 상보, T-DEL-3)
            return ("KEEP", "unregistered-location", age)
        # 전부 음성 + 나이 도달 → filesystem 삭제 후보 (§7.3 "전부 음성만")
        return ("REMOVE", None, age)

    # 빈 껍데기 (git 부재) = age + canonical 후 안전삭제 (§7.3)
    if age is None:
        # mtime 미상 = age 판정 불가 → 보수 보존
        return ("KEEP", "unregistered-location", age)
    if not age_ok:
        return ("KEEP", "unregistered-location", age)
    return ("REMOVE", None, age)


def census_stray_checkouts(paths):
    """stray checkout census 흡수 — 미등록 git 체크아웃 개수·최고령 age 집계 (가시화, 삭제 0)."""
    entries = []
    oldest = 0
    for p in paths:
        if has_git_dir(p):
            a = age_seconds(p) or 0
            oldest = max(oldest, a)
            entries.append((p, a))
    return {"count": len(entries), "oldest_age": oldest, "entries": entries}


# ═══════════════════════════════ standalone main ═══════════════════════════════════
def main(argv=None):
    """standalone 진입 (§3.5 축 격리 — File1 미경유 독립 실행/테스트용).
    단일 root 하위 미등록 후보를 분류·판정해 stderr advisory 출력. always exit 0."""
    import argparse
    ap = argparse.ArgumentParser(description="orphan worktree/clone 3축 분류 (advisory)")
    ap.add_argument("--root", required=True, help="스캔 root (미등록 후보 상위)")
    ap.add_argument("--source", default="home-direct",
                    choices=["workspace-root", "home-direct", "worktrees-base"])
    args = ap.parse_args(argv)

    root = os.path.expanduser(args.root)
    kept = removed = 0
    try:
        names = os.listdir(root)
    except OSError:
        print("[%s] DONE: kept=0 removed=0 (root 접근불가)" % SCRIPT_NAME)
        return 0
    for name in sorted(names):
        full = os.path.join(root, name)
        if not os.path.isdir(full):
            continue
        if not matches_residue_pattern(name, args.source):
            continue
        cls = classify_orphan(full, args.source)
        decision, reason, age = judge_orphan(full, args.source, cls["git_exists"])
        if decision == "KEEP":
            kept += 1
            ad = "" if age is None else " age=%dd" % (age // 86400)
            print("[%s] KEEP (%s):%s %s" % (SCRIPT_NAME, sanitize(reason or "none"), ad,
                                            sanitize(full)), file=sys.stderr)
        else:
            removed += 1
            print("[%s] REMOVE-candidate: %s" % (SCRIPT_NAME, sanitize(full)), file=sys.stderr)
    print("[%s] DONE: kept=%d removed=%d" % (SCRIPT_NAME, kept, removed))
    return 0


if __name__ == "__main__":
    sys.exit(main())
