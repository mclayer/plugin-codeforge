---
adr_number: 61
title: Python script-writing convention — heredoc escape guard + external .py 의무
status: Accepted
category: Team & Process
date: 2026-05-12
is_transitional: false
related_files:
  - CLAUDE.md
  - scripts/check-adr-sunset-criteria.sh
  - scripts/lib/
  - templates/scripts/
  - templates/github-workflows/
related_stories:
  - CFP-418
  - CFP-423
  - CFP-455
  - CFP-478
amendment_log:
  - amendment: 1
    date: 2026-05-14
    carrier_story: CFP-478
    summary: "Q2 §결정 6 ratchet (권장 (장기) → 표준 (즉시)) + Q3 workflow YAML scope inclusion (§결정 1 body 명시). 28-file scripts/lib/ post-CFP-478 SSOT 확립 evidence. ratchet ↑ direction — ADR-058 §결정 5 sunset_justification 면제 (strengthen direction)."
    ratchet_direction: strengthen
    sunset_justification_required: false
mechanical_enforcement_actions: []
---

# ADR-061: Python script-writing convention — heredoc escape guard + external .py 의무

## 상태
`Accepted`

## 컨텍스트

CFP-418 (ADR retroactive backfill) Phase 2 PR #419 FIX iteration 1 의 root cause 가 **Python regex backref + bash heredoc escape interaction trap** 으로 식별되었다.

### 트랩 시나리오 (CFP-418 evidence)

작성된 Orchestrator 명령:

```bash
python << 'PYEOF'
import re
# Insert sunset section before "## 관련 파일" heading, preserving the heading via backref
re.sub(r'(\n)(## 관련 파일)', f'{section_text}\n\\1\\2', content, count=1)
PYEOF
```

**기대**: `<<'PYEOF'` (single-quoted heredoc) 이므로 bash 가 backslash 처리 안함. Python 이 `\\1\\2` 를 `\1\2` (2개 backref) 로 interpret.

**실제 결과**: 43개 ADR 파일에서 `## 관련 파일` heading 이 `\x01\x02` (SOH + STX 제어문자) 로 교체됨.

### 원인 분석

bash heredoc with `<<'EOF'` 은 **공식적으로** verbatim transmission 을 보장하지만, 실제로는 환경/shell 버전에 따라 `\\1` → `\1` 변환이 발생할 수 있다. Python 은 string literal `'\1'` 을 octal escape (chr(1) = SOH) 로 해석하므로, regex backref 가 무효화되고 raw 제어문자가 replacement 에 삽입된다.

검증 (`python -c "s = '\\\\1'; print(len(s), repr(s))"` in heredoc context):
- 기대: `len=2, repr='\\\\1'` (literal backslash + 1)
- 실제: `len=1, repr='\\x01'` (octal escape applied)

### Trap 의 위험성

- **Detect 가 어렵다**: 신뢰 가능한 evidence (CI lint, sanity check) 없으면 silent corruption 가능
- **Recovery 비용 높음**: CFP-418 에서 separate fix commit + 43 file restore script 필요했음
- **재발 위험 큼**: 향후 backfill / migration / batch transformation script 에서 동일 trap 가능

## 결정

### 결정 1: 외부 `.py` 파일 실행 의무화

bash heredoc 안 multi-line Python (> 5 lines) 작성 **금지**. 다음 절차 의무:

1. `Write` tool 로 `.py` 파일 (보통 `.tmp_*.py` 또는 `scripts/<task>-<date>.py`) 작성
2. `python <file>.py` 또는 `PYTHONIOENCODING=utf-8 python <file>.py` 실행
3. 작업 완료 후 `.tmp_*.py` 즉시 삭제 (`rm .tmp_*.py` — same commit chain)

### 결정 2: 짧은 `python -c` 허용 범위

다음 조건 **모두** 충족 시 `python -c "..."` 형태 inline 허용:

- 5줄 이내
- backslash escape 없음 (regex backref / octal / hex / unicode escape 없음)
- string literal 내 `\` 미사용
- f-string `{...}` 표현식만 사용

위반 시 외부 `.py` 파일 작성 의무 (결정 1).

### 결정 3: heredoc 사용 금지 영역

다음 cases 에서 bash heredoc 안 Python 사용 **금지**:

- regex backref (`\1`, `\g<N>`)
- string substitution with backslash
- 멀티라인 string 처리
- byte-level escape (`\x..`, `\u....`, octal)
- json/yaml string content with backslashes

heredoc 대안:
- 외부 `.py` 파일 (결정 1)
- 또는 bash native tools (`awk`, `sed`, `grep`, `tr`)

### 결정 4: `<<'EOF'` single-quoted 의 한계 명시

`<<'EOF'` (single-quoted) 가 verbatim transmission 을 **공식 보장** 하지만, 실제 환경 (Windows Git Bash + PowerShell mixed runtime, MSYS2, WSL) 에서는 backslash 처리 불일치 사례가 있다. 본 결정은 platform-portable script 작성 의무 — heredoc verbatim 가정 의존 금지.

### 결정 5: Script 작성 후 sanity check

multi-line `.py` script 작성 후 다음 sanity check 의무:

1. **Diff inspection**: `git diff` 또는 `git diff --stat` 로 변경 라인 분포 확인 (예상 영역 외 변경 없음)
2. **Lint re-run**: 관련 lint script (`check-doc-section-schema.sh`, `check-adr-sunset-criteria.sh` 등) 즉시 재실행
3. **Sample file inspection**: 예상 영역의 1-2 sample file 을 `Read` tool 로 확인

CFP-418 trap 은 1단계 (lint re-run) 에서 만약 적용했다면 즉시 발견 가능했다.

### 결정 6: Reusable backfill helper 권장 (장기)

향후 동일 패턴 (frontmatter field 추가 / section insertion / regex-based bulk transformation) 에 대해 reusable Python helper module 작성 권장 — `scripts/lib/adr_transform.py` 같은 위치. 한 번 정확하게 작성하고 sanity check 거친 후 재사용.

본 ADR scope 외 — 별도 follow-up CFP carrier.

### 결정 7: ADR-039 정합 — script work 도 subagent 권장

ADR-039 (Orchestrator subagent default for codeforge modification work) 의 원칙은 script 작성 / 실행에도 적용. 단:
- inline whitelist 4-entry 안 (Read-only Q&A, scratchpad 등) 에서 짧은 script (결정 2 범위) 는 허용
- 그 외 영역에서 multi-line `.py` script 작성 = `Agent` tool spawn 권장 (DeveloperAgent / 적합 role:dev)

본 결정은 CFP-418 evidence (Orchestrator inline backfill script 가 silent corruption 유발) 의 ADR-039 정합 영역 확장.

### 결정 8: Self-application

본 ADR 자체의 `is_transitional` 분류 = `false` (permanent policy). codeforge script-writing 의 영구 표준 carrier.

본 ADR 도 sunset criteria 정책 적용 받음 — `## 해소 기준` 섹션 = `N/A — permanent policy` (ADR-058 §결정 4 self-application 정합).

## 결과

### 긍정
- CFP-418 type trap 재발 위험 차단
- script work audit trail 강화 (`.py` 파일 = git history 에 남음)
- platform-portable script 작성 의무화
- ADR-039 와 정합 (subagent default)

### 부정 / Trade-off
- `Write` tool + `python` 실행 2-step 으로 latency 약간 증가 (inline `python -c` 대비)
- `.tmp_*.py` 파일 추가 housekeeping 필요 (cleanup 의무)

### 영향 받는 영역
- Orchestrator 의 모든 bulk transformation / migration script work
- backfill operation (frontmatter 추가, section 삽입 등)
- ADR / Story / change-plan 자동화 처리

## 해소 기준

N/A — permanent policy

