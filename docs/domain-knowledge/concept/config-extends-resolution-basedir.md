---
kind: concept_definition
type: domain-knowledge
slug: config-extends-resolution-basedir
title: Config-extends resolution basedir — 격리 설치된 toolchain 의 shareable-config 가 config-file 위치 기준 module resolution 에서 미해결되는 hollow-gate 결함 class
status: Active
updated: 2026-07-01
carrier_story: CFP-2527
related_adrs:
  - ADR-136  # frontend 품질게이트 표준 — D1 stylelint CSS lint, 결정11 Node CI-only 격리(RUNNER_TEMP toolchain), 결정4 2-part AND floor
  - ADR-119  # research-before-claims — 외부 기술 사실(stylelint resolution 의미론) 자료조사+출처인용 의무
related_concepts:
  - mutation-based-hollow-gate-detection  # hollow-gate 일반 — 코드 실행은 되나 동작 미검증. 본 결함 = config-resolution 실패형 hollow-gate (sibling)
  - lane-verification-floor                # 게이트 자기 무결성(meta-hollow-gate) — warning-tier 게이트가 한 줄도 검증 못 하면 floor 미달
  - toolchain-decoupled-local-build-path   # toolchain 격리 패턴 family — CI-only 격리 설치의 resolution 비용 (sibling, 다른 언어)
related_files:
  - templates/github-workflows/css-lint.yml  # 본 결함 carrier — Install step basedir 미export, 두 stylelint 호출 --config-basedir 미지정
sources:
  - https://stylelint.io/user-guide/options/      # configBasedir 정의 — extends/plugins/customSyntax 상대경로 base directory
  - https://stylelint.io/user-guide/configure/     # extends = Node require.resolve() locater, npm module / 상대경로 referencing-config 기준
  - https://stylelint.io/user-guide/cli/           # --config-basedir / --print-config CLI flag 정의
  - https://github.com/stylelint/stylelint/blob/main/lib/utils/getModulePath.mjs    # resolution 순서(basedir→cwd→global-modules), NODE_PATH 미참조, ConfigurationError 메시지
  - https://github.com/stylelint/stylelint/blob/main/lib/augmentConfig.mjs          # configBasedir fallback = dirname(config filepath), augmentConfigFull 이 print-config·lint 공용
  - https://github.com/stylelint/stylelint/issues/1810   # "Extended config path can only be in the config file path" — config-file-dir 기준 resolution 실증
---

# Config-extends resolution basedir

## 정의

**Config-extends resolution basedir 결함 class** = lint/build toolchain 을 **격리 디렉터리**(CI 의 `$RUNNER_TEMP/...` 등 repo 밖 sandbox)에 설치하면서, config 파일이 `extends`(또는 plugins/customSyntax)로 가리키는 **shareable package(예: `stylelint-config-standard`)의 module resolution base** 를 그 격리 디렉터리로 지정해 주지 않아, resolver 가 config-file 위치(또는 CWD) 기준으로 package 를 찾다 실패하고 게이트가 **한 줄도 검증하지 못한 채 죽는**(continue-on-error warning-tier 면 merge 는 통과) hollow-gate 결함이다.

핵심 메커니즘 = **"설치 위치"와 "resolution 탐색 base" 의 분리**. 격리 설치는 `node_modules` 를 의도적으로 repo 밖에 둔다(host runtime 오염 회피 — toolchain-decoupled 패턴). 그러나 resolver 의 default base 는 config 파일이 사는 곳(또는 CWD)이지 격리 설치처가 아니다. 두 위치가 어긋나면 resolution 이 실패한다. 해소책 = resolver 에 격리 설치처를 **명시적 base** 로 주입(stylelint 의 `--config-basedir` / `configBasedir`).

## 컨텍스트

