---
title: codeforge-design lane 구조 (설계 레인 — Change Plan + ADR 확정)
last_captured: 2026-05-18
kind: architecture_doc
family_ref: ../../../plugin-codeforge/docs/architecture/codeforge-family.md#모듈
---

> **목표 invariant (ADR-078 §결정 1 verbatim)**: 코드 직접 read 없이 architecture_doc 1개 read 로 전체 구조 (모듈 + 경계 + 인터페이스 + 데이터 흐름) 파악.

<!-- 본 file = lane plugin self-owned seed (CFP-969 / Sub-Epic CFP-949 Wave 1, parent Epic CFP-756 / ADR-078).
     누적 현재 상태 SSOT — Story key 독립, 고정 경로. 델타는 Change Plan SSOT (disjoint, ADR-078 §결정 3).
     family-level structure = family_ref (wrapper repo seed) 참조. 본 doc 은 lane internal 구조만 채운다. -->

## 모듈

codeforge-design = 설계 레인 plugin. **Change Plan + ADR 확정** 책임. `[verified: CLAUDE.md @ e6e1398d Sub-agent fan-out table + agents/ tree direct enumeration]` — agent 구성:

**Permanent (8 agent)** — 모든 설계 lane 진입 시 spawn:

| 모듈 (agent) | 역할 | 입장 / 책임 |
|---|---|---|
| **ArchitectPLAgent** | 설계 lane PL (supervisor + FIX 판정자) | ArchitectAgent chief + 6 SubAgent 산출물 검수 + final pl_recommendation |
| **ArchitectAgent** (chief author) | 통합 author / synthesizer | 6 (또는 8) SubAgent 산출물 통합 + Change Plan §1-§13 author + ADR draft + Story §3/§7/§11 mirror write |
| **CodebaseMapperAgent** | 보수 — as-is 변호자 | 기존 패턴 유지, 변경 영향 최소화 (Change Plan §2 현재 구조 input) |
| **RefactorAgent** | 혁신 — to-be 옹호자 | 결합도 감소, 인터페이스 분리, 패턴화 (Change Plan §3 + §6 input) |
| **SecurityArchitectAgent** | 위협 — 공격자 관점 | 외부 입력 / 신뢰 경계 / 권한 위임 (Change Plan §7.1-§7.3, §7.5-§7.6 input) |
| **OperationalRiskArchitectAgent** | 운영 리스크 — production-readiness 변호자 | 끊김 / 실패 / 과부하 / 스테이징-프로덕션 누설 (Change Plan §7.4 운영 리스크 + §11.6 idempotency consult input) |
| **TestContractArchitectAgent** | QA perspective contributor | §8 Test Contract 커버리지 / 경계 / invariant (Epic 소속 Story 시 §8.6 `story_key` + `suite: "story"` 필수) |
| **DataMigrationArchitectAgent** | 데이터 무결성 — 변호자 | schema 변경 / 기존 데이터 처리 / 실패 복구 (Change Plan §11.1-§11.5 input) |

**CONDITIONAL deputy (3 agent)** — Story 조건 충족 시 ArchitectPLAgent 가 추가 spawn:

| 모듈 (agent) | trigger 조건 | 책임 |
|---|---|---|
| **LiveOpsDeputy** | Live touching Story (real funds / live exchange API / production credential / live order placement 1+ touching, CFP-77) | operator approval / kill switch / incident response / OperationEvent audit (Change Plan §13 + §7.5 consult input) |
| **LiveOrderingDeputy** | Live touching Story (위 동일 CFP-77 trigger) | order submit / partial fill / cancel race / rejection mapping / ledger reconcile invariant (Change Plan §11 ledger + §8.5 order replay + §11.6 idempotency consult input) |
| **ProductionEvidenceDeputy** | production cutover Story (ADR-072) | 실측 production 통과 evidence — staging→production cutover gate (CONDITIONAL spawn 시 별도 §섹션 input) |

> 4-way 이념 대립 축 (Mapper ↔ Refactor ↔ SecurityArch ↔ DataMigrationArch) = chief author 가 충돌 해소 + Change Plan 명시. TestContractArch / OpRiskArch / LiveOps / LiveOrdering / ProductionEvidence = contributor 단일 축 (대립 비참여).

