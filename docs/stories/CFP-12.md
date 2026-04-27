# CFP-12: Bootstrap drift 자동 검출 + label 자동 부트스트랩 script (CFP-11 후속)

## §1. 사용자 요구사항 (verbatim — story-section-1-immutable.yml로 변경 차단)

CFP-11 PR #42 머지 직후 사용자 (autonomy mode 인가):

> "merge하고 다음 작업. 모든 권한에 승인 없이 실행해"

CFP-11 §11 회고에 명시된 후속 Story 2건 통합:

> CFP-12 (잠정): SessionStart hook에 `gh api repos/*/actions/permissions/workflow` check 추가 — `default_workflow_permissions == "write"` + `can_approve_pull_request_reviews == true` 검증
>
> CFP-13 (잠정): label 자동 bootstrap script — `scripts/bootstrap-labels.sh` 또는 SessionStart hook 통합

본 Story는 CFP-12/13을 단일 Story로 통합 — 둘 다 "환경 부트스트랩 drift 검출/회복"으로 책임이 동일.

## 2. 도메인 해석

본 Story의 도메인은 **환경 정합 자동 검출 layer**. CFP-1~10이 코드 정합(invariant CI)을 자동화했지만 CFP-11이 환경 정합(org permission, label 부재)은 별도 layer 필요함을 입증.

- 도메인 제약: SessionStart hook 비차단 (consumer 매 세션마다 실행, 실패가 hook 자체 abort로 이어지면 안 됨)
- 암묵 가정: gh CLI + python3 + PyYAML은 plugin 필수 의존 (이미 설치됨)
- 범위 경계: 검출(WARN) + 수동 회복 안내. 자동 fix는 권한 의존(org admin) 또는 신규 동작(label create — idempotent script로 분리)
- 우선순위: CFP-11이 발견한 2 환경 drift (org permission / label) 둘 다 cover

지식 공백: 없음 (CFP-11 발견 + GitHub API 표준 도구).

## 3. 관련 ADR

- **ADR-001/002**: 무관
- 신규 ADR 필요 없음 (CFP-11 §11에서 ADR-003 잠정 후보 거론했으나 본 Story는 그 detail에 도달 안 함)

## 4. 관련 코드 경로

| 경로 | 변경 유형 | 변경 후 책임 |
|------|-----------|--------------|
| `overlay/hooks/check-bootstrap.sh` | 신규 | non-blocking 부트스트랩 drift 검출 (org permission + 18 label 존재) |
| `overlay/hooks/regen-agents.sh` | 수정 | check-bootstrap 호출 wiring (project.yaml validate 직후) |
| `scripts/bootstrap-labels.sh` | 신규 | 18 plugin label idempotent 일괄 생성 |
| `docs/consumer-guide.md` | 수정 | §2d label section + §2f org permission section에 CFP-12 자동화 참조 추가 |
| `docs/stories/CFP-12.md` | 신규 | 본 Story file |
| `docs/change-plans/cfp-12-bootstrap-check-and-labels.md` | 신규 | Change Plan |

## 5. 요구사항 확장 해석

### 유스케이스

1. **신규 consumer가 plugin 적용 후 첫 세션 시작**: `regen-agents.sh` SessionStart hook이 `check-bootstrap.sh`를 호출해 org permission 미설정 시 stderr WARN 출력. consumer가 즉시 인지하고 §2f 따라 enable
2. **신규 consumer label 부재 상태**: `check-bootstrap.sh`가 18 label 중 N개 부재 detect. 안내 따라 `bash scripts/bootstrap-labels.sh` 1회 실행
3. **기존 consumer가 label 일부 삭제 (실수)**: 다음 세션 시작에서 부재 detect → 재실행으로 복구
4. **gh CLI 미설치 / 인증 만료**: check-bootstrap.sh silent skip — 다른 hook이 안내. SessionStart 자체 abort 회피

### Acceptance Criteria

- [x] `check-bootstrap.sh` non-blocking 동작 (exit 0, drift 시 stderr WARN만)
- [x] org permission 미설정 detect (default_workflow_permissions != "write" 또는 can_approve_pull_request_reviews != true)
- [x] 18 plugin label 부재 detect (개별 enumerate, 상위 5개만 표시)
- [x] `bootstrap-labels.sh` idempotent (기존 label은 update, 부재면 create)
- [x] regen-agents.sh wiring (project.yaml validate 직후, `|| true`로 비차단)
- [x] consumer-guide §2d/§2f에 자동화 script 참조 추가
- [x] Local 3 시나리오 PASS (idempotent / drift detect / non-blocking)

### 엣지 케이스

- **yq 미설치**: validate_config.py와 동일하게 `python3 + PyYAML` 사용으로 회피 (PyYAML은 이미 plugin 필수 의존)
- **org/repo 미설정 (project.yaml github.org 빈 값)**: silent skip (consumer 초기 설정 단계 가능)
- **gh api network failure**: silent skip (한 세션에 한 번 잃은 정보, 다음 세션에 재시도)
- **label 일부 다른 색상**: bootstrap-labels.sh가 `gh label edit`로 재정렬 (idempotent)

### §5.5 사용자 확인 필요 (모두 본 세션에서 확인 완료)

- [✓] 사용자 자율 실행 모드 인가 (CFP-8 시점부터 연장)
- [✓] CFP-11 §11 회고에 명시된 CFP-12/13 scope 그대로 적용
- [✓] CFP-12/13 통합 결정 (둘 다 환경 부트스트랩 drift 검출/회복으로 책임 동일)

## 6. 외부 지식 배경

본 변경은 plugin 내부 hook 확장. 외부 지식 보강 불필요.

> "외부 지식 보강 불필요" 판정 사유: GitHub API + PyYAML 표준 도구. CFP-11에서 발견된 drift 양상이 input.

