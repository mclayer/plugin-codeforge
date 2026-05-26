#!/usr/bin/env python3
"""codeforge UserPromptSubmit hook 로직 — 한영 키보드 레이아웃 변환 추론. (CFP-1751)

플러그인 배포본. 모든 consumer 자동 적용. hooks/korean-english-recovery (bash shim) 가 호출.

목적: 사용자가 한영 전환 키를 누르지 못한 채 입력한 메시지를 두벌식 ↔ QWERTY 매핑으로
변환해 의미 후보를 추정. 결과를 additionalContext 로 주입 → Orchestrator 가 변환 의미로
답변하고 첫 줄에 "한영전환으로 읽음" 통보 후 진행.

설정 (consumer 환경변수):
  BYPASS_KOREAN_ENGLISH_RECOVERY=1   비활성화

동작:
  - stdin 으로 UserPromptSubmit JSON 수신 (`prompt` 필드).
  - 양방향 시도: eng→kor (영문 키로 한글 의도) / kor→eng (한글 키로 영어 의도).
  - 품질 점수(합성 음절 비율 / 영어 vowel 분포) 임계치 이상이면 additionalContext 출력.
  - 그 외에는 조용히 통과.

fail-safe: 어떤 실패(파싱 / 예외 / python missing 등)에도 통과 (block 안 함).
"""
import sys
import os
import json

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

# 두벌식 한글 키보드 → 자모 매핑
ENG_TO_JAMO = {
    'q': 'ㅂ', 'w': 'ㅈ', 'e': 'ㄷ', 'r': 'ㄱ', 't': 'ㅅ',
    'y': 'ㅛ', 'u': 'ㅕ', 'i': 'ㅑ', 'o': 'ㅐ', 'p': 'ㅔ',
    'a': 'ㅁ', 's': 'ㄴ', 'd': 'ㅇ', 'f': 'ㄹ', 'g': 'ㅎ',
    'h': 'ㅗ', 'j': 'ㅓ', 'k': 'ㅏ', 'l': 'ㅣ',
    'z': 'ㅋ', 'x': 'ㅌ', 'c': 'ㅊ', 'v': 'ㅍ', 'b': 'ㅠ', 'n': 'ㅜ', 'm': 'ㅡ',
    'Q': 'ㅃ', 'W': 'ㅉ', 'E': 'ㄸ', 'R': 'ㄲ', 'T': 'ㅆ',
    'O': 'ㅒ', 'P': 'ㅖ',
}
JAMO_TO_ENG = {v: k for k, v in ENG_TO_JAMO.items()}

# Hangul 음절 인덱스 (U+AC00 base)
CHOSEONG = ['ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅃ', 'ㅅ',
            'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']
JUNGSEONG = ['ㅏ', 'ㅐ', 'ㅑ', 'ㅒ', 'ㅓ', 'ㅔ', 'ㅕ', 'ㅖ', 'ㅗ', 'ㅘ', 'ㅙ',
             'ㅚ', 'ㅛ', 'ㅜ', 'ㅝ', 'ㅞ', 'ㅟ', 'ㅠ', 'ㅡ', 'ㅢ', 'ㅣ']
JONGSEONG = ['', 'ㄱ', 'ㄲ', 'ㄳ', 'ㄴ', 'ㄵ', 'ㄶ', 'ㄷ', 'ㄹ', 'ㄺ', 'ㄻ',
             'ㄼ', 'ㄽ', 'ㄾ', 'ㄿ', 'ㅀ', 'ㅁ', 'ㅂ', 'ㅄ', 'ㅅ', 'ㅆ', 'ㅇ',
             'ㅈ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']

CHO_SET = set(CHOSEONG)
JUNG_BASIC = {'ㅏ', 'ㅐ', 'ㅑ', 'ㅒ', 'ㅓ', 'ㅔ', 'ㅕ', 'ㅖ',
              'ㅗ', 'ㅛ', 'ㅜ', 'ㅠ', 'ㅡ', 'ㅣ'}

