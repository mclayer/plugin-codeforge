# Inter-plugin Contract Drift Detection (CFP-E) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** wrapper repo `docs/inter-plugin-contracts/` 의 sibling file 본문이 lane plugin canonical 본문과 verbatim 일치하는지 자동 검증하는 lint + GitHub Actions job 도입. drift 발견 시 wrapper PR/push CI fail.

**Architecture:** 신규 script `scripts/check-inter-plugin-drift.sh` (Python heredoc + bash wrapper, 기존 `check-inter-plugin-contracts.sh` 패턴) 가 MANIFEST.yaml 순회 → 각 Active entry 의 canonical 을 GitHub REST API 로 live fetch → 정규화 후 sibling body 와 byte 비교 → drift 발견 시 unified_diff 출력 + exit 1. `.github/workflows/contract-lint.yml` 에 신규 job + `workflow_dispatch:` trigger 추가. 신규 ADR-011 이 정책 동결.

**Tech Stack:** bash + Python 3 (urllib.request, difflib, pyyaml), GitHub REST API (`/repos/{owner}/{repo}/contents/{path}`), GitHub Actions (`secrets.GITHUB_TOKEN`).

---

## Task 별 컨텍스트

본 plan은 spec [`docs/superpowers/specs/2026-04-30-cfp-e-inter-plugin-contract-drift-detection-design.md`](../specs/2026-04-30-cfp-e-inter-plugin-contract-drift-detection-design.md) 의 §4-§5 를 task 화. 모든 변경은 branch `cfp-e-drift-detection` (이미 spec commit ff49eae 존재).

**전체 작업 범위 (5 files)**:
- 신규 ADR: `docs/adr/ADR-011-inter-plugin-contract-drift-detection.md` (Task 1)
- 신규 lint script: `scripts/check-inter-plugin-drift.sh` (Task 2)
- 신규 test harness: `scripts/test-check-inter-plugin-drift.sh` (Task 3)
- `.github/workflows/contract-lint.yml` 갱신 (Task 4)
- `CHANGELOG.md` entry append (Task 5)
- 추가: spec/plan 사전 commit (이미 완료) + Task 6 (final lint + push) + Task 7 (PR + merge)

---

### Task 1: ADR-011 신설

**Files:**
- Create: `docs/adr/ADR-011-inter-plugin-contract-drift-detection.md`

- [ ] **Step 1: ADR file 작성**

