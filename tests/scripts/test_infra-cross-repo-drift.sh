#!/usr/bin/env bash
# tests/scripts/test_infra-cross-repo-drift.sh
# CFP-2700 (Epic) G5 Phase 2 (구현 lane) — Discriminating self-test (.sh channel) for the
#   `--cross-repo` mode of scripts/lib/check_infra_resource_drift.py (ADR-157 §결정4 cross-repo 대조).
#
# ★ 보안 민감 슬라이스 (untrusted foreign-repo content ingest + read-WRITE PAT) — §7 위협모델 1급.
#   실 네트워크 금지 — fetch·Issue-발행을 **주입가능 seam**(env)으로 stub:
#     INFRA_CROSS_REPO_FETCH_ROOT = local mock-repo fixture(디렉터리 = 가짜 저장소 트리),
#       트리 <froot>/<ns>/<ref>/<path> (ref 를 경로에 반영 = ref-pin 시연) + sidecar `<path>.status`.
#     INFRA_CROSS_REPO_ISSUE_SINK = transient fail-open 시 Issue 를 append 할 JSON sink 파일.
#
# ★ 3-way (AC-21): (a) content-mismatch → FAIL(exit 1) / (b) 전파 → PASS(exit 0) / (c) token 부재 →
#   degraded-FAIL(exit 3). normative 2: (t1) transient → fail-open+WARN+Issue (미발행 mutant=RED) /
#   (t2) content-mismatch ≠ transient (오분류 mutant=최중요 RED). + ref-pin(moving HEAD 거부/idempotent) +
#   403·404 fail-closed + namespace spoof hard-fail + secret-masking(§7.3 PAT 값 미출력) + vacuous.
#
# ★ 판별력 = presence-only 금지 — 실 exit code + FIXED 출력 토큰 결박 + 대표 mutation RED-flip
#   (스캐너 소스 변형 시 test 가 오분류를 잡아 RED = 로직 load-bearing 증명).
#
# self-contained bash (tests/scripts 관례 — ADR-151 인벤토리 enroll 채널). Exit 0 = 전 케이스 PASS.

set -uo pipefail
export PYTHONIOENCODING=utf-8

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SSOT_PY="$REPO_ROOT/scripts/lib/check_infra_resource_drift.py"
PASS=0
FAIL=0

TOKEN_ENV="CODEFORGE_CROSS_REPO_PAT"
FETCH_ROOT_ENV="INFRA_CROSS_REPO_FETCH_ROOT"
ISSUE_SINK_ENV="INFRA_CROSS_REPO_ISSUE_SINK"
SENTINEL="ghp_SEKRETsentinelVALUE0123456789abcd"   # secret-masking 실증용 (실 PAT 아님) — 미출력이 계약
NS="acme/foreign-collector"
REF="v1.2.3"
FPATH="src/config.txt"
CANON="MCTRADER_RAW_NAS_URL"
FOREIGN_PROPAGATED='let url = std::env::var("MCTRADER_RAW_NAS_URL").unwrap();'
FOREIGN_MISMATCH='let url = std::env::var("OLD_MINIO_URL").unwrap();  // 미전파 = derived grep 0건'

# ── manifest carrier 생성 (cross-repo 는 repo-local scan 안 함 — carrier 만 필요) ──
_mk_repo() {  # <tmp> <ref> [namespaced(1|0)]
  local tmp="$1" ref="$2" namespaced="${3:-1}"
  mkdir -p "$tmp/.claude/_overlay"
  if [ "$namespaced" = "1" ]; then
    cat > "$tmp/.claude/_overlay/project.yaml" <<EOF
infra_resources:
  resources:
    - id: raw-nas
      namespace: $NS
      canonical_env: $CANON
      cross_repo_ref: $ref
      cross_repo_path: $FPATH
      aliases:
        accepted: []
EOF
  else
    cat > "$tmp/.claude/_overlay/project.yaml" <<EOF
infra_resources:
  resources:
    - id: local-only
      canonical_env: $CANON
      aliases:
        accepted: []
EOF
  fi
}

