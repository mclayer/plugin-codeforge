#!/usr/bin/env bash
# tests/scripts/test_event_channel_resolution.sh
# CFP-2984 Phase 2 (구현 lane) — AC-14 discriminating self-test (참조 무결성).
#
# AC-14: A 소유 문서의 **사건 기록 지시**가 명명한 기록 대상을, `ADR-109 §결정 9` 가 고정한
#   **2축 값공간**(`§10 FIX Ledger` = governance FIX / `§14 Lane Evidence` = telemetry)으로
#   해소하면, 429·세션한도 사건의 지시 대상이 **전건 telemetry 축**으로 해소되고
#   **FIX Ledger 축 해소가 0건**이어야 한다.
#
# ★ 자산 정정 (iter3 F-9) — "실제 채널 레지스트리" 자산은 **부재**한다(`채널 레지스트리`·
#   `channel_registry` 전 repo grep 0 hit). 따라서 본 오라클은 기존 레지스트리를 재사용하지
#   않고, `ADR-109 §결정 9` 산문의 2축 명명을 **파싱해 값공간을 파생**한다. 값공간이 파생되지
#   않으면(절 부재·축 2개 아님·governance 축 식별 불가) **통과가 아니라 fail-closed RED** 다.
#
# ★ 경계: §10 스키마(B 소유) **무접촉** — 본 검사는 A 소유 문서의 *문면*만 읽는다.
#
# ★ 극성(polarity) 처리: 실 문서는 `§10 FIX Ledger row append **금지**` 처럼 §10 을 **금지 대상**
#   으로 명명한다. 이를 위반으로 세면 거짓 RED 다. 축 언급 직후 구간의 부정 토큰으로
#   affirm/prohibit 를 가르고, **affirm 만** 판정 대상으로 삼는다.
#
# 3방향 mutant:
#   ① 제거      M1 = §결정 9 축 정의 bullet 삭제        → 값공간 파생 실패 fail-closed RED
#   ② 주입      M2 = "429 … §10 FIX Ledger 에 row append" 지시 주입 → RED
#   ③ 등가변형  M3 = **같은 위반을 별칭으로 은닉**("FIX 원장에 기록") → 별칭 해소로 RED ★
#               M3-nc = 정상 telemetry 지시를 별칭 표기로 치환 → **PASS 유지**(대조군)
#   ④ 미해소    M4 = 값공간 밖 채널("§7 에 기록") 지시 주입 → unresolved fail-closed RED
#   ⑤ floor     M5 = telemetry 지시 전멸 → 지시 집합 소실 회피 차단 RED
#
# 대조군(INV-T4): **실 repo A 소유 corpus** 무변조 = PASS.
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
ADR141="archive/adr/ADR-141-all-opus-single-tier.md"
SKILL="skills/rate-limit-429-mitigation/SKILL.md"

# ─────────────────────────────────────────────────────────────────────────────
cat > "$WORK/checker.py" <<'PY'
#!/usr/bin/env python3
"""AC-14 사건 기록 지시 → ADR-109 §결정 9 2축 값공간 해소 (fail-closed).

사용: checker.py <root> <axis-source-relpath> <scan-relpath> [<scan-relpath> ...]
"""
import os
import re
import sys

SEC9_START = r"### §결정 9(?![0-9])"
SEC9_END = r"### §결정 10(?![0-9])"
# 축 정의 bullet — `- **§10 FIX Ledger** = governance FIX ...`
AXIS_BULLET = re.compile(r"^-\s{0,4}\*\*§\s{0,2}(\d{1,2})\s{0,2}([^*]{1,40})\*\*\s{0,4}=\s{0,4}(.{1,200})")

INCIDENT = re.compile(
    r"429|rate[- ]?limit|session limit|usage limit|세션\s?한도|리밋|failover|한도"
)
RECORD = re.compile(r"기록|append|row|marker|원장|등재|태그|write")
# 채널 참조 토큰 — 절 참조(§N, 소수점 하위절 제외) ∪ 명명형(레이블·원장).
#   명명형은 후행 `원장` 을 **흡수**한다("lane-evidence 원장" 을 두 토큰으로 쪼개면
#   뒤 조각이 bare 원장 = 미해소로 오탐한다 — 실제 이 오탐을 밟고 고쳤다).
#   bare `원장` 은 마지막 대안 — 축을 명명하지 않은 기록 대상이므로 미해소가 정답이다.
CHANNEL_TOKEN = re.compile(
    r"§\s{0,2}(\d{1,2})(?![0-9.])"
    r"|((?:FIX\s{0,2}Ledger|Lane\s{0,2}Evidence|fix[-\s]?ledger|lane[-\s]?evidence"
    r"|FIX\s{0,2}원장|lane\s{0,2}원장)(?:\s{0,2}원장)?|원장)",
    re.IGNORECASE,
)
NEGATION = re.compile(r"금지|않는다|않음|미부착|미등재|제외|아니|아님|영향\s?0|NOT|무접촉|비대상")
NEG_WINDOW = 44


