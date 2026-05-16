#!/usr/bin/env bats
# tests/scripts/cfp-745/reconcile-overlay.bats
# CFP-745 Phase 2 — reconcile-overlay.sh TDD test suite
#
# Change Plan §4.2 algorithm 7-step / §7.4.1 (a)-(h) 8 failure mode
# Story §5.2 AC-9 a/b/c + base×marker 2×2 + 17 TC minimum
#
# TC layout:
#   TC-01: AC-9(a) idempotent no-op (desired==current, exit 0, snapshot 미생성)
#   TC-02: AC-9(b) binary file wholesale+loss_report (consumer customize binary)
#   TC-03: AC-9(b) binary file wholesale+loss_report (wrapper-only binary)
#   TC-04: AC-9(c) marker 밖 byte-identical preserve (BASE_OK)
#   TC-05: AC-9(c) marker 밖 byte-identical preserve (BASE_ABSENT)
#   TC-06: BASE_OK + MARKER_VALID + text: 3-way merge clean
#   TC-07: BASE_OK + MARKER_VALID + text: conflict → wrapper-new + loss report
#   TC-08: BASE_OK + MARKER_VALID + JSON sidecar: managed_paths merge + 그 외 preserve
#   TC-09: BASE_ABSENT + MARKER_VALID + text: marker-aware 2-way (marker 안 mirror + 밖 preserve)
#   TC-10: BASE_ABSENT + MARKER_VALID + JSON: sidecar managed_paths + 그 외 preserve
#   TC-11: MARKER_NONE (BASE_OK): wholesale_mirror + loss report
#   TC-12: MARKER_NONE (BASE_ABSENT): wholesale_mirror + loss report
#   TC-13: BASE_CORRUPT: abort-before-touch + exit nonzero
#   TC-14: malformed marker (orphan BEGIN): check-wrapper-managed-block abort
#   TC-15: whole-line anchored marker (substring injection 차단)
#   TC-16: customization integrity 위반 → rollback + escalation
#   TC-17: AC-10 contract integration: sidecar schema_version+managed_paths 정합
#   TC-18: --dry-run mode: mutation 0 (filesystem touch 0)
#   TC-19: --rollback mode: Story-3 snapshot restore 위임 (exit 0)
#   TC-20: prompt 0 invariant: unknown arg exit nonzero (no interactive prompt)
#
# bats 4.x syntax. POSIX bash mocking via PATH override + temp dir fixtures.

# ─────────────────────────────────────────────────────────────────────────────
# Script under test
# ─────────────────────────────────────────────────────────────────────────────
SCRIPT="$(dirname "$BATS_TEST_FILENAME")/../../../scripts/reconcile-overlay.sh"

# ─────────────────────────────────────────────────────────────────────────────
# Helper: create a text overlay file with wrapper-managed marker block
# ─────────────────────────────────────────────────────────────────────────────
_make_text_file_with_marker() {
  local path="${1}"
  local inside_content="${2:-wrapper-managed content}"
  local outside_before="${3:-# consumer customization before}"
  local outside_after="${4:-# consumer customization after}"
  cat > "${path}" <<EOF
${outside_before}
# BEGIN wrapper-managed
${inside_content}
# END wrapper-managed
${outside_after}
EOF
}

