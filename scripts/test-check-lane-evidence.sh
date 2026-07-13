#!/usr/bin/env bash
# CFP-2270 — Test harness for check-lane-evidence.sh §14 면제 분기 (ADR-031 Amendment 2).
#
# D2 (#2248) 게이트 적합성: wrapper-self dogfood (repo-kind `mixed`) §14 면제 + 회귀 가드 +
# fail-safe 검증. 8 케이스 (설계 §8 Test Contract):
#   1. exempt           — mixed sandbox + Story file 부재 → [N/A] 면제, FAIL 0
#   2-4. 회귀 가드       — consumer/plugin/unknown sandbox + Story 누락 → advisory-red [FAIL] 보존
#   5. over-broad 차단   — mixed sandbox 인데 Story file 실존 → 정상평가 (면제 안 함)
#   6-8. fail-safe       — python 미탐지 / detect script 부재 / 비-mixed exit → 면제 억제
#
# 명시 assert: grep -q '\[N/A\]' (면제) / grep -q '\[FAIL\]' (보존).
# 형제 harness scripts/test-check-doc-locations.sh 컨벤션 (mktemp -d sandbox + cleanup).
#
# detect-repo-kind 경로 해석: check-lane-evidence.sh 는 CLAUDE_PLUGIN_ROOT env 우선 →
#   fallback ${BASH_SOURCE[0]}/../templates/scripts/detect-repo-kind.py. 본 harness 는 각
#   sandbox 에 script + templates/scripts/detect-repo-kind.py 를 배치하고 cd sandbox 후 실행 —
#   --repo-root . 가 sandbox 를 보므로 sandbox 의 신호 파일(.claude-plugin / .claude/_overlay)이
#   repo-kind 를 결정적으로 결정한다.
#
# Usage: bash scripts/test-check-lane-evidence.sh
set -uo pipefail

cd "$(dirname "$0")/.."
REPO_ROOT="$(pwd)"

SCRIPT_SRC="$REPO_ROOT/scripts/check-lane-evidence.sh"
DETECT_SRC="$REPO_ROOT/templates/scripts/detect-repo-kind.py"

PASS=0
FAIL=0

# python interpreter 탐지 (harness 자체 sanity)
PY=""
if command -v python3 >/dev/null 2>&1; then PY="$(command -v python3)"
elif command -v python >/dev/null 2>&1; then PY="$(command -v python)"; fi
if [ -z "$PY" ]; then
    echo "FATAL: python3/python 미탐지 — harness 실행 불가" >&2
    exit 2
fi

# sandbox 골격 생성: $tmp/scripts/check-lane-evidence.sh + $tmp/templates/scripts/detect-repo-kind.py
# signals 인자 = 공백구분 토큰: plugin / overlay (각 신호 파일 생성)
make_sandbox() {
    local tmp="$1"; shift
    mkdir -p "$tmp/scripts" "$tmp/templates/scripts"
    cp "$SCRIPT_SRC" "$tmp/scripts/check-lane-evidence.sh"
    cp "$DETECT_SRC" "$tmp/templates/scripts/detect-repo-kind.py"
    local sig
    for sig in "$@"; do
        case "$sig" in
            plugin)
                mkdir -p "$tmp/.claude-plugin"
                printf '{}' > "$tmp/.claude-plugin/plugin.json"
                ;;
            overlay)
                mkdir -p "$tmp/.claude/_overlay"
                printf 'codeforge: {}' > "$tmp/.claude/_overlay/project.yaml"
                ;;
        esac
    done
}

# 단일 케이스 실행.
#   $1 name / $2 expect_grep (있어야 하는 패턴) / $3 not_grep (없어야 함, 빈문자열=skip)
#   $4 envset (실행 시 prepend env, 예: PATH=... 또는 CLAUDE_PLUGIN_ROOT=...)
#   $5 setup_fn (sandbox cwd 에서 추가 mutation, 빈문자열=skip)
#   $6 extra_args (check-lane-evidence.sh 추가 인자, 빈문자열=없음)
#   $7+ signals (plugin / overlay)
run_case() {
    local name="$1" expect="$2" not_expect="$3" envset="$4" setup_fn="$5" extra_args="$6"
    shift 6
    local signals=("$@")

    local tmp
    tmp="$(mktemp -d)"
    if [ "${#signals[@]}" -gt 0 ]; then
        make_sandbox "$tmp" "${signals[@]}"
    else
        make_sandbox "$tmp"
    fi

    if [ -n "$setup_fn" ]; then ( cd "$tmp" && eval "$setup_fn" ); fi

    # 실행: sandbox 안에서. STRICT 미사용 — 면제/보존 모두 default mode advisory 출력 grep 판정.
    local out
    out="$( cd "$tmp" && eval "$envset" bash scripts/check-lane-evidence.sh $extra_args 2>&1 )"

    local ok=1
    if ! printf '%s' "$out" | grep -q "$expect"; then
        ok=0
        echo "  expected pattern not found: $expect"
    fi
    if [ -n "$not_expect" ] && printf '%s' "$out" | grep -q "$not_expect"; then
        ok=0
        echo "  forbidden pattern found: $not_expect"
    fi

    if [ "$ok" -eq 1 ]; then
        echo "PASS $name"
        PASS=$((PASS + 1))
    else
        echo "FAIL $name"
        printf '%s\n' "$out" | sed 's/^/    | /'
        FAIL=$((FAIL + 1))
    fi

    rm -rf "$tmp"
}

