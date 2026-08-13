"""AC-7 / AC-9 — 본 Story 산출물의 `ADR-064` 무접촉 · K-list(9항) 무접촉.

Story §8.0.2 RTM 명명 테스트 (이름 변경 금지 — `ac-traceability` Hop3 `born_missing`
이 symbol 실재를 대조한다):

  - `test_story_diff_excludes_adr064` (AC-7 / NG-19) — mutant: ADR-064 경로를 diff 에
    주입 → RED
  - `test_klist_untouched` (AC-9 / NG-20, K-1·2·5·6·7·8·10·11·12) — mutant: K-7 재제안
    문면 주입 → RED

★판별력 규율★ — 각 테스트는 **mutant kill + negative control 왕복**을 모두 수행한다.
"항상 RED" 와 "mutant 를 잡는 RED" 를 구별하지 못하는 단방향 assert 는 두지 않는다.

★작업 트리 무오염★ — 모든 mutant 주입은 `tmp_path` 안의 합성 git repo / 합성 문서
트리에서만 일어난다. 실 repo 는 **읽기 판정 1 회**만 한다.

Carrier: CFP-2926 Phase 2 (구현) / Story §8.0.8 NG-19·NG-20
"""

from __future__ import annotations

import io
import subprocess
from pathlib import Path

import pytest

try:
    import gate_verdict
    import check_story_diff_adr064 as ng19
    import check_klist_untouched as ng20
except ImportError as exc:  # pragma: no cover - 부트스트랩 실패
    pytest.skip("게이트 모듈 import 실패: %s" % (exc,), allow_module_level=True)


