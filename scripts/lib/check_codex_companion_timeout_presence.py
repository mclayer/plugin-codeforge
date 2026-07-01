#!/usr/bin/env python3
# CFP-2545 / ADR-081 Amendment 12 §결정 D14 — Codex companion 브로커 경로 wall-clock 가드 presence lint (SSOT)
# ADR-061 §결정 1 Python-SSOT 패턴 (thin wrapper = scripts/check-codex-companion-timeout-presence.sh)
#
# 목적:
#   codeforge 소유 codex companion dispatch 발화(`node ... codex-companion(.mjs) ... adversarial-review`
#   또는 `task --write`)가 항상 wall-clock 상한(`timeout <N> --kill-after=<K>`) prefix 로 감싸졌는지
#   정적 검사. AC-1 mechanical 강제 층 (markdown 지시만으로는 self-discipline → hollow-gate).
#
# 검사 (dispatch 발화 = "실행 라인" 만; 주석·backtick inline 문서 예시는 대상 아님):
#   1. dispatch 발화 앞에 `timeout <정수>` prefix 존재 (없으면 위반).
#   2. `--kill-after=<정수>` 동반 (없으면 위반).
#   3. N (timeout 초) 이 양의 정수 (0/음수 위반).
#   4. hollow-gate 차단 (invariant I-3): 스캔 대상 파일이 존재하는데 dispatch 발화 총 건수가 0 이면
#      위반 (exit 1) — 파일 구조 drift 로 발화가 lint 스코프를 이탈해도 항상 GREEN 되는 경로 차단.
#   5. 경로 부재 fail-open (consumer no-op): 스캔 대상 파일 자체가 하나도 없으면 honest no-op (exit 0).
#      byte-identical template mirror 를 consumer 가 상속해도 `plugins/codeforge-review/agents/` 경로
#      부재 시 spurious RED 를 내지 않게 하는 degradation (wrapper=파일 존재→발화≥1 강제 / consumer=파일 부재→no-op).
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

# Windows 콘솔 cp949 기본 인코딩에서 em-dash 등 UTF-8 출력 실패 방지 (CI=Linux UTF-8 무관, 로컬 dev 견고성).
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except (AttributeError, ValueError):
    pass

# ── dispatch 발화 식별 패턴 ────────────────────────────────────────────────────
# codeforge 소유 companion dispatch 실행 라인:
#   node ... codex-companion(.mjs) ... adversarial-review ...
#   node ... codex-companion(.mjs) ... task --write ...
# (CMD 변수 경유 `node "$CMD" adversarial-review` 형태 포함 — "codex-companion" 리터럴이 같은 라인에 없을 수 있어
#  node + (adversarial-review|task --write) 조합 + 문맥 companion 을 함께 인정)
_NODE = r'node\s+[^\n]*'
DISPATCH_ADVERSARIAL = re.compile(r'\bnode\b[^\n]*\badversarial-review\b')
DISPATCH_TASK_WRITE = re.compile(r'\bnode\b[^\n]*\btask\s+--write\b')

# timeout 가드 prefix — 라인의 dispatch node 호출 앞에 위치해야 함.
# N 값 형태 2종 허용: 리터럴 정수(`timeout 300`) 또는 env-default(`timeout ${VAR:-300}`).
# env-default 형태는 default 값을 추출해 양수 검증 (design 이 env-override 를 primary 로 규정 — 리터럴만 요구하면 정본 형태를 오탐).
_INT = r'\d+'
_ENV_DEFAULT = r'\$\{[A-Za-z_][A-Za-z0-9_]*:-(\d+)\}'  # ${VAR:-<int>} — default 값 capture
TIMEOUT_PREFIX = re.compile(r'\btimeout\s+(?:(' + _INT + r')|' + _ENV_DEFAULT + r')')
KILL_AFTER = re.compile(r'--kill-after=(?:(' + _INT + r')|' + _ENV_DEFAULT + r')')


def _extract_int(match):
    """TIMEOUT_PREFIX / KILL_AFTER match 에서 정수값 추출 (리터럴 group1 또는 env-default group2)."""
    if match is None:
        return None
    lit, envdef = match.group(1), match.group(2)
    if lit is not None:
        return int(lit)
    if envdef is not None:
        return int(envdef)
    return None

