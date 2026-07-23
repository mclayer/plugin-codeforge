"""
CFP-2810 Phase 2 Test Contract — Concurrency Crosswalk Manifest (SSOT).

128 workflows (128 rows total):
  - Shared (templates + .github): 68
  - Templates-only: 17
  - .github-only: 43

Wired (concurrency changes tracking + cancellation control): 107 rows
  - Class A (cancel==true): 68
  - Class B (cancel==false, state-bearing): 5
  - Class C (cancel==false, schedule): 5
  - Class D (cancel==false, non-mutation): 2
  - Class M (cancel==expr): 27

Not wired: 21 rows (event_class W/F/SKIP, intentionally excluded from AC bijection).
"""

MANIFEST = [
    {"name": "ac-traceability-matrix.yml", "event_class": "P", "side_effect_class": "A", "cancel_spec": "true", "group_shape": "A", "is_d": False, "is_narrow": False, "in_tpl": True, "in_gh": True, "shared": True, "wired": True},
    {"name": "ac-traceability-self-test.yml", "event_class": "P", "side_effect_class": "A", "cancel_spec": "true", "group_shape": "A", "is_d": False, "is_narrow": False, "in_tpl": False, "in_gh": True, "shared": False, "wired": True},
    {"name": "actionlint-check.yml", "event_class": "P", "side_effect_class": "A", "cancel_spec": "true", "group_shape": "A", "is_d": False, "is_narrow": False, "in_tpl": True, "in_gh": True, "shared": True, "wired": True},
    {"name": "actionlint-workflows-test.yml", "event_class": "P", "side_effect_class": "A", "cancel_spec": "true", "group_shape": "A", "is_d": False, "is_narrow": False, "in_tpl": False, "in_gh": True, "shared": False, "wired": True},
    {"name": "active-sessions-presence-check.yml", "event_class": "P", "side_effect_class": "A", "cancel_spec": "true", "group_shape": "A", "is_d": False, "is_narrow": True, "in_tpl": True, "in_gh": True, "shared": True, "wired": True},
    {"name": "adr-citation-slug.yml", "event_class": "P", "side_effect_class": "A", "cancel_spec": "true", "group_shape": "A", "is_d": False, "is_narrow": True, "in_tpl": True, "in_gh": True, "shared": True, "wired": True},
    {"name": "adr-cross-ref-consistency.yml", "event_class": "P", "side_effect_class": "A", "cancel_spec": "true", "group_shape": "A", "is_d": False, "is_narrow": True, "in_tpl": True, "in_gh": True, "shared": True, "wired": True},
    {"name": "adr-digit-width-check.yml", "event_class": "P", "side_effect_class": "A", "cancel_spec": "true", "group_shape": "A", "is_d": False, "is_narrow": False, "in_tpl": False, "in_gh": True, "shared": False, "wired": True},
    {"name": "adr-reservation-claim-test.yml", "event_class": "P", "side_effect_class": "A", "cancel_spec": "true", "group_shape": "A", "is_d": False, "is_narrow": False, "in_tpl": False, "in_gh": True, "shared": False, "wired": True},
    {"name": "adr-reservation-stale-reclaim.yml", "event_class": "S", "side_effect_class": "C", "cancel_spec": "false", "group_shape": "C", "is_d": False, "is_narrow": False, "in_tpl": True, "in_gh": True, "shared": True, "wired": True},
    {"name": "adr-sunset-criteria.yml", "event_class": "P", "side_effect_class": "A", "cancel_spec": "true", "group_shape": "A", "is_d": False, "is_narrow": False, "in_tpl": True, "in_gh": True, "shared": True, "wired": True},
    {"name": "adr-uniqueness-check.yml", "event_class": "P", "side_effect_class": "A", "cancel_spec": "true", "group_shape": "A", "is_d": False, "is_narrow": False, "in_tpl": False, "in_gh": True, "shared": False, "wired": True},
    {"name": "authoring-self-gate-test.yml", "event_class": "M", "side_effect_class": "M", "cancel_spec": "expr", "group_shape": "A", "is_d": False, "is_narrow": False, "in_tpl": False, "in_gh": True, "shared": False, "wired": True},
    {"name": "auto-phase-label.yml", "event_class": "SKIP", "side_effect_class": "-", "cancel_spec": "existing", "group_shape": "existing", "is_d": False, "is_narrow": False, "in_tpl": True, "in_gh": True, "shared": True, "wired": False},
    {"name": "bidirectional-smoke.yml", "event_class": "P", "side_effect_class": "A", "cancel_spec": "true", "group_shape": "A", "is_d": False, "is_narrow": False, "in_tpl": True, "in_gh": True, "shared": True, "wired": True},
    {"name": "bootstrap-labels.yml", "event_class": "SKIP", "side_effect_class": "-", "cancel_spec": "existing", "group_shape": "existing", "is_d": False, "is_narrow": False, "in_tpl": True, "in_gh": True, "shared": True, "wired": False},
    {"name": "bootstrap-whitelist-test.yml", "event_class": "P", "side_effect_class": "A", "cancel_spec": "true", "group_shape": "A", "is_d": False, "is_narrow": False, "in_tpl": False, "in_gh": True, "shared": False, "wired": True},
    {"name": "branch-liveness-test.yml", "event_class": "SKIP", "side_effect_class": "-", "cancel_spec": "existing", "group_shape": "existing", "is_d": False, "is_narrow": False, "in_tpl": False, "in_gh": True, "shared": False, "wired": False},
    {"name": "branch-liveness-watchdog.yml", "event_class": "S", "side_effect_class": "C", "cancel_spec": "false", "group_shape": "C", "is_d": False, "is_narrow": False, "in_tpl": False, "in_gh": True, "shared": False, "wired": True},
    {"name": "bypass-justification-marker.yml", "event_class": "M", "side_effect_class": "M", "cancel_spec": "expr", "group_shape": "A", "is_d": False, "is_narrow": False, "in_tpl": True, "in_gh": True, "shared": True, "wired": True},
    {"name": "bypass-label-counter.yml", "event_class": "SKIP", "side_effect_class": "-", "cancel_spec": "existing", "group_shape": "existing", "is_d": False, "is_narrow": False, "in_tpl": True, "in_gh": True, "shared": True, "wired": False},
    {"name": "cfp2701-story-form-parser-contract-test.yml", "event_class": "P", "side_effect_class": "A", "cancel_spec": "true", "group_shape": "A", "is_d": False, "is_narrow": False, "in_tpl": False, "in_gh": True, "shared": False, "wired": True},
    {"name": "check-plugin-version-bump-self.yml", "event_class": "P", "side_effect_class": "A", "cancel_spec": "true", "group_shape": "A", "is_d": False, "is_narrow": False, "in_tpl": False, "in_gh": True, "shared": False, "wired": True},
    {"name": "check-plugin-version-bump.yml", "event_class": "P", "side_effect_class": "A", "cancel_spec": "true", "group_shape": "A", "is_d": False, "is_narrow": False, "in_tpl": True, "in_gh": False, "shared": False, "wired": True},
    {"name": "claude-md-line-cap.yml", "event_class": "P", "side_effect_class": "A", "cancel_spec": "true", "group_shape": "A", "is_d": False, "is_narrow": False, "in_tpl": True, "in_gh": True, "shared": True, "wired": True},
    {"name": "codex-companion-timeout-check.yml", "event_class": "P", "side_effect_class": "A", "cancel_spec": "true", "group_shape": "A", "is_d": False, "is_narrow": True, "in_tpl": True, "in_gh": True, "shared": True, "wired": True},
    {"name": "confluence-forward-sync.yml", "event_class": "S", "side_effect_class": "C", "cancel_spec": "false", "group_shape": "C", "is_d": False, "is_narrow": False, "in_tpl": False, "in_gh": True, "shared": False, "wired": True},
    {"name": "consumer-deploy-seed.yml", "event_class": "SKIP", "side_effect_class": "-", "cancel_spec": "existing", "group_shape": "existing", "is_d": False, "is_narrow": False, "in_tpl": True, "in_gh": False, "shared": False, "wired": False},
    {"name": "consumer-scripts-manifest.yml", "event_class": "P", "side_effect_class": "A", "cancel_spec": "true", "group_shape": "A", "is_d": False, "is_narrow": False, "in_tpl": False, "in_gh": True, "shared": False, "wired": True},
    {"name": "container-image-scan.yml", "event_class": "W", "side_effect_class": "-", "cancel_spec": "none", "group_shape": "none", "is_d": False, "is_narrow": False, "in_tpl": True, "in_gh": False, "shared": False, "wired": False},
    {"name": "contract-lint.yml", "event_class": "M", "side_effect_class": "M", "cancel_spec": "expr", "group_shape": "A", "is_d": False, "is_narrow": False, "in_tpl": False, "in_gh": True, "shared": False, "wired": True},
    {"name": "cross-layer-impact-check.yml", "event_class": "P", "side_effect_class": "A", "cancel_spec": "true", "group_shape": "A", "is_d": False, "is_narrow": True, "in_tpl": True, "in_gh": True, "shared": True, "wired": True},
    {"name": "css-lint.yml", "event_class": "P", "side_effect_class": "A", "cancel_spec": "true", "group_shape": "A", "is_d": False, "is_narrow": False, "in_tpl": True, "in_gh": True, "shared": True, "wired": True},
    {"name": "decision-principle-vocabulary.yml", "event_class": "P", "side_effect_class": "A", "cancel_spec": "true", "group_shape": "A", "is_d": False, "is_narrow": False, "in_tpl": True, "in_gh": True, "shared": True, "wired": True},
    {"name": "decision-record-disposition-test.yml", "event_class": "M", "side_effect_class": "M", "cancel_spec": "expr", "group_shape": "A", "is_d": False, "is_narrow": False, "in_tpl": True, "in_gh": True, "shared": True, "wired": True},
    {"name": "deferral-carrier-declared.yml", "event_class": "M", "side_effect_class": "M", "cancel_spec": "expr", "group_shape": "A", "is_d": False, "is_narrow": False, "in_tpl": False, "in_gh": True, "shared": False, "wired": True},
    {"name": "deferred-followup-reconcile.yml", "event_class": "M", "side_effect_class": "M", "cancel_spec": "expr", "group_shape": "A", "is_d": False, "is_narrow": False, "in_tpl": False, "in_gh": True, "shared": False, "wired": True},
    {"name": "deferred-item-recovery.yml", "event_class": "P", "side_effect_class": "A", "cancel_spec": "true", "group_shape": "A", "is_d": False, "is_narrow": False, "in_tpl": False, "in_gh": True, "shared": False, "wired": True},
    {"name": "dependency-order-check.yml", "event_class": "P", "side_effect_class": "A", "cancel_spec": "true", "group_shape": "A", "is_d": False, "is_narrow": True, "in_tpl": True, "in_gh": True, "shared": True, "wired": True},
    {"name": "dev-process-metrics-test.yml", "event_class": "M", "side_effect_class": "M", "cancel_spec": "expr", "group_shape": "A", "is_d": False, "is_narrow": False, "in_tpl": False, "in_gh": True, "shared": False, "wired": True},
    {"name": "disjoint-axis-whitelist-lint.yml", "event_class": "M", "side_effect_class": "M", "cancel_spec": "expr", "group_shape": "A", "is_d": False, "is_narrow": False, "in_tpl": False, "in_gh": True, "shared": False, "wired": True},
    {"name": "doc-frontmatter-category-test.yml", "event_class": "P", "side_effect_class": "A", "cancel_spec": "true", "group_shape": "A", "is_d": False, "is_narrow": False, "in_tpl": False, "in_gh": True, "shared": False, "wired": True},
    {"name": "doc-locations-check.yml", "event_class": "M", "side_effect_class": "M", "cancel_spec": "expr", "group_shape": "A", "is_d": False, "is_narrow": False, "in_tpl": False, "in_gh": True, "shared": False, "wired": True},
    {"name": "duplication-check.yml", "event_class": "M", "side_effect_class": "M", "cancel_spec": "expr", "group_shape": "A", "is_d": False, "is_narrow": False, "in_tpl": True, "in_gh": False, "shared": False, "wired": True},
    {"name": "evidence-registry-check-test.yml", "event_class": "P", "side_effect_class": "A", "cancel_spec": "true", "group_shape": "A", "is_d": False, "is_narrow": False, "in_tpl": False, "in_gh": True, "shared": False, "wired": True},
    {"name": "evidence-registry-check.yml", "event_class": "P", "side_effect_class": "A", "cancel_spec": "true", "group_shape": "A", "is_d": False, "is_narrow": False, "in_tpl": True, "in_gh": True, "shared": True, "wired": True},
    {"name": "fable-roster-integrity.yml", "event_class": "P", "side_effect_class": "A", "cancel_spec": "true", "group_shape": "A", "is_d": False, "is_narrow": False, "in_tpl": True, "in_gh": True, "shared": True, "wired": True},
    {"name": "fix-ledger-sync.yml", "event_class": "M", "side_effect_class": "B", "cancel_spec": "false", "group_shape": "A", "is_d": False, "is_narrow": False, "in_tpl": True, "in_gh": False, "shared": False, "wired": True},
    {"name": "force-push-base-advance-check.yml", "event_class": "P", "side_effect_class": "A", "cancel_spec": "true", "group_shape": "A", "is_d": False, "is_narrow": False, "in_tpl": True, "in_gh": True, "shared": True, "wired": True},
    {"name": "governance-remeasure-cron.yml", "event_class": "SKIP", "side_effect_class": "-", "cancel_spec": "existing", "group_shape": "existing", "is_d": False, "is_narrow": False, "in_tpl": True, "in_gh": True, "shared": True, "wired": False},
    {"name": "hard-gate-self-verification-test.yml", "event_class": "M", "side_effect_class": "M", "cancel_spec": "expr", "group_shape": "A", "is_d": False, "is_narrow": False, "in_tpl": True, "in_gh": True, "shared": True, "wired": True},
    {"name": "hook-selftest-execution.yml", "event_class": "P", "side_effect_class": "A", "cancel_spec": "true", "group_shape": "A", "is_d": False, "is_narrow": True, "in_tpl": True, "in_gh": True, "shared": True, "wired": True},
    {"name": "increment-justification.yml", "event_class": "P", "side_effect_class": "A", "cancel_spec": "true", "group_shape": "A", "is_d": False, "is_narrow": False, "in_tpl": True, "in_gh": True, "shared": True, "wired": True},
    {"name": "infra-resource-manifest-drift.yml", "event_class": "M", "side_effect_class": "M", "cancel_spec": "expr", "group_shape": "A", "is_d": False, "is_narrow": False, "in_tpl": True, "in_gh": True, "shared": True, "wired": True},
    {"name": "invariant-check.yml", "event_class": "M", "side_effect_class": "M", "cancel_spec": "expr", "group_shape": "A", "is_d": False, "is_narrow": False, "in_tpl": False, "in_gh": True, "shared": False, "wired": True},
    {"name": "issue-body-claim-pre-screen.yml", "event_class": "S", "side_effect_class": "B", "cancel_spec": "false", "group_shape": "B", "is_d": False, "is_narrow": False, "in_tpl": False, "in_gh": True, "shared": False, "wired": True},
    {"name": "kill-switch-integration-test.yml", "event_class": "W", "side_effect_class": "-", "cancel_spec": "none", "group_shape": "none", "is_d": False, "is_narrow": False, "in_tpl": True, "in_gh": False, "shared": False, "wired": False},
    {"name": "kst-timestamp-display.yml", "event_class": "P", "side_effect_class": "A", "cancel_spec": "true", "group_shape": "A", "is_d": False, "is_narrow": False, "in_tpl": True, "in_gh": True, "shared": True, "wired": True},
    {"name": "lane-count-ssot.yml", "event_class": "M", "side_effect_class": "M", "cancel_spec": "expr", "group_shape": "A", "is_d": False, "is_narrow": False, "in_tpl": False, "in_gh": True, "shared": False, "wired": True},
    {"name": "lane-evidence-check.yml", "event_class": "P", "side_effect_class": "D", "cancel_spec": "false", "group_shape": "A", "is_d": True, "is_narrow": False, "in_tpl": True, "in_gh": True, "shared": True, "wired": True},
    {"name": "lane-evidence-harness-check.yml", "event_class": "M", "side_effect_class": "M", "cancel_spec": "expr", "group_shape": "A", "is_d": False, "is_narrow": False, "in_tpl": False, "in_gh": True, "shared": False, "wired": True},
    {"name": "lexicon-drift-check.yml", "event_class": "P", "side_effect_class": "A", "cancel_spec": "true", "group_shape": "A", "is_d": False, "is_narrow": False, "in_tpl": True, "in_gh": True, "shared": True, "wired": True},
    {"name": "lint.yml", "event_class": "M", "side_effect_class": "M", "cancel_spec": "expr", "group_shape": "A", "is_d": False, "is_narrow": False, "in_tpl": False, "in_gh": True, "shared": False, "wired": True},
    {"name": "live-deploy-approval.yml", "event_class": "W", "side_effect_class": "-", "cancel_spec": "none", "group_shape": "none", "is_d": False, "is_narrow": False, "in_tpl": True, "in_gh": False, "shared": False, "wired": False},
    {"name": "live-secret-policy.yml", "event_class": "W", "side_effect_class": "-", "cancel_spec": "none", "group_shape": "none", "is_d": False, "is_narrow": False, "in_tpl": True, "in_gh": False, "shared": False, "wired": False},
    {"name": "live-test-guard.yml", "event_class": "W", "side_effect_class": "-", "cancel_spec": "none", "group_shape": "none", "is_d": False, "is_narrow": False, "in_tpl": True, "in_gh": False, "shared": False, "wired": False},
    {"name": "marketplace-lag-detect.yml", "event_class": "SKIP", "side_effect_class": "-", "cancel_spec": "existing", "group_shape": "existing", "is_d": False, "is_narrow": False, "in_tpl": False, "in_gh": True, "shared": False, "wired": False},
    {"name": "marketplace-parity.yml", "event_class": "M", "side_effect_class": "M", "cancel_spec": "expr", "group_shape": "A", "is_d": False, "is_narrow": False, "in_tpl": False, "in_gh": True, "shared": False, "wired": True},
    {"name": "mid-flight-marker-check.yml", "event_class": "P", "side_effect_class": "A", "cancel_spec": "true", "group_shape": "A", "is_d": False, "is_narrow": True, "in_tpl": True, "in_gh": True, "shared": True, "wired": True},
    {"name": "operational-outcome-signal-lint.yml", "event_class": "M", "side_effect_class": "M", "cancel_spec": "expr", "group_shape": "A", "is_d": False, "is_narrow": False, "in_tpl": False, "in_gh": True, "shared": False, "wired": True},
    {"name": "orchestrator-autonomy-stop-taxonomy-check.yml", "event_class": "P", "side_effect_class": "A", "cancel_spec": "true", "group_shape": "A", "is_d": False, "is_narrow": True, "in_tpl": True, "in_gh": True, "shared": True, "wired": True},
    {"name": "parallel-epic-conflict-check.yml", "event_class": "P", "side_effect_class": "B", "cancel_spec": "false", "group_shape": "A", "is_d": False, "is_narrow": False, "in_tpl": True, "in_gh": True, "shared": True, "wired": True},
    {"name": "parallel-work-sentinel-check.yml", "event_class": "P", "side_effect_class": "A", "cancel_spec": "true", "group_shape": "A", "is_d": False, "is_narrow": False, "in_tpl": True, "in_gh": True, "shared": True, "wired": True},
    {"name": "path-relocation-consistency.yml", "event_class": "P", "side_effect_class": "A", "cancel_spec": "true", "group_shape": "A", "is_d": False, "is_narrow": True, "in_tpl": True, "in_gh": True, "shared": True, "wired": True},
    {"name": "phase-gate-auto-cleanup.yml", "event_class": "SKIP", "side_effect_class": "-", "cancel_spec": "existing", "group_shape": "existing", "is_d": False, "is_narrow": False, "in_tpl": True, "in_gh": True, "shared": True, "wired": False},
    {"name": "phase-gate-localrefs-test.yml", "event_class": "P", "side_effect_class": "A", "cancel_spec": "true", "group_shape": "A", "is_d": False, "is_narrow": False, "in_tpl": False, "in_gh": True, "shared": False, "wired": True},
    {"name": "phase-gate-mergeable.yml", "event_class": "M", "side_effect_class": "D", "cancel_spec": "false", "group_shape": "A", "is_d": True, "is_narrow": False, "in_tpl": True, "in_gh": True, "shared": True, "wired": True},
    {"name": "phase-label-invariant.yml", "event_class": "P", "side_effect_class": "B", "cancel_spec": "false", "group_shape": "A", "is_d": False, "is_narrow": False, "in_tpl": True, "in_gh": True, "shared": True, "wired": True},
    {"name": "pl-delegation-ratio-check.yml", "event_class": "M", "side_effect_class": "M", "cancel_spec": "expr", "group_shape": "A", "is_d": False, "is_narrow": False, "in_tpl": True, "in_gh": False, "shared": False, "wired": True},
    {"name": "post-deploy-benchmark.yml", "event_class": "W", "side_effect_class": "-", "cancel_spec": "none", "group_shape": "none", "is_d": False, "is_narrow": False, "in_tpl": True, "in_gh": False, "shared": False, "wired": False},
    {"name": "post-deploy-smoke.yml", "event_class": "W", "side_effect_class": "-", "cancel_spec": "none", "group_shape": "none", "is_d": False, "is_narrow": False, "in_tpl": True, "in_gh": False, "shared": False, "wired": False},
    {"name": "post-merge-followup.yml", "event_class": "SKIP", "side_effect_class": "-", "cancel_spec": "existing", "group_shape": "existing", "is_d": False, "is_narrow": False, "in_tpl": True, "in_gh": True, "shared": True, "wired": False},
    {"name": "production-cutover-evidence.yml", "event_class": "SKIP", "side_effect_class": "-", "cancel_spec": "existing", "group_shape": "existing", "is_d": False, "is_narrow": False, "in_tpl": True, "in_gh": True, "shared": True, "wired": False},
    {"name": "rebase-staleness-detection.yml", "event_class": "P", "side_effect_class": "A", "cancel_spec": "true", "group_shape": "A", "is_d": False, "is_narrow": False, "in_tpl": True, "in_gh": True, "shared": True, "wired": True},
    {"name": "reconcile-overlay-workflow-channel-test.yml", "event_class": "P", "side_effect_class": "A", "cancel_spec": "true", "group_shape": "A", "is_d": False, "is_narrow": False, "in_tpl": False, "in_gh": True, "shared": False, "wired": True},
    {"name": "regression-smoke-health-monitor.yml", "event_class": "S", "side_effect_class": "C", "cancel_spec": "false", "group_shape": "C", "is_d": False, "is_narrow": False, "in_tpl": True, "in_gh": True, "shared": True, "wired": True},
    {"name": "requirements-dialog-formalization-presence.yml", "event_class": "P", "side_effect_class": "A", "cancel_spec": "true", "group_shape": "A", "is_d": False, "is_narrow": False, "in_tpl": True, "in_gh": True, "shared": True, "wired": True},
    {"name": "reservation-cleanup.yml", "event_class": "S", "side_effect_class": "C", "cancel_spec": "false", "group_shape": "C", "is_d": False, "is_narrow": False, "in_tpl": True, "in_gh": False, "shared": False, "wired": True},
    {"name": "resource-safety-claim-proof-presence.yml", "event_class": "P", "side_effect_class": "A", "cancel_spec": "true", "group_shape": "A", "is_d": False, "is_narrow": True, "in_tpl": True, "in_gh": True, "shared": True, "wired": True},
    {"name": "responsibility-marker-drift-check.yml", "event_class": "P", "side_effect_class": "A", "cancel_spec": "true", "group_shape": "A", "is_d": False, "is_narrow": False, "in_tpl": True, "in_gh": True, "shared": True, "wired": True},
    {"name": "responsibility-topology-check.yml", "event_class": "P", "side_effect_class": "A", "cancel_spec": "true", "group_shape": "A", "is_d": False, "is_narrow": False, "in_tpl": True, "in_gh": True, "shared": True, "wired": True},
    {"name": "retro-alert-pickup-kpi.yml", "event_class": "SKIP", "side_effect_class": "-", "cancel_spec": "existing", "group_shape": "existing", "is_d": False, "is_narrow": False, "in_tpl": True, "in_gh": True, "shared": True, "wired": False},
    {"name": "retro-mandatory.yml", "event_class": "SKIP", "side_effect_class": "-", "cancel_spec": "existing", "group_shape": "existing", "is_d": False, "is_narrow": False, "in_tpl": True, "in_gh": True, "shared": True, "wired": False},
    {"name": "return-envelope-schema-lint.yml", "event_class": "M", "side_effect_class": "M", "cancel_spec": "expr", "group_shape": "A", "is_d": False, "is_narrow": False, "in_tpl": False, "in_gh": True, "shared": False, "wired": True},
    {"name": "run-hook-crlf-test.yml", "event_class": "P", "side_effect_class": "A", "cancel_spec": "true", "group_shape": "A", "is_d": False, "is_narrow": False, "in_tpl": False, "in_gh": True, "shared": False, "wired": True},
    {"name": "schema-7-principles-check.yml", "event_class": "P", "side_effect_class": "A", "cancel_spec": "true", "group_shape": "A", "is_d": False, "is_narrow": False, "in_tpl": True, "in_gh": True, "shared": True, "wired": True},
    {"name": "self-context-telemetry-allowlist-lint.yml", "event_class": "M", "side_effect_class": "M", "cancel_spec": "expr", "group_shape": "A", "is_d": False, "is_narrow": False, "in_tpl": False, "in_gh": True, "shared": False, "wired": True},
    {"name": "selftest-execution-liveness-test.yml", "event_class": "M", "side_effect_class": "M", "cancel_spec": "expr", "group_shape": "A", "is_d": False, "is_narrow": False, "in_tpl": False, "in_gh": True, "shared": False, "wired": True},
    {"name": "semantic-staleness-detection.yml", "event_class": "P", "side_effect_class": "A", "cancel_spec": "true", "group_shape": "A", "is_d": False, "is_narrow": False, "in_tpl": True, "in_gh": True, "shared": True, "wired": True},
    {"name": "shell-test-exit-masking-detect.yml", "event_class": "P", "side_effect_class": "A", "cancel_spec": "true", "group_shape": "A", "is_d": False, "is_narrow": True, "in_tpl": True, "in_gh": True, "shared": True, "wired": True},
    {"name": "spawn-description-prefix-detect.yml", "event_class": "P", "side_effect_class": "A", "cancel_spec": "true", "group_shape": "A", "is_d": False, "is_narrow": True, "in_tpl": True, "in_gh": True, "shared": True, "wired": True},
    {"name": "spawn-event-schema-lint.yml", "event_class": "M", "side_effect_class": "M", "cancel_spec": "expr", "group_shape": "A", "is_d": False, "is_narrow": False, "in_tpl": False, "in_gh": True, "shared": False, "wired": True},
    {"name": "spawn-prompt-fact-verify.yml", "event_class": "P", "side_effect_class": "A", "cancel_spec": "true", "group_shape": "A", "is_d": False, "is_narrow": False, "in_tpl": False, "in_gh": True, "shared": False, "wired": True},
    {"name": "story-init-trigger-expr-check.yml", "event_class": "P", "side_effect_class": "A", "cancel_spec": "true", "group_shape": "A", "is_d": False, "is_narrow": False, "in_tpl": True, "in_gh": True, "shared": True, "wired": True},
    {"name": "story-init.yml", "event_class": "SKIP", "side_effect_class": "-", "cancel_spec": "existing", "group_shape": "existing", "is_d": False, "is_narrow": False, "in_tpl": True, "in_gh": True, "shared": True, "wired": False},
    {"name": "story-section-1-immutable.yml", "event_class": "P", "side_effect_class": "A", "cancel_spec": "true", "group_shape": "A", "is_d": False, "is_narrow": False, "in_tpl": True, "in_gh": False, "shared": False, "wired": True},
    {"name": "story-section-ownership-check.yml", "event_class": "P", "side_effect_class": "A", "cancel_spec": "true", "group_shape": "A", "is_d": False, "is_narrow": False, "in_tpl": True, "in_gh": True, "shared": True, "wired": True},
    {"name": "story-section-schema.yml", "event_class": "P", "side_effect_class": "A", "cancel_spec": "true", "group_shape": "A", "is_d": False, "is_narrow": False, "in_tpl": True, "in_gh": True, "shared": True, "wired": True},
    {"name": "subagent-wait-liveness-check.yml", "event_class": "P", "side_effect_class": "A", "cancel_spec": "true", "group_shape": "A", "is_d": False, "is_narrow": True, "in_tpl": True, "in_gh": True, "shared": True, "wired": True},
    {"name": "subissue-from-impl-manifest.yml", "event_class": "P", "side_effect_class": "B", "cancel_spec": "false", "group_shape": "A", "is_d": False, "is_narrow": False, "in_tpl": True, "in_gh": False, "shared": False, "wired": True},
    {"name": "test-yaml-ext-fixture.yaml", "event_class": "F", "side_effect_class": "-", "cancel_spec": "none", "group_shape": "none", "is_d": False, "is_narrow": False, "in_tpl": True, "in_gh": False, "shared": False, "wired": False},
    {"name": "test.yml", "event_class": "M", "side_effect_class": "M", "cancel_spec": "expr", "group_shape": "A", "is_d": False, "is_narrow": False, "in_tpl": True, "in_gh": False, "shared": False, "wired": True},
    {"name": "tier-downgrade-guard.yml", "event_class": "P", "side_effect_class": "A", "cancel_spec": "true", "group_shape": "A", "is_d": False, "is_narrow": False, "in_tpl": True, "in_gh": True, "shared": True, "wired": True},
    {"name": "venue-shape-fidelity-presence-check.yml", "event_class": "P", "side_effect_class": "A", "cancel_spec": "true", "group_shape": "A", "is_d": False, "is_narrow": False, "in_tpl": True, "in_gh": True, "shared": True, "wired": True},
    {"name": "verification-floor-check.yml", "event_class": "M", "side_effect_class": "M", "cancel_spec": "expr", "group_shape": "A", "is_d": False, "is_narrow": False, "in_tpl": False, "in_gh": True, "shared": False, "wired": True},
    {"name": "version-3way-atomic.yml", "event_class": "P", "side_effect_class": "A", "cancel_spec": "true", "group_shape": "A", "is_d": False, "is_narrow": False, "in_tpl": True, "in_gh": True, "shared": True, "wired": True},
    {"name": "whitelist-manifest-3way.yml", "event_class": "P", "side_effect_class": "A", "cancel_spec": "true", "group_shape": "A", "is_d": False, "is_narrow": False, "in_tpl": False, "in_gh": True, "shared": False, "wired": True},
    {"name": "windows-bootstrap-smoke.yml", "event_class": "M", "side_effect_class": "M", "cancel_spec": "expr", "group_shape": "A", "is_d": False, "is_narrow": False, "in_tpl": False, "in_gh": True, "shared": False, "wired": True},
    {"name": "wording-baseline-regen.yml", "event_class": "P", "side_effect_class": "A", "cancel_spec": "true", "group_shape": "A", "is_d": False, "is_narrow": False, "in_tpl": False, "in_gh": True, "shared": False, "wired": True},
    {"name": "wording-dictionary.yml", "event_class": "P", "side_effect_class": "A", "cancel_spec": "true", "group_shape": "A", "is_d": False, "is_narrow": False, "in_tpl": True, "in_gh": True, "shared": True, "wired": True},
    {"name": "workflow-permissions-check.yml", "event_class": "P", "side_effect_class": "A", "cancel_spec": "true", "group_shape": "A", "is_d": False, "is_narrow": False, "in_tpl": True, "in_gh": True, "shared": True, "wired": True},
    {"name": "workflow-yaml-parse.yml", "event_class": "P", "side_effect_class": "A", "cancel_spec": "true", "group_shape": "A", "is_d": False, "is_narrow": False, "in_tpl": True, "in_gh": True, "shared": True, "wired": True},
    {"name": "worktree-completion-gate.yml", "event_class": "M", "side_effect_class": "M", "cancel_spec": "expr", "group_shape": "A", "is_d": False, "is_narrow": False, "in_tpl": False, "in_gh": True, "shared": False, "wired": True},
    {"name": "worktree-first-pre-checkout.yml", "event_class": "P", "side_effect_class": "A", "cancel_spec": "true", "group_shape": "A", "is_d": False, "is_narrow": False, "in_tpl": True, "in_gh": True, "shared": True, "wired": True},
    {"name": "worktree-first-pre-commit-main-block.yml", "event_class": "P", "side_effect_class": "A", "cancel_spec": "true", "group_shape": "A", "is_d": False, "is_narrow": False, "in_tpl": True, "in_gh": True, "shared": True, "wired": True},
    {"name": "worktree-first-spawn-evidence-cwd.yml", "event_class": "P", "side_effect_class": "A", "cancel_spec": "true", "group_shape": "A", "is_d": False, "is_narrow": False, "in_tpl": True, "in_gh": True, "shared": True, "wired": True},
    {"name": "wrapper-managed-block.yml", "event_class": "P", "side_effect_class": "A", "cancel_spec": "true", "group_shape": "A", "is_d": False, "is_narrow": False, "in_tpl": True, "in_gh": True, "shared": True, "wired": True},
    {"name": "wrapper-template-managed-coverage.yml", "event_class": "P", "side_effect_class": "A", "cancel_spec": "true", "group_shape": "A", "is_d": False, "is_narrow": False, "in_tpl": True, "in_gh": True, "shared": True, "wired": True},
]

