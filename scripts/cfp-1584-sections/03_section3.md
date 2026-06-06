## 3. 스폰 시퀀스 + 프롬프트 템플릿

### 3.0 Orchestrator execution mode — Default subagent (수정 작업) (ADR-039)

> **NORMATIVE SSOT (ADR-039 §결정 1·2 codification)**. 본 §3.0 = wrapper / consumer Orchestrator 의 매 codeforge 수정 작업 행위 직전 reading 의무 영역. 본 단락이 4 SSOT doc cross-ref tree 의 root.

#### §3.0.1 결정 stmt

codeforge 수정 작업 = Orchestrator default **subagent spawn**. "inline 으로 충분한가 vs subagent 가 나은가" 결정 분기 **자체 금지** — branch logic 제거 = ADR-025 §결정 7 `policy_violation_subdecision` 발화 채널 차단.

#### §3.0.2 수정 작업 정의 (closed enumeration — ADR-039 §결정 1)

- file edit / write (`docs/**`, `src/**`, `templates/**` 포함)
- GitHub state change (Issue / PR / comment / label / milestone / sub-issue / branch / merge)
- Story file write (§1-§14 어느 섹션이든)
- FIX Ledger §10 row append (fix-event-v1 contract — Amendment: Orchestrator-owned delegate subagent 포함)
- Lane-spawn evidence §14 row append (ADR-031 — Amendment 1: Orchestrator-owned delegate subagent 포함)
- gate label transition (`gate:design-review-pass` 등)
- phase label transition (`phase:요구사항` → `phase:설계` 등)
- workflow yaml 수정·추가
- ADR / Change Plan / domain-knowledge 페이지 write
- **trivial Read 1건 도 spawn 의무** (사용자 verbatim 명시 — Story CFP-275 AC-3 trivial-threshold-zero)

#### §3.0.3 Inline whitelist (closed 4-entry — ADR-039 §결정 2)

| # | Category | 설명 | Mechanism rationale |
|---|---|---|---|
| 1 | 사용자 dialog | `AskUserQuestion` / 확답 step / 정보 요청 답변 (Yes/No / 옵션 선택) | Subagent one-shot 이라 continuous dialog 자체 mechanism 불가능 (ADR-009 §결정 + "플랫폼 제약") |
| 2 | TodoWrite scratchpad | progress visualization marker write | TodoWrite = file write 아님, Orchestrator scratchpad / meta progress channel — 수정 작업 enumeration 미포함 |
| 3 | Read-only Q&A 답변 | 사용자 정보 요청 응답 (state report / option enumeration / 도메인 설명) | 수정 작업 아님 — codeforge orchestration scope 외 |
| 4 | Status report | Phase 완료 / Story close / final report | 수정 작업 아님 (read-only synthesis) — ADR-025 Amendment 1 §결정 11 의 "1번 final report" |

4 entry **외** 의 모든 codeforge orchestration 행위 = subagent spawn 의무. **모호 시 = 수정 작업 측 분류** (안전 방향 — ADR-013 cutoff precedent 정합). 5번째 카테고리 추가 = ADR-039 amendment 의무.

**Skill 호출 분류 (Change Plan §3.0.2 mirror)**: Skill 호출 (`superpowers:brainstorming` / `writing-plans` / `verification-before-completion` / `executing-plans` / `dispatching-parallel-agents` 등) = **Inline** (5번째 entry 추가 X — closed 4-entry 보존). Skill = wrapper around tool calls (file write / GitHub state mutation 자체 미발화 — meta wrapper). Skill 내부 individual tool call (Read / Edit / Write / mcp__github__\* / Agent / Bash) level 에서 spawn 분류 발동 — ADR-039 §결정 1 자연 routing.

#### §3.0.4 Dialog turn separation (Story CFP-275 AC-5 / Change Plan §3.0.1 — normative)

사용자 dialog (Inline whitelist entry 1) 와 dialog 직후 state change (subagent spawn 의무 영역 — file edit / GitHub state / Story write / FIX Ledger / label transition 등) 는 **별도 turn / message** 로 분리한다. 한 메시지 안에서 inline write + dialog 동시 수행 = `policy_violation`.

#### §3.0.5 구현 실행 방식 — Subagent-Driven 자동 선택 (CFP-358 / CFP-374)

