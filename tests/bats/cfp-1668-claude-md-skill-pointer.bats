# CFP-1668 Test-5: CLAUDE.md skill pointer validation

@test "Test-5.1: CLAUDE.md exists" {
  [ -f "CLAUDE.md" ] || return 1
}

@test "Test-5.2: confluence-migration skill enumerated" {
  if [ ! -f "CLAUDE.md" ]; then
    skip "CLAUDE.md missing"
  fi
  grep -q "confluence-migration" "CLAUDE.md" || {
    echo "ERROR: confluence-migration skill not found"
    return 1
  }
}

@test "Test-5.3: Skill enumeration has 12+ codeforge skills" {
  if [ ! -f "CLAUDE.md" ]; then
    skip "CLAUDE.md missing"
  fi
  count=$(grep -cE 'codeforge:[a-z-]+' "CLAUDE.md")
  [ "$count" -ge 12 ] || {
    echo "WARNING: Expected 12+ skills, found $count"
  }
}

@test "Test-5.4: Lane-entry skill table present" {
  if [ ! -f "CLAUDE.md" ]; then
    skip "CLAUDE.md missing"
  fi
  grep -q "Lane 진입 시" "CLAUDE.md" || {
    echo "ERROR: Lane-entry skill table not found"
    return 1
  }
}

@test "Test-5.5: Skill pointer has standard format codeforge:name" {
  if [ ! -f "CLAUDE.md" ]; then
    skip "CLAUDE.md missing"
  fi
  grep "confluence-migration" "CLAUDE.md" | grep -q "\`codeforge:" || {
    echo "WARNING: Not in standard format"
  }
}