```markdown
---
adr_number: 11
title: Inter-plugin Contract Drift Detection — canonical/sibling 본문 verbatim 자동 검증
status: Proposed
category: Team & Process
date: 2026-04-30
related_files:
  - docs/superpowers/specs/2026-04-30-cfp-e-inter-plugin-contract-drift-detection-design.md (parent CFP)
  - docs/adr/ADR-010-inter-plugin-contract-sibling-sync.md (§5 후속 ADR 의도 직접 충족)
  - docs/adr/ADR-008-inter-plugin-contract-versioning.md
  - docs/inter-plugin-contracts/MANIFEST.yaml
  - scripts/check-inter-plugin-drift.sh (본 ADR 강제 lint)
  - .github/workflows/contract-lint.yml (job inter-plugin-drift)
related_stories:
  - CFP-E (본 ADR 신설 시점)
  - CFP-42 (parent — sibling backfill + ADR-010 도입)
  - CFP-D (parent — review_verdict v1 Archived 전환, drift skip 룰 도출)
---

# ADR-011: Inter-plugin Contract Drift Detection

## 상태

`Proposed` (2026-04-30) — CFP-E PR merge 시 `Accepted` 전환. 1회 drift catch + fix cycle 후 `Adopted`.

## 컨텍스트

ADR-010 §5 명시: "본문 verbatim drift 검출 (canonical SHA vs sibling SHA 비교) 은 후속 ADR 에서 결정". CFP-42 시점 도입한 lint 는 manifest completeness + orphan + frontmatter schema (ADR-010 reference 포함) + sibling marker 까지만 검증. 본문 verbatim 정합성은 author 의무 (수동 sync PR) — drift 누적 위험.

CFP-D 결과 v1 review_verdict 는 wrapper 단독 SSOT (canonical 부재) 로 확인 — drift 검사 대상에서 자동 skip 룰 필요.

## 결정

### 1. canonical live fetch 방식

- 매 wrapper PR/push 시 GitHub REST API (`GET /repos/{owner}/{repo}/contents/{path}`) 로 canonical 본문 fetch
- SHA snapshot 저장 안 함 (MANIFEST schema 변경 회피)
- GITHUB_TOKEN read-only 권한 (모든 lane plugin public)

### 2. 정규화 후 byte-verbatim 비교

전처리 5 단계:
1. Frontmatter 분리 (sibling/canonical 각각 본문만)
2. Sibling-only meta section 제거 (`**상위 SSOT 위치**:` 시작 단락)
3. Line ending 정규화 (CRLF → LF)
4. Trailing whitespace trim (각 줄)
5. Trailing newline 통일 (file 끝 \n 1개)

정규화 후 byte 일치 검사. 불일치 시 `difflib.unified_diff()` + `::error::` annotation.

### 3. PR/push trigger 만 (cron 미도입)

- 1 인 maintainer 환경, lane plugin 변경 = wrapper sync PR 항상 동반 가정
- `workflow_dispatch:` 추가 (수동 debug)
- cron 도입은 향후 maintainer 다인 환경 또는 lane only 변경 시나리오 빈발 시 별도 ADR

### 4. status=Archived 자동 skip + canonical 부재 처리

- MANIFEST entry 의 `status: Archived` → drift 검사 자동 skip ("skip (Archived)" 출력)
- `status: Active` 인데 canonical fetch 404 → `::error::` exit 1 (정합성 lint error)
- v1 review_verdict (CFP-D 후 Archived) 가 첫 수혜 사례

### 5. 강제 메커니즘

- 신규 GitHub Actions job `inter-plugin-drift (CFP-E)` 가 `contract-lint.yml` 에 추가
- main branch protection 의 required-status-check 에 등록 (CFP-E PR merge 후 1일 dogfood 후 사용자 직접 GitHub Settings UI 등록)
- drift 발견 시 PR merge 차단 (간접 강제 → 직접 강제 격상)

## 결과

### 위배 시 처리

- drift 발견 + status=Active: lint exit 1 → required check fail → PR merge 차단
- canonical 404 + status=Active: lint exit 1 (Active entry 의 canonical 부재는 정합성 결함)
- status=Archived: 자동 skip (review_verdict v1 패턴)
- 후속 ADR 또는 CFP 가 cron / cross-repo webhook 도입 시 본 ADR §3 갱신

### 선례·관계 ADR

- ADR-008 (versioning): 본 ADR 과 무관 (frontmatter 비교 안 함)
- ADR-010 (sibling sync): 본 ADR 이 §5 후속 ADR 직접 충족
- ADR-009 (wrapper-only decomposition): drift detection 이 wrapper-only 모델의 sibling backfill 정합성 보장

### 후속 영향

- 7번째 contract 추가 시: lane plugin canonical + wrapper sibling + MANIFEST entry → 본 lint 가 자동 검증
- 신규 contract major bump (v2 → v3): 양쪽 plugin 동시 release + 본 lint 가 sibling sync 강제

## 관련 파일

- [`scripts/check-inter-plugin-drift.sh`](../../scripts/check-inter-plugin-drift.sh) — 본 ADR 강제 lint
- [`scripts/test-check-inter-plugin-drift.sh`](../../scripts/test-check-inter-plugin-drift.sh) — 회귀 테스트 harness
- [`.github/workflows/contract-lint.yml`](../../.github/workflows/contract-lint.yml) — job `inter-plugin-drift`
- [`docs/inter-plugin-contracts/MANIFEST.yaml`](../inter-plugin-contracts/MANIFEST.yaml) — registry SSOT
- [`docs/adr/ADR-010-inter-plugin-contract-sibling-sync.md`](ADR-010-inter-plugin-contract-sibling-sync.md) §5 — 본 ADR 의 motivation
```

