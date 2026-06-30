---
adr_number: 33
title: Docker-first Infra Engineering — InfraEngineerAgent mandate 재정의 + 4 SSOT 매트릭스 cell update
date: 2026-05-07
status: Accepted
category: Architecture
carrier_story: CFP-128
parent_epic: null
supersedes: null
amends:
  - ADR-014
amendment_log:
  - amendment_id: 1
    date: 2026-06-30
    status: applied
    summary: "Rust consumer 로컬빌드 경로 표준 — Docker rust-image 마운트 빌드(공식 패턴 + CARGO_TARGET_DIR 분리 + --user + 공통-부모 마운트)를 1차 경로로, MSYS2/MSVC/WSL2 toolchain 을 대안 경로로 codify. cargo check(링커-less 사전검증) = 로컬 1차 권장. build-verification ↔ artifact-equivalence 분별선 명문(로컬=보강·CI=권위 불변식). examples/rust-cli-minimal + templates/scripts/build-local.{sh,ps1} + consumer-guide §1q 산출물. §결정 1-7 본문 변경 0건 — Docker-first 정책의 Rust 로컬 dev-feedback 적용 codify(인프라 전략 자체 무변경)."
    ref: null
    carrier_story: CFP-2506
related_stories:
  - CFP-128
  - CFP-2506
related_files:
  - CLAUDE.md
  - templates/impl-manifest.md
  - docs/project-config-schema.md
  - docs/consumer-guide.md
  - templates/github-workflows/container-image-scan.yml
  - scripts/check-container-strategy.sh
  - examples/webapp-minimal/
  - examples/cli-tool-minimal/
  - examples/library-minimal/
  - examples/rust-cli-minimal/
  - templates/scripts/build-local.sh
  - templates/scripts/build-local.ps1
  - templates/consumer-scripts.manifest
  - docs/domain-knowledge/domain/build-toolchain/rust-local-build-equivalence.md
  - docs/inter-plugin-contracts/develop-output-v1.md
  - docs/inter-plugin-contracts/design-output-v2.md
is_transitional: false
---

# ADR-033: Docker-first Infra Engineering

## 상태

**Accepted (2026-05-07)** — CFP-128 Phase 1 wrapper PR #240 (`d8155a5`, merged 2026-05-07T04:56:20Z) + Phase 2 wrapper PR (본 PR, merge 시점에 effective). carrier_story = CFP-128 (single Story, not part of Epic). Effective date = Phase 2 wrapper PR merge timestamp (ADR-031 §14 freeze pattern 재사용 — 본 effective date 이전 Phase 1 PR open 된 모든 Story = grandfather, retroactive 강제 없음).

