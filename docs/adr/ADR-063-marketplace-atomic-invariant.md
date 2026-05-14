---
adr_number: 63
title: Marketplace ↔ plugin.json atomic invariant — 3-file coordination (version bump 시)
status: Accepted
category: Team & Process
date: 2026-05-12
is_transitional: false
sunset_justification: "N/A — permanent governance policy. ADR-064 §self-application top-down ratchet 정합 (Amendment 1 = 강화 방향 only, proactive trigger layer 추가). ADR-058 §결정 5 약화 방향 발의 차단 logic 통과."
related_files:
  - CLAUDE.md
  - scripts/check-marketplace-parity.sh
  - docs/adr/ADR-016-marketplace-registration-policy.md
  - docs/adr/ADR-037-plugin-version-bump-rule.md
  - docs/adr/ADR-065-architect-phase1-mechanical-self-check.md
  - docs/orchestrator-playbook.md
related_stories:
  - CFP-387
  - CFP-418
  - CFP-423
  - CFP-436
  - CFP-597
amendments:
  - amendment: 1
    date: 2026-05-13
    cfp: CFP-597
    summary: "§결정 9 신설 — ArchitectAgent Phase 1 marketplace sync proactive self-check trigger. ADR-065 §결정 5 cross-ref-only boundary 보존. 3-layer proactive forcing function (ArchitectAgent §3.6 self-check + Change Plan §13 declarative declare + Orchestrator → GitOpsAgent §3.6 spawn). review-verdict-v4 v4.4 → v4.5 MINOR bump (`marketplace_sync_declared: bool` optional field). Strengthening direction only — ADR-064 self-application top-down ratchet 정합."
  - amendment: 2
    date: 2026-05-14
    cfp: CFP-631
    summary: "§결정 11 신설 — mirrored field `description` PR-time mechanical proactive lint mandate. carrier script `scripts/check-marketplace-description-verbatim.sh` + workflow `templates/github-workflows/marketplace-description-verbatim.yml` + `.github/workflows/...` byte-identical mirror (ADR-005). evidence-checks-registry 42번째 entry `marketplace-description-verbatim` blocking-on-pr tier 직접 시작 — ADR-060 §결정 19 (Amendment 6, CFP-509) auto_blocking manual gate + 사용자 explicit directive (Story §1 CFP-631) §결정 5 default warning exception (6 sample 누적 CFP-387/393/423/597/612/619 drift evidence, 본 carrier Story 자체가 별도 promotion carrier 의무 합병). bypass channel `hotfix-bypass:marketplace-description-verbatim` (ADR-024 Amendment 3 §결정 6.A 16번째 family member). Amendment 1 (design-time self-check) 와 layered 2-layer proactive forcing function. §결정 12 self-application — 본 carrier Phase 1 PR 자체가 lint 첫 적용 대상 (description bump 동반, marketplace sibling sync PR 선행 merge 의무). Strengthening direction only — ADR-064 self-application top-down ratchet 정합."
---

# ADR-063: Marketplace ↔ plugin.json atomic invariant — 3-file coordination

## 상태
`Accepted`

## 컨텍스트

codeforge plugin family 의 version bump 는 3 파일 (`.claude-plugin/plugin.json`, `CHANGELOG.md`, `mclayer/marketplace/.claude-plugin/marketplace.json`) 에 mirrored 정보를 보유한다. ADR-016 (marketplace sibling sync policy) 은 mirrored field 4종 (`name`/`version`/`description`/`author`) sync 의무를 정의하지만, **bump 시 3 file 의 atomic coordination invariant** 는 미명시.

### 3-Wave drift evidence (CFP-387 / CFP-418 / CFP-423 retro)

| Story | Drift 양상 | 감지 channel | Recovery |
|---|---|---|---|
| **CFP-387** | Phase 2 PR 시 marketplace-parity chicken-and-egg — wrapper plugin.json 5.11.0 + codeforge-design 0.7.0 새로 bump 됐으나 marketplace.json 미sync (5.10.0 + 0.6.0). PR CI fail. | `check-marketplace-parity.sh` post-PR-open | marketplace sync PR 선행 merge → Phase 2 PR re-run |
| **CFP-418** | 해당 없음 (backfill, version bump 없음) — Wave count 제외 | — | — |
| **CFP-423** | pre-existing CFP-393 drift — marketplace 5.15.0 sync 완료 but plugin.json 5.14.0 + CHANGELOG.md 5.14.0 정체 (이전 PR drift). PR CI fail. | `check-marketplace-sync.sh` (CFP-34) post-PR-open + `invariant-check` plugin.json↔CHANGELOG mismatch | 본 PR이 5.16.0 catch-up + sync 합쳐 처리 |

