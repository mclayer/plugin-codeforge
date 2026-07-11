---
adr_number: 147
title: CI runner topology — mclayer org self-hosted 이관 표준 (vars 기반 조건부 runs-on)
status: Accepted
is_transitional: false
category: Infrastructure
date: 2026-07-11
carrier_story: CFP-2607
related_adrs:
  - ADR-048-ci-native-test-execution
  - ADR-027
  - ADR-005
  - ADR-063
  - ADR-020
  - ADR-069
  - ADR-121
  - ADR-125
  - ADR-078
  - ADR-112
related_files:
  - templates/github-workflows/
  - .github/workflows/invariant-check.yml
  - .github/workflows/phase-gate-mergeable.yml
  - scripts/bootstrap-consumer.sh
  - scripts/reconcile-overlay.sh
  - docs/architecture/codeforge-family.md
related_stories:
  - CFP-2607
---

# ADR-147: CI runner topology — mclayer org self-hosted 이관 표준 (vars 기반 조건부 runs-on)

## 상태

`Accepted` (2026-07-11 KST) — CFP-2607 Epic Phase 1 설계 lane 확정. ArchitectPLAgent design lane supervised chief-author write per ADR-070 / CFP-578 chief author precedent (status `reserved` 미경유 직접 `active` — chief author scope, ADR-RESERVATION row 147). is_transitional: false (permanent infrastructure topology invariant — ratchet, 약화 방향 차단).

## 컨텍스트

mclayer org 의 CI 실행을 GitHub-hosted runner(`ubuntu-latest`)에서 org 소유 self-hosted runner 로 이관해 비용·속도·통제권을 확보한다. Phase 1(본 Epic)은 설계·문서만(코드 변경 0)이며 실 배선은 Phase 2 child Story 가 담당한다. 현재 codeforge family 의 workflow SSOT (`templates/github-workflows/`, 76 file / 96 `runs-on`)는 전부 `ubuntu-latest` 로 고정되어 있고, self-app 사본(`.github/workflows/`)은 `invariant-check.yml` 이 template 과 byte-identical 을 blocking 강제한다.

**runner infra (gh api 실측, PL firsthand)**:
- **group6 `self-hosted-linux-private`**: Linux 4대 online, 라벨 `[self-hosted, X64, Linux, docker]`, `allows_public_repositories=false`, `visibility=all`.
- **group5 `self-hosted-private`**: Windows 1대(`MCCHO-DESKTOP`), 라벨 `[self-hosted, Windows, X64]`(docker 미장착), `allows_public_repositories=false`, `visibility=all`.

**제약 3종 (설계 hard constraint)**:
1. **public repo 물리 배제** — GitHub 은 self-hosted runner 를 private/internal repository 전용으로 권장한다. fork PR 이 self-hosted 에서 임의 코드를 실행하는 것은 최대 공격 표면이기 때문이다 (source: docs.github.com "About self-hosted runners" / "Security hardening for self-hosted runners"). org 은 이를 `allows_public_repositories=false` 로 물리 강제한다 (source: docs.github.com "Managing access to self-hosted runners using groups").
2. **byte-parity blocking** — `.github/workflows/invariant-check.yml`(6-tuple 필수 컨텍스트 `invariant-check`)의 "Workflow parity" step 이 `templates/github-workflows/*.yml ↔ .github/workflows/<base>.yml` 을 `diff -q` 로 blocking 검사한다(L48-77). `CONSUMER_ONLY_WORKFLOWS` 18개만 제외되며 `phase-gate-mergeable.yml` 은 **제외 대상이 아니다** → self-app 사본은 template 과 반드시 byte-identical. (Story KU-9 의 "byte-parity blocking 게이트 부재" 는 self-app workflow 에 대해 오류다 — `wrapper-template-managed-coverage.yml`(warning-tier)은 `.claude/_overlay/**` marker coverage 를 검사하지 워크플로 byte-parity 를 검사하지 않는다.)
3. **public wrapper 는 같은 파일을 배포** — `plugin-codeforge`(public)는 template SSOT 를 보유하고 자기 자신에게 self-app 사본을 배포한다. 따라서 template 의 `runs-on` in-file default 는 public 이 물리적으로 만족 가능한 값(=hosted)이어야 한다.

## 결정

### §결정 1 — vars 기반 조건부 runs-on 계약 (단일 JSON-array key)

