#!/usr/bin/env python3
# CFP-2545 / ADR-081 Amendment 12 §결정 D14 — Codex 리뷰 dispatch 발화 wall-clock 가드 presence lint (SSOT)
# CFP-2828 / ADR-081 Amendment 14 §결정 D15 — dispatch RE-TARGET: companion 브로커(`node codex-companion.mjs
#   adversarial-review`) → Codex CLI `codex exec` 직접 (파일명·action 명 유지 = required-context 재적립
#   chicken-egg 회피, ADR-130 §결정6 동형; D-5). wall-clock 리스크는 "소멸 아닌 이동"(CLI 고유 hang
#   #20919/#19945) 이라 은퇴 아닌 재타겟.
# CFP-2549 / ADR-139 §결정 4 2안 — background-wait liveness gate 의 Ports&Adapters codex adapter
#   (검사 로직 SSOT = scripts/lib/liveness_check_base.py, 본 파일 = codex-특정 어휘 주입 adapter).
# CFP-2884 / ADR-081 Amendment 15 §결정 D16 8항 — **3번째 disjoint 축** `scan_encoding_env_presence`
#   (UTF-8 인코딩 env export presence) 합류. 축 2 (`scan_stdin_redirect`) 와 동형 shape (자체 라벨 진단
#   + 독립 rc 반환 → `run_scan` max() 합성). warning tier 유지 · required 승격 0 (7일-green chicken-egg,
#   ADR-130 §결정 6). 신규 mechanical action 0 — 기존 entry 내부 축 확장.
# ADR-061 §결정 1 Python-SSOT 패턴 (thin wrapper = scripts/check-codex-companion-timeout-presence.sh)
#
# 목적:
#   codeforge 소유 Codex 리뷰 dispatch 발화(`codex exec ... - < <promptfile>`)가 항상 wall-clock 상한
#   (option-first `timeout --kill-after=<K> <N>`) prefix 로 감싸졌는지 + 각 발화가 stdin `- <` file-redirect
#   (inline positional prompt 부재, D8 계승) 를 동반하는지 + dispatch 표면이 UTF-8 인코딩 env export 를
#   별도 줄로 보유하는지 정적 검사. AC-9/AC-4/AC-7 mechanical 강제 층
#   (markdown 지시만으로는 self-discipline → hollow-gate).
#
# 검사 (dispatch 발화 = "실행 라인" 만; 주석·backtick inline 문서 예시는 대상 아님):
#   1. dispatch 발화 앞에 option-first `timeout --kill-after=<K> <N>` prefix 존재 (없으면 위반).   [AC-9]
#   2. `--kill-after=<정수>` 동반 (없으면 위반).                                                    [AC-9]
#   3. N (timeout 초) 이 양의 정수 (0/음수 위반).                                                   [AC-9]
#   4. hollow-gate 차단 (invariant I-3): 스캔 대상 파일이 존재하는데 dispatch 발화 총 건수가 0 이면
#      위반 (exit 1) — 파일 구조 drift 로 발화가 lint 스코프를 이탈해도 항상 GREEN 되는 경로 차단.
#   5. 경로 부재 fail-safe (consumer no-op): 스캔 대상 파일 자체가 하나도 없으면 honest no-op (exit 0).
#      byte-identical template mirror 를 consumer 가 상속해도 `plugins/codeforge-review/agents/` 경로
#      부재 시 spurious RED 를 내지 않게 하는 degradation (wrapper=파일 존재→발화≥1 강제 / consumer=파일 부재→no-op).
#   6. stdin `- <` redirect presence (positive 구조 계약, AC-4 / D-6): 각 codex exec dispatch 실행 발화가
#      `- <` file-redirect 를 동반해야 함 (부재 = 위반). base 5-part(timeout 축)와 disjoint 한 additive 축 —
#      base 무변경 유지(composition, max exit code). 한글 실값의 argv 노출 회피 + D8 inline-arg 금지
#      superset 커버 — 근거 단일 anchor = **ADR-081 §결정 D16 + ADR-170 §결정 21 (= §결정 2 표 entry 7)
#      동형 승계** ("argv 는 ASCII path 만, 한국어 실값·content 는 UTF-8 파일 내부"). 구 축약 태그 참조
#      (정의 문서가 repo 내 0건이던 dangling pointer) 는 본 anchor 로 재정착 — 재분산 금지
#      (ADR-081 Amendment 15 §결정 D16 4항).
#   7. UTF-8 인코딩 env export presence (AC-7 3번째 disjoint 축 — CFP-2884 / ADR-081 §결정 D16 8항):
#      codex exec dispatch 실행 발화를 1건 이상 보유한 파일은 `export LC_ALL=<locale>.UTF-8` 과
#      `export PYTHONUTF8=1` 을 각각 **별도 줄**로 보유해야 함 (부재 = 위반). inline env-prefix
#      (`LC_ALL=C.UTF-8 codex exec ...`) 는 라인 앵커 unmatch → RED — execution_first_tokens first-token
#      판정 보존 (CodexReviewAgent.md `export MSYS_NO_PATHCONV=1` 별도 줄 선례 동형).
#      ★ 보증 등급 정직: env export = **2급 defense-in-depth** — `LC_ALL`/`LANG` 은 Python-on-Windows
#      파일 I/O 에 무효 [InfraOp 실측, ADR-081 §결정 D16 3항] 이므로 본 축 GREEN 이 "인코딩 안전"을
#      뜻하지 않는다. 1급 보증 = helper 코드계층 명시 `encoding='utf-8'`
#      (scripts/lib/check_promptfile_utf8_roundtrip.py round-trip assert). 본 축은 presence 만 검사
#      (presence ≠ 무결성 — over-claim 금지, ADR-119).
#
# Ports&Adapters (CFP-2549 재배치): 검사 로직(runnable-form 판정 + 5-part scan driver)은 base 로 추출,
#   본 파일은 codex-특정 dispatch 패턴 / DEFAULT_SCAN_DIRS / home_marker / 진단 메시지 어휘 + AC-4 redirect 축
#   + AC-7 encoding env 축만 보유.
#
# Usage:
#   check_codex_companion_timeout_presence.py [<path> ...]   # 인자 = 스캔 대상 (파일 또는 디렉터리)
#   check_codex_companion_timeout_presence.py                # 인자 0개 = repo root 스캔
#   check_codex_companion_timeout_presence.py --self-test    # inline fixture RED/GREEN 판별 (CI D3 step)
#
# Exit code:
#   0 = PASS (모든 dispatch 발화에 timeout 가드 + `- <` redirect 존재, dispatch 보유 파일에 인코딩 env
#       export 존재) 또는 honest no-op (대상 파일 부재)
#   1 = 위반 (가드/redirect 누락 dispatch 발화 ≥1, 인코딩 env export 누락 dispatch 파일 ≥1,
#       또는 파일 존재하나 발화 0건 = hollow-gate)
#   2 = setup error (인자 경로 미존재 등)
#
# ReDoS 관측: line-by-line bounded scan + anchored 고정 리터럴 + \d+ + zero-width lookahead `[^\n]*`
#   (단일 선형 pass, nested quantifier 부재 = catastrophic backtracking 구조 부재 — structural, per-line
#   bounded). CFP-2884 추가분 (ENCODING_ENV_PATTERNS) 도 동일 형상 — 라인 앵커(`^...$`, MULTILINE) +
#   단일 문자클래스 `+`/`*` 1개 + 고정 리터럴 tail (중첩 quantifier 0, 교대 backtrack 분기 0).
#   임의 입력 총 작업량 무해성 절대단정 아님 (honest ceiling — ADR-168 §결정 16 (구 ADR-082 §결정 16, 재제정 CFP-2840) / ADR-151 §결정 7).
#   재현 가능한 복잡도 회귀 self-test 부재 — 위 서술은 **구조 관측**이지 벤치마크 증거 아님 (bounded
#   degradation 천장, 임의 입력 무해 아님).