# 스캔 대상 파일 확장자 (dispatch 발화가 사는 markdown/shell)
SCAN_EXTS = ('.md', '.sh', '.yml', '.yaml')

# dispatch 발화 검색 스코프 (파일 목록 하드코딩 금지 — 디렉터리 prefix 기반, E4 차단)
# codeforge 소유 companion dispatch 발화가 사는 유일 위치 = codeforge-review agent md (origin/main 실측).
DEFAULT_SCAN_DIRS = (
    'plugins/codeforge-review',
)


def _iter_files(paths):
    for p in paths:
        if os.path.isfile(p):
            if p.endswith(SCAN_EXTS):
                yield p
        elif os.path.isdir(p):
            for root, _dirs, files in os.walk(p):
                # .git / node_modules 회피
                if '.git' in root.split(os.sep) or 'node_modules' in root.split(os.sep):
                    continue
                for f in files:
                    if f.endswith(SCAN_EXTS):
                        yield os.path.join(root, f)


def _is_doc_example_line(line):
    """dispatch 발화(실행 라인)가 아닌 prose/문서 예시 판정.

    실행 라인 = 코드 블록 안 실제 커맨드. 첫 non-whitespace 토큰이:
      - `timeout` (가드 prefix 로 시작하는 실행 라인)  → 실행
      - `node`    (가드 없이 바로 실행 — 위반 대상)      → 실행
      - `#`       (주석 write-mode 예외, Story §7.2.4 — :91 주석도 검사 대상) → 실행(검사)
    그 외 (prose: `>`/`-`/`**`/한글 서술 등으로 시작하고 node 호출이 문장 중간 backtick 안) = 문서 예시 → 제외.

    이 discriminator 로 §실행 패턴 doc note(`> **... node·Bash ... `adversarial-review --wait` ...**`)는
    제외하고, 코드 블록 안 실제 `timeout ... node ... adversarial-review` / `# timeout ... node ... task --write`
    실행 라인만 검사한다."""
    stripped = line.lstrip()
    # 주석 write-mode 예외: `# timeout ... node ... task --write` 형태 → 검사 대상 (실행 시 활성)
    if stripped.startswith('#'):
        body = stripped[1:].lstrip()
        return not (body.startswith('timeout') or body.startswith('node'))
    # 실행 라인: timeout 가드 prefix 또는 node 직접 호출로 시작
    if stripped.startswith('timeout') or stripped.startswith('node'):
        return False
    # 그 외 = prose/문서 예시
    return True


def check_lines(text, filename):
    """텍스트에서 dispatch 발화 라인을 찾아 timeout 가드 검증. (violations, dispatch_count) 반환."""
    violations = []
    dispatch_count = 0
    for i, raw in enumerate(text.splitlines(), start=1):
        line = raw
        m_adv = DISPATCH_ADVERSARIAL.search(line)
        m_task = DISPATCH_TASK_WRITE.search(line)
        if not (m_adv or m_task):
            continue
        # inline prose 예시 제외 (실행 라인 / 주석 write-mode 예외만 대상)
        if _is_doc_example_line(line):
            continue
        dispatch_count += 1
        kind = 'adversarial-review' if m_adv else 'task --write'
        # timeout prefix 는 dispatch node 호출 *앞* 에 위치해야 함
        node_pos = (m_adv or m_task).start()
        prefix = line[:node_pos]
        mt = TIMEOUT_PREFIX.search(prefix)
        if not mt:
            violations.append(f'{filename}:{i}: dispatch 발화({kind})에 `timeout <N>` prefix 부재 — wall-clock 가드 누락 (ADR-081 §D14)')
            continue
        n = _extract_int(mt)
        if n is not None and n <= 0:
            violations.append(f'{filename}:{i}: `timeout {n}` — N 은 양의 정수여야 함 (0/음수 = 무한대기 미방지)')
        mk = KILL_AFTER.search(line)
        if not mk:
            violations.append(f'{filename}:{i}: dispatch 발화({kind})에 `--kill-after=<K>` 부재 — detached node 좀비 방지 누락')
        else:
            k = _extract_int(mk)
            if k is not None and k < 0:
                violations.append(f'{filename}:{i}: `--kill-after={k}` — K 는 음수 불가')
    return violations, dispatch_count


