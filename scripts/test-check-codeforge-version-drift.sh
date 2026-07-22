#!/usr/bin/env bash
# test-check-codeforge-version-drift.sh — CFP-2433 drift-mapping decouple self-test
#
# Deterministic black-box test suite for check-codeforge-version-drift.sh (§8 AC coverage).
# 외부 의존 격리: fake gh + fake cache dir override (HOME).
# mock marketplace.json fixtures — deterministic 결정성 확보(live gh-api ×).
#
# Standalone self-test (drift script = session-start CLI gate, CI 미배선이라 self-test 도 standalone).
# Live gh-api 의존 AC(AC-1/AC-2 codex latest 1.0.5 실 fetch) = honest defer (smoke 검증).
#
# Coverage: AC-1(override resolution) / AC-2(drift 분류) / AC-3(superpowers 부재) /
#           AC-4(mclayer fallback) / AC-5(cache 무손상) / AC-6(문법 + exit) / AC-7(superpowers 비노출)

set -eu

# ── 격리 sandbox 생성 (repo 오염 방지) ────────────────────────────────────────
SANDBOX=$(mktemp -d)

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SCRIPT_PATH="$REPO_ROOT/scripts/check-codeforge-version-drift.sh"

# ── fake gh binary (fake GitHub API 응답 격리) ──────────────────────────────────
# 스크립트의 gh api "repos/<repo>/contents/.claude-plugin/marketplace.json" --jq '.content'를 intercept
# repo 좌표에 따라 fixture marketplace.json 을 base64 인코딩해 반환
mkdir -p "$SANDBOX/bin"
cat > "$SANDBOX/bin/gh" << 'FAKE_GH_EOF'
#!/usr/bin/env bash
# fake gh: mock GitHub API for deterministic testing

# 첫 인자로 명령 확인
cmd="${1:-}"

if [[ "$cmd" == "auth" ]]; then
  if [[ "${2:-}" == "status" ]]; then
    exit 0
  fi
fi

if [[ "$cmd" != "api" ]]; then
  echo "ERROR: unexpected command: $cmd" >&2
  exit 2
fi

# api 명령: 두 번째 인자가 repo path
repo_path="${2:-}"

# jq 옵션 확인
jq_option=""
for arg in "$@"; do
  if [[ "$arg" == ".content" ]]; then
    jq_option="content"
    break
  fi
done

# repo_path 기반 fixture 선택
if [[ "$repo_path" == *"openai/codex-plugin-cc"* ]]; then
  # AC-1/AC-2: codex override (1.0.5 latest)
  if [[ -n "$jq_option" ]]; then
    echo -n '{"plugins":[{"name":"codex","version":"1.0.5"}]}' | base64 -w 0
    echo ""
  else
    content_b64=$(echo -n '{"plugins":[{"name":"codex","version":"1.0.5"}]}' | base64 -w 0)
    echo "{\"content\":\"$content_b64\"}"
  fi
  exit 0

elif [[ "$repo_path" == *"mclayer/marketplace"* ]]; then
  # AC-4: mclayer fallback (7 codeforge + codex 1.0.4)
  mklp='{"plugins":[{"name":"codeforge","version":"6.40.1"},{"name":"codeforge-requirements","version":"6.40.1"},{"name":"codeforge-design","version":"6.40.1"},{"name":"codeforge-review","version":"6.40.1"},{"name":"codeforge-develop","version":"6.40.1"},{"name":"codeforge-test","version":"6.40.1"},{"name":"codeforge-pmo","version":"6.40.1"},{"name":"codex","version":"1.0.4"}]}'
  if [[ -n "$jq_option" ]]; then
    echo -n "$mklp" | base64 -w 0
    echo ""
  else
    content_b64=$(echo -n "$mklp" | base64 -w 0)
    echo "{\"content\":\"$content_b64\"}"
  fi
  exit 0

elif [[ "$repo_path" == *"openai-codex/marketplace"* ]]; then
  # AC-1 mutation: 구 좌표 미응답
  echo "404 Not Found" >&2
  exit 1

