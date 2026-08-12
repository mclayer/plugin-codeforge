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
# CFP-2929 §3.8 B-10 / §5.1 B-6·B-8 — **4번째 disjoint 축** `scan_output_path_dialect` (출력 경로 방언
#   정규화 presence + `-o` 식별자 대조) 합류 ⊕ **사정권 확대** `DEFAULT_SCAN_DIRS`
#   `('plugins/codeforge-review',)` → `('plugins',)` (discovery 기반 — 아래 상수 주석). 축 2·3 과 동형
#   shape (자체 라벨 진단 + 독립 rc → max() 합성). warning tier 유지 · required 승격 0.
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
#   8. 출력 경로 방언 정규화 (E6 4번째 disjoint 축 — CFP-2929 §3.8 **B-10**):
#      `-o <출력경로>` 를 동반하는 codex exec dispatch 실행 발화를 보유한 파일은
#      (a) `<IDENT>=$(cygpath …)` **정규화 대입**을 (주석 아닌 실행 줄에) 보유해야 하고,
#      (b) `-o "$VAR"` 형 argv 의 `VAR` 가 그 정규화의 **대입 대상 식별자 집합**(직접 대입 ∪ 순수
#          복사 대입 `X="$Y"` 폐포)에 속해야 한다. 위반 = RED.
#      ★ **위치 비의존**(B-10): 정규화가 preflight 함수 내부(P-0)로 이동했으므로 "dispatch 라인 직전
#        별도 줄" 로 정의하면 born-red 다. 판정 대상 = **변수 흐름**이지 줄 위치가 아니다.
#      ★★ **정직 상한 (over-claim 금지 — ADR-119 / ADR-168 §결정 16)**: 본 축은 셸 **정적 리터럴
#        대조**이며 데이터 흐름 분석이 아니다. 다음은 **잡지 못한다** —
#          · 별칭·간접 재대입 (`eval`, `declare -n` nameref, `${!ref}` 간접 확장, 배열·`$@` 경유)
#          · **정규화 이후의 재대입**(`OUT="$(cygpath …)"` 뒤 `OUT=/tmp/x` 로 되돌리기 — 본 축은
#            줄 순서를 보지 않으므로 GREEN 을 유지한다)
#          · 함수 인자·서브셸 경계를 넘는 전파, 외부 파일 source
#        따라서 본 축 GREEN 은 "출력 경로가 런타임에 정규화된다"의 **보증이 아니라 presence 신호**다
#        (warning tier). 런타임 진실의 결박 = §8.1 Windows 3-arm oracle (execution-backed).
#
# Ports&Adapters (CFP-2549 재배치): 검사 로직(runnable-form 판정 + 5-part scan driver)은 base 로 추출,
#   본 파일은 codex-특정 dispatch 패턴 / DEFAULT_SCAN_DIRS / home_marker / 진단 메시지 어휘 + AC-4 redirect 축
#   + AC-7 encoding env 축 + E6 output-path dialect 축만 보유.
#
# Usage:
#   check_codex_companion_timeout_presence.py [<path> ...]   # 인자 = 스캔 대상 (파일 또는 디렉터리)
#   check_codex_companion_timeout_presence.py                # 인자 0개 = repo root 스캔
#   check_codex_companion_timeout_presence.py --self-test    # inline fixture RED/GREEN 판별 (CI D3 step)
#   check_codex_companion_timeout_presence.py --list-scope-dirs
#                                                            # DEFAULT_SCAN_DIRS 열거 (사정권 side)
#   check_codex_companion_timeout_presence.py --list-dispatch-surfaces [<path> ...]
#                                                            # dispatch 발화 보유 파일 열거 (discovery side,
#                                                            #   인자 0개 = repo root `.`) — AC-13 차집합 test 용
#
# Exit code:
#   0 = PASS (모든 dispatch 발화에 timeout 가드 + `- <` redirect 존재, dispatch 보유 파일에 인코딩 env
#       export + 출력 경로 정규화 존재) 또는 honest no-op (대상 파일 부재)
#   1 = 위반 (가드/redirect 누락 dispatch 발화 ≥1, 인코딩 env export 누락 dispatch 파일 ≥1,
#       `-o` 경로 정규화 부재·식별자 불일치 dispatch 발화 ≥1, 또는 파일 존재하나 발화 0건 = hollow-gate)
#   2 = setup error (인자 경로 미존재 등)
#
# ReDoS 관측: line-by-line bounded scan + anchored 고정 리터럴 + \d+ + zero-width lookahead `[^\n]*`
#   (단일 선형 pass, nested quantifier 부재 = catastrophic backtracking 구조 부재 — structural, per-line
#   bounded). CFP-2884 추가분 (ENCODING_ENV_PATTERNS) 도 동일 형상 — 라인 앵커(`^...$`, MULTILINE) +
#   단일 문자클래스 `+`/`*` 1개 + 고정 리터럴 tail (중첩 quantifier 0, 교대 backtrack 분기 0).
#   임의 입력 총 작업량 무해성 절대단정 아님 (honest ceiling — ADR-168 §결정 16 (구 ADR-082 §결정 16, 재제정 CFP-2840) / ADR-151 §결정 7).
#   재현 가능한 복잡도 회귀 self-test 부재 — 위 서술은 **구조 관측**이지 벤치마크 증거 아님 (bounded
#   degradation 천장, 임의 입력 무해 아님).
#   CFP-2929 추가분 (CYGPATH_ASSIGN / COPY_ASSIGN / DASH_O_ARG / VAR_ARG) 도 동일 형상 — 고정 리터럴
#   (`=$(cygpath` / `-o`) + 단일 문자클래스 `+`/`*` + 선택적 그룹 (중첩 quantifier 0, 교대 backtrack
#   분기 0). ★ 단 `_normalized_identifiers` 의 복사-대입 **폐포 루프**는 정규식이 아닌 **알고리즘** 축
#   비용이다 — 최악 O(파일당 복사대입 수²) 이며 파일 크기로 bound 된다 (무한 루프 불가: 매 회차
#   집합이 단조 증가하고 상한 = 후보 식별자 수). 이 역시 **구조 관측**이지 벤치마크 증거 아님.

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

