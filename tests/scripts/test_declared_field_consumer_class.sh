#!/usr/bin/env bash
# tests/scripts/test_declared_field_consumer_class.sh
# CFP-2984 Phase 2 (구현 lane) — AC-26 discriminating self-test.
#
# AC-26: `templates/team-spec-*.yaml` 이 선언한 튜닝 필드는 각각
#   {machine / advisory-only / none} **3값 중 정확히 하나**로 분류되어야 하고,
#   그 분류가 **실제 소비자 실측**과 불일치하는 필드는 0건이어야 한다.
#
# ★ 탈출구 봉쇄 (iter2): "미배선으로 표기하면 통과" 는 금지된 처방이다 — `parallel_spawn_cap`
#   처럼 advisory 소비자를 **실제 보유한** 필드를 "미배선" 으로 적으면 거짓 선언이 합격 조건이
#   된다(`ADR-064:1258` 이 같은 줄에서 그 처방을 경고). 본 오라클은 선언 토큰을 3-enum 으로
#   **정규화한 뒤 실측과 대조**하므로, 동의어 표기로는 빠져나갈 수 없다.
#
# ★ 실측 기준 (선언 주석과 동일 문구 — 선언·검사가 같은 기준을 쓴다):
#     machine       = templates/ 밖 코드 파일(*.py *.sh *.js *.ts *.bats *.yml *.yaml)의
#                     비-주석 줄에서 필드명을 읽는 site 존재
#     advisory-only = machine 0 ∧ *.md 산문에 `<field> = <값>` 값 지시 site 존재
#     none          = 둘 다 0 (선언면·인용면만 존재)
#
# ★ INV-T9 (검사 정의역이 자기 자신을 포함할 때 명시): 측정 정의역에서 `tests/**` 를 **제외**한다.
#   본 파일과 픽스처가 필드명을 문자열로 담고 있어, 제외하지 않으면 오라클 자신이 "기계 소비자"
#   로 계상되는 자기오염이 생긴다. 이 제외는 은닉하지 않고 여기 선언한다.
#
# 3방향 mutant (전부 픽스처 실변형 적용):
#   ① 제거      M1 = 한 필드의 분류 선언 줄 삭제                      → fail-closed RED
#   ② 주입      M2 = 오분류 1건 주입 (advisory-only → machine)        → RED
#   ③ 등가변형  M3 = advisory 소비자 보유 필드를 "미배선" 으로 표기     → 정규화 후 실측 대조 RED
#               M3-nc = 실측이 none 인 필드를 "미배선" 으로 표기        → **PASS 유지**(대조군)
#   추가        M4 = enum 밖 토큰("maybe")                            → fail-closed RED
#
# 대조군(INV-T4): 무변조 픽스처 PASS + **실 repo 7 file** PASS.
# INV-T3 순수 픽스처: 네트워크 0 · 실 ~/.claude/** 0 · 실 git 원격 0 · 쓰기는 mktemp -d 내부만.
# Exit 0 = 전 케이스 PASS.

set -euo pipefail
export PYTHONIOENCODING=utf-8

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PASS=0
FAIL=0
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

# ─────────────────────────────────────────────────────────────────────────────
cat > "$WORK/checker.py" <<'PY'
#!/usr/bin/env python3
"""AC-26 선언 소비자 분류 ↔ 실측 대조 (fail-closed).

정의역: <root>/templates/team-spec-*.yaml 의 top-level 스칼라 int/bool 키 = 튜닝 필드.
선언  : 같은 파일 주석의 `consumer_class: <field> = <token>` 라인.
실측  : root 이하 파일 스캔 (tests/** 제외 — INV-T9 자기오염 배제).
"""
import glob
import os
import re
import sys

import yaml

CANON = ("machine", "advisory-only", "none")

# 3-enum 정규화 — 동의어·표기 변형을 정본 토큰으로 접는다(③ 등가변형 봉쇄의 핵심).
SYNONYM = {
    "machine": "machine", "기계": "machine", "machine-consumer": "machine",
    "wired": "machine", "배선": "machine", "기계소비자": "machine",
    "advisory-only": "advisory-only", "advisory": "advisory-only",
    "advisoryonly": "advisory-only", "권고": "advisory-only",
    "advisory only": "advisory-only", "산문": "advisory-only",
    "none": "none", "미배선": "none", "unbound": "none", "unwired": "none",
    "n/a": "none", "na": "none", "없음": "none", "zero": "none", "소비자0": "none",
}

