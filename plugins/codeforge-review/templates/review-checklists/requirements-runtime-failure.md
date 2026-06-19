# Requirements Review — runtime-failure 변종 체크리스트 (lane=requirements-review)

RequirementsReviewPLAgent 가 runtime-failure Story 재진입 시 ClaudeReviewAgent / CodexReviewAgent 에 packet 으로 주입하는 **internal-invariant ground-truth falsification** 체크리스트. 두 워커가 **공통 입력**으로 사용. SSOT 분리는 [ADR-001](https://github.com/mclayer/plugin-codeforge/blob/main/archive/adr/ADR-001-review-agent-unification.md) 결정.

CFP-2359 / [ADR-125](https://github.com/mclayer/plugin-codeforge/blob/main/archive/adr/ADR-125-requirements-review-lane.md) Amendment 2 신설. 기존 [`requirements.md`](requirements.md) (외부사실 의존성 체크리스트) 와 **disjoint 한 internal-invariant 축** 이다 — 같은 lane 의 **별개 검증 mode**. requirements.md 는 외부지식 진위를 검증하고, 본 체크리스트는 내부 코드·invariant 의 bound/lifetime/ordering ground-truth 보존 여부를 falsification 한다.

본 체크리스트는 **외부사실 mandate 를 약화하지 않는다** ([ADR-124](https://github.com/mclayer/plugin-codeforge/blob/main/archive/adr/ADR-124-external-knowledge-provisioning-model.md) §결정 6 무약화) — runtime-failure Story 한정으로만 발동하는 추가 mode.

## 트리거 (언제 본 변종으로 발동하는가)

runtime-failure Story 재진입 ([ADR-064](https://github.com/mclayer/plugin-codeforge/blob/main/archive/adr/ADR-064-decision-principle-mandate.md) §결정 13 root-cause 사다리 3rd rung — 문제정의 오류 → 요구사항 lane 재진입) 시에만. 트리거 조건:

- 직전 진단이 **표면 증상-anchored** (코드·invariant 미실측) 이거나
- 같은 가설이 hypothesis-differentiation escalation 종점 (현재 '설계') 까지 가서도 반복 FAIL → 1차 가정을 구현/설계가 아니라 **문제정의 오류** 로 재분류 → 요구사항 lane 재진입.

위 트리거 미충족 (정상 요구사항 산출물 리뷰) = requirements.md (외부사실 축) 으로 발동. 본 변종 N/A.

## 리뷰 대상 (scope) — hypothesis-withheld 4-tuple

packet = **hypothesis-withheld 4-tuple** `{코드, 증상, outcome-contract, invariant-surface}`. 기존 진단 (Orchestrator / lane 의 원인 단정) 은 packet 에서 **제외** 된다 — 가설을 정답이 아닌 **반증 대상** 으로 다룬다 (확증 편향 차단, ADR-064 §결정 13 재진입 규율 1 prohibited prior 동형).

- `코드` — 실패 경로의 실제 코드 (file 단위)
- `증상` — 관찰된 runtime 실패 증상 (전 lane PASS 후 제품 사망 등)
- `outcome-contract` — 충족되어야 했던 outcome 계약 (제품이 살아 있어야 함 등)
- `invariant-surface` — `docs/system-invariants.md` standing invariant-surface (ADR-068 I-8 Amendment 6 — long-lived mutable structure 의 bound/lifetime/ordering 색인). 부재/미갱신 자체가 surface 결손 신호.

## Category enum (출력 분류)

`invariant-violation` ([review-verdict-v4](https://github.com/mclayer/plugin-codeforge/blob/main/docs/inter-plugin-contracts/review-verdict-v4.md) §18.1 — closed-enum 12번째 literal, v4.14 live)

증상을 설명하는 file:line 으로 짚힌 위반 invariant (실패 경로 long-lived mutable 구조의 bound/lifetime/ordering ground-truth 위반).

## 비대칭 verdict 규칙 (Popper — 필수)

증상을 설명하는 **file:line 으로 짚힌 위반 invariant `invariant-violation` finding 1개 > "verified OK" N개**. 단일 falsification 이 N attestation 을 이긴다.

- "전부 확인함 OK" N개 attestation **만으로는 PASS 를 낼 수 없다** — falsifier 탐색이 의무다.
- 증상 미설명 시 `invariant-violation` finding 부재 = PASS 의 **필요조건이되 충분조건은 아니다** (review-verdict-v4 §18.3 verdict 레벨 realization, ADR-064 §결정 13 재진입 규율 3 / ADR-125 Amendment 2 §2 와 동일).

### 검사연극 금지 (필수 — finding 발의·verdict 차단 룰)

- **증상-anchored 단정 금지**: "원인 = X 임이 확인됨" 식 표면 증상에 끼워맞춘 단정 발의 금지. 진단은 falsification 을 통과해야 acted-on 자격이 생긴다 (ADR-119 §결정 10 ②).
- **가설 숨김 유지**: packet 에 제외된 기존 진단을 워커가 추정·복원해 그 가설을 확증하려는 행위 금지 (확증 편향 = prohibited prior 위반).
- **외부조사 강제 금지**: 본 변종은 내부 코드·invariant 의 ground-truth 축이다 — 외부 web 조사 (RFC/CVE/벤더) 를 falsification 수단으로 강제하면 검사연극 (외부사실 축은 requirements.md 가 담당, disjoint). ADR-119 §결정 6 SSOT.

## 체크리스트 (5축 — generative invariant sweep)

ADR-068 I-8 standing invariant-surface cross-ref. 실패 경로의 long-lived mutable 구조를 **열거 → bound/lifetime/ordering invariant 명시 → 코드 보존 여부 실측** (ADR-119 §결정 10 ② generative invariant sweep).

### 1. long-lived mutable 구조 enumeration (`invariant-violation`)

- 실패 경로의 **모든 long-lived mutable 구조** (buffer / queue / cache / counter / ledger / WAL 등) 가 열거되었는가 — **누락 0** 가 목표.
- `docs/system-invariants.md` standing surface 색인과 cross-ref — 색인 row 부재 구조가 실패 경로에 있는가 (I-8 surface 결손).
- short-lived (단일 요청/트랜잭션 수명) · immutable 구조는 scope 외 (long-lived ∧ mutable 만).

### 2. bound invariant (`invariant-violation`)

- 각 구조의 bound 가 명시되었는가 — **backlog cap (일시 적체 한도) vs lifetime cap (프로세스 수명 누적 한도) 를 구분** 했는가.
- backlog cap 만 있고 lifetime cap 부재 = 무한 누적 (monotone) 위험 표면화 여부.

### 3. lifetime invariant (`invariant-violation`)

- 각 구조의 **회수·reclaim 여부** 가 명시되었는가 — monotone 미회수 (계속 쌓이기만) detect.
- "이 구조는 회수 안 됨" 이 상시 구조적 속성인데 코드/문서에 보존되었는가 (Epic #2346 진단축 D incident — WAL accumulator 회수 부재가 장애 중 재도출).

### 4. ordering invariant (`invariant-violation`)

- 순서·watermark invariant 가 명시되었는가 (예: watermark monotone 전진, 순서 보장 큐).
- 실패 경로가 ordering invariant 위반에 의존하는가 (out-of-order 처리 / watermark 후퇴).

### 5. 코드 보존 실측 (`invariant-violation`)

- 각 invariant 가 **enforce 되는 (또는 위반되는) file:line** 이 실측되었는가 (추정 금지 — Read/Grep direct verify).
- 증상을 설명하는 위반 invariant 가 **file:line 으로 짚혔는가** — 이 1개가 finding 의 핵심 (비대칭 규칙 §위 참조).

## 정합 (abstention escape)

invariant-surface 입력 (`docs/system-invariants.md`) 이 부재·미갱신이면 **그 결손 자체를 finding** 으로 보고하되 (I-8 surface 미확장), 추정으로 위반 invariant 를 채우지 않는다. ADR-119 §결정 3.2 "확인 불가/추정" 명시 후 진행 (데드락 회피).

## 다음 게이트 (verdict 종합 후)

- PASS (falsifier 탐색 후 file:line invariant-violation finding 0건): Orchestrator post-Sonnet 이 `gate:requirements-review-pass` 라벨 부착 → phase:요구사항-리뷰 → **phase:설계** 전환.
- FIX (file:line invariant-violation finding 1+): Orchestrator → 문제정의 재정의 (요구사항 명세 §1-§6 의 outcome-contract / invariant 가정 갱신) → 요구사항 리뷰 재실행. 비대칭 규칙 — 단일 falsification 이 N attestation 을 이기므로 OK N개로 무마 불가.

## Consumer overlay 확장

Consumer 는 `.claude/_overlay/templates/review-checklists/requirements-runtime-failure.md` 에 도메인 특화 invariant 축 (도메인 ledger·reconcile invariant 등) 을 추가할 수 있다. SessionStart hook 이 base + overlay merge.
