# 정정/축소 lane (correction lane)

> 진실 정정·de-bloat 를 promotion 의식 없이 근거만으로 진행하는 경량 경로.
> 강제 수단 = `scripts/check-tier-downgrade-guard.sh` + `tier-downgrade-guard.yml`.

## 문제
- `docs/evidence-checks-registry.yaml` 의 `current_tier` 필드 = "검사 강제 강도"의 단일 출처(SSOT). 값: `warning` / `blocking-on-pr` / `blocking-on-merge`.
- 그러나 **어떤 검사도 이 필드를 지키지 않았다**. 기존 약화방지 가드(`sunset-weakening-evidence` / `adr-077-ratchet` / `adr-sunset-criteria`)는 전부 `docs/adr/ADR-*.md` 경로에만 걸려 있어, registry 의 tier 하향(blocking→warning)·entry 제거는 아무 검토 없이 통과됐다 (PR #1930 에서 실제 1건 tier 강등이 무감지로 통과).
- 동시에, 레드팀의 더 깊은 발견: 시스템은 모든 진실 정정·de-bloat 를 금지된 "약화"로 취급해 full promotion 의식(CFP/ADR)을 요구한다 — 정당한 cleanup 이 과도하게 의식화된다.

## 정책 — "정정/축소 lane"
강제 강도를 **낮추거나** 거버넌스를 **제거하는** 변경은 promotion CFP/ADR 대신 마커 한 줄로 진행한다.

대상 변경:
- `current_tier` 하향 (예: `blocking-on-merge` → `warning`)
- 검사·결정기록(ADR)의 은퇴(entry 제거)
- 죽은 버전·dead governance 삭제

진행 방법:
- commit message **또는** PR 본문에 다음 라인을 추가한다.
  ```
  tier-downgrade-justification: <근거>
  ```
- 근거는 **red-team / audit 증거를 인용**한다 (어느 발견이 이 정정을 정당화하는지).
- promotion CFP·ADR amendment·승격 의식 불필요. 근거 마커가 곧 승인이다.

## 강제
- `scripts/check-tier-downgrade-guard.sh` 가 base(`origin/main`) 대비 tier 하향/entry 제거를 감지한다.
- 마커가 있으면 하향 내역 + 근거를 출력하고 통과(exit 0).
- 마커가 없으면 각 미정당화 하향을 명시하고 **실패(exit 1)** — warning-theater 아님(`continue-on-error` 미설정).
- 마커 입력 경로 2종: 환경변수 `TIER_DOWNGRADE_JUSTIFICATION`(CI 가 PR 본문 주입) 또는 최신 commit message 의 `tier-downgrade-justification:` 라인.

## 범위 / 비범위
- **범위**: 강제 강도를 *낮추는* / 거버넌스를 *제거하는* 변경.
- **비범위**: 강제 강도를 *올리는* 변경(warning→blocking 승격, 신규 검사 도입)은 본 lane 대상이 아니다 — 기존 promotion 경로(evidence-checks-registry `promotion_criteria` + 승격 carrier)를 따른다.

## 의도적 최소 구성 (이 결정 자체가 첫 dogfood)
본 가드는 **evidence-checks-registry 프레임워크에 등록하지 않는다**.

- 등록하면 label 카운트·MANIFEST 연쇄·hotfix-bypass 라벨 family 증가를 유발한다.
- 그 연쇄가 바로 "삭제도 추가만큼 의식화된다"는 레드팀 비판을 그대로 재현한다.
- 따라서 등록 생략은 의식화 회피를 위한 의도적 결정이며, 이 결정 자체가 정정/축소 lane 의 첫 dogfood(자기적용) 사례다.
