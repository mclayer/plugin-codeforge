#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
tests/scripts/test_infra-cross-repo-drift.py
CFP-2700 (Epic) G5 Phase 2 (구현 lane) — Discriminating self-test (.py channel) for the
  `--cross-repo` mode of scripts/lib/check_infra_resource_drift.py (ADR-157 §결정4 cross-repo 대조).

★ 보안 민감 슬라이스 (untrusted foreign-repo content ingest + read-WRITE PAT) — §7 위협모델 준수 1급.
  실 네트워크 금지 — fetch·Issue-발행을 **주입가능 seam**으로 stub:
    INFRA_CROSS_REPO_FETCH_ROOT = local mock-repo fixture(디렉터리 = 가짜 저장소 트리).
    INFRA_CROSS_REPO_ISSUE_SINK = transient fail-open 시 Issue 를 append 할 JSON sink 파일.
  mock 트리: <fetch_root>/<ns>/<ref>/<path>  (ref 를 경로에 반영 = ref-pin 시연) + sidecar `<path>.status`.

★ 3-way (AC-21):
  (a) 타저장소 미선언 참조 fixture → FAIL(non-zero, exit 1 content-mismatch).
  (b) 선언·전파 fixture → PASS(exit 0).
  (c) token 부재 → degraded-FAIL(non-zero, exit 3).

★ normative 2 (mutation-killable — ADR-157 §결정4 FIX-2):
  (t1) transient(503/timeout) → fail-open + WARN + Issue 발행 (Issue-발행 seam 미호출 mutant=RED).
       + MK issue_publish_off (발행 seam 무력화 → sink 비어 RED) + MK token_check_off (c 축).
  (t2) content-mismatch → transient 로 **분류 안 됨** (content-mismatch→transient 오분류 mutant=최중요 RED).
       + MK mismatch_as_transient (ok-branch drift→transient → exit 0+Issue, 최중요 kill).

★ 부가 계약:
  · vacuous (namespace 자원 0) → exit 0 (wrapper-self 정상, I-5 consumer 채택-bound).
  · ref-pin (moving HEAD `main` → hard-fail exit 1) + MK refpin_off (moving-HEAD 수용 → exit 0 RED).
  · ref-pin idempotent (동일 pinned ref 2-run → stdout byte-identical ∧ exit 동일).
  · 403/404 = resp.ok 후 fail-closed (transient 아님, exit 1) — spoof(namespace 형식) hard-fail.
  · secret-masking (§7.3): sentinel PAT 값이 stdout·Issue sink 어디에도 미출력 (load-bearing = 출력 캡처 확인).

