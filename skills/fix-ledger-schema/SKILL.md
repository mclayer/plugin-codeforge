---
name: fix-ledger-schema
description: §10 FIX Ledger 스키마 + RESET 룰 + max FIX 카운터. FIX 루프 트리거 시 root-cause-decision과 함께 Orchestrator 호출 의무. Orchestrator 단독 §10 append 독점 (fix-event-v1 contract).
tools: Read
---

# §10 FIX Ledger 스키마

> 참조 테이블 skill — 내용을 읽고 FIX Ledger 작성에 적용하세요.

## 호출 시점

FIX 루프 트리거 시 (설계리뷰 / 구현리뷰 / 구현테스트 / 보안테스트 FAIL). `codeforge:root-cause-decision`과 함께 호출.

## §10 FIX Ledger 스키마

**카운터 SSOT** = `docs/stories/<KEY>.md` §10 "FIX Ledger" — Orchestrator 단독 관리 ([fix-event-v1](../../docs/inter-plugin-contracts/fix-event-v1.md) contract, CFP-32 monopoly). GitHub Issue 라벨은 보조 (fix-ledger-sync.yml Action mirror).

```
| Iter | 시각 | 레인 | 트리거 | 원인 판정 | 재실행 범위 | RESET? |
|------|------|------|--------|-----------|-------------|--------|
| 1    | ISO8601 | 설계-리뷰   | DesignReviewPL P0 × 2 | 설계 | Change Plan §3 재작성 | — |
| 2    | ISO8601 | 구현-테스트 | 성능 mean +15% | 설계 | Change Plan §3 재작성 | **RESET 구현-리뷰** |
```

상세 룰 (max FIX 횟수 / RESET marker / parallel diagnosis / mechanical fast-path) 은 [playbook §6](../../docs/orchestrator-playbook.md) SSOT.
