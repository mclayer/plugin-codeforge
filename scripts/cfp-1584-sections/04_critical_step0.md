## CRITICAL Step 0 — pre-spawn-pin (mandatory, ADR-039 §결정 14)

Branch 생성 직전:
```bash
git fetch origin
MAIN_HEAD=$(git rev-parse origin/main)
echo "PINNED_MAIN_HEAD=$MAIN_HEAD"
```

모든 후속 branch 생성 + rebase + PR open 시 본 SHA 사용. self-claim / packet reference / local HEAD / memory SHA 무조건 신뢰 금지. mid-flight main churn 가능 — rebase 시점에 재고정 의무.
```

**Cross-ref**: ADR-039 §결정 14 / §결정 9 (Amendment 1 enforcement Phase 2 hook 격상 경로) / [[feedback_verify_pin_head_sha]] / [[feedback_no_permission_prompts]] / codeforge-develop:`agents/DeveloperPLAgent.md` "PR 생성 Pre-flight Guard" Step 0 확장 (CFP-895 paired PR).

### 3.1 9 레인 + Cross-cutting 스폰 순서 (요약, CFP-1059 / [ADR-087](../docs/adr/ADR-087-deploy-lane-and-lifecycle-extension.md) + [ADR-088](../docs/adr/ADR-088-deploy-review-lane-and-production-evidence-transfer.md) — 7 → 9 lane 확장)

> **Phase 1 declarative**: 본 §3.1 의 배포 / 배포 리뷰 lane spawn 시퀀스 = declarative anchor (CFP-1059 Story-1). 실 DeployPLAgent / DeployReviewPLAgent spawn = lane plugin seed (codeforge-deploy / codeforge-deploy-review) 신설 후 활성 — 별 sub-Story carrier 영역.

```
[Cross-cutting 트리거]
Epic 창설:  Orchestrator → PMOAgent (Scope 분해 자문)
Story 완료: Orchestrator → PMOAgent (회고 감사 + ADR 후보 검토)
Epic 묶음 완료 (모든 Story merged): Orchestrator → DeployPLAgent 자동 trigger (Epic close → Deploy cascade, ADR-026 Amendment N 동반)

[Story 내부 9 레인 — CFP-1059 ADR-087/088 — 6 → 8 단계 확장 + Cross-cutting PMOAgent]
요구사항:    Orchestrator → RequirementsPLAgent(DomainAgent ∥ Analyst ∥ Researcher 병렬, 셋 다 non-skippable) → PL dedup·상충 조정 → Story file §3-6 갱신
설계:        Orchestrator → ArchitectPLAgent → (CodebaseMapper ∥ Refactor ∥ SecurityArchitect ∥ TestContractArch ∥ DataMigrationArchitect 병렬) → ArchitectAgent (chief author) 통합 → ArchitectPLAgent 검수 → Change Plan 확정
                         → ArchitectAgent direct write (docs/change-plans/<slug>.md + docs/adr/ADR-NNN-<slug>.md) + ArchitectAgent 가 Story file §3/§7/§11 직접 self-write (codeforge-design self-write 표)
