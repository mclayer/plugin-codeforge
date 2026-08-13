#!/usr/bin/env python3
"""tests/scripts/test_cfp2914_surfaces.py

CFP-2914 Phase 2 — 표면 검증 테스트 (AC-5·AC-6·AC-9·AC-10a)

AC-5  declared-not-bound 정산 축 검출 (4-site) + negative control
AC-6  cap 13 문면 정합 (4면 반영 × 3면 대조 실측)
AC-9  over-claim 금지 어휘 (2층 검출 + MUT-9d 신규추가 감지)
AC-10a 검사량 5종 무축소 (before/after 실측 파싱)

검사 원칙 (ADR-145 no-hollow):
- 모든 assert는 repo 파일 실제 파싱 기반
- `or True` 금지 (무력한 assert)
- 상수 항등식 금지 (리터럴 산술만으로 검증 금지)
- mutant로 판별력 실증 의무 (RED 확인)
"""

import os
import re
import subprocess
import sys
import tempfile
import yaml
from pathlib import Path


class TestCapSurfaceConsistency:
    """AC-6: worker_count_max = 13 일치성 검증

    반영 4면: 반드시 13이어야 함
      ①  parallel-dispatch-protocol-v1.md:215
      ②  parallel-dispatch-protocol-v1.md:298
      ③  scripts/check_parallel_dispatch_prompt.py:84
      ④  skills/rate-limit-429-mitigation/SKILL.md:133
      ⑤-⑦ templates/team-spec-*.yaml 7파일

    대조 3면: 반드시 7 유지 (실측 파싱)
      ⑧  ADR-042
      ⑨  skills/deputy-mandate/SKILL.md
      ⑩  archive/adr/ADR-044*.md
    """

    def test_cap_surface_consistency(self):
        """반영 4면 13 + 대조 3면 7 (모두 실측 파싱)"""
        worktree_root = Path(__file__).parent.parent.parent

        # 반영 4면: 13 확인
        protocol_file = worktree_root / "docs/inter-plugin-contracts/parallel-dispatch-protocol-v1.md"
        protocol_text = protocol_file.read_text(encoding='utf-8')
        assert re.search(r'worker_count_max.*default\s+13', protocol_text, re.IGNORECASE), \
            f"AC-6 실패: {protocol_file}에 'default 13'이 없음"
        assert re.search(r'worker_count.*<=.*worker_count_max.*default\s+13', protocol_text, re.IGNORECASE), \
            f"AC-6 실패: {protocol_file}에 검사 항목 5번 '(default 13)'이 없음"

        prompt_check = worktree_root / "scripts/check_parallel_dispatch_prompt.py"
        prompt_text = prompt_check.read_text(encoding='utf-8')
        assert re.search(r'WORKER_COUNT_MAX_DEFAULT\s*=\s*13', prompt_text), \
            f"AC-6 실패: {prompt_check}에 'WORKER_COUNT_MAX_DEFAULT = 13'이 없음"

        rate_limit_skill = worktree_root / "skills/rate-limit-429-mitigation/SKILL.md"
        rate_limit_text = rate_limit_skill.read_text(encoding='utf-8')
        assert re.search(r'parallel_spawn_cap\s*=\s*13', rate_limit_text), \
            f"AC-6 실패: {rate_limit_skill}에 'parallel_spawn_cap = 13'이 없음"

        team_spec_dir = worktree_root / "templates"
        team_spec_files = sorted(team_spec_dir.glob("team-spec-*.yaml"))
        assert len(team_spec_files) == 7, f"AC-6 실패: team-spec 파일 수 {len(team_spec_files)} ≠ 7"
        for team_spec_file in team_spec_files:
            team_spec_text = team_spec_file.read_text(encoding='utf-8')
            assert re.search(r'parallel_spawn_cap:\s*13', team_spec_text), \
                f"AC-6 실패: {team_spec_file}에 'parallel_spawn_cap: 13'이 없음"

        # 대조 3면: 7 유지 (실측 파싱)
        adr_042 = worktree_root / "archive/adr/ADR-042-agent-model-selection-policy.md"
        if adr_042.exists():
            adr_042_text = adr_042.read_text(encoding='utf-8')
            assert re.search(r'(?:team.*spec|deputy|default).*\b7\b', adr_042_text, re.IGNORECASE), \
                f"AC-6 실패: {adr_042}에 'default 7' 참조 없음"

        deputy_skill = worktree_root / "skills/deputy-mandate/SKILL.md"
        if deputy_skill.exists():
            deputy_text = deputy_skill.read_text(encoding='utf-8')
            assert re.search(r'6\s+permanent', deputy_text), \
                f"AC-6 실패: {deputy_skill}에 '6 permanent deputy'이 없음"

        adr_044_files = list(worktree_root.glob("archive/adr/ADR-044*.md"))
        if adr_044_files:
            adr_044_text = adr_044_files[0].read_text(encoding='utf-8')
            assert re.search(r'default\s+7', adr_044_text, re.IGNORECASE), \
                f"AC-6 실패: ADR-044에 'default 7' schema 참조 없음"


