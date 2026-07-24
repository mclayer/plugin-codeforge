---
kind: registry
registry: design-info-read-protocol
version: "1.0"
status: Active
canonical_repo: mclayer/plugin-codeforge
canonical_path: docs/inter-plugin-contracts/design-info-read-protocol-v1.md
date: 2026-07-24
authors:
  - ArchitectAgent (CFP-2813 carrier — ADR-166 규범 SSOT, 본 계약 파일 = ADR-166 §결정 verbatim 미러)
  - DeveloperAgent (CFP-2813 Phase 2 — 계약 파일 + reader-side 배선 실배선)
version_history:
  - { version: "1.0", date: 2026-07-24, carrier: CFP-2813, change: "initial — design-info read protocol schema SSOT 신설. Living Architecture 1차 소스 선언 + G1-G5 소비자 분류 + G1+G2 mandatory 선행 read + 부분집합 anchor 정책(arc42 §5 Building Block View floor + 그룹별 권장) + 5-anchor 부재 4 H2 closed-enum fallback + traceability marker(advisory ceiling) + 우선순위 규칙 + Orchestrator 제외(T-1). ADR-166 §결정 2-6 mirror." }
related_adrs:
  - ADR-166  # 규범 SSOT (본 계약 = verbatim 미러). design-info read protocol carrier
  - ADR-078  # Living Architecture 7 doc read 대상 정의 (4 H2 closed-enum + Amd2 5-anchor + Amd3 per-PR granularity)
  - ADR-112  # Living Architecture update gate (freshness 선결 조건 — Amd1 per-PR default + blocking-on-pr(surfacing) tier)
  - ADR-124  # 외부지식 충당 3-단계 — disjoint axis (외부 사실 소스 ↔ 본 계약 = 내부 현재상태 소스). 충돌 0
  - ADR-125  # 요구사항리뷰 lane 현행 다축 (Amd3 결정 B 내부 시스템 적합성 축 = RequirementsReviewPL G2 편입 근거)
  - ADR-142  # Orchestrator context 위임 L1 — Orchestrator 제외 근거 (read = lane-agent 계층, T-1 해소 조건)
  - ADR-118  # 모노레포 D5 — inter-plugin contract wrapper 단일 원본 (본 계약 등록 채널 근거)
  - ADR-039  # spawn/발화 monopoly — 주입 지점(agent .md / base / spawn packet) 구조 제약 (spawn 구조 무변경)
  - ADR-119  # research-before-claims — advisory ceiling 정직 라벨 의무 (읽음 기계 증명 불가, hollow did-you-read 금지)
  - ADR-100  # git = SoR-work — read 대상 authoritative source (Confluence = readable mirror, G1 dual-read scoped)
related_files:
  - docs/inter-plugin-contracts/MANIFEST.yaml  # registries row (design-info-read-protocol)
  - plugins/codeforge-review/templates/review-pl-base.md  # G2 리뷰 PL 4 전원 주입 표면 (per-PL 예외 0)
  - plugins/codeforge-requirements/agents/DomainAgent.md  # G2
  - plugins/codeforge-requirements/agents/FeasibilityAgent.md  # G2
  - plugins/codeforge-requirements/agents/ChangeImpactAgent.md  # G2
  - plugins/codeforge-requirements/agents/ContinuityAgent.md  # G2
  - plugins/codeforge-design/agents/CodebaseMapperAgent.md  # G2
  - plugins/codeforge-design/agents/ArchitectAnalystAgent.md  # G1 기배선 — 본 계약 cross-ref 정렬
  - docs/architecture/codeforge-family.md  # read 대상 (5-anchor + 4 H2 보유)
  - archive/adr/ADR-166-design-info-read-protocol.md  # 규범 SSOT
producers:
  - ArchitectAgent  # 규범 SSOT owner (ADR-166), Living Architecture 7 doc write monopoly
consumers:  # 프로토콜 준수 대상 (선행 read 수행 주체) — G1 + G2
  - codeforge-design/ArchitectAnalystAgent  # G1 mandatory (기배선 dual-read + 본 계약 cross-ref)
  - codeforge-requirements/DomainAgent  # G2 mandatory
  - codeforge-requirements/FeasibilityAgent  # G2 mandatory
  - codeforge-requirements/ChangeImpactAgent  # G2 mandatory
  - codeforge-requirements/ContinuityAgent  # G2 mandatory
  - codeforge-design/CodebaseMapperAgent  # G2 mandatory
  - codeforge-review/DesignReviewPLAgent  # G2 mandatory (review-pl-base 공용 주입)
  - codeforge-review/CodeReviewPLAgent  # G2 mandatory (review-pl-base 공용 주입)
  - codeforge-review/SecurityTestPLAgent  # G2 mandatory (review-pl-base 공용 주입)
  - codeforge-review/RequirementsReviewPLAgent  # G2 mandatory (review-pl-base 공용 주입 — F-2 재판정)
