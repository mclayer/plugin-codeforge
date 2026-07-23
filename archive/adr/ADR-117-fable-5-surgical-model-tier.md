---
adr_number: 117
title: Fable 5 surgical 모델 tier 채택 (chief author / 장기 agentic / 적대적 심판 한정)
status: Superseded
superseded_by: ADR-141
category: governance
date: 2026-06-10
carrier_story: CFP-2134
is_transitional: false   # ADR 본체 = permanent policy. [2026-07-03 CFP-2560 Amendment 3: 본 ADR 전체 Superseded by ADR-141 — fable 영구 폐기, 이력 보존.] [2026-07-24 CFP-2811 Amendment 4: obsolete 외부 제약 서사(구 Amendment 1·2) 본문 삭제 — Amendment 3 §결정 3 명시 override, 이력 = git history + ADR-141 컨텍스트 ledger.]
amends: null
supersedes: null
amendment_log:
  - by: "CFP-2241"
    date: "2026-06-14"   # 구 Amendment 1 (transitional override) — 서사 필드(scope/sunset_justification) = CFP-2811 Amendment 4 로 삭제, by/date 최소 audit skeleton 만 잔존 (결정-사실 = ADR-141 컨텍스트 ledger)
  - by: "CFP-2554"
    date: "2026-07-02"   # 구 Amendment 2 (원복 실행) — 서사 필드 = CFP-2811 Amendment 4 로 삭제, by/date 최소 audit skeleton 만 잔존 (결정-사실 = ADR-141 컨텍스트 ledger)
  - by: "CFP-2560"
    date: "2026-07-03"
    scope: "Amendment 3 — 본 ADR 전체 Superseded by ADR-141 (전 에이전트 opus 단일 tier 정책). fable 을 영구·전면 폐기(surgical 11 + 3-tier 폐지). frontmatter status Accepted → Superseded + superseded_by: ADR-141 추가. 본체 텍스트(결정 1~5 + Amendment 1·2)는 rewrite 0 — frozen audit trail 이력 보존. Amendment 1 옵션 C('fable 영구 폐기 + opus 정착') 기각 사유였던 '임시 조치·원복 가능' 전제가 사용자 새 directive('fable 안쓸거다. 전부 opus with 1M로 돌려라', 2026-07-03 KST)로 대체됨 → 영구 폐기가 이제 사용자 결정. 실 frontmatter opus 통일 + fable alias 청산 = CFP-2560 Phase 2."
    sunset_justification: "본 Amendment 는 ratchet 강화·약화가 아니라 상위 carrier(ADR-141)로의 supersede 전이다. fable surgical tier(비용 거버넌스 정제)의 폐기 = 3-tier 축소 = 약화 방향이므로 evidence 3축(ADR-058 §결정 5 / ADR-064 §결정 7)을 ADR-141 근거 섹션에 기재 — (a) 사용자 directive 명확 + fable↔opus 2일 4진동 obsolescence(진동 부채) (b) opus ≥ fable/sonnet/haiku reasoning(능력 상향) + machinery 소멸(운영 단순화) (c) fable→opus 11종 = 비용 절반(fable $10/$50 = opus $5/$25 의 2배, ADR-117 컨텍스트 실측). 본체 이력 보존 = Event Sourcing(frozen audit trail, ADR-042 Amd12 선례). is_transitional 무변경(false — 본체 permanent 였고 이제 Superseded)."
  - by: "CFP-2811"
    date: "2026-07-24"
    scope: "Amendment 4 — obsolete 외부 제약 서사 삭제 (Option B). 구 본문 `## Amendment 1`(CFP-2241 임시 override 서사) + `## Amendment 2`(CFP-2554 원복 서사) 전문 삭제 + frontmatter 해당 entry 의 scope/sunset_justification 필드 삭제(by/date 최소 audit skeleton 잔존) + is_transitional 주석 구 Amd1 절 삭제 + related_stories 주석 reword. Amendment 3 §결정 3('결정 1~5 + Amendment 1·2 텍스트 삭제 0') 명시 override — paired override = ADR-141 Amendment 5(§상태·§결정 2 보존지시 한정 override). 거버넌스 근거 = ADR-058 §결정 11(obsolete 사실서사 제거 이중 게이트: 보존결정 명시 amendment override + 사용자 비준 — 사용자 Option B sign-off 2026-07-24). 결정 1~5 + Amendment 3 + 상태/컨텍스트/근거/결과/관련 파일 = frozen 보존. 결정-사실 audit = ADR-141 §컨텍스트 진동 부채 ledger + plugins 4 CHANGELOG + git history."
    sunset_justification: "본 Amendment 는 tier 정책 무접촉 — frozen 이력-보존 default 의 obsolete 사실서사 1건 한정 governed 예외 집행(ADR-058 §결정 11)이다. evidence: ① 사용자 명시 비준(CFP-2811 §9 Option B sign-off, 2026-07-24 — 애매성 0) ② obsolete 3중 무효화(CFP-2554 해소 → ADR-141 fable 폐기 → CFP-2803/ADR-141 Amendment 4 fable 정식 재도입 6.120.0 live)로 서사가 기술한 상태 불성립 + stale 인과 참조의 하류 드리프트 실증(ADR-042 4곳) ③ 결정-사실 substance 는 ADR-141 ledger + CHANGELOG + git 에 복구 가능(의미 손실 0 — 외부 append-only core concern 무손상). is_transitional 무변경(false — 본체 Superseded 상태 유지)."
