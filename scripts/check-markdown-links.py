import re, sys
from pathlib import Path

LINK_RE = re.compile(r'\[[^\]]*\]\(([^)]+)\)')
FENCE_RE = re.compile(r'^[ \t]*```')
ROOT = Path(".")
md_files = list(ROOT.rglob("*.md"))
md_files = [p for p in md_files if ".claude/agents" not in str(p)]
# Enhancement B: tests/fixtures/ 제외 (의도된 broken-link FP test fixture 보존)
# normalize to forward slashes for cross-platform path matching
md_files = [p for p in md_files if "tests/fixtures" not in str(p).replace("\\", "/")]
# 슬림화: archive/ 제외 (frozen 보관물 — 내부 상대링크는 live 표준 검증 대상 아님.
# 보관 시점 SHA 기준 동결, 후속 단계서 삭제될 live 문서를 가리킬 수 있음)
md_files = [p for p in md_files if not str(p).replace("\\", "/").startswith("archive/")]
# CFP-2152 S1 (ADR-118): plugins/ = lane repo subtree 흡수 격리 구역 — lane 잔여물 링크 정리는 S3 책임, 그전까지 lint 범위 제외
md_files = [p for p in md_files if not str(p).replace("\\", "/").startswith("plugins/")]

errors: list[str] = []
for md in md_files:
    in_fence = False
    for lineno, line in enumerate(md.read_text(encoding="utf-8").splitlines(), start=1):
        # Toggle on fenced code block boundaries; skip everything inside
        if FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        # Enhancement A: inline code-span strip (backtick-enclosed 링크 FP 제거)
        stripped_line = re.sub(r'`[^`]*`', '', line)
        for match in LINK_RE.finditer(stripped_line):
            target = match.group(1).strip()
            # Skip external URLs, anchors, mailto
            if target.startswith(("http://", "https://", "#", "mailto:")):
                continue
            # Skip placeholder targets (e.g., <REPLACE>, ${VAR}, {key})
            if "<" in target or "$" in target or target.startswith("{"):
                continue
            # Skip canonical sibling-repo paths (e.g., ../../../plugin-codeforge/) — paths
            # assume local clone layout (sibling repos in /workspace/<org>/), valid only
            # in canonical sibling repos (mclayer/plugin-codeforge-*/) — wrapper-local
            # check would always FAIL. inter-plugin-drift lint covers canonical↔sibling
            # verbatim parity. CFP-1336 carrier — pre-existing sibling-repo path convention.
            if target.startswith("../../../plugin-codeforge"):
                continue
            # Strip anchor fragment
            file_part = target.split("#", 1)[0]
            if not file_part:
                continue
            resolved = (md.parent / file_part).resolve()
            if not resolved.exists():
                errors.append(f"{md}:{lineno}: broken link -> {target}")

if errors:
    print("\n".join(errors))
    sys.exit(1)
print(f"all internal links OK across {len(md_files)} markdown files")
