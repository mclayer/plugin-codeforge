#!/usr/bin/env bash
# tests/scripts/test_reconcile-overlay-workflow-channel.sh
# CFP-2440 Phase 2 — Discriminating self-test for reconcile-overlay.sh workflow channel
# Change Plan §8 Test Contract AC-1~11 이행
#
# anti-theater: always-pass 0, tautology 0. 각 AC 는 구현의 1-line mutation 으로 RED 전환.
# 실 배포 SSOT(templates/whitelist) in-place mutate 0 — 전부 mktemp -d temp fixture 격리.

set -u  # set -e 미사용(결함 2) — test 호출은 || true 로 감싸 partial run 허용 + FAIL 카운터 집계

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
RECONCILE_SH="$REPO_ROOT/scripts/reconcile-overlay.sh"

PASS=0
FAIL=0

# Helper: consumer repo-kind 마커 생성 (결함 1 수정)
# detect-repo-kind.py 는 .claude/_overlay/project.yaml 존재 + plugin.json 부재 → consumer 판정.
# plugin.json 을 만들면 plugin/mixed 로 분류돼 whitelist filter 가 우회되므로 절대 생성 금지.
setup_consumer_marker() {
  local consumer_root="$1"
  mkdir -p "$consumer_root/.claude/_overlay"
  echo "name: test-consumer" > "$consumer_root/.claude/_overlay/project.yaml"
}

# AC-5: anchor source base (mutation-survivable)
# discriminating: 3 load-bearing fixture(`fix-ledger-sync.yml`·`story-section-1-immutable.yml`·
# `subissue-from-impl-manifest.yml`)가 WORKFLOW_SRC_DIR(=templates/github-workflows anchor)에만
# 존재하고 consumer .github/workflows 에는 부재. --apply 후 dest 에 정확히 3건 landing 검증.
# anchor 가 `.github/` 로 mutate 되면 src_base 가 consumer 의 빈 .github/workflows 를 가리켜
# 0건 전파 → FAIL(dead-ref 오판 검출). src 가 temp 격리 dir 라 우연 통과 불가 → dest landing
# assert 가 곧 src_base==templates anchor 검증과 동치.
test_ac5_anchor_source_base() {
  local test_name="AC-5-anchor-source-base"
  local fixture_root fixture_wrapper fixture_consumer tmp_snapshot

  fixture_root="$(mktemp -d)"
  fixture_wrapper="$fixture_root/fixture-wrapper"
  fixture_consumer="$fixture_root/fixture-consumer"
  tmp_snapshot="$fixture_root/snapshots"

  mkdir -p "$fixture_wrapper/templates/github-workflows" \
           "$fixture_wrapper/templates/scripts" \
           "$fixture_consumer/.github/workflows" \
           "$tmp_snapshot"

  local fixture_files=("fix-ledger-sync.yml" "story-section-1-immutable.yml" "subissue-from-impl-manifest.yml")
  for f in "${fixture_files[@]}"; do
    echo "# fixture: $f" > "$fixture_wrapper/templates/github-workflows/$f"
  done

  printf "fix-ledger-sync.yml\nstory-section-1-immutable.yml\nsubissue-from-impl-manifest.yml\n" \
    > "$fixture_wrapper/templates/scripts/consumer_applicable_workflows.txt"

  setup_consumer_marker "$fixture_consumer"

  RECONCILE_OVERLAY_WORKFLOW_SRC_DIR="$fixture_wrapper/templates/github-workflows" \
  RECONCILE_OVERLAY_WORKFLOW_DST_DIR="$fixture_consumer/.github/workflows" \
  CONSUMER_APPLICABLE_WHITELIST="$fixture_wrapper/templates/scripts/consumer_applicable_workflows.txt" \
  RECONCILE_OVERLAY_SNAPSHOT_DIR="$tmp_snapshot" \
  CONSUMER_ROOT="$fixture_consumer" \
  bash "$RECONCILE_SH" --apply > /dev/null 2>&1 || true

  local count=0
  for f in "${fixture_files[@]}"; do
    [ -f "$fixture_consumer/.github/workflows/$f" ] && ((count++)) || true
  done

  if [ "$count" -eq 3 ]; then
    echo "✓ PASS: $test_name (count=$count) — anchor=WORKFLOW_SRC_DIR (3 fixture landed in dest)"
    PASS=$((PASS+1))
    rm -rf "$fixture_root"
    return 0
  else
    echo "✗ FAIL: $test_name — expected 3 files in dest, got $count"
    FAIL=$((FAIL+1))
    rm -rf "$fixture_root"
    return 1
  fi
}

