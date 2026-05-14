---
adr_number: 32
title: ADR-027 Amendment 1 — bootstrap strict mode opt-in (hard enforcement layer)
date: 2026-05-06
status: Accepted
category: Plugin Distribution & Consumer Onboarding
carrier_story: CFP-127
parent_epic: CFP-124
supersedes: null
amends:
  - ADR-027
amendments:
  - id: amendment-2
    carrier_story: CFP-660
    effective_date: 2026-05-14
    parent_epic: CFP-431
    summary: |
      Strict-eligible drift 4종 → 5종 확장 — 5번째 (e) consumer workflow version drift
      (consumer `.github/workflows/<name>.yml` 가 wrapper `templates/github-workflows/<name>.yml`
      과 SHA / 핵심 line 불일치). check_bootstrap.py check 10 (workflow_version_drift) 신설.
      stale workflow = race condition / counter collision / silent skip vector 차단.
      `hotfix-bypass:workflow-version-drift` 20번째 family member.
related_files:
  - overlay/hooks/check_bootstrap.py
  - overlay/hooks/check-bootstrap.sh
  - overlay/hooks/check-bootstrap.ps1
  - overlay/hooks/validate_config.py
  - overlay/_overlay/project.yaml.example
  - docs/project-config-schema.md
  - docs/consumer-guide.md
  - docs/adr/ADR-027-consumer-adoption-protocol.md
  - docs/evidence-checks-registry.yaml  # CFP-660 47th entry workflow-version-drift
  - docs/inter-plugin-contracts/label-registry-v2.md  # CFP-660 v2.14 — hotfix-bypass:workflow-version-drift 20번째 family member
  - scripts/bootstrap-labels.sh  # dynamic read path 무변경 (registry-driven)
is_transitional: false
mechanical_enforcement_actions:
  - action_name: workflow-version-drift
    decision_anchor: "Amendment 2 §결정 6"
    evidence_check_entry: workflow-version-drift
    workflow_file: null  # check_bootstrap.py runtime check (별 workflow yml 미신설 — 본 Story scope OUT)
    bypass_label: hotfix-bypass:workflow-version-drift
---

# ADR-032: ADR-027 Amendment 1 — bootstrap strict mode opt-in

## 상태

**Accepted (2026-05-06)** — CFP-127 Phase 1 PR #60 (Sonnet decider CFP-127-001 strict-eligible 4-type pick alpha high confidence) + Phase 2 PR #233 merged. 본 amend = ADR-027 §결정 2 (3-trigger enforcement model) Tertiary trigger amendment 1 (additive, supersede 아님). ADR-027 §결정 3 (Bypass) 와는 별도 mechanism — strict mode 활성 시에도 §결정 3 bypass env (`HOTFIX_BYPASS_CODEFORGE`) 는 그대로 작동. carrier_story = CFP-127 (CFP-124 Epic 의 Phase 4 child).

## 컨텍스트

CFP-124 진단 (2026-05-06) §1.3 가장 깊은 root cause A0:

> **Enforcement model = "LLM-trust + reminder-soft" by design.** ADR-027 §결정 2 (3-trigger enforcement model) 의 Tertiary trigger (SessionStart hook 강화) 가 의도적으로 선택한 모델 — `Claude Code hook 자체는 session 차단 권한 없음 — LLM 이 첫 reasoning turn 에 reminder 받아 사용자에게 dependency 미충족 surface ... (enforcement = LLM 측 책임)`. CFP-96 Epic (28 audit issue) 가 closed 됐음에도 사용자가 "제대로 쓰이지 않는다" 호소하는 핵심 이유 — Claude Orchestrator 가 "이 변경은 작아서 lane 안 돌려도 된다"고 합리화하면 막을 수단이 코드 레이어에 없다.

mctrader 데뷔 audit 검증 (ADR-027 §컨텍스트:35): 7 Epic 모두 main merge / 6 lane plugin 0개 spawn — manual workaround 회귀.

진단의 Gap #4 (Codex P0 #2):