import contextlib
import io
import os
import re
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import liveness_check_base as base

# Windows 콘솔 cp949 기본 인코딩에서 em-dash 등 UTF-8 출력 실패 방지 (CI=Linux UTF-8 무관, 로컬 dev 견고성).
base.configure_utf8_stdout()

# ── dispatch 발화 식별 패턴 (codex adapter 어휘 — CFP-2828 재타겟) ──────────────────
# codeforge 소유 Codex 리뷰 dispatch 실행 라인:
#   timeout ... codex exec ... --sandbox read-only      ... - < <promptfile>
#   timeout ... codex exec ... --sandbox workspace-write ... - < <promptfile>   (write-gate 예외 + marker)
# sandbox 축 3-tier: read-only / workspace-write / generic(sandbox 플래그 부재 codex exec 도 timeout 축 검사
#   대상 — evasion 차단, generic 이 fallback 이라 세 pattern 순서로 라벨 결정 [detect 는 첫 매칭 index 반환]).
_SANDBOX = r'(?:-s|--sandbox)\s+'
DISPATCH_EXEC_READONLY = re.compile(r'\bcodex\s+exec\b(?=[^\n]*' + _SANDBOX + r'read-only\b)')
DISPATCH_EXEC_WORKSPACE = re.compile(r'\bcodex\s+exec\b(?=[^\n]*' + _SANDBOX + r'workspace-write\b)')
DISPATCH_EXEC_GENERIC = re.compile(r'\bcodex\s+exec\b')

