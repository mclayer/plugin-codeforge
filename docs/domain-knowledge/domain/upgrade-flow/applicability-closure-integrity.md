---
kind: domain_fact
type: domain-knowledge
area: upgrade-flow
topic_slug: applicability-closure-integrity
title: applicability ⊥ closure 직교 모델 + closure-완전성 도메인 정의
status: Active
tags:
  - upgrade-flow
  - applicability-closure-integrity
  - consumer-applicability-filter
  - transitive-dependency-closure
  - conditional-resource-provisioning
  - whitelist-manifest-ssot
  - adr-130
related_adrs:
  - ADR-130  # 본 entry 의 carrier ADR (applicability ⊥ closure 분류규칙 + closure-완전성 SSOT)
  - ADR-083  # consumer-applicability-filter (Sunsetted) — ADR-130 이 supersede. 8 invariant verbatim base.
  - ADR-076  # §결정 2 declarative reconciliation upgrade — 11 영역 wrapper SSOT desired state (closure 의 desired-state anchor)
  - ADR-027  # consumer adoption protocol (boundary disjoint — consumer-side signal SSOT)
  - ADR-005  # dual-channel template ↔ live byte-identical mirror (closure 자산 self-app exemption 근거)
  - ADR-058  # §결정 5 symmetric evidence-gate (약화 vs 강화 ratchet 정합)
  - ADR-097  # carrier-preserved sunset 선례 (supersede 결정 근거)
related_stories:
  - CFP-2394  # parent Epic — consumer-applicability whitelist↔manifest closure 정합 복원
  - CFP-2395  # 본 carrier Story (Epic CFP-2394 Story A — gating Story)
created: 2026-06-25
updated: 2026-06-25
---

# applicability ⊥ closure 직교 모델 + closure-완전성 도메인 정의

## 정의

codeforge upgrade flow 안에서 wrapper 자산이 consumer repo 로 배포될 때 두 개의 **직교(orthogonal)하는 축**이 작동한다.

- **applicability** (수평 필터 — "복사할지 말지"): 이 자산이 consumer repo 에 *적용 대상* 인가. consumer-applicable vs plugin-self-governance 분류. positive whitelist 기반. 판정 SSOT = `templates/scripts/consumer_applicable_workflows.txt` (28 [verified-via: PL `git show origin/main` grep -vE comment/blank = 28]).
- **closure** (수직 폐포 — "복사한다면 무엇과 함께"): 적용 대상 자산이 *실행 가능* 하려면 무엇이 함께 배포돼야 하는가. workflow → scripts → 데이터(tsv) → 정책doc(md) 의 의존 폐포. 판정 SSOT = `templates/consumer-scripts.manifest` (16 [verified-via: 동 실측 = 16]) + 런타임 `templates/scripts/mirror-dependency-closure.py`.

본 entry = ADR-130 §결정 7 이 규정한 1급 도메인 정의 anchor — codeforge 의 applicability/closure 개념 narrative SSOT. ArchitectAgent / DeveloperAgent / 미래 workflow 신설자 / 후속 Story B·C·D carrier 가 참조하는 단일 정의. 거버넌스 SSOT = ADR-130 §결정 본문, 본 entry = 도메인 narrative SSOT (2-SSOT 분리, declarative-reconciliation.md 선례 답습).

> **본질 선언** (ADR-130 본질 선언 verbatim): applicability(수평 필터)와 closure(수직 폐포)는 직교하는 두 축이다. 두 축을 한 축으로 뭉뚱그린 것이 consumer 회귀 결함의 도메인 뿌리다. consumer-applicable 판정은 positive whitelist(applicability SSOT)로, 실행가능 폐포는 manifest(closure SSOT)로 닫는다. closure-완전성은 scripts + 데이터(tsv) + 정책doc(md) 3종을 명시적으로 커버하며, "완전" = 적용 대상 항목의 hard-block 의미 자산이 모두 manifest 에 등재된 상태다.

## 컨텍스트

Epic CFP-2394 는 applicability whitelist(28) ↔ closure manifest(16) 의 격차를 복원한다. 이 격차의 표면 증상 = "applicable 로 판정된 항목의 closure 가 manifest 에 미등재되어 consumer 가 실행 단계에서 깨지는" 것. 즉 **applicability 판정은 통과했으나 closure 가 불완전** 한 상태.

