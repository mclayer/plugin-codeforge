"""
eval_story_init_trigger_expr.py
CFP-2252 (S4) / ADR-049 Amendment 2 §3.2 (F5) — story-init.yml trigger if-expression
truth-table 평가 harness (CI-gated, stdlib only — node 의존 0).

목적:
  actionlint 는 if-expression 의 truth-value 를 평가하지 않음 (문법만). 음성 조건
  (TC-8 Bug 오발화 차단 / TC-9 phase gate / TC-10 null 안전)은 production canary 로
  음성 증명 불가 → 본 harness 가 음성/양성 조건을 결정적으로 검증한다 (역할 분리:
  canary = 양성 조건 production 입증 / 본 harness = 음성+양성 truth-table).

scope:
  story-init.yml 의 native-type cutover 후 if-expression 의 실제 연산자 부분집합만
  재구현 — `contains()` / `==` / `||` / `&&` / null 비교. (전체 GitHub Actions
  expression engine 재구현 아님 — maintenance 비용 회피, self-host 안전.)

post-cutover if-expression (ADR-049 Amendment 2 §3.2):
  (action == 'opened' || label.name == 'phase:요구사항' || action == 'typed')
  && (issue.type.name == 'Story' || contains(labels, 'type:story'))
  && contains(labels, 'phase:요구사항')

GitHub Actions null 비교 semantics:
  - 부재/null 객체의 property 접근 → null (no error).
  - null == 'Story' → false (안전).
  - contains(null, x) 는 본 workflow 에서 발생 안 함 (labels.*.name 은 항상 array).

Usage:
  # self-test (11 truth-table case — TC-6~11 + baseline):
  python3 scripts/lib/eval_story_init_trigger_expr.py --self-test
  # single fixture (JSON on stdin) → "fire" / "skip":
  echo '{"action":"opened","type_name":"Story","labels":["phase:요구사항"]}' \
    | python3 scripts/lib/eval_story_init_trigger_expr.py

exit code: 0 = (self-test PASS) 또는 (단일 평가 정상) / 1 = self-test FAIL 또는 입력 오류.
"""
import json
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


def evaluate(ctx: dict) -> bool:
    """post-cutover story-init.yml if-expression 의 truth-value 평가.

    ctx keys:
      action: str           — github.event.action ('opened' / 'labeled' / 'typed' / ...)
      label_name: str|None  — github.event.label.name (labeled 이벤트만 set; 그 외 None)
      type_name: str|None   — github.event.issue.type.name (native type 부재 시 None)
      labels: list[str]     — github.event.issue.labels.*.name
    """
    action = ctx.get("action")
    label_name = ctx.get("label_name")  # opened/typed 이벤트엔 None (Actions null)
    type_name = ctx.get("type_name")    # native type 부재 = None (null-safe)
    labels = ctx.get("labels") or []

    def contains(haystack, needle):
        # contains(array, item) — Actions array membership
        return needle in (haystack or [])

    # 1번 그룹: 발화 trigger 이벤트 (opened OR phase:요구사항 labeled OR typed)
    event_gate = (
        action == "opened"
        or label_name == "phase:요구사항"   # None == 'phase:요구사항' → False (null 안전)
        or action == "typed"
    )

    # 2번 그룹: Story 판별 OR-bridge (native type == 'Story' OR type:story 라벨)
    story_gate = (
        type_name == "Story"               # None == 'Story' → False (null 안전)
        or contains(labels, "type:story")
    )

    # 3번 그룹: phase gate AND 보존 (요구사항 lane 진입 신호 — type 단독 발화 차단)
    phase_gate = contains(labels, "phase:요구사항")

    return event_gate and story_gate and phase_gate


