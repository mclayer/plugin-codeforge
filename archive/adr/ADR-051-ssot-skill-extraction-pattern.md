---
adr_number: 51
title: SSOT Exception Skill Extraction Pattern
status: Accepted
category: Plugin Architecture
date: 2026-05-13  # Amendment 1 — Draft → Accepted 전환 (CFP-506)
related_files:
  - CLAUDE.md (enforcement 대상)
  - skills/ (skill 파일 위치)
  - .claude-plugin/plugin.json
related_stories:
  - CFP-343 (본 ADR carrier)
  - CFP-506 (Amendment 1 — Draft → Accepted + anchor vs reference 판정자 + 5~9 skill 추출 base pattern + silent dead code 3-층 안전망)
related_adrs:
  - ADR-012  # SSOT boundary — cap 수호 대상 (CFP-506 Amendment 1 cross-ref)
  - ADR-016  # marketplace sync 의무
  - ADR-058  # is_transitional: false 정합 (permanent policy)
  - ADR-060  # CFP-506 Amendment 5 — declaration-only ADR mechanical enforcement framework
  - ADR-064  # decision principle mandate (anchor 분류 source)
  - ADR-040  # Amendment 3 §결정 7.D self-application 패턴 reuse
is_transitional: false
amendment_log:
  - amendment: 1
    carrier_story: CFP-506
    date: 2026-05-13
    summary: |
      status Draft → Accepted 전환 — 선례 4 SSOT skill (review-responsibility / root-cause-decision / fix-ledger-schema / deputy-mandate) 모두 lane 진입 시 ≥2 회 사용 충족 확인 + 본 Story 4 신규 skill (lane-self-write-boundary / story-cutoff-classification / inter-plugin-contract-registry / story-epic-flow-preflight) 추출 = 5~9 번째 사용 사례 (Accepted gate 정합) +
      신설 §결정 4 anchor vs reference 판정자 — "Orchestrator 가 매 turn 자기검열해야 하는가" 가 분류 기준. ADR-051 기존 추출 기준 3종 (≥20줄 / lane-conditional / cap 위반 기여) 과 **AND 관계** (anchor 는 ≥20줄이라도 skill 추출 거부, ResearcherAgent Unknown 1 해소) +
      신설 §결정 5 5~9 번째 skill 추출 base pattern reuse — 본 Story 4 신규 skill 모두 §결정 2 형식 표준 (skills/<slug>/SKILL.md subdirectory) + §결정 4 trigger 명시 의무 정합 +
      신설 §결정 6 silent dead code 회피 메커니즘 3-층 안전망 (CLAUDE.md "Lane 진입 시 skill 호출 의무" 표 row append + skill description frontmatter trigger verbatim + lane plugin agent prompt 안 skill 호출 path 명시) +
      `is_transitional: false` 유지 (permanent policy, ratchet 약화 차단 정합).
---

# ADR-051: SSOT Exception Skill Extraction Pattern

## 상태

**Accepted** (2026-05-13, CFP-506 Amendment 1) — Draft (2026-05-09, CFP-343) 으로부터 전환. 선례 4 SSOT skill (review-responsibility / root-cause-decision / fix-ledger-schema / deputy-mandate) lane 진입 시 ≥2 회 사용 충족 + 본 CFP-506 의 4 신규 skill (5~9 번째 사용 사례) 추출 = Accepted gate 정합.

## 컨텍스트

ADR-012 (CFP-44) 에서 wrapper CLAUDE.md ≤380줄 cap 결정 후 377줄 달성. 이후 CFP들이 content를 반복 추가해 453줄로 cap 초과. CLAUDE.md는 매 대화 턴마다 시스템 컨텍스트로 전체 로드돼 토큰 비용이 증가한다.

CLAUDE.md 내 4개 SSOT 예외 테이블 (~160줄)은 특정 lane 진입 시 또는 FIX 루프 시작 시에만 참조되는 조건부 참조 테이블이다. Claude Code plugin skill 메커니즘을 이용하면 이 테이블들을 on-demand 로딩으로 전환할 수 있다.

**추가 발견**: 기존 `skills/codeforge-brainstorm.md` (flat 파일)이 Claude Code skill discovery 기준에 맞지 않아 system-reminder에 미노출 (동작 안 함). 올바른 형식은 `skills/<slug>/SKILL.md` (subdirectory).

