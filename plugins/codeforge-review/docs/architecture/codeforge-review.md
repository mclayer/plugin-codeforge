---
title: codeforge-review lane 구조 (요구사항리뷰 / 설계리뷰 / 구현리뷰 / 보안테스트 — 산출물 검수)
last_captured: 2026-08-17
captured_at_sha: 6bb0e8aa5  # D7 provenance — 검증 시점 코드 commit anchor (CFP-3011 Phase 1, ADR-183 심사 정의역·종결 술어 설계 반영 — Phase 2 배선 전 계약 예고 포함)
last_update_cfp: CFP-3011  # 4 영역 갱신 — ADR-183 신설 반영: ① 경계 — 심사 정의역(scrutiny domain, FIX 발생 자격 축) 신설: §9/§10 감사 기록면 = out(FIX 라운드 미발생, 입력·증거로는 계속 read — "심사 대상 제외 ≠ 입력 제외"), 침해 속성(기록값≠실측·결손·재현 불가·secret 착지) = in 예외. :43 ADR-022 인용 historical 표기 정정(Deprecated — 현행 규범 = review-verdict-v4 "PL pl_recommendation = final verdict") ② 인터페이스 — review_verdict v4.18 예고: findings[].scrutiny_domain(in|out|out-provisional closed-enum) + domain_basis + verdict-level scrutiny_counts/examined_count/required_count/closed_axes[] (전부 optional additive MINOR — 집행 "부재=RED" 는 base 절차 축) ③ 데이터 흐름 — PL synthesis 에 scrutiny_domain 산정(선행 계약 조회) 단계 + lane PASS 종결 술어(심사 완결 등식 + in-domain P0/P1 잔존 0 + INCONCLUSIVE 취급) + 병리 판정 이벤트 = FIX 라운드 미생성·carrier/escalation 라우팅(Epic #3010 child 2 입력) ④ 모듈 — base 책임에 심사 정의역 결속·종결 판정 추가. 이전 CFP-2911 = interfaces 축 갱신 — ADR-081 §결정 D17(Amendment 16) 신설 반영: Codex promptfile prompt-injection 방어층 강화(nonce CSPRNG 불가측성·파일명 미포함 late-bound / delimiter 블록 개수 1 + terminal INV / born-broken 술어 협착[is_sentinel_line nonce-결합 full-line 판정·앵커 outside-scope count] / 판독측 지시 full-block 기계강제 helper `assert_directive_placement` — SSOT=whitelist `## 판독측 지시 marker` 절 + emit-nonce/--nonce write-required helper CLI). D16 언어 축 ⊥ D17 injection 축 disjoint. honest ceiling(delimiting tier, "완전 차단" 아님). 이전 CFP-2884 = ADR-081 §결정 D16(Amendment 15) 신설 반영: Codex worker promptfile 3-구획 언어 경계(A 영어 지시문 / B 인용 원문 verbatim / C 한글 요약 additive 병기) + promptfile UTF-8 round-trip fail-closed 배선(dispatch 직전 assert, 실패 = inconclusive). 직전 CFP-2828 = dispatch 재배선 — CodexReviewAgent dispatch primitive 을 companion 브로커(node) → `codex exec` 직접 단일 primitive 로 재배선(ADR-081 §결정 D15): hermetic read-only sandbox + `-o out.json` result-via-file + AC-6 소비 재검증(fail-closed 5단계) + option-first timeout wall-clock 가드. 그 직전 CFP-2813 = model tier 실측(ADR-141) + RequirementsReview lane 다축(ADR-125 Amd2/Amd3) + review-verdict wrapper 단일 원본(ADR-118 D5) + ADR-166 read protocol + per-PR 현행화 게이트(ADR-078 Amd3/ADR-112 Amd1)
kind: architecture_doc
family_ref: ../../../plugin-codeforge/docs/architecture/codeforge-family.md#모듈
---

> **목표 invariant (ADR-078 §결정 1 verbatim)**: 코드 직접 read 없이 architecture_doc 1개 read 로 전체 구조 (모듈 + 경계 + 인터페이스 + 데이터 흐름) 파악.

<!-- 본 file = lane plugin self-owned seed (CFP-971 / Sub-Epic CFP-949 Wave 2 / Epic CFP-756 / ADR-078).
     누적 현재 상태 SSOT — Story key 독립, 고정 경로. 델타 = Change Plan SSOT (disjoint, ADR-078 §결정 3).
     family-level structure = family_ref (wrapper repo seed) 참조. 본 doc 은 lane internal 구조만 채운다.
     review lane = 4 lane (RequirementsReview / DesignReview / CodeReview / SecurityTest) 공유 — PL 이 lane-specific packet 으로 도메인 주입 (CFP-2326 / ADR-125 — 요구사항리뷰 4번째 host lane). -->

