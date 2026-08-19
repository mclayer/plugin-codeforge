---
name: fix-ledger-schema
description: §10 FIX Ledger 스키마 + RESET 룰 + max FIX 카운터. FIX 루프 트리거 시 root-cause-decision과 함께 Orchestrator 호출 의무. Orchestrator 단독 §10 append 독점 (fix-event-v1 contract).
tools: Read
---

# §10 FIX Ledger 스키마

> 참조 테이블 skill — 내용을 읽고 FIX Ledger 작성에 적용하세요.

## 호출 시점

FIX 루프 트리거 시 (설계리뷰 / 구현리뷰 / 구현테스트 / 보안테스트 FAIL). `codeforge:root-cause-decision`과 함께 호출.

## §10 FIX Ledger 스키마

**카운터 SSOT** = `docs/stories/<KEY>.md` §10 "FIX Ledger" — Orchestrator 단독 관리 ([fix-event-v1](../../docs/inter-plugin-contracts/fix-event-v1.md) contract, CFP-32 monopoly). GitHub Issue 라벨은 보조 (fix-ledger-sync.yml Action mirror).

**현재 schema** = fix-event-v1 **v1.6 (CFP-2985, 15 column)**. **Column SSOT** = [fix-event-v1 §2 Schema](../../docs/inter-plugin-contracts/fix-event-v1.md) — 본 skill 은 column 을 자체 선언하지 않고 그 표를 복사한다. v1.x optional 누락 시 backward-compat (column 생략 또는 null 허용 — 기존 7-column row 유효).

```markdown
| Iter | 시각 | 레인 | 트리거 | 원인 판정 | 재실행 범위 | RESET? | debate_artifact_ref | reasoning_carryover | affected_scope | affected_paths_with_depth | reproducer_command | replay_verdict | verification_domain_enumeration | verification_domain_coverage |
|------|------|------|--------|-----------|-------------|--------|---------------------|---------------------|----------------|---------------------------|--------------------|----------------|---------------------------------|------------------------------|
| 1    | 2026-04-29T19:15:00+09:00 | 설계-리뷰   | DesignReviewPL P0 × 2 | 설계 | Change Plan §3 재작성 | — | null | null | single-file | null | null | null | null | null |
| 2    | 2026-04-29T23:22:00+09:00 | 구현-테스트 | 성능 mean +15% | 설계 | Change Plan §3 재작성 | **RESET 구현-리뷰** | null | null | cross-module | null | null | null | null | null |
| 3    | 2026-08-19T12:00:00+09:00 | 구현-리뷰   | CodeReviewPL P0 × 1 (요구사항 자체가 미확정) | 요구사항 | 요구사항 lane 재진입 | RESET 구현-리뷰 | null | null | cross-module | null | null | null | `grep -rn 'affected_scope' docs plugins templates` | 3 대 12 |
```

시각 칸(표시) = ADR-079 §결정 2 초-KST `+09:00` (`YYYY-MM-DDTHH:MM:SS+09:00`) / machine 층 UTC = [fix-event-v1 §3](../../docs/inter-plugin-contracts/fix-event-v1.md).

상세 룰 (max FIX 횟수 / RESET marker / parallel diagnosis / mechanical fast-path) 은 [playbook §6](../../docs/orchestrator-playbook.md) SSOT.

### `원인 판정` 값공간 = 6값 (fix-event-v1 v1.6, CFP-2985) ∧ max-FIX 카운터 trigger lane 과 disjoint

값공간 = `설계` / `구현` / `요구사항` / `환경` / `설계-리뷰` / `구현-리뷰` (뒤 4값 = v1.6 additive, 기존 2값 유효). 값공간 정본 = [fix-event-v1 §2](../../docs/inter-plugin-contracts/fix-event-v1.md), **어느 값을 고르는가의 규칙** = [`codeforge:root-cause-decision`](../root-cause-decision/SKILL.md) (계약이 `decision_rule_ssot` 로 지목).

★ **값공간이 6값이 됐다고 아래 max-FIX 카운터 정의역이 확장되지 않는다** ([ADR-067](../../archive/adr/ADR-067-fix-ledger-implementability-escalation.md) Amendment 4 §9.1):

| 축 | 값공간 | 무엇을 결정하는가 |
|---|---|---|
| `원인 판정` (재진입 라우팅) | 6값 | 다음 iteration 이 **어느 lane 으로 재진입**하는가 |
| max-FIX 카운터 trigger | `설계-리뷰` / `구현-리뷰` 2 lane | **어느 lane 의 재진입 횟수**가 3/3 reassessment 를 유발하는가 |

