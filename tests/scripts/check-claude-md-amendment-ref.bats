#!/usr/bin/env bats
# tests/scripts/check-claude-md-amendment-ref.bats
# CFP-708 / ADR-074 — CLAUDE.md Amendment ref drift detection lint bats tests
#
# TDD Red→Green: 스크립트 구현 전 작성 (Red), 구현 후 PASS (Green)
#
# Test cases (TC-1..TC-8):
#   TC-1 stale:              CLAUDE.md same-line "[ADR-063](...) Amendment 2 (CFP-NNN)" + ADR length=4 → exit 1
#   TC-2 latest:             CLAUDE.md same-line "[ADR-063](...) Amendment 4 (CFP-NNN)" + ADR length=4 → exit 0
#   TC-3 no-amendment-log:   CLAUDE.md same-line "[ADR-999](...) Amendment 1 (CFP-NNN)" + ADR no log → exit 1
#   TC-4 multi-Amendment:    CLAUDE.md 안 다수 same-line ADR cross-ref 동시 detect (각각 verify)
#   TC-5 setup-error:        ADR file 부재 시 exit 2 (setup error)
#   TC-6 phantom-ahead:      ADR link 과 Amendment cite 가 cross-bullet (별도 줄) — pair 미생성 → exit 0
#   TC-7 stale-behind:       ADR link 과 Amendment cite 가 cross-bullet (별도 줄) — pair 미생성 → exit 0
#   TC-8 legitimate-drift:   ADR link 과 Amendment cite 가 same-line + 번호 stale → exit 1 + drift output
#
# AC-5 (CFP-1009): TC-1/3/4/5 fixture line-join rewrite (adjacent→same-line), test intent invariant 보존
#
# Local run: bats tests/scripts/check-claude-md-amendment-ref.bats
# Ubuntu runner: bats 사전 설치, yq 또는 python3 필요 (script 참조)

SCRIPT="$(dirname "$BATS_TEST_FILENAME")/../../scripts/check-claude-md-amendment-ref.sh"
REPO_ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../.." && pwd)"

setup() {
    # 스크립트 존재 확인 (TDD Red: 아직 없으면 skip 대신 fail 유도)
    TEST_DIR="$(mktemp -d 2>/dev/null || mktemp -d -t cfp708)"
    export TEST_DIR

    # python3 필수 (yq 대안)
    if ! command -v python3 &>/dev/null; then
        skip "python3 not available"
    fi

    # 기본 디렉토리 구조 생성
    mkdir -p "$TEST_DIR/docs/adr"
}

teardown() {
    rm -rf "$TEST_DIR"
}

# ─────────────────────────────────────────────────
# TC-1: stale ref — Amendment 2 claim + ADR amendment_log length=4 → exit 1
# ─────────────────────────────────────────────────
@test "TC-1 stale: Amendment 2 claim + ADR has 4 amendments → exit 1 + drift message" {
    # ADR-063 fixture — amendment_log 4 entries
    cat > "$TEST_DIR/docs/adr/ADR-063-marketplace-atomic-invariant.md" <<'ADREOF'
---
adr_number: 63
title: Marketplace atomic invariant fixture
status: Accepted
category: governance
date: 2026-05-12
amendment_log:
  - amendment: 1
    carrier_story: CFP-597
    date: 2026-05-13
    summary: "Amendment 1 summary"
  - amendment: 2
    carrier_story: CFP-631
    date: 2026-05-14
    summary: "Amendment 2 summary"
  - amendment: 3
    carrier_story: CFP-627
    date: 2026-05-14
    summary: "Amendment 3 summary"
  - amendment: 4
    carrier_story: CFP-NNN
    date: 2026-05-15
    summary: "Amendment 4 summary"
---

# ADR-063 fixture body
ADREOF

    # CLAUDE.md fixture — Amendment 2 (CFP-NNN) 언급 (stale: 실제 latest = 4)
    # AC-5 line-join: ADR link + Amendment cite 를 same line 으로 합쳐 same-line strict 대응
    cat > "$TEST_DIR/CLAUDE.md" <<'CLAUDEEOF'
# CLAUDE.md fixture for TC-1

**Marketplace atomic invariant** = [ADR-063](docs/adr/ADR-063-marketplace-atomic-invariant.md) (Amendment 2 (CFP-631) §결정 11 신설 — mirrored field description PR-time mechanical proactive lint mandate.)
CLAUDEEOF

    run bash "$SCRIPT" \
        --claude-md "$TEST_DIR/CLAUDE.md" \
        --adr-dir "$TEST_DIR/docs/adr"

    echo "# status: $status" >&3
    echo "# output: $output" >&3

    # exit 1 — drift detected (warning tier, but lint script exits 1)
    [ "$status" -eq 1 ]
    # drift message 포함
    [[ "$output" == *"DRIFT"* ]] || [[ "$output" == *"stale"* ]] || [[ "$output" == *"drift"* ]]
    # ADR-063 언급
    [[ "$output" == *"ADR-063"* ]] || [[ "$output" == *"063"* ]]
}

