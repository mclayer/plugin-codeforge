#!/usr/bin/env bash
# scripts/check-plugin-version-bump-self.sh — ADR-037 Amendment 2 Arc A v2 게이트 (wrapper-self)
#
# CFP-2310 S2 (#2312) carrier — ADR-037 §결정 5 forward-only deferred self-application 실현.
# Arc A 전면 v2: commit_signal + diff_signal(surface-table) + coupling_signal(T1/T2/T3) 의
# normalization-before-max → β lenient 비대칭(actual ≥ expected) 검사 → 9-plugin per-scope 독립
# 평가 + actual_bump=major 시 9-plugin MAJOR atomic cross-check.
#
# 설계 SSOT: archive/adr/ADR-037-plugin-version-bump-rule.md Amendment 2 (결정 A2-1~A2-9).
# v1 재사용: templates/github-workflows/check-plugin-version-bump.yml (commit_signal 로직 + β 비대칭 기반).
#
# ──────────────────────────── 동작 모드 ────────────────────────────
#   (1) production CI mode  : --base-sha <SHA> --head-sha <SHA>
#         PR base..HEAD 의 git log(commit_signal) + git diff(diff_signal/coupling) + plugin.json
#         before/after(actual_bump) 를 실측해 평가. exit 0 항상(warning-first, A2-7) —
#         위반은 ::warning:: 으로 보고. (workflow 가 non-blocking job 으로 wrap)
#   (2) self-test mode      : --self-test
#         scripts/test-fixtures/version-bump-self/ 의 합성 fixture 를 평가해 expected verdict
#         (PASS/FAIL) 과 cross-check. RED→GREEN proof. discriminating 검증분기 — exit 1 시 실패.
#   (3) eval mode (fixture) : --eval --changed-files <file> --commit-msgs <file> \
#                                    --bump-spec <file>
#         단위 평가 진입점(self-test 가 내부 호출). stdin/file 로 합성 입력을 받아 verdict 산출.
#         production 과 동일 핵심 로직(compute_verdict)을 공유 — dead-suite 회피, 실 CI 실행.
#
# Exit codes:
#   production mode : 0 항상 (warning-first — A2-7 초기 tier=warning, non-blocking)
#   self-test mode  : 0 = 모든 fixture verdict 일치 / 1 = 불일치(RED→GREEN proof 깨짐)
#   eval mode       : 평가 verdict 를 stdout 마지막 줄 "VERDICT=<PASS|FAIL>" 로 출력 (exit 0)
#   2               : usage / 환경 오류 (fail-loud)
#
# Conventional Commits + ADR-037 §결정 1~5 / Amendment 2 §결정 A2-1~A2-9 정합.

set -uo pipefail

# Windows cp949 회피 — UTF-8 강제 (CI 는 ubuntu 라 무영향, 로컬 자가검증 보호)
export LC_ALL="${LC_ALL:-C.UTF-8}" 2>/dev/null || true

# ──────────────────────────── 0. roster (A2-9 — 디렉터리 enumeration authoritative) ────────────────────────────
# 9-plugin roster = {codeforge}(wrapper root) ∪ {plugins/codeforge-*/ 디렉터리}.
# TOPOLOGICAL_ORDER(walk_plan.py) 비의존 — 별 lifecycle Python 상수 결합 금지 (A2-9 decoupling 의무).
WRAPPER_NAME="codeforge"

discover_roster() {
  # echo: wrapper plugin name + 각 lane plugin name (디렉터리 실측)
  local root="${1:-.}"
  echo "$WRAPPER_NAME"
  local d
  for d in "$root"/plugins/codeforge-*/; do
    [ -d "$d" ] || continue
    # plugin.json name 우선, 없으면 디렉터리명.
    # tr -d '\r': Windows/MSYS 에서 jq 출력 trailing CR 제거 — roster name 이
    #   actual_bump map key 와 byte-identical 하도록 보장 (A2-9 cross-check key lookup 정합).
    local pj="$d.claude-plugin/plugin.json"
    if [ -f "$pj" ]; then
      { jq -r '.name' "$pj" 2>/dev/null || basename "$d"; } | tr -d '\r'
    else
      basename "$d" | tr -d '\r'
    fi
  done
}

