---
title: "CFP-17 — 설계 lane 재구조화 (ArchitectPLAgent + SecurityArchitectAgent 도입)"
date: 2026-04-27
status: draft
story_key: CFP-17
related_adrs:
  - ADR-004 (신규 — 본 Story가 발행)
authors:
  - Josh
  - Claude (brainstorming via superpowers:brainstorming)
based_on:
  - 사용자 직관 (보안 설계 공백 인지)
  - Codex 독립 감사 (ArchitectAgent 책임 공백 7건 + Top-3 우선순위)
  - superpowers:brainstorming 6-section dialogue
inputs_decisions:
  - 옵션 (1) 보안 설계 deputy 신설
  - 옵션 (C) ArchitectPL을 순수 supervisor로 추출, ArchitectAgent는 deputy 강등 (본업 보존)
  - 옵션 (3) 번들 = α(PL 분리) + β(SecurityArch) + γ(ADR draft 명문화)
  - 옵션 (i) Architect-heavy authoring (PL은 글 안 씀, Architect deputy가 chief author)
  - 옵션 (a) Change Plan 신규 §섹션 (§7 보안 설계)
  - 옵션 (C, again) Architect는 Claude 단독 — Codex 관점은 DesignReview lane에서 수렴
---

# Spec — 설계 lane 재구조화: ArchitectPLAgent + SecurityArchitectAgent 도입

## 1. 배경 & 문제 정의

### 1.1 사용자가 식별한 1차 공백

CodeForge는 7-레인 구조 (요구사항 → 설계 → 설계리뷰 → 구현 → 구현리뷰 → 구현테스트 → **보안테스트**) 로 운영되며, 설계 lane은 ArchitectAgent가 PL+chief designer 양 역할을 겸직, CodebaseMapperAgent(보수/변호자)·RefactorAgent(혁신/옹호자)의 대립을 조정해 Change Plan을 작성한다.

사용자가 보안 테스트 lane을 직접 경험하면서 한 가지 비대칭을 발견했다:

> **보안은 lane으로 게이트가 있는데, 보안 설계를 변호하는 에이전트가 없다.**

현재 구조에서 trust boundary·auth model·threat model 등 보안 설계 결정은 ArchitectAgent가 implicit하게 책임지지만, Mapper·Refactor 어느 deputy도 보안 관점을 표현하지 않는다. 결과:

- trust boundary·auth 모델 오설계는 **보안 테스트 lane에서 처음 발견** → 설계 원인 판정 → Phase 1 follow-up PR 회귀 (가장 비싼 FIX 경로, CLAUDE.md decision table 명시됨)
- 책임 매트릭스에서 trust boundary·auth·credential 등은 모두 SecurityTest 컬럼에 ✅, Design lane 컬럼에는 명시적 제외 ("—")
- shift-right 비용이 누적되는 구조

### 1.2 사용자의 추가 요청 — Architect 책임 공백 전수 점검

사용자는 보안 공백 1건만으로 멈추지 않고, **"이 참에 ArchitectAgent의 다른 역할 공백이 없는지 점검해보자"** 고 제안. **Codex CLI(GPT-5)와 함께** 독립 감사를 의뢰.

### 1.3 Codex 독립 감사 결과 (요약)

ArchitectAgent의 책임 공백 7건 식별, Top-3:

1. **§8 Test Contract 단독 작성** — 설계 단계 QA 견제 부재 (High)
2. **데이터/스키마 마이그레이션·롤백** — Change Plan 슬롯 자체 부재 (High)
3. **FIX 루프 단독 판정** — Mapper/Refactor 대립이 판정 단계까지 이어지지 않음 (High)

