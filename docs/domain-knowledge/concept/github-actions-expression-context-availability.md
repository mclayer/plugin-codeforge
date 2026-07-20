---
kind: concept_definition
type: domain-knowledge
slug: github-actions-expression-context-availability
title: GitHub Actions expression context-availability — 평가 시점(workflow key)별 available context/function 불일치로 job-level 조건식에 디스크-접근 함수(hashFiles)를 쓰면 load-time schema-invalid → 게이트 born-invalid(non-existent) 결함 class
status: Active
updated: 2026-07-01
carrier_story: CFP-2530
related_adrs:
  - ADR-136  # frontend 품질게이트 표준 — D1 stylelint CSS lint. 결정3(job-level graceful no-op) 예시 errata = Amendment 2(CFP-2530). 결정13 = 본 결함 정정 anchor
  - ADR-130  # path-filter 금지 invariant(§결정4) — required check permanent-pending 함정. 본 결함의 "왜 path-filter 대신 job-level if 를 썼나" 배경 + 정정 후에도 path-filter 금지 유지
  - ADR-119  # research-before-claims — 외부 기술 사실(GitHub Actions context-availability 의미론) 자료조사+출처인용 의무
related_concepts:
  - config-extends-resolution-basedir      # CFP-2527 sibling — 같은 D1 게이트가 실효 0 인 결함이나 mechanism 상이(runtime config-resolution 실패 = 로드는 됨 / 본건 = load-time schema-invalid = 로드 자체 실패). 층위 스택의 더 깊은 층
  - mutation-based-hollow-gate-detection    # hollow-gate 일반 — 코드 실행은 되나 동작 미검증. 본건 = 실행조차 안 되는 non-existent gate 극단형. discriminating fixture(mutation-kill) 회귀 채널 anchor
  - lane-verification-floor                 # 게이트 자기 무결성(meta) — 로드조차 안 되는 게이트는 floor 미달의 극단
tags:
  - github-actions
  - expression-context-availability
  - hashFiles
  - job-level-if
  - step-level-if
  - load-time-schema-invalid
  - born-invalid-gate
  - non-existent-gate
  - actionlint
  - graceful-skip
sources:
  - https://docs.github.com/en/actions/reference/accessing-contextual-information-about-workflow-runs   # Contexts reference / Context availability 표 — workflow key 별 available context/function
  - https://github.com/actions/runner/blob/main/docs/adrs/0279-hashFiles-expression-function.md         # actions/runner ADR 0279 — hashFiles() runner-side 전용(디스크 read 필요), server-side 평가 시 runtime error
  - https://github.com/rhysd/actionlint/blob/v1.7.12/docs/checks.md   # actionlint ctx-spfunc-availability check — job-level if 에서 hashFiles 부적격 검출
  - https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/collaborating-on-repositories-with-code-quality-features/troubleshooting-required-status-checks   # required check skip 3-경로(trigger-filter Pending vs job-if Success vs step exit 0 genuine)
---

# GitHub Actions expression context-availability

## 정의

**GitHub Actions expression context-availability 결함 class** = workflow 의 expression(`${{ ... }}` / `if:`)이 **평가되는 workflow key 별로 available 한 context·special-function 집합이 다르다**는 사실을 위반해, 어떤 key 에서 available 하지 않은 함수/context 를 쓰는 바람에 GitHub 이 workflow 를 **로드하는 시점에 schema-invalid 로 reject** 하고, 그 결과 게이트(job)가 **한 번도 로드·실행되지 못하는**(born-invalid) 결함이다. 대표 실증 = job-level `jobs.<job_id>.if` 에 디스크-접근 함수 `hashFiles(...)` 를 쓴 경우 — `hashFiles` 는 job-level `if:` 의 available function 집합에 없어 workflow 전체가 load-time invalid 가 되고, 모든 run 이 job 생성 이전에 0 초 fail 한다.

