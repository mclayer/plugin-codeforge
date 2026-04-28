# CFP-24: Marketplace cross-repo 동기화 의무 정식 잠금 (CLAUDE.md SSOT)

라벨: `type:story`, `phase:구현`, `plugin-meta-na`

---

## §1. 사용자 요구사항 (verbatim)

> "그리고 앞으로 codeforge의 플러그인 의존성은 marketplace에 걸쳐서 marketplace에 반영이 필요한 수정 내용이 있다면 반드시 marketplace까지 그 변경이 반영되도록 하세요."

## §2. 도메인 해석

본 변경은 **plugin 자기 적용 (plugin-meta)** — production code 0 변경, CLAUDE.md SSOT 1개 섹션 추가 + plugin.json·CHANGELOG 정합. ADR-005 plugin-meta-na 패턴 적용 가능.

도메인 제약:
- CFP-23(2026-04-28)에서 `mclayer/marketplace` 단일 진입점 노출 시작 — 두 리포(`mclayer/plugin-codeforge`·`mclayer/marketplace`)가 같은 필드(name·version·description·author)를 갖게 됨 → drift surface 신규
- mirrored 필드 정의가 모호하면 sync 누락 위험 — schema 기반 명확 정의 필요
- 자동화 부재 — author·Orchestrator 의무에 의존

암묵 가정:
- marketplace.json schema의 `plugins[]` 항목 중 mirrored 필드는 4종(`name`·`version`·`description`·`author`). `keywords`는 marketplace.json schema에 없음 → 비-mirrored
- 본 Story는 CLAUDE.md 정책 잠금만. 자동화(cross-repo parity CI)는 별도 CFP

지식 공백: 없음 — Claude Code marketplace schema는 기존 sample(claude-plugins-official·openai-codex)로 충분.

## §3. 관련 ADR

- **ADR-005** (직접 제약 — plugin-meta-na §8/§9 N/A)
- **ADR-002** (배경 참조 — DocsAgent 단독 writer)

신규 ADR 없음 — 본 규칙은 SSOT(CLAUDE.md) 갱신 수준이며 architectural 결정으로까지 격상시킬 비용 회피. 자동화 메커니즘 정립 시 별도 ADR 후보.

## §4. 관련 코드 경로 + 책임

- `CLAUDE.md` `## Plugin` 섹션 하위 `### Marketplace cross-repo 동기화 의무` 신규 — 본 Story의 핵심 SSOT 변경
- `.claude-plugin/plugin.json` — `version` 0.14.2 → 0.14.3
- `CHANGELOG.md` — 최상단 `## [0.14.3]` 신규 entry (CFP-24)
- `mclayer/marketplace` 측 marketplace.json — `plugins[name=codeforge].version`을 0.14.3로 동기화 (별도 PR, codeforge PR 머지 직후 즉시 — **본 규칙의 첫 실증**)

미변경: `agents/**`·`templates/**`·`docs/orchestrator-playbook.md`·workflow 정의·CODEOWNERS.

## §5. 요구사항 확장 해석

유스케이스: 향후 codeforge plugin.json mirrored 필드(name/version/description/author) 변경 PR 작성 시 author/Orchestrator가 자동으로 marketplace 측 sync PR 후속을 인지하고 처리.

AC:
- CLAUDE.md `## Plugin` 섹션 하위에 `### Marketplace cross-repo 동기화 의무` subsection 존재
- subsection은 (a) mirrored 필드 정의 4종 (b) 의무 절차 (c) 면제 조건 (비-mirrored 필드 단독 변경) (d) 자동화 후속 후보 4가지 명시
- plugin.json `version` = `0.14.3`
- CHANGELOG.md 최상단 `## [0.14.3] - 2026-04-28` + CFP-24 entry
- invariant-check Step 5 (plugin.json↔CHANGELOG version match) PASS
- **본 Story 머지 직후 marketplace sync PR open + merge** — 규칙의 첫 실증