# Story file (§14 YAML block 포함) 생성 — over-broad 차단 케이스용.
STORY_WITH_14='mkdir -p docs/stories; cat > docs/stories/CFP-TEST.md <<EOF
## §14 Lane Evidence
\`\`\`yaml
- lane: 설계
  iteration: 1
\`\`\`
EOF'

# CFP-2293 sibling: no-§ §14 heading (`## 14.`) — story-init renderer 컨벤션(§ 없음).
# §? 수용 fix 전에는 extract_section_14 가 못 잡아 [FAIL](YAML block 부재) → fix 후 [OK].
STORY_WITH_14_NOSEC='mkdir -p docs/stories; cat > docs/stories/CFP-TEST-NOSEC.md <<EOF
## 14. Lane Evidence
\`\`\`yaml
- lane: 설계
  iteration: 1
\`\`\`
EOF'

# 비-mixed stub detector (case 8): 항상 unknown(exit 3) 반환.
DETECT_STUB='printf "#!/usr/bin/env python3\nprint(\"unknown\")\nimport sys; sys.exit(3)\n" > templates/scripts/detect-repo-kind.py'

# case 6 (python 신호 불가) 용 shadow bin: 실제 PATH 는 유지(bash/coreutils 동작 보장)하되
# python3/python 을 stdout 무방출 + 비-0 exit stub 으로 prepend shadow → check-lane-evidence.sh
# 내부 python 호출이 mixed 신호를 못 얻음 → fail-safe (면제 억제). PATH 를 비우면 Windows
# Git Bash(MSYS2)에서 bash 자체 DLL 로드가 깨지므로 shadow 방식을 사용(cross-platform 견고).
SHADOW_BIN="$(mktemp -d)"
for stub in python3 python; do
    printf '#!/bin/sh\nexit 127\n' > "$SHADOW_BIN/$stub"
    chmod +x "$SHADOW_BIN/$stub"
done
cleanup() { rm -rf "$SHADOW_BIN"; }
trap cleanup EXIT

echo "=== check-lane-evidence.sh §14 면제 harness (ADR-031 Amendment 2) ==="

# 1. exempt: mixed + Story file 부재 → [N/A], FAIL 0
run_case "1 exempt-mixed-no-story" '\[N/A\]' '\[FAIL\]' "" "" "" plugin overlay

# 2. 회귀: consumer (overlay only) + Story 누락 → advisory-red [FAIL] 보존
run_case "2 regress-consumer-no-exempt" '\[FAIL\]' '\[N/A\]' "" "" "" overlay

# 3. 회귀: plugin (plugin.json only) + Story 누락 → [FAIL] 보존
run_case "3 regress-plugin-no-exempt" '\[FAIL\]' '\[N/A\]' "" "" "" plugin

# 4. 회귀: unknown (신호 없음) + Story 누락 → [FAIL] 보존
run_case "4 regress-unknown-no-exempt" '\[FAIL\]' '\[N/A\]' "" "" ""

# 5. over-broad 차단: mixed + Story file 실존(§14 보유) → 정상 [OK], 면제 안 함
#    --story 로 Story file 직접 주입 (sandbox 는 git 무관 → branch auto-detect 불가).
run_case "5 mixed-with-story-no-exempt" '\[OK\]' '\[N/A\]' \
    "" "$STORY_WITH_14" "--story docs/stories/CFP-TEST.md" plugin overlay

# 5b. no-§ §14 (`## 14.`): renderer 컨벤션 story → §? 로 파싱되어 [OK] (CFP-2293 sibling 회귀가드)
run_case "5b mixed-with-nosec-story" '\[OK\]' '\[N/A\]' \
    "" "$STORY_WITH_14_NOSEC" "--story docs/stories/CFP-TEST-NOSEC.md" plugin overlay

# 6. fail-safe: python 신호 불가 (python3/python stub 이 비-0 exit, stdout 무방출) → 면제 억제
run_case "6 failsafe-no-python" '\[FAIL\]' '\[N/A\]' \
    "PATH=$SHADOW_BIN:\$PATH" "" "" plugin overlay

# 7. fail-safe: detect script 부재 (CLAUDE_PLUGIN_ROOT 가짜) → 면제 억제
run_case "7 failsafe-script-absent" '\[FAIL\]' '\[N/A\]' \
    'CLAUDE_PLUGIN_ROOT=/nonexistent-plugin-root' "" "" plugin overlay

