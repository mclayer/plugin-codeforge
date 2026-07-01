#!/usr/bin/env python3
# CFP-2545 / ADR-081 Amendment 12 §결정 D14 — Codex companion 브로커 경로 wall-clock 가드 presence lint (SSOT)
# CFP-2549 / ADR-139 §결정 4 2안 — background-wait liveness gate 의 Ports&Adapters codex adapter
#   (검사 로직 SSOT = scripts/lib/liveness_check_base.py, 본 파일 = codex-특정 어휘 주입 adapter).
# ADR-061 §결정 1 Python-SSOT 패턴 (thin wrapper = scripts/check-codex-companion-timeout-presence.sh)
#
# 목적:
#   codeforge 소유 codex companion dispatch 발화(`node ... codex-companion(.mjs) ... adversarial-review`
#   또는 `task --write`)가 항상 wall-clock 상한(`timeout <N> --kill-after=<K>`) prefix 로 감싸졌는지
#   정적 검사. AC-1 mechanical 강제 층 (markdown 지시만으로는 self-discipline → hollow-gate).
#
# 검사 (dispatch 발화 = "실행 라인" 만; 주석·backtick inline 문서 예시는 대상 아님):
#   1. dispatch 발화 앞에 option-first `timeout --kill-after=<K> <N>` prefix 존재 (없으면 위반).
#   2. `--kill-after=<정수>` 동반 (없으면 위반).
#   3. N (timeout 초) 이 양의 정수 (0/음수 위반).
#   4. hollow-gate 차단 (invariant I-3): 스캔 대상 파일이 존재하는데 dispatch 발화 총 건수가 0 이면
#      위반 (exit 1) — 파일 구조 drift 로 발화가 lint 스코프를 이탈해도 항상 GREEN 되는 경로 차단.
#   5. 경로 부재 fail-safe (consumer no-op): 스캔 대상 파일 자체가 하나도 없으면 honest no-op (exit 0).
#      byte-identical template mirror 를 consumer 가 상속해도 `plugins/codeforge-review/agents/` 경로
#      부재 시 spurious RED 를 내지 않게 하는 degradation (wrapper=파일 존재→발화≥1 강제 / consumer=파일 부재→no-op).
#
# Ports&Adapters (CFP-2549 재배치): 검사 로직(runnable-form 판정 + 5-part scan driver)은 base 로 추출,
#   본 파일은 codex-특정 dispatch 패턴 / DEFAULT_SCAN_DIRS / home_marker / 진단 메시지 어휘만 보유.
#   behavior 무변경 (self-test 9 case + 외부 테스트 회귀 0).
#
# Usage:
#   check_codex_companion_timeout_presence.py [<path> ...]   # 인자 = 스캔 대상 (파일 또는 디렉터리)
#   check_codex_companion_timeout_presence.py                # 인자 0개 = repo root 스캔
#   check_codex_companion_timeout_presence.py --self-test    # inline fixture RED/GREEN 판별 (CI D3 step)
#
# Exit code:
#   0 = PASS (모든 dispatch 발화에 timeout 가드 존재) 또는 honest no-op (대상 파일 부재)
#   1 = 위반 (가드 누락 dispatch 발화 ≥1, 또는 파일 존재하나 발화 0건 = hollow-gate)
#   2 = setup error (인자 경로 미존재 등)
#
# ReDoS-safe: anchored 고정 리터럴 + \d+ (catastrophic backtracking 유발 nested quantifier 부재).

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import liveness_check_base as base

# Windows 콘솔 cp949 기본 인코딩에서 em-dash 등 UTF-8 출력 실패 방지 (CI=Linux UTF-8 무관, 로컬 dev 견고성).
base.configure_utf8_stdout()

# ── dispatch 발화 식별 패턴 (codex adapter 어휘) ────────────────────────────────
# codeforge 소유 companion dispatch 실행 라인:
#   node ... codex-companion(.mjs) ... adversarial-review ...
#   node ... codex-companion(.mjs) ... task --write ...
# (CMD 변수 경유 `node "$CMD" adversarial-review` 형태 포함 — "codex-companion" 리터럴이 같은 라인에 없을 수 있어
#  node + (adversarial-review|task --write) 조합 + 문맥 companion 을 함께 인정)
DISPATCH_ADVERSARIAL = re.compile(r'\bnode\b[^\n]*\badversarial-review\b')
DISPATCH_TASK_WRITE = re.compile(r'\bnode\b[^\n]*\btask\s+--write\b')

