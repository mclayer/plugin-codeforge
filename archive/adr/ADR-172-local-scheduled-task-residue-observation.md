---
adr_number: 172
title: 로컬 스케줄 작업 기반 세션-독립 잔재 관측 — 도입기 관측-only 와 승격 게이트
date: 2026-08-13
status: Accepted
category: orchestration-discipline
carrier_story: CFP-2949
supersedes: null
amends: null  # new-sibling — ADR-128 §결정 4 정의역 amendment 는 별 carrier(§결정 7). 기존 계약 supersede 0.
related_adrs:
  - ADR-128  # 완료 단계 수렴 — §결정 4 "단일 자동 수렴 검증기 구조적 불가" 의 정의역이 본 ADR 로 좁혀짐 (§결정 7)
  - ADR-169  # 세션 잔재 수명 규약 — 잔여 4클래스 중 crash 미발화 1건이 본 ADR 의 겨냥 대상. §결정 4 가 OS 스케줄러를 opt-in 보조로 격하한 판례 승계 (§결정 7)
  - ADR-110  # prior art — Windows Task Scheduler 로 세션 밖 Claude Code 자동 재개. disjoint-layer write boundary 원칙 동형
  - ADR-106  # 관측→보고→판정→집행 4단계. 본 ADR 은 관측·보고까지만 (판정·집행 0)
  - ADR-026  # post-merge automation — telemetry only / disable-by-flag / idempotency. 이중 자동화 경합 경계 대상
  - ADR-040  # worktree convention — 관측 대상 도메인 정의
  - ADR-119  # 검증 후 단언 — lever 계상 금지 조건·미확인 declare 의 근거
  - ADR-112  # living-arch declare 요건 (closed-binary) — 본 ADR 은 declare 부적격
  - ADR-133  # ADR 번호 atomic claim — 본 ADR 번호(172) 예약 mechanism
  - ADR-145  # AC traceability zero-drop — normative AC ↔ 명명 테스트 Hop2
  - ADR-109  # 429 완화 — 세션 내부 정의역이라 본 트래픽 미통제 (주기 선택이 유일 lever)
related_stories:
  - CFP-2949
related_cfps:
  - CFP-2949  # carrier — Desktop 로컬 스케줄 작업으로 잔재 정리 자동화
related_files:
  - scripts/lib/check_workspace_residue_discovery.py  # 관측 대상 스캐너 (mode 분기 = 관측-only 게이트 1)
  - scripts/lib/check_codeforge_scratch_ttl.py  # GC_DRY_RUN 게이트 2
  - scripts/lib/check_harness_temp_residue.py  # TEMP_GC_DELETE_ENABLED default-off 게이트 3
  - docs/orchestrator-playbook.md  # 비대화형 호출 계약 서브섹션 + ADR-128 정의역 mirror 5 anchor
  - skills/worktree-lifecycle/SKILL.md  # 정본 절차 SSOT (부트스트랩 지목 대상)
is_transitional: false
mechanical_enforcement_actions: []  # Phase 2 이행 — scheduled_task_reconcile.py + §8 명명 테스트(normative 9건) + playbook/skill 편집. 본 ADR = 결정 SSOT.
---

# ADR-172: 로컬 스케줄 작업 기반 세션-독립 잔재 관측 — 도입기 관측-only 와 승격 게이트

## 상태

Accepted (2026-08-13) — CFP-2949 Phase 1(설계) carrier.

## 컨텍스트

codeforge 의 로컬 잔재 수렴(worktree eager teardown · residue-clean · scratch TTL · orphan 판정)은 **Orchestrator 자율준수에 의존**한다. required CI 로 승격할 수 없는데, 그 이유가 구조적이다 — 잔재 스캔 대상(`~/.claude/worktrees` · `~/.claude/codeforge-scratch` · workspace root · Temp)이 **운영자 홈에 결박**돼 있고 GitHub Actions 러너에는 그 홈이 존재하지 않는다. ADR-128 은 이를 "단일 자동 수렴 검증기 **구조적 불가**"로, ADR-169 는 잔여 4클래스(crash 미발화 · advisory ceiling · fail-safe 보수성 · per-repo 협소)로 각각 박제했다.

여기에 **세션과 독립적으로 운영자 머신에서 세션을 자동 개시하는 실행 surface**(Claude Desktop 로컬 스케줄 작업)가 등장했다. 이 surface 는 로컬 FS 도달 · 최소 간격 1분 · 세션 독립을 **동시에** 만족하는 유일한 축이다(Actions 는 로컬 미도달, 관리 클라우드·self-hosted 는 운영자 홈이 기본 구성 밖).

