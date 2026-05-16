#!/usr/bin/env bash
# reconcile-overlay.sh — CFP-745 Wave 2 Story-5 — overlay 영역 3-way merge reconcile runtime
#
# Change Plan §3.4 algorithm (7-step) / §4.1 CLI / §4.2 per-file 3-way merge
# §4.4 ownership 경계 / §4.5 sidecar manifest schema / §7.4.1 (a)-(h) DR
# Story AC-1..AC-10 + EPIC-AC-4 (silent overwrite 0) + reconcile-protocol-v1 v1.4 §4.7
#
# 역할: overlay 3-way merge orchestration shell ONLY (Refactor 결론, §4.4)
#   - agent-fm 2-way merge = merge.py SSOT 위임 (semantic 분산 0)
#   - D4 marker lint = check-wrapper-managed-block.sh 위임 (변경 0)
#   - base 확보 = Story-3 snapshot infra 재사용 (재구현 0)
#   - user_decision_branches: 0 (no prompt — Epic §1 WHY "0 자리")
#
# 환경 변수 (test seam — 프로덕션은 기본값 사용):
#   RECONCILE_OVERLAY_MARKER_LINT     — marker lint 스크립트 경로
#   RECONCILE_OVERLAY_SNAPSHOT_DIR   — snapshot 디렉터리 경로
#   RECONCILE_OVERLAY_WRAPPER_DIR    — wrapper SSOT overlay 템플릿 경로
#   RECONCILE_OVERLAY_CONSUMER_OVERLAY_DIR — consumer overlay 경로
#
# SecurityArch §7.2: whole-line anchored marker (substring injection 차단, ADR-027 §결정 7.D.3)
# ADR-061 정합 — heredoc-python 0 (multi-line python = 외부 .py 의무, bash POSIX only here)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT_NAME="[reconcile-overlay]"

# ─────────────────────────────────────────────────────────────────────────────
# §4.4 Ownership 경계 — 외부 SSOT 연결 (test-injectable seams)
# ─────────────────────────────────────────────────────────────────────────────
MARKER_LINT="${RECONCILE_OVERLAY_MARKER_LINT:-${SCRIPT_DIR}/check-wrapper-managed-block.sh}"
SNAPSHOT_DIR="${RECONCILE_OVERLAY_SNAPSHOT_DIR:-${HOME}/.claude/_snapshots}"
WRAPPER_SSOT_DIR="${RECONCILE_OVERLAY_WRAPPER_DIR:-${SCRIPT_DIR}/../.claude/_overlay}"
CONSUMER_OVERLAY_DIR="${RECONCILE_OVERLAY_CONSUMER_OVERLAY_DIR:-${SCRIPT_DIR}/../.claude/_overlay}"
JSON_MERGE_PY="${SCRIPT_DIR}/lib/reconcile_json_sidecar.py"
VALIDATE_SIDECAR_PY="${SCRIPT_DIR}/lib/validate_sidecar.py"

# Normalize to absolute paths
WRAPPER_SSOT_DIR="$(cd "${WRAPPER_SSOT_DIR}" 2>/dev/null && pwd || echo "${WRAPPER_SSOT_DIR}")"
CONSUMER_OVERLAY_DIR="$(cd "${CONSUMER_OVERLAY_DIR}" 2>/dev/null && pwd || echo "${CONSUMER_OVERLAY_DIR}")"

# FIFO N=5 snapshot retention (Story-3 §4 SSOT 재사용)
SNAPSHOT_RETENTION="${RECONCILE_OVERLAY_SNAPSHOT_RETENTION:-5}"

# ─────────────────────────────────────────────────────────────────────────────
# §4.1 CLI 인자 schema (ADR-076 §결정 3 dry-run/apply/rollback 3-mode enum)
# ─────────────────────────────────────────────────────────────────────────────
MODE="apply"
MODE_SET_COUNT=0

