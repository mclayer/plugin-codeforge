---
adr_number: 10
title: Inter-plugin Contract Sibling Sync — canonical/sibling 책임 + sync 트리거 + drift 처리 정책
status: Proposed
category: Team & Process
date: 2026-04-29
related_files:
  - docs/superpowers/specs/2026-04-29-cfp-42-inter-plugin-contract-sibling-backfill-design.md (parent CFP)
  - docs/adr/ADR-008-inter-plugin-contract-versioning.md (versioning 룰 — 본 ADR 과 함께 모든 contract frontmatter 에 인용 의무)
  - docs/adr/ADR-009-wrapper-only-decomposition.md (ζ arc 결과 — 본 ADR 의 P0 gap 출처)
  - docs/inter-plugin-contracts/MANIFEST.yaml (contract 완결성 SSOT)
  - docs/inter-plugin-contracts/review-verdict-v2.md (선례 패턴)
is_transitional: false
---

## 상태

Proposed (2026-04-29) — CFP-42 Phase 1 PR merge 시 Accepted 전환. CFP-42 Phase 2 PR merge 시 Adopted 전환.

## 컨텍스트

ζ arc (CFP-31 parent · CFP-29~CFP-40 추출) 가 6 lane plugin 으로 분리되며 5 신규 inter-plugin `kind: contract` 표면을 lane plugin 들의 `docs/inter-plugin-contracts/` 에 canonical 로 신설:
- `requirements-output-v1` (codeforge-requirements)
- `design-output-v1` (codeforge-design)
- `develop-output-v1` (codeforge-develop)
- `test-verdict-v1` (codeforge-test)
- `pmo-output-v1` (codeforge-pmo)

ADR-009 본문 §51 은 "Inter-plugin contract 6종 보유" 라고 단언하지만, 실제 wrapper repo 의 [docs/inter-plugin-contracts/](../inter-plugin-contracts/) 에는 5 파일 — 그중 3 은 `kind: registry`, 2 는 `kind: contract` (review-verdict v1+v2). 즉 5 lane output sibling reference 가 wrapper 에 backfill 안 된 상태로 ζ arc 종료.

