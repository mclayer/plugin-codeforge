#!/usr/bin/env bash
# tests/scripts/test_declared_tier_vs_actual.sh
# CFP-2984 Phase 2 (구현 lane) — AC-16 discriminating self-test.
#
# AC-16: Story §5.3 이 선언한 **tier 분포 수치** 를 **AC 표 실측 재계수** 와 대조하고,
#   「검증 수단의 required 경계」 선언의 **수단 집합** 을 **실제 required 컨텍스트 집합** 과
#   대조한다. 둘 다 일치해야 하고, required 밖 수단이 커버 선언 없이 남은 건수 = 0 이며,
#   **선언 수치나 커버 선언이 부재·파싱 불가면 통과가 아니라 실패(fail-closed)** 다.
#
# ★★ born-RED 가 정답 (Change Plan §8.2-C / Story §7.8):
#   현행 Story 는 E2(§5.3 stale 수치)가 **미해소**다. 따라서 실 Story 에 대해 이 오라클은
#   **정당하게 RED** 이며, **GREEN 이 나오면 그 오라클이 hollow** 인 것이다.
#   ⇒ 본 스크립트는 실 Story leg 을 **정보성 보고**로 두고(강제 assert 아님), pass/fail 은
#     픽스처 기반 discriminating leg 으로 판정한다. 이유 2가지:
#       (a) 실 Story 는 **internal-docs repo** 소재라 wrapper CI 정의역 밖 — 도달 불가할 수 있다.
#       (b) 실 Story 를 "RED 여야 한다" 로 못박으면 E2 를 고치는 순간 테스트가 깨지는
#           change-detector 가 된다. AC 의 verdict(RED)는 **보고 사실**이고, 본 테스트가
#           지키는 것은 **오라클의 검출력**이다. 이 분리를 숨기지 않는다.
#
# ★ 정의역 (Change Plan §8.2-C):
#   포함 = Story `### 5.3 AC 표` ~ `#### 5.3.2` 직전 (AC 표 + §5.3.1 정본 요약표 + 「검증
#          수단의 required 경계」 블록). 내구 앵커 = **절 이름**(줄번호 아님 — 편집으로 이동한다).
#   제외 = §9 iteration 기록(시점 동결 이력) ∪ 정의역 내 **fenced code block**(iter2 재현 명령
#          출력 기록 = 이력성). 이력을 고치라고 강요하면 부조리가 된다.
#          ⚠ 정직: fence 제외는 "fence 안에 stale 수치를 숨기면 안 잡힌다" 는 잔여를 남긴다.
#             이 잔여를 은닉하지 않고 declare 한다(§7.8 권고 = fence 안 값에 시점 라벨 부착).
#
# 3방향 mutant (전부 픽스처 실변형):
#   ① 제거      M1 = 「required 경계」 커버 선언 블록 삭제      → fail-closed RED
#               M1b = §5.3.1 요약표 tier 행 삭제                → fail-closed RED
#   ② 주입      M2 = 선언 tier 수치 위조(normative 30→31)      → RED
#               M2b = required 선언 집합에서 context 1개 누락    → RED
#   ③ 등가변형  M3 = 수치를 **표 밖 산문으로 이동**(요약표 행 제거 + 산문 기재) → fail-closed RED
#               M3b = 산문 stale 주장 주입("normative 23건")     → RED
#
# 대조군(INV-T4): 정합 픽스처 = PASS (수치·집합 전건 일치).
# INV-T3 순수 픽스처: 네트워크 0 · 실 ~/.claude/** 0 · 실 git 원격 0 · 쓰기는 mktemp -d 내부만.
# Exit 0 = 전 케이스 PASS.

set -euo pipefail
export PYTHONIOENCODING=utf-8

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
CLAUDE_MD="$REPO_ROOT/CLAUDE.md"
PASS=0
FAIL=0
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

# ─────────────────────────────────────────────────────────────────────────────
cat > "$WORK/checker.py" <<'PY'
#!/usr/bin/env python3
"""AC-16 선언 tier 분포·required 경계 ↔ 실측 대조 (fail-closed).

사용: checker.py <story-path> <claude-md-path>
"""
import re
import sys

