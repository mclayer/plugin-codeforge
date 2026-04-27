# CFP-13: invariant-check Step 6 → 3 lane (design/code/security) 확장 (CFP-9 후속)

## 1. 사용자 요구사항 (verbatim — story-section-1-immutable.yml로 변경 차단)

CFP-12 PR #43 + chore PR #44 머지 직후 사용자 (autonomy mode 인가 연장):

> "merge하고 다음 작업. 모든 권한에 승인 없이 실행해"

CFP-12 §11 회고에 명시된 확장 후보:

> 확장 후보: severity_overrides·lane=design/security enum도 동일 invariant 적용 (별도 step 또는 Step 6 확장)

본 Story는 lane=design + lane=security category enum parity를 Step 6에 흡수 (Step 6 자체를 lane-loop refactor).

## 2. 도메인 해석

본 Story의 도메인은 **CFP-9 invariant pattern을 3 lane 전체로 확장**. CFP-9는 lane=code만 cover했지만 동일 mirror 패턴이 design/security lane에도 존재 (PL packet + Codex 프롬프트). 단일 Step에서 3 lane 모두 검증.

- 도메인 제약: 3 lane 각각 다른 SSOT path / PL md 파일 / Codex anchor
- 암묵 가정: Codex 프롬프트는 `#### lane=<X>` heading anchor로 lane 격리 (CFP-9 발견)
- 범위 경계: category_enum만. severity_overrides는 별도 step (또는 별도 Story)
- 우선순위: lane=design (6 cat) + lane=security (9 cat)도 lane=code (10 cat)와 동일 보장 받기

지식 공백: 없음 (CFP-9 pattern + 3 lane 사실적 분석).

## 3. 관련 ADR

- **ADR-001**: 워커 통합 결정의 mirror 구조 — 본 Story가 그 mirror의 정합 자동 검증 확장
- **ADR-002**: 무관
- 신규 ADR 필요 없음

## 4. 관련 코드 경로

| 경로 | 변경 유형 | 변경 후 책임 |
|------|-----------|--------------|
| `.github/workflows/invariant-check.yml` | 수정 (Step 6 lane-loop refactor) | 3 lane × 3 location = 9 정합 검증 |
| `docs/stories/CFP-13.md` | 신규 | 본 Story file |
| `docs/change-plans/cfp-13-extend-enum-parity-3-lanes.md` | 신규 | 본 Story Change Plan |

## 5. 요구사항 확장 해석

### 유스케이스

1. **새 design category 추가** (예: `pattern-misuse`): SSOT만 추가하면 invariant fail → DesignReviewPLAgent + CodexReviewAgent lane=design 동시 sync 강제
2. **security category SSOT 변경 (예: `pii` → `data-leak` rename)**: 3 location 모두 갱신 필요 detect
3. **CodexReviewAgent.md 구조 변경 시 lane=security anchor 부재**: regex match 실패 → 즉시 차단
4. **lane=code 기존 invariant 유지**: refactor 후에도 CFP-9 case 100% 동일 동작 (Test 4 검증)

### Acceptance Criteria

- [x] LANES list 3개 entry (design/code/security)
- [x] 각 lane SSOT path / PL name / Codex anchor 매핑
- [x] 4 test case 모두 PASS:
  - Test 1: 3 lane 모두 정합 OK (10+6+9 = 25 categories x 3 location)
  - Test 2: design SSOT 추가 → 2 drift detect (PL + Codex)
  - Test 3: security PL list 누락 → 1 drift detect
  - Test 4: code Codex 순서 변경 → 1 drift detect (CFP-9 invariant 유지)

### 엣지 케이스

- **Codex 프롬프트의 lane=design이 가장 먼저 등장**: CFP-9에서 발견한 self-discovery 재확인. 본 refactor에서 lane-anchor 패턴이 재사용되어 동일 위험 회피
- **lane 1개만 fail 시 다른 lane은 계속 검증**: `continue` 사용으로 부분 fail 시 다른 lane 결과도 보고

### §5.5 사용자 확인 필요 (모두 본 세션에서 확인 완료)

- [✓] 사용자 자율 실행 모드 인가 연장
- [✓] CFP-12 §11에 명시된 확장 후보 채택 (severity_overrides는 별도 후속)

## 6. 외부 지식 배경

본 변경은 CFP-9 pattern의 단순 확장. 외부 지식 보강 불필요.

> "외부 지식 보강 불필요" 판정 사유: CFP-9가 입증한 패턴을 3 lane × 3 location 매트릭스로 일반화. SSOT는 모두 plugin 내부.

