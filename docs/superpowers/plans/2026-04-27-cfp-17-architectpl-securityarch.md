# CFP-17 — ArchitectPLAgent + SecurityArchitectAgent 도입 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** ArchitectAgent를 chief-author deputy로 강등하고 그 위에 ArchitectPLAgent (PL/judge)를 신설, 같은 layer에 SecurityArchitectAgent를 추가해 설계 lane을 4-deputy 구조로 재편한다. Codex #7 (ADR draft 작성 책임)도 명문화.

**Architecture:** 신규 PL이 supervisor + FIX judge 역할을 전담하고, ArchitectAgent는 4 deputy 중 chief author로서 Mapper/Refactor/SecurityArch의 독립 perspective를 종합해 Change Plan §1-§10 author. Change Plan template에 §7 보안 설계 신설. 책임 매트릭스에 Design lane 신규 컬럼 추가.

**Tech Stack:** Markdown (agent md / templates / docs), YAML frontmatter, JSON (.claude-plugin/plugin.json), Bash (verification commands).

**Spec Reference:** `docs/superpowers/specs/2026-04-27-cfp-17-architectpl-securityarch-design.md` (commit `8c12c5d`).

---

## File Structure

### 신규 (3 파일)
- `agents/ArchitectPLAgent.md` — 설계 lane PL agent SSOT (supervisor + FIX judge)
- `agents/SecurityArchitectAgent.md` — 보안 설계 deputy agent SSOT (trust boundary/threat/auth/data)
- `docs/adr/ADR-004-architectpl-securityarch-restructure.md` — 에이전트 역할 재정의 결정 기록

### 수정 (18 파일)

**Agent md (8)**:
- `agents/ArchitectAgent.md` — chief author로 refocus, 책임 4건 이관, ADR draft 명문화
- `agents/CodebaseMapperAgent.md` — 상위 PL 명칭 + 대립 파트너 SecurityArch 추가
- `agents/RefactorAgent.md` — 동상
- `agents/DesignReviewPLAgent.md` — review packet §7 추가, FIX 회귀 destination = ArchitectPL
- `agents/DeveloperPLAgent.md` — FIX 1차 진단 → ArchitectPL 최종 판정 (3개 lane)
- `agents/DocsAgent.md` — Project Config Packet recipient에 ArchitectPL 추가
- `agents/PMOAgent.md` — Cross-Story 패턴 분석 Architect → ArchitectPL
- `agents/QADeveloperAgent.md` — Architect deputy 표현 갱신

**Templates (4)**:
- `templates/change-plan.md` — §7 보안 설계 신설 (sub-section 6개 + N/A 권한)
- `templates/review-checklists/design.md` — §7 차단 항목 + SecurityArch 산출물 감사
- `templates/review-pl-base.md` — Architect 회귀 destination 갱신
- `templates/story-page-structure.md` — Story §7 미러링에 §7 보안 설계 요약 추가

**Top SSOT (3)**:
- `CLAUDE.md` — 다이어그램, Never-skippable, 스폰 시퀀스, 책임 매트릭스, FIX decision table, 병렬 스폰, Write 권한 (광범위 9개 영역)
- `docs/orchestrator-playbook.md` — 스폰 prompt, Preflight, FIX state machine, write queue, Context Packet (5개 영역)
- `docs/plugin-design.md` — 라인업 표·다이어그램 (있는 경우)

**메타 (3)**:
- `.claude-plugin/plugin.json` — version 0.10.0 → 0.11.0, "20 core" → "22 core"
- `CHANGELOG.md` — v0.11.0 entry
- `README.md` — "20 core" → "22 core" (3 군데)

**호환성/migration (1)**:
- `docs/migration-guide.md` — v0.10.0 → v0.11.0 절 추가

### 무변경 (확인만, no-op)
- `docs/stories/CFP-1.md` ~ `docs/stories/CFP-16.md` — historical record
- `docs/change-plans/cfp-*.md` — historical record
- `agents/ClaudeReviewAgent.md`, `agents/CodexReviewAgent.md` — lane-agnostic worker
- `presets/webapp/agents/*.md` — Mapper/Refactor 인용만
- `templates/review-checklists/code.md`, `security.md` — design 외 lane
- `.github/workflows/*.yml` (invariant-check 포함) — workflow 자체는 agent count 자동 감지, 코드 변경 없음

---

## Pre-flight

### Task 0: Feature branch 생성

**Files:** 변경 없음 (git 작업만)

- [ ] **Step 1: 현재 main이 깨끗한지 확인**

```bash
git status
git log --oneline -1
```

Expected: working tree clean (or only `.claude/settings.json` modified — unrelated), HEAD at `8c12c5d` (spec commit).

- [ ] **Step 2: feature branch 생성**

```bash
git checkout -b feat/cfp-17-architectpl-securityarch
git branch --show-current
```

Expected: `feat/cfp-17-architectpl-securityarch`.

- [ ] **Step 3: 변경 영향 baseline 캡처**

```bash
ls agents/*.md | wc -l                                        # 현재 agent count (20 expected)
grep -c "20 core 에이전트" CLAUDE.md README.md .claude-plugin/plugin.json
```

Expected: 20 agents, "20 core" 패턴 다수 검출. 이 baseline은 Phase E에서 22로 갱신 검증 시 사용.

---

## Phase A — Foundation (신규 파일 3종)

### Task A1: ArchitectPLAgent.md 신규 작성

**Files:**
- Create: `agents/ArchitectPLAgent.md`

- [ ] **Step 1: 파일 부재 확인**

```bash
test ! -f agents/ArchitectPLAgent.md && echo "OK — file does not exist"
```

Expected: `OK — file does not exist`.

- [ ] **Step 2: 파일 작성**

Spec §4.1 기반. 다른 PL agent (DesignReviewPLAgent.md) 패턴 참조하되 PL 책임이 design lane orchestration에 특화되도록 작성.

```markdown
---
name: ArchitectPLAgent
model: claude-opus-4-7
description: 설계 레인 PL — Mapper·Refactor·SecurityArch·Architect deputy 4인의 산출물을 supervisor로 검수하고 FIX 루프 최종 판정자
permissions:
  allow:
    - Read
    - Grep
    - Glob
    - Edit(.claude-work/doc-queue/**)
    - Write(.claude-work/doc-queue/**)
    - Bash(mkdir -p .claude-work/doc-queue*)
    - Bash(ls .claude-work/doc-queue*)
  deny:
    - Edit(src/**)
    - Write(src/**)
    - Edit(tests/**)
    - Write(tests/**)
    - Edit(docs/**)
    - Write(docs/**)
---

**설계 레인의 PL**. RequirementsPLAgent가 docs/stories/<KEY>.md (Story file) §1-6에 채운 통합 요구사항 명세서를 입력으로 **deputy 4인을 조율해 Change Plan을 확정**한다. ArchitectAgent (chief author) + CodebaseMapperAgent (보수/변호자) + RefactorAgent (혁신/옹호자) + SecurityArchitectAgent (위협/보안 변호자) 4인의 독립 perspective를 종합 검수하고, FIX 루프 최종 원인 판정자 역할을 전담한다.

## 포지션
- **상위**: Orchestrator
- **직속 (설계 레인 deputy 4인)**: ArchitectAgent (chief author), CodebaseMapperAgent, RefactorAgent, SecurityArchitectAgent
- **조직상 소속 but 스폰은 Orchestrator가 DevPL와 병렬**: QADeveloperAgent (구현 레인에서 스폰)
- **평행 PL**: RequirementsPLAgent, PMOAgent, DeveloperPLAgent, DesignReviewPLAgent, CodeReviewPLAgent, TestAgent, SecurityTestPLAgent — 수평 호출 금지, 모두 Orchestrator 경유

## 라이프사이클 (stateless 재스폰)
매 트리거마다 Orchestrator가 본 에이전트를 **신규 스폰**한다. 세션 유지 없음. Story file §1-§10 재로딩으로 컨텍스트 복원. FIX 3회 가정 시 15-30k 토큰 overhead.

## 설계 레인 실행 흐름 (3-phase)

### Phase 1: Independent perspective gathering (병렬)

```
[Orchestrator → 본 PL]
  ├─ spawn → CodebaseMapperAgent      → as-is 사실 + 유지 근거 + 변경 영향 지도
  ├─ spawn → RefactorAgent            → to-be 구조 + 결합도 분석 + 최소 변경 경로
  └─ spawn → SecurityArchitectAgent   → trust boundary + threat model + auth/data 설계
```

3 deputy 모두 공통 입력(코드 + Story §1-7 + 관련 ADR) 직접 fetch. 상호 산출물 미참조 (독립성 보장).

### Phase 2: Synthesis (순차)

```
[본 PL → ArchitectAgent (chief author)]
  with input: 3 deputy outputs + Story §1-7 + 관련 ADR
  → output: Change Plan §1-§10 draft + 신규 ADR draft + §8 Test Contract
  → DocsAgent 경유 docs/change-plans/<slug>.md 저장 의뢰