## 다이어그램 (선택)

```mermaid
flowchart TD
    Script[Python script 필요?] --> Lines{≤ 5 lines?}
    Lines -->|yes| Backslash{backslash<br/>escape 있음?}
    Lines -->|no| External[Write .py 파일<br/>python file.py 실행]
    Backslash -->|no| Inline[python -c '...' 허용]
    Backslash -->|yes| External
    External --> Sanity[diff inspection +<br/>lint re-run + sample<br/>file Read]
    Sanity --> Cleanup[rm .tmp_*.py<br/>same commit chain]
```

## 관련 파일

- `CLAUDE.md` — "스크립트 작성 표준" 섹션 cross-ref 1-2줄
- `scripts/check-adr-sunset-criteria.sh` — CFP-418 backfill trap 발견 채널 (lint enforcement evidence)
- `scripts/lib/` — `scripts/lib/<name>.py` 외부 split 표준 위치 (Amendment 1 — CFP-478, 28 file SSOT)
- `templates/scripts/` — 향후 reusable helper 위치 (결정 6 follow-up)
- `templates/github-workflows/` — Amendment 1 (CFP-478) §결정 1 scope 명시 영역
- `docs/adr/ADR-039-orchestrator-subagent-default-for-codeforge-modification-work.md` — 정합 ADR
- `docs/adr/ADR-058-adr-sunset-criteria-mandate.md` — 본 ADR self-application 출처

---

## Amendment 1 (CFP-478 — 2026-05-14)

### Context

CFP-455 (Option A prior art) 가 `scripts/check-evidence-registry.sh` (8-line thin wrapper) + `scripts/lib/check_evidence_registry.py` (314 lines 외부 split) pattern 1 file 적용. CFP-478 = 동일 패턴 27 후보 (19 scripts/ + 8 templates/github-workflows/) bulk scale-up — `scripts/lib/` directory 1 → 28 file 전환. ADR-061 §결정 6 본문 verbatim "본 ADR scope 외 — 별도 follow-up CFP carrier" 명시 → CFP-478 = follow-up CFP carrier.

본 Amendment 는 ratchet ↑ direction (강화 방향) — ADR-058 §결정 5 `sunset_justification` 의무 면제 (§결정 5 strengthen direction 정합).

### 결정 (Amendment delta)

#### Amendment §결정 1.A: 적용 범위 명시 (Q3 carrier)

§결정 1 본문 "bash heredoc 안 multi-line Python (> 5 lines) 작성 **금지**" 의 적용 범위 = **`scripts/*` + `templates/github-workflows/*` 양 영역**.

Rationale: heredoc verbatim transmission inconsistency (CFP-418 SOH+STX corruption evidence) = bash heredoc 자체 영역. workflow YAML `run: |` block 안 bash heredoc 도 동일 위험 surface. Amendment 1 본 단락이 §결정 1 본문 scope 명시화.

위반 처리:
- `scripts/*.sh` 안 heredoc Python > 5 lines = 금지 (§결정 1 invariant)
- `templates/github-workflows/*.yml` 의 step `run:` block 안 heredoc Python > 5 lines = 금지 (Amendment 1 신설)

#### Amendment §결정 6.A: `scripts/lib/` 표준 격상 (Q2 carrier — ratchet ↑)

§결정 6 본문 "Reusable backfill helper 권장 (장기) — `scripts/lib/adr_transform.py` 같은 위치" 의 표현 강화:

- **Before** (ADR-061 원본): "권장 (장기)" + "본 ADR scope 외 — 별도 follow-up CFP carrier"
- **After** (Amendment 1): **표준 (즉시) — `scripts/lib/<name>.py` 위치 의무**. 외부 split 대상 `.py` 파일 = `scripts/lib/` 하위. file naming = snake_case from kebab-case (`scripts/check-foo-bar.sh` → `scripts/lib/check_foo_bar.py`). workflow YAML 외부 split = `scripts/lib/workflow_<purpose>.py` 또는 `scripts/lib/<workflow-prefix>_<purpose>.py` (CFP-478 Change Plan §3.x SSOT 정합).