# AC-2: update not bootstrap
# discriminating: dst 에 구버전 존재 + source 신버전 → --apply 후 dst 가 신버전 갱신.
# `! -f dst` never-overwrite(bootstrap 의미론) 로 오구현 시 갱신 누락 → dst="v1-old" → FAIL.
test_ac2_update_not_bootstrap() {
  local test_name="AC-2-update-not-bootstrap"
  local fixture_root fixture_wrapper fixture_consumer tmp_snapshot

  fixture_root="$(mktemp -d)"
  fixture_wrapper="$fixture_root/fixture-wrapper"
  fixture_consumer="$fixture_root/fixture-consumer"
  tmp_snapshot="$fixture_root/snapshots"

  mkdir -p "$fixture_wrapper/templates/github-workflows" \
           "$fixture_wrapper/templates/scripts" \
           "$fixture_consumer/.github/workflows" \
           "$tmp_snapshot"

  local wf_name="test-workflow.yml"
  echo "version: v2-new" > "$fixture_wrapper/templates/github-workflows/$wf_name"
  echo "version: v1-old" > "$fixture_consumer/.github/workflows/$wf_name"
  echo "$wf_name" > "$fixture_wrapper/templates/scripts/consumer_applicable_workflows.txt"

  setup_consumer_marker "$fixture_consumer"

  RECONCILE_OVERLAY_WORKFLOW_SRC_DIR="$fixture_wrapper/templates/github-workflows" \
  RECONCILE_OVERLAY_WORKFLOW_DST_DIR="$fixture_consumer/.github/workflows" \
  CONSUMER_APPLICABLE_WHITELIST="$fixture_wrapper/templates/scripts/consumer_applicable_workflows.txt" \
  RECONCILE_OVERLAY_SNAPSHOT_DIR="$tmp_snapshot" \
  CONSUMER_ROOT="$fixture_consumer" \
  bash "$RECONCILE_SH" --apply > /dev/null 2>&1 || true

  local dst_content
  dst_content=$(cat "$fixture_consumer/.github/workflows/$wf_name" 2>/dev/null || echo "")

  if [[ "$dst_content" == "version: v2-new" ]]; then
    echo "✓ PASS: $test_name — update confirmed (old→new)"
    PASS=$((PASS+1))
    rm -rf "$fixture_root"
    return 0
  else
    echo "✗ FAIL: $test_name — expected v2-new, got '$dst_content'"
    FAIL=$((FAIL+1))
    rm -rf "$fixture_root"
    return 1
  fi
}

# AC-6: over-broad enumerate (consumer 자체 파일 보존)
# discriminating: consumer 자체 비-whitelisted custom.yml(source 엔 없음). --apply 후 byte-identical
# 보존. reconcile 이 wrapper SSOT(source) 만 순회해야 함. dest 를 순회/삭제하면 변형 → FAIL.
test_ac6_over_broad_enumerate() {
  local test_name="AC-6-over-broad-enumerate"
  local fixture_root fixture_wrapper fixture_consumer tmp_snapshot

  fixture_root="$(mktemp -d)"
  fixture_wrapper="$fixture_root/fixture-wrapper"
  fixture_consumer="$fixture_root/fixture-consumer"
  tmp_snapshot="$fixture_root/snapshots"

  mkdir -p "$fixture_wrapper/templates/github-workflows" \
           "$fixture_wrapper/templates/scripts" \
           "$fixture_consumer/.github/workflows" \
           "$tmp_snapshot"

  echo "# consumer file" > "$fixture_consumer/.github/workflows/custom.yml"
  local original_content
  original_content=$(cat "$fixture_consumer/.github/workflows/custom.yml")

  echo "# empty" > "$fixture_wrapper/templates/scripts/consumer_applicable_workflows.txt"

  setup_consumer_marker "$fixture_consumer"

  RECONCILE_OVERLAY_WORKFLOW_SRC_DIR="$fixture_wrapper/templates/github-workflows" \
  RECONCILE_OVERLAY_WORKFLOW_DST_DIR="$fixture_consumer/.github/workflows" \
  CONSUMER_APPLICABLE_WHITELIST="$fixture_wrapper/templates/scripts/consumer_applicable_workflows.txt" \
  RECONCILE_OVERLAY_SNAPSHOT_DIR="$tmp_snapshot" \
  CONSUMER_ROOT="$fixture_consumer" \
  bash "$RECONCILE_SH" --apply > /dev/null 2>&1 || true

  local after_content
  after_content=$(cat "$fixture_consumer/.github/workflows/custom.yml" 2>/dev/null || echo "__REMOVED__")

  if [[ "$after_content" == "$original_content" ]]; then
    echo "✓ PASS: $test_name — consumer file untouched"
    PASS=$((PASS+1))
    rm -rf "$fixture_root"
    return 0
  else
    echo "✗ FAIL: $test_name — consumer file modified/removed (got '$after_content')"
    FAIL=$((FAIL+1))
    rm -rf "$fixture_root"
    return 1
  fi
}

