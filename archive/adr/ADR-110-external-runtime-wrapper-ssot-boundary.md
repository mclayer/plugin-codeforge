---
adr_number: 110
title: External-runtime-wrapper SSOT boundary — OS-level wrapper ↔ codeforge plugin SSOT disjoint layer
status: Accepted
category: tooling-infrastructure
date: 2026-05-24
carrier_story: CFP-1355
parent_epic: CFP-1353
sibling_story: CFP-1354
supersedes: null
amends: null
amendments: []
related_stories:
  - CFP-1353  # parent Epic (Rate limit resilience)
  - CFP-1354  # sibling Story A (in-process axis, disjoint mechanism)
  - CFP-1355  # 본 carrier Story B (OS-external axis)
related_adrs:
  - ADR-027  # consumer adoption protocol (project.yaml schema 확장)
  - ADR-039  # inline whitelist closed 4-entry 무손상 (wrapper = OS-external process, inline 영역 외부)
  - ADR-040  # worktree convention (wrapper script worktree path 영향 영역 외)
  - ADR-053  # Amendment 2 (D1 trigger TYPE 6번째 entry append, sibling carrier)
  - ADR-057  # model-tier substitution disjoint axis (in-process Sonnet→Opus fallback)
  - ADR-058  # is_transitional + sunset_justification 정합
  - ADR-068  # I-3 conditional guard + I-5 dimensional empirical grounding
  - ADR-070  # §D6 mandatory-real-execution-evidence STANDING
  - ADR-073  # transition trigger enum 8-set closed-set ratchet (verify-before-assert)
  - ADR-082  # write-time self-write verification mandate
  - ADR-083  # consumer-applicability filter mixed 분류
  - ADR-085  # active_sessions[] multi-session coordination
  - ADR-097  # paradigm replacement carve-out 비대상
related_files:
  - scripts/codeforge-session-resume.ps1                  # Phase 2 carrier
  - templates/scheduler/codeforge-auto-resume.xml         # Phase 2 carrier
  - docs/consumer-guide.md                                # §1j Phase 2 carrier
  - docs/domain-knowledge/domain/runtime/external-session-auto-resume.md
  - tests/wrapper-resume.Tests.ps1                        # Phase 2 carrier
is_transitional: false
mechanical_enforcement_actions:
  - action: external-wrapper-ssot-boundary-self-check
    status: declaration-only-Wave-1
    progress_note: "ADR-110 신설 시점 registry entry 부재 (declaration-only). pattern_count ≥ 2 재발 시 follow-up CFP MUST promote — ADR-082 §결정 6 retain pattern 답습. Phase 2 carrier = `scripts/check-external-wrapper-ssot-boundary.sh` (wrapper script 가 codeforge plugin SSOT path 침범 0건 verify) + evidence-checks-registry warning entry."
    target_section: §결정 1
  - action: resume-fidelity-test-evidence
    status: declaration-only-Wave-1
    progress_note: "Phase 2 4-source empirical fidelity test 실 measurement 결과 (M-1/M-2/M-3/M-4) artifact 영구 보존 의무. mechanical wire = Phase 2 `docs/kpi/resume-fidelity-history.jsonl` append-only event log (ADR-106 operational-signal-history precedent 답습)."
    target_section: §결정 7
---

# ADR-110: External-runtime-wrapper SSOT boundary — OS-level wrapper ↔ codeforge plugin SSOT disjoint layer

## 상태

**Accepted (2026-05-24 KST)** — CFP-1355 carrier story (Epic CFP-1353 Story B, sibling: CFP-1354 in-process axis).

## 컨텍스트

Anthropic infra rate limit 도달로 Claude Code session 자체가 종료된 시점, in-process Orchestrator 가 자동 재시도 불가 영역 (session-dead 후 OS-external recovery). 사용자 발화 verbatim:

> codeforge의 개선이나 consumer 프로젝트 작업 중 API Limit이 걸리는 때가 있다. 이 때 limit이 풀리면 자동 시작했으면 좋겠는데

본 ADR = **OS-level external wrapper (Windows Task Scheduler + PowerShell)** 와 **codeforge plugin SSOT (codeforge-* lane plugin)** 의 disjoint layer 경계 codify. 두 layer 책임 영역 / write 경계 / cross-ref 정책 normative SSOT.

**Sibling Story A (CFP-1354 ADR-109 in-process 429 framework)** 와 **disjoint axis** — sibling carrier name space 충돌 우려 0 (Story A 의 ADR-109 = in-process 429 mitigation framework 가 Phase 1 PR open 시점 ADR 번호 점유, 본 ADR-110 = Orchestrator post-chief collision-rebase ratchet correction 결과 sequential next available 재할당 — ADR-050 + ADR-085 multi-session sibling parallel work coordination 정합). 본문 내용 = OS-external axis 한정.

