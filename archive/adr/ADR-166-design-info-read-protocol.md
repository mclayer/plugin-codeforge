---
adr_number: 166
title: 설계 정보 읽기 프로토콜 (design-info read protocol) — Living Architecture 1차 소스 승격 + G1-G5 소비자 분류 + reader-side 배선
date: 2026-07-24
status: Active
category: governance
carrier_story: CFP-2813
supersedes: null
amends: null  # new-sibling — ADR-078(what/where)·ADR-112(update timing)·ADR-124/125/126(외부지식 축) 무변경. §결정 1 non-amendment 판정.
related_adrs:
  - ADR-078  # Living Architecture SSOT origin (4 H2 closed-enum + Amd2 5-anchor) — 본 ADR 의 read 대상 정의. Amd3(CFP-2813) = per-PR granularity 확정 (본 ADR 의 (a) 선결 게이트 짝)
  - ADR-112  # update gate (when/how-to-mark) — 본 ADR 은 read 축 (소비 방향). write 축과 disjoint. Amd1(CFP-2813) = per-PR default + blocking-on-pr(surfacing) tier
  - ADR-124  # 외부지식 충당 3-단계 — disjoint axis: 외부 사실 소스 우선순위 ↔ 본 ADR = 내부 현재상태 소스 우선순위 (양 축 병존, 충돌 0)
  - ADR-125  # 요구사항리뷰 lane — 현행 scope = 다축: 외부사실(§결정 6) + internal-invariant falsification(Amd2, runtime-failure 변종) + 내부 시스템 적합성(Amd3 결정 B — 아키텍처 구현가능성·과거 결정 충돌·중복의 Read 대조). Amd3 결정 B 가 RequirementsReviewPL 의 G2 편입 근거 (§결정 2 — 설계리뷰 F-2 재판정, 구 "외부사실 단일 축" 인용은 stale 이었음)
  - ADR-142  # Orchestrator context 위임 L1 — 본 ADR 의 Orchestrator 제외 근거 (read 프로토콜 = lane-agent 계층 한정, T-1 해소 조건)
  - ADR-118  # 모노레포 D5 — inter-plugin contract wrapper 단일 원본 (본 프로토콜 계약 파일의 등록 채널 근거)
  - ADR-039  # spawn/발화 monopoly — 주입 지점(agent .md / base / spawn packet)의 구조 제약 (spawn 구조 무변경)
  - ADR-119  # research-before-claims — advisory ceiling 정직 라벨 의무 ("읽었음" 기계 증명 불가 — hollow did-you-read 게이트 금지)
  - ADR-100  # git = SoR-work — read 대상의 authoritative source (Confluence = readable mirror, ADR-078 Amd2 dual-read 는 G1 1-agent scoped 유지)
  - ADR-127  # 정식 full 8-lane + Phase 1/2 PR 분리
related_stories:
  - CFP-2813
related_files:
  - docs/inter-plugin-contracts/design-info-read-protocol-v1.md  # Phase 2 계약 파일 (본 ADR §결정 verbatim 미러, kind:registry)
  - docs/inter-plugin-contracts/MANIFEST.yaml  # Phase 2 registries row append
  - plugins/codeforge-review/templates/review-pl-base.md  # G2 리뷰 PL 4 전원 주입 표면 (Phase 2 — per-PL 예외 0)
  - plugins/codeforge-requirements/agents/DomainAgent.md  # G2 (Phase 2)
  - plugins/codeforge-requirements/agents/FeasibilityAgent.md  # G2 (Phase 2)
  - plugins/codeforge-requirements/agents/ChangeImpactAgent.md  # G2 (Phase 2)
  - plugins/codeforge-requirements/agents/ContinuityAgent.md  # G2 (Phase 2)
  - plugins/codeforge-design/agents/CodebaseMapperAgent.md  # G2 (Phase 2)
  - plugins/codeforge-design/agents/ArchitectAnalystAgent.md  # G1 기배선 — protocol v1 cross-ref 정렬 (Phase 2)
  - docs/architecture/codeforge-family.md  # interfaces + data_flow 갱신 (Phase 1 반영 완료)
