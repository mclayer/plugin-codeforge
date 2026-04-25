# Change Plan 템플릿

ArchitectAgent가 설계 레인에서 작성하는 변경 계획서 표준 구조. DocsAgent가 `docs/change-plans/<slug>.md`에 저장.

**사용 대상**: ArchitectAgent (작성), DocsAgent (저장·Story 페이지 §7 미러링), DesignReviewPL (리뷰 대상), QADeveloperAgent (§8 Test Contract 입력), DeveloperPL·4 Dev (구현 입력)

---

## Frontmatter (필수)

```yaml
---
title: <한 줄 제목>
slug: <kebab-case-slug>
status: draft | in-review | approved | implemented
author: ArchitectAgent
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

### §3. 도입할 설계 (RefactorAgent 입력 기반)
- 신규 포트/어댑터/클래스 — **이름·시그니처·타입 확정**
- 레이어 경계·의존성 방향
- Mapper vs Refactor 대립 결론 (어느 쪽 채택했고 왜)
- 관련 ADR 정합성 (신규 ADR 필요 여부)

### §4. API 계약
- 라우트·요청/응답 스키마
- 컨텍스트·이벤트 스키마
- 의존성 (외부 라이브러리 · 내부 포트)
- 타입 정의

### §5. 변경 계획 (파일 단위)

| 파일 경로 | 변경 유형 | 담당 Agent | 설명 |
|-----------|-----------|------------|------|
| `src/...` | 추가·수정·제거 | BackendDev/Frontend/DataEng/ServerEng | 한 줄 |

### §6. 리팩토링 선행 작업 (Dev 실행 의뢰 명시)
- 요건 범위 내 리팩토링만 (전역 리팩터링 금지)
- 각 항목 담당 Dev 명시 (Backend/Frontend/DataEng/ServerEng)
- 단계별 테스트 통과 유지 방안

### §7 Impl Manifest 초안은 여기 비움 (구현 완료 후 DocsAgent가 Story 페이지 §8.5에 기록 — [`impl-manifest.md`](impl-manifest.md) 스키마 참조)

### §8. Test Contract (QADev TDD 입력 — 누락 시 DesignReview P0 차단)

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

### §9. 분기 선택 (필요 Dev 조합)
- 의존성 없는 한 **4 Dev 병렬 가능**
- 의존성 있으면 순서 명시 (예: DataEng 스키마 → Backend 어댑터)

### §10. ADR 대상 여부 + 기존 ADR 정합성 점검
- Change Plan 결정이 기존 ADR과 일치 / 주의 / 위반 (위반 시 신규 ADR 필요)
- 신규 ADR 필요 여부 (새 ADR은 [`adr.md`](adr.md) 템플릿 따름)

---

## DocsAgent 저장·미러링 의무

1. Architect가 확정 → DocsAgent가 `docs/change-plans/<slug>.md`에 저장
2. **저장 즉시** Story 페이지 §7에 요약 미러링 — "§1 목적 / §3 도입할 설계 / §4 API 계약 / §9 분기 선택"을 verbatim 또는 5-10줄 요약으로 복사
3. FIX 루프에서 갱신될 때마다 같은 파일 업데이트 (git 버전 히스토리 추적)

## 구현 진입 조건

- Change Plan 모든 섹션(§1-10) 존재 + DesignReview PASS
- Dev 스폰 전 Change Plan 저장 완료 필수
