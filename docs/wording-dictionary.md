---
schema_version: "1.0"
introduced_by: CFP-610
last_updated: 2026-05-27
amendments:
  - amendment: 1
    carrier_cfp: CFP-672
    date: 2026-05-14
    summary: "카테고리 (a) 4 → 5 어휘 (`별` standalone 추가, ADR-064 Amendment 4 lockstep)"
  - amendment: 2
    carrier_cfp: CFP-750
    date: 2026-05-16
    summary: "lint scope per-word decoupling (FORBID_DICTIONARY array → WORD_TARGETS map). 박제/못 박기/pin/freezing = expanded scope (docs/** + CLAUDE.md + CHANGELOG.md + templates/**) / 별 = 5-scope 유지. ADR-064 Amendment 5 lockstep"
  - amendment: 3
    carrier_cfp: CFP-1060
    date: 2026-05-20
    summary: "`별 + carrier-noun` hand-off vocabulary exemption codify (Wave 1 declarative). 의도된 '별도의 N' 패턴 (별 sub-CFP / 별 carrier / 별 session / 별 Story / 별 Issue / 별 PR / 별 lane / 별 sub-Epic / 별 Epic / 별 Wave 등) = forbid-list exempt. CFP-1041 evidence (13+ occurrence declarative SSOT, DesignReview F-DR-1041-3 bypass-as-design pattern). Wave 2 mechanical lint update = CFP-2154 (PR #2155, 2026-06-11) 가 `scripts/check-wording-dictionary.sh` 에 선언 regex verbatim wire 완료 (self-test 12 case). ADR-064 Amendment 6 lockstep."
  - amendment: 4
    carrier_cfp: CFP-1764
    date: 2026-05-27
    summary: "카테고리 (c) 신설 — codename → 평이 어휘 1:1 mapping table (mid-turn glossary lookup SSOT). closed 15 codename 첫 batch + ratchet extensibility (신규 어휘 추가 = 별 CFP 의무). ADR-071 Amendment 8 §결정 19 lockstep — Orchestrator 가 agent burst output 을 사용자 메시지로 합성할 때 (mid-turn paste-and-translate) 의무 lookup."
title: "codeforge wording dictionary — 어휘 사전 (forbid + 평문 정의 의무 + codename mapping)"
---

# codeforge wording dictionary

codeforge 의 표현 규율 (ADR-064 §결정 2 + §결정 9) 의 어휘 SSOT.

## 개요

