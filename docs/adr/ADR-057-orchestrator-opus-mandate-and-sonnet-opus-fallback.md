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
  - by: "CFP-1845"
    date: "2026-05-30"
    scope: "Amendment 4 — §결정 1 (Orchestrator 모델 필수) 버전 핀 claude-opus-4-7 → 별칭 opus 전환 (항상 최신 Opus tier 지칭, 현재 4.8). 버전 릴리스마다 일괄 변경 chore 제거 + 자동 추적. CLAUDE.md 세션 개시 체크리스트 mirror 동시 갱신. 결정 2 (fallback) · 결정 3 (tier 할당) 본문 변경 0건. 관련 파일 목록(line 292~)의 cross-repo agent model 표기는 follow-up cross-repo PR 에서 동기 갱신 (현 시점 실제 파일값 보존). ADR-042 Amendment 12 sibling atomic."
    sunset_justification: "별칭 전환은 §결정 1 normative 강도 약화가 아니라 표기 방식 변경 — Orchestrator = Opus **tier** 필수 invariant 불변, 버전 핀(claude-opus-4-7)만 별칭(opus, 항상 최신 Opus)으로 전환. sunset gate 1 (Sonnet 잔류 agent 0건) + gate 2 (fallback rate < 1%) measurement contract 변경 0건 — 분모/분자/window/sample sentinel 모두 그대로. 별칭 전환은 ratchet 무관 (scope/강도 불변, ADR-058 §결정 5 정합) — 미래 버전 bump 자동 추적으로 유지보수 chore 제거가 유일 효과. 원의도(Sonnet quota 소진 시 Orchestrator 차단 회피)는 정확 버전이 아니라 Opus tier 보장으로 충족되므로 별칭으로 충분. 사용자 directive 2026-05-30 KST verbatim: 'opus, sonnet, haiku 모두 최신 버전으로 지칭하도록 해'. ADR-042 Amendment 12 와 atomic sibling."
related_stories:
  - CFP-379
  - CFP-392
  - CFP-393
  - CFP-448
  - CFP-1845
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

codeforge를 사용하는 모든 Claude Code 세션에서 Orchestrator 모델은 **별칭 `opus` (항상 최신 Opus tier — 현재 4.8) 필수**. CLAUDE.md 세션 개시 의무 체크리스트에 강제 추가. Consumer overlay로 축소 불가.

> **Amendment 4 (2026-05-30, CFP-1845)**: 버전 핀 `claude-opus-4-7` → 별칭 `opus` 전환. 본 §결정의 normative 강도 불변 — **Orchestrator = Opus tier 필수** invariant 그대로, 버전 표기만 별칭화(항상 최신 Opus 자동 추적). 원의도(Sonnet quota 소진 시 Orchestrator 차단 회피)는 정확 버전이 아니라 Opus **tier** 보장으로 충족되므로 별칭으로 충분. ADR-042 Amendment 12 와 atomic sibling.

근거: Orchestrator가 Opus로 실행되면 Sonnet quota 소진이 Orchestrator를 차단하지 않음. Subagent의 Sonnet spawn 실패는 Orchestrator(Opus)가 감지하고 Opus fallback으로 재시도 가능.

CLAUDE.md 세션 개시 의무 체크리스트 업데이트는 CFP-379 S2 Story에서 수행한다.

### 결정 2: Sonnet subagent rate-limit → Opus fallback (max 1회)

Orchestrator가 Sonnet 모델 subagent spawn 시 rate-limit 에러를 수신하면:

1. 동일 입력 패킷으로 `model: opus` 재spawn (1회 한정)
2. 재spawn 성공 시 정상 진행 — §14 Lane Evidence에 `[rate-limit-fallback:sonnet→opus]` 태그 추가
3. Opus도 실패 시 사용자에게 rate-limit 상황 알림 후 대기 (자동 재시도 금지)

판별 기준: Agent tool result에 "rate limit", "quota exceeded", "429" 포함 시 rate-limit로 분류. task failure(agent 로직 오류)와 혼동하지 않도록 에러 메시지 패턴 확인 필수.

이 정책은 orchestrator-playbook.md §3 lane spawn 절차에 명문화한다.

### 결정 3: ADR-042 Amendment 4 + Amendment 5 적용 (selective tier 할당 — Amendment 3 갱신)

본 ADR 이 ADR-042 Amendment 4 (carry) + Amendment 5 (CFP-448 Amendment 3 cross-ref) 를 carry. 최종 tier 할당 (**Amendment 3 갱신 후 SSOT** — selective rollback 결과):