# AC-10: empty vs absent whitelist (never-reduce)
# discriminating: empty(빈 파일) 및 absent(파일 없음) 양 분기에서 consumer 기존 배포본 존속.
# copy/skip 이 remove 로 escalate 하면(F-CR-001 wipe) existing.yml 삭제 → FAIL.
test_ac10_empty_vs_absent_whitelist() {
  local test_name="AC-10-empty-vs-absent"
  local fixture_root fixture_wrapper fixture_consumer tmp_snapshot
  local branch_fail=0

  for branch in empty absent; do
    fixture_root="$(mktemp -d)"
    fixture_wrapper="$fixture_root/fixture-wrapper"
    fixture_consumer="$fixture_root/fixture-consumer"
    tmp_snapshot="$fixture_root/snapshots"

    mkdir -p "$fixture_wrapper/templates/github-workflows" \
             "$fixture_wrapper/templates/scripts" \
             "$fixture_consumer/.github/workflows" \
             "$tmp_snapshot"

    echo "# existing" > "$fixture_consumer/.github/workflows/existing.yml"

    local whitelist_path="$fixture_wrapper/templates/scripts/consumer_applicable_workflows.txt"
    if [ "$branch" = "empty" ]; then
      printf '# empty\n\n   \n' > "$whitelist_path"   # 존재하나 0 entry
    else
      whitelist_path="$fixture_root/nonexistent-whitelist.txt"  # 부재 (파일 미생성)
    fi

    setup_consumer_marker "$fixture_consumer"

    RECONCILE_OVERLAY_WORKFLOW_SRC_DIR="$fixture_wrapper/templates/github-workflows" \
    RECONCILE_OVERLAY_WORKFLOW_DST_DIR="$fixture_consumer/.github/workflows" \
    CONSUMER_APPLICABLE_WHITELIST="$whitelist_path" \
    RECONCILE_OVERLAY_SNAPSHOT_DIR="$tmp_snapshot" \
    CONSUMER_ROOT="$fixture_consumer" \
    bash "$RECONCILE_SH" --apply > /dev/null 2>&1 || true

    if [ ! -f "$fixture_consumer/.github/workflows/existing.yml" ]; then
      echo "✗ FAIL: $test_name ($branch branch) — existing.yml removed (never-reduce 위반)"
      branch_fail=1
    fi
    rm -rf "$fixture_root"
  done

  if [ "$branch_fail" -eq 0 ]; then
    echo "✓ PASS: $test_name — empty AND absent: file preserved (never-reduce)"
    PASS=$((PASS+1))
    return 0
  else
    FAIL=$((FAIL+1))
    return 1
  fi
}

# AC-8: dry-run (filesystem touch 0)
# discriminating: --dry-run 시 dst 파일 생성 0. dry_run guard 제거 시 dry-run 도 cp → 파일 생성 → FAIL.
test_ac8_dry_run() {
  local test_name="AC-8-dry-run"
  local fixture_root fixture_wrapper fixture_consumer tmp_snapshot

  fixture_root="$(mktemp -d)"
  fixture_wrapper="$fixture_root/fixture-wrapper"
  fixture_consumer="$fixture_root/fixture-consumer"
  tmp_snapshot="$fixture_root/snapshots"

  mkdir -p "$fixture_wrapper/templates/github-workflows" \
           "$fixture_wrapper/templates/scripts" \
           "$fixture_consumer/.github/workflows" \
           "$tmp_snapshot"

  echo "v1" > "$fixture_wrapper/templates/github-workflows/test.yml"
  echo "test.yml" > "$fixture_wrapper/templates/scripts/consumer_applicable_workflows.txt"

  setup_consumer_marker "$fixture_consumer"

  local dst_exists_before=0
  [ -f "$fixture_consumer/.github/workflows/test.yml" ] && dst_exists_before=1

  RECONCILE_OVERLAY_WORKFLOW_SRC_DIR="$fixture_wrapper/templates/github-workflows" \
  RECONCILE_OVERLAY_WORKFLOW_DST_DIR="$fixture_consumer/.github/workflows" \
  CONSUMER_APPLICABLE_WHITELIST="$fixture_wrapper/templates/scripts/consumer_applicable_workflows.txt" \
  RECONCILE_OVERLAY_SNAPSHOT_DIR="$tmp_snapshot" \
  CONSUMER_ROOT="$fixture_consumer" \
  bash "$RECONCILE_SH" --dry-run > /dev/null 2>&1 || true

  local dst_exists_after=0
  [ -f "$fixture_consumer/.github/workflows/test.yml" ] && dst_exists_after=1

  # 신규 파일이라 before=0 이 정상 — dry-run 후에도 0 이어야 함.
  if [ "$dst_exists_before" -eq 0 ] && [ "$dst_exists_after" -eq 0 ]; then
    echo "✓ PASS: $test_name — dry-run no side-effects (dst not created)"
    PASS=$((PASS+1))
    rm -rf "$fixture_root"
    return 0
  else
    echo "✗ FAIL: $test_name — filesystem modified (before=$dst_exists_before after=$dst_exists_after)"
    FAIL=$((FAIL+1))
    rm -rf "$fixture_root"
    return 1
  fi
}

