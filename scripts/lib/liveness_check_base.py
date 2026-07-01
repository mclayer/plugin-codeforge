#!/usr/bin/env python3
# CFP-2549 / ADR-139 §결정 4 2안 — background-wait liveness gate presence lint 의 Ports&Adapters base (SSOT)
# ADR-061 §결정 1 Python-SSOT 패턴 + §결정 11 ReDoS-safe (line-by-line scan, anchored 리터럴 + \d+, per-entry cap)
#
# 목적:
#   background subagent/worker 대기(dispatch 발화)가 항상 runnable option-first wall-clock 가드
#   (`timeout --kill-after=<K> <N>`) 로 감싸졌는지 정적 검사하는 **어휘 무관(vocabulary-agnostic)**
#   재사용 base. adapter (codex-companion / general subagent-wait) 가 자기 dispatch 패턴·스캔 스코프·
#   home_marker 를 주입한다. base 는 codex-특정/general-특정 리터럴을 담지 않는다.
#
# Ports&Adapters:
#   - 이 파일 = base port (어휘 무관 검사 로직). codex 리터럴(adversarial-review 등) / general 리터럴
#     (run_in_background 등) 은 adapter 가 compiled regex 로 주입. base 에는 리터럴 leak 금지.
#   - adapter 는 detect_dispatch_utterance / detect_timeout_guard / check_liveness_presence 를
#     자기 dispatch_patterns·scan 스코프·home_marker 로 호출한다.
#
# 5-part 판정 semantics (adapter 공통 — codex-companion presence lint 에서 verbatim 추출):
#   1. option-first 가드 존재 → PASS
#   2. 가드 누락 / duration-first 오배열 / N<=0 → 위반 (exit 1)
#   3. hollow-gate (invariant I-3): home_marker 경로 파일이 스캔 트리에 실존하는데 dispatch 발화
#      총 건수가 0 이면 위반 (exit 1) — 발화가 lint 스코프를 이탈해도 항상 GREEN 되는 경로 차단.
#   4. 경로 부재 fail-safe (consumer no-op): 스캔 대상 파일 자체가 하나도 없으면 honest no-op (exit 0).
#   5. home_marker 부재 + dispatch 발화 0건 → honest no-op (exit 0, consumer degradation).
#
# ReDoS-safe: anchored 고정 리터럴 + \d+ (catastrophic backtracking 유발 nested quantifier 부재), 라인 단위 스캔.

import os
import re
import sys


def configure_utf8_stdout():
    """Windows 콘솔 cp949 기본 인코딩에서 em-dash 등 UTF-8 출력 실패 방지.
    (CI=Linux UTF-8 무관, 로컬 dev 견고성). adapter 가 진입점에서 1회 호출."""
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except (AttributeError, ValueError):
        pass


# ── runnable-form timeout 가드 패턴 (어휘 무관 — 값 형태만 검사) ────────────────────
# ★ runnable-form 강제 (CFP-2545 구현리뷰 FIX iter1 선례): GNU coreutils 는 duration-first
#   `timeout <N> --kill-after=<K> cmd` 에서 `--kill-after` 를 실행할 명령으로 오인 → exit 127 (가드 무효).
#   유일 runnable 형태 = option-first `timeout --kill-after=<K> <N> cmd`. lint 는 이 실행 가능 형태만
#   PASS 로 강제 (문자열 존재 축) + execution-backed 테스트가 런타임 진실에 결박 (실행 축, tests/scripts).
#   [verified: coreutils 8.32 — timeout 1 --kill-after=1 sleep 5 → exit 127 / timeout --kill-after=1 1 sleep 5 → exit 124]
# N/K 값 형태 2종 허용: 리터럴 정수(`300`) 또는 env-default(`${VAR:-300}`).
_INT = r'\d+'
_ENV_DEFAULT = r'\$\{[A-Za-z_][A-Za-z0-9_]*:-(\d+)\}'  # ${VAR:-<int>} — default 값 capture
_VAL = r'(?:(' + _INT + r')|' + _ENV_DEFAULT + r')'    # 정수 or env-default (2 capture group)

