# `docs/stories/<KEY>.md` Story File Structure Template

GitHub Story Issue 1건당 `docs/stories/<KEY>.md` 파일 1개. 요구사항 접수부터 Phase 2 PR merge까지 모든 컨텍스트·설계·개발 서사가 이 파일로 누적.

**사용 대상**: 모든 lane plugin (자기 owner section 갱신, codeforge-{requirements,design,develop,test,pmo,review} CLAUDE.md self-write 표 참조), Orchestrator (§10 FIX Ledger + general docs/** 처리), 모든 에이전트 (파일 경로 + 섹션 번호 참조해 read-only fetch via `Read`)

**위치**: `docs/stories/<KEY>.md` (KEY = `<github.story_key_prefix>-N`, 예: `PLG-7`). 제목 H1 `<KEY>: <한 줄 요약>`.

**자동 생성**: `story-init.yml` Action이 사용자가 GitHub Issue Form (story.yml) 제출 시 자동:
1. 다음 KEY 번호 계산 (`Glob(docs/stories/<PREFIX>-*.md)` max+1)
2. 파일 신규 생성 (§1 verbatim, §2-11 placeholder)
3. Phase 1 PR 자동 open
4. Issue body를 docs file 링크로 변환

각 lane plugin 이 Action 후 자기 owned section 갱신 (codeforge-{requirements,design,develop,test,pmo,review} CLAUDE.md self-write 표).

---

## 라벨 (GitHub Issue labels)

GitHub Issue (Story 1건)에 부착되는 라벨:

- `type:story` 필수
- `phase:*` (single-active, phase-label-invariant.yml Action이 강제) — 7종 중 1개
- `gate:design-review-pass` (Phase 1 PR mergeable 전제, 설계 리뷰 PASS 후 부착)
- `gate:security-test-pass` (Phase 2 PR mergeable 전제, 보안 테스트 PASS 후 부착)
- `fix:*-retry` (FIX 루프 누적, fix-ledger-sync.yml Action이 자동 부착)
- `component:*` (consumer overlay `labels.components`)
- `adr:NNN` (관련 ADR)

§1 변조 금지 invariant는 `story-section-1-immutable.yml` Action이 강제 (PR에서 §1 line range 변경 시 자동 reject).

---

## 섹션 구조 (번호 고정 · 누락 섹션 진입 차단)

### §1. 사용자 요구사항 (verbatim — story-section-1-immutable.yml로 변경 차단)
- story-init.yml Action이 사용자 GitHub Issue Form 입력을 verbatim 삽입
- 재작성·요약 금지 (변조 방지)
- §1 line range 변경 시 PR 자동 reject

### §2. 도메인 해석 (DomainAgent)
- 도메인 제약 / 암묵 가정 / 범위 경계 / 우선순위 힌트
- 지식 공백 섹션
- 기존 `docs/domain-knowledge/` 파일 참조 목록

**타이밍**: 파일 생성 시점엔 placeholder (요구사항 레인 진입 전 비어있음). DomainAgent가 Analyst·Researcher와 **병렬 실행** 후 결과 반환하면 RequirementsPL 이 §2 직접 self-write (codeforge-requirements) — 따라서 **Analyst·Researcher는 §2를 입력으로 참조하지 않음** (독립 관점 보장). §5·§6과 같은 사이클에 동시 기록.

### §3. 관련 ADR
- 직접 제약 ADR (verbatim 또는 full 요약)
- 배경 참조 ADR (번호 + 1줄 요약)
- 기존 ADR 갱신·신설 필요 여부

### §4. 관련 코드 경로 + 책임
- 변경 대상 파일·클래스·레이어
- 현재 책임 요약

### §5. 요구사항 확장 해석 (RequirementsAnalyst)
- 유스케이스 / AC / 엣지 케이스 / 제외 범위 / 암묵 가정
- §5.5 "사용자 확인 필요" (blocking wait 항목)

### §6. 외부 지식 배경 (Researcher)
- Researcher 자체 도출 키워드 커버리지 + 출처 URL
- ADR 정합성 점검 결과
- "외부 지식 보강 불필요" 판정 시에도 사유를 명시 (섹션 생략 금지 — 독립 관점 결과 보존)

### §7. 설계 서사 (ArchitectAgent (chief author) → ArchitectPLAgent 검수)
- Change Plan 링크 (`docs/change-plans/<slug>.md`)
- §1 목적 / §3 도입할 설계 / §4 API 계약 / §7 보안 설계 요약 / §9 분기 선택 요약 미러링 (5-10줄)
  - §7 보안 설계 요약: Change Plan §7의 보안 설계 요약 (1-3줄) 또는 `N/A — <사유>` 그대로 미러링
- CodebaseMapper ↔ RefactorAgent ↔ SecurityArchitectAgent 3-way 대립 결론

### §8. 개발 서사 (DeveloperPL + role:dev roster)

#### §8.1 Backend 산출물
#### §8.2 Frontend 산출물
#### §8.3 DataEng 산출물
#### §8.4 InfraEng 산출물 (consumer roster에 따라 추가/생략 가능)

#### §8.5 Impl Manifest (파일 단위 매핑표)
[`impl-manifest.md`](impl-manifest.md) 스키마 따름. DeveloperPL 이 §8.5 직접 self-write (codeforge-develop) → Phase 2 PR에 commit → `subissue-from-impl-manifest.yml` Action이 자동으로 file 단위 sub-issue 생성.

### §9. 품질 게이트 이력

#### §9.0 Clarification 재스폰 이력 (FIX 아님)

PL(RequirementsPL / ArchitectPLAgent)이 병렬 서브 에이전트 결과 통합 중 추가 질의를 위해 Orchestrator 경유 재스폰 요청한 이력. FIX 루프(§10)와 구분 — 재스폰은 아직 게이트 실패가 아님.

| # | 시각 | 레인 | 재스폰 대상 | Clarification 사유 | 이전 출력 ref | 결과 |
|---|------|------|-------------|-------------------|---------------|------|
| 1 | ISO8601 | 요구사항 | ResearcherAgent | {PL이 추가 조사 요청한 주제} | §6 initial | §6 보강 |
| 2 | ISO8601 | 설계 | RefactorAgent | {ArchitectPLAgent가 특정 제안 재해석 요청} | §7 Change Plan draft v1 | §7 갱신 |

- 같은 에이전트 **2회 한도** — 3회째 필요성 발생 시 사용자 ESCALATE로 전환
- Orchestrator append-only 관리 (CFP-32, 행 삭제·수정 금지)

#### §9.1 설계 리뷰 Iteration N
- Claude · Codex severity counts + 주요 findings + DesignReviewPL 판정
- Iteration N마다 append

#### §9.2 구현 리뷰 Iteration N
- 동일 형식

#### §9.3 구현 테스트 레인
- 기능 통과/실패 + 성능 baseline 대비 변동

#### §9.4 보안 테스트 레인
- 1차 layer 결과 요약 (Dependabot / CodeQL / Secret Scanning / Push Protection)
- Claude · Codex severity counts + 주요 findings + SecurityTestPL 판정
- Iteration N마다 append

### §10. FIX Ledger (FIX 카운터 SSOT)

| Iter | 시각 | 레인 | 트리거 | 원인 판정 | 재실행 범위 | RESET? |
|------|------|------|--------|-----------|-------------|--------|
| 1    | ISO8601 | 설계-리뷰 | ... | 설계 | ... | — |
| ... |

Orchestrator 가 append-only 관리 (CFP-32 monopoly, 행 삭제·수정 금지). "현재 사이클" count는 RESET 마커 이후 iteration만 합산. §10 commit이 main에 push되면 `fix-ledger-sync.yml` Action이 자동:
- Story Issue에 `[FIX #N]` 코멘트 mirror
- `fix:<레인>-retry` 라벨 부착

### §11. 참조
- GitHub Issue URL: `https://github.com/<org>/<repo>/issues/<N>`
- Phase 1 PR URL (merged)
- Phase 2 PR URL (merged)
- Change Plan 링크 (`docs/change-plans/<slug>.md`)
- 관련 ADR 링크 (`docs/adr/ADR-NNN-<slug>.md`)
- 회고 (PMOAgent 작성)

---

## 단계별 갱신 책임

| 단계 | 갱신 섹션 | Owner agent |
|------|----------|-------------|
| 요구사항 접수 (story-init.yml Action 자동) | §1 verbatim 삽입, §2-11 placeholder | story-init.yml Action |
| 요구사항 병렬 에이전트 완료 | Domain→§2 / Analyst→§5 / Researcher→§6 (각 에이전트 직접 Edit) | RequirementsPLAgent / DomainAgent (codeforge-requirements) |
| 요구사항 확정 (RequirementsPLAgent) | §3-4 | RequirementsPLAgent (codeforge-requirements) |
| 설계 확정 (ArchitectAgent → ArchitectPLAgent 검수) | §3/§7/§11 + `docs/change-plans/<slug>.md` + `docs/adr/ADR-NNN-<slug>.md` | ArchitectAgent (codeforge-design direct Edit) |
| 설계 리뷰 iteration (DesignReviewPL) | §9.1 | DesignReviewPL (codeforge-review review-verdict-v2) |
| 설계 리뷰 PASS | gate:design-review-pass 라벨 부착 → Phase 1 PR mergeable | DesignReviewPL (codeforge-review review-verdict-v2) |
| 구현 완료 (DeveloperPL) | §8.1-8.4 + §8.5 매핑표 commit + Phase 2 PR creation | DeveloperPL (codeforge-develop direct Edit) |
| 구현 리뷰 iteration (CodeReviewPL) | §9.2 | CodeReviewPL (codeforge-review review-verdict-v2) |
| 구현 테스트 (Orchestrator verdict receipt) | §9.3 | TestAgent verdict + Orchestrator |
| 보안 테스트 iteration (SecurityTestPL) | §9.4 (1차 + 2차 layer 모두) | SecurityTestPL (codeforge-review review-verdict-v2) |
| 보안 테스트 PASS | gate:security-test-pass 라벨 부착 → Phase 2 PR mergeable | SecurityTestPL (codeforge-review review-verdict-v2) |
| Clarification 재스폰 (RequirementsPL · ArchitectPLAgent) | §9.0 append | RequirementsPL / ArchitectPL (FIX 라벨 미추가 — fix-ledger-sync.yml은 §10만 trigger) |
| FIX 루프 | §10 append | **Orchestrator 단독** (CFP-32 fix-event-v1 monopoly, fix-ledger-sync.yml Action이 자동 mirror+label) |
| Story 완료 회고 (PMOAgent) | §11 회고 블록 | PMOAgent (codeforge-pmo direct Edit) |
| Phase 2 PR merged (최종) | Issue auto-close (PR body의 `Closes #N`) | (자동) |

---

## 섹션 읽기 규약

- **필요한 섹션만 읽기**: 프롬프트에 `§X, §Y 참조` 명시 → 에이전트가 `Read(docs/stories/<KEY>.md)` 후 해당 섹션만 참조
- 전체 file 읽기는 ArchitectAgent (chief author) 설계 진입 1회만 허용 (§1-6 전체 필요)
- **파일 변경은 lane plugin owner direct edit + Orchestrator 단독 (§10 FIX Ledger)** — codeforge-* CLAUDE.md self-write 표 + CFP-32 fix-event-v1 contract
