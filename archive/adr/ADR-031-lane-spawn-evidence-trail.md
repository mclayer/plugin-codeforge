---
adr_number: 31
title: Lane-spawn evidence trail (committed Orchestrator self-write + Phase 2 PR description regex + phase-gate-mergeable invariant)
date: 2026-05-06
status: Accepted
category: orchestration
carrier_story: CFP-126
parent_epic: CFP-124
supersedes: null
related_files:
  - templates/story-page-structure.md
  - templates/github-workflows/lane-evidence-check.yml
  - templates/github-pr-template.md
  - docs/orchestrator-playbook.md
  - scripts/check-lane-evidence.sh
  - CLAUDE.md
is_transitional: false
---

# ADR-031: Lane-spawn evidence trail

## 상태

**Accepted (2026-05-06)** — CFP-126 Phase 1 PR #59 (Sonnet decider CFP-126-001 pick (a) §14 high confidence) + Phase 2 PR #232 merged. Storage location freeze: **(a) Story file 의 신규 §14 Lane Evidence section** (12 field YAML schema, additive). 다른 3 candidate (§8.5 sub-block / frontmatter / PR description-only) 는 superseded. carrier_story = CFP-126 (CFP-124 Epic 의 Phase 3 child).

**Amendment 1 (2026-05-08, CFP-275)** — §결정 1 의 "Wrapper Orchestrator self-write committed lane evidence" 정의 확장: **Orchestrator-owned delegate subagent** (Orchestrator 가 §14 row append 전용으로 spawn 한 subagent) 의 §14 lane evidence write 도 본 §결정 1 의 "Orchestrator self-write" 정의에 포함됨. mechanism level subagent 경유여도 ownership identity = Orchestrator 유지. lane plugin agent 가 자체 임의 §14 직접 append 는 여전히 금지 (lane plugin spawn ≠ Orchestrator-owned delegate spawn). Cross-ref: ADR-039 §결정 3 + §결정 12.

**Amendment 2 (2026-06-15, CFP-2270)** — **§14 applicability 경량 노트: wrapper-self dogfood (repo-kind `mixed`) 면제.** §결정 1 의 §14 storage location (= Story file `§14 Lane Evidence` section) 은 Story file 이 commit 영역에 실존함을 전제한다. 그러나 wrapper plugin 자기개선 dogfood Story 는 **ADR-013 dogfood-out** 에 의해 wrapper repo `docs/stories/<KEY>.md` 가 구조적으로 부재하고 (정본 = GitHub Issue + `mclayer/codeforge-internal-docs`), 본 repo 는 `.claude-plugin/plugin.json` + `.claude/_overlay/project.yaml` 양존 = `detect-repo-kind.py` 분류 `mixed` (exit 2, ADR-027 Amendment 6 §결정 10 + ADR-083 §결정 1 4-way truth-table SSOT). 이 상태에서 `scripts/check-lane-evidence.sh` 의 Story-file presence / §14 YAML block 검사는 **충족 불가능한 검사** (검사 대상 자체가 dogfood-out 으로 부재) — false-red advisory 노이즈만 발생한다.

따라서 다음을 **applicability 노트**로 명문화한다 (정식 lint enforcement 승격 아님 — pattern_count:1, advisory 수준):

