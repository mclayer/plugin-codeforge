#!/usr/bin/env python3
"""Helper script to create remaining CFP-722 fixture files."""
import pathlib, json
import sys

# Windows cp949 stdout encoding 차단 (CFP-1393 F8-FU / ADR-061 standardize)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

ROOT = pathlib.Path(__file__).parent.parent.parent
FIXTURE_ROOT = ROOT / "tests/fixtures/cfp-722/check-story-section-ownership"

def write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

# ─── TC-3b monopoly §13 ───────────────────────────────────────────────────────
base_13 = """---
key: CFP-201
title: Monopoly §13 test
status: phase:설계
type: story
---

## 1. 개요

§1 내용.

## 3. ADR 결정 매트릭스

ArchitectAgent 가 작성한 §3.

## 13. ArchitectPL Verdict

ArchitectPL 이 작성한 §13 원문.
판정: PASS. iteration 1.
"""
head_13 = """---
key: CFP-201
title: Monopoly §13 test
status: phase:설계
type: story
---

## 1. 개요

§1 내용.

## 3. ADR 결정 매트릭스

ArchitectAgent 가 작성한 §3.

## 13. ArchitectPL Verdict

lane plugin agent 가 §13 을 수정함 — monopoly violation.
판정: FIX. iteration 2 (lane plugin 이 임의로 추가).
"""
ctx = {"pr_branch": "cfp-201/develop", "pr_labels": ["phase:설계"], "path_pattern": "docs/stories/*.md"}
case = FIXTURE_ROOT / "tc-3b-monopoly-section13"
write(case / "input/base.md", base_13)
write(case / "input/head.md", head_13)
write(case / "input/context.json", json.dumps(ctx, indent=2, ensure_ascii=False) + "\n")
write(case / "expected/stdout.txt", "warning violation: §13 monopoly section modified without Orchestrator/delegate attribution (branch: cfp-201/develop)\n")
write(case / "expected/exit-code.txt", "0")

# ─── TC-3c monopoly §14 ───────────────────────────────────────────────────────
base_14 = """---
key: CFP-202
title: Monopoly §14 test
status: phase:구현
type: story
---

## 1. 개요

§1 내용.

## 8. 개발 서사

§8 내용.

## 14. Lane Evidence

| lane | start | end | outcome |
|---|---|---|---|
| 요구사항 | 2026-01-01 | 2026-01-02 | PASS |
"""
head_14 = """---
key: CFP-202
title: Monopoly §14 test
status: phase:구현
type: story
---

## 1. 개요

§1 내용.

## 8. 개발 서사

§8 내용.

## 14. Lane Evidence

| lane | start | end | outcome |
|---|---|---|---|
| 요구사항 | 2026-01-01 | 2026-01-02 | PASS |
| 구현 | 2026-01-03 | 2026-01-04 | PASS (lane plugin 이 직접 추가 — monopoly violation) |
"""
ctx2 = {"pr_branch": "cfp-202/develop", "pr_labels": ["phase:구현"], "path_pattern": "docs/stories/*.md"}
case = FIXTURE_ROOT / "tc-3c-monopoly-section14"
write(case / "input/base.md", base_14)
write(case / "input/head.md", head_14)
write(case / "input/context.json", json.dumps(ctx2, indent=2, ensure_ascii=False) + "\n")
write(case / "expected/stdout.txt", "warning violation: §14 monopoly section modified without Orchestrator/delegate attribution (branch: cfp-202/develop)\n")
write(case / "expected/exit-code.txt", "0")

# ─── TC-3d monopoly §10.5 (GitOps) ──────────────────────────────────────────
base_10dot5 = """---
key: CFP-203
title: Monopoly §10.5 GitOps test
status: phase:구현
type: story
---

## 1. 개요

§1 내용.

## 10.5. GitOps

GitOps Orchestrator 작성 원문.
ADR 예약 항목 A.
"""
head_10dot5 = """---
key: CFP-203
title: Monopoly §10.5 GitOps test
status: phase:구현
type: story
---

## 1. 개요

§1 내용.

## 10.5. GitOps

lane plugin 이 §10.5 를 수정함 — monopoly violation.
ADR 예약 항목 A.
ADR 예약 항목 B (lane plugin 추가).
"""
ctx3 = {"pr_branch": "cfp-203/develop", "pr_labels": ["phase:구현"], "path_pattern": "docs/stories/*.md"}
case = FIXTURE_ROOT / "tc-3d-monopoly-section10dot5"
write(case / "input/base.md", base_10dot5)
write(case / "input/head.md", head_10dot5)
write(case / "input/context.json", json.dumps(ctx3, indent=2, ensure_ascii=False) + "\n")
write(case / "expected/stdout.txt", "warning violation: §10.5 monopoly section modified without Orchestrator/delegate attribution (branch: cfp-203/develop)\n")
write(case / "expected/exit-code.txt", "0")

