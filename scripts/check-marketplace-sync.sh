#!/usr/bin/env bash
# CFP-34 (ζ arc F3) — Marketplace mirrored 필드 drift detection
#
# 검사: .claude-plugin/plugin.json 의 mirrored 필드 (name, version, description, author)
#       vs mclayer/marketplace/.claude-plugin/marketplace.json 의 plugins[name=<local>] entry
#
# CFP-24 marketplace sync 정책의 자동 enforcement.
# Codex round 2 조건 #4 직접 대응: lane plugin 추출 4개 임계점 전 sync 자동화 필수.
#
# Behavior:
#   - gh CLI 가용 + auth 가능 시: marketplace.json 원격 fetch + 비교
#   - gh 미설치 또는 미인증 시: warn-skip (로컬 dev 환경 — CI는 항상 가용)
#   - drift 발견 시 exit 1 + diff 출력
#
# Note: codeforge-review 등 외부 plugin 은 본 lint scope 밖 (각 plugin repo 의 자체 CI).
#       본 lint 는 LOCAL repo 의 plugin.json 만 검증.
set -uo pipefail
cd "$(dirname "$0")/.."

# gh 가용성 체크
if ! command -v gh >/dev/null 2>&1; then
    echo "⚠ check-marketplace-sync: gh CLI 미설치 — skip (CI에서 검증)"
    exit 0
fi

if ! gh auth status >/dev/null 2>&1; then
    echo "⚠ check-marketplace-sync: gh 미인증 — skip (CI에서 검증)"
    exit 0
fi

PY_EXIT=0
python3 <<'PY' || PY_EXIT=$?
import sys, json, base64, subprocess
from pathlib import Path

LOCAL = Path(".claude-plugin/plugin.json")
if not LOCAL.exists():
    print(f"::error::{LOCAL}: 부재")
    sys.exit(1)

local = json.loads(LOCAL.read_text(encoding="utf-8"))

# Mirrored 필드 (CFP-24 정책)
MIRRORED = ["name", "version", "description", "author"]

local_name = local.get("name")
if not local_name:
    print(f"::error::{LOCAL}: 'name' 필드 부재")
    sys.exit(1)

# Marketplace fetch
try:
    proc = subprocess.run(
        ["gh", "api", "repos/mclayer/marketplace/contents/.claude-plugin/marketplace.json", "--jq", ".content"],
        capture_output=True, text=True, encoding="utf-8", check=True
    )
except subprocess.CalledProcessError as e:
    print(f"::error::marketplace.json fetch 실패: {e.stderr.strip()}")
    sys.exit(1)

content_b64 = proc.stdout.strip()
try:
    marketplace = json.loads(base64.b64decode(content_b64))
except Exception as e:
    print(f"::error::marketplace.json 디코드 실패: {e}")
    sys.exit(1)

# 자기 entry 찾기
entry = None
for p in marketplace.get("plugins", []):
    if p.get("name") == local_name:
        entry = p
        break

if entry is None:
    print(f"::error::marketplace.json plugins[name={local_name!r}] 부재 — 신규 plugin? (수동 등록 필요)")
    sys.exit(1)

# Mirrored 필드 비교
drift = []
for f in MIRRORED:
    local_v = local.get(f)
    remote_v = entry.get(f)
    if local_v != remote_v:
        drift.append((f, local_v, remote_v))

if drift:
    print(f"::error::CFP-34 marketplace-sync (STRICT): {len(drift)} drift 발견")
    print(f"  Local:  .claude-plugin/plugin.json")
    print(f"  Remote: mclayer/marketplace/.claude-plugin/marketplace.json plugins[name={local_name!r}]")
    print()
    for f, lv, rv in drift:
        print(f"  - {f}:")
        print(f"      local : {json.dumps(lv, ensure_ascii=False)}")
        print(f"      remote: {json.dumps(rv, ensure_ascii=False)}")
    print()
    print("CFP-24 정책: mirrored 필드 변경 시 cross-repo sync PR 의무.")
    print("Action: mclayer/marketplace 에 위 drift 반영 PR open + merge.")
    sys.exit(1)

print(f"✓ CFP-34 marketplace-sync: '{local_name}' mirrored 필드 sync (name/version/description/author)")
PY

echo ""
echo "(check-marketplace-sync: strict 모드 — CFP-24 정책 자동 enforcement)"
exit $PY_EXIT
