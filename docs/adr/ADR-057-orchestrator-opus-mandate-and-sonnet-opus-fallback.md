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
related_stories:
  - CFP-379
  - CFP-392
  - CFP-393
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

### 결정 3: ADR-042 Amendment 4 적용 (6 agent Opus 상향)

본 ADR이 ADR-042 Amendment 4를 carry. 상향 대상:

| Agent | 변경 | 비고 |
|---|---|---|
| FeasibilityAgent | Sonnet → Opus | OPUS (e) architecture constraint 해석 |
| ContinuityAgent | Sonnet → Opus | OPUS (e) cross-story/ADR 패턴 판정 |
| ChangeImpactAgent | Sonnet → Opus | OPUS (a) 단일 축이나 전체 코드베이스 영향 분석 |
| CodebaseMapperAgent | Sonnet → Opus | ADR-042 §결정2 역전 — symbol resolution 정확도 부족 확인 |
| RefactorAgent | Sonnet → Opus | ADR-042 §결정2 역전 — advocacy 품질 개선 필요 |
| DeveloperPLAgent | Sonnet → Opus | FIX 1차 원인 진단 품질 개선 |

Sonnet 유지 + fallback 적용 대상: DeveloperAgent · BackendDeveloperAgent · FrontendDeveloperAgent · IntegrationTestAgent · StatefulTestAgent (ADR-055 기준 tier 명시 없음 — Sonnet 유지, fallback 적용)

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
| **metric** | 월 50회 이상 Sonnet subagent spawn 발생 환경에서 3개월 연속 rate-limit fallback 발생률 < 1%. 분자 = §14 Lane Evidence `transcript` 필드의 `[rate-limit-fallback:sonnet→opus]` 태그 발화 건수 / 분모 = 월간 Sonnet 잔류 agent 5종 (ADR-057 §결정 3 + ADR-042 Amendment 4 SSOT — DeveloperAgent · BackendDeveloperAgent · FrontendDeveloperAgent · IntegrationTestAgent · StatefulTestAgent) 의 spawn row 카운트. 측정 단위 = calendar month UTC (half-open `[month-N-start, month-N+1-start)`). minimum sample size gate (월 < 50 spawn 환경 = `sample_size_sufficient: false`, gate 발화 보류 — zero division 회피 + 거짓 PASS/FAIL 신호 차단). |
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
- `plugin-codeforge-requirements/agents/ChangeImpactAgent.md` — model: claude-opus-4-7
- `plugin-codeforge-requirements/agents/FeasibilityAgent.md` — model: claude-opus-4-7
- `plugin-codeforge-requirements/agents/ContinuityAgent.md` — model: claude-opus-4-7
- `plugin-codeforge-design/agents/CodebaseMapperAgent.md` — model: claude-opus-4-7
- `plugin-codeforge-design/agents/RefactorAgent.md` — model: claude-opus-4-7
- `plugin-codeforge-develop/agents/DeveloperPLAgent.md` — model: claude-opus-4-7