설계 리뷰:   Orchestrator → DesignReviewPLAgent (lane=design packet 작성) → packet return (no writes — CFP-61 / ADR-022)
             **review-verdict 5-step algorithm (CFP-61 / ADR-022 §결정 3)**:
             1. ReviewPL spawn → workers (ClaudeReviewAgent ∥ CodexReviewAgent 병렬) → dedup → review-verdict-v3 packet 작성 (no writes)
                ├── findings + pl_recommendation 작성
                ├── decision_state = pending_sonnet (or blocked_packet_incomplete if pl_recommendation=ESCALATE_PACKET_INCOMPLETE)
                └── return to Orchestrator
             2. Orchestrator: decision-packet-v2.1 작성 (trigger: review-verdict, review_lane_context populated, findings_hash verified)
             3. Orchestrator: Agent tool with model:sonnet 호출 → 응답 parse (§4.5.3 Sonnet 응답 schema)
                ├── decision=PASS|FIX → sonnet_final_status 채움, decision_state=decided, step 4 로 진행
                ├── decision=PACKET_REQUIRES_REVIEW_REOPEN → decision_state=review_reopen_requested, ReviewPL 재 spawn (1 회 한도 per (story_key,lane,iteration))
                └── timeout/malformed (Codex P1 #4) → decision_state=decider_timeout
                    └── Story §9 / §10 append 차단. §12 row append (decider_pick=<none>, audit_result=user-escalation, attempts[].outcome=timeout|malformed)
             4. Orchestrator self-write (decision_state=decided 일 때만):
                ├── Story §9 append (lane iteration result) — append-only, never rolled back
                ├── GitHub Issue/PR comment (lane-specific prefix per comment-prefix-registry-v1) via mcp__github__add_issue_comment
                ├── PASS 시: gate:*-pass label + phase:* 다음 단계 전환 via mcp__github__issue_write
                └── Story §12 Sonnet Decision Log row append
                
                **Partial-write policy (Codex P1 #5)**: 각 sub-step 별 idempotent retry (initial + 2 retry = 3 회 한도, Codex Round 2 gap fix). 실패 시 `writes_completed.<field>=false` + `write_errors[]` populate, decision_state=write_partial. **any required write 가 retry 한도 후에도 false 잔존 시 user escalation** (모든 required 가 아닌 1 건이라도 잔존 시 — Codex Round 2 gap fix wording 명확화). Story §9 + §12 는 append-only — 이미 append 된 내용 rollback 안 함. 외부 복구 후 다음 spawn 사이클에 missing write 재시도 가능 (write_partial → write_complete 전환).
             5. FIX 시 (sonnet_final_status=FIX):
                ├── Story §10 FIX Ledger append (decider: claude_sonnet, override marker if pl_recommendation != sonnet_final_status)
                ├── fix-ledger-sync.yml Action mirror (auto)
                └── DeveloperPL + ArchitectPL parallel diagnosis spawn (CFP-19 R4)
                
                **Spawn-failure policy (Codex P1 #6)**: §10 append 성공 + diagnosis spawn 실패 시 — §10 row 유지 (append-only), §12 append (audit_result=user-escalation, spawn_status=failed), 1 회 retry → second failure = user escalation. spawn 성공할 때까지 §10 row 는 "open FIX with no diagnosis" 상태로 visible.
                         → PASS 시 **2 트랙 병렬** (R7):
                            · Track A: Orchestrator post-Sonnet self-write (gate:design-review-pass 라벨 부착 + Phase 1 PR mergeable) → merge
                            · Track B: DeveloperPL spawn → Change Plan §5·§8 fetch + 첫 commit draft 준비 (PR open 보류)
                         → Track A merge 완료 시 Track B가 즉시 mcp__github__create_pull_request 호출
                         → 동시에 Orchestrator가 background SecurityTestPL prefetch 의뢰 → .claude-work/cache/<KEY>-sec1.json 생성
구현:        Orchestrator → (DeveloperPLAgent(role:dev roster 병렬) ∥ QADev) → 완료 보고
                         → §8.5 Impl Manifest DeveloperPL 이 직접 self-write (codeforge-develop self-write 표, R5)
                         → Orchestrator가 ArchitectPLAgent stateless 재스폰 → 매핑표 감사 (chief author 보조)
                         → §8.5 commit 시 subissue-from-impl-manifest.yml 자동 sub-issue 생성
구현 리뷰:   Orchestrator → CodeReviewPLAgent (lane=code packet 작성) → packet return (no writes — CFP-61 / ADR-022)
             → Orchestrator가 한 메시지에 (ClaudeReviewAgent ∥ CodexReviewAgent) dispatch → PL 종합 → PASS/FIX (R3, R2)
             → PASS/FIX 결정: review-verdict 5-step algorithm 적용 (위 설계-리뷰 동일 흐름, lane=code, [구현-리뷰] prefix)
                         FIX 시 mechanical_category 자격 확인 → fast-path 또는 정상 cycle (R11)
구현 테스트: CI gate (ADR-048) — Orchestrator inline 수행:
                         `gh pr checks <PR_NUMBER> --watch` (timeout 30분)
                         → PASS + lanes.security_ai: false (default): merge gate 진입
                         → PASS + lanes.security_ai: true: SecurityTestPL spawn
                         → FAIL: `gh run view --log-failed` 수집 → FIX loop (DeveloperPL 1차 진단 → ArchitectPL 최종 판정)
통합 테스트: (Epic 하위 전체 Story CI gate PASS 후 1회 실행 — **상세: §3.11**)
보안 테스트: Orchestrator → SecurityTestPLAgent (lanes.security_ai: true 시만, lane=security packet 작성, 1차 layer cache hit/miss 확인)
             1차 layer: .claude-work/cache/<KEY>-sec1.json hit 시 inline 첨부 (R10) / miss 시 PL이 직접 fetch
             2차 layer: PL이 packet return → Orchestrator가 한 메시지에 (ClaudeReviewAgent ∥ CodexReviewAgent) dispatch → PL 종합 → PASS/FIX (R3, R2)
                         → PASS/FIX 결정: review-verdict 5-step algorithm 적용 (위 설계-리뷰 동일 흐름, lane=security)
                         → PASS 시 Orchestrator post-Sonnet self-write (gate:security-test-pass 라벨 부착) → Phase 2 PR mergeable
완료:        Phase 2 PR merge (`Closes #<Story Issue>`) → Issue 자동 close → PMOAgent 가 Story §11 직접 self-write (codeforge-pmo)
             → PMOAgent (회고)

[Epic 묶음 완료 후 — CFP-1059 / ADR-087+088, Phase 1 declarative]
배포:        Orchestrator → DeployPLAgent (codeforge-deploy plugin Phase 1 declare — 실 spawn = lane plugin seed 후) → 변경 repo enumeration + DeployWorkerAgent N 병렬 dispatch (repo 단위)
             각 repo 배포 sequence: blue-green 신호 → green deploy → healthcheck poll → atomic swap (Traefik label flip) → 3-시간 보존 timer → 자동 rollback 결정
             → §12 배포 manifest (codeforge-deploy self-write)
             FAIL (healthcheck / atomic swap / secret lookup): 자동 rollback + Story §10 FIX Ledger append (Orchestrator) + DeveloperPL 또는 ArchitectPL 1차 진단 routing
배포 리뷰:   Orchestrator → DeployReviewPLAgent (codeforge-deploy-review plugin Phase 1 declare, debate-protocol-v1 trigger 의무) → 검증 3종 병렬:
             - smoke 검증 (양방향 호환 — ADR-089 §결정 4 + bidirectional-smoke.yml workflow)
             - 성능 비교 (production runtime measure ↔ pre-deploy baseline — ADR-068 I-5 dimensional empirical grounding 정합)
             - cutover 사후 검증 (ProductionEvidenceDeputy ownership 이관 — codeforge-design CONDITIONAL → codeforge-deploy-review 정식)
             → §13 배포 검증 evidence (codeforge-deploy-review self-write)
             FAIL: 성능 미충족 / smoke 실패 시 FIX dispatch (DeveloperPL / ArchitectPL / RequirementsPL — debate-protocol-v1 multi-round adversarial debate 가능)
             PASS: Orchestrator self-write (gate:deploy-review-pass label + phase:완료 전환) → Epic 묶음 close
```

**Lane-specific write targets (Step 4 GitHub comment / label / phase 매핑)**:

| Lane | Comment prefix | Gate label (PASS) | Phase 다음 단계 |
|---|---|---|---|
| 설계-리뷰 | `[설계-리뷰]` | `gate:design-review-pass` | `phase:구현` |
| 구현-리뷰 | `[구현-리뷰]` | (none — flow continues) | `phase:구현-테스트` |
| 보안-테스트 | `[보안-테스트]` | `gate:security-test-pass` | (PR mergeable) |

상세 SSOT: comment-prefix-registry-v1 (CFP-61 갱신 — review verdict 작성자 = Orchestrator post-Sonnet) + label-registry-v1.

#### CI gate (구현 리뷰 PASS 후 — ADR-048)

구현 리뷰 PASS 직후 Orchestrator inline 수행 (read-only whitelist 예외):

```bash
gh pr checks <PR_NUMBER> --watch
```

- **timeout**: 30분. 초과 시 사용자에게 보고 후 대기.
- **PASS + `lanes.security_ai: false`** (default): merge gate 진입.
- **PASS + `lanes.security_ai: true`**: SecurityTestPL spawn (codeforge-review plugin).
- **FAIL**: 아래 명령으로 실패 로그 수집 후 FIX loop 진입.

```bash
gh run view --log-failed
```

FIX routing: DeveloperPL 1차 진단 (`gh run view` 출력 첨부) → ArchitectPL 최종 판정 → §10 FIX Ledger append.

**Worktree dispatch**: 매 lane spawn 시 worktree 자동 생성 — 상세는 §3.5

상세 분기 규칙은 CLAUDE.md "스폰 시퀀스" 섹션과 각 에이전트 md 참조.

### §3.11 Epic 통합테스트 게이트 (ADR-055 Amendment 2)

**트리거 조건**: Epic 하위 `stories_in_scope` 모든 Story의 CI gate PASS 확인.
단일 Story(non-Epic)는 해당 Story CI PASS 직후 동일 규칙 적용.

#### §3.11.1 IntegrationTestAgent spawn 패킷

```yaml
agent: IntegrationTestAgent (codeforge-test plugin, Sonnet tier)
context_packet:
  epic_key: <EPIC-KEY>
  stories_in_scope: [<STORY-KEY-1>, <STORY-KEY-2>, ...]
  story_8_6_contracts:
    - story_key: <KEY>
      contract_path: "docs/stories/<KEY>.md#§8.6"
  baseline_suite_path: <consumer overlay integration_test.baseline_suite_path>
  required_env_keys: <consumer overlay integration_test.required_env_keys>
  docker_compose_test_path: "docker-compose.test.yml"
```

#### §3.11.2 IntegrationTestAgent 실행 순서

1. **Deployability 검증** (실패 시 즉시 env_missing/infra_setup FIX 분기):
   - `.env` 필수 키 존재 확인
   - `docker-compose -f docker-compose.test.yml up --wait`
   - DB 연결 테스트
   - 각 서비스 health check endpoint 200 확인

2. **Story Suite 자동생성**: 각 Story §8.6 계약 읽기 → `tests/integration/stories/<EPIC-KEY>/<STORY-KEY>/test_*.py` 생성 (story_key metadata 태깅)

3. **Baseline Suite 실행**: `<baseline_suite_path>/` 전체 실행

4. **Story Suite 실행**: `tests/integration/stories/<EPIC-KEY>/` 전체 실행

5. **test-verdict-v2.1 패킷 생성** → Orchestrator에 반환

#### §3.11.3 결과 라우팅

| pl_recommendation | 처리 |
|---|---|
| `PASS` | Baseline 자동승격 → Epic State Ledger `integration_test.status = "pass"` → 보안테스트(opt-in) or Epic 완료 |
| `FIX` | `responsible_stories` 의 각 Story → failure_type별도 FIX loop (§결정 9) → FIX 완료 후 재spawn (max 3회) |
| `ESCALATE_PACKET_INCOMPLETE` | §8.6 누락 → TestContractArchitectAgent 의뢰, docker-compose 부재 → InfraEngineerAgent 의뢰 → 보완 후 재spawn |

#### §3.11.4 Baseline 자동승격 (PASS 시)

**IntegrationTestAgent 자체 수행** — Orchestrator inline 금지 (git commit 권한 = agent 소유).

```bash
# IntegrationTestAgent Mandate 7 (agent 내부 수행):
mkdir -p tests/integration/baseline/<STORY-KEY>
cp tests/integration/stories/<EPIC-KEY>/<STORY-KEY>/test_*.py \
   tests/integration/baseline/<STORY-KEY>/
# SUITE_TYPE = "story" → "baseline" 메타데이터 갱신 후:
git add tests/integration/baseline/
git commit -m "test(baseline): <EPIC-KEY> Story Suite 자동승격 — N개 케이스 추가"
```

Orchestrator는 verdict `pl_recommendation: PASS` 수령 후 Epic State Ledger `integration_test.status = "pass"` 만 갱신.

---

### §3.12 Epic State Ledger (ADR-055 Amendment 2 §결정 8)

Orchestrator는 Epic 진행 중 `.claude-work/epic-state/<EPIC-KEY>.yaml` 에 상태를 유지한다.

#### 파일 경로 규약

```
.claude-work/epic-state/
  CFP-NNN.yaml        # Epic 1개 = 파일 1개
```

#### Ledger 스키마

```yaml
epic_key: string                    # e.g. "CFP-373"
status: pending | in_progress | pass | fail
lock_holder: string | null          # 현재 write 중인 세션 ID (UUID 권장). null = unlocked
ledger_version: int                 # write 시마다 +1 (낙관적 CAS 용)
last_updated: ISO8601               # 마지막 write timestamp (KST `+09:00` zoned — display layer, ADR-079 §결정 2)
session_resume_hint: string | null  # 세션 재시작 시 다음 액션 힌트

stories:
  - key: string                     # e.g. "CFP-373-S1"
    status: pending | in_progress | ci_pass | fix_loop | done
    current_lane: string            # e.g. "구현리뷰"
    pr_number: int | null
    fix_count: int                  # 기본값: 0

integration_test:
  status: not_started | running | pass | fail | escalate
  verdict_ref: string | null        # test-verdict-v2.1 패킷 저장 경로 또는 GitHub comment URL
  last_run_at: ISO8601 | null
  rerun_count: int                  # 기본값: 0
```

**lock 사용 규칙**: Orchestrator는 ledger write 직전 `lock_holder`를 자신의 세션 ID로 설정, write 완료 후 `null`로 해제. 이미 non-null인 경우 5초 대기 후 재확인 (단일 Orchestrator 세션이 정상 케이스 — non-null 지속 시 stale lock, 강제 해제 후 진행).

#### Orchestrator 상태 업데이트 의무

| 이벤트 | 업데이트 필드 |
|---|---|
| Epic 생성 | 파일 초기화 (`stories` 목록 + `status: pending`) |
| Story lane 전환 | `stories[i].status`, `stories[i].current_lane` |
| Story PR 생성 | `stories[i].pr_number` |
| CI gate PASS | `stories[i].status = "ci_pass"` |
| FIX loop 진입 | `stories[i].fix_count++` |
| 통합테스트 시작 | `integration_test.status = "running"` |
| 통합테스트 완료 | `integration_test.status`, `verdict_ref` |

#### 세션 재시작 Resume 절차

세션 개시 체크리스트(§1.1) Step 0 이후:

1. `.claude-work/epic-state/` 디렉터리 스캔
2. `integration_test.status != "pass"` 또는 `stories[*].status != "ci_pass"` 인 파일 존재 시 사용자에게 진행 중인 Epic 목록 표시 → "이 Epic을 이어서 진행할까요?" 확인
3. 승인 시: `session_resume_hint` 읽어 다음 액션 결정 → 해당 Story/lane부터 재개
4. 거부 시: 신규 작업 대기

---

### 3.2 에이전트 프롬프트 표준 템플릿

**공통 블록** (모든 에이전트 스폰 포함):

```
[컨텍스트]
- Story Issue: #<N> (label: phase:<현재 라벨>)
- Story SSOT: docs/stories/<KEY>.md
- 참조 섹션: §{X}, §{Y}
- 관련 ADR (직접 제약 있을 때만 verbatim):
  {ADR 번호 + 1줄 요약}

[작업 지시]
{에이전트별 구체 지시 — 산출물·경계·완료 기준}

[복귀 보고 형식]
- TL;DR 1-3줄 + 상세 본문
- GitHub Issue 코멘트: 각 lane plugin 이 자기 phase prefix 로 직접 mcp__github__add_issue_comment 호출
  · 기록 형식: `[<phase>] <AgentName>: <요약>` + 상세 본문 + 원문 링크
- 산출물 경로: {파일 경로 또는 Story file 섹션 N 직접 Edit (각 lane plugin self-write 표)}

[제약]
- 문서화 표준은 각 lane plugin CLAUDE.md self-write 표 참조 — 자기 owner section 외 직접 write 금지
- {에이전트 권한·책임 경계 추가}
```

**에이전트별 특이 블록**:

| 에이전트 | 추가 블록 |
|----------|----------|
| **PMOAgent** | 스폰 트리거 명시 (Epic 창설 / Story 완료 / 사용자 요청), 감사 범위 지정 |
| **RequirementsPLAgent** | DomainAgent · Analyst · Researcher **병렬** 스폰 지시 (셋 다 non-skippable). 세 결과 dedup·상충 조정 후 Story file §3-6 반영. Clarification 재스폰 의뢰 권한 |
| **DomainAgent** | 사용자 원문 verbatim (Story file §1 복사) + 4소스 fetch 경로 (`docs/domain-knowledge/**` Glob+Read, `docs/adr/**` 도메인 카테고리, <domain-paths>/**, §1 원문). 타 에이전트 산출물 미수신 — 독립 키워드 자체 도출 |
| **RequirementsAnalystAgent** | 공통 입력(Story §1 + ADR)만 수신, 타 에이전트 해석 미포함. Ambiguity 키워드 섹션 생성 의무. codex CLI 필수 |
| **ResearcherAgent** | 사용자 원문에서 외부 기술·선행사례 관점 키워드 자체 도출, 타 에이전트 산출물 미수신. "조사 불필요" 판정도 명시 반환 (null skip 금지) |
| **ArchitectPLAgent** | 설계 lane PL. **7 permanent SubAgent** (SecurityArch / InfraOperationalArch / TestContractArch / DataArch / ModuleArch / **AggregateArch** / **APIContractArch** — CFP-1086 / ADR-042 Amd 8) + 3 4-tuple sub-tuple (CodebaseMapper / Refactor / ArchitectAnalyst) flat spawn 후 ArchitectAgent (chief author) 통합 의뢰 → draft 검수. **CONDITIONAL SubAgent 추가 spawn 분기**: (a) AggregateArch applicability — `project.yaml aggregate_arch.applicable: false` 시 미spawn (frontend-only / API-only / external-managed consumer, CFP-1086 P2). (b) Live touching Story → +LiveOps + LiveOrdering. (c) Production cutover 영향 Story (Change Plan §13 `production_cutover_touching: true`) → +ProductionEvidence (CFP-632 / [ADR-72](../docs/adr/ADR-72-production-evidence-deputy-and-epic-cutover-gate.md)). Live touching + production cutover both = **최대 13 SubAgent** (7 permanent + 3 sub-tuple + LiveOps + LiveOrdering + ProductionEvidence). FIX 최종 판정자 (구현 리뷰·구현 테스트·보안 테스트 FAIL 시). Stateless 재스폰. **chief tie-break ladder 3 단계** (ADR-068 Amd 2): RACI lookup → ADR-068 invariant → chief judgement. **Deputy 신설 결정 framework** (ADR-086): axis 분석 + 5-checklist self-app + deferred carrier path. write queue 의뢰 권한 |
| **ArchitectAgent** | Change Plan §1-§13 chief author + ADR draft author + §8 Test Contract author + §11 데이터 마이그레이션 author. ArchitectPLAgent 산하 SubAgent. 입력 = **7 permanent SubAgent + 3 sub-tuple** 산출물 (Mapper / Refactor / ArchitectAnalyst / SecurityArch / InfraOperationalArch / TestContractArch / DataArch / ModuleArch / AggregateArch / APIContractArch) + Story §1-7. `docs/change-plans/<slug>.md` + `docs/adr/ADR-NNN-<slug>.md` + Story §3/§7/§11 **직접 write** (CFP-26 Phase 0a + codeforge-design self-write 표). Clarification 재스폰 의뢰 권한 |
| **CodebaseMapperAgent** | as-is 변호 역할 (4-tuple sub-tuple component). 매 설계 레인 진입 시 7 permanent deputy + Refactor + ArchitectAnalyst 와 병렬 재스폰, base_sha/scope_paths frontmatter. 타 SubAgent 산출물 미수신 — 원 소스 직접 독해 |
| **DataArchitectAgent** (CFP-1086 mandate 축소 — RDB OLTP 영역 제거 → 빅데이터 OLAP only) | 빅데이터 OLAP 영역 advocate. 매 설계 레인 진입 시 7 permanent deputy 와 병렬 재스폰. Parquet 파일 / 객체저장소 / DuckDB / streaming pipeline / 백필 / 시계열 집계 → chief author 가 Change Plan §3 OLAP + §11 OLAP 에 통합. RDB OLTP 영역은 AggregateArch primary 로 분리 (CFP-1086 / ADR-042 Amd 8) |
| **AggregateArchitectAgent** (CFP-1086 신설 — Sonnet single-mandate advocacy) | RDB OLTP aggregate invariant advocate. 매 설계 레인 진입 시 (CONDITIONAL applicability `project.yaml aggregate_arch.applicable: true`) 7 permanent deputy 와 병렬 재스폰. aggregate boundary + 트랜잭션 경계 + persistence-bound + Alembic 정책 7 원칙 (양방향 호환 / 확장-정리 분리 / reverse / smoke / cross-repo / 백업 / hard limit) → chief author 가 Change Plan §3 aggregate + §11.1-§11.6 RDB OLTP 에 통합. consumer overlay `project.yaml aggregate_arch.migration_tool` 9-enum override (alembic default) |
| **APIContractArchitectAgent** (CFP-1086 신설 — skeleton at S1 / body 심화 = S2 별 PR) | API transport contract advocate. 매 설계 레인 진입 시 7 permanent deputy 와 병렬 재스폰. REST/GraphQL/gRPC/WebSocket + API versioning + DTO + OpenAPI/GraphQL schema + contract testing → chief author 가 Change Plan §3 API + §8 contract testing 에 통합. mandate body 심화 = Story-2 carrier (sequential prerequisite — S1 skeleton 위에 작성) |
| **ModuleArchitectAgent** (CFP-1086 — CodeArch rename + mandate 정정, 도메인 모델 invariant 영역 AggregateArch 분리) | §3 code module-level 구조 advocate. 매 설계 레인 진입 시 7 permanent deputy 와 병렬 재스폰. layered / hexagonal / clean / DDD bounded context module placement / module boundary / dependency direction → chief author 가 Change Plan §3 code 에 통합. aggregate boundary / 트랜잭션 경계 영역은 AggregateArch primary 로 분리 (CFP-1086 / ADR-042 Amd 8) |
| **RefactorAgent** | to-be 혁신 역할 (4-tuple sub-tuple component). 타 SubAgent 산출물 미수신, 원 소스 직접 독해. "잠재 변호 논리 예상" 섹션으로 self-identify한 충돌 지점 제출 (chief author 가 Mapper 실제 변호와 대조) |
| **ArchitectAnalystAgent** (CFP-1026 신설 — PriorArtAgent conceptual rename) | 변경 전 기존 설계 분석 단일 축 (4-tuple sub-tuple component). 매 설계 레인 진입 시 7 permanent deputy + Mapper + Refactor 와 병렬 재스폰. ADR / Change Plan / Story §3/§7/§11 분석 → chief author 가 Change Plan §2 컨텍스트 에 통합 |
| **SecurityArchitectAgent** | 설계 lane 보안 SubAgent (보안 boundary·auth·credential·crypto 전담; 운영 리스크는 InfraOperationalArch). 타 SubAgent 산출물 미수신, 원 소스 직접 독해. trust boundary·auth 모델·credential 흐름·암호학 결정에 대한 보안 설계 권고 산출 → chief author 가 Change Plan §7 (보안 설계 섹션, §7.1-§7.3·§7.5-§7.6; 외부 입력 무관 시 §7.7 N/A) 에 통합 |
| **InfraOperationalArchitectAgent** (CFP-1026 — OperationalRiskArch rename) | 설계 lane 운영 SubAgent (CFP-46 신설 — DR / cancel-on-disconnect / clock sync / rate limit / env isolation **design-time SSOT** 전담). 타 SubAgent 산출물 미수신, 원 소스 직접 독해. 운영 리스크 정책 결정 산출 → chief author 가 Change Plan §7.4 (6 sub-items 포함 Container) 에 통합 + §11.6 Idempotency CONDITIONAL 에 AggregateArch 와 consult (CFP-1086 — AggregateArch primary, InfraOpArch transactional 의미만 협업). **boundary axis** (CFP-632 / ADR-72 §결정 4): policy SSOT (본 SubAgent §7.4 invariant 정의) vs evidence SSOT (ProductionEvidenceDeputy production grounding subsection 실측 명시) 분리 |
| **ProductionEvidenceDeputyAgent** (CONDITIONAL — production cutover 영향 Story 만, CFP-632 / ADR-72) | 설계 lane production-grounding SubAgent. trigger = Change Plan §13 `production_cutover_touching: true` 선언 OR Live touching + production cutover both. 타 SubAgent 산출물 미수신, 원 소스 직접 독해. 책임 3종: (1) production evidence quad owner (bucket prefix listing + WAL sample + drainage rate + L2/L3 cadence trigger 4중) (2) EPIC CLOSED gate 검증 (3) post-cutover wiring inspection (compose.yml env / production deploy state / collector emit schema 실측 ↔ 가설 mismatch surface). chief author가 Change Plan §7.4 production grounding subsection 추가 + EPIC close PR retro epic_close_gate 의무. OpRiskArch §7.4 와 boundary axis 분리 (design-time policy vs runtime-evidence). Mandate matrix 7 cell overlap 71% — 양 측 consult 5 cell |
| **QADeveloperAgent** | Change Plan §8 Test Contract 입력. 매핑표 반환 의무 |
| **`role: dev` 에이전트** (DeveloperAgent·DataEng·InfraEng·preset·overlay) | 계획서 변경 금지 — 결함 발견 시 즉시 DevPL→ArchitectPLAgent 에스컬레이션 |
| **DesignReviewPLAgent** (codeforge-review plugin) | lane=design packet 작성 (codeforge-review repo의 `templates/review-checklists/design.md` 인용 + scope_globs + category_enum + severity_overrides). Claude/Codex 통합 워커 병렬 스폰 후 종합. ADR 정합성 체크 P0 고정 |
| **CodeReviewPLAgent** | lane=code packet 작성. Claude/Codex 통합 워커 병렬 스폰 후 종합. DesignReviewPL과 공통 severity 규칙 (base 템플릿 SSOT) |
| **SecurityTestPLAgent** | (lanes.security_ai: true 시만) 1차 layer = Dependabot/CodeQL/Secret Scanning 결과 `gh api repos/*` 로 fetch → packet에 inline 첨부. 2차 layer = lane=security packet으로 Claude/Codex 통합 워커 병렬 스폰 후 종합. CI gate PASS 이후 진입 |
| **ClaudeReviewAgent / CodexReviewAgent** | lane-agnostic 워커 ([ADR-001](../docs/adr/ADR-001-review-agent-unification.md)). 호출 PL이 review packet으로 도메인(체크리스트·스코프·category enum·severity 자동 룰) 주입. packet 누락 시 ESCALATE 반환 — generic fallback 금지. 정규화 스키마 P0/P1/P2/P3 + lane 필드 반환. CodexReviewAgent는 codex-companion.mjs 실행 |
| *(DocsAgent — 부재, CFP-40 final delete. ζ arc 완료 후 각 lane plugin self-write 로 분산)* | — |

### 3.3 컨텍스트 주입 정책

- **Story file 경로 + 참조 섹션 번호**가 기본 — verbatim 복사 지양
- ADR **직접 제약**인 경우에만 프롬프트에 verbatim 포함
- 배경 참조 ADR은 Story file §3 링크로 충분
- 코드 경로는 Story file §4에 요약, 구체 내용은 `Read`/`Glob`/`Grep` 도구로 직접 접근

### 3.4 Cross-repo Epic 패턴 ([ADR-020](../docs/adr/ADR-020-cross-repo-epic-pattern.md) + Amendment 1 + 2)

mctrader 등 multi-repo consumer 의 cross-repo Epic 진행 시.

#### Epic 시작
1. consumer 가 Epic owner repo 결정 (doc-only hub repo 권장 — 예: mctrader-hub)
2. **Centralization mode 결정** ([ADR-020 Amendment 1](../docs/adr/ADR-020-cross-repo-epic-pattern.md) + Amendment 2 CFP-122):
   - **Mode A (repo-local)**: 각 작업 repo 가 자체 `docs/stories/<KEY>.md`. Implementation repo 가 자율 storyboard 운영 시.
   - **Mode B (hub-centralized)**: 1 hub repo 가 모든 child Story 보유, implementation repo 는 code PR 만. Doc-only hub + 도메인 ADR collocate 시 (mctrader 패턴).
   - **Mode C (mechanical Epic, NEW Amendment 2)**: Mode B special case. Phase 2-N 모든 PR 가 동일 mechanical content (file copy 동일 + acceptance 동일 + Sonnet 무발화 + parent Epic §5 표 enumerate). child Story Issue / per-lane spec 생략 허용. CFP-120 / CFP-121 Phase 2 사용 사례. PR body marker `mode: mechanical` 의무.
   - Mixed-mode 금지 — 단일 Epic 내 모드 일관 유지 (다른 Epic 은 다른 mode 가능).
3. parent Epic Issue 생성 (owner repo)
4. child Story 생성 — 선택된 mode 에 따라 hub 또는 각 작업 repo. Story §1 메타에 `epic_dependencies` graph 명시:
   ```yaml
   epic_dependencies:
     - type: hard_block | design_parallel | impl_parallel
       target: <KEY>
       repo: <owner/repo>
   ```
5. Change Plan §3 에 `consumes: { <producer>: <SemVer> }` 버전 고정 의무

#### Epic 진행
- **Topological merge order**: dependency graph 따라 producer 먼저 → consumer 나중
- `hard_block` 위반 detected 시 Epic 차단 (PMOAgent enforce)
- `design_parallel` / `impl_parallel` = 동시 진행 허용
- **Joint-phase PR 허용** (ADR-020 Amendment 1 §결정 9): 단일 Story 가 1 phase 안에서 multi-repo joint PR 보유 가능 (예: foundation Story 의 data + engine 동시 변경). 모든 PR 가 동일 Story key reference + dependency graph topological merge.

#### Epic Rollback
producer merge 후 consumer break 시:
1. Producer revert PR open
2. 모든 affected consumer 의 contract 버전 하향 고정 PR
3. Producer fix → 새 minor SemVer release
4. Consumer 버전 고정 갱신

#### Epic close — `EPIC-RESULTS-<EPIC_KEY>.md` artifact 의무 (CFP-83)

Epic close PR (Phase N+1) 동반 작성:

- **위치**: [`docs/doc-locations.yaml`](doc-locations.yaml) `epic_results` row 참조 ([ADR-041](adr/ADR-041-doc-location-registry.md)) — Mode A/B/C → `<scope>/docs/retros/` / dogfood → `<internal-docs>/<plugin-folder>/retros/` (Amendment 1 — CFP-288)
- **Template**: [`templates/epic-results.md`](../templates/epic-results.md) — 14 섹션 의무 (§1 child Story summary / §2 Phase decomposition / §3 Blocking AC / §4 Calibration AC / §5 Demonstration AC / §6 Codex review aggregate / §7 자율 결정 요약 (Sonnet decider) / §8 Out-of-scope / §9 CI iteration 통계 + 사용자 stop trigger 횟수 / §10 PR gate evidence / §11 후속 candidate 우선순위 / §12 debut-audit metric / §13 통계 / §14 결론)
- **작성자**: PMOAgent self-write (codeforge-pmo lane plugin owner)
- **mctrader 사례**: `mctrader-hub/docs/retros/EPIC-RESULTS-MCT-*.md` (Amendment 1 — root → docs/retros/)
- **§9 stop trigger 횟수** = ADR-025 + Amendment 1 (CFP-73 / CFP-80) stop discipline metric. 합법 stop whitelist 5종 외 stop = `policy_violation` defect 추적.
- **§10 PR gate evidence** = 향후 audit 시 GitHub API 라벨 verify fall-back evidence (Issue #181 P1-5 partial 해소)

#### Cross-references
- [ADR-020](../docs/adr/ADR-020-cross-repo-epic-pattern.md) + Amendment 1 + 2 (cross-repo Epic 패턴 SSOT — Mode A / B / C + Joint-phase narrow form)
- [requirements-output-v1.1](../docs/inter-plugin-contracts/requirements-output-v1.md) (Story §1 epic_dependencies field schema)
- [`consumer-guide.md`](consumer-guide.md) §5.1 (consumer 측 mode 선택 안내 — Mode A/B 비교표)

### §3.4.1 Multi-repo Story Routing (CFP-342 / ADR-069)

`project.yaml`의 `codeforge.stories.repos[]` 블록이 선언된 consumer에서 Orchestrator가 Story 작업 대상 repo를 결정하는 절차. [ADR-069](../docs/adr/ADR-069-multi-repo-story-key-system.md) §결정 4 SSOT.

#### Agent target repo 결정 우선순위 (4-step)

```
1. Frontmatter primary — story_scope: repo + repo: <name>
   → project.yaml repos[] 에서 name 매핑 → 해당 impl repo 직접 지정

2. Hub fallback — story_scope: hub
   → project.yaml 에서 role: governance repo 조회 → hub repo 작업

3. Component fallback (legacy / frontmatter 부재)
   → Issue label 'component:<name>' 검색
   → project.yaml repos[].components 매핑 검색
   → 단일 match → 해당 impl repo
   → N(>=2) match → ESCALATE (ambiguous)

4. ESCALATE — 1-3 모두 실패
   → Orchestrator 경유 사용자 명시 요청 (§2.3 ESCALATE 형식)
```

**Backward compat**: Story frontmatter 에 `story_scope` 없는 기존 Story (`legacy-hub`) 는 step 3 → component fallback 진입. component 매핑 부재 시 hub repo 묵시 처리 (단일 hub repo 가정).

#### Project Config Packet 확장

lane spawn 시 Orchestrator 가 subagent 에 주입하는 Project Config Packet ([§12 참조](#12-project-config-packet))에 `codeforge.stories` slice 추가:

```yaml
# Project Config Packet 추가 항목 (codeforge.stories 활성 시)
codeforge_stories_active: true
hub_repo: <name>                      # role: governance repo name
hub_github: <owner/repo>              # hub GitHub 좌표
repos:                                # impl repo 목록
  - name: <name>
    role: implementation
    path: <local-path>
    github: <owner/repo>
    story_dir: <story-dir>
    components: [<component>, ...]
counters_path: <path>                 # .codeforge/counters.json 위치
```

#### Story 생성 결정 로직

| 작업 유형 | 결정 | Story 위치 |
|---|---|---|
| Cross-repo 조율 (N repo 동시 영향) | Hub story 생성 (story_scope: hub) | hub repo / docs/stories/<KEY>.md |
| 단일 impl repo 작업 | Repo story 생성 (story_scope: repo) | <impl-repo-path>/docs/stories/<KEY>.md |
| Cross-repo + 구현 동시 | Hub story 먼저 → 각 impl repo story (delegates[]) | hub + impl 각자 |
| Legacy flat key (frontmatter 부재) | legacy-hub 처리 → hub repo | hub repo / docs/stories/<KEY>.md |

#### Bidirectional linking 의무 (AC-8)

- Hub story `delegates[]` 의 각 entry → 해당 repo story file 존재 여부 확인 (warn-only, block 아님)
- Repo story `hub_story` + `hub_repo` → hub story file 존재 여부 확인 (warn-only)
- Drift 발견 시: `[multi-repo-routing] WARN: delegate drift — <repo>#<KEY> 미존재` 형식으로 알림

#### Counter 발급 (Phase 2 자동화 — 현재 Phase 1 = manual)

Phase 1 (현재): 사용자가 `.codeforge/counters.json` 직접 관리. Orchestrator는 counter 값 읽어 KEY 결정 후 사용자에게 increment 안내.

Phase 2 (follow-up CFP): `scripts/codeforge-story-counter.py` 자동 발급 (file lock + atomic rename + reconciliation).

#### Cross-references
- [ADR-050](../docs/adr/ADR-020-cross-repo-epic-pattern.md) §결정 4 (Agent target repo 결정 priority SSOT)
- [ADR-020](../docs/adr/ADR-020-cross-repo-epic-pattern.md) Amendment 3 (본 시스템 = Mode B automation layer)
- [`consumer-guide.md`](consumer-guide.md) §3 (multi-repo story key 활성화 가이드)
- [`overlay/_overlay/project.yaml.example`](../overlay/_overlay/project.yaml.example) (codeforge.stories 블록 예시)

### §3.4.2 Parallel epic coordination (ADR-050 + Amendment 1 CFP-534)

복수 Orchestrator 세션 (두 개 이상 Claude Code 창) 이 서로 다른 Epic 을 병렬 진행할 때 충돌 조율 의무 SSOT.

**Epic Scope Manifest 작성 의무**: Phase 1 시작 시 Orchestrator 가 Epic Issue body 에 `<!-- scope_manifest -->` 블록 작성. GitOpsAgent 가 다른 open 에픽과 교집합 검사.

**필드 의미** (Amendment 1, CFP-534 — 3 신규 field 추가):

| Field | 의미 | 충돌 라벨 |
|---|---|---|
| `planned_adrs[]` | 예약 ADR 번호 (ADR-RESERVATION.md sequential append) | `conflict:adr-number` |
| `planned_files[]` | 예상 변경 파일 경로 | `conflict:file-overlap` |
| `planned_claude_md_sections[]` | CLAUDE.md / playbook 섹션 (section-ownership.yaml lookup) | `conflict:section-locked` |
| `planned_inter_plugin_contracts[]` (신규) | inter-plugin-contracts file 경로 (`MANIFEST.yaml` 포함) | `conflict:contract-overlap` |
| `planned_label_registry_bumps[]` (신규) | label-registry-v2.md version bump 의도 (`kind: MAJOR\|MINOR\|PATCH` + `scope`) | `conflict:registry-bump-overlap` |
| `cross_section_conflict_detection` (신규, default false) | cross-section 검사 활성 flag — true 시 frontmatter 3-location 의미 충돌 사전 경고 | (activation flag — 라벨 부여 0건) |

**GitOpsAgent intersection 검사 동작** (Amendment 1):

1. `parallel-epic-conflict-check.yml` workflow 가 변경 파일 lookup → `conflict:*` 라벨 자동 부여.
2. GitOpsAgent 가 양쪽 PR 에 `[GitOps]` prefix WARN comment 자동 발의 — 충돌 영역 / 상대 PR / merge-order / 권장 조치 명시.
3. lower CFP 번호 PR = `merge-order:1` 부여, 후순위 PR = `merge-order:2` + rebase 지시.
4. 미해결 시 PMOAgent sibling SendMessage → cross-Story hotspot 패턴 감지 → ADR 후보 발의 가능.

**Sentinel evidence (CFP-534)**: 2026-05-13 KST CFP-521 v2.4 vs CFP-429 v2.5 가 `docs/inter-plugin-contracts/label-registry-v2.md` frontmatter 3-location (`version` / `bumped_at` / `amendments[]` row) 동시 수정 → manual 15분 추가 + risk. Amendment 1 = 해당 사고 재발 방지 carrier.

**Cross-references**: [ADR-050](../docs/adr/ADR-050-parallel-epic-conflict-coordination.md) Amendment 1 / `templates/github-workflows/parallel-epic-conflict-check.yml` / sibling `mclayer/plugin-codeforge-pmo` `agents/GitOpsAgent.md` §3.5 / `docs/parallel-work/section-ownership.yaml`.

### §3.5 Worktree dispatch (CFP-136 / ADR-040)

매 lane spawn 시 Orchestrator 가 worktree 생성 후 sub-agent 에 cwd 주입. file 충돌 0 보장.

**Lifecycle**:

1. **lane spawn 직전**:
   ```bash
   bash templates/scripts/worktree-create.sh cfp-NNN/<lane> origin/main
   # → returns worktree path: $HOME/.claude/worktrees/<repo>/cfp-NNN-<lane>
   ```
   하위 sub-task (SubAgent / role:dev) 가 있으면 sub-worktree 추가:
   ```bash
   bash templates/scripts/worktree-create.sh cfp-NNN/<lane>/<sub> cfp-NNN/<lane>
   ```

2. **sub-agent spawn 시**: prompt 에 `Working dir: <worktree-path>` 명시. sub-agent 가 cd 해서 작업.
   - **`git -C <worktree_abs_path>` 강제 directive (ADR-040 Amendment 6 / CFP-843)**: spawn prompt 에 "All file operations MUST target `<worktree_abs_path>` — git command = `git -C <worktree_abs_path> <subcommand>` (상대경로 git 호출 금지), Write/Edit tool = absolute path rooted at `<worktree_abs_path>`, path 정규형 = forward slash (cross-platform MSYS Git Bash 정합)" 1줄 의무. 근거: harness 가 bash 호출 간 cwd 를 reset → 상대경로 git/tool 호출이 main repo root 로 resolve → agent-internal write 가 main working tree 에 landing (CFP-825 §3 RC-1 동근원).

3. **sub-agent return 후**: Orchestrator 또는 sub-agent 가 자기 sub-branch 에 commit. Sequential merge:
   ```bash
   bash templates/scripts/worktree-merge.sh cfp-NNN/<lane> cfp-NNN/<lane>/<sub1> cfp-NNN/<lane>/<sub2>
   ```

4. **lane 완료 후**: parent (story root) branch 으로 merge:
   ```bash
   bash templates/scripts/worktree-merge.sh cfp-NNN cfp-NNN/<lane>
   ```

5. **Story 완료 후**: 모든 sub-worktree prune:
   ```bash
   bash templates/scripts/worktree-prune.sh cfp-NNN/<lane>/<sub>
   bash templates/scripts/worktree-prune.sh cfp-NNN/<lane>
   ```
   Story root worktree 는 **PR merge 확인 후** prune:
   ```bash
   # 1) branch protection 감지
   PROTECTED=$(gh api "repos/$(gh repo view --json nameWithOwner --jq .nameWithOwner)/branches/main" --jq '.protected')
   # PROTECTED=true → merge 시도 금지, push → PR → mergedAt 확인 순서 필수
   # PROTECTED=false → local merge 후 바로 cleanup 가능

   # 2) PR merge 확인 (non-null mergedAt = merged) — PROTECTED=true 시 필수
   gh pr view <PR_NUMBER> --json mergedAt --jq .mergedAt

   # 3) mergedAt 확인 후 cleanup
   MAIN_ROOT=$(git -C "$(git rev-parse --git-common-dir)/.." rev-parse --show-toplevel)
   cd "$MAIN_ROOT"
   git worktree remove "$HOME/.claude/worktrees/<repo>/cfp-NNN"
   git worktree prune
   git branch -d cfp-NNN
   ```
   **branch-protected repo** (`PROTECTED=true`): push → PR 생성 → `mergedAt` 확인 → cleanup 순서 강제 (ADR-040 Amendment 2). pre-merge `git worktree remove` = policy violation.

**Conflict 처리**:
- worktree-merge.sh 가 conflict detect 시 exit code 2
- Orchestrator 가 conflict 받으면 chief author / 충돌 SubAgent sub-agent 재 spawn (cwd = parent worktree)
- 또는 PMOAgent escalation (CFP-139 GitOpsAgent 도입 후)

**SessionStart hook**:
- `bash templates/scripts/check-worktree-stale.sh` 자동 호출
- 7일 이상 + origin 부재 worktree 자동 prune

**Cross-platform**:
- Windows: `${HOME}\.claude\worktrees\<repo>\<branch-flat>` (PowerShell or Bash via Git for Windows)
- macOS / Linux: `~/.claude/worktrees/<repo>/<branch-flat>`
- Path 변환은 `worktree-path-util.sh` 함수 (`is_windows`, `to_posix_path`).

**Marketplace sync PR proactive dispatch (CFP-597 / [ADR-063](../docs/adr/ADR-063-marketplace-atomic-invariant.md) Amendment 1)**:

Orchestrator 가 Phase 2 PR open 시점에 Change Plan §13 안 `marketplace_sync_required: true` declare 감지 시 GitOpsAgent (codeforge-pmo) spawn. spawn prompt:

**artifacts (verbatim 첨부, [ADR-070](../docs/adr/ADR-070-codex-verify-before-trust.md) verify-before-trust mandate)**:
- Change Plan §13 sub-row (`marketplace_sync_required` + `mirrored_fields_changed[]` + `triggering_plugins[]`)
- triggering plugin name + 변경된 mirrored field enum

**GitOpsAgent §3.6 행위** (codeforge-pmo sibling, Phase 2 carrier):
1. `mclayer/marketplace` repo worktree 신설 — branch `cfp-NNN`, base `main`
2. `.claude-plugin/marketplace.json` 안 해당 plugin entry 의 mirrored field 갱신 (`mirrored_fields_changed[]` 기준)
3. marketplace PR open — title `[CFP-NNN] Sibling sync — <plugin> <version> mirrored field update`
4. PR body 안 `Closes <triggering-plugin-PR>` cross-reference
5. ADR-063 §결정 2 ordering 정합 — marketplace PR 선행 merge 의무

dispatch trigger: Phase 2 PR carrier (Orchestrator monopoly, ADR-039 subagent default 정합). lane 위치 = codeforge-pmo (GitOpsAgent home, sibling plugin). reactive `check-marketplace-parity.sh` channel = defense-in-depth 보존.

**의존성**:
- ADR-024 amendment 1 (hierarchical branch convention)
- ADR-040 (worktree convention SSOT)
- CFP-137 (agent teams 적극 도입) — 본 §3.5 의 use case full
- CFP-139 (GitOpsAgent) — Orchestrator 의 worktree management 책임을 GitOpsAgent 로 이관 (Wave 3)
- CFP-597 (ADR-063 Amendment 1) — marketplace sync PR proactive dispatch trigger

#### §3.5.1 Parallel work sentinel polling (CFP-966 / [ADR-073 Amendment 2](../docs/adr/ADR-073-orchestrator-verify-before-assert.md))

> **NORMATIVE — ADR-073 Amendment 2 §결정 1-A/1-B/1-C declarative anchor**. lane spawn 직전 (§3.5 step 1) 시점에 적용되는 mid-flight parallel race 차단 polling 의무. mechanical wire (lint script + workflow + hook json sample) = sibling Story-2 CFP-967 carrier — 본 §3.5.1 = behavioral directive + declarative anchor (declaration-only-Wave-1 status).

**동인 (sentinel evidence)**: 2026-05-18 KST same-day 2/2 parallel race incidents — CFP-953 (first, label-based search miss → CFP-932 carrier miss) + CFP-946 (second, 11분 gap Epic close miss → PR #962 "Closes #946" 충돌). long-running Orchestrator session 의 turn-0-only SessionStart snapshot staleness 영역.

**Transition trigger enum 3종 (closed set)** — 각 transition 직전 polling 의무:

| ID | 발화 시점 | Polling 의무 |
|----|---|---|
| `lane_spawn` | lane 진입 직전 (§3.5 step 1 — Agent tool spawn 직전) | title-based search + Epic state poll + HEAD compare |
| `pr_open` | PR open 직전 (`gh pr create` 직전, Phase 1 / Phase 2 / retro PR) | 동일 3-step + sibling Story PR list cross-ref |
| `merge_transition` | PR merge 직전 (`gh pr merge` 직전) + 직후 (gate label / phase label transition 직전) | 동일 3-step + Epic state final poll (close eligibility check) |

closed enum — 4번째 trigger 추가 = ADR-073 Amendment 강화 방향만 (ADR-058 §결정 5 / ADR-064 §결정 7 top-down ratchet 정합).

**HEAD compare pattern (verify-before-trust 4-layer governance Layer 1)** — 매 transition trigger 직전 3-step 의무:

```bash
# Step 1 — title-based search (memory rule 6 의무, CFP-953 incident carrier)
gh issue list --search "<keyword>" --state all --json number,title,labels,closedAt
# label-based search 만 (rule 6 위반) → CFP-953 incident reproduction risk

# Step 2 — Epic state poll (memory rule 7 의무, CFP-946 incident carrier)
gh issue view <epic_number> --json state,closedAt,closedBy,labels
# polling 직전 5+ min 경과 session state cache (TodoWrite / Story §0 / .claude-work/progress) 무조건 stale 가정

# Step 3 — HEAD compare sibling commits (mid-flight race 차단)
PRIOR_HEAD=<session state cache 의 pinned HEAD — stale 가능>
CURRENT_HEAD=$(git ls-remote origin <branch> | cut -f1)   # direct verify (재고정)
gh api repos/{owner}/{repo}/compare/${PRIOR_HEAD}...${CURRENT_HEAD} --jq '.commits[].sha'
```

**Cold start `session_start` 보강**: session 첫 turn additionalContext 안 active CFP context list + open Epic state list + current branch HEAD vs origin/main delta 3-item preload (SessionStart hook tier 위임 — Story-2 CFP-967 `templates/.claude/hooks/SessionStart-parallel-work-poll.json.sample` mechanical wire). additionalContext = layer 1 fallback 만 — actual sustained polling = 매 transition trigger 직전 §3.5.1 3-step.

**Sustained in-session polling 의무**: turn-0-only SessionStart hook 한계 해소 — long-running session 안 매 transition trigger 직전 HEAD SHA 재고정 의무 (session state cache stale 무조건 가정).

**Cross-ref**:
- [ADR-073 Amendment 2](../docs/adr/ADR-073-orchestrator-verify-before-assert.md) §결정 1-A/1-B/1-C — declarative anchor SSOT
- `docs/evidence-checks-registry.yaml` `parallel-work-sentinel-pickup` entry — warning tier (declaration-only-Wave-1, recurrence count 2 / threshold 3 / promotion_trigger auto_blocking)
- [`docs/domain-knowledge/domain/orchestrator-discipline/parallel-work-sentinel-polling.md`](../docs/domain-knowledge/domain/orchestrator-discipline/parallel-work-sentinel-polling.md) — narrative SSOT (sentinel batch + escalation matrix)
- memory rule 6 (title-based search 의무, CFP-953 carrier) + rule 7 (Epic 진행 중 polling 의무, CFP-946 carrier) — declarative cross-ref normative anchor
- sibling Story-2 [CFP-967](https://github.com/mclayer/plugin-codeforge/issues/967) — mechanical wire (script + hook + workflow + bats), sequential (Story-1 merge 후)

#### §3.5.2 Cross-repo worktree target authority verify (CFP-1578 / [ADR-082 Amendment 21](../docs/adr/ADR-082-write-time-self-write-verification-mandate.md) §결정 1 sub-scope 1-J)

> **NORMATIVE — ADR-082 Amendment 21 §결정 1 layer 1 sub-scope (1-J) declarative anchor**. chief author / lane agent / Orchestrator 가 spawn prompt 작성 또는 직접 file write 직전 cross-repo worktree target authority verify-before-write 의무. mechanical wire (lint script + workflow + hook json sample + bats fixture) = 별 sub-CFP Wave 2 carrier — 본 §3.5.2 = behavioral directive + declarative anchor (Wave 1 declaration-only).

**동인 (sentinel evidence)**: CFP-1539+CFP-1540 batch retro §4.1 #2 — PMOAgent retro spawn 시 internal-docs PR target 작성 시 wrapper repo plugin-codeforge worktree 안에서 `git worktree add` 시도 후 정정 발생. wrapper repo worktree mis-target 첫 catch occurrence. ADR-013 dogfood-out internal-docs SSOT path (Story file + Change Plan + retro = internal-docs) + ADR-040 worktree convention (각 repo 별 worktree 분리) 정합 영역 codify 부재. paired sibling = CFP-1559 Amendment 20 (Issue body stale claim pre-screen super-class, axis disjoint — content verify vs target authority verify, 동시 발의 race).

**4-tuple primitive (cross-repo write-target boundary mandate)** — spawn prompt 작성 또는 직접 file write 직전 4 의무:

| ID | Primitive | 동작 |
|----|---|---|
| (a) | worktree target authority verify-before-write | `git -C <worktree_abs_path> remote -v` 실행 → expected repo (예: wrapper plugin-codeforge vs internal-docs) 와 actual remote URL 일치 확인. mismatch 시 write 차단 + sentinel 발화 |
| (b) | spawn prompt 안 `worktree_target_repo: <expected-repo-name>` field | write-target authority anchor block 형식 명시 (sub-scope 1-C `[USER-UTTERANCE-VERBATIM]` + 1-E `[PRE-SPAWN-ORIGIN-MAIN-SHA]` block precedent 답습). enum = `wrapper` / `internal-docs` / `marketplace` / `consumer-<name>` |
| (c) | cross-repo 작업 sequence 시 명시적 worktree switch | wrapper repo worktree 안에서 internal-docs PR 생성 시도 금지 (각 repo 별 worktree 분리, ADR-040 정합). cross-repo write 필요 시 별 worktree explicit create + cwd switch + write 의무 |
| (d) | verified-via annotation `worktree_target_authority_verified: <bool>` | spawn prompt 안 명시 (write-time semantic truth verify, annotation 부재 시 sentinel 발화) |

**Verify pattern (verify-before-trust 4-layer governance Layer 3 — ADR-082 sub-scope 1-J)**:

```bash
# Step 1 — worktree target repo authority verify (mandate (a))
ACTUAL_REMOTE_URL=$(git -C <worktree_abs_path> remote get-url origin)
# expected = wrapper plugin-codeforge → "mclayer/plugin-codeforge"
# expected = internal-docs → "mclayer/codeforge-internal-docs"

# Step 2 — expected target enum 일치 verify (mandate (a))
EXPECTED_REPO="wrapper"   # spawn prompt field (b) 에서 declare
case "$EXPECTED_REPO" in
  wrapper) EXPECTED_URL_PATTERN="mclayer/plugin-codeforge" ;;
  internal-docs) EXPECTED_URL_PATTERN="mclayer/codeforge-internal-docs" ;;
  marketplace) EXPECTED_URL_PATTERN="mclayer/marketplace" ;;
  consumer-*) EXPECTED_URL_PATTERN="mclayer/${EXPECTED_REPO#consumer-}" ;;
esac
if ! echo "$ACTUAL_REMOTE_URL" | grep -q "$EXPECTED_URL_PATTERN"; then
  echo "ERROR: worktree target mismatch — expected $EXPECTED_REPO ($EXPECTED_URL_PATTERN), got $ACTUAL_REMOTE_URL"
  exit 1
fi

# Step 3 — cross-repo write 시 별 worktree switch (mandate (c))
# wrapper worktree 안에서 internal-docs PR 생성 시도 = mismatch → step 2 차단
# 필요 시 internal-docs 별 worktree 생성:
# git -C /path/to/internal-docs-repo worktree add <internal-docs-worktree> <branch>
```

**Cold start sentinel**: session 첫 turn 직후 active worktree list scan + worktree↔expected-repo 매핑 확인 (SessionStart hook tier 위임 — Wave 2 sub-CFP `templates/.claude/hooks/SessionStart-worktree-target-verify.json.sample` mechanical wire). actual sustained verify = 매 spawn prompt 작성 또는 file write 직전 §3.5.2 mandate.

**Cross-ref**:
- [ADR-082 Amendment 21](../docs/adr/ADR-082-write-time-self-write-verification-mandate.md) §결정 1 layer 1 sub-scope (1-J) — declarative anchor SSOT
- [ADR-040 worktree convention](../docs/adr/ADR-040-worktree-convention.md) — namespace 표준 (`${HOME}/.claude/worktrees/<repo-name>/<branch-flat>`) + worktree-first normative 정합
- [ADR-013 dogfood-out internal-docs SSOT](../docs/adr/ADR-013-codeforge-family-dogfood-out-policy.md) — Story file + Change Plan + retro = internal-docs / src + tests + workflow + ADR + CLAUDE.md = wrapper plugin-codeforge
- `docs/evidence-checks-registry.yaml` `worktree-target-authority-verify` entry — warning tier deferred-followup (Wave 2 sub-CFP wire)
- paired sibling CFP-1559 Amendment 20 — Issue body stale claim pre-screen super-class, axis disjoint (content verify vs target authority verify, 동시 발의 race)
- 동인: CFP-1539+CFP-1540 batch retro §4.1 #2 — worktree mis-target 첫 catch carrier

#### §3.5.3 Version race coordination sequential merge orchestration (CFP-1603 / [ADR-045 §D-9](../docs/adr/ADR-045-story-retro-mandatory-trigger.md) pattern_count 2 escalation_resolved_carrier)

> **NORMATIVE — ADR-045 §D-9 forcing function 산출 declarative anchor** (escalation_action: `escalate_user`, escalation_resolved_carrier: CFP-1603). same-day multi-Story plugin.json version bump 영역 의 race resolution sequence orchestration codify. mechanical wire (workflow lint + bats fixture) = 별 sub-CFP Wave 2 carrier — 본 §3.5.3 = behavioral directive + declarative anchor (Wave 1 declaration-only).

**동인 (sentinel evidence, pattern_count 2 reach)**:

| # | Occurrence | Story batch | Race semantic |
|---|---|---|---|
| 1 | Wave 2 batch (2026-05-25 KST 전반) | CFP-1559 PATCH (6.7.3) + CFP-1540 (sentinel script cp949 fix) | sentinel script invocation reliability fix sibling (race coordination axis disjoint — first occurrence carrier) |
| 2 | Wave 3 batch (2026-05-25 KST 후반) | CFP-1580 MINOR (6.8.0) + CFP-1559 rebase (6.7.3 → 6.8.1) | 양 PR same base SHA (6.7.2) target → race resolution sequence: #1580 선행 merge (MINOR > PATCH per ADR-037 §결정 1) → #1559 rebase 6.7.3 → 6.8.1 PATCH + marketplace sibling sync |

ADR-045 §D-9 pattern_count ≥ threshold 2 reach = Mandatory framing 발동 영역 (PMOAgent retro 산출 evidence). 본 carrier = `escalation_action: escalate_user` resolution (declarative-only Wave 1 codify), Wave 2 mechanical wire = 별 sub-CFP.

**Race detection criteria (same-base-SHA primitive)**:

| ID | Criterion | Trigger |
|----|---|---|
| (a) | same-base-SHA + same-mirrored-field | 복수 Story (동일 또는 별 Orchestrator session) plugin.json `.version` field bump target 이 동일 base SHA (예: 6.7.2) 인 경우 — sentinel polling §3.5.1 `lane_spawn` / `pr_open` transition trigger 직전 HEAD compare step 에서 자연스럽게 detect |
| (b) | same-day multi-Story batch | session boundary 와 무관 — 동일 base SHA target 시 race 활성 (ADR-040 worktree convention 정합, 각 Story 별 worktree 분리) |
| (c) | marketplace sibling sync trigger 동반 여부 | mirrored field (`name` / `version` / `description` / `author`) 변경 시 marketplace sibling PR 동반 — ADR-063 §결정 2 ordering 활성. 변경 0 시 sequential ordering 4-step → 2-step 축소 (mandate 5 fallback) |

**Sequential merge orchestration sequence — 4-step (full path, marketplace sibling sync 동반 시)**:

```
선행 PR (MINOR, 예 6.8.0) + 후행 PR (PATCH, 예 6.7.3) same base SHA 6.7.2 target

Step 1 — 선행 marketplace sibling PR merge (선행 PR mirrored field MINOR mirror)
  · marketplace.json `.plugins[name=codeforge].version` 6.7.2 → 6.8.0 sync
  · ADR-063 §결정 2 ordering 정합 — marketplace PR 선행 merge

Step 2 — 선행 plugin PR merge (MINOR 6.8.0)
  · plugin.json `.version` 6.7.2 → 6.8.0 atomic (3-file invariant ADR-063 §결정 1)
  · CHANGELOG.md `[Unreleased]` → `[6.8.0]` released entry transition

Step 3 — 후행 plugin PR rebase + version bump 재계산 (6.7.3 → 6.8.1)
  · git rebase origin/main (base SHA 6.7.2 → 6.8.0)
  · plugin.json `.version` 6.7.3 → 6.8.1 재bump (SemVer monotonic invariant: PATCH 6.7.3 < MINOR 6.8.0 < PATCH rebased 6.8.1)
  · CHANGELOG.md `[Unreleased]` merge conflict resolve — chronological append (선행 6.8.0 entry 위, 후행 entry 아래) OR 후행 별 sub-section
  · 후행 marketplace sibling PR (PATCH rebased 6.8.1 mirror) rebase 동반

Step 4 — 후행 marketplace sibling PR merge → 후행 plugin PR merge (PATCH 6.8.1)
  · marketplace.json `.plugins[name=codeforge].version` 6.8.0 → 6.8.1 sync
  · plugin.json `.version` 6.8.1 atomic
```

**Sequential merge orchestration sequence — 2-step (marketplace sibling sync 부재 축소 path)**:

```
선행 PR + 후행 PR mirrored field 변경 0건 (예: doc-only fast-path Story batch)

Step 1 — 선행 plugin PR merge
  · plugin.json 변경 0, CHANGELOG.md `[Unreleased]` entry 추가

Step 2 — 후행 plugin PR rebase + merge
  · git rebase origin/main (선행 PR merge commit 포함)
  · CHANGELOG.md `[Unreleased]` merge conflict resolve — chronological append
  · plugin.json bump 0건 (race coordination orchestration 자체는 mirrored field 변경 0 시에도 적용 — base SHA 변경 시 후행 PR rebase 의무)
```

**ordering invariant (MINOR > PATCH > PATCH per ADR-037 §결정 1 정합)**:

```
race resolution priority:
  MAJOR > MINOR > PATCH

동일 surface category (예: PATCH + PATCH) race 시:
  lower CFP 번호 선행 merge (ADR-050 §3.4.2 patterns 답습)

후행 PR rebase 후 bump 재계산:
  base 변경분 + 후행 PR 변경분 합산 → SemVer monotonic 보장
  · MINOR + PATCH = MINOR rebased to MINOR.MINOR+1.0 OR PATCH (semantic preserve)
  · PATCH + PATCH = PATCH rebased to next PATCH
  · MAJOR + MINOR = MAJOR rebased to MAJOR.MINOR+1.0 (ADR-063 Amendment 7 §결정 18 9-plugin atomic MAJOR scope 정합 시 atomic bundle 의무)
```

**Race resolution example (Wave 3 evidence verbatim, 2026-05-25 KST)**:

| Step | Actor | Action | Resulting state |
|------|---|---|---|
| 1 | Orchestrator | sentinel polling §3.5.1 `pr_open` transition direct verify | #1580 (MINOR 6.8.0) + #1559 (PATCH 6.7.3) both target base 6.7.2 — race detected |
| 2 | Orchestrator | ADR-037 §결정 1 ordering decide — MINOR 선행 | #1580 first merge order assigned |
| 3 | GitOpsAgent (codeforge-pmo §3.6) | marketplace sibling PR #1580-marketplace open + merge | marketplace.json 6.8.0 sync |
| 4 | Orchestrator | #1580 plugin PR merge | plugin.json 6.7.2 → 6.8.0, CHANGELOG `[Unreleased]` → `[6.8.0]` |
| 5 | Orchestrator | #1559 rebase + version bump 재계산 | plugin.json 6.7.3 → 6.8.1, CHANGELOG `[Unreleased]` entry chronological append |
| 6 | GitOpsAgent | marketplace sibling PR #1559-marketplace rebase + merge | marketplace.json 6.8.0 → 6.8.1 sync |
| 7 | Orchestrator | #1559 plugin PR merge | plugin.json 6.8.0 → 6.8.1 atomic |

**Wave 2 mechanical wire carrier (declaration-only Wave 1 retain — Wave 2 별 sub-CFP)**:

- workflow lint — same-day multi-Story plugin.json version bump 영역 sequential merge ordering 자동 verify (별 sub-CFP, evidence-checks-registry `version-race-coordination-ordering` entry 후보)
- bats fixture — race resolution scenario coverage (MINOR+PATCH / PATCH+PATCH / MAJOR+MINOR / marketplace 부재 축소 4 case)
- `mechanical_enforcement_actions: []` declaration-only-Wave-1 (ADR-082 §결정 6 + ADR-070 §D5 retain pattern 답습)

**Cross-ref**:

- [ADR-037 §결정 1 plugin version bump rule](../docs/adr/ADR-037-plugin-version-bump-rule.md) — SemVer monotonic invariant + Option β core rule (Lenient base, 12 surface category) upstream policy SSOT
- [ADR-063 §결정 1/§결정 2 marketplace atomic invariant](../docs/adr/ADR-063-marketplace-atomic-invariant.md) — 3-file atomic invariant + marketplace sibling sync ordering upstream policy SSOT
- [ADR-045 §D-9 cross_story_pattern_adr_trigger](../docs/adr/ADR-045-story-retro-mandatory-trigger.md) — forcing function SSOT (pattern_count threshold 2 → escalate_user → 본 §3.5.3 codify carrier)
- [ADR-050 §3.4.2 Parallel epic coordination](../docs/adr/ADR-050-parallel-epic-conflict-coordination.md) — Epic-scope conflict detection (axis disjoint, PR-level post-hoc) cross-ref
- §3.5.1 Parallel work sentinel polling — race detection mechanism (sentinel polling `pr_open` / `merge_transition` transition trigger 가 race detect)
- [ADR-024 §3 sequence-of-singletons](../docs/adr/ADR-024-story-scoped-branch-policy.md) — trunk-based branching axis (release branch 부재, main-direct PR sequential)
- §3.6 marketplace sync PR proactive dispatch (CFP-597 / ADR-063 Amendment 1) — GitOpsAgent §3.6 행위 (sibling axis disjoint, marketplace sibling sync proactive dispatch vs race resolution sequence orchestration)
- 동인: ADR-045 §D-9 pattern_count 2 reach (Wave 2 + Wave 3 batch sentinel evidence) escalation_resolved_carrier

### §3.6 TeamCreate / TeamDelete protocol (CFP-137 / [ADR-044](../docs/adr/ADR-044-phase-scoped-sequential-team.md))

> **Activation**: `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` env 활성 시에만 본 §3.6 적용. env=0 또는 미설정 시 = ADR-039 default subagent context fallback (§3.0 + 기존 §3.1 one-shot Agent tool 패턴).

매 lane 진입 시 Orchestrator (영구 lead) 가 다음 sequence 수행:

```
1. Preflight check (§3B)
2. (CFP-139 후) GitOpsAgent SendMessage — lane worktree 준비 (§3.5 lifecycle)
3. TeamCreate(team_spec=templates/team-spec-<lane>.yaml, worktree=<path>)
   - team-spec yaml 7종 SSOT (ADR-044 §결정 2)
   - Codex worker dispatch_mode=user_request_only — 사용자 explicit request 시에만 활성
4. lane 진행:
   - Lane PL → teammate dispatch (TaskCreate)
   - teammate ↔ teammate SendMessage (Adversarial / Cross-layer 패턴)
   - PL 중재 + dedup → pl_recommendation
5. TeamDelete (in-flight teammate 완료 명시 wait — TeamDelete 시점에 in-flight task 가 있으면 platform 이 자동 wait, Orchestrator 는 추가 polling 미필요)
6. Orchestrator self-write (Story §9 + GitHub gate label + phase transition — review-verdict v4 4-step algorithm)
7. FIX 시 → TEAM-FIX 새 team (parallel diagnosis: DeveloperPL + ArchitectPL)
```

**Lead = Orchestrator** (Story 전 기간 fixed). One-team-per-lead 강제 — 다음 lane TeamCreate 전 현 team `TeamDelete()` 의무.

**team-spec yaml 7종**: `templates/team-spec-{decompose,requirements,design,design-review,develop,code-review,security-test}.yaml`. 구현 테스트 lane = CI gate (ADR-048, team 미생성 — Orchestrator inline `gh pr checks`).

### §3.7 SendMessage 사용 패턴

> **Activation**: env=1 시에만 SendMessage 발화. env=0 시 fallback = Orchestrator round-trip (PL ↔ worker continuous dialog 부재).

**Adversarial debate 패턴** (TEAM-{DESIGN,CODE,SECURITY}-REVIEW, Codex worker 활성 시):

```
1. PL → ClaudeReviewAgent: "primary review pass — 모든 finding 수집"
2. ClaudeReviewAgent → PL: findings packet (round 1)
3. PL → CodexReviewAgent: "Claude packet 검수 + 누락 찾기"
4. CodexReviewAgent → ClaudeReviewAgent (직접 SendMessage): "P1 #3 finding 의 evidence 부족 — file:line cite 추가"
5. ClaudeReviewAgent → CodexReviewAgent: "evidence 추가, 또한 P0 #2 도 보강"
6. PL ↔ both workers: dedup + severity 합의
7. PL → Orchestrator: review-verdict v4 packet (worker_dialog_rounds = 5, ADR-044 §결정 5 measurable)
```

**Cross-layer 패턴** (TEAM-DEVELOP, dev ↔ QA):

```
1. PL → QADev: "Impl Manifest 매핑표 작성"
2. QADev → PL: 매핑표 v1
3. PL → role:dev (e.g., SoftwareDeveloperAgent): "feature X 구현"
4. role:dev → QADev (직접 SendMessage): "test fixture <path> 의 boundary case 추가 권유"
5. QADev → role:dev: "fixture 갱신 — invariant 가 valid 한지 확인 required"
6. PL → develop-output v1.1 packet (cross_layer_dialog_rounds = 2, ADR-044 §결정 5 measurable — codeforge-develop sibling sync follow-up)
```

**Sequential-dialog 패턴** (Stage 0 [TEAM-DECOMPOSE], TEAM-DECOMPOSE):
- PMOAgent + (CFP-139 후) GitOpsAgent 단순 sequential — Adversarial 부재.

### §3.8 TeammateIdle nudge protocol

> **Activation**: env=1 시에만 TeammateIdle hook 발화.

idle teammate 감지 시 platform 이 본 hook trigger:

```
[Hook fires]
  └─ PL 수신: idle teammate name + last_task_completed_at
       ├─ option A: PL → idle teammate SendMessage (추가 task dispatch)
       │   예: TEAM-DESIGN 의 RefactorAgent idle 시 "추가 boundary 검토"
       └─ option B: PL → Orchestrator SendMessage: "TeamDelete 권유 — 모든 teammate finished"
            └─ Orchestrator → TeamDelete (in-flight wait + worktree merge orchestration)
```

Sample hook = `templates/agent-teams-hook-samples/TeammateIdle.json.sample` (ADR-044 §결정 3). Phase 2 PR scope = nudge logic + script 실제 구현.

### §3.9 env-divergent context fallback (default ↔ enabled context 분기)

| env | 동작 |
|---|---|
| `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` | §3.6 + §3.7 + §3.8 활성. team-spec yaml 7종 본격 사용. SendMessage / TaskCreate / TeammateIdle hook 발화. |
| `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=0` 또는 미설정 | ADR-039 default subagent context fallback. Orchestrator 가 lane PL 1개만 spawn (one-shot Agent tool). PL 이 sub-agent 재 spawn 매 round Orchestrator 경유. SendMessage / TeamCreate / TaskCreate / TeammateIdle hook 미발화. team-spec yaml 미사용. review-verdict v4 의 worker_dialog_rounds = 0 (Adversarial 패턴 mechanism level 부재). |

**Backward compat 보장**: env=0 사용자 = 본 CFP-137 도입 후에도 ADR-039 + 기존 §3.1 one-shot 패턴 그대로 동작. 본 CFP-137 의 Phase 1 PR merge 시점에 env=0 사용자 영향 0.

**Hook 등록 의무 (env 무관)**: `templates/agent-teams-hook-samples/{TeammateIdle,TaskCreated,TaskCompleted}.json.sample` 3종 sample 은 consumer 측 `.claude/hooks/` 로 install 가능 — env=0 시 trigger 미발화이지만 install 자체는 무해 (Anthropic platform 이 env 기반 자동 분기). consumer-guide §"Agent teams 적극 도입 (CFP-137)" install 안내 정합.

---

### §3.10 Codex Proactive Check (CFP-354 / [ADR-052](../docs/adr/ADR-052-codex-proactive-check-touchpoints.md))

Orchestrator가 6개 touchpoint에서 `codex:codex-rescue` subagent를 **proactive check** 용도로 자동 dispatch. 기존 `codex:rescue`(사후 대응 — stuck 시) 채널과 분리.

**Dispatch 패턴**:

```text
Agent(subagent_type="codex:codex-rescue", prompt=<ProactiveCheckPacket>)
```

**Codex CLI worker check file-redirect dispatch mandate** (CFP-1244 / [ADR-081 Amendment 6](../docs/adr/ADR-081-codex-worker-prompt-boilerplate.md) §결정 D8 + [ADR-052 Amendment 12](../docs/adr/ADR-052-codex-proactive-check-touchpoints.md)):

codeforge Orchestrator/lane 이 Codex CLI worker check 를 invoke 할 때 (Codex CLI v0.125.0 확인):

1. **file-redirect invocation 의무** — composed worker prompt (D1.A-D 4 mandatory boilerplate field 포함) 를 file 로 write 후 file-redirect 형식 `codex exec --sandbox read-only < <promptfile>` 로 invoke. direct stdin-pipe (prompt 를 stdin 직접 pipe) / inline-arg invocation 금지 — TTY 부재 sandbox 안 0-byte stall (>5min) systemic 원인 (CFP-1187 운영 phase Epic S4/S5 early stall evidence).
2. **result-via-file 수신 + synchronous block-wait 금지** — Codex worker 결과는 output file 경유 수신. Orchestrator 는 Codex stream 을 bounded window 초과 synchronous block-wait 금지 — bounded window 초과 시 다음 step 진행 후 result file pickup (CFP-1187 S7 ArchitectPL stream idle-timeout after 40 tool_uses → redo evidence 차단).
3. **stall / stream idle-timeout 시 substitution** — file-redirect invocation 후에도 stall / stream idle-timeout 발생 시 substitution path `fallback_skip_with_marker` 진입 + Story §10 marker `[codex-sandbox-fallback: dispatch_stall_or_stream_timeout]` (fail-mode enum 8번째 value, ADR-070 Amendment 7 / ADR-052 Amendment 12).

dispatch invocation mandate 본문 SSOT = ADR-081 §결정 D8.

**ProactiveCheckPacket 스키마**:

```yaml
touchpoint: <1|2|3|4|5|6>
purpose: <한 줄 목적>
context:
  lane: <requirements|design|develop|orchestrator>
  story_key: <CFP-NNN>
  artifacts: <첨부 산출물 — verbatim content 의무, CFP-578 / ADR-070 §결정 D2 + ADR-052 Amendment 5>
task: <Codex에게 요청할 구체적 작업>
```

**`artifacts` 필드 verbatim 첨부 의무** (CFP-578 / [ADR-070](../docs/adr/ADR-070-codex-verify-before-trust.md) §결정 D2 + [ADR-052 Amendment 5](../docs/adr/ADR-052-codex-proactive-check-touchpoints.md)):

Codex worker spawn prompt 안 file path reference 만 사용 금지. 모든 file content 가 verify task scope 인 경우 prompt payload 안 verbatim 첨부 필수 — Codex sandbox file system access 실패 (CFP-506 / CFP-520 / CFP-530 3 회 reproduce sentinel) systemic 원인 차단.

| verbatim 첨부 대상 | 영역 |
|---|---|
| 사용자 §1 원문 | story-section-1-immutable.yml SSOT, 변조 금지 invariant 정합 |
| Story §2-§6 / §7 PL synthesis 본문 | sandbox 영역 외 (internal-docs path) |
| 관련 ADR / Change Plan 본문 | sandbox 영역 외 가능성 (cross-repo / cross-plugin path) |
| cross-repo state | sibling plugin file / marketplace.json / contract MANIFEST 등 |

**partial 첨부 허용 (cap 초과 시)**: file content cap 초과 시 (token 비용 risk) → verify 대상 영역만 verbatim 첨부 + 나머지 file path reference 표시 + `[partial: lines NN-NN]` marker 의무.

**verify-before-trust 결과 처리 단계** (CFP-578 / [ADR-070](../docs/adr/ADR-070-codex-verify-before-trust.md) §결정 D1 / D3):

Codex worker 결과 수신 후 Orchestrator 는 finding evidence 의 ground truth 를 own working directory 안 Read / Glob / Grep 으로 verify 의무:

1. Codex finding evidence (인용 본문 / file path / line number / commit SHA / contract version 등) 추출
2. Orchestrator direct file Read / Glob / Grep 으로 evidence 영역 ground truth 확정
3. **mismatch 검출 시 verdict reject** + Story §10 FIX Ledger row append (false positive count tally, fix-event-v1 contract `[codex-false-positive]` sub-tag — schema MINOR bump 별도 carrier) + Orchestrator override rationale 명시 (4 종 verbatim: Codex evidence + Orchestrator Read 결과 + mismatch 영역 + reject 후속 동작)
4. **match 검출 시 finding accept** → recommendation / severity 기반 후속 동작 (PROCEED / ADDRESS_FIRST) 진입

**결과 처리** (touchpoint #2 **mandatory** 분기 — CFP-532 / [ADR-052 Amendment 4](../docs/adr/ADR-052-codex-proactive-check-touchpoints.md), 나머지 5 touchpoint **optional** 유지, verify-before-trust 단계 통과 후):

| recommendation | findings | 처리 (touchpoint #2 **mandatory**) | 처리 (touchpoint #1/#3/#4/#5/#6 optional) |
|---|---|---|---|
| PROCEED | — | 그대로 다음 단계 | 그대로 다음 단계 |
| ADDRESS_FIRST | P0 포함 | 해당 agent findings 반영 후 재진행 (blocking) | 동일 |
| ADDRESS_FIRST | P1-only | **inline FIX 의무 (skip 차단)** | Orchestrator 판단으로 skip 가능 → story §10 기록 |
| ADDRESS_FIRST | P2-only | Orchestrator 판단으로 Story §10 deferred 기록 가능 | 동일 |
| 판정 불일치 (#5 전용) | — | N/A (#5 = optional) | 사용자 에스컬레이션 |
| verify mismatch 검출 (모든 touchpoint) | — | finding reject + Story §10 false positive count tally + override rationale (ADR-070 §결정 D3) | 동일 |

**Boilerplate composition SSOT (CFP-819 / [ADR-081](../docs/adr/ADR-081-codex-worker-prompt-boilerplate.md) + ADR-052 Amendment 6)**: Codex worker prompt 본문 3 mandatory section (dogfood-out Story path verbatim / lane stage 표기 = current_lane + phase / sandbox boundary = sandbox_outside_paths) + verify-before-trust scope 5 sub-scope 분리 (file scope grep+quote / dir scope recursive grep+count / cross-repo gh api+commit SHA / grep count claim active vs historical 차원 / ADR §결정 번호 정확성) + 3-lane partition 표 (Codex factual citation 영역 / DesignReviewPL boundary completeness 영역 [ADR-068 4 invariants + Amd 1 I-5] / CodeReviewPL post-impl style + historical reference 보존성 영역 disjoint scope) = ADR-081 SSOT. declaration-only retain (ADR-070 §D5 precedent), mechanical lint 부재.

**Substitution scope 3-path enum (CFP-946-A / [ADR-052 Amendment 8](../docs/adr/ADR-052-codex-proactive-check-touchpoints.md) + [ADR-070](../docs/adr/ADR-070-codex-verify-before-trust.md) §결정 D1 expansion / Amendment 3)**: Codex worker spawn 결정 시점에 substitution scope explicit declare 의무 — 운영적 substitution behavior 의 normative codification. 9 occurrence sentinel (CFP-756 Epic close retro Sentinel #4 strike #8) 산물.

| Enum value | semantics | 적용 trigger | Story §10 marker (의무) |
|---|---|---|---|
| `inline_orchestrator_verify` (default) | Orchestrator 가 own working directory file Read 로 ground truth 확정 후 Codex finding accept/reject | Codex worker output 정상 수신 (sandbox network-block 없음) + finding evidence 영역 = Orchestrator working directory 안 | (면제 — default, marker 부재 = 암묵 default) |
| `manual_substitution_declare` | Codex worker spawn 직전 substitution scope 명시 declare (spawn prompt `task` field 또는 sub-field `substitution_scope` + Story §10 marker carrier) | sandbox 영역 외 file (internal-docs / sibling repo / cross-plugin path) verify task 필요 시 | `[codex-substitution-scope-declared: <scope-enum>]` (1 회/spawn) |
| `fallback_skip_with_marker` | Codex worker spawn 자체 skip + Orchestrator 가 substitution 후속 동작 단독 수행 (verify-before-trust 5 sub-scope 全 적용) | Codex CLI 미가용 / sandbox network-block 확정 / `codex exec` dispatch stall 또는 stream idle-timeout / 8+ occurrence sentinel reentrant 위험 영역 | `[codex-sandbox-fallback: <fail-mode>]` (1 회/spawn, fail-mode enum 8 종 = `api_missing` / `version_skew` / `enterprise_blocked` / `gh_api_network_blocked` / `manual_substitution_declared` / `inline_orchestrator_verify_only` / `subagent_recursion_blocked` / `dispatch_stall_or_stream_timeout` — 8번째 = CFP-1244 / ADR-070 Amendment 7 / ADR-052 Amendment 12) |

**verify-before-trust 5 sub-scope 무조건 적용**: substitution path 3-enum 어느 case 채택해도 Orchestrator verify-before-trust 5 sub-scope (file scope grep+quote / dir scope recursive grep+count / cross-repo gh api+commit SHA / grep count claim active vs historical 차원 / ADR §결정 번호 정확성, [ADR-081 §결정 D2](../docs/adr/ADR-081-codex-worker-prompt-boilerplate.md)) 무조건 적용. substitution = "Codex worker substitution" 이지 verify-before-trust 면제 아님.

**6 touchpoint × 3-enum cross-matrix**: 각 touchpoint 의 default + manual_substitution_declare trigger + fallback_skip_with_marker trigger = [ADR-052 Amendment 8](../docs/adr/ADR-052-codex-proactive-check-touchpoints.md) §A1 표 SSOT.

**narrative SSOT**: [`docs/domain-knowledge/domain/codex-collaboration/`](../docs/domain-knowledge/domain/codex-collaboration/) (ADR-052/070/081 cross-ref hub + substitution scope decision tree).

#### §3.10.1-bis Graceful degradation step pair (a)(b)(c) (CFP-963 / [ADR-081 Amendment 4](../docs/adr/ADR-081-codex-worker-prompt-boilerplate.md) §결정 D1.D body 확장 + [ADR-060 Amendment 14](../docs/adr/ADR-060-evidence-enforceable-promotion-framework.md) §결정 28 carrier)

ADR-081 Amendment 4 §결정 D1.D body 확장 (`sandbox_network_required: <bool>` → `network_scope: <4-tier enum>`: `offline` / `repo-fetch-only` / `web-fetch` / `offline_substitution_declared`) 이 codex worker spawn-prompt boilerplate 의 4-tier declaration 영역 codify. 본 sub-section = Codex CLI 미가용 / sandbox network-block 확정 / 8+ occurrence sentinel reentrant 위험 영역의 **graceful degradation step pair (a)(b)(c)** 명시 — fail-mode 8-enum 의 mechanical detection layer SSOT (신규 enum value 0, 기존 8-enum 재사용 — `api_missing` / `version_skew` / `enterprise_blocked` / `gh_api_network_blocked` / `manual_substitution_declared` / `inline_orchestrator_verify_only` / `subagent_recursion_blocked` / `dispatch_stall_or_stream_timeout`).

**step (a) — Codex spawn 직전 detect (fail-mode 8-enum membership)**:

Orchestrator 가 Codex worker spawn (Agent tool spawn / SendMessage to codex worker) **직전** 다음 3 detect probe 수행 — fail-mode 8-enum 의 spawn-time-detectable subset (api_missing / version_skew / enterprise_blocked) detection:

| Detect probe | mechanism | fail-mode binding |
|---|---|---|
| `codex --help 2>&1 \| grep -q -- '--allow-network'` 실패 | Codex CLI 자체 미가용 — codex@openai-codex plugin 미설치 / PATH 영역 외 | `api_missing` |
| `codex --version 2>&1` semver parse 실패 또는 minimum required version 미달 | Codex CLI version skew — `--allow-network` flag syntax 또는 `sandbox.network_access` config syntax 미지원 | `version_skew` |
| `gh api /rate_limit 2>&1` HTTP 403 (enterprise org policy gate) | enterprise org network egress 정책 차단 — codex CLI 자체는 가용하나 외부 HTTP 403 | `enterprise_blocked` |

3 detect probe 모두 PASS = step (b) inline_orchestrator_verify default path (substitution 비활성, 정상 Codex spawn). 1+ probe 실패 = step (b) `offline_substitution_declared` declare path 진입.

**step (b) — `network_scope: offline_substitution_declared` declare + verify-before-trust 5 sub-scope 全 적용**:

step (a) 1+ probe 실패 시 Orchestrator 는 다음 action:

1. **Codex worker spawn 자체 skip** — codex CLI 미가용 / sandbox network-block 영역, dispatch 자체 무의미.
2. **`network_scope: offline_substitution_declared` 4-tier enum value declare** — ADR-081 Amendment 4 §결정 D1.D body 정합 (boolean equivalent 부재 영역, strict ratchet-up). spawn-prompt body 가 사후 audit trail 용도로 declare 보유 (실제 spawn 미발생, declaration retain).
3. **Orchestrator inline 단독 substitution path 진입** — substitution path 3-enum `fallback_skip_with_marker` (ADR-052 Amendment 8 / ADR-070 Amendment 3 §결정 1 expansion 정합). Codex finding evidence ground truth 를 own working directory file Read / Glob / Grep 로 단독 verify (ADR-070 §결정 D1 무조건 적용).
4. **verify-before-trust 5 sub-scope 全 적용** — substitution = "Codex worker substitution" 이지 verify-before-trust 면제 아님 ([ADR-081 §결정 D2](../docs/adr/ADR-081-codex-worker-prompt-boilerplate.md) 5 sub-scope 무조건 적용):
   - D2.A file scope verify (single file 안 grep count)
   - D2.B dir scope verify (recursive grep)
   - D2.C cross-repo scope verify (gh api / git fetch origin — enterprise_blocked 영역은 본 sub-scope 자체 실패 가능, ADR-073 §결정 D1 정합 fallback)
   - D2.D grep count claim verify (active vs historical 차원)
   - D2.E ADR §결정 번호 정확성 verify

**step (c) — Story §10 marker + §14 `network_scope_actual` field**:

substitution path activation 시 Orchestrator 는 다음 audit trail 의무:

1. **Story §10 marker (1 회/spawn)**: `[codex-sandbox-fallback: <fail-mode>]` row append — fail-mode 8-enum 안 정확 1 value 보유 의무 (api_missing / version_skew / enterprise_blocked / gh_api_network_blocked / manual_substitution_declared / inline_orchestrator_verify_only / subagent_recursion_blocked / dispatch_stall_or_stream_timeout). fix-event-v1 contract 정합 (Orchestrator monopoly, CFP-32). `codex-network-scope-presence` lint (ADR-060 Amendment 14 §결정 28 / CFP-963 Phase 2 carrier) 가 marker enum 정합 membership check 검증.
2. **§14 Lane Evidence row 의 `network_scope_actual` field** (optional 13번째 field — evidence-check-registry-v1 v1.3 신규 schema, ADR-031 §14 12 field 영향 0 backward-compat): 본 lane row 의 actual scope (`offline_substitution_declared`) 기록. Codex dispatch 아닌 lane row = omit (omit-on-N/A pattern). present 시 4-tier enum 안 정확 1 value 보유 의무 (offline / repo-fetch-only / web-fetch / offline_substitution_declared). `codex-network-scope-presence` lint 가 §14 row 안 본 field membership check 검증.
3. **PMOAgent retro trigger 영역 carry-over** (선택): substitution 발화 누적 ≥3 occurrence within Story = ADR-045 §D-9 cross-Story pattern threshold reach 후보 (PMO retro carrier evaluation 영역).

**ratchet trigger (사용자/PMO escalation)**: 본 step pair (a)(b)(c) 의 `[codex-sandbox-fallback: <fail-mode>]` marker 누적 count 가 운영 중 ≥10 회 reach 시 ADR-052 Amendment 4 (touchpoint #2 mandatory) 의 codex CLI 가용 영역 가정 자체 재평가 후보. 본 정책 변경 = 별 follow-up CFP 의무 (ADR-064 §결정 1 scope unitary 정합).

#### §3.10.1-ter Graceful degradation step pair (a)(b)(c) — reactive variant (CFP-1003 / [ADR-052 Amendment 9](../docs/adr/ADR-052-codex-proactive-check-touchpoints.md) + [ADR-070 Amendment 5](../docs/adr/ADR-070-codex-verify-before-trust.md) + [ADR-081 Amendment 5](../docs/adr/ADR-081-codex-worker-prompt-boilerplate.md))

§3.10.1-bis = proactive 6 touchpoint scope 한정 (codeforge 강제 invariant). 본 sub-section = reactive `codex:rescue` 채널 (사용자 ad-hoc invocation, ADR-022 Deprecated default 영역, ADR-070 D1 L110 `사용자 책임 영역 (적용 외)`) 의 best-effort 가이드 anchor — codeforge 강제 미발효, 사용자 자율 선택 영역.

**적용 trigger**: 사용자가 직접 `codex:rescue` subagent 를 ad-hoc invoke 한 경우 (proactive 6 touchpoint 자동 dispatch 영역 아님, ADR-052 D1 L84/L90 분리 invariant 정합).

**best-effort 가이드 anchor (사용자 자율 선택, codeforge 강제 0)**:

| step | proactive 변형 (§3.10.1-bis) | reactive 변형 (본 sub-section) |
|---|---|---|
| **step (a) detect** | Orchestrator Codex spawn 직전 3 detect probe 의무 (codeforge 강제 invariant) | 사용자 ad-hoc invocation 직전 3 detect probe 권장 (사용자 자율 선택) — `codex --help / --version / gh api /rate_limit` 동일 mechanism |
| **step (b) declare + verify-before-trust 5 sub-scope** | Orchestrator `network_scope: offline_substitution_declared` declare + verify-before-trust 5 sub-scope 全 적용 (codeforge 강제) | 사용자 자율 선택 — ad-hoc invocation prompt 본문 안 `network_scope: <4-tier enum>` declare 권장 + ADR-070 verify-before-trust pattern 채택 권장 (codeforge 강제 0, ADR-081 Amendment 5 A2 SSOT) |
| **step (c) Story §10 marker + §14 `network_scope_actual` field** | Orchestrator audit trail 의무 (`[codex-sandbox-fallback: <fail-mode>]` row + `network_scope_actual` field) | reactive 변형 marker = `[codex-rescue-fallback: <fail-mode>]` 권장 (사용자 자율 선택, Wave 2 mechanical lint scope 확장 시 marker enum value codify 결정 영역) — 사용자 ad-hoc invocation 시 codeforge 강제 0 |

**mechanical lint scope 확장 (Wave 2)**: `codex-network-scope-presence` lint (evidence-checks-registry entry, ADR-060 Amendment 14 §결정 28 carrier) 의 mechanical detection scope = proactive 6 touchpoint spawn prompt 한정 (CFP-1003 / ADR-052 Amendment 9 + ADR-070 Amendment 5 + ADR-081 Amendment 5 — proactive/reactive disjoint codify). reactive 영역 mechanical lint 확장 = 별 CFP carrier 분리 (Wave 2, ADR-064 §결정 1 unitary 정합).

**사용자 책임 영역 invariant 보존**: 본 sub-section 의 4-anchor best-effort 가이드 = 사용자 ad-hoc invocation 시점에 anchor 채택 / 비채택 = 사용자 책임 영역. codeforge 측 강제 미발효 invariant retain (ADR-070 D1 L110 + ADR-022 Deprecated 정합). proactive 6 touchpoint scope 강제 invariant 와 disjoint axis.

#### §3.10.1 Pre-question Review (iterative reformulation — CFP-446 / [ADR-052 Amendment 2](../docs/adr/ADR-052-codex-proactive-check-touchpoints.md))

| 항목 | 내용 |
|---|---|
| 트리거 | `AskUserQuestion` 호출 직전 (항상, 전 레인). ADR-064 §결정 3 룰 5 정합 — `AskUserQuestion` 발화 자체 결정 (가치 판단 / 미공개 컨텍스트 2 종 한정) 통과 후 진입 |
| artifacts | 질문 초안 + 옵션 목록 (round 별도 갱신) |
| task | "아래 질문 초안을 검토해 (1) ambiguity / context-external 영역 = 표현 애매 또는 답 추론 정보 컨텍스트 부재 (2) verbosity 영역 = 핵심 결정 대비 장황. 2 기준 모두 통과 = `accept` / 1 종이라도 검출 = `reject` + reformulation 제안. reformulation 결과도 brevity 준수 의무" |
| 출력 적용 (iterative) | Codex `accept` → 그대로 `AskUserQuestion` 발화 / Codex `reject` → reformulation 반영 후 다음 round dispatch / 최대 3 rounds / fall-through 시 round 3 reformulation 그대로 `AskUserQuestion` 발화 |

**Round 흐름 (max 3 + fall-through)**:

```
Round 1: Codex dispatch (질문 초안 v1)
  ├─ accept → AskUserQuestion(v1) [early termination]
  └─ reject → reformulation v2
       ↓
Round 2: Codex dispatch (질문 초안 v2)
  ├─ accept → AskUserQuestion(v2)
  └─ reject → reformulation v3
       ↓
Round 3: Codex dispatch (질문 초안 v3)
  ├─ accept → AskUserQuestion(v3)
  └─ reject (fall-through) → AskUserQuestion(v3) [그대로]
```

사용자 발화 directive verbatim (CFP-446 §1 — Story file SSOT): "이 리뷰는 최대 3회 반복할 수 있고 3회를 채우면 그냥 사용자에게 질문하라" — fall-through 정책 SSOT.

**Codex reject 기준 (2 종)**:

| 기준 | 운영적 정의 |
|---|---|
| `ambiguity` / `context-external` | 질문 표현 애매 또는 답 추론 정보 컨텍스트 부재 (사용자가 답할 수 없는 질문) |
| `verbosity` | 질문 본문이 핵심 결정 영역 대비 장황 — 사용자 발화 directive: "질문의 내용이 길수록 좋지 않은 질문" |

**Brevity 행동 규범 (질문자 + 리뷰어)**:

- **질문자 (Orchestrator)** — 질문 초안 작성 시 1 문장 단위 + numbered list (max 3 항목). 컨텍스트 길이 < 핵심 질문 길이 비율 유지. ADR-064 §결정 3 룰 4 정합
- **리뷰어 (Codex)** — `verbosity` reject 시 reformulation 결과도 brevity 준수 의무. round N+1 입력이 round N 보다 길어지면 Orchestrator 가 reformulation 거부 후 round N+1 skip → fall-through 조기 진입 가능 (자기모순 차단)

**debate-protocol-v1 미사용 결정 (ADR-052 Amendment 2 A5)**:

본 iterative reformulation 은 `debate-protocol-v1` (§3.13) 의 multi-round adversarial debate 와 영역 분리. 본 영역은 단일 agent (Codex) self-iteration 으로 충분 — role_lock / anti-sycophancy / anchor 재발 / transcript Story §9 영속화 모두 불필요. 사용자 발화 directive ("Codex 에 리뷰 요청 … 다시 재구성하여 리뷰") 가 self-iteration 패턴 정합.

| 영역 | debate-protocol-v1 (ADR-059) | §3.10.1 iterative reformulation |
|---|---|---|
| 참여자 | 2 agent adversarial | 1 agent (Codex) self-iteration |
| Trigger | finding severity / recommendation divergence | Codex reject (ambiguity / verbosity) |
| Round 영속화 | Story §9 transcript 의무 | Orchestrator turn 내 transient (영속화 불필요) |
| FIX 흐름 | §10 ledger + reasoning carryover | N/A — verdict producer 영역 외 |

#### §3.10.2 Design Synthesis Check (**mandatory** — CFP-532 / [ADR-052 Amendment 4](../docs/adr/ADR-052-codex-proactive-check-touchpoints.md))

| 항목 | 내용 |
|---|---|
| 트리거 | ArchitectAgent Change Plan §3 초안 완료 → ArchitectPLAgent 전달 직전 (항상) |
| **mandatory: true** | **Orchestrator 가 dispatch 결과 P0 + P1 finding 모두 inline FIX 의무 (skip 영역 차단). P2-only 만 Orchestrator 판단으로 Story §10 deferred 기록 가능. 6 sample success rate 100% sentinel: CFP-426 + CFP-427 + CFP-428 + CFP-429 + 2 carry-over Story — 모든 review lane FIX 회피 evidence** |
| artifacts | §3 Change Plan 초안 + 6 SubAgent 산출물 요약 |
| task | "6 SubAgent 산출물이 §3에 균형 있게 반영됐는지 검증. 모순·누락·순환 논리 포착" |
| 출력 적용 | ADDRESS_FIRST 시 ArchitectAgent §3 수정 후 재전달 (P0 + P1 inline FIX 의무, P2-only deferred 가능) |

#### §3.10.3 Development Rescue

| 항목 | 내용 |
|---|---|
| 트리거 | DeveloperPLAgent FIX 2+ 반복 동일 이슈 감지 시 |
| artifacts | 구현 블로커 설명 + 관련 코드/로그 |
| task | "구현 블로커를 독립적으로 진단하고 root cause 및 해결 경로를 제시" |
| 출력 적용 | DeveloperPLAgent 진단 결과 적용 |

#### §3.10.4 Requirements Output Review (multi-round debate 격상 — CFP-411 / ADR-052 Amendment 1)

| 항목 | 내용 |
|---|---|
| 트리거 | RequirementsPLAgent §1-§6 통합 완료 → `phase:설계` 진입 직전 (항상) |
| artifacts | Story §1-§6 전체 내용 |
| task | "§1-§6 요구사항 완전성 검증. 테스트 불가능한 AC, 누락 엣지케이스, 모호한 표현, 상충 요구사항 포착" |
| 출력 적용 (default 흐름) | Codex `recommendation = PROCEED` 또는 RequirementsPL 의미 비교 결과 divergence 없음 → 그대로 `phase:설계` 진입 |
| 출력 적용 (divergence 흐름 — Amendment 1) | RequirementsPL 이 Codex `{findings, recommendation, rationale}` vs 자기 synthesis (§2/§5/§6) 의 의미적 차이 (AC / Edge Case / why 해석) 검출 시 `debate-protocol-v1` (§3.13) 자동 발동. lane-agnostic 패턴 정합. 합의 시 §5/§6 보강 후 `phase:설계` 진입, max 5 미합의 시 사용자 escalation, FIX verdict 시 **RequirementsPL 자체 재spawn** (transcript 입력 — ArchitectAgent 미관여) |

**Divergence detection (Requirements lane — semantic, structured surface 부재)**:

```
PL LLM judgment:
  - compare(codex_findings vs §2/§5/§6 self-synthesis)
  - criteria: ac_semantic_diff | edge_case_semantic_diff | why_interpretation_diff
  - anchor_id assignment: §<section-ref> (review-verdict-v4 패턴 재사용)
    예: §5-AC-3, §5.2-EC-2, §2-bound-1, §6-source-2
  - 모호 시 가장 광범위한 anchor 채택 (debate 진입 결정 우선)
```

DesignReview lane (review-verdict-v4 `findings[]` structured 비교) 과 달리 Requirements lane 은 PL LLM 의미 판정 위임. false positive 차단 = `codeforge-requirements/agents/RequirementsPLAgent.md` sibling sync 의 prompt engineering 영역 (ADR-010 follow-up).

**FIX 흐름 redo 대상 분기 (ADR-052 Amendment 1 A4)**:

- DesignReview lane debate FIX → ArchitectAgent re-run (§3.13 정합, ADR-059 §결정 3)
- Requirements lane debate FIX → **RequirementsPL 자체 redo** (§2/§5/§6 재합성). ArchitectAgent 미관여 — lane scope 분리. transcript verbatim 주입.

#### §3.10.5 FIX Root Cause 2nd Opinion

| 항목 | 내용 |
|---|---|
| 트리거 | ArchitectPLAgent "설계 vs 구현" root cause 판정 완료 직후 (항상) |
| artifacts | 판정 결과 + evidence pack (Change Plan 버전 + 리뷰 findings + 테스트 로그) |
| task | "root cause 판정에 독립적 2nd opinion 제시. 동의/불동의 + 근거" |
| 출력 적용 | 동의 → 기존 판정 진행 / 불동의 → **사용자 에스컬레이션** (최종 판정 사용자) |

#### §3.10.6 ADR Draft Review

| 항목 | 내용 |
|---|---|
| 트리거 | ArchitectAgent ADR 초안 완료 직후 (항상) |
| artifacts | ADR 초안 전체 |
| task | "ADR 결정 논거 검토. 순환 논리, 약한 근거, 대안 미검토, §결정 ↔ §컨텍스트 불일치 포착" |
| 출력 적용 | ADDRESS_FIRST 시 ArchitectAgent ADR 수정 후 설계리뷰 진입 |

> **ADR-082 cross-ref (CFP-776)**: Codex proactive check 의 finding evidence 신뢰는 외부 worker output verify layer (ADR-070). lane agent 가 §9 evidence / corpus enumeration write 시점 source/value verify 누락은 별 disjoint layer ([ADR-082 §결정 2](../docs/adr/ADR-082-write-time-self-write-verification-mandate.md)) — Codex proactive check 와 verify 대상 disjoint (Codex output ↔ lane self-write write-time).

---

### §3.13 Multi-round Adversarial Debate (debate-protocol-v1, CFP-391 / [ADR-059](../docs/adr/ADR-059-debate-protocol-v1.md))

debate-protocol-v1 = lane-agnostic registry (ADR-059 §결정 5). 현재 두 lane 에 적용:

| Lane | Story | Divergence surface | Divergence 판정자 | FIX redo 대상 |
|---|---|---|---|---|
| DesignReview | CFP-391 (deployed) | review-verdict-v4 `findings[]` 동일 `anchor_id` 의 severity OR recommendation | DesignReviewPL structured 검사 | ArchitectAgent re-run (ADR-059 §결정 3) |
| Requirements | CFP-411 (ADR-052 Amendment 1) | RequirementsPL synthesis (§2/§5/§6) vs Codex proactive check 의미 차이 | RequirementsPL LLM 의미 판정 | **RequirementsPL 자체 redo** (§2/§5/§6 재합성) |

DesignReview lane 에서 Claude worker 와 Codex worker 가 review-verdict-v4 finding 불일치를 산출했을 때 Orchestrator (또는 DesignReviewPL via Orchestrator self-write delegate) 가 `debate-protocol-v1` 을 자동 발동한다. Requirements lane 에서 RequirementsPL 이 Codex proactive check 결과와 자기 synthesis 의 semantic divergence 를 검출할 때 동일 protocol 발동 (touchpoint #4, ADR-052 Amendment 1). 본 protocol = ADR-022 deprecation (CFP-134) 이후 ad-hoc Codex review 자동 발동 무효 정책과 정합 — 자동 발동은 debate 한정 (사용자 explicit Codex request 시 활성된 워커들 사이의 divergence 해소).

#### Trigger surface (divergence detection)

DesignReviewPLAgent 가 review-verdict-v4 packet 합성 직전 surface 검사:

```
for anchor_id in union(claude_findings.anchor_id, codex_findings.anchor_id):
    claude_f = claude_findings.get(anchor_id)
    codex_f  = codex_findings.get(anchor_id)
    if claude_f and not codex_f:
        divergence = "recommendation"  # 한쪽 FIX, 다른쪽 silent = PASS
    elif claude_f.severity != codex_f.severity:
        divergence = "severity"
    elif claude_f.recommendation != codex_f.recommendation:
        divergence = "recommendation"
    else:
        divergence = None  # 합의 — debate 미발동
    if divergence:
        debate_triggers.append({anchor_id, anchor_text, claude_pos, codex_pos, divergence_type: divergence})
```

debate_triggers 비어있지 않으면 각 trigger 별로 debate 발동 (multi-anchor 동시 debate 가능 — anchor 별도 독립 라운드 카운터).

#### Round 실행 흐름 (사이클 1회)

| 단계 | 책임자 | 행위 |
|---|---|---|
| Round 0 init | DesignReviewPL | `anchor_text` + 양측 initial position 추출. role_lock 명시. system_prompt_appendix 주입 |
| Round 1 ~ N | Claude / Codex worker | role-lock 유지 prompt + `anchor` 입력 최상단 강제 prepend + transcript carryover. `remaining_disagreements` + `position_change` flag 출력 |
| Round N 종료 판정 | DesignReviewPL | `remaining_disagreements` 검사 + `position_change` reason 검증 + LLM 합의 판정 |
| min 3 미달 합의 | DesignReviewPL | `force_continue` + adversarial prompt 재주입 — 가짜 합의 검증 (EC-2) |
| max 5 미합의 | Orchestrator | `AskUserQuestion` packet 발화 (escalation_packet schema 정합) — 사용자 dialog 응답이 최종 verdict |
| anchor 재발 검출 | DesignReviewPL | Story §9 scan → `anchor_recurrence_count >= 2` 시 debate 진입 없이 즉시 사용자 escalation |

#### Anti-sycophancy 강제 directive (매 라운드 system prompt 주입)

> "당신의 Round 0 입장을 유지하라. 상대 주장의 근거가 결정적일 때만 입장 변경 허용. 입장 변경 시 출력에 `position_change: true` + `position_change_reason` 명시 의무. `remaining_disagreements` 미해결 쟁점을 빠짐없이 나열하라. 비어 있으면 가짜 합의로 간주된다."

#### Transcript 영속화 (Story §9 inline append)

- 위치: codeforge family Story = `<internal-docs-clone>/<plugin-folder>/stories/<KEY>.md §9`. Consumer Story = `docs/stories/<KEY>.md §9`
- Section header format: `### Debate transcript: <anchor_id>`
- Schema: debate-protocol-v1 registry 정의 준수 (trigger / rounds[] / termination)
- Writer: DesignReviewPL via Orchestrator self-write delegate (ADR-039 Amendment 정합)

#### FIX verdict 처리 (reasoning carryover)

```
debate_verdict == FIX
  ↓
transcript Story §9 append (### Debate transcript: <anchor_id>)
  ↓
§10 FIX Ledger row append (Orchestrator self-write)
  ├─ debate_artifact_ref = #debate-transcript-<anchor_id>
  └─ fix-event-v1 1.1 contract (CFP-391 MINOR bump)
  ↓
[lane 분기]
  ├─ DesignReview lane → ArchitectPLAgent re-spawn
  │   ├─ prompt 에 debate transcript verbatim 주입 (요약 금지)
  │   └─ ArchitectAgent re-run instruction:
  │      "양측 입장의 reasoning trail 을 반영해 redesign 하라"
  │   ↓
  │   DesignReview re-entry (FIX-N+1, 카운터 정합)
  │
  └─ Requirements lane (CFP-411 / ADR-052 Amendment 1 A4) → RequirementsPLAgent 자체 re-spawn
      ├─ prompt 에 debate transcript verbatim 주입 (요약 금지)
      ├─ ArchitectAgent 미관여 (lane scope 분리)
      └─ re-run instruction:
         "transcript 의 양측 입장을 반영해 §2/§5/§6 재합성하라.
          AC / Edge Case / why 해석 영역의 미해결 disagreement 모두 검토."
      ↓
      Requirements re-synthesis → §1~§6 재완료 → touchpoint #4 재발화 (FIX-N+1)
```

#### env=0 / env=1 동작 차이

| 환경 | Round dispatch | 토큰 비용 |
|---|---|---|
| `env=1` (agent teams 활성) | `SendMessage(to=worker, body=round_N_input)` continuous dialog | round 간 cache 가능 (5 min TTL) |
| `env=0` (default subagent context) | Orchestrator round-trip polyfill — 매 라운드 Claude worker / Codex worker 각각 `Agent` tool one-shot spawn (transcript 누적 입력 첨부). 라운드 카운터 PL 자체 관리 | 매 라운드 cold start (cache 미적용) — 비용 증가 |

양쪽 동일 protocol schema 준수. env=0 fallback 시 토큰 비용 증가는 사용자 인식 의무 (consumer-guide §1f).

#### Token budget cap (operational risk 완화)

매 라운드 worker 출력 권고 cap (PL 이 enforce):

- `statement`: <= 2000 token
- `rationale`: <= 3000 token
- 총 ~5000 token / round / worker
- 5 라운드 × 2 worker × 5K = 50K token (Opus PL 200K context 한도 내 안전)

초과 시 PL 이 worker 에게 condensation 요청 (1회 한정) 후 invalid 처리. max 5 라운드 cap = 비용 폭증 차단 forcing function.

#### Wave 4 — DesignLane blanket trigger (CFP-582 / [ADR-059 Amendment 2](../docs/adr/ADR-059-debate-protocol-v1.md))

cross-module Story 의 ArchitectAgent 산출물 (Change Plan §3 / ADR / Story §3/§7/§11) 에 대한 blanket Codex worker 검증 — divergence 발생 시 다시 multi-round debate 흐름 진입. dispatch_mode `blanket_cross_module_designlane` 자동 활성 조건 + 6 step 진입 절차:

1. **touched_top_level_paths 산정**: Story §1 spec_links + Change Plan §2 영향 영역 union 의 top-level path (예: `src/foo/` / `docs/` / `templates/`). 중복 dedup 후 distinct count.
2. **touched_lanes 산정**: 같은 union 에서 codeforge lane plugin folder mapping (codeforge-{requirements,design,develop,review,pmo,test}) 의 distinct lane count.
3. **판정**: `touched_top_level_paths >= 2` OR `touched_lanes >= 2` 시 dispatch_mode = `blanket_cross_module_designlane` 활성 (단일 module Story 는 활성 안 함, 기존 `auto_on_divergence` 분기 유지).
4. **spawn prompt 갱신**: ArchitectPLAgent 가 Codex worker spawn 시 prompt `artifacts` 필드에 Change Plan §3 + 신규 ADR draft + Story §3/§7/§11 mirroring content verbatim 첨부 (ADR-070 verify-before-trust 정합).
5. **§14 row append**: Lane Evidence 에 spawn 직전 row 추가 (`dispatch_mode=blanket_cross_module_designlane`, `touched_top_level_paths=N`, `touched_lanes=M`). end column = Codex return 시 outcome (`agreement_reached` / `divergence_detected` / `escalated`).
6. **verdict 처리**: agreement 시 정상 PASS (FIX 없음). divergence detected 시 다시 §3.13 multi-round debate 진입 (`auto_on_divergence` flow + `convergence_quality_invariant` 3 marker 의무). PL verdict 작성 시 `prior_codex_findings[]` (Touchpoint #2 carry-over, §결정 9) 가 transcript Round 0 input 으로 verbatim 첨부.

**non-blanket 케이스**: `touched_top_level_paths < 2` AND `touched_lanes < 2` (single-module Story) — Wave 4 trigger 미활성, 기존 `auto_on_divergence` (Codex single-shot vs Claude finding 비교) flow 유지. dispatch_mode 4-value enum precedence `auto_on_divergence > blanket_cross_module_designlane > mechanical_fast_path_inline > user_request_only` 정합.

**EC-1 (Codex 미가용 fallback)**: codex CLI 미설치 / authentication fail / network unavailable 시 ArchitectPLAgent 가 blanket trigger skip + Story §10 row append (`reason: "codex unavailable - blanket trigger skipped"`). 사용자 통지 후 정상 PASS 진행 — DesignReviewPL lane (CFP-391 기존 flow) 가 후속 검증 channel.

#### lane-agnostic 적용

본 §3.13 = DesignReview lane scope (Story 1 / CFP-391). Story 2 (Requirements lane — CFP-392) 진입 시 동일 protocol contract 재사용 + lane-specific `semantic` divergence_type 정의 (ADR-052 touchpoint #4 격상 Amendment 와 동행). CodeReview / SecurityTest lane 은 deferred CFP-C scope.

---

### §3.14 Orchestrator-user dialog convergence (CFP-612 / [ADR-071](../docs/adr/ADR-071-orchestrator-user-dialog-convergence.md))

debate-protocol-v1 (§3.13) = **agent ↔ agent** debate domain. 본 §3.14 = **Orchestrator ↔ user** dialog domain. 두 sub-section 은 "수렴 dialog 가 본질" 1 점 conceptual common ground 만 공유 — schema 재사용 금지 (§3.13 의 3 marker pattern 은 debate transcript verification, §3.14 는 turn-by-turn cognitive frame). 본 §3.14 는 매 user-facing turn 의 Orchestrator 행동 본문 SSOT.

> **본질 anchor**: Orchestrator 가 사용자와 대화할 때, mechanical rule 추종이 아니라 진짜 수렴 대화에 참여하도록 codeforge SSOT 를 영구적으로 바꾸는 변화. 본 anchor 가 충족되지 않으면 아래 mechanism 을 몇 개 쌓든 의미 없다 — 모든 mechanism 은 본질을 보조하는 scaffolding (가설 E 의 mechanical 규칙 자체 한계 trap 회피 forcing function).

> **ADR-082 cross-ref (CFP-776)**: 본 §3.14 = Orchestrator ↔ user 대화 표현 layer. lane agent §9 evidence / corpus enumeration write-time source/value verify 는 별 disjoint layer ([ADR-082 §결정 1](../docs/adr/ADR-082-write-time-self-write-verification-mandate.md) 4-layer 표) — 사실 verify layer ↔ 대화 표현 layer 분리 (ADR-073 ↔ ADR-071 분리 패턴과 동형). schema 재사용 금지.

#### 호출 시점 + skill 호출

매 user-facing turn 직전 (= [ADR-039](../docs/adr/ADR-039-orchestrator-subagent-default-for-codeforge-modification-work.md) inline whitelist 1번 entry = 사용자 dialog turn) Orchestrator 가 `codeforge:user-dialog-mode` skill 호출 — frame mode 진입 4 step + 4 layer 검증 + sub-mechanism 2 종 lookup. skill SSOT mirror 만, 본 §3.14 = 본문 SSOT.

#### frame mode 진입 4 step (ADR-071 §결정 1)

| step | 행위 | self-check |
|---|---|---|
| 1 | codeforge 내부 어휘 "내부 메모" 분류 격리 | 사용자 발화 본문에 ADR-NNN / CFP-NNN / lane plugin name / hook name / inter-plugin contract name 직접 등장 안 함 (식별자 인용 시 사전 요약 의무, [ADR-064 §결정 3 룰 3](../docs/adr/ADR-064-decision-principle-mandate.md) 정합) |
| 2 | 사용자 지금까지 무엇 알고 있는지 정리 | 사용자 mental model 추정 — 이전 turn 발화 기준 + 미공개 컨텍스트 분리 |
| 3 | 사용자 이 turn 무엇 답·결정해야 하는지 한 문장 | turn 의 사용자 action item 이 1 문장으로 명확. 한 문장 안 되면 step 미완 (메시지 발화 차단) |
| 4 | 위 셋 바탕으로 메시지 작성 | step 1+2+3 통합 위에 본문 작성 |

**frame mode marker 형식 (visible vs hidden cognitive layer)**: 본 §3.14 derived default = **hidden cognitive layer** (Orchestrator 자체 thinking 단계 — 사용자 visible 영역 marker 미발화). Layer 1 가시적 preamble 이 visible signal 충당. visible cognitive marker 추가 (예: "[frame mode 진입]" 사용자 prefix) 가 필요한 영역은 별도 follow-up CFP.

#### frame mode 안 세부 룰 3 종 (ADR-071 §결정 2)

**(a) 메시지 직전 self-check 3 문항** — 사용자가 답해야 할 것이 한 문장으로 명확한가 / 비-codeforge 맥락 사람이 이해 가능한가 / 답하는 데 필요한 배경 (왜 / trade-off / 걸려있는 것) 충분한가. 3 문항 모두 PASS 후 발화.

**(b) 사실/가치 분리** — 사실 → derived default 적용. 가치 → `AskUserQuestion` 발화. 모호 → 가치 측 (safe direction). [§결정 5 결정 트리 참조](../docs/adr/ADR-071-orchestrator-user-dialog-convergence.md).

**(c) sub-agent 결과 평이 번역** — raw packet 노출 금지, codeforge 내부 용어 평이한 한글, **3 줄 제약 거부** (길이 자유), "왜 / trade-off / 걸려있는 것" 배경 포함, 원본 packet 은 사용자 요청 시 별도.

#### 4 layer 검증 (ADR-071 §결정 3)

| Layer | 동작 | 위치 / 발화 시점 | trivial turn 면제 |
|---|---|---|:-:|
| **Layer 1 — 가시적 preamble** | 메시지 맨 위 "지금 답해주실 것" 1 문장 가시 | 매 user-facing turn 맨 윗줄 | ✅ (응답 ≤ 1 줄 + 의문/결정 부재 시) |
| **Layer 2 — 자기 declare** | turn 끝 "주의한 가설" 1 줄 declare (보조 신호) | 매 turn 맨 아랫줄 | ✅ |
| **Layer 3 — keyword "추상" 즉시 halt** | 사용자 메시지 본문 "추상" 한글 token 등장 시 immediate halt + 재작성 | 사용자 token detection 시점 | ❌ (trivial turn 에서도 active) |
| **Layer 4 — 누적 detection** | N=1 즉시 halt (같은 양상 다음 turn 재발) / M=5 max threshold `AskUserQuestion` escalation | 매 turn 끝 incident 검사 | ❌ |

**Layer 3 stem vs exact match 결정** (E2 — 본 §3.14 결정 영역): derived default = **stem match** (substring "추상" 등장 모두 trigger — "추상" / "추상적" / "추상화" 등). false positive risk (예: 도메인 어휘 "추상 미술") 인지 + 사용자 explicit override 시 incident row append 후 dialog 재개. **Hanja form "抽象" 면제** + **영문 alias ("abstract") = trigger 아님** (한글 token 만 anchor).

**Layer 4 file rotate / archive 정책** (E3 — 본 §3.14 결정 영역): derived default = **no auto reset** + **manual archive only** (사용자 explicit reset request 시 archive). yearly file rotate vs 별도 row delineator marker 선택은 첫 archive 시점 사용자 결정 영역.

**trivial turn 정의 3 criteria AND** (E12 — 본 §3.14 결정 영역): (1) 응답 ≤ 1 줄 + (2) 의문 부재 + (3) 결정 부재. 3 criteria 모두 충족 시 Layer 1 + Layer 2 면제. Layer 3 / Layer 4 는 trivial turn 에서도 active.

**Turn-shape derived defaults** (E9 / E10 / E11 — 본 §3.14 결정 영역, Story §5.3 turn-shape edge 4 종 중 E12 제외 3 종. Codex Proactive Check #2 FIX-1 carrier):

| Edge | 정의 | Layer 1 (preamble) | Layer 2 (declare) | Layer 3 ("추상" halt) | Layer 4 (누적 detection) |
|---|---|---|---|---|---|
| **E9 streaming token** | Orchestrator 가 token stream 단계로 응답 (incremental flush) | **final flush 시 적용** — incremental token stream 단계는 preamble 의미 없음, 사용자 시점 = 1 turn 완료 (final flush) | final flush 시 적용 | active (streaming 중 사용자 추가 input 가능) | active (turn 끝 incident 검사) |
| **E10 tool-call-only** | 사용자 화면에 prose 없는 turn (순수 file read / Bash 단발 호출 / mcp__* call 만) | **면제** (no user-facing prose = preamble 의미 없음) | **면제** | active | active (단 incident 영역은 prose turn 만 — tool-call-only turn 자체는 incident 분류 외) |
| **E11 AskUserQuestion popup** | `AskUserQuestion` structured popup 발화 turn | **preamble = "AskUserQuestion 으로 답해주실 것:" 1 문장** (popup 이 본 발화의 결정 영역 cover — preamble 은 popup 진입 시그널만, popup 본문 verbatim 인용 불요) | popup 본문이 declare 충당 — separate Layer 2 줄 면제 | active (popup option_text 안 "추상" 등장 가능) | active |
| **E12 trivial answer** | 응답 ≤ 1 줄 + 의문 부재 + 결정 부재 (3 criteria AND) | **면제** (trivial turn 자체가 preamble cognitive overhead 정당화 불가) | **면제** | active (1 줄 안 "추상" 등장 시 trigger) | active (trivial turn 도 pattern_dimension 분류 영역) |

E10 tool-call-only 의 정량 정의 = **(a) 사용자 화면 prose 0 줄 + (b) cosmetic 1-줄 미만 (예: "잠시만요" / 빈 status report)**. (a) AND (b) 충족 시 tool-call-only 분류 — 정의 외 turn = E9 streaming 또는 일반 turn (Layer 1+2 적용).

[empirical-source: derived default (analytical reasoning from Claude Code turn-shape model, no external corpus yet, frustration evidence carrier = CFP-612 §1 사용자 directive verbatim). circular self-citation 인정 + 후속 corpus 누적 후 ratchet 강화 영역 — [ADR-068 Amendment 1](../docs/adr/ADR-068-boundary-completeness-invariants.md) I-5 정합 (cognitive layer 영역의 derived default 첫 empirical annotation 사례).]

E11 popup turn 의 Layer 2 면제 사유 = popup 본문 자체가 declare semantic 충당 — preamble + popup option_text + popup body = 3 channel 의 user-facing signal 이미 충분, Layer 2 추가 시 cognitive redundancy.

#### Sub-mechanism 2 종 (수렴 보장, ADR-071 §결정 4)

**Sub-mechanism 1** — 매 halt 후 (Layer 3 / Layer 4 N=1) 재작성 메시지 맨 아랫줄 (Layer 2 declare 와 별도 줄) 에 `이전과 다르게 한 점:` prefix + 1 줄 본문. 단순 표현 다듬기 (어휘 변경 / 문장 길이 압축) 가 아닌 **차원 전환** 의무.

**Sub-mechanism 2** — 같은 양상 재발 시 (Layer 4 file row count ≥ 2) 단순 표현 다듬기 금지. **4 차원 enum** 중 다른 차원 강제 전환:

| 차원 | 의미 | 전환 예시 |
|---|---|---|
| **표현** | 어휘 / 문장 길이 / 구조 | "ADR-064 §결정 3" → "결정 제시 5 룰" |
| **결정 구조** | 옵션 제시 방식 / derived default / AskUserQuestion 형식 | numbered list → 권장 1 + 대안 1 |
| **보고 형식** | sub-agent 결과 표시 / 평이 번역 / 길이 | raw JSON → 평이 한글 (3 줄 제약 거부) |
| **질문 자체** | 어떤 결정을 사용자에게 묻는지 자체 변경 | "방향 X / Y 중 어느 것" → "본 결정의 user value 우선순위는?" |

#### Layer 4 영속 file (ADR-071 §결정 6)

- **path**: `docs/orchestrator-communication-incidents.md` (wrapper repo). consumer 측은 자기 repo 의 동일 path 별도 lifecycle.
- **owner**: Orchestrator 단독 monopoly (FIX Ledger / Git Ops Log / ADR-RESERVATION 패턴 정합 — wrapper repo 안 4번째 cross-Story append-only file 패턴).
- **lifecycle**: append-only, cross-Story 영속 (Story 종료 시 reset 없음), M=5 lifetime counter, manual reset only.
- **schema**: 8-column (iter / timestamp / story_key / pattern_dimension / pattern_summary / trigger / different_dimension_after_halt / escalation_outcome). [ADR-071 §결정 6](../docs/adr/ADR-071-orchestrator-user-dialog-convergence.md) verbatim.
- **사용자 escalation 후 다음 incident**: pattern_dimension 강제 전환 (sub-mechanism 2 정합).

#### 사실/가치 판단 결정 트리 (ADR-071 §결정 5)

```
결정 후보 발화 직전:
  is_factual?
    YES → derived default 적용 (컨텍스트로 추론 가능 시)
                   ↓
                  declare default + 결과 보고 + 사용자 정정 의무
    NO (가치 판단 영역) → AskUserQuestion 발화 의무
    AMBIGUOUS → 가치 측 분류 (safe direction)
                   ↓
                  AskUserQuestion 발화 의무
```

**사실 예시**: 파일 존재 / `wc -l` 결과 / `git log` 출력 / SHA / `grep` 결과
**가치 예시**: 사용자 선호 (UX / 보고 길이) / 정책 강화 방향 / scope 결정 / brainstorm 채택안
**모호 예시**: derived default 추론 가능 + future 작업 영향 큼 → 가치 측 (사용자 확인 후 진행)

#### 3 memory entry normative 승격 mapping (ADR-071 §결정 8)

| memory entry | 정책 위치 SSOT 이전 | unchanged scope |
|---|---|---|
| `feedback_explain_before_ask` | 본 §3.14 frame 본문 + ADR-071 §결정 1 step 4 + §결정 4 sub-mechanism 1 | — |
| `feedback_question_quality` | 본 §3.14 frame 본문 + ADR-071 §결정 2 (b) + §결정 5 결정 트리 | — |
| `feedback_subagent_driven_auto_select` | **변경 없음** — §3.0.5 기존 정책 유지 | codeforge wrapper side SSOT 변경 0 (사용자 personal memory side entry 자체 영향 없음 — 사용자 영역, codeforge wrapper scope 외) |

**승격 시점**: 본 Story (CFP-612) Phase 2 PR merge 시점. PMOAgent retro ([ADR-045](../docs/adr/ADR-045-story-retro-mandatory-trigger.md) mandate) 의제로 사용자 personal memory entry 삭제 제안 (사용자 결정 영역).

#### CFP-582 conceptual cross-ref (schema fit 부적합 — ADR-071 §결정 9)

[§3.13 debate-protocol-v1](../docs/adr/ADR-059-debate-protocol-v1.md) Amendment 2 (CFP-582) 의 3 marker pattern (`counterargument_present` / `alternative_proposed` / `debate_purpose_statement_present`) = **debate transcript verification schema** (multi-round adversarial debate 의 convergence_quality_invariant 검증용).

본 §3.14 = **turn-by-turn Orchestrator-user dialog** (single-turn cognitive frame + cross-Story 누적 detection). 두 sub-section 의 schema 직접 mapping **부적합**. 본 §3.14 의 frame mode + 4 layer + sub-mechanism 어느 항목도 §3.13 의 3 marker schema 를 import 하지 않는다. CFP-582 의 본질 (수렴 dialog) 만 conceptual cross-ref. **schema 재사용 절대 금지**.

#### env=0 / env=1 동작 동일

`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` env 무관 — 본 §3.14 = Orchestrator (top-level Claude 세션) 의 cognitive frame, agent teams platform capability 와 무관. env=0 default subagent context / env=1 agent teams enabled context 모두 동일 행동.

#### scope 외 (ADR-071 §결정 10)

- **Layer 1 preamble mechanical lint** — 별도 follow-up CFP (Wave 5 = cognitive + persistence layer 만, lint 별도 CFP 분리)
- **agent ↔ agent debate** (§3.13 cover 완료)
- **코드 품질 / 보안 / 성능**
- **사용자 personal memory entry 자체 삭제** (사용자 영역 — codeforge wrapper scope 외)
- **consumer overlay 영역 customization** (overlay 가 정책 축소 불허)
- **debate-protocol-v1 3 marker import** (schema 직접 채택 절대 금지)
- **frame mode marker visible vs hidden** = 본 §3.14 derived default hidden cognitive layer, visible 추가 = 별도 CFP
- **Layer 3 false positive 처리 advanced policy** = 첫 incident 시점 사용자 결정 영역
- **Layer 4 file rotate / archive 자동화** = 별도 CFP

#### DialogFidelityAgent verifier auxiliary (ADR-071 Amendment 1 / CFP-777, Amendment 2 / CFP-818)

DialogFidelityAgent = codeforge-pmo **cross-cutting read-only verifier** (additive auxiliary, **5번째 cognitive layer 신설 금지** — Layer 1-4 enum 보존 invariant, ADR-071 §결정 12).

**Spawn trigger 3-anchor** (ADR-039 §결정 2 inline whitelist 보존, 자동 hook 부재 → Orchestrator 자율 채택):
- `post_user_turn`: 사용자 turn 응답 직후 (Layer 3 "추상" detect / numbered list 발화 / AskUserQuestion 직전)
- `pre_architectpl_synthesis`: ArchitectPL synthesis 완료 직전 (Codex TP#2 augment)
- `pre_fix_rootcause`: FIX 루프 root cause 판정 직전 (Codex TP#3 augment)

**3-anchor 발화 형태 매핑 표 (ADR-071 §결정 13.2, CFP-818)**: 각 anchor 가 어떤 turn shape 직전 활성하는지 + Codex touchpoint dedup:

| anchor | 발동 시점 | 발화 형태 매핑 (UC) | Codex touchpoint dedup |
|---|---|---|---|
| `post_user_turn` | 사용자 turn 응답 직후 (Layer 3 "추상" detect / numbered list 발화 / `AskUserQuestion` 직전) | UC-1 (`AskUserQuestion` 발화 직전) / UC-2 (numbered list 또는 dialog format 발화 직전) / Layer 3 "추상" stem detect 직후 | 없음 (Codex 6 touchpoint 와 disjoint) |
| `pre_architectpl_synthesis` | ArchitectPL synthesis 완료 직전 (사용자 보고 발화 직전) | UC-3 (Orchestrator 가 ArchitectPL synthesis 결과 사용자 보고 발화 직전) | **Codex TP#2 (mandatory, [ADR-052](../docs/adr/ADR-052-codex-proactive-check-touchpoints.md) Amendment 4) 와 동일 위치** — 양 verifier 활성 (EC-6 dedup: Codex = P0/P1 inline FIX mandatory, DialogFidelityAgent = correction_action_hint 5-enum 권고) |
| `pre_fix_rootcause` | FIX 루프 root cause 판정 직전 (ArchitectPL 1차 진단 후 최종 판정 직전) | UC-4 (Orchestrator 가 FIX 루프 root cause 판정 직전) | **Codex TP#3 (FIX 2+ 감지 시) 와 동일 위치** — 양 verifier 활성 (EC-5 dedup: Codex = P0/P1 single-shot 검토, DialogFidelityAgent = ledger drift detection 권고) |

dedup 패턴 (EC-5/EC-6): 동일 위치 활성 시 Orchestrator 가 양 verdict 통합 (verify-before-trust [ADR-070](../docs/adr/ADR-070-codex-verify-before-trust.md) 의무).

**turn-shape edge × 3-anchor 12 cell 활성 표 (ADR-071 §결정 13.3, CFP-818)**: 위 "Turn-shape derived defaults" 표 의 E9/E10/E11/E12 edge × 3-anchor cross-product 활성 매핑:

| anchor \ edge | E9 streaming token | E10 tool-call-only | E11 AskUserQuestion popup | E12 trivial answer |
|---|---|---|---|---|
| `post_user_turn` | **final flush 시 활성** (mid-stream spawn 금지 — idempotency, EC-4 derived default) | **면제** (사용자 발화 직접 미발생, EC-3 derived default) | **active** (popup 본문 자체가 dialog convergence anchor — popup option_text/body Layer 3 "추상" detect 영역, EC-2 derived default) | **면제** (cost > benefit, trivial turn 3-criteria AND 충족 시 cognitive overhead 정당화 불가, EC-1 derived default) |
| `pre_architectpl_synthesis` | active (edge-independent — Story 1회 발동, ArchitectPL synthesis 완료 직전 fixed timepoint) | active | active | active |
| `pre_fix_rootcause` | active (edge-independent — FIX 발동 시점 fixed, [ADR-067](../docs/adr/ADR-067-fix-ledger-implementability-escalation.md) FIX 3 카운터 범위 안 ≤ 3/Story) | active | active | active |

cell 값 enum: `active` (spawn 의무) / `면제` (spawn 금지) / `final flush 시 활성` (E9 streaming 의 final flush 단계 1회만 spawn — mid-stream 금지).

**Output Port closed enum**: `verify_result: fidelity_ok | drift_detected | ledger_gap` + `correction_action_hint: rescan_ledger | escalate_user | self_correct | no_action | null` (free-form 차단, generator 역할 침범 금지).

**Orchestrator dispatch**: verifier output 수신 후 `correction_action_hint` enum (rescan_ledger / escalate_user / self_correct / no_action / null) 에 따라 Orchestrator 가 직접 action 분기 — verifier 는 권고만, 실제 메시지 변경 / ledger append / 사용자 escalation 은 Orchestrator monopoly.

**verify-before-trust 의무** ([ADR-070](../docs/adr/ADR-070-codex-verify-before-trust.md)): `evidence_path[]` direct Read verify 의무, mismatch 시 verdict reject + Story §10 tally + override rationale 명시.

**Inline whitelist 1번 entry 정합 cross-ref (ADR-071 §결정 13.4 / CFP-818)**: DialogFidelityAgent spawn (subagent 형태) 자체는 [ADR-039 §결정 2](../docs/adr/ADR-039-orchestrator-subagent-default-for-codeforge-modification-work.md) inline whitelist 4-entry 1번 entry (사용자 dialog) 의 scope **안** cognitive 보강 — 사용자 dialog 본 발화는 inline 유지 + 직전/직후 verifier spawn 은 ADR-039 §결정 1 default subagent spawn 정합. 5번째 entry 신설 아님 (closed enumeration 보존).

**Q-3check disjoint scope cross-ref (ADR-071 §결정 13.5 / CFP-818)**: [ADR-064 §결정 9](../docs/adr/ADR-064-decision-principle-mandate.md) Question quality 3-check = Orchestrator self-check (proposing/stop-time). DialogFidelityAgent = 외부 verifier (발화 entity ≠ 검증 entity 분리, self-referential trap 회피). disjoint scope — 양자 cross-cutting 보강 (3-check 가 cover 못하는 누적 결정 ledger drift / 세션 개시 요건 일관성 = DialogFidelityAgent cover, DialogFidelityAgent 가 cover 못하는 turn-internal cognitive frame / 7 anti-pattern P1-P7 = 3-check cover).

**closed enum 확장 시 별도 CFP 의무 (ADR-071 §결정 13.6 / CFP-818)**: 3-anchor enum closed enumeration 보존. 확장 후보 3종 (`pre_lane_spawn` / `pre_phase_transition` / `pre_pause_decision`) 발생 시 별도 CFP 신설 의무 ([ADR-064 §결정 7](../docs/adr/ADR-064-decision-principle-mandate.md) top-down ratchet + [ADR-058 §결정 5](../docs/adr/ADR-058-adr-sunset-criteria-mandate.md) sunset_justification 정합).

#### Conversational reporting frequency suppression (ADR-071 §결정 15 / CFP-851 / Amendment 4)

Orchestrator 가 사용자에게 **말 거는 시점·빈도** (frequency / timing) 의 closed enumeration 계약. 본질 anchor = **frequency vs richness 분리 invariant** — 본 정책이 좁히는 것은 발화 횟수·시점 만, **말할 때의 풍부함은 §결정 2(c) "3 줄 제약 거부 · 길이 자유 · 배경 포함" 그대로 보존**. SSOT = [ADR-071 §결정 15](../docs/adr/ADR-071-orchestrator-user-dialog-convergence.md), 본 §3.14 = lookup mirror.

**3 touchpoint closed enumeration** — Orchestrator 사용자 발화 허용 시점:

| touchpoint | 발화 사유 | scope |
|---|---|---|
| **(a) 결과-명세 확인** | 사용자가 선언한 결과 자체가 모호 + 잘못 추측 시 rollback 비싼 경우 (verifiable outcome surface 안전판 — wrong-dataset risk 차단) | 가치 / 명세 판단 — `AskUserQuestion` 발화 (§결정 5 결정 트리 — 모호 → 가치 측 분류) |
| **(b) 사용자만 풀 수 있는 차단** | 인증·권한 등 codeforge 자체 해소 불가, 사용자 행동 필요 | ADR-039 inline whitelist 1번 entry (사용자 dialog) scope 안 |
| **(c) 최종 완료 보고 1회** | 요청한 작업 단위 전체 완료 (산출물 = 최종 결과 자체) | ADR-039 inline whitelist 4번 entry (Status report) scope 안 |

그 외 진행·중간 결정·근거·중간 결과 = **산출물 channel** 전용 기록 (대화 turn 아님): `docs/stories/<KEY>.md` / `docs/change-plans/<slug>.md` / `docs/adr/ADR-NNN-<slug>.md` / PR description / GitHub Issue comment / TodoWrite panel ([ADR-038](../docs/adr/ADR-038-progress-visualization-todowrite.md) progress visualization).

**무약화 invariant** — 3 touchpoint 발화 시:
- Layer 1 가시적 preamble + Layer 2 자기 declare 의무 — turn-shape edge derived default (E9/E10/E11/E12 표) 무변경
- §결정 2(c) richness 보존 — raw packet 노출 금지, 평이한 한글, 3 줄 제약 거부, "왜 / trade-off / 걸려있는 것" 배경 포함
- DialogFidelityAgent auxiliary 3-anchor spawn 보존 — §결정 12/13 family pattern 정합
- §결정 14 incident append-rate measurement 보존

**closed enum 확장 패턴** — 4번째 touchpoint 신설 시 별도 CFP 의무 (ADR-064 §결정 7 top-down ratchet + ADR-058 §결정 5 sunset_justification + Story §1 사용자 explicit 승인 의무). 본 ADR-071 안 3번째 closed enumeration 인스턴스 (3-anchor enum / 4 차원 enum / 3 touchpoint enum 동형).

**mechanical lint = 별도 follow-up CFP** (§결정 10 패턴 정합 — behavioral directive only, advisory warning tier 첫 도입 시 evidence-checks-registry entry append + dialog-fidelity-effect precedent 동형 runtime cron measurement).

---

### §3.15 Action-blocked fallback decision tree (CFP-658 / [ADR-027 Amendment 2](../docs/adr/ADR-027-consumer-adoption-protocol.md))

enterprise org-level `default_workflow_permissions: read` 차단 환경 또는 일반 Action failure 시 codeforge 의무 사용 + ADR-039 inline whitelist 외 영역 modification 금지 의무 충돌 해소. Orchestrator 가 매 lane spawn 직전 본 decision tree 수행.

#### Trigger detection 절차 (lane spawn 직전 의무)

```
매 lane spawn 직전:
  ┌─ Step 1: Issue label `fallback:manual` 부착 여부 확인 (Trigger C)
  │     YES → fallback path 활성 (per-Issue override)
  │     NO → Step 2
  │
  └─ Step 2: `.claude/_overlay/project.yaml` 의 `bootstrap.fallback_mode` 확인 (Trigger A)
        == "action_blocked" → fallback path 활성 (environment default)
        == "auto" or absent → 정상 workflow path (story-init.yml 자동 실행 가정)
```

우선순위 (C) > (A). per-Issue 명시 의지 > environment default. (A) 활성 환경에서도 (C) label 없는 Issue 는 정상 workflow 시도 후 fail 시 사용자 escalate.

**Option (B) Outage detection 폐기**: workflow run conclusion + N분 timeout 자동 감지 = workflow self-fail detection 불가 (silent failure, Researcher 위험 1) → 폐기.

#### Fallback path 활성 시 Orchestrator 행동

| Step | 행동 | Owner |
|---|---|---|
| 1 | RequirementsPLAgent spawn (mctrader-hub MCT-135 패턴 시 skip 가능 — ADR-064 §결정 3 룰 1 derived default) | Orchestrator |
| 2 | ArchitectPLAgent spawn — Phase 1 PR manual `gh pr create` 책임 + Codex Touchpoint #2 dispatch (ADR-052 Amendment 4 mandatory) | Orchestrator |
| 3 | `templates/scripts/manual-story-init-fallback.sh <ISSUE_NUMBER>` 호출 (Phase 2 carrier 신설 후 활성) | ArchitectPLAgent or RequirementsPLAgent |
| 4 | phase label 수동 전이 (`codeforge:lane-self-write-boundary` skill 정합) | Orchestrator self-write |
| 5 | Story §14 Lane Evidence row append (ADR-031) | Orchestrator |
| 6 | Trigger (C) PR description 의 manual fallback checklist 6 항목 검증 | Orchestrator |

#### Governance ratchet 약화 mitigation 3종 (자동 발화)

| Invariant | Mitigation | Tier |
|---|---|---|
| §1 verbatim immutable | post-merge lint `section-1-verbatim-postmerge.yml` (Phase 2 carrier) warning tier | ADR-060 framework |
| phase-label transition | Orchestrator 수동 의무 (본 §3.15 Step 4) | governance |
| 4 required check | manual PR 도 phase-gate-mergeable + doc frontmatter + doc section + invariant-check 통과 의무 (`enforce_admins:true` ratchet 유지, CFP-70) | blocking |

#### Codex Touchpoint #2 mandatory (ADR-052 Amendment 4)

manual fallback path 활성 시에도 ArchitectAgent §3 직후 Codex proactive check dispatch 의무. `artifacts` 필드 verbatim attach (ADR-070) — manual write 영역의 governance ratchet 약화 vector 차단 forcing function.

#### env=0 / env=1 동작 동일

`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` env 무관. agent teams platform capability 와 별도 — fallback path 활성화는 Orchestrator detection 수준 결정.

상세 SSOT:
- [ADR-027 §결정 6](../docs/adr/ADR-027-consumer-adoption-protocol.md) — fallback path normative SSOT
- [domain-knowledge `workflow-blocked-manual-fallback.md`](../docs/domain-knowledge/domain/github-actions/workflow-blocked-manual-fallback.md) — recovery runbook
- [consumer-guide §1h](consumer-guide.md) — consumer runbook
- [project-config-schema](project-config-schema.md) — `bootstrap.fallback_mode` schema

---

### §3.19 Admin merge pre-flight gate (CFP-1522 / [ADR-113](../docs/adr/ADR-113-admin-merge-preflight-gate.md))

Orchestrator 가 `gh pr merge --admin <PR-N>` attempt 시점 직전 5-step pre-flight gate 의무. ADR-073 §결정 1 verify-before-assert transition trigger `admin_merge_attempt` sub-domain instantiation. ADR-045 §D-9 pattern_count 3 reach Mandatory ADR escalation 산물 (CFP-1334 retro + CFP-1318 retro + CFP-1495 PR #1505 close evacuation 3-incident super-class `admin_merge_action_required_force_attempt`).

#### §3.19.1 5-step procedure

**Step 1 — required check state enum fetch**

```bash
gh pr checks <PR-N> --json name,state,conclusion --jq '.[] | select(.state != "completed" or .conclusion != "success") | "\(.name): \(.state)/\(.conclusion)"'
```

empty output (모든 required check `state=completed AND conclusion=success`) → admin merge 진행. non-empty → Step 2.

**Step 2 — ACTION_REQUIRED detection + abort (10-value closed_enum)**

```yaml
abort_states_enum:  # closed-set, open_extension: false
  - action_required        # primary block — manual approval needed
  - failure                # explicit fail
  - cancelled              # workflow cancelled
  - timed_out              # CI timeout
  - stale                  # stale check, fresh commit re-trigger needed
  - pending                # in-progress
  - in_progress            # in-progress alias
  - skipped                # workflow conditional skip
  - neutral                # neutral state, Orchestrator manual judgment
  - unknown                # closed-set 외 value → fail-closed semantic (admin merge 차단)
```

1+ check 의 state 가 위 10-value enum 영역에 속하면 abort + Step 3 진입. `unknown` value (closed-set enum 외) = **fail-closed** (admin merge 차단 + 사용자 escalation).

**Step 3 — fresh commit trigger recovery**

ACTION_REQUIRED 잔존 시 fresh commit (empty 또는 trailing whitespace amendment commit) 으로 workflow re-trigger:

```bash
git -C "<worktree_abs_path>" commit --allow-empty -m "[CFP-NNN] re-trigger required checks (admin-merge preflight Step 3)"
git -C "<worktree_abs_path>" push origin <branch>
```

`phase-gate-mergeable.yml` `on:` block = `pull_request: [opened, synchronize, labeled, unlabeled, edited]` only — `workflow_dispatch` entry 부재 (verified). manual re-trigger 경로 부재 영역에서 fresh commit = primary recovery. Wave 4 brainstorm carrier 영역 = `workflow_dispatch` entry 보완 검토 (별 follow-on CFP, ADR-113 §결정 8).

**Step 4 — re-verify (≤ 60s wait + re-fetch)**

```bash
sleep 60   # workflow propagation grace (CI dispatch latency typical 30-60s, Anthropic infra-independent)
gh pr checks <PR-N> --json name,state,conclusion --jq '.[] | select(.state != "completed" or .conclusion != "success")'
```

empty → admin merge 진행. non-empty → Step 5 (attempt cap check).

**Step 5 — attempt cap = 3 STOP + escalate**

Step 1-4 cycle 의 attempt count 가 **3 회** reach 시 STOP + 사용자 escalation 의무. Workflow log direct verify:

```bash
gh run list --workflow="phase-gate-mergeable.yml" --branch=<branch> --limit 10 --json databaseId,conclusion,createdAt
gh run view <latest-id> --log
```

Workflow self-error (workflow code bug / dependency outage) 추정 시 사용자 escalation. **`auto-retry` 무한 loop 차단** (Threat A: counter reset abuse mitigation).

#### §3.19.2 Attempt cap dual scope (per-PR + per-Story)

attempt cap=3 = **dual scope AND** (Threat A counter reset abuse — close+reopen / PR 재생성 / attempt 분산 차단):

- **per-PR scope**: 동일 PR-N 안 `gh pr merge --admin` 시도 누적 ≥ 3 → STOP
- **per-Story scope**: 동일 carrier_story (CFP-NNN) 안 모든 PR 의 admin-merge 시도 누적 ≥ 3 → STOP (close+reopen / PR 재생성 우회 차단)

**dual carrier 조건**: 둘 중 1+ trigger 시 STOP + 사용자 escalation 의무.

#### §3.19.3 진단 flow (failure mode enum 4-fail)

| Fail mode | 진단 | 대응 |
|---|---|---|
| **fail-1** API call failure (network / token expiry / Anthropic infra 429) | `gh` exit code ≠ 0 + stderr 분석 | retry exp-backoff 3회 + `codeforge:rate-limit-429-mitigation` skill + ADR-066 PAT 만료 check (90d rotation) |
| **fail-2** state enum unknown | `gh pr checks` output 안 10-value enum 외 state value detect | **fail-closed semantic** (admin merge 차단 + 사용자 escalation, 10-value enum invariant 보존) |
| **fail-3** re-trigger 후 ACTION_REQUIRED 잔존 | Step 3 fresh commit trigger 후 Step 4 re-verify 에서 동일 ACTION_REQUIRED | workflow self-error 추정 → attempt cap 카운트 + Step 5 STOP escalation |
| **fail-4** silent bypass attempt | Orchestrator/subagent 가 5-step skip + `gh pr merge --admin` 직접 호출 | ADR-024 Amendment 6/8 §결정 6.A 5 lint chain 자동 covered (별 mechanism 0) |

#### §3.19.4 우회 mechanism enum (a-d)

**ADR-113 §결정 3/4 cross-ref** — 다음 4 우회 시도 mitigation:

- (a) **Counter reset abuse** (Threat A) — close+reopen / PR 재생성 / attempt 분산 → **per-PR + per-Story dual scope** (§3.19.2 AND condition)
- (b) **`enforce_admins` toggle abuse** (Threat B) — `gh api -X PATCH /repos/<org>/<repo>/branches/main/protection` 안 `enforce_admins.enabled: false` toggle → **explicit forbid** (audit-trailed exception channel 외 금지, ADR-113 §결정 3)
- (c) **Pre-flight gate script bypass** — Orchestrator instrumentation 우회 + 직접 `gh pr merge --admin` → Wave 2 mechanical wire carrier (`scripts/check-admin-merge-preflight.sh` 3-layer self-block: pre-commit + pre-push + Orchestrator instrumentation, 별 sub-Story carrier)
- (d) **Bypass-as-norm-mutation** — `hotfix-bypass:admin-merge-preflight-gate` norm mutation → ADR-024 Amendment 6/8 §결정 6.A 5 lint chain 자동 covered (`bypass-label-counter` + `per-plugin-cumulative-counter` + `bypass-justification-marker` + `cross-repo-bypass-counter` + `check-bypass-audit-comment.sh`) + `[bypass-justification]` PR comment marker 의무 (`comment-prefix-registry-v1` 14번째 prefix)

#### §3.19.5 Fallback path (CFP-1495 carrier 재진입)

CFP-1495 PR #1505 close evacuation (산출 8 file headRefOid `13b958eb` 보존) recovery procedure (ADR-113 §결정 7 §7.4.1 DR):

```bash
git -C "<new-worktree>" fetch origin 13b958eb
git -C "<new-worktree>" checkout -b cfp-1495-redo origin/main
git -C "<new-worktree>" cherry-pick 13b958eb
git -C "<new-worktree>" push -u origin cfp-1495-redo
gh pr create --title "[CFP-1495] Confluence drift detection cron — REDO" --body "Recovery from closed PR #1505 (headRefOid 13b958eb). post-CFP-1522 ADR-113 admin-merge pre-flight gate active 후 재진입."
```

branch naming `cfp-1495-redo` 권장 (ADR-024 cfp-NNN 정합, 간결 — `cfp-1495` 동일 branch 재사용 시 origin ref dangle 위험). post-CFP-1522 merge 후 활성.

#### §3.19.6 evidence-checks-registry binding

- entry name: `admin-merge-preflight-gate`
- current_tier: `warning` (deferred-followup Wave 1 declaration-only)
- bypass_label: `hotfix-bypass:admin-merge-preflight-gate` (label-registry-v2 v2.70 95번째 family member)
- carrier_adr: ADR-060 (4-tier framework)
- owner_adr: ADR-113 (5-step procedure SSOT)
- paired_owner_adr: ADR-073 §결정 1 (verify-before-assert transition trigger `admin_merge_attempt` sub-domain)

Wave 2 mechanical wire (`scripts/check-admin-merge-preflight.sh` + workflow + bats fixture) = 별 sub-Story carrier (`status: Active` 전환 시점).

---

