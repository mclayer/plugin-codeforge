---
adr_number: 141
title: 전 에이전트 opus(1M) 단일 tier 정책 — fable 폐기 + 3-tier 폐지
status: Accepted
category: governance
date: 2026-07-03
carrier_story: CFP-2560
supersedes:
  - ADR-117   # Fable 5 surgical 모델 tier — 본 ADR 이 fable 를 영구 폐기하며 supersede (본체 텍스트는 이력 보존)
is_transitional: false
related_adrs:
  - ADR-042   # Agent model selection policy — §결정 1 3-tier 표 supersede + §결정 3 신규 agent ADR 의무 승계 (Amd19)
  - ADR-057   # Orchestrator opus mandate + 비-opus fallback — §결정 1 흡수 / §결정 2 moot / §결정 4 dead (Amd6 → Superseded)
  - ADR-117   # Fable 5 surgical tier — 본 ADR carrier 로 Superseded (Amendment 3)
  - ADR-058   # ADR sunset criteria mandate — §결정 5 약화 evidence-gate (본 ADR = 3-tier 축소 방향)
  - ADR-064   # is_transitional:false governance 약화 symmetric evidence-gate
  - ADR-063   # marketplace atomic invariant — Phase 2 plugin bump mirrored-field sync
  - ADR-109   # 429 rate-limit mitigation — opus rate-limit 대응 소관 (ADR-057 §결정 2 moot 후 이관 명시)
  - ADR-127   # 정식 full-flow 비협상 + consumer overlay 확장-only (down-tier 불허 정합)
amendment_log: []
related_files:
  - CLAUDE.md
  - docs/consumer-guide.md
  - docs/orchestrator-playbook.md
  - docs/architecture/codeforge-family.md
---

# ADR-141: 전 에이전트 opus(1M) 단일 tier 정책 — fable 폐기 + 3-tier 폐지

## 상태

Accepted (2026-07-03 KST — CFP-2560 carrier). codeforge family 의 **전 에이전트 model tier 를 단일 `opus`(최신 Opus tier, 1M 컨텍스트 native)로 통일**하고, fable 을 완전 폐기하며, Opus/Sonnet/Haiku 3-tier 선택 기준을 폐지하는 governance SSOT.

본 ADR 은 다음 3개 ADR 을 carrier 로 재편한다:
- **ADR-117** (Fable 5 surgical tier) → **Superseded** (본체 텍스트 이력 보존, 삭제 아님).
- **ADR-042** (Agent model selection policy) → §결정 1 3-tier 표 supersede + Amd15/16/17 tier-flip dead + §결정 3 의무 승계 (Amendment 19).
- **ADR-057** (Orchestrator opus mandate + fallback) → §결정 1 흡수 / §결정 2 moot / §결정 4 dead → 전체 Superseded (Amendment 6).

## 컨텍스트

### 사용자 directive (트리거)

2026-07-03 KST, 사용자 directive verbatim: **"fable 안쓸거다. 전부 opus with 1M로 돌려라"**. 이는 CFP-2554 (2026-07-02, 하루 전 fable 원복)의 직접 revert 이자, 이번에는 **영구·전면**(sonnet/haiku 포함) + **1M 컨텍스트 통일**이다.

### fable↔opus 진동 부채 (환경 변화)

fable 과 opus 사이 model tier 가 **2일간 4회 진동**했다 (ContinuityAgent 실측 경고):
- CFP-2134 (2026-06-10) — fable surgical 11 채택 (ADR-117 §결정 1).
- CFP-2241 (2026-06-14) — 미 정부 제약으로 fable→opus 임시 override (ADR-117 Amendment 1, transitional).
- CFP-2554 (2026-07-02) — 제약 해제로 fable 원복 (ADR-117 Amendment 2).
- CFP-2560 (2026-07-03) — 본 ADR, fable 영구 폐기.

이 진동은 dormant 보존(정책은 두되 model alias 만 교체)이 매번 재활성 유혹(4번째 진동)을 남긴 구조에 기인한다. 사용자 directive 는 이 진동 부채를 **완전 청산**(fable 삭제 + 3-tier 기계 소멸)하라는 신호로 해석한다.

### 1M 컨텍스트 인코딩 사실 (요구사항리뷰 lane 확정 — F3)