- [ ] **Step 2: Commit**

```bash
git add docs/adr/ADR-011-inter-plugin-contract-drift-detection.md
git commit -m "docs(cfp-e): add ADR-011 — inter-plugin contract drift detection policy

ADR-010 §5 후속 ADR 의도 직접 충족. canonical live fetch + 정규화 후
byte-verbatim 비교 + PR/push trigger + Archived skip 룰 동결.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

### Task 2: scripts/check-inter-plugin-drift.sh 신설

**Files:**
- Create: `scripts/check-inter-plugin-drift.sh`

- [ ] **Step 1: script 작성**

```bash
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
    for attempt in range(2):  # initial + 1 retry
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

def normalize(text, strip_sibling_meta=False):
    """정규화 5 단계:
       1. Frontmatter 분리
       2. (sibling only) **상위 SSOT 위치**: 단락 제거
       3. CRLF → LF
       4. Trailing whitespace trim
       5. Trailing newline 통일
    """
    # Step 3: line ending 먼저 (모든 후속 처리 단순화)
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Step 1: frontmatter 분리
    if text.startswith("---\n"):
        end = text.find("\n---\n", 4)
        if end != -1:
            text = text[end + 5:]

    # Step 2: sibling-only meta section 제거
    if strip_sibling_meta:
        # **상위 SSOT 위치**: 로 시작하는 단락 제거
        # 단락 끝 = 다음 빈 줄 직전 또는 다음 ## 헤더 직전
        pattern = re.compile(
            r"^\*\*상위 SSOT 위치\*\*:.*?(?=\n\n|\n##\s|\Z)",
            re.DOTALL | re.MULTILINE,
        )
        text = pattern.sub("", text)
        # 제거 후 연속 빈 줄 정리 (3개 이상 → 2개)
        text = re.sub(r"\n{3,}", "\n\n", text)

    # Step 4: trailing whitespace trim
    text = "\n".join(line.rstrip() for line in text.split("\n"))

    # Step 5: trailing newline 통일
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

        sibling_norm = normalize(sibling_text, strip_sibling_meta=True)
        canonical_norm = normalize(canonical_text, strip_sibling_meta=False)

        if sibling_norm == canonical_norm:
            print(f"  ✓ {name} {fname}")
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

print(f"✓ CFP-E drift: {checked} contract(s) verbatim 일치, {skipped} skipped (Archived)")
PY

echo ""
echo "(check-inter-plugin-drift: ADR-011 — canonical/sibling 본문 verbatim 검증)"
exit $PY_EXIT
```

- [ ] **Step 2: 실행 권한 부여**

```bash
chmod +x scripts/check-inter-plugin-drift.sh
```

- [ ] **Step 3: 로컬 1회 실행 (drift 0 가정 — sanity check)**

Run: `PYTHONIOENCODING=utf-8 GH_TOKEN=$(gh auth token) bash scripts/check-inter-plugin-drift.sh`

Expected: exit 0, 출력에 5 contract 모두 `✓` + 1 skip (review_verdict v1 Archived).

만약 drift 가 발견되면 그 자체가 의미 있는 catch — Task 2 에서 handle 안 하고 issue 분리 (실제 drift 면 별도 PR 로 sibling sync).

- [ ] **Step 4: Commit**

```bash
git add scripts/check-inter-plugin-drift.sh
git commit -m "feat(cfp-e): scripts/check-inter-plugin-drift.sh 신설 (ADR-011)

canonical (GitHub REST API live fetch) ↔ sibling (local) 본문 verbatim
비교. 정규화 5 단계 (frontmatter / sibling meta / line ending / trailing
whitespace / trailing newline). status=Archived skip + Active canonical 404
fail. CFP_E_TEST_FIXTURE_DIR 환경 변수로 fetch mock 가능.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