ADR 정합성: ADR-001/002 무관. 통과.

## 7. 설계 서사

Change Plan: [`docs/change-plans/cfp-12-bootstrap-check-and-labels.md`](../change-plans/cfp-12-bootstrap-check-and-labels.md)

### 핵심 설계

**§3 도입할 설계**:
- `check-bootstrap.sh` (non-blocking 진단) + `bootstrap-labels.sh` (idempotent fix) 분리
- check는 SessionStart에 자동 wiring, fix는 manual (label create는 부수 효과 있는 동작이라 자동 실행 회피)
- yq 의존 회피 — PyYAML로 통일 (plugin 필수 의존만 사용)

### CodebaseMapper ↔ RefactorAgent 대립 결론

- **Mapper(보수)**: "consumer-guide에 단계 추가만으로 충분. SessionStart hook은 기존대로 조용히 동작"
- **Refactor(혁신)**: "drift는 발생할 수 있고 사람의 주의 의존은 fail-prone. SessionStart에서 1회 안내가 매 세션 reminder 역할 — non-blocking이라 부담 minimal"
- **채택: Refactor 우세**. CFP-1~10이 모두 자동 검출 패턴을 채택했으므로 일관성. consumer-guide 단계는 self-discovery로 끊기지만 SessionStart 안내는 매번 reminder.

## 8. 개발 서사

### §8.1-8.4 산출물

**N/A — Plugin meta script 확장**.

### §8.5 Impl Manifest

| 파일 경로 | 변경 유형 | 담당 | 변경 줄 수 (대략) | 상위 요건 ref |
|-----------|-----------|------|-------------------|---------------|
| `overlay/hooks/check-bootstrap.sh` | 신규 | DocsAgent | 신규 ~120 | Change Plan §3 |
| `overlay/hooks/regen-agents.sh` | 수정 | DocsAgent | +5 / -0 (BOOTSTRAP_CHECK_SCRIPT 변수 + 호출) | Change Plan §3 |
| `scripts/bootstrap-labels.sh` | 신규 | DocsAgent | 신규 ~70 | Change Plan §3 |
| `docs/consumer-guide.md` | 수정 | DocsAgent | +6 (§2d/§2f 참조 추가) | Change Plan §3 |
| `docs/stories/CFP-12.md` | 신규 | DocsAgent | 신규 | Change Plan §5 |
| `docs/change-plans/cfp-12-bootstrap-check-and-labels.md` | 신규 | DocsAgent | 신규 | Change Plan §5 |

## 9. 품질 게이트 이력

### §9.1-9.2 설계·구현 리뷰

**N/A** — Plugin meta script. PR review에서 reviewer 확인.

### §9.3 구현 테스트

**Local 3 시나리오 결과:**

| Test | 입력 | Expected | Actual |
|---|---|---|---|
| 1 | `bootstrap-labels.sh` 모든 label 이미 존재 | 18 idempotent update + exit 0 | OK ✓ |
| 2 | `check-bootstrap.sh` 현 plugin (org permission OFF + label 18종 존재) | 1 WARN ("Workflow permissions 미설정") + exit 0 | matched ✓ (default=read, can_approve=False detect) |
| 3 | `regen-agents.sh` SessionStart end-to-end (validate + check-bootstrap + agent regen) | 정상 chain + WARN 노출 + 20 agent regen 성공 | matched ✓ |

기존 SessionStart logic 정상 동작 (regression 없음).

### §9.4 보안 테스트

**N/A** — local script, attack surface 변경 없음. gh CLI는 read-only API만 호출 (`gh api repos/*/actions/permissions/workflow` GET, `gh label list` GET).

## 10. FIX Ledger

| Iter | 시각 | 레인 | 트리거 | 원인 판정 | 재실행 범위 | RESET? |
|------|------|------|--------|-----------|-------------|--------|
| 1 | 2026-04-27 03:00 UTC | local test | check-bootstrap silent skip (yq 미설치) | 구현 (의존성 설계) | yq → python3+PyYAML 교체 | — |

## 11. 회고

**발견 1 — 환경 정합 layer는 invariant 자동화 layer 옆에 자연스럽게 정착**: CFP-5~10은 invariant-check.yml step으로 통일됐지만 CFP-12는 SessionStart hook layer (다른 lifecycle, consumer-side). 자동화 책임의 lifecycle 분리가 자연스러움. 코드 정합 = PR-time CI, 환경 정합 = session-time hook.

**발견 2 — 의존성 최소주의의 가치**: yq를 사용하려다 미설치 silent skip 발견 (Test 1에서). PyYAML로 교체 — 이미 validate_config.py가 사용하는 의존이라 추가 부담 zero. plugin 의존성 표(CLAUDE.md "필수 CLI 2종")의 권위가 검증됨.

**발견 3 — non-blocking 진단의 가치**: check-bootstrap이 fail해도 SessionStart 자체는 진행. 환경 drift는 사용자 주의를 끌면 충분, abort는 reverse — 매 세션마다 사용자가 "왜 안 되지" 검색하게 만든다. CFP-11이 직접 겪은 사례 (label 부재로 Issue 제출 자체 막힌 경험).

**향후 작업 (별도 Story)**:
- **CFP-13** 통합됨 (본 Story)
- **ADR-003 (조건부)**: invariant 자동화 vs 환경 부트스트랩 vs 사용자 가이드의 책임 분리 ADR (3 layer가 모두 자리잡았으니 ADR로 정리할 시점)
- **CFP-14 (잠정)**: workflow degrade 패턴 (PR auto-create fail 시 Issue comment fallback) — CFP-11 §7 Mapper 의견 재검토 후보, 1인 maintainer 외 환경 추가 시 가치 발생
