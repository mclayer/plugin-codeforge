# CLAUDE.md

## 언어 정책
모든 응답·주석·문서는 **한글 주 언어**. 영어는 기술 용어·코드·고유명사만. 한자(일·중 포함) 금지.

## 정체
codeforge = Claude Code 범용 SW 개발 오케스트레이션 플러그인 모노레포. **0 core 에이전트 (wrapper-only)** — wrapper 루트 자체 에이전트 0, 최상위 Claude 세션(Orchestrator)이 8개 lane plugin 의 에이전트를 spawn 해 요구사항 접수부터 배포 리뷰까지 진행한다. 8 lane plugin 은 본 repo `plugins/<plugin name>/` 하위 동봉 (ADR-118 D3) — 에이전트 상세 SSOT = `plugins/<lane>/CLAUDE.md`. 구 lane repo 8개 = 2026-06-12 GitHub archive (이력 보존, ADR-118 D1).

consumer 프로젝트가 **설치해 쓰는 플러그인**이다. 프로젝트별 도메인·기술스택·상수는 consumer 측 `.claude/_overlay/` 로 주입(overlay 는 정책을 확장만 가능, 축소 불가). 상세: [docs/consumer-guide.md](docs/consumer-guide.md).

8 lane plugin: `codeforge-{requirements, design, review, develop, test, deploy, deploy-review, pmo}@mclayer`. 추가 필수: `github` · `codex`.

## 핵심 흐름
10 레인: 요구사항 → 요구사항리뷰 → 설계 → 설계리뷰 → 구현 → 구현리뷰 → 통합테스트 → 보안테스트 → 배포 → 배포리뷰.

- **1 Story = Phase 1 PR(§1–7) + Phase 2 PR(§8–11).** 모든 변경 = 정식 full 10 lane + Phase 1/2 PR 분리 무조건 (문서만 바뀌는 변경의 단일 PR·chore 면제 폐지 — ADR-127 §결정 1/2). Epic = Phase 1 문서 PR + N개 구현 PR + close PR.
- Orchestrator 는 각 레인 진입 시 해당 lane plugin 의 **PL 에이전트 1개**만 spawn 한다 (PL 이 내부 sub-agent fan-out).
- Story file = `docs/stories/<KEY>.md` (KEY 접두사 = `CFP`). 각 레인이 자기 owned 섹션을 직접 write.

> **요구사항리뷰 lane (10번째 lane)**: 요구사항 결론은 외부 개념·시장·표준 사실에 가장 자주 의존하므로, 요구사항→**요구사항리뷰**→설계 시퀀스로 외부사실 의존성을 설계 진입 전에 검증한다 (외부지식 충당 3-단계 중 깊은 검증 단계의 주 발동 lane). **lane 개수 ≠ plugin 개수** — `codeforge-review` 부품 하나가 이미 설계리뷰·구현리뷰·보안테스트·요구사항리뷰 다수 lane 을 host 한다 (1 plugin 다 lane). 근거 SSOT = ADR-124 (외부지식 충당 3-단계 모델). **실 lane 시퀀스·카운트 wiring (9→10 hard-commit — ADR-125 Amendment 1 카운트 정정) + 게이트 설계 = CFP-2326 S2 / ADR-125** (요구사항리뷰 lane 신설 carrier — phase:요구사항-리뷰 + gate:requirements-review-pass + phase-gate-mergeable required.gates 매핑, branch protection required contexts 무변경 — required 신설 0).