| Agent | 최종 tier | 비고 |
|---|---|---|
| FeasibilityAgent | **Opus 유지** | OPUS (e) architecture constraint 해석 — multi-source synthesis (src + ADR) |
| ContinuityAgent | **Opus 유지** | OPUS (f) cross-story/ADR 패턴 판정 — PMOAgent 와 유사 mandate |
| ChangeImpactAgent | **Opus 유지** | OPUS (a) 단일 축이나 전체 코드베이스 영향 분석 — 사용자 framing (CFP-448) verbatim 적용: 'changeimpact는 내가 보기에 opus가 괜찮아보인다'. axis-A 약함 (Opus 필요) + multi-source 가능성 명시 |
| CodebaseMapperAgent | **Sonnet (Amendment 3 rollback) + mandate text 재정의 의무** | ADR-042 §결정 2 original 분류 정합 (single-mandate advocacy). Codex review (CFP-379) symbol resolution 정확도 finding 은 mandate text 재정의 동시 산출물로 해소 — 단순 model field downgrade 금지 |
| RefactorAgent | **Sonnet (Amendment 3 rollback) + mandate text 재정의 의무** | ADR-042 §결정 2 original 분류 정합 (single-mandate advocacy). Codex review (CFP-379) advocacy 품질 finding 은 mandate text 재정의 동시 산출물로 해소 |
| DeveloperPLAgent | **Sonnet (Amendment 3 rollback)** | ADR-042 §결정 1 (b) "Implementation work — code write / refactor / test 구현" verbatim 정합 회귀. 사용자 framing (CFP-448) verbatim: '코드 작성 에이전트들이 sonnet이 되는게 낫지 않을까? 왜냐하면 아키텍트가 짜준 디자인 명세에서 제한되게 움직여 고도의 추론이 필요하지 않기 때문이다' — mandate 이미 명확, 재정의 불필요 + Codex re-review 면제 |

**Sonnet 잔류 + fallback 적용 대상 (Amendment 3 후 8종)** — ADR-057 §결정 3 = SSOT, CLAUDE.md L127 = mirror reference:
1. DeveloperAgent (codeforge-develop)
2. BackendDeveloperAgent (webapp preset)
3. FrontendDeveloperAgent (webapp preset)
4. IntegrationTestAgent (codeforge-test)
5. StatefulTestAgent (codeforge-test)
6. DeveloperPLAgent (codeforge-develop) — **Amendment 3 신규**
7. CodebaseMapperAgent (codeforge-design) — **Amendment 3 신규**
8. RefactorAgent (codeforge-design) — **Amendment 3 신규**

> **SSOT 명시 (CFP-448 CL-6 사용자 확정)**: 본 §결정 3 표 가 Sonnet 잔류 agent 명단의 단일 source of truth 다. `CLAUDE.md` "Sonnet subagent rate-limit → Opus fallback (ADR-057)" 섹션의 명단은 본 표 의 mirror reference 임. drift 시 본 ADR 표 우선. mirror 갱신 의무 = 본 ADR Amendment 의 part of definition of done.

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

