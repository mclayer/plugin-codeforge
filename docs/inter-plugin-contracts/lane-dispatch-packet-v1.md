---
kind: registry
registry: lane_dispatch_packet
version: "1.0"
status: Active
canonical_repo: mclayer/plugin-codeforge
canonical_path: docs/inter-plugin-contracts/lane-dispatch-packet-v1.md
date: 2026-08-12
authors:
  - DataEngineerAgent (CFP-2926 Phase 2 — inter-plugin-contracts registry 신설 carrier)
related_adrs:
  - ADR-044  # Phase-scoped sequential team — env=1 TeamCreate fan-out dispatch packet + (3개 lane PL 병렬 가능, 나머지 sequential 수업 의존) slot reservation + worker roster (allowed_spawn_roster discriminator constraint + Sonnet-default 14 + Haiku 7 mechanical fallback roster mapping)
  - ADR-042  # agent-model-selection-policy — subagent model tier assigned (Sonnet/Haiku leaf vs Opus PL)
  - ADR-039  # subagent default — allowed_spawn_roster scope_globs output_section ownership disjoint requirement
  - ADR-170  # Orchestrator-owned delegate — PL (depth-1 leaf) can spawn nested subagent 불가(ADR-044 reentrance 제약 3종 inherit)
  - ADR-008  # Inter-plugin contract versioning (MINOR/PATCH versioning, additive extension only for v1.x)
  - ADR-010  # Inter-plugin Contract Sibling Sync (kind:registry exempt, wrapper canonical)
related_files:
  - plugins/codeforge-design/templates/review-pl-base.md  # review_packet 선례 재사용 — §2 field 구조·필수 필드 정의 패턴
  - docs/orchestrator-playbook.md  # §3.0.5 Phase 1 PL dispatch timing + §4.2 Task DAG optional 배치 계획 suggestion
  - templates/team-spec-requirements.yaml  # TEAM-REQUIREMENTS 6 SubAgent roster (RequirementsPLAgent fan-out 사례)
  - docs/inter-plugin-contracts/MANIFEST.yaml  # registries: entry 미추가(lane-dispatch-packet — stop/spawn-event 선례)
  - docs/inter-plugin-contracts/parallel-dispatch-protocol-v1.md  # orchestrator_to_pl_packet schema cross-ref (§6.1 OOP packet dispatch) vs lane_dispatch_packet (PL → worker fan-out)
amendment_log:
  - id: A1
    date: 2026-08-12
    carrier: CFP-2926
    class: initial_version
    change: "신설 — lane PL → worker dispatch packet 필수 필드 계약 (snapshot_sha / scope_globs / output_section / allowed_spawn_roster). review_packet 선례 재사용(계약명 pointer + lane-specific field list). ESCALATE_PACKET_INCOMPLETE 기계 게이트. kind:registry sibling_sync_exempt (ADR-010 §결정 2). version 1.0 — additive-only covenant for v1.x (ADR-008 §결정 2)."
---

# lane-dispatch-packet v1

> **정체**: 본 계약 = codeforge lane PL agent (RequirementsPLAgent, ArchitectPLAgent, DeveloperPLAgent, DesignReviewPLAgent, CodeReviewPLAgent, SecurityTestPLAgent) 가 story 진행 중 worker(sub-agent) 를 spawn 할 때 **Orchestrator → PL → worker** 계층의 dispatch packet 필수 필드 정의다.
>
> **선례 재사용**: `review-pl-base.md` 의 `review_packet` 선례를 답습한다 (field 구조·필수필드 정의·ESCALATE_PACKET_INCOMPLETE 게이트 메커니즘). 신규 mechanism 0 — 기존 패턴을 lane worker 계층(PL→worker)으로 확대.
>
> **설계 SSOT**: [ADR-044 Amendment 7](../../archive/adr/ADR-044-phase-scoped-sequential-team.md) (dispatch packet + roster constraint) + 본 dispatch 계약 (§2 필수 필드 schema + §7.12 구현).

## 1. 목적

codeforge PL agent 는 내부 worker(sub-agent) 를 spawn 할 때 다음 정보를 **structured packet** 형태로 전달해야 한다:
- **story_key**: 계약 identity (freeze, cross-lane trace)
- **role**: worker agent type (roster-derived subagent_type)
- **scope_globs**: worker가 읽을 파일 범위 (ownership boundary — taint 아님)
- **output_section**: worker가 쓸 Story section 번호 (소유권 disjoint 보장)
- **allowed_spawn_roster**: worker가 spawn 가능한 nested subagent roster 제한 (depth-1 leaf 강제)
- **contract_version**: 본 계약 버전 (호환성)

**필수 필드 누락 시 게이트**: Orchestrator 가 Packet Incomplete 신호(`ESCALATE_PACKET_INCOMPLETE`) 감지 후 Story phase 진행 차단 — 예외 0, manual override 불가.

## 2. Schema (필수 필드 5 + 선택 2)