CFP-35 (review-verdict v2 retrofit) 는 이미 "**canonical at lane plugin repo + sibling at wrapper repo**" 패턴을 도입 ([review-verdict-v2.md:19-22](../inter-plugin-contracts/review-verdict-v2.md#L19-L22)) — 본 ADR 은 이 패턴을 5 신규 contract 에 일반화하고, 향후 누락이 재발하지 않도록 명시적 정책으로 동결.

## 결정

### 1. Canonical 위치 룰

- `kind: contract` 의 canonical 은 **producer plugin** repo 의 `docs/inter-plugin-contracts/<contract-name>-v<N>.md`
- 현재 producer 분포: 5 lane output 은 각 lane plugin, review_verdict 는 codeforge-review

### 2. Sibling 위치 룰

- wrapper repo `docs/inter-plugin-contracts/<contract-name>-v<N>.md` 가 sibling reference (consumer 1차 진입점)
- sibling 본문은 canonical 과 verbatim 일치. 부가 정보는 본문 시작의 "**상위 SSOT 위치**" 섹션 (review-verdict-v2 패턴)
- sibling frontmatter 에 `related_adrs ∋ "ADR-008"` (versioning 룰) + `related_adrs ∋ "ADR-010"` (본 ADR) 의무

### 3. MANIFEST.yaml = kind:contract registry SSOT

wrapper repo `docs/inter-plugin-contracts/MANIFEST.yaml` 가 모든 `kind: contract` 파일을 enumerate. 신규 contract 추가 절차:

1. lane plugin 에 canonical 작성 (ADR-008 versioning 룰 준수)
2. wrapper MANIFEST.yaml 에 entry 추가
3. wrapper sibling file 작성 (canonical 본문 verbatim mirror + 상위 SSOT 위치 섹션 + 본 ADR 인용 frontmatter)
4. 본 ADR 본문 불변 — MANIFEST 만 갱신

`kind: registry` 파일 (cross-cutting protocol — comment-prefix-registry, fix-event, label-registry) 은 본 MANIFEST 범위 밖. 기존 `check-doc-frontmatter.sh` + `check-doc-section-schema.sh` 가 검증.

### 4. Sync 트리거

- canonical 변경 PR merge 직후 wrapper sibling sync PR open · merge 의무 (CFP-24 marketplace cross-repo sync 정책 동질)
- canonical PR body 또는 Story §11 에 "wrapper sibling sync PR 후속 의무" 명시
- author 의무 (본 ADR 시점) — CI 자동 차단은 후속 ADR (drift detection 도입 시점)

### 5. Drift 검출 정책

- 본 ADR 시점: manifest completeness + orphan + frontmatter schema (ADR-010 reference 포함) + sibling marker — `scripts/check-inter-plugin-contracts.sh` lint
- 본문 verbatim drift 검출 (canonical SHA vs sibling SHA 비교) 은 후속 ADR 에서 결정

## 결과

### 위배 시 처리

- lint FAIL: PR merge 차단 (필수 status check — wrapper repo CI)
- canonical 변경 후 sibling sync PR 누락: 다음 wrapper PR 가 lint manifest mismatch 로 차단 (간접 강제)
- 후속 ADR 에서 drift detection workflow 도입 시 직접 강제 가능

### 선례·관계 ADR

- ADR-008: 모든 contract frontmatter 에 함께 인용 의무. 본 ADR 은 ADR-008 의 versioning 룰을 전제로 한 sync 정책 layer
- ADR-009: ζ arc decomposition 결과 → 본 ADR 의 P0 gap 출처

### 후속 영향

- 7번째·8번째 contract 추가 시 4단계 절차 + lint 자동 차단의 이중 안전망 작동
- 향후 wrapper-canonical `kind: contract` (cross-cutting typed schema) 등장 시 MANIFEST schema 에 `role` 필드 도입 — 본 ADR 갱신 또는 신규 ADR

## 해소 기준

N/A — permanent policy

## 관련 파일

- [docs/inter-plugin-contracts/MANIFEST.yaml](../inter-plugin-contracts/MANIFEST.yaml) — registry SSOT
- [docs/inter-plugin-contracts/review-verdict-v2.md](../inter-plugin-contracts/review-verdict-v2.md) — 선례 패턴
- [scripts/check-inter-plugin-contracts.sh](../../scripts/check-inter-plugin-contracts.sh) — 본 ADR 강제 lint
- [docs/adr/ADR-008-inter-plugin-contract-versioning.md](ADR-008-inter-plugin-contract-versioning.md)
- [docs/adr/ADR-009-wrapper-only-decomposition.md](ADR-009-wrapper-only-decomposition.md)

---

## Amendment 1 — ADR number reserve protocol 강화 (CFP-291 / Issue #298, 2026-05-09)

### 배경

§4 Sync 트리거 절차에 "ADR 번호를 실제 할당하기 전에 현재 최댓값을 확인" 하는 명시적 단계가 없었다. 병렬 feature branch 가 동시에 동일 번호를 채택하는 race condition 이 관찰됐으며, 이를 기계적으로 차단할 프로토콜이 필요하다.

### 결정

새 ADR 번호를 reserve 하기 전 반드시 아래 3단계를 수행한다:

1. **Verify** — `Glob(docs/adr/ADR-*.md)` 결과를 숫자 정렬하여 현재 최대 번호(max)를 확인.
   ```bash
   ls docs/adr/ADR-*.md | sort -t- -k2 -n | tail -3
   ```
2. **Reserve** — 사용할 번호를 `max + 1` 로 결정.
3. **Re-verify immediately before commit** — 파일 이름을 실제 기록하기 직전에 동일 Glob 을 한 번 더 실행하여, 동일 번호를 사용하는 파일이 존재하지 않음을 확인. 충돌 발견 시 즉시 중단하고 번호를 재산정.

이 절차는 (a) 새 ADR 파일 생성, (b) Story §3 에 ADR 번호 최초 기입, (c) DesignLane agent 가 change-plan 또는 story file 에 `ADR-NNN` 를 삽입하는 모든 시점에 적용된다.

### 위배 시 처리

- 중복 ADR 번호가 PR 에서 발견되면 CI `check-doc-frontmatter.sh` 가 FAIL (duplicate `adr_number` 검출).
- 작성자는 번호를 re-number 하고 re-push 해야 한다. retroactive 수정 허용 (충돌 발생 시 번호가 작은 쪽을 선점).

---

## Amendment 2 — inter-plugin contract MAJOR bump canonical-first 의무 (CFP-291 / Issue #311, 2026-05-09)

### 배경

§4 Sync 트리거는 "canonical 변경 PR merge 직후 wrapper sibling sync PR open·merge 의무" 를 규정하지만, MAJOR version bump(예: v3 → v4) 시 어느 repo 가 먼저 merge 해야 하는지 순서를 명시하지 않았다. wrapper-first MAJOR bump 가 발생하면 canonical 이 구버전인 상태에서 sibling 이 신버전을 선언하는 일시적 drift 가 생겨 consumer 에게 잘못된 contract 가 노출된다.

### 결정

**MAJOR version bump 에 한해 canonical-first 순서를 의무화한다:**

1. **Canonical PR 먼저** — lane plugin repo 에 MAJOR bump PR 을 open·merge 한다.
2. **Wrapper sibling sync PR 후속** — canonical merge 완료 후에만 wrapper sibling sync PR 을 open 한다.
3. **Wrapper-first MAJOR 금지** — wrapper sibling 에 MAJOR bump 를 먼저 commit 하는 것은 금지. 해당 PR 은 CI `inter-plugin-drift` check 가 차단한다.

MINOR / PATCH bump 는 이전과 동일하게 wrapper-first 허용 (ADR-008 §결정 3 forward-compat 정책 유지).

### 위배 시 처리

- `scripts/check-inter-plugin-contracts.sh` 의 향후 drift check 확장에서, wrapper sibling 의 MAJOR version 이 MANIFEST.yaml 에 기록된 canonical MAJOR version 보다 높을 경우 CI FAIL.
- 현 시점 (lint 확장 전): author 의무 + PR description 에 "canonical 먼저 merge 확인" 체크박스 추가 의무.
- 장기: `inter-plugin-drift.yml` workflow (후속 ADR 도입 예정) 가 자동 강제.

---

## Amendment 3 — sync-contract-bump.sh standard tool 명시 (CFP-408, 2026-05-12)

### 배경

§4 Sync 트리거 + Amendment 2 (MAJOR canonical-first) 는 정책 룰만 규정하고, 실제 sync PR sequence 를 author 가 manual 3 PR 로 open. CFP-46 / CFP-137 / CFP-391 3 Story 반복으로 동일 부담 관찰. 누락 시 drift risk (sibling 본문 vs canonical 불일치, marketplace mirror 누락).

### 결정

**`scripts/sync-contract-bump.sh` 가 본 ADR §4 / Amendment 2 의 standard tool 이다:**

1. **호출 방식**: `scripts/sync-contract-bump.sh <contract> <new-version> [--dry-run]`
2. **3-stage sequence** (script 가 plan + 일부 자동화 수행):
   - Stage 1: wrapper sibling 갱신 + branch + commit + PR (자동, real-run)
   - Stage 2: canonical lane plugin repo 갱신 + PR (수동 — Phase 2 follow-up 자동화 예정)
   - Stage 3: marketplace.json mirror (plugin.json version 변경 동반 시만, 수동)
3. **Merge order strict**: canonical → wrapper sibling → marketplace
4. **MAJOR bump 자동 감지**: MANIFEST.yaml 의 Active file 명에서 vN 추출 → new version 비교 → MAJOR 시 canonical-first 의무 PR body 자동 footer
5. **Dry-run 우선 의무**: real-run 전 `--dry-run` 으로 plan 검토 권장
6. **Scope limitation**: kind:contract 만 적용 (kind:registry — fix-event / label-registry / debate-protocol 등 — 본 script 적용 외)

### 위배 시 처리

- script 미사용 manual 3 PR 패턴은 허용 (deprecated 아님). 단 sequence 룰 (canonical-first MAJOR) 은 동일 의무.
- script 사용 시 `Generated by` footer 가 PR body 에 자동 삽입 — review 시 식별 단서.
- script 의 stage 1 자동화 부재 (canonical / marketplace) 영역은 author 의무로 진행 — Phase 2 follow-up CFP 에서 canonical clone + commit + PR 자동화 확장 검토.

### 관련 파일

- [scripts/sync-contract-bump.sh](../../scripts/sync-contract-bump.sh) — standard tool entry point
- [scripts/test-sync-contract-bump.sh](../../scripts/test-sync-contract-bump.sh) — 8 test scenario harness (18 assertion)
- [docs/orchestrator-playbook.md](../orchestrator-playbook.md) §sibling-sync — Orchestrator 호출 절차

---

## Amendment 4 — sibling PR phase-gate fast-pass (sibling-pr label, CFP-499, 2026-05-12)

### 배경

wrapper Story 가 sibling repo (lane plugin) 에 mechanical mirror sync PR 을 open 시, sibling PR 은 자체 설계리뷰 evidence 가 없다. wrapper Story 의 설계리뷰 PASS 결과는 wrapper PR 에만 박제 (comment + label) 되어 sibling PR 의 `phase-gate-mergeable` workflow 가 인식하지 못한다.

결과 — 매 wrapper Story 마다 모든 sibling PR 이 `phase-gate-mergeable` action_required 차단. Orchestrator 가 evidence comment 박제 (CFP-133 fallback) 또는 label cycle 등의 ad-hoc workaround 로 unblock. recurring 비용 + workflow drift (sibling repo 별로 CFP-133 fallback 적용 시점 차이) 로 신뢰 무너짐.

CFP-448 (#448) sibling PR plugin-codeforge-requirements#20 + plugin-codeforge-design#34 차단 진단 후 본 Amendment 발의.

### 결정

**`sibling-pr` label 부착 PR 은 `phase-gate-mergeable` fast-pass 처리한다:**

1. **mechanism**: `phase-gate-mergeable.yml` step 5a (type:epic / doc-only fast-pass) 분기에 `isSiblingPr` 추가
   ```javascript
   const isSiblingPr = allLabels.includes('sibling-pr');
   if (isEpicLabel || isSiblingPr || isDocOnly) { fast-pass success; return; }
   ```

2. **Label 부착 의무자**: Orchestrator self-write 영역 (lane plugin 미관여). wrapper Story 의 sibling sync PR open 시점에 자동 부착.

3. **정합성 보증**: sibling PR 의 design review 정합성은 wrapper Story PR 의 design review PASS 가 보증. sibling PR 내용 = wrapper Story 의 mechanical mirror (verbatim file changes, agent definition / contract / plugin metadata).

4. **scope limitation**: `sibling-pr` label fast-pass 는 **review evidence** 만 우회. marketplace-parity / CodeQL / dogfood-artifact-paths 등 다른 required check 는 영향 0.

5. **anti-misuse 안전망**: `sibling-pr` label 은 Orchestrator self-write 만 (lane plugin self-write 영역 침해 금지, ADR-035 §결정 4 정합). lane plugin agent / human author 가 부착 시 audit 대상 (CFP-499 §11 follow-up — `check-sibling-pr-label-source.sh` lint 후행 CFP carrier).

### 위배 시 처리

- workflow `isSiblingPr` 분기 누락 sibling repo (drift) — recurring 차단 재발. workflow drift sync 별도 carrier 의무.
- `sibling-pr` label 의 misuse (lane plugin self-write 또는 human author 부착) — anti-misuse lint 후행 carrier 가 PR review 단계 차단.

### Scope (본 Amendment 즉시 적용 repo)

- wrapper `templates/github-workflows/phase-gate-mergeable.yml` (SSOT fixture)
- `mclayer/plugin-codeforge-requirements/.github/workflows/phase-gate-mergeable.yml` (CFP-448 sibling PR 차단 해소 + drift sync)
- 나머지 5 sibling repo (codeforge-design / codeforge-develop / codeforge-test / codeforge-review / codeforge-pmo) — 후행 carrier (codeforge-design 은 이미 wrapper SSOT verbatim 정합, 다른 4 repo 는 drift 가능성)

### 관련 파일

- [templates/github-workflows/phase-gate-mergeable.yml](../../templates/github-workflows/phase-gate-mergeable.yml) — wrapper SSOT fixture (sibling-pr fast-pass 추가)
- `mclayer/plugin-codeforge-requirements/.github/workflows/phase-gate-mergeable.yml` — drift sync + sibling-pr fast-pass
- CFP-499 Story file (`mclayer/codeforge-internal-docs/wrapper/stories/CFP-499.md`)
