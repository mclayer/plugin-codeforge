---
adr_number: 174
title: MCLATS ARC CI 러너 topology — 운영 클러스터 동거 CI 실행면 + ADR-147 축별 처분
status: Proposed
is_transitional: false
category: Infrastructure
date: 2026-08-14
carrier_story: CFP-2963
related_adrs:
  - ADR-147-ci-runner-topology-selfhosted-migration  # 축별 처분 대상 (본 ADR 이 전방 참조 — ADR-147 원문 무편집, 파일 amendment 는 CFP-2913 완결 후 착수)
  - ADR-121  # deploy lane 제거 — CI ARC ⊥ deploy ARC 경계 문서화
  - ADR-164  # watchdog=hosted HARD — 감시 대상 장애 도메인이 MCLATS 로 이동 (R14 후속)
  - ADR-048-ci-native-test-execution  # Amendment 3 미착지 부채 — 콜드스타트 2계층 측정 입력 (R12)
  - ADR-119  # 검증-후-단언 — presence-only oracle 불허 상속
  - ADR-072  # ProductionEvidence — MS-1/MS-4 충족, evidence quad 도메인 재실체화
related_files:
  - docs/change-plans/cfp-2963-mclats-arc-ci-runner.md
  - scripts/ci-runner-provisioning-check.sh
  - docs/architecture/codeforge-family.md
related_stories:
  - CFP-2963
  - CFP-2913  # 순차 제약 (Q-2) — ADR-147 파일 amendment 착수 gate
---

# ADR-174: MCLATS ARC CI 러너 topology — 운영 클러스터 동거 CI 실행면 + ADR-147 축별 처분

## 상태

`Proposed` (2026-08-14 KST) — CFP-2963 Phase 1 설계 lane draft. ArchitectAgent chief author 작성, ArchitectPLAgent 검수 후 Accepted 전이. adr_number = ADR-133 claim primitive 반환값 174 (state branch `adr-reservation-state` OCC — 173 은 타 claimant 선점 상태 실측, max+1 재계산 미사용).

## 컨텍스트

CFP-2963: 개발 호스트(MCCHO-DESKTOP)의 Linux CI 러너 부하를 철수하고, MCLATS(mctrader 실거래 운영 K8s 클러스터, mclats01/02)에 ARC(gha-runner-scale-set) 기반 CI 러너를 신설해 이관한다. 확정 제약(재논의 금지): Q-1 docker 의존 5 workflow 전량 kubernetes containerMode 재편 후 일괄 이관(dind/privileged 거부) / Q-2 CFP-2913 순차 / mclats02 위주 배치·apiserver 최소권한·신규 group public 거부·러너 디스크↔Kafka NVMe 물리 분리·추가 지출 0 / roster 18 repo(AC-8 술어) / I-1~I-4·T-15 hard rail / D1~D16 재사용.

