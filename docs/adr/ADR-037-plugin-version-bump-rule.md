---
adr_number: 37
title: Plugin version bump rule SSOT — Option β (Lenient + wrapper-coupling) + Option α (Conventional Commits)
status: Proposed
category: governance
date: 2026-05-08
related_files:
  - .claude-plugin/plugin.json
  - templates/github-workflows/check-plugin-version-bump.yml
  - docs/orchestrator-playbook.md
  - docs/consumer-guide.md
  - docs/adr/ADR-008-inter-plugin-contract-versioning.md
  - docs/adr/ADR-009-wrapper-only-decomposition.md
  - docs/adr/ADR-016-marketplace-registration-policy.md
related_stories:
  - CFP-261 (carrier)
  - CFP-259 (parent Epic)
  - CFP-262 (downstream — drift severity cross-reference)
---

# ADR-037: Plugin version bump rule SSOT — Option β + α

## 상태

`Proposed` (2026-05-08, CFP-261 carrier — Phase 2 PR merge 후 `Accepted` 전환).

## 컨텍스트

CFP-259 Epic Wave 1 둘째 작업. codeforge plugin family (wrapper + 6 lane plugin = 7 plugin) 의 `.claude-plugin/plugin.json` `version` field bump 기준 SSOT 부재.

**현재 상태**:

- ADR-016 가 marketplace mirror 의무화 (`name`·`version`·`description`·`author` 4 mirrored 필드 → marketplace.json sync)
- ADR-008 가 inter-plugin contract SemVer 강제 (`review_verdict` / `requirements_output` / `design_output` / `develop_output` / `test_verdict` / `pmo_output` 6 contract)
- 7 plugin 의 현재 version = wrapper 5.3.0 + 6 lane plugin 자체 SemVer

**부재**:

- 어떤 변경이 plugin major / minor / patch 인지 SSOT 없음
- bump 결정이 author 재량 → 일관성 없음
- consumer 가 update 필요한지 판단 불가

**선택지 도출 과정** (Codex Round 1 + Claude options + 사용자 confirm, 2026-05-08):

- Codex Option 1 (Strict) → rejected (internal dogfood 단계 noise 과도)
- Codex Option 2 (Lenient) → rejected (wrapper coupling gap)
- Codex Option 3 (Family Train) → rejected (over-coupled)
- Claude Option β (Lenient + Wrapper-coupling) ✅ 채택
- Claude Option α (Conventional Commits CI) ✅ 채택 (β 보강)

## 결정

### 결정 1: Option β core rule (Lenient base, 12 surface category)

| Surface | MAJOR | MINOR | PATCH |
|---|---|---|---|
| (a) Agent file | 삭제 / 역할 재정의 | 추가 | minor edit |
| (b) Skill file | 삭제 / redefine | 추가 | minor edit |
| (c) Hook script | 삭제 / required hook 추가 / behavior break | 선택 hook 추가 | config-only |
| (d) Template (workflow / Form) | required workflow 추가 / story schema break | 선택 workflow 추가 / Form 추가 / additive schema | comments only |
| (e) Inter-plugin contract MAJOR (per ADR-008) | 해당 plugin (producer / consumer) MAJOR | — | — |
| (f) Inter-plugin contract MINOR (per ADR-008) | — | 해당 plugin MINOR | — |
| (g) CLAUDE.md SSOT semantic | 기존 artifact invalidate 시 | additive guidance | typo / clarity |
| (h) ADR (new / amend / supersede) | binding migration 동반 | 새 ADR / additive amendment | editorial fix |
| (i) Bootstrap script | 기존 install 실패 유도 | 선택 setup step | comments / help |
| (j) Slash command | 삭제 / behavior break | 추가 | wording / help |
| (k) Dependency requirement | 하드 minimum 상승 | 선택 새 tool 지원 | docs wording |
| (l) Marketplace mirrored field | — | description / author 변경 | typo |

**Wrapper plugin 적용 예외**: ADR-009 invariant 에 의해 wrapper agent 0개 — (a) 행은 N/A. 6 lane plugin 만 (a) 적용.

