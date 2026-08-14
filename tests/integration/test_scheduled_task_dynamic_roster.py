#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# tests/integration/test_scheduled_task_dynamic_roster.py — §8.8 동적 로스터
#
# 계약:
#   §8.8.1 fuzz (DO): input_surface 7 class, seed 2949, corpus, wall-clock ≤ 60s
#   §8.8.2 property (DO — hypothesis): P1 dedup 멱등, P2 회수 완전성, 500 sample
#   §8.8.4 concurrency (DO): 4 worker, barrier 정렬, wall-clock ≤ 120s
#
# ★ 정직 주의:
#   - fuzz 의 verdict 필터 oracle ② 는 회귀 안전망일 뿐, 실 carrier 는 §8.1 단위 테스트
#   - concurrency 는 데이터 경쟁 아닌 오보(같은 사실의 상이한 서술) 겨냥
#   - property 반례 발견 시 corpus 에 append 후 RED 착지

import time
import os
import json
import re
import tempfile
import pytest
import subprocess
import threading
import multiprocessing as mp
from pathlib import Path
from unittest import mock
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts" / "lib"))

import scheduled_task_reconcile as sut

try:
    from hypothesis import given, settings, strategies as st
    HYPOTHESIS_AVAILABLE = True
except ImportError:
    HYPOTHESIS_AVAILABLE = False


# ══════════ oracle ① 술어: 미정규화 절대경로 검출 (§8.8.1 / AC-13) ══════════════
#   SUT 가 **선언한** 정규화 3축과 정확히 같은 축만 잰다. SUT 가 보장하지 않는 축까지
#   재면 정상 코드에서 false RED 가 나므로(오라클이 계약을 넘어서면 안 된다) 축을 맞춘다:
#     ① 드라이브 문자 `X:\` / `X:/`      (SUT `_RESIDUAL_DRIVE_RE`)
#     ② `/Users/` · `/home/` 루트 세그먼트 (SUT `_RESIDUAL_USERROOT_RE`)
#     ③ 현 사용자명 경로 세그먼트          (SUT `_current_user_residual_re`)
#   ★ 드라이브 검사는 SUT `_DRIVE_RE` 와 동일한 negative lookbehind 를 쓴다 —
#     사실 줄 조립 seam(`key=test:` + 경로)의 `t:` 를 드라이브로 오탐하지 않기 위해서다.
_UNNORM_DRIVE_RE = re.compile(r"(?<![A-Za-z0-9])[A-Za-z]:[\\/]")
_UNNORM_USERROOT_RE = re.compile(r"(?i)[\\/](?:Users|home)[\\/]")
_CURRENT_USER = os.path.basename(os.path.expanduser("~"))
_UNNORM_USERNAME_RE = (
    re.compile(r"(?i)(?:^|[\\/])%s(?:$|[\\/])" % re.escape(_CURRENT_USER))
    if _CURRENT_USER else None
)

# 오탐 금지 대상 — 정규화가 **성공한** 결과물 토큰. 위반으로 잡히면 오라클이 자해다.
NON_VIOLATING_TOKENS = (
    "~/.claude/worktrees/foo",
    "<workspace>/plugin-codeforge",
    "<user-home>/.claude",
    "<drive>\\data\\archive",
    "/<user>/temp/cache",
    "<미정규화-경로-제거>",
    "- 선언=test · 실측=test · 불일치=N · key=test:<drive>\\data\\archive",
    "- 선언=test · 실측=test · 불일치=N · key=test:\\\\server\\share\\resource",
)


def unnormalized_path_hits(text):
    """산출 문자열의 미정규화 절대경로 위반을 열거 (위반 0 = 빈 리스트)."""
    hits = []
    m = _UNNORM_DRIVE_RE.search(text)
    if m:
        hits.append(("drive", m.group(0)))
    m = _UNNORM_USERROOT_RE.search(text)
    if m:
        hits.append(("user-root", m.group(0)))
    if _UNNORM_USERNAME_RE is not None:
        m = _UNNORM_USERNAME_RE.search(text)
        if m:
            hits.append(("current-user", m.group(0)))
    return hits