# ─── TC-4a FP whitespace ─────────────────────────────────────────────────────
story_4a_base = """---
key: CFP-300
title: FP whitespace test
status: phase:요구사항
type: story
---

## 1. 개요

§1 내용.

## 2. 도메인 컨텍스트

RequirementsPL 이 작성한 §2.
내용 A.
내용 B.
"""
story_4a_head = """---
key: CFP-300
title: FP whitespace test
status: phase:요구사항
type: story
---

## 1. 개요

§1 내용.

## 2. 도메인 컨텍스트

RequirementsPL 이 작성한 §2.
내용 A.
내용 B.

"""
# Only trailing whitespace added — non-violation
ctx4a = {"pr_branch": "cfp-300/requirements", "pr_labels": ["phase:요구사항"], "path_pattern": "docs/stories/*.md"}
case = FIXTURE_ROOT / "tc-4a-fp-whitespace"
write(case / "input/base.md", story_4a_base)
write(case / "input/head.md", story_4a_head)
write(case / "input/context.json", json.dumps(ctx4a, indent=2, ensure_ascii=False) + "\n")
write(case / "expected/stdout.txt", "")
write(case / "expected/exit-code.txt", "0")

# ─── TC-4b FP format (table reformatting only) ────────────────────────────────
story_4b_base = """---
key: CFP-301
title: FP format test
status: phase:요구사항
type: story
---

## 1. 개요

§1 내용.

## 2. 도메인 컨텍스트

RequirementsPL 이 작성한 §2.
| 항목 | 값 |
|---|---|
| A | 1 |
| B | 2 |
"""
story_4b_head = """---
key: CFP-301
title: FP format test
status: phase:요구사항
type: story
---

## 1. 개요

§1 내용.

## 2. 도메인 컨텍스트

RequirementsPL 이 작성한 §2.
| 항목 | 값    |
|------|-------|
| A    | 1     |
| B    | 2     |
"""
# Only table alignment changed — semantic content same = non-violation
ctx4b = {"pr_branch": "cfp-301/requirements", "pr_labels": ["phase:요구사항"], "path_pattern": "docs/stories/*.md"}
case = FIXTURE_ROOT / "tc-4b-fp-format"
write(case / "input/base.md", story_4b_base)
write(case / "input/head.md", story_4b_head)
write(case / "input/context.json", json.dumps(ctx4b, indent=2, ensure_ascii=False) + "\n")
write(case / "expected/stdout.txt", "")
write(case / "expected/exit-code.txt", "0")

# ─── TC-4c FP link-target only ────────────────────────────────────────────────
story_4c_base = """---
key: CFP-302
title: FP link-target test
status: phase:요구사항
type: story
---

## 1. 개요

§1 내용.

## 2. 도메인 컨텍스트

RequirementsPL 이 작성한 §2.
참조: [ADR-060](docs/adr/ADR-060.md).
내용 A.
"""
story_4c_head = """---
key: CFP-302
title: FP link-target test
status: phase:요구사항
type: story
---

## 1. 개요

§1 내용.

## 2. 도메인 컨텍스트

RequirementsPL 이 작성한 §2.
참조: [ADR-060](docs/adr/ADR-060-evidence-enforceable-promotion-framework.md).
내용 A.
"""
# Only link target updated — semantic content same = non-violation
ctx4c = {"pr_branch": "cfp-302/requirements", "pr_labels": ["phase:요구사항"], "path_pattern": "docs/stories/*.md"}
case = FIXTURE_ROOT / "tc-4c-fp-link-target"
write(case / "input/base.md", story_4c_base)
write(case / "input/head.md", story_4c_head)
write(case / "input/context.json", json.dumps(ctx4c, indent=2, ensure_ascii=False) + "\n")
write(case / "expected/stdout.txt", "")
write(case / "expected/exit-code.txt", "0")

