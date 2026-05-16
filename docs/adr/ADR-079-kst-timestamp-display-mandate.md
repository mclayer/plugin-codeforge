---
adr_number: 79
title: KST timestamp display mandate (Layer-bounded)
status: Active
category: governance
date: 2026-05-16
is_transitional: false
carrier_story: CFP-770
parent_epic: null
supersedes: []
amends: []
amendment_log:
  - amendment: 1
    date: 2026-05-16
    carrier_story: CFP-771
    summary: "Phase 2 mechanical enforcement wire — evidence-checks-registry row append (warning-tier) + kst-timestamp-display.yml workflow + scripts/lib/check_kst_timestamp.py SSOT + label-registry-v2 v2.19 hotfix-bypass:kst-timestamp-display 27th family. mechanical_enforcement_actions[0].status deferred-followup → Active (ADR-040 Amendment 3 §결정 7.D self-application — declarative governance ADR 의 deferred-followup mechanical action 이 Phase 2 carrier 에서 Active 전환). §결정 본문 무변경 (status field + amendment_log only). self-app 근거 = established `.github/workflows/` byte-identical convention (CLAUDE.md L313 ADR-060 단락 Amendment 4 auto-phase-label.yml 선례 + decision-principle-vocabulary.yml exemplar 동형 — ADR-005 인용 아님: ADR-005 = Plugin Self-Application N/A 표준화, workflow byte-identical 정책 아님). 강화 방향 (검출 능력 추가) — ADR-058 §결정 5 ratchet 정합."
    direction: strengthen
related_stories:
  - CFP-770  # 본 Story carrier — Phase 1 (ADR-079 신설 + RESERVATION row 79 reserved 미경유 직접 active + CLAUDE.md/playbook/template/domain-knowledge)
  - CFP-771  # Phase 2 mechanical lint carrier (blocks-on CFP-770) — Amendment 1 이 mechanical_enforcement_actions[] 채움
related_adrs:
  - ADR-064  # Decision principle mandate — §결정 1 CFP-scope-unitary (Phase 1/Phase 2 독립 CFP), §결정 4 ordering invariant (RESERVATION row sequential append)
  - ADR-058  # ADR sunset criteria mandate — is_transitional:false governance presumption (§결정 7), §해소 기준 N/A permanent policy, §결정 5 sunset_justification ratchet 차단
  - ADR-040  # Worktree convention Amendment 3 — normative ADR mechanical_enforcement_actions[] 의무 (Phase 1 deferred-followup declare, CFP-771 Amendment 1 채움)
  - ADR-057  # Orchestrator Opus mandate — consumer overlay 축소 불가 패턴 (KST wrapper-canonical 강제, tz override 불가 정합)
  - ADR-073  # Orchestrator verify-before-assert — external timestamp 무변조 invariant (quote-external UTC verbatim + KST parenthetical) 정합
  - ADR-031  # Lane-spawn evidence — §14 Lane Evidence display 표 (KST) vs schema field spawned_at/returned_at (UTC strict 보존) Layer-bounded disjoint
  - ADR-060  # Evidence-enforceable promotion framework — Phase 2 CFP-771 warning-tier lint carrier (mechanical_enforcement_actions[] 채움 target)
  - ADR-061  # Python script-writing convention — Phase 2 CFP-771 scripts/lib/check_kst_timestamp.py thin-wrapper SSOT 정합
  - ADR-054  # doc-only fast-path — 본 Story = template frontmatter schema 변경 → full-lane 강제 (fast-path 제외)
  - ADR-013  # dogfood-out — Story file = internal-docs wrapper/stories/CFP-770.md
  - ADR-063  # Marketplace atomic invariant — 본 Story doc-only, plugin.json version bump 동반 여부 판단 (§3.6 marketplace_sync_declared)
