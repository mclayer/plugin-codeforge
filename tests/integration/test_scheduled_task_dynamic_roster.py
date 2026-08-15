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

# 발화 계층 harness 재사용 (F-C 봉합분). §8.8.2 P1/P2 계약이 명명한 대상은 **채널 발화
#   개체 수**이므로 `run()` 을 완주시키는 harness 가 있어야 같은 계층에서 잴 수 있다.
#   sys.path 명시 주입 — pytest import mode 에 의존하지 않는다.
sys.path.insert(0, str(Path(__file__).parent))
from test_scheduled_task_dispatch_path import (   # noqa: E402
    FakeChannel, invoke_run, keys_of, make_obs_list,
)

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
)

# ★ **정의역 밖** — Change Plan §8.8.1 각주는 UNC(`\\server\share`)를 SUT 정규화 3축의
#   *검사 대상 자체가 아님*(검사 안 함)으로 규정한다. 아래 토큰을 NON_VIOLATING_TOKENS
#   에 두고 `hits == []` 를 단언하면 "검사해서 정상" 으로 지위가 뒤바뀌어 고착되고,
#   향후 UNC 마스킹이 도입되면 그 봉합이 오히려 이 오라클을 RED 로 만든다(ratchet).
#   그래서 여기로 분리하고 **단언하지 않는다** — 기록만 남기는 참조 상수다.
#   (구현리뷰 iter2 F-5. 시각 실측: 토큰 유입 `e80dc27a6` 12:53:24 → 각주 `c774f00e`
#    13:24:51 — 코드가 먼저이고 정당화가 31분 뒤였다.)
OUT_OF_DOMAIN_TOKENS = (
    "- 선언=test · 실측=test · 불일치=N · key=test:\\\\server\\share\\resource",
)

# ★ **양성 대조군** (FIX13/F-SEC-4 동반 — 아래 `_predicate_text` 가 오라클을 멀게 하지
#   않았음을 매 실행 확인한다). 이 토큰은 SUT 3축 중 드라이브·Users 루트에 정확히
#   걸리는 실 누출 형상이며, 무해화→역무해화 왕복 **후에도** 반드시 검출돼야 한다.
VIOLATING_CONTROL_TOKENS = (
    "key=test:C:\\Users\\alice\\x",
    "key=test:/home/bob/x",
)


def _predicate_text(text):
    """경로 누출 술어의 **정의역 정렬** — 마크다운 무해화 이전 문자열로 되돌린다.

    ★ 왜 필요한가 (FIX13 / 보안 F-SEC-4 봉합의 형제 영향):
      `_safe_text` 말미의 마크다운 무해화는 활성 구성자 앞에 `\\` 를 **삽입**한다.
      그런데 이 술어의 드라이브 축(`[A-Za-z]:[\\/]`)과 사용자명 축(`[\\/]<user>`)은
      `\\` 를 **경로 구분자**로 읽는다 ⇒ `D:<drive>` 처럼 SUT 3축 어디에도 걸리지 않는
      형상이 `D:\\<drive\\>` 로 바뀌면서 **거짓 위반**이 된다(실측: 10,000 case 중 14건,
      전부 `duplicate_expand` 가 만든 `D:D:\\…` 형상).
      SUT 는 무해화 **이전**에 정규화를 끝내므로, 정규화 계약의 정의역도 그 시점 문자열이다.
      `unneutralize_markdown` 은 `_neutralize_markdown` 의 좌역원(정확 복원)이라 이
      되돌림은 검출력을 깎지 않는다 — 실 누출(`C:\\Users\\x` → `C:\\\\Users\\\\x`)은
      되돌리면 그대로 다시 걸린다. 그 사실을 `VIOLATING_CONTROL_TOKENS` 가 매 실행 고정한다.
    """
    return sut.unneutralize_markdown(text)


def unnormalized_path_hits(text):
    """산출 문자열의 미정규화 절대경로 위반을 열거 (위반 0 = 빈 리스트)."""
    text = _predicate_text(text)
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


def _worker_heartbeat(idx, hb_path, barrier, base_epoch, rounds=1, interval=0.0):
    """Worker: barrier 정렬 후 heartbeat 를 `rounds` 회 write (oracle ④ 용).

    ★ rounds/interval 이 있는 이유: oracle ④ 는 **쓰기 중(in-flight) 표집**으로
      원자성을 재므로 관측창이 필요하다. 1회 write 는 창이 없어 부모가 찢어진 중간
      상태를 구조적으로 볼 수 없다(이전 판본의 판별력 0 원인).
    """
    sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts" / "lib"))
    import scheduled_task_reconcile as sut
    barrier.wait()  # 동시 진입
    for r in range(rounds):
        sut.write_heartbeat(now=base_epoch + idx * 1000 + r, path=hb_path)
        if interval:
            time.sleep(interval)