### 결정 2: Wrapper-coupling trigger 3종 (β core 추가, wrapper-only)

wrapper plugin (codeforge) 은 (1)-(12) 자체 surface 변경 외에 다음 3 trigger 시 추가 MAJOR:

- **T1 contract MAJOR**: 어느 lane plugin 의 inter-plugin contract MAJOR 발생 시 → wrapper plugin 도 MAJOR. 근거: wrapper CLAUDE.md "## Inter-plugin Contract" 섹션이 모든 contract reference + sibling sync 의무 (ADR-010).
- **T2 agent topology**: 어느 lane plugin 의 agent file 삭제 또는 역할 재정의 발생 시 → wrapper plugin 도 MAJOR. 근거: wrapper "Development Agent Team" 표 + 책임 매트릭스 + decision table 영향.
- **T3 family invariant ADR**: family-wide invariant ADR (ADR-009 wrapper-only / ADR-016 marketplace mirror / ADR-024 branch policy / ADR-008 contract SemVer / ADR-037 본 ADR) supersede 시 → wrapper plugin MAJOR. 근거: family-wide invariant 변경은 모든 plugin 의 운영 의미 변경.

**Trigger boundary** (over-trigger 방지):
- Lane plugin 의 internal refactor (preset 추가 / 작은 prompt edit / template wording) 는 T1/T2/T3 trigger 안됨
- T1/T2/T3 외 변경은 wrapper 자체 surface 변경 ((a)-(l) 행) 에 의해서만 wrapper bump
- 6 lane plugin 의 자체 bump 는 wrapper 와 독립 (lane 의 own surface 변경에만 반응)

### 결정 3: Option α (Conventional Commits enforcement layer)

모든 plugin (wrapper + 6 lane plugin) 의 commit message 형식 의무:

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

- `feat!:` 또는 footer `BREAKING CHANGE:` → MAJOR signal
- `feat:` → MINOR signal
- `fix:` / `docs:` / `chore:` / `style:` / `refactor:` / `test:` → PATCH signal

**`templates/github-workflows/check-plugin-version-bump.yml` (Phase 2 spillover)** 가 PR 단계에서:

1. PR commit messages 의 prefix 추출 + type 분류 → `commit_signal`
2. PR diff 의 변경 파일 → 결정 1 surface table mapping → `diff_signal`
3. T1/T2/T3 wrapper-coupling trigger 검사 → `coupling_signal` (wrapper plugin 만)
4. PR base vs head 의 `plugin.json` `version` field bump 종류 추출 → `actual_bump`
5. `max(commit_signal, diff_signal, coupling_signal) == actual_bump` 검사 → 위반 시 fail-closed

### 결정 4: ADR-008 cross-reference

본 ADR 의 (e)/(f) 행 (inter-plugin contract → plugin propagation 룰) 은 ADR-008 와 strictly cross-reference:

- ADR-008 의 contract MAJOR 정의 = 필수 필드 변경 / type 변경 / enum 제거 / 흐름 방향 변경
- 본 ADR (e) 행 = "ADR-008 contract MAJOR 발생 시 producer/consumer plugin MAJOR"
- 본 ADR (f) 행 = "ADR-008 contract MINOR 발생 시 producer/consumer plugin MINOR"
- ADR-008 supersede 발의 시 → 본 ADR (e)/(f) 행 재검토 의무 + T3 trigger 작동 (family invariant ADR supersede)

### 결정 5: Migration (forward-only)

- 기존 plugin version 그대로 — 7 plugin 모두 현재 version 유지
- 본 ADR Accepted 후 첫 PR 부터 Conventional Commits + bump 검사 적용
- 기존 commit message 가 형식 위반해도 historical record 무 retroactive 적용 (commit 재작성 금지)
- 7 plugin 자체 첫 적용 시점 = 각 plugin 의 next bump 시점 (각 plugin maintainer 자체 PR 로 적용)
- `release-please` bot 도입 = 별도 PR / CFP (Phase 2 spillover beyond CFP-261)