CODE_EXT = (".py", ".sh", ".js", ".ts", ".bats", ".yml", ".yaml")
SKIP_DIRS = {".git", "node_modules", "__pycache__", "tests"}

_DECL_RE = re.compile(
    r"consumer_class\s{0,4}:\s{0,4}([A-Za-z_][A-Za-z0-9_]{0,63})\s{0,4}=\s{0,4}(.{0,40})$"
)


def tuning_fields(path):
    with open(path, encoding="utf-8") as f:
        doc = yaml.safe_load(f) or {}
    return sorted(
        k for k, v in doc.items()
        if isinstance(v, (int, bool)) and not isinstance(v, str)
    )


def declarations(path):
    """{field: raw_token}. 같은 필드 2회 선언 = 모호 → 특수값 '<dup>'."""
    out = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            m = _DECL_RE.search(line.strip())
            if not m:
                continue
            field, raw = m.group(1), m.group(2).strip().strip("`").strip()
            out[field] = "<dup>" if field in out else raw


    return out


def normalize(raw):
    """raw 토큰 → 3-enum. 해소 불가 = None (fail-closed 신호)."""
    if raw is None:
        return None
    key = raw.strip().strip("`\"'").lower()
    key = re.sub(r"\s+", "", key)
    return SYNONYM.get(key)


def _iter_files(root):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            yield os.path.join(dirpath, fn)


def measure(root, field):
    """실측 소비자 클래스 산출 + 근거 site."""
    tmpl_prefix = os.path.join(root, "templates") + os.sep
    machine_sites, advisory_sites = [], []
    assign_re = re.compile(re.escape(field) + r"\s{0,4}=\s{0,4}\S")
    for path in _iter_files(root):
        ext = os.path.splitext(path)[1].lower()
        try:
            with open(path, encoding="utf-8", errors="replace") as f:
                lines = f.readlines()
        except OSError:
            continue
        rel = os.path.relpath(path, root).replace(os.sep, "/")
        if ext in CODE_EXT:
            # 선언면(templates/team-spec-*.yaml) 은 소비가 아니라 선언 — 정의역 밖.
            if path.startswith(tmpl_prefix):
                continue
            for i, line in enumerate(lines, 1):
                s = line.strip()
                if not s or s.startswith("#"):
                    continue
                if field in s:
                    machine_sites.append("%s:%d" % (rel, i))
        elif ext == ".md":
            for i, line in enumerate(lines, 1):
                if assign_re.search(line):
                    advisory_sites.append("%s:%d" % (rel, i))
    if machine_sites:
        return "machine", machine_sites
    if advisory_sites:
        return "advisory-only", advisory_sites
    return "none", []


def main():
    root = os.path.abspath(sys.argv[1])
    specs = sorted(glob.glob(os.path.join(root, "templates", "team-spec-*.yaml")))
    violations = []
    if not specs:
        print("VIOLATION: templates/team-spec-*.yaml 0 건 — 정의역 부재 (fail-closed)")
        sys.exit(1)

    cache = {}
    for path in specs:
        rel = os.path.relpath(path, root).replace(os.sep, "/")
        fields = tuning_fields(path)
        decls = declarations(path)
        if not fields:
            violations.append("%s: 튜닝 필드 0 건 — 정의역 붕괴 (fail-closed)" % rel)
            continue
        for field in fields:
            raw = decls.get(field)
            if raw is None:
                violations.append(
                    "%s: 필드 `%s` 분류 선언 부재 — 3값 중 하나로 분류되지 않음 (fail-closed)"
                    % (rel, field))
                continue
            if raw == "<dup>":
                violations.append(
                    "%s: 필드 `%s` 분류 선언 2회 이상 — 값 모호 (fail-closed)" % (rel, field))
                continue
            declared = normalize(raw)
            if declared is None:
                violations.append(
                    "%s: 필드 `%s` 분류 토큰 '%s' 를 3-enum {machine, advisory-only, none} 으로 "
                    "해소 불가 — 파싱 불가 = 통과 아님 (fail-closed)" % (rel, field, raw))
                continue
            if field not in cache:
                cache[field] = measure(root, field)
            actual, sites = cache[field]
            if declared != actual:
                violations.append(
                    "%s: 필드 `%s` 선언 '%s'(정규형 %s) ≠ 실측 '%s' — 근거 site %s"
                    % (rel, field, raw, declared, actual, sites[:3] or "없음"))

    for v in violations:
        print("VIOLATION: %s" % v)
    if violations:
        print("")
        print("check-declared-field-consumer-class: %d violation" % len(violations))
        sys.exit(1)
    n_fields = sum(len(tuning_fields(p)) for p in specs)
    print("check-declared-field-consumer-class: PASS — %d file / %d field 선언 == 실측"
          % (len(specs), n_fields))
    for field, (actual, sites) in sorted(cache.items()):
        print("  %-26s actual=%-14s sites=%s" % (field, actual, sites[:2] or "없음"))
    sys.exit(0)


