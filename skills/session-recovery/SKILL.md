---
name: session-recovery
description: 세션 재개(resume) 복원 절차 + 중단 이후 회수 라우팅 + 운영 트러블슈팅 lookup (활성 Story resume / 사용자 최종 확정 상태 복원 / mid-run 사망·stall·세션 한도 도달·429 계열 4-class 회수 진입점 / 미완결 상태 산출 고정 · salvage 결과 기록 · 판별 원장 freshness / 장수명 lane 작업 분할 계획 / 에이전트 스폰 실패 / GitHub MCP 장애 / Codex CLI 미설치 / Story file·Mapper stale). 세션 개시 시 활성 Story 존재 또는 위 장애·중단 발생 시 호출. gate 명제 (§7.4 FIX 카운터 복원 / §9.6-§9.7.1 label 매핑) 는 playbook 잔류 — 본 skill 은 guide 절차만.
tools: Read
---

# Session Recovery (CFP-2198 / ADR-120 — playbook §7 + §9.1-§9.5 이전)

> **절차 본문 SSOT = 본 skill** — `docs/orchestrator-playbook.md` §7 guide 절차 + §9.1-§9.5 트러블슈팅에서 이전 (CFP-2198, ADR-120 §결정 1 cold×guide). **gate 명제는 playbook 잔류** (ADR-120 §결정 3 — skill 확률 활성화는 gate 캐리어 불가): §7.4 FIX 카운터 복원 의무 / §9.6 PR keyword 정책 / §9.7-§9.7.1 phase×gate label 매핑. 본 절차 수행 중 해당 지점 도달 시 playbook 원문 참조.
>
> **mirror-carrier 주석 (Codex TP 반영)**: 본 body 안의 의무/금지 표현은 전부 1차 carrier 의 mirror 다 — Never-skippable 병렬 스폰 = requirements lane agent 정의 (Domain/Analyst/Researcher 등 4+ 파일) / Codex CLI 미설치 시 진입 불가·중단 = wrapper `CLAUDE.md` 필수 의존성 anchor / Mapper 매 진입 재스폰·재사용 금지·단독 설계 결정 금지 = design lane `CLAUDE.md` + `CodebaseMapperAgent.md` + `ArchitectPLAgent.md` mandate. 본 skill 미활성 turn 에도 해당 gate 들은 1차 carrier 로 유지된다 (ADR-120 §결정 3 정합 — 본 skill 은 gate 의 단독 carrier 아님).

## 1부 — 세션 재개(resume) 복원 절차 (playbook §7 이전분)

### 7.1 활성 Story 조회

```
mcp__github__list_issues(state='open', labels=['type:story'])
```

또는 `Bash(gh issue list --label "type:story" --state open --json number,title,labels)`.

- 0건: 신규 세션
- 1건: 자동 resume — §7.3 매핑
- 2건 이상: 사용자에게 확인

### 7.2 Story file 최신 섹션 판독

`Read(docs/stories/<KEY>.md)` → 어느 섹션까지 채워졌는지 확인해 재진입 지점 보정.

### 7.3 phase label ↔ 재진입 에이전트 매핑

