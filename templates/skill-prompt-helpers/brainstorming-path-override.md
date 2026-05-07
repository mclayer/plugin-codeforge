# Skill: superpowers:brainstorming — codeforge family path override

When invoking `superpowers:brainstorming` from codeforge family plugin work, override the default spec save location:

- **Default** (PROHIBITED for codeforge family): `docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md`
- **Override**: `<internal-docs-clone>/<plugin-folder>/specs/YYYY-MM-DD-<KEY>-<topic>-design.md`
  - `<internal-docs-clone>` = local clone of `mclayer/codeforge-internal-docs`
  - `<plugin-folder>` = wrapper / requirements / design / review / develop / test / pmo (matching plugin name)
  - `<KEY>` = CFP-NNN of current Story

Pass this as part of the Skill invocation prompt argument. ADR-017 CI lint will reject the default path at PR stage.

**Reference**: [ADR-013](../../docs/adr/ADR-013-codeforge-family-dogfood-out-policy.md) · [ADR-017](../../docs/adr/ADR-017-skill-override-path-enforcement.md) · [Integration SSOT §4](../../docs/superpowers-integration.md)

---

## Pre-Issue scenario (Stage 0 — [ADR-034](../../docs/adr/ADR-034-pre-issue-brainstorming-stage.md))

Brainstorming 이 codeforge requirements lane **진입 전** 호출되는 경우 (사용자 / consumer Orchestrator 의 scoping draft, [orchestrator-playbook §1.2.0](../../docs/orchestrator-playbook.md)):

- **Consumer project**: spec path = `docs/superpowers/specs/YYYY-MM-DD-<slug>-design.md` (skill default — consumer 는 ADR-017 미적용)
- **Plugin repo dogfood (codeforge family)**: spec path = `<internal-docs-clone>/<plugin-folder>/specs/YYYY-MM-DD-cfp-NNN-<slug>-design.md` ([ADR-013](../../docs/adr/ADR-013-codeforge-family-dogfood-out-policy.md) / [ADR-017](../../docs/adr/ADR-017-skill-override-path-enforcement.md) enforced — default path PROHIBITED)

산출 후 (Stage 0 → Stage 1 hand-off):
1. spec 결론 요약 (≤ 500 char 권장) → story.yml Issue Form `user-original` 필드 (§1 verbatim source — RequirementsPL 입력)
2. spec file path 또는 URL → story.yml Issue Form `spec_link` 필드 (optional, ADR-034 / Phase 2 fixture)

In-lane 시나리오 (DomainAgent / RequirementsPL — 본 fragment 위 본문) 와 별개 — 본 Stage 0 는 사용자 발화 직후 ~ Issue Form 제출 직전 단계. RequirementsPL 가 lane 내부에서 추가 brainstorming 호출 가능 (2 spec 공존 OK, 서로 다른 단계 SSOT).
