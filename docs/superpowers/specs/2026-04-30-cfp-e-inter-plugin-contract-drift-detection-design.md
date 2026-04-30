---
title: Inter-plugin contract drift detection (canonical ↔ sibling 본문 verbatim 자동 검증)
slug: cfp-e-inter-plugin-contract-drift-detection
status: Phase-1-Design
author: Claude (Opus 4.7) — CFP-E Phase 1 author
created: 2026-04-30
story: CFP-E
related_adrs:
  - ADR-008 (Inter-plugin Contract Versioning) — 본 CFP 와 무관
  - ADR-010 (Inter-plugin Contract Sibling Sync) — 본 CFP 가 §5 후속 ADR 의도 충족
  - ADR-011 (Inter-plugin Contract Drift Detection — 본 CFP author)
---

### §1. 목적

ADR-010 §5 후속 ADR 의도 직접 충족: wrapper repo `docs/inter-plugin-contracts/` 의 sibling file 본문이 lane plugin canonical 본문과 verbatim 일치하는지 자동 검증. drift 발견 시 wrapper PR/push CI fail.

### §2. 범위

**In scope (5 active sibling/canonical pair)**:

| Sibling (wrapper) | Canonical (lane plugin) |
|---|---|
| review-verdict-v2.md | `mclayer/plugin-codeforge-review/docs/inter-plugin-contracts/review-verdict-v2.md` |
| requirements-output-v1.md | `mclayer/plugin-codeforge-requirements/docs/inter-plugin-contracts/requirements-output-v1.md` |
| design-output-v1.md | `mclayer/plugin-codeforge-design/docs/inter-plugin-contracts/design-output-v1.md` |
| develop-output-v1.md | `mclayer/plugin-codeforge-develop/docs/inter-plugin-contracts/develop-output-v1.md` |
| test-verdict-v1.md | `mclayer/plugin-codeforge-test/docs/inter-plugin-contracts/test-verdict-v1.md` |
| pmo-output-v1.md | `mclayer/plugin-codeforge-pmo/docs/inter-plugin-contracts/pmo-output-v1.md` |

**Out of scope**:
- review_verdict v1 (status=Archived, canonical 부재 — CFP-D 결과): 자동 skip
- cron / cross-repo webhook / SHA snapshot 저장 (live fetch only)
- consumer overlay file drift
- frontmatter 비교 (sibling 과 canonical 의 frontmatter 가 의도적으로 다름 — `related_plugins`, `authors` 등)
- ADR-001 / ADR-008 / ADR-009 변경

### §3. 결정 근거 (Q1-Q6)

| 결정점 | 채택 | 대안 기각 사유 |
|---|---|---|
| Q1 trigger | PR/push to main + workflow_dispatch (cron drop) | (B) cron only — PR 시점 차단 부재 / (C) PR + cron — 1 인 maintainer 환경에서 lane only 변경 시나리오 비현실적, YAGNI 위배 |
| Q2 비교 방법 | strict body verbatim (정규화 후) | (b) section-level — 구현 복잡 / (c) fuzzy similarity — 검출기 의미 약화 / (d) minimal sanity — drift 일부만 catch |
| Q3 action | PR fail (CI block) | (β) issue 만 — 강제 효과 약함 / (γ) annotation 만 — 차단 부재 |
| Q4 storage | live fetch (GITHUB_TOKEN) | (II) MANIFEST canonical_sha — 또 다른 sync 대상 / (III) cache file — 동일 문제 |
| Q5 skip | status=Archived 자동 skip + canonical 404 graceful warning (Active 인데 부재 → fail) | (ii) MANIFEST skip_drift flag — schema 변경 부담 / (iii) status 무시 — Active/Archived 구분 못 함 |
| Q6 file 위치 | 기존 `contract-lint.yml` 에 새 job 추가 | (1) 신규 file — cron drop 후 분리 명분 사라짐 |
| Q3.1 ADR | 신규 ADR-011 발의 | ADR-010 §5 만 보강 — "후속 ADR" 명시 의도 충족 안 함 |

