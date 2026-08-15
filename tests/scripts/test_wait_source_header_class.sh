#!/usr/bin/env bash
# tests/scripts/test_wait_source_header_class.sh
# CFP-2984 Phase 2 (구현 lane) — AC-30 discriminating self-test.
#
# 대상 = ADR-109 §결정 2 의 **대기원(wait source) 지시 문면**.
# 오라클 = 그 문면이 **대기원으로 명명한 헤더 토큰**을 `SKILL.md` 의 `header-semantic-class`
#          정본 fence(초 단위 상대값 / RFC 3339 절대시각)에 대조 →
#          **절대시각 분류 헤더가 대기원으로 명명된 건수 = 0**.
#
# ★ 리터럴 문장 매칭 금지 (등가 표현 우회 차단):
#   판정은 "특정 문장이 있는가" 가 아니라 **토큰 정규화 → 클래스 매핑 → 대기원 술어 결속**이다.
#   `Anthropic-RateLimit-Requests-Reset` / `anthropic-ratelimit-*-reset` / 대소문자·축약 변형이
#   전부 같은 의미 클래스로 접힌다.
#
# ★ AC-5a 와 오라클 분리 (P2-3): 여기는 **문면**(문서가 무엇을 대기원으로 명명하는가),
#   AC-5a 는 **계산**(함수가 무엇에서 대기를 유도하는가). 서로를 대신하지 않는다.
#
# ★ 부정문 처리 (오검출 차단 keystone): ADR-109 는 "`anthropic-ratelimit-*-reset` 은 대기원이
#   **아니다**" 라고 **명시 배제**한다. 부정 문맥을 대기원 명명으로 세는 오라클은 정본을 RED 로
#   만든다 — TC-C1 이 그 오검출 부재를 못박는다.
#
# ★ 정직 천장: 본 검사는 **문장 단위 부정 표지**로 배제를 판정한다. 여러 문장에 걸친 우회 서술
#   (예: 앞 문장에서 배제하고 뒤 문장에서 슬쩍 대기원으로 쓰는 형태)은 잔여이며 사람 검토 축이다.
#
# self-contained bash + 순수 픽스처 (INV-T3). Exit 0 = 전 케이스 PASS.

set -euo pipefail
export PYTHONIOENCODING=utf-8

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SKILL="$REPO_ROOT/skills/rate-limit-429-mitigation/SKILL.md"
ADR109="$REPO_ROOT/archive/adr/ADR-109-in-process-429-mitigation-framework.md"

PY=python3
command -v python3 >/dev/null 2>&1 || PY=python

PASS=0
FAIL=0
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

ORACLE="$WORK/oracle_30.py"
cat > "$ORACLE" <<'PYORACLE'
# -*- coding: utf-8 -*-
"""AC-30 오라클 — 대기원 지시 문면의 헤더 토큰 ↔ 의미 클래스 대조.

exit 0 = finding 0.  exit 1 = finding >= 1 (fail-closed 포함).
"""
import argparse
import io
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:  # pragma: no cover
    pass

RE_FENCE = re.compile(r"^```([A-Za-z0-9_-]*)\s*$")

# 대기원 술어 — "이 헤더에서 대기를 얻는다" 는 의미의 표현 집합 (표기 변형 흡수).
WAIT_PREDICATES = [
    "대기원", "wait source", "대기시간으로", "대기 값", "대기값", "대기시간 유도",
    "대기로 유도", "wait_seconds", "대기 산출", "대기시간을 유도", "header 값 적용",
]
# 부정 표지 — 같은 문장이 그 헤더를 대기원에서 **배제**한다는 표시.
NEGATION_MARKERS = [
    "아니다", "아니며", "제외", "않는다", "않으며", "금지", "not ", "NOT ", "미산출", "쓰지 않",
]


def read(path):
    return io.open(path, encoding="utf-8").read()


def fences(text):
    out, cur, info = [], None, None
    for line in text.split("\n"):
        m = RE_FENCE.match(line)
        if m and cur is None:
            cur, info = [], m.group(1)
            continue
        if line.strip() == "```" and cur is not None:
            out.append((info, cur))
            cur, info = None, None
            continue
        if cur is not None:
            cur.append(line)
    return out


