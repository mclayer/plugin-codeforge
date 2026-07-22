---
adr_number: 150
title: 런타임 DAST 보안 동적 축(§8.9) 신설 — oracle=attack ⊥ G4 robustness + presence/구조 fail-closed(검출력 천장 정직 공개)
status: Accepted
category: governance
date: 2026-07-12
carrier_story: CFP-2612
supersedes: []
related_adrs:
  - ADR-146  # 강 의존(landed) — 본 ADR = G4 burden-flip 표준(§8 preamble do-it-unless-proven-infeasible)의 보안 축 확장. 정직 천장 / consumer test.yml 러너 / 자연 N/A 3축 AND / 2-layer(Layer1 존재 default-FALSE ⊥ Layer2 per-change DO) 상속. Epic ⊥G5 = ADR-146 §결과 disjoint 목록의 cross-ref 확장(amend 아님). §8.9 독립 = §결정12 "next free number" 논리 상속. ★ ADR-146 amend/재사용 금지 — G5 carrier = 본 ADR-150 신규
  - ADR-145  # G1 정합만(amend/재사용 금지) — G5 AC 는 3-tier(normative/declared/advisory) + AC-ID sub-letter 문법(`ac_id.py` SSOT 공유)에 정합만. G1 게이트(AC↔§8↔실파일 zero-drop)와 G5 게이트(DAST applicability presence)는 disjoint
  - ADR-124  # 경계(지식층 ⊥ 실행층) — 보안 lane = 외부지식 3-단계 단계③(CVE·표준 다출처 검증 = 지식층) 주 발동. G5 DAST = 실행 층(앱 구동 재현) — 축 disjoint
  - ADR-048  # 강 의존(러너 + opt-in) — DAST 실 구동 = consumer `test.yml`(QADeveloperAgent). 신규 codeforge 러너 부활 금지(StatefulTest deprecated). `security_ai` opt-in ⊥ §8.9 presence mandate(비대칭 3-lane decouple)
  - ADR-001  # cross-ref(amend 아님) — 정적 워커(Claude/CodexReviewAgent)에 DAST 결과 = packet pointer 입력(trivy/hadolint additive 선례 동형, contract_version 무변경). review packet schema 확장 0
  - ADR-033  # SARIF fetch 재사용 — DAST(ZAP) 결과 = `code-scanning/alerts?tool_name=zap` fetch(trivy/hadolint SARIF 패턴 재사용, 신규 수집 채널 0). 1차 정적 container scan ⊥ DAST 동적 실행(축 disjoint, 상보)
  - ADR-119  # research-before-claims / 게이트=ground-truth — INV-G5-4 정직 천장: 게이트는 재현 시도·기록 presence/구조까지만, "취약점 실제 검출"은 강제 안 함(강제하는 척 = 검사연극)
  - ADR-060  # adequacy SSOT — G5 축 = 보안-adequacy(동적 보안 검증 충분성). "test liveness" 표현 금지(ADR-139/146 §결정4 어휘 가드 상속)
  - ADR-127  # no-exemption 자연 N/A 3축 AND — DAST 자연 N/A(공격 표면 부재) = skip 아님. 산출물 target 부재 ∧ downstream 무변경 ∧ 미래의무 무선결(3축 AND). Phase 2 runner-wiring 별 CFP defer = 축3 위반 → 동일 Story 유지
  - ADR-136  # execution-liveness 3요건(L1 blocking/L2 full-scope/L3 self-test) = §8.9 게이트 준수 상위 원리 + 2-layer applicability(정적 opt-in ⊥ 동적 per-change) 선례
  - ADR-005  # N/A 명시 패턴 — 자연 N/A substantive reason(≥30자) + §11 데이터 마이그레이션 N/A(wrapper-self governance, schema/data 무변경) 근거
  - ADR-068  # boundary invariant I-1~I-5 — deputy mandate boundary(chief tie-break ladder) + I-4 wording SSOT
  - ADR-133  # ADR-RESERVATION atomic claim — 본 ADR 번호(150) claim→write→row-append 3-step(claimant ArchitectPLAgent:CFP-2612, claim-state max 149→150 = concurrent CFP-2613 148·149 선점 후 max+1-avoidance)
  - ADR-013  # dogfood-out — 본 ADR = Story §7 설계 SSOT, Change Plan 병존(internal-docs `wrapper/change-plans/cfp-2612-g5-runtime-dast-security-axis.md`)
  - ADR-006  # §8 Test Contract authoring mechanism owner — §8.9 = SecurityArchitectAgent(위협 모델·공격 표면) + TestContractArchitectAgent(계약 필드) 공동 input, ArchitectAgent(chief) 통합. burden-flip §8 preamble(ADR-146) 하위 보안 로스터