**chief author + Orchestrator post-chief verify-before-trust catch 2-layer**: (1) chief packet stated "ADR-110 신규" pre-allocation. chief verify-before-trust 가 `git show origin/main:docs/adr/ADR-RESERVATION.md` direct fetch → max active = 108 (CFP-1346), → downgrade to ADR-109. (2) Orchestrator post-chief 가 PR-pending state 추가 verify: Story A wrapper PR #1386 (already open) 가 ADR-109 reserve 중 → sibling collision detected → ADR-110 으로 ratchet escalation. ADR-082 Amendment 7 backward-staleness catch (`M ≤ max` stale 차단) + ADR-050 sibling parallel work coordination 정합 — pre-publish inline FIX 완료 (2-layer verify pattern reinforcement, single-layer verify gap evidence).

## 결정

### §결정 1 — External runtime wrapper SSOT boundary disjoint layer

OS-level external wrapper (`scripts/codeforge-session-resume.ps1` + `templates/scheduler/codeforge-auto-resume.xml`) 는 codeforge plugin SSOT (codeforge-{requirements,design,develop,review,test,pmo,deploy,deploy-review} lane plugin) 와 disjoint layer.

**Invariant**: wrapper script 는 codeforge plugin SSOT path (`codeforge-*/skills/` / `codeforge-*/agents/` / `codeforge-*/templates/` / wrapper repo `CLAUDE.md` / wrapper repo `docs/inter-plugin-contracts/`) 를 **write / modify 0건**. wrapper script = read-only consumer of CLI surface (`claude --resume`) only.

**Boundary 표**:

| Layer | Owner | Write scope | Read scope |
|---|---|---|---|
| OS-level wrapper | wrapper script (PowerShell) | `%LOCALAPPDATA%/codeforge/last-session.txt` + log file | Claude CLI surface (`claude --resume <uuid>`) + `~/.claude/projects/<repo-hash>/<uuid>.jsonl` (path verify only, content read 0) |
| Codeforge plugin SSOT | codeforge-* lane plugin agent | lane plugin self-write path (codeforge-* 안 ADR / Story / change-plan / agent / skill) | 본 layer 안 cross-ref |
| Consumer overlay | consumer `.claude/_overlay/` | consumer overlay self-write | wrapper script toggle `runtime.auto_resume.enabled: bool` (Phase 2 schema) |

**거절된 대안**:
- (A) wrapper script 가 codeforge plugin SSOT 안 file (예: CLAUDE.md / settings.json) 동적 modify — invariant 위배, ADR-039 inline whitelist 확장 surface 신설 risk
- (B) codeforge plugin agent 가 wrapper script invoke — lane plugin schema 확장 surface 신설, ADR-039 4-entry 무손상 invariant 위배

### §결정 2 — Wrapper script placement

| Element | Path | Layer | Owner |
|---|---|---|---|
| Wrapper SSOT (script source) | `scripts/codeforge-session-resume.ps1` | wrapper repo (plugin-codeforge) | wrapper plugin |
| XML template | `templates/scheduler/codeforge-auto-resume.xml` | wrapper repo (신규 sub-dir) | wrapper plugin |
| Install destination (consumer) | `%ProgramFiles%/codeforge/` (admin-writable, tampering 차단) | consumer machine | consumer install script |
| User-writable runtime state | `%LOCALAPPDATA%/codeforge/` (user RW) | consumer machine | wrapper script runtime |

### §결정 3 — Task Scheduler stored credential boundary

Windows Task Scheduler 가 stored credential 사용 시 → Windows Credential Manager LSA / DPAPI 영역 위임. codeforge plugin SSOT 침범 0건:
- wrapper script 안 credential literal 0건
- Task Scheduler XML 안 password 평문 0건 (`<Principal LogonType="InteractiveToken">` 만 사용, ServiceAccount 금지)
- codeforge plugin agent 가 credential 접근 0건 (lane plugin secret boundary 영역 외)

### §결정 4 — Session UUID persistence (abstraction layer)

| Element | Path | Format | ACL |
|---|---|---|---|
| Last session UUID file | `%LOCALAPPDATA%/codeforge/last-session.txt` | plain text UUID (single line, no newline-trail) | `icacls /inheritance:r /grant:r "%USERNAME%:F"` user-only RW |

**Rationale**: codeforge layer abstraction — wrapper script 가 `~/.claude/projects/` 직접 read 회피. Anthropic upstream path schema 변경 시 wrapper 영향 격리 (RefactorAgent decoupling 권고 정합).

