---
kind: concept_definition
type: domain-knowledge
slug: production-cluster-ci-cohabitation-guardrails
title: Production cluster CI cohabitation guardrails — 운영 클러스터에 CI 워크로드를 동거시킬 때의 K8s 표준 가드레일 매핑
status: Active
updated: 2026-08-13
carrier_story: CFP-2963
related_adrs:
  - ADR-147  # CI runner topology — 본 개념은 K8s 이관 시 운영 보호 축
related_files:
  - docs/domain-knowledge/concept/arc-ephemeral-scale-set-runner-model.md   # 짝 개념 (러너 실행 모델)
tags:
  - codeforge
  - kubernetes
  - ci
  - resource-isolation
  - production-safety
sources:
  - https://kubernetes.io/docs/concepts/scheduling-eviction/pod-priority-preemption/   # PriorityClass·preemption·preemptionPolicy Never
  - https://kubernetes.io/docs/concepts/scheduling-eviction/taint-and-toleration/      # dedicated nodes = taint+toleration 은 단방향, affinity 병행 필요
  - https://kubernetes.io/docs/concepts/policy/resource-quotas/                        # ResourceQuota(네임스페이스 총량) + LimitRange(per-container default)
  - https://kubernetes.io/docs/concepts/storage/ephemeral-storage/                     # ephemeral-storage limit 초과 = kubelet eviction
  - https://kubernetes.io/docs/concepts/storage/volumes/                               # emptyDir = 노드 backing 매체(루트 fs) + sizeLimit
---

# Production cluster CI cohabitation guardrails

## 정의

실거래/운영 클러스터에 CI(고 burst·저 우선) 워크로드를 동거시킬 때, "CI 가 운영을 절대 밀어내지 못하고, 자원·디스크·스케줄링 3면에서 상한이 걸린 상태" 를 K8s 표준 프리미티브만으로 구성하는 가드레일 세트.

## 컨텍스트

CI 를 별도 클러스터가 아니라 이미 운영 중인 클러스터에 얹는 선택지를 검토할 때, 쟁점은 "돌아가느냐"가 아니라 "burst 가 터졌을 때 운영이 먼저 죽지 않는다는 보장이 어느 프리미티브에서 나오느냐"다. 본 개념은 CFP-2963 요구사항 lane 이 k8s 공식 문서를 2026-08 시점에 검증해 정립했다 (변경 이력 참조).

## 핵심 규칙

### 가드레일 매핑 (5축, 2026-08 k8s 공식 문서 검증)

1. **우선순위·선점**: PriorityClass — value 높을수록 우선, 스케줄러는 pending 고순위 pod 를 위해 저순위 pod 를 **preempt(축출)** 가능. 가드레일 = CI pod 에 **낮은 value + `preemptionPolicy: Never`** 부여(대기열 우대도, 타 pod 선점도 불가) + 운영 워크로드에 높은 value → 노드 압박 시 축출 순서가 항상 CI 먼저. 주의: "PodDisruptionBudget is supported, but not guaranteed".
2. **스케줄링 격리(양방향)**: taint+toleration 은 "남을 못 들어오게" 하는 단방향 — toleration 을 가진 pod 도 다른 노드에 갈 수 있다. 특정 노드(예: 세컨더리 노드) 위주 배치는 **nodeSelector/nodeAffinity 병행** 필수. (전용 노드 = taint ⊕ affinity 2-piece.)
3. **자원 총량 상한**: ResourceQuota = CI 네임스페이스에 `requests/limits.cpu·memory`, `requests.ephemeral-storage`, pod count 총량 cap. LimitRange = per-container default request/limit 강제 주입(미지정 pod 가 quota 에 거절되는 것 방지).
4. **디스크 폭주 차단**: ephemeral-storage(= 비 tmpfs emptyDir + writable layer + logs) limit 초과 시 **kubelet 이 pod eviction** — CI 빌드 산출물 폭주가 노드 디스크를 잠식하기 전에 pod 단위로 끊는다. emptyDir 는 "whatever medium that backs the node"(통상 `/var/lib/kubelet` = 노드 루트 fs) — **물리 디스크 분리 요구(예: 데이터 플레인 NVMe 와 CI 워크디렉토리 분리)는 limit 만으로 불충분, 노드 디스크 레이아웃(kubelet root-dir 가 어느 물리 디스크인지) 실측이 선행**되어야 한다.
5. **관측 한계 정직 선언**: metrics-server 부재 시 `kubectl top` 불가 — 가드레일 동작 검증은 ResourceQuota status·`kubectl describe node`(Allocated resources)·eviction 이벤트로 대체. (ARC autoscale 은 이벤트 기반이라 metrics-server 불요 — 짝 개념 참조.)

## 경계

### 반례 경계

- ResourceQuota 는 **스케줄링 시점 requests/limits 합산** 제어 — 실사용량 폭주는 limit(cgroup)와 eviction 이 담당. 둘은 대체재가 아니라 보완재.
- taint 없이 affinity 만 쓰면 "CI 는 그 노드로 가지만, 운영 pod 도 그 노드로 갈 수 있음" — 격리 방향을 요구사항에서 명시해야 설계가 갈리지 않는다.

### 적용 범위 경계

- 본 개념 = k8s 공식 문서 기반 **표준 프리미티브 매핑** (요구사항 lane Researcher 소유, 2026-08 시점 검증). 특정 클러스터의 노드 구성·디스크 레이아웃·metrics-server 유무는 **실측 대상**이지 본 개념이 단정하는 사실이 아니다 (5축 중 4·5 축이 그 실측을 전제로 서술).
- **러너 실행 모델 자체는 본 개념 범위 밖** — ephemeral pod 수명·`runs-on` 매칭·containerMode·캐시 외부화는 짝 개념 `arc-ephemeral-scale-set-runner-model` 소관.

## 관련 ADR

- **ADR-147 (CI runner topology — mclayer org self-hosted 이관 표준)** — CI 러너 토폴로지 표준. 본 개념은 그 K8s 이관 시의 운영 보호 축.

## 변경 이력

| 일자 | 변경 | carrier |
|---|---|---|
| 2026-08-13 | 신규 작성 — CFP-2963 요구사항 lane Researcher 산출 (운영 클러스터 CI 동거 가드레일 외부 사실 조사) | CFP-2963 |
| 2026-08-14 | 헤딩 구조 재배치 — concept doc-section-schema 필수 헤딩(컨텍스트·핵심 규칙·경계·관련 ADR·변경 이력) 정합. 내용 무손실 (가드레일 매핑 절을 핵심 규칙 하위 `###` 로 강등 + 기존 `## 반례 경계` 를 `## 경계` 하위 `###` 로 이동 + frontmatter 인용 ADR·짝 개념을 관련 ADR/경계 로 목록화) | CFP-2963 |
