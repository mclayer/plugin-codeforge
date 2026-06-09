---
kind: domain_fact
type: domain-knowledge
area: governance-principle
topic_slug: adr-active-sunset-procedure
title: ADR 능동 일몰(active sunset) 실행 절차 SSOT — 단일·평시 sunset 6단계 + archive 강등 경로 + 역참조 안전 점검
status: Active
tags:
  - adr-sunset
  - active-sunset
  - sunset-status
  - archive-demotion
  - cross-reference-safety
  - carrier-preserved-sunset
  - adr-058
  - adr-095
  - adr-097
related_adrs:
  - ADR-058  # sunset criteria mandate — §결정 5 sunset_justification evidence-gate (본 절차의 정당화 입력)
  - ADR-095  # sunset metric 표준화 + K8s threshold (GA 12개월 / Beta 9개월) + bulk 집계 dashboard
  - ADR-097  # paradigm replacement governance anchor — §결정 3 carrier-preserved sunset (bulk sunset 개념)
  - ADR-050  # ADR-RESERVATION GitOpsAgent 운영 레지스트리 (G2 RESERVATION 잠금)
  - ADR-041  # doc-locations SSOT (본 문서 위치 + ADR archive/adr/ 경로)
related_stories:
  - CFP-2061-S3  # 본 carrier — 능동 일몰 절차 SSOT 신설 (Epic CFP-2061 de-bloat 거버넌스 영속화)
  - CFP-1186     # ADR-076 sunset 실행 첫 사례 (carrier-preserved, sunset_status: Sunsetted)
  - CFP-1111     # ADR-076/083 bulk sunset carrier (Wave 4 Story-11)
created: 2026-06-09
updated: 2026-06-09
---

# ADR 능동 일몰(active sunset) 실행 절차 SSOT

## 1. 목적 + 경계 (기존 기계장치와 중복 0)

codeforge 에는 ADR 일몰 **기준·메트릭·약화 차단** 기계장치가 이미 존재한다. 본 문서는 그것들을 **재정의하지 않고**, "기준을 충족한 단일 ADR 을 *실제로 일몰시키는 실행 절차*" 공백만 메운다.

| 기존 기계장치 | 책임 | 본 절차와의 경계 |
|---|---|---|
| **ADR-058** §결정 1-5 | `is_transitional` 분류 + `## 해소 기준` 3-tuple 의무 + 약화 evidence-gate (`sunset_justification`) | 본 절차는 ADR-058 이 정의한 evidence-gate 를 **입력**으로 받는다. sunset 의 정당화 *내용*은 ADR-058 이 SSOT — 본 절차는 그 정당화를 *어디에 어떻게 기록하고 status 를 어떻게 전이*하는지의 실행 단계만 정의. |
| **ADR-095** | sunset metric 형식 표준 + K8s 시간 threshold (GA 12개월 / Beta 9개월) + bulk 집계 dashboard schema | 본 절차는 ADR-095 의 metric/threshold 를 **후보 판정(2단계)의 입력 신호**로 인용. metric 산정 규칙 신설 0. |
| **ADR-097** §결정 3 | bulk(9+ ADR 동시) sunset = carrier-preserved sunset 개념 + paradigm replacement 면제 channel | 본 절차 scope = **단일·평시 sunset** (1 ADR, paradigm replacement 아님). bulk sunset 은 ADR-097 면제 channel 이 SSOT — 본 절차는 §6 에서 "bulk = 본 절차 비대상, ADR-097 경로" 만 명시. |
| **`scripts/lib/check_adr_sunset_criteria.py`** | sunset *기준* mechanical lint (warning) — `is_transitional` 존재 / `## 해소 기준` 섹션 / 3-tuple / 모달 어휘 | 본 절차는 이 lint 가 검증하지 **않는** 영역(status 전이·archive 강등·역참조)을 다룬다. lint 와 disjoint — 본 절차의 §5 역참조 점검은 Wave 1 declarative-only (mechanical lint = 후속 carrier). |