### Task 3: scripts/test-check-inter-plugin-drift.sh 신설 (test harness)

**Files:**
- Create: `scripts/test-check-inter-plugin-drift.sh`

- [ ] **Step 1: test harness 작성**

```bash
#!/usr/bin/env bash
# CFP-E — Test harness for check-inter-plugin-drift.sh
#
# 8 test cases (T-1 ~ T-8 per CFP-E spec §8). Each case:
#   1. Create tmp fixture dir (canonical mock)
#   2. Apply test-specific mutation
#   3. Run lint with CFP_E_TEST_FIXTURE_DIR=<tmp>
#   4. Assert expected exit code
#   5. Cleanup
#
# Usage: bash scripts/test-check-inter-plugin-drift.sh
# Exit: 0 if all pass, 1 if any fail.

set -uo pipefail

cd "$(dirname "$0")/.."
REPO_ROOT="$(pwd)"
LINT_SCRIPT="$REPO_ROOT/scripts/check-inter-plugin-drift.sh"

PASS=0
FAIL=0

# 정상 fixture 생성 — 5 active contract 의 canonical 을 sibling 본문에서
# "**상위 SSOT 위치**:" section 만 제거한 버전으로 만듦 (정규화 후 일치)
build_baseline_fixture() {
  local fix_dir="$1"
  python3 <<PYEOF
import re, pathlib, yaml, sys
fix_dir = pathlib.Path("$fix_dir")
manifest = yaml.safe_load(pathlib.Path("docs/inter-plugin-contracts/MANIFEST.yaml").read_text(encoding="utf-8"))
for contract in (manifest or {}).get("contracts", []):
    repo = contract.get("canonical_repo", "")
    repo_basename = repo.split("/")[-1]
    canonical_path = contract.get("canonical_path", "").rstrip("/")
    for fent in contract.get("files", []):
        fname = fent.get("file", "")
        status = fent.get("status", "")
        if status != "Active":
            continue
        sibling = pathlib.Path("docs/inter-plugin-contracts") / fname
        if not sibling.exists():
            continue
        text = sibling.read_text(encoding="utf-8")
        # frontmatter 분리
        if text.startswith("---\n"):
            end = text.find("\n---\n", 4)
            if end != -1:
                fm_block = text[:end + 5]
                body = text[end + 5:]
            else:
                fm_block = ""
                body = text
        else:
            fm_block = ""
            body = text
        # sibling-only meta section 제거 (canonical 은 이 섹션 부재)
        body = re.sub(
            r"^\*\*상위 SSOT 위치\*\*:.*?(?=\n\n|\n##\s|\Z)",
            "",
            body,
            flags=re.DOTALL | re.MULTILINE,
        )
        body = re.sub(r"\n{3,}", "\n\n", body)
        # canonical fixture 는 frontmatter + meta-stripped body
        target_dir = fix_dir / repo_basename
        target_dir.mkdir(parents=True, exist_ok=True)
        (target_dir / fname).write_text(fm_block + body, encoding="utf-8")
PYEOF
}

run_test() {
  local name="$1"
  local expected_exit="$2"
  local mutation_fn="$3"

  local tmp
  tmp=$(mktemp -d)
  trap "rm -rf '$tmp'" RETURN

  # build baseline canonical fixture
  build_baseline_fixture "$tmp/fixtures"

  # mutation 적용 (sibling local 또는 fixture 어느 쪽이든)
  # Note: sibling 변경은 caller 가 책임지고 restore (or use git checkout)
  ( eval "$mutation_fn" )

  local actual_exit=0
  PYTHONIOENCODING=utf-8 CFP_E_TEST_FIXTURE_DIR="$tmp/fixtures" bash "$LINT_SCRIPT" >/dev/null 2>&1 || actual_exit=$?

  # restore sibling files (mutation 이 git tracked file 변경한 경우)
  git checkout -- docs/inter-plugin-contracts/ 2>/dev/null || true

  if [ "$actual_exit" = "$expected_exit" ]; then
    echo "✓ $name (exit $actual_exit)"
    PASS=$((PASS+1))
  else
    echo "✗ $name (expected exit $expected_exit, got $actual_exit)"
    FAIL=$((FAIL+1))
  fi
}

# T-1: positive — drift 없는 정합 상태
run_test "T-1 정합 상태 (no drift)" 0 ":"

# T-2: negative — sibling 본문에 한 글자 추가
run_test "T-2 sibling 본문 drift (한 글자 추가)" 1 \
  "python3 -c '
import pathlib
p = pathlib.Path(\"docs/inter-plugin-contracts/requirements-output-v1.md\")
text = p.read_text(encoding=\"utf-8\")
# 본문 첫 ## 섹션 직전에 X 한 글자 추가
text = text.replace(\"## 1.\", \"X## 1.\", 1)
p.write_text(text, encoding=\"utf-8\")
'"

# T-3: negative — canonical 본문 mock 변경
run_test "T-3 canonical drift (fixture 변경 mock)" 1 \
  "python3 -c '
import pathlib, sys
fix_dir = pathlib.Path(\"$tmp/fixtures\")
target = fix_dir / \"plugin-codeforge-requirements\" / \"requirements-output-v1.md\"
text = target.read_text(encoding=\"utf-8\")
text = text.replace(\"## 1.\", \"Y## 1.\", 1)
target.write_text(text, encoding=\"utf-8\")
'"

# T-4: positive — sibling 의 **상위 SSOT 위치**: section 변경 (정규화 후 무관)
run_test "T-4 sibling meta section 변경 (정규화 무시)" 0 \
  "python3 -c '
import pathlib
p = pathlib.Path(\"docs/inter-plugin-contracts/requirements-output-v1.md\")
text = p.read_text(encoding=\"utf-8\")
text = text.replace(\"**상위 SSOT 위치**:\", \"**상위 SSOT 위치 (변경됨)**:\", 1)
p.write_text(text, encoding=\"utf-8\")
'"

# T-5: positive — line ending CRLF vs LF (정규화 후 동일)
run_test "T-5 line ending CRLF (정규화 후 동일)" 0 \
  "python3 -c '
import pathlib
p = pathlib.Path(\"docs/inter-plugin-contracts/requirements-output-v1.md\")
text = p.read_text(encoding=\"utf-8\")
text_crlf = text.replace(\"\\n\", \"\\r\\n\")
p.write_text(text_crlf, encoding=\"utf-8\", newline=\"\")
'"

# T-6: positive — Archived entry skip (review_verdict v1 — CFP-D 후 status=Archived)
run_test "T-6 Archived entry 자동 skip" 0 ":"

# T-7: negative — Active entry 의 canonical 404 (fixture 삭제로 mock)
run_test "T-7 Active canonical 404 (fixture 삭제)" 1 \
  "rm '$tmp/fixtures/plugin-codeforge-requirements/requirements-output-v1.md'"

# T-8: positive — trailing whitespace 차이 (정규화 후 동일)
run_test "T-8 trailing whitespace 차이 (정규화 후 동일)" 0 \
  "python3 -c '
import pathlib
p = pathlib.Path(\"docs/inter-plugin-contracts/requirements-output-v1.md\")
text = p.read_text(encoding=\"utf-8\")
# 각 line 끝에 trailing space 1개 추가
text_ws = \"\\n\".join(line + \"  \" for line in text.split(\"\\n\"))
p.write_text(text_ws, encoding=\"utf-8\")
'"

echo ""
echo "Results: $PASS passed, $FAIL failed"
[ "$FAIL" = "0" ]
```

