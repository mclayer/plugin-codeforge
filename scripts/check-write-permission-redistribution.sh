#!/usr/bin/env bash
# CFP-26 Phase 0a invariant (ADR write-path 축) + CFP-2661 D10 corpus-wide ADR-path union + dead-root fail-closed
#
# 검사 [CFP-2661 D10 — corpus-wide, 열거형 아님]:
#   어떤 agent md frontmatter 도 ADR write-path 권한(Edit/Write(docs/adr/**))을 allow·deny 어느 block 에서든
#   archive/adr union 없이 docs/adr 단독으로 선언하지 않는다. ADR 실 위치 = archive/adr (PR #1973 이동) 이므로
#   docs/adr 단독 = dead-path 재분배 (allow=권한 dead / deny=차단 gap). union 의무 (삭제형 금지 — consumer
#   정답 경로 docs/adr 보존). block(allow/deny) 단위 검사 = construct-level (AC-7 양방향 mutation-kill).
#
# CFP-2661 D10 census (AC-6): scanned agent md 수 + adr_perm_agents(docs/adr 선언 agent, allow∪deny) emit.
#   dead-root(plugins/*/agents/*.md 0건) = 스캔 대상 부재 → skip 아니라 fail-closed(exit≠0). 구판은
#   `agents/` root(모노레포 이후 부재) 가드로 4 assert 전량 silent skip + `✓ OK` + exit 0 (vacuous-PASS)였다.
#
# NOTE (out-of-CFP-2661-scope): 구판 CFP-26 single-owner 이관 assert(DomainAgent docs/domain-knowledge /
#   PMOAgent docs/retros / ArchitectAgent docs/change-plans)는 dead `agents/` root 가드로 이미 vacuous(never-run)
#   였다. 그 중 docs/adr write-path 축만 본 corpus-wide union 검사로 승계·강화한다. domain-knowledge/retros
#   축(ADR 무관)은 CFP-2661 범위 밖 — 별도 follow-up (발견≠필요, 여기서 무리 확장 금지).
set -euo pipefail
cd "$(dirname "$0")/.."

FAIL=0
SCANNED=0
ADR_PERM_AGENTS=0

shopt -s nullglob
AGENT_MDS=(plugins/*/agents/*.md)
shopt -u nullglob

# CFP-2661 D10 fail-closed: agent md 0건 = dead-root 경로 파손 → exit≠0 (skip 아님, AC-6).
if [[ ${#AGENT_MDS[@]} -eq 0 ]]; then
  echo "✗ [CFP-2661 D10 fail-closed] agent md 0건 (plugins/*/agents/*.md) — 스캔 대상 부재." >&2
  echo "  dead-root 경로 파손 의심 (구 agents/ root 모노레포 이후 부재). vacuous-PASS 봉인 = exit 1." >&2
  echo "check-write-permission-redistribution: census scanned=0 adr_perm_agents=0 — FAIL-CLOSED" >&2
  exit 1
fi

# frontmatter permissions block(allow|deny) 추출 (2번째 `---` 전까지).
extract_block() {
  local f="$1" key="$2"
  awk -v key="$key" '
    /^---$/{c++; next}
    c==1 && /^permissions:/{in_perm=1; next}
    c==1 && in_perm && $0 ~ "^  " key ":"{in_block=1; next}
    c==1 && in_perm && /^  [a-z]+:/{in_block=0}
    c==1 && in_block{print}
    c>=2{exit}
  ' "$f"
}

# block 안 docs/adr write-path 선언 시 archive/adr union 동반 검사 (construct-level, verb 별).
# NOTE(self-lint): 아래 relocation-detection 라인은 OLD docs/adr 와 NEW archive/adr 리터럴을 동일 construct
#   (같은 물리 라인)에 두어 path-relocation-consistency lint 의 co-occurrence 를 스스로 만족한다 (detection
#   pattern 은 dead-path config 아님 — self-flag 회피, born-safe 자기정직).
check_block_union() {
  local f="$1" blockname="$2" block="$3"
  local verb
  for verb in Edit Write; do
    # relocation docs/adr → archive/adr: OLD 지목 ∧ NEW 미동반 = union 위반 (양 리터럴 동일 라인).
    if printf '%s\n' "$block" | grep -qF -- "$verb(docs/adr/**)" && ! printf '%s\n' "$block" | grep -qF -- "$verb(archive/adr/**)"; then
      echo "✗ [CFP-2661 D10] $f permissions.$blockname: $verb(docs/adr/**) 가 $verb(archive/adr/**) union 미동반 (ADR 실 위치 archive/adr, PR #1973; docs/adr 단독 = dead-path, union 의무 · 삭제형 금지)."
      FAIL=1
    fi
  done
}

for f in "${AGENT_MDS[@]}"; do
  SCANNED=$((SCANNED+1))
  allow_block="$(extract_block "$f" allow || true)"
  deny_block="$(extract_block "$f" deny || true)"
  has_adr=0
  # ADR write-path 선언 agent 판정 (docs/adr ∪ archive/adr 어느 형이든; 양 리터럴 동일 라인 = self-lint co-occur).
  if printf '%s\n' "$allow_block" | grep -qE 'docs/adr/\*\*|archive/adr/\*\*'; then has_adr=1; fi
  if printf '%s\n' "$deny_block" | grep -qE 'docs/adr/\*\*|archive/adr/\*\*'; then has_adr=1; fi
  if [[ $has_adr -eq 1 ]]; then
    ADR_PERM_AGENTS=$((ADR_PERM_AGENTS+1))
    check_block_union "$f" allow "$allow_block"
    check_block_union "$f" deny "$deny_block"
  fi
done

# CFP-2661 D10 census (AC-6 — scanned-count emit, dead-root vacuous-PASS 봉인).
echo "check-write-permission-redistribution: census scanned=$SCANNED adr_perm_agents=$ADR_PERM_AGENTS"

if [[ $FAIL -eq 0 ]]; then
  echo "✓ CFP-2661 D10 — corpus-wide ADR-path archive/adr union invariant OK (scanned=$SCANNED, adr_perm_agents=$ADR_PERM_AGENTS)"
fi
exit $FAIL
