# 검사 146개 판정표 (CHECK-VERDICT)

> 근거: evidence-checks-registry.yaml 의 등급(tier)·상태(status)·재발횟수(recurrence) 직접 파싱.
> 자동 분류 규칙 — 차단형/실제깨짐=KEEP · 미연결/재발0+감시=CUT-NOW · 재발0=CUT-LIKELY · 재발5+=RECONSIDER

## 요약

| 판정 | 개수 | 의미 |
|---|---:|---|
| KEEP | 24 | 진짜 일하는 것 — 유지 |
| RECONSIDER | 9 | 재발 많음 — 단 시스템 단순화 시 사라질 수도 |
| CUT-NOW | 38 | 미연결 or 증거0 감시 — 즉시 제거 |
| CUT-LIKELY | 75 | 예방적 추가, 증거 없음 — 제거/통합 |
| **합계** | **146** | |

## 유지 (KEEP) — 24개

| 검사명 | 등급 | 재발 | 소유결정 | 사유 |
|---|---|---:|---|---|
| marketplace-description-verbatim | blocking-on-pr | 6 | ADR-063 | 차단형 |
| plugin-declarative-seed-byte-parity-check | warning | 6 | ADR-107 | 실제 깨짐 검사 |
| workflow-yaml-parse | warning | 6 | ADR-060 | 실제 깨짐 검사 |
| amendment-number-frontmatter-verify | warning | 2 | ADR-082 | 실제 깨짐 검사 |
| label-registry-frozen-baseline-count-parity | warning | 2 | ADR-108 | 실제 깨짐 검사 |
| adr-dual-block-parity | warning | 1 | ADR-082-Amendment-28 | 실제 깨짐 검사 |
| inter-plugin-contracts-parity | warning | 1 | ADR-010 | 실제 깨짐 검사 |
| workflow-actionlint-precommit | warning | 1 | ADR-026 | 실제 깨짐 검사 |
| worktree-first-spawn-evidence-cwd | blocking-on-pr | 1 | ADR-040 | 차단형 |
| auto-phase-label-sibling-parity | warning | 0 | ADR-065 | 실제 깨짐 검사 |
| branch-protection-context-parity | warning | 0 | ADR-024 | 실제 깨짐 검사 |
| ddd-pattern-frontmatter-check | warning | 0 | ADR-091 | 실제 깨짐 검사 |
| doc-locations-registry | warning | 0 | ADR-041 | 실제 깨짐 검사 |
| invariant-check | blocking-on-pr | 0 | ADR-002 (footer pattern) + 다중 CFP (5/7/8/10) | 차단형 |
| issue-design-content-confluence-link | warning | 0 | ADR-111 | 실제 깨짐 검사 |
| marketplace-parity | warning | 0 | ADR-016 / ADR-023 §결정 5 | 실제 깨짐 검사 |
| per-plugin-cumulative-counter | blocking-on-pr | 0 | ADR-024 | 차단형 |
| phase-gate-mergeable | blocking-on-merge | 0 | ADR-031 §결정 3 + label-registry-v2 | 차단형 |
| version-3way-atomic | blocking-on-pr | 0 | ADR-063 | 차단형 |
| workflow-permissions-block-presence | warning | 0 | ADR-060 | 실제 깨짐 검사 |
| worktree-first-pre-checkout | blocking-on-pr | 0 | ADR-040 | 차단형 |
| worktree-first-pre-commit-main-block | blocking-on-pr | 0 | ADR-040 | 차단형 |
| worktree-first-session-start-wire | blocking-on-pr | 0 | ADR-040 | 차단형 |
| wrapper-managed-block | blocking-on-pr | 0 | ADR-027 | 차단형 |

## 재검토 (RECONSIDER) — 재발 많지만 자가초래 복잡도일 수 있음 — 9개

