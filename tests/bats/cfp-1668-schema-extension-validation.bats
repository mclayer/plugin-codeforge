# CFP-1668 Test-2: Schema extension validation (4 new atlassian fields)

@test "Test-2.1: project-config-schema.md exists" {
  [ -f "docs/project-config-schema.md" ] || return 1
}

@test "Test-2.2: Schema has instance field" {
  if [ ! -f "docs/project-config-schema.md" ]; then
    skip "Schema file missing"
  fi
  grep -E "(instance|confluence)" "docs/project-config-schema.md" | grep -q "instance" || {
    echo "ERROR: instance field not found"
    return 1
  }
}

@test "Test-2.3: Schema has homepage_id field" {
  if [ ! -f "docs/project-config-schema.md" ]; then
    skip "Schema file missing"
  fi
  grep -q "homepage_id" "docs/project-config-schema.md" || {
    echo "ERROR: homepage_id field not found"
    return 1
  }
}

@test "Test-2.4: Schema has mirror_targets field" {
  if [ ! -f "docs/project-config-schema.md" ]; then
    skip "Schema file missing"
  fi
  grep -q "mirror_targets" "docs/project-config-schema.md" || {
    echo "ERROR: mirror_targets field not found"
    return 1
  }
}

@test "Test-2.5: Schema has per_doc_type_override field" {
  if [ ! -f "docs/project-config-schema.md" ]; then
    skip "Schema file missing"
  fi
  grep -q "per_doc_type_override" "docs/project-config-schema.md" || {
    echo "ERROR: per_doc_type_override field not found"
    return 1
  }
}
