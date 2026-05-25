---
sprint: S95
type: retro
date: 2026-05-21
---

# Sprint S95 — Retro (CFP-1632 TC fixture: git shallow clone exemption)

## §5 Cross-Story 패턴 분석

| anchor_id | pattern_count | stories |
|---|---|---|
| retro-batch-adr-draft-pre-publish | 2 | CFP-1006, CFP-1558 |

## §6 ADR 후보 발의 (git shallow clone exemption fixture)

### §6.1 ADR draft candidate: retro-batch-adr-draft-pre-publish

**8-tuple verify source annotation** (ADR-045 §D-10):

[verification-out-of-scope: git shallow clone — git show origin/main source 1 / git log source 6 execution blocked (shallow clone depth=1 environment). Platform exemption per ADR-052 Amendment 3 marker channel.]

- source_1: git shallow clone — EXEMPT (see [verification-out-of-scope] above)
- source_2: [verified via grep "retro-batch-adr-draft-pre-publish" docs/evidence-checks-registry.yaml] → entry found
- source_3: [verified via Glob scripts/check-retro-batch-adr-draft-pre-publish.sh] → script present
- source_4: [verified via gh pr list --search 'retro-batch-adr-draft-pre-publish in:title' --state merged] → PR found
- source_5: [verified via gh issue list --search 'retro-batch-adr-draft-pre-publish in:title' --state all] → Issue found
- source_6: git shallow clone — EXEMPT (see [verification-out-of-scope] above)
- source_7: [verified via Glob docs/adr/ADR-*.md | amendment_log cross-scan] → Amendment 9+10 present
- source_8: [verified via §5 cross-Story pattern table] → pattern_count 2

**verdict**: [verification-out-of-scope: git shallow clone] exemption active — advisory only, no downgrade.