## 결정

1. **Skill extraction 기준**: CLAUDE.md 내 cross-lane 참조 테이블 중 (a) 크기 ≥20줄, (b) 특정 lane 또는 이벤트에서만 참조, (c) inline 존재가 ADR-012 cap 위반 원인인 경우 → skill로 분리.

2. **Skill 형식 표준**: `skills/<slug>/SKILL.md` (subdirectory with SKILL.md) — flat .md 파일 금지.

3. **4개 skill 신설**:
   - `codeforge:review-responsibility` — 책임 매트릭스
   - `codeforge:root-cause-decision` — 원인 판정 decision table
   - `codeforge:fix-ledger-schema` — §10 FIX Ledger 스키마
   - `codeforge:deputy-mandate` — SubAgent mandate matrix

4. **Trigger 명시 의무**: 각 skill description 필드 + CLAUDE.md 오케스트레이션 규칙 섹션 상단 "Lane 진입 시 skill 호출 의무" trigger 테이블에 호출 시점 명시.

5. **Brainstorm skill 형식 정정**: `skills/codeforge-brainstorm.md` → `skills/codeforge-brainstorm/SKILL.md`.

6. **Version bump**: skill 추가 시 반드시 plugin version bump (캐시 반영 필수).

### 결정 7: Anchor vs reference 판정자 (CFP-506 Amendment 1 — Researcher Unknown 1 해소)

ADR-051 추출 기준 3종 (≥20줄 / lane-conditional / inline 존재 ADR-012 cap 위반 원인) 에 신규 판정자 추가:

> **"Orchestrator 가 매 turn 자기검열해야 하는가"**

본 판정자가 분류 결정 기준이다:

- **YES** → **anchor** (CLAUDE.md 본문 inline 유지). skill 추출 거부. 예: forbid-list 8 어휘 (매 발화 어휘 검증) / 4 normative anchor (best-effort / broad coverage / full-scope / active amendment 가치 판정) / sequential 강제 3 사유 / Top-down ratchet (ADR-064 normative SSOT).
- **NO** → **reference / skill 추출 후보**. 추가 검증 = ADR-051 기존 3종 (≥20줄 + lane-conditional + cap 위반 기여) 모두 충족 시 skill 추출. 예: Lane self-write boundary 표 / Story cutoff 분류 표 / Inter-plugin Contract MANIFEST 표 / Story flow + Epic flow + Preflight 표.

**AND 관계 명시**: anchor 가 ≥20줄이라도 (예: 결정 원칙 영역 약 35줄) skill 추출 거부 — 본 판정자가 우선 (CFP-506 Q1 결정 정합). 추출 기준 3종 = NO 진영 안 추가 필터.

**Rationale**: anchor 가 skill 로 잘못 분류되면 lane-conditional lazy load → Orchestrator 자기검열 우회 → 사후 감지 lint 만 의존 (proposing-time enforce 실패). ResearcherAgent Unknown 1 evidence (CFP-506 §6.2) — anchor enforcement path 보전 = inject 가치 우선.

### 결정 8: 5~9 번째 skill 추출 — base pattern reuse (CFP-506 Amendment 1)

본 Story (CFP-506) 4 신규 skill 추출이 ADR-051 의 5~9 번째 사용 사례:

| # | Slug | 추출 영역 (CLAUDE.md 본문) | Trigger (description frontmatter) |
|---|---|---|---|
| 5 | `lane-self-write-boundary` | Lane plugin self-write 책임 표 (현 L302-327) | Lane plugin self-write 영역 lookup 시 (Orchestrator lane spawn 직전 owner path 확인) |
| 6 | `story-cutoff-classification` | Story 작성 의무 cutoff 분류 표 (현 L392-432) | Story 작성 의무 vs chore commit 면제 분류 시 (사용자 요구사항 접수 직후) |
| 7 | `inter-plugin-contract-registry` | Inter-plugin Contract index + Versioning + Write boundary (현 L333-364) | Inter-plugin contract MANIFEST / Versioning / Write boundary lookup 시 (contract version bump / sibling sync 결정) |
| 8 | `story-epic-flow-preflight` | 레인 6개 단계 정의 + Story flow + Epic flow + Preflight 표 (현 L76-118) | Story flow / Epic flow / Cross-repo Epic / Preflight 결정 시 (lane 진입 prerequisite) |

