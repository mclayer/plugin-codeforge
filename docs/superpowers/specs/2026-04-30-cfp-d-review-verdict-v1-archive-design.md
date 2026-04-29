---
title: review_verdict v1 Deprecated → Archived 전환 (CFP-D)
slug: cfp-d-review-verdict-v1-archive
status: Phase-1-Design
author: Claude (Opus 4.7) — CFP-D Phase 1 author
created: 2026-04-30
story: CFP-D
related_adrs:
  - ADR-008 (Inter-plugin Contract Versioning) — §5 보강
  - ADR-010 (Inter-plugin Contract Sibling Sync) — sync 의무 준수
---

### §1. 목적

review_verdict v1 contract 의 status 를 `Deprecated` → `Archived` 로 전환. consumer 부재 확신 (사용자 명시 2026-04-30) 으로 grace period 불필요. canonical (codeforge-review) + wrapper sibling 양쪽 동기화. history attribution 보존 (ADR-008 §5 "이전 file 은 historical record 로 유지" 룰 준수).

### §2. 범위

**In scope**:
- canonical + wrapper sibling 양쪽 v1 file 의 frontmatter `status` + body header 전환
- MANIFEST.yaml entry status 갱신
- CLAUDE.md Inter-plugin Contract 표 status 컬럼 갱신
- ADR-008 §5 한 단락 보강 (Deprecated → Archived 전환 트리거 정의)
- Active SSOT (orchestrator-playbook, migration-guide) v1 references 갱신
- History 14 files 일괄 "v1 (Deprecated)" → "v1 (Archived)" 치환
- CHANGELOG.md 새 entry append

**Out of scope**:
- v1 file 삭제 (ADR-008 §5 historical record 보존)
- 신규 v3 contract 발의
- 일반 history pruning (CFP-E 후속 분리)
- 신규 ADR-011 발의 (ADR-008 §5 보강으로 대체)

### §3. 결정 근거

| 결정점 | 채택 | 대안 기각 사유 |
|---|---|---|
| Q1 archive 의미 | A: status 전환만, file 보존 | B (archive/ 서브폴더 이동) — ADR-008 §5 update 부담 + lint scope 분기 / C (file 삭제) — ADR-008 §5 위반 + history attribution 유실 |
| Q2 적용 범위 | a: canonical + wrapper sibling 양쪽 | b (sibling 만) — ADR-010 sync 의무 위반, incoherent state |
| Q3 ADR 처리 | A: ADR-008 §5 보강 | B (신규 ADR-011) — 1 건 단발 결정에 ADR 비용 과함, YAGNI 위배 |
| Q4 references 갱신 | Y: 21 files 모두 (active + history) | X (active 만) — 사용자가 history file 도 일관성 유지 선호 |
| Q5 history pruning | β: 별도 CFP-E 로 분리 | α (CFP-D 합류) — pruning 기준 별도 brainstorm 필요 |
| Q6 PR 시퀀스 | 1: canonical 먼저 → wrapper 나중 | 2 (병렬 — incoherent 짧은 구간) / 3 (wrapper 먼저 — sibling 이 canonical 앞서면 mirror 의미 위배) |

### §4. 변경 대상 file 분류

#### §4.1 status 전환 (frontmatter + body header) — 2 files

- canonical: `mclayer/plugin-codeforge-review` `docs/inter-plugin-contracts/review-verdict-v1.md`
- wrapper sibling: 본 repo `docs/inter-plugin-contracts/review-verdict-v1.md`

변경 내용:
- frontmatter `status: Deprecated` → `Archived`
- frontmatter `authors:` 마지막 entry 추가: `CFP-D status Archived 전환 (2026-04-30)`
- body line 18 헤더 `(DEPRECATED)` → `(ARCHIVED)`
- body line 20 경고 문구 갱신: "consumer 부재 확신 시점 (2026-04-30, CFP-D) Archived 전환 — historical record 로 영구 보존, lint scope 에 동일 schema 검증 적용 (status enum 만 다름)"

#### §4.2 SSOT 표/registry 갱신 — 2 files

- `docs/inter-plugin-contracts/MANIFEST.yaml` v1 entry: `status: Deprecated` → `Archived`
- `CLAUDE.md` "Inter-plugin Contract" 섹션 review_verdict 표의 v1 행: "Deprecated" → "Archived"

#### §4.3 ADR-008 §5 보강 — 1 file

