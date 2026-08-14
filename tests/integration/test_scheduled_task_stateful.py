#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# tests/integration/test_scheduled_task_stateful.py — §8.5 Stateful + §8.3 Perf Baseline
#
# §8.5.1 long-running invariant: 200-iteration sustained loop (duration/RSS 무증가)
# §8.5.2 restart recovery: tick K회 건너뛰고 K개 추가 → 1회 호출 → K 전부 보고
# §8.5.3 idempotency replay: 같은 잔재 2-3회 → 보고 1개
#
# §8.3 Perf Baseline: p95 < 주기 × 0.5 (wall-clock 한계 43200s, 판별력 0)
#   → 실측 p95 기록 + §8.5.1 단조 무증가를 실 teeth 로 삼음

import time
import os
import tempfile
import pytest
import subprocess
from pathlib import Path
from unittest import mock
import sys
import json
import gc
import tracemalloc

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts" / "lib"))

import scheduled_task_reconcile as sut


# ═══════════════════════ 실 사용자 상태 격리 헬퍼 (테스트 seam) ═══════════════════
def _real_heartbeat_state():
    """실 사용자 heartbeat 파일 스냅샷 (mtime_ns, size). 부재 = None.

    ★ sut.HEARTBEAT_FILE 은 import 시점 expanduser("~") 로 확정되므로 HOME override 로는
      격리되지 않는다. 테스트는 SCHEDULED_TASK_HEARTBEAT_FILE 로 기록 대상을 tmpdir 로
      돌리고, 이 스냅샷으로 실 경로 무접촉을 단언한다 — 테스트가 스케줄 작업의 생존
      신호를 위조하면 watchdog 이 구조적 false-negative 가 된다(ADR-172 §결정 6)."""
    try:
        st = os.stat(sut.HEARTBEAT_FILE)
    except OSError:
        return None
    return (st.st_mtime_ns, st.st_size)


def _isolated_env(heartbeat_path):
    """기존 env 상속 + heartbeat 기록 대상만 tmpdir 로 치환한 subprocess env."""
    env = dict(os.environ)
    env[sut.ENV_HEARTBEAT_FILE] = str(heartbeat_path)
    return env


