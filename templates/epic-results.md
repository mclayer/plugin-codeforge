---
template: epic-results
version: 1.0
date: 2026-05-04  # KST 일자 의미 (ADR-079 §결정 2 — date-only KST 일자, Korea 고정 +9 DST 영구 부재)
introduced_by: CFP-83
related_adrs:
  - ADR-020 (Cross-repo Epic 패턴 + Amendment 1)
  - ADR-022 (Sonnet decider)
  - ADR-025 + Amendment 1 (Stop discipline + Epic-level continuity)
  - ADR-079 (KST timestamp display mandate — date:/opened_at/closed_at KST 일자 의미)
---

# EPIC-RESULTS template (CFP-83)

## 사용 위치 및 시점

- **위치**: [`docs/doc-locations.yaml`](../docs/doc-locations.yaml) `epic_results` row 참조 ([ADR-041](../archive/adr/ADR-041-doc-location-registry.md)) — Mode A/B/C → `<scope>/docs/retros/EPIC-RESULTS-<EPIC_KEY>.md` / dogfood (codeforge family) → `<internal-docs>/<plugin-folder>/retros/EPIC-RESULTS-<EPIC_KEY>.md` (Amendment 1 — CFP-288)
- **시점**: Epic close PR 동반 작성 (Phase N+1 close PR 의 doc artifact)
- **작성자**: PMOAgent (Cross-cutting) self-write — codeforge-pmo lane plugin owner path
- **mctrader 사용 사례**: `mctrader-hub/docs/retros/EPIC-RESULTS-MCT-*.md` (Amendment 1 — root → docs/retros/ 이동, consumer root clutter 해소)

본 template = 14 섹션 + §requirement-slice-mapping (G3(b) 요구 슬라이스 생존, CFP-2624/ADR-152) + §deferred (no-silent-drop 회수 착지, CFP-2541/ADR-137). 모든 섹션 의무. N/A 시 "N/A — <사유>" 명시.

---

## EPIC-RESULTS Body 구조

