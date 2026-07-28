#!/usr/bin/env bash
# CFP-2822 Phase 2 — sanitize/redaction discriminating self-test (§7.5)
#
# 계약 SSOT: change-plan cfp-2822 §7.5 (마스킹 3지점 — ★A 상대화 / ★B secret obliterate /
#           ★C diff 미포함) / §7.6 T-INFO/LOG/SECRET / INV (secret leak 0).
# 대상 production: scripts/lib/check_orphan_worktree_classify.py (sanitize / relativize_path / strip_control).
#
# intended 계약 (병렬 DeveloperAgent 가 cross-platform 수정 중):
#   · benign forward-slash 경로 ~/.claude/worktrees/<repo>/<branch> → **relativized 정보 보존**
#     (worktrees·branch 세그먼트 잔존, `[REDACTED:*]` 로 뭉개지면 FAIL — 어느 잔재인지 식별 불가).
#   · benign backslash 경로 → 동일 (정보 보존).
#   · ghp_+36자 GitHub PAT → **obliterate** (raw 토큰 미출현, [REDACTED] 치환, leak 0).
#   · AKIA+16 AWS key → **obliterate** (raw key 미출현, leak 0).
#
# anti-theater: 정보보존(non-secret)과 obliterate(secret)를 양방향 변별 — 둘 다 뭉개거나 둘 다
#   보존하면 한쪽이 FAIL. secret leak = raw 토큰 substring 부재로 강하게 입증.
# ※ 작성 시점 benign-fwd(실 repo명 긴 경로)가 cloud_generic 엔트로피 오탐으로 [REDACTED:cloud_key]
#   클로버되면 = sanitize cross-platform 수정 대기 RED (계약대로 작성 완료 — 수정 후 GREEN).
#
# Exit: 0 (all pass) / 1 (any fail).

set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
export CFP2822_LIBDIR="$REPO_ROOT/scripts/lib"
PY="${PYTHON:-python3}"; command -v "$PY" >/dev/null 2>&1 || PY=python

"$PY" - <<'PY'
import sys, os
sys.path.insert(0, os.environ["CFP2822_LIBDIR"])
import check_orphan_worktree_classify as m

PASS = FAIL = 0
def ok(x):
    global PASS; PASS += 1; print("PASS: " + x)
def bad(x, d=""):
    global FAIL; FAIL += 1; print("FAIL: " + x + (("  " + d) if d else ""))

home = os.path.expanduser("~")

# ── (1) benign forward-slash 경로 → relativized 정보 보존 (intended; 수정 대기 시 RED) ──
p_fwd = home + "/.claude/worktrees/plugin-codeforge/cfp-2822-phase2"
out = m.sanitize(p_fwd)
if "[REDACTED" in out:
    bad("§7.5 benign fwd-slash 경로 정보 보존 (수정 대기 RED — cloud_generic 오탐 클로버)",
        "out=%r (relativized 정보 보존 기대, [REDACTED] 금지)" % out)
elif out.startswith("~") and "worktrees" in out and "cfp-2822-phase2" in out:
    ok("§7.5 benign fwd-slash → relativized 정보 보존 (~/…worktrees…cfp-2822-phase2, obliterate 0)")
else:
    bad("§7.5 benign fwd-slash relativize 기대", "out=%r" % out)

# ── (2) benign backslash 경로 → relativized 정보 보존 ──
p_back = home + "\\.claude\\worktrees\\myrepo\\cfp-99-branch"
out = m.sanitize(p_back)
if "[REDACTED" in out:
    bad("§7.5 benign backslash 경로 정보 보존 (수정 대기 RED)", "out=%r" % out)
elif out.startswith("~") and "worktrees" in out and "cfp-99-branch" in out:
    ok("§7.5 benign backslash → relativized 정보 보존 (obliterate 0)")
else:
    bad("§7.5 benign backslash relativize 기대", "out=%r" % out)

# ── (3) ghp_+36 GitHub PAT → obliterate (raw 미출현, leak 0) ──
tok = "ghp_" + ("A" * 36)
inp = "leftover token=%s in reason" % tok
out = m.sanitize(inp)
if tok not in out and "[REDACTED" in out:
    ok("§7.5 ghp_+36 → obliterate (raw 토큰 미출현 + [REDACTED] 치환, leak 0)")
else:
    bad("§7.5 ghp_ obliterate 기대 (raw 미출현)", "out=%r" % out)

# ── (4) AKIA+16 AWS key → obliterate ──
akey = "AKIA" + "IOSFODNN7EXAMPLE"   # AKIA + 16
inp = "aws creds %s embedded" % akey
out = m.sanitize(inp)
if akey not in out and "[REDACTED" in out:
    ok("§7.5 AKIA+16 AWS key → obliterate (raw key 미출현, leak 0)")
else:
    bad("§7.5 AKIA obliterate 기대 (raw 미출현)", "out=%r" % out)

# ── (5) control-char strip (로그 인젝션 방지) — CR/LF/TAB 제거 ──
inp = "path\r\n[stale-check] FORGED\tINJECT"
out = m.sanitize(inp)
if "\r" not in out and "\n" not in out and "\t" not in out:
    ok("§7.5 control-char strip: CR/LF/TAB 제거 (로그 인젝션 방지)")
else:
    bad("§7.5 control-char strip 기대", "out=%r" % out)

print("")
print("HARNESS-SUMMARY PASS=%d FAIL=%d" % (PASS, FAIL))
sys.exit(0 if FAIL == 0 else 1)
PY
ec=$?
echo "============================================"
echo "sanitize/redaction self-test — exit=$ec"
echo "============================================"
exit $ec
