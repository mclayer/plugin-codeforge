---
adr_number: 117
title: Fable 5 surgical 모델 tier 채택 (chief author / 장기 agentic / 적대적 심판 한정)
status: Accepted
category: governance
date: 2026-06-10
carrier_story: CFP-2134
is_transitional: false   # ADR 본체 = permanent policy. Amendment 1 (CFP-2241) 만 transitional override (제약 해제 시 원복) — amendment_log 참조.
amends: null
supersedes: null
amendment_log:
  - by: "CFP-2241"
    date: "2026-06-14"
    scope: "Amendment 1 — 미 정부 제약에 따른 fable → opus 임시 transitional override. 결정 1 의 surgical 10 에이전트 `model: fable` → `model: opus` 임시 치환 (정책 = 어느 역할이 fable 적격인가 결정 1 표 불변, 모델 alias 만 임시 교체). 결정 3 floor (Claude Code 2.1.170) + ADR-057 Amendment 5 (fable model-unavailable → opus fresh re-spawn fallback) 는 삭제하지 않고 dormant 보존 (원복 대비). 결정 1·2·3·4·5 본문 변경 0건 — model alias 만 frontmatter 치환. bump: 4 lane plugin PATCH (design 0.25.3 / develop 0.10.2 / review 1.12.2 / requirements 0.8.3) + wrapper 6.19.3."
    sunset_justification: "transitional override 는 ratchet 강화가 아니라 외부 제약(미 정부 fable 사용 불가)에 대한 임시 대응이다. 원의도(capability 상승이 2배 비용을 정당화하는 surgical 역할에 최강 모델 적용)는 thinking 프로파일 동일(ADR-117 컨텍스트)인 opus 로 충족 — 능력 손실 0. 명시 override(frontmatter 직접 치환) 채택 근거 = ADR-057 Amendment 5 의 매 spawn 실패→재시도 fallback 은 지연 + 제약 트리거 문구 불확실. 원복 trigger = 사용자 '제약 해제' 통지, 원복 절차 = (a) 10 frontmatter opus → fable 환원 + 임시 표식 코멘트 제거 (b) 본 Amendment 를 dormant/superseded 마킹 (c) floor·fallback 정책 재활성 확인 — 원복도 Story 경유. ADR-058 §결정 5 self-application (Amendment 시 sunset_justification 의무) 정합. [상태: dormant/superseded — 2026-07-02 CFP-2554 Amendment 2 로 해소(원복 완료). 실 frontmatter 환원 = Phase 2.]"
  - by: "CFP-2554"
    date: "2026-07-02"
    scope: "Amendment 2 — 미 정부 제약 해제에 따른 fable 원복 실행 + surgical set 10→11 정합. Amendment 1 (CFP-2241 임시 opus override) 를 dormant/superseded 마킹. 결정 1 표(10행) + Amendment 1 표(10행) 를 11행으로 정합 — RequirementsReviewPLAgent 추가(적대적 심판 / 요구사항리뷰 verdict, ADR-125 carrier drift 청산: ADR-125 가 요구사항리뷰 lane 신설 시 CFP-2241 override 관습을 승계했으나 ADR-117 표 미갱신). 결정 1·2 본문 '10' 카운트 정정. floor(결정 3) + ADR-057 Amendment 5 fallback + SSOT dormant 주석 3곳(CLAUDE.md:86 / consumer-guide:59 / playbook:515, 10→11) 재활성 = Phase 2 적용. 실 frontmatter opus→fable 환원 + 임시 코멘트 제거 + bump + marketplace sync = Phase 2 PR."
    sunset_justification: "본 Amendment 는 ratchet 강화가 아니라 Amendment 1 transitional override 의 해소(원복)다. 원복 trigger = 사용자 '제약 해제' 통지(ADR-117 Amd1 §원복 절차 revert-trigger 정의 정합). 능력 손실 0(fable/opus thinking 프로파일 동형 — 가격비 2배·프로파일 동형 CFP-2554 §6.3 cited 재확인). Amendment 2 자체는 permanent(원복은 되돌리지 않음) — Amendment 1 만 dormant/superseded. ADR-058 §결정 5 self-application(Amendment 시 sunset_justification 의무) 정합. is_transitional 무변경(false 유지 — 본체 permanent, Amendment 1 만 transitional 이었고 이제 해소)."
