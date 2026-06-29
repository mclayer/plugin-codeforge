---
kind: concept_definition
type: domain-knowledge
slug: claim-to-evidence-audit
title: Claim-to-evidence audit + cross-document consistency sweep (LLM-as-fact-checker grounding every substantive assertion to measured repo fact or cited source, plus execution-based cross-reference integrity)
status: Active
updated: 2026-06-30
carrier_story: CFP-2478
related_adrs:
  - ADR-119  # research-before-claims — Amd 2 게이트/실패진단 ground-truth + falsifiable evidence. 본 감사기 = 이 정책의 기계 자동화 carrier
  - ADR-074  # CLAUDE.md amendment ref drift lint — 가장 가까운 cross-document coherence 선례 (narrative↔amendment_log)
  - ADR-052  # Codex proactive Touchpoint — Codex=신호원 dual-peer trigger origin (감사기 dispatch 재사용)
  - ADR-070  # verify-before-trust 5 sub-scope — "주장→증거 감사기"의 수동 원형 (기계화 대상)
  - ADR-077  # clarification 강제 재조사 — fact-check marker 무검증 승격 금지 (finding 승격 룰 anchor)
related_concepts:
  - merge-time-adversarial-verification-gate  # Epic CFP-2457 Story A — 같은 적대적 검증 family, review-of-output mechanism
  - mutation-based-hollow-gate-detection       # Epic CFP-2457 Story B — probe-the-detector mechanism
  - clarification-driven-reinvestigation       # fact-check marker invariant 재사용 anchor
  - orchestrator-runtime-hook-enforcement      # 감사기 dispatch enforcement layer (Orchestrator inline 전용)
tags:
  - claim-verification
  - fact-checking-automation
  - cross-document-consistency
  - cross-reference-integrity
  - documentation-drift
  - llm-as-fact-checker
  - stale-reference-detection
  - phantom-id-detection
  - executable-specification
  - single-source-of-truth
  - false-positive-calibration
sources:
  - https://www.datadoghq.com/blog/ai/llm-hallucination-detection/                  # LLM-as-judge claim 분해 후 context 대조 (claim extraction → verify → score)
  - https://arxiv.org/abs/2506.07446                                                 # Fact in Fragments (AFEV) — atomic fact extraction+verification, over-extraction/inferred-fact FP 정성 근거 (수치 미보고)
  - https://arxiv.org/html/2606.19819v1                                              # CREDENCE — claim reduction for decomposition (over-extraction 억제)
  - https://arxiv.org/pdf/2508.03860                                                 # Hallucination to Truth — fact-checking/factuality 평가 survey
  - https://arxiv.org/abs/2212.01479                                                 # Detecting Outdated Code Element References in Docs — 3,000+ GitHub 프로젝트 다수 stale ref (학술 선례)
  - https://link.springer.com/article/10.1007/s10664-023-10397-6                     # 위 논문 저널판 (Empirical Software Engineering)
  - https://docs.gitlab.com/development/documentation/testing/vale/                  # Vale — terminology/용어 일관성 docs-as-code linter (GitLab CI 적용)
  - https://www.sphinx-doc.org/en/master/usage/extensions/intersphinx.html          # Sphinx intersphinx — cross-ref 부재/변경 시 warning (cross-document integrity)
  - https://www.sphinx-doc.org/en/master/_modules/sphinx/builders/linkcheck.html    # Sphinx linkcheck — anchor 검증 + false-positive 이력
  - https://github.com/thomvaill/log4brains                                         # log4brains — ADR 관리/relationship 시각화 (ADR tooling)
  - https://adr.github.io/adr-tooling/                                              # ADR tooling 카탈로그 (adr-tools/MADR)
  - https://docs.python.org/3/library/doctest.html                                  # doctest — executable documentation (예시를 실행으로 검증)
  - https://ai-assisted-software-development.com/executable-specs/                  # executable spec — "enforce 안 되면 documentation, executable spec 아님"
  - https://en.wikipedia.org/wiki/Single_source_of_truth                            # SSOT — 데이터 원소 1곳에서만 master (drift 구조적 차단)
  - https://malkomich.github.io/api-first-with-openapi-generator:-from-spec-to-rest-api-and-type-safe-sdks/  # generate-from-spec + build-fail-on-drift (감사 대안 = 생성)
  - https://dl.acm.org/doi/10.1109/TSE.2023.3329667                                 # Mitigating False Positive Static Analysis Warnings (TSE) — FP 18~86%, 20~30%+ 시 도구 폐기
  - https://arxiv.org/pdf/2311.07482                                                # Quieting the Static — alert suppression 연구 (cry-wolf 실증)
  - https://arxiv.org/pdf/2601.06118                                                # Beyond Reproducibility — token probabilities 로 LLM nondeterminism 노출
  - https://www.morphllm.com/defeating-nondeterminism-llm-inference                 # batch-invariance failure = temp0 에도 비결정 (감사기 재현성 위협)
