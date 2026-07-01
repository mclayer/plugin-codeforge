# Changelog

`codeforge-requirements` plugin 릴리스 이력.

버전 체계: [Semantic Versioning 2.0.0](https://semver.org/lang/ko/). v1.0 이전은 minor bump도 breaking 가능.

## [0.12.0] - 2026-07-02 — CFP-2554 fable surgical tier 원복 (MINOR)

### Changed

미 정부 제약 해제로 ADR-117 Amendment 1 임시 opus override 를 해제하고 surgical 에이전트를 `model: fable` 로 원복(ADR-117 Amendment 2).

- requirements lane surgical 1 에이전트 frontmatter `model: opus`(임시 CFP-2241) → `model: fable` 환원 + 임시 표식 코멘트 제거: `ResearcherAgent`.

#### Why

능력 손실 0(fable/opus thinking 프로파일 동형), 비용 축만 2배 재부담 — ADR-117 결정 1 정당화 역할(long-horizon 외부 지식 종합) 한정. 모델-tier 행동 변경(다음 세션부터 fable) = consumer 영향 → MINOR.

## [0.8.4] - 2026-06-15

### CFP-2249 — superpowers 의존 완전 제거 (PATCH)

Epic CFP-2249 (superpowers 의존 완전 제거, ADR-122 — supersede ADR-028) 의 lane 반영. 요구사항 lane 7 agent 의 `superpowers:*` skill 호출 / `docs/superpowers-integration.md` 참조를 codeforge native discipline 으로 교체. 필수 plugin 4→3 (superpowers 제거) 의 wrapper 정책 변경에 동반하는 lane catch-up. capability 추가/제거 0 (skill 위임 경로만 native 흡수) — PATCH.

#### Changed

- `agents/RequirementsPLAgent.md` · `agents/DomainAgent.md` · `agents/RequirementsAnalystAgent.md` · `agents/ChangeImpactAgent.md` · `agents/FeasibilityAgent.md` · `agents/ContinuityAgent.md` · `agents/codex-proactive-check.md` — `superpowers:*` 호출 / `superpowers-integration.md` 참조 제거 → codeforge native (ADR-122) 흡수. discipline = research-before-claims (ADR-119) 검증-후-단언 + codeforge native skill.

#### Why

ADR-122 — superpowers 외부 plugin 의존이 brainstorming / writing-plans / tdd / verification discipline 을 codeforge native 로 내재화하면서 불필요해짐. consumer breaking 0 (wrapper 가 동일 discipline 을 codeforge native skill 로 제공).

## [0.8.1] - 2026-06-12

### Changed (CFP-2178 — S6 lane repo archive 참조 sweep, PATCH)

- `overlay/hooks/session-start-deps-check.sh` 안내 URL — 구 lane repo (`mclayer/plugin-codeforge-requirements`) → wrapper 모노레포 앵커 (`mclayer/plugin-codeforge/tree/main/plugins/codeforge-requirements#dependencies`). 구 lane repo 8개 = 2026-06-12 GitHub archive (ADR-118 D1) — read-only repo 안내 차단.
- `CLAUDE.md` `story_issues` repo 좌표 — `mclayer/plugin-codeforge-requirements` → `mclayer/plugin-codeforge` (archive 후 read-only repo 에 issue 생성 지시 = 기능 파손 해소).

## [0.7.1] - 2026-05-30

### CFP-1845 follow-up — agent model 핀 → 별칭 전환 (PATCH)

[CFP-1845 follow-up] agent model 핀 → 별칭 전환 (opus/sonnet/haiku 항상 최신 지칭). frontmatter model field 8건. tier 분류 변경 0건 (표기 방식만, ratchet 약화 아님). wrapper #1846 / #1847 연계. marketplace sibling sync 동반.

#### Changed

- `agents/*.md` 8 파일 frontmatter `model:` field — pinned version (`claude-opus-4-7` / `claude-sonnet-4-6` / `claude-haiku-4-5-20251001`) → alias (`opus` / `sonnet` / `haiku`). 본문/description 의 과거 버전 서술 (frozen audit trail) 미변경.

## [0.7.0] - 2026-05-27

### CFP-1764 Story-3 — 3 agent prompt template 평이 번역 의무 directive 추가 (MINOR)

ADR-071 Amendment 8 (wrapper plugin-codeforge, Story-1 #1769 MERGED 2026-05-27 12:30:49 KST) horizontal axis 자매 carrier. 본 lane plugin 안 3 부속 작업자 (DomainAgent / ResearcherAgent / RequirementsAnalystAgent) prompt template 본문에 codename → 평이 어휘 평문 풀이 의무 directive 추가. 사용자 dialog turn paste 합성 영역 jargon leak 차단.

#### Added

- `agents/DomainAgent.md` — "출력 시 평이 어휘 의무 (ADR-071 §결정 19, Amendment 8 — CFP-1764)" section 신설 (Lookup SSOT = wrapper `docs/wording-dictionary.md` 카테고리 (c) 15 batch + Scope (In/Out) + 적용 예시 15-row 표). 본문 첫 사용 영역 self-application 1줄 추가 ("RequirementsPLAgent (요구사항 작업 영역 PL)").
- `agents/ResearcherAgent.md` — 동상 directive section 신설 + Cross-agent Signal 영역 self-application 1줄 ("DomainAgent 또는 RequirementsAnalyst (부속 작업자 동료)").
- `agents/RequirementsAnalystAgent.md` — 동상 directive section 신설 + codex exec prompt body 안 directive 명시 권장 추가 + Lookup SSOT 안 ratchet 평문 풀이 self-application ("ratchet extensibility (강화 방향 고정 확장)").
- `.claude-plugin/plugin.json` — version 0.6.0 → 0.7.0 MINOR. description CFP-1764 Story-3 entry append.

#### Why

ADR-071 §결정 19 (Amendment 8, Story-1 carrier) horizontal axis 자매 — agent burst output 의 원천 영역. 사용자 directive 2026-05-27 KST (mctrader-hub#517 4-turn 누적 redirect + confirm directive: "오케이 그렇게 escalation 하자. 그렇게 버전업되면 버전 업그레이드 통해 적용받는 식으로") wrapper canonical path 의무 적용. consumer overlay (`.claude/_overlay/`) 축소 불가 invariant 유지.

#### Compatibility

- canonical: wrapper `plugin-codeforge` (Amendment 8 ADR-071 + wording-dictionary 카테고리 (c) SSOT, Story-1 PR #1769 MERGED)
- sibling: codeforge-pmo (Story-3 PR sibling sync, 동일 MINOR)
- marketplace: 4 mirrored field (`name` / `version` / `description` / `author`) atomic sync 의무 (ADR-063 §결정 2 ordering)
- Effective date: marketplace sync PR merged + 본 PR merged + consumer `/plugins install` 후 (ADR-053 structural change restart 적용 영역)

## [0.6.0] - 2026-05-13

### CFP-510 — RequirementsPLAgent divergence detection 4 영역 확장 (MINOR)

wrapper plugin-codeforge ADR-052 Amendment 3 sibling sync. CFP-411 (Amendment 1) 의 semantic 3 criteria 에 **4번째 영역 = fact-check** 추가. PL self-evaluation 의무 = synthesis fact claim 영역 marker 5종 (`[verified]` / `[hypothesis]` / `[fact-check-pending]` / `[user-input]` / `[verification-out-of-scope: <사유>]`). MINOR bump (mandate text 영역 확장 — agent definition signature 영역).

#### Changed

- `agents/RequirementsPLAgent.md` — "Divergence detection 3 criteria" → "Divergence detection 4 영역 (3 semantic + 1 factual)" 단락 확장 + "PL self-evaluation 의무 — fact claim marker 5종" 단락 신설 + Debate-protocol-v1 dispatch divergence_type 분류 (semantic / factual + polyfill) 명시.
- `agents/codex-proactive-check.md` — "dispatch_mode: auto_on_divergence" 단락 divergence 4 영역 명시 + "Fact-check 영역 (ADR-052 Amendment 3 / CFP-510)" 단락 신설 (4 sub-criteria 검증 방법 표 + PL marker 5종 인지 의무).
- `.claude-plugin/plugin.json` — version 0.5.1 → 0.6.0 MINOR. description CFP-510 entry append.

#### Why

axis-A (mandate 영역 확장 — fact-check 영역 명시): semantic 3 criteria implicit 영역 → 4 영역 explicit normative anchor. axis-B (PL synthesis quality — marker 5종 forcing function): 가설 vs verified 영역 구분 의무 부재 → false negative 차단. axis-C (Codex worker mandate 정합): codex-proactive-check.md 가 RequirementsPLAgent marker 5종 cross-verify 의무 명시.

#### Compatibility

- canonical: wrapper `plugin-codeforge` 5.24.0 (PR Phase 1 sibling sync — ADR-010 §단계 절차 wrapper-first 정합)
- Effective date: 본 PR merged + marketplace sync PR merged + consumer `/plugins install` 후 (ADR-053 structural change restart 적용 영역)

## [0.5.1] - 2026-05-12

### CFP-448 — ChangeImpactAgent Opus → Sonnet rollback (PATCH)

ADR-057 Amendment 3 (wrapper plugin-codeforge PR #488 merged, 2026-05-12) selective rollback 의 sibling sync. CFP-379 (Amendment 4) 의 6 agent Opus 상향 중 3 agent (ChangeImpactAgent / CodebaseMapperAgent / RefactorAgent) Sonnet 복귀 — 본 lane plugin 은 ChangeImpactAgent 만 해당.

#### Changed

- `agents/ChangeImpactAgent.md` `model:` field `claude-opus-4-7` → `claude-sonnet-4-6`. mandate text 변경 0건 — ChangeImpactAgent 는 ADR-042 §결정 2 invariant 자연 정합 (AS-IS → DELTA structured mapping = single-source map, advocacy/synthesis pattern 아님). exclusion criterion 정합 (CFP-448 §5.3 EC-5 universal mandate align).
- `.claude-plugin/plugin.json` — version 0.5.0 → 0.5.1 PATCH (model field 단순 변경, mandate / contract / agent definition signature 영역 변경 0건). description CFP-448 entry append.

#### Why

axis-A (operational cost) — ADR-042 original Sonnet 분류 정합 회복 (CFP-379 → CFP-448 1 주일 운영 evidence). axis-B (mandate 깊이) — single-mandate structured output (advocacy/synthesis pattern 아님) 으로 Sonnet sufficient cover. axis-C (SSOT alignment) — CLAUDE.md L127 8종 정합 회복 (CL-6 사용자 확정 Option (i)).

#### Compatibility

- **Wire**: codeforge wrapper >= 5.22.1 (Phase 2 PR pair atomic — wrapper 5.22.1 + design 0.7.0 + 본 0.5.1 + Story §8 internal-docs).
- **Codex re-review**: 면제 — mandate text 변경 0건 (Story §5.3 EC-2 정합). 단순 model tier rollback.
- **ADR-053 재구동**: agent definition 변경 = 구조적 변경. consumer 측 `/plugins install codeforge-requirements@mclayer` 의무.

## [0.5.0] - 2026-05-11

### CFP-411 — Requirements lane Codex proactive check + semantic divergence debate (MINOR)

ADR-052 touchpoint #4 (RequirementsPLAgent §1~§6 완료 직후 Codex proactive check) 를 single-shot 검토에서 multi-round adversarial debate 로 격상. Story 1 (CFP-391) 의 `debate-protocol-v1` + ADR-059 + ADR-044 Amendment 1 `auto_on_divergence` 를 Requirements lane 에 transplant.

#### Added

- `agents/codex-proactive-check.md` — Codex worker entry 신설. `dispatch_mode: auto_on_divergence`. ADR-052 D2 touchpoint #4 spawn timing + debate-protocol-v1 dispatch 흐름 정의.

#### Changed

- `agents/RequirementsPLAgent.md` — 새 section "Codex Proactive Check + 의미적 divergence debate (touchpoint #4)" 추가:
  - **Semantic divergence detection 3 criteria**: AC 의미 차이 / Edge Case 누락 / Why 해석 mismatch (1개 이상 hit = divergence = true)
  - **Debate-protocol-v1 dispatch**: trigger.lane=requirements, divergence_type=semantic, min 3 / max 5 / soft default 4
  - **dispatch_mode auto_on_divergence** 우선순위 룰 정합
- `.claude-plugin/plugin.json` — version 0.4.0 → 0.5.0, description 갱신 (codex-proactive-check 추가, CFP-411 entry).

#### Why

본 lane 의 Codex proactive check 가 PL synthesis 와 의미 차이를 보일 때 single-shot 결과로 단순 PROCEED/ADDRESS_FIRST 분기만 수행했음. AC 분기·Edge Case 누락·why 해석 mismatch 같은 의미 차이는 multi-round 대화로 해소되어야 함 — Story 1 의 lane-agnostic debate-protocol-v1 을 transplant.

#### Compatibility

- **Wire**: codeforge >= 5.13.0 (wrapper ADR-052 Amendment 1 + ADR-059 + ADR-044 Amendment 1 정합)
- **Backward compat**: divergence 미검출 시 기존 ADR-052 single-shot 흐름 유지 — 새 동작은 superset
- **Sibling**: marketplace.json codeforge-requirements version 0.4.0 → 0.5.0 sync 의무 (ADR-016)

#### Related

- Story: [CFP-411](https://github.com/mclayer/plugin-codeforge/issues/392) — doc-only fast-path applied
- Wrapper PR: [#411](https://github.com/mclayer/plugin-codeforge/pull/411) merged 2026-05-11
- ADR: [ADR-052 Amendment 1](https://github.com/mclayer/plugin-codeforge/blob/main/docs/adr/ADR-052-codex-proactive-check-touchpoints.md), [ADR-059](https://github.com/mclayer/plugin-codeforge/blob/main/docs/adr/ADR-059-debate-protocol-v1.md), [ADR-044 Amendment 1](https://github.com/mclayer/plugin-codeforge/blob/main/docs/adr/ADR-044-phase-scoped-sequential-team.md)

## [0.1.0] - 2026-04-29

### CFP-37 (codeforge ζ arc) — Initial extraction (NEW)

codeforge ζ arc 세 번째 lane plugin 추출 (parent spec mclayer/plugin-codeforge CFP-31 §5.7). 4 sub-agent + 도메인 KB owner write 이전.

### Added

- `agents/RequirementsPLAgent.md` — synthesizer, 4 sub-agent 통합 + Story §2/§5/§6 self-write
- `agents/DomainAgent.md` — 도메인 KB direct write, WebFetch/WebSearch
- `agents/RequirementsAnalystAgent.md` — Bash(codex exec *) wrapper
- `agents/ResearcherAgent.md` — 외부 지식 리서치, WebFetch/WebSearch
- `templates/domain-knowledge.md` — 도메인 KB 페이지 schema (CFP-27 신설본)
- `docs/inter-plugin-contracts/requirements-output-v1.md` — canonical contract
- `overlay/hooks/{regen-agents,session-start-deps-check}.sh`
- README + CLAUDE.md

### Why

CFP-31 §5.7: Requirements lane 4 agents 가 PL 산하 병렬 패턴 + DomainAgent 의 KB owner write 가 코드 이동 첫 case (PMO 보다 큰 표면). codeforge-review v1.0 + codeforge-pmo v0.1 검증 후 진입.

### Compatibility

- **Wire**: codeforge >= 2.0.0 (wrapper 측 4 agent 삭제 + plugin install 의무 BREAKING)
- **Migration**: codeforge wrapper 와 본 plugin 동시 install 의무
- **Marketplace sync**: 본 plugin 신규 entry 등록 + codeforge wrapper version sync