| phase 라벨 | Story file 섹션 | 재진입 에이전트 |
|-----------|-----|-----------------|
| phase:요구사항 | §1만 채움 | RequirementsPLAgent 재스폰 → Domain·Analyst·Researcher **병렬 재스폰** (Never-skippable 3종 전원) |
| phase:요구사항 | §2·§5·§6 **일부만** 채움 (부분 완료 resume) | 비어있는 섹션의 에이전트만 **선택 재스폰** + 이미 채워진 섹션은 PL 통합 단계에서 재활용. §9.0에 "Resume 부분 재스폰" 행 append |
| phase:요구사항 | §2·§5·§6 모두 채움 | RequirementsPLAgent 통합 명세서 재확정 단계 재진입 ("사용자 확인 필요" 해소 여부 체크 + **확정 상태 복원** 체크 — §7.3.1 sibling). 일부 관점 재보강 필요 시 clarification 재스폰 |
| phase:요구사항-리뷰 | §1-7 채움 + §9 요구사항리뷰 블록 유무 무관 | RequirementsReviewPLAgent 재진입 판정 전 **확정 상태 복원** 수행 (§7.3.1) — 확정 gate = 리뷰 PASS 후·설계 진입 직전이므로 이 phase 에서는 정상적으로 `미확정` 또는 `왕복중` |
| phase:설계 | (설계 진입 직후 resume) | ArchitectPLAgent 재스폰 **전** §7.3.1 **확정 상태 복원** 수행 — `미확정`/`왕복중` 이면 설계 진입 preflight 의 `user-final-sign-off-resolved` 미해소(advisory) → 설계 스폰 전 design-entry gate 확정 왕복 재개 |
| phase:설계 | §7 + §11 초안만 | ArchitectPLAgent — Mapper·Refactor·SecurityArchitect·TestContractArchitect·ModuleArchitect **병렬 재스폰** + ArchitectAgent (chief author) 통합 의뢰 (이전 산출물 세션 외 유지 불가, §7/§11 Change Plan 초안만 복원됨) |
| phase:설계 | §7/§11에 6 SubAgent 일부만 반영 (부분 완료 resume) | 미반영 쪽 SubAgent만 **선택 재스폰** + 반영된 쪽은 재활용. §9.0에 "Resume 부분 재스폰" 행 append |
| phase:설계 | §7 완료 | ArchitectAgent 가 Change Plan 저장 완료 보고 + Story §3/§7/§11 self-write 완료 확인 → 설계 리뷰 진입 |
| phase:설계-리뷰 | §9.1 블록 없음 | DesignReviewPLAgent 재스폰 (Claude/Codex 병렬) |
| phase:설계-리뷰 | §9.1 블록 FIX | ArchitectPLAgent → ArchitectAgent (chief author) 재스폰, Change Plan 갱신 |
| phase:구현 | §7 완료, §8 비어있음 | Phase 2 PR open 여부 확인. 없으면 DeveloperPL 직접 mcp__github__create_pull_request 호출. 있으면 DevPL + QADev 병렬 스폰 |
| phase:구현 | §8 일부 | 마지막 구현 에이전트 (§8에서 확인) 재스폰 |
| phase:구현-리뷰 | §9.2 블록 없음 | CodeReviewPLAgent 재스폰 |
| phase:구현-리뷰 | §9.2 블록 FIX | DeveloperPL 1차 진단 → ArchitectPLAgent 최종 판정 |
| phase:구현-테스트 | §9.3 블록 없음 | `gh pr checks <PR_NUMBER> --required --watch --fail-fast` 백그라운드 재실행 (CI gate 재확인 — ADR-048 Amd 2) |
| phase:구현-테스트 | §9.3 블록 FAIL | DeveloperPL 1차 진단 → ArchitectPLAgent 최종 판정 |
| phase:통합-테스트 | §9 통합 테스트 블록 없음 | IntegrationTestAgent 재스폰 |
| phase:통합-테스트 | §9 통합 테스트 FAIL | DeveloperPL 1차 진단 → ArchitectPLAgent 최종 판정 |
| phase:보안-테스트 | §9.4 블록 없음 | SecurityTestPLAgent 재스폰 (Claude/Codex 병렬, lanes.security_ai: true 시만) |
| phase:보안-테스트 | §9.4 블록 FIX | DeveloperPL 1차 진단 → ArchitectPLAgent 최종 판정 |

### 7.3.1 확정 상태 복원 (design-entry gate — ADR-159 결정 4 / Story AC-7)

세션 재개 시 사용자 최종 확정(design-entry gate — 요구사항리뷰 PASS 후·설계 진입 직전) 관련 상태를 복원한다. **복원 범위 = 2종뿐**:

| 복원 항목 | 내용 | 원천 |
|---|---|---|
| **(a) 확정 여부** | 3값 enum — `확정됨` / `왕복중` / `미확정` | Story file 의 **확정 발화 verbatim 기록** (§5.5) |
| **(b) 미해소 질문 목록** | 확정 packet 의 미해결 질문 잔량 (0건이면 "0건" 명시 — 잔량 은폐 금지) | 동일 (Story file §5.5 primary) |

**확정 여부 3값 판정 (Story file 판독 = §7.2 Read 의 부속 단계, 별도 도구·harness 없음)**:

| 값 | 판정 |
|---|---|
| `확정됨` | 사용자 최종 확정 발화 verbatim 이 Story file 에 기록돼 있음 (presence) |
| `왕복중` | 확정 요청(informed sign-off packet) 은 기록됐으나 확정 발화 verbatim 미기록 — 미해소 질문 잔량 존재 가능 |
| `미확정` | 확정 요청 자체가 미기록 (확정 gate 미도달 — 리뷰 전/중 정상 상태 포함) |

- **복원 원천 서열 (SSOT — ADR-159 결정 4)**: **Story file §5.5 확정 발화 verbatim = primary**. Jira mirror = **best-effort 보조** — Jira 결손 ≠ 확정 무효(fail-open). 양채널 상충 시 Story file 우선, 판정 불가면 §7.6 fallback(사용자 판단 요청).
- **Jira 미해결 결정 fork 복원과의 관계**: `decision_channel` 활성 시 세션 재개는 [`codeforge:jira-decision-channel`](../jira-decision-channel/SKILL.md) §10 rehydrate 를 1회 호출한다(기존 연계, 무변경) — 원격 확정 fork 가 미해결이면 그 복원분이 위 (b) 미해소 질문 목록에 합류한다.
- **자동확정 절대 금지**: 복원 결과가 `왕복중`/`미확정` 이어도 Orchestrator 가 확정을 대신 판정하지 않는다 — 확정 왕복 재개만 (ADR-159 결정 4 / ADR-099·ADR-100 `auto_decide_on_timeout: false` 정합). 확정 대기 stop = 정당 멈춤 (ADR-144 A1 / ADR-071 §23.4 carve-out) — over-halt 아님.
- **advisory ceiling (정직 라벨 — ADR-159 결정 6)**: 본 절차가 복원하는 것은 **확정 기록의 presence** 다. 단일 사용자 환경에서 author 로 "사용자 발화 vs Orchestrator 자체 기록" 을 구분할 수 없으므로(ADR-119 §결정 10 ④), 본 복원은 **"user actually confirmed" 의 기계 증명이 아니다** — 기록·규칙의 presence 는 testable, user actually confirmed 는 NOT testable. 본 §7.3.1 = **advisory 복원 규칙**(behavioral directive)이며 신규 기계 게이트가 아니다.

> **§7.4 FIX 카운터 복원 = gate, playbook 잔류** — 세션 개시/압축 재개 시 의무 절차는 `docs/orchestrator-playbook.md` §7.4 원문 수행 (본 skill 미수록).

### 7.5 사용자 통보

```
🔄 세션 재개

[복원된 상태]
- Story: <KEY> — {제목}
- phase: {현재 라벨}
- 재진입 지점: {에이전트 이름} 스폰
- FIX 카운터: 설계 리뷰 {n}/3, 구현 리뷰 {m}/3, 구현 테스트 {k}, 보안 테스트 {s}
- 사용자 최종 확정: {확정됨 | 왕복중 | 미확정} — 미해소 질문 {q}건   ← §7.3.1 (기록 presence 기준)
- Story file 마지막 갱신 섹션: §{X}

[이어서 진행합니다. 문제 있으면 알려주세요.]
```

### 7.6 Fallback (자동 판정 실패)

- 활성 Story 2건 이상 → 사용자에게 어느 Story resume 질문
- Story file 접근 불가 → §9.4 (본 skill 2부)
- phase 라벨과 Story file 섹션 불일치 → 사용자 판단 요청

