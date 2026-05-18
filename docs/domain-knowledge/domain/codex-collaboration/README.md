---
title: Codex Collaboration — narrative SSOT hub
area: codex-collaboration
introduced_by: CFP-946-A
parent_epic: CFP-946
status: active
date: 2026-05-18
related_adrs:
  - ADR-052  # Codex Proactive Check 6 touchpoint SSOT
  - ADR-070  # Codex verify-before-trust pattern SSOT
  - ADR-081  # Codex worker prompt boilerplate composition SSOT
  - ADR-082  # Write-time self-write verification mandate (disjoint super-class)
  - ADR-073  # Orchestrator verify-before-assert (disjoint layer)
  - ADR-064  # decision principle mandate (forbid-list 13 어휘)
related_files:
  - docs/adr/ADR-052-codex-proactive-check-touchpoints.md
  - docs/adr/ADR-070-codex-verify-before-trust.md
  - docs/adr/ADR-081-codex-worker-prompt-boilerplate.md
  - docs/orchestrator-playbook.md
  - CLAUDE.md
---

# Codex Collaboration — narrative SSOT hub

본 페이지 = codeforge wrapper 의 **Codex worker integration 운영 narrative SSOT** (CFP-946-A carrier, parent_epic CFP-946 P1 escalate_user). ADR-052 / ADR-070 / ADR-081 3 ADR 의 cross-ref hub.

## §1. 배경

codeforge wrapper 는 `codex@openai-codex` plugin 의 codex CLI runtime 을 외부 worker 로 활용해 6 touchpoint Codex proactive check 채널을 운영한다 ([ADR-052](../../../adr/ADR-052-codex-proactive-check-touchpoints.md)). 외부 worker output 의 신뢰 boundary 는 ADR-070 verify-before-trust pattern 으로 codify, dispatch prompt 의 composition 은 ADR-081 boilerplate SSOT 로 codify.

본 narrative SSOT = 위 3 ADR 의 운영 narrative cross-ref hub. 신규 결정 채택은 본 페이지 영역 외 — 결정 본문 SSOT 는 각 ADR.

## §2. USING vs OWNING 분리 (load-bearing invariant)

ADR-070 §결정 D1-B 본문 verbatim:

> "Codex worker 의 sandbox 자체 확장 (codex@openai-codex plugin 영역) — codex CLI runtime SSOT 영역, 본 ADR scope 외 (codex@openai-codex plugin 자체 영역)"

본 narrative 가 다루는 영역 = **USING boundary** 한정 (codeforge wrapper Orchestrator 가 codex worker 결과 신뢰 boundary 운영). **OWNING boundary** (codex@openai-codex plugin 자체 sandbox runtime / network policy / CLI 영역) = codex@openai-codex plugin SSOT, 본 페이지 scope 외.

## §3. 8 occurrence sentinel lineage

Codex worker sandbox-level file system access 실패가 누적 9 회 occurrence sentinel — parent_epic CFP-946 P1 escalate_user 산물:

| Sentinel # | Story | 일자 | 영역 | 처리 substitution path |
|---|---|---|---|---|
| 1 | CFP-506 | 2026-05-13 | touchpoint #4 file Read ERR | inline_orchestrator_verify (verbatim 첨부 후 re-spawn) |
| 2 | CFP-506 | 2026-05-13 | touchpoint #6 4 findings false positive | inline_orchestrator_verify (direct file Read verify reject) |
| 3 | CFP-520 | 2026-05-13 | touchpoint 6종 skip | fallback_skip_with_marker (derived default skip) |
| 4 | CFP-530 | 2026-05-13 | touchpoint #6 skip option B | fallback_skip_with_marker |
| 5 | CFP-919 | 2026-05-17 | Epic B Story-1 touchpoint #2 sandbox fail | inline_orchestrator_verify |
| 6 | CFP-920 | 2026-05-17 | Epic B Story-2 touchpoint #2 sandbox fail | inline_orchestrator_verify |
| 7 | CFP-921 | 2026-05-17 | Epic B Story-3 touchpoint #2 sandbox fail | inline_orchestrator_verify |
| 8 | CFP-923 | 2026-05-17 | Epic B Story-4 touchpoint #2 sandbox fail | inline_orchestrator_verify |
| 9 | CFP-946-A | 2026-05-18 | 본 Story-A Phase 1 PR reentrant | manual_substitution_declare + fallback_skip_with_marker (substitution path 3-enum codify carrier) |

본 sentinel lineage = ADR-052 Amendment 8 + ADR-070 Amendment 3 의 evidence base. Sentinel #4 strike #8 (parent_epic CFP-946) 가 substitution path 3-enum codification 의 escalate_user trigger.

## §4. 3 ADR cross-ref hub

본 page 의 핵심 역할 = 3 ADR 의 normative anchor 분리 명시:

| ADR | normative scope | 결정 본문 SSOT |
|---|---|---|
| [ADR-052](../../../adr/ADR-052-codex-proactive-check-touchpoints.md) | **6 touchpoint behavior** (dispatch trigger + ProactiveCheckPacket v1 schema + 처리 결과 + mandatory/optional 분기) | D1-D4 + Amendment 1-8 본문 |
| [ADR-070](../../../adr/ADR-070-codex-verify-before-trust.md) | **verify-before-trust pattern** (Codex output ground truth verify 의무 + reject 흐름 + Story §10 false positive count tally + **substitution scope 3-path enum codify**) | D1-D5 + Amendment 1-3 본문 |
| [ADR-081](../../../adr/ADR-081-codex-worker-prompt-boilerplate.md) | **prompt boilerplate composition** (3 mandatory section + verify-before-trust scope 5 sub-scope + 3-lane partition + severity calibration rubric) | D1-D5 + D6 + Amendment 1 본문 |