# 8. fail-safe: 비-mixed exit (detect stub 이 unknown/exit3 반환) → rc!=2 → 면제 억제
run_case "8 failsafe-detect-nonmixed" '\[FAIL\]' '\[N/A\]' \
    "" "$DETECT_STUB" "" plugin overlay

# ── CFP-2471 (Epic CFP-2468 W3) 축③ fan-out 관측 회귀 가드 ──────────────────
# stale roster 정정 + <6 deputy row silent SKIP → honest WARN/SKIP 분기.
# 별도 fixture-only 케이스 (sandbox 불요 — --story 직접 주입). run_case 와 분리한 lightweight runner.
echo "--- CFP-2471 W3 축③ fan-out 관측 ---"

# 3 deputy row (1~5, env=1 fan-out 미달) → honest WARN (silent SKIP 차단)
WARN_STORY="$(mktemp -d)/CFP-WARN.md"
cat > "$WARN_STORY" <<'EOF'
## §14 Lane Evidence
```yaml
- lane: 설계
  spawned_at: 2026-06-30T09:00:00Z
- lane: 설계
  spawned_at: 2026-06-30T09:00:01Z
- lane: 설계
  spawned_at: 2026-06-30T09:00:02Z
```
EOF
warn_out="$(bash "$SCRIPT_SRC" --story "$WARN_STORY" --check-parallelization 2>&1)"
if printf '%s' "$warn_out" | grep -q 'PARALLELIZATION WARN'; then
    echo "PASS W3-3a 1~5 deputy row → honest WARN (silent SKIP 차단)"
    PASS=$((PASS + 1))
else
    echo "FAIL W3-3a 1~5 deputy row 가 WARN 미발화 (silent SKIP 회귀)"
    printf '%s\n' "$warn_out" | sed 's/^/    | /'
    FAIL=$((FAIL + 1))
fi
rm -rf "$(dirname "$WARN_STORY")"

# 0 deputy row (env=0) → honest SKIP 사유 명시 (silent 0)
ZERO_STORY="$(mktemp -d)/CFP-ZERO.md"
cat > "$ZERO_STORY" <<'EOF'
## §14 Lane Evidence
```yaml
- lane: 구현
  iteration: 1
```
EOF
zero_out="$(bash "$SCRIPT_SRC" --story "$ZERO_STORY" --check-parallelization 2>&1)"
if printf '%s' "$zero_out" | grep -q 'env=0 fan-out 관측 불가'; then
    echo "PASS W3-3b 0 deputy row → honest SKIP 사유 명시 (env=0)"
    PASS=$((PASS + 1))
else
    echo "FAIL W3-3b 0 deputy row 가 honest SKIP 사유 미명시 (meta-hollow-gate 회귀)"
    printf '%s\n' "$zero_out" | sed 's/^/    | /'
    FAIL=$((FAIL + 1))
fi
rm -rf "$(dirname "$ZERO_STORY")"

# stale roster 정정 회귀: 헤더 주석에 현 6 permanent 토큰 존재 + 구 토큰 (OpRiskArch/DataMigrationArch) 부재
if grep -q 'InfraOperationalArchitectAgent' "$SCRIPT_SRC" && grep -q 'APIContractArchitectAgent' "$SCRIPT_SRC"; then
    echo "PASS W3-3c stale roster 정정 — 현 6 permanent 토큰 (InfraOperationalArchitectAgent/APIContractArchitectAgent) 존재"
    PASS=$((PASS + 1))
else
    echo "FAIL W3-3c 현 6 permanent deputy 토큰 부재 (stale roster 회귀)"
    FAIL=$((FAIL + 1))
fi

# ══════════════════════════════════════════════════════════════════════════════
# CFP-2652 (Epic CFP-2468 W3 follow-up) — 정확성 갭 3건 self-test
#   gap (a) env-absence vs evidence-absence re-key (TC-A1~A6 + MUT-A1/A2)
#   gap (c) label↔block write-back Check 7 + SSOT 단일성 (TC-C1~C5 + MUT-C/SSOT)
# execution-backed (검사연극 금지) — 각 케이스 실 exit/출력 grep. equivalent mutant(생존 EXPECTED)
#   vs real-kill(RED) 구별 (hollow 오독 차단).
# ══════════════════════════════════════════════════════════════════════════════
echo ""
echo "--- CFP-2652 gap (a) env-absence vs evidence-absence re-key ---"

WORKFLOW_SRC="$REPO_ROOT/.github/workflows/phase-gate-mergeable.yml"
SSOT_SRC="$REPO_ROOT/docs/inter-plugin-contracts/gate-lane-map-v1.yaml"
C2652_TMP="$(mktemp -d)"
cleanup_2652() { rm -rf "$C2652_TMP"; }
trap 'cleanup; cleanup_2652' EXIT

# fixture writer: $1=name → path (§14 YAML block wrapper)
mk_story() { local p="$C2652_TMP/$1.md"; shift; { echo '## §14 Lane Evidence'; echo '```yaml'; cat; echo '```'; } > "$p"; echo "$p"; }