related_files:
  - docs/adr/ADR-RESERVATION.md  # row 79 sequential append (carrier_story = CFP-770)
  - CLAUDE.md  # 신규 단락 "시각 표시 정책 (KST, ISO 8601)" — Orchestrator self-censor 표면 (AC-3)
  - docs/orchestrator-playbook.md  # normative cross-ref 5곳 (§12 / §14.11 / §6 / §3B.4 / §14) (AC-4)
  - templates/story-page-structure.md  # frontmatter date field KST 일자 의미 + §14 schema field UTC strict 보존 명시 (AC-5, DataMigrationArch 결정)
  - templates/epic-results.md  # frontmatter date field KST 일자 의미 (AC-5)
  - docs/domain-knowledge/concept/kst-display-invariant.md  # 신설 (AC-6, DomainAgent owner write)
  - docs/domain-knowledge/domain/governance-principle/timestamp-display-policy.md  # 신설 (AC-6, DomainAgent owner write)
  - docs/parallel-work/section-ownership.yaml  # CLAUDE.md 신규 단락 owned_sections row append (Layer A self-application, AC-3)
mechanical_enforcement_actions:
  - action: kst-timestamp-display
    status: Active
    progress_note: "Phase 2 CFP-771 Amendment 1 (2026-05-16 KST) 가 evidence-checks-registry row append (58번째 entry, current_tier:warning) + kst-timestamp-display.yml warning-tier workflow + scripts/lib/check_kst_timestamp.py SSOT (ADR-064 check_decision_principle_vocabulary.py framework 구조 차용 — cp949 L13-18 / normalize_path L54 / collect / in_scope / scan_file, FORBID_DICTIONARY → KST_TS_RE RFC 3339 §5.6 colon-offset regex 교체) + label-registry-v2 v2.19 (hotfix-bypass:kst-timestamp-display 27th family) wire 완료. Phase 1 시점 registry entry 부재 deferred-followup → Phase 2 carrier 에서 Active 전환 (ADR-040 Amendment 3 §결정 7.D self-application). grep-testable: governance display layer 영속 artifact (KST_SCOPE_GLOBS 5 = CLAUDE.md / playbook / ADR-*.md 전체 파일 scan / retros / epic-results) 의 ISO 8601 `+09:00` colon-offset form 강제 + contract field layer (docs/inter-plugin-contracts/ EXEMPT_PREFIX) UTC strict 0건 변경 invariant + frontmatter `^date:` date-only KST 일자 의미 Guard. hotfix-bypass:kst-timestamp-display (namespace per-entry — ADR-024 Amendment 3 정합)."
    target_section: §결정 2
# Phase 1 scope = ADR 본문 신설 + RESERVATION row 79 + CLAUDE.md/playbook/template/domain-knowledge
# 일괄 적용만. mechanical lint wire (evidence-checks-registry row append + workflow + script) =
# Phase 2 CFP-771 (blocks-on CFP-770). ADR-040 Amendment 3 §결정 7.D self-application invariant
# 정합 — declarative governance ADR 의 mechanical action 은 deferred-followup status 로 declare
# (registry entry 부재 시점 valid declaration, ADR-068 / ADR-077 mechanical_enforcement_actions
# deferred-followup 선례 동형).
---

# ADR-079: KST timestamp display mandate (Layer-bounded)

## 상태

**Active (2026-05-16 KST)** — CFP-770 carrier. RESERVATION row 79 sequential append 동반 (본 Story Phase 1 PR). Phase 2 mechanical lint = CFP-771 (blocks-on CFP-770, Amendment 1 이 `mechanical_enforcement_actions[]` 채움).

## 컨텍스트

### 직접 동인

CFP-722 RESUME 세션 (2026-05-16 KST) 사용자 directive verbatim:

> "너가 말만 던지고 holding 상태다보니까 알 수가 없다. 이런 경우에는 KST 로 시간을 표시해달라"

Orchestrator 가 작업 holding 상태일 때 시각 표시 부재 → 사용자가 진행 상태/지연 인지 불가 → 의사결정 지연. "말만 던지고 holding" 상태가 사용자에게 불가시 = operational friction.

### 배경 root cause

