"""
CFP-1523 Phase 2 — legacy_adr_migration_map 148 row 생성 스크립트
ADR-061 §결정 1 외부 .py 파일 의무 (multi-line Python)
"""

import yaml
import re

# ─── 1. Confluence ADR 페이지 목록 (getConfluencePageDescendants 결과, 111개)
confluence_adr_pages = [
    {"id": "2097174", "title": "ADR-099 — check-no-atlassian.sh 역전 + Atlassian-allow 재정의"},
    {"id": "2129922", "title": "ADR-100 — Confluence doc SSOT 인정 (wrapper governance docs 의 Confluence authoritative readable source 추가)"},
    {"id": "2064386", "title": "ADR-101 — verify-before-trust Confluence REST ground-truth (SSRF / 응답 변조 boundary)"},
    {"id": "2097197", "title": "ADR-102 — Ratchet 약화 evidence-gate governance anchor (spec-level predecessor reversal sunset mechanism)"},
    {"id": "2097218", "title": "ADR-103 — git→Confluence sync mechanism (custom GitHub Action + 3-anchor hash-git-source + Option B narrow allow)"},
    {"id": "2097239", "title": "ADR-036: Project key atomic reservation — KEY = PREFIX-Issue#"},
    {"id": "2064409", "title": "ADR-001: Review/Test 워커 에이전트 통합 — Claude/Codex 2종으로 단일화하고 도메인은 PL packet으로 분리"},
    {"id": "2129989", "title": "ADR-071: Orchestrator-user dialog convergence — frame mode + 4 layer 검증 + cross-Story 영속 incidents file"},
    {"id": "2130011", "title": "ADR-073: Orchestrator verify-before-assert — cross-repo ground truth + assumption verify mandate"},
    {"id": "2064430", "title": "ADR-074: CLAUDE.md Amendment ref drift detection lint"},
    {"id": "2064454", "title": "ADR-075: Defense-in-depth sublayer registry — sublayer enumeration SSOT 분리"},
    {"id": "2130033", "title": "ADR-002: 모든 에이전트 md의 \"문서화 표준\" 섹션은 DocsAgent.md SSOT 참조 1줄만 유지"},
    {"id": "2064476", "title": "ADR-076: 선언적 reconciliation upgrade flow SSOT"},
    {"id": "2130058", "title": "ADR-077: Clarification 강제 재조사 전파 정책 SSOT"},
    {"id": "2064498", "title": "ADR-078: 살아있는 구조 설계 문서 (living architecture doc) 유지 정책 SSOT"},
    {"id": "2064520", "title": "ADR-079: KST timestamp display mandate (Layer-bounded)"},
    {"id": "2064544", "title": "ADR-080: Agent role terminology — deputy → SubAgent canonical form + identifier preservation"},
    {"id": "2162690", "title": "ADR-081: Codex worker prompt boilerplate composition SSOT"},
    {"id": "2064566", "title": "ADR-003: SSOT drift 검출·회복 책임을 3 layer로 분리"},
    {"id": "2097260", "title": "ADR-082: Write-time self-write verification mandate"},
    {"id": "2064594", "title": "ADR-083: Consumer-applicability filter — repo-kind detection truth-table + positive whitelist"},
    {"id": "2064616", "title": "ADR-084: numeric-space-sharing channel disjointness invariant codification"},
    {"id": "2064640", "title": "ADR-085: Multi-session collaboration protocol"},
    {"id": "2130080", "title": "ADR-004: 설계 lane 재구조화 — ArchitectPLAgent + SecurityArchitectAgent 도입"},
    {"id": "2097282", "title": "ADR-037: Plugin version bump rule SSOT — Option β (Lenient + wrapper-coupling) + Option α (Conventional Commits)"},
    {"id": "2064661", "title": "ADR-005: Plugin Self-Application N/A 표준화"},
    {"id": "2162713", "title": "ADR-086: Deputy 신설 결정 framework"},
    {"id": "2130101", "title": "ADR-038: Progress visualization via TodoWrite (single-Story, hierarchical 4-marker)"},
    {"id": "2064682", "title": "ADR-039: Orchestrator subagent default for codeforge modification work"},
    {"id": "2064702", "title": "ADR-087: Deploy lane 신설"},
    {"id": "2064722", "title": "ADR-006: TestContractArchitectAgent 신설"},
    {"id": "2097304", "title": "ADR-040: Worktree convention — base directory + naming + lifecycle (CFP-134 Epic Wave 1)"},
    {"id": "2162754", "title": "ADR-041: Doc Location Registry — codeforge plugin doc taxonomy 통합 SSOT"},
    {"id": "2097325", "title": "ADR-088: Deploy Review lane 신설"},
    {"id": "2097346", "title": "ADR-042: Agent model selection policy — Opus / Sonnet / Haiku tier criteria"},
    {"id": "2064745", "title": "ADR-042 (alt): Codeforge measurement channel architecture"},
    {"id": "2097366", "title": "ADR-043: Codeforge telemetry privacy policy"},
    {"id": "2130121", "title": "ADR-044: Phase-scoped sequential team SSOT (CFP-134 Epic Wave 2)"},
    {"id": "2130141", "title": "ADR-089: Schema 변경 7 원칙"},
    {"id": "2064765", "title": "ADR-045: Story 완료 회고 의무화 — Phase 2 PR merge 후 PMOAgent 자동 trigger"},
    {"id": "2097386", "title": "ADR-046: ResearcherAgent role redefinition — Concept formulation + Deep exploration + Requirement reshape mandate"},
    {"id": "2064787", "title": "ADR-047: Framework Migration Epic Pattern — PMOAgent Version Delta Review + Deputy Migration Notes"},
    {"id": "2130162", "title": "ADR-047 (alt): GitOpsAgent — cross-cutting git ops agent in codeforge-pmo plugin (CFP-139 / CFP-134 Wave 3)"},
    {"id": "2064807", "title": "ADR-048: CI-native 테스트 실행 — TestAgent 제거 + SecurityTestPL opt-in (CFP-317)"},
    {"id": "2162816", "title": "ADR-048 (alt): GitHub Enterprise Cloud Governance-as-Code (rulesets / required workflows / audit log)"},
    {"id": "2064829", "title": "ADR-090: Cross-layer 참조 정책"},
    {"id": "2097406", "title": "ADR-049: Issue Types + Sub-issues Native Migration (label hack → 1st-class)"},
    {"id": "2162880", "title": "ADR-050: Parallel Epic Conflict Coordination — 복수 Orchestrator 세션 충돌 조율 정책 (CFP-344)"},
    {"id": "2130184", "title": "ADR-051: SSOT Exception Skill Extraction Pattern"},
    {"id": "2130206", "title": "ADR-007: DataMigrationArchitectAgent 신설"},
    {"id": "2097426", "title": "ADR-052: Codex Proactive Check — 6 Touchpoints"},
    {"id": "2097446", "title": "ADR-091: ArchitectLane DDD vocabulary governance"},
    {"id": "2097467", "title": "ADR-053: 구조적 변경 재구동 선행 의무 및 codeforge 변경 시 consumer 배포 포함"},
    {"id": "2064890", "title": "ADR-092: Changelog SSOT location"},
    {"id": "2064910", "title": "ADR-008: Inter-plugin Contract Versioning — review_verdict v1.x compat / v2.0 BREAKING"},
    {"id": "2162901", "title": "ADR-093: Completion report 4-field schema"},
    {"id": "2097530", "title": "ADR-009: Wrapper-only core + writer-distributed lane plugins (ζ arc decomposition)"},
    {"id": "2097551", "title": "ADR-054: doc-only Story fast-path 분류 표 + fallback 규칙"},
    {"id": "2097571", "title": "ADR-010: Inter-plugin Contract Sibling Sync — canonical/sibling 책임 + sync 트리거 + drift 처리 정책"},
    {"id": "2064954", "title": "ADR-055: Integration Test Lane — codeforge-test 통합테스트 전용 부활"},
    {"id": "2130272", "title": "ADR-056: Domain-Concept knowledge directory separation"},
    {"id": "2162962", "title": "ADR-094: Consumer 구형 버전 Fallback 정책"},
    {"id": "2130293", "title": "ADR-056 (alt): 요구사항 레인 코드 컨텍스트 3 에이전트 추가"},
    {"id": "2097593", "title": "ADR-011: Inter-plugin Contract Drift Detection"},
    {"id": "2097613", "title": "ADR-057: Orchestrator Opus 필수화 + Sonnet → Opus rate-limit fallback 정책"},
    {"id": "2162982", "title": "ADR-095: 9 ADR sunset metric 표준화"},
    {"id": "2130379", "title": "ADR-058: ADR 해소 기준 섹션 의무화 + transitional 분류 frontmatter"},
    {"id": "2130399", "title": "ADR-012: Wrapper CLAUDE.md SSOT Boundary"},
    {"id": "2097653", "title": "ADR-059: Multi-round Adversarial Debate Protocol (debate-protocol-v1)"},
    {"id": "2163002", "title": "ADR-013: Codeforge Family Dogfood-out Policy"},
    {"id": "2097673", "title": "ADR-060: Evidence-enforceable promotion framework"},
    {"id": "2065056", "title": "ADR-096: min_prerequisite_version manifest schema"},
    {"id": "2097693", "title": "ADR-061: Python script-writing convention — heredoc escape guard + external .py 의무"},
    {"id": "2097714", "title": "ADR-062: Carrier Story bootstrap dependency 룰"},
    {"id": "2130425", "title": "ADR-097: Paradigm replacement governance anchor"},
    {"id": "2163045", "title": "ADR-098: UpgradeAgent runtime ownership"},
    {"id": "2163065", "title": "ADR-063: Marketplace ↔ plugin.json atomic invariant — 3-file coordination"},
    {"id": "2097737", "title": "ADR-014: Operational Risk SSOT Distribution — codeforge-design plugin owns §7.4 schema, wrapper owns matrix/decision rows"},
    {"id": "2097759", "title": "ADR-064: codeforge 결정 원칙 mandate — 결정 내용·결정 제시·적용 속도 normative SSOT"},
    {"id": "2163087", "title": "ADR-065: ArchitectAgent Phase 1 산출물 mechanical sync self-check 의무 (non-marketplace 영역)"},
    {"id": "2065138", "title": "ADR-104: 운영 phase 1st-class 정의"},
    {"id": "2163113", "title": "ADR-066: CODEFORGE_CROSS_REPO_PAT rotation policy"},
    {"id": "2163133", "title": "ADR-015: Stateful / restart invariant test category — codeforge-test 2 agent split + §8.5 CONDITIONAL"},
    {"id": "2065161", "title": "ADR-067: fix-ledger implementability escalation + max FIX overflow handling"},
    {"id": "2097781", "title": "ADR-016: Marketplace registration policy for codeforge plugin family (narrow scope)"},
    {"id": "2097805", "title": "ADR-068: Boundary completeness invariants (semantic dual-binding)"},
    {"id": "2163218", "title": "ADR-069: Multi-Repo Hierarchical Story Key System"},
    {"id": "2065243", "title": "ADR-105: 자동 rollback 도메인 재정의"},
    {"id": "2097825", "title": "ADR-017: Skill override path enforcement for codeforge dogfood artifacts"},
    {"id": "2097845", "title": "ADR-070: Codex verify-before-trust pattern (sandbox access invariant)"},
    {"id": "2097865", "title": "ADR-018: Gemini Decider Auto-Proceed System (Phase 1 doc-only policy)"},
    {"id": "2163239", "title": "ADR-019: Sonnet Decider Auto-Proceed Policy"},
    {"id": "2163281", "title": "ADR-106: 운영 metric → PMOAgent input 회로 (self-improving loop)"},
    {"id": "2130615", "title": "ADR-023: Lane plugin lifecycle — add / deprecate / rename governance"},
    {"id": "2163304", "title": "ADR-020: Cross-repo Epic 패턴"},
    {"id": "2130639", "title": "ADR-72: ProductionEvidence Deputy 신설 + EPIC cutover gate evidence quad"},
    {"id": "2065349", "title": "ADR-021: Phase-gap measurable signal — debut-audit 카테고리 #2 backing"},
    {"id": "2065371", "title": "ADR-RESERVATION: ADR 번호 예약 레지스트리"},
    {"id": "2097973", "title": "ADR-022: Sonnet Decider — Comprehensive Policy"},
    {"id": "2098015", "title": "ADR-024: Story-scoped branch policy — main 직접 수정 금지 + Phase 2 enforcement deferred"},
    {"id": "2098035", "title": "ADR-025: Stop discipline — Decider-decides ≠ user-confirms"},
    {"id": "2098055", "title": "ADR-026: Post-merge follow-up automation"},
    {"id": "2130680", "title": "ADR-027: Consumer Adoption Protocol — bootstrap + 3-trigger enforcement"},
    {"id": "2163370", "title": "ADR-028: Superpowers integration policy — codeforge family wrapping mechanism"},
    {"id": "2163392", "title": "ADR-029: Phase execution visibility expansion — sub-step terminal narration"},
    {"id": "2163415", "title": "ADR-030: Live Epic lane-entry policy + real-funds gate"},
    {"id": "2098076", "title": "ADR-031: Lane-spawn evidence trail"},
    {"id": "2130703", "title": "ADR-032: ADR-027 Amendment 1 — bootstrap strict mode opt-in (hard enforcement layer)"},
    {"id": "2098097", "title": "ADR-033: Docker-first Infra Engineering — InfraEngineerAgent mandate 재정의 + 4 SSOT 매트릭스 cell update"},
    {"id": "2098139", "title": "ADR-034: Pre-Issue Brainstorming as Optional Stage 0 — orchestrator-playbook §1.2.0 + story.yml spec_link"},
    {"id": "2065516", "title": "ADR-035: codeforge agent teams + GitOps + retro 의무화 + ADR-022 deprecate Epic architecture"},
]

