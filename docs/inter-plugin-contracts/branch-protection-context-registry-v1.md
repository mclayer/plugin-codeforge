---
kind: registry
registry: branch-protection-context-registry
version: "1.2"
status: Archived
superseded_by: wrapper CLAUDE.md 브랜치 보호 표 (wrapper 1행) + docs/security/branch-protection-audit.md  # CFP-2178 S6 — lane repo 8개 archive 로 cross-repo parity 대상 소멸
canonical_repo: mclayer/plugin-codeforge
canonical_path: docs/inter-plugin-contracts/branch-protection-context-registry-v1.md
date: 2026-05-30
authors:
  - ArchitectAgent (CFP-1806 carrier — 8 codeforge plugin family main branch protection contexts SSOT structured codify)
version_history:
  - { version: "1.0", date: 2026-05-30, carrier: CFP-1806, change: "initial — 8 codeforge plugin family (wrapper + 7 lane plugin) main branch required_status_checks.contexts[] structured SSOT codify. Previously markdown table only in wrapper CLAUDE.md '6 lane plugin branch protection contexts SSOT' 단락 (CFP-1785-S1 PATCH 후 상태). Parent retro: CFP-1785 retro FU-B P3 (structured cross-repo parity verify의 input anchor SSOT 분리)." }
  - { version: "1.1", date: 2026-05-31, carrier: CFP-1850-S2, change: "MINOR — codeforge-pmo / codeforge-deploy / codeforge-deploy-review 3 entry contexts[] 채움 (contexts: [] + protected: false → [check-gate, phase-gate-mergeable]). pmo = phase-gate-mergeable 필수 신규 추가 (gh API PATCH 적용). deploy/deploy-review = 실제 PROTECTED 상태 반영 (이전 protected:false = drift). 8 lane plugin 모두 phase-gate-mergeable 필수 포함 통일 (review 는 invariant 유지 — live check). 단일 chore PR 영구 차단은 CFP-1850-S1 isChoreOnly fast-pass 로 해소되어 requirements/pmo 필수 추가 안전. wrapper 6번째 context 표기 drift 정정 동반 (deploy-lane-presence 축약 → actual job 표시명 'Verify deploy lane presence (Phase 2 wire — ADR-087 Amd 2)', CFP-1807 parity lint clean)." }
  - { version: "1.2", date: 2026-06-12, carrier: CFP-2178, change: "MINOR — status Active → Archived. lane repo 8개 GitHub archive (Epic #2151 S6, ADR-118 D1) 로 9-repo cross-repo parity 검증 대상 소멸. 잔존 SSOT = wrapper CLAUDE.md 브랜치 보호 표 (wrapper 1행) + docs/security/branch-protection-audit.md. related_files 의 부재 script 인용 (scripts/lib/check_branch_protection_context_name_strict_match.py — S3 에서 파일 소멸) 제거. file 잔존 + historical record 보존 (ADR-008 §5.1). MINOR 등급 근거 = status 전환 + version_history append — 필드 제거/의미 파괴 0 비파괴 변경 (ADR-008 §2 v1.x backward-compatible)." }
owner_adr: ADR-024
carrier_story: CFP-1806
sibling_sync_exempt: true
related_adrs:
  - ADR-008  # Inter-plugin contract versioning (kind:registry MINOR/PATCH sibling sync 면제)
  - ADR-010  # Inter-plugin Contract Sibling Sync (kind:registry exempt — §결정 2)
  - ADR-024  # Story-scoped branch policy (branch protection governance SSOT)
  - ADR-058  # ADR sunset criteria mandate (is_transitional: false ratchet 강화 방향)
  - ADR-060  # Evidence-enforceable promotion framework (cross-repo parity lint tier framework)
  - ADR-064  # Decision principle mandate (CFP scope unitary)
  - ADR-087  # Deploy lane lifecycle (codeforge-deploy plugin contexts schema host)
  - ADR-088  # Deploy Review lane (codeforge-deploy-review plugin contexts schema host)
  - ADR-113  # Admin merge pre-flight gate (contexts strict match cross-ref)
related_files:
  - CLAUDE.md  # "6 lane plugin branch protection contexts SSOT" 단락 (prose narrative cross-ref)
  - docs/inter-plugin-contracts/MANIFEST.yaml  # registries[] entry
  - docs/inter-plugin-contracts/label-registry-v2.md  # severity:/hotfix-bypass:* family cross-ref
  - docs/adr/ADR-024-story-scoped-branch-policy.md
  - docs/security/branch-protection-audit.md  # audit log SSOT (post-PATCH state record)
