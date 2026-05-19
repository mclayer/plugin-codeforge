#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# CFP-33 (ζ arc F2) — Comment prefix registry self-validation
# CFP-478 / ADR-061 §결정 1 + Amendment 1 §결정 6.A — heredoc Python 외부 .py split
#
# 검사: docs/inter-plugin-contracts/comment-prefix-registry-v1.md 의 yaml block 유효성
# Usage / exit code / semantics 상세: scripts/check-comment-prefix.sh header.
import sys, re
from pathlib import Path

try:
    import yaml
except ImportError:
    print("⚠ check-comment-prefix: pyyaml 미설치 — skip", file=sys.stderr)
    sys.exit(0)

REGISTRY = Path("docs/inter-plugin-contracts/comment-prefix-registry-v1.md")
EXPECTED_COUNT = 14  # v1.3: 11 phase + Preflight + GitOps + SECURITY-FALLBACK + bypass-justification (CFP-845)
REQUIRED_FIELDS = {"prefix", "phase", "current_owner", "target_owner_plugin", "posters", "auto_mirror"}

if not REGISTRY.exists():
    print(f"::error::comment-prefix-registry-v1.md 부재")
    sys.exit(1)

text = REGISTRY.read_text(encoding="utf-8")

# ## 3. 항목 섹션의 fenced yaml block 추출
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

if not isinstance(data, dict) or "prefixes" not in data:
    print(f"::error::{REGISTRY}: yaml 최상위 'prefixes:' 키 누락")
    sys.exit(1)

prefixes = data["prefixes"]
if not isinstance(prefixes, list):
    print(f"::error::{REGISTRY}: prefixes 는 list 여야 함")
    sys.exit(1)

errors = []

# 1. 개수 검증
if len(prefixes) != EXPECTED_COUNT:
    errors.append(f"prefix 개수 mismatch: 발견 {len(prefixes)}, 기대 {EXPECTED_COUNT}")

# 2. 각 entry 검증
for i, entry in enumerate(prefixes):
    if not isinstance(entry, dict):
        errors.append(f"entry[{i}]: dict 아님 — {type(entry).__name__}")
        continue
    missing = REQUIRED_FIELDS - set(entry.keys())
    if missing:
        errors.append(f"entry[{i}] (prefix={entry.get('prefix','?')!r}): 필수 필드 누락 — {sorted(missing)}")
        continue
    posters = entry.get("posters")
    if not isinstance(posters, list) or len(posters) == 0:
        errors.append(f"entry[{i}] (prefix={entry['prefix']!r}): posters 빈 list 금지")
    am = entry.get("auto_mirror")
    if not isinstance(am, bool):
        errors.append(f"entry[{i}] (prefix={entry['prefix']!r}): auto_mirror 는 bool — got {type(am).__name__}")

# 3. prefix 중복 검출
prefix_strs = [e.get("prefix") for e in prefixes if isinstance(e, dict)]
seen = set()
for p in prefix_strs:
    if p in seen:
        errors.append(f"prefix 중복: {p!r}")
    seen.add(p)

if errors:
    print(f"::error::CFP-33 comment-prefix-registry (STRICT): {len(errors)} 건")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)

print(f"✓ CFP-33 comment-prefix-registry: {len(prefixes)} prefix entry 전부 schema 충족")
