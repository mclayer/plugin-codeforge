# CLAUDE.md

## 언어 정책
모든 응답·주석·문서는 **한글 주 언어**. 영어는 기술 용어·코드·고유명사만. 한자(일·중 포함) 금지.

## 정체
codeforge = Claude Code 범용 SW 개발 오케스트레이션 플러그인 모노레포. **0 core 에이전트 (wrapper-only)** — wrapper 루트 자체 에이전트 0, 최상위 Claude 세션(Orchestrator)이 6개 lane plugin 의 에이전트를 spawn 해 요구사항 접수부터 보안테스트까지 진행한다. 6 lane plugin 은 본 repo `plugins/<plugin name>/` 하위 동봉 (ADR-118 D3) — 에이전트 상세 SSOT = `plugins/<lane>/CLAUDE.md`. 구 lane repo 8개 = 2026-06-12 GitHub archive (이력 보존, ADR-118 D1).

consumer 프로젝트가 **설치해 쓰는 플러그인**이다. 프로젝트별 도메인·기술스택·상수는 consumer 측 `.claude/_overlay/` 로 주입(overlay 는 정책을 확장만 가능, 축소 불가). 상세: [docs/consumer-guide.md](docs/consumer-guide.md).

6 lane plugin: `codeforge-{requirements, design, review, develop, test, pmo}@mclayer`. 추가 필수: `github` · `codex`.

## 핵심 흐름
8 레인: 요구사항 → 요구사항리뷰 → 설계 → 설계리뷰 → 구현 → 구현리뷰 → 통합테스트 → 보안테스트.

- **1 Story = Phase 1 PR(§1–7) + Phase 2 PR(§8–11).** 모든 변경 = 정식 full 8 lane + Phase 1/2 PR 분리 무조건 (문서만 바뀌는 변경의 단일 PR·chore 면제 폐지 — ADR-127 §결정 1/2). Epic = Phase 1 문서 PR + N개 구현 PR + close PR.
- Orchestrator 는 각 레인 진입 시 해당 lane plugin 의 **PL 에이전트 1개**만 spawn 한다 (PL 이 내부 sub-agent fan-out).
- Story file = `docs/stories/<KEY>.md` (KEY 접두사 = `CFP`). 각 레인이 자기 owned 섹션을 직접 write.

> **요구사항리뷰 lane**: 요구사항 결론은 외부 개념·시장·표준 사실에 가장 자주 의존하므로, 요구사항→**요구사항리뷰**→설계 시퀀스로 외부사실 의존성을 설계 진입 전에 검증한다 (외부지식 충당 3-단계 중 깊은 검증 단계의 주 발동 lane). **lane 개수 ≠ plugin 개수** — `codeforge-review` 부품 하나가 이미 설계리뷰·구현리뷰·보안테스트·요구사항리뷰 다수 lane 을 host 한다 (1 plugin 다 lane). 근거 SSOT = ADR-124 (외부지식 충당 3-단계 모델). **실 lane 시퀀스·카운트 wiring (9→10 hard-commit — ADR-125 Amendment 1 카운트 정정) + 게이트 설계 = CFP-2326 S2 / ADR-125** (요구사항리뷰 lane 신설 carrier — phase:요구사항-리뷰 + gate:requirements-review-pass + phase-gate-mergeable required.gates 매핑, branch protection required contexts 무변경 — required 신설 0).

