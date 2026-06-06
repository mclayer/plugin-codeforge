## 5. docs/stories file 동기화

### 5.1 Lane plugin self-write 체크리스트

ζ arc decomposition (CFP-31~CFP-40) 후 write 책임은 lane plugin 별로 분산. 아래 표는 각 트리거 시점에 어떤 agent 가 어디에 직접 write 하는지 정리.

| 트리거 | 갱신 path | 책임 agent |
|--------|----------|------------|
| Issue Form 제출 | Story §1 verbatim + Phase 1 PR | story-init.yml Action 자동 |
| RequirementsPL 통합 완료 | Story §2/§5/§6 | RequirementsPLAgent (codeforge-requirements) |
| DomainAgent 지식 공백 발견 시 | `docs/domain-knowledge/<area>/<topic>.md` | DomainAgent (codeforge-requirements) |
| RequirementsPL 통합 후 ADR / 코드 경로 갱신 | Story §3/§4 | RequirementsPLAgent (codeforge-requirements) |
| ArchitectAgent Change Plan + ADR 확정 | `docs/change-plans/<slug>.md` + `docs/adr/ADR-NNN-<slug>.md` + Story §3/§7/§11 | ArchitectAgent (codeforge-design) |
| 설계 리뷰 iteration 종료 (ReviewPL packet return) | (no direct write — packet only) | DesignReviewPLAgent (codeforge-review, review-verdict-v3 pl_recommendation) |
| 설계 리뷰 PASS/FIX verdict final write | Story §9.1 + GitHub comment [설계-리뷰] + gate:design-review-pass label + phase transition + Story §12 row | **Orchestrator 단독** (CFP-61 / ADR-022 review-verdict 5-step step 4) |
| 구현 완료 | Story §8 + §8.5 Impl Manifest + Phase 2 PR creation | DeveloperPLAgent (codeforge-develop) |
| 구현 리뷰 iteration 종료 (ReviewPL packet return) | (no direct write — packet only) | CodeReviewPLAgent (codeforge-review, review-verdict-v3 pl_recommendation) |
| 구현 리뷰 PASS/FIX verdict final write | Story §9.2 + GitHub comment [구현-리뷰] + phase transition + Story §12 row | **Orchestrator 단독** (CFP-61 / ADR-022 review-verdict 5-step step 4) |
| 구현 테스트 종료 (CI gate) | Story §9.3 (`gh pr checks` 결과 — Orchestrator 직접 기록) | **Orchestrator 단독** (ADR-048 CI gate inline) |
| 통합 테스트 종료 (IntegrationTestAgent) | Story §9 통합 테스트 섹션 append + `phase:보안-테스트` 전환 | Orchestrator 단독 |
| 보안 테스트 iteration 종료 (ReviewPL packet return) | (no direct write — packet only, lanes.security_ai: true 시만) | SecurityTestPLAgent (codeforge-review, review-verdict-v3 pl_recommendation) |
| 보안 테스트 PASS/FIX verdict final write | Story §9.4 + GitHub comment [보안-테스트] + gate:security-test-pass label + phase transition + Story §12 row | **Orchestrator 단독** (CFP-61 / ADR-022 review-verdict 5-step step 4) |
| FIX 발생 | Story §10 FIX Ledger append | **Orchestrator 단독** (CFP-32 fix-event-v1 monopoly) |
| PMOAgent 회고 | `docs/retros/<sprint>.md` + Story §11 + Epic Milestone close | PMOAgent (codeforge-pmo) |
| 단계별 상태 변화 | GitHub Issue comment `[<phase>] <Agent>: <한 줄>` | review-verdict 영역 → Orchestrator (CFP-61); 기타 → 각 lane plugin

### 5.2 Story file 읽기 규약

- **필요한 섹션만 읽기**: 프롬프트에 `§X, §Y 참조` 명시 → 에이전트가 `Read(docs/stories/<KEY>.md)` 후 해당 섹션만 참조
- 전체 file 읽기는 ArchitectAgent (chief author) 설계 진입 1회만 허용 (§1-6 전체 필요)
- file 변경 권한 분담 (CFP-26 Phase 0a 이후):
  - `docs/change-plans/**` + `docs/adr/**` → **ArchitectAgent direct**
  - `docs/domain-knowledge/**` → **DomainAgent direct**
  - `docs/retros/**` → **PMOAgent direct**
  - `docs/stories/**` 각 섹션 → 해당 lane plugin self-write (§5.1 표 참조). §10 FIX Ledger → **Orchestrator 단독** (CFP-32 fix-event-v1). §9 (review-verdict) + §12 (Sonnet Decision Log) → **Orchestrator 단독** (CFP-61 / ADR-022 review-verdict final write)
  - `docs/**` general (orchestrator-playbook, plugin-design, consumer-guide 등) → Orchestrator 또는 수동
  - GitHub Issue/PR/comment + label → review-verdict 영역 ([설계-리뷰] / [구현-리뷰] / [보안-테스트] comment + gate/phase label) → **Orchestrator 단독** (CFP-61 / ADR-022). 기타 → 각 lane plugin self-write (codeforge-{review,pmo,requirements,test,develop,design} CLAUDE.md self-write 표)
  - 그 외 모든 에이전트는 자기 owner section 에만 직접 write — 4 single-owner type(`change-plan`/`adr`/`domain-knowledge`/`retro`)은 owner agent direct write (CFP-26 Phase 0a)

### 5.3 GitHub Issue body vs Story file

| 위치 | 내용 |
|------|------|
| Story Issue body | "Story SSOT: `docs/stories/<KEY>.md`" 한 줄 링크 (story-init.yml이 자동 변환) |
| docs/stories/<KEY>.md | 전체 컨텍스트·서사 (§1-11 규격) |
| Story Issue comments | 단계별 이벤트 로그 (각 lane plugin 이 자기 phase prefix `[<phase>] <AgentName>: <한 줄>` 형식으로 직접 기록) |

GitHub Issue는 워크플로우 상태·이벤트, docs file은 구조화 영속 — 역할 분리.

---