## 2부 — 트러블슈팅 (playbook §9.1-§9.5 이전분)

### 9.1 에이전트 스폰 실패

| 증상 | 원인 | 대응 |
|------|------|------|
| Agent 툴 호출 실패 | subagent_type 철자 오류 | `agents/` 목록과 대조 후 재시도 |
| 권한 거부 | path-scoped 권한 불일치 | 대상 에이전트 md frontmatter 확인, 담당 에이전트 재선택 |
| 무한 스폰 | 서브에이전트가 Agent 툴 호출 시도 | 플랫폼 제약 위반 — 해당 에이전트 md에 "직접 스폰 불가" 명시 확인 |

### 9.2 GitHub MCP 연결 장애

GitHub Issue/PR 갱신·코멘트 기록·sub-issue 생성 불가 시:

1. 세션 내 임시 로그로 전환 — Orchestrator 메모리에 갱신 내용 누적
2. 사용자에게 "GitHub MCP 장애" 통보. 가능한 fallback: `gh issue ...` Bash CLI
3. 복구 후 각 lane plugin 재스폰으로 backlog 동기화 (lane plugin self-write 재실행)
4. **FIX 카운터 조회 불가 시** (docs file은 로컬 file이라 read는 보통 가능): 그래도 실패하면 ArchitectPLAgent 판정 정지 → 사용자 판단 요청

### 9.3 Codex CLI / 플러그인 미설치

- **CodexReviewAgent**: 미설치 시 3 리뷰 레인(설계 리뷰·구현 리뷰·보안 테스트) **모두 진입 불가** → 설치 안내 + 세션 중단
- **RequirementsAnalyst**: `codex` CLI 미설치 시 요구사항 레인 **진입 불가** → 동일
- `SKIPPED` 경로 허용 안 됨

### 9.4 Story file stale 감지

에이전트 보고에서 "Story file에 없는 컨텍스트" 또는 "현재 코드와 불일치" 감지 시:

1. Orchestrator 가 해당 lane plugin 재스폰 → 최신 상태로 Story file 갱신 (lane plugin self-write)
2. 갱신 완료 후 해당 에이전트 재스폰

### 9.5 CodebaseMapper 산출물 stale 감지

- Mapper는 **매 설계 레인 진입 시 재스폰** — 이전 Story 산출물 재사용 금지
- 리뷰·테스트에서 설계 레인 복귀 시에도 재스폰 (구현 레인에서 코드 변경 가능성)
- 재사용 감지 시 ArchitectAgent (chief author) 단독 설계 결정 금지 (§2 설계 공동작업자 부재 상태)

> **§9.6-§9.7.1 = gate, playbook 잔류** — Phase 1/2 PR keyword 정책 + phase×gate label 매핑 + transition timing 은 `docs/orchestrator-playbook.md` §9.6-§9.7.1 원문 참조 (본 skill 미수록).

## 3부 — 중단 이후 회수 라우팅 · salvage 결과 기록 (CFP-2984 / ADR-179)

