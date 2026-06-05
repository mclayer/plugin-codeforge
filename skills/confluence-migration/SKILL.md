---
name: codeforge:confluence-migration
description: codeforge family 의 Confluence doc-mirror governance 진입점. wrapper-self (CFP space) + consumer (per-instance) 양 적용. 5 ADR + IA tree + agent + workflow + script 분산 자료 단일 진입점. 호출 시점 = consumer 측 Confluence migration 결정 + wrapper-self IA mirror 작업.
metadata:
  category: governance
  ddd_pattern: Domain Service
  bounded_context: codeforge-governance
  introduced_by: CFP-1668
  adr_refs:
    - ADR-099
    - ADR-100
    - ADR-101
    - ADR-103
    - ADR-111
---

# codeforge:confluence-migration Skill

codeforge family 의 Confluence doc-mirror governance 단일 진입점.

wrapper-self (`CFP` space) + consumer (per-instance) 양 적용 — 분산된 5 ADR / IA tree / agent / workflow / script 자료를 단일 lookup-table 로 제공.

## 적용 조건

- `project.yaml atlassian.enabled: true` + `atlassian.confluence.mirror_targets` 비어 있지 않음 (consumer Confluence migration 활성)
- 또는 wrapper-self CFP space 작업 (docs/confluence-ia-tree.yaml 갱신 / sync 작업)

조건 불충족 시 = Confluence migration 비활성 상태 (consumer-guide §1o Step 1-4 셋업 선행 필요).

---

## 1. 공통 invariant 7건

CFP-1668 Story §2.3 verbatim. consumer scope 동일 적용 (ADR-100 Amendment 2 + ADR-111 Amendment 2).

