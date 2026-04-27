# CFP-16: invariant-check Step 8 — severity_overrides count + breakdown parity (CFP-13/14 후속)

## 1. 사용자 요구사항 (verbatim — story-section-1-immutable.yml로 변경 차단)

CFP-15 PR #47 머지 직후 사용자 (autonomy mode 인가 연장):

> "merge하고 다음 작업. 모든 권한에 승인 없이 실행해"

CFP-13 §11 + CFP-14 §11에서 잠정 후속으로 enumerate한 항목:

> CFP-15/CFP-16 (잠정): severity_overrides parity (3 lane × 3 location 같은 패턴) — string equality 불가, 별도 design 필요

본 Story는 그 design을 결정 후 적용. **string equality 회피 + count + severity (P0/P1) breakdown parity**가 의미 있는 절충점.

## 2. 도메인 해석

본 Story의 도메인은 **drift 검출 가능한 가장 약한 invariant**. CFP-9/13 (string equality)은 SSOT와 mirror가 동일 form일 때 적용 가능했지만 severity_overrides는:

- SSOT: verbose Korean (`**X** → P0 강제 (\`category\`) — Hexagonal/Clean Architecture ADR 준수`)
- PL: condensed Korean (`"X → P0"`)
- Codex: 의도적 영문 요약 (`Auto-P0: ADR violation, §8 missing, §3-6 sections missing.`)

3 location form이 **의도적으로 다름**. canonical string 강제는 SSOT 본문 부자연스럽게 만들거나 Codex 프롬프트 영문 요약을 깨뜨림 (LLM 입력 quality 영향). string equality 적용 불가.

대안:
- **Count + breakdown parity**: bullet 개수 + P0/P1 분포. drift 검출 충분, content equivalence는 PR review 의존
- **canonical phrasing**: SSOT/PL을 동일 string으로 강제. 가독성 손실
- **LLM-based equivalence**: semantic 비교. over-engineering + cost

채택: **count + breakdown parity**. ADR-003 §3.2 "Q3 검증 비용이 PR-time에 적합한가" 기준에서 저비용 + 의미 있음.

- 도메인 제약: SSOT는 verbose Korean, PL은 condensed, Codex는 영문 요약 — 동시에 보존
- 암묵 가정: count + P0/P1 분포가 다르면 drift (실제 사용 시 가장 빈번한 사고 패턴)
- 범위 경계: SSOT ↔ PL만 cover (Codex는 영문 요약이라 scope 외)
- 우선순위: 마지막 enumerate된 잠정 후속 close

지식 공백: 없음.

## 3. 관련 ADR

- **ADR-001**: 워커 통합 packet 구조의 mirror — 본 Story가 그 mirror 정합 확장 (severity_overrides field)
- **ADR-002/003**: 무관
- 신규 ADR 필요 없음

ADR-003 §3.2 Q3 (검증 비용)에 따라 PR-time CI invariant layer 채택 — 동일 결정 일관성.

## 4. 관련 코드 경로

| 경로 | 변경 유형 | 변경 후 책임 |
|------|-----------|--------------|
| `.github/workflows/invariant-check.yml` | 수정 (Step 8 추가) | 3 lane × SSOT/PL severity_overrides count + P0/P1 분포 정합 |
| `docs/stories/CFP-16.md` | 신규 | 본 Story file |
| `docs/change-plans/cfp-16-severity-overrides-count-parity.md` | 신규 | Change Plan |

## 5. 요구사항 확장 해석

### 유스케이스

1. **새 severity 룰 추가 (예: design lane에 "P1 룰 1개")**: SSOT만 추가하면 count drift detect → PL 동시 갱신 강제
2. **severity 변경 (P0 → P1)**: SSOT만 변경하면 P0/P1 분포 drift detect
3. **drift 발견 시 reviewer는 content 검토**: count 정합 = 룰 1:1 매칭 가능성 보장. content equivalence는 reviewer 책임

### Acceptance Criteria

- [x] Step 8 추가 (Python parser ~95줄)
- [x] 3 lane (design/code/security) × SSOT/PL 정합 검증
- [x] count 일치 + P0/P1 breakdown 일치 검증
- [x] Codex 프롬프트는 명시적으로 scope 외 (의도적 영문 요약)
- [x] 4 test case PASS:
  - Test 1: 3 lane 모두 정합 OK (design 3 bullet 3 P0 / code 3 bullet 3 P0 / security 7 bullet 4 P0 + 3 P1)
  - Test 2: design SSOT P1 1개 추가 → count + P1 drift detect (2건)
  - Test 3: code PL 1개 제거 → count + P0 drift detect (2건)
  - Test 4: security SSOT P0→P1 변경 → P0/P1 drift detect (2건)

### 엣지 케이스

- **SSOT bullet에 multiple severity 등장 (예: "→ P0 또는 P1")**: regex `→\s*P\d`가 multiple match — 모두 카운트 (현재 사례 없으나 미래 보장)
- **PL list 빈 list**: regex match 실패 → "severity_overrides YAML list 부재" 1건 detect
- **section heading 변경**: regex match 실패 → 즉시 차단

