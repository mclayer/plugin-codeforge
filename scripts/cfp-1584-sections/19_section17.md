## 17. Inter-plugin contract sibling sync 절차 (CFP-408 / ADR-010 Amendment 3)

### 17.1 호출 방식

inter-plugin contract version bump 발생 시 Orchestrator 는 manual 3 PR 패턴 대신 `scripts/sync-contract-bump.sh` standard tool 호출.

```bash
# 1단계: dry-run 으로 plan 검토 (의무)
bash scripts/sync-contract-bump.sh <contract> <new-version> --dry-run

# 2단계: real-run (wrapper sibling stage 자동화)
bash scripts/sync-contract-bump.sh <contract> <new-version>
```

`<contract>` = `MANIFEST.yaml` `contracts[].name` (예: `review-verdict`, `design-output`). kind:registry (label-registry, debate-protocol, fix-event 등) 는 본 script 적용 외 — exit 3 + 명시적 reject.

### 17.2 3-stage sequence

| Stage | Repo | 자동화 | 비고 |
|-------|------|--------|------|
| 1 | wrapper (mclayer/plugin-codeforge) | ✅ (script real-run) | branch + commit + push + `gh pr create` |
| 2 | canonical (lane plugin repo) | ❌ (수동) | 본 script 는 plan 출력만; 수동 clone + commit + PR |
| 3 | marketplace (mclayer/marketplace) | ❌ (수동) | `plugin.json` `version` 변경 동반 시만 |

Phase 2 follow-up CFP 에서 canonical clone + commit + PR 자동화 확장 검토.

### 17.3 Merge order strict

**canonical → wrapper sibling → marketplace.** MAJOR bump 시 canonical-first 의무 (ADR-010 Amendment 2). script 가 MANIFEST Active file 명에서 vN 추출 → 자동 감지 → PR body footer 자동 삽입.

병렬 epic 환경에서는 `merge-order:1/2` label (ADR-050) 동시 사용. cross-section conflict (inter-plugin-contracts / label-registry / MANIFEST.yaml 동시 수정) 시 `conflict:{contract-overlap,registry-bump-overlap}` 라벨 (ADR-050 Amendment 1, CFP-534) 자동 부착 — lower CFP 선행 merge.

### 17.4 Test harness

`scripts/test-sync-contract-bump.sh` — 8 scenario × 18 assertion (usage / --help / unknown contract / invalid version / dry-run preview / kind:registry reject / dry-run idempotency). PR-time CI 통합 미적용 (Phase 2 — ADR-060 evidence-check registry 등록 시 promote).

---

