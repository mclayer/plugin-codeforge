---
title: Script Ownership Boundary Taxonomy
doc_type: domain_knowledge
category: governance
status: active
created: 2026-05-17
carrier: CFP-821
related_adrs: [ADR-039, ADR-061, ADR-005, ADR-064]
---

# Script Ownership Boundary Taxonomy

## 개요

본 문서 = CFP-821 Wave 3 Story-7 D3 deliverable. codeforge 플러그인의 script 파일 소유권 경계를 3 분류로 명문화한다. declarative SSOT only — mechanical lint enforcement은 별도 follow-up Issue 권장 (§5.4 OOS, ADR-064 minimal-change).

**Prior art**: Helm `templates/` (wrapper SSOT) vs `values.yaml` (consumer customization) / Ansible `roles/` (reusable) vs `playbooks/` (consumer orchestration) — codeforge 3 분류 taxonomy 동형 (Change Plan §6.4).

---

## 3 분류 Taxonomy

### Category 1 — Wrapper SSOT

**위치**: `${CLAUDE_PLUGIN_ROOT}/codeforge/scripts/*.sh` (plugin-installed 경로)

**ownership**: codeforge wrapper repo (`mclayer/plugin-codeforge`) 독점 소유.

**upgrade behavior**: upgrade 시 wholesale mirror (consumer touch 0). consumer가 이 경로의 파일을 직접 수정해서는 안 된다.

**예시**:
- `scripts/reconcile-overlay.sh` (CFP-745 Wave 2 Story-5 overlay 3-way merge)
- `scripts/check-wrapper-managed-block.sh` (CFP-702 D4 marker lint)
- `scripts/check-3way-version-parity.sh` (CFP-820 3-way version atomic)
- `scripts/setup-branch-protection.sh` (→ Category 3 참조: consumer-distributed)

**ADR-039 정합**: Subagent context에서 wrapper SSOT script는 Orchestrator가 inline whitelist 없이 직접 호출 금지. DeveloperPL의 subagent(DeveloperAgent)가 위임 실행.

---

### Category 2 — Consumer overlay

**위치**: consumer repo `scripts/*.sh` (consumer가 직접 작성)

**ownership**: consumer 프로젝트 독점 소유 (codeforge wrapper 무관).

**upgrade behavior**: codeforge upgrade 시 wrapper가 이 영역에 접근하지 않는다. consumer 자기 책임.

**예시** (consumer 영역):
- consumer 프로젝트 특화 배포 스크립트
- consumer가 직접 작성한 데이터 처리 스크립트
- ADR-039 §결정 2 consumer overlay 정의 파일 (`scripts/*.sh`)

**ADR-039 정합**: consumer overlay script는 codeforge 에이전트의 직접 수정 대상이 아니다. Orchestrator가 consumer에게 수정 지시를 내릴 수 있으나, agent가 직접 write하지 않는다.

---

### Category 3 — Mixed-zone (Distributed Templates)

**위치**: wrapper `templates/scripts/*.sh` → consumer cp `scripts/*.sh`

**ownership**: 초기 SSOT = wrapper (desired state). consumer가 bootstrap 시점에 복사해 소유권 이전.

**upgrade behavior**:
- bootstrap 시: `cp -n` (no-clobber) — consumer에 없으면 복사, 있으면 보존
- upgrade 시: reconcile (D4 marker block 안 = wrapper SSOT mirror / 밖 = consumer customize 보존)
- marker 부재 = `wholesale_mirror_with_user_visible_loss_report` fallback (ADR-027 §결정 7.C, EPIC-AC-4 silent overwrite 0)

**D4 marker syntax** (ADR-027 Amendment 3 §결정 7.A.1):
- `.sh` 파일: `# BEGIN wrapper-managed` / `# END wrapper-managed` (whole-line anchored)
- CFP-125 `bootstrap-consumer.sh` 패턴 차용

**예시**:
- `templates/scripts/setup-branch-protection.sh` → consumer `scripts/setup-branch-protection.sh`
- `templates/scripts/worktree-create.sh` → consumer `scripts/worktree-create.sh`
- `templates/scripts/manual-story-init-fallback.sh`

**ADR-039 정합**: Mixed-zone script는 DeveloperAgent가 Phase 2 PR에서 templates 경로에 작성 (wrapper SSOT). consumer deployment는 UpgradeAgent 또는 bootstrap 시 반영.

---

## 경계 규칙 요약

| 분류 | 위치 | upgrade behavior | consumer touch |
|---|---|---|---|
| **1 Wrapper SSOT** | `${CLAUDE_PLUGIN_ROOT}/codeforge/scripts/` | wholesale mirror | 금지 |
| **2 Consumer Overlay** | consumer repo `scripts/` (자기 작성) | wrapper 무관 | 자기 책임 |
| **3 Mixed-zone** | wrapper `templates/scripts/` → consumer cp | D4 marker reconcile | marker 밖만 허용 |

---

## ADR Cross-references

- **ADR-039** (Orchestrator subagent default): Category 1 script 호출은 DeveloperPL subagent 위임. consumer overlay는 Orchestrator 직접 write 금지. [ADR-039 §결정 1]
- **ADR-061** (Python script-writing convention): Category 1/3 script 중 Python 로직이 5줄 초과하거나 backslash escape를 포함하면 외부 `.py` 파일 의무 (bash heredoc 금지). [ADR-061 §결정 1]
- **ADR-005** (byte-identical self-app): Category 3 Mixed-zone의 templates 경로 원본 ↔ `.github/` 또는 `.github/workflows/` 미러는 byte-identical (ADR-005). script 파일은 consumer cp 후 diverge 허용 (D4 marker 범위 내).
- **ADR-064** (decision principle): 본 taxonomy = declarative SSOT only. mechanical lint는 별도 follow-up Issue 권장 — ADR-064 minimal-change + Story scope creep 회피.

---

## 보완 영역 (OOS — 별도 follow-up Issue)

bash 스크립트 내 top-level `local` keyword 남용 lint (Story-5 FIX iter F-CR-745-1 lineage) = 본 Story-7 scope 외. ADR-064 minimal-change + Story scope creep 회피 원칙으로 별도 codeforge-improvement Issue 권장.

관련 codeforge-improvement Issue: (follow-up — TBD)