핵심 메커니즘 = **"평가 시점" 이 "가용성" 을 결정한다**. `jobs.<job_id>.if` 는 GitHub *서버* 가 runner 배정 *전* 에 평가한다(어느 job 을 돌릴지 결정하는 단계) → 이 시점엔 아직 runner·디스크가 없다. 반면 `jobs.<job_id>.steps.<step_id>.if` 는 job 이 runner 에 배정된 뒤 *runner-side* 에서 평가한다 → 디스크 접근 가능. 따라서 디스크의 파일을 읽어 hash 하는 `hashFiles` 는 step-level 에서만 available 하고 job-level 에선 부적격이다.

이 결함은 [[config-extends-resolution-basedir]](CFP-2527, 같은 D1 게이트)보다 **한 층 더 깊다** — config-resolution 결함은 workflow 가 *로드·실행은 되나* runtime 에 config 를 못 찾아 죽는 hollow-gate(검증 0)인 반면, 본 결함은 workflow 가 *로드조차 안 되는* **non-existent gate**(실행 자체 0)다. 층위 스택: **load-time schema-invalid(본건) → runtime resolution 실패(config-extends-basedir) → 검증은 되나 signal 오염(cosmetic noise) → mutation 생존(hollow-gate 일반)**.

## 컨텍스트

CFP-2530 동인 = ADR-136 D1 CSS lint 게이트(`css-lint.yml` 양 copy)의 born-invalid 실증. ADR-136 결정3 은 D1 graceful no-op(CSS 자산 0 인 frontend-무관 repo 에서 게이트가 비차단 통과)을 실현하는 "권장 형태" 로 job-level `if: hashFiles('**/*.css', '**/*.scss', '**/*.html') != ''` 를 명문화했다. 이 예시가 문서적 뿌리로 css-lint.yml 양 copy(`.github/workflows/` + `templates/github-workflows/`, byte-identical parity)에 그대로 이식됐다.

결정3 이 job-level conditional 을 택한 배경은 정당하다 — ADR-130 §결정4 가 workflow-level `on: paths:` path-filter 를 금지하기 때문이다(required check 가 path-filter 로 skip 되면 GitHub 이 'Pending(expected)' 를 영구 보고 → PR merge 영구 차단; F-4). 즉 "CSS 없는 repo 에서 no-op" 을 path-filter 로 하면 안 되니 job-level conditional 로 우회하려 한 것이다. 그러나 그 conditional 의 조건식에 `hashFiles` 를 쓴 것이 context-availability 위반이었다. `hashFiles` 없이 job-level 에서 "CSS 가 있나" 를 알 방법은 없다(디스크 미접근) → 정정 해법은 job-level conditional 자체를 버리고 **in-job fast-exit(step-level)** 로 no-op 을 실현하는 것이다.

ADR-130 §결정4 는 2축이다 — **(i) negative**: path-filter skip 금지(위 permanent-pending 함정). **(ii) positive**: graceful no-op 을 job-level `if:` conditional skip 으로 구현하라는 긍정 명령. (ii)의 긍정 형태는 CSS-존재를 job-level 에서 판정해야 하는데 그 판정에 `hashFiles`(디스크 접근)가 필요하고 job-level context-availability 부적격이라 **실현 불가**한 조건 위에 서 있었다. in-job fast-exit(F-4 경로 C)은 (ii)가 보증하려던 **outcome(required-safe non-blocking Success)을 동형 달성**한다 → §결정4 의 *의도*는 permanent-pending 회피이지 "job-level `if:` 리터럴 강제" 가 아니다. 리터럴 메커니즘 조항만 좁혀지고(job-level conditional skip → in-job fast-exit) load-bearing invariant(path-filter 금지 + permanent-pending 회피)는 보존 → **ADR-130 amend 불요**.