# 11 truth-table — §8.2 TC-6~11 (음성/양성) + baseline 5 (현 동작 보존 회귀).
# 각 case: (id, ctx, expect_fire, note)
TRUTH_TABLE = [
    # --- §8.2 TC-6~11 (Change Plan 명시 케이스) ---
    (
        "TC-6",
        {"action": "opened", "type_name": "Story", "label_name": None,
         "labels": ["phase:요구사항"]},
        True,
        "native-type only (type:story 라벨 부재) — 라벨삭제 후 발화 보존",
    ),
    (
        "TC-7",
        {"action": "opened", "type_name": None, "label_name": None,
         "labels": ["type:story", "phase:요구사항"]},
        True,
        "라벨 fallback (issue.type null) — org type 미활성 consumer",
    ),
    (
        "TC-8",
        {"action": "opened", "type_name": "Bug", "label_name": None,
         "labels": ["phase:요구사항"]},
        False,
        "Bug type — Story 아님 → 미발화 (오발화 차단)",
    ),
    (
        "TC-9",
        {"action": "opened", "type_name": "Story", "label_name": None,
         "labels": []},
        False,
        "phase:요구사항 라벨 부재 → 미발화 (phase gate AND 보존)",
    ),
    (
        "TC-10",
        {"action": "opened", "type_name": None, "label_name": None,
         "labels": []},
        False,
        "issue.type null + 라벨 모두 부재 → 미발화 (null 안전성)",
    ),
    (
        "TC-11",
        {"action": "typed", "type_name": "Story", "label_name": None,
         "labels": ["phase:요구사항"]},
        True,
        "typed 이벤트 + Story type + phase:요구사항 → 발화",
    ),
    # --- baseline 회귀 (기존 라벨-only 동작 보존 — labeled re-trigger) ---
    (
        "BL-1",
        {"action": "labeled", "type_name": None, "label_name": "phase:요구사항",
         "labels": ["type:story", "phase:요구사항"]},
        True,
        "labeled(phase:요구사항) re-trigger + 라벨 — 기존 CFP-280 race fix 발화 보존",
    ),
    (
        "BL-2",
        {"action": "labeled", "type_name": None, "label_name": "component:api",
         "labels": ["type:story", "phase:요구사항"]},
        False,
        "labeled(무관 라벨) — event_gate false (CFP-2149 gate 라벨 편집 재트리거 차단)",
    ),
    (
        "BL-3",
        {"action": "labeled", "type_name": "Story", "label_name": "phase:요구사항",
         "labels": ["phase:요구사항"]},
        True,
        "labeled(phase:요구사항) + native Story type (라벨 부재) — 전환 후 발화",
    ),
    (
        "BL-4",
        {"action": "typed", "type_name": "Bug", "label_name": None,
         "labels": ["phase:요구사항"]},
        False,
        "typed + Bug type — story_gate false (오발화 차단)",
    ),
    (
        "BL-5",
        {"action": "opened", "type_name": "Story", "label_name": None,
         "labels": ["type:story", "phase:요구사항"]},
        True,
        "transient dual-state (native Story + type:story 라벨 공존) — 발화 보존",
    ),
]


def run_self_test() -> int:
    failures = []
    for case_id, ctx, expect, note in TRUTH_TABLE:
        got = evaluate(ctx)
        status = "PASS" if got == expect else "FAIL"
        line = (
            f"[{status}] {case_id}: expect={'fire' if expect else 'skip'} "
            f"got={'fire' if got else 'skip'} — {note}"
        )
        print(line)
        if got != expect:
            failures.append(case_id)
    print(f"\n{len(TRUTH_TABLE) - len(failures)}/{len(TRUTH_TABLE)} truth-table case PASS")
    if failures:
        print(f"FAIL: {', '.join(failures)}", file=sys.stderr)
        return 1
    return 0


def run_single() -> int:
    # stdin 을 UTF-8 로 강제 read (Windows cp949 mojibake 차단 — 한글 라벨 매칭 보존).
    if hasattr(sys.stdin, "reconfigure"):
        try:
            sys.stdin.reconfigure(encoding="utf-8")
        except (ValueError, OSError):
            pass
    raw = sys.stdin.read().strip()
    if not raw:
        print("::error::빈 입력 — JSON ctx 또는 --self-test 필요", file=sys.stderr)
        return 1
    try:
        ctx = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"::error::JSON parse 실패: {e}", file=sys.stderr)
        return 1
    # alias 허용: type_name | type / labels | label_names
    if "type" in ctx and "type_name" not in ctx:
        ctx["type_name"] = ctx["type"]
    print("fire" if evaluate(ctx) else "skip")
    return 0


def main() -> int:
    if "--self-test" in sys.argv:
        return run_self_test()
    return run_single()


if __name__ == "__main__":
    sys.exit(main())