요구사항리뷰 lane 이 확정한 인코딩 결론(source: 요구사항리뷰 lane, Claude Code v2.1.197 실측):
- Opus 4.8 은 Anthropic API / Max 플랜에서 **server-side 1M 컨텍스트를 native 로 제공**한다 — plain `model: opus` frontmatter 로 1M 이 활성화된다.
- `opus[1m]` suffix frontmatter 도 v2.1.197 에서 동작하나, Pro·credit-gated 플랜에서 hard-fail 위험이 있어(fail-soft 이식성 손실) plain `opus` 를 권장한다. `[1m]` fix-floor 는 미bisect(확인 불가) 이므로 floor 인용 근거로 쓰지 않는다.
- `CLAUDE_CODE_SUBAGENT_MODEL` env 는 **global 단일 override** 라 per-agent roster 를 붕괴시킨다 → 기각.

### 기존 3-tier 정책의 소멸 대상

- ADR-042 §결정 1 = Opus/Sonnet/Haiku 3-tier role-pattern 선택 기준.
- ADR-042 Amd15/16/17 = stakes-gated opus→sonnet tier-flip (ServiceDeveloper / InfraOpArch / DomainAgent).
- ADR-057 §결정 2 = sonnet rate-limit → opus fallback. §결정 4 = fable model-unavailable → opus fallback.
- ADR-117 = fable surgical 11 + Claude Code v2.1.170 floor.

전 에이전트가 opus 단일 tier 가 되면 위 machinery 는 모두 대상(sonnet/fable)이 0 이 되어 무의미해진다.

## 결정

### 결정 1: 전 에이전트 단일 tier = plain `model: opus` (1M native)

codeforge family 의 **모든 lane plugin 에이전트 frontmatter `model:` field = plain `opus`** 로 통일한다 (45 파일). Orchestrator 세션 모델도 `opus` 유지(결정 4). 단일 tier 이탈(특정 에이전트를 opus 아닌 tier 로 두기)은 **본 ADR amendment 를 의무**로 한다.

**인코딩 = plain `opus`** (요구사항리뷰 F3 근거):
- 근거: Opus 4.8 이 Anthropic API/Max 에서 1M native (server-side) 이므로 plain `opus` 로 1M 활성. `[1m]` suffix 는 Pro·credit-gated 플랜 hard-fail 위험(fail-soft 이식성)이라 기각. `CLAUDE_CODE_SUBAGENT_MODEL` env 는 global 단일 override 라 roster 붕괴 → 기각.
- **3rd-party provider pin (Bedrock/Vertex 소비자)**: Anthropic first-party 가 아닌 provider 를 쓰는 consumer 는 overlay 에 `ANTHROPIC_DEFAULT_OPUS_MODEL='claude-opus-4-8[1m]'` 를 pin 하도록 consumer-guide (Phase 2) 에 안내한다. wrapper self 및 first-party consumer 는 plain `opus` 로 충분.

45 파일 = agents 44 (field-bearing) + ProductionEvidenceDeputyAgent 1 (현 field 부재 → 결정 6 에서 `model: opus` 명시 추가). 실측 AS-IS(origin/main, `grep -rln "^model: <tier>" plugins/`): fable 11 / sonnet 15 / haiku 6 / opus 12 = 44 field-bearing + 1 field 부재.

### 결정 2: fable 완전 폐기 (dormant 아님)

`model: fable` alias 를 codeforge family 에서 **완전 폐기**한다 — surgical 표 / v2.1.170 floor / ADR-057 fallback / SSOT 문장을 모두 청산한다 (dormant 보존 아님). 근거 = fable↔opus 진동 부채(컨텍스트) — dormant 보존은 4번째 진동 유혹을 남긴다.

단 **ADR-117 본체 텍스트는 이력 보존**한다 (Superseded 마킹 + Amendment 3 append). frozen audit trail 원칙 상 과거 결정 시점 서술은 삭제하지 않는다 (Event Sourcing — ADR-042 Amd12 선례).

### 결정 3: 3-tier 선택 기준 폐지 + ADR-042 §결정 3 의무 승계