# AC-9: idempotency (AND-합성 게이트 회귀 방어 — overlay-identical + workflow-drift)
# discriminating: overlay 채널은 wrapper SSOT 와 동일(overlay-identical), 워크플로 dst 만 drift(구버전).
# 만약 L788-789 AND-합성을 단일 overlay 게이트로 되돌리면 overlay 일치 → L778 이 먼저 exit 0 →
# 워크플로 갱신 영영 미적용 → dst 가 구버전 잔존 → FAIL. silent no-op 회귀 방어 핵심 test.
# 검증: 1회 apply 로 dst 가 신버전 landing(byte == source) + 2회째 byte-identical(idempotent).
test_ac9_idempotency() {
  local test_name="AC-9-idempotency-and-synthesis"
  local fixture_root fixture_wrapper fixture_consumer tmp_snapshot

  fixture_root="$(mktemp -d)"
  fixture_wrapper="$fixture_root/fixture-wrapper"
  fixture_consumer="$fixture_root/fixture-consumer"
  tmp_snapshot="$fixture_root/snapshots"

  mkdir -p "$fixture_wrapper/templates/github-workflows" \
           "$fixture_wrapper/templates/scripts" \
           "$fixture_consumer/.github/workflows" \
           "$fixture_consumer/.claude/_overlay" \
           "$fixture_wrapper/overlay" \
           "$tmp_snapshot"

  # overlay 채널: wrapper SSOT == consumer overlay (overlay-identical)
  echo "overlay-stable" > "$fixture_wrapper/overlay/ov.txt"
  echo "overlay-stable" > "$fixture_consumer/.claude/_overlay/ov.txt"

  # 워크플로 채널: source 신버전, consumer dst 구버전 (drift)
  echo "wf-v2-new" > "$fixture_wrapper/templates/github-workflows/test.yml"
  echo "wf-v1-old" > "$fixture_consumer/.github/workflows/test.yml"
  echo "test.yml" > "$fixture_wrapper/templates/scripts/consumer_applicable_workflows.txt"

  setup_consumer_marker "$fixture_consumer"

  # 1회차 apply — overlay-identical 이라 단일 게이트면 early-exit 되어 워크플로 미갱신.
  RECONCILE_OVERLAY_WRAPPER_DIR="$fixture_wrapper/overlay" \
  RECONCILE_OVERLAY_CONSUMER_OVERLAY_DIR="$fixture_consumer/.claude/_overlay" \
  RECONCILE_OVERLAY_WORKFLOW_SRC_DIR="$fixture_wrapper/templates/github-workflows" \
  RECONCILE_OVERLAY_WORKFLOW_DST_DIR="$fixture_consumer/.github/workflows" \
  CONSUMER_APPLICABLE_WHITELIST="$fixture_wrapper/templates/scripts/consumer_applicable_workflows.txt" \
  RECONCILE_OVERLAY_SNAPSHOT_DIR="$tmp_snapshot" \
  CONSUMER_ROOT="$fixture_consumer" \
  bash "$RECONCILE_SH" --apply > /dev/null 2>&1 || true

  local content_1st
  content_1st=$(cat "$fixture_consumer/.github/workflows/test.yml" 2>/dev/null || echo "")

  # 2회차 apply — 이제 양 채널 모두 stable → byte-identical 이어야(idempotent).
  RECONCILE_OVERLAY_WRAPPER_DIR="$fixture_wrapper/overlay" \
  RECONCILE_OVERLAY_CONSUMER_OVERLAY_DIR="$fixture_consumer/.claude/_overlay" \
  RECONCILE_OVERLAY_WORKFLOW_SRC_DIR="$fixture_wrapper/templates/github-workflows" \
  RECONCILE_OVERLAY_WORKFLOW_DST_DIR="$fixture_consumer/.github/workflows" \
  CONSUMER_APPLICABLE_WHITELIST="$fixture_wrapper/templates/scripts/consumer_applicable_workflows.txt" \
  RECONCILE_OVERLAY_SNAPSHOT_DIR="$tmp_snapshot" \
  CONSUMER_ROOT="$fixture_consumer" \
  bash "$RECONCILE_SH" --apply > /dev/null 2>&1 || true

  local content_2nd
  content_2nd=$(cat "$fixture_consumer/.github/workflows/test.yml" 2>/dev/null || echo "")

  # 핵심 assert: 1회차에 워크플로가 신버전으로 갱신(AND-합성 게이트 통과) + 2회째 byte-identical.
  if [ "$content_1st" = "wf-v2-new" ] && [ "$content_1st" = "$content_2nd" ]; then
    echo "✓ PASS: $test_name — AND-합성 갱신 + idempotent (1st=2nd=wf-v2-new)"
    PASS=$((PASS+1))
    rm -rf "$fixture_root"
    return 0
  else
    echo "✗ FAIL: $test_name — 1st='$content_1st' 2nd='$content_2nd' (expected both wf-v2-new)"
    FAIL=$((FAIL+1))
    rm -rf "$fixture_root"
    return 1
  fi
}