related_adrs:
  - ADR-057  # Orchestrator Opus 필수 mandate + Sonnet→Opus rate-limit fallback — 본 ADR §결정 5 (Orchestrator 제외) 정합. Amendment 5 (fable model-unavailable → opus fallback) = ADR-117 Amendment 1 로 dormant 보존, Amendment 2 로 재활성(Phase 2).
  - ADR-058  # §결정 11 (CFP-2811) — obsolete 사실서사 제거 이중 게이트 (본 ADR Amendment 4 의 거버넌스 근거, 첫 적용 사례)
  - ADR-125  # 요구사항리뷰 lane 신설 (CFP-2326) — RequirementsReviewPLAgent 도입원. ADR-125 가 CFP-2241 override 관습을 승계하며 surgical 명단을 10→11 로 늘렸으나 본 ADR 표를 미갱신 → Amendment 2 stale 발생원. Amendment 2 로 표 11행 정합.
related_stories:
  - CFP-2134  # carrier (Cross-repo Fable 5 채택 Epic — foundation)
  - CFP-2241  # 구 Amendment 1 carrier — 본문 서사 CFP-2811 Amendment 4 로 삭제 (결정-사실 = ADR-141 컨텍스트 ledger)
  - CFP-2554  # 구 Amendment 2 carrier — 본문 서사 CFP-2811 Amendment 4 로 삭제 (결정-사실 = ADR-141 컨텍스트 ledger)
  - CFP-2811  # Amendment 4 carrier (obsolete 외부 제약 서사 삭제 + Amendment 3 §결정 3 override)
related_files:
  - docs/consumer-guide.md
mechanical_enforcement_actions: []   # 신규 lint/sentinel 0 — model alias 적용은 각 lane plugin 의 에이전트 frontmatter (별 lane PR) 가 SSOT. Claude Code 버전 floor 는 런타임 spawn 실패로 자가 강제 (미인식 ID = silent fallback 없이 fail).
---

# ADR-117: Fable 5 surgical 모델 tier 채택 (chief author / 장기 agentic / 적대적 심판 한정)

## 상태

**Superseded by [ADR-141](ADR-141-all-opus-single-tier.md) (2026-07-03 KST — CFP-2560 Amendment 3).** ADR-141 이 전 에이전트 opus 단일 tier 정책을 신설하며 fable 을 영구·전면 폐기했다(surgical 11 + 3-tier 폐지). 본 ADR 의 결정 1~5(fable surgical tier) 는 더는 현행 정책이 아니다 — 현행 = 전 에이전트 opus 단일 tier(ADR-141 §결정 1). fable↔opus 4진동/2일 진동 부채를 청산하기 위해 dormant 보존이 아닌 완전 폐기를 채택했으며, 본체 텍스트는 **이력 보존(frozen audit trail)** 이다(삭제 아님). 상세 = ADR-141 + 하단 `## Amendment 3`.

