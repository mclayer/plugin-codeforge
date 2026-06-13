# Changelog

`codeforge-pmo` plugin 릴리스 이력.

버전 체계: [Semantic Versioning 2.0.0](https://semver.org/lang/ko/). v1.0 이전은 minor bump도 breaking 가능.

## [0.4.0] - 2026-06-14

### CFP-2236 — DialogFidelityAgent 전면 폐지 (sunset) (MINOR)

DialogFidelityAgent (CFP-777 Story-1 신설 cross-cutting read-only dialog fidelity verifier) 전면 폐지. agent count 3→2 (PMOAgent + GitOpsAgent). CFP-777 의 신규 agent 추가가 MINOR (0.1.3→0.2.0) 였으므로 대칭 제거도 MINOR (capability 축소, ADR-037).

#### Removed

- `agents/DialogFidelityAgent.md` — 파일 삭제 (git history 가 이력 보존).
- `CLAUDE.md` — 3 sibling agent 서술 → 2 sibling. 책임 표 DialogFidelity 열 제거. Agent 상세 SSOT 링크 제거. sunset 안내 추가.
- `docs/architecture/codeforge-pmo.md` — title frontmatter "Dialog fidelity" 제거 / 모듈 표 DialogFidelity 행 제거 (3→2) / Cross-cutting boundary bullet 제거 / verifier surface 블록 제거 / 데이터 흐름 trigger 5 (dialog turn) 블록 + downstream bullet 제거 / ADR-076 current state 인용 제거. sunset banner 2종 추가.

#### Why

- **죽은 의무 (dead mandate)**: 3-anchor spawn 의무 (특히 `pre_architectpl_synthesis` "항상 active") 런타임 미준수 — CFP-2234 전 과정에서 ArchitectPL synthesis 사용자 보고 시점에도 미spawn (CFP-2215 이전 TodoWrite dead 와 동형). 본 CFP-2236 설계 lane fable→opus fallback = fable 의존 불안정성 동반 evidence.
- **검증 ground 중복 (redundancy)**: 동일 anchor 의 Codex TP#2/TP#3 (mandatory P0/P1 inline FIX) + ADR-064 §결정 9 Q-3check (Orchestrator self-check) 가 이미 cover. DialogFidelity = `correction_action_hint` 5-enum 권고만 = 최저 구속력.
- **비용 대비 효과 0 (cost vs effect)**: 매 synthesis·매 FIX 직전 Opus verifier spawn 누적 비용, 측정된 효과 0 (§결정 14 measurement deferred-followup 실 wiring 0).

ADR-058 §결정 5 (약화 evidence-gate) + ADR-064 §결정 7 (symmetric ratchet) 정합 — 약화 방향 1급 허용, evidence-grounded, first weaken-direction amendment.

#### Cross-references

- ADR-071 Amendment 9 (carrier-preserved in-place sunset — §결정 12/13/14 + §17.4.3 의 DialogFidelity 부분 강등, ADR-071 본체 무손상)
- ADR-058 §결정 5 (약화 evidence requirement) / ADR-064 §결정 7 (symmetric ratchet)
- ADR-037 (plugin bump semantics — capability 축소 = MINOR, CFP-777 신규 agent MINOR 와 대칭)
- ADR-063 (marketplace atomic invariant — 4 mirrored field sync 동반)
- Story file (internal-docs): `wrapper/stories/CFP-2236.md`

## [0.3.3] - 2026-06-12

### Changed (CFP-2178 — S6 lane repo archive 참조 sweep, PATCH)

- `overlay/hooks/session-start-deps-check.sh` 안내 URL — 구 lane repo (`mclayer/plugin-codeforge-pmo`) → wrapper 모노레포 앵커 (`mclayer/plugin-codeforge/tree/main/plugins/codeforge-pmo#dependencies`). 구 lane repo 8개 = 2026-06-12 GitHub archive (ADR-118 D1) — read-only repo 안내 차단.
- `CLAUDE.md` `story_issues` repo 좌표 — `mclayer/plugin-codeforge-pmo` → `mclayer/plugin-codeforge` (archive 후 read-only repo 에 issue 생성 지시 = 기능 파손 해소).
- `README.md` Inter-plugin Contract 절 — "canonical=lane repo + wrapper sibling 동기 의무" 서술 → wrapper `docs/inter-plugin-contracts/pmo-output-v1.md` 단일 원본 (ADR-118 D5 — sibling sync 폐지).

## [0.3.1] - 2026-05-30

### [CFP-1845 follow-up] agent model 핀 → 별칭 전환 (PATCH)

[CFP-1845 follow-up] agent model 핀 → 별칭 전환 (opus/sonnet/haiku 항상 최신 지칭). frontmatter model field 3건. tier 분류 변경 0건. wrapper #1846 / #1847 연계. marketplace sibling sync 동반.

#### Changed

- `agents/PMOAgent.md` — `model: claude-opus-4-7` → `model: opus`
- `agents/DialogFidelityAgent.md` — `model: claude-opus-4-7` → `model: opus`
- `agents/GitOpsAgent.md` — `model: claude-sonnet-4-6` → `model: sonnet`

## [0.3.0] - 2026-05-27

### CFP-1764 Story-3 — PMOAgent prompt template 평이 번역 의무 directive 추가 (MINOR)

ADR-071 Amendment 8 (wrapper plugin-codeforge, Story-1 #1769 MERGED 2026-05-27 12:30:49 KST) horizontal axis 자매 carrier. PMOAgent prompt template 본문에 codename → 평이 어휘 평문 풀이 의무 directive 추가. retro / Epic 분해 / Cross-Story 패턴 보고 산출물 안 사용자 dialog paste 영역 jargon leak 차단.

#### Added

- `agents/PMOAgent.md` — "출력 시 평이 어휘 의무 (ADR-071 §결정 19, Amendment 8 — CFP-1764)" section 신설:
  - In scope 산출물 4종 명시 (retro `## 핵심 발견` / `## 다음 단계` / Epic 분해 위험 신호 / Cross-Story patterns 요약 / ADR 후보 발의 `## 배경` `## 문제` 첫 paragraph)
  - Lookup SSOT = wrapper `docs/wording-dictionary.md` 카테고리 (c) 15 batch + ratchet 평문 풀이 ("강화 방향 고정 확장")
  - Out of scope (governance artifact 본문 / pmo_output v1 structured field / retro frontmatter)
  - 적용 예시 15-row 표
- `.claude-plugin/plugin.json` — version 0.2.0 → 0.3.0 MINOR. description CFP-1764 Story-3 entry append.

#### Why

ADR-071 §결정 19 (Amendment 8, Story-1 carrier) horizontal axis 자매 — PMOAgent retro 본문 + Cross-Story patterns 요약 sentence 가 Story 작업 단위 완료 직후 사용자에게 보고되는 영역. 사용자 directive 2026-05-27 KST (mctrader-hub#517 4-turn 누적 redirect + confirm directive: "오케이 그렇게 escalation 하자. 그렇게 버전업되면 버전 업그레이드 통해 적용받는 식으로") wrapper canonical path 의무 적용.

#### Compatibility

- canonical: wrapper `plugin-codeforge` (Amendment 8 ADR-071 + wording-dictionary 카테고리 (c) SSOT, Story-1 PR #1769 MERGED)
- sibling: codeforge-requirements (Story-3 PR sibling sync, 동일 MINOR)
- marketplace: 4 mirrored field (`name` / `version` / `description` / `author`) atomic sync 의무 (ADR-063 §결정 2 ordering)
- Effective date: marketplace sync PR merged + 본 PR merged + consumer `/plugins install` 후 (ADR-053 structural change restart 적용 영역)

## [0.2.0] - 2026-05-16

### CFP-777 (Epic #761 Story-1) — DialogFidelityAgent 신규 cross-cutting verifier agent 추가 (MINOR)

ADR-071 Amendment 1 external verifier auxiliary layer 채널 신설. Orchestrator-user dialog turn 의 세션 개시 요건 + 누적 결정/제약 ledger (Layer 4 incidents) 이탈 여부를 외부 read-only agent 가 검수 — verifier-narrower-than-generator 패턴 (ADR-071 가설 E self-referential trap 해소).

#### Added

- `agents/DialogFidelityAgent.md` — 신규 cross-cutting verifier agent:
  - Input Port: closed enum spawn_anchor 3-value (`post_user_turn | pre_architectpl_synthesis | pre_fix_rootcause`) + current_output_hash + ledger_path + decision_ledger + current_output_verbatim
  - Output Port: closed enum verify_result 3-value (`fidelity_ok | drift_detected | ledger_gap`) + evidence_path[] + incident_row_match + correction_action_hint 4+null
  - 3-anchor spawn trigger (ADR-039 §결정 2 inline whitelist 보존)
  - verifier-narrower-than-generator 3 mechanical mitigation (M1 read-only tools / M2 closed enum output / M3 SHA-256 hash-pin)
  - ADR-070 verify-before-trust 의무 / ADR-079 KST timestamp / ADR-042 Amendment 6 Opus pilot tier
  - Story §14 spawn evidence trail row schema

#### Changed

- `CLAUDE.md` — agent count 2→3: DialogFidelityAgent 추가. agent 책임 영역 표 3열 확장. Agent 상세 SSOT 링크 추가.
- `.claude-plugin/plugin.json` — version `0.1.3` → `0.2.0` (MINOR: 신규 agent 추가). description 끝에 CFP-777 신설 내용 append.

#### Why

ADR-071 Amendment 1 §결정 12 — external verifier auxiliary layer additive invariant. Orchestrator 자기 자신이 dialog fidelity 를 검증하는 구조(self-referential trap, 가설 E)는 blind spot 내재 → codeforge-pmo 소속 외부 agent 위임으로 해소. ADR-042 Amendment 6 Opus pilot tier 정합 (verifier 역할의 정밀도 요건).

#### Cross-references

- ADR-071 Amendment 1 §결정 12 (external verifier auxiliary layer)
- ADR-042 Amendment 6 (Opus pilot tier)
- ADR-070 §B verify-before-trust chain
- ADR-039 §결정 2 (Inline whitelist 4-entry 보존)
- ADR-079 (KST timestamp display layer)
- Story file (internal-docs): `wrapper/stories/CFP-777.md`

## [0.1.3] - 2026-05-13

### CFP-597 — GitOpsAgent §3.6 marketplace sync proactive PR dispatch (ADR-063 Amendment 1, PATCH)

Orchestrator 가 Phase 2 PR open 시점에 Change Plan §13 `marketplace_sync_required: true` declare 감지 시 GitOpsAgent §3.6 spawn → marketplace cfp-NNN worktree 신설 + marketplace.json mirrored field sync + PR open.

#### Added

- `agents/GitOpsAgent.md` — `§3.6 Marketplace sync proactive PR dispatch (CFP-597 / ADR-063 Amendment 1)` 섹션 신설:
  - Trigger 조건 (Orchestrator monopoly, Phase 2 PR open 시점, Change Plan §13 lookup)
  - artifacts verbatim 첨부 의무 (ADR-070 verify-before-trust)
  - 행위 5단계 (worktree 신설 / marketplace.json 갱신 / PR open / cross-reference / merge ordering)
  - ADR-063 §결정 2 ordering 정합 (marketplace PR 선행 merge 의무)
  - dispatch trigger 영역 + Cross-reference

## [0.1.2] - 2026-05-13

### CFP-534 — ADR-050 Amendment 1 GitOpsAgent intersection 로직 확장 (PATCH)

EPIC-RESULTS CFP-425 §7.5 follow-up carrier #5. ADR-050 Amendment 1 (wrapper) sibling sync — GitOpsAgent agent file 책임 §3.5 신설 (Epic Scope Manifest intersection 검사 — cross-section conflict detection).

#### Changed

- `agents/GitOpsAgent.md` — §3.5 "Epic Scope Manifest intersection 검사" 신설. 3 신규 scope manifest field (`planned_inter_plugin_contracts[]` / `planned_label_registry_bumps[]` / `cross_section_conflict_detection`) 활용 로직 + intersection 발견 시 WARN comment 자동 발의 + merge-order 자동 부여 (lower CFP 우선).

#### Why

2026-05-13 KST CFP-521 v2.4 vs CFP-429 v2.5 가 `docs/inter-plugin-contracts/label-registry-v2.md` frontmatter 3-location 동시 수정 (manual 15분 추가 + risk) sentinel evidence. 단순 file overlap 검출로는 frontmatter 의미 충돌 식별 불가 → cross-section detection layer 신설.

#### Cross-references

- ADR-050 Amendment 1 (wrapper) — `docs/adr/ADR-050-parallel-epic-conflict-coordination.md`
- Epic CFP-425 §7.5 follow-up
- Story file (internal-docs): `wrapper/stories/CFP-534.md`

## [0.1.1] - 2026-05-13

### CFP-462-followup — phase-gate-mergeable workflow sync (PATCH)

EPIC-RESULTS CFP-462 §6 carrier #1. Wrapper PR #500 (CFP-499 / ADR-010 Amendment 4 sibling-pr label fast-pass) merge 후 sibling repo backport 누락 detection.

#### Changed

- `.github/workflows/phase-gate-mergeable.yml` — wrapper SSOT (`templates/github-workflows/phase-gate-mergeable.yml`) verbatim mirror. CFP-113/123/133/342/499 누락 전체 backport (old version 였음).

#### Why

ADR-010 sibling sync 의무. sibling-pr label fast-pass + CFP-113/123/133/342 정합.

#### Compatibility

- **Wire**: workflow file 만 변경. agent / contract / overlay 영향 없음.
- **Marketplace sync**: 본 PATCH bump 의 marketplace.json mirror 는 별도 후속 carrier.

## [0.1.0] - 2026-04-29

### CFP-36 (codeforge ζ arc) — Initial extraction (NEW)

codeforge ζ arc 두 번째 lane plugin 추출 (parent spec mclayer/plugin-codeforge CFP-31 §5.6). 가장 작은 lane (PMOAgent 1개) 으로 writer-distributed 패턴의 두 번째 검증 단계.

### Added

- `agents/PMOAgent.md` — codeforge wrapper에서 이전. self-write 권한 확장 (Edit(docs/stories/**), mcp__github__add_issue_comment, mcp__github__issue_write, gh api milestones/graphql)
- `templates/retro.md` — codeforge wrapper에서 이전
- `docs/inter-plugin-contracts/pmo-output-v1.md` — pmo_output v1 contract (canonical)
- `overlay/hooks/regen-agents.sh` — codeforge core merge.py 재사용 (sibling discovery 불필요)
- `overlay/hooks/session-start-deps-check.sh` — codeforge core 설치 verify
- `.claude-plugin/plugin.json` v0.1.0 (initial)
- `README.md` — 설치 + dependency 안내

### Why

CFP-31 ζ arc 로드맵 §5.6: PMOAgent 가 가장 작은 lane (1 agent) + 가장 약한 결합 (Cross-cutting, lane gate 무관) → writer-distributed 패턴의 두 번째 검증으로 적합. CFP-35 review v2 retrofit (코드 이동 0) 검증 후 코드 이전 첫 사례.

### Compatibility

- **Wire**: codeforge >= 1.0.0 (codeforge wrapper 측 PMOAgent 삭제 + plugin install 의무 추가가 BREAKING)
- **Migration**: codeforge wrapper 와 본 plugin 동시 install 의무. consumer 측 SessionStart hook chain 활성화
- **Marketplace sync**: 본 plugin 신규 entry 등록 + codeforge wrapper version sync 동시 진행 (CFP-24 정책)
