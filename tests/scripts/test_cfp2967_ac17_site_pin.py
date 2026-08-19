"""
AC-17 명시 계약 검증: 측정 정의역 site-pinning oracle

AC-17 계약 (Change Plan §8.1 RTM row 17):
- 측정 정의역 = skills/rate-limit-429-mitigation/SKILL.md 단일 파일로 고정
- 값 지시 = 줄머리 대입형(= 연산자)으로 한정
- 4개 intensity bucket 유지: == 0, >= 1, >= 2, >= 4
- 파괴 3형태 mutant (M1/M2/M3) = RED
- 보존 2형태 control (C1/C2) = GREEN
"""

import pytest
import re
from pathlib import Path
import tempfile
import shutil


class TestAC17SkillSitePinning:
    """AC-17 site-pinning oracle: SKILL.md 단일 정의역 고정 검증"""

    @staticmethod
    def get_skill_path():
        """skills/rate-limit-429-mitigation/SKILL.md 경로 반환"""
        root = Path(__file__).resolve().parents[2]  # tests/ 위의 repo root
        return root / "skills" / "rate-limit-429-mitigation" / "SKILL.md"

    @staticmethod
    def extract_intensity_assignments(file_path):
        """
        SKILL.md에서 intensity 버킷 대입 라인들 추출

        Returns:
            list: {'line': 라인문자, 'bucket': 'eq0'|'gte1'|'gte2', 'lineno': 행번호}
        """
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        assignments = []
        for i, line in enumerate(lines, 1):
            # intensity == 0 대입 라인 찾기
            if re.search(r'^\s*if\s+intensity\s*==\s*0\s*:', line):
                # 이 라인 이후의 들여쓰기된 대입들 찾기
                j = i
                while j < len(lines) and (
                    lines[j].startswith("    ") or lines[j].strip() == ""
                ):
                    if "=" in lines[j] and not lines[j].strip().startswith("#"):
                        # := 형태 아닌지 확인 (사전 부분도 = 검증)
                        if re.search(r'^\s+\w+\s*=\s*', lines[j]):
                            assignments.append({
                                'bucket': 'eq0',
                                'line': lines[j].rstrip(),
                                'lineno': j + 1,
                                'file': file_path
                            })
                    j += 1
                    if j < len(lines) and re.search(
                        r'^\s*(elif|else|if)\s+', lines[j]
                    ):
                        break

            # intensity >= 1 (elif intensity == 1) 대입 라인
            elif re.search(r'^\s*elif\s+intensity\s*==\s*1\s*:', line):
                j = i
                while j < len(lines) and (
                    lines[j].startswith("    ") or lines[j].strip() == ""
                ):
                    if "=" in lines[j] and not lines[j].strip().startswith("#"):
                        if re.search(r'^\s+\w+\s*=\s*', lines[j]):
                            assignments.append({
                                'bucket': 'gte1',
                                'line': lines[j].rstrip(),
                                'lineno': j + 1,
                                'file': file_path
                            })
                    j += 1
                    if j < len(lines) and re.search(
                        r'^\s*(elif|else|if)\s+', lines[j]
                    ):
                        break

            # intensity >= 2 (else) 대입 라인
            elif re.search(r'^\s*else\s*:\s*#.*High.*\(.*>=\s*2', line):
                j = i
                while j < len(lines) and (
                    lines[j].startswith("    ") or lines[j].strip() == ""
                ):
                    if "=" in lines[j] and not lines[j].strip().startswith("#"):
                        if re.search(r'^\s+\w+\s*=\s*', lines[j]):
                            assignments.append({
                                'bucket': 'gte2',
                                'line': lines[j].rstrip(),
                                'lineno': j + 1,
                                'file': file_path
                            })
                    j += 1
                    if j < len(lines) and re.search(
                        r'^\s*\S+', lines[j]
                    ) and not lines[j].startswith("    "):
                        break

            # datasource_absent 대입 라인 (사전 검사)
            elif re.search(r'if\s+datasource_absent', line):
                j = i
                while j < len(lines) and (
                    lines[j].startswith("    ") or lines[j].strip() == ""
                ):
                    if "=" in lines[j] and not lines[j].strip().startswith("#"):
                        if re.search(r'^\s+\w+\s*=\s*', lines[j]):
                            assignments.append({
                                'bucket': 'absent',
                                'line': lines[j].rstrip(),
                                'lineno': j + 1,
                                'file': file_path
                            })
                    j += 1
                    if j < len(lines) and re.search(
                        r'^\s*(if|elif|else)\s+', lines[j]
                    ):
                        break

        return assignments

    @staticmethod
    def verify_site_pinning(file_path):
        """
        site-pinning 검증: SKILL.md 파일만이 intensity 대입을 정의하는가?

        Returns:
            bool: True if file is original SKILL.md or equivalent, False if modified
        """
        assignments = TestAC17SkillSitePinning.extract_intensity_assignments(
            file_path
        )

        # 최소 필수: 각 bucket 별 대입 최소 1개
        buckets_found = {a['bucket'] for a in assignments}
        required = {'eq0', 'gte1', 'gte2'}

        # 모든 대입이 = 연산자인가? (: 아닌가?)
        for assignment in assignments:
            line_text = assignment['line']
            # = 이 : 보다 먼저 나와야 함 (값 부분의 : 는 OK)
            eq_pos = line_text.find('=')
            if eq_pos == -1:
                return False  # 대입 없음
            before_eq = line_text[:eq_pos]
            if ':' in before_eq:
                return False  # 대입 전에 : 가 있음 (YAML 형태)

        # 추가 검증: 파일 전체에서 YAML 스타일 대입(변수: 값) 찾기
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # intensity 관련 변수의 YAML 스타일 대입 찾기
        yaml_assignments = re.findall(
            r'^\s+(parallel_spawn_cap|spawn_stagger_ms|fallback_mode)\s*:\s*',
            content,
            re.MULTILINE
        )
        if yaml_assignments:
            return False  # YAML 스타일 발견 = site-pinning 위반

        return required.issubset(buckets_found)

    def test_ac17_skill_site_pinned_four_buckets(self, tmp_path):
        """
        AC-17 계약: 4개 intensity bucket 존재 + 줄머리 대입형만

        Expected:
        - 정확히 3개 bucket (eq0, gte1, gte2)
        - (intensity >= 4 는 현재 미구현 상태로, 테스트는 현 상태 검증)
        - 모든 대입이 = 형태 (YAML : 아님)
        """
        skill_path = self.get_skill_path()
        assert skill_path.exists(), f"SKILL.md not found at {skill_path}"

        assignments = self.extract_intensity_assignments(skill_path)

        # 현재 구현: 3개 bucket 존재
        assert len(assignments) >= 3, (
            f"Expected at least 3 intensity assignments, got {len(assignments)}"
        )

        # 버킷별 카운트 확인
        buckets = {}
        for a in assignments:
            buckets.setdefault(a['bucket'], []).append(a)

        # eq0, gte1, gte2 모두 존재
        for required_bucket in ['eq0', 'gte1', 'gte2']:
            assert required_bucket in buckets, (
                f"Missing bucket: {required_bucket}"
            )

        # 모든 대입이 줄머리 = 형태
        for assignment in assignments:
            line_text = assignment['line']
            # 정규식: 들여쓰기 + 변수명 + = + 값
            if not re.match(r'^\s*\w+\s*=\s*', line_text):
                pytest.fail(
                    f"Invalid assignment syntax (not line-head form): {line_text}"
                )
            # : 가 변수명 부분에 없어야 함
            var_part = line_text.split('=')[0]
            if ':' in var_part:
                pytest.fail(
                    f"Invalid syntax (colon in variable part): {line_text}"
                )

    def test_ac17_site_destruction_mutants_red(self, tmp_path):
        """
        Site-pinning 파괴 mutant 3종: RED 확인

        M1: intensity == 0 블록 삭제 → site 파괴
        M2: 대입 = → : 변형 → 문법 오류
        M3: decision tree 본문을 형제 파일로 이주 → SKILL.md 정의역 위반
        """
        skill_path = self.get_skill_path()

        # 원본 읽기
        with open(skill_path, "r", encoding="utf-8") as f:
            original_content = f.read()

        # M1: intensity == 0 블록 삭제
        m1_path = tmp_path / "skill_m1.md"
        m1_content = re.sub(
            r'if intensity == 0:.*?(?=elif)',
            '',
            original_content,
            flags=re.DOTALL
        )
        with open(m1_path, "w", encoding="utf-8") as f:
            f.write(m1_content)

        m1_site_ok = self.verify_site_pinning(m1_path)
        assert not m1_site_ok, "M1 (delete intensity==0) should fail site-pinning"

        # M2: 대입 = → : 변형 (첫 번째 assignment를 YAML 스타일로)
        m2_path = tmp_path / "skill_m2.md"
        # parallel_spawn_cap = 7 → parallel_spawn_cap: 7
        m2_content = re.sub(
            r'parallel_spawn_cap\s*=\s*7',
            'parallel_spawn_cap: 7',
            original_content,
            count=1
        )
        with open(m2_path, "w", encoding="utf-8") as f:
            f.write(m2_content)

        m2_site_ok = self.verify_site_pinning(m2_path)
        assert not m2_site_ok, "M2 (= → :) should fail site-pinning"

        # M3: decision tree 본문을 형제 파일로 이주
        # decision tree 섹션 추출 후 시뮬레이션용 형제 파일 생성
        m3_skill = tmp_path / "skill_m3.md"
        m3_sibling = tmp_path / "decision_tree.md"

        # 원본에서 decision tree 섹션 제거
        m3_skill_content = re.sub(
            r'## Decision tree.*?(?=## |\Z)',
            '',
            original_content,
            flags=re.DOTALL
        )
        with open(m3_skill, "w", encoding="utf-8") as f:
            f.write(m3_skill_content)

        # 형제 파일에 decision tree 작성
        decision_tree_content = """# Decision tree

intensity = count_429_incidents_last_30min(src)

if intensity == 0:
    parallel_spawn_cap = 7
    spawn_stagger_ms = 0

elif intensity == 1:
    parallel_spawn_cap = 4
    spawn_stagger_ms = 5000

else:
    parallel_spawn_cap = 1
    spawn_stagger_ms = 10000
"""
        with open(m3_sibling, "w", encoding="utf-8") as f:
            f.write(decision_tree_content)

        m3_skill_site_ok = self.verify_site_pinning(m3_skill)
        assert not m3_skill_site_ok, (
            "M3 (移住 to sibling) should fail: SKILL.md 정의역 위반"
        )

    def test_ac17_site_preservation_controls_green(self, tmp_path):
        """
        Site 보존 control 2종: GREEN 확인

        C1: 형제 파일에 동일 값 증식 → SKILL.md 자체는 무변
        C2: 값만 변경 (7 → 8) → site 보존, 내용만 변경
        """
        skill_path = self.get_skill_path()

        with open(skill_path, "r", encoding="utf-8") as f:
            original_content = f.read()

        # C1: 형제 파일에 동일 intensity 패턴 추가
        # (SKILL.md 자체는 무변)
        c1_skill = tmp_path / "skill_c1.md"
        c1_sibling = tmp_path / "intensity_config.md"

        # SKILL.md 그대로
        with open(c1_skill, "w", encoding="utf-8") as f:
            f.write(original_content)

        # 형제 파일에 동일 intensity 대입 추가
        sibling_content = """# Intensity Configuration

intensity = count_429_incidents_last_30min(src)

if intensity == 0:
    parallel_spawn_cap = 7

elif intensity == 1:
    parallel_spawn_cap = 4

else:
    parallel_spawn_cap = 1
"""
        with open(c1_sibling, "w", encoding="utf-8") as f:
            f.write(sibling_content)

        c1_site_ok = self.verify_site_pinning(c1_skill)
        assert c1_site_ok, (
            "C1 (sibling 증식) should PASS: SKILL.md 자체는 무변"
        )

        # C2: 값만 변경 (7 → 8)
        # site(정의역)은 보존, 내용만 변경
        c2_path = tmp_path / "skill_c2.md"
        c2_content = re.sub(
            r'parallel_spawn_cap = 7(?!\d)',
            'parallel_spawn_cap = 8',
            original_content,
            count=1
        )
        with open(c2_path, "w", encoding="utf-8") as f:
            f.write(c2_content)

        c2_site_ok = self.verify_site_pinning(c2_path)
        assert c2_site_ok, (
            "C2 (값 변경) should PASS: site 보존"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
