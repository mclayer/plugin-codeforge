# CFP-23: `mclayer` marketplace 노출 사실 README/CHANGELOG 명시

라벨: `type:story`, `phase:구현`, `plugin-meta-na`

---

## §1. 사용자 요구사항 (verbatim)

> "marketplace는 mclayer가 좋겠다."
>
> "요건이 명확해 brainstorming은 필요 없겠다. mclayer 내 plugin-xxx로 이름 붙이면 플러그인이고 이때 플러그인의 이름은 xxx이다."
>
> "생성하고 (ii)로 진행하고 marketplace리포에 두자"
>
> "진행"

(상기 4건 연속 결정 — marketplace 패턴 (ii) 별도 wrapper 리포 신설은 [`mclayer/marketplace`](https://github.com/mclayer/marketplace) bootstrap commit `a7a708c`로 외부 처리 완료. 본 Story는 후속 #1: codeforge 리포 측에 marketplace 노출 사실을 README/CHANGELOG에 명시 + plugin.json version bump.)

## §2. 도메인 해석

본 변경은 **plugin 자기 적용 (plugin-meta)** — production code 0 변경, 문서·메타만 갱신. ADR-005 plugin-meta-na 패턴 적용 가능 (§8 Test Contract N/A · §9 lane 게이트 N/A · 단일 PR).

도메인 제약:
- plugin.json `version` ↔ CHANGELOG.md 최상단 `## [N.N.N]` header parity (invariant-check Step 5)
- README install 명령은 사용자 입장 정보 — 양 마스터(코드포지 README + marketplace README) drift 가능. 본 Story는 codeforge 측만 갱신, marketplace 측은 bootstrap commit에서 이미 처리됨

암묵 가정:
- marketplace name=`mclayer` 결정 사용자 명시
- 네이밍 규약 `mclayer/plugin-<X>` = `<X>` plugin 사용자 명시 (본 Story 대상 plugin = codeforge)
- v0.14.2는 PATCH bump (release event 동반 문서 갱신, BREAKING 아님 — migration-guide 항목 불필요)

지식 공백: 없음.

## §3. 관련 ADR

- **ADR-005** (직접 제약 — plugin-meta-na §8/§9 N/A)
- **ADR-002** (배경 참조 — DocsAgent 단독 writer)

신규 ADR 없음.

## §4. 관련 코드 경로 + 책임

- `.claude-plugin/plugin.json` — `version` 필드 0.14.1 → 0.14.2
- `CHANGELOG.md` — 최상단에 `## [0.14.2] - 2026-04-28` 신규 entry (CFP-23)
- `README.md` — `### 1. 플러그인 설치` 섹션: `<marketplace>` placeholder → 실제 `mclayer` + 영구 등록 예시 추가

`templates/**` · `agents/**` · `CLAUDE.md` · `docs/orchestrator-playbook.md` · workflow 미변경.

## §5. 요구사항 확장 해석 (RequirementsAnalyst — 본 plugin-meta-na는 Analyst 미스폰, PL 자가 정리)

유스케이스: 신규 사용자가 codeforge 설치 시 GitHub 원본 좌표를 직접 등록하는 대신 `mclayer/marketplace`를 통해 일괄 등록 가능.

AC:
- README의 install 섹션이 `<marketplace>` placeholder 없이 구체적 `mclayer` 명시
- CHANGELOG.md 최상단이 `## [0.14.2] - 2026-04-28` 이고 CFP-23 entry 포함
- `.claude-plugin/plugin.json` `version` = `0.14.2`
- invariant-check Step 5 (plugin.json↔CHANGELOG version match) PASS
- `python3 -m json.tool` 양쪽 (plugin.json·marketplace.json — marketplace.json은 본 PR 비대상이지만 reference parity check) 통과

엣지 케이스:
- 기존 사용자(직접 GitHub 좌표 등록): 영향 없음 (CHANGELOG `Migration` 섹션이 명시)
- marketplace name 충돌: 없음 (mclayer는 신규 marketplace, claude-plugins-official / openai-codex와 식별자 분리)

제외 범위:
- README의 stale "23 core 에이전트" 문구 (CFP-21 이후 24)·v0.7.0 문구·DataMigrationArch 누락된 agent 구조 다이어그램 — **본 Story 비대상** (별도 cleanup CFP 후보)
- marketplace 측 README/spec/plan은 bootstrap commit에서 이미 처리됨
- cross-repo version parity CI (codeforge plugin.json ↔ marketplace.json plugins[].version)는 후속 CFP 후보

§5.5 사용자 확인 필요: 없음.

## §6. 외부 지식 배경 (Researcher — 본 plugin-meta-na는 Researcher 미스폰)

외부 지식 보강 불필요 — Claude Code marketplace 메커니즘은 `update-config` skill 스키마 + 기존 `claude-plugins-official` / `openai-codex` 마켓플레이스 sample로 충분히 cover됨.

## §7. 설계 서사

Change Plan 별도 작성 안 함 (plugin-meta-na 단일 PR). 변경 의도는 §4 코드 경로 직접 매핑.

ADR-005 §"적용 범위": "plugin self-application 한정. production code 0 변경 + lane 게이트 의미 없음" 충족.

§7 보안 설계 요약: N/A — 문서·메타 변경, attack surface 추가 없음.

## §8. 개발 서사

### §8.1-§8.4

N/A — production code 0 변경. plugin-meta-na 패턴.

### §8.5 Impl Manifest

N/A — sub-issue 자동 생성 비대상 (§8.5 매핑표가 sub-issue trigger인데 plugin-meta-na는 코드 sub-issue 단위가 의미 없음).

본 Story가 commit하는 파일 (참고용):

| 파일 | 변경 종류 |
|---|---|
| `.claude-plugin/plugin.json` | version bump |
| `CHANGELOG.md` | new entry prepend |
| `README.md` | install 섹션 갱신 |
| `docs/stories/CFP-23.md` | 본 Story file 신규 |
| `docs/superpowers/specs/2026-04-28-cfp-23-marketplace-exposure-notice-design.md` | spec 신규 |
| `docs/superpowers/plans/2026-04-28-cfp-23-marketplace-exposure-notice.md` | plan 신규 |

## §9. 품질 게이트 이력

### §9.0 Clarification 재스폰 이력

없음.

### §9.1 설계 리뷰

N/A — plugin-meta-na 패턴.

### §9.2 구현 리뷰

N/A — plugin-meta-na 패턴.

### §9.3 구현 테스트

N/A — production code 0 변경.

### §9.4 보안 테스트

N/A — attack surface 추가 없음.

## §10. FIX Ledger

(append-only — FIX 발생 시 행 추가)

| Iter | 시각 | 레인 | 트리거 | 원인 판정 | 재실행 범위 | RESET? |
|------|------|------|--------|-----------|-------------|--------|
| —    | —   | —    | —      | —         | —           | —      |

현재까지 FIX 없음.

## §11. 참조

- 선행 작업: `mclayer/marketplace` bootstrap commit `a7a708c` (https://github.com/mclayer/marketplace)
- spec: [`docs/superpowers/specs/2026-04-28-cfp-23-marketplace-exposure-notice-design.md`](../superpowers/specs/2026-04-28-cfp-23-marketplace-exposure-notice-design.md)
- plan: [`docs/superpowers/plans/2026-04-28-cfp-23-marketplace-exposure-notice.md`](../superpowers/plans/2026-04-28-cfp-23-marketplace-exposure-notice.md)
- 관련 ADR: [`docs/adr/ADR-005-plugin-self-application-na-standardization.md`](../adr/ADR-005-plugin-self-application-na-standardization.md)
- GitHub Issue URL: (PR 머지 후 추가)
- PR URL: (open 후 추가)
- 후속 CFP 후보:
  1. cross-repo version parity CI (codeforge plugin.json ↔ marketplace.json plugins[].version)
  2. README cleanup (23→24 agent count · v0.7.0 → CHANGELOG link · 다이어그램 DataMigrationArch 추가)
  3. plugin 분리 의제 복원 (Apr 27 audit 결과)
