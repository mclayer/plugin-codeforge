---
adr_number: 48
title: CI-native 테스트 실행 — TestAgent 제거 + SecurityTestPL opt-in (CFP-317)
status: Accepted
category: architecture
date: 2026-05-09
carrier_story: CFP-317
related_adrs:
  - ADR-023  # Lane plugin lifecycle
  - ADR-008  # Inter-plugin contract versioning
  - ADR-039  # Orchestrator subagent default
  - ADR-073  # Amendment 2 cross-ref — merge_transition sentinel polling 무약화 (본 ADR Amendment 2 (b))
  - ADR-113  # Amendment 2 cross-ref — admin merge pre-flight gate interface (본 ADR Amendment 2 (d) stuck fallback)
supersedes: null
superseded_by: null
amends: null
amended_by: CFP-2214  # Amendment 2 — CI gate 대기 규칙 개정 (Amendment 1 = ADR-055)
amended_date: "2026-06-13"
is_transitional: false
---

# ADR-048: CI-native 테스트 실행 — TestAgent 제거 + SecurityTestPL opt-in

## 상태

Accepted — CFP-317 (2026-05-09)

## 컨텍스트

codeforge 7-lane 중 두 lane이 GitHub CI로 대체 가능한 역할을 수행하고 있었음:

1. **구현 테스트 lane**: TestAgent가 consumer overlay `run-tests.sh`를 호출하나, 이 명령은 GitHub CI와 동일. 테스트 코드도 없는 상태에서 실행 에이전트만 있는 구조는 본말이 전도됨.
2. **보안 테스트 lane**: 1차 layer(Dependabot/CodeQL/Secret Scanning)는 이미 GitHub native. 2차 layer AI 분석은 solo/내부 시스템 consumer에게 과도한 overhead.

첫 번째 consumer(mctrader)는 내부 네트워크 전용 시스템이며 GitHub Actions CI 워크플로가 전무한 상태. codeforge가 테스트를 "실행"하기 전에 테스트를 "개발"하는 역할을 강화해야 함.

## 결정

### §결정 1: 구현 테스트 lane 제거 — QADeveloperAgent가 test.yml 작성

TestAgent / StatefulTestAgent spawn 폐지. QADeveloperAgent 의무 확장:
- 기존: 테스트 코드(`tests/`) 작성
- 추가: `.github/workflows/test.yml` 생성 또는 갱신 (consumer `project.yaml` `tests.runner` 기반)
- 추가: performance baseline 파일 생성/갱신

### §결정 2: CI gate — Orchestrator inline polling

> **[Amendment 2 (CFP-2214) supersede]** — 아래 원문 중 `gh pr checks <PR_NUMBER> --watch` (전체 검사 전경 blocking 대기) + "최대 30분 timeout" 절차는 Amendment 2 로 대체: required-only (`--required --watch --fail-fast`) + 백그라운드 비블로킹 watch + stuck admin-merge fallback. PASS/FAIL 분기 구조는 유지. 원문은 이력 보존.

구현 리뷰 PASS 후 Orchestrator가 `gh pr checks <PR_NUMBER> --watch` 실행 (최대 30분 timeout). read-only inline whitelist 예외 적용 (ADR-039 §결정 Inline whitelist 정합).

- PASS + `lanes.security_ai: false` (default) → merge gate 진입
- PASS + `lanes.security_ai: true` → SecurityTestPL spawn
- FAIL → `gh run view --log-failed` 로그 수집 → DeveloperPL 1차 진단 → ArchitectPL 최종 판정 → FIX loop

### §결정 3: SecurityTestPL opt-in 격하

SecurityTestPL은 기본 미spawn. `project.yaml` `lanes.security_ai: true` 설정 시에만 활성. agent 파일은 codeforge-review plugin 내 보존 (삭제 안 함). `gate:security-test-pass` 라벨은 `security_ai: true` consumer에서만 필수 게이트.

### §결정 4: codeforge-test plugin deprecated (ADR-023 lifecycle)

`codeforge-test` plugin을 Deprecated 선언. `test_verdict` contract v1을 Archived. consumer overlay `run-tests.sh` / `run-perf.sh` 파일은 더 이상 필요 없음.

### §결정 5: 7-lane → 5-lane + CI gate

공식 lane 아키텍처:
```
요구사항 → 설계 → 설계리뷰 → 구현 → 구현리뷰 → [CI gate]
```
보안 테스트 lane은 `security_ai: true` consumer에서만 선택적으로 추가.

## 결과

### 긍정적