related_concepts:
  - runtime-dast-security-axis
  - security-adequacy-presence-ceiling
is_transitional: false
---

# ADR-150 — 런타임 DAST 보안 동적 축(§8.9) 신설

## 상태

Accepted (2026-07-12 KST) — CFP-2612 (Epic CFP-2602 G5) carrier. "보안 테스트 레인이 전면 정적(코드 층 SAST 9축)이라, 실행 중에만 발동하는 취약점(런타임 injection·인증 우회·민감데이터 노출·설정 취약)이 조용히 미검증으로 남는" 병(보안-adequacy 갭)을 도메인 불변식 위반으로 재정의하고, 배포/기동한 애플리케이션을 실제 구동해 공격을 능동 재현·관측하는 **DAST(Dynamic Application Security Testing) 동적 축**을 §8 Test Contract 의 **독립 §8.9 로스터**로 신설하는 governance SSOT. G4(ADR-146) burden-flip 표준의 보안 축 instantiation — 강화(ratchet↑) 방향, 약화 surface 0(신규 required context 0, branch-protection 7-tuple 무변경, inter-plugin 계약 무변경). ADR-146 을 **cross-ref**하되 amend 하지 않는다(G5 = 신규 oracle 축 = 신규 ADR, §결정 1).

## 컨텍스트

사용자 원문(Story §1 verbatim): "codeforge 테스트 레인이 테스트 가능한 최대한의 동적 테스트를 수행하도록 강화한다"(2026-07-11 세션, 최광범위 승인). Epic CFP-2602(요건충족·산출물생존 강제) 확장 child, 게이트 G5 슬라이스 — G4(기능 동적 §8.8) 형제.

실측된 갭(요구사항 lane §4, origin/main 실측):

