"""
scripts/lib/check_stray_scratch_leak.py
CFP-2092 — stray-scratch-leak SessionStart 안전망 SSOT

기능:
  SessionStart 훅에서 호출 — 홈 루트(~)에 남아있는 codeforge 스크래치 의심
  파일/디렉터리를 advisory 로 경고 (항상 exit 0, non-blocking).
  repo-confinement 가드가 누락된 과거 누출분 또는 가드 우회분을 정리하도록
  사용자에게 환기 (재발 방지 2중 안전망).

  탐지 대상:
    - FILE_GLOBS — `.codeforge-tmp-*`, `.tmp-*`, `*-story.md`, story-payload*.json 등
      (디렉터리 아닌 항목만).
    - DIR_GLOBS — `.tmp` 디렉터리.
    - git-clone 휴리스틱 — `^[a-z]{2,8}[0-9]+-.+` (예: cfp2092-foo) 이름 +
      내부 `.git` 존재 디렉터리.

책임 경계:
  - 책임: 홈 루트 누출 의심 항목을 stderr 경고로 환기 (advisory).
  - 비책임: 자동 삭제·차단 없음 (오탐 가능 → 사용자 판단). 항상 exit 0.

Bypass:
  BYPASS_STRAY_SCRATCH_LEAK=1 — exit 0 (경고 없음).
"""

import fnmatch
import os
import re
import sys

# Windows cp949 stdout/stderr encoding 차단 (ADR-061 standardize)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

SCRIPT_NAME = "stray-scratch-leak"
BYPASS_ENV = "BYPASS_STRAY_SCRATCH_LEAK"

# repo 밖 임시 산출물 유일 허용 경로
SCRATCH_HINT = "~/.claude/codeforge-scratch/"

# 홈 루트 누출 의심 파일 glob (디렉터리 아닌 항목만 매칭)
FILE_GLOBS = [
    ".codeforge-tmp-*",
    ".tmp-*",
    "*-story.md",
    "story-payload*.json",
    "story_new.md",
    "story-cfp-*.md",
    "cfp*-story.md",
    "origin-ADR-*.md",
    "origin-CHANGELOG.md",
    "plan-codeforge-*.md",
    "wrapper-claude.md",
]

# 홈 루트 누출 의심 디렉터리 glob
DIR_GLOBS = [".tmp"]

# git-clone 휴리스틱: 이름이 `<prefix><번호>-<slug>` 형태 + 내부 .git 존재
_CLONE_DIR_RE = re.compile(r"^[a-z]{2,8}[0-9]+-.+")


def main():
    if os.environ.get(BYPASS_ENV) == "1":
        sys.exit(0)

    home = os.path.expanduser("~")
    try:
        entries = os.listdir(home)
    except OSError:
        sys.exit(0)

    hits = []
    for name in entries:
        full = os.path.join(home, name)
        is_dir = os.path.isdir(full)

        if not is_dir:
            # 파일 glob 매칭
            if any(fnmatch.fnmatch(name, g) for g in FILE_GLOBS):
                hits.append(name)
            continue

        # 디렉터리 — DIR_GLOBS 또는 git-clone 휴리스틱
        if any(fnmatch.fnmatch(name, g) for g in DIR_GLOBS):
            hits.append(name)
            continue
        if _CLONE_DIR_RE.match(name) and os.path.isdir(os.path.join(full, ".git")):
            hits.append(name)

    if not hits:
        sys.exit(0)

    # dedup + 정렬 (결정적 출력)
    hits = sorted(set(hits))

    print(
        f"[{SCRIPT_NAME}] WARNING: 홈 루트에 codeforge 스크래치 의심 {len(hits)}개 (CFP-2092):",
        file=sys.stderr,
    )
    for name in hits:
        print(f"  ~/{name}", file=sys.stderr)
    print(
        f"[{SCRIPT_NAME}] 정리: 정식 repo 반영 여부 확인 후 삭제하세요.\n"
        f"[{SCRIPT_NAME}] repo 밖 임시 산출물은 {SCRATCH_HINT} 아래에만 두세요 (유일 허용 경로).\n"
        f"[{SCRIPT_NAME}] 오탐이면 bypass: {BYPASS_ENV}=1 환경변수 설정.",
        file=sys.stderr,
    )
    sys.exit(0)


if __name__ == "__main__":
    main()
