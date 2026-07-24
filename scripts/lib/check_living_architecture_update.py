"""
scripts/lib/check_living_architecture_update.py
CFP-2813 Phase 2 — Living Architecture per-PR 최신성 게이트 core SSOT (독립 재구현, stdlib-only).

기능:
  PR 이 구조 표면(scripts/** · templates/** · plugins/<X>/** 등)을 변경했는데 대응하는
  Living Architecture doc(docs/architecture/codeforge-family.md + 6 lane
  plugins/<X>/docs/architecture/<X>.md)를 갱신하지도, no-op declare 하지도 않으면 FAIL.
  판정축 = 변경-문서 coupling(touch/timing closed-binary) — 날짜(git commit / last_captured)가
  신뢰 불가하므로 "무엇을 언제 바꿨나" 만 본다(Change Plan §2 freshness 이원성 대응).

  cross-import 0 — 다른 check_*.py 를 import 하지 않는다(게이트별 완전 독립 core 관행, Change Plan §2).

알고리즘 (Change Plan §3.2 verbatim):
  1. capability 판정: arch doc 0개 보유 → honest no-op + 명시 Success (exit 0).
  2. 3-class closed 분류(classify): 구조(plugin/family) / 비구조 / unknown-surface(fail-closed).
     unknown-surface → FAIL. 구조 표면 0 → 명시 Success.
  3. doc 집합 D 도출(derive_docs): glob self-discovery. plugin 표면인데 doc 부재 → mapping-miss FAIL.
  4. per-doc closed-binary(judge): (a) doc 가 frontmatter 외 본문 diff ≥1 hunk 로 변경 OR
     (b) PR body 유효 no-op marker(global 또는 per-doc). 둘 다 아니면 missing-update FAIL.
  5. marker 형식 위반(빈 rationale / stoplist / 길이 미달 / 구조 미완성) → invalid-declare FAIL.
  6. bypass 라벨 = workflow 층 소관(본 core 미처리 — check-bypass-audit-comment.sh 배선).
  7. scanned-N execution-trace 의무 방출(ADR-154 AC-5).

honest ceiling (필수 — L2/L3 분할, ADR-119 / Change Plan §3.4/§3.5):
  - 본 게이트(L2) = presence / shape / coupling 까지만 판정:
      · 대응 doc 가 변경 파일에 있는가 (touch presence)
      · 그 변경이 frontmatter-only 가 아닌가 (shape — 날짜-touch gaming 차단)
      · 변경 표면 ↔ doc 집합 bijection 이 성립하는가 (coupling — mapping-miss)
      · no-op marker 형식이 유효한가 (shape)
  - "doc 본문이 델타를 실제로·의미 있게 반영했는가"(L3 substance) 는 기계 판정 불가 —
    DesignReviewPL review-tier 소관(review-verdict-v4 living_architecture_updated_self_check_passed
    + living-architecture-not-updated finding). 본문 1줄 어휘 치환도 (a) 를 충족한다(L2 천장 정직 공개).
  - "기계 강제 100%" over-claim 금지. 본 게이트는 최신성 결박의 필요조건이지 충분조건 아님.
  - marker rationale 의 실질 토큰 padding gaming(stop-phrase + 무의미 토큰 부풀리기)은 L2 로 완봉
    불가 — rationale 타당성 판정은 L3 review-tier 잔존(형식 floor·정규화 anchored 까지가 기계 천장).

resource-safety (marker 정규식 — ADR-082 §결정16 정직):
  - MARKER_RE 는 전 quantifier bounded({1,64}/{0,8}/{1,400}), 중첩 모호 quantifier 0
    (CWE-1333 ReDoS-safe). paired proof-reference =
    tests/scripts/test_check-living-architecture-update.sh 의 ReDoS 시간-상한 회귀 테스트
    (악의 표본 wall-clock bound). presence != truth — 참됨 반증은 그 self-test lane 소관.
  - marker 내용 = 비실행 텍스트 취급 — 파싱 결과(rationale/doc-id)를 shell 명령·파일 경로·eval
    구성에 사용 금지. doc-id 는 [a-z0-9-]{1,64} 화이트리스트 매칭 후 glob 결과와 대조만.

Exit-code 3-tier (ADR-061 / Change Plan §4):
  0: PASS — 명시 Success(구조 표면 0) / honest no-op(arch doc capability 미보유) / 전 doc 충족
  1: 위반 검출 — missing-update | invalid-declare | mapping-miss | unknown-surface (각 ::error:: 1줄)
  2: meta-error — git 미설치 / repo 아님 / unparseable 입력 (fail-closed, silent skip 금지)

Test seam (self-test 전용 — env 주입, 정확히 이 목록):
  PR_BODY                    — PR body 텍스트(marker 파싱 입력). 미설정 = 빈 문자열(marker 부재).
  LIVING_ARCH_PR_BODY_FILE   — PR body 파일 경로(PR_BODY 우선). CI 는 대형 body 를 파일로 전달.
  LIVING_ARCH_CHANGED_MOCK   — newline-separated 변경 경로 주입(파일 목록만 우회). frontmatter
                               body-diff 판정은 여전히 실 git(fixture repo 전제).
"""

