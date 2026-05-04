# `docs/stories/<KEY>.md` Story File Structure Template

GitHub Story Issue 1건당 `docs/stories/<KEY>.md` 파일 1개. 요구사항 접수부터 Phase 2 PR merge까지 모든 컨텍스트·설계·개발 서사가 이 파일로 누적.

**사용 대상**: 모든 lane plugin (자기 owner section 갱신, codeforge-{requirements,design,develop,test,pmo,review} CLAUDE.md self-write 표 참조), Orchestrator (§10 FIX Ledger + general docs/** 처리), 모든 에이전트 (파일 경로 + 섹션 번호 참조해 read-only fetch via `Read`)

**위치**: `docs/stories/<KEY>.md` (KEY = `<github.story_key_prefix>-N`, 예: `PLG-7`). 제목 H1 `<KEY>: <한 줄 요약>`.

**자동 생성**: `story-init.yml` Action이 사용자가 GitHub Issue Form (story.yml) 제출 시 자동:
1. 다음 KEY 번호 계산 (`Glob(docs/stories/<PREFIX>-*.md)` max+1)
2. 파일 신규 생성 (§1 verbatim, §2-11 placeholder)
3. Phase 1 PR 자동 open
4. Issue body를 docs file 링크로 변환

각 lane plugin 이 Action 후 자기 owned section 갱신 (codeforge-{requirements,design,develop,test,pmo,review} CLAUDE.md self-write 표).

---

## 라벨 (GitHub Issue labels)

GitHub Issue (Story 1건)에 부착되는 라벨:

- `type:story` 필수
- `phase:*` (single-active, phase-label-invariant.yml Action이 강제) — 7종 중 1개
- `gate:design-review-pass` (Phase 1 PR mergeable 전제, 설계 리뷰 PASS 후 부착)
- `gate:security-test-pass` (Phase 2 PR mergeable 전제, 보안 테스트 PASS 후 부착)
- `fix:*-retry` (FIX 루프 누적, fix-ledger-sync.yml Action이 자동 부착)
- `component:*` (consumer overlay `labels.components`)
- `adr:NNN` (관련 ADR)

§1 변조 금지 invariant는 `story-section-1-immutable.yml` Action이 강제 (PR에서 §1 line range 변경 시 자동 reject).

---

## 섹션 구조 (번호 고정 · 누락 섹션 진입 차단)

### §1. 사용자 요구사항 (verbatim — story-section-1-immutable.yml로 변경 차단)
- story-init.yml Action이 사용자 GitHub Issue Form 입력을 verbatim 삽입
- 재작성·요약 금지 (변조 방지)
- §1 line range 변경 시 PR 자동 reject

### §2. 도메인 해석 (DomainAgent)
- 도메인 제약 / 암묵 가정 / 범위 경계 / 우선순위 힌트
- 지식 공백 섹션
- 기존 `docs/domain-knowledge/` 파일 참조 목록

**타이밍**: 파일 생성 시점엔 placeholder (요구사항 레인 진입 전 비어있음). DomainAgent가 Analyst·Researcher와 **병렬 실행** 후 결과 반환하면 RequirementsPL 이 §2 직접 self-write (codeforge-requirements) — 따라서 **Analyst·Researcher는 §2를 입력으로 참조하지 않음** (독립 관점 보장). §5·§6과 같은 사이클에 동시 기록.

### §3. 관련 ADR
- 직접 제약 ADR (verbatim 또는 full 요약)
- 배경 참조 ADR (번호 + 1줄 요약)
- 기존 ADR 갱신·신설 필요 여부

### §4. 관련 코드 경로 + 책임
- 변경 대상 파일·클래스·레이어
- 현재 책임 요약

### §5. 요구사항 확장 해석 (RequirementsAnalyst)
- 유스케이스 / AC / 엣지 케이스 / 제외 범위 / 암묵 가정
- §5.5 "사용자 확인 필요" (blocking wait 항목)

### §6. 외부 지식 배경 (Researcher)
- Researcher 자체 도출 키워드 커버리지 + 출처 URL
- ADR 정합성 점검 결과
- "외부 지식 보강 불필요" 판정 시에도 사유를 명시 (섹션 생략 금지 — 독립 관점 결과 보존)

### §7. 설계 서사 (ArchitectAgent (chief author) → ArchitectPLAgent 검수)
- Change Plan 링크 (`docs/change-plans/<slug>.md`)
- §1 목적 / §3 도입할 설계 / §4 API 계약 / §7 보안 설계 요약 / §9 분기 선택 요약 미러링 (5-10줄)
  - §7 보안 설계 요약: Change Plan §7의 보안 설계 요약 (1-3줄) 또는 `N/A — <사유>` 그대로 미러링
- CodebaseMapper ↔ RefactorAgent ↔ SecurityArchitectAgent 3-way 대립 결론

### §8. 개발 서사 (DeveloperPL + role:dev roster)

#### §8.1 Backend 산출물
#### §8.2 Frontend 산출물
#### §8.3 DataEng 산출물
#### §8.4 InfraEng 산출물 (consumer roster에 따라 추가/생략 가능)

#### §8.5 Impl Manifest (파일 단위 매핑표)
[`impl-manifest.md`](impl-manifest.md) 스키마 따름. DeveloperPL 이 §8.5 직접 self-write (codeforge-develop) → Phase 2 PR에 commit → `subissue-from-impl-manifest.yml` Action이 자동으로 file 단위 sub-issue 생성.

### §9. 품질 게이트 이력

#### §9.0 Clarification 재스폰 이력 (FIX 아님)

PL(RequirementsPL / ArchitectPLAgent)이 병렬 서브 에이전트 결과 통합 중 추가 질의를 위해 Orchestrator 경유 재스폰 요청한 이력. FIX 루프(§10)와 구분 — 재스폰은 아직 게이트 실패가 아님.

| # | 시각 | 레인 | 재스폰 대상 | Clarification 사유 | 이전 출력 ref | 결과 |
|---|------|------|-------------|-------------------|---------------|------|
| 1 | ISO8601 | 요구사항 | ResearcherAgent | {PL이 추가 조사 요청한 주제} | §6 initial | §6 보강 |
| 2 | ISO8601 | 설계 | RefactorAgent | {ArchitectPLAgent가 특정 제안 재해석 요청} | §7 Change Plan draft v1 | §7 갱신 |

- 같은 에이전트 **2회 한도** — 3회째 필요성 발생 시 사용자 ESCALATE로 전환
- Orchestrator append-only 관리 (CFP-32, 행 삭제·수정 금지)

#### §9.1 설계 리뷰 Iteration N
- Claude · Codex severity counts + 주요 findings + DesignReviewPL 판정
- Iteration N마다 append
- **Gate evidence row (CFP-85)** — PASS verdict 시 의무 추가:
  - PR URL (Phase 1 PR)
  - Expected gate label: `gate:design-review-pass`
  - Observed gate label timestamp (ISO8601, gh API verify 시점)
  - Observed phase label transition (`phase:설계-리뷰` → `phase:구현`)

#### §9.2 구현 리뷰 Iteration N
- 동일 형식 + Gate evidence row (CFP-85) — PASS verdict 시 의무 추가:
  - PR URL (Phase 2 PR)
  - Expected: phase transition (`phase:구현-리뷰` → `phase:구현-테스트`)
  - Observed phase label timestamp

#### §9.3 구현 테스트 레인
- 기능 통과/실패 + 성능 baseline 대비 변동
- Gate evidence row (CFP-85) — PASS verdict 시 phase transition (`phase:구현-테스트` → `phase:보안-테스트`) timestamp

#### §9.4 보안 테스트 레인
- 1차 layer 결과 요약 (Dependabot / CodeQL / Secret Scanning / Push Protection)
- Claude · Codex severity counts + 주요 findings + SecurityTestPL 판정
- Iteration N마다 append
- **Gate evidence row (CFP-85, terminal)** — PASS verdict 시 의무 추가:
  - PR URL (Phase 2 PR)
  - Expected gate label: `gate:security-test-pass`
  - Observed gate label timestamp (ISO8601)
  - Phase label terminal state (`phase:보안-테스트` 유지 또는 Issue close 시점)
  - **Issue close timestamp** — Story Issue close 시점 기록 (lane plugin 의무 — phase progression audit trail)

#### §9 Gate evidence audit format (CFP-85 신규)

각 §9.x PASS verdict row 옆에 다음 형식으로 gate evidence 표 신설:

```markdown
**Gate evidence**:
| PR | Expected | Observed label | Verified at | Phase transition |
|---|---|---|---|---|
| <PR URL> | gate:design-review-pass | gate:design-review-pass ✅ | 2026-MM-DDTHH:MM:SSZ | phase:설계-리뷰 → phase:구현 (2026-MM-DDTHH:MM:SSZ) |
```

본 표 = audit reproducibility 보장 — GitHub API 라벨 verify 가 향후 막혀도 file-evidence 로 phase progression audit 가능.

### §10. FIX Ledger (FIX 카운터 SSOT)

| Iter | 시각 | 레인 | 트리거 | 원인 판정 | 재실행 범위 | RESET? |
|------|------|------|--------|-----------|-------------|--------|
| 1    | ISO8601 | 설계-리뷰 | ... | 설계 | ... | — |
| ... |

Orchestrator 가 append-only 관리 (CFP-32 monopoly, 행 삭제·수정 금지). "현재 사이클" count는 RESET 마커 이후 iteration만 합산. §10 commit이 main에 push되면 `fix-ledger-sync.yml` Action이 자동:
- Story Issue에 `[FIX #N]` 코멘트 mirror
- `fix:<레인>-retry` 라벨 부착

### §11. 참조
- GitHub Issue URL: `https://github.com/<org>/<repo>/issues/<N>`
- Phase 1 PR URL (merged)
- Phase 2 PR URL (merged)
- Change Plan 링크 (`docs/change-plans/<slug>.md`)
- 관련 ADR 링크 (`docs/adr/ADR-NNN-<slug>.md`)
- 회고 (PMOAgent 작성)

### §12. Sonnet Decision Log (CFP-59 / CFP-61 / ADR-022)

Story 내 모든 substantive decision 의 Sonnet final pick 기록. per-Story append-only.

| packet_id | trigger | options_count | decider_pick | override? | audit_result | timestamp |
|-----------|---------|---------------|--------------|-----------|--------------|-----------|
| CFP-NN-001 | brainstorming-constraint | 4 | A | no  | direct       | ISO8601 |
| CFP-NN-002 | option-formulation       | 5 | C | yes | sanity-PASS  | ISO8601 |
| CFP-NN-003 | review-verdict           | 2 | FIX | yes (pl: PASS) | direct | ISO8601 |

- `packet_id`: `<KEY>-<3-digit seq>` (decision-packet-v2.1).
- `trigger` enum 5: option-formulation / fix-root-cause / codex-ambiguity / brainstorming-constraint / **review-verdict** (CFP-61 NEW).
- `decider_pick`: options[].id picked by Sonnet (`claude-sonnet-4-6`). review-verdict trigger 시 = `sonnet_final_status` (PASS|FIX 이진, contract-fixed per ADR-022 §결정 4). blocked / timeout / suspended / reopen 케이스 = `<none>` 또는 `<blocked>` (아래 failure-state 표 참조).
- `options_count`: review-verdict 시 = 2 (PASS|FIX 이진 선택지). Trigger 5 의 option set = contract-fixed — Sonnet 가 추가 / 삭제 / rename / synthesize 금지 (ADR-022 §결정 4 invariant).
- `override?`: PL pl_recommendation reduce binary != sonnet_final_status 시 yes. FIX_DISCRETIONARY → FIX 로 reduce 시 override 아님 (PL 도 issue 인지). PASS → FIX 또는 FIX → PASS 시 override.
- `audit_result` enum 6: direct (override 없음) / sanity-PASS / sanity-FAIL / decider-suspended / user-escalation / **review-reopen** (CFP-61 NEW — packet_requires_review_reopen 발화 시).
- Detailed packet artifact = `<internal-docs>/<plugin-folder>/decisions/<packet_id>.yaml` (full v2.1 schema, includes `decider_decision.model` field + `review_lane_context` when trigger=review-verdict).
- 첫 5 review-verdict trigger packet scheduled self-audit (schema 검증 + invariant 충족 + override rate baseline).
  review-verdict trigger 한정 (option-formulation / fix-root-cause / codex-ambiguity / brainstorming-constraint trigger 별도 audit policy 적용 — ADR-019 §결정 7 그대로).

Schema SSOT: [decision-packet-v2.1](../docs/inter-plugin-contracts/decision-packet-v2.md).

ADR-018 의 §12 "Gemini Decision Log" superseded by 본 §12 (CFP-59 / ADR-019). ADR-019 §12 → ADR-022 §12 (CFP-61 trigger enum 5 + failure-state rows).

**Failure-state §12 row format (decision_state ≠ decided 인 케이스, ADR-022 §결정 7 mirror)**:

| decision_state | options_count | decider_pick | override? | audit_result | reason 컬럼 |
|---|---|---|---|---|---|
| `blocked_packet_incomplete` | 0 | `<blocked>` | n/a | user-escalation | `pl_recommendation:ESCALATE_PACKET_INCOMPLETE` |
| `decider_timeout` | 2 | `<none>` | n/a | user-escalation | `attempts[].outcome:timeout` (또는 malformed) |
| `decider_suspended` | 2 | `<none>` | n/a | decider-suspended | `attempts[].outcome:decider_suspended` (Sonnet quota / auth) |
| `review_reopen_requested` | 2 | `<none>` | n/a | review-reopen | `attempts[].outcome:packet_requires_review_reopen` |
| `write_partial` (decided 후 write 일부 실패) | 2 | `<sonnet_final_status>` | (정상) | user-escalation | `write_errors[].step:<failed step>` |

`<blocked>` / `<none>` 은 literal placeholder string 으로 §12 row 에 기재 (machine-readable enum value).

**§10 FIX Ledger 원인 판정 컬럼 evidence (CFP-61 부터)**:
- 정상 (PL≡Sonnet): `<원인>` (decider:claude_sonnet)
- Override (PL≠Sonnet): `<원인>` (decider:claude_sonnet, override: pl_recommendation=<X> sonnet_final=<Y>)

**§10 append-only resolution rule**: §10 row 는 append-only (CFP-32 monopoly). Iteration N FIX → iteration N+1 PASS 시점에 row N 이 mutate 되지 않음 (CFP-32 monopoly + CFP-61 §4.7.1 명시). 같은 cycle 내 PASS 회복은 §9 의 다음 iteration PASS row + phase/gate label transition 으로 외부 visible. RESET 마커는 별도 lane 의 cascading retry 때만 사용.

### §13. Live Operational Discipline (CONDITIONAL — Live touching Story 만 의무)

CONDITIONAL trigger: Story 가 **real funds / live exchange API / production credential / live order placement** 중 하나 이상 touching 시 본 §13 의무. Backtest/Paper-only Story = 미작성 (또는 `N/A — backtest/paper only` 명시).

**필수 필드 11종**:

| # | 필드 | 설명 | 예시 |
|---|------|------|------|
| 1 | Vault path | Secret 저장 위치 (per-exchange / per-account isolation) | `mctrader/live/bithumb/spot/main/{connect_key, secret_key}` |
| 2 | Runtime injection | Secret 주입 방식 (영구 저장 금지) | `1Password CLI subprocess → process-local env (lifetime: process only)` |
| 3 | Key permission | API key 권한 scope | `order:create + order:cancel + read; withdrawal:DISABLED` |
| 4 | IP allowlist | 거래소 측 IP 제한 | `Bithumb: <발급 시점 IP>; CI/CD: 미허용` |
| 5 | Withdrawal off proof | 출금 비활성 verify (screenshot / API response) | `Bithumb account settings — withdrawal disabled (2026-MM-DD)` |
| 6 | First-trade cap | 실거래 첫 한도 (engine call site enforce) | `KRW 10,000 (~7-8 USD), 단일 round trip` |
| 7 | Kill switch trigger | 자동 발동 조건 + manual override 절차 | `auto: drawdown / max_exposure / rate_limit / KRW_drift`<br>`manual: operator-action-v1 (UI/CLI)` |
| 8 | Operator approval | 실거래 진입 승인 절차 | `--confirm-live + ADR-008 D4 3-condition AND` |
| 9 | Reconciliation invariant | engine ↔ 거래소 ledger 정합 검증 | `KRW position drift < 1 KRW; partial fill 8-state lifecycle preserve; fee_actual ≠ fee_expected drift threshold` |
| 10 | Runbook | 운영 절차 (first-trade / kill-switch / incident) link | `docs/runbooks/live-first-trade.md`, `kill-switch-trigger.md`, `incident-response-7step.md` |
| 11 | Rollback | 비상 회복 경로 (real money 비가역 case 포함) | `kill switch trigger + open order cancel + key revoke + reconciliation`; 실 자금 손실 case = forward-only (rollback 불가) |

**미작성 시 (Live touching 인데도)**: SecurityTest lane P0 차단 (review verdict FIX, 본 §13 누락 = 보안 설계 결함). DesignReview lane 도 §7 / §11 / §8.5 cross-ref 부재 시 P0 차단.

**ADR cross-ref**: 본 §13 = ADR (consumer-side Live policy ADR — 예: mctrader ADR-012 Live Rollout Policy) 의 contract enforcement. Story-level §13 작성 시 해당 ADR cross-ref 의무.

---

## Epic Story Condensed Mode (CFP-84)

mctrader debut audit Issue [#181](https://github.com/mclayer/plugin-codeforge/issues/181) P1-4 finding: Epic-level Story (frontmatter `type: epic`) 가 일반적으로 §§ 일부 collapsed/축약 형태로 작성됨 (예: MCT-25, MCT-50 의 §5-6 결합 / §8 부재). Implementation child Story 가 details 를 carry 하므로 Epic 자체의 §8 dev narrative / §10 FIX Ledger 등 일부 섹션 = 의미 X.

본 condensed mode = Epic Story (frontmatter `type: epic`) 만 적용. Implementation Story (`type: story`) 는 § 1-§13 strict mode 유지.

### Epic Story 섹션 의무 매트릭스

| § | 섹션 | Implementation Story (`type: story`) | Epic Story (`type: epic`) |
|---|---|:-:|:-:|
| §1 | 사용자 요구사항 (verbatim) | 의무 | **의무** (story-section-1-immutable.yml 동일 적용) |
| §2 | 도메인 해석 (DomainAgent) | 의무 | 권장 (Epic-level brief OK) |
| §3 | 관련 ADR | 의무 | **의무** (Epic = ADR-driven 결정 source) |
| §4 | 관련 코드 경로 + 책임 | 의무 | 선택 (Epic-level scope 만 명시 OK) |
| §5 | 요구사항 확장 해석 | 의무 | 선택 (`§5-6 결합` 허용) |
| §6 | 외부 지식 배경 | 의무 | 선택 (`§5-6 결합` 또는 `N/A — Epic-level` 허용) |
| §7 | 설계 서사 (ArchitectAgent) | 의무 | **의무** (Epic-level design choice = ADR-driven) |
| §8 | 개발 서사 (DeveloperPL) | 의무 | **N/A 명시 의무** ("N/A — child Story 가 carry" 명시) |
| §9 | 품질 게이트 이력 | 의무 | Epic 닫는 시점 child verdict aggregate (선택) |
| §10 | FIX Ledger | 의무 | **N/A 명시 의무** (Epic 자체 FIX 없음 — child Story 가 별도 §10) |
| §11 | 참조 (회고 + child Story link) | 의무 | **의무** — child Story Issue link 모음 + EPIC-RESULTS reference |
| §12 | Sonnet Decision Log | 발생 시 | **의무** (Epic-level substantive 결정 누적) |
| §13 | Live Operational Discipline | CONDITIONAL | CONDITIONAL (child 영향 시) |

### "결합" 허용 패턴

다음 형식 만 허용:
- `## §5-6. 요구사항 확장 + 외부 지식 (combined for Epic)` — sub-content 안에 §5 항목 + §6 항목 가시 분리
- `## §X-Y. <combined title>` — heading 에 결합 명시 + 내용 안 sub-항목 분리

거부 (lint enforce — CFP-84 Phase 2 follow-up):
- 단순 `## 5-6` (heading 에 § 누락 시) → reject
- 결합 표현 없이 한 섹션이 두 § 내용 mix → reject
- §1, §3, §7 같은 mandatory 섹션 결합 → reject

### N/A 명시 형식

Implementation 무관한 §8 / §10 등 = **명시적 "N/A — <사유>" 작성 의무** (단순 섹션 omit = lint reject):

```markdown
## §8. 개발 서사

N/A — Epic Story (type=epic). 5 child Story (MCT-13 ~ MCT-17) 가 §8 dev narrative carry. EPIC-RESULTS-MCT-12.md §2 Phase decomposition 참조.

## §10. FIX Ledger

N/A — Epic 자체 FIX 없음. Child Story 별 §10 (별도 file) + EPIC-RESULTS §9 CI iteration 통계 참조.
```

### Epic close 시 §11 의무 (Story §11 ↔ EPIC-RESULTS link)

Epic Story 의 §11 회고 블록 = Epic close PR (Phase N+1) 동반 작성. EPIC-RESULTS-<EPIC_KEY>.md 가 별도 artifact 으로 작성됨 ([CFP-83 epic-results template](epic-results.md)) — Story §11 = link + 1-paragraph summary 만 보유.

```markdown
## §11. 참조

### Child Story
- mclayer/<repo>#<issue>: <CHILD-1> — <one-line summary>
- ...

### Epic close artifact
- [EPIC-RESULTS-<EPIC_KEY>.md](../../EPIC-RESULTS-<EPIC_KEY>.md) — 14 섹션 close summary

### 회고 (Epic close 후 PMOAgent fill)
<one paragraph>
```

### Implementation enforcement (CFP-84 Phase 2 follow-up)

본 CFP-84 Phase 1 = doc only. Phase 2 (별도 follow-up CFP) lint script `scripts/check-story-section-schema.sh` 강화:
- `type: epic` frontmatter detect → condensed mode allowed
- `type: story` strict mode (§1-§13 모두 의무, N/A 도 명시)
- 결합 허용 / N/A 형식 검증

---

## 단계별 갱신 책임

| 단계 | 갱신 섹션 | Owner agent |
|------|----------|-------------|
| 요구사항 접수 (story-init.yml Action 자동) | §1 verbatim 삽입, §2-11 placeholder | story-init.yml Action |
| 요구사항 병렬 에이전트 완료 | Domain→§2 / Analyst→§5 / Researcher→§6 (각 에이전트 직접 Edit) | RequirementsPLAgent / DomainAgent (codeforge-requirements) |
| 요구사항 확정 (RequirementsPLAgent) | §3-4 | RequirementsPLAgent (codeforge-requirements) |
| 설계 확정 (ArchitectAgent → ArchitectPLAgent 검수) | §3/§7/§11 + `docs/change-plans/<slug>.md` + `docs/adr/ADR-NNN-<slug>.md` | ArchitectAgent (codeforge-design direct Edit) |
| 설계 리뷰 iteration (DesignReviewPL packet return) | (no write — pl_recommendation 반환만) | DesignReviewPL (codeforge-review review-verdict-v3) |
| 설계 리뷰 PASS/FIX verdict final write | §9.1 append + GitHub comment [설계-리뷰] + gate:design-review-pass 라벨 + phase transition + §12 row | **Orchestrator 단독** (CFP-61 / ADR-022 review-verdict 5-step step 4) |
| 구현 완료 (DeveloperPL) | §8.1-8.4 + §8.5 매핑표 commit + Phase 2 PR creation | DeveloperPL (codeforge-develop direct Edit) |
| 구현 리뷰 iteration (CodeReviewPL packet return) | (no write — pl_recommendation 반환만) | CodeReviewPL (codeforge-review review-verdict-v3) |
| 구현 리뷰 PASS/FIX verdict final write | §9.2 append + GitHub comment [구현-리뷰] + phase transition + §12 row | **Orchestrator 단독** (CFP-61 / ADR-022 review-verdict 5-step step 4) |
| 구현 테스트 (Orchestrator verdict receipt) | §9.3 | TestAgent verdict + Orchestrator |
| 보안 테스트 iteration (SecurityTestPL packet return) | (no write — pl_recommendation 반환만) | SecurityTestPL (codeforge-review review-verdict-v3) |
| 보안 테스트 PASS/FIX verdict final write | §9.4 append + GitHub comment [보안-테스트] + gate:security-test-pass 라벨 + phase transition + §12 row | **Orchestrator 단독** (CFP-61 / ADR-022 review-verdict 5-step step 4) |
| Clarification 재스폰 (RequirementsPL · ArchitectPLAgent) | §9.0 append | RequirementsPL / ArchitectPL (FIX 라벨 미추가 — fix-ledger-sync.yml은 §10만 trigger) |
| FIX 루프 | §10 append | **Orchestrator 단독** (CFP-32 fix-event-v1 monopoly, fix-ledger-sync.yml Action이 자동 mirror+label) |
| Story 완료 회고 (PMOAgent) | §11 회고 블록 | PMOAgent (codeforge-pmo direct Edit) |
| Sonnet decision 발생 시 (substantive trigger 4 + review-verdict trigger 5) | §12 append + `<internal-docs>/<plugin-folder>/decisions/<packet_id>.yaml` 생성 | Orchestrator (CFP-59 / CFP-61 / ADR-022, decision-packet-v2.1) |
| Live touching Story 의 §13 (CONDITIONAL) | §13 11 필드 (vault / injection / permission / allowlist / withdrawal-off / first-trade cap / kill switch / operator approval / reconciliation / runbook / rollback) | ArchitectAgent (chief author, §7 / §11 / §8.5 와 동시 작성) |
| Phase 2 PR merged (최종) | Issue auto-close (PR body의 `Closes #N`) | (자동) |

---

## 섹션 읽기 규약

- **필요한 섹션만 읽기**: 프롬프트에 `§X, §Y 참조` 명시 → 에이전트가 `Read(docs/stories/<KEY>.md)` 후 해당 섹션만 참조
- 전체 file 읽기는 ArchitectAgent (chief author) 설계 진입 1회만 허용 (§1-6 전체 필요)
- **파일 변경은 lane plugin owner direct edit + Orchestrator 단독 (§10 FIX Ledger)** — codeforge-* CLAUDE.md self-write 표 + CFP-32 fix-event-v1 contract