# ─── TC-5 heading drift ──────────────────────────────────────────────────────
# Story with malformed heading → empty slice → LOUD warning
story_5_base = """---
key: CFP-400
title: Heading drift test
status: phase:구현
type: story
---

## 1. 개요

§1 내용.

## 8. 개발 서사

§8 내용.
"""
story_5_head = """---
key: CFP-400
title: Heading drift test
status: phase:구현
type: story
---

## 1. 개요

§1 내용.

## 8. 개발 서사

§8 내용.
추가 내용.
"""
ctx5 = {"pr_branch": "cfp-400/develop", "pr_labels": ["phase:구현"], "path_pattern": "*/stories/*.md"}
case = FIXTURE_ROOT / "tc-5-heading-drift"
write(case / "input/base.md", story_5_base)
write(case / "input/head.md", story_5_head)
write(case / "input/context.json", json.dumps(ctx5, indent=2, ensure_ascii=False) + "\n")
write(case / "expected/stdout.txt", "")
write(case / "expected/exit-code.txt", "0")

# ─── TC-6 carrier exempt ─────────────────────────────────────────────────────
# Story with bootstrap_exempt_protocols = policy:lane-self-write-boundary-mechanical
# AND carrier_story = same key → all-PASS
story_6_base = """---
key: CFP-722
title: Carrier story exemption test
status: phase:구현
type: story
carrier_story: CFP-722
bootstrap_exempt_protocols:
  - "script:check-story-section-ownership.sh"
  - "workflow:story-section-ownership.yml"
  - "policy:lane-self-write-boundary-mechanical"
---

## 1. 개요

§1 내용.

## 2. 도메인 컨텍스트

RequirementsPL §2.

## 8. 개발 서사

DeveloperPL §8.
"""
story_6_head = """---
key: CFP-722
title: Carrier story exemption test
status: phase:구현
type: story
carrier_story: CFP-722
bootstrap_exempt_protocols:
  - "script:check-story-section-ownership.sh"
  - "workflow:story-section-ownership.yml"
  - "policy:lane-self-write-boundary-mechanical"
---

## 1. 개요

§1 내용.

## 2. 도메인 컨텍스트

DeveloperPL 이 §2 를 destructive 수정함 — 그러나 carrier-exempt 이므로 PASS.

## 8. 개발 서사

DeveloperPL §8.
구현 A 추가.

## 8.5. Impl Manifest

신규 섹션 (DeveloperPL append).

## 10. FIX Ledger

| iteration | lane | verdict | note |
|---|---|---|---|
| 0 | code | PASS | 초기 |

## 14. Lane Evidence

| lane | start | end | outcome |
|---|---|---|---|
| 구현 | 2026-01-01 | 2026-01-02 | PASS |
"""
ctx6 = {"pr_branch": "cfp-722/develop", "pr_labels": ["phase:구현"], "path_pattern": "*/stories/*.md"}
case = FIXTURE_ROOT / "tc-6-carrier-exempt"
write(case / "input/base.md", story_6_base)
write(case / "input/head.md", story_6_head)
write(case / "input/context.json", json.dumps(ctx6, indent=2, ensure_ascii=False) + "\n")
write(case / "expected/stdout.txt", "notice carrier-exempt: CFP-722 declares bootstrap_exempt_protocols including policy:lane-self-write-boundary-mechanical — ownership checks bypassed\n")
write(case / "expected/exit-code.txt", "0")

# ─── TC-7 delegate subagent PASS ─────────────────────────────────────────────
# Orchestrator-owned delegate subagent modifies §10 → PASS (not violation)
story_7_base = """---
key: CFP-500
title: Delegate subagent test
status: phase:구현
type: story
---

## 1. 개요

§1 내용.

## 10. FIX Ledger

| iteration | lane | verdict | note |
|---|---|---|---|
| 0 | design | PASS | 초기 |
"""
story_7_head = """---
key: CFP-500
title: Delegate subagent test
status: phase:구현
type: story
---

## 1. 개요

§1 내용.

## 10. FIX Ledger

| iteration | lane | verdict | note |
|---|---|---|---|
| 0 | design | PASS | 초기 |
| 1 | code | FIX | Orchestrator delegate 추가 |
"""
# branch is cfp-500 (flat Orchestrator-pattern, NOT lane-scoped like cfp-500/develop)
ctx7 = {"pr_branch": "cfp-500", "pr_labels": ["phase:구현-리뷰"], "path_pattern": "*/stories/*.md"}
case = FIXTURE_ROOT / "tc-7-delegate-subagent-pass"
write(case / "input/base.md", story_7_base)
write(case / "input/head.md", story_7_head)
write(case / "input/context.json", json.dumps(ctx7, indent=2, ensure_ascii=False) + "\n")
write(case / "expected/stdout.txt", "")
write(case / "expected/exit-code.txt", "0")

