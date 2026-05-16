---
kind: registry
registry: debut-audit-triage
version: "1.0"
status: Active
canonical_repo: mclayer/plugin-codeforge
canonical_path: docs/inter-plugin-contracts/debut-audit-triage-v1.md
date: 2026-04-15
authors:
  - CFP-60 (mctrader 데뷔작 mechanism)
related_adrs:
  - ADR-021 (phase-gap measurable signal — #2 카테고리 detection backing)
related_files:
  - docs/inter-plugin-contracts/label-registry-v1.md (audit:* + category:* label v1.1)
  - scripts/check-debut-audit-signals.sh (R1-R4 detection — Phase 2)
  - scripts/bootstrap-debut-audit-labels.sh (9 label 등록 — Phase 2)
---

# Debut-audit Triage v1

Consumer 데뷔 평가 (mctrader debut 등) Codex 평가 7 카테고리의 owner agent 트리아지 룰.

## 1. 목적

mctrader 등 신규 consumer 의 codeforge 사용 첫 사례 ("데뷔작") 진행 시 Codex 평가가 발견하는 codeforge gap 을 mclayer/plugin-codeforge issue 로 등록할 때 owner agent 와 처리 경로를 mechanical 결정.

## 2. Schema (카테고리 트리아지 표)

| # | 카테고리 (label) | Owner agent | 처리 경로 ((b) WARN / (c) FAIL) |
|---|---|---|---|
| 1 | `category:lane-progression` | PMOAgent | playbook §3 보완 CFP / lane retrospective |
| 2 | `category:agent-gap` | ArchitectPL | 신규 agent ADR + lane plugin CFP / 책임 매트릭스 row 추가 / phase 분리·통합 ADR. **R1-R4 measurable signal ([ADR-021](../adr/ADR-021-phase-gap-measurable-signal.md))** detection trigger 시 발화 |
| 3 | `category:decision-table` | wrapper Orchestrator | CLAUDE.md decision table 추가 CFP |
| 4 | `category:deputy-mandate` | ArchitectPL | 6 SubAgent matrix 확장 CFP (CFP-46 패턴) |
| 5 | `category:workflow-invariant` | wrapper Orchestrator | 신규 workflow + scripts/ CFP |
| 6 | `category:template` | owner agent (Change Plan = ArchitectAgent / ADR = ArchitectAgent / Story = wrapper) | templates/ 추가 CFP |
| 7 | `category:contract-schema` | producer lane plugin | contract version bump CFP |

## 2.1 9-label 전체 매핑 (label-registry-v1.1)

데뷔 평가 발견 Issue 에는 **두 prefix label 동시 부착 의무**:

| Prefix type | Label | 역할 | Mutually exclusive? |
|---|---|---|:-:|
| **audit:** (어느 평가 source 인가) | `audit:debut-eval` | 일반 consumer 데뷔 평가 | No (audit:* 는 source 표시) |
| | `audit:from-mctrader-debut` | mctrader 데뷔 평가 (첫 사례) | No |
| **category:** (어느 카테고리 인가, §2 표 참조) | `category:lane-progression` | #1 | **Yes** (mutually exclusive) |
| | `category:agent-gap` | #2 | **Yes** |
| | `category:decision-table` | #3 | **Yes** |
| | `category:deputy-mandate` | #4 | **Yes** |
| | `category:workflow-invariant` | #5 | **Yes** |
| | `category:template` | #6 | **Yes** |
| | `category:contract-schema` | #7 | **Yes** |

**총 9 label = 2 audit:* + 7 category:***. 매 Issue 부착 = `audit:<source>` 1개 + `category:<해당>` 1개 (같은 카테고리 다중 부착 금지).

`category:agent-gap` 발견은 [ADR-021](../adr/ADR-021-phase-gap-measurable-signal.md) R1-R4 measurable signal trigger 시 발화 — `scripts/check-debut-audit-signals.sh` 자동 detection (Phase 2).

## 3. 항목 (Audit prefix 의미 요약)

- `audit:debut-eval` — 일반 consumer 데뷔 평가 (mctrader 외 다른 consumer 도 사용 가능)
- `audit:from-mctrader-debut` — mctrader 데뷔 평가 (첫 사례, scope 제한 명시)

## 4. 변경 규칙 (Issue 등록 절차 + label SemVer)

본 registry v1.x append-only:
- 신규 카테고리 추가 = minor bump (v1.0 → v1.1) — `category:*` label registry 동시 갱신 의무 ([label-registry-v1.md](label-registry-v1.md))
- 카테고리 mutually-exclusive invariant 변경 = major bump (v2.0 BREAKING per ADR-008)
- audit prefix 추가 = minor bump

### Issue 등록 절차

Codex 평가 결과 (b) WARN 또는 (c) FAIL 발견 시:

1. owner agent (또는 wrapper Orchestrator) 가 `mclayer/plugin-codeforge` Issue 생성
2. 두 prefix label 부착: `audit:from-mctrader-debut` (또는 `audit:debut-eval`) + `category:<해당>`
3. Issue body = Codex 평가 발췌 + CFP-NN proposal draft (제목 / 결정 / 거부된 대안 outline)
4. 후속 처리는 §2 표 의 "처리 경로" column 따라

## 5. 비차단 원칙

데뷔 평가 발견은 **mctrader 작업 진행 비차단**:
- codeforge 개선 backlog 는 wrapper repo 별도 Story (CFP-NN)
- mctrader Epic / Story 진행 속도 우선
- (c) FAIL 발견도 즉시 차단 X — issue 등록 후 mctrader 진행 재개

## 6. Detection 자동화 (Phase 2)

`scripts/check-debut-audit-signals.sh` 가 ADR-021 의 R1-R4 룰 mechanical detection. 매 Story Phase 2 PR merge 직후 실행 → finding 시 본 트리아지 표 따라 owner agent triage.