DOMAIN_START = r"^### 5\.3 AC 표\s*$"
DOMAIN_END = r"^#### 5\.3\.2"
AC_ROW = re.compile(r"^\|\s{0,2}(AC-\d{1,3}[a-z]?)\s{0,2}\|(.*)\|\s{0,2}$")
SUMMARY_ROW = re.compile(
    r"^\|\s{0,2}\**\s{0,2}([^|]{1,40}?)\s{0,2}\**\s{0,2}\|\s{0,2}\**\s{0,2}(\d{1,4})\s{0,2}\**\s{0,2}\|"
)
# 정의역 내 산문 tier 주장 — "normative N건" / "N개 normative" / "N건의 normative"
PROSE_TIER = re.compile(r"normative\s{0,2}(\d{1,3})\s{0,2}건|(\d{1,3})\s{0,2}개\s{0,2}normative")
LIMIT_NOTE = re.compile(r"머지\s?비차단|머지를\s?막지|머지\s?차단력\s?한계")
REQUIRED_DECL = re.compile(r"8-tuple\s{0,2}=\s{0,2}(.+?)이며", re.DOTALL)
CTX_TOKEN = re.compile(r"`([^`]{3,80})`")
CLAUDE_ROW = re.compile(r"wrapper \(plugin-codeforge\)\s{0,2}\|\s{0,2}`(\[[^`]{10,2000}\])`")

SUMMARY_KEYS = {
    "AC 총수": "total",
    "tier: normative": "normative",
    "tier: advisory": "advisory",
    "tier: declared": "declared",
    "source: user": "user",
    "source: derived": "derived",
}


def strip_fences(text):
    """정의역 내 fenced code block 제거 (이력 기록 — §8.2-C 명시 제외)."""
    return re.sub(r"^```.*?^```", "", text, flags=re.DOTALL | re.MULTILINE)


def extract_domain(text):
    lines = text.split("\n")
    s = e = None
    for i, l in enumerate(lines):
        if s is None and re.match(DOMAIN_START, l):
            s = i
        elif s is not None and re.match(DOMAIN_END, l):
            e = i
            break
    if s is None:
        return None
    return "\n".join(lines[s:e if e is not None else len(lines)])


def recount(domain):
    """§5.3 AC 표 전수 재계수 (파서 산출 — 눈으로 세지 않음)."""
    rows, seen = [], set()
    in_table = False
    for line in domain.split("\n"):
        m = AC_ROW.match(line.strip())
        if not m:
            # AC 표는 §5.3.1 헤딩 전까지. 요약표는 첫 cell 이 AC-ID 가 아니라 미매칭.
            if line.startswith("#### 5.3.1"):
                in_table = False
            continue
        in_table = True
        ac_id, rest = m.group(1), m.group(2)
        cells = [c.strip() for c in rest.split("|")]
        if len(cells) < 6:
            continue
        source, tier = cells[1], cells[-1]
        rows.append({"id": ac_id, "source": source, "tier": tier, "raw": rest})
        seen.add(ac_id)
    counts = {
        "total": len(rows),
        "normative": sum(1 for r in rows if r["tier"] == "normative"),
        "advisory": sum(1 for r in rows if r["tier"] == "advisory"),
        "declared": sum(1 for r in rows if r["tier"] == "declared"),
        "user": sum(1 for r in rows if r["source"] == "user"),
        "derived": sum(1 for r in rows if r["source"] == "derived"),
    }
    limit_rows = [r["id"] for r in rows if LIMIT_NOTE.search(r["raw"])]
    dup = len(rows) - len(seen)
    return rows, counts, limit_rows, dup


def parse_summary(domain):
    """§5.3.1 정본 요약표의 선언 수치."""
    decl = {}
    for line in domain.split("\n"):
        m = SUMMARY_ROW.match(line.strip())
        if not m:
            continue
        label = m.group(1).strip().strip("*`").strip()
        for key, canon in SUMMARY_KEYS.items():
            if label == key or label.replace(" ", "") == key.replace(" ", ""):
                decl[canon] = int(m.group(2))
    return decl


def parse_required_decl(domain):
    m = REQUIRED_DECL.search(domain)
    if not m:
        return None
    return [t.strip() for t in CTX_TOKEN.findall(m.group(1))]