1. **시각 표시 normative SSOT 부재** — UTC 강제 정책 (CFP-295 / Issue #302 sealed) 은 contract field layer 한정이었으나 display layer 적용 영역이 미분리 상태였다. 두 layer 가 한 정책 안에서 충돌 — display layer 의 first historical decision 이 본 ADR 까지 부재.
2. **memory `feedback_time_display` = ephemeral non-authoritative layer** — 사용자 personal memory entry ("시간 표시 시 UTC 대신 KST(UTC+9) 사용") 가 현재 유일한 KST display 표현 근거. CLAUDE.md "behavioral directive → memory 금지 (normative)" 원칙에 의해 memory = ephemeral + consumer 비전파 + single-session scope = structural enforcement 불가 상태. 본 ADR 가 SSOT 영구 layer 격상 carrier.
3. **`docs/domain-knowledge/` KST display invariant 직접 entry 0건** (DomainAgent 전수 검증) — normative 격상 carrier 부재. AC-6 가 신규 페이지 2종으로 해소.
4. **communication-incidents 3 row (CFP-672/701/707)** — 표현 layer fragmentation 누적 sentinel. `docs/orchestrator-communication-incidents.md` cross-Story append-only ledger 가 표현 layer 일관성 결함을 이미 축적 중.

## 결정

### 결정 1 — Layer-bounded timestamp authority (disjoint axis)

codeforge 시스템의 timestamp 는 **두 disjoint layer** 로 분리된다. 두 layer 는 **변환 관계가 아니라 disjoint axis** — display layer 가 KST 표기라고 해서 contract field layer 값을 변환하지 않는다. 변환 logic 자체가 부재 (notation rule only, value transform 없음). 이것이 drift 회피 forcing function 이다.

| Layer | 정의 | 시각 표기 권한 |
|---|---|---|
| **display layer** (governance self-write) | Orchestrator·lane agent 가 사람에게 읽히기 위해 직접 작성하는 시각 — dialog / CLAUDE.md / playbook / ADR amendment_log / retro / EPIC-RESULTS / Story §10·§14·§9 / comment prefix | **KST `+09:00` ISO 8601 zoned 강제** (본 ADR 가 first historical decision) |
| **contract field layer** (machine-readable serialized value) | 7 inter-plugin contract timestamp field + Story §14 schema field (`spawned_at`/`returned_at`) — 기계 간 직렬화·정렬·dedup signature·lint 검증 대상 | **0건 변경 (KST 강제 비대상)** — 형식이 UTC strict Z suffix 든 ISO8601 bare 든 layer 전체가 비대상 |

### 결정 2 — display layer KST notation rule

display layer 영속 artifact 시각 표기 = **ISO 8601 RFC 3339 §5.6 colon-offset form `YYYY-MM-DDTHH:MM:SS+09:00` 의무**. basic form `+0900` 금지 (RFC 3339 §5.6 colon form 단일 SSOT — ResearcherAgent UU#1 cross-tool format drift 회피 forcing function).

| 영역 | 형식 |
|---|---|
| 영속 artifact (CLAUDE.md / playbook / ADR / retro / EPIC-RESULTS / Story §10·§14·§9 본문 표 / comment prefix) | ISO 8601 zoned `2026-05-16T19:30:00+09:00` |
| dialog · prose (Orchestrator ↔ 사용자) | prose `2026-05-16 19:30 KST` 허용 (사용자 가시성 우선) |
| frontmatter `date:` (date-only) | `2026-05-16` = **KST 일자 의미** 명문화 (zoned 형식 강제 아님 — date-only vs zoned 의도적 분리. Korea fixed +9 / DST 영구 부재로 일자 의미 모호성 없음) |

KST 약어 단독 표기 회피 — 영속 artifact 는 numeric `+09:00` 의무, prose 는 `KST` 허용 (IANA `Asia/Seoul` ≡ numeric `+09:00`, ResearcherAgent UU#3 KST abbreviation collision 회피).

### 결정 3 — contract field layer 불변 invariant (0건 변경)

7 inter-plugin contract timestamp field + Story §14 schema field (`spawned_at`/`returned_at`) = **본 ADR 가 정의를 0건 변경**. 형식 분포는 무관:

| 형식 분류 | field | 비대상 사유 |
|---|---|---|
| **UTC strict Z suffix** (6 contract — CFP-295 / Issue #302 sealed) | fix-event-v1 `시각` / git-ops-event-v1 `timestamp` / debate-protocol-v1 `detected_at`·`emitted_at`·`terminated_at` / stop-event-v1 `timestamp` / evidence-check-registry-v1 `recurrence.last_occurrence`·hotfix-bypass-audit `timestamp` | sealed pre-decision 보존 |
| **ISO8601 bare** (2 contract — UTC 미명시, sealed pre-decision 부재) | test-verdict-v2 `executed_at` / pmo-output-v1 `worktree_manifest.events[].timestamp` | machine-readable serialized value layer — display layer 아님 |
| **§14 schema field UTC strict** (Story-page-structure §14 12-field YAML block) | `spawned_at: ISO8601 UTC` / `returned_at: ISO8601 UTC` (`scripts/check-lane-evidence.sh` lint 검증 대상, ADR-031) | machine-readable schema field — Story §14 본문 markdown 표 (Start/End column) display layer 와 disjoint co-exist |

invariant 본질 = "본 ADR 의 어떤 deliverable 도 이 field timestamp 정의를 변경하지 않음" — 형식 분포와 독립적으로 유효 (Layer-bounded 핵심 invariant, AC-7).

### 결정 4 — scope-bounded-tz-authority (external timestamp 무변조)

governance self-write 만 KST 직접 표기. external timestamp (GitHub API response / git commit metadata / 기타 upstream UTC) 는 **변조 금지**. quote-external = UTC verbatim + KST parenthetical 부기 허용 (`2026-05-16T06:30:00Z (15:30 KST)`). ADR-073 verify-before-assert 정합.

### 결정 5 — 가시성 4 영역 (V-1 primary + V-2/V-3/V-4 secondary)

사용자 directive 실제 동기(why) = "Orchestrator holding/지연 상태 가시성 부재". 단순 KST 숫자 표기를 넘어:

1. **V-1 pause/resume checkpoint (PRIMARY)** — `[PAUSE] YYYY-MM-DDTHH:MM:SS+09:00 — <사유>` / `[RESUME] YYYY-MM-DDTHH:MM:SS+09:00 — <재개점>` 표준. 사용자 directive 가 직접 지목한 유일 영역 (AC-9).
2. **V-2 retro auto-trigger 시각 (secondary)** — `[RETRO TRIGGER] YYYY-MM-DDTHH:MM:SS+09:00 — Phase 2 PR merge +5min` comment prefix 표준 (ADR-045 / CFP-138, comment-prefix-registry 정합, AC-10).
3. **V-3 §10 FIX Ledger dual-clock 분리 (secondary)** — Story §10 ledger 표시 시각 = Orchestrator local KST clock (display layer) / `fix-ledger-sync.yml` Action mirror = GitHub API UTC (machine layer). fix-event-v1 contract field 는 UTC strict 보존, Story §10 ledger 표시만 KST (AC-11, E-2 정합).
4. **V-4 ADR amendment_log date (secondary)** — `date:` field = date-only KST 일자 의미 normative (AC-12).

### 결정 6 — forward-only effective date

본 ADR Accepted (2026-05-16 KST) 이후 신규 작성분만 적용. legacy retroactive backfill 미수행 (점진 sweep = Phase 2 CFP-771 `hotfix-bypass:kst-timestamp-display` 점진 정리). FeasibilityAgent "retroactive backfill 부적합" 경고 정합 (DataMigrationArch backfill 안전성 검토).

### 결정 7 — consumer overlay tz override 불가

wrapper-canonical KST 강제. consumer overlay (`.claude/_overlay/`) 는 정책을 축소할 수 없고 확장만 가능 (CLAUDE.md normative + ADR-057 정합). 미국/유럽 consumer 도입 시 별도 CFP (현 시점 scope 외). OpRiskArch 검토 — consumer overlay tz override 가 audit-trail-coherence (cross-consumer Story 시각 비교) 를 깨므로 wrapper-canonical 단일 기준 유지.

### 결정 8 — cross-plugin template SSOT 경계 명확화 (factual divergence 정정)

spec/Story §4.0 scope_manifest 가 "5 template frontmatter (wrapper-local)" 로 가정했으나 **factual divergence 확정** (CodebaseMapper fact source 재확인):

| template | 실제 SSOT 위치 | 본 ADR scope |
|---|---|---|
| `templates/story-page-structure.md` | **wrapper repo** (CLAUDE.md L334 relative link, 실재 확인) | Phase 1 변경 대상 (AC-5) |
| `templates/epic-results.md` | **wrapper repo** (실재 확인) | Phase 1 변경 대상 (AC-5) |
| `templates/adr.md` | **codeforge-design plugin** (CLAUDE.md L290 — `https://github.com/mclayer/plugin-codeforge-design/`) | wrapper Phase 1 scope 외 — codeforge-design plugin 후속 sibling Story (Phase 1 declare only) |
| `templates/change-plan.md` | **codeforge-design plugin** (wrapper repo 부재) | 동 |
| `templates/retro.md` | **codeforge-pmo plugin** (CLAUDE.md L334 — `https://github.com/mclayer/plugin-codeforge-pmo/`) | wrapper Phase 1 scope 외 — codeforge-pmo plugin 후속 sibling Story (Phase 1 declare only) |

**결정**: 본 Phase 1 = wrapper-local 2 template (`story-page-structure.md` / `epic-results.md`) frontmatter `date:` field KST 일자 의미 명시 + CLAUDE.md 신규 단락이 "ADR / change-plan / retro template (lane plugin SSOT) 도 동일 KST 일자 의미 적용 — 해당 plugin 후속 Story 가 sibling 반영" normative declare. cross-plugin template 직접 변경 = 본 wrapper Phase 1 scope 외 (ADR-013 sibling sync 패턴, memory `project_stale_skill_ownership_lore` cross-plugin ownership 잘못 가정 차단). AC-5 / AC-12 의 "5 template" 은 "wrapper-local 2 + cross-plugin 3 declare" 로 정정 — invariant 본질 (5 template `date:` 모두 KST 일자 의미) 은 유효, wrapper Phase 1 의 직접 변경 대상만 2 로 축소.

### 결정 9 — §14 Lane Evidence dual-layer co-existence (DataMigrationArch primary)

Story `§14 Lane Evidence` 는 한 섹션 안에 **두 layer 가 disjoint co-exist**:

- **display layer (KST 강제)** — Story 본문 markdown 표 `Start` / `End` column (사람이 읽는 lane evidence trail). 본 Story §14 GitOps row 가 이미 `2026-05-16T15:42:00+09:00` zoned (self-app 선행 evidence).
- **contract field layer (UTC strict 보존)** — `templates/story-page-structure.md` §14 12-field YAML schema block 의 `spawned_at: ISO8601 UTC` / `returned_at: ISO8601 UTC` (field semantics 표 #4/#5, `scripts/check-lane-evidence.sh` lint 검증 대상, ADR-031).

**결정**: `spawned_at`/`returned_at` schema field = **UTC strict 보존 (전환 안 함)**. 사유 — (a) `check-lane-evidence.sh` lint + §10 FIX Ledger fix_iteration cross-validation 의 machine-readable serialized value layer (결정 1 contract field layer 정의 직결), (b) Story §14 본문 markdown 표 Start/End 가 별도 display layer 로 이미 KST 강제 — schema field 와 표 표시가 별 layer (disjoint co-exist, 변환 관계 아님). RequirementsPL §2 D-8 deferred 분기 해소 = **schema field 전환 안 함 + 본문 표 KST 강제** (dual-layer 명문화). `templates/story-page-structure.md` §14 schema YAML comment 에 "schema field = UTC strict (machine layer, ADR-079 §결정 9) / 본문 markdown 표 Start·End = KST `+09:00` (display layer)" 명시 추가.

### 결정 10 — ADR-079 governance presumption + mechanical enforcement deferred

- `is_transitional: false` — KST display mandate = permanent policy (안전망 transitional 아님). ADR-058 §결정 7 governance presumption 정합.
- `## 해소 기준` = **N/A permanent policy** (transitional 아니므로 sunset criteria 의무 면제, ADR-058 §결정 7).
- frontmatter `mechanical_enforcement_actions[]` = **deferred-followup declare** (ADR-040 Amendment 3 §결정 7.D self-application 정합). Phase 1 시점 evidence-checks-registry entry 부재 = valid declaration (ADR-068 / ADR-077 deferred-followup 선례 동형). Phase 2 CFP-771 Amendment 1 이 registry row append + warning-tier lint wire + `hotfix-bypass:kst-timestamp-display` label 신설.
- ADR-064 §결정 1 CFP-scope-unitary — Phase 1 (CFP-770 Story doc/template) + Phase 2 (CFP-771 mechanical lint) = 독립 CFP·독립 Story·독립 PR (한 CFP "경량→full" 아님, 별개 CFP 분리 허용 패턴).

## 대안 (기각)

| 대안 | 기각 사유 |
|---|---|
| **B. Full KST (contract field 포함)** | CFP-295 / Issue #302 sealed UTC strict pre-decision 파기 → 7 contract 정렬·dedup signature 호환성 breaking + sibling plugin (codeforge-pmo GitOpsAgent git-ops-event-v1 producer) cross-repo bump. 사용자 분기 A 확정으로 기각. |
| **C. Dual-notation (KST + UTC 병기 전체)** | 모든 영속 artifact 에 두 형식 병기 = verbosity 폭증 + drift 표면 증가 (두 값 동기화 부담). scope-bounded-tz-authority (external 만 parenthetical) 로 충분. |
| **§14 schema field KST 전환** | `check-lane-evidence.sh` lint + cross-validation 의 machine layer 직결 — 전환 시 lint regex breaking + ADR-031 §14 schema 정의 변경 (contract-adjacent). 결정 9 dual-layer 로 해소 (전환 불요). |
| **cross-plugin template (adr/change-plan/retro) wrapper Phase 1 직접 변경** | memory `project_stale_skill_ownership_lore` cross-plugin ownership 잘못 가정 — ADR-013 sibling sync 위반. 결정 8 declare-only 로 해소. |

## 결과

- **Phase 1 (CFP-770)**: ADR-079 신설 + RESERVATION row 79 + CLAUDE.md 신규 단락 + playbook 5 cross-ref + wrapper-local 2 template frontmatter + 2 domain-knowledge 신설 + section-ownership.yaml row. dogfood self-app (본 Story §10/§14/§9 즉시 KST).
- **Phase 2 (CFP-771, blocks-on CFP-770)**: mechanical lint workflow + script + evidence-checks-registry row + label-registry MINOR + ADR-079 Amendment 1 (`mechanical_enforcement_actions[]` 채움) + cross-plugin template sibling Story trigger + legacy retroactive sweep.
- **contract field layer**: 0건 변경 (7 contract + §14 schema field — Layer A 정합, inter-plugin contract bump 0건).
- **DesignReview**: 본 ADR 의 `mechanical_enforcement_actions[]` deferred-followup status + `is_transitional: false` + `## 해소 기준` N/A 정합 검증 의무 (ADR-040 Amendment 3 / ADR-058 §결정 7).

## 해소 기준

N/A — permanent policy (`is_transitional: false`, ADR-058 §결정 7 governance presumption). KST display mandate 는 sunset 대상이 아닌 영구 governance 정책. 약화 방향 amendment (display layer scope 축소 / forward-only → no-op / consumer overlay tz override 허용) 는 ADR-058 §결정 5 `sunset_justification` 의무로 차단 (top-down ratchet — 강화 방향만 허용).

## 관련 파일

- [ADR-RESERVATION](ADR-RESERVATION.md) — row 79 carrier_story = CFP-770
- [ADR-064](ADR-064-decision-principle-mandate.md) — §결정 1 CFP-scope-unitary / §결정 4 ordering invariant
- [ADR-058](ADR-058-adr-sunset-criteria-mandate.md) — §결정 7 governance presumption / §결정 5 ratchet
- [ADR-040](ADR-040-worktree-convention.md) — Amendment 3 §결정 7.D mechanical_enforcement_actions[] self-application
- [ADR-057](ADR-057-orchestrator-opus-mandate-and-sonnet-opus-fallback.md) — consumer overlay 축소 불가 패턴
- [ADR-031](ADR-031-lane-spawn-evidence-trail.md) — §14 Lane Evidence schema (dual-layer co-existence 근거)
- `CLAUDE.md` — 신규 단락 "시각 표시 정책 (KST, ISO 8601)"
- `docs/orchestrator-playbook.md` — normative cross-ref 5곳
- `docs/domain-knowledge/concept/kst-display-invariant.md` — 신설 (개념 SSOT)
- `docs/domain-knowledge/domain/governance-principle/timestamp-display-policy.md` — 신설 (정책 narrative SSOT)