동시에 이 surface 는 codeforge 에 **신뢰 밖 입력을 신뢰 안 환경에서 처리하는 최초 노드**를 도입한다. 지금까지 모든 기계 주체(Actions 러너)는 신뢰 밖 입력을 신뢰 밖 환경에서 처리했다. 스케줄 작업 세션은 운영자 머신에서 사람 없이 개시되며 자격증명 5종을 **주입이 아니라 상속**한다.

실행 surface 선택은 2026-08-12T12:15:00+09:00 사용자 결정이며, 그 지위는 **가치 판단**이다(배제된 축들은 "도달 불가"라는 사실 주장이 아니라 비용·위험 판단으로 범위 밖).

## 결정

### §결정 1 — 채택 surface 와 도입 곡선

로컬 스케줄 작업을 채택하되 **도입기는 관측-only** 로 고정한다. 산출은 `선언값 · 실측값 · 불일치` **사실 3-tuple** 이며, `PASS`/`FAIL`/`OK`/`정상`/`문제없음` 같은 **verdict 어휘가 등장하면 그 순간 ADR-106 의 "판정" 단계에 진입**해 기결정을 위반한다. 하위 스크립트 출력에 verdict 어휘가 있으면(실측 오염원 1건 존재) **그 줄은 인용하지 않고 수치 필드만 재서술**한다.

**1호 대상 = 로컬 잔재 관측 보고 1종.** 3필터(주기 ≥1분 ∧ 실행 예산 ∧ 로컬 FS 도달) AND 통과 ∧ 기존 workflow 116개와 중복 0(그 0 은 구조적 — Actions 러너에 운영자 홈이 없어 해당 workflow 가 작성될 수 없다).

### §결정 2 — 정본 SSOT 무손상, 저장 프롬프트는 부트스트랩

절차 정본은 **기존 skill** 이다. 저장 프롬프트는 절차를 **0줄** 담고 정본을 지목만 한다. 정본 미도달 시 fallback 은 **정직 중단**이며 **경로 하드코딩은 금지**한다(정본 이동 시 조용히 stale 해져 hollow 가 된다). 정본 skill 에 "스케줄 작업 인지 분기"를 넣는 **역참조를 금지**한다(현재 정본 2종에 관련 리터럴 0건이며 이 0 을 불변식으로 유지).

부트스트랩 프롬프트 전문은 **본 ADR 에 박제**한다 — repo 신규 지시 파일을 만들지 않으면서 프롬프트 축의 버전관리·리뷰를 성립시키는 유일한 자리다.

```
codeforge 로컬 잔재 관측 (관측-only · 보고 전용)

1. <repo 절대경로> 로 cd 한다. 작업 디렉터리 설정에 의존하지 않는다.
2. codeforge:worktree-lifecycle skill 의 잔재 관측 절차를 정본으로 읽는다.
   정본을 찾지 못하면 "정본 미도달" 을 사실로 보고하고 즉시 종료한다.
   절차를 기억이나 추측으로 대체하지 않는다.
3. scripts/lib/scheduled_task_reconcile.py 를 실행한다.
4. 그 산출을 그대로 보고 채널에 전달한다.

금지: 파일 삭제·이동·worktree 제거·stash drop / GitHub label·state·merge·close 변경 /
      보호 브랜치 push / 자기 스케줄·프롬프트 수정 / 하위 출력의 verdict 어휘 인용.
이 작업은 관측하고 보고만 한다. 판정도 집행도 하지 않는다.
```

### §결정 3 — 정의 거버넌스: two-master 는 **잔존한다**

프롬프트 축은 §결정 2 로 git-resident 가 되지만, **등록 축(schedule · folder · model · enabled · permission mode)은 git 으로 재현할 수 없다.** 등록 상태를 repo 에 미러하는 선언 파일은 **도입하지 않는다** — 등록 상태를 기계 판독할 표면이 없어 **drift 대조 수단이 없고**, 대조 불가능한 미러는 버전관리의 외형만 만들고 실질을 주지 않는다.

⇒ **`[git-재현-불가: 등록 축]` 으로 라벨하고 수기 절차로 인정한다. "two-master 없음" 이라고 쓰지 않는다.**

### §결정 4 — 관측-only 의 기계 lever 와 **계상 금지 조건**

기계 강제는 두 층에서만 성립한다.

