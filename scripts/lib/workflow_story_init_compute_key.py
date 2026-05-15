"""
workflow_story_init_compute_key.py
CFP-478 Phase 2 sub-PR b — ADR-061 Amendment 1 §결정 1.B
Block #17: story-init.yml lines 131-158 (key/slug/title_clean computation)

CFP-671 / ADR-036 Amendment 1: title regex precedence + Issue# fallback.
Title `[<PREFIX>-<N>]` or `<PREFIX>-<N>` pattern matched + prefix matched → title KEY 우선.
Title pattern absent OR prefix MISMATCH → Issue # fallback (race-free guarantee 보존).

Usage (via workflow YAML run: block):
  PYOUT=$(python3 "${GITHUB_WORKSPACE}/scripts/lib/workflow_story_init_compute_key.py")
  KEY=$(printf '%s' "$PYOUT" | sed -n '1p')
  SLUG=$(printf '%s' "$PYOUT" | sed -n '2p')
  TITLE_CLEAN=$(printf '%s' "$PYOUT" | sed -n '3p')
  echo "key=$KEY" >> "$GITHUB_OUTPUT"
  echo "slug=$SLUG" >> "$GITHUB_OUTPUT"
  {
    echo "title_clean<<TITLE_EOF"
    printf '%s\n' "$TITLE_CLEAN"
    echo "TITLE_EOF"
  } >> "$GITHUB_OUTPUT"

env: block must provide:
  ISSUE_TITLE: ${{ github.event.issue.title }}
  PREFIX: ${{ steps.project_config.outputs.story_key_prefix }}
  ISSUE_NUMBER: ${{ github.event.issue.number }}
"""
import os
import re


def main() -> None:
    title = os.environ.get("ISSUE_TITLE", "")
    prefix = os.environ.get("PREFIX", "")
    issue_number = os.environ.get("ISSUE_NUMBER", "")

    # [STORY] prefix 제거 후 title clean
    title_clean = re.sub(r"^\[STORY\]\s*", "", title).strip()

    # Title pattern `[<PREFIX>-<N>]` or `<PREFIX>-<N>` 우선 추출
    m = re.search(r'\[?([A-Z]+-\d+)\]?', title_clean)
    key_from_title = m.group(1) if m else ""

    # Prefix guard — cross-project KEY injection 차단
    if key_from_title and key_from_title.startswith(prefix + "-"):
        key = key_from_title
    else:
        # Fallback to Issue # — ADR-036 결정 1 race-free guarantee 보존
        key = f"{prefix}-{issue_number}"

    # slug computation (CFP-596 base 동일)
    slug = re.sub(r"[^A-Za-z0-9가-힣]+", "-", title_clean, flags=re.UNICODE)
    slug = slug.strip("-")[:40].rstrip("-")

    print(key)
    print(slug)
    print(title_clean)


if __name__ == "__main__":
    main()