# option-first runnable 형태: timeout, 이어서 --kill-after=<K> 옵션(및 추가 -옵션), 그 다음 duration <N>.
# duration 앞에는 반드시 최소 1개 옵션(--kill-after)이 와야 함. duration-first 는 이 패턴에 unmatch → RED.
#   group 1/2 = --kill-after=<K> (리터럴/env)  ·  group 3/4 = duration <N> (리터럴/env)
TIMEOUT_RUNNABLE = re.compile(
    r'\btimeout\s+'
    r'(?:--\S+\s+)*'                       # 임의 개수의 앞선 -옵션 (예: --preserve-status)
    r'--kill-after=' + _VAL + r'\s+'       # --kill-after=<K> (필수, duration 앞)
    r'(?:--\S+\s+)*'                       # kill-after 뒤 추가 -옵션 허용
    + _VAL + r'(?=\s|$)'                   # duration <N> (옵션들 뒤) — 뒤에 공백 또는 라인 끝 (env-default `}` 뒤 \b 실패 회피)
)
# duration-first 오배열 탐지 (진단 메시지용): timeout 뒤 정수/env 가 먼저 오고 그 뒤 --kill-after.
TIMEOUT_DURATION_FIRST = re.compile(
    r'\btimeout\s+' + _VAL + r'\s+(?:--\S+\s+)*--kill-after='
)
# 가드 자체 부재 판정용 (timeout 토큰 존재 여부)
TIMEOUT_TOKEN = re.compile(r'\btimeout\b')


def _extract_int_pair(match, base):
    """TIMEOUT_RUNNABLE match 에서 정수 값 추출.
    base = group index 시작 (kill=1/2, duration=3/4)."""
    if match is None:
        return None
    lit, envdef = match.group(base), match.group(base + 1)
    if lit is not None:
        return int(lit)
    if envdef is not None:
        return int(envdef)
    return None


class TimeoutGuardResult:
    """detect_timeout_guard 구조화 결과.

    matched     : option-first runnable 가드 존재 여부 (bool)
    kill_after  : --kill-after=<K> 정수 (int|None)
    duration    : duration <N> 정수 (int|None)
    diagnosis   : matched=False 일 때 원인 enum
                  ('duration_first' | 'token_present_no_killafter' | 'absent')
                  matched=True 이면 None
    """

    __slots__ = ('matched', 'kill_after', 'duration', 'diagnosis')

    def __init__(self, matched, kill_after, duration, diagnosis):
        self.matched = matched
        self.kill_after = kill_after
        self.duration = duration
        self.diagnosis = diagnosis


def detect_timeout_guard(prefix):
    """option-first `timeout --kill-after=<K> <N>` runnable-form 검출 (어휘 무관).

    prefix = dispatch 발화 앞 텍스트(가드가 위치해야 하는 구간). 리터럴 정수 및 `${VAR:-<int>}`
    env-default 2 형태 지원. 반환 = TimeoutGuardResult.

    matched=True  → option-first 가드 존재 (kill_after/duration 정수 채워짐).
    matched=False → diagnosis 로 원인 구분:
      - 'duration_first'            : `timeout <N> --kill-after=<K>` 오배열 (exit 127, 가드 무효)
      - 'token_present_no_killafter': timeout 토큰은 있으나 --kill-after 부재/형태 불량
      - 'absent'                    : timeout 가드 자체 부재
    """
    mt = TIMEOUT_RUNNABLE.search(prefix)
    if mt:
        k = _extract_int_pair(mt, 1)   # --kill-after=<K> (group 1/2)
        n = _extract_int_pair(mt, 3)   # duration <N>     (group 3/4)
        return TimeoutGuardResult(True, k, n, None)
    if TIMEOUT_DURATION_FIRST.search(prefix):
        return TimeoutGuardResult(False, None, None, 'duration_first')
    if TIMEOUT_TOKEN.search(prefix):
        return TimeoutGuardResult(False, None, None, 'token_present_no_killafter')
    return TimeoutGuardResult(False, None, None, 'absent')