> **본 3부가 답하는 질문** = "세션·에이전트가 중간에 끊겼을 때 **어디서 무엇을 들고** 다시 시작하나". 1부 §7.3 재진입 매핑의 **누락된 선행 단계**다 — §7.3 은 "어느 에이전트를 재스폰할지"만 말하고 그 재스폰에 **무엇을 인계할지**는 말하지 않는다.
>
> **본 절 내부 번호 = 3.1~3.7.** 1부 §7.x · 2부 §9.x 는 playbook 원본 번호 mirror 이고, 본 3부는 playbook 대응 절이 없는 신설분이라 별 번호계를 쓴다.
>
> **§9.1 표와 disjoint** — §9.1 은 **pre-run 호출 실패**(subagent_type 철자 오류 · 권한 거부 · 무한 스폰)이고 본 3부는 **mid-run 중단 이후**다. 두 표를 섞지 말 것 (조직 원리가 다르다).
>
> **모듈 의존 방향 = 하향 단방향 1 edge.** 본 3부는 429 rung 을 [`codeforge:rate-limit-429-mitigation`](../rate-limit-429-mitigation/SKILL.md) 로 참조한다. 역방향(rate-limit → session-recovery) 참조는 **신설하지 않는다** — 필요 시 sibling 이 아니라 L0 정책([ADR-109](../../archive/adr/ADR-109-in-process-429-mitigation-framework.md))을 지목한다 (더 안정된 모듈로의 참조 = SDP 정합, 2-cycle 금지).
>
> **★ 4-class closed set 은 본 skill 이 정의하지 않는다.** closed set SSOT = [ADR-109](../../archive/adr/ADR-109-in-process-429-mitigation-framework.md) **단일**이며, 그 집합의 회수-라우팅 view 는 [ADR-179 §결정 7](../../archive/adr/ADR-179-agent-salvage-bundle-handoff.md) 이 소유한다. 아래 §3.1 표는 **그 집합의 소비자 view** 이지 독립 정의가 아니다 — **class 추가·삭제는 ADR amendment 로만** 하고 본 파일 편집으로 집합을 바꾸지 않는다 (두 skill 이 각자 열거하면 검사기가 두 정의역에서 상이 판정을 낸다).

### 3.1 실패 class → 회수 경로 진입점

| class | 회수 경로 진입점 | 재시도 예산 | 산출 고정 시점 |
|---|---|---|---|
| 429 계열 (rate limit) | [`codeforge:rate-limit-429-mitigation`](../rate-limit-429-mitigation/SKILL.md) 3-step 절차 안 — **탐지 직후·대기 진입 전 산출 고정** 후 대기 진입 ([ADR-109](../../archive/adr/ADR-109-in-process-429-mitigation-framework.md) §결정 7) | 사다리 소관 | 대기 진입 **전** |
| 세션·주간 한도 | [ADR-141](../../archive/adr/ADR-141-all-opus-single-tier.md) Amendment 6 fresh re-spawn + Amendment 10 salvage 인계 | 1 (per-spawn) | 재spawn packet 구성 **전** |
| stall (무출력 정체) | [ADR-139](../../archive/adr/ADR-139-background-wait-liveness-gate.md) `inconclusive` 기록 → **비파괴 recovery 만** (kill · TaskStop · 기산출 폐기 동반 재spawn 금지) | 0 | `inconclusive` 기록 시점 |
| mid-run 사망 | [ADR-178 §결정 5-4](../../archive/adr/ADR-178-subagent-progress-commit-preservation.md) 3-step runbook (census → 무결성 판정 → 인계 3-tuple) + [ADR-179 §결정 2](../../archive/adr/ADR-179-agent-salvage-bundle-handoff.md) 번들 | 0 | 진행 커밋 시점 (상시 선행 적재) |

- **진입점 셀이 빈 행은 커버로 세지 않는다** — class 는 있는데 갈 곳이 없으면 미커버다. 그 경우 §3.2 에 명시 열거한다.
- **재시도 예산 0 의 의미**: 회수 경로 자신은 재시도를 발행하지 않는다 ([ADR-179 §결정 8](../../archive/adr/ADR-179-agent-salvage-bundle-handoff.md) — 복구가 스스로 예산을 곱하면 손실 감축이 발생 증가로 되돌아온다).

### 3.2 미커버 class 선언 (차집합 착지면)

**현재 미커버 = 0건.** §3.1 표가 정본 4-class 전건에 진입점을 지정한다.

정본 집합에는 있는데 §3.1 이 커버하지 못하는 class 가 생기면 **침묵하지 말고** 아래 3열 표로 이 절에 명시 열거한다 — 열 = `미커버 class` / `사유` / `임시 진입점`. **임시 진입점 없는 미커버 선언은 선언이 아니다** (어디로 가라는 말이 없으면 운영자는 멈춘다).