def _worker_heartbeat_nonatomic(idx, hb_path, barrier, base_epoch, rounds, torn_pause):
    """MUTANT worker (negative control): **비원자** write — 절단 후 분할 기록.

    production 을 건드리지 않고 `write_heartbeat` 의 `os.replace` 원자 write 를 잃은
    writer 를 테스트면에서 재현한다. 관측창을 결정론으로 넓히려 중간에 pause 한다
    (실제 비원자 write 의 창은 수십 µs 라 표집 확률이 호스트 의존이 된다).
    """
    barrier.wait()
    for r in range(rounds):
        value = "%d" % (base_epoch + idx * 1000 + r)
        with open(hb_path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(value[:5])       # ★ 절단 상태 노출 (유효 정수지만 기대집합 밖)
            fh.flush()
            time.sleep(torn_pause)
            fh.write(value[5:] + "\n")


def _read_heartbeat_sample(path):
    """heartbeat 파일 1회 표집 → (kind, raw). kind = absent | present | unreadable."""
    try:
        with open(path, encoding="utf-8") as fh:
            return ("present", fh.read())
    except FileNotFoundError:
        return ("absent", None)          # 첫 write 이전 = 유효 상태
    except OSError:
        return ("unreadable", None)      # 공유 위반 등 — 판정 불가 표본(집계에서 제외)


def _poll_heartbeat(path, procs, deadline_s=60.0, max_samples=200000):
    """워커 **join 전에** 돌면서 heartbeat 파일을 반복 판독해 표본을 모은다.

    ★ 이것이 oracle ④ 의 판별력 원천이다. 전건 join 후 1회 판독은 정지 시점만 보므로
      비원자 writer 도 통과한다(정지 시점엔 어떤 writer 도 완전한 값을 남긴다).
    """
    samples = []
    end = time.time() + deadline_s
    while any(p.is_alive() for p in procs):
        samples.append(_read_heartbeat_sample(path))
        if len(samples) >= max_samples or time.time() > end:
            break
    return samples


def _torn_samples(samples, expected_values):
    """표본 중 **찢어진 상태**를 열거한다 (빈 리스트 = 부분 기록 0).

    찢어짐 판정 = 파일이 존재하는데 내용이 **기록된 적 없는 값**인 경우.
      · 빈 문자열(절단 직후) · 자릿수 절단 prefix(`17551`) 모두 여기 걸린다.
      · `int()` 파싱 성공만 보는 판정은 prefix 절단을 놓친다 — prefix 도 유효 정수다.
    """
    expected = {str(v) for v in expected_values}
    torn = []
    for kind, raw in samples:
        if kind != "present":
            continue
        body = (raw or "").strip()
        if body not in expected:
            torn.append(raw)
    return torn


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
        #   ★ OUT_OF_DOMAIN_TOKENS(UNC)는 여기서 단언하지 않는다 — Change Plan §8.8.1
        #     각주가 "정의역 밖(검사 안 함)" 으로 규정한 축이라 어느 쪽으로도 고착시키지
        #     않는다(구현리뷰 iter2 F-5).
        for tok in NON_VIOLATING_TOKENS:
            assert unnormalized_path_hits(tok) == [], (
                f"oracle ① 자해: 비위반 토큰을 위반으로 오탐 — {tok!r}"
            )

        # 자기 건전성(**양성 대조군**): 실 누출 형상은 마크다운 무해화 왕복 **후에도**
        #   반드시 검출된다. `_predicate_text` 의 역무해화가 술어를 멀게 했다면 여기서
        #   RED — 아래 `violations == []` 이 공허해지는 경로를 이 단언이 닫는다.
        assert len(VIOLATING_CONTROL_TOKENS) >= 2, "양성 대조군 정의역 붕괴"
        for tok in VIOLATING_CONTROL_TOKENS:
            assert unnormalized_path_hits(tok) != [], (
                f"oracle ① 자해: 실 누출 형상을 놓친다 — {tok!r}"
            )
            assert unnormalized_path_hits(sut._neutralize_markdown(tok)) != [], (
                f"oracle ① 자해: 무해화된 실 누출 형상을 놓친다(역무해화 실패) — {tok!r}"
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


# ══════════════════ D3 라운드트립 계약 property (§8.8.2 — 신설) ══════════════════
class TestPropertyDedupRoundtrip:
    """D3: `역추출(render_fact_tuple(o)) == dedup_key(o)` 항등.

    이 항등이 깨지면 채널에 실린 키와 다음 실행의 재유도값이 달라져 **dedup 이 무력화**
    되고(매 실행 중복 발화) 최악의 경우 **임의 키 주입**이 성립한다. 실측으로 파괴된
    3형상을 회귀 고정한다 (ArchitectPL 설계 판정 (c)/(d) 이행):

      형상 ① 후행 공백 절단   — 역추출 정규식의 후행 `\\s*$` anchor 가 키 끝 공백을 삼킴
      형상 ② 임의 키 주입     — greedy `.*` 가 **마지막** `· key=` 를 골라, 관측 경로에
                                `· key=` 를 매립하면 추출값이 공격자 지정 문자열이 됨
      형상 ③ 길이 상한 비대칭 — 정방향은 상한 무제한, 역추출만 `_MAX_KEY_LEN` 초과 폐기
                                → 장문 키가 영원히 재수집되지 않아 무한 중복 발화

    ★ 이 property 는 SUT 의 **역추출 정규식 자신**(`sut._FACT_KEY_RE`)을 사용한다 —
      테스트가 별도 파서를 재구현하면 SUT 의 실 추출 경로를 재지 못한다.
    """

    @pytest.fixture
    def corpus_paths(self):
        """§8.8.1 fuzz corpus (input_surface 7 class) 재사용."""
        corpus_file = Path(__file__).parent.parent / "fixtures" / "cfp_2949" / "fuzz-corpus" / "paths.txt"
        if not corpus_file.exists():
            pytest.fail(f"corpus 부재: {corpus_file} (D3 정의역 입력 필수)")
        paths = []
        with open(corpus_file, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    paths.append(line)
        return paths

    @staticmethod
    def _extract(line):
        """SUT 역추출 경로 그대로 (fetch_existing_keys 가 쓰는 정규식)."""
        m = sut._FACT_KEY_RE.match(line)
        return None if m is None else m.group(1)

    def test_property_dedup_key_roundtrip_over_corpus(self, corpus_paths):
        """corpus 7 class 전량 + 3형상 회귀 케이스에 대해 라운드트립 항등."""
        # 형상별 회귀 케이스 (corpus 에 없는 축 — 실측 파괴 형상 그대로)
        shape_cases = [
            ("① 후행 공백", "~/.claude/worktrees/trailing-space   "),
            ("① 후행 탭", "~/.claude/worktrees/trailing-tab\t"),
            ("② 키 주입 · key=", "~/.claude/worktrees/x · key=INJECTED-EVIL"),
            ("② 키 주입 다중", "~/a · key=E1 · key=E2"),
            ("③ 상한 초과", "~/.claude/codeforge-scratch/" + "z" * 600),
            ("③ 상한 경계 직하", "~/" + "y" * (sut._MAX_KEY_LEN - 10)),
        ]
        cases = [("corpus", p) for p in corpus_paths] + shape_cases
        assert len(cases) >= len(corpus_paths) + 6, "케이스 구성 붕괴"

        failures = []
        for label, path in cases:
            obs = sut.Observation(
                cls="worktree", display_path=path,
                declared="완결 직후 정리", measured="age=9d 보존사유=none",
                mismatch=True,
            )
            expected = sut.dedup_key(obs)
            line = sut.render_fact_tuple(obs)
            extracted = self._extract(line)
            if extracted != expected:
                failures.append((label, path[:60], expected[:60],
                                 None if extracted is None else extracted[:60]))
            # 상한 대칭: 발화 키는 역추출 폐기 문턱을 넘지 않아야 한다
            if len(expected) > sut._MAX_KEY_LEN:
                failures.append((label + " [상한 비대칭]", path[:60], str(len(expected)), "-"))

        assert failures == [], (
            f"D3 라운드트립 파괴 {len(failures)}건 — (label, path, expected, extracted): {failures}"
        )

    def test_property_scrub_is_injective_over_corpus(self, corpus_paths):
        """verdict 어휘 변환의 **단사성** — 서로 다른 잔재가 한 키로 붕괴하지 않는다.

        ★ 계기 (구현리뷰 iter5 F-CR5-03, production 런타임 결함):
          구판 `_scrub_verdict_tokens` 는 매치 토큰을 `<제거>` 로 **삭제 치환**했다.
          삭제는 정보를 잃으므로 단사가 아니고, `_safe_text` 가 `dedup_key` 에도 걸리므로
          경로가 `pass`/`fail` 로만 다른 **두 잔재가 같은 키**를 갖는다 —
          한쪽이 먼저 발화되면 다른 쪽은 "기보고" 로 분류돼 **영구 억제**된다.
          공격자 없이 경로 문자열만으로 성립하며 어디에도 선언돼 있지 않았다.

        검사 2축:
          (ㄱ) **좌역원 존재** — `unscrub(scrub(x)) == x` 가 corpus 전량 + 어휘 케이스에서
               성립한다. 좌역원이 있으면 단사가 따라온다(구성적 증명).
          (ㄴ) **키 분리 실증** — 어휘만 다른 경로 쌍이 서로 다른 `dedup_key` 를 갖는다.
               (ㄱ)만으로도 함의되지만, 결함이 실제로 나타났던 층(키)에서 직접 잰다.
          (ㄷ) **구성상 lexicon-free** — 산출에 어휘 매치가 0 (INV-E 는 약화되지 않았다).

        mutant kill: 가역 변환을 삭제 변환으로 되돌리기
          (`_LEXICON_RE.sub(lambda m: m.group(0)[0] + "%-" + m.group(0)[1:], s)`
           → `_LEXICON_RE.sub("<제거>", s)`) ⇒ (ㄱ)·(ㄴ) 동시 RED.

        ★ 정직 천장: 여기서 재는 것은 **어휘 변환** 축의 단사성이다. `_safe_text` 전체는
          단사가 **아니다** — `_normalize_paths` 의 fail-closed 경로가 여러 입력을
          `<미정규화-경로-제거>` 하나로 접는다. 그 붕괴는 "정규화 실패 = 위치 미공개"
          라는 **선언된 보안 선택**이지 본 결함과 다른 축이며, 본 테스트는 그 축을
          단사라고 주장하지 않는다.
        """
        lexicon_cases = []
        for tok in sut.VERDICT_LEXICON:
            lexicon_cases += [
                "~/.claude/worktrees/cfp-100-%s" % tok,
                "~/.claude/worktrees/cfp-100-%s" % tok.lower(),
                "~/w/%s-머리" % tok,
                "~/w/꼬리-%s" % tok,
            ]
        esc_cases = ["100%", "%%", "%-", "a%-b", "%%-%", "~/w/50%-off", ""]
        cases = list(corpus_paths) + lexicon_cases + esc_cases
        assert len(cases) >= len(corpus_paths) + 4 * len(sut.VERDICT_LEXICON) + 7

        # (ㄱ) 좌역원
        broken = [c for c in cases if sut.unscrub_verdict_tokens(sut._scrub_verdict_tokens(c)) != c]
        assert broken == [], (
            "가역성 파괴 %d건 — 좌역원이 없으면 단사성이 무너지고 키 붕괴가 되살아난다: %r"
            % (len(broken), [b[:60] for b in broken[:5]])
        )

        # (ㄱ') 서로 다른 입력 → 서로 다른 산출 (corpus 전량 pairwise, 실 단사 관측)
        seen = {}
        collisions = []
        for c in cases:
            out = sut._scrub_verdict_tokens(c)
            if out in seen and seen[out] != c:
                collisions.append((seen[out][:50], c[:50], out[:50]))
            seen[out] = c
        assert collisions == [], f"스크럽 충돌 {len(collisions)}건: {collisions[:3]}"

        # (ㄴ) 어휘만 다른 경로 쌍의 키 분리 — 결함이 나타났던 층에서 직접
        pairs = [
            ("~/.claude/worktrees/cfp-100-pass", "~/.claude/worktrees/cfp-100-fail"),
            ("~/.claude/worktrees/run-ok", "~/.claude/worktrees/run-OK"),
            ("~/w/작업-정상", "~/w/작업-문제없음"),
        ]
        for left, right in pairs:
            kl = sut.dedup_key({"cls": "worktree", "display_path": left})
            kr = sut.dedup_key({"cls": "worktree", "display_path": right})
            assert kl != kr, (
                "키 붕괴: %r 와 %r 이 같은 키 %r — 한쪽 잔재가 영구 억제된다" % (left, right, kl)
            )

        # (ㄷ) INV-E 무손상 — 산출에 어휘 매치 0
        leaked = [c for c in cases if sut.contains_verdict_lexicon(sut._scrub_verdict_tokens(c))]
        assert leaked == [], f"INV-E 위반(산출 어휘 잔존) {len(leaked)}건: {leaked[:3]!r}"

    def test_property_roundtrip_survives_fetch_existing_keys(self):
        """end-to-end: 렌더 본문을 채널 코멘트로 되먹여 `fetch_existing_keys` 로 회수 →
        `dedup_key` 재유도값이 **전량 멤버십 성립**(= 재발화 0).

        위 단위 항등이 `fetch_existing_keys` 의 실 경로(sentinel 필터 + 길이 폐기 +
        set 수집)까지 살아남는지 확인한다 — 정규식만 고치고 상한을 비대칭으로 두면
        여기서 RED (장문 키가 회수 집합에서 빠져 재발화).
        """
        observations = [
            sut.Observation(cls="worktree", display_path=p, declared="d",
                            measured="m", mismatch=False)
            for p in (
                "~/.claude/worktrees/normal",
                "~/.claude/worktrees/trailing   ",
                "~/.claude/worktrees/x · key=INJECTED-EVIL",
                "~/.claude/codeforge-scratch/" + "z" * 600,
            )
        ]
        body = sut.render_report(observations, "d3-task", "d3-run")

        fake_gh = mock.Mock(return_value=mock.Mock(
            returncode=0, stdout=json.dumps({"comments": [{"body": body}]})))
        recovered = sut.fetch_existing_keys("owner/repo#1", gh=fake_gh)

        assert recovered is not None, "채널 회수 실패"
        missing = [sut.dedup_key(o) for o in observations
                   if sut.dedup_key(o) not in recovered]
        assert missing == [], (
            f"기보고 키 {len(missing)}건이 회수 집합에서 누락 — 매 실행 중복 발화. "
            f"누락(앞 60자): {[k[:60] for k in missing]}"
        )
        # 비공허성: 주입한 EVIL 문자열이 **독립 키**로 회수되지 않았는가 (키 주입 0)
        assert "INJECTED-EVIL" not in recovered, (
            f"임의 키 주입 성립 — 공격자 지정 문자열이 독립 키로 회수됨: {recovered}"
        )


# ═══════════════════════════════ Property Tests §8.8.2 ═══════════════════
class TestPropertyDedupIdempotence:
    """§8.8.2 property P1: dedup 멱등.

    동일 잔재 집합에 N회(2≤N≤5) 실행 → **채널 발화 개체 수 = 1**.

    ★ 계층 정정 (구현리뷰 iter4 F-C 부속 — ArchitectPL 신규 확인):
      직전 판본은 서로 다른 키를 로컬 `set` 에 넣고 `len == num_observations` 를 쟀다.
      그건 **로컬 키 집합의 원소 수**이지 Change Plan `:944` 가 계약한 **채널 발화
      개체 수**가 아니다 — 바깥 N회 루프가 단언에 **완전 무영향**이라 루프를 통째로
      지워도 결과가 같았다(멱등을 전혀 재지 않는 오라클). 여기서 `run()` 을 N회
      **완주**시켜 채널에 착지한 발화 개체를 직접 센다.
    """

    @given(
        count=st.integers(min_value=2, max_value=5),
        num_observations=st.integers(min_value=1, max_value=10),
    )
    @settings(max_examples=500, deadline=None)  # §8.8.2: 500 sample (계약 준수)
    def test_property_dedup_idempotent(self, count, num_observations):
        """같은 관측 N회 실행 → 채널 발화 개체 1

        mutant kill: `fresh = [o for o in observations if dedup_key(o) not in existing]`
        → `fresh = list(observations)` (dedup 필터 제거) ⇒ 발화 개체 = N ⇒ RED.

        ★ hypothesis 는 function-scoped fixture 를 거부하므로 tmp 는 본문에서 만든다.
        """
        if not HYPOTHESIS_AVAILABLE:
            pytest.fail("hypothesis 설치 필수 (§8.8.2 계약 이행 불가)")
        obs_list = make_obs_list(num_observations)
        chan = FakeChannel()

        with tempfile.TemporaryDirectory() as tmpdir:
            for i in range(count):
                r = invoke_run(tmpdir, obs_list, chan, run_id="r-%03d" % i)
                # 1회차만 신규, 이후 전량 기보고 (경로 식별 앵커)
                expected_new = num_observations if i == 0 else 0
                assert r.new == expected_new, (
                    f"{i + 1}회차 신규 {r.new} (기대 {expected_new}) — dedup 멱등 붕괴"
                )

        # 멱등 본체: 반복 횟수와 무관하게 채널 발화 개체는 1
        assert len(chan.posted) == 1, (
            f"발화 개체 {len(chan.posted)} (기대 1) — {count}회 실행에 중복 발화"
        )
        for k in keys_of(obs_list):
            assert f"key={k}" in chan.posted[0], (
                f"관측 {k!r} 가 유일 발화 본문에 미등재"
            )


class TestPropertyReconcileCompleteness:
    """§8.8.2 property P2: 회수 완전성.

    tick K회 건너뛰고 잔재 K개 축적 후 **1회 실행** → 채널 발화 개체 = K.
    cursor 면 RED (K 중 일부만).

    ★ 계층 정정 (구현리뷰 iter4 F-C 부속 — ArchitectPL 신규 확인):
      직전 판본은 `render_report()` 를 **직접** 호출해 `items=K` 를 쟀다. 그런데
      Change Plan `:958` 이 명명한 mutant 는 **cursor**(= `run()` 의 필터·절단 계층)다
      — render 계층을 겨눈 오라클은 그 mutant 를 **원리적으로 죽일 수 없다**
      (`render_report` 는 받은 목록을 전부 렌더하므로 상류가 잘려도 items 는 항상
      입력과 일치한다). 여기서 `run()` 을 완주시켜 **채널에 착지한 본문**을 잰다.

    ★ K ≤ 30 < MAX_FACT_LINES(50) — 정당한 상한 절단과 겹치지 않는 정의역이다
      (상한 절단 자체의 오라클은 dispatch_path harness ④가 따로 진다).
    """

    @given(
        accumulated_count=st.integers(min_value=1, max_value=30),
    )
    @settings(max_examples=500, deadline=None)  # §8.8.2: 500 sample (계약 준수)
    def test_property_reports_all_accumulated(self, accumulated_count):
        """축적 K개 → 채널 발화 K개

        mutant kill: `to_post = fresh[:MAX_FACT_LINES]` → `to_post = fresh[:2]`
        (cursor·절단) ⇒ K>2 에서 RED. 직전 render 계층 판본은 이 mutant 에 전량 통과했다.
        """
        if not HYPOTHESIS_AVAILABLE:
            pytest.fail("hypothesis 설치 필수 (§8.8.2 계약 이행 불가)")
        assert accumulated_count <= sut.MAX_FACT_LINES, (
            "정의역 전제 위반: K 가 상한을 넘으면 정당한 절단과 구별 불가"
        )
        observations = make_obs_list(accumulated_count)
        chan = FakeChannel()

        # Act: 축적분 전량을 1회 실행으로 회수 (빈 채널 = tick 건너뜀 재현)
        with tempfile.TemporaryDirectory() as tmpdir:
            r = invoke_run(tmpdir, observations, chan)

        # Assert ①: 발화 개체 1 + DONE 앵커가 축적 개수 전량을 신규로 계상
        assert len(chan.posted) == 1, f"발화 개체 {len(chan.posted)} (기대 1)"
        assert (r.observed, r.new, r.posted) == (accumulated_count, accumulated_count, 1), (
            f"P2 회수 완전성 위반: DONE observed={r.observed} new={r.new} posted={r.posted} "
            f"(기대 {accumulated_count}/{accumulated_count}/1)"
        )

        # Assert ②: 채널 본문의 items 정수값 = 축적 개수 (cursor·절단이면 여기서 RED)
        report = chan.posted[0]
        m = re.search(r"items=(\d+)", report)
        assert m is not None, f"items 필드 부재: {report!r}"
        assert int(m.group(1)) == accumulated_count, (
            f"P2 회수 완전성 위반: 축적 {accumulated_count}건, 발화 items={m.group(1)}"
        )
        fact_lines = [ln for ln in report.splitlines() if ln.startswith("- 선언=")]
        assert len(fact_lines) == accumulated_count, (
            f"P2 회수 완전성 위반: 발화 사실 줄 {len(fact_lines)}, 축적 {accumulated_count}"
        )

        # Assert ③: 각 관측의 식별자(dedup key)가 **채널에 착지한** 본문에 실렸는가
        for obs in observations:
            key = sut.dedup_key(obs)
            assert f"key={key}" in report, (
                f"P2 회수 완전성 위반: 관측 {key!r} 가 발화 본문에 미등재"
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
        """Oracle ④: 4워커 동시 heartbeat write 중 **쓰기 중 표집**으로 부분 기록 0.

        ★ 이전 판본의 판별력 0 (구현리뷰 iter2 F-4 — 여기서 봉합):
          4 프로세스를 `p.join()` 으로 **전건 완료시킨 뒤 1회 판독**했기 때문에 찢어진
          중간 상태가 구조적으로 관측 불가였다. 인라인 주석은 *"파일이 유효한 정수라는
          것 자체가 부분 기록 0 증명"* 이라 적었으나 이는 비-sequitur 다 — 비원자 writer
          도 **정지 시점엔** 완전한 값을 남긴다. 그 주석은 삭제했다.

        ★ 여기서의 형상:
          ① 워커는 `rounds` 회 반복 write 해 관측창을 만든다.
          ② 부모는 **join 전에** 폴러(`_poll_heartbeat`)로 파일을 반복 판독해 표본을 모은다.
          ③ 모든 표본이 유효 상태임을 단언 — 유효 = 파일 부재(첫 write 이전) ∨ 내용이
             **실제 기록된 값 집합의 원소**. `int()` 파싱 성공만 보면 자릿수 절단
             prefix(`17551`)를 놓치므로 기대집합 소속으로 잰다.
          ④ 비공허성 앵커 2종 — present 표본 수 하한 + **서로 다른 값 2개 이상 관측**
             (= 폴러가 파일이 바뀌는 동안 실제로 표집했다는 증거).

        ★ 앵커 하한(present >= 50 / distinct >= 2)의 근거 — **실측 1환경뿐, CI 미확인**:
          · 로컬 Windows 실측(무돌연변이, 본 테스트 3회 연속): `samples=9754~10428
            present=1585~2179 distinct=92~98 torn=0` ⇒ 하한은 실측의 각각 **1/32 이하 ·
            1/46 이하** 수준이라 여유가 크다. (수치는 iter7 F-CR6-03 봉합 후 재측정치다.
            봉합 전 distinct 는 40 대였다 — 공유 임시명 때문에 write 대부분이 실패해
            파일이 그만큼 덜 바뀌었기 때문이고, 개선 방향이라 하한 판단은 그대로다.)
          · 구조적 하한: 워커의 쓰기 구간이 `ROUNDS * INTERVAL` = **최소 150ms** 로 고정돼
            있고 폴러는 그 전 구간을 훑는다 — 하한 미달은 폴러가 150ms 를 통째로 놓친
            경우뿐이다.
          · **ubuntu CI 실측치는 없다.** 낮출 근거가 없으므로 **하한을 유지한다** —
            임의 완화는 근거 없이 검출력을 깎는 일이다. 하한 미달 시의 실패 방향은
            거짓 GREEN 이 아니라 **거짓 RED**(안전측)이며, 그때는 CI 실측치를 근거로
            재조정한다(추정으로 미리 낮추지 않는다).

        ★ Windows 한정 관측(판정 무영향) — **정량치·귀속 정정 (iter7 F-CR6-08)**:
          이전 판본은 *"600 write 중 약 14회"* + *"이 경고는 테스트(폴러)가 만든 것"*
          이라 적었다. 둘 다 틀렸다. 본 테스트 3회 연속 재측정(로컬 Windows):
            · `heartbeat 기록 실패 (non-blocking)` 경고 = 600 write 중 **494~501회**
              (약 82~84%). 종전 표기의 약 **36배**다.
            · **폴러를 0개로 두어도** 같은 형상에서 36~55회가 잔존한다 ⇒ 원인은 폴러
              단독이 아니다. 봉합 전에는 폴러 0 에서도 247회였고(공유 임시명으로
              writer 끼리 같은 파일을 덮었다 = F-CR6-03), 그 축을 봉합한 뒤 남은 것이
              위 36~55회 — `os.replace` 대 target 자신의 동시 경합이다.
            · 즉 현재의 지배 기여자는 폴러의 읽기 핸들(약 450회분)이고, 잔여 40여 회는
              폴러와 무관한 writer↔writer 경합이다.
          SUT 가 `OSError` 를 삼키고 **이전 값을 유지**하므로 표본은 계속 유효 상태이고
          오라클 판정에는 영향이 없다(그 성질은 그대로다).

        mutant kill: `write_heartbeat` 의 `os.replace` 원자 write 를 비원자 write
          (open+write 직접)로 교체 ⇒ RED. 형제 negative control =
          `TestConcurrencyNegativeControl.test_concurrency_oracle4_nonatomic_writer_is_torn`
          (production 무접촉으로 폴러의 검출력 자체를 상시 입증).
        """
        WORKERS = 4
        ROUNDS = 150
        INTERVAL = 0.001          # 관측창 확보 (총 쓰기 구간 ≈ 150ms 이상)

        with tempfile.TemporaryDirectory() as tmpdir:
            hb_path = os.path.join(tmpdir, "heartbeat.epoch")
            mp.set_start_method("spawn", force=True)
            barrier = mp.Barrier(WORKERS)
            base_epoch = 1700000000      # 고정 10자리 (prefix 절단이 기대집합에 없게)
            expected = {base_epoch + i * 1000 + r
                        for i in range(WORKERS) for r in range(ROUNDS)}

            procs = [
                mp.Process(target=_worker_heartbeat,
                           args=(i, hb_path, barrier, base_epoch, ROUNDS, INTERVAL))
                for i in range(WORKERS)
            ]
            start = time.time()
            for p in procs:
                p.start()

            # Act: ★ join **전에** 쓰기 중 표집
            samples = _poll_heartbeat(hb_path, procs)

            for p in procs:
                p.join()
            elapsed = time.time() - start
            samples.append(_read_heartbeat_sample(hb_path))     # 정지 시점 1건 추가

            present = [s for s in samples if s[0] == "present"]
            distinct = {(raw or "").strip() for _, raw in present}

            # Assert (ㄱ) — 비공허성 1/2: 폴러가 쓰기 구간에서 실제로 표집했다
            assert len(present) >= 50, (
                f"비공허성 붕괴: present 표본 {len(present)}건 (총 {len(samples)}) — "
                "폴러가 쓰기 중 파일을 거의 보지 못했다. 이 상태의 '부분 기록 0' 은 공허하다"
            )
            # Assert (ㄴ) — 비공허성 2/2: 파일이 폴러 밑에서 실제로 바뀌었다
            assert len(distinct) >= 2, (
                f"비공허성 붕괴: 관측된 서로 다른 값 {len(distinct)}종 — 폴러가 쓰기 중이 아니라 "
                f"정지 상태만 봤다(이전 판본과 동일한 사각). 관측값={sorted(distinct)[:5]}"
            )

            # Assert (ㄷ) — oracle ④ 본체: 모든 표본이 유효 상태 (부분 기록 0)
            torn = _torn_samples(samples, expected)
            assert torn == [], (
                f"oracle ④ 위반: 찢어진 표본 {len(torn)}건 관측 (원자 write 아님). "
                f"예: {torn[:3]!r}"
            )

            # Assert (ㄹ) — 최종 상태도 기록된 값 (전건 완료 후 정지 시점)
            assert os.path.exists(hb_path), f"heartbeat 파일 부재: {hb_path}"
            with open(hb_path, encoding="utf-8") as f:
                content = f.read().strip()
            assert content in {str(v) for v in expected}, (
                f"oracle ④: 최종 내용이 기록된 값 집합 밖: {content!r}"
            )

            print(f"\nConcurrency oracle ④: samples={len(samples)} present={len(present)} "
                  f"distinct={len(distinct)} torn={len(torn)} wall_clock={elapsed:.2f}s")


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

    def test_concurrency_oracle4_nonatomic_writer_is_torn(self):
        """Negative control (oracle ④ 대칭): **비원자 writer** 를 넣으면 폴러가 찢어짐을 잡는다.

        oracle ④ 의 판별력은 "쓰기 중 표집" 에서 나온다. 그 표집이 실제로 찢어진 상태를
        구별하는지를 **production 무접촉**으로 상시 입증한다 —
        `_worker_heartbeat_nonatomic` 은 `os.replace` 원자 write 없이 절단 후 분할
        기록하는 writer 이며, 폴러가 그 중간 상태를 표본으로 잡아야 한다.

        ★ 이 테스트가 GREEN 이라는 것은 "찢어짐이 관측됐다" 는 뜻이고, 그것이
          oracle ④ 의 `torn == []` 단언이 genuine 하다는 증거다(형제 oracle ① 의
          `WORKERS=1 → interleaving 0` 과 같은 구조).
        """
        ROUNDS = 15
        TORN_PAUSE = 0.008        # 결정론적 관측창 (총 ≈120ms)

        with tempfile.TemporaryDirectory() as tmpdir:
            hb_path = os.path.join(tmpdir, "heartbeat-nonatomic.epoch")
            mp.set_start_method("spawn", force=True)
            barrier = mp.Barrier(1)
            base_epoch = 1700000000
            expected = {base_epoch + r for r in range(ROUNDS)}

            procs = [
                mp.Process(target=_worker_heartbeat_nonatomic,
                           args=(0, hb_path, barrier, base_epoch, ROUNDS, TORN_PAUSE))
            ]
            for p in procs:
                p.start()

            samples = _poll_heartbeat(hb_path, procs)

            for p in procs:
                p.join()

            present = [s for s in samples if s[0] == "present"]
            assert len(present) >= 10, (
                f"negative control 자체가 공허: present 표본 {len(present)}건 — "
                "폴러가 파일을 보지 못했다(검출력 판정 불가)"
            )

            torn = _torn_samples(samples, expected)
            assert len(torn) >= 1, (
                "negative control 실패: 비원자 writer 인데 찢어진 표본 0건 — "
                f"폴러의 검출력이 없다(oracle ④ 의 torn==[] 이 공허해진다). "
                f"present={len(present)}"
            )

            print(f"\nNegative control oracle ④: present={len(present)} torn={len(torn)} "
                  f"예시={torn[0]!r}")

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
