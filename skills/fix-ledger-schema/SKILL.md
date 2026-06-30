---
name: fix-ledger-schema
description: §10 FIX Ledger 스키마 + RESET 룰 + max FIX 카운터. FIX 루프 트리거 시 root-cause-decision과 함께 Orchestrator 호출 의무. Orchestrator 단독 §10 append 독점 (fix-event-v1 contract).
tools: Read
---

# §10 FIX Ledger 스키마

> 참조 테이블 skill — 내용을 읽고 FIX Ledger 작성에 적용하세요.

## 호출 시점

FIX 루프 트리거 시 (설계리뷰 / 구현리뷰 / 구현테스트 / 보안테스트 / **배포 / 배포 리뷰** FAIL — CFP-1059 / ADR-087+088 후 8 lane 확장). `codeforge:root-cause-decision`과 함께 호출.

> **배포 + 배포 리뷰 lane FIX (CFP-1059 / [ADR-087](../../archive/adr/ADR-087-deploy-lane-and-lifecycle-extension.md) + [ADR-088](../../archive/adr/ADR-088-deploy-review-lane-and-production-evidence-transfer.md))**: 본 스키마 = lane name 무관 (레인 column 에 "배포" / "배포-리뷰" 진입). 배포 lane FAIL = atomic swap race / healthcheck FAIL / secret lookup FAIL / 자동 rollback 발동 영역. 배포 리뷰 lane FAIL = smoke / 성능 비교 / cutover 사후 검증 3종 영역 — **debate-protocol-v1 trigger 의무** (성능 미충족 시 RequirementsPL ↔ ArchitectPL ↔ DeveloperPL 3-way multi-round adversarial debate 자동 발동). FIX dispatch routing = root-cause-decision skill 의 배포 단계 failure table 참조. ProductionEvidenceDeputy ownership 이관 (codeforge-design CONDITIONAL → codeforge-deploy-review 정식 — ADR-088 §결정 3) 영역 = §10 row 의 `lane` column = "배포-리뷰" + `원인 판정` column 영역 결정.

## §10 FIX Ledger 스키마

**카운터 SSOT** = `docs/stories/<KEY>.md` §10 "FIX Ledger" — Orchestrator 단독 관리 ([fix-event-v1](../../docs/inter-plugin-contracts/fix-event-v1.md) contract, CFP-32 monopoly). GitHub Issue 라벨은 보조 (fix-ledger-sync.yml Action mirror).

```
| Iter | 시각 | 레인 | 트리거 | 원인 판정 | 재실행 범위 | RESET? |
|------|------|------|--------|-----------|-------------|--------|
| 1    | ISO8601 | 설계-리뷰   | DesignReviewPL P0 × 2 | 설계 | Change Plan §3 재작성 | — |
| 2    | ISO8601 | 구현-테스트 | 성능 mean +15% | 설계 | Change Plan §3 재작성 | **RESET 구현-리뷰** |
```

상세 룰 (max FIX 횟수 / RESET marker / parallel diagnosis / mechanical fast-path) 은 [playbook §6](../../docs/orchestrator-playbook.md) SSOT.

### Max FIX counter 3/3 도달 시 ArchitectPL 재량 implementability reassessment

설계-리뷰 또는 구현-리뷰 카운터가 3/3에 도달한 경우 ArchitectPL은 implementability reassessment를 수행해야 한다. 다음 3종 escalation trigger 중 1+ 충족 시 사용자 escalation이 의무다 (ADR-067 §결정 2 참조):

- (i) ESCALATE root cause = "design granularity inadequate" — 설계 세분화 부족으로 반복 FIX 수렴 불가
- (ii) cross-module invariant 위반 without convergence path — 모듈 간 불변 조건 충돌이 수렴 경로 없음
- (iii) DeveloperPL ↔ ArchitectPL N+1 round divergence 유지 — 두 PL 판정이 라운드를 거쳐도 수렴하지 않음

사용자 escalation gate timing: ArchitectPL 결정 — 3 trigger 중 1+ 충족 시 의무 escalation. 0 충족 시 RESET path 선택 가능 (사용자 escalation 생략). 상세: [playbook §6.4](../../docs/orchestrator-playbook.md).

### FIX-close ground-truth replay = 닫기 조건 + max-FIX 카운터 disjoint (fix-event-v1 v1.4, CFP-2480 / ADR-067 Amendment 3)