### 3.3 미완결 상태 산출 고정 경로

완결 경로만 있는 문서는 중단 상황에서 쓸모가 없다. **완결 · 미완결 · 미완결(저장 실패) 3 상태 전건에 산출 고정 행위와 종료 표식을 지정한다.**

| 상태 | 산출 고정 행위 | 종료 표식 | 근거 |
|---|---|---|---|
| 완결 | 의미 단위 완결 커밋 (미완 표식 제거) | `[WIP]` 토큰 **제거** | [ADR-178 §결정 5-2](../../archive/adr/ADR-178-subagent-progress-commit-preservation.md) |
| 미완결 | 진행 커밋 선행 적재 → salvage 번들(참조형 인덱스) 생성 → 재spawn packet 에 3-tuple 주입 | `[WIP]` 토큰 + 본문 `Remaining:` 1줄 | [ADR-178 §결정 5-2·5-4](../../archive/adr/ADR-178-subagent-progress-commit-preservation.md) / [ADR-179 §결정 2](../../archive/adr/ADR-179-agent-salvage-bundle-handoff.md) |
| 미완결 (저장 실패) | degrade 사다리 F1(dirty 유지) → F2(scratch + 보존 마커) → F3(손실 범위 사고 레코드) | `empty_reason` + `failed_at` (빈 번들 ≠ 생성 실패) | [ADR-179 §결정 8](../../archive/adr/ADR-179-agent-salvage-bundle-handoff.md) |

**무효 전이 (금지 — 관측되면 결함)**:

| 무효 전이 | 왜 금지인가 |
|---|---|
| 저장 실패 → 성공 보고 | 저장에 실패하면 종료 코드가 `0` 이 아니어야 하고 회수 불가 범위를 기록해야 한다. 실패를 성공으로 접으면 상류가 없는 번들을 있다고 믿는다 |
| 번들 미생성 → 재spawn 인계 | 인계 3-tuple 이 없는 재spawn 은 처음부터 다시 하는 것과 같다. 번들 부재 시에는 **부재 사실**을 packet 에 명시하고 인계한다 (조용한 빈손 인계 금지) |

- **부분 기록 번들은 유효 번들로 판독하지 않는다** — 절단된 번들은 `suspect` 이며 완결 산출로 승격하지 않는다.

### 3.4 salvage 결과 기록

회수를 했는지 안 했는지가 사후에 남아야 다음 세션이 같은 손실을 두 번 겪지 않는다. 회수 시도 1건당 아래 항목을 기록한다.

| 항목 | 값공간 | 비고 |
|---|---|---|
| `class` | §3.1 정본 4-class 중 1 | 정규화 후 정확히 1개에 사상되지 않으면 기록 불가(모호) |
| `bundle_ref` | `branch@SHA` 또는 `없음` | 원문 동봉 금지 (참조형) |
| `resume_spawn` | `stop-event-v1` `recovery_action` enum 의 `retry` 로 **부분 표현 가능** | 완전 표현 아님 — 계약 확장은 별 lane 소관 |
| `salvage_outcome` | **양 계약에 부재** | 신규 필드 배선은 본 절 경계 밖. 현재는 **미배선 사실을 그대로 적는다** (있는 척 금지) |
| `burn` | 소각량(재작업 span) 추정 1줄 | 추정임을 명시 |

- **기록은 계약 수정 없이 수행한다** — `spawn-event-v1` · `stop-event-v1` 스키마는 읽기만 한다.

### 3.5 판별 원장 freshness 가드

사후 판별(§3.4 기록 · 종료 레코드 조회)은 **원장이 최신일 때만** 신뢰할 수 있다. 최신 레코드 시각과 기준 시각의 격차가 임계를 넘으면 `stale` 로 판정하고, 그 판별 결과를 근거로 삼지 않는다.

