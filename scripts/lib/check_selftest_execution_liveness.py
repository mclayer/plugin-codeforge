#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
scripts/lib/check_selftest_execution_liveness.py
CFP-2622 (Epic CFP-2602 G6) / ADR-151 — self-test execution-liveness 인벤토리 메타-게이트 pure core.

wrapper-self 의 `tests/scripts/*.sh` self-test corpus 를 "선언(declared L3 fixture)"에서
"실제 CI 실행(channel alive)"으로 승격하는 forcing-function. 각 self-test 가 인벤토리에 레코드로
enroll 됐는지(silent-un-run root 차단) + 그 실행 채널이 실재·alive·형식 presence 를 갖추는지를
**정적 lint** 로 fail-closed 강제한다. 신규 동적 러너 부활 아님(ADR-048 무충돌) — Ports&Adapters
정적 검사(배선 presence). `scripts/lib/check_ac_traceability_matrix.py` house style 답습
(offline-first / read-only / argparse / pathlib / PyYAML).

━━ 정직 천장 (ADR-151 §결정7 — presence/alive/형식 까지만 fail-closed) ━━
  본 메타-게이트는 다음 까지만 강제한다: self-test CI 배선 presence / 채널 alive / discriminating
  fixture 형식 enum / L2 both-copies presence / manual_reason substantive. **강제 안 함(정직 공개)**:
  (i) discriminating 검출력(fixture 가 실제 mutation 을 죽이는가) = G3 소관(AC-4 미강제)
  (ii) 열거 완결성(feasible self-test 최대 배선) = review-tier(AC-1b)
  (iii) L1 blocking 승격 = ADR-060 evidence-gate(AC-6). "wrapper 동적검증 완전 봉인" hard-claim 금지.

━━ SCOPE disjoint (ADR-151 §결과 경계) ━━
  ⊥ G3(검출력 실증) / ⊥ ADR-147(러너 인프라 — 배선된 job 이 실 러너 배정받는가) /
  ⊥ consumer 동적(G2 soak / G5 DAST / G4 burden-flip). G6 = wrapper-self self-test 실행-liveness 축.

offline (네트워크 0 — 입력 전부 로컬 파일). read-only (verifier — write 0).
표준 라이브러리(argparse/re/glob/pathlib) + PyYAML(yaml) 만.

Usage:
  python3 check_selftest_execution_liveness.py [--repo-root DIR] [--inventory FILE]

Exit codes (fail-closed):
  0 = 전 fail-closed AC 통과 (유일 success).
  1 = ≥1 fail-closed 위반 (각 위반을 stderr 에 AC-id prefix + 1행 출력).
  2 = usage/parse 오류 (argparse) 전용 — 그 외 없음.

ADR refs: ADR-151 (결정 SSOT — §결정2 스키마 / §결정3 AC / §결정9 재귀 AC-9) /
  ADR-136 결정14 (execution-liveness 3요건 L1/L2/L3, 핵심 렌즈 무수정) /
  ADR-061 §결정 1 (Python entry-point + thin bash wrapper) / ADR-119 (게이트=ground-truth).
