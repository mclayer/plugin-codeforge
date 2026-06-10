"""
workflow_story_init_compute_key.py
CFP-478 Phase 2 sub-PR b — ADR-061 Amendment 1 §결정 1.B
Block #17: story-init.yml lines 131-158 (key/slug/title_clean computation)

CFP-671 / ADR-036 Amendment 1: title regex precedence + Issue# fallback.
Title `[<PREFIX>-<N>]` bracket-mandatory pattern matched + prefix matched → title KEY 우선.
Title pattern absent OR prefix MISMATCH → Issue # fallback (race-free guarantee 보존).

CFP-2116 / ADR-036 Amendment 2: 대괄호 필수 정밀화.
bare reference (`CFP-NNNN` without brackets) 는 KEY 로 인정하지 않음.
reservation(`[CFP-NNNN]`) vs reference(`CFP-NNNN` bare) 단일 판별 신호 = 대괄호 형태.

Usage (via workflow YAML run: block):
  PYOUT=$(python3 "${GITHUB_WORKSPACE}/scripts/lib/workflow_story_init_compute_key.py")
  KEY=$(printf '%s' "$PYOUT" | sed -n '1p')
  SLUG=$(printf '%s' "$PYOUT" | sed -n '2p')
  TITLE_CLEAN=$(printf '%s' "$PYOUT" | sed -n '3p')
  echo "key=$KEY" >> "$GITHUB_OUTPUT"
  echo "slug=$SLUG" >> "$GITHUB_OUTPUT"
  {
    echo "title_clean<<TITLE_EOF"
    printf '%s\n' "$TITLE_CLEAN"
    echo "TITLE_EOF"
  } >> "$GITHUB_OUTPUT"

env: block must provide:
  ISSUE_TITLE: ${{ github.event.issue.title }}
  PREFIX: ${{ steps.project_config.outputs.story_key_prefix }}
  ISSUE_NUMBER: ${{ github.event.issue.number }}
"""
import argparse
import os
import re
import sys

# Windows cp949 stdout encoding 차단 (CFP-1393 F8-FU / ADR-061 standardize)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


def compute_key(title: str, prefix: str, issue_number: str) -> str:
    """Story KEY 계산 순수 함수 (CFP-2116 / ADR-036 Amendment 2).

    title        : Issue title (ISSUE_TITLE env — [STORY] prefix 포함 가능)
    prefix       : Story key prefix (예: "CFP")
    issue_number : GitHub Issue number 문자열

    반환: "<prefix>-<KEY>" 형식의 KEY 문자열.

    판별 규칙:
      - [STORY] prefix 제거 후 title_clean 추출
      - reservation 판별: `[PREFIX-N]` 대괄호 **필수** 패턴만 인정
        (ADR-036 Amd 2: bare `PREFIX-N` 는 reference → fallback)
      - prefix guard: startswith(prefix+"-") — cross-project KEY injection 차단
        (ADR-036 Amd 1 §결정 2 security guard — 살아있는 코드 경로 유지)
      - 매치 부재 또는 prefix MISMATCH → f"{prefix}-{issue_number}" fallback
        (ADR-036 §결정 1 race-free guarantee 보존)
    """
    # [STORY] prefix 제거 후 title clean
    title_clean = re.sub(r"^\[STORY\]\s*", "", title).strip()

    # Title pattern `[<PREFIX>-<N>]` 대괄호 **필수** 추출 (CFP-2116 / ADR-036 Amd 2)
    # 변경: \[?([A-Z]+-\d+)\]? (optional) → \[([A-Z]+-\d+)\] (mandatory)
    # 근거: bare reference(CFP-2104 후속)와 reservation([CFP-662]) 구분 — 대괄호 단일 판별 신호
    m = re.search(r'\[([A-Z]+-\d+)\]', title_clean)
    key_from_title = m.group(1) if m else ""

    # Prefix guard — cross-project KEY injection 차단 (ADR-036 Amd 1 §결정 2, 불변)
    if key_from_title and key_from_title.startswith(prefix + "-"):
        key = key_from_title
    else:
        # Fallback to Issue # — ADR-036 결정 1 race-free guarantee 보존 (불변)
        key = f"{prefix}-{issue_number}"

    return key