이 결함은 "path-filter 금지(ADR-130)" 라는 정당한 제약과 "job-level 에서 디스크를 볼 수 없다(context-availability)" 라는 플랫폼 사실 사이의 **구조적 긴장**이 낳은 unknown-unknown 이다 — 두 제약을 동시에 만족하는 유일 채널이 in-job fast-exit 임을 놓쳤다.

## 외부 사실 anchor (GitHub 공식 + actions/runner + actionlint — ADR-119 자료조사+인용, 본 lane firsthand WebFetch 실측)

### F-1: job-level `if:` available 집합 = `{github, needs, vars, inputs}` context + `{always, cancelled, success, failure}` function (`hashFiles` 제외)
GitHub "Contexts reference / Context availability" 표: `jobs.<job_id>.if` 에서 available context = `github`, `needs`, `vars`, `inputs`; available special function = `always`, `cancelled`, `success`, `failure`. `hashFiles` 및 `steps`/`runner`/`job`/`matrix`/`strategy`/`env`/`secrets` context 는 **NOT available**. (출처: https://docs.github.com/en/actions/reference/accessing-contextual-information-about-workflow-runs — 본 lane WebFetch 실측 confirm.)

> **대조 증거 (긍정 통제)**: `github` context 는 job-level 에서 available 이므로, css-lint.yml 의 sibling `css-lint-test` job 이 쓰는 `if: github.repository == 'mclayer/plugin-codeforge'` 는 정상 동작한다. 즉 "job-level `if:` 자체가 불가" 가 아니라 "`hashFiles` 가 job-level 부적격" 인 것 — available 집합의 문제임을 이 대조가 보인다.

### F-2: step-level `if:` = F-1 + `{steps, runner, job, matrix, strategy, env}` context + `hashFiles` function 추가 available
`jobs.<job_id>.steps.<step_id>.if` 에서는 F-1 집합에 더해 `steps`, `runner`, `job`, `matrix`, `strategy`, `env` context 와 `hashFiles` function 이 available 하다. (출처: 동일 Context availability 표 — 본 lane WebFetch 실측 confirm.) → 디스크-접근·실행-상태 의존 표현은 step-level 로 내려야 유효.

### F-3: 인과 timing — job-level `if:` = 서버 평가(runner 배정 前), `hashFiles` = runner-side 전용(디스크 read 필요)
> "`hashFiles()` will only allow on runner side since it needs to read files on disk, using `hashFiles()` on any server side evaluated expression will cause runtime errors." (출처: actions/runner ADR 0279 — https://github.com/actions/runner/blob/main/docs/adrs/0279-hashFiles-expression-function.md — 본 lane WebFetch verbatim 실측 confirm.)

job-level `if:` 는 server-side 평가(runner 배정 전, 디스크 없음) → 디스크 read 필요한 `hashFiles` 는 여기서 쓸 수 없다. 이것이 F-1 의 available 집합에서 `hashFiles` 가 빠진 근본 이유다.

### F-4: required-check skip 3-경로 명확 구분 (혼용 금지)
동일 non-blocking 'Success' 처럼 보여도 인과가 다른 세 경로가 있다:
- **(경로 A) trigger `on: paths:`/`branches:` filter skip → 'Pending(expected)' 영구 → required merge 차단.** "checks associated with that workflow will remain in a 'Pending' state. A pull request that requires those checks to be successful will be blocked from merging." (함정 — ADR-130 §결정4 가 금지하는 대상.)
- **(경로 B) job-level `if:` conditional skip → 'Success'(skip 메커니즘, job 이 아예 안 돎).** "If, however, a job within a workflow is skipped due to a conditional, it will report its status as 'Success'."
- **(경로 C) step 이 실행돼 `exit 0` → 'Success'(genuine pass 메커니즘, job 은 돌되 검사 대상 0 이라 통과).**

(출처: https://docs.github.com/.../troubleshooting-required-status-checks §Handling skipped but required checks — 본 lane WebFetch 실측 confirm; 경로 A/B 는 인용, 경로 C 는 일반 CI 동작.)

> **⚠ 혼용 금지 (CFP-2530 요구사항리뷰 dual-peer)**: 경로 B(skip)와 경로 C(exit 0)는 둘 다 required-safe 이나 **다른 메커니즘**이다. ADR-136 결정3 이 두 경로를 "또는" 으로 병렬 나열했으나(혼용 소지), context-availability 를 위반하지 않고 job-level graceful-skip(경로 B)을 실현할 방법이 없다(CSS 존재 판정에 디스크 필요 → hashFiles → 부적격). 따라서 **경로 C(in-job fast-exit = genuine pass)가 유일 실현 채널**이다.

### F-5: actionlint `ctx-spfunc-availability` check 가 검출
actionlint(rhysd/actionlint) v1.7.12 의 "Availability of contexts and special functions" check(anchor `ctx-spfunc-availability`)가 job-level `if:` 의 `hashFiles` 를 검출한다. 실측 에러 문구 2종(actionlint 버전·message 경로별 상이):
- `function 'hashfiles' is not available in this context` — 설계 lane WebFetch(checks.md) 실측.
- `calling function "hashFiles" is not allowed here` — 요구사항리뷰 lane Codex 정확-태그 실행 ground-truth.

(출처: https://github.com/rhysd/actionlint/blob/v1.7.12/docs/checks.md#ctx-spfunc-availability — 본 lane WebFetch 실측 confirm.)

> **회귀 test 판정 규칙 (F6 — false-GREEN 차단)**: **primary 판정 = actionlint `exit != 0`**(mutation-kill). **secondary = stderr regex** `not allowed here|not available in .*context|ctx-spfunc`(위 2 실측 문구 + anchor 포함, tolerant — 진단 라벨 전용). regex 를 primary 로 두면 문구 drift 시 mutation 이 살아있는데 regex 미매칭으로 GREEN 오판(false-GREEN)하는 리스크가 있으므로, regex 미매칭이어도 exit != 0 이면 RED 성립으로 확정한다.

## 핵심 규칙

### R1: 디스크-접근·실행-상태 의존 함수/context 는 step-level 전용 — job-level 조건식에 쓰지 말 것
`hashFiles`(디스크 read) 및 `steps`/`runner`/`job`/`env` 등 실행-상태 의존 context 는 job 이 runner 에 배정된 뒤에야 값이 존재한다. 이를 `jobs.<job_id>.if` 에 쓰면 load-time schema-invalid → 게이트가 로드조차 안 됨(born-invalid). available 표(F-1/F-2)를 workflow key 기준으로 조회한 뒤 표현을 배치한다.

### R2: CSS-0 / config-0 graceful skip 은 step-level 가드 또는 in-job early-exit(exit 0)로만 — job-level hashFiles·trigger paths-filter 둘 다 금지
"자산 없는 repo 에서 no-op" 을 실현하는 두 함정: (a) job-level `if: hashFiles(...)`(load-time invalid — 본 결함), (b) `on: paths:` trigger filter(required permanent-pending — F-4 경로 A / ADR-130 §결정4). 유효 채널은 **step-level `if:` 가드**(예: `if: steps.resolve_config.outputs.config_found == 'true'`) + **in-job fast-exit**(스캔 대상 0 개 → `::notice::` 후 `exit 0`, F-4 경로 C)뿐이다.

### R3: job 항상 등록 + in-job fast-exit = conditional job-skip 과 동형 required-safe
job-level `if:` 를 제거하면 job 은 항상 등록되나, 검사 대상이 0 인 repo 에선 후속 step 이 step-level 가드로 skip 되거나 early-exit 로 exit 0 → job **Success**(genuine pass, F-4 경로 C). 결과(required 승격 후에도 merge 비차단)는 conditional job-skip(경로 B)과 동형이고, unique job name(ADR-130 §결정6)도 무변경이다.

### R4: 재유입 봉인 = 검출(actionlint `.github/` lint) ∪ 차단(discriminating test) — byte-identical parity 제약 존중, 두 채널 분리
job-level `hashFiles` 류 재유입 봉인은 **강제력이 다른 두 채널의 합집합**이다 — lint 검출 단독은 "봉인" 이 아니라 "검출" 이다(F2). 그리고 검출 채널의 lint 대상 glob 은 **byte-identical parity 제약 때문에 blanket templates/ 확장을 하면 안 된다**(F8):

- **parity 제약 (F8)**: `actionlint-check.yml` 같은 governance workflow 는 wrapper 의 `.github/workflows/` copy 와 `templates/github-workflows/` copy 가 **byte-identical parity 로 강제**되는 경우가 많다(invariant-check.yml Workflow parity step, `CONSUMER_ONLY_WORKFLOWS[]` exclusion 목록에 없으면 강제). 이 parity 파일에 blanket `templates/github-workflows/*.yml` glob 을 박으면 — **consumer repo(배포된 template copy)에는 `templates/github-workflows/` 디렉터리가 없어** unmatched glob 이 literal 로 lint 도구에 넘어가 "file not found" → warning-tier 라 비차단이나 **매 consumer PR 마다 spurious warning**. 즉 "양 copy 를 lint 하려고 파일에 양 경로 glob 을 박는" naive 확장은 parity-enforced 파일에 부적합.
- **검출 채널 = actionlint-check.yml `.github/workflows/*.yml` lint (parity 파일 무접촉)**: 각 repo(consumer·wrapper)의 실 workflow 는 항상 `.github/workflows/` 에 있으므로 이 경로만 lint 하면 consumer·wrapper 공통 정확 + byte-identical parity 무손상 + consumer spurious warning 0. warning-tier(비차단)라 검출 O·차단 X.
- **차단 채널 = wrapper-self discriminating test** (`.github/workflows/` + `templates/github-workflows/` 양쪽 actionlint hard-fail, exit != 0): wrapper-self only(`github.repository` gate/test 하네스, consumer 미배포)라 templates/ 부재 문제 무관 → **templates/ copy coverage 를 이 test 가 검출+차단 겸 담당**. templates/ 는 본디 wrapper-self 관심사이므로 wrapper-self 채널에 집중하는 것이 관심사 정합. **primary 판정 = exit != 0**(정상 exit 0 ↔ mutation 재삽입 exit != 0, mutation 생존 0), regex 는 진단 secondary(F-5). anti-theater([[mutation-based-hollow-gate-detection]]).

즉 "재유입 봉인 = actionlint-check.yml `.github/` 검출(parity 무접촉) ∪ discriminating test templates/+.github/ 차단(wrapper-self)". parity-enforced consumer 파일에 blanket templates/ glob 을 박지 않는다. (대안 = actionlint-check.yml 에 dir-존재 조건부 glob 삽입으로 parity 유지하며 wrapper 양쪽 lint — 유효하나 parity 파일에 wrapper-self 분기 삽입 = 관심사 오염이라 비채택.)

## 경계

- **In scope**: workflow key 별 expression context/function 가용성 위반으로 인한 load-time schema-invalid(born-invalid gate) 결함 class + job-level ↔ step-level `if:` 가용성 차이 의미론 + graceful-skip 정합 해법(step-level 가드 + in-job fast-exit) + required-check skip 3-경로 구분 + GitHub Actions 서버-평가 vs runner-평가 timing.
- **Out of scope**:
  - stylelint config-resolution 실패([[config-extends-resolution-basedir]], CFP-2527 sibling) — 다른 층위(runtime config-resolution 실패 = 로드는 됨 / 본건 = load-time schema-invalid = 로드 자체 실패). 둘 다 D1 게이트가 실효 0 이나 mechanism 상이.
  - config-standard cosmetic rule noise 정책(CFP-2527 층위2 follow-up, floor-rule vs cosmetic-rule 분리) — 검증은 되나 signal 오염 층위.
  - actionlint warning→blocking-on-pr 승격(ADR-060 별도 promotion path) — 본 결함 봉인은 검출(actionlint-check.yml `.github/` lint) ∪ 차단(wrapper-self test)이지 tier 승격이 아님.
  - 비-GitHub-Actions CI(GitLab/CircleCI 등)의 동형 expression-context 결함 일반화 — 개념은 CI-비의존이나 가용성 명세는 플랫폼별 상이(각 플랫폼 context 표 확인 전제).
- **Anti-pattern**: job-level `if:` 에 `hashFiles`/`steps`/`runner`/`env` 등 부적격 표현 사용(load-time invalid — 본 결함). "자산 없으면 no-op" 을 `on: paths:` trigger filter 로 구현(required permanent-pending — F-4 경로 A). warning-tier(`continue-on-error: true`)라 "merge 안 막히니 괜찮다" 로 born-invalid 방치(continue-on-error 는 job *안* step 실패만 삼킬 뿐 workflow load 실패엔 무개입 — load 실패는 job 이 없어 개입 지점 자체가 부재). **parity-enforced workflow 파일(byte-identical 강제)에 blanket `templates/github-workflows/*.yml` glob 을 박음 → consumer 에 templates/ 디렉터리 부재라 unmatched glob → 매 consumer PR spurious warning**(F8 — templates/ coverage 는 wrapper-self test 로 분리해야 함, R4). 반대로 재유입 lint 채널을 아예 두지 않아 검출·차단 0 으로 방치(R4).

## 관련 ADR

- **ADR-136** 결정3(job-level graceful no-op) — 본 결함의 예시 errata 지점. 결정13(Amendment 2, CFP-2530) = 정정 anchor(job-level `if:` 삭제 → step-level 가드 + in-job fast-exit + templates/ 재유입 봉인: actionlint-check.yml byte-identical parity 무접촉·`.github/` 검출 유지 + wrapper-self test 가 templates/ 차단, F8 (B) 채택).
- **ADR-130** §결정4 — path-filter 금지 invariant(required permanent-pending 함정). 본 결함의 배경(왜 path-filter 대신 job-level `if:` 를 썼나) + 정정 후에도 path-filter 금지 유지(F-4 경로 A).
- **ADR-119** — research-before-claims. F-1~F-5 외부 사실 자료조사+출처인용 의무 anchor. 본 concept 의 5 anchor 전부 본 lane firsthand WebFetch 실측 confirm.

## 변경 이력

- 2026-07-01 KST — 초기 작성 (CFP-2530 설계 lane 산출물). **born-invalid gate — ADR-136 D1 css-lint.yml 양 copy 가 css-lint.yml 신설(PR #2511, CFP-2505 Phase 2, commit 7a9b0347) 이래 job-level `if: hashFiles(...)` 로 인해 단 한 번도 로드/실행된 적 없음**을 본 lane firsthand 판정(css-lint.yml 신설 PR = `git log --diff-filter=A` firsthand 실측 → #2511; #2529 = CFP-2527 Phase 2 config-basedir fix 로 별개 + 양 copy line 59 job-level `if: hashFiles(...)` byte-identical Read 실측 + actionlint ctx-spfunc-availability check 문구 대조). 외부 사실 5 anchor(F-1 context-availability 표 / F-2 step-level 추가 집합 / F-3 actions/runner ADR 0279 verbatim / F-4 required-check skip 3-경로 / F-5 actionlint ctx-spfunc-availability) 전부 본 lane WebFetch firsthand 실측 confirm — drift 0. 기존 concept/ 자산에 GitHub Actions expression 가용성 주제 선행 부재(config-extends-resolution-basedir = runtime resolution 층위 sibling, mutation-based-hollow-gate-detection = hollow-gate 일반) → 신규.
