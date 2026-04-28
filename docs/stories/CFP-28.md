# CFP-28: Phase 0c — Lint strict 전환 + retro frontmatter backfill

라벨: `type:story`, `phase:구현`, `plugin-meta-na`

---

## §1. 사용자 요구사항 (verbatim)

> "시작합시다" (CFP-28 Phase 0c 진행 승인 — 직전 디자인 제안 "Retro frontmatter backfill / 회고 §1 regex 완화 / Legacy change-plan allowlist / Strict 전환 / CI rename / version bump 0.17.0 → 0.18.0 + marketplace sync"에 대해 "ㄱㄱ")

## §2. 도메인 해석

본 변경은 **plugin 자기 적용 (plugin-meta)** — production code 0 변경, lint 스크립트 + retro 본문 frontmatter + workflow job 이름 + plugin.json/CHANGELOG/migration-guide 정합. ADR-005 plugin-meta-na 패턴 적용.

CFP-26 Phase 0a (write 권한 재분배) → CFP-27 Phase 0b (lint 도입 — warning 모드) → **본 CFP-28 Phase 0c (lint strict 전환)** 의 staged ε path 마지막 단계. CFP-27 도입 시점에 명시적으로 "CFP-28 strict 전환"이 후속으로 약속되어 있어 본 Story가 그 commitment 이행.

도메인 제약:
- 16 legacy change-plan (`docs/change-plans/cfp-1` ~ `cfp-18`, CFP-3·CFP-17 제외)이 CFP-27 schema 도입 이전 산출물로 §1-§11 헤딩 부재 — 모두 backfill하면 거대 busywork. allowlist로 면제 처리
- 3 retro 파일이 frontmatter 부재 — 모두 backfill (3 file 한정 작업)
- 2 retro의 §1 헤딩 텍스트가 schema와 불일치 (`§1 결과` 강제 → 실제 `§1 Cross-Story 정량 분석` / `§1 Sprint 정량 분석`) — 회고 종류별로 §1 명칭이 자연스럽게 다양함. regex 완화 (`§1 결과` → 임의 text 허용)

암묵 가정:
- strict 전환은 의미상 BREAKING (consumer가 docs schema 위반 시 PR 차단). v0.17.0 → v0.18.0 minor bump 적절
- v1.0 이전이므로 minor bump도 BREAKING 표기 가능

지식 공백: 없음.

## §3. 관련 ADR

- **ADR-005** (직접 제약 — plugin-meta-na §8/§9/§11 N/A)
- **ADR-002** (배경 참조 — DocsAgent 단독 writer / CFP-26 Phase 0a 후 4 owner doc direct write)

신규 ADR 없음 — 본 Story는 lint 모드 전환 + 데이터 backfill 수준이며 architectural 결정으로까지 격상시킬 비용 회피.

## §4. 관련 코드 경로 + 책임

- `scripts/check-doc-frontmatter.sh` — `exit 0` → `exit 1` 전환, warning tail message 제거, 헤더 주석 갱신
- `scripts/check-doc-section-schema.sh` — `exit 0` → `exit 1` 전환 + 회고 §1 regex 완화 (`^## §1 결과` → `^## §1\s+\S`) + legacy change-plan allowlist 추가
- `docs/retros/2026-04-27-v0.11.0-sprint-close.md` — frontmatter 추가
- `docs/retros/2026-04-28-codex-audit-closure-sprint.md` — frontmatter 추가
- `docs/retros/2026-04-28-marketplace-bootstrap-sprint.md` — frontmatter 추가
- `.github/workflows/lint.yml` — job name `(CFP-27 — warning)` → `(CFP-28 — strict)` 2건
- `.claude-plugin/plugin.json` — version 0.17.0 → 0.18.0
- `CHANGELOG.md` — 최상단 `## [0.18.0]` 신규 entry
- `docs/migration-guide.md` — 목차 + `## v0.17 → v0.18` 신규 섹션 (Non-BREAKING 표기 — consumer 영향은 Phase 0c lint이 strict 전환된다는 사실 안내만)
- `mclayer/marketplace` 측 marketplace.json — `plugins[name=codeforge].version`을 0.18.0로 동기화 (별도 PR, codeforge PR 머지 직후)

미변경: `agents/**`·`templates/**`·`docs/orchestrator-playbook.md`·`docs/plugin-design.md`·CODEOWNERS·invariant-check.yml·기타 workflow.

## §5. 요구사항 확장 해석