related_plugins:
  - codeforge (wrapper, SSOT host repo)
  - codeforge-requirements (lane plugin, registry entry)
  - codeforge-design (lane plugin, registry entry)
  - codeforge-review (lane plugin, registry entry, `invariant` outlier 보존)
  - codeforge-develop (lane plugin, registry entry)
  - codeforge-test (lane plugin, registry entry)
  - codeforge-pmo (lane plugin, registry entry — CFP-1850-S2 phase-gate-mergeable 필수 추가)
  - codeforge-deploy (lane plugin, registry entry — CFP-1850-S2 PROTECTED 정정)
  - codeforge-deploy-review (lane plugin, registry entry — CFP-1850-S2 PROTECTED 정정)
---

# branch-protection-context-registry-v1 — Inter-plugin Contract Registry

> **Archived (v1.2, CFP-2178 S6, 2026-06-12)** — lane repo 8개 GitHub archive (ADR-118 D1) 로 cross-repo parity 검증 대상 소멸. 잔존 SSOT = wrapper `CLAUDE.md` 브랜치 보호 표 (wrapper 1행) + [`docs/security/branch-protection-audit.md`](../security/branch-protection-audit.md). 본 file 은 historical record 로 보존 (ADR-008 §5.1). 이하 본문 = archive 시점 상태 동결.
>
> **CFP-2782 (ADR-121 Wave 2, 2026-07-22) supersession 주석 (frozen body 무수정)** — 배포 2 lane(구 ADR-087 / ADR-088 host plugin) + wrapper `Verify deploy lane presence (Phase 2 wire — ADR-087 Amd 2)` context 는 ADR-121 / CFP-2782 로 물리 제거됐다. 현행 wrapper required contexts = 본 frozen snapshot 의 6-tuple(위 context 포함)이 아니라 **9→8-tuple 전환 후 상태** (deploy 관련 context 1개 제거, SSOT = wrapper CLAUDE.md 브랜치 보호 표 + `docs/security/branch-protection-audit.md` 2026-07-22 entry). 이하 §3·§5 의 위 context 및 배포 2 plugin repo entry = 2026-06-12 archive 시점 동결 이력이므로 **무수정 보존** (ADR-008 §5.1 historical record — frozen snapshot 재작성 = 이력 위조 회피).

8 codeforge plugin family (wrapper + 7 lane plugin) 의 GitHub `main` branch protection `required_status_checks.contexts[]` array SSOT. cross-repo parity verify lint (`branch-protection-context-parity` — CFP-1807) + context name strict-match lint (`branch-protection-context-name-strict-match` — CFP-1849) 의 **input anchor SSOT** 로 작동.

**kind**: registry (sibling sync 면제, ADR-008 §결정 2 + ADR-010 §결정 2 정합)

## 1. 목적

### 1.1 SSOT 분리 동기

이전까지 8 plugin family contexts SSOT 는 wrapper `CLAUDE.md` "6 lane plugin branch protection contexts SSOT" 단락 안 markdown 표 형태로만 존재. consumer lint (CFP-1807 cross-repo parity, CFP-1849 context name strict match) 는 markdown 표 parser (anchored regex per ADR-061 Amd 3 §결정 11) 로 해당 단락을 line-by-line scan 해 작동.

본 carrier (CFP-1806) 가 structured yaml schema 로 SSOT 분리. wrapper CLAUDE.md prose narrative 단락은 human-readable mirror 로 보존 (서술 + 비고 영역, 자동화 parser 의 fallback SSOT). lint consumer 는 향후 본 contract 의 §3 yaml block 우선 read 가능 (Phase 2 mechanical lint 갱신 = 별 sub-CFP carrier — declaration-only Wave 1).

### 1.2 Parent retro

- **CFP-1785 retro FU-B P3** — branch protection contexts cross-repo SSOT structured codify priority. P3 = "후속 carrier 분리 — 본 PR scope 외 declarative SSOT 분리".
- `codeforge-internal-docs/plugin-codeforge/retros/2026-05-28-cfp-1785.md` FU-B P3 row evidence carrier.

### 1.3 sub-domain 분리 axis (3-way disjoint)