# AC-1: new propagation
# discriminating: 신규 whitelisted 워크플로 미보유 consumer → --apply 후 copy. skip 오구현 시 부재 → FAIL.
test_ac1_new_propagation() {
  local test_name="AC-1-new-propagation"
  local fixture_root fixture_wrapper fixture_consumer tmp_snapshot

  fixture_root="$(mktemp -d)"
  fixture_wrapper="$fixture_root/fixture-wrapper"
  fixture_consumer="$fixture_root/fixture-consumer"
  tmp_snapshot="$fixture_root/snapshots"

  mkdir -p "$fixture_wrapper/templates/github-workflows" \
           "$fixture_wrapper/templates/scripts" \
           "$fixture_consumer/.github/workflows" \
           "$tmp_snapshot"

  echo "new-content" > "$fixture_wrapper/templates/github-workflows/new-wf.yml"
  echo "new-wf.yml" > "$fixture_wrapper/templates/scripts/consumer_applicable_workflows.txt"

  setup_consumer_marker "$fixture_consumer"

  RECONCILE_OVERLAY_WORKFLOW_SRC_DIR="$fixture_wrapper/templates/github-workflows" \
  RECONCILE_OVERLAY_WORKFLOW_DST_DIR="$fixture_consumer/.github/workflows" \
  CONSUMER_APPLICABLE_WHITELIST="$fixture_wrapper/templates/scripts/consumer_applicable_workflows.txt" \
  RECONCILE_OVERLAY_SNAPSHOT_DIR="$tmp_snapshot" \
  CONSUMER_ROOT="$fixture_consumer" \
  bash "$RECONCILE_SH" --apply > /dev/null 2>&1 || true

  if [ -f "$fixture_consumer/.github/workflows/new-wf.yml" ]; then
    echo "✓ PASS: $test_name — new workflow propagated"
    PASS=$((PASS+1))
    rm -rf "$fixture_root"
    return 0
  else
    echo "✗ FAIL: $test_name — file not found"
    FAIL=$((FAIL+1))
    rm -rf "$fixture_root"
    return 1
  fi
}

