# CFP-17: 설계 lane 재구조화 — ArchitectPLAgent + SecurityArchitectAgent 도입

## §1 요구사항 원문 (사용자 input — 변경 금지)

이 세션을 통해 보안 테스트를 수행하고 있다. 그럼 보안 설계를 위한 Agent가 있어야 하지 않을까?
이 참에 이 Agent 구조에서 ArchitectAgent의 역할 공백이 없는지 점검해볼까? codex와 함께해라.
ArchitectPLAgent를 생성하고 architectAgent를 그 아래로 내리고 싶다.

(이하 brainstorming 결과 spec과 plan에 정제됨)

## §2 도메인 해석 (DomainAgent — N/A)

본 Story는 plugin meta change. 도메인 모델 변경 없음.

## §3 ADR 정합성 + 신규 ADR (RequirementsPL → DocsAgent)

- 기존 ADR 위반 없음
- **신규 ADR-004** 발행 (본 Story가 발행) — 설계 lane 재구조화

## §4 변경 영향 코드 경로 (RequirementsPL)

- agents/*.md (신규 2 + 수정 8)
- templates/{change-plan, review-checklists/design, review-pl-base, story-page-structure}.md
- CLAUDE.md, docs/orchestrator-playbook.md, docs/plugin-design.md
- .claude-plugin/plugin.json, CHANGELOG.md, README.md
- docs/adr/ADR-004-architectpl-securityarch-restructure.md (신규)
- docs/migration-guide.md

## §5 통합 요구사항 명세서 (RequirementsPL — Codex 감사 통합)

→ docs/superpowers/specs/2026-04-27-cfp-17-architectpl-securityarch-design.md (commit 8c12c5d)

## §6 외부 지식 / 선행 사례 (Researcher — N/A)

본 Story는 plugin self-application. 외부 라이브러리·표준 의존 없음.

## §7 Change Plan 요약 (Architect chief author 미러링)

→ docs/change-plans/cfp-17-architectpl-securityarch.md (Phase 1 PR에서 작성)

**§7 보안 설계**: N/A — agent md / template / docs 변경. 외부 입력·인증·민감데이터 흐름 변경 0개. trust boundary 변경 없음. (CLAUDE.md "Plugin 자체 적용 dogfooding" 패턴)

## §8 구현 결과 (Phase 2)

→ Phase 2 PR commit history

### §8.5 Impl Manifest

→ Phase 2 PR §8.5 매핑표 commit 후 `subissue-from-impl-manifest.yml` Action이 자동 sub-issue 생성

## §9 리뷰·테스트 결과 (Phase 2)

- 설계 리뷰: DesignReviewPL — §7 N/A 사유 검사
- 구현 리뷰: CodeReviewPL — docs/agents/templates 일관성·SSOT drift
- 구현 테스트: TestAgent — N/A (실행 가능 코드 0). invariant-check workflow 자동 검증
- 보안 테스트: SecurityTestPL — N/A (코드 0). 1차 layer 자동 통과

## §10 FIX Ledger

| Iter | 시각 | 레인 | 트리거 | 원인 판정 | 재실행 범위 | RESET? |
|------|------|------|--------|-----------|-------------|--------|

**비어있음**.

## §11 회고 (PMOAgent)

**Sprint-level 회고**: [`docs/retros/2026-04-27-v0.11.0-sprint-close.md`](../retros/2026-04-27-v0.11.0-sprint-close.md) 참조 (CFP-1~17 통합 회고).

### 본 Story (CFP-17) 핵심 결정 sentinel

- **ADR-004 발행**: 설계 lane 재구조화 — ArchitectPLAgent (PL/judge) + ArchitectAgent (chief author) + 3 deputy (Mapper / Refactor / SecurityArch) 4인 체제
- **Change Plan §7 보안 설계 신설**: SecurityArchitectAgent 산출물 (trust boundary / STRIDE-LITE / Auth/Authz / 민감 데이터 / 위협↔완화 / N/A 권한) 통합 슬롯
- **Codex #7 ADR draft 책임 명문화**: chief author가 신규 ADR draft author
- **Self-application paradox 처리 성공**: CFP-17 자체는 옛 구조로 진행, merge 직후부터 새 구조 발효
- **22 core 에이전트** (20 → 22, +ArchitectPLAgent +SecurityArchitectAgent)

### Sprint 결과
- v0.11.0 cut: PR #50 (main) + PR #52 (post-merge CI fix) + PR #53 (final review polish) 모두 main 머지
- main CI 모두 SUCCESS (invariant-check + lint + test)
- 후속 후보: CFP-18 (TestContractArchitect, Codex #1) 우선, CFP-20 (DesignReview checklist 확장, Codex #4-#6) 차순 — sprint retro §2.3 권고

### Phase 2 후속 분리
- Codex #1 → CFP-18 (다음 Story)
- Codex #2 → CFP-19 (deferred — DB 없는 plugin 부담)
- Codex #4·#5·#6 → CFP-20 묶음 (LOW risk)