모든 in-scope workflow 의 `runs-on: ubuntu-latest` 를 아래 단일 표현식으로 대체한다:

```yaml
runs-on: ${{ fromJSON(vars.CI_RUNS_ON_JSON || '["ubuntu-latest"]') }}
```

- **단일 key `CI_RUNS_ON_JSON`** (JSON array 문자열) 하나로 scalar(단일 라벨)과 다중 라벨을 interface 1개로 통일한다. 2-key / 2-template-fork 방식은 SSOT 파괴·byte-parity 붕괴로 **기각**한다(RefactorAgent 권고 채택).
- **적용 범위 = uniform single-leg job (P1-2)** — Surface A 거버넌스 템플릿(전부 ubuntu 단일 leg) + Surface B 의 non-matrix job. **matrix os-leg job(Surface B 4 rust-ci + container job)은 §결정 11** — 단일 key 로 모든 leg 가 같은 값으로 resolve 되면 Windows leg 가 group5 라우팅을 상실(붕괴)하므로 leg-keyed 변수로 분기한다.
- **변수명 SSOT (P2-c)** — 요구사항 lane 표기 `CI_RUNNER`(scalar) = 본 설계 lock `CI_RUNS_ON_JSON`(array). scalar→array 확장(다중 라벨 지원). matrix Surface B 는 leg-keyed `CI_RUNS_ON_LINUX_JSON` / `CI_RUNS_ON_WINDOWS_JSON`(§결정 11). Story §5.2/§5.3/§6.2 의 구 `CI_RUNNER` 표기는 이 매핑으로 해석한다.
- **in-file default = `["ubuntu-latest"]` (불변)** — §결정 4 참조. 이 default 는 §제약 3(public wrapper 가 같은 파일 배포)에 의해 self-hosted 로 flip 할 수 없다.
- **Ports & Adapters**: workflow 파일 = port(실행 의도), repository variable = adapter(물리 runner 배선). runner 물리 선택은 파일이 아닌 variable 값으로만 표현된다.

> **확인불가 defer (research-before-claims)**: `fromJSON(...)` 이 `runs-on` 에서 **array 로 확장**되는 동작은 GitHub 공식 문서에 명시적 예시가 부재하다(source: docs.github.com "Workflow syntax — `jobs.<job_id>.runs-on`" 은 label array 와 표현식을 각각 허용하나 fromJSON-array-in-runs-on 조합의 명시 예시 없음). 따라서 이 계약은 §결정 6 카나리 이전에 **KU-2 dry-run(Change Plan §8)으로 실증**해야 하며, 실증 전 Phase 2 배선을 차단한다. scalar coalescing(`vars.X || 'default'`)은 흔한 패턴이나 array 확장은 추정 lock-in 금지 — dry-run 실측 대상.

### §결정 2 — public=GitHub-hosted / private·internal=self-hosted 분기

- **분기 규칙**: repository visibility 로 분기한다. public repository(`plugin-codeforge`, `marketplace`)는 `CI_RUNS_ON_JSON` **미설정** → §결정 1 coalesce 로 `["ubuntu-latest"]`(hosted) 유지. private/internal repository(대상 18개)는 `CI_RUNS_ON_JSON` 을 self-hosted 라벨 배열로 설정한다.
- **public 봉쇄 근거**: runner group 2개 모두 `allows_public_repositories=false` 이므로, 설사 public repo 가 self-hosted 라벨을 요청해도 GitHub 이 fail-safe 로 거부한다(올바른 실패 모드 — source: docs.github.com "Managing access to self-hosted runners using groups"). 이는 §결정 4 provisioning invariant 와 defense-in-depth 를 이룬다.
- **container job 배선**: `container:`/DooD 를 쓰는 job 은 group6(Linux, docker 장착)로 강제한다. group5(Windows, docker 미장착)는 container job 물리 불가.

### §결정 3 — byte-parity blocking 정합 (templates ↔ .github lockstep)

- template `runs-on` 을 §결정 1 표현식으로 수정할 때, 비-`CONSUMER_ONLY_WORKFLOWS` workflow 의 self-app 사본(`.github/workflows/<base>.yml`)도 **동일한 표현식으로** 수정해 `invariant-check.yml` byte-parity 를 통과시킨다.
- **public wrapper 기능 불변**: `plugin-codeforge`(public)에서 `CI_RUNS_ON_JSON` 은 미설정이므로 표현식이 `["ubuntu-latest"]` 로 coalesce → CI 는 hosted 에서 그대로 실행된다. 즉 "파일은 바뀌되(byte-identical vars 표현식 양쪽) 동작은 불변(unset var → hosted coalesce)". Story §4.1 의 ".github delta 0" 가정은 **오류** — 사본은 template 과 같은 vars 편집을 받아 byte-identical 을 유지해야 한다(delta = 동일 vars 표현식, 기능 inert).