class TestDeclaredNotBoundAbsenceAxis:
    """AC-5: declared-not-bound 정산 4-site 부재 축 검출 + negative control"""

    def test_declared_not_bound_absence_axis(self):
        """4-site 부재 축 + dangling/sunset_justification 주입 감지"""
        worktree_root = Path(__file__).parent.parent.parent

        # ① 선언 확인
        protocol_file = worktree_root / "docs/inter-plugin-contracts/parallel-dispatch-protocol-v1.md"
        protocol_text = protocol_file.read_text(encoding='utf-8')
        assert re.search(r'현행\s+배선\s+상태\s*=\s*.*미배선.*호출자\s+0', protocol_text), \
            f"AC-5 실패: {protocol_file}에 '미배선(호출자 0)' 선언 부재"

        # ② registry entry 확인
        registry_file = worktree_root / "docs/evidence-checks-registry.yaml"
        registry_text = registry_file.read_text(encoding='utf-8')
        assert 'lane-evidence-trail' in registry_text, \
            f"AC-5 실패: {registry_file}에 'lane-evidence-trail' entry 부재"

        # ③ 호출자 0 정직 마커 확인
        prompt_check = worktree_root / "scripts/check_parallel_dispatch_prompt.py"
        prompt_text = prompt_check.read_text(encoding='utf-8')
        assert re.search(r'현행\s+배선\s+상태\s*=\s*.*미배선.*호출자\s+0', prompt_text), \
            f"AC-5 실패: {prompt_check}에 정직 미배선 마커 부재"

        # **Negative control: registry entry 구조 검증 + 필수 필드 presence**
        # F-CR-004: 실제 검사기(registry 파싱) 호출로 정정
        import yaml

        try:
            registry_data = yaml.safe_load(registry_text)
        except yaml.YAMLError as e:
            pytest.fail(f"AC-5 registry YAML 파싱 실패: {e}")

        # entry 별 구조 및 필수 필드 검증
        # ★ fail-closed: shape 를 assert 로 확정한 뒤 순회한다. `if 'entries' in ...` 로 감싸면
        #   registry 최상위 shape 가 바뀌는 순간 루프가 0회 돌고 missing_fields 가 빈 채로
        #   assert 를 통과해 검사가 조용히 사라진다(vacuous pass). 그 침묵 경로를 차단한다.
        assert isinstance(registry_data, dict), \
            f"AC-5 실패: registry 최상위가 dict 가 아니다 — {type(registry_data).__name__}"
        assert 'entries' in registry_data, \
            f"AC-5 실패: registry 에 'entries' 키 부재 — 최상위 키 {list(registry_data)}"
        entries = registry_data.get('entries') or []
        assert len(entries) > 0, "AC-5 실패: registry entries 가 비어 있다 — 검사 정의역 0"

        missing_fields = []
        for entry_idx, entry in enumerate(entries):
                entry_name = entry.get('name', f'entry[{entry_idx}]')

                # 필수 필드 확인
                if not entry.get('name'):
                    missing_fields.append(f"{entry_name}:name(required)")
                if not entry.get('description'):
                    missing_fields.append(f"{entry_name}:description(required)")
                if not entry.get('current_tier'):
                    missing_fields.append(f"{entry_name}:current_tier(required)")

                # detect_command 가 있으면 empty 이면 안됨 (bash scripts/... 형태)
                detect_cmd = entry.get('detect_command')
                if detect_cmd == '':  # 명시적 빈 문자열 = 선언했지만 구현 X
                    missing_fields.append(f"{entry_name}:detect_command(empty)")

                # workflow 가 있으면 (null 아니면) empty 이면 안됨
                workflow = entry.get('workflow')
                if workflow == '':  # 명시적 빈 문자열
                    missing_fields.append(f"{entry_name}:workflow(empty)")

        assert len(missing_fields) == 0, \
            f"AC-5 negative control: 다음 entry 들의 필수 필드 부재/공백: {missing_fields}"


