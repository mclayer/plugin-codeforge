---
name: post-merge-closure
description: PR merge 후처리 automation flow (trigger / disable-flag / 4 action sequence / telemetry / idempotency / boundary — ADR-026) + PMOAgent retro batch closure 운영 절차 (trigger 조건 / 4-option decision tree / closure summary table / retro PR auto-merge — ADR-045 §D-11) lookup. PR merge 직후 후처리 확인 시 또는 follow-up Issue ≥3 batch closure 진입 시 호출. gate 명제 (§16.5 main 직접 push 금지 / §18.3 verify-before-trust) 는 playbook 잔류.
tools: Read
---

# Post-merge & Closure Ops (CFP-2198 / ADR-120 — playbook §16 + §18 이전)

> **절차 본문 SSOT = 본 skill** — `docs/orchestrator-playbook.md` §16 post-merge automation flow + §18 PMOAgent retro batch closure 에서 이전 (CFP-2198, ADR-120 §결정 1 cold×guide). **gate 명제는 playbook 잔류** (ADR-120 §결정 3): §16.5 main 직접 push 금지 invariant / §18.3 verify-before-trust mandate (5 sub-scope). normative wording SSOT = ADR-026 (§16) / ADR-045 §D-11 (§18) — 본 skill 로 SSOT 이동 아님 (운영 절차 위치만 이전).
>
> **mirror-carrier 주석 (Codex TP 반영)**: 본 body 안의 의무 표현 (§18.1 AND trigger / §18.2 4-option enum + PROMOTE 발의 의무 / §18.4 closure table SSOT / §18.5 close-blocking) 은 전부 `ADR-045 §D-11` normative SSOT + `retro-mandatory.yml` mechanical enforcement 의 mirror 다. 본 skill 미활성 turn 에도 해당 gate 들은 ADR + CI 로 유지된다 (ADR-120 §결정 3 정합 — 본 skill 은 gate 의 단독 carrier 아님).

## 1부 — Post-merge automation flow (playbook §16 이전분, ADR-026 + CFP-74)

ADR-026 의무 — wrapper Orchestrator 가 PR merge event 시 4 action 자동 처리. 사용자 admin merge 후 manual stops 4-5건/merge 자동 처리 → stop 빈도 직접 감소.

### 16.1 Trigger

GitHub Actions workflow `templates/github-workflows/post-merge-followup.yml`. trigger = `pull_request closed event + merged == true`. 사용자 admin merge / squash merge / rebase merge 모두 cover.

### 16.2 Disable-by-flag safety

`.codeforge/post-merge-automation.disabled` file 추가 시 workflow 즉시 skip. 운영 emergency 안전망.

### 16.3 4 Action sequence

| Order | Action | Script | Auth |
|-------|--------|--------|------|
| 1 | Phase label transition | `scripts/next-phase.sh` + `gh issue edit` | GITHUB_TOKEN (current repo) |
| 2 | Story §9 writer (cross-repo) | `scripts/post-merge-story-writer.sh` | CODEFORGE_CROSS_REPO_PAT (internal-docs contents:write) |
| 3 | Carrier Issue close (Phase 2 only) | `gh issue close` | GITHUB_TOKEN |
| 4 | Sibling PR auto-close (archive marker) | `scripts/post-merge-sibling-close.sh` | GITHUB_TOKEN |

각 action `continue-on-error: true` — 일부 실패 시 telemetry outcome=partial 기록 + 사용자 manual fallback.

### 16.4 Telemetry counter

`<internal-docs>/wrapper/post-merge-counters.jsonl` (JSONL append-only, contract_version 1.0). schema:
- `timestamp` / `story_key` / `pr` / `outcome` (auto_completed | partial | manual_only) / `actions_completed[]` / `actions_failed[]` / `decider` / `workflow_run_id`

PMOAgent retro 시 30+ run 누적 후 ROI report 생성 의무. ADR-022 §결정 8 Phase 2 transition gate input.

> **§16.5 main 직접 push 금지 invariant = gate, playbook 잔류** — `docs/orchestrator-playbook.md` §16.5 원문 참조 (본 skill 미수록).

### 16.6 Idempotency

- Story §9 writer: 본 PR ref 의 row 이미 존재 시 skip (grep 기반 dedup)
- Telemetry counter: workflow_run_id 별도 unique entry (재실행 시 별도 entry)
- Phase label transition: 현재 phase == next phase 시 no-op

### 16.7 Boundary (Phase 1 scope, ADR-026 §결정 3)

- ✅ wrapper Orchestrator post-merge automation (4 action + telemetry)
- ✅ disable-by-flag + main 직접 push 금지
- ❌ Enforcement (whitelist 외 stop refusal) — Phase 2 ROI 평가 후 별도 CFP
- ❌ Consumer overlay path support — Phase 2 PMOAgent retro 후


## 2부 — PMOAgent retro batch closure operating sequence (playbook §18 이전분, CFP-1680 / ADR-045 §D-11)

axis 분리 (§D-9 post-hoc threshold escalation / §D-10 pre-publish 8-tuple verify gate / **§D-11 post-batch closure lifecycle (본 §18)**):

- §D-9 = retro write 시점 (escalation, before)
- §D-10 = retro §6 ADR draft pre-publish 시점 (verify, between)
- **§D-11 = batch closure 시점 (status update, after)** — 본 §18 운영 절차 영역

### 18.1 Batch close trigger conditions

PMOAgent batch closure 자동 trigger 조건 (AND gate):

