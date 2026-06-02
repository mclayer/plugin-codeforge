# Skill: superpowers:verification-before-completion — codeforge gate label 결합

When invoking `superpowers:verification-before-completion` from codeforge family plugin work, integrate with codeforge gate label discipline:

- **체크리스트 빠짐 방지** → `review-verdict-v4` packet schema 의 `evidence` column populate
- **Lane gate label**: `gate:design-review-pass` (DesignReviewPL) / `gate:security-test-pass` (SecurityTestPL) — Sonnet decider final pick 후 Orchestrator self-write
- **Story §9 evidence**: lane iteration result append

**Skill output → codeforge artifact**:
- Verification checklist 결과 → review-verdict-v4 packet 의 findings[].evidence
- PASS 판정 → gate label apply + phase transition
- FIX 판정 → Story §10 FIX Ledger row append (decider:claude_sonnet)

**Reference**: [Integration SSOT §3 row 5](../../docs/superpowers-integration.md) · [ADR-022 Sonnet decider](../../docs/adr/ADR-022-sonnet-review-verdict-decider.md) · [review-verdict-v4](../../docs/inter-plugin-contracts/review-verdict-v4.md)