WIRED = [r for r in MANIFEST if r["wired"]]
SKIP_ROWS = [r for r in MANIFEST if r["event_class"] == "SKIP"]
NOT_WIRED = [r for r in MANIFEST if not r["wired"]]

# Counts
COUNT_TOTAL = len(MANIFEST)
COUNT_SHARED = len([r for r in MANIFEST if r["in_tpl"] and r["in_gh"]])
COUNT_TEMPLATES_ONLY = len([r for r in MANIFEST if r["in_tpl"] and not r["in_gh"]])
COUNT_GH_ONLY = len([r for r in MANIFEST if not r["in_tpl"] and r["in_gh"]])
COUNT_WIRED = len(WIRED)

COUNT_CLASS_A = len([r for r in WIRED if r["side_effect_class"] == "A"])
COUNT_CLASS_B = len([r for r in WIRED if r["side_effect_class"] == "B"])
COUNT_CLASS_C = len([r for r in WIRED if r["side_effect_class"] == "C"])
COUNT_CLASS_D = len([r for r in WIRED if r["side_effect_class"] == "D"])
COUNT_CLASS_M = len([r for r in WIRED if r["side_effect_class"] == "M"])

COUNT_EVENT_P = len([r for r in MANIFEST if r["event_class"] == "P"])
COUNT_EVENT_S = len([r for r in MANIFEST if r["event_class"] == "S"])
COUNT_EVENT_M = len([r for r in MANIFEST if r["event_class"] == "M"])

