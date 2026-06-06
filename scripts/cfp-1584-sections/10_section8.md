## 8. 토큰 예산 모니터링 + 세션 회고

### 8.1 추적 지표

- 레인별 input/output 토큰 (요구사항 / 설계 / 설계 리뷰 / 구현 / 구현 리뷰 / 구현 테스트 / 보안 테스트)
- 에이전트별 누적 토큰 (0 core in wrapper + 23 distributed across 6 lane plugins + preset/overlay-only `role: dev` 에이전트)
- FIX iteration별도 추가 토큰
- **ArchitectPLAgent + ArchitectAgent (chief author) stateless 재스폰 overhead**: PL 재스폰 당 ~5k + chief author 재스폰 당 ~10k (Story file §1-8 fetch). FIX 3회 가정 시 ~45k

### 8.2 레인별 사전 예산·중단 임계

두 지표로 추적:
- **Total**: 레인 전체 누적 (병렬·순차 합산, 에이전트별 input+output)
- **Peak concurrent**: 같은 시점에 동시 실행되는 에이전트의 현재 context 합계 — 병렬 모델에서 실제 비용 지표. v0.7.0 병렬화로 요구사항·설계 peak이 크게 증가

| 경로 | Total 사전 예산 | Total 중단 임계 | Peak concurrent (동시 컨텍스트 합) | 비고 |
|------|-----------------|-----------------|------------------------------------|------|
| 요구사항 | 80k | 150k | ~60k (Domain ∥ Analyst ∥ Researcher, 각 ~20k 풀 컨텍스트) | v0.6 순차 대비 total +30k / peak 3× |
| 설계 | 280k | 400k | ~200k (Mapper ∥ Refactor ∥ ArchitectAnalyst ∥ SecurityArchitect ∥ InfraOperationalArchitect ∥ TestContractArchitect ∥ DataArchitect ∥ ModuleArchitect ∥ AggregateArchitect ∥ APIContractArchitect, 각 ~20-25k) + ArchitectAgent (chief author) 10k + ArchitectPLAgent 5k | CFP-1086 / ADR-042 Amd 8 — 7 permanent + 3 sub-tuple = 10 SubAgent parallel spawn (vs CFP-676 시점 5+3 = 8) total +55k / peak +50k. spawn count 평균 22→28 (1.27배) / full activation 34→40 (1.18배, ADR-068 I-5 dimensional empirical grounding `count` dimension `[empirical-source: TBD]` annotation). AggregateArch CONDITIONAL applicability false 시 9 SubAgent = total +30k / peak +25k 감소 |
| 설계 리뷰 | 50k | 120k | ~40k (Claude ∥ Codex) | 기존 유지 |
| 구현 | 200k | 400k | roster size × ~20k + QADev 20k | 기존 유지 (`role: dev` 병렬 수에 비례) |
| 구현 리뷰 | 60k | 150k | ~40k (Claude ∥ Codex) | 기존 유지 |
| 구현 테스트 | 0k (CI native) | — | Orchestrator inline `gh pr checks` | ADR-048 CI gate — 토큰 비용 없음 |
| 보안 테스트 | 60k | 150k | ~40k (Claude ∥ Codex 보안 focus) | 기존 유지 (1차 layer는 GitHub native, 토큰 비용 없음) |
| Clarification 재스폰 (per instance) | 10-20k 추가 | — | 단일 에이전트 재실행 | 2회 한도 (§4.4.2 PL재량 layer). clarification 강제 fan-out = §4.4.1 (6+조건부 PMO, 정량 envelope = ADR-077 §결정 4 표 cross-ref). per-instance 정량 = [empirical-source: TBD] (Story-3 §8.3 Perf Baseline carry) |
| FIX 루프 (per iteration) | 50k + ArchitectPLAgent 재스폰 5k + chief author 재스폰 10k | 150k | FIX 트리거 레인 동일 | 기존 유지 |

**Peak 고려 이유**: 병렬 스폰은 순차보다 wall-clock 단축하나 **동시 활성 context 총량** 증가 → session memory pressure. Peak이 임계 접근 시 순차 fallback 또는 에이전트 범위 축소 검토.