1. **누적 follow-up Issue count ≥ 3** (priority:low OR priority:medium, codeforge-improvement label)
2. **모두 동일 epic 또는 동일 retro origin** (cross-retro batch 영역 미적용 — 단일 retro 1 batch 1 carrier 원칙)
3. **사용자 명시 trigger OR session lifecycle 자동 발동**:
   - 사용자 명시 trigger = `/pmo-batch-close <epic-key>` skill 호출 (Wave 2 명시 trigger 명령, 별 sub-CFP carrier)
   - session lifecycle 자동 발동 = retro PR merge 직후 5분 grace 내 unresolved follow-up count ≥ 3 detect 시 (ADR-045 §결정 1 retro-mandatory.yml 정합 batch closure 영역 확장)

### 18.2 4-option enum decision tree

각 Issue 에 다음 decision tree 적용:

```
1. Recent carrier (≤ 7 일 ago merged) 가 Issue body intent 를 cover 하는가?
   ├─ YES + direct merge link verify PASS  → CLOSE_AS_OBVIATED
   └─ NO  → 2
2. pattern_count >= threshold (보통 N=2) 에 도달했는가?
   ├─ YES + active carrier 발의 가능  → PROMOTE (label priority:P1, 신규 Story 발의)
   ├─ YES + carrier 발의 보류 (future Wave)  → DEFER (rationale 명시)
   └─ NO  → 3
3. declarative monitor only 영역인가? (pattern_count 미달, sentinel 가치 보유)
   ├─ YES  → CLOSE_AS_SENTINEL (close, declarative anchor 영속화)
   └─ NO   → DEFER (keep open, future carrier 대기)
```

4-option closed-set (ADR-064 §결정 1 forbid-list dictionary 회피 — 어휘 채택 시 정확 enum value 의무):

- **`CLOSE_AS_OBVIATED`** — recent carrier resolution, direct merge link verify 의무
- **`CLOSE_AS_SENTINEL`** — declarative monitor only, pattern_count not reached
- **`PROMOTE`** — pattern_count reached + active Story 발의 의무 + label `priority:P1`
- **`DEFER`** — keep open, future carrier 대기, rationale 명시 의무

> **PROMOTE 발의 전 필요성 게이트 (ADR-119 §결정 9 cross-ref)**: pattern_count 도달 ≠ 무조건 발의. PROMOTE (신규 Story follow-up 발의) 전 3문 게이트 선통과 의무 — ① 깨졌나·강제 요인 ② 이득>비용·리스크 ③ 관찰자 없어도 할 일. 셋 다 YES 아니면 발의 금지 (DEFER/CLOSE_AS_SENTINEL 로 강등, "관찰됨·미조치" 기록).

> **§18.3 verify-before-trust mandate (5 sub-scope) = gate, playbook 잔류** — closure write-time 의무 + 1+ sub-scope failure 시 중단 룰은 `docs/orchestrator-playbook.md` §18.3 원문 수행 (본 skill 미수록).

### 18.4 Closure summary table SSOT format

PMOAgent batch closure 산출 retro file §X (close lane sub-section) 안 다음 5-column table 의무 (ADR-068 I-4 wording SSOT invariant 정합):

| # | Issue | Tier | Decision | Final state | Comment URL |
|---|---|---|---|---|---|
| 1 | #NNN | priority:low \| priority:medium | CLOSE_AS_OBVIATED \| CLOSE_AS_SENTINEL \| PROMOTE \| DEFER | closed (not_planned) \| closed (completed) \| open (deferred) | https://github.com/owner/repo/issues/NNN#issuecomment-NNN |
| 2 | #NNN | ... | ... | ... | ... |

추가 메타 field 옵션 (closure summary table 아래):

```yaml
batch_summary:
  total_issues_processed: N
  decisions:
    CLOSE_AS_OBVIATED: N
    CLOSE_AS_SENTINEL: N
    PROMOTE: N
    DEFER: N
  net_pattern_count_change: 0  # closure ≠ pattern increment
  follow_up_carrier_filed: [<CFP-NNN>, ...]  # PROMOTE 결정 시 신규 Story
```

### 18.5 Retro PR auto-merge sequence

Batch closure 산출 retro PR 의 closure forcing function 3 step (ADR-045 §D-11 (5) 정합):

1. **Issue 단위 `[PMO]` prefix comment + state transition** —
   - Issue 단위 closure decision rationale comment 작성 (`[PMO] <decision_enum>: <rationale_with_verify_evidence>`)
   - state 전환: `gh issue close <N> --reason not_planned` (CLOSE_AS_OBVIATED / CLOSE_AS_SENTINEL / DEFER) OR `--reason completed` (PROMOTE)

2. **Retro PR open + auto-merge** —
   - Retro file §X close lane sub-section 안 closure summary table embed
   - Retro PR open (cfp-NNN-retro branch) + auto-merge (ADR-045 §결정 4 retro PR 자동 merge 정합)
   - closure evidence trail 영속화 (post-merge audit trail)

3. **`gate:retro-complete` label add OR `not_planned` reason close** —
   - 본 Story Issue (batch closure carrier Issue) 자체 = `gate:retro-complete` label add OR `not_planned` reason close (ADR-045 §결정 5 close-blocking 정합)
   - close-blocking gate 통과 확인 (ADR-045 §결정 5 정합)

**cross-ref**:

- **ADR-045 §D-11** = normative SSOT (본 §18 의 wording authority)
- **ADR-045 §D-9 / §D-10** = adjacent forcing function (escalation / pre-publish verify), 본 §18 = post-batch closure lifecycle disjoint axis
- **ADR-082 §결정 12** = retro-time verify-before-trust adjacent axis (PMOAgent retro write-time vs PMOAgent batch closure-time 분리)
- **playbook §13.5 PMOAgent 보고 기록** = `[PMO]` phase prefix comment 정합 batch closure 영역 sub-domain

