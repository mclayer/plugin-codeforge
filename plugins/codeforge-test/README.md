# codeforge-test

[`codeforge`](https://github.com/mclayer/plugin-codeforge) ζ arc CFP-38 — Test lane plugin.

TestAgent (functional + performance subset 병렬 실행) → test_verdict v1 contract.

## Dependencies

**필수**: [`codeforge@mclayer`](https://github.com/mclayer/plugin-codeforge) (>= 3.0.0). Story §10 FIX Ledger append 는 Orchestrator 단독 (codeforge core CFP-32 monopoly).

## 설치

```jsonc
// ~/.claude/settings.json
{
  "extraKnownMarketplaces": {
    "mclayer": { "source": { "source": "github", "repo": "mclayer/marketplace" } }
  },
  "enabledPlugins": {
    "codeforge@mclayer": true,
    "codeforge-review@mclayer": true,
    "codeforge-pmo@mclayer": true,
    "codeforge-requirements@mclayer": true,
    "codeforge-test@mclayer": true
  }
}
```

## Architecture

TestAgent 는 두 subset 를 병렬 실행:
- **functional**: 단위·통합·인프라 테스트 (consumer overlay 가 러너 지정)
- **performance**: baseline 대비 mean 10% 이상 악화 시 FAIL (consumer overlay 가 baseline 위치 지정)

PASS 시 self-write (phase:구현-테스트 → phase:보안-테스트 transition + comment). FAIL 시 verdict 에 fix_routing_hint 첨부 → Orchestrator 가 §10 append.

## Inter-plugin Contract

`test_verdict v1` — `docs/inter-plugin-contracts/test-verdict-v1.md` (canonical).
