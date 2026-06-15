#!/usr/bin/env bash
# bootstrap-labels.sh — Plugin이 사용하는 GitHub label 55종 + hotfix-bypass:* yaml dynamic 일괄 생성 (1회).
# CFP-1306: hotfix-bypass:parallel-anchors-checked-presence 92번째 family member dynamic pick-up (label-registry-v2 v2.66 → v2.67 / ADR-060 Amendment 15 §결정 29 / ADR-024 Amendment 14 §결정 6.A.7 carrier — parallel_anchors_checked presence lint Wave 3 mechanical enforcement bypass channel, late-comer rebase: CFP-1367 90+91번째 먼저 머지됨 → v2.67). bootstrap-labels.sh body 변경 0 (CFP-598 dynamic registry-driven pattern via parse-hotfix-bypass-labels.py — registry yaml entry append 시 자동 pick-up).
# CFP-1429 (Sub-C S3.5 of Mega-Epic CFP-1415): hotfix-bypass:living-architecture-update 84번째 family member dynamic pick-up (label-registry-v2 v2.58 → v2.59 / ADR-112 carrier — Living Architecture per-Epic mandatory update gate mechanical wire). bootstrap-labels.sh body 변경 0 (CFP-598 dynamic registry-driven pattern via parse-hotfix-bypass-labels.py — registry yaml entry append 시 자동 pick-up).
# CFP-1059: Deploy lane + Deploy Review lane + Schema 7 원칙 + Cross-layer 정책 신설 (46 → 55 hardcoded base + 7 hotfix-bypass:* dynamic, label-registry-v2 v2.41 → v2.42 / ADR-087 + ADR-088 + ADR-089 + ADR-090 carrier).
# CFP-954: production-touching label 정식 추가 (41 → 42종, label-registry-v2 v2.33 → v2.34 정합 — CFP-949 v2.33 collision rebase ratchet, dual-carrier: CFP-949 5 entry 보존 + CFP-954 production-touching append).
#
# CFP-11 end-to-end 실증에서 발견된 bootstrap drift — 신규 repo에 plugin 적용 시
# type:* / phase:* / gate:* / fix:* / hotfix:* / audit:* 라벨 부재로 Issue Form
# 제출 자체가 실패한다.
#
# 본 스크립트는 idempotent — 기존 라벨은 "already exists" 메시지 후 통과.
#
# Usage:
#   gh auth login   # 사전 인증 필요
#   bash scripts/bootstrap-labels.sh                # 현재 repo
#   bash scripts/bootstrap-labels.sh org/repo       # 명시 repo
#   bash scripts/bootstrap-labels.sh --dry-run      # 라벨 목록만 stdout 출력 (gh 미호출, CFP-33 lint 용)
#
# Exit code: 0 (모두 처리, 일부 already-exists 포함) / 1 (gh 미설치 또는 인증 실패)

set -u