## 결과

### 긍정

- plugin SemVer 기준 명확화 → consumer 가 update 필요성 판단 가능
- Conventional Commits CI 강제 → bump 결정의 mechanical 검사 (drift 방지)
- Wrapper-coupling trigger 3종 → wrapper docs 가 lane plugin 변경에 자동 반응
- ADR-008 (contract SemVer) 와 cross-reference 정합 → contract / plugin 두 SemVer 영역 명확 분리
- Lenient base → MAJOR noise 최소화 (internal dogfood 단계 적합)

### 부정 / Trade-off

- Conventional Commits 학습 곡선 → 잘못된 prefix 시 CI 실패 (PR 재작성 부담)
- Wrapper-coupling trigger 3종 → wrapper bump 결정이 conditional (CI 검사 복잡도 증가)
- Phase 1 단계 = manual bump + CI 검사. Phase 2 spillover (release-please bot) 도입 전까지 manual 작업 잔존
- 기존 commit message 형식 위반 historical record → grep / audit 시 mixed pattern

### 영향

- **wrapper plugin (codeforge)**: 본 ADR 자체 Accepted 가 family invariant ADR 신설이라 T3 trigger 작동 → wrapper plugin 자체 next bump 시 MAJOR (5.3.0 → 6.0.0)
- **6 lane plugin**: 각자 next bump 시 본 ADR 적용. 적용 시점 = 각 plugin 의 own surface 변경이 발생하는 PR
- **consumer**: consumer-guide 에 본 ADR cross-reference 추가 + consumer 자체 plugin 작성 시 본 ADR 권장 (mandatory 아님)
- **CFP-262 (downstream)**: drift severity 분류 (MAJOR=hard-stop / MINOR=warn / PATCH=info) 가 본 ADR 의 surface table cross-reference

## 다이어그램

```
PR open
   │
   ├── Conventional Commits prefix 추출 → commit_signal
   ├── PR diff 분석 → 결정 1 surface table → diff_signal
   ├── (wrapper PR 만) T1/T2/T3 검사 → coupling_signal
   ├── plugin.json version bump 추출 → actual_bump
   │
   ▼
expected = max(commit_signal, diff_signal, coupling_signal)
   │
   ├── if actual_bump == expected → PASS
   │
   └── else → FAIL with explanation
        ├── "expected MAJOR but got MINOR — diff includes (a) agent file deletion"
        └── "expected PATCH but got MINOR — no signals matched MINOR threshold"
```

## 관련 파일

- [`.claude-plugin/plugin.json`](../../.claude-plugin/plugin.json) — wrapper plugin (현재 5.3.0)
- `templates/github-workflows/check-plugin-version-bump.yml` — Phase 2 spillover (본 PR 에는 부재)
- [`docs/orchestrator-playbook.md`](../orchestrator-playbook.md) — Conventional Commits 안내 섹션 추가
- [`docs/consumer-guide.md`](../consumer-guide.md) — consumer 자체 plugin 작성 가이드
- [`docs/adr/ADR-008-inter-plugin-contract-versioning.md`](ADR-008-inter-plugin-contract-versioning.md) — 결정 1 (e)/(f) propagation
- [`docs/adr/ADR-016-marketplace-registration-policy.md`](ADR-016-marketplace-registration-policy.md) — 결정 1 (l) marketplace mirror
- [`docs/adr/ADR-009-wrapper-only-decomposition.md`](ADR-009-wrapper-only-decomposition.md) — 결정 1 (a) wrapper agent 0개 적용 예외
- [Internal-docs Change Plan: CFP-261](https://github.com/mclayer/codeforge-internal-docs/blob/main/wrapper/change-plans/cfp-261-plugin-version-bump-rule.md)
- [Internal-docs Epic spec: CFP-259](https://github.com/mclayer/codeforge-internal-docs/blob/main/wrapper/specs/2026-05-08-cfp-259-plugin-version-key-governance-epic-design.md)
