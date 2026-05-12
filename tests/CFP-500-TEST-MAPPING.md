# CFP-500 Phase 2 — AC ↔ Test Mapping

Story `CFP-500` Phase 2 의 Acceptance Criteria 와 자동/정적 검증 source 매핑.
Story file SSOT: `<internal-docs>/wrapper/stories/CFP-500.md` §5.2.

## AC ↔ Test Matrix

| AC | 검증 종류 | 검증 source | 비고 |
|----|-----------|------------|------|
| **AC-1** | manual | `docs/adr/ADR-038-progress-visualization-todowrite.md` Amendment 2 (Phase 1 merge 완료, PR #444) | DesignReview lane PASS history (Iter 4, 2026-05-12 02:55 KST) |
| **AC-2** | manual + diff | `templates/.claude/hooks/SessionStart-codeforge-prereq-check.json.sample` — 7 top-level field (`_comment` / `_doc` / `_adr` / `_layer` / `_severity` / `_bypass` / `_limits` + nested `hooks`) | drift 6 + 신규 3 키 (`_adr` / `_layer` / `_limits`) inherit, `_prerequisite` drop |
| **AC-3** | runtime (test 2 keyword grep `MUST` / `first tool actions`) + static (heredoc) | `scripts/check-codeforge-prereq.sh` + `tests/scripts/test_check_codeforge_prereq.sh` runtime assertion (2)(3)(4)(5) | spec §2-2 verbatim prompt-injection 텍스트 |
| **AC-4** | runtime | `tests/scripts/test_check_codeforge_prereq.sh` 5 runtime assertion (PASS): (1) stdout non-empty / (2) `ToolSearch` / (3) `select:TodoWrite` / (4) `ADR-038` / (5) `first tool actions` | bash smoke test |
| **AC-5** | path + frontmatter + lint | `docs/domain-knowledge/domain/runtime/deferred-tool-and-session-start-hook.md` — frontmatter `kind: domain_fact` / `area: runtime` / `topic_slug: deferred-tool-and-session-start-hook` / `owner: ArchitectAgent`. `scripts/check-doc-frontmatter.sh` + `scripts/check-doc-locations.sh --full` PASS 의무 (CI) | ADR-056 §결정 1·2 정합 path |
| **AC-6** | manual diff | `docs/orchestrator-playbook.md` §1.1 0i + `CLAUDE.md` "세션 개시 의무" 1줄 supersede (CFP-375 / CFP-385 hook 위임 + 폴백 절차로 정확히 교체) | 다른 0a-h 항목 / 다른 단락 무손실 |
| **AC-6a** | manual diff | `docs/consumer-guide.md` §2h.1 `SessionStart prereq-check hook` subsection 신설 | drift / worktree-gc 와 동일 패턴 cp 명령 + manual merge 절차 |
| **AC-7** | manual + lint | `.claude-plugin/plugin.json` version 5.17.0 → 5.18.0 + description 끝에 CFP-500 entry append. marketplace sync PR = post-merge 의무 (별도 follow-up) | ADR-037 §결정 1(c) MINOR bump, ADR-016 mirrored field |
| **AC-8** | post-merge manual | (1) marketplace sync PR merge → (2) `/plugins install codeforge@mclayer` → (3) `bash scripts/check-codeforge-version-drift.sh` PASS → (4) wrapper repo 자체 `.claude/settings.json` `hooks.SessionStart[]` 에 prereq-check hook 등록 + 신규 세션 부팅 시 stdout prompt-injection 동작 manual 검증 | ADR-053 consumer 재구동, 외부 consumer sweep = Story-2 별도 |
| **AC-9** | CI lint | `check-doc-frontmatter.sh` / `check-doc-section-schema.sh` / `phase-gate-mergeable.yml` / `lane-evidence-check.yml` / `adr-sunset-criteria.yml` (CFP-389 / ADR-060 warning mode) | branch protection 4 required check + warning mode |
| **AC-10** | manual diff | Story §14 Lane Evidence rows + Phase 2 PR description `## Lane evidence` 블록 | ADR-031 / CFP-126 |
| **AC-11** | static grep | `tests/scripts/test_check_codeforge_prereq.sh` 정적 검증 stage (Section [1/2]): (a) shebang + `set -euo pipefail` / (b) single-quoted heredoc `<<'EOF'` / (c) filesystem touch 0 (`>>`, mkdir, rm, mv grep 0건) / (d) network call 0 (curl, wget, `gh api` grep 0건) | bash smoke test 첫 stage 가 정적 grep 자동화 |

## Smoke test 실행

```bash
bash C:/Users/mccho/.claude/worktrees/plugin-codeforge/cfp-500/tests/scripts/test_check_codeforge_prereq.sh
# Expected: All assertions PASS, exit 0
```

## Phase 2 PR scope (file 목록 — Phase 1 already merged)

신규 (4):
- `templates/.claude/hooks/SessionStart-codeforge-prereq-check.json.sample`
- `scripts/check-codeforge-prereq.sh`
- `tests/scripts/test_check_codeforge_prereq.sh`
- `docs/domain-knowledge/domain/runtime/deferred-tool-and-session-start-hook.md`

수정 (5):
- `docs/orchestrator-playbook.md` §1.1 0i + §3B.1 Preflight row 4 cross-ref 갱신
- `CLAUDE.md` "세션 개시 의무" 단락 0i 인라인 명시 supersede
- `.claude-plugin/plugin.json` version 5.17.0 → 5.18.0 + description append
- `.claude/settings.json` `hooks.SessionStart[]` 에 prereq-check entry append (wrapper dogfooding, AC-1a)
- `docs/consumer-guide.md` §2h.1 신설 (AC-6a)

Optional (1):
- `tests/CFP-500-TEST-MAPPING.md` — 본 mapping

Story / §8 / §8.5 / §14 = `<internal-docs>/wrapper/stories/CFP-500.md` (별도 internal-docs Phase 2 PR).