def extract_section(text, start_pat, end_pat):
    ms = re.search(start_pat, text)
    if not ms:
        return None
    tail = text[ms.end():]
    me = re.search(end_pat, tail)
    end = ms.end() + me.start() if me else len(text)
    return text[ms.start():end]


def derive_value_space(axis_src_text):
    """§결정 9 산문 → {axis_id: {'sec': N, 'label': str, 'aliases': set}}.

    파생 실패(절 부재 / 축 2개 아님 / governance 축 식별 불가) = fail-closed.
    """
    sec = extract_section(axis_src_text, SEC9_START, SEC9_END)
    if sec is None:
        return None, "ADR-109 §결정 9 절 부재 — 2축 값공간 파생 불가 (fail-closed)"
    axes = []
    for line in sec.split("\n"):
        m = AXIS_BULLET.match(line.strip())
        if m:
            axes.append((int(m.group(1)), m.group(2).strip(), m.group(3)))
    if len(axes) != 2:
        return None, ("§결정 9 축 정의 bullet %d 개 (기대 정확히 2) — 값공간 미고정 "
                      "(fail-closed)" % len(axes))
    space = {}
    gov = [a for a in axes if "governance" in a[2].lower()]
    if len(gov) != 1:
        return None, ("§결정 9 에서 governance 축을 1개로 식별 불가(%d) — 축 의미 미해소 "
                      "(fail-closed)" % len(gov))
    for sec_no, label, desc in axes:
        axis_id = "governance-fix" if "governance" in desc.lower() else "telemetry"
        words = re.findall(r"[A-Za-z]+", label)
        aliases = {"§%d" % sec_no, "§ %d" % sec_no}
        if words:
            joined = " ".join(w.lower() for w in words)
            aliases |= {joined, joined.replace(" ", "-"), joined.replace(" ", ""),
                        "%s 원장" % words[0].lower(), "%s원장" % words[0].lower()}
        space[axis_id] = {"sec": sec_no, "label": label, "aliases": aliases}
    return space, None


def resolve(token_text, sec_no, space):
    """채널 토큰 → axis_id | None(미해소)."""
    if sec_no is not None:
        for axis_id, meta in space.items():
            if meta["sec"] == sec_no:
                return axis_id
        return None
    key = re.sub(r"\s+", " ", token_text.strip().lower())
    # 후행 `원장`(= ledger 의 한국어 표기)은 축 이름의 접미이지 별개 채널이 아니다.
    #   "lane-evidence 원장" → "lane-evidence" 로도 해소를 시도한다(등가 표기 흡수).
    candidates = [key]
    stripped = re.sub(r"\s{0,2}원장$", "", key).strip()
    if stripped and stripped != key:
        candidates.append(stripped)
    for cand in candidates:
        for axis_id, meta in space.items():
            for a in meta["aliases"]:
                if cand == a or cand.replace(" ", "") == a.replace(" ", ""):
                    return axis_id
    return None


def scan_directives(path, rel, space):
    """사건 기록 지시 줄 → 채널 언급별 (axis, polarity) 목록."""
    hits = []
    with open(path, encoding="utf-8") as f:
        for lno, line in enumerate(f, 1):
            s = line.rstrip("\n")
            if not (INCIDENT.search(s) and RECORD.search(s)):
                continue
            for m in CHANNEL_TOKEN.finditer(s):
                sec_no = int(m.group(1)) if m.group(1) else None
                axis = resolve(m.group(0), sec_no, space)
                after = s[m.end():m.end() + NEG_WINDOW]
                polarity = "prohibit" if NEGATION.search(after) else "affirm"
                hits.append({"rel": rel, "line": lno, "token": m.group(0).strip(),
                             "axis": axis, "polarity": polarity, "text": s.strip()[:120]})
    return hits


