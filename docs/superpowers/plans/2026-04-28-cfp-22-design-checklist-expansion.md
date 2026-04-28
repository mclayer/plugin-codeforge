# CFP-22 DesignReview Checklist Expansion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Codex audit #4·#5·#6 (관측성 / API 호환 / SLO) 직접 closure. design.md SSOT + DesignReviewPL severity_overrides + CodexReview prompt 동기 갱신. Non-BREAKING v0.14.1.

**Architecture:** 새 deputy 없음, 새 §섹션 없음. 기존 design.md "§7 보안 설계 감사" 패턴 동형으로 3 audit 절 추가 (API 호환 / 관측성 / SLO). category enum 3 + severity_overrides P0 3 + P1 3 추가. 4 파일 단일 PR.

**Tech Stack:** Markdown SSOT · YAML frontmatter · invariant-check Step 6/8 parity · ripgrep verify.

---

## Task 1: design.md 3 audit 섹션 + category enum + severity 자동 룰

**Files:**
- Modify: `templates/review-checklists/design.md`

- [ ] **Step 1: Category enum 확장 (§Category enum 절)**

old_string anchor:
```
`adr-mismatch | design-completeness | mapper-refactor-balance | implementability | test-contract | section-missing | security-design | data-migration`
```

new_string:
```
`adr-mismatch | design-completeness | mapper-refactor-balance | implementability | test-contract | section-missing | security-design | data-migration | api-compatibility | observability | slo-missing`
```

- [ ] **Step 2: Severity 자동 룰 절 갱신**

기존 §11 P0 3건 다음에 P0 3건 + P1 3건 추가 (조건부 P0).

`.../design.md` `## Severity 자동 룰` 절 끝(§11 룰 마지막 행 다음)에 추가:
```
- **API breaking change에 versioning 전략 부재** → P0 강제 (`api-compatibility`) — 공개 API·SLA 대상만, 내부 도구는 P1
- **외부 입력 컴포넌트에 관측성 결정 부재** → P0 강제 (`observability`) — boundary 컴포넌트만, 내부 함수는 P1
- **공개 API · SLA 대상 서비스에 SLO 부재** → P0 강제 (`slo-missing`) — 내부 도구는 P1
- **API 변경 시 deprecation timeline 미정의** → P1 (`api-compatibility`)
- **신규 컴포넌트 metric 종류 미명시** → P1 (`observability`)
- **SLO 목표 측정 방법 부재** → P1 (`slo-missing`)
```

- [ ] **Step 3: §"§11 데이터 마이그레이션 감사" 다음에 3 신규 audit 섹션 추가** (§"## 다음 게이트 (PASS 시)" 직전)

