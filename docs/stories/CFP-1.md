# CFP-1: v0.9 Review 워커 정의 보강 + Plugin Self-Application 정책 도입

## §1. 사용자 요구사항 (verbatim)

세션 흐름에서 두 단계로 사용자가 요청:

1. **Review 워커 정의 보강**: "이 Agent에서 추가되면 좋을 것이 있을까? claude와 codex를 통해 각각 리뷰하고 종합하여 알려달라." (대상: `agents/ClaudeReviewAgent.md`, IDE에 `ClaudeDesignReviewAgent.md`로 열려 있었으나 v0.9 통합으로 삭제됨 → 통합 후 SSOT인 `ClaudeReviewAgent.md` 대상)
2. **Self-application 정책 도입**: "Story file은 매 변경시 작성이 가능하다면 필수로 작성할 수 있도록 구성하세요"

> 본 Story는 plugin meta 변경에 대한 첫 번째 dogfooding 사례이며, GitHub Issue Form (story.yml)이 plugin repo에 아직 부재하므로 Issue 트리거 자동 생성 없이 수동 작성됨. Issue Forms 인프라는 Self-Application 정책 §"인프라 2단계"에서 별도 도입 예정.

## §2. 도메인 해석 (DomainAgent — 본 변경에서는 brainstorming 결과 압축)

본 변경의 도메인은 **plugin 자체 메타 거버넌스**. 일반 consumer 프로젝트의 도메인 해석과 성격이 다름:

- 도메인 제약: 변경이 plugin SSOT(`templates/`, `CLAUDE.md`, `agents/**`, `docs/orchestrator-playbook.md`)에 영향 → 모든 consumer가 받게 되므로 한 번 굳어지면 변경 비용 큼
- 암묵 가정: plugin이 자기 워크플로우를 적용하지 않으면 consumer 동작 모방 신호 약화 (dogfooding gap)
- 범위 경계: Review 워커 정의 보강 ∪ self-application 정책 도입 ∪ 1단계 인프라(`docs/stories/` 디렉토리). 인프라 2단계(`.github/workflows/`, `ISSUE_TEMPLATE/`)는 본 Story 범위 밖 — 별도 Story로 분리
- 우선순위: Plugin 정책 도입 시점 자체가 dogfooding 지표 — 가능한 한 빠르게

지식 공백: 없음 (이번 변경은 plugin 내부 정책이라 외부 도메인 지식 의존 안 함).

## §3. 관련 ADR

- **[ADR-001-review-agent-unification](../adr/ADR-001-review-agent-unification.md)** (active): 3 lane × 2 vendor = 6 워커를 lane-agnostic 2 워커로 통합. 본 Story는 ADR-001 결정의 운영 robustness 강화 (구조 변경 아님)
- **신규 ADR 필요 없음**: Self-application 정책 도입은 Process Decision이며, plugin 거버넌스 결정이지만 ADR 기준(Architecture Decision: 라이브러리·프레임워크·아키텍처 패턴·데이터 저장·인프라·도메인 핵심 개념)에 부합하지 않음. 향후 정책이 복잡화하면 ADR-002 검토

## §4. 관련 코드 경로 + 책임

| 경로 | 변경 유형 | 현재 책임 | 변경 후 책임 |
|------|-----------|-----------|--------------|
| `agents/ClaudeReviewAgent.md` | 보강 (+61/-8) | Lane-agnostic Claude 리뷰 워커 정의 | + lane별 진단 가이드, packet 검증 강화, WebSearch 가드, failure mode, 회귀 힌트 |
| `agents/CodexReviewAgent.md` | 보강 (+20/-3) | Lane-agnostic Codex 리뷰 워커 정의 | + Claude와 sync된 packet 검증·dedup·회귀 |
| `CLAUDE.md` | 신규 §섹션 | Plugin core 정책 SSOT | + "Story 작성 의무" 섹션 (강제·면제 cutoff + Plugin 자체 적용) |
| `docs/project-config-schema.md` | 신규 키 | Consumer overlay schema SSOT | + `story_cutoff.additional_exempt_categories` |
| `docs/stories/CFP-1.md` | 신규 | (디렉토리 부재) | 본 Story file (plugin self-application 첫 인스턴스) |
| `docs/change-plans/cfp-1-review-polish-and-self-application.md` | 신규 | (없음) | 본 Story의 Change Plan |

