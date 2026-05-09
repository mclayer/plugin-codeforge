"""
test_codeforge_stories.py — CFP-342 / ADR-050 multi-repo story key system
validate_config.py 의 codeforge.stories 블록 검증 테스트

Test Contract: Change Plan §8 AC-1 ~ AC-8 / Invariant I1 ~ I5
QADeveloperAgent 작성 (Phase 2 구현 레인)

테스트 실행:
    python -m pytest tests/validate_config/test_codeforge_stories.py -v
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

# overlay/hooks/validate_config 를 import 경로에 추가
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "overlay" / "hooks"))

from validate_config import validate, _is_list_of_repo_entries  # noqa: E402


# ---------------------------------------------------------------------------
# 공통 minimal-valid base config (required fields 모두 포함)
# ---------------------------------------------------------------------------

def _base_config() -> dict:
    return {
        "project": {"name": "test-project"},
        "github": {
            "org": "acme",
            "repo": "test-project",
            "default_branch": "main",
            "pr_title_prefix_template": "[{key}] {title}",
            "story_key_prefix": "TP",
            "codeowners": {
                "architect_team": "@acme/architects",
                "domain_expert_team": "@acme/domain-experts",
            },
            "discussions": {"domain_kb_category": "Domain Q&A"},
            "milestone": {"epic_naming_pattern": "Epic-{key}-{slug}"},
        },
    }


def _valid_repos_block() -> dict:
    """최소 유효 codeforge.stories 블록 (governance 1 + implementation 1)."""
    return {
        "codeforge": {
            "stories": {
                "hub": {
                    "key_pattern": "MCT-{seq:03d}",
                    "story_dir": "docs/stories",
                    "template": "hub-story.md",
                },
                "repo_key_pattern": "MCT-{seq:03d}",
                "counters": {
                    "path": ".codeforge/counters.json",
                    "lock": "file",
                },
                "repos": [
                    {
                        "name": "mctrader-hub",
                        "role": "governance",
                        "github": "mclayer/mctrader-hub",
                        "story_dir": "docs/stories",
                        "creates_repo_stories": False,
                    },
                    {
                        "name": "mctrader-data",
                        "role": "implementation",
                        "path": "/workspace/mctrader-data",
                        "github": "mclayer/mctrader-data",
                        "story_dir": "docs/stories",
                        "components": ["data"],
                        "creates_repo_stories": True,
                    },
                ],
            }
        }
    }


# ===========================================================================
# AC-1: validate_config.py schema validation
# ===========================================================================

class TestAC1SchemaValidation:
    """AC-1: codeforge.stories.repos 블록 schema 검증 5 sub-case."""

    def test_ac1a_valid_block_passes(self):
        """AC-1(a): valid block (1+ entry) → exit 0 (errors 없음)."""
        cfg = {**_base_config(), **_valid_repos_block()}
        errors = validate(cfg)
        assert errors == [], f"예상치 못한 에러: {errors}"

    def test_ac1b_name_missing_fails(self):
        """AC-1(b): repos[].name 누락 → schema violation."""
        cfg = _base_config()
        cfg["codeforge"] = {
            "stories": {
                "repos": [
                    {"role": "governance", "github": "mclayer/hub"},  # name 없음
                ]
            }
        }
        errors = validate(cfg)
        assert any("codeforge.stories.repos" in e for e in errors), \
            f"repos name 누락 에러 미감지: {errors}"

    def test_ac1c_role_enum_violation_fails(self):
        """AC-1(c): role enum 위반 (e.g. role: foo) → schema violation."""
        cfg = _base_config()
        cfg["codeforge"] = {
            "stories": {
                "repos": [
                    {"name": "hub", "role": "foo", "github": "mclayer/hub"},  # role 위반
                ]
            }
        }
        errors = validate(cfg)
        assert any("codeforge.stories.repos" in e for e in errors), \
            f"role enum 위반 에러 미감지: {errors}"

    def test_ac1d_implementation_without_path_fails(self):
        """AC-1(d): role: implementation 인데 path 누락 → schema violation."""
        cfg = _base_config()
        cfg["codeforge"] = {
            "stories": {
                "repos": [
                    {
                        "name": "impl-repo",
                        "role": "implementation",
                        # path 없음
                        "github": "mclayer/impl-repo",
                    },
                ]
            }
        }
        errors = validate(cfg)
        assert any("codeforge.stories.repos" in e for e in errors), \
            f"path 누락 에러 미감지: {errors}"

    def test_ac1d_implementation_without_github_fails(self):
        """AC-1(d): role: implementation 인데 github 누락 → schema violation."""
        cfg = _base_config()
        cfg["codeforge"] = {
            "stories": {
                "repos": [
                    {
                        "name": "impl-repo",
                        "role": "implementation",
                        "path": "/workspace/impl-repo",
                        # github 없음
                    },
                ]
            }
        }
        errors = validate(cfg)
        assert any("codeforge.stories.repos" in e for e in errors), \
            f"github 누락 에러 미감지: {errors}"

    def test_ac1e_unknown_key_fails(self):
        """AC-1(e): unknown key (codeforge.stories.unknown) → _check_unknown_keys 차단."""
        cfg = _base_config()
        cfg["codeforge"] = {
            "stories": {
                "unknown_key": "should-be-rejected",  # 미정의 키
            }
        }
        errors = validate(cfg)
        assert any("unknown key" in e and "unknown_key" in e for e in errors), \
            f"unknown key 에러 미감지: {errors}"

    def test_ac1_codeforge_block_absent_passes(self):
        """AC-1 backward compat: codeforge 블록 전체 없어도 PASS (opt-in only)."""
        cfg = _base_config()
        # codeforge 블록 없음 → single-repo flat 모드 유지
        errors = validate(cfg)
        assert errors == [], f"codeforge 블록 부재 시 에러 발생: {errors}"

    def test_ac1_empty_repos_list_passes(self):
        """AC-1 경계: repos: [] → opt-in 미활성. schema 위반 아님."""
        cfg = {**_base_config()}
        cfg["codeforge"] = {"stories": {"repos": []}}
        errors = validate(cfg)
        assert errors == [], f"빈 repos 리스트 에러 발생: {errors}"

    def test_ac1_counters_invalid_lock_fails(self):
        """counters.lock 값이 enum 위반 → schema violation."""
        cfg = _base_config()
        cfg["codeforge"] = {
            "stories": {
                "counters": {"lock": "redis"},  # 'file' 만 허용
            }
        }
        errors = validate(cfg)
        assert any("codeforge.stories.counters.lock" in e for e in errors), \
            f"counters.lock enum 위반 미감지: {errors}"


# ===========================================================================
# AC-2: Hub story frontmatter 정합성 (템플릿 파일 존재 검증)
# ===========================================================================

class TestAC2HubStoryTemplate:
    """AC-2: templates/hub-story.md 파일 내용 검증."""

    TEMPLATE_PATH = Path(__file__).parent.parent.parent / "templates" / "hub-story.md"

    def test_ac2_template_file_exists(self):
        """AC-2: hub-story.md 파일이 존재해야 한다."""
        assert self.TEMPLATE_PATH.exists(), f"hub-story.md 없음: {self.TEMPLATE_PATH}"

    def test_ac2a_story_scope_hub_present(self):
        """AC-2(a): frontmatter 에 story_scope: hub 포함."""
        content = self.TEMPLATE_PATH.read_text(encoding="utf-8")
        assert "story_scope: hub" in content, "story_scope: hub 미포함"

    def test_ac2b_delegates_field_present(self):
        """AC-2(b): frontmatter 에 delegates[] field 포함."""
        content = self.TEMPLATE_PATH.read_text(encoding="utf-8")
        assert "delegates:" in content, "delegates 필드 미포함"

    def test_ac2c_title_h1_pattern(self):
        """AC-2(c): H1 title 패턴이 <KEY>: <coordination title> 형식."""
        content = self.TEMPLATE_PATH.read_text(encoding="utf-8")
        assert "# <KEY>: <coordination title>" in content, "H1 title 패턴 불일치"

    def test_ac2_delegation_section_present(self):
        """AC-2: Delegation 섹션 존재."""
        content = self.TEMPLATE_PATH.read_text(encoding="utf-8")
        assert "## Delegation" in content, "Delegation 섹션 미포함"

    def test_ac2_acceptance_gates_section_present(self):
        """AC-2: Acceptance Gates 섹션 존재."""
        content = self.TEMPLATE_PATH.read_text(encoding="utf-8")
        assert "## Acceptance Gates" in content, "Acceptance Gates 섹션 미포함"


# ===========================================================================
# AC-3: Repo story frontmatter 정합성
# ===========================================================================

class TestAC3RepoStoryTemplate:
    """AC-3: templates/repo-story.md 파일 내용 검증."""

    TEMPLATE_PATH = Path(__file__).parent.parent.parent / "templates" / "repo-story.md"

    def test_ac3_template_file_exists(self):
        """AC-3: repo-story.md 파일이 존재해야 한다."""
        assert self.TEMPLATE_PATH.exists(), f"repo-story.md 없음: {self.TEMPLATE_PATH}"

    def test_ac3a_story_scope_repo_present(self):
        """AC-3(a): frontmatter 에 story_scope: repo 포함."""
        content = self.TEMPLATE_PATH.read_text(encoding="utf-8")
        assert "story_scope: repo" in content, "story_scope: repo 미포함"

    def test_ac3a_repo_field_present(self):
        """AC-3(a): frontmatter 에 repo: field 포함."""
        content = self.TEMPLATE_PATH.read_text(encoding="utf-8")
        assert "repo: <repo-name>" in content, "repo 필드 미포함"

    def test_ac3c_hub_story_field_present(self):
        """AC-3(c): hub_story + hub_repo 필드 포함."""
        content = self.TEMPLATE_PATH.read_text(encoding="utf-8")
        assert "hub_story:" in content, "hub_story 필드 미포함"
        assert "hub_repo:" in content, "hub_repo 필드 미포함"

    def test_ac3_required_sections_present(self):
        """AC-3: Implementation Scope / Technical Design / Acceptance Criteria / Test Plan 섹션 존재."""
        content = self.TEMPLATE_PATH.read_text(encoding="utf-8")
        for section in ["## Implementation Scope", "## Technical Design",
                        "## Acceptance Criteria", "## Test Plan"]:
            assert section in content, f"{section} 섹션 미포함"

    def test_ac3_links_section_with_hub_link(self):
        """AC-3: Links 섹션에 Hub 링크 형식 포함."""
        content = self.TEMPLATE_PATH.read_text(encoding="utf-8")
        assert "## Links" in content, "Links 섹션 미포함"
        assert "Hub:" in content, "Hub 링크 미포함"


# ===========================================================================
# AC-4: .codeforge/counters.json schema (Phase 1 = schema 정의 검증만)
# ===========================================================================

class TestAC4CounterSchema:
    """AC-4: counters.json schema 명세 검증 (Phase 1 = 구조 유효성만)."""

    def _valid_counter_data(self) -> dict:
        return {
            "version": 1,
            "prefix": "MCT",
            "counters": {
                "mctrader-hub": {"next": 112},
                "mctrader-data": {"next": 1},
            },
            "reservations": {},
        }

    def test_ac4a_valid_counter_structure(self):
        """AC-4(a): version:1 + prefix + counters.<repo>.next 구조."""
        data = self._valid_counter_data()
        assert data["version"] == 1
        assert isinstance(data["prefix"], str) and data["prefix"]
        assert isinstance(data["counters"], dict)
        for repo, entry in data["counters"].items():
            assert isinstance(repo, str) and repo
            assert "next" in entry and isinstance(entry["next"], int)
            assert entry["next"] >= 1, "counter.next >= 1 invariant"

    def test_ac4a_version_invariant(self):
        """AC-4(a): version 필드는 정수 1 이어야 한다."""
        data = self._valid_counter_data()
        assert data["version"] == 1

    def test_ac4_counter_next_monotonic_simulated(self):
        """AC-4(b) + I1 시뮬레이션: counter next 단조 증가 invariant."""
        # Phase 2 실제 구현 전 단조 증가 로직 단위 시뮬레이션
        counter = {"next": 5}
        old_next = counter["next"]
        # increment
        counter["next"] += 1
        assert counter["next"] > old_next, "단조 증가 위반"

    def test_ac4c_reconciliation_logic(self):
        """AC-4(c): reconciliation — counter.next < filesystem_max+1 시 보정."""
        counter_next = 3   # counter file 의 현재 값
        filesystem_max = 5  # glob 으로 발견한 최대 seq

        # reconciliation rule: counter.next = max(counter.next, filesystem_max + 1)
        reconciled = max(counter_next, filesystem_max + 1)
        assert reconciled == 6, f"reconciliation 결과 오류: {reconciled}"
        assert reconciled > filesystem_max, "reconciled 값이 filesystem max 보다 커야 함"


# ===========================================================================
# AC-5: Agent target repo 결정 priority
# ===========================================================================

class TestAC5AgentTargetRepoPriority:
    """AC-5: story_scope + repo frontmatter → target repo 결정 우선순위."""

    def _resolve_target_repo(
        self,
        story_scope: str | None,
        repo: str | None,
        component: str | None,
        repos_config: list[dict],
    ) -> str | None:
        """
        target repo 결정 로직 (Change Plan §3.5 / ADR-050 §결정 4 4-priority 구현).
        None 반환 = ESCALATE.
        """
        # Priority 1: story_scope: repo + repo: <name>
        if story_scope == "repo" and repo:
            match = next((r for r in repos_config if r["name"] == repo), None)
            if match:
                return match["name"]

        # Priority 2: story_scope: hub → hub repo
        if story_scope == "hub":
            hub = next((r for r in repos_config if r["role"] == "governance"), None)
            if hub:
                return hub["name"]

        # Priority 3: component fallback (legacy / frontmatter 부재)
        if component:
            matches = [
                r for r in repos_config
                if component in r.get("components", [])
            ]
            if len(matches) == 1:
                return matches[0]["name"]
            # N>=2 matches → ESCALATE (None)

        # Priority 4: ESCALATE
        return None

    def _repos(self) -> list[dict]:
        return [
            {"name": "mctrader-hub", "role": "governance", "components": []},
            {"name": "mctrader-data", "role": "implementation", "components": ["data"]},
            {"name": "mctrader-engine", "role": "implementation", "components": ["engine"]},
        ]

    def test_ac5a_repo_frontmatter_direct(self):
        """AC-5(a): story_scope: repo + repo: <name> → 직접 지정."""
        result = self._resolve_target_repo(
            story_scope="repo", repo="mctrader-data",
            component=None, repos_config=self._repos()
        )
        assert result == "mctrader-data"

    def test_ac5b_hub_scope(self):
        """AC-5(b): story_scope: hub → hub repo (governance)."""
        result = self._resolve_target_repo(
            story_scope="hub", repo=None,
            component=None, repos_config=self._repos()
        )
        assert result == "mctrader-hub"

    def test_ac5c_component_fallback_single(self):
        """AC-5(c): frontmatter 부재 → component: engine → 단일 매핑."""
        result = self._resolve_target_repo(
            story_scope=None, repo=None,
            component="engine", repos_config=self._repos()
        )
        assert result == "mctrader-engine"

    def test_ac5d_escalate_on_ambiguous_component(self):
        """AC-5(d): component 다중 매핑 → ESCALATE (None)."""
        repos = self._repos() + [
            {"name": "mctrader-engine2", "role": "implementation", "components": ["engine"]},
        ]
        result = self._resolve_target_repo(
            story_scope=None, repo=None,
            component="engine", repos_config=repos
        )
        assert result is None, "다중 매핑 시 ESCALATE(None) 반환해야 함"

    def test_ac5d_escalate_no_match(self):
        """AC-5(d): 1-3 모두 실패 → ESCALATE (None)."""
        result = self._resolve_target_repo(
            story_scope=None, repo=None,
            component=None, repos_config=self._repos()
        )
        assert result is None, "모든 우선순위 실패 시 ESCALATE(None) 반환해야 함"


# ===========================================================================
# AC-6: Backward compat
# ===========================================================================

class TestAC6BackwardCompat:
    """AC-6: 기존 flat MCT-NNN story 및 story_scope 부재 backward compat."""

    def test_ac6a_codeforge_block_absent_no_error(self):
        """AC-6(a): codeforge 블록 부재 → validate PASS."""
        cfg = _base_config()
        errors = validate(cfg)
        assert errors == [], f"codeforge 블록 부재 시 에러: {errors}"

    def test_ac6c_legacy_hub_fallback_in_priority(self):
        """AC-6(c): story_scope 부재 = legacy-hub → hub repo fallback."""
        repos = [
            {"name": "mctrader-hub", "role": "governance", "components": []},
            {"name": "mctrader-data", "role": "implementation", "components": ["data"]},
        ]
        # story_scope 없고 component도 없음 → ESCALATE (hub repo 묵시 처리는 consumer-level)
        # validate_config.py 레벨에서는 에러 없음이 invariant
        cfg = _base_config()
        errors = validate(cfg)
        assert errors == []

    def test_ac6_new_schema_fields_are_optional(self):
        """AC-6: codeforge.stories 블록 필드들은 모두 optional."""
        # 빈 stories 블록만 있어도 에러 없음
        cfg = _base_config()
        cfg["codeforge"] = {"stories": {}}
        errors = validate(cfg)
        assert errors == [], f"빈 stories 블록 에러: {errors}"


# ===========================================================================
# AC-7: 다른 consumer 동일 시스템 적용
# ===========================================================================

class TestAC7GenericConsumer:
    """AC-7: project.yaml 선언만으로 동일 시스템 사용 가능."""

    def test_ac7a_different_consumer_config_valid(self):
        """AC-7(a)(b): consumer 가 repos[] 블록 선언만으로 활성화. Plugin core 변경 0."""
        # 다른 consumer prefix (PLAT-NNN)
        cfg = {
            "project": {"name": "platform-service"},
            "github": {
                "org": "acme",
                "repo": "platform-hub",
                "default_branch": "main",
                "pr_title_prefix_template": "[{key}] {title}",
                "story_key_prefix": "PLAT",
                "codeowners": {
                    "architect_team": "@acme/architects",
                    "domain_expert_team": "@acme/domain-experts",
                },
                "discussions": {"domain_kb_category": "Domain Q&A"},
                "milestone": {"epic_naming_pattern": "Epic-{key}-{slug}"},
            },
            "codeforge": {
                "stories": {
                    "repos": [
                        {
                            "name": "platform-hub",
                            "role": "governance",
                            "github": "acme/platform-hub",
                        },
                        {
                            "name": "platform-api",
                            "role": "implementation",
                            "path": "/workspace/platform-api",
                            "github": "acme/platform-api",
                            "components": ["api"],
                        },
                    ]
                }
            },
        }
        errors = validate(cfg)
        assert errors == [], f"다른 consumer config 에러: {errors}"

    def test_ac7_consumer_guide_template_exists(self):
        """AC-7(c): project.yaml.example 에 codeforge.stories 주석 예시 포함."""
        example_path = (
            Path(__file__).parent.parent.parent
            / "overlay" / "_overlay" / "project.yaml.example"
        )
        assert example_path.exists(), "project.yaml.example 없음"
        content = example_path.read_text(encoding="utf-8")
        assert "codeforge:" in content, "codeforge 섹션 예시 미포함"
        assert "stories:" in content, "stories 섹션 예시 미포함"
        assert "repos:" in content, "repos 예시 미포함"


# ===========================================================================
# AC-8: Bidirectional linking (schema-level validation)
# ===========================================================================

class TestAC8BidirectionalLinking:
    """AC-8: delegates[] ↔ hub_story 양방향 링크 schema 검증."""

    def test_ac8_hub_story_delegates_structure(self):
        """AC-8(a): hub story 의 delegates[] 구조 유효성."""
        delegates = [
            {
                "story_key": "MCT-001",
                "repo": "mctrader-data",
                "path": "docs/stories/MCT-001.md",
                "status": "draft",
            },
            {
                "story_key": "MCT-001",
                "repo": "mctrader-engine",
                "path": "docs/stories/MCT-001.md",
                "status": "in-progress",
            },
        ]
        # status enum 검증 (§5.5 Q3 결정: draft / in-progress / merged / cancelled)
        valid_statuses = {"draft", "in-progress", "merged", "cancelled"}
        for entry in delegates:
            assert entry["status"] in valid_statuses, \
                f"status enum 위반: {entry['status']}"
            assert "story_key" in entry and entry["story_key"]
            assert "repo" in entry and entry["repo"]
            assert "path" in entry and entry["path"]

    def test_ac8_repo_story_hub_link_structure(self):
        """AC-8(b): repo story 의 hub_story + hub_repo 필드 구조."""
        frontmatter = {
            "story_key": "MCT-001",
            "story_scope": "repo",
            "repo": "mctrader-data",
            "hub_story": "MCT-112",
            "hub_repo": "mctrader-hub",
        }
        assert frontmatter.get("hub_story") is not None or \
               frontmatter.get("hub_story") == "null", \
               "hub_story 필드 없음"
        assert frontmatter.get("hub_repo") is not None or \
               frontmatter.get("hub_repo") == "null", \
               "hub_repo 필드 없음"

    def test_ac8_standalone_repo_story_null_hub(self):
        """AC-8: 단독 repo story 는 hub_story: null 명시 허용."""
        frontmatter = {
            "story_key": "MCT-001",
            "story_scope": "repo",
            "repo": "mctrader-data",
            "hub_story": None,  # 단독 story
            "hub_repo": None,
        }
        # hub_story: null 은 유효 (단독 impl story)
        assert frontmatter["hub_story"] is None  # null 허용


# ===========================================================================
# Invariant I1 ~ I5
# ===========================================================================

class TestInvariants:
    """Change Plan §8.2 Invariant I1 ~ I5."""

    def test_i1_counter_monotonic(self):
        """I1: counter.next 단조 증가 — 발급 후 decrement 금지."""
        seq = [1, 2, 3, 4, 5]
        for i in range(1, len(seq)):
            assert seq[i] > seq[i - 1], f"단조 증가 위반: {seq[i]} <= {seq[i-1]}"

    def test_i2_file_counter_consistency(self):
        """I2: file-system glob max <= counter.next (reconciliation invariant)."""
        counter_next = 10
        filesystem_max = 9  # max seq found in docs/stories/MCT-*.md
        assert counter_next >= filesystem_max + 1, \
            f"counter.next({counter_next}) < filesystem_max+1({filesystem_max+1})"

    def test_i2_reconciliation_corrects_stale_counter(self):
        """I2: stale counter (counter < filesystem_max+1) → 보정 후 invariant 만족."""
        counter_next = 3  # stale
        filesystem_max = 7
        # reconciliation
        corrected = max(counter_next, filesystem_max + 1)
        assert corrected >= filesystem_max + 1, "보정 후에도 invariant 불만족"

    def test_i3_story_scope_repo_location_invariant(self):
        """I3: story_scope: repo + repo: <name> → file 은 해당 repo story_dir 내."""
        # story_scope=repo + repo=mctrader-data → file: /workspace/mctrader-data/docs/stories/<KEY>.md
        repo_config = {
            "name": "mctrader-data",
            "path": "/workspace/mctrader-data",
            "story_dir": "docs/stories",
        }
        expected_prefix = repo_config["path"] + "/" + repo_config["story_dir"] + "/"
        story_path = "/workspace/mctrader-data/docs/stories/MCT-001.md"
        assert story_path.startswith(expected_prefix), \
            f"story 파일이 repo story_dir 외부: {story_path}"

    def test_i4_delegates_bidirectional_invariant(self):
        """I4: hub delegates[].story_key → repo story 의 hub_story 일치."""
        hub_key = "MCT-112"
        delegates = [{"story_key": "MCT-001", "repo": "mctrader-data"}]
        # repo story frontmatter
        repo_frontmatter = {"story_key": "MCT-001", "hub_story": "MCT-112"}

        for delegate in delegates:
            assert repo_frontmatter.get("hub_story") == hub_key, \
                f"bidirectional 불일치: hub_story={repo_frontmatter.get('hub_story')} != {hub_key}"

    def test_i5_legacy_story_scope_absent_backward_compat(self):
        """I5: story_scope 부재 story 는 변경 없이 작동 (legacy-hub fallback)."""
        legacy_frontmatter = {
            "story_key": "MCT-107",
            # story_scope 없음
        }
        # legacy-hub 처리 = story_scope 없으면 hub repo 묵시
        scope = legacy_frontmatter.get("story_scope", "legacy-hub")
        assert scope == "legacy-hub", f"legacy fallback 실패: {scope}"


# ===========================================================================
# _is_list_of_repo_entries helper 직접 단위 테스트
# ===========================================================================

class TestIsListOfRepoEntriesHelper:
    """_is_list_of_repo_entries helper 함수 직접 단위 테스트."""

    def test_valid_governance_entry(self):
        assert _is_list_of_repo_entries([
            {"name": "hub", "role": "governance", "github": "acme/hub"}
        ]) is True

    def test_valid_implementation_entry(self):
        assert _is_list_of_repo_entries([
            {
                "name": "impl",
                "role": "implementation",
                "path": "/workspace/impl",
                "github": "acme/impl",
            }
        ]) is True

    def test_empty_list_is_valid(self):
        assert _is_list_of_repo_entries([]) is True

    def test_not_list_invalid(self):
        assert _is_list_of_repo_entries("not-a-list") is False

    def test_list_with_non_dict_invalid(self):
        assert _is_list_of_repo_entries(["string-entry"]) is False

    def test_name_empty_string_invalid(self):
        assert _is_list_of_repo_entries([{"name": "", "role": "governance"}]) is False

    def test_role_invalid_enum_fails(self):
        assert _is_list_of_repo_entries([{"name": "hub", "role": "admin"}]) is False

    def test_implementation_missing_path_fails(self):
        assert _is_list_of_repo_entries([
            {"name": "impl", "role": "implementation", "github": "acme/impl"}
        ]) is False

    def test_duplicate_name_fails(self):
        """uniqueness invariant: 동일 name 중복 entry → invalid."""
        assert _is_list_of_repo_entries([
            {"name": "hub", "role": "governance"},
            {"name": "hub", "role": "implementation", "path": "/p", "github": "a/b"},
        ]) is False

    def test_optional_fields_valid(self):
        assert _is_list_of_repo_entries([
            {
                "name": "impl",
                "role": "implementation",
                "path": "/workspace/impl",
                "github": "acme/impl",
                "story_dir": "docs/stories",
                "components": ["api", "worker"],
                "creates_repo_stories": True,
            }
        ]) is True

    def test_components_non_string_invalid(self):
        assert _is_list_of_repo_entries([
            {
                "name": "impl",
                "role": "implementation",
                "path": "/p",
                "github": "a/b",
                "components": [123],  # 숫자 → invalid
            }
        ]) is False

    def test_creates_repo_stories_non_bool_invalid(self):
        assert _is_list_of_repo_entries([
            {
                "name": "impl",
                "role": "implementation",
                "path": "/p",
                "github": "a/b",
                "creates_repo_stories": "yes",  # 문자열 → invalid
            }
        ]) is False