def main():
    root = os.path.abspath(sys.argv[1])
    axis_rel, scan_rels = sys.argv[2], sys.argv[3:]
    axis_path = os.path.join(root, axis_rel.replace("/", os.sep))
    if not os.path.isfile(axis_path):
        print("VIOLATION: 값공간 원본 %s 부재 — fail-closed" % axis_rel)
        sys.exit(1)
    with open(axis_path, encoding="utf-8") as f:
        space, err = derive_value_space(f.read())
    if space is None:
        print("VIOLATION: %s" % err)
        print("")
        print("check-event-channel-resolution: 1 violation (값공간 파생 실패)")
        sys.exit(1)

    hits = []
    for rel in scan_rels:
        p = os.path.join(root, rel.replace("/", os.sep))
        if not os.path.isfile(p):
            print("VIOLATION: 스캔 대상 %s 부재 — fail-closed" % rel)
            sys.exit(1)
        hits.extend(scan_directives(p, rel, space))

    violations = []
    affirm_tel = [h for h in hits if h["polarity"] == "affirm" and h["axis"] == "telemetry"]
    affirm_gov = [h for h in hits if h["polarity"] == "affirm" and h["axis"] == "governance-fix"]
    unresolved = [h for h in hits if h["axis"] is None]

    for h in unresolved:
        violations.append(
            "%s:%d 기록 대상 '%s' 가 2축 값공간(§%d %s / §%d %s) 으로 미해소 — fail-closed | %s"
            % (h["rel"], h["line"], h["token"],
               space["governance-fix"]["sec"], space["governance-fix"]["label"],
               space["telemetry"]["sec"], space["telemetry"]["label"], h["text"]))
    for h in affirm_gov:
        violations.append(
            "%s:%d 429·한도 사건 기록 지시가 **FIX Ledger 축**('%s')으로 해소 — §결정 9 "
            "disjoint 위반(ADR-067 RESET contamination) | %s"
            % (h["rel"], h["line"], h["token"], h["text"]))
    if not affirm_tel:
        violations.append(
            "telemetry 축으로 해소되는 affirm 지시 0건 — 지시 집합 소실(삭제로 회피) 의심, "
            "fail-closed. 최소 1건은 실재해야 검사가 의미를 가진다")

    for v in violations:
        print("VIOLATION: %s" % v)
    if violations:
        print("")
        print("check-event-channel-resolution: %d violation" % len(violations))
        sys.exit(1)
    print("check-event-channel-resolution: PASS — 값공간 2축 파생 "
          "(§%d %s = governance / §%d %s = telemetry)"
          % (space["governance-fix"]["sec"], space["governance-fix"]["label"],
             space["telemetry"]["sec"], space["telemetry"]["label"]))
    print("  지시 언급 %d 건 | affirm→telemetry %d / affirm→FIX Ledger %d / prohibit %d / 미해소 %d"
          % (len(hits), len(affirm_tel), len(affirm_gov),
             len([h for h in hits if h["polarity"] == "prohibit"]), len(unresolved)))
    sys.exit(0)


if __name__ == "__main__":
    main()
PY

