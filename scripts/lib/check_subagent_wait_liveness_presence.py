#!/usr/bin/env python3
# CFP-2549 / ADR-139 INV-L1~L4 + I-3 hollow-gate + consumer no-op fail-safe — general subagent-wait liveness presence lint
# ADR-061 §결정 1 Python-SSOT 패턴 (thin wrapper = scripts/check-subagent-wait-liveness-presence.sh)
#   + §결정 11 ReDoS-safe (line-by-line, anchored 리터럴 + \d+, per-entry cap)
# 검사 로직 SSOT = scripts/lib/liveness_check_base.py (본 파일 = general 어휘 주입 Ports&Adapters adapter).
# tier: [measurement]  (L3 delivery-gap detection lever — CFP-2573 / ADR-144 §결정 7 / ADR-139 Amendment 1)
#
# CFP-2573 AC-3 확장 (adapter-local — liveness_check_base.py 무손상): timeout-guard presence 검사에 더해
#   playbook §3.10.1 의 delivery-gap 규율 anchor(spawn-then-blind-wait 금지 + force-resume + lead-collect)
#   존재를 assert. playbook 실존하나 anchor 부재면 RED(hollow-gate 확장). ADR-139 Amendment 1 / ADR-144 §결정 4.
#
# 목적:
#   `docs/orchestrator-playbook.md` 의 background-wait liveness gate 공통 규약을 정적 검사.
#   ADR-139 이 codex-companion 특정 §D14 를 "모든 codeforge-owned background subagent 대기" 로 일반화 —
#   본 adapter 는 그 일반 dispatch-wait convention 을 lint 한다.
#
# 검사 대상 dispatch 발화 (background dispatch utterance):
#   background-dispatch 유틸리티 발화(`run_in_background` OR `bg spawn`)를 담은 실행/규약 라인이,
#   INV-L1(wall-clock ceiling)·INV-L2(fail-open 금지)를 강제하려면 항상 runnable option-first
#   `timeout --kill-after=<K> <N>` 가드 prefix 로 감싸져야 함. 가드는 base(어휘 무관) 로 검사.
#
# 검사 (dispatch 발화 = "실행 라인/규약 라인" 만; prose backtick 언급은 대상 아님):
#   1. dispatch 발화(run_in_background|bg spawn) 앞에 option-first `timeout --kill-after=<K> <N>` 존재 (없으면 위반).
#      → INV-L1 wall-clock ceiling + runnable-form (duration-first 는 exit 127 broken → RED).
#   2. `--kill-after=<정수>` 동반 + N 양의 정수 (누락/N<=0/K<0 위반).
#   3. hollow-gate 차단 (invariant I-3): 스캔 대상(docs/orchestrator-playbook.md)이 tree 에 존재하는데
#      background-wait liveness convention 발화 총 건수가 0 이면 위반 (exit 1) — 규약 단락이 silently
#      삭제/드리프트해 lint 스코프를 이탈해도 항상 GREEN 되는 경로 차단.
#   4. 경로 부재 fail-safe (consumer no-op): docs/orchestrator-playbook.md 자체가 부재하면 (consumer 는
#      playbook 미보유) honest no-op (exit 0).
#
# Usage:
#   check_subagent_wait_liveness_presence.py [<path> ...]   # 인자 = 스캔 대상 (파일 또는 디렉터리)
#   check_subagent_wait_liveness_presence.py                # 인자 0개 = docs/orchestrator-playbook.md 스캔
#   check_subagent_wait_liveness_presence.py --self-test    # inline fixture RED/GREEN 판별 (CI step)
#
# Exit code:
#   0 = PASS (모든 dispatch 발화에 timeout 가드 존재) 또는 honest no-op (대상 파일 부재)
#   1 = 위반 (가드 누락 dispatch 발화 ≥1, 또는 playbook 존재하나 발화 0건 = hollow-gate)
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

# ── dispatch 발화 식별 패턴 (general subagent-wait adapter 어휘) ────────────────────
# background dispatch 유틸리티 발화:
#   run_in_background  (harness Agent/Bash background dispatch)
#   bg spawn           (background spawn 규약 어휘)
# 규약 = 이 발화를 담은 실행/규약 라인은 항상 runnable option-first timeout 가드 prefix 로 감싸야 함.
DISPATCH_RUN_IN_BACKGROUND = re.compile(r'\brun_in_background\b')
DISPATCH_BG_SPAWN = re.compile(r'\bbg\s+spawn\b')