def parse_class_table(skill_text):
    """`header-semantic-class` 정본 fence → [(pattern_regex, class, eligibility)]."""
    for info, lines in fences(skill_text):
        if info != "header-semantic-class":
            continue
        rows = []
        for ln in lines:
            t = ln.strip()
            if not t or t.startswith("#"):
                continue
            parts = [p.strip() for p in t.split("|")]
            if len(parts) != 3:
                return None, "header-semantic-class 행 형식 위반: %r" % (t,)
            token, klass, elig = parts
            # 토큰 glob(`*`) → 정규식. 대소문자 무시.
            # ★ 가변 세그먼트 문자류에 `*` 를 **포함**시킨다 — 문서가 구체 헤더명
            #   (`anthropic-ratelimit-requests-reset`) 뿐 아니라 glob 표기
            #   (`anthropic-ratelimit-*-reset`) 로도 헤더를 부르기 때문이다.
            #   포함하지 않으면 glob 표기가 어떤 클래스에도 매핑되지 않아 오라클이 **후보 0**
            #   으로 조용히 통과한다(= 공허 GREEN). TC-N1 이 이 퇴화를 잡는다.
            rx = re.compile("^" + re.escape(token.lower()).replace(r"\*", r"[a-z0-9_*-]+") + "$")
            rows.append((rx, klass.lower(), elig.lower()))
        return rows, None
    return None, "`header-semantic-class` 정본 fence 부재"


def wait_source_section(adr_text):
    """ADR-109 §결정 2 절 본문 (다음 `### ` 헤딩 전까지)."""
    lines = adr_text.split("\n")
    out, inside = [], False
    for ln in lines:
        if ln.startswith("### "):
            inside = ln.startswith("### §결정 2")
            continue
        if inside:
            out.append(ln)
    return "\n".join(out)


RE_TOKEN = re.compile(r"`([A-Za-z][A-Za-z0-9_*-]{2,})`")


def normalize_token(tok):
    """헤더 토큰 정규화 — 대소문자·축약 접두 변형 흡수."""
    t = tok.strip().strip("`").lower()
    if t.startswith("ratelimit-") or t.startswith("*-"):
        t = "anthropic-" + t.lstrip("*-") if t.startswith("*-") else "anthropic-" + t
    return t


def split_sentences(text):
    return [s for s in re.split(r"(?<=[.。])\s+|\n", text) if s.strip()]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--skill", required=True)
    ap.add_argument("--adr109", required=True)
    ap.add_argument(
        "--ignore-negation",
        action="store_true",
        help="부정 표지를 무시한다 — 정본 GREEN 이 '후보 부재'가 아니라 '부정 처리'에 의존함을 실증하는 진단 모드",
    )
    args = ap.parse_args()

    findings = []
    skill_text = read(args.skill)
    adr_text = read(args.adr109)

    table, err = parse_class_table(skill_text)
    if table is None:
        print("FAILCLOSED: %s" % err)
        return 1

    section = wait_source_section(adr_text)
    if not section.strip():
        print("FAILCLOSED: ADR-109 §결정 2 절 추출 실패 — 정의역 소실")
        return 1

    named = 0
    for sent in split_sentences(section):
        if not any(p in sent for p in WAIT_PREDICATES):
            continue
        negated = (not args.ignore_negation) and any(n in sent for n in NEGATION_MARKERS)
        for raw in RE_TOKEN.findall(sent):
            tok = normalize_token(raw)
            klass = None
            for rx, k, _elig in table:
                if rx.match(tok):
                    klass = k
                    break
            if klass is None:
                continue
            if klass == "absolute-rfc3339" and not negated:
                named += 1
                findings.append(
                    "ABSOLUTE-AS-WAIT-SOURCE: 토큰 `%s`(정규화 %s, class=%s)이 대기원으로 명명됨 — 문장: %s"
                    % (raw, tok, klass, sent.strip()[:110])
                )

    if findings:
        print("\n".join(findings))
        return 1
    print("OK finding=0 (absolute-class-as-wait-source=%d, class_rows=%d)" % (named, len(table)))
    return 0


sys.exit(main())
PYORACLE

