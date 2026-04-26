---
title: v0.9 Review 워커 정의 보강 + Plugin Self-Application 정책 도입
slug: cfp-1-review-polish-and-self-application
status: draft
author: ClaudeOrchestrator (brainstorming-derived)
reviewers: [user, DesignReviewPLAgent]
related_adrs: [ADR-001-review-agent-unification]
created: 2026-04-26
story: CFP-1
---

## §1. 목적

ADR-001 (review-agent-unification) 통합 직후의 두 가지 후속 gap을 한 변경에 묶어 처리한다.

1. **운영 gap** — 통합된 lane-agnostic 워커(`ClaudeReviewAgent` · `CodexReviewAgent`)가 실제 PL packet을 받았을 때의 robustness가 부족 (lane-conditional 검증 부재 / lane별 진단 가이드 부재 / dedup 보조 형식 부재 / 회귀 힌트 부재 / failure mode 처리 부재)
2. **거버넌스 gap** — Plugin 자체가 자기 워크플로우(`docs/stories/<KEY>.md` 의무 + Story 단위 작업 분해)를 dogfooding하지 않음. 최근 commit 패턴 (`1298e0f`, `3d2bfb2`)이 모두 Story 없이 chore/feat — Plugin이 자기에게 정책 적용 안 하면 consumer에게도 약한 신호

본 변경 자체가 거버넌스 정책 도입 + 그 정책의 첫 적용 사례로서 dogfooding 시작점.

### 수용 기준

- `agents/ClaudeReviewAgent.md` · `agents/CodexReviewAgent.md` packet 검증·lane별 진단·dedup·회귀·failure mode 항목 보강 완료
- `CLAUDE.md`에 "Story 작성 의무" 일반 정책 섹션 + "Plugin 자체 적용" 하위 섹션 존재
- `docs/project-config-schema.md`에 consumer overlay 확장 키 (`story_cutoff.additional_exempt_categories`) 명시
- `docs/stories/CFP-1.md` 존재 (본 Change Plan과 매핑)
- `docs/stories/` 디렉토리 신설 — Plugin 자체 dogfooding 1단계 인프라

## §2. 현재 구조 분석

### 2.1 Plugin repo dogfooding 인프라 부재

- `docs/stories/` 디렉토리 부재
- `.github/workflows/`에 plugin templates에서 정의한 6종 (story-init.yml, phase-label-invariant.yml, story-section-1-immutable.yml, subissue-from-impl-manifest.yml, phase-gate-mergeable.yml, fix-ledger-sync.yml) 부재 — `lint.yml`, `test.yml`만 존재
- `.github/ISSUE_TEMPLATE/` 디렉토리 비어 있음
- 즉 plugin이 정의한 거버넌스를 자기 자신에게 적용 안 함

### 2.2 v0.9 Review 워커 통합 직후 상태

ADR-001로 6 워커(3 lane × 2 vendor) → 2 워커(`ClaudeReviewAgent` · `CodexReviewAgent`)로 통합. 도메인은 PL packet 주입. 그러나:

- `ClaudeReviewAgent.md`에 lane별 진단 가이드 부재 (CodexReviewAgent에는 lane=design/code/security 각 focus prompt 존재 → 비대칭)
- Packet 검증이 "필수 필드 존재"만 — lane↔checklist 일치 / lane=design ADR 입력 / lane=code Story §8.5 접근성 / lane=security 1차 layer inline 미검증
- `WebSearch` · `WebFetch` 권한이 모든 lane에서 열려 있음 — design/code lane에서 외부 검색 의미 없음
- Failure mode 처리(네트워크 차단 / scope_globs 0건 / 대상 파일 부재) 미명시
- 회귀 정보(P0·P1 finding의 "1차 원인 가정 = 설계/구현") 보고 스키마 부재 → PL synthesizer가 회귀 lane 분류 어려움
- title/body 자유 형식 → review-pl-base.md §3 dedup(`location + category` 키) 정확도 저하 가능