# ──────────────────────────── 1. rank 유틸 (β 비대칭용) ────────────────────────────
rank() {
  case "$1" in
    none) echo 0 ;;
    patch) echo 1 ;;
    minor) echo 2 ;;
    major) echo 3 ;;
    downgrade) echo -1 ;;
    *) echo 0 ;;
  esac
}

# rank int → 이름 (max 결과 역변환)
rank_name() {
  case "$1" in
    0) echo none ;;
    1) echo patch ;;
    2) echo minor ;;
    3) echo major ;;
    *) echo none ;;
  esac
}

# ──────────────────────────── 1b. changed-files line 파서 (F-3 입력 guard) ────────────────────────────
# 입력: 단일 line ("<status>\t<path>") → CR strip + 형식 검증.
# 출력(전역): PARSED_STATUS / PARSED_PATH. 반환: 0=유효 / 1=skip(빈 line·TAB 부재·형식불량).
#   blank / TAB 없는 line → cut -f2- 가 전체 line 을 path 로 오인(허위 wrapper scope) 하는 것을 차단.
#   fail-closed 방향 보존 — guard 는 형식 불량 line 만 skip (정상 line 은 그대로 통과).
PARSED_STATUS=""
PARSED_PATH=""
parse_diff_line() {
  local raw="$1"
  raw="${raw%$'\r'}"                 # CRLF CR strip (parser CR 대칭)
  [ -n "$raw" ] || return 1          # 빈 line skip
  case "$raw" in
    *$'\t'*) : ;;                    # TAB 포함 = 유효 후보
    *) return 1 ;;                    # TAB 부재 = 형식불량 skip (cut -f2- garbage 차단)
  esac
  PARSED_STATUS="$(printf '%s' "$raw" | cut -f1)"
  PARSED_PATH="$(printf '%s' "$raw" | cut -f2-)"
  # status / path 둘 다 비공백이어야 유효
  [ -n "$PARSED_STATUS" ] || return 1
  [ -n "$PARSED_PATH" ]   || return 1
  return 0
}

# ──────────────────────────── 2. commit_signal (v1 재사용, Conventional Commits) ────────────────────────────
# 입력: 멀티라인 commit 메시지 문자열 → none/patch/minor/major
compute_commit_signal() {
  local msgs="$1"
  local signal="none"
  if echo "$msgs" | grep -qE '^(feat|fix|chore|refactor|docs|style|test|build|ci|perf)(\([^)]+\))?!:' \
     || echo "$msgs" | grep -qE '^BREAKING CHANGE:'; then
    signal="major"
  elif echo "$msgs" | grep -qE '^feat(\([^)]+\))?:'; then
    signal="minor"
  elif echo "$msgs" | grep -qE '^(fix|docs|chore|style|refactor|test|build|ci|perf)(\([^)]+\))?:'; then
    signal="patch"
  fi
  echo "$signal"
}

