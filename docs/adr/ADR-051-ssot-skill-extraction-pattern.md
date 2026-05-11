---
adr_number: 51
title: SSOT Exception Skill Extraction Pattern
status: Draft
category: Plugin Architecture
date: 2026-05-09
related_files:
  - CLAUDE.md (enforcement 대상)
  - skills/ (skill 파일 위치)
  - .claude-plugin/plugin.json
related_stories:
  - CFP-343 (본 ADR carrier)
  - ADR-012 (SSOT boundary — cap 수호 대상)
  - ADR-016 (marketplace sync 의무)
is_transitional: false
---

# ADR-051: SSOT Exception Skill Extraction Pattern

## 상태

Draft (2026-05-09) — CFP-343.

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
   - `codeforge:deputy-mandate` — deputy mandate matrix

4. **Trigger 명시 의무**: 각 skill description 필드 + CLAUDE.md 오케스트레이션 규칙 섹션 상단 "Lane 진입 시 skill 호출 의무" trigger 테이블에 호출 시점 명시.

5. **Brainstorm skill 형식 정정**: `skills/codeforge-brainstorm.md` → `skills/codeforge-brainstorm/SKILL.md`.

6. **Version bump**: skill 추가 시 반드시 plugin version bump (캐시 반영 필수).

## 결과

**ADR-012 §3 amendment**: 본 결정에 의해 ADR-012 §3 "4 SSOT 예외 항목 (책임 매트릭스 / 원인 판정 decision table / FIX Ledger §10 schema / 6 deputy mandate matrix)"은 CLAUDE.md inline 유지에서 skill 분리 방식으로 전환된다. ADR-012 cap(≤380줄) 수호 수단을 확장하는 amendment이며 ADR-012 본문에 cross-reference 추가 권장.

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



- [ADR-012](ADR-012-wrapper-claudemd-ssot-boundary.md) — cap 정책 SSOT
- [ADR-016](ADR-016-marketplace-registration-policy.md) — marketplace sync 의무
- [CFP-343 spec](https://github.com/mclayer/codeforge-internal-docs/blob/main/wrapper/specs/2026-05-09-cfp-343-ssot-skill-extraction-design.md)
