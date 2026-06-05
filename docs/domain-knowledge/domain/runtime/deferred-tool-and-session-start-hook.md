---
kind: domain_fact
type: domain-knowledge
area: runtime
topic_slug: deferred-tool-and-session-start-hook
title: Claude Code deferred tool mechanism + SessionStart hook prompt-injection 모델 + codeforge 3-tier enforcement
status: Active
owner: ArchitectAgent
updated: 2026-05-12
tags:
  - claude-code-runtime
  - deferred-tool
  - sessionstart-hook
  - prompt-injection
  - enforcement-tier
related_adrs:
  - ADR-037  # plugin version drift SessionStart hook (선례 #1)
  - ADR-038  # progress visualization (Amendment 2 §결정 9 = 본 entry 의 carrier ADR)
  - ADR-040  # worktree-gc SessionStart hook (선례 #2)
  - ADR-041  # doc location registry (domain_knowledge variants path cover)
  - ADR-056  # domain-knowledge dir separation (path = domain/<area>/<topic>.md)
  - ADR-058  # 해소 기준 의무 (Amendment 2 sunset_justification 3-tuple)
carrier_story: CFP-500
date: 2026-05-12
---

# Claude Code deferred tool mechanism + SessionStart hook prompt-injection 모델 + codeforge 3-tier enforcement

본 entry 는 codeforge platform 내부 동작 사실 (DomainAgent kind) 의 observable behavior 모델 — Anthropic 공식 SDK / platform ABI spec 부재 영역에서 codeforge family + consumer 10+ repo 운영 검증으로 도출된 empirical knowledge. CFP-500 (SessionStart prereq-check hook 3rd attempt) 의 도메인 지식 SSOT.

**Epistemic disclaimer**: 본 entry 의 모든 모델은 관찰 기반 (empirical observation). harness update 시 변화 가능성 retain — 변경 감지 시 본 entry 를 **재검증** 한 후 갱신 (Story §2.5 D-7 / I-2 정합).

## 정의

본 entry 는 Claude Code harness 의 두 가지 핵심 메커니즘 — (1) **deferred tool 메커니즘** + (2) **SessionStart hook 의 prompt-injection 모델** — 그리고 codeforge 가 이 둘을 결합해 운영하는 **3-tier enforcement 모델** 의 영구 정의 (domain_fact kind).

- **deferred tool**: Claude Code harness 가 turn 0 에서 schema 를 노출하지 않고 이름만 노출하는 tool. `ToolSearch` lazy-fetch 후에야 invoke 가능. default-loaded tool 의 보완 분류.
- **SessionStart hook**: `.claude/settings.json` `hooks.SessionStart[]` 등록 항목. harness 가 세션 부팅 시 sequential 실행, 각 hook stdout 을 Orchestrator turn 0 의 `additionalContext` 로 inject. system prompt 본문 영구 변경 아님 — ephemeral.
- **3-tier enforcement 모델 (codeforge wrapper-specific framework)**: 선언적 규칙 enforcement 의 강도 분류. (a) physical / (b) startup-time / (c) runtime. ADR-038 Amendment 2 §결정 9 본문 SSOT.

## 컨텍스트

CFP-500 (본 carrier Story) = TodoWrite 선제 로드 enforcement 의 3rd attempt. 앞선 2 attempt (CFP-375 / CFP-385) 는 (c) runtime tier — CLAUDE.md / playbook 인라인 directive — 만으로 운영, 모두 실패 확정. `선언적 규칙 = 신뢰 불가` 가 2회 검증된 시점에 (c) → (b) tier escalation 필요성 도달. codeforge 는 이미 (b) tier hook 2종 (ADR-037 drift / ADR-040 worktree-gc) 을 운영 중 — CFP-500 = 3번째 (b) tier hook 도입.

본 entry 는 ADR-038 Amendment 2 §결정 9 의 carrier 도메인 지식. Anthropic 측 공식 ABI spec 부재 영역 — codeforge family 운영 검증으로 도출된 empirical model.

## 핵심 규칙

### 규칙 1 — deferred tool 메커니즘 (Claude Code harness)