DISPATCH_PATTERNS = [DISPATCH_RUN_IN_BACKGROUND, DISPATCH_BG_SPAWN]
KIND_LABELS = ['run_in_background', 'bg spawn']

# max-wait / liveness 어휘 (INV-L1 ceiling vocab) — 규약 단락이 max-wait ceiling 을 언급하는지 확인용.
# (detect_execution_backed_selftest helper 로 presence 축만 판정 — 진단 힌트/규약 준수 참조.)
MAXWAIT_VOCAB = [
    re.compile(r'\bmax-?wait\b', re.IGNORECASE),
    re.compile(r'wall-?clock'),
    re.compile(r'\bliveness\b', re.IGNORECASE),
]

# ── CFP-2573 AC-3: delivery-gap 규율 anchor (playbook §3.10.1 강화 문단 presence) ──────────────
# playbook 이 실존하는데 아래 3 anchor 가 전부 존재하지 않으면 hollow-gate 확장 RED
#   (force-resume/delivery-gap 규율 삭제 → presence-lint RED). ReDoS-safe (고정 리터럴).
DELIVERY_GAP_ANCHORS = [
    ('spawn-then-blind-wait', re.compile(r'spawn-then-blind-wait')),
    ('force-resume', re.compile(r'force-resume')),
    ('lead-collect', re.compile(r'lead-collect')),
]

# 스캔 대상 파일 확장자 (playbook markdown 우선, 일반 유지).
SCAN_EXTS = ('.md', '.sh', '.yml', '.yaml')

# dispatch 발화 검색 스코프 = orchestrator playbook (background-wait liveness 공통 규약이 사는 위치).
DEFAULT_SCAN_TARGETS = (
    os.path.join('docs', 'orchestrator-playbook.md'),
)

# hollow-gate(I-3) vs consumer no-op 구분 기준 = playbook 파일 존재 (home_marker analog).
HOME_MARKER = os.path.join('docs', 'orchestrator-playbook.md')

ADAPTER_NAME = 'subagent-wait-liveness-presence'

# 실행 라인 discriminator: 첫 토큰이 timeout(가드 prefix) 또는 background dispatch 유틸리티 토큰이면
# 검사 대상 (규약 라인). prose backtick 언급(`> ...` / `- ...` / 서술)은 제외.
_EXEC_FIRST_TOKENS = ('timeout', 'run_in_background', 'bg')
_is_doc_example_line = base.make_execution_line_discriminator(_EXEC_FIRST_TOKENS)


# ── 진단 메시지 어휘 (general adapter) ──────────────────────────────────────────
def _msg_n_nonpos(filename, i, kind, n=None, k=None):
    return f'{filename}:{i}: `timeout ... {n}` — N(max-wait duration) 은 양의 정수여야 함 (0/음수 = 무한대기 미방지, INV-L1 위반)'


def _msg_k_neg(filename, i, kind, n=None, k=None):
    return f'{filename}:{i}: `--kill-after={k}` — K 는 음수 불가'


def _msg_duration_first(filename, i, kind):
    return (
        f'{filename}:{i}: background-wait 발화({kind}) `timeout <N> --kill-after=<K>` = **duration-first 오배열** — '
        f'GNU coreutils 는 `--kill-after` 를 실행 명령으로 오인해 exit 127 (가드 무효). '
        f'option-first `timeout --kill-after=<K> <N>` 로 재배열 필요 (ADR-139 INV-L1)')


def _msg_token_present_no_killafter(filename, i, kind):
    return (
        f'{filename}:{i}: background-wait 발화({kind}) `timeout` 은 있으나 `--kill-after=<K>` 부재 또는 형태 불량 — '
        f'runnable option-first `timeout --kill-after=<K> <N>` 필요 (idle-timeout kill 유효 + INV-L1, ADR-139)')


def _msg_absent(filename, i, kind):
    return (
        f'{filename}:{i}: background-wait 발화({kind})에 `timeout` wall-clock 가드 prefix 부재 — '
        f'max-wait ceiling 없이 무한 대기 (INV-L1/INV-L2 위반, ADR-139)')


DIAG_MESSAGES = {
    'n_nonpos': _msg_n_nonpos,
    'k_neg': _msg_k_neg,
    'duration_first': _msg_duration_first,
    'token_present_no_killafter': _msg_token_present_no_killafter,
    'absent': _msg_absent,
}