1. **스크립트 층 3중 게이트** — `mode`=observe-only(삭제 코드경로 미진입) ∧ `GC_DRY_RUN=1`(실 삭제 직전 분기) ∧ `TEMP_GC_DELETE_ENABLED` unset. **신규 플래그 0건.**
2. **권한 층** — `permissions.deny` 키 신설(전 모드에 적용되는 유일 통제이며 **현재 키 부재**) + per-task permission mode `Manual` 고정 + `disableBypassPermissionsMode`.

**host `~/.claude/settings.json` 을 방어 lever 로 계상하지 않는다** — 실측이 `allow` 40건 · `deny` 키 부재 · `defaultMode: bypassPermissions` 이므로 **넓히는 방향으로만 작동하며 제한 기여가 0** 이다. 제한 기여 0 인 항목을 lever 로 세는 것 자체가 검사연극이다.

★ **계상 금지 조건**: 위 권한 층은 **`deny` 가 스케줄 작업 세션에 실제로 적용되는지를 live 실측하기 전까지 lever 로 계상하지 않는다.** 미실측 상태의 "안전하다"는 서술은 그 자체가 검사연극이다(ADR-119).

### §결정 5 — reconcile 은 **상태 무의존**이고 **결정론 코드**다

플랫폼이 누락 실행을 회수할 때 **최근 1회만 실행하고 나머지는 폐기**하므로, 대상을 "이 tick 이 담당하는 구간"으로 정의하면 폐기된 tick 의 대상이 **영구 미관측**이 된다.

⇒ 대상은 `g(현재 상태)` 다. **매 실행이 현재 잔재 전량을 재관측**하고 상태를 이월하지 않는다. dedup 키는 `class + 홈-상대 경로` 로 **대상에서 유도**하며 저장하지 않는다(상태 파일을 두면 그 파일 자신이 잔재가 되는 자기참조가 생긴다). dedup 상태의 실질 저장소는 **append-only 보고 채널 자신**이며, 조회 실패는 **fail-closed**(다음 실행이 자기치유).

**이 reconcile·dedup·마커 부착은 자연어 프롬프트가 아니라 결정론 CLI 에 둔다.** 프롬프트에 두면 검사 대상이 LLM 이 되어 해당 수용 기준들의 결정론 오라클이 붕괴하고, 그러면 그 기준들을 강등해야 하는데 강등 근거가 없다. 이는 §결정 2 의 "지시 파일 금지"에 저촉되지 않는다 — 금지 대상은 **절차를 서술하는 지시 파일**이지 **절차를 실행하는 코드**가 아니다.

### §결정 6 — 운영 파라미터 (전건 확정)

| 항목 | 값 | 근거 |
|---|---|---|
| 주기 | **Daily** | 실행 예산 소비 여부가 미확인이므로 보수 선택. 잔재는 누적형이라 저빈도에서 가치 손실이 작다 |
| worktree 격리 토글 | **OFF** | ON 은 실행마다 worktree 를 만드는데 **생성 위치·회수 주체가 둘 다 미확인**이다. 잔재 스캔 도메인에 생기면 매 보고가 자기 소음이 되고, workspace root 에 생기면 유일한 삭제 허용 root 에 자기 발밑을 넣는다. **미확인은 안전 근거가 아니다** |
| 작업 디렉터리 | **기존 main 체크아웃** | **INV-OBS: 관측자는 자기 관측 도메인에 새 객체를 추가하지 않는다.** 이미 존재하는 객체라 신규 0 |
| 긴급 정지 | **2-플래그 OR, fail-closed** | 기존 repo-resident 플래그는 **활성화에 커밋이 필요**해 즉시성이 없다. 신규 로컬 플래그를 **scratch 밖**(`~/.claude/worktree-gc-state/`)에 둔다 — scratch 에 두면 TTL purge 가 7일 뒤 **정지 장치를 조용히 삭제**한다 |
| 생존 감시 | **로컬 세션 시작 축 watchdog** | 클라우드 역구조는 성립하나 **겨냥이 틀리다** — 승인 대기 정지와 앱 미상주를 구별할 정보가 없어 머신 오프 구간을 전부 오탐한다 |

### §결정 7 — 선행 결정과의 관계

- **ADR-128 §결정 4 정의역 amendment 를 발의한다** — "구조적 불가"의 정의역을 **클라우드 평면**으로 좁히고 세션 독립 로컬 스케줄러는 그 정의역 밖임을 각주한다. 약화되는 통제 0(순수 정의역 명확화). **단 "기계 게이트 신설 과설계 금지" 조항은 무손상 유지** — 정의역을 좁힌 것이 새 게이트를 만들어도 된다는 허가가 아니다.
- **ADR-169 본문은 amendment 하지 않는다** — 본문에 "클라우드 러너" 표현이 없다(그 표현은 playbook 전용). playbook mirror 만 수정한다.
- **★ ADR-169 §결정 4 판례를 승계한다** — 그 결정은 **같은 문제 도메인(로컬 잔재 GC)에서 이미** OS 스케줄러를 "**opt-in 보조이며 주 트리거가 아님**"으로 격하했다. 본 ADR 의 도입기 관측-only 는 이 판례와 정합이나, **주 트리거·required 로 승격하려면 그 판례의 재검토가 선행 의무**다.