# lightweight assertion: $1 name / $2 out / $3 expect(literal, 빈=skip) / $4 not_expect(literal, 빈=skip)
assert_out() {
    local name="$1" out="$2" expect="$3" not_expect="${4:-}" ok=1
    if [ -n "$expect" ] && ! printf '%s' "$out" | grep -qF "$expect"; then ok=0; echo "  expected(!found): $expect"; fi
    if [ -n "$not_expect" ] && printf '%s' "$out" | grep -qF "$not_expect"; then ok=0; echo "  forbidden(found): $not_expect"; fi
    if [ "$ok" -eq 1 ]; then echo "PASS $name"; PASS=$((PASS+1)); else echo "FAIL $name"; printf '%s\n' "$out" | sed 's/^/    | /'; FAIL=$((FAIL+1)); fi
}

# TC-A1 (env-absence 무손상, AC-3): 설계 행 0 → env=0 SKIP. evidence-absence 부재.
A1="$(mk_story A1-env-absence <<'EOF'
- lane: 구현
  iteration: 1
EOF
)"
out="$(bash "$SCRIPT_SRC" --story "$A1" --check-parallelization 2>&1)"
assert_out "TC-A1 env-absence 0행 → env=0 SKIP" "$out" "env=0 fan-out 관측 불가" "evidence-absence"

# TC-A2 (full evidence-absence, AC-1): 설계 행 6, spawned_at 全無(6/0) → evidence-absence WARN, env=0 부재.
#   (6/0 full → TC-A3 6/3 partial → TC-A6 6/6 complete: 동일 design_rows=6 축 progression 대비.)
A2="$(mk_story A2-full-evabsence <<'EOF'
- lane: 설계
  iteration: 1
- lane: 설계
  iteration: 2
- lane: 설계
  iteration: 3
- lane: 설계
  iteration: 4
- lane: 설계
  iteration: 5
- lane: 설계
  iteration: 6
EOF
)"
out="$(bash "$SCRIPT_SRC" --story "$A2" --check-parallelization 2>&1)"
assert_out "TC-A2 full evidence-absence(6/0) → WARN, env=0 부재" "$out" "evidence-absence" "env=0"

# TC-A3 (★partial evidence-absence, Codex P2): 설계 행 6, valid spawned_at 3 → evidence-absence,
#   "fan-out 미달"·env=0 문자열 부재 (partial 을 fan-out 미달/env=0 로 오분류하지 않음).
A3="$(mk_story A3-partial <<'EOF'
- lane: 설계
  spawned_at: 2026-06-30T09:00:00Z
- lane: 설계
  spawned_at: 2026-06-30T09:00:01Z
- lane: 설계
  spawned_at: 2026-06-30T09:00:02Z
- lane: 설계
  iteration: 4
- lane: 설계
  iteration: 5
- lane: 설계
  iteration: 6
EOF
)"
out="$(bash "$SCRIPT_SRC" --story "$A3" --check-parallelization 2>&1)"
assert_out "TC-A3 ★partial(6/3) → evidence-absence, fan-out 미달 부재" "$out" "evidence-absence" "fan-out 미달"
assert_out "TC-A3 ★partial(6/3) → env=0 부재" "$out" "evidence-absence" "env=0"

# TC-A4 (진짜 fan-out 미달): 설계 행 3, 全 유효 spawned_at → fan-out 미달 WARN "3<6". evidence-absence 부재.
A4="$(mk_story A4-fanout <<'EOF'
- lane: 설계
  spawned_at: 2026-06-30T09:00:00Z
- lane: 설계
  spawned_at: 2026-06-30T09:00:01Z
- lane: 설계
  spawned_at: 2026-06-30T09:00:02Z
EOF
)"
out="$(bash "$SCRIPT_SRC" --story "$A4" --check-parallelization 2>&1)"
assert_out "TC-A4 진짜 fan-out 미달(3/3) → '3<6'" "$out" "3<6" "evidence-absence"

# TC-A5 (EC-1 malformed): 설계 행 2, spawned_at malformed → evidence-absence (env=0 아님).
A5="$(mk_story A5-malformed <<'EOF'
- lane: 설계
  spawned_at: not-a-valid-date
- lane: 설계
  spawned_at: also-bad
EOF
)"
out="$(bash "$SCRIPT_SRC" --story "$A5" --check-parallelization 2>&1)"
assert_out "TC-A5 EC-1 malformed(2/0valid) → evidence-absence, env=0 부재" "$out" "evidence-absence" "env=0"

# TC-A6 (정상 완비): 설계 행 6, 全 유효 diff<60s → OK. WARN/evidence-absence 부재.
A6="$(mk_story A6-ok <<'EOF'
- lane: 설계
  spawned_at: 2026-06-30T09:00:00Z
- lane: 설계
  spawned_at: 2026-06-30T09:00:01Z
- lane: 설계
  spawned_at: 2026-06-30T09:00:02Z
- lane: 설계
  spawned_at: 2026-06-30T09:00:03Z