Opus/Sonnet/Haiku 3-tier role-pattern 선택 기준(ADR-042 §결정 1)을 **폐지**한다. 단일 tier = opus 이므로 role 별 tier 판정이 불요하다. ADR-042 Amd15(ServiceDev sonnet) / Amd16(InfraOpArch stakes-gated sonnet) / Amd17(DomainAgent financial-invariant-0 sonnet) tier-flip 은 대상 tier(sonnet)가 소멸하므로 **dead** 이다 (ADR-042 Amendment 19 로 dead 마킹).

**신규 agent 도입 의무 승계**: ADR-042 §결정 3("신규 agent 도입 / model 변경 시 ADR 의무")은 본 ADR 로 승계한다 — **신규 agent 는 `model: opus` default 이며, 단일 tier 이탈은 본 ADR amendment 의무**. (ADR-023 lane lifecycle + ADR-037 version bump 와 계속 연동.)

**ADR-042 §결정 2 invariant 의 지위 판정**: §결정 2 는 "Sonnet 으로 fully cover 가능 = role 재정의 시그널"이라는 원칙이었다. 본 ADR 하에서:
- **tier 신호로서는 폐지** — sonnet tier 자체가 없으므로 "Sonnet cover 가능성" 을 tier 선택 신호로 쓸 수 없다.
- **role-정합 원칙으로서는 잔존** — "에이전트 mandate 가 얕으면 role 을 재정의하라"는 설계 규율은 tier 와 무관하게 유효하다. 단, 그 결론이 더는 "model downgrade" 로 이어지지 않고 "mandate 명확화 / role 재편" 으로만 이어진다. 즉 §결정 2 는 tier-선택 함수에서 분리되어 **순수 role-설계 원칙**으로 잔존한다.

### 결정 4: Orchestrator opus mandate 흡수 (ADR-057 §결정 1 carrier 이전)

ADR-057 §결정 1(Orchestrator 세션 모델 = opus 필수, consumer overlay 축소 불가)을 본 ADR 로 흡수한다. CLAUDE.md 세션 개시 체크리스트의 "Orchestrator 모델 = opus" 근거는 유지되며 그 SSOT 만 ADR-141 로 이전한다. 전 에이전트 opus 단일 tier 이므로 Orchestrator opus 는 그 특수 사례가 아니라 정책 전체의 자연 귀결이 된다.

### 결정 5: 외부위임 래퍼 2종 포함 + 의식적 waiver 기록

사용자 "전부" 문언에 따라 외부위임 dispatch 래퍼 2종(RequirementsAnalystAgent · CodexReviewAgent, 현 haiku)도 `model: opus` 로 포함한다. 이는 ADR-042 §결정 1 (b) invariant("opus = 깊은 mandate 를 요구하는 역할") 에 대한 **의식적 waiver** 로 명시 기록한다:
- **uniformity > marginal cost** — 단일 tier 의 운영 단순화(tier 판정 machinery 소멸)가 이 2종의 marginal 비용 상향을 정당화한다.
- **거버넌스 약화 아님** — 이 2종은 비용 상향뿐이며, dispatch role(Claude 측은 prompt 조립·relay, 실 추론은 외부 GPT-5.4) 은 무변경. mandate 재정의 불요.
- **tier 실효 제한적** — 실 추론이 외부 GPT-5.4 이므로 Claude 측 model tier 의 산출물 품질 영향은 제한적임을 기록.

### 결정 6: CC floor + consumer overlay 규율 + ProductionEvidenceDeputy

- **Claude Code floor**: fable floor(v2.1.170)를 폐기하고 **Opus 4.8 인식 최소 버전 = v2.1.154** 로 갱신한다 (source: anthropics/claude-code CHANGELOG v2.1.154 — Opus 4.8 최초 릴리스 ("Opus 4.8 is here!"), 요구사항리뷰 lane 확정). consumer-guide "필수 의존성" 갱신 (Phase 2).
- **consumer overlay down-tier 불허**: overlay 는 opus 미만으로의 down-tier 를 불허한다 (보수 방향만 허용). ADR-127 §결정 6 확장-only 정합.
- **ProductionEvidenceDeputyAgent**: 현재 `model:` field 부재(상속) → **`model: opus` 명시 추가** (Phase 2). model-field 파일 수 44 → **45**.

### 결정 7: dead-path 처리 + Phase 2 실행 범위