## §5. 요구사항 확장 해석 (RequirementsAnalyst — brainstorming 압축)

### 유스케이스

1. **Review 워커 운영 robustness**: PL이 lane=design/code/security 중 하나로 packet 작성 → 워커가 lane-conditional 검증 + lane별 진단 + 자동 P0 룰 + 회귀 힌트 → PL이 dedup·종합 정확도 확보
2. **Plugin 자체 변경에 Story file 강제**: Plugin SSOT 변경 시 Orchestrator가 cutoff 분류 → 강제이면 Story file 작성, 면제이면 commit body에 사유 명시
3. **Consumer 도메인 면제 확장**: Consumer가 `project.yaml`에 도메인 특화 면제 카테고리(`additional_exempt_categories`) 추가 → Orchestrator가 cutoff 분류 시 입력으로 사용

### Acceptance Criteria

- ClaudeReviewAgent + CodexReviewAgent 보강 11+4 = 15건 적용 완료, 두 파일 dedup 키 형식 일치
- CLAUDE.md에 "Story 작성 의무" 섹션 존재 (강제 6항목 + 면제 4항목 + Plugin dogfooding 하위)
- `docs/project-config-schema.md`에 `story_cutoff.additional_exempt_categories` 키 schema 명시
- 본 CFP-1 Story file 자체가 정책의 첫 self-test (§1-7 채움 + §8/§9 N/A 명시)
- Orchestrator는 다음 변경 시작 시 cutoff 분류 선언

### 엣지 케이스

- Cutoff 모호: 강제 측 분류 (정책 명시)
- Plugin meta 변경에서 무의미한 lane: §섹션에 `N/A — <사유>` 명시
- Consumer가 강제 항목 축소 시도: schema validation 부재 시 PR review에서 수동 거절 (자동 차단은 인프라 2단계)

### §5.5 사용자 확인 필요 (blocking wait — 모두 본 세션에서 확인 완료)

- [✓] Cutoff 강제·면제 항목 정의 (Section 1)
- [✓] 인프라 1단계 vs 2단계 분리 (Section 2)
- [✓] Story KEY prefix = `CFP` (Section 2 후속)
- [✓] §8/§9 N/A 처리 방식 (Section 3)
- [✓] 일반 정책으로 일반화 + Consumer overlay 확장 (Section 4)
- [✓] Commit 분할 방식 (Change Plan §9)

## §6. 외부 지식 배경 (Researcher)

본 변경은 plugin 내부 거버넌스 + 통합 후 polish 성격으로 외부 지식 의존도 낮음. 다만 한 가지 외부 입력:

- **Codex(GPT-5) 리뷰**: `codex:codex-rescue` subagent로 ClaudeReviewAgent.md 정의 비대칭·robustness 분석을 요청. Codex가 7개 dimension에서 14건 finding 반환 (P1=8, P2=6). 결과는 본 Change Plan §3.2의 11건 중 다수의 근거가 됨

> "외부 지식 보강 불필요" 판정 사유: plugin 자체 정책 변경 + plugin SSOT 내부 정합성 위주이므로 외부 라이브러리·표준·선행사례 조사 무관. Codex 리뷰는 외부 모델의 독립 관점 입력이지 외부 지식 인용 아님.

ADR 정합성 점검: ADR-001 `status: active`, 본 변경이 그 결정을 위반하지 않음 (lane-agnostic 2 워커 구조 유지, packet 주입 메커니즘 유지). 통과.

## §7. 설계 서사 (Architect)

Change Plan: [`docs/change-plans/cfp-1-review-polish-and-self-application.md`](../change-plans/cfp-1-review-polish-and-self-application.md)

### 핵심 설계 (Change Plan §1·§3·§4·§9 미러링)