### §4. 비교 알고리즘

**입력**:
- wrapper sibling file (local checkout)
- canonical file (live fetch via GitHub REST API: `GET /repos/{org}/{repo}/contents/{path}`)

**전처리 (정규화)**:

| 단계 | 동작 |
|---|---|
| 1. Frontmatter 분리 | `---\n...\n---\n` 첫 블록 제거. sibling/canonical 각각 본문만 추출 |
| 2. Sibling-only meta section 제거 | sibling 본문에서 `^\*\*상위 SSOT 위치\*\*:` 로 시작하는 단락 제거. 단락 끝 = 다음 빈 줄 또는 `^## ` 직전 |
| 3. Line ending 정규화 | `\r\n` → `\n` |
| 4. Trailing whitespace trim | 각 line 끝 공백 제거 |
| 5. Trailing newline 통일 | file 끝 `\n` 1 개로 통일 |

**비교**:
- 정규화된 sibling body == canonical body? (byte 단위)
- 불일치 시 `difflib.unified_diff()` 형식 출력 + `::error::` GitHub Actions annotation
- 일치 시 `✓` 출력, exit 0

**예시 출력 (drift 발견)**:
```
::error::CFP-E drift: requirements_output v1
  canonical: mclayer/plugin-codeforge-requirements/docs/inter-plugin-contracts/requirements-output-v1.md
  sibling:   docs/inter-plugin-contracts/requirements-output-v1.md
--- canonical body
+++ sibling body
@@ -47 +47 @@
- 기존 줄 (canonical)
+ 새 줄 (sibling drift)
```

**구현**:
- `scripts/check-inter-plugin-drift.sh` (bash wrapper + inline Python heredoc — 기존 `check-inter-plugin-contracts.sh` 패턴)
- 의존: `pyyaml` (frontmatter parse), `urllib.request` (canonical fetch)
- 환경 변수: `GH_TOKEN` (workflow `secrets.GITHUB_TOKEN`)

### §5. workflow 통합 + 에러 처리

**`.github/workflows/contract-lint.yml` 새 job 추가** (기존 `inter-plugin-contracts` job 옆):

```yaml
  inter-plugin-drift:
    name: inter-plugin-drift (CFP-E)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install pyyaml
      - name: Run check-inter-plugin-drift.sh
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: bash scripts/check-inter-plugin-drift.sh
```

기존 `on: { pull_request, push }` 트리거 그대로. `workflow_dispatch:` 추가:

```yaml
on:
  pull_request: { branches: [main] }
  push: { branches: [main] }
  workflow_dispatch: {}    # NEW — manual debug trigger
```

**에러 처리 분류 (script 내부)**:

| 상황 | 처리 | exit |
|---|---|---|
| Active entry, drift 발견 | unified_diff 출력 + `::error::` | 1 |
| Active entry, drift 0 | `✓` 출력 | 0 |
| Active entry, canonical 404 | `::error::` "Active 인데 canonical 부재" | 1 |
| Archived entry | "skip (Archived)" 출력 | 0 |
| MANIFEST 부재 / parse 실패 | `::error::` | 1 |
| GH_TOKEN 부재 / API rate limit | `::error::` + 안내 | 1 |
| Network 일시 오류 | retry 1회 후 fail | 1 |

**Branch protection**: 신규 job name `inter-plugin-drift (CFP-E)` 를 main branch 의 required-status-check 목록에 추가 (수동 — GitHub Settings UI). CFP-E PR merge 후 1 일 dogfood + 사용자 직접 등록.

### §6. 보안 (§7 단순)