CFP-2527 동인 = ADR-136 D1 CSS lint 게이트(`templates/github-workflows/css-lint.yml`, escalation #2502) 의 hollow-gate 실증. ADR-136 결정11 은 **Node CI-only 격리** 를 의도적 설계로 채택했다 — toolchain 을 `$RUNNER_TEMP/css-lint-toolchain/node_modules` 에 격리 설치해 consumer host stack(Python/Go/Rust) production runtime 에 Node 강요를 0 으로 만든다. 그러나 Install step 이 `STYLELINT_BIN` 만 `GITHUB_ENV` export 하고 **basedir 을 export 하지 않았고**, 후속 두 step(`--print-config` self-check, 실 lint run)이 `--config <repo-root-config>` 만 주고 `--config-basedir` 를 주지 않아, stylelint 이 `extends: stylelint-config-standard` 를 config-file 위치(repo root) 기준으로 resolve 하다 repo root 에 격리된 package 가 없어 `ConfigurationError: Could not find "stylelint-config-standard"` 로 죽는다. continue-on-error(warning-tier)라 merge 는 통과하지만 단 한 줄도 lint 하지 못하는 hollow-gate.

이 결함은 toolchain 격리(설계상 정당)와 resolution base 명시(누락) 사이의 **구조적 결합 누락** — 격리를 채택하는 순간 resolution base 명시가 비협상 동반 조건이 된다는 점이 핵심 unknown-unknown 이다.

## 외부 사실 anchor (stylelint 공식 — ADR-119 자료조사+인용)

### F-1: `configBasedir` 정의 = extends/plugins 상대경로 + module resolution base
> "Absolute path to the directory that relative paths defining "extends", "plugins", and "customSyntax" are _relative to_. Only necessary if these values are relative paths." (출처: https://stylelint.io/user-guide/options/ , 동일 정의 CLI `--config-basedir` https://stylelint.io/user-guide/cli/)

공식 문서 자체는 "relative paths" 만 언급하나, 실제 source(F-4)는 npm-module-name resolution(`stylelint-config-standard`)에도 이 base 가 적용됨을 보인다 — 문서 표현보다 동작 범위가 넓다(문서-동작 갭).

### F-2: extends resolution = Node `require.resolve()` algorithm, referencing-config 기준
> "The value of `"extends"` is a "locater" (or an array of "locaters") that is ultimately `require()`d. It can fit whatever format works with Node's `require.resolve()` algorithm." + npm module name / "a relative path ... relative to the referencing configuration" (출처: https://stylelint.io/user-guide/configure/)

즉 extends 는 **config 파일이 사는 디렉터리 기준** Node module resolution 이다(CWD 기준 아님 — issue #1810 가 "Extended config path can only be in the config file path" 로 실증, 출처: https://github.com/stylelint/stylelint/issues/1810).

### F-3: `configBasedir` 미지정 시 default base = config 파일 디렉터리
> `const configDir = stylelint._options.configBasedir || dirname(cosmiconfigResult.filepath || '');` (출처: https://github.com/stylelint/stylelint/blob/main/lib/augmentConfig.mjs)

configBasedir 부재 시 fallback = `dirname(config filepath)` = config 파일이 사는 디렉터리. 본 결함에서 config 가 repo root 에 있으면 base = repo root → 격리된 node_modules 미발견.

### F-4: resolution 순서 = basedir → cwd → global-modules, **NODE_PATH 미참조**
`getModulePath` 는 ① 주어진 `basedir` ② `cwd`(default `process.cwd()`) ③ global `node_modules` 순으로 시도하며, **`NODE_PATH` 환경변수를 참조하지 않는다**. 실패 시 throw: `Could not find "{lookup}". Do you need to install the package or use the "configBasedir" option?` (출처: https://github.com/stylelint/stylelint/blob/main/lib/utils/getModulePath.mjs)

→ issue 의 "NODE_PATH 무효 / `--config-basedir` 만 유효" 단정은 **source 로 확증**(반증 아님). NODE_PATH=$WORK/node_modules 를 주어도 getModulePath 가 읽지 않으므로 무효.
→ 단 미묘한 정밀화: 순서가 basedir→cwd 이므로, CWD(=GitHub Actions 의 repo root)에 격리 설치가 있었다면 cwd fallback 으로 우연히 해결됐을 것이나, 본 결함은 설치처가 `$RUNNER_TEMP`(repo 밖)라 basedir·cwd 둘 다 빗나간다. 따라서 `--config-basedir "$WORK/node_modules"` 명시가 유일 해소.

### F-5: `--config-basedir` 는 `--print-config` 와 실 lint run 양쪽에 동일 적용
print-config 와 lint 는 동일하게 `augmentConfigFull()` → `extendConfig()` → `loadExtendedConfig()` → `mergeConfigs()` 로 extends 체인을 resolve 한다(출처: https://github.com/stylelint/stylelint/blob/main/lib/augmentConfig.mjs). 따라서 basedir 누락은 두 호출 모두를 죽이고, 수정도 **두 호출 모두**에 `--config-basedir` 추가가 필요하다(한쪽만 고치면 다른 step 에서 여전히 죽음).

### F-6: version drift — 17.x 유효성 (confirmed, drift 0)
위 resolution 의미론(getModulePath basedir→cwd→global, configBasedir fallback=config dir, augmentConfigFull 공용 경로)은 stylelint 의 장기 안정 아키텍처로, env 17.13.0 에서 유효함이 **confirmed** 다(공식 문서 = 최신 17.x 라인 기준 동일 정의, issue #1810 이래 동작 일관). **검증 방식 (CFP-2527 요구사항리뷰 lane dual-peer)**: ① ClaudePeer 가 정확 tag `17.13.0` source(`getModulePath.mjs` / `augmentConfig.mjs` / `printConfig.mjs` / `resolveConfig.mjs`)를 main 브랜치가 아닌 **tag `17.13.0` 기준으로 대조** — main 과 의미론 동일, line-level drift 0. ② CodexPeer 가 정확 태그 격리 sandbox(stylelint 17.13.0 / stylelint-config-standard 40.0.0) 실 실행으로 exit-code ground-truth(`--config-basedir` 부착 → exit 0 / 미부착 → ConfigurationError exit 78 / NODE_PATH-only → exit 78) 확증. 두 면(tag source 대조 + 정확 태그 실행) 모두 drift 0 → 추정 잔재 제거. (정정 단서: GitHub 태그 = v-prefix 없는 `17.13.0`; `v17.13.0` = 404.)

## 핵심 규칙

### R-1: 격리 toolchain 채택 = resolution base 명시 동반 (비협상 결합)
toolchain 을 repo 밖 sandbox 에 격리 설치하는 순간, config 의 extends/plugins resolution base 를 그 격리처로 **명시 주입** 하는 것이 비협상 동반 조건이다. 격리만 하고 base 를 안 주면 resolver default(config-file-dir / cwd)가 격리처를 빗나가 hollow-gate. 이는 toolchain-decoupled 패턴(host 오염 회피)의 숨은 비용 — 격리의 대가로 resolution 명시성이 든다.

### R-2: NODE_PATH 는 stylelint resolution 에 무효 — base flag 만 유효
stylelint `getModulePath` 가 NODE_PATH 를 미참조하므로, 격리 설치처를 NODE_PATH 로 알리는 우회는 작동하지 않는다(F-4). 유효 채널은 `--config-basedir`(CLI) / `configBasedir`(API)뿐. 다른 resolver(ESLint 등)는 NODE_PATH 동작이 다를 수 있어 toolchain별 resolution 명세 확인이 전제(generalize 시 주의).

### R-3: extends resolution 을 호출하는 모든 step 에 base 적용 (부분 수정 = 잔존 hollow)
print-config(effective-config self-check)와 실 lint run 이 동일 extends-resolution 경로를 타므로, base 는 extends 를 resolve 하는 **모든 호출**에 적용해야 한다(F-5). 한 호출만 고치면 다른 호출에서 ConfigurationError 잔존 → 부분 hollow.

### R-4: warning-tier hollow-gate 의 이중 은폐 위험
continue-on-error(warning-tier)는 hollow-gate 를 두 겹으로 은폐한다 — (a) merge 비차단이라 결함이 production gate 에 도달, (b) "lint 가 돈다" 는 외형(step 존재)이 "검증한다" 로 오인. 이 결함 class 는 required 승격 전 반드시 해소돼야 하며(lane-verification-floor R-5 meta-hollow-gate), discriminating test(mutation 생존 0 fixture)로 회귀 차단해야 한다.

## 경계

- **In scope**: 격리 설치된 lint/build toolchain 에서 config 의 shareable-package(extends/plugins) module resolution base 가 설치처와 어긋나 게이트가 검증 0 으로 죽는 hollow-gate 결함 class + resolution base 명시 해소책 + stylelint resolution 의미론(basedir→cwd→global, NODE_PATH 무효, print-config·lint 공용 경로).
- **Out of scope**:
  - extends 패키지가 끌어오는 **rule 내용**(config-standard cosmetic rule violation flood) — 이는 floor-rule vs cosmetic-rule 분리 정책(별 concept [[floor-rule-vs-cosmetic-rule-separation]] 후보), 본 결함과 **다른 층위**. 본 Story scope 외 follow-up(개념 §2차 참조).
  - 특정 CI runner·shell 의 env export 구문(GITHUB_ENV 등) 구현 디테일 — 구현 lane.
  - 비-stylelint resolver(ESLint/prettier/tsc)의 동형 결함 일반화 — 개념은 toolchain-비의존이나 resolution 명세는 toolchain별 상이(R-2 단서).
- **Anti-pattern**: 격리 설치 후 base 미명시(hollow-gate 본 결함). NODE_PATH 로 격리처 알리려는 우회(stylelint 무효 — R-2). extends-resolving step 중 일부만 base 적용(잔존 hollow — R-3). warning-tier 라 "merge 안 막히니 괜찮다" 로 hollow-gate 방치(이중 은폐 — R-4).

## 2차(부차) 개념 메모 — floor-rule vs cosmetic-rule 분리 (본 Story fold-in 금지)

issue 부차 발견: basedir fix 적용 시 `extends: stylelint-config-standard` 가 config-standard **전체 cosmetic rule** 을 끌어와 기존 styles.css(mctrader-web 1589줄)에서 144 violation(129 auto-fixable + 15 manual, manual 중 13 = no-descending-specificity) 발생 → warning-tier 영구 점등 → required 승격 영구 불가. 이는 ADR-136 onboarding 정책((a) floor-only config 분리 vs (b) `--fix`+잔여 manual cleanup 명문화)으로, **구현 버그(basedir)와 분리된 정책 항목**. 개념적 본질 = hollow-gate 의 두 층위 분리 — **층위1(resolution 실패 = 본 결함, 검증 0)** ↔ **층위2(검증은 되나 floor 초과 cosmetic noise = signal-to-noise 붕괴 → required 승격 불가)**. 본 Story = 층위1 만 scope. 층위2 = follow-up.

## 관련 ADR

- **ADR-136** 결정11 — Node CI-only 격리(RUNNER_TEMP toolchain). 본 결함의 격리 설계 anchor + resolution base 명시 누락 지점. 결정4 2-part AND floor(print-config self-check) = F-5 두-호출 수정 대상 중 하나.
- **ADR-119** — research-before-claims. F-1~F-6 외부 사실 자료조사+출처인용 의무 anchor.

## 변경 이력

- 2026-07-01 KST — 초기 작성 (CFP-2527 ResearcherAgent Mandate 1·2 산출물). stylelint 공식 docs(options/configure/cli) + source(getModulePath/augmentConfig) + issue #1810 cited. 기존 concept/ 자산에 config-resolution/module-resolution 주제 선행 부재(mutation-based-hollow-gate-detection = hollow-gate 일반, toolchain-decoupled-local-build-path = Rust toolchain 격리로 sibling 이나 resolution-base 결함 미커버) → 신규. issue 의 NODE_PATH 무효 단정 source 확증(F-4), basedir·print-config 양쪽 적용 단정 source 확증(F-5).
- 2026-07-01 KST — F-6 '추정→confirmed' 정정 (CFP-2527 요구사항리뷰 lane dual-peer P3 doc-hygiene). ClaudePeer tag `17.13.0` source 대조 + CodexPeer 정확 태그 격리 실행(exit 78 ground-truth) 양면으로 drift 0 confirm — 17.13.0 정확 태그 line-level 미대조 잔재 제거. 설계 lane ArchitectAgent 반영(ADR-136 결정12 Amendment 1 동반).