내용:
```
## §4 API 호환 감사 (Codex audit #5, [CFP-22 spec](../../docs/superpowers/specs/2026-04-28-cfp-22-design-checklist-expansion.md))

### API 변경 식별
- [ ] API 변경(route / schema / response code / status code) 영향이 §4 API 계약 또는 §5 변경 계획에 명시되었는가
- [ ] Breaking 여부 분류 (additive / breaking / internal-only)가 명시되었는가

### Backward / Forward compatibility
- [ ] Breaking change 시 versioning 전략이 결정되었는가 (URL prefix / Accept header / OpenAPI version / GraphQL schema)
- [ ] Deprecation timeline이 정의되었는가 (sunset notice / parallel run / migration window)
- [ ] Consumer 영향 분석 (alpha/beta consumer 식별 + 통보 채널)이 명시되었는가

### Severity 자동 룰
- API breaking change에 versioning 전략 부재 → **P0** (공개 API·SLA 대상만)
- API 변경 시 deprecation timeline 미정의 → **P1**
- API 변경 없는 Story → N/A 명시 + 사유 1줄

## §3·§4 관측성 감사 (Codex audit #4, [CFP-22 spec](../../docs/superpowers/specs/2026-04-28-cfp-22-design-checklist-expansion.md))

### 관측성 결정
- [ ] 신규/변경 컴포넌트의 log level + 구조화 형식 (JSON / plain) 결정이 명시되었는가
- [ ] 신규 컴포넌트의 metric 종류 (counter / gauge / histogram + 라벨 차원)가 명시되었는가
- [ ] 신규 외부 호출의 trace span 결정이 명시되었는가

### 핵심 이벤트 emit
- [ ] 핵심 비즈니스 이벤트 emit 지점이 명시되었는가 (예: 결제 완료 / 인증 실패 / 외부 호출 실패)
- [ ] error response의 trace ID·correlation ID 전파 정책이 명시되었는가

### 민감 데이터 redact
- [ ] log·metric·trace의 민감 데이터 redact 정책이 명시되었는가 (SecurityArch §7.4와 cross-ref)
- [ ] PII / 금융 / 헬스 데이터가 외부 시스템(log aggregator / APM)에 전송되지 않음을 검증했는가

### Severity 자동 룰
- 외부 입력 컴포넌트에 관측성 결정 부재 → **P0** (boundary 컴포넌트만)
- 신규 컴포넌트 metric 종류 미명시 → **P1**
- 민감 데이터 redact 정책 부재 → **P1** (SecurityArch §7.4와 동시 P1)
- 내부 함수·docs-only Story → N/A 명시 + 사유 1줄

## §3 SLO 감사 (Codex audit #6, [CFP-22 spec](../../docs/superpowers/specs/2026-04-28-cfp-22-design-checklist-expansion.md))

### SLO 목표 정의
- [ ] 가용성 목표 (예: 99.9%)가 정의되었는가
- [ ] 지연 목표 (p50·p95·p99 latency)가 정의되었는가
- [ ] Throughput 목표 (rps / 동시 connection)가 정의되었는가

### 측정·검증 방법
- [ ] SLO 측정 방법이 명시되었는가 (synthetic monitoring / 실 트래픽 sampling / SLO calculator)
- [ ] Error budget 정책이 정의되었는가 (소진 시 release 정지 / 우선순위 조정)

### §8.3 성능 baseline와의 관계
- [ ] §8.3 성능 baseline (mean 10% 회귀 차단)와 SLO가 별개임을 인지하고 둘 다 정의되었는가 (baseline = 회귀 감지, SLO = 운영 목표)

### Severity 자동 룰
- 공개 API · SLA 대상 서비스에 SLO 부재 → **P0**
- SLO 목표 측정 방법 부재 → **P1**
- 내부 도구·plugin meta Story → N/A 명시 + 사유 1줄
```

- [ ] **Step 4: Verify**

```bash
grep -c "api-compatibility\|observability\|slo-missing" templates/review-checklists/design.md
# Expected: ≥6 (3 categories in enum + 3 P0 rules in severity overrides + 3 P1 rules)
grep -c "^## " templates/review-checklists/design.md
# Expected: previous + 3 (3 new audit 섹션)
```

- [ ] **Step 5: Commit**

```
feat(cfp-22): design.md — 3 audit 섹션 (API 호환·관측성·SLO) + category enum + severity 자동 룰 (1/4)
```

---

## Task 2: DesignReviewPL severity_overrides + CodexReview prompt

**Files:**
- Modify: `agents/DesignReviewPLAgent.md`
- Modify: `agents/CodexReviewAgent.md`

- [ ] **Step 1: DesignReviewPLAgent.md** — category_enum + severity_overrides 갱신

old_string anchor:
```
  category_enum:
    - adr-mismatch
    - design-completeness
    - mapper-refactor-balance
    - implementability
    - test-contract
    - section-missing
    - security-design
    - data-migration
  severity_overrides:
    - "ADR violation → P0"
    - "§8 Test Contract 누락 → P0"
    - "§3-6 섹션 누락 → P0"
    - "§7 보안 설계 누락 → P0"
    - "§7.6 N/A 사유 부재 → P0"
    - "Architect 통합 판정에서 SecurityArch 위협-완화 매핑 미반영 → P0"
    - "§11 데이터 마이그레이션 누락 → P0"
    - "§11.6 N/A 사유 부재 → P0"
    - "Architect 통합 판정에서 DataMigrationArch 마이그레이션 안전성 매핑 미반영 → P0"
```

