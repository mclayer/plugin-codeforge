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
  - .github/workflows/invariant-check.yml                    # Amendment 2 — line 37 "wrapper self-app = 후속 follow-up CFP" 박제 (CONSUMER_ONLY_WORKFLOWS 등재) = 본 Amendment 가 실현하는 deferred self-app, S2 가 등재 해제
  - docs/adr/ADR-118-monorepo-consolidation.md               # Amendment 2 — 9-plugin 모노레포 구조 (wrapper root + plugins/codeforge-*/) surface-table path 적응 근거
  - docs/adr/ADR-063-marketplace-atomic-invariant.md         # Amendment 2 — §결정 18-B 9-plugin MAJOR atomic cross-check 정합 + §결정 19 Tier 분리
  - docs/adr/ADR-092-changelog-ssot-location.md              # Amendment 2 — §결정 3 wrapper CHANGELOG 동결 → 새 게이트 CHANGELOG 비의존 명시 근거
  - docs/adr/ADR-054-doc-only-story-fast-path.md             # Amendment 2 — ADR Amendment(신규 ADR 아님) + src/tests 무변경 = doc-only fast-path 분류 근거
related_stories:
  - CFP-261 (carrier)
  - CFP-259 (parent Epic)
  - CFP-262 (downstream — drift severity cross-reference)
  - CFP-744 (Amendment 1 carrier — Wave 2 Story-4, atomic upgrade 후 0 drift invariant)
  - CFP-2310 (parent Epic — version-bump self-application 모노레포-aware v2 게이트)
  - CFP-2311 (Amendment 2 carrier — Epic CFP-2310 S1, 모노레포 self-application boundary + diff_signal/coupling v2 모델)
is_transitional: false
amendments:
  - id: 1
    carrier_story: CFP-744
    date: 2026-05-16
    title: "Atomic upgrade 후 0 drift invariant (7-plugin family atomic upgrade 정책 명문화)"
    sunset_justification: "N/A — is_transitional: false (permanent governance policy, 해소 기준 = permanent policy). Amendment 1 = ratchet 강화 방향 (기존 detect-only drift check 위에 atomic upgrade 후 0 drift 의무 신설 — scope 확장, 약화 0). ADR-058 §결정 5 정합 — 강화 방향 amendment sunset_justification 면제 사유 (permanent policy 자기 강화)."
  - id: 2
    carrier_story: CFP-2311
    date: 2026-06-16
    title: "모노레포-aware self-application + v2 모델 (diff_signal surface-table 모노레포 path 적응 + wrapper-coupling T1/T2/T3 형식화 + 공유 파일 귀속 SSOT + self-application boundary 실현 + fix:-PR 면제 경계 + warning-first tier)"
    direction: strengthen
    sunset_justification: "N/A — is_transitional: false (permanent governance policy). Amendment 2 = ratchet 강화 방향 only — (1) self-application boundary 실현 (§결정 5 forward-only deferred → wrapper self-apply, scope 확장) (2) diff_signal surface-table 신설 + 모노레포 path 적응 (v1 commit_signal-only 위에 변경 파일 → 기대 bump 매핑 layer 추가, invariant 강도 상승) (3) wrapper-coupling T1/T2/T3 형식화 (§결정 2 의도 mechanical 형식화) (4) 공유 파일 귀속 SSOT (false-positive 차단 = 정밀도 강화). β lenient 비대칭 (over-bump PASS / under-bump FAIL) 보존 — dogfood noise 회귀 차단은 약화 아님 (ADR-037 본래 Lenient base 의 의도된 비대칭 유지). 약화 요소 0건. ADR-058 §결정 5 약화 방향 발의 차단 logic 통과 (self-application boundary 후퇴 / diff_signal surface-table 제거 / coupling trigger 약화 / 공유 파일 귀속 과확장 = sunset_justification 3-tuple 의무)."
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

## Amendment 2 — 모노레포-aware self-application + v2 모델 (CFP-2311, 2026-06-16)

