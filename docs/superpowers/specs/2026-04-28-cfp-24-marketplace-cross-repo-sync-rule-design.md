# CFP-24: Marketplace cross-repo 동기화 의무 정식 잠금 — spec

## 1. 요건 (사용자 verbatim 정렬)

> 앞으로 codeforge의 플러그인 의존성은 marketplace에 걸쳐서 marketplace에 반영이 필요한 수정 내용이 있다면 반드시 marketplace까지 그 변경이 반영되도록 하세요.

## 2. 배경

CFP-23(2026-04-28) `mclayer/marketplace` 단일 진입점 노출 시작 — `mclayer/plugin-codeforge` 리포의 `.claude-plugin/plugin.json`과 `mclayer/marketplace` 리포의 `.claude-plugin/marketplace.json`이 같은 의미의 필드(name·version·description·author)를 동시 보유하게 됨. drift surface 신규 발생.

CFP-23 머지 직후 PR `mclayer/marketplace#1` 수동 sync(0.14.1 → 0.14.2)로 첫 패턴 정립. 그러나 이는 1회 실증일 뿐 정식 SSOT 규칙으로 묶이지 않음. 사용자가 본 규칙 명시로 lock-in 요구.

## 3. 비목표

- cross-repo parity CI 자동화 — 별도 CFP(잠정 CFP-25 후보)
- ADR 격상 — 자동화 메커니즘 정립 시 검토
- marketplace.json schema 확장 — Anthropic upstream 결정에 의존
- 다른 mirrored 필드(예: `homepage`·`repository`) 추가 — schema가 그렇게 변경되는 시점에 본 규칙도 갱신

## 4. 결정사항

| 항목 | 결정 |
|---|---|
| 패턴 | plugin-meta-na (ADR-005) — production code 0 변경, §8/§9 N/A, 단일 PR |
| Mirrored 필드 정의 | `name` · `version` · `description` · `author` (4종) — marketplace.json `plugins[]` schema와 plugin.json schema 양쪽 모두 정의된 필드 |
| 비-mirrored 필드 | `keywords` (marketplace.json schema에 없음) — 변경해도 sync 면제 |
| 의무 절차 | (a) codeforge PR 작성 시 mirrored 필드 변경 점검 (b) 변경 시 PR 본문/Story §11에 sync PR 의무 명시 (c) codeforge PR merge → 즉시 marketplace sync PR open·merge (d) gh API cross-check |
| 잠금 위치 | `CLAUDE.md` `## Plugin` 섹션 하위 `### Marketplace cross-repo 동기화 의무` subsection (1 layer down) |
| 버전 bump | 0.14.2 → **0.14.3** (PATCH — Non-BREAKING SSOT 추가) |
| migration-guide entry | 불필요 (Non-BREAKING) |
| Story 강제 여부 | 강제 (CLAUDE.md SSOT 의미 변경 카테고리) |
| 본 Story의 marketplace sync 후속 | **의무** — 본 규칙의 첫 self-실증. 머지 직후 `plugins[codeforge].version` 0.14.2 → 0.14.3 sync PR |

## 5. 산출물

- `CLAUDE.md` — `### Marketplace cross-repo 동기화 의무` subsection 신규
- `.claude-plugin/plugin.json` — version 0.14.3
- `CHANGELOG.md` — `[0.14.3]` entry (Added/Why/Migration)
- `docs/stories/CFP-24.md` — Story file
- `docs/superpowers/specs/<본 파일>` + `<plan>`
- 후속 별도 리포 PR: `mclayer/marketplace` marketplace.json sync (Story §11 의무)

## 6. 사용자 영향

- **신규 사용자**: 영향 없음 (정책 추가, 행동 면 영향 없음)
- **codeforge contributor (Claude / 사용자)**: 향후 plugin.json 수정 PR 작성 시 marketplace sync PR 후속 의무 추가 — author/Orchestrator workflow 1단계 추가

## 7. 위험 / 가정

- 가정: marketplace.json schema의 `plugins[]` mirrored 필드는 현재 4종 — Anthropic upstream schema 변경 시 본 규칙 갱신 필요
- 가정: Mirrored 필드는 "값이 항상 같아야 한다"가 아니라 "변경 시 양쪽 모두 검토·갱신". description의 자연스러운 비대칭(codeforge는 더 자세, marketplace는 1줄)은 허용
- 위험: author 망각 → marketplace drift. cross-repo parity CI 미완성 단계에서는 사람의 의무에 의존. 본 Story 첫 실증으로 패턴 정착, 후속 CFP에서 자동 차단

## 8. invariant-check pre-push 자가 검증 (playbook §3B.5)

본 PR이 plugin-meta-na 패턴이므로 push 직전 author 의무:

- **Step 5** (plugin.json ↔ CHANGELOG version match):
  - `jq -r '.version' .claude-plugin/plugin.json` → `0.14.3`
  - `grep -oE '^## \[[0-9]+\.[0-9]+\.[0-9]+\]' CHANGELOG.md | head -1` → `## [0.14.3]`
  - PASS 예상
- **Step 3** (agent count): agents/*.md 24 ↔ CLAUDE.md "24 core 에이전트" — 본 PR 미변경 → PASS
- **Step 7** (BREAKING parity): Non-BREAKING → trigger 안 됨 → PASS
- 기타 Step 1·2·4·6·8: 본 PR 미변경 영역 → PASS 예상
- markdown internal links: CLAUDE.md 신규 subsection의 외부 https:// link만 있으니 internal link broken risk 없음

## 9. 본 규칙의 첫 self-실증 절차 (post-merge)

1. codeforge PR merge (admin override per plugin-meta-na)
2. local main sync
3. cd `mclayer/marketplace` workspace
4. branch `chore/sync-codeforge-0.14.3`
5. marketplace.json `plugins[name=codeforge].version`: 0.14.2 → 0.14.3
6. JSON validate + gh API cross-check (codeforge plugin.json `0.14.3` ↔ marketplace.json `0.14.3`)
7. commit + push + PR + merge
