---
name: codeforge-brainstorm
description: codeforge 프로젝트 전용 brainstorming — Requirements 에이전트 4종 병렬 컨텍스트 수집 후 강화된 설계 대화 진행. ADR-034 Amendment 1에 의해 Stage 0 공식 스킬로 지정. Amendment 2 (CFP-386) 에 의해 Phase 0 자동 실행.
---

# codeforge:brainstorm Skill

codeforge 프로젝트에서 `superpowers:brainstorming`을 대체하는 강화 brainstorming 스킬.

## 적용 조건

- `.claude/_overlay/project.yaml` 존재 (codeforge consumer 프로젝트)
- 또는 `docs/adr/` 디렉터리 존재 (wrapper dogfood 프로젝트)

조건 불충족 시 `superpowers:brainstorming`으로 fallback.

## Phase 0 진입 정책 (ADR-034 Amendment 2 — CFP-386)

스킬 발동 시 **Phase 0 을 자동 실행** — 별도 사용자 확인 (AskUserQuestion) 없이 즉시 4 개 에이전트를 병렬 spawn.

근거: 매 호출마다 동일 비용 경고 = 학습된 reflex 가 되어 productivity 만 저해. 호출 시점에 이미 비용 발생 의사 표명됨. CFP-358 / CFP-374 의 Subagent-Driven 자동 선택 패턴 정합.

### 사용자 cost-out 경로 (Phase 0 skip)

Phase 0 의 비용 (ResearcherAgent Opus tier 포함 4 에이전트 병렬 spawn) 을 원하지 않는 경우, `codeforge:brainstorm` 대신 `superpowers:brainstorming` 을 **직접 호출**한다. 이 경우 Phase 0 가 수행되지 않고 일반 brainstorming 만 진행 (Amendment 1 의 fallback 경로 유지).

## Phase 0: 병렬 에이전트 burst

4개 에이전트를 **동시에** spawn. Agent tool 4 calls in parallel.

> **템플릿 변수 주의**: `{USER_IDEA}`, `{OPEN_EPICS}`, `{DESIGN_SUMMARY}`는 Orchestrator가 에이전트 spawn 직전 실제 값으로 대체한다. 스킬 파일 내 이 변수들은 "여기에 해당 내용을 삽입하라"는 지시이며 실제 코드가 아니다.

### DomainAgent 프롬프트 템플릿

```
당신은 codeforge DomainAgent입니다.
사용자의 아이디어: {USER_IDEA}

docs/domain-knowledge/ 디렉터리를 읽고 이 아이디어와 관련된
핵심 도메인 사실 5개 이내를 300자 이내로 요약하세요.
추론 없이 사실만. 존재하지 않으면 "관련 domain-knowledge 없음"으로 응답.
```

### ResearcherAgent 프롬프트 템플릿

```
당신은 codeforge ResearcherAgent입니다.
사용자의 아이디어: {USER_IDEA}

이 아이디어의 unknown unknowns와 핵심 개념을 탐구하세요.
출력 형식 (500자 이내):
- 핵심 개념 3개: [개념명: 1줄 설명]
- Unknown unknowns 2개: [발견한 암묵적 가정 또는 위험]
추론 근거 생략. 결론만.
```

### RequirementsAnalystAgent 프롬프트 템플릿

```
당신은 codeforge RequirementsAnalystAgent입니다.
사용자의 아이디어: {USER_IDEA}

**먼저 WHY를 추출하세요.** 사용자가 이것을 요구하는 근본 동기·필요·배경을 파악합니다.
지식 부족이나 선입견으로 인해 실제 필요와 다른 방향을 요청했을 가능성을 항상 고려하세요.

**WHY를 렌즈로 요구사항을 확장하세요.** 사용자가 명시한 것(what)이 아니라 파악한 동기(why)를 기준으로 AC를 도출합니다. why가 충족되려면 사용자가 미처 언급하지 않은 요구사항까지 포함해야 합니다.

출력 형식:
- 추정 동기 (why): [이 요청의 근본 필요 1~2줄]
- 명시된 요구 ↔ 실제 필요 일치 여부: 일치 / 불일치 가능성 있음 (사유 1줄)
- why 기반 확장 요구사항: [명시되지 않았지만 동기 충족에 필요한 항목 1~3개]
- AC 3~5개: [Given/When/Then 형식 — why 충족 기준으로 작성]
- Edge Case 2개: [예외 시나리오]
추론 과정 생략. 목록만.
```