# ── mock-repo fixture 파일 생성 ──
_mk_mock() {  # <froot> <ref> <mode(content|status)> <payload>
  local froot="$1" ref="$2" mode="$3" payload="$4"
  mkdir -p "$froot/$NS/$ref/$(dirname "$FPATH")"
  if [ "$mode" = "content" ]; then
    printf '%s\n' "$payload" > "$froot/$NS/$ref/$FPATH"
  else
    printf '%s\n' "$payload" > "$froot/$NS/$ref/$FPATH.status"
  fi
}

# ── scanner 실행 (상속 seam/토큰 env 제거 = hermetic; '-' = 미설정) ──
_run() {  # <scanner_py> <repo_root> <token|-> <froot|-> <sink|->
  local py="$1" root="$2" tok="$3" froot="$4" sink="$5"
  local -a e=(env -u "$TOKEN_ENV" -u "$FETCH_ROOT_ENV" -u "$ISSUE_SINK_ENV" "PYTHONIOENCODING=utf-8")
  [ "$tok" != "-" ]   && e+=("$TOKEN_ENV=$tok")
  [ "$froot" != "-" ] && e+=("$FETCH_ROOT_ENV=$froot")
  [ "$sink" != "-" ]  && e+=("$ISSUE_SINK_ENV=$sink")
  "${e[@]}" python3 "$py" --repo-root "$root" --cross-repo 2>&1
}

# ── mutant 생성 (SSOT 문자열-치환) ──
_mkmutant() {  # <kind> <outpath>
  python3 - "$SSOT_PY" "$2" "$1" <<'PY'
import sys
src_path, out_path, kind = sys.argv[1], sys.argv[2], sys.argv[3]
s = open(src_path, encoding="utf-8").read()
if kind == "mismatch_as_transient":
    s2 = s.replace("                drift.append((rid, ns, canon, ref, path))",
                   "                transient.append((rid, ns, canon))  # MUTANT", 1)
elif kind == "issue_publish_off":
    s2 = s.replace("            published = _publish_issue(issue_sink, title, body, token)",
                   "            published = False  # MUTANT", 1)
elif kind == "token_check_off":
    s2 = s.replace("    if not token:", "    if False:  # MUTANT", 1)
elif kind == "refpin_off":
    s2 = s.replace("        if not ref or ref.lower() in _MOVING_REFS or not _CROSS_REF_RE.match(ref):",
                   "        if not ref:  # MUTANT", 1)
else:
    s2 = s
assert s2 != s, "anchor drift kind=%s" % kind
open(out_path, "w", encoding="utf-8").write(s2)
PY
}

# ── assert helper (exit + expect/forbid 토큰) ──
_assert() {  # <name> <exit> <exp_exit> <out> <expect_tok|""> <forbid_tok|"">
  local name="$1" e="$2" ee="$3" out="$4" et="$5" ft="$6" ok=1
  [ "$e" -eq "$ee" ] || ok=0
  if [ -n "$et" ]; then case "$out" in *"$et"*) : ;; *) ok=0;; esac; fi
  if [ -n "$ft" ]; then case "$out" in *"$ft"*) ok=0;; esac; fi
  if [ "$ok" -eq 1 ]; then
    echo "OK PASS: $name (exit $e)"; PASS=$((PASS+1))
  else
    echo "X FAIL: $name — expected exit=$ee expect='$et' forbid='$ft', got exit=$e"
    echo "  output: $out"; FAIL=$((FAIL+1))
  fi
}

echo "═══════════════════════════════════════════════════════════════════════════"
echo " CFP-2700 G5: infra cross-repo drift — discriminating self-test (.sh)"
echo "═══════════════════════════════════════════════════════════════════════════"
echo

# ── 3-way (AC-21) ──
echo "── 3-way (AC-21): (a) content-mismatch / (b) 전파 / (c) token 부재 ──"
_t=$(mktemp -d); _mk_repo "$_t" "$REF"; _mk_mock "$_t/_mock" "$REF" content "$FOREIGN_MISMATCH"
_o=$(_run "$SSOT_PY" "$_t" tkn "$_t/_mock" -); _e=$?
_assert "(a) content-mismatch → fail-closed exit 1 + DRIFT" "$_e" 1 "$_o" \
  "CROSS-REPO DRIFT (content-mismatch)" "propagated=1"