---

# design-info-read-protocol-v1 registry

## 상위 SSOT 위치

본 파일이 canonical SSOT — wrapper-owned, lane-agnostic registry (kind:registry, wrapper 단일 원본 — ADR-118 D5). sibling repo verbatim mirror 없음 (kind:contract 와 구분). **규범 SSOT = [ADR-166](../../archive/adr/ADR-166-design-info-read-protocol.md)** — 본 계약 파일은 ADR-166 §결정 2-6 의 verbatim 미러다. 판정 상충 시 ADR-166 우선.

## 1. 목적

Living Architecture(현재상태 구조 문서, ADR-078 7 doc) 를 **모든 작업의 1차 설계 정보 소스**로 승격하고, 그 선행 read 를 소비자 agent 의 **reader-side 배선(agent .md / base 주입 표면)** 에 결박한다. 병인 = 현재상태 질문을 append-only 이력(archive/adr) 조각에서 재구성하는 **layer 오용** → "단편적으로 읽어 잘못된 정보". 선언-only read 표준은 dead-letter(llms.txt 실증, source: ppc.land) 이므로 본 프로토콜은 선언이 아니라 **주입 표면 배선**으로 정의한다.

## 2. 1차 소스 선언 + 소비자 그룹 분류 (G1-G5 — ADR-166 §결정 2)

**Living Architecture 7 doc = "현재 상태(지금 어떻게)"의 canonical source.** 층위 규칙: 현재 상태 질문 → `docs/architecture/` 1차 / ADR = "왜 결정"(explanation, on-demand) / change-plan = "이번에 무엇을"(델타, on-demand). append-only 이력에서 현재 상태를 재구성하는 것은 본 프로토콜 위반 경로다.

| 그룹 | agent | 의무 |
|---|---|---|
| G1 (현재상태 1차 소비자) | ArchitectAnalystAgent | **mandatory** (기배선 — git primary / Confluence fallback dual-read 유지 + 본 계약 cross-ref) |
| G2 (재구성 소비자 — 편입 9) | DomainAgent · FeasibilityAgent · ChangeImpactAgent · ContinuityAgent · CodebaseMapperAgent · DesignReviewPLAgent · CodeReviewPLAgent · SecurityTestPLAgent · RequirementsReviewPLAgent | **mandatory 선행 read** |
| G3 (델타·근거 소비자) | DeveloperAgent 계열 · QADeveloperAgent · RefactorAgent | on-demand (강제 0 — 프로토콜이 on-demand 역할 규정) |
| G4 (write 주체) | ArchitectAgent · PMOAgent | 대상 아님 (쓰는 쪽) |
| G5 (실행·검증 leaf) | TestAgent · IntegrationTestAgent · Security leaf | 대상 아님 |
| 제외 (T-1) | **Orchestrator** | **강제 금지** — ADR-142 L1 정합 (raw read 는 lane-agent 계층으로 위임되는 구조) |

**RequirementsReviewPL 의 G2 편입 근거 (설계리뷰 F-2 재판정)**: ADR-125 는 "외부사실 단일 축"이 아니다 — 현행 scope = 외부사실(§결정 6) + internal-invariant falsification(Amd2) + **내부 시스템 적합성(Amd3 결정 B)** 다축. 결정 B 는 "아키텍처 구현가능성·과거 결정 충돌·중복"을 설계문서(ADR·Change Plan)·과거 Story·ADR Read 대조로 검증하도록 mandate — 이 lane 은 현재상태(as-is 아키텍처) 대조를 정식 mandate 로 보유하며 그 현행 소스가 정확히 본 프로토콜이 병으로 규정한 layer 오용이다 → G2 정의 문언 충족. **hypothesis-withheld packet 규율(Amd3 결정 B)과 무저촉**: packet 에서 숨기는 것 = 작성측 자가분석 결론이고, Living Architecture 는 작성측 결론이 아닌 중립 canonical 현재상태다.