> **Carrier**: CFP-2311 (Epic CFP-2310 S1 — version-bump self-application 모노레포-aware v2 게이트). **Source directive**: consumer debut (mctrader-data) escalation #2306 — ADR-037 §결정 3 version-bump 강제가 plugin repo 자신에는 미배포된 self-application 갭. 본 Amendment = ADR-118 모노레포 통합 후 9-plugin 구조에서 §결정 5 forward-only deferred self-application 을 실현하고, 기존 v1 (`commit_signal` + `actual_bump` only) 위에 v2 (`diff_signal` surface-table + `coupling_signal` T1/T2/T3) 모델을 형식화한다. **본 Amendment = 설계 결정 SSOT (선언) — 실 게이트 wire (workflow + lint script) 는 S2 (#2312) carrier (Phase 2).**

### Amendment 2 컨텍스트 — 측정된 갭 (origin/main 실측, #2306 evidence 정정)

| 항목 | 실측 | 판정 |
|---|---|---|
| `check-plugin-version-bump.yml` | `.github/workflows/` 부재, `templates/github-workflows/` 에만 존재 | 진짜 self-application 갭 (Arc A) |
| `invariant-check.yml` line 37 | `# CFP-261 / ADR-037 — check-plugin-version-bump.yml Phase 2 v1 = consumer-only initial. wrapper self-app = 후속 follow-up CFP.` 박제 (`CONSUMER_ONLY_WORKFLOWS` 등재) | 본 Amendment = 그 예약 후속 실현 |
| v1 template 로직 | `commit_signal` (Conventional Commits) + `actual_bump` (plugin.json before/after) 만 — `diff_signal` surface-table + `coupling_signal` 미구현 ("Phase 2 v2 follow-up reminder" step 명시) | v2 모델 = 본 Amendment 형식화 영역 |
| 모노레포 구조 | wrapper root `.claude-plugin/plugin.json` (`codeforge` 6.24.0) + 8 lane `plugins/codeforge-*/.claude-plugin/plugin.json` (독립 version) | v1 trigger `paths:` 가 `plugins/**` 미포함 — lane-only PR 미감지 |

### Amendment 2 결정

#### 결정 A2-1 — self-application boundary 실현 (§결정 5 forward-only deferred → wrapper self-apply)

§결정 5 는 "7 plugin 자체 첫 적용 시점 = 각 plugin 의 next bump 시점" 으로 self-application 을 **forward-only deferred** 했고, `invariant-check.yml` line 37 이 "wrapper self-app = 후속 follow-up CFP" 로 박제했다. 본 결정 A2-1 = **그 예약 후속 실현 선언**:

> **codeforge wrapper plugin (`codeforge`) 은 ADR-037 version-bump 정합 게이트를 자기 자신에게 self-apply 한다.** wrapper root `.claude-plugin/plugin.json` 변경을 동반하는 모든 PR 은 `commit_signal` + `diff_signal` + `coupling_signal` 의 `max` 와 `actual_bump` 정합 검사 대상이다 (β lenient 비대칭 — 결정 A2-5).

- self-application = `templates/github-workflows/check-plugin-version-bump.yml` 의 v2 갱신 + `.github/workflows/check-plugin-version-bump.yml` self-app copy 신설 (S2 carrier, `invariant-check.yml` `CONSUMER_ONLY_WORKFLOWS` 등재 해제).
- 8 lane plugin self-application = wrapper 단일 워크플로 + 9-plugin matrix 평가 (결정 A2-2) — lane 별 별도 워크플로 신설 0 (모노레포 단일 게이트 SSOT).
- 본 Amendment 자체 (`archive/adr/ADR-037-*.md` 만 변경) = self-application 첫 dogfood 사례: `commit_signal=none` (결정 A2-6) + `diff_signal=none` (결정 A2-3 `archive/**` 비귀속) + `actual_bump=none` → β lenient PASS (no-bump 정상).

#### 결정 A2-2 — 모노레포 9-plugin surface scope 구분 (ADR-118 path 적응)

§결정 1 surface table 의 12 surface category 는 단일-repo 시대 wrapper-root 경로 가정이었다. ADR-118 모노레포 통합 후 변경 파일 → 기대 bump 매핑은 **귀속 plugin 별로 분리 평가**된다:

| Scope | 경로 | 귀속 plugin | bump 평가 대상 plugin.json |
|---|---|---|---|
| **wrapper root surface** | `.claude-plugin/plugin.json`, `scripts/**`, `templates/**`, `skills/**`, `hooks/**`, `commands/**`, `agents/**`, `docs/**`, `CLAUDE.md` | wrapper (`codeforge`) only | `.claude-plugin/plugin.json` (root) |
| **lane surface** | `plugins/<lane>/**` | 해당 lane plugin only | `plugins/<lane>/.claude-plugin/plugin.json` |

- PR diff 가 wrapper root surface + lane surface 를 **동시** 건드리면 → 각 scope 별 독립 surface-table 평가 (wrapper 1개 + 영향 lane N개 = 최대 9 plugin 동시 평가). 단 wrapper↔lane 결합 시 coupling 전파 = 결정 A2-4 적용.
- `agents/**` 행: wrapper `agents/` = ADR-009 invariant 로 0개 (실측: `agents/*.md` count 0) → wrapper surface (a) 행은 N/A (§결정 1 "Wrapper plugin 적용 예외" 보존). lane agent = `plugins/<lane>/agents/**` 로 해당 lane (a) 행 적용.

#### 결정 A2-3 — 공유 파일 귀속 SSOT (false-positive 차단 — 산업계 모노레포 함정 동형)

모노레포 단일 워크플로가 전 plugin 을 과확장 평가하면 (예: `docs/` 변경 → 8 lane 전부 bump 요구) false-positive 폭증 — 산업계 모노레포 monorepo-wide bump 함정과 동형. **귀속 SSOT (closed mapping)**:

| 경로 glob | 귀속 plugin | 비고 |
|---|---|---|
| `.claude-plugin/plugin.json` | wrapper only | wrapper root manifest |
| `scripts/**` | wrapper only | wrapper-root 공유 스크립트 (lane 은 `plugins/<lane>/scripts/**`) |
| `templates/**` | wrapper only | wrapper-root 템플릿 (consumer 배포 SSOT) |
| `skills/**` | wrapper only | wrapper-root skill |
| `hooks/**` | wrapper only | wrapper-root hook |
| `commands/**` | wrapper only | wrapper-root slash command |
| `agents/**` | wrapper only | ADR-009 invariant 로 실질 0개 (N/A) |
| `CLAUDE.md` | wrapper only | wrapper-root SSOT (lane 은 `plugins/<lane>/CLAUDE.md`) |
| `docs/**` | wrapper only | wrapper-root 문서 |
| `archive/**` | **비귀속 (exempt)** | ADR/legacy 동결 — 어느 plugin 의 runtime surface 도 아님 (결정 A2-6 면제 근원) |
| `plugins/<lane>/**` | 해당 `<lane>` only | lane self-contained 경로 (ADR-118 D3 — `plugins/<name>/` ↔ plugin.json name 1:1) |
| `.github/**`, `marketplace.json` 등 repo-meta | 비귀속 (별 게이트) | version-bump 게이트 surface 아님 — `invariant-check` / `marketplace-parity` 등 별 채널 |

**과확장 금지 invariant**: 변경 파일이 `plugins/<lane>/**` 에만 있으면 wrapper bump 요구 0 (역도 동일 — wrapper root surface 변경이 lane bump 요구 0, 단 coupling 전파 결정 A2-4 예외). 귀속 미정 경로 (closed mapping 누락) = fail-closed (= wrapper 귀속 보수 평가 또는 명시 exempt 등재 의무, silent skip 금지 — ADR-083 fail-closed-unknown 정합). 단 `archive/**` 는 명시 exempt (위 표) — runtime surface 아님.

#### 결정 A2-4 — wrapper-coupling T1/T2/T3 형식화 (§결정 2 모노레포 전파 규칙)

§결정 2 의 T1/T2/T3 의도 (wrapper docs 가 lane plugin 변경에 자동 반응) 를 모노레포 단일-PR 환경에서 **bump 전파 규칙**으로 형식화한다. §결정 2 원문 (T1 contract MAJOR / T2 agent topology / T3 family invariant ADR supersede) 보존 + 모노레포 경로 차원 추가:

| Trigger | 발동 조건 (lane surface 변경) | wrapper bump 전파 | 모노레포 path signal |
|---|---|---|---|
| **T1 contract MAJOR** | 어느 `plugins/<lane>/**` inter-plugin contract MAJOR (ADR-008) | wrapper MAJOR | `plugins/*/` contract 파일 + wrapper `CLAUDE.md` "Inter-plugin Contract" 참조 변경 동반 |
| **T2 agent topology** | 어느 `plugins/<lane>/agents/*.md` 삭제 또는 역할 재정의 | wrapper MAJOR | `plugins/*/agents/*.md` 삭제/redefine diff |
| **T3 family invariant ADR** | family invariant ADR (ADR-009 / ADR-016 / ADR-024 / ADR-008 / ADR-037) **supersede** | wrapper MAJOR | 위 5 family invariant ADR 파일의 `status: Superseded` 전환 (`archive/adr/ADR-009/016/024/008/037-*.md`) |

**Coupling trigger boundary (over-trigger 차단)**:
- lane internal refactor (preset 추가 / prompt edit / template wording) = T1/T2/T3 **비발동** (§결정 2 원문 boundary 보존).
- **Amendment ≠ supersede**: family invariant ADR 의 *additive amendment* 는 T3 미발동 (Amendment 1 선례 — §A1-5 "T3 trigger 미발동: family invariant ADR supersede 0"). 본 Amendment 2 자체도 ADR-037 additive amendment = **T3 미발동** (wrapper MAJOR 강제 0). T3 는 `status: Superseded` 전환만 발동.
- coupling_signal 은 **wrapper PR 만** 평가 (lane plugin 의 자체 bump 는 wrapper 와 독립 — §결정 2 "6 lane plugin 의 자체 bump 는 wrapper 와 독립" 보존).

#### 결정 A2-5 — β lenient 비대칭 보존 (over-bump PASS / under-bump FAIL)

ADR-037 Option β Lenient base 의 핵심 비대칭 = `expected = max(commit_signal, diff_signal, coupling_signal)` 대비:

- `actual_bump >= expected` → **PASS** (over-bump 허용 — 보수적 상향 bump 은 noise 아님)
- `actual_bump < expected` → **FAIL** (under-bump 차단 — consumer update 판단 불가)
- `actual_bump == downgrade` → **FAIL** (forward-only 위반, §결정 5)
- `expected > 0 AND actual_bump == none` → **FAIL** (signal 있는데 bump 누락)

v1 template (`Validate consistency` step) 이 이미 commit_signal 축에서 이 비대칭을 구현 (over `a_rank > c_rank` = OK / under `c_rank > a_rank` = FAIL). v2 = `expected` 를 3-signal `max` 로 확장 (diff_signal + coupling_signal 합산). **Strict-reject 의도 보존** (line 70 Codex Option 1 Strict rejected 의 dogfood noise 회피) — 본 비대칭이 over-bump 를 PASS 시켜 dogfood noise 회귀를 차단하므로, β lenient 보존 = 약화 아님 (ADR-037 본래 의도된 비대칭의 유지).

#### 결정 A2-6 — fix:-PR / no-surface PR bump 판정 SSOT (#2294/#2298 류 면제 경계)

요구사항 lane Domain G1 미정의 영역 해소. `fix:` 커밋이거나 wrapper root plugin.json 미변경 (linter `.yml` / manifest 만 수정) PR 이 bump 대상인지의 경계를 SSOT 확정:

**판정 규칙 (commit_signal × diff_signal 교집합)**:

| 케이스 | commit_signal | diff_signal | expected | bump 의무 |
|---|---|---|---|---|
| `archive/**` ADR-only 변경 (본 Amendment) | `docs:` → patch | none (`archive/**` 비귀속, 결정 A2-3) | **none** | **면제** — diff_signal=none 이 commit `docs:` patch 를 상쇄? → 아래 정밀 규칙 |
| linter `.yml` / manifest 만 수정 (`#2294` 류) | `fix:` → patch | wrapper surface 귀속 시 patch / 비귀속 시 none | 귀속 여부에 종속 | 아래 정밀 규칙 |
| prefix 부재 커밋 | none | 귀속 surface 변경 시 해당 rank | diff_signal 단독 | diff_signal 종속 |