"""

import argparse
import glob
import os
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # PyYAML 부재 = 판정불가 = fail-closed
    print(
        "::error::check-selftest-execution-liveness: PyYAML(import yaml) 부재 — "
        "판정불가(fail-closed). CI 는 `pip install pyyaml`, 로컬은 pip 설치 필요.",
        file=sys.stderr,
    )
    sys.exit(1)

# 출력 인코딩 robust 화 (Windows cp949 등 비-UTF-8 locale 에서 한글·em-dash print 차단).
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
    except Exception:
        pass

EXIT_PASS = 0  # 전 fail-closed AC 통과
EXIT_FAIL = 1  # ≥1 위반 OR 판정불가 (fail-closed)
# EXIT 2 = argparse usage 전용 (parser.error 가 자동 반환).

# ── 스키마 (ADR-151 §결정2 — 8-field 레코드) ──────────────────────────────────
REQUIRED_FIELDS = (
    "self_test",
    "execution_channel",
    "channel_status",
    "blocking_tier",
    "discriminating_fixture",
    "l2_full_scope",
    "manual_reason",
    "g_boundary_check",
)
CHANNEL_STATUS_ENUM = {"alive", "dead", "permanently_skipped"}
BLOCKING_TIER_ENUM = {"required", "non_required", "warning_tier", "manual"}
DISCRIMINATING_ENUM = {"present", "smoke_only", "N/A"}
L2_ENUM = {"both_copies", "single", "N/A"}
MANUAL_CHANNELS = {"agent_runtime", "manual_registered"}
WORKFLOW_PREFIX = "workflow:"
INLINE_PREFIX = "inline_self_test_flag:"

MANUAL_REASON_MIN = 30  # §8.5.0 동형 재사용 (≥30자 substantive)

# 재귀 자기적용 대상 (ADR-151 §결정9 / AC-9) — 메타-게이트 자신의 self-test.
META_SELF_TEST = "tests/scripts/test_check-selftest-execution-liveness.sh"

# 테스트 파일명 → subject 스크립트명 (inline_self_test_flag AC-2 용): 선두 test_/test- 제거.
_LEADING_TEST_RE = re.compile(r"^test[_-]")


def _error(ac_id, msg):
    """위반 1건을 stderr 에 AC-id prefix + 1행 출력 (fail-closed 계약)."""
    print(f"::error::[{ac_id}] {msg}", file=sys.stderr)


def _subject_script(self_test_basename):
    """self-test basename(test_x.sh / test-x.sh) → 검사대상 스크립트 basename(x.sh)."""
    return _LEADING_TEST_RE.sub("", self_test_basename)


def _is_substantive(reason):
    """manual_reason substantive 판정 — 공백 제거 ≥30자 ∧ 단일문자 반복 아님."""
    if not isinstance(reason, str):
        return False
    non_ws = re.sub(r"\s", "", reason)
    if len(non_ws) < MANUAL_REASON_MIN:
        return False
    if len(set(non_ws)) <= 1:  # 단일 문자 반복 (예: 'aaaa...')
        return False
    return True


# ── workflow 인덱스 (adapter — 로컬 파일 I/O) ─────────────────────────────────
def _load_workflow_index(repo_root):
    """.github/workflows + templates/github-workflows 의 *.yml/*.yaml 를 basename → [path] 로 인덱싱.

    같은 basename 이 양 dir 에 존재하면 (parity pair) 두 경로 모두 수집한다.
    """
    index = {}
    for sub in (".github/workflows", "templates/github-workflows"):
        d = repo_root / sub
        if not d.is_dir():
            continue
        for pattern in ("*.yml", "*.yaml"):
            for p in sorted(d.glob(pattern)):
                index.setdefault(p.name, []).append(p)
    return index


def _parse_jobs(path):
    """workflow 파일을 파싱해 jobs dict(jid → job body) 반환. 파싱 실패 시 None."""
    try:
        with open(path, encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
    except (OSError, yaml.YAMLError, ValueError):
        return None
    if not isinstance(data, dict):
        return None
    jobs = data.get("jobs")
    if not isinstance(jobs, dict):
        return {}
    return jobs


def _job_run_texts(job_body):
    """job body 의 steps[].run 문자열 목록 반환 (AC-2 run-line 스캔용)."""
    runs = []
    if not isinstance(job_body, dict):
        return runs
    for step in job_body.get("steps") or []:
        if isinstance(step, dict):
            run = step.get("run")
            if isinstance(run, str):
                runs.append(run)
    return runs


def _job_permanently_skipped(job_body):
    """job 이 영구 skip(if: false 리터럴) 또는 steps 부재(born-invalid)인지 판정."""
    if not isinstance(job_body, dict):
        return True  # 형태 불명 = 실행 불가 취급
    if_val = job_body.get("if")
    if if_val is False:
        return True
    if isinstance(if_val, str) and if_val.strip().lower() == "false":
        return True
    steps = job_body.get("steps")
    if not steps:  # None / [] = 실행 step 부재
        return True
    return False


def _find_job_across_copies(wf_index, wf_file, job_id):
    """basename wf_file 의 양 copy 중 job_id 를 가진 (path, job_body) 목록 반환."""
    hits = []
    for path in wf_index.get(wf_file, []):
        jobs = _parse_jobs(path)
        if jobs is None:
            continue
        if job_id in jobs:
            hits.append((path, jobs[job_id]))
    return hits


# ── 채널별 AC-2 / AC-3 검사 ───────────────────────────────────────────────────
def _check_workflow_channel(violations, rec, self_test_base, wf_file, job_id, wf_index):
    """workflow:F:J 채널 — AC-2(배선 실재) + AC-3(alive→job 실행가능) 검사."""
    if wf_file not in wf_index:
        _error("AC-2", f"{rec['self_test']}: execution_channel workflow '{wf_file}' 파일 부재 "
                        f"(.github/workflows·templates/github-workflows 어디에도 없음).")
        violations.append(1)
        return
    job_hits = _find_job_across_copies(wf_index, wf_file, job_id)
    if not job_hits:
        _error("AC-2", f"{rec['self_test']}: workflow '{wf_file}' 에 job '{job_id}' 부재.")
        violations.append(1)
        return
    # self_test basename 이 job J 의 run: line 중 하나에 등장해야 함.
    wired = any(
        any(self_test_base in run for run in _job_run_texts(job_body))
        for _path, job_body in job_hits
    )
    if not wired:
        _error("AC-2", f"{rec['self_test']}: '{self_test_base}' 가 {wf_file}:{job_id} 의 어느 "
                       f"run: line 에도 등장하지 않음 (배선 부재 = silent-un-run).")
        violations.append(1)
    # AC-3 — channel_status alive 인데 job 이 영구 skip 이면 FAIL.
    if rec["channel_status"] == "alive":
        if all(_job_permanently_skipped(job_body) for _path, job_body in job_hits):
            _error("AC-3", f"{rec['self_test']}: channel_status alive 이나 {wf_file}:{job_id} 가 "
                           f"영구 skip(if:false) 또는 steps 부재 = hollow 채널.")
            violations.append(1)


def _check_inline_channel(violations, rec, self_test_base, wf_file, job_id, wf_index):
    """inline_self_test_flag:F:J 채널 — subject 스크립트가 `--self-test` run: line 에 등장 검사(AC-2)."""
    if wf_file not in wf_index:
        _error("AC-2", f"{rec['self_test']}: inline channel workflow '{wf_file}' 파일 부재.")
        violations.append(1)
        return
    job_hits = _find_job_across_copies(wf_index, wf_file, job_id)
    if not job_hits:
        _error("AC-2", f"{rec['self_test']}: inline workflow '{wf_file}' 에 job '{job_id}' 부재.")
        violations.append(1)
        return
    subject = _subject_script(self_test_base)  # test_x.sh → x.sh (검사대상 스크립트)
    wired = any(
        any(subject in run and "--self-test" in run for run in _job_run_texts(job_body))
        for _path, job_body in job_hits
    )
    if not wired:
        _error("AC-2", f"{rec['self_test']}: inline subject '{subject}' + '--self-test' 가 "
                       f"{wf_file}:{job_id} 의 어느 run: line 에도 함께 등장하지 않음.")
        violations.append(1)


def _parse_channel(channel):
    """execution_channel 문자열 파싱 → (kind, wf_file, job_id).

    kind ∈ {'workflow','inline','agent_runtime','manual_registered','__bad__'}.
    """
    if channel == "agent_runtime":
        return ("agent_runtime", None, None)
    if channel == "manual_registered":
        return ("manual_registered", None, None)
    for prefix, kind in ((WORKFLOW_PREFIX, "workflow"), (INLINE_PREFIX, "inline")):
        if channel.startswith(prefix):
            rest = channel[len(prefix):]
            parts = rest.split(":")
            if len(parts) != 2 or not parts[0] or not parts[1]:
                return ("__bad__", None, None)
            return (kind, parts[0], parts[1])
    return ("__bad__", None, None)


# ── 레코드별 검사 (스키마 + enum + 채널 + AC-5 + AC-8) ────────────────────────
def _check_record(violations, rec, wf_index):
    """1 레코드 스키마/enum/채널/AC-5/AC-8 검사. self_test 는 상위(AC-1a)에서 파일존재 대조."""
    # 스키마 — 필수 8-field presence.
    st = rec.get("self_test", "<no self_test>")
    missing = [f for f in REQUIRED_FIELDS if f not in rec]
    if missing:
        _error("SCHEMA", f"{st}: 필수 필드 누락 {missing}.")
        violations.append(1)
        return  # 필드 부재 시 이후 검사 무의미

    # enum 검증.
    if rec["channel_status"] not in CHANNEL_STATUS_ENUM:
        _error("SCHEMA", f"{st}: channel_status enum 위반 '{rec['channel_status']}'.")
        violations.append(1)
    if rec["blocking_tier"] not in BLOCKING_TIER_ENUM:
        _error("SCHEMA", f"{st}: blocking_tier enum 위반 '{rec['blocking_tier']}'.")
        violations.append(1)
    if rec["discriminating_fixture"] not in DISCRIMINATING_ENUM:
        _error("SCHEMA", f"{st}: discriminating_fixture enum 위반 '{rec['discriminating_fixture']}'.")
        violations.append(1)
    if rec["l2_full_scope"] not in L2_ENUM:
        _error("SCHEMA", f"{st}: l2_full_scope enum 위반 '{rec['l2_full_scope']}'.")
        violations.append(1)

    # AC-8 — g_boundary_check 비-빈 문자열.
    gbc = rec["g_boundary_check"]
    if not isinstance(gbc, str) or not gbc.strip():
        _error("AC-8", f"{st}: g_boundary_check 비어있음/누락 — runtime 축 경계 확인 강제.")
        violations.append(1)

    # AC-3 — channel_status dead 는 항상 FAIL(채널 부재 = silent-un-run).
    if rec["channel_status"] == "dead":
        _error("AC-3", f"{st}: channel_status dead — 죽은 채널(silent-un-run), fail-closed.")
        violations.append(1)

    self_test_base = os.path.basename(st)
    kind, wf_file, job_id = _parse_channel(rec["execution_channel"])

    # AC-2 / AC-3 — 채널별.
    if kind == "__bad__":
        _error("SCHEMA", f"{st}: execution_channel 형식 위반 '{rec['execution_channel']}' "
                         f"(workflow:F:J | inline_self_test_flag:F:J | agent_runtime | manual_registered).")
        violations.append(1)
    elif kind == "workflow":
        # permanently_skipped 를 workflow 채널에 선언 = FAIL (AC-3).
        if rec["channel_status"] == "permanently_skipped":
            _error("AC-3", f"{st}: workflow 채널에 channel_status permanently_skipped = FAIL.")
            violations.append(1)
        _check_workflow_channel(violations, rec, self_test_base, wf_file, job_id, wf_index)
    elif kind == "inline":
        _check_inline_channel(violations, rec, self_test_base, wf_file, job_id, wf_index)
    elif kind in MANUAL_CHANNELS:
        # AC-2 — agent_runtime / manual_registered 는 manual_reason ≥30자 substantive 필수.
        if not _is_substantive(rec["manual_reason"]):
            _error("AC-2", f"{st}: {kind} 채널이나 manual_reason 이 substantive(≥30자, 비-반복) 미충족.")
            violations.append(1)

    # AC-5 — l2_full_scope.
    l2 = rec["l2_full_scope"]
    if l2 == "single":
        _error("AC-5", f"{st}: l2_full_scope single — 실행이 full scope 를 커버 못 함(부분), fail-closed.")
        violations.append(1)
    elif l2 == "both_copies":
        # parity target = 채널 workflow basename 이 양 dir 에 모두 존재해야 함.
        if kind not in ("workflow", "inline") or wf_file is None:
            _error("AC-5", f"{st}: l2_full_scope both_copies 이나 workflow 채널 아님 "
                           f"(parity target 도출 불가).")
            violations.append(1)
        else:
            # parity target = 채널 workflow basename 이 .github/workflows ∧ templates/github-workflows
            # 양 dir 에 모두 존재하는지 (byte-identical parity pair presence). 경로 부모명으로 판별.
            paths = wf_index.get(wf_file, [])
            has_github = any(
                p.parent.name == "workflows" and p.parent.parent.name == ".github" for p in paths
            )
            has_tmpl = any(
                p.parent.name == "github-workflows" and p.parent.parent.name == "templates"
                for p in paths
            )
            if not (has_github and has_tmpl):
                _error("AC-5", f"{st}: l2_full_scope both_copies 이나 '{wf_file}' 가 "
                               f".github/workflows ∧ templates/github-workflows 양쪽에 존재하지 않음.")
                violations.append(1)


# ── AC-1a / AC-9 (corpus 대조) ────────────────────────────────────────────────
def _check_corpus(violations, records, repo_root):
    """AC-1a — tests/scripts/*.sh ↔ 인벤토리 레코드 1:1 bijection. AC-9 — 메타-게이트 자기 레코드 alive."""
    tests_dir = repo_root / "tests" / "scripts"
    disk = set()
    if tests_dir.is_dir():
        for p in sorted(tests_dir.glob("*.sh")):
            disk.add(f"tests/scripts/{p.name}")
    else:
        _error("AC-1a", f"tests/scripts 디렉터리 부재({tests_dir}) — corpus 대조 판정불가.")
        violations.append(1)

    # 레코드 self_test 정규화(경로 slash 통일) + 중복 검출.
    rec_paths = {}
    for rec in records:
        st = rec.get("self_test")
        if not isinstance(st, str):
            continue
        st_norm = st.replace("\\", "/")
        rec_paths.setdefault(st_norm, 0)
        rec_paths[st_norm] += 1

    # 중복 레코드 (같은 self_test 2+).
    for st_norm, cnt in sorted(rec_paths.items()):
        if cnt > 1:
            _error("AC-1a", f"{st_norm}: 인벤토리에 레코드 {cnt}개 — self-test 당 정확히 1 레코드 위반.")
            violations.append(1)

    # 레코드 → 파일 부재.
    for st_norm in sorted(rec_paths):
        if st_norm not in disk:
            _error("AC-1a", f"{st_norm}: 레코드 존재하나 tests/scripts 실파일 부재 (record→missing file).")
            violations.append(1)

    # 파일 → 레코드 부재.
    for f in sorted(disk):
        if f not in rec_paths:
            _error("AC-1a", f"{f}: tests/scripts 실파일 존재하나 인벤토리 레코드 부재 "
                           f"(missing file→record = silent-un-run root).")
            violations.append(1)

    # AC-9 — 메타-게이트 자기 self-test 레코드 존재 ∧ channel_status alive (self-exclude 금지).
    meta_rec = next((r for r in records
                     if isinstance(r.get("self_test"), str)
                     and r["self_test"].replace("\\", "/") == META_SELF_TEST), None)
    if meta_rec is None:
        _error("AC-9", f"{META_SELF_TEST}: 메타-게이트 자기 self-test 레코드 부재 "
                       f"(재귀 self-exclude 금지 — meta-hollow-gate 차단).")
        violations.append(1)
    elif meta_rec.get("channel_status") != "alive":
        _error("AC-9", f"{META_SELF_TEST}: 메타-게이트 자기 레코드 channel_status "
                       f"'{meta_rec.get('channel_status')}' ≠ alive.")
        violations.append(1)


# ── 오케스트레이션 ────────────────────────────────────────────────────────────
def run(repo_root, inventory_path=None):
    repo_root = Path(repo_root).resolve()
    inv = Path(inventory_path).resolve() if inventory_path else \
        repo_root / "docs" / "selftest-execution-liveness-inventory.yaml"

    if not inv.is_file():
        _error("AC-1a", f"인벤토리 파일 부재: {inv} (판정불가, fail-closed).")
        return EXIT_FAIL
    try:
        with open(inv, encoding="utf-8") as fh:
            doc = yaml.safe_load(fh)
    except (OSError, yaml.YAMLError, ValueError) as e:
        _error("SCHEMA", f"인벤토리 YAML 파싱 실패: {inv} ({e}).")
        return EXIT_FAIL

    if not isinstance(doc, dict) or not isinstance(doc.get("self_tests"), list):
        _error("SCHEMA", f"인벤토리 최상위 key 'self_tests' (list) 부재/형식 오류: {inv}.")
        return EXIT_FAIL

    records = doc["self_tests"]
    wf_index = _load_workflow_index(repo_root)

    violations = []
    for rec in records:
        if not isinstance(rec, dict):
            _error("SCHEMA", f"레코드가 mapping 이 아님: {rec!r}.")
            violations.append(1)
            continue
        _check_record(violations, rec, wf_index)

    _check_corpus(violations, [r for r in records if isinstance(r, dict)], repo_root)

    if violations:
        _error("SUMMARY", f"self-test execution-liveness 메타-게이트 FAIL — 위반 {len(violations)}건 "
                          f"(fail-closed, exit 1). 정직 천장: presence/alive/형식 까지만 강제 "
                          f"(검출력=G3·열거완결성=review·L1승격=ADR-060 미강제, ADR-151 §결정7).")
        return EXIT_FAIL

    print(f"✓ check-selftest-execution-liveness: {len(records)} 레코드 전 fail-closed AC "
          f"(AC-1a/2/3/5/8/9 + SCHEMA) 통과. presence/alive/형식 천장 — 검출력=G3 미강제.")
    return EXIT_PASS


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=(
            "self-test execution-liveness 인벤토리 메타-게이트 (정적 lint, fail-closed AC-1a/2/3/5/8/9). "
            "tests/scripts/*.sh 전수 enroll + 실행 채널 alive/형식 presence 강제. "
            "presence/alive/형식 까지만 — 검출력=G3 미강제(ADR-151 §결정7)."
        )
    )
    default_root = Path(__file__).resolve().parents[2]  # scripts/lib → scripts → repo-root
    parser.add_argument(
        "--repo-root", default=str(default_root),
        help="repo 루트 (기본 = __file__ parents[2]). 인벤토리·tests/scripts·workflow dir 도출 기준.",
    )
    parser.add_argument(
        "--inventory", default=None,
        help="인벤토리 경로 override (기본 = <repo-root>/docs/selftest-execution-liveness-inventory.yaml).",
    )
    args = parser.parse_args(argv)
    return run(repo_root=args.repo_root, inventory_path=args.inventory)


if __name__ == "__main__":
    sys.exit(main())