## 경계

**Lane self-write boundary** `[verified: CLAUDE.md @ e6e1398d Self-write 책임 표]`:

| 경계 영역 | owner agent |
|---|---|
| `docs/change-plans/<slug>.md` (§7.4 + §11.6 통합 포함) | ArchitectAgent (direct write, CFP-26 Phase 0a) |
| `docs/adr/ADR-NNN-<slug>.md` | ArchitectAgent (direct write, CFP-26 Phase 0a) |
| Story §3 (ADR list mirror) | ArchitectAgent |
| Story §7 (보안 + §7.4 운영 리스크 mirror) | ArchitectAgent |
| Story §11 (데이터 마이그레이션 mirror) | ArchitectAgent |
| `docs/architecture/<path>.md` (본 doc 영역) | ArchitectAgent (lane gate — ADR-078 §결정 1 4 영역 갱신 의무, 매 Change Plan merge 시) |
| GitHub comment `[설계]` prefix | ArchitectPLAgent |
| `phase:설계` → `phase:설계-리뷰` transition | ArchitectPLAgent |

**Deputy mandate matrix** (§7 / §11 sub-section ownership) — `codeforge:deputy-mandate` skill SSOT 요약:

| Change Plan sub-section | owner deputy |
|---|---|
| §2 현재 구조 | CodebaseMapperAgent |
| §3 도입할 설계 + §6 리팩토링 선행 | RefactorAgent |
| §7.1-§7.3 / §7.5-§7.6 보안 | SecurityArchitectAgent |
| §7.4 운영 리스크 (DR / rate / env / clock) + §11.6 idempotency consult | OperationalRiskArchitectAgent |
| §8 Test Contract | TestContractArchitectAgent |
| §11.1-§11.5 schema / migration | DataMigrationArchitectAgent |
| §13 Live Operational Discipline (CONDITIONAL) | LiveOpsDeputy |
| §11 ledger reconcile + §8.5 order replay + §11.6 idempotency (order side, CONDITIONAL) | LiveOrderingDeputy |
| production cutover gate evidence (CONDITIONAL) | ProductionEvidenceDeputy |

**Cross-cutting gate boundary**:
- **Codex Proactive Check Touchpoint #2** = ArchitectAgent §3 완료 직후 mandatory dispatch (CFP-532 / ADR-052 Amendment 4) — P0 + P1 finding 모두 inline FIX 의무 (skip 영역 차단)
- **ADR-065 mechanical self-check** = Phase 1 산출물 commit 직전 7-item mechanical sync (label-registry / doc-locations / workflow self-app / link target / MANIFEST.yaml / section-ownership / doc-locations row) self-verify 의무
- **ADR-068 boundary completeness** = ArchitectAgent §3 / §7 작성 시 4+1 semantic invariants (I-1 API contract semantic / I-2 cross-module propagation / I-3 guard placement intent / I-4 wording SSOT / I-5 dimensional empirical grounding) self-verify 의무
- **ADR-082 write-time self-write verification** = §9 evidence / corpus enumeration / cross-plugin ownership write-time source direct verify 의무 (assertion 금지)

**Disjoint scope** (ADR-078 §결정 3):
- 본 doc (architecture_doc) = lane internal 누적 현재 상태, Story key 독립
- Change Plan = Story별 변경 델타, Story key 종속, 1회 작성
- ADR = 단일 결정 단위, 불변
- 본 doc ↔ Change Plan = 상보 disjoint (구조 vs 델타)

## 인터페이스 계약

lane 간 + lane 내부 계약 surface = `docs/inter-plugin-contracts/` (canonical = 본 plugin repo, wrapper = sibling sync mirror — ADR-010):

**Producer 계약 (kind:contract)** — 본 lane 이 생성:

| contract | 용도 | SSOT pointer |
|---|---|---|
| `design_output` | 설계 lane 산출물 핸드오프 (Change Plan + ADR + Story §3/§7/§11 mirror) | `docs/inter-plugin-contracts/design-output-v2.md` (canonical) + wrapper sibling mirror (ADR-010) |