rm -rf "$_t"

_t=$(mktemp -d); _mk_repo "$_t" "$REF"; _mk_mock "$_t/_mock" "$REF" content "$FOREIGN_PROPAGATED"
_o=$(_run "$SSOT_PY" "$_t" tkn "$_t/_mock" -); _e=$?
_assert "(b) 전파 fixture → PASS exit 0 + OK" "$_e" 0 "$_o" "CROSS-REPO OK" ""
rm -rf "$_t"

_t=$(mktemp -d); _mk_repo "$_t" "$REF"; _mk_mock "$_t/_mock" "$REF" content "$FOREIGN_PROPAGATED"
_o=$(_run "$SSOT_PY" "$_t" - "$_t/_mock" -); _e=$?
_assert "(c) token 부재 → degraded-FAIL exit 3" "$_e" 3 "$_o" "CROSS-REPO DEGRADED-FAIL" ""
rm -rf "$_t"

_t=$(mktemp -d); _mk_repo "$_t" "$REF"; _mk_mock "$_t/_mock" "$REF" content "$FOREIGN_PROPAGATED"
_mkmutant token_check_off "$_t/mutant.py"
_o=$(_run "$_t/mutant.py" "$_t" - "$_t/_mock" -); _e=$?
# RED-flip: degraded 체크 무력화 → token 부재인데 대조 진행 = exit 3 아님.
_assert "(c) MK token_check_off → degraded 우회(exit 3 아님) RED" "$([ "$_e" -ne 3 ] && echo 0 || echo 9)" 0 \
  "$_o" "" "DEGRADED-FAIL"
rm -rf "$_t"
echo

# ── t1 transient fail-open + Issue 발행 ──
echo "── t1: transient(503/timeout) → fail-open + WARN + Issue 발행 (미발행 mutant=RED) ──"
_t=$(mktemp -d); _mk_repo "$_t" "$REF"; _mk_mock "$_t/_mock" "$REF" status "503"; _sink="$_t/issues.jsonl"
_o=$(_run "$SSOT_PY" "$_t" tkn "$_t/_mock" "$_sink"); _e=$?
_ok=1
[ "$_e" -eq 0 ] || _ok=0
case "$_o" in *"CROSS-REPO TRANSIENT (fail-open)"*) : ;; *) _ok=0;; esac
case "$_o" in *"transient_failopen=1"*) : ;; *) _ok=0;; esac
[ -s "$_sink" ] || _ok=0
if [ "$_ok" -eq 1 ]; then echo "OK PASS: t1 transient → fail-open exit 0 + Issue sink 발행"; PASS=$((PASS+1));
else echo "X FAIL: t1 — exit=$_e sink=$([ -s "$_sink" ] && echo nonempty || echo empty)"; echo "  $_o"; FAIL=$((FAIL+1)); fi
rm -rf "$_t"

_t=$(mktemp -d); _mk_repo "$_t" "$REF"; _mk_mock "$_t/_mock" "$REF" status "timeout"; _sink="$_t/issues.jsonl"
_mkmutant issue_publish_off "$_t/mutant.py"
_o=$(_run "$_t/mutant.py" "$_t" tkn "$_t/_mock" "$_sink"); _e=$?
# RED-flip: 발행 seam 무력화 → transient 는 여전히 exit 0 이나 audit trail(sink) 소실.
if [ ! -s "$_sink" ]; then echo "OK PASS: t1 MK issue_publish_off → sink 비어 audit trail 소실(RED-flip)"; PASS=$((PASS+1));
else echo "X FAIL: t1 MK issue_publish_off — sink 이 비어야 kill 성립 (내용=$(cat "$_sink"))"; FAIL=$((FAIL+1)); fi
rm -rf "$_t"
echo