if __name__ == "__main__":
    main()
PY

# ─────────────────────────────────────────────────────────────────────────────
# 픽스처 mini-repo — 실 repo 소비자 지형을 축약 재현 (순수 픽스처, 네트워크 0).
# ─────────────────────────────────────────────────────────────────────────────
build_fixture() {
  local dst="$1"
  rm -rf "$dst"
  mkdir -p "$dst/templates" "$dst/skills/rate-limit-429-mitigation" "$dst/archive/adr"
  cat > "$dst/templates/team-spec-alpha.yaml" <<'YAML'
# Team spec — 픽스처 lane
parallel_spawn_cap: 7
spawn_stagger_ms: 0
cascade_circuit_breaker: false
# consumer_class: parallel_spawn_cap = advisory-only
# consumer_class: spawn_stagger_ms = advisory-only
# consumer_class: cascade_circuit_breaker = none
lane: alpha
YAML
  # advisory 소비자: 산문이 값을 지시 (기계 파서 아님)
  cat > "$dst/skills/rate-limit-429-mitigation/SKILL.md" <<'MD'
# rate-limit mitigation (픽스처)

intensity == 0 (통상 경로):
```
parallel_spawn_cap = 7  # default
spawn_stagger_ms = 0    # no stagger
```
MD
  # 인용면 — 링크·신설 기록은 소비가 아니다 (cascade_circuit_breaker 가 none 으로 남아야 함)
  cat > "$dst/archive/adr/ADR-044-fixture.md" <<'MD'
`cascade_circuit_breaker: bool` (optional, default false) 3 field 신설 — 링크 인용면.
MD
}

run_check() {
  local root="$1" outvar_rc
  set +e
  CHECK_OUT="$(python3 "$WORK/checker.py" "$root" 2>&1)"
  outvar_rc=$?
  set -e
  CHECK_RC=$outvar_rc
}

assert_verdict() {
  # assert_verdict <name> <PASS|RED> <root>
  local name="$1" expect="$2" root="$3" verdict
  run_check "$root"
  verdict="PASS"; [ "$CHECK_RC" -eq 0 ] || verdict="RED"
  if [ "$verdict" = "$expect" ]; then
    echo "OK  $name (expect=$expect got=$verdict)"
    PASS=$((PASS+1))
  else
    echo "X   FAIL: $name (expect=$expect got=$verdict)"
    echo "$CHECK_OUT" | sed 's/^/    /'
    FAIL=$((FAIL+1))
  fi
}

patch_decl() {
  # patch_decl <fixture-root> <old-substring> <new-substring>
  python3 - "$1/templates/team-spec-alpha.yaml" "$2" "$3" <<'PY'
import io, sys
path, old, new = sys.argv[1], sys.argv[2], sys.argv[3]
raw = io.open(path, encoding="utf-8").read()
if old not in raw:
    print("SETUP: mutant 앵커 미발견 %r" % old, file=sys.stderr)
    sys.exit(3)
io.open(path, "w", encoding="utf-8", newline="\n").write(raw.replace(old, new, 1))
PY
}

echo "── AC-26 declared field consumer class"

# ── 대조군 ① 픽스처 정본 ────────────────────────────────────────────────────
build_fixture "$WORK/base"
assert_verdict "baseline/픽스처 정본" PASS "$WORK/base"
echo "$CHECK_OUT" | sed 's/^/    /'