# 복합 모음 결합 (두벌식 입력 시 두 단모음을 누르면 합성)
COMBINE_V = {
    ('ㅗ', 'ㅏ'): 'ㅘ', ('ㅗ', 'ㅐ'): 'ㅙ', ('ㅗ', 'ㅣ'): 'ㅚ',
    ('ㅜ', 'ㅓ'): 'ㅝ', ('ㅜ', 'ㅔ'): 'ㅞ', ('ㅜ', 'ㅣ'): 'ㅟ',
    ('ㅡ', 'ㅣ'): 'ㅢ',
}
# 복합 종성
COMBINE_J = {
    ('ㄱ', 'ㅅ'): 'ㄳ',
    ('ㄴ', 'ㅈ'): 'ㄵ', ('ㄴ', 'ㅎ'): 'ㄶ',
    ('ㄹ', 'ㄱ'): 'ㄺ', ('ㄹ', 'ㅁ'): 'ㄻ', ('ㄹ', 'ㅂ'): 'ㄼ',
    ('ㄹ', 'ㅅ'): 'ㄽ', ('ㄹ', 'ㅌ'): 'ㄾ', ('ㄹ', 'ㅍ'): 'ㄿ', ('ㄹ', 'ㅎ'): 'ㅀ',
    ('ㅂ', 'ㅅ'): 'ㅄ',
}
SPLIT_V = {v: k for k, v in COMBINE_V.items()}
SPLIT_J = {v: k for k, v in COMBINE_J.items()}


def compose_jamos(jamos):
    """자모 리스트 → Hangul 음절 합성. 합성 불가 토큰은 그대로 통과."""
    out = []
    i = 0
    n = len(jamos)
    while i < n:
        j = jamos[i]
        if j not in CHO_SET:
            out.append(j)
            i += 1
            continue
        cho = j
        # 중성 필요
        if i + 1 >= n or jamos[i + 1] not in JUNG_BASIC:
            out.append(cho)
            i += 1
            continue
        jung = jamos[i + 1]
        ci = i + 2
        # 복합 모음
        if ci < n and (jung, jamos[ci]) in COMBINE_V:
            jung = COMBINE_V[(jung, jamos[ci])]
            ci += 1
        # 종성 (다음 자음이 다음 음절 초성인지 판단)
        jong = ''
        if ci < n and jamos[ci] in CHO_SET:
            jc = jamos[ci]
            if ci + 1 < n and jamos[ci + 1] in JUNG_BASIC:
                # jc 는 다음 음절 초성
                pass
            elif ci + 1 < n and jamos[ci + 1] in CHO_SET and (jc, jamos[ci + 1]) in COMBINE_J:
                # 복합 종성 가능, 그 다음이 모음이면 두 번째 자음은 다음 초성
                if ci + 2 < n and jamos[ci + 2] in JUNG_BASIC:
                    jong = jc
                    ci += 1
                else:
                    jong = COMBINE_J[(jc, jamos[ci + 1])]
                    ci += 2
            else:
                jong = jc
                ci += 1
        try:
            cho_idx = CHOSEONG.index(cho)
            jung_idx = JUNGSEONG.index(jung)
            jong_idx = JONGSEONG.index(jong) if jong else 0
            code = 0xAC00 + cho_idx * 588 + jung_idx * 28 + jong_idx
            out.append(chr(code))
        except (ValueError, IndexError):
            out.append(cho)
            out.append(jung)
            if jong:
                out.append(jong)
        i = ci
    return ''.join(out)


def eng_to_kor(s):
    jamos = []
    for ch in s:
        if ch in ENG_TO_JAMO:
            jamos.append(ENG_TO_JAMO[ch])
        else:
            jamos.append(ch)
    return compose_jamos(jamos)