def _write_gh_stub(dirpath):
    """`STR_GH_BIN` 로 주입할 gh stub 을 만들고 `(명령문자열, 호출로그 경로)` 반환.

    ★ 실 GitHub 네트워크 호출 차단용 mock-seam. SUT 는 `STR_GH_BIN`(공백분리 명령)을
      이미 지원하는데 tests/** 에서 그 seam 을 쓰는 곳이 0건이라 `run(--channel ...)`
      경로가 실 `gh issue view` 를 발사하고 있었다 — 그 봉합.

    ★ UTF-8 못박기(load-bearing): Windows 기본 인코딩(cp949)으로 stub 을 쓰면 한글이
      깨지거나 조용히 빈 결과가 나와 오판을 유발한 전례가 있다. 파일 저작·stub 자신의
      stdout·호출 로그를 모두 UTF-8 로 고정한다.

    Returns:
        (gh_cmd, log_path) — gh_cmd 는 `"<python> <stub.py>"` 형태(공백분리 1개 스페이스).
    """
    log_path = os.path.join(dirpath, "gh-stub-calls.log")
    stub_path = os.path.join(dirpath, "gh_stub.py")
    stub_src = (
        "#!/usr/bin/env python3\n"
        "# QADev gh stub — 네트워크 호출 0. 호출 기록 후 최소 JSON 응답.\n"
        "import json, sys\n"
        "if hasattr(sys.stdout, 'reconfigure'):\n"
        "    sys.stdout.reconfigure(encoding='utf-8', errors='replace')\n"
        "LOG = %r\n"
        "with open(LOG, 'a', encoding='utf-8', newline='\\n') as fh:\n"
        "    fh.write('\\t'.join(sys.argv[1:]) + '\\n')\n"
        "args = sys.argv[1:]\n"
        "if 'view' in args and '--json' in args:\n"
        "    print(json.dumps({'comments': []}))\n"
        "sys.exit(0)\n"
    ) % (log_path,)
    with open(stub_path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(stub_src)

    # SUT `_gh` 는 shlex.split(posix=(os.name != 'nt')) 로 토큰화한다 — 공백 포함 경로는
    #   Windows 에서 인용부호가 토큰에 남아 깨진다. 전제 위반 시 조용한 오판 대신 즉시 실패.
    assert " " not in sys.executable and " " not in stub_path, (
        f"stub 주입 전제 위반(경로에 공백): python={sys.executable!r} stub={stub_path!r}"
    )
    return "%s %s" % (sys.executable, stub_path), log_path


class TestLongRunningInvariant:
    """§8.5.1 long-running invariant: 반복 실행 시 자원·시간 단조 무증가."""

    def test_long_running_200_iterations_no_resource_growth(self):
        """200-iteration sustained loop — 자원 누적(누수) 부재를 **자원 축으로** 검증.

        ★ 축 지위 (Story §8.2-F 정직 강등 이행):
          - **wall-clock = 비차단 기록**. 이 축은 호스트 부하에 민감해 전체 스위트 동시
            실행 시 ratio 3.05 로 재현 FAIL 한다. Story §8.2-F 는 이 축을 "보조로 정직
            강등" 한다고 **선언**했는데 코드는 bare assert(=blocking)로 남아 선언↔코드가
            불일치였다. 여기서 선언 쪽으로 통일한다 — 측정값은 반드시 기록하되 판정하지
            않는다(측정 삭제 아님).
          - **자원 축(gc / tracemalloc) = blocking teeth**. 약화 없음(기존 비율 단언 유지)
            + **누적 성장 상한**을 추가한다. 비율 단언은 per-iteration Δ 비교라 *일정
            속도* 누수(매 호출 동일량 누적)에 ratio≈1.0 이 되어 눈이 먼다 — 누적 축이
            그 사각을 덮는다.

        ★ 실측 기준:
          - 비율 축 (Orchestrator 3-trial): gc Δ ratio=0.92, tracemalloc Δ ratio=0.86
          - 누적 축 (QADev 3-trial, warmup 20 이후 net):
              gc 객체 net = 0 / 0 / 0 개      (spread 0)
              tracemalloc net = 50.4 / 50.1 / 51.7 KB  (측정 루프 자체의 누적 리스트분)
            누수 대조군(호출당 객체 1000개): gc net=179개, tracemalloc net=4400.4KB
          - 임계값: gc net <= 100 개 / tracemalloc net <= 512 KB
            (정상 실측 대비 각각 +100 / 10배 여유, 누수 대조군은 각각 1.8배 / 8.6배 초과)
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = tmpdir
            scratch_root = os.path.join(tmpdir, "scratch")
            temp_root = os.path.join(tmpdir, "temp")
            os.makedirs(scratch_root, exist_ok=True)
            os.makedirs(temp_root, exist_ok=True)

            durations = []
            gc_deltas = []  # 각 iteration의 gc 객체 변화
            tracemalloc_deltas = []  # 각 iteration의 tracemalloc 변화
            gc_levels = []  # 각 iteration 종료 시 gc 객체 **절대 수준** (누적 축)
            mem_levels = []  # 각 iteration 종료 시 traced memory **절대 수준** KB (누적 축)

            tracemalloc.start()

            for i in range(200):
                # Act: collect_observations 호출 (스캐너 3종 observe-only)
                # ★ tmpdir 격리: scan_roots 명시적 주입 (실제 홈 스캔 0)
                gc.collect()  # 측정 전 정리
                gc_before = len(gc.get_objects())
                tracemalloc.reset_peak()

                start = time.time()
                scan_roots = [
                    {"path": os.path.join(tmpdir, "worktrees"), "mode": "cross-check-only", "source": "worktrees-base"},
                    {"path": os.path.join(tmpdir, "workspace"), "mode": "discover+classify", "source": "workspace-root"},
                    {"path": os.path.join(tmpdir, "home"), "mode": "discover+classify", "source": "home-direct"},
                ]
                obs = sut.collect_observations(
                    repo_root=repo_root,
                    scan_roots=scan_roots,
                    scratch_root=scratch_root,
                    temp_root=temp_root,
                )
                elapsed = time.time() - start

                gc_after = len(gc.get_objects())
                _, peak_tracemalloc = tracemalloc.get_traced_memory()

                durations.append(elapsed)
                gc_deltas.append(gc_after - gc_before)
                tracemalloc_deltas.append(peak_tracemalloc / 1024)  # KB로 변환

                # 누적 축 표본 — 수집 후 gc.collect() 로 회수 가능분을 걷어낸 **잔존** 수준
                gc.collect()
                gc_levels.append(len(gc.get_objects()))
                current_tracemalloc, _ = tracemalloc.get_traced_memory()
                mem_levels.append(current_tracemalloc / 1024)

            tracemalloc.stop()

            # ─────────────────────────────────────────────────────────────
            # 기록 1: wall-clock — **비차단**(Story §8.2-F 정직 강등). 판정하지 않는다.
            # ─────────────────────────────────────────────────────────────
            first_half = sorted(durations[:100])
            second_half = sorted(durations[100:])

            p95_first = first_half[int(len(first_half) * 0.95)]
            p95_second = second_half[int(len(second_half) * 0.95)]
            wall_ratio = (p95_second / p95_first) if p95_first > 0 else float("nan")

            # ★ 이 축은 호스트 부하에 종속이라 blocking 단언의 근거가 없다(전체 스위트
            #   동시 실행에서 ratio 3.05 재현 FAIL). 측정은 유지하고 판정만 뗀다 —
            #   blocking teeth 는 아래 자원 축이 전담한다.
            print(f"\n[wall-clock advisory · 비차단] p95_first={p95_first:.4f}s "
                  f"p95_second={p95_second:.4f}s ratio={wall_ratio:.3f} "
                  f"(참고 기준 1.5 — 초과해도 FAIL 아님, 부하 민감 축)")
            if wall_ratio > 1.5:
                print(f"[wall-clock advisory] 참고 기준 초과 (ratio={wall_ratio:.3f}) — "
                      f"호스트 부하 신호. 판정 축 아님.")

            # ─────────────────────────────────────────────────────────────
            # Assert 2: gc 객체 수 단조성 (실 teeth 1/2)
            # ─────────────────────────────────────────────────────────────
            # 전반부(0-99)와 후반부(100-199) gc 증가분 비교
            first_half_gc_delta = sum(gc_deltas[:100]) / 100  # 평균
            second_half_gc_delta = sum(gc_deltas[100:]) / 100  # 평균

            # 후반부 평균 증가가 전반부 평균 증가를 크게 초과하지 않아야 함
            # (지속 누적 = gc_delta_second > gc_delta_first 지속)
            assert second_half_gc_delta <= first_half_gc_delta * 1.2, (
                f"gc 객체 후반부 누적 (누수 신호): 전반부 Δ={first_half_gc_delta:.1f}, "
                f"후반부 Δ={second_half_gc_delta:.1f}, 비율={second_half_gc_delta/first_half_gc_delta:.2f}"
            )

            # ─────────────────────────────────────────────────────────────
            # Assert 3: tracemalloc 메모리 단조성 (실 teeth 2/2)
            # ─────────────────────────────────────────────────────────────
            first_half_tracemalloc_delta = sum(tracemalloc_deltas[:100]) / 100  # 평균, KB
            second_half_tracemalloc_delta = sum(tracemalloc_deltas[100:]) / 100  # 평균, KB

            # 후반부 평균 증가가 전반부 평균 증가를 크게 초과하지 않아야 함
            assert second_half_tracemalloc_delta <= first_half_tracemalloc_delta * 1.8, (
                f"tracemalloc 후반부 누적 (누수 신호): 전반부 Δ={first_half_tracemalloc_delta:.1f}KB, "
                f"후반부 Δ={second_half_tracemalloc_delta:.1f}KB, 비율={second_half_tracemalloc_delta/first_half_tracemalloc_delta:.2f}"
            )

            # ─────────────────────────────────────────────────────────────
            # Assert 4·5: 자원 **누적 성장 상한** (실 teeth — 일정 속도 누수 사각 봉합)
            # ─────────────────────────────────────────────────────────────
            # ★ 위 비율 단언(Assert 2/3)은 per-iteration Δ 비교라 매 호출 동일량을
            #   누적하는 누수에서 ratio≈1.0 이 되어 눈이 먼다. 워밍업(20) 이후의
            #   **절대 수준 순증**을 상한으로 구속해 그 사각을 덮는다.
            WARMUP = 20                 # 캐시 워밍(_workspace_prefix_cache 등) 정착 구간
            GC_NET_LIMIT = 100          # 실측 net=0 (3-trial, spread 0) / 누수 대조군 179
            MEM_NET_LIMIT_KB = 512      # 실측 net≈50KB (3-trial) / 누수 대조군 4400KB

            gc_net = gc_levels[-1] - gc_levels[WARMUP]
            mem_net = mem_levels[-1] - mem_levels[WARMUP]

            assert gc_net <= GC_NET_LIMIT, (
                f"gc 객체 **누적** 순증 {gc_net}개 > 상한 {GC_NET_LIMIT}개 (누수 신호). "
                f"level[{WARMUP}]={gc_levels[WARMUP]} → level[-1]={gc_levels[-1]}"
            )
            assert mem_net <= MEM_NET_LIMIT_KB, (
                f"traced memory **누적** 순증 {mem_net:.1f}KB > 상한 {MEM_NET_LIMIT_KB}KB "
                f"(누수 신호). level[{WARMUP}]={mem_levels[WARMUP]:.1f}KB → "
                f"level[-1]={mem_levels[-1]:.1f}KB"
            )

            # 측정값 기록 (분석용)
            perf_record = {
                "test": "test_long_running_200_iterations_no_resource_growth",
                "wall_clock_advisory_nonblocking": {
                    "p95_first_half_seconds": f"{p95_first:.4f}",
                    "p95_second_half_seconds": f"{p95_second:.4f}",
                    "ratio": f"{wall_ratio:.3f}",
                    "verdict_role": "none — 비차단 기록 (Story §8.2-F 정직 강등)",
                },
                "cumulative_net_growth": {
                    "warmup_index": WARMUP,
                    "gc_objects_net": gc_net,
                    "gc_objects_limit": GC_NET_LIMIT,
                    "tracemalloc_net_kb": f"{mem_net:.1f}",
                    "tracemalloc_limit_kb": MEM_NET_LIMIT_KB,
                },
                "gc_objects": {
                    "first_half_avg_delta": f"{first_half_gc_delta:.1f}",
                    "second_half_avg_delta": f"{second_half_gc_delta:.1f}",
                    "ratio": f"{second_half_gc_delta/first_half_gc_delta:.3f}",
                },
                "tracemalloc_kb": {
                    "first_half_avg_delta_kb": f"{first_half_tracemalloc_delta:.1f}",
                    "second_half_avg_delta_kb": f"{second_half_tracemalloc_delta:.1f}",
                    "ratio": f"{second_half_tracemalloc_delta/first_half_tracemalloc_delta:.3f}",
                },
            }
            print(f"\n[Long-Running Invariant] {json.dumps(perf_record, indent=2)}")


class TestRestartRecovery:
    """§8.5.2 restart recovery: subprocess 재기동 후 누락 복구.

    K회 건너뛴 tick 동안 K개 잔재 추가 → 1회 호출 → K 전부 보고.
    """

    def test_restart_recovery_reports_accumulated(self):
        """재기동 후 누적 잔재 K개 보고.

        AC-9 reconcile 무상태성: 매 실행이 현재 상태 전량을 재관측.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = tmpdir
            scratch_root = os.path.join(tmpdir, "scratch")
            temp_root = os.path.join(tmpdir, "temp")
            worktree_root = os.path.join(tmpdir, "worktrees")
            home_root = os.path.join(tmpdir, "home")
            os.makedirs(scratch_root, exist_ok=True)
            os.makedirs(temp_root, exist_ok=True)
            os.makedirs(worktree_root, exist_ok=True)
            os.makedirs(home_root, exist_ok=True)

            # Arrange: 1차 스캔 (정보성 행들만)
            scan_roots = [
                {"path": worktree_root, "mode": "cross-check-only", "source": "worktrees-base"},
                {"path": os.path.join(tmpdir, "workspace"), "mode": "discover+classify", "source": "workspace-root"},
                {"path": home_root, "mode": "discover+classify", "source": "home-direct"},
            ]
            obs1 = sut.collect_observations(
                repo_root=repo_root,
                scan_roots=scan_roots,
                scratch_root=scratch_root,
                temp_root=temp_root,
            )
            # 잔재 0건일 때도 scratch 정보성 행 1개는 항상 존재 (관찰점)
            # 따라서 obs1 >= 1 이 아니라 worktree class 관측 0 + scratch class 정보성 1행
            worktree_obs_before = [o for o in obs1 if o.cls == "worktree"]
            assert len(worktree_obs_before) == 0, (
                f"잔재 추가 전 worktree 관측 0 기대, 실제: {len(worktree_obs_before)}"
            )

            # "K회 건너뛴" 시뮬레이션 = 잔재 K=5개 생성
            for i in range(5):
                old_dir = os.path.join(worktree_root, f"old-stale-{i}")
                os.makedirs(old_dir, exist_ok=True)
                Path(os.path.join(old_dir, "marker.txt")).touch()

            # Act: 재기동 후 1회 호출 (상태 무의존 reconcile)
            obs2 = sut.collect_observations(
                repo_root=repo_root,
                scan_roots=scan_roots,
                scratch_root=scratch_root,
                temp_root=temp_root,
            )

            # Assert: 누적 worktree 5개 모두 보고 + scratch 정보성 유지
            worktree_obs_after = [o for o in obs2 if o.cls == "worktree"]
            assert len(worktree_obs_after) == 5, (
                f"재기동 후 worktree 정확히 5개 기대, 실제: {len(worktree_obs_after)}"
            )

            # worktree 디렉터리명 확인 (주입한 이름과 일치)
            reported_paths = [o.display_path for o in worktree_obs_after]
            for i in range(5):
                # display_path 에 old-stale-{i} 포함 확인
                found = any(f"old-stale-{i}" in path for path in reported_paths)
                assert found, (
                    f"worktree old-stale-{i} 보고 미발견 (reconcile 완결성 위반)"
                )

    def test_restart_recovery_lock_skip(self):
        """축 격리(axis isolation): 한 축 예외 해도 다른 축 관측 살아남음.

        실재 계약: collect_observations 는 3축 독립 관측 모델.
        각 축(workspace/scratch/temp) 이 예외를 던져도 exit 하지 않고
        정상 축의 관측은 반환된다(fail-safe 설계).

        ★ 계약 교체 사유: SUT 에 lock 기능 없음 (존재하지 않는 계약 폐지).
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            scratch_root = os.path.join(tmpdir, "scratch")
            temp_root = os.path.join(tmpdir, "temp")
            worktree_root = os.path.join(tmpdir, "worktrees")
            workspace_root = os.path.join(tmpdir, "workspace")
            os.makedirs(scratch_root, exist_ok=True)
            os.makedirs(temp_root, exist_ok=True)
            os.makedirs(worktree_root, exist_ok=True)
            os.makedirs(workspace_root, exist_ok=True)

            # Arrange: 정상 worktree 축 잔재 주입 (살아남을 축)
            os.makedirs(os.path.join(worktree_root, "normal"), exist_ok=True)
            Path(os.path.join(worktree_root, "normal", "marker.txt")).touch()

            # Arrange: temp 축을 예외 발생하도록 monkeypatch
            # (다른 정상 축들은 정상 호출 → 관측 살아남음)
            def failing_observe_temp(*args, **kwargs):
                """temp 관측 축을 의도적으로 실패."""
                raise RuntimeError("temp 축 관측 의도적 실패 (축 격리 테스트)")

            scan_roots = [
                {"path": worktree_root, "mode": "cross-check-only", "source": "worktrees-base"},
                {"path": workspace_root, "mode": "discover+classify", "source": "workspace-root"},
                {"path": os.path.join(tmpdir, "home"), "mode": "discover+classify", "source": "home-direct"},
            ]

            # Act: temp 축 예외 + worktree/workspace/scratch 축 정상 → 부분 관측 반환
            with mock.patch.object(sut, "_observe_temp", side_effect=failing_observe_temp):
                try:
                    obs = sut.collect_observations(
                        repo_root=tmpdir,
                        scan_roots=scan_roots,
                        scratch_root=scratch_root,
                        temp_root=temp_root,
                    )
                except Exception as e:
                    pytest.fail(
                        f"축 격리 위반: workspace 축 예외가 전 collect_observations 를 중단 "
                        f"(fail-safe 설계 위반). 예외: {e}"
                    )

            # Assert (ㄱ): 축 격리 성공 — 예외가 전파되지 않고 결과 반환
            assert isinstance(obs, (list, tuple)), (
                "축 격리 (ㄱ): collect_observations 는 항상 list|tuple 반환 (axis failure 해도)"
            )

            # Assert (ㄴ): 살아남은 축의 관측이 실제로 반환됨 (non-empty)
            # ★ 핵심: temp 축이 죽어도 worktree/scratch 축의 관측은 살아남음
            worktree_obs = [o for o in obs if o.cls == "worktree"]
            scratch_obs = [o for o in obs if o.cls == "scratch"]
            temp_obs = [o for o in obs if o.cls == "temp"]

            # worktree 축은 정상 호출 → 주입한 "normal" 잔재 보고됨
            assert len(worktree_obs) > 0, (
                f"축 격리 (ㄴ-worktree): temp 실패해도 worktree 관측 살아나야 함, "
                f"실제: {len(worktree_obs)}"
            )

            # worktree 관측에 주입한 "normal" 디렉터리명 포함 확인
            reported_paths = [o.display_path for o in worktree_obs]
            found_normal = any("normal" in path for path in reported_paths)
            assert found_normal, (
                f"축 격리 (ㄴ-worktree-content): worktree 'normal' 디렉터리 미발견, "
                f"보고됨: {reported_paths}"
            )

            # scratch 축도 정상 호출 → 정보성 행 포함
            assert len(scratch_obs) >= 1, (  # scratch 는 항상 최소 정보성 1행
                f"축 격리 (ㄴ-scratch): scratch 관측 부재 (축 격리 불완전), "
                f"실제: {len(scratch_obs)}"
            )

            # temp 축은 실패 → 관측 부재 (기대)
            assert len(temp_obs) == 0, (
                f"축 격리 (ㄷ-temp-excluded): temp 축 실패로 temp 관측 0 기대, "
                f"실제: {len(temp_obs)}"
            )


class TestIdempotencyReplay:
    """§8.5.3 idempotency replay: 같은 잔재 2-3회 반복 → 보고 1개."""

    def test_idempotency_same_observations_single_report(self):
        """동일 관측 N회(2-3회) → 발화 1개 (dedup)."""
        obs = sut.Observation(
            cls="test",
            display_path="~/.claude/worktrees/same",
            declared="decl",
            measured="meas",
            mismatch=False,
        )

        # Act: 같은 관측 3회 렌더
        key_set = set()
        for _ in range(3):
            key = sut.dedup_key(obs)
            key_set.add(key)

        # Assert: 고유 key = 1 (발화 1개 기대)
        assert len(key_set) == 1, f"고유 key 는 1개 기대, 실제: {len(key_set)}"


# ═══════════════════════════════ Perf Baseline §8.3 ═══════════════════════
class TestPerfBaseline:
    """§8.3 Perf Baseline: p95 < 주기 × 0.5.

    ★ 정직 천장:
      - 주기 = Daily (86400s)
      - 한계 = 43200s (반주기)
      - 실제 p95 ≪ 한계 (판별력 사실상 0)
      - 실 teeth = §8.5.1 단조 무증가 + 명시 측정값 기록
    """

    def test_perf_baseline_p95_within_limit(self):
        """p95 실행소요 < 43200s (한계) — 측정값 기록."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = tmpdir
            scratch_root = os.path.join(tmpdir, "scratch")
            temp_root = os.path.join(tmpdir, "temp")
            worktree_root = os.path.join(tmpdir, "worktrees")
            home_root = os.path.join(tmpdir, "home")
            os.makedirs(scratch_root, exist_ok=True)
            os.makedirs(temp_root, exist_ok=True)
            os.makedirs(worktree_root, exist_ok=True)
            os.makedirs(home_root, exist_ok=True)
            durations = []

            scan_roots = [
                {"path": worktree_root, "mode": "cross-check-only", "source": "worktrees-base"},
                {"path": os.path.join(tmpdir, "workspace"), "mode": "discover+classify", "source": "workspace-root"},
                {"path": home_root, "mode": "discover+classify", "source": "home-direct"},
            ]

            # 기본 성능 샘플: 100회
            for i in range(100):
                start = time.time()
                obs = sut.collect_observations(
                    repo_root=repo_root,
                    scan_roots=scan_roots,
                    scratch_root=scratch_root,
                    temp_root=temp_root,
                )
                elapsed = time.time() - start
                durations.append(elapsed)

            sorted_dur = sorted(durations)
            p95 = sorted_dur[int(len(sorted_dur) * 0.95)]
            p50 = sorted_dur[int(len(sorted_dur) * 0.50)]

            # Assert: 한계 (명시 이유: 판별력 0)
            assert p95 < 43200, f"p95 한계 exceed (판별력 부재), 실측: {p95:.3f}s"

            # 측정값 기록 (분석용)
            perf_record = {
                "test": "collect_observations",
                "samples": len(durations),
                "p50_seconds": p50,
                "p95_seconds": p95,
                "max_seconds": max(durations),
                "min_seconds": min(durations),
                "daily_period_seconds": 86400,
                "baseline_threshold_seconds": 43200,
                "note": "wall-clock 한계로 인해 판별력 = 0. 실 teeth = §8.5.1 단조 무증가.",
            }

            # 로그 출력 (실제 보고에 포함)
            print(f"\n[Perf Baseline] {json.dumps(perf_record, indent=2)}")

    def test_perf_baseline_sustained_p50_stability(self):
        """Sustained p50 안정성 — 반복 샘플링에서 variance 낮음.

        단조 무증가 검증 (§8.5.1 에서도 수행).
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = tmpdir
            scratch_root = os.path.join(tmpdir, "scratch")
            temp_root = os.path.join(tmpdir, "temp")
            worktree_root = os.path.join(tmpdir, "worktrees")
            home_root = os.path.join(tmpdir, "home")
            os.makedirs(scratch_root, exist_ok=True)
            os.makedirs(temp_root, exist_ok=True)
            os.makedirs(worktree_root, exist_ok=True)
            os.makedirs(home_root, exist_ok=True)

            scan_roots = [
                {"path": worktree_root, "mode": "cross-check-only", "source": "worktrees-base"},
                {"path": os.path.join(tmpdir, "workspace"), "mode": "discover+classify", "source": "workspace-root"},
                {"path": home_root, "mode": "discover+classify", "source": "home-direct"},
            ]

            # 5개 batch × 40 iteration = 200 총
            batches = []
            for batch_idx in range(5):
                durations_batch = []
                for i in range(40):
                    start = time.time()
                    obs = sut.collect_observations(
                        repo_root=repo_root,
                        scan_roots=scan_roots,
                        scratch_root=scratch_root,
                        temp_root=temp_root,
                    )
                    elapsed = time.time() - start
                    durations_batch.append(elapsed)
                p50_batch = sorted(durations_batch)[20]
                batches.append(p50_batch)

            # Assert: batch 간 p50 무증가 추세
            for i in range(1, len(batches)):
                # 허용 오차: 1.2배 이내 증가 허용 (자연 변동)
                ratio = batches[i] / batches[i-1] if batches[i-1] > 0 else 1.0
                # 느슨한 검증 (실제 판별력은 §8.5.1)
                assert ratio < 2.0, (
                    f"batch {i} p50 급증: {batches[i]:.3f}s (이전: {batches[i-1]:.3f}s)"
                )


# ═══════════════════════════════ Integration: Long-running CLI Invocation
class TestLongRunningCLIInvocation:
    """§8.5 long-running: CLI 반복 호출 (subprocess 기반)."""

    def test_cli_invocation_sustained_10_iterations(self):
        """CLI **10회** 반복 호출 — exit code 안정(INV-F) ∧ 실 heartbeat 무접촉.

        ★ 반복수 10 의 근거 (선언면 승격 — P1-5):
          이전 판본은 함수명이 `..._200_iterations` 인데 본문은 `range(10)` 이었고,
          그 차이는 인라인 주석(`# 실제는 200이지만 CI 시간 제약`)에만 있었다. 이름과
          docstring 은 **선언면**이므로 실제와 어긋나면 그 자체가 결함이다.
          여기서는 실제(10)에 맞춰 이름을 정정하고, 근거를 선언면으로 올린다:
          이 테스트의 1회 호출은 subprocess 기동 + 관측 1사이클이라 200회면 CI wall-clock
          예산을 초과한다. **in-process 200-iteration 축은
          `test_long_running_200_iterations_no_resource_growth` 가 이미 전담**하므로
          본 테스트의 목적은 반복수 자체가 아니라 **subprocess 경계에서의 exit code
          계약(INV-F)과 실 사용자 상태 무접촉**이다.

        ★ 격리: heartbeat 기록 대상을 tmpdir 로 주입한다. 주입이 없으면 이 테스트가
          실 사용자 파일(~/.claude/worktree-gc-state/scheduled-task-last-run.epoch)의
          mtime 을 갱신한다(실측 확인 결함) — 스케줄 작업이 미설치인 머신에서 유일한
          기록자가 테스트가 되어 관측자 생존 신호를 위조한다.
        """
        ITERATIONS = 10
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = tmpdir
            hb_path = os.path.join(tmpdir, "heartbeat.epoch")
            real_before = _real_heartbeat_state()

            # Arrange: CLI 진입점 파일 경로
            script_path = Path(__file__).parent.parent.parent / "scripts" / "lib" / "scheduled_task_reconcile.py"
            if not script_path.exists():
                pytest.fail(f"script 부재: {script_path} (requires_golden 마커, 미충족)")

            exit_codes = []
            for i in range(ITERATIONS):
                # Act: subprocess 호출 (실 상태 격리 env 주입)
                result = subprocess.run(
                    [sys.executable, str(script_path), "--repo-root", repo_root, "--dry-run"],
                    capture_output=True,
                    timeout=10,
                    env=_isolated_env(hb_path),
                )
                exit_codes.append(result.returncode)

            # Assert: INV-F (항상 0) — 선언한 반복수만큼 실제로 돌았는지도 함께 구속
            assert len(exit_codes) == ITERATIONS, (
                f"선언 반복수 {ITERATIONS} ≠ 실행 {len(exit_codes)}"
            )
            for code in exit_codes:
                assert code == 0, f"exit code 항상 0 기대 (INV-F), 실제: {code}"

            # Assert: 실 사용자 heartbeat 무접촉 (부재면 부재인 채로 — 존재/mtime/size 불변)
            assert _real_heartbeat_state() == real_before, (
                f"테스트가 실 heartbeat 경로를 건드렸다: {sut.HEARTBEAT_FILE} "
                f"(before={real_before}, after={_real_heartbeat_state()})"
            )

    def test_cli_invocation_heartbeat_isolated_from_real_state(self):
        """CLI 가 heartbeat 를 **기록하는** 경로에서도 실 사용자 상태는 무접촉.

        ★ teeth 설계: 정지 플래그(F1)를 tmpdir repo-root 에 두어 heartbeat 기록 경로를
          결정론적으로 태운다. --dry-run 경로는 설계상 heartbeat 를 기록하지 않으므로
          그 경로만으로는 "기록이 어디로 가는가" 를 판별할 수 없다 —
          ambient 잔재 유무에 따라 단언이 공허해진다.
          ① 주입 경로에 실제로 기록됨(seam 실효) ∧ ② 실 경로 불변 — 두 단언이 쌍이다.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            # Arrange: F1 정지 플래그 (halted 종료 경로 = heartbeat 기록 경로)
            os.makedirs(os.path.join(tmpdir, ".codeforge"), exist_ok=True)
            Path(os.path.join(tmpdir, sut.STOP_FLAG_REPO_RELPATH)).touch()
            hb_path = os.path.join(tmpdir, "heartbeat.epoch")
            real_before = _real_heartbeat_state()

            script_path = Path(__file__).parent.parent.parent / "scripts" / "lib" / "scheduled_task_reconcile.py"
            if not script_path.exists():
                pytest.fail(f"script 부재: {script_path}")

            # Act
            result = subprocess.run(
                [sys.executable, str(script_path), "--repo-root", tmpdir],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=30,
                env=_isolated_env(hb_path),
            )

            # Assert: 정지 경로 진입 확인 (기록 경로 결정론)
            assert result.returncode == 0, f"INV-F 위반: {result.returncode}"
            assert "halted=1" in (result.stdout or ""), (
                f"정지 경로 미진입 — 기록 경로가 결정론적이지 않다: {result.stdout!r}"
            )
            # Assert ①: 주입 경로에 실제로 기록됨 (env seam 이 살아 있음)
            assert os.path.exists(hb_path), (
                f"주입 경로에 heartbeat 미기록 — 격리 seam 무효: {hb_path}"
            )
            # Assert ②: 실 사용자 경로 불변
            assert _real_heartbeat_state() == real_before, (
                f"테스트가 실 heartbeat 경로를 건드렸다: {sut.HEARTBEAT_FILE} "
                f"(before={real_before}, after={_real_heartbeat_state()})"
            )


# ═══════════════════════ --dry-run 부수효과 0 (생존 신호 위조 금지) ═══════════════
class TestDryRunSideEffectZero:
    """--dry-run 은 채널 미접촉 + 부수효과 0 — heartbeat 도 기록하지 않는다.

    근거: heartbeat 기록 주체·시점 = 결정론 CLI 가 **관측 사이클을 실제로 돌고**
    정상 종료한 때(ADR-172 §결정 6). 사이클을 완결하지 않은 실행이 fresh 생존 신호를
    남기면 watchdog 이 구조적 false-negative(관측자 사망을 생존으로 보고)가 된다.
    """

    def test_dry_run_does_not_write_heartbeat(self):
        """M-DRY 오라클: --dry-run 종료 경로에서 heartbeat 파일 생성·갱신 0.

        dry-run 경로에 write_heartbeat() 를 재삽입하면 주입 경로에 파일이 생겨 RED.
        ★ 관측 0건이면 다른 종료 경로(관측 0건 무발화)로 빠지므로, 관측 1건을 주입해
          **dry-run 경로만** 태운다.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            hb_path = os.path.join(tmpdir, "heartbeat.epoch")
            real_before = _real_heartbeat_state()
            fixture = [sut.Observation(
                cls="temp",
                display_path="~/fixture/only",
                declared="선언 fixture",
                measured="실측 fixture",
                mismatch=False,
            )]

            # Act: dry-run 경로 (관측 1건 주입 — 실 홈 스캔 0, hermetic)
            with mock.patch.dict(os.environ, {sut.ENV_HEARTBEAT_FILE: hb_path}):
                with mock.patch.object(sut, "collect_observations", return_value=fixture):
                    rc = sut.run(["--repo-root", tmpdir, "--dry-run"])

            assert rc == 0, f"INV-F 위반: {rc}"
            # Assert: dry-run 은 생존 신호를 남기지 않는다
            assert not os.path.exists(hb_path), (
                f"--dry-run 이 heartbeat 를 기록했다 — 부수효과 0 계약 위반 · "
                f"관측 사이클 미완결 실행이 생존 신호 위조: {hb_path}"
            )
            assert _real_heartbeat_state() == real_before, (
                f"테스트가 실 heartbeat 경로를 건드렸다: {sut.HEARTBEAT_FILE}"
            )

    def test_halted_path_still_writes_heartbeat(self):
        """비-공허성 대조군: heartbeat 를 기록하는 종료 경로(F1 정지)는 여전히 기록한다.

        위 M-DRY 단언이 "env seam 이 죽어서 항상 통과" 하는 게 아님을 보이는 짝.
        (이 짝이 없으면 `not os.path.exists` 는 어떤 이유로든 항상 참이 될 수 있다.)
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            os.makedirs(os.path.join(tmpdir, ".codeforge"), exist_ok=True)
            Path(os.path.join(tmpdir, sut.STOP_FLAG_REPO_RELPATH)).touch()
            hb_path = os.path.join(tmpdir, "heartbeat.epoch")
            real_before = _real_heartbeat_state()

            with mock.patch.dict(os.environ, {sut.ENV_HEARTBEAT_FILE: hb_path}):
                rc = sut.run(["--repo-root", tmpdir])

            assert rc == 0, f"INV-F 위반: {rc}"
            assert os.path.exists(hb_path), (
                f"정지 종료 경로에서 heartbeat 미기록 — 기존 기록 경로가 소실됐다: {hb_path}"
            )
            assert _real_heartbeat_state() == real_before, (
                f"테스트가 실 heartbeat 경로를 건드렸다: {sut.HEARTBEAT_FILE}"
            )


# ═════════════════════ 판별 테스트: 격리 fixture 역할 검증 ═════════════════════
class TestHeartbeatFileIsolation:
    """판별 테스트: autouse fixture 의 역할을 검증.

    fixture 제거 시 RED 로 변경되어야 하는 테스트 — fixture 의 진정성(실제로 격리하는가)을 입증.
    """

    def test_heartbeat_isolation_env_set_outside_gc_state(self):
        """(ㄱ) 테스트 실행 중 env 설정 + 실 GC state 디렉터리 밖을 가리킴.

        Assert:
          - SCHEDULED_TASK_HEARTBEAT_FILE 이 설정되어 있음
          - 그 값이 ~/.claude/worktree-gc-state 를 포함하지 않음
          - 그 값이 tmp 경로 또는 비어있지 않음
        """
        env_key = "SCHEDULED_TASK_HEARTBEAT_FILE"
        env_value = os.environ.get(env_key)

        # Assert (ㄱ): env 설정됨 + 실 GC state 경로 밖
        assert env_value is not None, f"{env_key} 가 설정되어야 함"
        assert env_value.strip(), f"{env_key} 이 비워있지 않아야 함"
        gc_state_dir = os.path.expanduser("~/.claude/worktree-gc-state")
        assert gc_state_dir not in env_value, (
            f"{env_key} 이 실 GC state 디렉터리({gc_state_dir}) 를 포함하면 안 됨, "
            f"실제: {env_value}"
        )

    def test_heartbeat_isolation_run_does_not_create_real_file(self, tmp_path):
        """(ㄴ) sut.run() 실행 후 실 경로 불변 ∧ 주입 경로에만 기록됨.

        Arrangement:
          - 실 heartbeat 파일의 초기 mtime 저장
          - sut.run() 호출 전 env 값 저장

        Act:
          - sut.run(["--repo-root", tmpdir, "--channel", "test/repo#1"]) 호출
            ★ `--channel` 지정이라 채널 축이 실제로 발동한다. `STR_GH_BIN` seam 에
              stub 을 주입해 **실 GitHub 네트워크 호출 0** 으로 만든다(P1-3a).
              이전 판본은 이 주입이 없어 실 `gh issue view` 가 나갔다.

        Assert:
          - 실 경로 파일이 **존재하지 않음** (또는 초기 mtime 유지)
          - 주입 경로(env 값)에 파일이 **실제로 기록됨** (size > 0)
          - gh stub **호출 기록이 비어있지 않음** — seam 이 죽어서 조용히 통과하는 게
            아니라 채널 축이 실제로 stub 을 거쳤다는 증거 (mock-seam 규율)
        """
        env_key = "SCHEDULED_TASK_HEARTBEAT_FILE"
        env_value = os.environ.get(env_key)

        # 실 heartbeat 파일 경로
        real_gc_state = os.path.expanduser("~/.claude/worktree-gc-state")
        real_heartbeat_file = os.path.join(real_gc_state, "scheduled-task-last-run.epoch")

        # 실 경로의 초기 상태 저장 (부재 또는 mtime)
        real_file_existed_before = os.path.exists(real_heartbeat_file)
        real_mtime_before = os.path.getmtime(real_heartbeat_file) if real_file_existed_before else None

        # Act: sut.run() 호출 (주입 경로에 heartbeat 기록하도록)
        # scheduled_task_reconcile 모듈은 conftest 상단에서 sys.path 주입됨
        import scheduled_task_reconcile as sut_module

        # Arrange: gh stub 주입 (네트워크 0)
        gh_cmd, gh_log = _write_gh_stub(str(tmp_path))
        assert not os.path.exists(gh_log), "stub 로그 초기 상태는 부재여야 한다"

        # run() 호출 — heartbeat 기록 강제 (repo 여러 번 스캔)
        with mock.patch.dict(os.environ, {sut_module.GH_BIN_ENV: gh_cmd}):
            result = sut_module.run(["--repo-root", str(tmp_path), "--channel", "test/repo#1"])
        assert result == 0, "run() 항상 0 반환"

        # Assert: gh stub 이 실제로 호출됨 (seam 실효 — 네트워크 0 이 '공허'가 아님)
        assert os.path.exists(gh_log), (
            f"gh stub 호출 기록 부재 — STR_GH_BIN seam 미작동 또는 채널 축 미진입: {gh_log}"
        )
        with open(gh_log, encoding="utf-8") as fh:
            gh_calls = [ln.strip() for ln in fh if ln.strip()]
        assert gh_calls, f"gh stub 호출 기록이 비어 있음: {gh_log}"
        assert any("issue" in c for c in gh_calls), (
            f"gh stub 이 issue 서브커맨드로 호출되지 않음: {gh_calls}"
        )

        # Assert: 실 경로 무변화
        real_file_exists_after = os.path.exists(real_heartbeat_file)
        real_mtime_after = os.path.getmtime(real_heartbeat_file) if real_file_exists_after else None

        if real_file_existed_before:
            assert real_mtime_after == real_mtime_before, (
                f"실 heartbeat 파일({real_heartbeat_file})이 변경되었음: "
                f"mtime_before={real_mtime_before}, mtime_after={real_mtime_after}"
            )
        else:
            assert not real_file_exists_after, (
                f"실 heartbeat 파일이 생성되었음 (fixture 격리 실패): {real_heartbeat_file}"
            )

        # Assert: 주입 경로에 파일이 실제로 기록됨 (discriminating marker)
        assert env_value is not None, f"{env_key} 이 설정되어야 함"
        assert os.path.exists(env_value), (
            f"주입 경로({env_value})에 파일이 기록되어야 함. "
            f"fixture env 설정이 무시되었거나 sut.run() 이 heartbeat를 호출하지 않음"
        )
        assert os.path.getsize(env_value) > 0, (
            f"주입 경로({env_value})에 파일이 비어있음. "
            f"sentinel 값(distinct marker)이 부재해 exit-code 단독 판정 함정 방지 안 됨"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "not requires_golden"])
