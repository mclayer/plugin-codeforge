---
adr_number: 143
title: Agent 수행 액션 렌더 줄 프리픽스 규약 (`[에이전트명] MM/DD HH:MM - 내용`) — ephemeral-UI 표시 sub-layer
status: Accepted
category: governance
date: 2026-07-05
carrier_story: CFP-2574
supersedes: []
related_adrs:
  - ADR-079  # KST timestamp display mandate — Amendment 2 (제3 ephemeral-UI render-line sub-layer EXEMPT) 동반 발의, §결정 6/8 layer resolution
  - ADR-038  # progress visualization (TodoWrite) — §결정 9 3-tier enforcement 모델 차용 + §결정 12 hook-stdout 선례 + TodoWrite 제외 Amd5 정합
  - ADR-039  # subagent default / inline whitelist — §결정 1 범위 경계 (Orchestrator inline 4종 제외) 재사용, whitelist 무변경
  - ADR-029  # sub-step stderr narration — bracket-prefix `[<lane>]` 시각 문법 선례 (신규 문법 아님)
  - ADR-119  # research-before-claims — §결정 3 허위 시각 fallback 금지 + §결정 4 검사연극(theater) 회피
  - ADR-115  # runtime hook enforcement — Amendment 1 injection 확장 base (PreToolUse gate 확장 + graceful degradation 5층 + Wave1 exit-0 불변식 계승, §결정 3 disjoint-matcher)
  - ADR-082  # write-time self-write verification / declaration-only Wave 1 — mechanical_enforcement_actions deferred-followup 동형
  - ADR-063  # marketplace atomic invariant — Phase 2 plugin.json MINOR bump sync
  - ADR-013  # dogfood-out — 본 ADR = Story §7 설계 SSOT, change-plan 면제 (ADR-127 정합)
related_concepts:
  - render-line-display-sublayer
is_transitional: false
amendment_log:
  - number: 1
    carrier_story: CFP-2587
    date: 2026-07-09
    direction: strengthen
    target: "§결정 4 (core) · §결정 5 · §결정 3 (leaf-semantics) · 비대상 (feasibility gap #1/#2)"
    summary: >-
      advisory ceiling → mechanical injection tier. description-bearing 도구(Agent/Bash)에 한해
      PreToolUse hook 이 hookSpecificOutput.updatedInput 으로 프리픽스를 기계 치환. 두 사실 전제
      (CFP-2567 실측 인용) 정정 — 전제① "PreToolUse tool_input rewrite 불가" 반증(hooks.md
      updatedInput = "replaces a tool's arguments before it runs"); 전제② "PreToolUse(Agent)
      서브에이전트 내부 미발화" = Agent-scoped 진술로 literal-true 유지, 반증 대상은 'leaf 기계주입
      불가' 결론(PreToolUse(Bash)+payload agent_type 도달로 supersede). detect-only Phase 2
      (cfp-2574-phase2-impl) = in-place 개편으로 supersede(helper = idempotency 가드로 재사용).
      Gate 검증 = feasibility spike Gate-A(Bash·토폴로지-충실) GO + Gate-B(Agent·단일-hook) GO.
    sunset_justification: >-
      N/A — 역전(§결정 4 "SecurityArch §7.1 non-mutation invariant 상속" REVERSED)은 약화가
      아니다. ADR-058 §결정 5 는 WEAKENING(forbid-scope 축소)에만 sunset_justification 의무를
      부과하나 본 amendment 는 mechanical tier ADD(capability-ADD) + forbid-scope 축소 0. REVERSE
      근거 = SecurityArch deputy 재판정 = SAFE-with-guardrails (G1 json.dumps 구조적 직렬화 /
      G2 subject sanitize ≤64·']' strip·namespace strip / G3 description-only whole-echo /
      G4 bare updatedInput = no allow-override / G5 fail-open). 역전 ≠ 약화 (forbid-scope 정의상).
related_files:
  - CLAUDE.md  # 범위① Orchestrator spawn-description 규약 directive + 전-agent behavioral note (Phase 2)
  - hooks/pretooluse-agent-spawn-gate  # 범위① description-format detect 확장 (warning-tier, exit-0-always, Phase 2)
  - scripts/lib/check_spawn_prompt_format.py  # description-format 검증 로직 확장 or sibling (Phase 2)
  - docs/orchestrator-playbook.md  # §14.11 Spawn ID 대장 인접 format 규약 절 + §14 cross-ref note (Phase 2)
  - docs/evidence-checks-registry.yaml  # spawn-description-prefix-detect warning-tier entry (Phase 2)
  - docs/inter-plugin-contracts/spawn-event-v1.md  # agent_type 어휘 SSOT (cross-ref only, 무편집)
  - docs/inter-plugin-contracts/comment-prefix-registry-v1.md  # `[lane]` GitHub Issue surface — homonym disjoint (§결정 7, cross-ref only)
