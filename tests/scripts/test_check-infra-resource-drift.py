#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
tests/scripts/test_check-infra-resource-drift.py
CFP-2700 (Epic) G2 Phase 2 (구현 lane) — Discriminating self-test (.py channel) for
  scripts/lib/check_infra_resource_drift.py (infra-resource manifest drift scan D3 + 역색인 D4).

★ .sh(ADR-151 인벤토리 enroll) 와 disjoint 보완 채널(ac-traceability Hop3 = `.py` AST 스타일). 동일
  AC set 을 subprocess 실 실행 + 소스 문자열-치환 mutation 으로 discriminating 검증 — presence-only 금지,
  실 exit code + FIXED 출력 토큰 결박 + 대표 mutation RED-flip(스캐너 소스 변형 시 test RED = 생존 0):
    AC-5  미선언 표면 검출 (secrets.<undeclared> → exit 1 + UNDECLARED) + MK undeclared_off
      · deprecated alias = allow_set 편입(참조돼도 undeclared 아님) + MK deprecated_unclassified
      · `_env:` 값 앞 pad≥5 검출(F-CR-003 회귀 봉인 — 구 {0,4} bound 는 candidate 로도 미계수인
        침묵 미탐이었음) + MK env_pad_narrow
    AC-6  orphan (선언·미참조 → warning+exit0 / --promote-orphan → exit1) + MK orphan_promote_off
    AC-7  substring 오분류 제외 (team-spec-decompose 구조판정 = env-key 0 → inert 무증가) + MK signal_always
    AC-8  역색인(D4) verdict-invariant (변조/제거해도 verdict 불변, side-output I-1) + MK revindex_noop
    AC-10 none-disguise fail (infra_resources 부재 + 사유부재 + 표면 → exit1 + NONE-DISGUISE) + MK none_off
    AC-11 none-disguise pass (resources:none + reason + 표면0 → exit0)
    AC-17 wrapper 실 secret dogfood (실 repo → exit0, candidates≥floor, inert>0,
      G6 수렴 ratchet: baseline 0 pair + grandfathered==0) + MK no_secrets(candidates 급감 = secrets load-bearing)
  + grandfather baseline hermetic(tmp corpus) + MK baseline_subtract_off
  + born-hollow guard(candidates==0 ∧ inert==0 → exit3) + argparse 오류(exit 2).

★ P1-A shell env-passthrough carve-in (§결정8(vi)) — dual pin:
  PIN-POSITIVE `VAR="${VAR}" <cmd>` → 검출 + MK passthrough_off(제거 시 미탐 RED).
  PIN-NEGATIVE 변수 '읽기' 일반형(STORY_KEY/GH_TOKEN/PAGE_TOKEN) → **미검출이 계약**
    + MK naive_shell_form(naive `${VAR}` 스캔 재도입 → FP 오검출로 RED-flip).
    ※ 이 negative 가 본 FIX 의 핵심 — 정직 천장을 **산문에서 집행 계약으로** 승격시킨다. 장래 누군가
      "shell 도 전부 스캔하자"고 넓히면 실측 정밀도 18-20% 회귀가 test RED 로 즉시 드러난다.

★ P1-B monotonic shrink + content_digest (선언 이행 — 선언만 있고 미구현이던 로직의 실배선):
  ① shrink-refuse(신규 pair 추가 시 --write-baseline exit 1 + pair 열거 + 부분 write 0) + MK growth_check_off
  ② shrink-allow(축소 방향은 재생성 성공) + escape hatch(--allow-baseline-growth --reason: 무사유 exit 2,
     사유 동반 통과 + growth_reason 각인)
  ③ digest-tamper(수기 행 추가 → exit 3) + digest 필드부재(exit 3) + MK digest_verify_off

★ baseline 판별력 분산 (F-CR-005): 본 정정 전 baseline 로직 mutant(subtract_off / gf_counter_off /
  load_baseline_empty) 3종이 **모두 test_ac17_wrapper_dogfood_scan 단 하나로만** 죽었다(실측). AC-17 의
  killer 는 실 repo debt count 에 결박된 `grandfathered≥3`(현 baseline 4 pair — 여유 1)이라, manifest
  등재로 baseline 이 shrink 하면 정상 코드가 false-RED 로 깨진다. → tmp corpus hermetic 케이스를 신설해
  baseline subtract 를 실 debt count 와 무관하게 결박(위 3 mutant 전건 hermetic kill 확보, 실측).
  AC-17 의 `grandfathered≥3` 은 non-vacuity floor 로 존치하되 **유일 killer 가 아니게** 됐다 —
  baseline shrink 시 조정 대상은 AC-17 뿐이며 hermetic 케이스는 무영향(의도된 결합 분리).
  ▸ G6 (AC-22 수렴): 5 pair 전건 manifest 등재로 baseline 5→0 shrink 완료 — AC-17 결박은 예고대로
    `grandfathered==0 ∧ baseline 0 pair`(수렴 유지 ratchet)로 갱신, hermetic 케이스 무변경.

★ AC-22 DEC-3 라이브 2계열 canonical 수렴 (G6 — ADR-157 §결정5):
  · fixture discriminating pair: 동일 소비면(선언면 `_env:` ATLASSIAN_USER_EMAIL + 소비면 workflow
    `secrets.CONFLUENCE_USER_EMAIL`)에 대해 manifest 가 canonical 1 + accepted alias 로 양키를 선언하면
    exit 0(수렴) / alias 누락 manifest 면 exit 1 + UNDECLARED(미수렴) — alias 선언이 load-bearing.
  · wrapper-live: 실 repo 를 **baseline 제거 상태**로 스캔해도 exit 0 + undeclared=0 + grandfathered=0
    (non-zero→zero 확증의 "zero" 면) + 2계열/alias-gap/audit-pii-key 의 역색인 매핑 결박.

standalone: `python3 tests/scripts/test_check-infra-resource-drift.py` → 전 test_* 실행, exit 0=PASS / 1=FAIL.
  pytest 하위호환(함수명 test_*) — CI 워크플로는 python3 직접 실행(byte-identical template step).
"""

import os
import re
import subprocess
import sys
import tempfile

# Windows cp949 회피: stdout/stderr UTF-8 강제 (scanner SSOT 동형 — 출력 em-dash/한글 안전).
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SSOT_PY = os.path.join(REPO_ROOT, "scripts", "lib", "check_infra_resource_drift.py")
REAL_BASELINE = os.path.join(REPO_ROOT, "docs", "infra-resource-baseline.yaml")
# 실 wrapper census 안정 하한(non-vacuity floor). 실측 candidates 는 스캔 범위 확장 시 변동하므로 **정확한
#   현재치를 여기 박지 않는다** (F-CR-007 수치 3-site drift 근절 — 수치 SSOT = 스캐너 실행 출력).
FLOOR = 50

# ─────────────────────── fixtures ───────────────────────────────────────────────
MANIFEST = """infra_resources:
  resources:
    - id: raw-nas
      canonical_env: RAW_NAS_URL
      aliases:
        accepted: [MINIO_URL]
    - id: api-cred
      canonical_env: SERVICE_API_TOKEN
  execution_units:
    collector:
      required: [raw-nas]