# base 에 주입할 dispatch 패턴 + 발화 종류 라벨 (index 정합 — sandbox 축 재라벨)
DISPATCH_PATTERNS = [DISPATCH_EXEC_READONLY, DISPATCH_EXEC_WORKSPACE, DISPATCH_EXEC_GENERIC]
KIND_LABELS = ['codex exec (read-only)', 'codex exec (workspace-write)', 'codex exec']

# stdin `- <` file-redirect presence (AC-4 positive 구조 계약 — bare `-` stdin marker + `<` 리다이렉트).
# `--flag` 오탐 회피: `-` 앞은 시작/공백, 바로 뒤는 (공백 후) `<` — `--output-schema` 는 두 번째 `-` 가 `<` 아님.
STDIN_REDIRECT = re.compile(r'(?:^|\s)-\s*<')

# ── UTF-8 인코딩 env export presence (AC-7 3번째 축 — CFP-2884 / ADR-081 §결정 D16 3항·8항) ──────
# "별도 줄 export" 강제: 라인 **전체**가 `export <VAR>=<값>` (선행 공백 + 후행 inline `#` 주석 허용) 이어야
#   매칭. inline env-prefix (`LC_ALL=C.UTF-8 codex exec ...`) 는 tail 앵커 unmatch → RED
#   (execution_first_tokens first-token 판정 파괴 금지 — CodexReviewAgent.md `export MSYS_NO_PATHCONV=1` 선례).
# locale 값 = `C` / `en_US` 류 단일 토큰 + `.UTF-8` suffix (대소문자 · 하이픈 유무 허용: UTF-8/utf8/…).
#   `.` 을 locale 토큰 문자셋에서 배제해 suffix 경계 모호성 제거 (backtrack 분기 0 — 위 ReDoS 관측 주석).
_ENV_LINE_TAIL = r'[ \t]*(?:#[^\n]*)?$'
ENCODING_ENV_PATTERNS = (
    ('export LC_ALL=<locale>.UTF-8',
     re.compile(r'^[ \t]*export[ \t]+LC_ALL=[A-Za-z0-9_@-]+\.[Uu][Tt][Ff]-?8' + _ENV_LINE_TAIL,
                re.MULTILINE)),
    ('export PYTHONUTF8=1',
     re.compile(r'^[ \t]*export[ \t]+PYTHONUTF8=1' + _ENV_LINE_TAIL, re.MULTILINE)),
)

# 스캔 대상 파일 확장자 (dispatch 발화가 사는 markdown/shell)
SCAN_EXTS = ('.md', '.sh', '.yml', '.yaml')

