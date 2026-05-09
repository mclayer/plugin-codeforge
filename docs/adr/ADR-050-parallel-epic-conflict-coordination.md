---
adr_number: 50
title: Parallel Epic Conflict Coordination — 복수 Orchestrator 세션 충돌 조율 정책 (CFP-344)
status: Accepted
category: governance
date: 2026-05-09
carrier_story: CFP-344
related_adrs:
  - ADR-036
  - ADR-040
  - ADR-024
  - ADR-034
  - ADR-039
related_files:
  - docs/adr/ADR-RESERVATION.md
  - docs/parallel-work/section-ownership.yaml
  - templates/github-workflows/parallel-epic-conflict-check.yml
  - docs/inter-plugin-contracts/label-registry-v1.md
supersedes: null
amends: null
---

# ADR-050: Parallel Epic Conflict Coordination

## 상태

Accepted (2026-05-09) — CFP-344 carrier.

## 컨텍스트

복수 Orchestrator 세션(두 개 이상의 Claude Code 창)이 동시에 서로 다른 에픽을 진행할 때
네 가지 충돌 유형이 발생한다:

1. **ADR 번호 충돌**: 두 세션이 동시에 같은 ADR 번호로 파일 생성 (ADR-048 중복 사례 실증)
2. **소스 파일 merge 충돌**: 같은 파일을 두 PR이 동시 수정 → git conflict
3. **중앙 설정 동시 편집**: CLAUDE.md / playbook locked 섹션 동시 수정
4. **에픽 일정 간섭**: 의존성 있는 에픽이 순서 없이 병렬 진행

두 세션은 직접 통신이 불가능하므로 **GitHub가 유일한 공유 조율 채널**이다.

현재 ADR-048이 두 개 (`ADR-048-ci-native-test-execution.md`, `ADR-048-ghec-governance-as-code.md`) 공존하는 사고가 실제 발생했음 — 본 ADR 도입 동기.

## 결정

### 결정 1: ADR-RESERVATION.md — ADR 번호 원자적 예약

`docs/adr/ADR-RESERVATION.md` 파일을 ADR 번호 예약 레지스트리로 신설.
GitOpsAgent가 sequential append로 번호를 클레임. 동시 append 시 git merge의
positional conflict를 GitOpsAgent가 번호 순 re-sort로 자동 해소.

**예약 흐름**:
1. ArchitectAgent가 ADR 필요 신호 발신
2. GitOpsAgent가 ADR-RESERVATION.md 마지막 번호 + 1 append → commit
3. ArchitectAgent가 예약된 번호로 `ADR-NNN-*.md` 생성
4. ADR merge 완료 후 `status: reserved → active` 갱신

### 결정 2: Epic Scope Manifest — Issue body YAML 블록

에픽 Issue body에 `<!-- scope_manifest -->` 블록으로 예상 변경 범위를 선언.
포맷: `planned_adrs`, `planned_files`, `planned_claude_md_sections`.
Orchestrator가 Phase 1 시작 시 작성. GitOpsAgent가 다른 open 에픽과 교집합 검사.

```yaml
<!-- scope_manifest -->
planned_adrs: [50]
planned_files:
  - docs/adr/ADR-050-*.md
  - templates/github-workflows/parallel-epic-conflict-check.yml
planned_claude_md_sections:
  - "오케스트레이션 규칙"
<!-- /scope_manifest -->
```

### 결정 3: parallel-epic-conflict-check.yml — GitHub Actions 자동 감지

PR open/push 시 다른 open PR들과 파일 overlap 검사 → `conflict:*` 레이블 자동 부여.
결과는 **non-blocking** (merge 가능, 경고만). 레이블 3종:
- `conflict:file-overlap` — 파일 중복
- `conflict:adr-number` — ADR-RESERVATION.md 동시 수정
- `conflict:section-locked` — locked 섹션 동시 수정

### 결정 4: section-ownership.yaml — locked 섹션 선언

`docs/parallel-work/section-ownership.yaml`이 CLAUDE.md/playbook 섹션별
편집 정책(`append-only` / `locked`)을 선언. Actions workflow가 이 파일을 읽어
locked 섹션 동시 수정 여부를 판단.

- `append-only`: 테이블 신규 row 추가만 허용, 기존 텍스트 수정 시 `conflict:section-locked` 트리거
- `locked`: 동시 수정 시 `merge-order` 레이블 의무 + `conflict:section-locked` 트리거

### 결정 5: merge-order 레이블 프로토콜

충돌 감지 시 낮은 CFP 번호 PR = `merge-order:1`, 높은 CFP 번호 PR = `merge-order:2`.
GitOpsAgent가 `merge-order:2` PR에 rebase 지시 주석 자동 작성.

```
[GitOpsAgent] 병렬 에픽 충돌이 감지되었습니다.

merge-order:1 PR: #XXX (CFP-YYY)
충돌 파일: [목록]

해당 PR이 merge된 후 `git rebase main`을 수행하세요.
```

## 결과

### 긍정

- 파일 충돌 PR open 시점에 자동 경고 → 사람이 merge 전 인지
- ADR 번호 중복 0 (sequential append + GitOpsAgent auto-reorder)
- 중앙 설정 파일 동시 수정 패턴 가시화 (section-ownership.yaml)
- merge 순서 프로토콜 명문화

### 부정 / 비용

- ADR-RESERVATION.md 자체가 충돌 hotspot이 될 수 있음 → append-only + GitOpsAgent auto-reorder로 완화
- scope_manifest 정확도 의존 → non-blocking (false alarm 시 merge 가능)
- parallel-epic-conflict-check.yml 실행 시간 (+15~30초/PR) → acceptable

### 위험

- section-ownership.yaml 미등록 섹션 충돌 → 점진적 등록 확대로 완화
- GitOpsAgent (CFP-139) 완전 구현 전까지 merge-order 레이블은 수동 운영

## 대안 고려

| 대안 | 채택 안 한 이유 |
|---|---|
| 전용 ParallelCoordinatorAgent 신설 | 새 에이전트 = ADR + model tier 결정 비용. GitOpsAgent 확장이 충분 |
| merge-first ordering 강제 (blocking) | 병렬 작업의 장점 소멸. non-blocking warning이 적절 |
| Reservation Issue Form (cfp-reserve 패턴 확장) | ADR-RESERVATION.md sequential append가 더 가볍고 audit trail 명확 |

## 관련 파일

- [ADR-036](ADR-036-project-key-atomic-reservation.md) — CFP 번호 예약 패턴 선례
- [ADR-040](ADR-040-worktree-convention.md) — per-session 격리 선례
- [ADR-024](ADR-024-story-scoped-branch-policy.md) — branch governance
- [ADR-034](ADR-034-pre-issue-brainstorming-stage.md) — Stage 0 (Story B amendment 대상)
- [ADR-039](ADR-039-orchestrator-subagent-default-for-codeforge-modification-work.md)
- `docs/adr/ADR-RESERVATION.md` — 결정 1 구현
- `docs/parallel-work/section-ownership.yaml` — 결정 4 구현
- `templates/github-workflows/parallel-epic-conflict-check.yml` — 결정 3 구현