# ── scan 출력 메시지 어휘 (general adapter) ────────────────────────────────────────
MESSAGES = {
    'noop_no_files': lambda: (
        '[subagent-wait-liveness-presence] 스캔 대상 파일 0건 — honest no-op (PASS, consumer degradation)'),
    'noop_no_home': lambda: (
        '[subagent-wait-liveness-presence] 스캔 트리에 orchestrator playbook '
        '(docs/orchestrator-playbook.md) 부재 — honest no-op (PASS, consumer degradation).'),
    'fail_hollow': lambda: (
        '[subagent-wait-liveness-presence] FAIL (I-3 hollow-gate): '
        'docs/orchestrator-playbook.md 실존하나 background-wait liveness convention 발화'
        '(run_in_background | bg spawn) 0건. '
        '규약 단락이 삭제/드리프트해 lint 스코프를 이탈했을 가능성 — 스코프/패턴 재확인 필요 (ADR-139 I-3).'),
    'fail_violations': lambda violations: (
        '[subagent-wait-liveness-presence] FAIL — background-wait wall-clock 가드 누락 (ADR-139 INV-L1/L2):\n'
        + '\n'.join('  ' + v for v in violations)),
    'pass': lambda total: (
        f'[subagent-wait-liveness-presence] PASS — background-wait 발화 {total}건 전부 '
        f'runnable option-first timeout 가드 존재 (INV-L1 wall-clock ceiling 강제).'),
}


def check_lines(text, filename):
    """텍스트에서 background-wait dispatch 발화 라인을 찾아 timeout 가드 검증. (violations, dispatch_count) 반환.
    (self-test 및 외부 테스트가 직접 호출하는 공개 API — base 로 위임.)"""
    return base.check_lines(text, filename, DISPATCH_PATTERNS, _is_doc_example_line,
                            KIND_LABELS, ADAPTER_NAME, DIAG_MESSAGES)


def check_delivery_gap_discipline(text):
    """playbook 텍스트에 delivery-gap 규율 anchor(spawn-then-blind-wait 금지 + force-resume + lead-collect)
    전부 존재하는지 검사. 부재 anchor label 리스트 반환 (빈 = PASS). (self-test/외부 테스트 공개 API — AC-3.)"""
    missing = []
    for label, pat in DELIVERY_GAP_ANCHORS:
        if not pat.search(text):
            missing.append(label)
    return missing


def _find_playbook(paths):
    """스캔 paths 안 docs/orchestrator-playbook.md 실경로 반환 (없으면 None)."""
    marker = os.path.normpath(HOME_MARKER)
    for f in base._iter_files(paths, SCAN_EXTS):
        if marker in os.path.normpath(f):
            return f
    return None


def _run_delivery_gap_scan(paths):
    """playbook 실존 시 delivery-gap 규율 anchor presence 검사 (AC-3 hollow-gate 확장).
    exit 0 = PASS 또는 playbook 부재 no-op / 1 = anchor 부재 (RED)."""
    pb = _find_playbook(paths)
    if pb is None:
        return 0  # playbook 부재 → consumer no-op (base 가 이미 no-op 처리)
    try:
        with open(pb, 'r', encoding='utf-8') as fh:
            text = fh.read()
    except (OSError, UnicodeDecodeError):
        return 0
    missing = check_delivery_gap_discipline(text)
    if missing:
        print('[subagent-wait-liveness-presence] FAIL (AC-3 delivery-gap hollow-gate 확장): '
              'docs/orchestrator-playbook.md 실존하나 delivery-gap 규율 anchor 부재 — '
              + ', '.join(missing)
              + ' (spawn-then-blind-wait 금지 + force-resume + lead-collect 필수, '
                'ADR-139 Amendment 1 / ADR-144 §결정 4).')
        return 1
    return 0


def run_scan(paths):
    base_exit = base.check_liveness_presence(
        paths, DISPATCH_PATTERNS, SCAN_EXTS, HOME_MARKER, ADAPTER_NAME,
        KIND_LABELS, _is_doc_example_line, DIAG_MESSAGES, MESSAGES)
    # CFP-2573 AC-3 확장: delivery-gap 규율 anchor presence (adapter-local — base 무손상)
    dg_exit = _run_delivery_gap_scan(paths)
    if base_exit == 2 or dg_exit == 2:
        return 2
    return 1 if (base_exit == 1 or dg_exit == 1) else 0