핵심 충돌 3건이 본 ADR 을 강제한다: ① ADR-147 Amd5 C1③④/C3(라벨-매칭·online-실재 검증)이 ARC(이름 매칭·scale-to-zero·라벨 미노출 — upstream actions/actions-runner-controller#4425)와 구조적 비호환 ② 과도기 전량 hosted 상태가 §결정4(i) 위반 ∧ Amd5 carve-out 성립조건(C1/C2'/C3) 미이행으로 미codify 상태 ③ "0.14.x 신설 ∧ 배포용 0.12.1 무접촉" 이 CRD 축(cluster-scoped, helm upgrade 미지원)에서 동시 만족 불가 [verified — helm.sh CRD best practices + docs.github.com ARC upgrade 절차 + CRD 4건 blob 상이 실측, InfraOperationalArch P0-2].

## 결정

### §결정 1 — CI ARC topology (이름 매칭 · 0.12.1 계열 pin · kubernetes mode)

- **scale-set/runner group** = `mclats-ci-linux` (scale-set:group 1:1 — group 내 유일성 자명 충족). 명명 규약 = `mclats-ci-<os>[-<variant>]` + **예약 토큰 2단 금지 룰** (비교 기준 = **case-insensitive 정규화 후** — GitHub `contains()`·runs-on 매칭 모두 대소문자 무시 [verified-ext: docs.github.com expressions — contains() "not case sensitive"]):
  - **(i) exact-match 금지** — 이름 전체가 예약 토큰(`self-hosted`/`linux`/`docker`/`x64`/`ubuntu-latest`)과 정확히 일치 금지 → §결정 2 값공간 3-domain 오분류 차단.
  - **(ii) substring 금지 = `self-hosted` 한정** — 이름 어디에도 `self-hosted` 문자열 포함 금지(`<os>`·`<variant>` 값 포함) → §결정 8 판별식 `contains(..., 'self-hosted')` 를 오염시키는 **유일** 토큰이라 이 축만 substring 금지가 필요하다. 기타 예약 토큰의 substring 포함(`mclats-ci-linux` 의 `linux` 등)은 **허용** — runs-on 매칭은 배열 원소 단위 비교라 substring 이 매칭·분류를 오염시키지 않는다.
  - (설계리뷰 iter1 **D-1 정정**: 구 문면 "전 예약 토큰 단독·substring 포함 금지" 는 채택 이름 `mclats-ci-linux`(`linux` substring)와 템플릿 `mclats-ci-<os>` 자체를 위반으로 만드는 자기모순 — 층3 분류기가 컷오버 정본 값을 FAIL-LOUD 차단하는 born-broken 채널이었다. 2단 분해 후 채택 이름·템플릿·층3 lint·§결정 8 판별식 4자 정합.)
- **namespace** = `arc-ci-systems`(신규 controller + listener, `flags.watchSingleNamespace=arc-ci-runners` 필수 — 기본값 watch-all 은 배포용 CR 을 조정해 무접촉 즉시 파손) ⊕ `arc-ci-runners`(러너 pod + job pod). 기존 `arc-systems`/`mctrader` ns 무접촉. listener 는 controller ns 에 생성됨(배포용 선례 실측) — ResourceQuota 는 양 ns 에 건다.
- **runs-on 매칭 = 이름 매칭 1안 확정**: `CI_RUNS_ON_LINUX_JSON = ["mclats-ci-linux"]` (1원소 배열). §결정 1(ADR-147) fromJSON 표현식·in-file default `["ubuntu-latest"]` 무변경(D1~D3) — workflow 파일 delta 0, 값 shape 만 전환. 매칭 성립은 AC-14① PoC 선결(판정 전 카나리 진입 금지).
- **chart 버전 = 배포용과 동일 계열 0.12.1 pin**. 근거: (i) 0.14.x 신설은 CRD 축에서 배포용 0.12.1 무접촉과 동시 만족 불가 — helm 은 기존 CRD skip(신규 CI born-broken, 경로 A), 공식 해소 절차는 전 scale-set uninstall + CRD 전삭제(배포용 CR 소멸, 경로 B) [verified — InfraOperationalArch P0-2 실측 4건] (ii) 0.14 의 실이득(multilabel)은 이름 매칭 채택으로 소요 0 — 2안(라벨 재사용)의 채택 근거는 과도기 변수 전량 삭제로 이미 소멸(TestContractArch AC-14② decision-irrelevant 논증 채택) (iii) 롤백 = `helm uninstall` 이 배포용 무영향(CRD 무접촉) — 단 ARC 철회 시 전체 잔재 제거(App key Secret·GitHub App·runner group·ns)는 Change Plan §11.3b teardown 절차 소관(D-4). **정직 수용(통지 항목 — Change Plan §3.9 N-1)**: GitHub 지원 정책("latest only") 밖 운용 — 보안 패치 미수령 리스크를 사용자 확정 가드레일(배포용 무접촉)의 하위 비용으로 수용한다. **재에스컬레이션 트리거(D-8)**: 0.12.x 계열(runner·listener·container hook 포함) 대상 CVE·upstream 보안 공지 공표 시 즉시 사용자 재회부(0.14+ 통일 재결정) — 방치 시 무기한 무패치 운용이 되는 경로를 차단한다. 해소 경로 = 배포용 포함 클러스터 전체 0.14+ 통일(무접촉 파기 = 사용자 재확인 필수 — 별도 결정, 본 ADR 범위 밖). Story §6.6 R1("0.12.1 재사용 불가")은 지원-정책 논거로서 기록 보존하되 본 결정이 CRD-무접촉 제약 우위로 override 한다.
- **containerMode = kubernetes** (Q-1 사용자 확정). dind 거부·DooD 부재. work volume = RWO PVC(StorageClass 실측 M-2 선결, 부재 시 `kubernetes-novolume` fallback 평가 — 0.12.1 계열의 novolume 지원 여부 자체가 실측 대상 M-16).
- **repo 소속** = `mclayer/ci-runner-infra`(private) 확장 — 신규 형제 디렉토리 **`ci-runner-arc/`** (`values/` + `manifests/` + `install.sh` + `runbooks/`). 기존 `ci-runner-linux/`(DooD fleet) 무편집 존치, Q-8 폐기 시 디렉토리 단위 삭제. mctrader k8s/ 병치는 기각(bounded context 침식 — ModuleArch), 신규 repo 는 기각(repo-분해 pressure 없음 — RefactorAgent, ADR-138 debate 경유).

### §결정 2 — 라우팅 값공간 3-domain additive 확장 (완화 아님)

ADR-147 Amd5 C1/C3 의 값공간을 **3rd 도메인 "ARC scale-set 이름" additive 확장**으로 재정의한다(축 삭제·완화 프레이밍 금지 — Amd5 sunset 저촉 회피):

| domain | 판별 술어 | 검증 축 | SSOT |
|---|---|---|---|
| hosted | 배열 원소 ∈ hosted 리터럴 allowlist | C1⑤ (로스터 정합) | allowlist 상수 + `capacity-overflow-roster.yaml`(존폐 = R9 이월) |
| classic self-hosted 라벨 | 길이>1 ∧ 첫 원소 `self-hosted` | C1③④ (등록 라벨 ⊆ ∧ online 1+) | `orgs/{org}/actions/runners` |
| **ARC scale-set 이름 (신설)** | 길이==1 ∧ hosted 아님 ∧ **예약 토큰 2단 룰 통과(§결정 1 (i)(ii) — exact ∉ 예약 토큰[case-insensitive] ∧ `self-hosted` substring 부재)** ∧ 레지스트리 등재 | **대체 통제 3층** (하기) | 신규 `ci-runner-arc/scale-set-registry.yaml` — private repo 필수(public 배치 = Amd4 §제약1 위반), hand-authored append-only(실 변수값 파생 생성 금지 — anti-tautology) |

- C1③④ 는 classic 도메인 **한정 정의역**으로 분기한다 — ARC 도메인에서 ③④ 는 `N/A + 사유` codify(축 삭제 아님·정의역 분기 = additive). 근거 = ARC 러너는 실행 중에도 runners API 에 라벨 미노출(#4425) ∧ scale-set 열거 public REST 부재(`orgs/{org}/actions/runner-scale-sets` 404 — PL·TestContractArch·ProductionEvidence 3자 독립 실측).
- **ARC 도메인 대체 통제 3층**: (층1) helm release `deployed`(operator cadence 의존 — 정직 ceiling) (층2) 카나리/웨이브 pickup 실증(AC-6 — 가장 강한 실증, 사후적) (층3) provisioning lint 의 값-검증을 3-domain 분류기로 additive 확장(미분류 = FAIL-LOUD 유지). `runner-groups/{id}/runners` group-scoped 열거는 가용(200)하나 idle=0 정상 상태에서 상시 0행 — 0행을 부재로 읽지 않는 lint 재정의를 층3 에 포함. **층3 구현 시점(D-5 통일)**: C1 값검증 배선 후속 Story 이월(본 Story = `_classify_value` 시그니처 기록만, 구현 0) — **컷오버 시점 실효 통제 층 = 층1·층2**.
- C2'(org-level 금지)는 **무접촉 유지**(substrate-agnostic). 미분류 값 무조건 FAIL-LOUD(Amd5 C1) 계승.

### §결정 3 — 보안 경계 (kubernetes mode 함의의 정직 codify)

- **`ACTIONS_RUNNER_REQUIRE_JOB_CONTAINER` = true(chart default) 유지 확정** — false 는 워크플로 코드를 SA 토큰 보유 러너 pod 안에서 실행시켜 B3 경계를 소멸시키고 "커밋 권한 = GitHub App 개인키 접근"으로 만든다 [source: docs.github.com deploy-runner-scale-sets 공식 경고]. **파생 의무**: 이관 대상 roster repo 의 전 Linux job 은 `container:` 를 선언해야 한다(미선언 job = 컷오버 시 born-broken) — 컷오버 선결 편집 (iii) 로 등재. values 에 false 가 들어가지 않음을 컷오버 체크 항목화(drift 차단).
- **자체 SA + 자체 Role 공급**(차트 kube-mode Role 자동생성 비활성 — `template.spec.serviceAccountName: ci-runner` 명시): rules = hook requiredPermissions 4-resource(pods CRUD / pods-exec / pods-log / secrets CRUD) 만. 차트 기본 Role 의 `batch/jobs` 초과분(pod 생성 우회 프리미티브)은 **기본 제외 + 제외 시 동작 여부 PoC(P-4)** — 불가 확정 시 명시 예외 등재. `deploy-runner` SA 재사용 절대 금지. ClusterRole/ClusterRoleBinding 0, 운영 ns 권한 0.
- **GitHub App = org-scope 신규 App**(`githubConfigUrl: https://github.com/mclayer`, 권한 = `Self-hosted runners: RW` + `Metadata: R`) — repo-scope 는 `Administration: RW`(= roster 18 repo 관리자 등가) 요구라 기각. **배포용 App 공유 금지**(rate limit installation 단위 격리 + 침해 격리). key 는 사전 생성 K8s Secret 참조(helm values 인라인 금지) + 회전 절차(정기 90일 `[hypothesis — 정책 선택: 사내 표준 부재 시 관례 기본값, D-9]` + 침해 의심 즉시) 문서화. **org-scope 의 '러너 관리 한정' 정밀화(D-11)**: 유출 시 blast 는 repo-admin 축에서만 소멸 — org 러너 관리면은 잔존하며 **T-1 전이(악성 러너 등록 → org 전체 self-hosted job[배포용 group 포함] 가로채기)를 포함**한다. ESC-1 통지문(Change Plan §3.9)에 1급 명시 + 탐지 = 러너 등록 audit log 모니터.
- **S-1 구조 잔여 정직 declare(제거 불가)**: 러너 SA 는 hook 요구 `secrets get/list` 때문에 자기 ns 전체 Secret — **GitHub App private key 포함**(차트가 설치 ns 에 강제) — 를 read 할 수 있다. RBAC resourceNames·ns 분리·list 제거 전부 불가 판정(SecurityArch §7.3-A4). 완화 = REQUIRE_JOB_CONTAINER=true(read 주체를 hook 코드로 국한) + org-scope App(유출 시 blast 를 러너 관리 권한으로 한정) + **CI ns 자격증명 = App key 외 0개** + 회전 절차. 사용자 가드레일 "apiserver 무접촉"의 문자적 달성은 kubernetes mode 와 양립 불가 — 달성 ceiling = SecurityArch 명제 C(주체 = 러너 pod 단일 / ns 한정 / 4-resource / 운영 권한 0 / 행사 코드 = hook). ESC-1~3 = 사용자 에스컬레이션·인수 항목 — **정의·선택지·귀결·권고 register = Change Plan §3.9**(D-2).
- **job pod 하드닝**(hook extension template 로 강제): `serviceAccountName: ci-job-noperm`(RoleBinding 0) + `automountServiceAccountToken: false` + NetworkPolicy 로 apiserver egress 차단(이중). Story W-4 의 "러너 automount false" 는 kubernetes mode 와 모순 — **job pod 한정으로 재정의**한다(러너 pod 은 토큰 필수, SecurityArch·InfraOp 수렴).
- **admission** = PSA `enforce=baseline` + `warn/audit=restricted`. restricted enforce 는 hook 의 `fs-init` initContainer securityContext 미주입·템플릿 교체 불가로 **현 시점 불가**(상한 정직 declare — hollow 상향 시도 차단; 근거 등급 = hook **소스-레벨 확인**이지 클러스터 admission 실측 아님 — 실증 = Change Plan §11.4b M-17, 설계리뷰 iter1 등급 정정). NetworkPolicy 2-tier(러너 pod = apiserver 허용 / job pod = apiserver 차단 + RFC1918 차단) + **scale-set 설치 전 NP 선-존재 hard-assert**(사내 SEC-03 승계). NetworkPolicy 는 내부 lateral 차단이지 외부 exfiltration 차단이 아님(정직 한정).

### §결정 4 — 운영 동거 가드레일 6축 + job pod 도달 경로

- **가드레일이 러너 pod 에만 도달하는 함정(P0-1)을 명시 봉합한다**: scale-set values 의 spec 은 러너 pod 전용 — 실 부하 주체인 **job pod**(hook 이 apiserver 로 직접 생성, priorityClass/affinity/resources 전무)에는 ① `ACTIONS_RUNNER_CONTAINER_HOOK_TEMPLATE`(ConfigMap mount) extension template(유일한 직접 경로 — `initContainers` 기재 절대 금지: fs-init 교체 사고) ② ns LimitRange(default request/limit 주입 — template 누락 시 2차 방벽) ③ ns ResourceQuota ④ PSA 라벨 4경로로만 도달한다. extension 반영 실증(M-12)은 카나리 PoC 필수 항목.
- **6축**: ① PriorityClass `ci-low` = **value 음수(후보값 -1000 `[empirical-source: M-6 기존 PriorityClass 실측 후 확정 — 운영 전 클래스 최저값보다 낮게, D-9]`) + `preemptionPolicy: Never` + globalDefault: false** — 운영 pod(미지정=0) 무접촉으로 열위 확정(운영 리소스 편집 불요) ② nodeAffinity `required` mclats02(러너 ∧ job pod 양쪽) — **taint 기각**(운영 pod 축출·toleration 편집 = 무접촉 위반) ③ ResourceQuota(양 ns) + LimitRange — **`pods: 2N+4`**(1 job = 러너+job 2 pod; N 으로 잡으면 job pod 생성 거부 = job 실패 F-12) ④ ephemeral-storage per-pod limit + emptyDir sizeLimit + 디스크 물리 분리 실측 **3경로**(kubelet root-dir ∧ imagefs(/var/lib/containerd) ∧ Kafka 데이터 마운트 — imagefs 축 추가) ⑤ 관측 = listener Ready + queue-depth + quota status(§결정12 대체 관측 계승) ⑥ **Docker Hub pull 쿼터(신설 6번째 축)** — 공유 egress IP 에서 CI pull 폭주가 운영 배포 pull 을 차단(무인증 100/6h per IP) → digest pin + `imagePullPolicy: IfNotPresent` + 필요 이미지 ghcr 미러(pull-through mirror 신설은 상주 워크로드 추가라 비권고).
- DiskPressure eviction 은 노드 전역 사건 — 물리 분리만으로 부족하며 CI 음수 priority 가 축출 순서를 확정한다(운영 pod 보호의 결정적 완화). PriorityClass 는 스케줄링·축출 순서만 지배 — CPU 경합·page cache·NVMe io·지연 tail 은 미지배(OUT-9 미측정 유지, "안전 단정" 금지).
- **clock sync = CONDITIONAL ACTIVE**: GitHub App JWT `exp ≤ 10분`, `iat` 60초 과거 권장 + NTP 명시 요구 [source: docs.github.com — Generating a JWT for a GitHub App] → mclats01/02 NTP 동기 활성 ∧ offset < 60초 를 선결 실측(M-8) + 컷오버 게이트 편입. drift = 전 CI 정지(fail-static, 운영 무영향).
- **maxRunners**: 추정 lock-in 금지 — 과도기 hosted 구간이 유일한 clamp-free 실수요 관측 창(M-1 최우선 실측): 1분 bucket 동시성 시계열 → p95×1.5 잠정, 단계 상향(1→4→p95×1.5). `minRunners: 0` 유지(idle 러너 운영 노드 상주 회피). CPU/메모리 축에서 maxRunners 는 안전 파라미터(Pending 대기로 degrade — preempt 불가) — 실질 상한 지배자는 디스크 io·page cache·pull 쿼터.

### §결정 5 — 컷오버 절차 (G0~G8 gate ladder + 카나리 7-AND)

- **gate ladder G0~G8**(ProductionEvidenceDeputy 설계 채택 — Change Plan §11 SSOT): G0 과도기 baseline 재확정(F-A 재가동 반영 — 신설) → G1 선결 편집 실증(12-site 3-way + 5 workflow 재편 + container: 선언) → G2 PoC 양방 기록(AC-14) → G3 W0 부트스트랩(TOCTOU) → G4 카나리 pre-flight(큐 배수·wrapper unset·ARC 기동·NP hard-assert·admission 부정 대조) → G5 카나리 판정 → G6 웨이브(PR 생애주기 횡단 금지 I-4) → G7 provisioning 재정합(AC-13) → G8 phase 2 종점(AC-22).
- **카나리 판정 = §결정 6(ADR-147) 5-AND 의 ARC 재실체화 + 2 leg 신설 = 7-AND**: ① 실행면 = **`runner_group_name` == `mclats-ci-linux`**(ARC 라벨 미노출로 구 conjunct 1 을 그대로 쓰면 건강해도 FAIL — `labels` 판정 금지, ground-truth = runner_group_name [verified — ProductionEvidence F-D 실측]) ② pickup bounded(콜드/웜 분리 기록 — **계약 = AC-6**: 변수 SET `updated_at` 이후 `created_at` 오름차순 최초 연속 3건 · ≤30분 후보 임계 · 무한대기 0 · `runner_name` oracle, D-10) ③ required context 전건 `success` — **`skipped`/`neutral` green 계상 금지**(ADR-147 I-3 동반함정) ④ mergeStateStatus CLEAN ∧ skipped 0 ⑤ preinstall baseline 실측(§결정5 계승) ⑥ **kubernetes mode 실증**(privileged 0 ∧ docker.sock hostPath 0 — job pod spec 실측) ⑦ **운영 무해 관측**(Evicted 0 — event TTL 1h 라 ≤30분 주기 수집, 일괄 사후 조회 금지; **관측 창·부하 실재 = AC-9 ①③**[완료 CI job ≥10 ∧ Running ≥1 증빙 선행], 창 = 카나리 구간 전체, D-10).
- **PoC 2단계**(변수 = repo 전역이라 "SET 후 PoC" = 곧 카나리 — 자기충돌 해소): P-1 = 리터럴 `runs-on: ["mclats-ci-linux"]` 전용 workflow(blast 0, 변수 무접촉) + 양성 대조 job(hosted) 병행 — 미완료 시 판정 무효. P-2 = vars 경유 잔여는 카나리에 흡수(P-1 통과 ⇏ P-2 통과 정직 한정 기록).
- **I-1~I-4 + T-15 무변경 승계**(hard rail). evidence 착지 = 3-tier(L-A git commit 정본 `ci-runner-infra/docs/cutover-evidence/CFP-2963/` / L-B Issue comment / L-C Story §9) — scratch·worktree 착지 금지.

### §결정 6 — 과도기 처분 (R1: bounded transitional 기록)

- 과도기(2026-08-13 변수 삭제 ~ 컷오버 완료) hosted 전량 상태는 **"실행면 부재로 인한 일시 미이행"** 으로 분류한다(C-14 기준 전자) — §결정 2(ADR-147) default 를 용량 축으로 영구 대체하는 것이 아니므로 supersede 비발동. 복귀 조건 = 카나리→웨이브 완료(AC-8/AC-13 재정합), 시한 = hosted 포함분 소진 이벤트 전(고정 날짜 아님 — E2 재계산 승계).
- **Amd5 carve-out 과의 관계**: 과도기 hosted 는 Amd5 carve-out 경로가 **아니다**(C1/C2'/C3 미이행으로 carve-out 은 현재 무효 상태 — sunset 자기발동 정직 기록). 본 §결정 6 이 그 공백을 별도의 bounded 예외로 codify 하며, Amd5 문면은 무접촉이다.
- **F-A 구간 별도 명기**: 2026-08-14 호스트 fleet 4대 재가동 + org online 4 실측 — "전수 offline" 전제의 관측된 파손. 과도기 전칭 서술은 기록 시점 명기 + 컷오버 시점 재실측 없이는 stale. 컷오버 runbook 에 AC-2 재이행 + compose restart policy 처분(재발 방지) 단계를 편입한다(G0/G8).

### §결정 7 — ADR-147 축별 처분 매핑 (R1~R9 — AC-15 이행)

단일 이분법(전체 transitional amendment vs 전체 supersede)은 **기각** — ADR-147 자신의 축-분리 선례(Amd3/Amd4/Amd5 disjoint declare, ArchitectAnalyst 판단기준 1)와 상충한다. 축별 개별 처분 + **ADR-147 원문 무편집·전방 참조**(Amd4 (4) append-only supersede-not-mutate 선례). ADR-147 파일 자체의 amendment(back-ref·C1 문면 정정 등)는 **CFP-2913 완결 후 착수**(Q-2 순차 — 동시 amendment 충돌 배제):

| 항 | 대상 | 처분 | 근거·형태 |
|---|---|---|---|
| **R1** | 과도기 hosted 의 ADR 정합화 | **채택 — 시한부 transitional 기록 (본 ADR §결정 6)** | 실행면 부재의 일시 미이행(C-14 전자) — supersede 비발동. F-A 구간 별도 명기 |
| **R2** | Amd5 C1③④ 재정의 | **채택 — 정의역 분기 (본 ADR §결정 2)** | ③④ = classic 도메인 한정, ARC 도메인 = 레지스트리 + 대체 통제 3층. ADR-147 문면 정정은 CFP-2913 후 amendment 이월 |
| **R3** | C3(ㄱ) 값 공간 폐쇄 재정의 | **채택 — 3rd 도메인 additive 확장 (본 ADR §결정 2)** | 완화 프레이밍 금지 준수 — Amd5 sunset 무저촉. 파일 편집 동일 이월 |
| **R4** | §결정 8 Amd3 extra_hosts 대체 | **채택 — 정의역 자연 축소 기록** | Amd3 문면은 자기 선언상 compose 층 한정 — DooD fleet 존속 구간 한정 유효 존치, Q-8 폐기 시 자연 소멸. ARC 측 해소 = 12-site 값-shape 3-way 승격(본 ADR §결정 8) — ADR-147 편집 불요 |
| **R5** | Amd4 volume/pre-bake 이식 | **채택 — ARC 등가 재정의 (본 ADR §결정 1/4)** | rust pre-bake = 러너 이미지 소결 유지 + 해당 경로 emptyDir/PVC 마운트 금지(마스킹 방지). cargo 공유 RWX PVC 불채택(#3673 + 동시쓰기 corruption). EXDEV 는 pod overlay 에도 잔존 — "compose 소멸=해결" over-claim 금지. VC 편입(Amd4(1))은 `ci-runner-arc/` 로 유효 계승. compose 축(anonymous volume·down -v)은 fleet 존속 구간 한정 유효 |
| **R6** | §결정 8 Amd1/Amd2 credential 재평가 | **채택 — "강화 2축 + 신규 노출 1축의 교환" 으로 codify (본 ADR §결정 3)** | T4/T5 구조 축소(ephemeral·JIT) + 정적 PAT 미사용(App 인증) = 강화 / K8s Secret App key + 러너 SA read(S-1) + apiserver 표면 = 신규 노출. 일방적 강화 서술 금지(SecurityArch O-5). Amd2 4-gate 는 Story-local — 본 Story 미상속·미사용 |
| **R7** | §결정 5 preinstall 소유자 재지정 | **채택 — 소유 = `ci-runner-arc/` 러너 이미지 (본 ADR §결정 1)** | bare-tool baseline 계약 유지 + rust pre-bake(Amd4(3) supersede-in-part 의 ARC 승계). "group6" 지시대상은 Q-8 fleet 폐기 시 자연 소멸. 카나리 leg⑤ 로 실증 |
| **R8** | §결정 8 DooD 위협모델 재작성 | **채택 — ARC 위협모델로 재작성 (본 ADR §결정 3 + Change Plan §7)** | docker.sock 소멸, 신규 경계 = B3(러너↔job pod)/B4(apiserver RBAC)/B5(커널 공유). blast radius = 실거래 노드 — privileged 0 + PSA baseline 생성시점 차단 |
| **R9** | capacity-overflow-roster 존폐 | **이월 — CFP-2913 완결 후 ADR-147 후속 amendment 범위** | 로스터 = Amd5 C1⑤ 소유 자산(CFP-2913 OPEN, phase:구현 실측 2026-08-14) — Q-2 순차 제약상 본 Story 가 선점 편집하지 않는다. 방향 관찰만 기록: ARC 탄력 용량 착지 후 hosted overflow 존재 이유 축소 → 존폐 재판정 필요 |

부수 항(AC-15 분모 밖, 방향 기록): R12 = ADR-048 Amd3 콜드스타트 임계 — 단일 임계 부적절, `cold p95 / warm p95` 2계층 측정 후 확정 + "scale-up 진행 중" 3번째 상태 추가 권고(카나리 실측 입력). R13 = orphan 러너 정리 — Change Plan §11.6 ID-5/ID-6 멱등 절차(1회성 아님 — F-14 stuck 재발 시 orphan 재발). R14 = ADR-164 근거 문면 정밀화 — 후속(watchdog=hosted 결론 무변경, co-death 축 = MCLATS 로 이동). R15 = ephemeral 권고 사정거리 — ARC 는 autoscaling 이라 공식 권고 사정거리 안 재진입(강화 방향 기록).

### §결정 8 — 소비자 workflow 층 처분 (mctrader 12-site + docker-build 4)

- **12-site 존재-truthiness 조건식 → 값-shape 판별 승격(형태 A)**: job-level env 1곳 집약(`rust-ci.yml` rdb-e2e 11 site + `docker-build.yml` smoke 1 site) 후 `(vars.CI_RUNS_ON_LINUX_JSON && contains(vars.CI_RUNS_ON_LINUX_JSON, 'self-hosted')) && 'host.docker.internal' || 'localhost'` — DooD 라벨 값만 host.docker.internal, ARC 이름/unset = localhost(kubernetes mode 는 services 가 job pod sidecar 라 localhost 도달). 신규 변수(형태 B, CI_NETWORK_MODE)는 컷오버·롤백 시 2-변수 동기화 실패라는 신규 드리프트 축을 만들어 기각 — 단일 변수에서 파생하는 A 가 동기화 리스크 0. magic-string 결합('self-hosted' substring)은 §결정 1 (ii)(`self-hosted` substring 금지 — ARC 이름에 구조적 미출현 보장)가 결박. DooD fleet 폐기(Q-8) 후 후속 Story 에서 localhost 고정(조건식 제거) 단순화 가능 — defer 기록. B 승격 재평가 = C1 값검증 배선 Story 시점.
- **docker-build 계열 4 workflow**: composite action `.github/actions/docker-build-push`(build+push 골격) 추출을 **kaniko/buildkit 재편(AC-20)과 동일 변경 단위로 결합 실행** — 재편이 4파일 골격을 어차피 재작성하므로 그 시점 1곳 추출이 최소 침습(선행 분리 시 2회 편집). smoke step 은 `docker-build.yml` 자체 step 존치(구조 차이 억지 통일 금지). reusable workflow(workflow_call)는 caller 재작성 비용 대비 이득 부족으로 기각.

## 결과

- **긍정**: (a) 호스트 Linux CI 부하 철수 경로 확정(사용자 1차 동기) (b) 라우팅 계약(D1~D3) 무변경 — workflow 파일 delta 0 유지 (c) 배포용 ARC CRD 무접촉(0.12.1 pin) — helm uninstall 이 배포용 무영향(ARC 철회 전체 잔재 제거 = Change Plan §11.3b teardown) (d) ephemeral 1 job = 1 pod 로 T4/T5 cross-job 잔재 구조 소거.
- **부정·trade-off**: (a) GitHub 지원 정책 밖 운용(0.12.1) — 통지·수용 필요, 해소 = 후속 0.14+ 통일(무접촉 파기 재확인) (b) S-1 구조 잔여(App key ↔ 러너 SA) — 제거 불가, 완화·회전·통지로 관리 (c) 콜드스타트(minRunners 0) — pre-bake + 2계층 임계 측정으로 관리 (d) REQUIRE_JOB_CONTAINER=true 파생 `container:` 재편 확대(roster 전 Linux job) (e) 지연 tail 미측정(OUT-9) — proxy 통제뿐임을 정직 유지.
- **영향 경계**: `mclayer/ci-runner-infra`(ci-runner-arc/ 신설) + mctrader workflow(12-site + 5 재편 + container: 선언) + org 라우팅 변수(값 shape) + MCLATS(신규 2 ns) + wrapper(`scripts/ci-runner-provisioning-check.sh` 안내 문자열 + arch doc). wrapper templates/`.github` = delta 0. branch protection 8-tuple 무변경.

## 해소 기준

N/A — permanent policy (is_transitional: false). CI 러너 topology 의 영구 invariant. 단 **§결정 6 의 과도기 조항은 자체 bounded**(복귀 조건 = 컷오버 완료 시 자동 소멸 — 조항 단위 시한부, ADR 전체 sunset 아님). 약화 방향(예약 토큰 2단 금지 룰 완화[exact-match 허용 또는 `self-hosted` substring 허용 — §결정 1 (i)(ii)] / REQUIRE_JOB_CONTAINER=false 전환 / PSA enforce 해제 / 신규 group public 허용 / 값공간 미분류 통과) 발의 차단 — supersede ADR 필수.

## 관련 파일

- `docs/change-plans/cfp-2963-mclats-arc-ci-runner.md` — 본 ADR 의 구체화 계약(§7 보안 / §8 Test Contract / §11 마이그레이션·롤백)
- `archive/adr/ADR-147-ci-runner-topology-selfhosted-migration.md` — 축별 처분 대상(원문 무편집 — 파일 amendment = CFP-2913 완결 후)
- `scripts/ci-runner-provisioning-check.sh` — 안내 문자열 delta(본 Story). 값-검증 3-domain 층3 분류기 = C1 값검증 배선 후속 Story 이월(본 Story = `_classify_value` 시그니처 기록만, 구현 0 — D-5 시점 통일)
- `docs/architecture/codeforge-family.md` — GHActions 노드·Trust boundary substrate 분기 갱신
- `mclayer/ci-runner-infra` `ci-runner-arc/` — ARC 자산 착지(신규)
