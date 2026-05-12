---
adr_number: 57
title: Orchestrator Opus 필수화 + Sonnet → Opus rate-limit fallback 정책
date: 2026-05-11
status: Accepted
category: governance
is_transitional: true
carrier_story: CFP-379
supersedes: []
amends: ADR-042
amendment_log:
  - by: "CFP-392"
    date: "2026-05-11"
    scope: "is_transitional 신설 + 해소 기준 섹션 추가 (Amendment 1)"
    sunset_justification: "최초 transitional 분류 + sunset 기준 신설 — ADR-058 §결정 1·2·3·5 self-application 첫 사례 (CFP-387 정책 첫 적용). 본 Amendment 1 이전에는 sunset 기준 부재 → ratchet anti-pattern visibility 발화 채널이 처음 열림. 기존 정책 (결정 1·2·3) 변경 0건, 종료 조건만 명시."
  - by: "CFP-393"
    date: "2026-05-11"
    scope: "Sunset gate 2 (결정 2 해제) measurement contract 강화 + KPI dashboard reference (Amendment 2). 분모 / 분자 / sample size sufficient sentinel / 측정 단위 / window 명시. 기존 정책 (결정 1·2·3) 본문 변경 0건."
    sunset_justification: "Amendment 1 이 결정 2 sunset gate 를 declaration form 으로 정의 — `월 50+ Sonnet spawn 환경 3개월 연속 fallback < 1%`. 본 Amendment 2 는 해당 declaration 의 mechanical realization (KPI dashboard infrastructure carrier) 만 추가, sunset criteria 자체 변경 0건. sunset 효력 = unchanged (Amendment 1 시점과 동일 — 측정 시작 시점만 본 Amendment 2 merge 이후로 명시화). ADR-060 §결정 12 (CFP-C 잠정 = 본 Amendment 2 + KPI dashboard, framework 첫 non-sunset application) carry. ADR-058 §결정 5 (Amendment 시 sunset_justification 의무) self-application — 본 row 자체가 그 정합."
  - by: "CFP-448"
    date: "2026-05-12"
    scope: "§결정 3 selective rollback (Amendment 3) — 6 agent 중 CodebaseMapperAgent / RefactorAgent / DeveloperPLAgent 3종 Opus → Sonnet 복귀, FeasibilityAgent / ContinuityAgent / ChangeImpactAgent 3종 Opus 유지. §결정 3 표 갱신 + sunset gate 2 measurement contract 분모 5종 → 8종 갱신 (ADR-057 §결정 3 = SSOT, CLAUDE.md L127 = mirror reference). 결정 1·2 본문 변경 0건."
    sunset_justification: "§결정 3 일부 revert 는 ratchet anti-pattern 이 아니라 axis-A (operational cost trade-off) + axis-B (ADR-042 §결정 2 invariant 정합) + axis-C (CL-6 사용자 확정 SSOT direction) 3축 evidence 기반 selective re-evaluation. CFP-379 → CFP-448 (2026-05-11 → 2026-05-12) 운영 evidence: (1) 사용자 framing (CFP-448) verbatim 적용: '내가 보기엔 코드 작성 에이전트들이 sonnet이 되는게 낫지 않을까? 왜냐하면 아키텍트가 짜준 디자인 명세에서 제한되게 움직여 고도의 추론이 필요하지 않기 때문이다' — DeveloperPLAgent 는 ADR-042 §결정 1 (b) 'Implementation work — code write / refactor / test 구현' verbatim 정의에 정합 회귀 (사용자 framing 직접 적용, Codex re-review 면제). (2) Codex review finding (CFP-379) 의 mandate 깊이 부족 우려는 CodebaseMapper / Refactor 2종 single-mandate advocacy agent 에서 mandate text 재정의 (description / 본문 role 정의 강화) 산출물 동시 의무 발화로 해소 — 단순 model field downgrade 금지. (3) Opus 유지 3종 (Feasibility / Continuity / ChangeImpact) 은 architecture 해석 / cross-Story pattern detection / 사용자 framing verbatim ('changeimpact는 내가 보기에 opus가 괜찮아보인다') — Sonnet cover 불가 또는 사용자 확정 영역으로 ADR-042 §결정 1 (e)/(f)/(a) tier criteria 정합. (4) sunset gate 1 ('Sonnet 잔류 agent 0건') 거리 증가 (5종 → 8종) 는 reverse direction 으로 보이나, 본 ADR 의 의도 (Orchestrator 차단 위험 구조적 해결) 는 결정 1 (Opus mandate) 으로 이미 달성 — gate 1 자체는 향후 Sonnet 모두 폐지될 때 발화하는 idealized end-state. 본 Amendment 3 의 selective rollback 은 operational reality (Opus token cost vs reasoning 품질 trade-off) 와 governance reality (ADR-042 §결정 2 invariant + ADR-042 §결정 1 (b) Implementation work 정합) 의 균형 → ratchet 회피 evidence. (5) ADR-058 §결정 5 self-application 두 번째 사례 (Amendment 2 첫 사례 후) — Amendment 시 sunset_justification 의무 정합."
  - by: "CFP-264"
    date: "2026-05-13"
    scope: "§결정 3 selective rollback 확장 (Amendment 4) — Amendment 3 의 Opus 유지 3종 (FeasibilityAgent / ContinuityAgent / ChangeImpactAgent) 모두 Opus → Sonnet 복귀 (ResearcherAgent 제외, path B 정합 — Codex proactive check touchpoint #4 권장 + 사용자 CL-1 확정). ResearcherAgent Opus 유지 (ADR-046 §결정 4·5 본문 invariant 정합 — 변경 0건). §결정 3 표 갱신 + Sunset gate 2 measurement contract 분모 8종 → 11종 갱신 (ADR-057 §결정 3 = SSOT, CLAUDE.md L127 = mirror reference). 결정 1·2 본문 변경 0건 + Amendment 1·2 sunset criteria 자체 변경 0건. ChangeImpactAgent 는 CFP-448 wave 에서 이미 sibling 측 Sonnet (commit c4084d8) → 본 Amendment 4 = SSOT (본 ADR 표) 측 갱신 + drift 정합 회복."
    sunset_justification: "axis-A (operational cost trade-off) 추가 가중 evidence — CFP-264 = CFP-448 의 reverse direction 2차 evidence. 사용자 §1 verbatim ('토큰이 너무 많이 쓰여서 opus를 조금 보수적으로 써야겠다') 직접 적용 + ADR-042 §결정 1 Sonnet (a) single-mandate advocacy criteria 회귀. 본 ADR `is_transitional: true` (Amendment 1) → ADR-058 §결정 5 self-application 세 번째 사례 (Amendment 2 / Amendment 3 prior art 정합). ratchet anti-pattern 회피 evidence 5종: (1) sunset gate 1 ('Sonnet 잔류 0건') 거리 증가 8 → 11종 reverse direction visibility — 본 ADR 핵심 의도 (결정 1 Orchestrator Opus mandate, 차단 위험 구조적 해결) 와 별개. gate 1 = idealized end-state, 모든 agent role 이 Opus 가 필요할 정도로 진화한 시점. 본 Amendment 4 는 그 종점이 아직 멀다는 운영 evidence (Sonnet sufficient role 추가 확인) 반영. (2) path B 채택 = ADR-046 §결정 4·5 본문 invariant (Researcher Opus tier rationale = 'Sonnet 대수 불가 — deep concept reasoning 책임') 정합 보존 — Codex proactive check (touchpoint #4 divergence detected) finding 직접 채택, mandate 약화 회피. PL 권장 Option B (사용자 framing verbatim 직접 적용 + mandate text reword) 도 Codex divergence 후 reject — Researcher mandate text invariant 강한 보존 우선. (3) Sunset gate 2 분모 11종 확대 = KPI sample size 자연 회복 강화 (CFP-393 §11 follow-up #1 mitigation patterning — CFP-448 의 8종 mitigation 의 추가 확장). 측정 contract 자체 변경 0건 (≥ 50 spawn / 3개월 / < 1%). (4) selective rollback 패턴 = 단일 model tier 강제 일괄 적용 회피 — Researcher 의 mandate boundaries (Concept formulation / Deep exploration / Requirement reshape) 본문 invariant 정합 + 나머지 3 agent 의 single-mandate advocacy (Feasibility — 구현 가능성 등급) / single-Story cross-ref (Continuity — 충돌/중복/의존 분류) / single-Story DELTA mapping (ChangeImpact — AS-IS → DELTA 매핑) 정합 분리. (5) ADR-042 Amendment 6 cross-ref atomic (tier criteria SSOT 동시 갱신) — drift 차단 mechanism 발효 (Amendment 5 / Amendment 3 prior art 정합)."
