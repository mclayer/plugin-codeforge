#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
scripts/lib/check_venue_shape_fidelity_presence.py
CFP-2504 Phase 2 / ADR-006 Amendment 1 §A1-2/A1-8 — 외부 venue/시계열 데이터 형상 재현
fidelity 의무의 **기계적 anchor-presence lint** Python SSOT engine (warning tier, exit 3-tier).

ADR-006 Amendment 1 은 Phase 1 에서 선언적 의무(TestContractArch §8 author input mandate +
설계리뷰/code-review 체크리스트 항목)만 정착하고 기계적 lint 는 deferred-followup 로 미뤘다.
본 엔진이 그 Phase 2 mechanical wire — review-독립 CI lint 로 §8 Test Contract 에 형상 재현
선언(또는 명시적 N/A) 이 **존재**하는지를 검사한다.

검사 범위 (CONDITIONAL — A1-7 consumer-applicability):
  project.yaml `venue.applicable: true` 인 consumer 한정 발동. flag false/미주입(wrapper self
  포함) = no-op PASS (안전 방향 default false — frontend.applicable ADR-136 동형). venue-touching
  consumer(mctrader 류) 만 실 검사 대상.

검사 대상 (anchor-presence, NOT synthetic-detection):
  docs/stories/*.md 의 §8 Test Contract 섹션 본문에 다음 중 하나의 anchor 가 존재하는가:
    (A) shape-declaration anchor — 형상 재현 선언 (Phase 1 확정 어휘):
        captured-golden / 실형상 / 실 venue tap / wiretap / 실 capture / "형상 재현" 등.
    (B) N/A anchor — venue 미접촉 N/A 사유 (ADR-005 N/A 패턴, A1-3):
        "N/A" + venue 미접촉/외부 venue 미의존 사유 1줄.
  (A) 도 (B) 도 부재 = 위반 (warning). "합성인지 자동판정"(본질적 fuzzy)은 scope 외 — 본 lint 는
  선언·N/A anchor 의 **존재** 만 판정 (A1-8: anchor presence 검출).

설계 균형 (false-pos/neg 최소화):
  - §8 섹션 부재 = data-absence honest no-op (구조 schema 는 story-section-schema.yml 담당,
    본 lint 는 §8 본문 anchor 만 — 중복 차단). story-section-schema 가 §8 누락을 별도로 잡는다.
  - frontmatter `type: epic` story = §8 N/A 명시 의무가 story-section-schema 관할 →
    본 anchor 검사는 §8 본문 존재 시에만 트리거 (epic 의 N/A 헤딩도 anchor 로 인정).
  - anchor 어휘는 Phase 1 산출물(TestContractArchitectAgent.md / review-checklists/design.md)
    의 확정 키워드와 1:1 정합 — 새 어휘 발명 0 (false-neg = 어휘 drift 회피).

graceful-degradation (2-tier 엄격 분리 — change-plan §7.4 / §7.5):
  data-absence(A) = fail-open(exit 0, honest ::notice::):
    docs/stories/ 부재(plugin/pre-init) / venue.applicable false·미주입 / §8 본문 부재 =
    검사 비대상 = 정책 공백 동형 fail-open (false-PASS 아닌 honest no-op).
  setup-error(B) = fail-closed(exit 2):
    project.yaml 존재하나 YAML parse 실패 = 검증 입력 신뢰 불가.

offline-first (네트워크 불요 — 입력 전부 로컬 파일). ReDoS-safe (anchored simple regex + 고정
substring 매칭, catastrophic backtracking 0). read-only (verifier — write 0).

Usage:
  python3 check_venue_shape_fidelity_presence.py [--config <project.yaml>] [--stories-dir <dir>]
    --config 미지정: .claude/_overlay/project.yaml (CWD-상대) → 부재 시 data-absence fail-open.
    --stories-dir 미지정: docs/stories (CWD-상대).

Exit codes (ADR-060 §결정 5 3-tier — warning tier):
  0 = PASS (전 story 형상 anchor/N/A 존재) OR data-absence honest no-op (fail-open)
  1 = anchor 부재 story 1+ 검출 (workflow continue-on-error 로 비차단, advisory warning)
  2 = SETUP error (project.yaml YAML parse 실패) — fail-closed

ADR refs: ADR-006 Amendment 1 §A1-2/A1-3/A1-7/A1-8 (형상 재현 fidelity 의무 + Phase 2 lint wire) /
  ADR-060 §결정 5/6/19 (warning-tier evidence framework + 승격 evidence-gate) /
  ADR-005 (N/A 패턴 — plugin-meta-na / runtime-inert) /
  ADR-061 §결정 1 (Python SSOT + thin wrapper) / ADR-136 (frontend.applicable default-false 2-layer 동형) /
  ADR-119 (검사연극 금지 — anchor-presence 한정·synthetic-detection scope-out 정직 기술).
"""

import argparse
import os
import re
import sys

# 출력 인코딩 robust 화 (env isolation — Windows MSYS/cp949 등 비-UTF-8 locale 에서 한글·em-dash(—)
# print() UnicodeEncodeError 차단). check_force_push_base_advance.py 답습.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
    except Exception:
        pass

EXIT_PASS = 0       # PASS or data-absence honest no-op (fail-open)
EXIT_VIOLATION = 1  # anchor 부재 검출 (advisory warning, 비차단)
EXIT_SETUP = 2      # SETUP·ENV error (fail-closed)

# ─────────────────────────────────────────────────────────────────────────────
# Anchor 어휘 — Phase 1 산출물(TestContractArchitectAgent.md / review-checklists/design.md)
# 확정 키워드와 1:1 정합. 새 어휘 발명 0 (어휘 drift = false-neg 회피).
#
# (A) shape-declaration anchor — 형상 재현 선언이 존재함을 나타내는 고정 substring.
#   각 토큰은 Phase 1 어휘에서 직접 인용 (captured-golden / 실형상 / venue tap / wiretap /
#   "형상 재현" / "실 capture"). 대소문자 무시 매칭(영문 토큰)으로 표기 변이 흡수.
# ─────────────────────────────────────────────────────────────────────────────
SHAPE_DECLARATION_ANCHORS = [
    "captured-golden",   # (a) 경로 — 실 venue tap/녹화 fixture (A1-2 a)
    "captured golden",   # 공백 표기 변이
    "실형상",             # (b) 경로 — 실형상-justified fixture (A1-2 b)
    "venue tap",         # 실 venue tap/wiretap
    "wiretap",
    "실 capture",        # 실 stream capture
    "형상 재현",          # 의무 본문 핵심 어구 (A1-0/A1-2)
    "형상 재현 fixture",
]

# (B) N/A anchor — venue 미접촉 N/A (A1-3). "N/A" 토큰 + venue 미접촉 사유 어구 동시 존재.
#   ADR-005 N/A 패턴 정합. shape-insensitive(A1-6) N/A 도 동일 어휘로 인정(접촉하나 비민감).
NA_VENUE_TOKENS = [
    "venue 미접촉",      # "외부 venue 미접촉" 도 substring 흡수
    "venue 미의존",      # "외부 venue 미의존" 도 substring 흡수
    "venue 미사용",      # 어절경계 안전 명시 — "미들웨어"·"미디어" 등 비-N/A 표현엔 미매칭
    "venue 미접근",      # 동상 — 의도했던 미접근 부정형 명시
    "venue 무접촉",
    "shape-insensitive",  # A1-6 shape-insensitive N/A (접촉하나 형상 비민감)
    "형상 비민감",
    "형상-무관",
]

# §8 Test Contract 헤딩 — `## §8` / `## 8` / `## §8.` / `## 8.` (story renderer 가 § 생략 헤딩
#   생성 — check_story_section_schema.py 정합). §8 vs §80 충돌 차단 위해 뒤에 [\.\s] anchor.
SECTION_8_HEADER_RE = re.compile(r"^##\s*§?8[\.\s]", re.MULTILINE)
# 다음 §N 헤딩(섹션 경계). `## §9` / `## 9` / `## §10` 등 — §8 본문 끝 경계.
NEXT_H2_RE = re.compile(r"^##\s", re.MULTILINE)

# frontmatter type 필드 (epic vs story 구분 — N/A 헤딩 관할 메모용, 본 lint 는 anchor 만).
TYPE_RE = re.compile(r"^type:\s*(\S+)\s*$", re.MULTILINE)
# venue.applicable: true/false (단순 YAML — 정규식 1차 스캔 후 yaml.safe_load 로 authoritative 판정).


def _notice(msg: str) -> None:
    print(f"::notice::check-venue-shape-fidelity-presence: {msg}")


def _warning(msg: str) -> None:
    print(f"::warning::check-venue-shape-fidelity-presence: {msg}")


def _error(msg: str) -> None:
    print(f"::error::check-venue-shape-fidelity-presence: {msg}", file=sys.stderr)


def _venue_applicable(config_path: str):
    """project.yaml `venue.applicable` 판정.

    반환:
      (True, None)   — venue.applicable: true (검사 active)
      (False, None)  — flag false/미주입/config 부재 (data-absence fail-open, no-op PASS)
      (None, errmsg) — config 존재하나 YAML parse 실패 (setup-error fail-closed)
    """
    if not os.path.isfile(config_path):
        # config 부재 = wrapper self / pre-init consumer = data-absence (no-op PASS).
        return False, None
    try:
        import yaml  # 지연 import — config 존재 시에만 필요
    except Exception:
        # PyYAML 부재 = setup-error (검증 입력 신뢰 불가). CI 는 PyYAML 보장.
        return None, "PyYAML 미설치 (setup-error, fail-closed)"
    try:
        with open(config_path, encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
    except Exception as exc:
        return None, f"project.yaml YAML parse 실패: {exc} (setup-error, fail-closed)"
    if not isinstance(data, dict):
        # 빈 파일/스칼라 = venue 섹션 부재 동형 (no-op PASS).
        return False, None
    venue = data.get("venue")
    if not isinstance(venue, dict):
        return False, None
    return bool(venue.get("applicable", False)), None


def _extract_section_8(text: str):
    """story 본문에서 §8 Test Contract 섹션 본문 추출. 부재 시 None (data-absence)."""
    m = SECTION_8_HEADER_RE.search(text)
    if not m:
        return None
    start = m.end()
    nxt = NEXT_H2_RE.search(text, start)
    end = nxt.start() if nxt else len(text)
    return text[start:end]


def _has_shape_anchor(section_body: str) -> bool:
    lowered = section_body.lower()
    for token in SHAPE_DECLARATION_ANCHORS:
        # 한글 토큰은 lower() 영향 없음, 영문 토큰은 표기 변이 흡수.
        if token.lower() in lowered:
            return True
    return False


def _has_na_anchor(section_body: str) -> bool:
    # "N/A" 토큰 존재 + venue 미접촉 사유 어구 동시 (단순 N/A 만으로는 불충분 — 사유 동반).
    if "n/a" not in section_body.lower():
        return False
    for token in NA_VENUE_TOKENS:
        if token.lower() in section_body.lower():
            return True
    return False


def _iter_story_files(stories_dir: str):
    if not os.path.isdir(stories_dir):
        return
    for name in sorted(os.listdir(stories_dir)):
        if not name.endswith(".md"):
            continue
        if name == ".gitkeep":
            continue
        yield os.path.join(stories_dir, name)


def run(config_path=None, stories_dir=None) -> int:
    config_path = config_path or os.path.join(".claude", "_overlay", "project.yaml")
    stories_dir = stories_dir or os.path.join("docs", "stories")

    applicable, err = _venue_applicable(config_path)
    if err is not None:
        _error(err)
        return EXIT_SETUP
    if not applicable:
        _notice(
            "venue.applicable false/미주입 (또는 project.yaml 부재) — 외부 venue/시계열 형상 lint "
            "비대상 (data-absence fail-open, exit 0). venue-touching consumer 는 project.yaml 에 "
            "venue.applicable: true 선언 시 활성 (ADR-006 Amd1 A1-7 / ADR-136 default-false 동형)."
        )
        return EXIT_PASS

    if not os.path.isdir(stories_dir):
        _notice(
            f"{stories_dir}/ 부재 — story lint 비대상 (data-absence fail-open, exit 0; "
            "plugin repo 또는 pre-init consumer)"
        )
        return EXIT_PASS

    checked = 0
    skipped_no_s8 = 0
    violations = []

    for path in _iter_story_files(stories_dir):
        try:
            with open(path, encoding="utf-8") as fh:
                text = fh.read()
        except Exception as exc:
            _warning(f"{path}: 읽기 실패 ({exc}) — skip")
            continue
        if not text.strip():
            continue
        checked += 1
        rel = path.replace("\\", "/")

        section_8 = _extract_section_8(text)
        if section_8 is None:
            # §8 헤딩 부재 = 구조 결손 → story-section-schema.yml 관할 (중복 차단).
            #   본 anchor lint 는 §8 본문 존재 시에만 anchor 검사 (data-absence honest skip).
            skipped_no_s8 += 1
            continue

        if _has_shape_anchor(section_8) or _has_na_anchor(section_8):
            continue

        violations.append(rel)

    if violations:
        for rel in violations:
            _warning(
                f"{rel}: §8 Test Contract 에 venue 형상 재현 anchor 부재 — "
                "형상 재현 선언(captured-golden / 실형상-justified fixture / 형상 재현) 또는 "
                "명시적 N/A(venue 미접촉 사유) 중 하나 필요 (ADR-006 Amendment 1 §A1-2/A1-3). "
                "합성-only(균일 +1 seq·고정 interval)는 shape-sensitive 코드에 불충분."
            )
        _warning(
            f"venue 형상 재현 anchor 부재 {len(violations)} story (checked={checked}, "
            f"§8-부재-skip={skipped_no_s8}). 본 lint 는 anchor-presence 만 검출 — "
            "'합성인지 자동판정'(본질적 fuzzy)은 scope 외 (ADR-006 A1-8 / ADR-119). "
            "warning-tier 비차단(continue-on-error) — merge 미차단 advisory."
        )
        return EXIT_VIOLATION

    _notice(
        f"venue 형상 재현 anchor presence PASS — checked={checked} story "
        f"(§8-부재-skip={skipped_no_s8}, story-section-schema 관할). 전 대상 형상 anchor/N/A 존재."
    )
    return EXIT_PASS


def main() -> int:
    parser = argparse.ArgumentParser(
        description="venue 형상 재현 fidelity anchor-presence lint (ADR-006 Amd1 Phase 2, warning tier)."
    )
    parser.add_argument(
        "--config",
        default=None,
        help="project.yaml 경로 (default: .claude/_overlay/project.yaml, CWD-상대)",
    )
    parser.add_argument(
        "--stories-dir",
        default=None,
        help="story 디렉터리 (default: docs/stories, CWD-상대)",
    )
    args = parser.parse_args()
    return run(config_path=args.config, stories_dir=args.stories_dir)


if __name__ == "__main__":
    sys.exit(main())