`branch-protection-*` 영역 3 sub-domain 분리 유지 (cross-cutting 영역 0건):

| # | sub-domain | scope | SSOT host |
|---|---|---|---|
| 1 | `branch-protection-drift` (ADR-024 Amd 2 / CFP-821 D2) | single-repo expected vs actual (manifest-driven) | `scripts/check-branch-protection-drift.sh` + `templates/scripts/setup-branch-protection.sh` |
| 2 | `branch-protection-sync` (CFP-821 D2 §결정 A) | manifest-driven dry-run helper | `templates/scripts/setup-branch-protection.sh` |
| 3 | `branch-protection-context-parity` (CFP-1807) + `branch-protection-context-name-strict-match` (CFP-1849) | cross-repo 8 plugin family iteration + SSOT 표 vs actual gh api response 집합 의미 비교 + workflow job 표시명 strict match | **본 registry** (CFP-1806) + wrapper CLAUDE.md prose mirror |

## 2. Schema

본 contract 의 yaml schema = §3 에서 정의. summary:
- top-level `plugins[]` array (closed-enum 8 codeforge plugin family)
- 각 plugin entry = `{ repo: string, contexts: string[] }`
- `repo` = GitHub `owner/repo` slug
- `contexts` = `required_status_checks.contexts[]` verbatim (workflow job 표시명 strict match)

## 3. 항목

본 registry 의 entry = §4 Family scope 안 closed-enum 8 plugin family. 각 entry 는 §5 Context schema yaml block 안 구체 contexts[] 보유.

## 4. 변경 규칙

- MINOR bump (v1.X → v1.X+1) = entry append (새 plugin family 추가) 또는 contexts[] array 확장
- MAJOR bump (v1.X → v2.0) = breaking schema change (top-level shape 변경)
- sibling sync 면제 (kind:registry per ADR-010 §결정 2)
- ADR-008 versioning policy 정합

## 5. Family scope (closed-enum 8 plugins)

본 registry 는 8 codeforge family plugin closed-enum 만 carrier. 다른 marketplace plugin (codex / superpowers / github / pyright-lsp / context7 / commit-commands / pr-review-toolkit) = scope 외.

```yaml
family:
  - mclayer/plugin-codeforge          # wrapper, 6-tuple contexts (post CFP-1808 deploy-lane-presence wire 활성)
  - mclayer/plugin-codeforge-requirements  # lane plugin (codeforge-requirements) — 이하 lane repo 8개 = 구 repo 삭제됨 2026-06-12, 현 plugins/<lane>/ 모노레포 (본 registry = Archived historical record)
  - mclayer/plugin-codeforge-design   # lane plugin (codeforge-design)
  - mclayer/plugin-codeforge-review   # lane plugin (codeforge-review), invariant outlier 보존
  - mclayer/plugin-codeforge-develop  # lane plugin (codeforge-develop)
  - mclayer/plugin-codeforge-test     # lane plugin (codeforge-test)
  - mclayer/plugin-codeforge-pmo      # lane plugin (codeforge-pmo) — CFP-1850-S2 phase-gate-mergeable 필수 추가
  - mclayer/plugin-codeforge-deploy   # lane plugin (codeforge-deploy) — CFP-1850-S2 PROTECTED 정정
  - mclayer/plugin-codeforge-deploy-review  # lane plugin (codeforge-deploy-review) — CFP-1850-S2 PROTECTED 정정
```

NOTE: 9 entry 명단이지만 codeforge family 통상 호칭 = "8 plugin family" (wrapper 1 + 7 lane). 본 registry 안 frontmatter / 본문 9 entry 명시는 codeforge-internal-docs lane plugin (별 lifecycle) 제외 + 본 `family` block 의 9 entry 는 GitHub repo level 명단 (wrapper repo 1 + lane plugin repo 8). audit log + lint scope 와 1:1 매칭.

## 3. Context schema (SSOT yaml)

`required_status_checks.contexts[]` array 의 plugin 별 closed-set 정의. context name = GitHub branch protection API `protection.required_status_checks.contexts[]` array element string verbatim (workflow job 표시명 / `jobs.<id>.name` OR `jobs.<id>` job_id fallback per CFP-1849 strict-match lint).