is_transitional: false
mechanical_enforcement_actions: []  # 읽기 행위는 원리상 기계 강제 불가 (advisory ceiling — §결정 5). 배선 presence 는 grep-실측 가능하나 mechanical lint 신설 0 (검사연극 금지, ADR-119 §결정 6). (a) 게이트 축의 mechanical action 은 ADR-078/112 소유.
---

# ADR-166: 설계 정보 읽기 프로토콜 (design-info read protocol)

## 상태

**Active (2026-07-24 KST)** — ArchitectAgent direct write per ADR-070 chief author precedent. CFP-2813 carrier (Phase 1 PR). 실 배선 = 동일 Story Phase 2.

`is_transitional: false` — permanent governance invariant (ADR-058 §결정 7 governance default presumption).

## 컨텍스트

사용자 확정 진단 (CFP-2813 Story §1, 2026-07-23): 현재상태 설계 SSOT(Living Architecture, ADR-078 7 doc)를 읽는 에이전트가 ArchitectAnalystAgent 1곳뿐 — 그 외 lane 에이전트는 append-only 이력(archive/adr 164개)·change-plan·story 조각에서 현재 상태를 매번 재구성한다. 이 **layer 오용**(현재상태 질문에 결정-이력 소스를 읽음)이 "단편적으로 읽어 잘못된 정보"의 구조적 원인이다 (Story §2.1).

외부 근거 (Story §6 재사용 — ADR-119 인용):
- **canonical source 부재** 가 동일 증상(경쟁 조각 문서 → 오정보)을 만든 실증 — source: Google SWE book ch.10 (abseil.io/resources/swe-book/html/ch10.html).
- **읽기 표준의 dead-letter 실패 모드**: llms.txt 는 표준 선언 + 채택 성장에도 파일 97% 가 AI 요청 0건 — reader-side 배선 없는 read 표준은 죽은 문서다 — source: ppc.land 실측 (Story §6.3). → 본 프로토콜은 선언이 아니라 **주입 표면 배선**으로 정의한다.
- **context rot**: 입력 길이 증가 시 정확도 비균일 하락 — 전 lane 전문(full-doc) 강제 주입은 역효과 — source: trychroma.com/research/context-rot. → 부분집합 anchor 정책.
- **이력/현재 분리**: 현재-상태 뷰를 별도 유지하고 append-only 에서 매번 재구성하지 않는 것이 ADR 커뮤니티 표준 해법 — source: adr.github.io/adr-tooling/ + Diátaxis reference/explanation 유형 분리 (diataxis.fr).

## 결정

### §결정 1 — ADR 형태 판정 (신규 ADR — A2-5 both-prong, AC-14 단일 결정 기록)

- **Amendment prong (ADR-078/112 로 착륙) = 기각**: ADR-078 = 문서의 what/where, ADR-112 = write timing(update gate). 본 결정 = **소비(read) 방향의 cross-lane 행위 계약** — write 축 ADR 에 얹으면 subject 오염 (disjoint axis: 갱신 의무 ↔ 읽기 의무). ADR-078 Amd2 dual-read 는 ArchitectAnalyst 1-agent scoped 로 유지 (본 ADR 이 supersede 하지 않음).
- **Amendment prong (ADR-124/125/126 으로 착륙) = 기각**: 그 계열 = **외부지식** 충당 축 (WebSearch/deep-research). 본 ADR = **내부 현재상태** 소스 축 — 소스 도메인 disjoint (ArchitectAnalyst 실측: collision-free, 기존 home 부재).
- **신규 ADR prong = 채택**: (i) distinct context — 1-agent read 배선의 40-agent 확대 요구 (ii) distinct decisions — G1-G5 소비자 분류 + mandatory/on-demand/제외 3-tier + anchor 부분집합 + 우선순위 규칙 (iii) distinct result — 신규 inter-plugin 계약 등록 + 9-agent 배선. → **ADR-166**. 게이트 축 = ADR-078 Amd3 + ADR-112 Amd1 분할 (Story §2.7 C-3 확정, Change Plan §10).

