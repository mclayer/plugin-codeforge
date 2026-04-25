#!/usr/bin/env bash
# 검사: docs/* 안의 마크다운 상대 링크가 깨지지 않았는가
# fenced code block(``` ... ```) 안의 placeholder·예시는 무시
set -euo pipefail

cd "$(dirname "$0")/.."

FAIL=0

while IFS= read -r f; do
  in_fence=0
  lineno=0
  while IFS= read -r line; do
    lineno=$((lineno + 1))
    # fenced code block 토글
    if [[ "$line" =~ ^[[:space:]]*\`\`\` ]]; then
      in_fence=$((1 - in_fence))
      continue
    fi
    [[ $in_fence -eq 1 ]] && continue
    # 인라인 코드 (`...`) 안의 링크는 검증 대상이 아니지만 line 단위 처리이므로 그대로 둠 (false positive 거의 없음)
    rest="$line"
    while [[ "$rest" =~ \]\(([^\)]+)\) ]]; do
      target="${BASH_REMATCH[1]}"
      rest="${rest#*\]\(${target}\)}"
      # 외부 URL skip
      [[ "$target" =~ ^https?:// ]] && continue
      [[ "$target" =~ ^mailto: ]] && continue
      # anchor 분리
      target_path="${target%%#*}"
      [[ -z "$target_path" ]] && continue
      # placeholder (<...>, $...) skip — 명백한 템플릿 자리
      [[ "$target_path" =~ \< ]] && continue
      [[ "$target_path" =~ \$ ]] && continue
      # 절대 경로화
      dir="$(dirname "$f")"
      abs_path="$dir/$target_path"
      if [[ ! -e "$abs_path" ]]; then
        echo "✗ $f:$lineno: 깨진 링크 → $target"
        FAIL=1
      fi
    done
  done < "$f"
done < <(find docs/ agents/ -name '*.md' -type f 2>/dev/null; ls CLAUDE.md README.md 2>/dev/null || true)

if [[ $FAIL -eq 0 ]]; then echo "✓ 마크다운 링크 무결"; fi
exit $FAIL