def decompose_syllable(ch):
    code = ord(ch)
    if 0xAC00 <= code <= 0xD7A3:
        base = code - 0xAC00
        return (CHOSEONG[base // 588], JUNGSEONG[(base // 28) % 21], JONGSEONG[base % 28])
    return None


def kor_to_eng(s):
    out = []
    for ch in s:
        d = decompose_syllable(ch)
        if d is None:
            if ch in JAMO_TO_ENG:
                out.append(JAMO_TO_ENG[ch])
            else:
                out.append(ch)
            continue
        cho, jung, jong = d
        if cho in JAMO_TO_ENG:
            out.append(JAMO_TO_ENG[cho])
        if jung in SPLIT_V:
            a, b = SPLIT_V[jung]
            out.append(JAMO_TO_ENG.get(a, ''))
            out.append(JAMO_TO_ENG.get(b, ''))
        elif jung in JAMO_TO_ENG:
            out.append(JAMO_TO_ENG[jung])
        if jong:
            if jong in SPLIT_J:
                a, b = SPLIT_J[jong]
                out.append(JAMO_TO_ENG.get(a, ''))
                out.append(JAMO_TO_ENG.get(b, ''))
            elif jong in JAMO_TO_ENG:
                out.append(JAMO_TO_ENG[jong])
    return ''.join(out)


# --- Heuristics ---

def hangul_composed_ratio(s):
    non_ws = [c for c in s if not c.isspace()]
    if not non_ws:
        return 0.0
    composed = sum(1 for c in non_ws if 0xAC00 <= ord(c) <= 0xD7A3)
    return composed / len(non_ws)


def mappable_ascii_ratio(s):
    non_ws = [c for c in s if not c.isspace()]
    if not non_ws:
        return 0.0
    mappable = sum(1 for c in non_ws if c in ENG_TO_JAMO)
    return mappable / len(non_ws)


def english_vowel_ratio(s):
    letters = [c for c in s.lower() if c.isalpha() and ord(c) < 128]
    if not letters:
        return 0.0
    vowels = sum(1 for c in letters if c in 'aeiou')
    return vowels / len(letters)


def looks_like_korean_mistype(prompt):
    p = prompt.strip()
    if len(p) < 4:
        return False
    return mappable_ascii_ratio(p) >= 0.8


def looks_like_english_mistype(prompt):
    p = prompt.strip()
    if len(p) < 3:
        return False
    return hangul_composed_ratio(p) >= 0.7


def conversion_quality(direction, original, converted):
    if direction == 'eng_to_kor':
        return hangul_composed_ratio(converted)
    # kor → eng
    non_ws = [c for c in converted if not c.isspace()]
    if not non_ws:
        return 0.0
    letter_ratio = sum(1 for c in non_ws if c.isalpha() and ord(c) < 128) / len(non_ws)
    if letter_ratio < 0.8:
        return 0.0
    vr = english_vowel_ratio(converted)
    if 0.20 <= vr <= 0.60:
        return 0.5 + letter_ratio * 0.4
    return letter_ratio * 0.3


def main():
    raw = sys.stdin.read() if not sys.stdin.isatty() else ""
    try:
        data = json.loads(raw) if raw.strip() else {}
    except Exception:
        return 0

    if os.environ.get("BYPASS_KOREAN_ENGLISH_RECOVERY", "0") == "1":
        return 0

    prompt = data.get("prompt", "")
    if not isinstance(prompt, str):
        return 0
    p = prompt.strip()
    if len(p) < 4:
        return 0

    best = None

    # eng → kor (영문 키로 한글 의도)
    if looks_like_korean_mistype(p):
        try:
            cand = eng_to_kor(p)
            q = conversion_quality('eng_to_kor', p, cand)
            if q >= 0.7 and cand != p:
                best = ('eng_to_kor', p, cand, q)
        except Exception:
            pass

    # kor → eng (한글 키로 영어 의도)
    if best is None and looks_like_english_mistype(p):
        try:
            cand = kor_to_eng(p)
            q = conversion_quality('kor_to_eng', p, cand)
            if q >= 0.5 and cand != p:
                best = ('kor_to_eng', p, cand, q)
        except Exception:
            pass

    if best:
        direction, orig, conv, q = best
        orig_short = orig if len(orig) <= 80 else orig[:77] + '...'
        conv_short = conv if len(conv) <= 80 else conv[:77] + '...'
        label = (
            '영문 키로 입력 → 한국어 의도 추정'
            if direction == 'eng_to_kor'
            else '한글 키로 입력 → 영어 의도 추정'
        )
        ctx = (
            "[codeforge 한영전환 추정] 사용자 입력이 키보드 한영전환 실수로 추정됨 "
            "(품질 점수 {q:.2f}).\n"
            "방향: {label}\n"
            "원문: {orig}\n"
            "변환 후보: {conv}\n"
            "행동: 변환 후보로 의미 추론하여 답변하고, 답 첫 줄에 "
            "짧게 통보 ('한영전환으로 읽음: <원문> → <변환문>'). "
            "추정이 틀리면 사용자가 한 마디로 정정. "
            "(memory: feedback_korean_english_layout_recovery)"
        ).format(q=q, label=label, orig=orig_short, conv=conv_short)
        out = {
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext": ctx,
            }
        }
        print(json.dumps(out, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