본 ADR 은 `is_transitional: true` (안전망 / fallback policy carrier — 영구 정책 아님). 아래 sunset gate 2종은 결정 1·결정 2 별도 독립 발화 (한 gate 만 충족 시 해당 결정만 부분 archive, 둘 다 충족 시 ADR 전체 Accepted → Superseded 전이). ADR-058 §결정 3 정합 — 각 gate 별도 측정성 3-tuple (metric / who / how) 정량 명시.

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
| **metric** | 월 50회 이상 Sonnet subagent spawn 발생 환경에서 3개월 연속 rate-limit fallback 발생률 < 1%. 분자 = §14 Lane Evidence `transcript` 필드의 `[rate-limit-fallback:sonnet→opus]` 태그 발화 건수 / 분모 = 월간 Sonnet 잔류 agent **8종 (Amendment 3 후 SSOT — DeveloperAgent · BackendDeveloperAgent · FrontendDeveloperAgent · IntegrationTestAgent · StatefulTestAgent · CodebaseMapperAgent · RefactorAgent · DeveloperPLAgent)** 의 spawn row 카운트. 측정 단위 = calendar month UTC (half-open `[month-N-start, month-N+1-start)`). minimum sample size gate (월 < 50 spawn 환경 = `sample_size_sufficient: false`, gate 발화 보류 — zero division 회피 + 거짓 PASS/FAIL 신호 차단). **Amendment 3 (CFP-448) 효과: 분모 5종 → 8종 확대 → KPI sample size 자연 회복 (CFP-393 §11 follow-up #1 mitigation)**. |
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
2. **본문 `## 해소 기준` 섹션 신설**: 위 섹션 — 결정 1 · 결정 2 별도 측정성 3-tuple (metric / who / how) + 부분 sunset 처리 절차. ADR-058 §결정 2 self-application — 위치 invariant ("결과" 직후 / "관련 파일" 직전) 정합.
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

ArchitectPLAgent + 5 SubAgent (CodebaseMapper / Refactor / SecurityArch / OpRisk / TestContract) 산출물 통합 결과:

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

## Amendment 4 (2026-05-30) — CFP-1845 — §결정 1 버전 핀 → 별칭 전환

### 변경 사항

1. **§결정 1 갱신**: Orchestrator 모델 필수 표기 `claude-opus-4-7` → 별칭 `opus` (항상 최신 Opus tier — 현재 4.8). normative 강도(Opus tier 필수) 불변, 버전 표기 방식만 별칭화.
2. **CLAUDE.md 세션 개시 체크리스트 mirror 동시 갱신** (prerequisite (1) Orchestrator 모델 항목).
3. **결정 2 (fallback) · 결정 3 (tier 할당) 본문 변경 0건**.
4. **관련 파일 목록(아래)의 cross-repo agent model 표기는 보존** — 실제 별칭 전환은 follow-up cross-repo PR 에서 수행, 그 시점 ADR-057 관련 파일 목록도 동기 갱신.

### sunset_justification (ADR-058 §결정 5 정합)

별칭 전환은 §결정 1 normative 강도 약화가 아니라 표기 방식 변경 — Orchestrator = Opus **tier** 필수 invariant 불변, 버전 핀만 별칭(항상 최신 Opus)으로 전환. sunset gate 1·2 measurement contract 변경 0건. ratchet 무관 (scope/강도 불변) — 미래 버전 bump 자동 추적으로 유지보수 chore 제거가 유일 효과. 사용자 directive 2026-05-30 KST. ADR-042 Amendment 12 와 atomic sibling.

### 기존 정책 변경 0건

결정 1 (Opus tier mandate) invariant + 결정 2 (Sonnet → Opus fallback max 1회) + 결정 3 (tier 할당 표) + Amendment 1~3 sunset criteria 모두 본문 변경 0건. 버전 표기 방식만 별칭화.

## 관련 파일

- `CLAUDE.md` — Orchestrator 모델 필수 확인 + Sonnet→Opus fallback 정책 섹션 (CFP-393 Amendment 2 = KPI dashboard link 1줄 append)
- `docs/orchestrator-playbook.md` — §3.0.12 rate-limit fallback 절차
- `docs/adr/ADR-042-agent-model-selection-policy.md` — Amendment 4 (본 ADR로 상향된 6 agent 명시)
- `docs/adr/ADR-058-adr-sunset-criteria-mandate.md` — Amendment 2 sunset_justification self-application source (CFP-393)
- `docs/adr/ADR-060-evidence-enforceable-promotion-framework.md` — Amendment 2 가 §결정 12 (CFP-C carrier) carry — framework 첫 non-sunset application
- `scripts/measure-rate-limit-fallback.sh` — Amendment 2 신설 (KPI aggregator, CFP-393)
- `templates/github-workflows/rate-limit-fallback-kpi.yml` — Amendment 2 신설 (monthly cron + threshold alert, CFP-393)
- `docs/kpi/rate-limit-fallback.json` — Amendment 2 신설 (KPI dashboard data SSOT, CFP-393)
- `docs/evidence-checks-registry.yaml` — Amendment 2 가 두 번째 entry `rate-limit-fallback-rate` append (CFP-393)
- `plugin-codeforge-requirements/agents/RequirementsPLAgent.md` — model: claude-opus-4-7
- `plugin-codeforge-requirements/agents/DomainAgent.md` — model: claude-opus-4-7
- `plugin-codeforge-requirements/agents/RequirementsAnalystAgent.md` — model: claude-opus-4-7
- `plugin-codeforge-requirements/agents/ResearcherAgent.md` — model: claude-opus-4-7
- `plugin-codeforge-requirements/agents/ChangeImpactAgent.md` — model: claude-opus-4-7 (**Amendment 3 Opus 유지** — 사용자 framing verbatim)
- `plugin-codeforge-requirements/agents/FeasibilityAgent.md` — model: claude-opus-4-7
- `plugin-codeforge-requirements/agents/ContinuityAgent.md` — model: claude-opus-4-7
- `plugin-codeforge-design/agents/CodebaseMapperAgent.md` — model: claude-sonnet-4-6 (**Amendment 3 rollback + mandate text 재정의 의무**)
- `plugin-codeforge-design/agents/RefactorAgent.md` — model: claude-sonnet-4-6 (**Amendment 3 rollback + mandate text 재정의 의무**)
- `plugin-codeforge-develop/agents/DeveloperPLAgent.md` — model: claude-sonnet-4-6 (**Amendment 3 rollback** — 사용자 framing verbatim + ADR-042 §결정 1 (b) implementation work 정합 회귀)