기타 (Medium): 관측성·운영 준비도 / API 호환성·에러 semantics / 성능 SLO·용량·핫패스 예산 / **ADR 초안 작성 책임 회색지대** (Codex #7).

### 1.4 사용자의 구조 제안

위 진단을 보고 사용자는 한 가지 구조 변경을 제안:

> **ArchitectPLAgent를 신설하고 ArchitectAgent를 그 아래로 내리고 싶다.**

이 spec은 그 제안을 6-section brainstorming으로 정제한 결과물이다.

---

## 2. 결정 요약

| 결정 | 옵션 | 의미 |
|------|------|------|
| **2.1** | 옵션 (1) | 보안 설계 책임을 가진 deputy 신설 — `SecurityArchitectAgent` |
| **2.2** | 옵션 (C) | ArchitectPL은 순수 supervisor (글을 쓰지 않음), ArchitectAgent는 deputy 강등하되 본업(Change Plan author) 보존 |
| **2.3** | 옵션 (3) — 통합 번들 | CFP-17 한 Story에 α(PL 분리) + β(SecurityArch 신설) + γ(Codex #7 ADR draft 책임 명문화) 모두 포함 |
| **2.4** | 옵션 (i) — Architect-heavy | PL은 orchestration + 검수 + FIX 판정, ArchitectAgent deputy가 Change Plan §1-§10 + ADR draft + §8 Test Contract author |
| **2.5** | 옵션 (a) — 신규 §섹션 | Change Plan template에 **§7 보안 설계** 신설 (현재 §7은 빈 placeholder, 자연스러운 슬롯) |
| **2.6** | 옵션 (C, again) — Claude 단독 | Architect는 Claude only. Codex 관점은 DesignReview lane(이미 Claude+Codex 병렬 검토)에서 수렴. "두 author 병렬"은 통합 결정의 dedup 불가능 |

**제외된 결정** (Phase 2 후속 CFP로 분리):
- TestContractArchitectAgent (Codex Top-1 — §8 author 견제)
- DataMigrationArchitectAgent (Codex Top-2 — §데이터/롤백)
- Codex deputy로 추가 (옵션 (D) — unique angle 정의 모호)
- Codex #4-#6 (관측성·API호환·SLO) DesignReview checklist 확장

이 후속들은 별도 Story로 분리. 본 CFP-17은 "PL 분리 + 보안 deputy + ADR draft 명문화"에 집중.

---

## 3. Pod 구조 & Information Flow

### 3.1 Pod 구조 (After)

```
ArchitectPLAgent (신설)                                  # PL: supervisor + judge
 ├── ArchitectAgent (강등, 본업 보존)                    # Chief Author: Change Plan §1-§10 + ADR draft
 ├── CodebaseMapperAgent (기존)                          # 보수 — as-is 변호자
 ├── RefactorAgent (기존)                                # 혁신 — 결합도/구조 옹호자
 └── SecurityArchitectAgent (신설)                       # 위협 — trust boundary/auth/data 변호자
```

ArchitectAgent는 deputy 4인 중 "**chief author**" 역할 — Mapper/Refactor/SecurityArch의 독립 perspective를 통합해 Change Plan 본체를 작성. 다른 3 deputy는 독립 관점 제출자.

### 3.2 Information Flow (3-phase)

```
[Phase 1: Independent perspective gathering — 병렬]
ArchitectPLAgent
  ├─ spawn → CodebaseMapperAgent      → as-is 사실 + 유지 근거 + 변경 영향 지도
  ├─ spawn → RefactorAgent            → to-be 구조 + 결합도 분석 + 최소 변경 경로
  └─ spawn → SecurityArchitectAgent   → trust boundary + threat model + auth/data 설계
       ※ 셋 다 공통 입력(코드 + Story §1-7 + ADR) 직접 fetch, 상호 산출물 미참조 (독립성)

[Phase 2: Synthesis — 순차]
ArchitectPLAgent
  └─ spawn → ArchitectAgent (with 3 deputy outputs + Story §1-7)
       → Change Plan §1-§10 draft + 신규 ADR draft + §8 Test Contract
       → DocsAgent 경유 docs/change-plans/<slug>.md 저장 의뢰

[Phase 3: PL 검수 + 판정]
ArchitectPLAgent
  ├─ Architect draft가 deputy 산출물 모두를 근거 있게 채택/반박했는지 감사
  ├─ §섹션 누락·§8 Test Contract 누락·신규 ADR 필요 미판단 등 차단 사유 검사
  └─ PASS → DesignReview lane 진입 요청 (Orchestrator 경유)
     RETURN → Architect 재스폰 (clarification context + 누락 항목)
```

### 3.3 FIX 루프 흐름 변화

```
[변경 전]
DeveloperPL 1차 진단 → ArchitectAgent 최종 판정

[변경 후]
DeveloperPL 1차 진단 → ArchitectPLAgent 최종 판정
                       (Architect deputy는 author이므로 자기 작품 판정 conflict of interest)
```

이로써 Codex 감사 #3 "FIX 루프 무견제성"이 자연 해소 — PL = judge / Architect = author 분리.

### 3.4 평행 PL 정합성

ArchitectPLAgent 신설 후 PL 라인업 (7 lane + 2 cross-cutting 모두 PL 가짐):
- RequirementsPLAgent / **ArchitectPLAgent (신)** / DesignReviewPLAgent / DeveloperPLAgent / CodeReviewPLAgent / TestAgent / SecurityTestPLAgent / PMOAgent / DocsAgent

이전엔 설계 lane만 PL 명칭 없이 ArchitectAgent가 PL 역할 겸함. 본 변경으로 7-레인 구조의 모든 lane이 PL을 갖는 형태로 대칭성 회복.

---

## 4. Agent 명세 + 권한

### 4.1 ArchitectPLAgent (신설)

**한 줄 정의**: 설계 레인 PL. Mapper·Refactor·SecurityArch·Architect deputy 4인의 산출물을 supervisor로 검수하고 FIX 루프 최종 판정자.

**책임**:
- Phase 1 deputy 3인(Mapper·Refactor·SecurityArch) 병렬 스폰
- Phase 2 ArchitectAgent 스폰 (deputy 산출물 forward + Story §1-7 컨텍스트)
- Phase 3 Architect draft 검수 — 4가지 감사 항목:
  1. Mapper 변호 근거를 근거 있게 채택/반박했는가
  2. Refactor 제안이 요구 범위 내인가
  3. SecurityArch 위협-완화 매핑이 §7 보안 섹션에 빠짐없이 반영됐는가
  4. §섹션 누락 / §8 Test Contract 부재 / 신규 ADR 판단 누락 차단
- Clarification 재스폰 trigger (deputy 또는 Architect)
- FIX 루프 최종 원인 판정 (DeveloperPL 1차 진단 수령 후)
- QADev Impl Manifest 매핑표 감사
- DocsAgent 경유 Phase 1 PR 라벨·코멘트 의뢰

**Stateless 재스폰**: 매 트리거마다 신규 — Story §1-§10 재로딩.

**Permissions** (다른 PL 동일 패턴):
```yaml
allow:
  - Read, Grep, Glob
  - Edit/Write(.claude-work/doc-queue/**)
  - Bash(mkdir/ls .claude-work/doc-queue*)
deny:
  - Edit/Write(src/**, tests/**, docs/**)
```

### 4.2 ArchitectAgent (refocused — chief author)

**한 줄 정의**: ArchitectPLAgent 직속 chief author. 4 deputy 중 통합 author 역할로 Change Plan 본체와 ADR draft 작성.

**책임 변경**:
- **유지**: Change Plan §1-§10 전체 author, §8 Test Contract author, **신규 ADR draft author** (Codex #7 명문화)
- **이관**: Mapper/Refactor 스폰 trigger → PL로 (Architect는 deputy outputs을 입력으로 수령)
- **이관**: 대립 조정 → PL로 (PL이 deputy outputs 검수)
- **이관**: FIX 최종 판정 → PL로 (Codex #3 무견제성 해소)
- **이관**: Impl Manifest 감사 → PL로

**입력**:
- ArchitectPLAgent로부터 forward된 3 deputy 산출물 (Mapper/Refactor/SecurityArch)
- Story §1-7 + 관련 ADR

**출력**:
- Change Plan §1-§10 draft (DocsAgent 경유 저장 의뢰)
- 신규 ADR draft (필요 시, DocsAgent 경유 docs/adr/ADR-NNN-<slug>.md 저장 의뢰)

**Permissions**: 현재와 동일 — 변경 없음.

### 4.3 SecurityArchitectAgent (신설)

**한 줄 정의**: ArchitectPLAgent 직속 deputy. 위협 모델·trust boundary·auth model 설계 변호자.

**성격**: 공격자 관점. "어디서 외부 입력이 들어오는가, 누가 무엇을 신뢰하는가, 데이터가 어떻게 흐르는가"를 묻는 보안 advocate. Mapper(보수)·Refactor(혁신)와 함께 3-way 대립의 한 축.

**입력** (Mapper/Refactor와 공통 패키지):
- Story §1-7 (요건 + 변경 대상 코드 경로 + ADR 목록)
- 변경 대상 코드 (직접 Read)
- 관련 ADR + 보안 관련 ADR (직접 Read)
- (재스폰 시) 이전 본인 출력 + PL clarification context

**산출물** (Architect가 Change Plan §7 author 시 입력):
- **Trust boundary 다이어그램** (text-based: 외부↔게이트웨이↔도메인↔영속성 경계)
- **Threat model 표** — STRIDE-LITE × 시스템 컴포넌트 매핑
  - Spoofing / Tampering / Repudiation / Information disclosure / Denial of Service / Elevation of privilege
- **Auth/Authz 설계 결정** — 인증 방식·세션·권한 모델
- **민감 데이터 분류 + 흐름** — PII/credential/secret 발생→흐름→저장→마스킹·암호화 지점
- **위협↔완화 매핑** — 식별 위협별 설계 단계 완화책 (구현 단계 X)
- **null 결과 명시 권한** — Story가 외부 입력·인증·민감데이터 무관 시 "본 Story는 trust boundary 변경 없음 — STRIDE 분석 N/A" 명시 (요구사항 lane "null 결과도 유효한 관점" 패턴 차용)

**Permissions**:
```yaml
allow:
  - Read, Grep, Glob
  - Bash(find/ls/git log/git blame *)
  - Edit/Write(.claude-work/doc-queue/**)
  - WebSearch, WebFetch       # OWASP ASVS·CWE·CVE 조회용
deny:
  - Edit/Write(src/**, tests/**, docs/**)
```

**Freshness**: Mapper/Refactor와 동일 — 매 설계 lane 진입 시 재스폰.

**SecurityArch ↔ SecurityTestPL 책임 경계**:
- **SecurityArchitect (Design lane)** = "**어디에 boundary가 있어야 하는가**" — 설계 결정 (예방)
- **SecurityTestPL (Security Test lane)** = "**코드가 그 boundary를 지키는가**" — 구현 검증 (검출)
- 둘 다 OWASP·CWE 참조하지만, 시점이 다름: 설계 시점 vs 구현 시점

### 4.4 CodebaseMapperAgent / RefactorAgent (minor 변경)

frontmatter `description` 한 줄 + 본문 "포지션" 절 1줄만 수정:
- `상위: ArchitectAgent` → `상위: ArchitectPLAgent`
- 본문 "대립 파트너" 절에 SecurityArch 추가 (3-way 대립)
- 그 외 본업·산출물 변동 없음

---

## 5. Change Plan template 변경

### 5.1 신규 §섹션 위치 — §7 보안 설계

**근거**:
- 현재 `templates/change-plan.md` §7은 placeholder ("§7 Impl Manifest 초안은 여기 비움" — Story §8.5에 실제 내용)
- §3 도입할 설계 → §4 API 계약 → ... → §7 보안 설계 → §8 Test Contract로 sequence (보안은 설계 본체 다음, Test Contract 직전)
- 번호 재할당 없음 — 다른 §섹션 reference 모두 보존

### 5.2 §7 본문 구조

```markdown
### §7. 보안 설계 (SecurityArchitectAgent 입력 — 위협 모델 + Trust Boundary)

#### §7.1 Trust boundary
- 외부 입력 진입점 (사용자·외부 API·메시지 큐·파일·환경 변수)
- 신뢰 경계 (외부↔게이트웨이↔도메인↔영속성)
- 각 boundary 검증 책임

#### §7.2 Threat model (STRIDE-LITE 표)
| 컴포넌트 | Spoofing | Tampering | Repudiation | Info Disclosure | DoS | Elevation |
|----------|----------|-----------|-------------|-----------------|-----|-----------|
| ...      | 위협·완화 | ... | ... | ... | ... | ... |

#### §7.3 Auth/Authz 설계
- 인증 방식 (JWT·session·OAuth 등) + 결정 근거
- 권한 모델 (RBAC·ABAC·기능 단위) + 결정 근거
- 세션 lifecycle

#### §7.4 민감 데이터 분류 + 흐름
- 데이터 분류표 (Public / Internal / PII / Secret)
- 데이터 흐름 (발생 → 흐름 → 저장 → 마스킹·암호화 지점)
- log/error 노출 금지 항목 명시

#### §7.5 위협 ↔ 완화 매핑
- 식별 위협 ID별 설계 단계 완화책 (구현 단계는 SecurityTest lane)
- 미완화 위협은 명시 + 수용 사유

#### §7.6 N/A 명시 (외부 입력·인증·민감데이터 무관 시)
- "본 Story는 trust boundary 변경 없음 — STRIDE 분석 N/A"
- 근거 1줄 (예: "내부 docs/templates 수정만, 외부 입력 0개")
- ※ N/A 근거 누락 시 DesignReview P0 차단
```

### 5.3 Frontmatter 갱신

```yaml
author: ArchitectAgent     # 그대로 (chief author 역할)
inputs:                    # 신규 명시
  - CodebaseMapperAgent
  - RefactorAgent
  - SecurityArchitectAgent
reviewers: [DesignReviewPLAgent]
```

### 5.4 차단 정책 추가 (CLAUDE.md / DesignReview checklist)

- **§7 누락 → P0 차단** (기존 §8 Test Contract 누락 P0 패턴 차용)
- **§7.6 N/A 사유 부재 → P0 차단** (N/A는 명시적이어야, 무사유 회피 금지)

### 5.5 Plugin dogfooding 안전장치

CFP-* Story들 다수가 docs-only / meta 변경 — 대부분 §7.6 N/A로 처리. CLAUDE.md "Plugin meta 변경은 §8 Test Contract / §9 리뷰·테스트 결과 등 무의미한 lane을 `N/A — <사유>`로 명시" 패턴을 §7로 확장.

### 5.6 기존 §7 placeholder 처리

현재 §7 "Impl Manifest 초안은 여기 비움" 안내문 — 정보 가치 낮음 (Story §8.5에 이미 명시). **삭제** + §5 footer에 "Impl Manifest는 구현 완료 후 Story §8.5에 기록" 1줄 인라인.

---

## 6. 책임 매트릭스 변경 (CLAUDE.md)

### 6.1 변경 원칙

**Design lane 신규 컬럼 추가** — DesignLane = SecurityArchitect 산출물:
- Trust boundary·threat model·auth 설계 결정 = **Design lane**으로 이동 (예방)
- 그 결정의 코드 준수 검증 = **SecurityTest**에 잔류 (검증)

이로써 한 영역이 두 곳에서 검토되는 중복 없이 **시점 분리** (설계 시점 / 구현 시점).

### 6.2 갱신 후 매트릭스 (요지)

| 체크 항목 | DesignLane (新) | DesignReview | CodeReview | SecurityTest |
|-----------|:---------------:|:------------:|:----------:|:------------:|
| Change Plan 완결성(§1-10) | — | ✅ | — | — |
| ADR 정합성(§3·§7 위반 여부) | — | ✅ | — | — |
| CodebaseMapper ↔ Refactor 균형 | — | ✅ | — | — |
| §8 Test Contract 타당성 | — | ✅ | — | — |
| **§7 Trust boundary 정의** | ✅ **(new)** | (감사) | — | (검증) |
| **§7 Threat model (STRIDE-LITE)** | ✅ **(new)** | (감사) | — | — |
| **§7 Auth/Authz 모델 결정** | ✅ **(new)** | (감사) | — | (검증) |
| **§7 민감 데이터 분류·흐름** | ✅ **(new)** | (감사) | — | (검증) |
| **§7 위협↔완화 매핑** | ✅ **(new)** | (감사) | — | (검증) |
| **§7 누락 / N/A 사유 부재** | — | ✅ **P0 차단** | — | — |
| 코드 ↔ Change Plan 변경 계획 준수 | — | — | ✅ | — |
| 코드 스타일·테스트 코드 품질·런타임 오류 | — | — | ✅ | — |
| Impl Manifest §8.5 ↔ 실제 파일 일치 | — | — | ✅ | — |
| **Injection 공격 표면** | — | — | — | ✅ |
| **Trust boundary 위반 (코드)** | (설계) | — | — | ✅ **(코드 준수 검증)** |
| Credential / secret 노출 | — | — | — | ✅ (1차: Secret Scanning) |
| **Auth / 세션 결함 (코드)** | (설계) | — | — | ✅ **(코드 준수 검증)** |
| 암호학 오용 | — | — | — | ✅ |
| **민감 데이터 유출 (런타임)** | (설계 분류) | — | — | ✅ **(런타임 노출 검증)** |
| 의존성 CVE 스캔 | — | — | — | ✅ (1차: Dependabot) |
| 정적 분석 결함·설정·배포 보안 | — | — | — | ✅ |
| Race / TOCTOU 보안 취약 | — | — | — | ✅ |

### 6.3 시점 분리 명시 (CLAUDE.md 표 하단 주석)

> **DesignLane vs SecurityTest**:
> - DesignLane(SecurityArch) = "**어디에 boundary가 있어야 하는가**" — 설계 결정 (예방)
> - SecurityTest = "**코드가 그 boundary를 지키는가**" — 구현 검증 (검출)
> - 두 lane이 같은 카테고리(예: trust boundary)를 다루지만 **시점이 다름**: 설계 결정 vs 코드 준수
> - DesignReview는 "§7 보안 설계 자체의 완결성"을 감사 (추가 보안 검토 X — SecurityArch 산출물이 충분한가만)

### 6.4 FIX 루프 decision table 신규 행

| Failure 유형 | 1차 가정 | 설계 원인 escalate 조건 |
|---|---|---|
| **DesignReview P0 §7 누락** | **설계** | 항상 설계 (Architect chief author 미흡) |
| **SecurityTest P0 trust boundary 위반** | **설계** | §7.1 boundary가 코드와 불일치 → 설계 원인. §7.1에 명시된 boundary를 코드가 안 지킴 → 구현 원인 |
| **SecurityTest P0 auth/authz 결함** | **설계** | §7.3 모델 결함 → 설계. 모델은 맞는데 구현 결함 → 구현 |

기존 행은 변경 없음. SecurityTest의 "trust boundary 위반"·"auth 모델 오설계"는 §7.1·§7.3이 SSOT.

---

## 7. SSOT Ripple — 영향 파일 목록

### 7.1 Tier 1 — 신규 생성 (3 파일)

| 파일 | 내용 |
|------|------|
| `agents/ArchitectPLAgent.md` | 신규 PL agent md (§4.1) |
| `agents/SecurityArchitectAgent.md` | 신규 deputy agent md (§4.3) |
| `docs/adr/ADR-004-architectpl-securityarch-restructure.md` | 에이전트 역할 재정의 결정 기록 (CLAUDE.md "ADR 생성 기준" 강제) |

### 7.2 Tier 2 — 핵심 agent md 수정 (8 파일)

| 파일 | 변경 요지 |
|------|----------|
| `agents/ArchitectAgent.md` | "Chief Author under ArchitectPLAgent"로 refocus. FIX 최종 판정·Mapper/Refactor 스폰·Impl Manifest 감사 책임 이관 (PL로). ADR draft 책임 명문화 (Codex #7) |
| `agents/CodebaseMapperAgent.md` | `상위: ArchitectAgent` → `ArchitectPLAgent`, 대립 파트너 SecurityArch 추가 |
| `agents/RefactorAgent.md` | 동상 |
| `agents/DesignReviewPLAgent.md` | review packet `scope_globs`에 §7 추가, `severity_overrides`에 "§7 누락 / N/A 사유 부재 → P0", FIX escalation destination = ArchitectPL |
| `agents/DeveloperPLAgent.md` | FIX 1차 진단 → ArchitectPL 최종 판정 (3개 lane 갱신: 구현 리뷰·구현 테스트·보안 테스트) |
| `agents/DocsAgent.md` | Phase prefix 표 변동 없음. Architect 직접 인용 부분 갱신. Project Config Packet recipient에 ArchitectPL 추가 |
| `agents/PMOAgent.md` | Cross-Story 패턴 분석 시 Architect → ArchitectPL 갱신 |
| `agents/QADeveloperAgent.md` | "Architect 계약 §8 이행자" → "Architect deputy 계약 §8 이행자, ArchitectPL 감사" |

### 7.3 Tier 3 — 템플릿 (4 파일)

| 파일 | 변경 요지 |
|------|----------|
| `templates/change-plan.md` | **§7 보안 설계 신설** (§5.2). 6 sub-section + N/A 권한. 기존 §7 placeholder 제거 |
| `templates/review-checklists/design.md` | **§7 차단 항목 + SecurityArch 산출물 감사 항목** 추가. category enum에 `security-design` 추가 |
| `templates/review-pl-base.md` | Architect 회귀 destination 갱신 (DesignReview FIX → ArchitectPL → Architect 재스폰) |
| `templates/story-page-structure.md` | Story §7 (Change Plan 미러링)에 §7 보안 설계 요약 추가 |

### 7.4 Tier 4 — 최상위 SSOT (3 파일, 광범위 수정)

| 파일 | 변경 요지 |
|------|----------|
| `CLAUDE.md` | (1) 7-lane 다이어그램: 설계 lane에 ArchitectPL + 4 deputy. (2) Never-skippable 갱신. (3) 스폰 시퀀스 [설계] 절 갱신. (4) **책임 매트릭스 변경** (§6). (5) **FIX decision table 신규 행** (§6.4). (6) 병렬 스폰 권장 SecurityArch 추가. (7) Write 권한 list ArchitectPL 추가. (8) ArchitectPL ↔ SecurityTestPL 시점 분리 주석. (9) ADR 정합성 절 §7 위반 시 P0 추가 |
| `docs/orchestrator-playbook.md` | (1) §3 스폰 프롬프트 — 설계 lane: Architect → ArchitectPL. (2) §3B Preflight — Design lane preflight에 §7 검사. (3) FIX state machine 최종 판정자 ArchitectPL. (4) write queue mention — ArchitectPL recipient 추가. (5) §12 Context Packet — 설계 lane packet recipient = ArchitectPL |
| `docs/plugin-design.md` | agent 다이어그램·라인업 표 갱신 (있는 경우) |

### 7.5 Tier 5 — 메타 (3 파일)

| 파일 | 변경 요지 |
|------|----------|
| `.claude-plugin/plugin.json` | version 0.10.0 → 0.11.0. description "20 core" → "22 core" |
| `CHANGELOG.md` | v0.11.0 entry: ArchitectPL + SecurityArch 도입, Codex #7 ADR draft 명문화 |
| `README.md` | agent 라인업 라인 갱신 (있는 경우) |

### 7.6 Tier 6 — 호환성 / 비변경

- **기존 CFP-1 ~ CFP-16 Story files**: 과거 historical record로 보존, 변경 안 함
- **`docs/migration-guide.md`**: "v0.11.0부터 ArchitectPL + SecurityArch 도입" 1 절 추가
- **`docs/change-plans/cfp-*.md`** (기존): historical record, 변경 안 함
- **`presets/webapp/agents/BackendDeveloperAgent.md`**: Mapper/Refactor 인용만, 변경 불필요
- **`templates/review-checklists/code.md`, `security.md`**: design 외 lane이라 영향 없음
- **`agents/ClaudeReviewAgent.md`, `CodexReviewAgent.md`**: lane-agnostic worker, packet은 PL이 작성하므로 worker md 변경 불필요
- **`.github/workflows/*.yml`**: workflow logic이 agent 이름을 직접 참조하지 않음
- **`.github/CODEOWNERS`**: agent 변경과 무관

### 7.7 총합

- **신규 파일**: 3
- **수정 파일**: 18
- **무변경**: 기존 Story files, 워크플로우, 일부 templates

---

## 8. Migration & Self-Application

### 8.1 Self-application paradox

CFP-17 자체가 ArchitectPL + SecurityArch 도입 Story인데, **개발 시점에는 옛 구조만 존재**:
- CFP-17 설계 단계에서 ArchitectPL은 아직 없음 → ArchitectAgent 단독이 Change Plan 작성
- CFP-17 설계 단계에서 SecurityArch는 아직 없음 → §7 보안 설계는 ArchitectAgent가 직접 작성
- CFP-17 PR merge 직후부터 새 구조 발효 → 다음 Story (CFP-18+)부터 ArchitectPL + SecurityArch 가동

**해결**: CFP-17 자체는 옛 구조로 진행, 머지 직후 v0.11.0 cut → 다음 Story부터 새 구조.

CFP-17 Story file §7 보안 설계는 옛 ArchitectAgent가 작성. 내용:
> §7. 보안 설계 — N/A. agent md / template / docs 변경. 외부 입력·인증·민감데이터 흐름 변경 0개. trust boundary 변경 없음.

### 8.2 CFP-17 자체의 lane 통과 (plugin meta dogfooding)

CLAUDE.md "Plugin meta 변경은 무의미한 lane을 N/A — <사유>로 명시" 패턴 그대로:

| Lane | CFP-17에서 처리 |
|------|----------------|
| 요구사항 | `docs/stories/CFP-17.md` §1-6 verbatim (본 spec 기반) |
| 설계 | ArchitectAgent 단독 (옛 구조) → Change Plan 작성 (CFP-17은 §7 N/A) |
| 설계 리뷰 | DesignReviewPL 정상 진행 (Claude+Codex). §7 N/A 사유 검사 |
| 구현 | DocsAgent 단독 writer (모든 변경이 agent md / template / docs / .claude-plugin/plugin.json) |
| 구현 리뷰 | CodeReviewPL — scope: docs/agents/templates 일관성·SSOT drift 위주 |
| 구현 테스트 | TestAgent — N/A (실행 가능한 코드 0). 단 `invariant-check.yml` workflow가 agent count·frontmatter·CLAUDE.md 표 parity 자동 점검 — 본 CFP가 신규 agent 2종 추가하므로 invariant 매핑 갱신 필수 |
| 보안 테스트 | SecurityTestPL — N/A (코드 0). 1차 layer (Dependabot/CodeQL/Secret Scanning) 자동 통과 |

### 8.3 Consumer 프로젝트 호환성

**v0.10.0 → v0.11.0 upgrade**:
- **Breaking 영향**: 없음 (consumer는 ArchitectAgent를 직접 호출하지 않음, Orchestrator 경유)
- **Template 영향**: `change-plan.md` §7 추가. 기존 change-plans 파일 회귀 갱신 불필요 — 신규 Story부터 적용
- **Overlay 영향**: `.claude/_overlay/project.yaml` schema 변경 없음

**docs/migration-guide.md 신규 절** (DocsAgent가 작성):
```markdown
## v0.10.0 → v0.11.0

### 변경 사항
- 신규 에이전트 2종: ArchitectPLAgent (설계 lane PL), SecurityArchitectAgent (설계 lane deputy)
- ArchitectAgent 역할 변경: 단독 PL → ArchitectPL 직속 chief author
- Change Plan template 신규 §7 보안 설계 섹션 — 신규 Story부터 적용

### Consumer 액션 필요
- 없음 (Orchestrator 경유 호출이라 직접 영향 없음)
- 권장: SessionStart hook 재실행해 새 agent md 인식

### 기존 docs/change-plans/* 회귀 갱신 불필요
- 과거 Change Plan은 historical record로 보존
- 새 §7 섹션은 v0.11.0 이후 신규 Story부터 적용
```

### 8.4 In-flight 충돌 검사

CFP-16 (invariant-check severity_overrides count + breakdown parity)은 이미 머지 완료 (commit `260ff37`, PR #48). v0.10.0 sprint 마무리 (commit `3bda565`, PR #49)도 main에 들어옴.

CFP-17 시작 시점 충돌 우려 없음 — main `3bda565`에서 깨끗이 분기 가능.

### 8.5 CFP-17 자체의 trigger 방식

**CLAUDE.md 표준 경로**: 사용자가 GitHub Issue Form (story.yml) 제출 → story-init.yml Action 자동 CFP-17.md 생성 + Phase 1 PR open

**사용자가 정해야 할 것** (writing-plans 단계 직전 결정):
- (a) GitHub Issue Form으로 정상 trigger (이 spec을 §1에 paste) — workflow 자체 dogfooding
- (b) Manual: 직접 `docs/stories/CFP-17.md` 생성 + manual Phase 1 PR

(a) 권장. workflow를 자체 dogfooding하고, story-init.yml Action 검증.

### 8.6 Rollback 전략

v0.11.0 머지 후 issue 발견 시:
- **Forward fix 우선**: v0.11.1 hotfix
- **Last resort rollback**: consumer가 plugin pin을 v0.10.0으로 다운그레이드 (`/plugins install codeforge@0.10.0`)
  - data migration 0건이라 안전

---

## 9. Open Issues / Future Work

### 9.1 Phase 2 후속 CFP 후보 (이번 범위 제외)

Codex 감사에서 식별된 나머지 공백:

| Codex # | 공백 | 권고 | 후속 CFP |
|---------|------|------|----------|
| #1 | §8 Test Contract 단독 작성 | TestContractArchitectAgent 신설 | CFP-18 후보 |
| #2 | 데이터/스키마 마이그레이션·롤백 | DataMigrationArchitectAgent 또는 §섹션 추가 | CFP-19 후보 |
| #4 | 관측성·운영 준비도 | DesignReview checklist 확장 | CFP-20 후보 (low risk) |
| #5 | API 호환성·에러 semantics | Architect 책임 확장 + design.md checklist | CFP-20 후보와 묶음 가능 |
| #6 | 성능 SLO·용량·핫패스 예산 | DesignReview checklist 확장 | CFP-20 후보와 묶음 가능 |

본 CFP-17이 머지된 후, PMOAgent가 Cross-Story 회고에서 우선순위를 검토 (CLAUDE.md PMOAgent 책임).

### 9.2 옵션 (D) — Codex deputy 추가 검토

Architect lane에 Codex를 5번째 deputy로 추가하는 옵션은 **unique angle 정의 모호**로 본 CFP에서 제외. 향후 명확한 angle (예: "alternative architecture proposer", "domain-naive outsider perspective")이 정의되면 별도 CFP로 검토.

### 9.3 옵션 (B) — Author + Reviewer 패턴

Architect (Claude) author → Codex가 draft 리뷰 패턴은 **DesignReview lane과 중복**으로 본 CFP에서 제외. DesignReview 단계에서 이미 Claude+Codex 병렬 리뷰가 작동.

### 9.4 향후 Architect deputy 5+로 확장 시 부담

본 CFP-17으로 deputy 4인 (Mapper/Refactor/SecurityArch/Architect-as-author). Phase 2에서 TestContract·DataMigration까지 추가하면 6인. ArchitectPL의 synthesis 부담이 증가 — 향후 PL이 deputy outputs 통합에 어려움 겪으면 Section-level decomposition (§3은 Architect, §7은 SecurityArch가 직접 author 등) 재검토.

---

## 10. Acceptance Criteria

CFP-17 머지 시 다음이 모두 통과해야 한다:

### 10.1 신규 파일 존재
- [ ] `agents/ArchitectPLAgent.md` — frontmatter `model: claude-opus-4-7`, permissions §4.1 일치
- [ ] `agents/SecurityArchitectAgent.md` — frontmatter `model: claude-opus-4-7`, permissions §4.3 일치
- [ ] `docs/adr/ADR-004-architectpl-securityarch-restructure.md` — status `Accepted`, related_files에 §7.1-7.3 명시 파일 list

### 10.2 수정 파일 일관성
- [ ] `agents/ArchitectAgent.md` 책임 이관 4건이 본문에 반영됨 (Mapper/Refactor 스폰 trigger 삭제, FIX 최종 판정 → PL, Impl Manifest 감사 → PL, ADR draft 명문화)
- [ ] `agents/CodebaseMapperAgent.md`, `agents/RefactorAgent.md` 상위가 `ArchitectPLAgent`로 변경, 대립 파트너 SecurityArch 추가
- [ ] `templates/change-plan.md` §7 보안 설계 신설, 기존 §7 placeholder 제거
- [ ] `templates/review-checklists/design.md` §7 차단 항목 + SecurityArch 산출물 감사 항목 추가
- [ ] `CLAUDE.md` 다이어그램·Never-skippable·스폰 시퀀스·책임 매트릭스·FIX decision table·병렬 스폰 권장·Write 권한 모두 갱신
- [ ] `docs/orchestrator-playbook.md` Architect spawn template, FIX state machine, write queue, Context Packet 모두 ArchitectPL 반영
- [ ] `.claude-plugin/plugin.json` version 0.11.0, "22 core 에이전트"

### 10.3 Workflow / Lint 통과
- [ ] phase-gate-mergeable workflow PASS
- [ ] story-section-1-immutable workflow PASS
- [ ] phase-label-invariant workflow PASS (단일 phase 라벨 유지)
- [ ] **invariant-check workflow PASS** — agent count·frontmatter·CLAUDE.md 표 parity (CFP-13/16 도입). 본 CFP-17이 agent 2종 추가 + 책임 매트릭스 변경하므로 invariant-check가 새 count·매핑을 통과해야 함
- [ ] subissue-from-impl-manifest workflow PASS (Phase 2 PR §8.5 매핑표 → sub-issue 자동 생성)
- [ ] fix-ledger-sync workflow PASS (FIX iteration 발생 시 Issue mirror)
- [ ] CLAUDE.md "필수 의존성 SSOT" SessionStart hook 변동 없음 (필수 플러그인·MCP 그대로)

### 10.4 Self-application dogfooding 통과
- [ ] CFP-17 자체의 Story file §7 = "N/A — meta change. 외부 입력·인증·민감데이터 흐름 변경 0개" 명시
- [ ] CFP-17 자체의 §8 Test Contract = "N/A — agent md/template/docs 변경, 실행 가능 코드 0" 명시
- [ ] DesignReview lane이 §7 N/A 사유를 인정해 PASS

### 10.5 Migration 문서
- [ ] `docs/migration-guide.md`에 v0.10.0 → v0.11.0 절 추가
- [ ] `CHANGELOG.md` v0.11.0 entry 추가

### 10.6 검증 시나리오 (post-merge, 다음 Story로 검증)
- CFP-18+ Story가 정상으로 ArchitectPL을 통해 진행됨 (Phase 1 PR open → 4 deputy 병렬 → Architect 통합 → PL 검수 → DesignReview)
- 신규 Change Plan에 §7 섹션이 채워짐 (외부 입력 있는 Story) 또는 §7.6 N/A 사유가 명시됨

---

## 11. Decision Log (brainstorming 트레이스)

| 시점 | 질문 | 옵션 | 채택 | 사유 |
|------|------|------|------|------|
| Q1 | 보안 설계 공백 해소 방법 | 신규 deputy / DesignReview 확장 / 현 구조 유지+보강 | (1) SecurityArchitectAgent | 대칭성·shift-left·Mapper/Refactor 패턴 정합 |
| Q1.5 | ArchitectAgent 책임 공백 audit | (사용자 추가 요청) | Codex와 병행 감사 | 독립 관점으로 7건 식별 |
| Q2 | ArchitectPL 분리 후 demoted Architect 역할 | (A) Solution / (B) Quality / (C) 강등 없음 단순 PL 추출 | (C) | 변경 최소·docs ripple 최소·기존 의미 보존 |
| Q3 | 본 Story 번들 범위 | (1) α만 / (2) α+β / (3) α+β+γ | (3) | ADR draft 명문화 1줄이라 묶어도 cost 적음 |
| Q4 | PL ↔ Architect 책임 분담 | (i) Architect-heavy / (ii) PL-heavy / (iii) Section split | (i) | (C)의 원 취지 부합·단일 author 일관성 |
| Q5 | SecurityArch 산출물 destination | (a) 신규 §섹션 / (b) §3 sub / (c) 별도 파일 / (d) 하이브리드 | (a) | 가시성·강제력·SSOT 일관성 |
| Q6 | Architect Claude+Codex 병렬 author? | (A) 두 author / (B) Author+Reviewer / (C) Claude 단독 / (D) Codex deputy | (C) | 통합 결정 dedup 불가·DesignReview에서 Codex 검토 이미 작동·Architect 토큰 비용 부담 |

---

## 12. References

- CLAUDE.md (orchestration overview)
- agents/ArchitectAgent.md (현재 책임 SSOT)
- agents/CodebaseMapperAgent.md
- agents/RefactorAgent.md
- agents/DesignReviewPLAgent.md
- agents/SecurityTestPLAgent.md
- templates/change-plan.md (§7 신설 대상)
- templates/review-checklists/design.md
- docs/orchestrator-playbook.md
- docs/adr/ADR-001-review-agent-unification.md (Review worker 통합 — design.md checklist 패턴 참조)
- docs/adr/ADR-003-three-layer-drift-responsibility.md (3 layer drift 책임 분리 — 참조)
- Codex 감사 결과 (본 brainstorming 세션 내 inline)

---

**Next step**: 사용자 spec 검토 → 승인 시 `superpowers:writing-plans` skill 호출 → 구현 plan 작성 → CFP-17 GitHub Issue Form 제출 (옵션 a) 또는 manual trigger (옵션 b).
