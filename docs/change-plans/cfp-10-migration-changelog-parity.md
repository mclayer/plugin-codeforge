---
title: invariant-check.yml Step 7 — Migration-guide ↔ CHANGELOG BREAKING 정합 (Phase D)
slug: cfp-10-migration-changelog-parity
status: draft
author: ClaudeOrchestrator (CFP-9 §11 후속)
reviewers: [user]
related_adrs: []
created: 2026-04-27
story: CFP-10
---

## §1. 목적

CHANGELOG.md의 모든 BREAKING release가 docs/migration-guide.md에 대응 섹션을 보유하는지 자동 검증. consumer가 plugin upgrade 시 migration 절차를 못 찾는 release 사고 사전 차단.

CFP-7~9와 동일 패턴 — narrative ↔ machine-readable parity. 다만 본 변경은 cross-document(2 별도 artifact) 정합 대상.

### 수용 기준

- `.github/workflows/invariant-check.yml` Step 7 추가 (Python parser ~70줄)
- CHANGELOG `## [X.Y.Z] ... (BREAKING ...)` ↔ migration-guide `## vA.B → vC.D` 매칭
- to-version major.minor 단위 매칭 (patch 별도 섹션 미강제)
- 4 test case 모두 PASS (정합 / CHANGELOG 추가 누락 / migration 제거 누락 / BREAKING 부재 시 skip)

## §2. 현재 구조 분석

### 2.1 CHANGELOG.md BREAKING 패턴

```text
## [0.9.0] — 2026-04-26 (BREAKING — Review/Test 워커 통합)
## [0.8.0] — 2026-04-26 (BREAKING — Atlassian 제거 + GitHub 전환)
```

11 versions, 2 BREAKING. 헤더 패턴 일관 — `## [<semver>] — <date> (BREAKING — <title>)`.

### 2.2 docs/migration-guide.md section 패턴

```text
## v0.8 → v0.9 (Review/Test 워커 통합)
## v0.7 → v0.8 (Atlassian 제거 + GitHub 전환)
## v0.6 → v0.7 (요구사항·설계 레인 병렬화)
## v0.5 → v0.6 (Plugin name rename ...)
## v0.3 → v0.4 (Stage 2 ...)
## v0.2 → v0.3 (Generic Dev roster + preset)
## v0.1 → v0.2 (보안 테스트 레인 + templates)
```

7 sections (BREAKING 2 + non-BREAKING 5). superset 형태 — 모든 major/minor bump 문서화.

### 2.3 자동 검증 부재 — 핵심 release 사고 패턴

"CHANGELOG에 BREAKING 적었는데 migration-guide 작성 잊음"이 가장 빈번한 release 사고 패턴. consumer 입장에서 "BREAKING이라는데 어떻게 마이그레이션?" 시점에 막힘. 1인 maintainer 환경에서 더 위험.

### 2.4 Mapper 변호 근거

기존 CHANGELOG/migration-guide 이중 작성을 보존하자는 Mapper 입장: "release process는 사람 책임. CI invariant보다 release checklist가 적합."

## §3. 도입할 설계

### 3.1 Mapper vs Refactor 대립 결론

채택: **Refactor 우세**.

근거:
- Release checklist는 사람의 주의 의존. CFP-7~9 동일 논리
- CHANGELOG 추가는 1줄 짧고, migration-guide section은 절차 본문이라 "CHANGELOG만 작성"이 자연스러운 실수 패턴
- single-direction 강제(BREAKING → migration 필수, 역방향은 superset 허용)로 release process 자율성 보존

### 3.2 Step 7 Python parser 구조

