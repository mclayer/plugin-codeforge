## 16. Post-merge automation flow (ADR-026 + CFP-74)

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

### 16.5 main 직접 push 금지 invariant

internal-docs cross-repo write 는 항상 branch (`<key>-post-merge-followup-prN`) + PR open 패턴. 사용자 admin merge 패턴 유지. 본 invariant 위반 시 ADR-024 위반 = policy_violation defect.

### 16.6 Idempotency

- Story §9 writer: 본 PR ref 의 row 이미 존재 시 skip (grep 기반 dedup)
- Telemetry counter: workflow_run_id 별도 unique entry (재실행 시 별도 entry)
- Phase label transition: 현재 phase == next phase 시 no-op

### 16.7 Boundary (Phase 1 scope, ADR-026 §결정 3)

- ✅ wrapper Orchestrator post-merge automation (4 action + telemetry)
- ✅ disable-by-flag + main 직접 push 금지
- ❌ Enforcement (whitelist 외 stop refusal) — Phase 2 ROI 평가 후 별도 CFP
- ❌ Consumer overlay path support — Phase 2 PMOAgent retro 후

---

