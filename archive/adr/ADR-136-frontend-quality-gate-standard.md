---
adr_number: 136
title: "frontend 품질게이트 표준 — D1 구조적 CSS lint(stylelint) CI 게이트 + D2 UI 실렌더 검증(§8.7) + frontend.applicable CONDITIONAL flag (escalation #2502 / Story CFP-2505)"
status: Proposed
category: governance
date: 2026-06-30
carrier_story: CFP-2505
parent_epic: null
supersedes: null
amends: null
amendments:
  - amendment: 1
    date: 2026-07-01  # KST +09:00
    cfp: CFP-2527
    summary: "결정12 — 격리 toolchain extends resolution base 명시(STYLELINT_BASEDIR + --config-basedir) 동반 의무"
  - amendment: 2
    date: 2026-07-01  # KST +09:00
    cfp: CFP-2530
    summary: "결정13 — 결정3 예시 errata: job-level if: hashFiles(...) 는 context-availability 위반(load-time schema-invalid → 게이트 born-invalid, 신설 이래 0 회 로드/실행) → 삭제. graceful no-op 을 step-level 가드 + in-job fast-exit(exit 0) 단일 채널로 일원화 + templates/ 재유입 봉인(F8: actionlint-check.yml byte-identical parity 파일 무접촉·.github/ 검출 유지, templates/ coverage 는 wrapper-self discriminating test 가 hard-fail 차단)"
related_adrs:
  - ADR-130  # applicability ⊥ closure + §결정4 graceful no-op job-level if: (path-filter skip 금지) + §결정6 required 등록 7일+unique job name + §결정1 positive whitelist — D1 직접 상위 토대
  - ADR-127  # overlay 확장-only/축소불가 invariant(§결정6 = 면제-카테고리 채널 폐지로 그 불변식 강화·재확인) — stylelint floor 영역 동형 적용(직접 근거 아닌 동형 선례/invariant 출처) + §결정5 N/A 3축 AND — D1 floor 축소불가 / D2 §8.7 N/A 근거
  - ADR-006  # §8 Test Contract author = ArchitectAgent(chief), deputy = input contributor — D2 §8.7 author 경계
  - ADR-005  # plugin-self N/A 표기(plugin-meta-na) + inheritance 차단 — frontend 없는 consumer §8.7/§11 N/A 선례. 본 Story 자체 §8/§11 면제 근거
  - ADR-015  # §8.5 stateful CONDITIONAL §8.5.0 applicability 표 형식 + lint(check-doc-section-schema.sh) — §8.7.0 동형 청사진
  - ADR-055  # §8.6 Integration CONDITIONAL sub-section — §8.7 이 §8.6 과 disjoint axis 임을 명시
  - ADR-116  # consumer 전파 reconcile-then-patch 멱등 주입 (본체 무수정 + never-reduce + idempotent) — D1 stylelint config 소급 전파 채널
  - ADR-042  # Amd8/10 aggregate_arch.applicable CONDITIONAL applicability flag schema 선례 — frontend.applicable 동형 차용
  - ADR-083  # consumer-applicability-filter (ADR-130 supersede) — conditional-applicability filter 1급 패턴 계보
  - ADR-063  # marketplace atomic sync — 결정12 Phase 2 version+desc mirror 의무
related_files:
  - templates/github-workflows/css-lint.yml
  - plugins/codeforge-develop/presets/webapp/.stylelintrc.json
  - scripts/check-lint.sh
  - templates/scripts/consumer_applicable_workflows.txt
  - templates/consumer-scripts.manifest
  - docs/project-config-schema.md
  - plugins/codeforge-design/templates/change-plan.md
  - templates/story-page-structure.md
  - scripts/bootstrap-consumer.sh
  - docs/consumer-guide.md
mechanical_enforcement_actions: []   # declaration-only — 본 ADR 은 frontend 품질게이트 표준의 정책 SSOT 등재(강화 ratchet). 실 wire(css-lint.yml workflow / stylelint preset / whitelist·manifest 등재 / §8.7 template 본문 / check-doc-section-schema.sh §8.7 lint / project-config-schema frontend block / bootstrap scaffold) = Phase 2 구현 lane. day-1 신규 lint 0 (D1 초기 warning-tier — §결정 5).
is_transitional: false
sunset_justification: "N/A — permanent governance 표준. ADR-058 §결정 5 강화(ratchet) 방향 전용 (frontend 품질게이트 ground-truth 층위 추가 — D1 구조적 lint + D2 render-truth, 검증 강제력 확장). 약화 surface 0 (stylelint config override 가 floor rule 약화 방향이면 ADR-127 위반 / D2 jsdom 으로 render-truth 대체 금지). frontend-bearing consumer 조건부 적용이라 비-frontend consumer 무손상(additive)."
---

# ADR-136: frontend 품질게이트 표준 — D1 구조적 CSS lint + D2 UI 실렌더 검증

## 상태