import argparse
import os
import re
import subprocess
import sys
from enum import Enum
from pathlib import Path, PurePosixPath
from typing import List, Optional, Set, Tuple, Union

# Windows cp949 stdout encoding 차단 (ADR-061 standardize)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
SCRIPT_NAME = "check-living-architecture-update"
FAMILY_DOC = "docs/architecture/codeforge-family.md"
FAMILY_STEM = "codeforge-family"
CONSUMER_DEFAULT_STRUCTURAL = ("src/",)  # consumer fallback 기본 구조 표면 (overlay 확장-only)

# no-op marker 계약 정규식 (Change Plan §3.3 — 자구 그대로).
#   전 quantifier bounded(ReDoS-safe, CWE-1333). group(1)=doc-id(optional), group(2)=rationale.
MARKER_RE = re.compile(
    r"\[living-arch-no-impact(?:\(([a-z0-9-]{1,64})\))?:[ \t]{0,8}([^\]\r\n]{1,400})\]"
)
MARKER_PREFIX_LITERAL = "[living-arch-no-impact"  # 구조 미완성 attempt 검출용
GLOBAL_DOC_ID = "*"                                 # 내부 sentinel — 실제 doc-id 아님
RATIONALE_MIN = 15                                  # Change Plan §3.3 rationale floor (길이 축 — 독립)
# 단순 부정 stoplist — 정규화(소문자·구두점/공백→토큰) 후 token-anchored 검사 (길이 floor 와 독립 축).
#   floor 선행 dead-branch 회피(QADev M7 kill): stoplist 항목이 <15자여도 padding("not applicable ....")
#   으로 floor 통과분이 stoplist 분기에 도달해야 함 → 정규화 anchored + residual-token 임계.
#   순수 무제한 substring 매칭 금지 — 실질 근거 문장이 어구 포함만으로 오차단되면 게이트 신뢰 훼손.
STOPLIST_SOURCE = ("해당 없음", "not applicable", "n/a")     # 사람 가독 원구 (아래 NORM 은 pre-computed)
STOPLIST_NORM_TOKENS = (("해당", "없음"), ("not", "applicable"), ("n", "a"))  # 위 원구의 _normalize_tokens 결과
RESIDUAL_MIN_SUBSTANTIVE = 2                         # stop-phrase anchored 후 잔여 실질 토큰이 미만이면 gaming 판정
_NORM_TOKEN_SPLIT_RE = re.compile(r"[^0-9a-z가-힣]+")  # 정규화 분할 (bounded char-class + 단일 +, ReDoS-safe)

# 구조 표면(family.md 도출) — closed enum (Change Plan §3.2).
FAMILY_STRUCTURAL_PREFIXES = (
    "scripts/",
    "templates/",
    ".github/workflows/",
    ".github/scripts/",
    "hooks/",
    "skills/",
    "overlay/",
    ".claude/agents/",
    "docs/inter-plugin-contracts/",
    ".claude-plugin/",
)
FAMILY_STRUCTURAL_EXACT = ("CLAUDE.md", "plugin.json")

