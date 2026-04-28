# Changelog

`codeforge-pmo` plugin 릴리스 이력.

버전 체계: [Semantic Versioning 2.0.0](https://semver.org/lang/ko/). v1.0 이전은 minor bump도 breaking 가능.

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
