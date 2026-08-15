#!/usr/bin/env bash
# tests/scripts/test_detection_surface_scope.sh
# CFP-2984 Phase 2 (구현 lane) — AC-15 discriminating self-test (감지 정의역).
#
# AC-15: 입력 픽스처 2종 — ① 한도 관련 문자열이 다수 포함된 **본문** / ② 동일 문자열을 담은
#   **오류·종료 통지 표면** — 에 대해 `ADR-109 §결정 1` 6-literal 감지식(A 소유)을 실행하면
#   **①은 미발화하고 ②만 발화**하며, 정의역 제한을 제거한 변이체는 ①에서 발화해 RED.
#
# ★ enum 하드코딩 금지 (ADR-109 Amendment 1 (c) 규율 준수): 리터럴 집합은 ADR 의
#   **code-fence 를 파싱해** 얻는다. 사본을 테스트에 박지 않는다 — fixture-vs-SSOT drift 차단.
#   code-fence 부재·파싱 실패 = 통과가 아니라 **fail-closed RED**.
#
# ★ 경계 (비협상): **CFP-2944 판별식 D 는 침범하지 않는다.** 본 테스트의 감지식은 §결정 1 /
#   Amendment 1 의 6-literal fast-path 이며, Amendment 2 의 D-0/D-i~iii/4치 출력은 대상이 아니다.
#   Amendment 2 는 `status: Proposed` + CFP-2944 소유이므로 읽지도 결박하지도 않는다.
#
# ★ 정의역 근거 앵커: 표면 제한("error/termination notification 표면 한정" ∧ "subagent
#   substantive output 본문 NOT")이 repo 문서에 실재하는지 먼저 확인한다 — 앵커 부재 시
#   RED(오라클이 자기가 발명한 규칙을 검사하는 자기충족 회피).
#
# ★ 정직 천장 2항 (over-claim 금지):
#   (1) 표면 라벨은 **픽스처가 제공**한다. 런타임에서 실제 신호의 표면을 판별하는 층은 본
#       테스트 범위 밖이며, 본 테스트가 검증하는 것은 "정의역 제한이 판정에 실제로 관여하는가"다.
#   (2) 본 오라클의 리터럴 매칭은 **대소문자·공백 정규화**를 한다. ADR-109 §결정 1 원문은
#       case-sensitive substring 이고 (f) 가 그 gap 을 escalate 후보로 남겼다 — 본 오라클은
#       그 방향(누락 감소)으로만 엄격하며, ADR 문면을 바꾸지 않는다.
#
# 3방향 mutant (감지식 구현에 실변형 적용 — sed 로 checker 사본을 변조):
#   ① 제거      M1 = 정의역(표면) 가드 제거          → ① 발화 → RED
#   ② 주입      M2 = 표면 가드를 **리터럴 밀도 임계**로 치환 + ①에 리터럴 다수 주입 → ① 발화 RED
#   ③ 등가변형  M3 = 리터럴 정규화 제거 → 대소문자·띄어쓰기 변형된 ② 가 **미발화** → RED
#   ④ fail-closed M4 = ADR code-fence 삭제 → 리터럴 집합 파생 실패 → RED
#
# 대조군(INV-T4): 무변조 감지식 + 실 픽스처 2종 → ① 미발화 ∧ ② 발화 = PASS.
# INV-T3 순수 픽스처: 네트워크 0 · 실 ~/.claude/** 0 · 실 git 원격 0 · 쓰기는 mktemp -d 내부만.
# Exit 0 = 전 케이스 PASS.

set -euo pipefail
export PYTHONIOENCODING=utf-8

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ADR109="$REPO_ROOT/archive/adr/ADR-109-in-process-429-mitigation-framework.md"
FIX_DIR="$REPO_ROOT/tests/fixtures/cfp2984"
BODY_FIX="$FIX_DIR/detection_surface_body.txt"
TERM_FIX="$FIX_DIR/detection_surface_termination.txt"

PASS=0
FAIL=0
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

# ─────────────────────────────────────────────────────────────────────────────
cat > "$WORK/detector.py" <<'PY'
#!/usr/bin/env python3
"""ADR-109 §결정 1 / Amendment 1 6-literal 감지식 — 표면 정의역 제한 포함.

사용: detector.py <adr-path> <fixture-path>
출력: FIRE / NOFIRE (+ 근거). exit 0 = 판정 성공, 2 = 파생 실패(fail-closed).
"""
import re
import sys

