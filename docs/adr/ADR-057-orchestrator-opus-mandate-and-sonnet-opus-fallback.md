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
related_stories:
  - CFP-379
  - CFP-392
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

| 항목 | 내용 |
|---|---|
| **metric** | 월 50회 이상 Sonnet subagent spawn 발생 환경에서 3개월 연속 rate-limit fallback 발생률 < 1%. 분자 = `[rate-limit-fallback:sonnet→opus]` 태그 발화 건수 / 분모 = 월간 Sonnet subagent spawn 총 건수. minimum sample size gate (월 < 50 spawn 환경 = 측정 데이터 부족, gate 발화 보류 — zero division 회피). |
| **who** | GitOpsAgent (KPI dashboard aggregator — CFP-393 Story-2 구현 예정) + Orchestrator (월간 §14 Lane Evidence aggregation self-report) |
| **how** | §14 Lane Evidence `[rate-limit-fallback:sonnet→opus]` 태그 발화 카운트 + 월간 Sonnet spawn 총량 카운트 → `scripts/measure-rate-limit-fallback.sh` (잠정, CFP-393 Story-2 carry) 가 dashboard 출력. 3개월 rolling window 누적. 미달 시 본 §결정 2 archive 의무 (별도 carrier Amendment 로 sunset_justification 명시). |

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

## 관련 파일

- `CLAUDE.md` — Orchestrator 모델 필수 확인 + Sonnet→Opus fallback 정책 섹션
- `docs/orchestrator-playbook.md` — §3.0.12 rate-limit fallback 절차
- `docs/adr/ADR-042-agent-model-selection-policy.md` — Amendment 4 (본 ADR로 상향된 6 agent 명시)
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