related_adrs:
  - ADR-057  # Orchestrator Opus 필수 mandate + Sonnet→Opus rate-limit fallback — 본 ADR §결정 5 (Orchestrator 제외) 정합. Amendment 5 (fable model-unavailable → opus fallback) = ADR-117 Amendment 1 로 dormant 보존, Amendment 2 로 재활성(Phase 2).
  - ADR-125  # 요구사항리뷰 lane 신설 (CFP-2326) — RequirementsReviewPLAgent 도입원. ADR-125 가 CFP-2241 override 관습을 승계하며 surgical 명단을 10→11 로 늘렸으나 본 ADR 표를 미갱신 → Amendment 2 stale 발생원. Amendment 2 로 표 11행 정합.
related_stories:
  - CFP-2134  # carrier (Cross-repo Fable 5 채택 Epic — foundation)
  - CFP-2241  # Amendment 1 carrier (미 정부 제약 fable → opus 임시 override)
  - CFP-2554  # Amendment 2 carrier (미 정부 제약 해제 → fable 원복 실행 + surgical 10→11 정합)
related_files:
  - docs/consumer-guide.md
mechanical_enforcement_actions: []   # 신규 lint/sentinel 0 — model alias 적용은 각 lane plugin 의 에이전트 frontmatter (별 lane PR) 가 SSOT. Claude Code 버전 floor 는 런타임 spawn 실패로 자가 강제 (미인식 ID = silent fallback 없이 fail).
---

# ADR-117: Fable 5 surgical 모델 tier 채택 (chief author / 장기 agentic / 적대적 심판 한정)

## 상태

Accepted (2026-06-10 KST — CFP-2134 carrier). Cross-repo Fable 5 채택 Epic 의 foundation 설계 결정. 본 ADR 은 정책 SSOT 이며, 실제 `model: fable` alias 적용은 각 lane plugin 의 에이전트 frontmatter 변경(별 lane PR — design / develop / review / requirements)으로 실현된다.

## 컨텍스트

Claude Fable 5(`claude-fable-5`, 2026-06-09 GA)는 Anthropic 일반 공개 최강 모델이다. Opus 4.8 대비 long-horizon 작업·SW 엔지니어링·적대적 추론에서 우위를 보인다.

비용·프로파일 사실:
- **가격**: $10 / $50 per MTok(input / output) = Opus 4.8($5 / $25)의 **정확히 2배**.
- **thinking 프로파일**: Opus 4.8 과 동일(adaptive on / extended 없음) → `opus` → `fable` 교체 시 thinking 능력 손실 0.

문제는 "2배 비용을 어디까지 정당화하는가"이다. codeforge 는 0 core 에이전트 wrapper 로, 8 lane plugin 의 ~30+ 에이전트가 역할별로 fan-out 된다. 역할의 성격은 이질적이다:
- 일부는 **long-horizon chief author / 장기 agentic 코딩 / 적대적 심판**(긴 컨텍스트·다단계 추론·대립 검증) — Fable 의 우위가 직접 발현.
- 다수는 **단기 구조적 advocate / 빠른 분류 / 외부 모델 위임 래퍼 / GitOps·worker** — long-horizon 이점이 발현될 표면이 작아 2배 비용 대비 효용이 낮다.

전체 일괄 채택(opus→fable 전면)은 후자 군까지 2배 비용을 물리므로 비효율이고, 3~4개 minimal pilot 은 채택 범위가 너무 좁아 효용 검증이 불충분하다. 따라서 capability 상승이 비용을 정당화하는 역할만 **외과적(surgical)으로** 골라 적용한다.

추가 제약: `model: fable` alias 는 Claude Code v2.1.170+ 에서만 인식된다. 미만 버전은 미인식 model ID 를 **조용히 fallback 하지 않고 spawn 자체를 실패**시킨다 — consumer 호환성 floor 를 명시할 의무가 발생한다.

## 결정

### 결정 1: surgical 채택 대상 11 에이전트에만 `model: fable` 적용

