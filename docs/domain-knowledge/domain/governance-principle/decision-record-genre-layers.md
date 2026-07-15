---
kind: domain_fact
type: domain-knowledge
area: governance-principle
topic_slug: decision-record-genre-layers
title: 결정기록 장르 4층 + 기수-임베드 좀비 벡터 + 4분기 처분 oracle + phantom-norm 인용 드리프트
status: Active
tags:
  - governance-principle
  - stale-record-disposition
  - phantom-norm
  - decision-record-genre
  - cardinal-embedding-zombie
  - disposition-oracle
related_adrs:
  - ADR-125  # phantom norm 발원 (6-tuple invariant 오인용)
  - ADR-145  # ①→③ 도피 표본 / I-APPLIC forward-only 해독제
  - ADR-087  # 5→6 ratchet 증가 실행 (phantom 반증 근거)
  - ADR-058  # §결정 9 carrier-preserved in-place 본문 보존
  - ADR-136  # I-6 정직 천장
  - ADR-013  # doc-only vehicle 근거
related_stories:
  - CFP-2697  # 카나리 carrier
  - CFP-2696  # Epic (stale/zombie decision-record 정산)
created: 2026-07-16
updated: 2026-07-16
---

# 결정기록 장르 4층 + 기수-임베드 좀비 벡터 + 4분기 처분 oracle + phantom-norm 인용 드리프트

## 정의

결정 기록(ADR·Change Plan·governance doc·workflow 주석)의 각 문장은 단일 성격이 아니다. **참조 대상(referent)·시제와 화행(tense·speech-act)·기수 결속(cardinal-bound)** 세 축으로 장르가 갈리며, 장르마다 stale 처분이 다르다. 앞의 4층이 기본 장르 골격이고, 뒤의 2개는 확장 처분 class(D7·D8)다.

| # | 장르 | 식별 기준 | stale 처분 |
|---|---|---|---|
| ① | Descriptive-dated | `## YYYY-MM-DD` 헤더 아래 서술 — 그 시점의 사실 기록 | 무처리 (dated 이력은 기록 시점 기준 참 — 시간이 지나도 거짓 아님) |
| ② | Descriptive-undated | 날짜 없는 현재형 사실 기술 — "지금 상태는 X" | 정정 (현재 사실과 어긋나면 현재값으로 수정) |
| ③ | Normative | 의무 어휘(MUST·의무·금지·불변·강제) — 규범 주장 | 효력 박탈 (거짓 규범은 규범 지위 자체를 제거) |
| ④ | Scope 선언 | 주어 = 자기 diff·자기 변경 범위 — "본 변경은 X 를 안 건드림" | 무처리 (자기 변경을 진술 — 시점 고정 참) |
| ⑤ | living-list 항목 | 존재-license(존재 근거)가 만료된 목록 항목 | byte 삭제 (D7 — 목록에서 물리 제거) |
| ⑥ | 보존된 이력 안 거짓 주장 | dated ∧ supersede 됨 ∧ 거짓 normative | 이력-거짓 표시 (D8 — byte 보존 + 별도 falsehood-mark) |

핵심: **①·④ 는 시점 고정된 참**이므로 stale 로 보여도 손대지 않는다. **②·③ 만 실제 정정·박탈 대상**이다. 처분을 틀리면(예: ④ 를 ② 로 오인해 숫자 치환) 오히려 참인 기록을 훼손한다.

## 컨텍스트

**좀비(zombie) 생성 벡터 = 가변 측정값을 불변 서술에 리터럴로 임베드하는 것.**

- 가변 측정값 = count(tuple 개수)·version(버전 번호)·SHA(커밋 해시) 등 시간에 따라 변하는 수치.
- 불변 서술 = 규범(③)·scope 선언(④)처럼 시점과 무관하게 참이어야 하는 문장.
- 참조 pointer(예: "CLAUDE.md 브랜치 보호 표", "ADR-125 §결정2")는 **안 썩는다** — 가리키는 대상이 갱신되면 자동으로 최신을 가리킨다.
- 반면 리터럴 수치("6-tuple")를 규범·scope 문장에 박으면, 실제 값이 6→7 로 바뀐 순간 그 문장은 stale·거짓처럼 보인다.
- 실 결함의 대다수는 **②·④ 의 융합**이다: scope 선언(④, 무처리 대상)에 가변 count 를 박아넣어 겉보기엔 정정 대상(②)처럼 보이는 하이브리드. 올바른 처분은 숫자 치환(6→7)이 아니라 **기수 제거(cardinal-removal)** — 참조 pointer 로 되돌려 좀비 벡터 자체를 제거한다.

## 핵심 규칙

**4분기 disposition oracle** — 각 stale-후보 문장을 아래 순서로 판정한다.

전치 필터:

- **Q0 (homonym 전치필터)**: 표면 문자열이 같아도 referent 가 다르면 별개다. "6 lane gate"(레인 수) ≠ "6-tuple"(context 수). 동음이의 토큰을 먼저 걸러 오정정을 막는다.
- **Q0′ (phantom-enforcement surface-detection)**: 그 문장이 실제로 강제되는 규범인지, 아니면 인용만 누적된 phantom(제정된 적 없는 규범)인지 판별한다. phantom 이면 §phantom norm 처리로 분기.

4분기:

1. **정정(②)** — 날짜 없는 현재형 사실이 현재값과 어긋남 → 현재값으로 수정.
2. **효력 박탈(③)** — 거짓 규범(의무 어휘) → 규범 지위 제거(문장을 서술로 강등하거나 규범 주장 삭제).
3. **삭제(⑤ / D7)** — 존재 근거 만료된 living-list 항목 → byte 삭제.
4. **이력-거짓(⑥ / D8)** — dated ∧ supersede ∧ 거짓 normative → byte 보존 + 외부 falsehood-mark.

- **Q4 fail-closed**: 위 어디에도 확정 못 하면 무처리(①·④ 가정) + 관찰 기록. 성급한 정정보다 보류가 안전(참인 기록 훼손 방지).

3 판별축(각 분기의 입력):

- **referent** — 문장이 가리키는 대상(레인 수 / context 수 / 버전 …).
- **tense·화행** — dated 이력(①) / 현재형 사실(②) / 규범 주장(③) / 자기-diff 진술(④).
- **cardinal-bound** — 문장의 참·거짓이 그 리터럴 수치에 결속돼 있는가. 결속돼 있으면 좀비 벡터 → 기수 제거 후보.

§9 tree(요약): Q0 homonym → Q0′ phantom → [② 정정 | ③ 박탈 | ⑤ 삭제 | ⑥ 이력-거짓] → 미결 시 Q4 fail-closed 무처리.

## phantom norm

**phantom norm = 제정된 적 없이 인용 누적만으로 규범 지위를 획득한 규범.**

- 좀비 vs phantom 대비: **좀비 = 부활**(한때 참이던 측정값이 stale 로 되살아나 거짓 행세) / **phantom = 처녀생식**(애초에 규범으로 제정된 적이 없는데 인용이 인용을 낳아 규범인 척).
- 처리: phantom 은 **폐기(rescind)가 불가능**하다 — 폐기하려면 먼저 존재해야 하는데 존재한 적이 없다. 유효한 처리는 오직 **오인용 정정**(그 규범을 인용한 문장들을 "그런 규범은 없었다"로 바로잡기)뿐이다.

### 보존되나 거짓 표시된 phantom-norm 실물 예

본 사례의 phantom = "6-tuple invariant / 6-tuple 불변 원칙". 실제로는 ADR-087 Amendment 2 가 required context 를 5→6 으로 **ratchet 증가**시킨 것뿐이고, 불변(invariant)으로 제정된 적이 없다. 그럼에도 아래 지점들이 이를 규범으로 인용했다.

- `docs/security/branch-protection-audit.md:227` — "6-tuple 불변 원칙 자체는 폐기 아님". dated 이력 섹션(`## 2026-07-11`) 안의 **거짓 normative**(class-⑥ / D8). **byte-for-byte 보존**(byte-purity — dated 이력 훼손 금지)하되, 그 거짓됨의 표식은 audit.md 안의 tombstone 이 아니라 **본 page 가 durable falsehood-mark 로 짊어진다**. 즉 audit.md 에는 어떤 수정·묘비도 생산하지 않는다.
- `archive/adr/ADR-125-requirements-review-lane.md:99` — **phantom 발원지**. 5→6 ratchet 증가를 "6-tuple invariant"로 오인용. Phase 2 correction 대상(본 Story 에서 기수·invariant 프레이밍 제거).
- `archive/adr/ADR-145-ac-traceability-zero-drop-gate.md:101` — **①→③ 도피 표본**. dated 서술로 보존될 자리를 "6-tuple 불변 원칙"이라는 규범 프레이밍으로 격상해 인용. Phase 2 correction 대상.

## 경계

honesty ceiling(ADR-136 I-6 정직 천장):

- **본 Story(A) 가 보장하는 것**: 위에 든 대상 파일들의 **in-file completeness**(그 파일 안 phantom-norm class 제거) + phantom-norm 프레이밍 제거 + **대표 4-분기 표본**(단일 축 = branch-protection required contexts, 2개 ADR 표본으로 methodology 시연).
- **보장하지 않는 것(B, 후속 #2698)**: 전체 규모(159개 ADR·다축)에 걸친 완전 sweep, cross-file 기수 임베드(~50 file 규모) 전수 정정.
- **금지**: "모든 사본을 고쳤다"류 hard-claim. 본 page 는 methodology 와 대표 표본을 정립할 뿐 전수 완결을 주장하지 않는다(성급한 완결 선언 = ADR-119 premature-declaration 재범).

## 관련 ADR

- **ADR-125** — phantom norm 발원(6-tuple invariant 오인용). §결정2 는 원래 required contexts 무변경(INTERNAL 흡수) 선언이었으나 :99 가 이를 invariant 로 오인용.
- **ADR-145** — ①→③ 도피 표본. I-APPLIC forward-only 해독제(적용성 판정의 비가역·비억제 성질)와 대비.
- **ADR-087** — 5→6 ratchet 증가 실행(phantom 반증 근거 — 이 증가가 "불변"이 아니라 ratchet 이었음을 실증).
- **ADR-058** — §결정 9 carrier-preserved in-place 본문 보존(dated 이력 byte 보존 원칙의 상위 근거).
- **ADR-136** — I-6 정직 천장(경계 절의 근거).
- **ADR-013** — doc-only vehicle 근거(본 정정이 정식 doc-only Story 로 진행되는 근거).

## 변경 이력

- 2026-07-16 (CFP-2697): 신규 — 결정기록 장르 4층 + 4분기 처분 oracle + phantom-norm 인용 드리프트 methodology 정립 (Epic #2696 카나리).