**Host 계약 (kind:registry — sibling sync 면제, ADR-010 §결정 2)** — 본 lane 이 발동 / 참여:

| contract | 본 lane 역할 |
|---|---|
| `debate-protocol-v1` | DesignReview lane divergence 시 multi-round adversarial debate carrier. **Wave 4 blanket trigger** (`blanket_cross_module_designlane`) = touched_top_level_paths ≥ 2 OR touched_lanes ≥ 2 Story 시 자동 활성 (ADR-059 Amendment 2). 4-value dispatch_mode 우선순위 `auto_on_divergence > blanket_cross_module_designlane > mechanical_fast_path_inline > user_request_only`. transcript → Story §9 append → §10 FIX Ledger `debate_artifact_ref` carrier |
| `parallel-dispatch-protocol-v1` | ArchitectPLAgent 의 6 (또는 8) SubAgent **parallel spawn** 계약 host. sequential 강제 사유 3종 (state dependency / shared resource / ordering invariant) 부재 시 default parallel (ADR-064 Trace 4) |
| `review-verdict-v4` | ArchitectPL → DesignReviewPL 핸드오프 carrier field 보유: `mechanical_self_check_passed` (ADR-065) + `boundary_completeness_self_check_passed` (ADR-068 I-1~I-4) + `dimensional_empirical_self_check_passed` (ADR-068 I-5) + `marketplace_sync_declared` (ADR-063 §결정 9) |

**Chief author monopoly**:
- **ADR-RESERVATION row append** — `docs/adr/ADR-RESERVATION.md` sequential append (ArchitectAgent chief 가 신규 ADR 번호 예약, parallel epic conflict 회피 — ADR-050)
- **신규 ADR draft write** — `docs/adr/ADR-NNN-<slug>.md` (CFP-26 Phase 0a, 본 lane plugin repo 가 아닌 wrapper / lane plugin 의 owner repo 에 따라 분기)

> 계약 schema field-level 상세 + version 값 = 각 contract file SSOT + MANIFEST.yaml. 본 섹션 = surface enumeration (계약 이름 + SSOT pointer, version literal 미박제 — version drift 회피).

## 데이터 흐름

**설계 lane 진입 → 산출물 flow** (Orchestrator 가 lane 진입 시 ArchitectPLAgent 1개 spawn — non-skippable):

```
[upstream] requirements_output 수신 (Story §1-§6 완료)
  ↓
ArchitectPLAgent (lane PL) spawn
  ↓ Story §13 CONDITIONAL trigger 검토 (Live touching / production cutover)
  ↓
ArchitectPLAgent parallel SubAgent spawn (parallel-dispatch-protocol-v1)
  ├─ CodebaseMapperAgent       → §2 input
  ├─ RefactorAgent             → §3 + §6 input
  ├─ SecurityArchitectAgent    → §7.1-§7.3 / §7.5-§7.6 input
  ├─ OperationalRiskArchAgent  → §7.4 + §11.6 idempotency consult input
  ├─ TestContractArchAgent     → §8 Test Contract input
  ├─ DataMigrationArchAgent    → §11.1-§11.5 input
  ├─ [CONDITIONAL] LiveOpsDeputy           → §13 + §7.5 consult
  ├─ [CONDITIONAL] LiveOrderingDeputy      → §11 ledger + §8.5 + §11.6 consult
  └─ [CONDITIONAL] ProductionEvidenceDeputy → cutover evidence gate
  ↓ (6 또는 8 산출물 병렬 수신)
ArchitectAgent (chief author) spawn — 산출물 통합
  ├─ Change Plan §1-§13 author (docs/change-plans/<slug>.md direct write)
  ├─ 신규 ADR draft (docs/adr/ADR-NNN-<slug>.md direct write + ADR-RESERVATION row append)
  ├─ Story §3 ADR list mirror
  ├─ Story §7 보안 + §7.4 운영 리스크 mirror
  ├─ Story §11 데이터 마이그레이션 mirror
  └─ §3.5 self-lint (6 deputy 산출물 input 표면 mechanical check)
     §5.5 ADR-065 mechanical 7-item self-check (commit 직전)
     §5.6 ADR-068 boundary completeness 4 invariants self-check
     §5.6.1 ADR-068 I-5 dimensional empirical grounding self-check
     §5.7 ADR-063 marketplace sync diff 감지 (Change Plan §13 declarative)
  ↓
[Codex Proactive Check Touchpoint #2 — mandatory dispatch]
  · ArchitectAgent §3 완료 직후 자동 발동 (CFP-532 / ADR-052 Amendment 4)
  · P0 + P1 finding 모두 inline FIX 의무 (skip 차단)
  ↓
ArchitectPLAgent 검수 → review-verdict packet 작성
  · 4 boolean field (mechanical / boundary / dimensional / marketplace_sync_declared)
  · PASS or FIX → ArchitectAgent 재스폰 (RETURN)
  ↓
[downstream] design_output → DesignReviewLane 핸드오프
```

