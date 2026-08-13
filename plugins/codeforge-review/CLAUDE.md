# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 본 repo의 정체

`codeforge-review` Claude Code plugin. 실행 코드 없음 — markdown(agents/templates) + shell hook.

**단독 동작 불가**: [`codeforge@mclayer`](https://github.com/mclayer/plugin-codeforge) core plugin (>= 0.17.0) 의존. core의 Orchestrator가 본 plugin의 PL agent에 review_packet 주입, `review_verdict v4` (canonical = 본 repo 루트 `docs/inter-plugin-contracts/review-verdict-v4.md` — 설치 캐시 기준 plugin 디렉터리 외부, 링크 비제공) contract로 결과 수령 (CFP-61). core 미설치 시 [overlay/hooks/session-start-deps-check.sh](overlay/hooks/session-start-deps-check.sh) fail-fast. core v0.16.0 (`1e75442`)에서 Phase 1 분리 — [docs/adr/ADR-001-extracted-from-codeforge.md](docs/adr/ADR-001-extracted-from-codeforge.md).

## Architecture — PL + Worker 패턴

```
Orchestrator(core)
  └─ RequirementsReviewPL | DesignReviewPL | CodeReviewPL | SecurityTestPL   ← lane 진입 시 1개 스폰
       ↓ review_packet 주입
       └─ ClaudeReviewAgent ∥ CodexReviewAgent          ← 한 메시지에 병렬 dispatch
```

- **4 PL agent** (`agents/{RequirementsReview,Design,Code,SecurityTest}ReviewPLAgent.md`) — 각 lane의 packet builder + verdict 종합. 워커 결과를 dedup → severity 종합 → `review_verdict_packet` 구성. **Synthesis only** — Story §9/GitHub comment/gate label/phase transition 은 Orchestrator 가 PL packet 받아 최종 write (CFP-61 / ADR-022). **Code/docs 직접 수정 금지**. (RequirementsReviewPL = CFP-2326 / ADR-125 신설 — 10번째 lane, 요구사항 외부사실 의존성 게이트.)
- **2 worker agent** (`agents/{Claude,Codex}ReviewAgent.md`) — lane-agnostic. PL이 packet으로 도메인(checklist · scope · category enum · severity override) 주입. **둘 다 필수 peer** — Claude/Codex 단독 fallback 허용 안 함. **신규 worker 신설 0** (ADR-001 lane-agnostic 재사용 — requirements-review lane 도 동일 2 worker).
- **공통 base** [templates/review-pl-base.md](templates/review-pl-base.md) — 4 PL이 공유하는 severity 종합·dedup·noise 분류·보고 형식·escalation·FIX Ledger·워커 의존성 SSOT. 각 PL md는 lane-specific 4가지(checklist packet · FIX 카운터 정책 · 검증 스코프 · 다음 게이트)만 본문에 명시.
- **4 lane checklist** (`templates/review-checklists/{requirements,design,code,security}.md`) — 각 lane의 항목·자동 P0 룰. PL이 packet의 `checklist_path`로 워커에 전달.

## Self-write 책임

★본 lane 의 정직한 write set = **repo 트리 내 code·docs 에 대해 공집합**★ — 4 PL 은 전부
**synthesis only** 이고 "**Code/docs 직접 수정 금지**"(위 Architecture 절 verbatim)라
repo 에 추적되는 파일을 직접 고치는 경로가 없다.
Story §9 / GitHub comment / gate label / phase transition 은 전부 **Orchestrator** 가 PL packet 을
받아 최종 write 한다 (CFP-61 / ADR-022).

| Path | 책임 agent |
|---|---|
| EMPTY-WRITE-SET(synthesis-only) | 없음 — repo 트리 내 code·docs 직접 write 공집합 |

> **위 공집합은 "어떤 파일도 write 하지 않는다" 가 아니다** — 본 lane `agents/` 의 6 agent md
> (4 PL + 2 worker) 는 **전부** `Edit/Write(.claude-work/doc-queue/**)` 제출 권한을 보유한다.
> 이 규약은 **각 agent frontmatter 선언 층에서 참**이다 (6/6 실측). 단 ★기계 집행은 아니다★:
> `invariant-check.yml` 의 doc-queue permission parity 검사(CFP-7)는 정의역이
> **wrapper 루트 `agents/*.md`** 인데(`:136`) wrapper 는 0 core 에이전트라 그 스텝은
> `exit 0` 으로 **skip** 한다 `[실측]` — plugin 하위 `agents/` 는 검사 대상이 아니다.
> ⇒ "required 게이트로 live 집행"이 아니라 ★**"선언은 참, 집행 채널 부재"**★ 가 정확하다.
> (wrapper 측 서술 = `docs/orchestrator-playbook.md` "두 축 분리".) 다만 그 제출 경로는
> `.gitignore:6` (`.claude-work/`) 로 무시되는 in-flight 큐(추적 파일 0)이지 repo 트리의
> code·docs 가 아니다. 또 위 표는 NG-8 겹침 검사가 읽는 **정의역**인데, doc-queue 는 agent
> frontmatter 권한 축에만 선언될 뿐 6 lane 표 어디에도 등재돼 있지 않아 겹침 비교 대상이 아니다.

본 lane 의 **1차 산출물**은 repo 파일이 아니라 in-memory `review_verdict v4` packet 이며,
그 packet 을 받아 실제로 write 하는 주체는 **Orchestrator** 다 — Story §9 섹션,
GitHub comment, gate label, phase transition 전부 Orchestrator 소관이다.
따라서 위 표의 공집합은 누락이 아니라 **정확한 사실**이다.

> **`EMPTY-WRITE-SET(synthesis-only)` 는 기계 판독 sentinel 이다** — NG-8
> (`scripts/lib/check_lane_overlap_predicate.py`) 의 lane write_set 겹침 검사가 이 토큰으로
> "정당 공집합(`declared_empty`)" 과 "표가 깨져 추출 0행(`extraction_empty`, RED)" 을 구별한다.
> ★토큰을 지우면 본 lane 이 RED 로 떨어진다★ (문면 장식이 아니라 load-bearing).
> 반대로 이 토큰을 두고 실 경로를 나열하면 `empty_sentinel_contradiction` RED 이고,
> **allowlist(`_DECLARED_EMPTY_ALLOWLIST`) 밖 lane 이 토큰을 달면 `sentinel_not_allowlisted` RED** 다.
> ★정직 천장★: 토큰 자체는 "무엇도 막지 못한다" — 막는 것은 코드측 allowlist 이며,
> 그 명단 확장은 **코드 diff(리뷰 표면)** 를 거친다. 정확한 주장은
> ★**"sentinel 토큰 축에서 자기선언만으로는 `declared_empty` 승격 불가"**★ 이며 그 범위를 넘지 않는다.
> ★표 행의 *내용*은 검사되지 않으므로★, lane 이 실 경로 행을 지우고 슬래시·별표를 포함한
> 임의 행 1개(`N/A` · `docs/` · **실재하는 무관 경로**까지)를 남기면 그 lane 의 write_set 은
> 1원소로 줄고 게이트는 `PASS` 한다 `[실측 확인]`. 즉 "자기 doc 편집만으로 유리한 판정을
> 얻을 수 없다"가 **아니라**, "sentinel 경로로는 승격할 수 없다" 까지가 보증 범위다.

Story §10 FIX Ledger append 는 **Orchestrator 단독** (CFP-32 monopoly).

## Drift-avoidance discipline (수정 시 반드시 지키세)

본 repo는 SSOT 분리를 명시적으로 강제. **공통 로직을 PL md에 다시 인라이닝하지 말 것** — 항상 base 템플릿 참조.

## Inter-plugin contract — review_verdict v4 (CFP-137 / ADR-044)

PL이 Orchestrator에 생성하는 typed schema packet. SSOT(canonical) = 본 repo 루트 `docs/inter-plugin-contracts/review-verdict-v4.md` (설치 캐시 기준 plugin 디렉터리 외부, 링크 비제공) — wrapper repo 측은 sibling reference (ADR-010 sync 의무). 본 plugin은 packet 구성만 책임 (최종 write는 Orchestrator). ADR-022 참조.

## Versioning 룰

`codeforge-review` 자체 version은 codeforge core version과 **독립**. v4 contract 호환되는 한 자유롭게 bump. Contract version 호환: `review_verdict_v4` min.

## Hook chain

- `SessionStart` → [overlay/hooks/session-start-deps-check.sh](overlay/hooks/session-start-deps-check.sh) → core 설치 verify → [overlay/hooks/regen-agents.sh](overlay/hooks/regen-agents.sh) 체인 실행
- `regen-agents.sh`는 core의 `overlay/hooks/merge.py`를 재사용해 `agents/*.md`를 `.claude/agents/`로 머지 출력.

## Worker 호출 규약 (편집 시 침해 금지)

- **Packet 누락 = 즉시 `ESCALATE_PACKET_INCOMPLETE` 반환**
- 워커는 서로 보고 미참조 — 독립 peer로 병렬 수행
- 워커는 **직접 다른 subagent 스폰 불가**
- **WebSearch/WebFetch는 `lane=security` + `lane=requirements-review` 전면 + `lane=design` 좁은 예외(외부 기술선택만)** 사용 가능. security/requirements-review = 외부사실 의존 결론 다출처 검증 (CFP-2326 / ADR-125, ADR-124 단계③ 게이트). `lane=design` = "외부 기술선택" 결론 한정 (positive-list 라이브러리·프로토콜·알고리즘·성능모델 ∩ negative-list ADR·boundary·계약·§8·섹션 배제 — CFP-2327 / ADR-124 Amd 1). 모두 외부사실 의존 지점에만 — 검사연극 차단 (ADR-119 §결정 6). **`lane=code` 는 전면 금지** (repo 내부 문서·코드만 근거 — design 좁은 예외와 비대칭 보존)
- `lane=security` PL은 워커 spawn 전 GitHub native 1차 layer fetch 의무

## Dogfood policy (CFP-45)

본 plugin repo 는 runtime SSOT 만 보유. dogfood artifacts (specs/plans/retros/stories/change-plans) 는 [`mclayer/codeforge-internal-docs`](https://github.com/mclayer/codeforge-internal-docs) 단일 monorepo SSOT. 본 plugin 폴더는 `codeforge-internal-docs/review/`. 상세 정책 + Story workflow 흐름은 wrapper [CLAUDE.md](https://github.com/mclayer/plugin-codeforge/blob/main/CLAUDE.md) canonical SSOT 참조 + [ADR-013](https://github.com/mclayer/plugin-codeforge/blob/main/docs/adr/ADR-013-codeforge-family-dogfood-out-policy.md) (PR-I 머지 후 Adopted).

Plugin repo 측 GitHub Issue 와 internal-docs 측 Story file 의 binding:
- Issue body frontmatter: `story_uri: <internal-docs URL>`
- Story file frontmatter: `story_issues: [{repo: "mclayer/plugin-codeforge", number: <N>}]`
- `.github/workflows/phase-gate-mergeable.yml` (본 repo) 가 cross-repo Story fetch via GitHub App
