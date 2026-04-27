---
title: invariant-check.yml Step 5 — ADR-002 footer SSOT 참조 1줄 패턴 검증 (Phase C-2)
slug: cfp-8-adr-002-footer-parity
status: draft
author: ClaudeOrchestrator (CFP-7 §11 후속)
reviewers: [user]
related_adrs: [ADR-002]
created: 2026-04-27
story: CFP-8
---

## §1. 목적

ADR-002 §3 결정 ("DocsAgent 외 21 agent md의 '## 문서화 표준' 섹션은 1줄 + DocsAgent.md 참조 link + footer 본문 확장 금지")의 자동 enforcement.

CFP-7 Phase C-1과 동일 패턴 — narrative SSOT (ADR-002 §3) ↔ machine-readable enforcement (invariant-check Step 5) mirror.

### 수용 기준

- `.github/workflows/invariant-check.yml` Step 5 추가 (Python parser ~100줄)
- ADR-002 §3.2 path example 오타 정정 (`../../agents/...` → `../../../agents/...`)
- 4 SSOT 본문 inline 복제 금지 keyword: "phase prefix", "Story file 섹션", "FIX Ledger 스키마", "Impl Manifest 스키마"
- 위치별 expected link target:
  - `agents/<X>.md` → `DocsAgent.md`
  - `presets/<flavor>/agents/<X>.md` → `../../../agents/DocsAgent.md`
- 4 test case 모두 PASS (정합 / 섹션 부재 / 금지 keyword / link target 불일치)

## §2. 현재 구조 분석

### 2.1 ADR-002 §3 SSOT 결정

ADR-002는 다음을 enforce하기로 결정:
- DocsAgent **외**의 모든 에이전트 md 마지막 섹션 = `## 문서화 표준`
- body 1줄 + DocsAgent.md 참조 link + 본문 확장 금지

§3.4는 "CodeReview 강제 항목"으로 PR review에 위임. 이는 사람의 주의 의존 — drift 위험 잔존.

### 2.2 21 agent md footer 현 상태

3 form 패턴 식별 (실제 link target은 fenced block 참조 — 본 문서 위치에서는 점검 대상 외):

```text
Form A (minimal, 3 PL agents): [`agents/DocsAgent.md`](DocsAgent.md) 참조.
Form B (extended): GitHub Issue/PR/docs write 권한 없음. ... 문서화 표준은 [DocsAgent.md](DocsAgent.md) 참조.
Form B' (queue-enabled): Form B + "(write queue 경유)" 절 추가
Form C (presets): Form B with link target [../../../agents/DocsAgent.md] (3 levels up)
```

### 2.3 현재 자동 검증 부재

PR review로 catch 가능하나 21 사본의 동시 drift 위험은 계속 노출. 특히 신규 에이전트 추가 시 "footer 잊어버림"이 가장 빈번한 drift 패턴.

### 2.4 ADR-002 §3.2 path example 오타

ADR-002 §3.2 example:
```markdown
# presets/<flavor>/agents/<X>.md 위치
[../../agents/DocsAgent.md](../../agents/DocsAgent.md)  # ← 잘못 (실제는 3 levels up)
```

`presets/webapp/agents/X.md` → `../../agents/DocsAgent.md`는 `presets/agents/DocsAgent.md`로 향하는데, 그 경로는 존재하지 않음. 실제 사용된 경로는 `../../../agents/DocsAgent.md` (3 levels up). 본 PR에서 정정.

### 2.5 Mapper 변호 근거

기존 ADR-002 §3.4 PR review 위임을 보존하자는 Mapper 입장: "CodeReview agent에 강제 항목으로 명시. 자동화는 over-engineering, sample drift는 한 번에 일어나지 않음."

## §3. 도입할 설계

### 3.1 Mapper vs Refactor 대립 결론

채택: **Refactor 우세**.

근거:
- ADR-002 §3.4 "CodeReview 강제 항목"은 PR review의 사람의 주의 의존 — 신규 에이전트 추가 시 footer 잊어버리는 패턴이 가장 빈번
- CFP-7 동일 패턴 (narrative ↔ machine-readable parity) 입증 — Python ~100줄 한 step에 충분
- ADR-002 §3 결정 자체가 진짜 SSOT: PR review만으로는 21 사본의 동시 drift 위험 잔존
- Mapper의 over-engineering 우려: 4 keyword + 위치별 path 매핑만으로 흡수 (복잡도 < CFP-7)

### 3.2 Step 5 Python parser 구조

```python
FORBIDDEN_KEYWORDS = [
    "phase prefix",
    "Story file 섹션",
    "FIX Ledger 스키마",
    "Impl Manifest 스키마",
]

def expected_link_target(path: Path) -> str:
    parts = path.parts
    if parts[0] == "agents":
        return "DocsAgent.md"
    if parts[0] == "presets" and "agents" in parts:
        return "../../../agents/DocsAgent.md"
    return ""
```

### 3.3 Targets 수집

```python
targets = []
for p in sorted(Path("agents").glob("*.md")):
    if p.stem == "DocsAgent": continue  # SSOT 본체 — scope 외
    targets.append(p)
for p in sorted(Path("presets").glob("*/agents/*.md")):
    targets.append(p)
```