# ── self-test (inline fixture, CI step 호출) ────────────────────────────────────
def self_test():
    # GREEN = option-first `timeout --kill-after=<K> <N>` 가 background-wait 발화(run_in_background/bg spawn)
    #   를 감싸고 max-wait vocab 동반. RED = duration-first(broken) / timeout 부재 / 발화 0건(hollow-gate) /
    #   N=0 / kill-after 누락. codex adapter self-test 구조/메시지 mirror (어휘 general 화).
    cases = [
        # (name, text, expect_exit)
        ('GREEN: option-first (env-default) run_in_background max-wait 가드',
         'timeout --kill-after=${SUBAGENT_KILL_AFTER_SEC:-30} ${SUBAGENT_MAX_WAIT_SEC:-300} run_in_background  # max-wait ceiling\n', 0),
        ('GREEN: option-first (리터럴) bg spawn',
         'timeout --kill-after=30 300 bg spawn worker  # wall-clock liveness ceiling\n', 0),
        ('RED: duration-first 오배열 (broken, exit 127)',
         'timeout ${SUBAGENT_MAX_WAIT_SEC:-300} --kill-after=30 run_in_background  # max-wait\n', 1),
        ('RED: duration-first 리터럴 (broken)',
         'timeout 300 --kill-after=30 bg spawn worker  # wall-clock\n', 1),
        ('RED: timeout 가드 제거 (mutation)',
         'run_in_background worker  # max-wait ceiling 언급하나 timeout 부재\n', 1),
        ('RED: background-wait 발화 0건 (hollow-gate I-3, 파일 존재)',
         '이 문단에는 background-wait 규약 발화가 없다 — liveness 를 prose 로만 언급.\n', 1),
        ('RED: N=0 (무한대기 미방지, option-first)',
         'timeout --kill-after=30 0 run_in_background worker  # max-wait\n', 1),
        ('RED: --kill-after 누락 (option 부재)',
         'timeout 300 run_in_background worker  # wall-clock\n', 1),
        ('RED: bg spawn 가드 제거',
         'bg spawn worker  # liveness max-wait 언급하나 timeout 부재\n', 1),
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

    # CFP-2573 AC-3 확장: delivery-gap 규율 anchor dimension (기존 timeout-guard 케이스 무손상 추가).
    #   GREEN = spawn-then-blind-wait 금지 + force-resume + lead-collect 3 anchor 존재.
    #   RED = delivery-gap 규율(force-resume/anchor) 삭제 mutation → RED 전환 (AC-3 mutation proof).
    dg_cases = [
        ('GREEN: delivery-gap 규율 anchor 3종 존재',
         'PL 은 spawn-then-blind-wait 금지 — 수집은 LEAD 소유. stall 시 lead force-resume. '
         'named lead-collect routine.\n', 0),
        ('RED: delivery-gap 규율 삭제 (force-resume/anchor delete mutation)',
         '이 문단엔 background-wait 규약만 있고 delivery-gap 규율(anchor)이 없다.\n', 1),
    ]
    for name, text, expect in dg_cases:
        missing = check_delivery_gap_discipline(text)
        got = 1 if missing else 0
        status = 'OK' if got == expect else 'MISMATCH'
        if got != expect:
            failed.append((name, expect, got))
        print(f'  [{status}] {name} (expect exit {expect}, got {got}; missing={missing})')

    total = len(cases) + len(dg_cases)
    if failed:
        print(f'[self-test] FAIL — {len(failed)} case mismatch')
        return 1
    print(f'[self-test] PASS — {total}/{total} case (timeout-guard RED→GREEN + AC-3 delivery-gap '
          'mutation discriminating)')
    return 0


def main(argv):
    args = argv[1:]
    if '--self-test' in args:
        return self_test()
    if not args:
        # 인자 0개 = repo root 기준 default 스캔 대상 (thin wrapper 가 repo root 로 cd)
        paths = [t for t in DEFAULT_SCAN_TARGETS if os.path.exists(t)]
        if not paths:
            # DEFAULT_SCAN_TARGETS(=background-wait liveness 규약이 사는 유일 위치) 부재.
            # 경로 부재 fail-safe (consumer no-op degradation): consumer 는 orchestrator-playbook 미보유 →
            # 스캔 대상 부재 → honest no-op (exit 0). hollow-gate 는 "playbook 이 실존할 때만" 발동.
            print('[subagent-wait-liveness-presence] 스캔 대상 경로(docs/orchestrator-playbook.md) 부재 — '
                  'honest no-op (PASS, consumer degradation). orchestrator playbook 부재.')
            return 0
    else:
        for a in args:
            if not os.path.exists(a):
                print(f'[subagent-wait-liveness-presence] setup error: 경로 미존재: {a}', file=sys.stderr)
                return 2
        paths = args
    return run_scan(paths)


if __name__ == '__main__':
    sys.exit(main(sys.argv))
