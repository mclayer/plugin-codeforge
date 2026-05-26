# CFP-1668 Test-4: Consumer-guide §1o validation

@test "Test-4.1: consumer-guide.md exists" {
  [ -f "docs/consumer-guide.md" ] || return 1
}

@test "Test-4.2: §1o section heading present" {
  if [ ! -f "docs/consumer-guide.md" ]; then
    skip "consumer-guide missing"
  fi
  grep -E "^###.*1o\." "docs/consumer-guide.md" | grep -q . || {
    echo "ERROR: §1o heading not found"
    return 1
  }
}

@test "Test-4.3: §1o has 4-step enumeration" {
  if [ ! -f "docs/consumer-guide.md" ]; then
    skip "consumer-guide missing"
  fi
  count=$(grep -cE "^#### Step [0-9]" "docs/consumer-guide.md")
  [ "$count" -ge 4 ] || {
    echo "ERROR: Expected at least 4 Step sections, found $count"
    return 1
  }
}

@test "Test-4.4: ADR-100 mentioned in §1o" {
  if [ ! -f "docs/consumer-guide.md" ]; then
    skip "consumer-guide missing"
  fi
  grep -qi "ADR-100" "docs/consumer-guide.md" || echo "WARNING: ADR-100 not referenced"
}

@test "Test-4.5: ADR-111 mentioned in §1o" {
  if [ ! -f "docs/consumer-guide.md" ]; then
    skip "consumer-guide missing"
  fi
  grep -qi "ADR-111" "docs/consumer-guide.md" || echo "WARNING: ADR-111 not referenced"
}