# 발동 허용 표면 2종 (playbook §3.0.12b scope 불변식 = error/termination notification 한정).
#   비허용: subagent substantive output 본문 / 도구 반환 텍스트 / 제3자 통제 임의 텍스트.
ALLOWED_SURFACES = {"spawn-rejection", "termination-notification"}

# Amendment 1 (b) 확장 감지집합 code-fence 앵커 — 6 literal 이 code-fence 안에 한 줄 1개씩.
FENCE_ANCHOR = re.compile(
    r"session/usage-limit 포함 detection\s{0,4}=\s{0,4}다음\s{0,4}6\s{0,4}literal[^\n]{0,80}\n+```\n(.*?)```",
    re.DOTALL,
)
# 정본 하한 (ratchet floor) — 확장은 자유, 축소는 위반.
REQUIRED_FLOOR = {
    "rate limit", "quota exceeded", "429", "server is temporarily limiting",
    "session limit", "usage limit",
}


def parse_literals(adr_text):
    m = FENCE_ANCHOR.search(adr_text)
    if not m:
        return None, "Amendment 1 (b) 6-literal code-fence 미발견 — 감지집합 파생 불가 (fail-closed)"
    lits = []
    for line in m.group(1).split("\n"):
        s = line.strip()
        if not s:
            continue
        if s.startswith('"') and s.endswith('"'):
            s = s[1:-1]
        lits.append(s)
    if not lits:
        return None, "code-fence 내부 literal 0 건 — fail-closed"
    # floor 비교는 **match 정규화와 분리된** canonicalizer 를 쓴다.
    #   결합해 두면 정규화 결함 하나가 floor 가드까지 조용히 무력화한다(실제로 M3 mutant 가
    #   floor 를 먼저 깨뜨려 detection leg 에 도달하지 못하는 형태로 이 결합을 드러냈다).
    got = {_canon_floor(x) for x in lits}
    missing = sorted(REQUIRED_FLOOR - got)
    if missing:
        return None, ("감지집합 ratchet floor 위반 — 정본 literal 누락 %s (확장은 허용, 축소는 "
                      "closed-set invariant 위반)" % missing)
    return lits, None


def _canon_floor(s):
    """floor 대조 전용 canonicalizer — match 정규화와 **독립**(결합 금지)."""
    return re.sub(r"\s+", " ", s.strip().lower())


def normalize(s):
    """대소문자·연속 공백 정규화 (③ 등가변형 봉쇄 지점 — MUTANT M3 가 이 함수를 무력화한다)."""
    return re.sub(r"\s+", " ", s.strip().lower())


def parse_fixture(text):
    head, _, body = text.partition("\n---\n")
    m = re.search(r"^surface:\s{0,4}(\S+)\s*$", head, re.MULTILINE)
    surface = m.group(1) if m else None
    return surface, body


def detect(surface, body, literals):
    # ── 정의역(표면) 가드 — MUTANT M1 이 이 블록을 제거한다 ──
    if surface not in ALLOWED_SURFACES:
        return False, "surface '%s' 가 허용 표면 %s 밖 — 정의역 제한으로 미발화" % (
            surface, sorted(ALLOWED_SURFACES))
    # ── 리터럴 any-match ──
    nb = normalize(body)
    hits = [l for l in literals if normalize(l) in nb]
    if hits:
        return True, "literal any-match %s" % hits[:3]
    return False, "허용 표면이나 literal 미매칭"


def main():
    adr_path, fx_path = sys.argv[1], sys.argv[2]
    with open(adr_path, encoding="utf-8") as f:
        literals, err = parse_literals(f.read())
    if literals is None:
        print("SETUP-FAIL: %s" % err)
        sys.exit(2)
    with open(fx_path, encoding="utf-8") as f:
        surface, body = parse_fixture(f.read())
    fired, why = detect(surface, body, literals)
    print("%s | literals=%d surface=%s | %s"
          % ("FIRE" if fired else "NOFIRE", len(literals), surface, why))
    sys.exit(0)


if __name__ == "__main__":
    main()
PY

run_detector() {
  # run_detector <detector.py> <adr> <fixture> → DET_OUT / DET_RC
  set +e
  DET_OUT="$(python3 "$1" "$2" "$3" 2>&1)"
  DET_RC=$?
  set -e
}