```yaml
plugins:
  - repo: mclayer/plugin-codeforge
    role: wrapper
    contexts:
      - "phase-gate-mergeable"
      - "invariant-check"
      - "doc frontmatter schema (CFP-28 — strict)"
      - "doc section schema (CFP-28 — strict)"
      - "check-gate"
      - "Verify deploy lane presence (Phase 2 wire — ADR-087 Amd 2)"
    note: "6-tuple (CFP-1808 Amendment 2 — deploy-lane-presence wire 활성). 6번째 context = `deploy-lane-presence.yml` 의 workflow job 표시명 (`jobs.*.name`) verbatim — CFP-1850-S2 drift 정정 (이전 `deploy-lane-presence` 축약 표기 = actual context명 mismatch). `check-gate` = `phase-gate-mergeable.yml` workflow job ID (CFP-1785-S1 PATCH)."

  - repo: mclayer/plugin-codeforge-requirements
    role: lane
    contexts:
      - "phase-gate-mergeable"
      - "check-gate"
    note: "2-tuple. CFP-1785-S1 PATCH 후 상태."

  - repo: mclayer/plugin-codeforge-design
    role: lane
    contexts:
      - "phase-gate-mergeable"
      - "check-gate"
    note: "2-tuple."

  - repo: mclayer/plugin-codeforge-review
    role: lane
    contexts:
      - "invariant"
      - "phase-gate-mergeable"
      - "check-gate"
    note: "3-tuple — `invariant` outlier 보존 (Story-2 cleanup scope, 구형 context 제거 별 sub-CFP carrier)."

  - repo: mclayer/plugin-codeforge-develop
    role: lane
    contexts:
      - "phase-gate-mergeable"
      - "check-gate"
    note: "2-tuple."

  - repo: mclayer/plugin-codeforge-test
    role: lane
    contexts:
      - "phase-gate-mergeable"
      - "check-gate"
    note: "2-tuple."

  - repo: mclayer/plugin-codeforge-pmo
    role: lane
    contexts:
      - "check-gate"
      - "phase-gate-mergeable"
    note: "2-tuple. CFP-1850-S2 — `phase-gate-mergeable` 필수 추가 (이전 `check-gate`만, 단일 chore PR 은 isChoreOnly fast-pass 로 통과)."

  - repo: mclayer/plugin-codeforge-deploy
    role: lane
    contexts:
      - "check-gate"
      - "phase-gate-mergeable"
    note: "2-tuple. CFP-1850-S2 — PROTECTED 정정 (이전 표기 protected:false = drift, 실제 보호됨). CFP-1059 / ADR-087 신설 plugin."

  - repo: mclayer/plugin-codeforge-deploy-review
    role: lane
    contexts:
      - "check-gate"
      - "phase-gate-mergeable"
    note: "2-tuple. CFP-1850-S2 — PROTECTED 정정 (이전 표기 protected:false = drift, 실제 보호됨). CFP-1059 / ADR-088 신설 plugin."
```

### 3.1 Schema invariants

- **closed-set 8 plugin scope** — 본 registry 안 9 row 외 plugin entry 추가 = MAJOR bump 의무 (family scope 확장 = breaking schema change).
- **contexts[] array element string verbatim** — GitHub branch protection API response `required_status_checks.contexts[]` array element 와 byte-identical match (whitespace / em-dash / 괄호 포함). CFP-1849 context name strict-match lint 의 input anchor.
- **`protected: false` + `contexts: []` 동시 표기** — NOT PROTECTED plugin 은 두 field 동시 표기 의무 (silent omission 차단). CFP-1850-S2 후 현재 8 plugin family 모두 PROTECTED (NOT PROTECTED instance 0건) — convention 은 미래 신설 plugin 용으로 보존.
- **`role` enum closed-set 2-value** — `wrapper` (1 plugin) / `lane` (7 lane plugin). 다른 role 신설 = MAJOR bump 의무.
- **`note` field optional, prose 자유 형식** — human-readable annotation. lint consumer 는 contexts[] / protected / role 3 field 만 mechanical read.

## 4. Versioning

ADR-008 정합. kind:registry — sibling sync 면제 (ADR-010 §결정 2).

| bump type | trigger | example |
|---|---|---|
| MAJOR | family scope 확장 (9 → 10 plugin) / role enum 추가 / contexts[] schema 자체 변경 (string array → object array 등) | family scope 외 plugin 추가 |
| MINOR | plugin entry 안 contexts[] 추가/제거 / 신규 closed-set 옵션 field 추가 / `protected: true → false` 전환 | wrapper contexts 7-tuple 확장 (현재 6-tuple) / codeforge-pmo PROTECTED 전환 |
| PATCH | note 영역 갱신 / typo 정정 / cross-ref ADR 번호 정정 / metadata 갱신 | `note: "..."` 본문 prose 수정 |

