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

`ADR-003`(SSOT drift 3 layer: CI invariant / SessionStart 부트스트랩 / 사용자 가이드)의 정의역은 **codeforge 자신의 self-SSOT 정합**이다(대표 산출물 3종 = `invariant-check.yml` / `check-bootstrap.sh` / `consumer-guide.md` 전부 codeforge 실행물). 본 정책의 D2(**consumer 제품 런타임의 부팅 fail-closed**)는 codeforge 가 아니라 consumer 제품 바이너리가 실행하는 invariant 로, ADR-003 §결정 2 Q1 의 3-bucket(plugin repo 내부 / consumer 환경=GitHub label·org-perm / 1회 setup) 어디에도 들어가지 않는다(§결정 3 상술). ADR-003 §대안 D 는 4번째 layer 가 필요한 *기제*("본 ADR supersede 또는 amend")를 주지만, D2 는 그 self-SSOT 도메인 밖이라 4th layer 가 아니라 **별 정의역의 신규 ADR** 이 옳다. ADR-003 에는 오귀속 방지 boundary-note 만 Amendment 로 남긴다.

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

원 사고의 미탐지 지점이 별 저장소·별 언어(Rust collector)였고, per-repo manifest 는 Pact broker 구조가 아니라 저장소 경계 전파를 못 한다. 따라서 cross-repo 대조를 **In-scope 정식 요건**으로 편입한다(OOS 분기 제거). 단 "본 정책은 전파를 *수행*하지 않는다 — 미전파를 각 참조면에서 loud 하게 *검출*할 뿐"임을 명시(green ≠ 전파 완료, riftmap "worse than no graph" 회피).

- **credential**: `CODEFORGE_CROSS_REPO_PAT` 재사용(ac-traceability-matrix.yml:65 선례, 23 workflow 사용중) — 신규 credential 도입 아님. **정직 주의(SecurityArch P0)**: 이 PAT 는 **read-only 토큰이 아니다**(실토큰 = classic `repo`+`workflow` read-WRITE no-expiration, ADR-066 Amd5). D3 는 이 토큰을 **read-only 로 *사용*(contents fetch only)** 할 뿐이며, "read-only PAT" 라고 서술하지 않는다(workflow yml 주석의 "read-only" 표기도 사용 방식이지 토큰 권한이 아님).
- **자원 ID cross-repo 네임스페이스**: top-level `namespace:` 필드 + cross-repo 참조 시 `<ns>/<id>` fully-qualified. cross-repo 참조만 fq 필수(§3.5 ADR-044 동형 충돌 회피 — 자원 ID `raw-nas` 도 repo 경계를 넘으면 ADR 번호 cross-repo 충돌과 동형 충돌을 낳는다).
- **failure-mode 분리(InfraOp 핵심 — flaky 타repo 가 본 repo CI 상시 red 회피, ADR-011 death 재현 차단)**:
  - fetch-success + content-mismatch = **DRIFT → fail-closed**(non-zero).
  - **token 부재(우리 misconfig) = degraded FAIL**(AC-21 유지 — main-path degrade 재사용 금지).
  - **foreign-repo transient unavailable(503 / network / timeout) = fail-OPEN + loud warning + Issue 발행**(타 repo 의 flakiness 가 본 repo 게이트를 상시 red 로 만드는 것 = ADR-011 death 재현이므로 회피).
  - foreign 403 / 404 = `resp.ok` 확인 후 판정(ADR-145 §결정 4 conflation 가드).
- **ref-pin(InfraOp + idempotency)**: 타 repo 의 moving main HEAD 가 아니라 manifest 에 pin 된 tag/SHA 를 대조 → moving-target-red 방지 + 재실행 결정성(§11 idempotency).

### §결정 5 — DEC-3 alias-model 수렴 (canonical = `ATLASSIAN_API_TOKEN`, live rename 안 함)

wrapper Confluence 자격증명 2계열을 **alias-model 로 수렴**한다(라이브 secret rename 하지 않음 — rotation-adjacent risk 회피, 물리 rename = OOS follow-up):