Phase 1 internal-docs PR (mclayer/codeforge-internal-docs#67) merged at 2026-05-07T04:46:52Z (`235c8c4`) — spec / plan / Change Plan / Story §1-§7 / Codex 7-area review CONDITIONAL_PASS archive.

본 ADR = ADR-014 (Operational Risk SSOT Distribution) **amend** — §7.4 OpRiskArch mandate 4 항목 추가 (container restart policy / volume DR / health check tuning / network mode). supersede 아님 (ADR-014 의 SSOT 분배 결정 자체는 그대로 유효).

## 컨텍스트

사용자 directive (2026-05-07):

> 한가지 중대 변경이 있다. 이제 Infra를 Docker를 사용하려 한다. 이를 위한 엔지니어링이 필요하다.
>
> 내가보기엔 Agent 구조의 재편이 동반될 것 같아서

### 현재 상태

InfraEngineerAgent (codeforge-develop, role:dev core — 현 `plugins/codeforge-develop/agents/InfraEngineerAgent.md`, 구 lane repo 삭제됨 2026-06-12) mandate = `systemd / launchd / Docker / K8s / PaaS / CI / cron / 패키징` (broad, 8 항목 평등). 어느 쪽이 default 인지 미명시. impl-manifest 예시 ([templates/impl-manifest.md:16](../../templates/impl-manifest.md#L16)) 도 systemd 우선. wrapper repo 내 Docker 실 fixture 0개 ([CHANGELOG.md](../../CHANGELOG.md) + examples/webapp-minimal narrative mention 만).

### 사용자 요구사항 해석

사용자 directive 의 "이제 Docker 사용" + "Agent 구조 재편" 의 의도를 brainstorming skill 5 turn / 6 substantive decision 으로 명시화 (CFP-128 spec §2). decision 6 = D1 Scope / D2 Lever / D3 Agent 재편 수준 / D4 Prod scope / D5 Migration / D6 Sec tooling.

### 거절된 대안

| Decision | 채택안 | 거절 대안 |
|---|---|---|
| D2 Lever | InfraEngineer mandate 재작성 (이 ADR) | presets/docker overlay / DockerEngineer 신설 / template fixture only |
| D3 Agent 재편 | mandate + 책임 매트릭스 cell update only | ContainerArch SubAgent 신설 / InfraEngineer 분할 / consumer overlay 위임 |
| D4 Prod scope | Dockerfile + compose 1st-class, K8s = preset opt-in | K8s 1st-class only / image+compose only / 3 다 1st-class |
| D5 Migration | Effective date 기반 + grandfather | hard cutoff / overlay flag / 30-day grace |

거절 합리성 = Codex 7-area review CFP-128-001 area_5_option_formulation PASS.

## 결정

### §결정 1 — InfraEngineerAgent default 출력 = Docker-first

InfraEngineerAgent mandate 재작성 (codeforge-develop sibling sync PR):

```yaml
role: dev
mandate: |
  운영 엔지니어링 — 컨테이너 자산 1st-class.
  primary: Dockerfile (multi-stage) + compose.yml + .dockerignore
  secondary: CI workflow (image build / publish / scan), k8s manifests (presets/k8s/ opt-in)
  legacy: systemd / launchd / PaaS (consumer overlay opt-in only — 본 ADR §결정 3)
```

impl-manifest 예시 row 교체: `deploy/systemd/<service>.service` → `Dockerfile` + `compose.yml` + `.dockerignore` (3 row append, 1 row delete).

### §결정 2 — K8s manifests = `presets/k8s/` opt-in

`mclayer/plugin-codeforge-develop/presets/k8s/` (NEW) — deployment.yaml.template + service.yaml.template + ingress.yaml.template + NOTES.md.

활성 mechanism = consumer overlay `project.yaml`:
```yaml
infra_strategy: docker_first  # default — Dockerfile + compose
infra_strategy_extras:
  k8s_preset_enabled: true    # opt-in K8s preset
```

K8s 가 1st-class 가 아닌 이유: 모든 consumer 가 K8s cluster 가용한 것 아님. 90% 케이스 = single host docker compose 충분. K8s = enterprise scale-up 옵션.

### §결정 3 — systemd / launchd / PaaS = legacy (consumer overlay opt-in only)

`infra_strategy: legacy_systemd` 명시 시만 fallback 허용. silent default 아님 — 명시적 opt-in 의무. PaaS (Heroku / Fly / Railway 등) = consumer overlay 자체 결정 (framework opinion 없음).

`infra_strategy: none` (3번째 enum value) = library / config-only repo 의 Docker artifact 미적용 default. examples/library-minimal 가 시범 (CFP-128 spec §3.3.6, plan Task 12).

### §결정 4 — SecurityTest 1st-layer = trivy + hadolint 추가

SecurityTestPLAgent (codeforge-review — 현 `plugins/codeforge-review/agents/SecurityTestPLAgent.md`) 1st-layer 자동 도구 세트 확장:

```
Before: Dependabot + CodeQL + Secret Scanning (3종, GitHub native only)
After:  + trivy (container image CVE)
        + hadolint (Dockerfile lint)
```

trivy false positive mitigation:
- workflow `--ignore-unfixed: true` default
- severity threshold = `CRITICAL,HIGH` (mid-severity = advisory only)

reusable workflow = `mclayer/plugin-codeforge/templates/github-workflows/container-image-scan.yml` (NEW).

### §결정 5 — CONDITIONAL SubAgent 매트릭스 cell annotation update

CLAUDE.md § "Deputy mandate 매트릭스 (codeforge-design lane)" 5 cell parenthetical 만 update (새 row 0 — boundary 모호 회피, ADR-014 SSOT 영향 최소화):

| §7 / §11 / §3 sub | Deputy | annotation 추가 |
|---|---|---|
| §7.1 Trust boundary | SecurityArch ✅ | + container network mode / secret mount |
| §7.4 DR/disconnect/...etc | OpRiskArch ✅ | + container restart policy / volume DR / health check |
| §7.5 민감 데이터 분류 | SecurityArch ✅ | + container secret mount; image layer 누설 |
| §11 Schema/Migration/Rollback | DataMigrationArch ✅ | + DB container volume / data persistence |
| §3 도입할 설계 (chief author 수준) | ArchitectAgent | + image base / multi-stage 전략 (Refactor consult) |

§7.4 cell 의 OpRiskArch mandate 확장 = ADR-014 amend (본 ADR `amends:` field). 4 새 항목 = container restart policy / volume DR / health check tuning / network mode. ADR-014 SSOT distribution 결정 자체 = 그대로 유효.

### §결정 6 — Migration policy = effective date + grandfather

**Effective trigger**: 본 ADR Status `Accepted` (Phase 2 wrapper PR merge timestamp) 이후 lane spawn 되는 Story 부터 의무.

**Grandfather scope** (ADR-031 §14 freeze pattern 재사용):
- Phase 1 PR 이 본 ADR effective date 이전 open 된 모든 Story = legacy 유지
- mctrader debut audit Issue #181 P1-3 in-flight Story 들 = grandfather
- 신규 Story = 자동 의무 (`infra_strategy: legacy_systemd | none` override 시만 예외)

**Consumer 측 follow-on Epic 의무화**:
- mctrader 5 repo (Tier B-extended) = 별도 Epic, **mctrader 워크스페이스에서 수행** (메모리 SSOT — wrapper 세션 직접 수행 금지)
- Epic 형태 = ADR-020 Mode B (hub-centralized, mctrader-hub) 기존 패턴 재사용
- 본 CFP-128 Story §11 회고에 "follow-on Epic candidate: mctrader containerization" pointer

### §결정 7 — 책임 매트릭스 + decision table 7 row append

[CLAUDE.md](../../CLAUDE.md) § "Design / Code / Security 리뷰 책임 매트릭스" 끝에 7 row append (CFP-128 spec §3.2.1) + § "원인 판정 decision table" 끝에 7 row append (CFP-128 spec §3.2.2). 상세 표 = CFP-128 Change Plan §3.2 / §3.3.

FIX Ledger §10 schema 무변화 (위 7 새 trigger 가 자연 발화 — 컬럼/row format 그대로).

## 영향

### 변경 영향 받는 SSOT (4 sibling repo + marketplace)

| Repo | 변경 |
|---|---|
| `mclayer/plugin-codeforge` (wrapper, canonical) | ADR-033 (NEW), ADR-014 amendments backref, CLAUDE.md 4 SSOT 매트릭스 update, templates/impl-manifest.md, docs/project-config-schema.md, docs/consumer-guide.md, templates/github-workflows/container-image-scan.yml (NEW), scripts/check-container-strategy.sh (NEW), examples/{webapp,cli-tool,library}-minimal/ |
| `mclayer/plugin-codeforge-develop` (sibling) | agents/InfraEngineerAgent.md mandate 재작성, presets/k8s/ (NEW), docs/inter-plugin-contracts/develop-output-v1.md (canonical) |
| `mclayer/plugin-codeforge-design` (sibling) | agents/OperationalRiskArchitectAgent.md §7.4 Container considerations, docs/inter-plugin-contracts/design-output-v2.md (canonical) |
| `mclayer/plugin-codeforge-review` (sibling) | agents/SecurityTestPLAgent.md (trivy + hadolint), templates/review-pl-base.md container security row |
| `mclayer/marketplace` | marketplace.json 4 plugin version bump mirror |

### Consumer 측 영향

- **신규 consumer**: framework default = Docker-first 자동 적용. `infra_strategy: docker_first` (default) — Dockerfile + compose.yml + .dockerignore 산출.
- **기존 consumer (mctrader 등)**: grandfather (Phase 1 PR open 시점 기준). retroactive 강제 없음. follow-on Epic 의무 (consumer 워크스페이스 수행).
- **Library / config-only consumer**: `infra_strategy: none` 명시 — Docker artifact 미적용 OK.

### Backward compatibility

- ✅ 기존 in-flight Story 무영향 (grandfather)
- ✅ 기존 consumer overlay 무영향 (`infra_strategy:` 미명시 시 default = `docker_first` 적용 — 신규 Story 부터)
- ⚠ Consumer 가 Docker artifact 부재 + `infra_strategy: docker_first` (default) 일 시 = `scripts/check-container-strategy.sh` 새 lint 가 exit 1. 명시적 `infra_strategy: legacy_systemd | none` 으로 회피 가능.

## 관련 ADR

- **ADR-014** (Operational Risk SSOT distribution) — 본 ADR 가 amend (§7.4 OpRiskArch mandate 4 항목 확장)
- **ADR-010** (Inter-plugin Contract Sibling Sync) — 본 Story cross-repo 전략 SSOT (wrapper canonical → 3 lane plugin sibling)
- **ADR-016** (Marketplace Registration Policy) — 4 plugin version bump → marketplace.json mirror PR
- **ADR-020** (Cross-repo Epic Pattern) — 본 Story 는 single Story (Mode A/B 무관). sibling sync = ADR-010 룰
- **ADR-031** (Lane spawn evidence trail) — effective date freeze pattern 재사용 + Story §14 lane evidence 의무
- **ADR-005** (N/A standardization) — §7.1-§7.5 / §8.5 / §11 의 N/A 명시 패턴
- **ADR-012** (wrapper CLAUDE.md SSOT boundary) — 본 ADR 가 update 하는 4 SSOT 매트릭스 정의
- **ADR-013** (codeforge family dogfood-out policy) — Spec/Plan/Change-Plan/Story 위치 internal-docs override
- **ADR-022** (Sonnet review-verdict decider) — 매 review iteration Sonnet final pick

## Codex 7-area review

**CFP-128-001-codex-spec-review.yaml** (gpt-5.5 high effort, 2026-05-07):
- overall_verdict: **CONDITIONAL_PASS** (P0:0, P1:3, all resolved)
- area_2_adr_audit: **PASS** — ADR-033 §결정 7개 internal consistency OK. ADR-014 amend 처리 OK. 기존 ADR conflict 없음.
- area_5_option_formulation: **PASS** — 6 거절된 대안 합리성 OK.
- 3 P1 fix 완료 (post-Codex commit).

archive: `mclayer/codeforge-internal-docs/wrapper/decisions/CFP-128-001-codex-spec-review.yaml`

## Effective date

`Phase 2 wrapper PR merge timestamp` placeholder — Phase 2 wrapper PR merge 후 follow-up commit 으로 실 ISO8601 timestamp populate (ADR-031 §14 freeze pattern). 본 ADR 가 status `Accepted` 로 전환되는 시점.

## 결과

**달성** (Phase 2 wrapper PR merge 시):
- InfraEngineerAgent default 출력 = Docker-first (Dockerfile + compose.yml + .dockerignore) — framework default 명시화
- 4 SSOT 매트릭스 (책임 + decision + 6 SubAgent mandate) cell update — boundary 모호 회피 (새 row 0, cell annotation only)
- §7.4 OpRiskArch mandate 4 항목 확장 (container restart / volume DR / health check / network mode) — ADR-014 amend
- SecurityTest 1st-layer trivy + hadolint 추가 — image CVE / Dockerfile lint 자동화
- consumer-side `infra_strategy` enum (docker_first / legacy_systemd / none) — opt-in / opt-out 명확
- 신규 consumer = Docker-first 자동 적용. 기존 consumer = grandfather (Phase 1 PR open 시점 기준)

**비용**:
- 1 ADR 신설 (ADR-033) + 1 ADR amend (ADR-014)
- CLAUDE.md 4 SSOT 매트릭스 row append (책임 +7 / decision +7 / 6 SubAgent 5 cell annotation)
- 4 sibling repo 동기 PR (wrapper canonical → develop / design / review sibling per ADR-010)
- 1 marketplace mirror PR (ADR-016, 4 plugin version bump)
- examples/ Docker fixture 추가 (webapp + cli-tool, library opt-out)
- scripts/check-container-strategy.sh + container-image-scan.yml workflow 신설
- consumer-side follow-on Epic 의무 (mctrader 등 — consumer 워크스페이스 수행)

**검증**:
- check-doc-frontmatter.sh + check-doc-section-schema.sh PASS (ADR / Story / Change Plan)
- check-inter-plugin-contracts.sh PASS (sibling sync 후)
- scripts/check-container-strategy.sh TDD 5 시나리오 PASS (Codex P1-3 fix)
- actionlint container-image-scan.yml PASS
- hadolint examples/{webapp,cli-tool}-minimal/Dockerfile 0 critical
- Story §14 Lane Evidence 7 row populated, lane-evidence-check.yml PASS
- phase-gate-mergeable gate:design-review-pass + gate:security-test-pass green

## 거부된 대안

본 ADR §결정 = 6 substantive decision (D1-D6, brainstorming 5 turn). 각 결정의 거절 대안:

- **D2 거절**: presets/docker overlay (의도 희석 — 일부 consumer 만 Docker), DockerEngineer 신설 (agent 수 증가 + boundary 모호), template fixture only (agent contract 명시 없으면 귀결성 부재)
- **D3 거절**: ContainerArch SubAgent 신설 (boundary 모호 + ADR-014 SSOT 영향), InfraEngineer 분할 (ROI 낮음 — Docker / compose / CI publish = 자연 묶음), consumer overlay 위임 (framework opinion 부재)
- **D4 거절**: K8s 1st-class (small-prod consumer 과잉), image+compose only (orchestration 책임 회피), 3 다 1st-class (mandate 과잉 + decision fatigue)
- **D5 거절**: hard cutoff (mctrader 동력 손실), overlay flag (drift 가능성), 30-day grace (solo-dev 일정 주도권 과잉)
- **D6 거절**: sec tooling 미도입 (Docker-first inconsistency), trivy + hadolint 둘 다 동시 (false positive 관리 부담), trivy-only (Dockerfile syntax 검증 공백)

거절 합리성 = Codex 7-area review CFP-128-001 area_5_option_formulation **PASS**.

## Amendment 1 — Rust consumer 로컬빌드 경로 표준 (CFP-2506, escalation #2503)

**carrier_story**: CFP-2506. **date**: 2026-06-30 (KST). **status**: applied. **본 ADR §결정 1-7 본문 변경 0건** — Docker-first 인프라 전략 자체는 무변경. 본 Amendment = 그 전략을 **Rust consumer 의 로컬 개발-피드백 경로**에 적용하는 표준을 codify 한 것(인프라 전략의 새 적용면 명문화이지 전략 재정의 아님).

### 동인

Windows 개발 환경의 Rust consumer 가 링커·binutils(`as.exe`·`dlltool`·`gcc`) 부재로 로컬 `cargo build`/`cargo test` 가 불가 → 매 변경이 분 단위 CI 왕복으로만 검증되어 피드백 루프가 늘어남(escalation #2503, mctrader simulator 세션). 컴파일·타입 버그(예: 비-Copy 값 `E0382 partial-move`)가 CI 에서야 표면화.

### A1-1 — Docker rust-image 마운트 빌드 = Rust 로컬빌드 1차 완전-빌드 경로 (ADR-033 §결정 1 Docker-first 정합)

native 링커 부재 host 에서 로컬 `build`/`test` 가 필요하면 **Docker rust-image 마운트 빌드를 1차 경로**로 표준화한다. 공식 패턴:

```
docker run --rm --user "$(id -u)":"$(id -g)" \
  -e CARGO_TARGET_DIR=/tmp/target \
  -v "<repo>":/src -w /src rust:<tag> cargo check
```

- `--user $(id -u):$(id -g)` — host↔container uid 불일치로 인한 산출물 권한 오염 회피(출처: docker hub rust 이미지 공식 패턴).
- `CARGO_TARGET_DIR` 분리 — host `target/`(Windows PE·캐시) ↔ container `target/`(ELF) 공유 시 캐시 오염 회피. named volume 으로 cargo registry 캐시 재사용 가능(출처: docker build cache / volumes 공식).
- rust 이미지 multi-arch(amd64/arm64) → M-series Mac 동작.

이 경로는 ADR-033 §결정 1(Docker-first default)·§결정 5 매트릭스 cell("§3 도입할 설계 ... image base / multi-stage 전략")의 자연 적용이다.

### A1-2 — build-verification ↔ artifact-equivalence 분별선 (Docker linux target 한계)

Docker linux 컨테이너 빌드는 target 이 `x86_64-unknown-linux-gnu`(ELF)로 바뀐다. 따라서:

- **보장(build-verification)**: 타입 검사·차용 검사·대부분의 컴파일 에러·플랫폼-비의존 로직의 `cargo test` 통과 — CI 권위의 *보강*으로 충분.
- **미보장(artifact-equivalence)**: `#[cfg(windows)]` 코드 경로·플랫폼-의존 동작(경로 구분자·파일 권한·FFI/winapi·줄바꿈)·Windows PE 산출물 ABI 자체. 이들의 ground-truth 는 **CI(Windows runner)** 가 권위.

표준 문서는 Docker 경로를 "컴파일·타입·플랫폼-비의존 테스트 검증"으로만 advertise 하고, "로컬은 보강(pre-flight)·CI 는 단일 검증 권위" 불변식을 명문화한다. **로컬 GREEN ≠ 머지 게이트** — branch protection 6-tuple 무축소(순수 가산).

### A1-3 — cargo check = 로컬 1차 권장(링커-less 사전검증)

`cargo check`(+`cargo clippy`)는 codegen 직전 정지(`--emit=metadata`)해 링커·`as`·`dlltool` 불요 — 링커 부재 host 에서도 동작하며 `E0382` 류 타입·차용 버그를 즉시 검출한다. 따라서 로컬빌드 표준의 **최소·고-ROI 1차 명령 = `cargo check`**(완전 빌드는 Docker/MSYS2/WSL2 2차 경로). Docker 미설치 host 는 `cargo check`(1차) 또는 MSYS2/WSL2(A1-4)로 graceful degrade.

### A1-4 — toolchain 대안 경로: MSYS2/MSVC/WSL2 (CI 권위 ABI 선결)

완전 빌드 toolchain 보강 시:

- **MSYS2(GNU ABI 보강)**: `pacman -S mingw-w64-x86_64-toolchain` 으로 `as`/`dlltool`/`gcc`(MinGW binutils) 채움 — `x86_64-pc-windows-gnu` target.
- **MSVC 전환(GNU→MSVC)**: Visual Studio Build Tools 설치 — `x86_64-pc-windows-msvc` target(rustup 기본). MinGW binutils 자체가 불요.
- **WSL2**: native linux rustup(repo 를 WSL2 native fs 에 둠 — `/mnt/c` NTFS cross-fs 는 3~10x 손실).

**선결 조건(비협상)**: MSVC↔GNU 는 ABI 비호환(C 런타임·예외·맹글링·import-lib 상이). 따라서 로컬 권장 ABI 는 **CI runner 의 권위 ABI 와 일치**해야 한다 — "무조건 MSVC" 권고는 거짓(CI 가 GNU 권위면 로컬도 GNU 채워야 로컬 GREEN↔CI RED 괴리 무재발). CI 권위 ABI 명세 채널 = 가이드 문서 선결-조건 명문(무거운 `project.yaml` 스키마 신설은 OOS — 과설계 회피).

### A1-5 — sibling crate 마운트 토폴로지 불변식

Cargo `path = "../other-crate"` 의존은 단일-repo 마운트 컨테이너에서 `../` 가 미해소되어 빌드 실패. **불변식 = 컨테이너 내부 `path=` 상대 토폴로지가 host 와 동형**. 기본 권장 = **공통-부모 마운트**(`-v <parent>:/src -w /src/<crate>`). 대안 = 개별 마운트+동형 배치 / Windows junction. build-local 스크립트는 단일 crate ↔ sibling-path workspace 를 다르게 처리(silent fail 방지).

### 산출물

- `docs/consumer-guide.md` §1q (opt-in 고급 섹션 말미 신규 서브섹션) + §3c preset 표 cross-ref.
- `examples/rust-cli-minimal/` (D1/D3 실증 fixture, cli-tool-minimal shape 답습).
- `templates/scripts/build-local.{sh,ps1}` (D2 권장 스크립트 쌍) + `templates/consumer-scripts.manifest` 등재(dependent-workflow 미부착 — CI invoke 아닌 ad-hoc CLI, `scripts/codeforge-upgrade.sh` 선례).
- `docs/domain-knowledge/domain/build-toolchain/rust-local-build-equivalence.md`(R-1~R-5 불변식 SSOT).

### 정합

- 신규 ADR 번호 미신설(in-flight Epic CFP-2481 번호 충돌 회피 + scope 과대 회피) → ADR-033 Amendment 로 처리.
- 본 Amendment = 문서·스크립트·example 표준이지 신규 엔진·신규 스키마 아님(과설계 회피, ADR-119 제안 필요성 게이트 정합).
- Story flow = Phase 1(§1-7 문서 + 본 Amendment + domain-knowledge) + Phase 2(consumer-guide·build-local·example·manifest 실체 + §8-11) — ADR-127 정식 풀 플로우.

## 해소 기준

N/A — permanent policy

## 관련 파일

- 본 ADR
- [ADR-014 Operational Risk SSOT distribution](ADR-014-operational-risk-ssot-distribution.md) — 본 ADR 가 amend
- [ADR-010 Inter-plugin Contract Sibling Sync](ADR-010-inter-plugin-contract-sibling-sync.md) — sibling sync 패턴
- [ADR-016 Marketplace Registration Policy](ADR-016-marketplace-registration-policy.md) — marketplace mirror
- [ADR-031 Lane spawn evidence trail](ADR-031-lane-spawn-evidence-trail.md) — effective date freeze pattern
- [ADR-005 Plugin Self-application N/A Standardization](ADR-005-plugin-self-application-na-standardization.md) — N/A 명시 패턴
- [ADR-012 Wrapper CLAUDE.md SSOT Boundary](ADR-012-wrapper-claudemd-ssot-boundary.md) — 4 SSOT 매트릭스 정의
- [ADR-013 codeforge family dogfood-out policy](ADR-013-codeforge-family-dogfood-out-policy.md) — Spec/Plan/Change-Plan/Story internal-docs override
- [ADR-022 Sonnet review-verdict decider](ADR-022-sonnet-review-verdict-decider.md) — 매 review iteration Sonnet decider
- CLAUDE.md (wrapper SSOT, 4 매트릭스 cell update)
- templates/impl-manifest.md
- docs/project-config-schema.md
- docs/consumer-guide.md
- templates/github-workflows/container-image-scan.yml (NEW Phase 2)
- scripts/check-container-strategy.sh (NEW Phase 2)
- examples/{webapp,cli-tool,library}-minimal/
- mclayer/codeforge-internal-docs/wrapper/{specs,plans,change-plans,stories,decisions}/CFP-128*