3회 누적 drift 의 공통 root cause:
- mirrored field bump 시 3 file 의 **atomic update 의무 미명시**
- bump를 한 file 만 수행하고 sibling sync 가 deferred / dropped 되면 lint 가 사후 감지만 가능
- 작성 시점 (Write 단계) 의 atomic 강제 mechanism 부재

### 기존 CI lint 의 한계

- `check-marketplace-parity.sh` (CFP-50 / ADR-023) — plugin.json ↔ marketplace.json 동치성 검증. **PR open 후 fire**. SSOT 사후 감지 channel (CFP-457 cleanup 후 단독 유지).
- ~~`check-marketplace-sync.sh`~~ — **deprecated CFP-457** (동일 영역 redundant coverage 였음, marketplace-parity 로 통합).
- `invariant-check` — plugin.json ↔ CHANGELOG.md 동치성 (version field).
- **Gap**: 3 file atomic invariant (작성 시점 강제) + ordering rule (marketplace sync PR vs plugin PR merge 순서) 미정의.

### 사용 시나리오

**Case A: 새 PR이 plugin.json version 변경**
- plugin.json + CHANGELOG.md 변경은 같은 PR 안에 함께 처리 (기존 `invariant-check` enforce)
- marketplace.json 은 별도 PR (mclayer/marketplace 다른 repo) — sibling sync PR 의무
- 본 PR과 sibling sync PR 의 **ordering**: marketplace sync 선행 merge → plugin PR merge (현재 관행)
- 또는 concurrent merge (atomic, drift 0-window) — 사용자 결정 영역

