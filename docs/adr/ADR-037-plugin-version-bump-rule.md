---
adr_number: 37
title: Plugin version bump rule SSOT — Option β (Lenient + wrapper-coupling) + Option α (Conventional Commits)
status: Accepted
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
  - docs/adr/ADR-076-declarative-reconciliation-upgrade.md   # Amendment 1 cross-ref — atomic upgrade runtime carrier (§결정 8 runtime ratchet)
  - docs/inter-plugin-contracts/reconcile-protocol-v1.md     # Amendment 1 — atomicity_boundary_runtime ratchet (v1.3) + 0 drift invariant 검증 channel
  - docs/evidence-checks-registry.yaml                       # Amendment 1 mechanical enforcement — atomic-upgrade-zero-drift entry (ADR-040 Amd3 §결정 7 binding)
  - scripts/check-codeforge-version-drift.sh                 # Amendment 1 — 0 drift invariant 사후 검증 detect mechanism (--plugin 7회 invocation, CFP-262 기존 script reuse)
  - scripts/atomic-upgrade-7-plugins.sh                      # Amendment 1 — atomic upgrade 후 0 drift invariant 실 enforcement carrier (Phase 2, post-atomic gate)
related_stories:
  - CFP-261 (carrier)
  - CFP-259 (parent Epic)
  - CFP-262 (downstream — drift severity cross-reference)
  - CFP-744 (Amendment 1 carrier — Wave 2 Story-4, atomic upgrade 후 0 drift invariant)
is_transitional: false
amendments:
  - id: 1
    carrier_story: CFP-744
    date: 2026-05-16
    title: "Atomic upgrade 후 0 drift invariant (7-plugin family atomic upgrade 정책 명문화)"
    sunset_justification: "N/A — is_transitional: false (permanent governance policy, 해소 기준 = permanent policy). Amendment 1 = ratchet 강화 방향 (기존 detect-only drift check 위에 atomic upgrade 후 0 drift 의무 신설 — scope 확장, 약화 0). ADR-058 §결정 5 정합 — 강화 방향 amendment sunset_justification 면제 사유 (permanent policy 자기 강화)."
mechanical_enforcement_actions:
  # ADR-040 Amendment 3 §결정 7.A schema (list[object]: action / status / target_section [+ optional progress_note]).
  # action name = docs/evidence-checks-registry.yaml entry name verbatim. governance category → mechanical action binding 의무.
  # FIX Iter 2 (Codex TP#2 F-P1 verified-true): 旧 action `marketplace-parity` = 의미 mismapping 정정.
  # marketplace-parity = wrapper-side publishing-time mirrored-field parity (plugin.json ↔ marketplace.json) — Amendment 1
  # consumer-side runtime 0-drift invariant 과 의미 disjoint, mechanically enforce 불가 (ADR-040 Amd3 §결정 7 위반).
  # → 신규 전용 entry `atomic-upgrade-zero-drift` 로 정정 (consumer-side installed `pin` ↔ marketplace SSOT post-atomic drift 0).
  - action: atomic-upgrade-zero-drift
    status: deferred-followup
    progress_note: "ADR-037 Amendment 1 '0 drift invariant' 의 전용 mechanical action. detect mechanism = scripts/check-codeforge-version-drift.sh `--plugin <codeforge-N>` 7회 invocation (F-002 옵션 A, codex/superpowers 제외 — CFP-262 기존 script 실재). 실 enforcement carrier = Phase 2 scripts/atomic-upgrade-7-plugins.sh post-atomic 0-drift gate (drift > 0 → 전체 7 plugin atomic rollback). status: deferred-followup — Phase 1 = registry declare (detect mechanism 실재) / Phase 2 = atomic-upgrade-7-plugins.sh + workflow self-app 시점 Active 전환 (bootstrap-labels-precondition 패턴 동형). current_tier: warning (ADR-060 §결정 5 첫 도입). cross-validation only (enforcing 아님): marketplace-parity = wrapper-side publishing-time mirrored-field parity (plugin.json↔marketplace.json) — Amendment 1 consumer-side runtime 0-drift invariant 과 의미 disjoint, NOT the invariant 자체 (cross-ref only)."
    target_section: "Amendment 1"
---

# ADR-037: Plugin version bump rule SSOT — Option β + α

## 상태

