---
name: inter-plugin-contract-registry
description: Inter-plugin contract MANIFEST / Versioning / Write boundary lookup 시 (contract version bump 결정). kind:contract 9 group / 14 file / kind:registry 17 file / versioning + write boundary 규칙을 정의한다. 단일 원본 체계 (CFP-2158 / ADR-118 D5 — sibling sync 폐지).
tools: Read
---

# Inter-plugin Contract Registry (CFP-29 Phase 1 후 + CFP-42 sibling backfill + CFP-2158 단일 원본 승격)

> 참조 테이블 skill — contract version bump 결정 직전 MANIFEST / Versioning / Write boundary 를 확인하세요.

codeforge core 가 외부 plugin과 통신할 때의 typed schema. wrapper repo 의 [docs/inter-plugin-contracts/](../../docs/inter-plugin-contracts/) 디렉터리가 **단일 원본 (canonical)** — CFP-2158 / ADR-118 D5 가 lane canonical ↔ wrapper mirror 이중체계를 폐지 (monorepo 통합 S1 후속). 두 종류 보유:

## kind:contract (typed inter-plugin schema, 9 group / 14 file)

[docs/inter-plugin-contracts/MANIFEST.yaml](../../docs/inter-plugin-contracts/MANIFEST.yaml) 가 SSOT. lint 였던 `scripts/check-inter-plugin-contracts.sh` 는 CFP-2159 (ADR-118 S3) 에서 은퇴 — 모노레포 통합으로 cross-repo mirror 검사 대상 소멸. contract 단일화 = S2 (CFP-2158) — lane 측 사본 폐지, 본 디렉터리가 유일 위치.

| Contract | Producer plugin | Files (단일 원본) |
|---|---|---|
| `review_verdict` | codeforge-review | review-verdict-v1.md (Archived) · review-verdict-v2.md (Archived) · [review-verdict-v3.md](../../docs/inter-plugin-contracts/review-verdict-v3.md) (Archived — CFP-137) · [review-verdict-v4.md](../../docs/inter-plugin-contracts/review-verdict-v4.md) (Active — CFP-137 / ADR-044) |
| `requirements_output` | codeforge-requirements | requirements-output-v1.md (Active) |
| `design_output` | codeforge-design | design-output-v1.md (Archived) · design-output-v2.md (Active — §7.4 + §11 idempotency, CFP-46) |
| `develop_output` | codeforge-develop | develop-output-v1.md (Active) |
| `test_verdict` | codeforge-test | test-verdict-v1.md (Archived) · [test-verdict-v2.md](../../docs/inter-plugin-contracts/test-verdict-v2.md) (Active — CFP-367 / ADR-055) |
| `pmo_output` | codeforge-pmo | pmo-output-v1.md (Active) |
| `git_ops_event` | codeforge-pmo | git-ops-event-v1.md (Active — CFP-139) |
| `deploy_output` | codeforge-deploy | deploy-output-v1.md (Draft — Active 복귀는 deploy lane 별 carrier) |
| `deploy_review_output` | codeforge-deploy-review | deploy-review-output-v1.md (Draft — Active 복귀는 deploy lane 별 carrier) |

각 contract 파일은 본 디렉터리가 단일 원본 — lane 측 사본·sibling sync 의무 없음. 구 sibling sync 정책 = Superseded ([ADR-010](../../archive/adr/ADR-010-inter-plugin-contract-sibling-sync.md) Amendment 5). Producer plugin 열은 schema 의 의미상 owner (어느 lane 이 produce 하는가) — 파일 위치와 무관하게 유효.

## kind:registry (cross-cutting protocol, 17 file)

wrapper-owned. `check-doc-frontmatter.sh` + `check-doc-section-schema.sh` 가 검증.

> 각 파일의 현재 `version` = 파일 frontmatter 가 SSOT. 본 목록은 버전 번호를 적지 않는다 (bump 마다 stale 재발 방지 — 과거 v1.1/v2.4 등 하드코딩이 수십 버전 뒤처졌던 결함 차단). 버전 확인은 해당 파일 frontmatter / MANIFEST.yaml 직접 조회.