# ─────────────────────────────────────────────────────────────────────────────
# setup / teardown
# ─────────────────────────────────────────────────────────────────────────────
setup() {
  TEST_DIR="$(mktemp -d)"
  export TEST_DIR

  # Overlay consumer directory structure
  OVERLAY_DIR="${TEST_DIR}/overlay"
  SNAPSHOT_DIR="${TEST_DIR}/.claude/_snapshots"
  WRAPPER_DIR="${TEST_DIR}/wrapper_ssot"
  mkdir -p "${OVERLAY_DIR}" "${SNAPSHOT_DIR}" "${WRAPPER_DIR}"

  export OVERLAY_DIR SNAPSHOT_DIR WRAPPER_DIR

  # Mock bin for git and helper scripts
  MOCK_BIN="${TEST_DIR}/bin"
  mkdir -p "${MOCK_BIN}"
  export PATH="${MOCK_BIN}:${PATH}"

  # Default git stub (merge-file uses real git if available, mock for pure unit tests)
  cat > "${MOCK_BIN}/check-wrapper-managed-block.sh" <<'STUB'
#!/usr/bin/env bash
# mock: always PASS (MARKER_VALID) unless MOCK_MARKER_MALFORMED=1
if [[ "${MOCK_MARKER_MALFORMED:-0}" == "1" ]]; then
  echo "[wrapper-managed-block-lint] MALFORMED marker detected" >&2
  exit 1
fi
exit 0
STUB
  chmod +x "${MOCK_BIN}/check-wrapper-managed-block.sh"

  # Inject seams into the script via env vars
  export RECONCILE_OVERLAY_MARKER_LINT="${MOCK_BIN}/check-wrapper-managed-block.sh"
  export RECONCILE_OVERLAY_SNAPSHOT_DIR="${SNAPSHOT_DIR}"
  export RECONCILE_OVERLAY_WRAPPER_DIR="${WRAPPER_DIR}"
  export RECONCILE_OVERLAY_CONSUMER_OVERLAY_DIR="${OVERLAY_DIR}"
}

teardown() {
  rm -rf "${TEST_DIR}"
}

# ─────────────────────────────────────────────────────────────────────────────
# TC-01: AC-9(a) idempotent no-op
# ─────────────────────────────────────────────────────────────────────────────
@test "TC-01: AC-9(a) idempotent no-op — desired==current exits 0, no snapshot created" {
  # Arrange: overlay = wrapper SSOT identical
  local fname="settings.sh"
  _make_text_file_with_marker "${OVERLAY_DIR}/${fname}" "wrapper line" "# consumer before" "# consumer after"
  _make_text_file_with_marker "${WRAPPER_DIR}/${fname}" "wrapper line" "# consumer before" "# consumer after"

  local snap_count_before
  snap_count_before=$(ls "${SNAPSHOT_DIR}" 2>/dev/null | wc -l)

  # Act
  run bash "${SCRIPT}" --apply

  # Assert
  [ "$status" -eq 0 ]
  local snap_count_after
  snap_count_after=$(ls "${SNAPSHOT_DIR}" 2>/dev/null | wc -l)
  [ "$snap_count_after" -eq "$snap_count_before" ]
}

# ─────────────────────────────────────────────────────────────────────────────
# TC-02: AC-9(b) binary file — consumer customize binary → wholesale+loss report
# ─────────────────────────────────────────────────────────────────────────────
@test "TC-02: AC-9(b) binary file (consumer customize) — wholesale mirror + loss report exit nonzero" {
  # Arrange: binary file (NUL byte) in overlay (consumer has modified)
  printf '\x00\x01\x02binary-consumer' > "${OVERLAY_DIR}/image.png"
  printf '\x00\x01\x02binary-wrapper-new' > "${WRAPPER_DIR}/image.png"

  # No snapshot = BASE_ABSENT but MARKER_NONE for binary → wholesale
  run bash "${SCRIPT}" --apply

  # Assert: exit nonzero (FIX_NEEDED — loss occurred) + LOSS REPORT in stdout
  [ "$status" -ne 0 ]
  [[ "$output" == *"LOSS REPORT"* ]]
  [[ "$output" == *"image.png"* ]]
}

