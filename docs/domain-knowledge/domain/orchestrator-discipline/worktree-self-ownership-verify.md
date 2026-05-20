---
kind: domain
domain: orchestrator-discipline
title: Worktree-first self-ownership verify — multi-worktree distributed local state 5th staleness layer + self-confusion failure mode
related_adrs:
  - ADR-073-Amendment-3  # 본 narrative SSOT 의 normative anchor (worktree-first self-ownership verify 3-tuple)
  - ADR-040  # worktree convention topology rule (본 narrative 의 동인 root — multi-worktree distributed local state 토폴로지 생성)
  - ADR-082  # internal lane agent self-write verify (disjoint super-class — write-time semantic truth verify vs commit ownership worktree topology verify)
  - ADR-073-Amendment-2  # detection layer (memory rule 6 title-based search + rule 7 Epic state poll, transition trigger enum 3종 + cold start) — 본 verification layer 의 선행 layer
  - ADR-064  # decision principle mandate (self-application top-down ratchet — Amendment 3 강화 방향 only)
  - ADR-058  # ADR sunset criteria mandate (is_transitional: false 영구 정책, sunset_justification N/A)
related_stories:
  - CFP-689   # 본 narrative SSOT carrier (plugin-codeforge#1038 PMO P1 ESC 정식 carrier)
  - CFP-1038  # PMO escalation P1 (worktree_first_self_confusion_within_single_session pattern_count 3 reach)
  - CFP-983   # disjoint axis carrier (real parallel cross-session collision sub-domain — 본 narrative scope 외)
  - CFP-966   # parallel-work-sentinel-pickup precedent (declarative-only-Wave-1 패턴 답습)
  - CFP-967   # parallel-work-sentinel-pickup Wave 2 mechanical wire precedent (sibling Story-2 pattern)
related_memory:
  - feedback_worktree_first_not_parallel_session  # normative 승격 carrier — 본 narrative SSOT 가 normative 명시
status: Active
date: 2026-05-20
---

# Worktree-first self-ownership verify

ADR-073 Amendment 3 (CFP-689, 2026-05-20 KST) 의 narrative SSOT. ADR-040 worktree-first normative 가 만든 **multi-worktree distributed local state** 토폴로지 안 self-confusion 영역의 도메인 본질 + path-based 3-tuple verify primitive + edge case + subagent verdict re-verify mandate + disjoint axis cross-ref.

## 1. 본질 anchor — 5th layer staleness (spatial dimension)

산업 표준 4-layer staleness hierarchy (Bazel hermeticity 동형) + codeforge 5th layer 확장:

| Layer | 영역 | Industry exemplar | codeforge cross-ref |
|---|---|---|---|
| 1 | source tree (working tree mutable, uncommitted edits) | Bazel hermeticity layer 1 | ADR-073 base §결정 1 (M1 working tree mutation lag) |
| 2 | network / repo deps | Bazel hermeticity layer 2 | ADR-073 base §결정 1 (M2 cross-repo origin lag) |
| 3 | clock / nondeterminism | Bazel hermeticity layer 3 | ADR-073 §결정 8 hook automation 영역 (시간 의존 cache invalidation) |
| 4 | process / sandbox isolation | Bazel hermeticity layer 4 | ADR-070 Codex worker sandbox boundary |
| **5** | **multi-worktree distributed local state (spatial dimension)** | **본 도메인 (codeforge-specific)** | **ADR-073 Amendment 3 §결정 1-D self-ownership verify 3-tuple** |

5th layer = ADR-040 worktree-first normative (`${HOME}/.claude/worktrees/<repo>/cfp-NNN[-suffix]`) 가 만든 토폴로지: **동일 lane branch 가 N 개 isolated worktree 에 분산**되는 spatial 차원. 단일-worktree 멘탈모델 (`C:/workspace/mclayer/<repo>/`) 로는 자기 세션이 dedicated worktree 에서 만든 commit 도 외부 commit 처럼 보임 — **자기 세션 자체 산출물을 외부 parallel session 으로 오인하는 self-confusion**.

## 2. Sentinel evidence — 2026-05-19~20 KST single session 3 occurrences (pattern_count 3 reach)

본 Amendment 3 의 정합 forcing function:

### Occurrence #1 — CFP-1026 brainstorm STAND-DOWN false-positive (2026-05-19)

Phase 0 4-agent parallel context fetch 직후 본 session 자기 산출물을 외부 work 으로 오인 → STAND-DOWN 발화 → 검증 후 false-positive 확인 → resume. 첫 sentinel 발현 — single-worktree 멘탈모델 잔존.

### Occurrence #2 — CFP-681 cfp-1014 dup worktree (2026-05-19~20)