# dispatch 발화 검색 스코프 (파일 목록 하드코딩 금지 — 디렉터리 prefix 기반, E4 차단)
# codeforge 소유 Codex 리뷰 dispatch 발화가 사는 유일 위치 = codeforge-review agent md (origin/main 실측).
DEFAULT_SCAN_DIRS = (
    'plugins/codeforge-review',
)

# hollow-gate(I-3) vs consumer no-op 구분 기준 = codeforge-owned Codex 리뷰 dispatch 의 유일 home.
HOME_MARKER = os.path.join('plugins', 'codeforge-review', 'agents')

ADAPTER_NAME = 'codex-companion-timeout-presence'  # action 명 유지 (D-5 — rename deferred, required-context 재적립 회피)

# 실행 라인 discriminator: 첫 토큰이 timeout(가드 prefix) 또는 codex(직접 실행)면 검사 대상.
# ★ CFP-2828 필수 재타겟: ('timeout','node') → ('timeout','codex'). 미갱신 시 `codex exec` 첫-토큰 라인이
#   doc-example 로 오분류되어 스킵 → dispatch 미인식 → hollow trap (§8.4 R1 이 이 회귀를 자기검출).
_is_doc_example_line = base.make_execution_line_discriminator(('timeout', 'codex'))


# ── 진단 메시지 어휘 (codex adapter — 재타겟 문구) ─────────────────────────────────
def _msg_n_nonpos(filename, i, kind, n=None, k=None):
    return f'{filename}:{i}: `timeout ... {n}` — N(duration) 은 양의 정수여야 함 (0/음수 = 무한대기 미방지)'


def _msg_k_neg(filename, i, kind, n=None, k=None):
    return f'{filename}:{i}: `--kill-after={k}` — K 는 음수 불가'


def _msg_duration_first(filename, i, kind):
    return (
        f'{filename}:{i}: dispatch 발화({kind}) `timeout <N> --kill-after=<K>` = **duration-first 오배열** — '
        f'GNU coreutils 는 `--kill-after` 를 실행 명령으로 오인해 exit 127 (가드 무효). '
        f'option-first `timeout --kill-after=<K> <N>` 로 재배열 필요 (ADR-081 §D15)')


def _msg_token_present_no_killafter(filename, i, kind):
    return (
        f'{filename}:{i}: dispatch 발화({kind}) `timeout` 은 있으나 `--kill-after=<K>` 부재 또는 형태 불량 — '
        f'runnable option-first `timeout --kill-after=<K> <N>` 필요 (codex 프로세스 reap + 가드 유효, ADR-081 §D15)')


def _msg_absent(filename, i, kind):
    return (
        f'{filename}:{i}: dispatch 발화({kind})에 `timeout` wall-clock 가드 prefix 부재 — 무한 대기 미방지 (ADR-081 §D15)')


DIAG_MESSAGES = {
    'n_nonpos': _msg_n_nonpos,
    'k_neg': _msg_k_neg,
    'duration_first': _msg_duration_first,
    'token_present_no_killafter': _msg_token_present_no_killafter,
    'absent': _msg_absent,
}


# ── scan 출력 메시지 어휘 (codex adapter — 재타겟 문구) ────────────────────────────────
MESSAGES = {
    'noop_no_files': lambda: (
        '[codex-companion-timeout-presence] 스캔 대상 파일 0건 — honest no-op (PASS, consumer degradation)'),
    'noop_no_home': lambda: (
        '[codex-companion-timeout-presence] 스캔 트리에 codeforge-owned Codex 리뷰 dispatch home '
        '(plugins/codeforge-review/agents/) 부재 — honest no-op (PASS, consumer degradation).'),
    'fail_hollow': lambda: (
        '[codex-companion-timeout-presence] FAIL (I-3 hollow-gate): '
        'plugins/codeforge-review/agents/ 실존하나 codex exec dispatch 발화 0건. '
        '발화가 lint 스코프를 이탈했을 가능성 — 스코프/패턴 재확인 필요.'),
    'fail_violations': lambda violations: (
        '[codex-companion-timeout-presence] FAIL — wall-clock 가드 누락:\n'
        + '\n'.join('  ' + v for v in violations)),
    'pass': lambda total: (
        f'[codex-companion-timeout-presence] PASS — codex exec dispatch 발화 {total}건 전부 '
        f'runnable option-first timeout 가드 존재.'),
}