### 2.3 ADR-001 결정 자체는 유지

본 변경은 ADR-001 결정(2 워커 lane-agnostic)을 **운영 수준에서 강화**. 통합 구조 자체는 건전.

### 2.4 Mapper 변호 근거

기존 코드/문서를 보존하자는 Mapper 입장: "ADR-001 통합이 방금 끝났고 워커 .md는 lane-agnostic 골격이 명확. 추가 보강 불필요, polish는 시간 두고 발견되는 결함마다 점진적 처리 가능."

## §3. 도입할 설계

### 3.1 Mapper vs Refactor 대립 결론

채택: **Refactor 우세**.

근거:
- ADR-001은 *구조* 결정. lane-agnostic 워커가 PL packet을 받았을 때의 *운영 robustness*는 별개 문제
- 보강 부재 시 매 PL이 동일 boilerplate를 packet에 작성 → 운영 손실 누적
- dedup·회귀 분류 정확도 저하 → FIX 루프 효율 저하
- Plugin 거버넌스 정책 부재는 즉시 누적 비용(consumer 동작 모방 약화) → 정책 시점이 명확할수록 좋음

Mapper 우려는 §5 변경 계획 범위를 "워커 .md + CLAUDE.md 정책 신설 + docs/stories/ 디렉토리 + schema 확장"으로 한정해 흡수 (전역 리팩토링·인프라 2단계 분리).

### 3.2 Review 워커 정의 보강 (이미 적용됨, +84/-11)

#### `agents/ClaudeReviewAgent.md` (+61/-8)

| # | 항목 | 위치 |
|---|---|---|
| 1 | Lane별 진단 가이드 (design/code/security 진단 순서 + default 자동 P0 룰) | 신규 §lane별 진단 가이드 |
| 2 | Lane-conditional packet 검증 (lane↔checklist + design ADR + code story_key + security 1차 layer) | §입력 검증 §1-3 |
| 3 | WebSearch/WebFetch lane=security 전용 가드 | §진단 도구 + §제약 |
| 4 | Failure Mode 표 (네트워크/scope 0건/대상 부재/Codex 미설치) | 신규 §Failure Mode |
| 5 | 회귀 힌트 (1차 원인 가정·권장 회귀) | §보고 형식 body |
| 6 | "필수 워커 — fallback 불가" 문구 | 서문 |
| 7 | title/body 형식 고정 ("[<category>] <원인>" + 첫 줄 location·trigger·impact) | §보고 형식 |
| 8 | 토큰 우선순위 가이드 (변경 파일 → packet 참조 → 인접) | §진단 도구 |
| 9 | 체크리스트 활용 방식 명확화 (trigger / category source 2축) | §역할 §2 |
| 10 | severity_overrides 충돌 처리 + default 룰 source 명시 | §lane별 진단 가이드 + §분류 규칙 |

#### `agents/CodexReviewAgent.md` (+20/-3)

| # | 항목 | 위치 |
|---|---|---|
| 1 | "필수 워커 — fallback 불가" 문구 통일 | 서문 |
| 2 | Lane-conditional packet 검증 미러링 | §입력 검증 §1-3 |
| 3 | title/body 형식 고정 (PL dedup 키 sync) | §정규화 보고 스키마 |
| 4 | 회귀 힌트 + 추론 기준 명시 | §보고 형식 + §변환 규칙 |

### 3.3 Plugin Self-Application 정책 (CLAUDE.md 신규 섹션)

`CLAUDE.md`에 다음 구조 신규 섹션 추가 (위치: "GitHub Workflow" 섹션 뒤, "docs/stories markdown 규약 요약" 섹션 앞 — Story 의무 정책 → docs/stories 규약 흐름이 자연스러움).

