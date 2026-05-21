# Change Plan 템플릿

ArchitectAgent가 설계 레인에서 작성하는 변경 계획서 표준 구조. DocsAgent가 `docs/change-plans/<slug>.md`에 저장.

**사용 대상**: ArchitectAgent (작성), DocsAgent (저장·Story 페이지 §7 미러링), DesignReviewPL (리뷰 대상), QADeveloperAgent (§8 Test Contract 입력), DeveloperPL · `role: dev` roster (구현 입력)

---

## Frontmatter (필수)

```yaml
---
title: <한 줄 제목>
slug: <kebab-case-slug>
status: draft | in-review | approved | implemented
author: ArchitectAgent     # chief author (under ArchitectPLAgent)
inputs:
  - CodebaseMapperAgent
  - RefactorAgent
  - SecurityArchitectAgent
  - TestContractArchitectAgent
  - DataArchitectAgent  # CFP-1092 rename — DataMigrationArchitectAgent → DataArchitectAgent (ADR-014 Amd 4 + ADR-042 Amd 7 wrapper SSOT cross-repo sibling propagation)
  - InfraOperationalArchitectAgent  # CFP-1092 rename — OperationalRiskArchitectAgent → InfraOperationalArchitectAgent (CFP-46 PR-D origin, ADR-014 Amd 4 wrapper SSOT)
reviewers: [DesignReviewPLAgent]
related_adrs: [ADR-NNN, ADR-MMM]
created: <ISO 8601>
story: <KEY>   # GitHub Story Issue key, e.g. PLG-7
---
```

---

## 본문 섹션 (번호 유지, 누락 시 DesignReview P0 차단)

### §1. 목적 (요건·수용 기준)
- 사용자 요구사항을 Change Plan 범위로 번역
- 수용 기준(acceptance criteria) — 이걸 통과하면 Story 완료

### §2. 현재 구조 분석 (CodebaseMapper 입력 — as-is)
- 변경 대상 영역의 파일·클래스·책임 (fact)
- 모듈 간 호출·의존 관계
- 기존 패턴·컨벤션 (ADR 추적 가능 시 인용)
- 유지 근거 논증 (Mapper 변호 내용)

### §3. 도입할 설계 (Mapper / Refactor / SecurityArch 3-way 입력 기반)
- 신규 포트/어댑터/클래스 — **이름·시그니처·타입 확정**
- 레이어 경계·의존성 방향
- Mapper / Refactor / SecurityArch 3-way 대립 결론 (어느 쪽 채택했고 왜)
- 관련 ADR 정합성 (신규 ADR 필요 여부)

#### §3.D bounded_context_boundary (ADR-091 §결정 5 — DDD vocabulary governance, CONDITIONAL)

> DDD 영역 touching Story 의무 / 비-touching 면제. ModuleArchitectAgent (boundary axis unified — module-level + aggregate-level, CFP-1126 흡수) 입력 기반. SSOT = [`docs/glossary.md`](../../docs/glossary.md) (wrapper repo, codeforge governance BC).

- **bounded_context**: 본 변경이 속한 BC 명시 (codeforge governance BC vs consumer application BC — 동음이의 시 qualifier 병기, ADR-091 §결정 4 Published Language 분리)
- **module placement**: 신규/변경 module 의 BC 안 배치 (layered / hexagonal / clean architecture — module-level dependency direction)
- **BC 간 통신**: cross-BC 참조 시 Anti-Corruption Layer (ACL) / Open Host Service (OHS) 패턴 명시 (glossary anchor)
- **forcing function (INV-5, ADR-091 §결정 7)**: 본 block 의 BC declaration 이 review-verdict-v4 `bc_violation` finding 과 연결 — 단순 nominal 아닌 spawn/review 실제 영향

#### §3.A affected_aggregates (ADR-091 §결정 3 — Aggregate 2-layer separate, CONDITIONAL)

> RDB OLTP aggregate touching Story 의무 (`project.yaml aggregate_arch.applicable: true`) / frontend-only·API-only·external-managed RDB consumer 면제. ModuleArchitectAgent (aggregate-level boundary advocate, AggregateArch mandate 흡수) 입력 기반.

