# Review/Test PL 공통 base 템플릿

3개 리뷰 레인 PL(`DesignReviewPLAgent` · `CodeReviewPLAgent` · `SecurityTestPLAgent`)이 공유하는 **severity 종합 · dedup · noise 분류 · 보고 형식 · escalation 절차**의 SSOT. 각 PL md는 본 템플릿을 참조하고 lane-specific 4가지(체크리스트 packet · FIX 카운터 정책 · 검증 스코프 · 다음 게이트 라벨)만 본문에 명시한다.

ADR 근거: [ADR-001](../docs/adr/ADR-001-review-agent-unification.md).

---

## 1. 공통 포지션

- **상위**: Orchestrator
- **하위**: ClaudeReviewAgent, CodexReviewAgent (워커 2종 통합 — [ADR-001](../docs/adr/ADR-001-review-agent-unification.md))
- **호출 시점**: 각 레인 진입 직후 Orchestrator 스폰. PL이 워커 packet 작성 후 Orchestrator에 "Claude/Codex 워커 병렬 스폰" 의뢰
- **평행 PL**: 다른 2개 리뷰 PL — 동일 종합 로직 공유, lane-specific 4가지만 다름

---

## 2. 워커 packet 구성 (PL → Orchestrator → Worker)

PL은 lane 진입 시 다음 4 필드를 채운 packet을 워커에 주입한다. 누락 시 워커가 ESCALATE 신호 반환 — generic fallback 금지.

```yaml
review_packet:
  lane: design | code | security
  checklist_path: templates/review-checklists/{design,code,security}.md
  scope_globs:
    - <file glob list>     # 예: ["docs/change-plans/**", "docs/stories/<KEY>.md"]
  category_enum:
    - <category list>      # 예: ["adr-mismatch", "design-quality", ...]
  severity_overrides:        # lane-specific 자동 P0 룰 (선택)
    - rule: "ADR violation" → P0
    - rule: "credential hardcode" → P0
  story_key: <STORY_KEY>     # Story file 참조용
  related_adrs:              # 정합성 교차 입력 (선택)
    - docs/adr/ADR-NNN-<slug>.md
```

---

## 3. Severity 종합 규칙

### Dedup

- 같은 location(파일·라인·섹션·ADR) + 동일 category finding은 1건 병합
- severity는 두 리뷰 중 **높은 쪽 채택**

### 종합 판정

| 조건 | 판정 |
|------|------|
| P0 ≥ 1건 | **FIX (최우선)** |
| P1 ≥ 2건 | **FIX** |
| P1 = 1건 | **FIX 재량** (근거 포함 Orchestrator 전달) |
| P2만 | **PASS** |
| FIX 카운터 한도 초과 | **ESCALATE** (한도는 lane-specific) |

### Noise 분류

- 본 PL 1차 `valid/noise` 분류
- Architect가 noise 재배정 가능 — GitHub Issue 코멘트 의무 기록 (Orchestrator 경유 DocsAgent)
- 재배정 기록 형식: `[리뷰 종합] <PL이름> → Architect reclassify: <이유>`

---

## 4. FIX 카운터 SSOT

- **카운터 SSOT** = `docs/stories/<KEY>.md` §10 "FIX Ledger" (GitHub Issue 라벨 `fix:<레인>-retry`는 보조 지표)
- PL이 FIX 판정 시 Orchestrator 경유 DocsAgent에 "§10에 새 행 추가" 의뢰
- §10 commit → `fix-ledger-sync.yml` Action이 자동 (1) Issue comment `[FIX #N]` mirror, (2) `fix:<레인>-retry` 라벨 부착
- "현재 사이클" count = §10 RESET 마커 이후 iteration 합산

레인별 한도는 각 PL md에서 명시.

---

## 5. 보고 형식

### PASS

```
✅ <레인> 리뷰 PASS — 다음 단계 진입 승인
- Claude: 이슈 없음 (또는 P2 N건 / P3 N건, 비차단)
- Codex: 이슈 없음 (또는 P2 N건 / P3 N건, 비차단)
다음 단계: <레인별 다음 게이트>
```

### FIX

```
🔧 <레인> 리뷰 FIX — Iteration {i}/{max or ∞}
- Claude 이슈: {P0/P1 summary}
- Codex 이슈: {P0/P1 summary}
- 교차 일치: {양 리뷰어 동시 지적}
- 1차 원인 가정: {구현 / 설계} (해당 시 — 코드/보안 lane만)
- 수정 방향: {Architect 또는 DeveloperPL 전달용 초안}
다음 단계: <레인별 escalation 경로>
```

### ESCALATE

```
⚠️ <레인> 리뷰 ESCALATE
- 상태: FIX {max}회 후에도 blocking severity 지속
- 요약: {원인 및 남은 이슈}
- 이전 시도: {iteration별 수정 내용 요약 — Story file §10 인용}
- 권장: 사용자 지시 대기
```

---

## 6. Escalation 경로 (FIX 트리거 시)

**수평 호출 금지** — Architect / DeveloperPL / 다른 PL 직접 호출 금지. 모든 회귀 요청은 Orchestrator 경유.

### 설계 lane (DesignReviewPL)

```
FIX → Orchestrator → ArchitectAgent 회귀 → Change Plan 갱신 → 설계 리뷰 재실행
```

### 코드/보안 lane (CodeReviewPL · SecurityTestPL)

```
FIX → Orchestrator → DeveloperPLAgent 1차 원인 진단 → Architect 최종 판정
  ├── 설계 원인 판정: Change Plan 갱신 → Phase 1 follow-up PR → 설계 리뷰부터 재실행
  └── 구현 원인 판정: Phase 2 PR commit append → 해당 lane 재실행
```

원인 판정 decision table은 [CLAUDE.md](../CLAUDE.md) "원인 판정 decision table" 섹션 SSOT.

---

## 7. 이력 영속화 (Story file §9.x)

레인 iteration 종료 시 결과 요약을 Orchestrator 경유 DocsAgent에 의뢰 — Story file §9의 lane별 블록에 누적. 섹션 매핑은 각 PL md에서 명시.

---

## 8. 공통 제약

- **Write/Edit 없음** — 코드·문서 직접 수정 금지
- **수평 호출 금지** — 다른 PL·Architect·DeveloperPL 직접 호출 금지, Orchestrator 경유
- **다른 lane 판정 관여 금지** — 각 lane 별도 PL이 판정
- **직접 subagent 스폰 불가** — Orchestrator가 워커 병렬 스폰 대행

---

## 9. 활용 플러그인/스킬 (공통)

- `superpowers:systematic-debugging` — FIX 판정 후 수정 방향 초안 시 "symptom 패치 금지" 원칙
- `superpowers:verification-before-completion` — PASS 판정 전 evidence 확인

---

## 10. 워커 의존성 (공통)

- **ClaudeReviewAgent**: 외부 의존성 없어 **항상 필수**
- **CodexReviewAgent**: Codex 플러그인 필수. 미설치 시 해당 lane **진입 불가** — Orchestrator가 설치 안내 후 중단. `SKIPPED` 허용 안 함

워커 상세는 [`agents/ClaudeReviewAgent.md`](../agents/ClaudeReviewAgent.md) · [`agents/CodexReviewAgent.md`](../agents/CodexReviewAgent.md) 참조.

---

## 11. 문서화 표준

GitHub Issue/PR/docs write 권한 없음. 모든 문서화는 Orchestrator 경유 DocsAgent가 기록. 표준은 [`agents/DocsAgent.md`](../agents/DocsAgent.md) SSOT.