DRY_RUN=0
REPO_ARG=""
if [ $# -ge 1 ]; then
    if [ "$1" = "--dry-run" ]; then
        DRY_RUN=1
    else
        REPO_ARG="--repo $1"
    fi
fi

# CFP-492 2-way self-check: create_label 호출 횟수 카운터.
# DRY_RUN 모드 시 stderr 로 "create_label invocations: N" 출력 → check-bootstrap-labels-count.sh 가 cross-verify.
LABEL_COUNT=0

if [ $DRY_RUN -eq 0 ] && ! command -v gh >/dev/null 2>&1; then
    echo "ERROR: gh CLI 미설치. https://cli.github.com 에서 설치 후 'gh auth login' 실행." >&2
    exit 1
fi

# Idempotent label create — 이미 존재하면 0 반환 (silent).
# --dry-run 모드: gh 미호출, "name|color|desc" tab-separated 출력 → CFP-33 check-label-registry.sh 가 parse.
# CFP-492: LABEL_COUNT 증가 (DRY_RUN/non-DRY_RUN 모두) — 2-way self-check 용.
create_label() {
    local name="$1"
    local color="$2"
    local desc="$3"
    LABEL_COUNT=$((LABEL_COUNT + 1))
    if [ $DRY_RUN -eq 1 ]; then
        printf '%s\t%s\t%s\n' "$name" "$color" "$desc"
        return 0
    fi
    # shellcheck disable=SC2086
    # CFP-1025 (ADR-024 Amendment 12) — error-unmask. 이전 `2>/dev/null` 가 실제 gh HTTP
    # error (403/404 — 예: workflow token 이 Issues:write 미보유) 를 삼켜 generic 메시지 +
    # 오인성 "Bootstrap completed successfully" 를 만들었다 (CFP-1006 Wave-1 mis-diagnosis 직접 원인).
    # 이제 captured stderr 를 terminal-failure 시 verbatim echo → masked false-success 재발 차단.
    # control flow (create || edit || fail-echo) + exit semantics 불변. --dry-run path (위)
    # 무영향 → LABEL_COUNT 2-way self-check parity 보존 (check-bootstrap-labels-count.sh).
    local _create_err _edit_err
    if _create_err=$(gh label create "$name" --color "$color" --description "$desc" $REPO_ARG 2>&1); then
        return 0
    fi
    if _edit_err=$(gh label edit "$name" --color "$color" --description "$desc" $REPO_ARG 2>&1); then
        return 0
    fi
    # already-exists 는 create 실패 + edit 성공으로 위에서 return 0 처리됨 (멱등 보존).
    # 여기 도달 = create AND edit 모두 실패 = 진짜 실패 (권한/네트워크/API).
    local _gh_err="${_edit_err:-$_create_err}"
    _gh_err=$(printf '%s' "$_gh_err" | tr '\n' ' ' | sed 's/  */ /g;s/^ *//;s/ *$//')
    echo "  ! $name: create/edit 실패 — ${_gh_err:-(gh stderr 비어있음 — 권한/네트워크 점검)}"
}

[ $DRY_RUN -eq 0 ] && echo "Plugin label 부트스트랩..."

# base label SSOT — templates/labels/base-labels.tsv (CFP-2250 / ADR-027 Amendment 11).
# 기존 hardcoded create_label 블록을 TSV read 로 전환 — .sh ↔ .ps1 (bootstrap-labels.ps1) 공유 SSOT.
# 형식: name<TAB>color<TAB>desc. 빈 줄 / # 시작 줄 = skip. 순서 = TSV 등재 순서 보존 (dry-run 출력 + check-label-registry.sh cross-verify 불변).
# provenance (CFP 번호 / ADR 근거) = label-registry-v2.md SSOT — TSV 는 데이터 평면화.
# type:epic/story/bug = native GitHub Issue Type (ADR-049) — 미생성 (impl-manifest 만 type axis 잔존, TSV 1행).
BASE_LABELS_TSV="${BASE_LABELS_TSV:-${_BOOTSTRAP_SCRIPT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)}/../templates/labels/base-labels.tsv}"
if [ ! -f "$BASE_LABELS_TSV" ]; then
    echo "ERROR: base label TSV 부재 — $BASE_LABELS_TSV" >&2
    exit 1
fi
while IFS=$'\t' read -r name color desc; do
    # skip 빈 줄 + # 주석 줄
    case "$name" in ''|'#'*) continue ;; esac
    create_label "$name" "$color" "$desc"
done < "$BASE_LABELS_TSV"

# hotfix-bypass:* — full set via dynamic read (CFP-598 below).
# CFP-610 / ADR-064 Amendment 2 — wording-dictionary entry now sourced from §3 yaml dynamic read (NOT hardcoded here).
# CFP-619 — pre-existing CFP-610 leak resolution: prior hardcoded `create_label "hotfix-bypass:wording-dictionary"` removed
#           (duplicate creation 발생 — dynamic read 가 yaml row 처리 + 본 hardcoded 라인 = 2 invocations, 3-way self-check FAIL).
#           DRY status restored: hardcoded 0 + yaml row 1 = single source of truth via dynamic parse only.
# 주: monitoring:* (codeforge-kpi-*) + operational-signal:* (ops-signal) base label 은 CFP-2250 에서 base-labels.tsv 로 이관 (위 TSV read 블록 처리).

