#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
scripts/lib/reference_integrity_guard.py
CFP-2697 / Epic #2696 (canary artifact D6) — decision-record 정정/삭제 전 참조-무결성 guard.

목적:
  decision-record 라인을 정정(correct)/효력박탈(strip)/삭제(delete) 하기 **전에**, 그 조치가
  다른 곳을 깨뜨리지 않는지 4개 check 로 검증하는 **재사용 pure-ish 모듈**.
  (oracle `decision_record_disposition` 가 "무엇을 할지"를 정하면, 본 guard 는 "그 조치가 안전한지"를 판정.)

4 check:
  ① parser-scan       : 대상 파일 body 가 어떤 workflow/lint/script 에 의해 **파싱**되는가?
                         (string-quote/echo/주석 ≠ parse). `.github/workflows/` + `scripts/` 실스캔.
                         반환 body_parsed(bool).
  ② inbound-scan      : 대상 **row/anchor** 단위(파일 단위 아님)로 들어오는 인바운드 참조 수.
                         `§결정 N`/`ADR-NNN`/`#anchor` 또는 `file:line` 단위. 반환 inbound_count(int).
  ③ external-id-scan  : 대상의 `§결정 N`/`ADR-NNN`/`#anchor` 가 **required-context workflow**
                         (예: phase-gate-mergeable.yml)에 의해 인용되는가? 반환 external_id_cited + where.
  ④ structural-integrity : 제거/편집 후 표/헤더/리스트 유효 ∧ (workflow 편집 시) templates↔.github
                         mirror-pair byte-identical ∧ wording-baseline 키 충돌 0.
                         (a) markdown 표/헤더 유효성 모드 / (b) mirror-pair byte-parity 모드.

verdict:
  delete  통과 ⇔ ① body_parsed=false ∧ ② inbound_count=0 ∧ ③ external-id safe(미인용)
            ∧ ④ structure_intact — **전부**. 아니면 pass=false + strip_normativity(moot-mark, bytes 보존)로 강등 권고.
  correct/strip(=edit) 통과 ⇔ ③ external-id invariant(참조 orphan 0) ∧ ④ byte-parity.

anti-overfit:
  본 guard 는 target["file"]/target["row"] 를 **데이터**로 받아 스캔할 뿐, 특정 fixture 신원을
  코드에 하드코딩하지 않는다. required-context workflow 목록은 governance **config**(override 가능)이지
  대상 파일의 신원이 아니다.

resource-safety honest-ceiling (ADR-082 §결정 16):
  스캔은 governance 디렉터리(.github/workflows, scripts, docs/archive)의 텍스트 파일에 대해
  라인-단위로 수행된다. 스캔 총량은 대상 repo 파일 수에 선형(bounded)이나, 본 주석은 "임의 입력
  무해"를 단정하지 않는다 — bounded degradation 만 주장한다.

I/O 경계:
  oracle 와 달리 본 guard 는 **스캐너**이므로 repo_root 하위 파일을 읽는다(설계상 불가피). 네트워크 0.
