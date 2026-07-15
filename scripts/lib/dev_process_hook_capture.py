#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# tier: [measurement]
# dev_process_hook_capture.py — dev-process-event-v1 hook-adapter (Port A) 공용 SSOT
#
# Carrier: CFP-2687 Phase 2 (구현) / Epic #2686 Story A — dev-process observability substrate
# 설계 SSOT: ADR-155 §결정 4(capture 이원화 — hook Port A / Barrier #2 NON-ambient lane)
#           + §결정 5(INV-8a/8b) + §결정 8(always-on α)
#           + change-plan 2026-07-15-cfp-2687 §3.4(hook NON-ambient · agent_type→lane map)
#           + §7.4(record-only non-blocking exit0) + Story §5.4(noise false-negative — 무변경 보존).
#
# 책임 (Port A hook-adapter 공용 로직 — D2 PreToolUse / D3 PostToolUse 가 import):
#   - resolve_lane(agent_type): NON-ambient lane 파생. agent_type→lane semi-open map.
#     미등재/부재 → "없음"(honest vacuous — consistent 위장 금지, 다른 신호로 lane 조작 금지).
#   - derive_story_key(): checkout/worktree basename `cfp-NNN` 에서 best-effort 파생(부재 → None).
#   - record_hook_event(): always-on α gate → INV-8b(capture_blob → append_event, emit_source="hook").
#   - noise 판정(should_capture_content): 5 noise-discard 규칙(§3.3) — content blob 억제만,
#     이벤트(fact) 자체는 보존(§5.4 over-discard 금지: 무변경 diff/0-byte 도 이벤트 기록).
#
# ★NON-ambient (Barrier #2): 본 hook 은 Stop-hook lane ambient 를 기대하지 않는다
#   (dependency direction: hook→env only). lane 은 payload agent_type/subagent_type 에서만 파생.
#
# 정직 천장(ADR-119): noise 판정은 heuristic(완전탐지 아님) — bias=RECORD(over-discard 회피).
#   lane map 은 semi-open — 미등재 agent 는 "없음"(fabricate 금지). agent 이름-lane 결정론 단정 안 함.

import os
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# wave-1 CONSUME + D4 gate (reuse-before-write — ADR-140). import 실패 시 path fallback.
try:
    from dev_process_blob_store import capture_blob
    from append_dev_process_event import append_event
    from dev_process_capture_activation import dev_process_capture_enabled
except Exception:  # pragma: no cover — import path fallback
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from dev_process_blob_store import capture_blob
    from append_dev_process_event import append_event
    from dev_process_capture_activation import dev_process_capture_enabled


_LANE_FALLBACK = "없음"
_EMPTY_AUDIT = {"redaction_applied": False, "redaction_count": 0, "redaction_rules_fired": []}


# ─────────────────────── NON-ambient lane map (semi-open) ───────────────────────
# agent_type(subagent_type) bare-name → lane_label. 미등재 → "없음"(honest vacuous).
# 값 = append_dev_process_event._LANE_LABELS 정합(10 lane + 없음). lane-agnostic /
# cross-cutting agent(공유 리뷰 worker · PMO · GitOps)은 **의도적으로 미등재**(static map 이
# 단일 lane 으로 해석 불가 → "없음". PL 이 domain 을 packet 으로 주입하므로 정적 결정 불가).
_AGENT_TYPE_TO_LANE = {
    # 요구사항
    "RequirementsPLAgent": "요구사항",
    "RequirementsAnalystAgent": "요구사항",
    "DomainAgent": "요구사항",
    "ResearcherAgent": "요구사항",
    "ChangeImpactAgent": "요구사항",
    "FeasibilityAgent": "요구사항",
    "ContinuityAgent": "요구사항",
    "codex-proactive-check": "요구사항",
    # 요구사항-리뷰
    "RequirementsReviewPLAgent": "요구사항-리뷰",
    # 설계
    "ArchitectPLAgent": "설계",
    "ArchitectAgent": "설계",
    "ArchitectAnalystAgent": "설계",
    "CodebaseMapperAgent": "설계",
    "RefactorAgent": "설계",
    "SecurityArchitectAgent": "설계",
    "TestContractArchitectAgent": "설계",
    "DataArchitectAgent": "설계",
    "ModuleArchitectAgent": "설계",
    "APIContractArchitectAgent": "설계",
    "InfraOperationalArchitectAgent": "설계",
    "LiveOpsDeputyAgent": "설계",
    "LiveOrderingDeputyAgent": "설계",
    # 설계-리뷰
    "DesignReviewPLAgent": "설계-리뷰",
    # 구현
    "DeveloperPLAgent": "구현",
    "DeveloperAgent": "구현",
    "InfraEngineerAgent": "구현",
    "DataEngineerAgent": "구현",
    "QADeveloperAgent": "구현",
    # 구현-리뷰
    "CodeReviewPLAgent": "구현-리뷰",
    # 구현-테스트
    "TestAgent": "구현-테스트",
    "IntegrationTestAgent": "구현-테스트",
    "StatefulTestAgent": "구현-테스트",
    # 보안-테스트
    "SecurityTestPLAgent": "보안-테스트",
    # 배포
    "DeployPLAgent": "배포",
    "DeployWorkerAgent": "배포",
    # 배포-리뷰
    "DeployReviewPLAgent": "배포-리뷰",
    "DeployReviewWorkerAgent": "배포-리뷰",
    "ProductionEvidenceDeputyAgent": "배포-리뷰",
    # (미등재 = 의도적 "없음"): ClaudeReviewAgent / CodexReviewAgent (lane-agnostic 공유 리뷰) /
    #                          PMOAgent / GitOpsAgent (cross-cutting).
}