값이 `요구사항`·`환경` 이면 그 축으로 재진입하되 **max-FIX 카운터는 소비하지 않는다** — 아래 §결정 8 replay disjoint 와 같은 형태이며 새 원리가 아니다. 소급 정규화 금지 — 기존 row 재저작 0 (append-only, [ADR-181](../../archive/adr/ADR-181-verification-domain-deficit-normative.md) INV-A).

### Max FIX counter 3/3 도달 시 ArchitectPL 재량 implementability reassessment

설계-리뷰 또는 구현-리뷰 카운터가 3/3에 도달한 경우 ArchitectPL은 implementability reassessment를 수행해야 한다. 다음 3종 escalation trigger 중 1+ 충족 시 사용자 escalation이 의무다 (ADR-067 §결정 2 참조):

- (i) ESCALATE root cause = "design granularity inadequate" — 설계 세분화 부족으로 반복 FIX 수렴 불가
- (ii) cross-module invariant 위반 without convergence path — 모듈 간 불변 조건 충돌이 수렴 경로 없음
- (iii) DeveloperPL ↔ ArchitectPL N+1 round divergence 유지 — 두 PL 판정이 라운드를 거쳐도 수렴하지 않음

사용자 escalation gate timing: ArchitectPL 결정 — 3 trigger 중 1+ 충족 시 의무 escalation. 0 충족 시 RESET path 선택 가능 (사용자 escalation 생략). 상세: [playbook §6.4](../../docs/orchestrator-playbook.md).

### FIX-close 닫기 조건 = ground-truth replay(강도) + 검증 정의역 선언(범위) · max-FIX 카운터와 disjoint (fix-event-v1 v1.4 + v1.6, CFP-2480 / CFP-2985 · ADR-067 Amendment 3 + Amendment 4 §9.3)

"수정됨" 으로 §10 row 를 닫기 전 **원 finding reproducer 재실행 통과(반증)** 가 닫기 조건이다 (`codeforge:root-cause-decision` "판정 후 액션" 의 close-time replay 의무 SSOT):

- **닫기 조건 = `replay_verdict == PASS`** (fix-event-v1 v1.4 13번째 column) — 원 reproducer(`reproducer_command`, 12번째 column)가 결정론적 GREEN 재현 + PL falsify 통과. `falsified` = 닫기 거부.
- **닫기 조건 = 검증 정의역(P / V) 선언 동반** (v1.6 `verification_domain_enumeration` · `verification_domain_coverage`, ADR-067 Amendment 4 §9.3). P / V / D 정의는 [ADR-181 §결정 1](../../archive/adr/ADR-181-verification-domain-deficit-normative.md) 을 **인용**한다 — 본 skill 은 재진술하지 않는다(재진술 = 값공간 분기, ADR-181 §결정 4 접합부 규약).
  - `verification_domain_enumeration` = 처방 정의역(P) site 를 **산출하는 명령**이지 열거 결과 목록이 아니다 (목록은 커밋이 지나면 조용히 stale 이 되고 그 stale 을 알려주는 채널이 0 이다). schema 제약 = `reproducer_command` 상속 — repo-relative 게이트·테스트 호출 형태만, raw shell free-string 금지, PII/secret/private absolute-path 금지(INV-SEC-1).
  - `verification_domain_coverage` = `x 대 y` (x = 닫기 시점 실제 재검사·재실행·재관찰한 site 수, y = 위 명령이 산출한 site 수). **비율·확률이 아니다.** 공허 값(`0 대 0` · `1 대 1` 자기 자신 1건뿐 · 대시 · `null` · 공란) = 선언 부재와 동치.
  - **`replay_verdict` 를 대체하지 않는다 (disjoint · 병렬 확장)** — `replay_verdict` = 검증 **강도**(고쳤다는 주장의 반증) / 정의역 선언 = 검증 **범위**. 둘 다 닫기 조건이며 한쪽이 다른 쪽을 면제하지 않는다.
  - **비율 임계 게이트 없음** — 분모가 자기신고라 임계 판정은 조작 유인을 창출한다. **기록은 요구하되 임계 판정은 하지 않는다.** 잔존 유인(작게 열거할수록 유리)은 ADR-181 §결정 6 라벨과 함께 **미완화 수용**으로 기록한다.
  - **완전성은 판정하지 않는다** (`declared`) — 열거가 전집합인지는 class 동일성 술어 부재로 기계 판정 불가. 금지 대상은 `D` 가 비어 있지 않은 것이 아니라 **`D` 를 미선언 상태로 두는 것**이다.
  - **max-FIX 카운터 무관** — 정의역 선언은 카운터를 소비하지 않는다 (카운터 참조 0). replay disjoint 와 동형.
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