"""

COMPOSE = """services:
  db:
    image: postgres:16-alpine
    environment:
      DATABASE_URL: postgres://app@db/app
      REDIS_URL: redis://redis:6379
"""

DECOMPOSE = """team_spec_decompose:
  mode: full
  STEP_NAME: parse
"""

WF_UNDECLARED = """name: wf
on: {push: {}}
jobs:
  j:
    steps:
      - run: echo ${{ secrets.ROGUE_TOKEN }}
"""

WF_DECLARED = """name: wf
on: {push: {}}
jobs:
  j:
    steps:
      - run: echo ${{ secrets.RAW_NAS_URL }}
"""

NOINFRA_YAML = """project: demo
atlassian:
  confluence:
    api_token_env: "ROGUE_TOKEN"
"""

NONEOK_YAML = """infra_resources:
  resources: none
  reason: this project has no infra resource dependencies
"""

# ── deprecated alias 계열 (F-CR-004: `m.classified.add(d)` mutant 가 17/17 전건 생존 = kill 0 이었음).
#    deprecated = "선언된 자원의 sunset 별칭" → 참조돼도 undeclared 아님(allow_set 편입)이 계약.
MANIFEST_DEPRECATED = """infra_resources:
  resources:
    - id: raw-nas
      canonical_env: RAW_NAS_URL
      aliases:
        accepted: [MINIO_URL]
        deprecated:
          - name: LEGACY_NAS_URL
"""

WF_DEPRECATED = """name: wf
on: {push: {}}
jobs:
  j:
    steps:
      - run: echo ${{ secrets.LEGACY_NAS_URL }}
"""

# ── `_env:` 값 앞 공백 pad≥5 (F-CR-003: 구 `\\s{0,4}` bound 는 candidate 로도 미계수 = 침묵 미탐).
#    PAD1(정렬 없음) = 회귀 대조군, PAD5(yaml 정렬 padding) = 본 subject. 둘 다 infra_resources block
#    밖에 둬야 SELF_EXCLUDE 를 타지 않는다(block = 선언면, 소비면 아님).
PROJ_PAD5 = """infra_resources:
  resources:
    - id: raw-nas
      canonical_env: RAW_NAS_URL
atlassian:
  confluence:
    api_token_env:     "PAD5_TOKEN"
    other_token_env: "PAD1_TOKEN"
"""

# ── hermetic grandfather baseline (F-CR-005: baseline 로직 killer 가 실 repo AC-17 단 하나 —
#    `grandfathered>=3` 이 실 debt count 에 결박돼 baseline shrink 시 false-RED. tmp corpus 로 분리).
#    content_digest = compute_content_digest({(".github/workflows/wf.yml","ROGUE_TOKEN")}) 실측 각인.
#    하드코딩 근거: 이 hex 는 canonical form **pin** 이다 — canonicalization 이 바뀌면 본 fixture 가 RED 로
#    떠서 generate/verify byte-stability(선례 ID-1 동형) 파손을 즉시 알린다(의도된 결박, 갱신은 수동 의식).
BASELINE_FIXTURE = """content_digest: 1a5fe7d1f00d8516308cc89cd123623e7e709e1b7aa728c7e812aac89d9053ac
grandfathered_undeclared_surfaces:
- file: .github/workflows/wf.yml
  env_key: ROGUE_TOKEN
  reason: hermetic fixture — 승격 시점 pre-existing 로 가정
"""

# ── P1-A carve-in (§결정8(vi)): shell env-passthrough 자기참조형 = 키 리터럴 position 등가 → 검출 대상.
SH_PASSTHROUGH = """#!/usr/bin/env bash
set -euo pipefail
AUDIT_PII_KEY="${AUDIT_PII_KEY}" python3 "$SCRIPT_DIR/lib/redact.py"
"""

# ── PIN-NEGATIVE fixture (정직 천장 (vi) 의 **실행화**): shell 변수 '읽기' 일반형 = 미검출이 계약.
#    전건이 실측 FP 계열 재현 — STORY_KEY(`_KEY` suffix 라 infra-signal 매치하나 실제론 parse-token,
#    실측 11 hit 중 6건) / GH_TOKEN 존재검사 / PAGE_TOKEN 자기대입(뒤 명령 없음 = passthrough 아님).
#    이 3형태가 검출되면 = naive form 스캔이 재도입된 것 = 실측 정밀도 18-20% 로의 회귀 → 본 test RED.
SH_READ_ONLY = """#!/usr/bin/env bash
STORY_KEY="${STORY_KEY:-}"
if [ -z "${GH_TOKEN:-}" ]; then
  echo "no token" >&2
fi
PAGE_TOKEN="${PAGE_TOKEN}"
echo "${STORY_KEY}"
"""

# ── AC-22 2계열 canonical 수렴 discriminating pair (G6 — DEC-3 / ADR-157 §결정5).
#    동일 소비면 2곳: 선언면 project.yaml `user_email_env:`(ATLASSIAN_USER_EMAIL, block 밖 = SELF_EXCLUDE
#    비대상) + 소비면 workflow `secrets.CONFLUENCE_USER_EMAIL`. manifest 만 다르다 — canonical 1 +
#    accepted alias 로 양키 선언(수렴) vs alias 누락(미수렴). rename 0 이 계약(라이브 secret 무중단).
PROJ_TWO_SERIES_CONVERGED = """infra_resources:
  resources:
    - id: confluence-user-email
      canonical_env: ATLASSIAN_USER_EMAIL
      aliases:
        accepted: [CONFLUENCE_USER_EMAIL]
atlassian:
  confluence:
    user_email_env: "ATLASSIAN_USER_EMAIL"
"""

PROJ_TWO_SERIES_UNCONVERGED = """infra_resources:
  resources:
    - id: confluence-user-email
      canonical_env: ATLASSIAN_USER_EMAIL
      aliases:
        accepted: []
atlassian:
  confluence:
    user_email_env: "ATLASSIAN_USER_EMAIL"
"""

WF_ALIAS_CONSUME = """name: wf
on: {push: {}}
jobs:
  j:
    steps:
      - run: echo ${{ secrets.CONFLUENCE_USER_EMAIL }}