# hotfix-bypass:* (CFP-598) — label-registry-v2.md §3 yaml dynamic read.
# canonical-only category (component:* 와 달리 consumer overlay 아님) — DRY_RUN + actual 양 모드 모두 처리.
_BOOTSTRAP_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REGISTRY_MD="${REGISTRY_MD:-${_BOOTSTRAP_SCRIPT_DIR}/../docs/inter-plugin-contracts/label-registry-v2.md}"
if [ -f "$REGISTRY_MD" ]; then
    if ! python -c "import yaml" 2>/dev/null; then
        echo "  ! hotfix-bypass:* labels SKIPPED — Python PyYAML 미설치 ('pip install pyyaml' 후 재실행 권장)." >&2
    else
        hotfix_bypass=$(python "${_BOOTSTRAP_SCRIPT_DIR}/parse-hotfix-bypass-labels.py" "$REGISTRY_MD" 2>/dev/null) || {
            rc=$?
            if [ $rc -eq 2 ]; then
                echo "  ! hotfix-bypass:* SKIPPED — registry 안 0 entry (drift sentinel)." >&2
            else
                echo "  ! hotfix-bypass:* SKIPPED — parse failure (exit $rc)." >&2
            fi
            hotfix_bypass=""
        }
        if [ -n "$hotfix_bypass" ]; then
            # process substitution (<(...)) — subshell 회피로 LABEL_COUNT 부모 shell 증분 보장
            # (pipe | while read 는 subshell → LABEL_COUNT 부모 미전파 — 2-way self-check parity 파괴)
            while IFS=$'\t' read -r name color desc; do
                [ -z "$name" ] && continue
                create_label "$name" "$color" "$desc"
            done < <(printf '%s\n' "$hotfix_bypass")
        fi
    fi
fi

# component:* (CFP-131 / Issue #237) — project.yaml `labels.components[]` 에서 동적 read.
# placeholder ("<REPLACE...") 항목 skip. Python + PyYAML 의존 (codeforge family 표준).
# --dry-run 모드 에서는 skip — component:* 는 consumer overlay 동적 (CFP-33 check-label-registry
# strict sync 와 충돌 회피). 실제 gh 호출 시에만 component:* 생성.
PROJECT_YAML="${PROJECT_YAML:-.claude/_overlay/project.yaml}"
if [ $DRY_RUN -eq 0 ] && [ -f "$PROJECT_YAML" ]; then
    # PyYAML preflight — 부재 시 명시적 warning (silent skip 금지, Codex P1 권고)
    if ! python -c "import yaml" 2>/dev/null; then
        echo "  ! component:* labels SKIPPED — Python PyYAML 미설치 ('pip install pyyaml' 후 재실행 권장). 29 base label 만 처리됨." >&2
    else
        # path 를 argv 로 안전 전달 (shell quoting 회피, Codex P1 권고)
        components=$(python -c "
import sys, yaml
try:
    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        d = yaml.safe_load(f) or {}
    for c in (d.get('labels', {}) or {}).get('components', []) or []:
        if isinstance(c, str) and not c.startswith('<REPLACE'):
            print(c)
except Exception as e:
    print(f'PARSE_ERROR: {e}', file=sys.stderr)
    sys.exit(1)
" "$PROJECT_YAML" 2>/dev/null) || components=""

        if [ -n "$components" ]; then
            # printf 로 안전 iterate (echo $var 회피, Codex P1 권고)
            printf '%s\n' "$components" | while IFS= read -r c; do
                [ -z "$c" ] && continue
                create_label "component:$c" "ededed" "Component: $c"
            done
        fi
    fi
fi

if [ $DRY_RUN -eq 0 ]; then
    echo ""
    # CFP-2250: base label count = TSV 데이터 행 (빈 줄 / # 주석 제외) — hardcode 수치 stale 방지.
    _base_count="$(grep -cve '^\s*#' -e '^\s*$' "$BASE_LABELS_TSV" 2>/dev/null || echo '?')"
    echo "✓ ${_base_count} base label (templates/labels/base-labels.tsv) + hotfix-bypass:* (registry 동적) + component:* (project.yaml.labels.components[] 동적) 처리 완료. 'gh label list' 로 확인."
fi

# CFP-492 2-way self-check (DRY_RUN 모드에서만):
# dry-run stdout 의 line count 는 caller 가 wc -l 로 확인 가능.
# 본 script 는 stderr 로 LABEL_COUNT 출력 → check-bootstrap-labels-count.sh 가 cross-verify.
# 잠재적 drift: 신규 label 추가 시 create_label invocation 추가했으나 dry-run 출력 line count 와 mismatch 발생 가능.
if [ $DRY_RUN -eq 1 ]; then
    echo "[bootstrap-labels self-check] create_label invocations: $LABEL_COUNT" >&2
fi