```python
# CHANGELOG에서 BREAKING 추출
br_re = re.compile(r"^## \[(\d+)\.(\d+)\.(\d+)\][^\n]*\(BREAKING", re.MULTILINE)
breaking_versions = [(m.group(1), m.group(2), m.group(3))
                     for m in br_re.finditer(changelog)]

# migration-guide에서 section to-version 추출
mg_re = re.compile(r"^##\s*v(\d+)\.(\d+)\s*[→\-]+>?\s*v(\d+)\.(\d+)\b", re.MULTILINE)
mg_sections = {f"{m.group(3)}.{m.group(4)}" for m in mg_re.finditer(mg_text)}

# 매칭 검증
for major, minor, patch in breaking_versions:
    if f"{major}.{minor}" not in mg_sections:
        errors.append(f"v{major}.{minor}.{patch} BREAKING but migration v?→v{major}.{minor} 부재")
```

### 3.3 Korean emdash 지원

migration-guide는 Korean emdash `→` (U+2192) 사용. `[→\-]+>?` regex로 emdash와 `->`/`→` 모두 허용. 미래에 다른 dash 변종 등장 시 확장 가능.

### 3.4 BREAKING 부재 시 vacuous truth

CHANGELOG에 BREAKING 1건도 없으면 step skip + ✓ 출력 (exit 0). 이론상 plugin이 v1.0 stable 이후 BREAKING 없는 minor만 release할 수 있으므로 정합.

### 3.5 ADR 정합성

- ADR-001/002 무관
- 신규 ADR 불요

## §4. API 계약

### 4.1 invariant-check workflow Step 추가

기존 Step 1-6 그대로 + Step 7.

### 4.2 Error message 형식

```
::error file=docs/migration-guide.md::Migration-guide BREAKING parity 실패 (N drift)
  - v<X.Y.Z> BREAKING but migration-guide.md에 '## v? → v<X.Y>' 섹션 부재
  CHANGELOG BREAKING versions: [...]
  migration-guide section to-versions: [...]
```

### 4.3 Exit code

기존 그대로.

## §5. 변경 계획 (파일 단위)

| 파일 경로 | 변경 유형 | 담당 | 상태 |
|-----------|-----------|------|------|
| `.github/workflows/invariant-check.yml` | 수정 (Step 7 + header) | DocsAgent | 적용 완료 + 4 test PASS |
| `docs/stories/CFP-10.md` | 신규 | DocsAgent | 작성 중 |
| `docs/change-plans/cfp-10-migration-changelog-parity.md` | 신규 (본 파일) | DocsAgent | 작성 중 |

## §6. 리팩토링 선행 작업

**없음**. invariant-check.yml에 step 추가만.

## §8. Test Contract

### §8.1 커버리지 계획

- 단위 테스트: **N/A** — Local sim 4 case로 갈음
- 통합 테스트: **PR CI에서 invariant-check.yml 실 실행**
- 인프라 테스트: **N/A**

### §8.2 경계 조건·invariant

- **Test 1 — 정합 OK**: 현 plugin (BREAKING 2건 + 7 migration sections) → exit 0
- **Test 2 — CHANGELOG 추가 누락**: v1.0.0 BREAKING 추가 + migration-guide v?→v1.0 section 미작성 → drift detect
- **Test 3 — migration 제거 누락**: v0.7→v0.8 section 제거 → "v0.8.0 BREAKING but ... 부재"
- **Test 4 — BREAKING 부재**: CHANGELOG의 모든 BREAKING 단어 제거 → skip + exit 0 (vacuous truth)
- **Edge case — patch BREAKING (X.Y.Z, Z>0)**: major.minor 단위로 매칭, 별도 section 미요구

### §8.3 Perf Baseline

**N/A** — 2 file read + regex, ms 수준.

## §9. 분기 선택

**단일 PR**. Phase 1/2 분리 면제.

Commit 시리즈 2개:
- **Commit 1**: `.github/workflows/invariant-check.yml` Step 7 + header
- **Commit 2**: Story + Change Plan

본 PR base는 `main`. CFP-9 머지 완료.

## §10. ADR 대상 여부 + 기존 ADR 정합성

- ADR-001/002 무관
- 신규 ADR 불요 — Phase A~C와 동일한 invariant 자동화 패턴

향후 Phase 격상 trigger 정량화는 별도 ADR-003 후보 (CFP-6 §11 회고 거론, 조건부).