new_string:
```
  category_enum:
    - adr-mismatch
    - design-completeness
    - mapper-refactor-balance
    - implementability
    - test-contract
    - section-missing
    - security-design
    - data-migration
    - api-compatibility
    - observability
    - slo-missing
  severity_overrides:
    - "ADR violation → P0"
    - "§8 Test Contract 누락 → P0"
    - "§3-6 섹션 누락 → P0"
    - "§7 보안 설계 누락 → P0"
    - "§7.6 N/A 사유 부재 → P0"
    - "Architect 통합 판정에서 SecurityArch 위협-완화 매핑 미반영 → P0"
    - "§11 데이터 마이그레이션 누락 → P0"
    - "§11.6 N/A 사유 부재 → P0"
    - "Architect 통합 판정에서 DataMigrationArch 마이그레이션 안전성 매핑 미반영 → P0"
    - "API breaking change에 versioning 전략 부재 → P0 (공개 API·SLA 대상만)"
    - "외부 입력 컴포넌트에 관측성 결정 부재 → P0 (boundary 컴포넌트만)"
    - "공개 API · SLA 대상 서비스에 SLO 부재 → P0"
```

- [ ] **Step 2: CodexReviewAgent.md** — lane=design prompt 갱신

old_string anchor:
```
Report each finding with severity [P0]/[P1]/[P2]/[P3], category from {adr-mismatch,
design-completeness, mapper-refactor-balance, implementability, test-contract,
section-missing, security-design, data-migration}, location as path:section, ADR reference where applicable.
Auto-P0: ADR violation, §8 missing, §3-6 sections missing, §7 보안 설계 누락 또는 §7.6 N/A 사유 부재, §11 데이터 마이그레이션 누락 또는 §11.6 N/A 사유 부재.
```

new_string:
```
Report each finding with severity [P0]/[P1]/[P2]/[P3], category from {adr-mismatch,
design-completeness, mapper-refactor-balance, implementability, test-contract,
section-missing, security-design, data-migration, api-compatibility, observability, slo-missing}, location as path:section, ADR reference where applicable.
Auto-P0: ADR violation, §8 missing, §3-6 sections missing, §7 보안 설계 누락 또는 §7.6 N/A 사유 부재, §11 데이터 마이그레이션 누락 또는 §11.6 N/A 사유 부재, API breaking without versioning (public/SLA-bound), boundary-component without observability decisions, public/SLA-bound service without SLO.
```

- [ ] **Step 3: Verify**

```bash
grep -c "api-compatibility\|observability\|slo-missing" agents/DesignReviewPLAgent.md agents/CodexReviewAgent.md
# Expected: ≥6 (3 categories × 2 files)
```

- [ ] **Step 4: Commit**

```
feat(cfp-22): DesignReviewPL severity_overrides + CodexReview lane=design prompt — 3 audit P0 (2/4)
```

---

## Task 3: CHANGELOG v0.14.1 + plugin.json bump

**Files:**
- Modify: `CHANGELOG.md`
- Modify: `.claude-plugin/plugin.json`

- [ ] **Step 1: plugin.json** — `0.14.0` → `0.14.1`

- [ ] **Step 2: CHANGELOG.md** — `## [0.14.0]` 위에 새 entry:

```
## [0.14.1] - 2026-04-28

### CFP-22 — DesignReview checklist 확장 (Codex audit #4·#5·#6)

**Non-BREAKING**. ADR-004 §"후속 조치" #4·#5·#6 직접 적용. 새 deputy 없음, 새 §섹션 없음 — 기존 design.md에 3 audit 섹션만 추가.

### Added
- design.md: §4 API 호환 감사 (Codex #5)
- design.md: §3·§4 관측성 감사 (Codex #4)
- design.md: §3 SLO 감사 (Codex #6)
- lane=design category enum: api-compatibility / observability / slo-missing (3개 추가, 8 → 11)
- DesignReviewPL severity_overrides: P0 3건 추가
- CodexReviewAgent lane=design prompt: auto-P0 3건 추가

### Why
Codex audit #4 (관측성) / #5 (API 호환) / #6 (SLO) 모두 설계 시점 누락 위험 — 운영 단계에서 발견 시 비싼 회귀. shift-left 정합성 (ADR-004 / ADR-006 / ADR-007 동일 trade-off, 단 새 deputy 불필요).

### Migration
Non-BREAKING — 기존 Story 진행 중인 경우 새 audit 룰은 다음 DesignReview 진입 시 자동 적용. P0 룰은 조건부 (공개 API·SLA·boundary 컴포넌트만) — 내부 도구·docs-only는 P1 또는 N/A 사유 1줄로 처리.

자세한 사항: [docs/superpowers/specs/2026-04-28-cfp-22-design-checklist-expansion.md](docs/superpowers/specs/2026-04-28-cfp-22-design-checklist-expansion.md)
```

- [ ] **Step 3: Commit**

```
feat(cfp-22): v0.14.1 — CHANGELOG + plugin.json bump (3/4)
```

---

## Task 4: invariant verify + Story doc + PR + admin merge

**Files:**
- Create: `docs/stories/CFP-22.md`
- Verify: invariant-check 8 step PASS

- [ ] **Step 1: Story doc 작성** — CFP-19/CFP-20/CFP-21 패턴 (plugin-meta-na). §1 사용자 verbatim, §2-7 spec 인용, §8/§9 N/A.

- [ ] **Step 2: invariant verify locally**

```bash
# Step 2: version match
jq -r '.version' .claude-plugin/plugin.json   # Expected: 0.14.1
grep -oE '^## \[[0-9]+\.[0-9]+\.[0-9]+\]' CHANGELOG.md | head -1  # Expected: [0.14.1]

# Step 6: 3 new categories parity (4 곳 — design.md SSOT + DesignReviewPL + CodexReview prompt + count)
for cat in api-compatibility observability slo-missing; do
  echo "=== $cat ==="
  grep -l "$cat" templates/review-checklists/design.md agents/DesignReviewPLAgent.md agents/CodexReviewAgent.md
done

# Step 8: severity overrides P0 count (design.md ↔ DesignReviewPL parity)
grep -c "→ \*\*P0\*\*\|→ P0 강제\|→ P0\b" templates/review-checklists/design.md
grep -c '"\(.*\)→ P0' agents/DesignReviewPLAgent.md
```

- [ ] **Step 3: Push + PR + admin merge**

- [ ] **Step 4: Final commit**

```
docs(cfp-22): Story doc + invariant verify (4/4)
```

---

## Self-Review

### 1. Spec coverage

- §4 API 호환 audit (Codex #5) → Task 1 ✓
- §3·§4 관측성 audit (Codex #4) → Task 1 ✓
- §3 SLO audit (Codex #6) → Task 1 ✓
- Category enum 3개 추가 → Task 1 + Task 2 ✓
- Severity 자동 룰 P0 3 + P1 3 → Task 1 + Task 2 ✓
- v0.14.1 release → Task 3 ✓
- invariant verify → Task 4 ✓

### 2. Placeholder scan

없음 — 모든 anchor 정확.

### 3. 일관성

- enum: `api-compatibility` / `observability` / `slo-missing` (4 곳 동일)
- 버전: 0.14.0 → 0.14.1
- 카테고리 수: 8 → 11

### 4. Non-BREAKING

ADR 변경 없음. 기존 Story 영향 — 다음 DesignReview 진입 시 자동 적용. P0 조건부 (공개 API·SLA·boundary만). consumer 액션 없음.
