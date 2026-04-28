# CLAUDE.md (codeforge-design)

codeforge ζ arc Design lane plugin (LAST extraction). 7 agent + change-plan/adr templates.

## Plugin position

codeforge core (>= 5.0.0) 의존.

## Inter-plugin contracts

- `design_output v1` — [`docs/inter-plugin-contracts/design-output-v1.md`](docs/inter-plugin-contracts/design-output-v1.md)

## Owner doc paths

- `docs/change-plans/**` — ArchitectAgent direct write (CFP-26 Phase 0a 보존)
- `docs/adr/**` — ArchitectAgent direct write (CFP-26 Phase 0a 보존)

## Self-write 책임

| Path | 책임 agent |
|---|---|
| `docs/change-plans/<slug>.md` | ArchitectAgent |
| `docs/adr/ADR-NNN-<slug>.md` | ArchitectAgent |
| `docs/stories/<KEY>.md §3 ADR list mirror` | ArchitectAgent |
| `docs/stories/<KEY>.md §7 보안 설계 mirror` | ArchitectAgent |
| `docs/stories/<KEY>.md §11 데이터 마이그레이션 mirror` | ArchitectAgent |
| GitHub comment `[설계]` prefix | ArchitectPLAgent |
| `phase:설계` → `phase:설계-리뷰` transition | ArchitectPLAgent |

## 5 Deputy 4-way 이념 대립

ArchitectPLAgent 가 5 deputies 병렬 spawn — 각자 독립 관점:
- CodebaseMapperAgent (보수)
- RefactorAgent (혁신)
- SecurityArchitectAgent (위협)
- TestContractArchitectAgent (Test Contract author input)
- DataMigrationArchitectAgent (데이터 무결성 author input)

ArchitectAgent (chief author) 가 통합 + ArchitectPLAgent 가 메타-규칙 검수.

상세는 codeforge wrapper CLAUDE.md "ArchitectPL deputies" 섹션 참조.
