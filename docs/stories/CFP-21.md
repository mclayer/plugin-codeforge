# CFP-21: DataMigrationArchitectAgent — 6번째 deputy (Codex audit #2, BREAKING)

라벨: `type:story`, `phase:구현`, `plugin-meta-na`

---

## §1. 사용자 요구사항 (verbatim)

> 다음 실행 (CFP series autonomous progression — Codex audit #2 deferred queue, ADR-006 패턴 차용)

## §2. 도메인 해석 (DomainAgent)

ADR-004 §"후속 조치" + v0.11.0 sprint 회고 §2.1에서 명시한 Codex audit #2 ("데이터 layer 결정 누락 위험") 직접 적용. CFP-19/CFP-20 머지로 N=5 deputy 안정화 완료. 데이터 마이그레이션·schema 진화·rollback 결정은 현재 ArchitectAgent chief author의 implicit 책임이지만 독립 advocate 부재 — schema 변경 영향·downtime risk·rollback path가 설계 시점에 누락되면 비싼 회귀 발생.

ADR-006 (TestContractArch precedent) 패턴 그대로 차용 — shift-left 데이터 무결성 advocate. plugin meta paradox로 본 CFP는 자기 적용 안 함, 다음 Story부터 §11 데이터 마이그레이션 발효.

지식 공백: 없음.

## §3. 관련 ADR

- **ADR-004**: ArchitectPL + SecurityArch (직접 제약 — deputy advocate 패턴 SSOT)
- **ADR-005**: Plugin self-application N/A (직접 제약 — §8/§9 N/A 처리 근거)
- **ADR-006**: TestContractArch precedent (직접 제약 — 본 CFP가 mirror)
- **ADR-007** (NEW): DataMigrationArchitectAgent 도입 결정

## §4. 관련 코드 경로 + 책임

- `agents/DataMigrationArchitectAgent.md` (NEW)
- `agents/{ArchitectPLAgent, ArchitectAgent}.md` — deputy 4 → 5
- `agents/{CodebaseMapper, Refactor, SecurityArchitect, TestContractArchitect}.md` — cross-ref 1줄
- `templates/change-plan.md` — §10 다음 §11 신설
- `templates/review-checklists/design.md` — §11 audit + 3 P0 차단 룰
- `agents/{DesignReviewPL, CodexReview}Agent.md` — category enum + severity overrides
- `CLAUDE.md` — 24 core, 다이어그램, 매트릭스, FIX decision table, 4-way 대립
- `docs/orchestrator-playbook.md` — 24 core, deputy 5인, 토큰 budget, §3.1, §3.2 표
- `docs/adr/ADR-007-datamigration-architect.md` (NEW)
- `.claude-plugin/plugin.json` — 0.13.0 → 0.14.0
- `CHANGELOG.md` — v0.14.0 BREAKING entry
- `docs/migration-guide.md` — v0.13.0 → v0.14.0 절

## §5. 요구사항 확장 해석 (RequirementsAnalyst)

**유스케이스**:
- (UC-1) 6번째 deputy로 schema 진화·rollback·integrity invariant 결정 advocate
- (UC-2) Change Plan §11 신설 — 5개 sub-section + N/A
- (UC-3) DesignReview §11 P0 차단 룰 (§7 audit 패턴 동형)

**AC**:
- AC-1: agent count 23 → 24 (CLAUDE.md "24 core" + ls agents/*.md = 24)
- AC-2: invariant-check.yml 8 step PASS
- AC-3: data-migration enum 4 곳 동일 (design.md SSOT + DesignReviewPL + ClaudeReview/CodexReview)
- AC-4: severity overrides §11 P0 3건 추가 (count parity)
- AC-5: plugin.json 0.14.0 ↔ CHANGELOG.md [0.14.0]
- AC-6: migration-guide v0.13.0 → v0.14.0 절 + 목차 link

**제외 범위**:
- §section ownership model (ADR-008 deferred)
- DataMigrationArch deep audit (다음 dogfooding 후)
- Codex audit #4-#6 잔여 항목 (CFP-22+)

§5.5 사용자 확인 필요: 없음 (autonomous progression 권한 보유).

## §6. 외부 지식 배경 (Researcher)

외부 지식 보강 불필요. 본 CFP는 plugin self-application meta 변경. ADR-006 (TestContractArch) precedent + ADR-004 (deputy advocate) 패턴 internal evidence로 충분.

## §7. 설계 서사 (ArchitectAgent + ArchitectPLAgent 검수)

**Spec**: [../superpowers/specs/2026-04-28-cfp-21-datamigration-architect-design.md](../superpowers/specs/2026-04-28-cfp-21-datamigration-architect-design.md)
**Plan**: [../superpowers/plans/2026-04-28-cfp-21-datamigration-architect.md](../superpowers/plans/2026-04-28-cfp-21-datamigration-architect.md)

**§1 목적**: 6번째 deputy 신설 — Codex audit #2 직접 closure. shift-left 데이터 무결성.

**§3 도입할 설계**: SecurityArchitectAgent verbatim 도형 mirror, 도메인 substitution.

**§4 API 계약**: Change Plan §11.1-§11.6 schema (Schema 영향 / Migration 전략 / Rollback / integrity invariant / Backfill / N/A).

**§7 보안 설계 요약**: Trust boundary 변화 없음. DataMigrationArch 권한은 SecurityArch 동일 (Read/Grep/Glob + WebSearch/WebFetch + write queue).

**§9 분기 선택 요약**: 새 deputy (option A) 채택. Change Plan §11 신설 + 책임 매트릭스 6행 추가.

**4-way 대립 결론**: 본 CFP는 plugin meta paradox라 deputy 병렬 spawn 안 함. ADR-007 = ADR-006 mirror, structural precedent.

## §8. 개발 서사

§8 lane은 **plugin-meta-na** (ADR-005). 본 CFP는 production code (`src/**`) 변경 없음 — 14 commit 모두 markdown SSOT 변경.

### §8.5 Impl Manifest

| change | path | agent_role | related_change_plan_section | description |
|--------|------|------------|------------------------------|-------------|
| A | docs/superpowers/specs/2026-04-28-cfp-21-datamigration-architect-design.md | DocsAgent | spec | CFP-21 spec |
| A | docs/superpowers/plans/2026-04-28-cfp-21-datamigration-architect.md | DocsAgent | plan | CFP-21 plan |
| A | docs/stories/CFP-21.md | DocsAgent | Story doc | Story SSOT |
| A | agents/DataMigrationArchitectAgent.md | DocsAgent | §3 | 6번째 deputy 신설 |
| M | agents/ArchitectPLAgent.md | DocsAgent | §3 | deputy 4 → 5 + Phase 1.5 + 메타-규칙 1 §11 |
| M | agents/ArchitectAgent.md | DocsAgent | §3 | deputy 4 → 5 + Change Plan §1-§11 + §11 author input |
| M | agents/CodebaseMapperAgent.md | DocsAgent | §3 cross-ref | DataMigrationArch §11 + 4-way 대립 |
| M | agents/RefactorAgent.md | DocsAgent | §3 cross-ref | DataMigrationArch §11 + 4-way 대립 |
| M | agents/SecurityArchitectAgent.md | DocsAgent | §3 cross-ref | DataMigrationArch §11 + 4-way 대립 |
| M | agents/TestContractArchitectAgent.md | DocsAgent | §3 cross-ref | DataMigrationArch §11 + 4-way 대립 |
| M | templates/change-plan.md | DocsAgent | §4 | §11 데이터 마이그레이션 신설 (§11.1-§11.6) |
| M | templates/review-checklists/design.md | DocsAgent | §4 | category enum data-migration + §11 audit + 3 P0 룰 |
| M | agents/DesignReviewPLAgent.md | DocsAgent | §4 | category_enum + severity_overrides §11 P0 3건 |
| M | agents/CodexReviewAgent.md | DocsAgent | §4 | lane=design prompt category enum + auto-P0 §11 |
| M | docs/orchestrator-playbook.md | DocsAgent | §5 | 24 core + deputy 5인 + 토큰 budget + §3.1/§3.2 |
| M | CLAUDE.md | DocsAgent | §5 | 24 core + 다이어그램 + 매트릭스 6행 + FIX decision table + 4-way 대립 |
| A | docs/adr/ADR-007-datamigration-architect.md | DocsAgent | §6 | DataMigrationArch 결정 ADR (ADR-006 mirror) |
| M | .claude-plugin/plugin.json | DocsAgent | §6 release | 0.13.0 → 0.14.0 |
| M | CHANGELOG.md | DocsAgent | §6 release | v0.14.0 BREAKING entry |
| M | docs/migration-guide.md | DocsAgent | §6 migration | v0.13.0 → v0.14.0 절 + 목차 link |

### §8.4 N/A 사유 (ADR-005 plugin-meta-na)

본 CFP는 production code 변경 없음 — 모든 변경이 SSOT markdown 파일. §8 Test Contract `runtime-inert` (코드는 있으나 테스트 대상 runtime behavior 변경 없음) 분류 + plugin-meta-na 적용.

### §11.6 N/A 사유 (DataMigrationArch self-application paradox)

본 CFP는 DataMigrationArch 부재 상태에서 작성 (paradox). 본 §11.6 N/A: "본 Story는 데이터 layer 변경 없음 — markdown SSOT 변경만, schema 변경 0개". §11 신설 적용은 다음 Story부터.

## §9. 품질 게이트 이력

§9 lane은 **plugin-meta-na** (ADR-005):

- §9.1 설계 리뷰: N/A — spec/plan이 audit 결과 반영 (Codex #2 + ADR-004 + ADR-006 precedent)
- §9.2 구현 리뷰: N/A — 14 commit이 mechanical markdown edit, plan에 anchor 명시
- §9.3 구현 테스트: N/A — code 변경 없음, invariant-check.yml 자동 검증 대체
- §9.4 보안 테스트: N/A — code 변경 없음, trust boundary 변화 없음

invariant-check.yml 자동 검증으로 SSOT parity 확인 → CI PASS 시 admin override merge.

## §10. FIX Ledger

(plugin-meta-na — FIX lane 미진입)

## §11. 데이터 마이그레이션

§11.6 N/A — "본 Story는 데이터 layer 변경 없음 — markdown SSOT 변경만, schema 변경 0개". DataMigrationArch self-application paradox.

## §12. 참조

- Spec: [../superpowers/specs/2026-04-28-cfp-21-datamigration-architect-design.md](../superpowers/specs/2026-04-28-cfp-21-datamigration-architect-design.md)
- Plan: [../superpowers/plans/2026-04-28-cfp-21-datamigration-architect.md](../superpowers/plans/2026-04-28-cfp-21-datamigration-architect.md)
- ADR-007: [../adr/ADR-007-datamigration-architect.md](../adr/ADR-007-datamigration-architect.md)
- 선행 ADR: [ADR-004](../adr/ADR-004-architectpl-securityarch-restructure.md), [ADR-005](../adr/ADR-005-plugin-self-application-na-standardization.md), [ADR-006](../adr/ADR-006-testcontract-architect.md)
- PR: TBD
