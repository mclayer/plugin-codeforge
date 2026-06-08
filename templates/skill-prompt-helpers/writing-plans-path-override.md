# Skill: superpowers:writing-plans — codeforge family path override

When invoking `superpowers:writing-plans` from codeforge family plugin work, override the default plan save location:

- **Default** (PROHIBITED for codeforge family): `docs/superpowers/plans/YYYY-MM-DD-<feature>-plan.md`
- **Override**: `<internal-docs-clone>/<plugin-folder>/plans/YYYY-MM-DD-<KEY>-<feature>-plan.md`
  - `<internal-docs-clone>` = local clone of `mclayer/codeforge-internal-docs`
  - `<plugin-folder>` = wrapper / requirements / design / review / develop / test / pmo (matching plugin name)
  - `<KEY>` = CFP-NNN of current Story

Pass this as part of the Skill invocation prompt argument. ADR-017 CI lint will reject the default path at PR stage.

**Reference**: [ADR-013](../../archive/adr/ADR-013-codeforge-family-dogfood-out-policy.md) · [ADR-017](../../archive/adr/ADR-017-skill-override-path-enforcement.md) · [Integration SSOT §4](../../docs/superpowers-integration.md)