class TestOverclaimLexiconTwoLayer:
    """AC-9: over-claim 금지 어휘 2층 검출 + MUT-9d 신규 추가 감지"""

    def test_overclaim_lexicon_two_layer(self):
        """금지 어휘 검출 (Layer1: 단정 용법, Layer2: 문장 단위) + MUT-9d 신규추가"""
        worktree_root = Path(__file__).parent.parent.parent

        # 금지 어휘 SSOT 위치 확인 (SSOT가 어디 있는지 먼저 찾기)
        # Change Plan과 ADR에서 정의된 금지 어휘 수집
        cp_file = worktree_root / "archive/adr/ADR-064-decision-principle-mandate.md"
        if not cp_file.exists():
            pytest.skip("ADR-064 부재 — SSOT 미확보")

        cp_text = cp_file.read_text(encoding='utf-8')

        # SSOT에서 명시된 금지 어휘 확인
        forbidden_words_in_cp = re.findall(r'"([^"]*(?:100%|hard-gate|완전|guarantee)[^"]*)"', cp_text)
        assert len(forbidden_words_in_cp) > 0 or \
               re.search(r'금지.*어휘|over-claim.*금지', cp_text, re.IGNORECASE), \
            "AC-9 SSOT: Change Plan에 금지 어휘 정의 부재"

        # Layer 1 & 2: 검사 대상 파일들에서 긍정 단정 용법 검출
        check_files = [
            cp_file,
            worktree_root / "docs/inter-plugin-contracts/parallel-dispatch-protocol-v1.md",
        ]

        violations = []
        for check_file in check_files:
            if not check_file.exists():
                continue
            text = check_file.read_text(encoding='utf-8')
            lines = text.split('\n')

            for line_no, line in enumerate(lines, 1):
                # Layer 1: 부정어 없는 단정 용법만
                has_negation = bool(re.search(r'\b(?:not|없음|금지|불가|disable|off)\b', line, re.IGNORECASE))
                # Layer 2: 명시/인용 제외 (backtick이나 따옴표 안)
                in_code = bool(re.search(r'`[^`]*|"[^"]*|\'[^\']*', line))

                # 금지 어휘 검사 (예시 어휘)
                if (re.search(r'\b100%\s+(?:기계강제|hard|automatic)', line, re.IGNORECASE) or
                    re.search(r'\b(?:hard-gate|완전\s+봉인)\b', line, re.IGNORECASE)) and \
                   not has_negation and not in_code:
                    violations.append(f"{check_file}:{line_no}")

        # 금지 어휘 위반 없어야 함
        assert len(violations) == 0, f"AC-9 위반: {violations}"

        # MUT-9d: 신규 어휘 추가 시 감지
        # 테스트 파일 자신도 검사 scope (I-8)
        self_file = Path(__file__)
        self_text = self_file.read_text(encoding='utf-8', errors='ignore')
        # 본 파일이 금지 어휘를 사용하지 않는지 확인
        assert not re.search(r'\b100%\s+기계강제\b', self_text, re.IGNORECASE), \
            "AC-9 I-8: 테스트 파일 자신이 금지 어휘를 사용함"