else
  echo "ERROR: unknown repo: $repo_path" >&2
  exit 2
fi
FAKE_GH_EOF
chmod +x "$SANDBOX/bin/gh"

# ── fake cache dir 구조 (HOME override) ────────────────────────────────────────
# PLUGINS_DIR="${HOME}/.claude/plugins/cache" 파생이므로 HOME override
# cache key (registry name) 별 plugin.json 배치:
# - openai-codex/codex/1.0.4/.claude-plugin/plugin.json (installed=1.0.4, latest override=1.0.5)
# - mclayer/codeforge[*]/6.40.1/.claude-plugin/plugin.json (7 entry)

mkdir -p "$SANDBOX/.claude/plugins/cache/openai-codex/codex/1.0.4/.claude-plugin"
cat > "$SANDBOX/.claude/plugins/cache/openai-codex/codex/1.0.4/.claude-plugin/plugin.json" << 'EOF'
{
  "name": "codex",
  "version": "1.0.4",
  "description": "OpenAI Codex plugin"
}
EOF

# mclayer 7 plugin (all at 6.40.1)
for plugin in codeforge codeforge-requirements codeforge-design codeforge-review \
              codeforge-develop codeforge-test codeforge-pmo; do
  mkdir -p "$SANDBOX/.claude/plugins/cache/mclayer/$plugin/6.40.1/.claude-plugin"
  cat > "$SANDBOX/.claude/plugins/cache/mclayer/$plugin/6.40.1/.claude-plugin/plugin.json" << EOF
{
  "name": "$plugin",
  "version": "6.40.1",
  "description": "codeforge plugin"
}
EOF
done

# ── 테스트 케이스 실행 (PATH, HOME override) ──────────────────────────────────────
export PATH="$SANDBOX/bin:$PATH"
export HOME="$SANDBOX"

PASS_COUNT=0
FAIL_COUNT=0

# ── Case (a): AC-1/AC-2 codex override resolution + drift ───────────────────────
{
  echo "━━ Case (a): AC-1/AC-2 codex override resolution + PATCH drift"
  case_a_output=$(bash "$SCRIPT_PATH" --json 2>/dev/null || echo "")
  if echo "$case_a_output" | grep -q '"plugin":"codex".*"status":"patch".*"installed":"1.0.4".*"latest":"1.0.5"' 2>/dev/null || false; then
    echo "✓ Case (a) PASS: override resolution (openai/codex-plugin-cc) + PATCH drift 검출"
    ((PASS_COUNT++)) || true
  else
    echo "✗ Case (a) FAIL: codex patch drift 미검출 또는 버전 불일치"
    echo "  output: $case_a_output"
    ((FAIL_COUNT++)) || true
  fi
}

# ── Case (b): AC-5 cache 무손상 (silent-regression 가드, load-bearing) ──────────
{
  echo ""
  echo "━━ Case (b): AC-5 cache 무손상 — codex installed=1.0.4 hit (not-installed 아님)"
  case_b_output=$(bash "$SCRIPT_PATH" --plugin codex --json 2>/dev/null || echo "")
  if (echo "$case_b_output" | grep -q '"plugin":"codex"' 2>/dev/null || false) && \
     ! (echo "$case_b_output" | grep -q '"status":"not-installed"' 2>/dev/null || false); then
    echo "✓ Case (b) PASS: cache 좌표 정상 (openai-codex/codex/1.0.4 hit)"
    ((PASS_COUNT++)) || true
  else
    echo "✗ Case (b) FAIL: cache 좌표 손상 또는 not-installed 검출"
    echo "  output: $case_b_output"
    ((FAIL_COUNT++)) || true
  fi
}