def run_scan(paths):
    files = list(_iter_files(paths))
    if not files:
        # 경로 부재 fail-open — honest no-op (consumer degradation, byte-identical mirror 상속 안전)
        print('[codex-companion-timeout-presence] 스캔 대상 파일 0건 — honest no-op (PASS, consumer degradation)')
        return 0
    all_violations = []
    total_dispatch = 0
    for f in files:
        try:
            with open(f, 'r', encoding='utf-8') as fh:
                text = fh.read()
        except (OSError, UnicodeDecodeError):
            continue
        v, c = check_lines(text, f)
        all_violations.extend(v)
        total_dispatch += c
    if total_dispatch == 0:
        # hollow-gate 판정 (I-3) vs consumer no-op degradation 구분 —
        # codeforge-owned companion dispatch 의 유일 home = plugins/codeforge-review/agents/ (origin/main 실측).
        # 이 home 이 스캔 트리 안에 실존하면 → 발화 0건 = 파일 구조 drift(발화 스코프 이탈) → hollow-gate exit 1.
        # home 이 부재하면(consumer repo 가 `.` 를 스캔했으나 codeforge-review plugin 미보유) → honest no-op exit 0.
        # workflow 가 `.`(repo root) 를 명시 인자로 주더라도 이 구분으로 consumer false-RED 를 차단
        # (경로 부재 fail-open — Story §5 판정 / ADR-081 §결정 D14).
        home_present = any(
            os.path.join('plugins', 'codeforge-review', 'agents') in os.path.normpath(f)
            or os.path.normpath('plugins/codeforge-review/agents') in os.path.normpath(f)
            for f in files
        )
        if not home_present:
            print('[codex-companion-timeout-presence] 스캔 트리에 codeforge-owned companion dispatch home '
                  '(plugins/codeforge-review/agents/) 부재 — honest no-op (PASS, consumer degradation).')
            return 0
        # hollow-gate 차단 (I-3): home 실존 + 파일 존재하나 dispatch 발화 0건 → 항상 GREEN 방지
        print('[codex-companion-timeout-presence] FAIL (I-3 hollow-gate): '
              'plugins/codeforge-review/agents/ 실존하나 codex companion dispatch 발화'
              '(node ... adversarial-review | task --write) 0건. '
              '발화가 lint 스코프를 이탈했을 가능성 — 스코프/패턴 재확인 필요.')
        return 1
    if all_violations:
        print('[codex-companion-timeout-presence] FAIL — wall-clock 가드 누락:')
        for v in all_violations:
            print('  ' + v)
        return 1
    print(f'[codex-companion-timeout-presence] PASS — dispatch 발화 {total_dispatch}건 전부 timeout 가드 존재.')
    return 0


# ── self-test (D3 inline fixture, CI step 호출) ────────────────────────────────
def self_test():
    cases = [
        # (name, text, expect_exit)
        ('GREEN: timeout+kill-after 가드 존재',
         'timeout ${CODEX_REVIEW_TIMEOUT_SEC:-300} --kill-after=30 node "$CMD" adversarial-review --wait "x"\n', 0),
        ('RED: timeout 가드 제거 (mutation)',
         'node "$CMD" adversarial-review --wait "x"\n', 1),
        ('RED: dispatch 발화 0건 (hollow-gate I-3, 파일 존재)',
         '이 파일에는 dispatch 발화가 없다 — companion 언급만 prose 로.\n', 1),
        ('RED: N=0 (무한대기 미방지)',
         'timeout 0 --kill-after=30 node "$CMD" adversarial-review --wait "x"\n', 1),
        ('RED: N 음수',
         'timeout -5 --kill-after=30 node "$CMD" adversarial-review --wait "x"\n', 1),
        ('RED: --kill-after 누락',
         'timeout 300 node "$CMD" adversarial-review --wait "x"\n', 1),
        ('GREEN: task --write 가드 존재',
         'timeout 300 --kill-after=30 node "$CMD" task --write "x"\n', 0),
        ('RED: task --write 가드 누락',
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
            # 경로 부재 fail-open (consumer no-op degradation): repo root 전체(`.`) 로 확장하면
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