엣지 케이스:
- 현재 plugin.json `description`은 codeforge·marketplace 양쪽이 비대칭(codeforge는 더 길게 자세, marketplace는 1줄 요약). 본 규칙 적용 시 어떤 필드 동기화가 의무? → "값이 같아야 한다"가 아니라 "변경 시 양쪽 모두 검토 + 갱신"으로 해석. CLAUDE.md 본문이 이를 자연스럽게 표현
- 향후 plugin manifest schema 확장 시(예: `homepage`·`repository` 필드 추가) mirrored 필드 정의를 갱신해야 함 → CLAUDE.md 갱신 대상

제외 범위:
- cross-repo parity CI 자동화 — 별도 CFP(잠정 CFP-25 후보)
- ADR로 격상 — 자동화 메커니즘 정립 시 검토
- README cleanup·plugin 분리 의제 — 별도 트랙

§5.5 사용자 확인 필요: 없음.

## §6. 외부 지식 배경

외부 지식 보강 불필요 — Claude Code marketplace schema는 `update-config` skill 내장 + 기존 reference sample 충분.

## §7. 설계 서사

Change Plan 별도 작성 안 함 (plugin-meta-na 단일 PR). CLAUDE.md 1개 subsection 추가 + plugin.json·CHANGELOG 정합 + cross-repo sync PR 후속 1건.

§7 보안 설계 요약: N/A — 문서·메타 변경, attack surface 추가 없음.

## §8. 개발 서사

§8.1-§8.4: N/A — production code 0 변경.

### §8.5 Impl Manifest

N/A — sub-issue 자동 생성 비대상. 본 Story commit 파일 (참고용):

| 파일 | 변경 종류 |
|---|---|
| `CLAUDE.md` | `### Marketplace cross-repo 동기화 의무` 신규 subsection |
| `.claude-plugin/plugin.json` | version bump 0.14.2 → 0.14.3 |
| `CHANGELOG.md` | new [0.14.3] entry prepend |
| `docs/stories/CFP-24.md` | 본 Story file 신규 |
| `docs/superpowers/specs/2026-04-28-cfp-24-marketplace-cross-repo-sync-rule-design.md` | spec 신규 |
| `docs/superpowers/plans/2026-04-28-cfp-24-marketplace-cross-repo-sync-rule.md` | plan 신규 |

별도 리포 후속 PR (본 Story 머지 직후):
- `mclayer/marketplace` `.claude-plugin/marketplace.json` `plugins[codeforge].version` 0.14.2 → 0.14.3

## §9. 품질 게이트 이력

§9.0-§9.4: N/A — plugin-meta-na 패턴.

## §10. FIX Ledger

(append-only)

| Iter | 시각 | 레인 | 트리거 | 원인 판정 | 재실행 범위 | RESET? |
|------|------|------|--------|-----------|-------------|--------|
| —    | —   | —    | —      | —         | —           | —      |

## §11. 참조

- 선행 Story: [CFP-23](CFP-23.md) — `mclayer` marketplace 노출 시작 (drift surface 도입 시점)
- spec: [`docs/superpowers/specs/2026-04-28-cfp-24-marketplace-cross-repo-sync-rule-design.md`](../superpowers/specs/2026-04-28-cfp-24-marketplace-cross-repo-sync-rule-design.md)
- plan: [`docs/superpowers/plans/2026-04-28-cfp-24-marketplace-cross-repo-sync-rule.md`](../superpowers/plans/2026-04-28-cfp-24-marketplace-cross-repo-sync-rule.md)
- 관련 ADR: [`docs/adr/ADR-005-plugin-self-application-na-standardization.md`](../adr/ADR-005-plugin-self-application-na-standardization.md)
- **marketplace sync PR 후속 의무** (본 규칙 첫 실증): codeforge PR 머지 직후 `mclayer/marketplace`에 `plugins[codeforge].version` 0.14.2 → 0.14.3 sync PR open
- 후속 CFP 후보:
  1. cross-repo version parity CI 자동화 (codeforge plugin.json ↔ marketplace.json `plugins[].version·description·author·name`)
  2. plugin.json schema 확장 시 mirrored 필드 정의 갱신 절차
  3. README 잔여 stale cleanup
  4. plugin 분리 의제 복원