- **canonical = `ATLASSIAN_API_TOKEN`**, **accepted alias = `CONFLUENCE_API_TOKEN`**.
- 근거(정정된 rationale — Mapper 반증 반영): canonical 이 ATLASSIAN 인 이유 = **Atlassian-account-scoped blast-radius 를 정직하게 명명**(CONFLUENCE 명은 blast-radius 과소표현). "Jira 공용" 근거는 **폐기**(Jira 는 무-secret session OAuth, 토큰 미사용).
- 2-channel(MCP-session PRIMARY / CI-fallback ALTERNATIVE)은 **의도적**(confluence-forward-sync.yml:8-13 documented). manifest 가 canonical 1 + accepted alias 를 선언하면 선언면(project.yaml)·소비면(workflow) 둘 다 classified → D3 재스캔 zero-unclassified(AC-22). "canonical 1 + alias N 수렴" 이면 물리 rename 없이 충족.

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
- **(e) FM3 = cross-repo subject durability**(최중요 — ADR-011/107 死因 직접 반박): D3 의 cross-repo subject = **live consumer 자원 선언**(durable, 실제 운영 자원이 존재하는 한 소멸 불가)이지, 모노레포 consolidation 으로 통합 가능한 mirror 가 아니다. ADR-011 은 cross-repo drift 를 *cross-repo 를 없애서*(모노레포 통합) 해결했으나 consumer(별 저장소·별 언어)는 그 탈출구를 못 쓴다 — D3 는 그 문제를 정면으로 푼다.

### §결정 8 — honest-ceiling (정직 상한 — 은폐 금지, "완전 봉인" 표현 금지)

본 정책은 **정적 선언-대조 모델 class 의 업계 공통 상한**을 진다("green badge ≠ safety"). AC-13/AC-21 의 정직 천장을 공개한다:

- **(i) 프록시 위장(socat)**: 문자열은 로컬 `minio:9000` 이나 실제론 외부 NAS. 정적 diff 는 이름 일치만 본다 — 라우팅 실체 증명 불가(Terraform/OpenTofu 도 "unmanaged resource drift 미검출", 대응 = 런타임 관측/eBPF, OOS).
- **(ii) 자기신고 누락**: 실행단위가 required 를 신고 안 하면 대조 지점 자체가 없다 — 리뷰 의존(census-floor oracle 로 *과소선언*만 부분 검출).
- **(iii) 동적 env 키 구성**: 런타임 문자열 조합 키 = out-of-scope. **결정가능/불가 경계 정직화**: "정적 리터럴 env key 참조 = 결정가능·in-scope(AST/grep) / 동적 구성 키 = out-of-scope". §1 의 "undecidable(크로스언어 전 프로그램 분석)" 과대일반화를 정정 — 지배적 실제 케이스(정적 리터럴)는 결정 가능하며, 원 사고("collector 는 derived grep 0건")도 스캔이 cross-repo 로 돌았다면 grep 이 잡았을 사건이다.
- **(iv) 스캔 밖 표면**: secret manager · 외부 deploy 파이프라인 · 수동 운영 스크립트 — ADR-121 이 배포를 GitHub Environments 로 완전 위임했으므로 구조적·기수용된 사실.
- **(v) 기동 후 런타임 변조**: 정적 게이트 정의역 밖.
- **AC-21 honest-ceiling**: AC-21 은 "grep 가능한 미선언 표면" 만 검출한다. "collector 가 자원을 아예 미참조(grep 0건)" = undecidable ceiling — AC-21 이 완전해결을 over-claim 하지 않는다.
- **PAT read-write 정직**: §결정 4 의 `CODEFORGE_CROSS_REPO_PAT` 는 read-write 토큰이며 read-only 로 사용할 뿐임을 명시(false read-only claim 금지).

∴ "완전 보장 / 완전 봉인" hard-claim 금지 — "구조 fail-closed + 형식누락 저감 + 잔여 정직 공개" 로 재약속.

### §결정 9 — census born-red 해소 (④ all-inert ⊃ ② examples/presets scan scope)

D3 self-test 의 census fail-closed(`candidates==0 ∧ inert==0 → born-hollow`, `check_path_relocation_consistency.py:752` 동형 재사용)를 만족시키려면 scan corpus 가 표면을 실제로 담아야 한다. 코드경로 falsify(verified): `:576 if old not in c.text: continue` → **inert 는 construct 가 자원명을 텍스트로 지목할 때만 증가**하므로 manifest 선언만으로는 inert 0. 따라서 D3 scan corpus 에 `examples/**` + `presets/**`(DATABASE_URL/REDIS_URL 등 실 표면)를 **포함**해야 inert>0(all-inert 도 non-vacuous PASS). ④ all-inert(predicate-gated) 단독 채택 불가 — **② examples/presets scan scope 를 필요조건으로 포함**한다. census 완화(③)는 ADR-136 Amd4 anti-hollow 충돌이라 비채택.

## 결과

### 긍정

- 인프라 자원 변경의 미전파가 **각 참조면에서 loud 검출**(부팅 거부 + CI drift red) — 지연 크래시 → 부팅 거부 목표 달성.
- wrapper-self 실 secret 표면(9종)이 실 스캔 대상(dogfood, none 위장 anti-hollow) — 게이트가 자기 자신에게 먼저 작동.
- cross-repo 축 In-scope 로 원 사고(별 저장소 collector) 재발 검출 경로 확보.
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