assert_detect() {
  # assert_detect <name> <FIRE|NOFIRE|SETUP-FAIL> <detector> <adr> <fixture>
  local name="$1" expect="$2" det="$3" adr="$4" fx="$5" got
  run_detector "$det" "$adr" "$fx"
  if [ "$DET_RC" -eq 2 ]; then
    got="SETUP-FAIL"
  else
    case "$DET_OUT" in
      FIRE*)   got="FIRE" ;;
      NOFIRE*) got="NOFIRE" ;;
      *)       got="UNKNOWN" ;;
    esac
  fi
  if [ "$got" = "$expect" ]; then
    echo "OK  $name (expect=$expect got=$got)"
    PASS=$((PASS+1))
  else
    echo "X   FAIL: $name (expect=$expect got=$got)"
    echo "    $DET_OUT"
    FAIL=$((FAIL+1))
  fi
}

mutate_detector() {
  # mutate_detector <out.py> <old> <new>   (old/new 는 각각 별개 인자 — printf 이스케이프 회피)
  local out="$1" old="$2" new="$3"
  python3 - "$WORK/detector.py" "$out" "$old" "$new" <<'PY'
import io, sys
src_p, dst_p, old, new = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
src = io.open(src_p, encoding="utf-8").read()
if old not in src:
    print("SETUP: detector mutant 앵커 미발견 %r" % old[:60], file=sys.stderr)
    sys.exit(3)
io.open(dst_p, "w", encoding="utf-8", newline="\n").write(src.replace(old, new, 1))
PY
}

echo "── AC-15 detection surface scope (정의역 제한)"

# ── 0. 정의역 근거 앵커 실재 확인 (자기충족 회피) ──────────────────────────
ANCHOR_HITS=$(grep -rl "error/termination notification 표면 한정" "$REPO_ROOT/docs" "$REPO_ROOT/archive" 2>/dev/null | wc -l | tr -d ' ')
if [ "$ANCHOR_HITS" -ge 1 ]; then
  echo "OK  정의역 근거 앵커 실재 ($ANCHOR_HITS 파일) — 'error/termination notification 표면 한정'"
  PASS=$((PASS+1))
else
  echo "X   FAIL: 정의역 근거 앵커 부재 — 오라클이 자기 발명 규칙을 검사하게 됨 (fail-closed)"
  FAIL=$((FAIL+1))
fi

# ── 대조군 (INV-T4 baseline) ────────────────────────────────────────────────
assert_detect "baseline/① 본문(리터럴 다수) 미발화" NOFIRE "$WORK/detector.py" "$ADR109" "$BODY_FIX"
assert_detect "baseline/② 종료 통지 발화"           FIRE   "$WORK/detector.py" "$ADR109" "$TERM_FIX"
run_detector "$WORK/detector.py" "$ADR109" "$TERM_FIX"; echo "    [②] $DET_OUT"
run_detector "$WORK/detector.py" "$ADR109" "$BODY_FIX"; echo "    [①] $DET_OUT"

# ── 대조군 ②: 표면만 바꾸면 판정이 뒤집히는가 (단일 변인 통제) ─────────────
python3 - "$BODY_FIX" "$WORK/body_as_termination.txt" <<'PY'
import io, sys
raw = io.open(sys.argv[1], encoding="utf-8").read()
io.open(sys.argv[2], "w", encoding="utf-8", newline="\n").write(
    raw.replace("surface: subagent-output-body", "surface: termination-notification", 1))
PY
assert_detect "대조군/① 본문을 허용 표면으로 태깅하면 발화" FIRE "$WORK/detector.py" "$ADR109" \
  "$WORK/body_as_termination.txt"
# ⇒ 두 픽스처의 유일 차이가 표면임이 실증된다(내용 동일, 판정 반전).

# ── ① 제거: 표면 가드 제거 → ① 발화 ────────────────────────────────────────
mutate_detector "$WORK/det_m1.py" \
  'if surface not in ALLOWED_SURFACES:' \
  'if False:  # MUTANT M1 — 정의역(표면) 가드 제거
        pass
    if False:'
assert_detect "M1 ①제거: 정의역 가드 제거 → ① 발화" FIRE "$WORK/det_m1.py" "$ADR109" "$BODY_FIX"
assert_detect "M1 형제/② 는 여전히 발화(검출력 잔존 확인)" FIRE "$WORK/det_m1.py" "$ADR109" "$TERM_FIX"