### PMOAgent 프롬프트 템플릿 (Phase 0 — 예비 분해)

```
당신은 codeforge PMOAgent입니다.
사용자의 아이디어: {USER_IDEA}
현재 open 에픽 목록: {OPEN_EPICS}  ← gh issue list --label phase:설계 등으로 수집

이 아이디어의 예비 분해를 제안하세요.
출력 형식:
- 예상 Story 수: N개 (근거 1줄)
- 의존 가능 epic: [CFP-NNN] 또는 "없음"
- 주요 위험 요소: 1개
추론 과정 생략.
```

### 컨텍스트 패킷 합성

4개 에이전트 결과를 다음 형식으로 합성:

```
=== brainstorming 컨텍스트 패킷 ===
[DomainAgent] {도메인 사실 요약}
[Researcher] 핵심 개념: {목록} / Unknowns: {목록}
[Analyst] 추정 동기(why): {근본 필요} / 일치 여부: {일치|불일치 가능성+사유} / 예비 AC: {목록} / Edge Cases: {목록}
[PMO] 예상 Story: {N}개 / 의존: {에픽} / 위험: {1개}
================================
```

### 자기 적용 의무 (ADR-073 §결정 1 첫 적용 사례 후 default)

Phase 0 4 agent prompt 안 file path / cross-repo state 인용 시 의무 (ADR-073 §결정 6 source-of-truth):

1. `cd <repo> && git fetch origin` 선행 (working tree stale 우려)
2. `git show origin/main:<path>` 또는 `gh issue/pr view --json state` direct verify
3. 인용 옆 `verified-via: <method>` annotation
4. spec/plan frontmatter `pre_lookup_evidence[]` PL 수동 declare 의무 (mechanical layer 부재 시)

agent prompt template 의 default behavior — Orchestrator 가 prompt 작성 시 사전 명시. Sentinel #4 (strike #1 + strike #2) anti-pattern 차단 forcing function.

**예시** (DomainAgent prompt 안):

```
docs/domain-knowledge/ 디렉터리를 읽고...
**verified-via 의무**: 인용 file path 옆 "verified-via: git show origin/main" 또는 "verified-via: gh issue view" annotation 의무.
```

## Phase 1: 강화된 brainstorming 대화

`superpowers:brainstorming` 스킬을 호출하되, 첫 메시지에 컨텍스트 패킷을 포함.

`superpowers:brainstorming`의 checklist 1(project context explore)은 이미 수행됨 —
Phase 0 결과로 대체. checklist 2부터 진행.

**Priority precedence (CFP-637 / ADR-064 §결정 10, Amendment 3)**: 본 Phase 1 의 dialog format / AskUserQuestion / "사용자 confirm" 지시는 **CLAUDE.md ADR-064 §결정 3 룰 1 (Derived default) + §결정 9 Question quality 3-check 보다 후순위**. dialog 진입은 다음 모두 충족 시에만:

1. **가치 판단 영역** 발견 (사용자 선호도 / 가치 판단 기준 / 미공개 컨텍스트 요구)
2. **derived default 비자명** (Epic body / Story context / ADR / 사용자 직전 발화로 합리적 default 도출 불가)
3. **2+ option 진짜 분기** (1-option 만 있는데 "그대로 진행할지?" 형식 발화 차단)

위 3 self-check 미통과 영역 = derived default declare + 진행 (사용자 정정 의무). dialog format / numbered list / "권장 = ..." 형식 발화 금지. CFP-358 / CFP-374 (Subagent-Driven 자동 선택) 의 generalized precedent — 본 skill 의 dialog reflex 차단이 §결정 10 의 first applied case.

본 precedence 는 superpowers:brainstorming 내부 checklist 도 동일 적용 (CFP-639 cross-plugin sister Story 가 upstream PR carrier).

**Why-first 원칙**: brainstorming의 첫 질문은 반드시 "왜"를 향한다. 사용자가 요청한 내용(what)이 아니라 그 배경·동기·실제 필요(why)를 먼저 확립한다.