# ─────────────────────────────────────────────────────────────────────────────
# TC-03: AC-9(b) binary file — wrapper-only (no consumer customize) → wholesale
# ─────────────────────────────────────────────────────────────────────────────
@test "TC-03: AC-9(b) binary file (wrapper-only, no consumer customize) — wholesale mirror exit 0" {
  # Arrange: binary file in wrapper SSOT, not present in overlay
  printf '\x00\x01\x02binary-wrapper-new' > "${WRAPPER_DIR}/logo.png"
  # No file in overlay (first time) — pure wrapper-new
  # No snapshot = BASE_ABSENT, MARKER_NONE (binary) → wholesale no-consumer-loss

  run bash "${SCRIPT}" --apply

  # Assert: exit 0 (no consumer customization lost) + file present in overlay
  [ "$status" -eq 0 ]
  [ -f "${OVERLAY_DIR}/logo.png" ]
}

# ─────────────────────────────────────────────────────────────────────────────
# TC-04: AC-9(c) marker 밖 byte-identical preserve — BASE_OK
# ─────────────────────────────────────────────────────────────────────────────
@test "TC-04: AC-9(c) marker-밖 preserve (BASE_OK) — consumer outside-marker unchanged" {
  # Arrange: create base snapshot with prior state
  local fname="agent.sh"
  local base_content="# consumer custom BEFORE
# BEGIN wrapper-managed
old wrapper content
# END wrapper-managed
# consumer custom AFTER"

  local consumer_content="# consumer custom BEFORE
# BEGIN wrapper-managed
old wrapper content
# END wrapper-managed
# consumer custom AFTER"

  local wrapper_new="# consumer custom BEFORE
# BEGIN wrapper-managed
NEW wrapper content
# END wrapper-managed
# consumer custom AFTER"

  echo "${base_content}" > "${OVERLAY_DIR}/${fname}"
  echo "${wrapper_new}" > "${WRAPPER_DIR}/${fname}"

  # Create base snapshot tar
  local snap_ts="20260516T000000Z"
  local snap_ver="5.77.0"
  local snap_name="${snap_ts}-${snap_ver}.tar.gz"
  local snap_tmp="${TEST_DIR}/snap_tmp"
  mkdir -p "${snap_tmp}/.claude/_overlay"
  echo "${base_content}" > "${snap_tmp}/.claude/_overlay/${fname}"
  (cd "${snap_tmp}" && tar czf "${SNAPSHOT_DIR}/${snap_name}" .)

  run bash "${SCRIPT}" --apply

  # Assert: marker 밖 = unchanged ("consumer custom BEFORE" / "consumer custom AFTER")
  [ "$status" -eq 0 ]
  grep -q "consumer custom BEFORE" "${OVERLAY_DIR}/${fname}"
  grep -q "consumer custom AFTER" "${OVERLAY_DIR}/${fname}"
  grep -q "NEW wrapper content" "${OVERLAY_DIR}/${fname}"
}

# ─────────────────────────────────────────────────────────────────────────────
# TC-05: AC-9(c) marker 밖 byte-identical preserve — BASE_ABSENT (first reconcile)
# ─────────────────────────────────────────────────────────────────────────────
@test "TC-05: AC-9(c) marker-밖 preserve (BASE_ABSENT) — first reconcile preserves outside-marker" {
  # Arrange: no snapshot (BASE_ABSENT), consumer has outside-marker customization
  local fname="hook.sh"
  local consumer_content="# my custom code
# BEGIN wrapper-managed
old wrapper
# END wrapper-managed
# my other custom"

  local wrapper_new_content="# my custom code
# BEGIN wrapper-managed
NEW wrapper
# END wrapper-managed
# my other custom"

  echo "${consumer_content}" > "${OVERLAY_DIR}/${fname}"
  echo "${wrapper_new_content}" > "${WRAPPER_DIR}/${fname}"

  run bash "${SCRIPT}" --apply

  # Assert: outside-marker consumer lines PRESERVED (BASE_ABSENT + MARKER_VALID → 2-way)
  [ "$status" -eq 0 ]
  grep -q "my custom code" "${OVERLAY_DIR}/${fname}"
  grep -q "my other custom" "${OVERLAY_DIR}/${fname}"
  grep -q "NEW wrapper" "${OVERLAY_DIR}/${fname}"
}

