---
kind: domain_fact
type: domain-knowledge
area: github-actions
topic_slug: mcp-issue-write-labels-zero-effect
title: MCP `mcp__github__issue_write` labels field zero-effect — verify-before-trust + gh CLI fallback 의무
status: Active
tags:
  - github-actions
  - mcp-tool
  - issue-write
  - labels-field
  - zero-effect-bug
  - verify-before-trust
  - gh-cli-fallback
  - workaround-codification
related_adrs:
  - ADR-039     # Orchestrator subagent default (MCP tool 직접 호출 inline whitelist 영역 외)
  - ADR-052     # Codex proactive check touchpoints (verify-before-trust 의 외부 worker output 영역, MCP write tool output 도 verify 의무 sub-domain instantiate)
  - ADR-070     # Codex verify-before-trust (외부 worker output ground truth direct read verify)
  - ADR-073     # Orchestrator verify-before-assert (cross-repo state / assumption 직 verify)
  - ADR-082     # Write-time self-write verification mandate (lane agent self-write 영역, MCP write tool output verify 의무 disjoint axis sub-domain)
related_stories:
  - CFP-1439    # 본 codify carrier (MCP `issue_write` labels field zero-effect 증거 12 Issue + 3 AC 발의)
  - CFP-1415    # Mega-Epic Confluence-as-derived-mirror governance standardization 발의 batch (12 Issue 영향, 본 bug 발견 carrier)
created: 2026-05-25
updated: 2026-05-25
---

# MCP `mcp__github__issue_write` labels field zero-effect — verify-before-trust + gh CLI fallback 의무

## Summary

MCP `mcp__github__issue_write` 의 `create` 또는 `update` operation 호출 시 `labels` field 가 silent zero-effect (다른 field 정상 적용, labels 만 빈 배열). 12 Issue evidence (CFP-1415 brainstorming batch). 후속 `gh issue edit --add-label` 호출 의무 + post-call verify (ADR-073 §결정 1 정합).

## Problem

MCP `mcp__github__issue_write` 의 `create` / `update` operation 호출 시 request body 안 `labels` field 가 명시되어도 GitHub Issue 의 실 labels 는 빈 상태. body / title / state 등 다른 field 는 정상 적용 — labels field 만 silent zero-effect.

미인지 시 발의된 Issue 가 unlabeled (`phase:unclassified` auto-classification 만 발생) 상태로 lane spawn 차단 + workflow filter (`gh issue list --label X`) zero-result.

## Usage

MCP `issue_write` create/update 직후 반드시 `gh issue edit --add-label` 별 호출로 label 보정 + 응답 verify (ADR-073). 아래 Pattern A (single Issue) / Pattern B (batch) / Pattern C (single-label-per-call atomic fail 회피) 의무 답습.

## 정의

본 SSOT 는 MCP `mcp__github__issue_write` (Anthropic MCP github plugin tool) 의 `labels` field 가 **silent zero-effect** 임을 codify 한 wrapper-scope authoritative reference. 본 quirk 의 root cause 는 미확정 (CFP-1439 AC-1 별 carrier 영역). 본 SSOT 는 mitigation workaround (gh CLI fallback) 와 verify-before-trust 의무를 명문화.

**evidence** (CFP-1439 sentinel):

