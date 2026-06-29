---
name: knowledge-capture-gate
description: 완료시점 재사용지식 capture 게이트 + MEMORY.md 용량관리 규약 lookup 시 (① 작업/Story 완료 처리 직전 capture admission 3문 게이트 + routing, ② MEMORY.md 용량 cap 초과 시 무손실 슬림화). 정책 SSOT = ADR-129, paired = ADR-045 Amendment 14 (§D-13 phase:완료 capture self-check) + ADR-071 Amendment 12 (§18.7 deferred mechanism 해제). 3문 admission = oh-my-claudecode(MIT) skillify 차용.
tools: Read
---

# Knowledge Capture Gate + MEMORY.md 용량관리 (CFP-2392 / ADR-129)

> 참조 테이블 skill — 작업/Story **완료 처리 직전**(capture 게이트) 과 MEMORY.md **용량 cap 초과 시**(슬림화) 두 시점에 본 skill 을 확인하세요.

본 skill 은 **lookup mirror** — 정책 원본은 아래이며 본 skill 로의 SSOT 이동/변경 금지:

- **정책 SSOT**: [ADR-129 OMC-adopt 지식캡처 + 메모리 다이어트](../../archive/adr/ADR-129-omc-knowledge-capture-memory-governance.md)
- **paired carrier**: [ADR-045 Amendment 14 §D-13](../../archive/adr/ADR-045-story-retro-mandatory-trigger.md) (phase:완료 precondition capture self-check) + [ADR-071 Amendment 12 §18.7](../../archive/adr/ADR-071-orchestrator-user-dialog-convergence.md) (MEMORY.md 슬림화 mechanism deferred 해제)
- **절차 SSOT**: [orchestrator-playbook](../../docs/orchestrator-playbook.md) §9.7.2 완료 단계 수렴 SSOT (capture self-check pointer)

**호출 시점 2개**:

| 시점 | 할 일 |
|---|---|
| ① 작업/Story 완료 처리 직전 (`phase:완료` transition) | capture admission 3문 게이트 + routing (§1) |
| ② MEMORY.md 용량 cap(24.4KB) 초과 감지 시 | 무손실 슬림화 (§2) |

> **출처 (MIT)**: 본 skill §1 의 3문 캡처 게이트 admission 휴리스틱 = oh-my-claudecode(MIT, Copyright (c) 2025 Yeachan Heo) skillify SKILL.md 차용. 차용 범위 = admission 3문 1건뿐 — 경로 규약·char-budget·용량 cap·슬림화 전략은 codeforge 내부 도출(ADR-129 §결정 5 / §컨텍스트).

---

## §1 Capture 게이트 — 완료시점 재사용지식 외부화 (ADR-129 §결정 1)

작업/Story 완료 처리 시점에 "이번 작업에서 재사용 가능한 지식이 나왔는가 — 나왔다면 외부화했는가" 를 확인한다.

### §1.1 admission 3문 게이트 (OMC skillify 차용 — semantic, behavioral)

아래 3문을 self-eval 한다. **3문 모두 YES** 일 때만 그 지식은 캡처 대상이다:

1. **5분 안에 구글로 찾을 수 있나?** → **No** (찾을 수 있으면 캡처 불요 — 일반 지식)
2. **이 코드베이스·프로젝트·워크플로에 특정한가?** → **Yes**
3. **실제 디버깅·설계·운영 노력을 들여 발견했나?** → **Yes**

(원문 OMC: (1) "Could someone Google this in 5 minutes?" → No (2) "Is this specific to this codebase, project, or workflow?" → Yes (3) "Did this take real debugging, design, or operational effort to discover?" → Yes)

> 이 admission 판정 자체는 **semantic judgment** — mechanical lint 불가. Orchestrator self-eval (behavioral directive). Phase 2 lint 은 "흔적 존재" 만 presence 검사 (ADR-129 §결정 1(1), Story §8.3).

### §1.2 routing — skill vs domain-knowledge

캡처 대상이면 산출물 형식을 결정한다:

| 지식 성격 | 산출물 | 위치 |
|---|---|---|
| 절차 / 실행 가능한 운영 지식 (어떻게 하는가) | `skills/<slug>/SKILL.md` | ADR-051 form (subdir + frontmatter name/description + trigger 명시 의무 (ADR-051 §결정 4)) |
| 사실 / 원리 / 패턴 지식 (무엇이 참인가) | `docs/domain-knowledge/<category>/<slug>.md` | 예: `docs/domain-knowledge/domain/governance-principle/` |

split 근거 = ADR-120 §결정 3 (skill = 절차 / domain-knowledge = 지식). 경로는 codeforge in-repo SSOT — OMC 의 `~/.claude/skills/omc-learned/`·`.omc/skills/` 미차용 (ADR-129 §컨텍스트).

### §1.3 forced-no-silent-skip (검사연극 회피)

게이트는 **always advisory** (warning-tier, hard-block 아님). 그러나 "캡처할 게 없다" 도 **명시적 흔적**으로 남긴다:

- 캡처함 → 신규 capture artifact (`skills/<slug>/SKILL.md` 또는 `docs/domain-knowledge/.../*.md`) 존재.
- 검토했는데 불요 → **no-capture note** 1줄: `"캡처 대상 검토 완료 — 외부화 불요(사유)"`.
- **둘 다 부재 = WARN** (silent skip 금지). "캡처" 또는 "검토-불요" 둘 중 하나는 흔적이 있어야 한다.

> 이로써 게이트가 "항상 통과(failing fixture 부재)" 인 검사연극이 되지 않는다. anti-theater discriminating case = capture 0 ∧ note 0 → WARN (Story §8.1 TC3).

#### §1.3.1 term-drift routing (+1문) — CFP-2453 / ADR-129 Amendment 1

§1.1 admission **3문 무변경**. 완료 시점 routing/self-check 항목으로 1문 추가 (관계 산출 = 1-fact admission 과 disjoint — 동음/유의/반의는 여러 용어를 함께 비교해야 드러나는 *관계*라 1-fact 가 아님, CFP-2453 §2.1 도메인 framing):

> **+1문 (완료 self-check)**: "이 작업이 consumer 도메인 용어를 신설/재정의했는가? → 했다면 `docs/domain-knowledge/domain/<area>/lexicon.md` / `concept-dictionary.md` 갱신, 안 했어도 `no-update` note 명시 (silent skip 불허)."

- **anti-theater 동형 보존**: 위 §1.3 `capture 0 ∧ note 0 → WARN` 규칙이 +1문에도 동형 적용 — **"갱신 0 ∧ no-update note 0 → WARN"**. 용어 재정의 있었으나 lexicon/concept-dict 갱신도 no-update note 도 없으면 WARN.
- **disjoint 유지 (ADR-129 §결정3)**: 본 +1문 = term-drift maintain routing (지식 캡처 필터의 하위), §1.1 admission 3문(1-fact) 과 별 축. admission gate schema 변경 아님 (routing 항목 추가). ADR-119 §결정9 제안 필요성 게이트와도 통합 금지 (disjoint).
- 정책 SSOT = [ADR-129 Amendment 1](../../archive/adr/ADR-129-omc-knowledge-capture-memory-governance.md). lexicon drift 유지 trigger 의 maintain 측 (생산 측 = DomainAgent bootstrap, ADR-091 Amendment 3).

### §1.4 게이트 tier / fail-safe (로컬-only warning-tier)

- tier = **warning + `workflow: null`** (로컬-only). `phase:완료` transition = Orchestrator self-write + 완료 marker = working-tree 검출이라 required CI check 불가 (ADR-099/ADR-122/ADR-128 선례 동형).
- required check 신설 0 → branch protection 6-tuple 무변경 (ADR-024 Amd19 §B 정합).
- fail-safe = git/gh 미인증 시 exit 0 보존 (data-loss 가드). 완료 marker 부재(진행 중) 시 exit 0 no-op.
- Phase 2 wire = `scripts/check-capture-gate-completion.sh` + evidence-checks-registry `knowledge-capture-completion-gate` entry active 전환.

---

## §2 MEMORY.md 용량관리 규약 (ADR-129 §결정 2 / ADR-071 §18.2-18.3/18.7)

ADR-071 §18.2 가 선언한 24.4KB cap 과 §18.3 의 슬림화 normative 를 실 규약으로 운영한다 (§18.7 deferred mechanism 해제 = ADR-071 Amendment 12).