## 3. mandatory 선행 read 의 형태 (부분집합 anchor + 2-doc ceiling + 4 H2 fallback — ADR-166 §결정 3)

- **read 대상**: 작업 대상 plugin 의 `plugins/<X>/docs/architecture/<X>.md` + `docs/architecture/codeforge-family.md` — **최대 2-doc ceiling**. 대상 plugin 특정 불가 작업 = **family.md 만**.
- **부분집합 anchor 정책 (compact 계층 — 신규 요약 파일·신규 anchor 0)**: mandatory floor = **arc42 §5 Building Block View 1-anchor** + 작업 관련 anchor on-demand. 전문(full-doc) pre-embed 금지 (context rot — source: trychroma.com/research/context-rot). 신규 요약 파일 신설 금지 (요약 자체 stale 재귀 + ADR-078 Amd2 open_extension:false 위반).

  **그룹별 권장 anchor**:

  | 그룹 | 권장 anchor (floor = arc42 §5 Building Block View) |
  |---|---|
  | DomainAgent · ContinuityAgent | §5 + Open Decisions Pending |
  | ChangeImpactAgent · CodebaseMapperAgent | §5 + C4 Component |
  | FeasibilityAgent | §5 + C4 Container |
  | 리뷰 PL 4 (Design/Code/Security/RequirementsReview) | §5 floor + 심사 대상 관련 anchor (RequirementsReviewPL = **+ Open Decisions Pending** — 내부적합 축의 과거 결정 충돌·중복 대조에 자연 정합) |
  | ArchitectAnalystAgent (G1) | 기배선 5-anchor 전체 dual-read 유지 (본 계약이 축소하지 않음) |

- **5-anchor 부재 fallback**: 대상 doc 에 5-anchor section 이 없으면 (실측: 6 lane plugin doc 전부 — 5-anchor 는 family.md 만 보유) **4 H2 closed-enum(`## 모듈` / `## 경계` / `## 인터페이스 계약` / `## 데이터 흐름`) fallback read**. 5-anchor 점진 backfill 은 (a) 게이트(ADR-112 Amd1)의 per-PR 갱신 기회가 유도 — **본 프로토콜이 backfill 을 강제하지 않는다** (schema 강제 = 기존 template/CFP-28 doc-section 게이트 소관).

## 4. reader-side 배선 (in-band 주입 + 계약 등록 — dead-letter 방지 — ADR-166 §결정 4)

- **배선 = 주입 표면 결박**: read 지시를 agent .md(요구 4 + Mapper + ArchitectAnalyst) / `review-pl-base.md`(리뷰 PL 4 전원 — **per-PL 예외 0**, 주입 단순화) 에 **self-contained 요지 + SSOT pointer(계약명 `design-info-read-protocol-v1`)** 로 in-band 저작. 문서 content 는 path-reference 자기주도 fetch (전문 pre-embed 금지 — ArchitectAnalyst 현행 배선 형식 답습). "문서화-후-권고"는 금지 실패 모드(llms.txt dead-letter).
- **SSOT 위치 / marketplace 배포**: 본 계약은 `docs/inter-plugin-contracts/` 소재로 marketplace 배포 시 lane plugin 패키지(`plugins/<lane>/`) 외부다 — 따라서 **소비 = spawn packet / agent .md in-band 지시**, 파일 링크 참조 아님 (기존 inter-plugin contract 소비 관행 답습). wrapper root `templates/` cross-plugin base 는 consumer 환경 resolve 불가 + 선례 0 로 기각. lane-local 복수 사본 = 사본 분기(AC-2 위반) 기각.
- **압축 주체 = per-agent 자기주도 read**: PL 1회 압축 fan-out 기각 — "한쪽이 다른 쪽의 요약에 의존하지 않음" 독립 관점 invariant 위반 + 압축 오류 single point.

## 5. read 추적 marker + advisory ceiling (정직 천장 — ADR-166 §결정 5)

- **traceability marker (AC-3)**: 프로토콜 수행 산출물 **선두 1줄** —

  ```
  [Living-Arch-Read: <doc-basename>, anchors=<list>, read_at=<HEAD sha7 | ISO ts>]
  ```

  grep 가능 표면. `<doc-basename>` = 읽은 arch doc 파일명(예: `codeforge-family.md`, `codeforge-design.md`, 2-doc 시 `,` 구분) / `<list>` = 읽은 anchor 목록(예: `arc42-§5, C4-Component`) / `read_at` = 읽은 시점의 HEAD commit sha7 또는 ISO timestamp.