# ── 공용 helper ───────────────────────────────────────────────────────────
def _write(path: Path, text: str) -> None:
    """LF 고정 write (Windows CRLF 혼입 차단)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with io.open(str(path), "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def _read(path: Path) -> str:
    with io.open(str(path), "r", encoding="utf-8", newline="") as handle:
        return handle.read()


def _git(root: Path, *args: str) -> str:
    """git 실행 (실패 = 즉시 예외 — exit-masking 금지)."""
    proc = subprocess.run(
        ["git", "-C", str(root), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    assert proc.returncode == 0, "git %s 실패 rc=%d: %s" % (
        " ".join(args),
        proc.returncode,
        proc.stderr,
    )
    return proc.stdout.strip()


def _commit(root: Path, rel: str, body: str, message: str) -> str:
    _write(root / rel, body)
    _git(root, "add", "--", rel)
    _git(root, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "--quiet", "-m", message)
    return _git(root, "rev-parse", "HEAD")


def _init_repo(root: Path) -> None:
    root.mkdir(parents=True, exist_ok=True)
    _git(root, "init", "--quiet")
    _git(root, "config", "user.email", "t@t")
    _git(root, "config", "user.name", "t")


# ══════════════════════════════════════════════════════════════════════════
# AC-7 / NG-19
# ══════════════════════════════════════════════════════════════════════════
def test_story_diff_excludes_adr064(tmp_path, repo_root):
    """AC-7 — 본 Story diff 가 `archive/adr/ADR-064-*.md` 를 포함하지 않는다.

    [Mutant M-a : ADR-064 경로를 diff 에 주입 → RED(`ADR064_TOUCHED`)]
    [Mutant M-a2: ADR-064 을 rename → 구 경로가 delete 로 노출 → RED (`--no-renames` 가
                  load-bearing 임을 확인)]
    [Mutant M-b : base 오지정으로 diff 0 파일 → ★RED(`EMPTY_DIFF`)★ — vacuous 참 금지]
    [Mutant M-b2: base ref 미해석 → fail-closed RED(`BASE_UNRESOLVED`, exit 1)]
    [Negative control: 위 전건 revert 후 PASS(exit 0) 복귀]
    """
    # ── (1) 실 repo 1 회 판정 ────────────────────────────────────────────
    real = ng19.evaluate(Path(repo_root), base_arg="main", head_arg="HEAD")
    if real.verdict == gate_verdict.PASS:
        # PASS 는 "실제로 파일을 봤다" 는 조건 위에서만 유효하다.
        assert real.trace["diff_files"] > 0, "0 파일 위의 PASS = vacuous 참"
        assert real.trace["forbidden_matches"] == 0
        assert real.trace["base_sha"] and real.trace["head_sha"]
    else:
        # base 미해석(shallow clone 등)은 ★조용한 통과가 아니라★ fail-closed 여야 한다.
        assert real.verdict == gate_verdict.RED, real.reason
        assert any(
            code in real.reason
            for code in (ng19.R_BASE_UNRESOLVED, ng19.R_EMPTY_DIFF, ng19.R_ADR064_TOUCHED)
        ), real.reason

    # ── (2) 합성 repo — mutant 왕복 ─────────────────────────────────────
    root = tmp_path / "ng19repo"
    _init_repo(root)
    # ★base 시점에 ADR-064 가 이미 존재★ — 실제 main 의 형상을 모델링한다. 이래야
    # "Story 가 ADR-064 를 지우거나 rename 하는" 변경이 diff 에 노출된다.
    _write(root / "archive/adr/ADR-064-decision-principle-mandate.md", "# ADR-064\n")
    _git(root, "add", "--", "archive/adr/ADR-064-decision-principle-mandate.md")
    base_sha = _commit(root, "docs/seed.md", "# seed\n", "A")
    clean_sha = _commit(root, "docs/other.md", "# other\n", "A2")

    # negative control — ADR-064 무접촉 diff 는 PASS(exit 0).
    clean = ng19.evaluate(root, base_arg=base_sha, head_arg="HEAD")
    assert clean.verdict == gate_verdict.PASS, clean.reason
    assert clean.exit_code == 0
    assert clean.trace["diff_files"] == 1
    assert clean.trace["forbidden_matches"] == 0

    # M-a — ADR-064 편집 → RED.
    _commit(
        root,
        "archive/adr/ADR-064-decision-principle-mandate.md",
        "# ADR-064 (mutant edit)\n",
        "B: touch ADR-064",
    )
    touched = ng19.evaluate(root, base_arg=base_sha, head_arg="HEAD")
    assert touched.verdict == gate_verdict.RED, touched.reason
    assert touched.exit_code == 1
    assert ng19.R_ADR064_TOUCHED in touched.reason
    assert touched.trace["forbidden_matches"] == 1

    # negative control — mutant 커밋 제거 후 PASS 복귀 (왕복).
    _git(root, "reset", "--hard", "--quiet", clean_sha)
    reverted = ng19.evaluate(root, base_arg=base_sha, head_arg="HEAD")
    assert reverted.verdict == gate_verdict.PASS, reverted.reason
    assert reverted.exit_code == 0

    # M-a2 — ADR-064 을 rename 으로 치우면 구 경로가 delete 로 노출 → RED.
    #   `--no-renames` 가 load-bearing: rename 검출을 켜면 git 이 이를 R 로 접어
    #   구 경로가 사라질 수 있다. base 시점에 파일이 존재해야 성립하는 시나리오다.
    _git(root, "mv", "archive/adr/ADR-064-decision-principle-mandate.md", "archive/adr/ADR-999-x.md")
    _git(root, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "--quiet", "-m", "B2: rename")
    renamed = ng19.evaluate(root, base_arg=base_sha, head_arg="HEAD")
    assert renamed.verdict == gate_verdict.RED, renamed.reason
    assert ng19.R_ADR064_TOUCHED in renamed.reason

    # negative control — rename 커밋 제거 후 PASS 복귀 (왕복).
    _git(root, "reset", "--hard", "--quiet", clean_sha)
    reverted = ng19.evaluate(root, base_arg=base_sha, head_arg="HEAD")
    assert reverted.verdict == gate_verdict.PASS, reverted.reason
    assert reverted.exit_code == 0

    # M-b — base 오지정 → diff 0 파일 → ★RED★ (0 매치를 '미포함'으로 읽지 않는다).
    empty = ng19.evaluate(root, base_arg=clean_sha, head_arg="HEAD")
    assert empty.verdict == gate_verdict.RED, empty.reason
    assert empty.exit_code == 1
    assert ng19.R_EMPTY_DIFF in empty.reason
    assert empty.trace["diff_files"] == 0

    # M-b2 — base ref 미해석 → fail-closed RED.
    unresolved = ng19.evaluate(root, base_arg="no-such-ref-cfp2926", head_arg="HEAD")
    assert unresolved.verdict == gate_verdict.RED, unresolved.reason
    assert unresolved.exit_code == 1
    assert ng19.R_BASE_UNRESOLVED in unresolved.reason

    # head 미해석도 동일하게 fail-closed.
    bad_head = ng19.evaluate(root, base_arg=base_sha, head_arg="no-such-head-cfp2926")
    assert bad_head.verdict == gate_verdict.RED, bad_head.reason
    assert ng19.R_HEAD_UNRESOLVED in bad_head.reason

    # 4항목 — trace numeric + identity_probe resolved-target echo.
    assert isinstance(reverted.trace["diff_files"], int)
    probe = reverted.identity_probe
    assert probe["base_sha"] == base_sha
    assert probe["forbidden_path_pattern"] == ng19.FORBIDDEN_PATH_PATTERN.pattern
    assert probe["diff_file_digest_sha256"]
    assert "git -C <repo_root> diff --name-only -z --no-renames" in probe["diff_command"]


# ══════════════════════════════════════════════════════════════════════════
# AC-9 / NG-20
# ══════════════════════════════════════════════════════════════════════════
EXPECTED_K_IDS = ["K-1", "K-2", "K-5", "K-6", "K-7", "K-8", "K-10", "K-11", "K-12"]

# Story §4.3 D 의 K-7 재제안 mutant 문면 (명문 DEFER 를 뒤집는 도입 선언).
K7_REPROPOSAL = (
    "- **env=1 auto-wake-parent dispatcher 를 본 Story 에서 도입한다** (종전 DEFER 판정 대체).\n"
)


def _build_klist_tree(root: Path) -> Path:
    """K 항목 9 개의 기결정 앵커만 심은 최소 합성 트리 (전건 PASS 여야 한다)."""
    bodies: dict = {}
    for item in ng20.K_ITEMS:
        rel = str(item["anchor_path"])
        bodies.setdefault(rel, ["# %s (합성 앵커 트리)" % (rel,)])
        bodies[rel].append(str(item["anchor_text"]))
    for rel, lines in bodies.items():
        _write(root / rel, "\n".join(lines) + "\n")
    return root


def test_klist_untouched(tmp_path, repo_root):
    """AC-9 — K-1·2·5·6·7·8·10·11·12 (9항) 무접촉.

    [Mutant M-c : K-7 재제안 문면 주입 → RED(`KLIST_WEAKENED`)]
    [Mutant M-e : K-1 nested TEAMS 금지 앵커 삭제 → RED(`KLIST_ANCHOR_MISSING`) — leg-A]
    [Mutant M-d : 스캔 경로 오타로 0 파일 → ★RED(`EMPTY_SCAN_TARGET`)★ — vacuous 참 금지]
    [Mutant M-f : 비-UTF8 문서 → fail-closed RED(`UNPARSEABLE_DOC`, exit 1)]
    [Negative control: 전건 revert 후 PASS(exit 0) 복귀]
    [오검출 회귀 가드: `재제안 금지` 형태의 **기결정 재확인** 문면은 위반 아님]
    """
    # ── (0) 9 항 정의 자체가 Story §4.3 D 와 일치 ───────────────────────
    assert [str(i["id"]) for i in ng20.K_ITEMS] == EXPECTED_K_IDS
    assert len(ng20.K_ITEMS) == ng20.EXPECTED_K_COUNT == 9

    # ── (1) 실 repo 1 회 판정 ────────────────────────────────────────────
    real = ng20.evaluate(Path(repo_root))
    assert real.verdict == gate_verdict.PASS, real.reason
    assert real.trace["files_scanned"] > 0, "0 파일 위의 PASS = vacuous 참"
    assert real.trace["k_items_compared"] == 9
    assert real.trace["anchors_checked"] == 9
    assert real.trace["weakening"] == 0
    assert real.trace["ambiguous"] == 0
    assert sorted(real.trace["per_k_item"].keys()) == sorted(EXPECTED_K_IDS)
    assert real.identity_probe["k_excluded_from_ac9"] == ["K-3", "K-4", "K-9"]
    assert real.identity_probe["scanned_file_digest_sha256"]

    # ── (2) 합성 트리 — mutant 왕복 ─────────────────────────────────────
    tree = _build_klist_tree(tmp_path / "ng20tree")
    baseline = ng20.evaluate(tree)
    assert baseline.verdict == gate_verdict.PASS, baseline.reason
    assert baseline.exit_code == 0
    assert baseline.trace["anchors_checked"] == 9
    assert baseline.trace["files_scanned"] > 0

    # M-c — K-7 재제안 문면 주입 → RED.
    playbook = tree / "docs/orchestrator-playbook.md"
    original = _read(playbook)
    _write(playbook, original + K7_REPROPOSAL)
    weakened = ng20.evaluate(tree)
    assert weakened.verdict == gate_verdict.RED, weakened.reason
    assert weakened.exit_code == 1
    assert ng20.R_WEAKENED in weakened.reason
    assert weakened.trace["weakening"] == 1
    assert weakened.trace["per_k_item"]["K-7"]["weakening"] == 1

    # negative control — 주입 줄 제거 후 PASS 복귀 (왕복).
    _write(playbook, original)
    assert ng20.evaluate(tree).verdict == gate_verdict.PASS

    # M-e — K-1 앵커(nested TEAMS 금지) 삭제 → RED (leg-A. AC-9 teams 축 assert).
    k1 = next(i for i in ng20.K_ITEMS if i["id"] == "K-1")
    anchor_file = tree / str(k1["anchor_path"])
    anchor_original = _read(anchor_file)
    _write(
        anchor_file,
        "\n".join(
            line for line in anchor_original.split("\n") if str(k1["anchor_text"]) not in line
        ),
    )
    anchor_gone = ng20.evaluate(tree)
    assert anchor_gone.verdict == gate_verdict.RED, anchor_gone.reason
    assert anchor_gone.exit_code == 1
    assert ng20.R_ANCHOR_MISSING in anchor_gone.reason
    assert "K-1" in anchor_gone.reason

    # negative control — 앵커 복원 후 PASS 복귀 (왕복).
    _write(anchor_file, anchor_original)
    assert ng20.evaluate(tree).verdict == gate_verdict.PASS

    # M-d — 스캔 경로 오타(docs → docsX): 문서는 실재하지만 root 가 어긋나 0 파일 → RED.
    typo = tmp_path / "ng20typo"
    _write(typo / "docsX" / "orchestrator-playbook.md", original)
    empty_scan = ng20.evaluate(typo)
    assert empty_scan.verdict == gate_verdict.RED, empty_scan.reason
    assert empty_scan.exit_code == 1
    assert ng20.R_EMPTY_SCAN in empty_scan.reason
    assert empty_scan.trace["files_scanned"] == 0

    # M-f — 비-UTF8 문서 → fail-closed RED (조용한 파일 제외 금지).
    bad = tree / "docs" / "_ng20_badbytes.md"
    bad.parent.mkdir(parents=True, exist_ok=True)
    with io.open(str(bad), "wb") as handle:
        handle.write(b"K-list \xff\xfe invalid utf8\n")
    unparseable = ng20.evaluate(tree)
    assert unparseable.verdict == gate_verdict.RED, unparseable.reason
    assert unparseable.exit_code == 1
    assert ng20.R_UNPARSEABLE in unparseable.reason

    # negative control — 문제 파일 제거 후 PASS 복귀 (왕복).
    bad.unlink()
    assert ng20.evaluate(tree).verdict == gate_verdict.PASS

    # ── (3) 오검출 회귀 가드 ────────────────────────────────────────────
    # `재제안 금지` = 기결정을 **재확인**하는 문장 — 위반으로 잡히면 K-list 를 지키라고
    # 쓴 문서가 K-list 위반이 된다 (실측 반례: review-pl-base.md:634).
    upheld_line = "**★env=1 auto-wake-parent dispatcher 재제안 금지** — full auto-wake substrate 부재"
    match = next(i for i in ng20.K_ITEMS if i["id"] == "K-7")["topic"].search(upheld_line)
    assert match is not None
    assert ng20.classify_window(upheld_line, match.start(), match.end())[0] == ng20.CLS_MENTION

    # 반대로 도입 선언은 반드시 weakening 으로 분류돼야 한다 (분류기 양방향 판별력).
    reproposal_line = K7_REPROPOSAL.strip()
    match2 = next(i for i in ng20.K_ITEMS if i["id"] == "K-7")["topic"].search(reproposal_line)
    assert match2 is not None
    assert (
        ng20.classify_window(reproposal_line, match2.start(), match2.end())[0]
        == ng20.CLS_WEAKENING
    )