### §결정 2 — 1차 소스 선언 + 소비자 그룹 분류 (G1-G5)

**Living Architecture 7 doc = "현재 상태(지금 어떻게)"의 canonical source 로 선언한다** (Story §6.5 R1). 층위 규칙: 현재 상태 질문 → `docs/architecture/` 1차 / ADR = "왜 결정"(explanation, on-demand) / change-plan = "이번에 무엇을"(델타, on-demand). append-only 이력에서 현재 상태를 재구성하는 것은 본 프로토콜 위반 경로다.

**소비자 그룹 (Story §2.4 codify + agent 명 단위 확정)**:

| 그룹 | agent | 의무 |
|---|---|---|
| G1 (현재상태 1차 소비자) | ArchitectAnalystAgent | mandatory (기배선 — dual-read 유지 + 본 계약 cross-ref) |
| G2 (재구성 소비자 — 편입 9) | DomainAgent · FeasibilityAgent · ChangeImpactAgent · ContinuityAgent · CodebaseMapperAgent · DesignReviewPLAgent · CodeReviewPLAgent · SecurityTestPLAgent · RequirementsReviewPLAgent | mandatory 선행 read |
| G3 (델타·근거 소비자) | DeveloperAgent 계열 · QADeveloperAgent · RefactorAgent | on-demand (강제 0) |
| G4 (write 주체) | ArchitectAgent · PMOAgent | 대상 아님 (쓰는 쪽) |
| G5 (실행·검증 leaf) | TestAgent · IntegrationTestAgent · Security leaf | 대상 아님 |
| 제외 | **Orchestrator** | 강제 금지 — ADR-142 L1 정합 (raw read 는 lane-agent 계층으로 위임되는 구조. T-1 해소 조건) |

**RequirementsReviewPL 의 G2 편입 근거 (설계리뷰 F-2 재판정 — ADR-125 현행 다축 기준)**: ADR-125 는 "외부사실 단일 축"이 아니다 — 현행 scope = 외부사실(§결정 6) + internal-invariant falsification(Amd2) + **내부 시스템 적합성(Amd3 결정 B)** 다축. 결정 B 는 "아키텍처 구현가능성·과거 결정 충돌·중복"을 dual-peer 의 "설계문서(ADR·Change Plan)·과거 Story·ADR Read 대조"로 검증하도록 mandate — 즉 이 lane 은 **현재상태(as-is 아키텍처) 대조를 정식 mandate 로 보유**하며, 그 현행 소스가 정확히 본 ADR 이 병으로 규정한 layer 오용(append-only 이력에서 현재상태 재구성)이다 → G2 정의("현재상태 필요하나 이력 조각에서 재구성") 문언 충족. 리뷰 PL 3 편입 논리(동일 packet-종합 구조)와의 일관성도 G2 를 지지한다. **hypothesis-withheld packet 규율(Amd3 결정 B)과 무저촉**: packet 에서 숨기는 것 = 작성측 자가분석 결론(Feasibility/Continuity 진단)이고, Living Architecture 는 작성측 결론이 아닌 중립 canonical 현재상태 — 오히려 내부적합 축의 독립 대조 ground 를 이력 재구성에서 canonical source 로 격상한다. (구 판정 "외부사실 단일 축 → G3" 은 ADR-125 stale 인용이었음 — I-7 정정.)

### §결정 3 — mandatory 선행 read 의 형태 (부분집합 anchor + 2-doc ceiling + 4 H2 fallback)