def resolve_lane(agent_type):
    """NON-ambient lane 파생 — agent_type→lane semi-open map. 미등재/부재 → '없음'.

    namespace prefix('codeforge-develop:DeveloperPLAgent')는 strip 후 bare-name 으로 조회.
    honest vacuous: 미등재 agent 를 다른 신호로 lane 조작하지 않는다(consistent 위장 금지).
    """
    if not agent_type or not isinstance(agent_type, str):
        return _LANE_FALLBACK
    bare = agent_type.rsplit(":", 1)[-1].strip().strip("]").strip()
    return _AGENT_TYPE_TO_LANE.get(bare, _LANE_FALLBACK)


# ─────────────────────── story_key best-effort 파생 ───────────────────────
_STORY_RE = re.compile(r"(?i)cfp-?(\d+)")


def _extract_story_key(path):
    """단일 경로에서 cfp-NNN → 'CFP-NNN'. basename 우선, 실패 시 전체 경로. 부재 → None."""
    if not path:
        return None
    base = os.path.basename(os.path.normpath(str(path)))
    m = _STORY_RE.search(base)
    if m:
        return "CFP-" + m.group(1)
    m = _STORY_RE.search(str(path))  # 전체 경로 최후 시도(worktree 중첩 경로 대비)
    if m:
        return "CFP-" + m.group(1)
    return None


def derive_story_key(cwd=None):
    """checkout/worktree basename 의 cfp-NNN → 'CFP-NNN'(best-effort). 부재 → None.

    명시 cwd 주입 시 그 경로가 **authoritative**(auto-fallback 안 함 — caller 의도 존중).
    cwd=None(런타임 기본) 시 CLAUDE_PROJECT_DIR → os.getcwd() 순으로 auto-derive.
    (worktree basename 'cfp-2687-p2' → 'CFP-2687'. 파생 실패는 append 가 '' 로 관용 — non-blocking.)
    """
    if cwd is not None:
        return _extract_story_key(cwd)
    for cand in (os.environ.get("CLAUDE_PROJECT_DIR", ""), os.getcwd()):
        sk = _extract_story_key(cand)
        if sk:
            return sk
    return None


# ─────────────────────── noise 판정 (§3.3 5-rule, bias=RECORD) ───────────────────────
NOISE_SPINNER = "spinner"
NOISE_STREAM_DUP = "stream-token-dup"
NOISE_DEP_INSTALL = "dep-install-log"
NOISE_NOCHANGE_LIST = "nochange-file-list"
NOISE_VERBOSE = "low-signal-verbose"