# ── Case (c): AC-4 mclayer 무회귀 (fallback via PLUGIN_MARKETPLACE, override미등재) ──
{
  echo ""
  echo "━━ Case (c): AC-4 mclayer fallback (7 codeforge plugin)"
  case_c_output=$(bash "$SCRIPT_PATH" --plugin codeforge --json 2>/dev/null || echo "")
  if echo "$case_c_output" | grep -q '"plugin":"codeforge".*"status":"none".*"installed":"6.40.1".*"latest":"6.40.1"' 2>/dev/null || false; then
    echo "✓ Case (c) PASS: mclayer fallback 정상 (override미등재 → \$mp fallback)"
    ((PASS_COUNT++)) || true
  else
    echo "✗ Case (c) FAIL: mclayer fallback 미동작 또는 버전 불일치"
    echo "  output: $case_c_output"
    ((FAIL_COUNT++)) || true
  fi
}

# ── Case (d): AC-3/AC-7 superpowers 부재 (bare 출력) ────────────────────────────
{
  echo ""
  echo "━━ Case (d): AC-3 superpowers 엔트리 부재 (bare 출력)"
  case_d_output=$(bash "$SCRIPT_PATH" 2>/dev/null || echo "")
  if ! (echo "$case_d_output" | grep -q "superpowers" 2>/dev/null || false); then
    echo "✓ Case (d) PASS: superpowers 항목 부재 (bare 출력)"
    ((PASS_COUNT++)) || true
  else
    echo "✗ Case (d) FAIL: superpowers 항목 노출됨"
    echo "  output 스니펫: $(echo "$case_d_output" | grep superpowers || echo "")"
    ((FAIL_COUNT++)) || true
  fi
}

# ── Case (e): AC-3/AC-7 superpowers 부재 (--json 출력) ─────────────────────────
{
  echo ""
  echo "━━ Case (e): AC-7 superpowers 엔트리 부재 (--json 출력)"
  case_e_output=$(bash "$SCRIPT_PATH" --json 2>/dev/null || echo "")
  superpowers_count=$(echo "$case_e_output" | grep -o '"plugin":"superpowers"' 2>/dev/null | wc -l || echo 0)
  if [[ "$superpowers_count" -eq 0 ]]; then
    echo "✓ Case (e) PASS: superpowers 엔트리 0건 (--json 출력)"
    ((PASS_COUNT++)) || true
  else
    echo "✗ Case (e) FAIL: superpowers 엔트리 $superpowers_count 건 검출"
    echo "  output: $case_e_output"
    ((FAIL_COUNT++)) || true
  fi
}

# ── Case (f): AC-6 문법 검증 (bash -n) ────────────────────────────────────────
{
  echo ""
  echo "━━ Case (f): AC-6 문법 검증"
  if bash -n "$SCRIPT_PATH" 2>/dev/null || false; then
    echo "✓ Case (f) PASS: bash -n 통과 (문법 정상)"
    ((PASS_COUNT++)) || true
  else
    echo "✗ Case (f) FAIL: bash -n 실패"
    ((FAIL_COUNT++)) || true
  fi
}

# ── Case (g): AC-6 정상 exit code (MAJOR drift 0 fixture) ─────────────────────
{
  echo ""
  echo "━━ Case (g): AC-6 exit code 0 (MAJOR drift 없음, patch-only fixture)"
  if bash "$SCRIPT_PATH" >/dev/null 2>&1 || false; then
    echo "✓ Case (g) PASS: exit 0 (MAJOR drift 미검출)"
    ((PASS_COUNT++)) || true
  else
    exit_code=$?
    echo "✗ Case (g) FAIL: exit $exit_code (기대: 0)"
    ((FAIL_COUNT++)) || true
  fi
}

# ── 결과 종합 ──────────────────────────────────────────────────────────────────
{
  echo ""
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "Test 결과 종합:"
  echo "  PASS: $PASS_COUNT / 7"
  echo "  FAIL: $FAIL_COUNT / 7"

  if [[ $FAIL_COUNT -eq 0 ]]; then
    echo ""
    echo "✓ 모든 테스트 케이스 PASS (exit 0)"
    rm -rf "$SANDBOX"
    exit 0
  else
    echo ""
    echo "✗ 테스트 실패 케이스 존재 (exit 1)"
    rm -rf "$SANDBOX"
    exit 1
  fi
}