### §2.1 2-layer 용량 budget

| layer | budget | source |
|---|---|---|
| (a) per-entry one-line | 인덱스 entry 1건 ≤ 약 200자 (one-line), 상세는 topic 파일로 | harness session-reminder ("Keep index entries to one line under ~200 chars; move detail into topic files") |
| (b) total file | MEMORY.md 전체 ≤ 24.4KB | ADR-071 §18.2 cap SSOT |

> 출처 명확화: char-budget 은 **OMC 차용 아님**. OMC skillify 에는 char-cap·descriptor-only split 없음. (a) ~200자 = harness reminder 도출, (b) 24.4KB = ADR-071 §18.2 도출 — 둘 다 internal (ADR-129 §결정 2(1)).

### §2.2 슬림화 전략 — `size > 24.4KB` 시

1. **oldest-first** — 가장 오래된 entry 부터 슬림화 (ADR-071 §18.3 normative).
2. **completed-Story consolidate** — 완료된 Story 의 여러 entry 를 topic 파일로 통합·압축.
3. **archive-not-delete** — 내용 삭제가 아니라 topic 파일로 **이동** (`[title](topic.md)` + `[[wikilink]]` cross-ref, 기존 convention).
4. **active-Story preserve** — 진행 중(active) Story 의 entry 는 슬림화 대상 **제외** (lossless invariant).

### §2.3 lossless invariant (무손실)

슬림화 후 (a) active-Story entry 보존 ∧ (b) 슬림화된 내용은 archive(topic 파일)에 존재. 위반 = WARN.

> "이 entry 가 archive 적격 완료-Story 인가" 판정 = **semantic** → mechanical lint 불가, honest decline (ADR-119 abstention). lint 은 size + entry presence 만 (Story §8.2/§8.3). Phase 2 wire = `scripts/check-memory-capacity.sh` + evidence-checks-registry `memory-capacity-gate` entry active 전환. fail-safe = MEMORY.md 경로 부재 시 exit 0 no-op.

---

## §3 ADR-119 cross-ref — 동형이나 통합 금지 (ADR-129 §결정 3)

본 §1 capture 게이트(3문 admission)와 [ADR-119](../../archive/adr/ADR-119-research-before-claims.md) §결정 9 **제안 필요성 3문 게이트**는:

- **동형 패턴** — 둘 다 noise 억제용 3문 게이트.
- **도메인 DISJOINT** — ADR-119 = 작업 제안·follow-up Issue **발의** 필터 / 본 게이트 = 재사용 **지식 캡처** 필터.

→ **통합 금지, cross-ref 만** (RefactorAgent — domain disjoint 라 한 게이트로 묶으면 서로 다른 결정면을 융합하는 over-abstraction). 두 게이트는 독립 유지.

> **완료-self-check family 관찰** (escalation-tier): worktree-clean(ADR-128) + capture(본 skill) = `phase:완료` local-only warning-tier self-check family emerging. 지금 공통 프레임워크 강제 추상화는 하지 않는다(검증 대상 disjoint, 이득<비용 — ADR-119 §결정 9 3문 게이트). family 3+ 면 escalation (ADR-129 §결정 3).

---

## 관련

- [ADR-129](../../archive/adr/ADR-129-omc-knowledge-capture-memory-governance.md) — 정책 SSOT (umbrella)
- [ADR-045 Amendment 14 §D-13](../../archive/adr/ADR-045-story-retro-mandatory-trigger.md) — phase:완료 capture self-check precondition
- [ADR-071 Amendment 12 §18.7](../../archive/adr/ADR-071-orchestrator-user-dialog-convergence.md) — MEMORY.md 슬림화 mechanism deferred 해제
- [ADR-128](../../archive/adr/ADR-128-completion-stage-formalization.md) — archetype (완료 단계 정식화, worktree-clean self-check)
- [ADR-051](../../archive/adr/ADR-051-ssot-skill-extraction-pattern.md) — skill subdir form
- [ADR-119](../../archive/adr/ADR-119-research-before-claims.md) — §결정 9 제안 필요성 3문 게이트 (동형·disjoint)