> **카운트 정합 (CFP-2554 Amendment 2, 2026-07-02)**: 원 표는 10행이었으나, ADR-125(요구사항리뷰 lane 신설, CFP-2326)가 RequirementsReviewPLAgent(적대적 심판 category)를 도입하며 surgical 명단을 11 로 늘렸다. ADR-125 본문이 본 표를 미갱신해 drift 가 발생했고, Amendment 2 가 11행으로 정합했다. **실측 SSOT = 11**(`grep -rl "임시(CFP-2241)" plugins/*/agents` = 11).

capability 상승이 2배 비용을 정당화하는 역할 = **chief author / 장기 agentic 코딩 / 적대적 심판**. 적용 대상 11개:

| lane | 에이전트 | 분류 근거 |
|---|---|---|
| design | Architect | chief author (설계 서사 multi-source synthesis) |
| design | ArchitectPL | 장기 검수 + deputy fan-out 통합 |
| design | SecurityArch | 적대적 보안 설계 추론 |
| develop | Developer | 장기 agentic 코딩 |
| develop | DeveloperPL | 장기 agentic 코딩 통합 |
| review | ClaudeReview | 적대적 심판 |
| review | CodeReviewPL | 적대적 심판 (구현 리뷰 verdict) |
| review | DesignReviewPL | 적대적 심판 (설계 리뷰 verdict) |
| review | SecurityTestPL | 적대적 심판 (보안 테스트 verdict) |
| review | RequirementsReviewPL | 적대적 심판 (요구사항리뷰 verdict — 외부사실 게이트, ADR-125 carrier) |
| requirements | Researcher | long-horizon 외부 지식 종합 |

### 결정 2: 제외 기준 — 단기 구조적 / 빠른 / 위임 / worker 역할

다음 군은 제외한다(현행 모델 유지) — Fable 의 long-horizon 이점이 2배 값을 정당화하지 못한다:
- **좁은 구조적 advocate**: ModuleArch · APIContractArch · Refactor · CodebaseMapper · ArchitectAnalyst (단일 mandate advocacy, 설계 시점 구조 결정).
- **빠른 haiku 군**: 빠른 분류·경량 처리 역할.
- **GPT-5.4 위임 래퍼**: RequirementsAnalyst · CodexReview (실제 추론은 외부 Codex/GPT-5.4 가 수행, 래퍼는 위임만).
- **deploy / test worker**: 단기 실행 worker.
- **confluence-sync · GitOps**: 기계적 sync / git ops.
- **PMO · Dialog · Continuity · Feasibility · Domain**: 단기 구조적 역할.

### 결정 3: 호환성 floor — Claude Code 최소 버전 2.1.170

`model: fable` alias 는 Claude Code v2.1.170+ 에서만 인식된다(미인식 ID = silent fallback 없이 spawn 실패). 따라서 **codeforge 최소 Claude Code 버전 = 2.1.170**. consumer-guide §"필수 의존성" 에 명시한다. 2.1.170 미만 consumer 는 본 결정 1 의 11 에이전트(design / develop / review / requirements lane) spawn 이 실패한다.

### 결정 4: 풀 ID 아닌 alias `fable` 사용

풀 ID(`claude-fable-5`)가 아닌 alias `fable` 을 frontmatter 에 기재한다 — 버전 업그레이드(Fable 5.x → 차기) 자동 추적 best-practice. Orchestrator `opus` alias 관행과 동형.

### 결정 5: Orchestrator 모델 제외 — 현행 `opus` 유지

최상위 세션(Orchestrator) 모델은 현행 `opus`(ADR-057 mandate)를 유지한다. Fable Orchestrator 채택은 비용·세션 전반 영향이 별개 차원이므로 **별 결정 사안**으로 분리한다 — 본 ADR scope 외.

## 해소 기준

N/A — permanent policy. 본 ADR 은 모델 tier 선택 정책의 상시 기준으로, sunset 대상이 아니다. 단, 모델 세대 전환(차기 최강 모델 GA / Opus·Fable 가격 구조 변동 / Orchestrator Fable 채택 별 결정)이 발생하면 본 ADR 을 amend 하여 surgical 대상·floor 버전을 재산정한다.

## 근거 (Rationale)