- lane: 설계
  spawned_at: 2026-06-30T09:00:04Z
- lane: 설계
  spawned_at: 2026-06-30T09:00:05Z
EOF
)"
out="$(bash "$SCRIPT_SRC" --story "$A6" --check-parallelization 2>&1)"
assert_out "TC-A6 정상 완비(6/6) → PARALLELIZATION OK" "$out" "PARALLELIZATION OK" "evidence-absence"

echo ""
echo "--- CFP-2652 gap (a) mutation (equivalent 생존 vs real-kill RED 구별) ---"

# 순수 bash literal-string mutation (python/sed 서브프로세스 fork 회피 — Windows/MSYS fork 안정성 +
#   heredoc-in-command-subst 신호파이프 실패 근절). 0=적용 성공 / 3=anchor 부재.
mutate_file() {
    local src="$1" search="$2" replace="$3" dst="$4" content
    content="$(cat "$src")"
    [[ "$content" == *"$search"* ]] || return 3
    printf '%s\n' "${content//"$search"/"$replace"}" > "$dst"
}
mutate() { mutate_file "$SCRIPT_SRC" "$1" "$2" "$3"; }   # SCRIPT_SRC 전용 shortcut
# (ii)↔(iii) 순수 swap (elif block 재배치, 닫는 fi 는 두 elif 뒤 유지) — mapfile builtin (fork 0).
mutate_swap() {
    local dst="$1"; mapfile -t L < "$SCRIPT_SRC"
    local ii=-1 iii=-1 ivc=-1 fic=-1 i
    for i in "${!L[@]}"; do
        [ $ii  -lt 0 ] && [[ "${L[$i]}" == *'elif [ "$spawned_at_count" -lt "$design_rows" ]; then'* ]] && ii=$i
        [ $iii -lt 0 ] && [[ "${L[$i]}" == *'elif [ "$spawned_at_count" -eq "$design_rows" ] && [ "$design_rows" -lt 6 ]; then'* ]] && iii=$i
        [ $ivc -lt 0 ] && [[ "${L[$i]}" == *'# (iv) design_rows >= 6'* ]] && ivc=$i
    done
    { [ $ii -ge 0 ] && [ $iii -gt $ii ] && [ $ivc -gt $iii ]; } || return 3
    # 체인을 닫는 `    fi` = iii 이후 ~ (iv) 주석 이전 구간의 유일한 4-space fi 라인.
    for ((i=iii;i<ivc;i++)); do [[ "${L[$i]}" == '    fi' ]] && { fic=$i; break; }; done
    [ $fic -ge 0 ] || return 3
    local out=() k
    for ((k=0;k<ii;k++));    do out+=("${L[$k]}"); done       # head (if(i)..return 0)
    for ((k=iii;k<fic;k++)); do out+=("${L[$k]}"); done       # (iii) elif..return 0 먼저
    for ((k=ii;k<iii;k++));  do out+=("${L[$k]}"); done       # (ii) elif..return 0 나중
    for ((k=fic;k<${#L[@]};k++)); do out+=("${L[$k]}"); done  # fi + 나머지 (iv..)
    printf '%s\n' "${out[@]}" > "$dst"
}

# 원본(unmutated) 출력 = positive control (원본엔 token 존재해야 discriminating 성립).
OUT_A2="$(bash "$SCRIPT_SRC" --story "$A2" --check-parallelization 2>&1)"
OUT_A3="$(bash "$SCRIPT_SRC" --story "$A3" --check-parallelization 2>&1)"
OUT_A4="$(bash "$SCRIPT_SRC" --story "$A4" --check-parallelization 2>&1)"
OUT_A6="$(bash "$SCRIPT_SRC" --story "$A6" --check-parallelization 2>&1)"

# real-kill: 원본 present ∧ mutant absent → PASS. 원본 absent(positive-control 실패) 또는 mutant present(생존) → FAIL.
assert_kill2() {
    local name="$1" orig="$2" mut="$3" tok="$4"
    if ! printf '%s' "$orig" | grep -qF "$tok"; then echo "FAIL $name (positive-control 실패 — 원본에 '$tok' 부재)"; FAIL=$((FAIL+1)); return; fi
    if printf '%s' "$mut" | grep -qF "$tok"; then echo "FAIL $name (mutation SURVIVED — '$tok' 잔존)"; printf '%s\n' "$mut" | sed 's/^/    | /'; FAIL=$((FAIL+1));
    else echo "PASS $name (real kill — 원본 present ∧ mutant absent)"; PASS=$((PASS+1)); fi
}
# equivalent: 원본 present ∧ mutant present(동작 불변) → PASS(생존 EXPECTED, AC-9 계수 제외).
assert_equiv2() {
    local name="$1" orig="$2" mut="$3" tok="$4"
    if ! printf '%s' "$orig" | grep -qF "$tok"; then echo "FAIL $name (positive-control 실패 — 원본에 '$tok' 부재)"; FAIL=$((FAIL+1)); return; fi
    if printf '%s' "$mut" | grep -qF "$tok"; then echo "PASS $name (equivalent mutant — 생존 EXPECTED, '$tok' 보존, AC-9 계수 제외)"; PASS=$((PASS+1));
    else echo "FAIL $name (equivalent 이 동작 변경 — mutant 에서 '$tok' 소실)"; printf '%s\n' "$mut" | sed 's/^/    | /'; FAIL=$((FAIL+1)); fi
}
# 각 mutation apply 검증 후 실행. anchor 부재/미적용 시 명시 FAIL (silent false-pass 차단).
run_mut() {  # $1=dst $2=fixture-story → mutant 출력 echo (미적용 시 "__MUT_APPLY_FAIL__")
    local dst="$1" story="$2"
    [ -s "$dst" ] || { echo "__MUT_APPLY_FAIL__"; return; }
    bash "$dst" --story "$story" --check-parallelization 2>&1
}

# MUT-A1: design-row 카운터 → 항상 0. TC-A2/A3(evidence-absence) real kill.
M="$C2652_TMP/mut-a1.sh"; mutate 'print drows+0' 'print 0' "$M" || echo "  MUT-A1 anchor 부재"
assert_kill2 "MUT-A1 counter→0 kills TC-A2"          "$OUT_A2" "$(run_mut "$M" "$A2")" "evidence-absence"
assert_kill2 "MUT-A1 counter→0 kills TC-A3(partial)" "$OUT_A3" "$(run_mut "$M" "$A3")" "evidence-absence"

# MUT-A2(b) equivalent: (iii)/(iv) equality 가드 == → <= (partial 을 (ii) 선점 → (iii)/(iv) 도달점은 항상
#   ==design_rows → <= ≡ ==, 동작 불변). 생존 EXPECTED (AC-9 계수 제외).
M="$C2652_TMP/mut-a2b.sh"; mutate '[ "$spawned_at_count" -eq "$design_rows" ] && [ "$design_rows" -lt 6 ]' '[ "$spawned_at_count" -le "$design_rows" ] && [ "$design_rows" -lt 6 ]' "$M" || echo "  MUT-A2(b) anchor 부재"
assert_equiv2 "MUT-A2(b) ==→<= equivalent (TC-A6 OK 보존)"    "$OUT_A6" "$(run_mut "$M" "$A6")" "PARALLELIZATION OK"
assert_equiv2 "MUT-A2(b) ==→<= equivalent (TC-A4 '3<6' 보존)" "$OUT_A4" "$(run_mut "$M" "$A4")" "3<6"

# MUT-A2(a) 순수 순서 swap (ii)↔(iii) = equivalent (상호배타 가드 → 재배치해도 동작 불변). 생존 EXPECTED.
M="$C2652_TMP/mut-a2a.sh"; mutate_swap "$M" || echo "  MUT-A2(a) swap anchor 부재"
assert_equiv2 "MUT-A2(a) pure-swap equivalent (TC-A3 evidence-absence 보존)" "$OUT_A3" "$(run_mut "$M" "$A3")" "evidence-absence"
assert_equiv2 "MUT-A2(a) pure-swap equivalent (TC-A4 '3<6' 보존)"            "$OUT_A4" "$(run_mut "$M" "$A4")" "3<6"

# MUT-A2(c) real-kill (게이트 무결성 backstop = (ii)-축):
#   (ii) 제거 (guard false) → partial/full 미분류 → evidence-absence kill (TC-A2 는 (iv) timing 진입).
M="$C2652_TMP/mut-a2c1.sh"; mutate 'elif [ "$spawned_at_count" -lt "$design_rows" ]; then' 'elif false; then' "$M" || echo "  MUT-A2(c)-제거 anchor 부재"
assert_kill2 "MUT-A2(c) (ii)-제거 kills TC-A2"          "$OUT_A2" "$(run_mut "$M" "$A2")" "evidence-absence"
assert_kill2 "MUT-A2(c) (ii)-제거 kills TC-A3(partial)" "$OUT_A3" "$(run_mut "$M" "$A3")" "evidence-absence"
#   (ii) 조임 < → ==0 → partial(6/3) 미매칭 → TC-A3 kill.
M="$C2652_TMP/mut-a2c2.sh"; mutate 'elif [ "$spawned_at_count" -lt "$design_rows" ]; then' 'elif [ "$spawned_at_count" -eq 0 ]; then' "$M" || echo "  MUT-A2(c)-조임 anchor 부재"
assert_kill2 "MUT-A2(c) (ii)-조임<→==0 kills TC-A3(partial)" "$OUT_A3" "$(run_mut "$M" "$A3")" "evidence-absence"
#   (ii) 넓힘 < → <= → 완비 케이스 오흡수 → TC-A6(OK)·TC-A4('3<6') kill.
M="$C2652_TMP/mut-a2c3.sh"; mutate 'elif [ "$spawned_at_count" -lt "$design_rows" ]; then' 'elif [ "$spawned_at_count" -le "$design_rows" ]; then' "$M" || echo "  MUT-A2(c)-넓힘 anchor 부재"
assert_kill2 "MUT-A2(c) (ii)-넓힘<→<= kills TC-A6" "$OUT_A6" "$(run_mut "$M" "$A6")" "PARALLELIZATION OK"
assert_kill2 "MUT-A2(c) (ii)-넓힘<→<= kills TC-A4" "$OUT_A4" "$(run_mut "$M" "$A4")" "3<6"

echo ""
echo "--- CFP-2652 gap (c) label↔block write-back Check 7 ---"

# PR body(+## Lane evidence 블록) fixture writer
mk_block() { local p="$C2652_TMP/$1.md"; shift; cat > "$p"; echo "$p"; }
mk_labels() { local p="$C2652_TMP/$1.txt"; shift; printf '%s\n' "$@" > "$p"; echo "$p"; }

# #2484-shape: gate:requirements-review-pass label ∧ 요구사항-리뷰 행 부재 (요구사항 PASS 는 별 lane)
BLOCK_2484="$(mk_block block-2484 <<'EOF'
## Summary
carrier PR body.
## Lane evidence

- 요구사항: PASS
- 설계: PASS
- 설계-리뷰: PASS
- 구현: PASS
- 구현-리뷰: SKIPPED
- 구현-테스트: SKIPPED
- 보안-테스트: SKIPPED

## Something else
tail.
EOF
)"
LABELS_RR="$(mk_labels labels-rr 'gate:requirements-review-pass' 'phase:구현')"

# TC-C1 (label↔block mismatch fire, AC-5): #2484-shape → Check 7 write-back 불일치.
out="$(bash "$SCRIPT_SRC" --story /dev/null --pr-block-file "$BLOCK_2484" --pr-labels-file "$LABELS_RR" 2>&1)"
assert_out "TC-C1 #2484-shape mismatch → Check 7 fire" "$out" "Check 7 write-back 불일치" ""
assert_out "TC-C1 mismatch 메시지에 정확 lane(요구사항-리뷰)" "$out" "요구사항-리뷰" ""

# TC-C2 (정합 no-fire, AC-6): 요구사항-리뷰 PASS 행 존재 → 무경고.
BLOCK_OK="$(mk_block block-ok <<'EOF'
## Lane evidence

- 요구사항: PASS
- 요구사항-리뷰: PASS
- 설계: PASS
- 설계-리뷰: PASS

## end
EOF
)"
out="$(bash "$SCRIPT_SRC" --story /dev/null --pr-block-file "$BLOCK_OK" --pr-labels-file "$LABELS_RR" 2>&1)"
assert_out "TC-C2 정합 → Check 7 no-fire ([OK])" "$out" "Check 7 label↔block write-back 정합" "Check 7 write-back 불일치"

# TC-C3 (shape-aware): 요구사항 PASS 존재하나 요구사항-리뷰 label→행 부재 = 별 lane, 정확 검출 (혼동 0).
BLOCK_SHAPE="$(mk_block block-shape <<'EOF'
## Lane evidence

- 요구사항: PASS
- 설계: PASS

## end
EOF
)"
out="$(bash "$SCRIPT_SRC" --story /dev/null --pr-block-file "$BLOCK_SHAPE" --pr-labels-file "$LABELS_RR" 2>&1)"
assert_out "TC-C3 shape-aware (요구사항≠요구사항-리뷰) → fire" "$out" "Check 7 write-back 불일치" ""
assert_out "TC-C3 shape-aware 정확 lane 지목(요구사항-리뷰)" "$out" "요구사항-리뷰" ""

