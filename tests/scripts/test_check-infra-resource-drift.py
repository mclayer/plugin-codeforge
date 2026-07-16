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
    AC-17 wrapper 실 secret 9종 dogfood (실 repo → exit0, candidates≥floor, inert>0, grandfathered≥3)
      + MK no_secrets(실 repo candidates 급감 = secrets 스캔 load-bearing)
  + grandfather baseline hermetic(tmp corpus) + MK baseline_subtract_off
  + born-hollow guard(candidates==0 ∧ inert==0 → exit3) + argparse 오류(exit 2).

★ baseline 판별력 분산 (F-CR-005): 본 정정 전 baseline 로직 mutant(subtract_off / gf_counter_off /
  load_baseline_empty) 3종이 **모두 test_ac17_wrapper_dogfood_scan 단 하나로만** 죽었다(실측). AC-17 의
  killer 는 실 repo debt count 에 결박된 `grandfathered≥3`(현 baseline 4 pair — 여유 1)이라, manifest
  등재로 baseline 이 shrink 하면 정상 코드가 false-RED 로 깨진다. → tmp corpus hermetic 케이스를 신설해
  baseline subtract 를 실 debt count 와 무관하게 결박(위 3 mutant 전건 hermetic kill 확보, 실측).
  AC-17 의 `grandfathered≥3` 은 non-vacuity floor 로 존치하되 **유일 killer 가 아니게** 됐다 —
  baseline shrink 시 조정 대상은 AC-17 뿐이며 hermetic 케이스는 무영향(의도된 결합 분리).

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
FLOOR = 50  # 실 wrapper census 안정 하한 (현 실측 candidates_scanned=129).

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
BASELINE_FIXTURE = """grandfathered_undeclared_surfaces:
- file: .github/workflows/wf.yml
  env_key: ROGUE_TOKEN
  reason: hermetic fixture — 승격 시점 pre-existing 로 가정
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
}


# ─────────────────────── helpers ────────────────────────────────────────────────

def _write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)


def make_corpus(tmp, project_yaml, wf=None, compose=None, decompose=None, baseline=None):
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
    assert census(out, "undeclared") == 0, "AC-17: 실 wrapper new undeclared 0 (baseline grandfather)"
    assert census(out, "grandfathered") >= 3, "AC-17: grandfathered≥3 (ATLASSIAN_USER_EMAIL/AUDIT_PII_KEY/GH_TOKEN)"


def test_ac17_nine_secret_reverse_index():
    rc, out = run_scanner(SSOT_PY, REPO_ROOT, "--emit-reverse-index")
    nine = ["ANTHROPIC_API_KEY", "CODEFORGE_CROSS_REPO_PAT", "ATLASSIAN_API_TOKEN",
            "CONFLUENCE_BASE_URL", "CONFLUENCE_SPACE_ID", "CONFLUENCE_USER_EMAIL",
            "DOCKER_HUB_TOKEN", "GITHUB_TOKEN", "SSH_KEY_PASSPHRASE"]
    missing = [k for k in nine if ("canonical_env=" + k) not in out]
    assert not missing, "AC-17: 9종 canonical secret 역색인 방출 누락 = %s" % missing


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
        print("OK All %d cases pass — AC-5/6/7/8/10/11/17 discriminating + mutation-kill + born-hollow" % npass)
        return 0
    print("X %d case(s) failed" % nfail)
    return 1


if __name__ == "__main__":
    sys.exit(_main())
