---
template: epic-results
version: 1.0
date: 2026-05-04
introduced_by: CFP-83
related_adrs:
  - ADR-020 (Cross-repo Epic 패턴 + Amendment 1)
  - ADR-022 (Sonnet decider)
  - ADR-025 + Amendment 1 (Stop discipline + Epic-level continuity)
---

# EPIC-RESULTS template (CFP-83)

## 사용 위치 및 시점

- **위치**: [`docs/doc-locations.yaml`](../docs/doc-locations.yaml) `epic_results` row 참조 ([ADR-041](../docs/adr/ADR-041-doc-location-registry.md)) — Mode A → owner repo root / Mode B/C → hub repo root / dogfood (codeforge family) → `<internal-docs>/<plugin-folder>/retros/EPIC-RESULTS-<EPIC_KEY>.md`
- **시점**: Epic close PR 동반 작성 (Phase N+1 close PR 의 doc artifact)
- **작성자**: PMOAgent (Cross-cutting) self-write — codeforge-pmo lane plugin owner path
- **mctrader 사용 사례**: `mctrader-hub/EPIC-RESULTS-MCT-{12,18,25,32,37}.md` 5건 (실제 emergent pattern, 본 template 화 source)

본 template = 13 섹션 구조. 모든 섹션 의무. N/A 시 "N/A — <사유>" 명시.

---

## EPIC-RESULTS Body 구조

```markdown
# Epic <EPIC_KEY> — <Title>

**Closed**: <YYYY-MM-DD>
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
```

## 작성 의무 사항 (CFP-83 신규)

본 template 의 §9 (CI iteration 통계 + 사용자 stop trigger) + §10 (PR gate evidence) + §12 (debut-audit metric) 는 mctrader 데뷔 audit Issue [#181](https://github.com/mclayer/codeforge-internal-docs/issues/) P1-1 finding 에서 신설:

- **§9 사용자 stop trigger 횟수**: ADR-025 + Amendment 1 (CFP-73 / CFP-80) stop discipline 의 정량 audit. 합법 stop whitelist 5종 외 stop 발생 시 `policy_violation` defect 추적.
- **§10 PR gate evidence**: 향후 audit 시 GitHub API 라벨 verify 가 막혀도 reproducibility 확보 (Issue #181 P1-5 partial 해소).
- **§12 debut-audit metric**: consumer 첫 cross-repo Epic 시 plugin-codeforge 측 추가 finding 정량 추적 (CFP-60 + ADR-021).

## 사용 절차

1. PMOAgent 가 Epic close PR 생성 시 본 template 복사 → `EPIC-RESULTS-<EPIC_KEY>.md` (Epic owner repo root)
2. 모든 §1~§14 섹션 fill-in. N/A 시 사유 명시.
3. Epic close PR commit message 에 `Epic close: <EPIC_KEY> — <total PRs> PRs across <N> repos` 명시
4. PR merge 후 PMOAgent retro 작성 시 본 EPIC-RESULTS evidence pack 으로 사용

## 관련 ADR / contract

- [ADR-020 + Amendment 1](../docs/adr/ADR-020-cross-repo-epic-pattern.md) — cross-repo Epic 패턴 + Mode A/B + Joint-phase
- [ADR-022](../docs/adr/ADR-022-sonnet-review-verdict-decider.md) — §7 Sonnet decider trigger 분류 source
- [ADR-025 + Amendment 1](../docs/adr/ADR-025-stop-discipline-non-whitelist-as-defect.md) — §9 stop trigger metric source
- [decision-packet-v2.1](../docs/inter-plugin-contracts/decision-packet-v2.md) — §7 Sonnet decider 결정 schema
- [fix-event-v1](../docs/inter-plugin-contracts/fix-event-v1.md) — §9 CI iteration ↔ FIX Ledger relation