### §결정 4 — provisioning invariant + fail-loud unset 감지 lint (private 안전은 default-flip 이 아니다)

RefactorAgent(in-file default=ubuntu-latest, public 안전)와 InfraOperationalArch(default=self-hosted, private billing-deadlock 회피)의 default 충돌을 chief tie-break ladder 로 해소한다:

- **ADR-068 invariant + §제약 3 지배**: public wrapper 가 같은 파일을 배포하므로 in-file coalesce default 는 **반드시 `["ubuntu-latest"]`** (public 은 self-hosted 물리 불가). default-flip 은 기각.
- **private 안전 = 2-layer 배선**으로 확보한다:
  - **(i) provisioning invariant** — 모든 in-scope private/internal repo 는 bootstrap Stage 5b(=`scripts/bootstrap-consumer.sh` L340-371 `wire-branch-protection.sh` 동형 hook 후보)에서 `CI_RUNS_ON_JSON` variable 을 **SET** 한다.
  - **(ii) unset 감지 lint(fail-loud) — 실행면은 billing-독립 (P1-1)** — in-scope private repo 에 required 변수(§결정 11 matrix repo = `CI_RUNS_ON_LINUX_JSON` ∧ `CI_RUNS_ON_WINDOWS_JSON` 둘 다, 그 외 = `CI_RUNS_ON_JSON`)가 미설정이면 fail-loud 로 감지한다. unset 은 hosted billing hard-block → 2-3초 FAIL → deadlock(AC-11)을 유발하며, 이는 조용한 pending 보다 나쁘다(InfraOp R-5 근거). **이 lint 를 hosted-CI 워크플로로 구현하면 안 된다** — 감지 대상인 billing 소진에 co-blocked 되어 발화 불가(**born-dead-gate** — Story §2.2/§2.7 이 확립한 hosted required check 2-3초 startup FAIL 과 동일 원인 class: css-lint born-invalid / execution-liveness 반복 재발). **실행면 = billing-독립 3택 조합**: ① **provisioning-time 스크립트(primary)** — bootstrap Stage 5b 에서 `gh api repos/{r}/actions/variables/{name}` 메타데이터 스캔(CI job 아님, operator/hub context = hosted 분 0)으로 변수 존재·값 검증, 미설정 시 provisioning 완료 차단 (**CI 실행 前이라 co-block 물리 불가**) ② **self-hosted runner 실행** — W0 착지 후 ongoing drift(변수 삭제) 검사를 self-hosted 에서(billing-free) ③ **org-level hub gh-api 주기 스캔**. **부트스트랩 순서 배선**: Stage 5b provisioning 검증(변수 present, fail-loud) → W0 runner 등록 → self-hosted ongoing drift 검사. "언제 lint 가 살아나는가" = provisioning-time(CI 이전) + self-hosted(W0 이후) — hosted-CI 아님.
  - **(iii) provisioning scope 제약 (P2-d)** — 변수는 **repo-scoped** 로 provisioning 한다. **org-level variable 금지**(또는 visibility-scoped private-only). org-level `CI_RUNS_ON_*_JSON` 은 public `plugin-codeforge`/`marketplace` 까지 override 해 §결정 2/3 의 delta-0(hosted 유지)을 파손한다.
- default-flip 을 provisioning invariant + fail-loud detection 으로 대체하는 이 판정은 Change Plan §7.4/§9 에 명문화한다.

### §결정 5 — preinstall baseline 계약

- **bare-tool baseline** (`git` / `bash` / `python3`+`pip` / `jq` / `gh` / `node`)는 self-hosted 이미지에 preinstall 을 의무화한다.
- **웨이브별 toolchain** (`rust` / `node` / `python` 버전 등)은 workflow 안 `setup-*` step 으로 주입한다(`runs-on` 이 아니라 job step 층 — RefactorAgent 단일 abstraction 유지).
- 카나리에서 `command -v <tool>` 실측으로 baseline 존재를 gate 한다(Change Plan §8). preinstall 목록 확정값은 카나리 실측 대상(`[empirical-source: canary 실측 대상]`, 추정 lock-in 금지).

