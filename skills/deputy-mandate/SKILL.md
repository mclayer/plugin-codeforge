---
name: deputy-mandate
description: 6+2 deputy mandate matrix. §7/§11/§13 sub별 ownership (CodebaseMapper·Refactor·SecurityArch·OpRiskArch·TestContractArch·DataMigrationArch + CONDITIONAL LiveOps·LiveOrdering). 설계 lane ArchitectPLAgent deputy spawn 결정 전 Orchestrator 호출 의무.
tools: Read
---

# Deputy Mandate 매트릭스 (codeforge-design lane)

> 참조 테이블 skill — 내용을 읽고 deputy spawn 결정 및 §7/§11/§13 책임 분담에 적용하세요.

## 호출 시점

설계 lane 진입 시. ArchitectPLAgent가 6→8 deputy parallel spawn 여부를 결정하기 전 호출.

## Deputy mandate 매트릭스 — 6 permanent + 2 CONDITIONAL

ADR-014 + ADR-012 §3 4번째 SSOT 예외. design lane deputy가 §7/§11/§13 sub별 owning 범위 명시 — H17 책임 분쟁 차단.

| §7 / §11 / §13 sub | CodebaseMapper | Refactor | SecurityArch | **OpRiskArch** | TestContractArch | DataMigrationArch | **LiveOps** (CONDITIONAL) | **LiveOrdering** (CONDITIONAL) |
|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| §7.1 Trust boundary | — | — | ✅ **(+container network mode / secret mount)** | (consult) | — | — | (consult Live API) | — |
| §7.2 Threat model | — | — | ✅ | — | — | — | — | — |
| §7.3 Auth/authz | — | — | ✅ | — | — | — | (consult operator approval) | — |
| **§7.4 DR / disconnect / rate limit / env isolation** | — | — | (consult) | **✅ (+container restart policy / volume DR / health check / network mode)** | — | — | (consult Live failure) | (consult exchange rate-limit) |
| **§7.4 Clock sync (CONDITIONAL)** | — | — | (consult) | **✅** | — | — | — | — |
| §7.5 민감 데이터 분류 | — | — | ✅ **(+container secret mount / image layer 누설)** | — | — | — | (consult API key) | — |
| §7.6 위협↔완화 매핑 | — | — | ✅ | (DR↔failover consult) | — | — | (consult kill switch) | — |
| **§11 Idempotency (CONDITIONAL)** | — | — | — | (consult) | — | **✅** | — | (consult order idempotency) |
| §11 Schema/Migration/Rollback | — | — | — | — | — | ✅ **(+DB container volume / data persistence)** | — | — |
| **§11 Ledger reconcile / partial fill / fee invariant (CONDITIONAL Live)** | — | — | — | (consult) | — | (consult §11) | — | **✅** |
| **§8.5 Stateful / restart invariant** | — | — | — | (consult §7.4 짝) | **✅** | (consult §11.6 짝) | — | (consult order replay) |
| **§13 Live Operational Discipline (CONDITIONAL Live touching)** | — | — | (consult §7.5) | (consult kill switch) | — | (consult §11) | **✅** | (consult §11 ledger) |

✅ = primary owner / (consult) = secondary input.

## CONDITIONAL deputy 활성 정책 (CFP-77)

- **LiveOpsDeputy + LiveOrderingDeputy** = Live touching Story만 active (real funds / live exchange API / production credential / live order placement 중 하나 이상). Backtest/Paper-only Story = 미spawn.
- ArchitectPLAgent가 Story의 §13 CONDITIONAL trigger 검토 후 6 → 8 deputy parallel spawn 결정.
- 활성 시: ArchitectAgent chief가 8 deputy 산출물 통합.

§7.4 schema 자체는 codeforge-design plugin SSOT. wrapper는 본 매트릭스만 SSOT 보유 ([ADR-014](docs/adr/ADR-014-operational-risk-ssot-distribution.md)).