```yaml
lane_dispatch_packet:
  contract_version: "1.0"        # 필수 — 본 계약 버전 (호환성 선언)
  lane: 요구사항 | 설계 | 구현    # 필수 — 10개 lane label enum (11값 label-registry-v2, 리뷰 4 lane 은 review_packet 유지)
  role: <agent_type>             # 필수 — worker subagent 종류 (roster 실명 verbatim, e.g. `AnalystAgent` / `RefactorAgent`)
  story_key: <KEY>               # 필수 — e.g. `CFP-2926` (public non-sensitive, freeze)
  snapshot_sha: <40-hex>         # 필수 — AC-10 S-1 (변경 범위 증명: "이 SHA 시점의 코드 상태를 기준으로 결정함")
  scope_globs: [<glob>...]       # 필수 — worker read-set (path pattern). taint 경계 아님 — 무엇을 읽을지만 지정
  output_section: <§N.M>         # 필수 — Story §8 / §9 / §10 등 worker write 섹션 지시자 (배치만, 관점 아님. 소유권 disjoint 보증)
  allowed_spawn_roster: [<agent_type>...]  # 필수 (depth-1 leaf PL = []빈 list, nested spawn 금지 ADR-170)
  common_input_refs: [<path>...] # 선택 — Story §3/§6 등 public read-only 참조 file list (cross-lane baseline)
```

### 2.1 필수 필드 위반 게이트 (`ESCALATE_PACKET_INCOMPLETE`)

PL 이 dispatch packet 작성 시 위 5 필수 필드 누락 또는 값 부재 = worker 에서 **ESCALATE 신호** 발화 + **Story phase 진행 차단**(manual override 불가). Orchestrator 가 신호 감지 후:
1. Story frontmatter `status: escalate` + escalation reason 기재
2. PL 경유 Architect → Story 반환 (재작성 의무)

## 3. 필드별 정의 (§2 필수 필드 상세)

### contract_version
- **값**: `"1.0"` (본 계약의 major.minor version)
- **목적**: 계약 호환성 선언. 구 worker 가 신 packet 형식 해석 불가 시 fallback 신호
- **required**: Yes

### lane
- **값**: 10개 lane enum ∪ `없음` (label-registry-v2 정합)
  - 요구사항 / 요구사항-리뷰 / 설계 / 설계-리뷰 / 구현 / 구현-리뷰 / 구현-테스트 / 보안-테스트 / 배포 / 배포-리뷰 / 없음
- **정의**: worker 가 진입하는 lane context (Story 다음 lane 진입 배경 정보)
- **required**: Yes
- **주의**: 리뷰 4 lane(요구사항-리뷰/설계-리뷰/구현-리뷰/보안-테스트)은 review_packet 사용 (본 계약 scope 외)

### role
- **값**: subagent_type (roster-derived, e.g. `AnalystAgent` / `RefactorAgent` / `DomainAgent` / `CodebaseMapperAgent`)
- **정의**: worker 의 agent type. templates/agent-roster.yaml 또는 consumer project.yaml 에서 검증되는 실명
- **required**: Yes
- **정직성**: `unknown-agent` fallback 허용 (semi-open, 미등재 값을 거부하지 않음 — ADR-141 semi-open enum pattern)

### story_key
- **값**: `CFP-2926` 또는 `<CONSUMER>-123` (consumer project key prefix 정합)
- **정의**: Story identity 상관 ID (freeze, cross-lane trace)
- **required**: Yes
- **민감성**: public non-sensitive (documentation 노출 OK)

### snapshot_sha
- **값**: 40자 hex (git commit SHA)
- **정의**: AC-10 S-1 — 변경 정책 snapshot (이 SHA 시점의 코드를 기준으로 변경 범위·영향 결정)
- **required**: Yes
- **출처**: Orchestrator 가 Story 진입 시 `git rev-parse HEAD` 실측

### scope_globs
- **값**: glob pattern list (예: `["docs/change-plans/**", "scripts/lib/**", "plugins/codeforge-develop/"]`)
- **정의**: worker 가 **read** 권한을 갖는 파일 범위. **write 권한이 아닌 read-set만 지정**
- **required**: Yes
- **주의**: 이는 **정보 보호**가 아니라 **책임 영역 명시** (worker 가 output_section 밖을 read 하는 것은 문제 아님, 하지만 write 책임은 output_section 만) — taint analysis 아님

### output_section
- **값**: `§8` / `§8.1.1` / `§10` / `§11` 등 (Story frontmatter section anchor)
- **정의**: worker 가 **write(편집) 권한**을 갖는 Story section 지시자. **배치 책임만 명시, 관점(perspective)이 아님** (RequirementsPLAgent 관점 ≠ ArchitectAgent 관점이어도 같은 output_section 에 기여 가능)
- **required**: Yes
- **소유권**: section 당 1 worker 권한(disjoint, SoD) — 동시 2 worker 의 같은 section write 금지 (ADR-039 §결정 3)

### allowed_spawn_roster
- **값**: agent_type list (또는 `[]` 빈 list, depth-1 leaf 일 때)
- **정의**: worker 가 spawn 가능한 nested sub-worker roster 제한
  - **depth-1 leaf (PL 직속)**: `[]` (spawn 금지, ADR-170 depth-1 제약)
  - **depth-2 intermediate(PL 의 worker)**: 명시된 roster 만 spawn 가능 (예: `["CodebaseMapperAgent", "DomainAgent"]`)
