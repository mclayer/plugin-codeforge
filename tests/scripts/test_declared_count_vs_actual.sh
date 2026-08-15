#!/usr/bin/env bash
# tests/scripts/test_declared_count_vs_actual.sh
# CFP-2984 Phase 2 (구현 lane) — AC-6 discriminating self-test.
#
# AC-6: A 소유 ADR 본문이 **선언한 열거 항목 수** 와 그 선언이 가리키는 **실제 표 행 수** 가
#   불일치하면 실패한다. **선언 수치가 부재하거나 파싱 불가하면 통과가 아니라 실패(fail-closed).**
#
# 재사용 (ADR-140 hygiene): 오라클 골격 = `scripts/lib/check_disjoint_axis_whitelist.py` 의
#   (C1) declared-vs-actual self-consistency **동형 패턴** — 정형 선언 라인 1개 ↔ 절 안 표 row
#   count 상호 대조 + 선언 부재/중복 fail-closed. 신규 발명 아님. 그 모듈을 직접 import 하지
#   않는 이유: 대상 ADR·선언 문구·표 위치가 전혀 달라 재사용 가능한 것은 *패턴*이지 *코드*가
#   아니다(그 모듈은 ADR-170 §결정 2 전용 리터럴에 결박돼 있다).
#
# ★ 한계 명시 (over-claim 금지): 본 검사의 배선 대상 2 job(`invariant-check` 계열 / 자체 lane)
#   중 어느 것도 branch protection 8-tuple 안에 있지 않다 — **RED 를 낼 수는 있어도 머지를
#   막지는 못한다.** "게이트가 막는다" 로 읽지 말 것.
#
# 선언 site 규약 (2형):
#   Form A (정형) : 표 위 최근접 bold lead-in 안의 `선언 열거 수 = <N>` — <N> 이 아라비아 숫자가
#                   아니면 **파싱 불가 = RED**(한글 수사 "여덟" 등).
#   Form B (산문) : 표 위 최근접 bold lead-in 안에 count 토큰(`N행`/`N종`/`N건`…)이 **정확히 1개**.
#   토큰 2개 이상 = **선언 모호 → RED**(2번째 토큰을 심어 site 를 지우는 회피 차단).
#   registry 별 **최소 선언 site 수 floor** — 미달 = RED(선언 라인 통째 삭제 회피 차단).
#
# 3방향 mutant (전부 실 문서 사본에 변형 적용):
#   ① 제거      M1a = 선언 bold 라인 삭제               → floor RED
#               M1b = **오라클의 대조 로직 삭제** → 위반 픽스처가 통과 → 검출력 소실 실증
#   ② 주입      M2a = 표 row 1개 삭제 / M2b = row 1개 위조 주입 → 불일치 RED
#   ③ 등가변형  M3a = 정형 선언 수치를 한글 수사("열")로 → 파싱 불가 RED
#               M3b = 산문 선언 수치를 한글 수사("일곱 행")로 → 토큰 소실 → floor RED
#               M3c = 선언 라인에 2번째 count 토큰 주입 → 모호 RED
#
# 대조군(INV-T4): **실 repo A 소유 ADR** 무변조 = PASS.
# INV-T3 순수 픽스처: 네트워크 0 · 실 ~/.claude/** 0 · 실 git 원격 0 · 쓰기는 mktemp -d 내부만.
# Exit 0 = 전 케이스 PASS.

set -euo pipefail
export PYTHONIOENCODING=utf-8

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PASS=0
FAIL=0
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

ADR109="archive/adr/ADR-109-in-process-429-mitigation-framework.md"
ADR179="archive/adr/ADR-179-agent-salvage-bundle-handoff.md"

# ─────────────────────────────────────────────────────────────────────────────
cat > "$WORK/checker.py" <<'PY'
#!/usr/bin/env python3
"""AC-6 declared-count vs actual-table-row 대조 (fail-closed).

사용: checker.py <root> <relpath>:<min_sites> [<relpath>:<min_sites> ...]
"""
import os
import re
import sys