# 비구조 표면(발동 없음) — closed enum ("그 외" open-set 아님, Change Plan §3.2 F-4).
NON_STRUCTURAL_PREFIXES = (
    "archive/",
    "tests/",
    "examples/",
    "docs/",       # docs/inter-plugin-contracts/** 는 위 구조 side 소속(structural 이 먼저 매칭)
    ".claude/",    # .claude/agents/** 는 위 구조 side 소속(structural 이 먼저 매칭)
    ".github/",    # .github/workflows·scripts 는 위 구조 side 소속(structural 이 먼저 매칭)
)
NON_STRUCTURAL_EXACT = (".gitignore", ".gitattributes", "mark.toml", "requirements.txt")

HUNK_RE = re.compile(r"^@@ -(\d+)(?:,\d+)? \+(\d+)(?:,\d+)? @@")


# ---------------------------------------------------------------------------
# Enums / sentinel types
# ---------------------------------------------------------------------------
class SurfaceClass(Enum):
    STRUCTURAL_PLUGIN = "structural-plugin"    # plugins/<X>/** → plugins/<X>/docs/architecture/<X>.md
    STRUCTURAL_FAMILY = "structural-family"    # 위 family 표면 → docs/architecture/codeforge-family.md
    NON_STRUCTURAL = "non-structural"          # 발동 없음
    UNKNOWN = "unknown"                        # 양측 enum 미매칭 → fail-closed


class Verdict(Enum):
    PASS = "pass"
    FAIL = "fail"
    META_ERROR = "meta-error"


class FailureCategory(Enum):
    MISSING_UPDATE = "missing-update"
    INVALID_DECLARE = "invalid-declare"
    MAPPING_MISS = "mapping-miss"
    UNKNOWN_SURFACE = "unknown-surface"


class MappingMiss:
    """derive_docs 매핑 실패 sentinel — (surface_path, expected_doc) 목록."""

    def __init__(self, surfaces: List[Tuple[str, str]]):
        self.surfaces = surfaces


class MarkerSet:
    """파싱된 유효 no-op marker 집합."""

    def __init__(self) -> None:
        self.global_present = False
        self.doc_ids: Set[str] = set()

    def covers(self, doc_id: str) -> bool:
        return self.global_present or doc_id in self.doc_ids


class Mode(Enum):
    WRAPPER = "wrapper"     # dogfood — family.md + 6 lane doc (full §3.2 알고리즘)
    CONSUMER = "consumer"   # capability-conditional fallback — src/** + 보유 doc 전체
    NO_OP = "no-op"         # arch doc capability 미보유 → honest Success


# ---------------------------------------------------------------------------
# Pure functions (contract — cross-import 0, git 무의존)
# ---------------------------------------------------------------------------
def _norm(path: str) -> str:
    p = path.strip().replace("\\", "/")
    while p.startswith("./"):
        p = p[2:]
    return p.lstrip("/")


def classify(path: str) -> SurfaceClass:
    """경로 1개를 3-class closed enum 으로 분류 (구조/비구조/unknown, Change Plan §3.2)."""
    p = _norm(path)
    if not p:
        return SurfaceClass.NON_STRUCTURAL
    segs = p.split("/")

    # 1. plugins/<X>/** — structural-plugin (lane arch doc self-trigger 포함 = benign, F-3)
    if len(segs) >= 2 and segs[0] == "plugins":
        return SurfaceClass.STRUCTURAL_PLUGIN

    # 2. family 구조 표면 (structural 을 non-structural 보다 먼저 — 예외 sub-path 정합)
    for pre in FAMILY_STRUCTURAL_PREFIXES:
        if p == pre.rstrip("/") or p.startswith(pre):
            return SurfaceClass.STRUCTURAL_FAMILY
    if p in FAMILY_STRUCTURAL_EXACT:
        return SurfaceClass.STRUCTURAL_FAMILY

    # 3. 비구조 표면 — closed enum
    if len(segs) == 1 and p.endswith(".md"):   # root *.md (CLAUDE.md 는 위에서 이미 구조)
        return SurfaceClass.NON_STRUCTURAL
    if p in NON_STRUCTURAL_EXACT:
        return SurfaceClass.NON_STRUCTURAL
    for pre in NON_STRUCTURAL_PREFIXES:
        if p == pre.rstrip("/") or p.startswith(pre):
            return SurfaceClass.NON_STRUCTURAL

    # 4. unknown — fail-closed (미래 신규 표면)
    return SurfaceClass.UNKNOWN


