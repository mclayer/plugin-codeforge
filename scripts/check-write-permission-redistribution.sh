#!/usr/bin/env bash
# CFP-26 Phase 0a invariant
# 검사: single-owner 4종 docs path가 owner agent로 이관되었는가
#   - ArchitectAgent: docs/change-plans/** + docs/adr/** Edit/Write 보유
#   - DomainAgent:    docs/domain-knowledge/** Edit/Write 보유
#   - PMOAgent:       docs/retros/** Edit/Write 보유
#   - DocsAgent:      위 4 경로 Edit/Write deny 보유
set -euo pipefail
cd "$(dirname "$0")/.."

FAIL=0

# helper: extract permissions sub-block (allow|deny) from agent md frontmatter
extract_block() {
  local f="$1" key="$2"
  awk -v key="$key" '
    /^---$/{c++; next}
    c==1 && /^permissions:/{in_perm=1; next}
    c==1 && in_perm && $0 ~ "^  " key ":"{in_block=1; next}
    c==1 && in_perm && /^  [a-z]+:/{in_block=0}
    c==1 && in_block{print}
    c>=2{exit}
  ' "$f"
}

assert_allow() {
  local f="$1" pat="$2"
  if ! extract_block "$f" allow | grep -qF -- "$pat"; then
    echo "✗ $f frontmatter permissions.allow에 '$pat' 없음"
    FAIL=1
  fi
}

assert_deny() {
  local f="$1" pat="$2"
  if ! extract_block "$f" deny | grep -qF -- "$pat"; then
    echo "✗ $f frontmatter permissions.deny에 '$pat' 없음"
    FAIL=1
  fi
}

# ArchitectAgent
assert_allow agents/ArchitectAgent.md "Edit(docs/change-plans/**)"
assert_allow agents/ArchitectAgent.md "Write(docs/change-plans/**)"
assert_allow agents/ArchitectAgent.md "Edit(docs/adr/**)"
assert_allow agents/ArchitectAgent.md "Write(docs/adr/**)"

# DomainAgent — CFP-37 ζ arc 후 codeforge-requirements plugin 으로 이관 → wrapper 부재 시 skip
if [[ -f agents/DomainAgent.md ]]; then
  assert_allow agents/DomainAgent.md "Edit(docs/domain-knowledge/**)"
  assert_allow agents/DomainAgent.md "Write(docs/domain-knowledge/**)"
fi

# PMOAgent — CFP-36 ζ arc 후 codeforge-pmo plugin으로 이관 → wrapper에 부재 시 skip
if [[ -f agents/PMOAgent.md ]]; then
  assert_allow agents/PMOAgent.md "Edit(docs/retros/**)"
  assert_allow agents/PMOAgent.md "Write(docs/retros/**)"
fi

# DocsAgent — 4 path deny
assert_deny agents/DocsAgent.md "Edit(docs/change-plans/**)"
assert_deny agents/DocsAgent.md "Write(docs/change-plans/**)"
assert_deny agents/DocsAgent.md "Edit(docs/adr/**)"
assert_deny agents/DocsAgent.md "Write(docs/adr/**)"
assert_deny agents/DocsAgent.md "Edit(docs/domain-knowledge/**)"
assert_deny agents/DocsAgent.md "Write(docs/domain-knowledge/**)"
assert_deny agents/DocsAgent.md "Edit(docs/retros/**)"
assert_deny agents/DocsAgent.md "Write(docs/retros/**)"

if [[ $FAIL -eq 0 ]]; then
  echo "✓ CFP-26 Phase 0a — single-owner 4종 권한 재분배 invariant OK"
fi
exit $FAIL