# ── t2 content-mismatch ≠ transient (최중요) ──
echo "── t2: content-mismatch → transient 로 분류 안 됨 (오분류 mutant=최중요 RED) ──"
_t=$(mktemp -d); _mk_repo "$_t" "$REF"; _mk_mock "$_t/_mock" "$REF" content "$FOREIGN_MISMATCH"; _sink="$_t/issues.jsonl"
_o=$(_run "$SSOT_PY" "$_t" tkn "$_t/_mock" "$_sink"); _e=$?
_ok=1
[ "$_e" -eq 1 ] || _ok=0
case "$_o" in *"transient_failopen=0"*) : ;; *) _ok=0;; esac
[ ! -s "$_sink" ] || _ok=0   # content-mismatch 에 Issue 발행 = 오분류
if [ "$_ok" -eq 1 ]; then echo "OK PASS: t2 content-mismatch → exit 1 + transient_failopen=0 + Issue 미발행"; PASS=$((PASS+1));
else echo "X FAIL: t2 — exit=$_e (expect 1) sink=$([ -s "$_sink" ] && echo nonempty || echo empty)"; echo "  $_o"; FAIL=$((FAIL+1)); fi
rm -rf "$_t"

_t=$(mktemp -d); _mk_repo "$_t" "$REF"; _mk_mock "$_t/_mock" "$REF" content "$FOREIGN_MISMATCH"
_mkmutant mismatch_as_transient "$_t/mutant.py"
_o=$(_run "$_t/mutant.py" "$_t" tkn "$_t/_mock" -); _e=$?
# RED-flip(최중요): drift→transient 오분류 → verdict fail-closed(1) → fail-open(0), census 오계수.
_assert "t2 MK mismatch_as_transient → fail-open(exit 0) + transient_failopen=1 (RED-flip)" "$_e" 0 "$_o" \
  "transient_failopen=1" "content_mismatch=1"
rm -rf "$_t"
echo

# ── ref-pin (moving HEAD 거부 + idempotent) ──
echo "── ref-pin: moving HEAD 거부(hard-fail) + MK refpin_off + idempotent ──"
_t=$(mktemp -d); _mk_repo "$_t" "main"; _mk_mock "$_t/_mock" "main" content "$FOREIGN_PROPAGATED"
_o=$(_run "$SSOT_PY" "$_t" tkn "$_t/_mock" -); _e=$?
_assert "ref-pin moving HEAD(main) → hard-fail exit 1" "$_e" 1 "$_o" "moving HEAD 금지" ""
_mkmutant refpin_off "$_t/mutant.py"
_o=$(_run "$_t/mutant.py" "$_t" tkn "$_t/_mock" -); _e=$?
# RED-flip: moving-HEAD 거부 무력화 → main 수용 → 전파 대조 진행 = exit 0.
_assert "ref-pin MK refpin_off → moving HEAD 수용(exit 0) RED" "$_e" 0 "$_o" "" "moving HEAD 금지"
rm -rf "$_t"

_t=$(mktemp -d); _mk_repo "$_t" "$REF"; _mk_mock "$_t/_mock" "$REF" content "$FOREIGN_PROPAGATED"
_o1=$(_run "$SSOT_PY" "$_t" tkn "$_t/_mock" -); _e1=$?
_o2=$(_run "$SSOT_PY" "$_t" tkn "$_t/_mock" -); _e2=$?
if [ "$_e1" -eq 0 ] && [ "$_e2" -eq 0 ] && [ "$_o1" = "$_o2" ]; then
  echo "OK PASS: ref-pin idempotent — pinned ref 2-run byte-identical ∧ exit 0=0"; PASS=$((PASS+1))
else
  echo "X FAIL: ref-pin idempotent — e1=$_e1 e2=$_e2 out-identical=$([ "$_o1" = "$_o2" ] && echo Y || echo N)"; FAIL=$((FAIL+1))
fi
rm -rf "$_t"
echo