- 옵션 A(opus 전체 → fable 전면 교체) **기각** — 단기 구조적 opus 에이전트(ModuleArch / APIContractArch / Refactor 등)까지 2배 비용을 물리나 long-horizon 이점 발현 표면이 작아 비용 대비 효용이 낮다.
- 옵션 B(minimal pilot 3~4개) **기각** — 채택 범위가 너무 좁아 chief author / 장기 코딩 / 적대적 심판 3 축의 효용을 동시에 검증하기 불충분하다.
- 옵션 C(surgical 11 에이전트 채택) **채택** — capability 상승이 2배 비용을 정당화하는 역할만 외과적으로 골라 적용. thinking 손실 0(프로파일 동일)이라 교체 부작용 없음. 제외 군은 현행 모델 유지로 비용 중립. (채택 시점 카운트 = 10; ADR-125 요구사항리뷰 lane 신설로 11 로 증가 → CFP-2554 Amendment 2 로 표 정합.)

## 결과

- **lane PR(별 PR)**: design / develop / review / requirements 4 lane plugin 의 해당 에이전트 frontmatter `model:` 를 `fable` 로 변경 — 각 lane plugin repo 의 별 PR(본 wrapper foundation PR OOS).
- **marketplace sync**: plugin.json 메타 변경(version) 동반 시 ADR-063 atomic invariant 에 따라 marketplace sync PR 선행(본 Epic 범위).
- **consumer 호환성**: 2.1.170 미만 consumer 는 해당 lane 에이전트 spawn 실패 — consumer-guide floor 명시로 사전 고지.
- **Orchestrator Fable 채택**: 별 결정 사안(§결정 5) — 향후 별 ADR/CFP.

## 관련 파일

- `docs/consumer-guide.md`

## Amendment 1 (2026-06-14) — CFP-2241 — 미 정부 제약에 따른 fable → opus 임시 transitional override

> **상태: dormant/superseded (2026-07-02, CFP-2554 Amendment 2 로 해소 — 원복 완료).** 미 정부 제약이 해제되어 fable 이 재가용해졌고, Amendment 2 가 본 임시 override 를 해소했다(설계 = Phase 1, 실 frontmatter opus→fable 환원 = Phase 2). 아래 내용은 **이력 보존용**이며 더는 현행 상태를 규정하지 않는다 — 현행 = fable surgical(결정 1 원상태). 원복 실행·재활성 계획은 Amendment 2 참조.

### 성격

본 Amendment 는 **transitional**(임시 + 원복 가능)이었다. ADR 본체 status 는 **Accepted 유지** — 결정 1~5 의 정책은 불변이며, 본 Amendment 는 외부 제약 기간에 한정해 모델 **alias 만** 임시 치환했다. 제약 해제 시 원복 절차 완료로 해소한다 (→ 2026-07-02 CFP-2554 Amendment 2 로 해소 완료).

### 컨텍스트

2026-06-14 KST, 미 정부 제약으로 `fable` alias(Claude Fable 5) 사용이 불가해졌다. 그 결과 결정 1 의 surgical 10 에이전트(`model: fable`)가 spawn 실패/우회 상태가 된다. 기존 ADR-057 Amendment 5(fable model-unavailable → opus fresh re-spawn fallback)는 매 spawn 실패 후 재시도 방식이라 (a) 실패→재시도 지연이 누적되고 (b) 제약 환경의 에러 문구가 fallback trigger 문자열과 일치한다는 보장이 없어 trigger 가 불확실하다.

### 결정

결정 1 의 surgical 10 에이전트 frontmatter `model: fable` → `model: opus`(최신 Opus tier alias)로 **임시 override** 한다.

- **정책 불변**: "어느 역할이 fable 적격인가"(결정 1 표 — chief author / 장기 agentic 코딩 / 적대적 심판 10 역할)는 그대로다. 모델 alias 만 임시 치환한다.
- **능력 손실 0**: ADR-117 컨텍스트의 사실대로 fable 의 thinking 프로파일은 opus 4.8 과 동일(adaptive on / extended 없음)이라 `fable` → `opus` 교체 시 thinking 능력 손실이 없다.
- **명시 override 채택**: 매 spawn 실패 후 재시도하는 ADR-057 Amendment 5 fallback 에 의존하지 않고 frontmatter 를 직접 교체한다 — 지연 + trigger 불확실성 제거.
- **임시 표식**: 각 frontmatter `model:` 라인에 임시 override 임을 알리는 inline 코멘트(CFP-2241 / ADR-117 Amendment 1 / 원복 안내)를 부착한다.

