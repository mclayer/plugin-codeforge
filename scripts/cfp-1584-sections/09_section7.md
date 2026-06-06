## 7. 세션 재개(resume) 복원 절차

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
| phase:설계 | §7 + §11 초안만 | ArchitectPLAgent — Mapper·Refactor·SecurityArchitect·TestContractArchitect·DataMigrationArchitect **병렬 재스폰** + ArchitectAgent (chief author) 통합 의뢰 (이전 산출물 세션 외 유지 불가, §7/§11 Change Plan 초안만 복원됨) |
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

### 7.4 FIX 카운터 복원 (세션 개시/압축 재개 시 의무)

세션 개시 시점 또는 컨텍스트 압축 후 재개 시 Orchestrator는 **반드시** 아래를 수행:

1. 활성 Story file `Read(docs/stories/<KEY>.md)` 호출
2. §10 "FIX Ledger" 파싱 → 마지막 `RESET 구현-리뷰` 이후 행으로 각 레인 카운터 산출 (설계-리뷰 / 구현-리뷰 / 구현-테스트 / 보안-테스트 4개)
3. 파일 read 실패 시 **사용자 ESCALATE** (카운터 불명 상태 진행 금지)

GitHub 라벨 count는 감사 이력으로 보존되나 복원 source of truth 아님 (§10 기준). 이 절차 없이 ArchitectPLAgent 판정 진행 금지.

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
- Story file 접근 불가 → §9.4
- phase 라벨과 Story file 섹션 불일치 → 사용자 판단 요청

---