### §5.5 사용자 확인 필요

- [✓] 사용자 자율 실행 모드 인가 연장
- [✓] CFP-13/14 §11 enumerate된 후속 채택
- [✓] string equality 미적용 결정 (3 location form 의도적 차이 보존)
- [✓] Codex 프롬프트 scope 외 결정 (영문 요약 의도)

## 6. 외부 지식 배경

본 변경은 plugin 내부 invariant 확장. 외부 지식 보강 불필요.

> "외부 지식 보강 불필요" 판정 사유: CFP-9/13 패턴의 약화 버전 (count-only). regex + Counter 표준 도구.

ADR 정합성: ADR-001 mirror enforce 확장 + ADR-003 §3.2 Q3 결정 기준 일관 적용. 통과.

## 7. 설계 서사

Change Plan: [`docs/change-plans/cfp-16-severity-overrides-count-parity.md`](../change-plans/cfp-16-severity-overrides-count-parity.md)

### 핵심 설계

**§3 도입할 설계**:
- SSOT 추출: `^## Severity 자동 룰` section 이후 `- ` bullet 추출
- PL 추출: `severity_overrides:` YAML list 추출
- 각 line에서 `→ P\d` 정규식으로 severity 추출 → Counter
- 비교: 총 bullet count + P0/P1 분포

### CodebaseMapper ↔ RefactorAgent 대립 결론

- **Mapper(보수)**: "CFP-9/13 string equality 패턴이 안 통하면 invariant 미적용 (자동 검증 포기)"
- **Refactor(혁신)**: "약한 invariant라도 drift detect 가능 — count + breakdown은 가장 빈번한 사고 패턴 catch"
- **채택: Refactor 우세**. ADR-003 §3.2 Q3 (검증 비용) 기준에서 저비용 + 의미 있음. content equivalence는 PR review로 보완. 약한 invariant도 0% 검증보단 강력.

## 8. 개발 서사

### §8.1-8.4 산출물

**N/A — Plugin meta workflow 확장**.

### §8.5 Impl Manifest

| 파일 경로 | 변경 유형 | 담당 | 변경 줄 수 (대략) | 상위 요건 ref |
|-----------|-----------|------|-------------------|---------------|
| `.github/workflows/invariant-check.yml` | 수정 (Step 8 추가) | DocsAgent | +95 | Change Plan §3 |
| `docs/stories/CFP-16.md` | 신규 | DocsAgent | 신규 | Change Plan §5 |
| `docs/change-plans/cfp-16-severity-overrides-count-parity.md` | 신규 | DocsAgent | 신규 | Change Plan §5 |

## 9. 품질 게이트 이력

### §9.1-9.2 설계·구현 리뷰

**N/A** — Plugin meta workflow.

### §9.3 구현 테스트

**Local 4 test case PASS:**

| Test | 입력 | Expected | Actual |
|---|---|---|---|
| 1 | 현 plugin (3 lane 정합) | "✓ design: 3 bullets (P0=3)" + "✓ code: 3 bullets (P0=3)" + "✓ security: 7 bullets (P0=4, P1=3)" | matched ✓ |
| 2 | design SSOT P1 1개 추가 | count + P1 drift 2건 | matched ✓ |
| 3 | code PL 1개 제거 | count + P0 drift 2건 | matched ✓ |
| 4 | security SSOT P0→P1 변경 | P0/P1 drift 2건 | matched ✓ |

기존 Step 1-7 정상 동작.

### §9.4 보안 테스트

**N/A** — local Python parser.

## 10. FIX Ledger

| Iter | 시각 | 레인 | 트리거 | 원인 판정 | 재실행 범위 | RESET? |
|------|------|------|--------|-----------|-------------|--------|

**비어있음**.

## 11. 회고

**발견 1 — 약한 invariant도 가치 있음**: CFP-9/13의 string equality pattern이 안 통하면 invariant 미적용으로 가는 게 아니라 **약한 invariant** 검토. count + breakdown은 가장 빈번한 drift (룰 추가/누락) 100% catch. content equivalence는 PR review가 보완.

**발견 2 — ADR-003 §3.2 Q3 기준의 가치**: 본 Story가 ADR-003 도입 후 첫 적용 사례. Q3 (PR-time 비용 적합) 기준으로 layer 결정 → CI invariant 채택 일관. ADR-003 §결정 기준의 reference 효용 입증.

**발견 3 — Codex 프롬프트는 scope 외 명시화**: 영문 요약은 LLM 입력 quality 위해 의도적 차이. invariant scope에서 명시 제외해 향후 reviewer가 "왜 Codex는 안 쳤지?" 질문할 때 즉시 답 가능.

**향후 작업**:
- **CFP-1~15 enumerate된 잠정 후속 모두 close** — 본 Story가 마지막
- 사용자 새 요구사항 또는 운영 중 발견 drift가 다음 trigger
- ADR-003이 향후 layer 결정 기준 reference로 작동