def check_lines(text, filename):
    """텍스트에서 dispatch 발화 라인을 찾아 timeout 가드 검증. (violations, dispatch_count) 반환.
    (self-test 및 외부 테스트가 직접 호출하는 공개 API — base 로 위임, timeout 축 behavior 무변경.)"""
    return base.check_lines(text, filename, DISPATCH_PATTERNS, _is_doc_example_line,
                            KIND_LABELS, ADAPTER_NAME, DIAG_MESSAGES)


def scan_stdin_redirect(paths):
    """AC-4 positive 구조 계약: 모든 codex exec dispatch 실행 발화 = stdin `- <` redirect 동반.

    base 5-part(timeout 축)와 disjoint 한 additive 검사 — base 무변경 유지 (composition).
    파일 walk = base._iter_files 재사용 (timeout 축과 동일 파일 집합 보장). 위반 ≥1 → exit 1, 없으면 0.
    (dispatch 발화 0건 = 이 축 vacuous → 0; hollow-gate/no-op 은 base timeout 축이 소유.)"""
    violations = []
    for f in base._iter_files(paths, SCAN_EXTS):
        try:
            with open(f, 'r', encoding='utf-8') as fh:
                text = fh.read()
        except (OSError, UnicodeDecodeError):
            continue
        for i, raw in enumerate(text.splitlines(), start=1):
            hit = base.detect_dispatch_utterance(raw, DISPATCH_PATTERNS)
            if hit is None:
                continue
            if _is_doc_example_line(raw):
                continue
            if not STDIN_REDIRECT.search(raw):
                violations.append(
                    f'{f}:{i}: codex exec dispatch 발화에 stdin `- <` redirect 부재 — '
                    f'inline positional prompt 금지, promptfile file-redirect 의무 (AC-4 / D8 계승, ADR-081 §D15)')
    if violations:
        print('[codex-companion-timeout-presence] FAIL (AC-4 — stdin `- <` redirect 부재):\n'
              + '\n'.join('  ' + v for v in violations))
        return 1
    return 0


def scan_encoding_env_presence(paths):
    """AC-7 3번째 축: codex exec dispatch 표면 = UTF-8 인코딩 env export 별도 줄 presence.

    판정 granularity = **파일 단위 술어, dispatch 발화 좌표로 진단** — codex exec dispatch 실행 발화를
    1건 이상 보유한 파일은 `export LC_ALL=<locale>.UTF-8` + `export PYTHONUTF8=1` 을 각각 별도 줄로
    보유해야 한다 (env export 는 dispatch 라인 자체가 아니라 그 표면의 shell 컨텍스트에 사는 값이라
    per-line 술어가 성립하지 않음 — 축 2 의 per-line 술어와 granularity 는 다르되 **shape 는 동형**:
    자체 라벨 진단(위반별 `file:line` 전체 목록 print) + 독립 rc 반환 → run_scan max() 합성).

    base 5-part(timeout 축) / 축 2(redirect) 와 disjoint additive — base 무변경 유지 (composition).
    파일 walk = base._iter_files 재사용 (세 축 동일 파일 집합 보장). 위반 ≥1 → 1, 없으면 0.
    (dispatch 발화 0건 파일 = 이 축 vacuous → skip; hollow-gate/no-op 은 base timeout 축이 소유.)

    ★ 보증 등급 정직 (ADR-119 / ADR-081 §결정 D16 3항): 본 축 GREEN = env export **presence** 뿐이며
    인코딩 무결성이 아니다 — `LC_ALL`/`LANG` 은 Python-on-Windows 파일 I/O 에 무효 (2급
    defense-in-depth). 1급 = helper 코드계층 명시 `encoding='utf-8'` round-trip assert.
    """
    violations = []
    for f in base._iter_files(paths, SCAN_EXTS):
        try:
            with open(f, 'r', encoding='utf-8') as fh:
                text = fh.read()
        except (OSError, UnicodeDecodeError):
            continue
        anchor_line = None
        for i, raw in enumerate(text.splitlines(), start=1):
            if base.detect_dispatch_utterance(raw, DISPATCH_PATTERNS) is None:
                continue
            if _is_doc_example_line(raw):
                continue
            anchor_line = i
            break
        if anchor_line is None:
            continue   # dispatch 발화 0건 = 본 축 vacuous
        missing = [label for label, pat in ENCODING_ENV_PATTERNS if not pat.search(text)]
        if missing:
            violations.append(
                f'{f}:{anchor_line}: codex exec dispatch 표면에 UTF-8 인코딩 env export 부재 '
                f'(누락: {", ".join(missing)}) — 각각 **별도 줄** export 의무 '
                f'(inline env-prefix 금지: first-token 판정 파괴). '
                f'2급 defense-in-depth — 1급 보증은 helper 코드계층 encoding=\'utf-8\' '
                f'(AC-7 / ADR-081 §결정 D16 3항·8항)')
    if violations:
        print('[codex-companion-timeout-presence] FAIL (AC-7 — UTF-8 인코딩 env export 부재):\n'
              + '\n'.join('  ' + v for v in violations))
        return 1
    return 0


