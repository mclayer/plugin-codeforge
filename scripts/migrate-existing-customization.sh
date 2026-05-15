#!/usr/bin/env bash
# CFP-702 / ADR-027 Amendment 3 §결정 7.E — retroactive marker wrap migration
# mctrader 5 repo (mclayer/mctrader-{market,market-bithumb,data,engine,web}) idempotent migration
#
# 목적: marker-부재 consumer 의 wrapper SSOT mirror 영역에 D4 marker block 을 삽입
#
# Idempotency invariant (§결정 7.E):
#   N회 실행 = 1회 effect — 이미 wrap 된 영역 재wrap 0
#   2차 실행 = file hash 동일 (Ansible blockinfile 동형)
#
# False-positive boundary (§결정 7.E.1 Axis 3):
#   wrap 대상 = byte-diff 0 (wrapper SSOT template 과 동일) + consumer-scripts.manifest 등재 영역만
#   consumer customize 영역 (byte-diff ≠ 0) = marker 밖 보존 (false-positive 0)
#
# Partial-state resume (§8.5 restart invariant):
#   중단 후 재실행 = partial wrap 영역 skip + 미wrap 영역만 처리 (resume-safe)
#
# Usage:
#   bash migrate-existing-customization.sh [--dry-run] [--repo-root <path>] [--plugin-root <path>]
#
# Options:
#   --dry-run       파일 변경 0, preview 출력만 (결정 분기 아님 — reconcile-protocol-v1 §4.3 정합)
#   --repo-root     consumer repo 루트 (기본: 현재 디렉토리)
#   --plugin-root   wrapper plugin 루트 (기본: 스크립트 위치 2단계 상위)
#
# Exit code (ADR-060 §결정 15 3-tier):
#   0 — PASS (정상 완료 또는 dry-run 완료)
#   1 — migration 오류
#   2 — setup error (필수 파일 부재 등)
set -euo pipefail

SCRIPT_NAME="[migrate-existing-customization]"

# ── 인수 파싱 ────────────────────────────────────────────────────────────────
DRY_RUN=false
REPO_ROOT=""
PLUGIN_ROOT=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run)
      DRY_RUN=true
      shift
      ;;
    --repo-root)
      REPO_ROOT="$2"
      shift 2
      ;;
    --plugin-root)
      PLUGIN_ROOT="$2"
      shift 2
      ;;
    *)
      echo "$SCRIPT_NAME ERROR: 알 수 없는 인수: $1" >&2
      exit 2
      ;;
  esac
done

# ── 기본 경로 설정 ────────────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ -z "$PLUGIN_ROOT" ]]; then
  PLUGIN_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
fi
if [[ -z "$REPO_ROOT" ]]; then
  REPO_ROOT="$(pwd)"
fi

readonly MANIFEST="$PLUGIN_ROOT/templates/consumer-scripts.manifest"
readonly DRY_RUN

# ── manifest 존재 확인 ────────────────────────────────────────────────────────
if [[ ! -f "$MANIFEST" ]]; then
  echo "$SCRIPT_NAME ERROR: consumer-scripts.manifest 없음: $MANIFEST" >&2
  exit 2
fi

echo "$SCRIPT_NAME INFO: plugin-root=$PLUGIN_ROOT, repo-root=$REPO_ROOT, dry-run=$DRY_RUN" >&2

# ── marker 삽입 함수 ──────────────────────────────────────────────────────────
get_begin_marker() {
  local file="$1"
  case "${file##*.}" in
    yml|yaml|sh) echo "# BEGIN wrapper-managed" ;;
    md)          echo "<!-- BEGIN wrapper-managed -->" ;;
    *)           echo "# BEGIN wrapper-managed" ;;
  esac
}

get_end_marker() {
  local file="$1"
  case "${file##*.}" in
    yml|yaml|sh) echo "# END wrapper-managed" ;;
    md)          echo "<!-- END wrapper-managed -->" ;;
    *)           echo "# END wrapper-managed" ;;
  esac
}

# ── idempotency 검사: 이미 wrap 됐는가? ──────────────────────────────────────
is_already_wrapped() {
  local consumer_file="$1"
  local begin_marker="$2"
  if grep -qF "$begin_marker" "$consumer_file" 2>/dev/null; then
    return 0  # already wrapped
  fi
  return 1  # not wrapped
}

