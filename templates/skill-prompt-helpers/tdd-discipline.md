# Skill: superpowers:test-driven-development — codeforge §8 Test Contract 결합

When invoking `superpowers:test-driven-development` from codeforge family plugin work, integrate with codeforge §8 Test Contract:

- **TDD red-green-refactor** → `docs/change-plans/<slug>.md §8 Test Contract` 의 unit / integration / infra / perf 분류
- **§8.5 Stateful / restart invariant** (CFP-47) — 별도 카테고리 (TestContractArchitectAgent applicability 표 valid)
- 각 test → `tests/**` directory, codeforge §8 Test Contract row 와 1:1 매핑

**Skill output → codeforge artifact**:
- TDD test file (failing) → §8 row (unit/integration/infra/perf) + tests/<scope>/test_<name>.py
- Implementation → src/<module>/<name>.py (DeveloperAgent vs QADeveloperAgent 책임 분리: tests/** vs src/**)
- 매 commit 단위 = TDD step 1 (red 단독), step 2 (green 추가), step 3 (refactor — optional)

**Reference**: [Integration SSOT §3 row 3](../../docs/superpowers-integration.md) · [ADR-015 §8.5 Stateful test category](../../docs/adr/ADR-015-stateful-test-category.md)
