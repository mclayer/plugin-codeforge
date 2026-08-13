#!/usr/bin/env bash
# CFP-2965 hook-chain latency decomposition driver (측정 전용 — repo 무수정)
# 사용: bash driver.sh <batch>   batch = setup | m2 | m1 | m3 | ghonce | integrity
set -u

REPO="/c/workspace/mclayer/plugin-codeforge"
REPO_W="C:/workspace/mclayer/plugin-codeforge"
RAW="$HOME/.claude/codeforge-scratch/cfp-2965-measure"
SANDBOX="$RAW/plugin-codeforge-sandbox"
SANDBOX_W="C:/Users/mccho/.claude/codeforge-scratch/cfp-2965-measure/plugin-codeforge-sandbox"
NOOP="$RAW/noop-cascade"

# 실원장 오염 회피: scope 휴리스틱(wrapper=basename에 plugin-codeforge 포함)을 만족하는
# sandbox 를 CLAUDE_PROJECT_DIR 로 지정 → full write 경로 실행 + 목적지 sandbox 격리.
export CLAUDE_PROJECT_DIR="$SANDBOX_W"
export CLAUDE_PLUGIN_ROOT="$REPO_W"
# bypass env 미설정 보장 (측정은 실경로)
unset BYPASS_CROSS_REPO_GH_SAFETY BYPASS_REPO_CONFINEMENT BYPASS_BRANCH_DELETE_MERGE_GATE \
      BYPASS_WORKTREE_LOCATION_GUARD BYPASS_CODEFORGE_BASH_DESCRIPTION_INJECT 2>/dev/null || true

PAY_SUB="$RAW/payload-sub.json"          # subagent 형 (agent_type 有, 한글 description)
PAY_SUB_ASCII="$RAW/payload-sub-ascii.json" # subagent 형 ASCII-only description
PAY_TOP="$RAW/payload-top.json"          # top-level 형 (agent_type 無)
PAY_POST="$RAW/payload-post.json"        # PostToolUse 형 (tool_response 有)
PAY_DEL="$RAW/payload-del.json"          # git push --delete 패턴 (gh 경로, 1회 전용)
PAY_GHW="$RAW/payload-ghwrite.json"      # gh write w/o --repo (block 경로 sanity 전용)

RUNHOOK_W="C:\\workspace\\mclayer\\plugin-codeforge\\hooks\\run-hook.cmd"
NOOPHOOK_W="C:\\Users\\mccho\\.claude\\codeforge-scratch\\cfp-2965-measure\\noop-cascade\\run-hook.cmd"

PRE_HOOKS=(cross-repo-gh-safety repo-confinement git-branch-delete-merge-gate worktree-location-guard pretooluse-bash-description-inject pretooluse-dev-process-capture)

now_us() { local t="${EPOCHREALTIME}"; printf '%s' "${t/./}"; }

loadsnap() {
  local lbl="$1"
  local cpu procs
  cpu=$(powershell.exe -NoProfile -Command "(Get-CimInstance Win32_Processor | Measure-Object -Property LoadPercentage -Average).Average" 2>/dev/null | tr -d '\r' | tail -1)
  procs=$(powershell.exe -NoProfile -Command "(Get-Process).Count" 2>/dev/null | tr -d '\r' | tail -1)
  echo "$(date -u +%H:%M:%SZ),$lbl,cpu_pct=$cpu,procs=$procs" >> "$RAW/m4-load.csv"
}

