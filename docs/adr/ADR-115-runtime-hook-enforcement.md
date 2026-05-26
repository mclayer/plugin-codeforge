---
adr_number: 115
title: Runtime hook enforcement policy — PreToolUse(Agent) blocking + UserPromptSubmit/Stop/SubagentStop non-blocking
status: Accepted
category: governance
date: 2026-05-26
carrier_story: CFP-1740
parent_epic: CFP-1740
supersedes: null
amends: null
amendments: []
amendment_log: []
is_transitional: false
mechanical_enforcement_actions:
  - runtime-hook-presence
related_adrs:
  - ADR-039  # §결정 9 deferred follow-up 직접 carrier — Orchestrator runtime enforcement (turn-time 행동 강제) 영역
  - ADR-025  # Phase 2 — policy_violation_subdecision 발화 채널 차단의 mechanical 보강 (PreToolUse deny 로 spawn-format 위반 차단)
  - ADR-038  # Amendment 1 §결정 8 — non-skippable attempt / non-blocking fail layered defense (graceful degradation 패턴 precedent)
  - ADR-040  # Amendment 3 §결정 7.D — mechanical_enforcement_actions[] 의무 self-application + worktree convention
  - ADR-060  # evidence-enforceable promotion framework — warning → blocking 승격 gate (PR ≥ 20 + failure = 0 + sibling merged)
  - ADR-061  # Amendment 3 — Python script-writing convention + CodeQL ReDoS line-by-line parse mandate (check_spawn_prompt_format.py 적용)
  - ADR-064  # §결정 9 stop-time + §결정 3 question quality 3-check — Stop/UserPromptSubmit hook 의 mechanical layer
  - ADR-070  # Codex verify-before-trust — SubagentStop ledger 위반 기록 대상
  - ADR-071  # Orchestrator ↔ user dialog convergence — §결정 17 back-translation gate (SubagentStop ledger 대상) + UserPromptSubmit dialog reminder
  - ADR-073  # verify-before-assert — Amendment 2 parallel-work-sentinel polling (UserPromptSubmit reminder 대상) + Amendment 15-16 SHA pin / drift detection
  - ADR-082  # Amendment 17 sub-scope 1-G amendment-slot pre-reservation (본 ADR 자체가 1-G META applied — reservation row 115 pre-claim 후 file write)
  - ADR-043  # stop-event-v1 Allow-list amendment 판정 (Story-4 carrier — hook_source/hook_decision field MINOR bump 정합)
  - ADR-068  # boundary completeness 6-invariant + I-5 dimensional empirical grounding (hook latency / session burn empirical citation)
related_files:
  - hooks/hooks.json                                          # 4 신규 hook entry append (UserPromptSubmit / PreToolUse:Agent / Stop / SubagentStop)
  - hooks/run-hook.cmd                                        # polyglot dispatcher (superpowers 5.1.0 MIT, 미변경 — entry router 재사용)
  - hooks/userprompt-submit                                   # 신규 extensionless polyglot (overlay/hooks/userprompt-reminder.{sh,ps1} wrapper-root 승격/미러)
  - hooks/pretooluse-agent-spawn-gate                         # 신규 extensionless polyglot — 유일 blocking hook
  - hooks/stop                                                # 신규 extensionless polyglot — non-blocking ledger
  - hooks/subagent-stop                                       # 신규 extensionless polyglot — non-blocking ledger
  - scripts/lib/check_spawn_prompt_format.py                  # ADR-061 Python lib (line-by-line parse, heredoc 금지)
  - scripts/check-runtime-hook-presence.sh                    # thin bash wrapper — evidence-checks-registry warning-tier
  - templates/github-workflows/runtime-hook-presence.yml      # workflow 신설
  - docs/inter-plugin-contracts/stop-event-v1.md              # v1.0 → v1.1 MINOR (hook_source / hook_decision field)
  - docs/inter-plugin-contracts/label-registry-v2.md          # `hotfix-bypass:runtime-hook-presence` family member append
  - docs/evidence-checks-registry.yaml                        # 4 entry (runtime-hook-{userprompt,pretooluse-agent,stop,subagentstop}-presence)
  - docs/consumer-guide.md                                    # hook 등록 안내 + one-channel rule
  - docs/orchestrator-playbook.md                             # §1.1 runtime hook dispatcher sub-section
  - CLAUDE.md                                                 # "세션 개시 의무" + "오케스트레이션 규칙" reference 갱신
  - overlay/hooks/userprompt-reminder.sh                      # consumer overlay — wrapper-root 승격 후 deprecated grace
  - overlay/hooks/userprompt-reminder.ps1                     # consumer overlay — wrapper-root 승격 후 deprecated grace