1. **면제 조건 (교집합, 좁게)**: `detect-repo-kind` 분류 == `mixed` **AND** auto-detect 후 STORY_PATH 가 비었을 때 (Story file 미발견). 두 조건 모두 참일 때만 §14 검사를 면제하고 `[N/A]` advisory 로 대체 (FAIL count 미증가). 여기서 `mixed` 판정 = detect subprocess 의 **exit code 2 AND stdout sentinel(`mixed`) 이 동시에 일치**할 때만 성립한다 (exit code 단독 의존 금지 — I-4 wording SSOT, 짝 변경 #2247 distinct-marker 와 동일 원리). 둘 중 하나만 일치하면 (예: interpreter 우연 exit 2 + 빈 stdout) `mixed` 로 인정하지 않고 fail-safe (§3) 로 면제 억제한다.
2. **회귀 보존 (over-broad 금지)**: `consumer` / `plugin` / `unknown` repo-kind 의 진짜 Story 누락 또는 §14 누락은 **면제 대상 아님** — 종전 advisory-red 보존. 면제는 dogfood `mixed` 한정. consumer 의 §14 누락까지 면제하면 lane-evidence invariant 자체가 무력화되므로 명시 차단.
3. **fail-safe (신호 불확실 → 면제 억제)**: detect subprocess 가 신호를 못 줄 때 (python3 미설치 / script 부재 / 예외 / 비-`mixed` exit) 는 면제하지 않고 **기존 advisory-red 동작 보존** (보수 측 fallback). `bootstrap-first-gate.py` `_detect_repo_kind` 의 `-1` sentinel→발화 억제 fail-safe (hook L141) 와 대칭 — 양쪽 모두 "불확실 시 더 안전한 측" 으로 degrade.
4. **CI 무영향**: `lane-evidence-check.yml` CI 워크플로는 §14 를 요구하지 않고 Phase 2 PR body `## Lane evidence` 블록만 검증하므로 본 면제와 무관 (무변경). 본 면제는 로컬 `check-lane-evidence.sh` advisory 노이즈만 다룸.

본 Amendment 는 §결정 1~5 의 normative 결정을 변경하지 않는다 — Story file 이 존재하는 모든 consumer / 일반 wrapper Story 에는 §14 evidence trail 이 종전과 동일하게 의무. 단지 "Story file 이 구조적으로 부재한 dogfood `mixed` 환경" 에 대한 applicability 공백을 advisory 면제로 보완한다. Cross-ref: ADR-013 (dogfood-out) / ADR-027 Amendment 6 §결정 10 (4-way truth-table) / ADR-083 §결정 1-2 (filesystem-only detection) / 짝 변경 #2247 (외부 script fork 테스트 distinct-marker — exit code 단독 판정 금지, stdout sentinel 병행).

**Amendment 3 (2026-08-09, CFP-2914)** — **§결정 1 lane 목록 7 → 8 (`요구사항-리뷰` 추가) + §결정 2 required lane row 동수 확장.** §결정 1 은 **FROZEN** 이므로 본 확장은 Amendment 의무 대상이다(직접 편집 금지).

ADR-125 / CFP-2326 이 **요구사항리뷰 lane 을 9번째 lane 으로 신설**했고, 이후 ADR-121 / CFP-2782 가 배포 2 lane 을 물리 제거해 현행 lane 은 **8종**이다 — `요구사항` / `요구사항-리뷰` / `설계` / `설계-리뷰` / `구현` / `구현-리뷰` / `구현-테스트` / `보안-테스트`. 그런데 §결정 1(`매 lane spawn (요구사항 / 설계 / 설계-리뷰 / 구현 / 구현-리뷰 / 구현-테스트 / 보안-테스트 …)`)은 **7종에 머물러 `요구사항-리뷰` 를 누락**한다. 같은 누락이 관측 채널 4곳에 전파돼 있다 `[verified: `.github/scripts/check-lane-evidence-block.mjs:24` REQUIRED_LANES 7종 · `.github/workflows/lane-evidence-check.yml:173` requiredLanes 7종 · `templates/story-page-structure.md:549` 7종]`. 반면 `scripts/check-lane-evidence.sh:82` `LANES` 는 이미 8종이고, `docs/inter-plugin-contracts/spawn-event-v1.md:73` `lane_label` enum 도 8종(+`없음`)이다 — 즉 **evidence 채널 안에서만 drift** 가 남아 있다.

본 Amendment 는 다음을 확정한다:

1. **§결정 1 lane 목록 = 8종** — `요구사항-리뷰` 를 정식 편입한다. FROZEN 인 storage location(= Story file `§14 Lane Evidence` section)과 12 field YAML schema 는 **무변경** — 확장 대상은 lane 열거뿐이다.
2. **§결정 2 PR body `## Lane evidence` required row = 8** — `.mjs` / `.yml` / `templates/story-page-structure.md` 를 동수 확장한다. **배열 단일화 의무**: `.mjs:24` ↔ `.yml:173` 은 현재 동일 배열의 2파일 복사본이라 각자 drift 할 수 있다 → `.mjs` 를 export 로 승격하고 `.yml` 이 이를 소비한다(선례 = `.yml:134-136` 이 이미 `.mjs` 를 dynamic import).
3. **하위호환 완화** — required row 가 7 → 8 로 늘면 기존 7-row PR 이 RED 가 된다. 신설 lane row 의 `SKIPPED` 값 사용을 명문 허용하고(row 값 enum 에 이미 존재), 게이트 메시지가 누락 lane 을 정확히 지시하게 한다.
4. **Amendment 2 면제 무손상** — dogfood `mixed` ∧ `STORY_PATH` 부재 시의 §14 면제는 본 Amendment 로 변경되지 않는다. lane 개수 확장은 면제 조건과 직교한다.

ratchet 강화 방향(관측 lane 축 순증 1, 감축 0). is_transitional: false 정합. 약화 방향(lane 목록 재축소)은 ADR-058 §결정 5 sunset_justification 의무. Cross-ref: ADR-125 (요구사항리뷰 lane 신설) / ADR-121 · CFP-2782 (배포 2 lane 물리 제거) / ADR-064 Amendment 16 (같은 carrier CFP-2914 의 peer co-dispatch leg 신설 — 본 Amendment 가 그 leg 의 lane 축 SSOT 를 정합화).

**Amendment 4 (2026-08-18, CFP-3017)** — **§결정 1 evidence row `transcript` field 의 `50자 이내` producer cap 처분 (Q-1 `함께 정산` 사용자 확정 — Story CFP-3017 §5.5) + 위생 invariant 신설 + 의무 주체 정의역 한정.** §결정 1 은 FROZEN 이므로 본 처분은 Amendment 의무 대상이다(직접 편집 금지 — Amendment 3 선례 동형). Amendment 번호 4 = 파일 내 max(3) 다음 슬롯이며 경합 부재를 firsthand 실측했다 — `origin/main`·미머지 브랜치 `origin/cfp-2985-fix-telemetry` 양쪽 `ADR-RESERVATION.md` 에 `adr_number: 31` amendment row 0건(grep rc=1) + wrapper open PR 전수(`gh pr list --repo mclayer/plugin-codeforge --state open` 8건, 2026-08-18) 중 본 파일 접촉 0건.

1. **producer cap 제거 + 서술 술어 전환 (ADR-067 Amendment 5+ 와 동일 형상 — CFP-3017 sibling)**: §결정 1 schema 의 `transcript: <inline summary 50자 이내 또는 internal-docs decision archive link>` 문면에서 **`50자 이내` 생산자 상한을 제거**하고, 길이 규범을 숫자 아닌 서술 술어로 전환한다 — **무손실 수용, 또는 표식된 절단**(head 보존 + tail 절단 + **필수 sentinel + 원본 포인터 + 원본 크기**, 절단 주체 = 수용측, **침묵 절단 금지**; `receiver_min_accept: unbounded` + `truncation_policy: marked-truncation-required` 동형). 숫자 리터럴 0 — 실측상 이 cap 은 집행된 적이 없다: `git grep -c "transcript" 6cc9a3a7b31836dc09b35ebdd0cc2b8c1f2a4454 -- scripts/check-lane-evidence.sh` → **rc=1 (hit 0 = 50자 cap 미집행)**. 즉 `transcript` 는 이미 사실상 무제한이며, 본 Amendment 는 규범 문면을 실태에 정합화하고 아래 위생 문면을 신설한다.
2. **위생 invariant 신설 (ADR-067 §결정 7 어휘 재사용 — 신규 어휘 0)**: `transcript` 값(inline summary 형)에 PII / secret / credential / API key / private absolute-path 포함 금지. 위반 발견 시 **fail-fast — 자동 redact 금지** (§14 는 committed evidence trail — 자동 치환은 원장 변조. 재저작으로 처리). 우선순위 근거 3: ① `transcript` = **required · 전 lane 전 spawn** — 노출 빈도가 구조적으로 최대 (ADR-067 `reasoning_carryover` 는 optional + 비-debate max-FIX 3/3 한정) ② 길이가 억제 수단으로 작동한 적 없음 (위 rc=1 실측) ③ 값의 성질 — 워커 발화 **원문 조각**은 설계 어휘 요약보다 붙여넣기 유입 확률이 높다.
3. ★**의무 주체 정의역 한정 (본 Amendment 의 경계 조항)**: 본 Amendment 의 위생·수용 의무 주체는 **「§14 에 값을 써넣는 Orchestrator」(Amendment 1 의 Orchestrator-owned delegate 포함)로 한정한다 — 이는 append 시점 의무이지 schema 확장·값 생산자(lane PL) 측 의무가 아니며, 본 ADR 의 자기 정의역 한정(『본 ADR 는 wrapper Orchestrator self-write 영역만 다룸. Lane plugin 자체의 spawn-side instrumentation … 은 별도 cross-plugin CFP — 본 Epic 비-범위』)을 넘지 않는다.** spawn-side instrumentation 은 본 Amendment 무접촉.
4. **미러 표면 동반 정정 — Phase 2 + 착지 순서 조건부**: `templates/story-page-structure.md` 의 두 좌표(evidence row 예시 `transcript: <inline 50자 OR link>` + 열 정의 표 행 `50자 inline OR link`)는 본 ADR schema 의 재기재 미러다. 재현(행 번호 인용 금지 — CFP-2986 이 동 파일을 in-flight 변경 중): `git grep -n "transcript" 6cc9a3a7b31836dc09b35ebdd0cc2b8c1f2a4454 -- archive/adr/ADR-031-lane-spawn-evidence-trail.md templates/story-page-structure.md`. 실 편집 = **Phase 2, CFP-2986 선착 후** rebase + 위 재현 명령 재실행으로 위치 재탐색.
5. **정직 라벨 (효과 상한)**: 본 처분의 집행면은 현재 0 이다 — `check-lane-evidence.sh` 는 `transcript` 값을 검사하지 않으며, 위생 fail-fast 는 **저작 규율**이다 (기계 차단 아님, "100% 기계강제" 아님). 검사를 신설한다면 ADR-171 warning tier 로 태어난다 (신규 blocking required context 0).
6. **수용기준 3행 (신설 규범 자기 수용기준 — 투입물의 성질로 명명, 양성 ∧ 음성 공존 의무)**: **양성** = 5-금지항목 무위반 ∧ (절단 시) sentinel·원본 포인터·원본 크기 동반한 `transcript` 값 → GREEN / **음성** = 그 값에서 요소 1개 제거(금지항목 1종 포함 또는 무표식 절단) → RED / **배선 자기보호** = 검사 배선·호출 제거 → RED.

ratchet 방향 정직 기술 (혼합 — "강화 only" 아님): 생산자 상한 문면은 소멸하나(집행 실적 0 인 문면의 실태 정합화 — 실효 약화 0), 위생 invariant + 표식 절단 술어는 신설(강화)된다. Amendment 2 면제·Amendment 3 lane 축과 직교 — 12 field schema 의 field 수·field 명 무변경, `transcript` field 의 값 제약 문면만 처분. Cross-ref: ADR-067 Amendment 5+ (CFP-3017 sibling — `reasoning_carryover` 동일 형상 처분 + §결정 7 위생 정의역 확장의 transcript 편입 carrier 가 본 Amendment) / ADR-171 (warning tier 탄생 원칙) / Story CFP-3017 §5.5 Q-1 사용자 확정.

## 컨텍스트

CFP-124 진단 (2026-05-06) §1.3 architectural root cause A1:

> **"Lane plugin 실제 spawn 흔적" 을 강제하는 invariant 부재.** Phase 1 PR + Phase 2 PR rhythm, §10 FIX Ledger, sub-issue, gate label — 모두 CI invariant 가 있지만 lane plugin 가 실제로 spawn 됐는지 검증 mechanism 없음. Claude (consumer Orchestrator) 가 인-context 에서 lane 작업을 simulate 하고 PR/ledger 만 만들면 `phase-gate-mergeable.yml` 가 통과한다.

ADR-027 §컨텍스트:35 검증 quote:

> 7 Epic (MCT-12 ~ MCT-63) 모두 main merge — 그러나 6 lane plugin 0개 spawn, manual Codex 7-area + Sonnet decider 패턴으로 우회.

### CFP-20 NG6 명시 — `§0` 위치는 cache-only

[CFP-20 spec](https://github.com/mclayer/codeforge-internal-docs/blob/main/wrapper/specs/2026-04-28-cfp-20-live-progress-design.md) NG6 명시:

> §0 file 이 commit 되거나 deliverable 이 되는 모델 (cache 로 유지)

CFP-20 Q5 = `초안 L1 (Story file §0) → 사용자 push back 후 revoked`. 즉 `.claude-work/progress/<KEY>.md` (`§0 Live Progress`) = gitignored, ephemeral cache. **CI invariant 가 보는 PR diff 에 노출 없음** — lane evidence storage 로 부적합.

본 ADR 의 evidence storage 는 **committed (PR diff 노출)** 영역에 위치 — CFP-20 §0 cache 와 명확히 분리.

## 결정 요약

5 결정 freeze. carrier story = CFP-126. Storage location 의 4 candidate 는 §결정 1 enumerate, Sonnet decider 가 CFP-126 Phase 1 에서 pick.

### 결정 1 — Wrapper Orchestrator self-write committed lane evidence in Story §14 (FROZEN)

매 lane spawn (요구사항 / 설계 / 설계-리뷰 / 구현 / 구현-리뷰 / 구현-테스트 / 보안-테스트, FIX 시 multiple entry 가능) 시 wrapper Orchestrator 가 **committed evidence** 를 **Story file `§14 Lane Evidence` section** 에 누적.

**Storage location FROZEN = (a) Story file `§14 Lane Evidence` section** (Sonnet decider CFP-126-001 pick high confidence, 2026-05-06).

**12 field YAML schema** (CFP-126 Phase 2 PR #232 templates/story-page-structure.md SSOT):

```yaml
- lane: 설계
  iteration: 1                                   # 첫 spawn = 1, FIX 재시도 = 2, 3, ...
  agent: ArchitectPLAgent (codeforge-design@mclayer)
  spawned_at: 2026-05-NN T HH:MM Z
  returned_at: 2026-05-NN T HH:MM Z
  output_status: completed | partial | failed
  outcome: PASS | FIX | SKIPPED | ESCALATED
  pr_ref: mclayer/plugin-codeforge#NNN           # Phase 2 PR ref (FIX/optimization 시 동일 PR 누적)
  decision_packet_ref: <internal-docs path or yaml id, optional>
  transcript: <inline summary 50자 이내 또는 internal-docs decision archive link>
  spawn_id: <orchestrator-side correlation id>
  fix_iteration: null                            # ADR-031 결정 4 bypass 시 BYPASS_LANE_EVIDENCE_REASON 인용
```

**Superseded candidate** (CFP-126 Phase 1 PR #59 Sonnet decider 미채택):

- ~~(b) Story file `§8.5 Impl Manifest` 안 sub-block~~ (가독성·schema 충돌)
- ~~(c) Story file frontmatter `lane_spawns:` YAML array~~ (frontmatter bloat)
- ~~(d) Phase 2 PR description body `## Lane evidence` 블록 만~~ (PR-only = Story file SSOT 분산)

**명시적 제외 (영구)**: `.claude-work/progress/<KEY>.md` (CFP-20 NG6 — gitignored cache, CI invariant 부적합).

§14 schema = additive (§1-§13 무영향 + §13 CONDITIONAL Live 와 분리). Effective date = ADR-031 Accepted PR merge (본 PR) 직후 신규 Phase 2 PR — retroactive 미처리.

### 결정 2 — Phase 2 PR description 의무 블록 `## Lane evidence` (regex 검증)

Phase 2 PR body 의무 marker:

```markdown
## Lane evidence

- 요구사항: PASS  (story=<KEY>, iteration=1, agent=RequirementsPLAgent)
- 설계: PASS
- 설계-리뷰: PASS  (gate:design-review-pass)
- 구현: PASS
- 구현-리뷰: PASS  (FIX iteration: 1 — Story §10 row 3)
- 구현-테스트: PASS
- 보안-테스트: PASS  (gate:security-test-pass)
```

CI workflow 가 `^## Lane evidence$` 헤더 + 7-row regex (`- <lane>: PASS|SKIPPED|FIX|ESCALATED`) 검증. 결정 1 의 storage 가 (a)/(b)/(c) pick 시 = Story-file ↔ PR-description cross-validate (lane name set + outcome 일치). (d) pick 시 = PR-description single source.

`templates/github-pr-template.md` placeholder 추가 — 작성 누락 방지.

### 결정 3 — `phase-gate-mergeable.yml` 가 evidence 부재 시 action_required block

`templates/github-workflows/phase-gate-mergeable.yml` 확장 (CFP-126 Phase 2):

- Phase 2 PR (label `phase:보안-테스트` 부착 / phase 진입 직후) → PR description regex 검증
- 7-row 모두 valid 형식 통과 시 = `success`
- 부재 또는 invalid format = `action_required`

`type:epic` / doc-only fast-pass (CFP-106) 변경 없음 — Epic doc PR 은 본 invariant 면제 (Phase 1 = lane spawn 개념 외).

### 결정 4 — Bypass = `BYPASS_LANE_EVIDENCE=1` env (REASON 의무 동반)

긴급 hotfix / planned skip 시:

```
BYPASS_LANE_EVIDENCE=1
BYPASS_LANE_EVIDENCE_REASON="<incident-id 또는 사유>"
```

두 env 동시 set 의무 (ADR-027 §결정 3 `HOTFIX_BYPASS_CODEFORGE` 패턴 정합).

Bypass 사용 시:
- workflow regex 검증 skip
- Phase 2 PR description 에 `BYPASS: <REASON>` 명시 의무 (CI grep)
- `docs/hotfix-playbook.md` 등재 의무
- Bypass 후 followup audit Issue 자동 생성 (ADR-026 post-merge automation 활용)

### 결정 5 — Effective date = ADR-031 Accepted 후 신규 Phase 2 PR 부터 (retroactive 미처리)

기존 Story (CFP-1 ~ CFP-123, mctrader MCT-12 ~ MCT-63) retroactive 처리 안 함:

- CFP-126 Phase 2 PR merge 직후의 새 Phase 2 PR 부터 본 invariant 적용
- 기존 Story 의 evidence 부재 = 정상 (effective date 이전)
- CI workflow 가 effective date 이후 Story 만 검사 (commit timestamp 또는 Story `date:` 비교)

ADR-027 §결과:108 retroactive 미처리 invariant 정합.

## 결과

- 본 ADR Accepted 후 모든 신규 Phase 2 PR 가 lane evidence carry 의무
- Wrapper Orchestrator 가 lane plugin 0개 spawn 시 PR merge 불가 (bypass 명시 시 audit-trail)
- Schema 데이터 누적 → 30+ Story 후 PMOAgent retro 가 actual lane spawn rate / iteration 분포 / outcome 분포 측정 (ADR-026 telemetry 패턴 정합)

## 6 lane plugin 영향 매트릭스

| Repo | 영향 | sibling PR 의무 |
|---|---|---|
| `mclayer/plugin-codeforge` (wrapper) | ADR-031 + workflow + lint script + template | 본 PR 자체 |
| `mclayer/plugin-codeforge-requirements` (이하 lane repo 8개 — 현 `plugins/<lane>/` 모노레포, 구 repo 삭제됨 2026-06-12) | 변경 없음 | 불요 |
| `mclayer/plugin-codeforge-design` | 변경 없음 | 불요 |
| `mclayer/plugin-codeforge-review` | 변경 없음 | 불요 |
| `mclayer/plugin-codeforge-develop` | 변경 없음 | 불요 |
| `mclayer/plugin-codeforge-test` | 변경 없음 | 불요 |
| `mclayer/plugin-codeforge-pmo` | 변경 없음 (단 retro 시 lane evidence 데이터 활용 — 30+ Story 후) | 불요 |

본 ADR 는 wrapper Orchestrator self-write 영역만 다룸. Lane plugin 자체의 spawn-side instrumentation (Lane plugin 측 transcript schema / agent metadata schema) 은 별도 cross-plugin CFP — 본 Epic 비-범위.

## Out-of-scope

- Lane plugin self-instrumentation (cross-plugin spawn-side schema)
- 기존 Story retroactive 적용
- Strict mode default-on (ADR-032 별도)
- `.claude-work/progress/<KEY>.md` 에 lane_spawns 추가 (CFP-20 NG6 cache invariant 보존)
- 자동 lane spawn (Orchestrator spawn 책임 — 본 ADR 는 evidence 만)

## 해소 기준

N/A — permanent policy

## 관련 파일

- `templates/story-page-structure.md` (Phase 2 PR — Sonnet pick 결과 schema)
- `templates/github-workflows/phase-gate-mergeable.yml` (Phase 2 — regex 검증)
- `templates/github-pr-template.md` (Phase 2 — placeholder)
- `docs/orchestrator-playbook.md` (Phase 2 — §3 lane spawn 절차 갱신)
- `scripts/check-lane-evidence.sh` + `scripts/test-check-lane-evidence.sh` (Phase 2 NEW)
- `CLAUDE.md` (Phase 2 — §"오케스트레이션 규칙" 갱신)
- spec: `codeforge-internal-docs/wrapper/specs/2026-05-NN-cfp-126-lane-spawn-evidence-trail-design.md` (CFP-126 Phase 1)
- plan: `codeforge-internal-docs/wrapper/plans/2026-05-NN-cfp-126-lane-spawn-evidence-trail-plan.md` (CFP-126 Phase 1)
- carrier story: `codeforge-internal-docs/wrapper/stories/CFP-126.md`
- parent Epic: `codeforge-internal-docs/wrapper/stories/CFP-124.md`

### Amendment 2 (CFP-2270) 관련 파일
- `scripts/check-lane-evidence.sh` (Phase 2 — `mixed` repo-kind + STORY_PATH 부재 시 §14 면제 분기 추가)
- `scripts/test-check-lane-evidence.sh` (Phase 2 — D2 회귀+fail-safe bash harness 신설, CFP-126 ADR 본문 NEW 표기가 미실현이었음을 본 Amendment 가 실현)
- `hooks/tests/test_bootstrap_first_gate.py` (Phase 2 — #2247 짝, TC9 family stdout sentinel 병행 assert)
- `plugins/codeforge-develop/agents/QADeveloperAgent.md` (Phase 2 — #2247 짝, distinct-marker 가이드 신설)
- `templates/scripts/detect-repo-kind.py` (무변경 — SSOT 재사용 대상)
- Story 정본: GitHub Issue mclayer/plugin-codeforge#2270 (wrapper-self dogfood, ADR-013 dogfood-out)

### Amendment 4 (CFP-3017) 관련 파일
- `archive/adr/ADR-067-fix-ledger-implementability-escalation.md` (Amendment 5+ provisional — CFP-3017 sibling, `reasoning_carryover` 동일 형상 처분 + §결정 7 위생 정의역의 transcript 편입)
- `templates/story-page-structure.md` (Phase 2 — `transcript` 두 좌표 미러 정정, CFP-2986 선착 후 재현 명령으로 위치 재탐색)
- `scripts/check-lane-evidence.sh` (무변경 — `transcript` 미검사 실측[rc=1]의 근거 파일. 검사 신설 시 ADR-171 warning tier 별 carrier)
- Story 정본: `mclayer/codeforge-internal-docs` `wrapper/stories/CFP-3017.md` §5.5 Q-1 (사용자 확정 `함께 정산`)
