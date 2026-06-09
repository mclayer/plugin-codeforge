---
adr_number: 116
title: Consumer overlay 보안 화이트리스트의 멱등 후처리 주입 (reconcile-then-patch)
status: Accepted
category: governance
date: 2026-06-08
carrier_story: CFP-1716
is_transitional: false
amends: null
supersedes: null
related_adrs:
  - ADR-026  # Amendment 4 §결정 6 — ALLOWED_HUB_REPOS 화이트리스트 정책 소유 (zero-trust strict-match anchor)
  - ADR-024  # Amendment 2 §결정 A — required_status_checks 확장-only / never-reduce 화이트리스트 선례 (branch-protection contexts)
  - ADR-057  # 오인용 정정 대상 — 실제 = Orchestrator Opus mandate (확장-only 와 무관). 본 ADR 이 인용 오류를 정정
  - ADR-061  # 외부 .py 파일 분리 (heredoc 금지) — extract_allowed_hub_repos.py 정합
related_stories:
  - CFP-1716  # carrier (사후 형식화 — 구현 PR #1909 선행 GREEN)
  - CFP-795   # ADR-026 Amendment 4 §결정 6 carrier (ALLOWED_HUB_REPOS 도입)
related_files:
  - scripts/inject-allowed-hub-repos.sh
  - scripts/lib/extract_allowed_hub_repos.py
  - tests/scripts/cfp-1716/inject-allowed-hub-repos.bats
  - .github/workflows/phase-gate-mergeable.yml
  - .github/workflows/phase-gate-auto-cleanup.yml
mechanical_enforcement_actions: []   # bats 8 cases 가 mechanical 검증 (idempotent / never-reduce / dedup / format-validation). 신규 lint/sentinel 0 — 기존 phase-gate-mergeable.yml required check 가 화이트리스트 strict-match gate 보유.
---

# ADR-116: Consumer overlay 보안 화이트리스트의 멱등 후처리 주입 (reconcile-then-patch)

## 상태

Accepted (2026-06-08 KST — CFP-1716 carrier). 사후 형식화 ADR — 구현 PR #1909(`cfp-1716-allowed-hub-repos-injection`)가 선행 작성·GREEN(8/8 bats) 상태에서 설계 lane 이 결정 근거를 정식 기록.

## 컨텍스트

`ALLOWED_HUB_REPOS` = phase-gate 워크플로우(`phase-gate-mergeable.yml` + `phase-gate-auto-cleanup.yml`)의 env. cross-repo Story(dogfood-out) PR body 의 self-declared `story_uri` host+owner/repo 를 이 목록과 **strict match** 해야 phase gate 통과(zero-trust anchor, fail-closed — 정책 소유 = ADR-026 Amendment 4 §결정 6 / CFP-795).