- **read 대상**: 작업 대상 plugin 의 `plugins/<X>/docs/architecture/<X>.md` + `docs/architecture/codeforge-family.md` — **최대 2-doc ceiling**. 대상 plugin 특정 불가 작업 = family.md 만.
- **부분집합 anchor 정책 (compact 계층 — 신규 요약 파일·신규 anchor 0)**: mandatory floor = **arc42 §5 Building Block View 1-anchor** + 작업 관련 anchor on-demand. 그룹별 권장 = Domain/Continuity → §5 + Open Decisions Pending / ChangeImpact/CodebaseMapper → §5 + C4 Component / Feasibility → §5 + C4 Container / 리뷰 PL 4 → §5 floor + 심사 대상 관련 anchor (RequirementsReviewPL = + Open Decisions Pending — 내부적합 축의 과거 결정 충돌·중복 대조에 자연 정합). 전문 pre-embed 금지 (context rot — source: trychroma.com). 신규 요약 파일 신설 금지 — 요약 계층 신설 = 그 요약 자체의 stale 재귀 (Structurizr 모델-생성 계열의 실패 모드, Story §6.2) + ADR-078 Amd2 open_extension:false 위반.
- **5-anchor 부재 fallback**: 대상 doc 에 5-anchor section 이 없으면 (실측: 6 lane plugin doc 전부 — family.md 만 보유) **4 H2 closed-enum(모듈/경계/인터페이스 계약/데이터 흐름) fallback read**. 5-anchor 점진 backfill 은 (a) 게이트(ADR-112 Amd1)의 per-PR 갱신 기회가 유도 — 본 프로토콜이 backfill 을 강제하지 않는다.

### §결정 4 — reader-side 배선 (in-band 주입 + 계약 등록 — dead-letter 방지)

- **배선 = 주입 표면 결박**: read 지시를 agent .md(요구 4 + Mapper + ArchitectAnalyst) / `review-pl-base.md`(리뷰 PL 4 전원 — per-PL 예외 0, 주입 단순화) 에 **self-contained 요지 + SSOT pointer** 로 in-band 저작. 문서 content 는 path-reference 자기주도 fetch (전문 pre-embed 금지 — ArchitectAnalyst 현행 배선 형식 답습). "문서화-후-권고"는 금지 실패 모드 (llms.txt dead-letter — source: ppc.land).
- **SSOT = `docs/inter-plugin-contracts/design-info-read-protocol-v1.md`** (kind:registry, wrapper 단일 원본 — ADR-118 D5) + MANIFEST row. wrapper root `templates/` cross-plugin base 는 기각 — marketplace 배포 시 lane plugin 패키지(`plugins/<lane>/`)에 wrapper-root 파일 미포함이라 consumer 환경 파일 참조 resolve 불가 + cross-plugin 파일시스템 결합 선례 0. 기존 계약과 동일하게 **소비 = spawn packet/agent .md in-band**, 파일 참조 아님. lane-local 복수 사본 = 사본 분기(AC-2 위반) 기각.
- **압축 주체 = per-agent 자기주도 read**: PL 1회 압축 fan-out 기각 — "한쪽이 다른 쪽의 요약에 의존하지 않음" 독립 관점 invariant (codeforge-design CLAUDE.md) 위반 + 압축 오류 single point.

### §결정 5 — read 추적 + advisory ceiling (정직 천장)

- **traceability marker**: 프로토콜 수행 산출물 선두 1줄 — `[Living-Arch-Read: <doc-basename>, anchors=<list>, read_at=<HEAD sha7 | ISO ts>]` (grep 가능).
- **advisory ceiling (불가침)**: "실제로 읽고 반영했는가"는 기계 검증 불가 — marker = 추적 표면이지 read 증명이 아니다. **hollow "did-you-read" 기계 게이트 배선 금지** (검사연극 — ADR-119). 실 반영 확인 = 산출물 표본 review (AC-3/AC-16 검증 방식). mechanical_enforcement_actions = [] 는 이 천장의 frontmatter 표현이다.
- **divergence 처리**: arch doc ↔ 실코드 충돌 발견 시 실측(코드)이 우선 — 산출물에 divergence 명시 (ArchitectAgent 갱신 신호, DesignReviewPL `living-architecture-not-updated` L3 채널과 합류). git ↔ Confluence divergence = git 우선 (ADR-100, G1 dual-read scoped).