**정밀 규칙 (SSOT)**:
1. **commit_signal=none 자연 면제**: Conventional Commits prefix 부재 (예: merge commit, prefix 없는 메시지) = `commit_signal=none`. 이때 expected 는 diff_signal + coupling_signal 만으로 결정 — `fix:`/`docs:` prefix 강제 부재가 자연 면제 (v1 `signal="none"` default 보존).
2. **`fix:` prefix PATCH 강제 vs diff_signal none 의 경계**: `fix:` 커밋이지만 변경 파일이 **전부 비귀속 경로** (`archive/**` / repo-meta / 비귀속 `.github/**`) → diff_signal=none. 이때 `expected = max(patch, none, none) = patch` 이나 **actual_bump=none 면제 조건** = "변경 파일 중 wrapper version-bump surface 귀속 파일 0개" 일 때 `commit_signal` 을 **none 으로 강등** (no-surface-touch exemption). 즉 commit prefix 가 `fix:`/`docs:` 여도 **귀속 surface 0 변경 = bump 면제** (consumer 가 받을 runtime 변경 0 = update 불요).
3. **`#2294`/`#2298` 류 (linter `.yml` / manifest 수정)**: 변경 파일이 wrapper surface 귀속 (`templates/**` / `scripts/**` / `.github/**` 중 `templates/` 미러면 `templates/` 귀속) → diff_signal = 해당 surface rank (대개 PATCH — comments/config-only). `fix:` commit_signal patch 와 정합 → PATCH bump 의무. 단 `.github/workflows/**` 단독 (templates 미러 아닌 self-app meta) = 비귀속 → 면제.
4. **doc-only fast-path Story 의 ADR-only PR** (본 Amendment): `archive/adr/**` 만 변경 = diff_signal none + no-surface-touch exemption → bump 면제 (ADR-054 doc-only fast-path 정합 + ADR-092 §결정 3 wrapper CHANGELOG 동결로 CHANGELOG 동반 의무도 0).

**경계 명문화 핵심**: bump 의무 = "consumer 가 받는 wrapper runtime surface 가 실제 변경됐는가" (귀속 surface touch) AND/OR "commit signal 이 그 변경을 declare 했는가". 둘 다 없으면 (no-surface-touch) `fix:`/`docs:` prefix 만으로는 bump 강제 0. CLAUDE.md "bump 기준 = 표 등재 여부" 실무 관행 (`archive/adr/**` EXEMPT) 과 정합.

#### 결정 A2-7 — warning-first → blocking 승격 경로 (tier)