# ── 출력 경로 방언 정규화 (E6 4번째 축 — CFP-2929 §3.8 B-10) ─────────────────────────
# (a) 정규화 **대입** presence: `<IDENT>=$(cygpath …)` / `<IDENT>="$(cygpath …)"`.
#     ★ 단순 `cygpath` **언급**(산문·주석)은 정규화가 아니다 — 대입 형태를 요구해 substring hollow 차단
#       (주석 줄 자체는 아래 `_normalized_identifiers` 가 line-level 로 배제. AC-4 anti-substring).
#     ★ 문(statement) 경계 앵커: 줄 시작 / 공백 / `;`·`&`·`|`·`(` 직후 — `local _n; _n="$(cygpath …)"`
#       (CodexReviewAgent.md P-0 실형태) 처럼 한 줄에 2문이 있는 형태를 놓치지 않기 위함.
_STMT_HEAD = r'(?:^|[;&|(]|[ \t])'
_IDENT = r'([A-Za-z_][A-Za-z0-9_]*)'
CYGPATH_ASSIGN = re.compile(
    _STMT_HEAD + r'(?:local[ \t]+)?' + _IDENT + r'=(?:")?\$\((?:[ \t]*)cygpath\b', re.MULTILINE)
# (b) 순수 복사 대입 `X="$Y"` / `X=$Y` / `X="${Y}"` — RHS 가 **변수 하나뿐**일 때만 (tail 앵커로 강제).
#     P-0 실형태 `OUT_JSON="$_n"` 처럼 정규화 산출이 1-hop 을 거쳐 argv 변수에 도달하는 경로를 잇는다.
COPY_ASSIGN = re.compile(
    _STMT_HEAD + r'(?:local[ \t]+)?' + _IDENT + r'="?\$\{?' + _IDENT +
    r'\}?"?(?=[ \t]*(?:$|[;&|)#]))', re.MULTILINE)