BOLD_LEAD = re.compile(r"^\*\*(.+?)\*\*")
FORM_A = re.compile(r"선언\s{0,2}열거\s{0,2}수\s{0,2}=\s{0,2}(\S{1,20})")
COUNT_TOKEN = re.compile(
    r"(?<![0-9])([0-9]{1,3})\s{0,2}(행|종|개|건|필드|항목|entry|window|literal|leg)"
    r"(?![0-9A-Za-z가-힣])"
)
SEP = re.compile(r"^\|[\s:\-\|]+\|$")
LEAD_LOOKBACK = 10


def table_spans(lines):
    """(start_idx, end_idx, data_row_count) 목록."""
    out, i = [], 0
    while i < len(lines):
        if lines[i].strip().startswith("|"):
            start, k, rows, seen_sep = i, i, 0, False
            while k < len(lines) and lines[k].strip().startswith("|"):
                s = lines[k].strip()
                if SEP.match(s):
                    seen_sep = True
                elif seen_sep:
                    rows += 1
                k += 1
            out.append((start, k, rows))
            i = k
        else:
            i += 1
    return out


def nearest_lead(lines, start):
    """표 위 최근접 bold lead-in. heading·다른 표를 만나면 중단."""
    for j in range(start - 1, max(-1, start - 1 - LEAD_LOOKBACK), -1):
        s = lines[j].strip()
        if s.startswith("#") or s.startswith("|"):
            return None
        m = BOLD_LEAD.match(s)
        if m:
            return j, m.group(1)
    return None


def scan(path):
    """(sites, violations). site = dict(line, form, declared_raw, declared, actual)."""
    sites, viol = [], []
    with open(path, encoding="utf-8") as f:
        lines = f.read().split("\n")
    for start, _end, rows in table_spans(lines):
        lead = nearest_lead(lines, start)
        if lead is None:
            continue
        lno, text = lead
        fa = FORM_A.search(text)
        toks = COUNT_TOKEN.findall(text)
        if fa:
            raw = fa.group(1).strip().strip("*`")
            if not raw.isdigit():
                viol.append(
                    "%s:%d 정형 선언 라인 수치 '%s' 파싱 불가 — 통과 아님, fail-closed "
                    "(아라비아 숫자만 허용; 한글 수사·기호 표기 금지)"
                    % (os.path.basename(path), lno + 1, raw))
                sites.append({"line": lno + 1, "form": "A", "declared": None, "actual": rows})
                continue
            declared = int(raw)
            sites.append({"line": lno + 1, "form": "A", "declared": declared, "actual": rows})
        elif len(toks) > 1:
            viol.append(
                "%s:%d 선언 라인에 count 토큰 %d 개(%s) — 선언 모호, fail-closed "
                "(2번째 토큰 주입으로 site 를 지우는 회피 차단)"
                % (os.path.basename(path), lno + 1, len(toks),
                   ", ".join("%s%s" % t for t in toks)))
            sites.append({"line": lno + 1, "form": "B?", "declared": None, "actual": rows})
            continue
        elif len(toks) == 1:
            declared = int(toks[0][0])
            sites.append({"line": lno + 1, "form": "B", "declared": declared, "actual": rows})
        else:
            continue  # 선언 site 아님 (count 토큰 0) — 정의역 밖
        s = sites[-1]
        if s["declared"] is not None and s["declared"] != s["actual"]:
            viol.append(
                "%s:%d declared-vs-actual 불일치 — 선언 %d ≠ 표 실 row %d "
                "(row 위조·삭제 또는 선언 값 변조 의심) | lead='%s'"
                % (os.path.basename(path), lno + 1, s["declared"], s["actual"], text[:60]))
    return sites, viol