ADR-083 이 applicability 필터(4-way repo-kind + positive whitelist)를 정의했으나, **closure 축이 1급으로 정의되지 않았고**, whitelist 의 normative 지위 역시 어느 ADR 에도 미정의 상태였다. ADR-130 이 그 공백을 메우고, 본 entry 가 도메인 narrative 로 박제한다.

### declarative reconciliation 3-layer 안에서의 위치 (prior art cross-ref)

[verified-via: 선례 `docs/domain-knowledge/domain/upgrade-flow/declarative-reconciliation.md` L74-78 3-layer 표]

본 모델은 같은 `upgrade-flow/` 도메인의 `declarative-reconciliation.md` (desired/current/converge) 위에 얹힌다 — ADR-076 §결정 2 declarative reconciliation upgrade 가 내부 anchor.

| reconciliation layer | applicability/closure 의 역할 |
|---|---|
| **Desired state** (wrapper SSOT 11 영역) | whitelist = desired state 의 "consumer 에 배포될 부분집합" 정의. closure 규칙 = desired state 의 "함께 배포돼야 실행되는 동반 자산" 정의. |
| **Current state** (consumer overlay + plugin install) | consumer `.github/workflows/` + `scripts/` 의 실제 배포 상태. closure 불완전 = current state 가 desired 의 실행가능 폐포를 못 채운 drift. |
| **Customization layer** (marker block 밖) | 본 모델 직접 대상 아님. 단 closure 자산이 consumer customization 과 충돌하지 않아야 한다는 경계는 보존. |

- **converge(=upgrade apply) 시점에 차단면이 드러난다**: `reconcile-overlay.sh` 가 whitelist-applicable 항목을 consumer 로 mirror 할 때, closure 미충족 항목은 consumer CI 에서 `bash scripts/<name>.sh` 가 파일 부재로 실패 → required check 차단. 단 현재 closure gate(`mirror-dependency-closure.py`)는 depth-1·shell-only 라 데이터/정책doc 미충족을 *감지하지 못한다* (§핵심 규칙 "런타임 gate 범위 vs manifest 등재 범위").

### 외부 established pattern 매핑