def derive_docs(paths: List[str], repo_root: Path) -> Union[Set[PurePosixPath], MappingMiss]:
    """구조 표면 경로 → 대응 Living Architecture doc 집합 (glob self-discovery, Change Plan §3.2 D2).

    plugins/<X>/** 표면인데 plugins/<X>/docs/architecture/<X>.md 파일 부재 → MappingMiss(mapping-miss).
    비구조/unknown 경로는 무기여(unknown 은 caller 가 derive_docs 이전에 fail-closed 처리)."""
    docs: Set[PurePosixPath] = set()
    missing: List[Tuple[str, str]] = []
    for path in paths:
        cls = classify(path)
        if cls == SurfaceClass.STRUCTURAL_PLUGIN:
            plugin = _norm(path).split("/")[1]
            doc = PurePosixPath("plugins") / plugin / "docs" / "architecture" / (plugin + ".md")
            if (repo_root / doc).is_file():
                docs.add(doc)
            else:
                missing.append((path, str(doc)))
        elif cls == SurfaceClass.STRUCTURAL_FAMILY:
            doc = PurePosixPath(FAMILY_DOC)
            if (repo_root / doc).is_file():
                docs.add(doc)
            else:
                missing.append((path, str(doc)))
    if missing:
        return MappingMiss(missing)
    return docs


def doc_id_of(doc: PurePosixPath) -> str:
    """doc 경로 → per-doc marker doc-id (family.md → 'family', lane → 플러그인 폴더명)."""
    if str(doc) == FAMILY_DOC:
        return "family"
    name = doc.name
    return name[:-3] if name.endswith(".md") else name


def _doc_satisfied(doc: PurePosixPath, changed: Set[PurePosixPath], markers: MarkerSet) -> bool:
    # (a) 대응 doc 자체가 frontmatter 외 본문 변경 OR (b) 유효 no-op marker(global/per-doc)
    return doc in changed or markers.covers(doc_id_of(doc))


def judge(doc_set: Set[PurePosixPath], changed: Set[PurePosixPath], markers: MarkerSet) -> Verdict:
    """per-doc closed-binary 종합 판정 (Change Plan §3.2 step 4).

    changed = criterion (a) 를 충족한 doc 집합(frontmatter 외 본문 diff ≥1 hunk).
    markers = 파싱된 유효 no-op marker 집합. 전 doc 충족 → PASS, 1+ 미충족 → FAIL(missing-update)."""
    for d in doc_set:
        if not _doc_satisfied(d, changed, markers):
            return Verdict.FAIL
    return Verdict.PASS


def unsatisfied_docs(
    doc_set: Set[PurePosixPath], changed: Set[PurePosixPath], markers: MarkerSet
) -> List[PurePosixPath]:
    return sorted((d for d in doc_set if not _doc_satisfied(d, changed, markers)), key=str)


def _normalize_tokens(text: str) -> List[str]:
    """rationale 정규화 → 실질 토큰 목록 (소문자 + 구두점/공백 축약, Korean·영숫자만 잔존)."""
    return [t for t in _NORM_TOKEN_SPLIT_RE.split(text.lower()) if t]


def _rationale_reject_reason(rationale: str) -> Optional[str]:
    """rationale 거절 사유 (없으면 None). 축 2개 독립 (길이 floor 선행 dead-branch 회피 — QADev M7):

    ① stoplist(정규화 token-anchored, 길이 무관): stop-phrase 와 동치(residual 0) 또는 stop-phrase 로
       anchored 시작 + 잔여 실질 토큰 < RESIDUAL_MIN_SUBSTANTIVE → invalid. 순수 무제한 substring 매칭
       아님(token-anchored prefix) — 실질 근거 문장이 어구 포함만으로 오차단되지 않음.
    ② 길이 floor(정규화·stoplist 무관): len(strip) < RATIONALE_MIN → invalid.
    두 축 모두 통과해야 valid — padding 으로 floor 통과한 stop-phrase 도 ①이 잡음."""
    stripped = rationale.strip()
    norm = _normalize_tokens(stripped)
    for stop in STOPLIST_NORM_TOKENS:
        n = len(stop)
        if tuple(norm[:n]) == stop:
            residual = len(norm) - n
            if residual < RESIDUAL_MIN_SUBSTANTIVE:
                return (
                    "stoplist 단순부정(정규화 anchored '%s', 잔여 실질 토큰 %d<%d): '%s'"
                    % (" ".join(stop), residual, RESIDUAL_MIN_SUBSTANTIVE, stripped[:48])
                )
    if len(stripped) < RATIONALE_MIN:
        return "rationale 길이 미달(%d<%d): '%s'" % (len(stripped), RATIONALE_MIN, stripped[:48])
    return None