- 테스트 코드 개발이 codeforge의 1st-class 책임이 됨 (실행 전 작성 선행)
- consumer가 codeforge 없이도 CI로 테스트 자동 실행 가능
- 7-lane overhead 감소 — 특히 solo/내부 시스템 consumer에서 실질적 단순화
- security AI overhead를 opt-in으로 격하해 소규모 consumer 진입장벽 완화

### 부정적/트레이드오프

- `test_verdict` typed contract 소멸 → FIX routing이 `gh` raw 출력 파싱 의존
- `gh pr checks` polling = 최대 30분 대기 가능 (CI 실행 시간 포함) — Amendment 2 (CFP-2214) 로 해소: required-only 백그라운드 watch (실측 required 6종 = PR open 후 15~30초)
- SecurityTestPL 사용 consumer는 `project.yaml` 명시적 opt-in 필요

## 해소 기준

N/A — permanent policy

## 관련 파일

- CLAUDE.md: 7-lane → 5-lane 선언 + 레인 표 수정
- `docs/project-config-schema.md`: `lanes.security_ai` 필드 추가
- `docs/consumer-guide.md`: overlay 파일 제거 + opt-in 섹션 신설
- `docs/orchestrator-playbook.md`: CI gate 절차 추가
- `templates/github-workflows/phase-gate-mergeable.yml`: security_ai 조건부 heuristic
- `docs/inter-plugin-contracts/test-verdict-v1.md`: status Archived
- `plugin-codeforge-test`: Deprecated 선언 (구 lane repo — 현 `plugins/codeforge-test/`, repo 삭제됨 2026-06-12)

---

## Amendment 1 — codeforge-test 통합테스트 전용 부활 (CFP-367 / ADR-055)

**날짜**: 2026-05-10

### 변경 사항

**§결정 4 변경**: ~~codeforge-test plugin deprecated~~ → **codeforge-test plugin 통합테스트 전용 부활**
- StatefulTestAgent: deprecated 유지
- IntegrationTestAgent: 신규 추가 (ADR-055 §결정 3)
- `test_verdict` contract: v1(Archived 유지) + v2(Active, ADR-055 §결정 6)

**§결정 5 변경**: ~~5-lane + CI gate~~ → **6-lane + CI gate**

```
요구사항 → 설계 → 설계리뷰 → 구현 → 구현리뷰 → [CI gate] → **통합테스트** → 보안테스트(opt-in)
```

### 원 결정 유지

§결정 1 (QADeveloperAgent test.yml 의무), §결정 2 (CI gate inline polling), §결정 3 (SecurityTestPL opt-in)은 변경 없음.

---

## Amendment 2 — CI gate 대기 규칙 개정: required-only + 백그라운드 비블로킹 watch + stuck admin-merge fallback (CFP-2214)

**날짜**: 2026-06-13

### 배경 (문제 + 실측)

