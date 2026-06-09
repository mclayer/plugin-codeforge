---
kind: registry
registry: evidence-check
version: "1.4"
canonical_repo: mclayer/plugin-codeforge
canonical_path: docs/inter-plugin-contracts/evidence-check-registry-v1.md
date: 2026-05-19
status: Active
authors:
  - CFP-389 (Initial v1.0 — evidence-enforceable promotion framework SSOT, ADR-060 carrier)
  - CFP-455 (MINOR bump v1.0 → v1.1 — current_tier required 전환 + 4-tier enum 본문 강조, ADR-060 Amendment 2 carrier)
  - CFP-509 (MINOR bump v1.1 → v1.2 — recurrence field 정식 도입 + ADR-060 promotion gate auto-firing, ADR-060 Amendment 6 carrier)
  - CFP-963 (MINOR bump v1.2 → v1.3 — neighbor `network_scope_actual` optional schema field 신설 §14 Lane Evidence row 13번째 optional field carrier, ADR-081 Amendment 4 §결정 D1.D 본문 확장의 mechanical enforcement layer + ADR-060 Amendment 14 §결정 28 신설 동반 carrier, Codex TP#4 CX-963-4 P3 finding integration)
  - CFP-2061-S2 (MINOR bump v1.3 → v1.4 — `entries[].tags` optional list field 신설 §3.2 codify, closed-set enum [security, consumer-whitelist] 검사 dead 자동 제외 hard-exclude 가드 carrier. SSOT = docs/check-dead-criteria.yaml. 신규 ADR 0 — doc-only fast-path ADR-054, framework data-substrate 하위 영역 append. CFP-2061-S1 §11 FU-1 tag SSOT 단일화 충족)
related_adrs:
  - ADR-008  # Inter-plugin Contract Versioning (kind:registry SemVer 정합)
  - ADR-010  # Inter-plugin Contract Sibling Sync (kind:registry scope 외 명시)
  - ADR-024  # Story-scoped branch policy (Amendment 3 audit-trailed exception channel)
  - ADR-041  # doc-locations
  - ADR-050  # parallel epic + warning mode prior art
  - ADR-058  # ADR sunset criteria mandate (직접 동인)
  - ADR-060  # Evidence-enforceable promotion framework (carrier)
related_files:
  - docs/evidence-checks-registry.yaml
  - docs/inter-plugin-contracts/MANIFEST.yaml
  - docs/doc-locations.yaml
  - scripts/check-adr-sunset-criteria.sh
  - scripts/check-bypass-audit-comment.sh
  - templates/github-workflows/adr-sunset-criteria.yml
  - CLAUDE.md
---

# evidence-check-registry v1.0

## 1. 목적

codeforge wrapper repo 의 **evidence-enforceable governance check** SSOT. ADR-058 declaration 의 mechanical enforcement 점진 적용 framework (ADR-060) 의 schema doc + 운영 룰.

각 evidence check entry 는 `docs/evidence-checks-registry.yaml` 의 row 로 정의되며, 본 schema 가 row 의 필수 / optional 필드 + 4-tier enforcement enum + promotion gate + bypass channel + audit trail 양식을 규정.

## 2. Schema (kind:registry, wrapper-owned canonical)

- **kind**: registry (cross-cutting protocol, NOT typed inter-plugin schema)
- **lint chain**: `check-doc-frontmatter.sh` + `check-doc-section-schema.sh` (기존 3 kind:registry entry 와 동일).
- **MANIFEST.yaml 등록**: `registries:` 블록 entry (label-registry / comment-prefix-registry 패턴) — `check-inter-plugin-contracts.sh` scope 외.
- **doc-locations.yaml 등록**: 신규 doc type `evidence_check_registry` row (ADR-041 §결정 정합).

## 3. 항목 (registry yaml entry row 필드 schema)

각 entry 는 다음 필드 보유:

| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `name` | string | 필수 | entry 식별자 (kebab-case). 예: `adr-sunset-criteria`. 전역 unique. |
| `description` | string | 필수 | 본 entry 가 검증하는 정책 요약 (1-3 문장). |
| `detect_command` | string | 필수 | violation 감지 lint 실행 명령 (절대 또는 repo-relative path). 예: `bash scripts/check-adr-sunset-criteria.sh`. |
| `workflow` | string | 필수 | GitHub Actions workflow yaml path. 예: `templates/github-workflows/adr-sunset-criteria.yml`. |
| `current_tier` | enum | **필수 (v1.1, CFP-455 / ADR-060 Amendment 2 — required 전환)** | enforcement tier. enum = `warning` / `blocking-on-pr` / `blocking-on-merge` / `hotfix-bypass` (대소문자 / 공백 정확 일치). 결정 3 (ADR-060). 미보유 entry = `scripts/check-evidence-registry.sh` exit 1 (validation FAIL). |
| `bypass_label` | string | optional — tier 별 의무 분리 (v1.1, CFP-455 / ADR-060 Amendment 2 §결정 16): `warning` = omit 권고 (non-blocking, bypass 의미 부적용) / `blocking-on-pr` / `blocking-on-merge` = optional (운영 장애 hotfix 채널 도입 가능) / `hotfix-bypass` = **required** (정의상 bypass channel SSOT) | bypass label name. namespace = `hotfix-bypass:<entry-name>` (예: `hotfix-bypass:adr-sunset`). per-entry namespace 분리 의무 (ADR-060 §결정 7). |
| `bypass_audit_lint` | string | optional (bypass_label 정의 시 의무) | audit comment 존재 검증 lint 명령. 예: `bash scripts/check-bypass-audit-comment.sh`. ADR-060 §결정 8. |
| `promotion_criteria` | object | 필수 (current_tier=warning 시) | warning → blocking 승격 gate 정의. 필드: |
| `promotion_criteria.pr_cumulative_min` | int | 필수 | 본 entry merge 후 카운트 시작, throughput 독립 PR 누적 (ADR-060 §결정 10). 기본 `20`. |
| `promotion_criteria.failure_threshold` | int | 필수 | bypass label 외 failure count 허용 임계 (0 = 무사고). 기본 `0`. |
| `promotion_criteria.sibling_dependencies` | list[string] | optional | 본 entry 승격 전 merged 필요한 sibling Story keys. 예: `[CFP-390, CFP-391]`. |
| `promotion_criteria.evidence_artifacts` | list[string] | 필수 | 승격 carrier PR 의 evidence 산출물 유형 (자동화 카운터 미도입 시 manual 첨부 의무). |
| `modal_anti_pattern_dictionary` | object | optional (lint 가 모달 어휘 검사 포함 시) | 모달 어휘 anti-pattern 사전. 필드: `version` (string, e.g., `"1.0"`) + `dictionary` (list[string]). versioning 의무 (확장 어휘 도입 시 MINOR bump). |
| `introduced_by` | string | 필수 | 본 entry 도입 carrier Story key. 예: `CFP-389`. |
| `owner_adr` | string | 필수 | 본 entry 가 검증 대상으로 삼는 정책 ADR. 예: `ADR-058`. |
| `carrier_adr` | string | 필수 | 본 entry 도입의 carrier ADR (framework SSOT 외). 예: `ADR-060`. |
| `status` | enum | optional (default `Active`) | entry lifecycle. enum = `Active` / `Deprecated` / `Archived`. |
| `recurrence` | object | optional (v1.2, CFP-509 / ADR-060 Amendment 6 — recurrence-driven promotion 정식 도입) | recurrence tracking. 필드: |
| `recurrence.count` | int | 필수 (recurrence 정의 시) | 본 entry 도입 후 누적 위반 발생 횟수 (machine-usable). 기본 `0`. |
| `recurrence.last_occurrence` | ISO8601 UTC | optional | 마지막 위반 timestamp (ISO8601 UTC Z suffix). count = 0 시 omit 가능. |
| `recurrence.threshold` | int | optional (default `3`) | promotion gate auto-firing threshold. recurrence.count ≥ threshold 시 warning → blocking-on-pr 승격 자동 발화 신호 (별도 carrier 가 actual blocking 부여). |
| `recurrence.promotion_trigger` | enum | optional (default `none`) | recurrence-based promotion 행동 enum. enum = `none` / `advisory` (PR comment 만) / `auto_blocking` (별도 carrier 강제). 기본 `none`. |

### 3.1 §14 Lane Evidence row 의 optional field (v1.3, CFP-963 — ADR-081 Amendment 4 + ADR-060 Amendment 14 carrier)

**`network_scope_actual`** (Codex worker dispatch lane evidence 영역 신규 optional field — Lane Evidence row 13번째 field) — v1.3 MINOR bump 신규 codify (CFP-963 / ADR-060 Amendment 14 §결정 28 + ADR-081 Amendment 4 §결정 D1.D 본문 확장 carrier, Codex TP#4 CX-963-4 P3 finding integration).

| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `lane_evidence[].network_scope_actual` | enum | optional (Codex dispatch lane only — omit-on-N/A pattern) | Codex worker dispatch 시점에 실제 적용된 network scope. 4-tier enum value SSOT (ADR-081 Amendment 4 §결정 D1.D 정합): `offline` / `repo-fetch-only` / `web-fetch` / `offline_substitution_declared`. spawn-prompt 안 `network_scope` declare value 와 실제 invocation 의 actual scope 간 mismatch 추적 영역 (graceful degradation step (c) 의 §14 evidence trace SSOT). 본 field present 시 4-tier enum 안 정확 1 value 보유 의무 — `codex-network-scope-presence` lint 가 membership check 만 (semantic adequacy 검증 불가). Codex dispatch 아닌 lane row = omit (backward-compat default — ADR-031 §14 기존 12 field schema 영향 0). |

**backward-compat**: 본 field 는 optional + omit-on-N/A pattern — ADR-031 §14 기존 12 field schema 영향 0 (1.1↔1.2↔1.3 backward-compat 보존). 기존 entry / 기존 §14 lane_evidence row 는 본 field 없이 정상 통과 (warning tier first, ADR-060 §결정 5 정합).

**field semantic**:
- 4-tier enum value 의미 = ADR-081 Amendment 4 §결정 D1.D 본문 SSOT (offline = file-IO-only / repo-fetch-only = own-repo + git fetch / web-fetch = cross-repo egress 허용 / offline_substitution_declared = codex CLI 미가용 substitution path activate)
- spawn-prompt 의 `network_scope` declare 와 실제 invocation 의 actual scope mismatch 감지 시 record (예: spawn declare = `web-fetch` but actual = `repo-fetch-only` 영역 fallback — Story §10 marker `[codex-substitution-scope-declared: <scope-enum>]` 와 cross-validate)
- `codex-network-scope-presence` lint (ADR-060 Amendment 14 §결정 28 / CFP-963 Phase 2 carrier) 가 §14 row 안 본 field 의 4-tier enum 정합 (membership check) 검증

### 3.2 entry 의 `tags` optional field (v1.4, CFP-2061-S2 — 검사 dead 자동 제외 hard-exclude 가드 carrier)

**`entries[].tags`** (검사 dead 자동 제외 가드 영역 신규 optional list field) — v1.4 MINOR bump 신규 codify (CFP-2061-S2 — 검사 dead 객관 판정 기준 SSOT `docs/check-dead-criteria.yaml` 의 양보불가 가드 carrier). 신규 ADR 0 (doc-only fast-path, ADR-054 — framework data-substrate 하위 영역 optional field append, recurrence/network_scope_actual 선례 동형).

| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `entries[].tags` | list[enum] | optional (omit-on-N/A pattern) | 검사 분류 tag. closed-set enum = `security` / `consumer-whitelist`. 본 field 보유 검사는 `docs/check-dead-criteria.yaml` 의 dead 판정에서 **hard-exclude** (객관 기준 충족해도 자동 dead 후보 불가 — 양보불가 가드, 오삭 차단). list 이므로 다중 tag 가능 (OR 의미 — 한 tag 라도 보유 시 제외). 미보유 entry = 기존 동작 영향 0. |

**tag 의미 SSOT** (closed-set, `docs/check-dead-criteria.yaml` §2 exclude_tags 정합):
- `security` — 보안 안전망 검사. 드물게 fire 하나 보안 사고 시 last-line-of-defense → 오삭 시 보안 회귀. **determination = presence-based (명시 부착)** — 작성자가 `tags: [security]` 명시 (false-negative=오삭 회피 우선). owner_adr 보안 ADR 자동 분류(derive)는 보조 신호로만 검토 가능.
- `consumer-whitelist` — consumer repo mirror 의무 workflow 대응 검사. **determination = derive-based (단일 출처 재사용)** — 멤버십은 `templates/scripts/consumer_applicable_workflows.txt`(ADR-083 §4.12 positive whitelist) 에서 derive (entry.workflow basename ↔ whitelist 줄 일치). 별도 명시 tag 신설 금지 — 명시 `tags: [consumer-whitelist]` 와 OR (둘 중 하나라도 성립 시 제외). 이중 정의 금지 (CFP-2061-S2 AC-4 tag SSOT 단일화).

**tag SSOT 단일화 (CFP-2061-S1 §11 FU-1 충족)**: 본 `tags` field 의 security / consumer-whitelist 2 값 = S1 정당화 순증 게이트(`increment-justification-presence`) exempt 판정과 **동일** SSOT (`docs/check-dead-criteria.yaml` exclude_tags.closed_set). S1 게이트 exempt + S5 dead 제외 양 lane 이 단일 참조 — 이중 정의 drift 금지.

**backward-compat**: optional + omit-on-N/A — 기존 146 entry 영향 0 (1.3 ↔ 1.4 backward-compat). 기존 entry 는 `tags` 없이 정상 통과. 본 field 의 mechanical lint enforcement 는 본 S2 scope 외 (doc-only fast-path — 정적 SSOT 만; S5 가 삭제 시점에 본 field 를 dead 제외 신호로 소비). 향후 advisory lint 필요 판정 시 별도 carrier (full-lane 분기 — CFP-2061-S2 §3 OOS8).

## 4. 변경 규칙 (SemVer, ADR-008 정합 + 4-tier enforcement enum 정식 도입)

**4-tier enum SSOT (v1.1, CFP-455 / ADR-060 Amendment 2 — required 전환 완료)**: 모든 registry yaml entry 는 다음 4 enum 중 정확히 하나의 `current_tier` 보유 의무 (대소문자 / 공백 정확 일치). 위반 시 `scripts/check-evidence-registry.sh` exit 1 (validation FAIL) + warning mode 단계 PR comment 경고 + blocking mode 승격 시 PR block.

| tier | 동작 | branch protection 영향 | 사용 시점 |
|---|---|---|---|
| `warning` | continue-on-error 또는 non-required check. PR comment / job summary 경고만. | `required_status_checks.contexts` 미부착 | 첫 도입 / 운영 신뢰도 검증 단계 |
| `blocking-on-pr` | required check. PR merge 차단. | `required_status_checks.contexts` 부착 | 승격 gate 통과 후 정식 enforce |
| `blocking-on-merge` | post-merge guard (예: phase-gate-mergeable). PR open 단계 통과, merge 시점 차단. | `required_status_checks.contexts` 부착 | 동적 검증 (PR 상태 변화 기반) |
| `hotfix-bypass` | bypass label 적용 PR 만 skip + audit comment 의무. label 부재 시 blocking-on-pr 등가. | `required_status_checks.contexts` 부착 (+ bypass workflow) | 운영 장애 hotfix 통로 필수 시 |

**v1.0 → v1.1 MINOR bump (CFP-455, 2026-05-12)**: `current_tier` 필드 optional → **required** 전환 + 기존 22 entry retroactive 분류 검증 (모두 현행 `current_tier` 보유 verified — mechanical regression 0건). schema 정합 mechanical 강제 = `scripts/check-evidence-registry.sh` (Phase 2 PR scope) + `templates/github-workflows/evidence-registry-check.yml` (Phase 2 PR scope, warning mode 첫 도입).

**v1.1 → v1.2 MINOR bump (CFP-509, 2026-05-13)**: `recurrence:` field 정식 도입 (optional object — count / last_occurrence / threshold / promotion_trigger). machine-usable recurrence metric framework 제공 — CFP-490 description-only `recurrence_count` (lane-evidence-trail entry) 의 schema 흡수 + ADR-060 §결정 새 추가 (recurrence.count ≥ recurrence.threshold 시 promotion gate auto-firing advisory). 22 entry retroactive 분류 검증 (기존 entry 는 recurrence 미정의 = backward-compat default).

**v1.3 → v1.4 MINOR bump (CFP-2061-S2, 2026-06-09)**: `entries[].tags` optional list field 정식 도입 (closed-set enum `security` / `consumer-whitelist` — 검사 dead 자동 제외 hard-exclude 가드). SSOT = `docs/check-dead-criteria.yaml` (검사 dead 객관 판정 기준 + 양보불가 가드). 신규 ADR 0 — doc-only fast-path (ADR-054), framework data-substrate 하위 optional field append (recurrence / network_scope_actual 선례 동형). consumer-whitelist = `templates/scripts/consumer_applicable_workflows.txt`(ADR-083) derive 권장 (명시 tag 와 OR). 기존 146 entry 영향 0 (optional + omit-on-N/A pattern, backward-compat). CFP-2061-S1 §11 FU-1 tag SSOT 단일화 충족 (S1 게이트 exempt + S5 dead 제외 동일 참조). MANIFEST `evidence_check_registry` row `version: "1.3"` → `"1.4"` 동반 (sibling sync 면제 kind:registry, MANIFEST versioning 추적만).

**v1.2 → v1.3 MINOR bump (CFP-963, 2026-05-19)**: `lane_evidence[].network_scope_actual` optional field 정식 도입 (§14 Lane Evidence row 13번째 optional field — 4-tier enum value SSOT `offline` / `repo-fetch-only` / `web-fetch` / `offline_substitution_declared`, ADR-081 Amendment 4 §결정 D1.D 본문 확장 정합). ADR-060 Amendment 14 §결정 28 carrier — 12번째 warning-tier evidence-checks-registry entry `codex-network-scope-presence` 가 §14 row 안 본 field membership check 검증. Codex TP#4 CX-963-4 P3 finding integration. 기존 entry / 기존 §14 row 는 본 field 없이 정상 통과 (optional + omit-on-N/A pattern, backward-compat). **MANIFEST drift catch-up 동반**: `docs/inter-plugin-contracts/MANIFEST.yaml` registries 블록 `evidence-check-registry-v1.md` row 의 `version: "1.1"` (CFP-509 v1.1→v1.2 sibling MANIFEST sync miss 영역의 silent stale — INV-1 parity drift) → `"1.3"` atomic catch-up (CFP-509 v1.1→v1.2 sibling sync 영역 + CFP-963 v1.2→v1.3 신규 MINOR 양 layer 단일 PR row write, INV-1 parity ratchet). 본 catch-up annotation = MANIFEST row inline comment SSOT.

## 5. Bypass channel 운영 (ADR-024 Amendment 3 + ADR-060 §결정 7-8)

### 5.1 권한자

- repo admin only. solo-dev 환경 = 사용자 본인 (mccho8865).
- contributor 추가 시 재논의 (별도 carrier).

### 5.2 namespace 분리

- per-entry namespace 의무: `hotfix-bypass:<entry-name>` (예: `hotfix-bypass:adr-sunset`).
- 단일 global bypass label 금지 (ADR-060 §대안 E 거부 정합) — scope 통제 우선.

### 5.3 Audit trail 3중 안전망

1. **Audit comment**: GitHub Actions bot 가 PR comment 1개 자동 append. schema (CI-parsable, ADR-060 §결정 8):
   ```
   [hotfix-bypass-audit] PR=<number> label_applied_by=<user> reason=<bypass_reason_textbox> ADR_files=<comma-separated-paths> timestamp=<ISO8601>
   ```
   - `timestamp` = ISO8601 UTC Z suffix 의무 (fix-event-v1 schema clarification 정합).
   - `reason` = PR description `### Bypass reason` 섹션 textbox 본문 (workflow 추출, 부재 시 PR block 의무).

2. **Audit assertion lint** (`bypass_audit_lint` 필드 정의 entry): bypass label 부착 PR 의 audit comment 1개 이상 존재 검증. 부재 시 PR block (workflow level conditional).

3. **Audit log 집계**: bypass label 적용 PR list quarterly merge 시 `docs/audit/hotfix-bypass-log.md` 자동 append — 별도 carrier scope (CFP-390 또는 신규 carrier). 본 registry 는 schema + bot comment 양식만.

### 5.4 Re-entry 안전망

bypass PR 안 변경 자체가 정책 위반 (재귀 시나리오) → audit comment 에 `[sunset-criteria-deferred]` 또는 entry-specific 태그 자동 추가 + 후속 보완 의무 자동 Issue 발의 (별도 carrier scope).

## 6. 승격 gate (ADR-060 §결정 6, AND condition)

warning → blocking-on-pr / blocking-on-merge 승격 = 3 condition AND:

- **(a) `promotion_criteria.pr_cumulative_min`**: ADR-060 / 본 entry merge 후 첫 main PR merge 일자부터 카운트. `hotfix-bypass:*` label 적용 PR 도 throughput 카운트 (EC-C 정합).
- **(b) `promotion_criteria.failure_threshold = 0`**: bypass label 외 failure count = 0. bypass label 적용 PR 의 lint 결과 skip (failure 미카운트).
- **(c) `promotion_criteria.sibling_dependencies` 모두 merged**: 본 entry 가 다른 Story 의존 시 모두 main merge 완료.

승격 carrier PR (별도 CFP-NNN) 의 `promotion_criteria.evidence_artifacts` 산출물 의무:
- `github_actions_run_history_url` — workflow 실행 이력 page URL.
- `lint_failure_count_zero_proof` — bypass label 외 failure = 0 lint 출력 (gh CLI / API 결과 첨부).
- `pr_cumulative_count_proof` — PR 누적 ≥ threshold 카운트 (gh CLI / API 결과 첨부).

본 3 산출물 부재 시 승격 carrier PR block. 자동화 카운터 인프라 미도입 시 manual 첨부 의무 — 자동화는 별도 carrier 책임.

## 7. 추가 변경 규칙 (Amendment / version 추적)

본 registry 는 ADR-008 §kind:registry SemVer 룰 적용:

- **MAJOR (v1.x → v2.0)**: 기존 entry 필드 제거 / enum 값 제거 / schema BREAKING 변경. 모든 consumer (lint script + workflow + registry yaml) 갱신 의무.
- **MINOR (v1.0 → v1.1)**: 신규 필드 추가 (default value 보유) / enum 값 추가 / `current_tier` required 전환 등. 기존 consumer backward compat 유지.
- **PATCH (v1.0 → v1.0.x)**: schema 문서 clarification / 운영 룰 추가 (필드 변경 없음).

### 완료된 변경 (historical)

- **v1.1 (CFP-455, 2026-05-12 — Accepted)**: `current_tier` optional → required 전환 + tier enum 정식 분류 (기존 22 entry retroactive 분류 검증 — 모두 보유 verified, mechanical regression 0건). MINOR bump. ADR-060 Amendment 2 carrier. CFP-391 (Issue #396) / CFP-412 (Issue #412) 의 closed without delivery 후 재재예약 carrier.
- **v1.2 (CFP-509, 2026-05-13 — Accepted)**: `recurrence:` field 정식 도입 (optional object). MINOR bump (신규 optional field). ADR-060 Amendment 6 carrier. CFP-490 description-only `recurrence_count` (lane-evidence-trail entry, CFP-500 FIX-5 + CFP-451 transient 2회) 의 schema 흡수.
- **v1.4 (CFP-2061-S2, 2026-06-09 — Accepted)**: `entries[].tags` optional list field 정식 도입 (closed-set enum `security` / `consumer-whitelist` — 검사 dead 자동 제외 hard-exclude 가드). MINOR bump (신규 optional field + omit-on-N/A pattern backward-compat). SSOT carrier = `docs/check-dead-criteria.yaml`. 신규 ADR 0 (doc-only fast-path, ADR-054). CFP-2061-S1 §11 FU-1 tag SSOT 단일화 충족. MANIFEST `evidence_check_registry` row "1.3" → "1.4" 동반.
- **v1.3 (CFP-963, 2026-05-19 — Accepted)**: `lane_evidence[].network_scope_actual` optional field 정식 도입 (§14 Lane Evidence row 13번째 optional field — 4-tier enum value SSOT). MINOR bump (신규 optional field + omit-on-N/A pattern backward-compat). ADR-060 Amendment 14 + ADR-081 Amendment 4 carrier. Codex worker dispatch lane evidence 영역 — `codex-network-scope-presence` lint (12번째 warning-tier entry, ADR-060 Amendment 14 §결정 28) 가 §14 row 안 본 field membership check 검증. **MANIFEST drift catch-up 동반** (`docs/inter-plugin-contracts/MANIFEST.yaml` row "1.1" → "1.3" — CFP-509 v1.1→v1.2 sibling MANIFEST sync miss INV-1 parity 영역 + CFP-963 v1.2→v1.3 신규 MINOR 양 layer atomic).

### Tier value transition 첫 사례 — `current_tier: warning → blocking-on-pr` (CFP-1607, 2026-05-25 KST — schema 변경 0, value transition only)

본 entry = 4-tier enum value transition 의 **첫 documenting 사례** (ADR-060 framework first-use blocking-on-pr promotion, ADR-024 Amendment 15 carrier). schema doc body / field definition / enum 값 변경 0건 — 본 section 은 registry yaml 안 `current_tier` field 의 enum value 가 `warning` → `blocking-on-pr` 전환된 첫 사례를 documenting only (forward-reference 영역).

**Transition pattern** (registry yaml entry-level field-level change):

```yaml
# Before (warning tier, advisory dashboard)
- name: per-plugin-cumulative-counter
  current_tier: warning
  status: warning
  recurrence:
    last_occurrence: null
    promotion_trigger: none

# After (blocking-on-pr tier, PR check fail = merge block)
- name: per-plugin-cumulative-counter
  current_tier: blocking-on-pr        # warning → blocking-on-pr ratchet
  status: blocking-on-pr              # status enum 동시 transition
  promoted_by: CFP-1607               # 신규 optional field — promotion carrier Story key
  promoted_date: 2026-05-25           # 신규 optional field — promotion 시점 KST
  recurrence:
    last_occurrence: 2026-05-25T18:00:00+09:00  # ratchet trigger time
    promotion_trigger: warning_to_blocking_on_pr  # transition enum value
```

**Schema invariant 보존**:
- `current_tier` enum 4-value SSOT (L57) 변경 0 — `warning` / `blocking-on-pr` / `blocking-on-merge` / `hotfix-bypass` 동일.
- `status` enum value transition (warning → blocking-on-pr) — schema body 변경 0.
- 신규 optional field 2종 (`promoted_by` + `promoted_date`) — entry-level documenting only (schema body 강제 추가 아님, ADR-060 framework first-use precedent emission).
- `recurrence.promotion_trigger` enum value 신규 (`warning_to_blocking_on_pr`) — schema body 의 enum 값 추가가 아닌 entry-level prose only.

**ADR-060 §결정 6 promotion gate AND 3/3 PASS evidence** (본 first-use precedent 가 충족):
1. `pr_cumulative_min: 20` ≤ 200 (10x threshold, gh pr list verified)
2. `failure_threshold: 0` = `recurrence.count: 0` (warning mode 8일간 발화 0건)
3. `sibling_dependencies: [CFP-390, CFP-412, CFP-455]` = ALL MERGED (CFP-412 substitution via ADR-060 Amendment 1+2 chain)

본 first-use precedent 가 향후 21+ warning-tier entry 의 blocking-on-pr 승격 path 의 template — `current_tier` + `status` + `recurrence.last_occurrence` + `recurrence.promotion_trigger` 4 field 동시 transition + optional `promoted_by` + `promoted_date` 부착 pattern.

**MINOR bump 미동반** (schema 변경 0 — value transition only) — kind:registry sibling sync 면제 (ADR-010 §결정 2). `docs/inter-plugin-contracts/MANIFEST.yaml` `evidence-check-registry-v1` row version retain (v1.3, CFP-963 baseline).

### 예상 변경 (forward-looking)

- **v1.x (CFP-D 잠정)**: `modal_anti_pattern_dictionary.version` 확장 어휘 도입 (예: `"1.1"` — "충분히" / "조만간" / "soon" / "TBD" 추가). MINOR bump.
- **v2.0 (가설)**: per-entry `bypass_label` 단일 global 전환 등 BREAKING.

## 8. Versioning + Write boundary

- **Versioning SSOT**: ADR-008 (kind:registry SemVer 룰).
- **Sibling sync**: kind:registry 는 wrapper-owned cross-cutting protocol — canonical/sibling 패턴 외 (ADR-010 scope: kind:contract only).
- **Write boundary**: wrapper Orchestrator + 본 registry 의 entry 도입 carrier Story 의 author agent (ArchitectAgent). registry yaml row append = framework SSOT (본 doc) 의 직접 author. lane plugin 직접 entry 추가 금지 (wrapper governance).

## 9. 관련 파일

- `docs/evidence-checks-registry.yaml` — registry data SSOT (첫 entry = adr-sunset-criteria)
- `docs/inter-plugin-contracts/MANIFEST.yaml` — `registries:` 블록 entry 추가 (versioning 추적)
- `docs/doc-locations.yaml` — 신규 doc type `evidence_check_registry` row (ADR-041)
- `docs/parallel-work/section-ownership.yaml` — `evidence-checks-registry.yaml` append-only entry (ADR-050)
- `docs/adr/ADR-060-evidence-enforceable-promotion-framework.md` — framework carrier ADR
- `docs/adr/ADR-058-adr-sunset-criteria-mandate.md` — 직접 동인 / 첫 entry 의 검증 대상 정책
- `docs/adr/ADR-024-story-scoped-branch-policy.md` Amendment 3 — audit-trailed exception channel 정식 도입
- `scripts/check-adr-sunset-criteria.sh` — 첫 entry lint 구체
- `scripts/check-bypass-audit-comment.sh` — audit assertion lint
- `templates/github-workflows/adr-sunset-criteria.yml` — warning mode workflow
- 후속 carrier: CFP-390 (인벤토리 backfill) / CFP-391 (4-tier 정식 amendment) / CFP-C 잠정 (ADR-057 amendment + KPI dashboard) / CFP-D 잠정 (retroactive backfill)