| 검사명 | 등급 | 재발 | 소유결정 | 사유 |
|---|---|---:|---|---|
| amendment-slot-reservation | warning | 9 | ADR-082 | 재발9회(실제 다발)—단 시스템 자체 복잡도 부작용 가능 |
| chief-author-span-telemetry | warning | 9 | ADR-039 | 재발9회(실제 다발)—단 시스템 자체 복잡도 부작용 가능 |
| mid-spawn-drift-detection | warning | 9 | ADR-082 | 재발9회(실제 다발)—단 시스템 자체 복잡도 부작용 가능 |
| spawn-prompt-head-pin-presence | warning | 9 | ADR-073 | 재발9회(실제 다발)—단 시스템 자체 복잡도 부작용 가능 |
| stale-local-main-checkout-divergence-check | warning | 8 | ADR-073-Amendment-7 | 재발8회(실제 다발)—단 시스템 자체 복잡도 부작용 가능 |
| architect-chief-author-base-sha-freeze-verify | warning | 6 | ADR-073-Amendment-15 | 재발6회(실제 다발)—단 시스템 자체 복잡도 부작용 가능 |
| retro-batch-adr-draft-pre-publish | warning | 6 | ADR-045-Amendment-9 | 재발6회(실제 다발)—단 시스템 자체 복잡도 부작용 가능 |
| bypass-label-counter | warning | 5 | ADR-024 | 재발5회(실제 다발)—단 시스템 자체 복잡도 부작용 가능 |
| marketplace-drift-detection | warning | 5 | ADR-063 | 재발5회(실제 다발)—단 시스템 자체 복잡도 부작용 가능 |

## 즉시 제거 (CUT-NOW) — 38개

| 검사명 | 등급 | 재발 | 소유결정 | 사유 |
|---|---|---:|---|---|
| issue-body-claim-pre-screen | warning | 7 | ADR-082-Amendment-20 | 미연결(선언만, 검사 없음) |
| admin-merge-preflight-gate | warning | 3 | ADR-113 | 미연결(선언만, 검사 없음) |
| fix-loop-reverify-mandate | warning | 3 | ADR-082-Amendment-29 | 미연결(선언만, 검사 없음) |
| spawn-prompt-fact-verify | warning | 3 | ADR-082-Amendment-23 | 미연결(선언만, 검사 없음) |
| retro-fact-verify-mandate | warning | 2 | ADR-082-Amendment-31 | 미연결(선언만, 검사 없음) |
| bootstrap-labels-precondition | warning | 1 | ADR-060 | 미연결(선언만, 검사 없음) |
| deputy-spawn-count-empirical-grounding | warning | 1 | ADR-068-Amendment-1 | 미연결(선언만, 검사 없음) |
| filesystem-worktree-pinned-default | warning | 1 | ADR-040-Amendment-7 | 미연결(선언만, 검사 없음) |
| synthesis-vs-commit-gap-check | warning | 1 | ADR-082-Amendment-24 | 미연결(선언만, 검사 없음) |
| workflow-changed-files-pattern | warning | 1 | ADR-082 | 미연결(선언만, 검사 없음) |
| adr-077-ratchet-declared | warning | 0 | ADR-077 | 재발0+거버넌스감시 |
| adr-sunset-criteria | warning | 0 | ADR-058 | 재발0+거버넌스감시 |
| architect-marketplace-self-check | warning | 0 | ADR-063 | 재발0+거버넌스감시 |
| backlog-issue-phase-label-forbid | warning | 0 | ADR-024-Amendment-17 | 미연결(선언만, 검사 없음) |
| bypass-justification-marker | warning | 0 | ADR-024 | 재발0+거버넌스감시 |
| codename-glossary-lookup | warning | 0 | ADR-071 | 재발0+거버넌스감시 |
| codex-network-scope-presence | warning | 0 | ? | 미연결(선언만, 검사 없음) |
| corpus-claim-verify | warning | 0 | ADR-082 | 재발0+거버넌스감시 |
| cross-layer-impact-detection | warning | 0 | ADR-090 | 미연결(선언만, 검사 없음) |
| cross-plugin-ownership-verify | warning | 0 | ADR-082 | 재발0+거버넌스감시 |
| cross-repo-bypass-counter | warning | 0 | ADR-024 | 재발0+거버넌스감시 |
| debate-convergence-quality-marker-presence | warning | 0 | ADR-059 | 재발0+거버넌스감시 |
| decision-principle-vocab | warning | 0 | ADR-064 | 재발0+거버넌스감시 |
| dependency-order-enforce | warning | 0 | ADR-090 | 미연결(선언만, 검사 없음) |
| deploy-lane-spawn-evidence | warning | 0 | ADR-087 | 미연결(선언만, 검사 없음) |
| deploy-review-lane-spawn-evidence | warning | 0 | ADR-088 | 미연결(선언만, 검사 없음) |
| dialog-fidelity-effect | warning | 0 | ADR-071 | 재발0+거버넌스감시 |
| kst-timestamp-display | warning | 0 | ADR-079 | 재발0+거버넌스감시 |
| lane-entry-ownership-verify | warning | 0 | ADR-085-§결정-3 | 재발0+거버넌스감시 |
| orchestrator-spawn-prompt-fact-verify | warning | 0 | ADR-082 | 재발0+거버넌스감시 |
| runtime-hook-pretooluse-agent-presence | warning | 0 | ADR-115 | 미연결(선언만, 검사 없음) |
| runtime-hook-stop-presence | warning | 0 | ADR-115 | 미연결(선언만, 검사 없음) |
| runtime-hook-subagentstop-presence | warning | 0 | ADR-115 | 미연결(선언만, 검사 없음) |
| runtime-hook-userprompt-presence | warning | 0 | ADR-115 | 미연결(선언만, 검사 없음) |
| schema-change-7-principles-self-check | warning | 0 | ADR-089 | 미연결(선언만, 검사 없음) |
| sunset-weakening-evidence | warning | 0 | ADR-058 | 재발0+거버넌스감시 |
| wording-dictionary | warning | 0 | ADR-064 | 재발0+거버넌스감시 |
| wording-ssot-grep-lint | warning | 0 | ADR-068 | 재발0+거버넌스감시 |