```markdown
## Story 작성 의무 (모든 변경 적용)

매 변경 시작 시 Orchestrator가 cutoff 분류 → 강제/면제 결정. 모호 시 강제 측 (false positive < false negative).

### 강제 대상 (Story file 작성 의무)

- 신규 ADR 결정 / 기존 ADR 변경
- 아키텍처·도메인 모델 추가/삭제/재정의
- 에이전트 추가·삭제·역할 재정의
- Workflow 정의(`templates/github-workflows/**`) 변경
- SSOT 문서(`templates/`·`presets/`·`CLAUDE.md`·`docs/orchestrator-playbook.md`) 의미 변경
- Breaking change · consumer migration 영향

### 면제 대상 (chore commit OK)

- Typo · 문법 · 줄바꿈 · 마크다운 형식 정리
- 링크 깨짐 수정 / 죽은 링크 제거
- Lint 자동 fix · dependency lock · version bump (security 영향 없는 경우)
- README 단순 문구 수정

면제 시 commit body에 `Story 면제 사유: <이유>` 명시 의무.

### Consumer overlay 확장

Consumer는 `.claude/_overlay/project.yaml`의 `story_cutoff.additional_exempt_categories[]`로 도메인 특화 면제 항목을 추가할 수 있다 (예: "DB 마이그레이션 자동 생성 파일"). **강제 항목 축소는 불허** — 안전 방향 확장만.

### Plugin 자체 적용 (dogfooding)

이 plugin repo도 동일 정책 적용. KEY prefix는 `CFP`. Plugin meta 변경은 §8 Test Contract / §9 리뷰·테스트 결과 등 무의미한 lane을 `N/A — <사유>`로 명시. 인프라 자동화(`.github/workflows/` · `ISSUE_TEMPLATE`)는 단계적 도입 — 1단계 = 정책+`docs/stories/` 디렉토리, 2단계 = workflow + Issue Forms (별도 작업).
```

### 3.4 Schema 확장 (`docs/project-config-schema.md`)

Consumer overlay에 `story_cutoff` 키 추가:

```yaml
story_cutoff:
  additional_exempt_categories:
    - <카테고리 자유 텍스트>   # 예: "auto-generated migration files", "vendored library updates"
```

### 3.5 인프라 1단계 (이번 PR)

- `docs/stories/` 디렉토리 신설 (Story file CFP-1.md로 자연스럽게 생성됨)
- `docs/stories/CFP-1.md` 신규 (본 Change Plan과 매핑되는 첫 Story 인스턴스)

### 3.6 인프라 2단계 (별도 작업, scope 외)

- `.github/ISSUE_TEMPLATE/story.yml` (+ bug.yml, audit.yml) 추가
- `.github/workflows/`에 6종 워크플로우 (story-init.yml 등) 복사
- branch protection · required status check 활성화

본 PR은 **1단계만** 처리 — 작업 흐름 단절 회피 + scope creep 방지.

### 3.7 ADR 정합성

- ADR-001 (review-agent-unification): **일치**. 본 변경은 ADR-001 결정의 운영 robustness 강화
- 신규 ADR 필요: **없음** (정책 도입은 Process Decision이고 Architecture Decision 아님 — 향후 정책 복잡화 시 ADR-002 검토)

## §4. API 계약

본 변경은 코드 API 변경 없음. "API"에 해당하는 것은 다음 두 가지 인터페이스:

### 4.1 정책 텍스트 (CLAUDE.md 신규 섹션) — §3.3 verbatim

### 4.2 Consumer overlay schema 확장 (`docs/project-config-schema.md`)

```yaml
# 추가될 키
story_cutoff:
  additional_exempt_categories: list[str]   # 선택, 기본 []
```

Validation 규칙: schema에 명시된 키만 허용. 강제 항목 축소(`force_strict: false` 같은 안전 우회 키)는 schema에 정의하지 않음 — 의도적 확장 일방향.

## §5. 변경 계획 (파일 단위)

| 파일 경로 | 변경 유형 | 담당 | 상태 |
|-----------|-----------|------|------|
| `agents/ClaudeReviewAgent.md` | 수정 (+61/-8) | (적용 완료) | staged 대기 |
| `agents/CodexReviewAgent.md` | 수정 (+20/-3) | (적용 완료) | staged 대기 |
| `CLAUDE.md` | 수정 (신규 §추가) | DocsAgent (= 본 작업자) | 대기 |
| `docs/project-config-schema.md` | 수정 (신규 키 추가) | DocsAgent | 대기 |
| `docs/stories/CFP-1.md` | 신규 | DocsAgent | 대기 |
| `docs/change-plans/cfp-1-review-polish-and-self-application.md` | 신규 (본 파일) | DocsAgent | 작성 중 |

## §6. 리팩토링 선행 작업

**없음.** 기존 파일 보존 + 정책 신설 + 워커 .md 보강(이미 적용)만. 전역 리팩토링 금지 원칙 준수.

## §8. Test Contract

### §8.1 커버리지 계획

- 단위 테스트: **N/A** — markdown 정의·정책 신설 변경, 자동 테스트 대상 아님
- 통합 테스트: **N/A**
- 인프라 테스트: **N/A** — 본 PR scope에 워크플로우 추가 없음 (1단계는 정책+디렉토리만)

### §8.2 경계 조건·invariant

- **Cutoff 모호성**: 모호 시 강제 측 분류 (정책에 명시) — 검증 방식: 후속 PR에서 Orchestrator의 cutoff 분류 + commit body의 면제 사유 표기를 PR reviewer가 수동 확인. 자동 검증 메커니즘은 인프라 2단계에서 도입 검토
- **Plugin meta 변경의 §처리**: 무의미한 lane은 `N/A — <사유>` 명시 (정책에 명시) — CFP-1 자체가 첫 사례, Story file의 §8/§9 N/A 표기를 PR reviewer가 확인
- **Consumer overlay 강제 항목 축소 시도**: schema validation에서 차단 — 단, 본 PR은 schema 키 명시만 추가, 실제 validation 구현(예: pre-commit hook · CI gate)은 향후 별도 작업
- **본 변경 자체가 정책 적용 대상**: CFP-1 Story file에 §1-7 채움 + §8/§9 N/A 명시 — 정책의 첫 self-test (수동 검증)

### §8.3 Perf Baseline

**N/A** — 성능 영향 없음 (markdown · 정책 변경).

## §9. 분기 선택

**단일 PR**. Phase 1 (요구사항+설계+설계리뷰) ↔ Phase 2 (구현+구현리뷰+구현테스트+보안테스트) 분리 면제 사유:

- Plugin meta 변경 — 구현/테스트/보안 lane이 모두 N/A
- Change Plan 자체가 brainstorming 결과로 사용자 승인 받음 (별도 설계 lane 게이트 무의미)
- Review lane은 본 PR review에서 일반 GitHub PR review로 갈음

Commit 시리즈:
- **Commit 1**: `agents/ClaudeReviewAgent.md` + `agents/CodexReviewAgent.md` (이미 적용된 변경 — 본 정책 도입 직전 staged)
- **Commit 2**: `CLAUDE.md` (정책 섹션) + `docs/project-config-schema.md` (schema 확장) + `docs/stories/CFP-1.md` (Story file) + `docs/change-plans/cfp-1-review-polish-and-self-application.md` (본 Change Plan)

이렇게 분할하는 이유: Commit 1은 v0.9 polish 본질, Commit 2는 self-application 정책 본질. 사후 git 추적·revert 용이.

## §10. ADR 대상 여부 + 기존 ADR 정합성

- **ADR-001** (review-agent-unification): 일치. 본 변경은 ADR-001 결정의 운영 강화
- **신규 ADR 필요**: 없음. 정책 도입은 Process Decision이며, plugin 거버넌스 결정이지만 ADR 기준(Architecture Decision)에 부합하지 않음
- 향후 정책이 복잡화하거나 (예: cutoff 자동 판정 알고리즘 도입, consumer overlay에 강제 항목 축소 메커니즘 추가 요구) Process Decision도 ADR 대상이 되도록 ADR 카테고리 확장이 필요하면 그때 별도 ADR-002 발의
