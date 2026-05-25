"""
CFP-1523 Phase 2 — confluence-ia-tree.yaml legacy_adr_migration_map.rows 148 row inject
ADR-061 §결정 1 외부 .py 파일 의무
ADR-082 §결정 1 — write 전 source verify: rows = migration_map_rows.yaml (verified)
"""

import re

YAML_PATH = "C:/workspace/mclayer/plugin-codeforge-cfp-1523-phase-2/docs/confluence-ia-tree.yaml"
ROWS_PATH = "C:/workspace/mclayer/plugin-codeforge-cfp-1523-phase-2/scripts/migration_map_rows.yaml"

# rows yaml 읽기 (raw text로 처리 — PyYAML dump 결과를 indent 맞춰 inject)
import yaml

with open(ROWS_PATH, encoding="utf-8") as f:
    rows_data = yaml.safe_load(f)

rows = rows_data["legacy_adr_migration_map"]["rows"]
print(f"Rows to inject: {len(rows)}")

# rows를 yaml 형식 문자열로 직렬화 (indent=4, 각 row 앞 '    - ')
def row_to_yaml_str(row, indent=4):
    lines = []
    prefix = " " * indent
    lines.append(f"{prefix}- page_id: {row['page_id']}")
    # title — 특수문자 처리를 위해 double-quoted
    title_escaped = str(row['title']).replace('"', '\\"')
    lines.append(f"{prefix}  title: \"{title_escaped}\"")
    lines.append(f"{prefix}  source_file: \"{row['source_file']}\"")
    if row['category'] is None:
        lines.append(f"{prefix}  category: null")
    else:
        lines.append(f"{prefix}  category: \"{row['category']}\"")
    lines.append(f"{prefix}  previous_parent_id: {row['previous_parent_id']}")
    lines.append(f"{prefix}  new_parent_id: {row['new_parent_id']}")
    lines.append(f"{prefix}  type: {row['type']}")
    lines.append(f"{prefix}  cascade_order: {row['cascade_order']}")
    return "\n".join(lines)

rows_yaml_block = "\n".join(row_to_yaml_str(r) for r in rows)

# confluence-ia-tree.yaml 읽기
with open(YAML_PATH, encoding="utf-8") as f:
    content = f.read()

# 현재 '  rows: []' 를 populated rows 로 교체
OLD_PATTERN = r'  rows: \[\]  # Phase 1 PR = empty skeleton, Phase 2 PR = 148 row append \(F-DR-001 — ADR 117 \+ IPC 30 \+ Consumer Guide 1\)'
NEW_CONTENT = f"  rows:  # Phase 2 PR — {len(rows)} row populated (ADR {sum(1 for r in rows if r['type']=='adr')} + IPC {sum(1 for r in rows if r['type']=='ipc')} + Consumer Guide {sum(1 for r in rows if r['type']=='consumer-guide')}, F-DR-001 ground truth, CFP-1523 Phase 2 cascade execute 2026-05-25T05:44+09:00 KST)\n{rows_yaml_block}"

new_content = re.sub(OLD_PATTERN, NEW_CONTENT, content)

if new_content == content:
    print("ERROR: Pattern not matched — rows injection failed")
    exit(1)

with open(YAML_PATH, "w", encoding="utf-8") as f:
    f.write(new_content)

print(f"confluence-ia-tree.yaml updated: {len(rows)} rows injected.")

# sanity check
with open(YAML_PATH, encoding="utf-8") as f:
    updated = f.read()

row_count = updated.count("  cascade_order:")
print(f"Sanity check — cascade_order occurrences: {row_count} (expected: {len(rows)})")