# base 에 주입할 dispatch 패턴 + 발화 종류 라벨 (index 정합)
DISPATCH_PATTERNS = [DISPATCH_ADVERSARIAL, DISPATCH_TASK_WRITE]
KIND_LABELS = ['adversarial-review', 'task --write']

# 스캔 대상 파일 확장자 (dispatch 발화가 사는 markdown/shell)
SCAN_EXTS = ('.md', '.sh', '.yml', '.yaml')

# dispatch 발화 검색 스코프 (파일 목록 하드코딩 금지 — 디렉터리 prefix 기반, E4 차단)
# codeforge 소유 companion dispatch 발화가 사는 유일 위치 = codeforge-review agent md (origin/main 실측).
DEFAULT_SCAN_DIRS = (
    'plugins/codeforge-review',
)

# hollow-gate(I-3) vs consumer no-op 구분 기준 = codeforge-owned companion dispatch 의 유일 home.
HOME_MARKER = os.path.join('plugins', 'codeforge-review', 'agents')

ADAPTER_NAME = 'codex-companion-timeout-presence'

# 실행 라인 discriminator: 첫 토큰이 timeout(가드 prefix) 또는 node(직접 실행)면 검사 대상.
_is_doc_example_line = base.make_execution_line_discriminator(('timeout', 'node'))


# ── 진단 메시지 어휘 (codex adapter — 기존 문구 verbatim 유지) ──────────────────────
def _msg_n_nonpos(filename, i, kind, n=None, k=None):
    return f'{filename}:{i}: `timeout ... {n}` — N(duration) 은 양의 정수여야 함 (0/음수 = 무한대기 미방지)'


def _msg_k_neg(filename, i, kind, n=None, k=None):
    return f'{filename}:{i}: `--kill-after={k}` — K 는 음수 불가'


def _msg_duration_first(filename, i, kind):
    return (
        f'{filename}:{i}: dispatch 발화({kind}) `timeout <N> --kill-after=<K>` = **duration-first 오배열** — '
        f'GNU coreutils 는 `--kill-after` 를 실행 명령으로 오인해 exit 127 (가드 무효). '
        f'option-first `timeout --kill-after=<K> <N>` 로 재배열 필요 (ADR-081 §D14)')


def _msg_token_present_no_killafter(filename, i, kind):
    return (
        f'{filename}:{i}: dispatch 발화({kind}) `timeout` 은 있으나 `--kill-after=<K>` 부재 또는 형태 불량 — '
        f'runnable option-first `timeout --kill-after=<K> <N>` 필요 (detached node 좀비 방지 + 가드 유효, ADR-081 §D14)')


def _msg_absent(filename, i, kind):
    return (
        f'{filename}:{i}: dispatch 발화({kind})에 `timeout` wall-clock 가드 prefix 부재 — 무한 대기 미방지 (ADR-081 §D14)')


DIAG_MESSAGES = {
    'n_nonpos': _msg_n_nonpos,
    'k_neg': _msg_k_neg,
    'duration_first': _msg_duration_first,
    'token_present_no_killafter': _msg_token_present_no_killafter,
    'absent': _msg_absent,
}


# ── scan 출력 메시지 어휘 (codex adapter — 기존 문구 verbatim 유지) ────────────────────
MESSAGES = {
    'noop_no_files': lambda: (
        '[codex-companion-timeout-presence] 스캔 대상 파일 0건 — honest no-op (PASS, consumer degradation)'),
    'noop_no_home': lambda: (
        '[codex-companion-timeout-presence] 스캔 트리에 codeforge-owned companion dispatch home '
        '(plugins/codeforge-review/agents/) 부재 — honest no-op (PASS, consumer degradation).'),
    'fail_hollow': lambda: (
        '[codex-companion-timeout-presence] FAIL (I-3 hollow-gate): '
        'plugins/codeforge-review/agents/ 실존하나 codex companion dispatch 발화'
        '(node ... adversarial-review | task --write) 0건. '
        '발화가 lint 스코프를 이탈했을 가능성 — 스코프/패턴 재확인 필요.'),
    'fail_violations': lambda violations: (
        '[codex-companion-timeout-presence] FAIL — wall-clock 가드 누락:\n'
        + '\n'.join('  ' + v for v in violations)),
    'pass': lambda total: (
        f'[codex-companion-timeout-presence] PASS — dispatch 발화 {total}건 전부 runnable option-first timeout 가드 존재.'),
}