**§1 목적**: ADR-001 통합 후 두 가지 gap (운영 robustness · 거버넌스 dogfooding)을 한 변경에 묶어 처리. 본 변경 자체가 정책 도입 + 첫 적용 사례.

**§3 도입할 설계**:
- Review 워커 .md 보강 (lane-conditional packet 검증, lane별 진단 가이드, WebSearch 가드, failure mode, 회귀 힌트, dedup 형식 sync — 15건)
- CLAUDE.md "Story 작성 의무" 신규 섹션 (강제·면제 cutoff + consumer overlay 확장 + plugin dogfooding 단계적 도입)
- `docs/project-config-schema.md` `story_cutoff` 키 추가
- 1단계 인프라: `docs/stories/` 디렉토리 + 본 Story file

**§4 API 계약**: 코드 API 변경 없음. 인터페이스는 (a) CLAUDE.md 정책 텍스트 verbatim, (b) consumer overlay schema 확장 (안전 방향 면제 추가만, 강제 축소 불허).

**§9 분기 선택**: 단일 PR. Phase 1/2 분리 면제. Commit 시리즈 2개로 본질 분리:
- Commit 1: agents/ClaudeReviewAgent.md + agents/CodexReviewAgent.md (v0.9 polish 본질)
- Commit 2: CLAUDE.md + schema + Story file + Change Plan (self-application 정책 본질)

### CodebaseMapper ↔ RefactorAgent 대립 결론

- **Mapper(보수)**: "ADR-001 통합 직후, 추가 보강 불필요. 점진적 polish가 안전."
- **Refactor(혁신)**: "운영 robustness gap이 즉시 누적 비용. dedup·회귀 분류 정확도 저하 → FIX 효율 저하. 정책 도입도 시점이 명확할수록 좋음."
- **채택: Refactor**. 근거: ADR-001은 *구조* 결정이고 *운영 robustness*는 별개 문제. Mapper 우려는 §5 변경 계획 범위를 워커 .md + 정책 신설 + 1단계 인프라로 한정하여 흡수 (인프라 2단계 분리, 전역 리팩토링 없음).

## §8. 개발 서사 (DeveloperPL + role:dev roster)

### §8.1-8.4 Backend / Frontend / DataEng / InfraEng 산출물

**N/A — Plugin meta 변경, 코드 산출물 없음**.

본 변경은 markdown 문서 + 정책 텍스트 변경에 한정. `role: dev` roster의 어떤 에이전트도 활성 책임 없음. DocsAgent가 단독으로 모든 파일을 작성 (CLAUDE.md, schema, Story file, Change Plan + 워커 .md 보강은 본 세션에서 직접 진행).

### §8.5 Impl Manifest (파일 단위 매핑표)

| 파일 경로 | 변경 유형 | 담당 에이전트 | 변경 줄 수 (대략) | 상위 요건 ref |
|-----------|-----------|---------------|-------------------|---------------|
| `agents/ClaudeReviewAgent.md` | 수정 | DocsAgent (proxy) | +61 / -8 | Change Plan §3.2 |
| `agents/CodexReviewAgent.md` | 수정 | DocsAgent (proxy) | +20 / -3 | Change Plan §3.2 |
| `CLAUDE.md` | 수정 | DocsAgent | +37 / -0 | Change Plan §3.3 |
| `docs/project-config-schema.md` | 수정 | DocsAgent | +9 / -1 | Change Plan §3.4 |
| `docs/stories/CFP-1.md` | 신규 | DocsAgent | 신규 | Change Plan §3.5 |
| `docs/change-plans/cfp-1-review-polish-and-self-application.md` | 신규 | DocsAgent (brainstorming proxy) | 신규 | Change Plan 본 파일 자체 |

> Plugin self-application 1단계 적용으로, `subissue-from-impl-manifest.yml` Action이 부재하여 sub-issue 자동 생성 없음. 인프라 2단계 도입 시 자동화.

## §9. 품질 게이트 이력

### §9.0 Clarification 재스폰 이력

해당 없음 — 본 Story는 brainstorming skill로 사용자와의 직접 대화로 진행되었고, RequirementsPL/Architect 정식 스폰이 없었으므로 재스폰 이력 항목 부재.