> 원 상태 (참고): Accepted (2026-06-10 KST — CFP-2134 carrier). Cross-repo Fable 5 채택 Epic 의 foundation 설계 결정. 본 ADR 은 정책 SSOT 이며, 실제 `model: fable` alias 적용은 각 lane plugin 의 에이전트 frontmatter 변경(별 lane PR — design / develop / review / requirements)으로 실현된다.

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

최상위 세션(Orchestrator) 모델은 현행 `opus`(ADR-057 mandate)를 유지한다. Fable Orchestrator 채택은 비용·세션 전반 영향이 별개 차원이므로 **별도 결정 사안**으로 분리한다 — 본 ADR scope 외.

## 해소 기준

N/A — permanent policy. 본 ADR 은 모델 tier 선택 정책의 상시 기준으로, sunset 대상이 아니다. 단, 모델 세대 전환(차기 최강 모델 GA / Opus·Fable 가격 구조 변동 / Orchestrator Fable 채택 별도 결정)이 발생하면 본 ADR 을 amend 하여 surgical 대상·floor 버전을 재산정한다.

## 근거 (Rationale)

- 옵션 A(opus 전체 → fable 전면 교체) **기각** — 단기 구조적 opus 에이전트(ModuleArch / APIContractArch / Refactor 등)까지 2배 비용을 물리나 long-horizon 이점 발현 표면이 작아 비용 대비 효용이 낮다.
- 옵션 B(minimal pilot 3~4개) **기각** — 채택 범위가 너무 좁아 chief author / 장기 코딩 / 적대적 심판 3 축의 효용을 동시에 검증하기 불충분하다.
- 옵션 C(surgical 11 에이전트 채택) **채택** — capability 상승이 2배 비용을 정당화하는 역할만 외과적으로 골라 적용. thinking 손실 0(프로파일 동일)이라 교체 부작용 없음. 제외 군은 현행 모델 유지로 비용 중립. (채택 시점 카운트 = 10; ADR-125 요구사항리뷰 lane 신설로 11 로 증가 → CFP-2554 Amendment 2 로 표 정합.)

## 결과

- **lane PR(별 PR)**: design / develop / review / requirements 4 lane plugin 의 해당 에이전트 frontmatter `model:` 를 `fable` 로 변경 — 각 lane plugin repo 의 별 PR(본 wrapper foundation PR OOS).
- **marketplace sync**: plugin.json 메타 변경(version) 동반 시 ADR-063 atomic invariant 에 따라 marketplace sync PR 선행(본 Epic 범위).
- **consumer 호환성**: 2.1.170 미만 consumer 는 해당 lane 에이전트 spawn 실패 — consumer-guide floor 명시로 사전 고지.
- **Orchestrator Fable 채택**: 별도 결정 사안(§결정 5) — 향후 별도 ADR/CFP.

## 관련 파일

- `docs/consumer-guide.md`

## Amendment 3 (2026-07-03) — CFP-2560 — 본 ADR 전체 Superseded by ADR-141 (fable 영구 폐기)

### 성격

본 Amendment 는 **supersede 전이**다 — 본 ADR(fable surgical tier)이 상위 carrier [ADR-141](ADR-141-all-opus-single-tier.md)(전 에이전트 opus 단일 tier)로 대체된다. frontmatter status = **Accepted → Superseded** + `superseded_by: ADR-141`. 본체 텍스트(결정 1~5 + Amendment 1·2)는 **rewrite 0** — frozen audit trail 로 이력 보존한다(Event Sourcing, ADR-042 Amd12 선례). Amendment 2 가 permanent 였으나, permanent ≠ 불변 supersede — 상위 정책 재편으로 전체가 Superseded 될 수 있다.

### 컨텍스트