유스케이스: docs/{change-plans,adr,domain-knowledge,retros}/** 의 신규/갱신 파일에서 frontmatter / 본문 섹션 schema 위반 시 lint.yml CI가 PR 차단 → drift 방지.

AC:
- `bash scripts/check-doc-frontmatter.sh` exit 1 (모든 schema 충족 시 0)
- `bash scripts/check-doc-section-schema.sh` exit 1 (모든 schema 충족 시 0)
- 현 시점 양 script local 실행 시 0 warning + exit 0
- 3 retro frontmatter 모두 `templates/retro.md` schema 충족 (title/date/sprint_period/cfp_keys/authors/related_stories/sentinel_refs)
- 16 legacy change-plan은 allowlist로 skip — 본 Story 외 별도 backfill 작업 의도 없음
- `lint.yml` 의 `doc-frontmatter` / `doc-section-schema` job 이름이 `(CFP-28 — strict)` 표기
- plugin.json version = 0.18.0
- CHANGELOG 최상단 `## [0.18.0] - 2026-04-28` + 본 Story entry
- migration-guide 목차 + `## v0.17 → v0.18` 섹션 존재
- marketplace.json sync PR 머지 (codeforge PR 머지 직후)

엣지 케이스:
- 회고 §1 regex 완화는 schema 의도(첫 메이저 섹션이 §1로 시작) 보존 — `§1 ` prefix만 강제, 제목 자유
- legacy allowlist는 set 기반: `{"cfp-1.md", "cfp-2.md", ..., "cfp-18.md"} - {"cfp-3.md", "cfp-17.md"}`. CFP-3/CFP-17은 docs/change-plans/ 디렉토리에 존재하지 않아 자동 면제
- CFP-19 이후의 모든 Story는 docs/superpowers/{specs,plans}/* 패턴 (docs/change-plans/ 아님) — schema 강제 대상 아님 (현재 디렉토리에 cfp-19+ 파일 없음으로 미래 backfill 부담 없음)

제외 범위:
- CFP-27.5 Story file `docs/stories/<KEY>.md` §1-§11 schema lint — 별도 spec
- CFP-30+ inter-plugin contract validation lint (review_verdict v1 / review_packet v1 schema) — bilateral, 별도 후속

§5.5 사용자 확인 필요: 없음 — 직전 design 제안에서 user "ㄱㄱ" 승인.

## §6. 외부 지식 배경

외부 지식 보강 불필요 — Python regex 완화 + bash exit code + YAML frontmatter 표준은 codebase 내 충분.

## §7. 설계 서사

Change Plan 별도 작성 안 함 (plugin-meta-na). 변경 8 file (script 2 + retro 3 + workflow 1 + plugin.json + CHANGELOG + migration-guide).

§7 보안 설계 요약: N/A — 문서·메타·lint 변경, attack surface 추가 없음.

## §8. 개발 서사

§8.1-§8.4: N/A — production code 0 변경.

### §8.5 Impl Manifest

| 파일 | 변경 유형 | 책임 에이전트 (실제 author) |
|---|---|---|
| `scripts/check-doc-frontmatter.sh` | 수정 (strict 전환) | Orchestrator (plugin-meta) |
| `scripts/check-doc-section-schema.sh` | 수정 (strict + regex 완화 + allowlist) | Orchestrator |
| `docs/retros/2026-04-27-v0.11.0-sprint-close.md` | 수정 (frontmatter prepend) | Orchestrator |
| `docs/retros/2026-04-28-codex-audit-closure-sprint.md` | 수정 (frontmatter prepend) | Orchestrator |
| `docs/retros/2026-04-28-marketplace-bootstrap-sprint.md` | 수정 (frontmatter prepend) | Orchestrator |
| `.github/workflows/lint.yml` | 수정 (job name 2건) | Orchestrator |
| `.claude-plugin/plugin.json` | 수정 (version) | Orchestrator |
| `CHANGELOG.md` | 수정 ([0.18.0] entry prepend) | Orchestrator |
| `docs/migration-guide.md` | 수정 (목차 + 섹션 추가) | Orchestrator |
| `docs/stories/CFP-28.md` | 신규 (본 file) | Orchestrator |

미변경 의도: cross-repo `mclayer/marketplace` PR은 본 Story 머지 후 별도 PR.

## §9. 리뷰 결과

§9.1 설계 리뷰: N/A — plugin-meta-na, ADR-005 면제.
§9.2 구현 리뷰: 본 Story PR self-review + invariant-check Step 1-9 (CI required status check).

## §10. FIX Ledger

| Iter | 시각 | 레인 | 트리거 | 원인 판정 | 재실행 범위 | RESET? |
|------|------|------|--------|-----------|-------------|--------|
| (비어있음) | | | | | | |

## §11. 데이터 마이그레이션

§11.1-§11.5: N/A — schema 변경 없음, 기존 데이터 처리 없음.

## §12. 회고 / 후속

본 Story 종료 시점에 PMOAgent 회고는 별도 sprint close에 통합 가능 (CFP-26 / CFP-27 / CFP-28 staged ε path 완료 회고).

후속 후보:
- **CFP-27.5**: Story file `<KEY>.md` §1-§11 schema lint
- **CFP-30+**: Inter-plugin contract validation lint (review_verdict v1 / review_packet v1)
- **codeforge-review v0.2.0**: own invariant-check workflow ([handoff spec](https://github.com/mclayer/plugin-codeforge-review/blob/main/docs/superpowers/specs/2026-04-28-own-lint-workflow-design.md))

marketplace sync PR (CFP-24 의무): codeforge PR 머지 직후 즉시 `mclayer/marketplace` PR open + merge.