# ─── 2. ADR number → category 매핑 (로컬 frontmatter 추출 결과)
adr_category_map = {
    "ADR-001": "Architecture",
    "ADR-002": "Team & Process",
    "ADR-003": "Team & Process",
    "ADR-004": "Team & Process",
    "ADR-005": "Team & Process",
    "ADR-006": "Team & Process",
    "ADR-007": "Team & Process",
    "ADR-008": "Architecture",
    "ADR-009": "Team & Process",
    "ADR-010": "Team & Process",
    "ADR-011": "Team & Process",
    "ADR-012": "Team & Process",
    "ADR-013": "Team & Process",
    "ADR-014": "Architecture",
    "ADR-015": "Architecture",
    "ADR-016": "Team & Process",
    "ADR-017": "Team & Process",
    "ADR-018": "Team & Process",
    "ADR-019": "Team & Process",
    "ADR-020": "orchestration",
    "ADR-021": "audit",
    "ADR-022": "Team & Process",
    "ADR-023": "governance",
    "ADR-024": "governance",
    "ADR-025": "Team & Process",
    "ADR-026": "Team & Process",
    "ADR-027": "Plugin Distribution & Consumer Onboarding",
    "ADR-028": "Team & Process",
    "ADR-029": "orchestration",
    "ADR-030": "governance",
    "ADR-031": "orchestration",
    "ADR-032": "Plugin Distribution & Consumer Onboarding",
    "ADR-033": "Architecture",
    "ADR-034": "workflow-policy",
    "ADR-035": "architecture",
    "ADR-036": "process",
    "ADR-037": "governance",
    "ADR-038": "orchestration",
    "ADR-039": "orchestration-discipline",
    "ADR-040": "tooling-infrastructure",
    "ADR-041": "Team & Process",
    "ADR-042": "governance",
    "ADR-042-alt": "orchestration-discipline",
    "ADR-043": "orchestration-discipline",
    "ADR-044": "orchestration",
    "ADR-045": "Team & Process",
    "ADR-046": "agent-design",
    "ADR-047": "Team & Process",
    "ADR-047-alt": "agent-design",
    "ADR-048": "architecture",
    "ADR-048-alt": "Infrastructure",
    "ADR-049": "Team & Process",
    "ADR-050": "governance",
    "ADR-051": "Plugin Architecture",
    "ADR-052": "workflow-policy",
    "ADR-053": "orchestrator-policy",
    "ADR-054": "Process",
    "ADR-055": "architecture",
    "ADR-056": "agent-design",
    "ADR-056-alt": "agent-design",
    "ADR-057": "governance",
    "ADR-058": "Team & Process",
    "ADR-059": "orchestration",
    "ADR-060": "governance",
    "ADR-061": "Team & Process",
    "ADR-062": "governance",
    "ADR-063": "Team & Process",
    "ADR-064": "governance",
    "ADR-065": "Team & Process",
    "ADR-066": "security",
    "ADR-067": "governance",
    "ADR-068": "governance",
    "ADR-069": "orchestration",
    "ADR-070": "workflow-policy",
    "ADR-071": "governance",
    "ADR-072": "governance",
    "ADR-073": "governance",
    "ADR-074": "governance",
    "ADR-075": "governance",
    "ADR-076": "governance",
    "ADR-077": "governance",
    "ADR-078": "governance",
    "ADR-079": "governance",
    "ADR-080": "governance",
    "ADR-081": "workflow-policy",
    "ADR-082": "governance",
    "ADR-083": "governance",
    "ADR-084": "workflow-policy",
    "ADR-085": "governance",
    "ADR-086": "governance",
    "ADR-087": "lifecycle",
    "ADR-088": "lifecycle",
    "ADR-089": "governance",
    "ADR-090": "governance",
    "ADR-091": "governance",
    "ADR-092": "tooling-infrastructure",
    "ADR-093": "tooling-infrastructure",
    "ADR-094": "tooling-infrastructure",
    "ADR-095": "governance",
    "ADR-096": "tooling-infrastructure",
    "ADR-097": "governance",
    "ADR-098": "governance",
    "ADR-099": "governance",
    "ADR-100": "governance",
    "ADR-101": "security",
    "ADR-102": "governance",
    "ADR-103": "tooling-infrastructure",
    "ADR-104": "governance",
    "ADR-105": "governance",
    "ADR-106": "governance",
    "ADR-RESERVATION": "governance",
}

