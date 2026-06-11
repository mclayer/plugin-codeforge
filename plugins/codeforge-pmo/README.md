# codeforge-pmo

[`codeforge`](https://github.com/mclayer/plugin-codeforge) ζ arc CFP-36 — PMO (Project Management Office) lane plugin.

PMOAgent 단독 — Epic 분해 자문 · Story 완료 회고 · Cross-Story 패턴 분석 · ADR 후보 발의. ζ arc writer-distributed 모델에 따라 docs/retros/** + Story §11 + Epic milestone 직접 write.

## Dependencies

**필수**: [`codeforge@mclayer`](https://github.com/mclayer/plugin-codeforge) (>= 1.0.0). 단독 동작 불가 — codeforge wrapper의 Orchestrator가 PMOAgent를 스폰하고 pmo_output v1 contract로 결과 수령.

본 plugin의 SessionStart hook이 codeforge core 설치 여부 verify. 미설치 시 fail-fast + install 안내.

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
    "codeforge-pmo@mclayer": true
  }
}
```

또는 CLI:

```
/plugins install codeforge@mclayer
/plugins install codeforge-review@mclayer
/plugins install codeforge-pmo@mclayer
```

## Architecture

PMOAgent (Cross-cutting agent — 단일 lane gate에 무관) 가 다음 트리거에 자체 실행:
- **Epic 창설 시** (1회): scope 분해 자문 — Story 분해·의존성 식별·병렬/순차 판정
- **Story 완료 시**: 회고 감사 — Preflight/Gate 준수·§8/§8.5 매핑·FIX evidence pack 완성도·토큰 예산
- **사용자 요청 시** (주기적): Cross-Story 패턴 보고서 — FIX 반복 유형·ESCALATE 트렌드·성능 회귀·코드 핫스팟

각 트리거마다 docs/retros/<sprint>.md direct write + Story §11 mirror + GitHub Epic milestone 갱신. 패턴 발견 시 ADR 후보 발의 → codeforge-design (CFP-40) 또는 wrapper의 ArchitectAgent에 hand-off.

## Inter-plugin Contract

`pmo_output v1` — `mclayer/plugin-codeforge-pmo/docs/inter-plugin-contracts/pmo-output-v1.md` (canonical). codeforge wrapper에 sibling reference 동기 의무 (CFP-24 marketplace sync 정책 유사).

## ζ arc 위치

CFP-36 — codeforge ζ arc 두 번째 lane plugin (review v2 retrofit 다음). 본 plugin이 가장 작은 lane이라 writer-distributed 패턴의 두 번째 검증 단계로 채택 (parent spec [CFP-31 §5.6](https://github.com/mclayer/plugin-codeforge/blob/main/docs/superpowers/specs/2026-04-29-cfp-31-wrapper-only-decomposition-design.md)).