# dispatch 발화 라인의 `-o <arg>` 추출. `--output-schema` 오탐 회피 = `-o` 앞이 시작/공백 (그 경우 앞
#   문자가 `-` 라 unmatch) ∧ 뒤에 공백 필수 (`-outdir` 류 unmatch).
DASH_O_ARG = re.compile(r'(?:^|[ \t])-o[ \t]+(\S+)')
# `-o` argv 가 변수 참조 형인지 (그 경우에만 (b) 식별자 대조가 성립 — 리터럴 경로는 (a) 만 적용).
VAR_ARG = re.compile(r'^"?\$\{?([A-Za-z_][A-Za-z0-9_]*)\}?"?$')

# 스캔 대상 파일 확장자 (dispatch 발화가 사는 markdown/shell)
SCAN_EXTS = ('.md', '.sh', '.yml', '.yaml')

# dispatch 발화 검색 스코프 (★ 파일 목록 하드코딩 금지 — 디렉터리 prefix 기반, B-8 / AC-13).
# ★ CFP-2929 사정권 확대: `plugins/codeforge-review` → `plugins` (plugin 루트 1개).
#   근거 = AC-13 은 **discovery 기반**이어야 한다 — 개별 파일·개별 plugin 열거는 born-stale 이며
#   "제2 dispatch 표면이 영구 미탐지" (본 Story 가 고치려는 결함) 를 그대로 재생산한다.
#   plugin 루트 1개만 두면 **신규 plugin·신규 파일이 자동으로 사정권 안**이라 목록 갱신 의무가 없다.
#   [verified: 본 확대 직전 실측 — `python … <dir>` 를 docs/templates/.github/archive/scripts 에 각각
#    실행 시 실행 dispatch 발화 0건(전부 prose/doc example) / `plugins` 실행 시 실 발화 2 표면
#    (codeforge-review CodexReviewAgent.md · codeforge-requirements RequirementsAnalystAgent.md)]
#   ★ `tests/` 미포함은 의도적 — 그 트리의 dispatch 리터럴은 lint 를 RED 로 만들기 위한 **음성 fixture**
#     (heredoc 안 픽스처) 라 사정권에 넣으면 상시-RED. AC-13 차집합 test 는 이 캐리어를 명시 제외한다.
DEFAULT_SCAN_DIRS = (
    'plugins',
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


def _is_comment_line(raw):
    """주석 줄 판정 (정규화 대입 수집에서 배제 — AC-4 anti-substring).

    ★ base 의 `_is_doc_example_line` 과 목적이 다르다: 저쪽은 "dispatch **실행** 라인인가"
    (주석 write-mode 예외를 **포함**시키는 판정) 이고, 이쪽은 "이 줄이 런타임에 실제로 대입을
    수행하는가" 다. 주석 안 `# OUT="$(cygpath -m "$OUT")"` 는 문면상 정규화처럼 보이지만 실행되지
    않으므로 (a) 를 충족시켜선 안 된다.
    """
    return raw.lstrip().startswith('#')


def _normalized_identifiers(text):
    """`cygpath` 정규화 산출이 도달하는 식별자 집합 + 정규화 대입 presence 반환.

    반환 = (identifiers:set, has_normalization:bool)

    구성 = ① 직접 대입 `X=$(cygpath …)` 의 `X` ② 순수 복사 대입 `Y="$X"` 의 폐포(fixpoint).
    ②가 필요한 이유 = P-0 실형태가 `_n="$(cygpath …)"` → 검사 → `OUT_JSON="$_n"` 의 **2-hop** 이라
    직접 대입 대상만 보면 `-o "$OUT_JSON"` 이 born-red 가 된다 (B-10).

    주석 줄은 양쪽 수집에서 배제 (`_is_comment_line`) — 문면만 갖춘 hollow 통과 차단.
    폐포 루프는 단조 증가 + 후보 유한 → 종료 보장 (무한 루프 불가).
    """
    live = '\n'.join('' if _is_comment_line(raw) else raw for raw in text.splitlines())
    direct = {m.group(1) for m in CYGPATH_ASSIGN.finditer(live)}
    has_normalization = bool(direct)
    copies = [(m.group(1), m.group(2)) for m in COPY_ASSIGN.finditer(live)]
    ids = set(direct)
    changed = True
    while changed:                     # 복사 대입 폐포 (단조 증가 → 유한 종료)
        changed = False
        for dst, src in copies:
            if src in ids and dst not in ids:
                ids.add(dst)
                changed = True
    return ids, has_normalization


def scan_output_path_dialect(paths):
    """E6 4번째 축: `-o` 출력 경로가 방언 정규화를 거친 식별자인가 (CFP-2929 §3.8 B-10).

    판정 granularity = **(a) 파일 단위 presence ⊗ (b) dispatch 발화 라인 단위 식별자 대조**:
      (a) `-o <arg>` 를 동반한 dispatch 실행 발화를 보유한 파일은 주석 아닌 줄에
          `<IDENT>=$(cygpath …)` 정규화 대입을 보유해야 한다.
      (b) `-o "$VAR"` 형 argv 의 `VAR` 는 `_normalized_identifiers` 집합에 속해야 한다.
          `-o <리터럴>` 형은 (b) 정의역 밖 → (a) 만 적용.
      `-o` 를 아예 갖지 않는 dispatch 발화 = 본 축 vacuous (출력 경로 argv 부재).

    ★ **위치 비의존** (B-10): 정규화가 preflight 함수 내부(P-0)로 이동했으므로 "dispatch 라인 직전
    별도 줄" 로 정의하면 born-red 다. 판정 대상 = 변수 흐름이지 줄 위치가 아니다.

    ★★ **정직 상한 (over-claim 금지 — ADR-119)**: 셸 정적 리터럴 대조이지 데이터 흐름 분석이 아니다.
    **별칭·간접 재대입 우회는 잡지 못한다** — `eval` / `declare -n` nameref / `${!ref}` 간접 확장 /
    배열·`$@` 경유 / 함수·서브셸 경계 전파 / 외부 파일 source / **정규화 이후의 재대입**(줄 순서
    미검사). 본 축 GREEN = "런타임에 정규화된다"의 보증이 아니라 **presence 신호**다 (warning tier).
    런타임 진실의 결박 = §8.1 Windows 3-arm oracle (execution-backed).

    base 5-part(timeout 축) / 축 2(redirect) / 축 3(encoding) 과 disjoint additive — base 무변경
    (composition). 파일 walk = base._iter_files 재사용 (4축 동일 파일 집합 보장). 위반 ≥1 → 1, 없으면 0.
    """
    violations = []
    for f in base._iter_files(paths, SCAN_EXTS):
        try:
            with open(f, 'r', encoding='utf-8') as fh:
                text = fh.read()
        except (OSError, UnicodeDecodeError):
            continue
        ids = None
        has_norm = False
        for i, raw in enumerate(text.splitlines(), start=1):
            if base.detect_dispatch_utterance(raw, DISPATCH_PATTERNS) is None:
                continue
            if _is_doc_example_line(raw):
                continue
            out_args = DASH_O_ARG.findall(raw)
            if not out_args:
                continue          # 출력 경로 argv 부재 = 본 축 vacuous
            if ids is None:       # 파일당 1회 수집 (dispatch 보유 파일에서만 — 불필요 비용 회피)
                ids, has_norm = _normalized_identifiers(text)
            if not has_norm:
                violations.append(
                    f'{f}:{i}: codex exec dispatch 표면에 출력 경로 방언 정규화 대입 부재 '
                    f'(`<IDENT>=$(cygpath …)` 형 · 주석 줄 제외) — Windows Git Bash 에서 POSIX 형 '
                    f'`-o /c/…` 는 `C:\\c\\…` 로 조용히 오해석된다 (exit 0 + 산출물 부재). '
                    f'presence 신호일 뿐 런타임 보증 아님 (E6 / CFP-2929 §3.8 B-10)')
                continue
            for arg in out_args:
                mv = VAR_ARG.match(arg)
                if mv is None:
                    continue      # 리터럴 경로 argv = (b) 정의역 밖 ((a) 는 위에서 충족 확인)
                var = mv.group(1)
                if var not in ids:
                    violations.append(
                        f'{f}:{i}: `-o "${var}"` 의 식별자가 정규화 대입 대상이 아님 '
                        f'(정규화 도달 식별자: {", ".join(sorted(ids)) or "없음"}) — '
                        f'정규화 산출을 `-o` 로 넘기지 않으면 정규화가 무의미하다. '
                        f'별칭·간접 재대입은 본 축이 잡지 못함 (정직 상한, E6 / CFP-2929 §3.8 B-10)')
    if violations:
        print('[codex-companion-timeout-presence] FAIL (E6 — 출력 경로 방언 정규화 부재/불일치):\n'
              + '\n'.join('  ' + v for v in violations))
        return 1
    return 0


def list_dispatch_surfaces(paths):
    """dispatch 실행 발화를 1건 이상 보유한 파일 목록 (정렬·repo-relative·`/` 구분자).

    AC-13 차집합 test 의 **discovery side** 기계 인터페이스 — 검출기를 bash 로 재구현(=drift 표면)
    하지 않게 하기 위한 read-only introspection. 스캔·판정·exit semantics 무변경.
    """
    found = set()
    for f in base._iter_files(paths, SCAN_EXTS):
        try:
            with open(f, 'r', encoding='utf-8') as fh:
                text = fh.read()
        except (OSError, UnicodeDecodeError):
            continue
        for raw in text.splitlines():
            if base.detect_dispatch_utterance(raw, DISPATCH_PATTERNS) is None:
                continue
            if _is_doc_example_line(raw):
                continue
            try:
                rel = os.path.relpath(f)
            except ValueError:
                # Windows 교차 드라이브 (예: repo=C: · 인자=D:\tmp) 는 relpath 불가 → 절대경로 유지.
                rel = f
            found.add(rel.replace(os.sep, '/'))
            break
    return sorted(found)


def run_scan(paths):
    # timeout 축 (base 5-part 소유: 가드 presence / hollow-gate I-3 / consumer no-op)
    #   ∪ AC-4 redirect 축 ∪ AC-7 encoding env 축 ∪ E6 output-path dialect 축 — 4축 **무조건 순차 실행**
    #   (short-circuit 없음: 동시 위반 시 네 라벨 진단이 모두 stdout 에 잔존해야 함,
    #   ADR-081 §결정 D16 8항 / CFP-2884 §8.2B B-3 / CFP-2929 §3.8 B-10).
    timeout_rc = base.check_liveness_presence(
        paths, DISPATCH_PATTERNS, SCAN_EXTS, HOME_MARKER, ADAPTER_NAME,
        KIND_LABELS, _is_doc_example_line, DIAG_MESSAGES, MESSAGES)
    redirect_rc = scan_stdin_redirect(paths)
    encoding_rc = scan_encoding_env_presence(paths)
    dialect_rc = scan_output_path_dialect(paths)
    return max(timeout_rc, redirect_rc, encoding_rc, dialect_rc)


# ── self-test (D3 inline fixture, CI step 호출) ────────────────────────────────
# 4축 라벨 진단 리터럴 (동시위반 fixture B-3 가 stdout 실재를 축별로 assert — CFP-2884 §8.2B B-3).
_AXIS_LABELS = {
    'timeout': '[codex-companion-timeout-presence] FAIL — wall-clock 가드 누락',
    'redirect': '[codex-companion-timeout-presence] FAIL (AC-4 — stdin `- <` redirect 부재)',
    'encoding': '[codex-companion-timeout-presence] FAIL (AC-7 — UTF-8 인코딩 env export 부재)',
    'dialect': '[codex-companion-timeout-presence] FAIL (E6 — 출력 경로 방언 정규화 부재/불일치)',
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
    """AC-7 encoding env 축 + AC-4 redirect 축 + E6 dialect 축 + timeout 축의 **scan 계층**
    discriminating self-test.

    text-only `check_lines` 로는 축 2·3·4 (파일 walk 기반) 을 행사할 수 없어 tempfile fixture 를 쓴다
    (실 `run_scan` 합성 경로를 그대로 통과 — max() 합성·순차 실행 무-short-circuit 도 함께 검증).
    반환 = (failed 리스트, 총 case 수).
    """
    guarded = ('timeout --kill-after=30 300 codex exec '
               '-s read-only --output-schema s.json -o "$OUT_JSON" - < p.md\n')
    env_block = ('export LC_ALL=C.UTF-8   # 별도 줄 export (inline env-prefix 는 first-token 판정 파괴)\n'
                 'export PYTHONUTF8=1\n')
    # 정규화 대입 — P-0 실형태 동형 (직접 대입 `_n` → **1-hop 복사** → argv 변수 `OUT_JSON`).
    norm_block = ('_n="$(cygpath -m "$OUT_JSON" 2>/dev/null)"\n'
                  'OUT_JSON="$_n"\n')
    norm_direct = 'OUT_JSON="$(cygpath -m "$OUT_JSON" 2>/dev/null)"\n'   # hop 없는 직접 대입 형
    norm_commented = ('# _n="$(cygpath -m "$OUT_JSON" 2>/dev/null)"\n'   # 실행되지 않는 문면 (D4)
                      '# OUT_JSON="$_n"\n')
    # (name, text, expect_rc, must_contain 축 set, must_not_contain 축 set)
    cases = [
        ('E1 GREEN: env export 2종 별도 줄 + 가드 + redirect + 정규화(1-hop) (4축 전부 충족)',
         env_block + norm_block + guarded, 0, set(), {'timeout', 'redirect', 'encoding', 'dialect'}),
        ('E2 RED: encoding env 부재 (AC-7 단독 발화 — 타 3축은 침묵해야 함)',
         norm_block + guarded, 1, {'encoding'}, {'timeout', 'redirect', 'dialect'}),
        ('E3 GREEN: dispatch 발화 0건 파일 → 축 2·3·4 vacuous (env·정규화 부재라도 false-RED 금지)',
         '이 파일에는 실행 dispatch 발화가 없다 — prose 서술만 존재.\n',
         0, set(), {'timeout', 'redirect', 'encoding', 'dialect'}),
        ('E4 RED: inline env-prefix 는 별도 줄 export 아님 (substring 검사 hollow 구현 검출)',
         '# 아래 첫 발화는 인라인 env-prefix 형태 (금지) — 별도 줄 export 부재\n'
         + norm_block + 'LC_ALL=C.UTF-8 PYTHONUTF8=1 ' + guarded + guarded,
         1, {'encoding'}, {'timeout', 'redirect', 'dialect'}),
        # ── E6 dialect 축 (CFP-2929 §3.8 B-10) ──
        ('D1 GREEN: 정규화 직접 대입(hop 0) + `-o "$OUT_JSON"` 동일 식별자 → dialect 축 충족',
         env_block + norm_direct + guarded, 0, set(),
         {'timeout', 'redirect', 'encoding', 'dialect'}),
        ('D2 RED: 정규화 대입 전무 (mutant i — `cygpath` 0) → dialect 단독 발화',
         env_block + guarded, 1, {'dialect'}, {'timeout', 'redirect', 'encoding'}),
        ('D3 RED: `-o "$OTHER_VAR"` 식별자 불일치 (mutant ii — 정규화는 있으나 argv 가 그 산출이 아님)',
         env_block + norm_block
         + 'timeout --kill-after=30 300 codex exec -s read-only -o "$OTHER_VAR" - < p.md\n',
         1, {'dialect'}, {'timeout', 'redirect', 'encoding'}),
        ('D4 RED anti-substring: 정규화 대입이 **주석 안에만** 존재 (문면 hollow 통과 차단)',
         env_block + norm_commented + guarded,
         1, {'dialect'}, {'timeout', 'redirect', 'encoding'}),
        ('D5 GREEN: `-o` 없는 dispatch 발화 → dialect 축 vacuous (출력 경로 argv 부재)',
         env_block + 'timeout --kill-after=30 300 codex exec -s read-only - < p.md\n',
         0, set(), {'timeout', 'redirect', 'encoding', 'dialect'}),
        ('D6 RED: 리터럴 `-o out.json` 이어도 정규화 대입 부재면 (a) 위반 (리터럴 우회 차단)',
         env_block + 'timeout --kill-after=30 300 codex exec -s read-only -o out.json - < p.md\n',
         1, {'dialect'}, {'timeout', 'redirect', 'encoding'}),
        ('B3 RED: 4축 동시위반 (timeout·redirect·env·정규화 전부 부재) → 라벨 4종 전부 stdout 실재',
         'codex exec -s read-only --output-schema s.json -o "$OUT_JSON"\n',
         1, {'timeout', 'redirect', 'encoding', 'dialect'}, set()),
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
    # ── scan 계층 축 (AC-4 redirect / AC-7 encoding env / E6 output-path dialect / 4축 동시위반)
    #    — CFP-2884 §8.2B B-3 + CFP-2929 §3.8 B-10 ──
    scan_failed, scan_total = _self_test_scan_axes()
    failed.extend((name, 'scan-axis', detail) for name, detail in scan_failed)
    total = len(cases) + scan_total
    if failed:
        print(f'[self-test] FAIL — {len(failed)} case mismatch')
        for entry in failed:
            print(f'  - {entry}')
        return 1
    print(f'[self-test] PASS — {total}/{total} case '
          f'(text 축 {len(cases)} RED→GREEN discriminating + scan 축 {scan_total} 4-axis 라벨 판별)')
    return 0


def main(argv):
    args = argv[1:]
    if '--self-test' in args:
        return self_test()
    if '--list-scope-dirs' in args:
        # AC-13 차집합 test 의 **사정권 side** (디렉터리 prefix — 파일 목록 아님, B-8).
        for d in DEFAULT_SCAN_DIRS:
            print(d)
        return 0
    if '--list-dispatch-surfaces' in args:
        # AC-13 차집합 test 의 **discovery side**. 인자 미지정 = repo root `.` 전수 discovery
        # (사정권과 **독립** 이어야 M-S 가 kill 된다 — 양변을 같은 목록에서 뽑으면 tautology).
        rest = [a for a in args if a != '--list-dispatch-surfaces']
        for a in rest:
            if not os.path.exists(a):
                print(f'[codex-companion-timeout-presence] setup error: 경로 미존재: {a}', file=sys.stderr)
                return 2
        for f in list_dispatch_surfaces(rest or ['.']):
            print(f)
        return 0
    if not args:
        # 인자 0개 = repo root 기준 default 스캔 디렉터리 (thin wrapper 가 repo root 로 cd)
        paths = [d for d in DEFAULT_SCAN_DIRS if os.path.isdir(d)]
        if not paths:
            # DEFAULT_SCAN_DIRS(=codeforge plugin 배포 표면 루트) 부재.
            # 경로 부재 fail-safe (consumer no-op degradation): repo root 전체(`.`) 로 확장하면
            # consumer 에 dispatch 발화 0건 → hollow-gate(I-3) false-RED 유발 →
            # byte-identical template↔.github mirror(ADR-005, CONSUMER_ONLY 미등록) 상속이 깨진다.
            # 따라서 `.` 로 넓히지 않고 honest no-op (exit 0) — hollow-gate 는 "codeforge-owned
            # dispatch 경로가 실존할 때만" 발동 (Story §5 판정 / ADR-081 §결정 D15).
            print('[codex-companion-timeout-presence] 스캔 대상 경로(plugins/) 부재 — '
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