build_corpus() {
  local dst="$1"
  rm -rf "$dst"
  mkdir -p "$dst/archive/adr" "$dst/skills/rate-limit-429-mitigation"
  cp "$REPO_ROOT/$ADR109" "$dst/$ADR109"
  cp "$REPO_ROOT/$ADR141" "$dst/$ADR141"
  cp "$REPO_ROOT/$SKILL"  "$dst/$SKILL"
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
  # assert_verdict <name> <PASS|RED> <root> [scan-rel ...]   (scan 생략 시 기본 3 파일)
  local name="$1" expect="$2" root="$3" verdict
  shift 3
  local scans=("$@")
  [ "${#scans[@]}" -gt 0 ] || scans=("$ADR109" "$ADR141" "$SKILL")
  set +e
  CHECK_OUT="$(python3 "$WORK/checker.py" "$root" "$ADR109" "${scans[@]}" 2>&1)"
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

echo "── AC-14 event channel resolution (2축 값공간 참조 무결성)"

# ── 대조군: 실 repo A 소유 corpus ───────────────────────────────────────────
assert_verdict "baseline/실 repo A 소유 corpus 무변조" PASS "$REPO_ROOT"
echo "$CHECK_OUT" | sed 's/^/    /'

# ── ① 제거: §결정 9 축 정의 bullet 삭제 ─────────────────────────────────────
build_corpus "$WORK/m1"
patch_file "$WORK/m1/$ADR109" \
  "- **§10 FIX Ledger** = governance FIX root cause classification" \
  "- (축 정의 삭제됨 — MUTANT M1)"
assert_verdict "M1 ①제거: §결정 9 축 정의 삭제 → 값공간 파생 실패" RED "$WORK/m1"

# ── ② 주입: 429 사건을 FIX Ledger 축에 기록하라는 지시 ─────────────────────
build_corpus "$WORK/m2"
patch_file "$WORK/m2/$SKILL" \
  "### fable-리밋 failover marker" \
  "429 재시도 사건은 §10 FIX Ledger 에 row 를 append 해 기록한다.

### fable-리밋 failover marker"
assert_verdict "M2 ②주입: FIX Ledger 축 지시 주입" RED "$WORK/m2"

# ── ③ 등가변형: 같은 위반을 **별칭**으로 은닉 ───────────────────────────────
build_corpus "$WORK/m3"
patch_file "$WORK/m3/$SKILL" \
  "### fable-리밋 failover marker" \
  "429 재시도 사건은 FIX 원장에 기록한다.

### fable-리밋 failover marker"
assert_verdict "M3 ③등가변형: 별칭('FIX 원장')으로 위반 은닉" RED "$WORK/m3"

# ── ③ 대조군: 정상 telemetry 지시를 별칭 표기로 치환해도 PASS ───────────────
build_corpus "$WORK/m3nc"
patch_file "$WORK/m3nc/$SKILL" \
  "fable→opus failover(Step 3.3) 발동 시 §14 Lane Evidence transcript 에" \
  "fable→opus failover(Step 3.3) 발동 시 lane-evidence 원장 transcript 에 429 태그를"
assert_verdict "M3-nc ③대조군: 정상 지시의 별칭 표기는 PASS" PASS "$WORK/m3nc"

# ── ④ 미해소: 값공간 밖 채널 지시 ───────────────────────────────────────────
build_corpus "$WORK/m4"
patch_file "$WORK/m4/$SKILL" \
  "### fable-리밋 failover marker" \
  "429 재시도 사건 marker 는 §7 에 기록한다.

### fable-리밋 failover marker"
assert_verdict "M4 ④미해소: 값공간 밖 채널(§7) = fail-closed" RED "$WORK/m4"

# ── ⑤ floor: telemetry 지시 전멸 ────────────────────────────────────────────
# (a) 외과적 삭제 — §14 표기 **및 명명형 별칭**을 함께 지워야 실제로 전멸한다.
#     ★ 최초 구현은 §14 만 지웠는데 `Lane Evidence` 명명형이 살아남아 floor 가 안 떨어졌다.
#       그 사실 자체가 별칭 해소가 실제로 동작한다는 증거이므로 기록해 둔다.
build_corpus "$WORK/m5"
python3 - "$WORK/m5" "$ADR109" "$ADR141" "$SKILL" <<'PY'
import io, os, re, sys
root = sys.argv[1]
INCIDENT = re.compile(r"429|rate[- ]?limit|session limit|usage limit|세션\s?한도|리밋|failover|한도")
RECORD = re.compile(r"기록|append|row|marker|원장|등재|태그|write")
TEL = re.compile(r"§\s{0,2}14|Lane\s{0,2}Evidence|lane[-\s]?evidence", re.IGNORECASE)
for rel in sys.argv[2:]:
    p = os.path.join(root, rel.replace("/", os.sep))
    out = []
    for line in io.open(p, encoding="utf-8").read().split("\n"):
        if INCIDENT.search(line) and RECORD.search(line) and TEL.search(line):
            out.append(TEL.sub("(축 표기 제거됨)", line))
        else:
            out.append(line)
    io.open(p, "w", encoding="utf-8", newline="\n").write("\n".join(out))
PY
assert_verdict "M5a ⑤floor: telemetry 지시 외과적 전멸 = fail-closed" RED "$WORK/m5"

# (b) 지시 집합이 애초에 없는 정의역 — 통과가 아니라 RED 여야 한다(빈 정의역 = 공허 GREEN 금지).
assert_verdict "M5b ⑤floor: 지시 0건 정의역(ADR-179) = fail-closed" RED "$REPO_ROOT" \
  "archive/adr/ADR-179-agent-salvage-bundle-handoff.md"

# ── 형제 회귀: 극성 처리가 정상 '금지' 문장을 위반으로 오탐하지 않는가 ──────
build_corpus "$WORK/sib"
assert_verdict "형제/무변조 사본 재확인 (금지 문장 오탐 0)" PASS "$WORK/sib"
# 금지 문장을 **긍정으로 뒤집으면** 잡히는가 (극성 처리가 살아있는지)
build_corpus "$WORK/sib2"
patch_file "$WORK/sib2/$SKILL" \
  "- **§10 FIX Ledger row append 금지** (ADR-109 §결정 9 boundary): 429 retry" \
  "- **§10 FIX Ledger row append 필수** (극성 반전 MUTANT): 429 retry"
assert_verdict "형제/극성 반전(금지→필수) 검출" RED "$WORK/sib2"

echo "── 결과: PASS=$PASS FAIL=$FAIL"
[ "$FAIL" -eq 0 ] || exit 1
