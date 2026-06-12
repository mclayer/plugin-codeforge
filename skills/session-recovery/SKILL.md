---
name: session-recovery
description: 세션 재개(resume) 복원 절차 + 운영 트러블슈팅 lookup (활성 Story resume / 에이전트 스폰 실패 / GitHub MCP 장애 / Codex CLI 미설치 / Story file·Mapper stale). 세션 개시 시 활성 Story 존재 또는 위 장애 발생 시 호출. gate 명제 (§7.4 FIX 카운터 복원 / §9.6-§9.7.1 label 매핑) 는 playbook 잔류 — 본 skill 은 guide 절차만.
tools: Read
---

# Session Recovery (CFP-2198 / ADR-120 — playbook §7 + §9.1-§9.5 이전)

> **절차 본문 SSOT = 본 skill** — `docs/orchestrator-playbook.md` §7 guide 절차 + §9.1-§9.5 트러블슈팅에서 이전 (CFP-2198, ADR-120 §결정 1 cold×guide). **gate 명제는 playbook 잔류** (ADR-120 §결정 3 — skill 확률 활성화는 gate 캐리어 불가): §7.4 FIX 카운터 복원 의무 / §9.6 PR keyword 정책 / §9.7-§9.7.1 phase×gate label 매핑. 본 절차 수행 중 해당 지점 도달 시 playbook 원문 참조.
>
> **mirror-carrier 주석 (Codex TP 반영)**: 본 body 안의 의무/금지 표현은 전부 1차 carrier 의 mirror 다 — Never-skippable 병렬 스폰 = requirements lane agent 정의 (Domain/Analyst/Researcher 등 4+ 파일) / Codex CLI 미설치 시 진입 불가·중단 = wrapper `CLAUDE.md` 필수 의존성 anchor / Mapper 매 진입 재스폰·재사용 금지·단독 설계 결정 금지 = design lane `CLAUDE.md` + `CodebaseMapperAgent.md` + `ArchitectPLAgent.md` mandate. 본 skill 미활성 turn 에도 해당 gate 들은 1차 carrier 로 유지된다 (ADR-120 §결정 3 정합 — 본 skill 은 gate 의 단독 carrier 아님).

## 1부 — 세션 재개(resume) 복원 절차 (playbook §7 이전분)

### 7.1 활성 Story 조회

```
mcp__github__list_issues(state='open', labels=['type:story'])
```

또는 `Bash(gh issue list --label "type:story" --state open --json number,title,labels)`.

- 0건: 신규 세션
- 1건: 자동 resume — §7.3 매핑
- 2건 이상: 사용자에게 확인

### 7.2 Story file 최신 섹션 판독

`Read(docs/stories/<KEY>.md)` → 어느 섹션까지 채워졌는지 확인해 재진입 지점 보정.

### 7.3 phase label ↔ 재진입 에이전트 매핑

| phase 라벨 | Story file 섹션 | 재진입 에이전트 |
|-----------|-----|-----------------|
| phase:요구사항 | §1만 채움 | RequirementsPLAgent 재스폰 → Domain·Analyst·Researcher **병렬 재스폰** (Never-skippable 3종 전원) |
| phase:요구사항 | §2·§5·§6 **일부만** 채움 (부분 완료 resume) | 비어있는 섹션의 에이전트만 **선택 재스폰** + 이미 채워진 섹션은 PL 통합 단계에서 재활용. §9.0에 "Resume 부분 재스폰" 행 append |
| phase:요구사항 | §2·§5·§6 모두 채움 | RequirementsPLAgent 통합 명세서 재확정 단계 재진입 ("사용자 확인 필요" 해소 여부 체크). 일부 관점 재보강 필요 시 clarification 재스폰 |
| phase:설계 | §7 + §11 초안만 | ArchitectPLAgent — Mapper·Refactor·SecurityArchitect·TestContractArchitect·ModuleArchitect **병렬 재스폰** + ArchitectAgent (chief author) 통합 의뢰 (이전 산출물 세션 외 유지 불가, §7/§11 Change Plan 초안만 복원됨) |
| phase:설계 | §7/§11에 6 SubAgent 일부만 반영 (부분 완료 resume) | 미반영 쪽 SubAgent만 **선택 재스폰** + 반영된 쪽은 재활용. §9.0에 "Resume 부분 재스폰" 행 append |
| phase:설계 | §7 완료 | ArchitectAgent 가 Change Plan 저장 완료 보고 + Story §3/§7/§11 self-write 완료 확인 → 설계 리뷰 진입 |
| phase:설계-리뷰 | §9.1 블록 없음 | DesignReviewPLAgent 재스폰 (Claude/Codex 병렬) |
| phase:설계-리뷰 | §9.1 블록 FIX | ArchitectPLAgent → ArchitectAgent (chief author) 재스폰, Change Plan 갱신 |
| phase:구현 | §7 완료, §8 비어있음 | Phase 2 PR open 여부 확인. 없으면 DeveloperPL 직접 mcp__github__create_pull_request 호출. 있으면 DevPL + QADev 병렬 스폰 |
| phase:구현 | §8 일부 | 마지막 구현 에이전트 (§8에서 확인) 재스폰 |
| phase:구현-리뷰 | §9.2 블록 없음 | CodeReviewPLAgent 재스폰 |
| phase:구현-리뷰 | §9.2 블록 FIX | DeveloperPL 1차 진단 → ArchitectPLAgent 최종 판정 |
| phase:구현-테스트 | §9.3 블록 없음 | `gh pr checks <PR_NUMBER> --watch` 재실행 (CI gate 재확인) |
| phase:구현-테스트 | §9.3 블록 FAIL | DeveloperPL 1차 진단 → ArchitectPLAgent 최종 판정 |
| phase:통합-테스트 | §9 통합 테스트 블록 없음 | IntegrationTestAgent 재스폰 |
| phase:통합-테스트 | §9 통합 테스트 FAIL | DeveloperPL 1차 진단 → ArchitectPLAgent 최종 판정 |
| phase:보안-테스트 | §9.4 블록 없음 | SecurityTestPLAgent 재스폰 (Claude/Codex 병렬, lanes.security_ai: true 시만) |
| phase:보안-테스트 | §9.4 블록 FIX | DeveloperPL 1차 진단 → ArchitectPLAgent 최종 판정 |

