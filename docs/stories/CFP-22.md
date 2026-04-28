# CFP-22: DesignReview checklist 확장 — Codex audit #4·#5·#6 (관측성·API 호환·SLO)

라벨: `type:story`, `phase:구현`, `plugin-meta-na`

---

## §1. 사용자 요구사항 (verbatim)

> 다음 작업 수행해 (CFP series autonomous progression — Codex audit #4·#5·#6 LOW risk single-file 변경)

## §2. 도메인 해석 (DomainAgent)

ADR-004 §"후속 조치"에서 명시한 Codex audit 후속 #4 (관측성) / #5 (API 호환) / #6 (SLO) 직접 적용. 본래 CFP-20에 묶였으나 CFP-20이 Live Progress Dashboard로 repurpose되어 본 항목 unassigned. v0.11.0 sprint retro §"우선순위 2" LOW risk 평가 항목.

새 deputy 도입 불필요 — 3 항목 모두 기존 §3·§4·§6 영역에 자연스럽게 통합 가능. 체크리스트 audit 항목으로만 추가 (검사 강화).

지식 공백: 없음.

## §3. 관련 ADR

- **ADR-001** (배경 참조 — review unification)
- **ADR-004** §"후속 조치" (직접 제약 — #4·#5·#6 closure)
- **ADR-005** (직접 제약 — plugin-meta-na §8/§9 N/A)

신규 ADR 없음 (checklist 확장은 SSOT 갱신 수준).

## §4. 관련 코드 경로 + 책임

- `templates/review-checklists/design.md` — 3 신규 audit 섹션 + category enum 3개 + severity 자동 룰 P0 3 + P1 3
- `agents/DesignReviewPLAgent.md` — packet category_enum + severity_overrides
- `agents/CodexReviewAgent.md` — lane=design prompt category enum + auto-P0
- `CHANGELOG.md` — v0.14.1 entry
- `.claude-plugin/plugin.json` — 0.14.0 → 0.14.1

## §5. 요구사항 확장 해석 (RequirementsAnalyst)

**유스케이스**:
- (UC-1) §4 API 호환 결정 (versioning / deprecation / consumer 통보) 설계 시점 audit
- (UC-2) §3·§4 관측성 결정 (log·metric·trace + 민감 데이터 redact) 설계 시점 audit
- (UC-3) §3 SLO 결정 (가용성·지연·throughput + 측정·error budget) 설계 시점 audit

**AC**:
- AC-1: ADR 변경 0건 (Non-BREAKING)
- AC-2: invariant-check 8 step PASS — 특히 Step 6 (3 lane category enum parity) + Step 8 (severity_overrides count + breakdown)
- AC-3: 3 신규 카테고리 (`api-compatibility` / `observability` / `slo-missing`) 4 곳 동일 (design.md SSOT + DesignReviewPL + CodexReview)
- AC-4: severity 자동 룰 P0 3건 (조건부 — 공개 API·SLA·boundary만) + P1 3건 추가
- AC-5: plugin.json 0.14.1 ↔ CHANGELOG.md [0.14.1]
- AC-6: design.md "Severity 자동 룰" 절 ↔ DesignReviewPL severity_overrides count + P0/P1 분포 parity

**제외 범위**:
- 새 deputy (DataMigrationArch 패턴 X — checklist만 확장)
- 새 §섹션 (Change Plan template §1-§11 그대로 유지)
- ADR-008 §section ownership model (deferred)

§5.5 사용자 확인 필요: 없음.

## §6. 외부 지식 배경 (Researcher)

외부 지식 보강 불필요. ADR-004 §"후속 조치" + 일반적인 SRE/DevOps 관행 (SLO·observability·API versioning) 충분.

## §7. 설계 서사

**Spec**: [../superpowers/specs/2026-04-28-cfp-22-design-checklist-expansion.md](../superpowers/specs/2026-04-28-cfp-22-design-checklist-expansion.md)
**Plan**: [../superpowers/plans/2026-04-28-cfp-22-design-checklist-expansion.md](../superpowers/plans/2026-04-28-cfp-22-design-checklist-expansion.md)

**§1 목적**: Codex audit #4·#5·#6 closure. shift-left 운영 결정.

**§3 도입할 설계**: design.md "§7 보안 설계 감사" / "§11 데이터 마이그레이션 감사" 패턴 동형으로 3 신규 audit 절 추가. category enum + severity 자동 룰 갱신.

**§4 API 계약**: ReviewPL packet schema 변경 — `category_enum` 3개 추가, `severity_overrides` 6 entries 추가.

**§7 보안 설계 요약**: §7 변화 없음. 관측성 audit가 §7.4 민감 데이터 cross-ref 강화 (log redaction).

**§9 분기 선택 요약**: deputy 추가 안 함 (option C — checklist 확장만). §섹션 신설 안 함 (기존 §3/§4/§6에 통합).

## §8. 개발 서사

§8 lane은 **plugin-meta-na** (ADR-005). 본 CFP는 production code (`src/**`) 변경 없음.

### §8.5 Impl Manifest

| change | path | agent_role | related_change_plan_section | description |
|--------|------|------------|------------------------------|-------------|
| A | docs/superpowers/specs/2026-04-28-cfp-22-design-checklist-expansion.md | DocsAgent | spec | CFP-22 spec |
| A | docs/superpowers/plans/2026-04-28-cfp-22-design-checklist-expansion.md | DocsAgent | plan | CFP-22 plan |
| A | docs/stories/CFP-22.md | DocsAgent | Story doc | Story SSOT |
| M | templates/review-checklists/design.md | DocsAgent | spec §2.1·§2.2·§2.3 | 3 audit + category enum 3 + severity 자동 룰 P0 3 + P1 3 |
| M | agents/DesignReviewPLAgent.md | DocsAgent | spec §2.3 | category_enum + severity_overrides 6 entries |
| M | agents/CodexReviewAgent.md | DocsAgent | spec §2.3 | lane=design prompt category enum + auto-P0 |
| M | .claude-plugin/plugin.json | DocsAgent | release | 0.14.0 → 0.14.1 |
| M | CHANGELOG.md | DocsAgent | release | v0.14.1 entry |

### §8.4 N/A 사유 (ADR-005 plugin-meta-na)

본 CFP는 production code 변경 없음 — 5 markdown 파일만 변경. §8 Test Contract `runtime-inert` + plugin-meta-na 적용.

### §11.6 N/A 사유

본 Story는 데이터 layer 변경 없음 — markdown SSOT 변경만. §11 데이터 마이그레이션 N/A.

## §9. 품질 게이트 이력

§9 lane은 **plugin-meta-na** (ADR-005):

- §9.1 설계 리뷰: N/A — spec/plan이 audit #4·#5·#6 직접 인용
- §9.2 구현 리뷰: N/A — mechanical markdown edit, plan에 anchor 명시
- §9.3 구현 테스트: N/A — code 변경 없음, invariant-check 자동 검증
- §9.4 보안 테스트: N/A — code 변경 없음, trust boundary 변화 없음

## §10. FIX Ledger

(plugin-meta-na — FIX lane 미진입)

## §11. 데이터 마이그레이션

§11.6 N/A — "본 Story는 데이터 layer 변경 없음 — markdown SSOT 변경만, schema 변경 0개".

## §12. 참조

- Spec: [../superpowers/specs/2026-04-28-cfp-22-design-checklist-expansion.md](../superpowers/specs/2026-04-28-cfp-22-design-checklist-expansion.md)
- Plan: [../superpowers/plans/2026-04-28-cfp-22-design-checklist-expansion.md](../superpowers/plans/2026-04-28-cfp-22-design-checklist-expansion.md)
- 선행 ADR: [ADR-004](../adr/ADR-004-architectpl-securityarch-restructure.md), [ADR-005](../adr/ADR-005-plugin-self-application-na-standardization.md)
- PR: TBD