COUNT_NARROW = len([r for r in MANIFEST if r["is_narrow"]])
COUNT_IS_D = len([r for r in MANIFEST if r["is_d"]])

# Convenience selectors
CLASS_A_ROWS = [r for r in WIRED if r["side_effect_class"] == "A"]
CLASS_B_ROWS = [r for r in WIRED if r["side_effect_class"] == "B"]
CLASS_C_ROWS = [r for r in WIRED if r["side_effect_class"] == "C"]
CLASS_D_ROWS = [r for r in WIRED if r["side_effect_class"] == "D"]
CLASS_M_ROWS = [r for r in WIRED if r["side_effect_class"] == "M"]

NARROW_ROWS = [r for r in MANIFEST if r["is_narrow"]]
IS_D_ROWS = [r for r in MANIFEST if r["is_d"]]

def resolve_path(row):
    """Resolve workflow file path from manifest row."""
    if row["in_gh"]:
        return f".github/workflows/{row['name']}"
    elif row["in_tpl"]:
        return f"templates/github-workflows/{row['name']}"
    else:
        raise ValueError(f"Row {row['name']} has no path (not in_tpl or in_gh)")

def is_class_a(row):
    """Check if row is Class A (mutation-bearing state change)."""
    return row["side_effect_class"] == "A" and row["wired"]