- canonical fetch: GITHUB_TOKEN read-only 권한 — 모든 lane plugin public, 토큰 권한 escalation 표면 0
- supply-chain: lane plugin canonical 이 적대적으로 변경되어도 본 lint 은 drift 만 detect — 자동 sync 안 함 (author 가 sync PR 작성 시 review). trust boundary 유지
- secret 노출: 출력에 token 미포함 (Python 코드 직접 사용)

### §7. 데이터 마이그레이션 (§11 단순)

N/A — 신규 lint 추가만, 기존 schema 변경 없음. MANIFEST.yaml schema 그대로. Rollback: workflow job + script delete + ADR-011 status `Rejected` 변경.

### §8. Test Contract

| ID | Type | Description | Pass Criteria |
|---|---|---|---|
| T-1 | positive | drift 없는 정합 상태 | exit 0 |
| T-2 | negative | sibling 본문에 의도적 한 글자 추가 | exit 1, drift line 표시 |
| T-3 | negative | canonical 본문 변경 mock (fixture) | exit 1 |
| T-4 | positive | sibling 의 "**상위 SSOT 위치**:" section 변경 | exit 0 (정규화 시 제거됨) |
| T-5 | positive | line ending CRLF vs LF | exit 0 (정규화 후 동일) |
| T-6 | positive | Archived entry (review_verdict v1) | "skip" 출력, exit 0 |
| T-7 | negative | Active entry 의 canonical 404 | exit 1 (fail) |
| T-8 | positive | trailing whitespace 차이 | exit 0 (정규화 후 동일) |

`scripts/test-check-inter-plugin-drift.sh` harness 신설 (CFP-42 `test-check-inter-plugin-contracts.sh` 패턴 따라). canonical fetch 는 local fixture 로 mock — `CFP_E_TEST_FIXTURE_DIR` 환경 변수로 fetch 경로 override.

### §9. ADR 정합성

| ADR | 영향 | 검증 |
|---|---|---|
| ADR-008 | 무영향 | versioning 룰 변경 없음 |
| ADR-009 | 무영향 | wrapper-only 모델 변경 없음 |
| ADR-010 | §5 후속 ADR 의도 직접 충족 | 신규 ADR-011 가 ADR-010 본문 인용 + 후속 ADR 발의 |
| ADR-011 (신규) | 본 CFP 가 author | drift detection 정책 동결 |

### §10. Risk + 완화

| Risk | 완화 |
|---|---|
| GitHub API rate limit (5000/hr) | live fetch 5 contracts × PR 트리거 — 무관. workflow_dispatch 남용 시에도 rate 한참 미만 |
| canonical fetch network 일시 오류 | retry 1 회 + clear error message |
| 정규화 누락 → false positive drift | T-4/T-5/T-8 회귀 테스트로 catch |
| 정규화 과잉 → false negative (진짜 drift 누락) | 실제 drift 패턴 (의미 변경) 은 단순 whitespace 만 아님 — strict byte 비교가 잘 catch |
| GH_TOKEN 권한 부족 | 모든 lane plugin public — 공개 repo read 토큰 무관해도 가능 |
| meta-CFP 머지 시 phase-gate-mergeable 차단 | admin merge (CFP-42, CFP-43, CFP-D 패턴) |

### §11. 작업 추정

- 신규 script `scripts/check-inter-plugin-drift.sh`: ~200 lines (Python heredoc + bash wrapper)
- 신규 test harness `scripts/test-check-inter-plugin-drift.sh`: ~150 lines
- `.github/workflows/contract-lint.yml`: 1 job 추가 (~10 lines) + workflow_dispatch trigger 추가
- 신규 ADR-011: ~80 lines
- 신규 spec/plan + CHANGELOG entry: ~150 lines

**총 PR**: 1 (wrapper 단독). branch `cfp-e-drift-detection`. 추정 token: 8-12k.

### §12. 리뷰 결과

(Phase 1 설계 리뷰 시 채움)

### §13. 변경 이력

- 2026-04-30: CFP-E Phase 1 author Claude (Opus 4.7) — 본 spec 작성