`docs/adr/ADR-008-inter-plugin-contract-versioning.md` §5 "SSOT 위치 룰" 섹션 끝에 한 단락 추가:

```markdown
### 5.1 Deprecated → Archived 전환 트리거 (CFP-D 보강, 2026-04-30)

`Deprecated` 상태의 contract file 은 다음 조건 모두 충족 시 `Archived` 로 전환:
1. consumer 부재 확신 (author 가 release / install metric 또는 사용자 confirm 으로 검증)
2. 후속 MAJOR 가 1개 이상 release 후 일정 grace period 경과 (case-by-case, default 6 CFP)
3. 전환 시 canonical + sibling 양쪽 frontmatter `status` 동시 갱신 (ADR-010 sync 의무)

`Archived` 상태도 file 자체는 유지 — historical record 보존 의무는 §5 본문 룰 그대로. lint (kind:contract) 은 status 값과 무관하게 동일 schema 강제. consumer 가 재출현하면 author 가 즉시 Active 또는 새 MAJOR 발의 결정 (Archived → Active 직접 전환 금지).
```

#### §4.4 Active narrative 갱신 — 2 files

- `docs/orchestrator-playbook.md`: v1 워커 흐름 언급 (해당 라인) 의 "v1 Deprecated" → "v1 Archived"
- `docs/migration-guide.md`: 현재 active contract 표시 + v1 status 표시 갱신

#### §4.5 History 갱신 — 14 files

`"v1 (Deprecated)"` 또는 `"v1.*Deprecated"` 패턴 → `"v1 (Archived)"` 치환:

1. `docs/superpowers/specs/2026-04-28-cfp-29-codeforge-review-extraction-design.md`
2. `docs/superpowers/specs/2026-04-28-docsagent-scope-reduction-and-review-extraction-design.md`
3. `docs/superpowers/specs/2026-04-29-cfp-31-wrapper-only-decomposition-design.md`
4. `docs/superpowers/specs/2026-04-29-cfp-42-inter-plugin-contract-sibling-backfill-design.md`
5. `docs/superpowers/specs/2026-04-30-cfp-43-wrapper-only-docs-cleanup-design.md`
6. `docs/superpowers/plans/2026-04-28-cfp-29-phase-1-codeforge-review-extract.md`
7. `docs/superpowers/plans/2026-04-29-cfp-32-foundation-invariant-ssot.md`
8. `docs/superpowers/plans/2026-04-29-cfp-42-inter-plugin-contract-sibling-backfill.md`
9. `docs/superpowers/plans/2026-04-30-cfp-43-wrapper-only-docs-cleanup.md`
10. `docs/change-plans/cfp-42-inter-plugin-contract-sibling-backfill.md`
11. `docs/stories/CFP-28.md`
12. `docs/retros/2026-04-29-zeta-arc-completion.md`
13. `docs/retros/2026-04-29-staged-epsilon-completion.md`
14. `docs/adr/ADR-009-wrapper-only-decomposition.md`

치환 전략: 정확한 pattern 매치 후 per-file Edit (sed 일괄 금지 — 의도 외 매치 회피). 단순 file path 참조 (`docs/inter-plugin-contracts/review-verdict-v1.md`) 는 그대로 유지 (file 보존되어 link 작동).

#### §4.6 CHANGELOG append — 1 file

`CHANGELOG.md` 새 entry:
```markdown
## [Unreleased] — CFP-D

### Changed
- review_verdict v1 contract status `Deprecated` → `Archived` (consumer 부재 확신, 2026-04-30)
- ADR-008 §5 보강 — `Deprecated → Archived` 전환 트리거 정의 (§5.1 추가)
- canonical (codeforge-review) + wrapper sibling 양쪽 동기화 (ADR-010 sync 의무)
```

**총: 22 files** (canonical 1 + wrapper 21).

### §5. 작업 시퀀스

#### §5.1 PR 1: canonical (codeforge-review repo)

- branch: `cfp-d-v1-archive`
- file 1개 변경: `docs/inter-plugin-contracts/review-verdict-v1.md`
- author note frontmatter 추가
- 직접 PR via `mcp__github` MCP tools (CFP-43 패턴)
- merge 대기 (sub-issue 생성 안 함 — single-file change)

#### §5.2 PR 2: wrapper (codeforge repo)