`superpowers:executing-plans` 또는 `superpowers:subagent-driven-development` 스킬 실행 중 "구현 실행 방식 선택" 프롬프트(Subagent-Driven vs Inline Execution)가 발생하면, `AskUserQuestion`으로 사용자에게 묻지 않고 **자동으로 Subagent-Driven 경로를 선택**해 진행한다.

**스킬 지시 우선순위 override (CFP-374)**: 스킬 파일이 `AskUserQuestion`을 호출하도록 지시하더라도, 이 §3.0.5 정책이 스킬 내용보다 우선한다. 스킬을 로드한 후 "구현 실행 방식" 선택지를 발견하면:
1. `AskUserQuestion` 호출 없이 해당 단계를 건너뛴다.
2. Subagent-Driven 경로로 **직접 진입**한다.
3. 사용자에게 선택을 묻는 어떤 형태의 확인도 하지 않는다.

이 정책은 wrapper + 모든 consumer에 동일 적용. behavioral directive → memory 저장 금지 (normative) 케이스 — playbook이 enforcement SSOT.

**Generalized normative SSOT (ADR-064 §결정 10, Amendment 3 CFP-637)**: 본 §3.0.5 (Subagent-Driven 자동 선택) 와 동일 패턴 (skill body 안 AskUserQuestion 지시 override) 은 **ADR-064 §결정 10 Skill body ↔ CLAUDE.md normative priority precedence** 로 generalize. CLAUDE.md normative > ADR > skill body > external skill body. 본 §3.0.5 = §결정 10 의 specific case (CFP-358 / CFP-374 carrier), §결정 10 = 전체 skill body 영역 generalized precedence (codeforge:brainstorm Phase 1 dialog reflex / superpowers:brainstorming checklist 등 포함).

#### §3.0.6 Ownership ≠ Mechanism 분리 (ADR-039 §결정 3 + §결정 12)

본 정책은 **mechanism (어떻게 수행)** 변경. **ownership (누가 작성권)** 무변.

- Orchestrator monopoly ownership (유지 — invariant 무손상):
  - Story §10 FIX Ledger row append (CFP-32 / fix-event-v1 contract)
  - Story §14 Lane Evidence row append (ADR-031 / CFP-126)
  - review-verdict v3 final write (Story §9 / GitHub comment / gate label / phase transition)
  - branch protection / CI workflow / cross-plugin schema templates
- Mechanism (변경): 위 ownership 영역의 file write / GitHub state change 도 **subagent spawn 으로 수행**. Orchestrator 가 "§10 row append 전용 subagent" / "§14 row append 전용 subagent" / "label transition 전용 subagent" 를 spawn 해 Edit / mcp__github__\* tool 호출.

**Orchestrator 정의 확장 (ADR-031 Amendment 1 + fix-event-v1 Amendment, CFP-275)**: "Orchestrator self-write" / "Writer monopoly v1: Orchestrator 단독" = top-level Claude 세션 + **Orchestrator 가 §10/§14 row append 전용으로 spawn 한 delegate subagent** 모두 포함. lane plugin agent 가 자체 임의 §10/§14 직접 append 는 여전히 금지 (lane plugin spawn ≠ Orchestrator-owned delegate spawn).

#### §3.0.7 Phase 1 doc-only trust model (ADR-039 §결정 8)

매 Orchestrator 행위 시 (1) ADR-039 / (2) 본 §3.0 / (3) CLAUDE.md "Default subagent context (수정 작업)" / (4) consumer-guide § "Subagent default (codeforge orchestration)" / (5) hotfix-playbook 1줄 reading 시 자체 인지. 자동 enforcement 부재. ADR-025 / ADR-029 precedent 정합 (Phase 1 doc-only trust pattern).

Phase 2 enforcement (stop-event-v1 ledger / inline write detect hook / spawn cost telemetry / rate-limited error second-order risk 측정) = ADR-039 §결정 9 deferred follow-up CFP.

#### §3.0.8 Cross-ref