- **advisory ceiling (불가침)**: "실제로 읽고 반영했는가"는 **기계 검증 불가** — marker 는 추적 표면이지 read 증명이 아니다. **hollow "did-you-read" 기계 게이트 배선 금지** (검사연극 — ADR-119). 실 반영 확인 = 산출물 표본 review (설계리뷰 `living-architecture-not-updated` L3 채널 합류). ADR-166 `mechanical_enforcement_actions: []` 이 이 천장의 frontmatter 표현이다.
- **divergence 처리 (우선순위 규칙 — Story §6.5 R1)**: "지금 어떻게(현재 상태)" 질문 = **arch doc 1차** / ADR = "왜 결정"(explanation) / change-plan = "이번에 무엇을"(델타) 보조. **arch doc ↔ 실코드 충돌 발견 시 = 실측(코드) 우선** + 산출물에 divergence 명시 (ArchitectAgent 갱신 신호, 설계리뷰 L3 채널). git ↔ Confluence divergence = git 우선 (ADR-100, G1 dual-read scoped).

## 6. rollout 순서 + scope (freshness 선결 조건 — ADR-166 §결정 6)

- **(a) 게이트 선행 binding**: 본 프로토콜의 mandatory 발효 = ADR-112 Amd1 게이트(`living-architecture-update`) 활성 **이후** (stale 소스를 표준 read 경로로 중앙집중화하는 자기모순 방지). 이행 = CFP-2813 Phase 2 PR 이 게이트 wire + 6 lane doc stale 해소 실갱신을 프로토콜 배선과 동반.
- **scope matrix (AC-11)**:

  | 대상 | 적용 |
  |---|---|
  | wrapper (plugin-codeforge) | **normative** — G1+G2 mandatory |
  | consumer | **capability-conditional 자동 적용** — `docs/architecture/*.md` 보유 시 동일 분류. 미보유 = honest no-op (arch doc 보유 강제 도입은 scope 밖) |
  | Orchestrator | **제외** (read 강제 금지 — T-1) |

  암묵 확장 금지 (AC-11) — 위 표 밖 대상(G3~G5 mandatory 확장 / Orchestrator 강제) = 본 프로토콜 위반.

## 7. 소비자 in-band 주입 요지 (배선 표면 참조용)

각 소비자 agent .md / review-pl-base 는 아래 self-contained 요지를 in-band 저작한다 (전문 복붙 금지 — 계약명 pointer 만):

1. **선행 read 의무**: 작업/심사 착수 전 Living Architecture 를 1차로 read — 작업 대상 plugin arch doc + `codeforge-family.md` (최대 2-doc, plugin 특정 불가 시 family.md 만).
2. **anchor**: floor = arc42 §5 Building Block View + 그룹별 권장 anchor (§3 표). 5-anchor 부재 doc = 4 H2 closed-enum(모듈/경계/인터페이스 계약/데이터 흐름) fallback. 전문 pre-embed 금지.
3. **marker**: 산출물 선두에 `[Living-Arch-Read: <doc-basename>, anchors=<list>, read_at=<HEAD sha7 | ISO ts>]` 1줄 (advisory — 읽음의 기계 증명 아님).
4. **우선순위**: 현재상태 = arch doc 1차 / ADR = 왜 / change-plan = 델타. arch doc ↔ 실코드 충돌 시 실측 우선 + divergence 명시.
5. **SSOT pointer**: 상세 = 본 계약 `design-info-read-protocol-v1` (kind:registry) + [ADR-166](../../archive/adr/ADR-166-design-info-read-protocol.md).

## 관련 파일

- [ADR-166](../../archive/adr/ADR-166-design-info-read-protocol.md) — 규범 SSOT (본 계약 verbatim 미러 원본)
- [ADR-078](../../archive/adr/ADR-078-living-architecture-doc.md) — read 대상 7 doc SSOT (4 H2 closed-enum + Amd2 5-anchor)
- [ADR-112](../../archive/adr/ADR-112-living-architecture-update-gate.md) — freshness 게이트 (선결 조건)
- `docs/architecture/codeforge-family.md` — read 대상 (5-anchor + 4 H2 보유)
- `plugins/codeforge-design/agents/ArchitectAnalystAgent.md` — G1 기배선 (dual-read)
- `plugins/codeforge-review/templates/review-pl-base.md` — G2 리뷰 PL 4 전원 주입 표면
