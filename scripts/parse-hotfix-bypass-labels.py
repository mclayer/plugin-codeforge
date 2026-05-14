#!/usr/bin/env python3
"""Parse hotfix-bypass:* family entries from label-registry-v2.md §3 yaml block.

Interface (Change Plan §4.1 CFP-598):
  argv[1]: registry-md-path (str)
  stdout:  name<TAB>color<TAB>description (1 line per hotfix-bypass:* entry)
  stderr:  error messages (PARSE_ERROR / NO_ENTRIES / FILE_NOT_FOUND / INVALID_ENTRY)
  Exit codes:
    0 = success (1+ entry emitted)
    1 = parse error (PyYAML missing / yaml.YAMLError / schema mismatch / invalid entry)
    2 = no entries found (drift sentinel — registry 안 0 hotfix-bypass:* row)
    3 = file missing / argv mismatch

Security (Story §7.5 CFP-598):
  - yaml.safe_load 의무 (never yaml.load — RCE 차단)
  - isinstance guard (str / list / dict type coercion)
  - Path.is_file() (symlink attack 차단)
  - stderr only for error messages (stdout contract 보호)

Usage:
  python scripts/parse-hotfix-bypass-labels.py docs/inter-plugin-contracts/label-registry-v2.md
"""

import sys
import re
import io
from pathlib import Path

# Windows cp949 환경에서 한글/특수문자 포함 description stdout 출력 보장
# (bash hotfix-bypass dynamic read 분기가 UTF-8 parse 의무)
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf_8"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")


def main() -> int:
    # argv 검사
    if len(sys.argv) < 2:
        print("PARSE_ERROR: argv[1] registry-md-path 누락", file=sys.stderr)
        return 3

    registry_path = Path(sys.argv[1])

    # 파일 존재 확인 (symlink → real file 모두 포함)
    if not registry_path.is_file():
        print(f"FILE_NOT_FOUND: {registry_path}", file=sys.stderr)
        return 3

    # PyYAML preflight
    try:
        import yaml
    except ImportError:
        print("PARSE_ERROR: PyYAML 미설치 ('pip install pyyaml' 후 재실행)", file=sys.stderr)
        return 1

    # 파일 읽기
    try:
        content = registry_path.read_text(encoding="utf-8")
    except OSError as e:
        print(f"PARSE_ERROR: 파일 읽기 실패 — {e}", file=sys.stderr)
        return 1

    # §3 yaml block 추출 (```yaml ... ``` fence)
    # label-registry-v2.md 의 §3 항목은 ```yaml\nlabels:\n... ``` 블록 1개
    yaml_block_pattern = re.compile(r"```yaml\s*\n(.*?)```", re.DOTALL)
    matches = yaml_block_pattern.findall(content)

    if not matches:
        print("PARSE_ERROR: ```yaml ... ``` 블록 미검출", file=sys.stderr)
        return 1

    # 첫 번째 yaml 블록 사용 (§3 항목 블록)
    yaml_text = matches[0]

    try:
        data = yaml.safe_load(yaml_text)
    except yaml.YAMLError as e:
        print(f"PARSE_ERROR: yaml.safe_load 실패 — {e}", file=sys.stderr)
        return 1

    # schema 확인
    if not isinstance(data, dict):
        print("PARSE_ERROR: yaml block root 가 dict 아님", file=sys.stderr)
        return 1

    labels = data.get("labels")
    if not isinstance(labels, list):
        print("PARSE_ERROR: 'labels' key 부재 또는 list 아님", file=sys.stderr)
        return 1

    # hotfix-bypass:* entry 필터
    results = []
    for entry in labels:
        if not isinstance(entry, dict):
            continue
        category = entry.get("category")
        if not isinstance(category, str):
            continue
        if category != "hotfix-bypass":
            continue

        # 필수 필드 검증
        name = entry.get("name")
        color = entry.get("color")
        description = entry.get("description", "")

        if not isinstance(name, str) or not name:
            print(f"INVALID_ENTRY: name 필드 누락 또는 비문자열 — entry: {entry}", file=sys.stderr)
            return 1
        if not isinstance(color, str) or not color:
            print(f"INVALID_ENTRY: color 필드 누락 또는 비문자열 — name={name}", file=sys.stderr)
            return 1
        if not isinstance(description, str):
            print(f"INVALID_ENTRY: description 필드가 문자열 아님 — name={name}", file=sys.stderr)
            return 1

        # name prefix 재확인 (category hotfix-bypass 이지만 name 불일치 방어)
        if not name.startswith("hotfix-bypass:"):
            print(f"INVALID_ENTRY: category=hotfix-bypass 이나 name prefix 불일치 — name={name}", file=sys.stderr)
            return 1

        results.append((name, color, description))

    if not results:
        print("NO_ENTRIES: registry 안 hotfix-bypass:* category 0 row (drift sentinel)", file=sys.stderr)
        return 2

    # stdout 출력 (name\tcolor\tdescription)
    for name, color, description in results:
        print(f"{name}\t{color}\t{description}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
