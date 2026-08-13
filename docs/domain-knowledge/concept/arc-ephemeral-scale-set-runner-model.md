---
kind: concept_definition
type: domain-knowledge
slug: arc-ephemeral-scale-set-runner-model
title: ARC ephemeral scale-set runner model — gha-runner-scale-set 실행 모델 (name/multilabel 매칭 + containerMode 3종 + 이벤트 기반 autoscale + 콜드캐시 외부화)
status: Active
updated: 2026-08-14
carrier_story: CFP-2963
related_adrs:
  - ADR-147  # CI runner topology (compose 기반 self-hosted) — 본 개념은 그 후속 K8s 이관 축의 실행 모델
related_files:
  - archive/adr/ADR-147-ci-runner-topology-selfhosted-migration.md
  - docs/domain-knowledge/concept/production-cluster-ci-cohabitation-guardrails.md   # 짝 개념 (운영 클러스터 동거 가드레일)
tags:
  - codeforge
  - ci
  - kubernetes
  - actions-runner-controller
  - self-hosted-runner
sources:
  - https://docs.github.com/en/actions/hosting-your-own-runners/managing-self-hosted-runners-with-actions-runner-controller/about-actions-runner-controller           # 아키텍처 (controller/listener/ephemeral)
  - https://docs.github.com/en/actions/hosting-your-own-runners/managing-self-hosted-runners-with-actions-runner-controller/deploying-runner-scale-sets-with-actions-runner-controller  # containerMode·인증·min/maxRunners·runnerGroup
  - https://docs.github.com/en/actions/hosting-your-own-runners/managing-self-hosted-runners-with-actions-runner-controller/using-actions-runner-controller-runners-in-a-workflow      # runs-on 매칭 (name + multilabel)
  - https://docs.github.com/en/actions/hosting-your-own-runners/managing-self-hosted-runners-with-actions-runner-controller/about-support-for-actions-runner-controller               # 지원 정책 (latest only)
  - https://github.blog/changelog/2026-03-19-actions-runner-controller-release-0-14-0/   # 0.14.0 GA — multilabel 도입
  - https://github.com/actions/actions-runner-controller/releases                        # 버전 timeline (최신 patch 0.14.2)
  - https://raw.githubusercontent.com/actions/actions-runner-controller/master/charts/gha-runner-scale-set/values.yaml  # scaleSetLabels·containerMode(dind/kubernetes/kubernetes-novolume)·workVolumeClaimTemplate accessModes=ReadWriteOnce
  - https://github.com/actions/actions-runner-controller/issues/3673                       # "ReadWriteMany volumes do not work on kubernetes mode" (closed) — RWX 반증 근거
  - https://runs-on.com/benchmarks/github-actions-cache-performance/                     # actions/cache = self-hosted 에서도 GitHub 클라우드 저장소 왕복
---

# ARC ephemeral scale-set runner model

## 정의

**gha-runner-scale-set** = GitHub 공식 지원 ARC(Actions Runner Controller) 모드. VM/컨테이너 상주(persistent) 러너가 아니라 **1 job = 1 ephemeral pod** 실행 모델 — compose 기반 상주 러너의 "이관"은 lift-and-shift 가 아니라 **실행 모델 전환**이다.

## 컨텍스트

compose 기반 상주 self-hosted 러너(ADR-147 표준)를 K8s 로 옮기는 축을 검토할 때, "러너를 어디서 돌리느냐"가 아니라 "러너 수명·매칭·캐시 계약이 무엇이냐"가 먼저 갈린다. 본 개념은 CFP-2963 요구사항 lane 이 GitHub 공식 문서·릴리스 노트·chart values 를 2026-08 시점에 검증해 정립했다 (변경 이력 참조).

## 핵심 규칙

### 핵심 구조 (2026-08 검증)