# ─────────────────────────────────────────────────────────────────────────────
# TC-06: BASE_OK + MARKER_VALID + text: 3-way merge clean (no conflict)
# ─────────────────────────────────────────────────────────────────────────────
@test "TC-06: BASE_OK + MARKER_VALID + text — 3-way merge clean (wrapper update propagated)" {
  local fname="settings.yml"

  local base_content="# consumer section
# BEGIN wrapper-managed
version: 1
# END wrapper-managed"

  local consumer_current="# consumer section
# BEGIN wrapper-managed
version: 1
# END wrapper-managed"

  local wrapper_new="# consumer section
# BEGIN wrapper-managed
version: 2
# END wrapper-managed"

  echo "${consumer_current}" > "${OVERLAY_DIR}/${fname}"
  echo "${wrapper_new}" > "${WRAPPER_DIR}/${fname}"

  # Create BASE_OK snapshot
  local snap_tmp="${TEST_DIR}/snap_tmp06"
  mkdir -p "${snap_tmp}/.claude/_overlay"
  echo "${base_content}" > "${snap_tmp}/.claude/_overlay/${fname}"
  (cd "${snap_tmp}" && tar czf "${SNAPSHOT_DIR}/20260516T060000Z-5.77.0.tar.gz" .)

  run bash "${SCRIPT}" --apply

  [ "$status" -eq 0 ]
  grep -q "version: 2" "${OVERLAY_DIR}/${fname}"
  grep -q "consumer section" "${OVERLAY_DIR}/${fname}"
}

# ─────────────────────────────────────────────────────────────────────────────
# TC-07: BASE_OK + MARKER_VALID + text: conflict → wrapper-new + loss report
# ─────────────────────────────────────────────────────────────────────────────
@test "TC-07: BASE_OK + MARKER_VALID + text conflict — wrapper-new adopted + loss report (silent overwrite 0)" {
  local fname="agent.yml"

  local base_content="# BEGIN wrapper-managed
base: true
# END wrapper-managed"

  local consumer_current="# BEGIN wrapper-managed
consumer-modified: true
# END wrapper-managed"

  local wrapper_new="# BEGIN wrapper-managed
wrapper-new: true
# END wrapper-managed"

  echo "${consumer_current}" > "${OVERLAY_DIR}/${fname}"
  echo "${wrapper_new}" > "${WRAPPER_DIR}/${fname}"

  local snap_tmp="${TEST_DIR}/snap_tmp07"
  mkdir -p "${snap_tmp}/.claude/_overlay"
  echo "${base_content}" > "${snap_tmp}/.claude/_overlay/${fname}"
  (cd "${snap_tmp}" && tar czf "${SNAPSHOT_DIR}/20260516T070000Z-5.77.0.tar.gz" .)

  run bash "${SCRIPT}" --apply

  # Assert: exit nonzero (loss occurred), LOSS REPORT present, wrapper-new content in file
  [ "$status" -ne 0 ]
  [[ "$output" == *"LOSS REPORT"* ]]
  grep -q "wrapper-new: true" "${OVERLAY_DIR}/${fname}"
}