- branch: `cfp-d-v1-archive`
- 21 files 변경 (§4.1-§4.6)
- spec/plan 파일 사전 commit 후 본 PR 에 포함
- subagent-driven-development 로 실행
- canonical PR (PR 1) merge 후 진행 — wrapper sibling 본문이 canonical 의 verbatim mirror 일관성 유지

#### §5.3 Lint 검증

- `bash scripts/check-inter-plugin-contracts.sh` exit 0 (status enum "Archived" 이미 line 103 포함)
- `bash scripts/test-check-inter-plugin-contracts.sh` T1-T6 모두 PASS

#### §5.4 Story file

`docs/stories/CFP-D.md` (Story 작성 의무 강제 대상 — ADR 보강 + SSOT 의미 변경). story-init Action workflow 가 자동 생성하지 않을 경우 수동 생성.

### §6. 보안 (§7 단순)

N/A — 문서 metadata 갱신만. trust boundary / auth / data 무영향.

### §7. 데이터 마이그레이션 (§11 단순)

N/A — schema 변경 없음. status enum "Archived" 는 lint 이 이미 인정 (CFP-42, line 103). consumer 부재 명시 (사용자 확인 2026-04-30) → migration step 0개. Rollback: PR revert 1회로 복구.

### §8. Test Contract

| ID | Type | Description | Pass Criteria |
|---|---|---|---|
| T-1 | positive | check-inter-plugin-contracts.sh 실행 (수정 후) | exit 0 |
| T-2 | positive | test-check-inter-plugin-contracts.sh T1-T6 | 모두 PASS |
| T-3 | manual | MANIFEST entry status 확인 | `grep -E "review-verdict-v1.*Archived" docs/inter-plugin-contracts/MANIFEST.yaml` 1 hit |
| T-4 | manual | canonical (codeforge-review) v1 file status 확인 | `mcp__github__get_file_contents` 결과 frontmatter `status: Archived` |
| T-5 | manual | active SSOT 잔재 없음 | `grep -rn "v1.*Deprecated" CLAUDE.md MANIFEST.yaml ADR-008-*.md migration-guide.md orchestrator-playbook.md` 0 hits |
| T-6 | manual | history file 14개 치환 확인 | 각 file 에 `"v1 (Archived)"` 또는 `"v1.*Archived"` 매치, `"v1 (Deprecated)"` 매치 0 |

### §9. ADR 정합성

| ADR | 영향 | 검증 |
|---|---|---|
| ADR-008 | §5 보강 (§5.1 추가) | 본 CFP 가 author. 위반 0 |
| ADR-009 | 무영향 | wrapper-only 모델 변경 없음 |
| ADR-010 | sync 의무 준수 | PR 1 → PR 2 시퀀스로 enforce |
| ADR-001 | v1 attribution 보존 | file 자체 유지로 satisfied |

### §10. Risk + 완화

| Risk | 완화 |
|---|---|
| canonical merge 후 wrapper sibling 누락 (sync 깜빡) | PR 2 의 wrapper sibling status 변경이 같은 PR scope 안에 포함 |
| history file 14개 일괄 치환 시 sed 오버킬 | 정확한 pattern: `"v1 (Deprecated)"` per-file Edit (sed -i 금지) |
| 추후 v2 도 Archived 전환 시점 룰 부재 | ADR-008 §5.1 보강에 트리거 정의 (consumer 부재 + 6 CFP grace) |
| meta-CFP 머지 시 phase-gate-mergeable 차단 | admin merge (`gh pr merge --admin`) 사전 인지 (CFP-42, CFP-43 패턴) |
| CFP-D Story file 부재로 §10 FIX Ledger 위치 불명 | Phase 1 시작 시점 docs/stories/CFP-D.md 수동 생성 (story-init Action 미동작 가능성 대비) |

### §11. 작업 추정

- canonical PR: 1 file × 5 lines (~매우 작음)
- wrapper PR: 21 files (대부분 1-2 lines 치환), ADR-008 §5.1 단락 1 추가
- 총 token: 5-10k (subagent task 5-7개)
- 총 PR: 2 (canonical + wrapper)
- 총 PR-commit: 5-7 (subagent-driven 단위 commit)

### §12. 리뷰 결과

(Phase 1 설계 리뷰 시 채움)

### §13. 변경 이력

- 2026-04-30: CFP-D Phase 1 author Claude (Opus 4.7) — 본 spec 작성