Claude Code harness 는 tool universe 를 2 분류로 운영:

| 분류 | turn 0 schema 노출 | 호출 가능성 |
|------|---------------------|-------------|
| **default-loaded** | 즉시 schema 노출 | turn 0 부터 invoke 가능 |
| **deferred** | 이름만 노출, schema 부재 | `ToolSearch` lazy-fetch 후 invoke 가능 |

본 분류는 매 세션 system-reminder 의 explicit enumeration 으로 확인 가능 — `The following deferred tools are now available via ToolSearch. Their schemas are NOT loaded — calling them directly will fail with InputValidationError.` 형태의 메시지가 turn 0 에 표면화된다.

#### codeforge orchestration 에 영향 큰 deferred tool 5종

매 세션 system-reminder 관찰 결과:

- **TodoWrite** — codeforge progress visualization (ADR-038 §결정 1) 의 critical path
- **Monitor** — long-running command 추적 (사용 빈도 낮음)
- **WebFetch / WebSearch** — Researcher lane 외부 reference
- **mcp__github__*** — GitHub MCP 모든 도구 (Orchestrator 의 1차 GitHub 채널)
- **NotebookEdit / Cron* / TeamCreate / SendMessage / RemoteTrigger / PushNotification** — 사용 빈도 낮은 surface

위 중 **TodoWrite 가 codeforge 의 critical path** — ADR-038 §결정 1 의 CFP-20 §14.7 render flow 3번째 channel 의무. TodoWrite 미작동 = progress visualization layer 전체 무력화 (Story §1 verbatim — 사용자가 "아직도! 아직도!!!" 반복 표출).

#### ToolSearch lazy-fetch 모델

`ToolSearch` 자체는 default-loaded — recursive bootstrap 가능. tool description 본문 `Fetches full schema definitions for deferred tools so they can be called.` verbatim.

쿼리 형식 (관찰):
- `ToolSearch(query="select:<name>")` — 정확한 이름 매치 fetch
- `ToolSearch(query="keyword")` — keyword search (max_results 추가 인자)
- `ToolSearch(query="+slack send")` — `+slack` required keyword + remaining ranking

성공 시 schema 가 `<functions>{...}</functions>` 블록으로 노출되어 호출 가능 상태가 된다. 실패 (schema 부재 상태 invoke) 시 `InputValidationError` 거절 — Orchestrator 가 self-recovery 가능하나 1 turn round-trip 비용.

#### Critical path 의무 — `ToolSearch("select:TodoWrite")` 선제 로드

ADR-038 §결정 8 (Amendment 1) — Orchestrator 가 세션 시작 시 `ToolSearch("select:TodoWrite")` 로 스키마를 선제 로드한다. 실패 시 1회 재시도 → 재실패 시 warning only (lane 비차단, §결정 7 정합).

본 의무가 (c) runtime tier 의 CLAUDE.md / playbook 인라인 명시 (CFP-375 / CFP-385) 만으로는 **2회 검증된 실패** — 본 entry 의 SessionStart hook tier 도입 동기.

### 규칙 2 — SessionStart hook 의 prompt-injection 모델

#### 동작 모델 (관찰 기반)

Claude Code harness 가 세션 부팅 시점에 `.claude/settings.json` 의 `hooks.SessionStart[]` 항목들을 sequential 실행. 각 hook 의 stdout 을 capture 하여 Orchestrator 의 **첫 turn context** 에 `additionalContext` 로 inject. Orchestrator 가 첫 turn 응답 시 이 context 를 system prompt 의 일부로 인식.

```
[Claude Code Harness]                   [Orchestrator (LLM turn)]
   │
   ├─ 세션 부팅
   ├─ .claude/settings.json read
   ├─ hooks.SessionStart[] iterate ────────→ each hook stdout
   │     │
   │     ├─ hook 1 (drift)         stdout
   │     ├─ hook 2 (worktree-gc)   stdout
   │     └─ hook 3 (prereq-check)  stdout
   │                                          │
   ├─ Combine stdout → additionalContext      │
   │                                          ▼
   └─ first turn dispatch  ─────→  prompt = [system_prompt + additionalContext + user_message]
                                              │
                                              ▼
                                         Orchestrator response
```