build_payloads() {
  local MARK
  MARK="CFP2965""LIVE""$(date +%s)"
  printf '%s' "$MARK" > "$RAW/marker.txt"
  cat > "$PAY_SUB" <<EOF
{"session_id":"cfp2965-measure","transcript_path":"C:/tmp/none.jsonl","cwd":"$REPO_W","hook_event_name":"PreToolUse","tool_name":"Bash","tool_input":{"command":"git -C $REPO_W status --porcelain # $MARK","description":"[DeveloperAgent] 08/13 21:40:00 - git status 확인 ($MARK)"},"agent_type":"DeveloperAgent"}
EOF
  cat > "$PAY_SUB_ASCII" <<EOF
{"session_id":"cfp2965-measure","transcript_path":"C:/tmp/none.jsonl","cwd":"$REPO_W","hook_event_name":"PreToolUse","tool_name":"Bash","tool_input":{"command":"git -C $REPO_W status --porcelain # $MARK","description":"[DeveloperAgent] 08/13 21:40:00 - check git status ($MARK)"},"agent_type":"DeveloperAgent"}
EOF
  cat > "$PAY_TOP" <<EOF
{"session_id":"cfp2965-measure","transcript_path":"C:/tmp/none.jsonl","cwd":"$REPO_W","hook_event_name":"PreToolUse","tool_name":"Bash","tool_input":{"command":"git -C $REPO_W status --porcelain # $MARK","description":"[Orchestrator] 08/13 21:40:00 - git status 확인 ($MARK)"}}
EOF
  cat > "$PAY_POST" <<EOF
{"session_id":"cfp2965-measure","transcript_path":"C:/tmp/none.jsonl","cwd":"$REPO_W","hook_event_name":"PostToolUse","tool_name":"Bash","tool_input":{"command":"git -C $REPO_W status --porcelain # $MARK","description":"[DeveloperAgent] 08/13 21:40:00 - git status 확인 ($MARK)"},"tool_response":{"stdout":" M docs/stories/CFP-2965.md\\n?? scripts/tmp-a.py\\n?? scripts/tmp-b.py\\n M hooks/hooks.json\\n M CLAUDE.md\\n $MARK","stderr":"","interrupted":false},"agent_type":"DeveloperAgent"}
EOF
  cat > "$PAY_DEL" <<EOF
{"session_id":"cfp2965-measure","transcript_path":"C:/tmp/none.jsonl","cwd":"$REPO_W","hook_event_name":"PreToolUse","tool_name":"Bash","tool_input":{"command":"git push origin --delete cfp-2965-nonexistent-measure-only-branch","description":"[DeveloperAgent] 08/13 21:40:00 - measure gh path ($MARK)"},"agent_type":"DeveloperAgent"}
EOF
  cat > "$PAY_GHW" <<EOF
{"session_id":"cfp2965-measure","transcript_path":"C:/tmp/none.jsonl","cwd":"$REPO_W","hook_event_name":"PreToolUse","tool_name":"Bash","tool_input":{"command":"gh pr comment 1 --body sanity-block-check","description":"sanity"},"agent_type":"DeveloperAgent"}
EOF
}