**중복 신설 금지 invariant**: 본 문서는 신규 워크플로 0 / 신규 스크립트 0 / 신규 ADR 0 (ADR-058 Amendment 로 연결만). doc-only fast-path (ADR-054).

## 2. sunset 전례 (실 retire 0건 주장 정정)

ADR-058 Amendment 1 (CFP-1149) 컨텍스트의 "실 retire 0건" 주장은 **stale** 다. 2026-05-22 이후 carrier-preserved sunset 이 실제로 집행된 ADR 이 존재한다 (verified-via Read archive/adr/):

| ADR | sunset_status | 집행 carrier | 방식 | verify |
|---|---|---|---|---|
| **ADR-076** (declarative reconciliation upgrade) | `sunset_status: Sunsetted` | CFP-1186 (2026-05-22) / CFP-1111 Wave 4 Story-11 | carrier-preserved — 효용이 imperative-walker-protocol-v1 으로 lossless carry (β2 audit #1113 Anchor 1 LOSSLESS). **본문 보존 (historical record), status 무이동** | frontmatter `sunset_status: Sunsetted` + §sunset_executed (CFP-1186) |
| **ADR-083** (consumer-applicability filter) | `sunset_status: Sunsetted` | CFP-1111 Wave 4 Story-11 | carrier-preserved — 효용이 walker per-step `applicable_to` filter 로 lossless carry (β2 audit #1113 Anchor 2 LOSSLESS) | frontmatter `sunset_status: Sunsetted` |

**정정 결론**: 능동 sunset 은 0건이 아니라 carrier-preserved bulk sunset 2건 (ADR-076/083) 의 전례를 가진다. 그러나 그 2건은 **bulk paradigm replacement (ADR-097 경로)** 였고, **단일·평시 sunset 의 표준 실행 절차는 여전히 부재** — 본 문서가 그 공백을 메운다. ADR-076/083 의 방식(본문 보존 + `sunset_status` 플래그 + 역참조 carry)은 본 절차의 G2 전례로 직접 인용한다.

## 3. G1 — 단일·평시 sunset 실행 6단계

단일 ADR 1건을, paradigm replacement 가 아닌 평시에 일몰시킬 때의 표준 절차. **각 단계는 enumeration 순서대로 진행**한다.

### 단계 0 — 적용 분기 판정 (gate)

- 대상이 **단일 ADR** + paradigm replacement (ADR-097 §결정 1 closed-set 3 조건) 아님 → 본 절차 진행.
- 대상이 **9+ ADR 동시 sunset** 또는 paradigm replacement 자격 → **본 절차 중단, ADR-097 면제 channel 경로**로 전환 (§6).

### 단계 1 — 트리거 (sunset 후보 발신)

다음 신호 중 1+ 발생 시 ArchitectAgent 가 sunset 후보를 식별:

- ADR `is_transitional: true` 의 `## 해소 기준` 3-tuple metric 이 충족됨 (ADR-058 §결정 3).
- ADR-095 시간 threshold 도달 (도입 사유 해소 후 GA-tier 12개월 / Beta-tier 9개월 경과).
- 대체 ADR/contract 가 Accepted 되어 본 ADR 효용이 다른 carrier 로 이전 가능 (supersede 신호).

### 단계 2 — 후보 판정 (sunset 자격 검증)

ArchitectAgent 가 다음 AND 조건을 검증한다 (1+ 미충족 = sunset 보류):

| 검증 | 신호 출처 |
|---|---|
| `is_transitional: true` (또는 명시적 sunset 발의 근거) | frontmatter (ADR-058 §결정 1) |
| `## 해소 기준` metric 충족 — 정량 측정 결과 보유 | ADR-058 §결정 3 + ADR-095 metric source |
| 효용 carry 경로 식별 — carrier-preserved (효용 소멸 = naive sunset 차단) | ADR-097 §결정 3 |
| 보안 ADR 예외 점검 — `is_transitional: false` presumption 영역이면 명시적 temporary 선언 보유 | ADR-058 §결정 7 |

**carrier-preserved 의무**: 효용이 대체 carrier 로 lossless 이전됨을 enumeration. naive sunset (효용 소멸, carrier 부재) 은 ADR-058 §결정 5 약화 차단 대상 — 본 절차 비대상.

### 단계 3 — `sunset_justification` 작성

ADR-058 §결정 5 evidence-gate 충족. amendment_log entry 에 다음을 명시:

- **약화 방향 evidence**: metric 측정 결과 / 외부 ADR 변경 / 환경 변화 / pattern obsolescence 중 해당 사유.
- **효용 carry 경로**: 효용이 어느 carrier(ADR/contract/script)로 lossless 이전되는지 (carrier-preserved 본문 — ADR-097 §결정 3 정합).
- 모달 어휘("안정화되면"/"임시"/"한시적"/"until further notice") 금지 (ADR-058 §결정 3 + lint).

### 단계 4 — status 강등 (G2 — §4 체크리스트 참조)

frontmatter `sunset_status: Sunsetted` 설정. 상세 = §4.

### 단계 5 — 역참조 갱신 (G3 — §5 절차 참조)

본 ADR 을 인용하는 다른 ADR/contract/doc 의 cross-ref 를 carrier-preserved 포인터로 갱신. 상세 = §5.

### 단계 6 — RESERVATION 잠금

`archive/adr/ADR-RESERVATION.md` 의 해당 `adr_number` row status 를 `active → archived` 로 갱신 (GitOpsAgent monopoly write, ADR-050). 잠금 = sunset 된 번호가 재사용/재할당되지 않음을 보장.

- RESERVATION schema status enum (`reserved | active | archived`, schema_version 1.1) 의 `archived` 값 사용.
- ADR 파일은 **삭제하지 않음** (번호는 영구 점유 — 본문 historical record).

## 4. G2 — archive 강등 체크리스트

status 강등 = **frontmatter 플래그 set + 파일 위치 유지 + RESERVATION 잠금** 3종. ADR-076/083 전례 동형 (§2).

| # | 항목 | 규칙 | 전례 |
|---|---|---|---|
| C-1 | `sunset_status: Sunsetted` frontmatter 추가 | 별도 `sunset_status` 필드 사용. **top-level `status:` 는 무변경** (Active/Accepted 유지 — status 는 ADR lifecycle, sunset_status 는 일몰 layer, disjoint) | ADR-076 L8 / ADR-083 |
| C-2 | `## sunset_executed` 본문 섹션 추가 | 일몰 carrier CFP + 일자 + 효용 carry 경로 + lossless evidence 명시 | ADR-076 §sunset_executed (CFP-1186) |
| C-3 | **본문 삭제 금지** | Sunsetted = retired/superseded 상태이나 본문은 historical record + carrier 참조 포인터로 영구 보존 | ADR-076 "본 ADR 본문 삭제 금지" |
| C-4 | **파일 위치 유지** | `archive/adr/ADR-NNN-<slug>.md` 그대로 (별도 sunsetted/ 디렉터리 이동 0 — doc-locations adr entry dogfood variant 정합). 파일 이동은 역참조 대량 파손 유발 → 금지 | doc-locations.yaml `adr` dogfood variant |
| C-5 | `is_transitional` 처리 | sunset 실행 시 `is_transitional: true → false (Sunsetted)` 전환 가능 (ADR-076 amendment_log 전례). 단 `sunset_status: Sunsetted` 가 일몰 SSOT 신호 | ADR-076 amendment_log |
| C-6 | RESERVATION row | §3 단계 6 — `active → archived` (GitOpsAgent) | ADR-050 schema |

**위치 확정 근거 (C-4)**: 일몰 ADR 을 별도 디렉터리로 *이동*하지 않는다. 이유 = (a) 역참조 경로 대량 파손, (b) `check_adr_sunset_criteria.py` 및 doc-locations 패턴이 `archive/adr/` 단일 위치 가정, (c) ADR-076/083 전례가 in-place 보존. 일몰 신호 = 파일 위치가 아닌 `sunset_status` frontmatter 플래그.

## 5. G3 — 역참조(cross-reference) 안전 점검 절차

sunset 대상 ADR 을 인용하는 모든 지점을 식별·갱신해 dangling reference 를 차단한다.

### 5.1 점검 대상 surface

| surface | grep 대상 |
|---|---|
| ADR frontmatter `related_adrs:` | `ADR-NNN` 토큰 (wrapper `archive/adr/` 전체) |
| ADR/doc 본문 cross-ref | `ADR-NNN` 산문 인용 |
| inter-plugin-contract / domain-knowledge / change-plan / playbook | `ADR-NNN` 인용 |
| **cross-repo** (sibling lane plugins + consumer overlay) | sibling repo 의 `docs/adr/` mirror + consumer `.claude/_overlay/` 인용 |

### 5.2 점검 절차 (Wave 1 — declarative, mechanical lint = 후속 carrier)

1. **grep 전수 수집**: wrapper repo 에서 `ADR-NNN` 토큰을 grep (frontmatter + 본문). 결과 = 역참조 inventory.
2. **cross-repo 확장**: `git fetch` 후 sibling lane plugin repo + consumer overlay 의 동일 grep (CLAUDE.md "검증 후 단언" 정합 — cross-repo 상태는 실제 확인). 인프라 장애(#2053/#2054) 시 manual gh 토큰 경유.
3. **carrier-preserved 갱신**: 각 역참조를 "ADR-NNN (Sunsetted — 효용 carry → <carrier>)" 포인터로 갱신. 인용 자체를 삭제하지 않음 (historical trail 보존).
4. **dangling 차단 확인**: 갱신 후 재-grep 으로 미갱신 잔존 0 확인 (verify-before-assert — CFP-2061-S1 F-1 재발 차단).

### 5.3 mechanical enforcement = 후속 carrier (Wave 1 declarative-only)

본 §5 는 **declarative-only** 다. 역참조 dangling 을 차단하는 mechanical lint (예: `sunset_status: Sunsetted` ADR 을 `related_adrs` 에 보유하면서 carrier 포인터 미부착 시 warning) 는 **후속 carrier** 다.

**근거**: lint script 신설 = `scripts/` + `templates/github-workflows/` 변경 → ADR-054 §결정 4/5 full-lane 강제. 본 S3 의 doc-only fast-path 유지를 위해 Wave 1 = declarative-only. mechanical 승격 = ADR-082 §결정 6 / ADR-070 §D5 retain pattern 답습 — pattern_count >= 2 (실 sunset 2건 이상 역참조 누락 발생) 재발 시 follow-up CFP MUST promote to mechanical (`adr-sunset-crossref-dangling` warning tier evidence-check-registry entry 후보).

## 6. bulk sunset 비대상 명시 (ADR-097 경로 분기)

9+ ADR 동시 sunset (paradigm replacement) 은 **본 절차 비대상**이다.

- 자격 판정: ADR-097 §결정 1 closed-set 3 조건 (9+ ADR 동시 sunset AND 단일 atomic Epic AND ratchet 강화 carrier-preserved).
- 경로: ADR-097 §결정 2 CFP scope unitary 면제 channel + §결정 3 carrier-preserved bulk sunset + ADR-095 bulk 집계 dashboard.
- 본 절차(§3-5)는 그 bulk Epic 안의 **개별 ADR 강등(§4) + 역참조(§5)** 의 단위 실행 참조로 재사용 가능 — 단 자격/면제/atomic merge order 는 ADR-097 이 SSOT.

## 7. 책임 (RACI)

| 단계 | 책임 |
|---|---|
| 트리거·후보 판정·`sunset_justification`·status 강등·역참조 (§3 단계 1-5) | ArchitectAgent (design lane chief author, ADR-070 chief author precedent) |
| RESERVATION 잠금 (§3 단계 6) | GitOpsAgent (ADR-050 monopoly write) |
| 절차 검수 + PASS 판정 | ArchitectPLAgent (design lane) |
| sunset PR 설계리뷰 — 모달 어휘 / carrier-preserved evidence / 역참조 dangling flag | DesignReviewPL (behavioral gate, Wave 1 mechanical lint 도입 전 1차 안전망) |
