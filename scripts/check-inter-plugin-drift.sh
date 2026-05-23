#!/usr/bin/env bash
# CFP-E (ADR-011) — Inter-plugin contract drift detection
#
# 검사: docs/inter-plugin-contracts/MANIFEST.yaml 의 각 Active entry 에 대해
#       canonical (lane plugin repo) 와 wrapper sibling 본문 verbatim 비교.
#
# 정규화 5 단계:
#   1. Frontmatter 분리
#   2. Sibling-only meta section 제거 (`**상위 SSOT 위치**:` 단락)
#   3. Line ending 정규화 (CRLF → LF)
#   4. Trailing whitespace trim
#   5. Trailing newline 통일 (file 끝 \n 1개)
#
# 비교: 정규화된 sibling body == canonical body? (byte 단위)
#       drift 발견 시 unified_diff + ::error:: annotation + exit 1
#
# Behavior:
#   - status=Archived entry: skip (출력 "skip (Archived)")
#   - status=Active entry, canonical 404: exit 1 (Active 인데 canonical 부재)
#   - GH_TOKEN 부재: 공개 repo read 는 무관하지만 rate limit 회피용 사용 권장
#   - canonical fetch 일시 오류: 1회 retry 후 fail
#
# Test fixture mode:
#   - 환경 변수 CFP_E_TEST_FIXTURE_DIR 설정 시 canonical fetch 대신 해당 디렉토리에서 읽음
#   - 형식: <fixture_dir>/<canonical_repo_basename>/<file>
#     예: /tmp/fixtures/plugin-codeforge-review/review-verdict-v2.md

set -uo pipefail
cd "$(dirname "$0")/.."

PY_EXIT=0
python3 <<'PY' || PY_EXIT=$?
import sys, os, re, json, base64, urllib.request, urllib.error, difflib
from pathlib import Path

try:
    import yaml
except ImportError:
    print("::error::CFP-E drift: pyyaml 미설치 — pip install pyyaml")
    sys.exit(1)

MANIFEST_PATH = Path("docs/inter-plugin-contracts/MANIFEST.yaml")
SIBLING_DIR = Path("docs/inter-plugin-contracts")
FIXTURE_DIR = os.environ.get("CFP_E_TEST_FIXTURE_DIR", "")
GH_TOKEN = os.environ.get("GH_TOKEN", "")

if not MANIFEST_PATH.exists():
    print(f"::error::CFP-E drift: {MANIFEST_PATH} 부재")
    sys.exit(1)

try:
    manifest = yaml.safe_load(MANIFEST_PATH.read_text(encoding="utf-8"))
except Exception as e:
    print(f"::error::CFP-E drift: MANIFEST.yaml parse 실패 — {e}")
    sys.exit(1)

def fetch_canonical(repo, path):
    """canonical 본문 fetch — fixture mode 또는 GitHub REST API.

    Returns: (status_code: int, body: str | None)
      - 200 OK + body
      - 404 NOT FOUND + None
      - other: raises Exception
    """
    if FIXTURE_DIR:
        repo_basename = repo.split("/")[-1]
        fixture_path = Path(FIXTURE_DIR) / repo_basename / Path(path).name
        if fixture_path.exists():
            return (200, fixture_path.read_text(encoding="utf-8"))
        return (404, None)

    url = f"https://api.github.com/repos/{repo}/contents/{path}"
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json"})
    if GH_TOKEN:
        req.add_header("Authorization", f"Bearer {GH_TOKEN}")

    last_err = None
    for attempt in range(2):
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read())
                content_b64 = data.get("content", "")
                body = base64.b64decode(content_b64).decode("utf-8")
                return (200, body)
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return (404, None)
            last_err = e
        except (urllib.error.URLError, TimeoutError) as e:
            last_err = e

    raise RuntimeError(f"canonical fetch 실패 ({repo}/{path}): {last_err}")

def normalize(text):
    """정규화 5 단계 (canonical + sibling 양쪽 동일 적용).

    순서: line ending → trailing whitespace → frontmatter → meta section → trailing newline
    (whitespace 가 frontmatter delimiter `---` 에도 영향 주지 않도록 먼저 trim)
    """
    # 1. Line ending 정규화
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # 2. Trailing whitespace per line (frontmatter delimiter `---` 도 깨끗하게)
    text = "\n".join(line.rstrip() for line in text.split("\n"))

    # 3. Frontmatter 분리
    if text.startswith("---\n"):
        end = text.find("\n---\n", 4)
        if end != -1:
            text = text[end + 5:]

    # 4. **상위 SSOT** section 제거 (canonical + sibling 양쪽 동일 strip)
    # heading 변형 허용 (예: "**상위 SSOT 위치 (변경됨)**:") — 본 section 자체를 메타로 간주
    pattern = re.compile(
        r"^\*\*상위 SSOT[^\n]*?\*\*:.*?(?=\n\n|\n##\s|\Z)",
        re.DOTALL | re.MULTILINE,
    )
    text = pattern.sub("", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    # 5. Trailing newline 통일 (file 끝 \n 1개)
    text = text.rstrip("\n") + "\n"

    return text

errors = []
checked = 0
skipped = 0

for contract in (manifest or {}).get("contracts", []):
    name = contract.get("name", "<unknown>")
    canonical_repo = contract.get("canonical_repo", "")
    canonical_path = contract.get("canonical_path", "")
    for fent in contract.get("files", []):
        fname = fent.get("file", "")
        status = fent.get("status", "")

        if status == "Archived":
            print(f"  skip {name} {fname} (Archived)")
            skipped += 1
            continue

        if status != "Active":
            errors.append(f"{name} {fname}: 알 수 없는 status '{status}' (Active|Archived 만 본 lint 처리)")
            continue

        sibling_path = SIBLING_DIR / fname
        if not sibling_path.exists():
            errors.append(f"{name} {fname}: sibling file 부재 ({sibling_path})")
            continue

        sibling_text = sibling_path.read_text(encoding="utf-8")

        canonical_full_path = canonical_path.rstrip("/") + "/" + fname
        try:
            status_code, canonical_text = fetch_canonical(canonical_repo, canonical_full_path)
        except Exception as e:
            errors.append(f"{name} {fname}: canonical fetch 오류 — {e}")
            continue

        if status_code == 404:
            errors.append(
                f"{name} {fname}: status=Active 이지만 canonical 부재 "
                f"({canonical_repo}/{canonical_full_path}) — Active entry 정합성 위반"
            )
            continue

        sibling_norm = normalize(sibling_text)
        canonical_norm = normalize(canonical_text)

        if sibling_norm == canonical_norm:
            print(f"  [OK] {name} {fname}")
            checked += 1
        else:
            diff = list(difflib.unified_diff(
                canonical_norm.splitlines(keepends=True),
                sibling_norm.splitlines(keepends=True),
                fromfile=f"canonical ({canonical_repo}/{canonical_full_path})",
                tofile=f"sibling (docs/inter-plugin-contracts/{fname})",
                n=3,
            ))
            errors.append(
                f"{name} {fname}: drift 발견\n"
                + "".join(diff)
            )

if errors:
    print(f"::error::CFP-E drift: {len(errors)} 건")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)

print(f"[OK] CFP-E drift: {checked} contract(s) verbatim 일치, {skipped} skipped (Archived)")
PY

echo ""
echo "(check-inter-plugin-drift: ADR-011 — canonical/sibling 본문 verbatim 검증)"
exit $PY_EXIT