- **트리거**: 사용자 directive verbatim(2026-07-03 KST, CFP-2560 §1) — **"fable 안쓸거다. 전부 opus with 1M로 돌려라"**. CFP-2554(2026-07-02 fable 원복)의 직접 revert 이자, 이번엔 **영구·전면**(sonnet/haiku 포함)·1M 통일.
- **진동 부채**: fable↔opus 가 2일간 4회 진동(CFP-2134 fable 채택 → CFP-2241 opus 임시 → CFP-2554 fable 원복 → CFP-2560 fable 폐기). dormant 보존이 매번 재활성 유혹을 남겼다(4번째 진동). 이번엔 dormant 아닌 완전 폐기(fable 삭제 + 3-tier machinery 소멸).
- **Amendment 1 옵션 C 전제 대체**: Amendment 1(CFP-2241)은 "옵션 C(fable 영구 폐기 + opus 정착)"를 "사용자 결정상 fable 영구 폐기가 아니며 제약 기간 한정 조치"라는 이유로 기각했었다. 그 전제("임시·원복 가능")가 사용자 새 directive 로 **대체**됨 → fable 영구 폐기가 이제 사용자 결정이다.

### 결정

1. **본 ADR 전체 Superseded** — 결정 1~5(fable surgical tier)는 더는 현행 정책이 아니다. 현행 = ADR-141 §결정 1(전 에이전트 opus 단일 tier).
2. **fable 완전 폐기(dormant 아님)** — surgical 11 표 / v2.1.170 floor(결정 3) / ADR-057 fable fallback(§결정 4) / SSOT 문장 모두 청산(ADR-141 §결정 2·7 Phase 2). dormant 재활성 채널 제거 = 진동 부채 청산.
3. **본체 이력 보존** — 결정 1~5 + Amendment 1·2 텍스트 삭제 0. `## 상태` 섹션 supersede 선언 + 본 Amendment 3 append 만.

### 원복 실행 범위 (Phase 분리 — CFP-2560)

- **Phase 1 (이 설계 PR)**: ADR-141 신규 저술 + 본 ADR status Superseded 전이(frontmatter + `## 상태` + Amendment 3) + ADR-042 Amd19 + ADR-057 Amd6 + architecture doc 갱신. **frontmatter model / plugin bump / SSOT 3 문서 / registry / marketplace = 미변경**(Phase 2 누출 방지).
- **Phase 2 (구현 PR)**: 45 frontmatter `model: opus` 통일 + SSOT 3 문서 fable·v2.1.170·stakes-gated 청산 + registry dead 마킹 + plugin bump 9 + CHANGELOG + marketplace sync + CFP-2134 Epic close.

### 근거 (Rationale)

- **옵션 A(dormant 보존 — fable 정책 두되 opus 임시 override) 기각** — CFP-2241/2554 진동 부채의 재생산 구조. 4번째 진동 유혹 존속.
- **옵션 B(fable 완전 폐기 + ADR-141 carrier supersede) 채택** — 사용자 directive 직접 이행. 진동 부채 완전 청산 + 운영 단순화(3-tier machinery 소멸) + surgical 11 비용 절반(fable→opus). 본체 이력 보존으로 audit trail 무손실.
- 약화-evidence 3축 = ADR-141 근거 섹션 SSOT (본 amendment_log row sunset_justification 요약).

## Amendment 4 (2026-07-24) — CFP-2811 — obsolete 외부 제약 서사 삭제 (구 Amendment 1·2 본문 제거 + Amendment 3 §결정 3 명시 override)

### 성격

본 Amendment 는 **obsolete 사실서사 제거**다 — 구 `## Amendment 1`(CFP-2241, 2026-06-14: 외부 제약에 따른 fable→opus 임시 transitional override 서사) + 구 `## Amendment 2`(CFP-2554, 2026-07-02: 제약 해소에 따른 fable 원복 서사) 본문 전문과 frontmatter 의 해당 서사 필드를 삭제한다. Amendment 3 §결정 3("본체 이력 보존 — 결정 1~5 + Amendment 1·2 텍스트 삭제 0")의 보존지시를 **명시 override** 한다. paired override = **ADR-141 Amendment 5** — ADR-141 §상태·§결정 2 의 "ADR-117 본체 텍스트 이력 보존, 삭제 안 함" 지시의 동반 한정 override. 거버넌스 근거 = **ADR-058 §결정 11**(obsolete 사실서사 제거 이중 게이트: ① 보존결정 명시 amendment override ② 사용자 명시 비준) 충족 — 사용자 비준 = CFP-2811 Story §9 **Option B sign-off (2026-07-24)**.