- **affected aggregates[]**: 변경 영향 aggregate root + consistency boundary + transaction boundary 명시 (DDD application BC aggregate — ADR-091 §결정 3 Layer B real consistency boundary)
- **invariant 보존**: 각 aggregate 의 business invariant + referential / uniqueness / non-null constraint
- **forcing function (INV-5)**: 본 block 이 review-verdict-v4 `aggregate_violation` finding 과 연결

### §4. API 계약
- 라우트·요청/응답 스키마
- 컨텍스트·이벤트 스키마
- 의존성 (외부 라이브러리 · 내부 포트)
- 타입 정의

### §5. 변경 계획 (파일 단위)

| 파일 경로 | 변경 유형 | 담당 Agent | 설명 |
|-----------|-----------|------------|------|
| `src/...` | 추가·수정·제거 | BackendDev/FrontendDev/DataEng/InfraEng | 한 줄 |

> **Impl Manifest**: 구현 완료 후 DocsAgent가 Story 페이지 §8.5에 기록 — [`impl-manifest.md`](impl-manifest.md) 스키마 참조.

### §6. 리팩토링 선행 작업 (Dev 실행 의뢰 명시)
- 요건 범위 내 리팩토링만 (전역 리팩터링 금지)
- 각 항목 담당 Dev 명시 (BackendDev/FrontendDev/DataEng/InfraEng — consumer roster에 따라 추가/생략)
- 단계별 테스트 통과 유지 방안

### §7. 보안 설계 (SecurityArchitectAgent 입력 — 누락 시 DesignReview P0 차단)

#### §7.1 Trust boundary
- 외부 입력 진입점 (사용자·외부 API·메시지 큐·파일·환경 변수)
- 신뢰 경계 (외부↔게이트웨이↔도메인↔영속성, 텍스트 다이어그램)
- 각 boundary 검증 책임 (어떤 컴포넌트가 무엇을 검증)

#### §7.2 Threat model (STRIDE-LITE 표)

| 컴포넌트 | Spoofing | Tampering | Repudiation | Info Disclosure | DoS | Elevation |
|----------|----------|-----------|-------------|-----------------|-----|-----------|
| ...      | 위협·완화 | ... | ... | ... | ... | ... |

#### §7.3 Auth/Authz 설계
- 인증 방식 (JWT·session·OAuth 등) + 결정 근거
- 권한 모델 (RBAC·ABAC·기능 단위) + 결정 근거
- 세션 lifecycle (생성·만료·갱신·폐기)

### §7.4 운영 리스크 (OperationalRiskArchitectAgent 산출 — CFP-46 / ADR-014)

production-readiness 단일 책임 축. 5 항목 모두 명시 또는 `N/A — <사유 1줄>` (CONDITIONAL 항목 한정). 누락·사유 부재 시 DesignReview P0 차단.

#### §7.4.1 DR (Disaster Recovery)
<항목 본문 또는 N/A — <사유>>
- 외부 API · 거래소 · 서비스 장애 모드 enumeration
- 재시작 후 상태 복원 (in-flight order / open positions / unconfirmed transactions)
- failover 경로 (primary → secondary endpoint, region 이중화)
- runbook reference (운영팀 대응 sequence)

#### §7.4.2 Cancel-on-disconnect
<항목 본문 또는 N/A — <사유>>
- 외부 stream (WebSocket / SSE) 끊김 감지 mechanism
- 자동 작업 취소 정책 (in-flight orders / pending submissions)
- 재진입 정책 (idempotent re-submit, gap detection)

#### §7.4.3 Clock sync (CONDITIONAL)
<항목 본문 또는 N/A — <사유 1줄, 외부 time-window 프로토콜 의존 여부>>
- **적용 조건**: 외부 time-window 프로토콜 의존 (recvWindow / signed timestamp / OAuth token expiry / TOTP)
- NTP 의존성 / drift tolerance budget
- timestamp skew 처리 (재시도 vs reject)

#### §7.4.4 Rate limit / quota
<항목 본문 또는 N/A — <사유>>
- 외부 API weight / IP ban 모델
- throttling 정책 (token bucket / sliding window)
- quota 초과 시 backoff / circuit breaker
- 거래소별 weight 표 (consumer overlay 가 도메인 특화 weight 정의)

#### §7.4.5 Env isolation
<항목 본문 또는 N/A — <사유>>
- staging / prod (or paper / live) 시크릿 분리 (vault / env var namespacing)
- 런타임 분리 (process / container / cluster)
- 승인 게이트 (live 배포 시 별도 approval flow)
- 누설 차단 (live key 가 staging 노출 검증)