setup() {
  mkdir -p "$RAW" "$SANDBOX" "$NOOP"
  build_payloads
  cp "$REPO/hooks/run-hook.cmd" "$NOOP/run-hook.cmd"
  printf '#!/usr/bin/env bash\nexit 0\n' > "$NOOP/noop-hook"
  chmod +x "$NOOP/noop-hook" 2>/dev/null || true

  {
    echo "== CFP-2965 measurement context =="
    echo "utc_now=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "repo_head=$(git -C "$REPO" rev-parse HEAD 2>/dev/null)"
    echo "bash=$BASH_VERSION"
    echo "python3=$(command -v python3) $(python3 --version 2>&1)"
    echo "CLAUDE_PROJECT_DIR(sandbox)=$CLAUDE_PROJECT_DIR"
    echo "CLAUDE_PLUGIN_ROOT=$CLAUDE_PLUGIN_ROOT"
    powershell.exe -NoProfile -Command "(Get-CimInstance Win32_Processor).Name; 'logical_cpus=' + [Environment]::ProcessorCount" 2>/dev/null | tr -d '\r'
  } > "$RAW/context.txt"

  # 실원장 baseline (오염 0 검증용)
  {
    echo "== real ledger baseline $(date -u +%H:%M:%SZ) =="
    if [ -f "$REPO/.claude/ledger/dev-process-event.jsonl" ]; then
      echo "real_ledger_lines=$(wc -l < "$REPO/.claude/ledger/dev-process-event.jsonl")"
    else
      echo "real_ledger_lines=ABSENT"
    fi
    if [ -d "$REPO/.claude-work/dev-process" ]; then
      echo "real_blob_files=$(find "$REPO/.claude-work/dev-process" -type f | wc -l)"
    else
      echo "real_blob_files=ABSENT"
    fi
  } > "$RAW/integrity-baseline.txt"

  # ── sanity: 각 훅 1회 직접 실행 (rc + stdout 유무) ─────────────────────
  {
    echo "== sanity (direct arm, 1x each) =="
    # 한글 payload 에서 python -c json.load(sys.stdin) tool_name 추출이 동작하는지 (인코딩 판별)
    TN=$(printf '%s' "$(cat "$PAY_SUB")" | python3 -c '
import json, sys
try:
    print(json.load(sys.stdin).get("tool_name", ""), end="")
except Exception:
    pass
' 2>/dev/null || true)
    echo "pyc_toolname_extract_korean_payload=[${TN}]"
    TN2=$(printf '%s' "$(cat "$PAY_SUB_ASCII")" | python3 -c '
import json, sys
try:
    print(json.load(sys.stdin).get("tool_name", ""), end="")
except Exception:
    pass
' 2>/dev/null || true)
    echo "pyc_toolname_extract_ascii_payload=[${TN2}]"

    for h in "${PRE_HOOKS[@]}"; do
      out=$(bash "$REPO/hooks/$h" < "$PAY_SUB" 2>"$RAW/sanity-$h.stderr"); rc=$?
      echo "direct:$h rc=$rc stdout_bytes=${#out}"
      printf '%s' "$out" > "$RAW/sanity-$h.stdout"
    done
    out=$(bash "$REPO/hooks/posttooluse-dev-process-capture" < "$PAY_POST" 2>/dev/null); rc=$?
    echo "direct:posttooluse-dev-process-capture rc=$rc stdout_bytes=${#out}"

    # cascade 1회 (stdin passthrough 검증: 정상 payload rc=0)
    cmd //c "$RUNHOOK_W" cross-repo-gh-safety < "$PAY_SUB" >/dev/null 2>&1; echo "cascade:cross-repo-gh-safety(normal) rc=$?"
    # cascade block 경로 검증: gh write w/o --repo → rc=2 여야 stdin 이 cascade 를 관통함이 증명됨
    cmd //c "$RUNHOOK_W" cross-repo-gh-safety < "$PAY_GHW" >/dev/null 2>&1; echo "cascade:cross-repo-gh-safety(gh-write-no-repo) rc=$? (expect 2)"
    # noop cascade 1회
    cmd //c "$NOOPHOOK_W" noop-hook < "$PAY_SUB" >/dev/null 2>&1; echo "cascade:noop rc=$?"

    # sandbox ledger 생성 확인 (dev-process-capture 가 sandbox 로 썼는지)
    if [ -f "$SANDBOX/.claude/ledger/dev-process-event.jsonl" ]; then
      echo "sandbox_ledger_lines=$(wc -l < "$SANDBOX/.claude/ledger/dev-process-event.jsonl")"
    else
      echo "sandbox_ledger_lines=ABSENT(!)"
    fi
  } > "$RAW/sanity.txt" 2>&1
  echo "setup done"
}

timed() { # csv label iter payload cmd...
  local csv="$1" lbl="$2" it="$3" pay="$4"; shift 4
  local s e rc
  s=$(now_us)
  "$@" < "$pay" > /dev/null 2>&1
  rc=$?
  e=$(now_us)
  echo "$lbl,$it,$((e - s)),$rc" >> "$csv"
}

m2() {
  local CSV="$RAW/m2.csv" n=12
  : > "$CSV"
  loadsnap "m2-start"
  local i
  for i in $(seq 1 "$n"); do
    timed "$CSV" "py-cold" "$i" /dev/null python3 -c "pass"
    timed "$CSV" "bash-spawn" "$i" /dev/null bash -c ':'
    timed "$CSV" "cascade-noop" "$i" "$PAY_SUB" cmd //c "$NOOPHOOK_W" noop-hook
    # inject 내부 stage 분해
    timed "$CSV" "stage-pyc-toolname" "$i" "$PAY_SUB" python3 -c '
import json, sys
try:
    print(json.load(sys.stdin).get("tool_name", ""), end="")
except Exception:
    pass
'
    timed "$CSV" "stage-pyc-agenttype" "$i" "$PAY_SUB" python3 -c '
import json, sys
try:
    v = json.load(sys.stdin).get("agent_type", "")
    print(v if isinstance(v, str) else "", end="")
except Exception:
    pass
'
    timed "$CSV" "stage-kst-stamp" "$i" /dev/null bash "$REPO/scripts/kst-render-stamp.sh"
    timed "$CSV" "stage-checker-inject" "$i" "$RAW/payload-noprefix.json" python3 "$REPO/scripts/lib/check_spawn_description_prefix.py" --inject --subject DeveloperAgent --kst-stamp "08/13 21:40:00" --bypass-env BYPASS_CODEFORGE_BASH_DESCRIPTION_INJECT
  done
  loadsnap "m2-end"
  echo "m2 done: $(wc -l < "$CSV") rows"
}

m1() {
  local CSV="$RAW/m1.csv" n=12
  : > "$CSV"
  loadsnap "m1-start"
  local i h
  for i in $(seq 1 "$n"); do
    for h in "${PRE_HOOKS[@]}"; do
      timed "$CSV" "$h|cascade" "$i" "$PAY_SUB" cmd //c "$RUNHOOK_W" "$h"
      timed "$CSV" "$h|direct" "$i" "$PAY_SUB" bash "$REPO/hooks/$h"
      timed "$CSV" "$h|polyglot-bash" "$i" "$PAY_SUB" bash "$REPO/hooks/run-hook.cmd" "$h"
    done
    # PostToolUse 훅 (post payload)
    timed "$CSV" "posttooluse-dev-process-capture|cascade" "$i" "$PAY_POST" cmd //c "$RUNHOOK_W" posttooluse-dev-process-capture
    timed "$CSV" "posttooluse-dev-process-capture|direct" "$i" "$PAY_POST" bash "$REPO/hooks/posttooluse-dev-process-capture"
    # inject 훅 변형 arm: top-level payload (agent_type 無 → 조기 exit)
    timed "$CSV" "inject-toplevel-earlyexit|direct" "$i" "$PAY_TOP" bash "$REPO/hooks/pretooluse-bash-description-inject"
    # inject 훅 변형 arm: ASCII payload (한글 인코딩 영향 대조)
    timed "$CSV" "inject-ascii|direct" "$i" "$PAY_SUB_ASCII" bash "$REPO/hooks/pretooluse-bash-description-inject"
  done
  loadsnap "m1-end"
  echo "m1 done: $(wc -l < "$CSV") rows"
}

m3() {
  local CSV="$RAW/m3.csv" rounds=8
  : > "$CSV"
  loadsnap "m3-start"
  local r h s e
  for r in $(seq 1 "$rounds"); do
    # A: 6 훅 순차 총 wall
    s=$(now_us)
    for h in "${PRE_HOOKS[@]}"; do bash "$REPO/hooks/$h" < "$PAY_SUB" > /dev/null 2>&1; done
    e=$(now_us); echo "A-seq6,$r,$((e - s)),0" >> "$CSV"
    # B: 6 훅 동시
    s=$(now_us)
    for h in "${PRE_HOOKS[@]}"; do bash "$REPO/hooks/$h" < "$PAY_SUB" > /dev/null 2>&1 & done
    wait
    e=$(now_us); echo "B-par6,$r,$((e - s)),0" >> "$CSV"
    # C: 12 동시 (2 체인 분)
    s=$(now_us)
    for h in "${PRE_HOOKS[@]}" "${PRE_HOOKS[@]}"; do bash "$REPO/hooks/$h" < "$PAY_SUB" > /dev/null 2>&1 & done
    wait
    e=$(now_us); echo "C-par12,$r,$((e - s)),0" >> "$CSV"
  done
  loadsnap "m3-end"
  echo "m3 done: $(wc -l < "$CSV") rows"
}

ghonce() {
  local CSV="$RAW/m1-gh-once.csv"
  : > "$CSV"
  loadsnap "ghonce-start"
  ( cd "$REPO" && timed "$CSV" "branch-delete-gate-ghpath|cascade" 1 "$PAY_DEL" cmd //c "$RUNHOOK_W" git-branch-delete-merge-gate )
  loadsnap "ghonce-end"
  cat "$CSV"
}

integrity() {
  {
    echo "== integrity end $(date -u +%H:%M:%SZ) =="
    if [ -f "$REPO/.claude/ledger/dev-process-event.jsonl" ]; then
      echo "real_ledger_lines=$(wc -l < "$REPO/.claude/ledger/dev-process-event.jsonl")"
    else
      echo "real_ledger_lines=ABSENT"
    fi
    if [ -d "$REPO/.claude-work/dev-process" ]; then
      echo "real_blob_files=$(find "$REPO/.claude-work/dev-process" -type f | wc -l)"
      local MARKV
      MARKV="$(cat "$RAW/marker.txt")"
      HITS=$(grep -rl "$MARKV" "$REPO/.claude-work/dev-process" 2>/dev/null | wc -l)
      echo "real_blob_marker_hits=$HITS (expect 0)"
    else
      echo "real_blob_files=ABSENT"
    fi
    if [ -f "$SANDBOX/.claude/ledger/dev-process-event.jsonl" ]; then
      echo "sandbox_ledger_lines=$(wc -l < "$SANDBOX/.claude/ledger/dev-process-event.jsonl")"
      echo "sandbox_blob_files=$(find "$SANDBOX/.claude-work" -type f 2>/dev/null | wc -l)"
    else
      echo "sandbox_ledger_lines=ABSENT(!)"
    fi
    # git 오염 0 확인
    echo "git_status_porcelain_lines=$(git -C "$REPO" status --porcelain | wc -l)"
  } > "$RAW/integrity-end.txt" 2>&1
  cat "$RAW/integrity-baseline.txt" "$RAW/integrity-end.txt"
}

case "${1:-}" in
  setup) setup ;;
  m2) m2 ;;
  m1) m1 ;;
  m3) m3 ;;
  ghonce) ghonce ;;
  integrity) integrity ;;
  *) echo "usage: driver.sh setup|m2|m1|m3|ghonce|integrity" >&2; exit 1 ;;
esac
