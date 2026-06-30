---
adr_number: 135
title: "own-branch force-push pre-flight HEAD-pin 가드 + parallel-work-sentinel blockable-but-warning mechanism (Epic CFP-2481 Phase B E2)"
status: Proposed
category: orchestration-discipline
date: 2026-06-30
carrier_story: CFP-2490
parent_epic: CFP-2481
supersedes: null
amends: null
related_adrs:
  - ADR-039  # Orchestrator subagent default — §결정 14 Pre-spawn-pin (branch-생성-시점 read-pin) = disjoint axis (본 ADR = push-시점)
  - ADR-073  # Orchestrator verify-before-assert — Amd 2 sentinel anchor / Amd 13 pre_push trigger (sentinel pickup 축, disjoint) / Amd 14 AND-aggregate (OOS) / §결정 1 cross-repo state (disjoint)
  - ADR-060  # Evidence-enforceable promotion framework — warning→blocking 승격 gate + recurrence promotion (warning 유지 정합 근거)
  - ADR-115  # Runtime hook enforcement — PreToolUse(Agent) gate precedent (hook 채널 enforcement 근거)
  - ADR-005  # Self-app byte-identical — templates/github-workflows ↔ .github/workflows parity 의무
  - ADR-024  # Story-scoped branch policy — hotfix-bypass:* family namespace (신규 bypass label 정합)
  - ADR-119  # Research-before-claims / 검사연극 금지 — opt-in 강제 한계 정직 기술 의무 근거
  - ADR-040  # Worktree convention — install-git-hooks.sh opt-in installer 기반 + Amd 3 §결정 7.D self-application
  - ADR-061  # Python thin-wrapper convention — sh thin wrapper + py SSOT 패턴
  - ADR-134  # Parallel eligibility dispatch (E1) — sentinel blocking / force-push HEAD-pin = E2 carrier 명시
related_files:
  - archive/adr/ADR-039-orchestrator-subagent-default-for-codeforge-modification-work.md
  - archive/adr/ADR-073-orchestrator-verify-before-assert.md
  - archive/adr/ADR-RESERVATION.md
  - scripts/lib/check_parallel_work_sentinel.py
  - scripts/check-parallel-work-sentinel.sh
  - templates/github-workflows/parallel-work-sentinel-check.yml
  - .github/workflows/parallel-work-sentinel-check.yml
  - tests/scripts/test_check-parallel-work-sentinel.sh
  - scripts/install-git-hooks.sh
  - docs/evidence-checks-registry.yaml
  - docs/inter-plugin-contracts/label-registry-v2.md
mechanical_enforcement_actions: []
is_transitional: false
sunset_justification: null
---

# ADR-135: own-branch force-push pre-flight HEAD-pin 가드 + parallel-work-sentinel blockable-but-warning mechanism (Epic CFP-2481 Phase B E2)

## 맥락

Epic CFP-2481(Epic 병렬 실행 정형화)의 E2(CFP-2490)는 두 개의 **독립(disjoint) race-guard 축**을 한 Story로 묶는다.