게이트 강도 = **warning-first → 증거 후 blocking 승격** (#2098 선례 — ADR-060 evidence-enforceable promotion framework 정합):

- **초기 tier = warning** (non-blocking): v2 게이트 신설 시 `continue-on-error` / advisory exit — false-positive 폭증 가능 신규 로직의 dogfood 관찰 기간 확보 (Epic CFP-2310 §주의 1 "consumer 템플릿 naive 복사 → false-positive 폭증" 리스크 완화).
- **blocking 승격 trigger**: ADR-060 §결정 5 default warning + 승격 gate (PR 누적 ≥ N + bypass 외 failure_threshold + evidence sample 누적) 충족 후 별 amendment (또는 Epic 후속 Story) 로 `required` context 전환. 승격 = ratchet 강화 방향 (warning → blocking, ADR-058 §결정 5 정합).
- **승격 시 InfraOperationalArch 동반 설계 (결정 A2-9)**: required context 전환은 cross-repo gh api flake 가 merge 차단 리스크 → fail-open vs fail-closed + bypass 보존을 승격과 묶어 결정.

#### 결정 A2-8 — ADR-092 §결정 3 정합 (wrapper CHANGELOG 비의존)

ADR-092 Amendment 1 §결정 3 = wrapper 루트 CHANGELOG 동결 (`archive/CHANGELOG-legacy.md` 보존, 신규 entry 금지). 따라서:

- **새 v2 게이트는 wrapper CHANGELOG 를 commit-signal 근거로 삼지 않는다.** wrapper version 이력 SSOT = plugin.json version + git history + marketplace.json mirror (ADR-092 §결정 3 재정의). v1 의 `invariant-check.yml` version-match (plugin.json ↔ CHANGELOG) 는 이미 prune 됨 (line 77 "REMOVED — CHANGELOG 동결") — v2 게이트도 CHANGELOG 부재를 정상으로 간주.
- **lane CHANGELOG 은 해당 lane 검사에만 종속 가능**: `plugins/<lane>/CHANGELOG.md` 는 per-plugin self-owned (ADR-092 §결정 1 + Amendment 1 lane 8종 보존). lane bump 평가 시 lane CHANGELOG entry 동반은 ADR-092 §결정 2 drift detection (lane 8종) 영역 — 본 version-bump 게이트와 cross-ref (commit-signal 근거는 아님, 별 detection 축).

#### 결정 A2-9 — ADR-063 §결정 18-B 9-plugin MAJOR atomic cross-check 정합

ADR-063 §결정 18-B (Amendment 7) = MAJOR version bump 시 9 plugin 동시 MAJOR atomic invariant. per-plugin 독립 평가 (결정 A2-2 scope 분리) 는 이 동시-MAJOR 의무를 **검증하지 못하는 사각** 이 있다 (예: `codeforge-deploy` 만 MAJOR bump, sibling 8 미bump → per-plugin 평가는 deploy 만 PASS):

- **cross-check 필요성 명시 (S2 구현 hint)**: v2 게이트는 어느 plugin 이든 `actual_bump=major` 감지 시 → **9-plugin MAJOR atomic cross-check** 발동 의무. 단일 plugin MAJOR + sibling 미bump = ADR-063 §결정 18-B 위반 = FAIL.
- **bypass label 분리**: `hotfix-bypass:marketplace-atomic-major` (ADR-063 §결정 18-B family member) — 기존 `hotfix-bypass:marketplace-atomic` 와 분리.
- **MINOR/PATCH 영역 외**: §결정 18-B 가 MAJOR atomic 만 family-wide 의무화 (MINOR/PATCH = per-plugin 독립). 따라서 cross-check 도 `actual_bump=major` 일 때만 발동 — MINOR/PATCH 는 결정 A2-2 per-plugin scope 평가로 충분.
- **Tier routing (ADR-063 §결정 19)**: MAJOR bump 은 Tier 무관 family bundle 경로 강제 (§결정 19 "MAJOR bump 시 Tier 2 lane 도 Tier 1 bundle walk 강제 routing"). v2 cross-check = 이 routing 의 PR-time mechanical 검증 surface.

### Amendment 2 거버넌스 렌즈 (deputy 영역 반영)

- **SecurityArch**: (1) `BYPASS_VERSION_BUMP=1` = `BYPASS_VERSION_BUMP_REASON` 비공백 audit-reason 강제 (v1 template `Bypass check` step 이미 구현 — `REASON` 부재 시 `::error` exit 1, 보존 의무). (2) lane plugin.json cross-repo 조회 = PAT read-only (ADR-066 `contents:read`, write scope 미사용). (3) third-party action SHA-pin (CFP-300 — v1 template `actions/checkout@34e1148...` 보존, v2 추가 action 도 SHA-pin 의무).
- **InfraOperationalArch**: required context 승격 (결정 A2-7) 시 cross-repo gh api (lane/marketplace 조회) flake 가 merge 차단 리스크 → **fail-open (gh 장애 시 PASS + warning) vs fail-closed (CI 환경 exit 2)** 결정을 required 전환과 묶어 설계. v1 §결정 22 (ADR-063) 선례 = CI 환경 fail-loud (gh 미설치/미인증/fetch 실패 → exit 2) — warning tier 동안은 fail-open advisory, blocking 승격 시 fail-closed 전환 + BYPASS env 보존 (긴급 merge 경로 유지).
- **TestContractArch**: S2 mechanical lint 이 discriminating fixture (RED→GREEN proof) 를 갖도록 surface-table / 귀속 규칙을 테스트 가능 형태로 명세 — (a) RED fixture: `plugins/codeforge-design/agents/X.md` 삭제 PR + design plugin.json 미bump = under-bump FAIL 기대 / (b) GREEN: 동 PR + design MINOR bump = PASS / (c) 면제 RED→GREEN: `archive/adr/**` only PR = no-surface-touch 면제 PASS (bump 0) / (d) coupling RED: lane agent 삭제 + wrapper plugin.json 미bump = T2 coupling FAIL. 결정 A2-2/A2-3/A2-6 의 closed mapping 이 fixture assert 가능 단위 (glob → rank deterministic).

### Amendment 2 self-application (ratchet 검증 + 첫 적용 사례)

본 Amendment 2 = **강화 방향 only** (frontmatter `amendments[2].sunset_justification` 명시). self-application boundary 실현 + diff_signal/coupling 형식화 + 공유 파일 귀속 정밀화 = scope 확장 + invariant 강도 상승. β lenient 비대칭 보존 = 약화 아님 (의도된 비대칭 유지). ADR-064 top-down self-application ratchet + ADR-058 §결정 5 약화 방향 발의 차단 logic 통과.

**T3 self-trigger 검증**: 본 Amendment 2 = ADR-037 (family invariant ADR) 의 *additive amendment* (supersede 아님) → 결정 A2-4 boundary 에 의해 **T3 미발동** (wrapper MAJOR 강제 0). Amendment 1 선례 (§A1-5) 정합.

**첫 적용 dogfood 사례 (본 carrier CFP-2311)**: 본 Amendment 도입 PR = `archive/adr/ADR-037-*.md` 단일 파일 변경. self-application 평가: `commit_signal` = `docs:` prefix → patch 이나 **변경 파일 전부 `archive/**` 비귀속** (결정 A2-3) → no-surface-touch exemption (결정 A2-6 규칙 2/4) → `commit_signal` none 강등 + `diff_signal=none` + `coupling_signal=none` → `expected=none` = `actual_bump=none` → **β lenient PASS (no-bump 정상)**. wrapper plugin.json bump 0 = marketplace sync 불요 (ADR-063 §결정 1 mirrored field 변경 0). **본 PR 자체가 결정 A2-6 면제 경계의 시연.**

### Amendment 2 mechanical enforcement boundary (Phase 1 declarative-only)

본 Amendment 2 = **declarative SSOT mandate** (Phase 1, ADR-054 doc-only fast-path scope). 실 게이트 artifact (`templates/github-workflows/check-plugin-version-bump.yml` v2 갱신 + `.github/workflows/check-plugin-version-bump.yml` self-app copy + `invariant-check.yml` `CONSUMER_ONLY_WORKFLOWS` 등재 해제 + lint script + discriminating fixture) = **S2 (#2312) carrier (Phase 2)**. `mechanical_enforcement_actions[]` entry append = S2 PR open 시점 (warning tier 시작, 결정 A2-7). ADR-076 §결정 9 + ADR-067 §결정 4 sequential ordering 정합.

## 해소 기준

N/A — permanent policy (`is_transitional: false`). base 결정 1-5 + Amendment 1 (0 drift invariant) + Amendment 2 (모노레포-aware self-application + v2 모델) 모두 permanent governance — codeforge plugin family 가 deprecate 되지 않는 한 영구 유효. Amendment 는 강화 방향만 허용 (ADR-058 §결정 5 + ADR-064 top-down self-application). Amendment 1 = ratchet 강화 (detect-only → atomic 후 0 drift 의무 신설, scope 확장) — sunset_justification 면제 (frontmatter `amendments[].sunset_justification` 명시). Amendment 2 = ratchet 강화 (self-application boundary 실현 + diff_signal/coupling v2 형식화 + 공유 파일 귀속 정밀화, scope 확장 + invariant 강도 상승, β lenient 비대칭 보존) — sunset_justification 면제 (frontmatter `amendments[2].sunset_justification` 명시).

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