- [ ] **Step 2: 실행 권한 부여**

```bash
chmod +x scripts/test-check-inter-plugin-drift.sh
```

- [ ] **Step 3: 로컬 실행 — 모든 T 케이스 PASS 확인**

Run: `PYTHONIOENCODING=utf-8 bash scripts/test-check-inter-plugin-drift.sh`

Expected: 8 passed, 0 failed. 출력 끝에 `Results: 8 passed, 0 failed`.

만약 fail 나면 mutation 패턴 또는 정규화 로직 점검 (Task 2 의 normalize 함수 vs Task 3 의 build_baseline_fixture 일관성 확인).

- [ ] **Step 4: Commit**

```bash
git add scripts/test-check-inter-plugin-drift.sh
git commit -m "test(cfp-e): scripts/test-check-inter-plugin-drift.sh 신설 (T-1 ~ T-8)

8 test case (정합 / sibling drift / canonical drift / meta section 변경 /
line ending / Archived skip / Active 404 / trailing whitespace). canonical
은 build_baseline_fixture 로 sibling 본문에서 meta section 제거한 버전 mock.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

### Task 4: contract-lint.yml 갱신 (새 job + workflow_dispatch)

**Files:**
- Modify: `.github/workflows/contract-lint.yml`

- [ ] **Step 1: workflow trigger 에 workflow_dispatch 추가**

[`.github/workflows/contract-lint.yml`](../../../.github/workflows/contract-lint.yml) line 3-7 변경:

기존:
```yaml
on:
  pull_request:
    branches: [main]
  push:
    branches: [main]