| 항목 | 값 | 근거 |
|---|---|---|
| 기대 기록 주기 상한 (C) | **15분** | 외부 관측 poll 의 jitter 상한 — GH Actions cron 5분 base + peak jitter 15~30분 ([ADR-164 §결정 6](../../archive/adr/ADR-164-parallel-branch-liveness-heartbeat-watchdog.md)) |
| 유도 규칙 | **T = 2 × C** | 기존 규칙 재사용 — `scripts/lib/check_branch_liveness.py` `_FLOOR_MIN` 주석 "floor ≈ 2× poller-jitter-upper(GH cron 5min base + peak jitter 15~30min) → 30~60min" |
| 임계 (T) | **30분 = 1800초** | 위 두 줄에서 유도된 값 (임의 상수 아님) |
| 경계 포함/배타 | `격차 > T` 일 때만 `stale`. **`격차 = T` 는 `fresh`** (배타적 stale) | [ADR-164 §결정 5](../../archive/adr/ADR-164-parallel-branch-liveness-heartbeat-watchdog.md) 의 `observer-elapsed > 임계` 부등호 승계 |

- **임계를 임의로 키우면 가드가 영구 미발화한다** — T 는 위 유도 규칙의 산출값이어야 하며, C 를 바꾸지 않고 T 만 키우는 편집은 위반이다.
- **정직 천장**: C·T 는 proposal 이다 (empirical calibration 미완 — ADR-164 §결정 6 상속). "정확한 임계" 를 단정하지 않는다.

### 3.6 장수명 lane 작업 분할 계획 구조

장수명·고복잡도 lane 은 착수 **전에** 독립 재개 가능 단위로 쪼개고, 단위가 끝날 때마다 부분 산출을 확정한다. 계획서는 아래 **3요소 스키마**를 채운다 — 셋 중 하나라도 결손이면 계획이 아니라 의향서다.

| 분할 단위 | 단위별 재개 입력 | 단위 간 확정 경계 |
|---|---|---|
| 독립 재개 가능한 최소 작업 덩어리 1개 (예: "3부 문서 신설") | 그 단위를 0-context 에서 다시 시작하는 데 필요한 입력 (예: 대상 파일 경로 + 정본 앵커 ADR 목록) | 단위 종료 시 확정되는 산출과 표식 (예: 커밋 1건 + `[WIP]` 제거) |
| 다음 덩어리 (예: "self-test 7본") | (예: 위 3부 문서 커밋 SHA + AC 표 행) | (예: 테스트별 커밋 + 실행 출력 rc 첨부) |

- **한계 (정직 라벨)**: 본 스키마는 **구조 결손만** 잡는다. 분할이 실제로 컨텍스트 압박을 줄이는지 = **내용 타당성은 사람 검토** 소관이며 기계 판정하지 않는다.

### 3.7 stall 판정 (오조기회수 방지)

| wall-clock 상한 | 진행신호 | 판정 |
|---|---|---|
| 초과 | 부재 | **stall** |
| 초과 | 존재 | stall 아님 (느리지만 진행 중) |
| 미초과 | 부재 | stall 아님 (짧은 무응답 — 조기 회수 금지) |
| 미초과 | 존재 | stall 아님 |

- **두 조건이 동시 성립할 때만 stall** 이다. 한쪽만으로 stall 을 단정하면 살아있는 에이전트를 죽인다.
- **진행신호 값공간 = 3원소** — output mtime · content grep · task-notification ([ADR-139](../../archive/adr/ADR-139-background-wait-liveness-gate.md) 결정 1 INV-L3). **3원소 중 1개만 도착해도 "부재 아님"** 이다.
- **판정불가는 stall 이 아니다** — 경과시간이 음수·비수치·`NaN` 이면 `indeterminate` 를 반환한다. 판정불가를 stall 로 접으면 오탐이 폭증한다.
- **stall ≠ PASS ≠ 사망** — stall 은 outcome 미측정(`inconclusive`)이며, 후속 조치는 §3.1 의 stall 행(비파괴 recovery 만)을 따른다.
