# CLAUDE.md (codeforge-test)

codeforge ζ arc Test lane plugin. TestAgent 단독 + owner doc 부재 (가장 단순한 lane).

## Plugin position

본 plugin 은 codeforge wrapper 의 dependency. 단독 동작 불가 — codeforge core (>= 3.0.0).

## Inter-plugin contracts

- `test_verdict v1` — [`docs/inter-plugin-contracts/test-verdict-v1.md`](docs/inter-plugin-contracts/test-verdict-v1.md) (canonical SSOT)

## Self-write 책임

| Path | 트리거 | Mechanism |
|---|---|---|
| GitHub comment `[구현-테스트]` prefix | 모든 실행 | `mcp__github__add_issue_comment` |
| `phase:구현-테스트` → `phase:보안-테스트` transition | PASS only | `mcp__github__issue_write` |

Story §10 FIX Ledger append 는 **Orchestrator 단독** (codeforge core CFP-32 monopoly). TestAgent 는 verdict 에 `fix_routing_hint` 첨부만.
