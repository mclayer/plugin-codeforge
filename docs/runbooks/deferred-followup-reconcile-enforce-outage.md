---
kind: runbook
title: deferred-followup-reconcile enforce-tier outage 운영 runbook
owner_story: CFP-2591
owner_adr: ADR-060
carrier_adr: ADR-060
status: Active
date: 2026-07-10
---

# deferred-followup-reconcile — enforce-tier outage 운영 runbook

> **범위**: `deferred-followup-reconcile` 게이트 (§결정 32) + sibling `deferral-carrier-declared` (b) lint
> 이 **enforce-tier(blocking-on-pr surfacing)** 로 flip 된 이후, 게이트 인프라 장애 또는 baseline 오류로
> PR merge 가 막히는 상황의 복구 절차.
>
> ⚠️ **현재 stage 는 Stage 1+2 (baseline + new-only shadow) — `continue-on-error: true` 유지**. 본 runbook
> 의 self-block 시나리오는 **flip 이후(별 후속 PR 에서 continue-on-error 제거 후)** 에만 성립한다. 현
> shadow stage 에서는 게이트가 merge 를 차단하지 않으므로 self-block 불가 — 본 문서는 **미래 flip PR
> 대비 사전 문서화**(§7.2.3 (iv) outage runbook 의무 선-충족)다.

## 1. 외부 의존 열거

본 게이트의 실행 성공은 다음 2개 외부 요소에 의존한다. 어느 하나라도 실패하면 게이트 결과가
성립하지 않는다 (fail-mode 별 처리는 §3).

| 의존 | 실패 양상 | 영향 |
|---|---|---|
| **GitHub Actions runner 가용성** | runner 큐 적체 / provisioning 실패 / Actions 장애 | 게이트 job 이 시작·완료 못 함 → (flip 후) required check pending → merge 막힘 |
| **baseline 파일 가독성/무결성** (`docs/deferred-followup-baseline.yaml`) | 파일 삭제/손상 / content_digest tamper / malformed YAML | `check` 이 SETUP exit 2 (fail-loud) → job 실패. 또는 baseline 오류로 정상 surface 가 new-debt 오발화 |

- baseline 무결성 = `content_digest` (sha256 over canonical `{gate_flags, declaration_surfaces}`) tamper-evident.
  손상 의심 시 `scripts/gen-deferred-followup-baseline.sh` 재생성 후 digest 대조.
- runner 장애는 게이트 코드 무관 (GitHub 인프라) — [githubstatus.com](https://www.githubstatus.com) 확인.

## 2. Tier 1 (surfacing) outage → 처리 원칙

본 게이트의 enforce-tier 는 **surfacing sub-mode**(continue-on-error 제거 + red-X/sticky 표면화, required
6-tuple **미편입**, contexts 무변경 — ADR-060 Amendment 20 §결정 3 reconciliation)다. 따라서:

- **blast 반경 한정**: surfacing 은 required check 가 아니므로, 게이트 outage 여도 **admin 은 merge 가능**
  (branch protection 6-tuple 미포함 → admin merge 경로 막지 않음). enforce-tier outage 의 최악은
  "PR 이 red-X 로 pending 표시되나 admin override 로 진행 가능" 수준 — hard block 아님.
- **honest ceiling**: 본 게이트는 hard block 을 주장하지 않는다. admin 우회는 구조적으로 열려 있고,
  우회 빈도는 AC-20 count(#4)로 **관측만** 한다 (차단 아님).

## 3. Manual fallback 3-step (enforce-tier outage 시)

게이트 인프라 장애로 정상 PR 이 막히면 다음을 **우선순위 순**으로 적용한다. (전부 admin 권한 필요.)

1. **(a) bypass label 부착**: PR 에 `hotfix-bypass:deferred-followup-reconcile` 라벨 부착 →
   author-verify scaffold job 이 audit comment 를 bot-authored 로 자동 발의(§결정6 v). audit trail 보존
   상태로 게이트 skip. (가장 감사-친화적 — 우회 흔적이 남는다.)
2. **(b) `continue-on-error: true` 임시 복원**: `.github/workflows/deferred-followup-reconcile.yml`
   lint step 에 `continue-on-error: true` 를 임시 복원하는 hotfix PR (= shadow stage 로 일시 회귀).
   장애 해소 후 원복 PR 로 flip 재적용. (게이트 전체를 일시 비차단화 — blast 광범위, 신중.)
3. **(c) `workflow_dispatch` disable**: 극단적 장애 시 Actions UI 또는 `gh workflow disable
   deferred-followup-reconcile.yml` 로 워크플로 자체를 비활성화. 장애 해소 후 `gh workflow enable`.
   (최후 수단 — 게이트 완전 정지, 반드시 재활성 티켓 동반.)

## 4. Self-block 회복 sequence (bad baseline 로 전 PR new-debt 발화 시)

baseline 오류(잘못된 grandfather 누락 / 손상 / 오생성)로 **정상 surface 가 new-debt 로 오발화**해
모든 PR 이 flag 되는 "self-block" 상황의 un-stick 절차. 다음 중 하나(우선순위 순):

1. **`git revert` baseline 커밋**: 문제 baseline 을 도입한 커밋을 revert 하는 PR 를 admin bypass 로 착지 →
   직전 정상 baseline 복원.
2. **baseline 재생성 PR**: `bash scripts/gen-deferred-followup-baseline.sh generate` 로 현재 tree 기준
   baseline 재생성 → 재생성 PR 을 admin bypass(라벨 (a))로 착지. (single-writer gen tool = provenance
   보존 — 손으로 편집 금지.)
3. **임시 continue-on-error 복원**: §3-(b) 와 동일 — self-block 을 즉시 해제 후 baseline 정정 PR 준비.

> **본 PR(CFP-2591 Stage 1+2)은 `continue-on-error: true` 유지라 self-block 이 구조적으로 불가**하다
> (shadow — new-debt 발화해도 merge 무차단). 위 sequence 는 **미래 flip PR(continue-on-error 제거)
> 착지 이후** 실효한다. 사전 문서화 목적.

## 5. Honest forcing ceiling (재확인)

- 게이트는 **hard block 을 주장하지 않는다**. surfacing tier 에서도 admin 우회는 구조적으로 열려 있다.
- 우회는 감사(audit comment) + AC-20 count(#4)로 **관측**될 뿐, mechanical 하게 차단되지 않는다.
- Tier 2(hard-required, 6-tuple 편입) = FUTURE/OOS — 본 runbook scope 외 (도입 시 별 carrier + 본
  runbook §3/§4 재검토 의무).

## 6. Cross-ref

- **ADR-060 Amendment 20 §결정 6 / §7.2.3 (iv)** — 본 runbook 의무 근거 (carrier trio 중 outage runbook).
- **ADR-060 Amendment 18 §결정 32** — deferred-followup-reconcile 게이트 원 정의.
- **ADR-127** — required 신설 0 ratchet (surfacing tier = 6-tuple 무변경).
- `scripts/gen-deferred-followup-baseline.sh` — baseline 재생성 single-writer gen tool.
- `docs/deferred-followup-baseline.yaml` — grandfather baseline (enumerated-freeze, content_digest tamper-evident).
