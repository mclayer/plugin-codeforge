---
adr_number: 65
title: ArchitectAgent Phase 1 산출물 mechanical sync self-check 의무 (non-marketplace 영역)
status: Accepted
category: Team & Process
date: 2026-05-13
is_transitional: false
related_files:
  - CLAUDE.md
  - docs/inter-plugin-contracts/review-verdict-v4.md
related_stories:
  - CFP-393
  - CFP-411
  - CFP-438
related_adrs:
  - ADR-016
  - ADR-031
  - ADR-039
  - ADR-041
  - ADR-049
  - ADR-050
  - ADR-063
mechanical_enforcement_actions: []
---

# ADR-065: ArchitectAgent Phase 1 산출물 mechanical sync self-check 의무 (non-marketplace 영역)

## 상태

`Accepted` (2026-05-13). ADR-063 (marketplace atomic invariant) 의 non-marketplace 영역 보완.

## 컨텍스트

codeforge-design lane 의 ArchitectAgent (chief author) 가 Phase 1 산출물을 commit 직전, 사전 정의된 checklist 부재로 인해 매 Story 반복 결함이 발생했다. 이 결함들은 모두 chief author 가 "산출물 commit 직전 self-check" 로 잡을 수 있는 mechanical sync 누락이다.

### 결함 evidence (3 Story 누적)

