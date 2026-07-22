---
name: lane-self-write-boundary
description: Lane plugin self-write 책임 영역 lookup 시 (Orchestrator lane spawn 직전 owner path 확인). docs/** + GitHub Issue/PR/comment + label 영역의 lane별 write 경계를 정의한다.
tools: Read
---

# Lane Plugin Self-write Boundary

> 참조 테이블 skill — lane spawn 직전 해당 plugin 의 owner path 를 확인하세요.

`docs/**` + GitHub Issue/PR/comment + label 영역의 write 책임은 lane plugin 별로 분산. wrapper repo 자체에는 agent 0개 — Orchestrator 가 lane plugin 을 spawn 하면 lane plugin 이 자기 owner section 을 직접 write.

**Lane plugin owner path**:

| Lane plugin | docs/ self-write 영역 | GitHub self-write |
|---|---|---|
| codeforge-requirements | `docs/stories/<KEY>.md §2·§5·§6`, `docs/domain-knowledge/<area>/<topic>.md`, `docs/domain-knowledge/domain/<area>/lexicon.md` + `concept-dictionary.md` (DomainAgent consumer-scope owner — CFP-2453/ADR-091 Amd3) | `[요구사항]` prefix comment, phase:요구사항→phase:설계 transition, Discussions Q&A routing |
| codeforge-design | `docs/stories/<KEY>.md §3·§7·§11`, `docs/change-plans/<slug>.md`, `docs/adr/ADR-NNN-<slug>.md` (소비자 repo) / `archive/adr/ADR-NNN-<slug>.md` (plugin-codeforge wrapper 자기 — prune 이후 이동) | `[설계]` prefix comment, phase:설계→phase:설계-리뷰 transition |
| codeforge-review (CFP-35 v2 — pre-CFP-61 history) | `docs/stories/<KEY>.md §9` (각 Review PL) | `[설계-리뷰]` / `[구현-리뷰]` / `[보안-테스트]` prefix comment, gate:design-review-pass / gate:security-test-pass label, phase transition (review-verdict-v2). **(History only — CFP-61 부터 final §9 verdict + GitHub gate write 책임 Orchestrator 로 transfer)** |
| **codeforge-review (CFP-137 v4 — current SSOT, CFP-134 / ADR-035 정정 후)** | review-verdict-v4 packet 작성 (findings + `pl_recommendation`) — synthesis 만, Orchestrator 에 return. **final §9 verdict append + GitHub comment + gate label + phase transition 은 Orchestrator self-write** (Stage 0 spec §3.5 verbatim, ADR-022 Deprecated 후 Sonnet decider 자동 발동 무효) | (review-verdict 영역 GitHub write 는 Orchestrator) |
| codeforge-develop | `docs/stories/<KEY>.md §8·§8.5`, Phase 2 PR creation | `[구현]` prefix comment, phase:구현→phase:구현-리뷰 transition |
| codeforge-pmo | `docs/retros/<sprint>.md`, `docs/stories/<KEY>.md §11`, Epic Issue body, Milestone description | `[PMO]` prefix comment, Epic Milestone via gh api |

**Wrapper Orchestrator 단독 영역**:
- `docs/stories/<KEY>.md §10` FIX Ledger append (CFP-32 monopoly · `fix-event-v1` contract)
- **review-verdict 최종 write** (Story §9 append / GitHub comment / gate label / phase transition) — **CFP-134 / ADR-035 정정 후 (Stage 0 spec §3.5 verbatim)**: PL synthesis (findings + `pl_recommendation`) 만 lane plugin self-write 영역, **final §9 verdict append + GitHub comment + gate label + phase transition 은 Orchestrator self-write** (ADR-022 Deprecated 후 Sonnet decider 자동 발동 무효 — review-verdict v3 의 Sonnet 5-step 영역 NO-OP, v4 MAJOR bump 가 정식 제거 — CFP-137 / ADR-044 cutover 완료).
- general `docs/**` write (lane plugin owner 외)
- branch protection · CI workflow · cross-plugin schema templates

**Cross-cutting rule — cross-repo `gh` CLI write 시 `--repo <owner/repo>` 명시 의무** (INCIDENT-2026-05-17, mctrader-data#94 §6 carry-over):

모든 lane plugin + Orchestrator 의 GitHub self-write (`gh pr|issue <write-verb>` — create/edit/comment/close/merge/review 등) 는 **`--repo <owner/repo>` (또는 `-R`) 를 명시**해야 한다. `gh` CLI 는 cwd 의 git remote 로 대상 repo 를 silent resolve 하므로, cross-repo 세션 (예: mctrader-data + mctrader-hub) 에서 worktree/cd 위치에 따라 의도와 다른 repo 의 같은 번호 PR/issue 를 덮어쓰는 사고가 발생한다 (2026-05-17 박제: `gh pr edit 94` 가 mctrader-hub#94 description 을 덮어쓴 후 GitHub API 미노출로 복원 불가).

- **물리 안전망**: `hooks/cross-repo-gh-safety` (PreToolUse, `matcher: Bash`) 가 write-verb + `--repo`/`-R`/`GH_REPO` 부재 시 `exit 2` 차단. read-only verb (view/list/checks) = scope 외 (정보 조회, write 사고 0).
- **가이드 차원**: 본 rule = hook 미적용 환경 (다른 plugin / hook bypass) fallback 인지 경로.
- **bypass**: 의도된 단일-repo 작업 확신 시 `BYPASS_CROSS_REPO_GH_SAFETY=1` (scope disjoint — `BYPASS_CODEFORGE_PREREQ` / `BYPASS_WORKTREE_FIRST` 와 별 env).

**Cross-cutting rule — cross-repo worktree target authority verify-before-write** (CFP-1578 / [ADR-082 Amendment 21](../../archive/adr/ADR-082-write-time-self-write-verification-mandate.md) §결정 1 sub-scope 1-J):

`gh --repo` rule (filesystem-orthogonal API-level) 와 disjoint axis 의 filesystem write-target boundary 영역 — chief author / lane agent / Orchestrator 가 spawn prompt 작성 또는 직접 file write 직전 worktree target authority verify-before-write 의무. **Cross-repo write-target boundary matrix**:

| Target repo | Expected remote URL pattern | Owner content (4 single-owner doc + Story sections + retro 영역) |
|---|---|---|
| `wrapper` (plugin-codeforge) | `mclayer/plugin-codeforge` | `archive/adr/**` (prune 이후 이동 — 소비자 repo 는 `docs/adr/**`) + `docs/inter-plugin-contracts/**` + `templates/**` + `scripts/**` + `.github/**` + `CLAUDE.md` + `skills/**` + `hooks/**` |
| `internal-docs` (codeforge-internal-docs) | `mclayer/codeforge-internal-docs` | `plugin-codeforge/stories/<KEY>.md` + `plugin-codeforge/change-plans/<slug>.md` + `plugin-codeforge/retros/<sprint>.md` + `plugin-codeforge/specs/` + `plugin-codeforge/plans/` (ADR-013 dogfood-out SSOT path) |
| `marketplace` (marketplace) | `mclayer/marketplace` | `marketplace.json` mirrored field sync (4 field per ADR-063) |
| `consumer-<name>` (예: `mctrader-hub`) | `mclayer/<name>` | consumer overlay `.claude/_overlay/` + consumer Story file (consumer repo SSOT) |

4-tuple primitive (spawn prompt 작성 또는 직접 file write 직전):

1. **worktree target authority verify** — `git -C <worktree_abs_path> remote -v` 실행 → expected repo (위 matrix) 와 actual remote URL 일치 확인. mismatch 시 write 차단.
2. **spawn prompt `worktree_target_repo: <expected-repo-name>` field 의무** — anchor block 형식 명시 (enum: `wrapper` / `internal-docs` / `marketplace` / `consumer-<name>`).
3. **cross-repo 작업 sequence 시 명시적 worktree switch** — wrapper repo worktree 안에서 internal-docs PR 생성 시도 금지 (각 repo 별 worktree 분리, ADR-040 worktree convention 정합). cross-repo write 필요 시 별 worktree explicit create + cwd switch + write 의무.
4. **verified-via annotation `worktree_target_authority_verified: <bool>` field** — spawn prompt 안 명시.

- **물리 안전망** (Wave 2 deferred): `worktree-target-authority-verify` lint (mechanical wire = 별 sub-CFP, evidence-checks-registry warning tier).
- **가이드 차원**: 본 rule = Wave 1 behavioral mandate — hook 미적용 환경 fallback 인지 경로.
- **bypass**: `BYPASS_WORKTREE_TARGET_AUTHORITY=1` (Wave 2 wire 후, scope disjoint — `BYPASS_CROSS_REPO_GH_SAFETY` / `BYPASS_WORKTREE_FIRST` 와 별 env).
- **disjoint axis vs cross-repo `gh` rule**: `gh --repo` = API-level target binding (gh CLI 가 cwd 의 git remote 로 silent resolve 차단) / 본 rule = filesystem-level worktree target binding (write 직전 worktree path↔remote URL authority verify). 두 axis 모두 cross-repo write 사고 차단 영역 disjoint complement.
- **동인**: CFP-1539+CFP-1540 batch retro §4.1 #2 — PMOAgent retro spawn 시 internal-docs PR target 작성 시 wrapper repo plugin-codeforge worktree 안에서 `git worktree add` 시도 후 정정 발생 (wrapper repo worktree mis-target 첫 catch occurrence). ADR-013 dogfood-out internal-docs SSOT path + ADR-040 worktree convention 정합 영역 codify 부재 super-class gap closure. paired sibling = CFP-1559 Amendment 20 (Issue body stale claim pre-screen super-class, axis disjoint).

**4 single-owner doc** (CFP-26 Phase 0a 이후): `docs/{change-plans,adr,domain-knowledge,retros}/**` (소비자 repo) / `archive/adr/**` + `docs/{change-plans,domain-knowledge,retros}/**` (plugin-codeforge wrapper 자기 — ADR 만 archive 이동, prune 이후) 는 owner agent direct write — lane plugin 의 ArchitectAgent / DomainAgent / PMOAgent 자기 owner path write.

문서화 표준 4 single-owner doc 템플릿은 [`templates/`](../../templates/) — change-plan / adr 현재 존재, domain-knowledge schema / retro schema CFP-27 신설. owner agent는 본인 owner path write 시 해당 템플릿 schema 준수 필수 — `scripts/check-write-permission-redistribution.sh` (CFP-26) + 향후 frontmatter/section schema lint (CFP-27)에서 강제.

자세한 owner path / mechanism / trigger 는 각 lane plugin 의 `CLAUDE.md` `Self-write 책임` 표 (codeforge-{review,pmo,requirements,test,develop,design}) 참조.

**machine_readable_ssot**: `docs/domain-knowledge/domain/governance-principle/lane-self-write-ownership-matrix.yaml` — per-section owner-agent mapping YAML SSOT (CFP-722 §13.A, 2026-05-16) + `cross_plugin_doc_ownership` sub-tree (CFP-841 §13.B, 2026-05-17). 본 SKILL.md = human-readable mirror; drift-sync: yaml ↔ SKILL.md ↔ story-page-structure.md headings ↔ lint regex (4-way, yaml-as-canonical single-direction — CFP-841 Phase 2 §13.B 해소).