`Accepted` (2026-05-08, CFP-261 carrier — Phase 1 PR #267 + Phase 2 PR #270 merged. Self-application 첫 적용 = wrapper plugin 5.3.0 → 5.4.0 MINOR bump 본 PR).

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

## Amendment 1 — Atomic upgrade 후 0 drift invariant (CFP-744, 2026-05-16)

> **Carrier**: CFP-744 (Epic CFP-699 Wave 2 Story-4 — 7 plugin family atomic upgrade A2). **Source directive** (Epic Issue #699 §1 WHY verbatim, 사용자 2026-05-14 KST): *"consumer 에서 버전을 한 곳에만 잘 유지하고 있다면 어긋날 일도 없고."* 본 Amendment = 이 directive 의 mechanical 정책 박제.

### Amendment 1 컨텍스트

base ADR-037 (결정 1-5) 은 plugin version **bump 기준** SSOT 를 정의했다. `scripts/check-codeforge-version-drift.sh` (CFP-262) 는 drift 를 **detect only** — drift 검출 시 hard-stop blocking 하나, drift 자체가 발생하지 않도록 강제하는 invariant 는 부재했다. 사용자 directive ("버전을 한 곳에만 잘 유지하고 있다면 어긋날 일도 없고") 는 "drift 발생 후 차단" 이 아니라 **"drift 자체가 구조적으로 발생 불가능"** 을 요구한다. CFP-743 (Wave 2 Story-3, MERGED) 이 per-plugin runtime SSOT (`scripts/codeforge-upgrade.{sh,ps1}` + UpgradeAgent) 를 완성했고, CFP-744 = per-family (7 plugin) atomic upgrade runtime 신설 시점.

### Amendment 1 결정

**결정 A1-1 — 0 drift invariant 정의 (정책 명문화)**

> **codeforge family 7 plugin (wrapper `codeforge` + 6 lane plugin `codeforge-{requirements,design,review,develop,test,pmo}`) 은 atomic upgrade `--apply` 완료 직후 version `pin` drift 가 0 (none) 이어야 한다.** drift > 0 검출 = atomic upgrade transaction 실패 분류 → 전체 7 plugin 이전 version `pin` 으로 atomic rollback (per-family transaction boundary, Epic EPIC-AC-3 "부분 실패 시 전체 rollback" verbatim).

본 invariant 의 의미: version 의 단일 진실원천(marketplace SSOT) 으로부터 7 plugin 이 atomic 하게 sync 되면, sync 직후 상태에서 drift 가 존재할 **구조적 가능성 자체가 없다**. drift 가 존재한다는 것 = atomic transaction 이 미완결 (= 실패) 이라는 신호. 따라서 0 drift 는 검증 대상이 아니라 **transaction 완결의 정의 자체** — "버전을 한 곳에만 잘 유지" (marketplace SSOT 단일 origin + atomic sync) 가 성립하면 "어긋날 일도 없고" (post-atomic drift 0) 가 자동 따라온다.

**결정 A1-2 — 검증 scope = codeforge family 7 plugin 한정 (codex / superpowers 제외)**

`scripts/check-codeforge-version-drift.sh` `PLUGIN_MARKETPLACE` map = **9 plugin** (codeforge family 7 + `codex` openai-codex/marketplace + `superpowers` claude-plugins-official/marketplace). `codex` / `superpowers` 는 **외부 marketplace** = codeforge atomic upgrade 대상이 아니다 (독립 lifecycle). 무필터 9-plugin 검사 시 codex/superpowers 독립 drift 가 **false transaction-fail → 불필요 전체 rollback** 을 유발한다. 따라서 0 drift invariant 검증 scope = **codeforge family 7 plugin 한정** — codex/superpowers 제외 보장 의무 (false rollback = 0).

**결정 A1-3 — 검증 mechanism = `--plugin <name>` 7회 invocation (F-002 옵션 A 채택, drift script 변경 0)**

0 drift invariant 사후 검증 = `scripts/atomic-upgrade-7-plugins.sh` 가 `bash scripts/check-codeforge-version-drift.sh --plugin <codeforge-N>` 를 7-family 명단 (`codeforge` / `codeforge-requirements` / `codeforge-design` / `codeforge-review` / `codeforge-develop` / `codeforge-test` / `codeforge-pmo`) 으로 **7회 invocation** 후 종합. **`check-codeforge-version-drift.sh` 변경 0** (`--plugin` filter 는 line 62 에 이미 존재 = contract-sanctioned scoping primitive). drift script 에 `--family` flag 신설 (옵션 B) 미채택 — 매 세션 실행되는 SSOT drift gate (CLAUDE.md "세션 개시 의무") 의 mutation 은 caller-side scoping 으로 충분히 회피 가능한 regression risk (Mapper 보수 변호 + ADR-064 minimal-change 정합). 7회 invocation 의 7-name 명단 자체가 codex/superpowers 를 구조적으로 배제 (결정 A1-2 보장).

**결정 A1-4 — base ADR-037 surface table 와의 관계**

본 Amendment 1 은 base 결정 1 surface table (12 surface MAJOR/MINOR/PATCH 분류) 을 **변경하지 않는다**. atomic upgrade 는 version *bump* 가 아니라 version *`pin` sync* (consumer 측 installed `pin` ← marketplace SSOT) — bump 기준 SSOT (base) 와 sync invariant (Amendment 1) 는 직교 영역. 7 plugin 자체의 plugin.json bump 결정은 여전히 base 결정 1-5 SSOT.

**결정 A1-5 — reconcile-protocol-v1 §4.3 (d) ratchet 동반**

본 Amendment 1 = reconcile-protocol-v1 v1.2 → **v1.3** MINOR bump (§4.3 (d) trigger 발동, `atomicity_boundary_runtime_v1` per_plugin → `atomicity_boundary_runtime_future` family_7_plugin runtime catch-up). 의미 invariant `atomicity_boundary_semantic_invariant: family_7_plugin_atomic` = ADR-016 §결정 1 SSOT, **변경 0** (runtime catch-up only — 의미 invariant 변경 시 ADR-016 §결정 1 변경 trigger 별도 carrier 의무). T3 trigger (결정 2) 미발동 — base ADR-037 surface 무변경 (결정 A1-4) + family invariant ADR (ADR-016) supersede 0.

### Amendment 1 mechanical enforcement binding (ADR-040 Amendment 3 §결정 7.A)

- **action**: `atomic-upgrade-zero-drift` (evidence-checks-registry entry verbatim, current_tier: warning, status: deferred-followup, detect_command: `scripts/check-codeforge-version-drift.sh` `--plugin <codeforge-N>` 7회 invocation)
- **binding 근거**: `atomic-upgrade-zero-drift` entry 가 Amendment 1 "0 drift invariant" 자체를 mechanically enforce — consumer-side installed 7-plugin version `pin` ↔ marketplace SSOT post-atomic drift 0. detect mechanism = 기존 `scripts/check-codeforge-version-drift.sh` (CFP-262, 실재) `--plugin` 7회 종합 (F-002 옵션 A, codex/superpowers 제외 구조적 배제). 실 enforcement carrier = Phase 2 `scripts/atomic-upgrade-7-plugins.sh` post-atomic 0-drift gate. status: deferred-followup (Phase 1 = registry declare / Phase 2 = script + workflow self-app 시점 Active 전환, `bootstrap-labels-precondition` 패턴 동형).
- **marketplace-parity 와의 의미 분리 (FIX Iter 2 — Codex TP#2 F-P1 verified-true)**: `marketplace-parity` entry 는 **wrapper-side publishing-time** mirrored field (name/version/description/author) cross-repo parity (plugin.json ↔ marketplace.json) 를 검증 — Amendment 1 의 **consumer-side runtime** 0-drift invariant 과 의미 **disjoint**. marketplace-parity 는 Amendment 1 을 mechanically enforce 하지 못함 (초기 mismapping = ADR-040 Amendment 3 §결정 7 위반 — action 이 §결정 enforce 의무 불충족, FIX Iter 2 로 정정). marketplace-parity = `related_cross_validation_evidence` cross-ref 로만 강등 (enforcing action 아님).
- **retroactive 면제**: 본 Amendment 1 = ADR-040 Amendment 3 (§결정 7.C) 발효 후 신설 amendment → `mechanical_enforcement_actions[]` 의무 적용 대상 (frontmatter 부착 + 전용 entry 정정 완료).

### Amendment 1 영향

- **wrapper plugin (codeforge)**: Phase 2 `scripts/atomic-upgrade-7-plugins.sh` 신설 = 선택 setup script 추가 → base 결정 1 (i) Bootstrap script MINOR. Phase 1 (본 PR) = ADR Amendment (additive) + contract MINOR — base 결정 1 (h) additive amendment = MINOR signal (plugin.json bump = Phase 2 carrier).
- **6 lane plugin**: 영향 0 (atomic upgrade = version `pin` sync, lane plugin 자체 surface 무변경).
- **consumer**: atomic upgrade 실행 시 7 plugin `pin` sync 후 drift 0 자동 보증 (사용자 directive mechanical 명문화 완성). consumer-guide upgrade troubleshooting cross-ref = Phase 2.

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

## 해소 기준

N/A — permanent policy (`is_transitional: false`). base 결정 1-5 + Amendment 1 (0 drift invariant) 모두 permanent governance — codeforge plugin family 가 deprecate 되지 않는 한 영구 유효. Amendment 는 강화 방향만 허용 (ADR-058 §결정 5 + ADR-064 top-down self-application). Amendment 1 = ratchet 강화 (detect-only → atomic 후 0 drift 의무 신설, scope 확장) — sunset_justification 면제 (frontmatter `amendments[].sunset_justification` 명시).



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