- **required**: Yes (기본값은 scope_globs 기준 자동 추론 금지 — 명시 의무)
- **주의**: 비어있어도(depth-1) 명시 의무 (무의식적 상향 spawn 차단)

### common_input_refs (선택)
- **값**: path list (예: `["docs/stories/CFP-2926.md#section-3", "archive/adr/ADR-044-*.md"]`)
- **정의**: Story 의 public read-only section 참조 (cross-lane baseline, 변경 대상 아님)
- **required**: No
- **목적**: worker 가 Story 타 lane 결과를 context 로 참조할 때 명시적 path 제공 (implicit 경로 추론 금지, ADR-039 scope_globs 한정)

## 4. 변경 규칙

- **additive-only v1.x**: 신 필드 추가 = MINOR bump + amendment (ADR-008 §결정 2). 필드 삭제/순서변경 = MAJOR(v2.0 BREAKING).
- **enum 변경**: lane enum 확장(9 lane → 10 lane) = MINOR + amendment. lane 값 제거 = MAJOR.
- **role semi-open enum**: `unknown-agent` fallback 허용 (미등재 값 reject 안함). roster 동기화 실패 시 graceful degrade.

## 5. 선례 & 선행 연구

### review_packet 재사용
`plugins/codeforge-review/templates/review-pl-base.md` 의 `review_packet` schema 를 답습:
- 필수 필드 명시 (contract_version / lane / checklist_path / scope_globs / category_enum / story_key)
- ESCALATE_PACKET_INCOMPLETE 게이트 (누락 시 phase 진행 차단, manual override 불가)
- lane-specific 확장 가능 (security packet 은 `first_layer_findings` 추가)

본 계약은 **PL→worker** 계층에 동일 패턴 적용.

### parallel-dispatch-protocol-v1 와의 경계
- `parallel-dispatch-protocol` = **Orchestrator → PL** 계층 (`orchestrator_to_pl_packet`: plan DAG + pl_autonomous_parallel_authority + dispatch_mode)
- `lane_dispatch_packet` = **PL → worker** 계층 (snapshot_sha + scope_globs + output_section + allowed_spawn_roster)

양 계약은 시간 순으로 순차:
1. Orchestrator → PL: parallel-dispatch-protocol (batch 계획 + PL 권한)
2. PL → worker: lane-dispatch-packet (배분 packet)

양 packet 은 disjoint field.

## 6. 정직성 (ADR-119 research-before-claims)

**hollow-gate 1순위**: `snapshot_sha` 가 "변경 정책 기준"이지 "변경 **증명**"이 아니다. SHA 는 시점 표기일 뿐, Git 그 SHA 이후 변경이 정책을 준수했는지 guarantee 하지 않는다. **AC-10 S-1 = 의도 선언**이지 사후 검증이 아니다.

**non-blocking**: packet 누락(ESCALATE_PACKET_INCOMPLETE)은 게이트이나, worker 가 packet 을 **overwrite/무시**하는 것을 prevent 하지 않는다 (runtime 제약 0). 정직성은 **워커 accountability** (그 worker 는 packet 에 기술한 output_section 만 기여한다는 서약).

## 7. Backward Compatibility

기존 worker (packet 미인식) = graceful degrade — Orchestrator 가 `contract_version` 부재 감지 시 "packet 구 형식" 추정 + worker 에 fallback signal.

신 packet (신 필드) + 구 worker 기대값 gap = ESCALATE_PACKET_INCOMPLETE (신 packet 의 새 필드는 선택이 없음).

## 7.12 Instantiation Example (drafter 역할)

drafter 역할 = depth-2 intermediate (PL 직속이 아닌 PL 의 worker):

```yaml
lane_dispatch_packet:
  contract_version: "1.0"
  lane: 설계
  role: RefactorAgent            # PL = ArchitectPLAgent, worker = RefactorAgent
  story_key: CFP-2926
  snapshot_sha: 3a7cae2f3 (worktree HEAD, 예시)
  scope_globs: 
    - "src/**"                     # read-set: 실코드
    - "docs/architecture/**"        # 기존 arch doc
    - "archive/adr/**"             # ADR 참조
  output_section: "§3"             # ArchitectPLAgent 의 Change Plan 중 구조 리팩터 섹션
  allowed_spawn_roster: []         # depth-2 leaf → spawn 금지 (ADR-170 depth-1 제약)
  common_input_refs:
    - "docs/change-plans/CFP-2926.md#section-1"  # Story 요구사항(change-plan), read-only baseline
```

RefactorAgent(drafter) 는 다음을 보장한다:
- output_section(`§3`)만 편집
- allowed_spawn_roster 공 list → 자신의 sub-agent 미spawn
- scope_globs 범위 read 권한 (스스로 이 범위 밖 파일을 read 해도 packet 은 정의하지만, write 책임은 `§3` 한정)
