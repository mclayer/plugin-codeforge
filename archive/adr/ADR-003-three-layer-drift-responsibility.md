---
adr_number: 003
title: SSOT drift 검출·회복 책임을 3 layer로 분리 (CI invariant / SessionStart 부트스트랩 / 사용자 가이드)
status: Accepted
category: Team & Process
date: 2026-04-27
related_files:
  - .github/workflows/invariant-check.yml
  - overlay/hooks/check-bootstrap.sh
  - scripts/bootstrap-labels.sh
  - docs/consumer-guide.md
  - overlay/hooks/regen-agents.sh
related_stories:
  - CFP-5
  - CFP-6
  - CFP-7
  - CFP-8
  - CFP-9
  - CFP-10
  - CFP-11
  - CFP-12
  - CFP-13
is_transitional: false
---

# ADR-003: SSOT drift 검출·회복 책임을 3 layer로 분리 (CI invariant / SessionStart 부트스트랩 / 사용자 가이드)

## 상태

`Accepted` (2026-04-27)

## 컨텍스트

CFP-1 self-application 정책 도입 이후 plugin이 자기 자신의 SSOT 정합을 자동 검증·회복하는 layer를 점진적으로 도입했다 (CFP-5~13).

**누적 layer 3종이 자연스럽게 분화됨**:

1. **CI invariant** (PR-time): `.github/workflows/invariant-check.yml` Step 1-7
   - SSOT 코드 정합 (workflow parity / version match / agent count / write queue 권한 / ADR-002 footer / 3-lane category enum / migration BREAKING)
   - 매 PR 시 자동 실행, drift 시 PR block

2. **SessionStart 부트스트랩** (session-time): `overlay/hooks/check-bootstrap.sh` + `scripts/bootstrap-labels.sh`
   - 환경 정합 (org permission / 18 plugin label 존재)
   - 매 session 시작 시 비차단 WARN, 수동 회복 안내

3. **사용자 가이드** (read-time): `docs/consumer-guide.md` §2 부트스트랩 단계
   - 1회 setup 절차 (workflow copy / labels / branch protection / org permission)
   - consumer가 plugin 적용 첫 단계에서 read

3 layer는 **다른 lifecycle**·**다른 회복 메커니즘**·**다른 autonomy 수준**을 가진다:

| Layer | Lifecycle | 회복 방식 | Autonomy |
|-------|-----------|-----------|----------|
| CI invariant | PR open / push | 자동 차단 (block PR) | 완전 자동 |
| SessionStart | 매 session | 비차단 WARN + 수동 안내 | 반자동 (drift 검출만) |
| 사용자 가이드 | 1회 read | manual setup | 사람 책임 |

CFP-11 end-to-end 실증에서 **3 layer 모두 필요함이 입증**됨:
- 코드 drift (sed Korean) → CI invariant로 catch 가능했던 영역
- 환경 drift (org permission) → SessionStart 부트스트랩으로만 catch 가능
- bootstrap drift (label 부재) → 가이드가 우선이지만 SessionStart로 reminder

향후 새 drift 검출 책임이 등장할 때 **어느 layer에 둘지 결정 기준이 부재**하면 다음 위험:
- 잘못된 layer 선택으로 false positive (e.g., 환경 정합을 CI block으로 쓰면 CI 인프라 ↔ consumer 환경 결합)
- 중복 검증 (e.g., 동일 drift를 3 layer 모두에서 catch)
- layer 누락 (drift 종류가 어느 layer에도 없음 — CFP-11 사례)

본 ADR은 3 layer 책임을 형식화해 향후 drift 검출 신규 추가 시 layer 선택 결정을 principled하게 만든다.

## 결정

### 1. Layer 책임 매트릭스

