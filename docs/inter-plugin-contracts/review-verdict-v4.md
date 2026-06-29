---
kind: contract
contract_version: "4.15"
status: Active
related_plugins:
  - codeforge (wrapper, consumer of FIX routing data + Orchestrator self-write)
  - codeforge-review (lane plugin, producer + synthesizer + final pl_recommendation author)
related_adrs:
  - ADR-001  # review-agent-unification — lane-agnostic worker
  - ADR-008  # Inter-plugin Contract Versioning (MAJOR/MINOR bump)
  - ADR-010  # Inter-plugin Contract Sibling Sync (canonical/sibling 관계)
  - ADR-022  # Deprecated by ADR-035 — Sonnet decider 영역 본 v4 에서 정식 제거
  - ADR-035  # codeforge agent teams Epic architecture (D2 implementation level)
  - ADR-042  # Amendment 8 — design lane 7+3+1 roster 재편 carrier (CFP-1086 — deputy_axis_restructure_self_check_passed field 신설)
  - ADR-044  # Phase-scoped sequential team SSOT (본 v4 carrier)
  - ADR-059  # debate-protocol-v1 — anchor_id field 가 stable identifier 로 의존 (CFP-391)
  - ADR-065  # ArchitectAgent Phase 1 mechanical self-check — mechanical_self_check_passed field (CFP-438)
  - ADR-068  # Boundary completeness invariants — boundary_completeness_self_check_passed field (CFP-527) + Amendment 1 (CFP-528) — I-5 dimensional_empirical_self_check_passed + Amendment 2 (CFP-1086) — wording SSOT chief tie-break ladder scope expansion + Amendment 3 (CFP-1087) — I-6 audit-gate-pointer-existence invariant (audit_gate_pointer_self_check_passed field)
  - ADR-063  # Marketplace atomic invariant — marketplace_sync_declared field (CFP-597 Amendment 1)
  - ADR-086  # Deputy 신설 결정 framework (CFP-1086 신설) — deputy_axis_restructure_self_check_passed field carrier
  - ADR-073  # Orchestrator verify-before-assert (CFP-1087 cross-ref backref — I-6 verification primitive ↔ §결정 1 verify-before-assert primitive directly-analogous, ADR-073 본문 0건 변경)
  - ADR-091  # ArchitectLane DDD vocabulary governance (CFP-1117 신설) — §결정 6 enforcement layer 3-tier 의 3번째 tier (review-verdict-v4 enum) + §결정 7 INV-5 forcing function review-verdict finding 연결 (findings[].type 3 DDD literal bc_violation / aggregate_violation / ubiquitous_language_drift carrier)
  - ADR-068  # I-2 cross-module propagation completeness — CFP-1303 parallel_anchors_checked[] semantic anchor (cross-anchor parity check field 가 I-2 의 review-verdict layer realization, Amendment 1 I-5 dimensional empirical / Amendment 3 I-6 audit-gate-pointer 와 disjoint axis)
  - ADR-111  # Confluence-mirror classification policy SSOT (CFP-1424 carrier) — §결정 5 cross-link discipline 정합 (Confluence mirror 대상 doc Issue body inline 시 Confluence anchor link presence verify). findings[].type "confluence-mirror-link-missing" literal carrier (closed-enum 8 → 9 ratchet, additive only). DesignReviewPL check item 추가 동반 (sibling cross-repo PR codeforge-review/agents/DesignReviewPLAgent.md)
  - ADR-125  # 요구사항리뷰 lane 신설 (CFP-2326 carrier, Epic CFP-2324 S2) — §결정 5 lane enum 에 "requirements-review" 4번째 literal 추가 (v4.12 → v4.13 MINOR). RequirementsReviewPLAgent = ADR-001 lane-agnostic base 재사용 (신규 worker 0). 리뷰 lane 식별자 (작성 lane requirements 아님 — ADR-125 결정 4 disjoint axis 작성측 ADR-052 touchpoint #4 ↔ 리뷰측 producer 게이트)
  - ADR-112  # Living Architecture per-Epic mandatory update gate SSOT (CFP-1426 carrier, Mega-Epic CFP-1415 Sub-C S3.2). §결정 3 review-verdict-v4 v4.10 → v4.11 MINOR bump 6번째 verdict-level optional bool field living_architecture_updated_self_check_passed carrier + §결정 4 findings[].type enum 10번째 literal "living-architecture-not-updated" carrier (closed-enum 9 → 10 ratchet, additive only). ArchitectAgent Epic close 직전 5-anchor section (arc42 §3+§5 + C4 Container+Component + Open Decisions Pending) 최소 1개 update OR `[living-arch-no-impact: <rationale>]` explicit declare 통과 시 true. DesignReviewPL false + no-op declare 부재 detect 시 "living-architecture-not-updated" finding emit. sibling Story #1425 (S3.1) = ADR-078 Amendment 2 5-anchor codify base. DesignReviewPL check item 추가 동반 (sibling cross-repo PR codeforge-review/agents/DesignReviewPLAgent.md)
  - ADR-064  # 결정 13 root-cause 사다리 3rd rung (문제정의 오류 → 요구사항 lane 재진입) SSOT (CFP-2350 Amendment 13). CFP-2358 v4.13 → v4.14 MINOR bump — runtime-failure 변종 falsification verdict 의 비대칭 규칙 (file:line invariant-violation finding 1개 > N attestation, Popper) 가 본 §결정 13 재진입 규율 3 (비대칭 결정규칙) 의 verdict-level realization. verify_status: verified — worktree Read ADR-064 "결정 13 — 문제정의 오류 rung (Trace 9, 3rd rung)". ADR-064 본문 0건 변경 (본 PS1 = Phase 2 mechanical wire carrier — §결정 13 Amendment 결정 2 가 review-verdict-v4 runtime-failure verdict enum 을 Phase 2 별 carrier defer 로 명시)
  - ADR-125  # 요구사항리뷰 lane Amendment 2 runtime-failure 변종 (internal-invariant ground-truth falsification 축, CFP-2350) SSOT. CFP-2358 v4.13 → v4.14 MINOR bump — lane enum 무변경 (requirements-review 재사용) + runtime-failure 변종의 비대칭 verdict 규칙 본문 명시. verify_status: verified — worktree Read ADR-125 "Amendment 2 (2026-06-19) — CFP-2350 — runtime-failure 변종 신설". ADR-125 본문 0건 변경 (Amendment 2 §4 enforcement = review-verdict-v4 enum 을 Phase 2 별 carrier defer 로 명시 — 본 PS1 = 그 Phase 2 carrier)
  - ADR-068  # I-8 standing invariant-surface invariant (Amendment 6 — CFP-2351) SSOT. CFP-2358 v4.13 → v4.14 MINOR bump — findings[].type 13번째 literal "invariant-surface-not-extended" (impl PR 이 새 long-lived mutable structure 추가 + docs/system-invariants.md 미확장 detect) + 8번째 verdict-level optional bool field invariant_surface_extension_self_check_passed carrier. ADR-068 Amendment 6 가 I-8 verdict-level field + finding type literal binding 을 "S4 (#2350) 위임" 으로 명시 defer — 본 PS1 (#2358) = 그 S4 single-owner carrier. verify_status: verified — worktree Read ADR-068 "Amendment 6 — CFP-2351 I-8 standing invariant-surface invariant 신설" + "review-verdict-v4 binding = S4 위임". ADR-068 본문 0건 변경