`Proposed` (2026-06-30 KST). Story CFP-2505 (escalation #2502 — mctrader-web WEB-033 실증 버그 발 wrapper 표준 발의) carrier. doc-only Story 의 설계 SSOT — 별도 change-plan 면제 (ADR-013 / ADR-127 doc-only Story ADR carrier). `is_transitional: false` — 영구 표준. Phase 2 (CFP-2505 구현 PR) 산출물(css-lint.yml + stylelint preset + whitelist/manifest 등재 + §8.7 template 본문 + project-config-schema frontend block + bootstrap scaffold) merge 시 Accepted.

본 ADR 은 어느 기존 ADR 도 supersede/amend 하지 않는다 — 전부 기존 패턴의 **확장(강화 방향)** instance 다 (신규 메커니즘 0, ArchitectAnalyst firsthand 검증). ADR-130 의 applicability⊥closure + graceful-no-op invariant 위에 frontend 품질게이트라는 새 적용 영역을 쌓는다.

## 본질 선언

> **게이트가 보증하는 결함 수준은 그 게이트가 딛고 선 ground-truth 추상 수준이 결정한다 — 텍스트(lint) < DOM 트리(jsdom) < 실 레이아웃 좌표(headless browser). 낮은 층위 게이트는 높은 층위 버그를 구조적으로 못 잡는다. frontend 품질을 닫으려면 게이트를 *추가* 하는 게 아니라 ground-truth *수준* 을 올려야 한다. 본 표준은 두 층위를 각각 메운다 — D1(구조적 CSS lint)은 원인(미닫힌 brace / 오중첩)을 텍스트 층위에서 차단하고, D2(UI 실렌더 검증)는 증상(static 추락 등 레이아웃 깨짐)을 실 Chromium 레이아웃 좌표 층위에서 포착한다. 두 게이트는 직교(서로 의존 0)하며 frontend-bearing consumer 에만 조건부 적용된다.**

## 컨텍스트

### 실증 결함 — WEB-033 (escalation #2502 입력 packet, consumer 측 실측 — 본 lane 미독립검증)

mctrader-web `styles.css` 의 미닫힌 `{` 2개(`.terminal-controls .tt-live` + `@media`)로 그 뒤 전체 CSS(거래내역 모달 포함)가 해당 셀렉터의 자손으로 오중첩됐다(CSS nesting 함정). lightningcss lenient 빌더가 brace 를 보정해 **에러 0 으로 빌드 성공**시켰다. 거래내역 모달은 `createPortal(document.body)` 로 그 오중첩 스코프 밖에 렌더돼 `position:fixed` 가 미적용 → `position:static` 으로 페이지 하단에 인라인 렌더됐다("모달이 아니라 아래로 나열"). 근본원인 확정은 CDP 헤드리스 Chrome 실측으로만 가능했다(수정 전 static rectTop=2676 → 수정 후 fixed rectTop=0).

> **"static 추락" = 조건부 발현** (consumer 측 실측, 요구사항리뷰 F2 보정): `createPortal → position:fixed 미적용 → static` 은 무조건 발현이 아니라 — `position:fixed` 규칙이 React-부모 전용 scope / CSS-module selector 에 의존해 portal 로 DOM 부모가 바뀐 조건에서만 풀리는 **조건부 발현**이었다(규칙이 전역 selector 였다면 portal 후에도 fixed 유지). 결론(D1+D2 양층 차단 필요)은 불변 — render-truth 게이트가 필요한 이유는 이 발현이 조건부라 정적 검출로는 예측 불가하기 때문이다.

### 3중 게이트 동시 통과 — 상관된 맹점

consumer 의 frontend 품질 3중 게이트(① lint ② jsdom 단위테스트 ③ 정적 2-peer 리뷰)가 이 버그를 **전부 통과**시켰다. 셋 다 layout 을 보지 않는 도구라 상관된 맹점을 공유한 것이다:

| 게이트 | 층위 | 못 잡은 본질 |
|---|---|---|
| ① lint | 텍스트(현 wrapper = node eslint+tsc / python ruff+pyright, **CSS 파서 0**) | CSS 파싱 도구 부재 → 미닫힌 `{` 볼 눈 없음. 검출실패 아닌 검출기 부재. |
| ② jsdom 단위테스트 | DOM 트리 | 모달 DOM 존재 확인(PASS) but position/실좌표/가시성 = 레이아웃 엔진 부재로 계산 자체 안 함 [§외부사실 검증: jsdom README "Unimplemented parts: Layout"]. static 추락 관측 밖. |
| ③ 정적 2-peer 리뷰 | 사람의 빌드/코드 신호 | lenient 빌드가 에러 0 성공 → 리뷰어 도달 위험신호 0. |

### 외부사실 검증 상태 (요구사항리뷰 lane PASS — 13/14 confirmed, refuted 0)

본 표준의 도구 결정은 요구사항리뷰 lane(ADR-125)에서 dual-peer + PL firsthand 출처 대조로 검증된 외부사실에 의존한다(상세 = Story §6 14건 체크리스트):
- 미닫힌 brace = stylelint CSS parser syntax error(CssSyntaxError) — rule 평가 이전 단계, rule 무관. CLI exit code 2(lint problem)→non-zero→CI 차단. [source: stylelint.io/user-guide/errors/ , /usage/cli/]
- jsdom 공식 README "Unimplemented parts: Layout" — getBoundingClientRect/offsetTop 등 layout 속성 다수 0 반환. [source: github.com/jsdom/jsdom README + issue #653]
- Playwright `toHaveScreenshot()`(pixelmatch baseline) + `toHaveCSS`/`boundingBox()`(computed-style 결정적). GHA ubuntu `npx playwright install --with-deps chromium` headless 동작. [source: playwright.dev/docs/test-snapshots , /ci]
- GitHub required check 가 path/branch-filter skip 시 'Pending(expected)' 영구 → PR merge 영구 block. job-level conditional skip 은 'Success' 보고. [source: docs.github.com troubleshooting-required-status-checks — ADR-130 §결정4 가 인용하는 동일 동작]
- stylelint config `rules:{X:null}` 로 floor rule 기술적 disable 가능 → config 차원만으론 축소불가 보장 불가. [source: stylelint.io/user-guide/configure/]

## 결정

### 결정 1 — 두 게이트 정체: D1(구조적 CSS lint) + D2(UI 실렌더), 직교·상보

| | D1 구조적 CSS lint | D2 UI 실렌더 검증 |
|---|---|---|
| 닫는 층위 | 구조적(syntactic) 정적 검출 | 의미적(semantic) 동적 검증 |
| ground-truth | CSS 소스 구문 트리 | 실 Chromium 레이아웃 좌표/스타일 |
| 메우는 사각 | ① 원인(미닫힌 brace) 발생지점 차단 | ②③ 증상(static 추락) 발현지점 포착 |
| 강제 메커니즘 | **CI lint 게이트** (required 승격 경로) | **§8 Test Contract 정책** (§8.7 신규 sub-section, 설계리뷰 P0 강제) |
| 도구 | stylelint + stylelint-config-standard | Playwright(computed-style 단언 primary + screenshot optional) |

- **두 게이트 직교**: D1 실패가 D2 를 단락(short-circuit)시키지 않도록 `needs:` 결합 금지 — 독립 job/workflow (RefactorAgent decoupling advocacy). WEB-033 = 구조결함이 의미결함으로 발현해 둘 다 잡을 수 있는 케이스이나, 일반적으로 D1 단독(brace 멀쩡한 z-index/specificity 결함 못 잡음)·D2 단독(작성된 케이스만 봄) 모두 불충분 → 상보.
- **mandatory↔whitelist 동치 비대칭** (default #9): D1 = CI lint 게이트(consumer required 승격 경로) / D2 = §8 Test Contract 정책(설계리뷰 §8.7 완결성 P0 강제, §8.5 동형). 두 게이트의 강제 채널이 다르다 — 정합 보존.

### 결정 2 — frontend.applicable CONDITIONAL flag (default #1, ADR-042 Amd8/10 동형)

frontend-bearing 판정의 authoritative source = `project.yaml frontend.applicable: bool` flag 신설 (`docs/project-config-schema.md` 신규 `frontend` 섹션):

- **schema** (선례 `aggregate_arch.applicable` 동형 — 선택필드 + 안전 default + additive-only + 미주입 비차단):
  - `frontend.applicable` (선택, bool, **default `false`** — 안전 방향): `true` = D1 CI 게이트 + D2 §8.7 활성. `false` 또는 미주입 = frontend 무관 → 게이트 PASS(비차단), §8.7 N/A.
  - 미주입 시 default `false` → 비-frontend consumer(backend/lib/CLI-only) 무손상.
- **2-layer 분리** (RefactorAgent interface separation): `frontend.applicable` = **authoritative gate**(D1/D2 공용 활성 여부) / whitelist(`consumer_applicable_workflows.txt`) membership = **eligibility**(css-lint.yml 이 consumer 에 배포될 자격). 두 layer 충돌 시 우선순위 = flag authoritative (ADR-130 §결정1 positive whitelist 와 정합 — whitelist 등재가 배포 자격, flag 가 런타임 활성).
- `aggregate_arch.applicable`(default true) 와 default 방향이 반대인 이유: aggregate 는 "RDB 가 있다" 가 보편 default 이나, frontend 는 wrapper 의 대다수 consumer(backend/lib)에 부재 — false 가 안전·보편 default.

### 결정 3 — D1 graceful no-op = job-level `if:` (path-filter 금지) [ADR-130 §결정4 정합 — 긴장① 해소]

stylelint 은 CSS 변경 시에만 의미가 있어 흔히 workflow-level `on: paths:` path-filter 를 쓰지만, **ADR-130 §결정4 가 path/branch-filter skip 을 금지**한다(required check 가 path-filter skip 시 GitHub 'Pending(expected)' 영구 → PR merge 영구 block). 따라서:

- **D1 graceful no-op = 반드시 job-level conditional**. 권장 형태:
  - `if: hashFiles('**/*.css', '**/*.scss', '**/*.html') != ''` 같은 **job-level 조건** (path-filter 아님 — workflow 는 항상 trigger 되되 job 이 conditional skip → 'Success' 보고).
  - 또는 in-job EXIT 0 (config/CSS 파일 부재 감지 → `::notice::` 후 exit 0). 선례 = `responsibility-topology-check.yml`(data-absence fail-open exit 0) + `test.yml`(doc-only fast-path).
- **이중 보호 권장** (InfraOperationalArch): job-level `if:` (skip 시 Success) + in-job fast-exit (실행되더라도 scan target 0 → graceful exit 0). 둘 중 하나라도 path-filter 로 구현 금지.
- **`on: paths:` 절대 금지** 를 css-lint.yml 헤더 주석에 명문화 (silent override 차단).

### 결정 4 — D1 floor 집합 = parser-level invariant ∪ rule-level floor, 축소불가는 CI 게이트 강제 (default #3·#4, ADR-127 overlay 확장-only/축소불가 invariant 동형 적용 — 긴장 보완)

D1 floor 는 2-part AND (Story §5 AC-D1-1 / §6 reshape #1·#3):

- **(A) parser-level invariant** [default #4-A]: 미닫힌 brace = stylelint CssSyntaxError(rule 평가 *이전* 단계, rule 무관) → **stylelint non-zero exit = CI fail** 이 게이트. 이것이 WEB-033 류 brace 결함의 1급 방어 — rule 목록으로 정의할 수 없는 invariant. [source: stylelint.io/user-guide/errors/]
- **(B) rule-level floor** [default #4-B]: block-no-empty + 잘못된 중첩 검출 rule 등 floor rule 이 effective-config 에서 active. non-overridable.
- **floor 축소불가 강제 위치 = CI 게이트 차원** [default #3, ADR-127 overlay 확장-only/축소불가 invariant 동형 적용]: consumer 가 overlay 에서 `rules:{X:null}` 로 floor rule 을 기술적 disable 할 수 있으므로(config 차원 약화 가능 — 공식 검증), 축소불가는 **config 파일만으론 보장 불가**. CI 게이트에서 `stylelint --print-config <file>` 로 floor rule 이 effective-config 에 active 한지 실측해 강제한다(floor null override 시 lint job 실패 — anti-hollow self-check). ADR-127 의 "overlay 는 정책 확장만 가능·축소 불가" 일반 invariant(§결정6 이 consumer overlay 면제 확장채널 `story_cutoff.additional_exempt_categories[]` 폐지로 강화·재확인한 그 불변식 — 면제채널 폐지 결정이지 stylelint 직접 근거 아님)를 stylelint floor 영역에 **동형 적용**한 것이며, 그 invariant 가 stylelint 영역에서 실효를 가지려면 이 effective-config 검증이 mechanism 이다.
- **hollow-gate 차단** [AC-D1-4]: 게이트가 파일을 실제 스캔(glob 커버리지)하는지 검증 — 0개 매칭이 "검사 없이 PASS"로 새지 않도록.
- **커버리지 계층화** [§6 항목2]: 순수 .css/.scss = config-standard(+postcss-scss) floor 직접 커버(WEB-033 styles.css = 순수 CSS → 1차 floor 커버). styled-components/CSS-in-JS = `postcss-styled-syntax` customSyntax 필수(빠지면 silent skip) → overlay 확장 슬롯.

### 결정 5 — D1 required 등록 = 초기 warning-tier → 7일+unique job name 후 승격 (default #2, ADR-130 §결정6 정합)

- **초기 = warning-tier** (`continue-on-error: true`) — day-1 required 금지. 선례 = `responsibility-topology-check.yml` warning-first(ADR-060 §결정5). branch protection 6-tuple 무변경.
- **required 승격 전제** (ADR-130 §결정6): repo 7일 green + **unique job name**(동명 중복 시 ambiguous required — anti-ambiguous). 승격은 본 Story 가 아닌 **별도 follow-up Story** carrier (wave rollout).
- **whitelist 등재 의무** (ADR-130 §결정1, ADR-083 carry): css-lint.yml 은 `consumer_applicable_workflows.txt` positive whitelist 에 basename 등재 — blacklist 금지(silent 유입 차단).
- **closure 등재** (ADR-130 §결정3): css-lint.yml 이 config/package.json 부재 시 EXIT1 hard-block 의존이면 `consumer-scripts.manifest` 직접 등재 의무. config 부재 시 default(config-standard) graceful exit 0 이면 등재 불요. **본 표준은 graceful(부재 시 exit 0) 채택** → manifest 등재 불요(단 Phase 2 가 실 hard-block 여부 확정).

### 결정 6 — D1 실행 채널 = 신규 독립 css-lint.yml (머지 차단 강제력) + check-lint.sh CSS 분기(보조) [ModuleArch authority]

ModuleArch boundary authority 판정:
- **신규 독립 `templates/github-workflows/css-lint.yml`** = D1 "머지 전 차단" mandate 의 1급 satisfier (CI required-check 경로 — 머지 차단 강제력). `duplication-check.yml` 의 `setup-node@v4` + warning-tier `continue-on-error` 패턴 재사용. path-filter 0.
- **`scripts/check-lint.sh` CSS 분기 추가** = 보조 채널(consumer pre-push/manual lint runner — fix 친화). 언어 분기를 `run_python_lint()` / `run_node_lint()` / `run_css_lint()` 함수로 추출(rule-of-three 정확 도달 — RefactorAgent reusability advocacy). 외부 exit-code/--fix/--quiet 계약 유지 → 호출자 영향 0.
- 두 채널 분담: css-lint.yml = 강제력(차단), check-lint.sh = 개발자 친화(early feedback). 직교.

### 결정 7 — stylelint config preset 위치 = webapp preset 하위 [ModuleArch authority]

- **`plugins/codeforge-develop/presets/webapp/.stylelintrc.json`** (stylelint-config-standard extends) — frontend-bearing ≈ webapp shape 동치이므로 frontend preset 에 동봉(별도 stylelint preset 디렉토리 신설 회피). wrapper root `presets/` = 빈 디렉토리(미사용 — 실 preset 은 plugins/codeforge-develop/presets/ 하위).
- **config SSOT 배포 채널** = bootstrap-consumer.sh Stage5 가 whitelist 등재 workflow 자동 copy + webapp preset scaffold(frontend=Y 시). 소급 = ADR-116 reconcile-then-patch.

### 결정 8 — D1 stylelint config 주입 채널 = ADR-116 reconcile-then-patch 틀 안 신규 결정 (긴장② 해소, ADR-116 §결정2 정합)

ADR-116 은 env value 주입(예: ALLOWED_HUB_REPOS) 선례이나 `.stylelintrc.json` **파일 자체** 주입/override 는 미명시였다(ArchitectAnalyst 긴장②). 본 ADR 신규 결정:

- stylelint config 의 consumer 소급 전파 = **reconcile-then-patch(ADR-116 §결정1) 틀 안에서 config 파일 주입** — 신규 consumer 는 bootstrap scaffold, 기존 consumer 는 reconcile-overlay(ADR-116). **consumer 측 config 본체 무수정**(ADR-116 §결정2 정합 — reconcile 가 override 가 아니라 floor 보장만) + never-reduce + idempotent + monotonic.
- consumer overlay 가 floor rule 을 약화하는 방향이면 결정4 의 CI effective-config 검증이 차단(config 주입과 floor 강제가 분리된 layer).
- 기존 open PR 소급 required 금지 — wave rollout (default #8).

### 결정 9 — D2 강제 granularity = risk-gate (§8.5 CONDITIONAL 동형) + UI/CSS 변경 트리거 정의 (default #5·#6)

- **risk-gate** [default #5]: UI/CSS 변경을 동반하는 PR 만 §8.7 본문 required, 아니면 N/A. 매 PR 강제 아님(비용 급증 회피). §8.5 Stateful CONDITIONAL 동형.
- **"UI/CSS 변경" 트리거 정의** [default #6, §8.7.0 applicability 표에 명문화]: CSS/SCSS 파일 + 컴포넌트(JSX/TSX/Vue/템플릿) + 스타일 토큰 중 1+ 변경. 확장자만으로 정의하면 JSX className·테마·토큰 누락 위험(엣지12) → 컴포넌트/토큰 포함.
- frontend 판단 = 정적 applicability(repo 단위 frontend.applicable) ⊥ 동적 this-PR-needs-execution(PR diff 가 UI/CSS 트리거 매칭) 2-layer 분리(엣지20).

### 결정 10 — D2 = §8.7 신규 CONDITIONAL sub-section, author = ArchitectAgent chief (긴장③ 해소, ADR-006 §결정2 / ADR-015 / ADR-055 정합)

`plugins/codeforge-design/templates/change-plan.md` §8 에 **§8.7 UI 실렌더 검증 (CONDITIONAL)** 신규 sub-section 추가(현 §8 = §8.1~§8.5.4, story-page-structure §8.6 Integration 존재 → §8.7 이 다음 자유 번호). 형식 = §8.5 Stateful 동형 (TestContractArchitectAgent input 설계):

> **§8.6 의도적 gap 근거 (Phase 2 renumber 금지)**: change-plan.md §8 본문은 §8.1~§8.5.4 까지만 존재한다 — **§8.6 부재**(§8.6 Integration 은 story-page-structure.md 에만 존재, change-plan.md 미수록). 따라서 change-plan.md 에 §8.7 삽입 시 §8.5.4 → §8.7 로 **§8.6 을 의도적으로 건너뛴 번호 gap** 이 발생한다. 이는 story-page-structure §8.6 Integration 과의 cross-template 번호 정합(두 template 이 같은 §8.6/§8.7 의미 좌표를 공유)을 위한 **의도적 gap** 이다 — Phase 2 가 change-plan.md §8.7 을 §8.6 으로 renumber 하지 말 것 + check-doc-section-schema.sh(§8.7 lint)가 change-plan.md §8.6 부재를 schema 오류로 오탐(false-positive)하지 않도록 gap 을 schema 에 허용 표기한다.

- **§8.7.0 Applicability decision (필수)** — §8.5.0 동형 Y/N 표(default #6 "UI/CSS 변경" 트리거 기준) + substantive reason(30자 minimum — ADR-015 §결정5 lint 정합). 1+ Y → §8.7.1+ 본문 필수 / 모두 N + reason → §8.7.x N/A.
- **§8.7.1 render-truth 도구 독립성** [AC-D2-1, §6 reshape #2]: UI/CSS 변경 → 실 layout 엔진(Playwright 권장)으로 outcome 검증. **jsdom 계열(testing-library+jsdom) = D2 부적격**(layout 미계산 — 공식 검증) 명시. lint·jsdom 과 도구 독립인 직교 게이트.
- **§8.7.2 min bar** [default #7]: 변경 UI 에 **≥1 computed-style 단언(`toHaveCSS`/`boundingBox()`, 결정적) primary** + screenshot 회귀(`toHaveScreenshot`) optional. jsdom-통과 ≠ 승인(jsdom 통과·실렌더 실패 → D2 실패). **layout-result 속성 포함 권장**: WEB-033 류 회귀(position:static→fixed 추락)를 구조적으로 보장하려면 computed-style 단언이 **layout 결과 속성(`position` / 좌표 `boundingBox` / `visibility`)을 포함**해야 한다 — 색상·폰트만 단언하면 layout 회귀를 못 잡는다. (강제 floor 수준 명시는 과잉 회피 — "layout-result 속성 포함" 권장에 둠.)
- **§8.7.3 도구/baseline** [AC-D2-7]: Playwright 권장(raw CDP 동등 저수준이나 세션/대기/diff 직접 구현 고비용 → 권장 안 함). screenshot baseline = Linux(CI) 생성으로 OS-drift 회피 + threshold 명시.
- **§8.7.x N/A 명시** (frontend 무관 / UI·CSS 변경 0): ADR-005 표기 답습 — `N/A — <사유>. 검증 채널: <대체>. 면제 분류: plugin-meta-na | runtime-inert`. ADR-127 §결정5 N/A 3축 AND(산출물 부재 + downstream 무변경 + 미래 의무 무선결) + inheritance 차단(per-Story 재실시).
- **author 경계** [ADR-006 §결정2]: §8.7 본문 author = ArchitectAgent(chief), TestContractArchitectAgent = input contributor(§7 SecurityArch 동형). §8.7 신설 = **TestContractArchitectAgent mandate 확장**(§8 커버리지 축에 render-truth 추가) — 신규 SubAgent 미도입(ADR-015 §결정2 정합). §8.6 Integration 과 disjoint axis(ADR-055 §결정4 — §8.6 = service 간 통합 / §8.7 = UI render-truth).
- **anti-hollow + anti-permanent-pending 양쪽** [AC-D2-6, §6 reshape #4]: D2 가 required wire 시 — (anti-hollow) 실행해 PASS/FAIL outcome 보고(mutation 생존 시 FAIL), (anti-permanent-pending) CI job context 이름을 consumer branch protection required contexts 에 정확 매핑(skip 시 명시 Success). consumer branch protection 에 context 추가 = D2 wiring 일부(consumer-guide 경고).

### 결정 11 — CI 운영·보안 표준 (InfraOperationalArch + SecurityArch input)

- **Node toolchain CI-only 격리** [InfraOperationalArch §7.4.5]: stylelint(Node) + Playwright(Node+Chromium)은 `actions/setup-node` + npx self-contained — consumer host stack(Python/Go/Rust) production runtime 에 Node 강요 0(CI-only 의존 격리).
- **supply-chain 비협상 기준선** [SecurityArch M1 — P0 dissent 반영]: `npx <pkg>@latest` 즉석 설치는 fresh malicious 버전 실행 위험(npm worm/공격 벡터 실재 — [source 확인 권장]). **stylelint / stylelint-config-standard / playwright 버전 pin + lockfile(package-lock.json) + `npm ci`** 를 wrapper preset 비협상 기준선으로 박는다(`@latest` 금지). AC-SEC-1 = D1/D2 workflow `permissions: contents: read` 최소 / AC-SEC-2 = secret 불요(접근 0) / AC-SEC-3 = version pin.
- **browser-in-CI 표면 최소** [SecurityArch M4]: Chromium headless 가 외부 URL navigate 없이 로컬 빌드만 렌더 → 추가 신뢰경계 최소(CI 격리 sandbox 안). 외부 navigate 금지.
- **§7.4 운영 리스크 active 항목**: §7.4.4 rate-limit(npm registry / Playwright CDN fetch — 캐시 권장) / §7.4.6 container(`timeout-minutes` 명시, self-hosted runner Chromium 경고). §7.4.1 trust boundary = CI-only Node(consumer runtime 무영향). §7.4.2 disconnect / §7.4.3 clock = `N/A — long-running connection / time-window 의존 0`.
- **§11.6 idempotency** [InfraOperationalArch consult]: D2 screenshot baseline 은 repo commit 으로 deterministic — CI render job 재실행 idempotency 보장(non-deterministic baseline 금지).

### 결정 12 — D1 격리 toolchain resolution base 명시 동반 의무 (Amendment 1, CFP-2527)

> **본 Amendment(CFP-2527, escalation #2502 consumer-side hollow-gate 실증)는 결정 11 의 Node CI-only 격리(`$RUNNER_TEMP/css-lint-toolchain/node_modules`)가 *미완성 wire* 였음을 보정한다. 결정 11 본문 무변경 — 결정 11 의 격리 설계 위에 "격리 채택 = resolution base 명시 비협상 동반" 이라는 강화(ratchet) 결합 조건을 추가한다(충돌 0, 약화 방향 0).**

- **결함(reached-but-dead hollow-gate)**: css-lint.yml 이 toolchain 을 `$RUNNER_TEMP/css-lint-toolchain/node_modules` 에 격리 설치(결정 11)하면서 `STYLELINT_BIN` 만 `GITHUB_ENV` export 하고 **basedir 을 export 하지 않았다**. 후속 두 step(`Floor effective-config self-check` `--print-config`[결정 4-B] + `Run stylelint` 실 lint)이 `--config <repo-root-config>` 만 주고 `--config-basedir` 를 주지 않아, stylelint 이 `extends: stylelint-config-standard` 를 **config-file basedir(=consumer repo root, node_modules 부재) 기준** 으로 resolve 하다 `ConfigurationError: Could not find "stylelint-config-standard"` 로 rule 평가 *이전* 단계에서 죽는다. `continue-on-error: true`(warning-tier, 결정 5)라 merge 는 통과하나 단 한 줄도 lint 못 하는 hollow-gate.
- **원인 메커니즘** = "설치 위치"와 "resolution 탐색 base" 의 분리. 격리 설치는 `node_modules` 를 의도적으로 repo 밖에 두나(host 오염 회피 — 결정 11), stylelint resolver 의 default base 는 config 파일이 사는 곳(또는 cwd)이지 격리 설치처가 아니다. 두 위치가 어긋나면 resolution 실패.
- **결정 (R-1 비협상 결합)**: 격리 install dir 사용 시 stylelint extends/plugins resolution base 명시가 비협상 동반 조건이다. 따라서:
  - (a) Install step 이 `STYLELINT_BASEDIR="$WORK/node_modules"`(= `$RUNNER_TEMP/css-lint-toolchain/node_modules`, `STYLELINT_BIN` export 와 동형 GITHUB_ENV 패턴) 를 `GITHUB_ENV` export.
  - (b) **extends 를 resolve 하는 모든 호출**(`--print-config` floor self-check[결정 4-B] + 실 lint run)에 `--config-basedir "$STYLELINT_BASEDIR"` 명시.
- **NODE_PATH 무효 (R-2)**: `getModulePath` 가 NODE_PATH 를 미참조하므로 NODE_PATH 로 격리처를 알리는 우회는 무효 — `--config-basedir`(CLI) / `configBasedir`(API)만 유효. [source: stylelint `lib/utils/getModulePath.mjs` @tag `17.13.0`]
- **부분 적용 = 잔존 hollow (R-3)**: `--print-config` 와 실 lint 가 동일 `augmentConfigFull()` → `extendConfig()` extends-resolution 경로를 타므로(F-5), basedir 를 한 호출에만 주면 다른 호출에서 ConfigurationError 잔존. 양 호출 동반 의무. [source: stylelint `lib/augmentConfig.mjs` @tag `17.13.0`]
- **출처 (ADR-119)**: stylelint 공식 docs(`stylelint.io/user-guide/options/`, `/cli/`, `/configure/`) + source(`getModulePath.mjs` resolution 순서 basedir→cwd→global / `augmentConfig.mjs` configBasedir fallback=`dirname(config filepath)`) @tag `17.13.0` + issue #1810. concept doc SSOT = [`docs/domain-knowledge/concept/config-extends-resolution-basedir.md`](https://github.com/mclayer/plugin-codeforge/blob/main/docs/domain-knowledge/concept/config-extends-resolution-basedir.md) F-1~F-6. 요구사항리뷰 lane dual-peer(Claude tag source 대조 + Codex exit-code ground-truth) drift 0 confirm(CFP-2527 §9.1).
- **ratchet 방향**: 결정 4(floor self-check)·결정 11(격리)의 *실효를 복구* 하는 강화 — 격리는 유지하되 그 격리가 검증 0 으로 죽지 않게 resolution base 를 명시. floor rule 집합·tier·격리 설계 변경 0. carrier = css-lint.yml 양 copy(`.github` + `templates`, byte-identical parity — invariant-check.yml Workflow parity step, CFP-65/67/68 consumer-only exclusion lineage) fix(Phase 2 구현 lane) + discriminating C5 fixture(`tests/scripts/test-css-lint.sh`, self-CI css-lint job 영구 skip 이라 단일 회귀 채널).

### 결정 13 — D1 job-level graceful-skip 채널 정정: `if: hashFiles(...)` = context-availability 위반 (Amendment 2, CFP-2530)

> **본 Amendment(CFP-2530)는 결정 3 이 job-level graceful no-op 의 "권장 형태" 로 명문화한 예시(`if: hashFiles(...) != ''`)가 GitHub Actions **context-availability 위반**임을 정정한다(결정3 예시 errata). 이 예시는 문서적 뿌리로, css-lint.yml 양 copy 에 그대로 이식돼 workflow 를 **load-time schema-invalid** 로 만들었다 — ADR-136 D1 게이트는 css-lint.yml 신설(PR #2511, CFP-2505 Phase 2, commit 7a9b0347 — job-level `if: hashFiles` line 이 여기서 유래, 본 lane `git log --diff-filter=A` firsthand 실측) 이래 단 한 번도 로드/실행된 적이 없다(born-invalid, hollow 을 넘어 non-existent). 결정 3 의 정책 의도(path-filter 금지 + graceful no-op)는 **불변** — no-op 을 실현하는 *메커니즘* 만 job-level `hashFiles` → step-level 가드 + in-job fast-exit 으로 정정한다(충돌 0, 약화 방향 0, 실효 복구 방향).**

- **결함 (born-invalid gate)**: 결정 3(본문 line ~112) 이 job-level `if: hashFiles('**/*.css', '**/*.scss', '**/*.html') != ''` 를 job-level conditional graceful no-op 의 "권장 형태" 로 명문화했다. 그러나 `hashFiles` 는 `jobs.<job_id>.if` context 에서 **available 함수가 아니다** — GitHub 이 workflow 를 로드하는 시점에 schema-invalid 로 reject 한다. 결과: workflow 의 모든 run 이 job 생성 이전에 0 초 fail, css-lint job 자체가 등록되지 않는다. `continue-on-error: true`(warning-tier, 결정 5)는 job *안* 의 step 실패를 삼키는 장치라 **workflow load 실패와 무관** — load 가 안 되면 continue-on-error 가 개입할 지점 자체가 없다. 이것이 결정 12(hollow-gate — 로드는 되나 검증 0)보다 한 층 더 깊은 결함: **게이트가 로드조차 안 되는 non-existent gate**. 결정 12 의 `--config-basedir` fix(CFP-2527)는 본 fix 후에야 비로소 실효한다 — 그 전에는 workflow 가 실행조차 안 됐다.
- **원인 메커니즘 (평가 시점 = context 가용성 결정자)**: GitHub Actions expression 은 평가되는 **workflow key 별로** available context/function 집합이 다르다. `jobs.<job_id>.if` 는 GitHub 서버가 runner 배정 *전* 에 평가한다(어느 job 을 돌릴지 결정하는 단계) → 이 시점엔 아직 runner·디스크가 없다. `hashFiles` 는 디스크의 파일을 읽어 hash 하는 함수 → runner-side(step-level)에서만 가능. 두 사실이 겹쳐 job-level `if:` 의 available function 집합 = `{always(), cancelled(), success(), failure()}` 로 제한되고 `hashFiles` 는 제외된다. (대조 증거: 같은 workflow 의 sibling `css-lint-test` job 이 쓰는 `if: github.repository == 'mclayer/plugin-codeforge'` 는 `github` context 가 job-level 에서 available 이라 정상 동작 — hashFiles 만 죽은 것이 아니라 hashFiles 가 job-level 부적격이기 때문임을 보인다.)
- **결정 (정정)**:
  - **(a)** css-lint.yml 양 copy(`.github/workflows/` + `templates/github-workflows/`, byte-identical parity)의 job-level `if: hashFiles(...) != ''` 라인을 **삭제**한다. job 은 항상 등록된다.
    - **F7 forward-hint (Phase 2 주석 재작성 대상)**: css-lint.yml 헤더 주석의 graceful-skip 프레이밍도 재작성 대상이다 — 현 주석(line ~17-25, 57-59)이 "(1) job-level if: hashFiles(...) / (2) in-job EXIT 0 이중 보호(ADR-136 결정3)" 로 서술한다. 삭제 라인(59)만 지우고 주석의 "이중 보호"/"job-level if" 프레이밍을 잔존시키면 code-review lane 에서 "주석 ↔ 코드 불일치" P2 로 잡힌다. Phase 2 는 주석을 **단일 채널 = 경로 C(in-job fast-exit) + step-level 가드**로 교체하고 job-level if 언급을 제거한다(silent override 차단 취지의 `on: paths:` 금지 주석은 보존). code-review lane 확인 대상.
  - **(b)** graceful no-op 을 **step-level 가드(`if: steps.resolve_config.outputs.config_found == 'true'`) + in-job fast-exit(ANCHOR/TARGETS 0 개 → `::notice::` 후 `exit 0`) 단일 채널**로 일원화한다. **이 메커니즘은 이미 css-lint.yml 에 완비돼 있다** — `resolve_config` step + 세 후속 step 의 `if: config_found=='true'` 가드 + effective-config self-check·Run stylelint 의 `git ls-files ... head -n 1` / `mapfile ... -eq 0 → exit 0` fast-exit. 따라서 삭제한 job-level `if:` 은 이미 존재하는 이중 보호와 **중복**이었고, 그 중복 라인만 load-time invalid 였다. 결과는 결정 3 이 의도한 "frontend 무관 repo 에서 no-op" 과 동형이며 required-safe(required 승격 후에도 merge 비차단)이고 unique job name(결정 5) 무변경이다.
    - **⚠ 두 no-op 경계 구분 (F3 design-completeness 정정 — "전부 skip" 은 부정확)**: no-op 은 두 서로 다른 repo 형상에서 발현하고 흐름이 다르다.
      - **(경계 1) config-부재 repo**(frontend 미배포 = webapp preset config 없음): `resolve_config` → `config_found=false` → Install / Floor self-check / Run stylelint 세 step 이 step-level 가드로 **전부 skip** → job Success(경로 B skip 아님 — step skip, job 자체는 Success genuine). 무용 npm 설치 0.
      - **(경계 2) config-present & CSS=0 repo**(config 은 배포됐으나 실 .css/.scss 자산 0): `config_found=true` → **Install step 은 실행됨**(stylelint npm ci 설치 — 이 경우 무용) → Floor self-check 의 `ANCHOR="$(git ls-files '*.css' '*.scss' | head -n 1)"` 가 empty → `exit 0` → Run stylelint 의 `mapfile TARGETS` 가 0 개 → `::notice::` + `exit 0` → job **Success(genuine pass, 경로 C)**. 즉 경계 2 는 "전부 skip" 이 **아니라** Install 실행 + 이후 fast-exit 이다.
      - 결과 정합(양 경계 모두 Success·required-safe)은 무손상이나, 경계 2 의 무용 Install 은 **Phase 2 최적화 후보**: Install step 에도 CSS-존재 step-level 가드(예: 별도 `has_css` step output 도입 후 `if: config_found=='true' && has_css=='true'`)를 추가해 config-present & CSS=0 repo 의 무용 stylelint 설치(npm ci 시간·npm registry fetch 비용)를 회피. Negative 미세 리스크 = 무용 toolchain 설치(경계 2 한정, 기능 영향 0). Phase 2 판정 위임.
  - **(c) ADR-130 §결정4 2축 정합 논증 (F1 — "무손상" 단정 대체)**: ADR-130 §결정4 는 2축이다 — **(i) negative**: `on: paths:`/`branches:` path-filter skip **금지**(required check 를 'Pending(expected)' 영구로 만드는 함정 — F-4 경로 A). **(ii) positive**: graceful no-op 을 **job-level `if:` conditional skip** 으로 구현하라는 긍정 명령("반드시"). 본 정정의 §결정4 정합:
    - **(i) 무손상**: 본 fix 는 path-filter 를 도입하지 않는다 — job-level `if:` graceful-skip 을 in-job fast-exit 으로 바꾸는 것이지 path-filter 회귀가 아니다. negative invariant 온전 보존.
    - **(ii) 정합 (literal 메커니즘 조항은 좁혀지되 load-bearing invariant 보존)**: §결정4 (ii)의 긍정 형태(job-level `if:` conditional skip)는 **CSS-존재를 job-level 에서 판정하려면 `hashFiles`(디스크 접근)가 필요한데 job-level context-availability 부적격이라 실현 불가**한 조건 위에 서 있었다(§결정4 가 인용한 GitHub required-check 동작은 정확하나, 그 outcome 을 job-level `if:` 리터럴로 실현하는 예시가 born-invalid). in-job fast-exit(경로 C)은 §결정4 (ii)가 보증하려던 **outcome — required-safe non-blocking Success — 을 동형 달성**한다. 따라서 §결정4 의 *의도*는 "permanent-pending 회피(required check 가 skip 돼도 merge 비차단)" 이지 "job-level `if:` 리터럴 강제" 가 아니다. 리터럴 메커니즘 조항은 좁혀지되(job-level conditional skip → in-job fast-exit) load-bearing invariant(permanent-pending 회피 + path-filter 금지)는 온전 보존 → **ADR-130 amend 불요**.
  - **(d) 재발 root 봉인 (F2/F8 — 봉인 = 검출 ∪ 차단 분리 + byte-identical parity 제약 존중)**: `actionlint-check.yml` 이 born-invalid workflow 를 못 잡은 이유 = Run 명령 glob 이 `.github/workflows/*.yml` 만 lint 하고 `templates/github-workflows/*.yml` 을 **실 lint 안 한다**(line ~98). trigger `on: paths:`(line ~38-40)와 목적 주석(line ~7)은 이미 templates 를 포함하는데 실행 glob 만 빠진 born-incomplete 구현 gap 이다.
    - **⚠ F8 byte-identical parity 제약 (설계 lane firsthand 실측)**: `actionlint-check.yml` 은 양 copy(`.github/workflows/` + `templates/github-workflows/`)가 **byte-identical** 이며(`diff` exit 0 실측), invariant-check.yml Workflow parity step 의 `CONSUMER_ONLY_WORKFLOWS[]` exclusion 목록에 **없어 byte-identical parity 가 강제**된다(css-lint.yml 과 동일 parity lineage). 따라서 이 파일에 naive blanket glob(`templates/github-workflows/*.yml`)을 박으면 — **consumer repo(배포된 template copy)에는 `templates/github-workflows/` 디렉터리가 없어** unmatched glob 이 literal 로 actionlint 에 넘어가 "file not found" → warning-tier(비차단)라 merge 는 안 막지만 **매 consumer PR 마다 spurious warning comment** 발생. parity 파일에 wrapper-self 전용 경로(templates/ = wrapper 에만 존재)를 심는 것 자체가 관심사 오염.
    - **봉인 채널 결정 = (B) 관심사 분리 [권장, 채택]** — 두 채널의 책임을 disjoint 하게 나눈다:
      - **검출 채널 = actionlint-check.yml (parity 파일 무접촉)**: `.github/workflows/*.yml` lint 를 **그대로 유지**(consumer·wrapper 공통 정확 — 각 repo 의 실 workflow 는 항상 `.github/workflows/` 에 있음). templates/ 경로를 이 파일에 추가하지 않는다 → byte-identical parity 무손상 + consumer spurious warning 0. warning-tier(`continue-on-error: true`)라 검출 O·차단 X 는 F2 그대로.
      - **차단 채널 = wrapper-self discriminating test (§8 부록 `test-actionlint-workflows.sh`)**: `.github/workflows/*.yml` **+** `templates/github-workflows/*.yml` 양쪽에 actionlint 를 hard-fail(exit != 0)로 실행. wrapper-self only(`github.repository` gate 또는 test 하네스)라 consumer 미배포 → templates/ 부재 문제 무관. **즉 test 가 templates/ coverage 를 검출+차단 겸 담당**. templates/ 는 본디 wrapper-self 관심사이므로 wrapper-self 차단 채널에 집중하는 것이 관심사 정합이다.
    - **대안 = (A) dir-존재 조건부 glob [비채택]**: actionlint-check.yml Run step 을 `FILES=(.github/workflows/*.yml); [ -d templates/github-workflows ] && FILES+=(templates/github-workflows/*.yml); ./actionlint "${FILES[@]}"` 로 바꿔 wrapper(templates/ 존재)=양쪽, consumer(부재)=`.github/`만 lint → byte-identical parity 유지 + consumer spurious warning 회피. 유효하나 (i) parity 파일에 wrapper-self 분기(templates/ 존재 검사) 삽입 = 관심사 오염 (ii) warning-tier 검출 채널일 뿐 차단 아님 → (B) 대비 관심사 정합 열위로 비채택.
    - 따라서 "재발 봉인 = actionlint-check.yml `.github/` 검출(parity 무접촉) ∪ discriminating test templates/+.github/ 차단(wrapper-self hard-fail)". glob 단독을 봉인으로 과대 서술하지 않으며, parity-enforced consumer 파일에 blanket templates/ glob 을 박지 않는다.
    - ADR-026 amend 불요 판정 유지(정확 — line 7 목적 주석·trigger paths 가 이미 templates 포함, glob 확장은 born-incomplete 구현 gap fix). blocking-on-pr 승격은 ADR-060 별도 promotion path(scope out).
- **⚠ REFINE 반영 (요구사항리뷰 dual-peer — 두 Success 메커니즘 혼용 금지)**: "job skipped via `if: false` → GitHub 'Success'(**skip 메커니즘** — job 이 아예 안 돎)" 와 "step 이 실행돼 `exit 0` → 'Success'(**genuine pass 메커니즘** — job 이 돌되 검사 대상 0 이라 통과)" 는 둘 다 non-blocking Success 이나 **인과 경로가 다르다**. 결정 3 은 두 경로를 "또는" 으로 병렬 나열했으나(혼용 소지), 본 fix 는 후자(in-job fast-exit = genuine pass)를 **단일 채택** 한다. 전자(job-level conditional skip)는 그 조건식에 `hashFiles` 를 쓰면 load-time invalid 라 실현 불가하고, `hashFiles` 없이 실현하려면 job-level 에서 CSS 존재를 알 방법이 없다(디스크 미접근) → in-job fast-exit 이 유일 실현 경로.
- **ratchet 방향**: 결정 3(job-level graceful no-op 정책)·결정 4(floor self-check)·결정 12(resolution base)의 *실효를 복구* — born-invalid → 최초 실행 가능. floor rule 집합·tier·격리 설계·no-op 정책 의도 변경 0. carrier = css-lint.yml 양 copy(byte-identical parity — invariant-check.yml Workflow parity step, CFP-65/67/68 consumer-only exclusion lineage) job-level `if:` 삭제(Phase 2 구현 lane) + actionlint Run glob 확장(Phase 2) + discriminating regression test(§8 명세 = 하단 "§8 Test Contract 명세").
- **ADR 무영향 확인**: ADR-026(actionlint 게이트) amend 불요 — line 7 목적 주석이 이미 templates/ 포함 의도를 명시하고 trigger paths 도 templates/ 를 watch 하므로, Run glob 확장은 born-incomplete 구현 gap 을 실 코드 fix 로 메우는 것이라 정책 변경이 아니다(구현 lane deliverable). ADR-130(path-filter 금지 invariant) 무손상((c)). ADR-127 overlay 축소불가 / 결정 4 floor self-check 무손상 — 본 fix 는 그 게이트들이 *실행되도록* 하는 선행 조건 복구.
- **출처 (ADR-119, 본 lane firsthand 검증)**: 신규 concept doc [`docs/domain-knowledge/concept/github-actions-expression-context-availability.md`](https://github.com/mclayer/plugin-codeforge/blob/main/docs/domain-knowledge/concept/github-actions-expression-context-availability.md) F-1~F-5 와 정합. 핵심 anchor = ① GitHub "Contexts reference / Context availability" 표(job-level `if:` = `{github,needs,vars,inputs}` context + `{always,cancelled,success,failure}` function, `hashFiles` 제외 / step-level `if:` = + `{steps,runner,job,matrix,strategy,env}` + `hashFiles`) — 본 lane WebFetch 실측 confirm. ② actions/runner ADR-0279 verbatim "hashFiles() will only allow on runner side since it needs to read files on disk, using hashFiles() on any server side evaluated expression will cause runtime errors" — 본 lane WebFetch 실측 confirm. ③ actionlint v1.7.12 `ctx-spfunc-availability` check 가 검출 — 에러 문구 = `function 'hashfiles' is not available in this context`(설계 lane WebFetch checks.md 실측) / `calling function "hashFiles" is not allowed here`(요구사항리뷰 Codex 정확-태그 실행 ground-truth); 두 문구 모두 동일 check 출력(actionlint 버전·message 경로별 상이) → 회귀 test primary 판정 = exit != 0, secondary regex = `not allowed here|not available in .*context|ctx-spfunc`(tolerant, F6). css-lint.yml 양 copy load-time invalid 는 본 lane Read 실측(양 copy line 59 job-level `if: hashFiles(...)` byte-identical). actionlint glob gap 은 본 lane Read 실측(actionlint-check.yml line 98 Run glob = `.github/workflows/*.yml` only, trigger paths line 38-40 = 양쪽 watch — 불일치).

### 결정 13 부록 — §8 Test Contract 명세 (TestContractArchitectAgent input, Phase 1 = narrative only)

> **Phase 1 scope 경계**: 본 §8 명세는 **narrative(설계)** 다. 실 test 스크립트(`.sh`) + workflow(`.yml`) fix write 는 **Phase 2 구현 lane deliverable** 이다 — Phase 1 에 `.sh`/`.yml` write 금지(CFP-2527 선례: Codex 설계리뷰 false-pos "test missing" 은 Phase 2 deliverable 이라 기각). 설계리뷰가 "test 파일 부재" 를 P0/P1 로 올리면 Phase 2 deliverable 로 기각.

- **신규 스크립트(Phase 2, wrapper-self only)**: `tests/scripts/test-actionlint-workflows.sh` — actionlint(Go binary)를 `.github/workflows/*.yml` **+** `templates/github-workflows/*.yml` 양쪽에 실행. wrapper-self only(`github.repository` gate 또는 test 하네스 — consumer 미배포)라 templates/ 부재 문제 무관. 목적 = job-level `hashFiles` 류 context-availability 위반이 어느 copy 에도 (재)유입되지 못하게 하는 discriminating 회귀 채널.
  - **F8 봉인 역할 명시**: 결정13(d) (B) 채택에 따라 **본 test 가 templates/github-workflows/ coverage 를 검출+차단 겸으로 담당**한다(exit != 0 hard-fail). actionlint-check.yml(byte-identical parity 파일)은 `.github/workflows/` 검출만 유지·무접촉이므로, templates/ copy 의 재유입을 실제로 hard-block 하는 유일 채널이 이 test 다. 즉 봉인의 "차단" 채널 = 이 test, "검출" 채널(비차단) = actionlint-check.yml `.github/` lint.
- **discriminating 3-분기 (CFP-1334 mutation-kill fixture mandate)**:
  - **GREEN (정상)**: css-lint.yml 양 copy(+ 전체 workflow) actionlint **exit 0**. 정정 후 job-level `if:` 부재 상태 통과.
  - **RED (mutation-kill, load-bearing) — F6 판정 robust화**: css-lint.yml **사본**(fixture)에 job-level `if: hashFiles(...)` 재삽입 → **RED 판정 = actionlint `exit != 0` (primary — mutation-kill 판정)** + **stderr regex 매칭(secondary — 진단 라벨/디버깅 hint)**. **regex 미매칭이어도 exit != 0 이면 RED 성립** — regex 를 primary 로 두면 문구 drift 시 false-GREEN(mutation 이 살아있는데 regex 안 맞아 GREEN 오판) 리스크가 있으므로 regex 는 진단 보조로만 쓴다. **GREEN exit(0) ≠ RED exit(!=0)** 를 명시 대조(anti-theater — 게이트가 mutation 을 실제로 죽이는지 falsify). 이 분기가 없으면 게이트가 "돌기만 하고 안 잡는" hollow 로 새므로 필수.
    - **실측 문구 (secondary regex anchor)**: 요구사항리뷰 lane Codex 정확-태그 실행 ground-truth = `calling function "hashFiles" is not allowed here` (현 tolerant regex `not allowed here` 분기와 매칭 확인). 설계 lane WebFetch 실측(actionlint checks.md) = `function 'hashfiles' is not available in this context`. 두 문구 모두 actionlint `ctx-spfunc-availability` check 출력(actionlint 버전·message 경로별 문구 상이) → secondary regex = `not allowed here|not available in .*context|ctx-spfunc` (양 실측 문구 + anchor 포함, tolerant). primary(exit != 0)가 판정, regex 는 라벨.
  - **graceful skip (NOT silent pass)**: actionlint 미설치(Go binary 부재) 시 `::notice::` + SKIP 카운트 emit 후 non-fail(warning-tier 정합) — **silent pass 금지**(CFP-2527 C5 toolchain-skip 패턴 동형: skip 을 명시 보고해 "안 돌았는데 green" 은폐 차단).
- **관심사 분리 (신규 파일 권장 근거)**: 기존 `tests/scripts/test-css-lint.sh`(CFP-2527 C5)는 stylelint **runtime** 동작(config-resolution/exit-78)을 검증한다. 본 신규 test 는 workflow **parse validity**(load-time schema)를 검증한다 — 두 관심사는 orthogonal(runtime config-resolution ⊥ load-time context-availability)이라 한 스크립트에 섞으면 실패 원인 진단이 흐려진다. 따라서 별도 파일 권장. (Phase 2 가 최종 파일 배치 확정.)
- **anti-hollow 자기검증**: 신규 test job 이 css-lint-test 처럼 wrapper-self CI 에서 실행되는지(또는 기존 actionlint-check.yml green 이 회귀 채널로 충분한지) Phase 2 가 판정 — 단 self-CI 실행 채널이 skip 되면 test 가 dead 이므로 실행 경로 실측 의무(CFP-2527 self-CI css-lint job 영구 skip → test-css-lint.sh 단일 회귀 채널이 된 선례 답습).

## 결과

### Positive

- frontend 품질게이트의 ground-truth 층위 모델(텍스트<DOM<실레이아웃) 1급 ADR 정의 + D1/D2 직교·상보 표준.
- WEB-033 류 결함(미닫힌 brace 빌드 우회 → 레이아웃 발현)을 D1(원인) + D2(증상) 양층 차단.
- frontend.applicable CONDITIONAL flag(default false/안전) → 비-frontend consumer 무손상(additive).
- floor 축소불가를 CI effective-config 검증으로 강제 → ADR-127 의 overlay 확장-only/축소불가 invariant(§결정6 이 면제채널 폐지로 강화·재확인) 를 stylelint 영역에 동형 적용해 실효(config 차원 약화 가능 공백 해소).
- D1 graceful no-op = ~~job-level `if:`~~ **step-level 가드 + in-job fast-exit**(Amendment 2 CFP-2530 정정 — job-level `if: hashFiles(...)` 는 context-availability 위반이었음), path-filter 금지 유지 → ADR-130 §결정4 permanent-pending 함정 회피.
- 신규 메커니즘 0 — 전부 기존 ADR 패턴 확장(ArchitectAnalyst 검증, 충돌 0).

### Negative

- Node toolchain 신규 도입(현 CI = Python 단일) — CI-only 격리 + npx self-contained 로 완화하나 빌드 의존 추가.
- D2 browser-in-CI 비용(Chromium 설치 + render 실행) — frontend-bearing 시만 활성으로 비용 격리하나 0 은 아님.
- stylelint config 의 consumer overlay 약화 가능성 — CI effective-config 검증이 mechanism 이나 Phase 2 구현 의존(미구현 시 floor 보장 공백).
- whitelist/manifest 유지 비용(css-lint.yml 신설 시 applicability 명시 의무) — ADR-130 Negative 계승.

### Neutral

- **Story CFP-2505 자체 = doc-only(설계 SSOT = 본 ADR)** — 실 wire(css-lint.yml / stylelint preset / whitelist·manifest / §8.7 template / project-config-schema frontend block / bootstrap scaffold / check-doc-section-schema.sh §8.7 lint) = Phase 2 구현 lane. 본 ADR 은 표준·규칙만 정의.
- version bump = Phase 2 (template/preset/script 변경 시 — ADR-037 분류). marketplace mirrored-field(plugin.json name/version/description/author) 변경 0 → 본 Phase 1 marketplace_sync_required: false.
- domain-knowledge(frontend-quality-gate area 4 후보 문서 — ground-truth-layer-model / jsdom-layout-blindness / css-brace-nesting-trap / render-truth-headless-browser) 실 write = Phase 2(OMC S1 선례). 본 ADR 은 capture 후보만 식별.
- D1 required 승격 = 별도 follow-up Story(7일+unique job name 충족 후 — wave rollout).
- **CFP-2530 (Amendment 2) — born-invalid errata**: css-lint.yml 양 copy 의 job-level `if: hashFiles(...)` 는 css-lint.yml 신설(PR #2511, CFP-2505 Phase 2 — commit 7a9b0347, 본 lane firsthand 실측) 이래 workflow 를 load-time schema-invalid 로 만들어 D1 게이트가 0 회 실행됐다. Amendment 2 가 job-level `if:` 삭제(step-level 가드 + in-job fast-exit 로 대체) + templates/ 재유입 봉인(F2/F8: 검출 = actionlint-check.yml `.github/` lint[byte-identical parity 파일 무접촉] ∪ 차단 = wrapper-self discriminating test 가 templates/+.github/ hard-fail). 실 fix = Phase 2.
  - **version bump 근거 (F4 — ADR-037 diff_signal 매핑)**: Phase 2 변경 surface = css-lint.yml 양 copy(wrapper-self workflow) job-level `if:` 삭제 + actionlint-check.yml 양 copy Run glob 확장 + 신규 `tests/scripts/test-actionlint-workflows.sh`(wrapper-self test). 이 셋 모두 **non-mirrored surface**(plugin.json name/version/description/author = marketplace mirrored-field 무변경) → ADR-037 diff_signal surface-table 상 "wrapper-self workflow/test/docs 변경 = non-mirrored → **PATCH**" 귀속(ADR-037 diff_signal 매핑). 단 실 bump 등급 확정은 **Phase 2 가 ADR-037 게이트로** 산정(신규 test 파일 추가·workflow 편집 조합이 PATCH 이상으로 승격될지 Phase 2 판정 — 설계 판정 = PATCH 예상). marketplace mirrored-field 무변경 → **marketplace_sync_required: false** 유지.

## 관련 파일

- `templates/github-workflows/css-lint.yml` — D1 신규 독립 workflow. ~~job-level `if:`~~ → **step-level 가드 + in-job fast-exit**(Amendment 2 CFP-2530 정정), warning-tier first. 결정 3/5/6/13.
- `.github/workflows/css-lint.yml` — 위 template 의 wrapper-self copy(byte-identical parity). Amendment 2 job-level `if:` 삭제 대상(양 copy). 결정 13.
- `templates/github-workflows/actionlint-check.yml` + `.github/workflows/actionlint-check.yml` — **F8 결정: byte-identical parity 파일 무변경(무접촉)**. `.github/workflows/*.yml` 검출 유지(consumer·wrapper 공통 정확). templates/ blanket glob 삽입 금지(consumer 에 templates/ 디렉터리 부재 → unmatched glob → spurious warning). templates/ coverage 는 아래 test 가 담당. 결정 13(d) (B).
- `tests/scripts/test-actionlint-workflows.sh` — Amendment 2 discriminating 회귀 test(§8 명세, Phase 2, wrapper-self only). **F8: templates/github-workflows/ + .github/workflows/ 양쪽 actionlint hard-fail — 봉인의 "차단" 채널 + templates/ coverage 담당**. 결정 13 부록 + 결정 13(d) (B).
- `plugins/codeforge-develop/presets/webapp/.stylelintrc.json` — stylelint config preset (Phase 2, config-standard extends + version pin). 결정 7/11.
- `scripts/check-lint.sh` — CSS 분기 + 언어 함수 추출 보조 채널 (Phase 2). 결정 6.
- `templates/scripts/consumer_applicable_workflows.txt` — css-lint.yml whitelist 등재 (Phase 2). 결정 5.
- `templates/consumer-scripts.manifest` — closure 등재(graceful 채택 → 조건부 불요). 결정 5.
- `docs/project-config-schema.md` — `frontend` 섹션 + `frontend.applicable: bool` default false (Phase 2). 결정 2.
- `plugins/codeforge-design/templates/change-plan.md` — §8.7 UI 실렌더 검증 CONDITIONAL sub-section (Phase 2). 결정 9/10.
- `templates/story-page-structure.md` — §8 에 §8.7 미러 cross-ref (Phase 2). 결정 10.
- `scripts/bootstrap-consumer.sh` — webapp preset stylelint config scaffold (Phase 2). 결정 7.
- `docs/consumer-guide.md` — stylelint 도입 안내 + D2 branch protection context 추가 경고 (Phase 2). 결정 10.
- `archive/adr/ADR-RESERVATION.md` — row 136 active (CFP-2505).
