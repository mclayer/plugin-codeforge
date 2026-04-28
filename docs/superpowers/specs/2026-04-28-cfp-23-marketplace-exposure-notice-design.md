# CFP-23: `mclayer` marketplace 노출 사실 README/CHANGELOG 명시 — spec

## 1. 요건 (사용자 결정 정렬)

- marketplace name = `mclayer` (사용자 명시)
- 네이밍 규약: `mclayer/plugin-<X>` repo = `<X>` plugin = install identifier `<X>@mclayer` (사용자 명시)
- 별도 wrapper 리포 (ii 패턴): `mclayer/marketplace` 신설 (사용자 명시 — bootstrap 외부 commit으로 처리됨)
- codeforge 리포 측 후속: README/CHANGELOG에 marketplace 노출 사실 명시 (본 spec 대상)

## 2. 배경

`mclayer/plugin-codeforge`는 v0.14.1까지 marketplace 노출 부재 상태로 release됨. 사용자는 `extraKnownMarketplaces`에 GitHub 원본 좌표(`mclayer/plugin-codeforge`)를 직접 등록해야 했고, `/plugins install codeforge@<marketplace>` 형태로 부를 marketplace 식별자가 없었다.

2026-04-28 `mclayer/marketplace` wrapper 리포 신설(commit `a7a708c`)로 단일 진입점 확보. 본 Story는 그 사실을 codeforge 리포 측 사용자 facing 문서(README + CHANGELOG)에 반영.

## 3. 비목표

- marketplace 리포 측 README/spec/plan (bootstrap commit에서 이미 처리)
- cross-repo version parity CI 자동화 (후속 CFP 후보)
- README의 stale 항목 cleanup (23→24 agent count, v0.7.0 line, agent 다이어그램 DataMigrationArch 누락) — 별도 CFP 후보. 본 spec은 install 섹션만 narrow 변경
- plugin 분리 의제 (Apr 27 audit 결과 복원) — 별도 CFP 후보

## 4. 결정사항

| 항목 | 결정 |
|---|---|
| 패턴 | plugin-meta-na (ADR-005) — production code 0 변경, §8/§9 N/A, 단일 PR |
| 버전 bump | 0.14.1 → **0.14.2** (PATCH — Non-BREAKING release event for documentation) |
| migration-guide entry | 불필요 (Non-BREAKING — invariant-check Step 7은 BREAKING만 trigger) |
| README 변경 범위 | `### 1. 플러그인 설치` 섹션 only. 다른 stale 항목은 별도 cleanup |
| CHANGELOG entry | 최상단 prepend `## [0.14.2] - 2026-04-28` + `### CFP-23 — mclayer marketplace 노출` |
| Story 강제 여부 | 강제 (CLAUDE.md cutoff: "Breaking change · consumer migration 영향" 카테고리 — Non-BREAKING이지만 install 경로 변경은 consumer 측 이주 가이드 필요) |

## 5. 산출물

- `.claude-plugin/plugin.json` — `version`: 0.14.1 → 0.14.2
- `CHANGELOG.md` — 최상단 새 entry
- `README.md` — install 섹션 (마켓플레이스 등록 명령 + `~/.claude/settings.json` 영구 등록 예시)
- `docs/stories/CFP-23.md` — Story file
- `docs/superpowers/specs/<본 파일>` + `docs/superpowers/plans/<plan>`

## 6. 사용자 영향

- **신규 사용자**: README install 섹션의 `/plugins marketplace add mclayer/marketplace` + `/plugins install codeforge@mclayer` 단계 따라 설치
- **기존 사용자**(GitHub 원본 좌표 직접 등록): 영향 없음. CHANGELOG `Migration` 섹션이 권장 이주 경로(`extraKnownMarketplaces.mclayer` source) 명시. 강제 이주 아님

## 7. 위험 / 가정

- 가정: `mclayer/marketplace` 리포 main branch에서 raw fetch 가능 (확인됨 — bootstrap commit 직후 raw URL HTTP 200)
- 가정: marketplace.json `plugins[name=codeforge].version`이 plugin.json `version`과 일치 — bootstrap 시 0.14.1로 설정. 본 PR로 0.14.2 bump 시 marketplace.json 측은 후속 cross-repo CI에서 처리 (또는 marketplace 리포에 별도 PR — 본 PR 범위 외)
- 위험: marketplace.json `plugins[].version` drift — 본 PR 머지 후 marketplace 리포에서 0.14.2로 동기화 PR 별도 필요. 사람 의무에 의존. cross-repo CI 후속 CFP가 mitigate 후보

## 8. invariant-check pre-push 자가 검증 (playbook §3B.5)

본 PR이 plugin-meta-na 패턴이므로 push 직전 author 의무:

- **Step 5** (plugin.json ↔ CHANGELOG version match):
  - `jq -r '.version' .claude-plugin/plugin.json` → `0.14.2`
  - `grep -oE '^## \[[0-9]+\.[0-9]+\.[0-9]+\]' CHANGELOG.md | head -1` → `## [0.14.2]`
  - PASS 예상
- **Step 3** (agent count): agents/*.md 24개 ↔ CLAUDE.md "24 core 에이전트" — 본 PR 미변경 → PASS
- **Step 7** (migration-guide BREAKING parity): 본 release Non-BREAKING → trigger 안 됨 → PASS
- 기타 Step 1·2·4·6·8: 본 PR 미변경 영역 → PASS 예상