### §결정 6 — 카나리 + 웨이브 롤아웃 (W0 부트스트랩 포함)

- **W0 (부트스트랩·1회성)**: SecurityArch P0 완화 순서 준수 — (1) 부트스트랩 PR 을 **runner 미등록 상태에서** 먼저 merge → (2) workflow diff 를 사람이 verbatim 리뷰 → (3) **그 후** runner 를 등록(코드 실행 전 검증). admin-merge 감사기록에 workflow diff 해시를 남긴다. **TOCTOU 가드(P2-a)**: runner 등록 직전 `main HEAD SHA == 검토된 workflow diff 의 base SHA` 를 재확인하는 게이트를 둔다 — 리뷰↔등록 사이 main 이 전진했으면 재리뷰(등록 차단). 부트스트랩 한정성은 "물리 게이트"가 아니라 **감사 convention**(1회성 라벨 + admin-merge 감사기록 + registration-time HEAD 재확인 게이트)으로 실태에 맞춰 bound 한다. 이는 billing hard-block 하에서 거버넌스 required check(check-gate/phase-gate-mergeable)가 dead 인 순환 merge-gate(Story §2.7 C-BOOTSTRAP)를 의도적·수동 admin-merge 1회로 돌파하는 조치이며, ADR-048 Amd2 의 *자동* admin-merge(5분 stuck fallback)와 구분된다.
- **카나리**: 1개 저부담 repo 에서 §결정 1 계약을 실측한다. 성공기준 = Change Plan §8 의 5-AND(실 runner metadata=self-hosted / pickup bounded / required context 전부 green / mergeStateStatus=CLEAN / preinstall baseline 실측).
- **웨이브**: 카나리 PASS 후 나머지 private/internal repo 를 웨이브로 순차 이관. Windows leg(단일 runner group5)는 직렬화 병목이므로 각 웨이브 내 최후순위. `--scale` 은 웨이브 최대 병렬 이상으로 설정한다(값 = 카나리 실측).

### §결정 7 — queue-starvation 24h 가드

- self-hosted 의 3 실패모드(runner offline / label-mismatch / group-거부)는 "Expected but never created" 상태(runner 부재로 check 가 아예 report 되지 않음)를 만들어 admin-merge rerun 조차 무효화한다.
- **가드**: job pickup 이 24h 내 발생하지 않으면 fail, 48h 내 미완료면 취소한다(source: docs.github.com "Self-hosted runners reference — usage limits"). 이 상태는 "정상 대기"가 아니라 DR 사안(사용자 통지)으로 분류한다 — §결정 9 참조.

### §결정 8 — fork PR self-hosted 미실행 + DooD/persistent 완화

- **fork PR + `pull_request_target` = self-hosted 미실행 유지**(SecurityArch Q-3, 비가역·보안). self-hosted 는 `workflow_dispatch`(수동) + 동일 repo 브랜치 push(org 멤버)만 트리거한다. fork PR CI 가 필요하면 hosted 를 유지한다 (source: docs.github.com "Security hardening for self-hosted runners" / GitHub Security Lab "Preventing pwn requests").
- **org allow_forking 실측(PL firsthand)**: `mctrader`(internal) `allow_forking=false`, org `default_workflow_permissions=read`, `can_approve_pull_request_reviews=false` → fork-PR 공격 표면은 대체로 CLOSED. 단 18 repo 전수 `allow_forking` 확인은 구현/리뷰 lane prerequisite 로 명시한다.
- **DooD 완화**: DooD job 은 host root 등가(`docker.sock` → escape) 이므로 non-privileged container / trusted 화이트리스트로 제한한다.
- **persistent runner 완화**: cross-job 오염(secret / tool-cache) 차단을 위해 ephemeral/JIT 를 권고하고, job 후 purge + secret 을 CLI-arg 로 전달 금지한다. org-wide PAT(`CODEFORGE_CROSS_REPO_PAT`) 사용 job 은 hosted 유지 또는 OIDC 로 전환한다.

### §결정 9 — ADR-048(ci-native) Amendment 필요성 (stuck 판정 pickup-기반)

