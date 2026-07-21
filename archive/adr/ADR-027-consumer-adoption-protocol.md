---
adr_number: 27
title: Consumer Adoption Protocol — bootstrap + 3-trigger enforcement
status: Proposed
category: Plugin Distribution & Consumer Onboarding
date: 2026-05-05
carrier_story: CFP-96
related_files:
  - overlay/hooks/check-bootstrap.sh
  - overlay/hooks/regen-agents.sh
  - overlay/_overlay/project.yaml.example
  - templates/github-workflows/phase-gate-mergeable.yml
  - docs/consumer-guide.md
  - CHANGELOG.md
related_stories:
  - CFP-96
  - CFP-103
  - CFP-104
  - CFP-105
  - CFP-106
  - CFP-107
  - CFP-108
  - CFP-127
  - CFP-1059  # Amendment 7 — consumer adoption 시 project.yaml `deploy.*` schema 확장 (5 sub-field: host_mapping / docker_hub / traefik / 1password / ssh_targets) — codeforge-deploy lane 신설 정합 (ADR-023 Amendment 1 + ADR-087 sibling carrier). §결정 11 신설
  - CFP-2456  # Amendment 12 — §결정 2 Secondary trigger 적용 범위 확장 (§결정 15 신설): ADR-127 §결정 4 dialog skip-offer 금지 규칙을 plugin-shipped 자동활성 UserPromptSubmit reminder hook 으로 소비자 세션 전파 (propagation gap 충당, unconditional fire + JSON additionalContext). ADR-127 Amendment 1 동반
amendments:
  - ADR-032
  - ADR-027-Amendment-2-CFP-658  # CFP-658 Wave 1 of Epic CFP-431 — Action-blocked manual fallback path normative SSOT
  - ADR-027-Amendment-3-CFP-702  # CFP-699 Wave 1 Story-2 — D4 customization marker 의무 추가 (# BEGIN/END wrapper-managed block)
  - ADR-027-Amendment-4-CFP-820  # CFP-699 Wave 3 Story-6 — consumer adoption 시 codeforge.version_pin schema detection 의무 (3-way version atomic invariant consumer layer, ADR-063 Amendment 5 §결정 15 동반). §결정 8 신설
  - ADR-027-Amendment-5-CFP-821  # CFP-699 Wave 3 Story-7 — consumer adoption 시 Issue Forms enumeration 정정 (3종 → audit+bug+story+discussion+codeforge-improvement 5 forms + config.yml) + D4 marker form-level wrap cross-ref (D1 coverage fan-out, ADR-076 §결정 2 표 PR template row 동반). §결정 9 신설
  - ADR-027-Amendment-6-CFP-899  # CFP-858 Wave 4 sub-Epic S2 — consumer adoption detection signals 4-way truth-table SSOT (.claude-plugin/plugin.json + .claude/_overlay/project.yaml 2-signal cross-product → consumer/plugin/mixed/unknown 4-way enum, ADR-083 §결정 1 sibling carrier). §결정 10 신설
  - ADR-027-Amendment-7-CFP-1059  # CFP-1059 Story-1 — consumer adoption 시 project.yaml `deploy.*` schema 확장 (5 sub-field: host_mapping / docker_hub / traefik / 1password / ssh_targets) — codeforge-deploy lane 신설 정합. §결정 11 신설
  - ADR-027-Amendment-8-CFP-1125  # CFP-1125 (CFP-1111 Wave-4 Story-11) — Amendment 6 sunset_boundary declarative (β2 audit #1113 Anchor 4 LOSSLESS 판정 carry). Amendment 6 §결정 10 4-way detection signals + D4 customization marker preserve invariant 의 효용을 CFP-1111 walker paradigm 으로 carry — walker repo-kind detection hook (detect-repo-kind.py 재사용) 동일 truth-table + walker per-step customization_marker_preserve flag 0 silent overwrite. is_transitional 본체 false 무변경 (영역 분리 — Amendment 6 영역만 sunset boundary 명시, 본체 다른 amendment 영향 0). ratchet 강화 only (declaration-only Wave-1 → walker Wave-4 carry), 약화 0건
  - ADR-027-Amendment-9-CFP-1177  # CFP-1177 Story-8 — customization marker block 을 paradigm-agnostic preserved layer 로 codify. 동일 invariant (marker 안 = wrapper SSOT wins, 밖 = consumer byte-identical 보존, integrity fingerprint check 의무, MARKER_NONE = wholesale + user-visible loss report) 가 declarative reconcile (ADR-076 / reconcile-overlay.sh) AND imperative walk apply (walk_plan.py apply_overlay_file) 양 경로에 동일 적용. Walk apply 는 merge_with_marker primitive 재사용 의무 (DRY — 재구현 금지). §결정 12 신설
  - ADR-027-Amendment-10-CFP-2243  # CFP-2243 — §결정 2 3-trigger enforcement 의 Secondary trigger (UserPromptSubmit) 구멍 메우기: "codeforge 의도 선언 + 미초기화 → bootstrap-first" 불변식 명문화 (§결정 13 신설). 기존 Secondary trigger regex 는 변경 동사만 잡고 "codeforge 사용 선언 시점(설계/brainstorm 요청) + 미초기화 감지" 미포착 → 미초기화 greenfield consumer 가 bootstrap 없이 superpowers:brainstorming 으로 silent fallback (Issue #2243). intent(변경동사 + codeforge 고유신호) ∧ detect-repo-kind exit 3 (unknown=진짜 greenfield) ∧ docs/adr·archive/adr 부재 AND-gate → wrapper plugin hooks/ 의 UserPromptSubmit 훅이 bootstrap 미충족 surface + 초기화 우선 유도 (warning inject only, exit 0 — hard-block 권한 보유하나 정책적 미사용). chicken-and-egg 해결 = overlay/ 아닌 wrapper plugin hooks/ 배치 (plugin 설치 즉시 활성). ADR-034 D1 옵션성 보존 (brainstorm 진입 차단 아님, 초기화 권고만). additive only, ratchet 강화 방향 — sunset_justification 불요
  - ADR-027-Amendment-12-CFP-2456  # CFP-2456 — §결정 2 Secondary trigger (UserPromptSubmit) 적용 범위 확장 (§결정 15 신설): ADR-127 §결정 4 dialog skip-offer 금지 규칙을 소비자 세션에 자동 도달시키는 신규 plugin-shipped UserPromptSubmit reminder hook 신설. propagation gap = ADR-127 no-skip 규칙이 wrapper 자기 거버넌스(CLAUDE.md/skill)에만 존재, 소비자 로드 4채널(소비자 root CLAUDE.md=프로세스정책0 / plugin-root CLAUDE.md=미로드[plugins-reference] / on-demand skill=호출의존 / overlay reminder=stale+settings.json의존) 어디에도 부재 → 소비자 Orchestrator free-style skip-offer. 채널=plugin hooks.json UserPromptSubmit 3번째 entry(유일 자동도달, Amendment 10 bootstrap-first-gate 선례) + unconditional fire(변경동사 regex-gate 없음 — skip-offer 는 변경동사 없는 turn 에도 발생) + JSON additionalContext emit(plain stdout 회귀 #13912 회피) + 2-file 패턴(shim+py, bounded read, fail-safe exit0, stderr no-PII) + story.yml doc-only dropdown orphan 양파일 제거(ADR-127 §결정2 정합, byte-mirror). enforcement 간극 명문화(behavioral 도달 ≠ hard block — ADR-027 §결정2 warning-inject-only 정합). overlay invariant 정합(축소불가 강화). additive only, ratchet 강화 — sunset_justification 불요
  - ADR-027-Amendment-13-CFP-2469  # CFP-2469 (Epic CFP-2468 Track W/W1) — §결정 2 3-trigger enforcement 의 mechanical(GitHub branch protection required_status_checks) vs advisory(UserPromptSubmit hook) layer 구분 명문화 (§결정 16 신설). §결정 2 "Block 아님 — warning inject only" 은 hook 層 한정 — branch protection 層은 mechanical merge-block (Primary trigger 실효화). consumer dead-gate(게이트 workflow 존재하나 required_status_checks 미등록 = merge 차단력 0) 해소 = advisory hook 이 아닌 mechanical protection layer 충전. 자동 배선 *시도* 실패(operator org-admin 부재 403)는 advisory 영역으로 graceful degrade (WARN + drift-preview fallback, hard-block 아님). paired carrier ADR-132 (메커니즘 SSOT) + ADR-024 Amendment 20 (step 2 수동→자동). additive only, ratchet 강화 (layer 구분 명문화로 dead-gate 차단 강제력 추가), weakening 0 — sunset_justification 불요
  - ADR-027-Amendment-11-CFP-2250  # CFP-2250 (Epic CFP-2244 S2) — §결정 4 (cross-platform 의무 POSIX + Windows) 의 Windows-parity mechanical 강화 (§결정 14 신설). mctrader 데뷔(Windows) 발견 결함: (1) bootstrap-consumer.ps1 Stage 6 가 `& bash bootstrap-labels.sh` 위임 → Git Bash·WSL 부재 native Windows 에서 WARN+수동안내 종료 → label 미시드 → Issue Form `label not found` (silent 온보딩 깨짐). (2) check_bootstrap.py `_resolve_plugins_json` 의 [HOME, USERPROFILE] 고정 순서 → WSL/dual-env 비결정. (3) manifest/project.yaml 부재 검증이 story-init 발동 후 exit 1 (원인 불명). (4) check_bootstrap.py REQUIRED_LABELS 의 type:* (ADR-049 native Issue Type 이관, bootstrap-labels.sh 미생성) 잔존 오탐. (5) .github/workflows/ 전부 ubuntu-latest, windows runner 0 (결함1 회귀 안전망 부재). 해소: 신규 scripts/bootstrap-labels.ps1 (PowerShell-native 시드, label 데이터 SSOT templates/labels/base-labels.tsv 공유 — .sh/.ps1 drift 차단) + Stage 6 3-tier fallback (bash→pwsh→ERROR, silent skip 금지) + _resolve_plugins_json OS-aware 결정화 (os.name nt → USERPROFILE 우선 / posix → HOME 우선) + preflight 전진 (story-init 발동 전 bootstrap 결손 명시) + REQUIRED_LABELS type:* 제거 (18→15, check_bootstrap.py S2 단독 소유 — S3 type:* org cutover 와 파일 충돌 회피) + windows-bootstrap-smoke.yml (windows-latest, 기본 shell pwsh, dry-run smoke). 정합 부수: ADR-122 후속 — bootstrap-consumer.{sh,ps1}/check-debut-readiness.{sh,ps1} 의 required 목록 superpowers 잔존 제거 (check_bootstrap.py 는 CFP-2249 정합 완료). additive only, ratchet 강화 방향 (§결정 4 의 Windows 측 mechanical 이행 — weakening 0) — sunset_justification 불요
amendment_log:
  - amendment_id: 8
    date: 2026-05-21
    cfp: CFP-1125
    summary: "Amendment 6 sunset boundary declarative (CFP-1111 Wave-4 Story-11 walker paradigm carry). Amendment 6 §결정 10 4-way detection signals (`.claude-plugin/plugin.json` + `.claude/_overlay/project.yaml` 2-signal cross-product → consumer/plugin/mixed/unknown) + D4 customization marker preserve invariant (Amendment 3 §결정 7) 의 효용을 walker per-step customization_marker_preserve flag + walker repo-kind detection hook (detect-repo-kind.py 재사용) 으로 carry. β2 audit (#1113) Anchor 4 LOSSLESS 판정. is_transitional 본체 false 무변경 (영역 분리 — Amendment 6 영역만 sunset boundary 명시, 다른 amendment 영역 영향 0). sister CFP-1115 (β5 ADR-027 Amendment 7) 가 D4 marker block imperative walk 정합 별 carrier. ratchet 강화 only (Wave-1 detection signals SSOT → Wave-4 walker integration test 안 4-way enum 정확 분류 + D4 marker pair preserve verify), 약화 0건 — ADR-058 §결정 5 ratchet 강화 only 정합."
    is_transitional: false
    sunset_justification: "Amendment 6 영역 한정 sunset boundary — 본체 `is_transitional: false` permanent governance invariant 무변경 (영역 분리 명시). Amendment 6 효용 (4-way detection signals + D4 marker preserve invariant) 은 CFP-1111 Wave-4 Story-11 walker paradigm 으로 carry. metric = walker integration test (4-way enum 정확 분류 + D4 marker pair preserve verify, N walk 실행 0 silent overwrite). who = walker repo-kind detection hook (detect-repo-kind.py 재사용) + walker per-step customization_marker_preserve flag. how = walker integration test 안 mock consumer + mock plugin + mock mixed 3 사례 cover + D4 marker pair preserve verify. cross-ref CFP-1113 β2 audit Anchor 4 LOSSLESS 판정 + sister CFP-1115 (β5 Amendment 7 별 carrier — D4 marker block imperative walk 정합)."
  - amendment_id: 9
    date: 2026-05-21
    cfp: CFP-1177
    summary: "customization marker block paradigm-agnostic preserved layer codify (CFP-1177 Story-8). Amendment 3 §결정 7 의 invariant (marker 안 = wrapper SSOT wins / 밖 = consumer byte-identical 보존 / integrity fingerprint check 의무 / MARKER_NONE = wholesale + user-visible loss report) 가 declarative reconcile (ADR-076 / reconcile-overlay.sh) AND imperative walk apply (walk_plan.py apply_overlay_file) 양 경로 모두에 동일 적용됨을 normative codify. apply_overlay_file = merge_with_marker primitive 재사용 (DRY 원칙 — marker logic 재구현 금지). §결정 12 신설. ratchet 강화: scope 확장 (declarative-only → declarative+imperative), weakening 0건 — ADR-058 §결정 5 정합."
    is_transitional: false
    sunset_justification: "ratchet 강화 방향 전용 (scope 확장: declarative-only invariant → declarative+imperative 양 경로 동일 invariant). is_transitional: false permanent governance invariant 무변경. metric = bats TC suite (tests/scripts/cfp-1177/cfp-1177-overlay-apply.bats 19 TC — MARKER_VALID 3-way / MARKER_NONE wholesale / integrity fallback / base_content 시그니처 호환 / frozen dataclass). who = apply_overlay_file 함수 (walk_plan.py §f). how = bats TC 19/19 GREEN + walk_plan.py _split_consumer_outer round-trip byte-identical verify. scope 확장 = weakening 0 (기존 declarative path 무변경, imperative path 신규 적용 추가). ADR-058 §결정 5 sunset_justification = ratchet 강화 방향 전용 exemption 정합."
  - amendment_id: 10
    date: 2026-06-15
    cfp: CFP-2243
    summary: "§결정 2 3-trigger enforcement model 의 Secondary trigger (UserPromptSubmit) 구멍 메우기 — §결정 13 신설. 기존 Secondary trigger (overlay/hooks/userprompt_reminder.py CHANGE_PATTERNS) 는 '변경 동사' 만 잡고 'codeforge 사용 선언 시점(설계/brainstorm 요청) + 미초기화 감지' 미포착. 결과: 미초기화 greenfield consumer 가 codeforge 사용 선언에도 bootstrap 없이 superpowers:brainstorming 으로 silent fallback (Issue #2243). 본 Amendment 10 = entry-gate sub-trigger 명문화: intent(변경동사 ∪ codeforge 고유신호) ∧ detect-repo-kind exit 3 (unknown = plugin.json·overlay 양 부재 = 진짜 greenfield) ∧ docs/adr·archive/adr 부재 AND-gate 충족 시에만 발화 (false-positive 억제). 발화 = bootstrap 미충족 surface + scripts/bootstrap-consumer.sh 안내 (GitHub remote 부재 시 자동 gh repo create 금지 — 명령 surface + 사용자 확인) → warning inject only, exit 0. hard-block 권한(exit 2 prompt erase)은 정책적 미사용 (ADR-027 §결정 2 'Block 아님' + ADR-034 D1 옵션성). chicken-and-egg 해결 = wrapper plugin hooks/ 배치 (overlay/ 아님 — plugin 설치 즉시 활성, 미초기화 consumer settings.json 등록 불요). ADR-034 D1 보존 (brainstorm 진입 차단 아님, 초기화 권고만 — 사용자 거부 시 진행). ratchet 강화: 기존 Secondary trigger 적용 범위 확장 (변경동사 only → codeforge 선언 + 미초기화 감지 포함), weakening 0건."
    is_transitional: false
    sunset_justification: "ratchet 강화 방향 전용 (Secondary trigger enforcement scope 확장: 변경동사-only intent → codeforge-선언 + 미초기화 감지 entry-gate 추가). is_transitional: false permanent governance invariant 무변경. metric = bootstrap-first-gate 단위 테스트 suite (TC1 positive intent+unknown+미초기화→reminder / TC2 consumer overlay 존재→silent / TC3 intent 미매치→silent / TC4 bypass→silent / TC5 fail-safe exit0 / TC6 intent regex enum) + detect-repo-kind.py 무변경 회귀 0. who = hooks/bootstrap-first-gate.py (wrapper plugin hooks/, UserPromptSubmit additive entry). how = AND-gate (intent ∧ detect exit3 ∧ docs·archive/adr 부재 ∧ not-bypassed) ⟺ 발화 invariant + 모든 경로 exit 0 fail-safe. scope 확장 = weakening 0 (기존 변경동사 Secondary trigger 무변경, codeforge-선언 entry-gate 신규 적용 추가). ADR-058 §결정 5 sunset_justification = ratchet 강화 방향 전용 exemption 정합."
  - amendment_id: 11
    date: 2026-06-15
    cfp: CFP-2250
    summary: "§결정 4 (cross-platform 의무 POSIX + Windows) Windows-parity mechanical 강화 — §결정 14 신설. mctrader 데뷔(Windows) 발견 부트스트랩 5 결함 + 1 정합 부수 해소 (Epic CFP-2244 S2). 결함1 = bootstrap-consumer.ps1 Stage 6 bash 위임이 native Windows(Git Bash·WSL 부재)에서 수동안내 종료 → label 미시드 silent 깨짐. 결함2 = check_bootstrap.py _resolve_plugins_json [HOME, USERPROFILE] 고정순서 WSL/dual-env 비결정. 결함3 = manifest/project.yaml preflight 가 story-init 발동 후 (원인 불명). 결함4 = REQUIRED_LABELS type:* (ADR-049 native Issue Type 이관, bootstrap-labels.sh 미생성) 잔존 오탐. 결함5 = windows CI 안전망 0. 정합 부수 = ADR-122 후속 4 스크립트 superpowers required 잔존 제거. 해소 = 신규 bootstrap-labels.ps1 (PowerShell-native + label 데이터 SSOT base-labels.tsv 공유) + Stage 6 3-tier fallback (bash→pwsh→ERROR) + OS-aware resolve (os.name 분기) + preflight 전진 + REQUIRED_LABELS type:* 제거 (18→15, check_bootstrap.py S2 단독 소유) + windows-bootstrap-smoke.yml. additive only, ratchet 강화 (§결정 4 Windows 측 mechanical 이행), weakening 0건 — ADR-058 §결정 5 정합."
    is_transitional: false
    sunset_justification: "ratchet 강화 방향 전용 (§결정 4 cross-platform 의무의 Windows 측 mechanical enforcement 추가: bash↔PowerShell label 시드 parity + windows-latest CI smoke + OS-aware resolve 결정화 + REQUIRED_LABELS 오탐 제거). is_transitional: false permanent policy 무변경. metric = (a) bootstrap-labels.ps1 -DryRun count == bootstrap-labels.sh --dry-run count parity, (b) _resolve_plugins_json os=nt → USERPROFILE / posix → HOME 결정적 단위 TC, (c) REQUIRED_LABELS type:* 부재 + len 15 assert, (d) windows-bootstrap-smoke.yml windows-latest GREEN, (e) 4 스크립트 superpowers grep 0. who = scripts/bootstrap-labels.ps1 + overlay/hooks/check_bootstrap.py + .github/workflows/windows-bootstrap-smoke.yml. how = label 데이터 SSOT 단일화(.sh/.ps1 동일 파일 read 로 drift 구조적 차단) + Stage 6 3-tier fallback (silent skip 0) + os.name 분기 결정화 + native Issue Type 이관 정합. scope = §결정 4 Windows 측 미이행 mechanical 보강 (weakening 0 — bash POSIX 경로 무변경, PowerShell native 경로 신규 추가). ADR-058 §결정 5 sunset_justification = ratchet 강화 방향 전용 exemption 정합."
  - amendment_id: 12
    date: 2026-06-29
    cfp: CFP-2456
    summary: "§결정 2 Secondary trigger (UserPromptSubmit) 적용 범위 확장 — §결정 15 신설. ADR-127 §결정 4 dialog skip-offer 금지(정식 풀 플로우 비협상 / 리뷰·절차 생략 제안 AskUserQuestion 포함 금지) 규칙이 wrapper 자기 거버넌스(CLAUDE.md + skills/user-dialog-mode + ADR-071 Amd11)에만 존재, 소비자 세션 Orchestrator 로드 4채널(소비자 root CLAUDE.md=프로세스정책 0 / plugin-root CLAUDE.md=미로드[plugins-reference 공식docs] / on-demand skill=호출의존 / overlay/hooks/userprompt_reminder.py=stale+settings.json의존) 어디에도 부재 = propagation gap → 소비자 Orchestrator 가 기본 reflex 로 phase-gate 라벨 후 skip-offer free-style(ADR-127 §결정4 위반, 모든 소비자 영향). 해소 = ADR-127 no-skip 규칙을 plugin `hooks/hooks.json` UserPromptSubmit 3번째 entry(유일 자동도달 채널 — Amendment 10 bootstrap-first-gate 선례, /plugins install 자동활성, 소비자 settings.json 비의존 → 미초기화 소비자 도달) 로 ship 하는 신규 reminder hook 신설. KEY: unconditional fire(변경동사 regex-gate 없음 — skip-offer 는 변경동사 없는 turn 에도 발생, 기존 hook 과 차별 invariant) + JSON additionalContext emit(plain stdout 회귀 #13912 회피) + 2-file 패턴(extensionless shim + py, bounded read 1MiB, 전경로 exit0 fail-safe, stderr no-PII) + story.yml doc-only fast-path dropdown orphan 양파일(`.github/`+`templates/`) byte-mirror 제거(ADR-127 §결정2 정합). enforcement 간극 명문화: behavioral 도달 ≠ hard block(UserPromptSubmit = context inject, block 은 PreToolUse 필요 — ADR-027 §결정2 warning-inject-only 정합) → AC2 = 도달+override guidance 충족이지 발화 0 보장 아님, 기계적 skip-offer lint OOS(검사연극). overlay invariant(축소불가) 정합·강화. additive only(기존 2 entry 무변경, overlay reminder deprecated 1-release grace 무변경), ratchet 강화 방향, weakening 0건."
    is_transitional: false
    sunset_justification: "ratchet 강화 방향 전용 (§결정 2 Secondary trigger enforcement scope 확장: 변경동사-gated Story protocol reminder → ADR-127 no-skip 규칙 unconditional 소비자 전파 채널 추가). is_transitional: false permanent governance invariant 무변경. metric = (a) hook 단위 TC suite — unconditional fire(change-verb prompt AND non-change-verb prompt '진행해' 양쪽 reminder emit, 구 hook 과 차별 discriminating) / JSON additionalContext 구조 assert(json.loads 후 hookSpecificOutput.hookEventName=='UserPromptSubmit' + additionalContext key-path, substring-only 금지 anti-theater) / reminder content 키워드(ADR-127·정식·생략·skip) / 전경로 exit0 / stderr prompt-echo 0, (b) story.yml 양파일 dropdown `문서 (Doc-only fast-path)` 부재 grep(byte-mirror). who = hooks/skip-offer-reminder.py + hooks/skip-offer-reminder(shim) + hooks/hooks.json + .github/ISSUE_TEMPLATE/story.yml + templates/.github/ISSUE_TEMPLATE/story.yml. how = plugin-shipped UserPromptSubmit hook(자동활성, settings.json 비의존) ⟺ 매 turn ADR-127 no-skip 컨텍스트 자동 도달 invariant + 전경로 exit0 fail-safe. scope 확장 = weakening 0 (기존 변경동사 Secondary trigger + overlay reminder 무변경, no-skip unconditional 전파 신규 추가). ADR-058 §결정 5 = ratchet 강화 방향 전용 exemption 정합."
  - amendment_id: 13
    date: 2026-06-30
    cfp: CFP-2469
    summary: "§결정 2 3-trigger enforcement model 의 mechanical vs advisory layer 구분 명문화 — §결정 16 신설. §결정 2 'Block 아님 — warning inject only' 은 **hook 層 (UserPromptSubmit advisory) 한정** 임을 명시. branch protection 層 (GitHub native `required_status_checks`) 은 **mechanical merge-block** = Primary trigger 의 실효화 (advisory 아님). consumer dead-gate (게이트 workflow 가 PR 마다 돌지만 required_status_checks.contexts[] 미등록 = merge 차단력 0, mctrader 16 repo 중 15개) 해소 = advisory hook 강화가 아니라 mechanical protection layer 자동 충전 (paired ADR-132 메커니즘 + ADR-024 Amendment 20 step 2 수동→자동). 단 그 충전 *시도* 자체의 실패 (operator org-admin 권한 부재 → branch protection PUT 403) = advisory 영역으로 graceful degrade (WARN 출력 + drift-preview fallback `setup-branch-protection.sh --dry-run`, hard-block 아님 — §결정 2 warning-inject-only 정합). 즉 본 amendment 가 layer 를 2분 — (a) protection 충전 결과 = mechanical (merge 실차단), (b) 충전 시도 실패 = advisory (graceful WARN). 이 구분이 '게이트 workflow 존재 ≠ merge 차단력' 갭을 mechanical layer 충전으로 메우는 dead-gate 해소의 핵심. additive only (기존 §결정 2 3-trigger 무변경, layer 구분 명문화 추가), ratchet 강화 (mechanical layer 충전 강제력 추가), weakening 0건."
    is_transitional: false
    sunset_justification: "ratchet 강화 방향 전용 (§결정 2 enforcement 의 mechanical(branch protection required_status_checks merge-block) vs advisory(UserPromptSubmit warning-inject) layer 구분 명문화 — dead-gate 차단 강제력 추가). is_transitional: false permanent governance invariant 무변경. metric = (a) consumer repo 배선 후 required_status_checks.contexts[] 등록 + 미배선(dead-gate) readiness check WARN 검출 (ADR-132 §결정 8 / CFP-2469 AC-1/AC-6), (b) operator 403 시 WARN graceful + non-FAIL (CFP-2469 AC-3). who = scripts/wire-branch-protection.{sh,ps1} (mechanical 충전) + overlay/hooks/check_bootstrap.py (advisory readiness WARN) + setup-branch-protection.sh --dry-run (403 fallback). how = mechanical(protection PUT 성공 = merge 실차단) ↔ advisory(PUT 시도 실패 403 = WARN graceful) 2-layer 분리. scope = 명문화 (기존 §결정 2 warning-inject-only 의 hook-層-한정 명시 + branch protection 層 mechanical 추가, weakening 0 — hook advisory 영역 무변경). ADR-058 §결정 5 = ratchet 강화 방향 전용 exemption 정합. paired ADR-132 (메커니즘 SSOT) + ADR-024 Amendment 20 (step 2 수동→자동) + ADR-066 §결정 2 (PAT 6-scope 무손상)."