1. **2 Helm chart**: `gha-runner-scale-set-controller`(controller manager) + `gha-runner-scale-set`(scale-set 단위, OCI `ghcr.io/actions/actions-runner-controller-charts`). GitHub 지원 = "latest Autoscaling Runner Sets version only" — legacy community chart 비지원.
2. **이벤트 기반 autoscale**: listener pod 이 GitHub Actions Service 에 HTTPS long-poll → `Job Available` 수신 시 EphemeralRunnerSet replica patch → JIT 토큰으로 러너 등록. **HPA/metrics-server 비의존** — metrics-server 미설치 클러스터에서도 스케일링 동작 (관측 도구 `kubectl top` 만 제한).
3. **runs-on 매칭 2 경로**:
   - (기본) `runnerScaleSetName` **이름** 매칭 — 이름은 runner group 내 유일. classic self-hosted 의 `self-hosted`/OS 라벨 부재.
   - (0.14.0+, 2026-03-19 GA) **multilabel** — `scaleSetLabels` 로 복수 라벨 부여 + `runs-on: [label1, label2, ...]` 배열 타게팅. `self-hosted` 등 예약 라벨 할당 가능 여부는 문서 미명시 (PoC 필요).
4. **containerMode 3종** (values.yaml 실측: `dind` / `kubernetes` / `kubernetes-novolume`):
   - 기본(미지정) = docker 없음, template 수동 구성.
   - `dind` = **privileged 필수** ("The Docker-in-Docker container requires privileged mode"). `docker:dind-rootless` 변형도 `--privileged` 요구.
   - `kubernetes` = privileged 불요, runner container hooks 로 job pod 생성. work volume 은 **RWO(ReadWriteOnce)** — upstream chart `charts/gha-runner-scale-set/values.yaml` 의 `workVolumeClaimTemplate` 예시가 `accessModes: ["ReadWriteOnce"]` 이고 같은 파일에 `ReadWriteMany` 는 0건. **RWX 는 요구되지 않을 뿐 아니라 쓰면 실패**한다 — upstream issue [actions/actions-runner-controller#3673](https://github.com/actions/actions-runner-controller/issues/3673) "ReadWriteMany volumes do not work on kubernetes mode" (closed). 단, RWO 로 충분하려면 워크플로 pod 과 러너 pod 이 같은 노드에 놓여야 하는데 **그 노드 동일성 조건은 upstream 문서에도 `runner-container-hooks/packages/k8s/README` 에도 기술이 없어 확인 불가**(반증이 아니라 미확인). container job 아닌 워크플로는 `ACTIONS_RUNNER_REQUIRE_JOB_CONTAINER=false` 없이는 fail. `kubernetes-novolume` = PV 자체가 불요한 3번째 선택지.
   - **DooD(호스트 docker.sock mount)는 containerMode 목록에 없음** — containerd 런타임 노드에는 docker 소켓 자체가 없어 DooD 전제 워크플로는 재편 대상.
5. **인증**: GitHub App 권장 (`github_app_id`/`github_app_installation_id`/`github_app_private_key` k8s Secret). PAT 는 enterprise-level 러너에만 필수.
6. **min/maxRunners**: minRunners = idle 최소 (할당 job 수와 합산), maxRunners = 상한. 둘 다 0 = 큐 drain.

### 콜드캐시 외부화 (ephemeral 파생 속성)

pod 소멸 = 로컬 캐시 소멸이 구조적 기본값. 표준 대책 4종:
- **image pre-bake** (toolchain 을 러너 이미지에 소결 → 노드 이미지 캐시가 실질 캐시층, @sha256 digest pin 병행)
- **actions/cache** — self-hosted 러너에서도 GitHub 클라우드 저장소 왕복 (repo 당 10GB 무료, 7일 미접근 evict, 초과 증설 = 유료)
- **registry pull-through mirror** (Docker Hub 캐시 로컬화)
- **PVC tool cache** (accessMode 요건 **확인 불가** — upstream 이 제시하는 것은 kubernetes containerMode work volume 의 RWO 예시뿐이고 RWX 는 #3673 상 미동작. tool cache 용도 PVC 의 accessMode·provisioner 선택은 GitHub 지원 범위 밖)

### 버전 이력 앵커

0.12.1(2024-06) → 0.13.x → 0.14.0(2026-03-19 GA, multilabel + actions/scaleset 공개 Go client) → 0.14.2(최신 patch). 0.12.0 에 CRD 전면 재설치 요구 이력 — CRD 는 cluster-scoped 공유라 **동일 클러스터 내 구버전 pin scale-set 과 신버전 공존 시 CRD skew 검증 필수**.

## 경계

- 본 개념 = GitHub 공식 문서·릴리스 노트·chart values 기반 **외부 사실 모델** (요구사항 lane Researcher 소유, 2026-08 시점 검증). 특정 클러스터에 실제로 적용할지·어떤 값으로 설정할지 판단은 설계 lane 실측 영역.
- 본문에 명시한 **미확인 3건**은 확정 사실이 아니다 — ① multilabel 로 `self-hosted` 등 예약 라벨을 할당할 수 있는지(문서 미명시 → PoC 필요) ② `kubernetes` containerMode 의 work volume 이 RWO 라는 사실 자체는 확정이지만, "표준 단일-노드 provisioner 로 충분하다"는 후속 판단은 **MCLATS StorageClass 실측 위에서만 성립** — 실측 미수행(설계 lane 영역) ③ RWO 성립의 전제인 **워크플로 pod ↔ 러너 pod 노드 동일성 조건** — upstream 문서·`runner-container-hooks/packages/k8s/README` 어디에도 기술 없음(확인 불가). ②·③ 을 우회하는 선택지로 **`kubernetes-novolume`(PV 불요)** 가 3안으로 존재한다.
- **자원·스케줄링 격리 축은 본 개념 범위 밖** — 운영 클러스터 동거 시의 우선순위·quota·디스크 가드레일은 짝 개념 `production-cluster-ci-cohabitation-guardrails` 소관.

## 관련 ADR

- **ADR-147 (CI runner topology — mclayer org self-hosted 이관 표준)** — compose 기반 self-hosted 러너 표준. 본 개념은 그 후속 K8s 이관 축의 실행 모델.

## 변경 이력

| 일자 | 변경 | carrier |
|---|---|---|
| 2026-08-13 | 신규 작성 — CFP-2963 요구사항 lane Researcher 산출 (ARC gha-runner-scale-set 실행 모델 외부 사실 조사) | CFP-2963 |
| 2026-08-14 | 헤딩 구조 재배치 — concept doc-section-schema 필수 헤딩(컨텍스트·핵심 규칙·경계·관련 ADR·변경 이력) 정합. 내용 무손실 (기존 3개 절을 핵심 규칙 하위 `###` 로 강등 + frontmatter 인용 ADR·짝 개념·본문 미확인 2건을 경계/관련 ADR 로 목록화) | CFP-2963 |
| 2026-08-14 | **사실 정정 — `kubernetes` containerMode 의 PV accessMode 를 RWX → RWO 로 교체** (요구사항리뷰 iter2 C-6). 근거 = upstream `charts/gha-runner-scale-set/values.yaml` 의 `workVolumeClaimTemplate` 예시 `accessModes: ["ReadWriteOnce"]`(파일 내 `ReadWriteMany` 0건) + upstream issue actions/actions-runner-controller#3673 "ReadWriteMany volumes do not work on kubernetes mode"(closed, RWX 사용 시 실패). 동반해 경계의 미확인 항목을 2건 → 3건으로 교체(RWX provisioner 선택 → MCLATS StorageClass 실측 + 노드 동일성 조건 확인 불가) + `kubernetes-novolume` 3안 명시. 콜드캐시 절의 "PVC tool cache = RWX 요구" 도 같은 반증에 걸려 확인 불가로 강등 | CFP-2963 |
