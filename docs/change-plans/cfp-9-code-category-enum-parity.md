---
title: invariant-check.yml Step 6 — Code review category enum 3 location 정합 (Phase C-3)
slug: cfp-9-code-category-enum-parity
status: draft
author: ClaudeOrchestrator (CFP-8 §11 후속)
reviewers: [user]
related_adrs: []
created: 2026-04-27
story: CFP-9
---

## §1. 목적

`templates/review-checklists/code.md` SSOT의 10종 code review category enum이 `agents/CodeReviewPLAgent.md` packet YAML과 `agents/CodexReviewAgent.md` lane=code 프롬프트에서 동일 set + 동일 순서로 mirror되는지 자동 검증.

CFP-7 (frontmatter 표) / CFP-8 (ADR-002 footer)와 동일 패턴 — narrative SSOT ↔ machine-readable mirror parity.

### 수용 기준

- `.github/workflows/invariant-check.yml` Step 6 추가 (Python parser ~75줄)
- 3 location 추출 + 비교 + diff 양방향 보고
- 4 test case 모두 PASS:
  - Test 1: 현 plugin (10 categories x 3 location) → OK
  - Test 2: SSOT에 `new-cat` 추가 → PL/Codex drift detect
  - Test 3: PL list에서 `dead-code` 제거 → PL drift detect
  - Test 4: Codex 순서 변경 → Codex drift detect (set 같음에도 순서 차이로 fail)

## §2. 현재 구조 분석

### 2.1 SSOT — `templates/review-checklists/code.md` line 14

```text
`runtime-bug | layer-violation | naming | test-quality | impl-manifest-mismatch | concurrency | error-handling | dead-code | dup-local | dup-boundary`
```

10 categories pipe-separated inline code. CFP-1~ ADR-001 워커 통합 결정의 일환으로 SSOT 위치 확정.

### 2.2 Mirror 1 — `agents/CodeReviewPLAgent.md` packet YAML

```yaml
category_enum:
  - runtime-bug
  - layer-violation
  - naming
  - test-quality
  - impl-manifest-mismatch
  - concurrency
  - error-handling
  - dead-code
  - dup-local
  - dup-boundary
```

PL이 lane=code 워커에 주입하는 packet의 일부. SSOT 변경 시 동시 갱신 필요.

### 2.3 Mirror 2 — `agents/CodexReviewAgent.md` lane=code 프롬프트

```text
Report each finding with severity [P0]/[P1]/[P2]/[P3], category from {runtime-bug,
layer-violation, naming, test-quality, impl-manifest-mismatch, concurrency,
error-handling, dead-code, dup-local, dup-boundary}, location as path:line.
```

Codex가 프롬프트로 받는 inline set. lane=design/security와 격리 anchor 필요.

### 2.4 자동 검증 부재

3 location의 동시 갱신은 사람의 주의 의존. PR #26 audit P0 #4가 이 invariant 영구화 motivation.

### 2.5 Mapper 변호 근거

기존 mirror 형태 보존하자는 Mapper 입장: "SSOT 자체를 1 location에만 두고 다른 2 위치가 SSOT를 참조하면 drift 자체 불가."

## §3. 도입할 설계

### 3.1 Mapper vs Refactor 대립 결론

채택: **Refactor 우세**.

근거:
- ADR-001 워커 통합 결정 자체가 "도메인 packet 형태로 PL이 워커에 주입" — packet 구조 변경 없이는 mirror 형태 불가피
- Codex 프롬프트는 LLM input이라 직접 link 불가 (텍스트 inline 필요)
- CFP-7/8과 동일 패턴 — narrative ↔ machine-readable parity 자동화가 가장 실용적

Mapper의 "자동화 redundant" 우려는 PR #26 audit P0 #4가 이미 drift 발생 사례 — 우려 무력화.

### 3.2 Step 6 Python parser 구조

**3 location 추출 regex**:

```python
# SSOT — pipe-separated inline code
ssot = re.search(r"`([a-z-]+(?:\s*\|\s*[a-z-]+)+)`", ssot_text)
ssot_enum = [s.strip() for s in ssot.group(1).split("|")]

# PL — YAML category_enum: list
pl = re.search(r"category_enum:\s*\n((?:\s*-\s*[a-z-]+\s*\n)+)", pl_text)
pl_enum = re.findall(r"-\s*([a-z-]+)", pl.group(1))

# Codex — lane=code anchored set
codex = re.search(r"####\s*lane=code.*?category from \{([^}]+)\}", codex_text, re.DOTALL)
codex_enum = [s.strip() for s in codex.group(1).split(",")]
```

**정합 비교**: list equality (순서 포함).

**diff 양방향 보고**: `set(SSOT) - set(location)` + `set(location) - set(SSOT)`.

### 3.3 lane=code anchor 필요성

CodexReviewAgent.md는 3 lane(design/code/security)별 `category from {...}` 보유. anchor 없는 regex는 첫 매치 = lane=design enum (다른 set). `#### lane=code` heading anchor 후 첫 매치로 해결. 첫 구현 시 발견된 self-discovery 패턴.

### 3.4 ADR 정합성

- ADR-001/002 무관
- 신규 ADR 불요

## §4. API 계약

### 4.1 invariant-check workflow Step 추가

기존 Step 1-5 그대로 + Step 6.

### 4.2 Error message 형식

```
::error::Code review category enum parity 실패 (N drift)
  CodeReviewPLAgent.md category_enum (N) ≠ SSOT (M)
    SSOT  : [...]
    PL    : [...]
    diff(only in SSOT): [...]
    diff(only in PL)  : [...]
```

### 4.3 Exit code

기존 그대로.

## §5. 변경 계획 (파일 단위)

| 파일 경로 | 변경 유형 | 담당 | 상태 |
|-----------|-----------|------|------|
| `.github/workflows/invariant-check.yml` | 수정 (Step 6 + header) | DocsAgent | 적용 완료 + 4 test PASS |
| `docs/stories/CFP-9.md` | 신규 | DocsAgent | 작성 중 |
| `docs/change-plans/cfp-9-code-category-enum-parity.md` | 신규 (본 파일) | DocsAgent | 작성 중 |

## §6. 리팩토링 선행 작업

**없음**. invariant-check.yml에 step 추가만.

## §8. Test Contract

### §8.1 커버리지 계획

- 단위 테스트: **N/A** — Local sim 4 case로 갈음
- 통합 테스트: **PR CI에서 invariant-check.yml 실 실행**
- 인프라 테스트: **N/A**

### §8.2 경계 조건·invariant

- **Test 1 — 정합 OK**: 현 plugin (10 x 3 location) → exit 0
- **Test 2 — SSOT 추가**: `new-cat` 1개 추가 → PL/Codex 둘 다 drift detect (2건)
- **Test 3 — PL 누락**: `dead-code` 제거 → PL drift 1건
- **Test 4 — Codex 순서 변경**: 동일 set이지만 순서 다름 → Codex drift detect (set 같음에도 순서 fail)
- **Edge case — 빈 SSOT**: pipe-separated enum 부재 시 즉시 차단
- **Edge case — Codex 다른 lane만 매치**: lane=code anchor로 격리

### §8.3 Perf Baseline

**N/A** — 3 file read + regex, ms 수준.

## §9. 분기 선택

**단일 PR**. Phase 1/2 분리 면제.

Commit 시리즈 2개:
- **Commit 1**: `.github/workflows/invariant-check.yml` Step 6 + header
- **Commit 2**: `docs/stories/CFP-9.md` + `docs/change-plans/cfp-9-...md`

본 PR base는 `main`. CFP-8 머지 완료.

## §10. ADR 대상 여부 + 기존 ADR 정합성

- ADR-001/002 무관
- **신규 ADR 필요 없음**: Phase A/B/C-1/C-2와 동일한 invariant 자동화 패턴

향후 Phase B/C/D 단계 격상 trigger 정량화는 별도 ADR-003 후보 (CFP-6 §11 회고에서 거론, 조건부).
