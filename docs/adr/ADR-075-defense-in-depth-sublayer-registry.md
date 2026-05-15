---
adr_number: 75
title: Defense-in-depth sublayer registry — sublayer enumeration SSOT 분리
status: Proposed
category: governance
date: 2026-05-14
is_transitional: false
sunset_justification: "N/A — permanent governance policy. ADR-064 §self-application top-down ratchet 정합 (sublayer enumeration 영역 의 SSOT 분리 + 향후 sublayer 추가 마찰 감소 = 강화 방향 only). ADR-058 §결정 5 약화 방향 발의 차단 logic 통과."
related_adrs:
  - ADR-063  # marketplace atomic invariant — §결정 5 본문 표 sublayer enumeration 영역 source
  - ADR-008  # inter-plugin contract versioning
  - ADR-010  # sibling sync — kind:registry sibling sync 면제 정합
  - ADR-058  # ADR sunset criteria
  - ADR-054  # doc-only fast-path 정합 (Phase 1 + Phase 2 combined)
related_stories:
  - CFP-709  # 본 carrier
  - CFP-441  # PR-time CI sublayer 도입 carrier
  - CFP-447  # local advisory sublayer 도입 carrier
  - CFP-477  # local auto-rebase guidance sublayer 도입 carrier
related_files:
  - docs/adr/ADR-063-marketplace-atomic-invariant.md
  - docs/inter-plugin-contracts/defense-in-depth-sublayer-registry-v1.md
  - docs/inter-plugin-contracts/MANIFEST.yaml
  - CLAUDE.md
mechanical_enforcement_actions: []
# Phase 1 PR scope = SSOT codify only (declarative). 
# 향후 sublayer 추가 시 enforcement 는 ADR-063 §결정 5 PR-time mechanical action 영역 (ADR-063 4-layer defense 정합).
---

# ADR-075: Defense-in-depth sublayer registry — sublayer enumeration SSOT 분리

## 상태

`Proposed` (2026-05-14). ADR-063 §결정 5 본문 표 sublayer enumeration 영역 의 kind:registry SSOT 분리 carrier.

## 컨텍스트

ADR-063 (marketplace atomic invariant) §결정 5 "기존 CI lint 보존 + 신규 lint follow-up" 표 가 작성 시점 sublayer enumeration 영역 으로 작동. 표 안 5 row 중 3 row 가 sublayer enumeration (PR-time CI / local advisory / local auto-rebase guidance), 2 row 가 atomic invariant 정보 (plugin.json ↔ CHANGELOG / plugin.json ↔ marketplace.json sync mechanism).

### 3 carrier 누적 마찰 evidence

| # | Story | Sublayer 도입 | ADR-063 §결정 5 본문 영향 |
|---|---|---|---|
| 1 | CFP-441 | PR-time CI (`scripts/check-version-bump-atomic.sh` + `version-bump-atomic-check.yml`) | ADR-063 §결정 5 본문 표 row append (3-file atomic 강제 row) |
| 2 | CFP-447 | local pre-push (advisory, opt-in) | ADR-063 §결정 5 본문 표 row append (local pre-push advisory row) |
| 3 | CFP-477 | local pre-push (auto-rebase guidance, opt-in env `PRE_PUSH_AUTO_REBASE=1`) | ADR-063 §결정 5 본문 표 row append (local pre-push auto-rebase guidance row) |

3회 누적 마찰 pattern:
- 신규 sublayer 도입 시 ADR-063 본문 직접 편집 의무
- sublayer 정보 (id / mechanism / stage / trigger_event / enforce_tier / file_path / env_opt_in_flag) 가 ADR-063 본문 표 의 비-structured cell 안 산재
- 4th / 5th sublayer 추가 시 동일 마찰 반복 — 표 row 추가 + 본문 cross-ref 업데이트

### 기존 SSOT boundary

| ADR | 영역 | 본문 vs registry |
|---|---|---|
| ADR-063 §결정 1 | 3-file atomic invariant (무엇) | 본문 SSOT |
| ADR-063 §결정 2 | PR ordering (어떻게 — sync 순서) | 본문 SSOT |
| ADR-063 §결정 5 | sublayer enumeration (어떻게 — defense layer) | **본문 SSOT** ← drift 영역 |
| ADR-063 §결정 9 | Amendment 1 ArchitectAgent §3.6 self-check | 본문 SSOT |
| ADR-063 §결정 11 | Amendment 2 description verbatim lint | 본문 SSOT |
| ADR-063 §결정 13 | Amendment 3 reactive scheduled detection | 본문 SSOT |

**Gap**: sublayer enumeration 만 registry pattern 으로 분리 가능 (4-layer defense 4번째 layer 가 본 ADR-075 sublayer registry — defense-in-depth meta-layer).

### kind:registry pattern 정합

기존 6 kind:registry entry (`docs/inter-plugin-contracts/MANIFEST.yaml`):
- label-registry / debate-protocol / evidence-check-registry / severity-propagation / parallel-dispatch-protocol-v1 + chain registries