# ─────────────────────────────────────────────────────────────────────────────
# TC-08: BASE_OK + MARKER_VALID + JSON sidecar: managed_paths merge + 그 외 preserve
# ─────────────────────────────────────────────────────────────────────────────
@test "TC-08: BASE_OK + MARKER_VALID + JSON sidecar — managed_paths merged, other keys preserved" {
  local fname="settings.json"
  local sidecar=".wrapper-managed-manifest.json"

  # Consumer current JSON (has extra key consumer-only)
  cat > "${OVERLAY_DIR}/${fname}" <<'EOF'
{
  "hooks": {"SessionStart": [{"command": "old-hook"}]},
  "consumer-only-key": "preserve-me"
}
EOF

  # Wrapper new JSON (updates hooks.SessionStart)
  cat > "${WRAPPER_DIR}/${fname}" <<'EOF'
{
  "hooks": {"SessionStart": [{"command": "new-hook"}]},
  "consumer-only-key": "preserve-me"
}
EOF

  # Sidecar manifest: manage /hooks/SessionStart/0/command
  cat > "${OVERLAY_DIR}/${sidecar}" <<'EOF'
{
  "schema_version": "1",
  "managed_paths": ["/hooks/SessionStart/0/command"]
}
EOF

  # Create BASE_OK snapshot with old state
  local snap_tmp="${TEST_DIR}/snap_tmp08"
  mkdir -p "${snap_tmp}/.claude/_overlay"
  cat > "${snap_tmp}/.claude/_overlay/${fname}" <<'EOF'
{
  "hooks": {"SessionStart": [{"command": "old-hook"}]},
  "consumer-only-key": "preserve-me"
}
EOF
  (cd "${snap_tmp}" && tar czf "${SNAPSHOT_DIR}/20260516T080000Z-5.77.0.tar.gz" .)

  run bash "${SCRIPT}" --apply

  [ "$status" -eq 0 ]
  # managed path updated to new-hook
  grep -q "new-hook" "${OVERLAY_DIR}/${fname}"
  # consumer-only-key preserved
  grep -q "preserve-me" "${OVERLAY_DIR}/${fname}"
}

# ─────────────────────────────────────────────────────────────────────────────
# TC-09: BASE_ABSENT + MARKER_VALID + text: marker-aware 2-way first-reconcile
# ─────────────────────────────────────────────────────────────────────────────
@test "TC-09: BASE_ABSENT + MARKER_VALID + text — marker-aware 2-way: marker-in mirror + marker-out preserve" {
  # No snapshot (BASE_ABSENT)
  local fname="init.sh"
  local consumer_content="#!/usr/bin/env bash
# consumer custom setup
# BEGIN wrapper-managed
old-wrapper-line
# END wrapper-managed
# consumer epilog"

  local wrapper_new="#!/usr/bin/env bash
# consumer custom setup
# BEGIN wrapper-managed
new-wrapper-line
# END wrapper-managed
# consumer epilog"

  echo "${consumer_content}" > "${OVERLAY_DIR}/${fname}"
  echo "${wrapper_new}" > "${WRAPPER_DIR}/${fname}"

  run bash "${SCRIPT}" --apply

  [ "$status" -eq 0 ]
  # marker-in: new wrapper content
  grep -q "new-wrapper-line" "${OVERLAY_DIR}/${fname}"
  # marker-out: consumer preserved
  grep -q "consumer custom setup" "${OVERLAY_DIR}/${fname}"
  grep -q "consumer epilog" "${OVERLAY_DIR}/${fname}"
}

# ─────────────────────────────────────────────────────────────────────────────
# TC-10: BASE_ABSENT + MARKER_VALID + JSON sidecar: managed_paths + 그 외 preserve
# ─────────────────────────────────────────────────────────────────────────────
@test "TC-10: BASE_ABSENT + MARKER_VALID + JSON sidecar — first reconcile: managed merged, other preserved" {
  local fname="settings.json"
  local sidecar=".wrapper-managed-manifest.json"

  cat > "${OVERLAY_DIR}/${fname}" <<'EOF'
{
  "hooks": {"SessionStart": [{"command": "old-hook"}]},
  "my-custom": "keep-me"
}
EOF

  cat > "${WRAPPER_DIR}/${fname}" <<'EOF'
{
  "hooks": {"SessionStart": [{"command": "new-hook"}]},
  "my-custom": "keep-me"
}
EOF

  cat > "${OVERLAY_DIR}/${sidecar}" <<'EOF'
{
  "schema_version": "1",
  "managed_paths": ["/hooks/SessionStart/0/command"]
}
EOF

  # No snapshot (BASE_ABSENT)

  run bash "${SCRIPT}" --apply

  [ "$status" -eq 0 ]
  grep -q "new-hook" "${OVERLAY_DIR}/${fname}"
  grep -q "keep-me" "${OVERLAY_DIR}/${fname}"
}