def main():
    root = os.path.abspath(sys.argv[1])
    targets = []
    for spec in sys.argv[2:]:
        rel, _, floor = spec.rpartition(":")
        targets.append((rel, int(floor)))
    violations = []
    total = 0
    for rel, floor in targets:
        path = os.path.join(root, rel.replace("/", os.sep))
        if not os.path.isfile(path):
            violations.append("registry 대상 파일 부재: %s — fail-closed" % rel)
            continue
        sites, viol = scan(path)
        violations.extend(viol)
        total += len(sites)
        if len(sites) < floor:
            violations.append(
                "%s: 선언 site %d 개 < floor %d — 선언 라인 삭제·무력화 의심 (fail-closed). "
                "site 를 늘리는 것은 자유, 줄이는 것은 ratchet 위반"
                % (rel, len(sites), floor))
        else:
            for s in sites:
                print("  site %s:%d form=%s declared=%s actual=%d"
                      % (rel, s["line"], s["form"], s["declared"], s["actual"]))
    for v in violations:
        print("VIOLATION: %s" % v)
    if violations:
        print("")
        print("check-declared-count-vs-actual: %d violation" % len(violations))
        sys.exit(1)
    print("check-declared-count-vs-actual: PASS — 선언 site %d 건 전건 declared == actual" % total)
    sys.exit(0)


if __name__ == "__main__":
    main()
PY

run_check() {
  local root="$1"; shift
  set +e
  CHECK_OUT="$(python3 "$WORK/${CHECKER:-checker.py}" "$root" "$@" 2>&1)"
  CHECK_RC=$?
  set -e
}

# ─────────────────────────────────────────────────────────────────────────────
# ★ crash-as-RED 차단 (CFP-2984 G7 감사 — 실사건 회귀 방지)
#   `rc≠0 → RED` 단독 판정은 **크래시와 검출을 구별하지 못한다**. 오라클이 예외로 죽으면
#   expect=RED 인 전 케이스가 "잡았다" 로 계상되고 mutant 원장이 통째로 거짓이 된다.
#   ★ 실증(G7): 본 파일의 대조 분기(`declared != actual`)에만 예외를 심자 clean 대조군은
#     그대로 통과하고 **전 10 케이스가 GREEN(rc=0)** 이 되었다 — 검출은 0 인데 만점.
#     즉 INV-T4 대조군만으로는 **조건부 크래시**를 못 잡는다. 그래서 이 가드가 필요하다.
#   ★ SyntaxError·IndentationError 는 Traceback 머리글 없이 출력된다(실측) — 함께 본다.
#   ★ 판정 근거 마커: RED 인데 위반 문면(VIOLATION)이 없으면 무증거 RED 로 본다.
# ─────────────────────────────────────────────────────────────────────────────
crash_marker() { # <output> → 0 = 크래시 흔적 있음
  case "$1" in
    *Traceback*|*SyntaxError*|*IndentationError*|*TabError*) return 0 ;;
  esac
  return 1
}