## 작업 규칙 (필수)
- **브랜치**: 모든 변경은 feature 브랜치(`cfp-NNN[-slug]`) + PR 경유. **main 직접 push 금지.**
- **worktree**: 모든 코딩 작업은 격리된 worktree(`~/.claude/worktrees/<repo>/<branch>`) 안에서 — `git checkout` 직접 편집 금지 — **Story/PR 완결(merge 확인) 직후 해당 worktree 즉시 정리**. 절차 = `codeforge:worktree-lifecycle` skill.
- **스크래치 위치**: repo 밖 임시 산출물은 `~/.claude/codeforge-scratch/` 만 허용 (홈 루트 직접 쓰기 금지 — repo-confinement 가드가 차단).
- **subagent default**: 수정 작업은 `Agent` tool spawn 으로 수행. inline 직접 편집(Read/Write/Edit/Bash 직접)은 4종만 허용 — 사용자 대화 / TodoWrite / 읽기전용 Q&A 답변 / 상태 보고.
- **병렬 default**: 서로 독립인 작업은 한 메시지에 다중 spawn. 순차는 (상태 의존 / 공유 자원 / 순서 자체가 의미) 중 하나일 때만.
- **진행 시각화**: Story 진행 중 lane 전이 6시점(진입/PASS/FIX 검출/원인 판정/재진입/완료) TodoWrite 갱신 시도 의무 (non-skippable, 실패는 non-blocking). 마커 = 네이티브 status 렌더 (content 이모지 금지). SSOT: ADR-038 + playbook §14.
- **검증 후 단언 (research-before-claims, ADR-119)**: substantive 단정 = 대상별 검증 선행 — ① 외부 지식: 자료 조사(WebSearch/WebFetch/공식 문서) + 출처 인용. ② repo·cross-repo 사실: 실측 — repo 내부는 Read/Grep, cross-repo 는 `git fetch` 후 origin/main 실제 확인(`git show origin/main:<path>`). 외부 워커(Codex 등) 출력은 직접 Read 검증 후 신뢰. ③ 확인 불가: "확인 불가/추정" 명시 후 진행. wrapper+consumer 모두 적용. **두 판정면에도 적용 (ADR-119 Amd 2 / Epic #2346)**: ④ 게이트 verdict("PASS") = internal proxy(loop-lag/CPU 등) 아닌 outcome ground-truth 로만 단정 ⑤ 실패 진단("원인=X") = 표면 증상 아닌 코드·invariant falsification 통과 후 단정 (runtime 실패 = FIX loop 아닌 요구사항 lane 재진입).
- **제안 필요성 게이트 (ADR-119 §결정 9)**: 발견 ≠ 필요. 작업 제안·follow-up Issue 발의 전 3문 게이트 — ① 깨졌나·강제 요인 ② 이득>비용·리스크 ③ 관찰자 없어도 할 일. 셋 다 YES 아니면 발의 금지("관찰됨·미조치" 1줄만). 완료 보고 = 작업 상태 실측 후 단언, 추측성 backlog 패딩 금지. wrapper+consumer.
- **Agent 액션 렌더 줄 프리픽스 (model-authored primary render · hook fail-open backup, ADR-143 Amendment 2 / CFP-2770 · 값 정확성 저작 규율 Amendment 3 / CFP-2818)**: harness UI 가 Agent 스폰·도구호출을 렌더하는 줄에 `[<주체명>] MM/DD HH:MM - <내용>` 프리픽스를 붙여 "누가·언제·무엇을 시작했는지" 를 즉시 식별(glanceability). 화면 렌더에 실제 도달하는 **유일 통로 = model-authored 프리픽스** — 에이전트/Orchestrator 가 description·prose 에 **직접 저작(primary)**. PreToolUse hook `updatedInput` 기계 주입(CFP-2587)은 도구 **실행 입력 계층**만 치환하고 화면 렌더 줄(model-emitted 원본 표시)에 미도달 → render-glanceability 목적에서 **fail-open backup 으로 강등**(실행-계층 정확성 목적 유효 잔존, 코드·G1-G5 삭제 0).
  - **범위①** Agent spawn `description` = `[<피스폰 subagent_type>] MM/DD HH:MM - <task>` — model 이 `Agent.description` 에 직접 저작(subject=피스폰자; dispatcher/Orchestrator 이름이 spawned 줄 subject 로 절대 미등장 — INV-1). backup = PreToolUse(Agent) hook `pretooluse-agent-spawn-gate`.
  - **범위②** 서브에이전트 leaf Bash 호출 `description` = `[<self agent_type>] MM/DD HH:MM - <action>` — model 이 `Bash.description` 에 직접 저작(subject=self). backup = sibling PreToolUse(Bash) hook `pretooluse-bash-description-inject`. **top-level Bash(Orchestrator 직속, agent_type 부재) = hook injection EXCLUDE**(dispatcher 명 미주입).
  - **범위③** Orchestrator 상태·액션 줄 = `[Orchestrator] MM/DD HH:MM - <내용>` self-subject 직접 저작 허용(렌더 UI 진행 줄 한정 — INV-2 self-subject 완화; model 은 자기가 Orchestrator 임을 앎 subject-genuine, hook 판별 불가와 계층 disjoint). **prose 상태보고(ADR-039 §결정 2 whitelist entry #4 — 사용자 대상 대화 텍스트)는 prefix-exempt 유지** — 렌더 UI action/상태 LINE(display 축) ≠ prose 상태보고(mechanism 축) disjoint.
  - **description 필드 없는 도구(Read/Edit/Grep/Write 등)** = 저작 표면 부재 → **advisory residual** 정직 잔존(프리픽스 불가 = 결함 아님, OOS).
  - **주체 규율(AC-4)**: subject 값 공간 = spawn-event-v1 `agent_type`(roster-derived) **verbatim** — 범위① = 피스폰 `subagent_type`, 범위② = self `agent_type`. 미등재·불명 = `unknown-agent` fallback (허구명·작업명·dispatcher 명 금지 — INV-1). spawn packet 주입 self명 = **"spawner-asserted, subagent-unverified"** 정직 선언 (검증됨 참칭 금지, 값은 Agent 호출 `subagent_type` verbatim 사본).
  - **전달 채널(서브에이전트 도달)**: SubagentStart hook `additionalContext` 가 서브에이전트 세션 시작 시 (a) self명(input `agent_type`, G2 namespace-strip 재사용) (b) fresh KST 헬퍼 실측치 (c) 저작 규율을 주입 — consumer 세션(wrapper CLAUDE.md 부재) 포함 도달 + spawn packet 저작 규율 보조. **전달의 기계화이지 준수의 기계화 아님** — model 저작 준수는 여전히 advisory (렌더 기계게이트 불가 invariant 무손상).
  - **시각원 — model 계층 지침(Amendment 3 §결정 3 계층 분기, AC-3)**: 표시 시각은 **실측 앵커에서만 유도** — 앵커 = 헬퍼 `scripts/kst-render-stamp.sh`(→ `scripts/lib/kst_render_stamp.py`) 실행 산출 또는 SubagentStart·spawn packet 주입 실측치. 로컬 clock read·암산 offset 가산 일절 금지 (이미-KST 값에 +9 재가산 = 정확히 +9h 미래). tz 변환 = 헬퍼 단일 경로. "UTC+9 고정 산술"은 **헬퍼 invocation 내부 정당화**이지 model 저작 지침 아님. 컴팩트(offset/연도/초/KST 라벨 미표기).
  - **floor(앵커 verbatim, AC-2)**: 앵커 값 **verbatim** 사용 — 경과분 상향 가산·반올림 금지. "표시 시각 ≤ 저작 시점 실측 now" invariant (앵커는 저작 이전 측정이라 verbatim 사용 시 미래 overshoot 정의상 불가).
  - **재실측 trigger 4종(stale 앵커)**: 제어를 (재)획득한 매 활성화 turn 시작 시 — T1 park/child-대기 복귀 / T2 세션 resume·cold-resume / T3 공백 후 lane·컨텍스트 전환 / T4 임의 suspension 복귀 — timestamp 프리픽스 최초 저작 전 헬퍼 1회 재실행. 수치 상한("X분 초과") 게이트 없음 (model 은 경과 실측 시계 부재 = uncheckable → theater 회피; ≈10분 = 비규범 comfort 참고).
  - **앵커 부재 시 생략 fallback(AC-1, 생략 > fabrication)**: 실측 앵커 미보유 시 `[<주체명>] MM/DD - <내용>`(HH:MM 생략 — 날짜는 harness date-only 주입으로 가용) 또는 시각 요소 전체 생략. 허구 시각 기입 금지 [source: RFC 5424 §6.2.3 — TIMESTAMP 획득 불가 시 NILVALUE MUST]. canonical 형식 대체 아닌 앵커-부재 한정 additive 변형 (RE_PREFIX 골격 무손상).
  - **TodoWrite 행 제외**(native status 렌더 전용·이중표기 금지). 3요소(주체명/시각/내용)에 secret·token·절대경로·자격증명 임베드 금지 — 내용은 액션 요약만. hook backup 발화 시 subject sanitize(namespace-strip·`]` strip·≤64·`unknown-agent` fallback, G2) + bare updatedInput(permissionDecision 미emit, G4 — sibling deny 무력화 불가) + whole-echo(description-only, G3) 기계 계약 무손상.
  - **정직성(ADR-119)**: render 도달은 기계게이트 불가(ephemeral + upstream #61152 render-transform hook 부재) → normative 0, advisory ceiling. render-loss(프리픽스 미표시) 근본원인 = **계층 어긋남**(실행 입력 ≠ 화면 표시)이지 #15897 아님 — hook 이 완전 성공(`updatedInput` 정상 emit)해도 화면은 model-emitted 원본을 렌더. #15897(multi-hook updatedInput drop, closed-not-planned, v2.0.76)은 실재 hook 버그로 정확히 기술하되 render-loss 근본원인으로 오프레이밍 금지. hook backup = fail-open(주입 실패 = 원 description, never wrong-value). "100% 기계강제/hard-gate" 아님.
  - **매턴 self-check(backstop)**: "이 액션·상태 줄에 `[주체명] MM/DD HH:MM -` 프리픽스를 직접 저작했는가? (TodoWrite·prose 상태보고·description-less 도구 제외)" + 값 정확성 2항 — "시각: 실측 앵커를 보유했는가(부재 시 생략했는가)? 앵커 값을 verbatim 사용했는가(상향 가산·+9 재가산 0)?" / "주체: subject 는 roster 실명(피스폰=`subagent_type`/self=`agent_type`) verbatim 인가(허구명·작업명·dispatcher 명 0)?" — model-authored 저작이 primary render 통로이므로 self-check 는 저작 attempt-obligation backstop(hook backup 은 이중 안전망).
- **Orchestrator context 위임 (ADR-142 §결정 1 L1 · advisory)**: 장수명 Orchestrator 는 raw 분석용 READ 축적을 read-worker subagent 에 offload 후 high-signal 요약만 수신함을 **default 경로로 승격**(prompt-mandate — hard block 아님). 검증 read(위 research-before-claims 의 repo 사실 Read/Grep 실측)·읽기전용 Q&A·status·Story inline 직전 확인·단일 1회성 사실확인 등 **essential/trivial carve-out 은 예외** — L1 은 "raw 분석 축적을 위임"이지 "검증 read 금지"가 아니다.

## 레인 진입 시 스킬 호출
Orchestrator 는 해당 레인 진입 직전 아래 스킬을 호출한다. 상세 절차·표는 각 스킬 본문 SSOT.

| 진입 시점 | 스킬 |
|---|---|
| 설계 | `codeforge:deputy-mandate` |
| 설계리뷰 / 구현리뷰 / 보안테스트 | `codeforge:review-responsibility` |
| 배포 / lane owner path 확인 | `codeforge:lane-self-write-boundary` |
| FIX 루프 | `codeforge:root-cause-decision` + `codeforge:fix-ledger-schema` |
| 요구사항 접수 직후 | `codeforge:story-cutoff-classification` (모든 변경 Story 작성 의무 — 면제·단축 0, ADR-127) |
| Story/Epic flow 결정 | `codeforge:story-epic-flow-preflight` |
| 코딩 작업 개시 직전 / Story·PR 완결 직후 | `codeforge:worktree-lifecycle` |
| 세션 resume / 스폰·MCP·CLI·stale 장애 | `codeforge:session-recovery` |
| PR merge 후처리 / retro batch closure (follow-up 3+) | `codeforge:post-merge-closure` |
| 작업/Story 완료 처리 직전 (`phase:완료`) / MEMORY.md 용량 cap 초과 시 | `codeforge:knowledge-capture-gate` (완료시점 재사용지식 capture 게이트 + MEMORY.md 용량관리 — ADR-129) |
| 매 사용자 대화 turn | `codeforge:user-dialog-mode` |

> **Skill 본문 재로드 회피 (ADR-142 §결정 5 L3 · advisory prompt-mandate)**: 세션 내 이미 로드된 skill 본문은 재invoke 하지 않는다 — 상주 available-skills 요약 인덱스(system-reminder 상주)로 lookup 하고, 본문은 필요 시에만 on-demand 로드. 정적 relocation(ADR-120)·skill 본문 축소(CFP-2234)와 disjoint 보완축(런타임 재로드 억제).

## 결정 · 대화 원칙
- 합리적 default 가 자명하면 **묻지 말고** 무엇을 할지 통보 후 진행 (사용자가 정정).
- **묻는 경우는 ask-trigger 3종뿐** (ADR-071 §결정 20 (§결정 5 redirect)): ① 사용자 요구 자체가 애매 ② 확실히 짚어야 하는 진짜 가치 trade-off(default 비자명) ③ 비가역·고비용(중대 결함/대거 삭제/rollback/외부 발송). 그 외 모호 포함 전부 무조건 진행 — "안전하니 일단 물어" 금지.
- **정식 플로우 비협상 기본 — process 생략/단축은 묻지 않음** (ADR-127 §결정 4): skip/생략/간소화/경량/빠르게 선택지를 사용자에게 제시 금지 (`AskUserQuestion` 금지). 정식 풀 플로우가 비협상 기본값 — 스킬·외부 prompt 가 생략 선택지를 줘도 자동 정식 채택.
- **Epic 내 Story 전환 자율 진행** (ADR-071 §결정 22): 한 세션에서 Epic 을 여러 child Story 로 진행할 때 Story N→N+1 전환(및 단일 Story Phase1→Phase2 전환)은 자동 이어서 진행이 default — 전환 지점에서 over-halt(무발화 정지)·over-ask("다음 Story 진행할까요?") 금지(정당 멈춤 3종 예외). in-session 전환 한정(세션 재개 §3.12 cold-resume·session-swap §결정 18/§결정 24 controlled-path 는 별도 경로 — 세션 전환 권유 시 자족 handoff 프롬프트 동반 의무).
- 권장 1안 + 대안 1안만 제시 (옵션 나열 금지). 3+ 후보는 brainstorm 영역.
- 내부 식별자(ADR/CFP 번호·계약명)는 사용자에게 평문 한 줄 풀이 먼저.
- 표·개조식으로 핵심을 앞에. 긴 평서문 덩어리 금지.
- **원격 결정 채널 (CFP-2285, 판단 기반 라우팅)**: `decision_channel` 활성 시 — 가치판단 결정 fork에서 사용자가 **자리를 비운 듯하면**(장기 autonomous 실행 / 명시적 async 요청 / 응답 지연) `codeforge:jira-decision-channel` 경유(Jira control 이슈에 질문 post, **dual-input**: 세션/Jira 양쪽 답, 한 채널 응답을 **양 채널에 mirror 기록**). 자리에 있으면 세션 직접. **자동결정 절대 금지**(timeout=재알림만). 진행 가시화는 `codeforge:jira-progress-mirror`(ADR-038 6-point lane 마일스톤 미러).
- **on-demand 깊은 조사 (CFP-2329)**: lane 이 작업 *중* 외부사실 의존 known-unknown 으로 막혀 얕은 자가조사(단계②)로 안 되면 — lane 은 요청만 올리고 Orchestrator 가 문지기로 `codeforge:research-request-gate` 경유(게이트 심사 → deep-research → cited 결과 주입). spawn=Orchestrator 전용 유지(lane 자가-spawn 불가), 검사연극 금지 상속. 근거 ADR-126 (외부지식 충당 3-단계 ADR-124 단계③ on-demand).

## 문서 위치
- 결정 기록(ADR) = `archive/adr/ADR-NNN-<slug>.md`.
- Change Plan / 도메인 지식 / 회고 = `docs/{change-plans,domain-knowledge,retros}/` (owner 에이전트 직접 write).
- 문서 종류별 위치 SSOT = [docs/doc-locations.yaml](docs/doc-locations.yaml).
- dogfood 산출물(spec/plan/story 등) = `mclayer/codeforge-internal-docs` repo.

## 필수 의존성 (세션 개시 확인)
- Orchestrator 모델 = `fable`(또는 `opus`). **Sonnet/Haiku 세션이면 중단** 후 재시작 — fable 은 valid Orchestrator 세션 모델(self-halt 대상 아님, ADR-141 Amendment 4). **이 '중단' 규범은 Orchestrator 세션 scope 한정** ('## opus default + ADR-141 carve-out (Amendment 1 haiku 7 + Amendment 2 sonnet 14 + Amendment 4 fable 10)' 의 guard 참조; carve-out non-opus(haiku 7 + sonnet 10 + fable 10) subagent 는 정상 — self-refuse 대상 아님).
- MCP 서버 `github` 필수 (`mcp__github__*` 우선, 미커버 영역만 `gh` CLI fallback).
- 필수 CLI: `gh`, `codex`.
- 미노출 시 `/mcp` 재인증 / `/plugins install` 요구 후 대기. 복구 전 작업 중단.

## 마켓플레이스 동기화
plugin.json 의 `name`·`version`·`description`·`author` 변경 시 `mclayer/marketplace` 의 동일 필드를 같은 Story 안 sync PR 로 맞춘다 (marketplace sync PR 선행 merge → plugin PR merge). 상세: [archive/adr/ADR-063-marketplace-atomic-invariant.md](archive/adr/ADR-063-marketplace-atomic-invariant.md).
bump 포함 PR merge (`mergedAt` 확인) 직후 Orchestrator 가 터미널 CLI `claude plugin update <plugin>@mclayer` 를 직접 실행하고 cache 반영을 실측한다 (`/plugins update` 슬래시 명령은 미지원) — 사용자에게 업데이트 액션 요구 금지, 보고 1줄만 (적용 = 다음 세션. ADR-063 Amendment 12).

## 브랜치 보호
**branch protection contexts SSOT (wrapper 단일)**: `phase-gate-mergeable.yml` workflow job ID = `check-gate` — contexts 에 `check-gate` 포함 의무. CFP-1850-S2 wrapper 6-tuple 정합 확정 → CFP-2603 (Epic CFP-2602 G1) 7-tuple 로 narrowing (신규 required context `ac-traceability-matrix` 추가 — AC-ID zero-drop fail-closed 게이트, [ADR-145](archive/adr/ADR-145-ac-traceability-zero-drop-gate.md) §결정 3: 6→7 narrowing = fail-closed 비호환 override 근거, ADR-125 의 required contexts 무변경 선례와의 divergence 추적) → CFP-2780 (ADR-136 Amendment 5 §결정16) 7-tuple → 9-tuple 로 narrowing (css-lint D1 게이트 required 승격 — 메인 `css structural lint (stylelint, warning-tier)` + `css-lint discriminating test (mutation 생존 0)` 둘 다 required 등재, hollow-gate 회피; ratchet-UP 확장이라 ADR-145 의 fail-closed 비호환 override 와 달리 상반 선례 override 아님) → CFP-2782 (ADR-121 Wave 2) 9-tuple → **8-tuple** 로 narrowing (배포 2 lane 물리 제거로 `Verify deploy lane presence (Phase 2 wire — ADR-087 Amd 2)` context 제거 — gate 목적(deploy lane wiring 존재 확인)이 deploy lane 제거로 obviated, 여전히 필요한 control 제거 아님 → 보안 약화 0; ADR-145 fail-closed override 와 무관, deprecation-driven 축소). 상세 이력 = audit doc 보존.

| repo | required_status_checks contexts | 비고 |
|------|--------------------------------|------|
| wrapper (plugin-codeforge) | `["phase-gate-mergeable","invariant-check","doc frontmatter schema (CFP-28 — strict)","doc section schema (CFP-28 — strict)","check-gate","ac-traceability-matrix","css structural lint (stylelint, warning-tier)","css-lint discriminating test (mutation 생존 0)"]` | 8-tuple (CFP-2782 — ADR-121 Wave 2 배포 2 lane 물리 제거로 `Verify deploy lane presence (Phase 2 wire — ADR-087 Amd 2)` context 제거 [9→8 narrowing, ADR-087 Superseded by ADR-121, gate 목적=deploy lane wiring 존재 확인 obviated → 보안 약화 아님]. CFP-2780 9-tuple 선행 — css-lint D1 게이트 required 승격, ADR-136 Amendment 5 §결정16: 메인 `css structural lint (stylelint, warning-tier)` + `css-lint discriminating test (mutation 생존 0)` 둘 다 required 등재 [hollow-gate 회피 — 메인 job 은 wrapper CSS 0 이라 구조적 always-green, 실 discriminating teeth 는 css-lint-test]. ★ job name "warning-tier" literal = cosmetic 부채 — rename 시 신 이름 7일-green 재적립 chicken-egg (ADR-130 §결정6) → rename deferred [관찰-only, 3문 게이트 미충족], ADR-136 §결정16 결정 A. ★ branch protection API 실등록 = post-merge Orchestrator 소관 [본 표 = 문서 SSOT]. CFP-2603 7-tuple 선행 [`ac-traceability-matrix`, ADR-145 §결정 3]; CFP-1808 Amendment 2 6-tuple 선행). lane 8 repo = archived (CFP-2178 S6) — 보호 규칙 잔존+동결, 활성 관리 = wrapper 단일. audit: [docs/security/branch-protection-audit.md](docs/security/branch-protection-audit.md) |

## 시각 표기
사용자 대면·문서 표기 = KST `+09:00` ISO 8601. 외부 timestamp(GitHub/git)는 원본 보존.

## opus default + ADR-141 carve-out (Amendment 1 haiku 7 + Amendment 2 sonnet 14 + Amendment 4 fable 10) (ADR-141)
codeforge family 의 **model tier = `opus` default + ADR-141 carve-out**. 3-tier 선택 기준·rate-limit fallback 은 폐기(ADR-141 §결정1/2/3; 단 fable 은 Amendment 4 로 carve-out 도입 — deprecated 아님). **frozen amendment-귀속(byte-frozen 이력, dated 결정치 그대로)**: Amendment 1 = haiku 7(외부위임·기계 워커) / Amendment 2 = sonnet **14**(중간추론) / Amendment 4 = fable 10(장수명 apex); 1M native 는 opus 기준. **별도 live-roster(reconcile 현재치)**: live roster: haiku 7 / sonnet **10** / fable 10 / opus 14 = 41 (CFP-2782 deploy 3종 제거 + IntegrationTest sonnet→fable 이전 반영 — Amendment 2 의 dated 14 는 frozen 이력이라 불변, live sonnet 은 10). **Amendment 4 fable carve-out(10 named apex 역할)**: 6 lane PL(RequirementsPL·RequirementsReviewPL·ArchitectPL·DesignReviewPL·DeveloperPL·CodeReviewPL) + ArchitectAgent(chief author) + ResearcherAgent + PMOAgent + IntegrationTestAgent. 근거 = 장수명 조율 + anti-fabrication(verify-before-trust 위반·fabricated-status·born-broken over-PASS 재발 결함을 특정 타격) — '더 똑똑해서'가 아님. **명시 제외(fable 아님)**: SecurityTestPLAgent(보안 lane — fable 안전분류기 cyber refusal 로 실가치 무력화 = 순손실 → opus 유지) / haiku 7 mechanical leaf / high-fan-out adversarial finder. **Orchestrator 모델 mandate = opus→fable(ADR-141 §결정4, 구 ADR-057 §결정1 흡수) codify + 이중성 정직 declare**: 문서 codify = fable. 단 Orchestrator 는 최상위 Claude 세션이라 모델은 사용자 launch 시점 선택 → **비-PR-enforceable**. 실 구현 = ① CLAUDE.md 정책 codify + ② 사용자 launch handoff(fable 선택, 비강제 사실). **fable Orchestrator = 정상 상태(self-refuse 대상 아님)**. **'전 에이전트 단일 opus tier'·'Sonnet/Haiku 세션 중단' 규범은 Orchestrator 세션·거버넌스 default scope 이다. carve-out non-opus(haiku 7 + sonnet 10 + fable 10) subagent 는 정상 상태이며 self-refuse 대상 아님**(#846 정산). opus rate-limit(429) 대응은 [ADR-109](archive/adr/ADR-109-in-process-429-mitigation-framework.md) 소관(fallback tier 없음 — sonnet 부활 ≠ rate-limit fallback machinery 부활). **fable-리밋 예외**: fable subagent(Amendment 4 carve-out 10 역할) 리밋 감지 시 Orchestrator 가 opus 로 fresh re-spawn 1회(Option A 즉시전환·1-hop·fresh-spawn-only) — [ADR-141](archive/adr/ADR-141-all-opus-single-tier.md) Amendment 6 (감지 SSOT = ADR-109 §결정1 Amendment 1; rate-limit *fallback* machinery[sonnet 축, dead] 부활 아님 — 별개 trigger[fable 리밋]·별개 SSOT·별개 태그 `[rate-limit-failover:fable→opus]`). 신규 agent = `model: opus` default, 단일 tier 이탈 = ADR-141 amendment 의무. 상세 = [ADR-141](archive/adr/ADR-141-all-opus-single-tier.md).

---
> 본 파일은 Orchestrator 가 매 턴 자기검열해야 하는 정책만 담는다. 레인 내부 절차·근거·이력은 각 lane plugin CLAUDE.md / 스킬 / `docs/` 가 SSOT.
