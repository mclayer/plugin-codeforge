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
    sunset_justification: "transitional override 는 ratchet 강화가 아니라 외부 제약(미 정부 fable 사용 불가)에 대한 임시 대응이다. 원의도(capability 상승이 2배 비용을 정당화하는 surgical 역할에 최강 모델 적용)는 thinking 프로파일 동일(ADR-117 컨텍스트)인 opus 로 충족 — 능력 손실 0. 명시 override(frontmatter 직접 치환) 채택 근거 = ADR-057 Amendment 5 의 매 spawn 실패→재시도 fallback 은 지연 + 제약 트리거 문구 불확실. 원복 trigger = 사용자 '제약 해제' 통지, 원복 절차 = (a) 10 frontmatter opus → fable 환원 + 임시 표식 코멘트 제거 (b) 본 Amendment 를 dormant/superseded 마킹 (c) floor·fallback 정책 재활성 확인 — 원복도 Story 경유. ADR-058 §결정 5 self-application (Amendment 시 sunset_justification 의무) 정합."
related_adrs:
  - ADR-057  # Orchestrator Opus 필수 mandate + Sonnet→Opus rate-limit fallback — 본 ADR §결정 5 (Orchestrator 제외) 정합. Amendment 5 (fable model-unavailable → opus fallback) = ADR-117 Amendment 1 로 dormant 보존.
related_stories:
  - CFP-2134  # carrier (Cross-repo Fable 5 채택 Epic — foundation)
  - CFP-2241  # Amendment 1 carrier (미 정부 제약 fable → opus 임시 override)
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

### 결정 1: surgical 채택 대상 10 에이전트에만 `model: fable` 적용

capability 상승이 2배 비용을 정당화하는 역할 = **chief author / 장기 agentic 코딩 / 적대적 심판**. 적용 대상 10개:

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

`model: fable` alias 는 Claude Code v2.1.170+ 에서만 인식된다(미인식 ID = silent fallback 없이 spawn 실패). 따라서 **codeforge 최소 Claude Code 버전 = 2.1.170**. consumer-guide §"필수 의존성" 에 명시한다. 2.1.170 미만 consumer 는 본 결정 1 의 10 에이전트(design / develop / review / requirements lane) spawn 이 실패한다.

### 결정 4: 풀 ID 아닌 alias `fable` 사용

풀 ID(`claude-fable-5`)가 아닌 alias `fable` 을 frontmatter 에 기재한다 — 버전 업그레이드(Fable 5.x → 차기) 자동 추적 best-practice. Orchestrator `opus` alias 관행과 동형.

### 결정 5: Orchestrator 모델 제외 — 현행 `opus` 유지

최상위 세션(Orchestrator) 모델은 현행 `opus`(ADR-057 mandate)를 유지한다. Fable Orchestrator 채택은 비용·세션 전반 영향이 별개 차원이므로 **별 결정 사안**으로 분리한다 — 본 ADR scope 외.

## 해소 기준

N/A — permanent policy. 본 ADR 은 모델 tier 선택 정책의 상시 기준으로, sunset 대상이 아니다. 단, 모델 세대 전환(차기 최강 모델 GA / Opus·Fable 가격 구조 변동 / Orchestrator Fable 채택 별 결정)이 발생하면 본 ADR 을 amend 하여 surgical 대상·floor 버전을 재산정한다.

## 근거 (Rationale)

- 옵션 A(opus 전체 → fable 전면 교체) **기각** — 단기 구조적 opus 에이전트(ModuleArch / APIContractArch / Refactor 등)까지 2배 비용을 물리나 long-horizon 이점 발현 표면이 작아 비용 대비 효용이 낮다.
- 옵션 B(minimal pilot 3~4개) **기각** — 채택 범위가 너무 좁아 chief author / 장기 코딩 / 적대적 심판 3 축의 효용을 동시에 검증하기 불충분하다.
- 옵션 C(surgical 10 에이전트 채택) **채택** — capability 상승이 2배 비용을 정당화하는 역할만 외과적으로 골라 적용. thinking 손실 0(프로파일 동일)이라 교체 부작용 없음. 제외 군은 현행 모델 유지로 비용 중립.

## 결과

- **lane PR(별 PR)**: design / develop / review / requirements 4 lane plugin 의 해당 에이전트 frontmatter `model:` 를 `fable` 로 변경 — 각 lane plugin repo 의 별 PR(본 wrapper foundation PR OOS).
- **marketplace sync**: plugin.json 메타 변경(version) 동반 시 ADR-063 atomic invariant 에 따라 marketplace sync PR 선행(본 Epic 범위).
- **consumer 호환성**: 2.1.170 미만 consumer 는 해당 lane 에이전트 spawn 실패 — consumer-guide floor 명시로 사전 고지.
- **Orchestrator Fable 채택**: 별 결정 사안(§결정 5) — 향후 별 ADR/CFP.

## 관련 파일

- `docs/consumer-guide.md`