## 모듈

codeforge-review = **4 review lane (요구사항리뷰 + 설계리뷰 + 구현리뷰 + 보안테스트) 산출물 검수** 책임 plugin (1 plugin 다 lane, CFP-2326 / ADR-125 요구사항리뷰 host 추가). **6 agent — 4 lane-specific PL + 2 lane-agnostic worker** 구성. PL ↔ worker 패턴 (ADR-001 통합 후) — 워커는 lane-agnostic 단일 model, PL 이 packet 으로 도메인(checklist / scope / category enum / severity override) 주입. `[verified: lane plugin CLAUDE.md "Architecture — PL + Worker 패턴" + agents/ tree direct enumeration]`:

| 모듈 (agent) | tier (model — agents/*.md frontmatter 실측 @ 14ac6b9b3, ADR-141) | 책임 |
|---|---|---|
| **RequirementsReviewPLAgent** | PL (요구사항리뷰 lane, CFP-2326 / ADR-125) — fable (Amd4 apex) | 요구사항 산출물 (Story §1-7 + 사용자 원문 + 도메인 지식) **다축 검수** (ADR-125 현행): ① 외부사실 의존성 (§결정 6 — 외부지식 충당 3-단계 ADR-124 단계③ 주 발동, WebSearch/WebFetch 허용) ② internal-invariant ground-truth falsification (Amd2 — runtime-failure 변종) ③ 내부 시스템 적합성 (Amd3 결정 B — 아키텍처 구현가능성·과거 결정 충돌·중복 Read 대조). 검사연극 금지. PL 책임 = synthesis only. PASS → gate:requirements-review-pass → 사용자 최종 확정 (design-entry sign-off, Amd3 결정 A) → phase:설계 |
| **DesignReviewPLAgent** | PL (설계리뷰 lane) — fable (Amd4 apex) | 설계 lane 산출물 (Change Plan + ADR + Story §3/§7/§11) 검수 — packet builder + verdict 종합. dedup → severity 종합 → `review_verdict_packet` 구성. **Synthesis only** (Story §9 / GitHub comment / gate label / phase transition 은 Orchestrator monopoly). **`living_architecture_updated_self_check_passed` 판정 + `living-architecture-not-updated` finding emit (ADR-112 §결정 3/4 — CFP-2813 소비 로직 배선, L3 review-tier)** |
| **CodeReviewPLAgent** | PL (구현리뷰 lane) — fable (Amd4 apex) | Phase 2 PR commit 검수 — 코드 품질 / 테스트 정합 / Change Plan §3-§7 적합성. PL 책임 = synthesis only (동일 패턴) |
| **SecurityTestPLAgent** | PL (보안테스트 lane) — opus (ADR-141 Amd4 명시 제외 — fable cyber refusal 순손실) | 보안 검증 lane — WebSearch/WebFetch 허용 (security lane 전용) + GitHub native 1차 layer fetch 의무 (worker spawn 전) |
| **ClaudeReviewAgent** | Worker (lane-agnostic) — opus | PL packet 수신 → checklist 항목 수행 → finding return. lane 도메인은 packet 으로 주입 (worker 본문 hard-coded 0건). **Codex 와 필수 peer 병렬** |
| **CodexReviewAgent** | Worker (lane-agnostic) — haiku (ADR-141 Amd1 외부위임 — 실 추론 = 외부 Codex) | 동일 packet 수신 → 독립 관점 finding return. ADR-070/081 verify-before-trust + boilerplate 적용. **Claude 와 필수 peer 병렬**. **dispatch primitive = `codex exec` 직접 단일 primitive** (companion 브로커 `node` 우회 폐지 — ADR-081 §결정 D15 / CFP-2828): 정적 리뷰 + 실행검증 2-트랙이 hermetic read-only sandbox(config 격리) 단일 primitive 로 수렴 → verdict 는 `-o out.json` result-via-file 채널로 수신 → **AC-6 소비 재검증(fail-closed 5단계)** 통과 후에만 `verdict` 필드 소비(텍스트 태그 스캔 폐지). own-Bash 실행표면 확대 0 (`node` dead-permission 은퇴 → 순 표면 감소) |

**공통 base** `templates/review-pl-base.md` = 4 PL 공유 SSOT (severity 종합 / dedup / noise 분류 / **심사 정의역 결속 + lane PASS 종결 술어 (ADR-183, CFP-3011 — Phase 2 배선 예정)** / 보고 형식 / escalation / FIX Ledger / 워커 의존성). 각 PL md 본문은 lane-specific 4 항목만 (checklist packet · FIX 카운터 정책 · 검증 스코프 · 다음 게이트). **ADR-166 (CFP-2813): 리뷰 PL 4 전원 = G2 mandatory 소비자** — 심사 대상 관련 Living Architecture 선행 read (per-PL 예외 0, 주입 표면 = 본 base — CFP-2813 Phase 2 배선. RequirementsReviewPL 편입 근거 = ADR-125 Amd3 결정 B 내부적합 축의 현재상태 대조 mandate).

**4 lane checklist** = `templates/review-checklists/{requirements,design,code,security}.md` — 각 lane 의 항목 + 자동 P0 룰. PL 이 packet `checklist_path` 로 worker 전달.

> 각 agent prompt / lifecycle 상세 = 해당 `agents/<Name>.md` SSOT. 본 표 = 모듈 단위 책임 enumeration (라인 수준 0건).

## 경계

**Lane self-write boundary** (`[verified: lane plugin CLAUDE.md @ 5b12053f "Architecture — PL + Worker 패턴" + "Drift-avoidance discipline"]` — `codeforge:lane-self-write-boundary` SSOT 정합):

| 경계 영역 | owner |
|---|---|
| review_verdict_packet 구성 (PL synthesis only) | RequirementsReviewPLAgent / DesignReviewPLAgent / CodeReviewPLAgent / SecurityTestPLAgent (4 PL 각 lane 별) |
| GitHub comment `[요구사항-리뷰]` / `[설계리뷰]` / `[구현리뷰]` / `[보안테스트]` prefix 발화 | Orchestrator (CFP-61 유래 — PL packet 받아 최종 write. 구 근거 ADR-022 = **Deprecated, historical 표기** — 현행 규범 = review-verdict-v4 "PL pl_recommendation = final verdict", ADR-183 §결정 12-5) |
| Story §9 (lane verdict mirror) | Orchestrator (PL packet 수령 후 최종 write, lane plugin self-write 영역 외) |
| `phase:요구사항-리뷰 → phase:설계` / `phase:설계-리뷰 → phase:구현` / `phase:구현-리뷰 → phase:보안테스트` / `phase:보안테스트 → phase:완료` transition label | Orchestrator |
| `templates/review-pl-base.md` (공통 SSOT) / `templates/review-checklists/*.md` / `agents/*.md` runtime SSOT | 본 lane plugin maintainer |
| `docs/architecture/codeforge-review.md` (본 doc) | ArchitectAgent write monopoly (**per-PR 현행화** — ADR-078 Amd3 / ADR-112 Amd1: `plugins/codeforge-review/**` 변경 PR = 본 doc 본문 갱신 OR `[living-arch-no-impact]` declare closed-binary, CFP-2813 게이트 강제) |

**심사 정의역 경계 (scrutiny domain — ADR-183 / CFP-3011, Phase 2 배선 예정)**: FIX 라운드 발생 자격의 축 — 각 lane 의 기존 `scope_globs ∩ category_enum` 이 FIX-eligible 정의역의 양성 열거 (신규 선언면 0, 결속만 신설). 감사 기록면(§9/§10 원장·카운터·서식·집계 — ADR-180 §결정 3 이벤트 로그 계열)은 out — FIX 라운드를 열지 못하나 **리뷰 입력(증거·anchor_recurrence 판별 재료)으로는 계속 read** ("심사 대상 제외 ≠ 입력 제외"). 예외 = 침해 속성(기록값≠실측 / 결손 / 재현 명령 부재·실패 / secret 착지 — 의도 무관 관찰 술어) 은 표면 위치 불문 in. ADR-181 검증 정의역 V(close-time 실행 도달)·§10 `원인 판정`(재진입 라우팅)과 별 축 — 교차 키 없음 (INV-R 보존).

**Drift-avoidance discipline 경계** (lane plugin CLAUDE.md 명시):

- **공통 로직 inlining 금지** — `templates/review-pl-base.md` 의 severity 종합 / dedup / FIX Ledger 로직을 PL md 본문에 다시 인라이닝 금지. 항상 base 템플릿 cross-ref.
- **Worker 호출 규약 invariant** — Packet 누락 시 즉시 `ESCALATE_PACKET_INCOMPLETE` 반환 / 워커 상호 미참조 / 워커 직접 다른 subagent spawn 불가 / WebSearch+WebFetch 는 `lane=security` + `lane=requirements-review` 전면 + `lane=design` 좁은 예외 (외부 기술선택 결론 한정, positive∩negative 양면 판정 — CFP-2327 / ADR-124 Amd 1) 허용, `lane=code` 전면 금지 (검사연극 차단 + design 좁은 예외와 비대칭 보존, ADR-119 §결정 6) / security PL 은 worker spawn 전 GitHub native 1차 layer fetch 의무 (2차 워커 web 단계 = 다출처+adversarial+시의성 심화, CFP-2327 / ADR-124 Amd 1 — 1차 자동도구 대체 아님).
- **Claude/Codex 단독 fallback 불허** — 둘 다 필수 peer, 단독 1개로 verdict 작성 금지.

**4-lane 책임 분담 매트릭스** (`codeforge:review-responsibility` skill SSOT 요약):

| Review lane | 검증 영역 |
|---|---|
| RequirementsReview (RequirementsReviewPLAgent, CFP-2326 / ADR-125 — **다축, Amd2/Amd3**) | ① 외부사실 의존성 게이트 — 외부 표준/규제 누락 / 도메인 선행사례 / AC 외부검증가능성 / 시장·벤더 단정 출처 / ADR-124 결정 6 휴리스틱 (단계③ 주 발동, 검사연극 금지 — 내부근거-only 결론에 외부조사 강제 금지) ② internal-invariant falsification (Amd2 — runtime-failure 재진입 시 hypothesis-withheld 4-tuple packet + 비대칭 verdict) ③ 내부 시스템 적합성 (Amd3 결정 B — 아키텍처 구현가능성·과거 결정 충돌·중복, generator≠verifier 독립 재검증) |
| DesignReview (DesignReviewPLAgent) | 설계 lane 산출물 문서 감사 — Change Plan §1-§13 완결성 / ADR 정합성 / Story §3/§7/§11 mirror / ADR-065 mechanical self-check / ADR-068 boundary completeness self-check |
| CodeReview (CodeReviewPLAgent) | Phase 2 PR 구현 품질 — 코드 quality / 테스트 정합 / Change Plan §3-§7 implementation 적합성 / style+history disjoint (ADR-081 §결정 D6 3-lane partition) |
| SecurityTest (SecurityTestPLAgent) | 보안 검증 — 위협 모델 적용 / 외부 입력 검증 / 권한 위임 review / secret 노출 / `live-secret-policy.yml` 정합 |
| DesignLane (codeforge-design, 본 lane 외) | 설계 결정 자체 (review lane 영역 외) — 중복 지적 시 ReviewPL dedup → severity 높은 쪽 채택 |

**Cross-cutting gate boundary**:

- **Codex Proactive Check Touchpoint #2** (ADR-052 Amendment 4) — ArchitectAgent §3 직후 mandatory. 본 lane 직접 발동 아님 (Orchestrator dispatch) 이지만 worker 산출물 = 후행 review lane 검수 input 영향.
- **`debate-protocol-v1` divergence trigger** — DesignReviewPLAgent 가 동일 `anchor_id` 에 대해 worker 간 severity / verdict 발산 감지 시 multi-round adversarial debate 자동 발동 (host 책임). ADR-059 Amendment 2 Wave 4 blanket trigger (`blanket_cross_module_designlane`) 도 본 PL 이 호스팅.
- **`hotfix-bypass:*` exception channel** — 본 lane verdict 가 evidence-check warning tier 우회 라벨 적용 시 audit-trailed exception 인지 검증 (ADR-024 Amendment 3).

**Disjoint scope** (ADR-078 §결정 3):

- 본 doc = lane internal 누적 현재 상태, Story key 독립
- review_verdict_packet = Story별 verdict 산출 (Story key 종속, 1회/lane)
- ADR = 단일 결정 단위 (결정 시점 고정 — 개정=supersede / 의미보존 위생편집 채널; ADR-058 §결정10)
- 본 doc ↔ review_verdict_packet = 상보 disjoint (구조 vs 산출)

**Scope partition**:

- dogfood artifacts (specs/plans/retros/stories/change-plans) = `mclayer/codeforge-internal-docs/codeforge-review/**` monorepo SSOT (ADR-013, lane plugin CLAUDE.md "Dogfood policy").
- 본 plugin repo = runtime SSOT 만 (agents/* + templates/* + 2 shell hook + `docs/inter-plugin-contracts/review-verdict-v4.md` canonical).

## 인터페이스 계약

lane 간 + lane 내부 계약 surface — kind:contract producer / kind:registry host / governance ADR anchor. 계약 schema field-level / version literal 미박제 (`MANIFEST.yaml` SSOT 가 권위, drift 회피).

**Producer (kind:contract)** — 본 lane 이 생성:

| contract | role | SSOT pointer |
|---|---|---|
| `review_verdict` | 4 PL (RequirementsReview/Design/Code/SecurityTest) → Orchestrator 핸드오프 packet — `lane` enum (requirements-review / design / code / security, v4.13 CFP-2326) + `pl_recommendation` enum (PASS / FIX / FIX_DISCRETIONARY / ESCALATE_PACKET_INCOMPLETE) + `findings[]` (severity + type + anchor_id — `living-architecture-not-updated` 포함, ADR-112) + boolean self-check carrier field (mechanical / boundary / dimensional / marketplace_sync_declared / living_architecture_updated) + **심사 정의역·종결 양성 증거 필드 축 (ADR-183 예고, Phase 2 — findings[].scrutiny_domain closed-enum·domain_basis + verdict-level scrutiny_counts·examined/required_count·closed_axes[], 전부 optional additive; "부재=RED" 집행 = base 절차 축)** | `docs/inter-plugin-contracts/review-verdict-v4.md` (**wrapper 단일 원본 — ADR-118 D5**, sibling sync 폐지) |

**Host (kind:registry — sibling sync 면제, ADR-010 §결정 2)** — 본 lane 이 발동 / 참여:

| registry | 본 lane 역할 |
|---|---|
| `debate-protocol-v1` | DesignReviewPLAgent = divergence_detected 시 multi-round adversarial debate host. 4-value `dispatch_mode` 우선순위 `auto_on_divergence > blanket_cross_module_designlane > mechanical_fast_path_inline > user_request_only`. min 3 / soft 4 / max 5 round. anti-sycophancy invariant (POSITION_CHANGE marker + role_lock + `remaining_disagreements` 매 라운드 출력). transcript → Story §9 append → §10 FIX Ledger `debate_artifact_ref` carry |
| `parallel-dispatch-protocol-v1` | 4 PL = 2 worker (Claude + Codex) **parallel spawn** 계약. peer-필수 invariant (단독 fallback 0). sequential 강제 사유 3종 부재 — default parallel (ADR-064 Trace 4) |
| `severity-propagation-v1` | review-verdict-v4 `findings[].severity` ↔ label-registry-v2 `severity:*` ↔ evidence-checks-registry `current_tier` 3-way bidirectional binding consumer + producer (PL 가 finding severity 결정 → label / tier propagate trigger) |

**Consumer (kind:contract)** — 본 lane 이 수신:

| contract | producer plugin | 용도 |
|---|---|---|
| `design_output` | codeforge-design | DesignReviewPLAgent input — Change Plan + ADR + Story §3/§7/§11 mirror 검수 |
| `develop_output` | codeforge-develop | CodeReviewPLAgent input — Phase 2 PR commit + Story §8/§8.5 검수 |

**Governance ADR anchor**:

- **ADR-001** (Review/Test 워커 에이전트 통합) — 3 lane × 2 vendor → 2 lane-agnostic worker. PL packet 으로 도메인 분리 + worker model 단일화 base anchor.
- **ADR-052** (Codex Proactive Check 6 touchpoint) — Touchpoint #2 mandatory dispatch (CFP-532 Amendment 4) / Touchpoint #4 multi-round adversarial debate (RequirementsPL § 영역 자체 redo). 본 lane = downstream 의 worker 산출물 검수 책임 + Codex calibration evidence 누적 (`codex_fp_tally` Story §10 prose marker).
- **ADR-059** (debate-protocol-v1) — host 책임 anchor. v1.2 = blanket_cross_module_designlane (Wave 4 cross-module Story 자동 활성) + `convergence_quality_invariant` 3 marker AND (counterargument_present / alternative_proposed / debate_purpose_statement_present).
- **ADR-068** (boundary completeness invariants, semantic) — DesignReviewPL + CodeReviewPL **dual-binding cross-validate** anchor. I-1 API contract semantic / I-2 cross-module propagation / I-3 guard placement intent / I-4 wording SSOT / I-5 dimensional empirical grounding 5 invariants self-check 결과 review-verdict-v4 carrier field (`boundary_completeness_self_check_passed` / `dimensional_empirical_self_check_passed`) verify.
- **ADR-070** (Codex verify-before-trust, 4-layer governance Layer 2) — CodexReviewAgent output ground truth 를 Orchestrator direct file Read 로 verify, mismatch 시 verdict reject + Story §10 false positive count tally + override rationale 명시.
- **ADR-081** (Codex worker prompt boilerplate) — CodexReviewAgent spawn prompt 본문 3 mandatory section (dogfood-out Story path / lane stage / sandbox boundary) + verify-before-trust scope 5 sub-scope + 3-lane partition (Codex factual citation / DesignReview boundary completeness / CodeReview style+history disjoint). severity calibration (D6) bidirectional binding evidence. **§결정 D15 (CFP-2828 — dispatch 재배선)**: 정적·실행검증 2-트랙 + companion 브로커(`node`) dispatch 폐지 → `codex exec` **단일 primitive** 수렴 (sandbox 수위 × reasoning effort × promptfile focus 프로파일 차이로만 분기). D8 file-redirect(`- < promptfile`) 계승 + option-first `timeout --kill-after=<K> <N>` wall-clock 가드(무한대기 방지, honest-ceiling: wall-clock bound 이지 자원소비 bound 아님) + `-o out.json` result-via-file verdict SSOT + AC-6 소비 재검증(fail-closed 5단계) helper `check_codex_review_output_schema.py`. **§결정 D16 (CFP-2884 — promptfile 언어 구획 + UTF-8 배선)**: promptfile **3-구획 언어 경계** — 구획 A(delimited untrusted block 밖 지시문 = 영어 강제, 한글 예외 = `templates/codex-korean-literal-whitelist.md` 리터럴 verbatim 한정) / 구획 B(block 내부 인용 원문 = **verbatim 보존·번역 금지**, 대상 집합에 Story §1 사용자 원문 편입 + 판독측 지시[블록 내부 지시 불복·인용물 무권위] + per-invocation nonce delimiter + 조립 시 sentinel 출현 거부) / 구획 C(`[Codex Review 원문]` verbatim 슬롯 **무변경** + `[한글 요약 — 비권위·additive]` 병기, 요약이 원문을 대체하면 위반). **축 A = promptfile UTF-8 round-trip fail-closed** — write 직후 조립 원본 in-memory 텍스트 ↔ 파일 re-read 내용 동일성 assert (byte 문법 유효성 단독 금지 — cp949 mojibake 는 valid UTF-8, BOM = RED, 한글 앵커 provenance = repo 소스 명시 디코드 한정) helper `check_promptfile_utf8_roundtrip.py`, 실패 = dispatch 중단 + `verdict=inconclusive` + 전용 marker `[promptfile-encoding-assert-failed]`. env export 2종(`LC_ALL`/`PYTHONUTF8`) = **2급 defense-in-depth**(1급 = helper 코드계층 `encoding='utf-8'`), lint 3번째 축 = `check_codex_companion_timeout_presence.py` `scan_encoding_env_presence` (warning tier 유지). honest-ceiling: 보증 = L1 산출물 내용 동일성 + 노출 표면 축소이지 상류 codex 오디코딩(#4013 CLOSED 2026-08-05) **완전 차단 아님**. **§결정 D17 (CFP-2911 — injection 방어층)**: nonce CSPRNG late-bound(파일명 미포함) + delimiter 블록 개수 1 + terminal INV + `is_sentinel_line` nonce-결합 full-line 판정(born-broken 협착) + `assert_directive_placement` 판독측 지시 기계강제(위치·횟수·순서·full-block 완결성, SSOT=whitelist `## 판독측 지시 marker` 절) + helper CLI emit-nonce/--nonce write-required. honest ceiling(delimiting tier — "완전 차단" 아님).
- **DesignReviewPL §8.6 audit gate** (ADR-014 Amendment 4 §결정 2): IntegrationTest contract pointer 존재 mechanical check only. policy 값 공백 PASS invariant. 상세는 `templates/review-pl-base.md` §8.6 + `templates/review-checklists/design.md` 분담 표. carrier = CFP-698 (Epic CFP-1026 W2 S4).

> 본 섹션 = surface enumeration (계약 이름 + SSOT pointer, 라인 수준 0건). 계약 schema field-level 상세 + version 값 = 각 contract file + MANIFEST.yaml SSOT (drift 회피 위해 본 doc version literal 미박제).

## 데이터 흐름

**4-lane review spawn flow** (Orchestrator 가 각 review lane 진입 시 해당 lane plugin PL 1개 spawn — non-skippable. 요구사항리뷰 = CFP-2326 / ADR-125 4번째 host lane):

```
[upstream] design_output 수신 (codeforge-design → DesignReview lane)
  ↓
Orchestrator → DesignReviewPLAgent spawn (lane PL, one-shot per attempt)
  │
  ├─ packet 구성 (checklist_path = templates/review-checklists/design.md + scope + category enum)
  │
  ├─ 한 메시지에 2 worker 병렬 dispatch (parallel-dispatch-protocol-v1):
  │     ├─ ClaudeReviewAgent (input: packet + design artifact)  → finding[]
  │     └─ CodexReviewAgent  (input: packet + design artifact)  → finding[] (+ verify-before-trust 5 sub-scope ground truth annotation)
  │
  ├─ 2 worker return (one-shot, stateless) — 독립 관점 finding[] PL 에 input
  │
  ├─ PL synthesis: dedup (anchor_id collapse) → severity 높은 쪽 채택 → noise 분류 → scrutiny_domain 산정 (선행 계약 조회, in|out|out-provisional — ADR-183, Phase 2 배선 예정) → review_verdict_packet 초안
  │
  ├─ divergence_detected check (동일 anchor_id 에 severity / FIX vs PASS 발산)
  │     │
  │     ├─ no divergence → review_verdict_packet emit
  │     │
  │     └─ divergence detected → debate-protocol-v1 발동 (host = DesignReviewPL)
  │           ├─ min 3 / soft 4 / max 5 round adversarial debate
  │           ├─ anti-sycophancy invariant (POSITION_CHANGE / role_lock / remaining_disagreements)
  │           ├─ blanket_cross_module_designlane (touched_top_level_paths ≥ 2 OR touched_lanes ≥ 2) 시 자동 활성
  │           ├─ convergence_quality_invariant 3 marker AND verify (counterargument / alternative / debate_purpose)
  │           ├─ consensus → review_verdict_packet emit + transcript → Story §9 append
  │           └─ max round 미합의 → AskUserQuestion escalation
  │
  ├─ Codex verify-before-trust (ADR-070) — Codex finding ground truth Orchestrator direct verify
  │     ├─ verified ✓ → finding 보존
  │     └─ mismatch → finding reject + Story §10 false positive tally + override rationale
  │
  └─ review_verdict_packet (pl_recommendation enum + findings + 4 boolean self-check carrier) emit
        │
        ▼
Orchestrator 수령 → Story §9 final verdict + GitHub comment `[설계리뷰]` + `phase:설계-리뷰 → phase:구현` label transition
  │
  ├─ pl_recommendation: PASS → 다음 lane (codeforge-develop) 핸드오프
  ├─ pl_recommendation: FIX → §10 FIX Ledger row append (fix-event-v1 monopoly) → ArchitectPLAgent re-spawn
  ├─ pl_recommendation: FIX_DISCRETIONARY → 사용자 판단 trigger
  └─ pl_recommendation: ESCALATE_PACKET_INCOMPLETE → 상위 lane 재spawn
```

**CodexReviewAgent dispatch 메커니즘 (ADR-081 §결정 D15 / CFP-2828 — companion 브로커 폐지)**: 2 worker 중 Codex 워커는 `codex exec` **단일 primitive** 로 dispatch (구 companion 브로커 `node` job-관리 / status·result 폴링 폐지) — hermetic read-only sandbox(정적 리뷰 + 실행검증 수렴, code write-gate 만 `workspace-write` 예외) 실행 → verdict 는 `-o out.json` result-via-file 채널로 수신 → 소비 **직전** AC-6 재검증(① 파일존재 ② JSON parse ③ schema 준수 ④ counts↔findings cross-field ⑤ category∈enum) fail-closed 통과 시에만 `verdict` 필드 소비. exit 0 자동 PASS 승격 = 구조적 차단(재검증 실패 = `inconclusive`). option-first `timeout` wall-clock 가드가 세션 블록/무한대기 방지(구 `--background` 폴링 대체). Claude 워커는 네이티브 실행 — 본 dispatch 재배선은 Codex 워커 축 한정(peer 대칭 보고 스키마 무변경).

**RequirementsReview lane / CodeReview lane / SecurityTest lane** — 동일 패턴 (PL + 2 worker parallel + verdict synthesis) 이지만 lane-specific 차이:

- **RequirementsReview (CFP-2326 / ADR-125 — 다축 Amd2/Amd3)**: input = 요구사항 산출물 (Story §1-6 + 사용자 원문 + 도메인 지식) / checklist = `templates/review-checklists/requirements.md` / 검증 3축 = 외부사실 (WebSearch+WebFetch — 단계③) + internal-invariant falsification (Amd2) + 내부적합 (Amd3 결정 B — repo Read 대조, tool-disjoint) / 검사연극 금지 / upstream = `requirements_output` / output = PASS → **사용자 최종 확정 (design-entry sign-off, Amd3 결정 A)** → `phase:요구사항-리뷰 → phase:설계` / FIX 회귀 = RequirementsPL (요구사항 명세 갱신)
- **CodeReview**: input = `develop_output` (Phase 2 PR + Story §8/§8.5) / checklist = `templates/review-checklists/code.md` / `style+history disjoint` invariant (ADR-081 §결정 D6 3-lane partition) / output label transition = `phase:구현-리뷰 → phase:보안테스트`
- **SecurityTest**: input = Phase 2 PR + security-relevant artifact / checklist = `templates/review-checklists/security.md` / WebSearch+WebFetch 허용 (security lane 전용) / GitHub native 1차 layer fetch 의무 (worker spawn 전) / output label transition = `phase:보안테스트 → phase:완료`

**FIX 루프 데이터 흐름** (max FIX 3/3, ADR-067):

- review_verdict `pl_recommendation: FIX` → Orchestrator §10 FIX Ledger row append → 원인 lane re-spawn (DesignReview FIX = ArchitectPL / CodeReview FIX = DeveloperPL 1차 진단 + ArchitectPL 최종 판정 / SecurityTest FIX = 동일 패턴)
- debate-protocol-v1 발동 시 transcript = Story §9 append → §10 FIX Ledger `debate_artifact_ref` carry → 원인 lane re-spawn 시 verbatim 입력 (reasoning carryover 보장)
- max 3 도달 시 = ArchitectPL implementability reassessment (ADR-067 §결정 3) — RESET / escalate / Pause 분기
- **lane PASS 종결 술어 (ADR-183, Phase 2 배선 예정)**: PASS = 심사 완결(coverage_required=Y 전수 심사, `examined_count == required_count` 등식 — `>=` 금지) ∧ in-domain P0/P1 잔존 0 (미측정 worker = INCONCLUSIVE ≠ 잔존 0, ADR-139 INV-L2) — 신규 P2 는 PASS 와 동시에 follow-up 착지(3문 게이트 + disposition). out finding = pl_recommendation 기여 0, findings[] 구조화 잔존. 닫힌 축 재개방(병리 — CFP-2878 §5 Q1 승계 + anchor_recurrence 4-lane 확대) = FIX 라운드 미생성, carrier 분리/escalation 라우팅 (Epic #3010 child 2 정지 장치의 입력 인터페이스 — 카운터·trigger 술어 무접촉)

**artifact propagation**:

- Story file (`internal-docs/codeforge-review/stories/<KEY>.md`) = lane 컨텍스트 SSOT (PL self-fetch, lane plugin self-write 영역 없음 — Story §9 final verdict 는 Orchestrator monopoly write)
- review_verdict_packet (transient artifact, in-memory) = Orchestrator 가 packet 수령 후 Story §9 final write + GitHub comment + label transition
- debate transcript = Story §9 append (Orchestrator write, lane plugin agent read-only)
- 본 doc (architecture_doc) = 누적 현재 상태 (영속, Story key 독립) — **per-PR closed-binary 현행화** (ADR-078 Amd3 / ADR-112 Amd1, CFP-2813). 소비 (ADR-166): 리뷰 PL 4 전원 = G2 mandatory 선행 read (review-pl-base 주입)

> 본 흐름 = lane spawn / event / artifact propagation 수준. 함수 호출 trace / 변수 전달 라인 0건 (anti-scope guard 준수).

---

### ADR-076 declarative reconciliation 3-layer cross-ref

본 lane 의 architecture_doc 운용은 [ADR-076](https://github.com/mclayer/plugin-codeforge/blob/main/archive/adr/ADR-076-declarative-reconciliation-upgrade.md) declarative reconciliation 3-layer 패턴을 도메인 disjoint 로 답습 (ADR-078 §결정 2 명시):

- **desired state** = 본 doc 의 4 H2 closed-enum (모듈 + 경계 + 인터페이스 계약 + 데이터 흐름) 누적 현재 상태 SSOT
- **current state** = lane plugin agent file (`agents/{DesignReviewPLAgent,CodeReviewPLAgent,SecurityTestPLAgent,ClaudeReviewAgent,CodexReviewAgent}.md`) + `templates/review-pl-base.md` 공통 + `templates/review-checklists/*.md` + `CLAUDE.md` (runtime 실제 동작)
- **converge** = ArchitectAgent per-PR 현행화 (ADR-078 Amd3 / ADR-112 Amd1 — `living-architecture-update` per-PR closed-binary 게이트, CFP-2813 재건축) + DesignReviewPL L3 review-tier (`living-architecture-not-updated` finding — 구 drift lint (CFP-923) 는 #1972/#2110 로 제거, content-drift 재도입 금지)

> 본 cross-ref = 패턴 답습. 도메인 (upgrade flow ↔ review lane) 은 disjoint. wording SSOT = ADR-076 본문 + ADR-078 §결정 2.

---

### anti-scope guard (ADR-078 §결정 1 verbatim — 작성자 필독)

본 doc 은 **구조 수준 only**. closed-enum 4 영역 외 다음 4종 패턴은 **금지** (라인 수준 허용 시 갱신 즉시 stale + "코드에 한 단계 더한 것" 전락 — Epic §위험신호 §1):

1. **클래스 / 함수 / 변수 라인 단위 열거** — 클래스 list, 변수 enumeration 금지.
2. **의존성 import graph 라인-level** — import 관계 라인 단위 그래프 금지.
3. **함수 signature / parameter list / return type** — API 의 line-level 시그니처 금지.
4. **코드 mirror** — `agents/` · `templates/` 구조를 1:1 복사한 디렉터리 트리 dump 금지.

→ 위 4종이 필요하면 그것은 코드 / Change Plan / ADR 영역. architecture_doc 은 "코드 read 없이 구조 파악" 목표만 만족하면 된다.