mechanical_enforcement_actions:
  - action_name: section-1-verbatim-postmerge
    decision_binding: "Amendment 2 §결정 6.A — manual fallback path 의 §1 verbatim invariant post-merge lint (warning tier)"
    evidence_registry_entry: section-1-verbatim-postmerge  # docs/evidence-checks-registry.yaml row
    bypass_label: hotfix-bypass:section-1-verbatim-postmerge
    carrier_cfp: CFP-658  # Phase 1 = SSOT 등재, Phase 2 = workflow + script 신설
    introduced_by_amendment: 2
  - action_name: wrapper-managed-block
    decision_binding: "Amendment 3 §결정 7 — consumer customization 영역의 # BEGIN/END wrapper-managed marker block 정합성 lint (blocking-on-pr tier). marker block 안 = wrapper SSOT desired state, 밖 = consumer customization preserve invariant 의 mechanical enforcement"
    evidence_registry_entry: wrapper-managed-block  # docs/evidence-checks-registry.yaml row (Phase 2 PR append, blocking-on-pr tier)
    bypass_label: hotfix-bypass:wrapper-managed-block
    carrier_cfp: CFP-702  # Phase 1 = ADR Amendment 3 + change-plan SSOT, Phase 2 = lint + workflow + migration script 신설
    introduced_by_amendment: 3
  - action_name: consumer-applicability-filter-detection
    decision_binding: "Amendment 6 §결정 10 — consumer adoption detection signals 4-way truth-table (`.claude-plugin/plugin.json` + `.claude/_overlay/project.yaml` 2-signal cross-product → consumer/plugin/mixed/unknown 4-way enum). ADR-083 §결정 1 sibling carrier — wrapper-side filter SSOT 와 boundary disjoint (ADR-027 = consumer-side signal SSOT / ADR-083 = wrapper-side filter mechanism). status: declaration-only-Wave-1 (Phase 2 carrier deferred — `templates/scripts/detect-repo-kind.py` 실 구현 + tests/integration/test_reconcile_overlay_consumer_filter.bats integration + evidence-checks-registry warning tier wire)"
    evidence_registry_entry: consumer-applicability-filter-detection  # docs/evidence-checks-registry.yaml row (Phase 2 PR append, warning tier — ADR-082 §결정 6 declaration-only retain pattern 답습)
    bypass_label: hotfix-bypass:consumer-applicability-filter-detection
    carrier_cfp: CFP-899  # Phase 1 = ADR-083 신설 + ADR-027 Amendment 6 §결정 10 + reconcile-protocol-v1 v1.9 §4.12 schema declare, Phase 2 = detect-repo-kind.py + whitelist populate + reconcile-overlay.sh hook + test suite
    introduced_by_amendment: 6
supersedes: null
superseded_by: null
is_transitional: false
---

# ADR-027: Consumer Adoption Protocol — bootstrap + 3-trigger enforcement

## 상태

Proposed (2026-05-05). CFP-96 Epic carrier ADR. Phase 2 (CFP-103 + CFP-104) implementation 완료 시 Accepted.

## 컨텍스트

mctrader 데뷔 audit (2026-05-02 ~ 2026-05-05) 7 Epic (MCT-12, MCT-18, MCT-25, MCT-32, MCT-37, MCT-48, MCT-63) 모두 main merge — 그러나 **6 lane plugin 0개 spawn**, manual Codex 7-area + Sonnet decider 패턴으로 우회. 검증된 사실 (2026-05-05):

