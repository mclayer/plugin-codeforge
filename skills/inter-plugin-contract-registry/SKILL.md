---
name: inter-plugin-contract-registry
description: Inter-plugin contract MANIFEST / Versioning / Write boundary lookup 시 (contract version bump / sibling sync 결정). kind:contract 6 entry / kind:registry 5 file / versioning + write boundary 규칙을 정의한다.
tools: Read
---

# Inter-plugin Contract Registry (CFP-29 Phase 1 후 + CFP-42 sibling backfill)

> 참조 테이블 skill — contract version bump / sibling sync 결정 직전 MANIFEST / Versioning / Write boundary 를 확인하세요.

codeforge core 가 외부 plugin과 통신할 때의 typed schema. wrapper repo 의 [docs/inter-plugin-contracts/](docs/inter-plugin-contracts/) 디렉터리는 두 종류 보유:

## kind:contract (typed inter-plugin schema, 6 entry / 8 file)

[docs/inter-plugin-contracts/MANIFEST.yaml](docs/inter-plugin-contracts/MANIFEST.yaml) 가 SSOT. lint 는 [scripts/check-inter-plugin-contracts.sh](scripts/check-inter-plugin-contracts.sh).

| Contract | Producer plugin | Files (wrapper sibling) |
|---|---|---|
| `review_verdict` | codeforge-review | review-verdict-v1.md (Archived) · review-verdict-v2.md (Archived) · [review-verdict-v3.md](docs/inter-plugin-contracts/review-verdict-v3.md) (Archived — CFP-137) · [review-verdict-v4.md](docs/inter-plugin-contracts/review-verdict-v4.md) (Active — CFP-137 / ADR-044) |
| `requirements_output` | codeforge-requirements | requirements-output-v1.md (Active) |
| `design_output` | codeforge-design | design-output-v1.md (Archived) · design-output-v2.md (Active — §7.4 + §11 idempotency, CFP-46) |
| `develop_output` | codeforge-develop | develop-output-v1.md (Active) |
| `test_verdict` | codeforge-test | test-verdict-v1.md (Archived) · [test-verdict-v2.md](docs/inter-plugin-contracts/test-verdict-v2.md) (Active — CFP-367 / ADR-055) |
| `pmo_output` | codeforge-pmo | pmo-output-v1.md (Active) |

각 wrapper sibling 은 lane plugin canonical 의 verbatim mirror + "**상위 SSOT 위치**" 섹션. canonical 변경 시 wrapper sibling sync PR 후속 의무 ([ADR-010](docs/adr/ADR-010-inter-plugin-contract-sibling-sync.md)).

## kind:registry (cross-cutting protocol, 5 file)

wrapper-owned. 본 lint scope 밖 — `check-doc-frontmatter.sh` + `check-doc-section-schema.sh` 가 검증.

- [comment-prefix-registry-v1.md](docs/inter-plugin-contracts/comment-prefix-registry-v1.md) — 11 phase prefix taxonomy
- [fix-event-v1.md](docs/inter-plugin-contracts/fix-event-v1.md) — Story §10 FIX Ledger writer monopoly (v1.1 — CFP-391 `debate_artifact_ref` optional 필드)
- [label-registry-v1.md](docs/inter-plugin-contracts/label-registry-v1.md) — phase/gate/fix label taxonomy (Archived — CFP-140) / [label-registry-v2.md](docs/inter-plugin-contracts/label-registry-v2.md) (Active — ADR-049, v2.4 — CFP-506 `hotfix-bypass:claude-md-line-cap` 8번째 family member)
- [debate-protocol-v1.md](docs/inter-plugin-contracts/debate-protocol-v1.md) — Codex↔Opus multi-round adversarial debate protocol (lane-agnostic, CFP-391 / ADR-059)
- [evidence-check-registry-v1.md](docs/inter-plugin-contracts/evidence-check-registry-v1.md) (v1.1 — Active) — evidence-enforceable governance check schema (CFP-389 / ADR-060). registry data SSOT = [`docs/evidence-checks-registry.yaml`](docs/evidence-checks-registry.yaml).

## Versioning + Write boundary

Versioning + sibling sync SSOT: [ADR-008](docs/adr/ADR-008-inter-plugin-contract-versioning.md) (SemVer 룰) + [ADR-010](docs/adr/ADR-010-inter-plugin-contract-sibling-sync.md) (canonical/sibling 책임 + 신규 contract 추가 4단계). Write boundary: 각 lane plugin = 자기 contract producer + self-writer. wrapper Orchestrator = verdict 응답 + lane 라우팅 + Story §10 FIX Ledger 만 처리 (상세 [playbook](docs/orchestrator-playbook.md)).

**SemVer 적용 규칙 (ADR-008)**:
- MAJOR bump: breaking change (consumer migration 필요) — sibling sync PR 의무 (ADR-010)
- MINOR bump: additive (new optional field, new status value) — sibling sync PR 의무 (ADR-010)
- PATCH bump: typo/doc fix — sibling sync 면제 (ADR-010 §결정 3)
- kind:registry = sibling sync 면제 (ADR-010 정합 — wrapper-owned, canonical 개념 없음)

**Sibling sync 4단계 절차 (ADR-010)**:
1. canonical (lane plugin repo) 에 contract 변경 PR open
2. wrapper sibling sync PR open (wrapper-first 원칙)
3. sibling sync PR merge → canonical PR merge
4. 6 lane plugin 모두 갱신 의무 (consumer migration guide 포함 시)