```markdown
# Epic <EPIC_KEY> — <Title>

**Closed**: <YYYY-MM-DD>  <!-- KST 일자 의미 — ADR-079 §결정 2 (date-only = KST 일자, `+09:00` zoned 형식 아님) -->
**Status**: Phase 1 (1 doc PR) + Phase 2~N (N implementation PRs) + Phase N+1 close PR merged. All CIs green.

<one-paragraph 요약 — domain context + key invariant 이 본 Epic 으로 충족된 점>

## §1 N child Story summary

| Story | repo | bump | CI | 비고 |
|---|---|---|:---:|---|
| <CHILD-1> (<role>) | <owner/repo> | <pre> → <post> | ✅/❌ | (선택) |
| ... |
| <CHILD-N> (<role>) | <owner/repo> | <pre> → <post> | ✅ | sealing |

## §2 Phase decomposition

| Phase | PR | scope |
|---|---|---|
| Phase 1 | <hub/owner-repo>#<N> | Epic doc + N child Story stub registration + Codex 7-area review |
| Phase 2 | <impl-repo>#<N> [+ <impl-repo>#<N>] | <foundation child Story or joint-phase narrow form ADR-020 §결정 9> |
| Phase 3..N | <impl-repo>#<N> | <each implementation child Story> |
| Phase N+1 | <hub/owner-repo>#<N> | Epic close + 본 EPIC-RESULTS doc + Story §11 finalize + Issue close |

## §3 Blocking AC (B1~Bn)

| # | AC | 충족 |
|---|---|:---:|
| B1 | <invariant 1> | ✅ (<test 명> ↔ <evidence>) |
| ... |

## §4 Calibration AC (C1~Cn) — 선택

| # | metric | 의미 | gate |
|---|---|---|---|
| C1 | <metric_name> | <definition> | <gate condition> |

(Calibration AC 없는 Epic = "N/A — pure functional 변경" 명시)

## §5 Demonstration AC (D1~Dn) — 선택

D1: <UI 또는 demo 의무 항목>. 후속 child Story 분리 시 KEY 명시.

(Demo AC 없는 Epic = "N/A — backend / infra only" 명시)

## §6 Codex review aggregate

| Story | 7-area 채택 | ADR conflict | substantive choice trigger 발생 |
|---|---:|---:|---|
| <Epic key> | 7/7 | 0/7 | <trigger e count> |
| Phase 2 priority sub-decision | <1순위 채택 / N/A> | — | — |

Phase 2~N implementation 시점 추가 review 발생 정황 정리. CFP-87 mid-implementation spec amendment PR 발생 시 본 row 에 명시.

## §7 자율 결정 요약 (Sonnet decider)

ADR-022 trigger 발화 substantive 결정 누적:

- <결정 1>: <one-line summary>
- <결정 2>: <one-line summary>
- ...

Sonnet decider Story §12 row 와 cross-reference. trigger 별 group:
- (a) substantive 다중 선택지: <count>
- (b) FIX root-cause 불일치: <count>
- (c) Codex ambiguity (option-formulation narrow): <count>
- (d-constraint) 제약 surfacing: <count>
- (e) review-verdict: <count per review iteration>

## §8 Out-of-scope (확정 거부)

본 Epic 에서 명시적으로 거부된 scope (anti-scope-creep mechanism):

- <항목 1> — <거부 사유 또는 별도 Epic 으로 분리>
- <항목 2> — ...

(향후 별도 Epic candidate 으로 §11 후속 candidate 우선순위 와 link)

## §9 CI iteration 통계 (CFP-83 신규 의무)

| PR | pushes | CI failures | root cause |
|---|---:|---:|---|
| <hub#N> Phase 1 | <N> | <M> | <fix description> |
| <impl-repo#N> Phase 2 | <N> | <M> | <fix description> |
| ... |

총 CI iteration: <N>회. **사용자 stop trigger 횟수**: <N>회 (ADR-025 / CFP-73 / CFP-80 stop discipline metric — 합법 stop whitelist 5종 외 stop = `policy_violation` defect 추적).

## §10 PR gate evidence (CFP-83 신규 의무)

audit reproducibility — gate label observation timestamp 명시:

| PR | phase | expected gate label | observed gate label | verification timestamp |
|---|---|---|---|---|
| <hub#N> Phase 1 | 설계-리뷰 | `gate:design-review-pass` | <observed> | <ISO8601> |
| <impl-repo#N> Phase 2 | 보안-테스트 | `gate:security-test-pass` | <observed> | <ISO8601> |
| ... |

(향후 audit 시 본 표 가 GitHub API 라벨 verify 의 fall-back evidence)

## §11 후속 candidate 우선순위 (Sonnet decider 채택)

본 Epic 사후 발견된 또는 deferred 된 work:

| 우선순위 | scope | 후보 Epic 또는 별도 Story | 비고 |
|:-:|---|---|---|
| 1 | <highest priority next work> | <KEY 또는 TBD> | <이유> |
| 2 | ... |

## §12 debut-audit metric (CFP-60 / ADR-021 reference) — 선택

consumer 첫 cross-repo Epic 시 추가:
- 본 Epic 진행 중 plugin-codeforge 측 추가 finding **N건**
- setup-time finding **N건** (separate Issue link)
- ADR-021 phase-gap measurable signal R<N> detection: <description>

(non-debut Epic = "N/A — not a debut audit Epic" 명시)

## §13 통계

- 신규 commit: <N> PRs × 평균 <M> commits ≈ <total>
- 신규 코드: ≈ <N> lines (src + tests, <repo> + <repo>)
- <hub-repo> PR: <N>
- <impl-repo> PR: <N> (<from-version> → <to-version>, <N> minor bumps)
- ...
- CI iteration: <N>회 (§9 와 동일)

## §14 결론

**Epic <EPIC_KEY> = <one-line domain achievement>.**

<2-3 sentences key invariant 충족 + 향후 prerequisite 영향 + deferred items 요약>

## §requirement-slice-mapping

<!-- CFP-2624 / ADR-152 §결정 5 — G3(b) Epic-close 요구-슬라이스 생존 매핑. Epic 의 각 요구 슬라이스를
     {실행 Story 매핑 | 명시적 deferral} 로 매핑해 조용한 드롭(silent drop — 예: compactor S4/S5 증발)을 차단.
     check_epic_results_slice_mapping (파일명 EPIC-RESULTS-*.md gate) 스캔 대상 — 섹션 present ∧ (≥1 well-formed
     row `slice|{story|defer}|tracking-ref` ∨ N/A-substantive) ∧ 천장 문구('완결성') present 를 fail-closed 강제.
     ★ 완결성(모든 슬라이스 열거)은 기계 강제 아님 = PMO Epic-close 감사 obligation(AC-6a declared).
     ★ disposition=defer 슬라이스는 아래 §deferred 5-column row(source: req-slice-defer)로도 착지 = 회수 게이트 도달. -->

| slice | disposition | tracking-ref |
|---|---|---|
| <요구 슬라이스 서술> | <story \| defer> | <실행 Story KEY (story) \| #NNN 또는 §deferred 착지 (defer)> |

정직 천장: 위 매핑은 각 슬라이스의 disposition 산출물 존재만 강제한다. **모든 슬라이스 열거 완결성**은 기계 강제 아님 — Epic 요구-슬라이스 인벤토리 SSOT 부재로 PMO Epic-close 감사 obligation(정직 divergence, ADR-152 §결정5).

(요구 슬라이스 분해 불가 Epic = "N/A — <사유 30자 이상, 완결성 정직 공개>" 명시. defer disposition 은 §deferred `source: req-slice-defer` row 로 착지시켜 회수 게이트 도달.)

## §deferred

<!-- CFP-2541 / ADR-137 — Epic-close triage-defer verdict + retro 서사 deferred 의 no-silent-drop 회수 착지.
     check-deferred-item-recovery.sh (_scan_retro_file, ## §deferred regex) 스캔 대상.
     source column enum: retro-narrative (retro §4/§8 서사 발생) | triage-defer (ADR-137 구현-리팩터링 triage defer verdict)
     | req-slice-defer (ADR-152 §결정6 G3(b) 요구-슬라이스 defer disposition 착지 — column 신설 아님, 값 도메인 확장). -->

| disposition | item | tracking | rationale | source |
|---|---|---|---|---|
| <tracked \| observed> | <deferred 항목 서술> | <#NNN tracking Issue \| "관찰-only"> | <이연/관찰 사유> | <retro-narrative \| triage-defer \| req-slice-defer> |

(deferred 항목 없는 Epic = "N/A — no deferred items" 명시. tracked = 추적 Issue 외부화 #NNN / observed = 관찰-only + 사유 명시. triage-defer source = ADR-137 Epic-close 구현-리팩터링 triage defer verdict anchor. req-slice-defer source = ADR-152 §결정6 G3(b) 요구-슬라이스 defer disposition anchor — scanner disposition enum{tracked,observed}만 검증, source 미검증 = scanner 무변경.)
```

