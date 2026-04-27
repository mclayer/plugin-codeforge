---
title: invariant-check Step 6 → 3 lane 확장 (CFP-9 후속)
slug: cfp-13-extend-enum-parity-3-lanes
status: draft
author: ClaudeOrchestrator (CFP-12 §11 후속)
reviewers: [user]
related_adrs: [ADR-001]
created: 2026-04-27
story: CFP-13
---

## §1. 목적

CFP-9가 lane=code에 도입한 review category enum 정합 invariant를 lane=design + lane=security로 확장. Step 6을 lane-loop refactor.

ADR-001 (워커 통합 packet 구조) mirror가 3 lane 모두에 적용되므로 invariant도 3 lane 모두에 적용이 자연스러움.

### 수용 기준

- LANES list 3개 (design / code / security) parameterize
- SSOT path 패턴: `templates/review-checklists/{lane}.md`
- Codex regex 패턴: `#### lane={lane}` anchor + 첫 번째 `category from {...}`
- 4 test case PASS (3 lane 정합 + design SSOT drift + security PL drift + code Codex drift)
- CFP-9의 lane=code invariant 100% 동일 동작 (regression 없음)

## §2. 현재 구조 분석

### 2.1 CFP-9 Step 6 (lane=code only)

3 location:
- SSOT: `templates/review-checklists/code.md` line 14 (10 cat)
- Mirror 1: `agents/CodeReviewPLAgent.md` `category_enum:` (10 cat YAML)
- Mirror 2: `agents/CodexReviewAgent.md` `#### lane=code` 이후 inline (10 cat set)

코드 ~75줄.

### 2.2 lane=design 동일 mirror 구조

- SSOT: `templates/review-checklists/design.md` (6 cat: adr-mismatch / design-completeness / mapper-refactor-balance / implementability / test-contract / section-missing)
- Mirror 1: `agents/DesignReviewPLAgent.md` `category_enum:` (6 cat YAML)
- Mirror 2: `agents/CodexReviewAgent.md` `#### lane=design` 이후 inline (6 cat set)

### 2.3 lane=security 동일 mirror 구조

- SSOT: `templates/review-checklists/security.md` (9 cat: injection / trust-boundary / auth / credential / crypto / pii / dependency-cve / config / race)
- Mirror 1: `agents/SecurityTestPLAgent.md` `category_enum:` (9 cat YAML)
- Mirror 2: `agents/CodexReviewAgent.md` `#### lane=security` 이후 inline (9 cat set)

### 2.4 자동 검증 부재 (lane=design/security)

CFP-9가 lane=code만 cover. design/security drift는 사람의 PR review 의존 잔존.

### 2.5 Mapper 변호 근거

기존 Step 6 (lane=code only) 보존하자는 Mapper 입장: "logic이 동일하다고 3 lane을 1 step에 묶는 건 추상화. step 분리가 자연스러운 boundary".

## §3. 도입할 설계

### 3.1 Mapper vs Refactor 대립 결론

채택: **Refactor 우세**.

근거:
- 3 lane은 SSOT path / PL md / Codex anchor만 다르고 검증 logic 100% 동일
- step 3개 분리 시 200+ 줄 중복 — 코드 유지보수 부담 증가
- lane만 다른 parameterize는 자연 추상화 (lane name 자체가 parameter)
- Mapper의 "step 분리" 선호는 lane별 검증 logic이 분기될 때만 재검토 가치

### 3.2 Step 6 lane-loop refactor

```python
LANES = [
    ("design",   "DesignReviewPLAgent"),
    ("code",     "CodeReviewPLAgent"),
    ("security", "SecurityTestPLAgent"),
]

codex_text = Path("agents/CodexReviewAgent.md").read_text(encoding="utf-8")
all_errors = []

for lane, pl_name in LANES:
    ssot_path = f"templates/review-checklists/{lane}.md"
    pl_path = f"agents/{pl_name}.md"
    # ... extract ssot_enum, pl_enum, codex_enum ...
    # ... compare and append to all_errors with lane prefix ...
```

각 lane 결과 progress 출력:
```
✓ lane=design: 6 categories x 3 locations
✓ lane=code: 10 categories x 3 locations
✓ lane=security: 9 categories x 3 locations
```

drift 시 error에 `[lane=<X>]` prefix 추가로 위치 명확화.

### 3.3 ADR 정합성

- **ADR-001**: 워커 통합 packet 구조의 mirror 정합 — 본 Story가 그 mirror enforce 확장. ADR-001 결정 변경 없음
- ADR-002 무관
- 신규 ADR 불요

## §4. API 계약

본 Story는 invariant-check workflow Step 6의 내부 logic refactor. 외부 API 변경 없음.

Error message 형식 (drift 시):
```
::error::Review category enum parity 실패 (N drift)
  [lane=design] agents/DesignReviewPLAgent.md category_enum (N) ≠ SSOT (M)
    SSOT  : [...]
    PL    : [...]
    diff(only in SSOT): [...]
    diff(only in PL)  : [...]
```

기존 CFP-9 형식에 lane prefix만 추가.

## §5. 변경 계획 (파일 단위)

| 파일 경로 | 변경 유형 | 담당 | 상태 |
|-----------|-----------|------|------|
| `.github/workflows/invariant-check.yml` | 수정 (Step 6 refactor) | DocsAgent | 적용 완료 + 4 test PASS |
| `docs/stories/CFP-13.md` | 신규 | DocsAgent | 작성 완료 |
| `docs/change-plans/cfp-13-extend-enum-parity-3-lanes.md` | 신규 (본 파일) | DocsAgent | 작성 중 |

## §6. 리팩토링 선행 작업

**없음**. Step 6 자체 refactor가 본 Story의 핵심.

## §8. Test Contract

### §8.1 커버리지 계획

- 단위 테스트: **N/A** — Local sim 4 case로 갈음
- 통합 테스트: **PR CI에서 invariant-check.yml 실 실행**
- 인프라 테스트: **N/A**

### §8.2 경계 조건·invariant

- **Test 1 — 정합 OK**: 3 lane × 3 location 모두 정합 (10+6+9 = 25 categories, 동일 순서)
- **Test 2 — design SSOT 추가**: `new-design-cat` 1개 → PL/Codex 둘 다 drift detect (2건)
- **Test 3 — security PL 누락**: `race` 제거 → PL drift 1건
- **Test 4 — code Codex 순서 변경**: CFP-9 case 동일 — Codex drift detect (regression test)
- **Edge case — lane 1개만 fail**: 다른 lane은 ✓ 출력 후 전체 sys.exit(1)

### §8.3 Perf Baseline

**N/A** — 9 file read + 9 regex, ms 수준.

## §9. 분기 선택

**단일 PR**. Phase 1/2 분리 면제.

본 PR base는 `main`. CFP-12 머지 완료.

## §10. ADR 대상 여부 + 기존 ADR 정합성

- **ADR-001**: mirror 구조 enforce 확장 — 결정 변경 없음
- ADR-002 무관
- 신규 ADR 불요

CFP-12 §11에서 거론된 ADR-003 (3 layer 책임 분리)은 별도 Story 후보.