def run_scan(paths):
    # timeout 축 (base 5-part 소유: 가드 presence / hollow-gate I-3 / consumer no-op)
    #   ∪ AC-4 redirect 축 ∪ AC-7 encoding env 축 — 3축 **무조건 순차 실행** (short-circuit 없음:
    #   동시 위반 시 세 라벨 진단이 모두 stdout 에 잔존해야 함, ADR-081 §결정 D16 8항 / CFP-2884 §8.2B B-3).
    timeout_rc = base.check_liveness_presence(
        paths, DISPATCH_PATTERNS, SCAN_EXTS, HOME_MARKER, ADAPTER_NAME,
        KIND_LABELS, _is_doc_example_line, DIAG_MESSAGES, MESSAGES)
    redirect_rc = scan_stdin_redirect(paths)
    encoding_rc = scan_encoding_env_presence(paths)
    return max(timeout_rc, redirect_rc, encoding_rc)


# ── self-test (D3 inline fixture, CI step 호출) ────────────────────────────────
# 3축 라벨 진단 리터럴 (동시위반 fixture B-3 가 stdout 실재를 축별로 assert — CFP-2884 §8.2B B-3).
_AXIS_LABELS = {
    'timeout': '[codex-companion-timeout-presence] FAIL — wall-clock 가드 누락',
    'redirect': '[codex-companion-timeout-presence] FAIL (AC-4 — stdin `- <` redirect 부재)',
    'encoding': '[codex-companion-timeout-presence] FAIL (AC-7 — UTF-8 인코딩 env export 부재)',
}


def _run_scan_capture(paths):
    """run_scan 실행 + stdout 캡처 — (rc, 출력 텍스트) 반환.

    축별 라벨 진단이 실제로 stdout 에 남는지 assert 하려면 exit code (스칼라) 만으론 불충분하다
    (max() 합성 후 rc 는 1 하나뿐 — 어느 축이 울었는지 구분 불가). 진단 텍스트가 warning tier 의
    actionable 신호이므로 그 실재를 직접 검사한다 (CFP-2884 §6.1 P3 판정).
    """
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = run_scan(paths)
    return rc, buf.getvalue()