## 결과

**얻는 것**: ADR-169 잔여 4클래스 중 **1건(crash 미발화 = observer-death)** 에 대해, 세션과 독립된 관측자가 사실을 보고한다. 나머지 3건은 본 ADR 이 해소하지 않는다(advisory ceiling 은 승격 이후 영역, fail-safe 보수성은 orthogonal, per-repo 협소는 ADR-169 §결정 2 가 이미 독자 해소).

**치르는 것 (honest ceiling — 결함이 아니라 선언된 상한)**

1. **다른 운영자는 본 결정을 merge 하는 것만으로 아무것도 얻지 못한다.** 작업 정의가 repo 밖 이 머신 로컬 config 다. "자동화를 배포했다"는 서술은 과장이다.
2. **등록 축 two-master 잔존** (§결정 3).
3. **관측 공백에 절대 상한이 없다** — 앱 미상주와 승인 대기 정지 어느 쪽도 문서상 상한이 0 이다. "공백 ≤ X" 를 단정하지 않는다.
4. **무음 사망은 탐지되지 않는다** — 승인 대기 정지는 막힌 것이 도구 호출 자체라 **자기보고가 원리적으로 불가능**하다. watchdog 은 완화이며 **watchdog 의 watchdog 은 없다. 최종 backstop 은 사람이다.**
5. **prompt-injection 은 완전 차단 불가** — 이 형상에서 플랫폼 안티-인젝션 4종이 전건 무력하다(권한 시스템은 `bypassPermissions` 가 무력화하며 문서가 "prompt injection 에 대한 보호를 제공하지 않는다"고 명시, 컨텍스트 격리는 특정 도구 한정, 승인 전 검토는 무인 실행이 정의상 제거, VM 권고는 로컬 FS 도달이라는 채택 근거와 충돌). 완화는 읽는 표면 축소 + 재량 축소이며 **잔여가 남는다**.
6. **상속 자격증명은 회수 불가** — `deny` 는 도구층 차단이지 scope 축소가 아니다.
7. **명의 귀속의 근본 해소는 별 identity 발급인데 그것은 "자격증명 주입 0" 원칙과 정면 충돌한다** — 진짜 trade-off 이며 본 ADR 은 마커 완화만 선택했다.
8. **비대화형 호출 계약은 문서 = advisory.** 기계 강제는 §결정 4 두 층에만 있다.

**승격은 본 결정의 범위 밖이다.** 본 ADR 이 정하는 것은 승격 게이트의 설계(조건 · 주체 = **사용자** · rollback 경로 3종)까지이며 승격 실행은 별 Story 다. 자동 승격은 금지된다.

## 관련 파일

- `scripts/lib/check_workspace_residue_discovery.py` — 관측 대상 스캐너. `mode` 분기 = 관측-only 게이트 1
- `scripts/lib/check_codeforge_scratch_ttl.py` — `GC_DRY_RUN` 게이트 2
- `scripts/lib/check_harness_temp_residue.py` — `TEMP_GC_DELETE_ENABLED` default-off 게이트 3
- `scripts/lib/scheduled_task_reconcile.py` — **Phase 2 신설.** 결정론 reconcile·dedup·마커 배선 (§결정 5)
- `docs/orchestrator-playbook.md` — 비대화형 호출 계약 서브섹션 + ADR-128 정의역 mirror 5 anchor (§결정 7)
- `skills/worktree-lifecycle/SKILL.md` — 정본 절차 SSOT, 부트스트랩 지목 대상 (§결정 2)
- `~/.claude/scheduled-tasks/<task-name>/SKILL.md` — 작업 프롬프트. **repo 밖 user-level**

## 해소 기준

N/A — permanent policy. 단 **승격 시점에 §결정 1·4·5 의 전제가 재검사 대상**이 된다(관측-only 가 깨지면 §결정 5 의 경합 방어 근거인 "read-modify-write 부재"도 함께 깨진다). 실행 surface 가 폐지되거나 로컬 잔재 수렴이 다른 경로로 required 승격되면 본 ADR 은 재검토된다.