- **보안 lane 전면 정적**: SecurityTestPL 1차(Dependabot/CodeQL/Secret Scanning/trivy/hadolint fetch) + 2차 web CVE 검증 + 9축 정적 코드 리뷰 — **실행 중 공격 재현(DAST)·런타임 취약 관측 전무** [verified: `plugins/codeforge-review/agents/SecurityTestPLAgent.md`, `templates/review-checklists/security.md` 9축 category_enum]. 정적(SAST)은 소스를 실행하지 않고 취약 패턴을 찾고, 동적(DAST)은 앱을 실제로 띄워 바깥에서 공격을 흉내 내 실행 중 발동 여부를 관측한다 — 둘은 다른 것을 잡는다(SAST white-box 코드 층 ⊥ DAST black-box 실행 층, INV-G5-2) [source: [Black Duck SAST vs DAST](https://www.blackduck.com/blog/sast-vs-dast-difference.html), [Fortinet DAST glossary](https://www.fortinet.com/resources/cyberglossary/dynamic-application-security-testing)].
- **G4 §8.8 은 기능 oracle 만**: `check_section_8_8` 이 4기법 `{fuzz,property,load,concurrency}` 를 하드코딩 [verified: `scripts/lib/check_doc_section_schema.py` L361]. G4-fuzz 의 oracle = crash/invariant(기능 robustness). 보안 취약 재현(attack) oracle 은 §8.8 에 부재 — **DAST 를 §8.8 에 밀어 넣으면 landed·self-tested 게이트를 침습**(higher coupling).

도메인 불변식(Story §2.2, INV-G5):

- **INV-G5-1**(능동재현 default·침묵금지): 실행 중 취약 재현이 feasible 한 공격 표면이 있으면 default 로 능동 재현(DO), 미수행은 침묵이 아니라 정당화(`infeasibility_reason`)를 요구 — ADR-146 burden-flip 의 보안 축.
- **INV-G5-2**(SAST⊥DAST 상보 union): 정적·동적은 대체가 아니라 합집합 — DAST 는 런타임 구성·인증 우회·실행 injection 등 정적이 못 보는 것을 추가로 잡는다.
- **INV-G5-3**(blast-radius 격리): active payload 는 실제 공격이므로 로컬/ephemeral 환경에서만 재현, production·실 데이터 오염 금지 [source: [ZAP Baseline](https://www.zaproxy.org/docs/docker/baseline-scan/) — active scan 은 실제 공격 요청 생성, 권한 없는 대상 금지].
- **INV-G5-4**(정직 천장): 게이트는 재현 시도·기록을 강제할 수 있을 뿐, "취약점을 실제로 검출했음"은 강제할 수 없다(도달 못 한 endpoint 미검출·false-negative·비결정) — 강제하는 척 = 검사연극(ADR-119). G4 §8.8.5 정직 천장과 동형.

외부 근거(Story §6 재인용 — 신규 외부 단정 없음, 요구사항리뷰 lane 단계③ CONFIRMED): DAST black-box 성격 [source: [Fortinet DAST glossary](https://www.fortinet.com/resources/cyberglossary/dynamic-application-security-testing)] / OWASP ZAP 3종 GitHub Action — baseline(passive, CI 안전) / full-scan(active+passive, staging 전용, **수십 분 소요이나 비결정 — 규모·활성 규칙 수에 의존**) / api-scan [source: [ZAP Baseline](https://www.zaproxy.org/docs/docker/baseline-scan/), [ZAP Full Scan](https://www.zaproxy.org/docs/docker/full-scan/), [ZAP API Scan](https://www.zaproxy.org/docs/docker/api-scan/)] / DAST 한계 6종(false-positive·authenticated scan 난이도·coverage false-negative·비결정·destructive payload·scan time) → "수행 ≠ 취약점 부재 증명"(INV-G5-4 뒷받침) / CI DAST 성숙도 = OWASP DSOMM dynamic-depth **directional**(정적+동적 CI 통합 + severity threshold 파이프라인 fail 은 성숙한 방향 — bare Level 번호 인용 대신 방향적 표현) [source: [Wiz DSOMM](https://www.wiz.io/academy/application-security/devsecops-maturity-model-dsomm), [Spectral DSOMM](https://spectralops.io/blog/what-is-the-devsecops-maturity-model-dsomm/)].

## 결정

보안 테스트 레인에 런타임 DAST 동적 축을 §8 Test Contract 의 **독립 §8.9 로스터**(single `dast` axis)로 신설하되, 기계가 강제 가능한 것(applicability 레코드 + 산출물 계약 필드 presence/구조 + 2 cross-field 선언-정합)의 천장을 정직히 공개(no-hollow)한다. 착지 = template §8.9 + `check_section_8_9`(`check_section_8_8` verbatim 동형) + self-test + agent-md mandate(모두 Phase 2, 동일 Story). 결정 SSOT = 본 ADR / 파일 단위 배선 = Change Plan.

### 결정 1 — G4-fuzz ⟷ G5-DAST oracle 경계 명문화 (본 ADR 핵심 결정 + 신규 ADR 정당)

- **oracle 로 축을 가른다**: G4-fuzz 와 G5-DAST 는 **둘 다 fuzzing/능동 입력 주입을 쓸 수 있으나** 결함으로 보는 대상(oracle)이 다르다 — **G4-fuzz oracle = 기능 crash/invariant 위반(robustness)** ⊥ **G5-DAST oracle = 보안 취약 재현(attack — injection 실행·인증 우회·민감데이터 노출·설정 취약)**. 같은 도구를 써도 무엇을 결함으로 판정하는가가 disjoint. 이 경계 명문화가 본 ADR 의 핵심.
- **신규 ADR 정당(A2-5 판정 구조 — design.md:53 "신규 ADR 없이 기존 ADR 변경 금지" P0 방지)**: G5 의 security-attack oracle 은 G4 §8.8 의 functional-crash oracle 과 **다른 mechanism**이다. ADR-146 Amendment 로 착륙하려면 §8.8 의 4기법 하드코딩(`{fuzz,property,load,concurrency}`)에 5번째를 끼워야 하나, 그것은 (i) landed·self-tested `check_section_8_8` 침습 (ii) 기능 oracle 로스터에 보안 oracle 을 혼입(축 오염)이다. G5 는 (i) 독립 `check_section_8_9` fail-closed 게이트 + (ii) 독립 §8.9 doc-section 좌표 + (iii) 신규 2 cross-field 선언-정합 검사(§결정 4)를 도입하므로 별도 컨텍스트/결정/결과 블록이 중복이 아니다 → **신규 ADR-150** (ADR-146 = cross-ref, **amend 아님**).
- **agent-md DAST mandate = ADR-150 흡수**: TestContractArch/QADev/SecurityTestPL 가 §8.9 를 author/이행/종합하는 mandate(Phase 2)는 본 ADR 표준의 downstream binding 이지 ADR-146/ADR-006 의 새 항목이 아니다 → ADR-006 §결정 authoring mechanism 을 cross-ref 할 뿐 ADR-006/ADR-146 Amendment 를 발의하지 않는다.

### 결정 2 — §8.9 독립 single-`dast` 로스터 (§8.8 편입 아님, next-free 좌표)

- **§8.9 독립 신규 좌표**: §8.8(G4 fuzz/property/load/concurrency 점유) → 다음 자유 번호 §8.9(ADR-146 §결정12 "next free number" 논리 상속). §8.6 의도적 gap 은 무관 — doc-section lint 는 **헤딩 존재만으로 트리거**(§8.6 존재 전제 안 함, `check_section_8_5`/`_8_7`/`_8_8` 동형).
- **single `dast` axis(4-기법 loop 아님)**: §8.8 은 4기법 multi-key(`TECHNIQUE_8_8_META`)이나 §8.9 는 **DAST 단일 축 1행**(§8.9.0 applicability 표 = `dast` 1 row). 4-technique loop 구조를 복제하지 않는다 — DAST 는 하나의 실행-보안 검증 활동.
- **sub-section 좌표(§8.8 numbering rationale 동형)**: §8.9.0 applicability(1 dast row) · §8.9.1 dast DO 산출물 계약 본문 · **§8.9.2-4 의도적 gap**(§8.8 이 4기법용 §8.8.1-4 를 갖는 것과 positional homolog — DAST single-axis 라 2-4 비어 있음) · **§8.9.5 정직 천장**(§8.8.5 "N.5 = 천장" 좌표 정합) · §8.9.x aggregate-N/A(runtime code 0 Story).

### 결정 3 — 정직 천장 = presence/구조 fail-closed, 검출-forcing 아님 (INV-G5-4)

- **게이트는 applicability 레코드 + 산출물 계약 필드 presence/구조 + 2 cross-field 선언-정합(§결정 4)까지만 fail-closed**. 실 SARIF-nonempty / 실 앱-boot evidence 를 강제하지 **않는다** — 그것은 detection-forcing = 검사연극(ADR-119) + false-positive 유인(도달 못 한 endpoint·비결정 스캔을 "검출 실패"로 오판).
- **실 실행 evidence = declared/advisory tier**: 재현 시도 진술 충실성(수행했다면 실제 payload·관측 기록) = AC-3a declared(DesignReview/SecurityTestPL review) / false-negative·비결정 경보 = AC-3b/3c advisory. 게이트는 이들을 강제하지 않는다.
- **잔여 정직 공개(§8.9.5)**: (i) 검출력(실제 취약 검출) = 강제 안 함 (ii) 공격 표면 열거 완결성 = AC-1c review 미강제 (iii) infeasibility 사유 타당성 = AC-2d review 미강제 (iv) **`g_boundary_check` presence ≠ boundary 실준수**(token 존재가 경계 실준수 보장 아님). "완전 봉인" hard-claim 금지 — G4 §8.8.5 4잔여 공개 동형.

### 결정 4 — 2 cross-field 선언-정합 normative 검사 (declared-consistency, detection 아님)

기계적으로 clean 하게 강제하기 위해 참조 필드를 enum-constrain 한다: `payload_class ∈ {passive, active, destructive}` · `auth_mode ∈ {unauthenticated, session, token}` · `environment_ref` 는 explicit non-prod/ephemeral marker 보유. 두 fail-closed 검사:

- **(a) blast-radius (INV-G5-3)**: `payload_class ∈ {active, destructive}` ⟹ `environment_ref` 가 non-prod/ephemeral 을 assert. 실 active 공격을 production 대상으로 조용히 돌리는 것을 차단.
- **(b) authenticated 정합**: `attack_surface` authenticated ∧ `auth_mode = unauthenticated` ⟹ `infeasibility_reason` present. 인증 표면을 미인증 스캔으로 조용히 skip 해 false-negative 를 숨기는 것을 차단.

- **★ 천장 NON-violation(DesignReview P0 pre-empt)**: 두 검사는 **declared-consistency**(active payload 를 선언하면 격리도 선언하라 / 인증 표면을 skip 하면 정당화하라)를 강제할 뿐 **detection 을 강제하지 않는다** — INV-G5-4 / G3 경계를 넘지 않는다. "취약점을 실제로 검출했는가"는 여전히 어느 검사도 강제하지 않는다. 이는 §8.8 자신의 "mixed-case per-technique N/A substantive check"(순수 presence 를 넘는 substantive 검사)의 §8.9 ratchet-forward analog — pure-presence 를 넘되 detection-forcing 은 아님.

### 결정 5 — 실행 러너 = consumer test.yml(QADev) + opt-in 비대칭 3-lane decouple

- **DAST 실 구동 = consumer `test.yml`(또는 별도 `dast.yml`, QADeveloperAgent, ADR-048 CI-native 정합)**: (a) 앱 CI 기동(docker compose up / 로컬 바이너리) → (b) 스캐너(ZAP baseline/full/api-scan) 실행 → (c) 결과 파싱. 신규 codeforge 러너 부활 = ADR-048 재충돌 금지(StatefulTest deprecated 유지).
- **opt-in 비대칭 3-lane decouple**: ① §8.9 presence = **design-lane doc-section**(`security_ai` 와 무관 — 전 Story normative) ⊥ ② DAST 실 구동 = **consumer test.yml**(QADev) ⊥ ③ DAST 결과 AI-synthesis = **보안 lane**(`security_ai: true` opt-in). presence mandate ⊥ opt-in. **`security_ai` 를 꺼도 §8.9 presence 게이트는 비활성화되지 않는다**.
- **credential 조달**: `auth_mode`(unauthenticated/session/token) 의미. authenticated 스캔 세션·토큰 조달 = **consumer secret store**(real-user credential 재사용 금지). scan credential = Secret — 로그·SARIF 로 유출 금지(§7 credential 축).

### 결정 6 — inter-plugin 계약 변경 0 (RTM 이중소유 회피)

- **DAST 산출물 필드(target/oracle/payload_class 등)를 어떤 inter-plugin 계약에도 넣지 않는다** — template §8.9 + `check_section_8_9` 이 RTM 을 carry(§8.5/§8.7/§8.8 이 design-output 필드 추가 0 으로 착륙한 선례 동형). 계약에 DAST 필드 = RTM 이중 소유(design-output ∧ §8.9) → drift.
- **design-output-v2 / test-verdict-v2 / review-verdict-v4 무변경**. DAST 결과 → 정적 워커(Claude/CodexReviewAgent) packet = **pointer 입력**(SARIF 참조 링크, trivy/hadolint additive 선례 동형 — ADR-001 cross-ref, contract_version 무변경, packet schema 확장 0).

### 결정 7 — Epic 게이트 disjoint 확장 (G1⊥G2⊥G3⊥G4⊥G5)

- Epic CFP-2602 게이트 disjoint: **G1**(AC↔§8↔실파일 zero-drop, ADR-145) ⊥ **G2**(soak/restart/replay 런타임 지속 생존, ADR-148) ⊥ **G3**(discriminating 검출력) ⊥ **G4**(기능 동적 §8.8 로스터, robustness oracle, ADR-146) ⊥ **G5**(런타임 DAST §8.9 로스터, **attack oracle**, 본 ADR). 공유 = 원리("선언→실행, adequacy 강화", Epic #2346 계보)뿐. ADR-146 §결과 disjoint 목록을 ⊥G5 로 **cross-ref 확장**(ADR-146 amend 아님).
- **G2 경계 무침범**: soak/restart/replay = G2 단일소유(ADR-146 §결정3 g2_boundary_check / ADR-015). DAST 레코드 `g_boundary_check` = "soak(G2)·기능 fuzz(G4)로 넘어가지 않음"을 **dual G2∧G4 경계**로 확인(§결정 4 (iv) 천장: presence ≠ 실준수).

### 결정 8 — adequacy 어휘 가드 ("test liveness" 표현 금지)

- G5 축 명칭 = **"보안-adequacy(동적 보안 검증 충분성)"**(ADR-060 SSOT). **G5 문서 "test liveness" 표현 금지**(ADR-139/146 §결정4 어휘 가드 상속 — adequacy ⊥ liveness-orchestration(stall) ⊥ 지속-liveness-runtime(soak=G2) 3-sense 동음이의 차단). soak/생존 어휘는 G2 참조 맥락에서만.

### 결정 9 — 9축 DAST 매핑 = 기존 category_enum 정규화·심각도 승격 (신규 category 0)

- DAST 는 **신규 보안 category 를 만들지 않는다** — 기존 9축 category_enum(injection/trust-boundary/auth/credential/crypto/pii/dependency-cve/config/race)의 **런타임 거울면**으로 정적으로 의심된 항목을 실행 층에서 능동 재현·심각도 승격한다. 매핑:

| 9축 category | DAST 런타임 매핑 | 근거 |
|---|---|---|
| injection | **YES** | 정통 runtime mirror — SQLi/XSS/command injection 실 실행 재현 |
| auth | **YES** | 런타임 authn/authz 우회 능동 재현(broken access control) |
| config | **YES** | 열린 포트·기본 credential·헤더 misconfiguration 실행 관측 |
| pii | **YES** | 민감데이터 런타임 노출(응답 leak) 능동 재현 |
| trust-boundary | **PARTIAL** | wire-subset — 외부 HTTP 경계만(내부 프로세스 경계는 정적 축) |
| credential | **PARTIAL** | wire-subset — 전송 중 credential 노출만(저장 credential 은 Secret Scanning 정적 축) |
| crypto | **PARTIAL** | wire-subset — TLS/cipher negotiation 런타임 관측만(구현 정합은 정적) |
| dependency-cve | **NO** | SCA(Dependabot) 소관 — DAST 아님 |
| race | **NO** | G4 §8.8 concurrency(기능 robustness) 소관 — security-DAST 아님 |

- **security.md = DAST **pointer only****: category_enum UNCHANGED. `security.md` 는 §8.9(SSOT)를 가리키는 pointer sub-section 만 추가 — checklist 에 DAST 계약을 중복 기재하면 §8.9 ⊥ checklist drift → pointer 로 drift 회피.
- **DAST 기전 = STRIDE-lite / 러너 = 설계상 공격자**: wrapper-self runtime-inert 에서도 러너-as-attacker 가 곧 실 보안 축 — blast-radius(active payload = 실 공격) / credential(scan credential = Secret, MUST NOT log/SARIF-leak) / audit.

### 결정 10 — 게이트 배선 = check_section_8_9 EXTEND + §8.8 L355 단일 예외 + execution-liveness 3요건

- **`check_section_8_9` 신규 함수 추가**(`check_section_8_8` verbatim 동형) + `SECTION_8_9_*` 헤딩 regex + DAST 12 필드 list + 2 cross-field 검사 + `main()` 신규 `section_8_9_warns` list/call/print. **신규 workflow `.yml` 0 → 신규 required context 0**(기존 strict context `doc section schema (CFP-28 — strict)` 편승; branch-protection **7-tuple**[verified: origin/main CLAUDE.md — CFP-2603/ADR-145 가 `ac-traceability-matrix` 추가로 6→7] **무변경**).
- **★ §8.8 zero-touch 의 유일 예외(Refactor mandatory)**: `check_section_8_8` L355 region-slice regex `^###\s+\S` → `^#{1,4}\s+\S`. §8.8 의 g2-region 이 4-hash `#### §8.9` 형제에서 종료하게 해 §8.9 로 bleed 하지 않게 함. **현행 문서 동작 무변경**(5-hash `#####` subsection 은 `#{1,4}` 미매치, §8.9 신설 전 다음 1-4-hash 헤딩은 여전히 `### §9`). §8.8 코드 유일 touch — Phase 2 가 `test-check-doc-section-8-8.sh` 재구동으로 무회귀 증명.
- **execution-liveness 3요건(ADR-136 결정14, AND)**: (L1 blocking) 신규 함수가 기존 strict context 에 편승(동일 `sys.exit(1)`) → born-broken required 위험 0. (L2 full-scope) 단일 canonical `.py` — 신규 `.yml` 부재 → dual-copy 불요. (L3 self-tested) 신규 `tests/scripts/test-check-doc-section-8-9.sh` — TC(천장 실증: **0 검출 valid DAST 레코드도 PASS** — 게이트가 detection 미강제) + sed-mutation(MUT-A DO 필드 누락 / MUT-B g-token 누락 / MUT-D 잘못된 status enum / MUT-E infeasible 인데 reason 누락 / MUT-F active⟹prod-blocked / MUT-G authenticated+unauth⟹reason-required) + sibling-dependency guard + LIVE ceiling_honesty_check(실 template 대상, fixture-fallback 금지).
- **RTM location-resolution(G1 P1 재사용, amend 금지)**: 게이트는 authoritative 위치에서 §8 을 resolve — wrapper-self dogfood = Change Plan §8 / consumer Story = Story §8. G5 게이트는 이 규칙을 신설하지 않고 ADR-145 §결정6 을 인용.

## 대안 (기각 근거)

- **DAST 를 §8.8 5번째 기법으로 편입**: 기능 robustness oracle 로스터에 보안 attack oracle 혼입(축 오염) + landed `check_section_8_8` 4기법 하드코딩 침습 → 기각, §8.9 독립(§결정 2).
- **ADR-146 Amendment 로 착륙**: security-attack oracle = 새 mechanism + 신규 게이트/좌표/cross-field 검사 → 별도 컨텍스트/결정/결과 블록 필요 → 기각, 신규 ADR-150(§결정 1, A2-5 구조).
- **execution-forcing 천장(실 SARIF-nonempty/앱-boot 강제)**: detection-forcing = 검사연극 + false-positive 유인(도달 못 한 endpoint·비결정) → 기각, presence/구조 fail-closed(§결정 3, INV-G5-4).
- **신규 보안 category 신설**: DAST = 기존 9축의 런타임 거울면(신규 취약 종류 아님) + checklist 중복 = drift → 기각, category_enum 무변경 + pointer only(§결정 9).
- **신규 required workflow context(7→8-tuple)**: presence/구조 doc-lint 는 기존 strict context 로 충분 → 기각, `check_section_8_9` EXTEND(§결정 10).
- **DAST 필드 계약 반영**: RTM 이중 소유(design-output ∧ §8.9) drift → 기각, ZERO contract change + packet pointer(§결정 6).
- **신규 codeforge DAST 러너 부활**: ADR-048 재충돌(StatefulTest deprecated) → 기각, consumer test.yml(§결정 5).
- **§8.9 presence 를 `security_ai` opt-in 에 결속**: opt-off consumer 가 DAST 선언 자체를 skip → adequacy 갭 재발 → 기각, 3-lane decouple(§결정 5).

## 결과

- feasible 한 런타임 공격 표면이 있는데 DAST 가 침묵 누락되면 §8.9 게이트가 구조적으로 차단(applicability 레코드 + 산출물 계약 필드 + 2 cross-field 선언-정합 presence fail-closed). 검출력·열거 완결성·사유 타당성은 AC review + advisory + G3 로 defense-in-depth(강제 금지).
- 형식누락·rot 저감 + 검출력·완결성·사유타당성·g-boundary-준수 4 잔여 정직 공개 = ADR-119/ADR-146 §8.8.5 정합(검사연극 회피). 2 cross-field 는 declared-consistency 만 강제(detection 미강제) — INV-G5-4 무침범.
- Epic CFP-2602 게이트 disjoint 확장: **G1⊥G2⊥G3⊥G4⊥G5**. G5 = 런타임 DAST(attack oracle) 축 — G4-fuzz(robustness oracle)와 oracle 로 disjoint.
- 약화 surface 0: 신규 required context 0, branch-protection 7-tuple 무변경, inter-plugin 계약 무변경, 신규 보안 category 0. §8.8 코드 유일 touch = L355 region-slice(현행 동작 무변경). sunset_justification = N/A(permanent governance ratchet, ADR-058 §결정 5 강화 방향).
- **wrapper-self dogfood**: codeforge 자체 = deployable service 0(runtime-inert) → 본 Story 의 §8.9 = 자연 N/A(레코드 schema + 정당화만 의무, 실 구동 면제). 실 DAST 구동 = consumer(예: mctrader-web HTTP API) test.yml. Phase 2 정량 파라미터(scan budget/duration)는 `[empirical-source: consumer test.yml, Phase 2]` defer(추정값 lock-in 아님).

## 관련 파일

- Story: `<internal-docs>/wrapper/stories/CFP-2612.md` (§7 설계 서사 / §3 ADR-150 확정)
- Change Plan: `<internal-docs>/wrapper/change-plans/cfp-2612-g5-runtime-dast-security-axis.md`
- 수정(Phase 2): `plugins/codeforge-design/templates/change-plan.md`(§8.9 로스터) · `templates/story-page-structure.md`(§8.9 미러) · `scripts/lib/check_doc_section_schema.py`(`check_section_8_9` 신규 + §8.8 L355 region-slice 유일 예외) · `plugins/codeforge-review/templates/review-checklists/security.md`(DAST pointer sub-section, category_enum 무변경) · `plugins/codeforge-review/agents/SecurityTestPLAgent.md`(DAST 결과 fetch/종합 절) · `plugins/codeforge-design/agents/TestContractArchitectAgent.md`(§8.9 계약 mandate) · `plugins/codeforge-develop/agents/QADeveloperAgent.md`(consumer test.yml DAST 배선 mandate)
- 신규(Phase 2): `tests/scripts/test-check-doc-section-8-9.sh`(L3 discriminating self-test — 천장 실증 + 6 mutation + LIVE ceiling_honesty_check)
- Phase 1: `docs/architecture/codeforge-family.md`(data_flow 1-line + Open Decisions row)
- 선례: `scripts/lib/check_doc_section_schema.py` `check_section_8_8`(clone source — CFP-2605/ADR-146) · `tests/scripts/test-check-doc-section-8-8.sh`(self-test 선례) · ADR-146(G4 sibling — burden-flip 표준·정직 천장·Phase 1/2 분리·2-layer) · ADR-145(G1 sibling — 3-tier AC + RTM location-resolution)
