"""
workflow_story_init_render_story.py
CFP-478 Phase 2 sub-PR b — ADR-061 Amendment 1 §결정 1.B
Block #15: story-init.yml lines 274-353 (Story file content rendering + base64 encode)

Renders Story file content and writes base64-encoded result to stdout.
Shell responsibility: capture stdout + write to $GITHUB_OUTPUT as content_b64.

Usage (via workflow YAML run: block):
  STORY_CONTENT=$(python3 "${GITHUB_WORKSPACE}/scripts/lib/workflow_story_init_render_story.py")
  CONTENT_B64=$(printf '%s' "$STORY_CONTENT" | base64 -w 0)
  echo "content_b64=$CONTENT_B64" >> "$GITHUB_OUTPUT"

env: block must provide:
  KEY: ${{ steps.key.outputs.key }}
  TITLE_CLEAN: ${{ steps.key.outputs.title_clean }}
  REQUIREMENT: ${{ steps.parse.outputs.requirement }}
  ISSUE_NUMBER: ${{ github.event.issue.number }}
  GITHUB_REPOSITORY: ${{ github.repository }}
"""
import io
import os
import sys


def main() -> None:
    # Ensure UTF-8 stdout regardless of platform encoding (GitHub Actions Linux / Windows local)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    key = os.environ.get("KEY", "")
    title_clean = os.environ.get("TITLE_CLEAN", "")
    requirement = os.environ.get("REQUIREMENT", "")
    issue_number = os.environ.get("ISSUE_NUMBER", "")
    github_repository = os.environ.get("GITHUB_REPOSITORY", "")

    content = f"""---
story_key: {key}
story_issues:
  - repo: {github_repository}
    number: {issue_number}
status: phase:요구사항
---

# {key}: {title_clean}

- **Issue**: #{issue_number}
- **Status**: phase:요구사항

## 1. 사용자 요구사항 (verbatim — Phase 2 후속 CFP 까지 CODEOWNERS manual review 로 변경 차단)

{requirement}

## 2. 도메인 해석

*(DomainAgent 작성 예정 — placeholder)*

## 3. 관련 ADR

*(RequirementsPL 작성 예정 — placeholder)*

## 4. 관련 코드 경로

*(RequirementsPL 작성 예정 — placeholder)*

## 5. 요구사항 확장 해석

*(RequirementsAnalyst 작성 예정 — placeholder)*

## 6. 외부 지식 배경

*(Researcher 작성 예정 — placeholder)*

## 7. 설계 서사

*(Architect 작성 예정 — placeholder)*

## 8. 개발 서사

*(DeveloperPL 작성 예정 — Phase 2 PR에서)*

## 9. 품질 게이트 이력

*(Review/Test PL 작성 예정 — Phase 2 PR에서)*

## 10. FIX Ledger

| Iter | 시각 | 레인 | 트리거 | 원인 판정 | 재실행 범위 | RESET? |
|------|------|------|--------|-----------|-------------|--------|

*(FIX 발생 시 append)*

## 11. 회고

*(PMOAgent 작성 예정 — Story 완료 시)*
"""
    sys.stdout.write(content)


if __name__ == "__main__":
    main()