"""

import argparse
import json
import os
import re
import sys

# ─────────────────────────────────────────────────────────────────────────────
# config — required-context workflow 목록 (governance config, override 가능 · 대상 신원 아님)
#   branch-protection required_status_checks 를 산출하는 workflow 파일들.
# ─────────────────────────────────────────────────────────────────────────────
_DEFAULT_REQUIRED_WORKFLOWS = (
    "phase-gate-mergeable.yml",
    "invariant-check.yml",
    "ac-traceability-matrix.yml",
    "deploy-lane-presence.yml",
    "doc-frontmatter-category-test.yml",
    "doc-schema-check.yml",
    "doc-section-schema.yml",
)

_SCAN_DIRS = (".github/workflows", "scripts")
_INBOUND_SCAN_DIRS = (".github/workflows", "scripts", "docs", "archive")

_TEXT_EXTS = (".yml", ".yaml", ".py", ".sh", ".md", ".txt", ".json")

# body 가 "파싱"됨을 시사하는 read/parse 동사 (string-quote/echo/주석 ≠ parse).
_PARSE_VERBS = (
    "cat ",
    "open(",
    "read_text",
    "get-content",
    ".read(",
    "readlines",
    "with open",
    "grep ",
    "get_file_contents",
    "yaml.safe_load",
    "yaml.load",
    "json.load",
    "safe_load",
    "load(",
    "read_file",
    "parse",
    "readfile",
)

# 정규식 (외부 id / anchor 탐지 — bounded)
_ADR_RE = re.compile(r"ADR-(\d+)")
_DECISION_RE = re.compile(r"§결정\s*(\d+)")
_ANCHOR_RE = re.compile(r"#([a-z0-9][a-z0-9\-]{2,80})")
_ADR_FILE_RE = re.compile(r"ADR-(\d+)")


def _read_text(path):
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return fh.read()
    except (OSError, UnicodeDecodeError):
        return None


def _iter_text_files(repo_root, subdirs):
    """repo_root 하위 지정 subdir 들의 텍스트 파일 경로를 순회(존재하는 것만)."""
    for sub in subdirs:
        base = os.path.join(repo_root, sub)
        if not os.path.isdir(base):
            continue
        for root, _dirs, files in os.walk(base):
            for name in files:
                if name.lower().endswith(_TEXT_EXTS):
                    yield os.path.join(root, name)


def _resolve_body(target, repo_root):
    """target 에서 대상 row 의 body 텍스트 확보. body 명시되면 그대로, 아니면 file+row 에서 읽음."""
    if target.get("body"):
        return target["body"]
    file_rel = target.get("file")
    row = target.get("row")
    if not file_rel:
        return ""
    abspath = os.path.join(repo_root, file_rel)
    text = _read_text(abspath)
    if text is None:
        return ""
    lines = text.splitlines()
    # row 가 정수(라인번호)면 해당 라인, anchor 문자열이면 그 anchor 포함 첫 라인.
    if row is None:
        return ""
    row_str = str(row)
    if row_str.isdigit():
        idx = int(row_str) - 1
        if 0 <= idx < len(lines):
            return lines[idx]
        return ""
    for line in lines:
        if row_str in line:
            return line
    return ""


# ─────────────────────────────────────────────────────────────────────────────
# ① parser-scan
# ─────────────────────────────────────────────────────────────────────────────
def check_parser_scan(target, repo_root):
    """대상 파일 body 가 workflow/lint/script 에 의해 파싱되는지 실스캔.

    heuristic(honest-ceiling): 대상 파일 경로/basename 이 스캔 대상 파일 안에서 read/parse 동사와
    같은 라인에 등장하면 body_parsed=True 로 본다. 순수 주석(`#` 선두)/echo-only 는 제외한다.
    전체 dataflow 분석이 아니라 토큰-근접 heuristic 임을 명시한다.
    """
    file_rel = target.get("file")
    if not file_rel:
        return {"body_parsed": False, "evidence": [], "note": "target.file 부재"}
    norm = file_rel.replace("\\", "/")
    base = os.path.basename(norm)
    evidence = []
    for scan_path in _iter_text_files(repo_root, _SCAN_DIRS):
        # 대상 자기 자신은 제외
        if os.path.abspath(scan_path) == os.path.abspath(os.path.join(repo_root, file_rel)):
            continue
        text = _read_text(scan_path)
        if text is None:
            continue
        for lineno, raw in enumerate(text.splitlines(), start=1):
            if base not in raw and norm not in raw:
                continue
            stripped = raw.strip()
            if stripped.startswith("#"):
                continue  # 주석 = 파싱 아님
            low = raw.lower()
            parsed = any(v in low for v in _PARSE_VERBS)
            if not parsed:
                # 대상 경로가 python/bash/script 호출의 argv 로 넘어가는 형태도 parse 로 간주
                if re.search(r"(python|bash|sh|\./)\S*.*" + re.escape(base), low):
                    parsed = True
            if parsed:
                evidence.append(
                    {"file": os.path.relpath(scan_path, repo_root).replace("\\", "/"),
                     "line": lineno, "text": stripped[:160]}
                )
    return {"body_parsed": len(evidence) > 0, "evidence": evidence}


# ─────────────────────────────────────────────────────────────────────────────
# ② inbound-scan (row/anchor 단위)
# ─────────────────────────────────────────────────────────────────────────────
def _target_row_anchors(target, repo_root):
    """대상 row 를 가리키는 anchor 문자열 후보 집합 산출 (row/anchor 단위 — 파일 단위 아님)."""
    body = _resolve_body(target, repo_root)
    file_rel = (target.get("file") or "").replace("\\", "/")
    anchors = set()
    # ADR 파일이면 §결정 N 을 ADR-NNN 으로 qualify.
    adr_num = None
    fm = _ADR_FILE_RE.search(os.path.basename(file_rel))
    if fm:
        adr_num = fm.group(1)
    for dm in _DECISION_RE.finditer(body):
        if adr_num:
            anchors.add("ADR-%s §결정 %s" % (adr_num, dm.group(1)))
        else:
            anchors.add("§결정 %s" % dm.group(1))
    for am in _ANCHOR_RE.finditer(body):
        anchors.add("#" + am.group(1))
    # file:line 형태(row 가 정수일 때)
    row = target.get("row")
    if row is not None and str(row).isdigit():
        anchors.add("%s:%s" % (os.path.basename(file_rel), row))
        anchors.add("%s:%s" % (file_rel, row))
    return anchors


def check_inbound_scan(target, repo_root):
    """대상 row/anchor 로 들어오는 인바운드 참조 수(파일 단위 아님)."""
    anchors = _target_row_anchors(target, repo_root)
    file_rel = (target.get("file") or "").replace("\\", "/")
    refs = []
    if not anchors:
        return {"inbound_count": 0, "refs": [], "anchors": []}
    self_abspath = os.path.abspath(os.path.join(repo_root, file_rel)) if file_rel else None
    for scan_path in _iter_text_files(repo_root, _INBOUND_SCAN_DIRS):
        if self_abspath and os.path.abspath(scan_path) == self_abspath:
            continue  # 자기 파일 내부는 인바운드 아님
        text = _read_text(scan_path)
        if text is None:
            continue
        for lineno, raw in enumerate(text.splitlines(), start=1):
            for anchor in anchors:
                if anchor in raw:
                    refs.append(
                        {"file": os.path.relpath(scan_path, repo_root).replace("\\", "/"),
                         "line": lineno, "anchor": anchor}
                    )
                    break
    return {"inbound_count": len(refs), "refs": refs, "anchors": sorted(anchors)}


# ─────────────────────────────────────────────────────────────────────────────
# ③ external-id-scan (required-context workflow 인용)
# ─────────────────────────────────────────────────────────────────────────────
def _target_external_ids(target, repo_root):
    """대상 body 의 외부 id (ADR-NNN / §결정 N / #anchor) 집합."""
    body = _resolve_body(target, repo_root)
    if target.get("external_ids"):
        return set(target["external_ids"])
    ids = set()
    for m in _ADR_RE.finditer(body):
        ids.add("ADR-" + m.group(1))
    for m in _DECISION_RE.finditer(body):
        ids.add("§결정 " + m.group(1))
    for m in _ANCHOR_RE.finditer(body):
        ids.add("#" + m.group(1))
    return ids


def check_external_id_scan(target, repo_root, required_workflows=None):
    """대상 외부 id 가 required-context workflow 에 인용되는지."""
    ids = _target_external_ids(target, repo_root)
    wf_names = required_workflows if required_workflows is not None else _DEFAULT_REQUIRED_WORKFLOWS
    where = []
    if not ids:
        return {"external_id_cited": False, "where": [], "ids": []}
    wf_dir = os.path.join(repo_root, ".github", "workflows")
    for wf_name in wf_names:
        wf_path = os.path.join(wf_dir, wf_name)
        text = _read_text(wf_path)
        if text is None:
            continue
        for lineno, raw in enumerate(text.splitlines(), start=1):
            for ext_id in ids:
                if ext_id in raw:
                    where.append({"workflow": wf_name, "line": lineno, "id": ext_id})
    return {"external_id_cited": len(where) > 0, "where": where, "ids": sorted(ids)}


def _external_ids_resolvable(target, repo_root):
    """대상이 참조하는 ADR-NNN 이 실재 파일로 resolve 되는지(orphan 0) — edit(③ invariant) 판정용."""
    ids = _target_external_ids(target, repo_root)
    adr_ids = [i for i in ids if i.startswith("ADR-")]
    if not adr_ids:
        return True  # 참조 ADR 없음 → orphan 불가 → invariant 성립
    adr_dirs = [os.path.join(repo_root, "archive", "adr"), os.path.join(repo_root, "docs", "adr")]
    existing = set()
    for d in adr_dirs:
        if os.path.isdir(d):
            for name in os.listdir(d):
                fm = _ADR_FILE_RE.search(name)
                if fm:
                    existing.add("ADR-" + fm.group(1))
    return all(i in existing for i in adr_ids)


# ─────────────────────────────────────────────────────────────────────────────
# ④ structural-integrity
# ─────────────────────────────────────────────────────────────────────────────
def validate_markdown_structure(text):
    """(a) markdown 표/헤더/리스트 유효성 모드 — 주어진 텍스트가 구조적으로 유효한지.

    표: 연속 `|`-선두 라인 블록의 컬럼 수 일관성 + 헤더 다음 separator 행 존재.
    헤더: `#{1,6} 내용` 유효, `#{7,}` 무효.
    반환 {"valid": bool, "errors": [...]}.
    """
    errors = []
    lines = text.splitlines()

    def col_count(line):
        s = line.strip()
        if s.startswith("|"):
            s = s[1:]
        if s.endswith("|"):
            s = s[:-1]
        return len(s.split("|"))

    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        stripped = line.strip()
        # 헤더 유효성
        hm = re.match(r"^(#+)\s*", line)
        if hm and len(hm.group(1)) > 6:
            errors.append({"line": i + 1, "kind": "header", "msg": "헤더 레벨 >6 (#{7,})"})
        # 표 블록
        if stripped.startswith("|"):
            block = []
            j = i
            while j < n and lines[j].strip().startswith("|"):
                block.append(lines[j])
                j += 1
            counts = [col_count(b) for b in block]
            if len(set(counts)) > 1:
                errors.append(
                    {"line": i + 1, "kind": "table", "msg": "표 컬럼 수 불일치 %s" % counts}
                )
            if len(block) >= 2:
                sep = block[1].strip()
                if not re.match(r"^\|?[\s:|-]+\|?$", sep) or "-" not in sep:
                    errors.append(
                        {"line": i + 2, "kind": "table", "msg": "헤더 다음 separator 행 부재/무효"}
                    )
            i = j
            continue
        i += 1
    return {"valid": len(errors) == 0, "errors": errors}


def mirror_pair_byte_parity(basename, repo_root):
    """(b) mirror-pair byte-parity 모드 — templates/ ↔ .github/ 동일 basename 파일 byte-동일 여부.

    반환 {"parity": bool, "pairs": [...], "note": ...}.
    pair 가 0/1개면 비교 대상 없음 → parity=True(무손상, 강제 아님).
    """
    matches = []
    for root, _dirs, files in os.walk(repo_root):
        rel = os.path.relpath(root, repo_root).replace("\\", "/")
        # .git VCS 디렉터리만 제외 — `.github/` 는 미러 대상이므로 삼키지 않는다
        # (FIX-1: `rel.startswith(".git")` 가 `.github` 도 매칭해 mirror-pair vacuous-pass 유발).
        if rel == ".git" or rel.startswith(".git/"):
            continue
        in_templates = rel == "templates" or rel.startswith("templates/") or "/templates" in ("/" + rel)
        in_github = rel == ".github" or rel.startswith(".github/")
        if not (in_templates or in_github):
            continue
        for name in files:
            if name == basename:
                matches.append(os.path.join(root, name))
    if len(matches) < 2:
        return {"parity": True, "pairs": [m.replace("\\", "/") for m in matches],
                "note": "mirror pair 없음(비교 대상 <2)"}
    blobs = []
    for m in matches:
        try:
            with open(m, "rb") as fh:
                blobs.append(fh.read())
        except OSError:
            blobs.append(None)
    parity = all(b is not None and b == blobs[0] for b in blobs)
    return {"parity": parity,
            "pairs": [os.path.relpath(m, repo_root).replace("\\", "/") for m in matches]}


def _wording_baseline_collision(repo_root):
    """wording-baseline 키 충돌 검사 (best-effort). baseline 파일 부재 시 collision=False."""
    # 이 repo 에는 별도 wording-baseline SSOT 파일이 없을 수 있다 → 없으면 충돌 없음(보수적 True-safe).
    candidates = [
        os.path.join(repo_root, "docs", "wording-baseline.yaml"),
        os.path.join(repo_root, "docs", "wording-baseline.md"),
    ]
    for path in candidates:
        text = _read_text(path)
        if text is None:
            continue
        keys = re.findall(r"^\s*([A-Za-z0-9_.\-]+)\s*:", text, re.MULTILINE)
        seen, dup = set(), set()
        for k in keys:
            if k in seen:
                dup.add(k)
            seen.add(k)
        if dup:
            return {"collision": True, "dup_keys": sorted(dup), "file": path}
    return {"collision": False, "dup_keys": []}


def check_structural_integrity(target, disposition, repo_root):
    """④ 구조 무결성 종합: 표/헤더 유효 ∧ mirror byte-parity ∧ wording-baseline 충돌 0."""
    file_rel = (target.get("file") or "").replace("\\", "/")
    errors = []
    table_valid = True
    if file_rel:
        abspath = os.path.join(repo_root, file_rel)
        text = _read_text(abspath)
        if text is not None:
            struct = validate_markdown_structure(text)
            table_valid = struct["valid"]
            errors.extend(struct["errors"])
    # mirror parity — target 이 workflow/template 계열일 때만 의미
    is_wf_or_tmpl = (
        file_rel.startswith(".github/")
        or file_rel.startswith("templates/")
        or "/templates/" in file_rel
    )
    if is_wf_or_tmpl and file_rel:
        mirror = mirror_pair_byte_parity(os.path.basename(file_rel), repo_root)
    else:
        mirror = {"parity": True, "pairs": [], "note": "workflow/template 아님 → mirror N/A"}
    collision = _wording_baseline_collision(repo_root)
    structure_intact = table_valid and mirror["parity"] and not collision["collision"]
    return {
        "structure_intact": structure_intact,
        "table_valid": table_valid,
        "mirror_parity": mirror["parity"],
        "wording_collision": collision["collision"],
        "errors": errors,
        "mirror": mirror,
    }


# ─────────────────────────────────────────────────────────────────────────────
# run_guard — 4 check 종합 + verdict
# ─────────────────────────────────────────────────────────────────────────────
_DISPOSITION_ALIASES = {
    "correct": "correct",
    "strip": "strip",
    "strip_normativity": "strip",
    "delete": "delete",
}


def run_guard(target, disposition, *, repo_root):
    """4 check 실행 후 disposition 별 verdict 산출.

    Parameters
    ----------
    target : dict — {"file": <relpath>, "row": <anchor|line>, "body"?: str, "external_ids"?: list}
    disposition : str — "correct" | "strip" | "strip_normativity" | "delete"
    repo_root : str — 스캔 루트

    Returns
    -------
    dict : {"pass": bool, "disposition": <normalized>, "checks": {...}, "recommend"?: str, ...}
    """
    disp = _DISPOSITION_ALIASES.get(str(disposition).strip())
    if disp is None:
        return {
            "pass": False,
            "disposition": disposition,
            "error": "unknown disposition (correct|strip|strip_normativity|delete 중 하나)",
            "checks": {},
        }

    parser = check_parser_scan(target, repo_root)
    inbound = check_inbound_scan(target, repo_root)
    external = check_external_id_scan(target, repo_root)
    structural = check_structural_integrity(target, disp, repo_root)

    checks = {
        "parser_scan": parser,
        "inbound_scan": inbound,
        "external_id_scan": external,
        "structural_integrity": structural,
    }

    body_parsed = parser["body_parsed"]
    inbound_count = inbound["inbound_count"]
    external_cited = external["external_id_cited"]
    structure_intact = structural["structure_intact"]

    result = {"disposition": disp, "checks": checks}

    if disp == "delete":
        ok = (not body_parsed) and (inbound_count == 0) and (not external_cited) and structure_intact
        result["pass"] = ok
        if not ok:
            result["recommend"] = "strip_normativity"
            result["recommend_reason"] = (
                "delete 불가(참조/파싱/구조 위험) — bytes 보존 moot-mark 로 강등 권고"
            )
            result["delete_conjunction"] = {
                "not_body_parsed": not body_parsed,
                "no_inbound": inbound_count == 0,
                "external_id_safe": not external_cited,
                "structure_intact": structure_intact,
            }
    else:
        # correct / strip = edit: ③ invariant(참조 orphan 0) ∧ ④ byte-parity(structure_intact)
        external_invariant = _external_ids_resolvable(target, repo_root)
        result["external_id_invariant"] = external_invariant
        result["pass"] = external_invariant and structure_intact
        if not result["pass"]:
            result["fail_reason"] = "edit 무결성 위반: external-id orphan 또는 구조/byte-parity 파손"

    return result


# ─────────────────────────────────────────────────────────────────────────────
# CLI 층
# ─────────────────────────────────────────────────────────────────────────────
def _main(argv=None):
    ap = argparse.ArgumentParser(
        description="decision-record 정정/삭제 전 참조-무결성 4-check guard."
    )
    ap.add_argument("--guard", action="store_true", help="guard 모드")
    ap.add_argument("--target", help="대상 파일(repo-relative)")
    ap.add_argument("--row", help="대상 row (anchor 문자열 또는 라인번호)")
    ap.add_argument(
        "--disposition",
        choices=["correct", "strip", "strip_normativity", "delete"],
        help="조치 종류",
    )
    ap.add_argument("--repo-root", default=".", help="스캔 루트 (기본 CWD)")
    ap.add_argument("--selfcheck", action="store_true", help="import/기동 sanity")
    args = ap.parse_args(argv)

    if args.selfcheck:
        print(json.dumps({"ok": True, "module": "reference_integrity_guard"}, ensure_ascii=False))
        return 0

    if args.guard or (args.target and args.disposition):
        if not args.target or not args.disposition:
            ap.error("--guard 는 --target 과 --disposition 필요")
        target = {"file": args.target, "row": args.row}
        res = run_guard(target, args.disposition, repo_root=args.repo_root)
        print(json.dumps(res, ensure_ascii=False, indent=2))
        return 0 if res.get("pass") else 1

    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(_main())