### §9.1 설계 리뷰

**N/A — 별도 설계 리뷰 lane 면제 사유**: brainstorming skill의 사용자 approval (Section 1-4 + Change Plan §1-10) 자체가 설계 검증 역할. PR review에서 reviewer가 Change Plan 정합성 추가 확인.

대신 본 변경에 대해 비공식 review 1건 진행됨 (Story file 작성 전):

- **Codex 리뷰** (`codex:codex-rescue`): ClaudeReviewAgent.md에 7 dimension 14 findings (P1=8, P2=6). Change Plan §3.2의 보강 11건 중 다수의 근거 제공. 결과는 적용 완료 (Change Plan §3.2 표 참조).

### §9.2 구현 리뷰

**N/A — markdown 정의·정책 변경, 코드 리뷰 lane 무관**. PR review에서 reviewer 확인.

### §9.3 구현 테스트

**N/A — 자동 단위/통합/성능 테스트 대상 아님**. 검증은 후속 변경에서 정책 적용 행위 관찰 (수동).

### §9.4 보안 테스트

**N/A — 코드·의존성·attack surface 변경 없음**. 1차 layer (Dependabot/CodeQL/Secret Scanning) 자동 실행 결과만 PR check로 확인.

## §10. FIX Ledger

| Iter | 시각 | 레인 | 트리거 | 원인 판정 | 재실행 범위 | RESET? |
|------|------|------|--------|-----------|-------------|--------|

**비어있음 — FIX 루프 미발생**. 본 Story는 brainstorming → Change Plan → implementation 1회 진행으로 모든 게이트(N/A 면제 포함) 통과.

## §11. 참조

- **GitHub Issue URL**: 부재 (plugin repo에 Issue Forms 미도입, self-application 1단계). 인프라 2단계 도입 시 post-hoc Issue 생성 검토
- **Phase 1 PR URL**: N/A (단일 PR)
- **Phase 2 PR URL**: 본 PR (예정 — 작성 후 갱신)
- **Change Plan**: [`docs/change-plans/cfp-1-review-polish-and-self-application.md`](../change-plans/cfp-1-review-polish-and-self-application.md)
- **관련 ADR**: [`docs/adr/ADR-001-review-agent-unification.md`](../adr/ADR-001-review-agent-unification.md)

### 회고 (PMOAgent — 본 세션에서 압축)

**발견 1 — Plugin dogfooding gap이 v0.9 통합 직후에 노출됨**: ADR-001로 워커 통합을 마쳤으나 plugin 자체에 Story file 의무가 없어, 통합 직후의 polish 작업(이 Story의 §3.2)이 또다시 Story 없이 진행될 뻔함. 사용자가 "Story file 매 변경 시 가능하면 필수로" 요청하여 정책 부재가 명시적으로 노출됨. 이 인지 자체가 가장 큰 가치.

**발견 2 — Plugin meta 변경의 §처리 표준 부재**: 일반 consumer Story와 plugin meta Story는 lane 의미가 다름 (구현/테스트/보안 N/A). Full 7-lane 강제 시 metaframework recursion 문제. "Full 템플릿 재사용 + lane skip 명시" 채택으로 해결 (Change Plan §3.3 → CLAUDE.md "Plugin 자체 적용" 하위 섹션).

**발견 3 — Consumer overlay 확장의 일방향 원칙**: 강제 축소 불허, 면제 추가만 허용. 이 안전 방향 원칙이 future drift를 막는 invariant.

**향후 작업 (별도 Story)**:
- **CFP-2 (예정)**: 인프라 2단계 — `.github/ISSUE_TEMPLATE/{story,bug,audit}.yml` + 6종 워크플로우 + branch protection. Plugin이 정의한 거버넌스 자동화의 자기 적용 완료.
- **CFP-3 (잠정)**: `story_cutoff` schema validation 자동화 (pre-commit hook 또는 CI check) — 강제 항목 축소 시도 자동 차단.
- **ADR-002 (조건부)**: Process Decision도 ADR 대상으로 격상하는 거버넌스 결정. Plugin 정책이 복잡화하면 발의.