- [comment-prefix-registry-v1.md](../../docs/inter-plugin-contracts/comment-prefix-registry-v1.md) — 11 phase prefix taxonomy
- [fix-event-v1.md](../../docs/inter-plugin-contracts/fix-event-v1.md) — Story §10 FIX Ledger writer monopoly (Active)
- [label-registry-v1.md](../../docs/inter-plugin-contracts/label-registry-v1.md) — phase/gate/fix label taxonomy (Archived — CFP-140) / [label-registry-v2.md](../../docs/inter-plugin-contracts/label-registry-v2.md) (Active — ADR-049)
- [debate-protocol-v1.md](../../docs/inter-plugin-contracts/debate-protocol-v1.md) — Codex↔Opus multi-round adversarial debate protocol (lane-agnostic, CFP-391 / ADR-059)
- [evidence-check-registry-v1.md](../../docs/inter-plugin-contracts/evidence-check-registry-v1.md) (Active) — evidence-enforceable governance check schema (CFP-389 / ADR-060). registry data SSOT = [`docs/evidence-checks-registry.yaml`](../../docs/evidence-checks-registry.yaml).
- 나머지 11 file (상세 = 각 파일 frontmatter SSOT): [branch-protection-context-registry-v1.md](../../docs/inter-plugin-contracts/branch-protection-context-registry-v1.md) · [debut-audit-triage-v1.md](../../docs/inter-plugin-contracts/debut-audit-triage-v1.md) · [decision-packet-v1.md](../../docs/inter-plugin-contracts/decision-packet-v1.md) · [decision-packet-v2.md](../../docs/inter-plugin-contracts/decision-packet-v2.md) · [defense-in-depth-sublayer-registry-v1.md](../../docs/inter-plugin-contracts/defense-in-depth-sublayer-registry-v1.md) · [imperative-walker-protocol-v1.md](../../docs/inter-plugin-contracts/imperative-walker-protocol-v1.md) · [operational-signal-v1.md](../../docs/inter-plugin-contracts/operational-signal-v1.md) · [parallel-dispatch-protocol-v1.md](../../docs/inter-plugin-contracts/parallel-dispatch-protocol-v1.md) · [reconcile-protocol-v1.md](../../docs/inter-plugin-contracts/reconcile-protocol-v1.md) · [severity-propagation-v1.md](../../docs/inter-plugin-contracts/severity-propagation-v1.md) · [stop-event-v1.md](../../docs/inter-plugin-contracts/stop-event-v1.md) (상단 5 bullet 6 file 과 합산 = 17)

## Versioning + Write boundary

Versioning SSOT: [ADR-008](../../archive/adr/ADR-008-inter-plugin-contract-versioning.md) (SemVer 룰 — 단일화 후에도 불변). 구 canonical/sibling 책임 + 신규 contract 4단계 절차 ([ADR-010](../../archive/adr/ADR-010-inter-plugin-contract-sibling-sync.md), Superseded — Amendment 5) 는 폐지. Write boundary: 각 lane plugin = 자기 contract producer + self-writer. wrapper Orchestrator = verdict 응답 + lane 라우팅 + Story §10 FIX Ledger 만 처리 (상세 [playbook](../../docs/orchestrator-playbook.md)).

**SemVer 적용 규칙 (ADR-008)**:
- MAJOR bump: breaking change (consumer migration 필요) — 단일 파일 + MANIFEST row 동시 갱신 (atomic, 같은 PR)
- MINOR bump: additive (new optional field, new status value) — 단일 파일 + MANIFEST row 동시 갱신 (atomic, 같은 PR)
- PATCH bump: typo/doc fix — 단일 파일 + MANIFEST row 동시 갱신 (atomic, 같은 PR)
- kind:registry = wrapper-owned (canonical/sibling 개념 자체 불요 — 단일 원본 체계와 동질)

**신규 contract 추가 2단계 절차 (단일 원본 — CFP-2158 / ADR-118 D5)**:
1. wrapper `docs/inter-plugin-contracts/` 에 직접 작성 (ADR-008 versioning + frontmatter 규약 준수)
2. MANIFEST.yaml entry 추가 (같은 PR, atomic)