_usage() {
    cat <<'USAGE'
reconcile-overlay.sh — CFP-745 overlay 영역 3-way merge reconcile runtime (A3)

사용법:
  bash scripts/reconcile-overlay.sh --apply
  bash scripts/reconcile-overlay.sh --dry-run
  bash scripts/reconcile-overlay.sh --rollback

옵션:
  --apply     (default) overlay 영역 3-way merge reconcile 실행 (mutation)
  --dry-run   preview only — 3-way merge 결과 표시, filesystem touch 0
  --rollback  직전 Story-3 snapshot 에서 restore (overlay reconcile snapshot 재사용)

원칙:
  - 사용자 결정 분기 0 (no prompt — reconcile-protocol-v1 user_decision_branches: 0)
  - marker 밖 = consumer-current byte-identical preserve (EPIC-AC-4 silent overwrite 0)
  - marker 안 = wrapper SSOT mirror (3-way merge / 2-way first-reconcile)
  - BASE_CORRUPT = abort-before-touch (partial-state 0)
  - MARKER_NONE = wholesale_mirror_with_user_visible_loss_report (ADR-027 §결정 7.C)
USAGE
}

if [[ $# -gt 0 ]]; then
    MODE=""
    while [[ $# -gt 0 ]]; do
        case "${1}" in
            --apply)
                MODE="apply"
                (( MODE_SET_COUNT++ )) || true
                shift
                ;;
            --dry-run)
                MODE="dry-run"
                (( MODE_SET_COUNT++ )) || true
                shift
                ;;
            --rollback)
                MODE="rollback"
                (( MODE_SET_COUNT++ )) || true
                shift
                ;;
            --help|-h)
                _usage
                exit 0
                ;;
            *)
                echo "${SCRIPT_NAME} 오류: 알 수 없는 인자 '${1}'" >&2
                echo "${SCRIPT_NAME} 허용 인자: --apply | --dry-run | --rollback" >&2
                exit 1
                ;;
        esac
    done
fi

# mode 미설정 시 기본값
if [[ -z "${MODE:-}" ]]; then
    MODE="apply"
fi

# mode 정확히 1개 강제
if [[ "${MODE_SET_COUNT}" -gt 1 ]]; then
    echo "${SCRIPT_NAME} 오류: mode 인자는 1개만 허용 (--apply / --dry-run / --rollback)" >&2
    exit 1
fi

