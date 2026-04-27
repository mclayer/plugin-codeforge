---
title: invariant-check.yml Step 4 — frontmatter ↔ CLAUDE.md "Write queue 의뢰 권한" 표 정합 (Phase C-1)
slug: cfp-7-write-queue-permission-parity
status: draft
author: ClaudeOrchestrator (CFP-6 §11 후속)
reviewers: [user]
related_adrs: []
created: 2026-04-27
story: CFP-7
---

## §1. 목적

CFP-6 schema-level enforcement에 이어 Phase C-1 — narrative ↔ machine-readable mirror 정합을 자동화. CLAUDE.md "Write queue 의뢰 권한" 표 ↔ agents/*.md frontmatter `permissions.allow` 양방향 SSOT drift를 invariant-check workflow Step 4로 차단.

### 수용 기준

- `.github/workflows/invariant-check.yml` Step 4 추가 (Python parser ~90줄)
- 7 SHORTHAND 매핑 (CodebaseMapper, Refactor, RequirementsAnalyst, Researcher, DesignReviewPL, CodeReviewPL, SecurityTestPL)
- DocsAgent EXEMPT_FROM_TABLE (single writer 별도 역할)
- 4 test case 모두 PASS:
  - Test 1: 현 plugin (15 listed + DocsAgent) → OK
  - Test 2: agent에서 권한 완전 누락 → drift detect
  - Test 3: 표에 없는 agent가 권한 보유 → drift detect
  - Test 4: 비대칭 (Edit만 또는 Write만) → drift detect

## §2. 현재 구조 분석

### 2.1 invariant-check.yml 현재 상태

CFP-5 Phase A 도입. 3 step:
1. Workflow parity (templates ↔ .github)
2. Version match (plugin.json ↔ CHANGELOG.md)
3. Agent count (agents/*.md ↔ CLAUDE.md "N core 에이전트")

shell 기반 `diff`/`grep`/`jq`로 충분한 수준의 mechanical 검증.

### 2.2 CLAUDE.md "Write queue 의뢰 권한" 표

본 line 1줄에 15개 에이전트 enumerate:

```
- **Write queue 의뢰 권한** (`.claude-work/doc-queue/**`만): RequirementsPLAgent, DomainAgent, PMOAgent, ArchitectAgent, CodebaseMapper, Refactor, DesignReviewPL, CodeReviewPL, SecurityTestPL, ClaudeReviewAgent, CodexReviewAgent, DeveloperPLAgent, RequirementsAnalyst, Researcher, TestAgent — 기타 Edit/Write 없음
```

7개가 shorthand 표기 (Agent suffix 생략 또는 PL suffix만).

### 2.3 agents/*.md frontmatter

각 에이전트의 `permissions.allow` list에 다음 두 entry가 짝으로 존재해야 정합:

```yaml
permissions:
  allow:
    - Edit(.claude-work/doc-queue/**)
    - Write(.claude-work/doc-queue/**)
```

현재 16 agent가 이 권한 보유 (15 표 listed + DocsAgent).

### 2.4 자동 검증 부재 — drift 위험

agent 추가/삭제 시 표와 frontmatter 동기화는 사람의 주의 의존. 비대칭 권한(Edit만 or Write만)도 누락 가능. PR review로 검출 가능하나 번거로움.

### 2.5 Mapper 변호 근거

기존 shell 기반 invariant-check를 보존하자는 Mapper 입장: "Python 도입은 의존성 폭증. shell + grep으로 비슷한 검증 가능."

## §3. 도입할 설계

### 3.1 Mapper vs Refactor 대립 결론

채택: **Refactor 우세**.

근거:
- Frontmatter 파싱은 awk/sed로 복잡 — 첫 두 `---` 사이 raw text 추출 + line continuation 처리
- Python 표준 라이브러리만 사용 (PyYAML 의존 회피) — `re` + `pathlib`만, ubuntu-latest runner default 의존
- 90줄 한 step에 의도 명료 표현 — Mapper 의존성 우려 흡수
- 향후 Phase C-2/C-3/D도 비슷한 패턴 → Python parser 도입이 자연스러운 ratchet

### 3.2 Step 4 Python parser 구조

```python
SHORTHAND = {
    "CodebaseMapper": "CodebaseMapperAgent",
    "Refactor": "RefactorAgent",
    "RequirementsAnalyst": "RequirementsAnalystAgent",
    "Researcher": "ResearcherAgent",
    "DesignReviewPL": "DesignReviewPLAgent",
    "CodeReviewPL": "CodeReviewPLAgent",
    "SecurityTestPL": "SecurityTestPLAgent",
}
EXEMPT_FROM_TABLE = {"DocsAgent"}  # single writer
```

### 3.3 표 line 추출 정규식

```python
m = re.search(
    r"\*\*Write queue 의뢰 권한\*\*[^:]*:\s*(.+?)\s*[—-]\s*기타",
    claude_md,
)
```

`*\*Write queue 의뢰 권한\*\*`로 표 line anchor → `:` 이후 → `— 기타`까지가 listed agent enumerate.

### 3.4 frontmatter 파싱 + 권한 검출

```python
fm_match = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
fm = fm_match.group(1)
has_edit = bool(re.search(r"Edit\(\.claude-work/doc-queue/\*\*\)", fm))
has_write = bool(re.search(r"Write\(\.claude-work/doc-queue/\*\*\)", fm))
```

PyYAML 의존 회피 — 첫 두 `---` 사이 raw text에서 정규식 직접 매칭.

### 3.5 3종 drift 분류

```python
errors = []

# 비대칭 (Edit만 or Write만)
for name, perms in sorted(actual_partial.items()):
    errors.append(f"{name}: Edit/Write 비대칭 — Edit={...} Write={...}")

# Listed but 완전 부재 (partial은 위에서 별도 보고, 중복 회피)
partial_names = set(actual_partial.keys())
for name in sorted(listed_full - actual_queue_agents - partial_names):
    errors.append(f"{name}: listed but frontmatter 부재")

# Frontmatter 있는데 unlisted (DocsAgent 제외)
for name in sorted(actual_queue_agents - listed_full - EXEMPT_FROM_TABLE):
    errors.append(f"{name}: frontmatter 있음 but 표 부재")
```

### 3.6 ADR 정합성

- ADR-001/ADR-002 무관
- 신규 ADR 필요 없음

## §4. API 계약

### 4.1 invariant-check workflow Step 추가

기존 Step 1-3 그대로 + Step 4 (Python heredoc).

### 4.2 Error message 형식

GitHub Actions native annotation:

```
::error file=CLAUDE.md::Write queue 권한 정합 실패 (N drift)
  - <agent>: listed but frontmatter 부재
  - <agent>: 비대칭 Edit=True Write=False
  - <agent>: frontmatter 있음 but 표 부재
```

### 4.3 Exit code

기존 Step 1-3 그대로 (workflow 레벨에서 step.run 비-0 시 fail). Step 4도 `sys.exit(1)` 시 workflow fail.

## §5. 변경 계획 (파일 단위)

| 파일 경로 | 변경 유형 | 담당 | 상태 |
|-----------|-----------|------|------|
| `.github/workflows/invariant-check.yml` | 수정 (Step 4 + header comment 갱신) | DocsAgent (= 본 작업자) | 적용 완료 + 4 test PASS |
| `docs/stories/CFP-7.md` | 신규 | DocsAgent | 작성 중 |
| `docs/change-plans/cfp-7-write-queue-permission-parity.md` | 신규 (본 파일) | DocsAgent | 작성 중 |

## §6. 리팩토링 선행 작업

**없음**. invariant-check.yml에 step 추가만, 기존 step 변경 없음.

## §8. Test Contract

### §8.1 커버리지 계획

- 단위 테스트: **N/A** — Python script지만 plugin에 pytest 인프라 없음. Local sim 4 case로 갈음
- 통합 테스트: **PR CI에서 invariant-check.yml 실 실행** — 본 PR이 첫 실증
- 인프라 테스트: **N/A**

### §8.2 경계 조건·invariant

- **Test 1 — 정합 OK**: 현 plugin (15 listed + DocsAgent) → exit 0
- **Test 2 — 권한 완전 누락**: PMOAgent에서 Edit/Write 둘 다 제거 → "PMOAgent: listed but frontmatter 부재" 1건
- **Test 3 — 표에 없는데 권한 보유**: DeveloperAgent (role:dev) frontmatter에 doc-queue 추가 → "DeveloperAgent: frontmatter 있음 but 표 부재" 1건
- **Test 4 — 비대칭**: PMOAgent에서 Write만 제거 → "PMOAgent: Edit/Write 비대칭" 1건 (listed-missing 중복 보고 X)
- **Edge case — frontmatter 부재 agent**: skip (continue) — 정합 검사 대상 아님
- **Edge case — 표 line 부재 (CLAUDE.md 자체 변조)**: exit 1 + "표 라인 부재" 에러

### §8.3 Perf Baseline

**N/A** — 20 agent file read + regex, ms 수준.

## §9. 분기 선택

**단일 PR**. Phase 1/2 분리 면제.

Commit 시리즈 2개:
- **Commit 1**: `.github/workflows/invariant-check.yml` Step 4 추가 + header comment 갱신
- **Commit 2**: `docs/stories/CFP-7.md` + `docs/change-plans/cfp-7-...md` 영속화

본 PR base는 `main`. CFP-5/CFP-6 모두 머지 완료.

## §10. ADR 대상 여부 + 기존 ADR 정합성

- ADR-001/ADR-002 무관
- **신규 ADR 필요 없음**: Phase A/B와 동일한 invariant 자동화 패턴, 기존 패턴 적용

향후 Phase B/C/D 단계 격상 trigger 정량화는 별도 ADR-003 후보 (CFP-6 §11 회고에서 거론, 조건부).