# ──────────────────────────── 3. 경로 귀속 SSOT (A2-3 — closed mapping + fail-closed-unknown) ────────────────────────────
# 입력: 단일 변경 파일 경로 → 귀속 결과 토큰:
#   "wrapper"          = wrapper root surface 귀속
#   "lane:<name>"      = 해당 lane plugin 귀속
#   "exempt"           = closed exempt 표 등재(비귀속)
# unmapped(둘 다 미매칭) = fail-closed = "wrapper" (보수 귀속, A2-3 deterministic 단일 규칙).
#
# A2-3 귀속 표 + closed exempt 표 + F-D5 mirror 쌍 규칙을 deterministic 단일 outcome 으로 적용.
classify_path() {
  local f="$1"

  # (i) lane self-contained — plugins/<lane>/** → 해당 lane only (ADR-118 D3)
  if [[ "$f" == plugins/codeforge-*/* ]]; then
    # plugins/codeforge-design/agents/X.md → codeforge-design
    local lane
    lane="$(echo "$f" | sed -E 's#^plugins/(codeforge-[^/]+)/.*#\1#')"
    echo "lane:$lane"
    return
  fi

  # (ii) closed exempt 표 — archive/** = 비귀속 (ADR/legacy 동결, A2-3/A2-6 면제 근원)
  if [[ "$f" == archive/* ]]; then
    echo "exempt"
    return
  fi

  # (iii) F-D5 mirror 쌍 규칙 — .github/workflows/<x>.yml 중 templates/github-workflows/<x>.yml 짝 존재 시
  #       → wrapper 귀속(self-app copy = wrapper runtime workflow). 짝 없으면 repo-meta exempt.
  if [[ "$f" == .github/workflows/*.yml || "$f" == .github/workflows/*.yaml ]]; then
    local base mirror
    base="$(basename "$f")"
    mirror="templates/github-workflows/$base"
    if [ -f "$mirror" ]; then
      echo "wrapper"   # mirror 짝 존재 → wrapper 귀속 (F-D5 dedup 은 rank 산출 단계에서 처리)
    else
      echo "exempt"    # 짝 없는 self-app meta-only → repo-meta exempt (별 게이트)
    fi
    return
  fi

  # (iv) repo-meta exempt — marketplace.json / 기타 .github/** (workflows 외)
  if [[ "$f" == marketplace.json || "$f" == .claude-plugin/marketplace.json ]]; then
    echo "exempt"
    return
  fi
  if [[ "$f" == .github/* ]]; then
    echo "exempt"   # .github/workflows/ 는 위 (iii) 에서 처리됨 — 여기는 ISSUE_TEMPLATE 등 meta
    return
  fi

  # (v) wrapper root surface 귀속 표 (A2-3) — 명시 등재 경로
  case "$f" in
    .claude-plugin/plugin.json) echo "wrapper"; return ;;
    scripts/*)   echo "wrapper"; return ;;
    templates/*) echo "wrapper"; return ;;
    skills/*)    echo "wrapper"; return ;;
    hooks/*)     echo "wrapper"; return ;;
    commands/*)  echo "wrapper"; return ;;
    agents/*)    echo "wrapper"; return ;;   # ADR-009 invariant 로 실질 0개 (N/A)
    docs/*)      echo "wrapper"; return ;;
    CLAUDE.md)   echo "wrapper"; return ;;
  esac

  # (vi) unmapped → fail-closed = wrapper 귀속 보수 평가 (A2-3 단일 규칙, ADR-083 정합)
  echo "wrapper"
}

# ──────────────────────────── 4. diff_signal (A2-3/A2-4 2단 매핑 표) ────────────────────────────
# 입력: 변경 파일 목록(개행 구분, 각 줄 "<status>\t<path>" — status ∈ {A,M,D,...})
#       귀속 scope ("wrapper" 또는 "lane:<name>")
# 출력: 해당 scope 의 diff_signal rank 이름(none/patch/minor/major)
#
# 2단 매핑: glob(귀속 후) → §결정 1 surface category → bump rank.
# 기본 rank = 보수 하한(patch). 휴리스틱 상향:
#   - 파일 삭제(D) = surface (a)/(b)/(j) 류면 major (T2 동반)
#   - 신규 파일(A) = surface (a)/(b)/(c)/(d)/(j) 류면 minor (추가)
#   - 기존 edit(M) = patch (minor edit)
# mirror 쌍 dedup (F-D5): templates/github-workflows/<x>.yml ↔ .github/workflows/<x>.yml
#   동일 논리 파일은 templates 쪽을 SSOT 로 1회만 rank 가산(.github 쪽 중복 가산 0).
compute_diff_signal_for_scope() {
  local scope="$1"      # "wrapper" 또는 "lane:<name>"
  local files_blob="$2" # "<status>\t<path>" 줄들
  local root="${3:-.}"

  local prefix=""
  if [[ "$scope" == lane:* ]]; then
    local lane="${scope#lane:}"
    prefix="plugins/$lane/"
  fi

  local max_rank=0
  # mirror dedup tracking: 이미 카운트한 templates/github-workflows basename 집합.
  # F-6 note: rank 산출이 max-accumulator 라 동일 rank 중복 가산은 idempotent (결과 불변) —
  #   dedup 의 실효는 "mirror 쌍이 서로 다른 surface category 로 잘못 이중 분류되는 것" 차단
  #   (F-D5 SSOT 1회 평가 계약 보존). 본 self-test scope 에선 결과 동등하나 계약 문서화 목적 유지.
  local -A seen_mirror_base=()

  local line status path rel
  while IFS= read -r line; do
    parse_diff_line "$line" || continue   # F-3 입력 guard (빈/TAB부재/CR line skip)
    status="$PARSED_STATUS"
    path="$PARSED_PATH"

    # 이 scope 에 귀속되는 파일만 평가
    local pclass
    pclass="$(classify_path "$path")"
    if [ "$scope" = "wrapper" ]; then
      [ "$pclass" = "wrapper" ] || continue
      rel="$path"
    else
      [ "$pclass" = "$scope" ] || continue
      rel="${path#"$prefix"}"   # lane prefix 제거 → wrapper-relative glob 동형 적용
    fi

    # F-D5 mirror dedup: .github/workflows/<x>.yml 이 templates/github-workflows/<x>.yml 짝이면
    #   templates 쪽 surface rank((d) Template) 를 SSOT 로 1회만 가산.
    if [[ "$path" == .github/workflows/*.yml || "$path" == .github/workflows/*.yaml ]]; then
      local b="$(basename "$path")"
      if [ -f "$root/templates/github-workflows/$b" ]; then
        # templates 짝 존재 → 이 .github 파일은 mirror. templates 쪽이 같은 PR 에 있으면
        # 거기서 카운트되므로 .github 쪽은 skip. templates 쪽이 없으면(자기 self-app만 변경)
        # 여기서 1회 (d) Template rank 로 카운트하되 seen 마킹.
        if [ -n "${seen_mirror_base[$b]:-}" ]; then
          continue
        fi
        seen_mirror_base[$b]=1
        # (d) Template surface, 기본 patch — workflow 신설(A)=minor / 삭제(D)=major
        local r=1
        [ "$status" = "A" ] && r=2
        [ "$status" = "D" ] && r=3
        [ "$r" -gt "$max_rank" ] && max_rank="$r"
        continue
      fi
    fi
    # templates/github-workflows/<x>.yml 쪽도 mirror dedup 마킹 (짝 .github 가 같은 PR 에 와도 중복 0)
    if [[ "$rel" == templates/github-workflows/*.yml || "$rel" == templates/github-workflows/*.yaml ]]; then
      local b2="$(basename "$rel")"
      seen_mirror_base[$b2]=1
    fi

    # 2단 매핑 표 — glob → surface category → rank (보수 하한 patch=1)
    local r=1
    case "$rel" in
      agents/*)
        # (a) Agent file — 추가=minor / 삭제=major / edit=patch (F-6: 중복 agents/*.md glob 제거)
        case "$status" in A) r=2 ;; D) r=3 ;; *) r=1 ;; esac
        ;;
      skills/*)
        # (b) Skill file
        case "$status" in A) r=2 ;; D) r=3 ;; *) r=1 ;; esac
        ;;
      hooks/*)
        # (c) Hook script — 보수: 추가=minor / 삭제·break=major / config-only edit=patch
        case "$status" in A) r=2 ;; D) r=3 ;; *) r=1 ;; esac
        ;;
      templates/github-workflows/*|templates/*Form*|templates/*form*)
        # (d) Template(workflow/Form) — 추가=minor / 삭제=major / edit=patch
        case "$status" in A) r=2 ;; D) r=3 ;; *) r=1 ;; esac
        ;;
      templates/*)
        # (d) 파생 template — 보수 patch (comments only 기본), 신규=minor
        case "$status" in A) r=2 ;; *) r=1 ;; esac
        ;;
      CLAUDE.md)
        # (g) CLAUDE.md SSOT — additive=minor / invalidate=major / typo=patch. 보수 patch.
        r=1
        ;;
      docs/*)
        # (g) 파생 문서 — 보수 patch
        r=1
        ;;
      commands/*)
        # (j) Slash command — 추가=minor / 삭제=major / edit=patch
        case "$status" in A) r=2 ;; D) r=3 ;; *) r=1 ;; esac
        ;;
      scripts/bootstrap-*.sh)
        # (i) Bootstrap script — 선택 setup=minor / break=major / comments=patch. 보수 patch.
        case "$status" in A) r=2 ;; *) r=1 ;; esac
        ;;
      scripts/*)
        # (i) 파생 스크립트 — behavior 변경 author 판정. 신규=minor / edit=patch.
        case "$status" in A) r=2 ;; *) r=1 ;; esac
        ;;
      .claude-plugin/plugin.json)
        # (l) plugin.json 자체 = actual_bump source, diff_signal 에서는 비가산 (version 변경=bump 자체)
        r=0
        ;;
      *)
        # 귀속됐으나 표 미열거 = 보수 patch
        r=1
        ;;
    esac
    [ "$r" -gt "$max_rank" ] && max_rank="$r"
  done <<< "$files_blob"

  rank_name "$max_rank"
}

# ──────────────────────────── 5. coupling_signal (A2-4 — T1/T2/T3, wrapper PR 만) ────────────────────────────
# in-PR coupling only (A2-4 escape hatch): lane surface 변경 + 동일 PR 에 wrapper root surface 변경 동반 시
#   T1/T2 → wrapper MAJOR. lane-only PR(wrapper root 0 변경) = coupling 0.
# T3(family invariant ADR supersede) = status:Superseded 전환만 발동(additive amendment 미발동).
# 입력: files_blob, wrapper_touched(0/1)
# 출력: none / major (coupling 은 MAJOR 전파만)
compute_coupling_signal() {
  local files_blob="$1"
  local wrapper_touched="$2"  # 1 = 동일 PR 에 wrapper root surface 변경 동반
  local root="${3:-.}"

  # in-PR coupling: wrapper root surface 무변경(lane-only PR) → coupling 0 (escape hatch)
  if [ "$wrapper_touched" != "1" ]; then
    echo "none"
    return
  fi

  local line status path
  while IFS= read -r line; do
    parse_diff_line "$line" || continue   # F-3 입력 guard
    status="$PARSED_STATUS"
    path="$PARSED_PATH"

    # T2 agent topology: 어느 lane plugins/<lane>/agents/*.md 삭제(D) 또는 역할 재정의
    #   (휴리스틱: 삭제 = topology 변경. 역할 재정의 의미판정은 author override 경로)
    if [[ "$path" == plugins/codeforge-*/agents/* && "$status" == "D" ]]; then
      echo "major"; return
    fi

    # T3 family invariant ADR supersede: family invariant ADR 의 status:Superseded 전환.
    #   archive/adr/ADR-{009,016,024,008,037}-*.md 가 변경 + status:Superseded 포함 시.
    #   (additive amendment ≠ supersede — A2-4 boundary)
    if [[ "$path" == archive/adr/ADR-009-* || "$path" == archive/adr/ADR-016-* \
       || "$path" == archive/adr/ADR-024-* || "$path" == archive/adr/ADR-008-* \
       || "$path" == archive/adr/ADR-037-* ]]; then
      if [ -f "$root/$path" ] && grep -qE '^status:\s*Superseded' "$root/$path" 2>/dev/null; then
        echo "major"; return
      fi
    fi
    # T1 contract MAJOR: plugins/*/ contract 파일 MAJOR — 의미판정 한계상 보수적으로
    #   contract 파일 삭제(D)만 휴리스틱 major (정밀 ADR-008 MAJOR 판정 = author override).
    if [[ "$path" == plugins/codeforge-*/*contract* && "$status" == "D" ]]; then
      echo "major"; return
    fi
  done <<< "$files_blob"

  echo "none"
}

# ──────────────────────────── 6. compute_verdict (핵심 — production/eval/self-test 공유) ────────────────────────────
# 입력(환경/인자):
#   files_blob       : "<status>\t<path>" 줄들 (변경 파일)
#   commit_msgs      : 멀티라인 commit 메시지
#   bump_spec        : "<plugin-name>:<base_v>-><head_v>" 줄들 (각 plugin 의 actual_bump 산출 입력)
#   root             : repo root (default .)
# 출력: stdout 로 per-scope 평가 로그 + 마지막 줄 "VERDICT=<PASS|FAIL>"
#   verdict_reason 줄들은 ::warning:: 로 production 에서 표면화.
compute_verdict() {
  local files_blob="$1"
  local commit_msgs="$2"
  local bump_spec="$3"
  local root="${4:-.}"

  local overall="PASS"

  # actual_bump 파싱: plugin-name → bump 이름 map
  local -A actual_bump=()
  local -A base_v=()
  local -A head_v=()
  local bline pname spec bv hv
  while IFS= read -r bline; do
    bline="${bline%$'\r'}"      # F-2: CRLF interior line CR strip (roster tr -d '\r' 와 parallel-anchor 대칭)
    [ -n "$bline" ] || continue
    pname="${bline%%:*}"
    spec="${bline#*:}"          # base_v->head_v
    bv="${spec%%->*}"
    hv="${spec##*->}"
    # F-2: 버전 값 자체에 잔존할 수 있는 CR 방어 제거 (interior field → (( )) syntax error 방지)
    bv="${bv%$'\r'}"; bv="${bv//$'\r'/}"
    hv="${hv%$'\r'}"; hv="${hv//$'\r'/}"
    base_v["$pname"]="$bv"
    head_v["$pname"]="$hv"
    if [ -z "$bv" ] || [ "$bv" = "null" ]; then
      actual_bump["$pname"]="none"   # 신규 plugin
    elif [ "$bv" = "$hv" ]; then
      actual_bump["$pname"]="none"
    else
      local bM bm bp hM hm hp
      IFS='.' read -r bM bm bp <<< "$bv"
      IFS='.' read -r hM hm hp <<< "$hv"
      if (( hM > bM )); then actual_bump["$pname"]="major"
      elif (( hM < bM )); then actual_bump["$pname"]="downgrade"
      elif (( hm > bm )); then actual_bump["$pname"]="minor"
      elif (( hm < bm )); then actual_bump["$pname"]="downgrade"
      elif (( hp > bp )); then actual_bump["$pname"]="patch"
      elif (( hp < bp )); then actual_bump["$pname"]="downgrade"
      else actual_bump["$pname"]="none"; fi
    fi
  done <<< "$bump_spec"

  # wrapper root surface touch 여부 (coupling in-PR 판정 + commit normalization 입력)
  local wrapper_touched=0
  local any_attributed_surface=0   # A2-6 no-surface-touch: 어느 scope 든 귀속 surface 1+ 있으면 1
  local line path pclass
  while IFS= read -r line; do
    parse_diff_line "$line" || continue   # F-3 입력 guard
    path="$PARSED_PATH"
    pclass="$(classify_path "$path")"
    if [ "$pclass" = "wrapper" ]; then
      wrapper_touched=1
      any_attributed_surface=1
    elif [[ "$pclass" == lane:* ]]; then
      any_attributed_surface=1
    fi
    # exempt → no surface
  done <<< "$files_blob"

  # ── commit_signal + A2-6 normalization-before-max ──
  local commit_raw
  commit_raw="$(compute_commit_signal "$commit_msgs")"
  local commit_norm="$commit_raw"
  if [ "$any_attributed_surface" -eq 0 ]; then
    # no-surface-touch exemption: 귀속 surface 0개 → commit_signal none 강등 (A2-6 규칙 2)
    commit_norm="none"
  fi
  echo "commit_signal: raw=$commit_raw normalized=$commit_norm (any_attributed_surface=$any_attributed_surface)"

  # ── 평가 대상 scope 집합 (변경 파일이 귀속된 scope만) ──
  local -A scopes=()
  while IFS= read -r line; do
    parse_diff_line "$line" || continue   # F-3 입력 guard
    path="$PARSED_PATH"
    pclass="$(classify_path "$path")"
    if [ "$pclass" = "wrapper" ]; then scopes["wrapper"]=1
    elif [[ "$pclass" == lane:* ]]; then scopes["$pclass"]=1; fi
  done <<< "$files_blob"

  # coupling_signal (wrapper PR 만)
  local coupling
  coupling="$(compute_coupling_signal "$files_blob" "$wrapper_touched" "$root")"
  echo "coupling_signal: $coupling (wrapper_touched=$wrapper_touched)"

  # ── per-scope 독립 평가 (A2-2) ──
  local scope sig_diff exp_rank c_rank d_rank cpl_rank a_rank actual pname_for_scope expected
  for scope in "${!scopes[@]}"; do
    if [ "$scope" = "wrapper" ]; then
      pname_for_scope="$WRAPPER_NAME"
    else
      pname_for_scope="${scope#lane:}"
    fi

    sig_diff="$(compute_diff_signal_for_scope "$scope" "$files_blob" "$root")"

    # expected = max(commit_norm, diff_signal, coupling[wrapper만])
    c_rank="$(rank "$commit_norm")"
    d_rank="$(rank "$sig_diff")"
    if [ "$scope" = "wrapper" ]; then
      cpl_rank="$(rank "$coupling")"
    else
      cpl_rank=0   # coupling 은 wrapper PR 만 (A2-4)
    fi
    exp_rank="$c_rank"
    [ "$d_rank" -gt "$exp_rank" ] && exp_rank="$d_rank"
    [ "$cpl_rank" -gt "$exp_rank" ] && exp_rank="$cpl_rank"
    expected="$(rank_name "$exp_rank")"

    actual="${actual_bump[$pname_for_scope]:-none}"
    a_rank="$(rank "$actual")"

    echo "  [scope=$scope plugin=$pname_for_scope] diff_signal=$sig_diff expected=$expected actual_bump=$actual (base=${base_v[$pname_for_scope]:-?} head=${head_v[$pname_for_scope]:-?})"

    # ── β lenient 비대칭 (A2-5) — '==' 아님 ──
    if [ "$actual" = "downgrade" ]; then
      echo "  ::violation:: [$pname_for_scope] version downgrade — forward-only 위반 (ADR-037 §결정 5)"
      overall="FAIL"
    elif [ "$a_rank" -ge "$exp_rank" ]; then
      : # PASS (over-bump 허용)
    else
      echo "  ::violation:: [$pname_for_scope] under-bump — expected '$expected'(rank $exp_rank) > actual '$actual'(rank $a_rank). bump 누락 (ADR-037 §결정 1 + A2-5)"
      overall="FAIL"
    fi
  done

  # ── A2-9 MAJOR atomic cross-check (actual_bump=major 감지 시 9-plugin 동시 MAJOR) ──
  local any_major=0
  local p
  for p in "${!actual_bump[@]}"; do
    [ "${actual_bump[$p]}" = "major" ] && any_major=1
  done
  if [ "$any_major" -eq 1 ]; then
    echo "MAJOR atomic cross-check (A2-9 / ADR-063 §결정 18-B) 발동:"
    local roster_list
    roster_list="$(discover_roster "$root")"
    local missing_major=""
    while IFS= read -r p; do
      p="${p%$'\r'}"   # 방어적 CR 제거 (roster key ↔ actual_bump map key byte 정합)
      [ -n "$p" ] || continue
      # actual_bump map 에 없거나 major 아니면 위반
      if [ "${actual_bump[$p]:-none}" != "major" ]; then
        missing_major="$missing_major $p"
      fi
    done <<< "$roster_list"
    if [ -n "$missing_major" ]; then
      echo "  ::violation:: MAJOR atomic 위반 — 다음 plugin 이 동시 MAJOR 미bump:$missing_major (ADR-063 §결정 18-B 9-plugin 동시 MAJOR atomic)"
      overall="FAIL"
    else
      echo "  MAJOR atomic OK — roster 전체 동시 MAJOR"
    fi
  fi

  echo "VERDICT=$overall"
}

# ──────────────────────────── 7. production CI 진입 ────────────────────────────
run_production() {
  local base_sha="$1" head_sha="$2" root="${3:-.}"

  if ! command -v jq >/dev/null 2>&1; then
    echo "::warning::jq 미설치 — version-bump-self 게이트 skip (non-blocking)"
    return 0
  fi

  # commit 메시지 수집
  local msgs
  msgs="$(git -C "$root" log --format='%s%n%b' "${base_sha}..${head_sha}" 2>/dev/null || echo "")"

  # 변경 파일 (status\tpath) — rename(R)/copy(C) 는 dst 만 취함
  local files_blob
  files_blob="$(git -C "$root" diff --name-status "${base_sha}" "${head_sha}" 2>/dev/null \
    | awk -F'\t' '{ if ($1 ~ /^R/ || $1 ~ /^C/) print substr($1,1,1) "\t" $3; else print $1 "\t" $2 }' || echo "")"

  # bump_spec — roster 각 plugin 의 plugin.json base→head version
  local bump_spec=""
  local roster_list p pj rel_pj bv hv
  roster_list="$(discover_roster "$root")"
  while IFS= read -r p; do
    p="${p%$'\r'}"   # 방어적 CR 제거 (Windows/MSYS roster name 정합)
    [ -n "$p" ] || continue
    if [ "$p" = "$WRAPPER_NAME" ]; then
      rel_pj=".claude-plugin/plugin.json"
    else
      rel_pj="plugins/$p/.claude-plugin/plugin.json"
    fi
    hv="$(jq -r '.version' "$root/$rel_pj" 2>/dev/null || echo "")"
    bv="$(git -C "$root" show "${base_sha}:${rel_pj}" 2>/dev/null | jq -r '.version' 2>/dev/null || echo "")"
    [ -z "$hv" ] && hv="$bv"
    bump_spec="${bump_spec}${p}:${bv}->${hv}"$'\n'
  done <<< "$roster_list"

  echo "=== ADR-037 Amendment 2 Arc A v2 version-bump self-check (warning-first, A2-7) ==="
  local out verdict
  out="$(compute_verdict "$files_blob" "$msgs" "$bump_spec" "$root")"
  echo "$out"
  verdict="$(echo "$out" | grep -E '^VERDICT=' | tail -1 | cut -d= -f2)"

  if [ "$verdict" = "FAIL" ]; then
    # warning-first (A2-7): 위반을 ::warning:: 으로 표면화하되 exit 0 (non-blocking)
    echo "$out" | grep '::violation::' | while IFS= read -r v; do
      echo "::warning::${v#*::violation:: }"
    done
    echo "::warning::version-bump-self 정합 위반 감지 (warning tier — non-blocking, ADR-037 A2-7). 승격 시 required context 전환 예정."
  else
    echo "::notice::version-bump-self 정합 OK"
  fi
  # A2-7 warning-first: production 은 항상 exit 0 (절대 branch protection required 추가 금지)
  return 0
}

# ──────────────────────────── 8. eval 진입 (fixture 단위 평가) ────────────────────────────
run_eval() {
  local changed_files_path="$1" commit_msgs_path="$2" bump_spec_path="$3" root="${4:-.}"
  local files_blob msgs bump_spec
  files_blob="$(cat "$changed_files_path" 2>/dev/null || echo "")"
  msgs="$(cat "$commit_msgs_path" 2>/dev/null || echo "")"
  bump_spec="$(cat "$bump_spec_path" 2>/dev/null || echo "")"
  compute_verdict "$files_blob" "$msgs" "$bump_spec" "$root"
}

# ──────────────────────────── 9. self-test 진입 (RED→GREEN proof) ────────────────────────────
# scripts/test-fixtures/version-bump-self/<case>/ 각 디렉터리:
#   changed-files     : "<status>\t<path>" 줄들
#   commit-msgs       : 멀티라인 commit 메시지
#   bump-spec         : "<plugin>:<base>-><head>" 줄들
#   expected-verdict  : "PASS" 또는 "FAIL" 1줄
# (self-test 는 companion test 스크립트 scripts/test-check-plugin-version-bump-self.sh 가 호출)

# ──────────────────────────── main ────────────────────────────
usage() {
  cat >&2 <<'USAGE'
Usage:
  check-plugin-version-bump-self.sh --base-sha <SHA> --head-sha <SHA> [--root <dir>]   # production CI
  check-plugin-version-bump-self.sh --eval --changed-files <f> --commit-msgs <f> --bump-spec <f> [--root <dir>]
USAGE
}

ROOT="."
MODE=""
BASE_SHA=""; HEAD_SHA=""
CHANGED_FILES=""; COMMIT_MSGS=""; BUMP_SPEC=""

while [ $# -gt 0 ]; do
  case "$1" in
    --base-sha) BASE_SHA="$2"; MODE="production"; shift 2 ;;
    --head-sha) HEAD_SHA="$2"; shift 2 ;;
    --eval) MODE="eval"; shift ;;
    --changed-files) CHANGED_FILES="$2"; shift 2 ;;
    --commit-msgs) COMMIT_MSGS="$2"; shift 2 ;;
    --bump-spec) BUMP_SPEC="$2"; shift 2 ;;
    --root) ROOT="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "::error::unknown arg: $1" >&2; usage; exit 2 ;;
  esac
done

case "$MODE" in
  production)
    if [ -z "$BASE_SHA" ] || [ -z "$HEAD_SHA" ]; then
      echo "::error::--base-sha + --head-sha required for production mode" >&2; exit 2
    fi
    run_production "$BASE_SHA" "$HEAD_SHA" "$ROOT"
    ;;
  eval)
    if [ -z "$CHANGED_FILES" ] || [ -z "$COMMIT_MSGS" ] || [ -z "$BUMP_SPEC" ]; then
      echo "::error::--eval requires --changed-files + --commit-msgs + --bump-spec" >&2; exit 2
    fi
    run_eval "$CHANGED_FILES" "$COMMIT_MSGS" "$BUMP_SPEC" "$ROOT"
    ;;
  *)
    usage; exit 2 ;;
esac