# 진행 스피너 글리프(braille spinner + ascii spinner + progress bar block)
_SPINNER_CHARS = set("⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏|/-\\▏▎▍▌▋▊▉█░▒▓ ")
_RE_DEP_INSTALL = re.compile(
    r"(?im)^\s*("
    r"(?:added|removed|changed|audited)\s+\d+\s+packages"
    r"|Collecting\s+\S+"
    r"|Downloading\s+\S+"
    r"|Requirement already satisfied"
    r"|Successfully installed\s+\S+"
    r"|(?:Compiling|Downloading|Installing)\s+\S+\s+v?\d"
    r"|npm\s+(?:warn|WARN|notice)"
    r"|Resolving dependencies"
    r")"
)
_RE_NOCHANGE = re.compile(
    r"(?im)(nothing to commit|no changes|파일이 변경되지 않았|unchanged|"
    r"working tree clean|already up to date|no modifications)"
)


def _looks_like_spinner(text):
    """줄 대부분이 spinner/progress 글리프로만 이뤄짐(고밀도) → spinner noise."""
    stripped = text.strip()
    if not stripped:
        return False
    non_ws = [c for c in stripped if not c.isspace()]
    if not non_ws:
        return False
    spinner_ratio = sum(1 for c in non_ws if c in _SPINNER_CHARS) / len(non_ws)
    # 매우 보수적(0.9) — 실제 진단 텍스트 오탐 회피(bias=RECORD)
    return spinner_ratio >= 0.9


def _looks_like_stream_dup(text):
    """동일 non-trivial 라인이 압도적으로 반복(스트리밍 토큰 중복 echo)."""
    lines = [ln.strip() for ln in text.split("\n") if ln.strip()]
    if len(lines) < 12:
        return False
    uniq = len(set(lines))
    # 유니크 비율이 극히 낮고(≤10%) 라인이 충분히 많을 때만 — 보수적
    return uniq / len(lines) <= 0.10


def _looks_like_dep_install(text):
    """의존성 설치 로그 signature 라인이 다수 지배(npm/pip/cargo)."""
    lines = [ln for ln in text.split("\n") if ln.strip()]
    if len(lines) < 6:
        return False
    hits = sum(1 for ln in lines if _RE_DEP_INSTALL.search(ln))
    return hits >= 6 and (hits / len(lines)) >= 0.5


def _looks_like_nochange_list(text):
    """무변경 파일목록/‘변경 없음’ 서술 (verbose 목록형). ★단, 짧은 무변경 사실은 noise 아님."""
    if not _RE_NOCHANGE.search(text):
        return False
    # 무변경 문구 + 다수 파일목록 라인일 때만 noise(장황). 짧으면 fact 로 보존(§5.4).
    lines = [ln for ln in text.split("\n") if ln.strip()]
    return len(lines) >= 8


def _looks_like_low_signal_verbose(text):
    """진단가치 없는 초저엔트로피 verbose — 매우 긴데 유니크 라인 극소(보수적)."""
    lines = [ln.strip() for ln in text.split("\n") if ln.strip()]
    if len(lines) < 40:
        return False
    uniq = len(set(lines))
    return uniq <= 3  # 40+ 줄인데 유니크 ≤3 = 반복 verbose


def classify_noise(text):
    """text 가 pure noise 면 규칙명 반환, 아니면 None. 순서 = 구체 → 일반.

    ★bias=RECORD(§5.4 over-discard 금지): 확신 있을 때만 noise 판정. None = 정상 capture.
    """
    if not text or not text.strip():
        return None
    if _looks_like_spinner(text):
        return NOISE_SPINNER
    if _looks_like_dep_install(text):
        return NOISE_DEP_INSTALL
    if _looks_like_nochange_list(text):
        return NOISE_NOCHANGE_LIST
    if _looks_like_stream_dup(text):
        return NOISE_STREAM_DUP
    if _looks_like_low_signal_verbose(text):
        return NOISE_VERBOSE
    return None