def detect_dispatch_utterance(line, dispatch_patterns):
    """text line 에서 dispatch 발화 검출 (어휘 무관 — 패턴 adapter 주입).

    dispatch_patterns = compiled regex list. 첫 매칭 (pattern_index, match) 반환, 없으면 None.
    (pattern_index 로 adapter 가 발화 종류를 라벨링 — 예: codex adversarial-review vs task --write.)
    """
    for idx, pat in enumerate(dispatch_patterns):
        m = pat.search(line)
        if m:
            return (idx, m)
    return None


def detect_execution_backed_selftest(text, patterns):
    """execution-backed selftest marker presence 검출 helper (어휘 무관).

    patterns = compiled regex list. text 안에 하나라도 존재하면 True (presence 축만 판정).
    general adapter 가 playbook/self-test 참조 존재 확인에 사용 (검출 로직은 base 공유).
    """
    for pat in patterns:
        if pat.search(text):
            return True
    return False


def make_execution_line_discriminator(execution_first_tokens):
    """실행 라인 vs prose/문서 예시 discriminator factory (어휘 무관 — first-token set adapter 주입).

    dispatch 발화(실행 라인)가 아닌 prose/문서 예시를 제외하는 판정자를 만든다.
    실행 라인 = 코드 블록 안 실제 커맨드. 첫 non-whitespace 토큰이:
      - execution_first_tokens 중 하나로 시작 (가드 prefix / 직접 실행 커맨드)  → 실행(검사)
      - `#` (주석 write-mode 예외) 뒤 body 가 execution_first_tokens 로 시작   → 실행(검사)
    그 외 (prose: `>`/`-`/`**`/서술 등으로 시작, dispatch 호출이 문장 중간 backtick 안) = 문서 예시 → 제외.

    execution_first_tokens = adapter 가 주입하는 실행 라인 시작 토큰 tuple
      (codex: ('timeout', 'node') / general: ('timeout', + dispatch 유틸리티 토큰)).
    """
    def _is_doc_example_line(line):
        stripped = line.lstrip()
        # 주석 write-mode 예외: `# timeout ... <dispatch>` 형태 → 검사 대상 (실행 시 활성)
        if stripped.startswith('#'):
            body = stripped[1:].lstrip()
            return not any(body.startswith(tok) for tok in execution_first_tokens)
        # 실행 라인: 가드 prefix 또는 dispatch 커맨드로 직접 시작
        if any(stripped.startswith(tok) for tok in execution_first_tokens):
            return False
        # 그 외 = prose/문서 예시
        return True

    return _is_doc_example_line


def _iter_files(paths, scan_exts):
    for p in paths:
        if os.path.isfile(p):
            if p.endswith(scan_exts):
                yield p
        elif os.path.isdir(p):
            for root, _dirs, files in os.walk(p):
                # .git / node_modules 회피
                if '.git' in root.split(os.sep) or 'node_modules' in root.split(os.sep):
                    continue
                for f in files:
                    if f.endswith(scan_exts):
                        yield os.path.join(root, f)