# ─────────────────────────────────────────────────
# TC-2: latest — Amendment 4 claim + ADR amendments length=4 → exit 0
# ─────────────────────────────────────────────────
@test "TC-2 latest: Amendment 4 claim + ADR has 4 amendments → exit 0" {
    # ADR-063 fixture — amendments 4 entries (ADR-063 실제 형식)
    cat > "$TEST_DIR/docs/adr/ADR-063-marketplace-atomic-invariant.md" <<'ADREOF'
---
adr_number: 63
title: Marketplace atomic invariant fixture
status: Accepted
category: governance
date: 2026-05-12
amendments:
  - amendment: 1
    date: 2026-05-13
    cfp: CFP-597
    summary: "Amendment 1"
  - amendment: 2
    date: 2026-05-14
    cfp: CFP-631
    summary: "Amendment 2"
  - amendment: 3
    date: 2026-05-14
    cfp: CFP-627
    summary: "Amendment 3"
  - amendment: 4
    date: 2026-05-15
    cfp: CFP-686
    summary: "Amendment 4"
---

# ADR-063 fixture body
ADREOF

    # CLAUDE.md fixture — Amendment 4 (CFP-686) 참조 (latest — length=4 일치)
    cat > "$TEST_DIR/CLAUDE.md" <<'CLAUDEEOF'
# CLAUDE.md fixture for TC-2

**Marketplace atomic invariant** = [ADR-063](docs/adr/ADR-063-marketplace-atomic-invariant.md)
(Amendment 4 (CFP-686) §결정 13 신설 — 정기 detection 의무.)
CLAUDEEOF

    run bash "$SCRIPT" \
        --claude-md "$TEST_DIR/CLAUDE.md" \
        --adr-dir "$TEST_DIR/docs/adr"

    echo "# status: $status" >&3
    echo "# output: $output" >&3

    # exit 0 — latest ref, no drift
    [ "$status" -eq 0 ]
    # PASS 메시지 포함
    [[ "$output" == *"PASS"* ]] || [[ "$output" == *"clean"* ]] || [[ "$output" == *"OK"* ]]
}

# ─────────────────────────────────────────────────
# TC-3: no-amendment-log — CLAUDE.md Amendment 1 claim + ADR에 amendment_log/amendments 없음 → exit 1
# ─────────────────────────────────────────────────
@test "TC-3 no-amendment-log: Amendment 1 claim + ADR has no amendment_log → exit 1" {
    # ADR-999 fixture — amendment_log 없음 (신규 ADR, Amendment 미적용)
    cat > "$TEST_DIR/docs/adr/ADR-999-test-adr.md" <<'ADREOF'
---
adr_number: 999
title: Test ADR without amendment_log
status: Accepted
category: governance
date: 2026-05-14
---

# ADR-999 fixture body (no amendment_log)
ADREOF

    # CLAUDE.md fixture — Amendment 1 (CFP-NNN) 언급 (ADR-999 에 amendment_log 없음)
    # AC-5 line-join: ADR link + Amendment cite 를 same line 으로 합쳐 same-line strict 대응
    cat > "$TEST_DIR/CLAUDE.md" <<'CLAUDEEOF'
# CLAUDE.md fixture for TC-3

Some policy = [ADR-999](docs/adr/ADR-999-test-adr.md) (Amendment 1 (CFP-500) §결정 9 신설.)
CLAUDEEOF

    run bash "$SCRIPT" \
        --claude-md "$TEST_DIR/CLAUDE.md" \
        --adr-dir "$TEST_DIR/docs/adr"

    echo "# status: $status" >&3
    echo "# output: $output" >&3

    # exit 1 — Amendment claim이 있지만 ADR에 amendment_log 없음
    [ "$status" -eq 1 ]
    # 오류 메시지 포함
    [[ "$output" == *"ADR-999"* ]] || [[ "$output" == *"999"* ]]
}