def parse_markers(pr_body: str) -> Tuple[MarkerSet, List[str]]:
    """PR body → (유효 MarkerSet, invalid-declare 사유 목록). 구조 미완성/길이 floor/정규화 stoplist(anchored) 검출."""
    marker_set = MarkerSet()
    invalid: List[str] = []
    matches = list(MARKER_RE.finditer(pr_body or ""))
    for m in matches:
        doc_id = m.group(1) or GLOBAL_DOC_ID
        rationale = (m.group(2) or "").strip()
        reason = _rationale_reject_reason(rationale)
        if reason:
            invalid.append(reason)
        elif doc_id == GLOBAL_DOC_ID:
            marker_set.global_present = True
        else:
            marker_set.doc_ids.add(doc_id)
    # 구조 미완성 attempt (prefix 는 있으나 완성형 regex 미형성 — 괄호/콜론/닫는 대괄호 누락)
    prefix_count = (pr_body or "").count(MARKER_PREFIX_LITERAL)
    if prefix_count > len(matches):
        invalid.append(
            "marker 구조 미완성(prefix %d > 완성형 %d) — 괄호/콜론/닫는 대괄호 확인"
            % (prefix_count, len(matches))
        )
    return marker_set, invalid


# ---------------------------------------------------------------------------
# Impure helpers (git / filesystem)
# ---------------------------------------------------------------------------
def _run_git(repo_root: Path, args: List[str]) -> Tuple[int, str, str]:
    proc = subprocess.run(
        ["git", "-C", str(repo_root)] + args,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return proc.returncode, proc.stdout, proc.stderr


def _git_available() -> bool:
    try:
        subprocess.run(["git", "--version"], capture_output=True, check=False)
        return True
    except (OSError, FileNotFoundError):
        return False


def _is_git_repo(repo_root: Path) -> bool:
    rc, out, _ = _run_git(repo_root, ["rev-parse", "--is-inside-work-tree"])
    return rc == 0 and out.strip() == "true"


def _base_spec(repo_root: Path) -> Tuple[str, bool]:
    """(base_sha, is_ci) — CI(GITHUB_BASE_REF)면 merge-base(origin/<base>, HEAD), 로컬이면 HEAD."""
    base_ref = os.environ.get("GITHUB_BASE_REF", "").strip()
    if base_ref:
        rc, out, _ = _run_git(repo_root, ["merge-base", "origin/%s" % base_ref, "HEAD"])
        if rc == 0 and out.strip():
            return out.strip(), True
        return "origin/%s" % base_ref, True
    return "HEAD", False


def _collect_changed(repo_root: Path, base_sha: str, is_ci: bool, from_stdin: bool) -> List[str]:
    mock = os.environ.get("LIVING_ARCH_CHANGED_MOCK")
    if mock is not None:
        return [ln.strip() for ln in mock.splitlines() if ln.strip()]
    if from_stdin:
        return [ln.strip() for ln in sys.stdin.read().splitlines() if ln.strip()]
    # 자체 수집 fallback (직접 호출·테스트용 — .sh 는 collect_changed_files.sh 로 stdin 주입)
    if is_ci:
        rc, out, _ = _run_git(repo_root, ["diff", "--name-only", base_sha, "HEAD"])
        lines = out.splitlines()
    else:
        _, out1, _ = _run_git(repo_root, ["diff", "--name-only", "HEAD"])
        _, out2, _ = _run_git(repo_root, ["diff", "--cached", "--name-only"])
        lines = out1.splitlines() + out2.splitlines()
    return sorted({ln.strip() for ln in lines if ln.strip()})


def _read_pr_body(args: argparse.Namespace) -> str:
    body_file = args.pr_body_file or os.environ.get("LIVING_ARCH_PR_BODY_FILE")
    if body_file:
        try:
            return Path(body_file).read_text(encoding="utf-8", errors="replace")
        except OSError:
            return ""
    return os.environ.get("PR_BODY", "")


def _frontmatter_end_line(text: str) -> int:
    """선두 frontmatter block(--- ~ ---)의 닫는 --- 의 1-based 줄번호. frontmatter 부재 = 0."""
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return 0
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return i + 1
    return 0


def _git_show(repo_root: Path, ref: str, doc: PurePosixPath) -> str:
    rc, out, _ = _run_git(repo_root, ["show", "%s:%s" % (ref, str(doc))])
    return out if rc == 0 else ""


def _has_body_hunk(diff_text: str, old_fm_end: int, new_fm_end: int) -> bool:
    """unified diff 의 +/- 줄 중 하나라도 frontmatter block 밖이면 True (frontmatter-only = False)."""
    old_ln = new_ln = 0
    for line in diff_text.split("\n"):
        if line.startswith("@@"):
            m = HUNK_RE.match(line)
            if m:
                old_ln = int(m.group(1))
                new_ln = int(m.group(2))
            continue
        if line.startswith("+++") or line.startswith("---"):
            continue
        if line.startswith("+"):
            if new_ln > new_fm_end:
                return True
            new_ln += 1
        elif line.startswith("-"):
            if old_ln > old_fm_end:
                return True
            old_ln += 1
        elif line.startswith("\\"):  # "\ No newline at end of file"
            continue
        else:
            old_ln += 1
            new_ln += 1
    return False


def _doc_touched_with_body_change(
    repo_root: Path, doc: PurePosixPath, base_sha: str, is_ci: bool
) -> bool:
    """대응 doc 가 변경 파일 ∧ frontmatter 외 본문 diff ≥1 hunk (criterion (a), anti-gaming §3.4).

    git 오류 시 fail-closed 로 False(미변경 취급) 반환 — silent PASS 금지."""
    if is_ci:
        rc, diff_text, _ = _run_git(repo_root, ["diff", base_sha, "HEAD", "--", str(doc)])
    else:
        rc, diff_text, _ = _run_git(repo_root, ["diff", "HEAD", "--", str(doc)])
        if rc == 0 and not diff_text.strip():
            _, staged, _ = _run_git(repo_root, ["diff", "--cached", "--", str(doc)])
            diff_text = staged
    if rc != 0 or not diff_text.strip():
        return False
    old_text = _git_show(repo_root, base_sha, doc)
    try:
        new_text = (repo_root / doc).read_text(encoding="utf-8", errors="replace")
    except OSError:
        new_text = ""
    old_fm_end = _frontmatter_end_line(old_text)
    new_fm_end = _frontmatter_end_line(new_text)
    return _has_body_hunk(diff_text, old_fm_end, new_fm_end)


def _detect_mode(repo_root: Path) -> Tuple[Mode, List[PurePosixPath]]:
    family = repo_root / FAMILY_DOC
    lane_docs = sorted(repo_root.glob("plugins/*/docs/architecture/*.md"))
    top_docs = sorted(repo_root.glob("docs/architecture/*.md"))
    if family.is_file() and lane_docs:
        return Mode.WRAPPER, []
    held = [PurePosixPath(p.relative_to(repo_root).as_posix()) for p in (top_docs + lane_docs)]
    if held:
        return Mode.CONSUMER, held
    return Mode.NO_OP, []


def _consumer_structural_paths(repo_root: Path) -> List[str]:
    """consumer 구조 표면 = src/** default + overlay project.yaml living_arch.structural_paths[] (확장-only)."""
    paths = list(CONSUMER_DEFAULT_STRUCTURAL)
    cfg = repo_root / ".claude" / "_overlay" / "project.yaml"
    if not cfg.is_file():
        return paths
    try:
        import yaml  # 지연 import — overlay 확장 필요 시에만 (stdlib-only 원칙, 부재 시 default 유지)

        data = yaml.safe_load(cfg.read_text(encoding="utf-8", errors="replace")) or {}
        extra = (((data.get("living_arch") or {}).get("structural_paths")) or [])
        for item in extra:
            s = str(item).strip().replace("\\", "/").lstrip("/")
            if s and not s.endswith("/"):
                s = s + "/"
            if s and s not in paths:
                paths.append(s)
    except Exception:
        # 확장-only — overlay parse 실패 시 default(src/**) 유지 (게이트 비차단 degrade, 정직 notice)
        print(
            "::notice::consumer overlay project.yaml 파싱 실패 — living_arch.structural_paths 확장 "
            "미적용, default src/** 만 사용."
        )
    return paths


def _matches_any_prefix(path: str, prefixes: List[str]) -> bool:
    p = _norm(path)
    for pre in prefixes:
        if p == pre.rstrip("/") or p.startswith(pre):
            return True
    return False


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------
def _summary(line: str) -> None:
    path = os.environ.get("GITHUB_STEP_SUMMARY")
    if not path:
        return
    try:
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(line + "\n")
    except OSError:
        pass


def _emit_trace(n_changed: int, n_structural: int, n_docs: int, note: str = "") -> None:
    line = (
        "[%s] scanned-N: changed=%d structural_surface=%d derived_docs=%d"
        % (SCRIPT_NAME, n_changed, n_structural, n_docs)
    )
    if note:
        line += " (%s)" % note
    print(line)
    _summary(line)


def _fail(category: FailureCategory, message: str, detail_lines: List[str]) -> None:
    print("::error::[%s] %s: %s" % (SCRIPT_NAME, category.value, message))
    _summary("### FAIL — %s" % category.value)
    _summary(message)
    for ln in detail_lines:
        print("  - " + ln)
        _summary("- %s" % ln)


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------
def _run_wrapper(
    repo_root: Path,
    changed_files: List[str],
    marker_set: MarkerSet,
    invalid_reasons: List[str],
    base_sha: str,
    is_ci: bool,
) -> int:
    classes = [(f, classify(f)) for f in changed_files]
    unknown = [f for f, c in classes if c == SurfaceClass.UNKNOWN]
    structural = [
        f for f, c in classes
        if c in (SurfaceClass.STRUCTURAL_PLUGIN, SurfaceClass.STRUCTURAL_FAMILY)
    ]
    n_changed, n_structural = len(changed_files), len(structural)

    if unknown:
        _emit_trace(n_changed, n_structural, 0, note="unknown-surface")
        _fail(
            FailureCategory.UNKNOWN_SURFACE,
            "미분류 신규 표면 — enum row 갱신(분류 확정) 또는 긴급 시 bypass 라벨+audit 로 해소 "
            "(no-op declare 로 우회 불가 — 매핑 대상 doc 부재)",
            list(unknown),
        )
        return 1

    if not structural:
        _emit_trace(n_changed, 0, 0)
        print(
            "::notice::[%s] 구조 표면 변경 0건 — 명시 Success (Living Architecture 갱신 불요)."
            % SCRIPT_NAME
        )
        return 0

    result = derive_docs(structural, repo_root)
    if isinstance(result, MappingMiss):
        _emit_trace(n_changed, n_structural, 0, note="mapping-miss")
        _fail(
            FailureCategory.MAPPING_MISS,
            "구조 표면의 대응 arch doc 도출 불가 — 신규 대상은 templates/architecture-doc.md seed 로 해소",
            ["%s → 기대 doc 부재: %s" % (s, d) for s, d in result.surfaces],
        )
        return 1

    doc_set = result
    _emit_trace(n_changed, n_structural, len(doc_set))

    if invalid_reasons:
        _fail(FailureCategory.INVALID_DECLARE, "no-op marker 형식 위반", invalid_reasons)
        return 1

    changed_docs = {
        d for d in doc_set if _doc_touched_with_body_change(repo_root, d, base_sha, is_ci)
    }
    if judge(doc_set, changed_docs, marker_set) == Verdict.FAIL:
        miss = unsatisfied_docs(doc_set, changed_docs, marker_set)
        _fail(
            FailureCategory.MISSING_UPDATE,
            "대응 Living Architecture doc 미갱신 — 본문 갱신 또는 no-op marker 필요",
            [
                "%s — 본문 hunk 갱신 또는 `[living-arch-no-impact(%s): <15자+ 근거>]` declare"
                % (str(d), doc_id_of(d))
                for d in miss
            ],
        )
        return 1

    print("::notice::[%s] PASS — 전 대응 doc 갱신/선언 충족." % SCRIPT_NAME)
    _summary("PASS — 전 대응 Living Architecture doc 갱신/선언 충족.")
    return 0


def _run_consumer(
    repo_root: Path,
    changed_files: List[str],
    held_docs: List[PurePosixPath],
    marker_set: MarkerSet,
    invalid_reasons: List[str],
    base_sha: str,
    is_ci: bool,
) -> int:
    structural_paths = _consumer_structural_paths(repo_root)
    structural = [f for f in changed_files if _matches_any_prefix(f, structural_paths)]
    n_changed, n_structural = len(changed_files), len(structural)

    if not structural:
        _emit_trace(n_changed, 0, len(held_docs))
        print(
            "::notice::[%s] 구조 표면(%s) 변경 0건 — 명시 Success."
            % (SCRIPT_NAME, "/".join(structural_paths))
        )
        return 0

    doc_set = set(held_docs)
    _emit_trace(n_changed, n_structural, len(doc_set))

    if invalid_reasons:
        _fail(FailureCategory.INVALID_DECLARE, "no-op marker 형식 위반", invalid_reasons)
        return 1

    changed_docs = {
        d for d in doc_set if _doc_touched_with_body_change(repo_root, d, base_sha, is_ci)
    }
    if judge(doc_set, changed_docs, marker_set) == Verdict.FAIL:
        miss = unsatisfied_docs(doc_set, changed_docs, marker_set)
        _fail(
            FailureCategory.MISSING_UPDATE,
            "보유 arch doc 미갱신 (consumer fallback 모드) — 본문 갱신 또는 no-op marker 필요",
            [
                "%s — 본문 hunk 갱신 또는 `[living-arch-no-impact(%s): <15자+ 근거>]` declare"
                % (str(d), doc_id_of(d))
                for d in miss
            ],
        )
        return 1

    print("::notice::[%s] PASS (consumer 모드) — 보유 doc 갱신/선언 충족." % SCRIPT_NAME)
    return 0


def _parse_args(argv: List[str]) -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        prog=SCRIPT_NAME,
        description="Living Architecture per-PR 최신성 게이트 (변경-문서 coupling closed-binary).",
    )
    ap.add_argument("--repo-root", default=None, help="repo 루트 (default: CWD)")
    ap.add_argument(
        "--changed-from-stdin",
        action="store_true",
        help="변경 파일 목록을 stdin(newline)에서 읽음 (.sh 가 collect_changed_files.sh 로 주입)",
    )
    ap.add_argument("--pr-body-file", default=None, help="PR body 파일 경로 (marker 파싱 입력)")
    return ap.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = _parse_args(list(sys.argv[1:] if argv is None else argv))
    repo_root = Path(args.repo_root or ".").resolve()

    if not _git_available():
        print("::error::[%s] meta-error: git 미설치 (환경 오류, fail-closed)." % SCRIPT_NAME)
        return 2

    mode, held_docs = _detect_mode(repo_root)
    if mode == Mode.NO_OP:
        _emit_trace(0, 0, 0, note="no-op")
        print(
            "::notice::[%s] architecture_doc capability 미보유 — honest no-op (명시 Success)."
            % SCRIPT_NAME
        )
        return 0

    if not _is_git_repo(repo_root):
        print(
            "::error::[%s] meta-error: git repository 아님 (%s) — fail-closed."
            % (SCRIPT_NAME, str(repo_root))
        )
        return 2

    base_sha, is_ci = _base_spec(repo_root)
    changed_files = _collect_changed(repo_root, base_sha, is_ci, args.changed_from_stdin)
    marker_set, invalid_reasons = parse_markers(_read_pr_body(args))

    if mode == Mode.WRAPPER:
        return _run_wrapper(repo_root, changed_files, marker_set, invalid_reasons, base_sha, is_ci)
    return _run_consumer(
        repo_root, changed_files, held_docs, marker_set, invalid_reasons, base_sha, is_ci
    )


if __name__ == "__main__":
    sys.exit(main())