# ── 대조군 ② 실 repo 7 file (실측 지형 위 GREEN) ────────────────────────────
assert_verdict "baseline/실 repo templates 7 file" PASS "$REPO_ROOT"
echo "$CHECK_OUT" | sed 's/^/    /'

# ── ① 제거 ──────────────────────────────────────────────────────────────────
build_fixture "$WORK/m1"
patch_decl "$WORK/m1" "# consumer_class: spawn_stagger_ms = advisory-only
" ""
assert_verdict "M1 ①제거: 분류 선언 줄 삭제" RED "$WORK/m1"

# ── ② 주입 (오분류) ─────────────────────────────────────────────────────────
build_fixture "$WORK/m2"
patch_decl "$WORK/m2" "consumer_class: parallel_spawn_cap = advisory-only" \
                      "consumer_class: parallel_spawn_cap = machine"
assert_verdict "M2 ②주입: 오분류 1건 (advisory-only→machine)" RED "$WORK/m2"

# ── ③ 등가변형: 탈출구 "미배선" ─────────────────────────────────────────────
build_fixture "$WORK/m3"
patch_decl "$WORK/m3" "consumer_class: parallel_spawn_cap = advisory-only" \
                      "consumer_class: parallel_spawn_cap = 미배선"
assert_verdict "M3 ③등가변형: advisory 보유 필드를 '미배선' 표기" RED "$WORK/m3"

build_fixture "$WORK/m3b"
patch_decl "$WORK/m3b" "consumer_class: spawn_stagger_ms = advisory-only" \
                       "consumer_class: spawn_stagger_ms = unbound"
assert_verdict "M3b ③등가변형: 'unbound' 표기" RED "$WORK/m3b"

build_fixture "$WORK/m3c"
patch_decl "$WORK/m3c" "consumer_class: spawn_stagger_ms = advisory-only" \
                       "consumer_class: spawn_stagger_ms = N/A"
assert_verdict "M3c ③등가변형: 'N/A' 표기" RED "$WORK/m3c"

# ── ③ 대조군 (정규화가 '아무 동의어나 RED' 가 아님을 증명) ──────────────────
build_fixture "$WORK/m3nc"
patch_decl "$WORK/m3nc" "consumer_class: cascade_circuit_breaker = none" \
                        "consumer_class: cascade_circuit_breaker = 미배선"
assert_verdict "M3-nc ③대조군: 실측 none 필드의 '미배선' 표기는 PASS" PASS "$WORK/m3nc"

# ── ④ enum 밖 토큰 = fail-closed ───────────────────────────────────────────
build_fixture "$WORK/m4"
patch_decl "$WORK/m4" "consumer_class: cascade_circuit_breaker = none" \
                      "consumer_class: cascade_circuit_breaker = maybe"
assert_verdict "M4 enum 밖 토큰 'maybe' = fail-closed" RED "$WORK/m4"

# ── 형제 회귀: 신규 튜닝 필드가 분류 없이 추가되면 잡히는가 ─────────────────
build_fixture "$WORK/sib"
python3 - "$WORK/sib/templates/team-spec-alpha.yaml" <<'PY'
import io, sys
p = sys.argv[1]
raw = io.open(p, encoding="utf-8").read()
raw = raw.replace("lane: alpha", "new_tuning_knob: 3\nlane: alpha")
io.open(p, "w", encoding="utf-8", newline="\n").write(raw)
PY
assert_verdict "형제/신규 튜닝 필드 무분류 추가" RED "$WORK/sib"

# ── 형제 회귀: 실 기계 소비자가 생기면 advisory-only 선언이 RED 로 뒤집히는가 ─
build_fixture "$WORK/sib2"
mkdir -p "$WORK/sib2/scripts"
cat > "$WORK/sib2/scripts/reader.sh" <<'SH'
#!/usr/bin/env bash
CAP=$(yq '.parallel_spawn_cap' templates/team-spec-alpha.yaml)
echo "$CAP"
SH
assert_verdict "형제/기계 소비자 등장 시 advisory-only 선언 RED" RED "$WORK/sib2"

echo "── 결과: PASS=$PASS FAIL=$FAIL"
[ "$FAIL" -eq 0 ] || exit 1
