#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# CFP-2829 S2 (leg A) — backward 파생 sync 엔진 (AC-3/4/5/8/9/14, §3.1-§3.8).
"""서술문서(Confluence 12) 방향반전 backward 파생 엔진 — leg A(offline/MCP-read, creds-free).

파이프라인 (Change Plan §3.1):
  Confluence 편집 → poll감지(--detect) → MCP READ(leg A, no creds)
    → ADF→md → _normalize_markdown → chunk → structure-gate-bridge(--derive, fail-closed)
    → git working-tree substrate write → git PR 제안(--propose, INV-A: PR-only)
  read 이중경로(INV-READ): 사람=Atlassian-first / 에이전트=git-substrate primary.

cutover flag = CFP2829_BACKWARD_SYNC_ENABLED (unset/"0"=OFF default) — OFF 시 backward 전면 skip
  (forward 무파괴, AC-3). flag ON 시에만 엔진 활성(AC-4).

leg 분리 (§3.10, born-broken 방지):
  leg A = MCP READ(getConfluencePage 등, no creds) + ADF→md + gate + git PR — 본 모듈(creds-free).
  leg B = property basic-auth REST(chunking store/anchor stamp, creds) — confluence_property_rest.py
          (InfraEngineer 소유). 본 모듈은 leg B 를 **hard import 하지 않는다** — creds 경로에서만 lazy import.

interface-freeze (§3.5 / R-1 / R-2 / R-5):
  3anchor.py 의 _normalize_markdown/_sha256_of_text/_git_head_sha/_git_sha_exists = importlib 동적 로드
  (3anchor.py 0줄 변경). offline 결정론 경로는 creds-free helper 직접 호출 — ATLASSIAN_* 를
  import-time·unconditional 접촉하지 않는다(leg A 는 creds 없이 buildable/testable, R-1).
  forward_sync.py 의 load_manifest = import 재사용(backward→forward 1방향 read-only, R-5).

INV-A (AC-5, offline scope): 산출 = git PR 제안 emit + direct git write(protected branch push) 0.
  auto-merge 구조적 비활성. branch protection/CODEOWNERS 실집행 = S3 (S2 는 offline 구조 assert 만).
"""
import argparse
import hashlib
import importlib
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