ratchet 방향 = 강화 (long-term recommendation → immediate standard). ADR-058 §결정 5 strengthen direction 정합 (`sunset_justification` 의무 면제).

#### Amendment §결정 6.B: thin wrapper 표준 8-line template

bash wrapper file 통일 패턴 — CFP-455 prior art verbatim:

```bash
#!/usr/bin/env bash
# <One-line description>. Detail in scripts/lib/<name>.py header.
# ADR-061 §결정 1 / Amendment 1 §결정 6.A — external .py split.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
[ "$#" -eq 0 ] && cd "$SCRIPT_DIR/.."
exec python3 "$SCRIPT_DIR/lib/<name>.py" "$@"
```

본 8-line template = `scripts/lib/` 외부 split bash wrapper 의 표준 형식. 작성자 / 리뷰어 / lint 채널 모두 본 template 정합 검증 가능.

#### Amendment §결정 1.B: workflow YAML state-coupling preservation invariant

workflow YAML 의 heredoc Python migration 시 **state-coupling preservation 의무**:

- step-local `VAR=$(python3 path/to/file.py)` capture chain 보존 (NOT `/tmp/<output>.txt` redirect/read-back — race condition + cleanup 부담)
- env injection 패턴 (`KEY=... TITLE_CLEAN=... python3 path/to/file.py`) + `.py` file 안 `os.environ.get(...)` 정합
- `$GITHUB_OUTPUT` forwarding = workflow `run:` block 의 final shell line 책임 (Python file = stdout-only)

Anti-pattern (금지): 동일 workflow file 안 N heredoc block 을 N 독립 GitHub Actions step 으로 분리 — shell-local 변수 capture chain (`$STORY_CONTENT` → `$CONTENT_B64` → `$GITHUB_OUTPUT`) 깨질 위험. CFP-478 evidence = `story-init.yml` 4 heredoc block.

### 영향 영역 변경

- **Before Amendment 1**: `scripts/lib/` directory = 1 file (CFP-455 prior art, `check_evidence_registry.py`)
- **After Amendment 1 + CFP-478 Phase 2 merge**: `scripts/lib/` directory = 28 file (CFP-455 1 + CFP-478 27). naming convention SSOT = snake_case from kebab-case.

향후 신규 lint/audit/validation script 작성자 = 본 Amendment §결정 6.A 의무 적용. ADR-061 §결정 1 / §결정 2 / §결정 3 invariants 무변경 (cap 5 lines + boundary + trap area 절대 금지 모두 유지).

### Sunset justification

`sunset_justification_required: false` — Amendment 1 = ratchet ↑ direction (강화 방향). ADR-058 §결정 5 정합. ADR-061 자체 `is_transitional: false` (permanent policy) — Amendment 1 도 동일 permanent.

### Carrier evidence (CFP-478)

- 27 candidate audit table (Change Plan §3 — wrapper/change-plans/cfp-478-heredoc-python-bulk-migration.md SSOT)
- trap-evidence verified candidates (P0): `check-decision-principle-vocabulary.sh:90` + `check-story-section-schema.sh:79` + `check-story-section-9-typed.sh:58` — 모두 `replace("\\", "/")` (Windows path normalization, byte-level escape § 결정 3 영역)
- state-coupling verified workflow: `templates/github-workflows/story-init.yml` 4 heredoc block (line 131-158 / 274-353 + 2 sub-blocks) — `$STORY_CONTENT` → `$CONTENT_B64` → `$GITHUB_OUTPUT` capture chain
- pyyaml import 9 candidates 중 8 graceful (try/except ImportError → sys.exit(0)) — 1 outlier `test-cfp-140-ghec-governance.sh` migration 시 표준 패턴 통일 의무 (CFP-478 AC-11)