- `~/.claude/plugins/installed_plugins.json` 등록 plugin = 4개 (`github` / `superpowers` / `claude-md-management` / `codex`). codeforge family **0개**.
- `mclayer/marketplace` repo 부재 (`gh api repos/mclayer/marketplace` → 404)
- 6 lane plugin GitHub repo 모두 존재 (`mclayer/plugin-codeforge-{requirements,design,develop,test,review,pmo}`) + 로컬 working dir clone 도 존재
- mctrader-hub `.claude/settings.json` SessionStart hook 이 `${CLAUDE_PLUGIN_ROOT}/codeforge/...` 참조하지만 wrapper 미설치로 silently dropped (#169 와 일치)

사용자 명시 (2026-05-05):

> codeforge는 무조건 사용해야 한다. 사용이 어렵다면 시간이 오래 걸리더라도 issue escalation 해서 개선하는 방식으로 가야 한다. 지금까지 사용하지 못했던 원인도 찾아 모두 제거하고 변경 착수시마다 codeforge를 사용하도록 해야 한다.
> 처음 시작시 codeforge 사용 선언시 의존 관계 플러그인 설치 등 이번 epic은 codeforge 반영 자체에 필요할 것이다.

본 ADR 은 consumer 가 처음 plugin 사용 선언 시점부터 변경 착수 시점까지 codeforge 사용을 enforce 하는 protocol 표준화.

## 결정

### 결정 1 — bootstrap 검증 책임 = wrapper plugin overlay/hooks/

Consumer 측 책임은 `.claude/settings.json` 에 hook 등록 + `.claude/_overlay/project.yaml` 작성만. 검증 로직 자체는 wrapper plugin `overlay/hooks/check-bootstrap.{sh,ps1}` 가 SSOT.

검증 항목 (`installed_plugins.json` 검사):

- codeforge wrapper + 6 lane plugin (`codeforge-{requirements,design,develop,test,review,pmo}`)
- 4 dependency: `github`, `codex`, `superpowers`, `claude-md-management`
- **9 plugin total**

추가 검증:

- consumer `.github/workflows/` 11종 (CFP-105 close 후 14종) sync
- consumer `.github/ISSUE_TEMPLATE/` 5 forms (audit + bug + story + discussion + codeforge-improvement) + `config.yml` sync (Amendment 5 §결정 9 정정 — 旧 stale "3종 (audit + bug + story)" = enumeration gap, reality audit + bug 2종 only / D1 fan-out 후 5 forms + config.yml SSOT. ADR-068 I-4 wording SSOT 정합)
- `CODEOWNERS` + branch protection 정합
- `.claude/_overlay/project.yaml` schema validation (per `docs/project-config-schema.md`)

### 결정 2 — 3-trigger enforcement model invariant

**Primary — Story phase 진입**: 기존 `phase-gate-mergeable.yml` + `phase-label-invariant.yml` workflow. CFP-96 Phase 4 (CFP-106) 에서 #143 fix (doc-only PR fast-pass) + #144 fix (CI terminal state classification) 적용.

**Secondary — UserPromptSubmit hook (NEW, CFP-104)**: consumer `.claude/settings.json` 에 등록, wrapper `overlay/hooks/userprompt-reminder.{sh,ps1}` 호출. 검출 패턴 regex `(구현|만들|수정|짜|fix|implement|refactor|create|add)` 매치 + 활성 Story 미특정 ∨ phase label 부재 시 stdout 으로 reminder 출력 → Claude Code 가 LLM context 에 inject. **Block 아님 — warning inject only.**

**Tertiary — SessionStart hook (강화, CFP-103 + CFP-104)**: 기존 `regen-agents.sh` 호출 + 신규 `check-bootstrap.{sh,ps1}` 강화. 부재/불일치 시 stdout 으로 안내 + LLM context inject. **Claude Code hook 자체는 session 차단 권한 없음** — LLM 이 첫 reasoning turn 에 reminder 받아 사용자에게 dependency 미충족 surface + 후속 작업 이전에 install 안내 (enforcement = LLM 측 책임).

### 결정 3 — Bypass 메커니즘

긴급 hotfix 등에서 enforcement 우회 필요 시:

```
HOTFIX_BYPASS_CODEFORGE=1
HOTFIX_BYPASS_REASON="<사유 텍스트>"
```

두 env flag 동시 설정 의무. bypass 사용 시:

- hook 의 reminder/warning 출력 skip
- `docs/hotfix-playbook.md` 에 사유 등재 의무
- bypass 후 후속 audit issue 자동 생성 (post-bypass audit, CFP-106 Phase 4 에서 detail)

### 결정 4 — Cross-platform 의무 (POSIX + Windows)

Hook 구현은 양 OS 모두 검증:

- POSIX: bash 5.x+ (Linux, macOS)
- Windows: PowerShell 5.1+ (mctrader-hub Windows 환경 정합)

consumer `.claude/settings.json` 에 OS 분기 등록 (또는 wrapper 가 `$OSTYPE` / `$env:OS` 분기). 단위 테스트 양 platform CI 의무 (CFP-103 task).

### 결정 5 — consumer-guide.md 가 SSOT

Consumer 절차 SSOT = `docs/consumer-guide.md`. 본 ADR 은 결정만 freeze, 절차/명령어 SSOT 는 consumer-guide. CFP-106 Phase 4 에서 consumer-guide §X "CI terminal state classification" + §Y "bootstrap protocol" 추가.

## 결과

- mctrader-hub Phase 6 verify (CFP-108, #204) 후 protocol 정합 확인
- 향후 mclayer org 의 모든 신규 consumer (mctrader-market 외 5개 포함) 가 본 protocol 채택
- mctrader 의 7 기 완료 Epic 은 retroactive 처리 안 함 (manual artifact 유지)

## Out-of-scope

- IDE plugin / browser companion / WebSocket reload — 현 hook 메커니즘 한정
- CFP-50 marketplace parity CI 자동화 — Phase 5 manual sync 후 follow-up
- 6 lane plugin 의 internal redesign — 발견 시 별도 CFP-N

## 해소 기준

N/A — permanent policy

## 관련 파일

- `overlay/hooks/check-bootstrap.sh` (Phase 2 강화)
- `overlay/hooks/regen-agents.sh` (Phase 2 또는 4 #169 docstring fix)
- `overlay/hooks/userprompt-reminder.{sh,ps1}` (Phase 2 NEW)
- `overlay/_overlay/project.yaml.example` (Phase 2 schema 보강)
- `templates/github-workflows/phase-gate-mergeable.yml` (Phase 4 #143 fix)
- `templates/github-workflows/story-init.yml` 등 4종 (Phase 3 NEW, CFP-45 close)
- `docs/consumer-guide.md` (Phase 4 §X 추가)
- spec: `codeforge-internal-docs/wrapper/specs/2026-05-05-cfp-96-first-consumer-adoption-bootstrap-design.md`
- plan: `codeforge-internal-docs/wrapper/plans/2026-05-05-cfp-96-first-consumer-adoption-bootstrap-plan.md`

## Amendment 1 — Strict mode opt-in (ADR-032, CFP-127)

**Effective**: 2026-05-06 (CFP-127 Phase 1 PR #60 + Phase 2 PR #233 merged).

본 ADR §결정 2 (3-trigger enforcement model) Tertiary trigger (`check-bootstrap` SessionStart hook) 의 `LLM-trust default` 는 유지 (warning-only, exit 0). [ADR-032](ADR-032-adr-027-amendment-1-hard-enforcement.md) 가 **additive opt-in strict mode** 추가 — supersede 아님.

**Strict mode 활성 조건** (CLI > env > yaml priority):
1. `--strict` flag (`bash overlay/hooks/check-bootstrap.sh --strict`)
2. `CODEFORGE_STRICT_BOOTSTRAP=1` env
3. `bootstrap.strict_mode: true` in `.claude/_overlay/project.yaml`

**Strict 활성 + 4종 strict-eligible drift 발견 → exit 1** (Sonnet decider CFP-127-001 pick alpha):
- (a) `project.yaml` 부재
- (b) plugin 8 critical (wrapper + 6 lane + superpowers) 미설치
- (c) `settings.json` 3 hook (SessionStart × 2 + UserPromptSubmit × 1) 미등록
- (d) 18 label 중 phase:* (7) + gate:* (3) = 10 critical 부재

**Bypass priority HIGHEST**: §결정 3 `HOTFIX_BYPASS_CODEFORGE=1 + REASON` 양 env set → strict 무관 hook self skip. Bypass mechanism (§결정 3) 와 Strict mode (Amendment 1) 동시 작동, 별도 mechanism.

**Default 미변경** = warning-only. mctrader 6-repo 점진 도입 가능. 본 amendment = additive 만 (default behavior 변경 없음).

상세: [ADR-032](ADR-032-adr-027-amendment-1-hard-enforcement.md) §결정 1-5.

## Amendment 2 — Action 차단 시 agent direct write fallback path (CFP-658)

**Effective**: 2026-05-14 (CFP-658 Wave 1 of Epic CFP-431 Phase 1 PR merged).

**Carrier**: CFP-658 (`carrier_story`). Parent Epic CFP-431 (audit:from-mctrader-debut). Sibling Waves: CFP-660 (consumer workflow drift detection) / CFP-661 (enterprise prerequisite + graceful degradation).

본 ADR §결정 2 (3-trigger enforcement model) Primary trigger (`story-init.yml` 등 workflow) 가 enterprise GitHub Actions `default_workflow_permissions: read` 차단 환경 또는 일반 Action failure 시 silent skip 되는 single-point-of-failure 해소 + ADR-039 inline whitelist 외 영역 modification 금지 와 의무 충돌 해소.

본 amendment = ADR-027 §결정 2 Primary trigger 의 **fallback path** 추가 (additive, supersede 아님). §결정 6 신설.

### 결정 6 — Action 차단 시 agent direct write fallback path (normative SSOT)

#### §결정 6.A — Fallback trigger 정의 + 우선순위

2 trigger hybrid:

| Option | 정의 | 적용 영역 |
|---|---|---|
| **(A) Declarative** | `.claude/_overlay/project.yaml` 의 `bootstrap.fallback_mode: action_blocked` enable | 영구 차단 환경 (enterprise admin policy disable) default |
| **(C) Explicit ad-hoc** | Issue 발의자 또는 Orchestrator 가 `fallback:manual` label 부착 | per-Issue override (일시 outage / 사용자 explicit 선택) |

**우선순위 (C) > (A)** — per-Issue override > environment default.

**Option (B) Outage detection (workflow run conclusion + N분 timeout) 폐기** — Researcher 위험 1 (workflow self-fail detection 불가, silent failure) 차단.

#### §결정 6.B — 활성 agent + 책임 분배

| Agent | 역할 | 사유 |
|---|---|---|
| RequirementsPLAgent | §1-§7 직접 생성 (Issue body §1 verbatim copy) — **skip 가능** | mctrader-hub MCT-135 evidence 패턴 (brainstorm Phase 0 4-agent burst 합성 spec 이 §3-6 SSOT 대체 시 RequirementsPL 의 4 mandate verbatim 수행 = redundant spawn 회피, ADR-064 §결정 3 룰 1 derived default) |
| ArchitectPLAgent | Phase 1 PR manual `gh pr create` 책임 + Codex Touchpoint #2 dispatch | ADR-052 Amendment 4 mandatory 영역 |
| Orchestrator | phase label 수동 부착 + §14 Lane Evidence row append | ADR-031 / lane-self-write-boundary skill 정합 |

#### §결정 6.C — Governance ratchet 약화 mitigation 3종 (SecurityArch T1/T2/T3)

| Invariant | Mitigation | Tier |
|---|---|---|
| §1 verbatim immutable | post-merge lint `section-1-verbatim-postmerge.yml` (Phase 2 carrier) — Story §1 ↔ Issue body §1 byte-identical, drift 시 `hotfix-bypass:section-1-verbatim-postmerge` audit comment 자동 발의 | warning (ADR-060 framework) |
| phase-label transition | Orchestrator 수동 의무 (`codeforge:lane-self-write-boundary` skill 정합) | governance |
| 4 required check | manual PR 도 phase-gate-mergeable + doc frontmatter + doc section + invariant-check 통과 의무 (`enforce_admins:true` ratchet 유지, CFP-70) | blocking |

#### §결정 6.D — PAT scope 최소권한 표 (SecurityArch 조건 2)

| Scope | 필요 여부 | 사유 |
|---|---|---|
| `repo` | required | Issue read / branch create / PR open |
| `read:org` | required | org membership 검증 |
| `write:packages` | forbidden | 본 fallback 범위 외 |
| `admin:*` | forbidden | governance ratchet 약화 vector |

GitHub App 권장 (ADR-066 90 days rotation 정합).

#### §결정 6.E — Shell injection 차단 (SecurityArch 조건 3)

Issue body parse 시 shell injection 위험 영역. `manual-story-init-fallback.sh` (Phase 2 carrier) 안 `printf '%s'` + heredoc single-quoted 의무 (ADR-061 bash 인접 변형):

```bash
ISSUE_BODY=$(gh issue view "$ISSUE_NUMBER" --json body --jq '.body')
SECTION_1=$(printf '%s' "$ISSUE_BODY" | awk '/^## 1\./,/^## 2\./' | head -n -1)
cat > "docs/stories/${KEY}.md" <<'STORY_EOF'
${SECTION_1}
STORY_EOF
```

#### §결정 6.F — 2-PAT namespace 분리 (OpRiskArch 조건 2)

| PAT name | Scope | 용도 |
|---|---|---|
| `CODEFORGE_CROSS_REPO_PAT` (기존) | repo + read:org | phase-gate-mergeable.yml + rate-limit-fallback-kpi.yml (ADR-066) |
| `CODEFORGE_FALLBACK_PAT` (신설) | repo only | manual fallback path 전용 — write:packages / admin:* 금지 |

namespace 분리 = fallback path 침해 시 blast radius 최소화.

#### §결정 6.G — Burst control + rate-limit (OpRiskArch 조건 3-4)

`manual-story-init-fallback.sh` 안 exponential backoff:
- 1차 retry: 1s wait — `[empirical-source: AWS SDK Builders' Library 'Timeouts, retries, and backoff with jitter' base * 2^attempt formula]`
- 2차 retry: 2s wait — `[empirical-source: 동상]`
- 3차 retry: 4s wait — `[empirical-source: 동상]`
- 초과: silent skip + `fallback:rate-limited` label 부착 — max 3 retry `[empirical-source: GitHub Actions secondary rate-limit conservative bound — 4xx burst 5+ retry 시 blocklist 진입 위험]`

#### §결정 6.H — Existence check verbatim port (DataMigrationArch 조건)

`templates/github-workflows/story-init.yml` L107-124 의 `existence_check` step (CFP-280 Iter 1 FIX, `gh api repos/<owner>/<repo>/branches/<branch>` atomic) 을 `manual-story-init-fallback.sh` 에 verbatim port — race fix manual fallback 영역으로 propagate 의무.

#### §결정 6.I — Trigger (C) ad-hoc PR description checklist mirror (OpRiskArch 조건 1)

`fallback:manual` label 부착 PR description 의무 영역:

```markdown
## Manual fallback checklist
- [ ] Issue body §1 verbatim copy (byte-identical 검증)
- [ ] KEY = PREFIX-${ISSUE_NUMBER} (ADR-036 atomic)
- [ ] Branch existence_check (`gh api repos/<owner>/<repo>/branches/<branch>`)
- [ ] PR opened via `gh pr create`
- [ ] phase:요구사항 label 부착
- [ ] `fallback:manual` label 부착
```

silent failure detection forcing function.

### Bypass 정합

§결정 3 `HOTFIX_BYPASS_CODEFORGE=1 + REASON` 양 env set → strict 무관 hook self skip. Amendment 2 fallback path 활성 시에도 §결정 3 bypass mechanism 그대로 작동 — 별도 mechanism.

### Default 미변경 = additive only

본 amendment = additive 만 (default behavior 변경 없음). consumer overlay 의 `bootstrap.fallback_mode` 부재 = default `auto` = 기존 동작 보존 (backward-compat).

상세 Change Plan: `codeforge-internal-docs/wrapper/change-plans/cfp-658-action-blocked-fallback.md`.

Cross-ref:
- [ADR-032](ADR-032-adr-027-amendment-1-hard-enforcement.md) — Amendment 1 strict-eligible 4종
- [ADR-036](ADR-036-project-key-atomic-reservation.md) — KEY atomic invariant 보존
- `docs/domain-knowledge/domain/github-actions/workflow-blocked-manual-fallback.md` — recovery runbook
- `docs/consumer-guide.md` §"Action 차단 환경 fallback" — consumer runbook
- `docs/orchestrator-playbook.md` §"fallback decision tree" — Orchestrator detection 절차
- `docs/project-config-schema.md` `bootstrap.fallback_mode` — schema

## Amendment 3 — D4 customization marker 의무화 (CFP-702)

**Effective**: 2026-05-15 (CFP-699 Wave 1 Story-2 Phase 1 PR merged 시점).

**Carrier**: CFP-702 (`carrier_story`). Parent Epic CFP-699 (선언적 reconciliation 기반 codeforge upgrade flow). Sibling Wave 1 Story-1: CFP-701 (reconciliation contract + ADR-076 + reconcile-protocol-v1, **MERGED prerequisite**).

본 ADR §결정 1 (bootstrap 검증 책임 = wrapper plugin overlay/hooks/) + §결정 5 (consumer-guide.md SSOT) 정합. ADR-076 (Story-1 carrier) 의 reconcile-protocol-v1 contract 가 `customization_preservation_entry: "marker_block"` + `marker_block_syntax_carrier: "CFP-702"` 로 본 Amendment 3 에 syntax 영역을 명시적 위임. 본 amendment = ADR-027 §결정 추가 (additive, supersede 아님). §결정 7 신설.

### 결정 7 — D4 customization marker block 의무 (normative SSOT)

#### §결정 7.A — marker block syntax 정식 정의

Consumer customization 영역과 wrapper SSOT desired state 영역을 명문화·구분하는 marker block:

```
# BEGIN wrapper-managed
<wrapper SSOT desired state mirror 영역 — upgrade 시 wrapper 최신 버전 기준 mirror>
# END wrapper-managed
```

**Comment prefix per-filetype** (§결정 7.A.1 — Axis 1 결정):

| File type | BEGIN marker | END marker | 적용 영역 |
|---|---|---|---|
| `.yml` / `.yaml` (project.yaml, workflow) | `# BEGIN wrapper-managed` | `# END wrapper-managed` | overlay project.yaml / consumer-local workflow |
| `.sh` / shell hook | `# BEGIN wrapper-managed` | `# END wrapper-managed` | `.claude/hooks/` fragment |
| `.md` (CLAUDE.md overlay) | `<!-- BEGIN wrapper-managed -->` | `<!-- END wrapper-managed -->` | `.claude/_overlay/CLAUDE.md` |
| `.json` (settings.json) — **marker-incapable** | (sidecar manifest) | (sidecar manifest) | `.claude/_overlay/.wrapper-managed-manifest.json` sidecar — JSON 은 주석 불가, key-path allowlist 방식 (실 구현 = Wave 2 Story-5 carrier, 본 Amendment 3 = sidecar 영역 declare only) |

**결정 근거** (Axis 1): file-type 별 native comment prefix variant 채택 — 단일 `#` 강제는 `.md` (markdown 은 `#` 가 heading) 충돌, JSON 은 주석 자체 불가. comment-syntax-bearing 영역 (`.yml`/`.sh`)은 `#`, markdown 은 HTML comment, JSON 은 sidecar manifest. 외부 prior art = Ansible blockinfile `marker` 파라미터 (file-type 별 comment prefix 주입 패턴, Story §6.2 표 정합도 "가장 높음").

#### §결정 7.B — marker block 안 = wrapper SSOT, 밖 = consumer customization preserve invariant

- **marker block 안 영역** = wrapper SSOT desired state target. upgrade 시 wrapper 최신 버전 기준 **wholesale mirror** (consumer 변경 무시 — wrapper wins inside block).
- **marker block 밖 영역** = consumer customization = **preserve** (upgrade 시 wrapper 가 절대 침범 0 — consumer wins outside block).

이는 reconcile-protocol-v1 §3.2 Rule 3.2.1 의 verbatim cross-ref. codeforge 모델 = "wrapper SSOT wins inside marker block, consumer wins outside" — npm / Helm 의 'consumer wins' default 와 **reverse** (SSOT-driven 모델, Story §6.1 Unknown unknowns 정합). 외부 prior art 동형 = Kustomize base(wrapper SSOT) + overlay(consumer customization) 분리.

#### §결정 7.C — marker 부재 fallback = wholesale_mirror_with_user_visible_loss_report

Consumer 가 marker block 도입 전 customization 영역 보유 시 (mctrader 5 repo 등 기존 adopter):

- snapshot 안 해당 file 전체 보존 (full backup — reconcile-protocol-v1 Rule 3.2.2 cross-ref)
- wholesale mirror 후 **user-visible loss report 생성** (`docs/upgrade-events/<date>-<version>.md` 안 `## Wholesale mirror losses` § 명시)
- **silent overwrite 0** invariant (EPIC-AC-4 "충돌 시 명시적 보고 (silent overwrite 0)" verbatim 정합)

reconcile-protocol-v1 `marker_block_absent_behavior: "wholesale_mirror_with_user_visible_loss_report"` field 의 verbatim cross-ref. 본 fallback = graceful degradation (marker 부재 = breaking 아님, additive governance — backward-compat).

#### §결정 7.D — lint mechanical enforcement (blocking-on-pr tier)

`scripts/check-wrapper-managed-block.sh` (Phase 2 carrier) — marker block 정합성 검증:

- **BEGIN/END pairing**: 모든 BEGIN 은 대응 END 보유 (orphan BEGIN / orphan END = malformed → exit ≠ 0)
- **순서 invariant**: BEGIN 이 END 보다 앞 (역전 = malformed)
- **nesting 정책** (§결정 7.D.1 — Axis 2 결정): **flat only — nesting 금지** (BEGIN ... BEGIN ... END ... END = lint reject). 결정 근거: nested marker 는 wrapper SSOT 영역 안에 consumer customization 을 중첩 = "marker 안 = 100% wrapper, 밖 = 100% consumer" invariant (§결정 7.B) 와 모순. depth tracking 복잡도 회피 + Ansible blockinfile flat-only 패턴 동형.
- **evidence-checks-registry tier**: `current_tier: blocking-on-pr` (Story §5.2 AC-3 + Spec §7 Story-2 row verbatim). bypass channel = `hotfix-bypass:wrapper-managed-block` label (ADR-024 §결정 6.A per-entry namespace).
- **workflow self-app**: `templates/github-workflows/wrapper-managed-block.yml` ↔ `.github/workflows/wrapper-managed-block.yml` byte-identical (ADR-065 §결정 1 정합).

##### §결정 7.D.2 — lint file-scope = consumer customization 영역 한정 (self-referential skip-list, Axis 5 결정 / CFP-702 FIX iter 2 설계 회귀)

wrapper-managed-block lint 의 검사 대상 file-scope = **consumer customization 영역 한정**. wrapper plugin 자기 meta 파일은 **skip-list 제외** — marker 문자열을 데이터 / 로직 / 문서 / fixture 로 보유하는 self-referential 파일이 actual marker block 으로 오탐되는 것 차단.

**Skip-list (dogfooding self-detection 회피 invariant)** — 다음 generalized 패턴:

1. **lint 구현 자체**: `scripts/check-wrapper-managed-block.sh` (marker 문자열 = grep 패턴 데이터)
2. **lint test fixture**: `scripts/test-check-wrapper-managed-block.sh` (marker 문자열 = malformed/정상 fixture)
3. **migration 구현**: `scripts/migrate-existing-customization.sh` (marker 문자열 = wrap 삽입 데이터)
4. **lint 을 설명하는 SSOT 문서**: `docs/inter-plugin-contracts/reconcile-protocol-v1.md` + `docs/evidence-checks-registry.yaml` + `docs/adr/ADR-027-consumer-adoption-protocol.md` (본 ADR 자신 — marker syntax 문서화 영역)
5. **lint workflow YAML**: `.github/workflows/wrapper-managed-block.yml` + `templates/github-workflows/wrapper-managed-block.yml` (marker 문자열 = workflow step 데이터)

**generalized rule** (enumeration 외 future-proof): "wrapper-managed-block lint 자신 + 그 lint 를 설명·테스트·구현하는 wrapper plugin SSOT 파일" = self-referential → skip. consumer customization 영역 (overlay 4-layer + consumer-local workflow) 만 actual 검사 대상. 결정 근거: D4 marker 의 의미적 scope (§결정 7.B) = **consumer 측 customization 영역의 wrapper SSOT ↔ consumer 경계 명문화** — wrapper plugin 자기 meta 파일은 애초에 marker block 의미 적용 영역 자체가 아님 (consumer 가 customize 하는 파일 아님). under-specified 설계 (FIX iter 2 이전 §결정 7.D 가 file-scope 미명세) 가 Phase 2 dogfooding 에서 7-file false positive 노출 → 본 §결정 7.D.2 가 의미적 scope 를 mechanical scope 로 확정·명문화.

##### §결정 7.D.3 — marker 매칭 = whole-line anchored (substring 매칭 금지, Axis 5 결정 / CFP-702 FIX iter 2 설계 회귀)

lint 의 marker detection = **whole-line anchored 매칭** 의무:

- shell 구현: `grep -xF "<marker>"` (full-line fixed-string) 또는 `grep -E '^# BEGIN wrapper-managed$'` (anchored 정규식)
- **substring 매칭 금지**: `grep -F` (substring) 은 `# BEGIN wrapper-managed-other` / 주석 안 `# ... # BEGIN wrapper-managed ...` / 문서 inline reference 같은 prefix-collision 및 부분문자열 false positive 유발 — FIX iter 2 root cause (현 Phase 2 구현 L96-97 `grep -cF` substring 매칭).
- comment prefix per-filetype (§결정 7.A.1) 별 anchored 패턴: `.yml`/`.sh` = `^# BEGIN wrapper-managed$` / `.md` = `^<!-- BEGIN wrapper-managed -->$` (선/후행 whitespace tolerance 는 구현 spec — change-plan §3, leading whitespace trim 후 anchor).

결정 근거: marker block = **줄 단위 boundary 선언** (§결정 7.A syntax — marker 는 자체 라인 점유). substring 매칭은 marker 의 줄 단위 의미를 위반 → whole-line anchor 가 marker syntax 의 의미적 정합. Ansible blockinfile 의 marker 도 전용 라인 점유 (동형 prior art).

**additive 정합**: §결정 7.D.2 / §결정 7.D.3 = additive (supersede 0). §결정 7.D.1 flat-only nesting + §결정 7.D evidence-tier / workflow self-app 모두 무손상 유지. governance 강화 방향 ratchet (false positive 차단 = lint 정밀도 강화) — ADR-058 §결정 5 sunset_justification 불요 (강화 방향).

#### §결정 7.E — retroactive migration (idempotent)

`scripts/migrate-existing-customization.sh` (Phase 2 carrier) — 기존 marker-부재 consumer (mctrader 5 repo, Tier B-extended) retroactive auto-wrap:

- **idempotency invariant**: N회 실행 = 1회 effect (이미 wrap 된 영역 재wrap 0). 2차 실행 = file hash 동일 (Story §5.2 AC-4 testable predicate). 외부 prior art = Ansible blockinfile marker-pair replace idempotency 동형.
- **false-positive boundary** (§결정 7.E.1 — Axis 3 결정): **wrapper SSOT template 과 byte-diff 가 0 인 영역 + `consumer-scripts.manifest` 등재 영역만 wrap** (conservative — consumer customize 영역은 marker 밖 보존). 결정 근거: byte-diff 0 = consumer 가 손대지 않은 순수 wrapper SSOT mirror 영역임이 mechanical 확정 → false-positive 0. manifest 등재 = wrapper 가 consumer 에 배포하는 영역의 explicit SSOT (Story §2 Refactor perspective — `consumer-scripts.manifest` 가 wrapper SSOT mirror 영역 anchor).
- **사용자 결정 분기 0 invariant**: false-positive boundary 가 사용자 prompt 없이 mechanical 판정 (byte-diff + manifest = 결정론적). dry-run preview 는 정보 제공만 = 결정 분기 아님 (reconcile-protocol-v1 `dry_run_classified_as_decision_branch: false` verbatim 정합, CFP-699 Epic §1 WHY "0 자리" directive 정합).

#### §결정 7.F — lint promotion_criteria (Axis 4 결정)

`wrapper-managed-block` evidence-checks-registry entry 의 promotion_criteria (blocking-on-pr 첫 도입이므로 Story-1 `worktree-first-pre-checkout` entry 패턴 reference):

| Field | 값 | 근거 |
|---|---|---|
| `pr_cumulative_min` | 20 | ADR-060 §결정 6 (a) 표준값 — `worktree-first-pre-checkout` L634 verbatim 동형 |
| `failure_threshold` | 0 | ADR-060 §결정 6 (b) — bypass 외 failure 0 |
| `current_tier` | `blocking-on-pr` | Spec §7 Story-2 row verbatim ("blocking-on-pr"). ADR-060 4-tier enum 의 2번째 tier — D4 marker 위반 = customization wholesale loss 직결 (HIGH risk) → warning tier 시작점 아닌 blocking-on-pr 직접 도입 정당 (Story §5.3 AC-3 edge 정합) |

#### §결정 7.G — reconcile-protocol-v1 4.3 (b) trigger 발동

Story-1 contract `reconcile-protocol-v1.md` §4.3 (b): "Wave 1 Story-2 (CFP-702) merge — marker block syntax 확정 시 `customization_preservation_entry` 영역 확장". 본 Amendment 3 에서 marker syntax 정식 확정 (§결정 7.A) → contract 4.3 (b) trigger 발동. **단 contract 갱신 = Phase 2 PR scope** (kind:registry MINOR sibling sync 면제, ADR-008 §결정 2 + ADR-010 §결정 2). Phase 1 (본 ADR Amendment 3) = syntax SSOT 확정만, contract `customization_preservation_entry` 영역 확장 반영 = Phase 2 PR 에서 동반 (Story §4.0.1 "reconcile-protocol-v1.md 수정 = Phase 1 또는 Phase 2 (ArchitectAgent 결정)" → **Phase 2 결정** — marker syntax 가 lint script 와 atomic 하게 검증되어야 contract 영역 확장이 mechanical 유효).

### Bypass 정합

§결정 3 `HOTFIX_BYPASS_CODEFORGE=1 + REASON` 양 env set → strict 무관 hook self skip. Amendment 3 marker lint 활성 시에도 §결정 3 bypass mechanism 그대로 작동. 추가로 marker lint per-entry bypass = `hotfix-bypass:wrapper-managed-block` label (ADR-024 §결정 6.A per-entry namespace, ADR-060 framework 정합) — 별도 mechanism.

### Default 미변경 = additive only

본 amendment = additive 만. marker 부재 consumer = §결정 7.C wholesale_mirror_with_user_visible_loss_report fallback (graceful degradation, backward-compat). 기존 consumer 동작 즉시 변경 0 — migration script (§결정 7.E) 가 retroactive opt-in 보장.

### 해소 기준 정합

ADR-027 frontmatter `is_transitional: false` (permanent policy, 기존 §"해소 기준" = "N/A — permanent policy" verbatim). Amendment 3 = D4 marker 의무 추가 = governance 강화 방향 ratchet — ADR-058 §결정 5 sunset_justification 불요 (강화 방향, ADR-064 top-down self-application 정합).

상세 Change Plan: `codeforge-internal-docs/wrapper/change-plans/cfp-702-d4-customization-marker.md`.

Cross-ref:
- [ADR-076](ADR-076-declarative-reconciliation-upgrade.md) — Story-1 carrier, reconcile semantic SSOT (boundary disjoint — ADR-076 = upgrade transaction layer / 본 Amendment 3 = consumer customization marker enforcement layer)
- `docs/inter-plugin-contracts/reconcile-protocol-v1.md` §3.2 Rule 3.2.1/3.2.2 + §4.3 (b) — customization preservation entry SSOT
- [ADR-053](ADR-053-structural-change-restart-prerequisite.md) §D2 — 본 Story 구조적 변경 (scripts/+workflow 신규) → Wave 2 Story-5 진입 prerequisite (dogfood-out 면제 분기)
- [ADR-060](ADR-060-evidence-enforceable-promotion-framework.md) — blocking-on-pr tier 첫 도입 (`wrapper-managed-block` registry entry)
- [ADR-065](ADR-065-architect-phase1-mechanical-self-check.md) §결정 1 — workflow templates/ ↔ .github/ byte-identical self-app
- [ADR-040](ADR-040-worktree-convention.md) §결정 7.A — `mechanical_enforcement_actions[]` frontmatter 의무 (본 Amendment 3 = `wrapper-managed-block` entry append)
- `docs/domain-knowledge/domain/upgrade-flow/declarative-reconciliation.md` — Customization layer marker syntax detail (RequirementsPL 본 lane 보강)
- `docs/consumer-guide.md` §"D4 customization marker" — consumer runbook (Phase 2 carrier)

## Amendment 4 — consumer adoption 시 codeforge.version_pin schema detection 의무 (CFP-820)

**Effective**: 2026-05-17 (CFP-699 Wave 3 Story-6 Phase 1 PR merged 시점).

**Carrier**: CFP-820 (Wave 3 Story-6). Parent Epic CFP-699 (선언적 reconciliation 기반 codeforge upgrade flow). Sibling carrier: ADR-063 Amendment 5 §결정 15 (marketplace ↔ plugin.json atomic invariant 의 consumer-side 3-way 확장 — 본 Amendment 4 = ADR-027 consumer adoption protocol 측 schema detection 영역, ADR-063 = 3-way invariant 영역. 두 ADR boundary disjoint, cross-ref 정합).

본 ADR §결정 1 (bootstrap 검증 책임 = wrapper plugin overlay/hooks/) + §결정 5 (consumer-guide.md SSOT) 정합. ADR-063 Amendment 5 §결정 15 (3-way version atomic invariant) 가 consumer pin SSOT location 으로 `.claude/_overlay/project.yaml codeforge.version_pin` (FORM (b), 사용자 confirm 2026-05-17 KST) 를 확정 → 본 Amendment 4 = consumer adoption protocol 의 bootstrap/reconcile detection 영역에 `codeforge.version_pin` schema detection 의무를 codify. 본 amendment = ADR-027 §결정 추가 (additive, supersede 아님). §결정 8 신설.

**ADR collision 회피 (신규 ADR 아닌 Amendment — CFP-820 Story §3.1.5 판정 정합)**: ADR-027 = consumer adoption protocol SSOT — `bootstrap.fallback_mode` (Amendment 2) + `bootstrap.strict_mode` (Amendment 1) 패턴이 이미 consumer-side detection + fallback semantic 의 carrier. `codeforge.version_pin` warning-first → blocking fallback = ADR-027 Amendment 2 `bootstrap.fallback_mode` 의 동형 패턴 → 신규 ADR 신설 시 consumer adoption 영역 2 ADR 분산 (SSOT drift). Amendment = ADR-064 top-down ratchet 강화 방향 only (consumer adoption scope 확장 — version pin detection 추가).

### 결정 8 — consumer adoption 시 codeforge.version_pin schema detection (normative SSOT)

#### §결정 8.A — version_pin schema detection 의무

Consumer adoption 시 (bootstrap / reconcile) wrapper plugin overlay/hooks/ (`validate_config.py` — §결정 1 책임 영역) 가 `.claude/_overlay/project.yaml` 의 `codeforge.version_pin` block 등록 여부 detect:

| State | Detection 결과 | 동작 |
|---|---|---|
| `codeforge.version_pin` block 부재 | `codeforge.version_pin` 미등록 (신규 consumer / 미설정) | **warning-first** — 3-way version parity lint skip + warn message "consumer `codeforge.version_pin` SSOT 미등록 — `codeforge.version_pin` 등록 후 3-way enforce 활성" (exit 0). onboarding 마찰 0 |
| `codeforge.version_pin.version` 등록 (semver string) | `codeforge.version_pin` 등록 | 3-way version parity enforce 활성 (publisher↔registry↔consumer `codeforge.version_pin` byte-identical, mismatch = blocking-on-pr exit 1) |
| `codeforge.version_pin` 존재하나 `version` field 부재 / 비-semver | `codeforge.version_pin` malformed | `validate_config.py` exit 4 (required field 누락/타입 위반 정합 — project-config-schema §6 verbatim) + actionable message. silent skip 금지 |

**결정 근거 (Axis — orthogonality invariant)**: `codeforge.version_pin 가용성` (block 등록 여부 = enforce 가능 여부) 과 `version 정합성` (값 일치 여부 = drift 존재 여부) 은 ORTHOGONAL 2 조건 — 동일 fallback 에 conflate 금지 (CFP-745 FIX Iter 2 base-absent≠marker-absent verified-true precedent 답습. conflate 시 결함: `codeforge.version_pin` 미등록 신규 consumer 즉시 blocking = onboarding 마찰 false-positive / `codeforge.version_pin` 등록 consumer 실 drift 가 warning 약화 false-negative). 외부 prior art = ADR-027 Amendment 2 `bootstrap.fallback_mode: auto | action_blocked` 의 동형 패턴 (consumer onboarding 마찰 회피 → 등록 후 enforce).

#### §결정 8.B — warning-first → 등록 후 blocking fallback semantic (사용자 confirm 2026-05-17 KST)

- **`codeforge.version_pin` 미등록** = warning-only (lint skip + warn, exit 0). `codeforge.version_pin` 부재 = mismatch 판정 불성립 (비교 대상 없음 — false-positive 차단). onboarding 마찰 0 (ADR-027 Amendment 2 `bootstrap.fallback_mode` 패턴 답습)
- **`codeforge.version_pin` 등록 후 mismatch** = blocking-on-pr (exit 1, PR 차단). drift 0 strict enforce (등록 영역)

이는 ADR-063 Amendment 5 §결정 15 `version_handshake_3way_binding.fallback_semantic` (reconcile-protocol-v1 v1.5 §4.8) 의 verbatim cross-ref. codeforge 모델 = "`codeforge.version_pin` 미등록 = graceful skip (additive governance — backward-compat), `codeforge.version_pin` 등록 = strict enforce". consumer-authored invariant 보존 — 모든 codeforge agent 는 `codeforge.version_pin` field write 금지 (project-config-schema §4b verbatim). 3-way lint = read-only compare-only (write surface 0).

#### §결정 8.C — schema location SSOT = project.yaml codeforge.version_pin (FORM (b))

consumer pin location = `.claude/_overlay/project.yaml` `codeforge.version_pin` block (기존 `codeforge:` block sibling sub-key — 기존 SSOT 확장, 신규 file 0, consumer 1-file 정책 정합). 별도 file (`.wrapper-plugin-pin.yaml`) / runtime artifact (`installed_plugins.json`) / hidden config root (`.codeforge/version-pin.yaml`) = 기각 (consumer 1-file 정책 위배 / 의도 declare semantic mismatch — CFP-820 Story §3.1.3 ALTERNATIVE 표 SSOT). schema 정의 = `docs/project-config-schema.md` `codeforge.version_pin` block (본 Amendment 4 동반 MINOR — `updated: 2026-05-17`).

#### §결정 8.D — mechanical enforcement = ADR-063 §결정 15 version-3way-atomic cross-ref (중복 codification 회피)

본 §결정 8 = consumer adoption protocol detection mandate (declarative SSOT). 실 mechanical lint = ADR-063 Amendment 5 §결정 15 의 `version-3way-atomic` evidence-check entry (blocking-on-pr tier, ADR-063 frontmatter `mechanical_enforcement_actions[]` 등재) 가 cover — `scripts/check-3way-version-parity.sh` (Phase 2 carrier) 가 3-way byte-identical version parity 검증. 본 Amendment 4 측 별도 mechanical action 신설은 **중복 codification 회피** (ADR-065 §결정 5 "cross-ref only — 중복 codification 회피" 정합) — ADR-063 marketplace 영역 ↔ ADR-027 consumer adoption 영역 boundary 정합. ADR-027 frontmatter `mechanical_enforcement_actions[]` = Amendment 2/3 entry 보존, Amendment 4 별도 entry 미추가 (ADR-063 §결정 15 entry 가 SSOT).

#### §결정 8.E — validate_config.py validator (Phase 2 carrier)

`overlay/hooks/validate_config.py` `SCHEMA_RULES` 에 `codeforge.version_pin` validator 추가 (Phase 2 carrier — PyYAML only, jsonschema 의존 회피, 기존 SCHEMA_RULES 패턴 정합 — project-config-schema §6 verbatim). Phase 1 (CFP-820) = declarative SSOT mandate (본 §결정 8). Phase 2 = validate_config.py validator 실 구현 + `overlay/_overlay/project.yaml.example` `codeforge.version_pin` 예시 row + `docs/consumer-guide.md` §2g.N consumer runbook.

### 해소 기준 정합

ADR-027 frontmatter `is_transitional: false` (permanent policy, 기존 §"해소 기준" = "N/A — permanent policy" verbatim). Amendment 4 = consumer adoption 시 version_pin schema detection 의무 추가 = governance 강화 방향 ratchet — ADR-058 §결정 5 sunset_justification 불요 (강화 방향, ADR-064 top-down self-application 정합 — consumer adoption scope 확장 only, weakening 0).

상세 Change Plan: `codeforge-internal-docs/wrapper/change-plans/cfp-820-3way-version-atomic.md`.

Cross-ref:
- [ADR-063](ADR-063-marketplace-atomic-invariant.md) Amendment 5 §결정 15 — 3-way version atomic invariant (본 Amendment 4 sibling carrier, boundary disjoint: ADR-063 = 3-way invariant 영역 / 본 Amendment 4 = consumer adoption protocol schema detection 영역)
- `docs/inter-plugin-contracts/reconcile-protocol-v1.md` v1.5 §4.8 `version_handshake_3way_binding` — fallback semantic + orthogonality invariant SSOT (§결정 8.B verbatim cross-ref)
- `docs/project-config-schema.md` `codeforge.version_pin` block — schema 정의 SSOT (본 Amendment 4 동반 MINOR — `updated: 2026-05-17`)
- [ADR-066](ADR-066-pat-rotation-policy.md) §결정 2 — `marketplace contents:read` reuse (3-way lint read-only, Amendment 3 write scope 미사용 — 추가 PAT grant 0)
- [ADR-064](ADR-064-decision-principle-mandate.md) §self-application — Amendment 4 = consumer adoption scope 확장 강화 방향 only (weakening 0)
- `docs/consumer-guide.md` §2g.N — consumer pin setup runbook (Phase 2 carrier)

## Amendment 5 — consumer adoption 시 Issue Forms enumeration 정정 + D4 marker form-level wrap cross-ref (CFP-821)

**Effective**: 2026-05-17 (CFP-699 Wave 3 Story-7 Phase 1 PR merged 시점).

**Carrier**: CFP-821 (Wave 3 Story-7 — coverage fan-out D1+D2+D3). Parent Epic CFP-699 (선언적 reconciliation 기반 codeforge upgrade flow). Sibling carrier: ADR-076 §결정 2 표 PR template row append (Amendment 아닌 표 1행 additive — Issue templates row 동형) + reconcile-protocol-v1 v1.6 §4.3 (h) trigger + §4.9 `coverage_fan_out_implementation_binding` block.

**번호 정정 (설계 lane strict-verify)**: 본 Amendment = **Amendment 5 §결정 9** (Story §1-§6 RequirementsPL synthesis 1차 view 의 'Amendment 4' = frontmatter 미검증 hypothesis — 설계 lane strict-verify origin/main direct Read 결과 **CFP-820 (Wave 3 Story-6) 이 Amendment 4 / §결정 8 점유** → 본 Story-7 = Amendment 5 §결정 9 정정. 동반 reconcile-protocol-v1 version = **v1.6 §4.3 (h)** (Story-7 §3.5 1차 view 'v1.5 §4.3 (h)' = CFP-820 이 v1.5 §4.3 (e) 점유 collision → v1.6 §4.3 (h) 정정). Codex TP#2 verify-before-trust 8-mirror 교훈 + CFP-820 §4.3 (e) "Amendment 번호 정정" 패턴 verbatim 답습 — fact 영향 0, 추적성/번호 정정만 (ADR-068 I-4 wording SSOT 정합).

본 ADR §결정 1 (bootstrap 검증 책임 = wrapper plugin overlay/hooks/) + §결정 5 (consumer-guide.md SSOT) + §결정 7 (Amendment 3 D4 marker syntax) 정합. ADR-076 §결정 2 9 영역 enumeration 표가 wrapper SSOT desired state 단위를 정의 → 본 Story-7 D1 = Issue/PR template fan-out 으로 §결정 1 line 84 의 systemic enumeration gap (`3종 (audit + bug + story)` ↔ reality audit + bug 2종 only, story 부재) 를 정정 + D4 marker (Amendment 3 §결정 7.A.1) 의 신설 form 적용 cross-ref. 본 amendment = ADR-027 §결정 추가 (additive, supersede 아님). §결정 9 신설.

**ADR collision 회피 (신규 ADR 아닌 Amendment — CFP-821 Story §3.1.2 판정 정합)**: ADR-027 = consumer adoption protocol SSOT — `.github/ISSUE_TEMPLATE/` sync enumeration (§결정 1) + D4 marker syntax (Amendment 3 §결정 7) 이 이미 consumer-side template adoption 의 carrier. Issue Forms enumeration 정정 + D4 marker form-level wrap = ADR-027 §결정 1 + Amendment 3 §결정 7.A.1 의 동형 영역 확장 → 신규 ADR 신설 시 consumer adoption 영역 SSOT 분산. Amendment = ADR-064 top-down ratchet 강화 방향 only (consumer adoption scope 확장 — Issue Forms 3종 → 5 forms + config.yml + D4 marker 신설 form 적용).

### 결정 9 — consumer adoption 시 Issue Forms enumeration 정정 + D4 marker form-level wrap (normative SSOT)

#### §결정 9.A — Issue Forms enumeration 정정 (§결정 1 line 84 systemic gap 해소)

§결정 1 line 84 의 `consumer .github/ISSUE_TEMPLATE/ 3종 (audit + bug + story) sync` = systemic enumeration gap (실제 origin/main `.github/ISSUE_TEMPLATE/` = audit.yml + bug.yml 2종 only, story 부재). D1 fan-out 후 정식 enumeration:

| Form | 역할 | SSOT location (Phase 2 carrier) |
|---|---|---|
| `audit.yml` | audit Issue Form (기존 — SSOT 승격) | `templates/.github/ISSUE_TEMPLATE/audit.yml` |
| `bug.yml` | bug Issue Form (기존 — SSOT 승격) | `templates/.github/ISSUE_TEMPLATE/bug.yml` |
| `story.yml` | Story Issue Form (신설) | `templates/.github/ISSUE_TEMPLATE/story.yml` |
| `discussion.yml` | Discussion Issue Form (신설) | `templates/.github/ISSUE_TEMPLATE/discussion.yml` |
| `codeforge-improvement.yml` | codeforge-improvement Issue Form (신설) | `templates/.github/ISSUE_TEMPLATE/codeforge-improvement.yml` |
| `config.yml` | Issue selector controller (`blank_issues_enabled` + `contact_links[]`, form 아님) | `templates/.github/ISSUE_TEMPLATE/config.yml` |
| `PULL_REQUEST_TEMPLATE.md` | PR template (현 `.github/` byte-identical mirror — consumer-distributable SSOT) | `templates/.github/PULL_REQUEST_TEMPLATE.md` |

prior art = microsoft/TypeScript 5 forms + config.yml 패턴 (정합도 최고). `templates/.github/` = consumer-distributable SSOT 신설 영역 (현 `.github/` = wrapper self-app, ADR-005 byte-identical). **본 §결정 9.A = declarative enumeration 정정 (normative SSOT)** — 실 file 신설 = Phase 2 carrier (구현 lane, §결정 9.E).

#### §결정 9.B — D4 marker form-level wrap (Amendment 3 §결정 7.A.1 신설 form 적용)

신설 `templates/.github/ISSUE_TEMPLATE/*.yml` + `PULL_REQUEST_TEMPLATE.md` 의 D4 customization marker 적용 = **form 전체 wrap** (Amendment 3 §결정 7.A.1 comment prefix per-filetype + §결정 7.D.3 whole-line anchored + §결정 7.D.1 flat-only 정합):

- `.yml` Issue Form / config.yml = `# BEGIN wrapper-managed` / `# END wrapper-managed` (form 전체를 marker block 으로 wrap — body[] sub-block partial marker 금지)
- `.md` PR template = `<!-- BEGIN wrapper-managed -->` / `<!-- END wrapper-managed -->`
- marker 안 = wrapper SSOT desired state / 밖 = consumer customization preserve (Amendment 3 §결정 7.B verbatim)

**결정 근거 (Axis — form-level wrap vs body[] partial)**: Issue Form yaml = structured spec — body[] sub-block 안 partial marker 는 yaml structure 파편화 risk + GitHub Issue Form parser 가 `#` 주석 무시 → form 전체 wrap 이 의미 정합 (Amendment 3 §결정 7.D.1 nesting 금지 flat-only + Ansible blockinfile flat 패턴 동형). consumer customization = D4 marker 밖 별도 form 추가 또는 marker 부재 form (Amendment 3 §결정 7.C `wholesale_mirror_with_user_visible_loss_report` 재사용 — D1 first-reconcile silent overwrite 0, EPIC-AC-4 보존).

#### §결정 9.C — D1 reconcile = reconcile-protocol-v1 §4.7 SSOT 재사용 (재구현 0)

D1 `.github/` 영역 consumer reconcile = reconcile-protocol-v1 v1.4 §4.7 `overlay_reconcile_implementation_binding` (marker-aware 2-way / `wholesale_mirror_with_user_visible_loss_report`) SSOT 재사용 — `.github/` 영역 area handler 추가 (algorithm 재구현 0, path 매핑만 신규). reconcile-protocol-v1 v1.6 §4.9 `coverage_fan_out_implementation_binding.d1_issue_pr_template_fan_out.reconcile_reuse` verbatim cross-ref. consumer (예: mctrader 5 repo) `.github/ISSUE_TEMPLATE/` marker 부재 시 first-reconcile = wholesale mirror + loss report (silent overwrite 0).

#### §결정 9.D — D2 branch protection FORM (b) + ADR-066 무변경 (F-P1-A 해소, cross-ref)

D2 = `templates/scripts/setup-branch-protection.sh` FORM (b) (manifest 합성 + dry-run preview only, gh api PUT = 0 — 실 등록 = consumer admin operator manual OOS). GitHub API write 자체 0 → fine-grained PAT `Administration:write` 불요 → **ADR-066 §결정 2 scope 5종 무변경 (ADR-066 무접촉)**. Codex TP#4 F-P1-A (D2 credential gap, P1 hidden-assumption) 해소 = scope-down OOS = least-privilege ratchet-safe (ADR-064 minimal-change). 본 §결정 9 = D1 Issue Forms enumeration carrier 가 primary — D2 FORM (b) ADR-066 무변경 = cross-ref only (reconcile-protocol-v1 v1.6 §4.9 `d2_branch_protection_setup_helper` SSOT, ADR-066 별도 entry 미추가).

#### §결정 9.E — Phase split (Phase 1 = declarative SSOT / Phase 2 = 구현 lane)

Phase 1 (CFP-821 본 PR) = declarative SSOT mandate (본 §결정 9 + ADR-076 §결정 2 표 PR template row + reconcile-protocol-v1 v1.6 §4.3 (h)/§4.9 + MANIFEST.yaml row + change-plan + Story §3.1/§7/§11 미러링 — pure design-SSOT, template/script/doc 실 file 0건, CFP-743/744/745/820 선례 정합). Phase 2 (별 PR, 구현 lane) = `templates/.github/ISSUE_TEMPLATE/*.yml` 5종 + `config.yml` + `templates/.github/PULL_REQUEST_TEMPLATE.md` 실 file + `.github/` byte-identical self-app + `templates/scripts/setup-branch-protection.sh` (FORM (b)) + `docs/script-boundary.md` + `docs/consumer-guide.md` §2 line 472/814 enumeration 정정 + §N D2 operator manual 절차 + reconcile-overlay.sh `.github/` area handler 실 연계.

#### §결정 9.F — mechanical enforcement (중복 codification 회피)

본 §결정 9 = consumer adoption protocol enumeration 정정 + D4 marker form-level wrap declarative mandate. D4 marker mechanical lint = Amendment 3 §결정 7.D `wrapper-managed-block` evidence-check entry (blocking-on-pr tier, frontmatter `mechanical_enforcement_actions[]` 이미 등재) 가 cover (신설 form 도 동일 lint 적용). 본 Amendment 5 측 별도 mechanical action 신설은 **중복 codification 회피** (ADR-065 §결정 5 "cross-ref only" 정합) — ADR-027 frontmatter `mechanical_enforcement_actions[]` = Amendment 2/3 entry 보존, Amendment 5 별도 entry 미추가 (Amendment 3 §결정 7.D `wrapper-managed-block` entry 가 D4 marker SSOT). D3 script boundary mechanical lint = §3.3 OOS 별도 follow-up Issue (codeforge-improvement (k) bash top-level local lint — ADR-064 minimal-change, Story scope creep 회피).

### 해소 기준 정합

ADR-027 frontmatter `is_transitional: false` (permanent policy, 기존 §"해소 기준" = "N/A — permanent policy" verbatim). Amendment 5 = consumer adoption 시 Issue Forms enumeration 정정 (3종 → 5 forms + config.yml) + D4 marker form-level wrap cross-ref = governance 강화 방향 ratchet — ADR-058 §결정 5 sunset_justification 불요 (강화 방향, ADR-064 top-down self-application 정합 — consumer adoption scope 확장 only, weakening 0).

상세 Change Plan: `codeforge-internal-docs/wrapper/change-plans/cfp-821-coverage-fan-out.md`.

Cross-ref:
- [ADR-076](ADR-076-declarative-reconciliation-upgrade.md) §결정 2 — Wrapper SSOT 영역 enumeration scheme (본 Amendment 5 sibling carrier: ADR-076 §결정 2 표 PR template row append 동반 — Issue templates row 동형 `template export — consumer overlay 시점 byte-identical mirror`)
- `docs/inter-plugin-contracts/reconcile-protocol-v1.md` v1.6 §4.9 `coverage_fan_out_implementation_binding` — D1/D2/D3 fan-out binding SSOT (§결정 9.A-9.D verbatim cross-ref)
- ADR-027 Amendment 3 §결정 7.A.1 / 7.B / 7.C / 7.D.1 / 7.D.3 — D4 marker syntax (본 Amendment 5 §결정 9.B 가 신설 form 에 적용 — comment prefix per-filetype + whole-line anchored + flat-only)
- [ADR-066](ADR-066-pat-rotation-policy.md) §결정 2 — scope 5종 무변경 (D2 FORM (b) — Administration:write grant 0, F-P1-A 해소 = scope-down OOS, 본 Amendment 5 = ADR-066 무접촉 cross-ref only)
- [ADR-024](ADR-024-story-scoped-branch-policy.md) Amendment 2 §결정 A·C — branch-protection-manifest SSOT (D2 setup-branch-protection.sh = §결정 C 운영 규칙 mechanical helper, ADR-024 Amendment 6 회피 — 본문 무변경)
- [ADR-005](ADR-005-plugin-self-application-na-standardization.md) — `templates/.github/*` ↔ `.github/*` byte-identical self-app (D1 Phase 2)
- [ADR-064](ADR-064-decision-principle-mandate.md) §self-application — Amendment 5 = consumer adoption scope 확장 강화 방향 only (신규 ADR 회피 + D2 scope-down least-privilege ratchet-safe, weakening 0)
- `docs/consumer-guide.md` §2 line 472/814 enumeration 정정 + §N D2 operator manual — consumer runbook (Phase 2 carrier)

## Amendment 6 — consumer adoption detection signals 4-way truth-table SSOT (CFP-899)

**Effective**: 2026-05-18 (CFP-858 Wave 4 sub-Epic S2 Phase 1 PR merged 시점).

**Carrier**: CFP-899 (Wave 4 sub-Epic CFP-858 S2 — consumer-applicability filter). Parent Epic CFP-858 (reconcile wholesale-mirror fix). Sibling carrier: ADR-083 신설 §결정 1 4-way truth-table (wrapper-side filter SSOT) + reconcile-protocol-v1 v1.9 §4.12 `consumer_applicability_filter_binding` block + MANIFEST.yaml v1.8 → v1.9 row update.

본 Amendment = ADR-027 §결정 1 (bootstrap 검증 책임 = wrapper plugin overlay/hooks/) + Amendment 3 §결정 7 (D4 customization marker) + Amendment 4 §결정 8 (codeforge.version_pin schema detection) 정합 — consumer adoption signal SSOT 영역 확장 (detection 차원 추가). ADR-027 = consumer-side signal SSOT (검증 항목 정의) / ADR-083 = wrapper-side filter mechanism (검증 결과 적용 mechanism) — **boundary disjoint** invariant 보존.

**ADR collision 회피 (Amendment vs 신규 ADR 판정)**:

- ADR-083 신규 = wrapper-side filter mechanism (4-way enum closed-set + positive whitelist + mixed exemption + fail-closed unknown 의 mechanism SSOT) — 신규 ADR 정당 (별 카테고리 별 super-class)
- ADR-027 Amendment 6 = consumer-side signal SSOT (signal 정의 + signal 의미) — Amendment 정당 (consumer adoption protocol scope 확장)
- 두 ADR sibling carrier 관계 (boundary disjoint) — 단일 ADR 통합 시 consumer-side signal SSOT 와 wrapper-side filter mechanism 가 한 ADR 안 dual-domain 혼재 (ADR-068 I-4 wording SSOT 위배)
- Amendment = ADR-064 top-down ratchet 강화 방향 only (consumer adoption signal scope 확장, weakening 0)

### 결정 10 — consumer adoption detection signals 4-way truth-table (normative SSOT)

#### §결정 10.A — 2-signal cross-product 4-way enum

Consumer adoption detection signals = filesystem-only **2-signal cross-product**:

| Signal A: `.claude-plugin/plugin.json` 존재 | Signal B: `.claude/_overlay/project.yaml` 존재 | repo_kind | semantic |
|---|---|---|---|
| ✅ | ❌ | `plugin` | wrapper-only repo (codeforge family plugin 자체 — repo 가 plugin SSOT, consumer overlay 부재) |
| ❌ | ✅ | `consumer` | consumer repo (codeforge plugin 사용자 — consumer overlay 활성, plugin SSOT 부재) |
| ✅ | ✅ | `mixed` | dogfood repo (codeforge wrapper repo 자체 — plugin SSOT + 자기 자신의 consumer overlay self-app) |
| ❌ | ❌ | `unknown` | signal 부재 (consumer bootstrap 미완료 또는 비-codeforge repo) |

**4-way enum closed-set**: `plugin` / `consumer` / `mixed` / `unknown`. open-set 확장 (예: `library` / `monorepo` / `archived` 등) = 별 ADR carrier 영역 (본 Amendment scope 외).

#### §결정 10.B — Filesystem-only invariant (network call 0)

본 2-signal 모두 consumer-side filesystem 안 — **network call 0 / gh api 0 / marketplace.json membership check 0**:

- (a) **Offline-first invariant** — ADR-066 PAT scope 최소화 정합 (consumer adoption protocol 가 cross-repo PAT 의존 시 enterprise org `default_workflow_permissions: read` 차단 영역 graceful degradation 의무 발생, ADR-027 Amendment 2 §결정 6 fallback path 패턴 의존성 증가)
- (b) **Trust boundary 명확** — filesystem-only = consumer 권한 area only / cross-repo trust 영역 0 (signal spoofing surface 최소)
- (c) **Primary signal 단일 read 비용** — file existence check (`Test-Path` / `[[ -f ... ]]`) 만 = O(1) syscall, < 1ms

`marketplace.json` 영역 cross-repo gh api 는 본 ADR + ADR-083 scope 외 (별 ADR carrier 발의 시 enterprise org 차단 영역 graceful degradation 의무 검토).

#### §결정 10.C — Signal semantic invariant

각 signal 의 의미 invariant:

| Signal | Schema SSOT | Detection mechanism | semantic |
|---|---|---|---|
| `.claude-plugin/plugin.json` | Claude Code plugin spec (external — anthropic 제공) | `[[ -f .claude-plugin/plugin.json ]]` (existence check only — content parsing 미요구) | "본 repo = Claude Code plugin SSOT" (mclayer/plugin-codeforge / mclayer/plugin-codeforge-{requirements,design,develop,test,review,pmo} 등) |
| `.claude/_overlay/project.yaml` | ADR-027 §결정 1 / ADR-027 Amendment 4 §결정 8 (codeforge.version_pin schema) | `[[ -f .claude/_overlay/project.yaml ]]` (existence check only — content parsing 미요구) | "본 repo = codeforge consumer (consumer overlay bootstrap 완료)" |

**Existence check only invariant**: content parsing (예: `plugin.json` 안 `name` field 검사 / `project.yaml` 안 `codeforge.version_pin` 검사) 은 본 Amendment scope 외 — 해당 schema 검증은 ADR-027 §결정 1 (`check-bootstrap.{sh,ps1}` Phase 2) + Amendment 4 §결정 8 (version_pin schema detection) 별 trigger 영역. **Signal detection = file existence 만** (분리 invariant).

#### §결정 10.D — wrapper self-app exemption (mixed repo dogfood)

본 wrapper repo (`mclayer/plugin-codeforge`) = mixed repo 분류:

- Signal A (`.claude-plugin/plugin.json`) 존재 — codeforge plugin SSOT 자체
- Signal B (`.claude/_overlay/project.yaml`) 존재 — consumer overlay self-app dogfood (wrapper repo 가 자기 자신의 consumer 영역으로도 동작 — codeforge family dogfood-out policy ADR-013 정합)
- 분류 우선순위 invariant — `mixed` = `plugin` 우선 적용 (filter skip — ADR-083 §결정 3 sibling carrier verbatim)

**self-loop bug 차단**: `consumer` 분류 (consumer signal 활성 + plugin signal 부재) 가 wrapper repo 에 false-positive 적용되면 wrapper dogfood workflow 손실 — Signal A 존재 보장으로 `mixed` 우선 분류가 self-loop 차단 (ADR-083 §결정 6 sibling carrier verbatim).

#### §결정 10.E — fail-closed unknown (silent default 차단)

`repo_kind == "unknown"` (Signal A + Signal B 모두 부재) = **fail-closed** (silent default 차단, no copy + abort with error log) — ADR-083 §결정 4 sibling carrier verbatim. silent default → wrapper-only 무차별 유입 silent harm 재발 (Epic CFP-858 결함 2 root cause) 차단.

**예외 0 invariant**: `--force-unknown-as-consumer` flag 신설 금지 — `hotfix-bypass:consumer-applicability-filter-detection` label 영역 외 (bypass label = PR-time mechanical enforcement 회피용, runtime fail-closed 회피는 위배 vector — ADR-083 §결정 4 sibling carrier verbatim).

#### §결정 10.F — ADR-083 sibling carrier boundary invariant

ADR-083 = wrapper-side filter mechanism SSOT (4-way enum 적용 + positive whitelist + hook insertion point + mechanical action). ADR-027 Amendment 6 = consumer-side signal SSOT (signal 정의 + filesystem-only invariant + semantic invariant + wrapper self-app exemption + fail-closed unknown).

**Boundary disjoint invariant**: 두 ADR 한 ADR 안 dual-domain 혼재 금지 (ADR-068 I-4 wording SSOT 정합). 단일 carrier 통합 시 = consumer-side signal 변경 (예: 새 signal 추가) 이 wrapper-side filter mechanism 변경 영역 으로 의도하지 않은 cascade — disjoint 보존 시 = consumer-side signal scope 확장 (ADR-027 Amendment N) ↔ wrapper-side filter mechanism scope 확장 (ADR-083 Amendment N) 별 carrier 분리 가능.

### 해소 기준 (Amendment 6)

ADR-027 frontmatter `is_transitional: false` (permanent policy, 기존 §"해소 기준" = "N/A — permanent policy" verbatim). Amendment 6 = consumer adoption signal SSOT scope 확장 (detection 차원 추가) = governance 강화 방향 ratchet — ADR-058 §결정 5 sunset_justification 불요 (강화 방향, ADR-064 top-down self-application 정합 — consumer adoption scope 확장 only, weakening 0).

상세 Change Plan: `codeforge-internal-docs/wrapper/change-plans/cfp-899-consumer-applicability-filter.md`.

Cross-ref:
- [ADR-083](ADR-083-consumer-applicability-filter.md) §결정 1-6 — wrapper-side filter mechanism SSOT (boundary disjoint sibling carrier)
- [ADR-076](ADR-076-declarative-reconciliation-upgrade.md) §결정 2 — Wrapper SSOT 영역 enumeration scheme (본 Amendment 6 = ADR-076 §결정 2 11 영역 wholesale_mirror branch 의 consumer-applicability gating layer)
- `docs/inter-plugin-contracts/reconcile-protocol-v1.md` v1.9 §4.12 `consumer_applicability_filter_binding` — 본 Amendment 6 § 결정 10.A-10.F verbatim cross-ref carrier contract
- ADR-027 §결정 1 — bootstrap 검증 책임 = wrapper plugin overlay/hooks/ (본 Amendment 6 = 검증 항목 detection signals 차원 추가)
- ADR-027 Amendment 3 §결정 7 — D4 customization marker (본 Amendment 6 = consumer signal 활성 후 marker block 적용 sequential)
- ADR-027 Amendment 4 §결정 8 — codeforge.version_pin schema detection (본 Amendment 6 = signal existence check / Amendment 4 = signal content schema check, sequential composition)
- ADR-027 Amendment 5 §결정 9 — Issue Forms enumeration 정정 (D1 fan-out, consumer-applicable forms 영역 — 본 Amendment 6 = wrapper-only forms vs consumer-applicable forms filter mechanism 의 signal SSOT)
- [ADR-064](ADR-064-decision-principle-mandate.md) §self-application — Amendment 6 = consumer adoption signal scope 확장 강화 방향 only (신규 ADR-083 = filter mechanism 신설, weakening 0)
- [ADR-082](ADR-082-write-time-self-write-verification-mandate.md) §결정 6 — `mechanical_enforcement_actions: []` declaration-only Wave 1 retain pattern (본 Amendment 6 의 `consumer-applicability-filter-detection` entry status: declaration-only-Wave-1)
- `docs/consumer-guide.md` §N consumer adoption signal detection runbook — consumer-side documentation (Phase 2 carrier)

### Amendment 6 sunset boundary (CFP-1125 carrier)

본 Amendment 6 (§결정 10 consumer-applicability filter 와 ADR-083 wrapper-side filter mechanism disjoint scope 선언) 의 효용은 CFP-1111 walker paradigm 으로 carry.

- **metric**: walker 의 repo-kind detection (`detect-repo-kind.py` 재사용) 이 Amendment 6 detection signals (`.claude-plugin/plugin.json` + `.claude/_overlay/project.yaml` 2-signal cross-product) 동일 truth-table 재사용 + D4 customization marker block (Amendment 3) preserve invariant 0 silent overwrite / N walk 실행
- **who**: walker repo-kind detection hook + walker per-step `customization_marker_preserve: true` flag
- **how**: walker integration test 안 4-way enum 정확 분류 + D4 marker pair preserve verify

**cross-ref**: [β2 audit (#1113)](https://github.com/mclayer/plugin-codeforge/issues/1113) Anchor 4 LOSSLESS 판정. D4 marker preserve = CFP-1111 §3 결정 3 C 명시 + Sister CFP-1115 (β5 ADR-027 Amendment 7) 가 D4 marker block imperative walk 정합 별 carrier.

**영역 분리 명시**: 본 sunset boundary 는 Amendment 6 영역 한정 — ADR-027 본체 frontmatter `is_transitional: false` (permanent policy) 무변경 + 다른 amendment (2/3/4/5/7) 영역 영향 0. ratchet 강화 only (Wave-1 detection signals SSOT → Wave-4 walker integration test 안 4-way enum 정확 분류 + D4 marker pair preserve verify), 약화 0건 — ADR-058 §결정 5 ratchet 강화 only 정합.

#### sunset_executed (CFP-1186, 2026-05-22) — Amendment 6 detection-signals 영역 한정

**상태**: Amendment 6 detection-signals 영역 Sunsetted — 4-way repo-kind detection signals (`.claude-plugin/plugin.json` + `.claude/_overlay/project.yaml` 2-signal cross-product truth-table) 효용이 imperative walker 로 lossless carry 완료됨.

carry 증거 (β2 audit Anchor 4 LOSSLESS 확인):
- walker repo-kind detection hook (`detect-repo-kind.py` 재사용) = Amendment 6 detection signals 동일 truth-table 재사용
- D4 customization marker block (Amendment 3) preserve invariant 0 silent overwrite / N walk 보존 (CFP-1111 §3 결정 3 C 명시 + walker `customization_marker_preserve: true` flag)
- walker integration test 안 4-way enum 정확 분류 + D4 marker pair preserve verify 완료 (walker per-step `applicable_to: {consumer/wrapper/both}` filter)

**is_transitional 무변경**: `false` 유지 (ADR-027 본체 + Amendment 3/4/5/7/9 영구 불변). 본 sunset = Amendment 6 § 결정 10 detection-signals 영역 만 (carry 완료 선언).

**본 ADR 본문 삭제 금지**: Sunsetted = 해당 영역의 carry 완료 선언. 본문은 historical record 로 영구 보존. Amendment 9 (CFP-1177) 및 기타 amendment 영향 0.

## Amendment 7 — consumer adoption 시 project.yaml `deploy.*` schema 확장 (CFP-1059)

**Effective**: 2026-05-20 (CFP-1059 Story-1 Phase 1 PR merge 시점).

**Carrier**: CFP-1059 Story-1 (ADR-023 Amendment 1 + ADR-087 + ADR-088 sibling carrier). 본 Amendment 7 = consumer adoption signal SSOT 영역 확장 — codeforge-deploy lane 신설 정합 (production cutover-touching consumer Story 진입 시 deploy 설정 SSOT 의무).

### 결정 11 — consumer overlay `.claude/_overlay/project.yaml` `deploy.*` schema 확장 (5 sub-field)

기존 §결정 1 (bootstrap 검증 책임) + Amendment 4 §결정 8 (`codeforge.version_pin` schema detection) + Amendment 6 §결정 10 (4-way detection signals) 정합. 본 Amendment 7 = `deploy.*` schema 영역 신설.

#### §결정 11.A — `deploy.*` 5 sub-field 정의

```yaml
# .claude/_overlay/project.yaml
deploy:
  host_mapping:                   # blue / green stack host mapping (ADR-087 §결정 5 step 1 bound)
    blue:  <host_alias>           # blue stack host (예: `production-blue`)
    green: <host_alias>           # green stack host (예: `production-green`)
  docker_hub:                     # Docker registry SSOT (ADR-087 §결정 5 step 2 bound)
    registry: <registry_url>      # 예: `docker.io` / `ghcr.io` / `<private-registry>`
    namespace: <namespace>        # 예: `mclayer`
    image_repo: <image_repo>      # 예: `mctrader-engine`
  traefik:                        # Traefik routing SSOT (ADR-087 §결정 5 step 4 traffic switch bound)
    network:           <docker_network_name>  # 예: `traefik-public`
    entrypoint:        <entrypoint>           # 예: `websecure`
    cert_resolver:     <resolver>             # 예: `letsencrypt`
    blue_label_prefix:  "traefik.http.routers.<service>-blue"
    green_label_prefix: "traefik.http.routers.<service>-green"
  1password:                      # 1Password secret SSOT (ADR-087 §결정 5 env injection bound, ADR-014 결정 2 env isolation 정합)
    vault: <vault_name>           # 예: `production`
    item:  <item_name>            # 예: `mctrader-engine-env`
    op_cli_path: <op_cli_path>    # 예: `/usr/local/bin/op` — `op` CLI binary path
  ssh_targets:                    # SSH target SSOT (ADR-087 §결정 5 step 1/2/3/4/5/6 모두 SSH execution path)
    - host:      <ssh_host>       # 예: `production-blue.example.com`
      user:      <ssh_user>       # 예: `deploy`
      port:      <ssh_port>       # default 22
      key_path:  <ssh_key_path>   # 예: `~/.ssh/production_ed25519`
      stack:     <blue|green>     # host_mapping cross-ref
```

#### §결정 11.B — 5 sub-field semantic invariant

| Sub-field | Mandatory | Schema invariant | ADR cross-ref |
|---|---|---|---|
| `host_mapping` | YES (production cutover-touching Story 진입 시) | `{blue, green}` 2-key dict (single-host blue-green deployment) | ADR-087 §결정 5 step 1+5+7 (blue provision / green decommission / blue retention) |
| `docker_hub` | YES | `{registry, namespace, image_repo}` 3-key dict | ADR-087 §결정 5 step 2 (image pull / tag) |
| `traefik` | YES | `{network, entrypoint, cert_resolver, blue_label_prefix, green_label_prefix}` 5-key dict | ADR-087 §결정 5 step 4 (traffic switch) |
| `1password` | YES | `{vault, item, op_cli_path}` 3-key dict | ADR-087 §결정 5 env injection (ADR-014 결정 2 env isolation 정합) |
| `ssh_targets` | YES | array of `{host, user, port, key_path, stack}` — minimum 2 entries (blue + green) | ADR-087 §결정 5 step 1-6 all SSH execution path |

#### §결정 11.C — Schema detection mechanism (filesystem-only, Amendment 6 §결정 10.B 정합)

- **Detection signal**: `[[ -f .claude/_overlay/project.yaml ]] && yq '.deploy' .claude/_overlay/project.yaml | grep -q "host_mapping"` (existence + sub-field non-null check)
- **Existence check only invariant** (Amendment 6 §결정 10.C 정합) — content semantic verify (예: `host_mapping.blue` 가 reachable 한 host 인지) 는 본 schema scope 외 (runtime DeployPL 검증 책임 영역)
- **Network call 0** — filesystem-only (Amendment 6 §결정 10.B offline-first invariant 정합)

#### §결정 11.D — fallback semantic (warning-first)

- `deploy.*` 미등록 + Story `production_cutover_touching: false` → silent skip (production cutover-touching 영역 아닌 Story 는 deploy.* schema 무관)
- `deploy.*` 미등록 + Story `production_cutover_touching: true` → **warning emit** (DeployPL spawn 전 consumer 에 schema 작성 안내)
- `deploy.*` 등록 + sub-field 누락 (`host_mapping.blue` 미존재 등) → **blocking-on-pr enforce** (DeployPL 진입 차단, Story §12 Deploy section 작성 불가)
- Amendment 4 §결정 8 `codeforge.version_pin` fallback semantic 답습 (warning-first → 등록 후 blocking, ADR-027 fallback path 패턴)

#### §결정 11.E — wrapper self-app exemption (Amendment 6 §결정 10.D 정합)

wrapper repo (`mclayer/plugin-codeforge`) = mixed repo 분류 → `deploy.*` schema 검증 skip (self-loop 차단 — wrapper repo 가 자기 production cutover 영역 아님, ADR-088 §결정 5 wrapper-self-app N/A 정합).

#### §결정 11.F — orthogonality invariant (Amendment 4 §결정 8 patterns 답습)

- `deploy.*` 가용성 ≠ `codeforge.version_pin` 가용성 (independent signals, conflate 금지)
- `deploy.*` 가용성 ≠ `bootstrap.fallback_mode` 가용성 (Amendment 2 §결정 6 fallback path 패턴 — independent signals)
- 모든 sub-field 가 independent (예: `1password` 만 등록 + `traefik` 미등록 = 가능 — Story §12 Deploy section author 시 `deploy.traefik` 영역 만 blocking)

### 해소 기준 (Amendment 7)

ADR-027 frontmatter `is_transitional: false` (permanent policy). Amendment 7 = consumer adoption signal scope 확장 (`deploy.*` schema 영역 추가) = governance 강화 방향 ratchet — ADR-058 §결정 5 sunset_justification 불요 (강화 방향, ADR-064 top-down self-application 정합 — consumer adoption scope 확장 only, weakening 0).

상세 Change Plan: `codeforge-internal-docs/wrapper/change-plans/cfp-1059-deploy-lane-and-lifecycle-extension.md` §3.4 (consumer overlay schema).

### Cross-references

- ADR-023 Amendment 1 (CFP-1059 / Story-1 sibling carrier — lane plugin 6 → 8 확장)
- ADR-087 (CFP-1059 / Story-1 신설 — Deploy lane as 7th lane plugin, §결정 5 6-step Deploy procedure SSOT — 본 Amendment 7 의 5 sub-field 가 6-step 의 input)
- ADR-088 (CFP-1059 / Story-1 신설 — Deploy Review lane + ProductionEvidence transfer)
- ADR-014 결정 2 (env isolation — `1password` sub-field 정합)
- ADR-072 §결정 5 (epic-cutover-gate-evidence-quad-check — production cutover-touching Epic scope 정합)
- ADR-027 §결정 1 (bootstrap 검증 책임 — 본 Amendment 7 = 검증 항목 `deploy.*` 차원 추가)
- ADR-027 Amendment 4 §결정 8 (`codeforge.version_pin` schema detection — 본 Amendment 7 의 fallback semantic 패턴 답습)
- ADR-027 Amendment 6 §결정 10 (4-way detection signals — 본 Amendment 7 = `deploy.*` signal SSOT 확장)
- ADR-083 §결정 1 (consumer-applicability filter 4-way enum — consumer repo 만 schema 검증 fire)
- ADR-064 §self-application top-down ratchet (강화 방향 only, 약화 0)
- ADR-058 §결정 5 sunset_justification (ratchet 강화 방향 = sunset 면제, is_transitional: false 보존)

## Amendment 9 — customization marker block paradigm-agnostic preserved layer codify (CFP-1177)

**Effective**: 2026-05-21 (CFP-1177 Story-8 Phase 2 PR merge 시점).

**Carrier**: CFP-1177 Story-8 (CFP-1111 Wave 3 consumer overlay apply orchestration). 본 Amendment 9 = Amendment 3 §결정 7 의 D4 customization marker invariant 를 imperative walk apply 경로로 scope 확장 codify. additive only (기존 declarative 경로 무변경, supersede 0). §결정 12 신설.

**Amendment 8 (CFP-1125) 와의 관계 (declaration → realization, drift 0)**: Amendment 8 = D4 marker preserve invariant 의 효용이 walker paradigm 으로 carry 됨을 **declaration-only** 로 명시 (Amendment 6 영역 sunset boundary declarative — `walker per-step customization_marker_preserve flag` 영역). Amendment 8 본문이 forecast 한 "sister CFP-1115 (β5) D4 marker block imperative walk 정합 별 carrier" 의 **실 realization** = 본 Amendment 9 (CFP-1177 이 #1115 흡수 — apply_overlay_file 구현 + DRY 의무 + integrity check). Amendment 8 본문의 "ADR-027 Amendment 7" label = stale forecast (해당 amendment slot 은 CFP-1059 deploy.* schema 가 점유) — 실 realization slot = 본 Amendment 9. 양 amendment boundary disjoint: Amendment 8 = declaration (효용 carry 선언) ↔ Amendment 9 = realization (imperative apply 구현 codify). 동일 invariant 의 declaration↔implementation 관계 — SSOT drift 0 (ADR-068 I-2 cross-module propagation completeness 정합).

**ADR collision 회피 (Amendment vs 신규 ADR 판정)**: ADR-027 = consumer adoption protocol SSOT — D4 customization marker (Amendment 3 §결정 7) 의 scope 확장. 동일 invariant 를 imperative 경로에도 적용하는 것은 Amendment 3 §결정 7.B/7.C 의 "declarative-specific" 제약을 "paradigm-agnostic" 으로 넓히는 ratchet 강화 방향. 신규 ADR 신설 시 D4 marker 의 2-경로 SSOT 분산 (ADR-068 I-4 wording SSOT 위배). Amendment = ADR-064 top-down ratchet 강화 방향 only (scope 확장, weakening 0).

### 결정 12 — customization marker block paradigm-agnostic preserved layer (normative SSOT)

#### §결정 12.A — Paradigm-agnostic invariant 확장

Amendment 3 §결정 7.B (marker 안 = wrapper SSOT wins, 밖 = consumer preserve) + §결정 7.C (MARKER_NONE = wholesale + user-visible loss report, silent overwrite 0 — EPIC-AC-4) 가 다음 양 경로 모두에 동일 적용됨을 normative codify:

| 경로 | 구현 | 상태 |
|---|---|---|
| 선언적 reconcile | `scripts/reconcile-overlay.sh` | 기존 (Amendment 3 carrier) |
| 명령적 walk apply | `scripts/lib/walk_plan.py` `apply_overlay_file` | 신설 (CFP-1177 Story-8 carrier) |

**Invariant 3종 (양 경로 동일)**:

1. **marker 안 = wrapper SSOT unconditionally wins** — consumer 변경 무시. `base_content` 는 marker 안 merge 에 사용되지 않는다 (by-design — reconcile-protocol-v1 시그니처 호환성 목적 보존).
2. **marker 밖 = consumer byte-identical 보존** — integrity fingerprint check 의무 (위반 시 abort-before-touch: consumer_content 원본 fallback, filesystem write 0).
3. **MARKER_NONE = wholesale wrapper mirror + user-visible loss report** — silent overwrite 0 (EPIC-AC-4). `loss_occurred: True` + `loss_report` non-empty 의무.

#### §결정 12.B — Walk apply DRY 의무 (merge_with_marker primitive 재사용)

`apply_overlay_file` (walk_plan.py) = `merge_with_marker` primitive 재사용 의무. marker logic 독립 재구현 금지 — 2-경로 분기 시 invariant drift 위험 (DRY 원칙 + ADR-068 I-4 wording SSOT 정합). `merge_with_marker` 가 "integrity fingerprint check 의무 (호출자 책임)" 을 docstring 에 위임 → `apply_overlay_file` 이 그 책임 이행 (Step 2 integrity check).

#### §결정 12.C — 순수 함수 invariant (filesystem 접촉 0)

`apply_overlay_file` = 순수 함수 (문자열 입력 → `OverlayApplyResult` 출력). filesystem write 0 — filesystem write + loss-report 표면화 = .sh dispatcher 책임. `reconcile-overlay.sh` 의 shell 오케스트레이션 / Python 계산 분리 패턴 답습.

#### §결정 12.D — integrity abort-before-touch analog

integrity 위반 (merged 결과의 marker-outside 가 consumer_content marker-outside 와 byte-identical 불일치) 시:
- `merged_content = consumer_content` (원본 fallback, corrupted merge 미발행)
- `integrity_ok = False`
- `integrity_violation_reason` non-empty (위반 사유 명시)
- filesystem write 0 (abort-before-touch analog — `reconcile-overlay.sh §7.4.1(g)` verbatim 정합)

#### §결정 12.E — mechanical enforcement (중복 codification 회피)

`wrapper-managed-block` evidence-check entry (Amendment 3 §결정 7.D frontmatter `mechanical_enforcement_actions[]` 이미 등재, blocking-on-pr tier) 가 consumer overlay 파일의 marker block 정합성 lint 를 cover. 본 Amendment 9 측 별도 mechanical action 신설 = 중복 codification 회피 (ADR-065 §결정 5 cross-ref only 정합). walk_plan.py 는 `.py` (lint file-type filter `.yml|.yaml|.sh|.md` 미해당) → `scripts/check-wrapper-managed-block.sh` SKIP_LIST 추가 불요.

### 해소 기준 정합

ADR-027 frontmatter `is_transitional: false` (permanent policy). Amendment 9 = D4 marker invariant scope 확장 (declarative-only → declarative+imperative) = governance 강화 방향 ratchet — ADR-058 §결정 5 sunset_justification: ratchet 강화 방향 전용 exemption 정합. bats TC 19/19 GREEN = metric. apply_overlay_file 함수 walk_plan.py §f = who. _split_consumer_outer round-trip byte-identical verify = how.

Cross-ref:
- ADR-027 Amendment 3 §결정 7.B/7.C/7.D — D4 marker syntax + invariant SSOT (본 Amendment 9 = scope 확장 carrier, 기존 §결정 7 무변경)
- ADR-027 Amendment 8 (CFP-1125, amendment_log id 8) — D4 marker preserve walker carry **declaration-only** (본 Amendment 9 = 그 declaration 의 실 realization, declaration↔implementation disjoint, drift 0)
- `scripts/lib/walk_plan.py` `apply_overlay_file` + `OverlayApplyResult` + `merge_with_marker` — 구현 SSOT (CFP-1177 Story-8)
- `tests/scripts/cfp-1177/cfp-1177-overlay-apply.bats` — 19 TC TDD suite (MARKER_VALID / MARKER_NONE / integrity fallback / signature / frozen)
- [ADR-076](ADR-076-declarative-reconciliation-upgrade.md) — declarative reconcile SSOT (기존 경로 무변경, 본 Amendment 9 = disjoint scope 확장)
- `docs/inter-plugin-contracts/imperative-walker-protocol-v1.md` — walk apply 계약 SSOT (paradigm carrier)
- [ADR-058](ADR-058-adr-sunset-criteria-mandate.md) §결정 5 — sunset_justification ratchet 강화 방향 exemption
- [ADR-064](ADR-064-decision-principle-mandate.md) §self-application — ratchet 강화 방향 only (scope 확장, weakening 0)

## Amendment 10 — Secondary trigger entry-gate: codeforge 선언 + 미초기화 → bootstrap-first (CFP-2243)

**Effective**: 2026-06-15 (CFP-2243 Phase 1 wrapper PR merge 시점 — ADR Proposed→Effective, ADR-032 / Amendment 1 2-stage 패턴 정합).

**Carrier**: CFP-2243 (dogfood, wrapper-self-application). single Story (Phase 1 문서/ADR PR + Phase 2 코드 PR). not part of Epic.

본 ADR §결정 2 (3-trigger enforcement model) 의 **Secondary trigger (UserPromptSubmit hook)** 가 가진 구멍을 메운다. 기존 Secondary trigger (`overlay/hooks/userprompt_reminder.py` `CHANGE_PATTERNS`) 는 "변경 동사" (`구현|만들|수정|fix|implement|...`) 만 검출 → 미초기화 consumer 에서 사용자가 codeforge 사용을 선언(설계/brainstorm/스토리 요청)했을 때 **bootstrap 미충족을 surface 하지 못하고** `superpowers:brainstorming` 으로 silent fallback (Issue #2243). 이는 §컨텍스트 line 90 사용자 원 directive ("처음 시작시 codeforge 사용 선언시 의존 관계 플러그인 설치 등 ... codeforge 반영 자체에 필요") 의 의도적 seed 가 메커니즘으로 실현되지 않은 gap.

본 amendment = ADR-027 §결정 2 Secondary trigger 의 **entry-gate sub-trigger 확장** (additive, supersede 아님). §결정 13 신설. ratchet 강화 방향 only.

### 결정 13 — codeforge 의도 선언 + 미초기화 → bootstrap-first 불변식 (normative SSOT)

#### §결정 13.A — intent 감지 범위 (변경동사 ∪ codeforge 고유신호)

발화 1차 조건 = 사용자 prompt 가 다음 2 class 중 하나 이상 매치:

| class | enum (ReDoS-free 단순 alternation) | matching 계약 | 근거 |
|---|---|---|---|
| **변경 동사** | `구현 / 만들 / 수정 / 짜 / 고쳐 / 추가 / fix / implement / refactor / create / add / build / change / update / modify / edit / write` | substring 매치 허용 (기존 동작 답습) | 기존 Secondary trigger `CHANGE_PATTERNS` verbatim 정합 (overlay/hooks/userprompt_reminder.py L36-43) |
| **codeforge-distinctive marker** | `codeforge / story / 스토리 / epic / lane / 레인` | **단독 매치 = intent 허용** (해당 토큰만으로 codeforge 선언 확정) | 신규 — codeforge 사용 선언 시점 포착 (Issue #2243 핵심 gap). value judgment A 사용자 확정 enum. distinctive = 일상 한국어에서 codeforge 외 의미 충돌 없음 |
| **generic 명사** | `설계 / 아키텍처` | **단독 매치 금지** — codeforge-distinctive marker **co-occurrence 시에만** intent 인정 | generic 한글 명사. 한글에는 `\b` word-boundary 가 없어 `상세설계` / `아키텍처 책` 등 무관 substring 이 false-positive 발화 → distinctive co-occurrence 로만 게이팅 (F2 해소) |

**matching 계약 (ADR 고정 — 구현 regex 위임 금지)**:
- 변경 동사 ∪ codeforge-distinctive marker 중 **1+ 단독 매치** = intent TRUE.
- generic 명사(`설계`/`아키텍처`)는 **codeforge-distinctive marker(또는 변경 동사) 동반 시에만** intent 기여. 단독 generic 명사 매치 = intent FALSE (false-positive 억제).
- 한글은 `\b` 부재 → substring 매치가 generic 명사를 오발화시키므로, generic 명사는 co-occurrence gate 로 격리. distinctive marker / 변경동사는 substring 허용 (오발화 위험 낮음 — distinctive 어휘).

2 class (변경동사 ∪ distinctive marker) 의 **합집합 (OR)** = intent 매치. generic 명사는 위 co-occurrence 계약을 통과할 때만 가산. (단 본 §13.A 1차 조건만으로는 발화하지 않음 — §13.B AND-gate 와 결합해야 발화. false-positive 이중 억제.)

#### §결정 13.B — AND-gate (발화 ⟺ intent ∧ 미초기화 greenfield)

발화 = 다음 **모두** 충족 시에만 (AND-gate):

1. **intent 매치** (§13.A) — 변경동사 ∪ codeforge-distinctive marker (generic 명사는 co-occurrence 시에만)
2. **detect-repo-kind exit 3 (`unknown`)** — `.claude-plugin/plugin.json` AND `.claude/_overlay/project.yaml` **양 신호 부재** = 진짜 greenfield. `templates/scripts/detect-repo-kind.py` (무변경 재사용) 가 exit 3 반환 시에만. consumer(exit 1, overlay 존재=초기화됨) / mixed(exit 2, wrapper-self) / plugin(exit 0, plugin.json 존재) 에서는 silent.
3. **`docs/adr` 부재 AND `archive/adr` 부재** — exit 3 이 plugin.json·overlay 양 부재를 이미 함의하므로 그 2 신호 중복검사 불요. skill 기존 fallback 조건(SKILL.md 적용조건 = project.yaml OR docs/adr OR archive/adr)과 정합 위해 docs/adr·archive/adr 부재만 추가 검사
4. **not-bypassed** (§13.E)

**"미초기화" SSOT 정의 = 4 부재** (detect truth-table 기준 단일화 — P1 해소):
> 미초기화(greenfield) ⟺ `.claude-plugin/plugin.json` 부재 ∧ `.claude/_overlay/project.yaml` 부재 ∧ `docs/adr` 부재 ∧ `archive/adr` 부재.
> 앞 2 부재(plugin.json + project.yaml) = detect-repo-kind `unknown`(exit 3) 의 **정확한 등가** (detect-repo-kind.py:99-115 실측 — `has_plugin=False ∧ has_overlay=False` 일 때만 unknown). 뒤 2 부재(docs·archive/adr)는 §결정 13.B 조건 3 의 추가 게이트. **이 4 부재 정의는 hook §13.B 술어 = SKILL.md 미초기화 판정 = consumer-guide greenfield 정의가 byte-동일 (I-4 wording SSOT)**.
> ⚠ `plugin.json` **존재** = detect plugin(exit 0) 또는 mixed(exit 2) → 본 gate 대상 아님(침묵). plugin.json 부재 항목을 미초기화 판정에서 누락하면 `plugin.json 존재 + overlay 부재 + ADR dir 부재`(scaffold 직후 plugin repo)를 consumer bootstrap 으로 오유도하는 술어 drift 발생 — 이를 차단하기 위해 plugin.json 부재가 미초기화 정의의 1번째 conjunct.

이 AND-gate = value judgment A 의 "repo_kind=unknown(greenfield) AND overlay/adr 부재" 정합. 미초기화에서만 발화 → 초기화 후 영구 침묵 (reflex 자연 억제). **detect-repo-kind.py 무변경 invariant 보존** (2 signal 만 검사하는 기존 SSOT 그대로 subprocess 호출).

**wrapper-self = mixed(exit 2) 침묵 (P3)**: wrapper repo 자신(`.claude-plugin/plugin.json` + `.claude/_overlay/...` overlay 양존, dogfood) = detect-repo-kind **mixed(exit 2)** → 조건 2(exit 3) 불충족 → gate 침묵. wrapper 자기 세션은 codeforge dogfood 작업이므로 bootstrap 유도가 무의미·간섭 → **의도된 무발화** (dogfood 무간섭 invariant). plugin.json 존재만으로도 4 부재 정의(1번째 conjunct) 가 깨지므로 이중으로 침묵 보장.

#### §결정 13.C — 발화 = warning inject only, exit 0 (hard-block 권한 보유하나 정책적 미사용)

발화 시 출력 = 정적 system-reminder context inject (사용자 prompt echo 0):
- bootstrap 미충족 상태 surface
- `scripts/bootstrap-consumer.sh` 초기화 안내
- GitHub remote 부재 시 명령 surface (자동 생성 금지 — §13.D)

**hard-block 미사용 = 거버넌스 invariant 에 의한 의도적 설계 결정** (기술적 한계 아님):
- UserPromptSubmit hook 은 기술적으로 exit code 2 또는 JSON `decision:block` 으로 사용자 prompt 를 erase(차단)할 수 있다 (출처: https://code.claude.com/docs/en/hooks.md — UserPromptSubmit hook decision control).
- **그러나 본 훅은 이 block 권한을 쓰지 않는다**: ADR-027 §결정 2 ("Block 아님 — warning inject only" + "enforcement = LLM 측 책임") + ADR-034 D1 (brainstorm = 순수 옵션). 사용자 prompt erase = 수용 불가.
- → **모든 경로 exit 0 + plain stdout context inject 만**. (DesignReview 의 "왜 block 안 쓰나" 오해 차단 목적으로 본 §13.C 에 명시.)

**observability — stderr 1-line audit (F4 채택)**:
- 본 훅은 Issue #2243 의 본질(silent fallback) 을 메우는 장치이므로, **회귀로 다시 silent 해진 것을 사후 감지** 할 수 있어야 한다. 이를 위해 발화 경로마다 stderr 에 1줄 audit 을 남긴다:
  - 형식: `[bootstrap-first-gate] fired exit_path=<warn-injected|silent-initialized|silent-bypassed|silent-mixed|silent-plugin>` (한 줄, 고정 prefix).
  - **prompt 내용 echo 0** — 사용자 입력 텍스트는 stderr 에 절대 기록하지 않는다 (korean-english-recovery 의 stderr advisory 동형 — diagnostic only, payload 미포함). PII/secret leak 차단.
  - stderr 이므로 UserPromptSubmit 의 stdout context-inject 채널과 분리 → 사용자 prompt 에 영향 0, exit 0 불변.
- **metric N/A 명시**: 본 훅은 매 prompt 1회 동기 advisory 단발 hook 이다. SLO / throughput / latency budget / error-rate metric = **N/A** (지속 서비스 아님, 단발 stderr 라인 1줄). 관측 = audit 라인 grep 로 충분 (시계열 metric backend 불요).

#### §결정 13.D — GitHub remote 부재 시 자동 생성 금지 (value judgment B)

`bootstrap-consumer.sh` 가 org/repo 감지 실패 (project.yaml 부재 + git remote 부재 → Stage 1 fatal) 하는 greenfield 환경:
- **자동 `gh repo create` 금지**. 부작용 (사용자 GitHub 계정에 repo 생성) = 명시 동의 없이 수행 불가.
- 훅/skill 은 **명령 + 필요 상태 surface + 사용자 확인 후 진행** — Orchestrator 가 확인 대화로 안내.

#### §결정 13.E — bypass env (ADR-027 §결정 3 honor + 전용 단일 flag)

| env | 의미 | 근거 |
|---|---|---|
| `HOTFIX_BYPASS_CODEFORGE=1` + `HOTFIX_BYPASS_REASON="<사유>"` (양 set) | bypass honored (silent skip + stderr audit) | §결정 3 정합 — 우회 surface 분산 차단 |
| `BYPASS_BOOTSTRAP_GATE=1` (단일 flag) | 본 훅 전용 advisory bypass (reason 불요 — advisory warning 이므로) | korean-english-recovery `BYPASS_KOREAN_ENGLISH_RECOVERY` 동형 패턴 |

#### §결정 13.F — wrapper plugin hooks/ 배치 (chicken-and-egg 해결)

본 entry-gate 훅 = **wrapper plugin `hooks/`** 에 배치 (`overlay/hooks/` 아님):
- `overlay/hooks/userprompt_reminder.py` (기존 Secondary trigger) 는 **consumer `.claude/settings.json` 등록 의존** → consumer 가 bootstrap 을 이미 마친 후에만 활성. 미초기화 greenfield 을 **구조적으로 못 잡음** (chicken-and-egg).
- wrapper plugin `hooks/hooks.json` UserPromptSubmit 배열은 **plugin 설치 즉시 활성** (consumer settings.json 등록 불요). → 미초기화 greenfield 의 첫 prompt 부터 발화 가능.
- 이는 SessionStart `check-bootstrap` 이 consumer settings.json 등록 의존이라 greenfield 못 잡는 동일 한계를 wrapper plugin hooks/ 로 해소.

**dispatch 형식 (F5 — additive entry, 실측 정합)**:
- `hooks/hooks.json` 의 `UserPromptSubmit` 배열(실측 `hooks/hooks.json:62-71`, 현재 `korean-english-recovery` 1 entry)은 전 hook 을 `run-hook.cmd <name>` polyglot shim 으로 dispatch 한다.
- 본 훅 추가 = 그 배열에 **`"${CLAUDE_PLUGIN_ROOT}/hooks/run-hook.cmd" bootstrap-first-gate` 1 entry append** (`async:false`). 기존 entry 무변경 (additive).
- shim(`hooks/bootstrap-first-gate`, 확장자 없음) = **korean-english-recovery shim 패턴 답습**: ① `BYPASS_BOOTSTRAP_GATE=1` 시 `exit 0` ② `python3`→`python` 탐색, 둘 다 부재 시 `exit 0` (fail-safe, 사용자 입력 차단 안 함) ③ `exec "$PY" "$DIR/bootstrap-first-gate.py"` (core 위임). bash 단발 + python core 분리 = sibling shim 동형.

#### §결정 13.G — D1 옵션성 보존 (brainstorm 진입 차단 아님)

ADR-034 D1 (brainstorm = 순수 옵션, CI 강제 없음) 보존:
- 게이트 대상 = "bootstrap 미초기화 감지 → surface → 초기화 우선 **유도(권고)**". brainstorm 호출 자체를 막지 않음.
- `superpowers:brainstorming` 직접 호출 (ADR-034 Amd 2 cost-out 경로) 도 block 금지 — warning 만.
- 사용자가 "초기화 없이 진행" 명시 선택 시 silent fallback (opt-out 보존).
- ADR-034 에는 1줄 cross-ref 주석만 추가 (게이트 대상 = bootstrap 미초기화 감지·제안, brainstorm 진입 자체 차단 아님 — D1 자기모순 회피).

### Bypass 정합

§결정 3 `HOTFIX_BYPASS_CODEFORGE=1 + REASON` 양 env set → strict 무관 hook self skip. Amendment 10 entry-gate 활성 시에도 §결정 3 bypass mechanism 그대로 작동. 추가로 본 훅 전용 advisory bypass = `BYPASS_BOOTSTRAP_GATE=1` (§결정 13.E) — 별도 mechanism.

### Default 미변경 = additive only

본 amendment = additive 만. 기존 Secondary trigger (변경동사 `CHANGE_PATTERNS`) 무변경. 초기화 완료 consumer (exit 0/1/2) = 발화 0 (backward-compat). detect-repo-kind.py 무변경. 기존 consumer 동작 즉시 변경 0.

### 해소 기준 정합

ADR-027 frontmatter `is_transitional: false` (permanent policy). Amendment 10 = Secondary trigger enforcement scope 확장 (변경동사-only → codeforge-선언 + 미초기화 감지 entry-gate) = governance 강화 방향 ratchet — ADR-058 §결정 5 sunset_justification 불요 (강화 방향, weakening 0건).

Cross-ref:
- ADR-027 §결정 2 (3-trigger enforcement model) — 본 Amendment 10 = Secondary trigger entry-gate 확장 carrier
- ADR-027 §결정 3 (HOTFIX_BYPASS_CODEFORGE bypass) — §13.E honor
- ADR-027 Amendment 6 §결정 10 + [ADR-083](ADR-083-consumer-applicability-filter.md) §결정 1/5 — detect-repo-kind 4-way truth-table (exit 0/1/2/3) SSOT, 무변경 재사용
- [ADR-034](ADR-034-pre-issue-brainstorming-stage.md) D1 — brainstorm 옵션성 보존 (게이트 ≠ 진입 차단), 1줄 cross-ref 주석 동반
- [ADR-058](ADR-058-adr-sunset-criteria-mandate.md) §결정 5 — sunset_justification ratchet 강화 방향 exemption
- [ADR-064](ADR-064-decision-principle-mandate.md) §self-application — ratchet 강화 방향 only (scope 확장, weakening 0)
- https://code.claude.com/docs/en/hooks.md — UserPromptSubmit hook decision control (exit 2 / decision:block = prompt erase 권한, exit 0 = context inject) — 본 훅은 exit 0 만 사용 (정책적 자기 절제)
- `skills/codeforge-brainstorm/SKILL.md` §"게이트 분기 절차" — skill 측 LLM 지시 (entry-gate 의 skill-side mirror). 미초기화 = 4 부재 SSOT 정의 동일화 (§13.B I-4 wording SSOT)
- `templates/scripts/detect-repo-kind.py:99-115` — `unknown`(exit 3) ⟺ `has_plugin=False ∧ has_overlay=False` 실측 SSOT (§13.B 4 부재 정의의 앞 2 conjunct 근거, 무변경 재사용)
- `hooks/hooks.json:62-71` — UserPromptSubmit `run-hook.cmd <name>` polyglot dispatch 배열 (§13.F additive entry append 대상, 실측)
- `hooks/korean-english-recovery` (shim) — bypass→exit0 / python 탐색→부재시 exit0 / exec core 패턴 SSOT (§13.F bootstrap-first-gate shim 답습 원형) + stderr advisory 동형 (§13.C audit 1-line)
- `overlay/hooks/userprompt_reminder.py:59` — 기존 무제한 `sys.stdin.read()` (sibling). bounded read `sys.stdin.read(1<<20)` 는 본 훅 **신규 강화** — 복사 아님 (Change Plan §3.2(a)/§7 I-3)
- `hooks/bootstrap-first-gate` + `hooks/bootstrap-first-gate.py` — Phase 2 mechanical enforcement carrier
- internal-docs Change Plan `cfp-2243-bootstrap-first-gate.md` §3/§7/§8/§11 — 구현 계약 SSOT (ADR-013 dogfood-out)

## Amendment 11 — §결정 4 Windows-parity mechanical 강화: PowerShell-native label 시드 + windows CI + resolve 결정화 + REQUIRED_LABELS 오탐 제거 (CFP-2250)

**Effective**: 2026-06-15 (Epic CFP-2244 S2, CFP-2250 Phase 1 설계 PR merge 시점).

**Carrier**: CFP-2250 (`carrier_story` for S2). Parent Epic CFP-2244 (Consumer Onboarding Hardening). Sibling Stories: CFP-2243 (S1, Amendment 10, **MERGED prerequisite**) / CFP-2251 (S3, type:* native Issue Type org cutover) / CFP-2252 (S4, story-init PAT/라우팅) / CFP-2253 (S5, consumer-guide 선형 온보딩).

본 ADR §결정 4 (cross-platform 의무 — POSIX bash + Windows PowerShell 양 OS 검증)는 결정으로만 존재했고 Windows 측 mechanical 이행이 미완이었다. mctrader 데뷔(native Windows 환경)에서 다음이 노출됐다 (실측, worktree HEAD 968d90fc):

| # | 결함 | 실측 위치 | 본질 |
|---|---|---|---|
| 1 | Windows label 시드 불완주 | `scripts/bootstrap-consumer.ps1:258-275` (`Stage-6-Labels`) `& bash bootstrap-labels.sh` → bash 미발견(L269) 시 WARN+수동안내(L270) 종료 | §결정 4 Windows-parity 미이행 — label 미시드 → Issue Form `label not found` silent 깨짐 |
| 2 | HOME/USERPROFILE 비결정 | `overlay/hooks/check_bootstrap.py:145-160` (`_resolve_plugins_json`) `[HOME, USERPROFILE]` 고정순서 first-match | WSL/dual-env 양 env set 시 OS 맥락 무시 → 비결정 |
| 3 | manifest/project.yaml preflight 늦음 | bootstrap precheck/story-init 발동 후 exit 1 | 검증이 너무 늦고 원인 불명 |
| 4 | REQUIRED_LABELS type:* 오탐 | `check_bootstrap.py:56-64` type:epic/story/bug ↔ `bootstrap-labels.sh:78-82` 미생성 (ADR-049 native 이관) | 구조적 오탐 (check 2 영구 "부재" 보고) |
| 5 | windows CI 안전망 부재 | `.github/workflows/` 52 파일 전부 ubuntu-latest (`runs-on: windows` grep 0) | 결함1 회귀 차단 CI 없음 |
| 6 (정합) | superpowers required 잔존 | `bootstrap-consumer.{sh,ps1}` / `check-debut-readiness.{sh,ps1}` required 목록 | ADR-122/CFP-2249 후속 누락 drift (check_bootstrap.py 는 정합 완료) |

본 amendment = §결정 4 의 **이행 강화** (additive, supersede 아님). §결정 14 신설.

### 결정 14 — Windows-parity mechanical enforcement (normative SSOT)

#### §결정 14.A — PowerShell-native label 시드 parity

신규 `scripts/bootstrap-labels.ps1` (PowerShell 5.1+) = `bootstrap-labels.sh` 의 native parity wrapper (bootstrap-consumer.ps1 이 .sh 의 wrapper 인 선례 답습). 동일 idempotent semantic (create→edit→fail-echo, `bootstrap-labels.sh:46-74` 미러). gh 호출 = **배열 인자** (`& gh label create $name --color $color --description $desc`) 의무 — 문자열 보간 명령 조립 / `Invoke-Expression` 금지 (PowerShell injection 차단, SecurityArch).

#### §결정 14.B — label 데이터 SSOT 단일화 (drift 구조적 차단)

`.sh` 의 hardcoded base label 을 공유 데이터 파일 `templates/labels/base-labels.tsv` (`name\tcolor\tdesc`)로 추출 → `.sh` ∧ `.ps1` 양쪽 동일 파일 read. 중복 hardcode 거절 (영구 drift 위험). hotfix-bypass:* (`parse-hotfix-bypass-labels.py`) + component:* (project.yaml) = Python 단일 경로라 .sh/.ps1 공통 호출 (추가 중복 0). label provenance SSOT = `label-registry-v2.md` (TSV 추출이 provenance 손실 아님). count cross-verify (`check-bootstrap-labels-count.sh`) TSV 경로로 통과 의무.

#### §결정 14.C — Stage 6 3-tier fallback (silent skip 금지)

`bootstrap-consumer.ps1:Stage-6-Labels`: (1) `Get-Command bash` 발견 → `& bash bootstrap-labels.sh` (POSIX 경로 회귀 0). (2) bash 미발견 → `& bootstrap-labels.ps1` (Windows-native fallback, 결함1 해소). (3) 둘 다 불가 → 명시 ERROR + return false. AS-IS 의 WARN-then-skip(L270) 제거 — silent skip 은 결함1 의 근본 (graceful degradation = 자동 fallback, 수동안내 종료 아님).

#### §결정 14.D — OS-aware plugins.json resolve 결정화

`check_bootstrap.py:_resolve_plugins_json` 우선순위 = `os.name == "nt"` → [USERPROFILE, HOME] / POSIX → [HOME, USERPROFILE]. 동일 (os, env, 파일존재) → 동일 path (결정적). OS 가 SSOT 인 env 를 OS 분기로 우선 = WSL(POSIX, HOME 정본) ∧ native Windows(USERPROFILE 정본) 양쪽 결정적.

#### §결정 14.E — preflight 전진 (story-init 발동 전)

bootstrap 미완/결손은 가장 이른 결정적 시점에 명시 안내: (1) `check_bootstrap.py` SessionStart — manifest 부재 silent return → 명시 WARN, project.yaml strict-eligible (a) 메시지 보강. (2) `bootstrap-consumer.{sh,ps1}` Stage 1 precheck — manifest/project.yaml 결손 사전 안내. story-init.yml 자체의 preflight(PAT/라우팅) = S4 #2252 영역 (본 amendment 침범 0 — bootstrap 측 안내로 한정).

#### §결정 14.F — REQUIRED_LABELS type:* 제거 (S2 단독 소유)

`check_bootstrap.py:REQUIRED_LABELS` 에서 type:epic/story/bug 제거 (18→15). ADR-049 native Issue Type 이관 + `bootstrap-labels.sh` 미생성 = 구조적 오탐. `check_plugin_labels` 메시지 `/18` → `len(REQUIRED_LABELS)` 동적. STRICT_ELIGIBLE_LABELS (phase:* 7 + gate:* 3 = 10) type:* 미포함 → 무영향. **충돌 경계**: type:* native Issue Type *org cutover* (ADR-049 Phase 2) = S3 #2251 영역. 본 amendment = `check_bootstrap.py` 파일 단독 오탐 row 제거 (Epic CFP-2244 가 S2 = check_bootstrap.py 단독 소유 명시 — S3/S4 3-way 파일 충돌 회피).

#### §결정 14.G — windows-latest CI smoke (안전망 신설)

신규 `.github/workflows/windows-bootstrap-smoke.yml` (단일 job, windows-latest — 기본 shell pwsh [source: GitHub Actions Windows default shell = PowerShell, github.blog/changelog 2019-10-17]). smoke = no live gh (dry-run, token secret 노출 0): bootstrap-labels.ps1 -DryRun count + bootstrap-consumer.ps1 -DryRun Stage 6 native 경로 + check_bootstrap.py Windows resolve. non-required tier 시작 (branch protection 6-tuple 미등재 — ADR-060 evidence-gate 후 승격 후보). ubuntu job 과 중복 아님 (경로 구분자 / pwsh ConvertFrom-Json / UTF-8 경계 discriminating).

#### §결정 14.H — superpowers required 정합 (ADR-122 후속)

`bootstrap-consumer.{sh,ps1}` + `check-debut-readiness.{sh,ps1}` required 목록에서 `superpowers@claude-plugins-official` 제거 + count 메시지(11→10) 정합. `check_bootstrap.py` 는 CFP-2249 에서 정합 완료. 10 plugin = codeforge 7 (wrapper + 6 lane) + github + codex + claude-md-management.

### Bypass 정합

§결정 3 `HOTFIX_BYPASS_CODEFORGE=1 + REASON` bypass mechanism 무손상. 본 amendment = bootstrap 실행 경로 강화 (enforcement bypass 와 별도 mechanism).

### Default 미변경 = additive only

bash POSIX 경로 무변경 (WSL/Git Bash 환경 회귀 0). PowerShell native 경로 = 신규 fallback 추가. 기존 consumer 동작 (bash 보유) 즉시 변경 0 (backward-compat). type:* 제거 = 오탐 제거 (실 동작 영향 = 노이즈 감소만).

### 해소 기준 정합

ADR-027 frontmatter `is_transitional: false` (permanent policy). Amendment 11 = §결정 4 Windows 측 mechanical enforcement 추가 = governance 강화 방향 ratchet (weakening 0건) — ADR-058 §결정 5 sunset_justification 불요.

Cross-ref:
- ADR-027 §결정 4 (cross-platform 의무 POSIX + Windows) — 본 Amendment 11 = Windows 측 mechanical 이행 carrier
- ADR-027 §결정 3 (HOTFIX_BYPASS bypass) — 무손상
- [ADR-122](ADR-122-superpowers-dependency-removal.md) — §결정 14.H superpowers required 정합 근거 (CFP-2249 sibling)
- [ADR-049](ADR-049-issue-types-native-migration.md) — §결정 14.F REQUIRED_LABELS type:* 제거 근거 (native Issue Type). S3 #2251 = org cutover Phase 2 영역 (파일 경계 분리)
- [ADR-032](ADR-032-adr-027-amendment-1-hard-enforcement.md) — Amendment 1 strict-eligible (REQUIRED_LABELS 변경이 STRICT_ELIGIBLE_LABELS 무영향 확인)
- [ADR-060](ADR-060-evidence-enforceable-promotion-framework.md) — §결정 14.G windows CI non-required → blocking 승격 gate
- [ADR-058](ADR-058-adr-sunset-criteria-mandate.md) §결정 5 — sunset_justification ratchet 강화 방향 exemption
- `scripts/bootstrap-consumer.ps1:258-275` / `scripts/bootstrap-labels.sh:46-82` / `overlay/hooks/check_bootstrap.py:56-64,145-160` — 실측 SSOT
- https://github.blog/changelog/2019-10-17-github-actions-default-shell-on-windows-runners-is-changing-to-powershell/ — windows-latest 기본 shell pwsh (§결정 14.G CI 외부 사실)
- internal-docs Change Plan `cfp-2250-bootstrap-hardening.md` §3/§8/§11 — 구현 계약 SSOT (ADR-013 dogfood-out)

## Amendment 12 — Secondary trigger 채널의 ADR-127 skip-offer 금지 규칙 소비자 전파 (자동활성 reminder hook, unconditional fire) (CFP-2456)

**Effective**: 2026-06-29 (CFP-2456 Phase 1 설계 PR merge 시점, KST `+09:00`).

**Carrier**: CFP-2456 (`carrier_story`). 본 amendment = 본 ADR §결정 2 (3-trigger enforcement model) 의 **Secondary trigger (UserPromptSubmit) 적용 범위 확장** — Amendment 10 (CFP-2243, bootstrap-first-gate) 가 같은 §결정 2 Secondary trigger 채널에 **신규 자동활성 hook 을 plugin `hooks/hooks.json` 으로 ship** 한 선례를 답습한다. §결정 15 신설.

### 컨텍스트 — propagation gap (실측 firsthand)

ADR-127 §결정 4 (dialog skip-offer 금지 — "생략/간소화/빠르게?" 를 `AskUserQuestion` 선택지로 제시 금지)는 **wrapper 자기 거버넌스 영역**(wrapper `CLAUDE.md` + `skills/user-dialog-mode/SKILL.md` + ADR-071 Amendment 11)에만 존재했고, **소비자(consumer) 세션 Orchestrator 가 매 turn 실제 로드하는 컨텍스트로 전파되는 채널이 0** 이었다 (CFP-2456 §1-2 실측):

| 소비자 로드 채널 | ADR-127 no-skip 규칙 존재 | 근거 |
|---|---|---|
| 소비자 repo root `CLAUDE.md` | **0** | 순수 프로젝트 설명서 — 프로세스 정책 0건 |
| **plugin-root `CLAUDE.md`** | 소비자 컨텍스트 **미로드** | "A `CLAUDE.md` file at the plugin root is **not loaded as project context**. Plugins contribute context through skills, agents, and hooks rather than CLAUDE.md." [source: Claude Code 공식 docs — plugins-reference (code.claude.com/docs/en/plugins-reference, "File locations reference" 절 직전), 2026-06-29 verbatim 확인]. → wrapper plugin 이 자기 `CLAUDE.md` 에 규칙을 적어도 소비자 Orchestrator 는 못 봄 |
| on-demand skill (`user-dialog-mode` 등) | 규칙 보유하나 소비자 호출 지시 0 | Skill tool 명시 호출 전 컨텍스트 미진입 |
| `UserPromptSubmit` hook reminder | **0 (stale)** | `overlay/hooks/userprompt_reminder.py:135-166` = ADR-022/027 era, no-skip 0줄 + consumer settings.json 등록 의존(미초기화 소비자 무발동) |

결과: 소비자 Orchestrator(LLM)는 학습된 기본 reflex("작은 변경은 절차 생략 제안")로 free-style 하며 phase-gate 라벨 후 `AskUserQuestion`(리뷰 lane 생략 제안)을 띄운다 — ADR-127 §결정 4 직접 위반. **mctrader 만이 아니라 모든 소비자가 영향** (낡은 설정 아님 — 전파 채널 자체가 빔).

### 결정 15 — ADR-127 no-skip 규칙의 plugin-shipped 자동활성 reminder hook 전파

본 ADR §결정 2 Secondary trigger (UserPromptSubmit) 채널에, ADR-127 §결정 4 (정식 풀 플로우 비협상 / 리뷰·절차 생략 제안 — `AskUserQuestion` 포함 — 금지) 규칙을 실어 소비자 세션에 **자동 도달**시키는 신규 plugin-level hook 을 신설한다.

#### §결정 15.A — 채널 = plugin `hooks/hooks.json` UserPromptSubmit (유일 자동 도달 경로)

소비자 로드 채널 4종 중 **plugin 이 자동 ship 가능 ∧ per-turn 자동 도달** 하는 유일 채널은 hook stdout 이다 (위 표 + plugins-reference 외부사실). plugin-root CLAUDE.md 는 미로드, project CLAUDE.md 는 plugin 자동 충전 불가, skill 은 명시 호출 의존. 따라서:

> **공식 docs divergence 정직 고지 (ADR-119 정합)**: plugins-reference 후반은 "To ship instructions that load into Claude's context, put them in a [skill]" 로 **skill 을 instructions ship 1순위로 권고**한다. 본 ADR 은 그 권고와 **의도적으로 divergent** — skill 은 명시 호출 전 미진입(약 도달)이라 *매 turn reflex override* 목적에는 부적합하다. 자동·무조건 도달이 본 결함의 핵심 요건이므로 hook(per-turn 자동 inject) 을 의도적으로 채택한다. (skill 권고는 "Claude 가 필요 시 호출하는 능력 추가" 용도이고, 본 건은 "Claude 가 호출 안 해도 매 turn 강제 도달" 용도라 목적이 다름.)


- 신규 hook 을 wrapper plugin `hooks/hooks.json` 의 UserPromptSubmit 배열 **3번째 entry** 로 등록 (`hooks/hooks.json:67-82` — 기존 korean-english-recovery + bootstrap-first-gate 2 entry 뒤). 형식 = `"${CLAUDE_PLUGIN_ROOT}/hooks/run-hook.cmd" skip-offer-reminder` (async:false). `/plugins install` 만으로 소비자 수동 wiring 없이 자동 활성 (Amendment 10 bootstrap-first-gate 와 동일 메커니즘, ContinuityAgent 실측).
- **AC4 핵심**: plugin-level hook 은 소비자 `.claude/settings.json` 비의존 → `.claude/` 미초기화 소비자(mctrader-market: `.claude/** = 0 files`)에도 도달. overlay/settings.json 의존 채널(`overlay/hooks/userprompt_reminder.py`)은 미초기화 소비자에서 무발동 = 부적합.

#### §결정 15.B — unconditional fire (변경동사 regex-gate 없음)

기존 Secondary trigger(`overlay/hooks/userprompt_reminder.py` CHANGE_PATTERNS, `:36-43`)와 bootstrap-first-gate(`:49-65` intent regex)는 **변경동사·codeforge 고유신호 매치 시에만** 발화한다. 그러나 skip-offer 는 변경동사 없는 turn — "진행해" / "다음 단계" / phase-gate 라벨 후 평문 — 에도 발생한다 (CFP-2456 KU-2). 따라서 본 reminder hook 은 **매 turn 무조건 발화** (regex-gate 없음). 이것이 기존 hook 과의 1급 차별 invariant — `_matches_intent` 류 gate 적용 금지.

- false-positive 비용 = 무시 가능: reminder 텍스트는 짧은 governance 상기일 뿐 작업 차단 0 (모든 경로 exit 0).

#### §결정 15.C — JSON `additionalContext` emit 형식 (plain stdout 회귀 회피)

inject 는 plain stdout prepend 이 아니라 Claude Code hooks JSON `hookSpecificOutput.additionalContext` 형식으로 emit 한다. plain stdout prepend 은 일부 Claude Code 버전에서 컨텍스트 미주입 회귀가 보고됐다 [source: anthropics/claude-code GitHub issue #13912 — plain stdout UserPromptSubmit context inject 회귀]. JSON `additionalContext` 경로 = **현행 docs 일치 확인됨** [source: Claude Code hooks-guide (code.claude.com/docs/en/hooks-guide), 2026-06-29 KST verbatim: "For `UserPromptSubmit` hooks, use `additionalContext` instead to inject text into Claude's context." + "Text from `additionalContext` is kept from every hook and passed to Claude together." + "Text returned via `additionalContext` is injected as a system reminder that Claude reads as plain text."]. schema envelope = `{"hookSpecificOutput": {"hookEventName": "UserPromptSubmit", "additionalContext": "<text>"}}` (`hookSpecificOutput.hookEventName` 패턴 = hooks-guide 문서화 schema). **설계 lock (uncertain deferral 아님)**: (a) emit 형식 = JSON `additionalContext` (plain stdout 금지) + (b) 정확 key 명 = `hookSpecificOutput.hookEventName` / `additionalContext` (현행 docs 확인됨) + (c) 테스트 파싱 방식 = anti-theater(`json.loads` 후 key-path 순회, substring assert 금지). 구현 lane 의 Phase 2 책무 = "live hooks-guide 로 동작 **재확인** (현행 일치 이미 확인 — 재확인은 회귀 가드)" 이지 schema 미결 deferral 이 아니다.

#### §결정 15.D — 2-file 패턴 + fail-safe (bootstrap-first-gate 청사진 답습)

신규 hook = 2-file 구조 (Amendment 10 bootstrap-first-gate 답습, `hooks/bootstrap-first-gate` + `hooks/bootstrap-first-gate.py`):
- extensionless POSIX shim `hooks/skip-offer-reminder` (bash; `set -uo pipefail`; python3→python 탐색; python 부재 시 exit 0 fail-safe; `exec`). 확장자 없는 파일명 = Windows `.sh` auto-detect 회피(`run-hook.cmd` 요구).
- python core `hooks/skip-offer-reminder.py`: bounded `_read_input` (`sys.stdin.read(1 << 20)` 1MiB — DoS 차단, bootstrap-first-gate `:80` 미러) + JSON key 추출(prompt/user_message/message/text/content) — 단 unconditional fire 라 입력 내용은 발화 판정에 미사용(읽되 echo 0). 정적 reminder 텍스트 build. **모든 경로 exit 0 (P0 fail-safe — 사용자 prompt erase 권한 미사용)**. stderr 1-line audit 에 **사용자 prompt 텍스트 절대 미기록**(PII/secret leak 차단, bootstrap-first-gate `:30` invariant 미러).

#### §결정 15.E — enforcement 간극 명문화 (behavioral 도달 ≠ hard block)

본 채널은 **behavioral guidance (도달)** 이지 **hard enforcement (물리적 차단)** 가 아니다. 본 ADR §결정 2 가 hook 을 "Block 아님 — warning inject only, enforcement = LLM 측 책임" 으로 규정한 것과 정합 (`ADR-027 §결정 2`). UserPromptSubmit stdout 은 context inject 에 그치며, 동작을 *block* 하려면 PreToolUse 류 차단 hook 이 필요하다 [source: Claude Code 공식 hooks docs — UserPromptSubmit = context injection layer, not a hard enforcement layer]. 따라서:
- AC2(skip-offer reflex override)는 "도달 + override guidance 제공" 충족이며 "물리적 발화 0 보장" 이 **아니다**. 어느 채널도 LLM 의 skip-offer 발화를 0-차단 못 함 (LLM trust 모델 의존).
- 기계적 skip-offer 탐지 lint(consumer-facing)는 **OOS** — runtime `AskUserQuestion` 발화는 정적 스캔 대상이 없고, 정당 ask-trigger 오탐 + 검사연극(ADR-119) 위험.

#### §결정 15.F — 정합 부수: story.yml doc-only fast-path dropdown orphan 제거

ADR-127 §결정 2 (doc-only fast-path 폐지) 발효 후에도 Story Issue Form dropdown 에 폐지된 옵션이 잔존했다 (실측):
- `.github/ISSUE_TEMPLATE/story.yml:59` + `templates/.github/ISSUE_TEMPLATE/story.yml:59` 양쪽 `        - 문서 (Doc-only fast-path)` byte-identical. 두 파일은 byte-mirror 쌍(`# BEGIN/END wrapper-managed` block) → 동시 제거 의무 (ADR-005 mirror invariant). dropdown 에서 해당 옵션 1줄만 제거, 나머지 5 옵션 보존.
- **기존 제출 Issue 무영향**: dropdown 옵션 제거는 *향후* Story 제출 폼에만 적용된다. 이미 제출돼 `문서 (Doc-only fast-path)` 값이 박힌 기존 Issue 의 body 는 제출 시점 snapshot 으로 불변이며 본 변경에 영향받지 않는다 (Issue Form dropdown = 제출 시 1회 렌더, 저장 후 폼 정의와 decouple).

### overlay invariant 정합 (강화 방향)

전파될 no-skip 규칙은 소비자 overlay 로 약화·무력화 불가다. codeforge overlay invariant = "정책을 확장(더 엄격하게)만 가능, 축소 불가" (CLAUDE.md 정체 단락 + ADR-071 §결정 10). plugin-shipped hook 채널은 그 특성상 소비자 overlay 가 깎을 수 없다(소비자 settings.json 비의존). ADR-127 §결정 6 이 이미 consumer 면제 확장채널을 폐지해 같은 방향을 강화했다 → 본 전파는 invariant 와 **충돌 아니라 정합·강화** (소비자에게 더 엄격한 규칙을 추가 도달).

### Default 미변경 = additive only

기존 UserPromptSubmit 2 entry (korean-english-recovery / bootstrap-first-gate) 무변경. overlay/hooks/userprompt_reminder.py 무변경. 신규 hook = 3번째 entry 추가만. 기존 소비자 동작 즉시 변경 0 (backward-compat, `/plugins install` 갱신 시 자동 활성).

#### dual-fire 결정 (lock)

overlay 가 설치된 소비자에서는 신설 plugin hook 과 deprecated `overlay/hooks/userprompt_reminder.py` 가 같은 turn 에 둘 다 발화(dual-fire)할 수 있다. **결정 = 1-release grace 중 dual-fire 허용**:
- 두 reminder 의 **내용 직교** — 신설 = ADR-127 no-skip rule(unconditional), 기존 = Story protocol/branch 안내(change-verb-gated). 같은 정책의 모순된 두 버전이 아니라 별개 주제 → LLM 컨텍스트에 둘 다 있어도 모순 0.
- 비용 = reminder 텍스트 약간의 중복 token (작업 차단 0). over-engineering(억제 로직 신설)은 비용 > 이득 → 미도입.
- overlay reminder 의 **sunset 은 별도 후속 CFP** (1-release grace 경과 후 deprecation 완료 — 본 Story scope 외). 본 Story 는 신설 hook 을 정본으로 ship 만 하고 기존 경로는 손대지 않는다.

#### DRY 결정 (lock)

`_read_input` bounded-stdin + JSON-key-extraction 패턴이 bootstrap-first-gate.py + userprompt_reminder.py + 신설 skip-offer-reminder.py 3곳에 존재(rule-of-three). **결정 = 신설 hook 은 self-contained 복제 확정** — `_hook_utils.py` 공통 추출은 미채택:
- 근거 = hook 격리성·fail-safe 독립 우선. 각 hook 은 독립 프로세스로 fail-safe(전경로 exit 0)를 자기 완결로 보장해야 하며, 공통 모듈 import 실패가 cross-hook 회귀를 일으킬 표면을 만들지 않는다.
- `_hook_utils` 추출 = OOS 후속 (ADR-119 §결정 9 3문 게이트 미충족 — 깨진 것 아님, ~25줄 복제는 hook 격리성 이득이 DRY 비용 상회). Story §5.6 기록 — rule-of-three 도달이 추가 hook 신설로 누적되면 Phase 2/후속에서 chief 재판정.

### 해소 기준 정합

ADR-027 frontmatter `is_transitional: false` (permanent policy). Amendment 12 = §결정 2 Secondary trigger 적용 범위 확장 (변경동사-gated → ADR-127 no-skip unconditional 전파) = governance 강화 방향 ratchet (weakening 0건) — ADR-058 §결정 5 sunset_justification 불요.

Cross-ref:
- ADR-027 §결정 2 (3-trigger enforcement model) — 본 Amendment 12 = Secondary trigger 적용 범위 확장 carrier
- ADR-027 Amendment 10 (CFP-2243, §결정 13 bootstrap-first-gate) — plugin-shipped 자동활성 UserPromptSubmit hook 선례 (2-file 패턴 + `hooks/hooks.json` 등록 + fail-safe exit 0 답습)
- [ADR-127](ADR-127-mandatory-full-flow-no-exemption.md) §결정 4 (dialog skip-offer 금지) — 전파 대상 정책 SSOT. 본 amendment = ADR-127 의 consumer propagation gap 충당 (ADR-127 Amendment 1 동반 — consumer 전파 영역 명문화)
- [ADR-071](ADR-071-orchestrator-user-dialog-convergence.md) §결정 10/21 — overlay 축소 불가 invariant + skip-offer 금지 dialog SSOT (정합·강화)
- [ADR-039](ADR-039-orchestrator-subagent-default-for-codeforge-modification-work.md) §결정 2 — `AskUserQuestion` inline whitelist (합법) ↔ skip-offer 종류만 narrowing (ADR-127 §결정 4 해소 선례 답습, 충돌 0)
- [ADR-005](ADR-005-plugin-self-application-na-standardization.md) — §결정 15.F story.yml byte-mirror 쌍 동시 제거 invariant
- [ADR-119](ADR-119-research-before-claims.md) §결정 9 — 기계적 skip-offer lint OOS 근거 (검사연극 회피)
- Claude Code plugins-reference (code.claude.com/docs/en/plugins-reference) — plugin-root CLAUDE.md 미로드 외부사실 (§결정 15.A/15.E 근거)
- anthropics/claude-code issue #13912 — plain stdout UserPromptSubmit inject 회귀 (§결정 15.C JSON additionalContext 채택 근거)
- `hooks/hooks.json:67-82` / `hooks/bootstrap-first-gate{,.py}` / `overlay/hooks/userprompt_reminder.py:36-43,135-166` / `.github/ISSUE_TEMPLATE/story.yml:59` + `templates/.github/ISSUE_TEMPLATE/story.yml:59` — 실측 SSOT (worktree HEAD 7abdb0a1)
- internal-docs Story `wrapper/stories/CFP-2456.md` §3/§7/§8/§11 — 설계·테스트 계약 SSOT (ADR-013 dogfood-out, 별도 change-plan 면제 — 본 ADR 이 §3 설계 SSOT)

## Amendment 13 — §결정 2 enforcement 의 mechanical(branch protection) vs advisory(hook) layer 구분 명문화 (consumer dead-gate 차단, CFP-2469)

> Epic CFP-2468 (codeforge 강제력·검증 균질성 복구) Track W/W1. Paired carrier = **ADR-132** (consumer branch-protection 자동 wire 메커니즘 SSOT) + **ADR-024 Amendment 20** (Amendment 2 §결정 C step 2 수동→자동). 본 Amendment = ADR-027 adoption protocol 측 연결 (§결정 16 신설 — layer 구분).

### 컨텍스트

§결정 2 의 "**Block 아님 — warning inject only**" + "enforcement = LLM 측 책임" 은 Secondary trigger (UserPromptSubmit hook) 를 가리킨다. 그러나 이 문구가 codeforge 전체 enforcement 모델로 오독되면 — consumer 게이트의 **merge 차단력** 까지 advisory 로 간주되어 dead-gate 가 정상으로 보일 위험이 있다. 실제로 consumer 16 repo 중 15개가 게이트 workflow 는 PR 마다 돌지만 `required_status_checks.contexts[]` 미등록 = merge 차단력 0 (**dead gate**) 였다. 본 Amendment 가 layer 를 2분해 이 오독을 차단한다.

### 결정 16 — 2-layer 구분

| layer | 메커니즘 | enforcement 성격 | §결정 2 적용 |
|---|---|---|---|
| **hook 層** | UserPromptSubmit (`userprompt-reminder` / `bootstrap-first-gate` / `skip-offer-reminder`) | **advisory** — warning inject only, context 주입, block 아님 | "Block 아님" = **이 層 한정** |
| **branch protection 層** | GitHub native `required_status_checks` (Primary trigger 의 mergeability 실효화) | **mechanical** — merge 실차단 (등록 context fail → PR merge 불가) | dead-gate 해소 = 이 層 자동 충전 |

핵심:

1. **branch protection 層 = mechanical**. 게이트 workflow 가 status check 를 emit 해도, 그 check 가 `required_status_checks.contexts[]` 에 등록되어야 merge 가 실제 차단된다. 본 ADR (ADR-132 메커니즘 + ADR-024 Amendment 20) 이 그 등록을 자동 충전 = dead-gate 해소. 이것은 advisory hook 강화가 아니라 **mechanical layer 충전**.
2. **충전 시도 실패 = advisory graceful**. 자동 배선이 operator org-admin 권한 부재로 GitHub 403 을 받으면 → WARN 출력 + drift-preview fallback (`setup-branch-protection.sh --dry-run`), hard-block 아님. 이 *시도-실패* 처리만 §결정 2 warning-inject-only 정합 (operator 환경 사실은 codeforge 결함 아님 → graceful degrade).
3. "게이트 workflow 존재 ≠ merge 차단력" 갭을 **mechanical layer 충전** 으로 메운다. advisory hook 으로는 dead-gate 를 해소할 수 없음을 명문화.

### Sunset justification

ratchet 강화 방향 전용 (§결정 2 enforcement 의 mechanical/advisory layer 구분 명문화 — dead-gate 차단 강제력 추가, mechanical protection layer 자동 충전). is_transitional: false permanent governance invariant 무변경. 기존 §결정 2 hook 層 advisory 영역 무변경 (weakening 0 — branch protection 層 mechanical 명문화만 추가). ADR-058 §결정 5 = ratchet 강화 방향 전용 exemption 정합. paired SSOT = ADR-132 (메커니즘) + ADR-024 Amendment 20 (step 2 수동→자동) + ADR-066 §결정 2 (PAT 6-scope 무손상 — operator gh auth 옵션 A).

Cross-ref:
- ADR-027 §결정 2 (3-trigger enforcement model) — 본 Amendment 13 = enforcement layer 구분 carrier
- [ADR-132](ADR-132-consumer-branch-protection-auto-wire.md) — consumer branch-protection 자동 wire 메커니즘 SSOT (paired)
- [ADR-024](ADR-024-story-scoped-branch-policy.md) Amendment 20 — Amendment 2 §결정 C step 2 수동→operator-token 자동 전환 (paired)
- [ADR-066](ADR-066-pat-rotation-policy.md) §결정 2 — codeforge PAT 6-scope (Administration:write 부재) 무손상, operator gh auth 옵션 A
- [ADR-119](ADR-119-research-before-claims.md) §결정 9 — 외부사실(GitHub branch protection mechanical merge-block / about-protected-branches) source 인용 의무