## Amendment 1 (2026-06-14) — CFP-2241 — 미 정부 제약에 따른 fable → opus 임시 transitional override

### 성격

본 Amendment 는 **transitional**(임시 + 원복 가능)이다. ADR 본체 status 는 **Accepted 유지** — 결정 1~5 의 정책은 불변이며, 본 Amendment 는 외부 제약 기간에 한정해 모델 **alias 만** 임시 치환한다. 제약 해제 시 원복 절차 완료로 해소한다.

### 컨텍스트

2026-06-14 KST, 미 정부 제약으로 `fable` alias(Claude Fable 5) 사용이 불가해졌다. 그 결과 결정 1 의 surgical 10 에이전트(`model: fable`)가 spawn 실패/우회 상태가 된다. 기존 ADR-057 Amendment 5(fable model-unavailable → opus fresh re-spawn fallback)는 매 spawn 실패 후 재시도 방식이라 (a) 실패→재시도 지연이 누적되고 (b) 제약 환경의 에러 문구가 fallback trigger 문자열과 일치한다는 보장이 없어 trigger 가 불확실하다.

### 결정

결정 1 의 surgical 10 에이전트 frontmatter `model: fable` → `model: opus`(최신 Opus tier alias)로 **임시 override** 한다.

- **정책 불변**: "어느 역할이 fable 적격인가"(결정 1 표 — chief author / 장기 agentic 코딩 / 적대적 심판 10 역할)는 그대로다. 모델 alias 만 임시 치환한다.
- **능력 손실 0**: ADR-117 컨텍스트의 사실대로 fable 의 thinking 프로파일은 opus 4.8 과 동일(adaptive on / extended 없음)이라 `fable` → `opus` 교체 시 thinking 능력 손실이 없다.
- **명시 override 채택**: 매 spawn 실패 후 재시도하는 ADR-057 Amendment 5 fallback 에 의존하지 않고 frontmatter 를 직접 교체한다 — 지연 + trigger 불확실성 제거.
- **임시 표식**: 각 frontmatter `model:` 라인에 임시 override 임을 알리는 inline 코멘트(CFP-2241 / ADR-117 Amendment 1 / 원복 안내)를 부착한다.

적용 대상 10 에이전트(결정 1 표와 동일):

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

### 보존(미삭제) 명시 — dormant

다음 정책은 **삭제하지 않고 dormant 보존** 한다 — 제약 해제 시 즉시 재유효해야 하기 때문이다.

- **결정 3 floor(Claude Code 2.1.170)**: fable alias 인식 floor. 현재 wrapper self 는 opus override 라 floor 가 휴면이나, consumer-guide 의 floor 문장은 보존한다(원복 시 재유효).
- **ADR-057 Amendment 5(fable model-unavailable → opus fresh re-spawn fallback)**: 현재 surgical 10 이 opus override 라 model-unavailable trigger 가 휴면이다. ADR-057 §결정 4 / playbook §3.0.12 / CLAUDE.md "비-opus tier → Opus fallback" 문장은 dormant 주석만 부착하고 보존한다.

SSOT 문서 dormant 주석 부착 위치: `CLAUDE.md`(비-opus tier 섹션) · `docs/consumer-guide.md`(floor 의존성) · `docs/orchestrator-playbook.md`(§3.0.12 fable model-unavailable case).

### 원복 절차

원복 trigger = 사용자가 "제약 해제" 통지. 원복도 Story 경유로 수행한다.

1. 10 에이전트 frontmatter `model: opus` → `model: fable` 환원 + 임시 표식 코멘트 제거.
2. 본 Amendment 1 을 dormant/superseded 로 마킹(amendment_log + 본 섹션 상태 표기).
3. 보존해 둔 floor(결정 3) + ADR-057 Amendment 5 fallback + SSOT dormant 주석이 재활성됐는지 확인(주석 제거 / trigger 재유효).
4. 4 lane plugin + wrapper version bump + marketplace sync(mirrored field 변경 시 ADR-063 atomic invariant).

### 해소 기준

미 정부 제약 해제 시 위 원복 절차 완료로 본 Amendment 가 해소된다. 해소 시 ADR 본체는 변경 없이 결정 1~5 가 원래대로(fable surgical) 작동한다.

### 근거 (Rationale)

- 옵션 A(ADR-057 Amendment 5 자동 fallback 에 의존) **기각** — 매 spawn 실패→재시도 지연 누적 + 제약 환경 에러 문구가 fallback trigger 문자열과 일치한다는 보장 없음(trigger 불확실).
- 옵션 B(명시 frontmatter override) **채택** — 사전 결정적이라 지연 0, trigger 확실. thinking 프로파일 동일이라 능력 손실 0. floor·fallback 정책은 dormant 보존이라 원복 즉시 가능.
- 옵션 C(fable 영구 폐기 + opus 정착) **기각** — 사용자 결정상 fable 영구 폐기가 아니며 제약 기간 한정 조치다. 영구 전환은 원복 불가를 초래해 사용자 전제(임시 + 원복 가능)에 위배.
