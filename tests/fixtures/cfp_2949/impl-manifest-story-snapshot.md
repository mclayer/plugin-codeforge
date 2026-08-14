<!--
tests/fixtures/cfp_2949/impl-manifest-story-snapshot.md
  — Story CFP-2949 §8.7 Impl Manifest 의 **동결 스냅샷** (구현리뷰 iter5 시점, stale)

★ 이 파일은 Story 를 추적하지 않는다. 일부러 **stale 한 상태로 동결**한 검사 입력이며,
  `tests/integration/test_scheduled_task_impl_manifest.py` 의 판별 테스트가
  "비교기가 이 선언과 실측의 불일치를 실제로 잡는가" 를 이 자료로 확인한다.
  Story 가 갱신돼도 이 파일은 그대로 둔다 — 갱신하면 판별 근거가 사라진다.

출처: mclayer/codeforge-internal-docs `wrapper/stories/CFP-2949.md` §8.7
      (구현리뷰 iter5 FIX 진입 시점 본문 verbatim, 읽기 전용 복사)
-->

### 8.7 Impl Manifest

> **행수 지표 규약 (단일 지표 — 섞지 말 것)**: 아래 표의 `N행` = `git diff --stat origin/main...HEAD` 의 **파일별 변경 행수**다. 따라서 **신규 = 파일 전체 행수**, **수정 = 추가 + 삭제 행수**(예: `docs/orchestrator-playbook.md` 27 = 21 추가 + 6 삭제). 파일의 현재 전체 행수(`wc -l`)와 혼동하지 말 것 — 수정 파일에서 둘은 다르다(`tests/conftest.py` 는 표의 34행 = 추가분이고 `wc -l` 은 94다). 본 절의 수치는 전건 **동결 HEAD `9e3235401`**(FIX4 봉합 3커밋 착지 후) 실측이다.
>
> **★ stale 이력 (구현리뷰 iter4 F-A — 은폐 금지)**: 직전 판본은 `7243714db` 기준 **18 files / 4971 insertions** 였다. **그 SHA 로는 정확한 수치**였으나 이후 FIX2 4커밋 + FIX4 3커밋이 착지해 stale 이 됐고, 그 사이 신설된 `tests/integration/test_scheduled_task_watchdog_hook.py` 는 Story 전역 **0회** 등장이었다. 본 판본에서 전 행 재실측 + 누락 2행(watchdog·dispatch_path) 추가로 정산한다. 재발 방지는 규약 자체에 있다 — **manifest 는 Story 의 마지막 커밋 이후 갱신**한다.

| 파일 | 구분 | 역할 |
|---|---|---|
| `.claude-plugin/plugin.json` | 수정 | 버전 6.128.2 → 6.129.1 (§8.1 주석 참조 — CFP-2944 §6.129.0 점유 회피) |
| `.github/workflows/cfp2949-scheduled-task-test.yml` | 신규 | 신규 pytest CI 배선 (35행, **7파일** 인자) — born-dead 차단 (§8.2-C) |
| `archive/adr/ADR-172-local-scheduled-task-residue-observation.md` | 수정 | §결정 8·9·10 신설 + Amendment 1 (128행) — wrapper 오라클 표면 제공 (AC-5·AC-12·AC-4) |
| `docs/architecture/codeforge-family.md` | 수정 | C4 Container 경계·데이터 흐름 추가 (9행) |
| `docs/orchestrator-playbook.md` | 수정 | 비대화형 호출 계약 신설 + 6 hit 건별 정정 (27행) |
| `hooks/hooks.json` | 수정 | SessionStart entry 1개 추가 (5행) |
| `hooks/session-start-scheduled-task-watchdog` | 신규 | SessionStart 생존 감시 — heartbeat 판독 전용·부수효과 0 (87행) |
| `scripts/lib/scheduled_task_reconcile.py` | 신규 | 결정론 CLI — 관측·dedup·필터·렌더·발화 (829행 — 2차 봉합 반영) |
| `skills/worktree-lifecycle/SKILL.md` | 수정 | 중립 pointer 1행 (역참조 불변식 유지) |
| `tests/conftest.py` | 수정 | heartbeat 격리 autouse fixture `isolated_scheduled_task_heartbeat_file` (34행) — in-process `sut.run()` 이 실 사용자 상태를 오염시키지 않도록 `SCHEDULED_TASK_HEARTBEAT_FILE` 을 테스트 tmp 로 고정 (§8.2-E) |
| `tests/fixtures/cfp_2949/README.md` | 신규 | 테스트 fixture 가이드 (51행) |
| `tests/fixtures/cfp_2949/ac1-measurement-declaration.json` | 신규 | AC-1 measured=false 선언 (7행) |
| `tests/fixtures/cfp_2949/fuzz-corpus/paths.txt` | 신규 | 경로 정규화 fuzz 코퍼스 (33행) |
| `tests/integration/test_scheduled_task_ac_matrix.py` | 신규 | AC 정합 행렬 테스트 (1171행, 21 tests) |
| `tests/integration/test_scheduled_task_dispatch_path.py` | 신규 | **`run()` 발화 경로 완주 harness** (486행, 7 tests) — 채널 조회 실패 가드·dedup 필터·신규 0건 가드·상한 절단·렌더·발화·발화실패 가드 (구현리뷰 iter4 F-C 봉합). 주입점 = 기존 `_gh` 포트 1개, production 표면 신설 0 |
| `tests/integration/test_scheduled_task_dynamic_roster.py` | 신규 | 동적 로스터 계약 테스트 (1178행, 14 tests) |
| `tests/integration/test_scheduled_task_stateful.py` | 신규 | 상태 유지 불변식 테스트 (1119행, 13 tests) |
| `tests/integration/test_scheduled_task_watchdog_hook.py` | 신규 | **SessionStart watchdog 판독 오라클** (276행, 5 tests) — ①absent ②stale ③malformed ④fresh(대조군) ⑤bypass (FIX2 F-6 신설). ★ 직전 manifest 판본에 **누락**돼 있었다 |
| `tests/test_scheduled_task_stop_flag.py` | 신규 | 정지 플래그 스모크 테스트 (246행, 9 tests) |
| `tests/unit/test_scheduled_task_reconcile_unit.py` | 신규 | CLI reconcile 단위 테스트 (439행, 30 tests) |