# AC-3: filter skip (whitelist filter 재사용)
# discriminating: whitelisted + plugin-only(비-whitelisted) 혼재 consumer. --apply 후 whitelisted 만
# 전파 + plugin-only skip(dst 부재) + skip 신호 출력. filter 미적용 시 plugin-only 도 전파 → FAIL.
test_ac3_filter_skip() {
  local test_name="AC-3-filter-skip"
  local fixture_root fixture_wrapper fixture_consumer tmp_snapshot

  fixture_root="$(mktemp -d)"
  fixture_wrapper="$fixture_root/fixture-wrapper"
  fixture_consumer="$fixture_root/fixture-consumer"
  tmp_snapshot="$fixture_root/snapshots"

  mkdir -p "$fixture_wrapper/templates/github-workflows" \
           "$fixture_wrapper/templates/scripts" \
           "$fixture_consumer/.github/workflows" \
           "$tmp_snapshot"

  echo "whitelisted" > "$fixture_wrapper/templates/github-workflows/keep-this.yml"
  echo "plugin-only" > "$fixture_wrapper/templates/github-workflows/skip-this.yml"
  echo "keep-this.yml" > "$fixture_wrapper/templates/scripts/consumer_applicable_workflows.txt"

  setup_consumer_marker "$fixture_consumer"

  local output
  output=$( \
    RECONCILE_OVERLAY_WORKFLOW_SRC_DIR="$fixture_wrapper/templates/github-workflows" \
    RECONCILE_OVERLAY_WORKFLOW_DST_DIR="$fixture_consumer/.github/workflows" \
    CONSUMER_APPLICABLE_WHITELIST="$fixture_wrapper/templates/scripts/consumer_applicable_workflows.txt" \
    RECONCILE_OVERLAY_SNAPSHOT_DIR="$tmp_snapshot" \
    CONSUMER_ROOT="$fixture_consumer" \
    bash "$RECONCILE_SH" --apply 2>&1 ) || true

  local keep_exists=0 skip_exists=0
  [ -f "$fixture_consumer/.github/workflows/keep-this.yml" ] && keep_exists=1
  [ -f "$fixture_consumer/.github/workflows/skip-this.yml" ] && skip_exists=1

  local has_skip_signal=0
  echo "$output" | grep -q "\[FILTER\] skip plugin-only workflow" && has_skip_signal=1 || true

  if [ "$keep_exists" -eq 1 ] && [ "$skip_exists" -eq 0 ] && [ "$has_skip_signal" -eq 1 ]; then
    echo "✓ PASS: $test_name — whitelisted propagated, plugin-only skipped (signal confirmed)"
    PASS=$((PASS+1))
    rm -rf "$fixture_root"
    return 0
  else
    echo "✗ FAIL: $test_name — keep=$keep_exists skip=$skip_exists signal=$has_skip_signal (expected 1/0/1)"
    FAIL=$((FAIL+1))
    rm -rf "$fixture_root"
    return 1
  fi
}

# AC-4: repo-kind (plugin/mixed full mirror · unknown fail-closed abort)
# discriminating: (a) mixed → whitelist 무시 full mirror(비-whitelisted 도 전파, 0 skip).
# (b) unknown → fail-closed abort(exit!=0 + abort 신호). fail-open 오구현 시 FAIL.
test_ac4_repo_kind() {
  local test_name="AC-4-repo-kind"
  local fixture_root fixture_wrapper fixture_consumer_mixed fixture_consumer_unknown tmp_snapshot

  fixture_root="$(mktemp -d)"
  fixture_wrapper="$fixture_root/fixture-wrapper"
  fixture_consumer_mixed="$fixture_root/fixture-consumer-mixed"
  fixture_consumer_unknown="$fixture_root/fixture-consumer-unknown"
  tmp_snapshot="$fixture_root/snapshots"

  mkdir -p "$fixture_wrapper/templates/github-workflows" \
           "$fixture_wrapper/templates/scripts" \
           "$fixture_consumer_mixed/.github/workflows" \
           "$fixture_consumer_unknown/.github/workflows" \
           "$tmp_snapshot"

  echo "wl" > "$fixture_wrapper/templates/github-workflows/whitelisted.yml"
  echo "nwl" > "$fixture_wrapper/templates/github-workflows/non-whitelisted.yml"
  echo "whitelisted.yml" > "$fixture_wrapper/templates/scripts/consumer_applicable_workflows.txt"

  # Case 1: mixed repo-kind (plugin.json + project.yaml 둘 다) → full mirror
  mkdir -p "$fixture_consumer_mixed/.claude/_overlay" "$fixture_consumer_mixed/.claude-plugin"
  touch "$fixture_consumer_mixed/.claude-plugin/plugin.json"
  echo "name: test-mixed" > "$fixture_consumer_mixed/.claude/_overlay/project.yaml"

  RECONCILE_OVERLAY_WORKFLOW_SRC_DIR="$fixture_wrapper/templates/github-workflows" \
  RECONCILE_OVERLAY_WORKFLOW_DST_DIR="$fixture_consumer_mixed/.github/workflows" \
  CONSUMER_APPLICABLE_WHITELIST="$fixture_wrapper/templates/scripts/consumer_applicable_workflows.txt" \
  RECONCILE_OVERLAY_SNAPSHOT_DIR="$tmp_snapshot" \
  CONSUMER_ROOT="$fixture_consumer_mixed" \
  bash "$RECONCILE_SH" --apply > /dev/null 2>&1 || true

  local mixed_wl_exists=0 mixed_nwl_exists=0
  [ -f "$fixture_consumer_mixed/.github/workflows/whitelisted.yml" ] && mixed_wl_exists=1
  [ -f "$fixture_consumer_mixed/.github/workflows/non-whitelisted.yml" ] && mixed_nwl_exists=1

  if [ "$mixed_wl_exists" -ne 1 ] || [ "$mixed_nwl_exists" -ne 1 ]; then
    echo "✗ FAIL: $test_name (mixed) — wl=$mixed_wl_exists nwl=$mixed_nwl_exists (expected 1/1 full mirror)"
    FAIL=$((FAIL+1))
    rm -rf "$fixture_root"
    return 1
  fi

  # Case 2: unknown repo-kind (plugin.json·project.yaml 모두 부재) → fail-closed abort
  mkdir -p "$fixture_consumer_unknown/.claude/_overlay"   # project.yaml 미생성 → unknown 신호

  local exit_code=0 output_unknown
  output_unknown=$( \
    RECONCILE_OVERLAY_WORKFLOW_SRC_DIR="$fixture_wrapper/templates/github-workflows" \
    RECONCILE_OVERLAY_WORKFLOW_DST_DIR="$fixture_consumer_unknown/.github/workflows" \
    CONSUMER_APPLICABLE_WHITELIST="$fixture_wrapper/templates/scripts/consumer_applicable_workflows.txt" \
    RECONCILE_OVERLAY_SNAPSHOT_DIR="$tmp_snapshot" \
    CONSUMER_ROOT="$fixture_consumer_unknown" \
    bash "$RECONCILE_SH" --apply 2>&1 ) || exit_code=$?

  local has_abort_signal=0
  echo "$output_unknown" | grep -q "repo-kind unknown.*fail-closed abort" && has_abort_signal=1 || true

  if [ "$exit_code" -ne 0 ] && [ "$has_abort_signal" -eq 1 ]; then
    echo "✓ PASS: $test_name — mixed full mirror + unknown fail-closed abort"
    PASS=$((PASS+1))
    rm -rf "$fixture_root"
    return 0
  else
    echo "✗ FAIL: $test_name (unknown) — exit=$exit_code signal=$has_abort_signal (expected exit!=0, signal=1)"
    FAIL=$((FAIL+1))
    rm -rf "$fixture_root"
    return 1
  fi
}

