#!/usr/bin/env python3
"""codeforge Stop hook 로직 — 직전 답변(이번 turn)의 codeforge 내부 jargon 검사. (CFP-1738)

플러그인 배포본. 모든 consumer 자동 적용. hooks/plain-language-check (bash shim) 가 호출.

회피 대상 = codeforge 내부 식별자만 (ADR-번호 / CFP-번호 / §결정 / 계약명 등).
일반 기술 용어(hook / worktree / schema / latency 등)는 검사하지 않음 — 사용자는 엔지니어.

설정 (consumer 환경변수):
  BYPASS_PLAIN_LANGUAGE=1            검사 끄기
  PLAIN_LANG_JARGON_THRESHOLD=N      발동 임계치 (기본 1 = 0 허용)
  PLAIN_LANG_EXTRA_PATTERNS=re1,re2  consumer 고유 패턴 추가 (쉼표 구분 정규식)

동작:
  - stdin 으로 Stop hook JSON 수신 (transcript_path / stop_hook_active).
  - stop_hook_active 면 무한루프 방지로 즉시 통과.
  - transcript JSONL 에서 '이번 turn'(마지막 user 이후) assistant text 만 추출.
  - 패턴 매치 수 >= 임계치 → decision=block + reason 출력.

한계: Stop 훅은 답이 화면에 표시된 *후* 작동 → "비노출" 불가, "노출 즉시 교정".
fail-safe: 어떤 실패(파일 없음/파싱 오류/예외)든 통과(차단하지 않음).
"""
import sys
import os
import re
import json

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

# codeforge 내부 식별자 패턴 — 단순/anchored, 백트래킹 위험 없음 (ADR-061 Amendment 3 정합).
# 일반 영어/기술 용어는 포함하지 않음 (회피 대상 아님).
BASE_PATTERNS = [
    r"ADR-\d+",
    r"CFP-\d+",
    r"§결정",
    r"§D-\d+",
    r"§\d+\.\d+",
    r"review-verdict-v\d",
    r"label-registry-v\d",
    r"reconcile-protocol-v\d",
    r"debate-protocol-v\d",
    r"fix-event-v\d",
    r"Amendment\s+\d+",
]


def build_patterns():
    pats = list(BASE_PATTERNS)
    extra = os.environ.get("PLAIN_LANG_EXTRA_PATTERNS", "").strip()
    if extra:
        for raw in extra.split(","):
            p = raw.strip()
            if not p:
                continue
            try:
                re.compile(p)
                pats.append(p)
            except re.error:
                pass  # consumer 의 잘못된 정규식 무시 (fail-safe)
    return pats


def extract_current_turn_text(transcript_path):
    events = []
    try:
        with open(transcript_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    events.append(json.loads(line))
                except Exception:
                    continue
    except Exception:
        return ""

    # 이번 turn = 마지막 user 이벤트 이후. tool-only turn 은 text 없음 → 통과.
    last_user = -1
    for i, ev in enumerate(events):
        if ev.get("type") == "user":
            last_user = i

    texts = []
    for ev in events[last_user + 1:]:
        if ev.get("type") != "assistant":
            continue
        content = (ev.get("message") or {}).get("content")
        if isinstance(content, str):
            texts.append(content)
        elif isinstance(content, list):
            for blk in content:
                if isinstance(blk, dict) and blk.get("type") == "text":
                    texts.append(blk.get("text") or "")
    return "\n".join(t for t in texts if t)


def main():
    raw = sys.stdin.read() if not sys.stdin.isatty() else ""
    try:
        data = json.loads(raw) if raw.strip() else {}
    except Exception:
        data = {}

    if data.get("stop_hook_active"):
        return 0
    if os.environ.get("BYPASS_PLAIN_LANGUAGE", "0") == "1":
        return 0

    tpath = data.get("transcript_path")
    if not tpath or not os.path.exists(tpath):
        return 0

    text = extract_current_turn_text(tpath)
    if not text:
        return 0

    try:
        threshold = int(os.environ.get("PLAIN_LANG_JARGON_THRESHOLD", "1"))
    except ValueError:
        threshold = 1

    hits = []
    for pat in build_patterns():
        for ln in text.splitlines():
            hits.extend(re.findall(pat, ln))

    if len(hits) >= threshold:
        sample = ", ".join(sorted(set(hits))[:8])
        reason = (
            "[codeforge 잡소리 검사] 직전 답변에 codeforge 내부 식별자가 {n}개 있다 ({s}). "
            "사용자는 codeforge 내부 사정을 모른다. 평범한 말로 다시 쓰되, 꼭 필요한 식별자는 "
            "평문 한 줄 풀이를 먼저 붙여라. (일반 기술 용어는 회피 대상 아님)"
        ).format(n=len(hits), s=sample)
        print(json.dumps({
            "decision": "block",
            "reason": reason,
            "systemMessage": "codeforge 잡소리 검사: 내부 식별자 {n}개 → 평범하게 다시 씀".format(n=len(hits)),
        }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
