# codeforge 삭제 계획서 (PRUNE PLAN)

> 목적: "절차를 통제하는 기계"를 걷어내고 "실제로 일하는 얇은 오케스트레이터"만 남긴다.
> 원칙: rewrite(전부 새로) ✗ · 패치 누적 ✗ · **하중 받치는 30%만 남기고 70% 삭제** ✓

---

## 0. 진단 요약 (실측)

| 항목 | 현재 | 문제 |
|---|---|---|
| 애플리케이션 코드(src) | 0 줄 | 이 repo는 100% 절차+기계 |
| CLAUDE.md | 27,000 토큰 / 매 턴 로드 | **나쁜 결과물 1순위 원인** |
| 결정 기록(ADR) | 120개 / 폐기 0건 | 쌓이기만 함 |
| 강제용 검사 스크립트(check-*) | 152개 | 규칙 감시가 유일한 일 |
| 그 스크립트 테스트 | 478파일 / 48,835줄 | 감시기를 다시 검증 |
| 문서 전체 | 216파일 / 73,242줄 | |
| CHANGELOG.md | 537KB | git 히스토리와 중복 |

**추가 증거 — 문서끼리 모순:** README는 "6 lane / 7 레인", CLAUDE.md는 "8 lane". 문서가 너무 많아 자기들끼리 어긋남(drift). 이게 비대화의 결과다.

---

## 1. 무엇이 "하중을 받치는가" (= 남길 것)

Claude Code 오케스트레이션 플러그인이 **실제로 작동하는 데 필요한 최소 골격:**

| 유지 | 이유 | 처리 |
|---|---|---|
| `.claude-plugin/plugin.json` | 플러그인 매니페스트(필수) | 그대로 |
| `skills/` 12개 | **on-demand 로드** — 매 턴이 아니라 필요할 때만 읽힘. 비대화 안 일으킴 | 유지하되 내부 jargon 정리 |
| 핵심 템플릿 한 줌 | 에이전트가 만드는 산출물 양식 | story / PR / ADR / change-plan / impl-manifest 만 |
| 핵심 CI 워크플로 ~10개 | 실제로 깨짐을 막는 게이트 | phase-gate + CI required check 류만 |
| `hooks/session-start` + 최소 | 세션 초기화 | 대화규칙 hook 제거 후 슬림화 |
| 짧은 CLAUDE.md | 오케스트레이션 정책 핵심 | **≤ 2,500 토큰 재작성** |

---

## 2. 디렉토리별 처분 (KEEP / CUT / ARCHIVE)

> ARCHIVE = `archive/` 디렉토리로 이동(삭제 아님, git 히스토리+참조용 보존). CUT = 삭제.

### docs/ (216파일 / 73,242줄)
| 경로 | 처분 | 비고 |
|---|---|---|
| `docs/adr/` 120개 | **ARCHIVE 전부** → `archive/adr/` | 살아있는 결정은 1장짜리 `docs/decisions.md`로 손수 요약 |
| `docs/inter-plugin-contracts/` 32개 | **CUT 대부분** | 레인 plugin 간 실제 통신 스키마 1~2개만 유지, 버저닝 레지스트리 전부 삭제 |
| `docs/domain-knowledge/` 45개 | **ARCHIVE** | 거버넌스 해설 — 참조용 보관 |
| `docs/orchestrator-playbook.md` | **CUT → 재작성** | 핵심만 CLAUDE.md 또는 skill로 흡수 |
| `docs/architecture/`, `docs/security/` | KEEP (소량) | 실질 정보 |
| `docs/walk-entries/`, `docs/upgrade-events/`, `docs/parallel-work/`, `docs/kpi/` | **CUT** | 메타 거버넌스 산물 |

### scripts/ (442파일 / 60,123줄)
| 분류 | 처분 | 비고 |
|---|---|---|
| `check-*` 152개 | **CUT ~140개** | 실제 깨짐(빌드/배포/문법) 잡는 ~10개만 유지. 규칙 감시용 전부 삭제 |
| bootstrap/upgrade/deploy 류 | KEEP 선별 | consumer 설치·배포에 실제 쓰이는 것만 |
| 나머지 거버넌스 측정/canary/walk 류 | **CUT** | |

### tests/ (478파일 / 48,835줄)
- **삭제하는 스크립트의 테스트는 함께 CUT.** 남기는 ~10개 스크립트 테스트만 유지 → 대략 480 → ~30파일.