```
                  CI invariant       SessionStart 부트스트랩        사용자 가이드
                  (PR-time)          (session-time)                  (read-time)
                  ───────────────    ──────────────────────────────  ─────────────────
대상                코드·문서 정합     환경·인증 정합                 1회 setup 절차
검증 시점          매 PR              매 session 시작                consumer 첫 setup
회복 메커니즘      block PR until fix  WARN + 수동 안내               manual 따라하기
실패 비용         CI red (가시)       stderr 1줄 (저가시)            가이드 미독자에 전달 0
auto-fix?          미적용 (manual)    미적용 (manual)                미적용 (manual)
대표 산출물        invariant-check.yml  check-bootstrap.sh             consumer-guide.md
                                       + bootstrap-labels.sh
```

### 2. Layer 선택 결정 기준

새 drift 검출 책임 도입 시 다음 3가지 질문 순서대로 답해 layer 결정:

#### Q1. Drift 발생 지점이 plugin repo 내부인가, consumer 환경인가?

- **plugin repo 내부** (e.g., agents/*.md frontmatter ↔ CLAUDE.md 표 정합) → **CI invariant 후보**
- **consumer 환경** (e.g., GitHub repo settings, label 존재, org permission) → **SessionStart 부트스트랩 후보**
- **둘 다 아닌 1회 setup 절차** (e.g., gh auth login 안내) → **사용자 가이드 단독**

#### Q2. 자동 회복 가능한가?

- **자동 회복 가능** (e.g., label create) → 회복 script + SessionStart 안내
- **자동 회복 불가능 (admin 권한 필요 등)** → SessionStart WARN + 가이드 안내
- **자동 회복 위험** (e.g., 데이터 손실 가능) → 가이드 단독 (사람 결정)

#### Q3. 검증 비용이 PR-time에 적합한가?

- **저비용 (ms~초 단위)** → CI invariant 그대로
- **고비용 (외부 API 호출, network 의존)** → SessionStart로 옮김 (PR마다 호출 회피)
- **검증 자체가 신뢰 안 됨 (false positive 위험)** → 가이드만

### 3. Layer 간 중복 회피 원칙

동일 drift를 2 layer 이상에서 검증하지 않는다 (단 2가지 예외):

**예외 1: SessionStart가 가이드의 reminder 역할**
- 가이드 §2 부트스트랩 단계가 SessionStart에서도 비차단 WARN으로 reminder 가능
- 정당화: 가이드만으론 사용자 attention drop이 있고 SessionStart는 매 session 비차단 알림만 (저비용)
- 사례: org permission 설정 (가이드 §2g + check-bootstrap.sh)

**예외 2: CI invariant가 가이드의 enforcement**
- 가이드에서 "이렇게 작성하세요"가 invariant로 enforce 가능
- 정당화: 가이드는 한 번 읽고 끝, 자동 검증이 진정한 SSOT
- 사례: ADR-002 footer 패턴 (가이드 + invariant Step 5)

이 외 중복은 drift이며 ADR 변경 또는 layer 통합 PR로 해결.

### 4. CFP-1~13에 적용된 책임 매핑

| CFP | Drift 종류 | Layer | Q1 답 | Q2 답 | Q3 답 |
|-----|-----------|-------|-------|-------|-------|
| 5 | workflow parity / version / agent count | CI invariant | repo 내부 | 수동 회복 | 저비용 |
| 6 | story_cutoff schema (config 검증) | SessionStart (validate_config.py) | repo·consumer 둘 다 (overlay) | 수동 (config 편집) | 저비용 |
| 7 | frontmatter ↔ CLAUDE.md 표 | CI invariant | repo 내부 | 수동 | 저비용 |
| 8 | ADR-002 footer | CI invariant | repo 내부 | 수동 | 저비용 |
| 9, 13 | review category enum | CI invariant | repo 내부 | 수동 | 저비용 |
| 10 | migration ↔ CHANGELOG | CI invariant | repo 내부 | 수동 | 저비용 |
| 11 | (sed Korean) workflow exec | CI catch via test (PR #40) | repo 내부 | 자동 (수정) | 저비용 |
| 12 | org permission | SessionStart 부트스트랩 + 가이드 | consumer 환경 | 자동 회복 불가 (admin) | 고비용 (gh API) |
| 12 | 18 label | SessionStart 부트스트랩 + 가이드 + script | consumer 환경 | 자동 회복 가능 (script) | 저비용 |

본 매핑은 추가될 미래 CFP가 layer 결정 시 reference로 사용.

## 결과

### 긍정

- **drift 책임 명확화**: 새 drift 검출 추가 시 어느 layer에 둘지 3 질문으로 principled 결정. 잘못된 layer 선택 회피
- **중복 회피**: 동일 drift를 여러 layer에서 검증하는 비용 차단 (예외 2종 명시)
- **layer 간 보완 보존**: 예외 2종으로 reminder + enforcement 협력 인정 (가이드만으론 부족)
- **CFP-1~13 사후 정합화**: 13 Story가 무계획적으로 만든 layer가 사후에 일관 architecture로 정리됨 (ratchet 패턴 입증)

### 부정 / 트레이드오프

- ADR 1개 추가로 plugin meta 복잡도 ↑ (단 3 layer는 이미 존재 — 본 ADR은 명시화만)
- Q1-Q3 결정 tree가 너무 단순할 가능성 (실제 사례에서 모호한 case 발생 가능). 그 경우 본 ADR 변경 PR로 case 추가
- "예외 2종" 정의가 시간 흐름에 따라 expand 가능 — 변경 시 본 ADR을 supersede 또는 amendment

### 대안 (기각)

| 대안 | 기각 사유 |
|------|----------|
| **A. 단일 layer (CI invariant only)** | 환경 drift (org permission)는 PR-time에 검증할 수 없음. consumer-side 정보 필요 |
| **B. 단일 layer (SessionStart only)** | 코드 drift는 PR-time에 block해야 main branch 보호 가능. session-time만은 너무 늦음 |
| **C. 단일 layer (가이드 only)** | CFP-11이 입증 — 가이드만으론 사용자 attention drop 시 fail. 자동 검출 layer 필수 |
| **D. layer 4개 이상** | YAGNI — 현재 사례에서 3 layer로 모두 cover. 4번째 layer가 필요한 시점에 본 ADR supersede 또는 amend |

## 해소 기준

N/A — permanent policy



```
                            [Drift 종류 도입]
                                    │
                                    ▼
                          ┌─────────────────────┐
                          │  Q1: 발생 지점?     │
                          │  plugin repo /      │
                          │  consumer 환경 /    │
                          │  1회 setup          │
                          └─────────────────────┘
                                    │
                ┌───────────────────┼───────────────────┐
                ▼                   ▼                   ▼
         repo 내부           consumer 환경           1회 setup
                │                   │                   │
                ▼                   ▼                   ▼
         ┌───────────┐       ┌──────────┐       ┌────────────┐
         │ CI invariant │   │ Q2: auto?  │   │ 사용자 가이드 │
         │ (PR block)  │   └──────────┘       │ (read-time)  │
         └───────────┘             │           └────────────┘
                                   ▼
                         ┌──────────────────┐
                         │  자동 / 수동      │
                         └──────────────────┘
                                   │
                            ┌──────┴──────┐
                            ▼             ▼
                       Script + WARN     WARN only
                       (예: labels)    (예: org perm)
                                   │
                                   ▼
                          ┌────────────────────┐
                          │ SessionStart       │
                          │ check-bootstrap.sh │
                          └────────────────────┘
```

## 관련 파일

- 본 ADR이 형식화한 3 layer 산출물:
  - `.github/workflows/invariant-check.yml` (Layer 1: CI invariant, Step 1-7)
  - `overlay/hooks/check-bootstrap.sh` (Layer 2: SessionStart 부트스트랩)
  - `scripts/bootstrap-labels.sh` (Layer 2: 자동 회복 script)
  - `docs/consumer-guide.md` §2a-2h (Layer 3: 사용자 가이드)
- CFP-11이 발견·입증한 3 layer 필요성: [`docs/stories/CFP-11.md`](https://github.com/mclayer/codeforge-internal-docs/blob/main/wrapper/stories/CFP-11.md)
- CFP-12가 layer 2 정합화: [`docs/stories/CFP-12.md`](https://github.com/mclayer/codeforge-internal-docs/blob/main/wrapper/stories/CFP-12.md)