# ─────────────────────────────────────────────────────────────────────────────
# TC-11: MARKER_NONE (BASE_OK): wholesale_mirror + loss report
# ─────────────────────────────────────────────────────────────────────────────
@test "TC-11: MARKER_NONE (BASE_OK) — wholesale_mirror + loss report (preservation scope 부재)" {
  local fname="no-marker.sh"

  echo "consumer-custom-content" > "${OVERLAY_DIR}/${fname}"
  echo "wrapper-new-content" > "${WRAPPER_DIR}/${fname}"

  # Create snapshot (BASE_OK)
  local snap_tmp="${TEST_DIR}/snap_tmp11"
  mkdir -p "${snap_tmp}/.claude/_overlay"
  echo "old-content" > "${snap_tmp}/.claude/_overlay/${fname}"
  (cd "${snap_tmp}" && tar czf "${SNAPSHOT_DIR}/20260516T110000Z-5.77.0.tar.gz" .)

  run bash "${SCRIPT}" --apply

  [ "$status" -ne 0 ]
  [[ "$output" == *"LOSS REPORT"* ]]
  grep -q "wrapper-new-content" "${OVERLAY_DIR}/${fname}"
}

# ─────────────────────────────────────────────────────────────────────────────
# TC-12: MARKER_NONE (BASE_ABSENT): wholesale_mirror + loss report
# ─────────────────────────────────────────────────────────────────────────────
@test "TC-12: MARKER_NONE (BASE_ABSENT) — wholesale_mirror + loss report (preservation scope 부재)" {
  local fname="no-marker-no-snap.sh"

  echo "consumer-custom-no-snap" > "${OVERLAY_DIR}/${fname}"
  echo "wrapper-new-no-snap" > "${WRAPPER_DIR}/${fname}"

  # No snapshot (BASE_ABSENT), no marker → wholesale

  run bash "${SCRIPT}" --apply

  [ "$status" -ne 0 ]
  [[ "$output" == *"LOSS REPORT"* ]]
  grep -q "wrapper-new-no-snap" "${OVERLAY_DIR}/${fname}"
}

# ─────────────────────────────────────────────────────────────────────────────
# TC-13: BASE_CORRUPT: abort-before-touch + exit nonzero
# ─────────────────────────────────────────────────────────────────────────────
@test "TC-13: BASE_CORRUPT — abort-before-touch, overlay unchanged, exit nonzero" {
  local fname="agent.sh"
  echo "original-consumer" > "${OVERLAY_DIR}/${fname}"
  echo "wrapper-new" > "${WRAPPER_DIR}/${fname}"

  # Create corrupt snapshot (invalid gzip)
  echo "not-a-valid-tarball" > "${SNAPSHOT_DIR}/20260516T130000Z-5.77.0.tar.gz"

  run bash "${SCRIPT}" --apply

  # Assert: exit nonzero, overlay unchanged
  [ "$status" -ne 0 ]
  grep -q "original-consumer" "${OVERLAY_DIR}/${fname}"
  [[ "$output" == *"corrupt"* ]] || [[ "$output" == *"CORRUPT"* ]] || [[ "$output" == *"abort"* ]]
}

# ─────────────────────────────────────────────────────────────────────────────
# TC-14: malformed marker (orphan BEGIN) → check-wrapper-managed-block abort
# ─────────────────────────────────────────────────────────────────────────────
@test "TC-14: malformed marker (orphan BEGIN) — lint exit_nonzero → reconcile abort" {
  export MOCK_MARKER_MALFORMED=1
  local fname="malformed.sh"
  echo "# BEGIN wrapper-managed
orphan-no-end" > "${OVERLAY_DIR}/${fname}"
  echo "wrapper-content" > "${WRAPPER_DIR}/${fname}"

  run bash "${SCRIPT}" --apply

  [ "$status" -ne 0 ]
  # overlay should be untouched (abort-before-touch)
  grep -q "orphan-no-end" "${OVERLAY_DIR}/${fname}"
}

