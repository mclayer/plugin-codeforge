## 11. Cross-agent write coordination

ζ arc decomposition (CFP-31~CFP-40) 후 wrapper repo 에는 agent 0개. write 책임은 6 lane plugin 으로 분산 (§5.1 표 참조). 결과적으로 wrapper-side `.claude-work/doc-queue/**` 기반 write queue 는 **사용 안 함**. 대신:

- **각 lane plugin 자기 owner section 직접 write** — `Edit` 또는 GitHub MCP 도구 호출 직접 수행
- **Multi-writer 영역의 자연 직렬화** — `docs/stories/<KEY>.md` 의 §1 → §2-§6 → §7 → §8 → §9 → §11 등 phase 진행 순서가 자연 직렬화 보장. concurrent write 충돌은 phase-label-invariant.yml + branch protection 으로 차단
- **§10 FIX Ledger 예외** — Orchestrator 단독 write (CFP-32 monopoly). lane plugin 은 verdict.status=FIX 만 반환 — §10 직접 write 안 함 (`fix-event-v1` contract)

Pre-CFP-32 의 deprecated write queue type (`adr-draft`, `change-plan`, `domain-knowledge`, `ledger-append`) 가 코드에 잔존하면 silent skip — 사용 안 함.

---