RequirementsPL 중복 spawn — authoritative `cfp-681-s2` worktree 의 자기 work commit `f39b221` 을 parallel session 산출물로 mis-flag → dup worktree setup → 검증 후 self-confusion 확인 → dup prune. agent level self-confusion 두 번째 발현 — `git worktree list` ground truth 미참조.

### Occurrence #3 — CFP-681 ArchitectPL Phase 3 자기 commit mis-flag (2026-05-20)

ArchitectPL verdict packet 안 자기 ArchitectAgent commit `00b7d8a` 를 `parallel_session_conflict` 로 mis-flag — **subagent 도 multi-worktree self-confusion 영역에서 보이는 패턴 입증**. Orchestrator 가 subagent verdict 를 final source of truth 로 취급 시 self-confusion contagion (Orchestrator → subagent → Orchestrator 재반영 cycle).

이 3 occurrences 가 ADR-045 §D-9 Mandatory framing pattern_count 3 reach forcing function — ADR-073 Amendment 3 발의 임계 도달.

## 3. Path-based 3-tuple verify primitive (사용자 prompt identity-based 대안 채택)

사용자 원문 prompt 의 3-tuple (cwd ↔ git config user.email / HEAD author ↔ session identity / `gh pr list head:<branch>` ownership) 은 **identity-based** — ResearcherAgent + FeasibilityAgent 통합 평가 결과 Solo-dev 환경 (단일 mccho-mclayer git config) 식별력 0 + edge case 다수 (signed commit GPG / detached HEAD / anonymous worktree / `CODEFORGE_SESSION_ID` env 부재). **path-based 대안 채택** (Amendment 3 §결정 1-D 정합):

### Verify primitive atomic group (3-step 동시 수행)

| ID | Verify check | 실행 cmd | PASS 조건 | Fallback rule |
|----|---|---|---|---|
| **(a)** | cwd ↔ worktree path 일치 | `git rev-parse --show-toplevel` vs `git worktree list --porcelain` | string equality (path normalize: forward-slash `/` + lowercase drive-letter `c:`) | normalize 후 mismatch 시 (a) FAIL → (c) backstop |
| **(b)** | HEAD lineage ↔ session reflog membership | `git reflog show <branch> --all` + `git log <commit> --oneline` cross-check | reflog membership = true (본 session commit chain 추적 가능) | reflog 90d GC 시 (b) FAIL → **(a)+(c) 2-source AND fallback** |
| **(c)** | worktree list + reflog 2-source AND | `git worktree list --porcelain | grep <branch>` parse `branch` field + reflog entry exists | 양 source PASS = self-ownership verify TRUE | (a) FAIL OR (b) FAIL OR (c) FAIL → parallel session verdict |

### 3-tuple verdict 분기

- **3-tuple PASS** (self-ownership TRUE): subagent verdict `parallel_session_conflict` REJECT + continue (자기 산출물 정상 진행) + Story §10 FIX Ledger `subagent_misflag_self_confusion` reason code row append.
- **3-tuple FAIL** (self-ownership FALSE): memory rule 6/7 detection layer 절차 인계 (title-based search + Epic state poll + HEAD compare sibling commits) — real parallel session 영역.

## 4. Edge case + fallback handling

### 4.1 detached HEAD (branch reflog 없음)

`branch` field 부재 → (b) 자동 skip → **(a)+(c) 2-source AND fallback** (PASS 조건 = (a) PASS AND (c) PASS — branch field 없을 시 `git worktree list --porcelain` 안 `(detached HEAD ...)` log line 검증).

### 4.2 anonymous worktree (`git worktree add --detach` path)

`branch` field 부재 — self-ownership verify 불가능 영역 → **forcing function**: "anonymous worktree 안 lane spawn 금지" (codeforge worktree convention violation — ADR-040 §결정 1 named worktree mandate 정합). detection 시 즉시 ABORT + named branch worktree 재생성 의무.

### 4.3 Signed commit GPG + CODEFORGE_SESSION_ID env 부재

사용자 prompt identity-based 3-tuple 영역의 edge — 본 Amendment 3 path-based 채택으로 회피 (identity-based scope OUT). path-based 3-tuple 은 commit signing / env 부재 양 영역 robust.

### 4.4 Reflog GC 90d window (`gc.reflogExpire=90 days` git default)

장기 stale lane branch (Phase 1 merge 후 Phase 2 sub-CFP 가 90일 후 진입하는 경우) verify 시 reflog membership false-negative 가능. **Phase 2 fallback rule 의무** — Wave 2 별 sub-CFP carrier mechanical wire 안 `git log --all --grep=<KEY>` + manual ownership claim 등 추가 fallback rule 명시.

### 4.5 Path normalization (Windows drive-letter case + slash direction)