```

대체:
```yaml
on:
  pull_request:
    branches: [main]
  push:
    branches: [main]
  workflow_dispatch: {}
```

- [ ] **Step 2: 새 job 추가**

기존 `inter-plugin-contracts` job 다음에 (line 22 직후) 새 job 추가:

```yaml
  inter-plugin-drift:
    name: inter-plugin-drift (CFP-E)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install pyyaml
      - name: Run check-inter-plugin-drift.sh
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: bash scripts/check-inter-plugin-drift.sh
```

- [ ] **Step 3: workflow file 검증 (yaml syntax)**

Run: `python3 -c "import yaml; yaml.safe_load(open('.github/workflows/contract-lint.yml'))"`

Expected: no error.

- [ ] **Step 4: Commit**

```bash
git add .github/workflows/contract-lint.yml
git commit -m "ci(cfp-e): contract-lint.yml — inter-plugin-drift job + workflow_dispatch

신규 job 'inter-plugin-drift (CFP-E)' 가 매 PR/push 시 ADR-011 lint 실행.
workflow_dispatch trigger 추가 (수동 debug 용).

main branch protection 의 required-status-check 에 'inter-plugin-drift
(CFP-E)' 등록은 1일 dogfood 후 사용자 직접 GitHub Settings UI 에서 처리.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

### Task 5: CHANGELOG entry append

**Files:**
- Modify: `CHANGELOG.md`

- [ ] **Step 1: 최상단 entry append**

[`CHANGELOG.md`](../../../CHANGELOG.md) line 8 (`## [Unreleased] - CFP-D` 위 또는 [Unreleased] 통합) 갱신:

기존:
```markdown
## [Unreleased] - CFP-D (2026-04-30)
```

대체 (CFP-D + CFP-E 함께 unreleased — 둘 다 같은 release 에 묶을 수도, 분리할 수도. 본 plan 은 분리 entry 권장 — release 시 한 version 으로 묶을지 별도 결정):
```markdown
## [Unreleased] - CFP-E (2026-04-30)

### CFP-E — Inter-plugin Contract Drift Detection (ADR-011 신설)

ADR-010 §5 후속 ADR 직접 충족. wrapper PR/push 시 canonical (lane plugin repo) ↔ wrapper sibling 본문 verbatim drift 자동 검증.

### Added

- `docs/adr/ADR-011-inter-plugin-contract-drift-detection.md` — drift detection 정책 동결 (live fetch + 정규화 5단계 + Archived skip + PR/push trigger only)
- `scripts/check-inter-plugin-drift.sh` — canonical live fetch (GitHub REST API) + 정규화 + byte-verbatim 비교 lint
- `scripts/test-check-inter-plugin-drift.sh` — 회귀 테스트 harness (T-1 ~ T-8: 정합 / sibling drift / canonical drift / meta section / line ending / Archived skip / Active 404 / trailing whitespace)
- `.github/workflows/contract-lint.yml` 신규 job `inter-plugin-drift (CFP-E)` + `workflow_dispatch:` trigger

### Changed

- (없음 — schema 변경 없이 lint 추가만)

### Migration

- consumer 무영향 — 신규 lint 추가만
- 첫 PR/push merge 후 1일 dogfood 후 main branch protection 의 required-status-check 에 `inter-plugin-drift (CFP-E)` 수동 등록 권장

## [Unreleased] - CFP-D (2026-04-30)
```

