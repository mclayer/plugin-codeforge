---
adr_number: 182
title: 리뷰 심사 정의역·FIX 증적 정의역 분리 + severity-gated exit — 종료 조건 도달 가능화
status: Accepted
is_transitional: false
category: process
date: 2026-08-17
carrier_story: CFP-2999
related_adrs:
  - ADR-067  # §결정 2/3 RESET reassessment — 본 ADR §결정 3 이 positive 기재 의무 신설 (amendment 실배선 = CFP-2985 편입). §결정 8 의 2층 disjoint (닫기 게이트 ⊥ max-FIX 카운터) 무손상 — PASS 층 분리는 본 ADR 신설분
  - ADR-125  # 요구사항리뷰 lane 규범 SSOT — §결정 4 disjoint 를 write 표면 축으로 additive 확장 (amendment 실배선 = 후속 배선 Story). required contexts 무변경 존중
  - ADR-039  # §결정 15 Orchestrator-monopoly 4-sub-scope (§9 verdict·§10 Ledger·§14·phase transition — lane self-write 열거에서 §9 제외) — 신규 증적 monopoly 섹션의 권한 재편 anchor. 본 ADR 은 §9 write 권한 무접촉
  - ADR-031  # §14 monopoly 섹션 선례 — 신규 monopoly 섹션 신설 정합 anchor
  - ADR-064  # §결정 5 CFP scope unitary 룰 (별개 CFP 분리 허용) — 판정(본 ADR)/처방(#2988) 분리 구조와 정합. 처방 재정의 금지는 본 ADR 자체 결정
  - ADR-119  # 검증-후-단언 + §결정 9 3문 게이트 — 소급 재분류 기각 근거·정직 천장 라벨 규율
  - ADR-127  # 전수 full lane 비협상 — 본 ADR 은 심사량 축소 아님 (심사 정의역 재배치)
  - ADR-133  # ADR 번호 atomic claim — 본 ADR 번호 182 발급 경로
  - ADR-159  # design-entry sign-off — §결정 2 는 그 gate 위치·의미 무접촉 declare
  - ADR-144  # stop taxonomy — 종료 조건 정밀화가 "생략 후 진행" 으로 오독 금지 경계
related_files:
  - plugins/codeforge-review/agents/RequirementsReviewPLAgent.md  # 심사 정의역 규정 — bucket A 수렴 대상 2좌표 (후속 배선)
  - plugins/codeforge-review/templates/review-pl-base.md  # §3 판정표 — §결정 2 정밀화 방향 (후속 배선)
  - archive/adr/ADR-067-fix-ledger-implementability-escalation.md  # B(CFP-2985) 소유면 — 본 ADR 무접촉
  - docs/inter-plugin-contracts/fix-event-v1.md  # B 소유면 — 본 ADR 무접촉
  - templates/story-page-structure.md  # C(CFP-2986) 소유면 — 본 ADR 무접촉
related_stories:
  - CFP-2999
  - CFP-2985
  - CFP-2986
---

# ADR-182: 리뷰 심사 정의역·FIX 증적 정의역 분리 + severity-gated exit

## 상태