> bootstrap enforcement 가 advisory-only. 플러그인/워크플로우 누락이 경고로만 남고 작업을 차단하지 않음. (`overlay/hooks/check_bootstrap.py:17` `Non-blocking: 발견된 drift 는 WARN 으로만 출력 (stderr). exit 0`)

본 ADR = ADR-027 §결정 2 (3-trigger enforcement model) Tertiary trigger 의 LLM-trust default 유지 + **opt-in strict mode** 추가 (additive amendment).

## 결정 요약

5 결정 freeze. carrier story = CFP-127. ADR-027 §결정 2 amends, supersede 안 함. ADR-027 §결정 3 (Bypass `HOTFIX_BYPASS_CODEFORGE`) 와 별도 mechanism — 동시 작동 가능.

### 결정 1 — ADR-027 §결정 2 Tertiary trigger LLM-trust default 유지 (additive only)

ADR-027 §결정 2 Tertiary trigger 의 "Claude Code hook 자체는 session 차단 권한 없음 — LLM 이 첫 reasoning turn 에 reminder 받아 ... (enforcement = LLM 측 책임)" 본질 그대로 유지. 본 amendment 는 **opt-in strict mode** 만 추가:

- Default behavior: ADR-027 §결정 2 Tertiary trigger 그대로 (warning-only, exit 0)
- Strict opt-in: 명시적 활성 시 adoption-critical drift → exit 1

ADR-027 §결정 2 의 phrase "Claude Code hook 자체는 session 차단 권한 없음" 은 정확 — strict mode exit 1 이어도 Claude Code session 진입은 가로막지 않음. 단 stderr + exit code 가 Orchestrator 첫 reasoning turn 에 surface 되어 사용자 escalation trigger 됨.

### 결정 2 — Strict-eligible drift 4종 정의

`check_bootstrap.py` 의 8 check 중 strict mode 시 exit 1 발화 가능한 항목 = **adoption-critical 4종**:

| Strict-eligible | 검사 | 차단 사유 |
|---|---|---|
| (a) `.claude/_overlay/project.yaml` 부재 | check_workflow_distribution / 기타 yaml-dependent skip | Orchestrator 가 consumer config 미인식, 모든 lane spawn 정합 불가 |
| (b) plugin 11종 중 wrapper / 6 lane / superpowers 미설치 | check_plugins_installed (REQUIRED_PLUGINS subset) | lane orchestration 자체 불가 — manual workaround 회귀 |
| (c) `.claude/settings.json` 의 SessionStart / UserPromptSubmit hook 미등록 | (NEW check 9 — settings.json hook presence) | CFP-103/CFP-104 enforcement layer 자동 누락 |
| (d) 18 label 중 phase:* (7) + gate:* (3) 부재 | check_plugin_labels (subset 검사) | Issue Form 제출 시 label not found error → Story-flow 차단 |

Non-eligible (warning-only 유지) — workflow permissions / consumer-scripts manifest / consumer workflow / Issue forms / CODEOWNERS / 기타 advisory drift. 본 4종은 **lane orchestration 자체를 불가능하게 하는** 항목만.

### 결정 3 — Strict mode opt-in 3 mechanism + 우선순위

3 활성 경로 (좌→우 우선순위):

1. **CLI flag**: `python overlay/hooks/check_bootstrap.py --strict` (직접 호출 시) / `bash check-bootstrap.sh --strict`
2. **Env**: `CODEFORGE_STRICT_BOOTSTRAP=1`
3. **YAML**: `.claude/_overlay/project.yaml` 에 `bootstrap.strict_mode: true`

CLI flag > env > yaml. 셋 중 하나 set 시 strict 활성. 셋 모두 unset = default warning-only.

Schema 확장:
- `docs/project-config-schema.md` §"bootstrap" 추가 — `strict_mode: bool (default false)`
- `overlay/hooks/validate_config.py` SCHEMA_RULES 에 `_is_bootstrap_section` validator
- `overlay/_overlay/project.yaml.example` 신규 commented field 예시

### 결정 4 — Strict exit 1 의 LLM context 동작