assert_verdict() {
  local name="$1" expect="$2" root="$3"; shift 3
  local verdict
  run_check "$root" "$@"
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

# 실 ADR 을 tmpdir 로 복제 후 변형 (원본 무접촉)
build_corpus() {
  local dst="$1"
  rm -rf "$dst"
  mkdir -p "$dst/archive/adr"
  cp "$REPO_ROOT/$ADR109" "$dst/$ADR109"
  cp "$REPO_ROOT/$ADR179" "$dst/$ADR179"
}

patch_file() {
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

echo "── AC-6 declared count vs actual table rows"

# ── 대조군: 실 repo A 소유 ADR 무변조 ───────────────────────────────────────
assert_verdict "baseline/실 repo A 소유 ADR 무변조" PASS "$REPO_ROOT" "$ADR109:2" "$ADR179:2"
echo "$CHECK_OUT" | sed 's/^/    /'

# ── ① 제거 (a) 선언 bold 라인 삭제 → floor RED ──────────────────────────────
build_corpus "$WORK/m1a"
patch_file "$WORK/m1a/$ADR109" "**정정 실행 (7행)**
" ""
assert_verdict "M1a ①제거: 선언 bold 라인 삭제" RED "$WORK/m1a" "$ADR109:2" "$ADR179:2"

# ── ② 주입 (a) 표 row 1개 삭제 ─────────────────────────────────────────────
build_corpus "$WORK/m2a"
patch_file "$WORK/m2a/$ADR109" "| 본 ADR | §결과 > 긍정 | 동상 |
" ""
assert_verdict "M2a ②주입: 표 row 1개 삭제" RED "$WORK/m2a" "$ADR109:2" "$ADR179:2"

# ── ② 주입 (b) 표 row 1개 위조 삽입 ────────────────────────────────────────
build_corpus "$WORK/m2b"
patch_file "$WORK/m2b/$ADR179" "| ⑩ | \`notes_ref\`" "| ⑪ | \`fake_field\` | 참조형 |
| ⑩ | \`notes_ref\`"
assert_verdict "M2b ②주입: 표 row 1개 위조 삽입" RED "$WORK/m2b" "$ADR109:2" "$ADR179:2"

# ── ③ 등가변형 (a) 정형 선언 수치를 한글 수사로 ────────────────────────────
build_corpus "$WORK/m3a"
patch_file "$WORK/m3a/$ADR179" "**선언 열거 수 = 10**" "**선언 열거 수 = 열**"
assert_verdict "M3a ③등가변형: 정형 수치 한글 수사('열')" RED "$WORK/m3a" "$ADR109:2" "$ADR179:2"

# ── ③ 등가변형 (b) 산문 선언 수치를 한글 수사로 → 토큰 소실 → floor RED ────
build_corpus "$WORK/m3b"
patch_file "$WORK/m3b/$ADR109" "**정정 실행 (7행)**" "**정정 실행 (일곱 행)**"
assert_verdict "M3b ③등가변형: 산문 수치 한글 수사('일곱 행')" RED "$WORK/m3b" "$ADR109:2" "$ADR179:2"

# ── ③ 등가변형 (c) 2번째 count 토큰 주입 → 선언 모호 ───────────────────────
build_corpus "$WORK/m3c"
patch_file "$WORK/m3c/$ADR109" "**정정 실행 (7행)**" "**정정 실행 (7행) — 총 9종**"
assert_verdict "M3c ③등가변형: 2번째 토큰 주입(선언 모호)" RED "$WORK/m3c" "$ADR109:2" "$ADR179:2"

# ── ① 제거 (b) 오라클 자신의 대조 로직 삭제 → 검출력 소실 실증 ─────────────
# 위반 픽스처(M2a)를 **대조 로직 없는 오라클**에 통과시켜, 그 로직이 load-bearing 임을 보인다.
python3 - "$WORK/checker.py" "$WORK/checker_nocmp.py" <<'PY'
import io, sys
src = io.open(sys.argv[1], encoding="utf-8").read()
old = '        if s["declared"] is not None and s["declared"] != s["actual"]:'
assert old in src, "SETUP: 대조 로직 앵커 미발견"
new = '        if False:  # MUTANT M1b — declared-vs-actual 대조 로직 제거'
io.open(sys.argv[2], "w", encoding="utf-8", newline="\n").write(src.replace(old, new, 1))
PY
CHECKER="checker_nocmp.py" assert_verdict \
  "M1b ①제거: 대조 로직 제거 오라클이 위반 픽스처를 통과(검출력 소실 실증)" PASS "$WORK/m2a" "$ADR109:2" "$ADR179:2"
# 위 leg 의 의미: 같은 입력에 대해 정본 오라클은 RED(M2a), 로직 제거 오라클은 PASS
#   ⇒ 그 대조 로직이 유일 검출 경로임이 실증됐다. presence-only 오라클이면 둘 다 PASS 였을 것.

# ── 형제 회귀: 봉합이 정상 site 검출력을 파괴하지 않았는가 ─────────────────
build_corpus "$WORK/sib"
assert_verdict "형제/무변조 사본 재확인" PASS "$WORK/sib" "$ADR109:2" "$ADR179:2"
# registry 대상 파일 부재도 fail-closed 인가
assert_verdict "형제/registry 대상 파일 부재 = fail-closed" RED "$WORK/sib" "archive/adr/ADR-000-nonexistent.md:1"

echo "── 결과: PASS=$PASS FAIL=$FAIL"
[ "$FAIL" -eq 0 ] || exit 1
