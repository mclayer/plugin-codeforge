"""
workflow_story_init_project_config_story_ssot_repo.py
CFP-2252 (S4) / ADR-013 Amendment 7 — TARGET_REPO 파라미터화 (하드코딩 제거).

story-init.yml 의 project_config step 에서 yq 부재 시 fallback 으로 호출.
project.yaml `github.story_ssot_repo` field 를 read — 부재 시 template default
"mclayer/codeforge-internal-docs" 출력 (확장-only — 축소/제거 금지,
선례 ADR-024 Amd2 §결정 A + ADR-026 Amd4 §결정 6, mechanism ADR-116 cross-ref).

Usage (via workflow YAML run: block):
  story_ssot_repo=$(CFG_PATH="$cfg" python3 \
    "${GITHUB_WORKSPACE}/scripts/lib/workflow_story_init_project_config_story_ssot_repo.py")
  echo "story_ssot_repo=$story_ssot_repo" >> "$GITHUB_OUTPUT"

env: block must provide:
  CFG_PATH: path to project.yaml (e.g. ".claude/_overlay/project.yaml")

부재 시 exit 0 + default 출력 (fail-closed 아님 — default 보존이 의도, 확장-only invariant).
기존 _project_config_name.py / _key_prefix.py 패턴 답습 (in_github block 단순 parser, stdlib only).
"""
import re
import sys
import os

# Windows cp949 stdout encoding 차단 (CFP-1393 F8-FU / ADR-061 standardize)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# template default (확장-only — 축소/제거 금지, ADR-013 Amd 7 / ADR-024 Amd2 §결정 A)
DEFAULT_STORY_SSOT_REPO = "mclayer/codeforge-internal-docs"


def main() -> None:
    path = os.environ.get("CFG_PATH", ".claude/_overlay/project.yaml")
    in_github = False
    try:
        fh = open(path, encoding="utf-8")
    except OSError:
        # cfg 부재 = default 보존 (확장-only invariant — 부재 시 mclayer 운영 default)
        print(DEFAULT_STORY_SSOT_REPO)
        return
    with fh:
        for raw in fh:
            line = raw.rstrip("\n")
            if re.match(r"^[A-Za-z_][\w-]*:\s*$", line):
                in_github = line.split(":", 1)[0] == "github"
                continue
            if in_github:
                m = re.match(r"^\s{2}story_ssot_repo:\s*(.*?)\s*$", line)
                if m:
                    val = m.group(1).strip().strip('"').strip("'")
                    # 빈 값 = default 보존 (override 만 허용, 축소 불가)
                    print(val if val else DEFAULT_STORY_SSOT_REPO)
                    return
    # field 부재 = default 보존
    print(DEFAULT_STORY_SSOT_REPO)


if __name__ == "__main__":
    main()
