---
kind: concept_definition
type: domain-knowledge
slug: hook-timeout-fail-open-boundary
title: Hook timeout fail-open boundary — 차단 게이트 결정론의 시간 예산 경계 + hook 체인 지연세의 병렬 실행 모델
status: Active
updated: 2026-08-14
carrier_story: CFP-2965
related_adrs:
  - ADR-115  # runtime hook enforcement — 본 concept 은 그 게이트 결정론의 "시간 예산 안에서만" 경계를 추가 (Amendment 2 가 timeout 예산 규칙 codify)
  - ADR-143  # render-line prefix — pretooluse-bash-description-inject (최중량 훅) 의 기능 SSOT
  - ADR-119  # research-before-claims — 실지연 ground-truth 판정면 (내부 proxy 금지)
related_concepts:
  - orchestrator-runtime-hook-enforcement   # 게이트 mechanism SSOT (무엇이 차단 가능한가) — 본 concept 은 언제까지 차단이 성립하는가(시간 축)
tags:
  - claude-code
  - hooks
  - timeout
  - fail-open
  - latency-tax
  - windows-process-spawn
sources:
  - https://code.claude.com/docs/en/hooks           # timeout 만료 fail-open verbatim / async / exec form / 병렬+dedup
  - https://code.claude.com/docs/en/hooks-guide     # timeout 기본값 표 / Windows 셸 선택 / updatedInput 비결정성 / deny precedence
  - https://code.claude.com/docs/en/plugins-reference  # 플러그인 hooks.json 변경 반영 경로 (/reload-plugins 또는 재시작)
  - https://pythondev.readthedocs.io/startup_time.html  # CPython 기동 8~100ms
  - https://gitforwindows.org/windows-vs-linux-fork-and-exec-semantics.html  # Windows 프로세스 생성 고비용·fork 부재
  - https://owasp.org/www-community/Fail_securely   # fail-open/fail-closed 표준 정의
---

## 정의

**Hook timeout fail-open boundary** = Claude Code PreToolUse 차단 게이트(deny)의 결정론은 **per-hook timeout 예산 안에서만** 성립한다는 플랫폼 semantics. timeout 만료 시 해당 hook 만 취소되고 tool call 은 정상 permission flow 로 **진행**된다(fail-open). 공식 문서 verbatim:

> "A timed-out `command`, `http`, or `mcp_tool` hook doesn't block the tool call. The call continues through the normal permission flow, so **don't count on a stalled hook to act as a gate**." — [hooks reference](https://code.claude.com/docs/en/hooks)

부수 개념 **hook 체인 지연세(latency tax)** = 모든 도구 호출에 hook 체인이 부과하는 호출당 고정 지연. Windows 에서는 프로세스 캐스케이드(fork 부재 + CreateProcess 고비용 + Python 콜드스타트 8~100ms/회 — 단 codeforge 측정 호스트 실측 = median 200ms/회, CFP-2965 M2)가 주 기원.

## 컨텍스트

codeforge 는 [orchestrator-runtime-hook-enforcement](orchestrator-runtime-hook-enforcement.md)로 "PreToolUse deny = 런타임 결정론적 gate" 를 확립했다. CFP-2965 (Bash 훅 체인 지연 실측: median 13,529ms / p90 51,564ms / max 586,398ms, n=6,376) 에서 세 사실이 추가로 확정됐다: ① 그 게이트의 결정론은 시간 예산 경계를 갖는다(본 concept), ② timeout 필드 부재의 실효 semantics 는 "무한" 이 아니라 **플랫폼 기본값 600초(command hook)** 다, ③ 위 실측의 관측 채널(VS Code 확장 Slow-log)은 **≥ 약 2,000ms 이벤트만 기록하는 절단(censoring) 채널**이다 (CFP-2965 M5 실측 확정 — 전 기간 min=2,000ms, 미만 기록 0건) — 이 채널 통계량의 무보정 전/후 비교는 생존자 편향으로 무효.

## 핵심 규칙

- **R-1 timeout 값 공간**: 단위 = 초, per-hook 적용. 기본값 = command/http/mcp_tool 10분(600s), prompt 30s, agent 60s. 이벤트 특례: UserPromptSubmit 은 command 계열을 30s 로, MessageDisplay 는 10s 로 하향. SessionEnd 는 전 hook 공유 1.5s 예산(per-hook timeout 을 1.5s 초과로 설정 시에만 그 값까지 상향, 최대 60s — ≤1.5s 값은 예산 무변경). [hooks-guide]
- **R-2 timeout 만료 = fail-open 창**: 만료된 hook 만 취소, 다른 hook 은 계속, tool call 은 진행. **deny 게이트에 짧은 timeout 을 주는 것 = 그 시간 초과 구간에서 게이트를 fail-open 으로 전환하는 결정** — timeout 값 산정은 성능 튜닝이 아니라 보안 방향성 결정을 겸한다 (OWASP fail-securely: 보안 통제 실패는 거부 경로와 같은 경로여야 함 — timeout fail-open 은 이 원칙의 플랫폼-강제 예외). 만료 fail-open 은 **흔적 0** (프로세스 kill — stderr·exit 전무)이라 내부 fail-open(진단 라인 방출)과 사후 판별이 다르다.
- **R-3 병렬 실행 모델 — 문서 사실과 구현 관측의 구분 (CFP-2965 보정)**: 공식 문서 사실 = "All matching hooks run in parallel" [hooks reference]. 구현 관측 (CFP-2965 M3/M5, 측정 호스트) = ① 격리 환경에서 6훅 동시 실행 시 wall 1,192ms ≈ 최중량 훅 단독×1.16 (max-수렴 — 병렬 모델 재현) ② 그러나 실세션 Slow-log p50 2,923ms ≈ 순차 체인 wall 실측 2,760ms 로 **순차 실행 정황** (병렬이면 wall < 절단 임계 2,000ms 라 로그 출현 자체가 불가한데 n=156 출현). 두 사실은 아직 미해소 모순 — 설계·측정은 양쪽 모델 모두에서 유효한 지표(체인 wall 직접 측정 + per-hook 격리)로 구성해야 한다. 문서-병렬 전제의 함의는 유지: (a) 무경쟁 병렬 시 체인 wall ≈ max(개별) + dispatch 오버헤드 (b) deny precedence: any-deny-wins 보존 의무 (c) 다중 hook 이 같은 tool input 에 updatedInput 반환 시 last-to-finish 승리(비결정) — "같은 input 수정 hook 은 1개만" 이 플랫폼 공식 경고.
- **R-4 async 는 차단 불가**: `async: true` = 전 이벤트 발화 + decision 전면 무시 — verbatim: "The hook's exit code, stdout, and stderr are discarded, so asynchronous hooks can't make decisions like blocking a tool call or denying a permission." [hooks reference] → deny 게이트·updatedInput 훅에 부적용, record-only 캡처 훅만 후보. 잔여 미확인 = async 훅의 tool_response 수신 동일성 + delivery-drop(프로세스 자체 미실행/소실) 관측성.
- **R-5 Windows 실행 방식**: shell form(args 부재) = Git Bash 직접 spawn (Git Bash 부재 시 PowerShell). exec form(args 지정) = 셸 자체가 없음(무셸, command 는 실 .exe 로 해석). cmd.exe 경유는 플랫폼 강제가 아니다 — 레포 자체 polyglot wrapper(run-hook.cmd) 층의 선택.
- **R-6 반영 경로**: 플러그인 hooks.json 변경은 settings-파일 hook 과 달리 live file-watch 비대상 — `/reload-plugins` 또는 세션 재시작으로 반영. 전/후 실측 시 "개선 후" 측정이 stale hook 으로 이뤄지는 오류를 막는 신선도 전제 (sentinel 마커로 신 코드 실행을 실측 확인 후 측정 개시).

## 경계

- **In scope**: Claude Code hook 실행 semantics 의 시간·병렬·fail-open 축. 지연세의 Windows 프로세스 캐스케이드 기원.
- **Out of scope**: 훅 기능 계약 내용(deny 조건·G1-G5·record-only 스키마 — 각 기능 ADR 소관) / harness 자체 수정 / 구체 감축 설계 결정(설계 lane 소관 — 본 concept 은 선택지의 물리 법칙만 제공).
- **Anti-pattern**: ① "timeout 부재 = 무한 대기" 가정 (실효 = 600s 기본값). ② 병렬 실행 hook 지연의 합산 모델 단정 — 역방향으로 "문서가 병렬이라 하니 실행도 병렬" 단정도 금지 (R-3 모순 미해소 — 실측으로 판별). ③ deny 게이트의 timeout 을 fail-open 결과 계상 없이 성능 수치만으로 산정. ④ async 화로 deny 게이트 지연 제거 시도 (차단 능력 상실). ⑤ 절단 채널(Slow-log) 통계량의 무보정 전/후 비교 (생존자 편향).

## 관련 ADR

- **ADR-115** (+Amendment 2) — runtime hook enforcement. 본 concept = 그 결정론 게이트의 시간 예산 경계 추가 (mechanism 무손상). Amendment 2 (CFP-2965) 가 24 entry timeout 실배선 + 산정 규칙 3종(하한 불변식/fail-open 계상/차등 tier) codify.
- **ADR-143** (+Amd2/3/4) — 최중량 훅 pretooluse-bash-description-inject 의 기능 SSOT (fail-open backup 방향성 = 의도된 fail-open 축, R-2 의 플랫폼-강제 fail-open 축과 구별).
- **ADR-119** (+Amd2) — 개선 판정 = 내부 proxy(스폰 수·CPU) 아닌 실지연 ground-truth.

## 변경 이력

| 일자(KST) | Story | 변경 |
|---|---|---|
| 2026-08-13 | CFP-2965 | 신규 — 요구사항 lane Mandate 1·2 탐구 산출. timeout fail-open boundary + 병렬 실행 지연 모델 + Windows 캐스케이드 기원 + 반영 경로 codify. |
| 2026-08-14 | CFP-2965 | 설계 lane 실측 보정 — 절단 임계 2,000ms 실측 확정(M5) / R-3 문서-병렬 vs 구현-순차 정황 모순 명시(M3·M5 — 양쪽 모델 유효 지표 의무) / R-1 SessionEnd "longer" 조건 정밀화 / R-4 async decision 무시 verbatim 승격 / T-2 무흔적 만료 판별 추가. 잔재 회수(main 체크아웃 untracked → cfp-2965 브랜치 정식 커밋). |
