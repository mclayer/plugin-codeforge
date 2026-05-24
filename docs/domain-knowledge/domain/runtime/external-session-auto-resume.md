---
kind: domain_fact
type: domain-knowledge
area: runtime
topic_slug: external-session-auto-resume
title: External session auto-resume — Anthropic infra rate limit session-dead 후 OS-level wrapper recovery 모델
status: Active
owner: DomainAgent
created: 2026-05-24
updated: 2026-05-24
tags:
  - claude-code-runtime
  - anthropic-infra
  - rate-limit
  - session-recovery
  - os-level-wrapper
  - windows-task-scheduler
related_adrs:
  - ADR-110               # 본 entry 의 carrier ADR (External-runtime-wrapper SSOT boundary)
  - ADR-053-Amendment-2   # D1 trigger TYPE 6번째 entry (external-wrapper-invoked session resume) sibling
  - ADR-057               # Sonnet→Opus model-tier substitution (in-process axis, disjoint mechanism)
  - ADR-073               # verify-before-assert (transition trigger enum, lane_spawn/pr_open/merge_transition)
  - ADR-082               # write-time self-write verification mandate (chief author write discipline)
  - ADR-085               # active_sessions[] multi-session collaboration protocol
  - ADR-070               # §D6 mandatory-real-execution-evidence STANDING (4-source measurement carrier)
  - ADR-068               # I-3 conditional guard + I-5 dimensional empirical grounding
carrier_story: CFP-1355
sibling_story: CFP-1354   # in-process axis (disjoint mechanism)
parent_epic: CFP-1353     # Rate limit resilience Epic
date: 2026-05-24
---

# External session auto-resume — Anthropic infra rate limit session-dead 후 OS-level wrapper recovery 모델

본 entry 는 Anthropic infra rate limit 도달로 Claude Code session 자체가 OS-level 에서 종료된 시점, in-process Orchestrator 가 더 이상 self-recovery 불가한 영역에서 OS-level external wrapper (Windows Task Scheduler + PowerShell) 가 reset 시간까지 대기 후 `claude --resume <uuid>` 호출로 새 session 을 spawn 해 conversation context 를 복원하는 mechanism layer 의 domain_fact SSOT.

**Epistemic disclaimer**: 본 entry 의 모든 모델은 관찰 기반 (empirical observation). Anthropic 공식 SDK 문서 / platform ABI spec 부재 영역. harness update 시 변화 가능성 retain — 변경 감지 시 본 entry 를 **재검증** 한 후 갱신. M-1/M-2/M-3/M-4 4-source measurement 실 수치는 Phase 2 post-deploy 사용자 hand-test 결과 영역 (agent simulate 불가).

## 정의

본 entry 의 핵심 개념 4종 영구 정의:

- **Session-dead 시나리오**: Claude Code session process 가 OS-level 에서 종료된 상태. in-process Orchestrator memory / tool state / conversation context 가 모두 휘발. `~/.claude/projects/<repo-hash>/<uuid>.jsonl` event log 만 disk 에 잔존.
- **External session auto-resume**: OS-level wrapper (Task Scheduler + PowerShell script) 가 별 process 로 동작, Anthropic infra rate limit reset 시간까지 대기 후 `claude --resume <uuid>` 호출로 새 Claude Code session spawn → 직전 session 의 conversation context 를 자동 복원.
- **`claude --resume <uuid>` CLI surface**: Anthropic Claude Code CLI 의 사용자 facing 기능. UUID 로 직전 session 의 jsonl event log 를 read → conversation context 재구성 → 새 turn 진입 가능 상태. wrapper 가 invoke 하는 단일 CLI primitive.
- **4-source empirical fidelity gate**: M-1 conversation context fidelity % / M-2 in-process state / M-3 VS Code ↔ CLI asymmetry / M-4 session UUID file path 4축 의 measurement 결과로 wrapper viability 를 사전 결정하는 gate (ADR-110 §결정 7). pass / partial / fail 3-way decision tree.

## 컨텍스트

### 사용자 발화 verbatim (CFP-1355 §1 anchor)