**중단 임계 초과 시**: 진행 중단 → §2.3 형식으로 "토큰 한계 도달, 계속 진행 결정" 에스컬레이션.

### 8.3 세션 회고 보고 (완료 시 필수)

#### 에이전트별 작업 요약 (23 distributed agent across 6 lane plugins + 스폰된 preset/overlay-only role:dev, 미참여 "-")

| Agent | 수행 내용 |
|-------|-----------|
| Orchestrator | |
| PMOAgent | |
| RequirementsPLAgent | |
| DomainAgent | |
| *(DocsAgent — 부재, CFP-40)* | — |
| ResearcherAgent | |
| RequirementsAnalystAgent | |
| ArchitectPLAgent | |
| ArchitectAgent | (chief author) |
| CodebaseMapperAgent | |
| RefactorAgent | |
| SecurityArchitectAgent | |
| TestContractArchitectAgent | |
| DataMigrationArchitectAgent | |
| DesignReviewPLAgent | |
| DeveloperPLAgent | |
| DeveloperAgent | |
| DataEngineerAgent | |
| InfraEngineerAgent | |
| <추가 role:dev 에이전트들> | |
| QADeveloperAgent | |
| CodeReviewPLAgent | |
| SecurityTestPLAgent | (lanes.security_ai: true 시만) |
| ClaudeReviewAgent | (3 lane 합산) |
| CodexReviewAgent | (3 lane 합산) |

#### 토큰 사용량 (전체 스폰된 에이전트, 0 허용)

| Agent | Input Tokens | Output Tokens | 합계 |
|-------|-------------|---------------|------|
| Orchestrator | | | |
| ... (20개 전체) | | | |
| **합계** | | | |

Orchestrator 자체 토큰 = 세션 전체 - 20 서브에이전트 합계.

### 8.4 성능 베이스라인 정책 (Issue #306 / NF-T5)

구현 테스트 레인의 성능 측정에 사용하는 **baseline 측정·비교·회귀 판정** 정책 SSOT.

**정책 요약**:
- **최초 실행 값 = baseline**: Story 의 첫 성능 테스트 실행 결과를 baseline 으로 기록 (`.claude-work/progress/<KEY>.md` 의 `perf_baseline` 필드 또는 Story file §9.3 성능 섹션).
- **+20% 초과 = P2 회귀**: 이후 실행에서 mean latency / throughput 등 주요 지표가 baseline 대비 **+20% 이상 악화** 시 → TestAgent 가 P2 회귀 finding 으로 보고.
- **판정 기준 단일화**: `mean` 지표 기준 (p50/p95 는 보조 정보). Change Plan §8.3 에 지표 명시된 경우 해당 지표를 우선 사용.
- **re-baseline 조건**: 설계 의도적 변경 (Change Plan §3 갱신 동반 PR merge 후) 이 성능 특성을 변경한 경우에만 Orchestrator 가 re-baseline 승인 (FIX 루프 §6.5 "성능 test FAIL" decision table 과 연동).

| 시나리오 | 판정 | 대응 |
|---|---|---|
| 최초 실행 | — | baseline 기록 (P2 판정 없음) |
| 재실행 mean ≤ baseline × 1.20 | PASS | — |
| 재실행 mean > baseline × 1.20 | P2 회귀 | TestAgent 가 finding 포함 verdict 반환 → FIX 루프 진입 |
| 설계 변경 동반 재실행 | re-baseline | Orchestrator 승인 후 baseline 갱신, 직전 값 archive |

**TestAgent 적용**: 구현 테스트 레인 성능 subset (R9) 의 종료 조건과 통합. `baseline 비교 임계 mean:10%` (§3.2 TestAgent 행) 는 **본 §8.4 정책으로 대체 — +20% 기준이 공식 SSOT**. §3.2 TestAgent 행의 `mean:10%` 는 참조 편의를 위한 구 수치로, 신규 Story 부터 본 §8.4 적용.

---