Accepted (2026-08-18 — Phase 1 PR #3015 merge `6cc9a3a7b` 로 채택. Proposed 2026-08-17) — CFP-2999 (mclayer/plugin-codeforge#2999) Phase 1 설계 carrier. **판정-only**: 본 ADR 은 5개 요청의 정책 판정을 성문까지만 수행한다. 실 파일면 배선은 §편입 지시(binding direction)가 carrier 별로 위임하며, 본 ADR 채택 시점의 wrapper 변경 표면 = 본 파일 + ADR-RESERVATION row 가 전부다. B(CFP-2985)·C(CFP-2986) 소유면 파일은 직접 수정하지 않는다.

## 컨텍스트

consumer Story MTD-1944 (repo `mclayer/mctrader`) 요구사항-리뷰 lane 이 13회차를 돌고 14회차 직전에 도달했다. 실측 (Issue #2999 §1, `@1735f84e`):

- **심사 정의역 == FIX write 정의역**: 요구사항-리뷰는 Story §1-§6 을 심사하고, FIX 는 같은 §1-§6 에 쓴다. FIX 산출물(수리 이력 마커·census 기록·회귀 방지 규율)은 산문이므로 원 요구사항과 동일한 결함 표면을 갖는다 — 매 회차가 다음 회차의 심사 대상을 생산한다.
- FIX 저작 행 = 정의역의 46.6% 인데 finding 의 78.6% 를 흡수, 단위 행당 결함 밀도 odds ratio ≈ 4.2배 `[§1 출처 — MTD-1944 단일 Story 실측, 12·13회차 blame 한정]`.
- 게이트 3종 (max-FIX 3/3·ADR-067 reassessment·자기구속 조건) 전부 「이번 회차의 결함」만 보고 「정의역의 성질」을 묻지 않아 5회 RESET 통과.
- wrapper 자신도 동일 class 를 2회 (CFP-2949 설계리뷰·CFP-2908 요구사항리뷰), 본 Story 의 요구사항리뷰 자체도 wrapper 측 재현 사례 (Story §10 iter2 원인 판정: "직전 수리가 새 심사 표면 생성"). lane·repo·문서 종류 불변의 구조 결함이다.

수리 산출물의 고밀도 결함은 업계 공지 상수다 — 결함 수리의 평균 ~7%(복잡 표면 25%+)가 새 결함을 주입한다 [source: Capers Jones, Software Defect Removal Efficiency, https://www.ppi-int.com/wp-content/uploads/2021/01/Software-Defect-Removal-Efficiency.pdf]. 상수를 심사 정의역에 계속 편입하면 finding 하한이 0 이 되지 않는 것은 산술 귀결이며, 고장난 것은 lane 이 아니라 **정지 조건의 정의**다.

**기결정 (Orchestrator 채택·사용자 통보 완료 — 본 ADR 의 입력 제약, 재논의 없음)**: ① 범위 = 판정-only (신규 ADR 성문까지, B/C 소유면 비침범 + 후속 편입 지시 명시) ② 요청 1 분리 채택 ③ 요청 2 severity-gated exit (R1 채택으로 제3항 불요) ④ 요청 3 구조/술어 구분 기재 의무 ⑤ 요청 4 원장 파생화 규율 (심사 정의역 비편입 조건부) ⑥ 요청 5 신규 즉시 + 재개 시점부터, 완료 회차 재판정 없음. Story §5.5 Q1~Q6 은 이 기결정으로 착지했다 (Q1=A, Q2=A, Q3=A, Q4=A, Q5=A, Q6=(ㄱ)).

## 결정

### §결정 0 — 심사 정의역 정본 = Story §1-§6 단일값 (AC-0 선결)

**요구사항-리뷰 lane 의 심사 정의역 정본 = `docs/stories/<KEY>.md` §1-§6** (표기 정본 = `§1-§6`). §7 = 설계 서사로 설계 lane 소유이므로, `§1-§7`/`§1-7` 해석은 요구사항리뷰가 설계 lane 산출물을 심사하는 오정의역이다. FIX 의 실효 write 정의역 = §2-§6 (§1 은 `story-section-1-immutable` 로 기구조 분리).

**census (Story §4.2 [P0] 재현 규칙 verbatim 실행 — firsthand)**:

```
git grep -nE '§ ?1 ?(-|–|—|~) ?(§)? ?[67]' 4b30b860 -- plugins/codeforge-review skills \
  docs/architecture docs/inter-plugin-contracts/label-registry-v2.md \
  archive/adr/ADR-125-requirements-review-lane.md
```

- 실행 결과 = **28 hit** (본 ADR 저작 시 firsthand 실행 — ArchitectPLAgent 독립 실행 28 과 일치, 관측자 2인 합치).
- **엔진 고정 (NF4-02 해소)**: census·통제 fixture 공히 `git grep`(byte-mode, locale 무관) 또는 `LC_ALL=C grep` 로 실행한다 — **동일 엔진 의무**. UTF-8 locale `grep -E` 는 구판(브래킷 클래스) 결함 술어를 6/6 통과시켜 판별력을 소실시킴이 실측됐다 (RR4 PL 4-locale 재현). 본 census 와 fixture 는 둘 다 `git grep` 로 실행했고, fixture 양성 6형(`§1-§6`·`§1-§7`·`§1-7`·`§1-6`·en-dash·em-dash) 6/6 match ∧ 음성 5형(`§2-§6`·`§1-§8`·`1-7`·`M1~M7`·`§16`) 0 match 를 재확인했다.
- **좌표 유효 범위 = @4b30b860 한정** (좌표 파생 정수의 무기한 유효 참칭 금지). 현행 base `6bb0e8aa5` 에서 동일 명령 재실행 결과 hit **집합 동일 (28↔28, 내용 delta 0)**, 파일 내 좌표만 2건 이동 (`docs/architecture/codeforge-family.md` 99→101 / `skills/session-recovery/SKILL.md` 38→40) — 좌표 한정 명시가 load-bearing 임의 실증.

**3-bucket 전건 분류 (28/28 종결 — 미분류 잔량 0)**. 판별 기준: 그 문면이 *요구사항리뷰가 무엇을 심사하는가* 를 규정하면 A, *타 lane 이 무엇을 심사하는가* 를 규정하면 B, 그 외 (lane 시퀀스·phase·PR 구성·요구사항 lane 산출물 범위·FIX 회귀 경로 등) = C 로서 본 설계 lane 이 판정·종결한다 (NF4-04: bucket C 수신자 = 본 ADR, 기록 artifact = 아래 표):

| # | 좌표 @4b30b860 | 표기 | bucket | 판정 (종결) |
|---|---|---|---|---|
| 1 | archive/adr/ADR-125-requirements-review-lane.md:96 | §1-7 | C | lane 위치·시퀀스 문면 — Phase 1 문서 골격 §1-7 지칭 (CLAUDE.md 「Phase 1 PR(§1–7)」 정합). 심사 정의역 규정 아님 → 정정 불요 |
| 2 | archive/adr/ADR-125-requirements-review-lane.md:102 | §1-§6 | A | 심사 대상 경계 문면 — 값 정본 일치, 수렴 delta 0 |
| 3 | archive/adr/ADR-125-requirements-review-lane.md:115 | §1-7 | C | lane 위치 문면 (#1 동형) → 정정 불요 |
| 4 | archive/adr/ADR-125-requirements-review-lane.md:325 | §1-7 | C | lane 시퀀스 문면 (#1 동형) → 정정 불요 |
| 5 | docs/architecture/codeforge-family.md:99 | §1-§6 | C | 요구사항 lane 산출물 기술 — 값 정본 일치 → 정정 불요 |
| 6 | docs/inter-plugin-contracts/label-registry-v2.md:559 | §1-7 | C | phase 라벨 설명 내 lane 위치 문면 (#1 동형) → 정정 불요 |
| 7 | plugins/codeforge-review/agents/ClaudeReviewAgent.md:45 | §1-§6 | A | 심사 scope 규정 — delta 0 |
| 8 | plugins/codeforge-review/agents/ClaudeReviewAgent.md:59 | §1-7 | B | 설계리뷰 lane 심사 scope — 제외 (정당 문면) |
| 9 | plugins/codeforge-review/agents/CodexReviewAgent.md:59 | §1-§6 | A | 심사 scope 규정 — delta 0 |
| 10 | plugins/codeforge-review/agents/CodexReviewAgent.md:215 | §1-§6 | A | 심사 대상 규정 — delta 0 |
| 11 | plugins/codeforge-review/agents/DesignReviewPLAgent.md:79 | §1-7 | B | 설계리뷰 scope_globs — 제외 (정당 문면) |
| 12 | plugins/codeforge-review/agents/RequirementsReviewPLAgent.md:4 | §1-7 | **A 수렴** | frontmatter description = 심사 정의역 규정 — 값 상이 → `§1-§6` 수렴 대상 |
| 13 | plugins/codeforge-review/agents/RequirementsReviewPLAgent.md:38 | §1-§6 | C | 요구사항 lane 산출물(입력) 기술 — 값 정본 일치 → 정정 불요 |
| 14 | plugins/codeforge-review/agents/RequirementsReviewPLAgent.md:80 | §1-§6 | A | scope_globs 주석 = 심사 scope 규정 — delta 0 |
| 15 | plugins/codeforge-review/agents/RequirementsReviewPLAgent.md:182 | §1-§7 | **A 수렴** | 심사 대상 규정 — §7(설계 서사·설계 lane 소유) 포함 오정의역 → `§1-§6` 수렴 대상 (**이 정정만으로 정의역 1 섹션 축소**) |
| 16 | plugins/codeforge-review/agents/RequirementsReviewPLAgent.md:227 | §1-§6 | C | FIX write 정의역 문면 (명세 갱신 목적지) — 값 정본 일치·§결정 1 (본문 정정 write 잔존) 과 정합 → 정정 불요 |
| 17 | plugins/codeforge-review/docs/architecture/codeforge-review.md:23 | §1-7 | **A 수렴** | 심사 대상 규정 (arch doc) — 값 상이 → `§1-§6` 수렴 대상 |
| 18 | plugins/codeforge-review/docs/architecture/codeforge-review.md:170 | §1-6 | **A 수렴(표기)** | 심사 input 규정 — 값(1..6) 일치·표기만 상이 → 표기 정규화 대상 (비-load-bearing) |
| 19 | plugins/codeforge-review/templates/review-checklists/design.md:10 | §1-7 | B | 설계리뷰 checklist input — 제외 (정당 문면) |
| 20 | plugins/codeforge-review/templates/review-checklists/requirements-runtime-failure.md:83 | §1-§6 | C | FIX 회귀 경로 문면 — 값 정본 일치 → 정정 불요 |
| 21 | plugins/codeforge-review/templates/review-checklists/requirements.md:9 | §1-§6 | A | 요구사항리뷰 checklist input — delta 0 |
| 22 | skills/jira-decision-channel/SKILL.md:99 | §1-7 | C | design-entry 확정 후 Phase 1 문서 변경 영향 문면 → 정정 불요 |
| 23 | skills/review-responsibility/SKILL.md:93 | §1-7 | **A 수렴** | 요구사항리뷰 심사 대상 규정 — 값 상이 → `§1-§6` 수렴 대상 |
| 24 | skills/session-recovery/SKILL.md:38 | §1-7 | C | phase 상태 복원 판정 기준 (Story 골격 채움 여부) → 정정 불요 |
| 25 | skills/story-cutoff-classification/SKILL.md:25 | §1-7 | C | Phase 1 PR 구성 규정 (CLAUDE.md 문면 정합) → 정정 불요 |
| 26 | skills/story-epic-flow-preflight/SKILL.md:19 | §1-7 | C | lane 위치 문면 (#1 동형) → 정정 불요 |
| 27 | skills/story-epic-flow-preflight/SKILL.md:24 | §1-7 | C | Phase 1 PR 구성 규정 → 정정 불요 |
| 28 | skills/story-epic-flow-preflight/SKILL.md:49 | §1-7 | C | lane 진입 prerequisite (Phase 1 문서 범위) → 정정 불요 |

**집계**: A = 11 (delta 0 = 6 · **수렴 대상 = 값 상이 4 + 표기 1 = 5좌표**) / B = 3 (제외) / C = 14 (전건 본 ADR 종결 판정 — 정정 불요). ⓓ 보증 5 site (RequirementsReviewPLAgent.md·codeforge-review.md·review-responsibility/SKILL.md·label-registry-v2.md·ADR-125) 전건 hit 포함 확인.

**NF4-01 해소**: §4.1(d) 파생 규칙 ("scope 문면 동기 대상 = §4.0 열거 전건") 은 위 3-bucket 필터를 **선적용한 뒤** bucket A 수렴 대상 5좌표에만 적용한다. ADR-125 hit 4좌표의 사전 bucket-A 배정은 해제한다 — firsthand 분류 결과 A(delta 0) 1 · C(종결) 3 이며, L96/L115/L325 는 CLAUDE.md 정합 문면이라 수렴 시 정당 문면 파괴 경로였다.

**실 정정 (bucket A 수렴 커밋) = 판정-only 범위 밖** — §편입 지시의 후속 배선 Story 가 수행한다. 본 ADR 은 정정 계획 특정(수렴 대상 5좌표 + 정본 값)까지다.

### §결정 1 — 심사 정의역·FIX 증적 정의역 분리 채택 (요청 1 — AC-1a/1b/1c)

**분리를 채택한다.** FIX 산출물 중 요구사항 명세가 아닌 **메타-텍스트 3종 (closed-enum)** 을 심사 정의역(§1-§6) 밖 신규 증적 정의역으로 이관한다:

1. **FIX 회차 마커** — `[FIX iter` 류 회차 리터럴 마커.
2. **census·측정 기록** — 재현 규칙 실행 결과·수치 census·계측 로그.
3. **회귀 방지 규율** — Story 가 자기 자신에게 부과하는 자기구속 조항.

**경계 (재귀 재생산 차단)**: 위 3종 밖의 것은 이관 대상이 아니다. **본문 정정 write 는 §2-§6 에 잔존한다** — FIX 가 요구사항 명세 자체(모순·오류)를 고치는 write 는 정의상 명세로 가야 하며, §1 은 immutable 구조 분리로 이미 제외되어 실효 FIX write 정의역 = §2-§6 이다. "본문 정정이냐 메타냐" 가 새 심사 대상이 되지 않도록 closed-enum 3종만 이관한다.

**이관 목적지 = 신규 증적 전용 monopoly 섹션** (Story §4.2 이관 목적지 3안 중 (c) — 회귀면 최소):
- §9 부적격 — Story §5.1 UC-4 의 「§9·§10 Orchestrator 독점」 중 **§10 은 참** (lint `MONOPOLY_SECTIONS` "10" 등재 ∧ fix-event-v1 append writer = Orchestrator 단독 ∧ ADR-039 §결정 15-②), **§9 전체 독점 주장만 부정확** — §9 final verdict 는 ADR-039 §결정 15-① Orchestrator-monopoly sub-scope 이나, §9 하위 서술(lane 산출 기록)은 lint `SECTION_OWNERS["9"] = [review, design, develop, requirements]` 다중 owner 다 (NF4-03). **비승계 대상 = 「§9 전체 독점」 주장 한정** (Story §5.6 (ii) 「§10 monopoly 는 참, §9 는 아님」 원 분해 승계 — CR-D2-01 정밀화).
- §10 부적격 — 표 스키마 + B(CFP-2985) 소유면.
- **섹션 번호는 본 ADR 이 예단하지 않는다** — C(CFP-2986) 편입 시 story-page-structure 정본에서 확정한다 (PR codeforge-internal-docs#3029 의 §9 성장축 외부화 착지 후 정합 확인 의무). write 주체는 monopoly 단일 주체 방향 (ADR-031 §14·ADR-039 §10 monopoly 선례 정합) — 확정 = C 편입 시.

**cross-ref 양방향 요건 (AC-1c — 추적성 보상, 무보상 통과 차단)**:
- **증적 side row 필수 필드 3종** = `{finding-id, 대상 섹션 heading 앵커, 정정 커밋 SHA}`. **라인 번호 등 좌표 파생 정수는 금지** — 편집마다 죽는 값이며 본 Story 고발 클래스다 (heading 앵커 + immutable SHA 만 허용).
- **본문 side** = Story 골격에 고정 포인터 1줄 ("수리 이력 = <증적 섹션> 참조" 형식의 골격 상수 — per-fix 본문 추가 0, C 편입 시 골격에 1회 성문).

**정직 효과 라벨 (over-claim 금지 — Story §4.2 선언 verbatim 승계)**: 분리의 효과 = **심사 정의역 축소**이지 결함 제거가 아니다. 마커형 메타-텍스트가 심사 정의역에 남는 경로만 봉인되며, 산문형 메타·본문 정정 write 는 §2-§6 에 남아 다음 회차 심사 대상이 된다. 증적 정의역(§9·§10·신규 섹션)에서도 같은 결함 class 는 계속 발생한다 (§결정 4 가 그 정의역의 품질 기준을 별도 부과). 결함 예측자는 "누가 쓰는가" 가 아니라 "산문 자기서술 vs 기계 파생" 축이다.

### §결정 2 — severity-gated exit (요청 2 — AC-2a/2b/2c)

**PASS 조건을 severity-gated exit 로 정밀화한다.** 이는 신규 판정표 신설이 아니라 **기존 `review-pl-base.md` §3 종합 판정표의 정밀화**다 (신규 표 = 이중 SSOT 금지. wrapper base 는 이미 P0/P1 축 — "finding 0 = PASS" 는 consumer 운용 실태였지 wrapper 규범 문면이 아니다):

> **PASS = P0 0 ∧ P1 0 ∧ 직전 회차 finding 전건 처분 종결 (CLOSED 또는 defer-수신처 지정, REOPENED 0) ∧ 잔여 P2/P3 전건 처분 lifecycle 등재** (deferred-item-lifecycle 연결 — won't-fix 은폐 금지, 미조치 처분으로 덮지 않는다)

- **처분 판정원 (AC-2c)** = ① 리뷰 PL 보고서의 처분 표 (finding-id 별 CLOSED/REOPENED/defer-착지점) ② fix-event-v1 v1.4 `replay_verdict` (FIX-close ground-truth replay). ②의 실배선 = B(CFP-2985) 편입 — 본 ADR 은 판정원 지정까지.
- **3층 분해 + ADR-067 §결정 8 무손상**: 본 ADR 은 lane 종료(PASS) ⊥ finding 처분(닫기) ⊥ 카운터 소비(Iter) 의 3층으로 분해한다. 이 중 **뒤 2층의 disjoint (닫기 게이트 ⊥ max-FIX 카운터) 가 ADR-067 §결정 8 원문**이고 ('층' 어휘·PASS 층 문면은 §결정 8 에 부재 — 원문 재대조 완료), **PASS 층의 분리는 본 ADR 신설분**이다. 따라서 §결정 8 supersede 0 — 본 정밀화는 PASS 층만 건드린다.
- **"메타-텍스트" 제3항 불요**: §결정 1 (R1) 채택으로 메타-텍스트가 심사 정의역에서 구조적으로 소거되므로 종료 조건에 그 판별 축이 필요 없다 (Story §6.5 R1↔R2 의존 관계. 외부 선행례에도 대응물 부재 — R1 미채택 시에만 필요했을 축).
- **도달 가능성 근거**: 새 조건의 각 항은 리뷰어 성실성과 양립한다 — P0/P1 은 severity 판정 (리뷰가 이미 수행), 처분 종결은 follow-up 확인 (신규 sweep 아님), 잔여 등재는 기록 행위다. finding 하한이 0 이 아니어도 (bad-fix 상수) P2/P3 잔여는 등재 처분으로 exit 가능하므로 종료 조건이 물리적으로 도달 가능해진다.
- **MTD-1944 13회차 시뮬레이션 (AC-2b — §1 문면만으로 수행)**: 제1항 P0=0 **충족** (6회차 연속 0) · P1=1 (PL-R13-01) **미충족** / 제2항 처분 7/7 CLOSED **충족** (해당 Story 최초) / 제3항 축 = R1 로 소거. 종합 = **PASS 불성립 (P1 1건) — 판별 가능** 판정. **판별 범위 분할 (정직 천장 승계)**: 제1·2항은 §1 문면만으로 자족 판별. 잔여 finding 의 실행의존 분류는 §1 문면만으로 6건 중 5건 미분류 (RR2 실측) — MTD-1944 재개 시 실 산출물 필요.
- **외부 정합**: inspection exit = "결함 0" 이 아니라 anomaly 의 처분·follow-up 종결 [source: IEEE 1028-2008, https://standards.ieee.org/standard/1028-2008.html — **verbatim 조항 미확보·2차 corroboration 만** (Story §9.4 확인 불가 기재 승계)]. follow-up 은 시정조치의 완료·유효성 검증 [source: ISO 19011:2018 §6.7]. 업계 release exit = "blocker/critical 0 + 잔여 문서화·수용" 2축 [source: BrowserStack, https://www.browserstack.com/guide/entry-and-exit-criteria-in-software-testing] — 본 정의와 구조 동형.
- **무접촉 declare**: design-entry sign-off (ADR-159) 의 위치·의미 무변경. required contexts 무변경 (ADR-125 §결정 2 존중 — 신규 required 게이트 0). 본 결정은 심사량 축소가 아니다 (ADR-127 전수 full lane 비협상 정합 — 출처 표기: **Story §1 (verbatim 내부) §6** "리뷰를 줄이자고 말하지 않는다" 문면 승계, ADR-127 자체 문면 아님). **ADR-144 stop taxonomy 무접촉**: 본 정밀화는 PASS 판정 기준의 정밀화이지 lane 실행의 생략·단축 허가가 아니다 (ADR-144 정당 멈춤 3종·ADR-127 전수 full lane 과 disjoint — "생략 후 진행" 오독 금지).

### §결정 3 — RESET 정당화 구조 축 (요청 3 — AC-3a/3b)

**RESET 정당화에 positive 기재 의무를 신설한다.** 현행 ADR-067 §결정 3 은 negative gate (3 trigger miss + dual metric miss → reset 가능) 이며 "처방을 바꿨다" 는 문면상 존재하지 않는다 — MTD-1944 의 5회 RESET 정당화는 **문면 근거 없는 관행**이었고, 본 결정은 그 관행의 문면화이자 자격 조건 부과다:

1. **2치 분류 기재 의무**: RESET 시 처방 변경이 「**구조 변경** (corrective action — 수렴 실패의 원인 구조 제거: 정의역·판정원·게이트 배선 변경)」인지 「**술어 개선** (correction — 같은 구조 안에서 심사 술어·패턴·표현만 정밀화)」인지 명시 기재한다 [source: CAPA correction vs corrective action 구분 — ISO 19011 계열 어휘, Story §6.4 R3].
2. **자격 조건**: **술어 개선 단독으로는 동일 카운터 내 재-RESET 불가.** MTD-1944 5회 RESET 은 전부 술어 개선이었고 문면상 구별되지 않았다 — 기재 의무만으로는 부족함을 실측이 시사한다.
3. **판별 불가 분기 (AC-3b)**: 구조/술어 판별 불가 시 **RESET 불허 — ESCALATE** (사용자 결정 회부). 판별 불가를 RESET 통과 경로로 쓸 수 없다.
4. **기재 위치** = §10 FIX Ledger RESET row 신규 column. **실배선 = B(CFP-2985) 편입** (fix-event-v1 trailing optional column 선례 4회 동형 — 본 ADR 은 의무·위치 지정까지, 필드 형식 정의는 B 몫).

**#2931 과의 disjoint 경계 (carrier 경합의 절 분담)**: #2931 = ADR-067 §결정 1 **trigger 범위** (누가 대상 — 요구사항-리뷰 lane 부재) / 본 결정 = **RESET 판정 기준** (무엇을 근거로). 동일 ADR-067 amendment carrier 를 두 축이 disjoint 절로 분담한다 — trigger 배선이 되어도 판정 기준이 "처방을 바꿨는가" 인 한 5회 RESET 은 통과했을 것이므로 두 축 모두 필요하다.

**소급 재분류 없음**: 과거 5회 RESET 의 재분류는 하지 않는다 — ADR-119 §결정 9 3문 게이트 미충족 (§1 이 이미 실측 분류 5/5 술어 개선을 제공, 재작업 이득 0).

### §결정 4 — 원장(§9·§10) 파생화 규율 적용 (요청 4 — AC-4a)

**적용을 채택한다.** 원장 write 정의역(§9·§10)에 산문 자기참조 가변 단정(줄 위치·수치·착지 단정) 금지 → **기계 파생 값 또는 재현 규칙 + immutable ref** 규율을 적용한다.

- **처방 본문 = #2988 참조 (SSOT 단일화 — 본 ADR 자체 결정)**: 파생화 처방의 정의·taxonomy·집행 메커니즘은 #2988 이 단일 SSOT 이며 본 ADR 에서 재정의하지 않는다 — 이 재정의 금지는 **본 ADR 의 자체 결정**이다 (ADR-064 §결정 5 「CFP scope unitary 룰」은 별개 CFP 분리를 허용하므로 판정(본 ADR)/처방(#2988) 분리 구조와 정합 — 원문 재대조 완료, "single carrier" 는 §결정 5 문면이 아니다). 본 결정은 **적용 범위 boolean 판정만** 수행한다 — "#2988 처방의 적용 정의역에 §9·§10 원장을 포함한다" = **true**. 근거 = §1 (마): Orchestrator 자신이 §9 원장에서 좌표 파생 정수 결함을 냈다 (그 결함을 설명하는 문장 자신에서) — 결함 class 는 write 주체를 가리지 않는다.
- **적용 경계 조건 (필수)**: **원장을 심사 정의역에 편입하지 않는 조건 하에서만** 적용한다. 원장을 리뷰 심사 정의역에 편입하면 §결정 1 이 끊은 자기증식 고리가 원장 경유로 재개통된다. 원장 품질은 심사 편입이 아니라 파생화 규율 + 기계 lint (실배선 후속) 로 확보한다.
- **수신자 = §9/§10 write 주체 전원**: §10 write = Orchestrator 단독 (ADR-039 §결정 15-②) / §9 는 final verdict 만 Orchestrator monopoly (§결정 15-①) 이고 하위 서술은 lint `SECTION_OWNERS["9"] = [review, design, develop, requirements]` 다중 owner — 따라서 규율 수신자 = Orchestrator + §9 하위 서술 write 4 lane 전원 (§1 (마)가 Orchestrator 자기 실증 사례 — CR-D2-01 정밀화).

### §결정 5 — 소급 transition 3-상태 (요청 5 — AC-5a/5b/5c)

| Story 상태 | 적용 규칙 |
|---|---|
| **신규** (본 판정 확정 후 개시) | 즉시 — 전 조항 (§결정 0~4) 적용 |
| **진행중·BLOCKED** (MTD-1944 포함) | **재개 시점부터** — 재개 후 첫 회차부터 신 exit 조건(§결정 2)·신 RESET 기재 의무(§결정 3) 적용. 완료된 회차의 재판정 0 |
| **완료** | 소급 0 — 재평가 대상에서 제외 |

**MTD-1944 조항 (AC-5b)**: 재개 = **14회차부터 신 exit 조건 적용** · 기존 RESET 5회 유효 보존 · **max-FIX 카운터 2/3 동결값 이월 — 재산정 금지** (재산정 시 5 RESET 무효화 → 카운터 폭증 → 자동 escalation 폭발, Story §4.2 [P2] 실측 경로).

**조정 규칙 (AC-5c — 사전 명문화)**: ① 완료 Story 제외 ② 기존 RESET 마커 유효 (§10 카운터 semantics "RESET 마커 이후만 합산" 무변경 — ADR-067 Amd 2 영구 invariant 존중) ③ 신규 마커부터 신 규칙 (§결정 3 기재 의무는 본 판정 확정 후 발생하는 RESET 부터). 완료 Story 전수 재스캔은 발의하지 않는다 (ADR-119 §결정 9 3문 게이트 미충족).

### §편입 지시 (binding direction — 후속 배선 목록의 SSOT)

본 ADR 은 판정-only 이므로 아래 실배선을 각 carrier 에 **후속 편입 지시**한다. 각 carrier 는 자기 소유면 완료 후 본 목록을 편입 checklist 로 사용한다:

**B (CFP-2985) 편입 목록**:
1. ADR-067 amendment 문면 (§결정 3 의 positive 기재 의무 + 자격 조건 + ESCALATE 분기 — #2931 몫과 disjoint 절 분담).
2. fix-event-v1 신규 column (`구조 변경/술어 개선` 2치 — trailing optional 선례 동형) + `replay_verdict` 처분 판정원 배선 (§결정 2).
3. §10 스키마의 RESET row column 반영.
4. **선행 gap 정산**: fix-event-v1 §3 "레인" enum 에 `요구사항-리뷰` 부재 (Story §4.1 부가 실측 1 — lane 문서 "§10 레인=요구사항-리뷰 누적" 문면과 계약 schema 어긋남. 신규 column 을 붙일 lane 행 자체가 미정의이므로 선행 정정).

**C (CFP-2986) 편입 목록**:
1. 신규 증적 monopoly 섹션 골격 (섹션 번호 확정 = story-page-structure 정본 — §결정 1).
2. section-schema (증적 row 필수 필드 3종 presence).
3. 본문 side 고정 포인터 1줄 (Story 골격 상수).
4. PR codeforge-internal-docs#3029 (§9 성장축 외부화) 착지 후 정합 확인 의무 — 역방향 충돌 검사.
5. **신규 증적 섹션의 소유권 집행 배선**: `scripts/lib/check_story_section_ownership.py` `MONOPOLY_SECTIONS`(또는 `SECTION_OWNERS`) 등재 + 미등재 섹션이 `Unknown section — skip (forward-compat)` (동 스크립트 L394-397 @6bb0e8aa5) 로 무검사 낙하함을 회귀 테스트로 고정 (born-hollow monopoly 차단 — INV-5 집행 채널 정합, CR-D2-02). write 주체가 Orchestrator 로 확정되면 = ADR-039 §결정 15 5번째 sub-scope 추가 → **별도 ADR Amendment 의무** (ADR-039 원문 「5번째 entry 의 4-sub-scope (…) 는 **closed enum**. 5번째 sub-scope 추가 = 별도 ADR Amendment 의무 (…)」 L430 @6bb0e8aa5 축약 인용 (load-bearing fragment verbatim — 괄호 열거·후속 rationale 은 (…) 로 생략) — 설계리뷰 iter3 CR-D3-02 로 추론 라벨 → verbatim 승격, DR4 CR-D4-02 로 축약 인용 라벨 정밀화).
6. **§9 소유권 SSOT 불일치 수렴**: `story-page-structure.md` 「단계별 갱신 책임」 표의 §9.x "Orchestrator 단독" 표기 ↔ lint `SECTION_OWNERS["9"]` 4-lane ↔ ADR-039 §결정 15-① verdict-한정 monopoly — 3자 정합화 (Story §4.2 장벽 1 실측 충돌의 수렴 배정, CR-D2-01 권고 수용).

**비분할면 잔여 배선 = 후속 배선 Story 1건 회부** (본 목록이 SSOT — 발의 3문 게이트 통과: 깨짐 = scope 문면 혼재 + 판정표 실태 괴리 실측 / 강제 요인 = 본 ADR 채택 / 관찰자 무관 필요):
1. bucket A 수렴 5좌표 정정 (§결정 0 표 — RequirementsReviewPLAgent.md frontmatter `§1-7`·L182 `§1-§7`, codeforge-review.md L23·L170, review-responsibility/SKILL.md L93. 좌표는 @4b30b860 한정 — 정정 시 재현 명령으로 재도출).
2. review-pl-base §3 판정표 정밀화 (§결정 2 문면 — 4 lane 공유 base 라 lane-override 여부 포함).
3. ADR-125 amendment (write 표면 disjoint 축 additive 확장 + 정본 값 `§1-§6` 성문).
4. requirements checklist P1 강제 자동룰 재검토 (실질 finding-0 합성 경로 ⓐ).
5. **AC 게이트 slicing 정정 (TestContractArch 이의 A 후속)**: `ac-traceability-matrix`·`ac-schema-authoring-gate` 의 §-slicing 이 §1 verbatim 내부 헤딩 shadowing (first-match) 으로 본 Story 에 비적용 PASS(vacuous) — last-match/§1-제외 정정 + internal-docs 복사본 parity. **source enum 측 (이의 B) 은 internal-docs `9a25c46a` 로 기정정 완료 (analyst 0 / derived 4 — 원자 결합의 선행 절반 이행)** → 잔여 = **slicing 정정 단독 수행 가능**, 단 정정 후 `test_ac_source_enum_matches_contract_enum` 회귀 확인 의무.

### ADR-183 경계·정합 (병렬 저작 조율)

> 사용자 결정 (2026-08-17): 본 ADR 이 cross-ref 1절을 추가하고 선착 머지, ADR-183 (CFP-3011) 이 후행 정합한다. 본 절은 순수 additive — 기존 §결정 0~5 문면 무변경.

- **상보 축 선언**: ADR-182 = 심사 정의역 **분리** (메타-텍스트 3종 이관 — *무엇이 심사 대상인가*) + severity-gated exit (PASS 의 severity·처분 조건) / ADR-183 (CFP-3011, 병행 저작) = 심사 정의역 **결속** (`scrutiny_domain` per-finding 필드 — *FIX 발생 자격*) + lane PASS **종결 술어** (coverage 명제) + 병리 판별. 두 축 = disjoint-상보: 분리 = 대상 집합 축 / 결속 = finding 자격 축이며, §결정 2 exit 의 severity·처분 조건 ∧ ADR-183 종결 coverage 술어는 **conjunction 으로 양립**한다.
- **정합 규칙**: 둘 다 accepted 시 최종 PASS = 본 ADR §결정 2 exit ∧ ADR-183 종결 술어. `review-pl-base.md` §3 배선 시 충돌 발견 → **후행 편입자 (ADR-183 / CFP-3011) 정합 의무** (본 ADR 선착 머지 기준). **본 절은 ADR-183 의 결정을 예단·구속하지 않는다** (경계 선언 한정).
- **저작 시점 실측 라벨**: ADR-183 = 본 절 저작 시점 (2026-08-17) branch `cfp-3011` @`f11b26f2`·PR #3012 state OPEN **미머지** (firsthand: `gh pr view 3012` + `git ls-remote origin cfp-3011`) — 상태 가변 표면이므로 이후 참조 시 재측정 의무 ("미머지" 는 저작 시점 한정 실측. frontmatter `related_adrs` 미등재 사유 = 미머지 가변 대상의 고정 참조 회피).

### AC 매핑 표 (13건 zero-drop)

**본 Story 의 AC 충족 정의 = 판정 기록 (본 ADR 성문) + 배선 carrier 지정 (Story key 명시)** — **본 Story 가 소유하지 않는 면 (B=CFP-2985 · C=CFP-2986 · 후속 배선 Story · #2988) 이면** 파일 diff 를 충족 조건으로 요구하지 않는다 (AC-3a verification 문면 그대로, 전 AC 로 일반화).

| AC | 착지 절 | 충족 형태 | 배선 carrier |
|---|---|---|---|
| AC-0 | §결정 0 | 정본 단일값 + 28 hit 3-bucket 전건 종결 + 수렴 계획 5좌표 특정 | 수렴 커밋 = 후속 배선 Story |
| AC-1a | §결정 1 | 분리 채택 판정 + closed-enum 3종 | scope 문면 = 후속 배선 Story |
| AC-1b | §결정 1 | 심사 scope 한정 + 이관 3종 목적지 (신규 monopoly 섹션) | 골격 = C (CFP-2986) / scope 규정 파일 문면 = 후속 배선 Story |
| AC-1c | §결정 1 | cross-ref 양방향 형식 (row 필수 필드 3종 + 본문 고정 포인터 1줄) | 스키마 = C (CFP-2986) |
| AC-2a | §결정 2 | severity-gated exit 채택 + 도달 가능성 근거 | base §3 = 후속 배선 Story |
| AC-2b | §결정 2 | 시뮬레이션 수행 — PASS 불성립(P1 1) 판별 가능 + 판별 범위 분할 | (본 ADR 내 완결) |
| AC-2c | §결정 2 | 처분 판정원 2종 + CLOSED 판별 기준 | replay 배선 = B (CFP-2985) |
| AC-3a | §결정 3 | 기재 의무 + 위치 (§10 RESET row column) 특정 | 실배선 = B (CFP-2985) |
| AC-3b | §결정 3 | 판별 불가 → RESET 불허·ESCALATE 분기 | 실배선 = B (CFP-2985) |
| AC-4a | §결정 4 | 적용 채택 (boolean true) + 비편입 경계 조건 + 수신자 전원 | 처방 본문 = #2988 |
| AC-5a | §결정 5 | transition 3-상태 표 | (본 ADR 내 완결) |
| AC-5b | §결정 5 | MTD-1944 재개 조항 (14회차 신 exit·RESET 5회 유효·카운터 2/3 동결 이월) | (본 ADR 내 완결) |
| AC-5c | §결정 5 | 조정 규칙 3항 사전 명문화 | (본 ADR 내 완결) |

### NF4 처분 표 (요구사항리뷰 4회차 defer 5건)

| ID | 처분 | 근거 |
|---|---|---|
| NF4-01 | **해소** | §결정 0 — 3-bucket 필터를 §4.1(d) 이행 전 선적용, ADR-125 4좌표 사전 배정 해제 (firsthand 분류: A delta-0 1 · C 종결 3) |
| NF4-02 | **해소** | §결정 0 — 엔진 고정 명문화 (census·fixture 동일 엔진 `git grep` byte-mode / `grep -E` 시 `LC_ALL=C` 의무) + 본 census 에서 이행 실증 |
| NF4-03 | **해소** | §결정 1·4 — UC-4 「§9·§10 독점」 중 §10 monopoly·§9 final-verdict monopoly 는 **참** (lint `MONOPOLY_SECTIONS`·fix-event-v1 writer·ADR-039 §결정 15-①/②), 비승계 = 「§9 전체 독점」 주장 한정 (§9 하위 서술 = lint 다중 owner — §결정 1 L119 3항 분해와 동일 문면), 이관 목적지 = 신규 monopoly 섹션 (§9 아님) |
| NF4-04 | **해소** | §결정 0 — bucket C 수신자 = 본 설계 lane (본 ADR), 기록 artifact = census 분류 표 (좌표 병기·@4b30b860 한정 — presence-testable) |
| NF4-05 | **해소** | 본 ADR 의 capture-recapture 인용 귀속 = **Petersson, Thelin, Runeson & Wohlin, "Capture–recapture in software inspections after 10 years research", Journal of Systems and Software 72(2):249-264, 2004** (Story §6.6 원문은 무접촉 — 정정 귀속은 본 ADR 부터 사용) |

### 정직 천장

- **§1 정량치의 한계**: 46.6%/78.6%/4.2배는 단일 Story(MTD-1944) 실측 + blame 은 12·13회차 한정이며, 13회차 리뷰 산출물은 원격 미push 로 **일부 재현 불가** (Story §4.3 정직 천장 승계). 일반화 근거 = 독립 2사례(CFP-2949·CFP-2908)의 존재 사실뿐. 본 ADR 은 이 수치를 metric 으로 신설하지 않는다 (ADR-067 §결정 6 surface-area metric 기각 선례 — 정성 판정 축으로만 사용).
- **기계 게이트 가능 vs advisory 구분 (Story §4.2 표 승계)**: §2-§6 내 `[FIX iter` 마커 0건 = 기계 가능(fail-closed) / 메타-텍스트의 목적지 존재 = presence 가능 / 산문형 메타의 §2-§6 부재 = **advisory** / 심사 워커가 실제로 §1-§6 만 봤는가 = **advisory** / P0·P1 0·처분 CLOSED = 기계 가능 / 잔여 분류 정확성 = **advisory** (분류자=수혜자) / RESET column 기재 = presence 가능·값의 정확성 = **advisory** (dual-peer 반증으로 완화, 강제 불가). **"100% 기계강제" 주장 금지** — 위 "가능" 전부를 배선해도 근본(FIX 산출물이 새 심사 대상이 되는 것)은 완전 봉인되지 않는다.
- **AC 게이트 현황 (TestContractArch 이의 A·B firsthand — 정직 declare)**: `ac-traceability-matrix`·`ac-schema-authoring-gate` 는 본 Story 에서 **비적용 PASS (vacuous)** 상태다 — Story §1 verbatim 내부의 `## 5.` 등 헤딩 shadowing 을 first-match slicing 이 오선택. 따라서 13 AC zero-drop 의 기계 강제 = 현재 0 이며 RTM 은 수기 채널 (RR4 RO-1 + Change Plan §8) 이다. 부가 (이의 B — **기해소**): §5.3 `source: analyst` 4건 (AC-0/2b/3b/5c) ∉ 계약 enum `("user","derived")` 잠복은 internal-docs `9a25c46a` 에서 정정 완료 (analyst 0 / derived 4 — Orchestrator relay 이행, 원자 결합의 선행 절반). 잔여 = slicing 정정 단독 (§편입 지시 5항) + `test_ac_source_enum_matches_contract_enum` 회귀 확인.
- **§1 immutable 의 기계 보호 범위**: 기계 검증 슬라이스 = §1 heading 부터 첫 `## 2.` 까지 9행 한정 (verbatim 내부 헤딩 shadowing 동일 기전) — 95행 verbatim 블록의 잔여 86행은 **수기 채널** (sha256 대조). "§1 immutable = 기계 보증" 으로 서술하지 않는다.
- **외부 인용**: 전건 source 병기. IEEE 1028-2008 은 verbatim 조항 미확보 (2차 corroboration 만 — 유료 표준 원문 미접근, Story §9.4 확인 불가 기재 승계).

## 결과

- **종료 조건이 도달 가능해진다**: 심사 정의역에서 메타-텍스트 3종이 제거되고 (§결정 1), PASS 가 severity-gated exit 로 정밀화되어 (§결정 2) bad-fix 상수 하에서도 P2/P3 잔여를 등재 처분으로 exit 할 수 있다. MTD-1944 시뮬레이션이 신 조건의 판별 가능성을 실증했다.
- **RESET 이 구조 축으로 판별된다**: 술어 개선 단독 재-RESET 이 차단되어 (§결정 3) "같은 구조 안에서 술어만 갈아끼우는" 5회 RESET 경로가 재발하지 않는다.
- **원장 정의역에 품질 기준이 부과된다** (§결정 4) — 심사 편입 없이.
- **파일면 변경 0 으로 판정이 확정된다**: B/C 소유면·비분할면 전건 무접촉 (병렬 3 Story 충돌 0). 실배선 = §편입 지시 3 carrier (B·C·후속 배선 Story 1건).
- **트레이드오프**: 수리 이력과 요구사항 문면의 물리 거리 증가 — cross-ref 양방향 요건 (AC-1c) 으로 보상하되, 인접 마커 대비 추적 hop 이 1 증가하는 것은 수용한다.
- **리스크 (정직)**: 신규 monopoly 섹션 번호·골격 확정이 C(CFP-2986) 편입에 종속 — C 지연 시 §결정 1 실효도 지연된다 (판정 자체는 유효). 심사 워커의 실 준수는 advisory 로 남는다.

## 관련 파일

- `archive/adr/ADR-067-fix-ledger-implementability-escalation.md` — §결정 3 amendment 대상 (B 편입, 본 ADR 무접촉)
- `archive/adr/ADR-125-requirements-review-lane.md` — write 표면 disjoint 축 확장 대상 (후속 배선 Story, 본 ADR 무접촉)
- `docs/inter-plugin-contracts/fix-event-v1.md` — 신규 column·lane enum 정산 대상 (B 편입, 본 ADR 무접촉)
- `templates/story-page-structure.md` — 신규 증적 monopoly 섹션 골격 대상 (C 편입, 본 ADR 무접촉)
- `plugins/codeforge-review/templates/review-pl-base.md` — §3 판정표 정밀화 대상 (후속 배선 Story)
- `plugins/codeforge-review/agents/RequirementsReviewPLAgent.md` — bucket A 수렴 2좌표 (후속 배선 Story)
- `skills/review-responsibility/SKILL.md` — bucket A 수렴 1좌표 (후속 배선 Story)
- `plugins/codeforge-review/docs/architecture/codeforge-review.md` — bucket A 수렴 2좌표 (후속 배선 Story)
- `scripts/lib/check_story_section_ownership.py` — `SECTION_OWNERS["9"]` 다중 owner·`MONOPOLY_SECTIONS` "10" 실측 근거 (본 Story 무접촉 — C 편입 시 신규 증적 섹션 등재 대상, §편입 지시 C-5)