run_case() {
  local name="$1" expected_exit="$2" expect_substr="$3" skill_path="$4" adr_path="$5"
  local out exit_code=0 ok=1
  out=$("$PY" "$ORACLE" --skill "$skill_path" --adr109 "$adr_path" 2>&1) || exit_code=$?
  # ★ crash-as-RED 차단 (형제 워커 실사건 회귀 방지): 오라클이 예외로 죽어서 난 rc!=0 은
  #   "검출" 이 아니다. 정규식 컴파일 오류 하나로 전 mutant 가 RED 로 보이는 하네스 사망을 막는다.
  case "$out" in
    *Traceback*)
      echo "X FAIL: $name — 오라클 크래시(Traceback). RED 를 검출로 셀 수 없다"
      printf '%s
' "$out" | sed 's/^/       /'
      FAIL=$((FAIL + 1))
      return ;;
  esac
  [ "$exit_code" -eq "$expected_exit" ] || ok=0
  # ★ P2-5 (CFP-2984): 빈 substr = 판정을 exit code 단독에 맡기는 것이다.
  #   크래시는 그 코드를 위조할 수 있으므로(rc≠0 을 ‘검출’ 로 오독), 산출 대조 없는 케이스를
  #   harness 결함으로 끈는다. 현행 호출부는 전건 비어있지 않음(신규 RED 0) — 향후 유입만 차단하는 ratchet.
  if [ -z "$expect_substr" ]; then
    echo "X FAIL: $name — harness 결함: expect_substr 가 비었다(판정이 exit code 단독)"
    FAIL=$((FAIL + 1))
    return
  fi
  case "$out" in *"$expect_substr"*) : ;; *) ok=0 ;; esac
  if [ "$ok" -eq 1 ]; then
    echo "OK PASS: $name (exit $exit_code)"
    PASS=$((PASS + 1))
  else
    echo "X FAIL: $name"
    echo "  expected exit=$expected_exit substr='$expect_substr', got exit=$exit_code"
    echo "  output: $out"
    FAIL=$((FAIL + 1))
  fi
}

mutate() {
  local dest="$1" src="$2" old="$3" new="$4"
  "$PY" - "$src" "$dest" "$old" "$new" <<'PYMUT'
import io
import sys
src, dest, old, new = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
s = io.open(src, encoding="utf-8").read()
assert s.count(old) == 1, ("mutant anchor count != 1", s.count(old), old[:60])
io.open(dest, "w", encoding="utf-8", newline="\n").write(s.replace(old, new))
PYMUT
}

echo "── AC-30: 대기원 지시 문면의 헤더 의미 클래스 대조"

# ── TC-C1 clean-input 대조군 (부정 문맥 오검출 부재 포함) ───────────────────
run_case "TC-C1 정본 — 절대시각 헤더가 대기원으로 명명된 건수 0" 0 "absolute-class-as-wait-source=0" "$SKILL" "$ADR109"

# ── TC-M1 ① 제거: 의미 클래스 대조표 삭제 → fail-closed ────────────────────
M1="$WORK/m1_skill.md"
mutate "$M1" "$SKILL" '```header-semantic-class' '```renamed-away'
run_case "TC-M1 ①제거 의미 클래스표 삭제 → fail-closed RED" 1 "FAILCLOSED" "$M1" "$ADR109"