- 영향 범위: CFP-1415 Mega-Epic brainstorming batch **12 Issue 전건** (#1415 / #1417 / #1418 / #1419 / #1420 / #1421 / #1424 / #1425 / #1426 / #1427 / #1428 / #1429) — MCP `issue_write` create 시 모두 빈 label 상태로 OPEN.
- PMOAgent (Sonnet → Opus fallback) 가 batch 발의 후 발견 + 12 Issue 모두 `gh issue edit <#> --add-label` 후속 호출로 label 보정.
- body / title 등 다른 field 정상 적용 (labels field 만 zero-effect).
- 발의 일: 2026-05-24 KST.
- 본 codify 일: 2026-05-25 KST (S5 Theme 2 carrier).

## 컨텍스트

### Hypothesis (verify 미완료, CFP-1439 AC-1 영역)

3 가설 (본 SSOT 단언 없음, verify-via reproducible test 의무):

1. **MCP github tool 권한 model 분리** — `mcp__github__issue_write` 가 `issues:write` 권한만 보유, `labels:write` 별 권한 분리 → labels 적용 silent skip. verify path: GitHub fine-grained PAT scope 비교 + MCP tool definition schema 확인.
2. **MCP tool 자체 bug** — `labels` field 가 schema 에 정의되나 backend mapping 안 됨 (Anthropic MCP github plugin 영역 bug). verify path: 다른 codeforge plugin 의 MCP write 실 호출 결과 비교 + MCP github plugin 버전 확인.
3. **gh-vs-MCP label resolution mismatch** — label 이름 case-sensitivity / typo / repo 에 label 미존재 (auto-create 안 됨). verify path: `gh label list` 결과와 cross-check + 12 Issue label 이름 verbatim verify.

root cause 확정 = CFP-1439 AC-1 (별 carrier 영역).

### verify-before-trust 4-layer governance sub-domain 위치

본 bug 는 4-layer verify-before-trust governance (ADR-073 / ADR-070 / ADR-082 / ADR-045 §D-9) 의 **5번째 sub-domain (MCP write tool output verify)** 위치:

| Layer | ADR | 영역 |
|---|---|---|
| 1 | ADR-073 | Orchestrator verify-before-assert (cross-repo state / assumption) |
| 2 | ADR-070 | Codex verify-before-trust (외부 worker output) |
| 3 | ADR-082 | Write-time self-write verification (internal lane agent self-write 값) |
| 4 | ADR-045 §D-9 | PMOAgent retro corpus enumeration cross-Story pattern_count escalation |
| **5 (본 entry)** | (ADR-073 disjoint sub-axis 후보) | **MCP write tool output verify** — request body 안 명시한 field 가 응답 / 실 state 에 반영됐는지 post-call verify 의무 (silent zero-effect 차단) |

본 sub-domain 은 ADR-073 §결정 1 verify-before-assert 의 instantiate — Orchestrator 가 MCP write tool 호출 후 응답을 trust 하기 전에 **request body 와 실 state 의 1:1 mapping** 을 verify 의무. silent zero-effect 발견 시 immediate fallback (gh CLI) + audit.

## 핵심 규칙

### 규칙 1 — MCP `issue_write` create/update 직후 `gh issue edit --add-label` 후속 호출 의무

MCP `mcp__github__issue_write` 의 `create` 또는 `update` operation 호출 시 `labels` field 명시 여부 무관하게 직후 `gh issue edit <#> --add-label <name>` 호출 의무. agent prompt 안 explicit instruction 의무 (silent skip 차단).

### 규칙 2 — single label per `gh edit` call (multi-label atomic fail 회피)

`gh issue edit` / `gh pr edit` 에서 `--add-label LBL_A --add-label LBL_B` 한 호출 안 다중 label 첨부 시, **존재하지 않는 label 1개라도 있으면 호출 전체 abort** (atomic fail). 따라서 label 별로 1 call 분리가 안전.

본 분리 호출 pattern 은 CFP-1322 / PR #1513 에서 실 적용됨 (4 label 첨부 시 multi-label 1 call 이 1 label not-found 로 전체 abort → label 별 분리 호출로 해결).

### 규칙 3 — post-call verify 의무 (ADR-073 §결정 1 정합)

`gh issue edit --add-label` 후속 호출 후 반드시 `gh issue view <#> --json labels --jq '[.labels[].name]'` 로 실 labels 응답 verify. 응답 labels 가 request labels 와 1:1 match 안 되면 immediate audit + bypass-justification PR/Issue comment 부착.

### 규칙 4 — Pattern A/B/C 답습 (Workaround codify)

**Pattern A — single Issue create (label 동시 부착)**:

```bash
# Step 1: MCP create (labels field 는 일단 비워두거나 명시해도 zero-effect)
mcp__github__issue_write({operation:"create", title:"...", body:"...", labels:["type:story","plugin:wrapper"]})
# → 응답: Issue #N created, but labels = []

# Step 2: gh CLI fallback 의무
gh issue edit N --add-label "type:story"
gh issue edit N --add-label "plugin:wrapper"

# Step 3: post-call verify (ADR-073 §결정 1 정합)
gh issue view N --json labels --jq '[.labels[].name]'
# → 응답 labels = ["type:story", "plugin:wrapper"] verify
```

**Pattern B — batch Issue create (N Issue, ≥2N API call)**:

```bash
for issue_data in batch; do
  mcp__github__issue_write({operation:"create", ...})         # Step 1: create
  for lbl in $LABELS_FOR_ISSUE; do
    gh issue edit $NEW_ID --add-label "$lbl"                  # Step 2: label boost (single per call)
  done
done
gh issue list --json number,labels --jq '.[] | select(...)'  # Step 3: batch verify
```

**Pattern C — single-label-per-call (atomic fail 회피, 규칙 2 정합)**:

```bash
gh issue edit N --add-label "lbl-A"
gh issue edit N --add-label "lbl-B"
gh issue edit N --add-label "lbl-C"
# verify: gh issue view N --json labels --jq ...
```

## 경계

### scope 내 (본 SSOT codify 영역)

- MCP `mcp__github__issue_write` `create` / `update` operation 의 `labels` field zero-effect codify.
- Workaround (gh CLI fallback) 의무 + verify-before-trust 의무 명문화.
- 4-layer verify-before-trust governance sub-domain 5번째 위치 정의.
- Pattern A/B/C 답습 영역.

### scope 외 (별 carrier 영역)

- **root cause 확정** (3 hypothesis verify-via reproducible test) — CFP-1439 AC-1 별 carrier.
- **AC-2 root cause 별 mitigation 결정** (consumer-guide PAT scope / upstream Issue report / label 사전 check script) — CFP-1439 AC-2 별 carrier.
- **AC-3 workaround 자동화** (PMOAgent batch 발의 script 안 자동 `gh issue edit --add-label` 보정) — codeforge-pmo plugin scope 별 carrier.
- **cross-plugin agent prompt sweep** — 8 lane plugin (codeforge-{requirements,design,develop,review,pmo,test,deploy,deploy-review}) agent prompt 안 `issue_write` 호출 sites 모두 explicit fallback instruction 추가. wrapper scope 외, cross-plugin Story carrier 영역.
- **ADR amendment** (ADR-073 sub-axis sub-scope 신설 또는 ADR-082 §결정 1 layer 1 sub-scope 확장) — pattern_count 추가 evidence 시 ADR escalation 영역 (현재 본 SSOT codify 단계, ADR 강화 = 별 carrier).
- **MCP github plugin upstream PR** (Anthropic 영역) — codeforge governance 영역 외.

## 관련 ADR

- **ADR-039** — Orchestrator subagent default. MCP tool 직접 호출은 inline whitelist 4-entry 영역 외 (`mcp__github__*` 사용은 PMOAgent / lane plugin agent self-write 영역). 본 quirk 의 발견 lineage = PMOAgent batch 발의 후속 작업.
- **ADR-052** — Codex proactive check touchpoints. verify-before-trust 의 외부 worker output 영역. 본 sub-domain (MCP write tool output) = ADR-052 verify-before-trust 5 sub-scope 의 직접 인접 패턴 (request/response mapping verify).
- **ADR-070** — Codex verify-before-trust. 외부 worker output ground truth direct read verify 의무. 본 SSOT 의 `gh issue view` post-call verify = ADR-070 §결정 1 direct verify 동일 pattern.
- **ADR-073** — Orchestrator verify-before-assert. §결정 1 verify-before-assert primitive = 본 SSOT 의 verify-before-trust 4-layer 5번째 sub-domain 의 direct parent. transition trigger enum 확장 후보 (`mcp_write_tool_response` 5번째 entry, evidence-gated promotion 영역).
- **ADR-082** — Write-time self-write verification mandate. lane agent self-write 영역 (scope a-d). 본 SSOT 의 MCP write tool output verify = ADR-082 disjoint axis sub-domain (lane self-write ↔ MCP tool output 분리).

## 변경 이력

- **2026-05-25 (CFP-1439)** — 본 SSOT codify (S5 Theme 2 carrier). 12 Issue evidence + 3 hypothesis + Pattern A/B/C workaround + 4-layer verify-before-trust 5번째 sub-domain 위치 정의. wrapper scope codify 한정 (cross-plugin sweep + root cause 확정 + AC-2/3 = 별 carrier 영역).