# Windows cp949 stdout 차단 (forward_sync L60-64 패턴).
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# ── sys.path 배선 (scripts/ + scripts/lib/) ─────────────────────────────────
_SCRIPTS_DIR = Path(__file__).resolve().parent
_LIB_DIR = _SCRIPTS_DIR / "lib"
for _p in (str(_SCRIPTS_DIR), str(_LIB_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

# ── 재사용 import (interface-freeze) ────────────────────────────────────────
import confluence_forward_sync as _forward   # R-5: load_manifest 재사용 (main-guard import-safe)  # noqa: E402
from confluence_property_chunking import (   # AC-11: chunking  # noqa: E402
    chunk, reassemble, anchor_a, CONSERVATIVE_BUDGET,
)
from sync_sentinel import (                   # AC-7: 순환차단 predicate  # noqa: E402
    SUBSTRATE_MARKER, commit_message_is_substrate, is_machine_authored_substrate,
    anchor_equality_skip, dedup_key,
)
from confluence_backward_gate import verify_substrate  # AC-2/AC-6: structure-gate-bridge  # noqa: E402


# ── 3anchor.py 4 helper importlib 동적 로드 (하이픈 파일, 0줄 변경 — R-1/R-2) ──
def _load_3anchor_helpers():
    """confluence-sync-3anchor.py 에서 creds-free helper 4종 동적 로드.

    module-level 에서 ATLASSIAN_* 를 읽지 않으므로 creds-free 로드 (R-1). 하이픈 파일명 →
    일반 import 문법 불가 → importlib.util.spec_from_file_location.
    """
    anchor_path = _SCRIPTS_DIR / "confluence-sync-3anchor.py"
    spec = importlib.util.spec_from_file_location("_cfp2829_threeanchor_backward", anchor_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_ta = _load_3anchor_helpers()
_normalize_markdown = _ta._normalize_markdown   # CRLF→LF + trailing-ws strip (byte-호환)
_sha256_of_text = _ta._sha256_of_text
_git_head_sha = _ta._git_head_sha
_git_sha_exists = _ta._git_sha_exists


# ── 예외 ────────────────────────────────────────────────────────────────────
class InvariantViolation(RuntimeError):
    """INV-A/INV-B/INV-READ 위반 — fail-closed 신호."""


import re
_DENY_BASIC_AUTH_RE = re.compile(r"Basic [A-Za-z0-9+/=]{20,}")


def pr_body_deny_scan(text: str) -> None:
    """SA-3: PR body/commit message 에 basic-auth 패턴 검출 시 fail-closed abort.

    leg A(creds-free)라 구조적 leak 0 — defense-in-depth 가드.
    """
    if text and _DENY_BASIC_AUTH_RE.search(text):
        raise InvariantViolation("SA-3 위반: PR body/commit message 에 basic-auth 패턴 검출 — fail-closed abort")


# ── cutover flag (AC-3/AC-4, §3.7) ──────────────────────────────────────────
FLAG_ENV = "CFP2829_BACKWARD_SYNC_ENABLED"


def backward_sync_enabled() -> bool:
    """cutover flag 판정 — unset/"0" = OFF(default). ON 시에만 backward 엔진 활성."""
    return os.environ.get(FLAG_ENV, "") not in ("", "0")


# ── anchor 반전 (AC-8, INV-B — offline 결정론) ──────────────────────────────
def substrate_anchor_a(markdown) -> str:
    """substrate git-equivalent markdown 의 anchor A = sha256(_normalize_markdown) hex.

    3anchor.py _sha256_of_file 동형(byte-호환). anchor A 해시 대상 = substrate markdown 유지 →
    알고리즘 불변, 신뢰근만 INV-B(승인 substrate)로 이동. 1-byte drift → 다른 hex(mismatch 100% 감지).
    """
    raw = markdown if isinstance(markdown, (bytes, bytearray)) else str(markdown).encode("utf-8")
    return hashlib.sha256(_normalize_markdown(bytes(raw))).hexdigest()


def anchor_mismatch(substrate_markdown, stored_anchor_a: str) -> bool:
    """substrate 재계산 anchor A 와 저장 anchor A 불일치 여부 (offline 결정론, mismatch 100% 감지)."""
    return substrate_anchor_a(substrate_markdown) != stored_anchor_a


# ── read 이중경로 (INV-READ, AC-9) ──────────────────────────────────────────
def resolve_read_source(subject: str) -> str:
    """read 주체 판별 → 서빙 경로 (INV-READ, AC-9 — read-poisoning 봉인).

    subject="agent" → "git-substrate"  (primary, Confluence 직독 아님 — 명목 표면 불신)
    subject="human" → "atlassian-first"(UX 표면)
    그 외 → ValueError (명시 계약).
    """
    if subject == "agent":
        return "git-substrate"
    if subject == "human":
        return "atlassian-first"
    raise ValueError(f"unknown read subject: {subject!r} (expected 'agent' | 'human')")


def _emit_read_audit_event(subject, live_anchor_a, git_source_hash) -> dict:
    """INV-READ divergence audit event emit (E-3, falsifiable — stderr JSON)."""
    event = {
        "event": "read_divergence",
        "subject": subject,
        "authoritative": "git-substrate",
        "live_anchor_a": live_anchor_a,
        "git_source_hash": git_source_hash,
    }
    print(json.dumps(event, ensure_ascii=False), file=sys.stderr)
    return event


def resolve_read_with_divergence(subject: str, live_anchor_a: str = None,
                                 git_source_hash: str = None) -> dict:
    """read 라우팅 + divergence(anchor mismatch) 시 git authoritative + audit(E-3, AC-9)."""
    source = resolve_read_source(subject)
    diverged = bool(live_anchor_a and git_source_hash and live_anchor_a != git_source_hash)
    result = {"subject": subject, "read_source": source, "diverged": diverged}
    if diverged:
        result["authoritative"] = "git-substrate"   # divergence → git 우선
        result["audit_event"] = _emit_read_audit_event(subject, live_anchor_a, git_source_hash)
    return result


# ── manifest 역방향 조회 (R-5 — backward→forward read-only, forward 무접촉) ──
def git_path_for(manifest: dict, page_id) -> str:
    """manifest 에서 page_id → git-path 역방향 조회 (O(n) 스캔). 없으면 None.

    forward_sync.py 의 page_id_for(정방향)과 대칭 — backward 자기 함수(forward 0줄 변경).
    """
    pages = (manifest or {}).get("pages", {}) or {}
    for path, entry in pages.items():
        pid = entry.get("page_id") if isinstance(entry, dict) else entry
        if pid is not None and str(pid) == str(page_id):
            return path
    return None


def load_manifest():
    """forward_sync.load_manifest 재사용 (R-5 — main-guard import-safe, cwd-relative)."""
    return _forward.load_manifest()


# ── 변경 감지 polling/dedup (AC-14 — deterministic, anchor B monotonic primary) ──
def detect_changes(candidates, seen=None) -> list:
    """polling: version-number(anchor B) monotonic + dedup_key 로 변경 집합 산출 (AC-14).

    candidates: [{"page_id":.., "version_number":.., ...}] — CQL/version diff 결과.
    seen: {page_id: 최근 처리 version} — 이미 처리 상태(idempotency, 중복 PR dedup).
    return: 신규(seen 부재) 또는 version 증가(monotonic)만 — 결정론.
    webhook=opportunistic(retry 미보장) → polling 이 truth 결정(IO-4).
    """
    seen = dict(seen or {})
    changed = []
    emitted = set()
    for c in candidates:
        pid = c.get("page_id")
        ver = c.get("version_number")
        if pid is None or ver is None:
            continue
        k = dedup_key(pid, ver)
        if k in emitted:               # 동일 batch 내 중복 제거
            continue
        prev = seen.get(pid)
        if prev is None or ver > prev:  # anchor B monotonic — 신규/증가만 변경
            changed.append(c)
            emitted.add(k)
            seen[pid] = ver
    return changed


# ── ADF → markdown (AC-7 APIContract / EC-4 — lossy-accept + adf_dropped_nodes[]) ──
# ADF-only 노드(md 등가 없음, "silently removed") — lossy-accept + metadata 기록(§5 EC-4).
#   source: atlassian-mcp-server issue 60/161 — media/panel/layout/table 복합/status/decision/color/macro.
ADF_ONLY_NODES = frozenset({
    "panel", "table", "tableRow", "tableCell", "tableHeader",
    "status", "decisionList", "decisionItem",
    "layoutSection", "layoutColumn",
    "extension", "bodiedExtension", "inlineExtension",
    "mediaGroup", "media", "mediaSingle",
    "expand", "nestedExpand", "inlineCard", "blockCard", "embedCard",
    "date", "mention", "taskList", "taskItem", "emoji",
})
# md 등가 없는 mark(inline) — 소실 기록(색상 등).
ADF_ONLY_MARKS = frozenset({"textColor", "backgroundColor", "underline", "subsup", "annotation"})


def _adf_marks_wrap(text: str, marks, dropped) -> str:
    for m in marks or []:
        mtype = m.get("type")
        if mtype == "strong":
            text = f"**{text}**"
        elif mtype == "em":
            text = f"*{text}*"
        elif mtype == "code":
            text = f"`{text}`"
        elif mtype == "strike":
            text = f"~~{text}~~"
        elif mtype == "link":
            href = (m.get("attrs") or {}).get("href", "")
            text = f"[{text}]({href})"
        elif mtype in ADF_ONLY_MARKS:
            dropped.append(f"mark:{mtype}")
    return text


def _adf_node_to_md(node, dropped, depth=0, ordered_idx=None) -> str:
    """ADF 노드 → markdown 재귀 변환. ADF-only 노드는 dropped 기록 후 skip(lossy-accept)."""
    if not isinstance(node, dict):
        return ""
    ntype = node.get("type")
    content = node.get("content", []) or []

    if ntype in ADF_ONLY_NODES:
        dropped.append(ntype)          # lossy-accept — out-of-model enrichment 소실 기록(E-2)
        return ""

    if ntype == "doc":
        blocks = [_adf_node_to_md(c, dropped, depth) for c in content]
        return "\n\n".join(b for b in blocks if b.strip())

    if ntype == "text":
        return _adf_marks_wrap(node.get("text", ""), node.get("marks"), dropped)

    if ntype == "hardBreak":
        return "\n"

    if ntype == "paragraph":
        return "".join(_adf_node_to_md(c, dropped, depth) for c in content)

    if ntype == "heading":
        level = int((node.get("attrs") or {}).get("level", 1))
        inner = "".join(_adf_node_to_md(c, dropped, depth) for c in content)
        return f"{'#' * max(1, min(6, level))} {inner}"

    if ntype == "blockquote":
        inner = "\n\n".join(_adf_node_to_md(c, dropped, depth) for c in content)
        return "\n".join(f"> {ln}" for ln in inner.split("\n"))

    if ntype == "codeBlock":
        lang = (node.get("attrs") or {}).get("language", "") or ""
        code = "".join(_adf_node_to_md(c, dropped, depth) for c in content)
        return f"```{lang}\n{code}\n```"

    if ntype == "rule":
        return "---"

    if ntype == "bulletList":
        items = []
        for c in content:
            item = _adf_node_to_md(c, dropped, depth + 1)
            items.append(f"- {item}")
        return "\n".join(items)

    if ntype == "orderedList":
        items = []
        for i, c in enumerate(content, start=1):
            item = _adf_node_to_md(c, dropped, depth + 1, ordered_idx=i)
            items.append(f"{i}. {item}")
        return "\n".join(items)

    if ntype == "listItem":
        parts = [_adf_node_to_md(c, dropped, depth) for c in content]
        return " ".join(p.strip() for p in parts if p.strip())

    # 알 수 없는 노드 — 정직 lossy 기록(out-of-model).
    dropped.append(ntype or "unknown")
    return ""


def adf_to_markdown(adf):
    """ADF document → (markdown, adf_dropped_nodes[]). lossy-accept: ADF-only=out-of-model(§5.5.C E-1).

    md-등가 노드는 충실 변환, ADF-only 노드(panel/macro/layout/table/status/decision/color)는
    dropped 기록 후 skip(정직 lossy). 무손실 canonical scope = markdown round-trip(SM-2).
    """
    dropped = []
    md = _adf_node_to_md(adf, dropped, depth=0)
    return md, sorted(set(dropped))


# ── audit trail metadata (E-2 — governance 추적성) ──────────────────────────
def build_substrate_commit_metadata(source_page_url, editor, timestamp,
                                    adf_dropped_nodes=None, anchor_a_hash=None) -> dict:
    """substrate commit metadata — Confluence source-page URL + editor + timestamp + 손실노드 (E-2)."""
    return {
        "source_page_url": source_page_url,
        "editor": editor,
        "timestamp": timestamp,
        "adf_dropped_nodes": list(adf_dropped_nodes or []),
        "anchor_a": anchor_a_hash,
        "substrate_marker": SUBSTRATE_MARKER,   # sentinel self-제외 (AC-7)
    }


# ── INV-A: git PR 제안-only (AC-5, offline 구조 assert) ─────────────────────
def _default_branch_name(rel_path: str) -> str:
    slug = rel_path.replace("\\", "/").replace("/", "-").replace(".md", "")
    return f"cfp2829-backward-{slug}"


def build_pr_proposal(rel_path, branch, base="main", title=None, body=None,
                      commit_metadata=None) -> dict:
    """git PR 제안 descriptor — auto_merge/direct-write 구조적 비활성(INV-A)."""
    proposal = {
        "kind": "git-pr-proposal",
        "base": base,
        "branch": branch,
        "rel_path": rel_path,
        "auto_merge": False,            # 구조적 비활성 (INV-A, AC-5)
        "direct_push_to_base": False,   # direct git write 금지 (INV-A, AC-5)
        "title": title or f"[backward-substrate] {rel_path}",
        "body": body or "",
        "commit_metadata": commit_metadata or {},
    }
    pr_body_deny_scan(proposal["title"])   # SA-3: basic-auth 패턴 fail-closed
    pr_body_deny_scan(proposal["body"])
    return proposal


def assert_pr_only(proposal: dict) -> None:
    """INV-A(AC-5): 산출은 git PR 제안-only. auto-merge/direct base write/base-branch 검출 시 fail-closed.

    fail-open escape hatch 부재 — 우회 경로 0.
    """
    if proposal.get("auto_merge"):
        raise InvariantViolation("INV-A 위반: auto_merge=True (자동머지 구조적 비활성 필수, AC-5)")
    if proposal.get("direct_push_to_base"):
        raise InvariantViolation("INV-A 위반: direct_push_to_base=True (direct git write 금지, PR-only, AC-5)")
    branch = proposal.get("branch")
    base = proposal.get("base")
    if not branch or branch == base:
        raise InvariantViolation(f"INV-A 위반: feature branch 부재/base 동일(branch={branch!r}, base={base!r}) — PR-only 위반")


# ── derive 파이프라인 (fail-closed 체이닝 — 어느 단계 실패 시 PR 미생성) ──────
def write_substrate_working_tree(repo, rel_path, markdown_bytes) -> str:
    """substrate markdown 을 git working-tree 에 write (commit/push 아님 — INV-A PR staging).

    파일 write 만 — direct git write(protected branch push) 0. 실 branch/commit/PR = propose 단계.
    """
    target = Path(repo) / rel_path.replace("\\", "/").lstrip("/")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(markdown_bytes)
    return str(target)


def derive_substrate(adf, rel_path, doc_type, budget=CONSERVATIVE_BUDGET,
                     source_page_url=None, editor=None, timestamp=None) -> dict:
    """ADF → md → _normalize_markdown(INV-T2) → chunk → structure-gate-bridge. fail-closed 체이닝.

    gate 미통과 시 chunk_properties=None → propose 거부(PR 미생성). ADF-only 노드 소실=lossy-accept
    + metadata(adf_dropped_nodes[], E-2). md-등가 손실 방어 = 하류 gate + anchor round-trip.
    """
    md, dropped = adf_to_markdown(adf)
    normalized = _normalize_markdown(md.encode("utf-8"))   # INV-T2 (자체 normalization bypass 금지)
    gate_passed = verify_substrate(normalized, doc_type, rel_path)   # AC-2/AC-6 fail-closed
    anchor = substrate_anchor_a(normalized)                          # AC-8 (offline 결정론)
    props = chunk(normalized, budget) if gate_passed else None       # AC-11 (fail-closed: gate 실패→None)
    metadata = build_substrate_commit_metadata(source_page_url, editor, timestamp, dropped, anchor)
    return {
        "rel_path": rel_path,
        "doc_type": doc_type,
        "markdown": normalized,          # bytes — git substrate(PR staging 대상)
        "anchor_a": anchor,
        "adf_dropped_nodes": dropped,
        "gate_passed": gate_passed,
        "chunk_properties": props,       # None if gate 실패(fail-closed 체이닝)
        "commit_metadata": metadata,
    }


def propose_pr(derive_result: dict, repo=".", branch=None, base="main", dry_run=True) -> dict:
    """derive 산출 → git PR 제안 (INV-A: PR-only, auto-merge 구조적 비활성, direct write 0).

    gate 미통과 substrate 는 PR 제안 불가(fail-closed 체이닝). dry_run=True(S2 default capability)면
    proposal descriptor 만 emit(실 git/gh 호출 0). dry_run=False 시 feature branch commit(marker
    trailer)+push+gh pr create (base-branch push/auto-merge 절대 없음).
    """
    if not derive_result.get("gate_passed"):
        raise InvariantViolation("gate 미통과 substrate 는 PR 제안 불가 (fail-closed 체이닝, AC-6)")
    rel = derive_result["rel_path"]
    branch = branch or _default_branch_name(rel)
    proposal = build_pr_proposal(rel, branch, base=base,
                                 commit_metadata=derive_result.get("commit_metadata"))
    assert_pr_only(proposal)             # INV-A (AC-5) — mutation: auto_merge/direct-write 삽입 시 RED

    if dry_run:
        proposal["executed"] = False
        return proposal

    _execute_pr_proposal(proposal, derive_result, repo)   # live git/gh (S3 loop 개방 시)
    proposal["executed"] = True
    return proposal


def _execute_pr_proposal(proposal, derive_result, repo) -> None:
    """live PR 실행 — feature branch commit(SUBSTRATE_MARKER trailer)+push+gh pr create.

    base-branch(main) push 절대 없음, auto-merge 없음(assert_pr_only 재확인 후에만 진입).
    """
    assert_pr_only(proposal)             # 재확인 (방어)
    rel = proposal["rel_path"]
    branch = proposal["branch"]
    base = proposal["base"]
    write_substrate_working_tree(repo, rel, derive_result["markdown"])
    trailer = f"\n\n{SUBSTRATE_MARKER}\nsource: {derive_result.get('commit_metadata', {}).get('source_page_url')}"
    commit_msg = f"[backward-substrate] {rel}{trailer}"
    pr_body_deny_scan(commit_msg)        # SA-3: basic-auth 패턴 fail-closed
    _run(["git", "-C", repo, "checkout", "-b", branch])
    _run(["git", "-C", repo, "add", rel])
    _run(["git", "-C", repo, "commit", "-m", commit_msg])
    _run(["git", "-C", repo, "push", "-u", "origin", branch])   # feature branch only (never base)
    _run(["gh", "pr", "create", "--base", base, "--head", branch,
          "--title", proposal["title"], "--body", proposal.get("body") or commit_msg])


def _run(cmd) -> None:
    subprocess.run(cmd, check=True)


# ── leg B lazy import (creds 경로 전용 — leg A creds-free 오염 금지) ─────────
def _lazy_leg_b():
    """leg B(property REST) lazy import. leg A(offline)는 절대 이 경로 미도달 — creds 측정만."""
    try:
        return importlib.import_module("confluence_property_rest")
    except ImportError as e:
        raise RuntimeError(
            "leg B(scripts/lib/confluence_property_rest.py, InfraEngineer 소유) 미가용 — "
            "leg A(offline/MCP-read)는 creds-free 유지, property REST 저장은 leg B 필요(creds)."
        ) from e


# ── CLI (--detect / --derive / --propose, flag early-exit) ──────────────────
def _read_json_arg(path):
    if not path:
        return None
    if path == "-":
        return json.loads(sys.stdin.read())
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _cli_detect(args) -> int:
    candidates = _read_json_arg(args.input) or []
    seen = _read_json_arg(args.state) or {}
    changed = detect_changes(candidates, seen)
    print(json.dumps({"changed": changed, "count": len(changed)}, ensure_ascii=False))
    return 0


def _cli_derive(args) -> int:
    adf = _read_json_arg(args.adf)
    if adf is None:
        print("[backward-sync] --derive 는 --adf <JSON> 필요.", file=sys.stderr)
        return 2
    result = derive_substrate(
        adf, args.rel_path, args.doc_type, budget=args.budget,
        source_page_url=args.source_url, editor=args.editor, timestamp=args.timestamp,
    )
    if result["gate_passed"] and args.write:
        write_substrate_working_tree(args.repo, args.rel_path, result["markdown"])
    # markdown(bytes) 은 emit 에서 제외(용량) — 요약만.
    summary = {k: v for k, v in result.items() if k not in ("markdown", "chunk_properties")}
    summary["markdown_bytes"] = len(result["markdown"])
    summary["chunk_count"] = (result["chunk_properties"] or {}).get("__manifest", {}).get("chunk_count") \
        if result["chunk_properties"] else None
    print(json.dumps(summary, ensure_ascii=False))
    return 0 if result["gate_passed"] else 1


def _cli_propose(args) -> int:
    adf = _read_json_arg(args.adf)
    if adf is None:
        print("[backward-sync] --propose 는 --adf <JSON> 필요.", file=sys.stderr)
        return 2
    result = derive_substrate(
        adf, args.rel_path, args.doc_type, budget=args.budget,
        source_page_url=args.source_url, editor=args.editor, timestamp=args.timestamp,
    )
    if not result["gate_passed"]:
        print(json.dumps({"proposal": None, "reason": "gate BLOCKED (fail-closed)"}, ensure_ascii=False))
        return 1
    proposal = propose_pr(result, repo=args.repo, branch=args.branch, dry_run=not args.no_dry_run)
    print(json.dumps({"proposal": proposal}, ensure_ascii=False))
    return 0


def build_parser():
    p = argparse.ArgumentParser(
        prog="confluence_backward_sync.py",
        description="backward 파생 sync 엔진 (CFP-2829 S2 leg A — flag CFP2829_BACKWARD_SYNC_ENABLED default OFF).",
    )
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--detect", action="store_true", help="polling: CQL/version diff + dedup (AC-14).")
    g.add_argument("--derive", action="store_true", help="ADF→md→normalize→chunk→gate (AC-2/AC-11).")
    g.add_argument("--propose", action="store_true", help="git PR 제안 (INV-A PR-only, AC-5).")
    p.add_argument("--input", default=None, help="--detect: candidates JSON 경로('-'=stdin).")
    p.add_argument("--state", default=None, help="--detect: seen dedup state JSON 경로.")
    p.add_argument("--adf", default=None, help="--derive/--propose: ADF document JSON 경로('-'=stdin).")
    p.add_argument("--rel-path", default="", help="repo-relative canonical 경로.")
    p.add_argument("--doc-type", default="", help="doc-locations doc_type 명(게이트-無=pass-through).")
    p.add_argument("--repo", default=".", help="git worktree 경로.")
    p.add_argument("--budget", type=int, default=CONSERVATIVE_BUDGET, help="chunk budget(JSON-encoded byte).")
    p.add_argument("--branch", default=None, help="--propose: feature branch 명(기본 자동 생성).")
    p.add_argument("--source-url", default=None, help="audit: Confluence source-page URL(E-2).")
    p.add_argument("--editor", default=None, help="audit: Confluence editor(E-2).")
    p.add_argument("--timestamp", default=None, help="audit: edit timestamp(E-2).")
    p.add_argument("--write", action="store_true", help="--derive: substrate 를 working-tree 에 write.")
    p.add_argument("--no-dry-run", action="store_true", help="--propose: live git/gh 실행(기본 dry-run capability).")
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)

    # cutover flag early-exit (AC-3/AC-4) — OFF 시 backward 전면 skip(forward 무파괴).
    if not backward_sync_enabled():
        print(f"[backward-sync] flag OFF ({FLAG_ENV} unset/0) — backward 전면 skip (forward 무파괴, AC-3).")
        return 0

    if args.detect:
        return _cli_detect(args)
    if args.derive:
        return _cli_derive(args)
    if args.propose:
        return _cli_propose(args)
    return 1


if __name__ == "__main__":
    sys.exit(main())
