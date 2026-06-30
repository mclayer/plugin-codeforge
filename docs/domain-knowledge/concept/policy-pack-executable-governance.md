---
kind: concept_definition
type: domain-knowledge
slug: policy-pack-executable-governance
title: Policy-pack executable governance (재사용 거버넌스 규칙을 읽고추정 아닌 실행검사로 묶는 패턴 + 자격 curation 기준)
status: Active
updated: 2026-06-30
carrier_story: CFP-2480
related_adrs:
  - ADR-119  # research-before-claims Amd 2 — 게이트 verdict 를 outcome ground-truth 로만 단정 (정책 실행 결과 anchor)
  - ADR-037  # plugin version-bump rule — 정책팩 첫 멤버 게이트 (게이트 자체 무변경, 실행 방식만 추가 — Amendment 4)
  - ADR-092  # changelog SSOT location — wrapper CHANGELOG 동결 (§결정 3) → changelog 게이트 policy_pack_scope 분기 근거
  - ADR-060  # evidence-enforceable promotion framework — 정책팩 멤버십 SSOT (evidence-checks-registry policy_pack_member field)
  - ADR-070  # Codex verify-before-trust — 정책 실행 결과도 신호원 → PL 재실행 falsify 후 채택 (Amendment 12 review-lane execution scope 일반화)
  - ADR-052  # Codex proactive Touchpoint — Codex=신호원 dual-peer trigger origin (정책 실행 dispatch 재사용, 새 touchpoint 신설 아님)
related_concepts:
  - execution-based-review-verification        # E1 (CFP-2477) — 본 개념의 일반 mechanism base. policy-pack = 그 specialization (curated membership). Popper/discriminating/flaky/sandbox/신호원 SSOT
  - merge-time-adversarial-verification-gate   # Story A (CFP-2458) — review-of-output mechanism. disposition SSOT 패턴 동형
  - mutation-based-hollow-gate-detection       # Story B (CFP-2464) — probe-the-detector mechanism. undetermined 3-상태 disposition 재사용
tags:
  - policy-as-code
  - executable-governance
  - reusable-governance-rule
  - membership-curation
  - deterministic-evaluable
  - incident-driven
  - config-and-behavioral
  - dead-gate-roi
  - execute-the-gate
sources:
  - https://www.openpolicyagent.org/docs/cicd                                                          # Policy-as-Code (PaC) — 거버넌스 규칙을 deterministic·machine-evaluable 코드로 정의, --fail/--fail-defined exit 1 = CI 중단
  - https://platformengineering.org/blog/policy-as-code                                                 # PaC 자격 curation 기준 — deterministic·machine-evaluable / "Start with policies that prevent actual incidents" / stable 규칙만 자동화; business judgment 류는 manual 유지
  - https://tag-security.cncf.io/community/resources/automated-governance-maturity-model/               # CNCF Automated Governance Maturity Model — 4-category(Policy/Evaluation/Enforcement/Audit), "configuration and behavioral" 둘 다 + ROI 재평가 후 통제 제거
---

## 정의

**Policy-pack executable governance** = 재사용 거버넌스 규칙(version-bump·migration·ADR 완결성 등)을 리뷰/머지 시점에 *읽고 추정* 하는 대신 Codex/lane worker 가 **해당 게이트를 실제 실행** 해 그 실행 결과(exit code + stdout)를 PR/Story 단정·정책 invariant 와 대조하고 위반을 finding 으로 보고하는 검사 묶음. "팩(pack)" = 어떤 규칙이 이 묶음에 속하는가의 **멤버십 집합** 이다 — 즉 본 개념의 1급 산출물은 실행 mechanism 이 아니라 *멤버십 curation 기준* 이다.

이는 산업 **Policy-as-Code (PaC)** — 거버넌스 규칙을 버전관리 코드로 정의해 자동 집행하며 규칙은 declarative·deterministic·machine-evaluable 해야 한다 (출처: openpolicyagent.org/docs/cicd) — 의 codeforge dogfood instantiation 이다. PaC 도구(OPA/Conftest)는 `--fail`/`--fail-defined` 로 위반 시 exit 1 → CI 중단(정책을 unit test 처럼 실행)한다 (출처: openpolicyagent.org/docs/cicd).

## 컨텍스트

CFP-2480 (Epic CFP-2476 의 E3) 동인 = CFP-2457 dogfood 사실 — 정적 diff 읽기(Claude peer + PL)가 놓친 ADR-037 version-bump P0(MINOR under-bump)를 Codex 의 *실 게이트 직접 실행* 만이 포착했다 [verified: project_cfp_2457 memory; 본 결론은 내부 dogfood 근거로 1차 정박]. 즉 "재사용 거버넌스 규칙은 실행돼야 잡힌다" 가 본 개념의 firsthand 동인.

### E1 specialization 으로서의 위치 (핵심 구분)

본 개념은 **E1 `execution-based-review-verification`(execute-the-gate 일반 mechanism)의 specialization 둘 중 하나** 다 (다른 하나 = `fix-ground-truth-replay`). 직교성:

| 개념 | mechanism | 무엇을 실행하나 |
|---|---|---|
| E1 execution-based-review-verification | execute-the-gate (일반) | PR touch 한 *임의 discriminating check* 실행 |
| **E3 policy-pack-executable-governance (본 개념)** | **execute-the-gate (curated membership)** | *재사용 거버넌스 규칙의 큐레이션된 집합* 실행 |

E1 = mechanism / E3 = curated membership. E1 이 "어떤 게이트든 실행해 단정과 대조한다" 를 정립했다면, E3 는 "어느 규칙이 이 묶음에 들 자격이 있는가" 의 curation 기준을 정립한다. **중복 정립 금지** — Popper 비대칭, discriminating check 우선, flaky quarantine, deterministic seeding, read-only sandbox, Codex=신호원은 모두 E1 concept(`execution-based-review-verification.md` X-1~X-6)이 SSOT 이고 본 개념은 참조만 한다.

## 핵심 규칙 (외부 개념 → invariant 매핑)

### P-1: 정책팩 멤버십 자격 기준 = deterministic·incident-driven·stable

모든 거버넌스 게이트가 정책팩 멤버는 아니다. 자동화 대상 자격 = (a) **deterministic·machine-evaluable** — human judgment 없이 일관·반복 verdict 를 내는 규칙만 (출처: platformengineering.org/blog/policy-as-code) , (b) **반복 incident 방지** — "Start with policies that prevent actual incidents" (출처: platformengineering.org/blog/policy-as-code) , (c) **stable** — 주 단위로 바뀌지 않는 규칙. business justification·architectural trade-off·exception 류는 manual 유지(pack 제외).

**함의 — §1 4 후보의 자격 비균질**: version-bump(deterministic·CFP-2457 incident·stable) = A급. migration·ADR 완결성 = 구조 검사로 deterministic 화 가능. changelog = ADR-092 동결로 tier 분기(P-2). E1 X-2 discriminating-check 우선과 정합 — 통과만 하는 hollow check 는 실행해도 yield 0(verify 불가, Popper 비대칭은 E1 X-1 SSOT).

### P-2: enforcement tier = 자격 기준 ⊕ 조직 결정 (changelog scope 분기)

멤버의 enforcement tier(warning/blocking)와 적용 scope 는 자격 기준(P-1)만으로 결정되지 않는다 — **조직 결정(내부 ADR 사실)이 ⊕ 로 합성** 된다. 대표 사례 = changelog: 외부 PaC 자격 기준상 검토 대상이나 ADR-092 §결정 3 이 wrapper 루트 CHANGELOG 를 **동결**(`archive/CHANGELOG-legacy.md` 보존, 신규 entry 금지)했으므로 changelog 게이트를 wrapper PR 에 적용하면 항상 false-RED 다. 따라서 changelog 멤버십의 `policy_pack_scope` = **lane-plugin / consumer 한정** (wrapper 제외).

**함의**: 멤버십 SSOT 는 멤버 boolean(`policy_pack_member`)만이 아니라 scope(`policy_pack_scope`)를 동반해야 한다 — scope 부재 시 동결된 영역에 cry-wolf. 멤버십 SSOT = `docs/evidence-checks-registry.yaml` optional field (ADR-060 framework, 신규 manifest 회피).

### P-3: verdict = exit-code 결정론 + machine-readable 위반 리포트

각 멤버 게이트의 verdict 는 **exit-code 기반 결정론** 이어야 한다 — PaC 의 `--fail` exit 1 모델(출처: openpolicyagent.org/docs/cicd) 정합. disposition 어휘는 **deny(차단)/warn(경고) 2-tier** 가 산업 reference(Conftest)이나 cross-industry 단일 표준은 부재 [hypothesis: 외부 다출처 표준 미확인] — 따라서 **신규 disposition 표준 정립 불필요**, E1 disposition + 기존 evidence-checks-registry 4-tier enum(warning/blocking-on-pr/blocking-on-merge/hotfix-bypass)으로 충분.

**함의**: 실행 결과는 재현 가능한 객관 사실이나 그 자체가 자동 신뢰 대상은 아니다(P-6). exit code(primary) + stdout(semantic body) 가 finding 구조의 evidence — E1 X-1 상 실행 GREEN 은 "PR 옳음" 증명이 아니라 falsify 도구일 뿐.

### P-4: 정책팩 대상 = config 검사 ∪ behavioral 검사 둘 다

CNCF Automated Governance Maturity Model 은 자동화 대상이 "both configuration and behavioral elements" 를 포함하고 각 check 가 machine-readable verdict + audit artifact 를 내야 한다고 본다 (출처: tag-security.cncf.io/community/resources/automated-governance-maturity-model/). 즉 정책팩은 정적 존재 검사(config: version 필드 존재)뿐 아니라 실행 검증(behavioral: bump 규칙 위반 시 RED)까지 포괄한다 — E1 execute-the-gate 정합.

### P-5: ROI 죽은 게이트 제거 (hollow-gate 동형)