def _self_test_scan_axes():
    """AC-7 encoding env 축 + AC-4 redirect 축 + timeout 축의 **scan 계층** discriminating self-test.

    text-only `check_lines` 로는 축 2·3 (파일 walk 기반) 을 행사할 수 없어 tempfile fixture 를 쓴다
    (실 `run_scan` 합성 경로를 그대로 통과 — max() 합성·순차 실행 무-short-circuit 도 함께 검증).
    반환 = (failed 리스트, 총 case 수).
    """
    guarded = ('timeout --kill-after=30 300 codex exec '
               '-s read-only --output-schema s.json -o out.json - < p.md\n')
    env_block = ('export LC_ALL=C.UTF-8   # 별도 줄 export (inline env-prefix 는 first-token 판정 파괴)\n'
                 'export PYTHONUTF8=1\n')
    # (name, text, expect_rc, must_contain 축 set, must_not_contain 축 set)
    cases = [
        ('E1 GREEN: env export 2종 별도 줄 + 가드 + redirect (AC-7 축 충족)',
         env_block + guarded, 0, set(), {'timeout', 'redirect', 'encoding'}),
        ('E2 RED: encoding env 부재 (AC-7 단독 발화 — 타 2축은 침묵해야 함)',
         guarded, 1, {'encoding'}, {'timeout', 'redirect'}),
        ('E3 GREEN: dispatch 발화 0건 파일 → AC-7 축 vacuous (env 부재라도 false-RED 금지)',
         '이 파일에는 실행 dispatch 발화가 없다 — prose 서술만 존재.\n',
         0, set(), {'timeout', 'redirect', 'encoding'}),
        ('E4 RED: inline env-prefix 는 별도 줄 export 아님 (substring 검사 hollow 구현 검출)',
         '# 아래 첫 발화는 인라인 env-prefix 형태 (금지) — 별도 줄 export 부재\n'
         'LC_ALL=C.UTF-8 PYTHONUTF8=1 ' + guarded + guarded,
         1, {'encoding'}, {'timeout', 'redirect'}),
        ('B3 RED: 3축 동시위반 (timeout 제거 + redirect 제거 + env 부재) → 라벨 3종 전부 stdout 실재',
         'codex exec -s read-only --output-schema s.json -o out.json\n',
         1, {'timeout', 'redirect', 'encoding'}, set()),
    ]
    failed = []
    for name, text, expect_rc, want, unwanted in cases:
        with tempfile.TemporaryDirectory() as td:
            fixture = os.path.join(td, 'fixture.md')
            with open(fixture, 'w', encoding='utf-8', newline='\n') as fh:
                fh.write(text)
            rc, out = _run_scan_capture([td])
        problems = []
        if rc != expect_rc:
            problems.append(f'rc {rc} != {expect_rc}')
        for axis in sorted(want):
            if _AXIS_LABELS[axis] not in out:
                problems.append(f'축 라벨 부재: {axis}')
        for axis in sorted(unwanted):
            if _AXIS_LABELS[axis] in out:
                problems.append(f'축 라벨 오발화: {axis}')
        status = 'OK' if not problems else 'MISMATCH'
        if problems:
            failed.append((name, '; '.join(problems)))
        print(f'  [{status}] {name} (expect rc={expect_rc}, labels={sorted(want) or "none"})')
        for p in problems:
            print(f'      ↳ {p}')
    return failed, len(cases)