# ─────────────────────────────────────────────────
# TC-4: multi-Amendment — CLAUDE.md 안 다수 ADR cross-ref 동시 detect
#        ADR-060 (Amendment 2 → length=8, stale), ADR-999 (Amendment 1 → length=1, OK)
# ─────────────────────────────────────────────────
@test "TC-4 multi-Amendment: multiple ADR refs — stale ref detected in one → exit 1" {
    # ADR-060 fixture — amendment_log 8 entries (Amendment 8 latest)
    cat > "$TEST_DIR/docs/adr/ADR-060-evidence-enforceable.md" <<'ADREOF'
---
adr_number: 60
title: Evidence-enforceable promotion framework
status: Accepted
category: governance
date: 2026-05-11
amendment_log:
  - amendment: 1
    carrier_story: CFP-390
    date: 2026-05-11
    summary: "A1"
  - amendment: 2
    carrier_story: CFP-455
    date: 2026-05-12
    summary: "A2"
  - amendment: 3
    carrier_story: CFP-449
    date: 2026-05-12
    summary: "A3"
  - amendment: 4
    carrier_story: CFP-481
    date: 2026-05-12
    summary: "A4"
  - amendment: 5
    carrier_story: CFP-531
    date: 2026-05-13
    summary: "A5"
  - amendment: 6
    carrier_story: CFP-509
    date: 2026-05-13
    summary: "A6"
  - amendment: 7
    carrier_story: CFP-508
    date: 2026-05-13
    summary: "A7"
  - amendment: 8
    carrier_story: CFP-530
    date: 2026-05-13
    summary: "A8"
---
# ADR-060 fixture
ADREOF

    # ADR-999 fixture — amendment_log 1 entry (Amendment 1 latest)
    cat > "$TEST_DIR/docs/adr/ADR-999-test-adr.md" <<'ADREOF'
---
adr_number: 999
title: Test ADR with 1 amendment
status: Accepted
category: governance
date: 2026-05-14
amendment_log:
  - amendment: 1
    carrier_story: CFP-500
    date: 2026-05-12
    summary: "A1"
---
# ADR-999 fixture
ADREOF

    # CLAUDE.md fixture:
    #   - ADR-060 Amendment 2 참조 (stale: 실제 latest=8)
    #   - ADR-999 Amendment 1 참조 (OK: latest=1)
    # AC-5 line-join: 두 ADR ref 모두 same-line 형식으로 합침
    # (padding 줄 불필요 — same-line strict 에서는 cross-line 격리 역할 없음)
    cat > "$TEST_DIR/CLAUDE.md" <<'CLAUDEEOF'
# CLAUDE.md fixture for TC-4

## Section A

**Evidence-enforceable** = [ADR-060](docs/adr/ADR-060-evidence-enforceable.md) (Amendment 2 (CFP-455) §결정 3 current_tier required 전환.)

## Section B

**Test ADR** = [ADR-999](docs/adr/ADR-999-test-adr.md) (Amendment 1 (CFP-500) §결정 9 신설.)
CLAUDEEOF

    run bash "$SCRIPT" \
        --claude-md "$TEST_DIR/CLAUDE.md" \
        --adr-dir "$TEST_DIR/docs/adr"

    echo "# status: $status" >&3
    echo "# output: $output" >&3

    # exit 1 — ADR-060 stale ref 감지
    [ "$status" -eq 1 ]
    # ADR-060 drift 언급
    [[ "$output" == *"ADR-060"* ]] || [[ "$output" == *"060"* ]]
    # ADR-999 는 OK (drift 미언급 또는 pass 언급)
}