# ── ② 주입: 표면 가드를 리터럴 '밀도 임계' 로 치환 + 리터럴 다수 본문 ──────
mutate_detector "$WORK/det_m2.py" \
  'if surface not in ALLOWED_SURFACES:' \
  'if len([x for x in literals if normalize(x) in normalize(body)]) < 2:  # MUTANT M2 — 표면 가드를 밀도 임계로 치환
        return False, "밀도 임계 미달"
    if False:'
assert_detect "M2 ②주입: 밀도 임계 치환 → 리터럴 다수 본문 발화" FIRE "$WORK/det_m2.py" "$ADR109" "$BODY_FIX"

# ── ③ 등가변형: 정규화 제거 → 대소문자·띄어쓰기 변형 ② 미발화 ─────────────
python3 - "$TERM_FIX" "$WORK/term_casevary.txt" <<'PY'
import io, sys
raw = io.open(sys.argv[1], encoding="utf-8").read()
# 의미 보존 표기 변형: 대소문자 + 연속 공백 (동일 신호, 표기만 다름)
raw = raw.replace("You've hit your session limit", "You've hit your  SESSION   Limit", 1)
io.open(sys.argv[2], "w", encoding="utf-8", newline="\n").write(raw)
PY
assert_detect "대조군/③ 표기 변형된 ② 는 정본 감지식에서 발화" FIRE "$WORK/detector.py" "$ADR109" \
  "$WORK/term_casevary.txt"
# 앵커는 `normalize()` 본문에 **유일**하게 걸어야 한다 — 단순 `return re.sub(...)` 로 잡으면
#   위쪽 `_canon_floor()` 가 먼저 매칭돼 floor 가드가 죽는다(엉뚱한 RED). 실제로 밟고 고쳤다.
mutate_detector "$WORK/det_m3.py" \
  '"""대소문자·연속 공백 정규화 (③ 등가변형 봉쇄 지점 — MUTANT M3 가 이 함수를 무력화한다)."""
    return re.sub(r"\s+", " ", s.strip().lower())' \
  '"""MUTANT M3 — 리터럴 정규화 제거 (대소문자·공백 변형이 매칭에서 탈락한다)."""
    return s'
assert_detect "M3 ③등가변형: 정규화 제거 → 표기 변형 ② 미발화" NOFIRE "$WORK/det_m3.py" "$ADR109" \
  "$WORK/term_casevary.txt"

# ── ④ fail-closed: ADR code-fence 삭제 → 감지집합 파생 실패 ────────────────
mkdir -p "$WORK/adr"
python3 - "$ADR109" "$WORK/adr/ADR-109-nofence.md" <<'PY'
import io, re, sys
raw = io.open(sys.argv[1], encoding="utf-8").read()
old = 'session/usage-limit 포함 detection = 다음 6 literal any-match'
assert old in raw, "SETUP: code-fence 앵커 미발견"
io.open(sys.argv[2], "w", encoding="utf-8", newline="\n").write(
    raw.replace(old, "(감지집합 code-fence 삭제됨 — MUTANT M4)", 1))
PY
assert_detect "M4 ④fail-closed: code-fence 삭제 → 파생 실패" SETUP-FAIL "$WORK/detector.py" \
  "$WORK/adr/ADR-109-nofence.md" "$TERM_FIX"

# ── ④-b ratchet floor: 정본 literal 1개 축소 → fail-closed ────────────────
python3 - "$ADR109" "$WORK/adr/ADR-109-shrunk.md" <<'PY'
import io, sys
raw = io.open(sys.argv[1], encoding="utf-8").read()
old = '"session limit"\n"usage limit"\n'
assert old in raw, "SETUP: literal 축소 앵커 미발견"
io.open(sys.argv[2], "w", encoding="utf-8", newline="\n").write(raw.replace(old, '"usage limit"\n', 1))
PY
assert_detect "M4b floor: 정본 literal 축소 → fail-closed" SETUP-FAIL "$WORK/detector.py" \
  "$WORK/adr/ADR-109-shrunk.md" "$TERM_FIX"

echo "── 결과: PASS=$PASS FAIL=$FAIL"
[ "$FAIL" -eq 0 ] || exit 1