# ── 403/404 = resp.ok 후 fail-closed (transient 아님) + namespace spoof ──
echo "── 403/404 fail-closed (transient 아님) + namespace spoof hard-fail ──"
_t=$(mktemp -d); _mk_repo "$_t" "$REF"; _mk_mock "$_t/_mock" "$REF" status "not_found"; _sink="$_t/issues.jsonl"
_o=$(_run "$SSOT_PY" "$_t" tkn "$_t/_mock" "$_sink"); _e=$?
_ok=1
[ "$_e" -eq 1 ] || _ok=0
case "$_o" in *"404 not-found"*) : ;; *) _ok=0;; esac
case "$_o" in *"transient_failopen=0"*) : ;; *) _ok=0;; esac
[ ! -s "$_sink" ] || _ok=0
if [ "$_ok" -eq 1 ]; then echo "OK PASS: 404 → fail-closed exit 1 + transient_failopen=0 + Issue 미발행"; PASS=$((PASS+1));
else echo "X FAIL: 404 — exit=$_e"; echo "  $_o"; FAIL=$((FAIL+1)); fi
rm -rf "$_t"

_t=$(mktemp -d); _mk_repo "$_t" "$REF"; _mk_mock "$_t/_mock" "$REF" status "403"
_o=$(_run "$SSOT_PY" "$_t" tkn "$_t/_mock" -); _e=$?
_assert "403 → fail-closed exit 1 (transient 아님)" "$_e" 1 "$_o" "403/401 forbidden" "transient_failopen=1"
rm -rf "$_t"

_t=$(mktemp -d)
mkdir -p "$_t/.claude/_overlay"
cat > "$_t/.claude/_overlay/project.yaml" <<EOF
infra_resources:
  resources:
    - id: raw-nas
      namespace: ../evil
      canonical_env: $CANON
      cross_repo_ref: $REF
      cross_repo_path: $FPATH
      aliases:
        accepted: []
EOF
_o=$(_run "$SSOT_PY" "$_t" tkn - -); _e=$?
_assert "namespace spoof(../evil) → hard-fail exit 1" "$_e" 1 "$_o" "namespace 형식 위반" ""
rm -rf "$_t"
echo

# ── secret-masking (§7.3) ──
echo "── secret-masking (§7.3): sentinel PAT 값이 stdout·Issue sink 미출력 ──"
_t=$(mktemp -d); _mk_repo "$_t" "$REF"; _mk_mock "$_t/_mock" "$REF" status "503"; _sink="$_t/issues.jsonl"
_o=$(_run "$SSOT_PY" "$_t" "$SENTINEL" "$_t/_mock" "$_sink"); _e=$?
_sink_txt=""; [ -f "$_sink" ] && _sink_txt=$(cat "$_sink")
_ok=1
case "$_o" in *"CROSS-REPO"*) : ;; *) _ok=0;; esac          # 출력 캡처 load-bearing (빈출력 false-pass 방지)
case "$_o" in *"$SENTINEL"*) _ok=0;; esac                   # stdout 누출 금지
case "$_sink_txt" in *"$SENTINEL"*) _ok=0;; esac            # Issue sink 누출 금지
if [ "$_ok" -eq 1 ]; then echo "OK PASS: secret-masking — sentinel PAT 값 stdout·sink 미출력(§7.3)"; PASS=$((PASS+1));
else echo "X FAIL: secret-masking — sentinel 누출 (out 또는 sink)"; echo "  out: $_o"; FAIL=$((FAIL+1)); fi
rm -rf "$_t"
echo

# ── vacuous (namespace 자원 0 = wrapper-self 정상) ──
echo "── vacuous: namespace 자원 0 → PASS exit 0 (I-5 consumer 채택-bound) ──"
_t=$(mktemp -d); _mk_repo "$_t" "$REF" 0
_o=$(_run "$SSOT_PY" "$_t" tkn - -); _e=$?
_assert "vacuous(namespace 0) → PASS exit 0" "$_e" 0 "$_o" "CROSS-REPO PASS (vacuous)" ""
rm -rf "$_t"
echo

echo "═══════════════════════════════════════════════════════════════════════════"
echo " Test Summary"
echo "═══════════════════════════════════════════════════════════════════════════"
echo "PASS: $PASS"
echo "FAIL: $FAIL"
if [ "$FAIL" -eq 0 ]; then
  echo "OK All $PASS cases pass — 3-way(AC-21) + t1/t2 normative + ref-pin(idempotent/moving-HEAD) + 403/404 + spoof + secret-masking + vacuous, mutation-kill 결박"
  exit 0
else
  echo "X $FAIL case(s) failed"
  exit 1
fi
