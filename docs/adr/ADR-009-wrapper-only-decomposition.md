---
adr_number: 9
title: Wrapper-only core + writer-distributed lane plugins (ζ arc decomposition)
status: Adopted
category: Team & Process
date: 2026-04-29
related_files:
  - docs/superpowers/specs/2026-04-29-cfp-31-wrapper-only-decomposition-design.md (parent design)
  - docs/inter-plugin-contracts/comment-prefix-registry-v1.md
  - docs/inter-plugin-contracts/label-registry-v1.md
  - docs/inter-plugin-contracts/fix-event-v1.md
  - docs/inter-plugin-contracts/review-verdict-v1.md (Archived)
  - docs/inter-plugin-contracts/review-verdict-v2.md
is_transitional: false
---

## 상태

Adopted (2026-04-29) — CFP-41 ζ arc 회고에서 Proposed → Accepted → Adopted 전환. 6 lane plugin 추출 + DocsAgent 해체 + writer-distributed model 모두 실 적용 완료.

## 컨텍스트

ε arc (CFP-25 ~ CFP-29) 가 review subsystem 1개를 별도 plugin (codeforge-review) 으로 추출해 plugin 분리 패턴을 처음 검증했지만, codeforge core 는 여전히 19 core 에이전트 + 7 lane 구조를 보유. 사용자 진단:

> "core 가 아직도 너무 크다. 변경 시 결합·역할 모호 발생. CFP-18 (TestContractArch) · CFP-21 (DataMigrationArch) deputy 추가가 매번 5+ 파일을 흔든 게 통증의 원인."

CFP-25 §10.1 "DocsAgent 영구 fixture" 결정 + §3.5 "DeveloperAgents overlay 충분, 분리 안 함" 결정이 ε arc 모델의 잔존 통증을 인정한 것이지만 wrapper-only 끝까지 가지 않은 결과.

## 결정

ζ arc (CFP-31 parent design ~ CFP-40 last extraction + CFP-41 retro) 는:

1. **codeforge core 를 wrapper-only 로 수렴** — agent 0개. Orchestrator (top-level Claude 세션) + playbook + CI workflow yaml + cross-plugin schema templates + inter-plugin contracts SSOT 만 보유
2. **6 lane plugin 신설/retrofit**:
   - `codeforge-review` (CFP-29 추출 + CFP-35 v2 retrofit) — Self-write 첫 검증
   - `codeforge-pmo` (CFP-36 신설) — 코드 이전 첫 사례
   - `codeforge-requirements` (CFP-37 신설) — 4 sub-agent + Domain KB owner write
   - `codeforge-test` (CFP-38 신설) — 가장 단순한 lane (1 agent)
   - `codeforge-develop` (CFP-39 신설) — 5 agent + presets
   - `codeforge-design` (CFP-40 신설, LAST) — 7 agent + change-plan/adr templates
3. **Writer-distributed model**: 각 lane plugin 이 자기 lane Story file § + GitHub comment + phase/gate label 직접 write. DocsAgent 단계적 해체 → CFP-40 시점 file 최종 삭제
4. **Foundation 사전 구축** (CFP-32-34): invariant SSOT 3종 (comment-prefix · label · fix-event) + contract harness + workflow yaml fixture tests + marketplace sync drift detection
5. **Codex round 2 sequencing 권고 채택**: design 가장 마지막 추출 (가장 큰 표면, split-brain 위험 회피)

## 결과

**달성**:
- core agent 19 → 0 (wrapper-only)
- 새 deputy/template 추가 시 wrapper 무손상 (CFP-18·CFP-21 통증 패턴 종결)
- 각 lane 의 자율 진화 가능 (independent release cadence)
- consumer 측 lane 단위 opt-out 가능 (예: PMO 미사용 시 codeforge-pmo 제외)
- Inter-plugin contract 6종 + invariant SSOT 3종 + harness 자동 검증