---

# ADR-115 — Runtime hook enforcement policy (PreToolUse(Agent) blocking + UserPromptSubmit/Stop/SubagentStop non-blocking)

## 상태

Accepted (2026-05-26 KST) — Epic CFP-1740 carrier_story. ADR-039 §결정 9 deferred follow-up (Orchestrator runtime enforcement, turn-time 행동 강제 공백) 영역의 **직접 carrier**. ADR-038 Amendment 1 §결정 8 (non-skippable attempt / non-blocking fail) layered defense 패턴의 runtime hook 확장 적용. declaration-only Wave 1 (ADR-070 §D5 / ADR-082 §결정 6 retain pattern 답습 — 4 hook entry registration + warning-tier `runtime-hook-presence` lint = Wave 1, blocking 승격 = ADR-060 evidence-gate 후 별 follow-up). is_transitional: false permanent governance ratchet (ADR-058 §결정 5 정합, §결정 7 보안 ADR default presumption false 정합).

## 컨텍스트

### 1. 기존 정책의 turn-time enforcement 공백

codeforge 는 규칙의 mechanical enforcement 를 거의 전부 **PR-time GitHub Actions lint (사후)** 로만 수행한다. Orchestrator 가 매 turn 실시간으로 하는 3 행동 — **질문 발화 / subagent spawn / turn 종료** — 은 "behavioral directive only, turn-final hook 부재 platform 한계" 라는 명분으로 mechanical enforcement 가 0건이었다 (ADR-064 §결정 9 stop-time + §결정 3 question quality / ADR-070 verify-before-trust / ADR-071 dialog convergence 본문 안에 "mechanical enforce 불가" 명시).

이 공백은 다음 3 결핍을 낳았다:
1. **사후 검출 only** — PR open 후에야 lint 가 위반을 잡으므로, turn 안에서 발생한 행동 위반 (잘못된 spawn-format / 불필요한 질문 발화 / stop-time 정리 누락) 은 turn 시점에 차단할 수단이 없었다.
2. **turn-time 행동 규칙의 mechanical enforcement 0건** — ADR-064 §결정 9 question quality 3-check, §결정 9 stop-time 정리, ADR-070 verify-before-trust 등이 전부 "behavioral directive only" 로 명시되어 있었다.
3. **미검증 가정** — "turn-final hook 부재" 주장 자체가 실제 테스트 0건의 미검증 가정이었다 (CFP-1740 spec §3 verify 결과 falsify).

### 2. 검증 결과 — 공식 hooks reference + GitHub issue verify 완료

CFP-1740 spec §3 verify-before-trust 결과 (ADR-070 §결정 D1 사용자 발화 sub-source 답습):

| mechanism | verify 결과 | 출처 | 본 ADR 적용 |
|---|---|---|---|
| **PreToolUse (matcher: "Agent")** | spawn 차단의 정석 — `permissionDecision: "deny"` 공식 지원 | code.claude.com/docs/en/hooks | **유일 blocking hook** — 실제 차단 |
| SubagentStart | **observability-only** — 차단 불가 | 공식 hooks reference | 사용 안 함 |
| **Stop / SubagentStop** | plugin 배포 경로 **block(continue) 깨짐** + false-positive **session burn 50분** + decision reason **Claude 미전달 (user only)** | GitHub #10412 (CLOSED) + #55754 | **block 금지** — ledger 기록 + 경고만 |
| **UserPromptSubmit** | stdout context 매 turn 주입 확정 | 공식 hooks reference | non-blocking reminder |