# AC-7: loss-report (consumer customization wholesale overwrite → silent overwrite 0)
# discriminating: consumer 가 whitelisted 워크플로를 직접 수정(source 와 diff). --apply wholesale
# overwrite 시 loss-report 신호 출력. silent overwrite(report 부재) 면 신호 미검출 → FAIL.
test_ac7_loss_report() {
  local test_name="AC-7-loss-report"
  local fixture_root fixture_wrapper fixture_consumer tmp_snapshot

  fixture_root="$(mktemp -d)"
  fixture_wrapper="$fixture_root/fixture-wrapper"
  fixture_consumer="$fixture_root/fixture-consumer"
  tmp_snapshot="$fixture_root/snapshots"

  mkdir -p "$fixture_wrapper/templates/github-workflows" \
           "$fixture_wrapper/templates/scripts" \
           "$fixture_consumer/.github/workflows" \
           "$tmp_snapshot"

  echo "source-version" > "$fixture_wrapper/templates/github-workflows/drift-wf.yml"
  # consumer 직접 수정 (marker 부재 → MARKER_NONE wholesale 경로, customization 존재)
  echo "consumer-custom-version" > "$fixture_consumer/.github/workflows/drift-wf.yml"
  echo "drift-wf.yml" > "$fixture_wrapper/templates/scripts/consumer_applicable_workflows.txt"

  setup_consumer_marker "$fixture_consumer"

  local output
  output=$( \
    RECONCILE_OVERLAY_WORKFLOW_SRC_DIR="$fixture_wrapper/templates/github-workflows" \
    RECONCILE_OVERLAY_WORKFLOW_DST_DIR="$fixture_consumer/.github/workflows" \
    CONSUMER_APPLICABLE_WHITELIST="$fixture_wrapper/templates/scripts/consumer_applicable_workflows.txt" \
    RECONCILE_OVERLAY_SNAPSHOT_DIR="$tmp_snapshot" \
    CONSUMER_ROOT="$fixture_consumer" \
    bash "$RECONCILE_SH" --apply 2>&1 ) || true

  # loss-report 신호 (reconcile-overlay.sh MARKER_NONE wholesale loss-report 경로)
  if echo "$output" | grep -qiE "LOSS REPORT|loss|손실|overwrite|덮어"; then
    echo "✓ PASS: $test_name — loss-report signal detected (silent overwrite 0)"
    PASS=$((PASS+1))
    rm -rf "$fixture_root"
    return 0
  else
    echo "✗ FAIL: $test_name — loss-report not found"
    echo "$output" | head -10
    FAIL=$((FAIL+1))
    rm -rf "$fixture_root"
    return 1
  fi
}