def self_test():
    # ★ CFP-2828 재타겟 discriminating (§8.4 표): timeout 축 GREEN/RED + hollow.
    #   판정은 exit code 가 아닌 **failure mode**(green/violation/hollow) 로 — R1(timeout 제거, `codex exec`
    #   column0) 은 exit 1 을 hollow 로도 낼 수 있어(가짜 통과), mode='violation' 을 요구해야 execution_first_tokens
    #   ('timeout','node')→('timeout','codex') 재타겟 회귀를 자기검출(미갱신 시 line 스킵→dispatch 0→mode=hollow≠violation).
    #   실행 축(B1/B2 execution-backed) + scan 축(G3 consumer no-op)은 tests/scripts bats(QADev) 소관 (text-only 불가).
    RO = '-s read-only --output-schema s.json -o out.json - < p.md'
    WW = '-s workspace-write --output-schema s.json -o out.json - < p.md'
    cases = [
        # (name, text, expect_mode)
        ('G1 GREEN: option-first (env-default) read-only',
         f'timeout --kill-after=${{CODEX_REVIEW_KILL_AFTER_SEC:-30}} ${{CODEX_REVIEW_TIMEOUT_SEC:-300}} codex exec {RO}\n',
         'green'),
        ('G2 GREEN: option-first (리터럴) write-mode 예외',
         f'timeout --kill-after=30 300 codex exec {WW}\n', 'green'),
        ('R1 RED: timeout 제거 (load-bearing — codex exec column0, 재타겟 회귀 자기검출)',
         f'codex exec {RO}\n', 'violation'),
        ('R2 RED: duration-first 오배열 (broken, exit 127)',
         f'timeout 300 --kill-after=30 codex exec {RO}\n', 'violation'),
        ('R3 RED: N=0 (무한대기 미방지)',
         f'timeout --kill-after=30 0 codex exec {RO}\n', 'violation'),
        ('R4 RED: --kill-after 누락 (option 부재)',
         f'timeout 300 codex exec {RO}\n', 'violation'),
        ('R5 RED: dispatch 발화 0건 (hollow-gate I-3, 파일 존재)',
         '이 파일에는 실행 dispatch 발화가 없다 — prose 서술만 존재.\n', 'hollow'),
    ]
    failed = []
    for name, text, expect in cases:
        violations, dispatch_count = check_lines(text, '<fixture>')
        if dispatch_count == 0:
            got = 'hollow'   # 파일 존재 가정 → I-3 hollow-gate
        elif violations:
            got = 'violation'
        else:
            got = 'green'
        status = 'OK' if got == expect else 'MISMATCH'
        if got != expect:
            failed.append((name, expect, got))
        print(f'  [{status}] {name} (expect {expect}, got {got})')
    # ── scan 계층 축 (AC-4 redirect / AC-7 encoding env / 3축 동시위반) — CFP-2884 §8.2B B-3 ──
    scan_failed, scan_total = _self_test_scan_axes()
    failed.extend((name, 'scan-axis', detail) for name, detail in scan_failed)
    total = len(cases) + scan_total
    if failed:
        print(f'[self-test] FAIL — {len(failed)} case mismatch')
        for entry in failed:
            print(f'  - {entry}')
        return 1
    print(f'[self-test] PASS — {total}/{total} case '
          f'(text 축 {len(cases)} RED→GREEN discriminating + scan 축 {scan_total} 3-axis 라벨 판별)')
    return 0


def main(argv):
    args = argv[1:]
    if '--self-test' in args:
        return self_test()
    if not args:
        # 인자 0개 = repo root 기준 default 스캔 디렉터리 (thin wrapper 가 repo root 로 cd)
        paths = [d for d in DEFAULT_SCAN_DIRS if os.path.isdir(d)]
        if not paths:
            # DEFAULT_SCAN_DIRS(=codeforge 소유 Codex 리뷰 dispatch 가 사는 유일 위치) 전부 부재.
            # 경로 부재 fail-safe (consumer no-op degradation): repo root 전체(`.`) 로 확장하면
            # consumer 에 dispatch 발화 0건 → hollow-gate(I-3) false-RED 유발 →
            # byte-identical template↔.github mirror(ADR-005, CONSUMER_ONLY 미등록) 상속이 깨진다.
            # 따라서 `.` 로 넓히지 않고 honest no-op (exit 0) — hollow-gate 는 "codeforge-owned
            # dispatch 경로가 실존할 때만" 발동 (Story §5 판정 / ADR-081 §결정 D15).
            print('[codex-companion-timeout-presence] 스캔 대상 경로(plugins/codeforge-review) 부재 — '
                  'honest no-op (PASS, consumer degradation). codeforge-owned Codex 리뷰 dispatch 부재.')
            return 0
    else:
        for a in args:
            if not os.path.exists(a):
                print(f'[codex-companion-timeout-presence] setup error: 경로 미존재: {a}', file=sys.stderr)
                return 2
        paths = args
    return run_scan(paths)


if __name__ == '__main__':
    sys.exit(main(sys.argv))