3 ADR 의 normative anchor scope 침범 0 — 각 ADR 영역 disjoint.

## §5. Substitution scope 3-path enum (운영 narrative)

ADR-070 §결정 D1 expansion (Amendment 3, CFP-946-A) 의 운영 narrative — 결정 본문 SSOT 는 ADR-070, 본 §5 는 narrative 만:

- **`inline_orchestrator_verify`** (default) — 정상 Codex worker dispatch + Orchestrator 가 finding evidence 의 ground truth 를 own working directory 안 file Read / Glob / Grep direct verify. mismatch 시 verdict reject + Story §10 false positive count tally + Orchestrator override rationale 4종 (ADR-070 §결정 D3).
- **`manual_substitution_declare`** — sandbox 영역 외 file (internal-docs / sibling repo / cross-plugin path) verify task 필요 시 채택. Codex worker spawn 직전 substitution scope 명시 declare (spawn prompt `task` field 본문 또는 별도 sub-field `substitution_scope`). Story §10 marker = `[codex-substitution-scope-declared: <scope-enum>]` (1 회/spawn).
- **`fallback_skip_with_marker`** — Codex CLI 미가용 / sandbox network-block 확정 / reentrant 위험 영역 채택. Codex worker spawn 자체 skip + Orchestrator 가 substitution 후속 동작 단독 수행 (verify-before-trust 5 sub-scope 全 적용, ADR-081 §결정 D2). Story §10 marker = `[codex-sandbox-fallback: <fail-mode>]` (1 회/spawn, fail-mode 6 enum).

**6 touchpoint × 3-enum cross-matrix**: 각 touchpoint 의 default + manual_substitution_declare trigger + fallback_skip_with_marker trigger 표 = [ADR-052 Amendment 8](../../../adr/ADR-052-codex-proactive-check-touchpoints.md) §A1 SSOT.

**decision tree narrative**: [`substitution-scope-decision-tree.md`](substitution-scope-decision-tree.md) (본 page 자매 narrative).

## §6. verify-before-trust 5 sub-scope (ADR-081 §결정 D2 cross-ref)

substitution path enum 3 중 어느 case 채택해도 Orchestrator verify-before-trust 5 sub-scope 무조건 적용:

1. **file scope** — grep + verbatim quote (file content full or partial)
2. **dir scope** — recursive grep + count (file path enumeration)
3. **cross-repo** — gh api + commit SHA pin (`mcp__github__get_file_contents` 또는 `gh api repos/.../contents/<path>?ref=<sha>`)
4. **grep count claim active vs historical** — active grep count (현재 main HEAD) vs historical grep count (이전 commit) 차원 분리 명시
5. **ADR §결정 번호 정확성** — ADR 인용 시 §결정 번호 + Amendment number 정확성 (ADR-052 Amendment 8 ≠ Amendment 5)

substitution path = "Codex worker substitution" 이지 verify-before-trust 면제 아님. 결정 본문 SSOT = ADR-081 §결정 D2.

## §7. 운영 invariant

- **3-enum exhaustive** — 4번째 path 발생 = ADR-070 §결정 D1 expansion 거절된 대안 영역 (auto-retry / 외부 verify proxy / multi-source consensus 등). 별 follow-up CFP carrier 영역.
- **declaration-only retain (ADR-070 §D5 precedent chain)** — substitution path 3-enum codification = mechanical lint 부재. ADR-070 §D5 declaration-only retain precedent + ADR-082 §결정 6 + ADR-081 §D5/§D6.e + ADR-076 §결정 6 fail-closed clause precedent chain 5번째 link. `mechanical_enforcement_actions: []` retain.
- **KPI deferred** — `substitution_count` + `verify_failure_rate` 정량 측정 (threshold=5 / 15%) 는 post-merge follow-up CFP carrier 영역. 본 narrative 의무 = prose tally only (Story §10 marker grep count, lint 없음).

## §8. Story-B 영역 cross-ref (Story-A scope 외)

본 narrative 의 USING boundary 운영 anchor + Story-B 의 mechanical USING (Codex CLI `--allow-network` flag wire + spawn prompt `network_scope` 3-tier enum field + `codex-network-scope-presence` warning-tier lint + graceful degradation 3 fail-mode fallback + `hotfix-bypass:codex-sandbox-substitution` label) 가 cross-ref binding. Story-B Amendment 본문 작성 시 본 narrative page 에 외부 anchor append (GH Actions per-job grant 패턴 + Helm/Docker network policy + Codex CLI `--allow-network` evidence host).

## §9. 관련 페이지

- [`substitution-scope-decision-tree.md`](substitution-scope-decision-tree.md) — substitution path 3-enum decision tree (trigger × Story §10 marker × verify-before-trust 5 sub-scope cross-matrix)
- [ADR-052](../../../adr/ADR-052-codex-proactive-check-touchpoints.md) — 6 touchpoint × 3-enum cross-matrix SSOT (Amendment 8)
- [ADR-070](../../../adr/ADR-070-codex-verify-before-trust.md) — substitution path 3-enum normative anchor SSOT (§결정 D1 expansion, Amendment 3)
- [ADR-081](../../../adr/ADR-081-codex-worker-prompt-boilerplate.md) — boilerplate composition SSOT (3 mandatory section + verify-before-trust 5 sub-scope)
- [playbook §3.10](../../../orchestrator-playbook.md) — Codex Proactive Check dispatch + substitution path 3-enum + 결과 처리 SSOT