#### §7.5 민감 데이터 분류 + 흐름
- 데이터 분류표 (Public / Internal / PII / Secret)
- 데이터 흐름 (발생 → 흐름 → 저장 → 마스킹·암호화 지점)
- log/error 노출 금지 항목 명시

#### §7.6 위협 ↔ 완화 매핑
- 식별 위협 ID별 설계 단계 완화책 (구현 단계는 SecurityTest lane)
- 미완화 위협은 명시 + 수용 사유
- DR↔failover / disconnect↔cancel 매핑 (OperationalRiskArch consult)

#### §7.7 N/A 명시 (외부 입력·인증·민감데이터 무관 시)
- "본 Story는 trust boundary 변경 없음 — STRIDE 분석 N/A"
- 근거 1줄 (예: "내부 docs/templates 수정만, 외부 입력 0개")
- ※ N/A 근거 누락 시 DesignReview P0 차단

### §8. Test Contract (TestContractArchitectAgent 입력 통합 + chief author author — QADev TDD 입력 — 누락 시 DesignReview P0 차단)

#### §8.1 커버리지 계획
- 단위 테스트 범위 (신규·변경된 함수·클래스)
- 통합 테스트 범위 (레이어 경계 · API-서비스 흐름)
- 인프라 테스트 범위 (배포·config 로딩·smoke)

#### §8.2 경계 조건·엣지·invariant
- 경계 조건 목록 (null, empty, 최대·최소값, 타임아웃, 동시성)
- invariant 목록 (반드시 유지되어야 할 속성)
- 테스트 계획 ↔ §1-6 항목 매핑 요건

#### §8.3 Perf Baseline Protocol (성능 영향 있을 때 필수)
- 대상 시나리오: {핫패스 함수 / 엔드포인트 / 파이프라인 스테이지}
- 측정 지표: {mean latency / p95 / throughput 등, 1개 이상 명시}
- baseline 파일: `tests/perf/baselines/<scenario>.<ext>`
- 임계치: `mean:10%` (전역 기본, 완화·강화 필요 시 명시)
- 환경 고정: {CPU · runtime 버전 · 외부 의존성 variance 변수 처리}
- baseline 갱신 트리거: 설계 의도로 성능 스펙이 변경된 경우에만 Architect 승인 후 갱신
- 성능 영향 없으면 "N/A (성능 영향 없음)" 1줄로 대체 가능

#### §8.4 N/A 권한 (Story 전체 §8 N/A 시 — ADR-005 정합)
- Story가 실행 가능 코드 0줄인 경우 §8 전체 N/A 허용
- 표기: "N/A — <사유 한 줄>. 검증 채널: <대체 검증>. 면제 분류: plugin-meta-na | runtime-inert"
- `plugin-meta-na`: agent md / template / docs / yaml만 수정, 실행 가능 코드 0줄
- `runtime-inert`: 코드는 있으나 테스트 대상 runtime behavior 변경 없음
- N/A 근거 누락 시 DesignReview P0 차단 (SecurityArch §7.7 N/A 패턴 동형)

#### §8.5 Stateful / restart invariant tests (CONDITIONAL — CFP-47 / ADR-015)

TestContractArch primary, OperationalRiskArchitectAgent + DataMigrationArchitectAgent consult (§7.4 disconnect/clock/rate/env 짝, §11.6 idempotency 짝). CONDITIONAL — 적용 조건 충족 시 본문, 미충족 시 §8.5.0 표 4개 Y/N 모두 N + substantive reason 기재 후 §8.5 N/A 명시.

##### §8.5.0 Applicability decision (필수)

| 적용 조건 | Y/N | 근거 1줄 (substantive — 단순 부정 X, 30자 이상) |
|---|:-:|---|
| Long-running connection (WebSocket / SSE / long-poll / persistent TCP / gRPC stream) | □ | <근거> |
| Stateful in-memory cache (>1 update/sec sustained, >5 min retention 또는 derived state) | □ | <근거> |
| Background worker / queue consumer (async job runner / scheduler / data stream consumer) | □ | <근거> |
| Process restart-aware system (in-flight 작업 보유 / persistent state / graceful shutdown 요구) | □ | <근거> |