def run_self_test() -> int:
    """D2 — inline fixture self-test (CFP-2116 Story §7.5).
    Returns 0 if all fixtures pass, non-zero otherwise.
    bats revival forbidden (de-bloat / CFP-2104 pattern). Logic SSOT in .py (ADR-061).
    """
    failures = []

    def check(label: str, title: str, prefix: str, issue_number: str, expected_key: str) -> None:
        result = compute_key(title, prefix, issue_number)
        status = "PASS" if result == expected_key else "FAIL"
        if status == "FAIL":
            failures.append((label, title, prefix, issue_number, expected_key, result))
        print(f"[self-test] {status} {label} -- expected={expected_key!r} actual={result!r}")

    # F1 (AC-1): bare reference → fallback (CFP-2116 P2-1 — 버그 수정 핵심)
    # 수정 전: 오추출 CFP-2104 / 수정 후: fallback CFP-2111
    check(
        "F1 (bare-reference->fallback)",
        "[STORY] CFP-2104 후속 — self-test CI 가시성 ...",
        "CFP",
        "2111",
        "CFP-2111",
    )

    # F2 (AC-2): bracket reservation → 우선 (ADR-036 Amd 1 §결정 1 무회귀)
    check(
        "F2 (bracket-reservation->key-precedence)",
        "[STORY] [CFP-662] bootstrap-labels workflow 신설 ...",
        "CFP",
        "670",
        "CFP-662",
    )

    # F3 (AC-3): KEY 토큰 부재 → fallback
    check(
        "F3 (no-token->fallback)",
        "[STORY] story-init KEY 계산 버그 — ...",
        "CFP",
        "2116",
        "CFP-2116",
    )

    # F4 (AC-4): 대괄호이나 prefix MISMATCH → fallback (security guard 무회귀)
    check(
        "F4 (prefix-mismatch->fallback)",
        "[STORY] [ABC-123] something",
        "CFP",
        "555",
        "CFP-555",
    )

    # F5 (E1): bare reference 선두 출현 → fallback (위치 무관, 대괄호 단일 판별)
    check(
        "F5 (bare-leading->fallback)",
        "[STORY] CFP-2104 후속",
        "CFP",
        "9000",
        "CFP-9000",
    )

    # F6 (E2): 대괄호 + bare 공존 → 대괄호 우선, bare 무시
    check(
        "F6 (bracket+bare->bracket-wins)",
        "[STORY] [CFP-662] CFP-600 후속 ...",
        "CFP",
        "670",
        "CFP-662",
    )

    # F7 (E4): 다중 대괄호 → first-match 결정성
    check(
        "F7 (multi-bracket->first-match)",
        "[STORY] [CFP-1] [CFP-2]",
        "CFP",
        "300",
        "CFP-1",
    )

    # F8 (P2-2): bare-before-bracket — bare 선두 뒤에 bracket 있어도 bracket reservation 우선
    # 제목: "[STORY] CFP-2104 후속 [CFP-662] 정리", PREFIX=CFP, Issue#=9999 → CFP-662
    # 근거: bare는 미매칭(대괄호 필수) → bracket이 first-match → CFP-662
    check(
        "F8 (bare-before-bracket->bracket-wins)",
        "[STORY] CFP-2104 후속 [CFP-662] 정리",
        "CFP",
        "9999",
        "CFP-662",
    )

    total = 8
    passed = total - len(failures)
    if failures:
        print(f"[self-test] FAILED {len(failures)}/{total}")
        for label, title, prefix, issue_number, exp, act in failures:
            print(
                f"  FAIL {label} | expected={exp!r} actual={act!r}"
                f" | title={title!r} prefix={prefix!r} issue_number={issue_number!r}"
            )
        return 1
    print(f"[self-test] ALL GREEN ({passed}/{total})")
    return 0


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(
        description="Story KEY 계산 (ADR-036 Amd 2 — bracket-mandatory)"
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run inline fixture self-test (D2, CFP-2116 §7.5)",
    )
    args = parser.parse_args(argv)

    # D2: --self-test mode (CFP-2116 §7.5 — inline fixture, ADR-061 .py SSOT)
    if args.self_test:
        sys.exit(run_self_test())

    # 기존 env-driven 동작 (3-line stdout 계약 무변경 — workflow sed 파싱 무손상)
    title = os.environ.get("ISSUE_TITLE", "")
    prefix = os.environ.get("PREFIX", "")
    issue_number = os.environ.get("ISSUE_NUMBER", "")

    key = compute_key(title, prefix, issue_number)

    # slug computation (CFP-596 base 동일)
    title_clean = re.sub(r"^\[STORY\]\s*", "", title).strip()
    slug = re.sub(r"[^A-Za-z0-9가-힣]+", "-", title_clean, flags=re.UNICODE)
    slug = slug.strip("-")[:40].rstrip("-")

    print(key)
    print(slug)
    print(title_clean)


if __name__ == "__main__":
    main()