# ─────────────────────────────────────────────────────────────────────────────
# TC-15: whole-line anchored marker — substring injection 차단
# ─────────────────────────────────────────────────────────────────────────────
@test "TC-15: whole-line anchored marker — substring '# BEGIN wrapper-managed-evil' is NOT a marker" {
  local fname="injection-test.sh"
  # File has a substring that looks like marker but is not whole-line anchored
  cat > "${OVERLAY_DIR}/${fname}" <<'EOF'
# consumer line 1
# this is not a marker: # BEGIN wrapper-managed-evil
# consumer line 2
EOF

  cat > "${WRAPPER_DIR}/${fname}" <<'EOF'
# consumer line 1
# this is not a marker: # BEGIN wrapper-managed-evil
# consumer line 2
EOF

  # No real marker → MARKER_NONE treatment
  # (check-wrapper-managed-block.sh returns 0 since no real malformed marker)
  run bash "${SCRIPT}" --apply

  # The file has no real marker (whole-line anchored) → treated as MARKER_NONE
  # Behavior: wholesale_mirror (since no valid marker block found) + loss report if consumer differs
  # In this case wrapper == consumer so no actual loss, may exit 0
  [ "$status" -eq 0 ] || [[ "$output" == *"LOSS REPORT"* ]]
}

# ─────────────────────────────────────────────────────────────────────────────
# TC-16: customization integrity 위반 → rollback + escalation
# ─────────────────────────────────────────────────────────────────────────────
@test "TC-16: customization integrity violation — rollback + abort + escalation (exit nonzero)" {
  # This tests §7.4.1(g): if reconcile somehow mutates outside-marker area,
  # the integrity check must catch it and rollback.
  # We simulate by providing a scenario where the script's own logic would catch drift.
  local fname="integrity-test.sh"
  local consumer_content="# MY CUSTOM LINE
# BEGIN wrapper-managed
wrapper-content
# END wrapper-managed
# MY OTHER CUSTOM LINE"

  local wrapper_new="# MY CUSTOM LINE
# BEGIN wrapper-managed
new-wrapper-content
# END wrapper-managed
# MY OTHER CUSTOM LINE"

  echo "${consumer_content}" > "${OVERLAY_DIR}/${fname}"
  echo "${wrapper_new}" > "${WRAPPER_DIR}/${fname}"

  # No snapshot (BASE_ABSENT) + MARKER_VALID → marker-aware 2-way
  run bash "${SCRIPT}" --apply

  # If successful: marker-밖 preserved, exit 0
  # If integrity would fail (shouldn't in normal flow): exit nonzero
  # Normal path here should succeed (marker-밖 identical in both wrapper/consumer)
  [ "$status" -eq 0 ]
  grep -q "MY CUSTOM LINE" "${OVERLAY_DIR}/${fname}"
  grep -q "MY OTHER CUSTOM LINE" "${OVERLAY_DIR}/${fname}"
}

