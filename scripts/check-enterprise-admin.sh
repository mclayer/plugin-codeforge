#!/usr/bin/env bash
# check-enterprise-admin.sh — CFP-140 / ADR-048
# Verify enterprise or org admin role for GitOpsAgent prerequisite gate.
# Usage: check-enterprise-admin.sh [--enterprise SLUG] [--org ORG] [--token TOKEN]
# Exit codes: 0=ok (enterprise or org admin), 1=no access
set -euo pipefail

ENTERPRISE_SLUG=""
ORG_SLUG=""
TOKEN_OVERRIDE=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --enterprise) ENTERPRISE_SLUG="$2"; shift 2 ;;
    --org)        ORG_SLUG="$2";        shift 2 ;;
    --token)      TOKEN_OVERRIDE="$2";  shift 2 ;;
    *) echo "Unknown option: $1" >&2; exit 1 ;;
  esac
done

if [[ -n "$TOKEN_OVERRIDE" ]]; then
  export GH_TOKEN="$TOKEN_OVERRIDE"
fi

if [[ -z "${GH_TOKEN:-}" ]]; then
  echo "ERROR: GH_TOKEN not set. Use --token or export GH_TOKEN." >&2
  exit 1
fi

# 1. Get current user
CURRENT_USER=$(gh api /user --jq '.login' 2>/dev/null || true)
if [[ -z "$CURRENT_USER" ]]; then
  echo "ERROR: Cannot authenticate with GitHub API. Check GH_TOKEN." >&2
  exit 1
fi
echo "Authenticated as: $CURRENT_USER"

# 2. Check enterprise admin (if slug provided)
ENTERPRISE_ADMIN=false
if [[ -n "$ENTERPRISE_SLUG" ]]; then
  ENTERPRISE_ROLE=$(gh api graphql \
    -f query='query($enterprise:String!,$login:String!){enterprise(slug:$enterprise){members(query:$login,first:1){nodes{enterpriseAdminRole}}}}' \
    -f enterprise="$ENTERPRISE_SLUG" \
    -f login="$CURRENT_USER" \
    --jq '.data.enterprise.members.nodes[0].enterpriseAdminRole // ""' 2>/dev/null || true)

  if [[ "$ENTERPRISE_ROLE" == "OWNER" ]]; then
    echo "Role: enterprise admin (OWNER) for $ENTERPRISE_SLUG"
    ENTERPRISE_ADMIN=true
  else
    echo "WARNING: Not enterprise admin for $ENTERPRISE_SLUG (role: ${ENTERPRISE_ROLE:-unknown})"
    echo "WARNING: enterprise-level ops (Area 1-3) will be degraded to org-level."
  fi
fi

# 3. Check org admin (if slug provided or as fallback)
ORG_ADMIN=false
if [[ -n "$ORG_SLUG" ]]; then
  ORG_ROLE=$(gh api "/orgs/${ORG_SLUG}/memberships/${CURRENT_USER}" \
    --jq '.role // ""' 2>/dev/null || true)

  if [[ "$ORG_ROLE" == "admin" ]]; then
    echo "Role: org admin for $ORG_SLUG"
    ORG_ADMIN=true
  else
    echo "WARNING: Not org admin for $ORG_SLUG (role: ${ORG_ROLE:-unknown or non-member})"
  fi
fi

# 4. Summary
if [[ "$ENTERPRISE_ADMIN" == true ]]; then
  echo "STATUS: enterprise-level governance ops available"
  exit 0
elif [[ "$ORG_ADMIN" == true ]]; then
  echo "STATUS: org-level governance ops available (enterprise-level degraded)"
  exit 0
else
  echo "ERROR: Neither enterprise admin nor org admin. Governance ops cannot proceed." >&2
  echo "See: scripts/check-enterprise-admin.sh --enterprise SLUG --org ORG" >&2
  exit 1
fi
