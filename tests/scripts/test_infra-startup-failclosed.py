#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
tests/scripts/test_infra-startup-failclosed.py
CFP-2700 (Epic) G3 Phase 2 (구현 lane) — Discriminating self-test (.py channel) for
  scripts/lib/check_infra_manifest_schema.py (AC-2 manifest schema validator) +
  scripts/lib/infra_startup_validator.py (AC-3/9/15 D2 startup fail-closed reference-impl) +
  tests/fixtures/infra-refimpl/ (AC-19 discriminating fixture pair).

★ .sh 채널(ADR-151 인벤토리 enroll)과 disjoint 보완 — 본 채널이 hermetic 상세·mutation 다수 관할.
  presence-grep 금지 — 전 케이스 subprocess 실 실행 + exit code + FIXED 토큰 결박 + mutation RED-flip:

  AC-2  manifest schema 4 필수 필드 (id/canonical_env/aliases/required) 필드별 negative fixture →
        non-zero exit + 누락 필드명 출력. positive control 1건 + mode enum/no-silent-degrade/dangling
        + MK schema_id_off / schema_required_off (검사 무력화 → negative 가 PASS = RED-flip).
  AC-3  D2 startup fail-closed 4계약: (1) 프로세스 env 검사(.env red-herring 무시) (2) exit-masking
        금지(78 전파) (3) 빈 값 reject (4) fail-closed default(mode 엔트리 부재 = required /
        block 부재·unit 미선언 = 거부) + optional_degradable degrade+WARN 계속
        + MK empty_value_ok / mode_default_open / missing_masked.
  AC-9  allow-set parity: --emit-allow-set union == D3 스캐너 parse_manifest classified (diff 0,
        같은 파서 산출 실측) + 공유 파서 mutation(deprecated_unclassified — G2 동일 anchor) 주입 시
        PARITY-BROKEN(exit 78) 트립 = parity 가 산문 아닌 집행 계약임의 증명.
  AC-15 채택 경로 3-way: adopted+누락→FAIL / 미채택+사유→비적용 PASS / 미채택+사유부재→FAIL
        + MK adoption_failopen (사유부재 통과 = RED-flip).
  AC-19 execution-backed fixture 판별: refimpl-enforced 미설정 → startup 단계 exit 78 + 센티넬
        **부재**(선언O+대조O=PASS 형상) / refimpl-unenforced → 센티넬 **출력 후** late-crash
        (선언O+대조X=FAIL 형상) + MK missing_masked 주입 시 enforced 가 unenforced 형상으로 퇴화
        (센티넬 출력 = RED-flip).

★ 자원 키 self-containment: fixture/validator subprocess 는 최소 env(파이썬 구동 필수 키만 승계,
  RAW_NAS_URL 등 자원 키 0)로 실행 — `env -i` 등가 (.sh 채널은 실제 env -i 사용).

standalone: `python3 tests/scripts/test_infra-startup-failclosed.py` → 전 test_* 실행, exit 0=PASS.
"""

import os
import re
import shutil
import subprocess
import sys
import tempfile

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
LIB = os.path.join(REPO_ROOT, "scripts", "lib")
SCHEMA_PY = os.path.join(LIB, "check_infra_manifest_schema.py")
VALIDATOR_PY = os.path.join(LIB, "infra_startup_validator.py")
PARSER_PY = os.path.join(LIB, "check_infra_resource_drift.py")
FIXTURE_DIR = os.path.join(REPO_ROOT, "tests", "fixtures", "infra-refimpl")
FIXTURE_MANIFEST = os.path.join(FIXTURE_DIR, "manifest.yaml")
ENFORCED = os.path.join(FIXTURE_DIR, "refimpl_enforced.py")
UNENFORCED = os.path.join(FIXTURE_DIR, "refimpl_unenforced.py")
SENTINEL = "BUSINESS_OP_REACHED"
EX_CONFIG = 78

# ─────────────────────── manifest fixtures (스키마 negative 도출 원본) ───────────
VALID_MANIFEST = """infra_resources:
  resources:
    - id: raw-nas
      canonical_env: RAW_NAS_URL
      aliases:
        accepted: [MINIO_URL]
        deprecated:
          - name: LEGACY_NAS_URL
    - id: derived-nas
      canonical_env: DERIVED_NAS_URL
      aliases:
        accepted: []
  execution_units:
    collector:
      required: [raw-nas, derived-nas]
      resource_modes:
        raw-nas: required
        derived-nas: optional_degradable
        derived-nas_degraded_behavior: "derived write skip + WARN"