mechanical_enforcement_actions:
  - action: spawn-description-prefix-inject  # (Wave-1 `spawn-description-prefix-detect` REPURPOSED — Amendment 1 CFP-2587)
    status: mechanical-injection-Phase-2  # declaration-only-Wave-1 → 기계 주입 실현 (advisory ceiling REVERSED)
    target_section: §결정 4 (Amendment 1)
    progress_note: "Amendment 1 (CFP-2587) REPURPOSE — advisory DETECT → mechanical INJECTION. 범위① (Agent spawn 헤더 `Agent.description`) + 범위② (서브에이전트 leaf `Bash.description`) 를 PreToolUse hook 의 `hookSpecificOutput.updatedInput` 으로 기계 치환 (`[<subject>] MM/DD HH:MM - <원 description>`). detect helper (`scripts/lib/check_spawn_description_prefix.py` RE_PREFIX 판정) = 폐기 아니라 **idempotency 가드로 재사용** (이미-conformant → 재주입 skip, 이중 프리픽스 차단; AC-12 판정 로직 이원화 금지). 표면① = 기존 `hooks/pretooluse-agent-spawn-gate` in-place 개편 (additionalContext(채널2 reminder) + updatedInput 을 단일 `hookSpecificOutput` 병합 — 단일 hook, multi-hook 무관). 표면② = 신규 sibling PreToolUse(Bash) inject hook (ADR-115 §결정 3 disjoint-matcher; `cross-repo-gh-safety` 확장 금지 = SRP·output-channel 붕괴). **top-level Bash (`agent_type` 부재) = EXCLUDE** (§결정 1 Orchestrator 명 절대 부재 정합). `docs/evidence-checks-registry.yaml` L3641 entry = injection 회귀 가드로 재목적 (또는 폐기). FAIL-OPEN 계승 = updatedInput 미emit → 원 description = advisory ceiling = ratchet-up (regression 아님). description 필드 없는 도구 (Read/Edit/Grep/Write) = advisory residual (mechanical 미커버). NO hard-gate — in-coverage best-effort + fail-open."
---

# ADR-143 — Agent 수행 액션 렌더 줄 프리픽스 규약 (ephemeral-UI 표시 sub-layer)

## 상태

Accepted (2026-07-05 KST) — CFP-2574 carrier. VS Code 확장(및 동류 harness UI)이 Agent 의 스폰·도구호출을 native 로 렌더하는 줄에 `[에이전트명] MM/DD HH:MM - 내용` 프리픽스를 붙이는 표시 규약 governance SSOT. 강화(ratchet↑) 방향 — 기존 규칙 없던 신규 표면에 규칙 1개 추가, 약화 surface 0. ADR-079 Amendment 2(제3 ephemeral-UI render-line sub-layer EXEMPT) 동반 발의로 KST display mandate 와 정합.

## 컨텍스트

사용자 요구(2026-07-04~05 KST, UI 샘플 라이브 렌더로 확정 — Story CFP-2574 §1 verbatim): codeforge 진행 시각화 중 **Agent 가 수행하는 액션의 description 표기**를 `[에이전트명] MM/DD HH:MM - 내용` 으로 바꾼다. 대상 UI = VS Code 확장의 액션/도구호출 렌더 줄(bold 도구명 + description 텍스트). 목적 = 화면만 훑어도 "누가 언제 무엇을 시작했는지" 를 줄 단위로 즉시 식별(glanceability).