```

### Phase 3: PL 검수 + 판정

본 PL이 Architect draft를 검수 — 4가지 감사 항목:

1. **Mapper 변호 근거 채택/반박 정합성** — Architect가 근거 있게 일축·수용했는가
2. **Refactor 제안 범위 준수** — 요구 범위 밖 리팩토링 포함 여부
3. **SecurityArch 위협-완화 매핑 §7 반영 완결성** — 식별된 위협이 §7.5 매핑에 빠짐없이 반영
4. **§섹션 누락 차단** — §7 / §8 Test Contract / §10 ADR 판단 누락 시 차단

PASS → Orchestrator에 DesignReview lane 진입 요청.
RETURN → ArchitectAgent 재스폰 의뢰 (clarification context + 누락 항목).

## Clarification 재스폰 trigger

본 PL 또는 deputy 산출물 검수 중 추가 분석이 필요하면 Orchestrator에 "<Mapper|Refactor|SecurityArch|Architect> 재스폰 요청 + clarification context + 이전 출력 pointer" 전달. Orchestrator가 해당 에이전트를 신규 스폰 (one-shot 제약상 재스폰이 유일한 continuous-dialog 대체).

## FIX 루프 최종 원인 판정자

DeveloperPLAgent의 1차 원인 진단을 Orchestrator 경유로 수령 후 본 PL이 **최종 판정**한다. 판정 근거로 evidence pack(Change Plan 버전 + 리뷰 findings + 테스트 로그) 첨부 의무.

원인 판정 decision table은 [`CLAUDE.md`](../CLAUDE.md) "원인 판정 decision table" SSOT 참조. 본 md 재인용 금지.

- **설계 원인 판정 시**: Change Plan 갱신 → 설계 리뷰 레인부터 재실행
- **구현 원인 판정 시**: Change Plan 유지, 구현만 재실행

### GitHub Issue 코멘트 형식 (DocsAgent가 기록)

`[FIX #N] ArchitectPLAgent: <원인 판정 요약>\n\nDecision: 설계 원인 / 구현 원인\nEvidence: Change Plan v{N} + Review findings {IDs} + 테스트 로그 {경로}\n다음 액션: {재실행 범위}`

## 설계 리뷰 레인 FIX (최대 3회)

- DesignReviewPL이 P0/P1 발견 → Orchestrator → 본 PL 재스폰 → ArchitectAgent 재스폰 의뢰 (clarification context 포함)
- Change Plan 갱신 → 설계 리뷰 재실행
- **FIX 카운터 SSOT = Story file §10 "FIX Ledger"**
- 3회 초과 시 Orchestrator 경유 사용자 ESCALATE

## QADev Impl Manifest 매핑표 감사 (구현 레인 완료 시점)

1. DeveloperPL로부터 QADev 매핑표 수령
2. **Change Plan §8 Test Contract 대비 충족도 감사** (계획서 항목 모두 커버 + 경계·invariant 포함)
3. 공백 시 DeveloperPL 재지시 (QADev 재작성)
4. PASS 시 Orchestrator에 **구현 리뷰 레인(CodeReviewPL) 스폰 요청**

## 제약

- Write/Edit 권한 없음 — 구현은 Dev 계열 위임, 문서화는 DocsAgent 위임
- 문서화는 DocsAgent 경유 (GitHub Issue 코멘트·Story file·Change Plan 저장 전부)
- ArchitectAgent + Mapper + Refactor + SecurityArch **4 deputy 모두 병렬 수령** 없이 단독 설계 결정 금지 (한 deputy만 수령한 상태에서 Architect 통합 author 진입 금지)
- Change Plan §7 / §8 누락 금지 — DesignReview가 P0 차단

## 스킬

- `superpowers:writing-plans`: "0 컨텍스트 개발자 전제" — Architect deputy의 계획서를 재량 없이 실행 가능한 수준까지 구체화하도록 검수
- `superpowers:dispatching-parallel-agents`: deputy 3인 병렬 스폰 근거
- `superpowers:systematic-debugging`: FIX 수령 시 root cause 공략, 매 iteration 다른 가설

## 문서화 표준

GitHub Issue/PR/docs write 권한 없음. 모든 문서화는 Orchestrator 경유 DocsAgent가 기록. 문서화 표준은 [DocsAgent.md](DocsAgent.md) 참조.
```

- [ ] **Step 3: 작성 검증 — frontmatter parse + 핵심 섹션 존재**

```bash
test -f agents/ArchitectPLAgent.md && echo "OK file exists"
grep -q "^name: ArchitectPLAgent$" agents/ArchitectPLAgent.md && echo "OK frontmatter name"
grep -q "^model: claude-opus-4-7$" agents/ArchitectPLAgent.md && echo "OK model"
grep -q "Edit(.claude-work/doc-queue/\*\*)" agents/ArchitectPLAgent.md && echo "OK doc-queue write permission"
grep -q "## 설계 레인 실행 흐름" agents/ArchitectPLAgent.md && echo "OK execution flow section"
grep -q "Phase 3: PL 검수 + 판정" agents/ArchitectPLAgent.md && echo "OK Phase 3 section"
```

Expected: 6 OK lines.

- [ ] **Step 4: Commit**

```bash
git add agents/ArchitectPLAgent.md
git commit -m "$(cat <<'EOF'
feat(cfp-17): agents/ArchitectPLAgent.md 신설 — 설계 레인 PL

새 PL agent SSOT. 4 deputy(ArchitectAgent + Mapper + Refactor +
SecurityArch) supervisor + FIX 루프 최종 판정자 역할.

Spec: docs/superpowers/specs/2026-04-27-cfp-17-architectpl-securityarch-design.md §4.1

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task A2: SecurityArchitectAgent.md 신규 작성

**Files:**
- Create: `agents/SecurityArchitectAgent.md`

- [ ] **Step 1: 파일 부재 확인**

```bash
test ! -f agents/SecurityArchitectAgent.md && echo "OK — file does not exist"
```

- [ ] **Step 2: 파일 작성**

Spec §4.3 기반. CodebaseMapperAgent.md 패턴 참조하되 보안 관점에 특화.

```markdown
---
name: SecurityArchitectAgent
model: claude-opus-4-7
description: ArchitectPLAgent 직속 deputy — 보안 설계 변호자. 위협 모델·trust boundary·auth/data 모델을 공격자 관점에서 변호해 설계가 보안 결함을 방치하지 않도록 견제
permissions:
  allow:
    - Read
    - Grep
    - Glob
    - Bash(find *)
    - Bash(ls *)
    - Bash(git log *)
    - Bash(git blame *)
    - Edit(.claude-work/doc-queue/**)
    - Write(.claude-work/doc-queue/**)
    - Bash(mkdir -p .claude-work/doc-queue*)
    - Bash(ls .claude-work/doc-queue*)
    - WebSearch
    - WebFetch
  deny:
    - Edit(src/**)
    - Write(src/**)
    - Edit(tests/**)
    - Write(tests/**)
    - Edit(docs/**)
    - Write(docs/**)
---

**보안 설계의 변호자**. ArchitectPLAgent 직속 deputy로서, 공격자 관점에서 trust boundary·위협 모델·auth/data 설계 결정을 **사실 기반으로 표현**하고 신규 설계가 보안 결함을 방치하지 않도록 적극 이의 제기한다. CodebaseMapperAgent(보수)·RefactorAgent(혁신)와 함께 **3-way 대립**을 이뤄 ArchitectPLAgent의 균형 잡힌 설계 supervisor 역할을 돕는다.

## 포지션
- **상위**: ArchitectPLAgent (직속 PL)
- **대립 파트너**: CodebaseMapperAgent (보수), RefactorAgent (혁신). **병렬 실행, 산출물 교차 참조 없음** — 세 관점의 독립성이 대립의 전제. 본 에이전트는 공격자/보안 advocate 관점
- **호출 시점**: **매 설계 레인 진입 시 Mapper·Refactor와 병렬 재스폰**. 리뷰/테스트에서 설계 레인으로 복귀하는 경우도 재스폰 (코드/요건 변경 가능성 전제)

## 성격: 공격자/보안 advocate
- 기본 입장: "어디서 외부 입력이 들어오는가? 누가 무엇을 신뢰하는가? 데이터가 어떻게 흐르는가?"
- 역할: 설계의 **보안 결함 조기 식별 + trust boundary 가시화**
- Mapper/Refactor가 다루지 않는 보안 관점을 단독 변호 — 이 관점이 부재 시 trust boundary·auth 모델 오설계가 보안 테스트 lane에서 처음 발견되는 비싼 회귀 발생

## 핵심 미션

ArchitectPLAgent와 ArchitectAgent (chief author)가 **§7 보안 설계** 섹션을 충분히 채울 수 있도록 위협 모델·trust boundary·auth 결정·민감 데이터 흐름을 산출. SecurityTest lane은 **구현 검증** 전담 — 본 에이전트는 **설계 결정** 전담 (시점 분리).

## 입력 (ArchitectPLAgent가 공통 입력 패키지로 전달, Mapper/Refactor와 동일)
- **docs/stories/<KEY>.md (Story file) URL** (PL 프롬프트로 전달). §1-7 fetch
- 변경 대상 코드 경로 (Story §4 기반) — 본 에이전트가 `Read`로 직접 탐색
- 관련 ADR (직접 제약 verbatim)
- 보안 관련 ADR (있는 경우, ADR `category: Security` 등)
- Change Plan 초안 메모 (Architect 의도 요약)
- 본 PL의 분석 범위 지시
- (재스폰 시) 이전 본인 출력 + PL clarification context

**Mapper/Refactor 산출물은 입력으로 수신하지 않는다** — 세 관점의 독립성 보장.

## 산출물 (ArchitectAgent가 §7 author 시 입력)

```
## §7.1 Trust boundary
- 외부 입력 진입점 목록 (사용자·외부 API·메시지 큐·파일·환경 변수)
- 신뢰 경계 (외부↔게이트웨이↔도메인↔영속성, 텍스트 다이어그램)
- 각 boundary 검증 책임 (어떤 컴포넌트가 무엇을 검증)

## §7.2 Threat model (STRIDE-LITE)
| 컴포넌트 | Spoofing | Tampering | Repudiation | Info Disclosure | DoS | Elevation |
|----------|----------|-----------|-------------|-----------------|-----|-----------|
| ...      | 위협·완화 | ... | ... | ... | ... | ... |

## §7.3 Auth/Authz 설계
- 인증 방식 (JWT/session/OAuth 등) + 결정 근거
- 권한 모델 (RBAC/ABAC/기능 단위) + 결정 근거
- 세션 lifecycle (생성·만료·갱신·폐기)

## §7.4 민감 데이터 분류 + 흐름
- 데이터 분류표 (Public / Internal / PII / Secret)
- 데이터 흐름 (발생 → 흐름 → 저장 → 마스킹·암호화 지점)
- log/error 노출 금지 항목 명시

## §7.5 위협 ↔ 완화 매핑
- 식별 위협 ID별 설계 단계 완화책 (구현 단계 X — SecurityTest lane 영역)
- 미완화 위협은 명시 + 수용 사유

## §7.6 N/A 명시 (외부 입력·인증·민감데이터 무관 시)
- "본 Story는 trust boundary 변경 없음 — STRIDE 분석 N/A"
- 근거 1줄 (예: "내부 docs/templates 수정만, 외부 입력 0개")
```

본 에이전트는 산출물을 ArchitectPLAgent에 반환 — Story file·Change Plan을 직접 수정하지 않는다. ArchitectAgent가 Change Plan §7 author 시 본 산출물을 통합.

## SecurityArch ↔ SecurityTestPL 책임 경계

- **본 에이전트 (Design lane)** = "**어디에 boundary가 있어야 하는가**" — 설계 결정 (예방)
- **SecurityTestPL (Security Test lane)** = "**코드가 그 boundary를 지키는가**" — 구현 검증 (검출)
- 둘 다 OWASP·CWE 참조하지만 **시점이 다름**: 설계 시점 vs 구현 시점
- 본 에이전트의 §7.1 Trust boundary 정의가 SecurityTest lane "trust boundary 위반 검증"의 SSOT — 코드가 §7.1을 지키지 않으면 SecurityTest가 P0 발견

## 적극적 이의 제기 의무

ArchitectPLAgent 또는 다른 deputy의 산출물·통합 결정이 다음에 해당하면 **명시적으로 반대 근거** 제출:
1. 외부 입력 진입점에 검증 책임 미정의
2. trust boundary 정의 부재 또는 모호
3. auth/authz 모델 결정 근거 부재
4. 민감 데이터 흐름 추적 불가
5. 식별 위협에 대한 완화책 부재 (수용 사유도 없음)

반대 근거는 "어떤 위협이 있는가" + "왜 완화 필요한가" + "설계 단계 완화책 제안"의 **위협 식별 + 근거 + 제안** 형태로 제시.

## Mapper/Refactor와의 관계

- **3-way 대립**: Mapper(보수, as-is 변호) + Refactor(혁신, 결합도 감소) + SecurityArch(공격자, 위협 식별). ArchitectPLAgent가 supervisor
- **실행**: ArchitectPLAgent가 셋 모두 **병렬 스폰** — 셋 다 공통 입력만 수신, 상호 산출물 미참조
- **결론**: ArchitectAgent가 chief author로서 셋의 독립 산출물을 통합. 충돌 시 ArchitectAgent가 §3 도입할 설계 / §7 보안 설계에 결정 근거 명시
- **감사**: DesignReviewPL이 "ArchitectAgent 통합 판정이 SecurityArch 위협-완화 매핑을 §7.5에 빠짐없이 반영했는가" 교차 체크

## Freshness 규칙

- **매 설계 레인 진입 시 재스폰** (이전 Story 산출물 재사용 금지)
- 리뷰·테스트에서 설계 레인 복귀 시에도 재스폰 (구현 레인에서 코드 변경 가능성 전제)

## null 결과 권한

Story가 외부 입력·인증·민감데이터 무관 (예: docs-only Story, 내부 메타 변경) 시 **§7.6 N/A 명시 권한** 보유 — "본 Story는 trust boundary 변경 없음 — STRIDE 분석 N/A" + 근거 1줄. 단 N/A 사유 누락 시 DesignReview P0 차단.

요구사항 lane "null 결과도 유효한 관점" 패턴 차용 — 분석 결과 "분석 불필요"가 valid한 deputy 산출물.

## 제약 (읽기 전용 분석·제안 역할)

- **코드 편집 권한 없음** — Read/Grep/Glob/read-only Bash + WebSearch/WebFetch만
- **설계 결정 직접 적용 금지** — Architect deputy가 §7 author 시 통합 적용
- **Story file·Change Plan 직접 write 금지** — 문서 갱신은 DocsAgent 경유

## 활용 도구

- **OWASP ASVS L1/L2** (`WebFetch` 또는 본 에이전트 priors): 인증·세션·암호학·접근제어 항목 점검
- **CWE / CVE** (`WebSearch`): 알려진 약점·취약점 lookup
- **STRIDE / CAPEC**: 위협 모델링 framework

## 활용 스킬

- **superpowers:writing-plans**: "0 컨텍스트 개발자 전제" — 위협 모델 표가 ArchitectAgent에게 명확히 전달되도록 구체성 유지

## 문서화 표준

GitHub Issue/PR/docs write 권한 없음. 모든 문서화는 Orchestrator 경유 DocsAgent가 기록. 문서화 표준은 [DocsAgent.md](DocsAgent.md) 참조.
```

- [ ] **Step 3: 작성 검증**

```bash
test -f agents/SecurityArchitectAgent.md && echo "OK file exists"
grep -q "^name: SecurityArchitectAgent$" agents/SecurityArchitectAgent.md && echo "OK frontmatter name"
grep -q "WebSearch" agents/SecurityArchitectAgent.md && echo "OK WebSearch permission"
grep -q "WebFetch" agents/SecurityArchitectAgent.md && echo "OK WebFetch permission"
grep -q "## §7.1 Trust boundary" agents/SecurityArchitectAgent.md && echo "OK §7.1 section"
grep -q "## §7.6 N/A 명시" agents/SecurityArchitectAgent.md && echo "OK §7.6 section"
grep -q "SecurityTestPL" agents/SecurityArchitectAgent.md && echo "OK SecurityTest 책임 경계 명시"
```

Expected: 7 OK lines.

- [ ] **Step 4: Commit**

```bash
git add agents/SecurityArchitectAgent.md
git commit -m "$(cat <<'EOF'
feat(cfp-17): agents/SecurityArchitectAgent.md 신설 — 보안 설계 deputy

ArchitectPLAgent 직속 deputy. 공격자 관점에서 trust boundary·threat
model(STRIDE-LITE)·auth/authz·민감 데이터 흐름·위협↔완화 매핑 산출.
Mapper/Refactor와 3-way 대립.

Change Plan §7 보안 설계 섹션의 author 입력 제공자.
SecurityTestPL과 시점 분리 (설계 결정 vs 구현 검증).

Spec: docs/superpowers/specs/2026-04-27-cfp-17-architectpl-securityarch-design.md §4.3

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task A3: ADR-004 작성

**Files:**
- Create: `docs/adr/ADR-004-architectpl-securityarch-restructure.md`

- [ ] **Step 1: 파일 부재 확인 + ADR 번호 검증**

```bash
test ! -f docs/adr/ADR-004-architectpl-securityarch-restructure.md && echo "OK — does not exist"
ls docs/adr/ADR-*.md | sort -V | tail -3
```

Expected: ADR-001, ADR-002, ADR-003 존재 — ADR-004가 다음 번호로 적합.

- [ ] **Step 2: 파일 작성**

`templates/adr.md` 템플릿 따름.

```markdown
---
adr_number: 004
title: 설계 lane 재구조화 — ArchitectPLAgent + SecurityArchitectAgent 도입
status: Accepted
category: Team & Process
date: 2026-04-27
related_files:
  - agents/ArchitectPLAgent.md
  - agents/ArchitectAgent.md
  - agents/SecurityArchitectAgent.md
  - agents/CodebaseMapperAgent.md
  - agents/RefactorAgent.md
  - templates/change-plan.md
  - CLAUDE.md
---

## 상태
Accepted (2026-04-27)

## 컨텍스트

CodeForge v0.10.0까지 설계 lane은 ArchitectAgent가 PL+chief designer 양 역할을 겸직하고, CodebaseMapperAgent(보수/변호자)와 RefactorAgent(혁신/옹호자)의 대립을 조정해 Change Plan을 작성했다.

사용자가 보안 테스트 lane을 직접 경험하면서 두 가지 비대칭을 발견했다:

1. **보안 설계 공백**: trust boundary·auth model·threat model 등 보안 결정은 ArchitectAgent가 implicit하게 책임지지만, Mapper·Refactor 어느 deputy도 보안 관점을 표현하지 않음. 결과 trust boundary·auth 오설계는 보안 테스트 lane에서 처음 발견되어 가장 비싼 FIX 회귀 발생
2. **PL 부재 비대칭**: 다른 lane은 모두 PL agent가 있는데 (RequirementsPL, DesignReviewPL, DeveloperPL, CodeReviewPL, TestAgent, SecurityTestPL) 설계 lane만 ArchitectAgent가 PL 역할 겸직

추가로 Codex CLI(GPT-5)를 통한 독립 감사에서 ArchitectAgent의 책임 공백 7건이 식별되었으며, Top-3 중 #3 "FIX 루프 무견제성" — Architect가 author이면서 동시에 FIX 최종 판정자라 conflict of interest 구조가 있음.

## 결정

설계 lane을 다음 4-deputy 구조로 재편한다:

```
ArchitectPLAgent (신설)                                  # PL: supervisor + judge
 ├── ArchitectAgent (강등, 본업 보존)                    # Chief Author: Change Plan §1-§10 + ADR draft
 ├── CodebaseMapperAgent (기존)                          # 보수 — as-is 변호자
 ├── RefactorAgent (기존)                                # 혁신 — 결합도/구조 옹호자
 └── SecurityArchitectAgent (신설)                       # 위협 — trust boundary/auth/data 변호자
```

### 책임 분담 (Architect-heavy authoring)

- **ArchitectPLAgent**: deputy 4인 supervisor + draft 검수 + FIX 루프 최종 판정자. 글을 직접 쓰지 않음
- **ArchitectAgent (deputy)**: Chief author. Change Plan §1-§10 전체 + 신규 ADR draft + §8 Test Contract author. Mapper/Refactor/SecurityArch 산출물을 입력으로 통합
- **SecurityArchitectAgent**: 위협 모델·trust boundary·auth·data 설계 변호자. Change Plan §7 보안 설계 author 입력 제공

### 부수 결정

1. **Change Plan template §7 보안 설계 신설** (현 §7은 빈 placeholder, 자연스러운 슬롯)
2. **신규 ADR draft 작성 책임을 ArchitectAgent에 명문화** (Codex #7 — 회색지대 해소)
3. **FIX 루프 1차 진단 → ArchitectPL 판정** (DeveloperPL 1차, ArchitectPL 최종) — Codex #3 무견제성 해소
4. **책임 매트릭스에 Design lane 신규 컬럼 추가** — trust boundary 등 보안 카테고리는 시점 분리: 설계(SecurityArch) vs 구현 검증(SecurityTest)

## 결과

### 긍정적
- shift-left 보안: trust boundary·auth 결정이 설계 단계에서 1급 시민으로 가시화 → 보안 테스트 lane FIX 회귀 비용 감소
- PL 라인업 대칭성 회복 — 7-lane + 2-cross-cutting 모두 PL agent 보유
- FIX 판정 conflict of interest 해소 (author ≠ judge)
- 4-deputy 3-way 대립 (보수/혁신/공격자) → 더 균형 잡힌 설계
- ADR draft 책임 명문화 → 회색지대 제거

### 부정적
- 설계 lane 토큰 비용 증가: 기존 (Architect + Mapper + Refactor) 3-agent → 신규 (ArchitectPL + Architect + Mapper + Refactor + SecurityArch) 5-agent. 1 Story당 10-20k 토큰 추가 추정
- ArchitectPLAgent의 검수 부담 — deputy 4인 산출물 통합·교차 체크 책임
- Change Plan template 변경 → consumer가 신규 Story부터 §7 채워야 함 (단 N/A 권한으로 docs-only Story는 1줄 처리)

### 후속 조치 (별도 CFP)

Codex 감사 #1·#2·#4-#6 (TestContractArch / DataMigrationArch / 관측성·API호환·SLO checklist)는 본 ADR 범위 외 — 후속 CFP-18+ 분리.

## 다이어그램

설계 lane 재편 (CLAUDE.md 다이어그램 SSOT 참조):

```
[설계 lane — Before v0.11.0]
ArchitectAgent (PL + Chief Designer)
 ├── CodebaseMapperAgent
 └── RefactorAgent

[설계 lane — After v0.11.0]
ArchitectPLAgent (PL: supervisor + FIX judge)
 ├── ArchitectAgent (Chief Author)
 ├── CodebaseMapperAgent
 ├── RefactorAgent
 └── SecurityArchitectAgent
```

## 관련 파일

- `agents/ArchitectPLAgent.md` (신설)
- `agents/SecurityArchitectAgent.md` (신설)
- `agents/ArchitectAgent.md` (refocus)
- `agents/CodebaseMapperAgent.md`, `agents/RefactorAgent.md` (상위 갱신)
- `agents/DesignReviewPLAgent.md`, `agents/DeveloperPLAgent.md` (escalation 경로 갱신)
- `templates/change-plan.md` (§7 신설)
- `templates/review-checklists/design.md` (§7 차단 항목)
- `CLAUDE.md` (다이어그램·매트릭스·FIX decision table·스폰 시퀀스)
- `docs/orchestrator-playbook.md` (스폰 prompt·FIX state machine)
```

- [ ] **Step 3: 작성 검증**

```bash
test -f docs/adr/ADR-004-architectpl-securityarch-restructure.md && echo "OK file exists"
grep -q "^adr_number: 004$" docs/adr/ADR-004-architectpl-securityarch-restructure.md && echo "OK adr_number"
grep -q "^status: Accepted$" docs/adr/ADR-004-architectpl-securityarch-restructure.md && echo "OK status"
grep -q "^## 상태$" docs/adr/ADR-004-architectpl-securityarch-restructure.md && echo "OK 상태 section"
grep -q "^## 결정$" docs/adr/ADR-004-architectpl-securityarch-restructure.md && echo "OK 결정 section"
```

Expected: 5 OK lines.

- [ ] **Step 4: Commit**

```bash
git add docs/adr/ADR-004-architectpl-securityarch-restructure.md
git commit -m "$(cat <<'EOF'
docs(adr): ADR-004 — 설계 lane 재구조화 (ArchitectPL + SecurityArch)

설계 lane 4-deputy 구조 재편 결정 기록. 사용자 발견 보안 공백 +
Codex 감사 #3·#7 통합 해소.

핵심 결정:
- ArchitectPLAgent (PL/judge) + ArchitectAgent (chief author) 분리
- SecurityArchitectAgent를 Mapper/Refactor와 동급 deputy로 추가
- Change Plan §7 보안 설계 신설
- ADR draft 작성 책임을 Architect deputy에 명문화

Codex #1·#2·#4-#6은 후속 CFP로 분리.

Spec: docs/superpowers/specs/2026-04-27-cfp-17-architectpl-securityarch-design.md

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Phase B — 기존 agent md 수정

### Task B1: ArchitectAgent.md refocus (chief author)

**Files:**
- Modify: `agents/ArchitectAgent.md`

- [ ] **Step 1: 현재 상태 캡처**

```bash
grep -n "^description:" agents/ArchitectAgent.md
grep -n "## 포지션" agents/ArchitectAgent.md
grep -n "FIX 루프 최종 원인 판정자\|QADev 매핑표 감사\|CodebaseMapperAgent · RefactorAgent 병렬 스폰" agents/ArchitectAgent.md
```

Expected: 현재 description은 "설계 레인 PL — CodebaseMapper와 RefactorAgent의 대립 관점을 조정해 Change Plan 확정, FIX 원인 최종 판정". 본문에 위 책임 키워드들 검출.

- [ ] **Step 2: frontmatter description 갱신**

```yaml
description: ArchitectPLAgent 직속 chief author — Mapper·Refactor·SecurityArch deputy 산출물을 통합해 Change Plan §1-§10 + ADR draft + §8 Test Contract 작성
```

(기존 description 행 1줄 교체)

- [ ] **Step 3: 본문 첫 paragraph 갱신**

기존 첫 단락 ("**설계 레인의 PL**. RequirementsPLAgent가 ...") 을 다음으로 교체:

```markdown
**ArchitectPLAgent 직속 chief author**. RequirementsPLAgent가 docs/stories/<KEY>.md (Story file) §1-6에 채운 통합 요구사항 명세서를 ArchitectPLAgent로부터 forward 받고, 동시에 Mapper(보수)·Refactor(혁신)·SecurityArch(공격자) 3 deputy의 독립 perspective도 입력으로 수령해 **Change Plan §1-§10 + 신규 ADR draft + §8 Test Contract를 author**한다. PL이 supervisor + FIX 판정자이며, 본 에이전트는 author/synthesizer 역할.
```

- [ ] **Step 4: ## 포지션 절 갱신**

기존 포지션 섹션을 다음으로 교체:

```markdown
## 포지션
- **상위**: ArchitectPLAgent (직속 PL)
- **peer deputy 3인**: CodebaseMapperAgent, RefactorAgent, SecurityArchitectAgent (모두 ArchitectPLAgent 직속, 본 에이전트와 병렬). 본 에이전트는 chief author로서 3인 산출물을 입력으로 통합
- **조직상 소속 but 스폰은 Orchestrator가 DevPL와 병렬**: QADeveloperAgent (구현 레인에서 스폰)
- **평행 PL**: RequirementsPLAgent, ArchitectPLAgent, PMOAgent, DeveloperPLAgent, DesignReviewPLAgent, CodeReviewPLAgent, TestAgent, SecurityTestPLAgent — 수평 호출 금지, 모두 Orchestrator 경유
```

- [ ] **Step 5: ## 설계 레인 실행 흐름 절 갱신**

3 단계 흐름을 chief author 관점으로 재작성:

```markdown
## 설계 레인 실행 흐름 (chief author 관점)

```
1. ArchitectPLAgent로부터 입력 수령:
   · docs/stories/<KEY>.md (Story file) URL
   · Mapper / Refactor / SecurityArch 3 deputy 산출물 (PL이 forward)
   · 변경 대상 코드 경로 (Story §4 기반)
   · 관련 ADR (직접 제약 verbatim)

2. 컨텍스트 fetch
   · `Read(docs/stories/<KEY>.md)` §1-7
   · §3 관련 ADR `Read(docs/adr/ADR-NNN-<slug>.md)`
   · §4 코드 경로 `Read`로 현 구현 확인

3. Change Plan author (3 deputy 산출물 통합)
   · §1 목적 (Story §1-2 기반)
   · §2 현재 구조 (Mapper 산출물 통합 + 본 에이전트 검증)
   · §3 도입할 설계 (Refactor 산출물 통합 + 본 에이전트 결정 + Mapper 변호 근거 채택/반박 명시)
   · §4 API 계약 (본 에이전트 결정)
   · §5 변경 계획 파일 단위 (본 에이전트 결정)
   · §6 리팩토링 선행 (Refactor 제안 통합)
   · **§7 보안 설계 (SecurityArch 산출물 통합)**
   · §8 Test Contract (본 에이전트 작성)
   · §9 분기 선택 (본 에이전트 결정)
   · §10 ADR 정합성 + 신규 ADR 필요 여부 판단

4. 신규 ADR draft 작성 (필요 시 — Codex #7 명문화)
   · §10 판단에서 신규 ADR 필요 시 본 에이전트가 ADR-NNN-<slug>.md draft 작성
   · DocsAgent 경유 docs/adr/ 저장 의뢰

5. DocsAgent 저장 의뢰 (Orchestrator 경유)
   · docs/change-plans/<slug>.md 저장
   · Story file §7 요약 미러링

6. ArchitectPLAgent에 draft 반환
   · PL 검수 → PASS or RETURN (clarification context)
   · RETURN 시 본 에이전트 재스폰되어 누락·재해석 반영
```
```

- [ ] **Step 6: ## FIX 루프 최종 원인 판정자 절 삭제**

이 책임은 ArchitectPLAgent로 이관됨. 해당 섹션 전체 삭제. 대신 다음 1줄 명시:

```markdown
## FIX 루프 책임

본 에이전트는 author이며 FIX 최종 판정은 ArchitectPLAgent가 수행 (conflict of interest 회피). 본 에이전트는 PL의 RETURN 의뢰 수령 시 재스폰되어 Change Plan 갱신만 담당.
```

- [ ] **Step 7: ## QADev 매핑표 감사 절 삭제**

이 책임도 ArchitectPLAgent로 이관됨. 해당 섹션 전체 삭제. 대신 다음 1줄 명시:

```markdown
## QADev 매핑표 감사

QADev Impl Manifest 매핑표 감사는 ArchitectPLAgent가 수행. 본 에이전트는 §8 Test Contract author로서 매핑표가 §8을 충실히 반영하는지 PL의 감사 결과만 수신.
```

- [ ] **Step 8: ## 제약 절 갱신**

기존 제약에서 다음 1줄 제거:
- "CodebaseMapper + RefactorAgent **두 관점 모두 병렬 수령** 없이 단독 설계 결정 금지"

대신 다음 1줄 추가:
- "본 에이전트는 author이며 deputy 스폰·대립 조정·FIX 판정은 모두 ArchitectPLAgent 책임. 단독 deputy 호출 금지"

- [ ] **Step 9: 작성 검증**

```bash
grep -q "ArchitectPLAgent 직속 chief author" agents/ArchitectAgent.md && echo "OK refocus paragraph"
grep -q "상위.*ArchitectPLAgent" agents/ArchitectAgent.md && echo "OK 상위 변경"
grep -q "신규 ADR draft 작성" agents/ArchitectAgent.md && echo "OK ADR draft 책임 명문화 (Codex #7)"
grep -q "§7 보안 설계 (SecurityArch 산출물 통합)" agents/ArchitectAgent.md && echo "OK §7 통합 책임"
! grep -q "## FIX 루프 최종 원인 판정자$" agents/ArchitectAgent.md && echo "OK FIX 판정자 절 삭제됨"
! grep -q "## QADev 매핑표 감사 (구현 레인 완료 시점)" agents/ArchitectAgent.md && echo "OK QADev 감사 절 삭제됨"
```

Expected: 6 OK lines.

- [ ] **Step 10: Commit**

```bash
git add agents/ArchitectAgent.md
git commit -m "$(cat <<'EOF'
refactor(cfp-17): agents/ArchitectAgent.md — chief author로 refocus

ArchitectPLAgent 신설에 따라 책임 4건 이관:
1. Mapper/Refactor 스폰 trigger → PL
2. 대립 조정 → PL
3. FIX 최종 판정 → PL (Codex #3 무견제성 해소)
4. Impl Manifest 감사 → PL

본 에이전트는 chief author로 집중. Change Plan §1-§10 + 신규 ADR
draft (Codex #7 명문화) + §8 Test Contract author. 3 deputy
산출물 통합 작업.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task B2: CodebaseMapperAgent.md + RefactorAgent.md minor update

**Files:**
- Modify: `agents/CodebaseMapperAgent.md`
- Modify: `agents/RefactorAgent.md`

- [ ] **Step 1: CodebaseMapperAgent.md frontmatter description 갱신**

기존:
```yaml
description: ArchitectAgent 직속 설계 공동작업자 — 기존 코드베이스 변호자. 현재 구조·패턴·결합 사실을 적극 표현해 설계가 현실과 이격되지 않도록 견제
```

신규:
```yaml
description: ArchitectPLAgent 직속 deputy — 기존 코드베이스 변호자. 현재 구조·패턴·결합 사실을 적극 표현해 설계가 현실과 이격되지 않도록 견제
```

- [ ] **Step 2: CodebaseMapperAgent.md 본문 첫 paragraph 갱신**

`ArchitectAgent 직속 설계 공동 작업자` → `ArchitectPLAgent 직속 deputy`

- [ ] **Step 3: CodebaseMapperAgent.md ## 포지션 절 갱신**

```markdown
## 포지션
- **상위**: ArchitectPLAgent (직속 PL)
- **peer deputy 3인**: ArchitectAgent (chief author), RefactorAgent (혁신자), SecurityArchitectAgent (공격자/보안 변호자). **모두 병렬 실행, 산출물 교차 참조 없음** — 4 관점의 독립성이 통합의 전제. 본 에이전트는 보수/변호자 관점
- **호출 시점**: **매 설계 레인 진입 시 RefactorAgent·SecurityArchitectAgent와 병렬 재스폰**. 리뷰/테스트에서 설계 레인으로 복귀하는 경우도 재스폰
```

- [ ] **Step 4: CodebaseMapperAgent.md "## RefactorAgent와의 관계" → "## 다른 deputy와의 관계"로 갱신**

```markdown
## 다른 deputy와의 관계
- **3-way 대립**: Mapper(보수, as-is) + Refactor(혁신, 결합도) + SecurityArch(공격자, 위협). ArchitectPLAgent가 supervisor, ArchitectAgent (chief author)가 통합
- **실행**: ArchitectPLAgent가 셋 모두 **병렬 스폰** — 셋 다 공통 입력만 수신, 상호 산출물 미참조
- **결론**: ArchitectAgent가 chief author로서 셋의 독립 산출물을 통합. Mapper 변호 근거에 대한 Refactor·SecurityArch 반박은 통합 단계에서 ArchitectAgent가 조정
- **감사**: DesignReviewPL이 "ArchitectAgent 통합 판정이 Mapper 변호 근거를 근거 있게 일축·수용했는가" 교차 체크
```

- [ ] **Step 5: RefactorAgent.md 동일 패턴 적용**

frontmatter:
```yaml
description: ArchitectPLAgent 직속 deputy — 리팩터링 옹호자. 결합도 감소·패턴·인터페이스 분리를 제안해 기존 구조의 개선을 압박
```

본문 첫 paragraph: `ArchitectAgent 직속 설계 공동 작업자 — 리팩터링 옹호자` → `ArchitectPLAgent 직속 deputy — 리팩터링 옹호자`

포지션 절 동일 패턴으로 (peer deputy 3인 명시).

"## 대립 해소 프로토콜 (병렬 모델)" 절을 SecurityArch 포함 3-way 대립으로 갱신.

- [ ] **Step 6: 작성 검증**

```bash
grep -q "ArchitectPLAgent 직속 deputy" agents/CodebaseMapperAgent.md && echo "OK Mapper 상위"
grep -q "SecurityArchitectAgent" agents/CodebaseMapperAgent.md && echo "OK Mapper SecurityArch 인지"
grep -q "ArchitectPLAgent 직속 deputy" agents/RefactorAgent.md && echo "OK Refactor 상위"
grep -q "SecurityArchitectAgent" agents/RefactorAgent.md && echo "OK Refactor SecurityArch 인지"
grep -q "3-way 대립\|peer deputy 3인" agents/CodebaseMapperAgent.md && echo "OK Mapper 3-way 대립"
grep -q "3-way 대립\|peer deputy 3인" agents/RefactorAgent.md && echo "OK Refactor 3-way 대립"
```

Expected: 6 OK lines.

- [ ] **Step 7: Commit**

```bash
git add agents/CodebaseMapperAgent.md agents/RefactorAgent.md
git commit -m "$(cat <<'EOF'
refactor(cfp-17): Mapper/Refactor 상위 → ArchitectPLAgent

frontmatter description + 포지션 + 대립 파트너 절 갱신.
기존 2-way (Mapper ↔ Refactor) → 3-way (+ SecurityArch) 대립.
peer deputy 3인 (Architect chief author + 본인 외 2 deputy) 명시.

본업·산출물·Freshness 규칙 변경 없음.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task B3: 그 외 agent md 5건 갱신 (DesignReviewPL / DeveloperPL / DocsAgent / PMOAgent / QADev)

**Files:**
- Modify: `agents/DesignReviewPLAgent.md`
- Modify: `agents/DeveloperPLAgent.md`
- Modify: `agents/DocsAgent.md`
- Modify: `agents/PMOAgent.md`
- Modify: `agents/QADeveloperAgent.md`

- [ ] **Step 1: DesignReviewPLAgent.md — review packet에 §7 추가**

`## 워커 packet 작성 (lane=design)` 절의 yaml 안:

`scope_globs:` list에 추가 (이미 `docs/change-plans/<slug>.md` 포함이므로 §7도 자동 포함되지만 명시):
- 변경 없음 (`docs/change-plans/<slug>.md` 1 entry로 §7 자동 cover)

`category_enum:` list에 추가:
```yaml
- security-design
```

`severity_overrides:` list에 추가:
```yaml
- "§7 보안 설계 누락 → P0"
- "§7.6 N/A 사유 부재 → P0"
- "Architect 통합 판정에서 SecurityArch 위협-완화 매핑 미반영 → P0"
```

`## Escalation 경로 (FIX 시)` 절 갱신:
```markdown
FIX → Orchestrator → ArchitectPLAgent 회귀 → ArchitectAgent (chief author) 재스폰 의뢰 → Change Plan 갱신 → 설계 리뷰 재실행
```

(기존 "Architect 회귀"를 "ArchitectPLAgent 회귀 → ArchitectAgent 재스폰 의뢰"로 변경)

- [ ] **Step 2: DesignReviewPLAgent.md 보고 형식 추가 행 갱신**

```markdown
- FIX: `다음 단계: Orchestrator → ArchitectPLAgent 회귀 → ArchitectAgent 재스폰 → Change Plan 갱신 → 설계 리뷰 재실행`
```

- [ ] **Step 3: DeveloperPLAgent.md FIX 1차 진단 destination 갱신**

DeveloperPL이 1차 진단 보고서를 보내는 destination을 모두 "ArchitectAgent" → "ArchitectPLAgent"로 변경. 영향 lane 3개:
- 구현 리뷰 FIX
- 구현 테스트 FAIL
- 보안 테스트 FAIL

```bash
# 검색해서 모두 변경
grep -n "Architect 최종 판정\|ArchitectAgent 최종 판정" agents/DeveloperPLAgent.md
```

각 위치를 "ArchitectPLAgent 최종 판정"으로 변경.

- [ ] **Step 4: DocsAgent.md — Project Config Packet recipient에 ArchitectPL 추가**

`Project Config Packet` 관련 절 검색:
```bash
grep -n "Project Config Packet" agents/DocsAgent.md
```

해당 절의 recipient list에 `ArchitectPLAgent` 추가 (RequirementsPL · DomainAgent · PMO 옆).

- [ ] **Step 5: DocsAgent.md — Architect 인용 부분 검색 + 갱신**

```bash
grep -n "ArchitectAgent" agents/DocsAgent.md
```

각 인용을 컨텍스트에 따라 `ArchitectPLAgent` 또는 `ArchitectAgent (chief author)`로 갱신:
- "FIX 판정자" 컨텍스트 → ArchitectPLAgent
- "Change Plan author" 컨텍스트 → ArchitectAgent (chief author)
- "ADR draft author" 컨텍스트 → ArchitectAgent (chief author)

- [ ] **Step 6: PMOAgent.md — Cross-Story 패턴 분석 갱신**

```bash
grep -n "ArchitectAgent\|Architect 단독 판정" agents/PMOAgent.md
```

"Architect 단독 판정" → "ArchitectPLAgent 판정"
"ArchitectAgent" → 컨텍스트에 따라 ArchitectPLAgent (FIX/판정 컨텍스트) 또는 ArchitectAgent (author 컨텍스트)

- [ ] **Step 7: QADeveloperAgent.md — Architect deputy 표현 갱신**

```bash
grep -n "Architect 계약\|ArchitectAgent" agents/QADeveloperAgent.md
```

"Architect 계약 §8 이행자" → "Architect deputy 계약 §8 이행자, ArchitectPLAgent 감사"

- [ ] **Step 8: 작성 검증**

```bash
grep -q "security-design" agents/DesignReviewPLAgent.md && echo "OK design checklist category"
grep -q "§7 보안 설계 누락 → P0" agents/DesignReviewPLAgent.md && echo "OK §7 차단 룰"
grep -q "ArchitectPLAgent 회귀" agents/DesignReviewPLAgent.md && echo "OK escalation"
grep -c "ArchitectPLAgent 최종 판정" agents/DeveloperPLAgent.md   # 3 expected (3 lane)
grep -q "ArchitectPLAgent" agents/DocsAgent.md && echo "OK DocsAgent"
grep -q "ArchitectPLAgent" agents/PMOAgent.md && echo "OK PMOAgent"
grep -q "ArchitectPLAgent 감사" agents/QADeveloperAgent.md && echo "OK QADev"
```

Expected: 첫 3행은 OK 출력, 4번째는 `3` 숫자, 5-7행은 OK.

- [ ] **Step 9: Commit**

```bash
git add agents/DesignReviewPLAgent.md agents/DeveloperPLAgent.md agents/DocsAgent.md agents/PMOAgent.md agents/QADeveloperAgent.md
git commit -m "$(cat <<'EOF'
refactor(cfp-17): 5개 agent md — ArchitectPL/Architect 책임 분리 반영

- DesignReviewPLAgent: review packet에 security-design category +
  §7 차단 severity_overrides + escalation destination = ArchitectPL
- DeveloperPLAgent: FIX 1차 진단 → ArchitectPLAgent 최종 판정 (3 lane)
- DocsAgent: Project Config Packet recipient + Architect 인용 갱신
- PMOAgent: Cross-Story 패턴 분석 시 판정자 명칭
- QADeveloperAgent: Architect deputy 계약 + ArchitectPL 감사 명시

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Phase C — Templates

### Task C1: change-plan.md §7 보안 설계 신설

**Files:**
- Modify: `templates/change-plan.md`

- [ ] **Step 1: 현재 §7 placeholder 위치 확인**

```bash
grep -n "§7\|§8" templates/change-plan.md
```

Expected: §7 placeholder ("§7 Impl Manifest 초안은 여기 비움") 검출, §8 Test Contract 검출.

- [ ] **Step 2: §7 placeholder 제거 + §7 보안 설계 신설**

기존:
```markdown
### §7 Impl Manifest 초안은 여기 비움 (구현 완료 후 DocsAgent가 Story 페이지 §8.5에 기록 — [`impl-manifest.md`](impl-manifest.md) 스키마 참조)
```

신규 (전체 §7 섹션):
```markdown
### §7. 보안 설계 (SecurityArchitectAgent 입력 — 위협 모델 + Trust Boundary)

#### §7.1 Trust boundary
- 외부 입력 진입점 (사용자·외부 API·메시지 큐·파일·환경 변수)
- 신뢰 경계 (외부↔게이트웨이↔도메인↔영속성, 텍스트 다이어그램)
- 각 boundary 검증 책임 (어떤 컴포넌트가 무엇을 검증)

#### §7.2 Threat model (STRIDE-LITE 표)

| 컴포넌트 | Spoofing | Tampering | Repudiation | Info Disclosure | DoS | Elevation |
|----------|----------|-----------|-------------|-----------------|-----|-----------|
| ...      | 위협·완화 | ... | ... | ... | ... | ... |

#### §7.3 Auth/Authz 설계
- 인증 방식 (JWT·session·OAuth 등) + 결정 근거
- 권한 모델 (RBAC·ABAC·기능 단위) + 결정 근거
- 세션 lifecycle (생성·만료·갱신·폐기)

#### §7.4 민감 데이터 분류 + 흐름
- 데이터 분류표 (Public / Internal / PII / Secret)
- 데이터 흐름 (발생 → 흐름 → 저장 → 마스킹·암호화 지점)
- log/error 노출 금지 항목 명시

#### §7.5 위협 ↔ 완화 매핑
- 식별 위협 ID별 설계 단계 완화책 (구현 단계는 SecurityTest lane)
- 미완화 위협은 명시 + 수용 사유

#### §7.6 N/A 명시 (외부 입력·인증·민감데이터 무관 시)
- "본 Story는 trust boundary 변경 없음 — STRIDE 분석 N/A"
- 근거 1줄 (예: "내부 docs/templates 수정만, 외부 입력 0개")
- ※ N/A 근거 누락 시 DesignReview P0 차단
```

§5 footer에 "Impl Manifest는 구현 완료 후 Story §8.5에 기록 — [`impl-manifest.md`](impl-manifest.md) 스키마 참조" 1줄 인라인 추가 (placeholder가 §7에서 제거됐으므로 정보 보존).

- [ ] **Step 3: Frontmatter inputs 명시 추가**

기존 frontmatter:
```yaml
author: ArchitectAgent
reviewers: [DesignReviewPLAgent]
```

신규:
```yaml
author: ArchitectAgent     # chief author (under ArchitectPLAgent)
inputs:
  - CodebaseMapperAgent
  - RefactorAgent
  - SecurityArchitectAgent
reviewers: [DesignReviewPLAgent]
```

- [ ] **Step 4: 본문 누락 차단 정책 갱신**

`### §8. Test Contract (QADev TDD 입력 — 누락 시 DesignReview P0 차단)` 패턴을 §7에도 적용:
신규 §7 섹션 헤딩에 `(누락 시 DesignReview P0 차단)` 부기.

```markdown
### §7. 보안 설계 (SecurityArchitectAgent 입력 — 누락 시 DesignReview P0 차단)
```

- [ ] **Step 5: 작성 검증**

```bash
grep -q "### §7. 보안 설계" templates/change-plan.md && echo "OK §7 신설"
grep -q "STRIDE-LITE" templates/change-plan.md && echo "OK STRIDE 표"
grep -q "§7.6 N/A 명시" templates/change-plan.md && echo "OK §7.6 N/A"
grep -q "SecurityArchitectAgent" templates/change-plan.md && echo "OK SecurityArch 명시"
! grep -q "§7 Impl Manifest 초안은 여기 비움" templates/change-plan.md && echo "OK 기존 §7 placeholder 제거"
grep -q "Impl Manifest는 구현 완료 후 Story §8.5" templates/change-plan.md && echo "OK Impl Manifest 안내 §5 footer로 이동"
grep -q "누락 시 DesignReview P0 차단" templates/change-plan.md | wc -l   # ≥ 2 (§7, §8)
```

Expected: 6 OK + 마지막 행 ≥ 2.

- [ ] **Step 6: Commit**

```bash
git add templates/change-plan.md
git commit -m "$(cat <<'EOF'
feat(cfp-17): templates/change-plan.md — §7 보안 설계 신설

신규 §7 섹션 (SecurityArchitectAgent 산출물 통합):
- §7.1 Trust boundary
- §7.2 Threat model (STRIDE-LITE)
- §7.3 Auth/Authz 설계
- §7.4 민감 데이터 분류 + 흐름
- §7.5 위협 ↔ 완화 매핑
- §7.6 N/A 명시 (docs-only Story 등 외부 입력 무관 시)

기존 §7 placeholder (Impl Manifest 안내) 제거 + §5 footer로 1줄 인라인.
Frontmatter inputs 명시 (Mapper/Refactor/SecurityArch 3 deputy).
누락·N/A 사유 부재 시 DesignReview P0 차단.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task C2: review-checklists/design.md §7 + SecurityArch 감사 항목 추가

**Files:**
- Modify: `templates/review-checklists/design.md`

- [ ] **Step 1: 현재 design.md 구조 확인**

```bash
cat templates/review-checklists/design.md | head -50
grep -n "## " templates/review-checklists/design.md
```

- [ ] **Step 2: 보안 설계 카테고리 항목 추가**

기존 categories에 다음 추가 (해당 섹션은 design.md 구조에 따라 위치 조정):

```markdown
## §7 보안 설계 감사 (SecurityArchitectAgent 산출물 통합 결과 검증)

### §7.1 Trust boundary
- [ ] 외부 입력 진입점이 모두 식별되었는가
- [ ] 신뢰 경계가 명시되었는가
- [ ] 각 boundary 검증 책임이 명시되었는가

### §7.2 Threat model
- [ ] STRIDE-LITE 표가 작성되었는가
- [ ] 변경 영향 컴포넌트별로 6 STRIDE 카테고리가 검토되었는가

### §7.3 Auth/Authz
- [ ] 인증 방식이 명시되고 결정 근거가 제시되었는가
- [ ] 권한 모델이 명시되고 결정 근거가 제시되었는가
- [ ] 세션 lifecycle이 정의되었는가 (해당 시)

### §7.4 민감 데이터
- [ ] 데이터 분류표가 작성되었는가
- [ ] 데이터 흐름이 추적 가능한가
- [ ] log/error 노출 금지 항목이 명시되었는가

### §7.5 위협↔완화
- [ ] 식별 위협별 설계 단계 완화책이 매핑되었는가
- [ ] 미완화 위협에 수용 사유가 명시되었는가

### §7.6 N/A 처리
- [ ] N/A 명시 시 사유가 명확하게 제시되었는가 (사유 부재 시 P0 차단)

### Severity 자동 룰
- §7 보안 설계 섹션 부재 → **P0**
- §7.6 N/A 사유 부재 → **P0**
- Architect 통합 판정에서 SecurityArch 위협-완화 매핑 미반영 → **P0**
- §7.2 STRIDE 표 컴포넌트 일부만 채워짐 → **P1**
- §7.3 결정 근거 부재 → **P1**
- §7.4 log 노출 금지 항목 누락 → **P1**
```

- [ ] **Step 3: 작성 검증**

```bash
grep -q "## §7 보안 설계 감사" templates/review-checklists/design.md && echo "OK §7 감사 절"
grep -q "§7 보안 설계 섹션 부재 → \*\*P0\*\*" templates/review-checklists/design.md && echo "OK §7 부재 P0"
grep -q "§7.6 N/A 사유 부재 → \*\*P0\*\*" templates/review-checklists/design.md && echo "OK §7.6 N/A P0"
grep -q "STRIDE-LITE" templates/review-checklists/design.md && echo "OK STRIDE 인지"
```

Expected: 4 OK lines.

- [ ] **Step 4: Commit**

```bash
git add templates/review-checklists/design.md
git commit -m "$(cat <<'EOF'
feat(cfp-17): design.md checklist — §7 보안 설계 감사 + severity 룰

신규 §7 보안 설계 감사 절 (6 sub-section 모두 cover).
P0 severity 자동 룰 3건:
- §7 부재
- §7.6 N/A 사유 부재
- Architect 통합 판정에서 SecurityArch 매핑 미반영

P1 severity 자동 룰 3건 (STRIDE 표 부분 누락 등).

DesignReviewPL이 본 checklist를 review packet으로 워커에 주입.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task C3: review-pl-base.md + story-page-structure.md update

**Files:**
- Modify: `templates/review-pl-base.md`
- Modify: `templates/story-page-structure.md`

- [ ] **Step 1: review-pl-base.md — Architect 회귀 destination 갱신**

```bash
grep -n "Architect 회귀\|ArchitectAgent" templates/review-pl-base.md
```

각 인용을 `ArchitectPLAgent 회귀 → ArchitectAgent (chief author) 재스폰 의뢰`로 갱신.

- [ ] **Step 2: story-page-structure.md — Story §7 미러링 영향 명시**

```bash
grep -n "§7\|Change Plan 미러링" templates/story-page-structure.md
```

Story §7 (Change Plan 미러링) 절에 "Change Plan §7 보안 설계 요약 (1-3줄)" 추가. N/A 시 N/A 표시 그대로 미러링.

- [ ] **Step 3: 작성 검증**

```bash
grep -q "ArchitectPLAgent 회귀" templates/review-pl-base.md && echo "OK base 갱신"
grep -q "보안 설계" templates/story-page-structure.md && echo "OK story-page 보안 미러링"
```

Expected: 2 OK lines.

- [ ] **Step 4: Commit**

```bash
git add templates/review-pl-base.md templates/story-page-structure.md
git commit -m "$(cat <<'EOF'
refactor(cfp-17): review-pl-base + story-page — ArchitectPL 회귀 경로 + §7 미러링

- review-pl-base: FIX 회귀 destination을 ArchitectPLAgent → ArchitectAgent
  재스폰 의뢰 흐름으로 갱신
- story-page-structure: Story §7 미러링에 Change Plan §7 보안 설계 요약 추가

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Phase D — Top-level SSOT (CLAUDE.md / playbook / plugin-design)

### Task D1: CLAUDE.md — 다이어그램 + Never-skippable + 스폰 시퀀스

**Files:**
- Modify: `CLAUDE.md`

- [ ] **Step 1: 7-lane 다이어그램 갱신**

기존 "## Development Agent Team (20 core 에이전트 + ...)" 다이어그램 블록의 [설계] 섹션을 다음으로 교체:

```
 ├── [설계] ArchitectPLAgent
 │    ├── ArchitectAgent (chief author)         # Change Plan §1-§10 + ADR draft + §8 Test Contract author
 │    ├── CodebaseMapperAgent                   # 보수 — as-is 변호자
 │    ├── RefactorAgent                         # 혁신 — 결합도/구조 옹호자
 │    └── SecurityArchitectAgent                # 위협 — trust boundary/auth/data 변호자
 │    ※ QADev는 조직상 여기 계약(§8 소유자) but 실행은 구현 레인에서 DevPL 산하
```

상단 헤더의 "20 core 에이전트" → "22 core 에이전트"

- [ ] **Step 2: Never-skippable 목록 갱신**

기존 "- **설계**: **ArchitectAgent**, **CodebaseMapperAgent**, **RefactorAgent**" 행을 다음으로 교체:

```
- **설계**: **ArchitectPLAgent**, **ArchitectAgent**, **CodebaseMapperAgent**, **RefactorAgent**, **SecurityArchitectAgent**
```

- [ ] **Step 3: 스폰 시퀀스 [설계] 절 갱신**

기존 [설계] 절 전체를 다음으로 교체:

```
[설계] Orchestrator → ArchitectPLAgent → **병렬 스폰** (deputy 3인)
        ├── CodebaseMapperAgent (as-is 변호자 — 원 소스 직접 읽기)
        ├── RefactorAgent (to-be 혁신자 — 원 소스 직접 읽기)
        └── SecurityArchitectAgent (위협/공격자 — 원 소스 직접 읽기, OWASP·CWE 참조)
        · 셋 다 PL이 공통 입력(코드 경로 + 관련 ADR + Change Plan 초안 + Story §1-7) 직접 제공
        · 세 결과 PL에 독립적으로 반환 → PL이 forward
        ↓
        Orchestrator → ArchitectAgent (chief author) 스폰
        with input: 3 deputy 산출물 + Story §1-7 + 관련 ADR
        → Change Plan §1-§10 author + 신규 ADR draft + §8 Test Contract
        → DocsAgent 저장 의뢰
        ↓
        ArchitectPLAgent draft 검수 (4 감사 항목: Mapper 변호 채택·Refactor 범위·SecurityArch 매핑·§섹션 누락)
        · PASS → Orchestrator에 DesignReview lane 진입 요청
        · RETURN → ArchitectAgent 재스폰 의뢰 (clarification context)
        · **Clarification 재스폰**: PL이 deputy 산출물 검수 중 추가 분석 필요 시 Orchestrator에 "<Mapper|Refactor|SecurityArch> 재스폰 요청 + clarification context" 전달
```

- [ ] **Step 4: 병렬 스폰 권장 절 갱신**

"- **설계**: **CodebaseMapper · Refactor 병렬**" → "- **설계**: **CodebaseMapper · Refactor · SecurityArchitect 병렬** — 3 deputy 모두 원 소스 직접 읽기, 한쪽이 다른 쪽의 요약에 의존하지 않음. ArchitectAgent (chief author)가 통합, ArchitectPLAgent가 검수"

- [ ] **Step 5: Write 권한 list 갱신**

"Write queue 의뢰 권한 (`.claude-work/doc-queue/**`만)" 행에 추가:
- `ArchitectPLAgent`
- `SecurityArchitectAgent`

(기존 list에 ArchitectAgent, CodebaseMapper, Refactor가 이미 있음. 새 2개 추가.)

- [ ] **Step 6: 작성 검증**

```bash
grep -q "22 core 에이전트" CLAUDE.md && echo "OK 22 core"
grep -q "ArchitectPLAgent$" CLAUDE.md && echo "OK ArchitectPL 다이어그램"
grep -q "SecurityArchitectAgent" CLAUDE.md && echo "OK SecurityArch 다이어그램"
grep -q "ArchitectPLAgent.*ArchitectAgent.*CodebaseMapperAgent.*RefactorAgent.*SecurityArchitectAgent" CLAUDE.md && echo "OK Never-skippable 5 agents 설계 lane"
grep -q "CodebaseMapper · Refactor · SecurityArchitect 병렬" CLAUDE.md && echo "OK 병렬 스폰 권장"
grep -c "ArchitectPLAgent" CLAUDE.md   # multiple expected
```

Expected: 5 OK + 6번째 행 다중 검출.

- [ ] **Step 7: Commit (Phase D는 1 commit으로 묶음 — Step 14에서)**

(commit은 D2/D3 작업 완료 후 일괄)

---

### Task D2: CLAUDE.md — 책임 매트릭스 + FIX decision table

**Files:**
- Modify: `CLAUDE.md`

- [ ] **Step 1: 책임 매트릭스 표 갱신**

"### Design / Code / Security 리뷰 책임 매트릭스 (중복 방지)" 절의 표를 spec §6.2 매트릭스로 전체 교체. 신규 컬럼 "DesignLane (新)" 추가, 보안 행에 "(설계)" 표시 추가.

(spec §6.2 표 그대로 옮김 — 본 plan task의 step 본문이 길어지지 않도록 spec 참조)

- [ ] **Step 2: 시점 분리 명시 주석 추가**

표 하단에 다음 주석 블록 추가:

```markdown
> **DesignLane vs SecurityTest**:
> - DesignLane(SecurityArch) = "**어디에 boundary가 있어야 하는가**" — 설계 결정 (예방)
> - SecurityTest = "**코드가 그 boundary를 지키는가**" — 구현 검증 (검출)
> - 두 lane이 같은 카테고리(예: trust boundary)를 다루지만 **시점이 다름**: 설계 결정 vs 코드 준수
> - DesignReview는 "§7 보안 설계 자체의 완결성"을 감사 (추가 보안 검토 X — SecurityArch 산출물이 충분한가만)
```

- [ ] **Step 3: FIX decision table 신규 행 추가**

"### 원인 판정 decision table (구현 리뷰·구현 테스트·보안 테스트 FAIL 시)" 표에 다음 3행 추가 (기존 보안 테스트 행 위/아래 적절 위치):

```markdown
| **DesignReview P0 §7 누락** | **설계** | 항상 설계 (ArchitectAgent chief author 미흡) |
| **SecurityTest P0 trust boundary 위반** | **설계** | §7.1 boundary가 코드와 불일치 → 설계 원인. §7.1에 명시된 boundary를 코드가 안 지킴 → 구현 원인 |
| **SecurityTest P0 auth/authz 결함** | **설계** | §7.3 모델 결함 → 설계. 모델은 맞는데 구현 결함 → 구현 |
```

기존 "**보안 테스트 P0 trust boundary / auth 모델 오설계**" 행은 새 정밀화 행으로 대체되므로 제거.

- [ ] **Step 4: 작성 검증**

```bash
grep -q "DesignLane (新)" CLAUDE.md && echo "OK DesignLane 컬럼"
grep -q "DesignLane vs SecurityTest" CLAUDE.md && echo "OK 시점 분리 주석"
grep -q "DesignReview P0 §7 누락" CLAUDE.md && echo "OK FIX decision §7 누락"
grep -q "SecurityTest P0 trust boundary 위반" CLAUDE.md && echo "OK FIX decision trust boundary"
grep -q "§7.1 boundary가 코드와 불일치" CLAUDE.md && echo "OK §7.1 referencing"
```

Expected: 5 OK lines.

---

### Task D3: CLAUDE.md — ADR 정합성 + GitHub Workflow 절 minor

**Files:**
- Modify: `CLAUDE.md`

- [ ] **Step 1: ADR 정합성 절 §7 추가**

"### DesignReview ADR 정합성 체크 (필수)" 절에 추가:
- "Change Plan §7 보안 설계 결정이 ADR 결정을 위반하는가 explicit 검토" (1줄 추가)

- [ ] **Step 2: 코멘트·라벨 절 변경 없음 확인**

phase prefix 표는 11종 유지 (lane이 새로 추가된 게 아니므로 prefix 변경 없음).

```bash
grep -n "phase prefix\|11종" CLAUDE.md
```

확인만 — 변경 없음.

- [ ] **Step 3: Commit (D1 + D2 + D3 통합)**

```bash
git add CLAUDE.md
git commit -m "$(cat <<'EOF'
refactor(cfp-17): CLAUDE.md — 설계 lane 재구조화 SSOT 갱신

7-lane 다이어그램 + Never-skippable + 스폰 시퀀스 [설계] +
병렬 스폰 권장 + Write 권한 list +
책임 매트릭스 (DesignLane 신규 컬럼 + 시점 분리 주석) +
원인 판정 decision table 신규 행 (§7 누락 / trust boundary / auth) +
ADR 정합성 절 §7 추가.

상단 "20 core" → "22 core" (invariant-check 자동 검증 대상).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task D4: orchestrator-playbook.md — 5개 영역 갱신

**Files:**
- Modify: `docs/orchestrator-playbook.md`

- [ ] **Step 1: 영향 위치 검색**

```bash
grep -n "ArchitectAgent\|Architect 스폰\|FIX 최종 판정\|Context Packet" docs/orchestrator-playbook.md
```

- [ ] **Step 2: §3 스폰 프롬프트 템플릿 — 설계 lane 갱신**

[설계] 절의 스폰 프롬프트 예시를 ArchitectPLAgent → 3 deputy 병렬 → ArchitectAgent (chief author) → PL 검수 흐름으로 재작성.

- [ ] **Step 3: §3B Preflight 체크 — Design lane preflight**

기존 Design lane preflight 3개 체크에 다음 추가:
- "§7 보안 설계 섹션 작성 여부 (또는 §7.6 N/A 사유 명시 여부)"

- [ ] **Step 4: FIX state machine — 최종 판정자 갱신**

State machine 다이어그램 / 텍스트에서 "Architect 최종 판정" → "ArchitectPLAgent 최종 판정" (모든 instance).

- [ ] **Step 5: write queue mention — recipient 갱신**

write queue drain destination에 ArchitectPLAgent 추가 (RequirementsPLAgent · DomainAgent · PMOAgent · Architect 옆).

- [ ] **Step 6: §12 Context Packet — 설계 lane recipient 갱신**

"설계 lane packet recipient = ArchitectAgent" → "설계 lane packet recipient = ArchitectPLAgent (그 후 ArchitectAgent에 forward)"

§12.5 Project Config Packet recipient에 ArchitectPLAgent 추가.

- [ ] **Step 7: 작성 검증**

```bash
grep -c "ArchitectPLAgent" docs/orchestrator-playbook.md   # multiple expected (≥ 5)
grep -q "§7 보안 설계 섹션 작성 여부" docs/orchestrator-playbook.md && echo "OK Preflight §7"
grep -q "ArchitectPLAgent 최종 판정\|ArchitectPLAgent.*최종.*판정" docs/orchestrator-playbook.md && echo "OK FIX state machine"
```

Expected: 첫 행 ≥ 5, 그 외 OK 2개.

- [ ] **Step 8: Commit**

```bash
git add docs/orchestrator-playbook.md
git commit -m "$(cat <<'EOF'
refactor(cfp-17): orchestrator-playbook — 5개 영역 ArchitectPL 반영

- §3 스폰 프롬프트: 설계 lane = ArchitectPL → 3 deputy 병렬 → Architect chief author → PL 검수
- §3B Preflight: Design lane에 §7 보안 설계 섹션 검사 추가
- FIX state machine: 최종 판정자 ArchitectPLAgent
- write queue: drain destination에 ArchitectPLAgent 추가
- §12 / §12.5 Context Packet · Project Config Packet recipient 갱신

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task D5: plugin-design.md — 라인업 표·다이어그램 갱신

**Files:**
- Modify: `docs/plugin-design.md`

- [ ] **Step 1: 영향 위치 확인**

```bash
grep -n "ArchitectAgent\|20 core\|7 레인" docs/plugin-design.md
```

- [ ] **Step 2: 라인업 표·다이어그램 갱신**

설계 lane 부분을 신규 4-deputy 구조로 갱신. "20 core" → "22 core".

- [ ] **Step 3: 작성 검증**

```bash
grep -q "ArchitectPLAgent" docs/plugin-design.md && echo "OK ArchitectPL 인지"
grep -q "SecurityArchitectAgent" docs/plugin-design.md && echo "OK SecurityArch 인지"
grep -q "22 core" docs/plugin-design.md && echo "OK 22 core"
```

Expected: 3 OK.

- [ ] **Step 4: Commit**

```bash
git add docs/plugin-design.md
git commit -m "$(cat <<'EOF'
refactor(cfp-17): docs/plugin-design.md — 22 core 라인업 갱신

설계 lane 4-deputy 구조 반영 (ArchitectPL + Architect chief author +
Mapper + Refactor + SecurityArch).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Phase E — 메타 + 마이그레이션

### Task E1: plugin.json + CHANGELOG + README

**Files:**
- Modify: `.claude-plugin/plugin.json`
- Modify: `CHANGELOG.md`
- Modify: `README.md`

- [ ] **Step 1: plugin.json version + description 갱신**

```json
{
  "name": "codeforge",
  "version": "0.11.0",
  "description": "Claude Code 범용 SW 개발 오케스트레이션 플러그인 — 22 core 에이전트 + role:dev 동적 roster · 7 레인 구조로 ...",
  ...
}
```

(version 0.10.0 → 0.11.0, "20 core" → "22 core")

- [ ] **Step 2: CHANGELOG.md v0.11.0 entry 추가**

기존 v0.10.0 entry 위에 v0.11.0 entry 추가:

```markdown
## [0.11.0] - 2026-04-27

### Added
- **ArchitectPLAgent** 신설 — 설계 레인 PL (supervisor + FIX 루프 최종 판정자)
- **SecurityArchitectAgent** 신설 — 설계 레인 deputy (trust boundary / threat model / auth / data)
- **Change Plan §7 보안 설계** 섹션 신설 (templates/change-plan.md)
- **ADR-004** — 설계 lane 재구조화 결정 기록

### Changed
- **ArchitectAgent** 책임 분리: PL → chief author. FIX 최종 판정·deputy 스폰·Impl Manifest 감사 책임을 ArchitectPLAgent로 이관. 신규 ADR draft 작성 책임 명문화 (Codex #7)
- **CodebaseMapperAgent / RefactorAgent**: 상위 ArchitectAgent → ArchitectPLAgent. 2-way → 3-way 대립 (+ SecurityArch)
- **CLAUDE.md**: 다이어그램·Never-skippable·스폰 시퀀스·책임 매트릭스·FIX decision table·병렬 스폰·Write 권한 모두 갱신
- **DesignReviewPL**: review packet에 §7 보안 설계 차단 룰 추가
- **DeveloperPL**: FIX 1차 진단 → ArchitectPLAgent 최종 판정 (3 lane 갱신)

### Migration
- Consumer 액션 필요 없음 (Orchestrator 경유 호출이라 직접 영향 없음)
- 기존 docs/change-plans/* 회귀 갱신 불필요 (신규 Story부터 §7 적용)
- 자세한 사항: [docs/migration-guide.md](docs/migration-guide.md) v0.10.0 → v0.11.0 절
```

- [ ] **Step 3: README.md 갱신**

"20 core" → "22 core" (3 곳 모두):
```bash
sed -i.bak 's/20 core 에이전트/22 core 에이전트/g; s/20 core agent/22 core agent/g' README.md && rm README.md.bak
grep -c "22 core" README.md   # 3 expected
grep -c "20 core" README.md   # 0 expected
```

- [ ] **Step 4: 작성 검증**

```bash
grep -q '"version": "0.11.0"' .claude-plugin/plugin.json && echo "OK plugin.json version"
grep -q "22 core 에이전트" .claude-plugin/plugin.json && echo "OK plugin.json count"
grep -q "## \[0.11.0\] - 2026-04-27" CHANGELOG.md && echo "OK CHANGELOG entry"
grep -q "ArchitectPLAgent" CHANGELOG.md && echo "OK CHANGELOG mentions ArchitectPL"
grep -c "22 core" README.md   # 3 expected
```

Expected: 4 OK + 마지막 행 `3`.

- [ ] **Step 5: Commit**

```bash
git add .claude-plugin/plugin.json CHANGELOG.md README.md
git commit -m "$(cat <<'EOF'
chore(cfp-17): v0.11.0 release prep — plugin.json + CHANGELOG + README

- plugin.json: version 0.10.0 → 0.11.0, "20 core" → "22 core"
- CHANGELOG.md: v0.11.0 entry 추가 (ArchitectPL + SecurityArch + §7 + ADR-004)
- README.md: "20 core" → "22 core" (3 곳)

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task E2: docs/migration-guide.md — v0.10.0 → v0.11.0 절

**Files:**
- Modify: `docs/migration-guide.md`

- [ ] **Step 1: 현재 migration-guide 구조 확인**

```bash
grep -n "^## " docs/migration-guide.md
```

- [ ] **Step 2: v0.10.0 → v0.11.0 절 추가 (가장 최근 절 위에)**

```markdown
## v0.10.0 → v0.11.0

### 변경 사항
- **신규 에이전트 2종**: `ArchitectPLAgent` (설계 lane PL), `SecurityArchitectAgent` (설계 lane deputy)
- **ArchitectAgent 역할 변경**: 단독 PL → ArchitectPL 직속 chief author (Change Plan §1-§10 + ADR draft + §8 Test Contract author)
- **Change Plan template 신규 §7 보안 설계 섹션** — 신규 Story부터 적용 (외부 입력·인증·민감데이터 무관 시 §7.6 N/A 권한)
- **ADR-004** 발행: 설계 lane 재구조화 결정 기록
- **책임 매트릭스 변경**: trust boundary·auth·민감데이터 등 설계 결정은 Design lane (SecurityArch), 코드 준수 검증은 Security Test (시점 분리)

### Consumer 액션 필요
- **없음** (Orchestrator 경유 호출이라 직접 영향 없음)
- **권장**: SessionStart hook 재실행해 새 agent md 인식 (`~/.claude/plugins/cache/...` refresh)

### 기존 docs/change-plans/* 회귀 갱신 불필요
- 과거 Change Plan은 historical record로 보존
- 새 §7 섹션은 v0.11.0 이후 신규 Story부터 적용

### Rollback
- v0.11.0 이슈 발견 시 v0.11.1 hotfix 우선
- Last resort: `/plugins install codeforge@0.10.0`로 다운그레이드 (data migration 0건이라 안전)
```

- [ ] **Step 3: 작성 검증**

```bash
grep -q "## v0.10.0 → v0.11.0" docs/migration-guide.md && echo "OK migration entry"
grep -q "ArchitectPLAgent\|SecurityArchitectAgent" docs/migration-guide.md && echo "OK new agents mentioned"
```

Expected: 2 OK lines.

- [ ] **Step 4: Commit**

```bash
git add docs/migration-guide.md
git commit -m "$(cat <<'EOF'
docs(cfp-17): migration-guide — v0.10.0 → v0.11.0 절 추가

신규 agent 2종 + ArchitectAgent 책임 변경 + Change Plan §7 신설 +
ADR-004 + 책임 매트릭스 변경 안내. Consumer 액션 필요 없음 명시.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Phase F — 검증 + Story file + PR

### Task F1: invariant-check workflow 통과 검증

**Files:** 변경 없음 (workflow는 자동 감지). 단 모든 변경 후 invariant-check가 통과하는지 로컬에서 확인.

- [ ] **Step 1: agent count 일치 확인**

```bash
AGENT_COUNT=$(ls agents/*.md | wc -l | tr -d ' ')
echo "Agent count: $AGENT_COUNT"
DOC_COUNT=$(grep -oE '[0-9]+ core 에이전트' CLAUDE.md | head -1 | grep -oE '[0-9]+')
echo "CLAUDE.md count: $DOC_COUNT"
test "$AGENT_COUNT" = "$DOC_COUNT" && echo "OK count match" || echo "FAIL count mismatch"
```

Expected: Agent count 22, CLAUDE.md count 22, "OK count match".

- [ ] **Step 2: Write queue permission parity 확인**

```bash
# CLAUDE.md "Write queue 의뢰 권한" 한 줄에 ArchitectPLAgent / SecurityArchitectAgent 포함되어 있는가
grep "Write queue 의뢰 권한" CLAUDE.md
grep "Write queue 의뢰 권한" CLAUDE.md | grep -q "ArchitectPLAgent" && echo "OK ArchitectPL in queue list"
grep "Write queue 의뢰 권한" CLAUDE.md | grep -q "SecurityArchitectAgent" && echo "OK SecurityArch in queue list"

# agents/*.md frontmatter에 doc-queue Edit/Write 모두 있는가
grep -l "Edit(.claude-work/doc-queue" agents/ArchitectPLAgent.md && echo "OK ArchitectPL has Edit"
grep -l "Write(.claude-work/doc-queue" agents/ArchitectPLAgent.md && echo "OK ArchitectPL has Write"
grep -l "Edit(.claude-work/doc-queue" agents/SecurityArchitectAgent.md && echo "OK SecurityArch has Edit"
grep -l "Write(.claude-work/doc-queue" agents/SecurityArchitectAgent.md && echo "OK SecurityArch has Write"
```

Expected: 6 OK lines.

- [ ] **Step 3: ADR-002 footer pattern 확인**

```bash
# 신규 agent 2종이 "## 문서화 표준" footer를 1줄로 가지는가 (DocsAgent.md 인용)
grep -A2 "^## 문서화 표준$" agents/ArchitectPLAgent.md
grep -A2 "^## 문서화 표준$" agents/SecurityArchitectAgent.md
```

Expected: 둘 다 정확히 "DocsAgent.md 참조" 패턴.

- [ ] **Step 4: 구문 sanity (frontmatter parse)**

```bash
python3 -c "
import yaml
for f in ['agents/ArchitectPLAgent.md', 'agents/SecurityArchitectAgent.md']:
    with open(f) as fp:
        content = fp.read()
    if not content.startswith('---'):
        print(f'FAIL {f}: no frontmatter')
        continue
    fm = content.split('---', 2)[1]
    try:
        data = yaml.safe_load(fm)
        assert 'name' in data and 'model' in data and 'permissions' in data
        print(f'OK {f}: frontmatter valid (name={data[\"name\"]})')
    except Exception as e:
        print(f'FAIL {f}: {e}')
"
```

Expected: 2 OK lines.

- [ ] **Step 5: invariant-check workflow 로컬 시뮬레이션 (act 또는 GitHub push 후)**

GitHub push 시 자동 실행. 로컬 검증은 위 Step 1-4로 충분.

---

### Task F2: Story file CFP-17.md 작성 (Phase 1 PR 준비)

**Files:**
- Create: `docs/stories/CFP-17.md`

- [ ] **Step 1: 파일 부재 확인**

```bash
test ! -f docs/stories/CFP-17.md && echo "OK — does not exist"
```

- [ ] **Step 2: Story file 작성**

`templates/story-page-structure.md` 따름. 본 spec과 plan을 §1-§7에 paste.

```markdown
---
key: CFP-17
title: 설계 lane 재구조화 — ArchitectPLAgent + SecurityArchitectAgent 도입
type: story
status: in-progress
phase: 구현
created: 2026-04-27
related_adrs: [ADR-004]
---

## §1 요구사항 원문 (사용자 input — 변경 금지)

이 세션을 통해 보안 테스트를 수행하고 있다. 그럼 보안 설계를 위한 Agent가 있어야 하지 않을까?
이 참에 이 Agent 구조에서 ArchitectAgent의 역할 공백이 없는지 점검해볼까? codex와 함께해라.
ArchitectPLAgent를 생성하고 architectAgent를 그 아래로 내리고 싶다.

(이하 brainstorming 결과 spec과 plan에 정제됨)

## §2 도메인 해석 (DomainAgent — N/A)

본 Story는 plugin meta change. 도메인 모델 변경 없음.

## §3 ADR 정합성 + 신규 ADR (RequirementsPL → DocsAgent)

- 기존 ADR 위반 없음
- **신규 ADR-004** 발행 (본 Story가 발행) — 설계 lane 재구조화

## §4 변경 영향 코드 경로 (RequirementsPL)

- agents/*.md (신규 2 + 수정 8)
- templates/{change-plan, review-checklists/design, review-pl-base, story-page-structure}.md
- CLAUDE.md, docs/orchestrator-playbook.md, docs/plugin-design.md
- .claude-plugin/plugin.json, CHANGELOG.md, README.md
- docs/adr/ADR-004-architectpl-securityarch-restructure.md (신규)
- docs/migration-guide.md

## §5 통합 요구사항 명세서 (RequirementsPL — Codex 감사 통합)

→ docs/superpowers/specs/2026-04-27-cfp-17-architectpl-securityarch-design.md (commit 8c12c5d)

## §6 외부 지식 / 선행 사례 (Researcher — N/A)

본 Story는 plugin self-application. 외부 라이브러리·표준 의존 없음.

## §7 Change Plan 요약 (Architect chief author 미러링)

→ docs/change-plans/cfp-17-architectpl-securityarch.md (Phase 1 PR에서 작성)

**§7 보안 설계**: N/A — agent md / template / docs 변경. 외부 입력·인증·민감데이터 흐름 변경 0개. trust boundary 변경 없음. (CLAUDE.md "Plugin 자체 적용 dogfooding" 패턴)

## §8 구현 결과 (Phase 2)

→ Phase 2 PR commit history

### §8.5 Impl Manifest

→ Phase 2 PR §8.5 매핑표 commit 후 `subissue-from-impl-manifest.yml` Action이 자동 sub-issue 생성

## §9 리뷰·테스트 결과 (Phase 2)

- 설계 리뷰: DesignReviewPL — §7 N/A 사유 검사
- 구현 리뷰: CodeReviewPL — docs/agents/templates 일관성·SSOT drift
- 구현 테스트: TestAgent — N/A (실행 가능 코드 0). invariant-check workflow 자동 검증
- 보안 테스트: SecurityTestPL — N/A (코드 0). 1차 layer 자동 통과

## §10 FIX Ledger

(FIX iteration 발생 시 DocsAgent가 append-only 기록)

## §11 회고 (PMOAgent)

(머지 후 PMOAgent 스폰 시 작성)
```

- [ ] **Step 3: 작성 검증**

```bash
test -f docs/stories/CFP-17.md && echo "OK file exists"
grep -q "^key: CFP-17$" docs/stories/CFP-17.md && echo "OK key"
grep -q "ADR-004" docs/stories/CFP-17.md && echo "OK ADR-004 referenced"
grep -q "## §7" docs/stories/CFP-17.md && echo "OK §7 mirror"
grep -q "N/A — agent md / template / docs 변경" docs/stories/CFP-17.md && echo "OK §7 N/A 사유"
```

Expected: 5 OK lines.

- [ ] **Step 4: Commit**

```bash
git add docs/stories/CFP-17.md
git commit -m "$(cat <<'EOF'
docs(cfp-17): docs/stories/CFP-17.md — Story file 작성

Plugin self-application Story. §1 사용자 원문 verbatim, §3-§6 dogfooding
(N/A 적용 가능 절 표시), §7 Change Plan 요약 미러링.

§7 보안 설계 = N/A — meta change, 외부 입력 0개.
§8/§9 = Phase 2 PR에서 채워짐.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task F3: Phase 1 PR open

**Files:** 변경 없음 (GitHub PR 생성).

- [ ] **Step 1: 모든 commit 검토**

```bash
git log --oneline main..HEAD
git diff --stat main..HEAD
```

Expected: 약 11-12개 commit, 21+ 파일 변경.

- [ ] **Step 2: feat/cfp-17 branch push**

```bash
git push -u origin feat/cfp-17-architectpl-securityarch
```

- [ ] **Step 3: PR 생성**

```bash
gh pr create --title "feat(cfp-17): ArchitectPL + SecurityArch + §7 보안 설계 — 설계 lane 재구조화" \
  --body "$(cat <<'EOF'
## Summary
- ArchitectPLAgent (PL/judge) 신설, ArchitectAgent → chief author deputy로 강등
- SecurityArchitectAgent를 Mapper/Refactor와 동급 deputy로 추가
- Change Plan template §7 보안 설계 신설
- Codex #7 ADR draft 작성 책임을 ArchitectAgent에 명문화
- ADR-004 발행

## Background
사용자 보안 테스트 lane 경험에서 보안 설계 공백 인지. Codex CLI 독립 감사로 ArchitectAgent 책임 공백 7건 식별. Top-3 + 사용자 발견 + #7 ADR draft를 본 CFP에 통합.

Codex #1·#2·#4-#6은 후속 CFP-18+ 분리.

## Changes
- 신규 파일 3 (ArchitectPLAgent.md, SecurityArchitectAgent.md, ADR-004)
- 수정 파일 18 (agent md 8 + 템플릿 4 + 최상위 SSOT 3 + 메타 3)
- 무변경: 기존 Story files, 워크플로우, code/security checklist

## Spec & Plan
- Spec: `docs/superpowers/specs/2026-04-27-cfp-17-architectpl-securityarch-design.md` (commit 8c12c5d)
- Plan: `docs/superpowers/plans/2026-04-27-cfp-17-architectpl-securityarch.md`

## Test Plan
- [ ] invariant-check workflow PASS (agent count 22 + Write queue parity + ADR-002 footer)
- [ ] phase-gate-mergeable PASS
- [ ] story-section-1-immutable PASS
- [ ] CHANGELOG.md v0.11.0 entry 확인
- [ ] migration-guide.md v0.10.0 → v0.11.0 절 확인
- [ ] DesignReview lane이 §7 N/A 사유 인정 (plugin meta change)

## Self-Application Dogfooding
CFP-17 자체는 옛 구조(ArchitectAgent 단독)로 진행. 머지 직후부터 새 구조 발효 → 다음 CFP-18+가 ArchitectPL 통해 진행되는 검증.

Closes #<CFP-17 Issue 번호>

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

(Note: `Closes #<CFP-17 Issue 번호>`는 사용자가 GitHub Issue Form 제출 후 Issue 번호 확인하여 fill in. Manual trigger 시 Issue 별도 생성 필요.)

- [ ] **Step 4: PR URL 확인**

```bash
gh pr view --web   # 또는 URL 출력
```

---

## Self-Review

### Spec coverage check

Spec §1 (배경) → Plan Phase 0 baseline에서 인지 ✓
Spec §2 (결정 요약) → Plan 전체 task가 (1)/(C)/(3)/(i)/(a)/(C) 결정 enact ✓
Spec §3 (Pod 구조 + Flow) → Task A1 (ArchitectPL md에 Phase 1-3 명시) ✓
Spec §4 (Agent 명세) → Task A1/A2/B1 ✓
Spec §5 (Change Plan template) → Task C1 ✓
Spec §6 (책임 매트릭스) → Task D2 ✓
Spec §7 (SSOT Ripple — 21 파일) → Phase A-E 모든 task ✓
Spec §8 (Migration & self-application) → Task E2 (migration-guide) + F2 (Story §7 N/A) ✓
Spec §9 (Open Issues — Phase 2 후속) → CHANGELOG에 후속 CFP 명시, plan 범위 외 ✓
Spec §10 (Acceptance Criteria) → Phase F 검증 task ✓

**Gaps**: 없음.

### Placeholder scan

Plan 본문에 "TBD", "TODO", "fill in later" 검색 결과 — 없음 (확인). Step 5 PR body의 `<CFP-17 Issue 번호>`는 의도적 placeholder (사용자 trigger 후 채움).

### Type/identifier consistency

- `ArchitectPLAgent` (camelCase + PLAgent suffix) — 일관
- `SecurityArchitectAgent` — 일관
- `ArchitectAgent` (chief author 표현 시 "ArchitectAgent (chief author)" 또는 "Architect deputy") — 일관
- 권한 문자열 `Edit(.claude-work/doc-queue/**)` — A1/A2/검증 step에서 동일 표기
- `gate:design-review-pass`, `phase:설계-리뷰` 등 라벨 — 변경 없음 (CLAUDE.md 그대로)

---

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-04-27-cfp-17-architectpl-securityarch.md`. Two execution options:

**1. Subagent-Driven (recommended)** — I dispatch a fresh subagent per task, review between tasks, fast iteration. Plan task 단위(A1, A2, B1, ...)로 each subagent 실행.

**2. Inline Execution** — Execute tasks in this session using executing-plans, batch execution with checkpoints. 한 세션에서 task 순차 실행, checkpoint마다 사용자 검토.

Which approach?