§결정 2 원문 (`gh pr checks <PR_NUMBER> --watch`, 최대 30분 timeout) 은 merge readiness 와 무관한 비-required 검사까지 전경(foreground) blocking 대기해 매 PR 마다 수 분의 세션 중단을 만들었다 (1 Story = 2+ PR 이므로 누적 큼). 실측 (2026-06-12, PR #2205/#2194/#2187/#2186 statusCheckRollup 타임라인):

| 측정 항목 | 값 |
|---|---|
| merge 를 실제로 차단하는 required 검사 | 6종뿐 (wrapper branch protection 6-tuple — CLAUDE.md 표) |
| required 6종 완료 시점 | PR open 후 15~30초 |
| 전체 검사 대기 시 추가 지연 | CodeQL ~50s, bootstrap-labels ~110s |
| 오인 대기 극단 | retro-check ~308s — merge 후(pull_request closed) trigger + sleep 300 내장 (ADR-045 D-1 grace, retro-mandatory.yml L152-156) |

### 변경 사항 (§결정 2 대기 절차 대체 — 4항)

**(a) required-only 대기**: CI gate 판정 = `gh pr checks <PR_NUMBER> --required --watch --fail-fast`. 전체 검사(비-required, warning tier) 완료 대기 금지 — 비-required 검사는 merge 차단 권한 없음 (사후 red 는 기존 bypass-counter / 정비 경로 무변경).

**(b) 백그라운드 비블로킹 watch**: watch 는 Bash `run_in_background` 로 실행 — 세션 즉시 자유, 명령 종료 시 harness 자동 재호출 → PASS 시 merge 진행. 원문 "최대 30분 timeout, 초과 시 사용자 보고 후 대기" 절차 삭제. 전경 blocking watch 금지. **merge 직전 [ADR-073 Amendment 2](ADR-073-orchestrator-verify-before-assert.md) `merge_transition` sentinel polling 의무는 그대로 유지** (백그라운드 재개 시점에 수행) — 본 항은 watch 형태 변경이며 verify-before-assert 약화 아님. watch PASS 와 merge 실행 사이 race (origin/main 이동 등) 의 최종 merge 권위 = ADR-073 Amd 2 `merge_transition` sentinel — sentinel 미통과 시 watch PASS 무효, 재검 후 진행 (보강: CFP-2219, codex P2 advisory — 해석 여지 축소 정정, 신규 결정 아님).

**(c) merge 후 검사 대기 금지**: merge 후 trigger 검사 (retro-check / close-blocking / retry-state-machine 등 pull_request closed·cron 계열 — retro-check 는 sleep 300 내장, ADR-045 D-1) 는 merge·다음 단계 진행과 무관 — 명시적 대기 금지.

**(d) stuck fallback 양성화**: required check 가 5분+ pending/expected stuck → 해당 run 1회 re-trigger (`gh run rerun <run-id>` 또는 empty-commit) → 여전히 stuck 시 admin merge (`gh pr merge --admin`) + 사후 검증 1회 (merge 후 main 에서 동일 검사 green 확인) + 사용자 결과 보고. 사후 검증 1회의 검사 집합 = merge 시점의 required check set 과 동일 — 추가/축소 없음 (보강: CFP-2219, codex P2 advisory — 해석 여지 축소 정정, 신규 결정 아님). 전 과정 자동 진행 (멈춰서 묻지 않음).

### edge 2건

- **required check 0건 repo** (branch protection 미설정 consumer): 기존 전체 watch fallback (`--required` 제거).
- **FAIL 처리 무변경**: `gh run view --log-failed` 수집 → FIX loop (DeveloperPL 1차 진단 → ArchitectPL 최종 판정) — §결정 2 원문 유지.

### 축 분리 / cross-ref

- **#1908 (flaky 자동 re-trigger 일반화) 와 축 분리** — 본 (d) 는 stuck(pending/expected 미진행) required check 의 1회 re-trigger + admin merge fallback 한정. flaky(FAIL 후 재시도) 일반화는 #1908 별도 축.
- **[ADR-113](ADR-113-admin-merge-preflight-gate.md) (admin merge pre-flight gate) interface**: (d) 의 re-trigger = ADR-113 §3.19 Step 3 (fresh commit trigger recovery) 동형, attempt cap dual scope (per-PR + per-Story ≤ 3) 유지. 단 **stuck-pending (5분+ pending/expected + re-trigger 1회 후 잔존) sub-case 한정**으로 ADR-113 Step 5 "STOP + 사용자 escalation" 을 "자동 admin merge + 사후 검증 1회 + 사용자 결과 보고" 로 대체 (해당 sub-case 는 본 Amendment 우선). 그 외 state (action_required / failure / unknown fail-closed 등) 의 ADR-113 절차 무변경.
- **ADR-073 Amendment 2 `merge_transition` sentinel**: (b) 에 명시 — 무약화.

### 전파 mirror

| 파일 | 지점 |
|---|---|
| `docs/orchestrator-playbook.md` | 스폰 시퀀스 "구현 테스트" 절 + "#### CI gate" 절 + §9.7.1 표 timing signal + §14.5/§14.6 상태 보고 예시 |
| `skills/story-epic-flow-preflight/SKILL.md` | CI gate 서술 (L21) + 레인 진입 트리거 표 |
| `skills/session-recovery/SKILL.md` | §7.3 재진입 표 `phase:구현-테스트` 행 (CFP-2198 playbook 이전분) |
| `docs/consumer-guide.md` | §7.5 CI watch 명령 패턴 (consumer mirror — `--required` + required 0건 fallback) |
| `.claude-plugin/plugin.json` | version 6.17.0 → 6.18.0 (MINOR) + marketplace.json sync (ADR-063) |

### 원 결정 유지 (Amendment 2)

§결정 1 (QADeveloperAgent test.yml 의무) / §결정 3 (SecurityTestPL opt-in) / §결정 4·5 (Amendment 1 형상) 변경 없음. §결정 2 의 PASS/FAIL 분기 구조 (security_ai 분기 + FIX routing) 유지 — 대기 형태 (required-only + 백그라운드) 와 stuck fallback 만 대체.