# ── byte-diff 0 검사: wrapper template 과 동일한가? ──────────────────────────
is_byte_identical() {
  local consumer_file="$1"
  local template_file="$2"
  if [[ ! -f "$template_file" ]]; then
    return 1  # template 없음 = byte-diff 확인 불가 → conservative skip
  fi
  if diff -q "$template_file" "$consumer_file" &>/dev/null; then
    return 0  # byte-identical
  fi
  return 1  # differs (consumer 가 customize 했거나 다름)
}

# ── 단일 파일에 marker 삽입 ───────────────────────────────────────────────────
wrap_file() {
  local consumer_file="$1"
  local begin_marker="$2"
  local end_marker="$3"

  if [[ "$DRY_RUN" == "true" ]]; then
    echo "$SCRIPT_NAME DRY-RUN: $consumer_file — marker 삽입 예정 (BEGIN: $begin_marker)" >&2
    return 0
  fi

  # 임시 파일에 wrapping 후 atomic 교체
  local tmp_file
  tmp_file="$(mktemp)"
  {
    echo "$begin_marker"
    cat "$consumer_file"
    echo "$end_marker"
  } > "$tmp_file"

  mv "$tmp_file" "$consumer_file"
  echo "$SCRIPT_NAME WRAPPED: $consumer_file" >&2
}

# ── manifest 파싱 + migration 실행 ───────────────────────────────────────────
process_manifest() {
  local wrapped=0
  local skipped_idempotent=0
  local skipped_modified=0
  local skipped_missing=0

  while IFS= read -r line || [[ -n "$line" ]]; do
    # 빈 줄 / 주석 skip
    [[ -z "$line" || "${line:0:1}" == "#" ]] && continue

    # <script-path>[:<workflow-path>] 파싱
    local script_path
    script_path="${line%%:*}"
    [[ -z "$script_path" ]] && continue

    # JSON 파일 = sidecar manifest 전용 (본 script 대상 외)
    if [[ "${script_path##*.}" == "json" ]]; then
      continue
    fi

    # consumer 파일 경로
    local consumer_file="$REPO_ROOT/$script_path"
    # plugin template 경로 (manifest entry = plugin-root-relative, bootstrap-consumer.sh §335 1:1 mirror)
    local template_file="$PLUGIN_ROOT/$script_path"

    # consumer 파일 없으면 skip
    if [[ ! -f "$consumer_file" ]]; then
      echo "$SCRIPT_NAME SKIP (no consumer file): $consumer_file" >&2
      ((skipped_missing++)) || true
      continue
    fi

    local begin_marker end_marker
    begin_marker="$(get_begin_marker "$script_path")"
    end_marker="$(get_end_marker "$script_path")"

    # ── idempotency check: 이미 wrap 됐으면 skip ──────────────────────────
    if is_already_wrapped "$consumer_file" "$begin_marker"; then
      echo "$SCRIPT_NAME SKIP (already wrapped): $consumer_file" >&2
      ((skipped_idempotent++)) || true
      continue
    fi

    # ── false-positive boundary: byte-diff 0 + manifest 등재 영역만 wrap ──
    if ! is_byte_identical "$consumer_file" "$template_file"; then
      echo "$SCRIPT_NAME SKIP (consumer modified — byte-diff ≠ 0): $consumer_file" >&2
      ((skipped_modified++)) || true
      continue
    fi

    # ── wrap 실행 ────────────────────────────────────────────────────────────
    wrap_file "$consumer_file" "$begin_marker" "$end_marker"
    ((wrapped++)) || true

  done < "$MANIFEST"

  # ── 결과 리포트 ──────────────────────────────────────────────────────────
  echo "$SCRIPT_NAME SUMMARY:" >&2
  echo "  wrapped:           $wrapped" >&2
  echo "  skipped_idempotent: $skipped_idempotent (already wrapped — idempotency OK)" >&2
  echo "  skipped_modified:  $skipped_modified (consumer customized — false-positive 0 invariant 준수)" >&2
  echo "  skipped_missing:   $skipped_missing (consumer 파일 없음)" >&2

  if [[ "$DRY_RUN" == "true" ]]; then
    echo "$SCRIPT_NAME DRY-RUN complete — filesystem 변경 0 (reconcile-protocol-v1 §4.3 정합)" >&2
  else
    echo "$SCRIPT_NAME migration complete" >&2
  fi
}

# ── 메인 ─────────────────────────────────────────────────────────────────────
main() {
  echo "$SCRIPT_NAME START (D4 retroactive marker wrap migration — CFP-702 / ADR-027 Amendment 3 §결정 7.E)" >&2
  process_manifest
  exit 0
}

main