# TC-C4 (§14 독립성, EC-3): dogfood(mixed) PR §14 면제([N/A])여도 label↔block Check 7 독립 실행.
C4="$C2652_TMP/c4"
mkdir -p "$C4/scripts" "$C4/templates/scripts" "$C4/docs/inter-plugin-contracts" "$C4/.claude-plugin" "$C4/.claude/_overlay"
cp "$SCRIPT_SRC" "$C4/scripts/"; cp "$DETECT_SRC" "$C4/templates/scripts/"
cp "$SSOT_SRC" "$C4/docs/inter-plugin-contracts/"
printf '{}' > "$C4/.claude-plugin/plugin.json"; printf 'codeforge: {}' > "$C4/.claude/_overlay/project.yaml"
cp "$BLOCK_2484" "$C4/block.md"; cp "$LABELS_RR" "$C4/labels.txt"
out="$(cd "$C4" && bash scripts/check-lane-evidence.sh --pr 0 --pr-block-file block.md --pr-labels-file labels.txt 2>&1)"
assert_out "TC-C4 §14 dogfood 면제([N/A]) 하에서도 Check 7 독립 fire" "$out" "Check 7 write-back 불일치" ""
assert_out "TC-C4 dogfood §14 면제 확인([N/A] 병존)" "$out" "[N/A]" ""