def check_lines(text, filename):
    """텍스트에서 dispatch 발화 라인을 찾아 timeout 가드 검증. (violations, dispatch_count) 반환.
    (self-test 및 외부 테스트가 직접 호출하는 공개 API — base 로 위임, behavior 무변경.)"""
    return base.check_lines(text, filename, DISPATCH_PATTERNS, _is_doc_example_line,
                            KIND_LABELS, ADAPTER_NAME, DIAG_MESSAGES)


def run_scan(paths):
    return base.check_liveness_presence(
        paths, DISPATCH_PATTERNS, SCAN_EXTS, HOME_MARKER, ADAPTER_NAME,
        KIND_LABELS, _is_doc_example_line, DIAG_MESSAGES, MESSAGES)


# ── self-test (D3 inline fixture, CI step 호출) ────────────────────────────────
def self_test():
    # ★ runnable-form 강제 (CFP-2545 구현리뷰 FIX iter1): GREEN = option-first `timeout --kill-after=<K> <N>`,
    #   RED = duration-first(broken, exit 127) / timeout 부재 / N=0 / kill-after 누락. 실행 축은 tests/scripts 가 결박.
    cases = [
        # (name, text, expect_exit)
        ('GREEN: option-first (env-default) 가드 존재',
         'timeout --kill-after=${CODEX_REVIEW_KILL_AFTER_SEC:-30} ${CODEX_REVIEW_TIMEOUT_SEC:-300} node "$CMD" adversarial-review --wait "x"\n', 0),
        ('GREEN: option-first (리터럴) task --write',
         'timeout --kill-after=30 300 node "$CMD" task --write "x"\n', 0),
        ('RED: duration-first 오배열 (broken, exit 127)',
         'timeout ${CODEX_REVIEW_TIMEOUT_SEC:-300} --kill-after=30 node "$CMD" adversarial-review --wait "x"\n', 1),
        ('RED: duration-first 리터럴 (broken)',
         'timeout 300 --kill-after=30 node "$CMD" adversarial-review --wait "x"\n', 1),
        ('RED: timeout 가드 제거 (mutation)',
         'node "$CMD" adversarial-review --wait "x"\n', 1),
        ('RED: dispatch 발화 0건 (hollow-gate I-3, 파일 존재)',
         '이 파일에는 dispatch 발화가 없다 — companion 언급만 prose 로.\n', 1),
        ('RED: N=0 (무한대기 미방지, option-first)',
         'timeout --kill-after=30 0 node "$CMD" adversarial-review --wait "x"\n', 1),
        ('RED: --kill-after 누락 (option 부재)',
         'timeout 300 node "$CMD" adversarial-review --wait "x"\n', 1),
        ('RED: task --write 가드 제거',
         'node "$CMD" task --write "x"\n', 1),
    ]
    failed = []
    for name, text, expect in cases:
        violations, dispatch_count = check_lines(text, '<fixture>')
        if dispatch_count == 0:
            got = 1  # hollow-gate (파일 존재 가정)
        elif violations:
            got = 1
        else:
            got = 0
        status = 'OK' if got == expect else 'MISMATCH'
        if got != expect:
            failed.append((name, expect, got))
        print(f'  [{status}] {name} (expect exit {expect}, got {got})')
    if failed:
        print(f'[self-test] FAIL — {len(failed)} case mismatch')
        return 1
    print(f'[self-test] PASS — {len(cases)}/{len(cases)} case (RED→GREEN discriminating 검증)')
    return 0


def main(argv):
    args = argv[1:]
    if '--self-test' in args:
        return self_test()
    if not args:
        # 인자 0개 = repo root 기준 default 스캔 디렉터리 (thin wrapper 가 repo root 로 cd)
        paths = [d for d in DEFAULT_SCAN_DIRS if os.path.isdir(d)]
        if not paths:
            # DEFAULT_SCAN_DIRS(=codeforge 소유 companion dispatch 가 사는 유일 위치) 전부 부재.
            # 경로 부재 fail-safe (consumer no-op degradation): repo root 전체(`.`) 로 확장하면
            # consumer 에 companion dispatch 발화 0건 → hollow-gate(I-3) false-RED 유발 →
            # byte-identical template↔.github mirror(ADR-005, CONSUMER_ONLY 미등록) 상속이 깨진다.
            # 따라서 `.` 로 넓히지 않고 honest no-op (exit 0) — hollow-gate 는 "codeforge-owned
            # dispatch 경로가 실존할 때만" 발동 (Story §5 판정 / ADR-081 §결정 D14).
            print('[codex-companion-timeout-presence] 스캔 대상 경로(plugins/codeforge-review) 부재 — '
                  'honest no-op (PASS, consumer degradation). codeforge-owned companion dispatch 부재.')
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