1. **parallel-work-sentinel "blockable-but-warning" mechanical wire** — mid-flight parallel race(같은 CFP/Epic 을 다른 세션이 동시 작업 → 중복 Issue/PR, in-flight merge miss) 탐지. sentinel base(script + py SSOT + workflow byte-identical 쌍 + discriminating test)는 **이미 Active**(CFP-967 mechanical wire + CFP-2451 prefix 파라미터화). 본 ADR = "blocking 승격은 보류(warning 유지)하되, 단일 tier-flip 축만으로 즉시 blocking 전환 가능한 구조(blockable-capable)를 보장"하는 최소 delta + hollow gate(검사연극) 회피 mechanism 정의.
2. **own-branch force-push pre-flight HEAD-pin 가드 부활** — branch-creating/force-push 행위자가 stale base 위에서 force-push 해 sibling commit 의 ancestry 를 corruption(덮어쓰기)하는 것을 push 직전 막는 pre-flight pin discipline. `ancestry_corruption_force_push_no_pre_flight_gate` pattern_count 2 reach(#1027: CFP-967 Phase 2 + CFP-991 Phase 2). 한 번도 landed 된 적 없음 — CFP-1103(force-push pre-flight gate) CLOSED NOT_PLANNED(2026-05-20), #1027 ESCALATION OPEN.

### 왜 신규 ADR(reuse-first 평가 결과)

reuse-first 원칙에 따라 기존 anchor 흡수를 먼저 평가했고, **모두 axis-disjoint 로 확정**되어 신규 ADR-135 를 신설한다.

| 기존 anchor | 실제 축 | force-push 가드 축과의 관계 |
|---|---|---|
| **ADR-039 §결정 14** (Pre-spawn-pin mandate) | **branch-생성-시점 read-pin** — `git rev-parse origin/main` explicit pin *before branch create* (stale-base 차단, self-claim/packet SHA/local HEAD 무조건 신뢰 금지). [verified ADR-039:261] | **disjoint** — read-time(branch 생성 전) vs push-time(force-push 직전 ancestry). #1027 verbatim: "ADR-073 §결정 1 ... 본 건 = own-branch force-push pre-flight" |
| **ADR-073 Amendment 13** (`pre_push` trigger) | **push-시점 parallel-work-sentinel pickup** — `git push` 직전 sentinel(중복작업 탐지) 재실행. evidence-checks-registry `pre-push-sentinel-pickup`(Wave 1 declarative, 미배선). [verified ADR-073:99/208] | **disjoint** — sentinel(중복작업 탐지) vs ancestry-corruption(force-push 덮어쓰기). 같은 "push 직전" 시점이나 검사 대상이 다른 sub-domain. (본 ADR §결정 7 에서 OOS 명시) |
| **ADR-073 §결정 1** (cross-repo verify-before-assert) | **Orchestrator 단정 발화 시점 cross-repo state verify** | **disjoint** — #1027 verbatim "ADR-073 = cross-repo state assertion, 본 건 = own-branch force-push pre-flight" |

→ own-branch force-push ancestry-corruption **pre-flight** 는 위 셋과 별개 결정축이다. #1027(본 ADR 의 escalation carrier) 자체가 "신규 ADR(next-free ADR 번호) ... OR ADR-073 Amendment 候補 평가(transition trigger enum 확장 — `force_push` 추가)"를 분기로 제시했고, axis-disjoint 확정에 따라 **신규 ADR-135** 채택. (CFP-702 ADR collision 교훈 답습 — ADR-RESERVATION row 135 sequential claim, collision check origin/main numeric max=ADR-134.)

## 결정

### §결정 1 — force-push pre-flight 3-check 정명

`git push --force-with-lease` 직전 다음 3-check 의무(#1027 root cause 직접 대응):

| check | 명령 | 탐지 대상 |
|---|---|---|
| **C1 branch-show-current** | `git branch --show-current` | 현재 branch 인지 (CFP-967 사례: 시작 branch 미인지 → 엉뚱한 branch force-push) |
| **C2 origin-HEAD-divergence-compare** | `git fetch origin <branch>` + `git rev-list --left-right --count origin/<branch>...HEAD` | origin HEAD ↔ local HEAD divergence (force-with-lease 가 자기 branch tip 만 보고, **base(main) advance 는 미검사**하는 gap) |
| **C3 claimed-HEAD-reachability** | `git merge-base --is-ancestor <claimed_HEAD> HEAD` (또는 `git for-each-ref --contains`) | claimed commit 이 현재 HEAD ancestry 에 도달 가능한가 (CFP-991 사례: production code orphan 을 design FIX chain 으로 overwrite) |

`--force-with-lease` 의 의미적 한계가 근본 원인이다: 자기 branch 의 remote tip 이 예상과 같을 때만 force-push 하므로 blind `--force` 보다 안전하지만, **base branch(main)의 advance 는 검사하지 않는다**. C2 가 정확히 이 gap 을 보완한다. [verified — `--force-with-lease` semantics + #1027 root cause 실측]

### §결정 2 — enforcement 채널 = local pre-push hook(opt-in, 진짜 pre-flight) + CI 사후 detect warning(2-layer)

force-push pre-flight 는 **CI 로 차단할 수 없다** — force-push 가 발생한 시점엔 이미 origin 이 변경된 후라 CI 는 사후 detect 만 가능. 진짜 pre-flight 차단은 **local pre-push hook(opt-in)** 채널만 가능.

- **Layer 1 (진짜 pre-flight, local)**: opt-in `pre-push` git hook(sample) — push 가 origin 에 도달하기 전 3-check 실행, 실패 시 push abort. 기존 자산 `scripts/install-git-hooks.sh` 가 `templates/.git-hooks/*.sample` glob 으로 auto-pickup(installer 코드 변경 불요 — 신규 sample 파일 추가만으로 등록). [verified install-git-hooks.sh glob]
- **Layer 2 (사후 가시화, CI warning)**: force-push 가 이미 발생한 PR 에서 ancestry anomaly 를 사후 detect 해 **경고**(차단 X, continue-on-error). de-bloat 재발 방지를 위해 live workflow + 실존 detect path + discriminating self-test 동반.

CI 로 pre-flight 차단이 구조적으로 불가능하다는 본질을 정직히 기술(검사연극 금지, ADR-119) — Layer 2 를 "force-push 차단"으로 과대 표기하지 않는다.

### §결정 3 — opt-in 강제력 한계 정직 기술

opt-in hook 은 미설치 환경에서 무력하다. 이것이 #1027 패턴이 재발한 근본 이유다.

- **server-side pre-receive hook** 이면 강제력이 있으나, GitHub.com 은 pre-receive hook 미지원(GitHub Enterprise Server 만 지원으로 알려짐). [hypothesis — 본 Story 비-load-bearing, deep-cite 생략; 필요 시 요구사항리뷰 deep-research 발동]
- 따라서 "강제력 있는 force-push 차단"은 GitHub.com 환경에서 **구조적으로 불가능**하다. 본 ADR 은 opt-in hook(권장 설치) + CI 사후 warning(가시화) 의 best-effort 조합으로 한정하고, 이 한계를 trade-off 로 명시한다(은폐 금지).

### §결정 4 — de-bloat 재발 방지(theater 회피 3-종 동반)

spawn-prompt-head-pin family 가 theater(실행경로 0 거짓 inventory)로 분류돼 #2112 de-bloat 로 제거된 전례가 있다. 신규 force-push 가드 자산은 다음 3-종을 반드시 동반한다(deferred-followup-reconcile gate CFP-2381 통과 조건):

1. **live workflow** — 실제 trigger 되는 `.github/workflows/*.yml`(+ byte-identical templates 쌍).
2. **실존 detect_command path** — evidence-checks-registry entry 의 detect_command 가 가리키는 script 가 실재.
3. **discriminating self-test** — mutation-RED(아래 §8 Test Contract).

### §결정 5 — EC-4 scope(force-push 가드가 detect 하는 범위 / cover 환경)

- **detect 범위**: base-advance(C2 divergence) / divergence(local↔origin) / claimed-HEAD reachability(C3). 3-check 가 SSOT.
- **cover 환경**: opt-in hook 설치 환경에서만 pre-flight 차단. **OOS(cover 불가)**: ① opt-in hook 미설치 환경(강제력 0), ② server-side 강제(GitHub.com 미지원), ③ `--force`(no-lease) blind force-push 의 일부 edge. Windows MSYS git-bash 환경은 hook sample 이 POSIX sh 로 작성돼 git-bash 에서 실행되므로 cover 대상(단 path 변환 주의 — Phase 2 구현 검증 의무).
- 미설치 환경은 CI 사후 warning(Layer 2)만 도달 — 정직 기술.

### §결정 6 — sentinel blockable-but-warning mechanism(hollow gate 회피)

continue-on-error=true(warning) 를 유지하면서 "단일 tier-flip 축만으로 blocking 전환"되는 구조:

- **tier 변수화**: workflow 에 단일 tier 축(예: env/workflow 변수 `SENTINEL_TIER` = `warning` | `blocking`, 또는 step 의 `continue-on-error` 가 그 변수에서 파생)을 둔다. 현재는 `warning` 으로 고정 → `continue-on-error: true` 유지. blocking 승격은 그 한 축만 `blocking` 으로 flip(별 Story 결정, ADR-060 evidence-gate).
- **hollow gate 회피**: "blockable 인데 warning"이 실제로는 아무것도 안 잡는 연극이 되기 쉽다. 이를 §8 mutation-RED 가 증명 — tier=blocking 으로 mutate 시 차단 동작(RED), tier=warning 정상(GREEN)이 **함께**여야 PASS. 단순 "exit 0 = PASS" non-discriminating 검사는 금지.
- branch protection 6-tuple 무변경 — warning tier 는 required_status_checks contexts 미등록(merge 무차단). blocking 승격 시에만 6-tuple 변경 필요 → 본 Story 무변경 확정. [verified 6-tuple SSOT]

### §결정 7 — OOS(out-of-scope) 명시

- **AND-aggregate**(ADR-073 Amendment 14 `parallel-work-sentinel-and-aggregate`, 3-mode 동시 invoke + AND aggregate) = single-mode dispatch 약점 보완 매력적이나 CFP-2490 "blockable-capable + warning" tight scope 밖 → **OOS**(별 sub-CFP carrier 잔류).
- **`pre-push-sentinel-pickup`**(ADR-073 Amendment 13, push 직전 parallel-work-sentinel 재실행 = 중복작업 탐지 축) = force-push ancestry-corruption 가드와 disjoint sub-domain → **OOS**(별 sub-CFP).
- **sentinel blocking 승격** = recurrence count 2 < threshold 3 미발화 + 사용자 §1 명시 보류 → **OOS**(별 Story, mutation-RED + 실 병렬 evidence 후 결정).

## 권장안 vs 대안

- **권장 1안**: force-push 가드 = opt-in pre-push hook(진짜 pre-flight) + CI 사후 warning(가시화) 2-layer / sentinel = tier 변수화 blockable-but-warning + mutation-RED. → opt-in 한계는 정직히 기술하되 best-effort enforcement 확보, de-bloat 내성(3-종 동반).
- **대안 1안**: force-push 가드를 convention(playbook 절차)으로만 강화하고 hook/CI 자산 0. → 강제력 더 약함 + #1027 재발 패턴 답습(미해결). 기각.

## #1027 carrier 귀속

CFP-2490 = #1027(force-push pre-flight HEAD-pin gate ESCALATION, OPEN)의 **ADR carrier(Phase 1, 본 ADR-135) + wire carrier(Phase 2)**. 흡수 시 close 경로이나, **PR body 에 `Closes #1027` closing keyword 금지** — phase-gate binding 오류(자동 close-state transition) 유발. PR body 는 `Related: #1027` only. 실제 close 는 Phase 2 wire 완료 후 Orchestrator 가 수동 판정.

## 적용 / 강제

`mechanical_enforcement_actions: []` — Phase 1 declaration-only(검사 스크립트·required check 0 신설). 실 mechanical wire(pre-push hook sample + installer auto-pickup + 사후 CI warning workflow + discriminating self-test + evidence-checks-registry warning entry + label-registry-v2 v2.100→v2.101 MINOR)는 Phase 2 carrier. 회귀 0 차단.

## E2 disjoint(E1/E3 영역 침범 0)

- **E1**(CFP-2488, ADR-134) = 병렬 적격성 5조건 + per-Story dispatch + ADR-039 Amendment 7. spawn-권한 layer.
- **E3a**(CFP-2489, ADR-133) = ADR-RESERVATION OCC atomic claim. numeric-space lock.
- **E2**(본 ADR-135) = sentinel race-guard(탐지) + force-push HEAD-pin(쓰기 보호). E1(적격성 판정)·E3a(ADR 번호 직렬화)와 disjoint axis — 침범 0.
- **E3b** = ADR-136 예비(claim primitive script + stale slot 자동 회수).

## 해소 기준

N/A — 영구 governance policy(is_transitional: false). force-push pre-flight 사전 차단 layer 추가 + sentinel blockable-capable 구조화 = 강화 방향 ratchet, 약화 surface 0(ADR-058 §결정 5 sunset_justification 비대상).

## 관련 파일

- `scripts/lib/check_parallel_work_sentinel.py` — sentinel 3-mode SSOT(Phase 2 blockable 판정 검토 대상)
- `templates/github-workflows/parallel-work-sentinel-check.yml` + `.github/workflows/parallel-work-sentinel-check.yml` — byte-identical 쌍(§결정 6 tier 변수화 Phase 2 carrier)
- `tests/scripts/test_check-parallel-work-sentinel.sh` — 기존 prefix discriminating test(§8 tier-flip mutation-RED 확장 Phase 2 carrier)
- `scripts/install-git-hooks.sh` — opt-in installer(glob auto-pickup, Phase 2 신규 sample 추가만)
- `docs/evidence-checks-registry.yaml` — sentinel entry + force-push 가드 신규 warning entry(Phase 2)
- `docs/inter-plugin-contracts/label-registry-v2.md` — v2.100 → v2.101 MINOR(force-push hotfix-bypass family member, Phase 2)
- [#1027](https://github.com/mclayer/plugin-codeforge/issues/1027) — escalation carrier