각 skill = 본 ADR §결정 2 형식 표준 (`skills/<slug>/SKILL.md` subdirectory) + 본 ADR §결정 7 trigger 명시 의무 + 본 ADR §결정 6 plugin version bump 의무 (skill 4종 추가 → plugin.json MINOR bump → ADR-063 atomic invariant 발효 → marketplace.json sync 동반 PR).

### 결정 9: Silent dead code 회피 — 3-층 안전망 (CFP-506 Amendment 1 — Researcher Unknown 2 부분 해소)

신규 skill 도입 시 lane plugin agent 가 호출 의무 망각 → boundary drift 가능 (silent dead code risk). 본 결정으로 3-층 안전망 의무화:

1. **1층 (CLAUDE.md "Lane 진입 시 skill 호출 의무" 표 row append)** — 본 표 lookup 만으로 호출 path 확인 가능. 신규 skill 도입 시 row append 의무 (description trigger 컬럼 = skill frontmatter trigger 와 verbatim 정합).
2. **2층 (skill description frontmatter trigger verbatim)** — 각 skill `SKILL.md` frontmatter `description` 필드에 호출 timing 발화 조건 명시. skill discovery 시점 Orchestrator 가 trigger 매칭.
3. **3층 (lane plugin agent prompt 안 skill 호출 path 명시)** — 각 lane plugin agent 의 prompt body 안 `codeforge:<slug>` skill 호출 의무 명시 (예: ArchitectPL prompt §스킬 호출 path → `codeforge:deputy-mandate`). lane plugin self-write 의무 영역.

3-층 모두 부재 시 = silent dead code. DesignReview lane (Phase 1 PR) 책무 = 신규 skill 도입 carrier Story 의 3-층 모두 verify (§9 audit 영역). 추가 sentinel lint (skill 호출 누락 자동 감지) = 별도 follow-up CFP scope (Researcher Unknown 2 추가 해소 경로).

## 결과

**ADR-012 §3 amendment**: 본 결정에 의해 ADR-012 §3 "4 SSOT 예외 항목 (책임 매트릭스 / 원인 판정 decision table / FIX Ledger §10 schema / 6 SubAgent mandate matrix)"은 CLAUDE.md inline 유지에서 skill 분리 방식으로 전환된다. ADR-012 cap(≤380줄) 수호 수단을 확장하는 amendment이며 ADR-012 본문에 cross-reference 추가 권장.

**달성** (Phase 2 구현 완료 후 검증):
- CLAUDE.md ~453 → ~312줄 예측 (ADR-012 ≤380줄 cap 충족, headroom +68줄)
- 4개 skill on-demand 로딩으로 lane 진입 전 불필요 토큰 제거
- Brainstorm skill 미동작 버그 해소

**비용**:
- Orchestrator가 lane 진입 시 skill 호출 의무 (누락 시 테이블 미참조 위험)
- Plugin version bump + 재설치 필요

**향후 확장**:
- 신규 cross-lane 대형 테이블 추가 시 동일 기준 적용 (ADR-012 cap 수호 수단)
- ADR-012 §3 4 SSOT 예외 → "skill로 분리된 참조 테이블" 패턴으로 확장 가능

## 거부된 대안

- **subdirectory CLAUDE.md 분할**: 작업 디렉터리에 따라 로딩 — lane 간 cross-cutting 참조에 적합하지 않음
- **SessionStart hook 조건부 주입**: project.yaml 플래그 기반 — per-lane 조건 표현 불가
- **ADR-012 cap만 낮추기 (linter 추가)**: 증상 억제, 근본 해결 아님

## 해소 기준

N/A — permanent policy

## 관련 파일

- [ADR-012](ADR-012-wrapper-claudemd-ssot-boundary.md) — cap 정책 SSOT
- [ADR-016](ADR-016-marketplace-registration-policy.md) — marketplace sync 의무
- [CFP-343 spec](https://github.com/mclayer/codeforge-internal-docs/blob/main/wrapper/specs/2026-05-09-cfp-343-ssot-skill-extraction-design.md)
