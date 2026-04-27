---
key: CFP-18
title: TestContractArchitectAgent 신설 — §8 Test Contract Architect 단독 작성 견제
type: story
status: in-progress
phase: 요구사항
created: 2026-04-27
related_adrs: [ADR-004]
---

## §1 요구사항 원문 (사용자 input — 변경 금지)

ADR-004 후속 — Codex audit #1 (Top-1, High severity) 해소:

**문제**: Change Plan §8 Test Contract는 ArchitectAgent (chief author) 단독 author. 설계 시점 QA 견제 부재 — chief author가 자기 검증 (self-validation) 위험. 보안 설계가 §7으로 분리됐던 ADR-004 패턴과 동형.

**요구**: TestContractArchitectAgent 신설하여 §8 Test Contract author/입력 분담. v0.11.0 새 구조 (ArchitectPL + 4 deputy)의 5번째 deputy로 추가하거나, chief author 산하 sub-author로 분리.

**가치**:
1. shift-left QA — 설계 시점에 Test Contract 견제 → 보안 테스트·구현 테스트 lane FIX 회귀 비용 감소
2. v0.11.0 dogfooding — ADR-004 deputy 추가 패턴의 두 번째 적용으로 SSOT 정합성 검증
3. Codex #1 (Top-1 High) 해소

## §2 도메인 해석 (DomainAgent — 분석 대기)

(요구사항 lane RequirementsPL 스폰 후 작성)

## §3 ADR 정합성 + 신규 ADR 후보

- 기존 ADR-004 (설계 lane 재구조화) 의 후속 적용 — 위반 없음
- **신규 ADR-006 후보**: TestContractArch 도입 결정 (option A: 5번째 deputy / option B: chief author 산하 sub / option C: §8 별도 author 분리). 설계 lane에서 결정.

## §4 변경 영향 코드 경로 (분석 대기)

(요구사항 lane 후 RequirementsPL이 작성)

## §5 통합 요구사항 명세서 (분석 대기)

(RequirementsPL — DomainAgent + Analyst + Researcher 병렬 결과 통합)

## §6 외부 지식 / 선행 사례 (분석 대기)

(Researcher 산출 — TDD 시점 author 분리, contract-first design 등 외부 사례)

## §7 Change Plan 요약 (설계 lane — 작성 대기)

→ docs/change-plans/cfp-18-test-contract-architect.md (설계 lane Phase 1 PR에서 작성)

**§7 보안 설계**: 분석 대기 — SecurityArchitect deputy가 평가. Test Contract author 분리가 trust boundary·credential 흐름에 영향 없을 가능성 높음 (§7.6 N/A 가능성 높음).

## §8 구현 결과 (Phase 2)

→ Phase 2 PR commit history

### §8.5 Impl Manifest

→ Phase 2 PR §8.5 매핑표 commit 후 자동 sub-issue 생성

## §9 리뷰·테스트 결과 (Phase 2)

(설계 리뷰 / 구현 리뷰 / 구현 테스트 / 보안 테스트 결과)

## §10 FIX Ledger

| Iter | 시각 | 레인 | 트리거 | 원인 판정 | 재실행 범위 | RESET? |
|------|------|------|--------|-----------|-------------|--------|

**비어있음**.

## §11 회고 (PMOAgent)

(머지 후 PMOAgent 스폰 시 작성)