# AC-11: rollback scope (combined multi-root snapshot — workflow dst INCLUDE)
# discriminating: --apply 후 최신 snapshot tar 의 tar tzf 에 .github/workflows entry 존재.
# snapshot 에서 워크플로 dst 를 빼면(single-root 회귀) entry 미발견 → FAIL.
test_ac11_rollback_scope() {
  local test_name="AC-11-rollback-scope"
  local fixture_root fixture_wrapper fixture_consumer tmp_snapshot

  fixture_root="$(mktemp -d)"
  fixture_wrapper="$fixture_root/fixture-wrapper"
  fixture_consumer="$fixture_root/fixture-consumer"
  tmp_snapshot="$fixture_root/snapshots"

  mkdir -p "$fixture_wrapper/templates/github-workflows" \
           "$fixture_wrapper/templates/scripts" \
           "$fixture_consumer/.github/workflows" \
           "$tmp_snapshot"

  echo "v1" > "$fixture_wrapper/templates/github-workflows/test.yml"
  echo "test.yml" > "$fixture_wrapper/templates/scripts/consumer_applicable_workflows.txt"

  setup_consumer_marker "$fixture_consumer"

  RECONCILE_OVERLAY_WORKFLOW_SRC_DIR="$fixture_wrapper/templates/github-workflows" \
  RECONCILE_OVERLAY_WORKFLOW_DST_DIR="$fixture_consumer/.github/workflows" \
  CONSUMER_APPLICABLE_WHITELIST="$fixture_wrapper/templates/scripts/consumer_applicable_workflows.txt" \
  RECONCILE_OVERLAY_SNAPSHOT_DIR="$tmp_snapshot" \
  CONSUMER_ROOT="$fixture_consumer" \
  bash "$RECONCILE_SH" --apply > /dev/null 2>&1 || true

  local latest_snap
  latest_snap=$(ls "$tmp_snapshot"/*.tar.gz 2>/dev/null | sort -r | head -1 || true)

  if [ -z "$latest_snap" ]; then
    echo "✗ FAIL: $test_name — snapshot not created"
    FAIL=$((FAIL+1))
    rm -rf "$fixture_root"
    return 1
  fi

  local tar_contents
  tar_contents=$(tar tzf "$latest_snap" 2>/dev/null || echo "")

  if echo "$tar_contents" | grep -q "\.github/workflows"; then
    echo "✓ PASS: $test_name — .github/workflows entry in snapshot (multi-root)"
    PASS=$((PASS+1))
    rm -rf "$fixture_root"
    return 0
  else
    echo "✗ FAIL: $test_name — .github/workflows not in snapshot"
    echo "$tar_contents" | head -10
    FAIL=$((FAIL+1))
    rm -rf "$fixture_root"
    return 1
  fi
}

echo "═══════════════════════════════════════════════════════════════════════════════"
echo "CFP-2440 Phase 2: reconcile-overlay.sh workflow channel"
echo "TDD Test Suite (AC-1~11) — discriminating self-test"
echo "═══════════════════════════════════════════════════════════════════════════════"
echo ""

# 결함 2 수정: || true 로 감싸 partial run 허용(첫 FAIL 이 전 suite abort 차단), FAIL 카운터 집계.
test_ac5_anchor_source_base || true
test_ac2_update_not_bootstrap || true
test_ac6_over_broad_enumerate || true
test_ac10_empty_vs_absent_whitelist || true
test_ac8_dry_run || true
test_ac9_idempotency || true
test_ac1_new_propagation || true
test_ac3_filter_skip || true
test_ac4_repo_kind || true
test_ac7_loss_report || true
test_ac11_rollback_scope || true

echo ""
echo "═══════════════════════════════════════════════════════════════════════════════"
echo "Test Results: $PASS passed, $FAIL failed"
echo "═══════════════════════════════════════════════════════════════════════════════"

# 결함 2 수정: 최종 exit 코드 = FAIL>0 여부(CI 게이트 — 실패 시 반드시 non-zero).
if [ "$FAIL" -eq 0 ]; then
  echo "All tests PASSED ✓"
  exit 0
else
  echo "Some tests FAILED ✗"
  exit 1
fi
