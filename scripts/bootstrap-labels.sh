#!/usr/bin/env bash
# bootstrap-labels.sh — Plugin이 사용하는 GitHub label 33종 일괄 생성 (1회).
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

if [ $DRY_RUN -eq 0 ] && ! command -v gh >/dev/null 2>&1; then
    echo "ERROR: gh CLI 미설치. https://cli.github.com 에서 설치 후 'gh auth login' 실행." >&2
    exit 1
fi

# Idempotent label create — 이미 존재하면 0 반환 (silent).
# --dry-run 모드: gh 미호출, "name|color|desc" tab-separated 출력 → CFP-33 check-label-registry.sh 가 parse.
create_label() {
    local name="$1"
    local color="$2"
    local desc="$3"
    if [ $DRY_RUN -eq 1 ]; then
        printf '%s\t%s\t%s\n' "$name" "$color" "$desc"
        return 0
    fi
    # shellcheck disable=SC2086
    gh label create "$name" --color "$color" --description "$desc" $REPO_ARG 2>/dev/null \
        || gh label edit "$name" --color "$color" --description "$desc" $REPO_ARG 2>/dev/null \
        || echo "  ! $name: create/edit 실패 (권한 문제 가능)"
}

[ $DRY_RUN -eq 0 ] && echo "Plugin label 부트스트랩..."

# type:* — CFP-140 / ADR-049: label hack deprecated, replaced by native GitHub Issue Types
# type:epic / type:story / type:bug → native Issue Types (org-level, see templates/issue-types.yaml)
# See: label-registry-v2.md (Active) supersedes label-registry-v1.md (Archived)
# impl-manifest = separate axis (retained — sub-issue visual marker)
create_label "impl-manifest"    "fbca04" "Sub-issue (Impl Manifest 파일 단위)"

# phase:* (7종, single-active)
for p in 요구사항 설계 설계-리뷰 구현 구현-리뷰 구현-테스트 보안-테스트; do
    create_label "phase:$p" "1d76db" "Phase: $p"
done

# phase:reservation (v1.4 / CFP-260 / ADR-036) — atomic key reservation Issue 의 임시 phase
create_label "phase:reservation" "ededed" "Phase: reservation (CFP-260 / ADR-036 — brainstorming KEY 사전 확보, 30 일 미진행 시 자동 close)"

# gate:* (3종) — gate:live-entry-pass added v1.3 (CFP-123 / ADR-030)
create_label "gate:design-review-pass"   "0e8a16" "Design review PASS"
create_label "gate:security-test-pass"   "0e8a16" "Security test PASS"
create_label "gate:live-entry-pass"      "0e8a16" "Live Epic lane-entry pass (3-condition AND: mode==live + --confirm-live + isolated runtime)"
# gate:retro-complete (v1.5 / CFP-138 / ADR-045) — Story 완료 회고 작성 mandate forcing function
create_label "gate:retro-complete"       "0e8a16" "Story 완료 회고 작성됨 (PMOAgent self-write — CFP-138 / ADR-045). 미부착 시 retro-mandatory.yml 가 close 차단."

# fix:* (4종)
for r in 설계-리뷰 구현-리뷰 구현-테스트 보안-테스트; do
    create_label "fix:$r-retry" "e99695" "FIX retry: $r"
done

# hotfix / audit (3종)
create_label "hotfix:minimal"     "ff9999" "Hotfix minimal"
create_label "hotfix:critical"    "ff0000" "Hotfix critical"
create_label "audit:post-hotfix"  "fef2c0" "Post-hotfix audit Story"