# TC-C5 (★ SSOT 단일성): gate→lane 매핑이 단일 SSOT 에서만 소비 (병렬 table 부재).
# 0 = 단일 SSOT clean / 1 = 병렬 table·drift 검출.
ssot_single_ok() {
    local script="$1" workflow="$2" ssot="$3" v=0 n
    n="$(grep -cE '^gate:[a-z-]+-pass: ' "$ssot" 2>/dev/null)"; [ "${n:-0}" -eq 3 ] || v=1
    grep -q 'load_gate_lane_map' "$script" 2>/dev/null || v=1
    grep -q 'gate-lane-map-v1.yaml' "$script" 2>/dev/null || v=1
    grep -qE 'GATE_LANE_MAP\["gate:' "$script" 2>/dev/null && v=1   # 하드코딩 병렬 table 금지 (literal gate: key 대입 — SSOT-driven "$key" 와 구별, ASCII locale-safe)
    grep -q 'gate-lane-map-v1.yaml' "$workflow" 2>/dev/null || v=1
    grep -qF "'gate:requirements-review-pass': '[요구사항-리뷰]'" "$workflow" 2>/dev/null && v=1  # 구 하드코딩 literal 금지
    return $v
}
if ssot_single_ok "$SCRIPT_SRC" "$WORKFLOW_SRC" "$SSOT_SRC"; then
    echo "PASS TC-C5 SSOT 단일성 (bash+JS 양측 SSOT 소비, 병렬 table 0)"; PASS=$((PASS+1))