| # | invariant | SSOT |
|---|---|---|
| 1 | **git = SoR-work** (Source of Record for working state) — git repo 가 진실의 원천 | ADR-100 §결정 1 |
| 2 | **Confluence = SoR-docs readable mirror** (단방향 git→Confluence) — Confluence 에서 직접 edit 금지 | ADR-100 §결정 2 |
| 3 | **3-anchor verify** — content property: git-source sha256 / native version / sync commit SHA. push 시 3 anchor stamp 의무 | ADR-103 §결정 3 + ADR-101 verify-before-trust |
| 4 | **mark engine path = retain_for_future** (mcp-direct deviation, #1320 secret 주입 후 활성) — 현재 MCP-direct 운영 중 (CFP-1491 W5-S17 precedent) | ADR-103 §결정 1 + docs/confluence-ia-tree.yaml deviation_path |
| 5 | **Issue-only retain 5 영역** — Story file / FIX Ledger / Lane Evidence / decision packet / spawn prompt = Confluence mirror 0 (ratchet 강화, ADR-111 Amendment 2 §결정 2) | ADR-111 Amendment 2 §결정 2 |
| 6 | **mirror 대상 closed-enum 5** — `adr` / `architecture_doc` / `change_plan` / `domain_knowledge` / `orchestrator_playbook` (확장 0 invariant) | ADR-111 Amendment 1 + Amendment 2 §결정 1 |
| 7 | **consumer ⊆ wrapper SYMMETRIC subset** — consumer mirror 대상은 wrapper closed-enum 5 의 subset 만 허용, 확장 0 invariant | ADR-111 Amendment 2 §결정 1 |

---

## 2. wrapper-self 진입점 (CFP space 정합)

wrapper-self = `mclayer/plugin-codeforge` Confluence space `CFP` 작업 영역.

### 2.1 ADR cross-ref

| ADR | 역할 |
|---|---|
| [ADR-099](../../archive/adr/ADR-099-atlassian-allow-redefinition.md) | Atlassian tool allow redefinition — `mcp__atlassian__*` 허용 관리 |
| [ADR-100](../../archive/adr/ADR-100-confluence-doc-ssot-recognition.md) | Confluence doc SSOT recognition — git = SoR-work / Confluence = readable mirror 원칙 |
| [ADR-101](../../archive/adr/ADR-101-verify-before-trust-confluence-rest.md) | verify-before-trust Confluence REST — 응답 검증 의무 |
| [ADR-103](../../archive/adr/ADR-103-git-confluence-sync-mechanism.md) | Confluence sync mechanism — 3-anchor stamp + mark engine path |
| [ADR-111](../../archive/adr/ADR-111-confluence-mirror-classification-policy.md) | mirror classification policy — closed-enum 5 mirror 대상 + 5 Issue-only retain 면제 SSOT |

### 2.2 IA tree SSOT

- **파일**: `docs/confluence-ia-tree.yaml`
- **space**: `CFP` (CodeForge)
- **homepage_id**: `1867943`
- **schema**: `1.2` (CFP-1668 MINOR bump — consumer instantiate template 신설)
- **ia_axis**: `per-plugin-top-level-plus-cross-cutting-sibling`

### 2.3 agent 2종

| agent | 역할 |
|---|---|
| `confluence-sync-read-verify` | Confluence page 내용 + 3-anchor property 읽기 verify |
| `confluence-sync-write-commit` | git doc → Confluence push + 3-anchor stamp write |

### 2.4 workflow 4종

| workflow | 역할 |
|---|---|
| `confluence-doc-sync.yml` | manual + PR trigger sync |
| `confluence-drift-detection.yml` | 24h cron drift detection (git sha256 ↔ Confluence property 비교) |
| `issue-design-content-confluence-link.yml` | GitHub Issue 설계 내용 ↔ Confluence page 링크 |
| `atlassian-tool-drift.yml` | Atlassian tool allow-by-omission drift 감지 (ADR-099 + ADR-103 §결정 3) |

### 2.5 script 5종

| script | 역할 |
|---|---|
| `scripts/confluence-sync-3anchor.py` | 3-anchor stamp sync 실행 (Python, ADR-061 multi-line script 정합) |
| `scripts/check-confluence-drift.sh` | drift detection bash wrapper |
| `scripts/check-atlassian-tool-drift.sh` | Atlassian tool drift check (ADR-099) |
| `scripts/check-issue-design-content-confluence-link.sh` | Issue-design-content link 정합 check |
| `scripts/check-no-atlassian.sh` | Atlassian MCP 비허용 환경에서 호출 방지 guard |

---

## 3. consumer 진입점 (4-step SOP)

consumer 측 Confluence migration 셋업 상세는 **`docs/consumer-guide.md §1o`** (CFP-1668 신설) SSOT.

요약 4-step:

### Step 1 — space 결정

consumer 결정:
- **(a) consumer 자기 Confluence space 생성** (권장 derived default — ownership 명확, parent_id collision 회피)
- **(b) wrapper `CFP` space 안 sub-tree** (cross-org space sharing 정합, OOS edge case 2번 — 소규모 consumer)

### Step 2 — IA tree instantiate

`docs/confluence-ia-tree.yaml` schema 1.2 `per_consumer_instantiate_template` section 사용. per-consumer skeleton 작성 후 consumer overlay에 등록.

### Step 3 — mirror 대상 선택

closed-enum 5 의 subset 선택 (`project.yaml atlassian.confluence.mirror_targets`):

```yaml
atlassian:
  enabled: true
  confluence:
    base_url: "https://<instance>.atlassian.net"
    space_key: <CONSUMER-SPACE-KEY>
    instance: <instance-hostname>
    homepage_id: "<numeric-id>"
    mirror_targets: [adr, architecture_doc]   # subset of [adr, architecture_doc, change_plan, domain_knowledge, orchestrator_playbook]
    api_token_env: <CONSUMER_ATLASSIAN_API_TOKEN>
    user_email_env: <CONSUMER_ATLASSIAN_USER_EMAIL>
    per_doc_type_override:                    # optional
      adr:
        parent_page_id: "<numeric-id>"
```

### Step 4 — 첫 push dry-run

```bash
python scripts/confluence-sync-3anchor.py --dry-run --space <CONSUMER-SPACE-KEY>
```

dry-run 결과 = mapping table (git path → Confluence page) + 3-anchor verify report. fail 시 ADR-101 verify-before-trust path.

---

## 4. cross-ref

| 영역 | 참조 |
|---|---|
| Confluence governance | ADR-100 / ADR-111 / ADR-099 / ADR-101 / ADR-103 |
| consumer-applicability | [ADR-083](../../archive/adr/ADR-083-consumer-applicability-filter.md) (본 Story Wave 1 으로 `unknown` → `applicable` 전환) |
| consumer adoption | [ADR-027](../../archive/adr/ADR-027-consumer-adoption-protocol.md) (atlassian.* schema 정합) |
| verdict packet | review-verdict-v4 (verdict-level optional bool fields — 현재 버전은 파일 frontmatter SSOT) |
| doc location | [docs/doc-locations.yaml](../../docs/doc-locations.yaml) (confluence_variant sub-tree — schema 1.2, CFP-1668) |
| consumer guide | [docs/consumer-guide.md §1o](../../docs/consumer-guide.md) (Confluence migration 셋업 4-step SOP) |
| IA tree | [docs/confluence-ia-tree.yaml](../../docs/confluence-ia-tree.yaml) (schema 1.2, per-consumer template 신설) |

---

## 5. CONDITIONAL applicability

`project.yaml atlassian.enabled: bool`:

- **`false` 또는 부재**: 본 skill 영역 미적용. consumer Confluence migration 비활성 opt-out (git-only governance 유지).
- **`true` + `mirror_targets` 비어 있음**: mirror 비활성 (atlassian suite 활성이나 mirror 0 상태).
- **`true` + `mirror_targets` 비어 있지 않음**: mirror 활성 — 본 skill 의 invariant 7건 + consumer-guide §1o 절차 적용.

consumer-applicability filter (ADR-083 §결정 1 4-way enum):
- **`applicable`**: `atlassian.enabled: true` + `mirror_targets` 존재 consumer
- **`plugin`**: wrapper-self CFP space 작업 (dogfood)
- **`consumer`**: consumer overlay에서 atlassian block 활성
- **`unknown`**: atlassian.enabled 미선언 = 면제 (opt-in invariant)

---

## 6. Issue-only retain 영역 (ADR-111 Amendment 2 §결정 2)

다음 5 영역 = **Confluence mirror 절대 금지** (Issue-only retain invariant, ratchet 강화):

1. **Story file** (`docs/stories/<KEY>.md`) — Issue 안 §1-§14 모두 포함
2. **FIX Ledger** (Story file §10 sub-section) — fix-event-v1 contract
3. **Lane Evidence** (Story file §14 sub-section) — ADR-031 carrier
4. **decision packet** (`decisions/<packet_id>.yaml`)
5. **spawn prompt** (ephemeral, session-scoped) — ADR-082 sub-scope 1-C

> **ratchet 강화 rationale**: ADR-111 Amendment 2 §결정 2 — 위 5 영역은 governance audit trail 의 원자 단위. Confluence mirror 시 mutable Confluence page 와 immutable Issue history 간 split-brain 위험. Issue-only retain = 단방향 audit trail 보존 invariant.