# debut audit (2종, source) + category (7종, mutually exclusive) — CFP-60 / debut-audit-triage-v1
# 색상 = label-registry-v1.md SSOT
create_label "audit:debut-eval"            "fbca04" "데뷔 평가 (consumer 첫 사용 사례) 발견 사항"
create_label "audit:from-mctrader-debut"   "fef2c0" "mctrader 데뷔 평가에서 발견된 codeforge gap (첫 사례)"
# CFP-429: from-cfp-425-followup (Epic CFP-425 gate FAIL 분기 후속 carrier provenance marker, label-registry-v2 v2.5)
create_label "from-cfp-425-followup"       "fbca04" "Epic CFP-425 (worktree-first mechanical enforcement 영구화) gate FAIL 분기 후속 carrier marker"
# CFP-88: audit:spec-amendment (CFP-87 / playbook §6.8 follow-up, label-registry v1.2)
create_label "audit:spec-amendment"        "fbca04" "Mid-implementation spec doc 수정 PR (Codex push-back / 사용자 mid-impl clarification / spec drift 발견 시)"
# CFP-90: early-close:* (CFP-85 / phase-invariant terminal state follow-up, label-registry v1.2)
create_label "early-close:duplicate"       "d4c5f9" "다른 Story 와 중복 — early-close 정당화"
create_label "early-close:reclassified"    "d4c5f9" "Out-of-scope 재분류 — 다른 Epic / 별도 Story 로 이전"
create_label "early-close:epic-rolled-up"  "d4c5f9" "Epic 종료 시 child Story 일괄 close — Epic close PR 가 absorbing"
create_label "category:lane-progression"   "0e8a16" "#1 — 7 lane 통과 / 막힘 (owner: PMOAgent)"
create_label "category:agent-gap"          "d93f0b" "#2 — phase 별 gap + 과부하 (owner: ArchitectPL, ADR-021 R1-R4)"
create_label "category:decision-table"     "1d76db" "#3 — 원인 판정 row 모호 / 신규 (owner: wrapper Orchestrator)"
create_label "category:deputy-mandate"     "5319e7" "#4 — 6 deputy mandate 부족 (owner: ArchitectPL)"
create_label "category:workflow-invariant" "bfd4f2" "#5 — GitHub Actions 강제 누락 (owner: wrapper Orchestrator)"
create_label "category:template"           "c5def5" "#6 — Story / Change Plan / ADR 필드 부족 (owner: per-template)"
create_label "category:contract-schema"    "bfdadc" "#7 — inter-plugin contract schema 부족 (owner: producer lane plugin)"

# conflict:* + merge-order:* (5종 — 병렬 에픽 충돌 조율, ADR-050 / CFP-344)
create_label "conflict:file-overlap"   "e4e669" "다른 open PR과 변경 파일 중복 (parallel-epic-conflict-check.yml 자동 감지)"
create_label "conflict:adr-number"     "e4e669" "ADR-RESERVATION.md 동시 수정 감지 — ADR 번호 충돌 위험"
create_label "conflict:section-locked" "d93f0b" "section-ownership.yaml locked 섹션 동시 수정 감지 — merge 순서 조율 필요"
create_label "merge-order:1"           "0075ca" "병렬 에픽 충돌 시 먼저 merge해야 하는 PR (낮은 CFP 번호)"
create_label "merge-order:2"           "e4e669" "병렬 에픽 충돌 시 merge-order:1 완료 후 git rebase main 의무"

# monitoring:* (3종 — CFP-451 v2.3 sub-axis 다축 완결 / CFP-393 v2.2 신설 tier, ADR-057 Amendment 2 / ADR-060)
# KPI / metric / dashboard / alert 영역. 기존 `audit` (후처리 분류) 와 분리.
# sub-axis: info (kpi-update) / warn (kpi-alert) / error (kpi-infra-error).
# rate-limit-fallback-kpi.yml workflow 가 자동 부착.
create_label "codeforge-kpi-alert"        "f29513" "codeforge KPI threshold violation alert (CFP-393 ADR-057 fallback rate KPI dashboard). rate-limit-fallback-kpi.yml workflow 가 sample_size_sufficient=true AND fallback_rate_percent >= 1.0% 시 Issue auto-open. ADR-060 evidence-enforceable framework 첫 non-sunset application."
create_label "codeforge-kpi-infra-error"  "d73a4a" "KPI workflow infrastructure failure — oncall investigation required. rate-limit-fallback-kpi.yml workflow 가 clone fail / aggregator script error / auto-PR fail detect 시 Issue auto-open. measurement alert (codeforge-kpi-alert) 와 분리된 channel — audience routing (oncall vs 정책 의사결정자). CFP-451 v2.3 sub-axis 다축 완결."
create_label "codeforge-kpi-update"       "0e8a16" "KPI workflow data refresh PR — auto-merge eligible. rate-limit-fallback-kpi.yml workflow 가 monthly cron 으로 발의하는 docs/kpi/rate-limit-fallback.json 데이터 갱신 PR marker. CFP-451 v2.3 sub-axis 다축 완결 (pre-existing CFP-393 leak 정정 — Codex F-451-001 (a))."

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
    echo "✓ 33 base label + component:* (project.yaml.labels.components[] 동적) 처리 완료. 'gh label list' 로 확인."
fi
