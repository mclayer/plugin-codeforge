---
schema_version: "1.0"
introduced_by: CFP-610
last_updated: 2026-05-14
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
    summary: "`별 + carrier-noun` hand-off vocabulary exemption codify (Wave 1 declarative). 의도된 '별도의 N' 패턴 (별 sub-CFP / 별 carrier / 별 session / 별 Story / 별 Issue / 별 PR / 별 lane / 별 sub-Epic / 별 Epic / 별 Wave 등) = forbid-list exempt. CFP-1041 evidence (13+ occurrence declarative SSOT, DesignReview F-DR-1041-3 bypass-as-design pattern). Wave 2 mechanical lint update = 별 sub-CFP carrier deferred. ADR-064 Amendment 6 lockstep."
title: "codeforge wording dictionary — 어휘 사전 (forbid + 평문 정의 의무)"
---

# codeforge wording dictionary

codeforge 의 표현 규율 (ADR-064 §결정 2 + §결정 9) 의 어휘 SSOT.

## 개요

사용자 (한국어 native, solo dev) 가 codeforge family jargon 노출 영역에서 frustration 을 표현한 directive (Issue #610, 2026-05-13) 를 계기로 신설. 2 카테고리:

- **(a) 사용 금지 어휘 (forbid)**: 사용 시 lint warning. ADR-064 §결정 2 와 verbatim sync 의무.
- **(b) 사용 허용 + 평문 정의 동반 의무**: codeforge 식별자 어휘. 사용 가능하되 inline 평문 정의 동반 필수.

## 카테고리 (a) — 사용 금지 어휘 (forbid)

**SSOT 방향**: 본 표 = SSOT. ADR-064 §결정 2 forbid-list 표 (Amendment 2 부분) + lint script (`scripts/check-wording-dictionary.sh`) `WORD_TARGETS` associative array 가 mirror. 변경 시 lockstep 갱신 의무.

**lint 적용 영역 (per-word scope decoupling — ADR-064 Amendment 5 / CFP-750)**: 어휘별 scope 독립 (`scripts/check-wording-dictionary.sh` `WORD_TARGETS` map).

| 어휘 | lint scope |
|---|---|
| 박제 / 못 박기 / pin / freezing | `docs/**` (전체 — adr / change-plans / inter-plugin-contracts / domain-knowledge / retros / security 등 모든 sub-dir + top-level `docs/*.md`) + `CLAUDE.md` + `CHANGELOG.md` + `templates/**` (expanded scope) |
| 별 (standalone) | `docs/adr/**` / `docs/change-plans/**` / `CLAUDE.md` / `docs/orchestrator-playbook.md` / `templates/**` (5-scope 유지 — `별` standalone false-positive carrier 분리, ADR-064 Amendment 4 §Amendment 결정 6) |

> **per-word scope decoupling 동기**: scope 확장 (5 → 전체) 시 `별` standalone 어휘를 동일 scope 에 두면 `각 packet 별` / `tier 별` / `별 layer` 등 한자어 `別` / 분류 접미사 `~별` 정당 사용이 expanded scope (특히 `docs/inter-plugin-contracts/**`) 에서 false-positive 로 증폭된다. **이는 expanded scope 도입의 known collateral** (silent bug 아님 — documented expected state). `별` 5-scope 유지 = §1 scope 위반 차단 + Amendment 4 carrier 분리 정합. (ADR-064 Amendment 5 §Amendment 결정 2 / `docs/domain-knowledge/domain/governance-principle/wording-discipline-enforcement.md` §규칙 5 와 3곳 mirror.)

**예외 채널**: `hotfix-bypass:wording-dictionary` label (ADR-024 Amendment 3 per-entry namespace 정합) + PR description `### Bypass reason` 본문 의무.

### Amendment 3 (CFP-1060) — `별 + carrier-noun` hand-off vocabulary exemption (Wave 1 declarative)

`별` standalone forbid-list 의 의도된 hand-off vocabulary pattern exemption codify. ADR / Story file 안 `별 sub-CFP` / `별 carrier` / `별 session` / `별 Story` / `별 Issue` / `별 PR` / `별 lane` / `별 sub-Epic` / `별 Epic` / `별 Wave` 등 carrier-noun 결합 = 의도된 "out of scope, separate carrier" hand-off vocabulary. CFP-1041 carrier evidence — declarative SSOT 13+ occurrence (ADR-085 + Story file). DesignReview F-DR-1041-3 P2 INFORMATIONAL 권고 (b) bypass channel 채택 = bypass-as-design pattern.

**규칙** (Wave 1 declarative-only): `별\s+(sub-CFP|carrier|session|Story|Issue|PR|lane|sub-Epic|Epic|Wave|layer|sub-axis|sub-CFP carrier|sub-Story)` 패턴 = forbid-list exempt (semantic = "별도의 N" 의도된 hand-off). 본 패턴 외 standalone `별` (예: "별 layer 만" 자체) = forbid-list 유지.

**Wave 2 mechanical lint update (별 sub-CFP carrier deferred)**: `scripts/lib/check_wording_dictionary.py` (또는 `scripts/check-wording-dictionary.sh`) 안 exemption regex pre-screen 추가. 본 Wave 1 = declarative SSOT only (lint script 무변경, bypass label 계속 사용).

**Backward-compat**: 기존 `hotfix-bypass:wording-dictionary` label 사용 carrier 유지 (Wave 2 mechanical wire 후 의도된 hand-off vocabulary 영역은 자동 PASS, label 채택 불요).

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
| ratchet | "강화 방향만 허용 + 약화 차단" — ADR amendment top-down rule. forbid-list 축소 / sequential 강제 사유 확장 등 약화 방향 = sunset_justification 의무 | ADR-058 §결정 5 + ADR-064 §결정 7 (CFP-610 dictionary 등록) |
| mirrored field | "여러 file 에 동시 존재 + 변경 시 lockstep sync 의무 field" — marketplace ↔ plugin.json `name`/`version`/`description`/`author` 가 대표 예 | ADR-063 (CFP-610 dictionary 등록) |

> **5개 cap** (Amendment 2 시점, 2026-05-13). 추가 entry 도입 = 별 CFP 의무 (scope creep 차단). 카테고리 (b) lint = advisory-only — baseline 폭증 risk 완화 (spec §4.2.1 FeasibilityAgent 영역).

## 사용 규칙

- **카테고리 (a) 어휘**: 사용 시 lint warning (`scripts/check-wording-dictionary.sh`). PR 머지 차단 안 함 (warning tier, ADR-060 §결정 5). 정당 사용 = `hotfix-bypass:wording-dictionary` label + PR description `### Bypass reason` 의무.
- **카테고리 (b) 어휘**: 사용 가능. 단 inline 평문 정의 동반 필수. 정의 누락 시 advisory warning (exit 0).
- **lint 적용 영역 (per-word scope decoupling — ADR-064 Amendment 5 / CFP-750)**: 어휘별 독립 — `박제` / `못 박기` / `pin` / `freezing` = `docs/**` + `CLAUDE.md` + `CHANGELOG.md` + `templates/**` (expanded scope) / `별` standalone = `docs/adr/**` / `docs/change-plans/**` / `CLAUDE.md` / `docs/orchestrator-playbook.md` / `templates/**` (5-scope 유지). 카테고리 (b) advisory = 박제 expanded scope 와 동일 영역.
- **behavioral directive 영역** (Orchestrator user-facing dialog text turn): mechanical enforce 미시도. retro audit signal 만 (PMOAgent retro file §wording-discipline 표).
- **외연 허용**: 본 dictionary 본문 자체 / 사용자 발화 verbatim 인용 영역에서 금지 어휘 등장은 허용 (EXEMPT_PATHS 처리).

## 신규 entry 추가 절차

1. **별 CFP brainstorm 의무** — scope creep 차단 (ADR-064 §결정 5 CFP scope unitary 정합)
2. **ADR-064 Amendment N 작성** — 본 dictionary entry 추가 + `amendment_log` row append
3. **lint workflow 정합 확인** — 기존 doc 안 신규 어휘 발생 시 grep sweep PR 동반 의무 (CFP-610 Story 3 패턴 차용)
4. **carrier-bootstrap-check.yml 정합 verify** — 5 표준 prefix (adr/contract/policy/workflow/script)
5. **카테고리 (a) 추가 시**: ADR-064 §결정 2 forbid-list 표 + lint script `WORD_TARGETS` associative array (어휘 entry + per-word scope) lockstep 갱신 의무
