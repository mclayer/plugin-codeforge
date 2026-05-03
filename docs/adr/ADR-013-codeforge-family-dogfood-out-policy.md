---
adr_number: 13
title: Codeforge Family Dogfood-out Policy
status: Adopted
category: Team & Process
date: 2026-04-30
related_files:
  - CLAUDE.md (canonical dogfood policy + internal-docs pointer)
  - docs/superpowers/specs/2026-04-30-cfp-45-dogfood-out-restructure-design.md (parent CFP)
  - mclayer/codeforge-internal-docs (NEW external repo — dogfood artifact monorepo)
related_stories:
  - CFP-45
  - CFP-56
---

## 상태

Adopted (2026-04-30) — CFP-45 PR-I 머지 시점.

**Amendment 1 (2026-05-01) — CFP-56**: Brainstorming/writing-plans skill override path enforcement 정책을 ADR-017로 추가. `docs/superpowers/specs/**`와 `docs/superpowers/plans/**`가 plugin repo PR에 나타나면 CI가 fail-closed 하며, internal-docs 경로가 authoritative artifact lane이다. 검사 로직은 `scripts/check-dogfood-artifact-paths.sh`, CI는 `.github/workflows/dogfood-artifact-paths.yml` (template: `templates/github-workflows/dogfood-artifact-paths.yml`).

## 컨텍스트

ADR-009 ζ arc 가 wrapper-only decomposition 으로 agent code 분리 완료. 그러나 dogfood artifacts (specs / plans / retros / stories / change-plans) 는 7 plugin repo 에 잔류 — plugin install footprint 부담 (wrapper 단독 1.5 MB / 78 file).

Plugin install mechanism = git clone of whole repo. plugin.json 에 `files` filter 부재. dogfood artifact 가 사용자 머신에 모두 다운로드.

CFP-44 (wrapper CLAUDE.md compression) 직후 사용자 진단:

> "codeforge 플러그인 계열의 변경에 대해서는 설계문서와 superpowers를 보존하지 않기로 하자. plugin이 너무 무거워진다."

Codex (gpt-5.4) 3 회 상담 후 (C) Aggressive scope + hybrid Action placement + bidirectional Issue↔Story binding 결정.

## 결정

7 plugin repo (mclayer/plugin-codeforge + mclayer/plugin-codeforge-{review, pmo, requirements, test, develop, design}) 의 dogfood artifacts 는 단일 monorepo `mclayer/codeforge-internal-docs` (Public) 보유:

1. **Plugin repo 잔류**: runtime SSOT (CLAUDE.md / playbook / ADR / inter-plugin-contracts / templates / scripts / agents / presets)
2. **Internal-docs 보유**: specs / plans / retros / stories / change-plans (7 plugin family folder × 5 subdir)
3. **Story workflow Action** (4종) 위치: internal-docs 측 (story-owned). plugin-side 는 phase-gate-mergeable cross-repo validation 만
4. **Phase 1 PR** = internal-docs (Story §1-7 + change-plan + ADR draft). **Phase 2 PR** = plugin repo (코드 변경). **§8-11 commit** = internal-docs
5. **Issue ↔ Story binding** (bidirectional): plugin repo Issue body `story_uri:` + Story file frontmatter `story_issues: [{repo, number}]`
6. **Cross-repo credential**: GitHub App (mclayer org-level) — fail-closed 시 명확한 error + admin override 절차
7. **History rewrite** = 별도 후속 CFP (CFP-45 는 working tree cleanup 까지)

## 결과

**달성**:
- Plugin install footprint 절감 — wrapper 1.5 MB → ~1 MB working tree (history 잔존)
- Dogfood artifact 단일 search surface (cross-plugin CFP 추적 용이)
- Plugin repo PR diff 가 순수 code change — dogfood noise 제거
- ADR-013 = future drift detection anchor