CNCF 모델은 통제를 ROI 재평가 후 제거한다 (출처: tag-security.cncf.io/community/resources/automated-governance-maturity-model/). 정책팩 멤버십은 append-only 가 아니라 cry-wolf·죽은 게이트(늘 GREEN hollow check)를 멤버에서 제외하는 curation 의무를 포함한다. 이는 Story B `mutation-based-hollow-gate-detection`(detector adequacy 검사)과 상보 — B 가 detector 의 discriminating power 를 검사한다면, 정책팩은 discriminating 한 게이트만 멤버로 큐레이션한다.

### P-6: Codex = 신호원, 정책 실행 결과도 PL 재실행 falsify 후 채택 (E1 상속)

정책 실행 결과조차 자동 채택 금지 — flaky·환경 차이(deps 미설치/OS 차이) 오염 가능. Codex 가 게이트를 실행해 "실행 결과 ↔ 단정 불일치" 를 *보고* 하나, 그 finding 채택은 PL 직접 재실행(firsthand re-run) falsify 통과 시만(`[hypothesis]` → `[verified]`). 이는 신규 결정이 아니라 ADR-070 Amendment 12(review-lane execution scope 일반화, E1 Amendment 11 sibling)의 정책-실행 영역 적용이다. 실행 주체 = Codex CLI 자체 sandbox(read-only 기본/network-off/`.git`·`.codex` 보호) — lane worker own-Bash 직접 실행 아님(E1 X-4/X-6 + ADR-070 Amd11 §B3 execution-dispatch-pattern-v1 상속).

## 경계

- **In scope**: 재사용 거버넌스 규칙의 실행형 정책 게이트 묶음 개념 정립 + 멤버십 curation 자격 기준(P-1) + tier ⊕ 조직 결정(P-2) + exit-code verdict(P-3) + config∪behavioral(P-4) + ROI 죽은 게이트 제거(P-5) + 신호원 승격(P-6).
- **Out of scope**:
  - E1 execution-based-review-verification(execute-the-gate 일반 mechanism) — 본 개념의 base. Popper/discriminating/flaky/sandbox/신호원 = E1 SSOT(재정의 금지).
  - `fix-ground-truth-replay`(E3 의 다른 specialization — FIX-close 시점 replay) — 별 concept.
  - 정책팩 완성형 멤버십 enumeration, replay 강제 범위, max-FIX 상호작용 최종형 — 설계 후속(§1 "설계 확정", AC-11 — E3 완료 게이트 아님).
  - 새 touchpoint #9/#10 추가, 리뷰 peer 축소 = Epic CFP-2476 비대상. E3 = 기존 #7/#8 mechanism 일반화 + FIX-close wire (ADR-052 새 touchpoint 신설 아님).
- **Anti-pattern**: 모든 check-*.sh 를 무차별 멤버로(P-1 자격 무시 → cry-wolf). 동결 영역(wrapper changelog)에 멤버 게이트 적용(P-2 scope 부재 → false-RED). 실행 GREEN 을 "PR 옳음" 단정(E1 X-1 verify 불가). 정책 실행 결과 무재현 자동 채택(P-6 / E1 X-5 separation 위반). tags 에 policy-pack 부착(dead-check-exclude semantic 과 conflate).

## 관련 ADR

- **ADR-119** Amd 2 — 게이트 verdict 를 outcome ground-truth 로만 단정. 정책 실행 결과 단정의 상위 근거.
- **ADR-037** Amendment 4 (CFP-2480) — 정책팩 진입점 codify (version-bump 게이트가 정책팩 첫 멤버, 게이트 자체 무변경 — 실행 방식만 추가). changelog scope 분기(P-2) cross-ref(ADR-092).
- **ADR-092** §결정 3 — wrapper CHANGELOG 동결. changelog 멤버십 `policy_pack_scope` lane-plugin/consumer 한정 근거(P-2).
- **ADR-060** — evidence-enforceable promotion framework. 정책팩 멤버십 SSOT = evidence-checks-registry `policy_pack_member`/`policy_pack_scope` optional field(schema MINOR).
- **ADR-070** Amendment 12 (CFP-2480) — 일반 정책-실행 verify-before-trust scope (E1 Amendment 11 §결정 D9 disposition 의 정책-실행 영역 적용). execution-dispatch-pattern-v1 재사용 declare(신규 dispatch 발명 0).
- **ADR-052** — Codex proactive Touchpoint origin. 정책 실행 dispatch 가 기존 #7/#8 mechanism 재사용 (새 touchpoint 아님 — Epic 비대상).

## 변경 이력

- 2026-06-30 KST — 초기 작성 (CFP-2480 E3 ResearcherAgent Mandate 1·2 산출물 + ArchitectAgent chief author). Policy-as-Code(OPA CI/CD) / 자격 curation 기준(platformengineering PaC) / CNCF Automated Governance Maturity Model(config+behavioral, ROI 제거) cited. E1 `execution-based-review-verification`(execute-the-gate 일반) 의 specialization(curated membership) 으로 명시 — E1 SSOT 개념 재정의 금지, 참조만. Epic CFP-2476 3-mechanism family(A review-of-output / B probe-the-detector / E1 execute-the-gate) 위 E3 specialization.