---

## 정의

**Claim-to-evidence audit** = ADR / PR description / Story 등 거버넌스 산출물의 모든 substantive 단정(주장)을 개별 claim 으로 파싱한 뒤, 각 claim 을 (a) 측정된 repo 사실(Read/Grep/스크립트 실행 결과) 또는 (b) 인용 출처에 매핑하고, 매핑 불가(grounding 실패)하거나 수치·사실 불일치인 claim 을 finding 으로 fail 시키는 검증 기법. 외부 학계·산업 용어로는 **claim extraction → verification → grounding**(LLM-as-judge / fact-checking 파이프라인)과 동형이다 (출처: Datadog LLM hallucination detection; arxiv 2508.03860 fact-checking survey).

**Cross-document consistency sweep** = 위 단일 claim 검증을 넘어, 문서 *간*(cross-document/cross-ADR) 참조 무결성을 실행 기반(grep/대조)으로 검사하는 보완 축 — ADR 간 cross-ref 번호, enum 리터럴, citation 줄번호, 버전 표기 등이 SSOT 와 일관적인지 검사한다. 외부 용어로는 **cross-reference integrity checking** + **stale/phantom reference detection** + **documentation drift detection**(출처: Sphinx intersphinx; arxiv 2212.01479 outdated code element references).

두 축의 공통 본질 = **assertion ≠ truth** 를 강제하는 grounding. executable-spec 문헌이 같은 통찰을 다른 말로 표현한다 — "scenario 가 정밀해 보여도 아무것도 enforce 하지 않으면 그것은 documentation 이지 executable spec 이 아니다"(출처: ai-assisted-software-development.com/executable-specs). 본 감사기 = 거버넌스 narrative 를 executable assertion 으로 전환하는 시도.

## 컨텍스트

CFP-2478(Epic CFP-2476 의 E2) 동인 = ADR-119(검증-후-단언) 정책의 **기계 자동화**. ADR-119 §결정 8 은 enforcement 를 declarative-only(`mechanical_enforcement_actions: []`)로 두고 mechanical 승격을 ADR-060 4-tier 경로에 위임했으므로, 본 감사기가 그 mechanical carrier 후보다 (Story 입력 packet verbatim).

발동 계기 = CFP-2457 에서 이 클래스의 drift 가 ≥4건 실발생 — (1) ADR-039 inline whitelist entry "5번째↔6번째" mis-cite(cross-ref 번호 오기), (2) ADR-052 D3 enum 리터럴 `<1..6>` stale(enum literal drift), (3) ADR-077 존재하지 않는 "I-4" ID 인용(phantom ID reference), (4) citation 줄번호 오기(line number cite drift). 이 4종은 외부 학술 taxonomy 의 **outdated code element reference**(소스에서 삭제됐으나 문서에 잔존하는 참조)와 정확히 같은 부류다 — arxiv 2212.01479 는 3,000+ GitHub 프로젝트 분석에서 "대부분의 프로젝트가 이력 어느 시점엔가 stale reference 를 최소 1개 포함"을 실증했다(출처: arxiv 2212.01479).

Epic 축 "execute-and-falsify" 에서 본 Story 는 Story A(merge-time-adversarial-verification-gate, review-of-output) / Story B(mutation-based-hollow-gate-detection, probe-the-detector)와 **같은 적대적-검증 family 의 세 번째 mechanism = ground-the-claim** 이다 — diff 를 읽는 2번째 비평가가 아니라 실행 대조(grep/Read/script)로 거짓 확신을 깨는 검증자. Codex(GPT-5)의 다른 학습분포 + 실행 대조가 single-pass Claude 보다 이 정합 결함을 잘 포착(Story 입력 packet). single-pass Claude 의 self-review 한계는 family C-1(echo-chamber)·C-5(single-pass 인식론적 한계) 와 동근.

## 핵심 규칙 (외부 개념 → invariant 매핑)

### CE-1: claim 추출 자체가 false-positive 원천 (over-extraction — 가장 중요한 unknown-unknown #1)