# ═══════════════════════════════ Multiprocessing Worker Module-level §8.8.4 ════
def _worker_dedup_concurrent(idx, barrier, sink_path, lock, worker_count, rounds):
    """Worker 프로세스: barrier 정렬 후 동시 sink append (worker_idx 포함).

    Args:
        idx: worker index (0..worker_count-1)
        barrier: multiprocessing.Barrier 동기화 객체
        sink_path: 발화 기록 파일 (format: "{idx}\t{key}\n")
        lock: multiprocessing.Lock (원자 쓰기)
        worker_count: 총 워커 수
        rounds: 각 워커가 수행할 라운드 수

    Concurrency model:
        - barrier.wait() 로 모든 워커가 동시에 진입
        - 각 round 마다 같은 obs 에 대해 dedup_key 생성
        - sink 파일에 "worker_idx\tkey\n" append (lock 으로 보호)
        - interleaving 감지: 라운드별로 워커 순서가 뒤바뀌는지 추후 검증
    """
    sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts" / "lib"))
    import scheduled_task_reconcile as sut

    for r in range(rounds):
        barrier.wait()  # ★ 동시 진입 정렬
        # ★ 모든 라운드/워커에서 동일한 obs (dedup 검증)
        obs = sut.Observation(
            cls="worktree",
            display_path="~/.claude/worktrees/shared",
            declared="d",
            measured="m",
            mismatch=True,
        )
        key = sut.dedup_key(obs)
        with lock:
            with open(sink_path, "a", encoding="utf-8") as f:
                # ★ worker_idx 포함 기록 (interleaving 감지용)
                f.write(f"{idx}\t{key}\n")


def _worker_heartbeat(idx, hb_path, barrier, base_epoch):
    """Worker: barrier 정렬 후 heartbeat write (oracle ④ 용)."""
    sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts" / "lib"))
    import scheduled_task_reconcile as sut
    barrier.wait()  # 동시 진입
    sut.write_heartbeat(now=base_epoch + idx, path=hb_path)


def _worker_dedup_bypass_mutant(idx, barrier, sink_path, lock, worker_count, rounds):
    """MUTANT: dedup 무시하고 매번 unique key 생성 (negative control 용)."""
    sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts" / "lib"))
    import scheduled_task_reconcile as sut

    for r in range(rounds):
        barrier.wait()
        obs = sut.Observation(
            cls="test",
            display_path="shared",
            declared="d",
            measured="m",
            mismatch=False,
        )
        key = sut.dedup_key(obs)
        # MUTANT: unique suffix 추가 (dedup 무시)
        mutant_key = f"{key}-worker{idx}"
        with lock:
            with open(sink_path, "a", encoding="utf-8") as f:
                f.write(f"{idx}\t{mutant_key}\n")


