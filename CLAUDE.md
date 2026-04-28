# CLAUDE.md (codeforge-requirements)

codeforge ζ arc Requirements lane plugin. 4 agent 병렬 (PL + 3 sub) + 도메인 KB owner write.

## Plugin position

본 plugin 은 codeforge wrapper 의 dependency. 단독 동작 불가 — codeforge core (>= 2.0.0) 가 Orchestrator 보유.

설치 + dependency + architecture 는 [`README.md`](README.md) 참조.

## Inter-plugin contracts

- `requirements_output v1` — [`docs/inter-plugin-contracts/requirements-output-v1.md`](docs/inter-plugin-contracts/requirements-output-v1.md) (canonical SSOT)

## Self-write 책임 (CFP-37 ζ arc 패턴)

| Path | 책임 agent | Mechanism |
|---|---|---|
| `docs/stories/<KEY>.md §2` (도메인 분석) | RequirementsPLAgent (DomainAgent 결과 통합) | `Edit(docs/stories/**)` |
| `docs/stories/<KEY>.md §5` (요구사항 확장 해석) | RequirementsPLAgent (Analyst 결과 통합) | `Edit(docs/stories/**)` |
| `docs/stories/<KEY>.md §6` (외부 지식 배경) | RequirementsPLAgent (Researcher 결과 통합) | `Edit(docs/stories/**)` |
| `docs/domain-knowledge/<area>/<topic>.md` | DomainAgent direct (CFP-26 Phase 0a 보존) | `Edit(docs/domain-knowledge/**)` |
| GitHub comment `[요구사항]` prefix | RequirementsPLAgent | `mcp__github__add_issue_comment` |
| `phase:요구사항` → `phase:설계` transition | RequirementsPLAgent | `mcp__github__issue_write` |
| Discussions Q&A category routing | DomainAgent (선택) | `Bash(gh api repos/*/discussions*)` |

## Sub-agent 4-way 병렬 패턴

PL 이 한 메시지에 3 sub-agent 동시 dispatch (사용자 원문 verbatim Story §1 + ADR 목록 §3 + 코드 §4 공통 입력):
- Each sub-agent 가 독립 관점 (도메인 / 분석 / 외부) 도출
- "null 결과"도 valid (사유 명시)
- PL 이 dedup·상충 조정 통합

상세는 [codeforge wrapper CLAUDE.md](https://github.com/mclayer/plugin-codeforge/blob/main/CLAUDE.md) "스폰 시퀀스" 절 참조.