"""

# 소스 문자열-치환 mutation (anchor → replacement). 미적용 시 AssertionError(anchor drift 검출).
MUTATIONS = {
    "undeclared_off": (
        "undeclared_all = [s for s in live_surfaces if s.key not in manifest.classified]",
        "undeclared_all = []",
    ),
    "orphan_promote_off": (
        "if orphans and args.promote_orphan:",
        "if orphans and False:",
    ),
    "signal_always": (
        "def _is_infra_signal(token):",
        "def _is_infra_signal(token):\n    return True  # MUTANT-signal-always",
    ),
    "revindex_noop": (
        "def _emit_reverse_index(live_surfaces, manifest):",
        "def _emit_reverse_index(live_surfaces, manifest):\n    return  # MUTANT-revindex-noop",
    ),
    "none_off": (
        "if hollow_none and candidates >= 1:",
        "if False and candidates >= 1:",
    ),
    "no_secrets": (
        "def _scan_workflow(physical, rel):",
        "def _scan_workflow(physical, rel):\n    return []  # MUTANT-no-secrets",
    ),
    # F-CR-004: deprecated alias 를 allow_set 에 미편입 → 참조 시 undeclared 오검출.
    "deprecated_unclassified": (
        "            m.classified.add(d)",
        "            pass  # MUTANT-deprecated-unclassified",
    ),
    # F-CR-003: `_env:` pad bound 를 구 {0,4} 로 되돌림 → pad≥5 침묵 미탐 재현.
    "env_pad_narrow": (
        r"_env:\s{0,40}",
        r"_env:\s{0,4}",
    ),
    # F-CR-005: baseline subtract 무력화 → grandfather 억제 소멸.
    "baseline_subtract_off": (
        "        if (s.rel, s.key) in baseline_keys:",
        "        if False:  # MUTANT-baseline-subtract-off",
    ),
    # P1-A: passthrough 검출 제거 → PIN-POSITIVE 미탐.
    "passthrough_off": (
        "            mm = _RE_SHELL_ENV_PASSTHROUGH.match(code)",
        "            mm = None  # MUTANT-passthrough-off",
    ),
    # P1-A PIN-NEGATIVE killer: `.sh` 를 **naive `${VAR}` 읽기 일반형**으로 스캔하도록 되돌린다 =
    #   §결정7(b) FM1 봉인 위반(실측 정밀도 18-20%)의 재도입 시뮬레이션. PIN-NEGATIVE 가 RED 로 트립해야
    #   천장이 산문 아닌 **집행 계약**임이 증명된다.
    "naive_shell_form": (
        "            mm = _RE_SHELL_ENV_PASSTHROUGH.match(code)",
        "            mm = re.search(r'\\$\\{([A-Z][A-Z0-9_]{2,64})', code)  # MUTANT-naive-shell-form",
    ),
    # P1-B: monotonic shrink 의 growth 거부 제거 → baseline 무단 확장 통과.
    "growth_check_off": (
        "        if added:",
        "        if False:  # MUTANT-growth-check-off",
    ),
    # P1-B: baseline digest 검증 생략 → 손상 baseline 이 verdict 를 내버림(vacuous).
    "digest_verify_off": (
        "    if digest_reasons:",
        "    if False:  # MUTANT-digest-verify-off",
    ),
}


# ─────────────────────── helpers ────────────────────────────────────────────────

def _write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)


def make_corpus(tmp, project_yaml, wf=None, compose=None, decompose=None, baseline=None, scripts=None):
    _write(os.path.join(tmp, ".claude", "_overlay", "project.yaml"), project_yaml)
    if wf is not None:
        _write(os.path.join(tmp, ".github", "workflows", "wf.yml"), wf)
    if compose is not None:
        _write(os.path.join(tmp, "examples", "svc", "compose.yml"), compose)
    if decompose is not None:
        _write(os.path.join(tmp, "examples", "svc", "team-spec-decompose.yaml"), decompose)
    if baseline is not None:
        # scanner DEFAULT_BASELINE_REL 과 동일 경로 — CLI override 없이 기본 탐색 경로를 실제로 태운다.
        _write(os.path.join(tmp, "docs", "infra-resource-baseline.yaml"), baseline)
    if scripts:
        # {relpath-under-scripts/: content} — LIVE_SCRIPT_GLOBS(`scripts/**`) 재귀 corpus 를 실제로 태운다.
        for name, content in scripts.items():
            _write(os.path.join(tmp, "scripts", *name.split("/")), content)


def read_baseline_pairs(path):
    """baseline 파일 → [(file, env_key)] (수치 하드코딩 0 — F-CR-007 runtime 도출)."""
    pairs = []
    cur = None
    with open(path, encoding="utf-8") as f:
        for line in f:
            mm = re.match(r"^-\s+file:\s*(\S+)\s*$", line)
            if mm:
                cur = mm.group(1)
                continue
            mm = re.match(r"^\s+env_key:\s*(\S+)\s*$", line)
            if mm and cur is not None:
                pairs.append((cur, mm.group(1)))
    return pairs


def run_scanner(scanner_py, repo_root, *args):
    """scanner subprocess 실행 → (exit_code, combined_output)."""
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    proc = subprocess.run(
        [sys.executable, scanner_py, "--repo-root", repo_root, *args],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env, timeout=60,
    )
    return proc.returncode, proc.stdout.decode("utf-8", "replace")


def make_mutant(tmp, kind):
    """SSOT 를 kind mutation 적용해 tmp/mutant.py 로 write → 경로 반환."""
    old, new = MUTATIONS[kind]
    src = open(SSOT_PY, encoding="utf-8").read()
    mutated = src.replace(old, new, 1)
    assert mutated != src, "mutation did not apply — anchor drift (kind=%s)" % kind
    path = os.path.join(tmp, "mutant.py")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(mutated)
    return path


def census(out, field):
    m = re.search(field + r"=(\d+)", out)
    return int(m.group(1)) if m else -1


# ─────────────────────── AC-5 미선언 표면 검출 ───────────────────────────────────

def test_ac5_undeclared_detect():
    with tempfile.TemporaryDirectory() as tmp:
        make_corpus(tmp, MANIFEST, wf=WF_UNDECLARED, compose=COMPOSE)
        rc, out = run_scanner(SSOT_PY, tmp)
        assert rc == 1, "AC-5: undeclared secret → exit 1, got %d\n%s" % (rc, out)
        assert "::warning::check-infra-resource-drift: UNDECLARED" in out
        assert "env-key=ROGUE_TOKEN" in out


def test_ac5_mutation_undeclared_off():
    with tempfile.TemporaryDirectory() as tmp:
        make_corpus(tmp, MANIFEST, wf=WF_UNDECLARED, compose=COMPOSE)
        mut = make_mutant(tmp, "undeclared_off")
        rc, out = run_scanner(mut, tmp)
        # RED-flip: undeclared 계산 무력화 → 미검출(PASS exit 0), UNDECLARED 토큰 소멸.
        assert rc == 0, "AC-5 MK: mutant → exit 0 (미검출), got %d\n%s" % (rc, out)
        assert "UNDECLARED" not in out


# ── AC-5 deprecated alias = allow_set 편입 (F-CR-004 mutant kill 확보) ──

def test_ac5_deprecated_alias_classified():
    with tempfile.TemporaryDirectory() as tmp:
        make_corpus(tmp, MANIFEST_DEPRECATED, wf=WF_DEPRECATED, compose=COMPOSE)
        rc, out = run_scanner(SSOT_PY, tmp)
        assert rc == 0, "AC-5: deprecated alias 참조 → undeclared 아님(exit 0), got %d\n%s" % (rc, out)
        assert "LEGACY_NAS_URL" not in out, "AC-5: deprecated alias 를 UNDECLARED 로 오검출\n%s" % out


def test_ac5_mutation_deprecated_unclassified():
    with tempfile.TemporaryDirectory() as tmp:
        make_corpus(tmp, MANIFEST_DEPRECATED, wf=WF_DEPRECATED, compose=COMPOSE)
        mut = make_mutant(tmp, "deprecated_unclassified")
        rc, out = run_scanner(mut, tmp)
        # RED-flip: deprecated 를 allow_set 미편입 → 정당 sunset 별칭이 undeclared 오검출(exit 1).
        assert rc == 1, "AC-5 MK: deprecated_unclassified → exit 1(오검출), got %d\n%s" % (rc, out)
        assert "env-key=LEGACY_NAS_URL" in out, \
            "AC-5 MK: deprecated alias 가 UNDECLARED 로 표면화돼야 kill 성립\n%s" % out


# ── AC-5 `_env:` pad≥5 검출 (F-CR-003 회귀 봉인) ──

def test_ac5_env_padding_ge5_detected():
    with tempfile.TemporaryDirectory() as tmp:
        make_corpus(tmp, PROJ_PAD5, compose=COMPOSE)
        rc, out = run_scanner(SSOT_PY, tmp)
        assert rc == 1, "F-CR-003: pad≥5 `_env:` → undeclared FLAG(exit 1), got %d\n%s" % (rc, out)
        assert "env-key=PAD5_TOKEN" in out, "F-CR-003: pad≥5 검출 누락(침묵 미탐 회귀)\n%s" % out
        assert "env-key=PAD1_TOKEN" in out, "F-CR-003: pad=1 대조군도 검출돼야 함\n%s" % out
        # candidate 로도 계수돼야 함 — 구 bound 는 census 에서조차 누락(silent drop)이었다.
        assert census(out, "candidates_scanned") == 2, \
            "F-CR-003: pad1+pad5 = candidates 2, got %d" % census(out, "candidates_scanned")


def test_ac5_mutation_env_pad_narrow():
    with tempfile.TemporaryDirectory() as tmp:
        make_corpus(tmp, PROJ_PAD5, compose=COMPOSE)
        mut = make_mutant(tmp, "env_pad_narrow")
        rc, out = run_scanner(mut, tmp)
        # RED-flip: bound 를 구 {0,4} 로 되돌리면 PAD5 는 candidate 로도 안 잡힘 = 침묵 미탐 재현.
        assert "PAD5_TOKEN" not in out, "F-CR-003 MK: env_pad_narrow → PAD5 미탐(RED)\n%s" % out
        assert census(out, "candidates_scanned") == 1, \
            "F-CR-003 MK: 구 bound → candidates 1(PAD5 silent drop), got %d" % census(out, "candidates_scanned")


# ── grandfather baseline hermetic (F-CR-005 판별력 분산 — 실 repo debt count 비결박) ──

def test_baseline_grandfather_hermetic():
    with tempfile.TemporaryDirectory() as tmp:
        # ROGUE_TOKEN = 미선언이나 baseline 이 동결 → new-only subtract 로 억제(exit 0).
        make_corpus(tmp, MANIFEST, wf=WF_UNDECLARED, compose=COMPOSE, baseline=BASELINE_FIXTURE)
        rc, out = run_scanner(SSOT_PY, tmp)
        assert rc == 0, "F-CR-005: baseline 동결 표면 → 억제(exit 0), got %d\n%s" % (rc, out)
        assert census(out, "undeclared") == 0, "F-CR-005: new undeclared 0(baseline subtract)"
        assert census(out, "grandfathered") == 1, \
            "F-CR-005: grandfathered=1, got %d" % census(out, "grandfathered")
        # anti-hollow: baseline 은 candidate census 를 깎지 않는다(억제는 verdict 면 한정).
        assert census(out, "candidates_scanned") == 1, \
            "F-CR-005: baseline 이 candidate census 를 감소시키면 anti-hollow 위반, got %d" \
            % census(out, "candidates_scanned")


def test_baseline_mutation_subtract_off():
    with tempfile.TemporaryDirectory() as tmp:
        make_corpus(tmp, MANIFEST, wf=WF_UNDECLARED, compose=COMPOSE, baseline=BASELINE_FIXTURE)
        mut = make_mutant(tmp, "baseline_subtract_off")
        rc, out = run_scanner(mut, tmp)
        # RED-flip: subtract 무력화 → baseline 이 있어도 flag(exit 1) + grandfathered 0.
        assert rc == 1, "F-CR-005 MK: subtract_off → exit 1, got %d\n%s" % (rc, out)
        assert census(out, "grandfathered") == 0, "F-CR-005 MK: grandfathered 0(억제 소멸)"


# ─────────────────────── P1-A shell env-passthrough carve-in (§결정8(vi)) ────────

def test_p1a_pin_positive_passthrough_detected():
    """PIN-POSITIVE: `VAR="${VAR}" <cmd>` = 키 리터럴 position 등가 → 검출."""
    with tempfile.TemporaryDirectory() as tmp:
        make_corpus(tmp, MANIFEST, compose=COMPOSE, scripts={"pt.sh": SH_PASSTHROUGH})
        rc, out = run_scanner(SSOT_PY, tmp)
        assert rc == 1, "P1-A: passthrough 미선언 → exit 1, got %d\n%s" % (rc, out)
        assert "env-key=AUDIT_PII_KEY" in out, "P1-A: passthrough 키 검출 누락\n%s" % out
        assert "form=passthrough" in out, "P1-A: form=passthrough 표기\n%s" % out
        assert census(out, "candidates_scanned") == 1, \
            "P1-A: passthrough 1건만 candidate, got %d" % census(out, "candidates_scanned")


def test_p1a_mutation_passthrough_off():
    with tempfile.TemporaryDirectory() as tmp:
        make_corpus(tmp, MANIFEST, compose=COMPOSE, scripts={"pt.sh": SH_PASSTHROUGH})
        mut = make_mutant(tmp, "passthrough_off")
        rc, out = run_scanner(mut, tmp)
        # RED-flip: passthrough 검출 제거 → 미탐(candidates 0, PASS).
        assert "AUDIT_PII_KEY" not in out, "P1-A MK: passthrough_off → 미탐(RED)\n%s" % out
        assert census(out, "candidates_scanned") == 0, \
            "P1-A MK: candidates 0(미탐), got %d" % census(out, "candidates_scanned")


def test_p1a_pin_negative_ceiling_enforced():
    """PIN-NEGATIVE: shell 변수 '읽기' 일반형 = **미검출이 계약**(정직 천장 (vi) 의 집행).

    naive form/bare 스캔이 재도입되면 이 단정이 깨져 RED → 천장이 산문 아닌 집행 계약이 된다.
    """
    with tempfile.TemporaryDirectory() as tmp:
        make_corpus(tmp, MANIFEST, compose=COMPOSE, scripts={"ro.sh": SH_READ_ONLY})
        rc, out = run_scanner(SSOT_PY, tmp)
        assert rc == 0, "PIN-NEG: 변수읽기 일반형 → 미검출 PASS(exit 0), got %d\n%s" % (rc, out)
        assert census(out, "candidates_scanned") == 0, \
            "PIN-NEG: 변수읽기는 candidate 로도 계수 안 됨(천장 (vi)), got %d\n%s" \
            % (census(out, "candidates_scanned"), out)
        for tok in ("STORY_KEY", "GH_TOKEN", "PAGE_TOKEN"):
            assert tok not in out, \
                "PIN-NEG: %s 검출 = naive form 스캔 재도입(실측 정밀도 18-20% 회귀)\n%s" % (tok, out)


def test_p1a_mutation_naive_shell_form():
    with tempfile.TemporaryDirectory() as tmp:
        make_corpus(tmp, MANIFEST, compose=COMPOSE, scripts={"ro.sh": SH_READ_ONLY})
        mut = make_mutant(tmp, "naive_shell_form")
        rc, out = run_scanner(mut, tmp)
        # RED-flip: naive `${VAR}` 읽기 스캔 재도입 → STORY_KEY(실측 FP 대표) 오검출 = 천장 tripwire 발동.
        assert census(out, "candidates_scanned") > 0, \
            "PIN-NEG MK: naive_shell_form → FP 검출로 candidates>0(RED-flip), got %d\n%s" \
            % (census(out, "candidates_scanned"), out)
        assert "STORY_KEY" in out, \
            "PIN-NEG MK: STORY_KEY = 미채택 naive form 의 대표 FP — 오검출돼야 tripwire 성립\n%s" % out


# ─────────────────────── P1-B monotonic shrink + content_digest ─────────────────

def test_p1b_shrink_refuse_growth():
    """① baseline 1 pair + corpus 2 undeclared → --write-baseline 거부(exit 1) + 추가 pair 열거."""
    with tempfile.TemporaryDirectory() as tmp:
        make_corpus(tmp, MANIFEST, wf=WF_UNDECLARED, compose=COMPOSE,
                    baseline=BASELINE_FIXTURE, scripts={"pt.sh": SH_PASSTHROUGH})
        rc, out = run_scanner(SSOT_PY, tmp, "--write-baseline")
        assert rc == 1, "P1-B①: baseline growth → exit 1(거부), got %d\n%s" % (rc, out)
        assert "BASELINE GROWTH REFUSED" in out, "P1-B①: 거부 토큰\n%s" % out
        assert "scripts/pt.sh :: AUDIT_PII_KEY" in out, \
            "P1-B①: 추가될 pair 를 명시 열거해야 조치 가능\n%s" % out
        # 거부 시 baseline 파일은 불변이어야 한다(부분 write 0).
        pairs = read_baseline_pairs(os.path.join(tmp, "docs", "infra-resource-baseline.yaml"))
        assert pairs == [(".github/workflows/wf.yml", "ROGUE_TOKEN")], \
            "P1-B①: 거부인데 baseline 이 변경됨 = 부분 write, got %s" % pairs


def test_p1b_mutation_growth_check_off():
    with tempfile.TemporaryDirectory() as tmp:
        make_corpus(tmp, MANIFEST, wf=WF_UNDECLARED, compose=COMPOSE,
                    baseline=BASELINE_FIXTURE, scripts={"pt.sh": SH_PASSTHROUGH})
        mut = make_mutant(tmp, "growth_check_off")
        rc, out = run_scanner(mut, tmp, "--write-baseline")
        # RED-flip: growth 체크 제거 → 무단 확장이 조용히 통과(exit 0) + baseline 2 pair 로 증가.
        assert rc == 0, "P1-B① MK: growth_check_off → 무단 확장 통과(exit 0), got %d\n%s" % (rc, out)
        pairs = read_baseline_pairs(os.path.join(tmp, "docs", "infra-resource-baseline.yaml"))
        assert len(pairs) == 2, "P1-B① MK: baseline 이 2 pair 로 무단 확장돼야 kill 성립, got %s" % pairs


def test_p1b_shrink_allow_and_growth_hatch():
    """② corpus 0 undeclared → 재생성 성공(shrink 1→0) + escape hatch 경로."""
    with tempfile.TemporaryDirectory() as tmp:
        # WF_DECLARED(RAW_NAS_URL = manifest 선언) → undeclared 0 → new_pairs ⊂ old_pairs = shrink.
        make_corpus(tmp, MANIFEST, wf=WF_DECLARED, compose=COMPOSE, baseline=BASELINE_FIXTURE)
        rc, out = run_scanner(SSOT_PY, tmp, "--write-baseline")
        assert rc == 0, "P1-B②: shrink(확장 아님) → 재생성 성공(exit 0), got %d\n%s" % (rc, out)
        pairs = read_baseline_pairs(os.path.join(tmp, "docs", "infra-resource-baseline.yaml"))
        assert pairs == [], "P1-B②: baseline 이 0 pair 로 shrink 돼야 함, got %s" % pairs
        # 재생성 후 CHECK 가 digest 검증을 통과해야 한다(generate↔verify byte-stable, 선례 ID-1 동형).
        rc2, out2 = run_scanner(SSOT_PY, tmp)
        assert rc2 == 0, "P1-B②: 재생성 baseline 이 verify 통과해야 함(exit 0), got %d\n%s" % (rc2, out2)


def test_p1b_growth_hatch_requires_reason():
    with tempfile.TemporaryDirectory() as tmp:
        make_corpus(tmp, MANIFEST, wf=WF_UNDECLARED, compose=COMPOSE,
                    baseline=BASELINE_FIXTURE, scripts={"pt.sh": SH_PASSTHROUGH})
        # 사유 없는 override = 감사 불가 → usage 오류(exit 2).
        rc, out = run_scanner(SSOT_PY, tmp, "--write-baseline", "--allow-baseline-growth")
        assert rc == 2, "P1-B: --allow-baseline-growth 는 --reason 필수(exit 2), got %d\n%s" % (rc, out)
        # 사유 동반 → 통과 + growth_reason 각인.
        rc2, out2 = run_scanner(SSOT_PY, tmp, "--write-baseline",
                                "--allow-baseline-growth", "--reason", "정당한 corpus 확장 (hermetic test)")
        assert rc2 == 0, "P1-B: escape hatch → 통과(exit 0), got %d\n%s" % (rc2, out2)
        body = open(os.path.join(tmp, "docs", "infra-resource-baseline.yaml"), encoding="utf-8").read()
        assert "growth_reason: 정당한 corpus 확장 (hermetic test)" in body, \
            "P1-B: 사유가 baseline 에 각인돼야 감사 표면 성립\n%s" % body
        assert "GROWTH ALLOWED" in out2, "P1-B: 로그 surface\n%s" % out2


def test_p1b_digest_tamper_exit3():
    """③ baseline 수기 행 추가 → content_digest 불일치 → exit 3(substrate-failure)."""
    with tempfile.TemporaryDirectory() as tmp:
        make_corpus(tmp, MANIFEST, wf=WF_UNDECLARED, compose=COMPOSE, baseline=BASELINE_FIXTURE)
        bl = os.path.join(tmp, "docs", "infra-resource-baseline.yaml")
        rc_ok, _ = run_scanner(SSOT_PY, tmp)
        assert rc_ok == 0, "P1-B③ 전제: 무결 baseline 은 exit 0"
        # 수기 tamper — 없는 debt 를 baseline 에 밀어넣어 undeclared 를 부당 억제하려는 시도.
        with open(bl, "a", encoding="utf-8", newline="\n") as f:
            f.write("- file: .github/workflows/wf.yml\n  env_key: SNEAKY_TOKEN\n  reason: hand-added\n")
        rc, out = run_scanner(SSOT_PY, tmp)
        assert rc == 3, "P1-B③: digest 불일치 → exit 3(substrate-failure), got %d\n%s" % (rc, out)
        assert "content_digest 불일치" in out, "P1-B③: 불일치 사유 표면\n%s" % out


def test_p1b_digest_field_missing_exit3():
    with tempfile.TemporaryDirectory() as tmp:
        # digest 필드 자체를 제거(구 포맷/수기 삭제) → 검증 불가 = 신뢰 불가 → exit 3.
        no_digest = "\n".join(l for l in BASELINE_FIXTURE.splitlines()
                              if not l.startswith("content_digest:")) + "\n"
        make_corpus(tmp, MANIFEST, wf=WF_UNDECLARED, compose=COMPOSE, baseline=no_digest)
        rc, out = run_scanner(SSOT_PY, tmp)
        assert rc == 3, "P1-B: digest 필드부재 → exit 3, got %d\n%s" % (rc, out)
        assert "content_digest 필드 부재" in out, "P1-B: 필드부재 사유 표면\n%s" % out


def test_p1b_mutation_digest_verify_off():
    with tempfile.TemporaryDirectory() as tmp:
        make_corpus(tmp, MANIFEST, wf=WF_UNDECLARED, compose=COMPOSE, baseline=BASELINE_FIXTURE)
        bl = os.path.join(tmp, "docs", "infra-resource-baseline.yaml")
        with open(bl, "a", encoding="utf-8", newline="\n") as f:
            f.write("- file: .github/workflows/wf.yml\n  env_key: SNEAKY_TOKEN\n  reason: hand-added\n")
        mut = make_mutant(tmp, "digest_verify_off")
        rc, out = run_scanner(mut, tmp)
        # RED-flip: verify 생략 → 손상 baseline 이 그대로 verdict 를 냄(exit 3 아님) = tamper 무검출.
        assert rc != 3, "P1-B MK: digest_verify_off → tamper 미검출(exit 3 아님), got %d\n%s" % (rc, out)
        assert "content_digest 불일치" not in out, "P1-B MK: 불일치 표면 소멸(RED)\n%s" % out


# ─────────────────────── AC-6 orphan ─────────────────────────────────────────────

def test_ac6_orphan_default_warning():
    with tempfile.TemporaryDirectory() as tmp:
        make_corpus(tmp, MANIFEST, wf=WF_DECLARED, compose=COMPOSE)
        rc, out = run_scanner(SSOT_PY, tmp)
        assert rc == 0, "AC-6: orphan default → exit 0, got %d\n%s" % (rc, out)
        assert "ORPHAN — resource-id=api-cred" in out


def test_ac6_orphan_promote():
    with tempfile.TemporaryDirectory() as tmp:
        make_corpus(tmp, MANIFEST, wf=WF_DECLARED, compose=COMPOSE)
        rc, out = run_scanner(SSOT_PY, tmp, "--promote-orphan")
        assert rc == 1, "AC-6: orphan --promote-orphan → exit 1, got %d\n%s" % (rc, out)
        assert "ORPHAN — resource-id=api-cred" in out


def test_ac6_mutation_orphan_promote_off():
    with tempfile.TemporaryDirectory() as tmp:
        make_corpus(tmp, MANIFEST, wf=WF_DECLARED, compose=COMPOSE)
        mut = make_mutant(tmp, "orphan_promote_off")
        rc, out = run_scanner(mut, tmp, "--promote-orphan")
        # RED-flip: promote 분기 무력화 → --promote-orphan 있어도 exit 0.
        assert rc == 0, "AC-6 MK: mutant --promote-orphan → exit 0, got %d\n%s" % (rc, out)


# ─────────────────────── AC-7 substring 오분류 제외 (구조판정) ───────────────────

def test_ac7_decompose_structural_exclude():
    with tempfile.TemporaryDirectory() as tmp:
        make_corpus(tmp, MANIFEST, compose=COMPOSE, decompose=DECOMPOSE)
        rc, out = run_scanner(SSOT_PY, tmp)
        # decompose(파일명 "compose" substring)는 실 env-key 0 → inert 무기여; compose 만 inert 2.
        assert rc == 0, "AC-7: exit 0, got %d\n%s" % (rc, out)
        assert census(out, "inert_skipped") == 2, "AC-7: inert=compose-only(2), got %d" % census(out, "inert_skipped")
        assert census(out, "undeclared") == 0


def test_ac7_mutation_signal_always():
    with tempfile.TemporaryDirectory() as tmp:
        make_corpus(tmp, MANIFEST, compose=COMPOSE, decompose=DECOMPOSE)
        mut = make_mutant(tmp, "signal_always")
        rc, out = run_scanner(mut, tmp)
        # RED-flip: infra-signal 무차별 True → decompose STEP_NAME 오분류 → inert 증가(>2).
        assert census(out, "inert_skipped") > 2, \
            "AC-7 MK: signal_always → inert>2 (decompose 오분류), got %d\n%s" % (census(out, "inert_skipped"), out)


# ─────────────────────── AC-8 역색인 verdict-invariant ───────────────────────────

def test_ac8_reverse_index_verdict_invariant():
    with tempfile.TemporaryDirectory() as tmp:
        make_corpus(tmp, MANIFEST, wf=WF_DECLARED, compose=COMPOSE)
        rc_no, out_no = run_scanner(SSOT_PY, tmp)
        rc_idx, out_idx = run_scanner(SSOT_PY, tmp, "--emit-reverse-index")
        assert rc_no == rc_idx, "AC-8: verdict invariant to --emit-reverse-index (%d vs %d)" % (rc_no, rc_idx)
        assert "referenced_by=" in out_idx, "AC-8: reverse-index 방출(referenced_by=)"
        assert "referenced_by=" not in out_no, "AC-8: flag 없으면 역색인 미방출"


def test_ac8_mutation_revindex_noop():
    with tempfile.TemporaryDirectory() as tmp:
        make_corpus(tmp, MANIFEST, wf=WF_DECLARED, compose=COMPOSE)
        rc_base, _ = run_scanner(SSOT_PY, tmp, "--emit-reverse-index")
        mut = make_mutant(tmp, "revindex_noop")
        rc_mut, out_mut = run_scanner(mut, tmp, "--emit-reverse-index")
        # RED-flip: 역색인 방출 제거 → referenced_by= 소멸. BUT verdict exit 불변(I-1: side-output).
        assert "referenced_by=" not in out_mut, "AC-8 MK: revindex_noop → referenced_by= 소멸(RED)"
        assert rc_mut == rc_base, "AC-8 MK: 역색인 변조에도 verdict exit 불변(I-1), %d vs %d" % (rc_mut, rc_base)


# ─────────────────────── AC-10/11 none-disguise ─────────────────────────────────

def test_ac10_none_disguise_fail():
    with tempfile.TemporaryDirectory() as tmp:
        make_corpus(tmp, NOINFRA_YAML, wf=WF_UNDECLARED, compose=COMPOSE)
        rc, out = run_scanner(SSOT_PY, tmp)
        assert rc == 1, "AC-10: none-disguise → exit 1, got %d\n%s" % (rc, out)
        assert "::warning::check-infra-resource-drift: NONE-DISGUISE" in out


def test_ac10_mutation_none_off():
    with tempfile.TemporaryDirectory() as tmp:
        make_corpus(tmp, NOINFRA_YAML, wf=WF_UNDECLARED, compose=COMPOSE)
        mut = make_mutant(tmp, "none_off")
        rc, out = run_scanner(mut, tmp)
        # RED-flip: none-disguise 분기 무력화 → NONE-DISGUISE 토큰 소멸(undeclared 경로로 exit 1 은 유지).
        assert "NONE-DISGUISE" not in out, "AC-10 MK: none_off → NONE-DISGUISE 소멸(RED)\n%s" % out


def test_ac11_none_disguise_pass():
    with tempfile.TemporaryDirectory() as tmp:
        make_corpus(tmp, NONEOK_YAML, compose=COMPOSE)
        rc, out = run_scanner(SSOT_PY, tmp)
        assert rc == 0, "AC-11: resources:none + reason + 표면0 → exit 0, got %d\n%s" % (rc, out)
        assert "NONE-DISGUISE" not in out


# ─────────────────────── born-hollow / argparse ─────────────────────────────────

def test_born_hollow_guard():
    with tempfile.TemporaryDirectory() as tmp:
        make_corpus(tmp, MANIFEST)  # 표면 0, examples 0.
        rc, out = run_scanner(SSOT_PY, tmp)
        assert rc == 3, "born-hollow: candidates==0 ∧ inert==0 → exit 3, got %d\n%s" % (rc, out)
        assert "FAIL-CLOSED" in out


def test_argparse_error_exit2():
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    proc = subprocess.run([sys.executable, SSOT_PY, "--nonexistent-flag"],
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=env, timeout=30)
    assert proc.returncode == 2, "argparse 오류 → exit 2, got %d" % proc.returncode


# ─────────────────────── AC-17 wrapper dogfood ───────────────────────────────────

def test_ac17_wrapper_dogfood_scan():
    rc, out = run_scanner(SSOT_PY, REPO_ROOT)
    assert rc == 0, "AC-17: 실 wrapper → exit 0(PASS), got %d\n%s" % (rc, out)
    assert census(out, "candidates_scanned") >= FLOOR, \
        "AC-17: candidates≥%d (non-vacuous), got %d" % (FLOOR, census(out, "candidates_scanned"))
    assert census(out, "inert_skipped") >= 1, "AC-17: inert>0 (born-red 아님, examples compose)"
    assert census(out, "undeclared") == 0, "AC-17: 실 wrapper new undeclared 0"
    # G6 (AC-22 수렴 ratchet): 5 pair 전건 manifest 등재 완료 → baseline 0 pair + grandfathered==0 이
    #   유지돼야 한다. baseline 로직 자체의 subtract non-vacuity 는 hermetic 케이스
    #   (test_baseline_grandfather_hermetic — F-CR-005 의도된 결합 분리)가 결박하므로 여기선 무의미하지
    #   않다. 신규 debt 는 baseline 재확장이 아니라 manifest 등재로 해소하는 것이 정석 경로(ADR-157).
    assert os.path.isfile(REAL_BASELINE), "AC-17: baseline 파일 자체는 존재(digest tamper-evident 대상)"
    n_baseline = len(read_baseline_pairs(REAL_BASELINE))
    assert n_baseline == 0, \
        "AC-17(G6): baseline 은 0 pair 여야 함(AC-22 수렴 후 ratchet) — got %d pair" % n_baseline
    assert census(out, "grandfathered") == 0, \
        "AC-17(G6): grandfathered==0 (수렴 유지), got %d" % census(out, "grandfathered")


def test_ac17_canonical_secret_reverse_index():
    # G6 갱신: confluence-user-email canonical = ATLASSIAN_USER_EMAIL (2계열 수렴 — 구 CONFLUENCE_USER_EMAIL
    #   은 accepted alias 로 강등, canonical 아님) + audit-pii-key(AUDIT_PII_KEY) 신규 등재.
    rc, out = run_scanner(SSOT_PY, REPO_ROOT, "--emit-reverse-index")
    canonical = ["ANTHROPIC_API_KEY", "AUDIT_PII_KEY", "CODEFORGE_CROSS_REPO_PAT", "ATLASSIAN_API_TOKEN",
                 "ATLASSIAN_USER_EMAIL", "CONFLUENCE_BASE_URL", "CONFLUENCE_SPACE_ID",
                 "DOCKER_HUB_TOKEN", "GITHUB_TOKEN", "SSH_KEY_PASSPHRASE"]
    missing = [k for k in canonical if ("canonical_env=" + k) not in out]
    assert not missing, "AC-17: canonical secret 역색인 방출 누락 = %s" % missing
    assert "canonical_env=CONFLUENCE_USER_EMAIL" not in out, \
        "AC-17(G6): CONFLUENCE_USER_EMAIL 은 canonical 이 아니라 accepted alias 여야 함(2계열 수렴)"


def test_ac17_mutation_no_secrets():
    with tempfile.TemporaryDirectory() as tmp:
        mut = make_mutant(tmp, "no_secrets")
        rc_base, out_base = run_scanner(SSOT_PY, REPO_ROOT)
        rc_mut, out_mut = run_scanner(mut, REPO_ROOT)
        base_c = census(out_base, "candidates_scanned")
        mut_c = census(out_mut, "candidates_scanned")
        # RED-flip: workflow secrets 스캔 제거 → 실 repo candidates 급감(<floor, <실측) = secrets load-bearing.
        assert mut_c < FLOOR and mut_c < base_c, \
            "AC-17 MK: no_secrets → candidates<%d & <%d, got %d" % (FLOOR, base_c, mut_c)


# ─────────────────────── AC-22 DEC-3 2계열 canonical 수렴 (G6) ────────────────────

def test_ac22_two_series_convergence_fixture_pair():
    """discriminating pair: canonical 1 + accepted alias 선언 = 수렴(exit 0) / alias 누락 = 미수렴(exit 1).

    동일 소비면(선언면 `_env:` ATLASSIAN_USER_EMAIL + 소비면 secrets.CONFLUENCE_USER_EMAIL)에 manifest 만
    바꿔 대조 — alias 선언이 load-bearing 임을 fixture 로 증명(rename 0 = ADR-157 §결정5 무중단 조건).
    """
    with tempfile.TemporaryDirectory() as tmp:
        make_corpus(tmp, PROJ_TWO_SERIES_CONVERGED, wf=WF_ALIAS_CONSUME, compose=COMPOSE)
        rc, out = run_scanner(SSOT_PY, tmp)
        assert rc == 0, "AC-22: 2계열 양키 선언(canonical+alias) → 수렴 PASS(exit 0), got %d\n%s" % (rc, out)
        assert census(out, "undeclared") == 0, "AC-22: 수렴 시 undeclared 0\n%s" % out
        assert census(out, "candidates_scanned") == 2, \
            "AC-22: 선언면+소비면 2 candidate (수렴이 census 를 깎지 않음), got %d" \
            % census(out, "candidates_scanned")
    with tempfile.TemporaryDirectory() as tmp:
        make_corpus(tmp, PROJ_TWO_SERIES_UNCONVERGED, wf=WF_ALIAS_CONSUME, compose=COMPOSE)
        rc, out = run_scanner(SSOT_PY, tmp)
        assert rc == 1, "AC-22: alias 누락 manifest → 미수렴 FLAG(exit 1), got %d\n%s" % (rc, out)
        assert "env-key=CONFLUENCE_USER_EMAIL" in out, \
            "AC-22: 미수렴 시 소비면 alias 가 UNDECLARED 로 표면화\n%s" % out
        assert "env-key=ATLASSIAN_USER_EMAIL" not in out, \
            "AC-22: canonical 자체는 선언돼 있어 undeclared 아님(판별 정밀)\n%s" % out


def test_ac22_wrapper_live_convergence_zero_without_baseline():
    """wrapper-live AC-22: baseline 제거 상태 스캔 = exit 0 + undeclared 0 + grandfathered 0.

    "non-zero→zero 확증"의 zero 면 — 정정 전(舊 manifest)에는 같은 조건에서 undeclared=5(비영)였다
    (G6 착수 시 firsthand 재현, PR 기록). 이제 5 pair 전건이 선언으로 분류돼 baseline subtract 없이도 0.
    + 2계열/alias-gap/audit-pii-key 의 자원 매핑을 역색인으로 결박(양키 분류 확인).
    """
    rc, out = run_scanner(SSOT_PY, REPO_ROOT,
                          "--baseline", os.path.join(REPO_ROOT, "docs", "__no-such-baseline__.yaml"),
                          "--emit-reverse-index")
    assert rc == 0, "AC-22: baseline 없이 실 wrapper → exit 0, got %d\n%s" % (rc, out)
    assert census(out, "undeclared") == 0, "AC-22: undeclared 0 (선언 수렴)\n%s" % out
    assert census(out, "grandfathered") == 0, "AC-22: grandfathered 0 (baseline subtract 미개입)\n%s" % out
    # 2계열 양키 분류: confluence-user-email 자원 한 줄에 선언면(project.yaml)과 소비면(workflow) 동시 매핑.
    mm = re.search(r"resource-id=confluence-user-email canonical_env=ATLASSIAN_USER_EMAIL "
                   r"referenced_by=\[([^\]]*)\]", out)
    assert mm, "AC-22: confluence-user-email 역색인 라인 부재(canonical=ATLASSIAN_USER_EMAIL)\n%s" % out
    refs = mm.group(1)
    assert ".claude/_overlay/project.yaml" in refs and ".github/workflows/confluence-forward-sync.yml" in refs, \
        "AC-22: 2계열 참조면(선언면+소비면) 동일 자원 매핑 실패 — refs=%s" % refs
    # alias-gap 해소: GH_TOKEN 스크립트 소비면이 github-token 자원으로 흡수.
    mm = re.search(r"resource-id=github-token canonical_env=GITHUB_TOKEN referenced_by=\[([^\]]*)\]", out)
    assert mm and "scripts/canary_auto_promote.py" in mm.group(1) \
        and "scripts/lib/check_deferred_item_recovery.py" in mm.group(1), \
        "AC-22: GH_TOKEN alias 소비면의 github-token 매핑 실패\n%s" % out
    # audit-pii-key 신규 자원: .py 리터럴 + .sh passthrough 양 소비면 매핑.
    mm = re.search(r"resource-id=audit-pii-key canonical_env=AUDIT_PII_KEY referenced_by=\[([^\]]*)\]", out)
    assert mm and "scripts/lib/audit_trail_pii_redact.py" in mm.group(1) \
        and "scripts/audit-trail-fetch.sh" in mm.group(1), \
        "AC-22: AUDIT_PII_KEY 소비면(py+sh)의 audit-pii-key 매핑 실패\n%s" % out
    # 미선언 잔존 0 의 역색인 대응면: unmapped 키 목록 자체가 방출되지 않아야 한다.
    assert "unmapped-undeclared-keys" not in out, \
        "AC-22: unmapped-undeclared-keys 방출 = 미해소 잔존 non-zero\n%s" % out


# ─────────────────────── standalone runner ──────────────────────────────────────

def _main():
    tests = [(n, f) for n, f in sorted(globals().items())
             if n.startswith("test_") and callable(f)]
    npass = 0
    nfail = 0
    print("=" * 75)
    print(" CFP-2700 G2: infra-resource-drift — discriminating self-test (.py)")
    print("=" * 75)
    for name, fn in tests:
        try:
            fn()
            print("OK PASS: %s" % name)
            npass += 1
        except AssertionError as e:
            print("X FAIL: %s\n  %s" % (name, e))
            nfail += 1
        except Exception as e:  # noqa: BLE001 — self-test 안전망(anchor drift 등).
            print("X ERROR: %s\n  %r" % (name, e))
            nfail += 1
    print("-" * 75)
    print("PASS: %d  FAIL: %d" % (npass, nfail))
    if nfail == 0:
        print("OK All %d cases pass — AC-5/6/7/8/10/11/17/22 discriminating + mutation-kill + born-hollow" % npass)
        return 0
    print("X %d case(s) failed" % nfail)
    return 1


if __name__ == "__main__":
    sys.exit(_main())