# ─────────────────────────────────────────────────
# TC-5: setup-error — ADR file 부재 시 exit 2
# ─────────────────────────────────────────────────
@test "TC-5 setup-error: ADR file not found → exit 2" {
    # ADR file 없이 CLAUDE.md만 생성 (ADR-777 참조하지만 파일 없음)
    # AC-5 line-join: ADR link + Amendment cite 를 same line 으로 합쳐 same-line strict 대응
    cat > "$TEST_DIR/CLAUDE.md" <<'CLAUDEEOF'
# CLAUDE.md fixture for TC-5

Missing ADR = [ADR-777](docs/adr/ADR-777-missing.md) (Amendment 1 (CFP-500) §결정 1.)
CLAUDEEOF

    # docs/adr 디렉토리에 ADR-777 없음
    run bash "$SCRIPT" \
        --claude-md "$TEST_DIR/CLAUDE.md" \
        --adr-dir "$TEST_DIR/docs/adr"

    echo "# status: $status" >&3
    echo "# output: $output" >&3

    # exit 2 — setup error (ADR file 부재)
    [ "$status" -eq 2 ]
    # 오류 메시지: ADR file 부재 언급
    [[ "$output" == *"ADR-777"* ]] || [[ "$output" == *"not found"* ]] || [[ "$output" == *"missing"* ]]
}

# ─────────────────────────────────────────────────
# TC-6: phantom-ahead cross-bullet — ADR link 과 Amendment cite 가 다른 줄 (별도 bullet)
#        same-line strict 적용 시 pair 미생성 → exit 0 (no drift output)
#        fixture: CLAUDE.md L185-L189 mimic (link on one bullet, amendment cite on cross-bullet 4 lines away)
# ─────────────────────────────────────────────────
@test "TC-6 phantom-ahead: ADR link and Amendment cite on separate lines → no pair → exit 0" {
    # ADR-038 fixture — amendment_log 4 entries (Amendment 4 latest)
    cat > "$TEST_DIR/docs/adr/ADR-038-progress-visualization.md" <<'ADREOF'
---
adr_number: 38
title: Progress visualization fixture
status: Accepted
category: governance
date: 2026-05-10
amendment_log:
  - amendment: 1
    carrier_story: CFP-274
    date: 2026-05-11
    summary: "A1"
  - amendment: 2
    carrier_story: CFP-500
    date: 2026-05-12
    summary: "A2"
  - amendment: 3
    carrier_story: CFP-501
    date: 2026-05-13
    summary: "A3"
  - amendment: 4
    carrier_story: CFP-502
    date: 2026-05-14
    summary: "A4"
---
# ADR-038 fixture body
ADREOF

    # ADR-040 fixture — amendment_log 6 entries (Amendment 6 latest)
    cat > "$TEST_DIR/docs/adr/ADR-040-worktree-convention.md" <<'ADREOF'
---
adr_number: 40
title: Worktree convention fixture
status: Accepted
category: governance
date: 2026-05-10
amendment_log:
  - amendment: 1
    carrier_story: CFP-136
    date: 2026-05-11
    summary: "A1"
  - amendment: 2
    carrier_story: CFP-139
    date: 2026-05-11
    summary: "A2"
  - amendment: 3
    carrier_story: CFP-341
    date: 2026-05-12
    summary: "A3"
  - amendment: 4
    carrier_story: CFP-426
    date: 2026-05-12
    summary: "A4"
  - amendment: 5
    carrier_story: CFP-531
    date: 2026-05-13
    summary: "A5"
  - amendment: 6
    carrier_story: CFP-843
    date: 2026-05-14
    summary: "A6"
---
# ADR-040 fixture body
ADREOF

    # CLAUDE.md fixture — L185-L189 mimic:
    #   L1: "... [ADR-038](...) ..." — ADR-038 link (no Amendment cite on same line)
    #   L2: blank
    #   L3: blank
    #   L4: "... [ADR-040](...) Amendment 6 (CFP-843) ..." — ADR-040 same-line cite (Amendment 6 = latest → OK)
    #
    # cross-bullet scenario: ADR-038 link on L1, Amendment 6 cite on L4 (4 lines away)
    # same-line strict: ADR-038 must NOT be paired with Amendment 6 (different line)
    # ADR-040 + Amendment 6 same-line pair = latest → exit 0 (no drift)
    cat > "$TEST_DIR/CLAUDE.md" <<'CLAUDEEOF'
# CLAUDE.md fixture for TC-6 (phantom-ahead cross-bullet)

**Progress viz** = [ADR-038](docs/adr/ADR-038-progress-visualization.md) — worktree + hook 정합.

blank line
blank line

**Worktree** = [ADR-040](docs/adr/ADR-040-worktree-convention.md) (Amendment 6 (CFP-843) §결정 7 신설.)
CLAUDEEOF

    run bash "$SCRIPT" \
        --claude-md "$TEST_DIR/CLAUDE.md" \
        --adr-dir "$TEST_DIR/docs/adr"

    echo "# status: $status" >&3
    echo "# output: $output" >&3

    # exit 0 — ADR-038 은 pair 미생성 (cross-bullet), ADR-040 Amendment 6 = latest
    [ "$status" -eq 0 ]
    # ADR-038 drift 출력 없음
    [[ "$output" != *"ADR-038"* ]] || [[ "$output" == *"OK"* ]] || [[ "$output" == *"PASS"* ]]
}