#### 핵심 특성 (관찰)

- **system prompt 본문 영구 변경 아님** — ephemeral additionalContext. 세션 종료 시 retain 안 됨.
- **prompt cache 내 첫 turn 의 일부로 진입** — 정확한 TTL (Anthropic 공개 자료의 "approximately 5 minutes" 류 언급은 있으나 official ABI spec 부재) / 알고리즘 / hook stdout 변동 시 invalidation 동작은 **Anthropic 미공개**.
- **audit trail 부재** — stdout 은 ephemeral, 별도 logging 없음. Anthropic 측 telemetry 의존.
- **strong advisory 강도** — Orchestrator 가 turn 0 첫 사용자 메시지 응답 직전에 보는 prompt-level 지시 → CLAUDE.md / playbook 본문 directive (c tier) 보다 prompt cache 위치·실행 시점이 강하나, function-call 강제 (a tier) 보다는 약함.

### 규칙 3 — codeforge 의 3 SessionStart hook 책임 분담

CFP-500 merge 후 codeforge 는 **2종 SessionStart hook** 운영 (worktree-gc 는 retire — 아래 표 참조). 책임 boundary 명확화:

> **retire 기록**: `SessionStart-codeforge-worktree-gc` hook 은 제거됨. SessionStart 동기 실행이 worktree 다수 스캔으로 세션 시작을 지연시켰고, 정리 대상은 본질적으로 로컬 완료 시점에만 안전 판정 가능. → worktree 정리는 **eager 완료 시점 GitOpsAgent** (agents/GitOpsAgent.md §5) 가 primary, 주기적 `check-worktree-stale.sh` (squash-aware) 는 수동/스케줄 backstop. 아래 표의 worktree-gc 행은 historical.

| Hook | ADR | Sample file | Helper script | Install path 모델 | 실행 책임 영역 | Severity |
|------|-----|-------------|---------------|--------------------|----------------|----------|
| `SessionStart-codeforge-drift.json.sample` | ADR-037 / CFP-262 | `templates/.claude/hooks/SessionStart-codeforge-drift.json.sample` | `scripts/check-codeforge-version-drift.sh` | **plugin-installed** (`${CLAUDE_PLUGIN_ROOT}/codeforge/scripts/...`) | plugin family version drift hard-stop blocking | MAJOR=exit 1 / MINOR=warning / PATCH=info |
| ~~`SessionStart-codeforge-worktree-gc`~~ **(RETIRED)** | ADR-040 / CFP-136 | 삭제됨 (sample 제거) | `templates/scripts/check-worktree-stale.sh` (backstop, 수동/스케줄) | consumer-installed (script 유지) | **retire** — SessionStart 동기 GC 제거 (시작 지연). eager 완료 정리 = GitOpsAgent §5, 주기 = 수동 backstop (squash-aware) | — |
| `SessionStart-codeforge-prereq-check.json.sample` | ADR-038 Amendment 2 / CFP-500 | `templates/.claude/hooks/SessionStart-codeforge-prereq-check.json.sample` | `scripts/check-codeforge-prereq.sh` | **plugin-installed** (drift 패턴 inherit) | deferred tool schema prefetch advisory | advisory exit 0 (stdout heredoc echo) |

#### Install path 모델 분기 사유

- **plugin-installed** (`${CLAUDE_PLUGIN_ROOT}/codeforge/scripts/...`) — script 본문이 consumer state 무관 시 채택. drift hook (gh api + version JSON 조회) + prereq-check hook (static heredoc echo) 모두 consumer worktree path 불필요.
- **consumer-installed** (`${CLAUDE_PROJECT_DIR}/templates/scripts/...`) — script 가 consumer worktree path 의존 시 채택. worktree-gc 는 `git rev-parse --show-toplevel` 호출 필요 → consumer-installed 필수.

#### idempotent + side-effect 명시 패턴 공통

세 hook 모두 다음 공통 invariant 보유 — codeforge SessionStart hook 패턴 SSOT:

1. **idempotent** — 매 세션 부팅 반복 실행 시 outcome 동일 (multi-instance 동시 부팅 safe).
2. **side-effect 명시** — drift = exit code only / worktree-gc = filesystem prune / prereq-check = stdout only.
3. **bypass channel** — `BYPASS_<NAME>=1` env (audit trail 의무 mode 별 강도 차이).
4. **prerequisite 명시** — 각 sample file `_prerequisite` (drift) 또는 본문 한계 declaration.

#### 실행 순서 (등록 순서대로 sequential)

harness 가 `.claude/settings.json` `hooks.SessionStart[]` 배열 등록 순서대로 sequential 실행 — 선례 2종 운영 검증 (drift / worktree-gc). 본 prereq-check 가 가장 가벼움 (stdout heredoc echo only) → 3번째 위치 권장. 등록 순서 가이드는 `docs/consumer-guide.md` SessionStart hooks subsection 에 명문화.

### 규칙 4 — Researcher 3-tier enforcement model — codeforge mapping

ADR-038 Amendment 2 §결정 9 본문의 Researcher 3-tier 모델 — 선언적 규칙 enforcement 의 강도 분류. codeforge wrapper-specific framework (학계 / industry 직접 prior 명명 없음, brainstorm Phase 0 Researcher burst 가 codeforge 기존 패턴을 강도별로 후행 분류).

| Tier | 위치 | 강도 | mechanism | codeforge 적용 사례 |
|------|------|------|-----------|---------------------|
| **(a) physical** | CI / git hook / branch protection | true blocking — function-call 강제 | exit code · server-side reject · required status check | ADR-024 (branch protection `restrictions:{}`) · ADR-037 (drift hard-stop) · ADR-060 evidence-enforceable framework (blocking-on-pr / blocking-on-merge tier) |
| **(b) startup-time** | SessionStart hook stdout → additionalContext | strong advisory + 가시성 | prompt-injection (system-reminder 와 유사) — turn 0 첫 turn 캐시 진입 (관찰 기반) | ADR-037 drift hook · ADR-040 worktree-gc hook · **CFP-500 prereq-check hook (3번째 SessionStart hook)** |
| **(c) runtime** | system prompt 본문 (CLAUDE.md / playbook 텍스트 directive) | weakest — behavioral compliance | 정책 텍스트만 — Orchestrator self-check | CFP-375 / CFP-385 (실패 확정) — TodoWrite ToolSearch 인라인 명시 |

#### Tier escalation 의 정당성

problem domain 별 measurable failure 패턴이 tier 선택을 결정:

- **(c) → (b) escalation 정당** — 동일 layer 의 2 attempt 가 모두 실패 검증 시. CFP-500 = TodoWrite ToolSearch 선제 로드의 3rd attempt = (b) tier escalation.
- **(b) → (a) escalation 검토 trigger** — (b) tier 도입 후 retrospective evaluation 결과 violation 5건/100세션 초과 시 (ADR-038 Amendment 2 amendment_log sunset_justification 3-tuple metric). over-engineering 회피 의무.
- **다른 domain (예: branch protection / FIX root-cause)** — 이미 (a) physical tier 적용 중 (ADR-024 / ADR-048) — domain 별 measurable failure 패턴이 결정.

#### (b) tier 의 책임 경계 (Amendment 2 §결정 9 본문 정합)

- **책임**: schema/state 가용성 advisory layer — Orchestrator turn 진입 시점에 deferred tool schema 가 prompt cache 에 fresh 한 상태로 가용함을 강하게 advise.
- **비책임**: behavioral attempt 의무 자체는 ADR-038 §결정 8 retain — hook 도 prompt-level advisory 이며 mechanical function-call 강제가 아님. behavioral compliance 자체는 여전히 Orchestrator 책임.

## 경계

본 entry 의 scope 한계 명시 — empirical observation 기반 entry 이므로 Anthropic 공식 ABI spec 부재 영역에서의 적용 한계:

### Anthropic 미공개 ABI 영역 (Researcher unknown #1)