LLM-as-judge 파이프라인의 1단계 = "답변을 atomic claim 으로 분해"인데, 이 분해 단계가 **inferred atomic fact**(원문에 strictly 존재하지 않으나 의미상 그럴듯한 fact)를 생성해 false-positive 를 낳는다(출처: arxiv 2506.07446 Fact in Fragments / AFEV — 정적 분해 전략이 claim 의 구조·의도를 못 잡아 reasoning error·noise 누적을 일으킨다고 보고; 정량 precision/recall 수치는 abstract 미보고). 산업·학계 공통 통찰: atomic decomposition 단계는 compound 구조 오분할·명시 주어 없는 절 분할 실패로 inferred-fact 를 만들어내는 정성적 FP 진원이다. CREDENCE 는 over-extraction 억제를 위해 claim *축소*(reduction)를 별도 단계로 둔다(출처: arxiv 2606.19819).

**함의**: "감사기가 단정 N개를 파싱했다"의 N 자체가 오류원. 원문에 없는 implicit 단정을 감사기가 만들어내 "근거 없는 주장" finding 으로 fail 시키면, 이는 원문 저자가 **충족 불가능한 요구**(존재하지 않는 주장에 증거를 대라)를 받는 것 — cry-wolf 의 악성 형태(mutation 의 equivalent-mutant 와 동형). 따라서 감사기 finding 은 **원문에 verbatim 존재하는 단정에만** 한정해야 하고, parsing 단계 출력 자체가 `[hypothesis]` default 다.

### CE-2: cross-document 정합은 grep-결정론 영역이 LLM 보다 강함 (mechanism 선택 축 — unknown-unknown #2)

CFP-2457 4 drift 중 (1)(2)(3)은 본질적으로 **deterministic string/number 대조**다 — "ADR-077 에 'I-4' anchor 가 실존하는가"는 grep 1회로 binary 판정되며 LLM 추론이 불필요하고, LLM 을 끼우면 오히려 nondeterminism 을 주입한다(CE-5). 이는 산업 docs-as-code 의 검증된 패턴 — Sphinx intersphinx 는 cross-ref 가 삭제·변경되면 warning(출처: sphinx intersphinx), linkcheck 는 anchor 부재를 검출(출처: sphinx linkcheck), Vale 는 용어 일관성을 deterministic rule 로 강제(출처: GitLab Vale). 기존 codeforge 선례 2종(`check_adr_citation_slug.py`: ADR-NNN→파일 존재 grep; ADR-074 lint: narrative cite↔amendment_log length 대조)도 deterministic grep 모델이다.

**함의 (선택지 — 결정은 PL/설계)**: cross-document sweep 은 **두 층위로 분해** 가능 — (층위 A) 결정론적 grep/대조로 충분한 부류(번호 존재/anchor 실존/줄번호 일치/버전 문자열 일치) = LLM 불필요, 기존 lint 선례 확장이 적합; (층위 B) 의미 정합이 필요한 부류(번호는 맞으나 §결정 N 의 *의미*가 인용과 다른 misquote — `check_adr_citation_slug.py` 가 명시 미탐지로 남긴 잔여) = LLM(Codex) 대조가 가치. 외부 선례가 일관되게 시사하는 것: **deterministic 으로 잡히는 것에 LLM 을 쓰지 말 것**(비용·재현성 손해).

### CE-3: drift 의 구조적 대안 = 검출이 아닌 생성 (detect-after-the-fact vs prevent-by-construction — unknown-unknown #3)