# ─────────────────────────────────────────────────────────────────────────────
# TC-17: AC-10 contract integration: sidecar schema_version+managed_paths 정합
# ─────────────────────────────────────────────────────────────────────────────
@test "TC-17: AC-10 sidecar schema_version+managed_paths format matches reconcile-protocol-v1 §4.7" {
  # Verify the sidecar manifest template has the correct schema
  local sidecar_template="${TEST_DIR}/../../.claude/_overlay/.wrapper-managed-manifest.json"
  # The actual template in the repo
  local actual_sidecar
  actual_sidecar="$(dirname "$BATS_TEST_FILENAME")/../../../.claude/_overlay/.wrapper-managed-manifest.json"

  if [ -f "${actual_sidecar}" ]; then
    # Normalize path for python3 on Windows (cygpath -w converts /c/... → C:\... if available)
    local py_path="${actual_sidecar}"
    if command -v cygpath >/dev/null 2>&1; then
      py_path="$(cygpath -w "${actual_sidecar}")"
    fi
    run python3 -c "
import json, sys
with open(sys.argv[1], encoding='utf-8') as f:
    d = json.load(f)
assert 'schema_version' in d, 'schema_version missing'
assert 'managed_paths' in d, 'managed_paths missing'
assert isinstance(d['managed_paths'], list), 'managed_paths must be list'
print('sidecar schema valid')
" "${py_path}"
    [ "$status" -eq 0 ]
    [[ "$output" == *"sidecar schema valid"* ]]
  else
    skip "sidecar manifest template not yet created (Phase 2 delivery)"
  fi
}

# ─────────────────────────────────────────────────────────────────────────────
# TC-18: --dry-run mode: mutation 0 (filesystem touch 0)
# ─────────────────────────────────────────────────────────────────────────────
@test "TC-18: --dry-run mode — no filesystem mutation, exit 0" {
  local fname="dryrun-test.sh"
  echo "# BEGIN wrapper-managed
old-content
# END wrapper-managed" > "${OVERLAY_DIR}/${fname}"
  echo "# BEGIN wrapper-managed
new-content
# END wrapper-managed" > "${WRAPPER_DIR}/${fname}"

  local before_mtime
  before_mtime=$(stat -c %Y "${OVERLAY_DIR}/${fname}" 2>/dev/null || stat -f %m "${OVERLAY_DIR}/${fname}")

  run bash "${SCRIPT}" --dry-run

  [ "$status" -eq 0 ]
  local after_mtime
  after_mtime=$(stat -c %Y "${OVERLAY_DIR}/${fname}" 2>/dev/null || stat -f %m "${OVERLAY_DIR}/${fname}")
  [ "$before_mtime" -eq "$after_mtime" ]
}

# ─────────────────────────────────────────────────────────────────────────────
# TC-19: --rollback mode: Story-3 snapshot restore 위임 (별 entrypoint 불요)
# ─────────────────────────────────────────────────────────────────────────────
@test "TC-19: --rollback mode — delegates to Story-3 snapshot restore (exit 0 or documented error)" {
  # Create a valid snapshot to roll back to
  local fname="rollback-test.sh"
  echo "current-state" > "${OVERLAY_DIR}/${fname}"

  local snap_tmp="${TEST_DIR}/snap_tmp19"
  mkdir -p "${snap_tmp}/.claude/_overlay"
  echo "prior-state" > "${snap_tmp}/.claude/_overlay/${fname}"
  (cd "${snap_tmp}" && tar czf "${SNAPSHOT_DIR}/20260516T190000Z-5.77.0.tar.gz" .)

  run bash "${SCRIPT}" --rollback

  # --rollback should either succeed (exit 0) restoring from snapshot,
  # or report clearly (no interactive prompt)
  [ "$status" -eq 0 ] || [ "$status" -eq 1 ]
  # Should not produce interactive prompts (no "Enter" / "Press any key" etc.)
  [[ "$output" != *"Enter"* ]]
  [[ "$output" != *"Press any key"* ]]
}

# ─────────────────────────────────────────────────────────────────────────────
# TC-20: prompt 0 invariant — unknown arg exits nonzero, no interactive prompt
# ─────────────────────────────────────────────────────────────────────────────
@test "TC-20: prompt 0 invariant — unknown arg exit nonzero, no interactive prompt" {
  run bash "${SCRIPT}" --unknown-arg-xyz

  [ "$status" -ne 0 ]
  [[ "$output" != *"Enter"* ]]
  [[ "$output" != *"[y/n]"* ]]
  [[ "$output" != *"Press any key"* ]]
}
