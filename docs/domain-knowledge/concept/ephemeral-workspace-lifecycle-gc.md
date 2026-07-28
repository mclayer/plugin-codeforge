---
kind: concept_definition
type: domain-knowledge
slug: ephemeral-workspace-lifecycle-gc
title: Ephemeral workspace lifecycle GC — 세션 잔재 수명 규약 (4분류 + TTL-at-creation + 트리거 다중화 + 보존 예외 명시 마커 + aging report)
status: Active
updated: 2026-07-26
carrier_story: CFP-2822
related_adrs:
  - ADR-169  # 세션 잔재 수명 규약 SSOT — 본 concept 를 §결정 1 concept SSOT 로 명명
  - ADR-040  # registered worktree lifecycle — 인접·분리 (본 개념의 상위집합, anti-corruption layer)
  - ADR-128  # 완료 단계 정식화 (§결정 3 = ADR-169 §결정 4 가 단일-wire sub-claim scoped-supersede)
  - ADR-045  # Story 완료 회고 (residue-clean 완료-게이트 = ADR-169 §결정 9 로 이관)
  - ADR-061  # thin-wrapper (8-line bash launcher + Python SSOT) — 발견 스캐너 구조 근거
  - ADR-110  # Task Scheduler — OS 스케줄러 consumer opt-in 보조 트리거
related_files:
  - archive/adr/ADR-169-ephemeral-residue-lifecycle.md              # 개념 normative SSOT
  - docs/domain-knowledge/concept/deferred-item-lifecycle.md        # fail-safe 보존 무한 잔존 방지 = observe-only + 사유 + 재알림 동형 프레임
  - templates/scripts/check-workspace-residue-discovery.sh          # 발견 스캐너 (Phase 2 land)
tags:
  - codeforge
  - governance
  - worktree
  - garbage-collection
  - lifecycle
  - no-data-loss
sources:
  - https://man7.org/linux/man-pages/man5/tmpfiles.d.5.html                 # systemd-tmpfiles Age 필드 + x/X 제외 라인 (TTL 선언 + 제외 마커 원형)
  - https://github.com/git/git/blob/master/reflog.c                          # stash refs/stash expire_total=0 (무만료 소스 확정)
  - https://git-scm.com/docs/git-worktree                                    # git worktree prune = metadata-only (실 dir 미삭제)
  - https://specifications.freedesktop.org/basedir-spec/latest/              # XDG RUNTIME_DIR 세션 바인딩 수명 + sticky-bit 보존 마커
  - https://github.com/d-kuro/gwq                                            # worktree.basedir + canonical naming (생성 위치 강제 선행사례)
---

# Ephemeral workspace lifecycle GC — 세션 잔재 수명 규약

## 정의

**세션 잔재(ephemeral residue)** = 작업 수행을 위해 생성되고 완결 후 가치가 소멸하는 파일시스템 산출물. 사후 청소(reactive cleanup)가 아니라 **생성 시점 수명 규약 + 자동 회수 + 완료 게이트 검증**으로 쌓이지 않는 구조를 만드는 것이 본 개념의 목적이다.

**잔재 4분류** (열거 방법·회수 책임 차이가 정책 경계를 결정):

| 분류 | 예 | 열거 방법 | 회수 책임 |
|---|---|---|---|
| (a) 도구-등록형 | 등록 worktree, git stash | `git worktree list --porcelain` / `git stash list` | 도구가 감지 신호는 주지만 **회수는 안 해줌** |
| (b) 규약-위치형 | `~/.claude/worktrees/`, codeforge-scratch | 표준 위치 하위 전량 스캔 | 위치 규약 = 수명 클래스 선언으로 겸용 가능 |
| (c) 미등록 orphan | workspace root `_wt-*`, 독립 clone, 홈 직하 찌꺼기 | **열거 불가 — 발견(discovery) 스캔 필요** | 어떤 도구도 자동 회수 안 함 (표준의 사각 그 자체) |
| (d) 제3자-소유 | harness `%TEMP%\claude` 세션 스크래치 | 위치는 알지만 수명 정책 소유권 외부 | 소유자 자체 GC 존재 여부가 정책 경계 결정 |

## 컨텍스트

기존 표준은 **등록 worktree**(ADR-040 eager + backstop GC)만 다뤘고, 그 외 잔재 클래스는 표준 밖이었다. 외부 기술 사실이 이 공백을 확정한다:

- `git worktree prune` = `$GIT_DIR/worktrees` administrative metadata 만 제거, 실 working directory·미등록 orphan dir 은 절대 안 건드림 → orphan/독립 clone 회수는 **자체 discovery 스캔 필수**.
- git **stash 는 기본 무만료** (`reflog.c` 가 `refs/stash` 를 특별 취급, `expire_total=0`) → 방치 시 무한 축적 확정.
- harness `%TEMP%\claude` 세션 스크래치는 harness 공식 자동 정리 경로 목록에 **미포함**(정리 주체 확인 불가) → 관측-only 취급.

**외부 표준 수렴 8-시스템** (systemd-tmpfiles / Jenkins WorkspaceCleanupThread / GitHub Actions self-hosted / Gradle 캐시 / Bazel disk cache / kubelet image GC / Windows Storage Sense / XDG Base Directory + 생성위치 강제 선행사례 gwq)이 6개 수렴점을 형성한다:

1. **수명은 생성 규약에 선언** (systemd-tmpfiles Age 필드가 원형 — TTL-at-creation).
2. **트리거는 {주기 + 시작-시점 catch-up + 용량 임계} 2+ 중첩** — 종료-시점 훅 단독 의존 사례 없음.
3. **age 는 last-access 계열 최신 timestamp** (수정 시각이 아니라 접근 시각).
4. **보존 예외는 명시 마커** (휴리스틱 아님 — git worktree lock / tmpfiles x·X 제외 라인 / XDG sticky-bit).
5. **용량 상한 백스톱 병행** (age 조건과 독립인 총량 임계 — kubelet watermark / Bazel max_size / Storage Sense low-disk).
6. **사용자 데이터 계열(stash 등)은 자동 삭제 대신 가시화·알림** (git 무만료 = 의도적 사용자 데이터 취급).

## 핵심 규칙

- **TTL-at-creation**: 생성 규약에 수명(클래스)을 선언하고 회수기는 선언만 읽고 동작. (규약-위치형은 위치=클래스로 겸용 가능.)
- **GC 트리거 4형**: ① eager(완결 시점) ② scheduled(주기) ③ **next-session lazy(다음 개시 시)** ④ threshold(용량 임계). 단일 트리거 의존이 아니라 2+ 중첩이 일반형 — 특히 크래시-안전은 다음 세션 개시 경로가 문서상 유일하게 실행이 보장되는 지점.
- **보존 예외(preservation override)**: dirty / unpushed / locked / worktree-pin 은 회수기가 침범하지 못하는 **명시 마커**. 등록·존재 여부 자체는 보존 사유가 아니며, **상태 신호 1+ 양성 또는 판정 불능(INCONCLUSIVE)** 시에만 fail-safe 보존 + 메타파일 사유 기록. mtime 단독 삭제 금지(상태 신호 AND 결합).
- **quarantine-grace**: 삭제 판정분도 즉시 삭제 대신 유예 후 삭제(동시 실행 안전 목적) — git `gc.pruneExpire` 기본 2주 grace 가 원형.
- **aging report**: 보존 예외 항목의 사유 + 나이를 주기 보고하고 임계 초과 시 재알림(지수 backoff + item·reason dedup) — fail-safe 무한 잔존을 막는 기성형. 자동 삭제 기한(TTL 강제 삭제)을 새로 두지 않는다(보존 원칙 역행 = 기각).
- **"지워도 되는가" 최종 판정 = 각 클래스 오너에게 위임**. 본 개념은 잔재 전반의 **발견 / 분류 / 가시화**를 표준화하되, 실제 삭제 authz(등록 worktree = git 경로 + 4-AND / 독립 clone = 삭제 금지 default / loose scratch = age + `.git` 미보유 + canonical / Temp = 관측-only)는 클래스별 오너 규칙에 맡긴다.

## 경계

- **registered worktree lifecycle(ADR-040) 와 인접하나 분리** — 신규 "session ephemeral residue lifecycle" 는 잔재 전반(등록 worktree 를 포함하는 **상위집합**: scratch / Temp / stash / orphan clone / 루트)의 발견·분류·가시화를 담당한다. ADR-040 은 등록 worktree 등록부 scoped(단일 repo), 본 개념은 multi-class filesystem walk.
- **anti-corruption layer**: discovery 는 등록-worktree 판정을 재구현하지 않고 기존 스크립트 결과를 subprocess 위임으로 소비한다(파싱 로직 재구현·circular import 금지). 이것이 두 bounded context 간 ACL.
- **회수 실행 owner 는 여전히 각 클래스 오너**: 본 개념은 판정·가시화 계층이지 삭제 실행 권한을 확대하지 않는다. 제3자-소유(harness Temp)는 소유 정책 확인 전까지 관측-only(삭제 syscall 0).
- **out-of-scope**: 중복/재사용 *측정*(duplication-ratio, rule-of-three)·전역 리팩터링·자동 삭제 강제(stash 자동삭제)는 본 개념 밖.

## 관련 ADR

- **ADR-169** — 세션 잔재 수명 규약 normative SSOT. 본 concept 를 §결정 1 의 concept SSOT 로 명명(4분류 + discovery 스캐너 + orphan 3-분류 + 크래시 보완 트리거 + scratch/Temp/stash 가시화).
- **ADR-040** — registered worktree lifecycle. 본 개념의 상위집합 관계 + anti-corruption layer(§경계).
- **ADR-128** — 완료 단계 정식화. 크래시 보완 트리거 다중화 재해석 SSOT = ADR-169 §결정 4.
- **ADR-045** — Story 완료 회고. residue-clean self-check precondition = ADR-169 §결정 9.
- **ADR-061** — thin-wrapper(8-line bash launcher + Python SSOT). 발견 스캐너 구조 근거.
- **ADR-110** — Task Scheduler. OS 스케줄러 = consumer opt-in 보조 트리거(주 트리거 아님).

## 변경 이력

- 2026-07-26 (CFP-2822 Phase 1) — 신설. ADR-169 세션 잔재 수명 규약 §결정 1 의 concept SSOT. 잔재 4분류 + TTL-at-creation + GC 트리거 4형(2+ 중첩) + 보존 예외 명시 마커 + quarantine-grace + aging report 의 외부 표준(8-시스템) 수렴 모델 codify.