# ─────────────────────── record (INV-8b, always-on α, non-blocking) ───────────────────────
def record_hook_event(event_type, *, content=None, agent_type=None, subagent_type=None,
                      lane_label=None, story_key=None, consumer_scope=None,
                      ledger_path=None, blob_root=None, apply_noise_filter=False, **fields):
    """Port A hook capture — always-on α gate → INV-8b(capture_blob → append_event, emit_source=hook).

    반환 event_id(미기록/실패/비활성 → None). 어떤 실패도 raise 안 함(record-only exit-0 — ADR-115).

    NON-ambient lane: lane_label 미지정 시 subagent_type(spawn target) 우선, 없으면 agent_type(self)
      로 resolve_lane(→ 미등재 '없음'). story_key 미지정 시 derive_story_key(best-effort).

    apply_noise_filter=True(주로 PostToolUse) 시 content 가 pure noise 면 blob 억제(content→None) —
      단 **이벤트(fact)는 그대로 기록**(§5.4 over-discard 금지: 무변경/노이즈도 index row 남김).
    """
    try:
        # always-on α — 비활성이면 아무것도 기록 안 함
        if not dev_process_capture_enabled(consumer_scope=consumer_scope):
            return None

        # NON-ambient lane 파생 (spawn target 우선 → self → 없음)
        if lane_label is None:
            src = subagent_type if subagent_type else agent_type
            lane_label = resolve_lane(src)  # 미등재/부재 → "없음" honest vacuous

        if story_key is None:
            story_key = derive_story_key()

        noise_rule = None
        if apply_noise_filter and content is not None:
            noise_rule = classify_noise(content)
            if noise_rule is not None:
                content = None  # blob 억제 — 그러나 이벤트(fact)는 아래에서 그대로 기록

        blob_ref = None
        audit = _EMPTY_AUDIT
        if content is not None:
            # ★INV-8b step (1): blob WRITTEN first (capture_blob 내부 INV-8a redact→hash→write)
            blob_ref, audit = capture_blob(content, root=blob_root)

        # ★INV-8b step (2): index row AFTER — blob_ref(hash)만 index 도달(content-blind)
        return append_event(
            ledger_path=ledger_path,
            event_type=event_type,
            emit_source="hook",
            consumer_scope=consumer_scope,
            story_key=story_key,
            lane_label=lane_label,
            blob_ref=blob_ref,
            redaction_applied=audit.get("redaction_applied", False),
            redaction_count=audit.get("redaction_count", 0),
            redaction_rules_fired=audit.get("redaction_rules_fired", []),
            **fields,
        )
    except Exception as exc:  # graceful degradation — 어떤 예외도 exit-0 semantics
        sys.stderr.write("[dev-process-hook-capture] WARN: record failed — %s\n" % exc)
        return None