## 작성 의무 사항 (CFP-83 신규)

본 template 의 §9 (CI iteration 통계 + 사용자 stop trigger) + §10 (PR gate evidence) + §12 (debut-audit metric) 는 mctrader 데뷔 audit Issue [#181](https://github.com/mclayer/codeforge-internal-docs/issues/) P1-1 finding 에서 신설:

- **§9 사용자 stop trigger 횟수**: ADR-025 + Amendment 1 (CFP-73 / CFP-80) stop discipline 의 정량 audit. 합법 stop whitelist 5종 외 stop 발생 시 `policy_violation` defect 추적.
- **§10 PR gate evidence**: 향후 audit 시 GitHub API 라벨 verify 가 막혀도 reproducibility 확보 (Issue #181 P1-5 partial 해소).
- **§12 debut-audit metric**: consumer 첫 cross-repo Epic 시 plugin-codeforge 측 추가 finding 정량 추적 (CFP-60 + ADR-021).

## 사용 절차

1. PMOAgent 가 Epic close PR 생성 시 본 template 복사 → `docs/retros/EPIC-RESULTS-<EPIC_KEY>.md` (Amendment 1 — `<scope>/docs/retros/`, ADR-041 doc-locations.yaml 기준)
2. 모든 §1~§14 섹션 fill-in. N/A 시 사유 명시.
3. Epic close PR commit message 에 `Epic close: <EPIC_KEY> — <total PRs> PRs across <N> repos` 명시
4. PR merge 후 PMOAgent retro 작성 시 본 EPIC-RESULTS evidence pack 으로 사용

## 관련 ADR / contract

- [ADR-020 + Amendment 1](../archive/adr/ADR-020-cross-repo-epic-pattern.md) — cross-repo Epic 패턴 + Mode A/B + Joint-phase
- [ADR-022](../archive/adr/ADR-022-sonnet-review-verdict-decider.md) — §7 Sonnet decider trigger 분류 source
- [ADR-025 + Amendment 1](../archive/adr/ADR-025-stop-discipline-non-whitelist-as-defect.md) — §9 stop trigger metric source
- [decision-packet-v2.1](../docs/inter-plugin-contracts/decision-packet-v2.md) — §7 Sonnet decider 결정 schema
- [fix-event-v1](../docs/inter-plugin-contracts/fix-event-v1.md) — §9 CI iteration ↔ FIX Ledger relation
