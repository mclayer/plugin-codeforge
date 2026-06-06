## 13. PMOAgent 프로젝트 관리 (Cross-cutting)

PMOAgent는 단일 Story 레인 게이트 밖에서 cross-cutting 감사·회고·패턴 분석을 전담. 요구사항 해석은 RequirementsPLAgent 영역으로 분리됨.

### 13.1 스폰 타이밍 4종 (CFP-316 / ADR-047 — Version Delta Review 추가)

| 트리거 | 시점 | 입력 | 산출물 |
|--------|------|------|--------|
| **Epic 창설** | Orchestrator가 Epic 생성 직후, Story 분해 직전 | 사용자 원문·관련 ADR·기존 Epic 이력·코드 구조 | Story 분해 자문 (의존성·우선순위·**병렬/순차 판정**) — 상세 규칙 [PMOAgent.md §1](https://github.com/mclayer/plugin-codeforge-pmo/blob/main/agents/PMOAgent.md) |
| **Story 완료** | CI gate PASS → (lanes.security_ai: true 시 보안 테스트 PASS →) Phase 2 PR merge 직후 | 해당 Story file §1-11 + FIX Ledger + GitHub Issue 코멘트 이력 + 토큰 사용량 | 회고 감사 보고 (Preflight 누락·§8/§8.5 매핑·FIX evidence 완성도·예산) |
| **사용자 요청** | `/pmo-audit` 혹은 명시 요청 | 최근 N Story (기본 5) file·Ledger·ADR 변경 이력 | Cross-Story 패턴 보고 + ADR 후보 발의 |
| **Version Delta Review** | Framework Delta Event 발생 후 5분 이내 (또는 사용자 수동 trigger `/pmo version-delta-review`) | Framework Delta Event 종류 + 진행 중 Story 목록 + 관련 ADR + consumer overlay 상태 | Migration Epic Issue (material drift 시) 또는 "no action" 보고서 → Story §11 기록 |

### 13.1a Version Delta Review 프로세스 (CFP-316 / ADR-047)

PMOAgent의 4번째 trigger — codeforge framework 진화(신규 SubAgent 추가, §section 변경, ADR 변경 등) 시 기존 진행 중 Stories/Change Plans의 구조 재편 필요 여부를 자동 평가한다.

**Framework Delta Event 4-Type 정의**:

| Type | 설명 | PMOAgent 반응 |
|------|------|---------------|
| **Type A — Version bump** | consumer 프로젝트의 codeforge version bump | patch: advisory review 보고서 / minor·major: Migration Epic 후보 평가 |
| **Type B — ADR 변경** | Story 구조/lane 동작에 영향을 주는 신규·실질적 ADR 변경 (inter-plugin contract schema MAJOR bump, GitHub workflow fixture 변경 등) | 영향 범위 평가 후 Migration Epic 여부 결정 |
| **Type C — Deputy 변경** | 신규 SubAgent 추가 또는 SubAgent mandate 변경 (새 필수 §section 발생) | 진행 중 Story에 새 §section 추가 Migration Story 생성 |
| **Type D — Bootstrap 변경** | ADR-027/ADR-032 enforcement 변경 | consumer-guide 업데이트 + bootstrap 재검증 Migration Story |

**Version Delta Review 프로세스 (4단계)**:

1. Framework Delta Event 종류 판별 (Type A/B/C/D)
2. 진행 중인 Stories/Change Plans의 §section 구조 점검 (영향 범위 평가)
3. Material drift 판별:
   - patch bump / advisory-only ADR: "no migration needed" 보고서 → Story §11 기록
   - minor/major bump 또는 신규 SubAgent 또는 §section 신설: Migration Epic 후보 평가
4. Migration Epic 생성 또는 "no action" 결정

**2차 detection / fallback** (누락 방지):
- (2차) PMOAgent Story 완료 회고 trigger 시 직전 5분 grace 내 Delta Event 미처리 자동 점검
- (3차 fallback) 사용자 수동 trigger `/pmo version-delta-review` skill 호출
- (장기) SessionStart hook 에 version bump 감지 추가 — 별도 CFP 후속

상세 Migration Epic Pattern 및 tiered template → [consumer-guide.md §5.2](consumer-guide.md#52-framework-migration-epic-pattern-cfp-316--adr-047).

### 13.2 감사 체크리스트 (Story 완료 회고 기본 세트)

1. **Preflight 실행 근거**: 각 레인 진입 시 Issue 코멘트에 `[<phase>] <AgentName>: Preflight PASS` 또는 failure 보고가 존재하는가
2. **§8 Test Contract ↔ tests/** 매핑**: QADev 매핑표의 모든 항목이 실제 tests/ 파일로 구현됐는가
3. **§8.5 Impl Manifest ↔ git diff**: 기록된 파일 목록이 PR의 실제 변경 파일과 일치하는가 (누락·추가 없이). subissue Action이 자동 생성한 sub-issue 목록과 대조
4. **FIX Ledger evidence pack**: 각 FIX iteration 행에 ArchitectPLAgent 판정 근거(Change Plan 버전 + 리뷰 findings + 테스트 로그)가 코멘트로 기록됐는가
5. **토큰 예산 준수**: 레인별 사전 예산(§8.2) 대비 실제 사용량, 중단 임계 접근 여부
6. **RESET 마커 타당성**: 테스트 FAIL 후 구현 리뷰 RESET이 올바른 조건에서 기록됐는가
7. **Phase/Gate 라벨 invariant**: phase-label-invariant·phase-gate-mergeable·story-section-1-immutable Action 모두 PASS 했는가

### 13.3 Cross-Story 패턴 검출 알고리즘 (사용자 요청 시)

```
inputs:
  - 최근 N Story (기본 5, 사용자 지정 가능)
  - 각 Story의 §10 FIX Ledger + ADR 변경 이력

outputs:
  - 반복 FIX 원인 분포 (설계 vs 구현, 레인별)
  - ESCALATE 발생 단계 히트맵
  - 성능 게이트 실패 트렌드 (baseline 갱신 Story vs 성능 회귀 Story)
  - 파일 핫스팟 (3+ Story에 걸쳐 수정된 파일)
  - ADR 후보 (패턴이 "설계 지침 부재"로 해석될 때)
```

### 13.4 ADR 후보 발의 절차

PMOAgent가 반복 패턴을 식별해 ADR draft 제안 (`pmo_output v1.adr_proposal` inline content) 을 Orchestrator에 전달하면, Orchestrator가 codeforge-design 의 ArchitectAgent를 스폰해 `status=Proposed` ADR 파일(`docs/adr/ADR-NNN-<slug>.md`)을 직접 write (CFP-26 Phase 0a). 다음 Story 설계 진입 시 ArchitectAgent (chief author)가 검토해 `status=Accepted` 전이 또는 기각.

```
# 경로:
# PMOAgent → (Orchestrator 경유) → ArchitectAgent (codeforge-design) → docs/adr/ADR-NNN-<slug>.md 직접 write
# ※ pre-CFP-32 write queue adr-draft type 은 사용 안 함 — Orchestrator가 ArchitectAgent 직접 스폰
```

ArchitectAgent가 write하는 ADR 파일 본문 구조는 PMOAgent.md의 "ADR 후보 발의" 템플릿을 따른다 (status=Proposed로 신설).

### 13.5 PMOAgent 보고 기록

모든 PMOAgent 산출물은 `[PMO]` phase prefix로 GitHub Issue 코멘트 직접 기록. Story 회고는 Story file §11 직접 self-write (codeforge-pmo), Cross-Story 감사는 **별도 Issue** (label: `type:audit`, 제목: `PMO Audit / <YYYY-MM-DD>`) PMOAgent 가 직접 생성.

### 13.6 범위 외

PMOAgent가 **하지 않는** 것:
- 단일 Story 요구사항 해석 (RequirementsPLAgent)
- Change Plan 작성·검토 (ArchitectPLAgent / ArchitectAgent / DesignReviewPL)
- 코드 수정 (Dev)
- 테스트 실행 (CI gate — Orchestrator inline)
- 사용자 직접 상호작용 (Orchestrator 경유 보고만)

---