적용 대상 11 에이전트(결정 1 표와 동일 — CFP-2554 Amendment 2 로 11행 정합):

| lane | 에이전트 | frontmatter |
|---|---|---|
| requirements | ResearcherAgent | `model: opus` (임시) |
| develop | DeveloperAgent | `model: opus` (임시) |
| develop | DeveloperPLAgent | `model: opus` (임시) |
| design | ArchitectAgent | `model: opus` (임시) |
| design | ArchitectPLAgent | `model: opus` (임시) |
| design | SecurityArchitectAgent | `model: opus` (임시) |
| review | ClaudeReviewAgent | `model: opus` (임시) |
| review | CodeReviewPLAgent | `model: opus` (임시) |
| review | DesignReviewPLAgent | `model: opus` (임시) |
| review | SecurityTestPLAgent | `model: opus` (임시) |
| review | RequirementsReviewPLAgent | `model: opus` (임시) [주] |

> **[주] (CFP-2554 Amendment 2)**: RequirementsReviewPLAgent 는 CFP-2241 (Amendment 1) 당시 표에 **부재**했다. 원인 = ADR-125(요구사항리뷰 lane 신설, CFP-2326)가 이 PL 을 신설하며 CFP-2241 의 `model: opus` 임시 override 코멘트 관습을 승계했으나(실 frontmatter 에는 override 가 존재), ADR-125·ADR-117 어느 쪽도 본 표를 동기화하지 않은 drift 다. 실측 override 대상은 처음부터 11개였고, Amendment 2 가 이 11번째 행을 표에 명시해 drift 를 청산했다.

### 보존(미삭제) 명시 — dormant

다음 정책은 **삭제하지 않고 dormant 보존** 한다 — 제약 해제 시 즉시 재유효해야 하기 때문이다.

- **결정 3 floor(Claude Code 2.1.170)**: fable alias 인식 floor. 현재 wrapper self 는 opus override 라 floor 가 휴면이나, consumer-guide 의 floor 문장은 보존한다(원복 시 재유효).
- **ADR-057 Amendment 5(fable model-unavailable → opus fresh re-spawn fallback)**: 현재 surgical 11(Amendment 1 당시 표는 10 — [주] 참조) 이 opus override 라 model-unavailable trigger 가 휴면이다. ADR-057 §결정 4 / playbook §3.0.12 / CLAUDE.md "비-opus tier → Opus fallback" 문장은 dormant 주석만 부착하고 보존한다. (CFP-2554 Amendment 2 로 재활성 — Phase 2.)

SSOT 문서 dormant 주석 부착 위치: `CLAUDE.md`(비-opus tier 섹션) · `docs/consumer-guide.md`(floor 의존성) · `docs/orchestrator-playbook.md`(§3.0.12 fable model-unavailable case).

### 원복 절차

원복 trigger = 사용자가 "제약 해제" 통지. 원복도 Story 경유로 수행한다.

1. 11 에이전트(Amendment 1 당시 표는 10 — [주] 참조) frontmatter `model: opus` → `model: fable` 환원 + 임시 표식 코멘트 제거.
2. 본 Amendment 1 을 dormant/superseded 로 마킹(amendment_log + 본 섹션 상태 표기).
3. 보존해 둔 floor(결정 3) + ADR-057 Amendment 5 fallback + SSOT dormant 주석이 재활성됐는지 확인(주석 제거 / trigger 재유효).
4. 4 lane plugin + wrapper version bump + marketplace sync(mirrored field 변경 시 ADR-063 atomic invariant).

### 해소 기준

미 정부 제약 해제 시 위 원복 절차 완료로 본 Amendment 가 해소된다. 해소 시 ADR 본체는 변경 없이 결정 1~5 가 원래대로(fable surgical) 작동한다.

### 근거 (Rationale)