**산출물 총계** (`git diff --stat origin/main...HEAD`, 동결 HEAD `9e3235401` 실측): **20 files changed, 6155 insertions(+), 8 deletions(-)**

**테스트 수집** (`pytest --collect-only -q` 파일별 실측, 동결 HEAD `9e3235401`): 7 파일 **99건** = ac_matrix 21 · dispatch_path 7 · dynamic_roster 14 · stateful 13 · watchdog_hook 5 · stop_flag 9 · unit 30. CI 인자 `-m "not requires_golden"` 적용 시 **선택 98 / deselected 1**(AC-1 live 축 — §8.4).

**★ 스위트 실행 재실측 (동결 HEAD `9e3235401`, 2026-08-14, 로컬 워크스테이션)**: CI 와 동일한 **7파일**·동일 mark 인자(`-m "not requires_golden"`)로 **`98 passed, 1 deselected`** (102.30s). 선행 baseline = `7243714db` **5파일 연속 2회 `84 passed, 1 deselected`**(94.65s / 95.11s). 증가분 **+14** 의 귀속(함수명 diff 실측): watchdog_hook **5**(FIX2 F-6 신설 파일) + dispatch_path **7**(FIX4 F-C 신설 파일) + `test_ac2_github_write_zero_on_empty_observation` **1**(FIX1 F-1 종료 경로 2분할) + `test_concurrency_oracle4_nonatomic_writer_is_torn` **1**(FIX2 F-4 oracle④ 대조군). 아래 84-건 서술은 **선행 baseline 시점의 기록**으로 보존한다. 직전 판본이 이 자리에 기재했던 **`83 passed, 1 failed`** — `test_perf_baseline_sustained_p50_stability` (`TestPerfBaseline`) 의 batch 간 p50 비 `ratio < 2.0` 단언에서 실측 ratio 3.024, 단독 재실행 FAIL/FAIL/PASS — 는 **관측이 철회된 것이 아니다**. 그 부하 민감 단언이 커밋 `7243714db` 에서 **비차단 기록으로 강등**되어 판정면에서 사라진 결과이며, 원 관측(부하 민감 간헐 실패)은 오히려 그 강등의 **근거로 채택**됐다.

**그 강등의 정직한 지위 (over-read 차단 · 구현리뷰 iter2 F-3 반영 정정)**: 강등 = **판정 제거이지 측정 제거가 아니다** — Change Plan §8.3 이 요구하는 baseline 기록(p50 / p95 / max / min / samples + 한계값 + note)은 두 테스트 모두 유지하고, 각 기록에 `verdict_role: "none — 비차단 기록"` 을 명시해 판정자가 아님을 못박았다. ★ **직전 판본이 이 자리에 적었던 *"실 teeth 는 §8.5.1 자원 축이 무접촉으로 전담한다"* 는 거짓이며 철회한다** — 두 축은 disjoint 다. 실증(ArchitectPL firsthand, 2026-08-14): 할당 0 인 CPU-burn 을 삽입하자 **소요가 1504배 늘었는데 `gc_net` 0 · `tracemalloc_net` 불변**이었다. `gc.get_objects()` 와 `tracemalloc` 은 **할당량을 재지 지연을 재지 않는다.** ⇒ 정확한 서술은 **"시간 축은 (i) 정지·사망 class 만 운영 watchdog 이 사후 탐지하고, (ii) 완주하되 43200s 초과 class 는 테스트·운영 양쪽 미판정이며, (iii) 비례 회귀는 계약 대상이 아니다"**(Change Plan §8.3 class 표). 따라서 위 `84 passed` 를 **"wall-clock 축이 검증됐다" 로 읽어서는 안 되며**, **"자원 축이 대신 검증했다" 로 읽어서도 안 된다.** 잔여 = §8.3 이 지명하는 안전마진에 **판정자가 없다**(Change Plan §9.5 행 14 에 선언 — 그 선언은 강제하지 않는다).

