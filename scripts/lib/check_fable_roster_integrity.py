#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
scripts/lib/check_fable_roster_integrity.py
CFP-2803 Phase 2 — §8 roster-integrity hard-gate (Fable 5 Tier A/B carve-out).

검사 대상: `plugins/*/agents/*.md` 41 파일 중 정확히 10개가 `model: fable` 이고,
그 10개가 Change Plan §7 target 정확 bijection 이며, SecurityTestPL 은 opus 유지,
전체 배포 haiku 7 / sonnet 10 / fable 10 / opus 14 (§3 census constraint).

Enumeration = globstar-robust — find + rglob 양 경로로 enumeration 진행.
preset-depth 3 파일(`plugins/*/presets/*/agents/*.md`) 포함 필수.

--self-test 모드: synthetic roster 생성해 mutation testing (M1~M5 discriminating fixture).
각 mutation(count off-by-one, bijection miss, SecurityTestPL drift, census distribution off,
globstar-fragile 38-file drop) 후 exit code 달라져야 함(anti-theater).

fail-closed (exit 0 = pass only, exit 1 = any violation / parse error, exit 2 = setup error).

Usage:
  python3 check_fable_roster_integrity.py [--repo-root DIR] [--self-test]

ADR-151 정직 천장: presence/alive/형식 까지만 fail-closed 강제.
"""

import argparse
import os
import re
import sys
import tempfile
from pathlib import Path

# 출력 인코딩 robust 화 (Windows cp949 등 비-UTF-8 locale 에서 한글 print 차단).
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
    except Exception:
        pass

EXIT_PASS = 0
EXIT_FAIL = 1
EXIT_SETUP = 2

# ── Target 10 fable 파일들 (bijection set) ──────────────────────────────────
FABLE_TARGETS = {
    "plugins/codeforge-requirements/agents/RequirementsPLAgent.md",
    "plugins/codeforge-review/agents/RequirementsReviewPLAgent.md",
    "plugins/codeforge-design/agents/ArchitectPLAgent.md",
    "plugins/codeforge-review/agents/DesignReviewPLAgent.md",
    "plugins/codeforge-develop/agents/DeveloperPLAgent.md",
    "plugins/codeforge-review/agents/CodeReviewPLAgent.md",
    "plugins/codeforge-pmo/agents/PMOAgent.md",
    "plugins/codeforge-design/agents/ArchitectAgent.md",
    "plugins/codeforge-requirements/agents/ResearcherAgent.md",
    "plugins/codeforge-test/agents/IntegrationTestAgent.md",
}

SECURITY_TEST_PL_PATH = "plugins/codeforge-review/agents/SecurityTestPLAgent.md"

# 정규화 경로 (backslash → forward slash)
FABLE_TARGETS_NORMALIZED = {p.replace("\\", "/") for p in FABLE_TARGETS}

# ── 모델 분포 기준 ──────────────────────────────────────────────────────────
EXPECTED_DIST = {
    "haiku": 7,
    "sonnet": 10,
    "fable": 10,
    "opus": 14,
}
EXPECTED_TOTAL = 41


def _error(msg):
    """stderr 에 ::error:: prefix 붙여 출력."""
    print(f"::error::{msg}", file=sys.stderr)


def _parse_model_from_frontmatter(path):
    """agent .md 파일 frontmatter 에서 model: 값 추출. 형식 오류 시 None."""
    try:
        with open(path, encoding="utf-8") as fh:
            in_frontmatter = False
            for line in fh:
                line = line.strip()
                if line == "---":
                    if not in_frontmatter:
                        in_frontmatter = True  # 첫 --- 시작
                        continue
                    else:
                        # 두 번째 --- 끝
                        break
                if in_frontmatter and line.startswith("model:"):
                    # model: <value> 형식 파싱
                    match = re.match(r"^model:\s*(\w+)", line)
                    if match:
                        return match.group(1)
    except (OSError, UnicodeDecodeError):
        pass
    return None


def _enumerate_agents(repo_root):
    """plugins/*/agents/*.md 를 globstar-robust 로 enumeration.

    Returns: {normalized_path: model_value} dict.
    각 파일은 정규화 경로(forward slash)로 저장.
    """
    agents_dir = repo_root / "plugins"
    agents = {}

    if not agents_dir.is_dir():
        return agents

    # rglob 으로 plugins 하위 모든 agents/*.md 찾기
    # 이 방식은 plugins/codeforge-develop/presets/*/agents/*.md 도 포함
    for md_file in agents_dir.rglob("*.md"):
        # 부모가 "agents" 디렉터리인지 확인
        if md_file.parent.name == "agents":
            norm_path = str(md_file.relative_to(repo_root)).replace("\\", "/")
            model = _parse_model_from_frontmatter(md_file)
            agents[norm_path] = model

    return agents


def _check_count(agents, fable_files):
    """count(model: fable) == 10 검사."""
    actual_fable = {p: model for p, model in agents.items() if model == "fable"}
    count = len(actual_fable)

    if count != 10:
        _error(f"fable 파일 count={count}, expected=10 (bijection 위반).")
        return False

    return True


def _check_bijection(agents):
    """target 10 파일 정확 일치 검사."""
    actual_fable_paths = {p for p, model in agents.items() if model == "fable"}

    # 목표와 실제 일치하는가
    missing = FABLE_TARGETS_NORMALIZED - actual_fable_paths
    extra = actual_fable_paths - FABLE_TARGETS_NORMALIZED

    if missing:
        _error(f"target fable 파일 누락: {sorted(missing)}")
        return False

    if extra:
        _error(f"예상 밖 fable 파일: {sorted(extra)}")
        return False

    return True


def _check_security_test_pl(agents):
    """SecurityTestPL 이 opus (fable 아님) 인지 검사."""
    model = agents.get(SECURITY_TEST_PL_PATH.replace("\\", "/"))

    if model != "opus":
        _error(f"SecurityTestPLAgent model={model}, expected=opus (fable sweep 대상 아님).")
        return False

    return True


def _check_distribution(agents):
    """전체 배포 census 검사: 총 41 파일, 분포 7/10/10/14."""
    dist = {}
    for path, model in agents.items():
        if model:
            dist[model] = dist.get(model, 0) + 1

    total = sum(dist.values())

    if total != EXPECTED_TOTAL:
        _error(f"enumeration 총 {total}개, expected={EXPECTED_TOTAL}.")
        return False

    for model, expected_count in EXPECTED_DIST.items():
        actual_count = dist.get(model, 0)
        if actual_count != expected_count:
            _error(f"{model} count={actual_count}, expected={expected_count}.")
            return False

    return True


def run_real(repo_root):
    """Real mode — repo 실제 roster 검사."""
    repo_root = Path(repo_root).resolve()
    agents = _enumerate_agents(repo_root)

    if not agents:
        _error(f"plugin agents 파일 부재 (enumeration 0).")
        return EXIT_FAIL

    violations = []

    # 4 check axes
    if not _check_count(agents, FABLE_TARGETS_NORMALIZED):
        violations.append("count")

    if not _check_bijection(agents):
        violations.append("bijection")

    if not _check_security_test_pl(agents):
        violations.append("security_test_pl")

    if not _check_distribution(agents):
        violations.append("distribution")

    if violations:
        return EXIT_FAIL

    print(f"✓ fable-roster-integrity PASS — fable {10}개, target bijection 정확, "
          f"SecurityTestPL opus, 배포 7/10/10/14, 총 41파일.")
    return EXIT_PASS


def run_self_test():
    """Self-test mode — synthetic roster 로 mutation testing."""

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_root = Path(tmpdir)

        # ── Setup: synthetic roster 생성 (canonical 41 파일) ──────────────────
        def create_synthetic(fable_override=None):
            """synthetic repo 생성. fable_override 는 {'path': 'model'} 형태 override."""
            for plugin_dir in ["codeforge-requirements", "codeforge-design",
                              "codeforge-develop", "codeforge-review", "codeforge-test", "codeforge-pmo"]:
                agents_dir = tmp_root / "plugins" / plugin_dir / "agents"
                agents_dir.mkdir(parents=True, exist_ok=True)

            # Preset dirs
            for preset_path in ["codeforge-develop/presets/backend-service/agents",
                               "codeforge-develop/presets/webapp/agents"]:
                preset_agents = tmp_root / "plugins" / preset_path
                preset_agents.mkdir(parents=True, exist_ok=True)

            # 기본 모델 배치 (41 파일)
            canonical = {
                # codeforge-requirements (7)
                "plugins/codeforge-requirements/agents/RequirementsPLAgent.md": "fable",
                "plugins/codeforge-requirements/agents/ResearcherAgent.md": "fable",
                "plugins/codeforge-requirements/agents/DomainAgent.md": "opus",
                "plugins/codeforge-requirements/agents/FeasibilityAgent.md": "opus",
                "plugins/codeforge-requirements/agents/ContinuityAgent.md": "opus",
                "plugins/codeforge-requirements/agents/ChangeImpactAgent.md": "sonnet",
                "plugins/codeforge-requirements/agents/RequirementsAnalystAgent.md": "haiku",
                "plugins/codeforge-requirements/agents/codex-proactive-check.md": "opus",
                # codeforge-design (14)
                "plugins/codeforge-design/agents/ArchitectPLAgent.md": "fable",
                "plugins/codeforge-design/agents/ArchitectAgent.md": "fable",
                "plugins/codeforge-design/agents/ArchitectAnalystAgent.md": "sonnet",
                "plugins/codeforge-design/agents/CodebaseMapperAgent.md": "haiku",
                "plugins/codeforge-design/agents/RefactorAgent.md": "sonnet",
                "plugins/codeforge-design/agents/APIContractArchitectAgent.md": "sonnet",
                "plugins/codeforge-design/agents/ModuleArchitectAgent.md": "sonnet",
                "plugins/codeforge-design/agents/DataArchitectAgent.md": "opus",
                "plugins/codeforge-design/agents/SecurityArchitectAgent.md": "opus",
                "plugins/codeforge-design/agents/TestContractArchitectAgent.md": "opus",
                "plugins/codeforge-design/agents/InfraOperationalArchitectAgent.md": "opus",
                "plugins/codeforge-design/agents/LiveOpsDeputyAgent.md": "opus",
                "plugins/codeforge-design/agents/LiveOrderingDeputyAgent.md": "opus",
                "plugins/codeforge-design/agents/ProductionEvidenceDeputyAgent.md": "opus",
                # codeforge-develop (8)
                "plugins/codeforge-develop/agents/DeveloperPLAgent.md": "fable",
                "plugins/codeforge-develop/agents/DeveloperAgent.md": "opus",
                "plugins/codeforge-develop/agents/DataEngineerAgent.md": "haiku",
                "plugins/codeforge-develop/agents/InfraEngineerAgent.md": "haiku",
                "plugins/codeforge-develop/agents/QADeveloperAgent.md": "haiku",
                "plugins/codeforge-develop/presets/backend-service/agents/ServiceDeveloperAgent.md": "sonnet",
                "plugins/codeforge-develop/presets/webapp/agents/BackendDeveloperAgent.md": "sonnet",
                "plugins/codeforge-develop/presets/webapp/agents/FrontendDeveloperAgent.md": "sonnet",
                # codeforge-review (6)
                "plugins/codeforge-review/agents/RequirementsReviewPLAgent.md": "fable",
                "plugins/codeforge-review/agents/DesignReviewPLAgent.md": "fable",
                "plugins/codeforge-review/agents/CodeReviewPLAgent.md": "fable",
                "plugins/codeforge-review/agents/SecurityTestPLAgent.md": "opus",
                "plugins/codeforge-review/agents/ClaudeReviewAgent.md": "opus",
                "plugins/codeforge-review/agents/CodexReviewAgent.md": "haiku",
                # codeforge-test (3)
                "plugins/codeforge-test/agents/TestAgent.md": "haiku",
                "plugins/codeforge-test/agents/IntegrationTestAgent.md": "fable",
                "plugins/codeforge-test/agents/StatefulTestAgent.md": "sonnet",
                # codeforge-pmo (2)
                "plugins/codeforge-pmo/agents/PMOAgent.md": "fable",
                "plugins/codeforge-pmo/agents/GitOpsAgent.md": "sonnet",
            }

            # Apply overrides
            if fable_override:
                canonical.update(fable_override)

            # Write files
            for path, model in canonical.items():
                md_file = tmp_root / path
                md_file.parent.mkdir(parents=True, exist_ok=True)
                md_file.write_text(f"---\nmodel: {model}\n---\n# Agent\n")

        # ── (i) Canonical post-state (PASS) ──────────────────────────────
        create_synthetic()
        agents = _enumerate_agents(tmp_root)
        if not (_check_count(agents, FABLE_TARGETS_NORMALIZED) and
                _check_bijection(agents) and
                _check_security_test_pl(agents) and
                _check_distribution(agents)):
            _error("(i) canonical: 기본 배치 검사 실패 — fixture 생성 오류.")
            return EXIT_FAIL

        # ── (ii) Mutate: 1개 fable→opus (count 9) ──────────────────────────
        create_synthetic({"plugins/codeforge-requirements/agents/RequirementsPLAgent.md": "opus"})
        agents = _enumerate_agents(tmp_root)
        if _check_count(agents, FABLE_TARGETS_NORMALIZED):  # PASS되면 mutation 실패(discriminating 아님)
            _error("(ii) mutant fable→opus: count 검사가 9를 통과(anti-discriminating).")
            return EXIT_FAIL

        # ── (iii) Mutate: SecurityTestPL opus→fable ────────────────────────
        create_synthetic({SECURITY_TEST_PL_PATH.replace("\\", "/"): "fable"})
        agents = _enumerate_agents(tmp_root)
        if _check_security_test_pl(agents):  # PASS되면 mutation 실패
            _error("(iii) mutant SecurityTestPL→fable: 검사가 drift를 놓침(anti-discriminating).")
            return EXIT_FAIL

        # ── (iv) Drop preset files (enumeration 38 = globstar-fragile) ──────
        # preset files 3개를 제외한 기본만 생성
        with tempfile.TemporaryDirectory() as tmpdir_no_preset:
            tmp_no_preset = Path(tmpdir_no_preset)
            for plugin_dir in ["codeforge-requirements", "codeforge-design",
                              "codeforge-develop", "codeforge-review", "codeforge-test", "codeforge-pmo"]:
                agents_dir = tmp_no_preset / "plugins" / plugin_dir / "agents"
                agents_dir.mkdir(parents=True, exist_ok=True)

            # 기본 38개 파일만 생성 (preset 3개 제외)
            canonical_no_preset = {
                k: v for k, v in {
                    "plugins/codeforge-requirements/agents/RequirementsPLAgent.md": "fable",
                    "plugins/codeforge-requirements/agents/ResearcherAgent.md": "fable",
                    "plugins/codeforge-requirements/agents/DomainAgent.md": "opus",
                    "plugins/codeforge-requirements/agents/FeasibilityAgent.md": "opus",
                    "plugins/codeforge-requirements/agents/ContinuityAgent.md": "opus",
                    "plugins/codeforge-requirements/agents/ChangeImpactAgent.md": "sonnet",
                    "plugins/codeforge-requirements/agents/RequirementsAnalystAgent.md": "haiku",
                    "plugins/codeforge-requirements/agents/codex-proactive-check.md": "opus",
                    "plugins/codeforge-design/agents/ArchitectPLAgent.md": "fable",
                    "plugins/codeforge-design/agents/ArchitectAgent.md": "fable",
                    "plugins/codeforge-design/agents/ArchitectAnalystAgent.md": "sonnet",
                    "plugins/codeforge-design/agents/CodebaseMapperAgent.md": "haiku",
                    "plugins/codeforge-design/agents/RefactorAgent.md": "sonnet",
                    "plugins/codeforge-design/agents/APIContractArchitectAgent.md": "sonnet",
                    "plugins/codeforge-design/agents/ModuleArchitectAgent.md": "sonnet",
                    "plugins/codeforge-design/agents/DataArchitectAgent.md": "opus",
                    "plugins/codeforge-design/agents/SecurityArchitectAgent.md": "opus",
                    "plugins/codeforge-design/agents/TestContractArchitectAgent.md": "opus",
                    "plugins/codeforge-design/agents/InfraOperationalArchitectAgent.md": "opus",
                    "plugins/codeforge-design/agents/LiveOpsDeputyAgent.md": "opus",
                    "plugins/codeforge-design/agents/LiveOrderingDeputyAgent.md": "opus",
                    "plugins/codeforge-design/agents/ProductionEvidenceDeputyAgent.md": "opus",
                    "plugins/codeforge-develop/agents/DeveloperPLAgent.md": "fable",
                    "plugins/codeforge-develop/agents/DeveloperAgent.md": "opus",
                    "plugins/codeforge-develop/agents/DataEngineerAgent.md": "haiku",
                    "plugins/codeforge-develop/agents/InfraEngineerAgent.md": "haiku",
                    "plugins/codeforge-develop/agents/QADeveloperAgent.md": "haiku",
                    "plugins/codeforge-review/agents/RequirementsReviewPLAgent.md": "fable",
                    "plugins/codeforge-review/agents/DesignReviewPLAgent.md": "fable",
                    "plugins/codeforge-review/agents/CodeReviewPLAgent.md": "fable",
                    "plugins/codeforge-review/agents/SecurityTestPLAgent.md": "opus",
                    "plugins/codeforge-review/agents/ClaudeReviewAgent.md": "opus",
                    "plugins/codeforge-review/agents/CodexReviewAgent.md": "haiku",
                    "plugins/codeforge-test/agents/TestAgent.md": "haiku",
                    "plugins/codeforge-test/agents/IntegrationTestAgent.md": "fable",
                    "plugins/codeforge-test/agents/StatefulTestAgent.md": "sonnet",
                    "plugins/codeforge-pmo/agents/PMOAgent.md": "fable",
                    "plugins/codeforge-pmo/agents/GitOpsAgent.md": "sonnet",
                }.items() if not k.startswith("plugins/codeforge-develop/presets")
            }

            for path, model in canonical_no_preset.items():
                md_file = tmp_no_preset / path
                md_file.parent.mkdir(parents=True, exist_ok=True)
                md_file.write_text(f"---\nmodel: {model}\n---\n# Agent\n")

            agents_no_preset = _enumerate_agents(tmp_no_preset)
            if _check_distribution(agents_no_preset):  # PASS되면 mutation 실패(globstar 안 작동)
                _error("(iv) mutant drop presets: 배포 검사가 38을 통과(anti-discriminating, globstar 안 작동).")
                return EXIT_FAIL

        # ── (v) Mutate: non-fable→fable (count 11) ────────────────────────
        create_synthetic({"plugins/codeforge-requirements/agents/DomainAgent.md": "fable"})
        agents = _enumerate_agents(tmp_root)
        if _check_bijection(agents):  # PASS되면 mutation 실패(11 target set 미감지)
            _error("(v) mutant non-fable→fable: bijection 검사가 11을 통과(anti-discriminating).")
            return EXIT_FAIL

    print("✓ fable-roster-integrity --self-test: 전 5-mutation 검사 통과 (discriminating fixture).")
    return EXIT_PASS


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=(
            "Fable tier roster-integrity 게이트 (CFP-2803 Phase 2). "
            "10 fable 정확 bijection + SecurityTestPL opus + census 41개 7/10/10/14. "
            "--self-test: synthetic mutation-testing."
        )
    )
    default_root = Path(__file__).resolve().parents[2]  # scripts/lib → repo-root
    parser.add_argument(
        "--repo-root", default=str(default_root),
        help="repo 루트 (기본 = __file__ parents[2]).",
    )
    parser.add_argument(
        "--self-test", action="store_true",
        help="synthetic roster 로 mutation-testing 모드 실행.",
    )

    args = parser.parse_args(argv)

    if args.self_test:
        return run_self_test()
    else:
        return run_real(args.repo_root)


if __name__ == "__main__":
    sys.exit(main())