- 옵션 A(ADR-057 Amendment 5 자동 fallback 에 의존) **기각** — 매 spawn 실패→재시도 지연 누적 + 제약 환경 에러 문구가 fallback trigger 문자열과 일치한다는 보장 없음(trigger 불확실).
- 옵션 B(명시 frontmatter override) **채택** — 사전 결정적이라 지연 0, trigger 확실. thinking 프로파일 동일이라 능력 손실 0. floor·fallback 정책은 dormant 보존이라 원복 즉시 가능.
- 옵션 C(fable 영구 폐기 + opus 정착) **기각** — 사용자 결정상 fable 영구 폐기가 아니며 제약 기간 한정 조치다. 영구 전환은 원복 불가를 초래해 사용자 전제(임시 + 원복 가능)에 위배.

## Amendment 2 (2026-07-02) — CFP-2554 — 미 정부 제약 해제에 따른 fable 원복 실행 + surgical 10→11 정합

### 성격

본 Amendment 는 **원복(reversal) 실행 + 표 정합**이다 — ratchet 강화가 아니라 Amendment 1(CFP-2241) transitional override 의 **해소**다. Amendment 2 자체는 **permanent**(원복은 되돌리지 않는다) — dormant 마킹 대상은 Amendment 1 뿐이다. ADR 본체 status = **Accepted 유지**, `is_transitional` = **false 유지**(본체 permanent, Amendment 1 만 transitional 이었고 이제 해소). 결정 1~5 정책은 불변 — 모델 alias 만 `opus`(임시) → `fable`(원상) 환원.

### 컨텍스트

- **트리거**: 사용자 통지(2026-07-02, CFP-2554 §1) — "fable 이 다시 사용 가능한 것 같다". 미 정부 제약 해제로 fable 재가용. 이는 Amendment 1 §원복 절차가 규정한 **"제약 해제 통지"** revert-trigger 에 정합한다. 법적 해제 사실 자체는 구조적 검증 불가(research-before-claims ③ — Orchestrator·에이전트 독립 확인 수단 부재) → 사용자 발화를 트리거로 간주.
- **능력 손실 0 재확인 (cited)**: fable 5·opus 4.8 모두 adaptive-only thinking + effort 파라미터, extended budget 미지원 → thinking 프로파일 **동형**. 가격은 fable $10/$50 = opus 4.8 $5/$25 의 정확히 2배 — surgical 대상 선정 시 이미 정당화된 역할군 한정이라 비용 재부담 근거 불변. 출처: Claude Platform pricing / whats-new-claude-4-8 / introducing-claude-fable-5 (CFP-2554 §6.3 cited).
- **self-application 시점 불변식**: 원복 대상 11개 중 design/develop/review lane 에이전트가 본 Story 의 후속 lane 수행자다(자기 모델 tier 를 되돌리는 self-reference). plugin frontmatter 변경은 **plugin 재로드(= 다음 세션)부터** 유효하므로, 본 Story 를 진행 중인 에이전트는 여전히 opus 로 완주한다 — 원복 효과는 다음 세션부터. 이 지연은 결함이 아니라 plugin 로드 모델의 구조적 성질.

### 결정 (known-issue 3항 판정)

1. **10↔11 ADR-117 표 정합 방향 — RequirementsReviewPL surgical 정식 편입 채택.** RequirementsReviewPL 은 결정 1 표가 이미 "적대적 심판(verdict)"으로 분류한 CodeReviewPL·DesignReviewPL·SecurityTestPL 3 리뷰 lane PL 과 **동형**(요구사항 외부사실 게이트 verdict) — 4번째 리뷰 lane PL 이다. ADR-125(요구사항리뷰 lane 신설, CFP-2326)가 이 PL 을 도입하며 CFP-2241 override 관습을 승계했으나 표를 미갱신한 drift 를 청산. **반박(기각) = 옵션 "override 만 제거, 표 10 유지"**: 실측 override 는 11개인데 표만 10 으로 남기면 RequirementsReviewPL 이 fable 근거 없이 opus 로 되돌아가거나(orphan) drift 가 영속화 → 더 큰 정합 파괴. 따라서 표 11행 정합 채택.
2. **RequirementsReviewPL fable 환원 포함 — 채택(YES).** 결정 1 종속 — 11개 전부 fable 환원 대상. (Phase 1 이 PR 에서 frontmatter 는 미변경하되, 표에는 11번째로 등재. 실 frontmatter 환원 = Phase 2.)
3. **dormant 주석 "10" 3곳 (CLAUDE.md:86 / consumer-guide:59 / playbook:515) — Phase 2 에서 10→11 정정 + 재활성.** 원복 시 이 3곳 주석이 더는 "현재 opus override 상태"를 단정하지 않게 재활성하되, 잔존 stale count "10"→"11" 동반 정정. 방향 = Phase 1 에서 확정, 적용 = Phase 2.

