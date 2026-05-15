"""
path_normalize.py — CFP-743 Phase 2 공유 path 정규화 헬퍼 (ADR-061 §결정 1 정합)

Change Plan §4.5 canonical 규칙 구현:
  - 6 입력 형태 수용 (MSYS2 / Windows backslash / Windows forward-slash / 상대 / 공백 / non-ASCII UTF-8)
  - canonical output: repo_root 기준 절대 경로 + forward-slash 단일 구분자 + UTF-8
  - 정규화 불가 = abort_before_touch (SystemExit 2 + stderr 메시지)
  - CFP-702 _to_canonical() precedent 동형 (신규 발명 금지)
  - sh ↔ ps1 parity: 양 script 가 본 .py 를 통해 동일 canonical output 보장

사용법:
  python path_normalize.py <path> [--repo-root <repo_root>]
  성공: 0, stdout = canonical path
  실패: 2, stderr = 오류 메시지 + path_normalization_failure tag
"""

import sys
import os
import re


def to_canonical(raw_path: str, repo_root: str | None = None) -> str:
    """
    raw_path 를 canonical 절대 경로로 변환 (forward-slash, UTF-8).

    지원 입력 형태:
    1. MSYS2/Git-Bash POSIX  : /c/Users/...
    2. Windows backslash     : C:\\Users\\...
    3. Windows forward-slash : C:/Users/...
    4. 상대 경로             : ./ ../ (repo_root 기준 절대화)
    5. 공백 포함 경로         : raw 보존 (shell 전달 시점만 quote)
    6. non-ASCII UTF-8       : byte-level 보존 (locale-dependent 변환 금지)

    실패 시: raise ValueError (caller 가 abort_before_touch 로 처리)
    """
    if not isinstance(raw_path, str):
        raise ValueError(f"path_normalization_failure: 입력이 문자열이 아님: {type(raw_path)}")

    path = raw_path.strip()

    if not path:
        raise ValueError("path_normalization_failure: 빈 경로 입력")

    # 형태 1: MSYS2/Git-Bash POSIX 경로 (/c/Users/... → C:/Users/...)
    msys2_match = re.match(r'^/([a-zA-Z])(/.*)$', path)
    if msys2_match:
        drive_letter = msys2_match.group(1).upper()
        rest = msys2_match.group(2)
        path = f"{drive_letter}:{rest}"

    # 형태 2: Windows backslash → forward-slash 변환
    # (drive C:\... 또는 UNC \\server\... 처리)
    if re.match(r'^[a-zA-Z]:\\', path) or re.match(r'^\\\\', path):
        path = path.replace('\\', '/')

    # 형태 3: Windows forward-slash (C:/...) — 이미 forward-slash, 그대로

    # 형태 4: 상대 경로 → repo_root 기준 절대화
    if not os.path.isabs(path.replace('/', os.sep)):
        if repo_root is None:
            # repo_root 미제공 시 현재 작업 디렉터리 기준
            repo_root = os.getcwd()
        abs_path = os.path.normpath(os.path.join(repo_root, path))
        path = abs_path.replace('\\', '/')
    else:
        # 절대 경로의 경우에도 normpath 후 forward-slash 통일
        # os.sep 기반 normpath (Windows: backslash, Unix: forward-slash)
        norm = os.path.normpath(path.replace('/', os.sep))
        path = norm.replace('\\', '/')

    # drive letter 보존 확인 (Windows 환경)
    if re.match(r'^[a-zA-Z]:', path):
        # drive letter 유지 (C: → 대문자)
        path = path[0].upper() + path[1:]

    # 인코딩 검증: non-ASCII UTF-8 segment byte-level 보존 (locale-dependent 변환 금지)
    try:
        path.encode('utf-8').decode('utf-8')
    except (UnicodeEncodeError, UnicodeDecodeError) as exc:
        raise ValueError(
            f"path_normalization_failure: UTF-8 인코딩 검증 실패: {exc}"
        ) from exc

    # 이중 슬래시 제거 (정책 단순화)
    while '//' in path:
        path = path.replace('//', '/')

    return path


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description='CFP-743 path 정규화 헬퍼 (Change Plan §4.5)',
        add_help=True,
    )
    parser.add_argument('path', help='정규화할 경로')
    parser.add_argument(
        '--repo-root',
        default=None,
        help='상대 경로 해소 기준 repo root (미제공 시 CWD)',
    )

    args = parser.parse_args()

    try:
        canonical = to_canonical(args.path, repo_root=args.repo_root)
        print(canonical)
        sys.exit(0)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(2)


if __name__ == '__main__':
    main()