→ 1개라도 Y: §8.5.1+ 본문 필수
→ 4개 모두 N + 각 substantive reason: §8.5 전체 N/A 허용 + §8.5.4 본문에 "N/A — <reason>" 명시
→ 단순 "not applicable" / "해당 없음" / 길이 <30자 reason 차단 (`scripts/check-doc-section-schema.sh` 강제)

##### §8.5.1 Long-running invariant tests (적용 시)

(체크표 1번 또는 2번 또는 3번 Y 일 때 본문 필수)

- **테스트 대상 invariant** (sustained load 동안 유지되어야 할 속성):
  - cache eviction rate / depth bound / sequence consistency / worker queue bound / time-window correctness 등
- **부하 시나리오 + 지속 시간** (예: 6시간 sustained / N/sec / Y업데이트 누적)
- **invariant assertion 주기** (예: 매 N분 / 매 M update / 매 K 이벤트)
- **expected baseline + tolerance** (drift 허용 범위)
- **테스트 fixture / framework** (consumer 환경 — pytest-anyio / asyncio long-running fixture / load generator 등)
- **WS stream push_interval 실증 체크** (CFP-319, stream 적용 시):
  - [ ] `push_interval` empirical source confirmed
        (wiretap 실측 또는 공식 문서 — 미확인 시 TBD 박제 + Phase 1.5 wiretap step 명시)

##### §8.5.2 Process restart recovery tests (적용 시)

(체크표 4번 Y 일 때 본문 필수)

- **restart 시나리오** (SIGTERM / SIGKILL / deploy rolling update / OOM)
- **in-flight state**: 어떤 작업이 in-flight 인 시점에 kill (예: 주문 submit 중 / DB transaction 중 / queue publish 중)
- **검증 invariant**:
  - idempotency key persistence (재시도 시 중복 차단)
  - state reconciliation (재시작 후 외부 truth 와 일치)
  - graceful shutdown 완료 (in-flight 완료 vs cancel 정책 실제 동작)
  - WebSocket re-attach + sequence-gap detection (재시작 후 stream 재요청)
- **테스트 helper** (consumer 환경 — fork-and-kill helper / supervisor / state harness)

##### §8.5.3 Idempotency replay tests (CONDITIONAL — §11.6 active 시)

(§11.6 idempotency CONDITIONAL active + 체크표 4번 Y 인 교집합)

- **replay 시나리오** (같은 idempotency key 재호출 — 직후 / restart 후 / N분 후 / TTL 직전)
- **expected behavior** (cached response return / no-op / merge / conflict 처리)
- **§11.6 idempotency invariant 와 cross-ref** (Change Plan §11.6 의 key 정의 / TTL / cleanup 정책 직접 인용)

##### §8.5.4 N/A 명시 (4 적용 조건 모두 No 시)

- 표기: "N/A — <substantive reason 1줄>. 검증 채널: <대체 검증 — 예: §8.1-§8.2 만으로 충분>"
- substantive reason 예시:
  - "본 Story 는 sync HTTP request/response 만 수정 — long-running connection / cache / worker / restart-aware state 0개"
  - "본 Story 는 read-only API endpoint 추가 — 외부 호출 idempotency / state mutation 없음"