Strict mode 활성 + adoption-critical drift 발견 시:

- `check_bootstrap.py` exit code = 1
- stderr 에 strict-eligible drift 명세 + escalation 안내 출력
- SessionStart hook 자체는 Claude Code session 진입 차단 안 함 (ADR-027 §결정 2 Tertiary trigger Phase 1 trust model 유지)
- 첫 reasoning turn 에 LLM 이 stderr context 받아 → 사용자 escalation 의무 (LLM-side 정책)
- LLM 측 의무 = 사용자에게 strict drift 내용 surface + 후속 작업 진행 의사 확인 (ADR-022 §결정 11 user escalation whitelist 의 (e2)/(d-intent) 사례 추가 후보)

### 결정 5 — 점진 도입 + default-on 전환은 별도 CFP + revert procedure 명시

Strict mode 도입 후:

- **mctrader 6-repo (1 hub + 5 sister)** 가 first opt-in target — `.claude/_overlay/project.yaml` 에 `bootstrap.strict_mode: true` 활성 권장 (consumer-guide 명시)
- 후속 신규 consumer 도 점진 opt-in (default false 유지 — adoption barrier 회피)
- 30+ Story 누적 후 PMOAgent retro 가 false-positive block rate vs adoption invariant 보장 효과 측정
- default-on 전환 = 별도 CFP 평가 (현재 본 ADR 비-범위)

기존 LLM-trust path 는 그대로 작동 — strict opt-in 안 한 consumer 는 변화 없음.

**Revert / disable procedure** (false-positive 발생 또는 adoption barrier 시):

| Mechanism | Disable 명령 |
|---|---|
| CLI flag (`--strict`) | flag 미사용 (next invocation) |
| Env (`CODEFORGE_STRICT_BOOTSTRAP=1`) | `unset CODEFORGE_STRICT_BOOTSTRAP` 또는 shell session 재시작 |
| YAML (`bootstrap.strict_mode: true`) | `false` 로 변경 또는 field 삭제 + commit |

3 mechanism 우선순위 (좌→우) — CLI > env > yaml. 즉 yaml=true 인데 CLI 에서 `--no-strict` (별도 flag) 사용 시 yaml 무시. (단 본 amendment 는 `--no-strict` flag 신설 안 함 — 위 표 의 disable 만 지원. CLI flag 는 활성-only, env+yaml 비활성으로 disable.)

ADR-027 §결정 3 (Bypass `HOTFIX_BYPASS_CODEFORGE`) 와 함께 사용 시:
- bypass env set → strict mode 활성 무관 hook 자체 skip (기존 ADR-027 패턴 정합)
- 즉 strict mode 가 bypass 를 막지 않음

## 결과

- ADR-027 §결정 2 Tertiary trigger 의 LLM-trust 본질 유지 + opt-in 강제 가능
- mctrader 6-repo 가 본 amendment 적용 후 lane spawn rate 측정 baseline 확보 (CFP-126 ADR-031 lane evidence 와 결합 효과)
- Strict-eligible drift 4종 = "lane orchestration 자체 불가" 만 — false-positive 위험 minimize

## Risk

| Risk | Mitigation |
|---|---|
| Strict mode false-positive (정상 환경인데 check-bootstrap 가 잘못 fail) | 4종 strict-eligible drift 만 — narrow scope. revert mechanism 3종 즉시 가능. opt-in default-off 30+ Story 모니터링. |
| Telemetry volume — strict mode 활성 consumer 의 stderr 출력 누적 | stderr 만 사용 (stdout 미오염). consumer-side log rotation 책임. |
| Schema drift — `bootstrap.strict_mode` field 명세 변경 시 yaml 호환성 깨짐 | `validate_config.py` schema validator 가 strict_mode 변경 시 backward compat 검증. minor schema 변경은 `project-config-schema.md` versioning. |
| Cold-start (신규 consumer 가 첫 opt-in 시 모든 4종 drift 동시 발견 → escalation flood) | 점진 도입 절차 (consumer-guide 신규 §X) — 단계 1: install plugin / 2: settings.json hook / 3: project.yaml 작성 / 4: strict_mode opt-in. 단계별 PASS 확인. |
| Strict mode 활성 후 mctrader 가 진행 중인 작업 차단 | 점진 도입 — opt-in 만, default-on 전환은 별도 CFP. 활성 후 issue 발생 시 즉시 revert 가능. |

