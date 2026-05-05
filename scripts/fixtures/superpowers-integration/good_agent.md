# SampleAgent (fixture, good — passes lint)

## superpowers integration

본 agent 의 superpowers skill 호출 지점 = SSOT [`docs/superpowers-integration.md`](../../../docs/superpowers-integration.md) §2 row "design / SampleAgent". 정책 재정의 안 함, link only. superpowers:writing-plans 호출 시 path override fragment 적용.

## 권한 (allowed-tools)

- Read(`<internal-docs-clone>/<plugin-folder>/specs/**`)
- Read(`<internal-docs-clone>/<plugin-folder>/plans/**`)
- Edit(`<internal-docs-clone>/<plugin-folder>/specs/**`)
- Write(`<internal-docs-clone>/<plugin-folder>/specs/**`)
