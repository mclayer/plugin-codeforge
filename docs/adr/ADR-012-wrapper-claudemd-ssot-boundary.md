---
adr_number: 12
title: Wrapper CLAUDE.md SSOT Boundary
status: Adopted
category: Team & Process
date: 2026-04-30
related_files:
  - CLAUDE.md (본 ADR 의 enforcement 대상 + 5-line summary inline)
  - docs/superpowers/specs/2026-04-30-cfp-44-wrapper-claudemd-ssot-compression-design.md (parent CFP)
related_stories:
  - CFP-44 (본 ADR 신설 시점 — wrapper CLAUDE.md 705→~330줄 압축)
  - CFP-43 (parent — X2 cleanup, 잔존 부속 사항 진단의 직전 상태)
  - ADR-009 (parent ζ arc decomposition — 6 lane plugin 추출)
---

# ADR-012: Wrapper CLAUDE.md SSOT Boundary

## 상태

Adopted (2026-04-30) — CFP-44 PR-4 머지 시점.

## 컨텍스트

CFP-43 (X2 cleanup) 후 wrapper CLAUDE.md 가 705줄로 잔존. 사용자 진단:

> "분리를 수행했지만 부속 사항이 너무 많이 남아있는 것 같다."

증상: ζ arc decomposition (ADR-009) 으로 6 lane plugin 추출 완료됐지만, wrapper CLAUDE.md 에 lane 내부 디테일 (agent 역할 · spawn sequence · ideology · lifecycle · severity rule 등) 잔존. 의도된 SSOT 분업이 아니라 추출 시 미처 옮기지 못한 부속.

CFP-44 brainstorming 단계의 audit 결과:
- 1 MISSING (codeforge-test) + 2 PARTIAL critical (design, requirements) — backfill 의무
- 3 PARTIAL safe (review, pmo, develop) — wrapper 압축 무손실
- 3 wrapper-must-keep (cross-lane scope, single-plugin home 없음): 책임 매트릭스 + 원인 판정 decision table + FIX Ledger §10 schema

Codex (gpt-5.4) 두 번째 의견 — A1' (audit-driven minimum + explicit boundary statement) 권고: "process symmetry 만 사고 risk reduction 못 사는 거래" 회피.

## 결정

Wrapper plugin (codeforge) CLAUDE.md content scope 는 다음으로 strictly limited:

1. **Plugin identity** — 인트로, marketplace cross-repo sync 의무, 세션 개시 dependency check
2. **Cross-cutting policy** — dogfood Story 작성 의무, write boundary table (Lane plugin self-write boundary), inter-plugin contract index, ADR list
3. **3 named SSOT exceptions** (cross-lane scope, no single-plugin home):
   - Design / Code / Security 책임 매트릭스
   - 원인 판정 decision table
   - FIX Ledger §10 schema + Orchestrator monopoly + RESET 룰

**Excluded** (lane plugin SSOT 또는 playbook 으로 위임):
- per-lane spawn detail · agent role description
- lane-internal ideology · lifecycle · Freshness rule
- severity rule detail (codeforge-review templates SSOT)
- 병렬 스폰 권장 (spawn sequence 중복)
- GitHub workflow subsection 상세 (consumer-guide.md + label-registry-v1.md SSOT)

CLAUDE.md 본문 top (intro 직후) 에 본 ADR 의 5-line summary + ADR link inline 명시 — drift detection anchor.

## 결과

**달성**:
- CLAUDE.md 705 → 377줄 (47% 절감, 매 세션 ~7k tokens 절약). 첫 추정 330줄은 cross-cutting policy 잔류량 underestimate — bottom-up 재계산 후 ≤380 cap 내 377줄로 수렴
- "wrapper-only" 정체성 명확화 — composition + cross-cutting policy only
- 3 SSOT 예외 명시로 cross-lane 콘텐츠의 단일 출처 보장
- 미래 wrapper drift 의 anchor — boundary 위반 PR 의 review 시 ADR-012 reference

**비용**:
- 3 cross-repo backfill PR (codeforge-{test, design, requirements}) — audit gap 해소
- ADR-012 자동 강제 수단 부재 (linter 후속 CFP)
- documentation-quality asymmetry — lane plugin 별 self-contained 깊이 차이 (review/pmo/develop 는 agent md 영역 의존)

**검증**:
- 압축 후 CLAUDE.md line count = 377 (target 330 미달, ≤ 380 cap 충족)
- §5.2 grep test (CFP-44 spec): 압축 대상 헤더 잔존 0
- ADR-012 frontmatter + section schema PASS

## 거부된 대안

- **A2 symmetric refresh** (CFP-43 패턴 답습, 6 cross-repo PR) — Codex 명시 reject: "process symmetry 만 사고 risk reduction 못 사는 거래"
- **A3 wrapper-only quick-win** (1 PR, lane plugin gap deferral) — ADR 급 결정 의도 (사용자 (2') 선택) 미달성, 결과 ~500줄 (target 미달)
- **Linter-first ratchet** (boundary 정의 없이 자동 강제만 도입) — 강제할 boundary 가 정의돼 있어야 lint rule 작성 가능. 후속 CFP 에서 도입 가능

## 다이어그램

```
Before (CFP-43 후, 본 ADR 결정 전):
codeforge wrapper CLAUDE.md (705 lines)
├── Plugin identity
├── 세션 개시 의무
├── Development Agent Team tree (52 lines, lane internal)
├── 레인 정의
├── 스폰 시퀀스 (91 lines, lane internal)
├── FIX 루프 + 원인 판정 table
├── 책임 매트릭스
├── 4-way 이념 (lane internal)
├── ArchitectPL 라이프사이클 (lane internal)
├── Deputy Freshness (lane internal)
├── Lane plugin self-write boundary
├── 병렬 스폰 권장 (duplicates spawn sequence)
├── Inter-plugin Contract index
├── ADR list
├── GitHub Workflow (89 lines, mostly in consumer-guide)
├── Story 작성 의무 (dogfood policy)
└── Domain Knowledge (lane internal)

After (CFP-44 머지 후):
codeforge wrapper CLAUDE.md (377 lines)
├── Plugin identity (KEEP)
├── ## SSOT Boundary (NEW — ADR-012 5-line + link)
├── 세션 개시 의무 (compressed — checklist 만)
├── Lane → plugin → agent count (10-line table, replaces 52-line tree)
├── 레인 정의 (compressed)
├── Spawn sequence pointer → playbook §3
├── FIX 루프 (trigger/counter/§10 schema only)
├── 원인 판정 decision table (KEEP — SSOT 예외 #2)
├── 책임 매트릭스 (KEEP — SSOT 예외 #1)
├── PMOAgent Cross-cutting trigger (compressed)
├── Lane plugin self-write boundary (KEEP)
├── Inter-plugin Contract index (KEEP)
├── ADR list (compressed)
├── GitHub Workflow (compressed listing only)
├── Story 작성 의무 (KEEP — dogfood policy)
└── docs/stories markdown 규약 (KEEP)
```

## 관련 파일

- 본 ADR
- [CFP-44 spec](../superpowers/specs/2026-04-30-cfp-44-wrapper-claudemd-ssot-compression-design.md)
- CLAUDE.md (본 ADR 의 enforcement 대상)
- [ADR-009 Wrapper-only Decomposition](ADR-009-wrapper-only-decomposition.md) — parent ζ arc 결정
- [ADR-010 Inter-plugin Contract Sibling Sync](ADR-010-inter-plugin-contract-sibling-sync.md) — sibling cleanup arc