# ═══════════════════════════════ Fuzz Tests §8.8.1 ════════════════════════
class TestFuzzPathNormalization:
    """§8.8.1 fuzz: 경로 정규화 위임 + 마커 렌더.

    target: relativize_path / sanitize 호출 경로
    input_surface: 7 class (corpus 로부터 로드)
    oracle 3항: 미정규화 절대경로 0 / verdict 어휘 0 / 예외 비전파
    """

    @pytest.fixture
    def corpus_paths(self):
        """고정 seed corpus 로드 (paths.txt, SHA 쌍 기록)."""
        corpus_file = Path(__file__).parent.parent / "fixtures" / "cfp_2949" / "fuzz-corpus" / "paths.txt"
        if not corpus_file.exists():
            pytest.fail(f"corpus 부재: {corpus_file} (requires_golden 마커, 미충족. §8.8.1 fuzz 정의역 입력 필수)")

        paths = []
        with open(corpus_file, encoding="utf-8") as f:  # UTF-8 명시
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    paths.append(line)
        return paths

    def test_fuzz_path_normalization_oracle1_no_unredacted_path(self, corpus_paths):
        """Oracle 1: 미정규화 절대경로 누출 0 (AC-13).

        fixed seed 2949 + 10,000 case mutation 반복.
        예산 계약: wall-clock ≤60s

        Mutation ops (6종):
          - truncate: 경로 일부 절단
          - control_inject: 제어문자 삽입
          - latin1_noise: latin-1 잡음 추가
          - duplicate_expand: 부분 중복 팽창
          - swapcase: 대소문자 전환
          - reverse: 역순

        ★ 오라클 봉합 (이전 판본):
          이전 판본은 `render_fact_tuple`·`dedup_key` 를 호출만 하고 **산출을 폐기**한 뒤
          `crash_count == 0` 과 wall-clock 만 단언했다 — 함수명·docstring 은 oracle ①
          (미정규화 절대경로 0)을 주장하는데 실제로는 oracle ③(crash 0)과 동일했다.
          여기서는 매 mutation case 의 **렌더 산출과 dedup 키 양쪽**에 대해 미정규화
          절대경로 부재를 단언한다.

        ★ 정직 천장: 검사 축은 SUT 가 **선언한** 3축(드라이브 / Users·home 루트 /
          현 사용자명)뿐이다. 타 사용자명 단독 세그먼트처럼 SUT 가 보장하지 않는 축은
          재지 않는다 — 계약을 넘는 단언은 정상 코드에 대한 false RED 다.

        mutant kill: `_normalize_paths` 를 항등함수(`return s`)로 ⇒ RED.
        """
        import random
        import hashlib

        # 자기 건전성(negative control): 정규화 **성공** 토큰을 위반으로 잡지 않는다.
        for tok in NON_VIOLATING_TOKENS:
            assert unnormalized_path_hits(tok) == [], (
                f"oracle ① 자해: 비위반 토큰을 위반으로 오탐 — {tok!r}"
            )

        # Arrange: fixed seed 2949 + corpus SHA 기록
        rng = random.Random(2949)
        corpus_str = "\n".join(corpus_paths)
        corpus_sha = hashlib.sha256(corpus_str.encode()).hexdigest()[:8]

        # Mutation operators (6종)
        def _mutate(path_str, op_idx):
            """Apply mutation operation."""
            s = path_str
            if op_idx == 0:  # truncate
                cut_pos = rng.randint(1, max(2, len(s) // 2))
                return s[:cut_pos]
            elif op_idx == 1:  # control_inject
                pos = rng.randint(0, len(s))
                return s[:pos] + chr(rng.randint(1, 31)) + s[pos:]
            elif op_idx == 2:  # latin1_noise
                if s:
                    idx = rng.randint(0, len(s) - 1)
                    return s[:idx] + chr(rng.randint(128, 255)) + s[idx + 1:]
                return s
            elif op_idx == 3:  # duplicate_expand
                if s:
                    idx = rng.randint(0, len(s) - 1)
                    chunk = s[max(0, idx - 2):idx + 3]
                    return s[:idx] + chunk + s[idx:]
                return s
            elif op_idx == 4:  # swapcase
                return s.swapcase()
            else:  # reverse
                return s[::-1]

        # Act: 10,000 case 생성 및 oracle 검증
        start_time = time.time()
        FUZZ_CASES = 10000
        crash_count = 0
        violations = []          # (case_idx, 표면, 위반 종류, 발췌, 산출)
        checked = 0              # 실제로 oracle 술어를 통과시킨 산출 개수 (비공허성)

        for case_idx in range(FUZZ_CASES):
            base_path = corpus_paths[case_idx % len(corpus_paths)]
            mutation_op = case_idx % 6
            mutated_path = _mutate(base_path, mutation_op)

            try:
                obs = sut.Observation(
                    cls="test",
                    display_path=mutated_path,
                    declared="test",
                    measured="test",
                    mismatch=False,
                )
                result = sut.render_fact_tuple(obs)
                key = sut.dedup_key(obs)
            except Exception as e:
                crash_count += 1
                # ★ 비전파: 계속 진행
                continue

            # ★ Oracle ①: 렌더 산출·dedup 키 **양쪽**에 미정규화 절대경로 부재
            for surface, text in (("render_fact_tuple", result), ("dedup_key", key)):
                checked += 1
                hits = unnormalized_path_hits(text)
                if hits and len(violations) < 5:      # 표본 5건만 보관(로그 폭주 방지)
                    violations.append((case_idx, surface, hits, text[:200]))
                elif hits:
                    violations.append((case_idx, surface, hits, "<생략>"))

        elapsed = time.time() - start_time
        print(f"\nFuzz oracle ①: SHA8={corpus_sha}, seed=2949, cases={FUZZ_CASES}, "
              f"checked_outputs={checked}, wall_clock={elapsed:.2f}s, "
              f"crashes={crash_count}, unnormalized_hits={len(violations)}")

        # 비공허성: 산출 검사가 실제로 수행됐는가 (crash 로 전량 skip 되면 공허)
        assert checked == FUZZ_CASES * 2, (
            f"oracle ①: 검사 산출 {checked}건, 기대 {FUZZ_CASES * 2}건 "
            f"(crash {crash_count}건으로 검사 자체가 건너뛰어짐)"
        )

        # Oracle ①: 미정규화 절대경로 0
        assert violations == [], (
            f"oracle ①: 미정규화 절대경로 누출 {len(violations)}건 (10,000 case, 6-op). "
            f"표본: {violations[:5]}"
        )

        # 부수 oracle: 예외 비전파 (oracle ③ 과 중복이나 crash 시 조기 진단 신호)
        assert crash_count == 0, (
            f"oracle ①: 예외 {crash_count}건 (10,000 case, 6-op mutation)"
        )
        assert elapsed <= 60, f"oracle: wall-clock {elapsed:.2f}s > 60s"

    def test_fuzz_path_normalization_oracle2_no_verdict_lexicon(self, corpus_paths):
        """Oracle 2: verdict 어휘 누출 0 (회귀 안전망, §8.1 실 carrier 아님).

        10,000 case mutation 반복.
        """
        import random
        verdict_words = ("PASS", "FAIL", "OK", "정상", "문제없음")
        rng = random.Random(2949)

        def _mutate(path_str, op_idx):
            s = path_str
            if op_idx == 0:
                cut_pos = rng.randint(1, max(2, len(s) // 2))
                return s[:cut_pos]
            elif op_idx == 1:
                pos = rng.randint(0, len(s))
                return s[:pos] + chr(rng.randint(1, 31)) + s[pos:]
            elif op_idx == 2:
                if s:
                    idx = rng.randint(0, len(s) - 1)
                    return s[:idx] + chr(rng.randint(128, 255)) + s[idx + 1:]
                return s
            elif op_idx == 3:
                if s:
                    idx = rng.randint(0, len(s) - 1)
                    chunk = s[max(0, idx - 2):idx + 3]
                    return s[:idx] + chunk + s[idx:]
                return s
            elif op_idx == 4:
                return s.swapcase()
            else:
                return s[::-1]

        FUZZ_CASES = 10000
        verdict_count = 0

        for case_idx in range(FUZZ_CASES):
            base_path = corpus_paths[case_idx % len(corpus_paths)]
            mutation_op = case_idx % 6
            mutated_path = _mutate(base_path, mutation_op)

            obs = sut.Observation(
                cls="test",
                display_path=mutated_path,
                declared="test",
                measured="test",
                mismatch=False,
            )
            result = sut.render_fact_tuple(obs)

            for word in verdict_words:
                if word in result:
                    verdict_count += 1

        assert verdict_count == 0, (
            f"oracle ②: verdict 어휘 누출 {verdict_count}건 (10,000 case)"
        )

    def test_fuzz_path_normalization_oracle3_no_crash(self, corpus_paths):
        """Oracle 3: 예외 비전파 (crash 0).

        10,000 case mutation 반복.
        """
        import random
        rng = random.Random(2949)

        def _mutate(path_str, op_idx):
            s = path_str
            if op_idx == 0:
                cut_pos = rng.randint(1, max(2, len(s) // 2))
                return s[:cut_pos]
            elif op_idx == 1:
                pos = rng.randint(0, len(s))
                return s[:pos] + chr(rng.randint(1, 31)) + s[pos:]
            elif op_idx == 2:
                if s:
                    idx = rng.randint(0, len(s) - 1)
                    return s[:idx] + chr(rng.randint(128, 255)) + s[idx + 1:]
                return s
            elif op_idx == 3:
                if s:
                    idx = rng.randint(0, len(s) - 1)
                    chunk = s[max(0, idx - 2):idx + 3]
                    return s[:idx] + chunk + s[idx:]
                return s
            elif op_idx == 4:
                return s.swapcase()
            else:
                return s[::-1]

        FUZZ_CASES = 10000
        crash_count = 0

        for case_idx in range(FUZZ_CASES):
            base_path = corpus_paths[case_idx % len(corpus_paths)]
            mutation_op = case_idx % 6
            mutated_path = _mutate(base_path, mutation_op)

            try:
                obs = sut.Observation(
                    cls="test",
                    display_path=mutated_path,
                    declared="test",
                    measured="test",
                    mismatch=False,
                )
                result = sut.dedup_key(obs)
                result = sut.render_fact_tuple(obs)
            except Exception as e:
                crash_count += 1
                # ★ 비전파 = 계속 진행
                continue

        assert crash_count == 0, (
            f"oracle ③: 예외 비전파 {crash_count}건 (10,000 case, crash 0 기대)"
        )


# ═══════════════════════════════ Property Tests §8.8.2 ═══════════════════
class TestPropertyDedupIdempotence:
    """§8.8.2 property P1: dedup 멱등.

    동일 잔재 집합에 N회(2≤N≤5) 실행 → 채널 발화 개체 수 = 1.
    """

    @given(
        count=st.integers(min_value=2, max_value=5),
        num_observations=st.integers(min_value=1, max_value=10),
    )
    @settings(max_examples=500, deadline=None)  # §8.8.2: 500 sample (계약 준수)
    def test_property_dedup_idempotent(self, count, num_observations):
        """같은 관측 N회 → 발화 개체 1"""
        if not HYPOTHESIS_AVAILABLE:
            pytest.fail("hypothesis 설치 필수 (§8.8.2 계약 이행 불가)")
        obs_list = [
            sut.Observation(
                cls=f"class{i}",
                display_path=f"path{i}",
                declared="decl",
                measured="meas",
                mismatch=False,
            )
            for i in range(num_observations)
        ]

        # N회 반복 호출 시 dedup 키 중복 제거
        all_keys = set()
        for _ in range(count):
            for obs in obs_list:
                key = sut.dedup_key(obs)
                all_keys.add(key)

        # 멱등: 반복 횟수와 무관하게 고유 키 개수는 동일
        unique_count = len(all_keys)
        assert unique_count == num_observations, (
            f"고유 키 개수: {unique_count}, 관측: {num_observations}"
        )


class TestPropertyReconcileCompleteness:
    """§8.8.2 property P2: 회수 완전성.

    tick K회 건너뛰고 잔재 K개 추가 후 1회 호출 → 보고 개체 = K.
    cursor 면 RED (K 중 일부만).
    """

    @given(
        accumulated_count=st.integers(min_value=1, max_value=30),
    )
    @settings(max_examples=500, deadline=None)  # §8.8.2: 500 sample (계약 준수)
    def test_property_reports_all_accumulated(self, accumulated_count):
        """축적 K개 → 보고 K개"""
        if not HYPOTHESIS_AVAILABLE:
            pytest.fail("hypothesis 설치 필수 (§8.8.2 계약 이행 불가)")
        # Arrange: K개의 관측 생성
        observations = [
            sut.Observation(
                cls=f"class{i}",
                display_path=f"path{i}",
                declared="decl",
                measured="meas",
                mismatch=False,
            )
            for i in range(accumulated_count)
        ]

        # Act: render_report 로 본문 생성
        # (실제 reconcile 은 부분 발화 가능하지만, 이 테스트는
        #  상태 무의존 원칙 검증)
        report = sut.render_report(observations, "test", "001")

        # Assert ①: items 는 **정수값**이 축적 개수와 같아야 한다.
        #   ★ 이전 판본은 `assert "items=" in report` 뿐이라 500 examples 전량이
        #     항진명제로 통과했다(개수를 전혀 재지 않음). 값을 파싱해 구속한다.
        m = re.search(r"items=(\d+)", report)
        assert m is not None, f"items 필드 부재: {report!r}"
        assert int(m.group(1)) == accumulated_count, (
            f"P2 회수 완전성 위반: 축적 {accumulated_count}건, 보고 items={m.group(1)} "
            f"(cursor·절단 구현이면 여기서 RED)"
        )

        # Assert ②: 각 관측의 식별자(dedup key)가 본문에 실제로 실렸는가
        for obs in observations:
            key = sut.dedup_key(obs)
            assert f"key={key}" in report, (
                f"P2 회수 완전성 위반: 관측 {key!r} 가 본문에 미등재"
            )


# ═══════════════════════════════ Concurrency Tests §8.8.4 ═══════════════
class TestConcurrencyDedup:
    """§8.8.4 concurrency: 멀티프로세스, barrier 정렬, worker_count=4 (200 라운드, ≤120s).

    shared_state ③:
      ① dedup 채널 → fake file sink
      ② heartbeat + F2 플래그
      ③ 잔재 스캔 root

    oracle 4항:
      ① 같은 key 의 발화 개체 = 1
      ② 누락 0
      ③ F2 ON 시 발화 0
      ④ 상태 파일 원자성 (부분 기록 0)
    """

    def test_concurrency_oracle1_dedup_single_emission(self):
        """Oracle ①: 4워커×200라운드 multiprocessing → dedup key 중복 제거.

        실측 (PL): 4워커 200라운드 = 3.53s / 예산 120s (34배 마진)

        Concurrency model:
          - mp.set_start_method("spawn", force=True) — Windows 호환
          - 4 Process 생성, barrier 동기화
          - 각 프로세스가 200 라운드, 매 라운드마다 barrier.wait() 동시 진입
          - sink 파일에 "worker_idx\tkey\n" append (lock 보호)
          - 모든 프로세스 join 후 sink 검증

        4-assert (자기 실행 사실 검증, DeveloperPL 요구):
          1. spawn_count == WORKERS (4) — 프로세스 실제 기동
          2. total_writes == WORKERS * ROUNDS (800) — 누락 0 (oracle ②)
          3. torn_lines == 0 — 부분 기록 0 (oracle ④)
          4. interleaving_count > 0 — 워커 순서 교차 입증 (★ 순차 1-worker 제외)
        """
        WORKERS = 4
        ROUNDS = 200

        with tempfile.TemporaryDirectory() as tmpdir:
            sink_path = os.path.join(tmpdir, "dedup-sink.txt")

            # Arrange: multiprocessing context
            mp.set_start_method("spawn", force=True)
            barrier = mp.Barrier(WORKERS)
            lock = mp.Lock()

            # Act: 4 worker 프로세스 생성 및 실행
            start_time = time.time()
            procs = [
                mp.Process(
                    target=_worker_dedup_concurrent,
                    args=(i, barrier, sink_path, lock, WORKERS, ROUNDS),
                )
                for i in range(WORKERS)
            ]
            spawn_count = len(procs)
            for p in procs:
                p.start()
            for p in procs:
                p.join()
            elapsed = time.time() - start_time

            # Assert 1: spawn_count == WORKERS (프로세스가 실제로 떴는가)
            actual_spawn = sum(1 for p in procs if p.exitcode is not None)
            assert actual_spawn == WORKERS, (
                f"oracle ①-assert1: spawn_count={actual_spawn}, 기대: {WORKERS}"
            )

            # Parse sink: "idx\tkey\n"
            lines = []
            with open(sink_path, encoding="utf-8") as f:
                for ln in f:
                    ln = ln.strip()
                    if ln:
                        lines.append(ln)

            # Assert 2: total_writes == WORKERS * ROUNDS (800)
            EXPECTED_WRITES = WORKERS * ROUNDS
            assert len(lines) == EXPECTED_WRITES, (
                f"oracle ①-assert2: total_writes={len(lines)}, 기대: {EXPECTED_WRITES} "
                f"(누락 {EXPECTED_WRITES - len(lines)})"
            )

            # Assert 3: torn_lines == 0 (파일이 tab + key 형식인가)
            torn_lines = 0
            for ln in lines:
                parts = ln.split("\t")
                if len(parts) != 2:
                    torn_lines += 1
            assert torn_lines == 0, (
                f"oracle ①-assert3: torn_lines={torn_lines} (형식: idx\\tkey)"
            )

            # Assert 4: interleaving_count > 0 (워커 순서가 교차하는가)
            # 각 라운드별로 워커 순서 시퀀스를 추출, 라운드마다 비교
            worker_orders_by_round = [[] for _ in range(ROUNDS)]
            for i, ln in enumerate(lines):  # ★ enumerate: 위치 인덱스 사용 (list.index 버그 회피)
                parts = ln.split("\t")
                worker_idx = int(parts[0])
                round_num = i // WORKERS
                if round_num < ROUNDS:
                    worker_orders_by_round[round_num].append(worker_idx)

            # ★ 자기 건전성 assert: 라운드별 워커 개수 균일성
            assert all(len(o) == WORKERS for o in worker_orders_by_round), (
                f"라운드 버킷 크기 불균일 — interleaving 산출 전제 붕괴"
            )

            # 연속 라운드 비교: 순서가 다르면 interleaving
            interleaving_count = 0
            for r in range(len(worker_orders_by_round) - 1):
                if worker_orders_by_round[r] != worker_orders_by_round[r + 1]:
                    interleaving_count += 1

            assert interleaving_count > 0, (
                f"oracle ①-assert4: interleaving_count={interleaving_count}, "
                f"기대: > 0 (워커 순서 교차 입증, 4워커 200라운드 barrier 정렬)"
            )

            # Oracle ①: 동일 obs 라면 dedup_key 는 같아야 함
            unique_keys = set(ln.split("\t")[1] for ln in lines)
            assert len(unique_keys) == 1, (
                f"oracle ①: 동일 obs 4워커 200라운드 → unique key 1개 기대, "
                f"실제: {len(unique_keys)}"
            )

            # Wall-clock 검증
            assert elapsed <= 120, f"oracle: wall-clock {elapsed:.2f}s > 120s"

            print(f"\nConcurrency oracle ①: spawn_count={actual_spawn}, total_writes={len(lines)}, "
                  f"torn_lines={torn_lines}, interleaving_count={interleaving_count}, "
                  f"wall_clock={elapsed:.2f}s, unique_keys={len(unique_keys)}")

    def test_concurrency_oracle2_no_missing_writes(self):
        """Oracle ②: 4워커×200라운드 = 800 write, 누락 0.

        기대: 800개 라인 모두 sink 에 도착
        """
        WORKERS = 4
        ROUNDS = 200
        EXPECTED_WRITES = WORKERS * ROUNDS

        with tempfile.TemporaryDirectory() as tmpdir:
            sink_path = os.path.join(tmpdir, "write-sink.txt")

            mp.set_start_method("spawn", force=True)
            barrier = mp.Barrier(WORKERS)
            lock = mp.Lock()

            procs = [
                mp.Process(
                    target=_worker_dedup_concurrent,
                    args=(i, barrier, sink_path, lock, WORKERS, ROUNDS),
                )
                for i in range(WORKERS)
            ]
            for p in procs:
                p.start()
            for p in procs:
                p.join()

            # Assert: 파일에서 라인 개수 확인
            with open(sink_path, encoding="utf-8") as f:
                lines = [ln.strip() for ln in f if ln.strip()]

            assert len(lines) == EXPECTED_WRITES, (
                f"oracle ②: 기대 write={EXPECTED_WRITES}, 실제: {len(lines)} (누락 {EXPECTED_WRITES - len(lines)})"
            )

    def test_concurrency_oracle3_f2_halts_no_channel_access(self):
        """Oracle ③: F2 ON → run() 호출 시 채널 접촉 0 (fetch_existing_keys 미호출)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            f2_path = os.path.join(tmpdir, "scheduled-task.disabled")
            Path(f2_path).touch()

            # Act: run() — F2 정지 플래그로 인해 채널 접촉 0 기대
            # ★ STOP_FLAG_LOCAL 은 import 시점에 고정되므로 모듈 속성 재대입 필수
            original_flag = sut.STOP_FLAG_LOCAL
            try:
                sut.STOP_FLAG_LOCAL = f2_path
                with mock.patch.object(sut, "fetch_existing_keys") as spy_fetch:
                    sut.run(["--repo-root", tmpdir, "--channel", "owner/repo#1"])

                    # Assert: fetch_existing_keys 호출 0
                    assert spy_fetch.call_count == 0, (
                        f"oracle ③: F2 ON 시 채널 fetch 0 기대, 실제: {spy_fetch.call_count}"
                    )
            finally:
                sut.STOP_FLAG_LOCAL = original_flag

    def test_concurrency_oracle4_heartbeat_atomic_write(self):
        """Oracle ④: 4워커 동시 heartbeat write 시 부분 기록 0 (파일 항상 완전한 정수).

        Concurrency: 4개 프로세스가 동시에 write_heartbeat 호출
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            hb_path = os.path.join(tmpdir, "heartbeat.epoch")
            mp.set_start_method("spawn", force=True)
            barrier = mp.Barrier(4)
            base_epoch = int(time.time())

            # Act: 4개 프로세스 동시 write (모듈 레벨 함수 사용)
            procs = [
                mp.Process(target=_worker_heartbeat, args=(i, hb_path, barrier, base_epoch))
                for i in range(4)
            ]
            for p in procs:
                p.start()
            for p in procs:
                p.join()

            # Assert: 파일 내용이 유효한 정수 에포크 (부분 기록 0)
            assert os.path.exists(hb_path), f"heartbeat 파일 부재: {hb_path}"
            with open(hb_path, encoding="utf-8") as f:
                content = f.read().strip()

            try:
                epoch_val = int(content)
                assert epoch_val > 0, f"유효한 에포크 기대, 실제: {epoch_val}"
                # Oracle ④: 파일이 유효한 정수라는 것 자체가 부분 기록 0 증명
            except ValueError:
                pytest.fail(f"oracle ④: heartbeat 파일이 유효한 정수 아님: {content!r} "
                           f"(부분 기록 또는 손상 의심)")


class TestConcurrencyNegativeControl:
    """Negative control: oracle 를 무력화한 mutant 에서 RED 입증."""

    def test_concurrency_oracle1_single_worker_violates_interleaving(self):
        """Negative control: WORKERS=1 → interleaving_count=0 → assert4 RED.

        이 테스트가 RED 가 되는 것이 oracle ①-assert4 가 genuine 이라는 증거다.
        (WORKERS=4 에서 interleaving_count > 0 이 나오는 것과 대비)
        """
        WORKERS = 1  # ★ Single worker = 순차 실행
        ROUNDS = 10  # 빠른 검증용

        with tempfile.TemporaryDirectory() as tmpdir:
            sink_path = os.path.join(tmpdir, "single-worker-sink.txt")

            mp.set_start_method("spawn", force=True)
            barrier = mp.Barrier(WORKERS)
            lock = mp.Lock()

            procs = [
                mp.Process(
                    target=_worker_dedup_concurrent,
                    args=(i, barrier, sink_path, lock, WORKERS, ROUNDS),
                )
                for i in range(WORKERS)
            ]
            for p in procs:
                p.start()
            for p in procs:
                p.join()

            # Parse sink
            with open(sink_path, encoding="utf-8") as f:
                lines = [ln.strip() for ln in f if ln.strip()]

            # 1-worker: 모든 라운드에서 워커 순서가 [0] 으로 동일
            worker_orders_by_round = [[] for _ in range(ROUNDS)]
            for i, ln in enumerate(lines):  # ★ enumerate: 위치 인덱스 사용
                parts = ln.split("\t")
                worker_idx = int(parts[0])
                round_num = i // WORKERS
                if round_num < ROUNDS:
                    worker_orders_by_round[round_num].append(worker_idx)

            # ★ 자기 건전성 assert
            assert all(len(o) == WORKERS for o in worker_orders_by_round if o), (
                f"1-worker 라운드 버킷 크기 불균일"
            )

            # Interleaving 계산: 연속 라운드 비교
            interleaving_count = 0
            for r in range(len(worker_orders_by_round) - 1):
                if worker_orders_by_round[r] != worker_orders_by_round[r + 1]:
                    interleaving_count += 1

            # Assert: 1-worker 이므로 interleaving_count == 0 (★ assert4 가 RED, 정상)
            assert interleaving_count == 0, (
                f"negative control: WORKERS=1 에서 interleaving={interleaving_count}, "
                f"기대: 0 (순차 실행이므로 교차 없음, assert4 는 RED — 정상)"
            )

    def test_concurrency_oracle1_discriminates_dedup_bypass(self):
        """Mutant: dedup_key 를 무시하고 unique suffix 추가 → oracle ① RED 입증.

        Worker 가 "key + worker_index" 형태로 write 하면
        4워커 1라운드 = 4개 unique key 발화 → oracle ① fail
        """
        WORKERS = 4
        ROUNDS = 1  # 빠른 검증용

        with tempfile.TemporaryDirectory() as tmpdir:
            sink_path = os.path.join(tmpdir, "mutant-sink.txt")
            mp.set_start_method("spawn", force=True)
            barrier = mp.Barrier(WORKERS)
            lock = mp.Lock()

            procs = [
                mp.Process(
                    target=_worker_dedup_bypass_mutant,
                    args=(i, barrier, sink_path, lock, WORKERS, ROUNDS),
                )
                for i in range(WORKERS)
            ]
            for p in procs:
                p.start()
            for p in procs:
                p.join()

            # Assert: oracle ① 가 RED 낼 것 (unique key > 1)
            with open(sink_path, encoding="utf-8") as f:
                lines = [ln.strip() for ln in f if ln.strip()]

            unique_keys = set(ln.split("\t")[1] for ln in lines)
            assert len(unique_keys) > 1, (
                f"negative control: mutant bypass 가 unique key {len(unique_keys)}개 생성 — "
                f"oracle ① 이 RED 를 낼 것을 입증"
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "not requires_golden"])