**CFP-393 (#398) iter 1 FIX (설계-리뷰 CI lint, 3건)**:

- `scripts/bootstrap-labels.sh` ↔ `docs/inter-plugin-contracts/label-registry-v2.md` sync 누락 (CFP-33 strict check FAIL)
- CLAUDE.md L129 `docs/kpi/rate-limit-fallback.json` Phase 1 link → Phase 2 target dangling (markdown internal links FAIL)
- `docs/doc-locations.yaml` 갱신 후 `docs/doc-location-registry.md` mirror regenerate 누락 (validate FAIL)

**CFP-393 (#398) iter 3 FIX (구현 Phase 2 PR CI, 1건 — marketplace 2건은 CFP-436 분리)**:

- `templates/github-workflows/rate-limit-fallback-kpi.yml` 신규했으나 `.github/workflows/` self-app copy 누락 (invariant-check FAIL)

**CFP-411 (#411) phase-gate path 누락**:

- phase 라벨 전환 시점 / gate label attach 미흡 → phase-gate-mergeable FAIL

### 공통 root cause

- chief author 가 6 deputy 산출물 통합 후 Change Plan + ADR draft 만 write, 주변 mechanical sync 파일을 별도 checklist 로 확인하지 않음
- 매 Story 에서 동일 결함 type 재발 (label-registry / doc-locations / workflow self-app / link target / MANIFEST.yaml)
- CI lint 가 사후 감지 channel 로 동작 — Phase 1 PR commit 시점 forcing function 부재

### 기존 SSOT 의 한계

- ArchitectAgent.md 본문 §3.5 self-lint (CFP-378) = 6 deputy 산출물 input 표면 형식 / Story §1 cross-ref / 외부 입력 무결성 — **design decision input 표면 check 만**. mechanical sync (label-registry / doc-locations / workflow self-app) 영역 미포함
- ADR-063 marketplace atomic invariant = `plugin.json` / `CHANGELOG.md` / `marketplace.json` 3-file atomic — **marketplace 영역만**. label-registry / doc-locations / workflow self-app 등 non-marketplace 영역 미포함
- review-verdict-v4 schema = `pl_recommendation` 단일 final verdict — chief author self-check pass 여부 explicit marker 부재

## 결정

### 결정 1: 7-item mechanical sync self-check 의무 (non-marketplace 영역)

ArchitectAgent chief author 는 Phase 1 산출물 commit 직전 다음 7 항목 mechanical sync 검증 의무:

| # | 항목 | 검증 방법 |
|---|---|---|
| 1 | `label-registry-v2.md` 변경 시 `scripts/bootstrap-labels.sh` sync 동반 | `bash scripts/check-labels-bootstrap-strict.sh` PASS |
| 2 | `doc-locations.yaml` 변경 시 `bash scripts/check-doc-locations.sh --regen` 실행 | regenerate 후 `doc-location-registry.md` mirror diff 0 |
| 3 | 신규 `templates/github-workflows/*.yml` 시 `.github/workflows/` self-app copy 동반 | `diff -q templates/github-workflows/X.yml .github/workflows/X.yml` exit 0 (byte-identical) |
| 4 | CLAUDE.md / docs/** 내 link target 이 Phase 1 분배인지 확인 | Phase 2 file 참조 시 dangling — markdown internal link lint PASS |
| 5 | `docs/inter-plugin-contracts/MANIFEST.yaml` registries 블록 갱신 필요성 확인 | 신규 registry 도입 시 row append, MANIFEST `check-inter-plugin-contracts.sh` PASS |
| 6 | `docs/parallel-work/section-ownership.yaml` 정책 필요 시 row append | 동시 편집 영향 받는 신규 section 도입 시 row append |
| 7 | `docs/doc-locations.yaml` 신규 doc type row 필요성 확인 | 신규 doc type 도입 시 row append, `check-doc-locations.sh` PASS |

각 항목 = chief author 가 본인 Phase 1 산출물 commit 직전 self-check. NA (해당 영역 변경 없음) = 명시적 PASS 로 분류.

### 결정 2: change-plan template "Phase 1 self-check 결과" 섹션 의무화

[`templates/change-plan.md`](../../../plugin-codeforge-design/templates/change-plan.md) 에 `§13. Phase 1 산출물 self-check 결과 (ADR-065 / CFP-438)` 섹션 추가. chief author 가 7 항목 결과 (PASS / NA / FIX) 를 명시 의무.

### 결정 3: review-verdict-v4 v4.1 → v4.2 MINOR bump — `mechanical_self_check_passed: bool` 필드 추가

review-verdict-v4 schema 에 다음 optional 필드 추가:

```yaml
mechanical_self_check_passed: <bool>   # NEW (ADR-065 / CFP-438, v4.2 MINOR)
                                        # ArchitectAgent Phase 1 7-item mechanical sync self-check 결과
                                        # true = 모두 PASS 또는 NA, false = FIX 의무
                                        # 적용 lane: design lane 만 (code/security lane = optional, omit 가능)
```

ADR-008 §결정 2 "새 선택 필드 추가" = MINOR bump 정합. Runtime impact 없음 (기존 v4.1 consumer 가 본 필드 무시 가능).

### 결정 4: false 시 FIX 의무 — ArchitectPLAgent 가 ArchitectAgent re-spawn 명령

`mechanical_self_check_passed: false` 수신 시:

- ArchitectPLAgent verdict packet 의 `pl_recommendation` 을 `FIX` 로 설정
- review-verdict-v4 `findings[]` 에 mechanical 누락 항목 each row 추가 (severity P1 — `mechanical_sync_required`)
- ArchitectAgent re-spawn — 누락 항목 only 보완 후 self-check 재실행
- Story §10 FIX Ledger row append (Orchestrator monopoly, fix-event-v1 contract)

### 결정 5: marketplace 영역 self-check 는 ADR-063 SSOT — 본 ADR scope 외

marketplace mirrored field (`name` / `version` / `description` / `author`) 변경 관련 3-file atomic invariant (`plugin.json` / `CHANGELOG.md` / `marketplace.json`) = ADR-063 SSOT. 본 ADR-065 = non-marketplace 영역 7 항목 한정.

cross-ref only — 중복 codification 회피.

## 결과

### 긍정적 결과

- chief author 의 산출물 commit 직전 mechanical sync 의무 인지 강화
- 매 Story 반복 결함 (CFP-393 3건 + 1건 + CFP-411) 사전 차단
- Phase 1 PR CI lint 에 도달하기 전 chief author 가 self-detect 가능
- review-verdict-v4 v4.2 packet 에 explicit marker — Orchestrator 가 FIX routing 결정 시 명시적 signal

### 부정적 결과

- chief author overhead 증가 (산출물 commit 직전 7 항목 검증 단계)
- 7 항목 detail noise → review-pl-base.md §3 P2 finding 증가 위험 — mitigation: 7 항목 한정, mechanical fast-path 정합 (Change Plan 본문 변경 0건 항목만)
- review-verdict-v4 schema MINOR bump → sibling sync PR 의무 (canonical = `plugin-codeforge-review`, wrapper sibling)

### Trade-off

- chief author 가 한 번 더 mechanical check 수행 → 5-10 min overhead vs Phase 1 PR FIX iteration 1회 (30+ min) 차단

## 해소 기준

N/A — permanent policy

## 관련 파일

- [`CLAUDE.md`](../../CLAUDE.md) — cross-ref 추가
- [`docs/inter-plugin-contracts/review-verdict-v4.md`](../inter-plugin-contracts/review-verdict-v4.md) — v4.1 → v4.2 MINOR bump
- `plugin-codeforge-design/agents/ArchitectAgent.md` — 7-item self-check 섹션 신설
- `plugin-codeforge-design/agents/ArchitectPLAgent.md` — verdict packet `mechanical_self_check_passed` 필드
- `plugin-codeforge-design/templates/change-plan.md` — §13 Phase 1 self-check 결과 섹션
- `plugin-codeforge-review/docs/inter-plugin-contracts/review-verdict-v4.md` — canonical v4.2 MINOR bump