# ─────────────────────── self-test (execution-backed) ───────────────────────
def _self_test():
    import json
    import tempfile
    import shutil

    failures = []

    def check(cond, msg):
        if not cond:
            failures.append(msg)

    # ── lane map: NON-ambient 파생 + 미등재 '없음' ──
    check(resolve_lane("DeveloperPLAgent") == "구현", "[l1] 구현 lane 미매핑")
    check(resolve_lane("codeforge-develop:DeveloperPLAgent") == "구현", "[l2] namespaced strip 실패")
    check(resolve_lane("ArchitectAgent") == "설계", "[l3] 설계 lane 미매핑")
    check(resolve_lane("ClaudeReviewAgent") == "없음", "[l4] lane-agnostic 이 없음 아님 (fabricate)")
    check(resolve_lane("UnknownFutureAgent") == "없음", "[l5] 미등재가 없음 fallback 아님")
    check(resolve_lane(None) == "없음", "[l6] None 이 없음 아님")
    check(resolve_lane("") == "없음", "[l7] 빈 문자열이 없음 아님")

    # ── story_key 파생 ──
    check(derive_story_key("/x/y/cfp-2687-p2") == "CFP-2687", "[s1] worktree basename 파생 실패")
    check(derive_story_key("/x/y/plugin-codeforge") is None, "[s2] cfp 없는데 None 아님")

    # ── noise 분류: bias=RECORD ──
    check(classify_noise("⠋⠙⠹⠸ ⠼⠴⠦⠧") == NOISE_SPINNER, "[n1] spinner 미검출")
    check(classify_noise("빌드 성공: 3 test 통과, diff 2 files") is None,
          "[n2] 정상 진단 텍스트가 noise 로 오탐 (over-discard)")
    check(classify_noise("") is None, "[n3] 빈 content noise 판정")
    dep = "\n".join(["added 12 packages", "Collecting foo", "Downloading bar",
                     "Requirement already satisfied", "Successfully installed baz",
                     "npm warn deprecated x", "Resolving dependencies"])
    check(classify_noise(dep) == NOISE_DEP_INSTALL, "[n4] dep-install 미검출")

    tmpdir = tempfile.mkdtemp(prefix="hook-capture-selftest-")
    ledger = os.path.join(tmpdir, "dev-process-event.jsonl")
    blob_root = os.path.join(tmpdir, "blobstore")

    # ── record: tool_call(hook) round-trip + emit_source=hook + NON-ambient lane ──
    eid = record_hook_event(
        "tool_call", content="pytest -q  # token=ghp_" + "a" * 36,
        agent_type="DeveloperPLAgent", consumer_scope="wrapper",
        ledger_path=ledger, blob_root=blob_root, story_key="CFP-2687",
    )
    check(eid is not None, "[r1] hook tool_call 미기록")
    with open(ledger, encoding="utf-8") as f:
        rows = [json.loads(ln) for ln in f if ln.strip()]
    r = rows[-1]
    check(r["emit_source"] == "hook", "[r1] emit_source != hook")
    check(r["lane_label"] == "구현", "[r1] NON-ambient lane 파생 실패")
    check(len(r["blob_ref"]) == 64, "[r1] blob_ref 미기록")
    rj = json.dumps(r, ensure_ascii=False)
    check("ghp_" not in rj, "[r1] token 이 index row 유입 (content-blind 위반)")

    # ── NON-ambient 미등재 lane → 없음 + vacuous (fabricate 금지) ──
    eid2 = record_hook_event(
        "tool_call", content="echo hi", agent_type="MysteryAgent",
        consumer_scope="wrapper", ledger_path=ledger, blob_root=blob_root, story_key="CFP-2687",
    )
    with open(ledger, encoding="utf-8") as f:
        rows = [json.loads(ln) for ln in f if ln.strip()]
    check(rows[-1]["lane_label"] == "없음", "[r2] 미등재 agent lane 이 없음 아님")

    # ── noise filter: pure noise → blob 억제하되 이벤트 보존(§5.4) ──
    eid3 = record_hook_event(
        "tool_call", content="⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏", agent_type="DeveloperPLAgent",
        consumer_scope="wrapper", ledger_path=ledger, blob_root=blob_root,
        story_key="CFP-2687", apply_noise_filter=True,
    )
    check(eid3 is not None, "[r3] noise 여도 이벤트(fact)는 보존돼야 (over-discard)")
    with open(ledger, encoding="utf-8") as f:
        rows = [json.loads(ln) for ln in f if ln.strip()]
    check(rows[-1]["blob_ref"] is None, "[r3] noise content 가 blob 억제 안 됨")

    # ── §5.4: 무변경 diff(content=None) — 이벤트 보존 ──
    eid4 = record_hook_event(
        "diff", content=None, agent_type="DeveloperPLAgent", consumer_scope="wrapper",
        ledger_path=ledger, blob_root=blob_root, story_key="CFP-2687",
    )
    check(eid4 is not None, "[r4] 무변경 diff 이벤트 미보존 (수정시도-무변경 fact 소실)")

    # ── activation gate: consumer default-false → 미기록 ──
    eid5 = record_hook_event(
        "tool_call", content="x", agent_type="DeveloperPLAgent", consumer_scope="consumer",
        ledger_path=ledger, blob_root=blob_root, story_key="CFP-2687",
    )
    check(eid5 is None, "[r5] consumer default-false 인데 기록됨")

    shutil.rmtree(tmpdir, ignore_errors=True)

    if failures:
        print("[dev_process_hook_capture --self-test] FAIL")
        for m in failures:
            print("  - " + m)
        return 1
    print("[dev_process_hook_capture --self-test] PASS "
          "(NON-ambient lane map + 미등재 없음; story_key 파생; noise bias=RECORD; "
          "INV-8b hook round-trip; content-blind; over-discard 금지; activation α)")
    return 0


def main():
    import argparse
    p = argparse.ArgumentParser(description="dev-process hook-adapter 공용 SSOT (CFP-2687 Phase 2)")
    p.add_argument("--self-test", action="store_true", help="execution-backed self-test")
    args = p.parse_args()
    if args.self_test:
        return _self_test()
    p.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