authors:
  - CFP-137 (2026-05-09) — review-verdict v3 → v4 MAJOR bump (Sonnet decider 영역 정식 제거 + worker_dialog_rounds 추가)
  - CFP-391 (2026-05-11) — findings[].anchor_id optional field 추가 (debate-protocol-v1 stable identifier SSOT 정합, FIX-1)
  - CFP-391 (2026-05-11) — v4.0 → v4.1 MINOR bump (anchor_id field 추가 = ADR-008 §결정 2 "새 선택 필드 추가" MINOR bump 정합, F-003 follow-up)
  - CFP-438 (2026-05-13) — v4.1 → v4.2 MINOR bump (mechanical_self_check_passed optional bool field 추가, ADR-065)
  - CFP-527 (2026-05-13) — v4.2 → v4.3 MINOR bump (boundary_completeness_self_check_passed optional bool field + findings[].type "boundary-completeness" literal 추가, ADR-068)
  - CFP-528 (2026-05-13) — v4.3 → v4.4 MINOR bump (dimensional_empirical_self_check_passed optional bool field + findings[].type "dimensional-empirical-gap" literal, ADR-068 Amendment 1)
  - CFP-597 (2026-05-13) — v4.4 → v4.5 MINOR bump (marketplace_sync_declared optional bool field, ADR-063 Amendment 1)
  - CFP-1086 (2026-05-20) — v4.5 → v4.6 MINOR bump (deputy_axis_restructure_self_check_passed optional bool field 신설 — ADR-042 Amendment 8 + ADR-086 P7 framework self-application 첫 사례 carrier + boundary_completeness_self_check_passed scope expansion — ADR-068 Amendment 2 wording SSOT chief tie-break ladder cross-ref)
  - CFP-1087 (2026-05-20) — v4.6 → v4.7 MINOR bump (audit_gate_pointer_self_check_passed 5번째 verdict-level optional bool field 신설 + findings[].type enum 5번째 literal "audit-gate-pointer-missing" — ADR-068 Amendment 3 §결정 1 I-6 audit-gate-pointer-existence invariant carrier, CFP-528 Amendment 1 패턴 verbatim 답습, CFP-1086 cascade sequential precedence 후 collision resolution renumber)
  - CFP-1117 (2026-05-21) — v4.7 → v4.8 MINOR bump (findings[].type enum 에 3 DDD finding type literal 추가 — bc_violation / aggregate_violation / ubiquitous_language_drift. ADR-091 §결정 6 enforcement layer 3-tier 의 3번째 tier (review-verdict-v4 enum) realize + §결정 7 INV-5 vocabulary theater 차단 forcing function 의 review-verdict finding 연결 (evidence #4). CFP-1117 Story-4 carrier (Epic CFP-1117 ArchitectLane DDD vocabulary governance). CFP-528 Amendment 1 (enum literal + 의미 1줄) 패턴 verbatim 답습. additive only backward-compat invariant (기존 v4.7 consumer 가 3 신규 enum literal 무시 가능). ADR-008 §결정 2 "enum literal 추가" MINOR bump 정합 (closed-enum 6 → 9 ratchet, additive only). 5 sibling (requirements/design/develop/test/pmo v4.3) pre-existing drift = 본 S4 scope 외 (별 sweep CFP carrier))
  - CFP-1303 (2026-05-23) — v4.8 → v4.9 MINOR bump (findings[].parallel_anchors_checked optional array field 신설 — CFP-604 retro F7 Wave 2 carrier, Wave 1 CFP-1291 prose-only anchor (CodeReviewPLAgent.md cross-anchor parity check step) 위 schema layer codify. 각 entry = 3 field (file_line string / pattern_type enum 5종 closed-set local_remote · client_server · read_write · forward_reverse · enum_closure / matched bool). LOCAL_AUTHOR ↔ REMOTE_AUTHOR pattern (CFP-604 F-CR-604-2 + parallel REMOTE_AUTHOR site evidence) cross-anchor parity check 영역의 schema-level enforcement carrier. ADR-068 I-2 cross-module propagation completeness 의 review-verdict layer realization. mechanical lint (parallel_anchors_checked field presence-grep heuristic) = Wave 3 별 carrier (deferred-followup). CFP-391 (anchor_id) pattern 답습 — findings[] entry 안 optional field 추가. additive only backward-compat invariant (기존 v4.8 consumer 가 본 신규 field 무시 가능). ADR-008 §결정 2 "새 선택 필드 추가" MINOR bump 정합)
  - CFP-1424 (2026-05-24) — v4.9 → v4.10 MINOR bump (findings[].type enum 에 "confluence-mirror-link-missing" 9번째 literal 추가 — ADR-111 §결정 5 cross-link discipline 정합 (Confluence mirror 대상 doc Issue body inline 시 Confluence anchor link presence verify finding). DesignReviewPL check item 추가 동반 (sibling cross-repo PR codeforge-review/agents/DesignReviewPLAgent.md). ADR-008 §결정 2 'enum literal 추가' MINOR bump 정합 (closed-enum 8 → 9 ratchet, additive only). 5 sibling (requirements/design/develop/test/pmo v4.3) pre-existing drift = 본 Sub-A S1.4 scope 외. CFP-528 Amendment 1 pattern verbatim 답습. Mega-Epic CFP-1415 Sub-A S1.4 wrapper-side carrier — AC-1 (CLAUDE.md ADR-111 cross-ref) + AC-3 (본 MINOR bump) + AC-4 (claude-md-line-cap PASS) wrapper-side bundle)
  - CFP-1565 (2026-06-01) — v4.11 → v4.12 MINOR bump (7번째 verdict-level optional bool field chief_author_crossref_consistency_self_check_passed 신설 + findings[].type enum 11번째 literal "chief-author-crossref-inconsistency" 추가 — ADR-068 Amendment 5 §결정 1 I-7 chief-author cross-ADR scope/fact claim consistency invariant carrier. chief author 가 §3/§7/§10/§11 작성 시 다른 ADR 의 SSOT 값 (scope list / count / enum / 권한 범위) 인용·단언 시 대상 ADR direct Read-verify 후 cross-adr-claim-verify-annotation 3-key (cited_adr+§결정 / cited_value / verify_status) 보유 + verify_status=verified (또는 Justification 면제) 시 true. false 시 ArchitectAgent re-spawn (FIX 의무) + findings[].type "chief-author-crossref-inconsistency" 동반 emit. mechanical_self_check_passed (ADR-065) + boundary_completeness_self_check_passed (ADR-068 I-1~I-4) + dimensional_empirical_self_check_passed (Amendment 1 I-5) + marketplace_sync_declared (ADR-063 Amendment 1) + audit_gate_pointer_self_check_passed (Amendment 3 I-6) + deputy_axis_restructure_self_check_passed (Amendment 2 conditional CFP-1086) + living_architecture_updated_self_check_passed (ADR-112) 와 disjoint — 동일 verdict packet 7번째 별도 boolean field. I-4 wording SSOT (identifier 표기) 와 disjoint axis (I-7 = cross-ADR factual/scope 값 SSOT 정합). DesignReviewPL + CodeReviewPL dual cross-validate. ADR-008 §결정 2 '새 선택 필드 추가' + 'enum literal 추가' MINOR bump 정합 (closed-enum 10 → 11 ratchet, additive only). Runtime impact 없음 (기존 v4.11 consumer 가 본 7번째 field + 11번째 literal 무시 가능 = backward-compat invariant). CFP-1426 v4.11 (verdict-level bool field + findings type literal) pattern verbatim 답습. CFP-1522 retro F-003 P1 evidence (ADR-113 §결정 6 admin:repo scope claim ↔ ADR-066 §결정 2 6-scope SSOT mismatch). Wave 1 declaration-only (mechanical wire = 별 sub-CFP carrier). 6 sibling (requirements/design/develop/test/pmo/wrapper) pre-existing drift = 본 scope 외 (cross-repo sibling sync PR codeforge-review canonical + 별 sweep CFP carrier).)
  - CFP-1426 (2026-05-24) — v4.10 → v4.11 MINOR bump (6번째 verdict-level optional bool field living_architecture_updated_self_check_passed 신설 + findings[].type enum 10번째 literal "living-architecture-not-updated" 추가 — ADR-112 Living Architecture per-Epic mandatory update gate carrier. ArchitectAgent Epic close 직전 5-anchor section (arc42 §3 Context & Scope + arc42 §5 Building Block View + C4 Container + C4 Component + Open Decisions Pending) 최소 1개 update OR `[living-arch-no-impact: <rationale>]` explicit declare 통과 시 true. DesignReviewPL false + no-op declare 부재 detect 시 "living-architecture-not-updated" finding emit (severity P1, design lane only — CodeReviewPL 영역 외 governance write-time anchor). mechanical_self_check_passed (ADR-065 syntactic 7-item) + boundary_completeness_self_check_passed (ADR-068 I-1~I-4) + dimensional_empirical_self_check_passed (Amendment 1 I-5) + marketplace_sync_declared (ADR-063 Amendment 1) + audit_gate_pointer_self_check_passed (Amendment 3 I-6) + deputy_axis_restructure_self_check_passed (Amendment 2 conditional CFP-1086) 와 disjoint — 동일 verdict packet 6번째 별도 boolean field (Living Architecture governance write-time invariant). ADR-008 §결정 2 '새 선택 필드 추가' MINOR bump 정합 + 'enum literal 추가' MINOR bump 정합 (closed-enum 9 → 10 ratchet, additive only). Runtime impact 없음 (기존 v4.10 consumer 가 본 6번째 field + 10번째 literal 무시 가능 = backward-compat invariant). CFP-1424 v4.9 → v4.10 (enum literal 추가) + CFP-1086/1087 cascade (verdict-level bool field 신설) pattern verbatim 답습. Mega-Epic CFP-1415 Sub-C S3.2 wrapper-side carrier — AC-3 (본 MINOR bump). sibling Story #1425 (S3.1) = ADR-078 Amendment 2 5-anchor section closed-set codify base. mechanical wire = Sub-C S3.5 / CFP-1429 carrier scripts/check-living-architecture-update.sh + templates/github-workflows/living-architecture-update.yml + label-registry-v2 family member `hotfix-bypass:living-architecture-update`. 5 sibling (requirements/design/develop/test/pmo v4.3) pre-existing drift = 본 S3.2 scope 외.)
  - CFP-2358 (2026-06-19) — v4.13 → v4.14 MINOR bump (findings[].type enum 에 2 literal 추가 — "invariant-violation" 12번째 (runtime-failure falsification 에서 file:line 으로 짚힌 위반 invariant — ADR-064 §결정 13 재진입 규율 3 비대칭 결정규칙의 verdict-level finding) + "invariant-surface-not-extended" 13번째 (ADR-068 I-8 Amendment 6 — impl PR 이 새 long-lived mutable structure 추가 + docs/system-invariants.md 미확장) (closed-enum 11 → 13 additive). + 8번째 verdict-level optional bool field invariant_surface_extension_self_check_passed 신설 (ADR-068 I-8 Amendment 6 — CFP-2351 declare → S4 #2350 위임분, 본 CFP-2358 Phase 2 carrier — 기존 7 field 와 disjoint). + runtime-failure 변종 falsification 비대칭 규칙 본문 명시 (요구사항리뷰 internal-invariant 변종, ADR-125 Amendment 2 — file:line invariant-violation finding 1개 > N attestation, Popper). lane enum 무변경 (requirements-review 재사용). ADR-064 §결정 13 Amendment 결정 2 + ADR-125 Amendment 2 §4 + ADR-068 Amendment 6 가 review-verdict-v4 binding 을 Phase 2 별 carrier ("S4 #2350 위임") 로 defer — 본 PS1 (#2358) = 그 Phase 2 single-owner carrier. CFP-1565 (verdict-level bool field + findings type literal 동시 신설) pattern verbatim 답습. ADR-008 §결정 2 'enum literal 추가' + '새 선택 필드 추가' MINOR bump 정합. additive only backward-compat invariant (기존 v4.13 consumer 가 2 신규 literal + 8번째 field 무시 가능).)
  - CFP-2471 (2026-06-30) — v4.14 → v4.15 MINOR bump (peer_degrade verdict-level optional object 신설 — dual-peer 2→1 honest degrade marker, ADR-044 Amendment 4 §결정 10 / Epic CFP-2468 Track W (W3). 3-key block: peer_count (int) + degrade_reason (string) + degrade_acknowledged (bool). 검증 floor = ≥1 independent peer (SoD) — Codex = floor 아닌 ceiling. silent 2→1 degrade 차단 (degrade_acknowledged 부재 = silent harm, ADR-094 (a) 거부 / honest degrade = (c) 동형). check-verification-floor.sh 가 축①(self-audit peer_count 0 verdict 무효) + 축②(silent degrade 차단) mechanical 검출. enforcement(PreToolUse Agent matcher deny)는 미구현 (matcher P2 empirical 미확정 — empirical-source TBD 보류). ADR-008 §결정 2 '새 선택 필드 추가' MINOR bump 정합. additive only backward-compat invariant (기존 v4.14 consumer 가 block 부재 = degrade 없음으로 해석). 적용 lane = 전 review lane. canonical 단일 원본 (ADR-118 D5) + MANIFEST mirror.)
  - CFP-2326 (2026-06-17) — v4.12 → v4.13 MINOR bump (lane enum 에 "requirements-review" 4번째 literal 추가 — CFP-2326 / ADR-125 결정 5, 9번째 lane 신설. 리뷰 lane 식별자 (작성 lane requirements 아님 — 본 lane 은 요구사항 외부사실 의존성 검증 producer, ADR-125 결정 4 disjoint axis). RequirementsReviewPLAgent = ADR-001 lane-agnostic base 재사용 (신규 worker 신설 0). ClaudeReviewAgent / CodexReviewAgent lane-conditional hard-check 에 requirements-review branch 추가. review-pl-base.md §2 lane enum + 매트릭스 + §5.5 Lane→gate 매핑 row 동반. ADR-008 §결정 2 'enum literal 추가' MINOR bump 정합 (lane enum 3 → 4, additive only). Runtime impact 없음 (기존 v4.12 consumer 가 신규 lane 값 무시 가능 = backward-compat invariant).)
amendment_log:
  - version: "4.15"
    date: 2026-06-30
    cfp: CFP-2471
    type: MINOR
    summary: "peer_degrade verdict-level optional object 신설 (dual-peer 2→1 honest degrade marker) — ADR-044 Amendment 4 §결정 10 / Epic CFP-2468 Track W (W3) lane verification floor. 검증 floor = ≥1 independent peer (SoD: implementer≠certifier). Codex (2nd peer) = floor 아닌 ceiling (cross-model diversity) — 미가용 시 single-peer honest degrade 가 정식 floor 충족 (진입 불가 아님). 3-key block: (1) peer_count (int) — 실제 발화 independent peer 수 (0 = self-audit floor 위반 verdict 무효 / 1 = single-peer degrade / 2 = dual-peer 정상). (2) degrade_reason (string) — degrade 사유 audit trail (ADR-094 (c) 사유 강제 기록, secret 미포함 의무 ADR-044 §결정7). (3) degrade_acknowledged (bool) — honest marker (true + peer_count:1 + degrade_reason = honest degrade 통과 / peer_count:1 인데 field 부재 = silent degrade 차단, ADR-094 (a) silent harm 거부). 차단 logic = check-verification-floor.sh (Phase 2 carrier): 축① peer_count:0 self-audit verdict + pl_recommendation:PASS → 무효·차단 / 축② peer_count:1 ∧ degrade_acknowledged 부재 (silent) → 차단. 적용 lane: 전 review lane (design/code/security/requirements-review). 기존 8 verdict-level bool field (mechanical_self_check_passed ~ invariant_surface_extension_self_check_passed) + worker_dialog_rounds (int) 와 disjoint — verdict-level object field (3-key) 신설. enforcement(PreToolUse Agent matcher deny)는 본 Story 미구현 (matcher P2 정확 토큰·CLI 런타임 발동 empirical 미확정 — [empirical-source: TBD], 설계 §결정10d 보류). 관측 baseline (check-verification-floor + check-lane-evidence 축③ + SubagentStart 관측)만 구현. ADR-008 §결정 2 '새 선택 필드 추가' MINOR bump 정합 (verdict-level field 추가 — backward-compat invariant, 기존 v4.14 consumer 가 block 부재 = degrade 없음으로 해석). branch protection 6-tuple 무변경 (warning-tier, ADR-128 상속). canonical 단일 원본 (ADR-118 D5, sibling sync 폐지) + MANIFEST.yaml review_verdict version mirror 동반. plugin.json 6.50.0 → 6.53.0 MINOR (review governance) + marketplace sync."
  - version: "4.14"
    date: 2026-06-19
    cfp: CFP-2358
    type: MINOR
    summary: "findings[].type enum 에 2 literal 추가 (closed-enum 11 → 13 additive) + 8번째 verdict-level optional bool field invariant_surface_extension_self_check_passed 신설 + runtime-failure 변종 falsification 비대칭 규칙 본문 명시 — Epic #2357 Phase 2 진단축 wrapper wire. (1) \"invariant-violation\" 12번째 literal — runtime-failure lane (요구사항리뷰 internal-invariant 변종, ADR-125 Amendment 2) falsification 에서 file:line 으로 짚힌 위반 invariant. ADR-064 §결정 13 재진입 규율 3 (비대칭 결정규칙 — file:line invariant 1개 > 'OK' N개) 의 verdict-level finding realization. (2) \"invariant-surface-not-extended\" 13번째 literal — ADR-068 I-8 Amendment 6: impl PR 이 새 long-lived mutable structure 추가 (또는 기존 구조 bound/lifetime/ordering invariant 변경) 하고 docs/system-invariants.md 색인 row 미확장 detect. (3) invariant_surface_extension_self_check_passed 8번째 verdict-level optional bool field — ADR-068 I-8 Amendment 6 (CFP-2351 declare → S4 #2350 위임분, 본 CFP-2358 Phase 2 carrier). mechanical_self_check_passed (ADR-065) + boundary_completeness_self_check_passed (ADR-068 I-1~I-4) + dimensional_empirical_self_check_passed (Amendment 1 I-5) + marketplace_sync_declared (ADR-063 Amendment 1) + audit_gate_pointer_self_check_passed (Amendment 3 I-6) + deputy_axis_restructure_self_check_passed (Amendment 2 conditional) + living_architecture_updated_self_check_passed (ADR-112) + chief_author_crossref_consistency_self_check_passed (Amendment 5 I-7) 와 disjoint — 동일 verdict packet 8번째 별도 boolean field. (4) runtime-failure 변종 verdict 비대칭 규칙 (§18) — file:line invariant-violation finding 1개가 N개 'verified OK' attestation 을 이긴다 (Popper). lane enum 무변경 (requirements-review 재사용 — runtime-failure 변종은 internal-invariant 축, ADR-125 Amendment 2). ADR-064 §결정 13 Amendment 결정 2 + ADR-125 Amendment 2 §4 + ADR-068 Amendment 6 review-verdict-v4 binding 이 Phase 2 별 carrier ('S4 #2350 위임') 로 defer 한 mechanical wire 의 carrier — 본 PS1 (#2358) = 그 single-owner. CFP-1565 (verdict-level bool field + findings type literal 동시 신설) pattern verbatim 답습. ADR-008 §결정 2 'enum literal 추가' + '새 선택 필드 추가' MINOR bump 정합 (closed-enum 11 → 13 ratchet, verdict-level bool 7 → 8). Runtime impact 없음 (기존 v4.13 consumer 가 2 신규 literal + 8번째 field 무시 가능 = backward-compat invariant). RequirementsReviewPLAgent / ClaudeReviewAgent / CodexReviewAgent runtime-failure branch 배선 = Epic #2357 Phase 2 checklist carrier (별 Story)."
  - version: "4.13"
    date: 2026-06-17
    cfp: CFP-2326
    type: MINOR
    summary: "lane enum 에 \"requirements-review\" 4번째 literal 추가 — CFP-2326 / ADR-125 결정 5, 9번째 lane (요구사항리뷰) 신설. 리뷰 lane 식별자 (작성 lane requirements 아님 — 본 lane 은 요구사항 결론 외부사실 의존성 검증 producer 게이트, ADR-125 결정 4 disjoint axis: 작성측 ADR-052 touchpoint #4 self-check (단계②) ↔ 리뷰측 producer 게이트 (단계③)). RequirementsReviewPLAgent = ADR-001 lane-agnostic review subsystem 재사용 (신규 worker 신설 0, base 재사용). ClaudeReviewAgent / CodexReviewAgent lane-conditional hard-check 에 requirements-review branch 추가 (story_key 필수 + 요구사항 산출물 Read 가능). review-pl-base.md §2 lane enum + lane 매트릭스 requirements-review 열 + §5.5 Lane→gate 매핑 row (requirements-review PASS → gate:requirements-review-pass + phase:요구사항-리뷰 → phase:설계) 동반. ADR-008 §결정 2 'enum literal 추가' MINOR bump 정합 (lane enum 3 → 4, additive only). Runtime impact 없음 (기존 v4.12 consumer 가 신규 lane 값 무시 가능 = backward-compat invariant). worker verdict 변환표 (review-pl-base §3) 는 lane-agnostic 이므로 무변경."
  - version: "4.12"
    date: 2026-06-01
    cfp: CFP-1565
    type: MINOR
    summary: "chief_author_crossref_consistency_self_check_passed 7번째 verdict-level optional bool field 신설 + findings[].type enum 11번째 literal \"chief-author-crossref-inconsistency\" — ADR-068 Amendment 5 §결정 1 I-7 chief-author cross-ADR scope/fact claim consistency invariant carrier. chief author 가 §3/§7/§10/§11 작성 시 다른 ADR 의 SSOT 값 (scope list / count / enum / 권한 범위) 인용·단언 시 대상 ADR direct Read-verify 후 cross-adr-claim-verify-annotation 3-key (cited_adr+§결정 / cited_value / verify_status) 보유 + verify_status=verified (또는 Justification 면제 out-of-scope) 시 true. false 시 ArchitectAgent re-spawn (FIX 의무) + findings[].type \"chief-author-crossref-inconsistency\" 동반 emit (severity P1). mechanical_self_check_passed (ADR-065 syntactic) + boundary_completeness_self_check_passed (ADR-068 I-1~I-4) + dimensional_empirical_self_check_passed (Amendment 1 I-5) + marketplace_sync_declared (ADR-063 Amendment 1) + audit_gate_pointer_self_check_passed (Amendment 3 I-6) + deputy_axis_restructure_self_check_passed (Amendment 2 conditional CFP-1086) + living_architecture_updated_self_check_passed (ADR-112) 와 disjoint — 동일 verdict packet 7번째 별도 boolean field. I-4 wording SSOT (identifier 표기 동기화) 와 disjoint axis (I-7 = cross-ADR factual/scope 값 SSOT 정합). DesignReviewPL + CodeReviewPL dual cross-validate. ADR-008 §결정 2 '새 선택 필드 추가' + 'enum literal 추가' MINOR bump 정합 (closed-enum 10 → 11 ratchet, additive only). Runtime impact 없음 (기존 v4.11 consumer 가 본 7번째 field + 11번째 literal 무시 가능 = backward-compat invariant). CFP-1426 v4.11 (verdict-level bool field + findings type literal 동시 신설) pattern verbatim 답습. CFP-1522 retro F-003 P1 evidence (ADR-113 §결정 6 admin:repo scope claim ↔ ADR-066 §결정 2 6-scope SSOT mismatch). Wave 1 declaration-only (mechanical wire = 별 sub-CFP carrier). DesignReviewPLAgent.md / CodeReviewPLAgent.md / review-pl-base.md I-7 check item 추가 동반 (sibling cross-repo PR codeforge-review canonical)."
  - version: "4.11"
    date: 2026-05-24
    cfp: CFP-1426
    type: MINOR
    summary: "living_architecture_updated_self_check_passed 6번째 verdict-level optional bool field 신설 + findings[].type enum 10번째 literal \"living-architecture-not-updated\" — ADR-112 Living Architecture per-Epic mandatory update gate carrier. ArchitectAgent Epic close 직전 5-anchor section (arc42 §3+§5 + C4 Container+Component + Open Decisions Pending) 최소 1개 update 통과 시 true, 또는 `[living-arch-no-impact: <rationale>]` explicit declare 시 true. DesignReviewPL false + no-op declare 부재 detect 시 \"living-architecture-not-updated\" finding emit. mechanical_self_check_passed (ADR-065 syntactic) + boundary_completeness_self_check_passed (ADR-068 I-1~I-4) + dimensional_empirical_self_check_passed (Amendment 1 I-5) + audit_gate_pointer_self_check_passed (Amendment 3 I-6) + deputy_axis_restructure_self_check_passed (Amendment 2) 와 disjoint — 동일 verdict packet 6번째 별도 boolean field (Living Architecture governance write-time invariant). ADR-008 §결정 2 '새 선택 필드 추가' MINOR bump 정합 + 'enum literal 추가' MINOR bump 정합 (closed-enum 9 → 10 ratchet, additive only). Runtime impact 없음 (기존 v4.10 consumer 가 본 6번째 field + 10번째 literal 무시 가능 = backward-compat invariant). CFP-1424 Amendment v4.10 (confluence-mirror-link-missing 9번째 literal) pattern verbatim 답습. CFP-1086/1087 cascade (verdict-level bool field 신설 pattern) 답습. mechanical wire = Sub-C S3.5 / CFP-1429 carrier."
  - version: "4.10"
    date: 2026-05-24
    cfp: CFP-1424
    type: MINOR
    summary: "findings[].type enum 에 \"confluence-mirror-link-missing\" literal 추가 — ADR-111 §결정 5 cross-link discipline 정합 (Confluence mirror 대상 doc Issue body inline 시 Confluence anchor link presence verify). DesignReviewPL check item 추가 동반 (sibling PR codeforge-review/agents/DesignReviewPLAgent.md). ADR-008 §결정 2 'enum literal 추가' MINOR bump 정합 (closed-enum 8 → 9 ratchet, additive only). 5 sibling (requirements/design/develop/test/pmo v4.3) pre-existing drift = 본 S1.4 scope 외. CFP-528 Amendment 1 pattern verbatim 답습."
  - version: "4.9"
    date: 2026-05-23
    cfp: CFP-1303
    type: MINOR
    summary: "findings[].parallel_anchors_checked optional array field 신설 — CFP-604 retro F7 Wave 2 carrier. Wave 1 CFP-1291 (codeforge-review #42 MERGED 2026-05-23 09:23 KST, CodeReviewPLAgent.md cross-anchor parity check step 본문 + finding inline marker prose) 위 schema layer codify. 각 entry = 3 field — file_line (string, path-line 형식) + pattern_type (enum 5종 closed-set, local_remote · client_server · read_write · forward_reverse · enum_closure) + matched (bool). pattern_type 5종 = 가장 빈번한 parallel-anchor 패턴 enumeration — local_remote (LOCAL_X ↔ REMOTE_X), client_server (client↔server symmetric), read_write (read↔write 짝), forward_reverse (forward↔reverse 짝), enum_closure (enum value 전수 coverage). 트리거 evidence = CFP-604 F-CR-604-2 (LOCAL_AUTHOR jq fallback unreachable, line 76) + 후속 FIX iter 2 적용 후 CI 에서 동일 root cause 의 parallel site (REMOTE_AUTHOR jq parsing line 213) 추가 발견 — CodeReviewPL anchor coverage gap pattern_count 2 evidence. ADR-068 I-2 cross-module propagation completeness 의 review-verdict layer realization (semantic anchor — propagation matrix 의 micro-scale parallel form). mechanical lint (parallel_anchors_checked field presence-grep heuristic on finding emit) = Wave 3 별 carrier (deferred-followup, ADR-064 §결정 1 scope unitary). CFP-391 (anchor_id) pattern 답습 — findings[] entry 안 optional field 추가 (verdict-level boolean field 신설 0건 — Codex worker counter-arg 영역 disjoint axis). mechanical_self_check_passed (ADR-065 syntactic 7-item) + boundary_completeness_self_check_passed (ADR-068 I-1~I-4) + dimensional_empirical_self_check_passed (Amendment 1 I-5) + audit_gate_pointer_self_check_passed (Amendment 3 I-6) + deputy_axis_restructure_self_check_passed (Amendment 2 sibling CFP-1086) 5 verdict-level boolean field 와 disjoint — parallel_anchors_checked 는 findings[] entry array 안 optional field 확장 (verdict-level boolean 신설 0건). ADR-008 §결정 2 '새 선택 필드 추가' MINOR bump 정합. Runtime impact 없음 (기존 v4.8 consumer 가 본 신규 field 무시 가능 = backward-compat invariant). CFP-1117-S4 v4.7 → v4.8 sibling sync precedent 답습 (wrapper sibling + 본 canonical atomic, 5 other lane plugin sweep = 별 follow-up CFP carrier — CFP-1167 precedent)."
  - version: "4.8"
    date: 2026-05-21
    cfp: CFP-1117
    type: MINOR
    summary: "findings[].type enum 에 3 DDD finding type literal 추가 — bc_violation / aggregate_violation / ubiquitous_language_drift. ADR-091 §결정 6 enforcement layer 3-tier 의 3번째 tier (review-verdict-v4 enum S4) realize + §결정 7 INV-5 vocabulary theater 차단 forcing function 의 review-verdict finding 연결 (evidence #4: 'bc_violation / aggregate_violation / ubiquitous_language_drift finding type 신설 + 실 emit 사례'). bc_violation = Bounded Context 위반 (cross-BC 참조 ACL/OHS 패턴 부재 / BC boundary 침범 / 동음이의 미qualifier) — Change Plan §3.D bounded_context_boundary forcing function 연결, DesignReviewPL + CodeReviewPL emit. aggregate_violation = Aggregate 위반 (consistency boundary 침범 / transaction boundary 부정합 / invariant 미보존 / aggregate root 외부 직접 access) — Change Plan §3.A affected_aggregates forcing function 연결, ADR-091 §결정 3 Layer B real Aggregate cross-validate, ModuleArchitectAgent (boundary axis unified, ADR-042 Amendment 10) 영역. ubiquitous_language_drift = Ubiquitous Language drift (glossary SSOT 외 미정의 DDD term 사용 / 동음이의 미구분 / anti-pattern 어휘) — check-ubiquitous-language lint 연결 (ADR-091 Amendment 2 §결정 6 2번째 tier), 14 agent ddd_pattern + glossary SSOT 기준. mechanical_self_check_passed (ADR-065 syntactic 7-item) + boundary_completeness_self_check_passed (ADR-068 I-1~I-4) + dimensional_empirical_self_check_passed (Amendment 1 I-5) + audit_gate_pointer_self_check_passed (Amendment 3 I-6) + deputy_axis_restructure_self_check_passed (Amendment 2 sibling CFP-1086) verdict-level boolean field 와 disjoint axis — DDD finding type 은 findings[].type enum literal 확장 (verdict-level boolean field 신설 0건). ADR-008 §결정 2 'enum literal 추가' MINOR bump 정합 (findings[].type closed-enum additive — 기존 boundary-completeness / mechanical_sync_required / dimensional-empirical-gap / audit-gate-pointer-missing / general 위에 3 literal 추가). Runtime impact 없음 (기존 v4.7 consumer 가 본 3 신규 enum literal 무시 가능 = backward-compat invariant). CFP-528 Amendment 1 (I-5 dimensional-empirical-gap literal + 의미 1줄) pattern verbatim 답습. 5 sibling (requirements/design/develop/test/pmo v4.3) pre-existing drift = 본 S4 scope 외 (별 sweep CFP carrier note)."
  - version: "4.7"
    date: 2026-05-20
    cfp: CFP-1087
    type: MINOR
    summary: "audit_gate_pointer_self_check_passed 5번째 verdict-level optional bool field 신설 + findings[].type enum 5번째 literal \"audit-gate-pointer-missing\" — ADR-068 Amendment 3 §결정 1 I-6 audit-gate-pointer-existence invariant carrier. ArchitectAgent §3 작성 시 §8.6 audit gate finding 영역 4-form pointer scope (link target / section anchor / file path reference / ADR §결정 N reference) existence verify 통과 시 true. false 시 ArchitectAgent re-spawn (FIX 의무) + findings[].type \"audit-gate-pointer-missing\" 동반 emit. mechanical_self_check_passed (ADR-065) + boundary_completeness_self_check_passed (ADR-068 I-1~I-4) + dimensional_empirical_self_check_passed (Amendment 1 I-5) + deputy_axis_restructure_self_check_passed (Amendment 2 sibling CFP-1086, conditional scope) 와 disjoint — 동일 verdict packet 다섯 별도 boolean field. ADR-008 §결정 2 '새 선택 필드 추가' MINOR bump 정합 + 'enum literal 추가' MINOR bump 정합 (closed-enum 5 → 6 ratchet, additive only). Runtime impact 없음 (기존 v4.6 consumer 가 본 신규 field + 신규 enum literal 무시 가능 = backward-compat invariant). CFP-528 Amendment 1 pattern verbatim 답습. CFP-1086 cascade (S1 5.96.0 + v4.6 + Amendment 2 + S3 5.97.0 + S4 5.98.0) sequential precedence 후 collision resolution renumber (main 영역 Amendment 2 점유 → 본 carrier Amendment 3 renumber + v4.7 + 5.99.0)."
  - version: "4.6"
    date: 2026-05-20
    cfp: CFP-1086
    type: MINOR
    summary: "deputy_axis_restructure_self_check_passed optional bool field 신설 — ADR-042 Amendment 8 (BackendArchEpic CFP-1086 Story-1 — design lane 5+3 → 7+3+1 roster 재편: AggregateArchitect 신설 + APIContractArchitect 신설 + ModuleArchitect rename + DataArchitect mandate 축소 + AggregateArch CONDITIONAL applicability P2) + ADR-086 (신설 Deputy 신설 결정 framework P7 — axis 분석 + 5-checklist self-application + deferred carrier path) carrier. ArchitectAgent (또는 후속 Amendment carrier) 가 ADR-086 §결정 2 5-checklist (axis disjoint / cost-token budget / consumer carrier / sibling Epic align / deferred trigger 명시) 통과 시 true. false 시 ArchitectAgent re-spawn (FIX 의무). 적용 lane: design lane only (deputy roster 변경 carrier Story 만 적용, code/security/test lane omit 가능). + boundary_completeness_self_check_passed scope expansion — ADR-068 Amendment 2 (CFP-1086 Story-1 sibling carrier — wording SSOT 충돌 시 chief tie-break ladder 3 단계: RACI lookup → ADR-068 invariant → chief judgement + ADR Amendment 발의). 본 ladder 3단계 모두 통과 시 true (기존 4 invariants I-1~I-4 + Amendment 2 mechanism boost). ADR-008 §결정 2 '새 선택 필드 추가' MINOR bump 정합 + scope expansion (boundary field semantic 확장 — 4 invariants 자체 의미 변경 0건). Runtime impact 없음 (기존 v4.5 consumer 가 본 신규 field 무시 가능 + boundary_completeness_self_check_passed 기존 field semantic backward-compat)."
  - version: "4.5"
    date: 2026-05-13
    cfp: CFP-597
    type: MINOR
    summary: "marketplace_sync_declared optional bool field 추가 — ADR-063 Amendment 1 §결정 9 ArchitectAgent Phase 1 marketplace sync proactive self-check 결과 explicit marker. true = Change Plan §13 안 marketplace_sync_required: true declare 완료 / false = declare 누락 또는 NA (marketplace 영역 변경 0건) / null/omit = v4.4 이전 consumer backward-compat. 적용 lane: design lane only (code/security lane omit 가능). ADR-008 §결정 2 '새 선택 필드 추가' = MINOR bump 정합. Runtime impact 없음 (기존 v4.4 consumer 가 본 필드 무시 가능)."
  - version: "4.4"
    date: 2026-05-13
    cfp: CFP-528
    type: MINOR
    summary: "dimensional_empirical_self_check_passed optional bool field 추가 + findings[].type enum 에 \"dimensional-empirical-gap\" literal 신설 — ADR-068 Amendment 1 §결정 1 I-5 dimensional empirical grounding invariant carrier. ArchitectAgent 가 §3/§7 작성 시 10 dimension enum (latency/scale/cardinality/throughput/cost/accuracy/lifecycle/volume/rate/count) 의 모든 quantitative parameter 가 `[empirical-source: <ref> | TBD]` annotation 보유 시 true. mechanical_self_check_passed (ADR-065 syntactic) + boundary_completeness_self_check_passed (ADR-068 I-1~I-4) 와 disjoint — 동일 verdict packet 셋 별도 boolean field. ADR-008 §결정 2 정합. Runtime impact 없음 (기존 v4.3 consumer 가 본 필드 무시 가능)."
  - version: "4.3"
    date: 2026-05-13
    cfp: CFP-527
    type: MINOR
    summary: "boundary_completeness_self_check_passed optional bool field 추가 + findings[].type enum 에 \"boundary-completeness\" literal 신설 — ADR-068 §결정 2 dual-binding self-check 결과 explicit marker. ArchitectAgent 가 §7 작성 시 4 invariants (I-1~I-4) 모두 verification format 통과 시 true. mechanical_self_check_passed (ADR-065 syntactic 7-item) 와 disjoint — 동일 verdict packet 양 별도 boolean field. ADR-008 §결정 2 \"새 선택 필드 추가\" = MINOR bump 정합. Runtime impact 없음 (기존 v4.2 consumer 가 본 필드 무시 가능)."
  - version: "4.2"
    date: 2026-05-13
    cfp: CFP-438
    type: MINOR
    summary: "mechanical_self_check_passed optional bool field 추가 — ADR-065 ArchitectAgent Phase 1 7-item mechanical sync self-check 결과 explicit marker. true = 모두 PASS 또는 NA, false = FIX 의무 (ArchitectAgent re-spawn). 적용 lane: design lane only (code/security lane = optional, omit 가능). ADR-008 §결정 2 \"새 선택 필드 추가\" = MINOR bump 정합. Runtime impact 없음 (기존 v4.1 consumer 가 본 필드 무시 가능)."
  - version: "4.1"
    date: 2026-05-11
    cfp: CFP-391
    type: MINOR
    summary: "findings[].anchor_id optional field 추가 — debate-protocol-v1 stable identifier 의존. ADR-008 §결정 2 \"새 선택 필드 추가\" = MINOR bump 정합. Runtime impact 없음 (ADR-008 §결정 4 v.x compat 룰 정합)."
  - version: "4.0"
    date: 2026-05-09
    cfp: CFP-137
    type: MAJOR
    summary: "v3 → v4 BREAKING — Sonnet decider 영역 (decision_state 8-value enum / sonnet_final_status / decider_decision_ref / write_errors step Sonnet semantics / 5-step Orchestrator algorithm) 정식 제거. PL pl_recommendation 자체가 final verdict. worker_dialog_rounds 추가."
---

# review_verdict v4 — Inter-plugin Contract (CFP-137 / ADR-044)

`codeforge-review` plugin → `codeforge` core (Orchestrator) 단방향 schema. v3와 BREAKING — Sonnet decider 영역 (`decision_state` 8-value enum / `sonnet_final_status` / `decider_decision_ref` / `write_errors` step Sonnet semantics / 5-step Orchestrator algorithm) 정식 제거. PL `pl_recommendation` 자체가 final verdict (PASS / FIX / FIX_DISCRETIONARY / ESCALATE_PACKET_INCOMPLETE).

신규 field `worker_dialog_rounds` 추가 — Adversarial debate (5 권장 패턴 — ADR-044 §결정 5) measurable verification.

**상위 SSOT 위치**: 본 파일이 단일 원본 (canonical) — CFP-2158 / [ADR-118](../../archive/adr/ADR-118-monorepo-consolidation.md) D5 가 lane canonical ↔ wrapper mirror 이중체계를 폐지 (monorepo 통합 S1 후속). frontmatter 의 ADR-010 인용은 historical (sibling sync 정책 Superseded — ADR-010 Amendment 5). versioning 룰 = ADR-008 불변.

## 1. v3 → v4 BREAKING 변경 요약

| 영역 | v3.0 (CFP-61 ~ CFP-134) | v4.0 (CFP-137 부터) |
|---|---|---|
| `decision_state` 8-value enum | `pending_sonnet` / `decided` / `blocked_packet_incomplete` / `decider_timeout` / `decider_suspended` / `review_reopen_requested` / `write_partial` / `write_complete` (NO-OP passthrough since CFP-134) | **제거** (단순화 — PL synthesis → Orchestrator self-write 단일 path) |
| `sonnet_final_status` | NEW (NO-OP passthrough since CFP-134) | **제거** |
| `decider_decision_ref` | NEW (NO-OP passthrough since CFP-134) | **제거** |
| `write_errors[].step` Sonnet semantics | `fix_ledger_append` / `diagnosis_spawn` 의 `decider:claude_sonnet` semantics | step enum 유지하되 Sonnet semantics 제거 — Orchestrator self-write retry only |
| 5-step Orchestrator algorithm | Sonnet 호출 step 3 포함 | **4-step 단순화** (step 3 제거, PL pl_recommendation 직접 적용) |
| `worker_dialog_rounds` | (없음) | **NEW** — Adversarial debate SendMessage round count (ADR-044 §결정 5) |
| `pl_recommendation` final authority | PL advisory + Sonnet final pick override | **PL pl_recommendation 자체가 final verdict** |
| Sonnet override marker (Story §10 FIX Ledger row) | `decider: claude_sonnet, override_marker if pl_recommendation != sonnet_final_status` | **제거** — PL recommendation 단일 source |

## 2. Schema (v4 verbatim)

```yaml
review_verdict:
  contract_version: "4.15"           # current version (MINOR bump series from 4.0 BREAKING)
  lane: design | code | security | requirements-review   # requirements-review: CFP-2326 / ADR-125 결정 5 — 9번째 lane (additive enum 확장, backward-compat). 리뷰 lane 식별자 (작성 lane requirements 아님)
  story_key: <STORY_KEY>
  iteration: <int>
  
  findings:                          # v3 그대로 (배열, severity/category/file/evidence/suggestion) + anchor_id NEW + type NEW (v4.3)
    - severity: P0 | P1 | P2
      category: <packet category_enum 중 하나>
      type: <finding_type_enum>      # NEW v4.3 (optional) — finding 유형 literal
                                     # enum: "general" | "mechanical_sync_required" | "boundary-completeness" | "dimensional-empirical-gap" | "audit-gate-pointer-missing" | "bc_violation" | "aggregate_violation" | "ubiquitous_language_drift" | "confluence-mirror-link-missing" | "living-architecture-not-updated" | "chief-author-crossref-inconsistency" | "invariant-violation" | "invariant-surface-not-extended"
                                     # "boundary-completeness": ADR-068 §결정 2 dual-binding — I-1~I-4 위반
                                     # "mechanical_sync_required": ADR-065 mechanical 7-item 위반 (v4.2)
                                     # "dimensional-empirical-gap": ADR-068 Amendment 1 §결정 1 I-5 위반 — quantitative parameter empirical-source annotation 누락 (v4.4)
                                     # "audit-gate-pointer-missing": ADR-068 Amendment 3 §결정 1 I-6 위반 — §8.6 audit gate finding 4-form pointer scope (link target / section anchor / file path reference / ADR §결정 N reference) existence verify 실패 (v4.7). boundary-completeness 와 disjoint axis (별 verdict field boolean audit_gate_pointer_self_check_passed)
                                     # "bc_violation": ADR-091 §결정 6 3번째 tier — Bounded Context 위반 (cross-BC 참조 ACL/OHS 패턴 부재 / BC boundary 침범 / 동음이의 미qualifier). Change Plan §3.D bounded_context_boundary forcing function 연결. DesignReviewPL + CodeReviewPL emit (v4.8)
                                     # "aggregate_violation": ADR-091 §결정 6 3번째 tier — Aggregate 위반 (consistency boundary 침범 / transaction boundary 부정합 / invariant 미보존 / aggregate root 외부 직접 access). Change Plan §3.A affected_aggregates forcing function 연결 + ADR-091 §결정 3 Layer B real Aggregate cross-validate. ModuleArchitectAgent (boundary axis unified, ADR-042 Amendment 10) 영역 (v4.8)
                                     # "ubiquitous_language_drift": ADR-091 §결정 6 3번째 tier — Ubiquitous Language drift (glossary SSOT 외 미정의 DDD term 사용 / 동음이의 미구분 / anti-pattern 어휘). check-ubiquitous-language lint (ADR-091 Amendment 2 §결정 6 2번째 tier) 연결. 14 agent ddd_pattern + glossary SSOT 기준 (v4.8)
                                     # "confluence-mirror-link-missing": ADR-111 §결정 5 cross-link discipline 위반 — Confluence mirror 대상 doc (closed-enum 4: adr / architecture_doc / change_plan / domain_knowledge) Issue body inline 시 Confluence anchor link presence verify 실패. DesignReviewPL + CodeReviewPL emit (v4.10)
                                     # "living-architecture-not-updated": ADR-112 §결정 4 Living Architecture per-Epic mandatory update gate 위반 — ArchitectAgent self-check living_architecture_updated_self_check_passed=false + no-op explicit declare 부재 (PR description / Change Plan §13 안 `[living-arch-no-impact: <rationale>]` 부재) detect 시 emit. severity P1 (FIX 의무 — ArchitectAgent re-spawn 후 5-anchor 1+ section update 또는 explicit declare 추가). evidence = 5-anchor enumeration (arc42 §3 + arc42 §5 + C4 Container + C4 Component + Open Decisions Pending) + 각 anchor update 부재 ground truth + Change Plan §3 affected_aggregates / §5 affected_modules / §7 affected_interfaces / §8 affected_data_flows 4 영역 변경 sample. scope = design lane only (DesignReviewPL primary emit, CodeReviewPL 영역 외 governance write-time anchor not code-time invariant) (v4.11)
                                     # "chief-author-crossref-inconsistency": ADR-068 Amendment 5 §결정 1 I-7 위반 — chief author 가 §3/§7/§10/§11 작성 시 다른 ADR 의 SSOT 값 (scope list / count / enum / 권한 범위) 인용·단언 시 대상 ADR direct Read-verify 누락 또는 인용 값 ↔ 대상 ADR 실제 SSOT mismatch detect (v4.12). I-4 wording SSOT (identifier 표기) 와 disjoint axis (별 verdict field boolean chief_author_crossref_consistency_self_check_passed). evidence = cross-adr-claim-verify-annotation 3-key (cited_adr+§결정 / cited_value / verify_status) + 대상 ADR direct Read 대조 결과. DesignReviewPL + CodeReviewPL emit
                                     # "invariant-violation": ADR-064 §결정 13 재진입 규율 3 (비대칭 결정규칙) — runtime-failure lane (요구사항리뷰 internal-invariant 변종, ADR-125 Amendment 2) falsification 에서 file:line 으로 짚힌 위반 invariant (증상을 설명하는 bound/lifetime/ordering invariant 위반) (v4.14). evidence = file:line + 위반 invariant 명세 (실패 경로 long-lived mutable 구조의 bound/lifetime/ordering ground-truth). 비대칭 규칙 적용 — 본 finding 1개가 N개 'verified OK' attestation 을 이긴다 (Popper, §18 참조). RequirementsReviewPL primary emit (runtime-failure 변종), DesignReviewPL + CodeReviewPL cross-validate
                                     # "invariant-surface-not-extended": ADR-068 I-8 Amendment 6 위반 — impl PR 이 새 long-lived mutable structure 추가 (또는 기존 구조 bound/lifetime/ordering invariant 변경) 하고 docs/system-invariants.md 색인 row 부재/미갱신 detect (v4.14). 별 verdict field boolean invariant_surface_extension_self_check_passed (CFP-2351 declare → S4 #2350 위임분, 본 CFP-2358 Phase 2 carrier). evidence = 신규/변경 long-lived mutable structure 7-key (name+location / kind / bound / lifetime / ordering / 코드 보존 지점 / accumulation·lifetime-class? Y/N) + docs/system-invariants.md 색인 부재 ground truth. CodeReviewPL primary emit (impl PR), DesignReviewPL cross-validate (Change Plan §3/§5/§11 ↔ standing surface 정합)
                                     # "general": 일반 finding (default, 미제공 시 동일 의미)
      file: <path>
      line: <int>
      evidence: <markdown>
      suggestion: <markdown>
      anchor_id: <string>            # NEW (optional) — finding 의 stable identifier
                                     # 형식: `<file>:<line>` (예: `src/foo.py:42`)
                                     #     또는 `§<section-ref>` (예: `§7.4`)
                                     #     또는 wrapper-defined hash (e.g., sha1(file+line+evidence)[:12])
                                     # 용도: debate-protocol-v1 (ADR-059 §결정 2/4) 이 stable identifier 로 의존
                                     #       — Codex worker counter-arg 가 동일 finding 을 anchor_id 로 reference
                                     # Producer 가 채움 (PL synthesis 시점). 미제공 시 PL 이 hash 로 auto-generate 가능
                                     # 동일 (story_key, lane, iteration) 안에서 unique 권장 (debate cross-ref 정합성)
      parallel_anchors_checked:      # NEW v4.9 (optional, array) — cross-anchor parity check enumeration
                                     # CFP-604 retro F7 Wave 2 carrier (CFP-1303). Wave 1 CFP-1291 prose-only marker
                                     # ("parallel anchors checked: [...]" CodeReviewPLAgent.md 명시) 위 schema codify.
                                     # PL synthesis 가 finding category 별 "parallel anchor enumeration" step 수행 결과
                                     # 를 각 entry 로 채움. 미수집 finding = field absent / null (Wave 3 lint 가 presence-grep
                                     # heuristic 으로 향후 flagging 예정 — deferred-followup).
        - file_line: <string>        # parallel anchor 후보 위치 (예: "src/foo.sh:213")
          pattern_type: <enum>       # closed-set 5종:
                                     #   "local_remote"     — LOCAL_X ↔ REMOTE_X (예: LOCAL_AUTHOR ↔ REMOTE_AUTHOR)
                                     #   "client_server"    — client side ↔ server side symmetric
                                     #   "read_write"       — read path ↔ write path 짝
                                     #   "forward_reverse"  — forward direction ↔ reverse direction 짝
                                     #   "enum_closure"     — enum value 전수 coverage (1+ value 누락 시 미coverage)
          matched: <bool>            # true = parallel anchor 발견 + 동일 root cause class 확인됨
                                     # false = parallel anchor candidate 검색했으나 부재 확인 (clean enumeration)
                                     # 의도: PL 이 "검색했다" vs "단순히 누락" 을 명시 구분 (false = 검색 evidence,
                                     #       field absent = 검색 자체 미수행 — Wave 3 lint heuristic 영역)
                                     # 적용 lane: code review lane (CodeReviewPLAgent 가 primary emit lane —
                                     #   Wave 1 CFP-1291 본문 정합). design review / security test lane optional emit.
  
  pl_recommendation: PASS | FIX | FIX_DISCRETIONARY | ESCALATE_PACKET_INCOMPLETE  # v3 유지, 단 final verdict 책무 단독
  
  mechanical_self_check_passed: <bool>  # NEW v4.2 (optional) — ADR-065 / CFP-438
                                         # ArchitectAgent Phase 1 7-item mechanical sync self-check 결과
                                         # true = 모두 PASS 또는 NA
                                         # false = FIX 의무 (ArchitectAgent re-spawn)
                                         # 적용 lane: design lane only (code/security lane = optional, omit 가능)
                                         # 미제공 시 (v4.1 producer) → Orchestrator 는 무시 (backward-compat)
                                         # 7 항목: label-registry sync / doc-locations regen / workflow self-app /
                                         #         link target Phase 분배 / MANIFEST.yaml 갱신 / section-ownership row /
                                         #         doc-locations row

  boundary_completeness_self_check_passed: <bool>  # NEW v4.3 (optional) — ADR-068 / CFP-527
                                         # ArchitectAgent §7 작성 시 4 semantic invariants (I-1~I-4) self-check 결과
                                         # true = 4 invariants (I-1 API contract semantic completeness /
                                         #        I-2 cross-module propagation completeness /
                                         #        I-3 unconditional vs conditional guard placement intent /
                                         #        I-4 wording SSOT) 모두 verification format 통과
                                         # false = FIX 의무 (ArchitectAgent re-spawn)
                                         # mechanical_self_check_passed (ADR-065 syntactic 7-item) 와 disjoint —
                                         #   동일 verdict packet 양 별도 boolean field
                                         # 적용 lane: design lane only (DesignReview + CodeReview 는 findings[] 로 cross-validate)
                                         # 미제공 시 (v4.2 producer) → Orchestrator 는 무시 (backward-compat)

  dimensional_empirical_self_check_passed: <bool>  # NEW v4.4 (optional) — ADR-068 Amendment 1 / CFP-528
                                         # ArchitectAgent §3/§7 작성 시 I-5 dimensional empirical grounding self-check 결과
                                         # true = 10 dimension enum (latency/scale/cardinality/throughput/cost/
                                         #        accuracy/lifecycle/volume/rate/count) 의 모든 quantitative parameter 가
                                         #        `[empirical-source: <ref>]` 또는 `[empirical-source: TBD]` annotation 보유
                                         # false = 1+ 누락 — FIX 의무 (ArchitectAgent re-spawn)
                                         # mechanical_self_check_passed (ADR-065 syntactic 7-item) +
                                         #   boundary_completeness_self_check_passed (ADR-068 I-1~I-4) 와 disjoint —
                                         #   동일 verdict packet 셋 별도 boolean field
                                         # 적용 lane: design lane only (DesignReview + CodeReview 는 findings[] 로 cross-validate)
                                         # 미제공 시 (v4.3 producer) → Orchestrator 는 무시 (backward-compat)

  marketplace_sync_declared: <bool>     # NEW v4.5 (optional) — ADR-063 Amendment 1 / CFP-597
                                         # ArchitectAgent Phase 1 marketplace sync proactive self-check 결과
                                         # true = Change Plan §13 안 marketplace_sync_required: true declare 완료
                                         #        (mirrored field 변경 감지 + GitOpsAgent §3.6 spawn 예약)
                                         # false = declare 누락 또는 NA (marketplace 영역 변경 0건,
                                         #         Change Plan §13 marketplace_sync_required: false 명시)
                                         # null/omit = v4.4 이전 consumer backward-compat (Orchestrator 무시)
                                         # 적용 lane: design lane only (chief author = ArchitectAgent)
                                         #            code/security lane omit 가능
                                         # 미제공 시 (v4.4 producer) → Orchestrator 는 무시 (backward-compat)
                                         # ADR-063 §결정 9 SSOT (2026-05-13 CFP-597 Amendment 1)

  audit_gate_pointer_self_check_passed: <bool>  # NEW v4.7 (optional) — ADR-068 Amendment 3 / CFP-1087
                                         # ArchitectAgent §3 작성 시 §8.6 audit gate finding 영역 I-6 self-check 결과
                                         # true = 4-form pointer scope (link target / section anchor / file path reference / ADR §결정 N reference) 모두 existence verify PASS
                                         # false = 1+ pointer 부재 — FIX 의무 (ArchitectAgent re-spawn) + findings[].type "audit-gate-pointer-missing" 동반
                                         # mechanical_self_check_passed (ADR-065 syntactic 7-item) +
                                         #   boundary_completeness_self_check_passed (ADR-068 I-1~I-4) +
                                         #   dimensional_empirical_self_check_passed (Amendment 1 I-5) +
                                         #   deputy_axis_restructure_self_check_passed (Amendment 2 sibling CFP-1086, conditional) 와 disjoint —
                                         #   동일 verdict packet 다섯 별도 boolean field
                                         # 적용 lane: design lane only (DesignReview + CodeReview 는 findings[] 로 cross-validate)
                                         # 미제공 시 (v4.6 producer) → Orchestrator 는 무시 (backward-compat)

  living_architecture_updated_self_check_passed: <bool>  # NEW v4.11 (optional) — ADR-112 / CFP-1426
                                         # ArchitectAgent Epic close 직전 Living Architecture per-Epic mandatory update gate self-check 결과
                                         # true = 5-anchor section (arc42 §3 Context & Scope + arc42 §5 Building Block View +
                                         #        C4 Container + C4 Component + Open Decisions Pending) 중 최소 1개 update 통과
                                         #        OR `[living-arch-no-impact: <rationale>]` explicit declare 1+ 형식 충족 (closed-binary)
                                         # false = update 0건 AND no-op declare 부재 — FIX 의무 (ArchitectAgent re-spawn) +
                                         #         findings[].type "living-architecture-not-updated" 동반 emit (severity P1)
                                         # mechanical_self_check_passed (ADR-065 syntactic 7-item) +
                                         #   boundary_completeness_self_check_passed (ADR-068 I-1~I-4) +
                                         #   dimensional_empirical_self_check_passed (Amendment 1 I-5) +
                                         #   marketplace_sync_declared (ADR-063 Amendment 1) +
                                         #   audit_gate_pointer_self_check_passed (Amendment 3 I-6) +
                                         #   deputy_axis_restructure_self_check_passed (Amendment 2 conditional CFP-1086) 와 disjoint —
                                         #   동일 verdict packet 6번째 별도 boolean field (Living Architecture governance write-time invariant)
                                         # 적용 lane: design lane only (DesignReview cross-validate, CodeReview 영역 외 — governance write-time anchor not code-time)
                                         # 미제공 시 (v4.10 이전 producer) → Orchestrator 는 무시 (backward-compat)
                                         # ADR-112 §결정 3 SSOT (2026-05-24 KST, Mega-Epic CFP-1415 Sub-C S3.2)
                                         # sibling Story #1425 (S3.1) = ADR-078 Amendment 2 (5-anchor section closed-set codify)
                                         # mechanical wire = Sub-C S3.5 / CFP-1429 carrier

  chief_author_crossref_consistency_self_check_passed: <bool>  # NEW v4.12 (optional) — ADR-068 Amendment 5 / CFP-1565
                                         # ArchitectAgent §3/§7/§10/§11 작성 시 I-7 chief-author cross-ADR scope/fact claim consistency self-check 결과
                                         # true = 모든 cross-ADR scope/fact claim (다른 ADR 의 scope list / count / enum / 권한 범위 인용)
                                         #        이 cross-adr-claim-verify-annotation 3-key (cited_adr+§결정 / cited_value / verify_status) 보유
                                         #        + verify_status=verified (대상 ADR direct Read 대조 완료) 또는 Justification 면제 out-of-scope
                                         # false = 1+ pending/미검증/mismatch — FIX 의무 (ArchitectAgent re-spawn) +
                                         #         findings[].type "chief-author-crossref-inconsistency" 동반 emit (severity P1)
                                         # mechanical_self_check_passed (ADR-065 syntactic 7-item) +
                                         #   boundary_completeness_self_check_passed (ADR-068 I-1~I-4) +
                                         #   dimensional_empirical_self_check_passed (Amendment 1 I-5) +
                                         #   marketplace_sync_declared (ADR-063 Amendment 1) +
                                         #   audit_gate_pointer_self_check_passed (Amendment 3 I-6) +
                                         #   deputy_axis_restructure_self_check_passed (Amendment 2 conditional CFP-1086) +
                                         #   living_architecture_updated_self_check_passed (ADR-112) 와 disjoint —
                                         #   동일 verdict packet 7번째 별도 boolean field
                                         # I-4 wording SSOT (identifier 표기 동기화) 와 disjoint axis (I-7 = cross-ADR factual/scope 값 SSOT 정합)
                                         # 적용 lane: design lane only (DesignReview + CodeReview 는 findings[] 로 cross-validate)
                                         # 미제공 시 (v4.11 이전 producer) → Orchestrator 는 무시 (backward-compat)
                                         # ADR-068 Amendment 5 §결정 1 SSOT (2026-06-01 KST, CFP-1565)
                                         # CFP-1522 retro F-003 P1 evidence (ADR-113 §결정 6 admin:repo scope ↔ ADR-066 §결정 2 6-scope SSOT mismatch)

  invariant_surface_extension_self_check_passed: <bool>  # NEW v4.14 (optional) — ADR-068 I-8 Amendment 6 / CFP-2358 (CFP-2351 declare → S4 #2350 위임분, 본 CFP-2358 Phase 2 carrier)
                                         # impl PR 이 새 long-lived mutable structure 추가 시 docs/system-invariants.md standing invariant-surface 색인 확장 self-check 결과
                                         # true = 신규/변경 long-lived mutable structure 각각 docs/system-invariants.md 7-key row append/갱신 완료
                                         #        (name+location / kind / bound / lifetime / ordering / 코드 보존 지점 / accumulation·lifetime-class? Y/N)
                                         #        OR 새 long-lived mutable structure 0건 (해당 없음 — runtime 0 governance Story 등, ADR-068 I-8 면제)
                                         # false = 1+ 신규 구조 색인 부재/미갱신 — FIX 의무 +
                                         #         findings[].type "invariant-surface-not-extended" 동반 emit (severity P1)
                                         # mechanical_self_check_passed (ADR-065 syntactic 7-item) +
                                         #   boundary_completeness_self_check_passed (ADR-068 I-1~I-4) +
                                         #   dimensional_empirical_self_check_passed (Amendment 1 I-5) +
                                         #   marketplace_sync_declared (ADR-063 Amendment 1) +
                                         #   audit_gate_pointer_self_check_passed (Amendment 3 I-6) +
                                         #   deputy_axis_restructure_self_check_passed (Amendment 2 conditional CFP-1086) +
                                         #   living_architecture_updated_self_check_passed (ADR-112) +
                                         #   chief_author_crossref_consistency_self_check_passed (Amendment 5 I-7) 와 disjoint —
                                         #   동일 verdict packet 8번째 별도 boolean field (I-8 standing invariant-surface axis)
                                         # 적용 lane: code lane primary (impl PR — CodeReviewPL cross-validate), design lane optional (Change Plan §3/§5/§11 ↔ standing surface 정합)
                                         # 미제공 시 (v4.13 이전 producer) → Orchestrator 는 무시 (backward-compat)
                                         # ADR-068 I-8 Amendment 6 §결정 1 SSOT (2026-06-19 KST, CFP-2351 declare → S4 #2350 위임분 / CFP-2358 review-verdict-v4 binding Phase 2 carrier)

  peer_degrade:                          # NEW v4.15 (optional, object) — ADR-044 Amendment 4 / CFP-2471 (Epic CFP-2468 W3)
                                         # dual-peer 2→1 honest degrade marker. 검증 floor = ≥1 independent peer (SoD: implementer≠certifier).
                                         # Codex (2nd peer) 는 floor 아닌 ceiling (cross-model diversity) — 미가용 시 single-peer honest degrade 가 정식 floor 충족.
                                         # block 부재 = degrade 없음 (정상 2-peer dual-peer 또는 floor 충족 single-peer-by-design).
                                         # block 존재 = single-peer 로 degrade 됨을 PL 이 명시 인지·기록 (honest degrade, ADR-094 (c) degraded+warning 동형).
    peer_count: <int>                    # 실제 발화 independent peer 수 (1 = single-peer degrade, 2 = dual-peer 정상).
                                         #   0 = self-audit (implementer=certifier) — floor 위반, verdict 무효 (축① — check-verification-floor 차단 대상).
    degrade_reason: <string>             # degrade 사유 (audit trail, ADR-094 (c) "사유 강제 기록").
                                         #   예: "Codex CLI 미설치", "Codex user_request_only 미요청 (ad-hoc ceiling 미발동)".
                                         #   secret 미포함 의무 (ADR-044 §결정7 secret hygiene — consumer 책임 영역).
    degrade_acknowledged: <bool>         # honest marker — PL 이 degrade 를 명시 인지·기록 (true) vs silent (field 부재/false).
                                         #   true + peer_count:1 + degrade_reason = honest degrade → floor 충족 (통과).
                                         #   peer_count:1 인데 본 field 부재/false = silent degrade → 차단 (축② — check-verification-floor 차단 대상, ADR-094 (a) silent harm 거부).
                                         # 적용 lane: 전 review lane (design / code / security / requirements-review).
                                         # 미제공 시 (v4.14 이전 producer) → Orchestrator 는 무시 (backward-compat — block 부재 = degrade 없음으로 해석).
                                         # ADR-044 Amendment 4 §결정 10 SSOT (2026-06-30 KST, CFP-2471). floor(≥1 peer) ⊥ ceiling(Codex ad-hoc) disjoint axis.

  worker_dialog_rounds: <int>        # NEW — Adversarial debate SendMessage round count
                                     # 0 = no Codex worker (default subagent context 또는 user_request_only 미요청)
                                     # >= 1 = SendMessage round 발화 횟수
                                     # >= 2 권장 (ADR-044 §결정 5 Adversarial measurable verification)
  
  write_errors:                      # v3 유지하되 Sonnet semantics 제거 — Orchestrator self-write retry only
    - step: story_section_9 | phase_comment | gate_label_attached | phase_label_transitioned | fix_ledger_append | diagnosis_spawn
      error_class: github_mcp_timeout | edit_conflict | mcp_auth_failure | other
      retry_count: <int>             # initial + max 2 retry = 3 attempts (v3 §4 partial-write policy 정합)
  
  writes_completed:                  # 의미 v3 와 동일 — Orchestrator self-write audit
    story_section_9: <bool>
    phase_comment: <bool>
    gate_label_attached: <bool>
    phase_label_transitioned: <bool>
    fix_ledger_append: <bool>        # FIX 시 only
    diagnosis_spawn: <bool>          # FIX 시 only
```

## 3. 4-step Orchestrator algorithm (v3 의 5-step → 4-step 단순화)

```
1. ReviewPL spawn → workers (Claude worker default + Codex worker on user_request) → dedup → review-verdict-v4 packet (no writes)
   ├── findings + pl_recommendation 작성
   ├── worker_dialog_rounds 채움 (Adversarial debate SendMessage round count)
   ├── mechanical_self_check_passed 채움 (design lane only — ArchitectPLAgent 가 ArchitectAgent §5.5 self-check 결과 forward, ADR-065 / CFP-438)
   └── return to Orchestrator

2. Orchestrator self-write (pl_recommendation = PASS | FIX | FIX_DISCRETIONARY 일 때만, ESCALATE_PACKET_INCOMPLETE 시 차단):
   ├── Story §9 append (lane iteration result) — append-only, never rolled back
   ├── GitHub Issue/PR comment (lane-specific prefix per comment-prefix-registry-v1) via mcp__github__add_issue_comment
   ├── PASS 시: gate:*-pass label + phase:* 다음 단계 전환 via mcp__github__issue_write
   └── (Story §12 Sonnet Decision Log row append — v4 에서 obsoleted, write 없음)

   **Partial-write policy (v3 §4 verbatim 차용)**: 각 sub-step 별 idempotent retry (initial + 2 retry = 3 회 한도). 실패 시 `writes_completed.<field>=false` + `write_errors[]` populate. **any required write 가 retry 한도 후에도 false 잔존 시 user escalation** (모든 required 가 아닌 1 건이라도 잔존 시). Story §9 는 append-only — 이미 append 된 내용 rollback 안 함. 외부 복구 후 다음 spawn 사이클에 missing write 재시도 가능.

3. FIX 시 (pl_recommendation=FIX):
   ├── Story §10 FIX Ledger append (decider field 제거 — PL recommendation 단일 source)
   ├── fix-ledger-sync.yml Action mirror (auto)
   └── DeveloperPL + ArchitectPL parallel diagnosis spawn (CFP-19 R4)

   **Spawn-failure policy (v3 §4 verbatim 차용)**: §10 append 성공 + diagnosis spawn 실패 시 — §10 row 유지 (append-only), 1 회 retry → second failure = user escalation. spawn 성공할 때까지 §10 row 는 "open FIX with no diagnosis" 상태로 visible.

4. ESCALATE 처리 (pl_recommendation=ESCALATE_PACKET_INCOMPLETE):
   ├── Orchestrator self-write 차단 (§9 / §10 / GitHub state 모두 차단)
   ├── ReviewPL 재 spawn (1 회 한도 per (story_key, lane, iteration))
   └── 한도 초과 시 user escalation
```

## 4. v3 → v4 migration 가이드

본 v4 는 wrapper Phase 1 PR (CFP-137 Wave 2) merge 시점 즉시 cutover. consumer scope 0건 (mctrader debut audit 까지) 으로 backward compat 면제. ADR-044 §결정 4 정합.

### 수신자 (Orchestrator + Lane PL) 갱신 항목

1. **Sonnet 호출 경로 제거** — Orchestrator 가 ReviewPL packet 수령 후 Sonnet Agent tool 호출 step skip. `pl_recommendation` 직접 적용.
2. **`decision_state` 처리 코드 제거** — 8-value enum 분기 무용. PL packet 의 pl_recommendation = `PASS` / `FIX` / `FIX_DISCRETIONARY` / `ESCALATE_PACKET_INCOMPLETE` 4-value 분기로 단순화.
3. **`sonnet_final_status` / `decider_decision_ref` field 참조 제거** — Story §10 FIX Ledger row 의 `decider:` column 자체 제거 (PL recommendation 단일 source).
4. **`worker_dialog_rounds` field 채움 의무** — review lane PL 이 SendMessage round count tracking → packet 작성 시 채움. Codex worker 미발화 시 (default subagent context 또는 user_request_only 미요청) `worker_dialog_rounds: 0`.
5. **5-step → 4-step algorithm 적용** — playbook §3.1 본문 갱신 (step 3 제거).

### Producer (codeforge-review plugin) 갱신 항목

1. PL synthesis template (`templates/review-pl-base.md`) 갱신 — packet 작성 시 v4 schema 따름.
2. `worker_dialog_rounds` field 채움 logic 추가 — SendMessage round count tracking.
3. canonical (codeforge-review plugin) review-verdict-v4.md 신설 + v3 status flip.
4. ADR-010 sibling sync follow-up PR 의무 — wrapper sibling 본 file 와 동기 verbatim.

### Story §10 FIX Ledger schema 영향

기존 v3 schema `| decider | override_marker |` column = v4 에서 제거 (PL recommendation 단일 source). 본 cleanup 은 별도 follow-up CFP — Story §10 schema 자체 SSOT = wrapper CLAUDE.md 의 "FIX Ledger §10 schema" 4 SSOT 예외 (ADR-012 §3) — wrapper Phase 1 PR scope 안에서 column 제거 추후 검토.

**v4 Phase 1 PR 시점 schema 정합**: 기존 v3 column (`decider`) 잔존 시 PL synthesis 가 `decider: <none>` 또는 absent 로 채움. cleanup 의무는 follow-up CFP scope.

## 5. ESCALATE 처리

pl_recommendation=ESCALATE_PACKET_INCOMPLETE 시:
- Orchestrator self-write 차단 (Story §9 / §10 / GitHub state 모두 차단)
- ReviewPL 재 spawn (1 회 한도 per (story_key, lane, iteration))
- 한도 초과 시 user escalation

## 6. v4 ↔ canonical sync (ADR-010)

본 file = canonical 단일 원본 (wrapper `docs/inter-plugin-contracts/review-verdict-v4.md` — ADR-118 D5, sibling sync 폐지. CFP-2178 S6 정정). CI lint = `check-inter-plugin-contracts.sh` (wrapper repo).

**Wrapper-first 절차 (ADR-010 §4 + Story §5.5 B1 default 채택)**:
1. 본 wrapper Phase 1 PR (CFP-137) merge — 본 file (sibling) 신설 + v3 sibling status flip.
2. canonical (codeforge-review plugin) sibling sync follow-up PR — verbatim mirror.
3. canonical merge 후 본 wrapper sibling 의 frontmatter `canonical_repo` 갱신 (annotation only — 내용 동일).

## 7. v3 deprecate / archive

- v3 status (wrapper sibling): Active → Archived (CFP-137 wrapper Phase 1 PR merge 시점)
- v3 archive: 6 CFP 무사고 후 (= v4 안정화 확인) — 별도 cleanup CFP에서 file 삭제 (v2 deprecate 패턴 정합)

## 8. v4 invariant — PL = decider 책임자 복원

ADR-022 Deprecated 후 (CFP-134 / ADR-035) Sonnet decider 자동 발동 무효 — PL `pl_recommendation` 자체가 final verdict. v4 가 본 invariant 를 schema level 에서 정식 codify.

- PL은 lane synthesis 후 findings + pl_recommendation 작성
- Orchestrator 는 pl_recommendation 직접 적용 (decision_state 무용, Sonnet 호출 무용)
- 사용자 explicit request 시에만 ad-hoc Sonnet 호출 가능 — codeforge orchestration 외 (memory `feedback_sonnet_decider_user_only.md` 정합)

**Edge case**: PL 이 packet 의 finding 분류 misjudgment 시 — packet 의 pl_recommendation 자체가 final 이므로 Sonnet override 채널 부재. mitigation = (a) 사용자 ad-hoc Sonnet 호출 요청 (codeforge 외 conversation), (b) FIX iteration 시 본 PL 재 spawn (Story file FIX Ledger 정합).

## 9. CONSUMER scope 영향 분석

- **mctrader (debut audit)**: 0건 — 본 v4 cutover 전까지 mctrader Story 자체 미진행 (mctrader debut audit 후 적용).
- **다른 consumer (가설)**: 본 cutover 시점에 v3 사용 중인 consumer 존재 가능성 0 — codeforge family agent 는 wrapper Orchestrator 만 review-verdict 수신. consumer Orchestrator 가 v3 직접 parsing 하는 사례 0건.
- **Backward compat 면제 근거**: ADR-008 §SemVer MAJOR bump rule + consumer scope 0 — 즉시 cutover 가능. Story §5.5 R3 default 채택.

## 10. Adversarial debate measurable verification (ADR-044 §결정 5)

`worker_dialog_rounds` field 가 5 권장 패턴 (Anthropic agent design pattern) Adversarial 영역 measurable signal:

- **0**: Codex worker 미발화 (default subagent context env=0 또는 dispatch_mode=user_request_only 미요청 시)
- **>= 1**: SendMessage round 발화 — Adversarial 진행
- **>= 2 권장**: 의미있는 debate cycle (Claude initial → Codex counter → Claude final, 또는 deeper rounds)

**Phase 2 PR scope (CFP-137 e2e fixture)**:
- review-verdict v4 schema lint — `worker_dialog_rounds` field 정합 검증
- `worker_dialog_rounds >= 2` 시 review-verdict packet 의 finding evidence 에 round-by-round narrative 포함 검증 (subjective fixture)

## 11. ArchitectAgent Phase 1 mechanical self-check (v4.2 — ADR-065 / CFP-438)

`mechanical_self_check_passed` optional bool field 가 ArchitectAgent Phase 1 산출물 commit 직전 7-item mechanical sync self-check 결과 explicit marker:

| # | 항목 | 검증 방법 |
|---|---|---|
| 1 | `label-registry-v2.md` 변경 시 `scripts/bootstrap-labels.sh` sync 동반 | `bash scripts/check-labels-bootstrap-strict.sh` PASS |
| 2 | `doc-locations.yaml` 변경 시 `bash scripts/check-doc-locations.sh --regen` 실행 | regenerate 후 `doc-location-registry.md` mirror diff 0 |
| 3 | 신규 `templates/github-workflows/*.yml` 시 `.github/workflows/` self-app copy 동반 | `diff -q templates/github-workflows/X.yml .github/workflows/X.yml` exit 0 (byte-identical) |
| 4 | CLAUDE.md / docs/** 내 link target 이 Phase 1 분배인지 확인 | Phase 2 file 참조 시 dangling — markdown internal link lint PASS |
| 5 | `docs/inter-plugin-contracts/MANIFEST.yaml` registries 블록 갱신 필요성 확인 | 신규 registry 도입 시 row append, `check-inter-plugin-contracts.sh` PASS |
| 6 | `docs/parallel-work/section-ownership.yaml` 정책 필요 시 row append | 동시 편집 영향 받는 신규 section 도입 시 row append |
| 7 | `docs/doc-locations.yaml` 신규 doc type row 필요성 확인 | 신규 doc type 도입 시 row append, `check-doc-locations.sh` PASS |

**Producer 책무 (ArchitectPLAgent)**:

- ArchitectAgent `§5.5 Phase 1 commit-time self-check` (ADR-065 / CFP-438) 통과 후 7 항목 결과 수령
- packet `mechanical_self_check_passed` 채움 (true = 모두 PASS 또는 NA, false = 1+ FAIL)
- false 시 `pl_recommendation: FIX` + `findings[]` 에 mechanical 누락 항목 each row append (severity P1, category `mechanical_sync_required`)

**Consumer 책무 (Orchestrator)**:

- false 수신 시: Story §10 FIX Ledger row append (Orchestrator monopoly, fix-event-v1 contract) → ArchitectPLAgent re-spawn 의뢰 → PL 이 ArchitectAgent re-spawn 명령
- true 수신 시: 정상 lane 진행 (mechanical 영역 PASS 신호로 채택)
- 미제공 (v4.1 producer) 수신 시: 무시 — backward-compat, 본 영역 lint 없음으로 간주

**적용 lane**:

- **design lane** (필수) — ArchitectPLAgent verdict packet 의 의무 필드
- **code lane / security lane** (optional) — code/security review 가 mechanical sync 외 영역만 다루므로 omit 가능

**marketplace 영역 분리**:

본 self-check 는 non-marketplace 영역만 (ADR-065 §결정 5). marketplace mirrored field (`name` / `version` / `description` / `author`) atomic invariant = ADR-063 SSOT (3-file: plugin.json / CHANGELOG.md / marketplace.json). cross-ref only — packet 의 mechanical_self_check_passed 는 marketplace 영역과 무관.

## 12. Boundary completeness semantic self-check (v4.3 — ADR-068 / CFP-527)

`boundary_completeness_self_check_passed` optional bool field 가 ArchitectAgent §7 작성 시 4 semantic invariant self-check 결과 explicit marker:

| Invariant | 코드 | 검증 방법 | verification format |
|---|---|---|---|
| API contract semantic completeness | I-1 | §3/§7 의 모든 public method/function 에 입력/출력 enum / state semantics docstring 명시 | docstring-template |
| Cross-module propagation completeness | I-2 | status enum 반환 method 의 모든 호출 site (caller) 에 enum 별 분기 처리 매핑 표 작성 | propagation-matrix |
| Guard placement intent | I-3 | invariant guard (assertion / pre-condition / post-condition) 의 위치가 "함수 진입 시점 무조건" vs "특정 path 한정" 인지 §7 본문 또는 ADR §결정 표에 명시 | guard-placement-diagram |
| Wording SSOT | I-4 | Story §3 결정 / §7 아키텍처 ↔ ADR ↔ impl (enum identifier / method name / docstring noun phrase) 양 방향 wording 동기화 | wording-sync-table |

**Dual-binding scheme (ADR-068 §결정 2)**:

- ArchitectAgent (design author): emit `boundary_completeness_self_check_passed: bool` (§7 작성 시 I-1~I-4 self-check)
- DesignReviewPL: `findings[].type: "boundary-completeness"` 로 I-1~I-4 위반 flag (문서 감사)
- CodeReviewPL: `findings[].type: "boundary-completeness"` 로 I-1~I-4 impl 위반 cross-validate (구현 검증)

**ADR-065 mechanical syntactic 분리 (§결정 3)**:

- `mechanical_self_check_passed` (ADR-065): syntactic 7-item (label-registry / doc-locations / workflow self-app 등) — 레포 governance structural 정합
- `boundary_completeness_self_check_passed` (ADR-068): semantic 4-invariant (API/propagation/guard/wording) — 설계 의미 완결성
- 양 필드 모두 design lane ArchitectPLAgent verdict packet 에 emit 의무 — 별도 boolean = 별도 FIX 트리거

**Producer 책무 (ArchitectPLAgent)**:

- ArchitectAgent I-1~I-4 self-check 통과 후 4 항목 결과 수령
- packet `boundary_completeness_self_check_passed` 채움 (true = I-1~I-4 모두 PASS, false = 1+ FAIL)
- false 시 `pl_recommendation: FIX` + `findings[]` 에 boundary-completeness 누락 항목 each row append (severity P1, category `boundary_completeness`, type `"boundary-completeness"`)

**Consumer 책무 (Orchestrator)**:

- false 수신 시: Story §10 FIX Ledger row append → ArchitectPLAgent re-spawn 의뢰
- true 수신 시: 정상 lane 진행 (boundary completeness semantic PASS 신호로 채택)
- 미제공 (v4.2 producer) 수신 시: 무시 — backward-compat

**Changelog**:

- v4.3 (2026-05-13, CFP-527): `boundary_completeness_self_check_passed` optional bool field 추가 + `findings[].type: "boundary-completeness"` literal 신설. ADR-068 §결정 2 dual-binding carrier. ADR-065 (mechanical syntactic) 와 disjoint — verdict packet 양 별도 boolean field.

## 13. Dimensional empirical grounding self-check (v4.4 — ADR-068 Amendment 1 / CFP-528)

`dimensional_empirical_self_check_passed` optional bool field 가 ArchitectAgent §3/§7 작성 시 I-5 dimensional empirical grounding self-check 결과 explicit marker:

| Dimension | Examples | Empirical source 후보 |
|---|---|---|
| latency | timeout / TTL / response_time / push_interval | wiretap script / probe artifact / RFC standard / vendor SLA |
| scale | batch_size / payload_size_bytes | sample run output / API spec |
| cardinality | max_connections / concurrent_users | load test result / capacity plan |
| throughput | rps / msgs_per_sec | benchmark / observation log |
| cost | token_budget / monthly_cost_usd | pricing doc / billing dashboard |
| accuracy | precision / sample_rate | statistical analysis |
| lifecycle | retention_days / expiry_seconds | compliance policy / RFC |
| volume | storage_gb / log_retention | capacity plan |
| rate | sample_rate / hit_rate | observation log |
| count | max_retries / queue_size | empirical tuning / RFC |

**Trigger 4종** (anti-pattern entry condition): empirical-absent default / synthetic guess / industry-assumption transplant / legacy inertia

**Mitigation 4종**: empirical-first (wiretap step 의무화) / explicit TBD 명시 / range-bound default / dimensional checklist

**Justification 조건** (annotation 면제): well-defined SLA / standardized protocol RFC / vendor doc explicit guarantee — 3종 부재 시 annotation 의무

**Exemption** (trivial decision): SLA/quantitative metric 무관 (logging / naming / refactoring) — Story §1 명시 선언 의무

**Producer 책무 (ArchitectPLAgent)**:
- ArchitectAgent I-5 self-check 통과 후 결과 수령
- packet `dimensional_empirical_self_check_passed` 채움 (true = 모든 quantitative parameter annotation 보유, false = 1+ 누락)
- false 시 `pl_recommendation: FIX` + `findings[]` 에 dimensional-empirical-gap 누락 항목 each row append (severity P1, category `dimensional_empirical_gap`, type `"dimensional-empirical-gap"`)

**Consumer 책무 (Orchestrator)**:
- false 수신 시: Story §10 FIX Ledger row append → ArchitectPLAgent re-spawn 의뢰
- true 수신 시: 정상 lane 진행
- 미제공 (v4.3 producer) 수신 시: 무시 — backward-compat

**Changelog**:

- v4.4 (2026-05-13, CFP-528): `dimensional_empirical_self_check_passed` optional bool field 추가 + `findings[].type: "dimensional-empirical-gap"` literal 신설. ADR-068 Amendment 1 §결정 1 I-5 carrier. ADR-065 (mechanical syntactic) + ADR-068 I-1~I-4 (boundary completeness) 와 disjoint — verdict packet 셋 별도 boolean field.

## 14. Deputy axis restructure self-check (v4.6 — ADR-042 Amendment 8 + ADR-086 / CFP-1086)

`deputy_axis_restructure_self_check_passed` optional bool field 가 deputy roster 변경 carrier Story (예: CFP-1086 Story-1 Amendment 8 = 7+3+1 roster 재편) 에서 ADR-086 §결정 2 5-checklist self-application 결과 explicit marker:

| Checklist | 통과 기준 |
|---|---|
| **axis disjoint** | 신설 deputy 가 기존 deputy 와 axis 중복 0 (orthogonal mandate scope dimension 의무 — ADR-086 §결정 1 axis 분석) |
| **cost-token budget** | spawn count 증가 시 ADR-068 I-5 dimensional empirical grounding 의무 (10 dimension `count` 의 quantitative parameter `[empirical-source: <ref> \| TBD]` annotation) |
| **consumer carrier** | consumer overlay 필드 명시 (CONDITIONAL applicability / tool override). `project.yaml` schema 신설 또는 갱신 의무 |
| **sibling Epic align** | 진행 중 sibling Epic 과 RACI 충돌 0 또는 cross-ref 명시 |
| **deferred trigger 명시** | 후속 carrier 별 CFP 명시 (sub-tuple expansion / CONDITIONAL P3 / consumer schema lint / RACI codify 등 follow-up 영역 enumeration) |

**적용 lane** = **design lane only** (deputy roster 변경 carrier Story 만 적용). code / security / test lane 모두 omit 가능.

**Producer 책무 (ArchitectPLAgent — design lane)**:
- ArchitectAgent (또는 후속 Amendment carrier) self-check 결과 수령 — 5-checklist + axis 분석 통과 시 true
- packet `deputy_axis_restructure_self_check_passed` 채움
- false 시 `pl_recommendation: FIX` + ArchitectAgent re-spawn 의뢰 (deferred carrier path 진입 — §결정 3 정합)

**Consumer 책무 (Orchestrator)**:
- false 수신 시: Story §10 FIX Ledger row append → ArchitectPLAgent re-spawn 의뢰
- true 수신 시: 정상 lane 진행 (deputy roster 변경 framework self-app PASS 신호로 채택)
- 미제공 (v4.5 이전 producer 또는 deputy roster 변경 0건 Story) 수신 시: 무시 — backward-compat

**Changelog**:

- v4.6 (2026-05-20, CFP-1086): `deputy_axis_restructure_self_check_passed` optional bool field 추가. ADR-086 P7 framework (Deputy 신설 결정 framework) self-application 첫 사례 carrier (CFP-1086 Story-1 ADR-042 Amendment 8 — 7+3+1 roster 재편). `boundary_completeness_self_check_passed` scope expansion (ADR-068 Amendment 2 wording SSOT chief tie-break ladder 3단계 mechanism — field semantic 확장, 4 invariants 자체 의미 변경 0건). ADR-065 (mechanical syntactic) + ADR-068 I-1~I-4 (boundary completeness) + ADR-068 I-5 (dimensional empirical) 와 disjoint — verdict packet 4 별도 boolean field.

## 15. DDD finding type 3 literal (v4.8 — ADR-091 / CFP-1117)

`findings[].type` enum 에 3 DDD finding type literal 신설 — ADR-091 §결정 6 enforcement layer 3-tier 의 **3번째 tier (review-verdict-v4 enum)** realize + §결정 7 INV-5 vocabulary theater 차단 forcing function 의 review-verdict finding 연결 (evidence #4):

| literal | DDD 영역 | 위반 정의 | forcing function 연결 | emit lane |
|---|---|---|---|---|
| `bc_violation` | Bounded Context | cross-BC 참조 ACL/OHS 패턴 부재 / BC boundary 침범 / 동음이의 미qualifier | Change Plan §3.D bounded_context_boundary | DesignReviewPL + CodeReviewPL |
| `aggregate_violation` | Aggregate | consistency boundary 침범 / transaction boundary 부정합 / invariant 미보존 / aggregate root 외부 직접 access | Change Plan §3.A affected_aggregates + ADR-091 §결정 3 Layer B real Aggregate | DesignReviewPL + CodeReviewPL (ModuleArchitectAgent boundary axis unified 영역, ADR-042 Amendment 10) |
| `ubiquitous_language_drift` | Ubiquitous Language | glossary SSOT 외 미정의 DDD term 사용 / 동음이의 미구분 / anti-pattern 어휘 | check-ubiquitous-language lint (ADR-091 Amendment 2 §결정 6 2번째 tier) | DesignReviewPL + CodeReviewPL |

**적용 원칙**:

- DesignReview = 설계 문서 감사 관점 (Change Plan §3.D bounded_context_boundary + §3.A affected_aggregates + Story §ubiquitous_language 완결성 검증)
- CodeReview = 구현 cross-validate 관점 (impl ↔ 설계 BC / Aggregate boundary 정합성 + glossary term drift 검증)
- Severity default = P1 (DDD boundary 위반이 구현 오류 / interpretation drift 로 전파 시 P0 가능)
- ADR-091 §결정 7 INV-5: 어휘 emit 이 review findings 를 실제로 변경 — 본 3 finding type 의 실 emit 사례 1건 이상이 vocabulary theater 차단 forcing function evidence (golden-path worked example S6 FINAL VERDICT evidence #4)

**verdict-level boolean field 와의 disjoint axis**:

- `mechanical_self_check_passed` (ADR-065 I-syntactic) / `boundary_completeness_self_check_passed` (ADR-068 I-1~I-4) / `dimensional_empirical_self_check_passed` (Amendment 1 I-5) / `audit_gate_pointer_self_check_passed` (Amendment 3 I-6) / `deputy_axis_restructure_self_check_passed` (Amendment 2 sibling CFP-1086) = ArchitectAgent self-check verdict-level boolean field
- DDD finding type 3종 = `findings[].type` enum literal 확장 (verdict-level boolean field 신설 0건). ADR-091 = DDD vocabulary governance 가 dedicated self-check boolean 을 신설하지 않고 findings[].type semantic accountability mechanism 으로 cross-validate (§결정 6 3번째 tier "reviewer finding type = semantic accountability" rationale 정합)

**Changelog**:

- v4.8 (2026-05-21, CFP-1117): `findings[].type` enum 에 `bc_violation` / `aggregate_violation` / `ubiquitous_language_drift` 3 DDD literal 신설. ADR-091 §결정 6 enforcement layer 3-tier 3번째 tier carrier + §결정 7 INV-5 forcing function review-verdict finding 연결. CFP-528 Amendment 1 (enum literal + 의미 1줄) pattern verbatim 답습. additive only backward-compat invariant (기존 v4.7 consumer 가 3 신규 enum literal 무시 가능). ADR-008 §결정 2 "enum literal 추가" MINOR bump 정합 (closed-enum additive). 5 sibling (requirements/design/develop/test/pmo v4.3) pre-existing drift = 본 S4 scope 외 (별 sweep CFP carrier).

## 16. Cross-anchor parity check enumeration (v4.9 — ADR-068 I-2 / CFP-1303)

`findings[].parallel_anchors_checked` optional array field 가 PL synthesis 시 cross-anchor parity check 결과 explicit marker:

**트리거 evidence (CFP-604)**:

- F-CR-604-2 (LOCAL_AUTHOR jq fallback unreachable, line 76) 식별 → FIX iter 2 적용
- 후속 CI 에서 동일 root cause 의 parallel site (REMOTE_AUTHOR jq parsing line 213) 추가 발견
- LOCAL_AUTHOR ↔ REMOTE_AUTHOR = 동일 root cause class (jq object/scalar handling) 의 짝
- CodeReviewPL 이 LOCAL 만 catch + REMOTE 누락 — cross-anchor parity check 부재 → pattern_count 2 evidence

**Wave 1 ↔ Wave 2 ↔ Wave 3 layered architecture**:

| Wave | Layer | Carrier | Status |
|---|---|---|---|
| 1 | prose anchor | CFP-1291 — CodeReviewPLAgent.md cross-anchor parity check step 본문 + finding inline marker prose | MERGED (2026-05-23 09:23 KST, codeforge-review #42) |
| 2 | schema field codify | CFP-1303 — `findings[].parallel_anchors_checked[]` v4.8 → v4.9 MINOR + 3 plugin sibling sync | 본 carrier |
| 3 | mechanical lint | TBD — `parallel_anchors_checked` field presence-grep heuristic on finding emit | deferred-followup |

**pattern_type 5종 enum closed-set**:

| Enum | 영역 | 예시 |
|---|---|---|
| `local_remote` | LOCAL_X ↔ REMOTE_X symmetric pair | LOCAL_AUTHOR ↔ REMOTE_AUTHOR (CFP-604 trigger), LOCAL_SHA ↔ REMOTE_SHA |
| `client_server` | client side ↔ server side symmetric | client validation ↔ server validation, client encode ↔ server decode |
| `read_write` | read path ↔ write path 짝 | read cache ↔ write cache invalidation, get_X ↔ set_X |
| `forward_reverse` | forward direction ↔ reverse direction 짝 | encode ↔ decode, serialize ↔ deserialize, expand ↔ contract |
| `enum_closure` | enum value 전수 coverage | switch/match 모든 enum value branch coverage, error class enumeration |

**ADR-068 I-2 cross-module propagation completeness 연결**:

- ADR-068 I-2 = status enum 반환 method 의 모든 호출 site (caller) 에 enum 별 분기 처리 매핑 표 작성 = propagation-matrix verification format
- `parallel_anchors_checked` = micro-scale parallel form — 동일 root cause class 의 parallel site 검사 (caller fan-out 대신 sibling site fan-in)
- 두 mechanism 모두 cross-anchor / cross-module 의미 완결성 영역 (I-2 = module-level, `parallel_anchors_checked` = finding-level)

**Producer 책무 (PL — primary: CodeReviewPL)**:

- PL synthesis 시 각 finding 별 "parallel anchor enumeration" step 수행
- finding category 가 위 5종 pattern_type 에 해당 시 candidate site 검색 (grep / glob / file 안 line context 분석)
- 결과를 `parallel_anchors_checked[]` array 로 채움 — matched 발견 시 신규 finding row append + parallel anchor 자체도 `parallel_anchors_checked` 역방향 row 부착 가능
- 미수집 finding = field absent / null (Wave 3 lint heuristic 영역)

**Consumer 책무 (Orchestrator)**:

- field 수신 시: 별도 action 없음 — Story §9 verdict append 시 verbatim 보존
- field 미수신 시 (v4.8 producer 또는 PL 검색 미수행): 무시 — backward-compat

**적용 lane**:

- **CodeReviewPL** (primary) — Wave 1 CFP-1291 본문 정합 (CodeReviewPLAgent.md cross-anchor parity check step 의 schema 형식 carrier)
- **DesignReviewPL** (optional) — 설계 boundary 영역의 parallel-anchor 패턴 검색 시 emit 가능
- **SecurityTestPL** (optional) — 보안 영역의 parallel-anchor 패턴 (예: input validation client_server) 검색 시 emit 가능

**verdict-level boolean field 와의 disjoint axis**:

- `mechanical_self_check_passed` (ADR-065 syntactic) / `boundary_completeness_self_check_passed` (ADR-068 I-1~I-4) / `dimensional_empirical_self_check_passed` (Amendment 1 I-5) / `audit_gate_pointer_self_check_passed` (Amendment 3 I-6) / `deputy_axis_restructure_self_check_passed` (Amendment 2 sibling CFP-1086) = ArchitectAgent self-check verdict-level boolean field
- `parallel_anchors_checked` = `findings[]` entry 안 optional array field (anchor_id pattern 답습) — verdict-level boolean 신설 0건

**Changelog**:

- v4.9 (2026-05-23, CFP-1303): `findings[].parallel_anchors_checked` optional array field 신설. CFP-604 retro F7 Wave 2 carrier (Wave 1 CFP-1291 prose anchor + Wave 3 mechanical lint 의 중간 layer schema codify). 각 entry = {file_line: string, pattern_type: enum 5종 closed-set local_remote/client_server/read_write/forward_reverse/enum_closure, matched: bool}. ADR-068 I-2 cross-module propagation completeness 의 review-verdict layer realization (micro-scale parallel form). CFP-391 (anchor_id) pattern 답습 — findings[] entry 안 optional field 추가. additive only backward-compat invariant (기존 v4.8 consumer 가 본 신규 field 무시 가능). ADR-008 §결정 2 "새 선택 필드 추가" MINOR bump 정합. mechanical lint (presence-grep heuristic) = Wave 3 별 carrier (deferred-followup, ADR-064 §결정 1 scope unitary).

## 17. Chief-author cross-ADR claim consistency self-check (v4.12 — ADR-068 Amendment 5 / CFP-1565)

`chief_author_crossref_consistency_self_check_passed` optional bool field 가 ArchitectAgent §3/§7/§10/§11 작성 시 I-7 chief-author cross-ADR scope/fact claim consistency self-check 결과 explicit marker:

| Scope | I-7 검증 대상 | verification format |
|---|---|---|
| cross-ADR scope claim | 다른 ADR 의 scope list / 권한 범위 (예: PAT scope) 인용 값 ↔ 대상 ADR SSOT 대조 | cross-adr-claim-verify-annotation |
| cross-ADR count claim | 다른 ADR 의 count (예: invariant 개수 / lane 개수) 인용 값 ↔ 대상 ADR SSOT 대조 | cross-adr-claim-verify-annotation |
| cross-ADR enum claim | 다른 ADR 의 enum closed-set 인용 값 ↔ 대상 ADR SSOT 대조 | cross-adr-claim-verify-annotation |

**cross-adr-claim-verify-annotation 3-key**:

- `cited_adr` — `ADR-NNN §결정 N` 형식 (인용 출처)
- `cited_value` — 인용한 list / count / enum / scope 값 verbatim
- `verify_status` — verified (target ADR direct Read 대조 완료) / pending (미대조) / out-of-scope (Justification 면제)

**Trigger**: chief author §3/§7/§10/§11 작성 시 cross-ADR scope/fact claim 인용 발화 시점에 대상 ADR direct Read-verify 누락 또는 인용 값 mismatch detect → false + `findings[].type: "chief-author-crossref-inconsistency"` 동반 emit.

**Justification 조건** (annotation 면제): self-ref (동일 ADR 안 §결정 cross-ref) / well-known stable constant (변경 빈도 0 영역, 예: SemVer 정의).

**Exemption** (trivial decision): cross-ADR scope/fact claim 0건 Story = scope 외 (Story §1 명시 선언).

**I-4 wording SSOT 와 disjoint axis**: I-4 = Story↔ADR↔impl identifier 표기 동기화 (wording sync) / I-7 = cross-ADR factual/scope **값** 의 SSOT 정합. I-6 audit-gate-pointer = pointer **실재** verify / I-7 = 인용 **값** SSOT 정합.

**Producer 책무 (ArchitectPLAgent)**:
- ArchitectAgent I-7 self-check 통과 후 결과 수령
- packet `chief_author_crossref_consistency_self_check_passed` 채움 (true = 모든 cross-ADR claim annotation 보유 + verify_status=verified/out-of-scope, false = 1+ pending/mismatch)
- false 시 `pl_recommendation: FIX` + `findings[]` 에 chief-author-crossref-inconsistency 항목 each row append (severity P1, type `"chief-author-crossref-inconsistency"`)

**Consumer 책무 (Orchestrator)**:
- false 수신 시: Story §10 FIX Ledger row append → ArchitectPLAgent re-spawn 의뢰
- true 수신 시: 정상 lane 진행
- 미제공 (v4.11 이전 producer) 수신 시: 무시 — backward-compat

**Changelog**:

- v4.12 (2026-06-01, CFP-1565): `chief_author_crossref_consistency_self_check_passed` 7번째 verdict-level optional bool field 신설 + `findings[].type: "chief-author-crossref-inconsistency"` 11번째 enum literal 신설. ADR-068 Amendment 5 §결정 1 I-7 carrier. mechanical_self_check_passed (ADR-065 syntactic) + boundary_completeness_self_check_passed (ADR-068 I-1~I-4) + dimensional_empirical_self_check_passed (Amendment 1 I-5) + audit_gate_pointer_self_check_passed (Amendment 3 I-6) + deputy_axis_restructure_self_check_passed (Amendment 2) + living_architecture_updated_self_check_passed (ADR-112) 와 disjoint — verdict packet 7번째 별도 boolean field. CFP-1426 v4.11 pattern verbatim 답습. CFP-1522 retro F-003 P1 evidence. closed-enum 10 → 11 ratchet (additive only). DesignReviewPL + CodeReviewPL dual cross-validate (sibling cross-repo PR codeforge-review canonical).

## 18. Runtime-failure 변종 falsification + I-8 invariant-surface extension (v4.14 — ADR-064 §결정 13 + ADR-125 Amendment 2 + ADR-068 I-8 Amendment 6 / CFP-2358)

본 v4.14 = Epic #2357 진단축의 Phase 2 wrapper wire — Phase 1 ADR 3종이 review-verdict-v4 binding 을 "Phase 2 별 carrier defer" (ADR-064 §결정 13 Amendment 결정 2) / "S4 #2350 위임" (ADR-068 Amendment 6) 으로 명시한 mechanical carrier. 본 PS1 (#2358) = 그 single-owner carrier. (verify_status: verified — worktree Read ADR-064 "결정 13 — 문제정의 오류 rung", ADR-125 "Amendment 2 ... runtime-failure 변종 신설", ADR-068 "Amendment 6 ... I-8 standing invariant-surface invariant 신설".)

### 18.1 findings[].type 2 신규 literal (closed-enum 11 → 13, additive only)

| literal | 영역 | 위반 정의 | primary emit lane | severity |
|---|---|---|---|---|
| `invariant-violation` | runtime-failure falsification | 증상을 설명하는 file:line 으로 짚힌 위반 invariant (실패 경로 long-lived mutable 구조의 bound/lifetime/ordering ground-truth 위반). ADR-064 §결정 13 재진입 규율 3 (비대칭 결정규칙) 의 verdict-level finding | RequirementsReviewPL (runtime-failure 변종 — ADR-125 Amendment 2) | P0/P1 |
| `invariant-surface-not-extended` | I-8 standing surface | impl PR 이 새 long-lived mutable structure 추가 (또는 기존 구조 bound/lifetime/ordering invariant 변경) 하고 `docs/system-invariants.md` 색인 row 부재/미갱신 detect. ADR-068 I-8 Amendment 6 | CodeReviewPL (impl PR) | P1 |

### 18.2 invariant_surface_extension_self_check_passed 8번째 verdict-level optional bool field

`invariant_surface_extension_self_check_passed` (CFP-2351 declare → S4 #2350 위임분, 본 CFP-2358 Phase 2 carrier — ADR-068 I-8 Amendment 6) 가 impl PR 의 standing invariant-surface 확장 self-check 결과 explicit marker:

- **true** = 신규/변경 long-lived mutable structure 각각 `docs/system-invariants.md` 7-key row append/갱신 완료 OR 새 구조 0건 (runtime 0 governance Story 등 ADR-068 I-8 면제 — `plugin-meta-na` 정합)
- **false** = 1+ 신규 구조 색인 부재/미갱신 — FIX 의무 + `findings[].type: "invariant-surface-not-extended"` 동반 emit (severity P1)
- 기존 7 verdict-level bool field (mechanical / boundary_completeness / dimensional_empirical / marketplace_sync / audit_gate_pointer / deputy_axis_restructure / living_architecture / chief_author_crossref) 와 **disjoint** — 동일 verdict packet 8번째 별도 boolean field (I-8 standing invariant-surface axis). 7 write-time 1회 발화 검증 axis 와 별 axis — 영속 standing-doc 색인 면.
- 적용 lane: code lane primary (impl PR), design lane optional (Change Plan §3/§5/§11 ↔ standing surface 정합)
- 미제공 (v4.13 이전 producer) → Orchestrator 무시 (backward-compat)

### 18.3 runtime-failure 변종 verdict 비대칭 규칙 (Popper)

runtime-failure lane (요구사항리뷰 internal-invariant 변종, ADR-125 Amendment 2) 의 verdict 는 **비대칭 규칙** 을 적용한다 — 증상을 설명하는 file:line `invariant-violation` finding **1개가 N개의 "verified OK" attestation 을 이긴다** (Popper). 단일 falsification 이 N attestation 을 이기므로, runtime-failure 변종 verdict 는 "전부 확인함 OK" N개 attestation 만으로 PASS 를 낼 수 없다 — 증상 미설명 시 `invariant-violation` finding 부재가 PASS 의 필요조건이되 충분조건은 아니다 (falsifier 탐색 의무). 이는 ADR-064 §결정 13 재진입 규율 3 (사다리 진단 레벨) 과 ADR-125 Amendment 2 §2 (lane 게이트 verdict 레벨) 의 review-verdict packet 레벨 realization 이다. lane enum 무변경 — runtime-failure 변종은 `requirements-review` lane 값을 internal-invariant 축으로 재사용한다 (외부사실 축과 disjoint 공존, ADR-124 §결정 6 무약화).

### 18.4 Producer / Consumer 책무

**Producer 책무 (RequirementsReviewPL / CodeReviewPL)**:
- runtime-failure 변종 falsification 시 file:line invariant-violation finding emit (RequirementsReviewPL primary — ADR-125 Amendment 2 게이트)
- impl PR I-8 surface 확장 self-check 결과 수령 → packet `invariant_surface_extension_self_check_passed` 채움 (CodeReviewPL primary)
- false 시 `pl_recommendation: FIX` + `findings[]` 에 invariant-surface-not-extended each row append (severity P1)

**Consumer 책무 (Orchestrator)**:
- false 수신 시: Story §10 FIX Ledger row append → 재진입 lane 또는 impl PR re-spawn 의뢰
- true 수신 시: 정상 lane 진행
- 미제공 (v4.13 이전 producer) 수신 시: 무시 — backward-compat

### 18.5 Changelog

- v4.14 (2026-06-19, CFP-2358): `findings[].type` enum 에 `invariant-violation` (12번째) + `invariant-surface-not-extended` (13번째) literal 신설 (closed-enum 11 → 13 ratchet, additive only) + `invariant_surface_extension_self_check_passed` 8번째 verdict-level optional bool field 신설 + runtime-failure 변종 verdict 비대칭 규칙 §18.3 본문 명시. ADR-064 §결정 13 (root-cause 3rd rung) + ADR-125 Amendment 2 (runtime-failure 변종 internal-invariant 축) + ADR-068 I-8 Amendment 6 (standing invariant-surface) 의 Phase 2 mechanical wire carrier — Phase 1 ADR 3종이 "Phase 2 별 carrier defer" / "S4 #2350 위임" 으로 명시한 binding. lane enum 무변경 (requirements-review 재사용). CFP-1565 (verdict-level bool field + findings type literal 동시 신설) pattern verbatim 답습. ADR-008 §결정 2 'enum literal 추가' + '새 선택 필드 추가' MINOR bump 정합. additive only backward-compat invariant (기존 v4.13 consumer 가 2 신규 literal + 8번째 field 무시 가능). RequirementsReviewPLAgent / ClaudeReviewAgent / CodexReviewAgent runtime-failure branch 배선 = Epic #2357 Phase 2 checklist carrier (별 Story).
