# mctrader

암호화폐 스캘핑 자동매매 프레임워크 (Python).

## 문서 안내

| 종류 | 위치 |
|------|------|
| ADR (Architecture Decision Records) | [Confluence — space MCTRADER](https://mctrader.atlassian.net/wiki/spaces/MCTRADER) |
| 운영 가이드 · 외부 API 스펙 | Confluence — space MCTRADER, 트리 `Guides` / `API Reference` |
| 버그 이력 | [Jira — project MCTRADER](https://mctrader.atlassian.net/jira/software/projects/MCTRADER) |
| 요건·계획서 | [`docs/requirements/`](docs/requirements/), [`docs/change-plans/`](docs/change-plans/) |
| 에이전트 오케스트레이션 규칙 | [`CLAUDE.md`](CLAUDE.md) |

## 개발

```bash
python3 -m venv .venv
.venv/bin/pip install -e .
.venv/bin/pytest
```

## 리포지토리

- 코드: https://github.com/mctrader/mctrader (이 리포)
- 이력 아카이브: https://gitlab.com/mctrader1/mctrader (read-only, 2026-04-23 이관 완료)
