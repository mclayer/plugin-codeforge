#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""tests/scripts/test_zero_dangling_deploy_ref.py

CFP-2782 AC-3 — deploy·deploy-review 2 lane 물리 제거의 **결정론적 완전성 SSOT**
(Story §5.3 AC-3 / Change Plan §8.1 — normative, Phase 2 승격).

제거 완료 후 non-frozen·non-fixture·non-KEEP 경로에서 deploy-machinery token 집합의
grep 결과가 **0** 이어야 한다. token 집합 = §4.1(a) delete-set 과 bijection —
삭제 항목마다 최소 1 token 이 대응(부분 하드리스트 금지, iter3 SSOT 완전화).

matcher = **hyphen+underscore 양형 강제**(§5.3 (ii) "token regex 가 `-`형과 `_`형 둘 다
매칭 = variant-gap 0"). 리터럴 substring 만으로는 `deploy_blue_green.py`(underscore)와
`deploy-blue-green.sh`(hyphen) 중 한 형만 잡혀 bijection 에 실 구멍이 남는다 → 토큰 내
구분자 `-`/`_` 를 `[-_]` 등가로 컴파일해 양형을 봉인.

exclusion = frozen(archive/** · CHANGELOG · walk-entries · change-plans · retros …)
+ fixture(scripts/test-fixtures/** · `_FAKE_` file-level allowlist) + KEEP-set(§5.5-1
RELOCATE: production-cutover-evidence machinery + relocated ProductionEvidenceDeputyAgent
+ production-cutover 도메인). delete-set 도 exclusion(사전-상태 run 이 사후-상태를 모델링).

자기참조(hollow-gate 회피): 본 스캐너 파일 + sibling walk_plan regression-guard 는 token
vocabulary·삭제 plugin 명을 **명명하는 것이 임무**이므로 `_FAKE_` file-level allowlist 로
제외(test_sweep_executor.py `_FAKE_LIVE_7` 선례 동형). 이는 dangling ref 가 아니라 검출
어휘 자체다 — allowlist 정직성은 `test_allowlist_entries_are_real_tracked_files` 가 fence.

file enumeration = `git ls-files`(tracked only — 미tracked `c2-baseline/`·scratchpad 제외,
CI ubuntu ground-truth). git 부재 시 os.walk fallback(Windows/CI 포터빌리티).
"""
import os
import re
import subprocess
from pathlib import Path

import pytest

# tests/scripts/ → tests/ → repo root
REPO_ROOT = Path(__file__).resolve().parents[2]
_SELF_REL = os.path.relpath(os.path.abspath(__file__), str(REPO_ROOT)).replace(os.sep, "/")

# ─────────────────────── hard-0 token set (delete-set ↔ bijection) ───────────
# (unambiguous deploy-identity; ADR-087/088 는 archive frozen → review-tier, 여기 아님)
TOKENS = [
    # (iii) core plugin/agent/contract identity
    "codeforge-deploy",            # covers codeforge-deploy AND codeforge-deploy-review
    "DeployPLAgent", "DeployWorkerAgent", "DeployReviewPLAgent", "DeployReviewWorkerAgent",
    "deploy-output", "deploy-review-output",
    "phase:배포", "gate:deploy-pass", "gate:deploy-review-pass",
    "plugin:codeforge-deploy",
    # (i) workflow basenames (8 delete + check-canary-compatibility;
    #     production-cutover-evidence = §5.5-1 RELOCATE KEEP → 토큰 아님)
    "auto-deploy", "canary-auto-promote", "canary-promotion-criteria",
    "deploy-lane-presence", "deploy-lane-spawn-evidence", "deploy-review-lane-spawn-evidence",
    "deployment-schema-check", "rollback-signal-monitor", "check-canary-compatibility",
    # (ii) script body basenames (양형 matcher 가 hyphen/underscore 양쪽 커버)
    "deploy_blue_green", "canary_auto_promote", "auto_rollback_hook",
    "check_rollback_signal", "canary-compatibility-helpers",
    # Korean lane-identity (precision-scoped: lane-identity 구문만, generic deployment 어휘 제외)
    "배포 레인", "배포·배포리뷰", "배포리뷰", "배포 리뷰", "배포-리뷰", "배포 lane",
]


def _compile_token(tok):
    """§5.3 양형: 토큰 내 구분자 '-'/'_' 를 `[-_]` 등가로, 나머지 문자는 리터럴로 컴파일.

    variant-gap 0 — `deploy_blue_green` 토큰이 `deploy_blue_green.py`(underscore)와
    `deploy-blue-green.sh`(hyphen) 둘 다 매칭. `deploy-output` 토큰이 MANIFEST 의
    `deploy_output` 키(underscore)도 매칭. `codeforge-deploy` 는 `codeforge-develop`
    (deploy≠develop, 4번째 char p≠v)에 오매칭하지 않음(자연 방어).
    """
    pat = "".join("[-_]" if ch in "-_" else re.escape(ch) for ch in tok)
    return re.compile(pat)


COMPILED_TOKENS = [(tok, _compile_token(tok)) for tok in TOKENS]

# scanned extensions (텍스트 자산만 — 바이너리·이미지 제외)
SCANNED_EXT = (".md", ".yaml", ".yml", ".tsv", ".py", ".sh", ".json", ".txt")

# ─────────────────────── exclusion: frozen / fixture / KEEP-set ──────────────
EXCL_PREFIX = (
    "archive/", "c2-baseline/",
    "docs/walk-entries/",          # frozen event-sourcing records
    "docs/change-plans/",          # frozen completed change-plans (historical)
    "docs/cross-repo-patches/",    # frozen patch snapshots (historical)
    "docs/retros/",                # frozen retrospectives
    "scripts/test-fixtures/",      # fixtures
)
# KEEP-set (§5.5-1 RELOCATE): production-cutover machinery + relocated agent + domain
EXCL_EXACT = {
    ".github/workflows/production-cutover-evidence.yml",
    "templates/github-workflows/production-cutover-evidence.yml",
    "scripts/check-production-cutover-evidence.sh",
    "scripts/parse-production-cutover-frontmatter.py",
    "plugins/codeforge-design/agents/ProductionEvidenceDeputyAgent.md",  # relocated (design-owned)
}
EXCL_KEEP_PREFIX = ("docs/domain-knowledge/domain/production-cutover/",)
# _FAKE_ / token-vocabulary file-level allowlist (Story §5.3 — dangling 아님, 검출 어휘)
EXCL_FAKE = {
    "tests/scripts/test_sweep_executor.py",               # 기존 _FAKE_LIVE_7 선례
    _SELF_REL,                                            # 본 스캐너 자신 (전체 token vocabulary)
    "tests/scripts/test_walk_plan_topological_order.py",  # AC-6b regression guard (삭제 plugin 명 negative-assert)
}

# ── CFP-2782 finalized frozen/substrate/registry file-level exclusions (DevPL 확정 —
#    각 frozen-class 를 QADev firsthand 검증 후 등재; active surface 는 이미 clean,
#    residual token 은 아래 class(backward-compat substrate / archived·sunsetted·append-only
#    doc / active-removed 후 append-only changelog 잔여)뿐 — dangling 아님, §8.5 honest-ceiling) ──
EXCL_CFP2782 = {
    # (a) CFP-2689 A/B dev-process-event substrate — P1 zero-edit 계약. 배포/배포-리뷰 = backward-compat
    #     historical lane label 존치(dev-process-event-v1.md §2 lane_label = 11값; spawn-event 9값과 별개 축).
    "scripts/lib/append_dev_process_event.py",
    "scripts/lib/query_dev_process_event.py",
    "scripts/lib/emit_dev_process_event.py",
    "scripts/lib/dev_process_blob_store.py",
    "scripts/lib/redact_dev_process_content.py",
    "scripts/lib/aggregate_dev_process_event.py",
    "docs/inter-plugin-contracts/dev-process-event-v1.md",
    "tests/unit/test_authoring_self_gate.py",  # 위 substrate 의 11값 VALID_LANE_LABELS oracle mirror ((a) 동류)
    # (c) frozen/archived/sunsetted/append-only docs (firsthand: frontmatter status 확인)
    "docs/security/branch-protection-audit.md",                             # append-only dated audit ledger (과거 tuple 이력 rewrite = history 위조)
    "docs/inter-plugin-contracts/branch-protection-context-registry-v1.md", # status: Archived (frozen 2026-05-30 pre-consolidation snapshot)
    "docs/inter-plugin-contracts/reconcile-protocol-v1.md",                 # status: Sunsetted (deprecated contract, canary binding = frozen)
    # (d) mixed registries — ACTIVE deploy entry 0 (firsthand 확인), residual = append-only version_history/changelog + parity-lock mirror
    "docs/inter-plugin-contracts/MANIFEST.yaml",        # deploy_output/deploy_review_output 삭제 tombstone comment + version_history
    "docs/inter-plugin-contracts/label-registry-v2.md", # v2.112 active deploy label 13 entry 삭제(0 active), residual = date/version_history append-only NOTE (ADR-108 §2B)
    "docs/evidence-checks-registry.yaml",               # active deploy entry 삭제(entry_count 104 / dup_loci 0), residual = last_updated append-only changelog
}
# delete-set (사후 소멸 — exclusion 으로 사전-상태 run 이 사후-상태 모델링)
DELETE_PREFIX = ("plugins/codeforge-deploy/", "plugins/codeforge-deploy-review/")
_DELETE_WORKFLOWS = [
    "auto-deploy", "canary-auto-promote", "canary-promotion-criteria", "deploy-lane-presence",
    "deploy-lane-spawn-evidence", "deploy-review-lane-spawn-evidence", "deployment-schema-check",
    "rollback-signal-monitor",
]
_DELETE_SCRIPTS = [
    "scripts/deploy_blue_green.py", "scripts/canary_auto_promote.py", "scripts/auto_rollback_hook.py",
    "scripts/canary-auto-promote.sh", "scripts/check-rollback-signal.sh", "scripts/check_rollback_signal.py",
    "scripts/check-canary-compatibility.sh", "scripts/lib/canary-compatibility-helpers.sh",
    "templates/deployment/deploy-blue-green.sh", "templates/deployment/auto-rollback-hook.sh",
    "docs/inter-plugin-contracts/deploy-output-v1.md", "docs/inter-plugin-contracts/deploy-review-output-v1.md",
]
DELETE_EXACT = set(_DELETE_SCRIPTS)
for _wf in _DELETE_WORKFLOWS:
    DELETE_EXACT.add(".github/workflows/%s.yml" % _wf)
    DELETE_EXACT.add("templates/github-workflows/%s.yml" % _wf)


def excluded(f):
    if f.startswith(EXCL_PREFIX):
        return True
    if f in EXCL_EXACT or f in EXCL_FAKE or f in EXCL_CFP2782:
        return True
    if f.startswith(EXCL_KEEP_PREFIX):
        return True
    if f.startswith(DELETE_PREFIX) or f in DELETE_EXACT:
        return True
    if f.endswith("CHANGELOG.md"):        # append-only history (archive/CHANGELOG-legacy.md 동류)
        return True
    if f == "docs/wording-dictionary-baseline.yaml":  # GENERATED (regen job — 수기 편집 금지)
        return True
    return False


def _tracked_files(root):
    """git ls-files(tracked only). git 부재 시 os.walk fallback(포터빌리티)."""
    try:
        out = subprocess.run(
            ["git", "-C", str(root), "ls-files"],
            capture_output=True, text=True, encoding="utf-8", check=True,
        )
        return out.stdout.splitlines()
    except (OSError, subprocess.CalledProcessError):
        files = []
        for dirpath, dirnames, filenames in os.walk(root):
            if ".git" in dirnames:
                dirnames.remove(".git")
            for name in filenames:
                rel = os.path.relpath(os.path.join(dirpath, name), str(root)).replace(os.sep, "/")
                files.append(rel)
        return files


def scan(root, files):
    """비-exclusion 텍스트 자산을 token(양형)으로 스캔. Returns {relpath: [(line, tok, text)]}."""
    hits = {}
    for f in files:
        if excluded(f):
            continue
        if not f.endswith(SCANNED_EXT):
            continue
        p = os.path.join(str(root), f)
        try:
            with open(p, encoding="utf-8") as fh:
                lines = fh.read().splitlines()
        except (OSError, UnicodeDecodeError):
            continue
        for i, line in enumerate(lines, 1):
            for tok, rgx in COMPILED_TOKENS:
                if rgx.search(line):
                    hits.setdefault(f, []).append((i, tok, line.strip()[:110]))
                    break
    return hits


# ─────────────────────── delete-set basename bijection (INV-5) ───────────────
# 삭제 machinery basename 마다 ≥1 token 이 (양형) 커버해야 함 — token drift 방어.
DELETE_SET_BASENAMES = (
    # workflow basenames (8)
    [w + ".yml" for w in _DELETE_WORKFLOWS]
    # script/contract basenames
    + [os.path.basename(s) for s in _DELETE_SCRIPTS]
    # plugin dir names + relocated-source contract ns
    + ["codeforge-deploy", "codeforge-deploy-review"]
)


# ═════════════════════════════════════════════════════════════════════════════
# AC-3 (i)(ii)(iii): zero surviving deploy-ref over non-frozen/non-fixture scope
# ═════════════════════════════════════════════════════════════════════════════

def test_zero_dangling_deploy_ref():
    """비-frozen·비-fixture·비-KEEP 경로 전역 deploy-machinery token grep == 0.

    RED = 삭제 미완 / surviving-ref 잔존. 완전성 결정론 SSOT (§4.1 대표맵 아님).
    """
    hits = scan(REPO_ROOT, _tracked_files(REPO_ROOT))
    total = sum(len(v) for v in hits.values())
    if total:
        detail = []
        for f in sorted(hits):
            for i, tok, txt in hits[f][:6]:
                detail.append("  %s:%d [%s] %s" % (f, i, tok, txt))
        pytest.fail(
            "AC-3 surviving deploy-ref = %d (files=%d) — 완전성 SSOT RED:\n%s"
            % (total, len(hits), "\n".join(detail))
        )


# ═════════════════════════════════════════════════════════════════════════════
# INV-5: set(delete_set_basenames) ⊆ token coverage (bijection guard)
# ═════════════════════════════════════════════════════════════════════════════

def test_delete_set_token_bijection():
    """모든 삭제 machinery basename 이 ≥1 AC-3 token(양형)으로 커버됨 (variant-gap 0).

    누군가 token 을 지우면(또는 delete-set 이 늘면) 이 self-assert 가 RED → SSOT drift 차단.
    """
    uncovered = [
        base for base in DELETE_SET_BASENAMES
        if not any(rgx.search(base) for _tok, rgx in COMPILED_TOKENS)
    ]
    assert not uncovered, (
        "INV-5 bijection gap — 아래 delete-set basename 이 어떤 token 으로도 미커버:\n  %s"
        % "\n  ".join(uncovered)
    )


# ═════════════════════════════════════════════════════════════════════════════
# discriminating negative — 스캐너가 vacuous-always-pass 아님 (mutation survives-0)
# ═════════════════════════════════════════════════════════════════════════════

def test_discriminating_injected_dangling_is_flagged(tmp_path):
    """합성 dangling token 주입 → 스캐너 flag(양형 포함). + control(benign) + exclusion 존중.

    ADR-060 Amд22 test-masking 방어: always-pass 아님을 3-way 로 실증.
    """
    live = tmp_path / "docs" / "some_live_doc.md"
    live.parent.mkdir(parents=True)

    # (1) positive — non-excluded 경로에 hyphen-form 토큰 주입 → flag
    live.write_text("이 문서는 auto-deploy.yml 를 참조한다.\n", encoding="utf-8", newline="\n")
    assert scan(str(tmp_path), ["docs/some_live_doc.md"]), \
        "discriminating: 주입한 'auto-deploy' 토큰 미검출 = 스캐너 vacuous"

    # (1b) 양형 — underscore-form 변종도 동일 토큰으로 flag (variant-gap 0 실증)
    live.write_text("MANIFEST: deploy_output 키가 잔존한다.\n", encoding="utf-8", newline="\n")
    assert scan(str(tmp_path), ["docs/some_live_doc.md"]), \
        "discriminating: underscore 변종 'deploy_output' 미검출 = 양형 gap"

    # (2) control — benign lane 서술은 미flag (non-vacuous 판별력)
    live.write_text("이 문서는 통합테스트·보안테스트 lane 을 서술한다.\n", encoding="utf-8", newline="\n")
    assert not scan(str(tmp_path), ["docs/some_live_doc.md"]), \
        "control: benign 서술이 flag 되면 false-RED 공장"

    # (3) exclusion 존중 — 동일 토큰이 frozen 경로(archive/**)면 미flag
    frozen = tmp_path / "archive" / "adr" / "ADR-999-x.md"
    frozen.parent.mkdir(parents=True)
    frozen.write_text("historical: auto-deploy.yml + codeforge-deploy\n", encoding="utf-8", newline="\n")
    assert not scan(str(tmp_path), ["archive/adr/ADR-999-x.md"]), \
        "exclusion: archive/** frozen 경로는 스캔 제외"


def test_keep_set_not_flagged():
    """§5.5-1 RELOCATE KEEP-set(production-cutover machinery + relocated deputy)는 exclusion.

    KEEP 파일에 deploy-ish 토큰이 있어도 delete-set 아님 → surviving-ref 아님.
    """
    for keep in EXCL_EXACT:
        assert excluded(keep), "KEEP-set 파일이 exclusion 되지 않음: %s" % keep
    assert excluded("docs/domain-knowledge/domain/production-cutover/x.md"), \
        "production-cutover 도메인 KEEP prefix 미제외"


def test_allowlist_entries_are_real_tracked_files():
    """allowlist/exclusion 정직성 fence — 오타로 '아무것도 제외 안 함'(또는 오타 exclusion 이
    실 dangling 을 우연히 못 가림) 방지. EXCL_FAKE(token-vocabulary) + EXCL_CFP2782(frozen/
    substrate/registry) 전 항목이 실 tracked 파일로 존재해야 exclusion 이 의미를 가진다
    (hollow exclusion 차단; §8.5 honest-ceiling — presence ≠ frozenness 는 review-tier).
    """
    for rel in EXCL_FAKE | EXCL_CFP2782:
        assert (REPO_ROOT / rel).is_file(), \
            "allowlist/exclusion 항목이 실 파일 아님(오타/이동 의심): %s" % rel