### 3. 가정 falsify — hook 자체는 작동 입증

과거 실패 (CFP-375 / CFP-385) 는 **runtime advisory tier** 였고, **SessionStart hook tier (CFP-500, ADR-038 Amendment 2)** 로 해결되었다 = hook 자체는 작동 입증. 따라서 "platform 한계" 가 아니라 "tier 선택 문제" 였다. 본 ADR 은 검증된 mechanism 을 정확한 tier 로 적용한다.

### 4. Pattern 분석 — sentinel 영역

본 ADR 은 누적 incident pattern_count 기반 escalation (ADR-045 §D-9) 산물이 **아니다** — CFP-1740 spec §2 WHY 가 **선제적 공백 메우기** (ADR-039 §결정 9 deferred follow-up 직접 이행) 영역. ADR-064 §결정 1 broad coverage + active amendment + best-effort 정합 (ADR-058 §결정 5 ratchet 강화 방향 sunset_justification 면제).

## 결정

### §결정 1 — 4-hook tier 분류 (1 blocking + 3 non-blocking)

매 turn 시점 enforcement 가 필요한 4 hook 을 다음 tier 로 분류한다. **plugin 배포 모델 유지** (`.claude/hooks` 직접 배포 회피) 가 모든 결정의 invariant 전제.