모두 enumeration + lookup 영역. sibling sync 면제 (ADR-010 §결정 2). 본 sublayer registry 가 7번째 entry 로 자연스러운 fit.

## 결정

### 결정 1: 신규 ADR 분리 (ADR-063 amendment 미선택)

본 SSOT 분리 = **신규 ADR (ADR-075)** 로 codify. ADR-063 의 4번째 amendment 미선택 근거:

- ADR-063 amendment 1-3 = invariant 강화 방향 (proactive layer 추가 + reactive layer 추가). 본 변경 = **본문 cleanup + registry pattern 분리** — invariant 변경 0건.
- ADR-063 §결정 5 본문 표 의 sublayer enumeration 영역 만 registry 이전. atomic invariant 정보 (3-file atomic / plugin.json ↔ CHANGELOG sync / plugin.json ↔ marketplace.json sync) 는 ADR-063 본문 유지.
- 신규 ADR 분리 = SSOT boundary 명확 (ADR-063 = atomic invariant policy / ADR-075 = sublayer enumeration registry pattern).

### 결정 2: kind:registry schema 선택 (kind:contract 미선택)

본 registry = kind:registry. ADR-010 §결정 2 sibling sync 면제 정합:

- sublayer enumeration = lookup 영역 (`stage` / `mechanism` / `enforce_tier` 등 metadata 검색)
- consumer plugin (codeforge family 6 lane) 모두 wrapper plugin 의 sublayer 정의 참조 영역 외 — wrapper internal governance registry
- kind:contract 미선택 근거: contract 영역 = inter-plugin handoff (verdict packet / output schema 등 input/output 의무 schema), 본 registry = enumeration 만 — sibling sync 영역 외

MANIFEST.yaml `registries:` 블록 7번째 entry append.

### 결정 3: 3 existing rows backfill scope

ADR-063 §결정 5 본문 표 의 5 row 중 sublayer-relevant **3 row 만 registry 이전**:

| ID | Sublayer | CFP origin | Stage | Mechanism | Enforce tier |
|---|---|---|---|---|---|
| 1 | PR-time CI atomic | CFP-441 | pull_request event | `scripts/check-version-bump-atomic.sh` + `version-bump-atomic-check.yml` | blocking-on-pr |
| 2 | local pre-push advisory | CFP-447 | local pre-push hook | `templates/.claude/hooks/pre-push.sh.sample` (opt-in install) | advisory + `PRE_PUSH_BLOCKING=1` blocking 분기 |
| 3 | local pre-push auto-rebase guidance | CFP-477 | local pre-push hook | `templates/.claude/hooks/pre-push-auto-rebase.sh.sample` (opt-in env `PRE_PUSH_AUTO_REBASE=1`) | advisory abort + 4-line guidance |

ADR-063 §결정 5 본문 표 의 비-sublayer 2 row (`plugin.json ↔ CHANGELOG` / `plugin.json ↔ marketplace.json`) = ADR-063 본문 유지 (atomic invariant 정보 영역).

### 결정 4: registry field set

`docs/inter-plugin-contracts/defense-in-depth-sublayer-registry-v1.md` schema field set:

| Field | Type | 의무 | 설명 |
|---|---|---|---|
| `id` | int | 필수 | sublayer registry 안 unique id (1부터 sequential) |
| `name` | string | 필수 | sublayer 명 (예: "PR-time CI atomic" / "local pre-push advisory") |
| `cfp_origin` | string | 필수 | sublayer 도입 carrier Story key (예: `CFP-441`) |
| `stage` | enum | 필수 | `pre_commit` / `pre_push` / `pull_request_event` / `post_merge` / `scheduled_cron` |
| `mechanism` | string | 필수 | sublayer 작동 방식 1-line summary |
| `trigger_event` | string | 필수 | sublayer 발화 trigger (예: "git push" / "pull_request open" / "24h cron") |
| `enforce_tier` | enum | 필수 | `advisory` / `blocking-on-pr` / `blocking-on-merge` / `warning` (ADR-060 tier 정합) |
| `file_path` | list[string] | 필수 | sublayer artifact file path (script + workflow + hook sample 등) |
| `env_opt_in_flag` | string | optional | opt-in env var (예: `PRE_PUSH_AUTO_REBASE=1`) — opt-in sublayer 만 |
| `bypass_label` | string | optional | bypass channel label (ADR-024 Amendment 3 §결정 6.A family member) — blocking tier 만 의무 |
| `status` | enum | 필수 | `active` / `deprecated` / `superseded` |

minimal schema (id + name + cfp_origin 만) 미선택 근거: lookup 시 mechanism / trigger_event / enforce_tier 정보 필수 — sublayer 추가 결정 시 직접 컨텍스트 영역.

### 결정 5: ADR-063 §결정 5 본문 표 정정 형식

ADR-063 §결정 5 본문 표 정정 형식 = sublayer-relevant 3 row 의 `→ registry cross-ref` 단축 형식:

```markdown
### 결정 5: 기존 CI lint 보존 + 신규 lint follow-up

(... 본문 유지 ...)

| Lint | 현재 | 신규 (별도 carrier) |
|---|---|---|
| plugin.json ↔ CHANGELOG | `invariant-check` workflow | 그대로 |
| plugin.json ↔ marketplace.json | `check-marketplace-parity.sh` post-PR | pre-commit hook (local) 권장 |
| sublayer enumeration (defense-in-depth) | 부재 | **[defense-in-depth-sublayer-registry-v1](../inter-plugin-contracts/defense-in-depth-sublayer-registry-v1.md)** — id=1 PR-time CI atomic (CFP-441) / id=2 local pre-push advisory (CFP-447) / id=3 local pre-push auto-rebase guidance (CFP-477) |
```

**효과**: 향후 4th / 5th sublayer 추가 시 ADR-063 본문 영향 0건 — registry yaml row append + version PATCH/MINOR 만.

### 결정 6: 향후 sublayer 추가 절차

신규 sublayer (4th / 5th / ...) 도입 시 절차:

1. **carrier Story 생성** — `codeforge-improvement` label + sublayer 도입 motivation 명시
2. **registry row append** — `docs/inter-plugin-contracts/defense-in-depth-sublayer-registry-v1.md` 안 sublayer entry append (id sequential)
3. **MANIFEST.yaml version bump** — registry entry version PATCH / MINOR (schema 변경 없음 PATCH / 신규 field 추가 MINOR)
4. **ADR-063 본문 영향 0건** — §결정 5 본문 표 의 sublayer enumeration row 가 registry cross-ref 형식 이므로 본문 영향 없이 registry row append 만으로 sublayer 추가 완료

### 결정 7: sibling sync exemption rationale

본 registry = kind:registry. ADR-010 §결정 2 정합 — sibling sync 면제:

- enumeration / lookup 영역 (wrapper internal governance)
- inter-plugin handoff schema 영역 외 (consumer plugin 6 lane 참조 없음)
- sibling repo 안 mirror copy 의무 없음 — wrapper repo SSOT only

### 결정 8: Self-application — ratchet 검증

본 ADR-075 = 강화 방향 only:

- ADR-063 §결정 5 본문 표 sublayer enumeration 영역 의 registry pattern 분리 → 향후 sublayer 추가 마찰 감소 (강화 방향)
- 약화 방향 미해당 (sublayer 정의 약화 / boundary 이동 / scope 축소 모두 부재)
- ADR-058 §결정 5 sunset_justification = frontmatter 명시 (`N/A — permanent governance policy`)

ADR-064 self-application top-down ratchet 정합.

## 결과

### 긍정

- ADR-063 §결정 5 본문 표 sublayer enumeration 마찰 해소 (3회 누적 → 0건 향후)
- registry pattern 정합 (kind:registry 6 → 7 자연 확장)
- 향후 sublayer 추가 → registry row append 만으로 완료 (ADR-063 본문 영향 0건)
- SSOT boundary 명확 (ADR-063 = atomic invariant policy / ADR-075 = sublayer enumeration registry pattern)

### 부정 / Trade-off

- 신규 ADR + 신규 kind:registry file 도입 cost (1회 만)
- 향후 sublayer 추가 시 registry yaml row append + version bump 의무 (ADR-063 본문 편집 대비 낮은 cost)

### 영향 받는 영역

- ADR-063 §결정 5 본문 표 (3 row → registry cross-ref 형식)
- MANIFEST.yaml registries 블록 (6 → 7 entry)
- CLAUDE.md ADR-063 단락 cross-ref + Inter-plugin Contract 단락 kind:registry count update
- doc-locations.yaml (신규 ADR + 신규 registry row)
- section-ownership.yaml (필요 시 — Amendment 영역 review)

## 해소 기준

N/A — permanent governance policy.

본 registry 의 sunset 조건 미해당 — sublayer enumeration 영역 의 SSOT 분리 자체가 permanent 결정. registry schema field 변경 시 version bump (MINOR / MAJOR) 로 처리.

## 관련 파일

- [ADR-063](ADR-063-marketplace-atomic-invariant.md) — §결정 5 본문 표 sublayer enumeration source (정정 대상)
- `docs/inter-plugin-contracts/defense-in-depth-sublayer-registry-v1.md` — 신규 kind:registry SSOT
- `docs/inter-plugin-contracts/MANIFEST.yaml` — registries 블록 7번째 entry append
- `CLAUDE.md` — ADR-063 단락 + Inter-plugin Contract 단락 cross-ref
- [ADR-008](ADR-008-inter-plugin-contract-versioning.md) — kind:registry versioning policy
- [ADR-010](ADR-010-inter-plugin-contract-sibling-sync.md) — kind:registry sibling sync 면제
- [ADR-054](ADR-054-doc-only-story-fast-path.md) — Phase 1 + Phase 2 combined (single PR) 정합
