# CFP-19: 오케스트레이션 병렬화 — Tier 1+2 R1-R11 Story 처리시간 단축

라벨: `type:story`, `phase:구현`, `plugin-meta-na`

---

## §1. 사용자 요구사항 (verbatim)

> 전체적으로 너무 느리다. 병렬로 수행할 수 있는 작업들이 있을텐데 너무 순차적으로 수행하는게 아닌지 codex와 함께 리뷰해서 계획된 CFP보다 우선해서 개정하자.

## §2. 도메인 해석 (DomainAgent)

**Plugin meta 변경 — Tier 1+2 11개 병렬화 개선 (R1-R11)**. 본 CFP는 codeforge plugin 자체 오케스트레이션 SSOT 문서 변경이라 도메인 컨텍스트가 plugin 자체. 도메인 지식 공백 없음 — 기존 ADR-001(review unification) / ADR-004(ArchitectPL+SecurityArch) / ADR-006(TestContractArch) / ADR-005(plugin-meta-na) 컨텍스트로 충분.

**Plugin meta paradox**: 변경된 병렬화 규칙은 다음 Story부터 발효. 본 CFP-19 자체는 기존 직렬 프로세스로 진행 (CFP-17/18 동일 패턴, ADR-005 plugin-meta-na 적용).

지식 공백: 없음.

## §3. 관련 ADR

- **ADR-001**: Review Agent Unification (직접 제약 — R3 Orchestrator-direct dual spawn 정합)
- **ADR-004**: ArchitectPL + SecurityArch (직접 제약 — R8 fail-fast pre-synthesis가 deputy 모델 정합)
- **ADR-005**: Plugin self-application N/A standardization (직접 제약 — 본 CFP §8/§9 N/A 처리 근거)
- **ADR-006**: TestContractArch (배경 참조 — N=5 deputy 안정화 후 ADR-007 검토 명시)

신규 ADR 없음 (Non-BREAKING).

## §4. 관련 코드 경로 + 책임

- `templates/review-pl-base.md` — 3 ReviewPL 공통 SSOT (R2/R3/R11)
- `agents/{DocsAgent,ArchitectPLAgent,DeveloperPLAgent,DesignReviewPLAgent,CodeReviewPLAgent,SecurityTestPLAgent,TestAgent}.md` — agent role md
- `docs/orchestrator-playbook.md` — Orchestrator 행동 SSOT
- `CLAUDE.md` — 다이어그램·Never-skippable·매트릭스 SSOT
- `.gitignore` — `.claude-work/cache/` 추가 의무 (R6/R10 cache)
- `.claude-plugin/plugin.json` + `CHANGELOG.md` — version bump

## §5. 요구사항 확장 해석 (RequirementsAnalyst)

**유스케이스**:
- (UC-1) Story 1건 처리시간 단축 — 직렬 병목 11개 (B1-B11) 식별 후 병렬화/캐시/fast-path 제거
- (UC-2) 본 plugin 자기 적용 안 함 — 기존 직렬 절차로 본 CFP 진행

**AC (Acceptance Criteria)**:
- AC-1: ADR 변경 0건 (Non-BREAKING)
- AC-2: invariant-check.yml 8 step 모두 PASS
- AC-3: 11개 R 모두 SSOT 문서 (`templates/review-pl-base.md`, `agents/**`, `docs/orchestrator-playbook.md`, `CLAUDE.md`)에 반영
- AC-4: enum/필드 일관성 — `mode: blocking|background`, `mechanical_category: typo|broken-link|minor-naming|comment-only|none`, `subset: functional|performance|all`, `kind: impl-manifest`, `type: security-prefetch`
- AC-5: cache 파일 `.gitignore`에 추가 (R6 sections + R10 sec1)
- AC-6: plugin.json `0.12.0 → 0.13.0`, CHANGELOG.md v0.13.0 entry

**제외 범위**:
- §section ownership model (ADR-007 별도 발의)
- 2-PR draft pipeline (deferred)
- CFP-20 DesignReview checklist 확장 (PMO 권고 deferred)
- CFP-21 DataMigrationArchitectAgent (deferred)