[verified-via: 요구사항리뷰 lane §9.1 #3 confirmed · 다출처]

| 내부 용어 | 외부 established concept | prior art |
|---|---|---|
| **closure** (scripts+데이터+정책doc 의존 폐포) | **transitive dependency closure** (패키지 매니저 핵심 — lockfile 이 transitive dep 를 닫음) | npm/pip/cargo lockfile, Bazel |
| **applicability** (consumer-applicable vs self-governance) | **conditional resource provisioning** | Helm `condition`/`tags`(chart 일부만 배포), Kustomize overlay base/patch, Ansible `when:` |
| **upgrade 부분 전달** | 템플릿 부분 머지 | Copier `update`, cookiecutter |

[source: npm package-lock / PyPA pylock.toml / bazel strict-deps]

## 핵심 규칙

### 1. applicability ⊥ closure 직교 모델 (두 독립 축)

| 축 | 질문 | 도메인 정의 | 판정 위치(SSOT) |
|---|---|---|---|
| **applicability** (수평) | "이 자산이 consumer repo 에 *적용 대상* 인가?" | consumer-applicable vs plugin-self-governance 분류. positive whitelist 기반. | `consumer_applicable_workflows.txt` (whitelist) |
| **closure** (수직) | "적용 대상 자산이 *실행 가능* 하려면 무엇이 함께 배포돼야 하는가?" | workflow → scripts → 데이터(tsv) → 정책doc(md) 의 의존 폐포. | `consumer-scripts.manifest` (manifest) + 런타임 `mirror-dependency-closure.py` |

- **직교성** [verified-via: ADR-083 §"기존 SSOT 의 한계" — "closure resolver = vertical bundle / consumer-applicability filter = horizontal axis, disjoint super-class"]: 두 축은 **sequential composition** (closure 먼저 → filter → cp)으로 합성되나 서로의 판정에 간섭하지 않는다.

### 2. whitelist ↔ manifest SSOT 관계 + 3-way 일관성

[verified-via: PL `git show origin/main:scripts/lib/walk_plan.py` grep `applicable_to|repo_kind|consumer_applicable|detect-repo-kind|FILTER_REPO_KIND` = 36 match → wire LIVE]

- **whitelist = applicability SSOT (live)**: `templates/scripts/consumer_applicable_workflows.txt` 가 applicability 판정의 단일 정본. walker(`scripts/lib/walk_plan.py`) + `reconcile-overlay.sh` 가 이 파일을 **실시간 read** 한다 (36 match wire-active). whitelist 변경 = applicability 판정 변경 (즉발 효력). 본 normative 지위는 현재 어느 ADR 도 미정의했던 공백 — ADR-130 §결정 5 가 명문화.
- **manifest = closure SSOT**: `templates/consumer-scripts.manifest` 가 closure 등재의 단일 정본.
- **3-way 일관성**: whitelist ↔ `.github/workflows/` (live basename) ↔ manifest 의 일관성이 현재 어디서도 강제되지 않는다 — Story D 가 CI gate 로 강제한다.

### 3. closure-완전성 규칙 (scripts + 데이터 + 정책doc 3종)

closure 는 **3종 종속 묶음** 의 의존 폐포다:

1. **scripts** — `scripts/check-*.sh`, `templates/scripts/*.py` 등 workflow 가 `run:` 으로 호출하는 실행 자산.
2. **데이터** — `templates/labels/base-labels.tsv` 등 스크립트가 hard-exit 의존하는 데이터 파일.
3. **정책doc** — 분류 근거·런타임 forbid-list 등 거버넌스 추적/실행 의존 문서(md/tsv).

- **"완전(complete)" 의 정의**: 적용 대상(applicable) 항목의 **hard-block 의미 자산이 모두 manifest 에 등재된 상태**. graceful-no-op 항목은 완전성 판정에서 honest 분류 근거와 함께 별도 처리(완전성 필수 대상 아님 — §"무차별 배포 금지").
- **closure 단위 = manifest entry**: consumer-applicable 판단·closure 묶음의 단위는 개별 파일이 아니라 manifest entry (scripts+데이터+정책doc 종속 묶음)다.

#### 런타임 gate 범위 vs manifest 등재 범위 구분 (depth-1 trade-off 명시 기록)

[verified-via: PL `git show origin/main:templates/scripts/mirror-dependency-closure.py` — AM-2 `transitive_depth_limit=1` (L11) + AM-3 `_DEP_PATTERNS` 2패턴 (L42-47: `scripts/check-[a-z0-9-]+\.sh` + `templates/scripts/[a-z0-9-]+\.py`)]

런타임 closure gate(`mirror-dependency-closure.py`)는 **depth-1 + shell-only(2 패턴)** 이다:

| 범위 | gate 가 잡는가 | 근거 |
|---|---|---|
| yml → `scripts/check-*.sh` (depth-1, 패턴 일치) | **잡음** | AM-3 패턴 1 |
| yml → `templates/scripts/*.py` (depth-1, 패턴 일치) | **잡음** | AM-3 패턴 2 |
| yml → `*.sh` → `*.tsv` (depth-2 데이터 dep, 예: `bootstrap-labels.sh` → `base-labels.tsv`) | **구조적으로 못 잡음** | AM-2 depth-1 한계 + `.tsv` 비패턴 |
| 정책doc(md) 거버넌스 dep | **못 잡음** | 비패턴 + 비실행 |

- **명시적 trade-off**: codeforge 의 closure 규칙은 "런타임 gate 가 잡는 범위" 와 "manifest 가 등재해야 할 실제 범위" 를 구분 정의한다. **데이터(tsv) / 정책doc / depth-2 자산은 manifest 직접 등록으로만 커버** 된다 (런타임 gate 우회). 이는 패키지 매니저가 full transitive closure 를 lockfile 로 닫는 것과 대비되는 codeforge 의 알려진 한계이며, Bazel 형 **declare-or-forbid** (선언 안 된 의존은 사용 금지)의 manifest-직접-등록 대용이다. [source: 요구사항리뷰 lane §9.1 #3 — phantom dependency 누락 위험]
- **강제 메커니즘 = Story D 위임**: depth-2/데이터 dep 강제 방식((A) `mirror-dependency-closure.py` 확장 + AM-3 v2 bump vs (B) 신규 check 분리)은 Story D 설계 결정. 본 entry·ADR-130 은 *규칙·범위* 만 정의.

### 4. 실제 차단면 — "42 미배포 = consumer-broken" 은 과대평가

[verified-via: Story §2.3 + Researcher 정정]

closure 자산 부재가 곧 "consumer-broken" 은 아니다. 차단 여부는 자산의 **실행 의미(execution semantic)** 가 결정한다:

| closure 자산 부재 시 행동 | 차단 여부 | 분류 | evidence |
|---|---|---|---|
| required check 의 1-hop dep (`worktree-first-pre-commit-main-block.yml` → `check-worktree-first-pre-commit-main-block.sh`) | **차단** (continue-on-error:false → PR merge block) | hard-block (실 차단면 i) | [verified-via: 워크플로 `continue-on-error: false` + manifest 미등록] |
| hard-exit 데이터 dep (`bootstrap-labels.sh` → `base-labels.tsv`) | **차단** (tsv 부재 → exit 1) | hard-block (실 차단면 ii) | [verified-via: PL `git ls-tree origin/main templates/labels/base-labels.tsv` 존재 + manifest grep -c base-labels.tsv = 0] |
| self-contained 스크립트 (`check-wording-dictionary.sh`) | **무차단** (scan target 부재 → graceful no-op, EXIT 0) | graceful-no-op | [verified-via: spec — forbid-list in-script, docs 런타임 미read] |

- **실 차단면 2종**: (i) required check 의 1-hop direct dep, (ii) hard-exit 데이터 dep. 이 둘만 hard-block. graceful-no-op 항목은 무차단.

### 5. graceful no-op = job-conditional skip (path-filter skip 금지) — load-bearing 외부 invariant

[verified-via: docs.github.com troubleshooting-required-status-checks, verbatim · 요구사항리뷰 lane §9.1 #1 dual-peer confirmed · PL WebFetch 재확인]

required status check 가 **workflow-level path/branch-filter(또는 commit message)로 skip** 되면:
> "checks associated with that workflow will remain in a 'Pending' state. A pull request that requires those checks to be successful will be blocked from merging."

반면 **job-level conditional(`if:`)로 skip** 되면:
> "If, however, a job within a workflow is skipped due to a conditional, it will report its status as 'Success'."

GitHub 권장 패턴:
> "To use a required check on a job that depends on other jobs, use the `always()` conditional expression in addition to `needs`."

- **invariant**: consumer-applicable workflow 의 graceful no-op(scan target 부재 등)은 **반드시 job-level `if:` conditional skip 으로 구현** 한다. **path-filter / branch-filter skip 금지** (required check "Pending(expected)" 영구 차단 → PR merge 영구 block 유발). 이 invariant 는 Story D 의 3-way 일관성 gate 설계에 직접 적용된다.

[source: https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/collaborating-on-repositories-with-code-quality-features/troubleshooting-required-status-checks]

### 6. 무차별 배포 금지 + mandatory 전환 = whitelist membership 동치

#### 무차별 배포 금지 원칙

"42 전부 배포" 가 아니라 **"차단 의미(hard-block vs graceful-no-op) + consumer 실 가치 기준 선별 배포"**:

- **consumer-applicable 1급 판정 기준** = (a) 차단 의미(hard-block vs graceful-no-op) + (b) consumer 실 가치 의 결합. *파일 존재 여부* 가 아니다.
- **hard-block 자산은 반드시 closure 포함** (required check 1-hop dep + hard-exit 데이터 dep). graceful-no-op·무가치 자산만 제외.
- graceful-no-op 항목은 closure 에 넣어도 무해하나, consumer 가치 0 이면 배포 자체 불필요 (Story C 제거 후보).

#### mandatory 전환 안전성 = whitelist membership 결정과 동치

[verified-via: CLAUDE.md 브랜치보호 표 — wrapper 6-tuple = wrapper-self 만]

closure-check 워크플로(Story D 신규)를 **plugin-self-governance 로 분류 → whitelist 미등재 → consumer 무전파 → 기존 consumer 회귀 0**. 따라서 opt-in→mandatory 전환 안전성 근거 = whitelist membership 결정 (self-governance 분류가 consumer 안전성 제어점).

#### required check 등록 전제 (정밀)

[verified-via: docs.github.com troubleshooting-required-status-checks, verbatim · PL WebFetch — P3 advisory 반영]

> "To be required, status checks must have completed successfully within the chosen **repository** during the past seven days."

- **정밀화**: "protected branch" 가 아닌 **"repository 단위 7일"** 이다 (Story §9.1 P3 advisory — "7일 내 protected branch" 표기 정정).
- workflow 간 **unique job name** 의무: "If you have a check and a status with the same name ... both the check and the status are required" — 동명 중복 시 ambiguous.

[source: https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/collaborating-on-repositories-with-code-quality-features/troubleshooting-required-status-checks]

## 경계

본 entry 영역 (in scope):
- applicability ⊥ closure 직교 모델의 1급 도메인 정의 (두 축 + sequential composition).
- whitelist↔manifest SSOT 관계 + 3-way 일관성 개념.
- closure-완전성 도메인 정의 (scripts+데이터+정책doc 3종, hard-block vs graceful-no-op, depth-1 런타임 gate 한계 trade-off).
- 실제 차단면(과대평가 정정) + 무차별 배포 금지 원칙 + mandatory 전환 동치.
- declarative reconciliation 3-layer 내 위치 + 외부 established pattern 매핑.

본 entry 영역 외 (out of scope):
- ADR-130 §결정 본문 자체 (거버넌스 SSOT — ADR file SSOT). 본 entry = 도메인 narrative anchor only.
- whitelist 의 실 분류 수행 (28 항목 분류 → applicable 항목 closure 등재) = **Story B** (manifest write-owner).
- whitelist plugin-only 제거 + dead-ref resolve = **Story C** (whitelist write-owner).
- 3-way 일관성 CI gate + evidence-checks-registry 74→75 = **Story D**.
- closure-완전성 mechanical 강제 메커니즘 결정 (closure.py 확장 vs 신규 check) = **Story D**.
- ADR-027 consumer-side template adoption signal (boundary disjoint — ADR-027 = consumer-side / ADR-130 = wrapper-side filter).

### 직교 도메인과의 disjoint

| 도메인 | Boundary 시점 | 본 entry 와의 관계 |
|---|---|---|
| **ADR-083 consumer-applicability-filter** (Sunsetted) | 4-way repo-kind + positive whitelist | ADR-130 이 supersede. 8 invariant verbatim 계승. 본 entry = 그 위에 closure 축 1급 정의. |
| **ADR-076 declarative reconciliation upgrade** | §결정 2 11 영역 wrapper SSOT desired state | closure 의 desired-state anchor. applicability/closure = §결정 2 enumeration 의 consumer-applicability gating layer (orthogonal axis). |
| **ADR-027 consumer adoption protocol** | consumer-side template adoption + D4 marker | wrapper-side filter(ADR-130) ↔ consumer-side signal(ADR-027) 경계 disjoint 보존 의무. |
| **ADR-005 dual-channel template↔live mirror** | `templates/` ↔ `.github/` byte-identical self-app | closure 자산(`detect-repo-kind.py` / `mirror-dependency-closure.py`)의 self-app exemption 근거. |
| **declarative-reconciliation.md** (sibling domain-knowledge) | 같은 `upgrade-flow/` 도메인 desired/current/converge | 본 entry 가 그 3-layer 위에 얹힘 (prior art anchor). |

## 관련 ADR

- **Carrier ADR**: `archive/adr/ADR-130-applicability-closure-integrity.md` (ArchitectAgent 신설 — Phase 1 PR scope, applicability ⊥ closure 분류규칙 + closure-완전성 SSOT, §결정 1-9).
- **Superseded base ADR**: `archive/adr/ADR-083-consumer-applicability-filter.md` (Sunsetted — ADR-130 이 supersede. 8 invariant verbatim 계승 base).
- **Desired-state anchor**: `archive/adr/ADR-076-declarative-reconciliation-upgrade.md` (§결정 2 11 영역 wrapper SSOT desired state).
- **Parent Epic**: CFP-2394 (consumer-applicability whitelist↔manifest closure 정합 복원).
- **본 Story**: CFP-2395 (Epic CFP-2394 Story A — gating Story, 후속 B/C/D gate).

직접 cross-ref ADR 목록: ADR-130 / ADR-083 / ADR-076 / ADR-027 / ADR-005 / ADR-058 / ADR-097 / ADR-124 / ADR-125.

## 변경 이력

- 2026-06-25 — Initial creation (CFP-2395 Phase 2 carrier, DeveloperPL self-write — ADR-130 §결정 7 규정 위치·구조 답습. applicability ⊥ closure 직교 모델 + whitelist↔manifest SSOT 관계 + closure-완전성 규칙(scripts+데이터+정책doc) + 실제 차단면 과대평가 정정 + graceful no-op job-conditional skip invariant + 무차별 배포 금지 + declarative reconciliation 3-layer 위치 + 외부 established pattern 매핑 7 절. domain-knowledge 1급 정의 = Phase 2 구현 lane 산출, OMC S1 선례 정합).