> codeforge의 개선이나 consumer 프로젝트 작업 중 API Limit이 걸리는 때가 있다. 이 때 limit이 풀리면 자동 시작했으면 좋겠는데
> 그리고 이런 에러가 발생하는 것도 해결해야 한다.
> API Error: Server is temporarily limiting requests (not your usage limit) · Rate limited

본 발화는 **2개 disjoint axis** 의 결합 요구로 분해:

| Axis | Story | Mechanism layer | 범위 |
|---|---|---|---|
| In-process 429 mitigation | CFP-1354 Story A (ADR-109) | Orchestrator-controlled in-process retry (model-tier substitution + exp-backoff + circuit breaker) | session 살아있는 상태에서 surgical mitigation |
| OS-level external resume | **CFP-1355 Story B (ADR-110, 본 entry)** | OS-level wrapper process (Task Scheduler + PowerShell + `claude --resume`) | session-dead 후 OS-external recovery |

두 axis 가 disjoint mechanism layer — Story A 가 처리한 session-alive 영역 _후에_ session 이 dead 된 상황을 Story B 가 cover.

### Anthropic infra rate limit 4축 모델

Anthropic API rate limit 은 4축 독립 운영 (Researcher synthesis SSOT, [Anthropic 공식 문서](https://docs.claude.com/en/api/rate-limits) 기반):

| 축 | 의미 | 측정 단위 | 본 entry 영향 영역 |
|---|---|---|---|
| **ITPM** (Input Tokens Per Minute) | 분당 input token | tokens/min | 큰 file/context burst 시 첫 도달 |
| **OTPM** (Output Tokens Per Minute) | 분당 output token | tokens/min | long-form response burst 시 도달 |
| **RPM** (Requests Per Minute) | 분당 request 수 | requests/min | parallel deputy fan-out / debate round burst / brainstorm 7-agent burst 시 도달 |
| **Concurrent** | 동시 in-flight request 수 | requests | parallel subagent spawn burst 시 도달 |

**Critical: single API key per org tier 의 shared bucket**. 동일 org 안 모든 session (wrapper repo + consumer repo + multi-Orchestrator parallel) 이 4축 bucket 을 공유. 1-tick fan-out burst (single Orchestrator turn 에서 7-agent parallel spawn 등) 이 4축 중 어느 하나라도 초과 시 → Anthropic 의 `429 Rate Limited` 응답 → Claude Code harness 의 session-dead handling 영역 진입.

### 429 응답의 2 sub-class

본 entry 의 trigger 응답은 2 sub-class:

| Sub-class | 응답 형태 | 의미 | 본 entry trigger 여부 |
|---|---|---|---|
| **429 + 사용자 quota** | `Rate limited — usage limit reached` | per-user 또는 per-org tier quota 초과 | 사용자 결정 영역 (tier upgrade / waiting) — 본 entry trigger 영역 |
| **429 + infra throttle** | `Server is temporarily limiting requests (not your usage limit) · Rate limited` | Anthropic infra-level (org tier 또는 service-wide) temporary throttle | 본 entry trigger 영역 (Story A in-process retry → 실패 cascade depth ≥ 2 → session-dead → 본 wrapper resume) |

본 entry 는 두 sub-class 모두 cover — wrapper 가 reset 시간까지 대기 후 resume invoke (구분 필요 없음, mechanism 동일).

### 429 incident 카테고리화 (lane별 trigger 패턴)

본 entry 운영 시 관찰 가능한 incident pattern (CFP-1354 ADR-109 §결정 1 detection 4-tuple cross-ref):

| Lane | Trigger 패턴 | 빈도 | 본 entry 활성 영역 |
|---|---|---|---|
| Requirements (RequirementsPL spawn) | 4 lane agent parallel fan-out (DomainAgent + Analyst + Researcher + 3 code-context agent) burst | 중 | session-alive 일반 영역 (Story A in-process 처리) |
| Design (ArchitectPL spawn) | 6+3+1 deputy 병렬 spawn burst (brainstorm Phase 0 시 추가 7-agent burst) | 고 | session-alive 일반 영역 (Story A in-process 처리) |
| DesignReview (debate round) | multi-round adversarial debate min 3 / max 5 round burst (PL + Codex worker 동시 dispatch) | 중 | session-alive 일반 영역 (Story A in-process 처리) |
| Develop FIX iter | 3-iter FIX cascade (parallel diagnosis burst per iter) | 저 | session-alive 일반 영역 (Story A in-process 처리) |
| **운영 누적 (multi-Orchestrator parallel)** | 별 wrapper / consumer Orchestrator session 동시 운영 시 shared bucket 누적 → infra-level 429 cascade | 저 (조건부 발생) | **session-dead 영역 — 본 entry trigger** |

본 entry 활성 영역 = 마지막 row (운영 누적 + multi-Orchestrator + Story A in-process retry exhaust 후 session-dead). Story A 가 이미 in-process surgical mitigation 으로 빈도 ↓ 시키지만, infra-level temporary throttle 이 5h 단위 reset 일 경우 in-process retry 불충분 → session-dead 후 본 wrapper 활성.

## 핵심 규칙

### 규칙 1 — In-process vs External disjoint axis

| Axis | Story | Mechanism | Trigger 조건 | Recovery 메커니즘 |
|---|---|---|---|---|
| **In-process** (Story A) | CFP-1354 ADR-109 | Orchestrator-controlled retry | session-alive 상태 429 응답 1회 | exp-backoff (1s/2s/4s/8s/16s/32s max 60s full jitter) + same-model retry 1회 + Opus fallback 1회 + 6 attempts soak |
| **External** (Story B, 본 entry) | CFP-1355 ADR-110 | OS-level wrapper (Task Scheduler + PowerShell) | session-dead 후 OS-level recovery 영역 | Anthropic header polling (`anthropic-ratelimit-unified-5h-reset`) + Task Scheduler trigger time mutate + `claude --resume <uuid>` invoke |

**Disjoint invariant**: 두 mechanism layer 가 영구 분리.
- Story A = in-process Orchestrator memory + tool state 보존 영역 (model-tier substitution / exp-backoff / circuit breaker primitive)
- Story B = OS-external new process spawn 영역 (별 OS process 가 별 session spawn → context 만 jsonl event log 에서 복원)

**Cascade 관계** (운영 영역): Story A in-process retry 가 cascade depth ≥ 2 → ADR-109 §결정 5 "user manual resume only" 영역 진입 → user manual 영역에서 session 종료 → Story B wrapper 가 background 에서 reset 시간까지 대기 → 자동 resume.

### 규칙 2 — Sonnet→Opus fallback amplification risk (ADR-057 cross-ref)

ADR-057 §결정 2 "자동 재시도 금지" invariant 은 **in-process model-tier substitution axis 한정** — Story B 의 OS-external wrapper 영역과 disjoint.

| Axis | ADR-057 §결정 2 적용 여부 | 사유 |
|---|---|---|
| In-process Sonnet→Opus retry (Story A) | **적용** | 동일 in-process turn 안 model substitution 이 1회로 제한 (rate-limit amplification 차단) |
| OS-external wrapper resume (Story B, 본 entry) | **미적용** (axis disjoint) | 새 OS process + 새 session spawn — model 선택은 새 session 의 default model 영역 (Orchestrator = Opus 의무, ADR-057 §결정 1) |

본 disjoint 분리가 명시되지 않으면 "wrapper 가 자동 resume = ADR-057 §결정 2 위배" 오해 가능 — disjoint axis cross-ref 영구 codify.

### 규칙 3 — Windows-specific wrapper 패턴 4종

본 entry Phase 1 scope = Windows 영역만. Linux/macOS = Phase 2 sub-CFP carrier (silent skip 금지, explicit abort 의무 — ADR-110 §결정 5):

| Element | Path / Format | Layer | Owner |
|---|---|---|---|
| **PowerShell wrapper SSOT** | `scripts/codeforge-session-resume.ps1` | wrapper repo (plugin-codeforge) | wrapper plugin (Phase 2 carrier) |
| **Task Scheduler XML template** | `templates/scheduler/codeforge-auto-resume.xml` | wrapper repo (신규 sub-dir) | wrapper plugin (Phase 2 carrier) |
| **Installer (opt-in admin)** | `scripts/install-codeforge-resume.ps1` | wrapper repo | wrapper plugin (Phase 2 carrier) |
| **Linux/macOS bash equivalent** | placeholder only (Phase 2 sub-CFP carrier) | wrapper repo (Phase 2+ scope) | wrapper plugin (Phase 2+ carrier) |

**Invariant** (ADR-110 §결정 5 RefactorAgent anti-pattern guard): Linux/macOS 환경 wrapper invoke 시 silent skip 금지. explicit abort (`Write-Error + exit 1 + msg "Linux/macOS bash equivalent = Phase 2 sub-CFP carrier"`) 의무. consumer-guide §1j 안 placeholder 만 명시.

### 규칙 4 — Anthropic header polling mechanism

Wrapper 의 rate-limit reset 검출은 Anthropic header polling 영역 (ADR-110 §결정 8):

```
[Task Scheduler trigger fire]
   │
   ├─ wrapper script invoke
   ├─ `claude --print "noop"` invoke (lightweight detection probe)
   │     │
   │     ├─ stderr / response header parse
   │     │     ├─ anthropic-ratelimit-unified-5h-reset: <Unix epoch UTC>
   │     │     ├─ anthropic-ratelimit-requests-reset: <Unix epoch UTC>
   │     │     └─ anthropic-ratelimit-tokens-reset: <Unix epoch UTC>
   │     │
   │     └─ if rate-limit detected:
   │         ├─ $resetEpoch = parse unified-5h-reset
   │         ├─ $nextTrigger = [DateTime]::UnixEpoch.AddSeconds($resetEpoch).ToLocalTime()
   │         └─ `schtasks /Change /TN <task-name> /ST <hh:mm>` mutate next trigger
   │
   └─ else (rate-limit cleared):
       ├─ `claude --resume <uuid>` invoke (read uuid from %LOCALAPPDATA%/codeforge/last-session.txt)
       └─ new session spawned with conversation context restored
```

**핵심 invariants**:
- `claude --print "noop"` = lightweight detection probe (output 최소화, token cost 0 에 가까운 invoke)
- Unix epoch UTC strict (ADR-079 contract field layer 무손상)
- `schtasks /Change` = Windows Task Scheduler trigger time mutation primitive (XML 재작성 불필요, 단일 command 로 사용)

### 규칙 5 — 4-source empirical fidelity gate (ADR-110 §결정 7)

Wrapper viability 의 precondition = 4-source empirical measurement (ADR-068 I-5 dimensional empirical grounding + ADR-070 §D6 mandatory-real-execution-evidence STANDING 정합):

| Source | 측정 대상 | Pass | Partial | Fail | Phase 2 measurement |
|---|---|---|---|---|---|
| **M-1** | conversation context fidelity % | ≥ 80% | 50-80% | < 50% | 사용자 post-deploy hand-test (agent simulate 불가) |
| **M-2** | in-process state /4 (tool state / file open / git state / TodoWrite list) | 4/4 | 2-3/4 | ≤ 1/4 | 사용자 post-deploy hand-test |
| **M-3** | VS Code extension ↔ CLI asymmetry | identical | convertible | asymmetric | 사용자 post-deploy hand-test |
| **M-4** | session UUID file path verify | verified | partial | mismatched | `ls ~/.claude/projects/<repo-hash>/` 244 jsonl files 실재 — Phase 1 verified ✓ |

**3-way decision tree** (CFP-1355 Change Plan §3.first_step verbatim, ADR-110 §결정 7 본문):

```
IF M-1 ≥ 80% AND M-2 = 4/4 AND M-3 ∈ {identical, convertible} AND M-4 = verified
THEN gate_result = pass
     → sub-area b/c/d 병렬 진입 허용 + ADR-110 §결정 1-10 모두 적용

ELIF M-1 50-80% OR M-2 2-3/4 OR M-3 = convertible OR M-4 = partial
THEN gate_result = partial
     → Partial wrapper scope (context-only resume + in-process state 재구성 의무)

ELSE
THEN gate_result = fail
     → sub-area b/c/d ABORT, sub-area e 만 carry-over (negative ADR — why-not external wrapper codify)
```

**Critical: Phase 2 영역 = test 설계 + decision tree codify 만**. 실 measurement 는 post-deploy 사용자 hand-test 의무 (agent simulate 불가, ADR-070 §D6 mandatory-real-execution-evidence STANDING 정합). 측정 결과는 `docs/kpi/resume-fidelity-history.jsonl` 영구 append (본 entry 동반 KPI seed file).

### 규칙 6 — Fallback path (ADR-110 §결정 9)

| Trigger | Fallback | 사용자 영역 |
|---|---|---|
| Task Scheduler trigger failure (3회 exhaust) | manual user resume + Windows Toast notification | 사용자 manual click |
| Fidelity-fail (§결정 7 gate result = fail) | wrapper script disabled + 사용자 escalation (negative ADR carry-over 'why-not external wrapper') | 사용자 결정 (wrapper 도입 abort) |
| UUID file corruption / disk full | manual session restart + Windows Toast notification (auto-resume abort) | 사용자 manual restart |

**ADR-057 §결정 2 invariant 보존**: 본 fallback path 는 OS-external session-dead 후만 활성 → in-process retry axis 와 분리 영역 (axis disjoint).

## 경계

본 entry 의 scope 한계 명시 — empirical observation 기반 entry 이므로 Anthropic 공식 ABI spec 부재 영역에서의 적용 한계:

### Anthropic 미공개 ABI 영역 (epistemic gaps)

| 미공개 항목 | 영향 | 본 entry mitigation |
|---|---|---|
| `claude --resume <uuid>` 의 정확 context restoration 알고리즘 | M-1 fidelity % 예측 불가 — 실 measurement 의무 | Phase 2 사용자 hand-test (post-deploy) |
| jsonl event log 의 정확 schema / field 의미 | UUID file path 추출만 cover, content 읽기 회피 | wrapper script = path verify only, content read 0 |
| Rate-limit reset header 의 정확 field 명 / 값 형식 | Anthropic 측 stable contract 보장 부재 | `anthropic-ratelimit-unified-5h-reset` 우선 + 보조 `requests-reset` / `tokens-reset` polling fallback |
| 4축 rate limit 의 정확 threshold 수치 | per-org tier / per-time-window | header polling 만 의존 — threshold 수치 의존 0 |

### Mechanical enforcement 한계

- 본 entry = empirical knowledge SSOT (DomainAgent kind). mechanical enforcement = ADR-110 mechanical_enforcement_actions 2 entry (`external-wrapper-ssot-boundary-self-check` + `resume-fidelity-test-evidence`) 영역.
- Phase 1 = declaration-only Wave 1 (ADR-082 §결정 6 retain pattern 답습). Phase 2 = mechanical wire 영역.

### Cross-platform 한계

- Phase 1 scope = Windows 영역만.
- Linux/macOS = Phase 2 sub-CFP carrier — wrapper invoke 시 explicit abort 의무 (silent skip 금지, ADR-110 §결정 5 RefactorAgent anti-pattern guard).

### Multi-session coordination 한계

- ADR-085 multi-session collaboration protocol = single repo 안 multi-Orchestrator session 영역 cover.
- 본 entry 는 wrapper resume 시 발생 가능한 ghost session (직전 session 잔존 + 새 session spawn 동시) → ADR-110 §결정 6 Local namespace mutex (`Local\CodeforgeResumeWrapper`) 로 차단 — single-user developer machine 가정.
- Multi-user developer machine = `project.yaml runtime.multi_user: bool` opt-in (Phase 2 carrier, Global namespace mutex 영역).

### VS Code extension parallel session 영역

- ADR-110 §결정 10 = Not strict (wrapper 가 별 process 이므로 perfect coordination 불가).
- extension upstream API exposure 시 strict coordination = 후속 sub-CFP carrier.

## 관련 ADR

- **ADR-110** — 본 entry 의 carrier ADR. External-runtime-wrapper SSOT boundary (10 §결정). OS-level wrapper ↔ codeforge plugin SSOT disjoint layer normative SSOT.
- **ADR-053 Amendment 2** — §D1 trigger TYPE 6번째 entry `external-wrapper-invoked session resume` (Windows Task Scheduler + PowerShell wrapper 가 `claude --resume <uuid>` 호출로 신규 session spawn 시 구조적 재구동 의무 영역). sibling carrier — D1 5 기존 trigger 와 axis 동형.
- **ADR-057 §결정 2** — Sonnet→Opus model-tier substitution (in-process axis). 본 entry OS-external axis 와 disjoint mechanism — 본 entry 활성 시 ADR-057 §결정 2 위배 0 (axis disjoint cross-ref 영구 codify).
- **ADR-073 §결정 1** — verify-before-assert (lane_spawn / pr_open / merge_transition trigger). 본 carrier Story (CFP-1355) chief author write-time pre-publish FIX 영역 (chief packet ADR-110 → ADR-109 → ADR-110 2-layer verify-before-trust catch, ADR-082 Amendment 7 backward-staleness 정합).
- **ADR-082** — write-time self-write verification mandate. 본 entry write-time verify (sub-dir 미존재 verify / cross-ref ADR direct grep verify) 의무 정합.
- **ADR-085** — multi-session collaboration protocol. 본 entry wrapper resume 후 새 session 의 active_sessions[] field 영역 — single-user 가정 retain (Phase 1 scope).
- **ADR-070 §D6** — mandatory-real-execution-evidence STANDING. 본 entry §결정 7 4-source measurement 실 실행 의무 정합 — Phase 2 사용자 hand-test 영역.
- **ADR-068 I-3 + I-5** — conditional guard + dimensional empirical grounding. 본 entry §결정 7 4-source measurement 의 dimensional empirical-source annotation 정합.

## 관련 CFP

- **CFP-1353** (parent Epic) — Rate limit resilience Epic. Story A + Story B 2 sibling axis 통합.
- **CFP-1354** (sibling Story A) — In-process Anthropic infra 429 mitigation framework (ADR-109 신규). disjoint mechanism axis cross-ref.
- **CFP-1355** (본 carrier Story B) — External session auto-resume Windows wrapper (ADR-110 신규). 본 entry 의 carrier Story.
- Phase 2 carrier: `scripts/codeforge-session-resume.ps1` + `templates/scheduler/codeforge-auto-resume.xml` + `tests/wrapper-resume.Tests.ps1` + `docs/consumer-guide.md` §1j + `docs/kpi/resume-fidelity-history.jsonl` append-only event log (본 entry sibling KPI seed).

## 변경 이력

- **2026-05-24** — CFP-1355 carrier — initial entry (ADR-110 §결정 1-10 + ADR-053 Amendment 2 +
  Anthropic infra 4축 rate limit 모델 + 429 incident 카테고리화 + in-process/external disjoint axis +
  Windows-specific wrapper 패턴 4종 + Anthropic header polling mechanism + 4-source empirical fidelity gate +
  fallback path codify). codeforge 의 OS-level external wrapper recovery 모델 SSOT 정식 명문화 — Story A in-process axis (CFP-1354 ADR-109) 와 disjoint mechanism layer 영구 분리.

---

**관찰 source**:
- 사용자 발화 verbatim (CFP-1355 §1) — `Server is temporarily limiting requests (not your usage limit) · Rate limited` 메시지 anchor
- ADR-110 §결정 1-10 + ADR-053 Amendment 2 본문
- [Anthropic 공식 rate limit 문서](https://docs.claude.com/en/api/rate-limits) (4축 모델 — ITPM/OTPM/RPM/concurrent + shared bucket per org tier)
- Anthropic Claude Code CLI `claude --resume <uuid>` + `claude --print "noop"` invoke surface (CLI surface verbatim)
- Windows Task Scheduler `schtasks /Change /TN /ST` mutation primitive (Microsoft 공식 schtasks reference)
- `~/.claude/projects/<repo-hash>/<uuid>.jsonl` event log path (Phase 1 verified — 244 jsonl files 실재)

**Acknowledged gaps**:
- `claude --resume <uuid>` 의 정확 context restoration 알고리즘 = Anthropic 미공개 → M-1 fidelity % 예측 불가 → Phase 2 post-deploy 사용자 hand-test 의무
- jsonl event log 의 정확 schema / field 의미 = Anthropic 미공개 → wrapper script = path verify only, content read 0
- 4축 rate limit 의 정확 threshold 수치 = per-org tier / per-time-window 미공개 → header polling 만 의존
- harness update 시 본 entry 의 모델 변화 가능성 → 변경 감지 시 재검증 의무 (Story §2.5 D-7 / I-2 정합)
