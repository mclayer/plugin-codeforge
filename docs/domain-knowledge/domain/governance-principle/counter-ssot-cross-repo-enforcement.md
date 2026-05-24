---
kind: domain_fact
type: domain-knowledge
area: governance-principle
topic_slug: counter-ssot-cross-repo-enforcement
title: Counter SSOT cross-repo enforcement — MCT-NNN key collision pattern + 3 enforcement option (Amendment 후보)
status: Active
tags:
  - governance-principle
  - counter-ssot
  - cross-repo
  - mct-nnn
  - key-collision
  - cascade-rename
  - enforcement-option
  - desync-correction
related_adrs:
  - ADR-035       # Application BC charter governance — counter governance 와 axis disjoint, cross-repo SSOT 원칙 정합
  - ADR-040       # Worktree convention — multi-worktree session 영역 (counter collision 발생 환경)
  - ADR-050       # Parallel epic coordination — counter collision 의 distributed work coordination layer
  - ADR-054       # Story 작성 의무 + doc-only fast-path — 본 SSOT codify 형식
  - ADR-085       # Multi-session collaboration protocol — counter SSOT violation 의 distributed origin axis
related_stories:
  - CFP-1486      # 본 codify carrier (counter governance amendment 후보 발의)
  - MCT-227       # mctrader consumer 측 counter collision correction Story (hub#447+#448 MERGED 2026-05-24)
created: 2026-05-25
updated: 2026-05-25
---

# Counter SSOT cross-repo enforcement — MCT-NNN key collision pattern + 3 enforcement option (Amendment 후보)

## Summary

Consumer project (mctrader 7+ repo) 의 MCT-NNN counter SSOT (mctrader-hub `counters.json`) 가 cross-repo distributed work 시 enforcement layer 부재로 collision 빈도 누적 — 3 known case (MCT-200/202 + MCT-204/205 + MCT-211/212) sentinel pattern. wrapper plugin-codeforge governance 영역 amendment 후보 3 option (A: mechanical enforcement / B: doc-only / C: centralization) 결정 carrier.

## Problem

Cross-repo single SSOT counter (mctrader-hub `counters.json`) 가 다음 violation pattern 누적:

| Pattern | Origin | Correction cost |
|---|---|---|
| out-of-band MCT-NNN key creation (hub counter 미경유) | parallel session distributed work | 1 cascade rename Story |
| post-Epic correction Story counter 미reserved | retroactive Story origin | 1 desync_correction Story |
| cross-repo collision (hub ↔ data repo 별 작업 LAND) | sibling repo parallel merge | 1 cascade rename + 13 file content + 7 file rename + 9 신규 reservation |

각 violation 발생 시 cascade rename + counters.json `_desync_correction` annotation + GitHub Issue/PR body post-merge annotation. governance Story 1개 + 정정 cost 약 1-2 시간.

## Usage

cross-repo MCT-NNN key 신설 시 mctrader-hub `counters.json` reservation 선행 의무 — 미경유 PR commit prefix `[MCT-NNN]` 차단 (Option A 적용 시) 또는 consumer self-discipline (Option B 적용 시) 또는 plugin API 경유 (Option C 적용 시).

## 정의

본 SSOT 는 mctrader 7+ repo (mctrader-hub + mctrader-data + mctrader-pulse + ...) 의 cross-repo MCT-NNN key SSOT (mctrader-hub `counters.json`) governance violation pattern + 3 enforcement option (A / B / C) decision 영역을 codify 한 wrapper-scope authoritative reference. 본 SSOT 는 violation pattern 정의 + 3 option trade-off + decision criteria 명문화.

**Evidence (3 known case)**:

| Case | Date (KST) | Origin | Resolution |
|---|---|---|---|
| MCT-200/202 | 2026-05-22 | out-of-band MCT-NNN key creation, mctrader-hub counter 미경유 | MCT-203 `_desync_correction` annotation |
| MCT-204/205 | 2026-05-22 | post-Epic correction Story, counters 미reserved | retroactive reservation backfill |
| MCT-211/212 | 2026-05-24 | cross-repo collision (hub ↔ mctrader-data 별 작업 LAND) | MCT-227 cascade rename (hub MCT-211→219 / 212→220 / 213~218→221~226 + 9 신규 reservation, hub#447+#448 MERGED) |

3 case 모두 enforcement layer 부재로 발생 — pattern_count ≥ 3 reach (ADR-045 §D-9 cross_story_pattern_adr_trigger Mandatory escalation threshold).

## 컨텍스트

### Counter SSOT 정의

- **SSOT location**: mctrader-hub `counters.json` (single source of truth, cross-repo aggregator)
- **Reservation API**: counters.json `reservations.MCT-NNN` field (manual append, no plugin tooling)
- **Cross-repo scope**: mctrader 7+ repo (hub + data + pulse + ...) 가 동일 MCT-NNN namespace 공유
- **Naming convention**: `MCT-NNN` (N = 3-digit, sequential)

### Violation root cause

1. **Distributed work** — 별 session/repo 가 MCT-NNN 을 평행 생성 (hub counters.json 미경유 → 동일 NNN 충돌)
2. **No mechanical enforcement** — PR commit prefix `[MCT-NNN]` 가 counters.json reservation 존재 verify 없이 통과
3. **Retroactive Story** — Epic close 후 corrective Story 의 reservation backfill 누락
4. **Cross-repo parallel merge** — hub PR 와 data repo PR 가 동시 LAND, hub counters.json refresh window 사이 collision

### verify-before-trust 4-layer governance positional axis

본 violation pattern 은 verify-before-trust 4-layer governance (ADR-073 / ADR-070 / ADR-082 / ADR-045 §D-9) 의 **distributed coordination layer (ADR-085 sibling)** 영역 — counter SSOT 영역 sub-domain 위치:

| Layer | ADR | 영역 |
|---|---|---|
| 1 | ADR-073 | Orchestrator verify-before-assert (cross-repo state) |
| 2 | ADR-070 | Codex verify-before-trust (외부 worker output) |
| 3 | ADR-082 | Write-time self-write verification (internal lane agent) |
| 4 | ADR-045 §D-9 | PMOAgent retro corpus pattern_count escalation |
| 5 | ADR-085 | Multi-session collaboration protocol (active_sessions / handoff) |
| **6 (본 entry)** | (ADR-085 disjoint sub-axis 후보) | **Counter SSOT cross-repo enforcement** — distributed counter reservation verify-before-assign |

본 sub-domain 은 ADR-085 multi-session collaboration 의 instantiate — distributed work 가 shared counter namespace 를 verify 없이 claim 시 silent collision. ADR-073 §결정 1 verify-before-assert + ADR-085 active_sessions 와 disjoint axis (counter SSOT 영역 별).

## 핵심 규칙

### 규칙 1 — MCT-NNN 신설 시 mctrader-hub `counters.json` reservation 선행 의무

cross-repo distributed work (mctrader 7+ repo 안 임의 repo) 가 MCT-NNN key 신설 시 다음 4-step sequential:

1. **Reservation request** — mctrader-hub `counters.json` `reservations.MCT-NNN` field append
2. **Pre-commit verify** — `MCT-NNN` reservation 존재 verify (현재 self-discipline)
3. **Commit prefix** — `[MCT-NNN]` commit prefix 사용 (PR title + commit message)
4. **Post-merge verify** — Epic close 시 `_desync_correction` annotation 부재 verify

본 4-step 위반 시 cascade rename + desync_correction Story 의무.

### 규칙 2 — 3 enforcement option decision matrix

| Option | Mechanism | Complexity | Coverage | Migration cost |
|---|---|---|---|---|
| **A** | mechanical enforcement | medium (workflow + script + ADR amendment) | 7+ repo all PR | low (CI gate 추가) |
| **B** | doc-only consumer self-discipline | low (current state, governance skill 박제) | self-discipline 만 | 0 (no change) |
| **C** | counter SSOT centralization in plugin | high (plugin API + downstream cascade) | full mechanical | high (consumer migration) |

### 규칙 3 — Option A 권장 (derived default, ADR-060 evidence-enforceable promotion framework)

pattern_count ≥ 3 reach (ADR-045 §D-9 cross_story_pattern_adr_trigger Mandatory threshold) → Option A mechanical enforcement 권장. Option B 는 위반 빈도 누적만 추적 (mitigation 0), Option C 는 over-engineering (single org dogfood scope).

**Option A 구체 mechanism (proposed, follow-up Story carrier)**:

- ADR-054 (또는 신규 counter governance ADR) amendment — counters.json reservation 미경유 PR commit prefix `[MCT-NNN]` 차단 CI gate
- `templates/.github/workflows/counter-ssot-check.yml` 신규 — PR title/commit prefix `[MCT-NNN]` 감지 → mctrader-hub counters.json `reservations.MCT-NNN` 존재 verify (cross-repo gh API fetch) → 미존재 시 PR fail
- `scripts/check-counter-ssot.sh` + `scripts/lib/check_counter_ssot.py` — Python SSOT 정합
- evidence-checks-registry `counter-ssot-check` entry (warning tier 첫 도입, ADR-060 §결정 5)
- `hotfix-bypass:counter-ssot-check` label 신설 (ADR-024 §결정 6.A per-entry namespace, family member next)
- bats fixture (TDD RED→GREEN proof per ADR-082 §결정 11.A)
- 7+ repo 전수 적용 (cross-repo workflow, CODEFORGE_CROSS_REPO_PAT scope)

### 규칙 4 — pattern_count + ADR-045 §D-9 escalation threshold

본 pattern 의 향후 occurrence 누적 시:

- pattern_count ≥ 2 (current state) → warning tier 도입 (Option A Phase 1 declarative — 현재 본 SSOT codify)
- pattern_count ≥ 3 (next occurrence) → mechanical wire activation (Option A Phase 2)
- pattern_count ≥ 5 → blocking-on-pr 승격 검토 (ADR-060 §결정 19)
- pattern_count ≥ 8 → ADR-045 §D-9 Mandatory ADR escalation (counter governance ADR 신설 의무)

## 경계

### scope 내 (본 SSOT codify 영역)

- mctrader 7+ repo cross-repo MCT-NNN counter SSOT violation pattern 정의
- 3 known case (MCT-200/202 + MCT-204/205 + MCT-211/212) evidence
- 3 enforcement option (A / B / C) trade-off matrix
- Option A 권장 + 구체 mechanism proposal (follow-up Story carrier)
- pattern_count escalation threshold ladder

### scope 외 (별 carrier 영역)

- **Option A 실 구현** (workflow + script + bats + evidence-checks-registry + label-registry) — **CFP-FU-1 별 follow-up Story** (Phase 1 declarative anchor 본 SSOT + Phase 2 mechanical wire 별 Story carrier, ADR-082 §결정 6 retain pattern 답습)
- **Option C centralization** (plugin API + consumer migration) — over-engineering (single org dogfood scope, 별 carrier 영역)
- **mctrader consumer-side counters.json schema** — consumer repo SSOT 영역 (wrapper plugin scope 외)
- **cross-repo CODEFORGE_CROSS_REPO_PAT scope 확장** — Option A 의 transitive requirement (ADR-066 carrier)
- **ADR-085 multi-session collaboration sub-axis 신설** — counter SSOT 영역의 ADR-085 §결정 0 disjoint sub-axis codify (Option A 실 wire 시 carrier)

## 관련 ADR

- **ADR-035** — Application BC charter governance. counter governance 와 axis disjoint (BC charter ↔ counter SSOT), cross-repo SSOT 원칙 정합. counter governance ADR 신설 시 ADR-035 cross-ref.
- **ADR-040** — Worktree convention. multi-worktree session 영역 (counter collision 발생 환경). distributed work coordination 의 baseline ADR.
- **ADR-050** — Parallel epic coordination. counter collision 의 distributed work coordination layer (Phase 1 scope_manifest 영역). counter SSOT violation = parallel epic coordination 실패 patten.
- **ADR-054** — Story 작성 의무 + doc-only fast-path. 본 SSOT codify 형식 (doc-only fast-path 정합). Option A 적용 시 별 amendment carrier.
- **ADR-085** — Multi-session collaboration protocol. counter SSOT violation 의 distributed origin axis (active_sessions / handoff). 본 SSOT 의 6th sub-domain 위치.

## 변경 이력

- **2026-05-25 (CFP-1486)** — 본 SSOT codify (S5 Theme 4 carrier). 3 known case evidence + 3 enforcement option (A/B/C) trade-off matrix + Option A 권장 + pattern_count escalation threshold ladder. wrapper scope codify 한정 (Option A 실 wire = 별 CFP-FU-1 carrier, Option C centralization = scope 외).