- **Policy SSOT**: [ADR-039](../docs/adr/ADR-039-orchestrator-subagent-default-for-codeforge-modification-work.md) (amends ADR-009)
- **Motivation**: [ADR-025](../docs/adr/ADR-025-stop-discipline-non-whitelist-as-defect.md) §결정 7 (`policy_violation_subdecision`)
- **Narration interaction**: [ADR-029](../docs/adr/ADR-029-phase-execution-visibility-expansion.md) (매 spawn / return narrate 의무)
- **§14 evidence**: [ADR-031](../docs/adr/ADR-031-lane-spawn-evidence-trail.md) Amendment 1 (Orchestrator-owned delegate inclusion)
- **§10 FIX Ledger**: [fix-event-v1](../docs/inter-plugin-contracts/fix-event-v1.md) Amendment (Orchestrator-owned delegate inclusion)
- **TodoWrite scratchpad**: TodoWrite tool surface 자체 standalone 정당화 (file write 아님 — meta progress channel). ADR-041 = informational reference, normative dep 아님 (PR #277 머지 order 무관).
- **Subagent semantics 분기**: [ADR-035](../docs/adr/ADR-035-codeforge-agent-teams-epic-architecture.md) (default subagent context 의 one-shot subagent — `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=0`)
- **Consumer scope**: [consumer-guide.md § "Subagent default (codeforge orchestration)"](consumer-guide.md)
- **Hotfix scope**: [hotfix-playbook.md](hotfix-playbook.md) (exception 없음 — 사용자 verbatim "무조건")

#### §3.0.9 Pre-action fact verification (normative — wrapper + all consumers)

Orchestrator 가 사용자에게 substantive path 를 제시하거나 외부 system 동작을 인용하기 전, 아래 5-item self-audit 의무:

| 항목 | verify 도구 | skip 금지 조건 |
|---|---|---|
| 인용 file / 디렉터리 실제 존재 여부 | `Glob` / `Bash ls` | path 를 사용자에게 제시하는 모든 경우 |
| workflow / Action trigger 조건 | `Read` | "자동으로 X 가 일어남" 주장 전 |
| schema / config 실제 fields | `Read` | structured contract 인용 전 |
| GitHub Issue / state | `mcp__github__issue_read` | Issue 상태 주장 전 |
| 사용자 환경 state | `Read ~/.claude/settings.json` 또는 `Bash which` | 설치 여부·인증 상태 주장 전 |

**Hedging 금지 신호 (이 단어 응답에 등장 시 verify 의무)**:
- "should be" / "보통" / "~로 추정" / "~일 것" / 외부 system 동작 가정

**Subagent 답 weak signal**: subagent 응답에 "추정" / "확인 필요" / "공식 미기재" 등장 시 main session 에서 fact 직접 검증.

5초 cost verify 로 방지 가능한 사실은 추론으로 답변 금지.

#### §3.0.10 Internal-docs branch safety (normative — codeforge dogfood 작업 시)

`codeforge-internal-docs` working directory 는 외부 프로세스(사용자 IDE / 별도 터미널 / 별도 Claude 세션)가 언제든 branch 를 switch 할 수 있다. 매 commit 전 의무:

1. **Branch verify — 단독 Bash call (chained 금지)**:
   ```bash
   git -C c:/workspace/mclayer/codeforge-internal-docs branch --show-current
   ```
   출력이 intended branch 와 일치 확인. 불일치 시 즉시 stash + checkout intended branch.

2. **Push 전 dry-run — 단독 Bash call**:
   ```bash
   git -C c:/workspace/mclayer/codeforge-internal-docs push --dry-run origin <branch>
   ```
   `main -> main` 출력 시 즉시 abort + branch verify.

3. **Chained `&&` 명령에서 branch verify 금지**: `git branch --show-current` 는 항상 exit 0 → verify 결과와 무관하게 다음 단계 진행. verify = 반드시 단독 call + 출력 확인 후 다음 call.

4. **main / master force push 절대 금지**. 사고 발생 시: cherry-pick → correct branch → push (force push X).


#### §3.0.11 Worktree-first mandate (normative — wrapper + all consumers)

모든 coding work 는 git worktree 안에서 수행. 원본 working directory(`git checkout <branch>`) 직접 편집 금지.

- **Story 시작 시**: `bash templates/scripts/worktree-create.sh cfp-NNN origin/main` 선행 → cwd = worktree path
- **Subagent spawn 시**: prompt 에 `Working dir: <worktree-path>` 명시 — lane spawn (§3.5) 과 ad-hoc spawn 동일. **추가 `git -C <worktree_abs_path>` directive (ADR-040 Amendment 6 / CFP-843)**: 모든 file operation (git command + Write/Edit absolute path, forward-slash 정규형) 을 worktree abs path 기준 강제 — harness cwd reset gap 차단 (§3.5 SSOT)
- **Ad-hoc 작업 포함**: lane spawn 외 일반 subagent spawn, 사용자 직접 작업 모두 동일 적용
- **Consumer 동일 적용**: consumer project 에서 codeforge 사용 시 동일 rule
- **위반 판정**: 원본 working directory 에서 file edit/write/bash 수행 = stop discipline 위반 (ADR-025 §결정 2 `policy_violation`)

인프라 SSOT: ADR-040 (CFP-136). Script: `bash templates/scripts/worktree-create.sh <branch> <base-ref>`.

#### §3.0.12 Rate-limit Fallback (ADR-057)

Agent tool이 Sonnet subagent spawn 결과로 rate-limit 에러를 반환하면:

1. 동일 입력 패킷으로 `model: opus` 재spawn (1회 한정)
2. 재spawn 성공 시 §14 Lane Evidence row에 `[rate-limit-fallback:sonnet→opus]` 태그 추가 후 정상 진행
3. Opus도 실패 시 사용자에게 상황 통지 → 대기 (자동 재시도 루프 금지)

판별 기준: Agent tool result에 "rate limit", "quota exceeded", "429" 포함 시 rate-limit로 분류.

#### §3.0.13 PR description `## Lane evidence` manual append 정책 (CFP-507)

Phase 2 PR description 안 `## Lane evidence` row append 시 Orchestrator (또는 Orchestrator-owned delegate subagent — §3.0.6 정합) 가 아래 3-step 절차를 준수한다. 본 정책은 CFP-490 (#490, merged) §7.5 origin investigation 의 carrier — codeforge-develop sibling plugin DeveloperPLAgent body composition convention (`agents/DeveloperPLAgent.md` "Phase 2 PR body composition convention" section) 와 짝.

**3-step 절차**:

1. **기존 heading 존재 check** — `grep '^## Lane evidence' <PR description body>` 또는 GitHub MCP `mcp__github__pull_request_read` 로 PR body fetch 후 line-prefix match
2. **존재 시 row 만 append** — 기존 `## Lane evidence` heading 다음 lane row 7개 영역 안 적절 lane row 의 status 갱신 (`<PASS|SKIPPED|FIX|ESCALATED|BYPASS>`). **heading 재추가 금지** — 두 번째 `## Lane evidence` heading 발생 시 `lane-evidence-check.yml` 5a duplicate guard 발화 (CFP-490 §결정 1 정합)
3. **부재 시 heading + 7-row template inject** — `## Lane evidence` heading + 7-row format (wrapper `templates/github-pr-template.md` SSOT line 79 verbatim 정합):
   ```
   ## Lane evidence

   - 요구사항: <PASS|SKIPPED|FIX|ESCALATED|BYPASS>
   - 설계: <PASS|SKIPPED|FIX|ESCALATED|BYPASS>
   - 설계-리뷰: <PASS|SKIPPED|FIX|ESCALATED|BYPASS>
   - 구현: <PASS|SKIPPED|FIX|ESCALATED|BYPASS>
   - 구현-리뷰: <PASS|SKIPPED|FIX|ESCALATED|BYPASS>
   - 구현-테스트: <PASS|SKIPPED|FIX|ESCALATED|BYPASS>
   - 보안-테스트: <PASS|SKIPPED|FIX|ESCALATED|BYPASS>
   ```

**동시 동기화 의무 (ADR-031 정합)**: Story §14 Lane Evidence row append 와 PR description row append 는 **동일 turn / 단일 spawn cycle** 안에서 동시 처리. 두 영역 drift 시 §14 = SSOT (ADR-031 §결정 3 enforcement layer 우선), PR description 은 mirror.

**위반 시 guard 발화**: `lane-evidence-check.yml` workflow 의 5a tie-break case A/B/C (CFP-490 §결정 1) 가 duplicate `## Lane evidence` heading 또는 7-row format 위반을 detect → PR 차단 + audit comment. Bypass channel = `hotfix-bypass:lane-evidence-check` label (ADR-024 Amendment 3 정합).

**Cross-ref**:
- codeforge-develop `agents/DeveloperPLAgent.md` "Phase 2 PR body composition convention" — agent body composition layer
- wrapper `templates/github-pr-template.md` line 79 — heading 형식 SSOT
- ADR-031 §결정 3 — §14 Lane Evidence enforcement layer
- CFP-490 §결정 1 — `lane-evidence-check.yml` 5a guard tie-break

#### §3.0.14 Stop-time 평문 정리 + 표현 맥락 파악·문장 구조 self-check (Amendment 2 신설, CFP-610)

ADR-064 §결정 3 룰 6 + §결정 9 의 playbook-side 운영 매뉴얼. SSOT = [ADR-064 §결정 3 룰 6 / §결정 9](../docs/adr/ADR-064-decision-principle-mandate.md). CLAUDE.md "Stop-time 평문 정리 (Trace 5)" 단락 = summary mirror.

**룰 6 — 표현 발화 전 self-check**:

Orchestrator 가 사용자 응답 발화 직전 다음 4 항목 self-check:
1. 직전 turn 의 핵심 결정 / 미해결 분기점
2. 사용자 발화 요지 (지금 무엇을 묻는가 / 무엇을 지시하는가)
3. 현재 진행 단계 (Phase 0 brainstorm / Phase 1 dialog / Phase 2 implementation / spec 작성 / FIX 루프 / lane spawn 등)
4. 문장 구조 — cold reader 가독성 (완전한 문장 / jargon 사전 점검 ([`docs/wording-dictionary.md`](../docs/wording-dictionary.md) 카테고리 a/b) / 식별자 평문 요약 (룰 3 정합) / 다중 분기 numbered list 분리 (룰 4 정합))

실패 signal — 사용자 frustration 발화 (예: "이게 무슨 말이냐") 시 retro audit 의무 (PMOAgent retro file §wording-discipline 표).

**§결정 9 — Stop-time 300자 평문 정리 + Question quality 3-check (Amendment 3 강화, CFP-637)**:

Orchestrator 가 사용자 dialog turn 종료 시 다음 의무:

**(a) 300자 ± 50자 평문 정리**:
- 포함 항목: 직전 turn 핵심 결정 / 다음 step / 미해결 분기
- 생략 가능: tool_use only turn (TodoWrite / Read Q&A 답변 / Status report 평문 자체) — ADR-039 Inline whitelist 4-entry 정합
- 적용 범위: wrapper + 모든 consumer (CLAUDE.md L208 normative 정합)

**(b) Question quality 3-check (Amendment 3 신설, CFP-637)** — 질문 형식 / 결정 option 발화 직전 self-check:

1. 가치 판단 영역인가? (사용자 선호도 / 가치 판단 기준 / 미공개 컨텍스트 요구)
2. derived default 자명한가? (Epic body / Story context / ADR / 사용자 직전 발화 누적)
3. 1-option 만 있는데 묻는 것 아닌가? (옵션 분기 자체가 무의미한 영역)

판정 로직: 위 3 중 1+ "묻지 말아야 함" → **발화 금지**, derived default declare + 결과 보고 + 진행 (사용자 정정 의무).

7 anti-pattern P1-P7 차단 carrier (Epic CFP-635 body §Anti-pattern enumeration verbatim):
- **P1**: Implementation detail 결정 묻기 (ADR scope / version bump option 등 derive 가능 영역)
- **P2**: Skill body 가이드라인 무비판 수렴 (skill body 가 normative 보다 우선시) — §결정 10 carrier
- **P3**: 1-option 만 있는데 "그대로 진행할지?" 묻기
- **P4**: Confirm-of-confirm ("진행해" 직후 또 묻기)
- **P5**: Status report 가 사실은 질문 ("미해결 분기" implicit confirm)
- **P6**: 3-option 자동 발사 (numbered list reflex)
- **P7**: Continuous "진행해" 패턴 인지 실패 (5+ turn 연속에도 dialog format 시작)

**강제 강도**: behavioral directive only — mechanical enforce 불가 (turn-final hook 부재). retro audit signal (PMOAgent retro file §wording-discipline + §over-questioning 표) + sunset gate metric (frustration 발화 0건 / 3 Story 누적). sister Story CFP-638 = Continuous "진행해" 패턴 partial mechanical detect carrier.

**Continuous "진행해" 패턴 detect (Amendment 3 sister, CFP-638)** — Orchestrator self-check (mechanical hook layer 부재 시 1차 안전망):

직전 N (≥3) user turn 안 다음 pattern 누적 detection:
- "진행해" / "그대로" / "계속" / "ok" / "yes" / "go" / "맞아" / "맞다"

3+ 연속 → 후속 turn 의 dialog format (numbered list / decision option / "권장 = ..." 형식) 발화 자동 차단. **declare + 결과 보고 only** (사용자 정정 의무, §결정 3 룰 1 정합).

5+ 연속 누적 → strong brevity signal. 후속 turn 은 numbered list 자체 발화 금지 (§결정 9 3-check 의 1+ 자동 trigger).

mechanical layer: `docs/evidence-checks-registry.yaml` entry `stop-time-continuous-confirm-detect` (CFP-638, warning tier, advisory only — turn-final hook 부재 platform 한계). retro audit signal SSOT = PMOAgent retro file §over-questioning 표 — Story 단위 frustration count + "진행해" repetition trace tracking.

미래 mechanical hook 도입 = 별도 CFP follow-up (PreToolUse / PostToolUse hook 안 AskUserQuestion / numbered list output detection, platform hook capability 확장 의존).

**wording dictionary 참조**: [`docs/wording-dictionary.md`](../docs/wording-dictionary.md) — 카테고리 (a) forbid + 카테고리 (b) 평문 정의 의무 entry SSOT.

**§결정 10 — Skill body ↔ normative precedence (Amendment 3 신설, CFP-637)**:

**Priority order**: CLAUDE.md normative > ADR > skill body > external (superpowers / claude-plugins-official / 외부 plugin) skill body.

skill body 안 "AskUserQuestion" / "사용자 confirm" / "확인" / "묻기" / dialog format 지시는 §결정 3 룰 1 (Derived default) + §결정 9 3-check 보다 후순위. derived default 자명 영역에서 skill body 지시 무시 의무.

Implementation pattern:
1. Skill 호출 시 skill body 안 AskUserQuestion / confirm 지시 발견
2. §결정 9 3-check 적용 — derived default 자명한가?
3. 자명 → skill body 지시 무시, derived default declare + 진행
4. 비자명 + 진짜 가치 판단 영역 → skill body 지시 적용 (AskUserQuestion 발화 허용)

Generalized precedent (CFP-358 / CFP-374):
- CFP-358 `superpowers:executing-plans` "구현 실행 방식 선택" → Subagent-Driven 자동 선택 (§3.0.5)
- CFP-374 `superpowers:subagent-driven-development` 동일

첫 applied case = `skills/codeforge-brainstorm/SKILL.md` Phase 1 dialog reflex 차단 (Amendment 3 Story B). cross-plugin sister Story CFP-639 = `superpowers:brainstorming` upstream PR carrier (wrapper 측 mitigation = 본 §결정 10 normative override 명시로 covered).

**적용 범위**: wrapper + 모든 consumer + 모든 skill (codeforge:* / superpowers:* / claude-plugins-official:* / 외부 plugin skill).

#### §3.0.15 Parallel Dispatch Protocol (CFP-609 / ADR-064 Amendment 1)

Orchestrator 가 lane PL agent spawn 시 **plan task DAG 분석 결과를 spawn prompt 에 기재** 의무. ADR-064 §결정 4 (Trace 4) "Orchestrator multi-task spawn default = parallel" normative declaration 의 execution-time enforcement carrier.

**SSOT** = [`docs/inter-plugin-contracts/parallel-dispatch-protocol-v1.md`](inter-plugin-contracts/parallel-dispatch-protocol-v1.md) (kind:registry, wrapper canonical, sibling sync 면제). 본 §3.0.14 = registry SSOT 의 1줄 요약 + 4 의무 항목 + 6 enum + 4-분기 cross-ref (DRY 구조 — verbatim mirror 차단).

**4 의무 항목** (Orchestrator → PL spawn prompt — registry §4 full schema):

1. plan DAG 분석 결과 batch list verbatim 기재 (registry §4.1)
2. PL 에 자율 병렬 권한 명시 — `pl_autonomous_parallel_authority: required` 3-value enum 중 `required` default (registry §4.2)
3. sequential 의무 영역만 명시 — 6 enum 중 해당만 (registry §4.3)
4. file-level conflict resolution 패턴 기재 — same-file-different-method / same-file-different-section / same-file-same-method (registry §4.4)

**6 sequential mandate enum** (close-set — full SSOT: registry §3):

`tdd_red_phase` / `schema_migration` / `adr_reservation_append` / `fix_ledger_append` / `sibling_sync_ordering` / `marketplace_sync_ordering`

**PL 자율 병렬 결정 tree 4-분기** (full SSOT: registry §5):

1. plan 의 parallel_with hint 있음 → multi-instance 병렬
2. parallel_with hint 부재 + 파일 disjoint + interface 의존 0 → 자율 병렬 (default)
3. same-file-different-method + commit atomic 분리 capability 보유 → 병렬 + merge 시점 sync (capability 부재 시 4번 fallback)
4. same-file-same-method 또는 schema_migration → sequential 의무 (6 enum 중 해당 명시)

**위반 시**: ADR-064 §결정 4 위반. spawn prompt 에 sequential 선택 사유 명시 없이 sequential dispatch = ADR-039 §결정 7 `policy_violation_subdecision` 발화 채널.

**Mechanical enforcement**: `parallel-dispatch-prompt-check` warning tier lint (ADR-060 evidence-enforceable framework 정합) — `scripts/check-parallel-dispatch-prompt.sh` + `templates/github-workflows/parallel-dispatch-prompt-check.yml` (`continue-on-error: true`, bypass label `hotfix-bypass:parallel-dispatch-prompt`).

**env=0 / env=1 동등성** (registry §6.4):
- env=0 (default subagent context, ADR-039) — Orchestrator round-trip polyfill, PL 이 batch N task multi-instance subagent dispatch 1 round trip 안에 spawn
- env=1 (agent teams, ADR-044) — TeamCreate + SendMessage continuous dialog, Lead ↔ Worker

**Cross-ref**:
- ADR-064 §결정 4 Trace 4 + Amendment 1 — normative SSOT + implementation contract carrier
- ADR-039 §결정 7 `policy_violation_subdecision` — 위반 발화 채널
- ADR-044 §결정 2 `dispatch_mode` enum — env=1 직교 차원
- ADR-056 — team-spec-requirements 6-way teammates (CFP-609 absorb)
- ADR-060 — evidence-enforceable promotion framework (warning tier entry)
- §12 spawn prompt template — `[Parallel Dispatch Hint]` block 기재 의무 (registry §4.1 verbatim)

#### §3.0.16 — DeveloperPL + branch-creating subagent pre-spawn-pin mandate (CFP-895 / ADR-039 Amendment 1)

ADR-039 §결정 14 (Amendment 1) 의 Orchestrator-side codification. DeveloperPL 또는 새 branch 를 생성하는 subagent (codeforge-develop:DeveloperAgent / role:dev 등) 가 Phase 2 PR open 또는 cross-repo paired PR open 시 stale base 회피 mandate.

**Orchestrator 의 의무 절차** (subagent return 직후):

1. **post-spawn verify** — `mcp__github__pull_request_read get` 의 `head.sha` parent commit 을 `mcp__github__list_commits sha=main perPage=1` (또는 `gh api repos/<owner>/<repo>/commits/main --jq .sha`) 와 비교.
2. **mismatch detection** — branch HEAD parent ≠ current origin/main 이면 stale-base → 즉시 **FIX trigger** (구현-side, RESET=NO).
3. **re-dispatch 의무** — 동일 subagent 재spawn 시 prompt 에 (a) explicit current-main-HEAD SHA (Orchestrator 가 방금 고정한 값) + (b) "self-reset 금지 / 기존 작업 content 보존, only rebase the base" + (c) 추가 mid-flight churn 대비 "rebase 시 main HEAD 재고정 (parallel session advance 가능)" 명시.
4. **§10 FIX Ledger row append** — stale-base rebase iteration = Orchestrator monopoly write (fix-event-v1 contract, CFP-32). 형식 = `구현 (Orchestrator verify-before-trust, 구현리뷰 이전 적발)` lane.

**근거 evidence**: CFP-699/CFP-702/CFP-848 3차 누적 (ADR-039 Amendment 1 §결정 14 표).

**SubAgent prompt Step 0 의무** — Orchestrator 가 DeveloperPL spawn 시 packet 에 다음 Step 0 명시:

```text