- 단순 "not applicable" / "해당 없음" / 길이 <30자 차단
- check-doc-section-schema.sh 강제 (Codex 개선 #1)

### §9. 분기 선택 (필요 Dev 조합)
- 의존성 없는 한 **`role: dev` roster 병렬 가능** (consumer roster에 따라 N개)
- 의존성 있으면 순서 명시 (예: DataEngineerAgent 스키마 → BackendDeveloperAgent 어댑터)

### §10. ADR 대상 여부 + 기존 ADR 정합성 점검
- Change Plan 결정이 기존 ADR과 일치 / 주의 / 위반 (위반 시 신규 ADR 필요)
- 신규 ADR 필요 여부 (새 ADR은 [`adr.md`](adr.md) 템플릿 따름)


### §10.A architecture_doc_impact (ADR-078 lane gate carrier, CFP-921)

ArchitectAgent 가 본 Change Plan 의 §3 (구조) / §5 (인터페이스) / §11 (데이터) 변경이 architecture doc 4 영역에 미치는 영향을 4-enum bool field 로 declare. ArchitectPL verdict packet `architecture_doc_updated: bool` self-check 의 input layer.

```yaml
architecture_doc_impact:
  modules: <true|false>      # 신규 module 도입 / 제거 / 책임 재분배
  boundaries: <true|false>   # trust / lane / plugin boundary 변경
  interfaces: <true|false>   # API / inter-plugin contract / agent prompt schema 변경
  data_flow: <true|false>    # 데이터 흐름 / event stream / handoff sequence 변경
```

**All false 시 rationale 의무 (skip 차단)**:

```yaml
architecture_doc_impact:
  modules: false
  boundaries: false
  interfaces: false
  data_flow: false
  none_rationale: |
    <Change Plan §3/§5/§11 변경이 architecture doc 4 영역에 도달하지 않는 사유 — file path / module 명 / interface 명 verbatim 인용 의무>
```

**ArchitectPL 검증** (verdict packet `architecture_doc_updated` field, design-output-v2 v2.4):
- 1+ true → ArchitectAgent 가 `docs/architecture/<path>.md` direct write 의무 → `architecture_doc_updated: true`
- All false + `none_rationale` 명시 → `architecture_doc_updated: false` (skip 정당화)
- All false + `none_rationale` 부재 OR §3/§5/§11 변경 ↔ 4-enum mismatch → FIX 의무

**Wording SSOT (I-4 byte-identical)**: 4 wording (`modules` / `boundaries` / `interfaces` / `data_flow`) = ADR-078 §결정 1 verbatim.

### §11. 데이터 마이그레이션 (DataMigrationArchitectAgent 입력 — 누락 시 DesignReview P0 차단)

DataMigrationArchitectAgent의 산출물을 ArchitectAgent (chief author)가 통합. SecurityArchitect §7 동형 패턴 — 외부 입력·schema·migration 무관 시 §11.7 N/A 명시 + 사유 1줄. 누락 시 DesignReview P0 차단 ([CFP-21 spec](../docs/superpowers/specs/2026-04-28-cfp-21-datamigration-architect-design.md)).

#### §11.1 Schema 변경 영향
- 변경 대상 테이블/컬렉션/인덱스/뷰 + 변경 유형 (ADD / MODIFY / DROP)
- 기존 데이터 행/문서 수 추정 + impact 분석 (테이블 크기 / 트래픽 / 의존 service)
- FK / unique / check constraint 영향

#### §11.2 Migration 전략
- 마이그레이션 방식 (online schema migration / offline / blue-green / dual-write / expand-contract / shadow table)
- Lock 시간 추정 + downtime 허용 여부
- Backward / forward compatibility (구버전 코드↔새 schema 양방향)
- 도구 (consumer 환경 — 예: pt-online-schema-change / gh-ost / Liquibase / Flyway / Prisma migrate / Alembic)

#### §11.3 Rollback 경로
- 실패 시 rollback 스크립트/절차
- Rollback이 데이터 손실 동반하는 지점 명시
- Point of no return 지점 (예: DROP COLUMN 후 데이터 복구 불가)
- Rollback 검증 절차 (production 적용 전 staging 시뮬레이션)

#### §11.4 Data integrity invariant
- Migration 전후 불변식 (row count 보존 / FK 정합성 / NULL 비율 / unique 위반 없음)
- 검증 쿼리·체크포인트 (pre-check / post-check)
- 불일치 감지 시 alert / halt 정책

#### §11.5 Backfill / 기존 데이터 처리
- Default value 정책 (nullable vs NOT NULL with default)
- Backfill 배치 전략 (chunk size / throttle / lock 회피 / replication lag)
- 진행률 모니터링 + resume 가능성

#### §11.6 Idempotency invariant (CONDITIONAL — CFP-46 / ADR-014)

DataMigrationArch primary, OperationalRiskArchitectAgent consult (§7.4.2 disconnect 후 재진입 짝). CONDITIONAL — 적용 조건 충족 시 본문, 미충족 시 `N/A — <사유 1줄>` 명시.

<적용 시 항목 본문: client order ID / exactly-once intent / 재시도 시 동작 / N/A — <사유 1줄>>

- **적용 조건**: 재시도 가능 외부 호출 / side effect 있는 외부 호출 (HTTP POST / queue publish / payment / 주문 submit) / 장기 워크플로우 / migration script
- **N/A 패턴**: batch-only / read-only / sync-only RPC
- 적용 시 본문 항목:
  - Idempotency key 정의 (client order ID / request ID / dedup token)
  - exactly-once intent 구현 방식 (DB unique constraint / dedup table / idempotency-key middleware)
  - 재시도 시 동작 (return cached response / no-op / merge)
  - TTL · cleanup 정책

#### §11.7 N/A 명시 (DB·migration 무관 시)
- "본 Story는 데이터 layer 변경 없음 — migration 분석 N/A"
- 근거 1줄 (예: "내부 docs/templates 수정만, schema 변경 0개")
- 사유 누락 시 DesignReview P0 차단

### §13. Phase 1 산출물 self-check 결과 (ADR-065 / CFP-438 — non-marketplace 영역)

ArchitectAgent chief author 가 Phase 1 산출물 (Change Plan + ADR + Story file 섹션) commit 직전 7-item mechanical sync self-check 결과 명시 의무. 본 섹션 누락 시 ArchitectPLAgent verdict packet 의 `mechanical_self_check_passed: false` 으로 처리 (review-verdict-v4 v4.2 schema).

| # | 항목 | 결과 (PASS / NA / FAIL) | 근거 |
|---|---|:-:|---|
| 1 | `label-registry-v2.md` 변경 시 `scripts/bootstrap-labels.sh` sync 동반 | □ | <근거 또는 NA 사유> |
| 2 | `doc-locations.yaml` 변경 시 `bash scripts/check-doc-locations.sh --regen` 실행 | □ | <근거 또는 NA 사유> |
| 3 | 신규 `templates/github-workflows/*.yml` 시 `.github/workflows/` self-app copy 동반 (byte-identical) | □ | <근거 또는 NA 사유> |
| 4 | CLAUDE.md / docs/** 내 link target Phase 1 분배 확인 (Phase 2 file 참조 시 dangling) | □ | <근거 또는 NA 사유> |
| 5 | `docs/inter-plugin-contracts/MANIFEST.yaml` registries 블록 갱신 필요성 확인 | □ | <근거 또는 NA 사유> |
| 6 | `docs/parallel-work/section-ownership.yaml` 정책 필요 시 row append | □ | <근거 또는 NA 사유> |
| 7 | `docs/doc-locations.yaml` 신규 doc type row 필요성 확인 | □ | <근거 또는 NA 사유> |

8. ☐ **ADR-078 architecture_doc 4 영역 갱신 자기 검증 (CFP-921)** — §10.A `architecture_doc_impact` 4-enum bool field declare 완료 + 1+ true 시 `docs/architecture/<path>.md` direct write 완료 OR all false 시 `none_rationale` 명시 (skip 차단). ArchitectPL verdict packet `architecture_doc_updated: bool` self-check binding (design-output-v2 v2.4 carrier).

**Overall**: `mechanical_self_check_passed: <true | false>`

- `true` = 모든 7 항목 PASS 또는 NA — review-verdict-v4 packet 에 forward
- `false` = 1+ FAIL — ArchitectPLAgent 가 `pl_recommendation: FIX` + ArchitectAgent re-spawn 명령

**marketplace 영역 분리**: marketplace mirrored field (`name` / `version` / `description` / `author`) atomic invariant 검증은 ADR-063 SSOT (3-file: `plugin.json` / `CHANGELOG.md` / `marketplace.json`). 본 §13 scope 외 — cross-ref only.

### §13.N Marketplace sync self-check (ADR-063 Amendment 1 / CFP-597)

```yaml
marketplace_sync_required: <bool>  # true = mirrored field 변경 감지, false = NA
mirrored_fields_changed: [<name|version|description|author>]  # 변경된 field enum
triggering_plugins:  # marketplace_sync_required=true 시
  - <plugin name>: <MAJOR|MINOR|PATCH>
```

silent skip 금지 — `marketplace_sync_required: false` 명시 의무 (AC-2 정합).

---

## DocsAgent 저장·미러링 의무

1. Architect가 확정 → DocsAgent가 `docs/change-plans/<slug>.md`에 저장
2. **저장 즉시** Story 페이지 §7에 요약 미러링 — "§1 목적 / §3 도입할 설계 / §4 API 계약 / §9 분기 선택"을 verbatim 또는 5-10줄 요약으로 복사
3. FIX 루프에서 갱신될 때마다 같은 파일 업데이트 (git 버전 히스토리 추적)

## 구현 진입 조건

- Change Plan 모든 섹션(§1-§11) 존재 + DesignReview PASS
- Dev 스폰 전 Change Plan 저장 완료 필수
