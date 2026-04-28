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

# helper: extract permissions allow block from agent md
allow_block() {
  local f="$1"
  awk '
    /^---$/{c++; next}
    c==1 && /^permissions:/{in_perm=1; next}
    c==1 && in_perm && /^  allow:/{in_allow=1; next}
    c==1 && in_perm && /^  [a-z]+:/{in_allow=0}
    c==1 && in_allow{print}
    c>=2{exit}
  ' "$f"
}

deny_block() {
  local f="$1"
  awk '
    /^---$/{c++; next}
    c==1 && /^permissions:/{in_perm=1; next}
    c==1 && in_perm && /^  deny:/{in_deny=1; next}
    c==1 && in_perm && /^  [a-z]+:/{in_deny=0}
    c==1 && in_deny{print}
    c>=2{exit}
  ' "$f"
}

assert_allow() {
  local f="$1" pat="$2"
  if ! allow_block "$f" | grep -qF -- "$pat"; then
    echo "✗ $f frontmatter permissions.allow에 '$pat' 없음"
    FAIL=1
  fi
}

assert_deny() {
  local f="$1" pat="$2"
  if ! deny_block "$f" | grep -qF -- "$pat"; then
    echo "✗ $f frontmatter permissions.deny에 '$pat' 없음"
    FAIL=1
  fi
}

# ArchitectAgent
assert_allow agents/ArchitectAgent.md "Edit(docs/change-plans/**)"
assert_allow agents/ArchitectAgent.md "Write(docs/change-plans/**)"
assert_allow agents/ArchitectAgent.md "Edit(docs/adr/**)"
assert_allow agents/ArchitectAgent.md "Write(docs/adr/**)"

# DomainAgent
assert_allow agents/DomainAgent.md "Edit(docs/domain-knowledge/**)"
assert_allow agents/DomainAgent.md "Write(docs/domain-knowledge/**)"

# PMOAgent
assert_allow agents/PMOAgent.md "Edit(docs/retros/**)"
assert_allow agents/PMOAgent.md "Write(docs/retros/**)"

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