standalone: `python3 tests/scripts/test_infra-cross-repo-drift.py` → 전 test_* 실행, exit 0=PASS / 1=FAIL.
  meta-gate(check-selftest-execution-liveness)는 tests/scripts/*.sh 만 glob — 동반 .sh 가 인벤토리 enroll,
  본 .py 는 workflow 의 .py step 으로 실행(ac-traceability Hop3 AST 스타일, 인벤토리 대상 아님).
"""

import json
import os
import subprocess
import sys
import tempfile

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SSOT_PY = os.path.join(REPO_ROOT, "scripts", "lib", "check_infra_resource_drift.py")

TOKEN_ENV = "CODEFORGE_CROSS_REPO_PAT"
FETCH_ROOT_ENV = "INFRA_CROSS_REPO_FETCH_ROOT"
ISSUE_SINK_ENV = "INFRA_CROSS_REPO_ISSUE_SINK"
# secret-masking 실증용 sentinel — 실 PAT 아님. 로그·Issue 어디에도 이 값이 새면 안 된다(§7.3).
SENTINEL_TOKEN = "ghp_SEKRETsentinelVALUE0123456789abcd"

NS = "acme/foreign-collector"
PINNED_REF = "v1.2.3"
FPATH = "src/config.txt"
CANON = "MCTRADER_RAW_NAS_URL"

# foreign content 대조군: 전파 O(canonical 참조) vs 미전파(구 키만 참조 = 원 MinIO 사고 재현).
FOREIGN_PROPAGATED = 'let url = std::env::var("MCTRADER_RAW_NAS_URL").unwrap();\n'
FOREIGN_MISMATCH = 'let url = std::env::var("OLD_MINIO_URL").unwrap();  // 미전파 = derived grep 0건\n'


def _manifest(ref=PINNED_REF, path=FPATH, ns=NS, canonical=CANON, namespaced=True):
    if not namespaced:
        return (
            "infra_resources:\n"
            "  resources:\n"
            "    - id: local-only\n"
            "      canonical_env: %s\n"
            "      aliases:\n"
            "        accepted: []\n" % canonical
        )
    return (
        "infra_resources:\n"
        "  resources:\n"
        "    - id: raw-nas\n"
        "      namespace: %s\n"
        "      canonical_env: %s\n"
        "      cross_repo_ref: %s\n"
        "      cross_repo_path: %s\n"
        "      aliases:\n"
        "        accepted: []\n" % (ns, canonical, ref, path)
    )


def _write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)


def make_repo(tmp, manifest):
    """cross-repo 모드는 repo-local scan 을 안 하므로 manifest carrier 만 있으면 된다."""
    _write(os.path.join(tmp, ".claude", "_overlay", "project.yaml"), manifest)


def make_mock_repo(fetch_root, ns=NS, ref=PINNED_REF, path=FPATH, content=None, status=None):
    """local mock-repo fixture(디렉터리 트리) — <fetch_root>/<ns>/<ref>/<path> (+ .status sidecar)."""
    base = os.path.join(fetch_root, *ns.split("/"), *ref.split("/"))
    target = os.path.join(base, *path.split("/"))
    os.makedirs(os.path.dirname(target), exist_ok=True)
    if content is not None:
        with open(target, "w", encoding="utf-8", newline="\n") as f:
            f.write(content)
    if status is not None:
        with open(target + ".status", "w", encoding="utf-8", newline="\n") as f:
            f.write(status)


def run_cross(scanner_py, repo_root, token=None, fetch_root=None, issue_sink=None, timeout=60):
    """cross-repo subprocess 실행 → (exit, out). 상속 seam/토큰 env 는 제거(hermetic)."""
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    for k in (TOKEN_ENV, FETCH_ROOT_ENV, ISSUE_SINK_ENV):
        env.pop(k, None)
    if token is not None:
        env[TOKEN_ENV] = token
    if fetch_root is not None:
        env[FETCH_ROOT_ENV] = fetch_root
    if issue_sink is not None:
        env[ISSUE_SINK_ENV] = issue_sink
    proc = subprocess.run(
        [sys.executable, scanner_py, "--repo-root", repo_root, "--cross-repo"],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env, timeout=timeout,
    )
    return proc.returncode, proc.stdout.decode("utf-8", "replace")


# 소스 문자열-치환 mutation (anchor → replacement). 미적용 시 AssertionError(anchor drift 검출).
MUTATIONS = {
    # t2 최중요: content-mismatch 를 transient 로 오분류 → fail-open(exit 0) + Issue 오발행.
    "mismatch_as_transient": (
        "                drift.append((rid, ns, canon, ref, path))",
        "                transient.append((rid, ns, canon))  # MUTANT-mismatch-as-transient",
    ),
    # t1: transient 시 Issue 발행 seam 무력화 → sink 비어 audit trail 소실.
    "issue_publish_off": (
        "            published = _publish_issue(issue_sink, title, body, token)",
        "            published = False  # MUTANT-issue-publish-off",
    ),
    # (c): token 부재 degraded 체크 무력화 → misconfig 가 조용히 통과.
    "token_check_off": (
        "    if not token:",
        "    if False:  # MUTANT-token-check-off",
    ),
    # ref-pin: moving HEAD 거부 무력화 → moving-target 수용(idempotency 파손, moving-red 유발 가능).
    "refpin_off": (
        "        if not ref or ref.lower() in _MOVING_REFS or \"..\" in ref or not _CROSS_REF_RE.match(ref):",
        "        if not ref:  # MUTANT-refpin-off",
    ),
    # non-SHA WARN emit 무력화 → non-SHA ref 인데 WARN 미방출 + nonsha_warn=0 (mutation-kill anchor).
    "nonsha_warn_off": (
        "        if not _SHA_REF_RE.match(ref):",
        "        if False:  # MUTANT-nonsha-warn-off",
    ),
}


def make_mutant(tmp, kind):
    old, new = MUTATIONS[kind]
    src = open(SSOT_PY, encoding="utf-8").read()
    mutated = src.replace(old, new, 1)
    assert mutated != src, "mutation did not apply — anchor drift (kind=%s)" % kind
    path = os.path.join(tmp, "mutant_%s.py" % kind)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(mutated)
    return path


# ─────────────────────── 3-way (AC-21) ──────────────────────────────────────────

def test_3way_a_content_mismatch_failclosed():
    with tempfile.TemporaryDirectory() as tmp:
        make_repo(tmp, _manifest())
        froot = os.path.join(tmp, "_mock")
        make_mock_repo(froot, content=FOREIGN_MISMATCH)
        rc, out = run_cross(SSOT_PY, tmp, token="tkn", fetch_root=froot)
        assert rc == 1, "(a) content-mismatch → fail-closed exit 1, got %d\n%s" % (rc, out)
        assert "CROSS-REPO DRIFT (content-mismatch)" in out, out
        assert "content_mismatch=1" in out, out


def test_3way_b_propagated_pass():
    with tempfile.TemporaryDirectory() as tmp:
        make_repo(tmp, _manifest())
        froot = os.path.join(tmp, "_mock")
        make_mock_repo(froot, content=FOREIGN_PROPAGATED)
        rc, out = run_cross(SSOT_PY, tmp, token="tkn", fetch_root=froot)
        assert rc == 0, "(b) 전파 fixture → PASS exit 0, got %d\n%s" % (rc, out)
        assert "CROSS-REPO OK" in out and "전파 확인" in out, out
        assert "propagated=1" in out, out


def test_3way_c_token_absent_degraded():
    with tempfile.TemporaryDirectory() as tmp:
        make_repo(tmp, _manifest())
        froot = os.path.join(tmp, "_mock")
        make_mock_repo(froot, content=FOREIGN_PROPAGATED)   # 전파 fixture 이나 token 부재가 앞선다
        rc, out = run_cross(SSOT_PY, tmp, token=None, fetch_root=froot)
        assert rc == 3, "(c) token 부재 → degraded-FAIL exit 3, got %d\n%s" % (rc, out)
        assert "CROSS-REPO DEGRADED-FAIL" in out, out


def test_3way_c_mutation_token_check_off():
    with tempfile.TemporaryDirectory() as tmp:
        make_repo(tmp, _manifest())
        froot = os.path.join(tmp, "_mock")
        make_mock_repo(froot, content=FOREIGN_PROPAGATED)
        mut = make_mutant(tmp, "token_check_off")
        rc, out = run_cross(mut, tmp, token=None, fetch_root=froot)
        # RED-flip: degraded 체크 무력화 → token 부재인데 대조 진행 = exit 0 (misconfig 조용히 통과).
        assert rc != 3, "(c) MK token_check_off → degraded 우회(exit 3 아님), got %d\n%s" % (rc, out)
        assert "DEGRADED-FAIL" not in out, out


# ─────────────────────── t1 transient fail-open + Issue ─────────────────────────

def test_t1_transient_failopen_issue_published():
    with tempfile.TemporaryDirectory() as tmp:
        make_repo(tmp, _manifest())
        froot = os.path.join(tmp, "_mock")
        make_mock_repo(froot, status="503")             # transient 위장 (sidecar)
        sink = os.path.join(tmp, "issues.jsonl")
        rc, out = run_cross(SSOT_PY, tmp, token="tkn", fetch_root=froot, issue_sink=sink)
        assert rc == 0, "(t1) transient → fail-open exit 0, got %d\n%s" % (rc, out)
        assert "CROSS-REPO TRANSIENT (fail-open)" in out and "transient_failopen=1" in out, out
        assert os.path.isfile(sink), "(t1) Issue sink 미생성 = 발행 안 됨\n%s" % out
        recs = [json.loads(l) for l in open(sink, encoding="utf-8") if l.strip()]
        assert len(recs) == 1, "(t1) Issue 1건 발행돼야 함, got %d" % len(recs)
        assert NS in recs[0]["body"] and "transient" in recs[0]["body"], recs[0]


def test_t1_mutation_issue_publish_off():
    with tempfile.TemporaryDirectory() as tmp:
        make_repo(tmp, _manifest())
        froot = os.path.join(tmp, "_mock")
        make_mock_repo(froot, status="timeout")
        sink = os.path.join(tmp, "issues.jsonl")
        mut = make_mutant(tmp, "issue_publish_off")
        rc, out = run_cross(mut, tmp, token="tkn", fetch_root=froot, issue_sink=sink)
        # RED-flip: 발행 seam 무력화 → transient 는 여전히 fail-open(exit 0)이나 audit trail(sink) 소실.
        published_records = []
        if os.path.isfile(sink):
            published_records = [l for l in open(sink, encoding="utf-8") if l.strip()]
        assert not published_records, "(t1) MK issue_publish_off → sink 비어야 kill 성립\n%s" % out


# ─────────────────────── t2 content-mismatch ≠ transient (최중요) ────────────────

def test_t2_mismatch_not_transient():
    with tempfile.TemporaryDirectory() as tmp:
        make_repo(tmp, _manifest())
        froot = os.path.join(tmp, "_mock")
        make_mock_repo(froot, content=FOREIGN_MISMATCH)
        sink = os.path.join(tmp, "issues.jsonl")
        rc, out = run_cross(SSOT_PY, tmp, token="tkn", fetch_root=froot, issue_sink=sink)
        # content-mismatch = fail-closed(exit 1), transient(exit 0 + Issue) 아님.
        assert rc == 1, "(t2) content-mismatch → exit 1(transient 아님), got %d\n%s" % (rc, out)
        assert "transient_failopen=0" in out, "(t2) transient 로 분류되면 안 됨\n%s" % out
        assert not os.path.isfile(sink) or not open(sink).read().strip(), \
            "(t2) content-mismatch 에 Issue 발행되면 오분류\n%s" % out


def test_t2_mutation_mismatch_as_transient():
    with tempfile.TemporaryDirectory() as tmp:
        make_repo(tmp, _manifest())
        froot = os.path.join(tmp, "_mock")
        make_mock_repo(froot, content=FOREIGN_MISMATCH)
        sink = os.path.join(tmp, "issues.jsonl")
        mut = make_mutant(tmp, "mismatch_as_transient")
        rc, out = run_cross(mut, tmp, token="tkn", fetch_root=froot, issue_sink=sink)
        # RED-flip(최중요): content-mismatch 를 transient 로 오분류 → verdict 가 fail-closed(exit 1)에서
        #   fail-open(exit 0)으로 뒤집히고 census 가 content_mismatch=1 대신 transient_failopen=1 로 계수.
        #   base(test_t2_mismatch_not_transient)는 exit 1 + content_mismatch=1 + transient_failopen=0.
        assert rc == 0, "(t2) MK mismatch_as_transient → 오분류로 fail-open(exit 0), got %d\n%s" % (rc, out)
        assert "transient_failopen=1" in out and "content_mismatch=0" in out, \
            "(t2) MK → content-mismatch 가 transient 로 계수돼야 kill 성립\n%s" % out


# ─────────────────────── ref-pin (idempotency + moving-HEAD 거부) ────────────────

def test_refpin_moving_head_hardfail():
    with tempfile.TemporaryDirectory() as tmp:
        make_repo(tmp, _manifest(ref="main"))            # moving HEAD = ref-pin 위반
        froot = os.path.join(tmp, "_mock")
        make_mock_repo(froot, ref="main", content=FOREIGN_PROPAGATED)
        rc, out = run_cross(SSOT_PY, tmp, token="tkn", fetch_root=froot)
        assert rc == 1, "ref-pin: moving HEAD → hard-fail exit 1, got %d\n%s" % (rc, out)
        assert "moving HEAD 금지" in out and "ref-pin" in out, out


def test_refpin_mutation_refpin_off():
    with tempfile.TemporaryDirectory() as tmp:
        make_repo(tmp, _manifest(ref="main"))
        froot = os.path.join(tmp, "_mock")
        make_mock_repo(froot, ref="main", content=FOREIGN_PROPAGATED)
        mut = make_mutant(tmp, "refpin_off")
        rc, out = run_cross(mut, tmp, token="tkn", fetch_root=froot)
        # RED-flip: moving-HEAD 거부 무력화 → main 수용 → 전파 대조 진행 = exit 0 (ref-pin 파손).
        assert rc == 0, "ref-pin MK refpin_off → moving HEAD 수용(exit 0), got %d\n%s" % (rc, out)


def test_refpin_idempotent():
    with tempfile.TemporaryDirectory() as tmp:
        make_repo(tmp, _manifest())
        froot = os.path.join(tmp, "_mock")
        make_mock_repo(froot, content=FOREIGN_PROPAGATED)
        rc1, out1 = run_cross(SSOT_PY, tmp, token="tkn", fetch_root=froot)
        rc2, out2 = run_cross(SSOT_PY, tmp, token="tkn", fetch_root=froot)
        assert rc1 == rc2 == 0, "ref-pin idempotent: 2-run 동일 exit 0, got %d/%d" % (rc1, rc2)
        assert out1 == out2, "ref-pin idempotent: pinned ref 2-run stdout byte-identical 아님"


# ─────────────────────── non-SHA ref = WARN (§결정8 (viii), F-CR-003) ─────────────

# 40-hex SHA (non-moving, _SHA_REF_RE 매치) — WARN 미방출 discrimination 축.
SHA_REF = "a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0"


def test_refpin_nonsha_warn():
    """non-SHA·non-moving ref(staging) → 수용(exit 0) + NON-SHA WARN + census nonsha_warn=1."""
    with tempfile.TemporaryDirectory() as tmp:
        make_repo(tmp, _manifest(ref="staging"))          # non-SHA, non-moving branch
        froot = os.path.join(tmp, "_mock")
        make_mock_repo(froot, ref="staging", content=FOREIGN_PROPAGATED)
        rc, out = run_cross(SSOT_PY, tmp, token="tkn", fetch_root=froot)
        assert rc == 0, "non-SHA ref(staging) → 수용(WARN) exit 0, got %d\n%s" % (rc, out)
        assert "CROSS-REPO NON-SHA REF" in out and "비-SHA ref" in out, out
        assert "nonsha_warn=1" in out, out
        assert "propagated=1" in out, "non-SHA 여도 대조는 진행돼 전파 확인\n%s" % out


def test_refpin_sha_no_warn():
    """40-hex SHA-pin ref → propagated PASS(exit 0) + WARN 미방출 (discrimination)."""
    with tempfile.TemporaryDirectory() as tmp:
        make_repo(tmp, _manifest(ref=SHA_REF))
        froot = os.path.join(tmp, "_mock")
        make_mock_repo(froot, ref=SHA_REF, content=FOREIGN_PROPAGATED)
        rc, out = run_cross(SSOT_PY, tmp, token="tkn", fetch_root=froot)
        assert rc == 0, "SHA-pin ref → PASS exit 0, got %d\n%s" % (rc, out)
        assert "propagated=1" in out, out
        assert "NON-SHA REF" not in out and "nonsha_warn=0" in out, \
            "SHA-pin 은 WARN 미방출이어야 함(discrimination)\n%s" % out


def test_refpin_mutation_nonsha_warn_off():
    """MK nonsha_warn_off: WARN emit 무력화 → non-SHA ref 인데 WARN 소실 + nonsha_warn=0 (RED-flip)."""
    with tempfile.TemporaryDirectory() as tmp:
        make_repo(tmp, _manifest(ref="staging"))
        froot = os.path.join(tmp, "_mock")
        make_mock_repo(froot, ref="staging", content=FOREIGN_PROPAGATED)
        mut = make_mutant(tmp, "nonsha_warn_off")
        rc, out = run_cross(mut, tmp, token="tkn", fetch_root=froot)
        assert "CROSS-REPO NON-SHA REF" not in out and "nonsha_warn=0" in out, \
            "(nonsha_warn_off) → WARN 소실 + nonsha_warn=0 이어야 kill 성립\n%s" % out


# ─────────────────────── 403/404 = fail-closed (transient 아님) ──────────────────

def test_404_hardfail_not_transient():
    with tempfile.TemporaryDirectory() as tmp:
        make_repo(tmp, _manifest())
        froot = os.path.join(tmp, "_mock")
        make_mock_repo(froot, status="not_found")        # 404
        sink = os.path.join(tmp, "issues.jsonl")
        rc, out = run_cross(SSOT_PY, tmp, token="tkn", fetch_root=froot, issue_sink=sink)
        assert rc == 1, "404 → fail-closed exit 1(transient 아님), got %d\n%s" % (rc, out)
        assert "404 not-found" in out and "hard_unavailable=1" in out, out
        assert "transient_failopen=0" in out, "404 를 transient 로 분류 금지\n%s" % out
        assert not os.path.isfile(sink) or not open(sink).read().strip(), \
            "404 에 Issue 발행되면 오분류(fail-open 오적용)\n%s" % out


def test_403_hardfail_not_transient():
    with tempfile.TemporaryDirectory() as tmp:
        make_repo(tmp, _manifest())
        froot = os.path.join(tmp, "_mock")
        make_mock_repo(froot, status="403")
        rc, out = run_cross(SSOT_PY, tmp, token="tkn", fetch_root=froot)
        assert rc == 1, "403 → fail-closed exit 1, got %d\n%s" % (rc, out)
        assert "403/401 forbidden" in out, out
        assert "transient_failopen=0" in out, out


def test_namespace_spoof_hardfail():
    with tempfile.TemporaryDirectory() as tmp:
        # namespace 가 owner/repo shape 아님(../evil = traversal) → _NS_RE anchored 첫 문자에서 hard-fail.
        #   (F-CR-002: dead allowlist 제거 후 실 차단은 _NS_RE shape/traversal — substring "namespace 형식 위반" 유지).
        make_repo(tmp, _manifest(ns="../evil"))
        froot = os.path.join(tmp, "_mock")
        make_mock_repo(froot, ns="../evil", content=FOREIGN_PROPAGATED)
        rc, out = run_cross(SSOT_PY, tmp, token="tkn", fetch_root=froot)
        assert rc == 1, "namespace spoof → hard-fail exit 1, got %d\n%s" % (rc, out)
        assert "namespace 형식 위반" in out, out


# ─────────────────────── vacuous (namespace 자원 0) ──────────────────────────────

def test_vacuous_pass():
    with tempfile.TemporaryDirectory() as tmp:
        make_repo(tmp, _manifest(namespaced=False))
        rc, out = run_cross(SSOT_PY, tmp, token="tkn")
        assert rc == 0, "vacuous(namespace 0) → PASS exit 0, got %d\n%s" % (rc, out)
        assert "CROSS-REPO PASS (vacuous)" in out, out


# ─────────────────────── secret-masking (§7.3) ──────────────────────────────────

def test_secret_masking_no_pat_leak():
    """sentinel PAT 값이 stdout·Issue sink 어디에도 미출력 (§7.3 self-redaction 실증).

    load-bearing = 출력 캡처가 실제로 동작함을 별도 토큰("CROSS-REPO")으로 확인 (빈 출력 false-pass 방지).
    """
    with tempfile.TemporaryDirectory() as tmp:
        make_repo(tmp, _manifest())
        froot = os.path.join(tmp, "_mock")
        make_mock_repo(froot, status="503")             # transient → Issue sink 경유
        sink = os.path.join(tmp, "issues.jsonl")
        rc, out = run_cross(SSOT_PY, tmp, token=SENTINEL_TOKEN, fetch_root=froot, issue_sink=sink)
        assert rc == 0, "secret-masking case 는 transient fail-open(exit 0), got %d\n%s" % (rc, out)
        assert "CROSS-REPO" in out, "출력 캡처 load-bearing 확인 실패 (빈 출력이면 masking 단정 무의미)"
        assert SENTINEL_TOKEN not in out, "§7.3: PAT 값이 stdout 에 누출\n%s" % out
        sink_text = open(sink, encoding="utf-8").read() if os.path.isfile(sink) else ""
        assert SENTINEL_TOKEN not in sink_text, "§7.3: PAT 값이 Issue sink 에 누출\n%s" % sink_text
        # drift/mismatch 경로도 (content-mismatch fixture) 토큰 미출력 재확인.
        make_mock_repo(froot, status=None, content=FOREIGN_MISMATCH)
        rc2, out2 = run_cross(SSOT_PY, tmp, token=SENTINEL_TOKEN, fetch_root=froot)
        assert SENTINEL_TOKEN not in out2, "§7.3: drift 경로 stdout PAT 누출\n%s" % out2


# ─────────────────────── redact 새 form (§7.3 보강 — fine-grained PAT / Bearer) ───

def _load_ssot_module():
    """SSOT 모듈을 직접 import — `_redact` 를 unit 수준으로 구동(subprocess 경로는 값 미출력이라 무구동)."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("check_infra_resource_drift", SSOT_PY)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_redact_new_forms_masked():
    """fine-grained PAT(github_pat_…) + Authorization: Bearer <t> + classic + userpass = 값 미출력(§7.3)."""
    mod = _load_ssot_module()
    fg_pat = "github_pat_11ABCDEFG0abcdefghij1234567890"
    bearer_secret = "s3cr3tBearerTokenValue0123456789xyz"
    classic = SENTINEL_TOKEN
    userpass_secret = "p4ssw0rdInUserInfo123"
    samples = {
        "fine-grained": ("config token=%s trailing" % fg_pat, fg_pat),
        "bearer": ("Authorization: Bearer %s" % bearer_secret, bearer_secret),
        "classic": ("using %s here" % classic, classic),
        "userpass": ("https://user:%s@host/x" % userpass_secret, userpass_secret),
    }
    for name, (raw, secret) in samples.items():
        red = mod._redact(raw)
        assert secret not in red, "redact(%s): 값 누출 → %r" % (name, red)
    # over-redaction 회귀 방지 — 비-secret hex digest(키워드 아님)는 보존.
    benign = "digest=" + "a" * 64
    assert ("a" * 64) in mod._redact(benign), "정상 hex digest 과도 redact: %r" % mod._redact(benign)


# ─────────────────────── standalone runner ──────────────────────────────────────

def _run_all():
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    passed = failed = 0
    print("=" * 79)
    print(" CFP-2700 G5: infra cross-repo drift — discriminating self-test (.py)")
    print("=" * 79)
    for fn in fns:
        try:
            fn()
            print("OK PASS: %s" % fn.__name__)
            passed += 1
        except AssertionError as e:
            print("X FAIL: %s\n  %s" % (fn.__name__, e))
            failed += 1
        except Exception as e:  # noqa: BLE001 — self-test runner 는 모든 예외를 FAIL 로 집계
            print("X ERROR: %s\n  %r" % (fn.__name__, e))
            failed += 1
    print("-" * 79)
    print("PASS: %d  FAIL: %d" % (passed, failed))
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(_run_all())