# ─────────────────────────────────────────────────────────────────────────────
# §4.1 --rollback: Story-3 snapshot restore 위임 (별 entrypoint 불요)
# ─────────────────────────────────────────────────────────────────────────────
if [[ "${MODE}" == "rollback" ]]; then
    echo "${SCRIPT_NAME} --rollback: Story-3 snapshot restore 위임"
    local_latest_snapshot=""
    if ls "${SNAPSHOT_DIR}"/*.tar.gz 2>/dev/null | sort -r | head -1 > /dev/null 2>&1; then
        local_latest_snapshot=$(ls "${SNAPSHOT_DIR}"/*.tar.gz 2>/dev/null | sort -r | head -1 || true)
    fi

    if [[ -z "${local_latest_snapshot}" ]]; then
        echo "${SCRIPT_NAME} 오류: 복원할 snapshot 이 없습니다. (${SNAPSHOT_DIR} 비어있음)" >&2
        exit 1
    fi

    echo "${SCRIPT_NAME} snapshot 복원: $(basename "${local_latest_snapshot}")"
    local overlay_parent
    overlay_parent="$(dirname "${CONSUMER_OVERLAY_DIR}")"
    local overlay_base
    overlay_base="$(basename "${CONSUMER_OVERLAY_DIR}")"

    tar xzf "${local_latest_snapshot}" -C "${overlay_parent}" 2>/dev/null || {
        echo "${SCRIPT_NAME} snapshot 복원 실패 (corrupt?)" >&2
        exit 1
    }
    echo "${SCRIPT_NAME} snapshot 복원 완료"
    exit 0
fi

# ─────────────────────────────────────────────────────────────────────────────
# 내부 헬퍼
# ─────────────────────────────────────────────────────────────────────────────

# whole-line anchored marker detection (ADR-027 §결정 7.D.3 — `grep -xF` style)
_has_marker_begin_sh() {
    local file="${1}"
    grep -qxF "# BEGIN wrapper-managed" "${file}" 2>/dev/null
}
_has_marker_end_sh() {
    local file="${1}"
    grep -qxF "# END wrapper-managed" "${file}" 2>/dev/null
}
_has_marker_begin_md() {
    local file="${1}"
    grep -qxF "<!-- BEGIN wrapper-managed -->" "${file}" 2>/dev/null
}
_has_marker_end_md() {
    local file="${1}"
    grep -qxF "<!-- END wrapper-managed -->" "${file}" 2>/dev/null
}

# Determine file type and marker validity (whole-line anchored, ADR-027 §결정 7.A.1)
_file_marker_capability() {
    local file="${1}"
    local ext="${file##*.}"
    # Binary check first (NUL byte)
    if LC_ALL=C grep -qP '\x00' "${file}" 2>/dev/null; then
        echo "binary"
        return
    fi
    case "${ext}" in
        yml|yaml|sh)
            if _has_marker_begin_sh "${file}" && _has_marker_end_sh "${file}"; then
                echo "text_marker_valid"
            else
                echo "text_marker_none"
            fi
            ;;
        md)
            if _has_marker_begin_md "${file}" && _has_marker_end_md "${file}"; then
                echo "text_marker_valid"
            else
                echo "text_marker_none"
            fi
            ;;
        json)
            echo "json_incapable"
            ;;
        png|jpg|jpeg|gif|pdf|zip|tar|gz)
            echo "binary"
            ;;
        *)
            echo "text_marker_none"
            ;;
    esac
}

# Extract inside-marker content
_extract_inside_marker_sh() {
    local file="${1}"
    awk '/^# BEGIN wrapper-managed$/{found=1; next} found && /^# END wrapper-managed$/{found=0; next} found{print}' "${file}"
}

# Reconstruct file: outside (from consumer) + marker block (from inside_content_file)
_reconstruct_sh() {
    local consumer_file="${1}"
    local inside_content_file="${2}"
    local output_file="${3}"
    local tmp_out
    tmp_out=$(mktemp)

    local before_marker=()
    local after_marker=()
    local in_marker=false
    local found_begin=false

    while IFS= read -r line; do
        if [[ "${line}" == "# BEGIN wrapper-managed" ]]; then
            found_begin=true
            in_marker=true
            continue
        fi
        if [[ "${line}" == "# END wrapper-managed" ]]; then
            in_marker=false
            continue
        fi
        if ! "${found_begin}"; then
            before_marker+=("${line}")
        elif ! "${in_marker}"; then
            after_marker+=("${line}")
        fi
    done < "${consumer_file}"

    {
        local ln
        for ln in "${before_marker[@]+"${before_marker[@]}"}"; do
            printf '%s\n' "${ln}"
        done
        echo "# BEGIN wrapper-managed"
        cat "${inside_content_file}"
        echo "# END wrapper-managed"
        for ln in "${after_marker[@]+"${after_marker[@]}"}"; do
            printf '%s\n' "${ln}"
        done
    } > "${tmp_out}"

    mv "${tmp_out}" "${output_file}"
}

# Outside-marker fingerprint for integrity check (AC-9(c))
_outside_marker_fingerprint_sh() {
    local file="${1}"
    awk '/^# BEGIN wrapper-managed$/{skip=1; next} skip && /^# END wrapper-managed$/{skip=0; next} !skip{print}' "${file}" \
        | md5sum 2>/dev/null \
        || awk '/^# BEGIN wrapper-managed$/{skip=1; next} skip && /^# END wrapper-managed$/{skip=0; next} !skip{print}' "${file}" \
        | openssl dgst -md5 2>/dev/null | awk '{print $NF}' \
        || echo "nohash"
}

# ─────────────────────────────────────────────────────────────────────────────
# Loss report accumulator (EPIC-AC-4 silent overwrite 0)
# ─────────────────────────────────────────────────────────────────────────────
LOSS_REPORT_ITEMS=()

_add_loss_report() {
    local file="${1}"
    local reason="${2}"
    LOSS_REPORT_ITEMS+=("  - ${file}: ${reason}")
}

_print_loss_report() {
    if [[ "${#LOSS_REPORT_ITEMS[@]}" -gt 0 ]]; then
        echo ""
        echo "=== LOSS REPORT ==="
        for item in "${LOSS_REPORT_ITEMS[@]}"; do
            echo "${item}"
        done
        echo "=== END LOSS REPORT ==="
        echo ""
        echo "${SCRIPT_NAME} 경고: consumer customization 손실 발생. 위 파일을 확인하세요."
        echo "${SCRIPT_NAME} 힌트: scripts/migrate-existing-customization.sh 로 marker wrap 후 재실행 권장"
    fi
}

# ─────────────────────────────────────────────────────────────────────────────
# §4.2 step 1: idempotency pre-check (AC-9(a))
# ─────────────────────────────────────────────────────────────────────────────
_idempotency_check() {
    local wrapper_dir="${1}"
    local consumer_dir="${2}"

    while IFS= read -r -d '' wrapper_file; do
        local rel_path="${wrapper_file#${wrapper_dir}/}"
        local consumer_file="${consumer_dir}/${rel_path}"
        if [[ ! -f "${consumer_file}" ]]; then
            return 1  # diff found
        fi
        if ! diff -q "${wrapper_file}" "${consumer_file}" > /dev/null 2>&1; then
            return 1  # diff found
        fi
    done < <(find "${wrapper_dir}" -type f \
        ! -name ".wrapper-managed-manifest.json" \
        -print0 2>/dev/null)

    return 0  # identical
}

# ─────────────────────────────────────────────────────────────────────────────
# §4.2 step 2: base 가용성 판정 (orthogonal from marker — §7.4.1(a) FIX Iter 2)
# ─────────────────────────────────────────────────────────────────────────────
_base_state() {
    local snap_dir="${1}"
    local latest_snapshot=""

    if [[ ! -d "${snap_dir}" ]]; then
        echo "BASE_ABSENT"
        return 0
    fi

    local snaps
    snaps=$(ls "${snap_dir}"/*.tar.gz 2>/dev/null | sort -r | head -1 || true)

    if [[ -z "${snaps}" ]]; then
        echo "BASE_ABSENT"
        return 0
    fi

    latest_snapshot="${snaps}"
    if [[ ! -f "${latest_snapshot}" ]]; then
        echo "BASE_ABSENT"
        return 0
    fi

    # Integrity check: validate tarball
    if ! tar tzf "${latest_snapshot}" > /dev/null 2>&1; then
        echo "BASE_CORRUPT:${latest_snapshot}"
        return 0
    fi

    echo "BASE_OK:${latest_snapshot}"
}

# ─────────────────────────────────────────────────────────────────────────────
# Post-reconcile snapshot (FIFO N=5, Story-3 §4 재사용)
# ─────────────────────────────────────────────────────────────────────────────
_create_snapshot() {
    local snap_dir="${1}"
    local overlay_dir="${2}"
    local version="${CODEFORGE_VERSION:-5.78.0}"
    local ts
    ts=$(date -u '+%Y%m%dT%H%M%SZ' 2>/dev/null || date '+%Y%m%dT%H%M%SZ')
    local snap_name="${ts}-${version}.tar.gz"
    local snap_path="${snap_dir}/${snap_name}"

    mkdir -p "${snap_dir}"
    local parent_dir
    parent_dir="$(dirname "${overlay_dir}")"
    local rel_name
    rel_name="$(basename "${overlay_dir}")"

    if (cd "${parent_dir}" && tar czf "${snap_path}" "${rel_name}" 2>/dev/null); then
        echo "${SCRIPT_NAME} snapshot 생성: ${snap_name}"
    else
        echo "${SCRIPT_NAME} 경고: snapshot 생성 실패 (비치명적)" >&2
    fi

    # FIFO N=5 eviction
    local count
    count=$(ls "${snap_dir}"/*.tar.gz 2>/dev/null | wc -l || echo 0)
    if [[ "${count}" -gt "${SNAPSHOT_RETENTION}" ]]; then
        ls "${snap_dir}"/*.tar.gz 2>/dev/null | sort | head -$(( count - SNAPSHOT_RETENTION )) | xargs rm -f 2>/dev/null || true
    fi
}

# ─────────────────────────────────────────────────────────────────────────────
# Per-file reconcile (§4.2 step 3-5: base×marker 2×2 dispatch)
# Returns:
#   0 — OK, no loss
#   1 — FIX_NEEDED (loss occurred, reported)
#   2 — ABORT (malformed marker)
#   3 — INTEGRITY_VIOLATION
# ─────────────────────────────────────────────────────────────────────────────
_reconcile_file() {
    local rel_path="${1}"
    local base_state="${2}"       # BASE_OK | BASE_ABSENT
    local base_snapshot="${3}"    # snapshot tar path (if BASE_OK), else ""
    local dry_run="${4}"          # "true" | "false"

    local consumer_file="${CONSUMER_OVERLAY_DIR}/${rel_path}"
    local wrapper_file="${WRAPPER_SSOT_DIR}/${rel_path}"
    local sidecar_file="${CONSUMER_OVERLAY_DIR}/.wrapper-managed-manifest.json"

    # Determine file marker capability
    local capability
    if [[ -f "${consumer_file}" ]]; then
        capability=$(_file_marker_capability "${consumer_file}")
    else
        # Consumer file doesn't exist — MARKER_NONE (no preservation scope)
        capability="text_marker_none"
    fi

    # ── Step: marker lint for text files (§7.4.1(d) malformed detection) ────
    # Call lint for text_marker_valid (full marker present) OR when orphan marker detected
    # Orphan = BEGIN without END or END without BEGIN → partial marker = malformed
    local _call_lint=false
    if [[ "${capability}" == "text_marker_valid" ]]; then
        _call_lint=true
    elif [[ "${capability}" == "text_marker_none" ]] && [[ -f "${consumer_file}" ]]; then
        # Detect orphan markers (partial pair)
        local _has_begin=false _has_end=false
        _has_marker_begin_sh "${consumer_file}" && _has_begin=true || true
        _has_marker_end_sh "${consumer_file}" && _has_end=true || true
        if "${_has_begin}" || "${_has_end}"; then
            _call_lint=true
        fi
    fi
    if "${_call_lint}"; then
        if ! bash "${MARKER_LINT}" "${consumer_file}" > /dev/null 2>&1; then
            echo "${SCRIPT_NAME} 오류: malformed marker in ${rel_path} — reconcile abort (§7.4.1(d))" >&2
            echo "${SCRIPT_NAME} 힌트: scripts/migrate-existing-customization.sh 로 marker 정정 후 재실행" >&2
            return 2
        fi
    fi

    # ── MARKER_NONE: wholesale_mirror_with_user_visible_loss_report ──────────
    if [[ "${capability}" == "text_marker_none" ]]; then
        local had_consumer_diff=false
        if [[ -f "${consumer_file}" ]] && ! diff -q "${consumer_file}" "${wrapper_file}" > /dev/null 2>&1; then
            had_consumer_diff=true
        fi

        if [[ "${dry_run}" == "false" ]] && [[ -f "${wrapper_file}" ]]; then
            cp "${wrapper_file}" "${consumer_file}"
        elif [[ "${dry_run}" == "true" ]]; then
            echo "${SCRIPT_NAME} [dry-run] MARKER_NONE wholesale: ${rel_path}"
        fi

        if "${had_consumer_diff}"; then
            _add_loss_report "${rel_path}" "MARKER_NONE: consumer customization wholesale overwrite (preservation scope 부재 — ADR-027 §결정 7.C)"
            return 1  # FIX_NEEDED
        fi
        return 0
    fi

    # ── binary: wholesale + loss report (§7.4.1(c)) ─────────────────────────
    if [[ "${capability}" == "binary" ]]; then
        local had_consumer_diff=false
        if [[ -f "${consumer_file}" ]] && ! diff -q "${consumer_file}" "${wrapper_file}" > /dev/null 2>&1; then
            had_consumer_diff=true
        fi

        if [[ "${dry_run}" == "false" ]] && [[ -f "${wrapper_file}" ]]; then
            cp "${wrapper_file}" "${consumer_file}"
        fi

        if "${had_consumer_diff}"; then
            _add_loss_report "${rel_path}" "binary: git merge-file 불가 → wholesale mirror (§7.4.1(c)). consumer binary 변경이 있었을 수 있음"
            return 1
        fi
        return 0
    fi

    # ── JSON marker-incapable: sidecar manifest ──────────────────────────────
    if [[ "${capability}" == "json_incapable" ]]; then
        if [[ ! -f "${sidecar_file}" ]]; then
            # MARKER_NONE for JSON
            local had_consumer_diff=false
            if [[ -f "${consumer_file}" ]] && ! diff -q "${consumer_file}" "${wrapper_file}" > /dev/null 2>&1; then
                had_consumer_diff=true
            fi
            if [[ "${dry_run}" == "false" ]] && [[ -f "${wrapper_file}" ]]; then
                cp "${wrapper_file}" "${consumer_file}"
            fi
            if "${had_consumer_diff}"; then
                _add_loss_report "${rel_path}" "JSON sidecar 부재 (MARKER_NONE): wholesale mirror. consumer customize JSON key 가 있었을 수 있음 (§7.4.1(f))"
                return 1
            fi
            return 0
        fi

        # Validate sidecar schema (ADR-061: external .py, no heredoc — validate_sidecar.py)
        local sidecar_valid=false
        if python3 "${VALIDATE_SIDECAR_PY}" "${sidecar_file}" 2>/dev/null; then
            sidecar_valid=true
        fi

        if ! "${sidecar_valid}"; then
            local had_consumer_diff=false
            if [[ -f "${consumer_file}" ]] && ! diff -q "${consumer_file}" "${wrapper_file}" > /dev/null 2>&1; then
                had_consumer_diff=true
            fi
            if [[ "${dry_run}" == "false" ]] && [[ -f "${wrapper_file}" ]]; then
                cp "${wrapper_file}" "${consumer_file}"
            fi
            if "${had_consumer_diff}"; then
                _add_loss_report "${rel_path}" "JSON sidecar malformed (MARKER_NONE): wholesale mirror (§7.4.1(f))"
                return 1
            fi
            return 0
        fi

        # Sidecar valid — JSON path merge
        if [[ "${dry_run}" == "false" ]]; then
            if [[ -f "${JSON_MERGE_PY}" ]]; then
                python3 "${JSON_MERGE_PY}" \
                    --consumer "${consumer_file}" \
                    --wrapper "${wrapper_file}" \
                    --sidecar "${sidecar_file}" \
                    --output "${consumer_file}" 2>/dev/null || {
                    _add_loss_report "${rel_path}" "JSON sidecar merge 실패: wholesale fallback"
                    cp "${wrapper_file}" "${consumer_file}"
                    return 1
                }
            else
                # No Python helper — wholesale
                _add_loss_report "${rel_path}" "JSON merge helper 부재: wholesale fallback"
                cp "${wrapper_file}" "${consumer_file}"
                return 1
            fi
        else
            echo "${SCRIPT_NAME} [dry-run] JSON sidecar merge preview: ${rel_path}"
        fi
        return 0
    fi

    # ── TEXT file with valid marker: base×marker 2×2 ─────────────────────────
    # capability == "text_marker_valid"

    # Save original for integrity check
    local orig_backup
    orig_backup=$(mktemp)
    if [[ -f "${consumer_file}" ]]; then
        cp "${consumer_file}" "${orig_backup}"
    fi

    local file_result=0

    if [[ "${base_state}" == "BASE_OK" ]] && [[ -n "${base_snapshot}" ]]; then
        # ── BASE_OK + MARKER_VALID: 3-way merge ──────────────────────────────
        local base_tmp
        base_tmp=$(mktemp -d)

        # Extract all from snapshot, then find the file (path-agnostic: supports any tar structure)
        tar xzf "${base_snapshot}" -C "${base_tmp}" 2>/dev/null || true

        # Search for the file by relative path suffix (handles ./, prefix variations)
        local base_file=""
        local _found_path
        _found_path=$(find "${base_tmp}" -type f 2>/dev/null \
            | grep -F "${rel_path}" | head -1 || true)
        if [[ -n "${_found_path}" ]] && [[ -f "${_found_path}" ]]; then
            base_file="${_found_path}"
        fi

        if [[ -n "${base_file}" ]] && [[ -f "${base_file}" ]]; then
            # Extract inside-marker content from each version
            local inside_base inside_wrapper inside_consumer merged_inside
            inside_base=$(mktemp)
            inside_wrapper=$(mktemp)
            inside_consumer=$(mktemp)
            merged_inside=$(mktemp)

            _extract_inside_marker_sh "${base_file}" > "${inside_base}"
            _extract_inside_marker_sh "${wrapper_file}" > "${inside_wrapper}"
            _extract_inside_marker_sh "${consumer_file}" > "${inside_consumer}"

            # 3-way merge inside content
            cp "${inside_consumer}" "${merged_inside}"
            local merge_exit=0
            git merge-file -q "${merged_inside}" "${inside_base}" "${inside_wrapper}" 2>/dev/null || merge_exit=$?

            if [[ "${merge_exit}" -ne 0 ]]; then
                # Conflict: wrapper-new wins + loss report
                _add_loss_report "${rel_path}" "3-way merge conflict: marker 안 wrapper-new 채택, consumer diverge = loss (§7.4.1(b))"
                cp "${inside_wrapper}" "${merged_inside}"
                file_result=1
            fi

            if [[ "${dry_run}" == "false" ]]; then
                _reconstruct_sh "${consumer_file}" "${merged_inside}" "${consumer_file}"

                # Integrity check (AC-9(c))
                local before_fp after_fp
                before_fp=$(_outside_marker_fingerprint_sh "${orig_backup}")
                after_fp=$(_outside_marker_fingerprint_sh "${consumer_file}")
                if [[ "${before_fp}" != "${after_fp}" ]]; then
                    echo "${SCRIPT_NAME} 오류: §7.4.1(g) customization integrity 위반: ${rel_path} marker 밖 byte-diff" >&2
                    cp "${orig_backup}" "${consumer_file}"
                    rm -rf "${base_tmp}" "${inside_base}" "${inside_wrapper}" "${inside_consumer}" "${merged_inside}" "${orig_backup}"
                    return 3
                fi
            else
                echo "${SCRIPT_NAME} [dry-run] 3-way merge: ${rel_path}"
                if [[ "${merge_exit}" -ne 0 ]]; then
                    echo "${SCRIPT_NAME} [dry-run] conflict in ${rel_path}: wrapper-new would win"
                fi
            fi

            rm -f "${inside_base}" "${inside_wrapper}" "${inside_consumer}" "${merged_inside}" 2>/dev/null || true
        else
            # Base file not found in snapshot → fallback to BASE_ABSENT path
            base_state="BASE_ABSENT"
        fi

        rm -rf "${base_tmp}" 2>/dev/null || true
    fi

    if [[ "${base_state}" == "BASE_ABSENT" ]]; then
        # ── BASE_ABSENT + MARKER_VALID: marker-aware 2-way first-reconcile ───
        local inside_wrapper inside_consumer
        inside_wrapper=$(mktemp)
        inside_consumer=$(mktemp)

        _extract_inside_marker_sh "${wrapper_file}" > "${inside_wrapper}"
        _extract_inside_marker_sh "${consumer_file}" > "${inside_consumer}"

        local had_inside_diff=false
        if ! diff -q "${inside_consumer}" "${inside_wrapper}" > /dev/null 2>&1; then
            had_inside_diff=true
        fi

        if [[ "${dry_run}" == "false" ]]; then
            # marker-밖 = consumer preserve (base 불요), marker-안 = wrapper-new
            _reconstruct_sh "${consumer_file}" "${inside_wrapper}" "${consumer_file}"

            # Integrity check (AC-9(c))
            local before_fp after_fp
            before_fp=$(_outside_marker_fingerprint_sh "${orig_backup}")
            after_fp=$(_outside_marker_fingerprint_sh "${consumer_file}")
            if [[ "${before_fp}" != "${after_fp}" ]]; then
                echo "${SCRIPT_NAME} 오류: §7.4.1(g) customization integrity 위반: ${rel_path} marker 밖 byte-diff (BASE_ABSENT)" >&2
                cp "${orig_backup}" "${consumer_file}"
                rm -f "${inside_wrapper}" "${inside_consumer}" "${orig_backup}"
                return 3
            fi
        else
            echo "${SCRIPT_NAME} [dry-run] marker-aware 2-way (first reconcile): ${rel_path}"
        fi

        # Note: BASE_ABSENT + MARKER_VALID = first reconcile.
        # Inside-marker content belongs to wrapper (preservation scope = marker 밖 only).
        # Mirroring wrapper inside is NOT a consumer loss → no loss report here.
        # had_inside_diff is informational only (reconcile protocol §4.2 step 4 first-reconcile).

        rm -f "${inside_wrapper}" "${inside_consumer}" 2>/dev/null || true
    fi

    rm -f "${orig_backup}" 2>/dev/null || true
    return "${file_result}"
}

# ─────────────────────────────────────────────────────────────────────────────
# Main execution
# ─────────────────────────────────────────────────────────────────────────────
DRY_RUN="false"
if [[ "${MODE}" == "dry-run" ]]; then
    DRY_RUN="true"
    echo "${SCRIPT_NAME} [dry-run] mode: filesystem touch 0"
fi

echo "${SCRIPT_NAME} overlay 영역 reconcile 시작 (mode: ${MODE})"

# §4.2 step 1: idempotency pre-check (AC-9(a))
if _idempotency_check "${WRAPPER_SSOT_DIR}" "${CONSUMER_OVERLAY_DIR}"; then
    echo "${SCRIPT_NAME} overlay 이미 wrapper SSOT 와 일치 — no-op 정상 종료 (AC-9(a))"
    exit 0
fi

# §4.2 step 2: base 가용성 판정 (orthogonal from marker)
BASE_RESULT=$(_base_state "${SNAPSHOT_DIR}")
BASE_KIND="${BASE_RESULT%%:*}"
BASE_SNAPSHOT_PATH="${BASE_RESULT#*:}"
# Normalize: if no colon (BASE_ABSENT), BASE_SNAPSHOT_PATH == BASE_RESULT which is wrong
if [[ "${BASE_KIND}" == "${BASE_SNAPSHOT_PATH}" ]]; then
    BASE_SNAPSHOT_PATH=""
fi

if [[ "${BASE_KIND}" == "BASE_CORRUPT" ]]; then
    echo "${SCRIPT_NAME} 오류: snapshot corrupt — abort-before-touch (§7.4.1(a))" >&2
    echo "${SCRIPT_NAME} corrupt snapshot: ${BASE_SNAPSHOT_PATH}" >&2
    echo "${SCRIPT_NAME} 수동 복구 필요: ${SNAPSHOT_DIR} 의 손상된 snapshot 파일을 삭제 후 재실행" >&2
    exit 1
fi

echo "${SCRIPT_NAME} base 상태: ${BASE_KIND}"
if [[ "${BASE_KIND}" == "BASE_OK" ]]; then
    echo "${SCRIPT_NAME} base snapshot: $(basename "${BASE_SNAPSHOT_PATH}")"
fi

# §4.2 step 3-5: per-file dispatch
OVERALL_EXIT=0
ABORT_DETECTED=false

while IFS= read -r -d '' wrapper_file; do
    rel_path="${wrapper_file#${WRAPPER_SSOT_DIR}/}"

    # Skip sidecar manifest itself
    if [[ "${rel_path}" == ".wrapper-managed-manifest.json" ]]; then
        continue
    fi

    # Ensure consumer directory exists (--apply only)
    if [[ "${DRY_RUN}" == "false" ]]; then
        local_dir=$(dirname "${CONSUMER_OVERLAY_DIR}/${rel_path}")
        mkdir -p "${local_dir}"
    fi

    file_exit=0
    _reconcile_file "${rel_path}" "${BASE_KIND}" "${BASE_SNAPSHOT_PATH}" "${DRY_RUN}" || file_exit=$?

    case "${file_exit}" in
        0) ;;
        1) OVERALL_EXIT=1 ;;
        2) ABORT_DETECTED=true; OVERALL_EXIT=1 ;;
        3) ABORT_DETECTED=true; OVERALL_EXIT=1 ;;
    esac

    if "${ABORT_DETECTED}"; then
        echo "${SCRIPT_NAME} abort: reconcile 중단" >&2
        break
    fi
done < <(find "${WRAPPER_SSOT_DIR}" -type f -print0 2>/dev/null)

# §4.2 step 6+7: post-reconcile snapshot
if [[ "${DRY_RUN}" == "false" ]] && ! "${ABORT_DETECTED}"; then
    _create_snapshot "${SNAPSHOT_DIR}" "${CONSUMER_OVERLAY_DIR}"
fi

# Loss report (EPIC-AC-4 surfacing)
_print_loss_report

if [[ "${OVERALL_EXIT}" -eq 0 ]]; then
    echo "${SCRIPT_NAME} overlay reconcile 완료 (loss 0)"
else
    if ! "${ABORT_DETECTED}"; then
        echo "${SCRIPT_NAME} overlay reconcile 완료 (loss 발생 — LOSS REPORT 확인)" >&2
    fi
fi

exit "${OVERALL_EXIT}"
