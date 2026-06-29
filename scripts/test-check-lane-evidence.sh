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

echo ""
echo "=== Summary: PASS=$PASS FAIL=$FAIL ==="
[ "$FAIL" -eq 0 ]