### §결정 5 — Polyglot platform adapter

| Platform | Phase 1 | Phase 2+ |
|---|---|---|
| Windows | PowerShell 5.1+ wrapper (active scope) | full carrier |
| Linux / macOS | **explicit abort** (`Write-Error + exit 1 + msg "Linux/macOS bash equivalent = Phase 2 sub-CFP carrier"`) | bash equivalent (systemd timer / launchd) sub-CFP carrier |

**Invariant** (RefactorAgent anti-pattern guard): silent skip 금지. Linux/macOS 환경 wrapper invoke 시 explicit abort + non-zero exit + msg 의무. consumer-guide §1j 안 placeholder 만 (Phase 2 sub-CFP carrier defer).

### §결정 6 — Ghost session prevention (mutex)

| Element | Value | Scope |
|---|---|---|
| Mutex name | `Local\CodeforgeResumeWrapper` | Local namespace (single-user developer machine 가정) |
| 2nd instance behavior | mutex acquire fail → wait timeout 5s → exit 0 + log "already running" | non-fatal exit (Task Scheduler re-trigger 영역 normal) |
| Global namespace | `project.yaml runtime.multi_user: bool` opt-in | Phase 2 carrier (multi-user developer machine 영역) |

### §결정 7 — Empirical fidelity gate (wrapper viability precondition)

**의무 sequencing** (ADR-068 I-3 conditional guard + ADR-070 §D6 mandatory-real-execution-evidence STANDING 정합):

Phase 2 design+implementation lane 진입 시 sub-area b/c/d 병렬 진입 **금지** — 4-source empirical measurement (M-1 conversation context fidelity % / M-2 in-process state / M-3 VS Code ↔ CLI asymmetry / M-4 session UUID file path) 실 실행 후 fidelity 3-way decision tree 분기 의무.

**4-source measurement schema**:

| Source | Threshold pass | Threshold partial | Threshold fail | Empirical-source |
|---|---|---|---|---|
| M-1 (conversation context fidelity %) | ≥ 80% | 50-80% | < 50% | `[empirical-source: TBD — Phase 2 measurement carrier]` |
| M-2 (in-process state /4) | 4/4 | 2-3/4 | ≤ 1/4 | `[empirical-source: TBD — Phase 2 measurement carrier]` |
| M-3 (VS Code ↔ CLI asymmetry) | identical | convertible | asymmetric | `[empirical-source: TBD — Phase 2 measurement carrier]` |
| M-4 (UUID file path) | verified | partial | mismatched | `[verified-via ls Phase 1]` — 244 jsonl files 실재 |

**3-way decision tree** (CFP-1355 Change Plan §3.first_step verbatim):

```
IF M-1 ≥ 80% AND M-2 = 4/4 AND M-3 ∈ {identical, convertible} AND M-4 = verified
THEN gate_result = pass → sub-area b/c/d 병렬 진입 허용 + §결정 1-10 모두 적용

ELIF M-1 50-80% OR M-2 2-3/4 OR M-3 = convertible OR M-4 = partial
THEN gate_result = partial → Partial wrapper scope (context-only resume + in-process state 재구성 의무)

ELSE THEN gate_result = fail → sub-area b/c/d ABORT, sub-area e 만 carry-over (negative ADR — why-not external wrapper)
```

### §결정 8 — Rate-limit detection

| Element | Mechanism |
|---|---|
| Detection invoke | `claude --print "noop"` (`--print` 모드 한정) |
| Header parse | stderr / response header 안 `anthropic-ratelimit-unified-5h-reset` (Unix epoch UTC strict, ADR-079 contract field layer 무손상) |
| Next trigger compute | `[DateTime]::UnixEpoch.AddSeconds($resetEpoch).ToLocalTime()` (Windows local time) |
| Task Scheduler mutate | `schtasks /Change /TN <task-name> /ST <hh:mm>` next trigger time |
| Detection 4-tuple (Story A cross-ref) | `"rate limit"` / `"quota exceeded"` / `"429"` / `"Server is temporarily limiting"` any-match |

**Disjoint axis cross-ref**: ADR-057 §결정 2 in-process Sonnet→Opus model-tier fallback (CFP-1354 Story A scope) ≠ 본 §결정 8 OS-external 5h reset header polling (본 Story B scope). disjoint mechanism layer.

### §결정 9 — Fallback path

| Trigger | Fallback |
|---|---|
| Task Scheduler trigger failure (3회 exhaust) | manual user resume + Windows Toast notification |
| Fidelity-fail (§결정 7 gate result = fail) | wrapper script disabled + 사용자 escalation (negative ADR carry-over 'why-not external wrapper') |
| UUID file corruption / disk full | manual session restart + Windows Toast notification (auto-resume abort) |