`presets/<any>/agents/*.md` 패턴으로 미래 preset 확장에도 자동 대응.

### 3.4 Section + body 추출 + 검증

```python
m = re.search(r"^## 문서화 표준\s*\n(.+?)(?=\n## |\Z)", text, re.MULTILINE | re.DOTALL)
if not m:
    errors.append(f"{path}: 섹션 부재")
    continue

body_lines = [ln for ln in m.group(1).strip().split("\n") if ln.strip()]
if len(body_lines) != 1:
    errors.append(f"{path}: body {len(body_lines)} 줄 (1줄이어야)")
    continue
body = body_lines[0]

# Link target 검증
expected = expected_link_target(path)
if expected:
    links = re.findall(r"\[(?:[^\]]+)\]\(([^)]+)\)", body)
    if not any(href.endswith("DocsAgent.md") for href in links):
        errors.append(f"{path}: DocsAgent.md 참조 link 부재")
        continue
    if expected not in links:
        errors.append(f"{path}: link target {links} ≠ {expected}")
        continue

# 금지 keyword 검사
for kw in FORBIDDEN_KEYWORDS:
    if kw in body:
        errors.append(f"{path}: 금지 keyword '{kw}'")
        break
```

### 3.5 ADR-002 §3.2 path 오타 정정

별도 commit으로 분리 안 함. invariant 자동화 enforce 대상이 잘못된 example을 포함했으므로 함께 정정이 자연스러움. ADR 결정 변경이 아닌 documentation fix.

### 3.6 ADR 정합성

- ADR-001 무관
- ADR-002: 본 변경이 enforce 대상. §3.2 path example 오타만 정정 (결정 변경 아님)
- 신규 ADR 필요 없음

## §4. API 계약

### 4.1 invariant-check workflow Step 추가

기존 Step 1-4 그대로 + Step 5 (Python heredoc).

### 4.2 Error message 형식

```
::error::ADR-002 footer pattern 정합 실패 (N drift)
  - <path>: '## 문서화 표준' 섹션 부재 (ADR-002 §3 위반)
  - <path>: footer body 1줄이 아님 (N 줄)
  - <path>: footer link target 불일치 — expected '<X>', got [...]
  - <path>: footer body에 SSOT 본문 키워드 '<keyword>' 포함 — drift 위험
```

### 4.3 Exit code

기존 그대로 — `sys.exit(1)` 시 workflow fail.

## §5. 변경 계획 (파일 단위)

| 파일 경로 | 변경 유형 | 담당 | 상태 |
|-----------|-----------|------|------|
| `.github/workflows/invariant-check.yml` | 수정 (Step 5 + header comment 갱신) | DocsAgent | 적용 완료 + 4 test PASS |
| `docs/adr/ADR-002-docsagent-inherit-footer-pattern.md` | 수정 (§3.2 path 1줄) | DocsAgent | 적용 완료 |
| `docs/stories/CFP-8.md` | 신규 | DocsAgent | 작성 중 |
| `docs/change-plans/cfp-8-adr-002-footer-parity.md` | 신규 (본 파일) | DocsAgent | 작성 중 |

## §6. 리팩토링 선행 작업

**없음**. invariant-check.yml에 step 추가만, 기존 Step 1-4 변경 없음.

## §8. Test Contract

### §8.1 커버리지 계획

- 단위 테스트: **N/A** — Python script지만 plugin에 pytest 인프라 없음. Local sim 4 case로 갈음
- 통합 테스트: **PR CI에서 invariant-check.yml 실 실행** — 본 PR이 첫 실증
- 인프라 테스트: **N/A**

### §8.2 경계 조건·invariant

- **Test 1 — 정합 OK**: 현 plugin (21 agent md) → exit 0
- **Test 2 — section 부재**: DeveloperAgent의 `## 문서화 표준` 섹션 제거 → "섹션 부재" 1건
- **Test 3 — 금지 keyword**: ArchitectAgent body에 "phase prefix 11종" 삽입 → "금지 keyword" 1건
- **Test 4 — link target 불일치**: presets/webapp/agents/Backend...에 `../../agents/...` (잘못된 2 levels up) → "link target 불일치" 1건
- **Edge case — DocsAgent**: scope 외 (footer 부재가 정상)
- **Edge case — 빈 body**: `body_lines == []` → "0 줄" detect

### §8.3 Perf Baseline

**N/A** — 21 agent file read + regex, ms 수준.

## §9. 분기 선택

**단일 PR**. Phase 1/2 분리 면제.

Commit 시리즈 2개:
- **Commit 1**: `.github/workflows/invariant-check.yml` Step 5 + header + ADR-002 §3.2 path fix
- **Commit 2**: `docs/stories/CFP-8.md` + `docs/change-plans/cfp-8-...md` 영속화

본 PR base는 `main`. CFP-7 머지 완료.

## §10. ADR 대상 여부 + 기존 ADR 정합성

- ADR-001 무관
- **ADR-002 결정 변경 없음** (§3.2 path example 오타만 정정)
- **신규 ADR 필요 없음**: Phase A/B/C-1과 동일한 invariant 자동화 패턴

향후 Phase B/C/D 단계 격상 trigger 정량화는 별도 ADR-003 후보 (CFP-6 §11 회고에서 거론, 조건부).