> **§7.4 FIX 카운터 복원 = gate, playbook 잔류** — 세션 개시/압축 재개 시 의무 절차는 `docs/orchestrator-playbook.md` §7.4 원문 수행 (본 skill 미수록).

### 7.5 사용자 통보

```
🔄 세션 재개

[복원된 상태]
- Story: <KEY> — {제목}
- phase: {현재 라벨}
- 재진입 지점: {에이전트 이름} 스폰
- FIX 카운터: 설계 리뷰 {n}/3, 구현 리뷰 {m}/3, 구현 테스트 {k}, 보안 테스트 {s}
- Story file 마지막 갱신 섹션: §{X}

[이어서 진행합니다. 문제 있으면 알려주세요.]
```

### 7.6 Fallback (자동 판정 실패)

- 활성 Story 2건 이상 → 사용자에게 어느 Story resume 질문
- Story file 접근 불가 → §9.4 (본 skill 2부)
- phase 라벨과 Story file 섹션 불일치 → 사용자 판단 요청

## 2부 — 트러블슈팅 (playbook §9.1-§9.5 이전분)

### 9.1 에이전트 스폰 실패

| 증상 | 원인 | 대응 |
|------|------|------|
| Agent 툴 호출 실패 | subagent_type 철자 오류 | `agents/` 목록과 대조 후 재시도 |
| 권한 거부 | path-scoped 권한 불일치 | 대상 에이전트 md frontmatter 확인, 담당 에이전트 재선택 |
| 무한 스폰 | 서브에이전트가 Agent 툴 호출 시도 | 플랫폼 제약 위반 — 해당 에이전트 md에 "직접 스폰 불가" 명시 확인 |

### 9.2 GitHub MCP 연결 장애

GitHub Issue/PR 갱신·코멘트 기록·sub-issue 생성 불가 시:

1. 세션 내 임시 로그로 전환 — Orchestrator 메모리에 갱신 내용 누적
2. 사용자에게 "GitHub MCP 장애" 통보. 가능한 fallback: `gh issue ...` Bash CLI
3. 복구 후 각 lane plugin 재스폰으로 backlog 동기화 (lane plugin self-write 재실행)
4. **FIX 카운터 조회 불가 시** (docs file은 로컬 file이라 read는 보통 가능): 그래도 실패하면 ArchitectPLAgent 판정 정지 → 사용자 판단 요청

### 9.3 Codex CLI / 플러그인 미설치

- **CodexReviewAgent**: 미설치 시 3 리뷰 레인(설계 리뷰·구현 리뷰·보안 테스트) **모두 진입 불가** → 설치 안내 + 세션 중단
- **RequirementsAnalyst**: `codex` CLI 미설치 시 요구사항 레인 **진입 불가** → 동일
- `SKIPPED` 경로 허용 안 됨

### 9.4 Story file stale 감지

에이전트 보고에서 "Story file에 없는 컨텍스트" 또는 "현재 코드와 불일치" 감지 시:

1. Orchestrator 가 해당 lane plugin 재스폰 → 최신 상태로 Story file 갱신 (lane plugin self-write)
2. 갱신 완료 후 해당 에이전트 재스폰

### 9.5 CodebaseMapper 산출물 stale 감지

- Mapper는 **매 설계 레인 진입 시 재스폰** — 이전 Story 산출물 재사용 금지
- 리뷰·테스트에서 설계 레인 복귀 시에도 재스폰 (구현 레인에서 코드 변경 가능성)
- 재사용 감지 시 ArchitectAgent (chief author) 단독 설계 결정 금지 (§2 설계 공동작업자 부재 상태)

> **§9.6-§9.7.1 = gate, playbook 잔류** — Phase 1/2 PR keyword 정책 + phase×gate label 매핑 + transition timing 은 `docs/orchestrator-playbook.md` §9.6-§9.7.1 원문 참조 (본 skill 미수록).
