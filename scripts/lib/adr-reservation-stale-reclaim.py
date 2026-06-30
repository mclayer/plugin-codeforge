#!/usr/bin/env python3
# scripts/lib/adr-reservation-stale-reclaim.py
# CFP-2491 / Epic CFP-2481 E3b — ADR-RESERVATION slot-level stale claim 자동 회수 로직.
#
# FIX (구현리뷰 P0 carry — F1): inline YAML heredoc Python(`python3 - <<'PY'`) → 별도 스크립트 추출.
#   근거: heredoc 들여쓰기 fragility 근본 제거 + 테스트 가능(test-escape 폐쇄) + ADR-061 §결정6 정합.
#   (구현리뷰 Claude P0 = YAML run-block 들여쓰기 보존 의혹 — DeveloperPL firsthand 재현 시 YAML
#    block-scalar dedent 로 column-0 도달해 IndentationError 미재현했으나, fragility class 영구 제거 +
#    test-escape 폐쇄를 위해 권장 B(추출) 채택. strengthen direction, 약화 surface 0.)
#
# 정책 (ADR-133 Amendment 1 A1-4 / Change Plan §3.5):
#   abandoned 영구 마킹 + 번호 재사용 금지 + gap(구멍) audit 보존.
#   abandoned slot free 복원은 단조성 위반 → A→abandoned→A ABA 재현. 회수 = "재사용 가능 표시"가 아니라
#   "abandoned 영구 마킹 + 다음 번호 진행, gap audit 보존" (`source:` Herlihy & Wing, "Linearizability",
#   ACM TOCS 1990 §5 — CAS counter ABA 단조성). max_adr_number 절대 감소 금지.
#
# 대상: claim state JSON 의 claims[] 중 status==claimed ∧ claimed_at < cutoff ∧ 대응 ADR 파일 미존재
#       → status: abandoned 마킹.
#
# Usage:
#   python3 scripts/lib/adr-reservation-stale-reclaim.py \
#       --state-file <claim-state.json> --adr-dir archive/adr --cutoff 2026-05-31T00:00:00Z \
#       [--out <new-state.json>]
#
# stdout: 적용 결과 요약 JSON `{"changed": N, "state": {...}}` (--out 미지정 시).
# --out 지정 시: 갱신된 state 만 해당 파일에 indent=2 로 write + stdout 에 changed 정수 1줄.
# exit 0 = 정상 (changed=0 포함). 비정상 입력 = exit 1.

import argparse
import glob
import json
import os
import sys


def reclaim_stale_claims(state: dict, adr_dir: str, cutoff: str) -> int:
    """state(claim JSON dict)를 in-place 수정해 stale claimed slot 을 abandoned 마킹.

    반환: abandoned 로 전환된 slot 수(changed). max_adr_number 는 절대 변경하지 않는다(단조성 보존).
    """
    changed = 0
    for c in state.get("claims", []):
        if c.get("status") != "claimed":
            continue
        if c.get("claimed_at", "") >= cutoff:
            continue  # 아직 TTL 미경과
        n = c.get("adr_number")
        # 대응 ADR 파일 존재 시 = committed/active → 회수 대상 아님.
        hits = glob.glob(os.path.join(adr_dir, f"ADR-{n}-*.md"))
        if hits:
            continue
        # stale claimed + ADR 미존재 → abandoned 영구 마킹 (번호 재사용 금지, gap 보존).
        c["status"] = "abandoned"
        c["abandoned_at"] = cutoff
        changed += 1
    # max_adr_number 는 절대 감소 안 함 (단조성 보존 — gap 잔류). 의도적 무수정.
    return changed


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="ADR-RESERVATION slot-level stale claim 자동 회수 (ADR-133)")
    p.add_argument("--state-file", required=True, help="claim state JSON 입력 파일")
    p.add_argument("--adr-dir", required=True, help="ADR 파일 디렉터리 (예: archive/adr)")
    p.add_argument("--cutoff", required=True, help="ISO 8601 cutoff — claimed_at 이 이 시각 이전이면 stale 후보")
    p.add_argument("--out", default=None, help="갱신 state write 대상 (미지정 시 stdout 에 요약 JSON)")
    args = p.parse_args(argv)

    try:
        with open(args.state_file, encoding="utf-8") as f:
            state = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        print(f"::error::claim state 읽기 실패: {e}", file=sys.stderr)
        return 1

    changed = reclaim_stale_claims(state, args.adr_dir, args.cutoff)

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
            f.write("\n")
        print(changed)
    else:
        print(json.dumps({"changed": changed, "state": state}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