related_stories:
  - CFP-379
  - CFP-392
  - CFP-393
  - CFP-448
  - CFP-264
related_adrs:
  - ADR-042
  - ADR-039
  - ADR-058
related_files:
  - CLAUDE.md
  - docs/orchestrator-playbook.md
  - docs/domain-knowledge/orchestrator-discipline/measurement-channel.md
---

# ADR-057: Orchestrator Opus 필수화 + Sonnet → Opus rate-limit fallback 정책

## 상태

**Accepted (2026-05-11)**

## 컨텍스트

Claude Sonnet 모델의 사용량 한도(rate limit, 세션 한도, 주간 한도)로 인해 codeforge Orchestrator 세션이 차단되는 경우가 발생한다. Orchestrator가 Sonnet으로 실행 중일 때 Sonnet quota가 소진되면 Orchestrator 자체가 차단되어 모든 작업이 중단된다.

또한 Codex 독립 리뷰 결과 FeasibilityAgent·ContinuityAgent·ChangeImpactAgent·CodebaseMapperAgent·RefactorAgent·DeveloperPLAgent 6개 에이전트가 Sonnet보다 Opus 기준에 더 부합함이 확인되어 ADR-042 Amendment 4와 함께 처리한다.

사전 탐지 불가 제약: Anthropic API quota 임박 시그널이 Claude Code CLI를 통해 agent에게 전파되지 않아 사전 탐지는 구조적으로 불가능하다. 사후 에러 감지 후 fallback으로 대응한다.

## 결정

### 결정 1: Orchestrator 모델 = Opus 필수

codeforge를 사용하는 모든 Claude Code 세션에서 Orchestrator 모델은 **claude-opus-4-7 필수**. CLAUDE.md 세션 개시 의무 체크리스트에 강제 추가. Consumer overlay로 축소 불가.

근거: Orchestrator가 Opus로 실행되면 Sonnet quota 소진이 Orchestrator를 차단하지 않음. Subagent의 Sonnet spawn 실패는 Orchestrator(Opus)가 감지하고 Opus fallback으로 재시도 가능.

CLAUDE.md 세션 개시 의무 체크리스트 업데이트는 CFP-379 S2 Story에서 수행한다.

### 결정 2: Sonnet subagent rate-limit → Opus fallback (max 1회)

Orchestrator가 Sonnet 모델 subagent spawn 시 rate-limit 에러를 수신하면:

1. 동일 입력 패킷으로 `model: opus` 재spawn (1회 한정)
2. 재spawn 성공 시 정상 진행 — §14 Lane Evidence에 `[rate-limit-fallback:sonnet→opus]` 태그 추가
3. Opus도 실패 시 사용자에게 rate-limit 상황 알림 후 대기 (자동 재시도 금지)

판별 기준: Agent tool result에 "rate limit", "quota exceeded", "429" 포함 시 rate-limit로 분류. task failure(agent 로직 오류)와 혼동하지 않도록 에러 메시지 패턴 확인 필수.

이 정책은 orchestrator-playbook.md §3 lane spawn 절차에 명문화한다.

### 결정 3: ADR-042 Amendment 4 + Amendment 5 + Amendment 6 적용 (selective tier 할당 — Amendment 4 갱신)

본 ADR 이 ADR-042 Amendment 4 (carry) + Amendment 5 (CFP-448 Amendment 3 cross-ref) + Amendment 6 (CFP-264 Amendment 4 cross-ref) 를 carry. 최종 tier 할당 (**Amendment 4 갱신 후 SSOT** — path B selective rollback 결과):