bump 시 본 registry frontmatter `version` 갱신 + MANIFEST.yaml `registries[]` `branch-protection-context-registry` entry 안 `version` 갱신 atomic 의무 (wrapper repo 내 atomic, sibling sync 면제).

## 5. Cross-reference

### 5.1 Consumer lint (input anchor)

| consumer | scope | input read 영역 |
|---|---|---|
| `branch-protection-context-parity` (CFP-1807) | cross-repo 9 plugin family iteration + SSOT 표 vs actual gh api response 집합 의미 비교 | 본 registry §3 yaml block (Phase 2 mechanical 갱신 = 별 sub-CFP carrier — 현 CFP-1807 lint 는 wrapper CLAUDE.md prose 표 line-by-line parse, Phase 2 에 본 contract yaml block 우선 read 전환 예정) |
| `branch-protection-context-name-strict-match` (CFP-1849) | main branch protection required check context name vs actual workflow job 표시명 strict match | 본 registry §3 yaml block contexts[] array element (PyYAML safe_load primary + line-by-line fallback per ADR-061 Amd 3 §결정 11) |

### 5.2 Related SSOT

- **wrapper CLAUDE.md "6 lane plugin branch protection contexts SSOT" 단락** — human-readable mirror SSOT. 본 contract §3 yaml block 과 byte-identical semantic 동기 의무 (wrapper-internal cross-ref, drift 시 본 contract = canonical SSOT).
- **`docs/security/branch-protection-audit.md`** — audit log SSOT (PATCH / Story-2 cleanup 기록). 본 registry 갱신 시 audit log 도 동반 append 의무 (ADR-024 §결정 6 cross-ref).
- **`docs/inter-plugin-contracts/label-registry-v2.md`** — `hotfix-bypass:branch-protection-context-parity` (110번째 family member, CFP-1807) + `hotfix-bypass:branch-protection-context-name-strict-match` (113번째 family member, CFP-1849) bypass label cross-ref.

### 5.3 ADR cross-ref

- **ADR-024 §결정 6.A** — per-entry namespace `hotfix-bypass:*` family member append SSOT (consumer lint bypass channel).
- **ADR-060 §결정 5** — warning-tier first introduction (CFP-1807 / CFP-1849 둘 다 warning tier).
- **ADR-087 Amendment 2 §B** — wrapper 6번째 context `deploy-lane-presence` Phase 2 wire 활성 carrier (CFP-1808). 본 registry §3 wrapper plugin row 의 6번째 entry `deploy-lane-presence` 정합.
- **ADR-088** — codeforge-deploy-review plugin contexts schema host (현재 NOT PROTECTED, Story-2 carrier 영역).
- **ADR-113** — admin merge pre-flight gate (contexts strict match cross-ref).
- **ADR-058 §결정 5** — `is_transitional: false` permanent governance (contexts SSOT 의 perpetual 성격).
- **ADR-064 §결정 5** — CFP scope unitary (본 carrier scope = 3 file 신설 + 1 MANIFEST.yaml entry append + 1 CLAUDE.md cross-ref 1 line + 2 internal-docs file 신설).

## 6. Out-of-scope (boundary 보존)

- **GitHub branch protection API actual state write** — 본 registry = SSOT declarative only. actual `gh api ... -X PUT` 호출은 `scripts/check-branch-protection-drift.sh` + `templates/scripts/setup-branch-protection.sh` SSOT (사용자 admin 권한 수동 영역).
- **codeforge-internal-docs lane plugin** — 별 lifecycle (wrapper 와 분리된 dogfood-out repo), 본 family scope 외.
- **non-codeforge marketplace plugin** — codex / superpowers / github 등 별 marketplace plugin = scope 외.
- **workflow self-application invariant verify** — `templates/github-workflows/*.yml` ↔ `.github/workflows/*.yml` byte-identical 검증은 ADR-005 SSOT (별 carrier).
- **PR-time `actual ≠ SSOT` drift remediation procedure** — `branch-protection-context-parity` lint (CFP-1807) 가 advisory emit, 실 remediation 은 admin 권한 수동 영역.