"""

NOT_ADOPTED_WITH_REASON = VALID_MANIFEST + """  startup_validation:
    adopted: false
    reason: "declarative-only consumer — 부팅하는 제품 바이너리 부재"
"""

NOT_ADOPTED_NO_REASON = VALID_MANIFEST + """  startup_validation:
    adopted: false
"""

# 소스 문자열-치환 mutation (anchor → replacement). 대상 모듈별 분리.
SCHEMA_MUTATIONS = {
    "schema_id_off": (
        '        if "id" not in item["keys"] or not item["id"]:',
        "        if False:  # MUTANT-schema-id-off",
    ),
    "schema_required_off": (
        '        if "required" not in u["keys"]:',
        "        if False:  # MUTANT-schema-required-off",
    ),
}
VALIDATOR_MUTATIONS = {
    # 계약 (3) 빈 값 reject 무력화 → set-but-empty 가 충족으로 오판.
    "empty_value_ok": (
        '    return val is not None and val.strip() != ""',
        "    return val is not None  # MUTANT-empty-value-ok",
    ),
    # 계약 (4) fail-closed default 무력화 → mode 엔트리 부재 = optional 취급 (fail-open).
    "mode_default_open": (
        '        mode = unit["modes"].get(rid, "required")',
        '        mode = unit["modes"].get(rid, "optional_degradable")  # MUTANT-mode-default-open',
    ),
    # 계약 (2) exit-masking: missing 판정 자체를 삼킴 → BOOT-REFUSED 소멸 = 지연 크래시 예약.
    "missing_masked": (
        "    if missing:",
        "    if False:  # MUTANT-missing-masked",
    ),
    # AC-15 사유부재 fail-closed 무력화 → 무사유 미채택이 조용히 통과.
    "adoption_failopen": (
        "    if adopted is False and reason:",
        "    if adopted is False:  # MUTANT-adoption-failopen",
    ),
}
# 공유 파서 mutation — G2 self-test 와 동일 anchor (deprecated alias allow-set 미편입).
PARSER_MUTATIONS = {
    "deprecated_unclassified": (
        "            m.classified.add(d)",
        "            pass  # MUTANT-deprecated-unclassified",
    ),
}


# ─────────────────────── helpers ────────────────────────────────────────────────

def clean_env(extra=None):
    """자원 키 0 의 최소 env (env -i 등가) — 파이썬 구동 필수 키만 승계."""
    base = {"PYTHONIOENCODING": "utf-8"}
    for k in ("SYSTEMROOT", "SystemRoot", "PATH", "PATHEXT", "TEMP", "TMP", "TMPDIR"):
        if k in os.environ:
            base[k] = os.environ[k]
    for k in ("RAW_NAS_URL", "MINIO_URL", "LEGACY_NAS_URL", "DERIVED_NAS_URL"):
        assert k not in base, "clean_env 에 자원 키 %s 유입 — self-containment 파손" % k
    if extra:
        base.update(extra)
    return base


def run_py(args, env=None):
    proc = subprocess.run([sys.executable] + args, stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT, env=(env or clean_env()), timeout=60)
    return proc.returncode, proc.stdout.decode("utf-8", "replace")


def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)


def write_manifest(tmp, content):
    p = os.path.join(tmp, "m.yaml")
    write(p, content)
    return p


def make_mutant_lib(tmp, target_path, mutations, kind):
    """scripts/lib 3-모듈을 tmp 로 복사하되 target 만 kind mutation 적용 → tmp lib dir 반환.

    (schema/validator 는 sibling parser 를 own-dir 에서 import 하므로 3-모듈 동반 복사 필수.)
    """
    libdir = os.path.join(tmp, "mutlib")
    os.makedirs(libdir, exist_ok=True)
    for src in (SCHEMA_PY, VALIDATOR_PY, PARSER_PY):
        dst = os.path.join(libdir, os.path.basename(src))
        if os.path.abspath(src) == os.path.abspath(target_path):
            old, new = mutations[kind]
            body = open(src, encoding="utf-8").read()
            mutated = body.replace(old, new, 1)
            assert mutated != body, "mutation did not apply — anchor drift (kind=%s)" % kind
            with open(dst, "w", encoding="utf-8", newline="\n") as f:
                f.write(mutated)
        else:
            shutil.copyfile(src, dst)
    return libdir


# ─────────────────────── AC-2 manifest schema validator ─────────────────────────

def test_ac2_positive_control():
    with tempfile.TemporaryDirectory() as tmp:
        p = write_manifest(tmp, VALID_MANIFEST)
        rc, out = run_py([SCHEMA_PY, "--manifest", p])
        assert rc == 0, "AC-2: positive control → exit 0, got %d\n%s" % (rc, out)
        assert "check-infra-manifest-schema: PASS" in out


def test_ac2_missing_id():
    neg = VALID_MANIFEST.replace(
        "    - id: raw-nas\n      canonical_env: RAW_NAS_URL\n",
        "    - canonical_env: RAW_NAS_URL\n")
    with tempfile.TemporaryDirectory() as tmp:
        p = write_manifest(tmp, neg)
        rc, out = run_py([SCHEMA_PY, "--manifest", p])
        assert rc == 1, "AC-2: id 누락 → exit 1, got %d\n%s" % (rc, out)
        assert "필수 필드 누락: id" in out, "AC-2: 누락 필드명 'id' 출력\n%s" % out


def test_ac2_missing_canonical_env():
    neg = VALID_MANIFEST.replace("      canonical_env: RAW_NAS_URL\n", "")
    with tempfile.TemporaryDirectory() as tmp:
        p = write_manifest(tmp, neg)
        rc, out = run_py([SCHEMA_PY, "--manifest", p])
        assert rc == 1, "AC-2: canonical_env 누락 → exit 1, got %d\n%s" % (rc, out)
        assert "필수 필드 누락: canonical_env" in out


def test_ac2_missing_aliases():
    neg = VALID_MANIFEST.replace("      aliases:\n        accepted: []\n", "")
    with tempfile.TemporaryDirectory() as tmp:
        p = write_manifest(tmp, neg)
        rc, out = run_py([SCHEMA_PY, "--manifest", p])
        assert rc == 1, "AC-2: aliases 누락 → exit 1, got %d\n%s" % (rc, out)
        assert "필수 필드 누락: aliases" in out


def test_ac2_missing_required():
    neg = VALID_MANIFEST.replace("      required: [raw-nas, derived-nas]\n", "")
    with tempfile.TemporaryDirectory() as tmp:
        p = write_manifest(tmp, neg)
        rc, out = run_py([SCHEMA_PY, "--manifest", p])
        assert rc == 1, "AC-2: required 누락 → exit 1, got %d\n%s" % (rc, out)
        assert "필수 필드 누락: required" in out


def test_ac2_mode_contracts():
    with tempfile.TemporaryDirectory() as tmp:
        p = write_manifest(tmp, VALID_MANIFEST.replace("raw-nas: required", "raw-nas: mandatory"))
        rc, out = run_py([SCHEMA_PY, "--manifest", p])
        assert rc == 1 and "resource_modes 값 위반" in out, \
            "AC-2: mode enum 위반 → exit 1, got %d\n%s" % (rc, out)
        p2 = write_manifest(tmp, VALID_MANIFEST.replace(
            '        derived-nas_degraded_behavior: "derived write skip + WARN"\n', ""))
        rc2, out2 = run_py([SCHEMA_PY, "--manifest", p2])
        assert rc2 == 1 and "no-silent-degrade" in out2, \
            "AC-2: degraded_behavior 부재 → exit 1, got %d\n%s" % (rc2, out2)
        p3 = write_manifest(tmp, VALID_MANIFEST.replace(
            "required: [raw-nas, derived-nas]", "required: [raw-nas, ghost-res]"))
        rc3, out3 = run_py([SCHEMA_PY, "--manifest", p3])
        assert rc3 == 1 and "참조 자원 미정의: ghost-res" in out3, \
            "AC-2: dangling rid → exit 1, got %d\n%s" % (rc3, out3)


def test_ac2_none_sentinel_paths():
    with tempfile.TemporaryDirectory() as tmp:
        p = write_manifest(tmp, "infra_resources:\n  resources: none\n  reason: no infra deps\n")
        rc, out = run_py([SCHEMA_PY, "--manifest", p])
        assert rc == 0 and "유효한 비적용 선언" in out, \
            "AC-2: none+reason → exit 0, got %d\n%s" % (rc, out)
        p2 = write_manifest(tmp, "infra_resources:\n  resources: none\n")
        rc2, out2 = run_py([SCHEMA_PY, "--manifest", p2])
        assert rc2 == 1 and "필수 필드 누락: reason" in out2, \
            "AC-2: none 무사유 → exit 1, got %d\n%s" % (rc2, out2)


def test_ac2_mutation_schema_id_off():
    neg = VALID_MANIFEST.replace(
        "    - id: raw-nas\n      canonical_env: RAW_NAS_URL\n",
        "    - canonical_env: RAW_NAS_URL\n")
    with tempfile.TemporaryDirectory() as tmp:
        libdir = make_mutant_lib(tmp, SCHEMA_PY, SCHEMA_MUTATIONS, "schema_id_off")
        p = write_manifest(tmp, neg)
        rc, out = run_py([os.path.join(libdir, "check_infra_manifest_schema.py"), "--manifest", p])
        # RED-flip: id 검사 무력화 → "필수 필드 누락: id" 소멸 (dangling 위반은 잔존 가능 — 토큰만 결박).
        assert "필수 필드 누락: id" not in out, \
            "AC-2 MK: schema_id_off → id 위반 소멸(RED-flip)이어야 함\n%s" % out


def test_ac2_mutation_schema_required_off():
    neg = VALID_MANIFEST.replace("      required: [raw-nas, derived-nas]\n", "")
    with tempfile.TemporaryDirectory() as tmp:
        libdir = make_mutant_lib(tmp, SCHEMA_PY, SCHEMA_MUTATIONS, "schema_required_off")
        p = write_manifest(tmp, neg)
        rc, out = run_py([os.path.join(libdir, "check_infra_manifest_schema.py"), "--manifest", p])
        assert rc == 0 and "필수 필드 누락: required" not in out, \
            "AC-2 MK: schema_required_off → required 위반 소멸 + exit 0 (RED-flip), got %d\n%s" % (rc, out)


# ─────────────────────── AC-3 D2 startup fail-closed 4계약 ───────────────────────

def test_ac3_required_missing_boot_refuse():
    rc, out = run_py([VALIDATOR_PY, "--unit", "collector", "--manifest", FIXTURE_MANIFEST])
    assert rc == EX_CONFIG, "AC-3: required 미설정 → exit %d, got %d\n%s" % (EX_CONFIG, rc, out)
    assert "STARTUP-FAILCLOSED" in out and "raw-nas" in out, \
        "AC-3: 미설정 자원 ID(raw-nas) loud 로그\n%s" % out
    assert "BOOT-REFUSED" in out


def test_ac3_empty_value_reject():
    rc, out = run_py([VALIDATOR_PY, "--unit", "collector", "--manifest", FIXTURE_MANIFEST],
                     env=clean_env({"RAW_NAS_URL": "   "}))
    assert rc == EX_CONFIG, "AC-3 계약(3): set-but-empty = 미설정 → exit %d, got %d\n%s" % (EX_CONFIG, rc, out)
    assert "raw-nas" in out


def test_ac3_process_env_not_dotenv():
    """계약 (1): .env 파일에 키가 있어도 프로세스 env 미설정이면 거부 (.env red-herring)."""
    with tempfile.TemporaryDirectory() as tmp:
        write(os.path.join(tmp, ".env"), "RAW_NAS_URL=http://from-dotenv\nDERIVED_NAS_URL=x\n")
        manifest = write_manifest(tmp, open(FIXTURE_MANIFEST, encoding="utf-8").read())
        rc, out = run_py([VALIDATOR_PY, "--unit", "collector", "--manifest", manifest])
        assert rc == EX_CONFIG, \
            "AC-3 계약(1): .env 존재해도 프로세스 env 기준 거부 → exit %d, got %d\n%s" % (EX_CONFIG, rc, out)


def test_ac3_optional_degradable_continues():
    rc, out = run_py([VALIDATOR_PY, "--unit", "collector", "--manifest", FIXTURE_MANIFEST],
                     env=clean_env({"RAW_NAS_URL": "http://nas"}))
    assert rc == 0, "AC-3 계약(4): optional_degradable 미설정 = degrade 계속 → exit 0, got %d\n%s" % (rc, out)
    assert "DEGRADED" in out and "derived-nas" in out and "STARTUP-OK" in out


def test_ac3_mode_absent_defaults_required():
    """계약 (4): resource_modes 엔트리 부재 unit(writer) → required 취급 = 거부."""
    rc, out = run_py([VALIDATOR_PY, "--unit", "writer", "--manifest", FIXTURE_MANIFEST])
    assert rc == EX_CONFIG, "AC-3 계약(4): mode 부재 = required 취급 → exit %d, got %d\n%s" % (EX_CONFIG, rc, out)


def test_ac3_declaration_absent_failclosed():
    """계약 (4): block 부재 / unit 미선언 → '감지 비활성' 아닌 거부 (proto 결함 (d) 봉인)."""
    with tempfile.TemporaryDirectory() as tmp:
        p = write_manifest(tmp, "project: demo\n")
        rc, out = run_py([VALIDATOR_PY, "--unit", "collector", "--manifest", p])
        assert rc == EX_CONFIG, "AC-3: block 부재 → exit %d, got %d\n%s" % (EX_CONFIG, rc, out)
        rc2, out2 = run_py([VALIDATOR_PY, "--unit", "ghost", "--manifest", FIXTURE_MANIFEST])
        assert rc2 == EX_CONFIG and "실행단위 미선언" in out2, \
            "AC-3: unit 미선언 → exit %d, got %d\n%s" % (EX_CONFIG, rc2, out2)


def test_ac3_mutation_empty_value_ok():
    with tempfile.TemporaryDirectory() as tmp:
        libdir = make_mutant_lib(tmp, VALIDATOR_PY, VALIDATOR_MUTATIONS, "empty_value_ok")
        rc, out = run_py([os.path.join(libdir, "infra_startup_validator.py"),
                          "--unit", "writer", "--manifest", FIXTURE_MANIFEST],
                         env=clean_env({"RAW_NAS_URL": "   "}))
        # RED-flip: 빈 값 reject 무력화 → set-but-empty 가 충족 오판 = STARTUP-OK (exit 0).
        assert rc == 0 and "STARTUP-OK" in out, \
            "AC-3 MK: empty_value_ok → 빈 값 통과(RED-flip, exit 0), got %d\n%s" % (rc, out)


def test_ac3_mutation_mode_default_open():
    with tempfile.TemporaryDirectory() as tmp:
        libdir = make_mutant_lib(tmp, VALIDATOR_PY, VALIDATOR_MUTATIONS, "mode_default_open")
        rc, out = run_py([os.path.join(libdir, "infra_startup_validator.py"),
                          "--unit", "writer", "--manifest", FIXTURE_MANIFEST])
        # RED-flip: fail-closed default 무력화 → mode 부재 unit 이 degrade 로 새어 exit 0.
        assert rc == 0, "AC-3 MK: mode_default_open → fail-open 퇴화(exit 0 = RED-flip), got %d\n%s" % (rc, out)


# ─────────────────────── AC-9 allow-set parity (G2 파서 재사용) ──────────────────

def test_ac9_allow_set_parity_diff0():
    """--emit-allow-set union == D3 스캐너 parse_manifest classified — 동일 manifest diff 0 실측."""
    rc, out = run_py([VALIDATOR_PY, "--emit-allow-set", "--manifest", FIXTURE_MANIFEST])
    assert rc == 0, "AC-9: emit-allow-set → exit 0, got %d\n%s" % (rc, out)
    mm = re.search(r"allow-set union=(\S+)", out)
    assert mm, "AC-9: union 라인 부재\n%s" % out
    startup_union = set(mm.group(1).split(","))
    # 스캐너 측: 동일 파서 모듈을 스캐너 관점(D3 allow_set = classified)에서 subprocess 실행으로 산출.
    code = ("import sys; sys.path.insert(0, %r); import check_infra_resource_drift as d; "
            "m = d.parse_manifest(%r); print(','.join(sorted(m.classified)))" % (LIB, FIXTURE_MANIFEST))
    rc2, out2 = run_py(["-c", code])
    assert rc2 == 0, "AC-9: 스캐너측 classified 산출 실패\n%s" % out2
    scanner_set = set(out2.strip().splitlines()[-1].split(","))
    assert startup_union == scanner_set, \
        "AC-9: parity diff != 0 — startup=%s scanner=%s" % (sorted(startup_union), sorted(scanner_set))


def test_ac9_behavioral_parity_deprecated_alias():
    """행동 parity: 스캐너가 classified 로 인정하는 deprecated alias = startup 충족 키."""
    rc, out = run_py([VALIDATOR_PY, "--unit", "collector", "--manifest", FIXTURE_MANIFEST],
                     env=clean_env({"LEGACY_NAS_URL": "http://legacy", "DERIVED_NAS_URL": "x"}))
    assert rc == 0 and "deprecated alias" in out, \
        "AC-9: deprecated alias 로 충족 + WARN, got %d\n%s" % (rc, out)


def test_ac9_mutation_shared_parser_parity_tripwire():
    """공유 파서 mutation(deprecated_unclassified — G2 동일 anchor) → PARITY-BROKEN 트립.

    classified(스캐너 allow_set)에서만 deprecated 가 빠지면 union(all_keys_by_resource)과 갈라진다
    — --emit-allow-set 의 내부 self-assert 가 exit 78 로 트립 = parity 는 집행 계약(산문 아님).
    """
    with tempfile.TemporaryDirectory() as tmp:
        libdir = make_mutant_lib(tmp, PARSER_PY, PARSER_MUTATIONS, "deprecated_unclassified")
        rc, out = run_py([os.path.join(libdir, "infra_startup_validator.py"),
                          "--emit-allow-set", "--manifest", FIXTURE_MANIFEST])
        assert rc == EX_CONFIG and "PARITY-BROKEN" in out, \
            "AC-9 MK: 파서 분기 mutation → PARITY-BROKEN exit %d (RED-flip), got %d\n%s" % (EX_CONFIG, rc, out)


# ─────────────────────── AC-15 consumer 채택 경로 ───────────────────────────────

def test_ac15_adopted_missing_fail():
    rc, out = run_py([VALIDATOR_PY, "--adoption-check", "--manifest", FIXTURE_MANIFEST])
    assert rc == EX_CONFIG and "ADOPTION-FAIL" in out, \
        "AC-15: 채택 + 누락 → FAIL(exit %d), got %d\n%s" % (EX_CONFIG, rc, out)


def test_ac15_adopted_all_set_pass():
    rc, out = run_py([VALIDATOR_PY, "--adoption-check", "--manifest", FIXTURE_MANIFEST],
                     env=clean_env({"RAW_NAS_URL": "http://nas", "DERIVED_NAS_URL": "http://derived"}))
    assert rc == 0 and "ADOPTED-PASS" in out, \
        "AC-15: 채택 + 전건 충족 → PASS, got %d\n%s" % (rc, out)


def test_ac15_not_adopted_with_reason_pass():
    with tempfile.TemporaryDirectory() as tmp:
        p = write_manifest(tmp, NOT_ADOPTED_WITH_REASON)
        rc, out = run_py([VALIDATOR_PY, "--adoption-check", "--manifest", p])
        assert rc == 0 and "NOT-ADOPTED-PASS" in out, \
            "AC-15: 미채택 + 사유 → 비적용 PASS, got %d\n%s" % (rc, out)


def test_ac15_not_adopted_no_reason_fail():
    with tempfile.TemporaryDirectory() as tmp:
        p = write_manifest(tmp, NOT_ADOPTED_NO_REASON)
        rc, out = run_py([VALIDATOR_PY, "--adoption-check", "--manifest", p])
        assert rc == EX_CONFIG and "ADOPTION-FAIL" in out, \
            "AC-15: 미채택 + 사유부재 → FAIL, got %d\n%s" % (rc, out)
        # 선언 자체 부재도 동일 fail-closed.
        p2 = write_manifest(tmp, VALID_MANIFEST)
        rc2, out2 = run_py([VALIDATOR_PY, "--adoption-check", "--manifest", p2])
        assert rc2 == EX_CONFIG, "AC-15: startup_validation 미선언 → FAIL, got %d\n%s" % (rc2, out2)


def test_ac15_mutation_adoption_failopen():
    with tempfile.TemporaryDirectory() as tmp:
        libdir = make_mutant_lib(tmp, VALIDATOR_PY, VALIDATOR_MUTATIONS, "adoption_failopen")
        p = write_manifest(tmp, NOT_ADOPTED_NO_REASON)
        rc, out = run_py([os.path.join(libdir, "infra_startup_validator.py"),
                          "--adoption-check", "--manifest", p])
        # RED-flip: 사유부재 fail-closed 무력화 → 무사유 미채택이 조용히 PASS.
        assert rc == 0, "AC-15 MK: adoption_failopen → 무사유 통과(RED-flip, exit 0), got %d\n%s" % (rc, out)


# ─────────────────────── AC-19 discriminating fixture pair (execution-backed) ────

def test_ac19_enforced_missing_startup_stage_exit():
    """선언O + startup대조O: 미설정 → 첫 business 이전 exit 78, 센티넬 **부재** = PASS 형상."""
    rc, out = run_py([ENFORCED])
    assert rc == EX_CONFIG, "AC-19: enforced 미설정 → exit %d, got %d\n%s" % (EX_CONFIG, rc, out)
    assert SENTINEL not in out, \
        "AC-19: 센티넬 출력됨 = business 도달 = startup-stage exit 아님(FAIL 형상)\n%s" % out
    assert "raw-nas" in out, "AC-19: 미설정 자원 ID 로그\n%s" % out


def test_ac19_enforced_set_reaches_business():
    rc, out = run_py([ENFORCED], env=clean_env({"RAW_NAS_URL": "http://nas"}))
    assert rc == 0 and SENTINEL in out, \
        "AC-19: enforced 설정 → business 도달(센티넬) + exit 0, got %d\n%s" % (rc, out)


def test_ac19_unenforced_late_crash_discriminated():
    """선언O + startup대조X: 센티넬 출력 **후** late-crash = FAIL 형상 (판별 성립)."""
    rc, out = run_py([UNENFORCED])
    assert SENTINEL in out, \
        "AC-19: unenforced 는 미설정에도 business 도달(센티넬)해야 판별 성립\n%s" % out
    assert rc not in (0, EX_CONFIG), \
        "AC-19: unenforced = 지연 크래시(uncaught, startup 거부 아님) — got %d\n%s" % (rc, out)
    assert out.index(SENTINEL) >= 0 and "KeyError" in out, \
        "AC-19: 센티넬 이후 크래시(KeyError) = late-crash 형상\n%s" % out


def test_ac19_mutation_missing_masked_degrades_enforced():
    """MK: validator 의 missing 판정 삼킴(missing_masked) → enforced 가 unenforced 형상으로 퇴화.

    = 센티넬이 출력되고 business 에서 late-crash — AC-19 판별 케이스가 RED 로 뒤집힘 (계약 (2)
    exit-masking 금지가 load-bearing 임의 증명).
    """
    with tempfile.TemporaryDirectory() as tmp:
        libdir = make_mutant_lib(tmp, VALIDATOR_PY, VALIDATOR_MUTATIONS, "missing_masked")
        rc, out = run_py([ENFORCED], env=clean_env({"REFIMPL_LIB_DIR": libdir}))
        assert SENTINEL in out, \
            "AC-19 MK: missing_masked → 센티넬 출력(business 도달 = RED-flip)\n%s" % out
        assert rc not in (0, EX_CONFIG), \
            "AC-19 MK: late-crash(uncaught) 형상 — got %d\n%s" % (rc, out)


# ─────────────────────── standalone runner ──────────────────────────────────────

def _main():
    tests = [(n, f) for n, f in sorted(globals().items())
             if n.startswith("test_") and callable(f)]
    npass = 0
    nfail = 0
    print("=" * 75)
    print(" CFP-2700 G3: infra-startup-failclosed — discriminating self-test (.py)")
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
        print("OK All %d cases pass — AC-2/3/9/15/19 discriminating + mutation-kill" % npass)
        return 0
    print("X %d case(s) failed" % nfail)
    return 1


if __name__ == "__main__":
    sys.exit(_main())