| Agent | 최종 tier | 비고 |
|---|---|---|
| ResearcherAgent | **Opus 유지** | OPUS (g) Deep research with reshape mandate — ADR-046 §결정 4·5 본문 invariant (Sonnet 대수 불가 — deep concept reasoning 책임). path B (Codex proactive check touchpoint #4 권장 + 사용자 CL-1 확정) 정합 Researcher Sonnet 다운 reject. |
| FeasibilityAgent | **Sonnet (Amendment 4 rollback)** | ADR-042 §결정 1 Sonnet (a) single-mandate advocacy 정합 — 구현 가능성 등급 + 경고 힌트 (supervisor synthesis 영역 아님, src+ADR read-only). 사용자 §1 verbatim 직접 적용. mandate text 변경 0건 (exclusion criterion — ADR-042 Amendment 6 §변경 사항 정합). |
| ContinuityAgent | **Sonnet (Amendment 4 rollback)** | ADR-042 §결정 1 Sonnet (a) single-mandate advocacy 정합 — 본 lane 단일 Story 안 기존 ADR/Story cross-ref만 수행 (cross-Story pattern detection 아님, 그 영역 = PMOAgent Opus 유지). 사용자 §1 verbatim 직접 적용. mandate text 변경 0건 (exclusion criterion). |
| ChangeImpactAgent | **Sonnet (Amendment 4 rollback)** | ADR-042 §결정 1 Sonnet (a) single-mandate advocacy 정합 — single-Story DELTA mapping (AS-IS → DELTA, src/** read-only). 본 Amendment 4 SSOT 측 갱신 (CFP-448 wave 에서 이미 sibling 측 Sonnet, drift 정합 회복). mandate text 변경 0건 (exclusion criterion). |
| CodebaseMapperAgent | **Sonnet (Amendment 3 rollback) + mandate text 재정의 의무** | ADR-042 §결정 2 original 분류 정합 (single-mandate advocacy). Codex review (CFP-379) symbol resolution 정확도 finding 은 mandate text 재정의 동시 산출물로 해소 — 단순 model field downgrade 금지 |
| RefactorAgent | **Sonnet (Amendment 3 rollback) + mandate text 재정의 의무** | ADR-042 §결정 2 original 분류 정합 (single-mandate advocacy). Codex review (CFP-379) advocacy 품질 finding 은 mandate text 재정의 동시 산출물로 해소 |
| DeveloperPLAgent | **Sonnet (Amendment 3 rollback)** | ADR-042 §결정 1 (b) "Implementation work — code write / refactor / test 구현" verbatim 정합 회귀. 사용자 framing (CFP-448) verbatim: '코드 작성 에이전트들이 sonnet이 되는게 낫지 않을까? 왜냐하면 아키텍트가 짜준 디자인 명세에서 제한되게 움직여 고도의 추론이 필요하지 않기 때문이다' — mandate 이미 명확, 재정의 불필요 + Codex re-review 면제 |

**Sonnet 잔류 + fallback 적용 대상 (Amendment 4 후 11종)** — ADR-057 §결정 3 = SSOT, CLAUDE.md L127 = mirror reference:
1. DeveloperAgent (codeforge-develop)
2. BackendDeveloperAgent (webapp preset)
3. FrontendDeveloperAgent (webapp preset)
4. IntegrationTestAgent (codeforge-test)
5. StatefulTestAgent (codeforge-test)
6. DeveloperPLAgent (codeforge-develop) — **Amendment 3 신규**
7. CodebaseMapperAgent (codeforge-design) — **Amendment 3 신규**
8. RefactorAgent (codeforge-design) — **Amendment 3 신규**
9. FeasibilityAgent (codeforge-requirements) — **Amendment 4 신규**
10. ContinuityAgent (codeforge-requirements) — **Amendment 4 신규**
11. ChangeImpactAgent (codeforge-requirements) — **Amendment 4 신규** (CFP-448 wave sibling 측 이미 Sonnet, SSOT drift 정합 회복)

> **SSOT 명시 (CFP-448 CL-6 사용자 확정 + CFP-264 CL-1 사용자 확정 — path B)**: 본 §결정 3 표 가 Sonnet 잔류 agent 명단의 단일 source of truth 다. `CLAUDE.md` "Sonnet subagent rate-limit → Opus fallback (ADR-057)" 섹션의 명단은 본 표 의 mirror reference 임. drift 시 본 ADR 표 우선. mirror 갱신 의무 = 본 ADR Amendment 의 part of definition of done.

## 근거

- Orchestrator Opus 전환은 Sonnet quota 소진 문제의 구조적 해결책
- Fallback 정책은 rate-limit 에러가 Claude Code Agent tool result에서 감지 가능한 경우에만 작동
- ADR-042 §결정2 역전 근거: Codex 독립 리뷰에서 CodebaseMapper·Refactor의 Sonnet mandate 부족 확인 (symbol resolution 정확도, advocacy 품질)
- measurement-channel.md Phase 2 deferred item "rate-limit cascade detection"을 본 ADR의 fallback 정책으로 RESOLVED 처리

## 결과

### 긍정
- Sonnet quota 소진 시 codeforge 작업 흐름 연속성 보장 (Orchestrator 차단 제거)
- 6개 agent Opus 상향으로 reasoning 품질 개선
- measurement-channel.md Phase 2 deferred item 해소

### 부정
- 비용 증가: Orchestrator + 상향 6 agent Opus 전환 → 토큰 비용 증가 (품질·연속성 우선 결정)
- Opus도 rate-limit 도달 시 동일 문제 재발 가능 (단, Sonnet과 별도 quota)
- rate-limit 판별이 Agent tool result 에러 메시지 문자열 패턴에 의존 → Anthropic CLI 에러 포맷 변경 시 오탐/미탐 위험

## 해소 기준

본 ADR 은 `is_transitional: true` (안전망 / fallback policy carrier — 영구 정책 아님). 아래 sunset gate 2종은 결정 1·결정 2 별도 독립 발화 (한 gate 만 충족 시 해당 결정만 부분 archive, 둘 다 충족 시 ADR 전체 Accepted → Superseded 전이). ADR-058 §결정 3 정합 — 각 gate 별 측정성 3-tuple (metric / who / how) 정량 명시.

### Sunset gate 1 — 결정 1 (Orchestrator Opus 필수화) 해제 조건

| 항목 | 내용 |
|---|---|
| **metric** | 전 Sonnet subagent 의 Opus 승격 결정 ADR Accepted — 구체적으로 ADR-042 Amendment N 형식으로 "Sonnet 잔류 agent 0건" 명문화. 잔류 agent 식별 SSOT = ADR-042 본문 + 각 lane plugin `agents/*.md` `model:` field. |
| **who** | ArchitectPLAgent (ADR-042 Amendment N 검토 시 자체 검증) + GitOpsAgent (`scripts/check-sonnet-agent-count.sh` — CFP-B carry 또는 별도 CFP, 미구현 시 ArchitectPLAgent manual review) |
| **how** | `Grep -l "model: claude-sonnet" plugin-codeforge-*/agents/*.md` 결과 0건 + ADR-042 Amendment N 본문 "Sonnet 잔류 agent 0건" 명시 + 본 §결정 1 archive 의무 (별도 carrier Amendment 로 sunset_justification 명시). 분기점 = Sonnet quota 소진 시 Orchestrator 차단 위험이 구조적으로 사라지는 시점 (모든 Sonnet agent Opus 상향 후). |

### Sunset gate 2 — 결정 2 (Sonnet → Opus rate-limit fallback) 해제 조건

> **Amendment 2 (CFP-393, 2026-05-11)** 가 본 gate 의 measurement contract 를 mechanical 화. KPI dashboard infrastructure = `scripts/measure-rate-limit-fallback.sh` + `templates/github-workflows/rate-limit-fallback-kpi.yml` + `docs/kpi/rate-limit-fallback.json` + `docs/evidence-checks-registry.yaml` 두 번째 entry `rate-limit-fallback-rate`. 본 표의 measurement 기준은 Amendment 2 시점에 정량 정의되었다. gate 자체 (≥ 50 spawn / month / 3개월 연속 / < 1%) 변경 0건.

| 항목 | 내용 |
|---|---|
| **metric** | 월 50회 이상 Sonnet subagent spawn 발생 환경에서 3개월 연속 rate-limit fallback 발생률 < 1%. 분자 = §14 Lane Evidence `transcript` 필드의 `[rate-limit-fallback:sonnet→opus]` 태그 발화 건수 / 분모 = 월간 Sonnet 잔류 agent **11종 (Amendment 4 후 SSOT — DeveloperAgent · BackendDeveloperAgent · FrontendDeveloperAgent · IntegrationTestAgent · StatefulTestAgent · CodebaseMapperAgent · RefactorAgent · DeveloperPLAgent · FeasibilityAgent · ContinuityAgent · ChangeImpactAgent)** 의 spawn row 카운트. 측정 단위 = calendar month UTC (half-open `[month-N-start, month-N+1-start)`). minimum sample size gate (월 < 50 spawn 환경 = `sample_size_sufficient: false`, gate 발화 보류 — zero division 회피 + 거짓 PASS/FAIL 신호 차단). **Amendment 3 (CFP-448) 효과: 분모 5종 → 8종 확대 → KPI sample size 자연 회복 (CFP-393 §11 follow-up #1 mitigation). Amendment 4 (CFP-264) 추가 확장: 분모 8종 → 11종 (path B 정합 — Researcher 제외 3 Requirements agent 추가) → mitigation 효과 추가 강화**. |
| **who** | `templates/github-workflows/rate-limit-fallback-kpi.yml` (monthly cron, 1일 00:00 UTC — Amendment 2 신설) + Orchestrator (§14 Lane Evidence row 작성 시 `[rate-limit-fallback:sonnet→opus]` 태그 부착 의무 — CLAUDE.md "Sonnet subagent rate-limit → Opus fallback (ADR-057)" 섹션 verbatim). |
| **how** | (1) workflow 가 `scripts/measure-rate-limit-fallback.sh` 실행 → wrapper `docs/stories/**` + internal-docs `<plugin-folder>/stories/**` 양쪽의 §14 Lane Evidence scan → 3개월 rolling window 의 분모 / 분자 집계 → `docs/kpi/rate-limit-fallback.json` 갱신 (auto-PR, ADR-024 §결정 6 정합). (2) `gate_status` enum = `pending` / `sample_insufficient` / `on_track` / `threshold_violated`. 3개월 모두 `on_track` 충족 시 ADR-057 §결정 2 sunset 가능 (별도 carrier — ADR-057 Amendment N 또는 후속 CFP). (3) `threshold_violated` 시 workflow 가 Issue auto-open (label = `codeforge-kpi-alert`). (4) registry entry `rate-limit-fallback-rate` (`current_tier: warning`) — advisory dashboard, PR block 없음. 미달 시 본 §결정 2 archive 의무 (별도 carrier Amendment 로 sunset_justification 명시). |

### Sunset 발화 시 처리 절차

1. 결정 1 gate 충족 → ADR-057 §결정 1 부분 archive (Amendment append + `is_transitional` 평가 갱신). Orchestrator Opus mandate 는 별도 ADR 또는 CLAUDE.md 영구 정책 carrier 로 transfer 또는 제거 결정.
2. 결정 2 gate 충족 → ADR-057 §결정 2 부분 archive. fallback 절차 (orchestrator-playbook.md §3.0.12) NO-OP 처리.
3. 둘 다 충족 → 본 ADR 전체 status Accepted → Superseded 전이. 후속 ADR carrier 명시 또는 정책 제거 결정 명시.
4. 일부 충족 시 충족된 결정만 부분 archive (해당 amendment_log row 에 `sunset_justification` 의무 명시 — ADR-058 §결정 5 정합).

## Amendment 1 (2026-05-11) — CFP-392 — 해소 기준 섹션 신설

### 변경 사항

1. **frontmatter `is_transitional: true` 신설**: 현재 ADR 분류 = 안전망 / fallback policy carrier — 영구 정책 아님. ADR-058 §결정 1 self-application — 안전망 ADR 의 transitional 분류 명시 의무 첫 발화.
2. **본문 `## 해소 기준` 섹션 신설**: 위 섹션 — 결정 1 · 결정 2 별 측정성 3-tuple (metric / who / how) + 부분 sunset 처리 절차. ADR-058 §결정 2 self-application — 위치 invariant ("결과" 직후 / "관련 파일" 직전) 정합.
3. **frontmatter `amendment_log` row 추가**: `by: CFP-392` / `date: 2026-05-11` / `scope: is_transitional 신설 + 해소 기준 섹션 추가` / `sunset_justification` 필드 4종. ADR-058 §결정 5 self-application — Amendment 시 sunset_justification 의무 첫 발화.

### sunset_justification (ADR-058 §결정 5 정합)

최초 transitional 분류 + sunset 기준 신설 — 본 Amendment 1 이전 ADR-057 은 sunset 기준 부재 (frontmatter `is_transitional` 미선언 + 본문 `## 해소 기준` 섹션 부재). 본 Amendment 가 sunset criteria 를 제공함으로써 향후 amendment 의 ratchet anti-pattern visibility 발화 채널이 처음 열린다. **기존 정책 (결정 1·2·3) 본문 변경 0건** — 종료 조건만 declaration form 으로 명시.

### ADR-058 self-application 검증 (본 Amendment 가 첫 사례)

- §결정 1 (transitional 분류 frontmatter 의무) → AC-1 충족 (`is_transitional: true`)
- §결정 2 (`## 해소 기준` 본문 섹션 의무) → AC-2 충족 (위치 invariant 정합)
- §결정 3 (3-tuple metric/who/how 정량 명시 + 모달 어휘 금지) → AC-3 충족 (sunset gate 2종 모두 3-tuple 정량 명시)
- §결정 5 (Amendment 시 sunset_justification 의무) → AC-4 충족 (frontmatter amendment_log row + 본문 Amendment 1 섹션 모두 명시)
- §결정 6 (ADR-058 자기 분류 `is_transitional: false`) → 본 Amendment 미해당 (ADR-058 은 source policy, 대상 아님 — self-defeat 회피 정합)
- §결정 7 (보안 ADR default permanent) → 본 Amendment 미해당 (ADR-057 = governance / Team & Process 계열)
- §결정 8 (DesignReview lane 임시 운영 문구 — manual gate, CFP-B CI lint 까지) → 본 Amendment 의 DesignReview lane 검증 trigger

## Amendment 2 (2026-05-11) — CFP-393 — KPI dashboard reference + measurement contract 강화

### 변경 사항

1. **KPI dashboard infrastructure 신설 (CFP-388 framework 첫 non-sunset application)**:
   - `scripts/measure-rate-limit-fallback.sh` — §14 Lane Evidence aggregator (wrapper `docs/stories/**` + internal-docs `<plugin-folder>/stories/**` 양쪽 scan, monthly window, idempotent + offline runnable).
   - `templates/github-workflows/rate-limit-fallback-kpi.yml` — monthly cron (`0 0 1 * *` UTC) + `workflow_dispatch:` (manual). aggregator 실행 → `docs/kpi/rate-limit-fallback.json` 갱신 (auto-PR, ADR-024 §결정 6 정합) → threshold 위반 시 Issue auto-open (label `codeforge-kpi-alert`).
   - `docs/kpi/rate-limit-fallback.json` — 신규 seed file. JSON schema = `{ measured_at, window_months: 3, sonnet_spawn_total, fallback_count, fallback_rate_percent, sample_size_sufficient, gate_status }`.
   - `docs/evidence-checks-registry.yaml` 두 번째 entry = `rate-limit-fallback-rate` (`current_tier: warning`, owner_adr = ADR-057, carrier_adr = ADR-060).

2. **Sunset gate 2 measurement contract 강화 (위 § "Sunset gate 2" 표 갱신)**:
   - **분모 명시**: Sonnet 잔류 agent 5종 (ADR-057 §결정 3 + ADR-042 Amendment 4 SSOT — DeveloperAgent · BackendDeveloperAgent · FrontendDeveloperAgent · IntegrationTestAgent · StatefulTestAgent) 의 §14 row spawn 카운트.
   - **분자 명시**: §14 `transcript` 필드의 `[rate-limit-fallback:sonnet→opus]` 태그 발화 row 카운트.
   - **측정 단위 명시**: calendar month UTC, half-open interval `[month-N-start, month-N+1-start)`.
   - **window 명시**: 3 month rolling.
   - **sample size sufficient sentinel**: 월간 분모 < 50 = `sample_size_sufficient: false` + `gate_status: sample_insufficient` + Issue auto-open 보류 (false alert 차단).

3. **CLAUDE.md "Sonnet subagent rate-limit → Opus fallback (ADR-057)" 섹션에 KPI dashboard reference 1줄 append**: link 추가만, 기존 정책 본문 변경 0건. ADR-053 재구동 trigger (safety direction — 모호 시 강제 측 분류, CFP-389 CL-3 prior art 정합) + ADR-037 MINOR bump (templates/github-workflows/** 신규 file) → marketplace sync (ADR-016) + consumer install + drift check 자동 발화 (재구동 prerequisite 절차).

### 기존 정책 변경 0건 (CFP-393 chief author 확인)

본 Amendment 2 는 measurement contract path + KPI dashboard infrastructure 만 추가. **결정 1 (Orchestrator Opus 필수화) / 결정 2 (Sonnet → Opus fallback max 1회) / 결정 3 (ADR-042 Amendment 4 6 agent 상향) 본문 변경 0건**. Amendment 1 의 sunset gate declaration 을 Amendment 2 가 mechanical realization 함 — sunset criteria 자체 (≥ 50 spawn / 3개월 / < 1%) 변경 0건. 측정 시작 시점만 본 Amendment 2 merge 이후로 명시화.

### ADR-058 self-application 검증 (Amendment 2)

- §결정 1 (transitional 분류 frontmatter 의무) → Amendment 1 충족 유지 (`is_transitional: true`).
- §결정 2 (`## 해소 기준` 본문 섹션 의무) → Amendment 1 충족 유지 + Amendment 2 가 sunset gate 2 표만 갱신 (위치 invariant 정합 — "결과" 직후 / "관련 파일" 직전).
- §결정 3 (3-tuple metric/who/how 정량 명시 + 모달 어휘 금지) → Amendment 2 갱신된 sunset gate 2 표가 3-tuple 강화 (분모 / 분자 / sample sentinel / window / unit 정량 명시). 모달 어휘 1차 사전 4 표현 ("안정화되면" / "임시" / "한시적" / "until further notice") 발화 0건 — `scripts/check-adr-sunset-criteria.sh` (CFP-389 lint) 통과 의무.
- §결정 5 (Amendment 시 sunset_justification 의무) → frontmatter amendment_log row + 본 단락 모두 충족.
- §결정 7 (보안 ADR default permanent) → 본 Amendment 미해당 (ADR-057 = governance / Team & Process 계열).

### ADR-060 §결정 12 cross-ref (framework 첫 non-sunset application)

ADR-060 §결정 12 = "CFP-C 잠정 = ADR-057 amendment + KPI dashboard — 본 framework 위에서 운영, 첫 적용 사례". 본 Amendment 2 = 해당 carry 의 정식 실현:
- evidence-checks-registry.yaml 두 번째 entry append (`rate-limit-fallback-rate`, `current_tier: warning`).
- evidence-check-registry-v1 schema 변경 0건 (FeasibilityAgent + DataMigrationArch 검증 — schema generality 1차 검증 PASS).
- framework 의 runtime metric pattern 1차 검증 완료 (기존 첫 entry `adr-sunset-criteria` = static lint pattern, 본 entry = runtime cron metric pattern).

### Drift 발견 (별도 follow-up 의무)

본 Amendment 2 작성 중 CodebaseMapper 검토에서 발견: CLAUDE.md "Sonnet subagent rate-limit → Opus fallback (ADR-057)" 섹션의 "적용 대상 Sonnet agent" 명단이 ADR-057 §결정 3 SSOT 와 불일치 — CLAUDE.md 가 ChangeImpactAgent · CodebaseMapperAgent · RefactorAgent 를 포함하나 ADR-057 §결정 3 Amendment 4 가 이 3개 agent 를 Opus 로 상향했다 (CFP-379). 본 Amendment 2 의 분모 정의는 ADR-057 §결정 3 SSOT (5종) verbatim 인용 — CLAUDE.md drift 정정은 본 Story scope 외, 별도 follow-up Issue 발의 의무 (Story §11 참조).

> **CFP-448 후속 (Amendment 3)**: 본 drift 가 CFP-448 의 동인 — Amendment 3 가 reverse direction (CLAUDE.md L127 8종 정합 회복) 으로 selective rollback (3 agent Opus → Sonnet). SSOT direction 은 CL-6 사용자 확정 결과 Option (i) = ADR-057 §결정 3 표 = SSOT.

## Amendment 3 (2026-05-12) — CFP-448 — §결정 3 selective rollback

### 변경 사항

1. **§결정 3 표 갱신 — 3 agent Opus → Sonnet 복귀** (위 § "결정 3" 표 SSOT — 이미 본 Amendment 에 의해 갱신됨):
   - **Sonnet rollback (3)**: CodebaseMapperAgent · RefactorAgent · DeveloperPLAgent
   - **Opus 유지 (3)**: FeasibilityAgent · ContinuityAgent · ChangeImpactAgent
2. **Sonnet 잔류 명단 = 8종** (5 기존 + 3 신규 rollback)
3. **SSOT 명시**: §결정 3 표 = SSOT, `CLAUDE.md` L127 mirror reference (CL-6 사용자 확정)
4. **Sunset gate 2 분모 5종 → 8종 갱신** (위 § "Sunset gate 2" 표 SSOT — 이미 본 Amendment 에 의해 갱신됨)
5. **mandate text 재정의 동시 산출물 의무 발화** (CodebaseMapperAgent / RefactorAgent 2종) — Sonnet rollback 결정 시 ADR-042 §결정 2 invariant 정합. 단순 model field downgrade 금지. **DeveloperPLAgent exclusion criterion**: DeveloperPLAgent 는 ADR-042 §결정 1 (b) "Implementation work — code write / refactor / test 구현" verbatim 정의로 mandate 이미 명확 (사용자 framing verbatim 적용: '아키텍트가 짜준 디자인 명세에서 제한되게 움직여 고도의 추론이 필요하지 않기 때문이다') — role 재정의 불필요. EC-5 universal mandate (§5.3) 와 align — exclusion 기준 = ADR-042 §결정 1 (b) implementation work 정의 직접 적용 + 사용자 framing verbatim 근거 시 면제
6. **Codex re-review 의무** (Story §5.3 EC-2 in-scope 승격 정합): mandate text 재정의 대상 2 agent (CodebaseMapper / Refactor) 의 재정의 후, Phase 2 PR open 전 또는 PR 안에 Codex re-review 발화 의무 — 재정의된 mandate 가 Sonnet 으로 cover 가능한지 검증 (CFP-379 finding 재발 차단). Codex re-review 결과 FIX verdict 시 rollback reject + Opus 복귀. **DeveloperPLAgent 는 사용자 framing 직접 적용 (코드 작성 agent = Sonnet, 고도 추론 불필요) → mandate text 재정의 면제 + Codex re-review 도 면제** (CFP-379 의 DeveloperPL Codex finding 'FIX 1차 진단 품질 개선' 은 ADR-042 §결정 1 (b) 정합 회귀로 거부 — 1차 진단은 Sonnet level 충분, 최종 판정은 ArchitectPLAgent (Opus) 가 수행. 단 Phase 2 CodeReview lane 일반 검토는 적용)

### 6 agent decision matrix (axis-A × axis-B × axis-C × Codex review × LangGraph precedent)

ArchitectPLAgent + 5 deputy (CodebaseMapper / Refactor / SecurityArch / OpRisk / TestContract) 산출물 통합 결과:

| Agent | axis-A (cost) | axis-B (mandate 깊이) | axis-C (CL-6 SSOT) | Codex review (CFP-379) | LangGraph precedent | 최종 |
|---|---|---|---|---|---|---|
| ChangeImpactAgent | Opus 필요 (axis-A 약함) | multi-source 가능성 (전체 코드베이스 영향 분석) | SSOT 정합 (Opus) — 사용자 framing verbatim ('changeimpact는 내가 보기에 opus가 괜찮아보인다') | finding 약함 (but Opus 유지 사용자 확정) | synthesizer-adjacent | **Opus 유지** |
| CodebaseMapperAgent | Sonnet 정합 (ADR-042 §결정 2 original) | single-mandate advocacy | mirror 갱신 후보 | symbol resolution finding — **mandate text 재정의 의무** | contributor tier | **Sonnet rollback + 재정의** |
| RefactorAgent | Sonnet 정합 (ADR-042 §결정 2 original) | single-mandate advocacy | mirror 갱신 후보 | advocacy 품질 finding — **mandate text 재정의 의무** | contributor tier | **Sonnet rollback + 재정의** |
| FeasibilityAgent | Opus tier (e) 필요 | multi-source synthesis (src+ADR) | SSOT 정합 (Opus) | architecture constraint 해석 finding 강함 | synthesizer-adjacent | **Opus 유지** |
| ContinuityAgent | Opus tier (f) 필요 | cross-Story pattern detection | SSOT 정합 (Opus) | pattern 판정 finding 강함 | synthesizer pattern | **Opus 유지** |
| DeveloperPLAgent | Sonnet sufficient (사용자 framing — '고도의 추론이 필요하지 않기 때문') | implementation work (ADR-042 §결정 1 (b) verbatim) — supervisor synthesis 가 아닌 아키텍트 명세 받아 제한된 implementation | SSOT swap (rollback) — 사용자 framing verbatim ('코드 작성 에이전트들이 sonnet이 되는게 낫지 않을까') | FIX 1차 진단 품질 finding — **거부 (1차 진단은 Sonnet level 충분, 최종 판정 ArchitectPL Opus)** | contributor tier (implementation lane) | **Sonnet rollback** |

**EC-9 tie-break 적용** (axis-A vs axis-B 충돌, CodebaseMapper + Refactor): axis-A 1차 우선 → rollback PASS + axis-B conditional constraint = mandate text 재정의 산출물 동시 의무 (EC-5 정합). **DeveloperPL** 은 tie-break 미해당 — axis-A / axis-B / axis-C 3 축 모두 Sonnet rollback 방향 일치 (사용자 framing verbatim + ADR-042 §결정 1 (b) 직접 정합).

### 기존 정책 변경 0건 (CFP-448 chief author 확인)

본 Amendment 3 은 §결정 3 표 + sunset gate 2 분모만 갱신. **결정 1 (Orchestrator Opus 필수화) 본문 변경 0건** + **결정 2 (Sonnet → Opus fallback max 1회) 본문 변경 0건** + **Amendment 1 sunset criteria 자체 변경 0건** + **Amendment 2 KPI infrastructure 변경 0건**. selective rollback 결과 분모만 8종으로 확대 → KPI dashboard 재계산 시 sample size 자연 회복 (data 변경 0건, schema 변경 0건 — backward-compat).

### ADR-058 self-application 검증 (Amendment 3)

- §결정 1 (transitional 분류 frontmatter 의무) → Amendment 1 충족 유지 (`is_transitional: true`).
- §결정 2 (`## 해소 기준` 본문 섹션 의무) → Amendment 1 충족 유지 (위치 invariant 정합 — "결과" 직후 / "관련 파일" 직전).
- §결정 3 (3-tuple metric/who/how 정량 명시 + 모달 어휘 금지) → 분모 갱신만 (5종 → 8종), 3-tuple structure 변경 0건. 모달 어휘 1차 사전 4 표현 ("안정화되면" / "임시" / "한시적" / "until further notice") 발화 0건 — `scripts/check-adr-sunset-criteria.sh` (CFP-389 lint) 통과 의무.
- §결정 5 (Amendment 시 sunset_justification 의무) → frontmatter amendment_log row + Amendment 3 sunset_justification 단락 (위) 모두 충족. **두 번째 self-application 사례** (Amendment 2 가 첫 사례).
- §결정 7 (보안 ADR default permanent) → 본 Amendment 미해당 (ADR-057 = governance / Team & Process 계열).

### Ratchet anti-pattern 회피 evidence (sunset_justification 본문 보강)

Amendment 1 sunset gate 1 ("Sonnet 잔류 agent 0건") 거리 = 5종 → 8종 (3종 증가). reverse direction 으로 보일 수 있으나:

1. **본 ADR 의 핵심 의도는 결정 1 (Orchestrator Opus mandate)** 으로 이미 달성됨 — Sonnet quota 소진 시 Orchestrator 차단 위험 = 구조적 해결. 결정 1 sunset 은 별도 cycle (Opus 도 quota 소진 위험 사라질 때).
2. **gate 1 ("Sonnet 잔류 0건") 자체는 idealized end-state** — 모든 agent role 이 Opus 가 필요할 정도로 진화한 시점. 본 Amendment 3 은 그 종점이 아직 멀다는 운영 evidence (Sonnet sufficient role 존재 — ADR-042 §결정 2 invariant + ADR-042 §결정 1 (b) implementation work 정합) 를 반영.
3. **Codex finding (CFP-379) 재발 차단** = mandate text 재정의 동시 산출물 의무 (CodebaseMapper + Refactor 2종). single tier downgrade 가 아니라 role definition 강화를 수반 = ratchet 회피 mechanism.
4. **사용자 framing (CFP-448) verbatim 직접 적용** = DeveloperPLAgent Sonnet rollback 의 1차 근거. 사용자 발화: "내가 보기엔 코드 작성 에이전트들이 sonnet이 되는게 낫지 않을까? 왜냐하면 아키텍트가 짜준 디자인 명세에서 제한되게 움직여 고도의 추론이 필요하지 않기 때문이다." → ADR-042 §결정 1 (b) "Implementation work — code write / refactor / test 구현" verbatim 정의 정합 회귀. CFP-379 의 DeveloperPL Codex finding "FIX 1차 진단 품질 개선" 은 거부 — 1차 진단은 Sonnet level 충분, 최종 판정은 ArchitectPLAgent (Opus) 가 수행 (ADR-042 §"왜 DeveloperPLAgent · DeveloperAgent · webapp preset 은 Sonnet 인가" verbatim).
5. **ADR-042 Amendment 5 cross-ref** (Amendment 3 atomic): agent model tier 정책 SSOT 가 본 Amendment 3 과 동시 갱신 — drift 차단 (ADR-063 atomic invariant 정합 cross-plugin scope, marketplace single sync ordering).

### Mirror 갱신 의무 (CL-6 사용자 확정)

본 Amendment 3 의 part of definition of done:

- (a) `CLAUDE.md` L127 (`Sonnet subagent rate-limit → Opus fallback (ADR-057)` 섹션) 의 "적용 대상 Sonnet agent" 명단을 본 §결정 3 표 의 8종 verbatim mirror 갱신
- (b) `CLAUDE.md` L127 본문에 **"본 명단은 ADR-057 §결정 3 표의 mirror reference 임. SSOT = ADR-057 §결정 3 표. drift 시 ADR 본문 우선"** 명시
- (c) `scripts/measure-rate-limit-fallback.sh` `SONNET_AGENTS` 배열 5종 → 8종 갱신 (3 신규 entry append + 주석 cross-ref Amendment 3)
- (d) `docs/evidence-checks-registry.yaml` `rate-limit-fallback-rate` entry — schema 변경 0건 (분모 정의는 ADR-057 §결정 3 reference 유지, data 자체는 cron 자동 재계산)
- (e) `docs/kpi/rate-limit-fallback.json` — schema 변경 0건, 다음 cron 시 자동 재집계

### Cross-ref (ADR-042 Amendment 5)

본 Amendment 3 = ADR-042 Amendment 5 동시 발의 (CFP-448 atomic). cross-ref:
- 본 ADR §결정 3 표 = SSOT (Sonnet 잔류 명단)
- ADR-042 §결정 1 표 + Amendment 5 row = SSOT (각 agent tier criteria 정합)
- 두 ADR 본문 모순 시 → CL-6 closure 정합: tier criteria 는 ADR-042, 잔류 명단은 ADR-057 (mandate 분리)

## Amendment 4 (2026-05-13) — CFP-264 — §결정 3 selective rollback 확장 (path B)

### 변경 사항

1. **§결정 3 표 갱신 — path B 정합 3 agent Opus → Sonnet 복귀** (위 § "결정 3" 표 SSOT — 이미 본 Amendment 에 의해 갱신됨):
   - **Sonnet rollback (3)**: FeasibilityAgent · ContinuityAgent · ChangeImpactAgent
   - **Opus 유지 (1)**: ResearcherAgent — ADR-046 §결정 4·5 본문 invariant 정합 (변경 0건)
2. **Sonnet 잔류 명단 = 11종** (8 기존 + 3 신규 path B rollback)
3. **SSOT 명시 변경 0건**: §결정 3 표 = SSOT, `CLAUDE.md` L127 mirror reference (CFP-448 CL-6 SSOT direction + CFP-264 CL-1 path B 확정 — 본 Amendment 4 가 명단만 확대)
4. **Sunset gate 2 분모 8종 → 11종 갱신** (위 § "Sunset gate 2" 표 SSOT — 이미 본 Amendment 에 의해 갱신됨)
5. **Mandate text 재정의 면제 (3 agent 모두)** — Sonnet rollback 결정 시 ADR-042 §결정 2 invariant 정합:
   - **FeasibilityAgent**: ADR-042 §결정 1 Sonnet (a) single-mandate advocacy 정합 verbatim — 구현 가능성 등급 + 경고 힌트, src+ADR read-only, supervisor synthesis 영역 아님 → mandate text 이미 명확, 재정의 불필요
   - **ContinuityAgent**: ADR-042 §결정 1 Sonnet (a) single-mandate advocacy 정합 — 본 lane 단일 Story 안 충돌/중복/의존 분류 (cross-Story pattern detection 영역 = PMOAgent Opus 유지, 본 agent 영역 외) → mandate text 이미 명확
   - **ChangeImpactAgent**: ADR-042 §결정 1 Sonnet (a) single-mandate advocacy 정합 — single-Story DELTA mapping (AS-IS → DELTA, src/** read-only) → mandate text 이미 명확
6. **Codex re-review 면제 (3 agent 모두)** — path B 채택 정합 (Codex proactive check touchpoint #4 가 Researcher Sonnet 다운 reject + 나머지 3 agent 의 Sonnet 다운은 mandate text 보존 + ADR-042 §결정 1 Sonnet (a) 정합) → CFP-379 Codex finding 대상 영역 외

### Path B 결정 framework (Codex proactive check touchpoint #4 발견)

본 Story 의 PL 권장 = Option B (사용자 framing verbatim 직접 적용 + Researcher 포함 4 agent Sonnet 다운). Codex proactive check 가 3 finding 발화:

| Finding | severity | 내용 | 처리 |
|---|---|---|---|
| Scope finding 1 | discretionary | `scripts/measure-rate-limit-fallback.sh` `SONNET_AGENTS` 배열 atomic 동반 갱신 의무 | 본 Story scope 8건 산출물에 포함 (path B 정합) |
| Scope finding 2 | severity 정정 (F-4 P2 → P1) | ADR-058 §결정 5 sunset_justification 의무 — `is_transitional: true` 인 ADR (ADR-057) 만 적용. `is_transitional: false` 인 ADR-042 / ADR-046 = 의무 비해당 | 본 Amendment 4 = ADR-057 (`is_transitional: true`) → sunset_justification 의무 적용 (위 frontmatter row 본문). ADR-042 Amendment 6 = `is_transitional: false` → sunset_justification 의무 비해당 (cross-ref atomic 만 명시) |
| Recommendation finding | **divergence** | ADR-046 §결정 4 verbatim ('Sonnet 대수 불가') + §결정 5 동일 + §결과 §긍정 ('Sonnet 대수 가능성 제거') — Researcher Sonnet 다운 자체가 ADR 본문 핵심 정책 reject 영역. PL Option B (사용자 framing verbatim 직접 적용) 도 본 invariant 와 충돌 — Researcher mandate text 약화 회피 우선 | **사용자 CL-1 = path B 확정** — Researcher 제외, 3 agent (Feasibility / Continuity / ChangeImpact) 만 Sonnet 다운. ADR-046 변경 0건 (Researcher mandate boundaries / Opus tier rationale 본문 invariant 강한 보존) |

### Mirror 갱신 의무 (CFP-264 CL-1 사용자 확정 — path B)

본 Amendment 4 의 part of definition of done:

- (a) `CLAUDE.md` L127 (`Sonnet subagent rate-limit → Opus fallback (ADR-057)` 섹션) 의 "적용 대상 Sonnet agent" 명단을 본 §결정 3 표 의 11종 verbatim mirror 갱신 (8종 → 11종, 3 신규: FeasibilityAgent / ContinuityAgent / ChangeImpactAgent)
- (b) `CLAUDE.md` L127 본문의 SSOT 명시 ("본 명단은 ADR-057 §결정 3 표의 mirror reference 임") 보존 — CFP-448 Phase 2 에서 이미 추가, 본 Amendment 변경 0건
- (c) `scripts/measure-rate-limit-fallback.sh` `SONNET_AGENTS` 배열 8종 → 11종 갱신 (3 신규 entry append + 주석 cross-ref Amendment 4)
- (d) `docs/evidence-checks-registry.yaml` `rate-limit-fallback-rate` entry — schema 변경 0건 (분모 정의는 ADR-057 §결정 3 reference 유지, data 자체는 cron 자동 재계산)
- (e) `docs/kpi/rate-limit-fallback.json` — schema 변경 0건, 다음 cron 시 자동 재집계

### 기존 정책 변경 0건 (CFP-264 chief author 확인)

본 Amendment 4 는 §결정 3 표 + sunset gate 2 분모만 갱신. **결정 1 (Orchestrator Opus 필수화) 본문 변경 0건** + **결정 2 (Sonnet → Opus fallback max 1회) 본문 변경 0건** + **Amendment 1 sunset criteria 자체 변경 0건** + **Amendment 2 KPI infrastructure 변경 0건** + **Amendment 3 sibling 측 변경 0건 (CodebaseMapper / Refactor mandate text 재정의 정합 보존)**. selective rollback path B 결과 분모만 11종으로 확대 → KPI dashboard 재계산 시 sample size 자연 회복 (data 변경 0건, schema 변경 0건 — backward-compat).

### ADR-058 self-application 검증 (Amendment 4)

- §결정 1 (transitional 분류 frontmatter 의무) → Amendment 1 충족 유지 (`is_transitional: true`).
- §결정 2 (`## 해소 기준` 본문 섹션 의무) → Amendment 1 충족 유지 (위치 invariant 정합 — "결과" 직후 / "관련 파일" 직전).
- §결정 3 (3-tuple metric/who/how 정량 명시 + 모달 어휘 금지) → 분모 갱신만 (8종 → 11종), 3-tuple structure 변경 0건. 모달 어휘 1차 사전 4 표현 ("안정화되면" / "임시" / "한시적" / "until further notice") 발화 0건 — `scripts/check-adr-sunset-criteria.sh` (CFP-389 lint) 통과 의무.
- §결정 5 (Amendment 시 sunset_justification 의무) → frontmatter amendment_log row + Amendment 4 sunset_justification 단락 (위) 모두 충족. **세 번째 self-application 사례** (Amendment 2 첫 사례 / Amendment 3 두 번째 사례 prior art 정합).
- §결정 7 (보안 ADR default permanent) → 본 Amendment 미해당 (ADR-057 = governance / Team & Process 계열).

### Cross-ref (ADR-042 Amendment 6 + ADR-046 변경 0건)

본 Amendment 4 = ADR-042 Amendment 6 동시 발의 (CFP-264 atomic). cross-ref:
- 본 ADR §결정 3 표 = SSOT (Sonnet 잔류 명단)
- ADR-042 §결정 1 표 + Amendment 6 row = SSOT (각 agent tier criteria 정합 — 3 신규 Sonnet 분류 명시)
- ADR-046 = 변경 0건 (Researcher mandate boundaries / Opus tier rationale 본문 invariant 강한 보존, path B 정합 invariant)
- 두 ADR 본문 모순 시 → mandate 분리: tier criteria 는 ADR-042, 잔류 명단은 ADR-057 (CFP-448 prior art 정합)

## 관련 파일

- `CLAUDE.md` — Orchestrator 모델 필수 확인 + Sonnet→Opus fallback 정책 섹션 (CFP-393 Amendment 2 = KPI dashboard link 1줄 append, CFP-264 Amendment 4 = mirror 명단 8종 → 11종 갱신)
- `docs/orchestrator-playbook.md` — §3.0.12 rate-limit fallback 절차
- `docs/adr/ADR-042-agent-model-selection-policy.md` — Amendment 4 (본 ADR로 상향된 6 agent 명시) / Amendment 5 (CFP-448 selective rollback) / Amendment 6 (CFP-264 path B 정합 cross-ref)
- `docs/adr/ADR-046-researcher-role-redefinition.md` — Researcher Opus tier rationale invariant (path B 정합 변경 0건)
- `docs/adr/ADR-058-adr-sunset-criteria-mandate.md` — Amendment 2 / 3 / 4 sunset_justification self-application source
- `docs/adr/ADR-060-evidence-enforceable-promotion-framework.md` — Amendment 2 가 §결정 12 (CFP-C carrier) carry — framework 첫 non-sunset application
- `scripts/measure-rate-limit-fallback.sh` — Amendment 2 신설 (KPI aggregator, CFP-393) / Amendment 3 SONNET_AGENTS 5종 → 8종 (CFP-448) / Amendment 4 SONNET_AGENTS 8종 → 11종 (CFP-264)
- `templates/github-workflows/rate-limit-fallback-kpi.yml` — Amendment 2 신설 (monthly cron + threshold alert, CFP-393)
- `docs/kpi/rate-limit-fallback.json` — Amendment 2 신설 (KPI dashboard data SSOT, CFP-393)
- `docs/evidence-checks-registry.yaml` — Amendment 2 가 두 번째 entry `rate-limit-fallback-rate` append (CFP-393)
- `plugin-codeforge-requirements/agents/RequirementsPLAgent.md` — model: claude-opus-4-7
- `plugin-codeforge-requirements/agents/DomainAgent.md` — model: claude-opus-4-7
- `plugin-codeforge-requirements/agents/RequirementsAnalystAgent.md` — model: claude-opus-4-7
- `plugin-codeforge-requirements/agents/ResearcherAgent.md` — model: claude-opus-4-7 (**Amendment 4 Opus 유지** — ADR-046 §결정 4·5 본문 invariant 정합, path B Codex proactive check 권장 + 사용자 CL-1 확정)
- `plugin-codeforge-requirements/agents/ChangeImpactAgent.md` — model: claude-sonnet-4-6 (**Amendment 4 rollback** — CFP-448 wave 에서 이미 sibling 측 Sonnet, SSOT drift 정합 회복)
- `plugin-codeforge-requirements/agents/FeasibilityAgent.md` — model: claude-sonnet-4-6 (**Amendment 4 rollback** — ADR-042 §결정 1 Sonnet (a) single-mandate advocacy 정합, mandate text 변경 0건)
- `plugin-codeforge-requirements/agents/ContinuityAgent.md` — model: claude-sonnet-4-6 (**Amendment 4 rollback** — ADR-042 §결정 1 Sonnet (a) single-mandate advocacy 정합, mandate text 변경 0건)
- `plugin-codeforge-design/agents/CodebaseMapperAgent.md` — model: claude-sonnet-4-6 (**Amendment 3 rollback + mandate text 재정의 의무**)
- `plugin-codeforge-design/agents/RefactorAgent.md` — model: claude-sonnet-4-6 (**Amendment 3 rollback + mandate text 재정의 의무**)
- `plugin-codeforge-develop/agents/DeveloperPLAgent.md` — model: claude-sonnet-4-6 (**Amendment 3 rollback** — 사용자 framing verbatim + ADR-042 §결정 1 (b) implementation work 정합 회귀)