- [ ] **Step 2: Commit**

```bash
git add CHANGELOG.md
git commit -m "docs(cfp-e): CHANGELOG entry — inter-plugin contract drift detection

CFP-E unreleased entry. ADR-011 신설 + 신규 lint script + test harness +
contract-lint.yml job + workflow_dispatch trigger 명시. CFP-D entry 와
함께 unreleased — release 시 한 version 으로 묶을지 별도 결정.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

### Task 6: Final lint + push

**Pre-condition:** Task 1-5 모두 commit 완료.

- [ ] **Step 1: 기존 lint 회귀 — check-inter-plugin-contracts.sh + test harness**

Run: `PYTHONIOENCODING=utf-8 bash scripts/check-inter-plugin-contracts.sh`

Expected: exit 0, "7 contract(s) schema 충족".

Run: `PYTHONIOENCODING=utf-8 bash scripts/test-check-inter-plugin-contracts.sh`

Expected: 6 passed, 0 failed (CFP-42 T1-T6 회귀 통과).

- [ ] **Step 2: 신규 lint — check-inter-plugin-drift.sh**

Run: `PYTHONIOENCODING=utf-8 GH_TOKEN=$(gh auth token) bash scripts/check-inter-plugin-drift.sh`

Expected: exit 0, 5 contract `✓` + 1 skip (review_verdict v1 Archived).

만약 drift 발견되면:
- 의미 있는 catch — sibling sync PR 별도 작성 필요 (본 CFP scope 밖)
- 또는 본 lint 의 정규화 로직 미세 차이 (T-4/T-5/T-8 보강 필요)
- 본 plan 은 lint 도입 자체가 목표 — drift catch 사실 자체가 lint 가 작동한다는 증거

- [ ] **Step 3: 신규 test harness — test-check-inter-plugin-drift.sh**

Run: `PYTHONIOENCODING=utf-8 bash scripts/test-check-inter-plugin-drift.sh`

Expected: `Results: 8 passed, 0 failed`.

- [ ] **Step 4: branch push**

```bash
git push -u origin cfp-e-drift-detection
```

---

### Task 7: wrapper PR open + admin merge

**Branch:** `cfp-e-drift-detection` (commits 누적: spec + plan + Task 1-5)

- [ ] **Step 1: PR 생성**

```bash
gh pr create --title "feat(cfp-e): inter-plugin contract drift detection (ADR-011 신설)" --body "$(cat <<'EOF'
## Summary
- ADR-010 §5 후속 ADR 직접 충족 — canonical (lane plugin repo) ↔ wrapper sibling 본문 verbatim drift 자동 검증
- 신규 ADR-011 (Inter-plugin Contract Drift Detection) author
- 신규 lint script + test harness + contract-lint.yml 새 job + workflow_dispatch trigger

## 결정 사항 (spec §3 결정 표)

| 결정점 | 채택 |
|---|---|
| trigger | PR/push to main + workflow_dispatch (cron drop) |
| 비교 방법 | strict body verbatim (정규화 후 byte 일치) |
| action | PR fail (CI block) |
| storage | live fetch (GITHUB_TOKEN) |
| skip | status=Archived 자동 skip + canonical 404 graceful warning |
| file 위치 | 기존 `contract-lint.yml` 에 새 job 추가 |
| ADR | 신규 ADR-011 발의 |