**FIX 루프 데이터 흐름**:
- DesignReviewLane FIX verdict → ArchitectPLAgent 재spawn → ArchitectAgent 재스폰 (Change Plan 갱신만 담당)
- 구현 lane FIX root cause = 설계 판정 시 ArchitectPLAgent (DeveloperPL 1차 진단 후 최종 결정) → Change Plan 갱신 + Phase 1 follow-up PR
- debate-protocol-v1 발동 시 transcript = Story §9 append → §10 FIX Ledger `debate_artifact_ref` carry → ArchitectAgent 재스폰 시 verbatim 입력

**artifact propagation**:
- Story file (`internal-docs/codeforge-design/stories/<KEY>.md`) = lane 컨텍스트 SSOT (ArchitectAgent self-fetch §1-§7)
- Change Plan (`docs/change-plans/<slug>.md`) = Story별 변경 델타 (1회 작성, Story key 종속)
- ADR (`docs/adr/`) = 단일 결정 단위 (불변)
- 본 doc (architecture_doc) = 누적 현재 상태 (영속, Story key 독립) — 매 Change Plan merge 시 4 H2 영역 갱신 의무 (CLAUDE.md `Self-write 책임` 표 last row)

> 본 흐름 = lane spawn / event / artifact propagation 수준. 함수 호출 trace / 변수 전달 라인 0건 (anti-scope guard 준수).

---

### ADR-076 declarative reconciliation 3-layer cross-ref

본 lane 의 architecture_doc 운용은 [ADR-076](../../../plugin-codeforge/docs/adr/ADR-076-declarative-reconciliation-upgrade.md) declarative reconciliation 3-layer 패턴을 도메인 disjoint 로 답습 (ADR-078 §결정 4 명시):

- **desired state** = 본 doc 의 4 H2 closed-enum (모듈 + 경계 + 인터페이스 계약 + 데이터 흐름) 누적 현재 상태 SSOT
- **current state** = lane plugin agent file (`agents/*.md`) + `CLAUDE.md` 의 실제 정의 상태
- **converge** = ArchitectAgent self-write (매 Change Plan merge 시 4 H2 갱신, CLAUDE.md `Self-write 책임` 표 last row) + design lane verdict gate (DesignReviewPL 가 본 doc drift 검증 — CFP-923 detection class d, architecture-drift lint 후속 carrier)

---

### anti-scope guard (ADR-078 §결정 1 verbatim — 작성자 필독)

본 doc 은 **구조 수준 only**. closed-enum 4 영역 외 다음 4종 패턴은 **금지** (라인 수준 허용 시 갱신 즉시 stale + "코드에 한 단계 더한 것" 전락 — Epic §위험신호 §1):

1. **클래스 / 함수 / 변수 라인 단위 열거** — 클래스 list, 변수 enumeration 금지.
2. **의존성 import graph 라인-level** — import 관계 라인 단위 그래프 금지.
3. **함수 signature / parameter list / return type** — API 의 line-level 시그니처 금지.
4. **코드 mirror** — `agents/` 또는 `src/` 구조를 1:1 복사한 디렉터리 트리 dump 금지.

→ 위 4종이 필요하면 그것은 코드 / Change Plan / ADR 영역. architecture_doc 은 "코드 read 없이 구조 파악" 목표만 만족하면 된다.
