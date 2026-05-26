# CFP-1668 Test-1: Confluence migration skill body validation

@test "Test-1.1: SKILL.md exists" {
  if [ ! -f "skills/confluence-migration/SKILL.md" ]; then
    skip "Phase 2 artifact not yet created"
  fi
}

@test "Test-1.2: SKILL.md has frontmatter YAML" {
  if [ ! -f "skills/confluence-migration/SKILL.md" ]; then
    skip "Phase 2 artifact not yet created"
  fi
  sed -n '/^---$/,/^---$/p' "skills/confluence-migration/SKILL.md" | grep -q "name:" || {
    echo "ERROR: name: field not found in frontmatter"
    return 1
  }
}

@test "Test-1.3: SKILL.md has description in frontmatter" {
  if [ ! -f "skills/confluence-migration/SKILL.md" ]; then
    skip "Phase 2 artifact not yet created"
  fi
  sed -n '/^---$/,/^---$/p' "skills/confluence-migration/SKILL.md" | grep -q "description:" || {
    echo "ERROR: description: field not found"
    return 1
  }
}

@test "Test-1.4: SKILL.md markdown has valid heading structure" {
  if [ ! -f "skills/confluence-migration/SKILL.md" ]; then
    skip "Phase 2 artifact not yet created"
  fi
  # Should have at least 3 major sections (##)
  [ "$(grep -c '^## ' 'skills/confluence-migration/SKILL.md')" -ge 3 ] || {
    echo "ERROR: Expected at least 3 ## sections"
    return 1
  }
}

@test "Test-1.5: SKILL.md has no obvious broken markdown links" {
  if [ ! -f "skills/confluence-migration/SKILL.md" ]; then
    skip "Phase 2 artifact not yet created"
  fi
  ! grep -E '\[.*\]\(\s*\)' "skills/confluence-migration/SKILL.md" || {
    echo "ERROR: Broken markdown links found"
    return 1
  }
}
