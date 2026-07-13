#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
scripts/lib/check_path_relocation_consistency.py
CFP-2661 / ADR-136 Amendment 4 §결정 15 — path-relocation-consistency lint
  (relocation-ledger 구동 construct-scoped dead-path 재유입 차단, census-floor oracle, warning tier / Layer 2).

대상 = wrapper-self 거버넌스 execution-surface (게이트 shell/python 스크립트 + workflow yaml +
  config yaml + agent-md frontmatter). ADR 실 위치가 `archive/adr/`(PR #1973 이동)로 relocation 된 뒤,
  게이트의 "실행표면 construct"(shell array / python literal / yaml sequence)가 구경로 `docs/adr` 만
  단독 지목하면 dead-path vacuous-PASS(scope=∅) / false-RED 을 일으킨다. 본 lint 은 relocation-ledger
  (`docs/path-relocation-ledger.yaml`)에 등록된 (old, new) pair 에 대해 **construct 단위 co-occurrence**
  (OLD 지목 construct 는 NEW 를 동일 construct 안에 동반해야 함)를 검사해 재유입을 정적 검출한다.

★ construct-scoped (기준 D) — file-level 판별기의 FN factory 회피 (Story §4.2 F2 / AC-14):
  file 은 dual(docs/adr ∪ archive/adr) 인데 특정 array/set/sequence construct 는 docs/adr 단독(dead)인
  경우가 실재한다 (check-no-atlassian.sh 의 ALLOWLIST_EXTRA_FILES / check_decision_principle_vocabulary.py
  의 EXEMPT_PATHS / agent-md frontmatter allow sequence). file-level 이면 "dual 이니 OK"(FN). 본 lint 은
  각 construct span 안에서만 co-occurrence 를 판정한다 → construct-level 검출.

★ active_when field-predicate selector (least-powerful — ADR-136 Amd4 §결정15.a):
  construct 활성 판정이 co-located sibling scalar 에 의존할 수 있다. ledger surface entry 의
  `active_when: {field: parallel_edit, equals: locked}` 는 gate parallel-epic-conflict-check.yml:69
  의 소비 predicate(`if s.get('parallel_edit')=='locked'`)를 **정확히 mirror** 한다 — sibling predicate
  매치 시에만 해당 construct 에 co-occurrence rule 적용. `field == literal` equality only(expression
  language 아님). selector 부재 ⇒ 그 surface_kind 전 construct active.

★ census 3-count + fallback 비대칭 (anti-hollow observability — ADR-136 Amd4 §결정15.b / AC-15):
  reporter 는 candidates_scanned(active/judged) / inert_skipped(predicate-gated out) / violations 를 emit.
  candidate = relocation-relevant construct (OLD `docs/adr` 지목 construct). "scanned 0" ≠ "violations 0".
  **verdict fail-open** (모호/unbounded construct → NEW-missing violation suppress, warning-tier OK) but
  **census fail-closed** (parser 가 candidate count 를 못 세우면 hard failure, else born-hollow).
  born-hollow guard: candidates==0 ∧ inert==0(빈 corpus/empty-scope — relocation-relevant construct 를
  active·inert 어느 것으로도 0) → PASS 아니라 FAIL (exit 3). all-inert(candidates==0 ∧ inert>0)는 게이트가
  relevant construct 를 찾아 predicate-gated 한 non-vacuous 상태 → PASS(census 로 관측, F-CR-2).

★ 정직 천장 (I-6 / AC-20 — "재유입 완전 차단" hard-claim 금지):
  (I-6.1) static-literal ceiling — 동적 조립(`base + "/adr"`)·간접 참조 미검출.
  (I-6.2) ledger-ceiling — ledger 에 없는 relocation 미검출 (일반 lint 아닌 원장-구동 lint).
  (I-6.3) predicate-ceiling — `field == literal` predicate 만; computed/cross-file/multi-condition 미표현.
  (I-6.4) coupling residual FN — active_when 은 gate:69 predicate 를 설계-시점 mirror; gate:69-side
          predicate 변경 검출은 self-test fixture 범위 밖 = declared FN.
  (I-6.5) body-prose FN — markdown 산문 Read/Glob/Write 지시문 신규 유입은 3 construct parser scope 밖.
  presence ≠ truth (bounded degradation) — construct-scoped 정적 리터럴 천장.

★ input-driven resource exhaustion safety (SecurityArch non-negotiable — Change Plan §7.2, CFP-2635 SF-1 선례):
  유일 위협 축 = adversarial construct 파일(초장문 라인 / 폭발적 배열 / nested 구조)의 파서 자원 고갈(DoS).
  완화 4축 bound (총 작업량 <= PER_FILE_SCAN_CAP × MAX_PHYSICAL_LINE_LEN 유한 bound):
    (1) regex backtracking : 전 regex anchored + bounded quantifier(`{0,N}`), nested quantifier 0.
    (2) 물리라인 length    : MAX_PHYSICAL_LINE_LEN per-line truncate-scan (정당 코드 미도달).
    (3) 알고리즘 복잡도    : O(n) index/depth-advance — slice-in-loop O(n²) 금지.
    (4) read-path         : itertools.islice(f, PER_FILE_SCAN_CAP) 로 라인 count bound + per-line truncate.
  No injection: `ast.literal_eval`도 미사용(순수 substring/regex) — eval/exec 0. No path-traversal:
  스캔 대상은 repo-relative glob, 임의 경로 open 0. bounded degradation — "임의 입력 무해" 가 아님(정직 천장).

CLI 계약 (ADR-061 house style — 고정, self-test + workflow 소비):
  bash scripts/check-path-relocation-consistency.sh [--repo-root DIR] [--ledger PATH]
    → DIR (기본 = 자동 탐지/cwd) 하 execution-surface 코퍼스 스캔.

Exit codes (ADR-060 §결정 5 3-tier — warning tier, verdict fail-open / census fail-closed):
  0 = PASS (violation 0, census candidate ≥ 1).
  1 = ≥1 co-occurrence violation (warning — workflow continue-on-error 로 PR 미차단, `::warning::` surface).
  2 = usage/parse 오류 (argparse) / ledger 부재·malformed.
  3 = census fail-closed (candidate 0 = born-hollow guard 발동, OR parser 가 candidate 를 못 셈).

ADR refs: ADR-136 Amendment 4 §결정 15 (carrier, census-floor / empty-scope oracle) /
  ADR-060 §결정 5 (warning tier) / ADR-151 §결정7 (honesty ceiling 상속) / ADR-145 §결정 8/9
  (non-applicable 재사용) / ADR-061 §결정1 (Python SSOT + thin wrapper) / ADR-005 (byte-identical
  workflow pair) / ADR-119 (게이트=ground-truth, 오탐 0) / ADR-127 (1 Story = 2 PR).
"""

import argparse
import glob
import itertools
import os
import re
import sys

# Windows cp949 인코딩 문제 회피: stdout/stderr 를 UTF-8 강제 (ADR-061 portability 답습).
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# ─────────────────────── input-driven exhaustion bounded 상수 ───────────────────
PER_FILE_SCAN_CAP = 6000        # per-file 물리 라인 count bound (T-4 read-path).
MAX_PHYSICAL_LINE_LEN = 8192    # per-physical-line 길이 bound (T-2, 정당 코드 미도달, 초과분 truncate).
MAX_CONSTRUCT_SPAN = 400        # multi-line construct(array/literal/block) 누적 라인 상한 (병리 방어).

# 스캔 대상 execution-surface 코퍼스 (Change Plan §3 — 게이트 실행표면 CLASS).
# 포함 = 게이트 shell/python 스크립트 + workflow yaml + 게이트-소비 config yaml(section-ownership /
#   doc-locations / evidence-checks-registry) + agent-md frontmatter. corpus-wide within these class globs
#   (고정 site 열거 아님 — AC-13). ADR body(archive/adr/**·docs/adr/** prose) + Confluence sync 데이터
#   mirror(docs/confluence-ia-tree.yaml 등 pass/fail 판정 없는 데이터 매핑) = 실행표면 아님 → 제외
#   (§5.6 non-goal "ADR 본문 docs/adr 대량 잔존" class + floor inflation·anti-hollow 신호 희석 회피, §3.3).
CORPUS_GLOBS = (
    "scripts/*.sh",
    "scripts/*.py",
    "scripts/lib/*.py",
    ".github/workflows/*.yml",
    "templates/github-workflows/*.yml",
    "docs/parallel-work/*.yaml",
    "docs/doc-locations.yaml",
    "plugins/*/agents/*.md",
)

# self-source EXEMPT (check_shell_test_masking.py SELF_SOURCE 선례):
# 본 lint 3-artifact(원장/script/self-test) + 자기 소스는 의도적 `docs/adr` 리터럴(설명/fixture)을 담는다
# → 파일-단위 EXEMPT (E-2 self-referential born-hollow boundary). census-floor tripwire 로 vacuity 별도 봉인.
_SELF_SOURCE_TOKENS = (
    "check_path_relocation_consistency",
    "check-path-relocation-consistency",
    "path-relocation-ledger",
)

DEFAULT_LEDGER_REL = "docs/path-relocation-ledger.yaml"
# grandfather baseline (new-only subtract — CFP-2646/CFP-2591 선례): 승격 시점 pre-existing 잔존
# dead-path(D-scope 외: D12 argparse default 관찰-only + prose stale ADR-link)를 (file, snippet) 로 동결.
# new-only surface — 신규 유입만 flag. baseline 이 candidate/inert census(anti-hollow)를 감소시키지 않음.
DEFAULT_BASELINE_REL = "docs/path-relocation-baseline.yaml"


# ─────────────────────── ledger 로더 (dependency-free — born-safe, no yaml import) ─────

def load_ledger(path):
    """relocation-ledger 를 [{old,new,carrier,surfaces,active_when}] 로 로드 (최소 indentation 파서).

    born-safe: eval/exec/yaml.safe_load 미사용 — 고정 스키마 라인 파서. 부재/malformed → None (exit 2 유발).
    """
    if not os.path.isfile(path):
        return None
    relocations = []
    cur = None
    in_surfaces = False
    in_active = False
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            for raw in itertools.islice(f, 5000):
                if len(raw) > MAX_PHYSICAL_LINE_LEN:
                    raw = raw[:MAX_PHYSICAL_LINE_LEN]
                line = raw.rstrip("\n").rstrip("\r")
                # comment / blank
                stripped = line.strip()
                if not stripped or stripped.startswith("#"):
                    continue
                indent = len(line) - len(line.lstrip(" "))
                # 새 relocation item: `- old: <v>`
                m = re.match(r"^-\s+old:\s*(.+?)\s*$", stripped)
                if m:
                    if cur is not None:
                        relocations.append(cur)
                    cur = {"old": m.group(1).strip(), "new": None, "carrier": None,
                           "surfaces": [], "active_when": None}
                    in_surfaces = False
                    in_active = False
                    continue
                if cur is None:
                    continue
                m = re.match(r"^new:\s*(.+?)\s*$", stripped)
                if m:
                    cur["new"] = m.group(1).strip()
                    in_surfaces = False
                    in_active = False
                    continue
                m = re.match(r"^carrier:\s*(.+?)\s*$", stripped)
                if m:
                    cur["carrier"] = m.group(1).strip()
                    in_surfaces = False
                    in_active = False
                    continue
                if re.match(r"^surfaces:\s*$", stripped):
                    in_surfaces = True
                    in_active = False
                    continue
                if re.match(r"^active_when:\s*$", stripped):
                    in_active = True
                    in_surfaces = False
                    cur["active_when"] = {"field": None, "equals": None}
                    continue
                if in_surfaces:
                    m = re.match(r"^-\s+(.+?)\s*$", stripped)
                    if m:
                        cur["surfaces"].append(m.group(1).strip())
                        continue
                if in_active and cur["active_when"] is not None:
                    m = re.match(r"^field:\s*(.+?)\s*$", stripped)
                    if m:
                        cur["active_when"]["field"] = m.group(1).strip()
                        continue
                    m = re.match(r"^equals:\s*(.+?)\s*$", stripped)
                    if m:
                        cur["active_when"]["equals"] = m.group(1).strip()
                        continue
        if cur is not None:
            relocations.append(cur)
    except OSError:
        return None
    # validation
    clean = []
    for r in relocations:
        if not r.get("old") or not r.get("new") or not r.get("surfaces"):
            continue
        clean.append(r)
    return clean if clean else None


# ─────────────────────── 공통 read (born-safe read-path) ────────────────────────

def _read_physical(path):
    """islice read cap + per-physical-line truncate (T-2/T-4). 실패 → None."""
    try:
        physical = []
        with open(path, encoding="utf-8", errors="replace") as f:
            for raw in itertools.islice(f, PER_FILE_SCAN_CAP):
                line = raw.rstrip("\n").rstrip("\r")
                if len(line) > MAX_PHYSICAL_LINE_LEN:
                    line = line[:MAX_PHYSICAL_LINE_LEN]
                physical.append(line)
        return physical
    except OSError:
        return None


def _indent_of(line):
    return len(line) - len(line.lstrip(" "))


_HEREDOC_OPEN = re.compile(r"<<-?\s{0,2}[\"']?([A-Za-z_][A-Za-z0-9_]{0,60})[\"']?")


def _mask_shell_heredocs(physical):
    """heredoc body 라인을 blank 처리 (echo/cat 문서 텍스트 안 docs/adr 산문 오탐 차단). O(n)."""
    out = []
    delim = None
    for line in physical:
        if delim is not None:
            if line.strip() == delim:
                delim = None
                out.append(line)
            else:
                out.append("")
            continue
        code = _strip_hash_comment(line)
        m = _HEREDOC_OPEN.search(code)
        if m and not line.lstrip().startswith("#"):
            out.append(line)
            delim = m.group(1)
        else:
            out.append(line)
    return out


def _mask_python_docstrings(physical):
    """triple-quoted docstring body 라인을 blank 처리 (모듈/함수 docstring 산문 안 docs/adr 오탐 차단). O(n).

    근사 파서 (완전 python tokenizer 아님) — FP-안전 방향: docstring 산문을 construct 로 오인하지 않게 blank.
    """
    out = []
    in_doc = False
    delim = None
    for line in physical:
        if not in_doc:
            opened = None
            idx = -1
            for d in ('"""', "'''"):
                k = line.find(d)
                if k != -1 and (idx == -1 or k < idx):
                    idx = k
                    opened = d
            if opened is None:
                out.append(line)
                continue
            rest = line[idx + 3:]
            if opened in rest:
                # 한 줄 docstring — 라인 blank (산문). 앞 code 는 드묾 → FP-안전 우선.
                out.append(line[:idx])
            else:
                in_doc = True
                delim = opened
                out.append(line[:idx])  # docstring open 앞 code 보존
        else:
            k = line.find(delim)
            if k != -1:
                in_doc = False
                out.append(line[k + 3:])
                delim = None
            else:
                out.append("")
    return out


# ─────────────────────── 주석 strip (quote-aware, born-safe) ────────────────────

def _strip_hash_comment(text):
    """따옴표 밖 첫 `#` 이후 제거 (shell/python/yaml inline 주석). FP-안전(불확실=절단)."""
    in_s = in_d = False
    i = 0
    n = len(text)
    while i < n:
        c = text[i]
        if c == "'" and not in_d:
            in_s = not in_s
        elif c == '"' and not in_s:
            in_d = not in_d
        elif c == "#" and not in_s and not in_d:
            return text[:i]
        i += 1
    return text


# ─────────────────────── construct span 모델 ────────────────────────────────────

class Construct:
    __slots__ = ("lineno", "text", "kind", "predicate")

    def __init__(self, lineno, text, kind, predicate=None):
        self.lineno = lineno        # 1-based 시작 물리 라인
        self.text = text            # construct span 합성 텍스트 (주석 strip 후)
        self.kind = kind            # shell_array | python_literal | yaml_sequence
        self.predicate = predicate  # {field: v} sibling scalar 값 map (active_when 평가용) or None


# ── shell constructs ─────────────────────────────────────────────────────────

_SH_ARRAY_OPEN = re.compile(r"^\s{0,80}(?:declare\s+-\w{1,8}\s+)?[A-Za-z_][A-Za-z0-9_]{0,80}(?:\[[^\]]{0,120}\])?\+?=\(")
_SH_ASSIGN = re.compile(r"^\s{0,80}(?:local\s+|export\s+|declare\s+-\w{1,8}\s+)?[A-Za-z_][A-Za-z0-9_]{0,80}(?:\[[^\]]{0,120}\])?\+?=(?!=)")


def _shell_constructs(physical):
    """shell array 리터럴 span + 단일 assignment RHS 를 construct 로 추출 (paren-depth O(n))."""
    constructs = []
    n = len(physical)
    i = 0
    while i < n:
        raw = physical[i]
        code = _strip_hash_comment(raw)
        if _SH_ARRAY_OPEN.match(code):
            # array literal — paren balance 까지 span 누적.
            span_lines = [code]
            depth = code.count("(") - code.count(")")
            start = i + 1
            j = i + 1
            while j < n and depth > 0 and (j - i) < MAX_CONSTRUCT_SPAN:
                c2 = _strip_hash_comment(physical[j])
                span_lines.append(c2)
                depth += c2.count("(") - c2.count(")")
                j += 1
            constructs.append(Construct(start, "\n".join(span_lines), "shell_array"))
            i = j
            continue
        if _SH_ASSIGN.match(code) and "=" in code:
            rhs = code.split("=", 1)[1]
            constructs.append(Construct(i + 1, rhs, "shell_array"))
        else:
            # fallback: 비-assignment 라인도 construct 후보 (예: `paths = sorted(... "docs/adr" ...)` 유형은
            # 아니지만, shell 에서 array 밖 리터럴 참조 라인). logical line 자체를 construct 로.
            constructs.append(Construct(i + 1, code, "shell_array"))
        i += 1
    return constructs


# ── python constructs ────────────────────────────────────────────────────────

_PY_NAMED_LITERAL_OPEN = re.compile(r"^\s{0,80}[A-Za-z_][A-Za-z0-9_]{0,80}\s{0,4}(?::[^=]{0,80})?=\s{0,4}[\[\{\(]")


def _bracket_delta(text):
    return (text.count("[") + text.count("{") + text.count("(")
            - text.count("]") - text.count("}") - text.count(")"))


def _python_constructs(physical):
    """python named literal(`NAME = [ ... ]`) span + logical line 을 construct 로 추출 (bracket-depth O(n))."""
    constructs = []
    n = len(physical)
    i = 0
    while i < n:
        raw = physical[i]
        code = _strip_hash_comment(raw)
        if _PY_NAMED_LITERAL_OPEN.match(code):
            span_lines = [code]
            depth = _bracket_delta(code)
            start = i + 1
            j = i + 1
            while j < n and depth > 0 and (j - i) < MAX_CONSTRUCT_SPAN:
                c2 = _strip_hash_comment(physical[j])
                span_lines.append(c2)
                depth += _bracket_delta(c2)
                j += 1
            constructs.append(Construct(start, "\n".join(span_lines), "python_literal"))
            i = j
            continue
        # 단일 logical line construct (예: `Path("docs/adr").glob(...)`, `default="docs/adr"`).
        constructs.append(Construct(i + 1, code, "python_literal"))
        i += 1
    return constructs


# ── yaml constructs (sibling-group 모델; .yml/.yaml + .md frontmatter) ───────────

_MD_FM_FENCE = "---"


def _yaml_body_lines(physical, is_md):
    """.md 는 frontmatter(첫 `---` ~ 다음 `---`)만; .yml/.yaml 는 전체. → [(lineno, line)]."""
    if not is_md:
        return [(idx + 1, physical[idx]) for idx in range(len(physical))]
    # frontmatter 추출
    if not physical or physical[0].strip() != _MD_FM_FENCE:
        return []
    out = []
    for idx in range(1, len(physical)):
        if physical[idx].strip() == _MD_FM_FENCE:
            break
        out.append((idx + 1, physical[idx]))
    return out


def _yaml_constructs(physical, is_md):
    """sibling-group 단위 construct 추출.

    group 규칙:
      - `- key: value` mapping item → 각 item = 독립 construct (자기 `-` 라인 + 더 깊은 sibling key 라인).
      - `- scalar` sequence item → 동일 indent 연속 scalar `-` = 한 block construct.
      - `key: value` mapping key (dash 없음) → 동일 indent 연속 sibling key = 한 block construct
        (variants single_repo/dogfood dual-path co-occurrence 를 한 construct 로 묶음 — FP-안전).
    predicate: mapping-item construct 안에 sibling `field: value` 존재 시 predicate map 채움 (active_when 평가).
    """
    body = _yaml_body_lines(physical, is_md)
    constructs = []
    i = 0
    n = len(body)
    while i < n:
        lineno, raw = body[i]
        code = _strip_hash_comment(raw)
        if not code.strip():
            i += 1
            continue
        indent = _indent_of(code)
        stripped = code.strip()

        # (1) mapping item: `- key: value`
        m = re.match(r"^-\s+([A-Za-z_][\w-]{0,80}):", stripped)
        if m:
            item_lines = [code]
            predicate = {}
            # 첫 key 기록
            kv = re.match(r"^-\s+([A-Za-z_][\w-]{0,80}):\s*(.*)$", stripped)
            if kv:
                predicate[kv.group(1)] = kv.group(2).strip()
            j = i + 1
            content_indent = indent + 2
            while j < n and (j - i) < MAX_CONSTRUCT_SPAN:
                ln2, raw2 = body[j]
                c2 = _strip_hash_comment(raw2)
                if not c2.strip():
                    j += 1
                    continue
                ind2 = _indent_of(c2)
                if ind2 <= indent:
                    break
                item_lines.append(c2)
                kv2 = re.match(r"^([A-Za-z_][\w-]{0,80}):\s*(.*)$", c2.strip())
                if kv2 and ind2 == content_indent:
                    predicate[kv2.group(1)] = kv2.group(2).strip()
                j += 1
            constructs.append(Construct(lineno, "\n".join(item_lines), "yaml_sequence", predicate))
            i = j
            continue

        # (2) scalar sequence: consecutive `- scalar` at same indent
        if re.match(r"^-\s+\S", stripped):
            block_lines = [code]
            j = i + 1
            while j < n and (j - i) < MAX_CONSTRUCT_SPAN:
                ln2, raw2 = body[j]
                c2 = _strip_hash_comment(raw2)
                if not c2.strip():
                    j += 1
                    continue
                if _indent_of(c2) != indent or not c2.strip().startswith("- "):
                    break
                block_lines.append(c2)
                j += 1
            constructs.append(Construct(lineno, "\n".join(block_lines), "yaml_sequence"))
            i = j
            continue

        # (3) mapping leaf-key block: consecutive same-indent `key: <non-empty value>` (sibling LEAF keys
        #     → one block; variants single_repo/dogfood dual-path co-occurrence). block-header key
        #     (empty value) 는 construct 미생성 — 자식 라인이 이후 iteration 에서 rule 1/2/3 로 처리
        #     (전체 subtree greedy 흡수 = top-level version:/name: 이 파일 전체를 삼키는 over-group 버그 회피).
        m_leaf = re.match(r"^[A-Za-z_][\w-]{0,80}:\s+\S", stripped)
        if m_leaf:
            block_lines = [code]
            j = i + 1
            while j < n and (j - i) < MAX_CONSTRUCT_SPAN:
                ln2, raw2 = body[j]
                c2 = _strip_hash_comment(raw2)
                if not c2.strip():
                    break
                if _indent_of(c2) == indent and re.match(r"^[A-Za-z_][\w-]{0,80}:\s+\S", c2.strip()):
                    block_lines.append(c2)
                    j += 1
                    continue
                break
            constructs.append(Construct(lineno, "\n".join(block_lines), "yaml_sequence"))
            i = j
            continue

        # block-header key (empty value, `key:` with nested children) → construct 미생성, 자식 처리 위임.
        i += 1
    return constructs


# ─────────────────────── construct 판정 ─────────────────────────────────────────

def _surface_kind_for(path):
    p = path.replace(os.sep, "/")
    if p.endswith(".sh"):
        return "shell_array"
    if p.endswith(".py"):
        return "python_literal"
    if p.endswith(".yml") or p.endswith(".yaml"):
        return "yaml_sequence"
    if p.endswith(".md"):
        return "yaml_sequence"  # agent-md frontmatter
    return None


def _is_active(construct, active_when):
    """active_when predicate 평가. field 부재 construct = active(default). field 有 = equals 매치만 active."""
    if active_when is None:
        return True
    field = active_when.get("field")
    equals = active_when.get("equals")
    if not field:
        return True
    pred = construct.predicate
    if not pred or field not in pred:
        # construct 가 predicate field 미보유 → selector 무관 = active (Change Plan §3.3).
        return True
    val = pred.get(field, "").strip().strip('"').strip("'")
    return val == equals


def scan_file(path, rel, ledger):
    """단일 파일 → (candidates, inert, violations). violations = (rel, lineno, snippet)."""
    physical = _read_physical(path)
    if physical is None:
        return 0, 0, []
    kind = _surface_kind_for(path)
    if kind is None:
        return 0, 0, []
    is_md = path.replace(os.sep, "/").endswith(".md")

    if kind == "shell_array":
        constructs = _shell_constructs(_mask_shell_heredocs(physical))
    elif kind == "python_literal":
        constructs = _python_constructs(_mask_python_docstrings(physical))
    else:
        constructs = _yaml_constructs(physical, is_md)

    candidates = 0
    inert = 0
    violations = []

    for reloc in ledger:
        old = reloc["old"]
        new = reloc["new"]
        surfaces = reloc.get("surfaces", [])
        if kind not in surfaces:
            continue
        active_when = reloc.get("active_when")
        for c in constructs:
            if old not in c.text:
                continue
            # relocation-relevant construct 발견 (OLD 지목).
            if not _is_active(c, active_when):
                inert += 1
                continue
            candidates += 1
            if new not in c.text:
                snippet = " ".join(c.text.split())[:140]
                violations.append((rel, c.lineno, snippet))
    return candidates, inert, violations


def scan_corpus(repo_root, ledger):
    files = []
    for pattern in CORPUS_GLOBS:
        files.extend(glob.glob(os.path.join(repo_root, *pattern.split("/"))))
    files = sorted(set(files))

    total_candidates = 0
    total_inert = 0
    all_violations = []
    scanned_files = 0
    for path in files:
        if not os.path.isfile(path):
            continue
        rel = os.path.relpath(path, repo_root).replace(os.sep, "/")
        if any(tok in rel for tok in _SELF_SOURCE_TOKENS):
            continue  # self-source EXEMPT (E-2 born-hollow boundary)
        scanned_files += 1
        cand, inert, viol = scan_file(path, rel, ledger)
        total_candidates += cand
        total_inert += inert
        all_violations.extend(viol)
    return scanned_files, total_candidates, total_inert, all_violations


# ─────────────────────── grandfather baseline (new-only subtract) ───────────────

_BASELINE_FILE_RE = re.compile(r"^\s{0,80}(?:-\s{0,4})?file:\s*[\"']?([^\"'\n]+?)[\"']?\s*$")
_BASELINE_SNIP_RE = re.compile(r"^\s{0,80}snippet:\s*[\"']?(.+?)[\"']?\s*$")


def load_baseline(path):
    """grandfather baseline 을 (file, snippet) 집합으로 로드 (dependency-free 라인 파서, born-safe).

    부재/malformed → 빈 집합 (subtract 0, honest — consumer 상속 시 spurious 억제 미발생).
    """
    keys = set()
    if not os.path.isfile(path):
        return keys
    cur_file = None
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            for raw in itertools.islice(f, 100000):
                if len(raw) > MAX_PHYSICAL_LINE_LEN:
                    raw = raw[:MAX_PHYSICAL_LINE_LEN]
                m = _BASELINE_FILE_RE.match(raw)
                if m:
                    cur_file = m.group(1).strip()
                    continue
                m = _BASELINE_SNIP_RE.match(raw)
                if m and cur_file is not None:
                    keys.add((cur_file, m.group(1).strip()))
    except OSError:
        return set()
    return keys


def subtract_baseline(violations, baseline_keys):
    """violation (rel, ln, snip) 이 baseline 에 있으면 억제 (new-only). → (new, grandfathered_count)."""
    new = []
    gf = 0
    for (rel, ln, snip) in violations:
        if (rel, snip) in baseline_keys:
            gf += 1
        else:
            new.append((rel, ln, snip))
    return new, gf


def write_baseline(path, violations):
    """현 corpus violation 전건을 (file, snippet) baseline 으로 동결 write (single writer, canonical LF)."""
    pairs = sorted({(rel, snip) for (rel, _ln, snip) in violations})
    lines = [
        "# docs/path-relocation-baseline.yaml — GENERATED by "
        "scripts/lib/check_path_relocation_consistency.py --write-baseline (CFP-2661)",
        "# DO NOT EDIT BY HAND. Regenerate: bash scripts/check-path-relocation-consistency.sh "
        "--repo-root . --write-baseline",
        "# grandfather = 승격 시점 D-scope 외 pre-existing 잔존 dead-path(file, snippet) 동결 → new-only "
        "subtract (ADR-060 §결정6 Clean-as-You-Code). 신규 dead-path 유입만 flag. candidate/inert census 무영향.",
        "schema_version: '1.0'",
        "generated_by: CFP-2661",
        "basis: ADR-136 Amendment 4 §결정 15 승격 시점 D1~D15 외 pre-existing dead-path(file, snippet) 동결",
        "grandfathered_dead_paths:",
    ]
    if not pairs:
        body = "\n".join(lines[:-1]) + "\ngrandfathered_dead_paths: []\n"
    else:
        for (rel, snip) in pairs:
            lines.append("- file: %s" % rel)
            lines.append("  snippet: %s" % snip.replace("\n", " "))
            lines.append("  reason: pre-existing D-scope 외 (CFP-2661 baseline snapshot grandfather)")
        body = "\n".join(lines) + "\n"
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(body)
    return len(pairs)


# ─────────────────────── 출력 (warning surface) ─────────────────────────────────

_ACTION_GUIDE = (
    "[path-relocation-consistency] warning-tier (ADR-136 Amendment 4 §결정 15 — PR merge 미차단, advisory):\n"
    "  검출 = relocation-ledger 등록 (old → new) pair 에 대해, execution-surface construct(shell array /\n"
    "    python literal / yaml sequence)가 OLD 경로를 단독 지목(NEW 미동반) = dead-path 재유입 위험.\n"
    "  remediation 3택: ① 동일 construct 에 NEW 경로 union-ADD (docs/adr ∪ archive/adr) —\n"
    "    삭제형 치환 금지(consumer 정답 경로 소실). ② 정당 sunset 이면 OLD 리터럴 제거.\n"
    "    ③ hotfix-bypass:path-relocation-consistency label + audit comment.\n"
    "  honesty ceiling(ADR-151 §결정7): construct-scoped 정적 리터럴 천장 — 동적 조립/간접 참조/ledger-외\n"
    "    relocation/body-prose 산문 지시문 미검출(declared FN). presence ≠ truth. '완전 봉인' 아님."
)


def main(argv):
    parser = argparse.ArgumentParser(
        prog="check_path_relocation_consistency.py",
        description="relocation-ledger 구동 construct-scoped dead-path 재유입 차단 lint (warning tier).",
    )
    parser.add_argument("--repo-root", default=None, help="스캔 루트 (기본 = scripts/lib 기준 자동 탐지).")
    parser.add_argument("--ledger", default=None, help="relocation-ledger 경로 override.")
    parser.add_argument("--baseline", default=None, help="grandfather baseline 경로 override.")
    parser.add_argument("--write-baseline", action="store_true", help="현 corpus violation 을 baseline 으로 동결.")
    parser.add_argument("repo_root_pos", nargs="?", default=None, help=argparse.SUPPRESS)
    try:
        args = parser.parse_args(argv[1:])
    except SystemExit:
        return 2

    repo_root = args.repo_root or args.repo_root_pos
    if repo_root is None:
        repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    repo_root = os.path.abspath(repo_root)
    ledger_path = args.ledger or os.path.join(repo_root, DEFAULT_LEDGER_REL)
    baseline_path = args.baseline or os.path.join(repo_root, DEFAULT_BASELINE_REL)

    ledger = load_ledger(ledger_path)
    if ledger is None:
        print("::error::check-path-relocation-consistency: ledger 부재/malformed — %s" % ledger_path)
        return 2

    scanned_files, candidates, inert, raw_violations = scan_corpus(repo_root, ledger)

    # ── --write-baseline: 현 corpus violation 전건 동결 (subtract 없이) ──
    if args.write_baseline:
        n = write_baseline(baseline_path, raw_violations)
        print(
            "check-path-relocation-consistency: baseline written %s — %d (file, snippet) frozen "
            "(candidates_scanned=%d)" % (baseline_path, n, candidates)
        )
        return 0

    baseline_keys = load_baseline(baseline_path)
    violations, grandfathered = subtract_baseline(raw_violations, baseline_keys)

    # census emit (anti-hollow observability — always; candidate/inert 은 baseline 무영향).
    print(
        "check-path-relocation-consistency: census candidates_scanned=%d inert_skipped=%d "
        "violations=%d (grandfathered=%d) over %d file"
        % (candidates, inert, len(violations), grandfathered, scanned_files)
    )

    # census fail-closed — born-hollow guard (AC-15/AC-16 empty-scope oracle). "scanned 0" ≠ "violations 0".
    #   조건 = candidates==0 AND inert==0 (relocation-relevant construct 을 active 로도 inert 로도 하나도
    #   못 찾음 = 진짜 vacuous/dead-scope). inert>0 = 게이트가 relevant construct 를 찾았고 predicate-gated
    #   된 것(all-inert 는 non-vacuous — census 로 관측). candidates>0 = 정상.
    if candidates == 0 and inert == 0:
        print(
            "::error::check-path-relocation-consistency: FAIL-CLOSED — candidates_scanned=0 ∧ inert_skipped=0 "
            "(born-hollow guard 발동: relocation-relevant construct 를 active·inert 어느 것으로도 0 = empty-scope "
            "oracle, ADR-136 Amd4 §결정15). 정당한 0건은 ledger 조정 또는 ADR-145 non-applicable 선언 경로로만 통과."
        )
        return 3

    for (rel, ln, snip) in violations:
        print(
            '::warning::check-path-relocation-consistency: FLAG — dead-path 단독 지목 (NEW 미동반) '
            '%s:%d snippet="%s"' % (rel, ln, snip)
        )

    if violations:
        print("")
        print(_ACTION_GUIDE)
        print("")
        print(
            "check-path-relocation-consistency: FLAG %d new violation over %d file "
            "(candidates_scanned=%d inert_skipped=%d grandfathered=%d) — warning tier "
            "(continue-on-error 로 비차단, advisory only)"
            % (len(violations), scanned_files, candidates, inert, grandfathered)
        )
        return 1

    # PASS 메시지는 실 census count 만 사실 서술 — unconditional "candidate ≥ 1" literal 금지.
    #   실제 pass 조건 = NOT(candidates==0 ∧ inert==0) 이라 candidates==0 ∧ inert>0(all-inert) 도 PASS.
    #   그 경우 candidate=0 인데 "candidate ≥ 1" 로 overstate 하면 anti-hollow 게이트가 자기 출력에서
    #   honesty-ceiling 미세 위반(self-referential) — census 사실만 emit (F-CR-2 정정).
    print(
        "check-path-relocation-consistency: PASS — new violation 0 (candidates_scanned=%d inert_skipped=%d "
        "grandfathered=%d over %d file — empty-scope oracle: relocation-relevant construct 존재 "
        "(candidates==0 ∧ inert==0 아님), warning tier)"
        % (candidates, inert, grandfathered, scanned_files)
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