def parse_actual_required(claude_text):
    m = CLAUDE_ROW.search(claude_text)
    if not m:
        return None
    return re.findall(r'"([^"]{3,80})"', m.group(1))


def main():
    story_path, claude_path = sys.argv[1], sys.argv[2]
    with open(story_path, encoding="utf-8") as f:
        story = f.read()
    with open(claude_path, encoding="utf-8") as f:
        claude_text = f.read()

    violations = []
    domain_raw = extract_domain(story)
    if domain_raw is None:
        print("VIOLATION: Story `### 5.3 AC 표` 절 부재 — 정의역 미해소 (fail-closed)")
        sys.exit(1)
    domain = strip_fences(domain_raw)

    rows, counts, limit_rows, dup = recount(domain)
    if counts["total"] == 0:
        violations.append("AC 표 행 0 건 — 실측 재계수 불가 (fail-closed)")
    if dup:
        violations.append("AC-ID 중복 %d 건 — 재계수 정본 붕괴" % dup)

    # (A) 선언 tier 분포 ↔ 실측 재계수
    decl = parse_summary(domain)
    missing = [k for k in ("total", "normative", "advisory", "declared", "user", "derived")
               if k not in decl]
    if missing:
        violations.append(
            "§5.3.1 정본 요약표에서 선언 수치 미해소: %s — 부재·파싱 불가는 통과가 아니라 "
            "실패 (fail-closed). 수치를 표 밖 산문으로 옮기면 여기서 걸린다" % missing)
    for k, v in sorted(decl.items()):
        if counts.get(k) is not None and v != counts[k]:
            violations.append(
                "선언-실측 불일치 [%s]: 요약표 선언 %d ≠ AC 표 실측 재계수 %d" % (k, v, counts[k]))
    # 파티션 정합 (독립 교차 검증)
    if counts["total"] and counts["normative"] + counts["advisory"] + counts["declared"] != counts["total"]:
        violations.append("tier 파티션 불성립: n+a+d=%d ≠ total=%d"
                          % (counts["normative"] + counts["advisory"] + counts["declared"],
                             counts["total"]))
    if counts["total"] and counts["user"] + counts["derived"] != counts["total"]:
        violations.append("source 파티션 불성립: u+d=%d ≠ total=%d"
                          % (counts["user"] + counts["derived"], counts["total"]))

    # (B) 정의역 내 산문 tier 주장 ↔ 실측 (stale 자기 셀 검출)
    for m in PROSE_TIER.finditer(domain):
        val = int(m.group(1) or m.group(2))
        if val != counts["normative"]:
            ctx = domain[max(0, m.start() - 55):m.end() + 25].replace("\n", " ")
            violations.append(
                "정의역 내 산문 normative 주장 %d ≠ 실측 %d — stale 선언 | …%s…"
                % (val, counts["normative"], ctx.strip()))

    # (C) 커버 선언 산식: 나머지 N건 = normative − 한계 표기 행수
    cover = re.search(r"나머지\s{0,2}\**\s{0,2}(\d{1,3})\s{0,2}\**\s{0,2}건", domain)
    if cover is None:
        violations.append(
            "「검증 수단의 required 경계」 커버 선언(‘나머지 N건’) 부재 — required 밖 수단을 "
            "커버하는 선언이 없다 (fail-closed)")
    else:
        expected = counts["normative"] - len(limit_rows)
        if int(cover.group(1)) != expected:
            violations.append(
                "커버 선언 산식 불일치: 선언 %s건 ≠ normative %d − 개별 한계 표기 %d = %d "
                "(한계 표기 행 %s)"
                % (cover.group(1), counts["normative"], len(limit_rows), expected, limit_rows))

    # (D) 선언 수단 집합 ↔ 실제 required 컨텍스트 집합
    declared_ctx = parse_required_decl(domain)
    actual_ctx = parse_actual_required(claude_text)
    if actual_ctx is None:
        violations.append("CLAUDE.md wrapper required contexts 행 파싱 불가 — fail-closed")
    elif declared_ctx is None:
        violations.append("Story 「검증 수단의 required 경계」 8-tuple 선언 부재 — fail-closed")
    else:
        d, a = set(declared_ctx), set(actual_ctx)
        if d != a:
            violations.append(
                "required 컨텍스트 집합 불일치 — 선언에만 %s / 실제에만 %s"
                % (sorted(d - a) or "없음", sorted(a - d) or "없음"))
        if len(actual_ctx) != 8:
            violations.append("실제 required 컨텍스트 %d 개 (선언 문면은 8-tuple) — 선언 stale"
                              % len(actual_ctx))

    print("실측 재계수: total=%d normative=%d advisory=%d declared=%d user=%d derived=%d "
          "| 한계표기 행=%s" % (counts["total"], counts["normative"], counts["advisory"],
                              counts["declared"], counts["user"], counts["derived"], limit_rows))
    print("선언 요약표: %s" % (dict(sorted(decl.items())) or "없음"))
    for v in violations:
        print("VIOLATION: %s" % v)
    if violations:
        print("")
        print("check-declared-tier-vs-actual: %d violation" % len(violations))
        sys.exit(1)
    print("check-declared-tier-vs-actual: PASS — 선언 == 실측 ∧ required 집합 일치")
    sys.exit(0)


