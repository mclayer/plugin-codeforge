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
related_files:
  - overlay/hooks/check_bootstrap.py
  - overlay/hooks/check-bootstrap.sh
  - overlay/hooks/check-bootstrap.ps1
  - overlay/hooks/validate_config.py
  - overlay/_overlay/project.yaml.example
  - docs/project-config-schema.md
  - docs/consumer-guide.md
  - docs/adr/ADR-027-consumer-adoption-protocol.md
is_transitional: false
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



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