# ─── TC-8 lane plugin direct fail ────────────────────────────────────────────
# Lane plugin agent directly modifies §10 via lane-scoped branch → FAIL
story_8_base = story_7_base  # same base
story_8_head = story_7_head  # same head content (§10 modified)
ctx8 = {"pr_branch": "cfp-500/develop", "pr_labels": ["phase:구현"], "path_pattern": "*/stories/*.md"}
case = FIXTURE_ROOT / "tc-8-lane-plugin-direct-fail"
write(case / "input/base.md", story_8_base)
write(case / "input/head.md", story_8_head)
write(case / "input/context.json", json.dumps(ctx8, indent=2, ensure_ascii=False) + "\n")
write(case / "expected/stdout.txt", "warning violation: §10 monopoly section modified without Orchestrator/delegate attribution (branch: cfp-500/develop)\n")
write(case / "expected/exit-code.txt", "0")

# ─── TC-9 §1 crossref exclusion ──────────────────────────────────────────────
# §1 modification should NOT trigger this lint (handled by story-section-1-immutable.yml)
story_9_base = """---
key: CFP-600
title: §1 exclusion test
status: phase:요구사항
type: story
---

## 1. 개요

§1 원문.

## 2. 도메인 컨텍스트

§2 원문.
"""
story_9_head = """---
key: CFP-600
title: §1 exclusion test
status: phase:요구사항
type: story
---

## 1. 개요

§1 원문 (수정됨 — 이 lint 에서는 무시, story-section-1-immutable.yml 영역).
추가 §1 내용.

## 2. 도메인 컨텍스트

§2 원문.
§2 추가 (RequirementsPL append — PASS).
"""
ctx9 = {"pr_branch": "cfp-600/requirements", "pr_labels": ["phase:요구사항"], "path_pattern": "docs/stories/*.md"}
case = FIXTURE_ROOT / "tc-9-section1-crossref-exclusion"
write(case / "input/base.md", story_9_base)
write(case / "input/head.md", story_9_head)
write(case / "input/context.json", json.dumps(ctx9, indent=2, ensure_ascii=False) + "\n")
write(case / "expected/stdout.txt", "")
write(case / "expected/exit-code.txt", "0")

# ─── F7-neg carrier-exempt-scope-proof ──────────────────────────────────────
# Story declares bootstrap_exempt but for DIFFERENT protocol — still violation
story_f7_base = """---
key: CFP-701
title: F7 carrier scope proof
status: phase:구현
type: story
carrier_story: CFP-701
bootstrap_exempt_protocols:
  - "script:some-other-script.sh"
  - "policy:some-other-policy"
---

## 1. 개요

§1 내용.

## 2. 도메인 컨텍스트

RequirementsPL §2 원문.
내용 A.
"""
story_f7_head = """---
key: CFP-701
title: F7 carrier scope proof
status: phase:구현
type: story
carrier_story: CFP-701
bootstrap_exempt_protocols:
  - "script:some-other-script.sh"
  - "policy:some-other-policy"
---

## 1. 개요

§1 내용.

## 2. 도메인 컨텍스트

DeveloperPL 이 §2 를 destructive 수정 — 다른 protocol exempt 라 여전히 위반.
"""
ctxf7 = {"pr_branch": "cfp-701/develop", "pr_labels": ["phase:구현"], "path_pattern": "*/stories/*.md"}
case = FIXTURE_ROOT / "f7-neg-carrier-exempt-scope-proof"
write(case / "input/base.md", story_f7_base)
write(case / "input/head.md", story_f7_head)
write(case / "input/context.json", json.dumps(ctxf7, indent=2, ensure_ascii=False) + "\n")
write(case / "expected/stdout.txt", "warning violation: §2 destructively modified by non-owner lane (branch: cfp-701/develop)\n")
write(case / "expected/exit-code.txt", "0")

# ─── F11a documented-FN tripwire ─────────────────────────────────────────────
# §8 owner (DeveloperPL) legitimately writes §8 — should PASS (not false-negative for owner writes)
story_f11a_base = """---
key: CFP-800
title: F11a documented FN tripwire
status: phase:구현
type: story
---

## 1. 개요

§1 내용.

## 8. 개발 서사

DeveloperPL §8 원문.
구현 A.
구현 B.
"""
story_f11a_head = """---
key: CFP-800
title: F11a documented FN tripwire
status: phase:구현
type: story
---

## 1. 개요

§1 내용.

## 8. 개발 서사

DeveloperPL §8 업데이트.
구현 A.
구현 B.
구현 C (추가).
구현 D (추가).
"""
ctxf11a = {"pr_branch": "cfp-800/develop", "pr_labels": ["phase:구현"], "path_pattern": "docs/stories/*.md"}
case = FIXTURE_ROOT / "f11a-documented-fn-tripwire"
write(case / "input/base.md", story_f11a_base)
write(case / "input/head.md", story_f11a_head)
write(case / "input/context.json", json.dumps(ctxf11a, indent=2, ensure_ascii=False) + "\n")
write(case / "expected/stdout.txt", "")
write(case / "expected/exit-code.txt", "0")

