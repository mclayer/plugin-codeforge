---
adr_number: 28
title: Superpowers integration policy — codeforge family wrapping mechanism
status: Accepted
category: Team & Process
date: 2026-05-05
related_files:
  - CLAUDE.md
  - docs/superpowers-integration.md
  - docs/adr/ADR-013-codeforge-family-dogfood-out-policy.md
  - docs/adr/ADR-017-skill-override-path-enforcement.md
  - templates/skill-prompt-helpers/
  - scripts/check-superpowers-integration.sh
  - templates/github-workflows/superpowers-integration.yml
related_stories:
  - CFP-113
---

# ADR-028: Superpowers integration policy

## 상태

Accepted (2026-05-05) — CFP-113 carrier.

## 컨텍스트

`superpowers@claude-plugins-official` 은 codeforge family 의 필수 의존이지만, 통합 표면이 4 위치에 산재 (CLAUDE.md / check_bootstrap.py / playbook §1.1 / consumer-guide §0b) + 17 lane agent file 의 prose reference + 4 agent (3 ReviewPL + PMOAgent) 의 stale `docs/superpowers/**` 권한. trust-based 산재 상태로 4 결함 (Skill→codeforge contract 부재 / prose 일관성 결여 / stale legacy path / trust-based override) 노출.

본 ADR 은 [CFP-113 spec](../../../codeforge-internal-docs/wrapper/specs/2026-05-05-cfp-113-superpowers-integration-wrapping-design.md) (Sonnet decider Option B 채택, Codex 3 mod + Sonnet 2 mitigation 통합) 의 정책 결정을 SSOT 로 기록.

## 결정

### 결정 1: Integration SSOT 위치 = wrapper `docs/superpowers-integration.md`

본 wrapper repo 의 `docs/superpowers-integration.md` 가 codeforge ↔ superpowers 통합 단일 진실원. lane plugin CLAUDE.md / agent md 는 본 doc 을 link 로 참조 — **정책 재정의 금지**. drift 시 wrapper 가 authoritative.

### 결정 2: Invocation contract level = checklist 표

`docs/superpowers-integration.md §2` 가 17 agent × 7 skill 호출 지점 enumerate. 각 row = (Lane / Agent / Trigger / Skill / Path override 필요 / I/O / Phase target). 변경 시 본 표 + lane plugin agent md 동시 갱신 (CI lint drift detection check 1).

### 결정 3: Path override 강제 = ADR-017 CI + skill-prompt-helpers fragment

**선제** (prompt-time): `templates/skill-prompt-helpers/` 4 fragment 가 Skill 호출 prompt 에 inline reference. **사후** (PR-time): ADR-017 + Amendment 1 fail-closed lint. pre-commit hook 미도입 (cost vs benefit 낮음, ADR-017 CI 가 충분).

### 결정 4: skill→codeforge artifact 변환 = integration doc 변환 표

`docs/superpowers-integration.md §3` 변환 표가 7 skill × codeforge artifact 매핑 SSOT. 각 lane plugin template 의 mapping 파일 신규 X (over-engineering 방지, 결정 1 정합 — 단일 SSOT).

### 결정 5: skill-prompt-helpers 소유권 = wrapper-owned, lane import-only

`templates/skill-prompt-helpers/` 는 wrapper (mclayer/plugin-codeforge) 소유. lane plugin 의 agent md 는 `Read(${CLAUDE_PLUGIN_ROOT}/codeforge/templates/skill-prompt-helpers/<fragment>.md)` 패턴으로 link only — **inline copy 금지** (CI lint check 3 fail-closed). 수정 제안 = wrapper PR 경유.

### 결정 6: Phase 2-7 lane plugin batch open + Epic close criteria

Phase 1 wrapper PR merge 시 6 lane CFP 일괄 open (batch). Epic close criteria 에 "6 lane CFP 중 N 완료" 명기. partial consistency 가시성 확보 (Sonnet mitigation #1).

각 lane CFP 의 acceptance criteria 에 stale `docs/superpowers/**` 권한 정리 **필수** 포함 (Codex mod #1 — optional 후속 처리 금지).

## 결과

긍정:
- 4 결함 모두 정리 (contract / prose / stale path / override)
- third-party schema 변경 시 (superpowers 자체 수정) 영향 표면 = wrapper SSOT 1 위치만 (loose coupling)
- contributor onboarding: superpowers ↔ codeforge 관계 1 doc 으로 즉시 이해 가능

부정:
- 17 agent md prose 갱신 = 6 lane plugin per-CFP 작업 필요 (Phase 2-7)
- skill-prompt-helpers/ inline reference 패턴이 lane agent md 에 추가됨 — 약간의 verbosity

Trade-off: Phase 1 wrapper PR 후 lane CFP 미진행 시 partial consistency. 결정 6 (batch open + Epic close criteria 명시) 로 가시성 확보.

## 거부된 대안

- **A (Light, doc consolidation only)** — 결함 #2 (17 agent prose 일관성) 미해결, structural debt 누적
- **C (Heavy, adapter pattern)** — superpowers third-party schema 변경 시 7 adapter 일괄 갱신 의무 = robustness 역효과 명백
- **pre-commit hook** — overhead 대비 benefit 낮음 (ADR-017 CI 가 충분, 본 CFP scope 제외, 후속 CFP 가능)

## 관련 파일

- `CLAUDE.md`
- `docs/superpowers-integration.md`
- `docs/adr/ADR-013-codeforge-family-dogfood-out-policy.md`
- `docs/adr/ADR-017-skill-override-path-enforcement.md` (Amendment 1 동시 발의)
- `templates/skill-prompt-helpers/`
- `scripts/check-superpowers-integration.sh`
- `scripts/test-check-superpowers-integration.sh`
- `templates/github-workflows/superpowers-integration.yml`
