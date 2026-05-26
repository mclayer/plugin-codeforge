# CFP-1668 Test-3: IA tree schema 1.1 → 1.2 backward-compat validation

@test "Test-3.1: confluence-ia-tree.yaml exists" {
  [ -f "docs/confluence-ia-tree.yaml" ] || return 1
}

@test "Test-3.2: YAML syntax is valid" {
  if [ ! -f "docs/confluence-ia-tree.yaml" ]; then
    skip "IA tree file missing"
  fi
  python3 -c "import yaml; yaml.safe_load(open('docs/confluence-ia-tree.yaml', encoding='utf-8'))" 2>/dev/null || {
    echo "ERROR: YAML parse failure"
    return 1
  }
}

@test "Test-3.3: schema_version is 1.2" {
  if [ ! -f "docs/confluence-ia-tree.yaml" ]; then
    skip "IA tree file missing"
  fi
  grep "^schema_version:" "docs/confluence-ia-tree.yaml" | grep -q "1.2" || {
    echo "ERROR: schema_version should be 1.2"
    return 1
  }
}

@test "Test-3.4: space section is preserved from 1.1" {
  if [ ! -f "docs/confluence-ia-tree.yaml" ]; then
    skip "IA tree file missing"
  fi
  grep -qE "^space(s)?:" "docs/confluence-ia-tree.yaml" || {
    echo "ERROR: space/spaces section missing"
    return 1
  }
}

@test "Test-3.5: per_consumer_instantiate_template section added for 1.2" {
  if [ ! -f "docs/confluence-ia-tree.yaml" ]; then
    skip "IA tree file missing"
  fi
  grep -q "^per_consumer_instantiate_template:" "docs/confluence-ia-tree.yaml" || {
    echo "ERROR: per_consumer_instantiate_template section not found"
    return 1
  }
}
