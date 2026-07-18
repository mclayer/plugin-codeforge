---
adr_number: 130
title: "applicability ⊥ closure 분류규칙 + closure-완전성 SSOT — consumer-applicable vs plugin-self-governance 판정 + scripts·데이터·정책doc 의존 폐포 (Epic CFP-2394 Story A)"
status: Accepted
category: governance
date: 2026-06-25
carrier_story: CFP-2395
parent_epic: CFP-2394
supersedes: [ADR-083]
amends: null
amendments: [1, 2]
amendment_log:
  - amendment: 1
    carrier_story: CFP-2398
    date: 2026-06-25
    summary: |
      §결정 5 3-way 일관성 채널 SSOT 정정 (Epic CFP-2394 Story C) — 평가 정본 채널을
      `.github/workflows/`(wrapper-self dogfood live) → `templates/github-workflows/`(consumer-distributable 배포 source) 로 정정.
      template-only consumer workflow (templates 존재 · wrapper `.github` 부재 = consumer-only, wrapper-self N/A)
      를 3-way 일관성 위반으로 오판하지 않도록 채널 SSOT 명문화 (silent harm 차단 방향 — 채널 정확화).
      근거 코드 실측: bootstrap-consumer.sh:284 (cp source = `templates/github-workflows/`) /
      reconcile-overlay.sh:500-510 (consumer repo_kind 일 때만 whitelist basename grep) /
      check-consumer-scripts-manifest.sh:142-146 (closure manifest dep_workflow 경로제약 = `templates/github-workflows/*.{yml,yaml}`) /
      consumer-guide.md:630/875 (templates = consumer-distributable, `.github`/confluence-* = wrapper-self dogfood 전용).
      Story D(3-way 일관성 CI gate) 설계 입력 = templates 채널 anchor 고정 (`.github` 부재 자산을 영구 FAIL 로 오판 차단).
      is_transitional:false 강화 방향 유지 (채널 정확화 — 약화 0). 8 invariant·다른 §결정 무변경 (§결정 5 채널 표기만 정정).
  - amendment: 2
    carrier_story: CFP-2751
    date: 2026-07-18
    summary: |
      §결정 3 closure-완전성 shape-coverage 확장 (P-A 재발 N=3 근절 carrier — mechanical_enforcement_actions
      "pattern_count >= 2 재발 시 follow-up CFP MUST promote" 발동). direction3 런타임 gate 의
      dependency shape 모델을 확장. 기존 closure 모델(§결정 3)은 "yml→scripts/check-*.sh(1-hop)→*.py
      (depth-2)" 를 가정했으나, story-init.yml 은 run-block 이 `python3 scripts/lib/workflow_story_init_*.py`
      를 1-hop 직접 호출하는 미모델링 shape 를 갖는다 (story-init.yml:86/87/115/150/197/579 6종).
      check_whitelist_manifest_3way.py 의 _DEP_PATTERNS(L85-88: 2 shape scripts/check-*.sh /
      templates/scripts/*.py + char-class [a-z0-9-] underscore 없음)가 이 shape 를 구조적으로 못 봐
      방향3 이 story-init helper 6종을 미검출(structural blindness live — 현 HEAD 방향3 PASS/exit0).
      _DEP_PATTERNS 에 shape `scripts/lib/[a-z0-9_-]+\.py` 1개 append 로 coverage 완성 (underscore =
      load-bearing — story-init lib 전부 underscore名, char-class 넓히면 blind 동시 해소; hyphen = 미래
      robust). 기존 2패턴 무변경(append-only, over-match 회귀 0). born-red 회피 ordering = D1(helper
      선등재: repos.py manifest 등재 + chmod 100755)→D2(패턴 활성) reusable pattern. tier 무변경
      (warning-tier, branch-protection 7-tuple 무변경 — required 승격은 별 rollout Story, §결정6). ReDoS-safe
      (단일 bounded quantifier + nested 0 + \b 경계). is_transitional:false 강화 방향 유지 (coverage 확장 —
      약화 0). 8 invariant·다른 §결정 무변경 (§결정 3 shape 모델만 확장 — §결정 3-A).
related_stories:
  - CFP-2395  # 본 ADR 신설 carrier (Epic CFP-2394 Story A — gating Story)
  - CFP-2394  # parent Epic — consumer-applicability whitelist↔manifest closure 정합 복원
  - CFP-2751  # Amendment 2 carrier — direction3 shape-coverage 확장 (yml→scripts/lib/*.py 1-hop, P-A 재발 N=3 근절)
related_adrs:
  - ADR-083   # consumer-applicability-filter (Sunsetted) — 본 ADR 이 supersede. 8 invariant verbatim carry. 분류규칙 재확정 base layer.
  - ADR-076   # §결정 2 declarative reconciliation upgrade — 11 영역 wrapper SSOT desired state. closure 의 desired-state anchor.
  - ADR-027   # consumer adoption protocol — boundary disjoint (ADR-027 = consumer-side / ADR-130 = wrapper-side filter). §결정7.D.2 dead-ref (Story C scope) 인접.
  - ADR-005   # dual-channel template ↔ live byte-identical mirror — closure 자산의 self-app exemption 근거 (detect-repo-kind.py / closure.py).
  - ADR-058   # §결정 5 symmetric evidence-gate — whitelist 축소(약화)는 evidence-gate 통과 시 가능, closure 확장(강화)은 ratchet 충돌 0.
  - ADR-097   # carrier-preserved sunset 선례 — sunset = 효용 소멸 아닌 carrier shift. 신규 ADR-130 supersede 결정의 핵심 선례.
  - ADR-124   # 외부지식 3-단계 — 외부사실(GitHub required-check skip semantic) 의존 검증 선행.
  - ADR-125   # 요구사항리뷰 lane — 본 Story 의 외부사실(§4 invariant) 설계 진입 전 검증 carrier.
  - ADR-037   # version-bump 분류 — Story A 자체 version bump 0. B|C|D 첫 코드변경 시 적용.
  - ADR-063   # marketplace atomic sync — Story A mirrored-field 변경 0 (marketplace_sync_required: false).
related_files:
  - archive/adr/ADR-083-consumer-applicability-filter.md  # 본 ADR 이 supersede (status 전환 — Story A 산출물)
  - archive/adr/ADR-RESERVATION.md  # row 130 active (CFP-2395) — chief author direct write
  - templates/scripts/consumer_applicable_workflows.txt  # applicability whitelist (28) — live SSOT normative 지위 명문화. Story C write-owner.
  - templates/consumer-scripts.manifest  # closure manifest (16) — closure SSOT. Story B write-owner.
  - templates/scripts/mirror-dependency-closure.py  # 런타임 closure gate (AM-2 depth-1 / AM-3 shell-only) — depth-2·데이터 dep 미추적 trade-off 기록 대상.
  - templates/labels/base-labels.tsv  # hard-exit 데이터 dep (depth-2, .tsv 비패턴) — manifest 직접 등록 only. Story B.
  - scripts/lib/walk_plan.py  # walker applicability filter wire LIVE (36 match) — whitelist live read SSOT 근거.
  - docs/domain-knowledge/domain/upgrade-flow/applicability-closure-integrity.md  # domain-knowledge 1급 정의 — 위치·구조 본 ADR 규정, write = Phase 2 구현 lane.
mechanical_enforcement_actions: []   # declaration-only — 본 ADR 은 분류규칙·closure-완전성의 SSOT 등재(강화 ratchet). 신규 lint 신설 0. closure-완전성 mechanical 강제(closure.py 확장 vs 신규 check)는 Story D 로 위임. pattern_count >= 2 재발 시 follow-up CFP MUST promote.
is_transitional: false
sunset_status: null
---

# ADR-130: applicability ⊥ closure 분류규칙 + closure-완전성 SSOT

## 상태

Accepted (2026-06-25 KST, CFP-2395 carrier — Epic CFP-2394 Story A). `is_transitional: false` — 영구 정책. 본 ADR 은 **강화(ratchet) 방향** — ADR-083 의 8 invariant 위에 closure-완전성 규칙 + whitelist normative 지위 + 3-way 일관성 + 무차별 배포 금지를 *확장*으로 쌓는다. 약화 방향이 아니므로 ADR-058 §결정 5 sunset_justification 의무 비대상.

본 ADR 은 ADR-083 (consumer-applicability-filter, Sunsetted) 을 **supersede** 한다 (un-sunset 아님 — §결정 8). ADR-083 의 8 invariant 를 verbatim 계승하고(§결정 1), 그 위에 closure 축을 1급으로 정의한다.

## 본질 선언

> **applicability(수평 필터 — "복사할지 말지")와 closure(수직 폐포 — "복사한다면 무엇과 함께")는 직교(orthogonal)하는 두 축이다. 두 축을 한 축으로 뭉뚱그린 것이 consumer 회귀 결함의 도메인 뿌리다. consumer-applicable 판정은 positive whitelist(applicability SSOT)로, 실행가능 폐포는 manifest(closure SSOT)로 닫는다. closure-완전성은 scripts + 데이터(tsv) + 정책doc(md) 3종을 명시적으로 커버하며, "완전" = 적용 대상 항목의 hard-block 의미 자산이 모두 manifest 에 등재된 상태다.**

## 컨텍스트

Epic CFP-2394 는 consumer-applicability whitelist(`consumer_applicable_workflows.txt` = 28 [verified-via: PL `git show origin/main` grep -cvE comment/blank = 28]) ↔ closure manifest(`consumer-scripts.manifest` = 16 [verified-via: 동 실측 = 16]) 의 격차를 복원한다. 이 격차의 표면 증상은 "applicable 로 판정된 항목의 closure 가 manifest 에 미등재되어 consumer 가 실행 단계에서 깨지는" 것이다.

ADR-083 이 applicability 필터(4-way repo-kind + positive whitelist)를 정의했으나, **closure 축은 1급으로 정의되지 않았고**, whitelist 의 normative 지위 역시 어느 ADR 에도 미정의 상태다. 본 ADR 이 그 공백을 메운다.

### 결함의 도메인 정체 — applicability 통과 / closure 불완전

사용자 원문의 "full closure(scripts + 데이터 + 정책doc) 가 실제 배포" = whitelist 가 "applicable" 로 판정한 항목의 closure 가 manifest 에 등재되지 않아 consumer 가 깨지는 상태다. 즉 *applicability 판정은 통과했으나 closure 가 불완전*하다.

### "42 미배포 = consumer-broken" 은 과대평가 (실 차단면 정밀화)

[verified-via: Story §2.3 + Researcher 정정] closure 자산 부재가 곧 "consumer-broken" 은 아니다. 차단 여부는 자산의 **실행 의미(execution semantic)** 가 결정한다:

| closure 자산 부재 시 행동 | 차단 여부 | 분류 | evidence |
|---|---|---|---|
| required check 의 1-hop dep (`worktree-first-pre-commit-main-block.yml` → `check-worktree-first-pre-commit-main-block.sh`) | **차단** (continue-on-error:false → PR merge block) | hard-block (실 차단면 i) | [verified-via: 워크플로 `continue-on-error: false` + manifest 미등록] |
| hard-exit 데이터 dep (`bootstrap-labels.sh` → `base-labels.tsv`) | **차단** (tsv 부재 → exit 1) | hard-block (실 차단면 ii) | [verified-via: PL `git ls-tree origin/main templates/labels/base-labels.tsv` 존재 + manifest grep -c base-labels.tsv = 0] |
| self-contained 스크립트 (`check-wording-dictionary.sh`) | **무차단** (scan target 부재 → graceful no-op, EXIT 0) | graceful-no-op | [verified-via: spec — forbid-list in-script, docs 런타임 미read] |

## 결정

### 결정 1 — ADR-083 8 invariant verbatim 계승 (약화 0)

ADR-083 §결정 1-6 의 8개 invariant 를 **verbatim 보존**한다. 본 ADR 의 추가분은 이 8 invariant 위에 **확장(강화 방향)** 으로 쌓이므로 ADR-058 symmetric evidence-gate 충돌 0.

1. **4-way repo-kind truth-table** (`plugin` / `consumer` / `mixed` / `unknown` closed-set) — `templates/scripts/detect-repo-kind.py` 가 Signal A(`.claude-plugin/plugin.json`) + Signal B(`.claude/_overlay/project.yaml`) 존재 조합으로 분류. open-set 확장(`library`/`monorepo`)은 본 ADR scope 외.
2. **positive whitelist** — whitelist 안 = consumer copy / whitelist 밖 = consumer skip (default skip). **blacklist 금지** (새 workflow 신설 시 blacklist 부재 = consumer silent 유입 silent harm 재발).
3. **mixed self-app exemption** — `repo_kind == "mixed"` (wrapper dogfood repo) = full workflow set 적용 (filter skip). `mixed` = `plugin` 우선 분류 (self-loop bug 차단).
4. **fail-closed unknown** — `repo_kind == "unknown"` = no copy, abort with error log (exit 1). silent default 금지. `--force-unknown-as-consumer` 신설 금지.
5. **signal filesystem-only** — 두 signal 모두 consumer-side filesystem 안. network call 0, gh api 0, marketplace.json membership check 0 (offline-first invariant + trust boundary 명확).
6. **sequential composition** — closure resolver 먼저 → applicability filter 다음 → cp. 두 hook 의 판정 순서 invariant (closure 가 "무엇과 함께", filter 가 "복사할지" — 서로 간섭 0).
7. **boundary disjoint** — ADR-027 (consumer-side template adoption signal) ↔ ADR-083/130 (wrapper-side filter). 경계 disjoint 보존 의무.
8. **carrier-preserved sunset** — sunset = 효용 소멸 아닌 carrier shift (효용 이전 = 강화 방향). ADR-083 효용은 walker per-step filter 로 carry LIVE (§결정 8).

> **약화 차단 invariant 보존**: ADR-083 이 차단한 약화 방향(filter 약화 / fail-open default / whitelist 무조건 축소)은 본 ADR 에서도 차단 유지. 단 whitelist 축소는 ADR-058 §결정 5 symmetric evidence-gate 통과 시 가능(절대 금지 아님 — §결정 9).

### 결정 2 — applicability ⊥ closure 직교 모델 (두 독립 축)

본 도메인의 핵심은 **두 개의 독립 축**이다. 한 축으로 뭉뚱그린 것이 결함의 도메인 뿌리다.

| 축 | 질문 | 도메인 정의 | 판정 위치(SSOT) |
|---|---|---|---|
| **applicability** (수평) | "이 자산이 consumer repo 에 *적용 대상*인가?" | consumer-applicable vs plugin-self-governance 분류. positive whitelist 기반. | `consumer_applicable_workflows.txt` (whitelist) |
| **closure** (수직) | "적용 대상 자산이 *실행 가능*하려면 무엇이 함께 배포돼야 하는가?" | workflow → scripts → 데이터(tsv) → 정책doc(md) 의 의존 폐포. | `consumer-scripts.manifest` (manifest) + 런타임 `mirror-dependency-closure.py` |

- **직교성** [verified-via: ADR-083 §"기존 SSOT 의 한계" — "closure resolver = vertical bundle / consumer-applicability filter = horizontal axis, disjoint super-class"]: applicability = "복사할지 말지"(수평 필터), closure = "복사한다면 무엇과 함께"(수직 폐포). 두 축은 sequential composition (closure 먼저 → filter → cp)으로 합성되나 서로의 판정에 간섭하지 않는다.
- **외부 established concept 매핑** [verified-via: 요구사항리뷰 lane §9.1 #3 confirmed · 다출처]: closure = **transitive dependency closure** (npm/pip/cargo lockfile, Bazel — lockfile 이 transitive dep 를 닫음). applicability = **conditional resource provisioning** (Helm `condition`/`tags`, Kustomize overlay, Ansible `when:`). [source: npm package-lock / PyPA pylock.toml / bazel strict-deps]

### 결정 3 — closure-완전성 규칙 (scripts + 데이터 + 정책doc 3종)

closure 는 **3종 종속 묶음**의 의존 폐포다:

1. **scripts** — `scripts/check-*.sh`, `templates/scripts/*.py` 등 workflow 가 `run:` 으로 호출하는 실행 자산.
2. **데이터** — `templates/labels/base-labels.tsv` 등 스크립트가 hard-exit 의존하는 데이터 파일.
3. **정책doc** — 분류 근거·런타임 forbid-list 등 거버넌스 추적/실행 의존 문서(md/tsv).

**"완전(complete)" 의 정의**: 적용 대상(applicable) 항목의 **hard-block 의미 자산이 모두 manifest 에 등재된 상태**. graceful-no-op 항목은 완전성 판정에서 honest 분류 근거와 함께 별도 처리(완전성 필수 대상 아님 — §결정 6).

**closure 단위 = manifest entry**: consumer-applicable 판단·closure 묶음의 단위는 개별 파일이 아니라 manifest entry (scripts+데이터+정책doc 종속 묶음)다. [Story §5.4 암묵 가정 verified]

#### 런타임 gate 범위 vs manifest 등재 범위 구분 (depth-1 trade-off 명시 기록)

[verified-via: PL `git show origin/main:templates/scripts/mirror-dependency-closure.py` — AM-2 `transitive_depth_limit=1` (L11) + AM-3 `_DEP_PATTERNS` 2패턴 (L42-47: `scripts/check-[a-z0-9-]+\.sh` + `templates/scripts/[a-z0-9-]+\.py`)]

런타임 closure gate(`mirror-dependency-closure.py`)는 **depth-1 + shell-only(2 패턴)** 이다. 따라서:

| 범위 | gate 가 잡는가 | 근거 |
|---|---|---|
| yml → `scripts/check-*.sh` (depth-1, 패턴 일치) | **잡음** | AM-3 패턴 1 |
| yml → `templates/scripts/*.py` (depth-1, 패턴 일치) | **잡음** | AM-3 패턴 2 |
| yml → `*.sh` → `*.tsv` (depth-2 데이터 dep, 예: `bootstrap-labels.sh` → `base-labels.tsv`) | **구조적으로 못 잡음** | AM-2 depth-1 한계 + `.tsv` 비패턴 |
| 정책doc(md) 거버넌스 dep | **못 잡음** | 비패턴 + 비실행 |

**명시적 trade-off 기록**: codeforge 의 closure 규칙은 "런타임 gate 가 잡는 범위" 와 "manifest 가 등재해야 할 실제 범위" 를 구분 정의한다. **데이터(tsv) / 정책doc / depth-2 자산은 manifest 직접 등록으로만 커버**된다 (런타임 gate 우회). 이는 패키지 매니저가 full transitive closure 를 lockfile 로 닫는 것과 대비되는 codeforge 의 알려진 한계이며, Bazel 형 **declare-or-forbid**(선언 안 된 의존은 사용 금지)의 manifest-직접-등록 대용이다. [source: 요구사항리뷰 lane §9.1 #3 confirmed — phantom dependency 누락 위험]

**closure-완전성 mechanical 강제 방식 결정 = Story D 로 위임**: depth-2/데이터 dep 을 강제하는 방식은 (옵션 A) `mirror-dependency-closure.py` 확장 + AM-3 v2 bump vs (옵션 B) 신규 check 분리 — 본 ADR 은 *규칙·범위*만 정의하고, 강제 메커니즘 구현은 Story D 의 설계 결정으로 명시 위임한다.

#### shape-coverage 확장 (§결정 3-A — Amendment 2, CFP-2751 — P-A 재발 N=3 근절)

[verified-via: PL/ArchitectAgent firsthand — `check_whitelist_manifest_3way.py` L85-88 `_DEP_PATTERNS` (2 shape) / `story-init.yml` L86/87/115/150/197/579 (yml→scripts/lib/*.py 1-hop 직접호출 6종) / 현 HEAD 방향3 = PASS/exit 0 (structural blindness live) / `consumer-scripts.manifest` L95-99 (story-init lib 5종 등재, repos.py 미등재)]

**미모델링 shape 발견**: 위 §결정 3 depth-1 trade-off 표는 방향3 런타임 gate 의 dependency shape 를 두 가지("yml→`scripts/check-*.sh`", "yml→`templates/scripts/*.py`")로 모델링했다. 그러나 `story-init.yml` 은 run-block 이 `python3 scripts/lib/workflow_story_init_*.py` 를 **1-hop 직접 호출**하는 **세 번째 shape**("yml→`scripts/lib/*.py` 1-hop 직접")를 갖는다. 이 shape 는:

- **CFP-2412 방향3 게이트(`check_whitelist_manifest_3way.py`)의 `_DEP_PATTERNS`(L85-88)가 인식하지 못한다** — 등재 패턴 2종(`scripts/check-[a-z0-9-]+\.sh` / `templates/scripts/[a-z0-9-]+\.py`)은 `scripts/lib/` 접두를 커버하지 않고, char-class `[a-z0-9-]` 는 underscore 를 포함하지 않아 underscore名(`workflow_story_init_*.py`) 자체가 미매칭. **이중 blind**.
- 결과: 방향3 이 whitelist workflow(`story-init.yml`)의 hard-block closure 자산(story-init helper 6종)을 **구조적으로 못 본다** — 현 HEAD 방향3 = PASS/exit 0 이지만 이는 검증이 아니라 blindness. 이 갭이 P-A 재발(N=3: MKT-001 / MKT-002 / MSM-001)의 도메인 뿌리다.

**결정 (Amendment 2)**:

1. **shape 추가** — `_DEP_PATTERNS` 에 shape `re.compile(r"\bscripts/lib/[a-z0-9_-]+\.py\b")` **1개를 append** 하여 "yml→`scripts/lib/*.py` 1-hop 직접" shape 의 closure-완전성 coverage 를 완성한다. §결정 3 의 3종 종속 묶음 규칙(scripts + 데이터 + 정책doc)은 무변경 — 본 확장은 그 규칙의 *shape 인식 표면*을 넓히는 것이다.
2. **char-class underscore 확장 근거** — `[a-z0-9_-]`(underscore + hyphen union). underscore 는 **load-bearing**: Python module 파일명 규약(PEP 8 snake_case)상 `scripts/lib/*.py` helper 는 underscore名이 지배적(story-init lib 6종 전부 underscore名)이므로, 형제 2패턴의 `[a-z0-9-]`(underscore 없음)을 그대로 복사하면 신규 shape 가 inert 가 된다. hyphen 은 미래 robustness(현 corpus 무영향).
3. **append-only(회귀 0)** — 기존 2패턴의 char-class·경로 접두는 넓히지 않는다(over-match 회귀 회피). 신규 shape 는 별 리스트 원소로만 추가 → 방향1/2/3 기존 판정 불변.
4. **born-red 회피 ordering (reusable pattern)** — coverage 를 넓히면 기존 미등재 closure 자산이 즉시 위반으로 켜진다(born-red = self-block). 따라서 **선등재(gap 해소) → 패턴 활성** 순서를 강제한다: (D1) 미등재 helper(`workflow_story_init_project_config_repos.py`)를 manifest 에 선등재 + `chmod +x`(100755) → (D2) `_DEP_PATTERNS` 확장. firsthand 실측: whitelist-scoped `scripts/lib/*.py` run-block 직접호출 중 현 미등재 = repos.py 1종뿐 → D1 후 born-green. 이 "선등재→패턴활성" 은 coverage 확장 게이트의 재사용 가능 패턴이다.
5. **scan surface·함정 무변경** — whitelist scoping(방향3 L321 `for name in whitelist`) + 주석 strip(`_YAML_COMMENT_LINE`) 재사용으로 두 false-RED 함정(① 주석-언급 helper / ② plugin-only workflow helper)이 자동 중화된다. 신규 로직 0.
6. **tier 무변경(warning)** — 본 확장은 warning-tier(continue-on-error) 유지 — branch-protection 7-tuple 무변경. §결정 6 의 warning→required 7일-green 승격 절차는 별 rollout Story 소관(본 Amendment 대상 아님). §1 요구의 "fail-closed" 는 logic-level 결정성(silent-pass 금지)으로 해석 — 검출 로직이 미등재를 결정적으로 보고.

**정합**: 본 확장은 §결정 3 closure-완전성 규칙의 **coverage 확장(강화 방향, ratchet)** 이므로 ADR-058 §결정 5 sunset_justification 비대상 + 8 invariant·다른 §결정 무변경. carrier = CFP-2751 (mechanical_enforcement_actions 의 "pattern_count >= 2 재발 시 follow-up CFP MUST promote" 발동 이행). repos.py 출처 = ADR-069 Amendment 1(multi-repo component routing, yq fallback helper).

### 결정 4 — graceful no-op = job-conditional skip (path-filter skip 금지) [load-bearing 외부 invariant]

[verified-via: docs.github.com troubleshooting-required-status-checks, verbatim · 요구사항리뷰 lane §9.1 #1 dual-peer confirmed · PL WebFetch 재확인]

required status check 가 **workflow-level path/branch-filter(또는 commit message)로 skip** 되면:
> "checks associated with that workflow will remain in a 'Pending' state. A pull request that requires those checks to be successful will be blocked from merging."

반면 **job-level conditional(`if:`)로 skip** 되면:
> "If, however, a job within a workflow is skipped due to a conditional, it will report its status as 'Success'."

GitHub 권장 패턴:
> "To use a required check on a job that depends on other jobs, use the `always()` conditional expression in addition to `needs`."

**invariant (Story A 확정)**: consumer-applicable workflow 의 graceful no-op(scan target 부재 등)은 **반드시 job-level `if:` conditional skip 으로 구현**한다. **path-filter / branch-filter skip 금지** (required check "Pending(expected)" 영구 차단 → PR merge 영구 block 유발). 이 invariant 는 Story D 의 3-way 일관성 gate 설계에 직접 적용된다.

[source: https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/collaborating-on-repositories-with-code-quality-features/troubleshooting-required-status-checks]

### 결정 5 — whitelist = live SSOT normative 지위 명문화

[verified-via: PL `git show origin/main:scripts/lib/walk_plan.py` grep `applicable_to|repo_kind|consumer_applicable|detect-repo-kind|FILTER_REPO_KIND` = 36 match → wire LIVE]

현재 어느 ADR 도 whitelist 의 normative 지위를 정의하지 않는다 (Continuity/Feasibility 공백). 본 ADR 이 명문화한다:

- **whitelist = applicability SSOT (live)**: `templates/scripts/consumer_applicable_workflows.txt` 가 applicability 판정의 단일 정본이다. walker(`scripts/lib/walk_plan.py`) + `reconcile-overlay.sh` 가 이 파일을 **실시간 read** 한다 (36 match wire-active). whitelist 변경 = applicability 판정 변경 (즉발 효력).
- **manifest = closure SSOT**: `templates/consumer-scripts.manifest` 가 closure 등재의 단일 정본이다.
- **3-way 일관성**: whitelist ↔ **`templates/github-workflows/`** (배포 source basename) ↔ manifest 의 일관성이 현재 어디서도 강제되지 않는다 — Story D 가 CI gate 로 강제한다. [Amendment 1 정정 — 구 표기 `.github/workflows/`(wrapper-self dogfood live)는 평가 정본 채널이 아니다. §결정 5-A 참조.]

#### 채널 SSOT 정정 (§결정 5-A — Amendment 1, Epic CFP-2394 Story C)

[verified-via: PL 코드 실측 — `git show origin/main` / worktree HEAD]

3-way 일관성의 평가 정본 채널은 **`templates/github-workflows/`** (consumer-distributable 배포 source) 이지, **`.github/workflows/`** (wrapper-self dogfood live) 가 **아니다**. ADR-083 path drift 와 동질의 채널 표기 drift 를 정정한다.

| 작용점 | anchor 채널 | evidence |
|---|---|---|
| consumer 복사 source (bootstrap) | `templates/github-workflows/` | [verified-via: `scripts/bootstrap-consumer.sh:284` — `cp "$PLUGIN_ROOT/templates/github-workflows/$w" ".github/workflows/$w"`] |
| consumer applicability filter (reconcile) | `templates/github-workflows/` 의 wrapper_file basename ↔ whitelist | [verified-via: `scripts/reconcile-overlay.sh:500-510` — `repo_kind == consumer` 일 때만 `grep -Fxq basename` whitelist 매칭, miss=skip] |
| closure manifest 경로제약 | `templates/github-workflows/*.{yml,yaml}` | [verified-via: `scripts/check-consumer-scripts-manifest.sh:142-146` — dep_workflow 경로제약 = `templates/github-workflows/*.{yml,yaml}` direct child] |
| 채널 의미 분리 | templates = consumer-distributable / `.github`·confluence-* = wrapper-self dogfood 전용 | [verified-via: `docs/consumer-guide.md:630/875`] |

**template-only consumer workflow 처리 (load-bearing — silent harm 차단)**: `templates/github-workflows/` 에는 존재하나 wrapper `.github/workflows/` 에는 부재한 워크플로(= **consumer-only template**, wrapper-self 미채택)는 dual-channel 의 정상 분기다. 평가 채널을 `.github/workflows/` 로 잘못 anchor 하면 이런 consumer-only template 을 "whitelist 가 가리키나 대상 부재 = dead-ref" 로 **오판**해 silent 제거 → consumer 가 해당 거버넌스를 silent 하게 잃는다(본 ADR 이 차단하려는 silent harm 그 자체). 따라서:

- **3-way gate 의 채널 anchor = `templates/github-workflows/` 단일 SSOT.** whitelist basename 의 대상 실존 검증은 templates 채널에서만 수행한다. `.github/workflows/` 부재는 일관성 위반 신호가 **아니다** (consumer-only template = 정상).
- **Story D CI gate 직접 적용**: Story D 의 3-way 일관성 mechanical 강제는 templates 채널을 anchor 로 설계해야 한다. `.github` anchor 시 consumer-only template 을 영구 FAIL 로 오판 → PR merge 영구 block.

[verified-via: Story C 실측 — `templates/github-workflows/` 에만 존재하고 `.github/workflows/` 부재인 whitelist 등재 항목 3건(`story-section-1-immutable.yml` / `subissue-from-impl-manifest.yml` / `fix-ledger-sync.yml`) = consumer-only template(dead 아님). templates 채널 기준 whitelist real-dead = 0건.]

#### 경로 정정 (ADR-083 path drift)

[verified-via: PL Bash — `templates/consumer_applicable_workflows.txt` (bare templates/) 부재 / `templates/scripts/consumer_applicable_workflows.txt` 존재]

ADR-083 §결정 2 본문은 whitelist 경로를 `templates/consumer_applicable_workflows.txt` (bare `templates/`)로 표기하나, 실제 경로는 **`templates/scripts/consumer_applicable_workflows.txt`** 다. 본 ADR 이 정정한다 (Story B 주의 — manifest/whitelist 경로 참조 시).

### 결정 6 — 무차별 배포 금지 + mandatory 전환 = whitelist membership 동치

#### 무차별 배포 금지 원칙

"42 전부 배포" 가 아니라 **"차단 의미(hard-block vs graceful-no-op) + consumer 실 가치 기준 선별 배포"**:

- **consumer-applicable 1급 판정 기준** = (a) 차단 의미(hard-block vs graceful-no-op) + (b) consumer 실 가치 의 결합. *파일 존재 여부*가 아니다.
- **hard-block 자산은 반드시 closure 포함** (required check 1-hop dep + hard-exit 데이터 dep). graceful-no-op·무가치 자산만 제외.
- graceful-no-op 항목은 closure 에 넣어도 무해하나, consumer 가치 0 이면 배포 자체 불필요 (Story C 제거 후보).

#### mandatory 전환 안전성 = whitelist membership 결정과 동치

[verified-via: CLAUDE.md 브랜치보호 표 — wrapper 6-tuple = wrapper-self 만]

closure-check 워크플로(Story D 신규)를 **plugin-self-governance 로 분류 → whitelist 미등재 → consumer 무전파 → 기존 consumer 회귀 0**. 따라서 opt-in→mandatory 전환 안전성 근거 = whitelist membership 결정 (self-governance 분류가 consumer 안전성 제어점).

#### required check 등록 전제 (정밀)

[verified-via: docs.github.com troubleshooting-required-status-checks, verbatim · PL WebFetch — P3 advisory 반영]

opt-in→mandatory 전환 시 GitHub required check 등록 전제:
> "To be required, status checks must have completed successfully within the chosen **repository** during the past seven days."

- **정밀화**: "protected branch" 가 아닌 **"repository 단위 7일"** 이다 (Story §9.1 P3 advisory — §6/§5.2 AC-5.4 의 "7일 내 protected branch" 표기 정정).
- workflow 간 **unique job name** 의무: "If you have a check and a status with the same name, and you select that name as a required status check, both the check and the status are required" — 동명 중복 시 ambiguous.

[source: https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/collaborating-on-repositories-with-code-quality-features/troubleshooting-required-status-checks]

### 결정 7 — domain-knowledge 위치·구조 규정 (write = Phase 2)

[verified-via: 선례 `docs/domain-knowledge/domain/upgrade-flow/declarative-reconciliation.md` 존재 + Feasibility/Continuity 합치 `concept/` 부적합]

domain-knowledge 1급 정의 문서:

- **경로**: `docs/domain-knowledge/domain/upgrade-flow/applicability-closure-integrity.md` (`domain/` — `concept/` 부적합. 선례 = `declarative-reconciliation.md` 동일 `upgrade-flow/` 도메인).
- **frontmatter**: doc section schema 정합 (`frontmatter_required: true`, owner = `codeforge-requirements:DomainAgent`, kind = domain).
- **구조(필수 절)**: (1) applicability ⊥ closure 직교 모델 1급 정의 / (2) whitelist↔manifest SSOT 관계 + 3-way 일관성 / (3) closure-완전성 도메인 정의(scripts+데이터+정책doc, hard-block vs graceful-no-op) / (4) 실제 차단면(과대평가 정정) / (5) 무차별 배포 금지 원칙 / (6) declarative reconciliation 3-layer 내 위치 (prior art cross-ref) / (7) 외부 established pattern 매핑(transitive closure / conditional provisioning).
- **write 시점**: **Phase 2 구현 lane** 산출 (OMC S1 선례 — domain-knowledge=Phase2). 설계 lane(Story A)은 위치·구조만 규정.

### 결정 8 — ADR-083 supersede (un-sunset 아님)

본 ADR 은 ADR-083 을 **supersede** 한다 (frontmatter `supersedes: [ADR-083]`). un-sunset(재활성)이 **아니다**. 근거:

- **(a) sunset paradigm 모순 회피** [verified-via: walk_plan.py 36 match wire LIVE]: ADR-083 의 sunset 은 실제로 walker 로 carry 됐다. **Amendment 3 의 "0 match drift" 서술은 stale** — CFP-1293 Phase 2 에서 walk_plan.py 에 filter wire 가 실재하게 됐으므로 현재는 36 match. 따라서 sunset 은 정당하며, un-sunset 은 "carrier shift 완료" 를 되돌리는 모순. (※ ADR-083 Amendment 3 의 "0 match drift" 문구를 verbatim 인용 금지 — 당시 시점 한정 stale fact.)
- **(b) ADR-097 carrier-preserved sunset 선례**: sunset 효용을 신규 ADR 가 명시적으로 계승(supersedes)하는 것이 이력 명료.
- **(c) ADR-125/126 신규-ADR 선례**: 외부지식 arc 도 신규 ADR 로 처리.
- **(d) 축 분리**: ADR-083 의 sunset 사유(walker carry)와 신규 분류규칙(데이터+정책doc closure 완전성)이 *다른 축* — 별 ADR 가 이력 추적성 우수.
- **un-sunset 리스크 회피**: Amendment 1-3 충돌(부분 계승 vs 전면 재활성)의 모호성 차단.

**ADR-083 frontmatter 처리**: ADR-083 의 `sunset_status: Sunsetted` 보존. 본 ADR-130 이 ADR-083 을 supersede 하므로 ADR-083 에 `superseded_by: ADR-130` cross-ref 추가 (Phase 2 구현 lane 에서 ADR-083 frontmatter 갱신 — Story A 는 본 ADR-130 측 `supersedes` 명문화로 충분).

### 결정 9 — whitelist 축소(약화) vs closure 확장(강화) ratchet 정합

[verified-via: ADR-083 약화 차단 invariant + ADR-058 §결정 5 symmetric evidence-gate]

- **whitelist 축소(Story C plugin-only 제거)** = ADR-083 약화 차단 invariant 의 *형식적* 대상이나, **ADR-058 §결정 5 symmetric evidence-gate 통과 시 가능**: "plugin-self-governance 로 정확히 분류된 항목의 whitelist 제거" 는 silent harm 재발이 아니라 *오분류 정정*이므로, evidence(분류 근거 + closure 무영향)와 함께 허용.
- **closure 확장(Story B manifest 등재 추가)** = ratchet **강화** 방향 → ADR-083/130 invariant 와 **충돌 0**.
- 두 방향 모두 본 ADR 의 1급 판정 기준(§결정 6 hard-block + consumer 가치)을 evidence 로 삼는다.

## 결과

### Positive

- applicability ⊥ closure 직교 모델의 1급 ADR 정의 (현재 ADR-083 본문 언급만 → SSOT 승격).
- closure-완전성 규칙(scripts+데이터+정책doc 3종) + "완전" 정의 확정 → Story B 분류·등재의 규칙 base.
- whitelist = live SSOT normative 지위 명문화 (현재 공백 해소).
- graceful no-op = job-conditional skip invariant (path-filter skip 영구 차단 함정 차단) → Story D gate 설계 안전판.
- mandatory 전환 = whitelist membership 동치 → consumer 회귀 0 보장.
- ADR-083 8 invariant verbatim 계승 (약화 0) + supersede 로 이력 명료.

### Negative

- whitelist/manifest 유지 비용 (새 workflow 신설 시 applicability + closure 명시 의무) — ADR-083 Negative 계승.
- closure-완전성 런타임 강제의 depth-1 한계 (데이터/정책doc/depth-2 = manifest 직접 등록 only) → Story D 가 강제 메커니즘 결정 필요.
- 3-way 일관성 강제 부재 (Story D 까지 수동 일관성 유지) — 본 ADR 은 규칙만, 강제는 D.

### Neutral

- **Story A 자체 코드변경 = 0** [verified-via: ChangeImpact]. 산출물 = ADR-130 + (Phase 2) domain-knowledge 문서. A 는 후속 Story B/C/D 가 건드릴 파일을 *식별·gate* 한다.
- version bump 0 (Story A). marketplace mirrored-field 변경 0 (ADR-063 atomic invariant 발효 조건 미충족).
- domain-knowledge 실 write = Phase 2 구현 lane (§결정 7).

## 관련 파일

- `templates/scripts/consumer_applicable_workflows.txt` — applicability whitelist (28, live SSOT). Story C write-owner.
- `templates/consumer-scripts.manifest` — closure manifest (16, closure SSOT). Story B write-owner.
- `templates/scripts/mirror-dependency-closure.py` — 런타임 closure gate (AM-2 depth-1 / AM-3 shell-only).
- `templates/labels/base-labels.tsv` — hard-exit 데이터 dep (depth-2, manifest 직접 등록 only).
- `scripts/lib/walk_plan.py` — walker applicability filter wire LIVE (36 match).
- `archive/adr/ADR-083-consumer-applicability-filter.md` — 본 ADR 이 supersede.
- `docs/domain-knowledge/domain/upgrade-flow/applicability-closure-integrity.md` — domain-knowledge 1급 정의 (write = Phase 2).
- `archive/adr/ADR-RESERVATION.md` — row 130 active (CFP-2395).