**ADR-057 §결정 2 invariant 보존**: "자동 재시도 금지" axis disjoint 정합 — Story A in-process retry (model-tier substitution) 와 분리 영역, 본 §결정 9 fallback = OS-external session-dead 후만 활성.

### §결정 10 — VS Code extension parallel session 충돌 차단

| Mechanism | Scope |
|---|---|
| Local mutex acquire | §결정 6 정합 |
| VS Code session active check | wrapper invoke 직전 best-effort process enumeration (`Get-Process Code` exists?) |
| 2-channel disjoint notify | extension suspend signal + wrapper resume signal 분리 (extension lifecycle 영역 외부, wrapper notify channel 만) |

**Not strict** (wrapper 가 별도 process 이므로 perfect coordination 불가 — Phase 2 telemetry refine 영역). extension upstream API exposure 시 strict coordination 영역 후속 sub-CFP carrier.

## 결과

- OS-level external wrapper (PowerShell + Task Scheduler) 가 codeforge plugin SSOT 와 disjoint layer 명시 — wrapper SSOT 가 codeforge SSOT path write 0건 invariant
- ADR-053 Amendment 2 (D1 trigger TYPE 6번째 entry `external-wrapper-invoked session resume`) sibling carrier 정합 — wrapper resume 시 codeforge SSOT 가 새 session 안 재로딩됨 (D1 5 기존 trigger 와 axis 동형)
- Phase 2 design+implementation lane 진입 시 §결정 7 empirical fidelity test gate 의무 — 4-source measurement (M-1/M-2/M-3/M-4) 실 실행 후 3-way decision tree 분기 (pass / partial / fail)
- fidelity-fail 시 sub-area b/c/d 전체 ABORT + sub-area e (ADR + domain-knowledge) 만 carry-over (negative ADR 'why-not external wrapper' codify)
- wrapper script Linux/macOS 환경 = explicit abort (Phase 2 bash equivalent sub-CFP carrier)
- 사용자 control: kill-switch (Task Scheduler disable via `schtasks /Delete` 또는 GUI) + retry counter ≥ 3 시 manual resume 선택지

**문서 변경**:
- 본 ADR (`docs/adr/ADR-110-external-runtime-wrapper-ssot-boundary.md`) 신규 — Phase 1 carrier
- ADR-053 Amendment 2 (`docs/adr/ADR-053-structural-change-restart-prerequisite.md`) — D1 trigger TYPE 6번째 entry append, Phase 1 carrier
- ADR-RESERVATION row 109 append (`docs/adr/ADR-RESERVATION.md`) — Phase 1 carrier
- Domain-knowledge entry (`docs/domain-knowledge/domain/runtime/external-session-auto-resume.md`) 신규 — Phase 1 carrier
- Story §7-§14 + Change Plan + Phase 2 carrier (`scripts/codeforge-session-resume.ps1` + `templates/scheduler/codeforge-auto-resume.xml` + `tests/wrapper-resume.Tests.ps1` + `docs/consumer-guide.md` §1j 신설 + CLAUDE.md + playbook + plugin.json 6.5.3 → 6.5.4 + marketplace sync)

## 해소 기준

N/A — permanent policy (`is_transitional: false`, Windows Task Scheduler / PowerShell wrapper = 운영 영구 영역, ADR-058 §결정 7 보안 ADR default presumption false 정합).

## 관련 파일

- [ADR-053](ADR-053-structural-change-restart-prerequisite.md) — Amendment 2 sibling carrier (D1 trigger TYPE 6번째)
- [ADR-057](ADR-057-orchestrator-opus-mandate-and-sonnet-opus-fallback.md) — model-tier substitution disjoint axis cross-ref
- [ADR-068](ADR-068-boundary-completeness-invariants.md) — I-3 conditional guard + I-5 dimensional empirical grounding
- [ADR-070](ADR-070-codex-verify-before-trust.md) — §D6 mandatory-real-execution-evidence STANDING
- [ADR-073](ADR-073-orchestrator-verify-before-assert.md) — verify-before-assert (본 Story chief author write-time pre-publish FIX 영역)
- [ADR-082](ADR-082-write-time-self-write-verification-mandate.md) — Amendment 7 backward-staleness catch (chief packet ADR-110 → ADR-109 (chief downgrade due to PR-pending state unaware) → ADR-110 (Orchestrator post-chief correction, sibling collision avoid))
- [ADR-083](ADR-083-consumer-applicability-filter.md) — consumer-applicability mixed 분류 (wrapper + consumer install layer)
- [ADR-085](ADR-085-multi-session-collaboration-protocol.md) — active_sessions[] dual carrier