**dead-path 처리 (실 파일 제거 0 — live-machinery 존치)**:
- `scripts/check-stakes-tier-gating.sh` (177줄) + `tests/scripts/test-check-stakes-tier-gating.sh` (435줄) = **존치**. env-driven 이고 frontmatter 무결합이라, 삭제 시 `docs/evidence-checks-registry.yaml` 의 `detect_command` 가 broken 된다. 본 ADR 텍스트로 "정책상 dead(전 에이전트 opus 라 flip 대상 0)" 만 판정.
- `docs/evidence-checks-registry.yaml` 2 entry (`stakes-tier-flip-evidence` ~L3267 / `rate-limit-fallback-rate` ~L55) = **존치 + dead 마킹** (Phase 2 에서 description 에 dead-policy 주석). entry 제거 시 `check-tier-downgrade-guard.sh` 가 `tier-downgrade-justification:` 마커를 요구하며 exit1 → CI red 위험 회피.
- `docs/domain-knowledge/concept/stakes-gated-model-tier-baseline.md` = **존치** (역사 참고).
- `rate-limit-fallback-kpi.yml` = 실측 NOT FOUND (registry 가 없는 파일을 참조) — 이 사실을 Phase 2 정리 항목으로 기록만.
- ADR-042 Amd16/17 = ADR 텍스트로 dead 판정만 (기계 정리 0).