def check_lines(text, filename, dispatch_patterns, is_doc_example_line,
                kind_labels, adapter_name, diag_messages):
    """텍스트에서 dispatch 발화 라인을 찾아 timeout 가드 검증. (violations, dispatch_count) 반환.

    dispatch_patterns  : compiled regex list (adapter 주입 — 어휘)
    is_doc_example_line: prose 제외 discriminator (make_execution_line_discriminator 산출)
    kind_labels        : dispatch_patterns index → 발화 종류 라벨 (adapter 어휘)
    adapter_name       : 진단 메시지 prefix 어휘 (예: 'codex-companion' / 'subagent-wait-liveness')
    diag_messages      : diagnosis enum + 검증 실패 → 메시지 template dict (adapter 어휘)
                         keys: 'duration_first','token_present_no_killafter','absent','n_nonpos','k_neg'
                         각 value = format(filename, i, kind, n=None, k=None) 을 받는 callable.
    """
    violations = []
    dispatch_count = 0
    for i, raw in enumerate(text.splitlines(), start=1):
        line = raw
        hit = detect_dispatch_utterance(line, dispatch_patterns)
        if hit is None:
            continue
        idx, m = hit
        # inline prose 예시 제외 (실행 라인 / 주석 write-mode 예외만 대상)
        if is_doc_example_line(line):
            continue
        dispatch_count += 1
        kind = kind_labels[idx]
        # timeout 가드 prefix 는 dispatch 발화 *앞* 에 위치해야 함
        node_pos = m.start()
        prefix = line[:node_pos]

        # ★ runnable-form 강제: option-first `timeout --kill-after=<K> <N>` 만 PASS.
        guard = detect_timeout_guard(prefix)
        if guard.matched:
            n, k = guard.duration, guard.kill_after
            if n is not None and n <= 0:
                violations.append(diag_messages['n_nonpos'](filename, i, kind, n=n))
            if k is not None and k < 0:
                violations.append(diag_messages['k_neg'](filename, i, kind, k=k))
            continue

        # runnable 아님 — 원인 진단.
        violations.append(diag_messages[guard.diagnosis](filename, i, kind))
    return violations, dispatch_count


def _home_present(files, home_marker):
    """home_marker 경로가 스캔된 파일 중 실존하는지 판정 (Windows/POSIX path 정규화)."""
    marker_norm = os.path.normpath(home_marker)
    for f in files:
        f_norm = os.path.normpath(f)
        if marker_norm in f_norm:
            return True
    return False


def check_liveness_presence(paths, dispatch_patterns, scan_exts, home_marker,
                            adapter_name, kind_labels, is_doc_example_line,
                            diag_messages, messages):
    """공유 scan 드라이버 — 파일 walk → dispatch 발화별 timeout 가드 검증 → 5-part exit semantics.

    5-part 판정 (codex-companion presence lint 에서 verbatim 추출한 semantics):
      1. 모든 dispatch 발화에 option-first 가드 존재 → PASS (exit 0)
      2. 가드 누락/duration-first/N<=0 위반 ≥1 → exit 1
      3. hollow-gate I-3: home_marker 실존 + dispatch 발화 0건 → exit 1
      4. 경로 부재 fail-safe: 스캔 파일 0건 → honest no-op (exit 0)
      5. home_marker 부재 + dispatch 발화 0건 → honest no-op (exit 0, consumer degradation)

    messages = adapter 어휘 출력 template dict.
      keys: 'noop_no_files','noop_no_home','fail_hollow','fail_violations','pass'
      각 value = callable (필요 arg 주입 — 아래 호출부 참조).
    """
    files = list(_iter_files(paths, scan_exts))
    if not files:
        # (4) 경로 부재 fail-safe — honest no-op (consumer degradation, byte-identical mirror 상속 안전)
        print(messages['noop_no_files']())
        return 0
    all_violations = []
    total_dispatch = 0
    for f in files:
        try:
            with open(f, 'r', encoding='utf-8') as fh:
                text = fh.read()
        except (OSError, UnicodeDecodeError):
            continue
        v, c = check_lines(text, f, dispatch_patterns, is_doc_example_line,
                           kind_labels, adapter_name, diag_messages)
        all_violations.extend(v)
        total_dispatch += c
    if total_dispatch == 0:
        # hollow-gate 판정 (I-3) vs consumer no-op degradation 구분 —
        # home_marker 경로가 스캔 트리 안에 실존하면 → 발화 0건 = 파일 구조 drift(발화 스코프 이탈) → hollow-gate exit 1.
        # home_marker 부재하면(consumer repo 가 home 미보유) → honest no-op exit 0.
        if not _home_present(files, home_marker):
            # (5) home 부재 → honest no-op
            print(messages['noop_no_home']())
            return 0
        # (3) hollow-gate 차단 (I-3): home 실존 + 파일 존재하나 dispatch 발화 0건 → 항상 GREEN 방지
        print(messages['fail_hollow']())
        return 1
    if all_violations:
        # (2) 가드 위반
        print(messages['fail_violations'](all_violations))
        return 1
    # (1) PASS
    print(messages['pass'](total_dispatch))
    return 0