**암묵 가정**:
- 본 plugin 자기 적용 안 함 — 기존 직렬 프로세스로 진행 (paradox 처리)
- consumer overlay에 영향 없음 — overlay는 N=5 deputy 모델 그대로 유지
- 13 commit을 단일 PR로 통합 (CFP-17 PR #50 패턴, plugin-meta-na 1 PR pattern)

§5.5 사용자 확인 필요: 없음 (사용자 결정 (c) 채택, 즉 1 PR 통합 + plugin-meta-na 적용 완료).

## §6. 외부 지식 배경 (Researcher)

외부 지식 보강 불필요 — 본 CFP는 plugin 자체 메타 변경. 외부 라이브러리/표준/선행사례 참조 없음.

근거:
- Codex(GPT-5) 감사 결과 (P-1..P-8): conversation 내 internal evidence
- general-purpose self-audit (a..k): conversation 내 internal evidence
- 두 audit 합의로 11개 직렬 병목 (B1-B11) 식별 — spec §1.1 SSOT

## §7. 설계 서사 (ArchitectAgent + ArchitectPLAgent 검수)

**Change Plan**: spec/plan 자체가 Change Plan 역할 (plugin-meta-na 패턴, CFP-17 동일):
- spec: [docs/superpowers/specs/2026-04-27-cfp-19-orchestration-parallelization.md](../superpowers/specs/2026-04-27-cfp-19-orchestration-parallelization.md)
- plan: [docs/superpowers/plans/2026-04-27-cfp-19-orchestration-parallelization.md](../superpowers/plans/2026-04-27-cfp-19-orchestration-parallelization.md)

**§1 목적**: Story 1건 처리시간 60-90분 → 30-40% 단축 (예상 20-32분 단축).

**§3 도입할 설계**:
- R1 dual-mode write queue · R2 verdict-first · R3 Orchestrator-direct dual spawn
- R4 parallel diagnosis · R5 §8.5 helper · R6 warm cache · R7 Phase 1∥Phase 2 prep · R8 fail-fast pre-synthesis
- R9 TestAgent subset · R10 security-prefetch · R11 mechanical fast-path

**§4 API 계약**:
- write queue frontmatter: `mode: blocking | background` 필수
- ReviewPL verdict packet: `mechanical_category` 필드 추가
- TestAgent: `subset` arg 추가
- DocsAgent: 신규 type=`security-prefetch`, kind=`impl-manifest`

**§7 보안 설계 요약**: cache 파일 `.gitignore` 의무 추가 (Trust boundary 변화 없음, sec1.json에 CVE 정보 포함 가능).

**§9 분기 선택 요약**: Tier 1+2 채택 (Tier 3 §section ownership은 N=5 deputy 안정화 후 ADR-007).

**3-way 대립 결론**: 본 CFP는 plugin meta paradox라 deputy 병렬 spawn 안 함 (CFP-17/18 동일 패턴). spec/plan이 audit 합의 결과를 반영.

## §8. 개발 서사

§8 lane은 **plugin-meta-na** (ADR-005). 본 CFP는 production code (`src/**`) 변경 없음 — 13 commit 모두 docs/agents/templates markdown SSOT 변경.

### §8.5 Impl Manifest

| change | path | agent_role | related_change_plan_section | description |
|--------|------|------------|------------------------------|-------------|
| A | docs/superpowers/specs/2026-04-27-cfp-19-orchestration-parallelization.md | DocsAgent | spec | CFP-19 spec |
| A | docs/superpowers/plans/2026-04-27-cfp-19-orchestration-parallelization.md | DocsAgent | plan | CFP-19 plan |
| A | docs/stories/CFP-19.md | DocsAgent | Story doc | Story SSOT |
| M | templates/review-pl-base.md | DocsAgent | R2/R3/R11 | verdict-first + Orchestrator dispatch + mechanical fast-path |
| M | agents/DesignReviewPLAgent.md | DocsAgent | R11 | mechanical_category 분류 의무 |
| M | agents/CodeReviewPLAgent.md | DocsAgent | R11 | mechanical_category 분류 의무 |
| M | agents/SecurityTestPLAgent.md | DocsAgent | R11 | mechanical_category none 예외 |
| M | agents/DocsAgent.md | DocsAgent | R1/R5/R10 | dual-mode + impl-manifest helper + security-prefetch helper |
| M | docs/orchestrator-playbook.md | DocsAgent | R1/R3/R4/R6/R7/R9/R10/R11 | §3.1 / §6.6/§6.7 / §11 / §12.6 |
| M | agents/ArchitectPLAgent.md | DocsAgent | R4/R8 | Phase 1.5 fail-fast + parallel diagnosis 입력 |
| M | agents/DeveloperPLAgent.md | DocsAgent | R4/R5/R11 | parallel diagnosis 출력 + manifest review-only + fast-path |
| M | agents/TestAgent.md | DocsAgent | R9 | subset arg + 병렬 spawn 절차 |
| M | CLAUDE.md | DocsAgent | R3/R7/R9/R10 sync | 스폰 시퀀스 다이어그램 동기화 |
| M | .gitignore | DocsAgent | R6/R10 | .claude-work/cache/ 추가 |
| M | .claude-plugin/plugin.json | DocsAgent | release | 0.12.0 → 0.13.0 |
| M | CHANGELOG.md | DocsAgent | release | v0.13.0 entry |

## §9. 품질 게이트 이력

§9 lane은 **plugin-meta-na** (ADR-005). 본 CFP는 13 markdown commit이라 production 리뷰/테스트 lane 면제:

- **§9.1 설계 리뷰**: N/A — spec/plan이 audit 결과 반영 (Codex P-1..P-8 + self-audit a..k 합의)
- **§9.2 구현 리뷰**: N/A — 13 commit이 mechanical markdown edit, plan에 anchor 명시
- **§9.3 구현 테스트**: N/A — code 변경 없음. invariant-check.yml 8 step 자동 검증 대체
- **§9.4 보안 테스트**: N/A — code 변경 없음. trust boundary 변화 없음 (cache .gitignore 추가만)

invariant-check.yml 자동 검증으로 SSOT parity 확인 → CI PASS 시 merge.

## §10. FIX Ledger

(plugin-meta-na — FIX lane 미진입)

## §11. 참조

- Spec: [docs/superpowers/specs/2026-04-27-cfp-19-orchestration-parallelization.md](../superpowers/specs/2026-04-27-cfp-19-orchestration-parallelization.md)
- Plan: [docs/superpowers/plans/2026-04-27-cfp-19-orchestration-parallelization.md](../superpowers/plans/2026-04-27-cfp-19-orchestration-parallelization.md)
- 선행 ADR: [ADR-001](../adr/ADR-001-review-agent-unification.md), [ADR-004](../adr/ADR-004-architectpl-securityarch-restructure.md), [ADR-005](../adr/ADR-005-plugin-self-application-na-standardization.md), [ADR-006](../adr/ADR-006-testcontract-architect.md)
- Phase 2 PR: TBD (commit 시점에 추가)