**Case B: marketplace.json 만 변경 (외부 정책 만 갱신)**
- plugin.json 영향 없음 (예: description 마이너 fix, CFP-378 #40 사례)
- ADR-016 sibling sync 단독 발화

**Case C: plugin.json 만 변경, marketplace.json 미sync**
- **Anti-pattern** — 본 ADR로 차단 대상
- CFP-387 / CFP-393 / CFP-423 drift 의 직접 원인

## 결정

### 결정 1: 3-file atomic invariant 명시 — bump 시 3 file 동시 처리 의무

mirrored field (`name`/`version`/`description`/`author`) 중 하나 이상 변경 시 다음 3 file 의 atomic coordination 의무:

| File | Repo | 변경 의무 |
|---|---|---|
| `.claude-plugin/plugin.json` | plugin repo (예: `mclayer/plugin-codeforge`) | mirrored field 변경 |
| `CHANGELOG.md` | plugin repo | 해당 version entry 추가 (version field 변경 시) |
| `.claude-plugin/marketplace.json` | `mclayer/marketplace` | 해당 plugin entry mirrored field 동일 |

3 file 중 어느 하나만 변경하고 나머지를 deferred / dropped 하면 invariant 위반 = drift 발생.

### 결정 2: PR ordering — marketplace sync 선행 merge 권장

cross-repo coordination 으로 인해 single atomic transaction 불가능. 다음 ordering 채택:

1. **(권장)** marketplace sync PR open + merge 선행
2. plugin PR open (`check-marketplace-parity.sh` PASS — marketplace 가 이미 최신)
3. plugin PR merge

또는 concurrent merge 가능 (drift 0-window):

1. marketplace sync PR + plugin PR 양쪽 open
2. plugin PR CI 의 marketplace check 는 fail 상태 — branch protection bypass 또는 admin override 필요
3. marketplace sync PR merge → 즉시 plugin PR CI re-run → PASS → merge

**Anti-pattern (금지)**:
- plugin PR merge 먼저 → marketplace 가 drift 상태로 main 에 노출 → 다음 PR 들이 모두 CI fail (CFP-387 chicken-and-egg 사례)

### 결정 3: 작성 단계 sanity check — pre-commit 권장

bump 작업 수행 시 다음 sanity check 의무 (ADR-061 §결정 5 정합):

1. plugin.json version + description 변경 직후 `bash scripts/check-marketplace-parity.sh` local 실행 → drift 확인 (사실상 fail 가능 — marketplace 가 미sync)
2. CHANGELOG.md 해당 version entry 작성
3. **즉시** marketplace sync 작업 시작 (별도 worktree / repo 에서 marketplace.json 변경 + PR open)
4. 3 file PR 모두 open 후 ordering (결정 2) 적용

선행 sanity check 없이 plugin PR open → CI fail → 사후 recovery 패턴은 마찰 비용이 높음 (rebase + force-push + re-run).

### 결정 4: bypass channel — 긴급 hotfix

production 장애 / security incident 대응 시 atomic invariant 일시 bypass 가능:

- `hotfix-bypass:marketplace-atomic` label (ADR-024 Amendment 3 hotfix-bypass family 정합)
- bypass 후 24시간 이내 marketplace sync PR open + merge 의무
- bypass 발생 시 `docs/audit/` 에 audit row 의무

본 channel 은 audit-trailed exception only — 정상 운영에서 사용 금지.

### 결정 5: 기존 CI lint 보존 + 신규 lint follow-up

기존 `check-marketplace-parity.sh` (CFP-50 / ADR-023) 는 본 ADR 의 atomic invariant 사후 감지 channel 로 유지. (`check-marketplace-sync.sh` 는 CFP-457 cleanup 으로 deprecated — marketplace-parity 와 redundant coverage 였음.) 신규 작성 시점 enforce (예: pre-commit hook, PR open 시점 cross-ref check) 는 별도 follow-up CFP carrier:

| Lint | 현재 | 신규 (별도 carrier) |
|---|---|---|
| plugin.json ↔ CHANGELOG | `invariant-check` workflow | 그대로 |
| plugin.json ↔ marketplace.json | `check-marketplace-parity.sh` post-PR | pre-commit hook (local) 권장 |
| 3-file atomic 강제 | 부재 | `check-version-bump-atomic.sh` (신규, 별도 CFP) |

### 결정 6: ADR-016 vs ADR-063 분리 — scope 명확화

- **ADR-016 (marketplace sibling sync policy)**: marketplace.json 에 plugin 등록 의무 + mirrored field 4종 정의. **무엇을 sync 하는지** 정의.
- **ADR-063 (본 ADR — atomic invariant)**: bump 시 3 file 동시 처리 + PR ordering. **어떻게 sync 하는지 + 작성 단계 invariant** 정의.

본 ADR 은 ADR-016 의 amendment 가 아닌 별도 정책 — ADR-016 의 sync mechanism 을 atomic 으로 강제하는 layer.

### 결정 7: ADR-061 §결정 5 정합 — sanity check 3종 적용

ADR-061 §결정 5 (script-writing sanity check) 와 정합 — version bump 작업도 다음 3종 sanity check 의무:

- diff inspection: `git diff --stat` 로 plugin.json + CHANGELOG.md 변경 확인
- lint re-run: `bash scripts/check-marketplace-parity.sh` 즉시 실행 (drift 사전 확인)
- sample inspection: marketplace.json mirrored field 확인 (`gh api /repos/mclayer/marketplace/contents/.claude-plugin/marketplace.json` 또는 직접 fetch)

### 결정 8: Self-application

본 ADR 자체 분류 = `is_transitional: false` (영구 정책). codeforge plugin family 의 영구 atomic coordination 표준.

본 ADR 도입 시점에 marketplace.json sync PR 의무 (3-file atomic) — 본 PR 자체가 version bump 동반하면 self-application 첫 사례.

### 결정 9: ArchitectAgent Phase 1 marketplace sync proactive self-check trigger (Amendment 1, CFP-597)

**Context (proactive vs reactive 시점 갭)**: 기존 §결정 1-8 = 작성/PR-open 단계 invariant + 사후 감지 channel (`check-marketplace-parity.sh`). codeforge-design lane 의 ArchitectAgent (chief author) 가 Phase 1 산출물 commit 시점에 mirrored field diff 를 인지하지 못하면 — Change Plan / verdict packet / Phase 2 PR open 모두 거친 후에야 reactive lint 가 fire. CFP-534 sentinel #3 evidence (12:10 codeforge-pmo plugin.json 0.1.1 → 0.1.2 PATCH bump 동반 marketplace.json sync 부재 → workflow FAIL reactive 감지) 가 본 gap 식별.

**ADR-065 boundary 보존**: ADR-065 (non-marketplace 7-item self-check) §결정 5 = "marketplace 영역 self-check 는 ADR-063 SSOT — 본 ADR scope 외" + "cross-ref only — 중복 codification 회피". 본 결정 9 = ADR-063 SSOT 안 marketplace 영역 ArchitectAgent self-check trigger codify. ADR-065 §결정 1 7-item 을 8-item 으로 확장하는 대신 ADR-063 본문에서 통합 — SSOT drift 차단.

**3-layer proactive forcing function**:

| Layer | 시점 | 책임 주체 | Mechanism |
|---|---|---|---|
| 1 | ArchitectAgent §3 commit 직전 | ArchitectAgent (codeforge-design chief author) | `git diff <plugin>/.claude-plugin/plugin.json` mirrored field 4종 (`name` / `version` / `description` / `author`) 변경 감지 self-check |
| 2 | Change Plan §13 declarative declare | ArchitectAgent (산출물 작성) | `marketplace_sync_required: <bool>` + `mirrored_fields_changed: [<enum>]` + `triggering_plugins[]` sub-row 의무 (silent skip 금지 — `false` 일 때도 명시 declare) |
| 3 | Phase 2 PR open 시점 | Orchestrator (monopoly) | Change Plan §13 lookup → `marketplace_sync_required: true` 감지 시 GitOpsAgent (codeforge-pmo) spawn → marketplace sync PR open + merge (ordering = §결정 2 권장 — marketplace PR 선행 merge) |

기존 reactive channel (`check-marketplace-parity.sh`) 은 defense-in-depth 로 보존. 본 결정 9 = 작성 시점 인식 forcing function 추가.

**ArchitectAgent §3.6 self-check 행위** (codeforge-design plugin sibling carrier):
1. `git diff` 로 Phase 1 산출물 안 `<plugin>/.claude-plugin/plugin.json` mirrored field 4종 비교
2. 변경된 field enum 도출 → `mirrored_fields_changed[]` (예: `[version]`, `[version, description]`)
3. Change Plan §13 sub-row 채움 — `marketplace_sync_required` (bool) + `mirrored_fields_changed[]` + `triggering_plugins[]` (변경 영향 받은 plugin 명단)
4. NA 케이스 (mirrored field diff 0건) = `marketplace_sync_required: false` 명시 declare 의무 (silent skip 차단)

**Change Plan §13 sub-row schema**:
```yaml
marketplace_sync_required: <bool>            # NEW (ADR-063 Amendment 1 / CFP-597)
mirrored_fields_changed: [<enum: name|version|description|author>]
triggering_plugins:
  - <plugin-name> (<bump-kind: MAJOR|MINOR|PATCH>)
```

**review-verdict-v4 v4.5 schema MINOR bump** (carrier: ADR-008 §결정 2 "새 선택 필드 추가"):
```yaml
marketplace_sync_declared: <bool>   # NEW (ADR-063 Amendment 1 / CFP-597, v4.5 MINOR)
                                     # ArchitectPL verdict packet 안 marketplace sync trigger declare 결과
                                     # true = Change Plan §13 declare 채움 완료 (true 또는 false 명시), false = §13 declare 누락
                                     # 적용 lane: design lane 만 (code/security lane = optional, omit 가능)
```

ADR-065 의 `mechanical_self_check_passed` 와 **별 boolean field** 운영 (verdict packet 안 분리된 marker) — ADR-063 marketplace 영역 ↔ ADR-065 non-marketplace 영역 boundary 정합.

**Orchestrator → GitOpsAgent §3.6 spawn flow** (Phase 2 PR open 시점, ADR-039 subagent monopoly 정합):
- Orchestrator inline 행위 = Change Plan §13 lookup + spawn 결정 (Inline whitelist "Status report" 정합)
- GitOpsAgent §3.6 (codeforge-pmo sibling carrier, Phase 2 deliverable) = marketplace repo worktree 신설 + marketplace.json sync + PR open + ordering 강제

**Self-application 첫 사례 (본 carrier)**:
본 ADR-063 Amendment 1 도입 PR 자체가 codeforge-design / codeforge-pmo / codeforge-review 3 plugin.json mirrored field (`version`) bump 동반 — Amendment 1 first applied case 시연 의무. Change Plan §13 declare + verdict packet `marketplace_sync_declared: true` + GitOpsAgent spawn 5-row trigger_chain evidence 모두 충족 시 self-application 성공.

**Hotfix bypass**: §결정 4 `hotfix-bypass:marketplace-atomic` label 그대로 — Amendment 1 별도 bypass channel 미도입 (단일 label family 유지).

### 결정 10: Self-application — Amendment 1 ratchet 검증

본 Amendment 1 = 강화 방향 only (proactive layer 추가 + invariant 강도 상승). ADR-064 self-application top-down ratchet 정합 — 약화 방향 (예: proactive trigger 약화 / boundary 이동 / scope 축소) 미해당. ADR-058 §결정 5 sunset_justification = frontmatter 명시 (`N/A — permanent governance policy. ADR-064 §self-application top-down ratchet 정합. ADR-058 §결정 5 약화 방향 발의 차단 logic 통과.`).

본 ADR-063 amendment 발의 시 매번 ratchet 방향 검증 의무 — 강화 방향만 허용.

### 결정 11: Description proactive lint mandate (Amendment 2, CFP-631)

**Context (Amendment 1 design-time + reactive lint 갭)**: Amendment 1 (§결정 9) = ArchitectAgent §3.6 self-check + Change Plan §13 declare + Orchestrator → GitOpsAgent spawn 3-layer 모두 design-time forcing function. 기존 reactive lint = `check-marketplace-parity.sh` warning tier post-PR 사후 감지. 두 layer 사이 PR-time mechanical enforce 영역 부재 — author 가 Amendment 1 self-check skip 또는 sibling sync drift 시점 author 인식 부재 시 reactive lint 가 작동하기까지 mirror drift 가 main 노출 가능.

**6 sample 누적 drift evidence** (CFP-619 retro §5.2 SSOT):

| Sample | CFP | Drift 유형 | 감지 channel | Recovery |
|---|---|---|---|---|
| 1 | CFP-387 | 초기 marketplace registration policy drift | post-PR `check-marketplace-parity.sh` | manual sibling PR |
| 2 | CFP-393 | KPI workflow description sync gap | post-PR `check-marketplace-parity.sh` | manual sibling PR |
| 3 | CFP-423 | Python script convention description gap | post-PR `check-marketplace-parity.sh` | manual sibling PR |
| 4 | CFP-597 | ADR-063 Amendment 1 도입 시점 description 동기화 | self-application 1st case | atomic sync 동반 |
| 5 | CFP-612 | description over-escape quote bug (`\&#34;...\&#34;`) | post-PR FAIL + commit 54509bd 별도 PR | manual fix-up commit |
| 6 | CFP-619 | description summary vs verbatim drift (PR #102 → #103) | post-PR FAIL → commit `c199dee` "byte-identical fix" follow-up | manual byte-identical fix follow-up PR |

**Blocking-on-pr tier 직접 시작 근거** (Codex Touchpoint #2 P1 #1 inline 정정):
- ADR-060 §결정 5 default warning-mode 의 **explicit exception** (사용자 directive Story §1)
- ADR-060 §결정 19 (Amendment 6, CFP-509) `auto_blocking` manual gate path — `recurrence.count: 6` + `threshold: 6` + `promotion_trigger: auto_blocking` 명시 (manual carrier-driven transition)
- §결정 6 AND-condition (PR cumulative ≥20 / failure_threshold 0 / sibling deps) 의 의의는 본 carrier Story 자체가 별도 promotion carrier 역할 합병으로 충족 — actual transition 의무 통과
- ADR-060 Amendment 2 §결정 16 (warning-tier `bypass_label` policy) 와 무관 (해당 §결정 = warning tier optional bypass_label, 본 결정 11 = blocking tier mandatory bypass_label)

**Mandate**:
- mirrored field `description` 의 PR-time mechanical proactive lint 의무 (wrapper plugin.json description ↔ marketplace.json `plugins[codeforge].description` byte-identical verify)
- tier: blocking-on-pr — ADR-060 §결정 5 default warning explicit exception (사용자 directive Story §1 + 6 sample 누적 evidence base) + §결정 19 (Amendment 6) auto_blocking manual gate, 위 "Blocking-on-pr tier 직접 시작 근거" 블록 참조
- bypass channel: `hotfix-bypass:marketplace-description-verbatim` label (ADR-024 Amendment 3 §결정 6.A per-entry namespace family member #16)

**Carrier components**:
- `scripts/check-marketplace-description-verbatim.sh` — bash lint script (algorithm: PR diff 안 description 변경 감지 → 변경 있을 때만 jq extract + byte compare + diff snippet emit)
- `templates/github-workflows/marketplace-description-verbatim.yml` — canonical workflow SSOT (ADR-005 invariant)
- `.github/workflows/marketplace-description-verbatim.yml` — byte-identical mirror
- `docs/evidence-checks-registry.yaml` entry `marketplace-description-verbatim` (blocking-on-pr tier, recurrence count=6, last_occurrence=2026-05-14)
- `docs/inter-plugin-contracts/label-registry-v2.md` v2.8 → v2.9 PATCH (§3 yaml hotfix-bypass:* 16번째 family member append)

**2-layer proactive forcing function** (Amendment 1 + Amendment 2 layered):

| Layer | 시점 | Mechanism |
|---|---|---|
| Amendment 1 (CFP-597) | Phase 1 산출물 commit 직전 (design-time) | ArchitectAgent §3.6 self-check + Change Plan §13 declarative declare + Orchestrator → GitOpsAgent §3.6 spawn |
| **Amendment 2 (본 결정 11, CFP-631)** | **pull_request event (PR-time)** | **GitHub Actions workflow `marketplace-description-verbatim.yml` 자동 enforce — `scripts/check-marketplace-description-verbatim.sh` byte-identical verify + 실패 시 PR 차단 (blocking-on-pr)** |

기존 reactive layer (`check-marketplace-parity.sh` warning) 도 defense-in-depth 로 보존 — 본 Amendment 2 가 author 인식 시점과 PR open 시점 사이 gap 을 mechanical lint 로 cover.

**Algorithm overview** (`check-marketplace-description-verbatim.sh`):
1. `git diff "${BASE_REF}..HEAD" -- .claude-plugin/plugin.json` 으로 description field 변경 감지 — 변경 없음 → exit 0 skip (false alarm 차단)
2. wrapper plugin.json description extract (`jq -r '.description'`)
3. marketplace.json fetch (`gh api`) + plugins[codeforge].description extract
4. byte-identical compare (`[[ "$P_DESC" == "$M_DESC" ]]`)
5. mismatch → diff snippet + exit 1
6. match → exit 0 (PASS)

**Error handling** (exit code 2 = environment error): jq missing / gh api fail / json malformed — actionable message + install / auth instruction.

**Bypass discipline** (ADR-024 Amendment 3 §결정 6.A 정합):
- `hotfix-bypass:marketplace-description-verbatim` label 부착 시 workflow skip
- bypass audit comment 자동 발의 (gh pr comment) — 24시간 이내 marketplace sync 의무 명시
- bypass 발생 시 `docs/audit/` 에 audit row 의무

본 channel 은 audit-trailed exception only — 정상 운영에서 사용 금지.

### 결정 12: Self-application — Amendment 2 ratchet 검증 + 본 carrier 첫 적용 사례

**Ratchet 검증**: 본 Amendment 2 = 강화 방향 only (PR-time mechanical enforce layer 추가 + invariant 강도 상승 — description field warning tier post-PR → blocking-on-pr PR-time). ADR-064 self-application top-down ratchet 정합 — 약화 방향 (예: PR-time enforce skip / warning 다운그레이드 / scope 축소) 미해당. ADR-058 §결정 5 sunset_justification = frontmatter `is_transitional: false` permanent governance policy 유지.

**Self-application 첫 사례 (본 carrier)**:
본 ADR-063 Amendment 2 도입 PR 자체가 wrapper plugin.json mirrored field 2종 (`version` 5.47.0 → 5.48.0 MINOR + `description` tail append Amendment 2 carrier note) bump 동반 — Amendment 2 first applied case 시연 의무. marketplace sibling sync PR 선행 merge → wrapper Phase 1 PR merge ordering 강제. Phase 2 PR (lint script + workflow yml 도입) merge 후 future PR 부터 본 lint 활성 — Phase 1 PR 자체는 lint 영역 외 (chicken-and-egg 회피, ADR-063 §결정 2 anti-pattern 정합 운영).

**Future amendment 발의 검증**: 본 ADR-063 amendment 발의 시 매번 ratchet 방향 검증 의무 — 강화 방향만 허용. Amendment 3+ 도입 시 (a) description 외 mirrored field 추가 PR-time enforce (예: keywords field 등 신규 mirrored field expansion) (b) lint frequency 강화 (예: per-commit hook) (c) 6 lane plugin description 확장 — 모두 강화 방향 후보. 약화 방향 (description warning tier 다운그레이드 / blocking 해제 / scope 축소) 미허용.

## 결과

### 긍정
- 3-Wave drift 패턴 차단 — atomic invariant 명시화
- CFP-387 chicken-and-egg + CFP-393 catch-up drift 재발 차단
- ADR-016 + ADR-037 + 본 ADR-063 = version bump triplet 완성 (무엇 / 의미 / 방법)

### 부정 / Trade-off
- bump 작업 cost 증가 — 항상 marketplace sync PR 병행 필요
- cross-repo coordination overhead (다중 worktree / PR 관리)
- 긴급 hotfix 시 bypass 채널 의존

### 영향 받는 영역
- 모든 plugin family version bump 작업 (wrapper + 6 lane plugin)
- marketplace sync PR open 의무 (Phase 2 PR pair → Phase 2 PR triplet)
- 별도 follow-up: pre-commit hook / 신규 atomic lint

## 해소 기준

N/A — permanent policy

## 다이어그램 (선택)

```mermaid
flowchart TD
    Bump[plugin.json mirrored field<br/>변경 필요?] -->|yes| Triplet[3-file atomic invariant<br/>발화]
    Bump -->|no| Skip[본 ADR 영역 외]
    Triplet --> P1[plugin.json<br/>+CHANGELOG.md<br/>변경 in plugin PR]
    Triplet --> P2[marketplace.json<br/>변경 in marketplace PR]
    P1 --> Order[ordering: marketplace<br/>PR 선행 merge]
    P2 --> Order
    Order --> CI{plugin PR CI<br/>marketplace check?}
    CI -->|PASS| Merge[plugin PR merge]
    CI -->|FAIL| Reorder[marketplace PR merge<br/>+ plugin PR rerun]
    Reorder --> CI
```

## 관련 파일

- `CLAUDE.md` — version bump 표준 cross-ref
- `scripts/check-marketplace-parity.sh` — 사후 감지 SSOT (CFP-50 / ADR-016 / ADR-023). CFP-457 cleanup 후 단독 유지 (`check-marketplace-sync.sh` CFP-34 deprecated).
- `scripts/check-marketplace-description-verbatim.sh` — Amendment 2 carrier (CFP-631 / 결정 11 — description PR-time mechanical enforce)
- `templates/github-workflows/marketplace-description-verbatim.yml` — Amendment 2 canonical workflow SSOT (ADR-005 byte-identical mirror invariant)
- `.github/workflows/marketplace-description-verbatim.yml` — Amendment 2 self-app mirror
- `docs/evidence-checks-registry.yaml` — Amendment 2 entry `marketplace-description-verbatim` (blocking-on-pr tier, recurrence count=6)
- `docs/inter-plugin-contracts/label-registry-v2.md` — Amendment 2 carrier `hotfix-bypass:marketplace-description-verbatim` 16번째 family member (v2.8 → v2.9 PATCH)
- `docs/adr/ADR-016-marketplace-registration-policy.md` — sibling sync policy
- `docs/adr/ADR-037-plugin-version-bump-rule.md` — version semantics SSOT
- `docs/adr/ADR-024-story-scoped-branch-policy.md` — hotfix-bypass label family (Amendment 3)
- `docs/adr/ADR-061-python-script-writing-convention.md` — sanity check 3종 정합
- `docs/adr/ADR-060-evidence-enforceable-promotion-framework.md` — §결정 5 default warning exception + §결정 19 (Amendment 6, CFP-509) auto_blocking manual gate (Amendment 2 carrier evidence base — blocking-on-pr 직접 시작 근거 SSOT)