# ─────────────────────────────────────────────────
# TC-7: stale-behind cross-bullet — ADR link 과 Amendment cite 가 다른 줄 (별도 bullet)
#        same-line strict 적용 시 pair 미생성 → exit 0
#        fixture: CLAUDE.md L279-L283 mimic (ADR-060 link on one line, ADR-082 Amendment cite on next line)
# ─────────────────────────────────────────────────
@test "TC-7 stale-behind: ADR link and Amendment cite on separate lines → no pair → exit 0" {
    # ADR-060 fixture — amendment_log 14 entries (Amendment 14 latest)
    cat > "$TEST_DIR/docs/adr/ADR-060-evidence-enforceable-14.md" <<'ADREOF'
---
adr_number: 60
title: Evidence-enforceable promotion framework fixture
status: Accepted
category: governance
date: 2026-05-11
amendment_log:
  - amendment: 1
    carrier_story: CFP-390
    date: 2026-05-11
    summary: "A1"
  - amendment: 2
    carrier_story: CFP-455
    date: 2026-05-12
    summary: "A2"
  - amendment: 3
    carrier_story: CFP-449
    date: 2026-05-12
    summary: "A3"
  - amendment: 4
    carrier_story: CFP-481
    date: 2026-05-12
    summary: "A4"
  - amendment: 5
    carrier_story: CFP-531
    date: 2026-05-13
    summary: "A5"
  - amendment: 6
    carrier_story: CFP-509
    date: 2026-05-13
    summary: "A6"
  - amendment: 7
    carrier_story: CFP-508
    date: 2026-05-13
    summary: "A7"
  - amendment: 8
    carrier_story: CFP-530
    date: 2026-05-13
    summary: "A8"
  - amendment: 9
    carrier_story: CFP-600
    date: 2026-05-14
    summary: "A9"
  - amendment: 10
    carrier_story: CFP-601
    date: 2026-05-14
    summary: "A10"
  - amendment: 11
    carrier_story: CFP-602
    date: 2026-05-14
    summary: "A11"
  - amendment: 12
    carrier_story: CFP-603
    date: 2026-05-15
    summary: "A12"
  - amendment: 13
    carrier_story: CFP-604
    date: 2026-05-15
    summary: "A13"
  - amendment: 14
    carrier_story: CFP-605
    date: 2026-05-15
    summary: "A14"
---
# ADR-060 fixture body
ADREOF

    # ADR-082 fixture — amendment_log 1 entry (Amendment 1 latest)
    cat > "$TEST_DIR/docs/adr/ADR-082-write-time-verify.md" <<'ADREOF'
---
adr_number: 82
title: Write-time self-write verification mandate fixture
status: Accepted
category: governance
date: 2026-05-15
amendment_log:
  - amendment: 1
    carrier_story: CFP-841
    date: 2026-05-15
    summary: "A1"
---
# ADR-082 fixture body
ADREOF

    # CLAUDE.md fixture — L279-L283 mimic:
    #   L1: "... [ADR-060](...) ..." — ADR-060 link (no Amendment cite on same line)
    #   L2: "... [ADR-082](...) Amendment 1 (CFP-841) ..." — ADR-082 same-line (Amendment 1 = latest → OK)
    #
    # stale-behind scenario: ADR-060 link on L1, Amendment 1 cite on L2 (next line)
    # same-line strict: ADR-060 must NOT be paired with Amendment 1 (different line)
    # ADR-082 + Amendment 1 same-line pair = latest → exit 0 (no drift)
    cat > "$TEST_DIR/CLAUDE.md" <<'CLAUDEEOF'
# CLAUDE.md fixture for TC-7 (stale-behind cross-bullet)

**Evidence-enforceable** = [ADR-060](docs/adr/ADR-060-evidence-enforceable-14.md) — 4-tier enforcement framework.
**Write-time verify** = [ADR-082](docs/adr/ADR-082-write-time-verify.md) (Amendment 1 (CFP-841) §결정 6 신설.)
CLAUDEEOF

    run bash "$SCRIPT" \
        --claude-md "$TEST_DIR/CLAUDE.md" \
        --adr-dir "$TEST_DIR/docs/adr"

    echo "# status: $status" >&3
    echo "# output: $output" >&3

    # exit 0 — ADR-060 은 pair 미생성 (cross-bullet), ADR-082 Amendment 1 = latest
    [ "$status" -eq 0 ]
    # PASS 또는 clean 출력
    [[ "$output" == *"PASS"* ]] || [[ "$output" == *"clean"* ]] || [[ "$output" == *"OK"* ]]
}