## 정규화 5단계
1. Frontmatter 분리
2. Sibling-only meta section (`**상위 SSOT 위치**:`) 제거
3. Line ending CRLF → LF
4. Trailing whitespace trim
5. Trailing newline 통일

## Test plan
- [x] `bash scripts/check-inter-plugin-drift.sh` — 5 active + 1 skip ✓
- [x] `bash scripts/test-check-inter-plugin-drift.sh` — T-1 ~ T-8 모두 PASS ✓
- [x] `bash scripts/check-inter-plugin-contracts.sh` 회귀 ✓
- [x] yaml syntax: `python -c "import yaml; yaml.safe_load(open('.github/workflows/contract-lint.yml'))"` ✓

## Post-merge action (수동)
- 1일 dogfood 후 main branch protection 의 required-status-check 에 `inter-plugin-drift (CFP-E)` 등록 (GitHub Settings UI)

## Linked
- spec: docs/superpowers/specs/2026-04-30-cfp-e-inter-plugin-contract-drift-detection-design.md
- plan: docs/superpowers/plans/2026-04-30-cfp-e-inter-plugin-contract-drift-detection.md
- 새 ADR: docs/adr/ADR-011-inter-plugin-contract-drift-detection.md
- parent ADR: docs/adr/ADR-010-inter-plugin-contract-sibling-sync.md §5

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

- [ ] **Step 2: PR phase-gate-mergeable 차단 확인 (meta-CFP 패턴)**

본 PR 은 docs/stories/CFP-E.md 부재 — phase-gate-mergeable required check 차단 예상 (CFP-42, CFP-43, CFP-D 동일 패턴).

또한 본 PR 자체가 `inter-plugin-drift (CFP-E)` job 을 신설하지만 main branch protection 에 아직 required check 등록 안 됨 (post-merge 수동 작업) → 본 PR 머지 차단 안 됨 (job 은 실행되어 PASS 만 보고).

- [ ] **Step 3: admin merge**

```bash
gh pr merge <PR#> --merge --admin --delete-branch
```

Expected: PR merged, remote branch 삭제됨.

- [ ] **Step 4: local main sync**

```bash
git checkout main
git pull origin main
git branch -d cfp-e-drift-detection
```

Expected: cfp-e-drift-detection local 도 삭제됨.

- [ ] **Step 5: post-merge 정합성 확인**

Run: `PYTHONIOENCODING=utf-8 GH_TOKEN=$(gh auth token) bash scripts/check-inter-plugin-drift.sh`

Expected: exit 0, 5 contract `✓` + 1 skip.

```bash
gh run list --workflow=contract-lint.yml --limit 1
```

Expected: 최신 run 의 `inter-plugin-drift (CFP-E)` job status = success.

- [ ] **Step 6 (수동, post-merge): branch protection required-status-check 등록**

GitHub Settings → Branches → main → Branch protection rule → Require status checks → 검색 `inter-plugin-drift (CFP-E)` → 추가 → Save.

본 step 은 1일 dogfood 후 사용자가 직접 처리 (자동 차단 효과 발효 시점 명시적 통제).

---

## 검증 종합

본 plan 실행 후 spec §8 Test Contract:
- T-1 ~ T-8 모두 PASS (`scripts/test-check-inter-plugin-drift.sh`) ✓
- 실제 5 active sibling/canonical pair 의 drift 0 (신규 lint 통과) ✓
- 기존 `check-inter-plugin-contracts.sh` 회귀 PASS ✓
- ADR-011 status `Proposed` (post-merge 후 `Accepted` 수동 전환 — 1회 drift catch + fix cycle 후 `Adopted`)

총 변경 (5 files):
- `docs/adr/ADR-011-*.md` (신규)
- `scripts/check-inter-plugin-drift.sh` (신규)
- `scripts/test-check-inter-plugin-drift.sh` (신규)
- `.github/workflows/contract-lint.yml` (job + trigger 추가)
- `CHANGELOG.md` (entry append)

총 commit: 7 (Task 1-5 단위 + Task 6 lint 검증 + Task 7 PR/merge).
