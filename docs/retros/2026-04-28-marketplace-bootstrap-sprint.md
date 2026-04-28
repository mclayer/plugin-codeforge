# 2026-04-28 Marketplace Bootstrap Sprint 회고

기간: 2026-04-28 (단일 세션, codex audit closure sprint 직후 연속)
범위: 2 CFP + 2 cross-repo sync PR + 1 신규 리포 bootstrap
선행 retro: [2026-04-28-codex-audit-closure-sprint.md](2026-04-28-codex-audit-closure-sprint.md)

---

## §1 결과 (closure)

### 1.1 commit·PR

| Story / 작업 | PR | merge commit | 비고 |
|---|---|---|---|
| `mclayer/marketplace` 리포 신설 (bootstrap) | (initial commit, no PR) | `a7a708c` | 신규 wrapper 리포. spec/plan 본 리포 내 작성 |
| CFP-23: codeforge 측 marketplace 노출 명시 | [#63](https://github.com/mclayer/plugin-codeforge/pull/63) | `8f9b63e` | plugin-meta-na, v0.14.2 |
| marketplace sync (codeforge 0.14.2) | [mclayer/marketplace#1](https://github.com/mclayer/marketplace/pull/1) | `540656b` | manual sync 첫 사례 |
| CFP-24: cross-repo 동기화 의무 정식 잠금 | [#64](https://github.com/mclayer/plugin-codeforge/pull/64) | `8584503` | plugin-meta-na, v0.14.3, CLAUDE.md SSOT |
| marketplace sync (codeforge 0.14.3) | [mclayer/marketplace#2](https://github.com/mclayer/marketplace/pull/2) | `5b7a51a` | CFP-24 규칙 첫 self-실증 |

### 1.2 영구 산출물

- 신규 GitHub 리포: [`mclayer/marketplace`](https://github.com/mclayer/marketplace) (public)
- 신규 install 경로: `/plugins install codeforge@mclayer` (또는 `extraKnownMarketplaces.mclayer` 영구 등록)
- CLAUDE.md `## Plugin` 하위 `### Marketplace cross-repo 동기화 의무` SSOT 규칙
- mirrored 필드 정의 4종: `name` · `version` · `description` · `author`
- 사용자 메모리: `feedback_marketplace_cross_repo_sync.md`

### 1.3 미머지 대기 / 휘발 없음

본 sprint 산출물 모두 main에 반영 완료 (codeforge·marketplace 양쪽).

---

## §2 핵심 패턴

### 2.1 단일-PR plugin-meta-na 연속 적용

CFP-23·CFP-24 둘 다 ADR-005 plugin-meta-na 패턴(production code 0 변경, §8/§9 lane 면제, 단일 PR + admin override merge). 사전 자가 검증(playbook §3B.5)으로 invariant-check Step 5/3/7 + markdown links + JSON syntax 모두 통과 — push 후 CI fail 없음(첫 commit의 ADR-005 link 오타 1건 제외).

### 2.2 Cross-repo 의존성 신규 도입 → 즉시 SSOT 잠금

CFP-23이 `mclayer/marketplace` 단일 진입점을 만들면서 두 리포의 mirrored 필드 drift surface를 신규 도입. CFP-24가 같은 세션 내에서 그 drift surface를 SSOT(CLAUDE.md)로 잠금 + 첫 self-실증으로 패턴 정착. **drift 도입과 잠금이 같은 sprint에서 순차 처리**된 점이 효율적이었음 (다른 사람/세션이 drift를 발견하기 전에 규칙 수립).

### 2.3 사용자 명시 → 영속화 2-layer

사용자 한 메시지("앞으로 codeforge의 플러그인 의존성은 marketplace에 걸쳐서 ... 반드시 ... 반영되도록 하세요.")를 다음 두 layer에 모두 영속화:
- **Memory** (Claude 세션 간 영속): `feedback_marketplace_cross_repo_sync.md`
- **CLAUDE.md** (모든 에이전트·세션 자동 컨텍스트): `## Plugin` `### Marketplace cross-repo 동기화 의무` subsection

memory만으로는 다른 에이전트가 못 봄 (memory는 main Claude 세션 전용). CLAUDE.md만으로는 사용자 의도 근거(verbatim 인용)가 본문에서 멀어짐. 두 layer 모두 가짐으로써 (a) Claude 자가 행동 (b) 모든 sub-agent·인간 contributor 행동 둘 다 cover.

---

## §3 Open question / 미플래닝 의제

### 3.1 Cross-repo parity CI 미자동화

CFP-24 규칙은 author·Orchestrator의 사람 의무에 의존. 자동 차단 메커니즘은 잠정 CFP-25 후보(retro 시점 기준 미플래닝).

후보 구현:
- codeforge GitHub Actions: PR diff에 `.claude-plugin/plugin.json` 포함 + mirrored 필드 변경 감지 → required status check가 marketplace PR linked 검증
- marketplace 측: PR merge 후 codeforge plugin.json fetch → version mismatch 시 fail → 자동 sync PR open

설계 자체는 1 sprint 분량. 단 cross-repo trigger는 GITHUB_TOKEN scope·repo dispatch event 학습 비용 있음.

### 3.2 미플래닝 의제 (memory `project_pending_planning.md` 참조)

1. **plugin 분리 audit (Apr 27 transcript-only)** — 사용자가 `이 전체 플러그인에서 쪼개거나 재사용 가능한 단위가 없을까? codex로도 알아보고 종합해서 알려줘`로 분리 가능성 audit 요청, Explore+Codex 병렬 분석 수행했으나 spec/plan/Story/ADR 어떤 형태로도 산출물 생성 안 됨. retro § 우선순위 후보에도 미등재. 본 retro에서 명시적 backlog 등재.

2. **아이디어 → spec 진입 트리거 비형식화** — 본 plugin의 7-lane 체인은 Issue Form 진입 시점부터 형식화돼 있고, 그 이전 단계(아이디어/audit/제안 → 정식 진입)는 비형식. `type:planning` 라벨 / `docs/planning/` 폴더 / PMOAgent 정기 backlog 감사 모두 부재. retro §4.2가 비형식 backlog 역할. **(a)** `type:planning` Issue 도입 / **(b)** `docs/planning/` 폴더 + audit 결과 정식 등재 절차 / **(c)** PMOAgent 주기 backlog 감사 트리거 — 3 옵션. 후보 CFP.

### 3.3 README 잔여 stale (CFP-23 §5 제외 범위 명시)

- `23 core 에이전트` 3회 (실제는 24, CFP-21 이후)
- `버전 0.7.0` 라인 (현재 0.14.3)
- agent 다이어그램에서 `DataMigrationArchitectAgent` 누락 (CFP-21 신설 deputy)

별도 cleanup CFP 후보 — 영향 범위 제한적이고 사용자 facing 문서이므로 우선순위 medium.

---

## §4 후속 우선순위 권고

| 우선순위 | 작업 | 형태 | Risk | 예상 effort | 근거 |
|---|---|---|---|---|---|
| 1 | **첫 non-meta Story 실증** | consumer 프로젝트 적용 후 production code Story 1건 full 7-lane 실행 | LOW (검증 only) | 1 sprint | 선행 retro §4.2와 동일 — 가장 권고됨. plugin-meta-na 100% 누적 (CFP-19/20/21/22/23/24 6 Story) → ground-truth 부재 |
| 2 | **Cross-repo parity CI 자동화** | CFP-25 후보. codeforge GitHub Actions가 mirrored 필드 변경 감지 + marketplace PR linked 검증 | MED (cross-repo dispatch 학습 비용) | 1 sprint | CFP-24 규칙 자동화 — 사람 의무에서 자동 차단으로 격상. drift 위험 0 |
| 3 | **plugin 분리 의제 복원** | Apr 27 audit 결과 transcript 복원 → spec/plan 트랙 진입 OR 새로 brainstorming | MED (audit 결과 의존) | 2-3 sprint | 본 retro §3.2 의제 1. mclayer marketplace 인프라 갖춰진 시점이라 분리 시 marketplace 추가 등재 비용 낮음 |
| 4 | **README 잔여 cleanup** | 23→24, v0.7.0→링크, 다이어그램 갱신 | LOW (docs only) | 1 commit + Story | 본 retro §3.3 |
| 5 | **플래닝 진입 형식화** | `type:planning` Issue + audit 결과 정식 등재 절차 + PMOAgent 주기 backlog 감사 | MED | 2 sprint | 본 retro §3.2 의제 2. Apr 27 audit 휘발 같은 사례 재발 방지 |

### 4.1 ADR 후보 발의 (PMO trigger 4)

본 sprint cross-story 패턴 분석 결과 신규 ADR **1건 후보**:

- **ADR 후보**: "Cross-repo plugin distribution dependency"
  - **status**: Proposed (자동화 메커니즘 정립 시 Accepted로 격상)
  - **range**: codeforge ↔ marketplace mirrored 필드 4종 + sync 절차 + 자동화 trigger 정의
  - 우선순위 2 작업과 묶어 진행 권고

ADR-005가 plugin-meta-na 패턴을 cover하지만 cross-repo 측면은 cover 안 함 → 별도 ADR이 architectural decision으로 적절.

---

## §5 운영 개선 제안 (다음 세션)

| # | 개선 항목 | 동기 | 적용 시점 |
|---|----------|------|----------|
| 1 | spec 작성 시점에 `mclayer/marketplace`에 대한 영향 평가 1줄 의무 | CFP-23/24 둘 다 spec 작성 후 회고적으로 sync PR을 인지 — spec 시점 표기로 forecast 가능 | 다음 plugin-meta CFP 시작 시 |
| 2 | 다음 세션 시작 시 memory `project_pending_planning.md` 자동 surface (의제 1·2 status 확인) | Apr 27 audit이 transcript-only로 휘발한 사례 재발 방지 | 다음 세션 시작 시점 |
| 3 | retro 시점에 "다음 권고 우선순위" 표를 GitHub Discussions의 backlog 카테고리에 자동 mirror | 비형식 backlog가 retro에만 갇혀 다음 세션이 못 봄 | 우선순위 5 작업과 함께 |

---

## §6 참조

- 선행 retro: [2026-04-28-codex-audit-closure-sprint.md](2026-04-28-codex-audit-closure-sprint.md)
- Stories: [CFP-23](../stories/CFP-23.md) · [CFP-24](../stories/CFP-24.md)
- ADR closure: [ADR-005](../adr/ADR-005-plugin-self-application-na-standardization.md) plugin-meta-na (CFP-23·CFP-24 모두 적용)
- merged PRs:
  - codeforge: [#63](https://github.com/mclayer/plugin-codeforge/pull/63) · [#64](https://github.com/mclayer/plugin-codeforge/pull/64)
  - marketplace: [#1](https://github.com/mclayer/marketplace/pull/1) · [#2](https://github.com/mclayer/marketplace/pull/2)
- 신규 외부 리포: [mclayer/marketplace](https://github.com/mclayer/marketplace)