"수정됨" 으로 §10 row 를 닫기 전 **원 finding reproducer 재실행 통과(반증)** 가 닫기 조건이다 (`codeforge:root-cause-decision` "판정 후 액션" 의 close-time replay 의무 SSOT):

- **닫기 조건 = `replay_verdict == PASS`** (fix-event-v1 v1.4 13번째 column) — 원 reproducer(`reproducer_command`, 12번째 column)가 결정론적 GREEN 재현 + PL falsify 통과. `falsified` = 닫기 거부.
- **max-FIX 카운터 disjoint (핵심)**: replay `falsified`(여전히 RED) = **max-FIX 3/3 카운터를 소비하지 않는다**. replay 는 "닫기 전 검증 게이트" 지 새 FIX iteration 이 아니다 — `falsified` = "현 iter 미완결(닫기 거부)" 이지 max 3/3 진입이 아님.
  - **무한거부 backstop**: replay 가 반복 `falsified` 면 무한루프 위험은 max-FIX 가 아니라 **fix-attempt 카운터** (실제 fix 시도 = §10 row Iter 증가)가 backstop. fix 를 새로 시도(새 Iter)할 때마다 max-FIX 가 소진되지, replay 재실행 자체는 카운터 무관.
  - **flaky false-RED 보호**: replay 가 flaky 로 `undetermined`(mixed/횟수 미충족)면 max-FIX 부당 소진 차단 (quarantine 보류 — ADR-070 §결정 D9 undetermined 동형).
- **(A)/(B)축 fail-mode 분리**: (A) replay-verdict 축 = `falsified` → fail-closed (닫기 거부, degrade 없음 — 수정이 실제로 안 됨). (B) Codex-미가용 축 = replay 실행 자체 불가 → lane-time `fail_open_then_record_with_marker` (`[fix-replay-fallback: fail-mode=codex_unavailable, disposition=open]`, 영구보류=delivery 마비 회피). merge-time #7 의 fail-closed-then-bounded-degrade 와 다름 — #7 degrade 는 (B)축용.
- **cross-lane RESET 무관 declare**: replay close-gate 는 §10 RESET? column semantics 와 disjoint — replay `falsified` 는 RESET 마커를 찍지 않는다 (닫기 거부일 뿐 lane 카운터 리셋 아님).
- 결정 SSOT = `scripts/lib/fix_replay_disposition.py` / concept = `docs/domain-knowledge/concept/fix-ground-truth-replay.md`.

### Cross-lane RESET 정책 (Pause-and-resume, ADR-067 §결정 4)

escalation lane (예: 보안-테스트) 에서 FIX 처리 후 design/code lane 카운터는 Pause-and-resume 방식으로 운용된다:

- escalation 중 design/code lane 카운터 보존 (cross-lane 합산 금지 — decision noise 회피)
- escalation lane FIX 완료 후 보존된 design/code lane 카운터 resume
- 각 lane (설계-리뷰 / 구현-리뷰 / 보안-테스트) 별 max=3 카운터 독립 관리

상세: [playbook §6.5](../../docs/orchestrator-playbook.md).

### §10 row reasoning_carryover field (fix-event-v1 v1.2, ADR-067 §결정 5)

§10 FIX Ledger row의 9번째 optional column — architectural amnesia 차단 목적. ArchitectPL re-spawn 시 직전 row의 reasoning_carryover full-text를 입력으로 전달 의무:

- `invariant_summary`: string, 50자 이내 — immutable boundary 요약 (변경 차단 영역)
- `disputed_claims`: string, 100자 이내 — FIX iter 내 unresolved 영역 (다음 cycle 입력)
- `transcript_ref`: string — Story §9 anchor link (예: `#debate-transcript-F-001`)

debate-protocol-v1 v1.1의 debate_artifact_ref pattern과 직교하는 필드. backward-compat: 기존 row null 또는 column 생략 모두 valid. 상세: [playbook §6.6](../../docs/orchestrator-playbook.md).

### 사용자 directive 2026-05-13 (CFP-530 ADR-059 Amendment 1 carrier — Wave 4 cross-ref)

FIX 루프 토론 목적 = 최적 구조 도출. ArchitectPL은 DeveloperPL 반론 수용이 적절한 경우 의무 수용해야 하며, 수용 불가 시 alternative proposal을 제시해야 한다. "타협이 어려웠던 부분을 기준으로 보수적으로 평가" 원칙 적용.