이 렌더 줄은 **기존 8-채널 관측 경계표(playbook §15.1) 어디에도 없는 9번째 표면**이다 [verified: `docs/orchestrator-playbook.md:3855-3866` — 표 안에 "VS Code 렌더 줄" 부재]. 성격 = 비영속(git·file·ledger 미기록, 화면 렌더만) / 기계 파싱 대상 아님(사람 가독용) / granularity = per-agent. 가장 가까운 친척 = stderr narration(Tier 1, ADR-029) + TodoWrite(rendering-only, ADR-038). 실측: 이 description 문자열이 도달하는 **committed/host-local 영속 artifact = ZERO** — spawn-event-v1 은 19 enum/numeric 필드(free-text 부재) [verified: `docs/inter-plugin-contracts/spawn-event-v1.md`], §14 Lane Evidence 는 agent_id/spawned_at/returned_at/outcome, §14.11 대장은 spawn_id/agent_type/lane/spawn_at(gitignored), §0 progress gitignored. → render line 은 순수 ephemeral (persist gap#3 = zero persist path).

3 설계 난점(요구사항 lane flag → 본 ADR 해소 대상):
1. **시각원(clock source)** — harness 는 system context 로 **날짜만** 주입, 시각(HH:MM) 미주입 [verified: anthropics/claude-code #34530 Closed "not planned"; 본 세션 실측 재현 — currentDate `2026-07-04` → reminder `2026-07-05`, 둘 다 HH:MM 없음]. 실시계 read 없이는 분 단위 시각 원천 불가.
2. **강제(enforcement) 층** — description = model-authored 자유 텍스트 → 렌더 layer 값·형식·존재 기계 강제 수단 부재. 준수 = 시도 의무(advisory).
3. **ADR-079 KST 표기 규칙과의 관계** — 컴팩트 `MM/DD HH:MM`(offset·연도·초·KST 라벨 전부 생략)은 ADR-079 §결정 2 세 승인 형식(zoned `+09:00` / prose `KST` / date-only) 어디에도 불부합.

## 결정

### 결정 1 — 적용 범위 (scope) + subject 판정

- **대상 범위 (c)** = Agent 가 수행하는 모든 액션 description 줄 — ① 에이전트 스폰 최상위 헤더(피스폰 에이전트명) + ② 서브에이전트의 개별 도구호출(bash/edit/read 등) description 전부.
- **제외 1: TodoWrite 행** — 어떤 경우에도 프리픽스 부재. TodoWrite 는 native status 렌더 전용 채널(ADR-038 §결정 2 Amendment 5) + inline whitelist entry #2 — 이중 표기 금지. 구조적 exclusion.
- **제외 2: 순수 Orchestrator inline 4종**(대화 / TodoWrite / 읽기전용 Q&A 답변 / 상태 보고) — ADR-039 §결정 2 closed inline whitelist 4-entry 그대로 재사용. **whitelist 변경 0건** (본 ADR 은 whitelist 를 축소·확장하지 않고 "Agent 수행 액션 한정" 경계 정의로 참조만).
- **subject 규칙**: 프리픽스는 **그 줄이 대표하는 subject 에이전트**를 이름한다 — dispatch 를 발화한 actor 가 아니다. 스폰 헤더의 subject = 피스폰 에이전트(actor = Orchestrator) → 헤더에는 Orchestrator 가 아니라 **피스폰 에이전트명**이 붙는다. leaf 도구호출의 subject = self(그 서브에이전트 자신). **Orchestrator 이름 자체는 프리픽스에 절대 등장하지 않는다** (inline 은 비대상, spawn 헤더는 피스폰자명).
- **discriminator (기존 앵커 재사용)**: "이 액션이 프리픽스 대상인가" = "spawn 된 에이전트에 귀속되는가(agent_id 존재) 또는 Agent-spawn 헤더인가". CFP-2544 PreToolUse 가드가 Orchestrator-inline ↔ agent-수행을 구분한 agent_id presence 판별자와 동형 [verified: MEMORY `project_cfp_2544` — "agent_id 부재=차단후보 / 존재=통과"].

### 결정 2 — 포맷 (format)

- 정식 형식 = `[에이전트명] MM/DD HH:MM - 내용`.
- `[에이전트명]` = spawn-event-v1 `agent_type`(roster-derived PascalCase 역할 식별자, 예: `ArchitectAgent` / `DomainAgent` / `DeveloperAgent`) 재사용. roster 미등재 스폰 = `unknown-agent` fallback (spawn-event-v1 semi-open enum 정합) [verified: `docs/inter-plugin-contracts/spawn-event-v1.md:75,137-147`]. 신규 명명체계 신설 0.
- 날짜 구분자 = `/` (예 `07/05`). 시각 뒤 구분자 = 정확히 ` - `(공백-하이픈-공백; 이중 공백·다른 구분자 불허).
- 컴팩트 — timezone offset(`+09:00`)·`KST` 라벨·연도·초 전부 **미표기**. 컴팩트 길이 = `MM/DD HH:MM`.
- 배치 = 기존 description 본문 앞 선행(치환 아님, 본문 보존). 기존 본문이 `[...]` 로 시작해도 escape 없이 프리픽스 선행(이중 대괄호 허용).

### 결정 3 — 시각원 (clock source) = UTC+9 고정 산술

harness 가 시각(HH:MM)을 주입하지 않으므로 [verified: #34530] 시각 확보는 실시계 read 로만 가능하다. 시각원을 다음으로 **pin** 한다:

- **primary (GNU date)**: `date -u -d '+9 hours' '+%m/%d %H:%M'` — UTC 를 읽어 +9시간 산술 후 컴팩트 포맷.
- **portable fallback (Python)**: `python3 -c "import datetime;print((datetime.datetime.utcnow()+datetime.timedelta(hours=9)).strftime('%m/%d %H:%M'))"`.
- **FORBID machine-local `date`** (offset 무명시 로컬) — consumer 가 UTC/US 타임존이면 KST 아닌 값 산출. wrapper-canonical KST 보장 불가.
- **FORBID `TZ=Asia/Seoul date`** — Windows Git Bash 는 `TZ=Asia/Seoul` 을 무시하고 `+0000` 반환 [verified: 실측] → portable KST 보장 실패. tzdata 의존 대신 **UTC+9 고정 산술**(Korea 고정 offset·DST 영구 부재 invariant 로 정당)만 채택.
- **주체·정확도 비대칭** (요구사항 lane PL 권고 반영):
  - **헤더① = dispatch-time stamp** — spawner 가 스폰 시점에 1회 stamp. 단발 stamp 라 자연스러움.
  - **leaf② = coarse turn-anchor** — 해당 turn 최초 산출 KST 를 재사용. **정확도 요구를 명시적으로 하향** — "수행 시작 = description 작성 시점 KST **근사**" 이지 exact per-call HH:MM 아님. 매 도구호출마다 `date` 강제(재귀·비용 폭증) 회피. 정직: description 은 도구 실행 *전* authored → 렌더 시각 = "작성 시각 ≈ 시작 시각" 근사.

### 결정 4 — enforcement = ADVISORY CEILING (advisory 조합이 상한)

ADR-038 §결정 9 3-tier 모델((a) physical CI/git hook / (b) startup-hook / (c) runtime advisory)을 SSOT 로 차용한다. 범위별 강제 상한이 비대칭이다:

- **범위① (spawn 최상위 헤더)** — 유일 mechanical lever = **PreToolUse(Agent) hook**. 기존 `hooks/pretooluse-agent-spawn-gate` → `scripts/lib/check_spawn_prompt_format.py` 가 이미 `tool_input.prompt` 4-block 을 검사하며, 동일 parse dict 의 `tool_input.description` 은 추가 fetch 없이 readable [verified: Mapper `:82-99`]. 이를 **description-format DETECT** 로 확장한다 — **warning-tier, exit 0 always, NO rewrite/NO mutation/NO timestamp injection** (SecurityArch §7.1 non-mutation invariant 상속: PreToolUse 는 tool_input 을 읽되 되쓰지 않고, exit code advisory-only). CFP-2567 실측 정합 — detect-only, 입력 rewrite 불가.
- **범위② (서브에이전트 leaf 도구호출)** — PreToolUse(Agent) 는 서브에이전트 **내부** 도구호출에 발화하지 않고, description 은 ephemeral(scan target 파일 부재) → **grep-lint 구조적 불가**. 강제 상한 = **prompt-mandate + 세션시작 리마인더 advisory 조합**. 준수 = 시도 의무(non-skippable attempt / non-blocking, ADR-038 §결정 7·8 attempt-obligation 상속).
- **theater 금지 (ADR-119 §결정 6)**: "100% 기계 강제" / "hard-gate" 서술을 **금지**한다. advisory 조합이 곧 강제 상한(ceiling)임을 정직하게 명문화한다. 실 강제력은 (a) 범위① warning-tier detect + (b) 범위② prompt/리마인더 attempt 조합에서 나온다 — 그 이상을 참칭하지 않는다.

### 결정 5 — 주입점 (injection point)

- **primary reach = CLAUDE.md directive** — CLAUDE.md 는 project-instructions 로 관측된 에이전트에 in-context 로 주입된다 [verified-for-observed: 본 설계 lane 세션도 CLAUDE.md 수신]. **전 sub-agent 예외 없이 auto-inject 되는지는 [hypothesis]** — 플랫폼 의존이라 universal 단정 회피(over-claim 금지). 범위① Orchestrator spawn 규약은 CLAUDE.md "작업 규칙" 절 directive 로 착지.
- **보강 = 세션시작 리마인더** — ADR-038 §결정 12 hook-stdout 주입 선례(SessionStart hook 이 컨텍스트로 값·규약 주입) 차용. advisory 반복 스킵 시 hook-tier 격상 전례 답습.
- **MINIMAL per-agent** — 필요 시 최소 behavioral 주입만. **per-agent 45파일 직접 편집 지양** (drift 표면).
- **shared-base 편집 = INEFFECTIVE** — `plugins/codeforge-review/templates/review-pl-base.md` / `plugins/codeforge-requirements/templates/recheck-receiver-base.md` 는 참조-time SSOT 이고 spawn 시 자동 로드 안 됨. agent 조립기 `overlay/hooks/merge.py:190-207` 는 core body + overlay body 만 합성 — base 주입 경로 자체 부재 [verified: Mapper]. shared-base 로 행동 주입 시도 = 무효.

### 결정 6 — ADR-079 관계 (제3 ephemeral-UI 표시 sub-layer, EXEMPT)

- render line = **제3 ephemeral-UI display sub-layer**로 신설, ADR-079 §결정 2 zoned-offset 의무에서 **EXEMPT**. (동반: ADR-079 Amendment 2 — 아래 §결과 참조).
- **거버넌스 관할(jurisdiction) framing (additive, NOT weakening)**: ADR-079 §결정 2 가 display layer 로 명시 열거한 "comment prefix" = **GitHub Issue comment prefix** (comment-prefix-registry `ADR-079:122` 결속)로, VS Code render line 과는 **다른 committed surface**. §결정 2 의 규칙은 이 신규 표면에 **도달한 적이 없다** → 새 표면에 규칙을 추가하는 것은 **additive/strengthen**이지 기존 규칙 약화가 아니다. 실측: persist gap#3 = zero persist path (render line 은 파일 미저장 ephemeral) → additive 논거 사실 우위.
- **anti-weakening 명시**: (i) §결정 2 영속 zoned scope 0건 축소 (ii) §결정 6 forward-only 무변경 (iii) §결정 7 consumer tz override 미허용 — 오히려 §결정 3 UTC+9 고정 산술이 §결정 7 wrapper-canonical KST 를 강화 인용.

### 결정 7 — homonym lexicon (동형 표면 명시)

- `[에이전트명]` (agent-role 식별자, VS Code render surface) ↔ comment-prefix `[lane]` (lane/phase 이름, GitHub Issue comment surface) = **표면형(대괄호 프리픽스) 동일 / 의미 disjoint** homonym.
- 두 표면은 disjoint(VS Code UI 렌더 줄 ↔ GitHub Issue 코멘트 본문)라 실제 충돌 없음. cross-ref 유지:
  - `[에이전트명]` 값 SSOT = spawn-event-v1 `agent_type` (roster-derived + unknown-agent).
  - `[lane]` 값 SSOT = comment-prefix-registry-v1 (GitHub Issue surface, entry 추가 불요) [verified: `comment-prefix-registry-v1.md:59,66-67,70`].
  - §14 Lane Evidence / §14.11 Spawn ID 대장 = 인접 committed layer(다른 surface).
- application-BC lexicon 의 homonym entry(`[에이전트명]` ↔ `[lane]`) 반영은 **후속(deferred)** — 개념 정착 후 DomainAgent write.

### 결정 8 — persist-guard (조건부 layer 재판정)

- render line description 은 **committed/host-local 영속 artifact 로 persist/export 금지**. 실측 현 상태 = zero persist path (§컨텍스트).
- **조건부 가드**: 만약 미래에 render line 을 파일·로그·transcript export 로 persist/export 하는 경로가 도입되면 — 그 export 는 **ADR-079 §결정 2 zoned scope 로 재분류**되며(offset·연도 모호성 부활), layer 재판정을 요한다. 컴팩트 offset-less 표기의 정당성은 "ephemeral 화면 전용 + Korea 고정 +9 invariant" 에 한정된다.

### 문서 예시 규칙 (doc-example rule)

본 규약을 ADR·playbook 등 lint scope(`check_kst_timestamp.py` KST_SCOPE_GLOBS = CLAUDE.md / playbook / ADR-*.md / retros) 문서에 기술할 때:

- 컴팩트 `MM/DD HH:MM` 예시는 **lint-inert** — `KST_TS_RE` 는 full `\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(Z|[+-]\d{2}:\d{2})` 를 요구하므로(연도·T·초·offset 필수) 컴팩트형은 구조적 non-match [verified: `scripts/lib/check_kst_timestamp.py:32`]. → **자유 배치** 가능.
- full-zoned **비-KST 부정 예시**(예: 아래처럼 `-07:00` offset)는 `scan_file` 이 fenced code block(` ``` `/`~~~`)·blockquote 를 skip 하므로 [verified: `check_kst_timestamp.py:132-151`] **반드시 code-fence 안**에 둔다:

```
# 부정 예시 (weakening 시나리오 — code-fence 안이라 lint-inert):
2026-07-05T14:30:00-07:00   # 비-KST offset — persist 되면 §결정 8 재판정 대상
```

- `hotfix-bypass:kst-timestamp-display` 우회 불요 — 컴팩트 예시는 구조적 미매칭이고 부정 예시는 fence 안이라 애초에 스캔 밖.

### advisory deny-scan hardening (SecurityArch, NON-blocking)

- 프롬프트-mandate·규약 문안에 1줄 advisory 병기: **"프리픽스 3요소(에이전트명/시각/내용)에 secret·token·절대경로·자격증명 임베드 금지 — `내용`은 액션 요약만."** `내용` free-text 는 pre-existing surface(위협 표면 NEUTRAL, 증가 아님)이고 본 규약은 bounded enum+timestamp 만 prepend 하므로 신규 trust boundary 0. NON-blocking guidance.

## 결과

- **신규 표면에 규칙 1개 추가** — 기존 8-채널 경계·ADR-038 TodoWrite·ADR-039 whitelist·ADR-079 zoned scope 무변경. 강화(ratchet↑) 방향, 약화 surface 0. `is_transitional: false` → sunset_justification N/A (ADR-058 §결정 5 강화 방향 면제).
- **ADR-079 Amendment 2 동반 발의** — 제3 ephemeral-UI render-line sub-layer 를 §결정 2 영역 표에 additive row 로 추가(compact `MM/DD HH:MM`, offset 생략 ≡ KST 고정 §결정 7 anchor) + 조건부 persist-guard. `direction: strengthen`, sunset_justification N/A. §결정 2 본문 zoned scope 0건 축소.
- **enforcement = declaration-only Wave 1** — `mechanical_enforcement_actions[0]` = `spawn-description-prefix-detect`(warning-tier, Phase 2 wire deferred). 범위② leaf 는 non-mechanical(advisory) 선언. Phase 1 신규 required check 0 / branch protection 6-tuple 무변경.
- **change-plan 면제** (ADR-013 dogfood-out + ADR-127 정합, ADR-140 선례 동형) — wrapper-self governance codify 는 docs/change-plans/ 산출 안 함. 본 ADR §결정 + Story §7 이 설계 SSOT 를 온전히 carry.
- **비용**: 신규 spawn 0 / 신규 required 게이트 0. Phase 2 = 기존 hook 확장 + CLAUDE.md directive + 리마인더 + registry warning entry (per-agent 45파일 미편집).

## 비대상 (out-of-scope)

- **ADR-038 / ADR-039 / ADR-042 §15 observability boundary 무변경** — 본 요구는 measurement(Tier-3 회계) 아닌 표시-only → ADR-042 amendment 불요. TodoWrite 제외 경계 유지 의무.
- **VS Code 확장 렌더 실동작·per-tool-call hook 주입 신뢰성** — 설계 feasibility 후보(gap #1/#2), 필요 시 on-demand deep-research. 본 ADR 은 규약·layer·강제 상한만 codify.
- **미/유럽 consumer tz override / locale 변환** — 별도 CFP (ADR-079 §결정 7 정합).
- **application-BC lexicon homonym entry 실 write** — deferred (개념 정착 후 DomainAgent).
- **Phase 2 구현**(hook 확장·CLAUDE.md directive·리마인더·registry entry·plugin.json bump) — 본 ADR = Phase 1 설계 SSOT.

## 해소 기준

N/A — permanent policy (`is_transitional: false`, ADR-058 §결정 7 governance presumption). ephemeral-UI 표시 규약은 sunset 대상 아닌 영구 표시 governance. 약화 방향 amendment(sub-layer scope 축소 / KST anchor 제거 / persist-guard 해제)는 ADR-058 §결정 5 `sunset_justification` 의무로 차단(ratchet — 강화 방향만).

## Amendment 1 (CFP-2587) — advisory ceiling → mechanical injection

> Carrier: CFP-2587 (운영자 결정 2026-07-09 = injection 전환·supersede). Direction = **strengthen (ratchet↑)**, `is_transitional` 무변경(false). 본 절은 위 §결정 원문을 **삭제하지 않고 amend** 한다 — 각 §결정의 무변경/정정/전환 상태를 decision-by-decision 으로 기재. 설계 SSOT = Story CFP-2587 §7 (특히 §7.8 ADR-143 Amendment 1 draft). Gate 검증 = feasibility spike **Gate-A(Bash·토폴로지-충실) GO + Gate-B(Agent·단일-hook) GO** [verified: `tests/spike/cfp-2587-updatedinput-honor/RESULTS.md` — CLI 2.1.204/Windows 11, #15897 `updatedInput`-drop 미재현, bare/allow updatedInput 양쪽 honor, BARE01 = partial updatedInput hard-fail → whole-echo mandatory].

### A1.0 핵심 전환 (mechanism)

§결정 4 의 **advisory ceiling** 을 description-bearing 도구(`Agent.description` + `Bash.description`)에 한해 **mechanical injection tier** 로 상향한다. PreToolUse hook 이 dispatch 시점 로컬 wall-clock 으로 KST `MM/DD HH:MM` 를 생성(`kst_render_stamp.py`, UTC+9 고정 산술 — §결정 3 재사용)하고 `hookSpecificOutput.updatedInput` 으로 `[<subject>] MM/DD HH:MM - <원 description>` 를 기계 치환한다. `updatedInput` = "replaces a tool's arguments before it runs" [source: https://code.claude.com/docs/en/hooks.md].

- **표면① `Agent.description` 스폰 헤더** — subject = `tool_input.subagent_type`(피스폰 에이전트). 기존 `pretooluse-agent-spawn-gate` in-place 개편(단일 hook — multi-hook 무관).
- **표면② `Bash.description` 서브에이전트 leaf** — subject = payload `agent_type`(self, 서브에이전트 내부 호출에 present). 신규 sibling PreToolUse(Bash) inject hook(ADR-115 §결정 3 disjoint-matcher).
- **소스-분기(SOURCE-BRANCHING)가 급소**: 헤더 = `subagent_type`, leaf = payload `agent_type`. 혼용 시 §결정 1 "Orchestrator/dispatcher 명 절대 부재" 불변식 붕괴.

### A1.1 정직한 전제 정정 (3-stage — history rewrite 아님, ADR-119)

§결정 4 가 근거로 인용한 두 사실 전제(CFP-2567 실측)를 다음 **3-stage** 로 정정한다. **retro-blame 아님** — measurement-time-valid → 그 사이 플랫폼 능력 추가 → 현행 공식 문서 supersede:

1. **measurement-time-valid**: CFP-2567 실측("detect-only, 입력 rewrite 불가")은 측정 시점 관측으로 valid 였다.
2. **capability-added (전제② 한정 실증)**: `agent_id`/`agent_type` = v2.1.69 신설 [best-evidence 2차 source: https://claudefa.st/blog/guide/changelog — "Added agent_id and agent_type to hook events for subagents and --agent"]. 측정 시점 < v2.1.69 였다면 "subagent 정체 불가" 관측이 자연.
3. **superseded (현행 공식 문서 = PRIMARY)**: 현행 hooks.md 가 `PreToolUse.updatedInput` rewrite + 서브에이전트 내부 `agent_type` payload 를 명문화 [source: https://code.claude.com/docs/en/hooks.md]. 구현 시점 Claude Code 버전 재검증 통과(spike CLI 2.1.204).

- **`updatedInput` 정밀 도입 버전 = abstain (문서 silent)** [verification-out-of-scope: hooks.md 버전주석 부재]. best-evidence(현행 hooks.md 명문화 + changelog v2.1.85 `updatedInput` AskUserQuestion 경로)로 현 CLI 이전부터 live 확립. **capability-added 메커니즘은 전제②(agent_type)에만 실증 — FACT1(`updatedInput`)로 전이 금지**(과일반화 방지).

**전제② framing (flat "반증" 금지 — ADR-119 정직성)**: 원문 §결정 4 "PreToolUse(Agent) 서브에이전트 내부 미발화" = **Agent-scoped 진술로 literal-true 유지**. 반증 대상은 그것이 아니라 **"leaf 기계주입 불가"라는 결론** — Bash leaf 호출은 PreToolUse(**Bash**)를 트리거하고 서브에이전트 내부에 `agent_type` 이 present 하므로 [verified: spike `fixtures/bash-in-subagent.json` — `agent_type="general-purpose"`, `agent_id` present] **PreToolUse(Bash)+payload `agent_type` 도달로 supersede**. 즉 PreToolUse(Agent) 미발화 진술은 참이되, leaf 주입 불가 결론이 틀렸다.

**#15897 (capability ≠ defect-free)**: `updatedInput` 능력이 무결은 아니다 — multi-hook PreToolUse 동시 실행 시 `updatedInput` drop [source: https://github.com/anthropics/claude-code/issues/15897 — title "…does not work when **multiple PreToolUse hooks are executed**", status **closed-as-not-planned**]. **트리거 = multi-hook(버전 아님), status = closed-as-not-planned → 구조적·영구 제약**(upstream fix 대기 금지, 설계로 우회). Bash matcher 는 이미 3 sibling deny-gate 상존 → injection 추가 시 multi-hook 조건 구조적 상시. **완화 = fail-open**(updatedInput drop = 프리픽스 소실 = 원 description = advisory ceiling = ratchet-up, wrong-value 아님)이지 upstream fix 아님. spike 가 프로덕션 4-hook 토폴로지에서 drop 미재현 확인(GO), 단 fail-open 이 safety net 으로 잔존하는 조건.

### A1.2 decision-by-decision

- **§결정 1 (scope/subject)** — **UNCHANGED (LOAD-BEARING)**. subject 분기(헤더=피스폰, leaf=self, Orchestrator 명 절대 부재)가 injection 정확성의 급소이므로 원문 그대로 구속.
- **§결정 2 (format)** — **UNCHANGED**. `RE_PREFIX = ^\[[^\]]{1,64}\] \d{2}/\d{2} \d{2}:\d{2} - \S` 를 injection 의 **idempotency 판정**으로 재사용(이미-conformant → 재주입 skip → 이중 프리픽스 미발생). 주입 문자열 포맷 동일.
- **§결정 3 (clock)** — SOURCE **UNCHANGED**(UTC+9 고정 산술, `kst_render_stamp.py`, machine-local `date`/`TZ=Asia/Seoul` FORBID) / **leaf-SEMANTICS CORRECTED**: "coarse turn-anchor" → **"per-dispatch stamp"**(AC-15). hook 이 dispatch 마다 실시각 stamp 하므로 **서브에이전트가 `date` 를 호출할 필요 없음** → turn-anchor down-grade 전제 자체가 dissolve. per-dispatch stamp 는 zero-persist-path 와 정합(turn-anchor 캐시 = 신규 persist path = ephemeral 정체성 붕괴 → 채택 불가).
- **§결정 4 (advisory ceiling)** — **AMENDED (core)**. description-bearing 도구(Agent/Bash)에 대해 mechanical injection tier(PreToolUse `hookSpecificOutput.updatedInput`). "**SecurityArch §7.1 non-mutation invariant 상속**" 조항 = **REVERSED**(SecurityArch deputy 재판정 → SAFE-with-guardrails G1-G5, §A1.3). **theater-ban 조항(ADR-119 §결정 6)은 보존** — §A1.4.
- **§결정 5 (injection point)** — **AMENDED**. primary reach = CLAUDE.md directive → **PreToolUse hook `updatedInput`**. CLAUDE.md directive 는 **삭제 아님** — 재문안(범위①/② mechanical injection 반영) + description-less 도구(Read/Edit/Grep/Write) advisory residual 을 carry(§A1.4).
- **§결정 6 / §결정 7 / §결정 8** — **UNCHANGED**. mechanical injection = **저작 주체 변경(model→hook)일 뿐 신규 persist/export 경로 0** → §결정 8 persist-guard 미발동 → render line 은 여전히 순수 ephemeral → **ADR-079 Amendment 2 정정 UNNEEDED**(ADR-079 over-amend 는 error). §결정 7 homonym 관계 불변(두 표면 disjoint).
- **Ratchet 방향** — **STRENGTHEN**. `sunset_justification` = **N/A**(ADR-058 §결정 5 는 WEAKENING 만 justification 의무 — mechanical tier 는 capability-ADD, forbid-scope 축소 0; amendment_log entry 에 REVERSED 정당화 기록). mechanical tier = ADR-038 §결정 9 3-tier 모델 안의 **사전 선언된 tier 상승**(신규 axis 아님) — 정밀 표기는 §A1.5. `is_transitional: false` 유지.

### A1.3 mutation 안전 계약 — STRIDE-LITE (SecurityArch 재판정: SAFE-with-guardrails)

§결정 4 "non-mutation invariant 상속" REVERSE 의 근거 = 5 guardrail(G1-G5)로 injection hook 의 trust boundary 를 bound. **역전 ≠ 약화**(forbid-scope 정의상 — capability-ADD, §A1.5).

- **G1** JSON 구조적 직렬화(`json.dumps(dict)`, f-string/template 금지) — 적대적 agent_type 자동 escape.
- **G2** subject sanitize: namespace-strip(`my-plugin:reviewer`→마지막 `:` 뒤) → `[`/`]` strip → ≤64 truncate → empty→`unknown-agent`.
- **G3** description-only mutation(원 tool_input **whole-echo** + description 키만 prepend; 필드 add/rename/delete 0).
- **G4** bare `updatedInput`(`permissionDecision` 무 → sibling deny allow-override 불가, AC-20).
- **G5** fail-open(mutation = stdout JSON; 실패 시 updatedInput 미emit + exit 0 = 원 description).

| STRIDE 범주 | 위협 시나리오 (이 hook) | 완화 guardrail | 판정 |
|---|---|---|---|
| **S**poofing | 적대적 `agent_type` 값이 타 에이전트 사칭 | G2 (subject sanitize) | **N/A** — bounded enum(agent_type semi-open) + timestamp, no new trust boundary. subject = 표시 라벨이지 인증 주체 아님 |
| **T**ampering | `updatedInput` 이 원 tool_input 인자 변조·파손 | G1 + G3 | **완화됨** — description 키만 prepend, 나머지 whole-echo 보존. spike BARE01 = partial updatedInput hard-fail → whole-echo mandatory (T-1) |
| **R**epudiation | 감사·로그 위조 | — | **N/A** — bounded enum + timestamp, no new trust boundary; ephemeral display sub-layer, zero persist path, 감사 artifact 미생성 (§11 N/A) |
| **I**nfo disclosure | 프리픽스에 secret/token/절대경로 임베드 | G3 | **N/A** — hook 저자 바이트 = bounded enum + timestamp (secret-incapable); `<내용>` free-text = model-authored pre-existing surface(위협 NEUTRAL). 신규 기계적 secret-scan 미추가(ADR-119 theater 회피) |
| **D**oS | hook 실패가 tool 실행 차단(self-DoS) | G5 (fail-open) | **N/A** — bounded enum + timestamp, no new trust boundary; fail-open 이 self-DoS 원천 배제; 프리픽스 = cosmetic, security control 아님 |
| **E**levation | `updatedInput` 이 sibling deny-gate allow-override | G4 (bare updatedInput) | **N/A** — no `permissionDecision` → denied call 승격 불가 (AC-20). spike ALLOW01 = allow 도 honor 하나 설계는 bare 채택 |

- **deny-scan applicability**: 이 hook 에 신규 기계적 secret-scan **미추가**(hook 저자 = secret-incapable). ADR-143 advisory deny-scan hardening 은 **model-authored content advisory 로 잔존**하되 hook 바이트로 확장 안 함(확장 = ADR-119 theater). **VERDICT = flip 은 SAFE-with-guardrails.**
- **§6 fact1 over-claim 정정**: `{permissionDecision:"allow", updatedInput:{…}}` 형태 JSON 예시는 **reconstructed/illustrative (문서 미제시)** — "PreToolUse allow+updatedInput 조합 = doc-silent, #15897 참조". **설계는 이에 무의존**(G4 = bare updatedInput). spike 는 bare(GATEA001)·allow(ALLOW01) **양쪽 honor** 확인 → 설계 채택 = bare.

```
# reconstructed/illustrative — 공식 문서 미제시 (PreToolUse allow+updatedInput 조합 = doc-silent, #15897 참조):
{"hookSpecificOutput":{"hookEventName":"PreToolUse","updatedInput":{"command":"…","description":"[DeveloperAgent] 07/09 18:30 - build injected description"}}}
# ↑ 설계는 permissionDecision 무(bare) 채택 (G4). 이 예시는 능력 설명용이지 설계 의존 아님.
```

### A1.4 theater-ban 보존 (ADR-119 §결정 6) + §결정 5 재문안 잔여

- **cover = description-bearing 도구 한정**(Agent/Bash). **description-less 도구(Read/Edit/Grep/Write) = 정직한 advisory-residual**(기존 prompt-mandate 잔존) / OOS — mechanical 미커버.
- **top-level Bash(Orchestrator 직속, `agent_type` 부재) = EXCLUDED** [verified: spike `fixtures/bash-top-level.json` — agent_type absent] → §결정 1 "Orchestrator 명 절대 부재" 정합.
- **fail-open 보존**: mechanical = in-coverage best-effort + fail-open 이지 hard-gate 아님.
- **"100% 기계강제" / "hard-gate" 서술 FORBID** 유지 — 실 강제력 = in-coverage injection + fail-open + description-less advisory residual 조합. 그 이상 참칭 금지.
- **§결정 5 CLAUDE.md directive**: 삭제 아님 — 재문안(범위① advisory→mechanical, 범위② Bash mechanical + top-level Bash caveat) + description-less advisory residual carry. 매턴 self-check note = mechanical injection 의 backstop 으로 잔존(hook 이 주된 강제).

### A1.5 ADR-038 tier 정밀화 · §11 N/A · supersede

- **ADR-038 tier framing (정밀)**: 본 mechanical tier = **runtime-mechanical enforcement**(기존 (c) runtime-advisory 대비 **강화**; CI/git physical (a)와 **별개**). **"(a) physical 실현"으로 표기 금지** — mechanical injection 은 런타임 hook 강제이지 CI/git physical 게이트가 아니다. ADR-038 §결정 9 3-tier 모델 안의 사전 선언된 tier 상승(c 대비 강화)이며 신규 axis 아님.
- **§11 데이터 마이그레이션 = N/A** (영속 0 · 스키마 0 · 순수 ephemeral display sub-layer; §11.6 idempotency = §7.4 ACTIVE — RE_PREFIX 재주입 가드 `f(f(x))=f(x)` + 빈/whitespace skip).
- **supersede**: detect-only Phase 2(`cfp-2574-phase2-impl`)는 **in-place 개편으로 대체**(브랜치 머지 아님 — content 는 이미 origin/main 착지, squash #2578; 브랜치 = stale leftover 폐기). detect helper(RE_PREFIX 판정) = 폐기 아니라 idempotency 가드로 재사용. plugin.json MINOR bump + 6 sub-plugin marketplace atomic(ADR-063). 비대상 §"per-tool-call hook 주입 신뢰성(gap #1/#2)" = spike Gate-A/B GO 로 해소.

## 관련 파일

- [ADR-079](ADR-079-kst-timestamp-display-mandate.md) — Amendment 2 (제3 ephemeral-UI sub-layer EXEMPT) 동반, §결정 6/8 layer resolution
- [ADR-038](ADR-038-progress-visualization-todowrite.md) — §결정 9 3-tier enforcement 모델 + §결정 12 hook-stdout 선례 + TodoWrite 제외 Amd5
- [ADR-039](ADR-039-orchestrator-subagent-default-for-codeforge-modification-work.md) — §결정 1 inline whitelist 4-entry 범위 경계 (무변경)
- [ADR-RESERVATION](ADR-RESERVATION.md) — row 143 carrier_story = CFP-2574 (dual-key registry leg)
- `CLAUDE.md` — 범위① spawn-description directive + 전-agent behavioral note (Phase 2)
- `hooks/pretooluse-agent-spawn-gate` + `scripts/lib/check_spawn_prompt_format.py` — 범위① description-format detect 확장 (Phase 2)
- `docs/orchestrator-playbook.md` — §14.11 인접 format 규약 절 + §14 cross-ref (Phase 2)
- `docs/evidence-checks-registry.yaml` — spawn-description-prefix-detect warning-tier entry (Phase 2)
- `docs/inter-plugin-contracts/spawn-event-v1.md` — `agent_type` 어휘 SSOT (cross-ref, 무편집)
- `docs/inter-plugin-contracts/comment-prefix-registry-v1.md` — `[lane]` homonym disjoint surface (cross-ref, 무편집)