### templates/ (229파일)
| 유지 | CUT |
|---|---|
| story-page-structure, github-pr-template, ADR, change-plan, impl-manifest, CODEOWNERS, 핵심 issue-form | team-spec 7종, agent-teams-hook-samples, scheduler, rulesets, walk/upgrade/audit 류, 중복 progress-examples |

### github-workflows (templates + .github = 289개)
- **KEEP ~10:** phase-gate-mergeable, invariant-check, doc schema check, CI 빌드, story-init.
- **CUT 나머지 ~279:** marketplace-drift, wording-dictionary, kst-timestamp, bypass-counter, canary, codex-network 등 거버넌스 강제 워크플로 전부.

### hooks/ (16파일)
| 유지 | CUT |
|---|---|
| session-start, run-hook.cmd, plugin.json 연결 | plain-language-check(+py+reminder), korean-english-recovery(+py), schedule-wakeup-reminder, userprompt-submit 대화규칙 주입, pretooluse-agent-spawn-gate 의 거버넌스 부분 |
- **효과:** 매 턴 주입되던 대화규칙 ~1,800 토큰 제거.

### 루트
| 파일 | 처분 |
|---|---|
| `CHANGELOG.md` (537KB) | **ARCHIVE** → `archive/CHANGELOG-legacy.md` (git 히스토리가 SSOT) |
| `CLAUDE.md` (27K토큰) | **재작성 ≤ 2,500토큰** |
| `README.md` | 재작성 (lane 수 모순 수정) |
| `overlay/`, `examples/` | KEEP 선별 (consumer 진입점) |

---

## 3. 목표 수치 (Before → After)

| 지표 | Before | After 목표 | 감축 |
|---|---|---|---|
| CLAUDE.md 토큰 | 27,000 | ≤ 2,500 | ~91% |
| 매 턴 hook 주입 | ~1,800 | 0 | 100% |
| ADR(살아있는) | 120 | 1장 요약 | ~99% |
| check 스크립트 | 152 | ~10 | ~93% |
| 테스트 파일 | 478 | ~30 | ~94% |
| CI 워크플로 | 289 | ~10 | ~97% |
| docs 줄 수 | 73,242 | ~5,000 | ~93% |

**한 줄 요약: 매 턴 모델이 깔고 시작하는 거버넌스 컨텍스트 ~30K 토큰 → ~2.5K 토큰.**

---

## 4. 실행 순서 (단계별, 각 단계 후 멈춰서 확인)

1. **백업 브랜치 + archive 이동** — 아무것도 영구 삭제 안 함. `archive/`로 옮기고 git 브랜치 하나 따둠. (되돌리기 100% 보장)
2. **CLAUDE.md 재작성** — ≤2,500토큰. 가장 효과 큰 단일 작업. 여기서 결과 품질 개선 즉시 체감 가능.
3. **대화규칙 hook 제거** — 매 턴 토큰 절약.
4. **워크플로 + check 스크립트 + 테스트 동반 삭제** — 한 묶음.
5. **docs ARCHIVE + decisions.md 요약 작성.**
6. **README/매니페스트 정합성 수정** — lane 수 등 모순 제거.
7. **재발 방지 규칙 1줄 추가:** "새 규칙 추가 시 기존 규칙 1개 삭제(net-zero) + CLAUDE.md 토큰 하드캡."

---

## 5. 리스크 / 안전장치

- **영구 삭제 0건 (1단계 기준):** 전부 `archive/`로 이동 + 백업 브랜치. 잘못되면 즉시 복구.
- **consumer 영향:** 이 repo를 설치해 쓰는 프로젝트(mctrader 등)가 의존하는 스크립트/워크플로는 CUT 전에 별도 확인. → 4단계 전에 "consumer가 실제 호출하는 파일" 목록 1회 추출.
- **검증:** 각 단계 후 플러그인이 로드되는지(plugin.json valid) + 핵심 CI가 도는지만 확인. 나머지는 안 봐도 됨.

---

## 6. 다음 결정 (사용자)

- 이 계획대로 **1단계(백업+archive 이동)부터** 시작할지
- 목표 수치(예: CLAUDE.md 2,500토큰)를 조정할지
- 또는 단계 순서를 바꿀지