- RequirementsAnalystAgent가 "불일치 가능성 있음"을 보고한 경우, brainstorming 초반에 이 점을 명시적으로 탐색한다 — "요청하신 것이 X인데, 실제로 해결하고 싶은 문제는 무엇인가요?"
- why 파악 결과 사용자의 실제 필요가 명시된 요구와 다를 경우, 더 나은 대안을 Orchestrator가 직접 제안한다 — "요청하신 X보다 Y가 실제 필요에 더 적합한 이유는 …" 형식.
- **why는 요구사항 확장의 렌즈다.** 사용자가 말한 것에 머물지 않고, 파악한 동기가 충족되려면 무엇이 더 필요한지를 brainstorming 전반에 걸쳐 지속적으로 물어본다. RequirementsAnalystAgent의 "why 기반 확장 요구사항"을 출발점으로 삼아 대화 중에 추가로 발굴한다.
- **추가 요구사항을 적극적으로 제안한다.** 사용자가 꺼내기를 기다리지 않는다. why와 도메인 컨텍스트를 바탕으로 "이것도 필요하지 않으시겠어요?"를 먼저 던진다. 제안 근거는 항상 why와 연결해 설명한다 — "X를 원하시는 이유가 Y라면, Z도 함께 해결해야 할 것 같습니다."
- 대안 제안 후 사용자가 원래 방향을 유지하면 그 선택을 존중하고 진행한다.

## Phase 2: 분해 및 scope_manifest 생성

brainstorming 설계 확정 후 (spec 작성 직전):

PMOAgent를 다시 spawn (2nd pass — Phase 0의 예비 분해와 달리 설계 확정 후 정확한 분해):

```
당신은 codeforge PMOAgent입니다.
확정된 설계: {DESIGN_SUMMARY}

다음을 생성하세요:
1. Epic/Story 분해 초안 (Story 제목 + 1줄 설명)
2. scope_manifest 초안 (YAML):
   planned_adrs: [예약 필요 ADR 수]
   planned_files:
     - 예상 변경 파일 경로들
   planned_claude_md_sections:
     - 예상 수정 섹션명들
```

PMOAgent 출력의 scope_manifest 초안을 spec 파일 끝에 추가.

### execution_context_verify step (ADR-073 Amd 17 — CFP-1786)

Phase 2 PMOAgent 2nd pass spawn 직전 의무 — **single-reader pattern**. Phase 0 4 agent 영역 verify 의무 0건 (race / token cost / inconsistency 3 risk 차단 invariant) — PMOAgent 단독 reader 가 1회 actual state direct read.

**4-item closed-enum hard cap verify**:

1. **label-registry-v2 version** — `git -C <worktree> show origin/main:docs/inter-plugin-contracts/label-registry-v2.md` line 6 frontmatter `version: vN.NN`
2. **evidence-checks-registry entry count** — `git -C <worktree> show origin/main:docs/evidence-checks-registry.yaml` content + `grep -c '^- name:'` direct count
3. **plugin metadata version** — `git -C <worktree> show origin/main:plugin.json` `version` field (또는 `.claude-plugin/plugin.json` actual path)
4. **marketplace.json version** — cross-repo `git -C <marketplace-worktree> show origin/main:marketplace.json` `plugins[name=codeforge].version` field

5번째 item 확장 = 별 CFP carrier 의무 (ADR-064 §결정 5 CFP scope unitary carve-out).

**Output**: PMOAgent 가 verified 4-item + `verified_via` annotation + `origin_main_sha` + `captured_at_kst` 7-field tuple 합성 → spec 파일 `execution_context:` frontmatter field 에 기록 (template field 활성화). Phase 1 brainstorming dialog context packet 에 corrected facts injection (4 agent prompt 가 stale 정보 인용 시 정정).

**예시 spec.md frontmatter** (활성화 시):

```yaml
execution_context:
  label_registry_v2_version: "v2.74"
  evidence_checks_registry_entry_count: 24
  plugin_metadata_version: "v1.5.12"
  marketplace_json_version: "v1.5.12"
  verified_via: "git -C <worktree> fetch origin && git show origin/main:<path>"
  origin_main_sha: "<40-char-hex>"
  captured_at_kst: "YYYY-MM-DDTHH:MM:SS+09:00"
```

backward-compat: 미선언 시 default "not captured" — Wave 2 mechanical lint (별 sub-CFP carrier — CFP-1786-W2 reserved) 가 stale 영역 감지.

## 종료

spec 파일 저장 완료 후 `superpowers:writing-plans` 스킬 호출.
(scope_manifest 초안은 spec 파일에 포함됨 — Phase 1 PR 시 Issue body에 붙여넣기)
