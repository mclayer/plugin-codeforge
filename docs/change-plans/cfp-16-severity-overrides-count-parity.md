---
title: invariant-check Step 8 — severity_overrides count + breakdown parity (CFP-13/14 후속)
slug: cfp-16-severity-overrides-count-parity
status: draft
author: ClaudeOrchestrator (CFP-15 §11 후속)
reviewers: [user]
related_adrs: [ADR-001, ADR-003]
created: 2026-04-27
story: CFP-16
---

## §1. 목적

3 lane 각각의 severity_overrides가 SSOT (review-checklist)와 PL packet 사이에서 **count + P0/P1 breakdown** 정합 자동 검증. CFP-13/14 §11에서 잠정 후속으로 enumerate된 마지막 항목.

string equality 미적용 — 3 location form 의도적 차이 (verbose / condensed / 영문 요약) 보존.

### 수용 기준

- Step 8 추가 (Python ~95줄)
- 3 lane (design/code/security) × SSOT/PL 검증
- count + P0/P1 분포 둘 다 검증
- Codex 프롬프트는 scope 외 (의도적 영문 요약)
- 4 test case PASS (정합 + bullet 추가 / PL 제거 / severity 변경)

## §2. 현재 구조 분석

### 2.1 3 lane × 3 location severity 표현 form

| Location | form |
|----------|------|
| SSOT (review-checklists/<lane>.md) | verbose Korean: `- **<condition>** → P<N> 강제 (\`<category>\`) — <suffix>` |
| PL packet (\<Lane\>PLAgent.md) | condensed Korean: `- "<condition> → P<N>"` |
| Codex prompt (CodexReviewAgent.md) | 영문 요약: `Auto-P0: <list>, P1: <list>` |

3 form 의도적 차이 — canonical string 강제 시 가독성/LLM quality 손실.

### 2.2 현재 정합 상태 (사전 검증)

| Lane | SSOT bullets | SSOT P0/P1 | PL strings | PL P0/P1 |
|------|--------------|------------|------------|----------|
| design | 3 | P0=3 | 3 | P0=3 |
| code | 3 | P0=3 | 3 | P0=3 |
| security | 7 | P0=4, P1=3 | 7 | P0=4, P1=3 |

3 lane × SSOT/PL 모두 정합 — 본 Story는 invariant 도입.

### 2.3 자동 검증 부재

PR review 의존 — 신규 룰 추가 시 SSOT/PL 둘 다 갱신 잊을 가능성. CFP-9/13 동일 사고 패턴 (mirror drift).

### 2.4 Mapper 변호 근거

기존 CFP-9/13 string equality 패턴 비적용 입장: "Form이 다른 string은 invariant 어렵다 — PR review에 위임"

## §3. 도입할 설계

### 3.1 Mapper vs Refactor 대립 결론

채택: **Refactor 우세**.

근거:
- 약한 invariant라도 drift detect 가능 (count + breakdown)
- 가장 빈번한 사고 (룰 추가/누락)는 100% catch
- ADR-003 §3.2 Q3 (PR-time 비용 적합) 기준 → CI invariant layer 일관
- Mapper의 "PR review 위임" 우려는 reviewer가 잊을 수 있음 (CFP-11이 이미 사람의 주의 의존 fail 입증)

### 3.2 Step 8 Python parser 구조

```python
LANES = [("design", "DesignReviewPLAgent"), ("code", "CodeReviewPLAgent"), ("security", "SecurityTestPLAgent")]
SEVERITY_RE = re.compile(r"→\s*P(\d)")

def extract_ssot_severity(path):
    text = path.read_text()
    m = re.search(r"^## Severity 자동 룰\s*\n(.+?)(?=\n## |\Z)", text, re.MULTILINE | re.DOTALL)
    bullets = [l for l in m.group(1).split("\n") if l.lstrip().startswith("- ")]
    counts = Counter()
    for b in bullets:
        for sev in SEVERITY_RE.findall(b):
            counts[f"P{sev}"] += 1
    return len(bullets), counts

def extract_pl_severity(path):
    # 동일 patten — severity_overrides: YAML list 아래 - "..." 추출
```

### 3.3 비교 logic

```python
if ssot_total != pl_total: drift("count")
for sev in P0/P1:
    if ssot_counts[sev] != pl_counts[sev]: drift(sev)
```

### 3.4 Codex 프롬프트 scope 외 명시화

step name + 코멘트에 명시: "Codex 프롬프트는 의도적 영문 요약이라 scope 외 — 향후 별도 design 필요 시 재검토".

향후 reviewer가 "왜 Codex는 안 쳤지?" 질문 시 즉시 reference 가능.

### 3.5 ADR 정합성

- **ADR-001**: mirror enforce 확장 (severity_overrides field) — 결정 변경 없음
- **ADR-003 §3.2 Q3**: PR-time 검증 적합 (저비용) → CI invariant 채택. 결정 일관

## §4. API 계약

본 Story는 invariant Step 추가. 외부 API 변경 없음.

## §5. 변경 계획 (파일 단위)

| 파일 경로 | 변경 유형 | 담당 | 상태 |
|-----------|-----------|------|------|
| `.github/workflows/invariant-check.yml` | 수정 (Step 8 추가) | DocsAgent | 적용 완료 + 4 test PASS |
| `docs/stories/CFP-16.md` | 신규 | DocsAgent | 작성 완료 |
| `docs/change-plans/cfp-16-severity-overrides-count-parity.md` | 신규 (본 파일) | DocsAgent | 작성 중 |

## §6. 리팩토링 선행 작업

**없음**. Step 추가만.

## §8. Test Contract

### §8.1 커버리지 계획

- 단위 테스트: **N/A**
- 통합 테스트: **PR CI에서 invariant-check.yml 실 실행**

### §8.2 경계 조건·invariant

- **Test 1 — 정합 OK**: 3 lane × 4 metrics (총 12 비교) all match → exit 0
- **Test 2 — design SSOT P1 1개 추가**: count + P1 drift 2건
- **Test 3 — code PL list 1개 제거**: count + P0 drift 2건
- **Test 4 — security SSOT P0→P1 변경**: P0/P1 drift 2건
- **Edge case — multiple severity 한 줄에**: regex multiple match (현재 미발생, 미래 보장)

### §8.3 Perf Baseline

**N/A** — 6 file read + regex.

## §9. 분기 선택

**단일 PR**. 메타 invariant 추가.

본 PR base는 `main`. CFP-15 머지 완료.

## §10. ADR 대상 여부 + 기존 ADR 정합성

- ADR-001: mirror enforce 확장, 결정 변경 없음
- ADR-003 §3.2 Q3 적용 — CI invariant layer 채택 일관
- 신규 ADR 불요