## 작업 규칙 (필수)
- **브랜치**: 모든 변경은 feature 브랜치(`cfp-NNN[-slug]`) + PR 경유. **main 직접 push 금지.**
- **worktree**: 모든 코딩 작업은 격리된 worktree(`~/.claude/worktrees/<repo>/<branch>`) 안에서 — `git checkout` 직접 편집 금지 — **Story/PR 완결(merge 확인) 직후 해당 worktree 즉시 정리**. 절차 = `codeforge:worktree-lifecycle` skill.
- **스크래치 위치**: repo 밖 임시 산출물은 `~/.claude/codeforge-scratch/` 만 허용 (홈 루트 직접 쓰기 금지 — repo-confinement 가드가 차단).
- **subagent default**: 수정 작업은 `Agent` tool spawn 으로 수행. inline 직접 편집(Read/Write/Edit/Bash 직접)은 4종만 허용 — 사용자 대화 / TodoWrite / 읽기전용 Q&A 답변 / 상태 보고.
- **병렬 default**: 서로 독립인 작업은 한 메시지에 다중 spawn. 순차는 (상태 의존 / 공유 자원 / 순서 자체가 의미) 중 하나일 때만.
- **진행 시각화**: Story 진행 중 lane 전이 6시점(진입/PASS/FIX 검출/원인 판정/재진입/완료) TodoWrite 갱신 시도 의무 (non-skippable, 실패는 non-blocking). 마커 = 네이티브 status 렌더 (content 이모지 금지). SSOT: ADR-038 + playbook §14.
- **검증 후 단언 (research-before-claims, ADR-119)**: substantive 단정 = 대상별 검증 선행 — ① 외부 지식: 자료 조사(WebSearch/WebFetch/공식 문서) + 출처 인용. ② repo·cross-repo 사실: 실측 — repo 내부는 Read/Grep, cross-repo 는 `git fetch` 후 origin/main 실제 확인(`git show origin/main:<path>`). 외부 워커(Codex 등) 출력은 직접 Read 검증 후 신뢰. ③ 확인 불가: "확인 불가/추정" 명시 후 진행. wrapper+consumer 모두 적용. **두 판정면에도 적용 (ADR-119 Amd 2 / Epic #2346)**: ④ 게이트 verdict("PASS") = internal proxy(loop-lag/CPU 등) 아닌 outcome ground-truth 로만 단정 ⑤ 실패 진단("원인=X") = 표면 증상 아닌 코드·invariant falsification 통과 후 단정 (runtime 실패 = FIX loop 아닌 요구사항 lane 재진입).
- **제안 필요성 게이트 (ADR-119 §결정 9)**: 발견 ≠ 필요. 작업 제안·follow-up Issue 발의 전 3문 게이트 — ① 깨졌나·강제 요인 ② 이득>비용·리스크 ③ 관찰자 없어도 할 일. 셋 다 YES 아니면 발의 금지("관찰됨·미조치" 1줄만). 완료 보고 = 작업 상태 실측 후 단언, 추측성 backlog 패딩 금지. wrapper+consumer.
- **Agent 액션 렌더 줄 프리픽스 (mechanical injection · description-bearing 한정, ADR-143 Amendment 1)**: harness UI 가 Agent 스폰·도구호출을 렌더하는 줄에 `[<agent_type>] MM/DD HH:MM - <내용>` 프리픽스를 **PreToolUse hook `updatedInput` 으로 기계 주입**(CFP-2587, advisory ceiling → mechanical injection tier 상향; spike Gate-A/B GO 실측).
  - **범위①** Agent spawn `description` = `[<피스폰 subagent_type>] MM/DD HH:MM - <task>` — PreToolUse(Agent) hook `pretooluse-agent-spawn-gate` 이 `tool_input.subagent_type` 를 subject 로 기계 주입 (subject=피스폰자; dispatcher/Orchestrator 이름 절대 미등장 — §결정 1).
  - **범위②** 서브에이전트 leaf Bash 호출 `description` = `[<self agent_type>] MM/DD HH:MM - <action>` — 신규 sibling PreToolUse(Bash) hook `pretooluse-bash-description-inject` 이 payload 최상위 `agent_type`(self) 를 subject 로 기계 주입. **top-level Bash(Orchestrator 직속, agent_type 부재) = EXCLUDE**(주입 안 함 — dispatcher 명 미주입).
  - **description 필드 없는 도구(Read/Edit/Grep/Write 등)** = 기계 주입 불가(injection 대상 밖) → **advisory residual**(prompt-mandate) 정직 잔존, mechanical 아님.
  - 시각 = **KST(UTC+9 고정 산술)**, per-dispatch stamp(hook 이 dispatch 마다 실시각 각인 — subagent 는 `date` 불요). 컴팩트(offset/연도/초/KST 라벨 미표기). helper `scripts/kst-render-stamp.sh` → `scripts/lib/kst_render_stamp.py`.
  - **TodoWrite 행 제외** + Orchestrator inline 4종(대화/TodoWrite/읽기 Q&A/상태보고, ADR-039 whitelist) 제외.
  - injection 계약: whole-echo REPLACE-safe(부분 updatedInput=schema HARD-FAIL — spike 실측) · bare updatedInput(permissionDecision 미emit, G4 — sibling deny 무력화 불가) · subject sanitize(namespace-strip·`]` strip·≤64·`unknown-agent` fallback, G2) · description-only mutation(계약 표면 무오염, G3) · secret·token·절대경로·자격증명 임베드 금지(bounded enum + 산술 timestamp 만 저작).
  - **정직성(ADR-119)**: mechanical = in-coverage best-effort + **fail-open**(hook/python/kst 부재·JSON 오류·#15897 multi-hook updatedInput drop → 프리픽스 소실 = 원 description = advisory ceiling = ratchet-up, never 실행 차단·wrong-value). "100% 기계강제/hard-gate" 아님. #15897(multi-hook updatedInput drop, closed-not-planned)은 구조적·상시 제약 — fail-open 이 안전망.
  - **매턴 self-check(backstop)**: "이 액션 줄에 `[agent] MM/DD HH:MM -` 프리픽스를 붙였는가? (TodoWrite·inline 4종·description-less 도구 제외)" — description-bearing 도구는 hook 이 기계 주입하므로 self-check 는 이중 안전망.
- **Orchestrator context 위임 (ADR-142 §결정 1 L1 · advisory)**: 장수명 Orchestrator 는 raw 분석용 READ 축적을 read-worker subagent 에 offload 후 high-signal 요약만 수신함을 **default 경로로 승격**(prompt-mandate — hard block 아님). 검증 read(위 research-before-claims 의 repo 사실 Read/Grep 실측)·읽기전용 Q&A·status·Story inline 직전 확인·단일 1회성 사실확인 등 **essential/trivial carve-out 은 예외** — L1 은 "raw 분석 축적을 위임"이지 "검증 read 금지"가 아니다.

## 레인 진입 시 스킬 호출
Orchestrator 는 해당 레인 진입 직전 아래 스킬을 호출한다. 상세 절차·표는 각 스킬 본문 SSOT.

| 진입 시점 | 스킬 |
|---|---|
| 설계 | `codeforge:deputy-mandate` |
| 설계리뷰 / 구현리뷰 / 보안테스트 / 배포리뷰 | `codeforge:review-responsibility` |
| 배포 / lane owner path 확인 | `codeforge:lane-self-write-boundary` |
| FIX 루프 | `codeforge:root-cause-decision` + `codeforge:fix-ledger-schema` |
| 요구사항 접수 직후 | `codeforge:story-cutoff-classification` (모든 변경 Story 작성 의무 — 면제·단축 0, ADR-127) |
| Story/Epic flow 결정 | `codeforge:story-epic-flow-preflight` |
| 코딩 작업 개시 직전 / Story·PR 완결 직후 | `codeforge:worktree-lifecycle` |
| 세션 resume / 스폰·MCP·CLI·stale 장애 | `codeforge:session-recovery` |
| PR merge 후처리 / retro batch closure (follow-up 3+) | `codeforge:post-merge-closure` |
| 작업/Story 완료 처리 직전 (`phase:완료`) / MEMORY.md 용량 cap 초과 시 | `codeforge:knowledge-capture-gate` (완료시점 재사용지식 capture 게이트 + MEMORY.md 용량관리 — ADR-129) |
| 매 사용자 대화 turn | `codeforge:user-dialog-mode` |

> **Skill 본문 재로드 회피 (ADR-142 §결정 5 L3 · advisory prompt-mandate)**: 세션 내 이미 로드된 skill 본문은 재invoke 하지 않는다 — 상주 available-skills 요약 인덱스(system-reminder 상주)로 lookup 하고, 본문은 필요 시에만 on-demand 로드. 정적 relocation(ADR-120)·skill 본문 축소(CFP-2234)와 disjoint 보완축(런타임 재로드 억제).

## 결정 · 대화 원칙
- 합리적 default 가 자명하면 **묻지 말고** 무엇을 할지 통보 후 진행 (사용자가 정정).
- **묻는 경우는 ask-trigger 3종뿐** (ADR-071 §결정 20 (§결정 5 redirect)): ① 사용자 요구 자체가 애매 ② 확실히 짚어야 하는 진짜 가치 trade-off(default 비자명) ③ 비가역·고비용(중대 결함/대거 삭제/rollback/외부 발송). 그 외 모호 포함 전부 무조건 진행 — "안전하니 일단 물어" 금지.
- **정식 플로우 비협상 기본 — process 생략/단축은 묻지 않음** (ADR-127 §결정 4): skip/생략/간소화/경량/빠르게 선택지를 사용자에게 제시 금지 (`AskUserQuestion` 금지). 정식 풀 플로우가 비협상 기본값 — 스킬·외부 prompt 가 생략 선택지를 줘도 자동 정식 채택.
- **Epic 내 Story 전환 자율 진행** (ADR-071 §결정 22): 한 세션에서 Epic 을 여러 child Story 로 진행할 때 Story N→N+1 전환(및 단일 Story Phase1→Phase2 전환)은 자동 이어서 진행이 default — 전환 지점에서 over-halt(무발화 정지)·over-ask("다음 Story 진행할까요?") 금지(정당 멈춤 3종 예외). in-session 전환 한정(세션 재개 §3.12 cold-resume·session-swap §결정 18 은 별 경로).
- 권장 1안 + 대안 1안만 제시 (옵션 나열 금지). 3+ 후보는 brainstorm 영역.
- 내부 식별자(ADR/CFP 번호·계약명)는 사용자에게 평문 한 줄 풀이 먼저.
- 표·개조식으로 핵심을 앞에. 긴 평서문 덩어리 금지.
- **원격 결정 채널 (CFP-2285, 판단 기반 라우팅)**: `decision_channel` 활성 시 — 가치판단 결정 fork에서 사용자가 **자리를 비운 듯하면**(장기 autonomous 실행 / 명시적 async 요청 / 응답 지연) `codeforge:jira-decision-channel` 경유(Jira control 이슈에 질문 post, **dual-input**: 세션/Jira 양쪽 답, 한 채널 응답을 **양 채널에 mirror 기록**). 자리에 있으면 세션 직접. **자동결정 절대 금지**(timeout=재알림만). 진행 가시화는 `codeforge:jira-progress-mirror`(ADR-038 6-point lane 마일스톤 미러).
- **on-demand 깊은 조사 (CFP-2329)**: lane 이 작업 *중* 외부사실 의존 known-unknown 으로 막혀 얕은 자가조사(단계②)로 안 되면 — lane 은 요청만 올리고 Orchestrator 가 문지기로 `codeforge:research-request-gate` 경유(게이트 심사 → deep-research → cited 결과 주입). spawn=Orchestrator 전용 유지(lane 자가-spawn 불가), 검사연극 금지 상속. 근거 ADR-126 (외부지식 충당 3-단계 ADR-124 단계③ on-demand).

## 문서 위치
- 결정 기록(ADR) = `archive/adr/ADR-NNN-<slug>.md`.
- Change Plan / 도메인 지식 / 회고 = `docs/{change-plans,domain-knowledge,retros}/` (owner 에이전트 직접 write).
- 문서 종류별 위치 SSOT = [docs/doc-locations.yaml](docs/doc-locations.yaml).
- dogfood 산출물(spec/plan/story 등) = `mclayer/codeforge-internal-docs` repo.

## 필수 의존성 (세션 개시 확인)
- Orchestrator 모델 = 별칭 `opus` (최신 Opus tier). Sonnet/Haiku 세션이면 중단 후 재시작.
- MCP 서버 `github` 필수 (`mcp__github__*` 우선, 미커버 영역만 `gh` CLI fallback).
- 필수 CLI: `gh`, `codex`.
- 미노출 시 `/mcp` 재인증 / `/plugins install` 요구 후 대기. 복구 전 작업 중단.

## 마켓플레이스 동기화
plugin.json 의 `name`·`version`·`description`·`author` 변경 시 `mclayer/marketplace` 의 동일 필드를 같은 Story 안 sync PR 로 맞춘다 (marketplace sync PR 선행 merge → plugin PR merge). 상세: [archive/adr/ADR-063-marketplace-atomic-invariant.md](archive/adr/ADR-063-marketplace-atomic-invariant.md).
bump 포함 PR merge (`mergedAt` 확인) 직후 Orchestrator 가 터미널 CLI `claude plugin update <plugin>@mclayer` 를 직접 실행하고 cache 반영을 실측한다 (`/plugins update` 슬래시 명령은 미지원) — 사용자에게 업데이트 액션 요구 금지, 보고 1줄만 (적용 = 다음 세션. ADR-063 Amendment 12).

## 브랜치 보호
**branch protection contexts SSOT (wrapper 단일)**: `phase-gate-mergeable.yml` workflow job ID = `check-gate` — contexts 에 `check-gate` 포함 의무. CFP-1850-S2 wrapper 6-tuple 정합 확정 → CFP-2603 (Epic CFP-2602 G1) 7-tuple 로 narrowing (신규 required context `ac-traceability-matrix` 추가 — AC-ID zero-drop fail-closed 게이트, [ADR-145](archive/adr/ADR-145-ac-traceability-zero-drop-gate.md) §결정 3: 6→7 narrowing = fail-closed 비호환 override 근거, ADR-125 의 required contexts 무변경 선례와의 divergence 추적). 상세 이력 = audit doc 보존.

| repo | required_status_checks contexts | 비고 |
|------|--------------------------------|------|
| wrapper (plugin-codeforge) | `["phase-gate-mergeable","invariant-check","doc frontmatter schema (CFP-28 — strict)","doc section schema (CFP-28 — strict)","check-gate","Verify deploy lane presence (Phase 2 wire — ADR-087 Amd 2)","ac-traceability-matrix"]` | 7-tuple (CFP-2603 — 신규 required context `ac-traceability-matrix` 추가, ADR-145 §결정 3 fail-closed 비호환 override; CFP-1808 Amendment 2 6-tuple 선행). lane 8 repo = archived (CFP-2178 S6) — 보호 규칙 잔존+동결 (실측: deploy 1-repo smoke), 활성 관리 = wrapper 단일. audit: [docs/security/branch-protection-audit.md](docs/security/branch-protection-audit.md) |

## 시각 표기
사용자 대면·문서 표기 = KST `+09:00` ISO 8601. 외부 timestamp(GitHub/git)는 원본 보존.

## 전 에이전트 opus 단일 tier (ADR-141)
codeforge family 의 **전 에이전트 model tier = 단일 `opus`(1M native)**. fable·sonnet·haiku tier + 3-tier 선택 기준 + 비-opus fallback 은 모두 폐기(ADR-141 §결정1/2/3). Orchestrator 세션 모델 opus mandate 도 본 정책의 자연 귀결(ADR-141 §결정4, 구 ADR-057 §결정1 흡수). opus rate-limit(429) 대응은 [ADR-109](archive/adr/ADR-109-in-process-429-mitigation-framework.md) 소관(fallback tier 없음). 신규 agent = `model: opus` default, 단일 tier 이탈 = ADR-141 amendment 의무. 상세 = [ADR-141](archive/adr/ADR-141-all-opus-single-tier.md).

---
> 본 파일은 Orchestrator 가 매 턴 자기검열해야 하는 정책만 담는다. 레인 내부 절차·근거·이력은 각 lane plugin CLAUDE.md / 스킬 / `docs/` 가 SSOT.