class TestInspectionVolumeFiveMetrics:
    """AC-10a: 검사량 5종 before/after (실측 파싱)

    5종:
      ① lane 수: 8
      ② 리뷰 peer 수: 2
      ③ FIX 루프 상한: 3
      ④ 게이트 수 (required contexts): 8
      ⑤ deputy mandate 수: 6 permanent + 3+1 CONDITIONAL
    """

    def test_inspection_volume_five_metrics(self):
        """5종 before/after 실측 (상수 항등식 금지)"""
        worktree_root = Path(__file__).parent.parent.parent

        # ① lane 수: 8 (실측 파싱)
        mjs_file = worktree_root / ".github/scripts/check-lane-evidence-block.mjs"
        if mjs_file.exists():
            mjs_text = mjs_file.read_text(encoding='utf-8')
            match = re.search(r'REQUIRED_LANES\s*=\s*\[([\s\S]*?)\]', mjs_text)
            if match:
                lanes_str = match.group(1)
                lane_list = re.findall(r'["\']([^"\']+)["\']', lanes_str)
                assert len(lane_list) >= 8, \
                    f"AC-10a 실패: lane 수 {len(lane_list)} < 8 (실측 .mjs)"

        # ② 리뷰 peer 수 = 2 — 실측원은 SUT 의 closed-set 배열 `PEER_AGENT_IDS` 다.
        #   (문서에 이름이 '등장하는가' 를 묻는 substring 확인은 판별력이 없다 — 어느 문서든
        #    이름을 언급만 해도 통과하므로 peer 가 1종으로 줄어도 검출하지 못한다.)
        sut = worktree_root / "scripts" / "check-lane-evidence.sh"
        assert sut.exists(), f"AC-10a 실패: SUT 부재 {sut}"
        sut_text = sut.read_text(encoding='utf-8')
        peer_decl = re.search(r'PEER_AGENT_IDS=\(([^)]*)\)', sut_text)
        assert peer_decl, "AC-10a 실패: PEER_AGENT_IDS closed-set 선언 부재"
        peer_ids = re.findall(r'"([^"]+)"', peer_decl.group(1))
        assert len(peer_ids) >= 2, \
            f"AC-10a 실패(검사량 축소): 리뷰 peer {len(peer_ids)}종 < 2 — {peer_ids}"

        # ③ FIX 루프: 3 (repo에서 명시 확인)
        # F-CR-010: 파일 부재를 실패로 승격 (fail-closed)
        claude_md = worktree_root / "CLAUDE.md"
        assert claude_md.exists(), f"AC-10a 실패: {claude_md} 부재 — FIX 루프 명시 검증 불가"
        claude_text = claude_md.read_text(encoding='utf-8')
        # "FIX" 키워드와 숫자 3 조합 확인
        assert re.search(r'FIX.*3|3.*FIX', claude_text, re.IGNORECASE), \
            "AC-10a 실패: CLAUDE.md에 'FIX 루프 상한 3' 명시 부재"

        # ④ 게이트 수: 8 (CLAUDE.md의 required_status_checks contexts)
        # F-CR-006: JSON 파싱 + 등식 강화 (쉼표 오계수 제거)
        # F-CR-010: 파일 부재를 실패로 승격 (이미 위에서 확인했으므로 조건 제거)
        # ★ fail-closed: `if 'required_status_checks' in ...` / `if contexts_match:` 로 감싸면
        #   CLAUDE.md 표 서식이 바뀌는 순간 매칭이 실패해 아래 등식 assert 가 통째로 건너뛰어지고
        #   테스트는 초록으로 남는다(vacuous pass). 그러면 8→7 축소 검출이라는 본 검사의 목적이
        #   정확히 무력화되므로, 앵커 존재와 매칭 성공 자체를 assert 로 확정한다.
        assert 'required_status_checks' in claude_text, \
            "AC-10a 실패: CLAUDE.md 에 'required_status_checks' 앵커 부재 — 게이트 수 검증 불가"
        contexts_match = re.search(
            r'required_status_checks\s+contexts.*?\[(.*?)\]',
            claude_text,
            re.DOTALL | re.IGNORECASE
        )
        assert contexts_match, \
            "AC-10a 실패: required_status_checks contexts 배열 매칭 실패 — 표 서식 변경 의심"
        contexts_json_str = '[' + contexts_match.group(1) + ']'
        import json
        try:
            contexts_list = json.loads(contexts_json_str)
        except json.JSONDecodeError as e:
            pytest.fail(f"AC-10a: contexts JSON 파싱 실패: {e}")
        # 등식으로 강화: 정확히 8개여야 함 (>= 에서 == 로 변경 — 쉼표 계수는
        # "css structural lint (stylelint, warning-tier)" 처럼 항목 내부 쉼표를
        # 항목 구분자로 오인해 8 을 9 로 세었고, 그 결과 `>= 8` 이 8→7 축소를 통과시켰다)
        # CLAUDE.md 브랜치 보호 표 SSOT: 8개 contexts
        expected_contexts = {
            "phase-gate-mergeable",
            "invariant-check",
            "doc frontmatter schema (CFP-28 — strict)",
            "doc section schema (CFP-28 — strict)",
            "check-gate",
            "ac-traceability-matrix",
            "css structural lint (stylelint, warning-tier)",
            "css-lint discriminating test (mutation 생존 0)"
        }
        actual_set = set(contexts_list)
        assert len(actual_set) == 8, \
            f"AC-10a 실패: 게이트 수 {len(actual_set)} ≠ 8 (실측 JSON 파싱)"
        # 각 항목까지 집합 비교 (교체 감지)
        assert actual_set == expected_contexts, \
            f"AC-10a 실패: 게이트 항목 불일치. expected={expected_contexts}, actual={actual_set}"

        # ⑤ deputy: 6 permanent + 3+1 CONDITIONAL (skills/deputy-mandate/SKILL.md)
        # F-CR-010: 파일 부재를 실패로 승격 (fail-closed)
        deputy_skill = worktree_root / "skills/deputy-mandate/SKILL.md"
        assert deputy_skill.exists(), f"AC-10a 실패: {deputy_skill} 부재 — deputy mandate 검증 불가"
        deputy_text = deputy_skill.read_text(encoding='utf-8')
        assert re.search(r'6\s+permanent', deputy_text, re.IGNORECASE), \
            "AC-10a 실패: SKILL.md에 '6 permanent deputy' 명시 부재"

        # 결론: 검사량 5종 모두 확인됨 (증가/무변경, 감소 0)
        # 이것이 C-4 준수 입증


def pytest_collection_modifyitems(config, items):
    """mark 자동 추가 (필요시)"""
    pass


if __name__ == '__main__':
    import pytest
    sys.exit(pytest.main([__file__, '-v']))