def extract_adr_key(title):
    """Confluence title에서 ADR key 추출"""
    # ADR-NNN (alt) 패턴
    m = re.match(r'^(ADR-\d+)\s*\(alt\)', title)
    if m:
        return m.group(1) + "-alt"
    # ADR-RESERVATION
    if "ADR-RESERVATION" in title:
        return "ADR-RESERVATION"
    # ADR-NNN 패턴
    m = re.match(r'^(ADR-\d+)', title)
    if m:
        return m.group(1)
    # ADR-72 (no leading zero)
    m = re.match(r'^(ADR-72)', title)
    if m:
        return "ADR-072"
    return None

# ─── 3. IPC 페이지 목록 (30개)
ipc_pages = [
    {"id": "2162838", "title": "comment-prefix-registry v1.3"},
    {"id": "2064850", "title": "debate-protocol-v1 registry"},
    {"id": "2097489", "title": "Debut-audit Triage v1"},
    {"id": "2162941", "title": "decision-packet v1"},
    {"id": "2130229", "title": "decision-packet v2.1"},
    {"id": "2130250", "title": "Defense-in-depth sublayer registry v1.0"},
    {"id": "2064975", "title": "deploy-output-v1"},
    {"id": "2064995", "title": "deploy-review-output-v1"},
    {"id": "2065015", "title": "design_output v1 — Inter-plugin Contract (ARCHIVED)"},
    {"id": "2130338", "title": "design_output v2 — Inter-plugin Contract"},
    {"id": "2065035", "title": "develop_output v1 — Inter-plugin Contract"},
    {"id": "2130359", "title": "evidence-check-registry v1.0"},
    {"id": "2097633", "title": "fix-event v1"},
    {"id": "2163024", "title": "git_ops_event v1 — Inter-plugin Contract"},
    {"id": "2130445", "title": "imperative-walker-protocol-v1 — Inter-plugin Contract Registry"},
    {"id": "2130465", "title": "label-registry v1"},
    {"id": "2130487", "title": "operational-signal-v1 — 운영 신호 input schema (self-improving loop)"},
    {"id": "2065076", "title": "parallel-dispatch-protocol-v1 registry"},
    {"id": "2065097", "title": "pmo_output v1 — Inter-plugin Contract"},
    {"id": "2065118", "title": "reconcile-protocol-v1 — Inter-plugin Contract Registry"},
    {"id": "2163156", "title": "requirements_output v1 — Inter-plugin Contract"},
    {"id": "2065181", "title": "review_verdict v1 — Inter-plugin Contract (ARCHIVED)"},
    {"id": "2163197", "title": "review_verdict v2 — Inter-plugin Contract (CFP-35 ζ arc retrofit)"},
    {"id": "2065202", "title": "review_verdict v3 — Inter-plugin Contract (CFP-61 Phase 1B-1)"},
    {"id": "2130532", "title": "severity-propagation-v1 — Inter-plugin Contract Registry"},
    {"id": "2130573", "title": "test_verdict v1 — Inter-plugin Contract"},
    {"id": "2097885", "title": "test-verdict-v2 — Integration Lane 결과 패킷 (Canonical)"},
    {"id": "2163260", "title": "stop-event v1"},
    {"id": "2065306", "title": "review_verdict v4 — Inter-plugin Contract (CFP-137 / ADR-044)"},
    {"id": "2065327", "title": "label-registry v2"},
]