### 원복 실행 범위 (Phase 분리)

- **Phase 1 (이 설계 PR — CFP-2554 Phase 1)**: ADR-117 표 정합(결정 1·Amendment 1 표 10→11) + 결정 1·3·Rationale 카운트 정정 + Amendment 1 dormant/superseded 마킹 + **본 Amendment 2 저술** + Story §7 설계 서사(내장 §8 Test Contract 포함). **frontmatter · plugin.json bump · dormant 주석 3곳 · marketplace = 미변경**(Phase 2 누출 방지). 이 PR 변경 파일 = ADR-117 단일.
- **Phase 2 (후속 구현 PR)**: 11 frontmatter `model: opus`(임시) → `model: fable` 환원 + 임시 코멘트(`# 임시(CFP-2241)...`) 제거 + dormant 주석 3곳 재활성(10→11) + 5 plugin(design/develop/review/requirements + wrapper) version bump + marketplace sync(mirrored field 변경 시 ADR-063 atomic invariant). **AC-1~AC-8 (CFP-2554 §5.2 / Story §7 Test Contract) = Phase 2 GREEN 대상** (Phase 1 이 이행하는 것은 AC-4 표 정합 일부 + 본 Amendment 저술).

### 재활성 계획 (Phase 2)

원복 시 dormant 보존 정책 3종이 재활성된다:
1. **결정 3 floor (Claude Code 2.1.170)**: fable alias 인식 floor 재유효 — consumer-guide floor 문장(§1b, `consumer-guide.md:59`)의 dormant 마킹 제거 + surgical count "10"→"11".
2. **ADR-057 Amendment 5 (fable model-unavailable → opus fresh re-spawn fallback)**: model-unavailable trigger 재활성 — `CLAUDE.md:86` 비-opus tier 섹션 + `docs/orchestrator-playbook.md:515` §3.0.12 fable model-unavailable case 의 dormant 주석 제거 + fallback 대상 count "10종"→"11종".
3. **SSOT dormant 주석 3곳 정정**: `CLAUDE.md:86`("surgical 10 에이전트") / `docs/consumer-guide.md:59`("surgical 10 에이전트") / `docs/orchestrator-playbook.md:515`("10 에이전트" + "10종") 을 모두 "11" 로 정정하고 "현재 opus override 상태" 단정을 제거.

### 근거 (Rationale)

- **옵션 A(표 11행 정합 + RequirementsReviewPL 정식 편입) 채택** — 실측 override 11 = 표 11 = dormant 주석 count 11 = 임시 코멘트 대상 11 로 네 SSOT 를 일치시켜 drift 를 청산. RequirementsReviewPL 이 "적대적 심판" category 에 성격상 부합(형제 3 리뷰 PL 과 동형)해 편입 근거 견고. TestContractArch consult 의 P0(표 10행 ≠ 실측 11) 청산.
- **옵션 B(override 만 제거, 표 10 유지) 기각** — RequirementsReviewPL 을 fable 근거 없이 되돌리거나(orphan) 표/실측 drift 를 영속화. 원복이 새 drift 를 만드는 자기모순.
- **옵션 C(RequirementsReviewPL 을 surgical 에서 제외 → 표 10 유지 + 이 PL 만 opus 정착) 기각** — 이 PL 은 요구사항리뷰 verdict(외부사실 게이트)로 적대적 심판 category 에 명백히 부합하며, 형제 3 리뷰 PL 과 다른 tier 를 부여할 원칙적 근거가 없다. 임의 예외는 정책 일관성 파괴.