ADR 정합성: ADR-001 mirror 구조 명시적 enforce. 통과.

## 7. 설계 서사

Change Plan: [`docs/change-plans/cfp-13-extend-enum-parity-3-lanes.md`](../change-plans/cfp-13-extend-enum-parity-3-lanes.md)

### 핵심 설계

**§3 도입할 설계**:
- LANES list로 3 lane parameter 통일 (lane name + PL agent name)
- SSOT path는 패턴화: `templates/review-checklists/{lane}.md`
- Codex anchor도 패턴화: `#### lane={lane}` heading + 첫 번째 `category from {...}`
- 검증 logic은 CFP-9 그대로 — 3회 반복 + lane prefix를 error message에

### CodebaseMapper ↔ RefactorAgent 대립 결론

- **Mapper(보수)**: "CFP-9 Step 6은 1 lane만 처리해 유지보수 단순. 3 lane은 Step 7/8/9로 분리해 설계 명확성 보존"
- **Refactor(혁신)**: "lane만 다른 동일 logic을 3 step으로 분리하면 200+ 줄 중복. lane-loop가 자연 추상화"
- **채택: Refactor 우세**. CFP-9 logic은 이미 충분히 검증됨. lane-loop 추상화로 75줄 → ~80줄 (sublinear 증가). Mapper의 분리 선호는 lane별 검증 logic이 다를 때 재검토 후보.

## 8. 개발 서사

### §8.1-8.4 산출물

**N/A — Plugin meta workflow 확장**.

### §8.5 Impl Manifest

| 파일 경로 | 변경 유형 | 담당 | 변경 줄 수 (대략) | 상위 요건 ref |
|-----------|-----------|------|-------------------|---------------|
| `.github/workflows/invariant-check.yml` | 수정 (Step 6 refactor) | DocsAgent | +24 / -19 (net +5) | Change Plan §3 |
| `docs/stories/CFP-13.md` | 신규 | DocsAgent | 신규 | Change Plan §5 |
| `docs/change-plans/cfp-13-extend-enum-parity-3-lanes.md` | 신규 | DocsAgent | 신규 | Change Plan §5 |

## 9. 품질 게이트 이력

### §9.1-9.2 설계·구현 리뷰

**N/A** — Plugin meta workflow.

### §9.3 구현 테스트

**Local 4 test case 결과:**

| Test | 입력 | Expected | Actual |
|---|---|---|---|
| 1 | 현 plugin (3 lane 모두 정합) | 3 lane × 3 location ✓ | "✓ lane=design: 6 categories x 3" + "✓ lane=code: 10 categories x 3" + "✓ lane=security: 9 categories x 3" ✓ |
| 2 | design SSOT에 `new-design-cat` 추가 | 2 drift (PL + Codex) | matched ✓ |
| 3 | security PL list에서 `race` 제거 | 1 drift (PL only) | matched ✓ |
| 4 | code Codex 순서 변경 (CFP-9 검증) | 1 drift (Codex only) | matched ✓ — CFP-9 invariant 유지 |

기존 Step 1-5/7 정상 동작 (regression 없음).

### §9.4 보안 테스트

**N/A** — local Python parser, attack surface 변경 없음.

## 10. FIX Ledger

| Iter | 시각 | 레인 | 트리거 | 원인 판정 | 재실행 범위 | RESET? |
|------|------|------|--------|-----------|-------------|--------|

**비어있음 — FIX 루프 미발생**.

## 11. 참조 + 회고

### 회고

**발견 1 — CFP-9 pattern은 3 lane × 3 location 매트릭스로 깔끔히 일반화**: 단일 lane invariant를 Story 1개에 검증하고, 검증된 패턴을 multi-lane으로 확장하는 ratchet이 자연스러움. CFP-5~10 기존 패턴(invariant-check.yml step 추가)에 더해 step 자체 확장도 포함.

**발견 2 — lane-loop는 sublinear 코드 증가**: 1 lane 75줄 → 3 lane 80줄. Mapper의 "step 분리" 우려는 logic 동일성 가정이 깨질 때만 재검토 가치 있음.

**발견 3 — severity_overrides는 별도 invariant 후보**: 본 Story는 category_enum만 cover. severity_overrides도 동일 mirror 구조이지만 category_enum과 결합도 낮아 별도 step(또는 별도 Story) 분리 가능.

**향후 작업 (별도 Story)**:
- **CFP-14 (잠정)**: severity_overrides parity (3 lane × 3 location 같은 패턴)
- **ADR-003 (조건부)**: invariant 자동화 / 환경 부트스트랩 / 사용자 가이드 3 layer 책임 분리 ADR
