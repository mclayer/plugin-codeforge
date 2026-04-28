#!/usr/bin/env bash
# CFP-33 (ζ arc F2) — Label registry ↔ bootstrap-labels.sh sync check
#
# 검사: docs/inter-plugin-contracts/label-registry-v1.md 의 ## 3. 항목 yaml block ↔
#       scripts/bootstrap-labels.sh --dry-run 출력 동기 여부
#
# 양방향 검증:
#   1. registry 의 모든 label 이 script 에 존재 (name + color 일치)
#   2. script 의 모든 label 이 registry 에 존재
#   3. category 분류 sanity (phase: single_active=true, 기타: false)
#
# Strict 모드: drift 발견 시 exit 1 → CI 차단.
set -euo pipefail
cd "$(dirname "$0")/.."

python3 <<'PY'
import sys, re, subprocess
from pathlib import Path

try:
    import yaml
except ImportError:
    print("⚠ check-label-registry: pyyaml 미설치 — skip", file=sys.stderr)
    sys.exit(0)

REGISTRY = Path("docs/inter-plugin-contracts/label-registry-v1.md")
BOOTSTRAP = Path("scripts/bootstrap-labels.sh")

if not REGISTRY.exists():
    print(f"::error::label-registry-v1.md 부재")
    sys.exit(1)

if not BOOTSTRAP.exists():
    print(f"::error::bootstrap-labels.sh 부재")
    sys.exit(1)

# 1. Registry yaml 추출
text = REGISTRY.read_text(encoding="utf-8")
m = re.search(
    r"^## 3\. 항목\s*\n(?:.*?\n)*?```yaml\n(?P<yaml>.*?)\n```",
    text,
    re.MULTILINE | re.DOTALL,
)
if not m:
    print(f"::error::{REGISTRY}: ## 3. 항목 fenced yaml 블록 미발견")
    sys.exit(1)

try:
    data = yaml.safe_load(m.group("yaml"))
except Exception as e:
    print(f"::error::{REGISTRY}: yaml parse 실패 ({type(e).__name__}: {e})")
    sys.exit(1)

if not isinstance(data, dict) or "labels" not in data or not isinstance(data["labels"], list):
    print(f"::error::{REGISTRY}: 'labels:' list 누락")
    sys.exit(1)

registry_labels = {}  # name -> {color, category, single_active, description}
for entry in data["labels"]:
    if not isinstance(entry, dict) or "name" not in entry:
        print(f"::error::{REGISTRY}: invalid label entry — {entry!r}")
        sys.exit(1)
    registry_labels[entry["name"]] = entry

# 2. Bootstrap script --dry-run 호출
try:
    proc = subprocess.run(
        ["bash", "scripts/bootstrap-labels.sh", "--dry-run"],
        capture_output=True, text=True, encoding="utf-8", check=True
    )
except subprocess.CalledProcessError as e:
    print(f"::error::bootstrap-labels.sh --dry-run 실패: {e.stderr}")
    sys.exit(1)

script_labels = {}  # name -> {color, description}
for line in proc.stdout.strip().splitlines():
    parts = line.split("\t")
    if len(parts) != 3:
        continue
    name, color, desc = parts
    script_labels[name] = {"color": color, "description": desc}

errors = []

# 3. 양방향 set 비교
reg_names = set(registry_labels.keys())
scr_names = set(script_labels.keys())

missing_in_script = reg_names - scr_names
extra_in_script = scr_names - reg_names
if missing_in_script:
    errors.append(f"registry 에는 있으나 bootstrap-labels.sh 에 없음: {sorted(missing_in_script)}")
if extra_in_script:
    errors.append(f"bootstrap-labels.sh 에는 있으나 registry 에 없음: {sorted(extra_in_script)}")

# 4. color 일치
for name in reg_names & scr_names:
    reg_color = str(registry_labels[name].get("color", "")).strip()
    scr_color = script_labels[name]["color"].strip()
    if reg_color.lower() != scr_color.lower():
        errors.append(f"{name}: color drift — registry={reg_color}, script={scr_color}")

# 5. single_active invariant — phase 카테고리만 true
for name, entry in registry_labels.items():
    cat = entry.get("category")
    sa = entry.get("single_active")
    if cat == "phase" and sa is not True:
        errors.append(f"{name}: phase 카테고리는 single_active=true 필요 — got {sa!r}")
    elif cat != "phase" and sa is True:
        errors.append(f'{name}: phase 외 카테고리는 single_active=false 필요 — got True (category="{cat}")')

if errors:
    print(f"::error::CFP-33 label-registry sync (STRICT): {len(errors)} 건")
    for e in errors:
        print(f"  - {e}")
    print("strict 모드 — bootstrap-labels.sh ↔ label-registry-v1.md drift 시 PR 차단.")
    sys.exit(1)

print(f"✓ CFP-33 label-registry: {len(reg_names)} label 양방향 sync (registry ↔ bootstrap-labels.sh)")
PY

echo ""
echo "(check-label-registry: strict 모드 — registry ↔ bootstrap-labels.sh 양방향 sync)"