산업의 SSOT 정착 패턴은 drift 를 *검출* 하지 않고 *발생 불가능* 하게 만든다 — 데이터 원소를 1곳에서만 master 하고 나머지를 생성(출처: Wikipedia SSOT). API-first 흐름: OpenAPI spec 이 SSOT, 서버·클라이언트·문서를 모두 spec 에서 generate → "절대 drift 불가"(출처: API-first with OpenAPI Generator). enforcement 방식 = **generate-and-diff / golden file**: 커밋된 산출물을 재생성해 diff 가 나면 CI fail(출처: snapshot/golden testing; API-first). enum 리터럴 drift(CFP-2457 #2)의 가장 견고한 해결은 "enum 을 코드 1곳에 정의하고 문서가 그것을 인용·생성"이지 "문서의 stale enum 을 사후 검출"이 아니다.

**함의 (선택지 — 결정은 PL/설계)**: 감사기(detect)는 거버넌스 narrative 처럼 **생성 불가능한 자유 텍스트**에 적합한 도구다(ADR 산문은 SSOT-generate 대상이 아님). 그러나 enum 리터럴·버전 표기처럼 **SSOT 가 존재하는** 항목은 detect 보다 generate-and-diff 가 구조적으로 우월할 수 있다. 즉 Story §1 의 "enum 리터럴·버전 표기 정합 검사"는 두 갈래(audit-detect vs generate-from-SSOT)가 있고, 항목 성격에 따라 다르게 갈 수 있다(PL 이 도메인 제약과 조화).

### CE-4: line-number citation 은 본질적으로 fragile — anchor 기반이 더 견고 (unknown-unknown #4)

CFP-2457 #4(줄번호 오기)는 단발 오류가 아니라 **줄번호 cite 의 구조적 fragility** 증상이다 — 파일이 1줄만 바뀌어도 그 아래 모든 줄번호 cite 가 자동 stale 된다. 이것이 GitHub permalink 가 commit-SHA 고정 + #L 범위를 쓰는 이유이자(출처: GitHub permanent link docs), content-anchor(불변 식별자) cite 가 line-number cite 보다 견고한 이유다. codeforge 자체 MEMORY.md 가 이 교훈을 firsthand 기록 — CFP-2426 에서 "line# fabrication → content-anchor grep SSOT 전환"(MEMORY.md). 학술 taxonomy 도 "code element reference"(symbol/identifier 기준)를 1급 단위로 두지 line-number 를 두지 않는다(출처: arxiv 2212.01479).

**함의 (선택지 — 결정은 PL/설계)**: "citation 줄번호 정합 검사"는 두 방향 — (a) 줄번호가 여전히 맞는지 사후 검사(fragile 한 관행을 유지한 채 패치), (b) 줄번호 cite 자체를 content-anchor cite 로 전환하도록 유도(근본 원인 제거). 감사기가 (a)만 하면 fragility 의 무한 두더지잡기가 되고, (b)는 별도 정책(cite 규약 변경)이 필요. 외부·내부 증거 모두 anchor-기반을 선호.

### CE-5: 감사기가 LLM 이면 finding 자체가 비결정 — 재현성이 audit 의 전제 (unknown-unknown #5)

audit/safety/regression 용도는 **bit-level 재현성**을 요구하나(출처: morphllm; arxiv 2601.06118), LLM 추론은 temperature 0 에서도 비결정이다 — floating-point 비결합성 + dynamic batching(batch-invariance failure)이 원인이며, batch-invariant kernel 로만 1,000회 bitwise 재현 달성(출처: morphllm; FlowHunt). 즉 "같은 ADR 을 같은 프롬프트로 감사해도 finding 집합이 run 마다 다를 수 있다."

**함의**: 감사기가 LLM(Codex) 기반이면 finding 은 **재현 불가능한 신호**이므로 자동 차단 권한을 줄 수 없다 — family C-3(overcorrection)·M-1(equivalent mutant)와 같은 결론으로 합류: Codex finding = `[hypothesis]` default, ground-truth(Read/Grep/script) 직접 falsify 후만 `[verified]` 승격(= Story §1 "Codex finding 은 ground-truth falsify 후 채택" = ADR-070 D1/D3 verify-before-trust = ADR-077 I-4). 반대로 CE-2 층위 A 의 deterministic grep 검사는 재현 가능하므로 자동 tier 부여가 정당화될 수 있다. **재현성이 차단권한의 전제** — 이 구분이 enforcement tier 설계의 핵심.

### CE-6: false-positive calibration = 채택 생존 조건 (family C-4 cry-wolf 상속)

static analysis 의 FP rate 는 도구별 18~86%, 20~30% 초과 시 산업 현장에서 도구 폐기가 빈번(출처: TSE 2023 Mitigating FP; arxiv 2311.07482 Quieting the Static). 본 감사기의 FP 원천은 critic 환각이 아니라 **mechanism-특유** — (CE-1) claim over-extraction, (CE-2 오용) deterministic 영역에 LLM 주입, (CE-5) nondeterminism. family Story A C-4 와 동일 결론: P2 급 finding 자동 차단 금지(기록 후 진행), 차단·FIX 승격 권한은 evidence 동반 + ground-truth 재검증 통과 finding 에 한정. Codex 는 승인·차단 권한 없는 신호원.

**함의 (검사연극 처리)**: Story §1 verbatim "오탐(검사연극) 처리"는 두 의미 — (가) 감사기 자신의 FP(억울한 finding), (나) 감사기가 *대상*에서 검사연극을 잡는 것. (가)는 CE-1·CE-5 구조 전처리(verbatim-claim 한정 + ground-truth 재검증)로, (나)는 deterministic 대조(CE-2 층위 A)로 가장 잘 처리된다. tautological/hollow 검사(코드 실행만 하고 동작 미검증)는 family Story B(mutation) 영역과 인접하나 mechanism 이 다름.

## 경계

- **In scope**: 거버넌스 산출물의 substantive 단정을 measured repo fact / cited source 에 grounding 하는 claim-to-evidence audit + cross-document/cross-ADR 정합 sweep 의 개념 정립 + 실패모드(over-extraction / nondeterminism / line-number fragility) + mechanism 선택축(deterministic grep vs LLM vs generate-from-SSOT) + finding 승격 룰.
- **Out of scope**:
  - Story A(merge-time-adversarial-verification-gate) — *PR diff 산출물* 을 critic 이 review (review-of-output). 본 개념은 *단정* 을 evidence 에 grounding (ground-the-claim). 같은 family, 다른 mechanism — 중복 아님, defense-in-depth.
  - Story B(mutation-based-hollow-gate-detection) — *테스트 detector* 를 변이로 probe (probe-the-detector). 본 개념은 *narrative 단정* 대상.
  - **적용 lane/게이트 시점, 전수 vs 변경분 한정, warning vs blocking tier, 오탐 처리 구체 wiring, dispatch enforcement 기구(Orchestrator inline matcher / CI job)** — Story §1 verbatim "설계에서 확정" 이며 본 개념 layer 위임 대상(개념·선택지만 제공, 결정은 PL/설계가 도메인 제약과 조화).
- **Anti-pattern**: claim over-extraction 으로 원문에 없는 단정을 만들어 fail(CE-1 cry-wolf). deterministic 으로 잡히는 cross-ref 정합에 LLM 주입(CE-2 비용·재현성 손해). LLM finding 을 ground-truth 재검증 없이 자동 차단(CE-5 비결정 신호 오용). line-number cite 의 사후 검사만으로 fragility 근본원인 방치(CE-4). enum/version SSOT 항목을 generate-from-SSOT 대신 detect-after-the-fact 로만 처리(CE-3).

## 관련 ADR

- **ADR-119** Amd 2 — 검증-후-단언 + falsifiable evidence 의무. 본 감사기 = 이 정책의 mechanical 자동화 carrier(§결정 8 declarative→mechanical 승격 경로).
- **ADR-074** — CLAUDE.md amendment ref drift lint. 가장 가까운 cross-document coherence 선례(narrative cite↔amendment_log length 대조). 본 sweep = 그 scope(CLAUDE.md↔amendment_log)를 ADR↔ADR cross-ref / enum / 줄번호 / 버전으로 확장.
- **ADR-052** — Codex proactive Touchpoint, dual-peer Codex 신호원 선례. 감사기 dispatch 가 이 origin 을 claim-audit 축으로 재사용(신규 touchpoint #8? 또는 별 mechanism class — Story 입력 packet).
- **ADR-070** D2 — verify-before-trust 5 sub-scope(file/dir/cross-repo/active-vs-historical/ADR §결정 번호 정확성). 이 5종이 "주장→증거 감사기"의 수동 원형 — 본 CFP 가 기계화·전수화. D1/D3 = finding ground-truth 재검증 후 채택(CE-5).
- **ADR-077** I-4 — fact-check marker 무검증 승격 금지. Codex finding = hypothesis default, 재검증 후 verified 승격(CE-5)의 재사용 anchor.

## 변경 이력

- 2026-06-30 KST — 초기 작성 (CFP-2478 ResearcherAgent Mandate 1·2 산출물). LLM-as-judge claim-verification(Datadog/Fact-in-Fragments/CREDENCE) + cross-reference integrity(Sphinx/Vale/log4brains) + outdated-reference 학술 선례(arxiv 2212.01479) + SSOT/generate-and-diff 대안 + static-analysis cry-wolf(TSE 2023) + LLM nondeterminism(morphllm/arxiv 2601.06118) cited. Epic CFP-2457 family Story A·B 와 mechanism 차이(ground-the-claim vs review-of-output vs probe-the-detector) 명시.
- 2026-06-30 KST — 요구사항리뷰 FIX(CFP-2478, P1×2): 외부 학술인용 정확성 정정. (P1-a) arxiv 2506.07446 의 "GPT-4 atomic extraction precision 0.65/recall 0.68" 귀속 제거 — 해당 논문(AFEV)은 abstract 에 GPT-4·0.65/0.68 정량 수치를 보고하지 않음(over-extraction/inferred-fact FP 정성 결론만 보존). (P1-b) "atomic decomposition FP 5.8%/FN 10.5% (출처 2510.22590 ATOM)" 수치+인용 제거 — 2510.22590(ATOM)은 temporal knowledge graph 구축 논문으로 5.8%/10.5% 미보고이며, 후보 출처 2410.16708 도 동 수치 미보고(출처불명 수치 삭제). frontmatter source 주석(2506.07446) 도 정성 근거로 재기술.
