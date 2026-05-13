# Changelog

`codeforge-pmo` plugin 릴리스 이력.

버전 체계: [Semantic Versioning 2.0.0](https://semver.org/lang/ko/). v1.0 이전은 minor bump도 breaking 가능.

## [0.1.2] - 2026-05-13

### CFP-534 — ADR-050 Amendment 1 GitOpsAgent intersection 로직 확장 (PATCH)

EPIC-RESULTS CFP-425 §7.5 follow-up carrier #5. ADR-050 Amendment 1 (wrapper) sibling sync — GitOpsAgent agent file 책임 §3.5 신설 (Epic Scope Manifest intersection 검사 — cross-section conflict detection).

#### Changed

- `agents/GitOpsAgent.md` — §3.5 "Epic Scope Manifest intersection 검사" 신설. 3 신규 scope manifest field (`planned_inter_plugin_contracts[]` / `planned_label_registry_bumps[]` / `cross_section_conflict_detection`) 활용 로직 + intersection 발견 시 WARN comment 자동 발의 + merge-order 자동 부여 (lower CFP 우선).

#### Why

2026-05-13 KST CFP-521 v2.4 vs CFP-429 v2.5 가 `docs/inter-plugin-contracts/label-registry-v2.md` frontmatter 3-location 동시 수정 (manual 15분 추가 + risk) sentinel evidence. 단순 file overlap 검출로는 frontmatter 의미 충돌 식별 불가 → cross-section detection layer 신설.

#### Cross-references

- ADR-050 Amendment 1 (wrapper) — `docs/adr/ADR-050-parallel-epic-conflict-coordination.md`
- Epic CFP-425 §7.5 follow-up
- Story file (internal-docs): `wrapper/stories/CFP-534.md`

## [0.1.1] - 2026-05-13

### CFP-462-followup — phase-gate-mergeable workflow sync (PATCH)

EPIC-RESULTS CFP-462 §6 carrier #1. Wrapper PR #500 (CFP-499 / ADR-010 Amendment 4 sibling-pr label fast-pass) merge 후 sibling repo backport 누락 detection.

#### Changed

- `.github/workflows/phase-gate-mergeable.yml` — wrapper SSOT (`templates/github-workflows/phase-gate-mergeable.yml`) verbatim mirror. CFP-113/123/133/342/499 누락 전체 backport (old version 였음).

#### Why

ADR-010 sibling sync 의무. sibling-pr label fast-pass + CFP-113/123/133/342 정합.

#### Compatibility

- **Wire**: workflow file 만 변경. agent / contract / overlay 영향 없음.
- **Marketplace sync**: 본 PATCH bump 의 marketplace.json mirror 는 별도 후속 carrier.

## [0.1.0] - 2026-04-29

### CFP-36 (codeforge ζ arc) — Initial extraction (NEW)

codeforge ζ arc 두 번째 lane plugin 추출 (parent spec mclayer/plugin-codeforge CFP-31 §5.6). 가장 작은 lane (PMOAgent 1개) 으로 writer-distributed 패턴의 두 번째 검증 단계.

### Added

- `agents/PMOAgent.md` — codeforge wrapper에서 이전. self-write 권한 확장 (Edit(docs/stories/**), mcp__github__add_issue_comment, mcp__github__issue_write, gh api milestones/graphql)
- `templates/retro.md` — codeforge wrapper에서 이전
- `docs/inter-plugin-contracts/pmo-output-v1.md` — pmo_output v1 contract (canonical)
- `overlay/hooks/regen-agents.sh` — codeforge core merge.py 재사용 (sibling discovery 불필요)
- `overlay/hooks/session-start-deps-check.sh` — codeforge core 설치 verify
- `.claude-plugin/plugin.json` v0.1.0 (initial)
- `README.md` — 설치 + dependency 안내

### Why

CFP-31 ζ arc 로드맵 §5.6: PMOAgent 가 가장 작은 lane (1 agent) + 가장 약한 결합 (Cross-cutting, lane gate 무관) → writer-distributed 패턴의 두 번째 검증으로 적합. CFP-35 review v2 retrofit (코드 이동 0) 검증 후 코드 이전 첫 사례.

### Compatibility

- **Wire**: codeforge >= 1.0.0 (codeforge wrapper 측 PMOAgent 삭제 + plugin install 의무 추가가 BREAKING)
- **Migration**: codeforge wrapper 와 본 plugin 동시 install 의무. consumer 측 SessionStart hook chain 활성화
- **Marketplace sync**: 본 plugin 신규 entry 등록 + codeforge wrapper version sync 동시 진행 (CFP-24 정책)