**비용**:
- 누적 5 wrapper BREAKING bump (v0.22 → v1 → v2 → v3 → v4 → v5)
- 7 plugin marketplace sync (CFP-24 정책) — 자동화 (CFP-34 deliverable) 로 sustainable
- 6 신규 inter-plugin contract — 각각 ADR-008 versioning 룰 적용
- DocsAgent 해체로 일반 docs/** writes 가 Orchestrator 직접 처리로 이동 (top-level 세션 path-scoped 권한 무관)

**검증**:
- 가상 시나리오 "새 architect deputy 추가" — codeforge-design 안에서만 변경, wrapper 무손상 ✓
- 가상 시나리오 "새 role:dev (예: ML Engineer)" — codeforge-develop preset 추가, wrapper 무관 ✓
- 모든 lint (10종) PASS — invariant SSOT + contract harness + workflow fixture + marketplace drift

## 거부된 대안

- **payload-only model** (CFP-25 review 패턴 답습) — DocsAgent 가 verdict 받아 write. 거부: 사용자 wrapper-only 채택 시 모든 lane이 self-write 일관 필요
- **agent-cluster split** (Codex round 1 1차 권고) — arch-deputies 만 분리 + ArchitectAgent chief + ArchitectPL 잔류. 거부: 명목상 decoupling 이지 새 deputy 추가 시 여전히 core SSOT 흔듦 (Codex round 1 후반 자기 판정으로 lane-coherence 우위)
- **DocsAgent 영구 fixture** (CFP-25 §10.1) — overrule. 모든 invariant 가 단일 agent 가 아니라 CI Action + phase label single-active 으로 enforcement
- **DeveloperAgents overlay 충분 잔류** (CFP-25 §3.5 + Codex round 2) — overrule. wrapper-only end-state 일관성 위해 codeforge-develop 으로 추출
- **Big-bang single CFP** — 6 plugin 동시 추출. 거부: 1 contract 1 CFP 데이터 (CFP-29) 무시 + ADR-008 manual versioning 한계 초과
- **Foundation CFP 압축** (F1+F2+F3 → 1 CFP) — 거부: 검증 신호 분리 불가 (Codex round 2 명시)

## 해소 기준

N/A — permanent policy



```
Before (ε arc 후, CFP-31 시점):
codeforge core (19 agents)
├── DocsAgent (영구 fixture)
├── PMOAgent (Cross-cutting)
├── 7 architect/deputy
├── 4 requirements
├── 5 develop
├── 1 test
└── (review 5 agent — codeforge-review plugin)

After (ζ arc 완료, CFP-40+ 시점):
codeforge core (wrapper-only, agent 0개)
├── orchestrator-playbook.md
├── CLAUDE.md (composition spec)
├── templates/{github-workflows,story-page-structure,impl-manifest,...}
├── docs/inter-plugin-contracts/
│   ├── comment-prefix-registry-v1.md
│   ├── label-registry-v1.md
│   ├── fix-event-v1.md
│   ├── review-verdict-v1.md (Archived)
│   ├── review-verdict-v2.md (sibling)
│   ├── requirements-output-v1.md (sibling)
│   ├── design-output-v1.md (sibling)
│   ├── develop-output-v1.md (sibling)
│   ├── pmo-output-v1.md (sibling)
│   └── test-verdict-v1.md (sibling)
├── docs/adr/ (ADR-001 ~ ADR-009)
├── scripts/ (10 lint + bootstrap)
└── 6 lane plugin 의존:
    ├── codeforge-review (5 agent + base + 3 checklist)
    ├── codeforge-pmo (PMOAgent)
    ├── codeforge-requirements (4 agent + domain-knowledge.md)
    ├── codeforge-test (TestAgent)
    ├── codeforge-develop (5 agent + presets/)
    └── codeforge-design (7 agent + change-plan.md + adr.md)
```

## 관련 파일

- 본 ADR
- [CFP-31 parent design](https://github.com/mclayer/codeforge-internal-docs/blob/main/wrapper/specs/2026-04-29-cfp-31-wrapper-only-decomposition-design.md)
- [CFP-32 ~ CFP-40 CHANGELOG entries](../../CHANGELOG.md)
- [docs/retros/2026-04-29-zeta-arc-completion.md](https://github.com/mclayer/codeforge-internal-docs/blob/main/wrapper/retros/2026-04-29-zeta-arc-completion.md) — ζ arc 종합 회고
- [ADR-008](ADR-008-inter-plugin-contract-versioning.md) — Inter-plugin Contract Versioning (ζ arc 의존성)