문제:
- consumer 가 `codeforge-upgrade` 로 wrapper 워크플로우 템플릿을 reconcile 하면 `ALLOWED_HUB_REPOS` env 가 template default(`github.com/mclayer/codeforge-internal-docs`)로 **무조건 덮어써진다** → consumer 가 추가한 hub repo 가 매 reconcile 마다 소실.
- mctrader-data 에서 `,github.com/mclayer/mctrader-hub` 가 **3회 재발 손실**(mctrader-data#189/#198/#199) — 전형적 configuration drift.
- consumer overlay `phase_gate.allowed_hub_repos[]` 는 schema/문서에만 선언되어 있고 **실제 주입 메커니즘이 0개**였다(미싱 링크).

기존 ADR-024 Amendment 2 §결정 A 가 동일 class(보안 화이트리스트, overlay-driven, never-reduce)를 branch-protection `required_status_checks.contexts` 에 이미 codify — consumer 는 자기 context **추가만** 가능(core 삭제 불허). 본 ADR 은 그 패턴을 `ALLOWED_HUB_REPOS` 도메인에 두 번째로 실현한다.

### 근거 ADR 재선정 (ADR-057 오인용 정정)

구현/문서/워크플로우 주석이 모두 "ADR-057 확장-only 정합" 으로 인용했으나, **ADR-057 의 실제 결정 = Orchestrator Opus 필수화 + Sonnet→Opus rate-limit fallback** 으로 확장-only 와 무관. "확장-only / 축소 불가" 개념은 실재하나(consumer-guide §2556 overlay 일반 원칙 + ADR-024 Amendment 2 §결정 A 화이트리스트 class) ADR-057 이 소유하지 않는다.

leak 진원 = `phase-gate-mergeable.yml:16` 주석 + ADR-026 Amendment 4 §결정 6 frontmatter summary(pre-existing) → 구현/Story §1 D4 가 답습. 본 ADR 은 ADR-057 을 **amend 하지 않고**(단일 결정 응집 보존), 올바른 근거를 재확정한다. 기존 leak 정정 = 별 doc-only fix carrier(CFP-1716 Story §11.3 권고).

## 결정

### 결정 1: reconcile-then-patch (post-renderer) 멱등 후처리 주입

상위 도구(`codeforge-upgrade` reconcile)가 desired state(template default)를 덮어쓴 뒤, consumer 환경-특화 확장을 **멱등 후처리**로 다시 적용한다(GitOps post-renderer 패턴 — Kustomize overlay / Helm post-renderer 와 동형). 흐름:

1. `extract_allowed_hub_repos.py` — consumer `project.yaml` 의 `phase_gate.allowed_hub_repos[]` 를 PyYAML `safe_load` 로 추출(field 부재 = exit 0 no-op / parse error = exit 1).
2. `inject-allowed-hub-repos.sh` — `.github/workflows/*.{yml,yaml}` 스캔으로 `ALLOWED_HUB_REPOS:` env line 보유 파일 **자동 발견**(파일명 하드코딩 0), double-quote 형식 line 만 AWK in-place rewrite(indent 보존).

### 결정 2: reconcile 워크플로우 본체 무수정 (wrapper thin-dispatcher invariant)

덮어쓰기 로직 자체를 제거하지 않는다(OOS). 주입은 **후처리 only** — wrapper 워크플로우 템플릿이 두꺼워지지 않도록 manual/optional step 으로 wire(현재). 자동 wire(reconcile→inject 체이닝)는 future codeforge-pmo UpgradeAgent 영역(별 CFP).

### 결정 3: 불변식 3종

- **never-reduce**: merge 결과 첫 entry 는 항상 template default(`github.com/mclayer/codeforge-internal-docs`). consumer 선언으로 default 제거 불가(mechanical 강제). 보안 의미 = 화이트리스트를 비워 fail-closed gate 를 우회하는 권한 축소 차단(monotonic allow-list = fail-safe).
- **idempotent**: 동일 입력 2회 실행 = 워크플로우 파일 byte-identical(dedup guard + 무조건 교체 rewrite).
- **monotonic whitelist + format validation**: positive charset whitelist(`^[A-Za-z0-9._-]+/[A-Za-z0-9._-]+/[A-Za-z0-9._-]+$`, 3-segment)로 comma/quote/공백/shell metachar reject — env value 가 shell·YAML 양쪽 노출이므로 injection 방어.

### 결정 4: 잔존 운영 리스크 + 보강 방향 (P2, 비차단)

- **bash 3.2 비호환(EC-4)**: dedup 이 `declare -A`(bash 4.0+) 의존 → macOS 시스템 기본 bash 3.2 에서 미작동. CI(ubuntu, bash 5.x) 무문제. **판정 = awk fallback 미채택**(검증 GREEN 구현 비훼손 + 정상 실행 위치 = reconcile 직후 Linux/CI), 대신 실행환경 CI/Linux 한정 명시 + bash 버전 preflight guard fail-fast 권고(silent 실패 → 명시 거부).
- **/tmp marker 고정 경로 race(EC-5)**: 성공 판정 marker(`/tmp/rewrite_marker.tmp`)가 PID suffix 부재 → 동시 실행 race + 공유 호스트 hijack 잠재. 단일 실행 시나리오 무영향이나 auto-wire 병렬화 시 재발. **판정 = robustness 보강 채택**(P2) — `mktemp`/exit-status IPC 전환 권고(파일시스템 marker 의존 제거). 현 GREEN 동작 유지, 보강은 Phase 2/별 carrier.

두 리스크 모두 **blocking 아님**(현 운영 전제에서 실무 무영향) — P2 enhancement 로 분리.

## 해소 기준

N/A — permanent policy. 본 ADR 은 consumer 보안 화이트리스트 확장-only 주입 메커니즘의 상시 정책으로, sunset 대상이 아니다(reconcile-then-patch 불변식은 메커니즘 존속 동안 영구 유효). 잔존 P2 리스크(§결정 4 — bash 3.2 / /tmp marker)는 별 enhancement carrier 로 보강하되 본 ADR 의 결정 자체를 폐기하지 않는다.

## 근거 (Rationale)

- 옵션 A(reconcile 덮어쓰기 로직 제거) **기각** — wrapper thin-dispatcher invariant 위배 + reconcile 본체 수정은 모든 consumer 영향 광역 리스크.
- 옵션 B(멱등 후처리 주입) **채택** — reconcile 무수정, 환경-특화 확장만 멱등 재적용, never-reduce 로 보안 화이트리스트 무결성 보존. ADR-024 Amendment 2 §결정 A 선례 동형.
- awk 전면 fallback **기각** — 검증된 GREEN 구현(8 bats)을 흔들고 retroactive 안정성 훼손. 실행환경 한정 + guard 가 비용 대비 충분.

## 영향 / 후속

- consumer adoption(mctrader-data 등) = 별 cross-repo PR(본 ADR OOS).
- ADR-057 오인용 정정(workflow 주석 + ADR-026 frontmatter + consumer-guide/schema/example + PR body) = 별 doc-only fix carrier CFP(CFP-1716 Story §11.3).
- R1(version guard) / R2(mktemp IPC) = Phase 2 동반 또는 별 enhancement CFP.
- auto-wire(reconcile→inject) = future codeforge-pmo UpgradeAgent 영역.