- `ADR-048-ci-native-test-execution` Amendment 2 의 5분 stuck-classifier 는 self-hosted 의 정상 queue-time 대기(특히 group5 Windows 단일 runner 의 matrix leg 직렬화)를 stuck 으로 오판해 premature admin-merge(게이트 무력화)를 유발할 수 있다.
- **carve-out**: stuck 판정을 pickup-기반으로 정련한다 — job 이 runner 에 **assigned + started** 인가(정상 실행 → 임계 상향: self-hosted 20~30분, Windows leg 별도) vs 단순 pending·미배정(진짜 stuck → DR: 사용자 통지, admin-merge 아님). 임계 상향값은 `[empirical-source: canary 실측 대상]` (추정 lock-in 금지).
- **본 §결정 9 가 carve-out 의 normative 정의다**: (a) stuck 판정 입력 = job 이 online·label-match runner 에 **assigned+started** 되었는가(`gh api .../runs/{id}/jobs` 의 `runner_name` non-null ∧ `status=in_progress`) (b) assigned+started = 정상 → self-hosted 라벨 job 은 stuck 임계 상향(카나리 실측값, 잠정 20~30분; Windows group5 leg 별도 상향) (c) **미배정(no matching online runner) = 진짜 stuck → DR 경로(사용자 통지, admin-merge 아님)** — self-hosted queue-time 을 hosted 초 단위 가정으로 오판해 premature admin-merge 하는 게이트 무력화를 차단한다.
- `ADR-048-ci-native-test-execution` **Amendment 3** 은 본 §결정 9 를 cross-ref 로 채택한다(Phase 2 prerequisite — Change Plan §10). 실 ADR-048 파일 amendment(amendment slot claim 포함)는 구현 lane follow-up.

### §결정 10 — ADR-RESERVATION 인용 slug 의무 + ADR-005 mirror 오귀속 정정

- ADR-048 번호는 dual-occupancy 이다: `ADR-048-ci-native-test-execution`(Accepted, canonical) + `ADR-048-ghec-governance-as-code`(Proposed, orphan). 본 ADR 이 ADR-048 을 인용할 때는 **slug 를 명시**한다(번호만 인용 금지 — ambiguous). related_adrs 에서 `ADR-048-ci-native-test-execution` slug 명시로 이 의무를 이행한다.
- ADR-005 mirror 오귀속 정정: workflow byte-identical mirror invariant 의 SSOT 는 ADR-005 가 아니라 ADR-027 Amd3(marker) + ADR-063(marketplace) + 실 enforcement=`invariant-check.yml` 이다. 본 ADR 은 mirror 를 ADR-005 에 귀속하지 않는다(ADR-005 = N/A 표준화만).

### §결정 11 — matrix os-leg / container-job per-runner 차등 (Surface B, P1-2)

**gap**: `runs-on: ${{ matrix.os }}` 로 `matrix.os:[ubuntu-latest,windows-latest]` 를 도는 job(firsthand 확인: `mctrader-engine/.github/workflows/rust-ci.yml`; 4 matrix rust-ci repo = mctrader/-engine/-market/-data-collector)에 §결정 1 단일 key 를 적용하면 두 leg 가 같은 변수 값으로 resolve → Windows leg 가 group5 라우팅을 상실(붕괴). §결정 5 의 `setup-*` step 은 도구 설치이지 runner **선택**이 아니라 gap 미해소.

**mechanism = leg-keyed 변수 + include-based hosted default**:

```yaml
strategy:
  matrix:
    include:
      - leg: linux
        runner_default: '["ubuntu-latest"]'
      - leg: windows
        runner_default: '["windows-latest"]'
runs-on: ${{ fromJSON(vars[format('CI_RUNS_ON_{0}_JSON', matrix.leg)] || matrix.runner_default) }}
```