### 컨텍스트 (obsolete 판정 — 3중 무효화)

구 Amendment 1 이 서술한 "외부 제약으로 fable 사용 불가" 사실 상태는 3중으로 무효화됐다:
1. **CFP-2554 (2026-07-02)** — 제약 해소, fable 원복 완료 (구 Amendment 2).
2. **ADR-141 / CFP-2560 (2026-07-03)** — fable 완전 폐기 (서사의 대상 자체 소멸).
3. **CFP-2803 / ADR-141 Amendment 4 (2026-07-23)** — **Fable 5 정식 재도입**(apex 10종 carve-out, 6.120.0 live). 현재 fable 정상 가용 — 서사가 기술한 상태의 정반대가 현행.

서사는 유지 비용만 남긴다: 문서 무게 + stale 인과 참조의 하류 드리프트 재생산(ADR-042 4곳 실증 — 본 Story 가 동반 정정).

### 결정 (삭제/보존 열거)

**삭제 (본 Amendment 집행)**:
1. 본문 구 `## Amendment 1` 전문 (구 L126-191 — override 서사·적용 표·dormant 보존·원복 절차·근거).
2. 본문 구 `## Amendment 2` 전문 (구 L193-227 — 원복 실행·재활성 계획·근거).
3. frontmatter amendment_log 구 Amendment 1·2 entry 의 서사 필드(scope / sunset_justification) — `by`/`date` 는 최소 audit skeleton 으로 잔존.
4. frontmatter `is_transitional` 주석의 구 Amendment 1 절 + related_stories CFP-2241/CFP-2554 주석의 서사절 (reword — carrier key 지칭만).

**보존 (frozen 그대로 — byte 무변경)**:
- `## 상태` · `## 컨텍스트` · 결정 1~5 · `## 해소 기준` · `## 근거` · `## 결과` · `## 관련 파일` · `## Amendment 3` 전문 — Amendment 3 가 Amendment 1·2 를 인용하는 dated 서술 포함(시점 고정 참, falsify 아님).
- 결정-사실 audit trail: **ADR-141 §컨텍스트 "fable↔opus 진동 부채" ledger**(CFP-2241 override 부과 + CFP-2554 원복 사실 rows — byte 무변경) + `plugins/{codeforge-design,codeforge-develop,codeforge-requirements,codeforge-review}/CHANGELOG.md` 원복 기록(append-only) + **git history**(삭제 서사 전문 복구 채널). → "의미 손실 0" 성립 (firsthand 확인 — CFP-2811 Story §7.4).

### 근거 (Rationale)

- **옵션 A(스텁 슬림화 — Superseded pointer 만 잔존) 기각** — 결정 1~5(원 surgical 결정)와 Amendment 3(supersede 기록)까지 삭제하면 ADR-141 §결정 2 보존지시와 과잉 충돌 + supersede 이력 손실. 사용자 최종 비준도 Option B (§9 재비준 — 충돌 인지 후).
- **옵션 B(obsolete 서사 한정 full 삭제 + 보존결정 2건 amendment override) 채택** — 사용자 확정 (2026-07-24). 삭제 범위를 obsolete 서사(구 Amendment 1·2)로 한정하고, 결정-사실 substance 는 ADR-141 ledger + CHANGELOG + git 에 잔존시켜 audit-trail invariant 충족.
- **frozen audit trail 원칙 자체는 철회 아님** — dated 이력의 byte-보존 default 는 존속한다. 본 건은 ADR-058 §결정 11 이중 게이트를 통과한 obsolete 사실서사 1건 한정의 governed 예외 집행이며, silent 삭제가 아니라 본 Amendment 가 삭제 범위를 열거해 audit 를 남긴다.