| hook | tier | 행위 | 차단 능력 platform 근거 | plugin 배포 신뢰성 |
|---|---|---|---|---|
| **PreToolUse (matcher: "Agent")** | **blocking** (실제 차단) | spawn 직전 spawn-prompt 필수 block presence 검증 → 누락 시 `permissionDecision: "deny"` + reason | 공식 hooks reference — `permissionDecision: "deny"` 공식 지원 | **plugin 경로 작동 OK** (PreToolUse:Bash 의 기존 `cross-repo-gh-safety` deny 선례 정합 — `hooks/hooks.json` dispatcher 활성 작동 입증) |
| **UserPromptSubmit** | non-blocking (기록 + 경고) | dialog reminder stdout 매 turn 주입 — ADR-071 user-dialog-mode + ADR-073 parallel-work-sentinel reminder context-inject | stdout context 매 turn 주입 — 공식 hooks reference 확정 | **plugin 경로 작동 OK** (stdout inject 영역은 block(continue) mechanism 영역 외 — #10412 영향 없음) |
| **Stop** | non-blocking (기록 + 경고) | stop-time 300자±50 평문 정리 advisory + question-quality 3-check advisory + stop-event-v1 ledger row append | block(continue) = **plugin 경로 깨짐** (#10412) + false-positive burn 50분 (#55754) → block 금지 | **block 금지** — ledger 기록 + 경고만 (record-only marker) |
| **SubagentStop** | non-blocking (기록 + 경고) | verify-before-trust (ADR-070) + back-translation gate (ADR-071 §결정 17) 위반 ledger row + 경고 | block(continue) = #10412 동일 — block 금지 | **block 금지** — ledger 기록 + 경고만 |

**핵심**: PreToolUse(Agent) 만 실제 차단. 나머지 3종은 `block(continue)` mechanism 의 신뢰성 문제 (§결정 2) 로 인해 **기록 + 경고만** (auto-block escalate 금지). PreToolUse(Bash) `cross-repo-gh-safety` deny 선례가 PreToolUse 전반의 plugin 경로 작동 신뢰성 입증.

### §결정 2 — plugin 배포 block 불신뢰 constraint (Stop/SubagentStop block 금지)

Stop / SubagentStop hook 의 `block(continue): false` mechanism 은 **plugin 배포 경로에서 깨진다**. 본 결정은 이 platform 결함을 verify-before-trust 한 결과를 binding constraint 로 codify.

**Evidence verbatim cite** (CFP-1740 spec §3 verification_sources):

- **GitHub issue #10412 (CLOSED)** — "Stop hook block doesn't propagate in plugin-distributed mode. Workaround: distribute hook scripts directly via `.claude/hooks/` instead of plugin path." → plugin 배포 경로 block(continue) 깨짐 입증. workaround 채택 시 codeforge plugin 배포 모델 자체가 무력화됨 → **채택 안 함**.
- **GitHub issue #55754** — "Stop hook false-positive block(continue): true → session burn 50 minutes. Decision reason field is delivered to user (Stop hook UI message) but NOT to Claude (next-turn context). Workaround: don't use Stop block." → false-positive recovery 비용 50분 + decision reason transmission 비대칭 (user only, Claude 미전달) → **block 시 deadlock 위험 + recovery 비용 prohibitive**.

**Binding constraint**:
- Stop / SubagentStop hook 은 `permissionDecision` 또는 `block(continue): false` 발화 **금지**.
- **non-blocking ledger + 경고만** (stop-event-v1 row append + stderr warning).
- plugin 배포 모델 유지 (`.claude/hooks` 직접 배포 회피).
- 사용자 escalation 은 ledger row + UserPromptSubmit reminder 의 다음 turn 재주입 경로로만 수행 (Claude 측 context 도달 보장).

### §결정 3 — 단일 dispatcher 통합 + one-channel rule

4 hook 전부 **기존 단일 dispatcher** (`hooks/hooks.json` → `hooks/run-hook.cmd` polyglot wrapper, superpowers 5.1.0 MIT) 에 통합. **parallel dispatcher 신설 금지**.

**`hooks/hooks.json` entry 패턴** (기존 SessionStart 2 + PreToolUse:Bash 1 답습):
```json
{
  "hooks": {
    "SessionStart":      [{"matcher": "startup|clear|compact", "hooks": [/* 기존 2 entry */]}],
    "PreToolUse":        [{"matcher": "Bash",  "hooks": [/* 기존 cross-repo-gh-safety */]},
                          {"matcher": "Agent", "hooks": [/* 신규 pretooluse-agent-spawn-gate */]}],
    "UserPromptSubmit":  [{"hooks": [/* 신규 userprompt-submit */]}],
    "Stop":              [{"hooks": [/* 신규 stop */]}],
    "SubagentStop":      [{"hooks": [/* 신규 subagent-stop */]}]
  }
}
```

각 hook entry = `${CLAUDE_PLUGIN_ROOT}/hooks/run-hook.cmd <hook-name>` 호출 (polyglot Windows cmd.exe + Unix bash 단일 file 호환). hook 스크립트는 extensionless polyglot (`hooks/userprompt-submit` / `hooks/pretooluse-agent-spawn-gate` / `hooks/stop` / `hooks/subagent-stop`) — Claude Code Windows auto-detection 의 `.sh` prefix 회피 (run-hook.cmd 본문 주석 verbatim 정합).

**one-channel rule** (consumer overlay 이중 발화 차단):
- 현재 `overlay/hooks/userprompt-reminder.{sh,ps1}` 는 **consumer overlay** hook (ADR-027 §결정 N — consumer `.claude/settings.json` 에 등록). wrapper 승격 시 wrapper-root hook + consumer overlay hook **양 channel 이중 발화 위험**.
- 본 ADR 은 **wrapper-root `hooks/userprompt-submit` 가 SSOT** — consumer overlay hook = deprecated grace (1 release grace 후 templates 제거, ADR-038 Amendment 3 §결정 10 정합 — polyglot wrapper SessionStart hook one-channel rule precedent 답습).
- consumer 측 `.claude/settings.json` 안 `UserPromptSubmit` entry 가 wrapper-root + overlay 양 channel 동시 활성 시 `scripts/check-no-duplicate-runtime-hook.sh` warning tier 발화 (ADR-038 Amendment 3 §결정 10 `check-no-duplicate-session-start-hook.sh` precedent 직접 답습, Phase 2 wire).

### §결정 4 — warning → blocking 승격 path (ADR-060 evidence-gate)

PreToolUse(Agent) spawn-format gate 는 **warning-tier 부터 시작**. ADR-060 4-tier promotion framework (PR ≥ 20 + bypass 외 failure = 0 + sibling Story merged) 충족 후 blocking 승격.

**Wave 1 (본 ADR scope)**:
- `evidence-checks-registry.yaml` 4 entry append: `runtime-hook-userprompt-presence` / `runtime-hook-pretooluse-agent-presence` / `runtime-hook-stop-presence` / `runtime-hook-subagentstop-presence`. 전부 `current_tier: warning` 시작.
- `hotfix-bypass:runtime-hook-presence` label family member (label-registry-v2 MINOR bump).
- PreToolUse(Agent) hook 자체의 `permissionDecision` 발화 = warning 단계에서는 **deny 대신 stderr warning + presence record only** (false-positive deny → spawn deadlock 회피).

**Wave 2 (별 follow-up CFP carrier)**:
- ADR-060 evidence-gate 충족 후 `current_tier: blocking-on-pr` 승격.
- PreToolUse(Agent) hook 의 `permissionDecision: "deny"` 활성 (Wave 1 evidence 충족 시).
- consumer 전파도 **advisory (warning) 부터** — false-positive deny → consumer spawn deadlock 위험 (§7.4 OperationalRisk 정합).

### §결정 5 — graceful degradation (auto-block escalate 금지)

hook stale / 불완전 설치 / 실행 오류 시 **graceful degradation** — auto-block escalate 금지 (= session stall / burn 회피, §결정 2 #55754 사고 회피).

**3-layer layered defense** (ADR-038 Amendment 1 §결정 8 verbatim 답습):
1. **non-skippable attempt** — hook 호출 시도 자체는 non-skippable (`hooks.json` entry 가 모든 매칭 turn 에서 발화). Orchestrator skip path 없음.
2. **non-blocking fail** — hook 실행 실패 / 누락 / stale 시 **경고 후 계속** (exit code 0 emit). turn 자체는 차단 안 함.
3. **runtime 폴백** — hook 미등록 / dispatcher 누락 시 SessionStart hook tier 폴백 (ADR-038 Amendment 2 §결정 9 precedent — TodoWrite preload runtime ToolSearch 폴백 동형).

**graceful degradation 영역 enum** (closed-set):
- hook file 부재 (`hooks/userprompt-submit` not found) → stderr warning + exit 0
- bash interpreter 부재 (Windows Git Bash 미설치) → run-hook.cmd 본문 `exit /b 0` 정합 (silent fail-open)
- hook 실행 timeout (> 5s) → warning 후 turn 계속
- ledger write 실패 (file system 권한 결여) → stderr warning + record-only (Stop/SubagentStop 적용)
- spawn-format parse error (PreToolUse(Agent), check_spawn_prompt_format.py exception) → warning + spawn 허용 (deadlock 회피, Wave 1)

**escalate 금지 invariant**: warning → blocking 승격은 **별 follow-up CFP + ADR-060 evidence-gate 통과** 후에만 (자동 escalation 금지). false-positive deny 누적 시 즉시 warning 복귀 (sibling Story 별 rollback carrier).

### §결정 6 — Scope boundary (inline-write detect hook 제외, 후속 CFP)

본 ADR scope = **4 hook 종**: UserPromptSubmit / PreToolUse(matcher:"Agent") / Stop / SubagentStop.

**제외 영역** (별 follow-up CFP):
- **inline-write detect hook** — ADR-039 §결정 9 두번째 bullet 의 Orchestrator inline Read/Write/Edit/Bash 직접 호출 검출 영역. PreToolUse(matcher:"Read"|"Write"|"Edit") 분기 + Orchestrator turn 컨텍스트 차별 검출 (Inline whitelist 4-entry vs 그 외 영역) 의 별도 mechanism 설계 필요. **본 Epic 제외, 후속 CFP**.

**근거 — ADR-064 §결정 1 CFP scope unitary 정합**:
- 본 ADR scope = "turn-time hook enforcement super-class" 안 **4 일관 영역** (spawn-format / dialog reminder / stop-time / subagent-return). 4 hook 모두 `hooks/hooks.json` 단일 dispatcher 통합 + warning-tier 시작 + graceful degradation 동일 패턴 → 단일 atomic scope.
- inline-write detect = **disjoint sub-domain** (Orchestrator inline-context 검출 mechanism 영역). 한 CFP 안 "경량 → full" 단계 채택 금지 정합 — 별 CFP 분리는 허용.

**미래 확장 잠재 영역** (informational only, 본 ADR scope 외):
- PostToolUse hook (사후 tool output 감사)
- Notification hook (사용자 통지 양식 강제)
- Live touching production-cutover lane 진입 시 추가 PreToolUse 분기 (CONDITIONAL ProductionEvidenceDeputy 정합)

## 결과 (Consequences)

### 긍정적 결과

1. **turn-time enforcement 공백 메움** — ADR-039 §결정 9 deferred follow-up 직접 이행. 매 turn 시점 spawn-format / dialog convergence / stop-time / subagent-return 4 영역 mechanical layer 활성.
2. **사후 PR-time lint → preventive turn-time layer 당김** — CFP-1489 spawn-prompt-head-pin / CFP-1497 amendment-slot-reservation / CFP-1500 mid-spawn-drift / CFP-1502 chief-author-span 4 사후 lint 의 검증을 PreToolUse(Agent) preventive layer 로 당김 (양 layer 공존, disjoint).
3. **ADR-064 §결정 9 stop-time + §결정 3 question quality 의 mechanical layer 부재** 영역 해소 — Stop hook 이 ledger row + advisory 발화.
4. **ADR-070 / ADR-071 §결정 17 의 mechanical layer 부재** 영역 해소 — SubagentStop hook 이 verify-before-trust / back-translation 위반 ledger row.
5. **plugin 배포 모델 유지** — `.claude/hooks` 직접 배포 우회 채택 안 함 (#10412 workaround 회피).

### 부정적 결과 / 트레이드오프

1. **hook latency 누적** — 4 hook 의 turn-time 호출이 각 < 200ms 목표 (PreToolUse < 500ms blocking gate 영역) 이나 누적 시 사용자 체감 latency 증가 가능. graceful degradation 5-layer (§결정 5) 가 timeout fail-open 보장.
2. **`hooks/hooks.json` 단일 file = 6 Story 직렬화 bottleneck** — CFP-1740 plan §batch 정합 sequential 강제 (state_dependency + shared_resource 양 사유, ADR-064 §결정 4 sequential mandate 정합).
3. **consumer overlay deprecated grace 비용** — 1 release grace 안 양 channel 동시 활성 시 이중 발화 검출 lint 필요 (§결정 3 one-channel rule, Phase 2 wire).
4. **PreToolUse(Agent) false-positive deny 위험** — spawn-format gate 의 검증 로직 false-positive 시 spawn deadlock. Wave 1 warning-only 가 위험 완화 (deny 활성 = ADR-060 evidence-gate 후 별 CFP).
5. **#55754 burn 회피 비용** — Stop/SubagentStop block 금지 binding constraint 가 enforcement 강도 상한 형성. 진정 차단 필요 영역은 PreToolUse 분기로만 (turn-completion gate 영역은 ledger + 다음 turn UserPromptSubmit 재주입).

### 의존성 / 후속 영역

- **Wave 2 (별 follow-up CFP)** — ADR-060 evidence-gate 충족 (PR ≥ 20 + bypass 외 failure = 0 + sibling Story merged) 후 PreToolUse(Agent) blocking 승격.
- **CFP-1740 Story-2 (#1742)** — PreToolUse(Agent) spawn-format gate 구현 (scripts/lib/check_spawn_prompt_format.py + hooks/pretooluse-agent-spawn-gate).
- **CFP-1740 Story-3 (#1743)** — Stop + SubagentStop hook 구현 (ledger atomic append).
- **CFP-1740 Story-4 (#1744)** — stop-event-v1 v1.0 → v1.1 MINOR bump (`hook_source` / `hook_decision` field, ADR-043 Allow-list amendment 판정).
- **CFP-1740 Story-5 (#1745)** — evidence-checks-registry 4 entry + label-registry MINOR + consumer-guide hook 등록 안내.
- **CFP-1740 Story-6 (#1746)** — 통합 검증 (4 신규 + 기존 3 hook 공존 + Win·Unix polyglot + ledger 경합).
- **별 CFP (inline-write detect hook)** — §결정 6 scope boundary 명시 제외 영역.

## 검증 + 측정 (Verification + Metrics, ADR-068 I-5 dimensional empirical grounding 정합)

10-dimension empirical-source annotation:

| dimension | parameter | value | empirical-source |
|---|---|---|---|
| latency | PreToolUse(Agent) hook timeout | < 500ms (blocking gate 영역 spawn 지연 상한) | [empirical-source: TBD — CFP-1740 Story-2 bats fixture 측정 후 ADR Amendment, code.claude.com hook timeout default 60s 기준 보수적 사용자 체감 임계] |
| latency | UserPromptSubmit/Stop/SubagentStop hook timeout | < 200ms (non-blocking, 누적 < 600ms/turn) | [empirical-source: TBD — CFP-1740 Story-1/3 bats fixture 측정] |
| count | hooks.json 신규 entry | 4 (UserPromptSubmit / PreToolUse:Agent / Stop / SubagentStop) | [empirical-source: CFP-1740 plan §Story 분해, verified-via Read hooks/hooks.json HEAD 기준 기존 3 entry + 4 신규 = 7 entry] |
| count | graceful degradation 영역 enum | 5 (file 부재 / interpreter 부재 / timeout / ledger 실패 / parse error) | [empirical-source: §결정 5 closed-set] |
| count | spawn-format 필수 block | 4 (PRE-SPAWN-ORIGIN-MAIN-SHA / USER-UTTERANCE-VERBATIM / worktree-first directive / parallel-dispatch block) | [empirical-source: ADR-082 Amendment 15 1-E + Amendment 5 1-C + ADR-040 Amendment 6 + ADR-064 Amendment 1] |
| accuracy | false-positive deny 허용 임계 (Wave 1 warning-only) | 0 (Wave 1 deny 비활성) | [empirical-source: §결정 4 Wave 1 warning-only invariant] |
| lifecycle | warning → blocking 승격 gate | PR ≥ 20 + bypass 외 failure = 0 + sibling Story merged | [empirical-source: ADR-060 §결정 1] |
| cost | session burn (false-positive Stop block 회피 비용) | 50분 (회피 대상) | [empirical-source: GitHub #55754 verbatim cite] |
| throughput | hook dispatcher 호출 빈도 | 1/turn UserPromptSubmit + 1/agent-spawn PreToolUse:Agent + 1/turn Stop + 1/subagent-return SubagentStop | [empirical-source: 공식 hooks reference event semantics] |
| rate | PreToolUse(Bash) 기존 deny rate (cross-repo-gh-safety) | [empirical-source: TBD — `hooks/cross-repo-gh-safety` exit code 1 (deny) 누적 횟수 측정 후 baseline, sibling carrier follow-up] |

## Boundary completeness self-check (ADR-068 I-1~I-6, ArchitectAgent §3 mandate 정합)

- **I-1 API contract semantic completeness** — `hooks/hooks.json` entry 4 신규 = JSON schema (matcher / hooks[].type / command / async). `permissionDecision` enum 영역 = `"deny"` / `"allow"` / 미발화 closed-set (공식 hooks reference). stop-event-v1 v1.1 field `hook_source` (enum `stop` / `subagent-stop`) + `hook_decision` (enum `record-only` — non-blocking marker) docstring Story-4 (#1744) carrier.
- **I-2 cross-module status enum propagation** — PreToolUse(Agent) `permissionDecision: "deny"` ↔ Orchestrator Agent tool spawn return value 매핑 = Claude Code platform native (caller 분기 처리는 platform 책임, hook 측 책임 외). Stop/SubagentStop ledger row `hook_source` enum ↔ stop-event-v1 reader 분기 처리 = Story-4 carrier.
- **I-3 unconditional vs conditional guard placement** — graceful degradation 5-layer (§결정 5) = **unconditional** (hook 진입 시점 무조건, 영역 enum 5 전부 fail-open exit 0). spawn-format gate (PreToolUse:Agent) = **conditional Wave 1** (warning-only, Wave 2 evidence-gate 후 blocking 승격 시 unconditional 전환). 본 ADR 본문 §결정 5 명시.
- **I-4 wording SSOT** — `runtime-hook-presence` action name = evidence-checks-registry entry name verbatim (frontmatter `mechanical_enforcement_actions[].action` + label `hotfix-bypass:runtime-hook-presence` family + workflow file name 3-way 일치, ADR-040 Amendment 3 §결정 7.A 정합).
- **I-5 dimensional empirical grounding** — 위 "검증 + 측정" 표 10 dimension annotation. `[empirical-source: TBD]` 3 entry 는 Story-2/3 bats fixture 측정 후 별 Amendment 로 채움 (CFP-1740 spec §3.3 검증 출처 명시 정합).
- **I-6 audit-gate-pointer-existence** — DesignReview lane finding 시 4-form pointer scope (file path / section anchor / ADR §결정 N reference) 보유 — 본 ADR 본문 = ADR-039 §결정 9 (file + ADR ref) + ADR-038 Amendment 1 §결정 8 (ADR ref + section anchor) + GitHub #10412 / #55754 (외부 link target) 3-way pointer presence.

## 결정 원칙 anchor (ADR-064 §결정 1-7 정합)

본 ADR = **broad coverage** (4 hook tier + 5 graceful degradation 영역 + 6 §결정 enum) + **best-effort** (공식 hooks reference + GitHub issue verify 완료 후 도달 가능한 최선의 안) + **active amendment** (ratchet 강화 방향, `is_transitional: false` permanent governance ratchet, ADR-058 §결정 5 정합 — ratchet 강화 sunset_justification 면제).

## Cross-reference

- **ADR-039 §결정 9** — Orchestrator subagent default for codeforge modification work, deferred follow-up (Orchestrator runtime enforcement) **직접 carrier**
- **ADR-025** — Phase 2 policy_violation_subdecision 발화 채널 차단 mechanical 보강
- **ADR-038 Amendment 1 §결정 8** — non-skippable attempt / non-blocking fail layered defense precedent
- **ADR-040 Amendment 3 §결정 7.D** — mechanical_enforcement_actions[] frontmatter 의무 self-application
- **ADR-060** — evidence-enforceable promotion framework (warning → blocking 승격 gate)
- **ADR-061 Amendment 3** — Python script-writing convention + CodeQL ReDoS line-by-line parse (check_spawn_prompt_format.py 적용)
- **ADR-064 §결정 9 / §결정 3** — stop-time + question quality 의 mechanical layer (Stop / UserPromptSubmit hook)
- **ADR-070 / ADR-071 §결정 17** — verify-before-trust + back-translation gate (SubagentStop ledger 대상)
- **ADR-073 Amendment 2** — parallel-work-sentinel polling (UserPromptSubmit reminder 대상)
- **ADR-082 Amendment 17 sub-scope 1-G** — amendment-slot pre-reservation strict claim mandate (본 ADR-115 자체 = 1-G META applied: ADR-RESERVATION row 115 pre-claim → commit → file write 순)
- **ADR-043** — stop-event-v1 Allow-list amendment 판정 (Story-4 carrier)
- **ADR-068 I-5** — dimensional empirical grounding (위 "검증 + 측정" 표 정합)
- **GitHub #10412 (CLOSED)** — plugin 배포 경로 block 깨짐 evidence
- **GitHub #55754** — false-positive session burn 50분 evidence + decision reason 비대칭 transmission
- **공식 hooks reference** — code.claude.com/docs/en/hooks
- **stop-event-v1** — inter-plugin contract, Story-4 carrier v1.0 → v1.1 MINOR bump

## 시각 표시 (ADR-079 KST `+09:00` colon-offset 정합)

본 ADR 작성 시점 = 2026-05-26 KST. governance display layer 모든 시각 표기 = KST `+09:00` ISO 8601 zoned. contract field layer (stop-event-v1 timestamp field) = UTC strict 0건 변경 invariant (ADR-079 layer-bounded 정합).