## 제거 유력 (CUT-LIKELY) — 75개

| 검사명 | 등급 | 재발 | 소유결정 | 사유 |
|---|---|---:|---|---|
| design-lane-plugin-feasibility-check | warning | 3 | ADR-107 | 재발3회(소수)—통합 검토 |
| subagent-sibling-story-polling-evidence | warning | 3 | ADR-073-Amendment-6 | 재발3회(소수)—통합 검토 |
| worktree-self-ownership-verify | warning | 3 | ADR-073-Amendment-3 | 재발3회(소수)—통합 검토 |
| claude-md-amendment-ref-drift-check | warning | 2 | ADR-074 | 재발2회(소수)—통합 검토 |
| lane-evidence-trail | warning | 2 | ADR-031 §결정 3 + fix-event-v1 | 재발2회(소수)—통합 검토 |
| mcp-token-freshness-precheck | warning | 2 | ADR-073-Amendment-8 | 재발2회(소수)—통합 검토 |
| numeric-claim-write-time-verify | warning | 2 | ADR-082-Amendment-22 | 재발2회(소수)—통합 검토 |
| parallel-anchors-checked-presence | warning | 2 | ADR-068 | 재발2회(소수)—통합 검토 |
| parallel-work-sentinel-pickup | warning | 2 | ADR-073-Amendment-2 | 재발2회(소수)—통합 검토 |
| bats-red-green-proof-presence | warning | 1 | ADR-060 | 재발1회(소수)—통합 검토 |
| branch-protection-context-name-strict-match | warning | 1 | ADR-024 | 재발1회(소수)—통합 검토 |
| codex-fallback-subclass-tally | warning | 1 | ADR-052-Amendment-14 | 재발1회(소수)—통합 검토 |
| confluence-drift-detection | warning | 1 | ADR-103 | 재발1회(소수)—통합 검토 |
| pl-inline-verify-cwd-mandate | warning | 1 | ADR-040 | 재발1회(소수)—통합 검토 |
| post-merge-followup-workflow-success-rate-kpi | warning | 1 | ADR-026 | 재발1회(소수)—통합 검토 |
| pre-spawn-prompt-finalize-verify | warning | 1 | ADR-082 | 재발1회(소수)—통합 검토 |
| stop-time-continuous-confirm-detect | warning | 1 | ADR-064 | 재발1회(소수)—통합 검토 |
| 429-retry-evidence-presence | warning | 0 | ADR-109 | 재발0(예방적 추가, 증거 없음) |
| ac-mapping-cross-ref | warning | 0 | CFP-451 F-001 Option C | 재발0(예방적 추가, 증거 없음) |
| active-sessions-presence | warning | 0 | ADR-085-§결정-2 | 재발0(예방적 추가, 증거 없음) |
| adr-077-design-reading-mandate-declared | warning | 0 | ADR-077 | 재발0(예방적 추가, 증거 없음) |
| adr-077-integration | warning | 0 | ADR-077 | 재발0(예방적 추가, 증거 없음) |
| architecture-drift | warning | 0 | ADR-078 | 재발0(예방적 추가, 증거 없음) |
| atlassian-tool-drift | warning | 0 | ADR-103 | 재발0(예방적 추가, 증거 없음) |
| atomic-upgrade-zero-drift | warning | 0 | ADR-037 | 재발0(예방적 추가, 증거 없음) |
| auto-phase-label | warning | 0 | ADR-024 Amendment 4 §결정 6.A.1 | 재발0(예방적 추가, 증거 없음) |
| bounded-context-presence-check | warning | 0 | ? | 재발0(예방적 추가, 증거 없음) |
| branch-protection-drift | warning | 0 | ADR-024 Amendment 2 | 재발0(예방적 추가, 증거 없음) |
| branch-protection-sync | warning | 0 | ADR-024 | 재발0(예방적 추가, 증거 없음) |
| canary-auto-promote | warning | 0 | ADR-105 | 재발0(예방적 추가, 증거 없음) |
| canary-compatibility-check | warning | 0 | ADR-72-Amendment-3 | 재발0(예방적 추가, 증거 없음) |
| carrier-bootstrap | warning | 0 | ADR-062 | 재발0(예방적 추가, 증거 없음) |
| channel-drift-detection | warning | 0 | ADR-063 | 재발0(예방적 추가, 증거 없음) |
| check-atlassian-allow | warning | 0 | ADR-099 | 재발0(예방적 추가, 증거 없음) |
| claude-md-line-cap | warning | 0 | ADR-012 | 재발0(예방적 추가, 증거 없음) |
| comment-prefix-registry | warning | 0 | comment-prefix-registry-v1 (kind:registry) | 재발0(예방적 추가, 증거 없음) |
| debate-parallel-cap-check | warning | 0 | ADR-109 | 재발0(예방적 추가, 증거 없음) |
| dependency-closure-self-test | warning | 0 | ADR-076 | 재발0(예방적 추가, 증거 없음) |
| deployment-schema-check | warning | 0 | ADR-091 | 재발0(예방적 추가, 증거 없음) |
| deputy-stagger-check | warning | 0 | ADR-109 | 재발0(예방적 추가, 증거 없음) |
| design-review-pl-8-6-pointer | warning | 0 | ADR-068 | 재발0(예방적 추가, 증거 없음) |
| dogfood-artifact-paths | warning | 0 | ADR-013 / ADR-017 | 재발0(예방적 추가, 증거 없음) |
| duplicate-session-start-hook-check | warning | 0 | ADR-038 | 재발0(예방적 추가, 증거 없음) |
| epic-cutover-gate-evidence-quad-check | warning | 0 | ADR-72 | 재발0(예방적 추가, 증거 없음) |
| evidence-registry-anomaly | warning | 0 | ADR-060 | 재발0(예방적 추가, 증거 없음) |
| evidence-registry-naming | warning | 0 | ADR-060 | 재발0(예방적 추가, 증거 없음) |
| evidence-registry-schema-validation | warning | 0 | ADR-060 | 재발0(예방적 추가, 증거 없음) |
| execution-context-state-presence | warning | 0 | ADR-082 | 재발0(예방적 추가, 증거 없음) |
| fix-event-depth-scope-presence | warning | 0 | ADR-067 Amendment 1 | 재발0(예방적 추가, 증거 없음) |
| inter-plugin-contracts | warning | 0 | ADR-008 / ADR-010 / MANIFEST.yaml | 재발0(예방적 추가, 증거 없음) |
| inter-plugin-drift | warning | 0 | ADR-011 | 재발0(예방적 추가, 증거 없음) |
| label-registry-sync | warning | 0 | label-registry-v2 (kind:registry) | 재발0(예방적 추가, 증거 없음) |
| living-architecture-update | warning | 0 | ADR-112 | 재발0(예방적 추가, 증거 없음) |
| marketplace-sync | warning | 0 | ADR-016 (mirrored field) | 재발0(예방적 추가, 증거 없음) |
| parallel-dispatch-prompt-check | warning | 0 | ADR-064 | 재발0(예방적 추가, 증거 없음) |
| parallel-epic-conflict | warning | 0 | ADR-050 | 재발0(예방적 추가, 증거 없음) |
| production-cutover-deputy-spawn-evidence | warning | 0 | ADR-72 | 재발0(예방적 추가, 증거 없음) |
| rate-limit-fallback-rate | warning | 0 | ADR-057 | 재발0(예방적 추가, 증거 없음) |
| regression-smoke-health-monitor | warning | 0 | ADR-106 | 재발0(예방적 추가, 증거 없음) |
| required-workflow-drift | warning | 0 | ADR-048 §결정 3 | 재발0(예방적 추가, 증거 없음) |
| retro-alert-pickup-rate | warning | 0 | ADR-045 | 재발0(예방적 추가, 증거 없음) |
| retro-mandatory-deployed | warning | 0 | ADR-045 | 재발0(예방적 추가, 증거 없음) |
| rollback-signal-monitor | warning | 0 | ADR-105 | 재발0(예방적 추가, 증거 없음) |
| rulesets-drift | warning | 0 | ADR-048 §결정 1 | 재발0(예방적 추가, 증거 없음) |
| section-1-verbatim-postmerge | warning | 0 | ADR-027 | 재발0(예방적 추가, 증거 없음) |
| self-improving-loop-closure | warning | 0 | ADR-106 | 재발0(예방적 추가, 증거 없음) |
| sibling-pr-label-author-check | warning | 0 | ADR-010 Amendment 4 §결정 5 | 재발0(예방적 추가, 증거 없음) |
| story-section-9-typed | warning | 0 | ADR-044 | 재발0(예방적 추가, 증거 없음) |
| story-section-ownership | warning | 0 | ADR-031 | 재발0(예방적 추가, 증거 없음) |
| superpowers-integration | warning | 0 | ADR-028 / CFP-113 | 재발0(예방적 추가, 증거 없음) |
| superpowers-schema-drift | warning | 0 | ADR-028 / CFP-121 | 재발0(예방적 추가, 증거 없음) |
| ubiquitous-language-drift-check | warning | 0 | ADR-091 | 재발0(예방적 추가, 증거 없음) |
| workflow-version-drift | warning | 0 | ADR-032 | 재발0(예방적 추가, 증거 없음) |
| wrapper-template-managed-coverage | warning | 0 | ADR-027 | 재발0(예방적 추가, 증거 없음) |
| write-permission-redistribution | warning | 0 | CFP-26 / ADR-009 (write 권한 invariant) | 재발0(예방적 추가, 증거 없음) |