**비용**:
- Cross-repo Plugin PR mergeability 가 internal-docs / App credential 의존 — outage 시 unmergeable risk
- 78 file (wrapper 단독) + 6 lane plugin 추가 file 의 git history 손실 (cross-repo simple copy migration)
- Skill default override 가 신뢰 기반 (자동 enforcement 없음 — CLAUDE.md policy 명시)

**검증**:
- 7 plugin repo main 에서 docs/{superpowers, stories, retros, change-plans}/ 부재
- CLAUDE.md 에 internal-docs pointer + ADR-013 inline summary
- Internal-docs 에서 4 Action workflow registered + cross-repo App credential 가용

## 거부된 대안

- **(B) Standard scope** (stories/change-plans 잔류) — Codex 1차 권고. 사용자 (C) override 로 reject — Action restructure 필수 전제로 진행
- **Per-plugin internal-docs (7개)** — ownership 명확하지만 cross-plugin CFP 추적 어려움. 단일 monorepo 우위
- **Branch archive** (main 만 깔끔, archive branch) — future CFP 위치 모호 + clone 시 archive 미노출
- **History rewrite (filter-repo)** — SHA invalidation + open PR base 깨짐 + forks/cache 충격. Codex 명시 reject (별도 후속 CFP)
- **GitHub App scope 광범** (write to all repos) — 보안 surface 확대. 최소 권한 원칙 (Issues write / PRs read / Contents read)

## 다이어그램

```
Before (CFP-45 결정 전):
mclayer/plugin-codeforge (wrapper)
├── docs/superpowers/specs/         # ← MOVE
├── docs/superpowers/plans/         # ← MOVE
├── docs/retros/                    # ← MOVE
├── docs/stories/                   # ← MOVE
├── docs/change-plans/              # ← MOVE
├── docs/adr/                       # KEEP
├── docs/inter-plugin-contracts/    # KEEP
├── docs/orchestrator-playbook.md   # KEEP
├── templates/                      # KEEP
├── scripts/                        # KEEP
└── .github/workflows/              # 4 Action MOVE, phase-gate UPDATE

(6 lane plugins: 동일 패턴)

After (CFP-45 머지 후):
mclayer/codeforge-internal-docs (NEW)
├── wrapper/
│   ├── specs/, plans/, stories/, change-plans/, retros/
├── review/, pmo/, requirements/, test/, develop/, design/  (동일 구조)
├── .github/workflows/  (4 story-owned Actions)
├── .github/ISSUE_TEMPLATE/  (story.yml + bug.yml + audit.yml)
└── CLAUDE.md  (internal-docs minimal)

mclayer/plugin-codeforge (wrapper, post-CFP-45)
├── docs/adr/ (+ ADR-013 NEW)        # KEEP + ADR-013
├── docs/inter-plugin-contracts/     # KEEP
├── docs/orchestrator-playbook.md    # KEEP
├── templates/, scripts/             # KEEP
├── CLAUDE.md (Dogfood policy rewrite + ADR-013 inline summary)
└── .github/workflows/phase-gate-mergeable.yml (cross-repo via App)
```

## 관련 파일

- [CFP-45 spec](https://github.com/mclayer/codeforge-internal-docs/blob/main/wrapper/specs/2026-04-30-cfp-45-dogfood-out-restructure-design.md) — parent
- [ADR-009 Wrapper-only Decomposition](ADR-009-wrapper-only-decomposition.md) — ζ arc parent
- [ADR-012 Wrapper CLAUDE.md SSOT Boundary](ADR-012-wrapper-claudemd-ssot-boundary.md) — direct predecessor
- [mclayer/codeforge-internal-docs](https://github.com/mclayer/codeforge-internal-docs) — NEW dogfood monorepo
- [ADR-017 Skill override path enforcement](ADR-017-skill-override-path-enforcement.md) — Amendment 1 carrier
- `scripts/check-dogfood-artifact-paths.sh` — path scan lint script
- `templates/github-workflows/dogfood-artifact-paths.yml` — CI workflow template
- `.github/workflows/dogfood-artifact-paths.yml` — active workflow (wrapper repo)