if __name__ == "__main__":
    main()
PY

# ─────────────────────────────────────────────────────────────────────────────
# 정합 픽스처 — 실 Story 구조를 축약 재현 (AC 4행, 요약표, required 경계 선언)
#   수치는 픽스처 자신의 AC 표와 정합: total 4 / normative 2 / advisory 1 / declared 1
#                                       user 2 / derived 2, 한계표기 1행 → 나머지 1
# ─────────────────────────────────────────────────────────────────────────────
REQ_LIST='`phase-gate-mergeable` · `invariant-check` · `doc frontmatter schema (CFP-28 — strict)` · `doc section schema (CFP-28 — strict)` · `check-gate` · `ac-traceability-matrix` · `css structural lint (stylelint, warning-tier)` · `css-lint discriminating test (mutation 생존 0)`'

build_fixture() {
  local dst="$1"
  mkdir -p "$(dirname "$dst")"
  cat > "$dst" <<FIX
# 픽스처 Story

### 5.3 AC 표

| id | statement | source | verification | coverage_required | phase | tier |
|---|---|---|---|---|---|---|
| AC-1 | 서술 | user | \`tests/scripts/test_a.sh\` | Y | 2 | normative |
| AC-2 | 서술 | derived | \`tests/scripts/test_b.sh\` — **한계 명시: 8-tuple 밖이라 실패해도 머지 비차단** | Y | 2 | normative |
| AC-3 | 서술 | user | 사람 검토 | N | 1 | advisory |
| AC-4 | 서술 | derived | 선언만 | N | 2 | declared |

> ★ **검증 수단의 required 경계 (일괄 선언 — AC-16 검사 대상)**
>
> 본 픽스처가 신설하는 검증 수단은 전건 branch protection 8-tuple 밖이다. 8-tuple = ${REQ_LIST} 이며, 본 픽스처가 발의하는 \`tests/scripts/test_*.sh\` 계열은 하나도 포함되지 않는다.
>
> 실측: normative 2건 중 개별 행에 머지 차단력 한계를 적은 것은 AC-2 1건뿐이고 나머지 **1건**(산식 = 2 − 1)을 본 일괄 선언이 커버한다.

#### 5.3.1 tier·source 전수 재계수 (게이트 파서 직접 실행 검증)

재현:

\`\`\`bash
# 이력 기록 — 정의역에서 제외된다 (iter 시점 값 normative 99건)
python3 scripts/lib/check_ac_wellformed.py story.md
\`\`\`

| 구분 | 값 | 항목 |
|---|---:|---|
| **AC 총수** | **4** | AC-1 ~ AC-4 |
| \`tier: normative\` | **2** | AC-1, AC-2 |
| \`tier: advisory\` | **1** | AC-3 |
| \`tier: declared\` | **1** | AC-4 |
| \`source: user\` | **2** | AC-1, AC-3 |
| \`source: derived\` | **2** | AC-2, AC-4 |

#### 5.3.2 오라클 3방향 mutant 배정

| AC | 오라클 기질 | ① 제거 | ② 주입 | ③ 등가변형 |
|---|---|---|---|---|
| AC-1 | x | y | z | w |

## 9. iteration 기록

iter2 시점 값: normative 99건 (시점 동결 이력 — 정의역 밖)
FIX
}

patch_fixture() {
  python3 - "$1" "$2" "$3" <<'PY'
import io, sys
path, old, new = sys.argv[1], sys.argv[2], sys.argv[3]
raw = io.open(path, encoding="utf-8").read()
if old not in raw:
    print("SETUP: mutant 앵커 미발견 %r" % old[:70], file=sys.stderr)
    sys.exit(3)
io.open(path, "w", encoding="utf-8", newline="\n").write(raw.replace(old, new, 1))
PY
}

# ─────────────────────────────────────────────────────────────────────────────
# ★ crash-as-RED 차단 (CFP-2984 G7 감사 — 실사건 회귀 방지)
#   `rc≠0 → RED` 단독 판정은 **크래시와 검출을 구별하지 못한다**. 오라클이 예외로 죽으면
#   expect=RED 인 전 케이스가 "잡았다" 로 계상되고 mutant 원장이 통째로 거짓이 된다.
#   ★ baseline 대조군은 **조건부 크래시**(검출 경로에서만 죽는 경우)를 못 잡는다 — G7 실증.
#   ★ SyntaxError·IndentationError 는 Traceback 머리글 없이 출력된다(실측) — 함께 본다.
# ─────────────────────────────────────────────────────────────────────────────
crash_marker() { # <output> → 0 = 크래시 흔적 있음
  case "$1" in
    *Traceback*|*SyntaxError*|*IndentationError*|*TabError*) return 0 ;;
  esac
  return 1
}

assert_verdict() {
  local name="$1" expect="$2" story="$3" verdict
  set +e
  CHECK_OUT="$(python3 "$WORK/checker.py" "$story" "$CLAUDE_MD" 2>&1)"
  CHECK_RC=$?
  set -e
  if crash_marker "$CHECK_OUT"; then
    echo "X   FAIL: $name — 오라클 크래시(예외). rc≠0 을 검출(RED)로 셀 수 없다"
    echo "$CHECK_OUT" | sed 's/^/    ! /'
    FAIL=$((FAIL+1)); return
  fi
  if [ "$CHECK_RC" -ne 0 ] && ! printf '%s' "$CHECK_OUT" | grep -q "VIOLATION"; then
    echo "X   FAIL: $name — RED 인데 판정 근거 마커(VIOLATION)가 없다 (무증거 RED)"
    echo "$CHECK_OUT" | sed 's/^/    ! /'
    FAIL=$((FAIL+1)); return
  fi
  verdict="PASS"; [ "$CHECK_RC" -eq 0 ] || verdict="RED"
  if [ "$verdict" = "$expect" ]; then
    echo "OK  $name (expect=$expect got=$verdict)"
    PASS=$((PASS+1))
  else
    echo "X   FAIL: $name (expect=$expect got=$verdict)"
    echo "$CHECK_OUT" | sed 's/^/    /'
    FAIL=$((FAIL+1))
  fi
}

echo "── AC-16 declared tier vs actual (+ required 경계 집합)"

# ── 대조군 ──────────────────────────────────────────────────────────────────
build_fixture "$WORK/base/story.md"
assert_verdict "baseline/정합 픽스처" PASS "$WORK/base/story.md"
echo "$CHECK_OUT" | sed 's/^/    /'

# ── ① 제거 ──────────────────────────────────────────────────────────────────
build_fixture "$WORK/m1/story.md"
patch_fixture "$WORK/m1/story.md" \
  "> 실측: normative 2건 중 개별 행에 머지 차단력 한계를 적은 것은 AC-2 1건뿐이고 나머지 **1건**(산식 = 2 − 1)을 본 일괄 선언이 커버한다." \
  "> (커버 선언 삭제됨 — MUTANT M1)"
assert_verdict "M1 ①제거: 커버 선언 블록 삭제" RED "$WORK/m1/story.md"

build_fixture "$WORK/m1b/story.md"
patch_fixture "$WORK/m1b/story.md" "| \`tier: normative\` | **2** | AC-1, AC-2 |
" ""
assert_verdict "M1b ①제거: 요약표 tier 행 삭제" RED "$WORK/m1b/story.md"

# ── ② 주입 ──────────────────────────────────────────────────────────────────
build_fixture "$WORK/m2/story.md"
patch_fixture "$WORK/m2/story.md" "| \`tier: normative\` | **2** |" "| \`tier: normative\` | **3** |"
assert_verdict "M2 ②주입: 선언 tier 수치 위조(2→3)" RED "$WORK/m2/story.md"

build_fixture "$WORK/m2b/story.md"
patch_fixture "$WORK/m2b/story.md" " · \`ac-traceability-matrix\`" ""
assert_verdict "M2b ②주입: required 선언 집합에서 context 1개 누락" RED "$WORK/m2b/story.md"

# ── ③ 등가변형 ──────────────────────────────────────────────────────────────
build_fixture "$WORK/m3/story.md"
patch_fixture "$WORK/m3/story.md" "| \`tier: normative\` | **2** | AC-1, AC-2 |
" "
본 픽스처의 normative 는 두 건이다(표 밖 산문으로 이동 — MUTANT M3).
"
assert_verdict "M3 ③등가변형: 수치를 표 밖 산문으로 이동" RED "$WORK/m3/story.md"

build_fixture "$WORK/m3b/story.md"
patch_fixture "$WORK/m3b/story.md" "#### 5.3.2 오라클" \
  "본 AC 가 normative 23건의 정직성을 지탱한다(산문 stale 주장 — MUTANT M3b).

#### 5.3.2 오라클"
assert_verdict "M3b ③등가변형: 산문 stale 주장('normative 23건') 주입" RED "$WORK/m3b/story.md"

# ── 형제 회귀 ───────────────────────────────────────────────────────────────
build_fixture "$WORK/sib/story.md"
patch_fixture "$WORK/sib/story.md" "| AC-3 | 서술 | user | 사람 검토 | N | 1 | advisory |" \
  "| AC-3 | 서술 | user | 사람 검토 | N | 1 | advisory |
| AC-5 | 서술 | user | 사람 검토 | N | 1 | advisory |"
assert_verdict "형제/AC 행 1개 추가 → 선언-실측 즉시 불일치" RED "$WORK/sib/story.md"

build_fixture "$WORK/sib2/story.md"
assert_verdict "형제/무변조 재확인 (이력 fence·§9 오탐 0)" PASS "$WORK/sib2/story.md"

# ── 실 Story leg (정보성 — assert 아님) ─────────────────────────────────────
echo ""
echo "── [정보성] 실 Story 적용 결과 — born-RED 가 정답 (Change Plan §8.2-C / Story §7.8)"
STORY_PATH="${CFP2984_STORY_PATH:-$HOME/.claude/worktrees/codeforge-internal-docs/CFP-2984-phase2/wrapper/stories/CFP-2984.md}"
if [ -f "$STORY_PATH" ]; then
  set +e
  REAL_OUT="$(python3 "$WORK/checker.py" "$STORY_PATH" "$CLAUDE_MD" 2>&1)"
  REAL_RC=$?
  set -e
  echo "$REAL_OUT" | sed 's/^/    /'
  if [ "$REAL_RC" -ne 0 ]; then
    echo "    ⇒ 실 Story verdict = RED. E2(§5.3 stale 수치) 미해소 상태의 **정답**이다."
    echo "      처방 2단: (a) 문면 정정 선결(§2-§6 write 경계 밖 → escalation E2)"
    echo "                (b) 오라클 완화 금지 — GREEN 을 만들면 그 오라클이 hollow 다."
  else
    echo "    ⇒ 실 Story verdict = GREEN. E2 가 해소됐거나 **오라클이 hollow** 다."
    echo "      GREEN 을 받아들이기 전에 위 '실측 재계수' 줄과 요약표 선언을 눈으로 대조할 것."
  fi
else
  echo "    실 Story 미도달 ($STORY_PATH) — 이 leg 은 정보성이며 판정에 기여하지 않는다."
  echo "    (Story 는 internal-docs repo 소재 = wrapper CI 정의역 밖. CFP2984_STORY_PATH 로 주입 가능)"
fi

echo ""
echo "── 결과: PASS=$PASS FAIL=$FAIL"
[ "$FAIL" -eq 0 ] || exit 1
