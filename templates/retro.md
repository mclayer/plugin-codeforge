# Retro 템플릿

PMOAgent가 `docs/retros/<sprint>.md` 직접 write 시 따르는 schema SSOT (CFP-26 Phase 0a 이후 owner direct write).

**사용 대상**: PMOAgent (Story 회고 + 세션 회고 + sprint close 통합 작성), Orchestrator (회고 trigger), DocsAgent (Story file §11 회고 pointer 미러링 — 직접 write 안 함)

---

## 파일 위치

- **위치**: `docs/retros/<YYYY-MM-DD>-<topic-slug>.md`. 날짜 prefix는 정렬 + 식별용
- **topic-slug**: kebab-case. 예: `marketplace-bootstrap-sprint`, `cfp-26-implementation`

---

## Frontmatter (필수)

```yaml
---
title: <한 줄 제목>
date: YYYY-MM-DD
sprint_period: "YYYY-MM-DD ~ YYYY-MM-DD"   # 단일 세션이면 같은 날짜 2번
cfp_keys: [CFP-NN, CFP-MM]                  # 본 retro가 다루는 CFP 목록
authors: [PMOAgent]                         # 작성 주체 (보조 author 있으면 추가)
related_stories: [<KEY-N>, <KEY-M>]        # 회고 대상 Story
sentinel_refs:
  - <prior retro file path>                # 직전 retro 또는 참고 retro
---
```

---

## 본문 섹션 (고정 순서)

```markdown
# <Title>

기간: <sprint_period>
범위: <CFP 개수> CFP + <PR 개수> PR + <기타 — bootstrap·migration 등>
선행 retro: [<previous retro link>](<previous-retro-file>)

---

## §1 결과 (closure)

### 1.1 commit·PR
| Story / 작업 | PR | merge commit | 비고 |
|---|---|---|---|
| ... | ... | ... | ... |

### 1.2 lint·invariant 상태
| Lint | Status |
|---|---|
| ... | ... |

---

## §2 무엇이 잘 갔나 (kept)
- 항목 1 — 구체 evidence (commit·PR·Story 인용)
- 항목 2

## §3 무엇이 막혔나 (problem)
- 항목 1 — 구체 evidence
- 항목 2

## §4 다음에 할 일 (try)
- 항목 1 — 구체 행동·CFP 후보
- 항목 2

---

## §5 cross-Story 패턴 (해당 시)
복수 Story·CFP에서 반복 발견된 패턴 — 설계 지침 부재 신호. ADR 후보 발의 sentinel.

## §6 ADR 후보 발의 (해당 시)
- 후보 1: <제목> — 근거: §5 패턴 N건
- 후보 2: ...

---

## §7 토큰 예산 vs 실제 (해당 시)
세션 회고 통합 시. playbook §8.3 테이블 참조.

| 레인 | 예산 | 실제 | 차이 |
|---|---|---|---|
| ... | ... | ... | ... |

## §8 개선 제안 (3건 이하)
다음 세션·CFP에 반영 가능한 actionable 제안. 4건 이상 작성 금지 — focus 유지.

1. ...
2. ...
3. ...
```

---

## PMOAgent 작성 절차

```
1. Sprint·Story·세션 종료 trigger 시 Orchestrator가 PMOAgent 스폰
2. 본 에이전트가 `docs/retros/<YYYY-MM-DD>-<slug>.md` 직접 write (CFP-26 Phase 0a)
3. Story file §11 회고 pointer는 Orchestrator 경유 DocsAgent에 의뢰 (Story file은 multi-writer)
4. ADR 후보 발의 (§6) 있으면 Orchestrator 경유 ArchitectAgent에 ADR draft 작성 의뢰 (write queue type=adr-draft, status=Proposed) — CFP-27.5 시점 이후 ArchitectAgent direct write로 전환
```