# ─────────────────────────────────────────────────
# TC-8: legitimate same-line drift — ADR link AND Amendment cite 가 same line
#        + Amendment 번호 stale (< latest) → exit 1 + drift output
# ─────────────────────────────────────────────────
@test "TC-8 legitimate-drift: ADR link and Amendment cite on same line + stale number → exit 1 + drift" {
    # ADR-074 fixture — amendment_log 2 entries (Amendment 2 latest)
    cat > "$TEST_DIR/docs/adr/ADR-074-claude-md-amendment-ref.md" <<'ADREOF'
---
adr_number: 74
title: Claude.md amendment ref drift lint fixture
status: Accepted
category: governance
date: 2026-05-15
amendment_log:
  - amendment: 1
    carrier_story: CFP-708
    date: 2026-05-15
    summary: "A1 initial lint"
  - amendment: 2
    carrier_story: CFP-1009
    date: 2026-05-20
    summary: "A2 same-line strict pure"
---
# ADR-074 fixture body
ADREOF

    # CLAUDE.md fixture — legitimate same-line cite, but Amendment 1 (stale: latest=2)
    # This is the true-positive case: both ADR link and Amendment cite are on same line,
    # and the amendment number is behind the latest.
    cat > "$TEST_DIR/CLAUDE.md" <<'CLAUDEEOF'
# CLAUDE.md fixture for TC-8 (legitimate same-line drift)

**Amendment ref lint** = [ADR-074](docs/adr/ADR-074-claude-md-amendment-ref.md) (Amendment 1 (CFP-708) §결정 8 초기 구현.)
CLAUDEEOF

    run bash "$SCRIPT" \
        --claude-md "$TEST_DIR/CLAUDE.md" \
        --adr-dir "$TEST_DIR/docs/adr"

    echo "# status: $status" >&3
    echo "# output: $output" >&3

    # exit 1 — legitimate same-line stale drift 감지
    [ "$status" -eq 1 ]
    # drift 출력 포함
    [[ "$output" == *"DRIFT"* ]] || [[ "$output" == *"stale"* ]] || [[ "$output" == *"drift"* ]]
    # ADR-074 언급
    [[ "$output" == *"ADR-074"* ]] || [[ "$output" == *"074"* ]]
}