사용자 (한국어 native, solo dev) 가 codeforge family jargon 노출 영역에서 frustration 을 표현한 directive (Issue #610, 2026-05-13) 를 계기로 신설. 3 카테고리:

- **(a) 사용 금지 어휘 (forbid)**: 사용 시 lint warning. ADR-064 §결정 2 와 verbatim sync 의무.
- **(b) 사용 허용 + 평문 정의 동반 의무**: codeforge 식별자 어휘. 사용 가능하되 inline 평문 정의 동반 필수.
- **(c) codename → 평이 어휘 1:1 mapping (mid-turn glossary lookup SSOT)**: Orchestrator 가 agent burst output 을 사용자 메시지로 합성할 때 (mid-turn paste-and-translate) 의무 lookup. 사용 금지 아님 — 사용자 dialog 영역에서 평이 어휘로 치환 또는 풀이 동반 의무. ADR-071 §결정 19 (Amendment 8) carrier.

## 카테고리 (a) — 사용 금지 어휘 (forbid)

**SSOT 방향**: 본 표 = SSOT. ADR-064 §결정 2 forbid-list 표 (Amendment 2 부분) + lint script (`scripts/check-wording-dictionary.sh`) `WORD_TARGETS` associative array 가 mirror. 변경 시 lockstep 갱신 의무.

**lint 적용 영역 (per-word scope decoupling — ADR-064 Amendment 5 / CFP-750)**: 어휘별 scope 독립 (`scripts/check-wording-dictionary.sh` `WORD_TARGETS` map).

| 어휘 | lint scope |
|---|---|
| 박제 / 못 박기 / pin / freezing | `docs/**` (전체 — adr / change-plans / inter-plugin-contracts / domain-knowledge / retros / security 등 모든 sub-dir + top-level `docs/*.md`) + `CLAUDE.md` + `CHANGELOG.md` + `templates/**` (expanded scope) |
| 별 (standalone) | `docs/adr/**` / `archive/adr/**` / `docs/change-plans/**` / `CLAUDE.md` / `docs/orchestrator-playbook.md` / `templates/**` (**6-scope** — `별` standalone false-positive carrier 분리로 `docs/inter-plugin-contracts/**` 등 확장 scope 는 배제하되, `archive/adr` = ADR 실위치라 CFP-2661 D1 이 lint scope union-ADD → ADR-064 Amendment 15/CFP-1561 이 SSOT 표기 5→6 정합. ADR-064 Amendment 4 §Amendment 결정 6 + Amendment 15) |

> **per-word scope decoupling 동기**: scope 확장 (5 → 전체) 시 `별` standalone 어휘를 동일 scope 에 두면 `각 packet 별` / `tier 별` / `별 layer` 등 한자어 `別` / 분류 접미사 `~별` 정당 사용이 expanded scope (특히 `docs/inter-plugin-contracts/**`) 에서 false-positive 로 증폭된다. **이는 expanded scope 도입의 known collateral** (silent bug 아님 — documented expected state). `별` 은 **6-scope**(5 영역 + `archive/adr/**` = ADR 실위치, CFP-2661 D1 union-ADD, ADR-064 Amendment 15/CFP-1561 formalize)이되 `docs/inter-plugin-contracts/**` / `CHANGELOG.md` 등 박제 expanded scope 는 여전히 **배제**(박제보다 narrow) = §1 scope 위반 차단 + Amendment 4 carrier 분리 정합. (ADR-064 Amendment 5 §Amendment 결정 2 + Amendment 15 / `docs/domain-knowledge/domain/governance-principle/wording-discipline-enforcement.md` §규칙 5 와 3곳 mirror.)

**예외 채널**: `hotfix-bypass:wording-dictionary` label (ADR-024 Amendment 3 per-entry namespace 정합) + PR description `### Bypass reason` 본문 의무.

### Amendment 3 (CFP-1060) — `별 + carrier-noun` hand-off vocabulary exemption (Wave 1 declarative)

`별` standalone forbid-list 의 의도된 hand-off vocabulary pattern exemption codify. ADR / Story file 안 `별 sub-CFP` / `별 carrier` / `별 session` / `별 Story` / `별 Issue` / `별 PR` / `별 lane` / `별 sub-Epic` / `별 Epic` / `별 Wave` 등 carrier-noun 결합 = 의도된 "out of scope, separate carrier" hand-off vocabulary. CFP-1041 carrier evidence — declarative SSOT 13+ occurrence (ADR-085 + Story file). DesignReview F-DR-1041-3 P2 INFORMATIONAL 권고 (b) bypass channel 채택 = bypass-as-design pattern.

**규칙** (Wave 1 declarative-only): `별\s+(sub-CFP|carrier|session|Story|Issue|PR|lane|sub-Epic|Epic|Wave|layer|sub-axis|sub-CFP carrier|sub-Story)` 패턴 = forbid-list exempt (semantic = "별도의 N" 의도된 hand-off). 본 패턴 외 standalone `별` (예: "별 layer 만" 자체) = forbid-list 유지.

**Wave 2 mechanical lint update (이행 완료 — CFP-2154)**: CFP-2154 (PR #2155, merge 8b67fc14, 2026-06-11) 가 `scripts/check-wording-dictionary.sh` 에 본 선언 regex 의 verbatim exemption pre-screen 으로 wire 완료 (`--self-test` 12 case 포함). 선언문(본 §규칙)이 SSOT — script 는 verbatim mirror (noun list 임의 확장 금지).

**Backward-compat**: 기존 `hotfix-bypass:wording-dictionary` label 사용 carrier 유지. Wave 2 wire 완료 (CFP-2154) 로 의도된 hand-off vocabulary 패턴은 자동 PASS — 신규 PR 은 label 채택 불요.

| 어휘 | 평문 정의 (사용자에게 보이는 의미) | 권장 대체 | 도입 CFP |
|---|---|---|---|
| 박제 | codeforge family 자체 신조어. 의미: "결정을 못 박듯 명문화 / 확정 / 기재" 다층 의미. 사용자 발화 verbatim (Issue #610): "아니 니가 쓰는 표현이다. 나는 그 표현이 뭔지 모르겠다고". | "명시" / "확정" / "기재" — 맥락에 맞게 선택 | CFP-610 |
| 못 박기 | 결정 noise — 미합의 상태에 사용 시 가짜 합의 인상. 한국어 형태 변화 처리 의무 (못박기 / 못박는 / 못 박았다 등) | "확정" / "결정 종결" | CFP-610 |
| pin | 영어 jargon — 한국어 native 사용자 의미 불투명. 일반 영어 어휘 false-positive risk ("pin to top" 등) 있으므로 lint 는 word-boundary regex + 5 scope 한정 + blockquote exempt 로 완화. | "고정" / "확정" | CFP-610 |
| freezing | 영어 jargon — 한국어 native 사용자 의미 불투명. 외부 인용 (blockquote `>` prefix) 영역 exempt. | "동결" / "변경 차단" | CFP-610 |
| 별 (standalone) | native Korean reader 의미 confusion — standalone `별` 의 native 의미 = "star" (天文 / 별자리 / 별빛). codeforge family doc 안 의도된 의미 = 한자어 `別` ("separate" / "another"). 두 의미 가 동일 character form 으로 collision — cold reader 가독성 영역. CFP-620 Epic 진행 세션 (Issue #620) live evidence. | "별도" / "별개" / "별 도리" / "또 다른" / "또 하나의" / "추가" / "신규" — 의미 영역에 맞게 선택 | CFP-672 |

> **시점 2 entry cap = 5 어휘** (Amendment 1 시점, 2026-05-14). Amendment 2 (CFP-610, 2026-05-13) 4 어휘 + Amendment 4 (CFP-672, 2026-05-14) 5번째 어휘 `별` 추가. 추가 entry 도입 = 새 CFP 의무 (ADR-064 §결정 5 CFP scope unitary 정합 — scope creep 차단).

## 카테고리 (b) — 사용 허용 + 평문 정의 동반 의무

codeforge 식별자 어휘. **사용 금지 아님** — 단 등장 시 inline 평문 정의를 동반해야 한다.

예시 형식: `normative ("강제 규칙")` / `sibling sync ("관련 다른 plugin 동시 갱신")`

정의 누락 시: lint advisory warning (exit 0 + console warn — baseline 폭증 risk 완화, 카테고리 (a) 와 별 동작).

| 어휘 | 평문 정의 | 도입 CFP / ADR |
|---|---|---|
| normative | "강제 규칙" — 모든 codeforge 작업이 따라야 하는 규범 | ADR-064 (CFP-610 dictionary 등록) |
| sibling sync | "관련 다른 plugin 동시 갱신 의무" — codeforge family 7 plugin 간 mirror 정합 | ADR-010 (CFP-610 dictionary 등록) |
| kind:contract | "다른 plugin 과의 데이터 교환 표준 (sibling sync 의무)" — `kind:registry` 와 구분 | ADR-008 (CFP-610 dictionary 등록) |
| ratchet | "evidence-gated symmetric ratchet — 강화·약화 양방향 허용 + 양방향 evidence 의무" — ADR amendment symmetric rule. forbid-list 축소 / sequential 강제 사유 확장 등 약화 방향 = sunset_justification 의무 | ADR-058 §결정 5 + ADR-064 §결정 7 (CFP-610 dictionary 등록) |
| mirrored field | "여러 file 에 동시 존재 + 변경 시 lockstep sync 의무 field" — marketplace ↔ plugin.json `name`/`version`/`description`/`author` 가 대표 예 | ADR-063 (CFP-610 dictionary 등록) |

> **5개 cap** (Amendment 2 시점, 2026-05-13). 추가 entry 도입 = 별 CFP 의무 (scope creep 차단). 카테고리 (b) lint = advisory-only — baseline 폭증 risk 완화 (spec §4.2.1 FeasibilityAgent 영역).

## 사용 규칙

- **카테고리 (a) 어휘**: 사용 시 lint warning (`scripts/check-wording-dictionary.sh`). PR 머지 차단 안 함 (warning tier, ADR-060 §결정 5). 정당 사용 = `hotfix-bypass:wording-dictionary` label + PR description `### Bypass reason` 의무.
- **카테고리 (b) 어휘**: 사용 가능. 단 inline 평문 정의 동반 필수. 정의 누락 시 advisory warning (exit 0).
- **lint 적용 영역 (per-word scope decoupling — ADR-064 Amendment 5 / CFP-750)**: 어휘별 독립 — `박제` / `못 박기` / `pin` / `freezing` = `docs/**` + `CLAUDE.md` + `CHANGELOG.md` + `templates/**` (expanded scope) / `별` standalone = `docs/adr/**` / `archive/adr/**` / `docs/change-plans/**` / `CLAUDE.md` / `docs/orchestrator-playbook.md` / `templates/**` (**6-scope** — archive/adr CFP-2661 D1 union, ADR-064 Amendment 15/CFP-1561; `docs/inter-plugin-contracts/**`·`CHANGELOG.md` 배제 = 박제보다 narrow). 카테고리 (b) advisory = 박제 expanded scope 와 동일 영역.
- **behavioral directive 영역** (Orchestrator user-facing dialog text turn): mechanical enforce 미시도. retro audit signal 만 (PMOAgent retro file §wording-discipline 표).
- **외연 허용**: 본 dictionary 본문 자체 / 사용자 발화 verbatim 인용 영역에서 금지 어휘 등장은 허용 (EXEMPT_PATHS 처리).

## 신규 entry 추가 절차

1. **별 CFP brainstorm 의무** — scope creep 차단 (ADR-064 §결정 5 CFP scope unitary 정합)
2. **ADR-064 Amendment N 작성** — 본 dictionary entry 추가 + `amendment_log` row append
3. **lint workflow 정합 확인** — 기존 doc 안 신규 어휘 발생 시 grep sweep PR 동반 의무 (CFP-610 Story 3 패턴 차용)
4. **carrier-bootstrap-check.yml 정합 verify** — 5 표준 prefix (adr/contract/policy/workflow/script)
5. **카테고리 (a) 추가 시**: ADR-064 §결정 2 forbid-list 표 + lint script `WORD_TARGETS` associative array (어휘 entry + per-word scope) lockstep 갱신 의무
6. **카테고리 (c) 추가 시 (ADR-071 §결정 19 / CFP-1764 Amendment 4)**: ADR-071 §결정 19 본문 동반 (codename → 평이 어휘 mapping table). closed 15 cap = 시점 1 baseline (Amendment 4). 신규 어휘 도입 = 별 CFP 의무 (ratchet extensibility, ADR-058 §결정 5 sunset_justification + ADR-064 §결정 7 evidence-gated symmetric ratchet 정합).

## 카테고리 (c) — codename → 평이 어휘 1:1 mapping (mid-turn glossary lookup SSOT)

ADR-071 §결정 19 (Amendment 8, CFP-1764) 의 SSOT. Orchestrator 가 agent burst output 을 사용자 메시지로 합성할 때 (mid-turn paste-and-translate) 의무 lookup. 카테고리 (a) forbid 와 별 — 본 카테고리는 **사용 금지 아님**, 사용자 dialog 영역에서 **평이 어휘로 1:1 치환 또는 평문 풀이 동반 의무**.

| # | codename | 평이 어휘 (1:1) | 비고 |
|---|----------|----------------|------|
| 1 | Story | 작업 단위 | codeforge SDLC 1 단위 |
| 2 | carry / carry-over | 이어 옮기다 / 다음으로 옮겨감 | 결정 / 정보 전달 |
| 3 | drift | 원본과 어긋남 / 이탈 | repo / file 일관성 깨짐 |
| 4 | spec | 명세서 | brainstorm 산출물 |
| 5 | scope manifest | 변경 범위 목록 | PR scope 명시 |
| 6 | ADR | 결정 기록 | Architecture Decision Record |
| 7 | Amendment | 수정안 / 후속 수정 | 기존 ADR 후속 결정 |
| 8 | sub-agent / agent | 부속 작업자 / 작업자 | spawn 단위 |
| 9 | lane | 작업 영역 (또는 영문 유지) | 8 lane plugin family |
| 10 | Phase 1 / Phase 2 | 1차 단계 / 2차 단계 | PR split |
| 11 | Layer N | N층 / N단계 | ADR-071 cognitive enum |
| 12 | sub-mechanism | 부속 매커니즘 | ADR-071 §결정 4 |
| 13 | mid-turn | 발화 도중 / 응답 도중 | Amendment 8 핵심 |
| 14 | forcing function | 강제 매커니즘 | governance ratchet |
| 15 | ratchet | 강화 방향 고정 | sunset asymmetry |

> **시점 1 entry cap = 15 codename** (Amendment 4 시점, 2026-05-27). 신규 어휘 도입 = 별 CFP 의무 — ratchet extensibility, ADR-058 §결정 5 sunset_justification + ADR-064 §결정 7 evidence-gated symmetric ratchet 정합.

### 적용 규칙

1. **Scope**: 사용자 dialog turn (Orchestrator 직접 발화) 영역만. ADR / spec / change-plan / Story file 등 governance artifact 영역 = scope 외 (codename 자연 사용).
2. **mid-turn forcing function**: ADR-071 §결정 2(a) frame mode step 4 (message 작성) 직전 step 3 cognitive 단계 — "glossary lookup 필수 실행" (codename 발견 시 평이 어휘 치환 또는 평문 풀이 동반).
3. **Mechanical layer (Story-2 carrier)**: `scripts/check-codename-glossary-lookup.sh` 가 PR diff scan 시 본 카테고리 (c) entry 의 codename 발견 + 평이 풀이 동반 부재 시 warning 발화 (`hotfix-bypass:codename-glossary-lookup` label 예외 채널). Story-2 = 75번째 hotfix-bypass family member 신설 + 23번째 evidence-checks-registry warning-tier entry 신설 carrier.
4. **Consumer false positive handling**: consumer project (mctrader-hub 등) 가 동일 codename 을 비즈니스 용어로 사용하는 경우 (예: "drift" = 포트폴리오 변동 감지), consumer overlay `jargon_filter_exempt_vocabulary: [...]` field 로 exempt 선언 — 별 follow-up CFP carrier (본 Amendment 8 scope 외).
5. **외연 허용**: 본 dictionary 본문 자체 / 사용자 발화 verbatim 인용 영역 / ADR / spec / change-plan / Story file 등 governance artifact 영역에서 codename 자연 사용 허용 (EXEMPT_PATHS 처리, 카테고리 (a) 와 동일 외연 정책).
6. **mid-turn lookup ≠ Layer 2 declare**: 카테고리 (c) lookup 시점은 발화 작성 중 (mid-turn, frame mode step 3). ADR-071 §결정 3 Layer 1 (preamble pre-turn) / Layer 2 (declare post-turn) 와 시점 disjoint — 5번째 cognitive layer 신설 아님 (§결정 12 invariant 보존).
