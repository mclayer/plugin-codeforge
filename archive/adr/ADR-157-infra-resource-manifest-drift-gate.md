---
adr_number: 157
title: 인프라 자원 선언 manifest + startup fail-closed 계약 + CI drift scan — consumer 런타임 boot invariant (ADR-003 3-layer 정의역 밖 신설)
status: Proposed
is_transitional: false
category: governance
date: 2026-07-16
related_files:
  - .claude/_overlay/project.yaml
  - docs/project-config-schema.md
  - scripts/lib/check_infra_resource_drift.py
  - scripts/check-infra-resource-drift.sh
  - .github/workflows/infra-resource-manifest-drift.yml
  - templates/github-workflows/infra-resource-manifest-drift.yml
  - plugins/codeforge-test/agents/IntegrationTestAgent.md
  - archive/adr/ADR-060-evidence-enforceable-promotion-framework.md
  - archive/adr/ADR-003-three-layer-drift-responsibility.md
  - archive/adr/ADR-096-min-prerequisite-version-manifest-schema.md
related_stories:
  - CFP-2700
amendments:
  - by: "CFP-2700"
    date: "2026-07-17"
    scope: "§결정 8 (iii) 교체 + (vi) 신설 + §결정 9.1 표 각주 — 결정가능 경계를 static-vs-dynamic 에서 position-carried semantics 로 재획정. G2 구현리뷰 FIX1 실측(scripts/*.sh 163 파일 form 스캔 11 hit / 진성 2 / 정밀도 약 18%)이 '정적 리터럴 = 일괄 결정가능' 서술의 과대를 반증 → shell 변수읽기면을 (vi) 로 정직 공개하고, 키 리터럴 position 등가인 env-passthrough form(실측 1 hit / 0 오탐) 만 carve-in. 검출 축소 0(.py 100% 정밀도 무변경 + .sh 는 구조적 0 → passthrough 검출 신설 = 순증)."
    sunset_justification: "null — ADR-157 = is_transitional:false permanent policy → ADR-058 §결정 5 sunset trigger 미해당. 본 Amendment = 강화/중립 방향 — ① 실검출 순증(.sh passthrough carve-in = 종전 구조적 0 → 1 표면, .py 경로 무변경) ② §결정 8 = honest-ceiling 절 자체이므로 (vi) 추가는 해당 절의 설계된 기능 수행(은폐 금지 이행)이지 강도 축소 아님 ③ 오탐 18% extractor 미채택 = §결정 7(b) FM1-false-positive 봉인 보존. 기존 (i)~(v) 천장·D1~D5 결정·death-mode 봉인 전부 무축소."
  - by: "CFP-2700 G5"
    date: "2026-07-17"
    scope: "§결정 4 ref-pin 교체 + namespace 정직 주 신설 + §결정 8 (vii)(viii) 신설 — cross-repo 2 통제(namespace allowlist / ref-pin) 정직화. G5 구현리뷰 P1 2건 실측(firsthand): F-CR-002 = allowlist 가 검사 대상과 동일 출처(cross)라 `ns not in allowlist` 조건이 항상 False = tautological dead code(실 차단은 _NS_RE 형식검증) / F-CR-003 = ref-pin 이 moving-HEAD 7-denylist 만 거부 → mutable branch(feature-x/staging/release/1.0) 수용, 'pin 된 tag/SHA 대조' 미집행(name-based 로 tag/branch 구분 불가). 두 건 = '선언 ≠ 배선'(I-7) 자기위반 → dead allowlist 전량 제거(실 차단=_NS_RE+loop-domain+fetch-result fail-closed 로 100% 보존) + ref-pin 을 moving-HEAD hard-fail + non-SHA advisory WARN 로 정직화(엄밀 idempotency=SHA-pin `^[0-9a-f]{7,64}$` 만 보장)."
    sunset_justification: "null — permanent policy. 강화/중립 방향 — ① 허위 통제 주장 제거(allowlist=dead, 실 차단 무변) ② 허위 'tag/SHA 강제' 주장 정정 + non-SHA WARN 순증(종전 침묵 수용 → surfacing) ③ 검출 무축소(_NS_RE spoof 차단·moving-HEAD hard-fail·SHA idempotency 보장 전부 무변). §결정 7 5축·Amendment 1 (i)~(vi) 천장·failure-mode 분리(content-mismatch/token/transient/403·404) 전부 무변경."
---

# ADR-157: 인프라 자원 선언 manifest + startup fail-closed 계약 + CI drift scan — consumer 런타임 boot invariant (ADR-003 3-layer 정의역 밖 신설)

## 상태

`Proposed` (2026-07-16 KST) — CFP-2700 (Epic) Phase 1 carrier. ArchitectAgent chief author (ADR-070 chief author scope). Epic child G1 이 본 ADR 을 D1 schema 와 함께 착지시킨다.

## 컨텍스트

### 문제 — 인프라 자원 변경의 미전파가 조용히 통과한다

로직·저장소·인프라 자원의 추가/이동/제거 시 그 자원을 참조하는 하드코드·설정·**타 저장소 코드**가 전부 따라오지 못해 코드가 깨진다. firsthand 재현 사고:

- `mctrader-data` 가 로컬 inhouse MinIO 를 제거하고 외부 NAS 2-backend(raw/derived)로 이전(`1d6eb3e` / PR #965). 그러나 ① 루트 compose 는 여전히 로컬 minio 를 띄우고 단일 `MCTRADER_MINIO_*` 만 주입 ② `mctrader-data-collector`(Rust 쓰기면, **별도 저장소·별도 언어**)는 raw/derived 개념 grep 0건 ③ 같은 자원을 env 키 3종으로 하드코딩.
- 결과: config load 는 **조용히 통과**(derived=None, opt-in)하고 첫 파생 write 에서 `DerivedBackendNotConfiguredError` **지연 크래시**(`storage/_routing.py:125`).
- **핵심**: 문서가 없어서가 아니다 — ADR + change-plan 둘 다 작성됐는데도 타 저장소로 전파되지 않았다. 결손 = 정보 부재가 아니라 **전파의 기계적 강제 부재**.

### wrapper-self 재현 — 이 병은 codeforge 자신에게도 있다

`ADR-107` frontmatter 는 `mechanical_enforcement_actions: [plugin-declarative-seed-byte-parity-check, design-lane-plugin-feasibility-check]` 를 **Active** 로 선언하나 실측 = 전부 부재(스크립트·workflow·registry entry 없음, 잔존 = hotfix-bypass 라벨 2개뿐, verified). 즉 "선언 ≠ 배선"(I-7)이 wrapper 에서 이미 발생했다. 그리고 wrapper 는 실 secret 자원 **9종**(`grep -rhoE "secrets\.[A-Z_]+" .github/workflows/ | sort -u` = 9, verified)을 보유하며, 동일 논리자원(Confluence 자격증명)이 `ATLASSIAN_API_TOKEN`(선언면, project.yaml) ↔ `CONFLUENCE_API_TOKEN`(소비면, forward-sync workflow) **2계열**로 존재한다 — MinIO 사고의 "env 키 난립" 과 동형이 wrapper 라이브에 실재.

### 왜 신규 ADR 인가 — ADR-003 3-layer 정의역 밖

`ADR-003`(SSOT drift 3 layer: CI invariant / SessionStart 부트스트랩 / 사용자 가이드)의 정의역은 **codeforge 자신의 self-SSOT 정합**이다(대표 산출물 3종 = `invariant-check.yml` / `check-bootstrap.sh` / `consumer-guide.md` 전부 codeforge 실행물). 본 정책의 D2(**consumer 제품 런타임의 부팅 fail-closed**)는 codeforge 가 아니라 consumer 제품 바이너리가 실행하는 invariant 로, ADR-003 §결정 2 Q1 의 3-bucket(plugin repo 내부 / consumer 환경=GitHub label·org-perm / 1회 setup) 어디에도 들어가지 않는다(§결정 3 상술). ADR-003 §대안 D 는 4번째 layer 가 필요한 *기제*("본 ADR supersede 또는 amend")를 주지만, D2 는 그 self-SSOT 도메인 밖이라 4th layer 가 아니라 **별도 정의역의 신규 ADR** 이 옳다. ADR-003 에는 오귀속 방지 boundary-note 만 Amendment 로 남긴다.

### 선행 ADR 정합 (verified)

- `ADR-076` — **Sunsetted**(`superseded_by: imperative-walker-protocol-v1`). 죽은 SSOT → **인용 금지**. D1(선언 *스키마*)과는 disjoint 축.
- `ADR-096` — min_prerequisite_version manifest schema. §결정 0 closed-set scope = **carrier *위치*(project.yaml + plugin.json dual)** 한정이지 project.yaml 전체 block 집합을 닫는 규정이 아니다 → D1 이 project.yaml `infra_resources:` block 확장으로 삶은 **무충돌**(disjoint 도메인, Amendment 불요, §결정 1 상술).
- `ADR-011` / `ADR-107` — 死因 3-mode 의 근거(§결정 7 상술).
- `ADR-060` — D3 CI drift scan 의 host framework. tier·승격은 ADR-060 Amendment(warning-tier entry) 소관, 본 ADR 은 승격 로직을 발명하지 않는다.
- `ADR-033` — `infra_strategy: {docker_first, legacy_systemd, none}` = 기존 applicability 축. D5 는 이 축 재사용(신규 flag 금지). manifest(자원 내용) ⊥ infra_strategy(applicability 스위치) 역할 분리.

## 결정

### §결정 1 — 인프라 자원 선언 manifest schema (D1, 2-plane, project.yaml carrier)

인프라 자원을 prose 가 아닌 **기계판독 manifest** 로 선언한다. carrier = consumer(및 wrapper-self dogfood) `.claude/_overlay/project.yaml` 의 **신규 `infra_resources:` block**(ADR-096 §결정 0 closed-set 은 carrier *위치* 한정이므로 신규 block 추가는 위반 아님 — 신규 sidecar 파일은 carrier proliferation 이라 회피). 스키마 SSOT = `docs/project-config-schema.md` `infra_resources` 섹션(본 ADR 이 스키마 *문서* author, 실 값 맵은 consumer overlay author — write boundary: consumer-authored). 2-plane:

```yaml
infra_resources:
  resources:                        # plane A — 자원 카탈로그 (id 단위)
    - id: raw-nas                   # 자원 논리 ID (env 키 아님)
      namespace: mctrader-data      # (선택) cross-repo 참조 시 필수 — §결정 4
      canonical_env: MCTRADER_RAW_NAS_URL
      aliases:
        accepted:  [MCTRADER_MINIO_URL]        # 동일 자원의 수용된 별칭
        deprecated:                            # 기한 필드 필수 (R6)
          - name: MINIO_URL
            status: deprecated
            deprecated_since: 2026-07-16
            remove_after: 2026-10-01
  execution_units:                  # plane B — 실행단위 → required 자원 (ID-only 참조)
    collector:
      required: [raw-nas]           # resource-id 만 참조 (env 키 재기재 금지 = drift 방지)
      resource_modes:               # EDGE 속성 — unit×resource 마다 mode
        raw-nas: required           # ∈ {required, optional_degradable}
    candle-writer:
      required: [raw-nas, derived-nas]
      resource_modes:
        raw-nas: required
        derived-nas: optional_degradable
        derived-nas_degraded_behavior: "파생 write skip + WARN, raw ingest 지속"
```

- **4 필수 필드**(AC-1/AC-2): 각 resource 는 `id` · `canonical_env` · `aliases`(빈 집합 허용) 표현, 각 execution_unit 은 `required[]` 표현. 필드별 누락 = negative fixture 로 non-zero exit(AC-2).
- **`mode` 는 자원 자체가 아니라 execution-unit×resource EDGE 에** 둔다(AC-18). 같은 토큰이 unit A 에서 optional, unit B 에서 required 일 수 있다(예: ADR-103 dry-run 자원). `optional_degradable` 시 `*_degraded_behavior` 필수 — 미설정을 fail 시키지 않되 무엇으로 degrade 하는지 선언 강제(no-silent-degrade).
- **env 키는 자원의 투영이지 자원이 아니다** — plane B 는 resource-id 만 참조하고 env 키를 재기재하지 않는다(재기재 = 2군데 진실 = drift 원천). canonical env key = **자원당 정확히 1개**(INV-4): env 키 다종 난립은 canonical 부재의 *증상*이지 원인이 아니다.
- **applicability vs 내용 분리**: `infra_strategy`(ADR-033, 적용 여부 스위치) ≠ `infra_resources`(자원 내용). 둘을 겹치지 않는다.

패턴 재사용(신규 발명 아님): `_env` reference 규약이 이미 project.yaml 6개소에 정착(`deploy.docker_hub.auth_secret_env` / `deploy.1password.connect_*_env` / `deploy.ssh_targets[].key_secret_env` / `atlassian.confluence.api_token_env` / `integration_test.*.connection_env`, verified) — D1 = 산재한 기존 규약의 중앙화 + (자원 ID · alias · mode) 필드 추가.

### §결정 2 — startup fail-closed 대조 계약 (D2, consumer 제품 실행, I-5 채택-bounded)

실행단위는 부팅 시 자신이 선언한 required 자원이 실제 설정됐는지를 **첫 business 동작 이전 startup 단계에서 대조**하고, 미설정 시 non-zero exit + 미설정 자원 ID 를 loud 하게 로그한다(지연 크래시 = 불합격, AC-3). **D2 = 제품 property(계약)이지 wrapper 의 강제가 아니다**(I-5): wrapper 는 plugin 이라 consumer 런타임에 코드를 주입할 수 없다. 따라서 D2 의 강제 범위 = **"wrapper 계약 + 참조 구현을 consumer 가 채택한 경우"** 로 한정하고, 미채택 consumer 미강제를 honest-ceiling 에 공개한다(AC-4). 이 구분을 흐리면 "wrapper green = 전 consumer 안전" 이라는 거짓 보증이 생긴다.

**proto-D2 4중 결함 정정이 계약의 선결(G3 선결)**: 기존 proto(`IntegrationTestAgent.md` `.env` 키 확인 step + `project-config-schema.md` `required_env_keys`)는 4중 결함(verified) — (a) `grep -q "^${key}=" .env || echo` **exit-masking**(키가 빠져도 exit 0) (b) `.env` 파일 grep ≠ **프로세스 env** (c) 빈 값 통과(`^KEY=`) (d) **fail-open 기본**("미정의 시 감지 비활성"). 죽은 proto 위에 계약을 얹으면 계약도 죽는다. 올바른 reference impl 계약:

1. **프로세스 env 검사**(`.env` 파일 파싱 아님) — 실행단위가 실제 보는 환경을 본다.
2. **exit-masking 금지** — 미설정 = non-zero exit 로 전파(assertion/카운터 부재의 `|| echo` 금지).
3. **빈 값 reject** — set-but-empty 도 미설정으로 간주.
4. **fail-closed default** — 선언된 required 자원은 감지 대상, "미정의 시 비활성" 금지. required → 부팅 거부 / optional_degradable → degrade + WARN(§결정 1 EDGE).

정정 대상은 기존 shell masking lint(`check_shell_test_masking.py`, scan glob = `scripts/test-*.sh`+`tests/scripts/*.sh`)의 **정의역 밖**(agent `.md` 펜스, verified)이므로 별도로 정정한다.

**crash-loop 함정(운영)**: D2 boot-refuse × `restart: always` = 무한 재시작. 완화 = distinct exit code(구성 오류 signal) + bounded restart + readiness probe 로 자원 미충족 시 unhealthy 표면화(§8.5 in-flight state 부재라 §8.5.2 대상 아님).

### §결정 3 — ADR-003 정의역 경계 (D2 는 3-layer 밖)

ADR-003 §결정 2 Q1-Q3 결정 tree 에 D2 를 실제로 태우면 **어느 bucket 에도 안 든다**: (Q1) 발생 지점 = plugin repo 내부도, consumer *환경*(GitHub settings/label/org-perm)도, 1회 setup 절차도 아닌 **consumer 제품 런타임의 부팅 순간**이다. (Q2) 자동 회복 축 무관 — 부팅 거부는 회복이 아니라 방어. (Q3) PR-time 검증 비용 축 무관 — 검증 주체가 CI 가 아닌 제품 바이너리. 즉 ADR-003 의 3 layer 는 전부 codeforge 가 실행하는 self-SSOT drift 검출이고 D2 는 그 정의역 밖이다. §대안 D("4th layer amend")는 같은 self-SSOT 도메인의 4th layer 를 위한 것이지 다른 정의역의 D2 를 위한 것이 아니다. → ADR-003 에는 **오귀속 방지 boundary-note** Amendment 만 남기고(정의역 경계 명문화), D2 의 실 계약은 본 ADR-157 이 소유한다.

### §결정 4 — cross-repo 대조 계약 (In-scope 확정 DEC-2, failure-mode 분리, ref-pin)

원 사고의 미탐지 지점이 별도 저장소·별도 언어(Rust collector)였고, per-repo manifest 는 Pact broker 구조가 아니라 저장소 경계 전파를 못 한다. 따라서 cross-repo 대조를 **In-scope 정식 요건**으로 편입한다(OOS 분기 제거). 단 "본 정책은 전파를 *수행*하지 않는다 — 미전파를 각 참조면에서 loud 하게 *검출*할 뿐"임을 명시(green ≠ 전파 완료, riftmap "worse than no graph" 회피).

- **credential**: `CODEFORGE_CROSS_REPO_PAT` 재사용(ac-traceability-matrix.yml:65 선례, 23 workflow 사용중) — 신규 credential 도입 아님. **정직 주의(SecurityArch P0)**: 이 PAT 는 **read-only 토큰이 아니다**(실토큰 = classic `repo`+`workflow` read-WRITE no-expiration, ADR-066 Amd5). D3 는 이 토큰을 **read-only 로 *사용*(contents fetch only)** 할 뿐이며, "read-only PAT" 라고 서술하지 않는다(workflow yml 주석의 "read-only" 표기도 사용 방식이지 토큰 권한이 아님).
- **자원 ID cross-repo 네임스페이스**: top-level `namespace:` 필드 + cross-repo 참조 시 `<ns>/<id>` fully-qualified. cross-repo 참조만 fq 필수(§3.5 ADR-044 동형 충돌 회피 — 자원 ID `raw-nas` 도 repo 경계를 넘으면 ADR 번호 cross-repo 충돌과 동형 충돌을 낳는다).
  - **namespace 통제 정직(Amendment 2 — G5 P1 F-CR-002)**: fetch 도메인 = **선언된 namespace 집합**(순회 대상 = manifest cross-repo 자원 그 자체)이고, `_NS_RE`(`owner/repo` shape anchored)가 malformed·traversal(`../evil` 등)을 차단한다. **별도 operator-approval allowlist 는 없다** — manifest = **신뢰 declaration source**(§7.2 semi-trusted, namespace 는 공격자 주입 아닌 작성자 선언)이고 fetch = read-only 라, 같은 consumer-authored carrier 안의 "allowlist" 는 검사 대상과 동일 출처(tautology)이자 보안 분리 무제공이다. 미승인/오타 namespace 는 fetch 404 → hard-fail, 오타-실재 repo 는 content-mismatch → fail-closed 로 **이미** 걸린다(중복 gate 불요). §결정 8 (vii) honest-ceiling 로 집행.
- **failure-mode 분리(InfraOp 핵심 — flaky 타repo 가 본 repo CI 상시 red 회피, ADR-011 death 재현 차단)**:
  - fetch-success + content-mismatch = **DRIFT → fail-closed**(non-zero).
  - **token 부재(우리 misconfig) = degraded FAIL**(AC-21 유지 — main-path degrade 재사용 금지).
  - **foreign-repo transient unavailable(503 / network / timeout) = fail-OPEN + loud warning + Issue 발행**(타 repo 의 flakiness 가 본 repo 게이트를 상시 red 로 만드는 것 = ADR-011 death 재현이므로 회피).
  - foreign 403 / 404 = `resp.ok` 확인 후 판정(ADR-145 §결정 4 conflation 가드).
- **normative Phase 2 test 요건(FIX-2 — §8 test contract, AC-21 우산; 신규 §5 AC 아님)**: fail-open 은 drift 를 조용히 삼킬 수 있는 유일 분기이고 Issue 가 유일 audit trail 이므로, 정직성 담보용 fixture 2건을 normative 로 강제한다 — (t1) **positive fixture**: foreign 503/timeout → fail-open + WARN + **Issue 발행**(Issue 미발행 mutant = kill 대상). (t2) **discrimination fixture**: content-mismatch 은 transient 로 **분류되지 않음**(content-mismatch → transient/fail-open 오분류 mutant = 최중요 kill).
- **ref-pin(InfraOp + idempotency)**: 타 repo 의 moving main HEAD 가 아니라 manifest 에 pin 된 ref 를 대조해 moving-target-red 방지 + 재실행 결정성(§11 idempotency)을 노린다. **집행 실태 정직(Amendment 2 — G5 P1 F-CR-003)**: name-based 로는 tag 와 branch 를 **구분할 수 없다**(오직 SHA 만 `^[0-9a-f]{7,64}$` 로 판별) → "pin 된 tag/SHA 만 대조" 는 **집행 불가**한 과대 서술이었다. 실 집행 = **① moving-HEAD blocklist(`main`/`master`/`head`/`trunk`/`develop`/`default`/`latest` 7종) = hard-fail** + **② 그 외 non-SHA ref(tag/mutable-branch) = 수용하되 WARN**("비-SHA ref 는 idempotent 미보장 — mutable branch·재지정 tag 는 재실행 간 content 변동 가능"). **엄밀 idempotency 는 SHA-pin 만 보장**. tag 를 hard-reject 하지 않는 이유 = 본 §결정4 설계 의도가 tag(인간 가독 pin)를 포함하고 SHA-strict 는 그 반대 위반이기 때문. gh-verify(ref 가 tag 인지 API 확인)는 자원당 network round-trip·중첩 failure-mode 추가 대비 이득 낮아(보안 경계 아님) 미채택. §결정 8 (viii) honest-ceiling 로 집행.

### §결정 5 — DEC-3 alias-model 수렴 (canonical = `ATLASSIAN_API_TOKEN`, live rename 안 함)

wrapper Confluence 자격증명 2계열을 **alias-model 로 수렴**한다(라이브 secret rename 하지 않음 — rotation-adjacent risk 회피, 물리 rename = OOS follow-up):

- **canonical = `ATLASSIAN_API_TOKEN`**, **accepted alias = `CONFLUENCE_API_TOKEN`**.
- 근거(정정된 rationale — Mapper 반증 반영): canonical 이 ATLASSIAN 인 이유 = **Atlassian-account-scoped blast-radius 를 정직하게 명명**(CONFLUENCE 명은 blast-radius 과소표현). "Jira 공용" 근거는 **폐기**(Jira 는 무-secret session OAuth, 토큰 미사용).
- 2-channel(MCP-session PRIMARY / CI-fallback ALTERNATIVE)은 **의도적**(confluence-forward-sync.yml:8-13 documented). manifest 가 canonical 1 + accepted alias 를 선언하면 선언면(project.yaml)·소비면(workflow) 둘 다 classified → D3 재스캔 zero-unclassified(AC-22). "canonical 1 + alias N 수렴" 이면 물리 rename 없이 충족.
- **born-useful 정직(FIX-3)**: G6(2계열 canonical 수렴) *이후* wrapper-self D3 의 지속 효용 = ① census-floor 유지 ② 미래 자원 추가 시 drift 가드 — **현존 2계열의 물리 *제거* 가 아니다**(accepted alias 로 축복되어 존치, 라이브 rename = OOS follow-up). 2-channel 의 '의도적' 판정은 Story §4.0 `[hypothesis]` 수준이며 `[verified]` 로 격상하지 않는다(over-claim 회피).

### §결정 6 — 역색인(D4) = 비커밋 ephemeral CI artifact

역색인은 D3 스캔의 **생성 부산물**(가시화 전용, 권위 원천 아님, I-1)이며 저장소에 커밋하지 않고 **CI artifact 로만** 방출한다(비권위 부산물). 근거:

- ADR-107 §결정 1 Path B("mirror-SSOT = drift 실증 실패, single-SSOT default 권장")와 정합 — 커밋 역색인은 mirror-SSOT 형상이라 상충. 비커밋이면 mirror 자체가 없어 상충 소멸.
- CFP-2673 계보 D4 tautology(생성물을 그 생성기로 검증 = self-match false-GREEN) 소멸(비교 대상 커밋본 부재).
- freshness 결박(stale 역색인 = D3 fail) 불요 — 매 실행 재생성이라 stale 개념 자체가 없다.
- I-1(역색인 변조로 판정 불변) 자연 충족(AC-8) — 판정은 manifest+scan 결과에서만 나오고 artifact 는 read 되지 않는다.
- 역색인은 스캔 커버리지(스캔한 표면 + 못 한 표면 class)를 함께 방출(R8 disclaimer).

### §결정 7 — "왜 이번엔 다른가": 3-death 봉인 (누락 = 설계리뷰 P0)

이 repo 에서 **drift 게이트가 죽는 것은 예외가 아니라 패턴**이다(3중 확증). grandfather baseline 단독으로는 불충분하다(Analyst 정정) — 3개의 서로 다른 death mode 를 각각 봉인해야 한다:

**死因 3-mode(firsthand)**:
- **FM1 — born-red**: ADR-011 = path-prefix 를 verbatim 비교가 drift 로 오판한 **false-positive**(technical debt 아님) → 만성 fail → 매 PR bypass 상시화로 은퇴 불가.
- **FM2 — Wave-2-never**: ADR-096 `mechanical_enforcement_actions: []`(선언만 착지, 배선 영원히 미도달).
- **FM3 — subject 소멸**: 모노레포 consolidation(ADR-118 D5)이 ADR-011/107 의 cross-repo subject 를 제거 → `check-inter-plugin-drift.sh` 부재 확증(검사 대상 자체가 사라짐).

**ADR-157 이 5축으로 봉인**:
- **(a) FM1-debt** = grandfather baseline(ADR-060 Amd20 §7.9.D, monotonic shrink ratchet) 재사용 — 기존 위반을 new-only 로 흡수(발명 금지, AC-16).
- **(b) FM1-false-positive** = surgical scope + allowlist(inline 주석형 + 사유 필수, 파일밖 allowlist 는 만료·리뷰주기 필수, R4) + `SELF_EXCLUDE`(스캐너 자기 코드·fixture·생성 역색인 제외) — ADR-011 의 path-prefix 오판 재발 차단.
- **(c) FM2** = Phase 1(ADR) + Phase 2(script/workflow/registry/self-test) **동시 착지**(ADR-only 착지 금지) + evidence-checks-registry + ADR-151 inventory enroll + §결정 32.D surfacing.
- **(d) anti-hollow self-test dual** = `.sh`(ADR-151 enroll) + `.py`(ac-traceability Hop3 = `.py` AST) 양쪽 discriminating self-test(RED→GREEN + mutation-kill).
- **(e) FM3 = cross-repo subject durability**(최중요 — ADR-011/107 死因 직접 반박): D3 의 cross-repo subject = **live consumer 자원 선언**(durable, 실제 운영 자원이 존재하는 한 소멸 불가)이지, 모노레포 consolidation 으로 통합 가능한 mirror 가 아니다. ADR-011 은 cross-repo drift 를 *cross-repo 를 없애서*(모노레포 통합) 해결했으나 consumer(별도 저장소·별도 언어)는 그 탈출구를 못 쓴다 — D3 는 그 문제를 정면으로 푼다.
  - **(e) 실현도 정직(FIX-4)**: (e)는 **consumer 채택 시 활성**된다 — 현 wrapper-self Epic 은 (e)의 *실* cross-repo 대조를 행사하지 않는다(G5 는 mock-repo fixture 로 cross-repo **계약**만 검증, 실 consumer 자원선언 대조는 채택-bound, I-5). 따라서 "5축 봉인(누락=P0)"은 (a)~(d) + **(e-계약)** 을 뜻하며, (e)의 실 cross-repo 활성이 consumer 채택에 bound 됨을 정직 표기한다("완전 봉인" over-claim 회피).

### §결정 8 — honest-ceiling (정직 상한 — 은폐 금지, "완전 봉인" 표현 금지)

본 정책은 **정적 선언-대조 모델 class 의 업계 공통 상한**을 진다("green badge ≠ safety"). AC-13/AC-21 의 정직 천장을 공개한다:

- **(i) 프록시 위장(socat)**: 문자열은 로컬 `minio:9000` 이나 실제론 외부 NAS. 정적 diff 는 이름 일치만 본다 — 라우팅 실체 증명 불가(Terraform/OpenTofu 도 "unmanaged resource drift 미검출", 대응 = 런타임 관측/eBPF, OOS).
- **(ii) 자기신고 누락**: 실행단위가 required 를 신고 안 하면 대조 지점 자체가 없다 — 리뷰 의존(census-floor oracle 로 *과소선언*만 부분 검출).
- **(iii) 동적 env 키 구성 + 참조면 position 경계** (Amendment 1 정정 — CFP-2700 G2 FIX1 실측): 런타임 문자열 조합 키 = out-of-scope(불변). 단 "정적 리터럴 env key 참조 = **일괄** 결정가능·in-scope" 서술은 **과대**였다 — 정정: 결정가능성을 가르는 축은 static-vs-dynamic 이 아니라 **참조 position 이 infra 의미를 보증하는가**이다.
  - **in-scope (키 리터럴 position)**: 토큰이 *키 리터럴* 자리를 점유해 form 자체가 infra 의미를 보증하는 참조면 — namespace 한정(`secrets.X`) / 인용 키 리터럴(`os.environ["X"]`) / 선언 position(`*_env:`). 이 자리는 infra 키만 점유 가능하다. **실측 정밀도 = `scripts/**/*.py` 10/10 (100%)**.
  - **out-of-scope**: position 이 infra 의미를 보증하지 않는 참조면 → **(vi)**.
  - §1 의 "undecidable(크로스언어 전 프로그램 분석)" 과대일반화 정정은 **유지** — 지배적 실제 케이스(키 리터럴 position 의 정적 리터럴)는 결정 가능하며, 원 사고("collector 는 derived grep 0건")도 스캔이 cross-repo 로 돌았다면 grep 이 잡았을 사건이다(해당 면 = 키 리터럴 position 이라 in-scope, **재조명 무변경**).
- **(iv) 스캔 밖 표면**: secret manager · 외부 deploy 파이프라인 · 수동 운영 스크립트 — ADR-121 이 배포를 GitHub Environments 로 완전 위임했으므로 구조적·기수용된 사실.
- **(v) 기동 후 런타임 변조**: 정적 게이트 정의역 밖.
- **(vi) shell 변수읽기면** (Amendment 1 신설 — 실측 근거 공개): shell 의 `$VAR` / `${VAR}` / `${VAR:-}` 는 **범용 변수읽기 form** 이라 지역변수와 env 읽기가 어휘적으로 동일하다 — `secrets.` 같은 namespace 도, python 인용 키 리터럴 같은 position 도 shell 에는 존재하지 않는다. ∴ form 은 infra 의미를 전혀 보증하지 않으며, `_TOKEN|_KEY|_URL` suffix 휴리스틱만으로 infra 자원을 가려낼 수 없다.
  - **실측 (CFP-2700 G2 FIX1, `scripts/*.sh` 163 파일 전수)**: form 스캔 **11 hit 중 진성 2**(`GH_TOKEN` / `AUDIT_PII_KEY`), **오탐 9** — `STORY_KEY`×6 / `PAGE_TOKEN`(페이지네이션 커서) / `ISSUE_URL` / `NEW_TOKEN`(테스트 fixture) = **정밀도 약 18%**(교차 재확증 20%, 파일수 173 기준). naive bare 스캔(약 4%)과 같은 급 → §결정 7(b) FM1-false-positive 봉인 위반(만성 오탐 → bypass 상시화 = ADR-011 death mode 재현)이라 **미채택**.
  - **env-출처 판별로도 해소 불가**: `STORY_KEY="${STORY_KEY:-}"` 는 진성 env 유래이나 infra 자원이 아니다 — 격차의 실체는 **env 변수 ≠ infra 자원**이며, suffix 는 그 프록시일 뿐 shell 명명관행이 프록시를 압도한다.
  - **carve-in (in-scope)**: shell env-passthrough 자기참조형 `VAR="${VAR}" <cmd>` = 자식 프로세스 env 주입 **선언** position → 키 리터럴 position 등가. **실측 1 hit / 0 오탐(100%)**(`scripts/audit-trail-fetch.sh:71` `AUDIT_PII_KEY`).
  - **잔여 (정직)**: 그 외 shell env 읽기(`${GH_TOKEN:-}` 가드 등)는 **미검출**. 현 live blast radius = **0** — 실측 `orphan=0`, 선언 9 자원 **전건**이 workflow `secrets.` 참조면 보유(`SSH_KEY_PASSPHRASE`→`auto-deploy.yml` 등) → **false-orphan 은 잠재이지 live 아님**(orphan 로직도 vacuous 아님). 장래 "shell 로만 소비되는 신규 자원" 등장 시 false-orphan 발생 가능 = **기수용 리스크**.
  - **(vi) 는 PIN-NEGATIVE self-test 로 실행화한다** — 산문 ceiling 금지. shell 변수읽기 fixture(`STORY_KEY="${STORY_KEY:-}"` + `if [ -z "${GH_TOKEN:-}" ]`)가 **미검출**임을 단정하는 self-test 가 장래 naive form/bare 스캔 재도입을 RED 로 트립시킨다. 즉 본 천장은 집행되는 계약이지 선언이 아니다(§결정 7(d) discriminating self-test 정합, I-7 "선언 ≠ 배선" 자기적용).
- **(vii) cross-repo namespace = 승인 gate 아닌 fetch-대상 확정** (Amendment 2 신설 — G5 P1 F-CR-002): cross-repo fetch 는 **선언된 namespace 만** 순회하며(`_NS_RE` 가 shape/traversal 차단) 임의 repo 로 확산하지 않는다. 그러나 이는 **operator-approval allowlist 가 아니다** — manifest = semi-trusted **신뢰 declaration source**(§7.2)이므로 namespace 는 작성자가 선언한 fetch 대상이지 별도 승인 대상이 아니고, 같은 consumer-authored carrier 안의 "allowlist" 는 검사 대상과 동일 출처라 구조적 무기여(tautology)다. 실 안전은 3중 — `_NS_RE`(spoof/traversal) + loop-domain(선언 자원만 순회) + fetch-result fail-closed(미승인/오타 ns → 404 hard-fail, 오타-실재 repo → content-mismatch fail-closed). read-only fetch 이므로 blast radius = PAT 접근 가능 repo 의 read 1회. ∴ "namespace allowlist 로 임의 repo spoof 를 승인 차단" over-claim 금지 — **PIN self-test 로 집행**(loop-domain 밖 ns 는 애초 도달 불가 = allowlist 무용을 단언, spoof 차단은 `_NS_RE` 경로임을 assertion 문구로 정직 명명).
- **(viii) cross-repo ref-pin = moving-HEAD blocklist + non-SHA advisory (tag/SHA "강제" 아님)** (Amendment 2 신설 — G5 P1 F-CR-003): name-based ref 검사로는 tag 와 mutable branch 를 구분할 수 없으므로(SHA 만 `^[0-9a-f]{7,64}$` 판별) "pin 된 tag/SHA 만 대조 → idempotent" 는 집행 불가한 과대였다. 실 집행 = moving-HEAD 7-denylist hard-fail + 그 외 non-SHA ref WARN(비-SHA = idempotent 미보장). **엄밀 idempotency 는 SHA-pin 만 보장**하며 tag/mutable-branch pin 은 수용하되(설계가 tag 포함) WARN 으로 비-idempotent 리스크를 표면화한다. 잔여(정직): mutable branch 를 ref 로 pin 하면 재실행 간 verdict 가 뒤집힐 수 있다 = developer footgun(blast radius = manifest 저자 통제 하 nondeterministic verdict, low) = 기수용. **PIN self-test 로 집행** — mutable branch(`staging`) → WARN emit ∧ exit 0, SHA → WARN 무.
- **AC-21 honest-ceiling**: AC-21 은 "grep 가능한 미선언 표면" 만 검출한다. "collector 가 자원을 아예 미참조(grep 0건)" = undecidable ceiling — AC-21 이 완전해결을 over-claim 하지 않는다.
- **PAT read-write 정직**: §결정 4 의 `CODEFORGE_CROSS_REPO_PAT` 는 read-write 토큰이며 read-only 로 사용할 뿐임을 명시(false read-only claim 금지).

∴ "완전 보장 / 완전 봉인" hard-claim 금지 — "구조 fail-closed + 형식누락 저감 + 잔여 정직 공개" 로 재약속.

### §결정 9 — census born-red 해소 + D3 base scan corpus 완전 열거 (④ all-inert ⊃ ② examples/presets scan scope)

D3 self-test 의 census fail-closed(`candidates==0 ∧ inert==0 → born-hollow`, `check_path_relocation_consistency.py:752` 동형 재사용)를 만족시키려면 scan corpus 가 표면을 실제로 담아야 한다. 코드경로 falsify(verified): `:576 if old not in c.text: continue` → **inert 는 construct 가 자원명을 텍스트로 지목할 때만 증가**하므로 manifest 선언만으로는 inert 0. 따라서 D3 scan corpus 에 `examples/**` + `presets/**`(DATABASE_URL/REDIS_URL 등 실 표면)를 **포함**해야 inert>0(all-inert 도 non-vacuous PASS). ④ all-inert(predicate-gated) 단독 채택 불가 — **② examples/presets scan scope 를 필요조건으로 포함**한다. census 완화(③)는 ADR-136 Amd4 anti-hollow 충돌이라 비채택.

#### §결정 9.1 — D3 base scan corpus 완전 열거 (flagship AC live 대상 산재 통합, 누락 = wrapper-self 스캔 vacuous)

census 필요조건(examples/presets)만 열거하면 flagship AC-17/AC-22 의 live 대상(project.yaml 선언면 · workflow·scripts 소비면)이 base corpus 로 통합되지 않아, 구현자가 본 절만 보면 wrapper-self 스캔이 vacuous(inert 만 관측, live violation 대상 0)해질 수 있다. 이를 막기 위해 Phase 2 스캐너 `CORPUS_GLOBS`(§3.3) 는 **최소** 다음 base scan corpus 를 반드시 담는다:

| corpus 경로 | 표면 성격 | flagship AC | 분류축 |
|---|---|---|---|
| `.github/workflows/**` | secret 소비면(`secrets.CONFLUENCE_API_TOKEN` 등 9종) + `_env` 주입 | **AC-17 / AC-22** | **live violation 대상** |
| `.claude/_overlay/project.yaml` | `_env` 선언면(`api_token_env: ATLASSIAN_API_TOKEN`) + `infra_resources:` manifest 자체 | **AC-22 선언면** | **live violation 대상** |
| `scripts/**` **정적 env-key 리터럴 참조** | 예 `confluence_forward_sync.py:96` `SECRET_ENV_VARS` = `CONFLUENCE_API_TOKEN` 소비면(Story §4.0 named 소비면) | **AC-13**(정적 키 참조 = 결정가능·in-scope) | **live violation 대상** |
| `examples/**` + `presets/**` | census inert 표면(`DATABASE_URL` / `REDIS_URL` 등, wrapper-self manifest 미선언) | — | census-only **inert**(§결정 9.2) |

- **live 대상 3면**(workflows / project.yaml / scripts 정적 리터럴)이 없으면 wrapper-self 스캔이 census inert 만 관측 → flagship AC-22("선언면·소비면 둘 다 classified, zero-unclassified") 검증 subject 자체가 부재 → **self-ref 재범**(선언만 있고 대조 subject 없는 born-hollow). §결정 5 의 2계열(ATLASSIAN/CONFLUENCE) 대조도 이 3면이 corpus 에 있어야 성립한다.
- agent `.md` 펜스(D2 proto locus)는 §결정 2 reference-impl 정정 축이 소유하며 D3 scan corpus 에도 포함(Story §7.1 난제 5).
- **표 각주 — `scripts/**` 행의 in-scope 범위** (Amendment 1, CFP-2700 G2 FIX1): `scripts/**` 행은 확장자별로 비대칭이다 — **`.py` = 인용 키 리터럴(`os.environ["X"]` 등) 전면 in-scope**(실측 10/10 진성) / **`.sh` = env-passthrough form(`VAR="${VAR}" <cmd>`) 한정**. `.sh` 의 **변수읽기면(`${VAR:-}` 등)은 base corpus 에 속하나 검출 대상이 아니다** — 정밀도 약 18% 로 FM1 재현이라 의도적 미채택(§결정 8 (vi) 실측 SSOT). 이 비대칭을 표에 명시하지 않으면 구현자가 `scripts/**` 행을 "전 확장자 전면 스캔"으로 읽어 shell 오탐 extractor 를 재도입하게 된다.
- **over-reach 금지(honest-ceiling 정직, §결정 8 상속)**: 다음은 base corpus 가 **아니며** honest-ceiling 로 정직 공개한다 — consumer secret manager / out-of-repo 수동 운영 스크립트 / **동적 구성 env 키**(런타임 문자열 조립). base corpus = **repo-committed 정적 리터럴 참조만** in-scope(AST/grep 결정가능). "동적 구성 키까지 in-scope" 로 확대 서술 금지(§결정 8 (iii) 결정가능/불가 경계 정합).

#### §결정 9.2 — inert-classification predicate 명세 (census 관측 ≠ violation)

scan corpus 에 포함된 `examples/**`+`presets/**` 표면(wrapper-self manifest 미선언, 예 `DATABASE_URL`)이 **undeclared-violation 으로 flag 되면 wrapper-self born-red = Story 중심명제(born-red 회피) 자기부정**이다. 따라서 이들을 census-only **inert**(관측하되 violation 아님)로 분류하는 predicate 를 명시한다:

- **predicate**: 표면이 **비-실행단위 데모/템플릿 경로**(`examples/`·`presets/`)에 위치하면 그 표면은 `execution_unit` 이 아니므로 **required-자원 대조 대상이 아니다** → **inert**(census count 만 증가, violation 아님). `check_path_relocation_consistency.py:576`(`if old not in c.text: continue` → 자원명 텍스트 지목 시 후보 진입) + `:579-580`(`if not _is_active(c, active_when): inert += 1`) 의 inert 조건과 **동형** — 데모/템플릿 경로의 자원명 언급은 "지목되나 활성 대조 대상 아님" 이라 inert 로 흡수된다.
- **live 대비**: 대조적으로 `.github/workflows/**`·`.claude/_overlay/project.yaml`·`scripts/**` 정적 리터럴의 미선언 자원 참조 = **live violation 대상**(execution_unit 실 소비면 → required 대조 성립).
- **G2 구현자 지침**(요약): **examples/presets = census-only inert / .github/workflows + project.yaml + scripts 정적 리터럴 = live violation 대상**. inert>0 로 born-hollow 회피(④⊃②) + live 대상 3면으로 flagship AC 검증 subject 확보 — 둘 다 필요조건.

## 결과

### 긍정

- 인프라 자원 변경의 미전파가 **각 참조면에서 loud 검출**(부팅 거부 + CI drift red) — 지연 크래시 → 부팅 거부 목표 달성.
- wrapper-self 실 secret 표면(9종)이 실 스캔 대상(dogfood, none 위장 anti-hollow) — 게이트가 자기 자신에게 먼저 작동.
- cross-repo 축 In-scope 로 원 사고(별도 저장소 collector) 재발 검출 경로 확보.
- 死因 3-mode 5축 봉인 — ADR-011/107/096 3연속 미완 선례의 구조적 재현 차단.

### 부정 / 트레이드오프

- 신규 ADR + Epic 6-child 로 governance 표면 ↑(단 D1~D5 는 산재 규약의 중앙화 + drift-gate 프레임워크 재사용, 신규 발명 최소).
- honest-ceiling 5종 잔존 — 정적 선언-대조 class 의 구조적 상한(리뷰 의존 backstop 은 이 repo 이력상 최약).
- D2 미채택 consumer 미강제(I-5) — wrapper 계약이 consumer 런타임을 물리 강제하지 못함(채택-bounded).
- cross-repo fail-open(transient) — foreign flakiness 는 검출 못 하고 Issue 로만 표면화(ADR-011 death 회피 대가).

### 영향 경계

- consumer `.claude/_overlay/project.yaml`(자원 목록 author) · consumer 제품 startup 코드(D2 채택) · wrapper CI(D3 scan) · `docs/project-config-schema.md`(스키마 SSOT) · `ADR-060`(D3 tier host) · `ADR-003`(boundary-note).

## 해소 기준

N/A — permanent policy (`is_transitional: false`). 인프라 자원 선언 계약 + startup fail-closed invariant + drift-gate 는 영구 governance carrier. D3 의 warning→surfacing 승격은 ADR-060 §결정 6 promotion gate 소관(본 ADR 의 sunset 이 아님).

## 관련 파일

- `.claude/_overlay/project.yaml` — wrapper-self manifest carrier(`infra_resources:` block)
- `docs/project-config-schema.md` — `infra_resources` 스키마 SSOT(consumer/wrapper 공통)
- `scripts/lib/check_infra_resource_drift.py` + `scripts/check-infra-resource-drift.sh` — D3 scan(Phase 2)
- `.github/workflows/infra-resource-manifest-drift.yml` ≡ `templates/github-workflows/…`(byte-identical, ADR-005)
- `plugins/codeforge-test/agents/IntegrationTestAgent.md` — proto-D2 4중 결함 정정(D2 reference impl)
- `archive/adr/ADR-060-…` — D3 CI drift scan tier host(Amendment 23, 2 warning-tier entry)
- `archive/adr/ADR-003-…` — 정의역 경계 boundary-note Amendment
- `archive/adr/ADR-096-…` — manifest schema 패턴 재사용(disjoint 도메인)

## Amendment 1 (CFP-2700, 2026-07-17 KST) — 결정가능 경계 재획정: static-vs-dynamic → position-carried semantics (§결정 8 (iii) 교체 / (vi) 신설 / §결정 9.1 각주)

### 계기 — G2 구현리뷰 FIX1 실측이 원 서술을 반증

Phase 2(G2) 구현리뷰가 shell env 참조 FN class 를 제기했다: `_scan_script` 가 `_RE_QUOTED_TOKEN`(`[\"']([A-Z][A-Z0-9_]{2,64})[\"']`) 만 쓰므로 shell 의 `if [ -z "${GH_TOKEN:-}" ]` 는 따옴표 다음이 `$` 라 **영구 미매치** — `scripts/**` 가 §결정 9.1 LIVE glob 인데 `.sh` 면 기여가 **구조적 0**(firsthand 확증). 그런데 §결정 8 (iii) 은 "정적 리터럴 env key 참조 = 결정가능·in-scope" 로 선언하고 있었다 → **결정가능하다 선언해놓고 검출하지 않음** = 본 Epic 중심명제("선언 ≠ 배선", I-7)의 자기위반이자 §결정 8 은폐 금지 저촉.

처분 후보는 ① form-based shell extractor 신설(FN 봉쇄) ② honest-ceiling 공개(검출 포기) 였다. **양자 모두 실측 없이는 판정 불가**라 chief author 가 직접 측정했다(ADR-119 §결정 4 — verdict 는 proxy 아닌 ground-truth 로만 단정).

### 실측 (firsthand, 교차 재확증)

| extractor | corpus | hits | 진성 | 오탐 | 정밀도 |
|---|---|---|---|---|---|
| 현행 QUOTED on `.sh` | `scripts/*.sh` 163 | 0 | 0 | 0 | — (FN class 확증) |
| 후보 ① FORM on `.sh` | `scripts/*.sh` 163 | 11 | 2 | 9 | **약 18%** |
| carve-in passthrough on `.sh` | `scripts/*.sh` 163 | 1 | 1 | 0 | **100%** |
| 현행 QUOTED on `.py`(수용된 bar) | `scripts/**/*.py` | 10 | 10 | 0 | **100%** |

Orchestrator 교차 재확증(173 파일 기준) = 진성 2 / 오탐 3종 8건 / 약 20% — 동일 결론.

### 판정 — ① 기각(as-specified), ② + 좁은 carve-in 채택

- **① 기각**: "`${VAR}` 는 bare identifier 가 아니라 form 이므로 `secrets.X` 와 동일한 form-signal 특성" 이라는 전제가 **실측으로 반증**됐다. 구문상 form 인 것은 맞으나 **판별력이 없다** — shell 에서 `${X}` 는 범용 변수읽기라 지역변수·계산문자열·env 읽기가 어휘적으로 동일하다. FP 를 만드는 것은 bare 여부가 아니라 suffix 휴리스틱이며, shell 명명관행(`STORY_KEY` 등)이 그 프록시를 압도한다. 18% 는 §결정 7(b) FM1 봉인 정면 위반.
- **② 단독도 부정확**: shell 에 딱 하나 키 리터럴 position 등가(env-passthrough 자기참조형)가 존재하며 실측 100% 정밀도다. 이를 버리면 §결정 8 (iii) 이 in-scope 로 약속한 결정가능 표면을 **반대 방향으로 자기위반**(결정가능한데 out-of-scope 선언)한다.
- **∴ ② primary + 좁은 ① carve-in** — ceiling 은 진짜 잔여만 덮고, 결정가능한 form 은 배선한다.

### 정정된 boundary + 처분

1. **§결정 8 (iii) 교체** — 경계축을 static-vs-dynamic → **position-carried semantics** 로 재획정. in-scope = 키 리터럴 position(`secrets.X` / 인용 키 리터럴 / `*_env:`). 동적 구성 키 out-of-scope 및 §1 과대일반화 정정은 **무변경**(원 사고 재조명 유지 — 해당 면은 키 리터럴 position 이라 in-scope).
2. **§결정 8 (vi) 신설** — shell 변수읽기면 미검출을 실측 수치와 함께 정직 공개 + carve-in + 잔여(live blast radius 0, false-orphan 은 잠재) 명시 + **PIN-NEGATIVE self-test 로 실행화**.
3. **§결정 9.1 표 각주** — `scripts/**` 행의 `.py`/`.sh` 비대칭 명시(구현자 오독 차단).

### 검출 강도 방향 (무축소 확증)

본 Amendment 는 **검출을 줄이지 않는다** — `.py` 경로 무변경(100% 보존) + `.sh` 는 종전 구조적 0 → passthrough 1 표면 검출 **순증**. 줄어든 것은 *검출* 이 아니라 *허위 커버리지 주장* 이다(honest-ceiling ratchet-up). false-orphan 잠재 리스크는 은폐 대신 기수용으로 표기.

### 자기적용 (I-7 "선언 ≠ 배선")

본 Amendment 자신이 재범하지 않도록: (vi) 는 **산문 천장이 아니라 self-test 로 집행**된다(PIN-NEGATIVE = 재도입 시 RED, PIN-POSITIVE = carve-in 검출, 각 mutation-kill 동반). 본 §의 문구는 Phase 2 코드(`check_infra_resource_drift.py` docstring ★정직 천장 블록)와 **wording SSOT 일치 의무**(ADR-068 I-4) — 어느 한쪽만 갱신 = 설계리뷰 P0.

### 비대상 (경계 명시)

- **ADR-060 = 무변경**. `ADR-060:80`(Amd23 progress_note)의 baseline 기제 선언(`content_digest` / `monotonic shrink`)은 **정확**하며 prior art(`check_deferral_carrier_declared.py` baseline loader/digest)까지 명명하고 있다. 실측: `deferred-followup-baseline.yaml` 에 digest 필드 + `check_deferred_followup_reconcile.py:356-399` 에 재계산·비교 **실동작** 확인 → **과선언이 아니라 미구현**. 두 기제는 disjoint 위협을 각각 막는다(shrink = regen-to-absorb / digest = hand-edit-to-absorb, 상호 대체 불가). 처분 = **코드가 선언을 따라감**(Phase 2 구현 lane). 여기서 ADR 선언을 낮추면 "안 굴러가니 안 굴러간다고 적자" = 본 Epic 중심명제 자기부정.
- D1~D5 결정 / §결정 7 3-death 5축 봉인 / (i)~(v) 기존 천장 = 전부 무변경.

## Amendment 2 (CFP-2700 G5, 2026-07-17 KST) — cross-repo 통제 정직화: namespace allowlist tautology 제거 + ref-pin "tag/SHA 강제" 과대 정정 (§결정 4 ref-pin 교체 + namespace 정직 주 / §결정 8 (vii)(viii) 신설)

### 계기 — G5 구현리뷰가 §결정4 cross-repo 통제 2건의 "선언 ≠ 배선"을 반증

G5(`--cross-repo` 모드) 구현리뷰 P1 2건 (firsthand, ArchitectAgent 직접 판정 — 서브에이전트 미사용):

- **F-CR-002 (namespace allowlist tautology)**: `run_cross_repo` 가 `allowlist = {ns for r in cross}` 를 구성한 뒤 **같은 `cross`** 를 순회하며 `if ns not in allowlist` 로 검사한다 — allowlist 가 검사 대상과 동일 출처라 조건이 **항상 False(dead code)**. 실 spoof 차단은 `_NS_RE`(형식/traversal 검증)가 수행하며 allowlist 는 **무기여**(`../evil` 은 `_NS_RE` 의 anchored `[A-Za-z0-9]` 첫 문자에서 걸림). 그럼에도 code 주석·schema `namespace` 필드 서술("fetch allowlist 겸 ... 임의 repo spoof 금지")·census 출력(`allowlist_ns`)이 **없는 통제("operator 승인 allowlist")를 선전**했다.
- **F-CR-003 (ref-pin denylist ≠ tag/SHA 강제)**: ref-pin 은 `_MOVING_REFS` 7-entry denylist(`main/master/head/trunk/develop/default/latest`)만 거부한다. mutable 브랜치(`feature-x`/`staging`/`release/1.0`)는 `_CROSS_REF_RE` 통과 후 **수용(PASS)**. 그러나 §결정4·schema·code header 가 "pin 된 tag/SHA 를 대조 → idempotent" 로 서술 — **tag 와 branch 는 이름으로 구분 불가**(오직 SHA 만 `^[0-9a-f]{7,64}$` 패턴 판별)이므로 name-based denylist 로는 "tag/SHA 강제"를 **집행할 수 없다**. 엄밀 idempotency 는 SHA 만 보장(tag 도 재지정 가능).

두 건 모두 본 Epic 중심명제("선언 ≠ 배선", I-7)의 자기위반이자 §결정 8 은폐 금지 저촉 — "선언≠배선" 16번째 재범.

### threat model 재확인 (판정 입력)

manifest = **semi-trusted**(consumer/developer-authored, §7.2). namespace·ref 는 **manifest 유래**(공격자 주입 아님 — 작성자 선언). fetch = read-only(read-WRITE PAT 이나 contents fetch only). 양 리뷰어 + Orchestrator firsthand = **exploitable P0 부재** 확정. ∴ 두 통제는 **보안 경계가 아니라** ① namespace = fetch 대상 확정(정직) ② ref-pin = idempotency/재실행 결정성 축이다.

### 판정 — F-CR-002 → honesty-ceiling (dead allowlist 제거, 실 통제 정직 문서화)

operator-curated 별도 allowlist 신설(택일 a)은 **기각**한다:
- **동일 trust 도메인**: 별도 allowlist 를 두어도 carrier = 같은 consumer-authored `project.yaml`(§4b write boundary). 악의적 manifest 저자는 namespace 와 allowlist 를 **동시에** 쓸 수 있어 same-file allowlist 는 보안 분리를 제공하지 않는다(CODEOWNERS-gated 별 도메인이 아닌 한 무의미).
- **read-only + fetch-result 이미 fail-closed**: 잘못된/미승인 namespace 는 fetch 404 → hard-fail(exit 1), 오타-실재 repo 는 content-mismatch → fail-closed 로 **이미** 걸린다 → allowlist 는 중복 pre-check.
- **proposal-necessity gate(ADR-119 §결정9) 미충족**: 깨지지 않았고(공격 표면 아님) 이득<비용(governance 표면 + consumer 부담 순증). fake operator-approval 통제 추가 = 역방향 "선언 ≠ 배선".

∴ 실 통제를 정직 명명한다 — **fetch 도메인 = 선언된 namespace 집합(순회 대상 = manifest cross-repo 자원)** + **`_NS_RE` shape/traversal 차단** + **fetch-result fail-closed(404/content-mismatch)**. 별도 승인 gate 는 존재하지 않으며 manifest 신뢰모델상 불요. dead allowlist set·`ns not in allowlist` 검사·`allowlist_ns` census·"allowlist" 주석/schema/header 문구를 **전량 제거**(선전도 통제도 함께 제거 — 잔여 claim 0).

### 판정 — F-CR-003 → honesty-ceiling (moving-HEAD blocklist + non-SHA advisory, "tag/SHA 강제" 정정)

SHA-strict(택일 a)·gh-verify(택일 b) 모두 **기각**, honesty-ceiling(택일 c) 채택:
- **SHA-strict 기각**: `v1.2.3` 등 release tag 를 거부해 §결정4 설계 의도("tag/SHA")를 **반대 방향으로** 위반 + 기존 fixture(`PINNED_REF="v1.2.3"`) 파손. tag 는 인간 가독 pin 의 주 use-case.
- **gh-verify 기각**: ref 가 tag 임을 gh API 로 확인하면 ADR 정합이나 자원당 network round-trip 추가 → 중첩 failure-mode(tag-verify 자체가 transient?) + mock seam 복잡도 + latency. **보안 경계가 아닌 축에 과투자**.
- **honesty-ceiling 채택**: name-based tag/branch 구분 불가라는 **구조적 사실**을 인정. (1) moving-HEAD 7-denylist = **hard-fail 유지**(가장 흔한 footgun `main` pin 즉시 차단). (2) 그 외 **non-SHA ref = WARN**("비-SHA ref 는 idempotent 미보장 — mutable branch/재지정 tag 는 재실행 간 content 변동 가능") — hard-fail 시 tag 까지 거부되므로 WARN(surfacing)만. (3) **엄밀 idempotency 는 SHA-pin(`^[0-9a-f]{7,64}$`)만 보장**을 §결정4·§결정8·schema·header 에 명시. 잔여(mutable branch pin → 비-idempotent)는 developer footgun, WARN 으로 표면화, blast radius = manifest 저자 통제 하 nondeterministic verdict(low).

### 정정된 문구 (wording SSOT — ADR-068 I-4 3면 일괄)

1. **§결정4 ref-pin 교체** — "pin 된 tag/SHA 를 대조 → idempotent" → "moving-HEAD blocklist(hard-fail) + non-SHA advisory WARN; name-based tag/branch 구분 불가 ∴ 'tag/SHA 강제' 집행 불가, 엄밀 idempotency 는 SHA-pin 만 보장".
2. **§결정4 namespace 정직 주 신설** — "namespace = fetch 대상 확정(선언 ns 만 순회) + `_NS_RE` shape/traversal; 별도 operator-approval allowlist 없음(신뢰 declaration source, read-only fetch, same-domain allowlist 무의미)".
3. **§결정8 (vii)(viii) 신설** — 위 두 판정을 honest-ceiling 절 집행 항목으로 등재, **discriminating self-test 로 실행화**(산문 금지, §결정7(d) 정합).
4. code header/주석 + `docs/project-config-schema.md` §infra_resources `namespace`/`cross_repo_ref` 서술 = 위 문구와 byte-정합(구현 lane fixer 가 code, 본 ADR·schema 는 chief author 가 정합화).

### 검출 강도 방향 (무축소 확증)

- **F-CR-002**: allowlist 제거 = **검출 무변**(allowlist 는 애초 dead — 실 차단은 `_NS_RE`+loop-domain+fetch-result 로 100% 보존). 줄어든 것은 *허위 통제 주장*.
- **F-CR-003**: moving-HEAD hard-fail **유지** + non-SHA WARN **신설**(종전 침묵 수용 → surfacing 순증). 줄어든 것은 *"tag/SHA 강제" 허위 주장*. SHA-pin idempotency 보장은 무변.

### 자기적용 (I-7 "선언 ≠ 배선" — honesty-document 가 실 gap 을 덮지 않게)

본 Amendment 는 통제를 문서로 덮고 선전만 남기는 재범을 스스로 차단한다: (a) allowlist 는 **제거**(문서로 정당화한 뒤 존치가 아님) — 선전·dead code 동반 삭제. (b) ref-pin 정직 문구는 **self-test 로 집행** — non-SHA WARN PIN(mutable branch `staging` → WARN ∧ exit 0, SHA → WARN 무) + allowlist discrimination(loop-domain 밖 ns 도달 불가 = allowlist 무용 증명, 기존 `../evil` spoof test 는 `_NS_RE` 경로임을 assertion 문구로 정직 명명, 구 "allowlist 미등재" 문구 제거). (c) §결정4/§결정8 ↔ code header/주석 ↔ schema **3면 wording SSOT 일치 의무**(ADR-068 I-4) — 어느 하나만 갱신 = 설계리뷰 P0.

### 비대상 (경계 명시)

- **failure-mode 분리(content-mismatch=fail-closed / token 부재=degraded / transient=fail-open+Issue / 403·404=fail-closed) = 무변경**. 본 Amendment 는 namespace·ref-pin 2 통제 정직화만 — fetch 판정 로직·exit 계약·Issue audit trail 무손상.
- D1~D5 / §결정7 5축 봉인 / Amendment 1 (i)~(vi) 천장 = 전부 무변경.