# ─── 4. 행 생성
rows = []
cascade_order = 1

# ADR 111행
for page in confluence_adr_pages:
    title = page["title"]
    page_id = page["id"]

    # ADR key 추출
    adr_key = extract_adr_key(title)
    if adr_key is None:
        # fallback
        adr_key = "unknown"

    # ADR-72 special case
    if "ADR-72" in title and adr_key != "ADR-RESERVATION":
        adr_key = "ADR-072"

    category = adr_category_map.get(adr_key, "governance")

    rows.append({
        "page_id": int(page_id),
        "title": title,
        "source_file": f"docs/adr/",  # ADR root source
        "category": category.lower(),  # case_normalization lowercase
        "previous_parent_id": 2097153,
        "new_parent_id": 2065980,
        "type": "adr",
        "cascade_order": cascade_order,
    })
    cascade_order += 1

# IPC 30행
for page in ipc_pages:
    rows.append({
        "page_id": int(page["id"]),
        "title": page["title"],
        "source_file": "docs/inter-plugin-contracts/",
        "category": None,
        "previous_parent_id": 2129949,
        "new_parent_id": 2130942,
        "type": "ipc",
        "cascade_order": cascade_order,
    })
    cascade_order += 1

# Consumer Guide 1행
rows.append({
    "page_id": 2162774,
    "title": "Consumer Guide — 플러그인 적용 가이드",
    "source_file": "docs/consumer-guide.md",
    "category": None,
    "previous_parent_id": 1867943,
    "new_parent_id": 2163807,
    "type": "consumer-guide",
    "cascade_order": cascade_order,
})

print(f"Total rows generated: {len(rows)}")
print(f"  ADR rows: {sum(1 for r in rows if r['type'] == 'adr')}")
print(f"  IPC rows: {sum(1 for r in rows if r['type'] == 'ipc')}")
print(f"  Consumer Guide rows: {sum(1 for r in rows if r['type'] == 'consumer-guide')}")

# ─── 5. YAML 출력
output = {"legacy_adr_migration_map": {"rows": rows}}

with open("C:/workspace/mclayer/plugin-codeforge-cfp-1523-phase-2/scripts/migration_map_rows.yaml", "w", encoding="utf-8") as f:
    yaml.dump(output, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

print("migration_map_rows.yaml written.")
