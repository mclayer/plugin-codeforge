# Contributing to codeforge

> **Note**: 본 plugin family 는 internal dogfood + mctrader 1 consumer 단계 (2026-05-08 시점). 외부 contributor 없음 — 본 가이드는 maintainer (mccho8865) 자체 dogfood + 향후 외부 contributor onboarding 용.

## Plugin family overview

7 plugin (wrapper + 6 lane plugin), 모두 [`mclayer/marketplace`](https://github.com/mclayer/marketplace) 경유 distribute:

| Plugin | Repo | Role |
|---|---|---|
| `codeforge` (wrapper) | mclayer/plugin-codeforge | Orchestration policy + CI templates + 0 agents (ADR-009) |
| `codeforge-requirements` | mclayer/plugin-codeforge-requirements | 4 agents (PL + Domain + Analyst + Researcher) |
| `codeforge-design` | mclayer/plugin-codeforge-design | 8 agents (PL + ArchitectAgent chief + 6 deputy) |
| `codeforge-review` | mclayer/plugin-codeforge-review | 5 agents (3 PL + 2 worker) |
| `codeforge-develop` | mclayer/plugin-codeforge-develop | 5 core agents + dynamic role:dev + presets |
| `codeforge-test` | mclayer/plugin-codeforge-test | 1 agent |
| `codeforge-pmo` | mclayer/plugin-codeforge-pmo | 1 agent |

## Branch policy (ADR-024)

- 모든 변경 = Story-scoped feature branch + PR 경유 (main 직접 push 금지)
- Branch naming: `cfp-<NNN>[-<slug>]` 또는 `cfp-<NNN>/<lane>[/<sub>]` (hierarchical)
- main branch protection = 4 required check + `enforce_admins: true`

## Project key (CFP-NNN) atomic reservation (ADR-036 / CFP-260)

- KEY = `<PREFIX>-<Issue#>` (GitHub atomic Issue numbering 위임 — race-free)
- brainstorming 시점 KEY 사전 확보 = `templates/github-issue-forms/cfp-reserve.yml` 발의 → 받은 # 가 KEY
- 30 일 미진행 reservation 자동 close (`reservation-cleanup.yml`)

자세한 사용 패턴: [`docs/orchestrator-playbook.md`](docs/orchestrator-playbook.md) §1.2.0.

## Conventional Commits (ADR-037 / CFP-261)

본 plugin family 는 [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/) 형식 의무. CI workflow `check-plugin-version-bump.yml` 가 PR 단계 검사.

### Commit type → version bump signal

| Commit prefix | Bump signal | 예시 |
|---|---|---|
| `feat!:` 또는 `BREAKING CHANGE:` footer | **MAJOR** | `feat!: drop ADR-022 Sonnet decider (CFP-135)` |
| `feat:` | **MINOR** | `feat(cfp-260): add cfp-reserve.yml Issue Form` |
| `fix:` | **PATCH** | `fix(cfp-133): broken link in ADR-024` |
| `docs:` | **PATCH** | `docs(playbook): clarify §1.2.0 brainstorming flow` |
| `chore:` / `refactor:` / `style:` / `test:` / `build:` / `ci:` / `perf:` | **PATCH** | `chore: bump dependency lock` |

### Plugin SemVer rule (ADR-037 §3.1, Option β)

| Surface | MAJOR | MINOR | PATCH |
|---|---|---|---|
| Agent file | 삭제 / 역할 재정의 | 추가 | minor edit |
| Skill file | 삭제 / redefine | 추가 | minor edit |
| Hook script | 삭제 / required hook 추가 / behavior break | 선택 hook 추가 | config-only |
| Template (workflow / Form) | required workflow 추가 / story schema break | 선택 workflow 추가 / Form 추가 / additive schema | comments only |
| Inter-plugin contract MAJOR (ADR-008) | 해당 plugin MAJOR | — | — |
| Inter-plugin contract MINOR (ADR-008) | — | 해당 plugin MINOR | — |
| CLAUDE.md SSOT semantic | 기존 artifact invalidate | additive guidance | typo / clarity |
| ADR | binding migration 동반 | 새 ADR / additive amendment | editorial fix |
| Bootstrap script | 기존 install fail 유도 | 선택 setup step | comments / help |
| Slash command | 삭제 / behavior break | 추가 | wording / help |
| Dependency requirement | 하드 minimum 상승 | 선택 새 tool 지원 | docs wording |
| Marketplace mirrored field | — | description / author 변경 | typo |

### Wrapper-coupling trigger 3종 (wrapper plugin only, ADR-037 §결정 2)

wrapper plugin (codeforge) 은 자체 surface 변경 외에 다음 3 trigger 시 추가 MAJOR:

- **T1**: 어느 lane plugin 의 inter-plugin contract MAJOR 발생 시
- **T2**: 어느 lane plugin 의 agent file 삭제 / 역할 재정의 시
- **T3**: family-wide invariant ADR (ADR-009 / ADR-016 / ADR-024 / ADR-008 / ADR-037) supersede 시

상세 SSOT: [`docs/adr/ADR-037-plugin-version-bump-rule.md`](docs/adr/ADR-037-plugin-version-bump-rule.md).

### Bypass

긴급 hotfix 시 `BYPASS_VERSION_BUMP=1` + `BYPASS_VERSION_BUMP_REASON=<text>` env 로 우회 가능 (audit trail 보존). hotfix-playbook 정합 ([`docs/hotfix-playbook.md`](docs/hotfix-playbook.md)).

## Marketplace mirror sync (ADR-016)

7 plugin 의 mirrored 필드 4종 (`name`·`version`·`description`·`author`) → `mclayer/marketplace/marketplace.json` sync 의무. plugin PR merge 직후 mirror sync PR open 의무 (parity CI 도입 전까지 author manual obligation).

## CI required checks (4 종)

main branch protection = 다음 4 check PASS 의무:

1. `phase-gate-mergeable` — Story phase progression 정합
2. `doc frontmatter schema (CFP-28)` — ADR / Change Plan / Story frontmatter
3. `doc section schema (CFP-28)` — 필수 section 존재
4. `invariant-check` — wrapper-only / agent topology / contract version 등 invariant

추가 check (advisory): `markdown internal links` / `inter-plugin-drift` / `marketplace mirrored fields drift` / `label-registry sync` / 등.

## Story discipline (ADR-013 / CFP-45)

매 변경 시작 시 cutoff 분류 — 강제 / 면제 결정. 모호 시 강제 측 분류.

**강제 대상**: 신규 ADR / 아키텍처 변경 / agent topology / workflow 변경 / SSOT semantic / breaking change.
**면제 대상**: typo / 링크 / lint auto-fix / dependency lock / README 단순 문구 수정.

면제 시 commit body 에 `Story 면제 사유: <이유>` 1줄 명시.

## Internal-docs (codeforge-internal-docs)

Plugin repo 작업 시 brainstorming spec / Change Plan / Story / Retro 는 [`mclayer/codeforge-internal-docs`](https://github.com/mclayer/codeforge-internal-docs) 에 SSOT (ADR-013 / ADR-017). plugin repo 의 `docs/{stories,change-plans,domain-knowledge,retros}/` 는 gitignored.

## Resources

- 정책 SSOT: [`CLAUDE.md`](CLAUDE.md)
- 작업 흐름 SSOT: [`docs/orchestrator-playbook.md`](docs/orchestrator-playbook.md)
- Consumer 가이드: [`docs/consumer-guide.md`](docs/consumer-guide.md)
- ADR list: [`docs/adr/`](docs/adr/)
- Inter-plugin contracts: [`docs/inter-plugin-contracts/`](docs/inter-plugin-contracts/)
