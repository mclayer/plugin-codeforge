# Plugin 문서

Claude Code 범용 SW 개발 에이전트 플러그인 문서 집합.

## 구조

| 파일 | 내용 |
|------|------|
| [`orchestrator-playbook.md`](orchestrator-playbook.md) | Orchestrator 행동 SSOT — 세션 생명주기·스폰·FIX 상태 머신·토큰 예산 |
| [`consumer-guide.md`](consumer-guide.md) | Consumer 프로젝트가 플러그인 설치·overlay 구성하는 방법 |
| [`plugin-design.md`](plugin-design.md) | 플러그인 설계 spec — core/overlay 경계 원칙, merge 계약, β 메커니즘 |
| [`project-config-schema.md`](project-config-schema.md) | `project.yaml` Schema SSOT — consumer SSOT 상수 구조화 |
| [`migration-guide.md`](migration-guide.md) | 플러그인 버전업 시 consumer overlay 마이그레이션 절차 |
| `change-plans/` | ArchitectAgent가 작성하는 Change Plan 저장 위치 (PR과 1:1 매핑, consumer 프로젝트에서 사용) |

## 상위 레벨 문서

| 파일 | 내용 |
|------|------|
| [`../CLAUDE.md`](../CLAUDE.md) | 플러그인 오케스트레이션 규칙 SSOT — 에이전트 목록·레인·권한·GitHub Workflow·ADR 규약 ("무엇") |
| [`../README.md`](../README.md) | 플러그인 소개 · 설치법 · overlay 적용법 |
| [`../templates/`](../templates/) | 공통 문서 양식 SSOT — Change Plan · ADR · Story Page · Impl Manifest |
| `../agents/*.md` | 20 core 에이전트 SSOT (consumer overlay/preset이 확장; v0.9 review 워커 통합 — [ADR-001](../archive/adr/ADR-001-review-agent-unification.md)) |
| `../presets/` | 프로젝트 shape별 Dev 번들 (webapp 등) |