| 미공개 항목 | 영향 | codeforge mitigation |
|---|---|---|
| prompt cache TTL 정확 수치 | 매 세션 hook stdout 주입이 cache hit rate 영향 가능성 | fixed format prompt (variability 0) → cache invalidation 최소화 |
| hook stdout 변동 시 cache invalidation 동작 | 동적 prompt 생성 시 cache miss 폭증 위험 | helper script = single-quoted heredoc echo, variability 0 |
| Hook timeout 한계 | Anthropic 미공개 (통상 수십초 추정) | helper script < 100ms 예상 (heredoc echo only) |
| Hook concurrent execution model | multi-instance 부팅 시 동작 미공개 | helper script = read-only stdout (filesystem mutation 0), race 영역 무관 |

ADR-058 metric 추적 대상 (Story §6 위험 #1) — manual sampling 으로 측정 시작, CFP-389 / ADR-060 evidence-enforceable framework 후속 evaluation 에서 grep-based auto count 격상 평가 가능.

### Hook 의 mechanical enforcement 한계

- (b) tier 는 **strong advisory** — function-call 강제 아님. Orchestrator 가 무시 가능.
- mechanical enforcement 가 필요한 영역 (예: branch protection / required status check) 은 (a) physical tier 적용 — domain mismatch.
- behavioral compliance 자체는 여전히 Orchestrator 책임 (ADR-038 §결정 7·8 retain).

### Consumer state 와의 interaction

- 본 entry 는 plugin-installed hook (drift / prereq-check) 모델 만 cover. consumer-installed hook (worktree-gc) 의 consumer worktree state 의존 영역은 ADR-040 SSOT 별도.
- consumer overlay (`.claude/_overlay/`) 의 hook 추가 / 변형은 본 entry scope 밖 — consumer-guide §2h.1 위임.

## 관련 ADR

- **ADR-038 Amendment 2 §결정 9** — 본 entry 의 carrier ADR. SessionStart hook tier escalation (CFP-500). `prereq_tools[]` + `prereq_checks[]` declarative array schema.
- **ADR-052 Amendment 1** — Codex proactive check touchpoint #4 multi-round adversarial debate 격상. 본 entry 의 deferred tool 메커니즘 영역 cross-ref.
- **ADR-056 §결정 1** — domain-knowledge dir separation. 본 entry path = `domain/<area>/<topic>.md` 정합.
- **ADR-058 §결정 5** — 안전망 ADR 해소 기준 의무. Amendment 2 amendment_log `sunset_justification` 3-tuple metric/who/how.
- **ADR-040 / CFP-136** — worktree-gc SessionStart hook (선례 #2). install path = consumer-installed.
- **ADR-037 / CFP-262** — plugin version drift SessionStart hook (선례 #1). install path = plugin-installed.
- **ADR-060 / CFP-389** — evidence-enforceable promotion framework. manual sampling → grep-based auto count 격상 후보.
- **ADR-038 Amendment 1 §결정 7·8** — failure non-blocking 폴백 + runtime advisory tier 의무 (CFP-375). 본 entry 의 (c) tier retain 폴백 정합.

## 변경 이력

- **2026-05-12** — CFP-500 carrier — initial entry (ADR-038 Amendment 2 §결정 9 도입). codeforge 의 3-tier enforcement 모델 SSOT 정식 명문화. (c) → (b) tier escalation 3rd attempt 의 도메인 지식 cornerstone.

---

**관찰 source**:
- 본 세션 + 선행 CFP-375 / CFP-385 / CFP-411 / CFP-500 세션 system-reminder 표면화
- 선례 2종 hook (drift / worktree-gc) wrapper repo 자체 + consumer 10 repo 운영 검증
- ToolSearch tool description 본문 verbatim ("Fetches full schema definitions for deferred tools so they can be called.")

**Acknowledged gaps**:
- Anthropic 공식 SDK 문서·platform ABI spec 부재 (prompt cache TTL / hook timeout / concurrent execution / invalidation)
- harness update 시 본 entry 의 모델 변화 가능성 → 변경 감지 시 재검증 의무