**Phase 2 실행 범위 (구현 PR — 본 Phase 1 문서 PR 밖)**:
1. 45 frontmatter `model: opus` 통일 (fable 11 / sonnet 15 / haiku 6 → opus + ProductionEvidenceDeputy field 신설).
2. SSOT 3 문서 fable·stakes-gated·v2.1.170 잔재 청산 (CLAUDE.md L86·88 / consumer-guide L59 / playbook L513-521·547·564).
3. registry 2 entry dead 마킹 (description 주석).
4. plugin bump 9 (wrapper 6.64.0 / design 0.33.0 / develop 0.15.0 / requirements 0.12.0 / review 1.19.0 / pmo 0.5.0 / deploy 1.0.4 / test 1.3.5 / deploy-review 1.0.5).
5. CHANGELOG 갱신 + marketplace sync (ADR-063 atomic invariant).
6. CFP-2134 Epic(#2134 OPEN, fable 채택 Epic) close (실 close = Orchestrator).
7. **stale-mirror 정책 지시문 4개 층 청산** (아래 "stale-mirror 층" 참조).

**stale-mirror 층 (P1-1 — live 정책 지시문, ADR-141 단일 opus 와 정면모순)**:

앞의 "SSOT 3 문서"(CLAUDE.md / consumer-guide / playbook) 외에도, **live normative 지시문**(Sonnet tier 표 / opus fallback / 조건부 tier override / consumer-facing dead schema)이 4개 층에 분산돼 있다. 이들은 dead-path 처리(env-driven·frontmatter 무결합 live-machinery 존치)와 **다른 부류**다 — 리뷰어·소비자가 실제로 읽고 따르는 *지시* 이므로 존치 시 ADR-141 단일 opus 와 정면모순한 정책이 잔존한다. 따라서 **F5(SSOT 3 문서 청산) 동형의 처리 = 청산**(의식적 존치 아님). Phase 2 실행:

- **(a) lane-plugin CLAUDE.md 4파일** — `plugins/codeforge-deploy/CLAUDE.md`(DeployPL/Worker Sonnet 표 + ADR-057 opus fallback 문장) · `plugins/codeforge-deploy-review/CLAUDE.md`(DeployReviewWorker Sonnet 표) · `plugins/codeforge-design/CLAUDE.md`(ModuleArch/APIContractArch/Mapper/Refactor/Analyst 등 Sonnet tier 표) · `plugins/codeforge-test/CLAUDE.md`(IntegrationTestAgent Sonnet 표기). repo 정책상 lane plugin CLAUDE.md = "에이전트 상세 SSOT" → ADR-141(단일 opus)과 모순하는 normative 문장. Phase 2 = tier 열 opus 통일 + ADR-057 fallback 문장 청산. 동 4 lane 의 `docs/architecture/<plugin>.md` mirror(codeforge-deploy.md / codeforge-deploy-review.md / codeforge-test.md)도 동반 정정(architecture doc lane gate — ADR-078 interfaces 영역).
- **(b) agent frontmatter 주석 9파일** — `# rate-limit 시 Orchestrator가 model:opus로 fallback spawn — ADR-057` frontmatter 주석 (ADR-057 §결정2 moot 후 dead 인용). 실측(origin/main, `grep -rln "^# rate-limit 시 Orchestrator" plugins/ --include="*.md"`) = **9파일**: DeployPLAgent · DeployWorkerAgent · DeployReviewWorkerAgent · DeveloperAgent · ServiceDeveloperAgent · BackendDeveloperAgent · FrontendDeveloperAgent · IntegrationTestAgent · StatefulTestAgent. (spec 상 "12파일" 추정은 over-count — line-anchored 주석 정밀 실측 = 9. body prose 산발 ADR-057 인용은 별도 검출 규칙 = `grep -rln "ADR-057" plugins/ --include="*.md" | xargs grep -l "opus.*fallback\|rate.limit"` = 15파일, agent 9 + lane CLAUDE.md·architecture 6 중복). Phase 2 = 주석 제거 또는 "단일 opus tier — fallback 대상 없음(ADR-141)" 로 대체.
- **(c) 조건부 tier 지시문 3파일** — `plugins/codeforge-design/agents/InfraOperationalArchitectAgent.md`(frontmatter 주석 L5-9 low-stakes 4-AND `opts.model:sonnet` override + 본문 "low-stakes shape 표면" subsection, Amd16 dead) · `plugins/codeforge-requirements/agents/DomainAgent.md`(frontmatter 주석 L4-9 financial-invariant-0 sonnet + 본문 "financial-invariant-0 shape mandate 표면" 섹션, Amd17 dead) · `plugins/codeforge-develop/presets/backend-service/agents/ServiceDeveloperAgent.md`(`model: sonnet` frontmatter + "sonnet 구현자" description, Amd15 dead). Phase 2 = `model: opus` 통일(위 항목 1 45-frontmatter 와 교집합) + 조건부 override 지시문/mandate-표면 섹션 청산.
- **(d) `docs/project-config-schema.md`** — L287-323 `story_stakes` 조건부 tier config 블록 + L445-457 `story_stakes` 섹션 설명(dead mechanism 을 live consumer-facing schema 로 노출). Phase 2 = 블록 제거 또는 "ADR-141 로 폐지(전 에이전트 opus 단일 tier — stakes 조건부 tier 소멸)" dead-policy 주석.

## 근거 (Rationale)

### 약화-evidence 3축 (ADR-058 §결정 5 + ADR-064 §결정 7 — is_transitional:false governance 약화 evidence-gate)

비용 거버넌스(3-tier stakes-gating) 축소 = 약화 방향이므로 각 개정 ADR amendment_log row 에 `sunset_justification` 을 의무 기재한다. evidence 3축:

- **(a) 사용자 directive 명확 + 환경 변화** — directive verbatim("fable 안쓸거다. 전부 opus with 1M로 돌려라") 는 애매성 0. 환경 변화 = fable↔opus 2일 4진동 obsolescence(tier 진동 부채) — dormant 보존이 진동을 재생산하는 구조를 청산.
- **(b) 능력 상향 방향 + 운영 단순화** — opus ≥ sonnet/haiku reasoning depth (하향 아닌 상향). stakes-gated / fallback / floor machinery 소멸 = 운영 표면 대폭 축소.
- **(c) fable→opus 11종 = 비용 절반** — fable $10/$50 (input/output per MTok) = opus $5/$25 의 정확히 2배 (source: ADR-117 컨텍스트 실측 인용). 즉 surgical 11종은 오히려 **비용 절반**이다. sonnet/haiku 21+종의 상향 비용은 사용자 명시 수용.

### 채택/기각 옵션 대조

- **옵션 A (전 에이전트 opus 단일 tier) 채택** — 사용자 directive 직접 이행. 진동 부채 완전 청산(fable 삭제 + 3-tier 기계 소멸) + 운영 단순화 + surgical 11 비용 절반. sonnet/haiku 상향 비용은 사용자 수용.
- **옵션 B (현행 유지 — fable surgical + 3-tier) 기각** — 사용자 directive("fable 안쓸거다") 정면 위배. 진동 부채 존속.
- **옵션 C (부분 — fable 만 폐기, sonnet/haiku 3-tier 유지) 기각** — 사용자 "전부 opus" 문언 위배. 3-tier machinery(stakes-gating / rate-limit fallback / 재-audit) 존속으로 운영 단순화 이득 미실현.

## 결과

### 긍정
- model tier machinery 대폭 소멸 (surgical 표 / v2.1.170 floor / fable fallback / sonnet fallback / stakes-gating 3종 / 재-audit 규칙) → 운영·거버넌스 표면 축소.
- fable↔opus 진동 부채 완전 청산 (dormant 재활성 유혹 제거).
- 전 에이전트 1M 컨텍스트 native → 긴 컨텍스트 작업 일관성.
- surgical 11종(fable→opus) 비용 절반.

### 부정 (trade-off)
- sonnet/haiku 21+종 opus 상향 = 토큰 비용 증가 (사용자 명시 수용 — uniformity·1M > cost).
- 외부위임 래퍼 2종(dispatch-only) opus = marginal 비용 상향, tier 실효 제한적 (결정 5 waiver).
- opus rate-limit(429) 위험 재발 시 sonnet fallback 이 더는 없음 → **ADR-109 (429 mitigation)** 소관으로 이관 (ADR-057 §결정 2 moot 후 유일 대응 채널).

### 영향 경계 (블라스트)
- 45 agent frontmatter (fable 11 / sonnet 15 / haiku 6 / opus 12 + ProductionEvidenceDeputy field 신설).
- SSOT 3 문서 (CLAUDE.md / consumer-guide.md / orchestrator-playbook.md).
- stale-mirror 4 층 (P1-1, Phase 2 청산): lane-plugin CLAUDE.md 4 + agent frontmatter 주석 9 + 조건부 tier 지시문 3 + project-config-schema 1 (+ architecture doc mirror 3). §결정 7 "stale-mirror 층" 참조.
- ADR 4 (ADR-141 신규 + ADR-117 Superseded + ADR-042 Amd19 + ADR-057 Amd6→Superseded).
- registry 2 entry (dead 마킹, 존치).
- live-machinery 2 (check-stakes-tier-gating.sh + test, 존치).
- plugin bump 9 + CHANGELOG + marketplace sync.
- architecture doc 1 (codeforge-family.md tier 서술 갱신) + lane architecture mirror 3 (deploy/deploy-review/test — stale-mirror (a) 동반).

## 해소 기준

N/A — permanent policy. 본 ADR 은 전 에이전트 단일 tier 정책의 상시 기준으로 sunset 대상이 아니다. 단 아래 재산정 트리거 발생 시 본 ADR 을 amend 하여 tier 정책을 재산정한다 (ADR-117 동형):
- 모델 세대 전환 (차기 최강 모델 GA / Opus 가격 구조 변동 / 1M 컨텍스트 정책 변경).
- 사용자 directive 로 tier 다양화 재요구.

## 관련 파일

- `CLAUDE.md` — 세션 개시 체크리스트(Orchestrator opus) + "비-opus tier → Opus fallback" 섹션 (Phase 2 청산).
- `docs/consumer-guide.md` — 필수 의존성 CC floor(v2.1.170 → v2.1.154) + fable 문장 청산 + 3rd-party provider pin note (Phase 2).
- `docs/orchestrator-playbook.md` — §3.0.12 fallback + §3.0.12a stakes-gated 절차 (Phase 2 청산/dead 마킹).
- `docs/architecture/codeforge-family.md` — model-tier 서술 앵커 (본 Phase 1 갱신).
- `archive/adr/ADR-117-fable-5-surgical-model-tier.md` — Superseded (Amendment 3).
- `archive/adr/ADR-042-agent-model-selection-policy.md` — Amendment 19 (3-tier supersede + tier-flip dead + §결정 3 승계).
- `archive/adr/ADR-057-orchestrator-opus-mandate-and-sonnet-opus-fallback.md` — Amendment 6 (§결정 1 흡수 / §결정 2 moot / §결정 4 dead → Superseded).
- `docs/evidence-checks-registry.yaml` — 2 entry dead 마킹 (Phase 2, 존치).
- `scripts/check-stakes-tier-gating.sh` + `tests/scripts/test-check-stakes-tier-gating.sh` — 존치 (live-machinery, 정책 dead).
- 45 agent frontmatter (Phase 2 `model: opus` 통일).