Windows drive-letter case 변동 (`C:/` vs `c:/`) + slash direction (`/` vs `\`) 차이로 `git rev-parse --show-toplevel` 출력과 `git worktree list --porcelain` path field 의 string equality 가 false 가능. **canonical form = lowercase drive + forward-slash** (`c:/users/...`). MSYS2 / Git Bash / WSL / native cmd.exe 전 환경 동형 보장.

## 5. Subagent verdict re-verify mandate (multi-worktree self-confusion 영역 agent 도 보임)

Occurrence #3 sentinel evidence (ArchitectPL Phase 3 ArchitectAgent commit `00b7d8a` mis-flag) 입증 — **subagent 도 verdict packet 안 `parallel_session_conflict` mis-flag 영역에서 stale source of truth**. Orchestrator 가 subagent verdict 를 final source of truth 로 취급 시 self-confusion contagion (Orchestrator → subagent → Orchestrator 재반영 cycle).

### Re-verify primitive

1. **즉시 ground-truth re-verify 의무** — `git worktree list --porcelain` + `git reflog show <branch>` direct execution (subagent 가 이미 수행했더라도 Orchestrator 자기 검증).
2. **subagent verdict ≠ final source of truth** — multi-worktree self-confusion 영역에서는 agent 도 mis-flag 패턴 입증. Subagent verdict 는 advisory annotation 만 — Orchestrator 가 self-ownership verify 3-tuple 결과를 ground truth 채택.
3. **3-tuple PASS 시**: subagent verdict REJECT + continue (자기 산출물 정상 진행) + Story §10 FIX Ledger `subagent_misflag_self_confusion` reason code row append (Orchestrator 단독 §10 append 독점, fix-event-v1 contract).
4. **3-tuple FAIL 시**: subagent verdict 채택 + memory rule 6/7 detection layer 절차 진행.

### ADR-082 §결정 1 layer disjoint 4-layer 표 cross-ref

| Layer | ADR | Verify 대상 | scope 분리 |
|---|---|---|---|
| Layer 1 (Orchestrator self-assertion) | ADR-073 base | cross-repo state + file path 단정 | working tree < origin/main canonical staleness 영역 |
| Layer 2 (External worker output) | ADR-070 | Codex finding evidence | sandbox boundary cross-cutting |
| Layer 3 (Internal lane agent self-write) | ADR-082 | §9 evidence / Phase 0 mapping / corpus enumeration write-time semantic truth | 작성 값 자체의 사실성 source verify |
| Layer 4 (PMOAgent retro corpus pattern_count) | ADR-045 §D-9 | cross-Story pattern_count ≥ threshold 2 검출 시 ADR escalation forcing function | retro corpus enumeration |
| **+ Amendment 3 (본 narrative)** | **ADR-073 Amendment 3** | **worktree-first self-confusion (lane agent self-write 가 만든 commit 의 self-ownership)** | **Layer 1 자체 영역 확장 (multi-worktree self-confusion sub-domain) — Layer 3 self-write 영역과 disjoint 보완** |

본 Amendment 3 = ADR-073 Layer 1 자체 영역 안 multi-worktree self-confusion sub-domain 신설. ADR-082 Layer 3 = 작성 값 사실성 verify / 본 Amendment 3 = commit ownership worktree topology verify — disjoint axis.

## 6. Disjoint scope — real parallel session 영역 (#983 후보 (a)/(b)) 와 분리

본 narrative SSOT 의 self-confusion sub-domain 은 #983 후보 (a)/(b) 의 real parallel cross-session collision sub-domain 과 **disjoint axis** (reflog membership 1 bit signal):

| 차원 | 진짜 parallel (cross-session conflict, #983 후보 (a)/(b)) | self-confusion (within single session, **본 narrative SSOT 영역**) |
|---|---|---|
| reflog membership | **본 세션 reflog 에 없는 commit** + 다른 worktree lineage 가 origin 에 독립 존재 | **본 세션 skeleton → lane commit 단일 선형** 이 multi-worktree 로 흩어진 산출물 |
| 1-bit signal | reflog membership = **false** | reflog membership = **true** |
| 적용 governance | memory rule 6/7 + ADR-073 Amendment 2 (detection layer) | **본 Amendment 3 (verification layer — detection 직전 self-ownership verify 선행)** |
| 처리 액션 | stand-down / re-spawn / merge-order 의뢰 | continue (자기 산출물 정상 진행) + subagent verdict reject |
| Carrier ESC | #983 (별 Story carrier — real parallel cross-session collision 영역) | CFP-689 (본 Story — plugin-codeforge#1038 PMO P1 ESC 정식 carrier) |

본 Amendment 3 = #983 P1 ESC body 안 후보 (c) "ADR-073 Amendment 3 — shared workdir collision worktree-first invariant 강화" 의 정식 carrier. #983 후보 (a)/(b) 는 별 Story carrier 영역 — 본 narrative SSOT scope 외, disjoint axis 명시 invariant.

## 7. Mechanical enforcement chain (Wave 1 declaration / Wave 2 mechanical wire / Wave 3 auto-promote blocking)

CFP-966 (declarative anchor) → CFP-967 (mechanical wire merged 2026-05-19) chain 완결 precedent 답습:

| Wave | Status | Carrier | Artifacts |
|---|---|---|---|
| **Wave 1 (declarative anchor only)** | `mechanical_enforcement_actions: [parallel-work-sentinel-pickup, worktree-self-ownership-verify]` (2 entry, warning tier, status: deferred-followup) | **CFP-689 (본 Amendment 3, 2026-05-20) — 본 narrative SSOT** | ADR-073 Amendment 3 본문 + frontmatter row + evidence-checks-registry entry (declaration-only) + 본 narrative SSOT + CLAUDE.md cross-ref + section-ownership.yaml row + plugin.json/CHANGELOG MINOR bump |
| **Wave 2 (mechanical wire)** | (entry status: deferred-followup → warning 전환) | **TBD 별 sub-CFP carrier (sequential next, Wave 1 merge 후)** | `scripts/check-worktree-self-ownership.sh` (thin bash wrapper, ADR-061) + `scripts/lib/check_worktree_self_ownership.py` (Python SSOT — 3-tuple verify primitive 구현 + edge case + path normalization) + `templates/github-workflows/worktree-self-ownership-verify.yml` + `.github/workflows/` byte-identical self-app (ADR-005) + `templates/.claude/hooks/PreToolUse-worktree-self-ownership.json.sample` (consumer opt-in cold start sample) + `tests/scripts/check-worktree-self-ownership/test_worktree_self_ownership.bats` (bats TC: PASS / FAIL / detached HEAD fallback / anonymous worktree ABORT / Windows path normalize / reflog GC fallback / BYPASS / TOCTOU re-check) + label-registry-v2 신규 entry `hotfix-bypass:worktree-self-ownership-verify` |
| **Wave 3 (recurrence count ≥ 3 자동 승격)** | (entry current_tier: warning → blocking-on-pr 전환) | post-Wave-2 follow-up CFP (recurrence.threshold=3 auto-firing — pattern_count 3 already reached 2026-05-19~20 sentinel evidence) | (entry tier 변경 only — ADR-060 §결정 19 Amendment 6 auto-firing) |

## 8. 외부 fact 인용 — `git worktree list --porcelain` 산업 표준 verify primitive

- **Linux kernel multi-branch 작업**: `git worktree list` 를 통한 multi-worktree topology 명시 (개발자 mental model 의 ground truth). `git worktree list --porcelain` machine-readable format = stable parse target.
- **Chromium multi-branch + sub-tree 작업**: `git worktree` + `git rev-parse --show-toplevel` 조합으로 cwd ↔ worktree 일치 verify (path-based primitive 산업 검증).
- **`git reflog` 90d default GC**: `gc.reflogExpire = 90 days` git default — 사용자 정의 verify primitive 신설 0 (산업 검증된 표준).

본 Amendment 3 의 3-tuple verify primitive 채택 = 산업 검증된 표준 (codeforge-specific 신설 verify 0).

## 9. 관련 cross-ref

- **ADR-073 Amendment 3** = 본 narrative SSOT 의 normative anchor (worktree-first self-ownership verify 3-tuple, declaration-only-Wave-1)
- **ADR-040 worktree convention** = 본 도메인의 동인 root (multi-worktree distributed local state 토폴로지 생성)
- **ADR-082** = disjoint super-class (write-time semantic truth verify vs commit ownership worktree topology verify)
- **ADR-073 Amendment 2 + memory rule 6/7** = detection layer (본 verification layer 의 선행 layer)
- **CFP-689** = 본 narrative SSOT carrier Story (plugin-codeforge#1038 PMO P1 ESC 정식 carrier)
- **CFP-983** = disjoint axis carrier (real parallel cross-session collision sub-domain — 본 narrative scope 외)
- **CFP-966/967 chain** = declarative-only-Wave-1 → Wave 2 mechanical wire precedent (본 narrative 의 답습 패턴)
- **memory `feedback_worktree_first_not_parallel_session`** = normative 승격 carrier (본 narrative SSOT 가 normative 명시)
- **#729 future Amendment 4 disjoint** = plugin-codeforge#729 (ADR-073 "Amendment 1" 슬롯 충돌, Amendment 4 재배정 의무, ContinuityAgent CRITICAL) 영역과 section disjoint 보장 — 본 Amendment 3 = self-ownership verify 3-tuple + transition trigger enum 4번째 entry / Amendment 4 = Glob false negative 별 §결정 영역.