### §결정 6 — rollout 순서 + scope (freshness 선결 조건)

- **(a) 게이트 선행 binding**: 본 프로토콜의 mandatory 발효 = ADR-112 Amd1 게이트 활성 **이후** (stale 소스를 표준 read 경로로 중앙집중화하는 자기모순 방지 — Story §5.2 가정 ④/§7.0-8). 이행 = CFP-2813 Phase 2 PR 이 게이트 wire + 6 lane doc stale 해소 실갱신을 프로토콜 배선과 동반 (Change Plan §9.R ①).
- **scope**: wrapper = normative / consumer = capability-conditional 자동 적용 (`docs/architecture/*.md` 보유 시 — 보유 강제 도입은 scope 밖) / Orchestrator = 제외. 암묵 확장 금지 (AC-11).

## 거절된 대안

- **전 41 agent 균일 mandatory**: context rot 비용·품질 역효과 (source: trychroma.com) + G4(write 주체)/G5(leaf) 는 무-target — 기각, G1+G2 한정 (Story §2.7 C-5).
- **PL 1회 압축 fan-out**: 독립 관점 invariant 위반 + 압축 single point — 기각 (§결정 4).
- **신규 compact summary 파일 계층**: 요약 자체 stale 재귀 + open_extension:false 위반 — 기각 (§결정 3).
- **wrapper root templates/ cross-plugin base**: marketplace 패키징 resolve 불가 + 선례 0 — 기각 (§결정 4).
- **read 여부 기계 게이트**: 원리상 검증 불가 — hollow gate = 검사연극 — 기각 (§결정 5).

## 결과

- **긍정**: 40-agent 재구성 read 의 구조적 오정보 채널 축소 (layer 오용 해소) + 설계 정보 획득 경로 단일화 (canonical source) + ADR-142 context 위임 intent 의 lane-agent 계층 materialize.
- **부정/비용**: G2 9-agent spawn 당 read 비용 증가 (부분집합 anchor + 2-doc ceiling 으로 상한) / read 대상 freshness 의존 — (a) 게이트가 선결 조건 (§결정 6).
- **신규 required context 0 / branch protection 8-tuple 무변경 / 신규 category 0** (governance 재사용). ADR-058 §결정 5 — 강화(ratchet) 방향, sunset_justification N/A.
- Phase 1 = 본 ADR + Change Plan §3.6 + family.md interfaces/data_flow 반영. Phase 2 = 계약 파일 + MANIFEST row + 9 주입 표면 배선 (Change Plan §5 #13-21).

## 해소 기준

N/A — permanent policy (governance 영구 invariant, ADR-058 §결정 7). 약화 방향 (G2 축소 / mandatory 해제 / marker 폐지) = ADR-058 §결정 5 sunset_justification 의무.

## 관련 파일

- [ADR-078](ADR-078-living-architecture-doc.md) — read 대상 SSOT (Amd3 = per-PR granularity 확정)
- [ADR-112](ADR-112-living-architecture-update-gate.md) — freshness 게이트 (Amd1 = 본 프로토콜의 선결 조건)
- `docs/inter-plugin-contracts/design-info-read-protocol-v1.md` — Phase 2 계약 파일 (본 ADR verbatim 미러)
- Change Plan: `codeforge-internal-docs/wrapper/change-plans/cfp-2813-living-arch-primary-source.md` — 배선 상세 (§3.6/§5/§9.R)