# ─── F11b drift-sync LOUD guard ──────────────────────────────────────────────
# Story with unusual heading patterns that could cause drift (e.g. empty section body)
# heading exists but section body is empty → should not cause exception, should emit warning
story_f11b_base = """---
key: CFP-801
title: F11b drift sync test
status: phase:구현
type: story
---

## 1. 개요

§1 내용.

## 2. 도메인 컨텍스트

§2 내용.

## 8. 개발 서사

§8 내용.
"""
story_f11b_head = """---
key: CFP-801
title: F11b drift sync test
status: phase:구현
type: story
---

## 1. 개요

§1 내용.

## 2. 도메인 컨텍스트

§2 내용.
§2 추가 (RequirementsPL — PASS).

## 8. 개발 서사

§8 내용.
§8 추가 (DeveloperPL — PASS).
"""
ctxf11b = {"pr_branch": "cfp-801/develop", "pr_labels": ["phase:구현"], "path_pattern": "docs/stories/*.md"}
case = FIXTURE_ROOT / "f11b-drift-sync-loud-guard"
write(case / "input/base.md", story_f11b_base)
write(case / "input/head.md", story_f11b_head)
write(case / "input/context.json", json.dumps(ctxf11b, indent=2, ensure_ascii=False) + "\n")
write(case / "expected/stdout.txt", "")
write(case / "expected/exit-code.txt", "0")

# ─── EC-2 line-shift ─────────────────────────────────────────────────────────
# Parallel session merge line-shift — heading-anchored slicing should handle correctly
story_ec2_base = """---
key: CFP-900
title: EC-2 line shift test
status: phase:구현
type: story
---

## 1. 개요

§1 내용.

## 2. 도메인 컨텍스트

RequirementsPL §2 원문.
내용 A.

## 8. 개발 서사

DeveloperPL §8 원문.
구현 A.
"""
story_ec2_head = """---
key: CFP-900
title: EC-2 line shift test
status: phase:구현
type: story
---

## 1. 개요

§1 내용 (수정 없음).
(병렬 세션 merge 로 인해 line-shift 발생할 수 있음).

## 2. 도메인 컨텍스트

RequirementsPL §2 원문.
내용 A.
내용 B (RequirementsPL 추가 — PASS).

## 8. 개발 서사

DeveloperPL §8 원문.
구현 A.
구현 B (DeveloperPL 추가 — PASS).
"""
ctx_ec2 = {"pr_branch": "cfp-900/develop", "pr_labels": ["phase:구현"], "path_pattern": "docs/stories/*.md"}
case = FIXTURE_ROOT / "ec-2-line-shift"
write(case / "input/base.md", story_ec2_base)
write(case / "input/head.md", story_ec2_head)
write(case / "input/context.json", json.dumps(ctx_ec2, indent=2, ensure_ascii=False) + "\n")
write(case / "expected/stdout.txt", "")
write(case / "expected/exit-code.txt", "0")

# ─── EC-3 new-file ───────────────────────────────────────────────────────────
# New story file (base absent) → non-violation (skip)
story_ec3_head = """---
key: CFP-999
title: EC-3 new file test
status: phase:요구사항
type: story
---

## 1. 개요

신규 Story — base 없음.

## 2. 도메인 컨텍스트

RequirementsPL §2.
"""
ctx_ec3 = {"pr_branch": "cfp-999/requirements", "pr_labels": ["phase:요구사항"], "path_pattern": "docs/stories/*.md"}
case = FIXTURE_ROOT / "ec-3-new-file"
# base.md intentionally absent (new file case — use empty sentinel)
write(case / "input/base.md", "")  # empty = "file did not exist"
write(case / "input/head.md", story_ec3_head)
write(case / "input/context.json", json.dumps(ctx_ec3, indent=2, ensure_ascii=False) + "\n")
write(case / "expected/stdout.txt", "")
write(case / "expected/exit-code.txt", "0")

print("All fixture files created.")
