---
kind: concept_definition
type: domain-knowledge
slug: ongoing-config-reconciliation
title: Ongoing config reconciliation — 초기 생성(bootstrap) vs 지속 갱신(reconcile) 의 구분, deletion propagation / 3-way base merge / dry-run 의미론
status: Active
updated: 2026-06-28
carrier_story: CFP-2440
related_adrs:
  - ADR-076  # 선언적 reconciliation upgrade flow SSOT (Sunsetted) — wholesale_mirror_with_user_visible_loss_report / dry-run·snapshot·transaction 3-enum 의 codeforge-내부 선례
  - ADR-130  # 채널 SSOT=templates/github-workflows/ + consumer-only template silent 제거 금지 (silent harm)
  - ADR-083  # §4.12 filter (plugin|mixed→full / consumer→whitelist / unknown→fail-closed)
  - ADR-116  # whitelist never-reduce / 0종→degrade
related_stories:
  - CFP-2439  # bootstrap(초기 onboarding) whitelist-driven 전환 — 본 Story 의 짝(ongoing 경로 부재가 본 Story 동인)
  - CFP-2440  # 본 concept 작성 carrier — reconcile-overlay.sh 워크플로 채널 dead 갭
tags:
  - config-reconciliation
  - ongoing-sync
  - drift-detection
  - deletion-propagation
  - orphan-pruning
  - three-way-merge
  - dry-run-semantics
  - idempotency-convergence
  - managed-file-ownership
---

# Ongoing config reconciliation

## 정의

`ongoing config reconciliation` = **이미 onboard 된 consumer 의 current state 를 desired state(wrapper SSOT)로 지속적으로 수렴(converge)시키는 동기화** — 1회성 초기 생성(bootstrap / scaffolding)과 구분되는 별도 lifecycle 단계.

핵심 구분축 = **"파일이 이미 존재하는가"에 대한 정반대 가정**:

| 차원 | bootstrap (초기 생성) | reconcile (지속 갱신) |
|---|---|---|
| 전제 | dest 부재 (greenfield) | dest 이미 존재 (이전 onboard) |
| 충돌 처리 | `! -f dst` guard — 미덮어씀 (one-time, idempotent skip) | 3-way merge — 사용자 수정 보존하며 갱신 |
| 신규 desired 파일 | 전체 생성 | **신규 whitelisted 파일을 지속 전파** (본 Story 갭) |
| 제거된 desired 파일 | N/A (생성만) | **deletion propagation / orphan handling** 결정 필요 |
| 재실행 의미 | no-op (이미 존재) | convergence (매 실행 동일 결과 = idempotent) |

## 컨텍스트

codeforge 맥락 매핑: `bootstrap-consumer.sh`(`! -f dst` guard) = bootstrap, `reconcile-overlay.sh` = reconcile. 본 Story(CFP-2440)의 갭 = reconcile-overlay.sh 가 워크플로 채널(`templates/github-workflows/` → consumer `.github/workflows/`)을 enumerate 하지 못해, 기존 onboard consumer 에 신규 whitelisted 워크플로를 지속 전파하는 경로가 dead.

## 핵심 규칙 — 외부 확립 패턴 (선행사례)

### managed vs user-modified 구분 = 3-way base merge

