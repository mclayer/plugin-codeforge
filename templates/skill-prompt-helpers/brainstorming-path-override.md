# Skill: superpowers:brainstorming — codeforge family path override

When invoking `superpowers:brainstorming` from codeforge family plugin work, override the default spec save location:

- **Default** (PROHIBITED for codeforge family): `docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md`
- **Override**: `<internal-docs-clone>/<plugin-folder>/specs/YYYY-MM-DD-<KEY>-<topic>-design.md`
  - `<internal-docs-clone>` = local clone of `mclayer/codeforge-internal-docs`
  - `<plugin-folder>` = wrapper / requirements / design / review / develop / test / pmo (matching plugin name)
  - `<KEY>` = CFP-NNN of current Story

Pass this as part of the Skill invocation prompt argument. ADR-017 CI lint will reject the default path at PR stage.

**Reference**: [ADR-013](../../docs/adr/ADR-013-codeforge-family-dogfood-out-policy.md) · [ADR-017](../../docs/adr/ADR-017-skill-override-path-enforcement.md) · [Integration SSOT §4](../../docs/superpowers-integration.md)