## Out-of-scope

- Strict mode default-on 전환 (별도 CFP, 30+ Story 후 평가)
- ADR-027 §결정 2 / §결정 3 supersede (본 ADR amendment 만)
- Plugin install 자동화 (`/plugins install` 명령은 Claude Code platform-level — codeforge 책임 밖)
- Cross-plugin lane-spawn evidence (ADR-031 별도)
- `--no-strict` 명시적 disable flag 신설 (revert 는 CLI 미사용 / env unset / yaml false 로 충분)

## 해소 기준

N/A — permanent policy

## 관련 파일

- `docs/adr/ADR-027-consumer-adoption-protocol.md` (Phase 1 PR — frontmatter `amendments: [ADR-032]` 갱신, Amendment 1 섹션 추가)
- `overlay/hooks/check_bootstrap.py` (Phase 2 — `--strict` flag + REQUIRED_PLUGINS adoption-critical subset + check 9 NEW + exit code logic)
- `overlay/hooks/check-bootstrap.sh` + `.ps1` (Phase 2 — exit code propagation)
- `overlay/hooks/validate_config.py` (Phase 2 — `bootstrap.strict_mode` validator)
- `overlay/_overlay/project.yaml.example` (Phase 2 — commented field 예시)
- `docs/project-config-schema.md` (Phase 2 — strict_mode field 명세)
- `docs/consumer-guide.md` (Phase 2 — 새 §"strict mode opt-in" subsection)
- spec: `codeforge-internal-docs/wrapper/specs/2026-05-NN-cfp-127-adr-027-amendment-1-design.md` (Phase 1 PR)
- plan: `codeforge-internal-docs/wrapper/plans/2026-05-NN-cfp-127-adr-027-amendment-1-plan.md` (Phase 1 PR)
- carrier story: `codeforge-internal-docs/wrapper/stories/CFP-127.md`
- parent Epic: `codeforge-internal-docs/wrapper/stories/CFP-124.md`

## CFP-658 cross-ref (Amendment 2 of ADR-027)

ADR-027 Amendment 2 (CFP-658, Wave 1 of Epic CFP-431) 는 본 ADR-032 Amendment 1 의 strict-eligible 4종 (a-d) 영역과 disjoint — fallback path 활성 시에도 strict mode 가 활성이면 lane orchestration 가능성 검증 의무 보존. Wave 2 (CFP-660, consumer workflow drift detection) 가 strict-eligible 4 → 5 종 확장 — **본 ADR Amendment 2 §결정 6** 참조.

---

## Amendment 2 — Consumer workflow version drift (5번째 strict-eligible drift, CFP-660 Wave 2 of Epic CFP-431)

**Effective**: 2026-05-14 (CFP-660 Wave 2 of Epic CFP-431 Phase 1 PR merged).

**Carrier**: CFP-660 (`carrier_story`). Parent Epic CFP-431 (audit:from-mctrader-debut). Sibling: CFP-658 (Wave 1, MERGED — Action-blocked fallback path) / CFP-661 (Wave 3 — enterprise prerequisite docs + graceful degradation).

본 amendment = ADR-032 §결정 2 "Strict-eligible drift 4종" 의 **5번째 drift 추가** (additive only, supersede 아님). §결정 6 신설.

### 컨텍스트

CFP-658 (Wave 1) merge 후 mctrader-hub 6-repo audit 에서 새 결함 form 발견 — consumer 측 `.github/workflows/<name>.yml` 가 wrapper `templates/github-workflows/<name>.yml` 와 **SHA / 핵심 line 불일치 (stale workflow)** 상태로 장기 유지 시:

1. **race condition** — wrapper 가 concurrency group / on-event trigger / counter logic 갱신했는데 consumer 는 옛 version 유지 → 동일 Story 의 wrapper-mode vs consumer-mode 동작 분기
2. **counter collision** — wrapper 가 atomic reservation step (예: KEY 발급) 갱신, consumer 는 race-prone 옛 path 유지
3. **silent skip** — wrapper 가 label-conditional trigger 조건 갱신 (예: `phase:요구사항` only → `phase:요구사항 OR phase:설계`), consumer 는 옛 조건 → 정상 Issue silent skip

이 3 form 모두 **lane orchestration 자체 불가** 영역 — ADR-032 §결정 2 의 strict-eligible 정의 (lane orchestration 자체를 불가능하게 하는 항목만) 와 정합. 따라서 strict-eligible 5번째 drift 로 분류 의무.

### 결정 6 — Consumer workflow version drift = strict-eligible 5번째 drift

#### §결정 6.A — 5번째 drift 정의 + 분류 기준

ADR-032 §결정 2 표 의 **5번째 row 추가**:

| Strict-eligible | 검사 | 차단 사유 |
|---|---|---|
| (a) `.claude/_overlay/project.yaml` 부재 | check_workflow_distribution | Orchestrator config 미인식 (기존) |
| (b) plugin 11종 중 8 critical 미설치 | check_plugins_installed | lane orchestration 자체 불가 (기존) |
| (c) `.claude/settings.json` 의 3 hook 미등록 | check_settings_hooks (check 9) | enforcement layer 자동 누락 (기존) |
| (d) 18 label 중 10 critical 부재 | check_plugin_labels | Story-flow 차단 (기존) |
| **(e)** consumer `.github/workflows/*.yml` 가 wrapper templates 와 SHA / 핵심 line drift | **check_workflow_version_drift (check 10 NEW — CFP-660)** | stale workflow = race condition / counter collision / silent skip vector |

분류 기준: **lane orchestration semantics divergence** — consumer workflow 가 wrapper-defined semantics 와 다른 동작을 하면 동일 Story 의 dual-mode behavior 발생, debugging 자체 불가.

#### §결정 6.B — Drift detection 알고리즘 (check 10 NEW)

scan 대상 = `EXPECTED_WORKFLOWS_FULL` (현재 7 file) ∪ `project.yaml` `bootstrap.expected_workflows` (override).

per-file 검사 2-tier:

**Tier 1 — Git blob SHA compare** (primary):
- wrapper resolve: `${CLAUDE_PLUGIN_ROOT}/codeforge/templates/github-workflows/<name>.yml` 의 `git hash-object` (또는 SHA-256 fallback when not under git)
- consumer resolve: `.github/workflows/<name>.yml` 의 동일 hash
- mismatch = drift detected

**Tier 2 — Core marker line compare** (Tier 1 fail soft fallback when git 미설치):
- `concurrency:` group declaration (race control)
- `on:` event types + labels filter (trigger condition)
- `permissions:` block (CFP-530 / ADR-060 Amendment 8 정합)
- header version comment (선택 — `# version: <semver>` marker if present)

각 marker 의 normalized whitespace 비교 (trailing whitespace / blank line collapse) — superficial diff 무시.

#### §결정 6.C — Strict mode integration

`_classify_strict_eligible()` 함수에 5번째 detection branch 추가:

```
(e) workflow_version_drift:
    workflows_dir = Path(".github/workflows")
    plugin_root_templates = plugin_root / "templates" / "github-workflows"
    if plugin_root_templates is None or not workflows_dir.is_dir():
        skip (warning 영역 — wrapper templates 없음 또는 consumer workflows dir 부재)
    for each <name> in EXPECTED_WORKFLOWS:
        if blob_sha(consumer_file) != blob_sha(wrapper_template):
            findings.append("[bootstrap] STRICT (e): <name>.yml drift detected — consumer SHA=<...> vs wrapper SHA=<...>")
```

Default mode (strict 미활성) = warning only (stderr drift report, exit 0). Strict mode + drift detected = exit 1.

#### §결정 6.D — Bypass channel + scope