template-sync 도구(cruft / copier)는 **base(생성 시점 template state)를 메타데이터로 보존**해 3-way merge 를 수행한다. cruft 는 `.cruft.json` 에 template git source + 정확한 commit + context 변수를 기록하고, update 시 **동일 context 로 template 을 재생성 → local 과 비교 → diff 만 적용**, 충돌 시 git merge workflow 로 사용자 해결을 prompt 한다 (출처: [cruft.github.io](https://cruft.github.io/cruft/), [github.com/cruft/cruft](https://github.com/cruft/cruft)). [fact-checked: cruft 공식 문서]

- codeforge-내부 선례 = ADR-076 §결정 1 의 3-layer state (desired / current / customization marker block) + `# BEGIN/END wrapper-managed` marker block. base 보존 = marker block 안/밖 구분으로 근사. [verified: ADR-076 lines 161-167]
- 함의: base 가 없으면 "사용자가 고친 것"과 "원래 template 값"을 구분 불가 → 사용자 수정을 silent overwrite. codeforge 의 워크플로 파일은 **byte-identical mirror 대상**(ADR-076 §결정 2 표 `github_workflow` row)이라 marker block 보다 wholesale mirror 에 가깝다 — 즉 워크플로는 "사용자 수정 보존" 요구가 낮은 영역(설계 lane 이 §2 와 조화 결정).

### deletion propagation = opt-in prune (안전 default = 보존)

template 에서 제거된 파일을 consumer 측에서 어떻게 처리하나(orphan handling)는 **확립된 위험 영역**이며, 업계 합의는 **삭제 전파를 opt-in 으로** 둔다:

- **ArgoCD**: 자동 prune 은 `prune: true` 를 명시해야 발동. default 는 보존. 추가 안전장치 = `Prune=false` annotation(개별 보호) / `Prune=confirm`(수동 확인 요구) / orphaned-resource monitoring(삭제 없이 경고만) / `PruneLast`(신규 적용 후 제거 — 서비스 중단 방지) (출처: [argo-cd.readthedocs.io Sync Options](https://argo-cd.readthedocs.io/en/stable/user-guide/sync-options/), [Orphaned Resources](https://argo-cd.readthedocs.io/en/stable/user-guide/orphaned-resources/)). [fact-checked: ArgoCD 공식 문서]
- **rsync `--delete`**: 명시적 opt-in. 핵심 안전 invariant — **송신측 I/O 에러 감지 시 삭제를 자동 비활성화**(transient filesystem 실패가 대량 삭제로 번지는 것 차단) (출처: [rsync man page](https://linux.die.net/man/1/rsync), [explainshell](https://explainshell.com/explain?cmd=rsync+--delete)). [fact-checked: rsync man page]
- **codeforge-내부 정합**: ADR-130 §결정5 의 "consumer-only template silent 제거 금지(silent harm)" + ADR-116 "whitelist never-reduce / 0종→degrade" 는 동일 철학 — **삭제는 위험, default 는 보존, 제거는 visible 해야** 한다. [verified: 입력 패킷 관련 ADR]

### dry-run / plan = exit-code 의미론으로 "변경 유무"를 신호

미리보기 단계는 단순 출력이 아니라 **exit code 로 drift 유무를 기계 판독 가능하게** 하는 것이 확립된 규약:

- **Terraform `plan -detailed-exitcode`**: `0`=변경 없음(수렴 상태), `1`=에러, `2`=변경 대기(drift 존재). CI 파이프라인이 이 3-값으로 "apply 진행 여부"를 자동 결정 (출처: [Terraform plan reference](https://developer.hashicorp.com/terraform/cli/commands/plan), [oneuptime detailed-exitcode](https://oneuptime.com/blog/post/2026-02-23-how-to-use-terraform-plan-detailed-exitcode-for-ci-testing/view)). [fact-checked: Terraform 공식 문서]
- **rsync `--dry-run`** + `--itemize-changes`: 실 변경 0 으로 "무엇이 바뀔지" 미리 표시 — 특히 `--delete` 와 결합 시 삭제 대상 사전 확인이 권장 안전 관행 (출처: [rsync man page](https://linux.die.net/man/1/rsync)). [fact-checked: rsync man page]
- **codeforge-내부 선례**: ADR-076 §결정 3 dry-run enum = "filesystem touch 0 + drift summary report", dependency missing 시 `[dry-run] missing deps:` 표기 후 `return 0 preview only`. reconcile-overlay.sh 가 이미 dry-run/apply/rollback mode 보유. [verified: ADR-076 lines 193-198 + 입력 패킷]

### idempotency / convergence

- **Ansible `--check`** mode + changed/ok 보고 = 같은 play 재실행 시 동일 결과(convergence). reconcile 의 정의적 속성 = "매 실행이 desired state 로 수렴, 이미 수렴 상태면 no-op". [fact-checked: Terraform/Ansible 비교 검색 — Ansible --check dry-run 규약]
- **codeforge-내부 선례**: ADR-076 §결정 3 transaction 의 "사후 sanity check" + result enum 4-값(SUCCESS / SUCCESS_WITH_DEGRADATION / PARTIAL_FAILURE / FAILED) deterministic mapping = convergence 결과의 정직 보고. [verified: ADR-076 Amendment 3 lines 222-240]

## unknown-unknown (이 Story 가 놓칠 수 있는 외부 모범사례)

1. **삭제 전파의 위험성** — 워크플로 채널 reconcile 이 "desired 에 없는 dest 파일 제거"까지 자동화하면 consumer-local 커스텀 워크플로를 파괴. 업계 합의 = prune 은 항상 opt-in, default 는 보존(ArgoCD `prune: false` default / rsync `--delete` 명시 요구). ADR-130 silent-harm 금지와 정합.
2. **transient 실패 → 대량 삭제 번짐** — rsync 의 "I/O 에러 시 삭제 자동 비활성화" invariant. reconcile 도 부분 실패 시 삭제/덮어쓰기를 fail-closed 로 멈춰야(이미 ADR-076 fail-closed + reconcile-overlay.sh fail-closed 보유).
3. **dry-run exit-code 계약** — 미리보기가 단순 텍스트가 아니라 `0=수렴 / 2=drift / 1=에러` 같은 기계 판독 신호여야 CI/게이트가 활용 가능(Terraform 선례). reconcile-overlay.sh 의 기존 dry-run 의 exit-code 의미를 워크플로 채널에도 일관 적용해야.
4. **PruneLast 순서** — 제거를 신규 적용 *후*로 미뤄 중단 방지(ArgoCD). 본 Story 가 deletion 을 도입한다면 "추가 먼저, 제거 나중" 순서.
5. **base 부재 시 사용자 수정 silent overwrite** — 워크플로는 byte-identical mirror 영역이라 위험이 낮으나, consumer 가 워크플로를 로컬 수정했다면 wholesale mirror 가 그것을 덮음 → ADR-076 `user_visible_loss_report` 처럼 **덮어쓰기를 visible** 하게.

## 경계

### vs additive-merge-pattern (concept 인접)

`additive-merge-pattern` = **git rebase 시점**(Story progression layer)의 main churn 정합. 본 개념 = **upgrade/reconcile transaction layer**의 consumer state 수렴. ADR-076 §결정 4 의 disjoint layer invariant 와 동형 — 두 개념은 다른 layer.

### vs bootstrap (CFP-2439)

bootstrap = one-time, `! -f dst` guard(미덮어씀). reconcile = ongoing, 3-way/wholesale. 본 Story 의 핵심 = 두 lifecycle 의 **채널 비대칭 해소**(bootstrap 은 whitelist-driven 으로 고쳐졌으나 reconcile 의 워크플로 전파는 dead).

### ResearcherAgent 영역 경계

본 concept = 외부 표준·선행사례 기반 정의(cruft/ArgoCD/Terraform/rsync). 사내 코드베이스(reconcile-overlay.sh 910줄 내부 로직)·ADR 해석은 DomainAgent 영역. 본 문서는 외부 패턴을 codeforge 맥락에 *매핑*만 한다.

## 관련 ADR

- [ADR-076](../../../archive/adr/ADR-076-declarative-reconciliation-upgrade.md) — codeforge-내부 reconciliation 선례(Sunsetted이나 historical SSOT): wholesale_mirror_with_user_visible_loss_report / dry-run·snapshot·transaction 3-enum / fail-closed dependency closure
- ADR-130 — 채널 SSOT=templates/github-workflows/ + consumer-only template silent 제거 금지(silent harm) ← deletion propagation opt-in 과 정합
- ADR-083 — §4.12 filter (consumer→whitelist) ← reconcile 워크플로 채널의 필터 재사용
- ADR-116 — whitelist never-reduce / 0종→degrade ← deletion 보수성과 정합

## 변경 이력

| 일자 | 변경 | carrier |
|---|---|---|
| 2026-06-28 | 신규 작성 — bootstrap vs reconcile 구분 + deletion propagation/3-way/dry-run 외부 선행사례 codify | CFP-2440 |

## 외부 출처 (fact-checked)

- cruft 3-way template update + .cruft.json base 메타데이터: https://cruft.github.io/cruft/ , https://github.com/cruft/cruft
- ArgoCD prune opt-in / orphaned resources / PruneLast / Prune=confirm: https://argo-cd.readthedocs.io/en/stable/user-guide/sync-options/ , https://argo-cd.readthedocs.io/en/stable/user-guide/orphaned-resources/
- Terraform plan -detailed-exitcode (0/1/2): https://developer.hashicorp.com/terraform/cli/commands/plan
- rsync --delete opt-in + I/O 에러 시 삭제 자동 비활성화 + --dry-run: https://linux.die.net/man/1/rsync , https://explainshell.com/explain?cmd=rsync+--delete