else
    echo "FAIL TC-C5 SSOT 단일성 위반 (병렬 table/drift 검출)"; FAIL=$((FAIL+1))
fi

echo ""
echo "--- CFP-2652 gap (c) mutation ---"

# MUT-C: label-parse no-op (gate label 필터가 아무것도 매칭 안 함) → Check 7 mismatch 미검출 → TC-C1 kill.
#   mutated copy 는 tmp — SSOT 는 CLAUDE_PLUGIN_ROOT 로 real repo 지정. positive control = OUT_C1(원본 #2484 run).
OUT_C1="$(bash "$SCRIPT_SRC" --pr 0 --pr-block-file "$BLOCK_2484" --pr-labels-file "$LABELS_RR" 2>&1)"
M="$C2652_TMP/mut-c.sh"; mutate "grep -E '^gate:.*-pass\$'" "grep -E '^__mut_nomatch__\$'" "$M" || echo "  MUT-C anchor 부재"
if [ -s "$M" ]; then
    MUT_C_OUT="$(CLAUDE_PLUGIN_ROOT="$REPO_ROOT" bash "$M" --pr 0 --pr-block-file "$BLOCK_2484" --pr-labels-file "$LABELS_RR" 2>&1)"
else
    MUT_C_OUT="__MUT_APPLY_FAIL__"
fi
assert_kill2 "MUT-C label-parse no-op kills TC-C1" "$OUT_C1" "$MUT_C_OUT" "Check 7 write-back 불일치"

# MUT-SSOT: (1) bash 에 하드코딩 병렬 GATE_LANE_MAP entry 주입 → TC-C5(ssot_single_ok) 검출.
M="$C2652_TMP/mut-ssot-bash.sh"; mutate 'declare -A GATE_LANE_MAP=()' 'declare -A GATE_LANE_MAP=(); GATE_LANE_MAP["gate:requirements-review-pass"]="요구사항-리뷰"' "$M" || echo "  MUT-SSOT(bash) anchor 부재"
if [ -s "$M" ] && ! ssot_single_ok "$M" "$WORKFLOW_SRC" "$SSOT_SRC"; then
    echo "PASS MUT-SSOT(bash 병렬 table) → TC-C5 검출 (real kill)"; PASS=$((PASS+1))
else
    echo "FAIL MUT-SSOT(bash 병렬 table) 미검출 (mutation 생존 또는 apply 실패)"; FAIL=$((FAIL+1))
fi
# MUT-SSOT: (2) JS workflow 에 구 하드코딩 bracket literal 주입 → TC-C5 검출.
MW="$C2652_TMP/mut-ssot-workflow.yml"
inject_js="const gateLaneMap = {};
                const lanePrefixForGate = { 'gate:requirements-review-pass': '[요구사항-리뷰]' };"
mutate_file "$WORKFLOW_SRC" "const gateLaneMap = {};" "$inject_js" "$MW" || echo "  MUT-SSOT(JS) anchor 부재"
if [ -s "$MW" ] && ! ssot_single_ok "$SCRIPT_SRC" "$MW" "$SSOT_SRC"; then
    echo "PASS MUT-SSOT(JS 하드코딩 literal) → TC-C5 검출 (real kill)"; PASS=$((PASS+1))
else
    echo "FAIL MUT-SSOT(JS 하드코딩 literal) 미검출 (mutation 생존 또는 apply 실패)"; FAIL=$((FAIL+1))
fi

echo ""
echo "=== Summary: PASS=$PASS FAIL=$FAIL ==="
[ "$FAIL" -eq 0 ]