# ── TC-M2 ② 주입: 절대시각 헤더를 대기원으로 기입 ──────────────────────────
M2="$WORK/m2_adr.md"
mutate "$M2" "$ADR109" \
  "  - **empirical-source**: [verified-via: RFC 7231 §7.1.3 — \`Retry-After\` = delta-seconds 또는 HTTP-date]" \
  "  - **empirical-source**: [verified-via: RFC 7231 §7.1.3 — \`Retry-After\` = delta-seconds 또는 HTTP-date]
  - \`anthropic-ratelimit-requests-reset\` 값을 대기시간으로 유도한다."
run_case "TC-M2 ②주입 절대시각 헤더를 대기원으로 → RED" 1 "ABSOLUTE-AS-WAIT-SOURCE" "$SKILL" "$M2"

# ── TC-M3 ③ 등가변형: 헤더명 대소문자 변형으로 우회 시도 ───────────────────
M3="$WORK/m3_adr.md"
mutate "$M3" "$ADR109" \
  "  - **empirical-source**: [verified-via: RFC 7231 §7.1.3 — \`Retry-After\` = delta-seconds 또는 HTTP-date]" \
  "  - **empirical-source**: [verified-via: RFC 7231 §7.1.3 — \`Retry-After\` = delta-seconds 또는 HTTP-date]
  - \`Anthropic-RateLimit-Tokens-Reset\` 을 대기원으로 삼는다."
run_case "TC-M3 ③등가변형 대소문자 변형 → 토큰 정규화 후 RED" 1 "ABSOLUTE-AS-WAIT-SOURCE" "$SKILL" "$M3"

# ── TC-M4 ③ 등가변형: 축약 표기(`ratelimit-*-reset`)로 우회 시도 ───────────
M4="$WORK/m4_adr.md"
mutate "$M4" "$ADR109" \
  "  - **empirical-source**: [verified-via: RFC 7231 §7.1.3 — \`Retry-After\` = delta-seconds 또는 HTTP-date]" \
  "  - **empirical-source**: [verified-via: RFC 7231 §7.1.3 — \`Retry-After\` = delta-seconds 또는 HTTP-date]
  - wait_seconds 는 \`ratelimit-requests-reset\` 에서 얻는다."
run_case "TC-M4 ③등가변형 축약 표기 → 정규화 후 RED" 1 "ABSOLUTE-AS-WAIT-SOURCE" "$SKILL" "$M4"

# ── TC-P1 정밀도 대조군: 상대값 헤더는 대기원이어도 정상 (오검출 부재) ─────
P1="$WORK/p1_adr.md"
mutate "$P1" "$ADR109" \
  "  - **empirical-source**: [verified-via: RFC 7231 §7.1.3 — \`Retry-After\` = delta-seconds 또는 HTTP-date]" \
  "  - **empirical-source**: [verified-via: RFC 7231 §7.1.3 — \`Retry-After\` = delta-seconds 또는 HTTP-date]
  - \`retry-after\` 값을 그대로 대기시간으로 유도한다."
run_case "TC-P1 상대값 헤더를 대기원으로 명명 → GREEN (오검출 부재)" 0 "absolute-class-as-wait-source=0" "$SKILL" "$P1"

# ── TC-P2 정밀도 대조군: 절대시각 헤더의 **배제 서술**은 위반이 아니다 ─────
P2="$WORK/p2_adr.md"
mutate "$P2" "$ADR109" \
  "  - **empirical-source**: [verified-via: RFC 7231 §7.1.3 — \`Retry-After\` = delta-seconds 또는 HTTP-date]" \
  "  - **empirical-source**: [verified-via: RFC 7231 §7.1.3 — \`Retry-After\` = delta-seconds 또는 HTTP-date]
  - \`anthropic-ratelimit-requests-reset\` 은 대기원에서 제외한다."
run_case "TC-P2 절대시각 헤더 배제 서술 → GREEN (부정 문맥 오검출 부재)" 0 "absolute-class-as-wait-source=0" "$SKILL" "$P2"

# ── TC-N1 ★ 비-공허 실증: 정본 GREEN 이 '후보 부재' 가 아님을 보인다 ────────
# 부정 표지 처리를 끄면 정본 문서 자체가 RED 가 된다 → §결정 2 안에 절대시각 토큰 후보가
# **실재**하며, TC-C1 의 GREEN 은 "볼 게 없어서" 가 아니라 "배제 서술을 옳게 읽어서" 다.
NOUT=$("$PY" "$ORACLE" --skill "$SKILL" --adr109 "$ADR109" --ignore-negation 2>&1) || NRC=$?
NRC=${NRC:-0}
if [ "$NRC" -eq 1 ]; then
  case "$NOUT" in
    *ABSOLUTE-AS-WAIT-SOURCE*)
      echo "OK PASS: TC-N1 부정 처리 off → 정본이 RED (TC-C1 GREEN 은 비-공허)"
      PASS=$((PASS + 1))
      ;;
    *)
      echo "X FAIL: TC-N1 부정 처리 off 인데 기대 finding 부재"
      echo "  output: $NOUT"
      FAIL=$((FAIL + 1))
      ;;
  esac
else
  echo "X FAIL: TC-N1 부정 처리 off 인데도 GREEN — §결정 2 안에 절대시각 토큰 후보가 0건이라는 뜻이고,"
  echo "        그렇다면 TC-C1 의 GREEN 은 공허하다 (오라클이 아무것도 보고 있지 않다)."
  echo "  output: $NOUT"
  FAIL=$((FAIL + 1))
fi

echo "── 결과: PASS=$PASS FAIL=$FAIL"
[ "$FAIL" -eq 0 ] || exit 1
