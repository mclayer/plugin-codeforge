# Security Review 체크리스트 (lane=security)

SecurityTestPLAgent가 ClaudeReviewAgent / CodexReviewAgent에 packet으로 주입하는 보안 테스트 체크리스트. SSOT 분리는 [ADR-001](https://github.com/mclayer/plugin-codeforge/blob/main/archive/adr/ADR-001-review-agent-unification.md).

## 리뷰 대상 (scope_globs)

- 앱 코드: `src/**` (injection · trust boundary · credential · auth · 세션)
- 인프라 자산: `config/**`, `deploy/**`, `scripts/**` (secret hardcoding · 권한 과다 · 네트워크 노출)
- 의존성 매니페스트: `requirements.txt` · `package.json` · `go.mod` · `Cargo.toml` 등 (CVE 스캔)
- Story file §8.5 Impl Manifest (보안 검증 범위 확인 입력)

## 1차 layer 입력 (PL이 packet에 첨부)

SecurityTestPL은 GitHub native 1차 layer 결과를 fetch하여 워커 packet에 inline 첨부:
- Dependabot alerts (의존성 CVE)
- CodeQL findings (정적 분석)
- Secret Scanning (credential 노출)
- Push Protection 차단 이력

워커는 1차 layer가 이미 보고한 finding에 대해 high-level 분석(trust boundary·auth model)에 집중.

## Category enum (출력 분류)

`injection | trust-boundary | auth | credential | crypto | pii | dependency-cve | config | race`

## Severity 자동 룰

- **SQL/Command/Template injection 가능 경로** → P0 강제 (`injection`)
- **Credential / API key / token hardcode** → P0 강제 (`credential`)
- **Auth 우회 가능 경로** (권한 검증 누락) → P0 강제 (`auth`)
- **알려진 CRITICAL CVE 의존성** → P0 강제 (`dependency-cve`)
- **HIGH CVE** → P1
- **약한 crypto · nonce 재사용 · ECB 모드** → P1 강제 (`crypto`)
- **PII/금융/헬스 데이터 로그·response 유출** → P1 강제 (`pii`)

## 체크리스트 (9축)

### 1. Injection 공격 표면 (`injection`)

- SQL · Command · LDAP · XPath · NoSQL · Template injection 패턴
- 사용자 입력 → 데이터베이스 쿼리 · 셸 명령 · 템플릿 렌더링 경로 추적

### 2. Trust boundary 위반 (`trust-boundary`)

- 외부 입력(HTTP request · 환경변수 · 파일 · IPC 메시지) 검증 없이 내부 로직 진입
- type coercion · 크기 제한 · format validation 누락

### 3. Auth / 세션 결함 (`auth`)

- 권한 검증 누락 (특히 어드민·리소스 소유권 체크)
- CSRF · session fixation · JWT 무결성 · insecure cookie
- 인증·인가 로직 우회 경로

### 4. Credential / secret 노출 (`credential`)

- 코드 · config · log · error response에 API key · token · password · DB 접속정보 hardcoded
- `.env.example`에 실제 값 포함
- 1차 layer Secret Scanning 결과 교차 확인

### 5. 암호학 오용 (`crypto`)

- 약한 알고리즘 (MD5 · SHA1 · DES · RC4)
- 취약한 random (non-CSPRNG)
- nonce·IV 재사용, ECB 모드
- hardcoded key

### 6. 민감 데이터 처리 (`pii`)

- PII · 금융 · 헬스 · 보안 토큰의 로그 유출
- 응답에 과다 정보 포함 (debug info leakage)
- cache · 임시 파일 잔존

### 7. 의존성 취약점 (`dependency-cve`)

- 매니페스트 파일 읽어 known CVE 확인 (1차 layer Dependabot 결과 교차)
- 오래된 major 버전 사용
- WebSearch로 CVE DB 보강

#### 7.1 1차 layer (자동도구) ↔ 2차 워커 (web) 단계 구분 (CFP-2327 / ADR-124 Amendment 1)

보안 lane 의 외부지식 충당은 두 단계로 나뉘며 **2차 단계가 1차를 대체하지 않는다** (심화 관계).

| 단계 | 주체 | 도구 | 성격 |
|---|---|---|---|
| **1차 (자동도구)** | SecurityTestPL fetch 의무 (worker spawn 전) | Dependabot / CodeQL / Secret Scanning (+ trivy / hadolint, docker_first) | 자동 스캔 결과 — 이미 보고된 finding |
| **2차 (web)** | Claude/Codex 워커 WebSearch/WebFetch | NVD / GitHub Security Advisory (GHSA) / CISA KEV | 1차가 놓친 외부사실 의존 결론의 깊은 다출처 검증 |

워커는 1차 layer 가 이미 보고한 finding 은 skip 하고, **외부사실 의존 결론** (CVE 진위 · 공급망 · 표준 동작) 에만 2차 web 단계를 적용한다.

#### 7.2 2차 워커 web 단계 심화 3 요소 (외부지식 충당 3-단계 단계③ — ADR-124 Amendment 1)

외부사실 의존 결론에 한해 다음 3 요소로 web 조사를 심화한다 (단일 출처 단정 금지).

- **다출처 교차**: CVE·취약점 사실은 최소 2 출처 교차 (예: NVD CVE record + GHSA + CISA KEV catalog). 출처 간 severity·affected-range 불일치 시 finding `body` 에 명시.
- **adversarial verify**: "안전하다" 가 아니라 "이 버전·구성에서 알려진 악용 경로가 있는가" 로 반증 시도. fixed-version 주장은 advisory·changelog 원문 직접 확인 (벤더 단정 그대로 신뢰 금지).
- **시의성 (recency)**: 0-day / actively-exploited (CISA KEV 등재 등) vs mature / patched 구분. 시의성이 severity 판정에 영향 — KEV 등재 + 미패치 = severity 상향 근거.

#### 7.3 검사연극 차단 (필수)

- web 조사는 **외부사실 의존 지점 (CVE·공급망·표준) 한정**. injection 패턴·hardcoded credential 등 **내부 코드 사실 축** 결함에는 깊은 web 조사를 강제하지 않는다 (ADR-124 결정 2 / 결정 6 의존 X row, ADR-119 §결정 6).
- 네트워크 차단·외부 fetch 실패 시 재시도 없이 로컬 매니페스트 + 1차 layer 결과로 계속. 해당 finding `body` 에 "외부 CVE DB 교차 검증 실패 (network blocked)" 명시 (abstention escape — ADR-119 §결정 3.2).

### 8. 설정·배포 보안 (`config`)

- `config/**` · `deploy/**`의 디폴트 credential · open port · 과도한 권한
- TLS 미적용 / 약한 cipher suite
- file permission 과다 (예: chmod 777)

### 9. Race / TOCTOU (`race`)

- 검증(Time-of-Check)과 사용(Time-of-Use) 사이 race condition
- 파일 존재 확인 후 open까지 사이 취약점

## DAST 런타임 동적 축 (pointer — 신규 category 아님)

> **SSOT = §8.9 Test Contract (`change-plan.md`)** — 본 checklist 는 pointer 만 두고 DAST 계약을 중복 기재하지 않는다 (drift 회피, [ADR-150](https://github.com/mclayer/plugin-codeforge/blob/main/archive/adr/ADR-150-runtime-dast-security-axis.md) §결정 9).

DAST(런타임 동적 보안 검증)는 **신규 category 가 아니라 기존 9축의 런타임 거울면**이다 — 위 category_enum 무변경:

- **injection / auth / config / pii** = YES runtime mirror (실행 중 능동 재현·심각도 승격)
- **trust-boundary / credential / crypto** = PARTIAL wire-subset (외부 HTTP 경계·전송 중 credential·TLS negotiation 만)
- **dependency-cve / race** = NO (SCA·G4 concurrency 소관)

리뷰어는 **§8.9 레코드(applicability + 산출물 계약 필드)를 참조**하며, checklist 에 DAST 계약을 중복 기재하지 않는다. 실 DAST 결과 종합은 SecurityTestPL(`security_ai: true` opt-in, `tool_name=zap` SARIF fetch).

## 다음 게이트 (PASS 시)

- DocsAgent가 `gate:security-test-pass` 라벨 부착
- Phase 2 PR mergeable → merge → "Closes #<Story Issue>" → Issue 자동 close
- PMOAgent (회고) 트리거
- Story file §9.4 "보안 테스트 Iteration N" 누적

## 1차 원인 가정 (FIX 시)

원인 판정 표는 [CLAUDE.md](../../CLAUDE.md) "원인 판정 decision table" SSOT. 본 체크리스트는 보안 lane 카테고리 enum과 severity override만 담당하며, 원인 분기 표는 inline 복제하지 않는다 (drift 방지). PL이 1차 진단 → DeveloperPL이 재진단 → Architect 최종 판정.

## FIX 카운터

- **무제한** (테스트 레인 family 정책 — 보안 결함은 ESCALATE 없이 끝까지 수정)
- Story file §10에 `레인 = 보안-테스트` iteration 누적

## Consumer overlay 확장

Consumer는 `.claude/_overlay/templates/review-checklists/security.md`에 도메인 특화 보안 체크(예: 금융 PCI-DSS · 헬스 HIPAA · GDPR 데이터 분류)를 추가할 수 있다.
