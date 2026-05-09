---
cfp: CFP-343
title: SSOT Exception Skill Extraction
status: Draft
date: 2026-05-09
related_adrs:
  - ADR-012
  - ADR-051
---

# CFP-343: SSOT Exception Skill Extraction — Change Plan

## §1 배경

CLAUDE.md 453줄. ADR-012 cap(≤380줄) 대비 +73줄 초과. 매 턴 시스템 컨텍스트로 전체 로드돼 토큰 비용 과다.

## §2 목표

4개 SSOT 예외 테이블을 codeforge plugin skill로 분리. CLAUDE.md ≤380줄 (목표 ~312줄) 복귀.

## §3 도입할 설계

- `skills/<slug>/SKILL.md` 형식 4개 신설 (subdirectory, not flat file)
- Orchestrator: lane 진입 시 해당 skill 명시 호출 (trigger 테이블 CLAUDE.md 상단 명시)
- 기존 `skills/codeforge-brainstorm.md` → `skills/codeforge-brainstorm/SKILL.md` 형식 정정

## §4 변경 범위

- `skills/` 4개 신설 + 1개 형식 정정
- `CLAUDE.md` 4개 섹션 교체 + trigger 테이블 신설
- `.claude-plugin/plugin.json` version 5.8.0 bump
- `docs/adr/ADR-051-ssot-skill-extraction-pattern.md` 신설

## §5 마이그레이션

N/A — 문서 변경. 하위 호환 (skill 추가, CLAUDE.md 내용 이동).

## §6 리팩터링 선행

없음.

## §7 보안 설계

N/A — 보안 관련 변경 없음.

## §8 Test Contract

- [ ] CLAUDE.md 라인 수 ≤380 확인: `wc -l CLAUDE.md`
- [ ] 이동된 4개 섹션 헤더가 CLAUDE.md에 없음 확인
- [ ] 4개 skill 파일 존재: `ls skills/*/SKILL.md`
- [ ] skill frontmatter name 필드 확인: `grep "^name:" skills/*/SKILL.md`
- [ ] plugin.json version 5.8.0: `grep '"version"' .claude-plugin/plugin.json`

## §9 리뷰 결과

(Phase 1 PR merge 후 기입)

## §10 FIX Ledger

(FIX 발생 시 Orchestrator 기입)

## §11 데이터 마이그레이션

N/A