`hotfix-bypass:workflow-version-drift` label (label-registry-v2 v2.14 sub-entry, 20번째 hotfix-bypass:* family member) — issue-level conditional bypass (ADR-024 Amendment 3 §결정 6.A per-entry namespace 정합). 

`HOTFIX_BYPASS_CODEFORGE=1 + REASON` env (ADR-027 §결정 3) priority HIGHEST — strict 무관 hook self skip.

revert: `unset CODEFORGE_STRICT_BOOTSTRAP` / `bootstrap.strict_mode: false` / `--strict` flag 미사용 (ADR-032 §결정 5 표 정합 — 3 mechanism disable 동일).

#### §결정 6.E — Consumer recovery procedure (warning mode default)

drift 발견 시 consumer 가 즉시 cp sweep:

```
cp ${CLAUDE_PLUGIN_ROOT}/codeforge/templates/github-workflows/*.yml .github/workflows/
git add .github/workflows/
git commit -m "chore: sync .github/workflows from wrapper templates"
```

**`scripts/sync-consumer-workflows.sh` sweep helper = out-of-scope** (별 CFP-TBD carrier 후보 — Phase 2 carrier 영역). 본 Story scope = runtime detection 만 (single-Story scope 보존).

#### §결정 6.F — Out-of-scope (carrier 분리)

- **Sweep automation script** (`scripts/sync-consumer-workflows.sh`) — 별 CFP carrier (issue #467 sibling 후보)
- **Cron-based reactive detection workflow** (`templates/github-workflows/workflow-drift-detection.yml` scheduled daily 02:00 UTC) — 별 CFP carrier 후보 (CFP-627 marketplace drift 패턴 정합, 본 Story 검토 후 OUT 결정 — single-Story scope 보존)
- **Per-marker custom drift threshold** (예: whitespace-only diff = false / semantic-only diff = true) — 본 Story = binary detection 만, threshold 별 CFP

### 결과

- **mctrader 6-repo (1 hub + 5 sister) audit** 결함 form 차단 — Story-flow 의 silent skip / counter collision evidence 만회
- **ADR-032 §결정 2 strict-eligible 정의 보존** — "lane orchestration 자체를 불가능하게 하는 항목만" invariant 유지 (Workflow semantics divergence 가 invariant 영역 충족)
- **Default mode 미변경** — Amendment 1 정합 (warning-only, opt-in only)

### Risk + Mitigation

| Risk | Mitigation |
|---|---|
| False-positive — superficial whitespace diff 도 drift 로 분류 | normalized whitespace 비교 (Tier 2) — ADR-005 self-application byte-identical 정합 영역 외, semantic line 만 |
| Tier 1 git hash 의존 — git 미설치 환경 fail | Tier 2 core marker line compare 자동 fallback |
| Strict mode flood — 점진 도입 환경에서 모든 5종 동시 발견 | Amendment 1 점진 도입 절차 (consumer-guide) — 단계 5 추가 (workflow sync) — opt-in only, default-off |
| `plugin_root` resolution fail (CLAUDE_PLUGIN_ROOT unset + fallback dir 부재) | `_resolve_plugin_root()` 가 None 반환 시 check 10 skip + warning ("plugin root 부재 — workflow drift 검증 불가") |
| Cron-based proactive detection 부재 — drift 가 다음 SessionStart 까지 surface 안 됨 | runtime detection = 1st defense layer / scheduled cron = 2nd layer (별 CFP carrier 후보, post-CFP-660). CFP-627 marketplace drift 패턴 정합 |

### Out-of-scope (Amendment 2 영역)

- Strict mode default-on 전환 (ADR-032 §결정 5 영역 — 30+ Story 후 평가, 본 Amendment 2 비-범위)
- Wrapper-to-consumer sweep automation (별 CFP carrier 후보)
- Multi-version compatibility — wrapper v5.59.0 consumer 와 wrapper v5.60.0 templates 호환성 검증 (별 CFP)
- ADR-032 §결정 2-5 supersede (본 amendment = additive 만)
