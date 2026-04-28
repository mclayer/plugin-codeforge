# Changelog

`codeforge-requirements` plugin 릴리스 이력.

버전 체계: [Semantic Versioning 2.0.0](https://semver.org/lang/ko/). v1.0 이전은 minor bump도 breaking 가능.

## [0.1.0] - 2026-04-29

### CFP-37 (codeforge ζ arc) — Initial extraction (NEW)

codeforge ζ arc 세 번째 lane plugin 추출 (parent spec mclayer/plugin-codeforge CFP-31 §5.7). 4 sub-agent + 도메인 KB owner write 이전.

### Added

- `agents/RequirementsPLAgent.md` — synthesizer, 4 sub-agent 통합 + Story §2/§5/§6 self-write
- `agents/DomainAgent.md` — 도메인 KB direct write, WebFetch/WebSearch
- `agents/RequirementsAnalystAgent.md` — Bash(codex exec *) wrapper
- `agents/ResearcherAgent.md` — 외부 지식 리서치, WebFetch/WebSearch
- `templates/domain-knowledge.md` — 도메인 KB 페이지 schema (CFP-27 신설본)
- `docs/inter-plugin-contracts/requirements-output-v1.md` — canonical contract
- `overlay/hooks/{regen-agents,session-start-deps-check}.sh`
- README + CLAUDE.md

### Why

CFP-31 §5.7: Requirements lane 4 agents 가 PL 산하 병렬 패턴 + DomainAgent 의 KB owner write 가 코드 이동 첫 case (PMO 보다 큰 표면). codeforge-review v1.0 + codeforge-pmo v0.1 검증 후 진입.

### Compatibility

- **Wire**: codeforge >= 2.0.0 (wrapper 측 4 agent 삭제 + plugin install 의무 BREAKING)
- **Migration**: codeforge wrapper 와 본 plugin 동시 install 의무
- **Marketplace sync**: 본 plugin 신규 entry 등록 + codeforge wrapper version sync