- **leg 별 라우팅 보존**: linux leg → `CI_RUNS_ON_LINUX_JSON`(private=`["self-hosted","X64","Linux","docker"]` → **group6**, public/unset=`["ubuntu-latest"]`); windows leg → `CI_RUNS_ON_WINDOWS_JSON`(private=`["self-hosted","Windows","X64"]` → **group5**, public/unset=`["windows-latest"]`).
- **byte-identical**: `matrix.include` 블록 + `runs-on` 표현식이 repo 간 uniform → §결정 3 byte-parity 무붕괴. 분기는 leg-keyed 변수 **값**에서만.
- **container job**: DooD/`container:` job 은 항상 linux leg key(group6, Windows docker 부재 §결정 2)로 pin.
- **provisioning invariant(§결정 4)**: matrix repo 는 `CI_RUNS_ON_LINUX_JSON` ∧ `CI_RUNS_ON_WINDOWS_JSON` 둘 다 SET; unset 감지 lint 는 둘 다 검사.
- **범위 구분**: Surface A(거버넌스 템플릿 = uniform ubuntu 단일 leg)는 §결정 1 단일 key 로 충분. 본 §결정 11 은 Surface B 4 matrix rust-ci + container job 한정.
- **확인불가 defer**: `vars[format(...)]` 동적 변수 lookup + `matrix.include` 의 `runner_default` 참조 조합은 fromJSON-array(§결정 1)와 동일하게 GitHub 공식문서 명시 예시 부재 → **KU-2 dry-run 에 windows-leg 확장 실증 추가**(Change Plan §8). 기존 `matrix.os` step 참조(setup-*/cargo target 등)는 `matrix.leg` rename 시 Phase 2 InfraEng 가 동반 갱신(또는 `os` 필드 병기 보존).

### §결정 12 — 관측성 (P2-e)

- **app-level runtime metric = N/A** (앱 런타임 0 — CI 배선 governance).
- **runner-level 관측성 (신규 boundary)**: self-hosted runner host 는 신규 실행 경계이므로 (a) runner online status(GitHub runner API `status:online`, §결정 6/7 DR) (b) queue-depth / pickup-latency(§결정 7 queue-starvation 24h 가드 + §8 카나리 5-AND(2) pickup bounded) (c) restart 자동복구(§결정 6 restart-aware) 를 관측한다. 상세 = Change Plan §7.4/§8 cross-ref.

## 결과

- **긍정**: (a) 단일 vars key 로 76 file / 96 `runs-on` 을 SSOT 1개 interface 로 통일 → byte-parity 무붕괴. (b) public repo 는 코드 변경 없이 unset-var coalesce 로 hosted 유지(위험 CLOSED). (c) private/internal 은 variable 값만으로 self-hosted 배선 → 파일 재작성 0. (d) branch protection 필수 컨텍스트 문자열은 불변(job id / job name 은 `runs-on` 과 orthogonal — INV-2).
- **부정·trade-off**: (a) fromJSON-array-in-runs-on 은 dry-run 실증 전 미확정(§결정 1) — Phase 1.5 dry-run gate 필요. (b) provisioning invariant 미충족 repo 는 billing-deadlock 위험 → fail-loud lint 신설 비용(Phase 2). (c) self-hosted persistent runner 는 secret/tool-cache 오염 신규 공격 표면(§결정 8) → ephemeral 전환 운영 비용.
- **영향 경계**: `templates/github-workflows/` (SSOT) + `.github/workflows/` (self-app lockstep) + `scripts/bootstrap-consumer.sh`(Stage 5b provisioning hook) + `docs/architecture/codeforge-family.md`(C4 Container + trust boundary 갱신, ADR-078). branch protection 필수 컨텍스트 문자열은 **불변**.
- **제외**: public 2(`plugin-codeforge`/`marketplace`) + `mctrader`/`deploy-k8s.yml` 3 ARC job(`mctrader-dev/stg/prd` — 이미 self-hosted). deploy scope 는 ADR-121 활성이나 deploy job 도 본 runner topology 를 cross-ref 통과.

## 해소 기준

N/A — permanent policy (is_transitional: false). 본 ADR 은 org CI runner topology 의 영구 invariant 이며 sunset 대상이 아니다. 약화 방향(예: public repo self-hosted 허용, byte-parity 완화)은 supersede ADR 없이 금지된다.

## 관련 파일

- `templates/github-workflows/` — runs-on SSOT (Surface A, Phase 2 편집)
- `.github/workflows/invariant-check.yml` — byte-parity blocking enforcement (L48-77)
- `.github/workflows/phase-gate-mergeable.yml` — 6-tuple 컨텍스트 (job id `check-gate`, runs-on orthogonal)
- `scripts/bootstrap-consumer.sh` (L340-371) — Stage 5b provisioning hook 후보
- `scripts/reconcile-overlay.sh` — workflow 채널 wholesale cp (L546-547, MARKER_NONE)
- `docs/architecture/codeforge-family.md` — C4 Container + trust boundary 갱신 (ADR-078 lane gate)
