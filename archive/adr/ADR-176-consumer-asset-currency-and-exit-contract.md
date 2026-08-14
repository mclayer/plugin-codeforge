---
adr_number: 176
title: consumer 배포 자산 currency 축 — 최신성 판정·전파 성공 기준 + mode-scoped exit 소비 계약
status: Proposed
is_transitional: false
category: governance
date: 2026-08-15
carrier_story: CFP-2978
related_adrs:
  - ADR-130-applicability-closure-integrity  # 2축(applicability ⊥ closure) SSOT — 본 ADR 이 3번째 직교 축을 additive 신설
  - ADR-076-declarative-reconciliation-upgrade  # L128 이 cp -n 갱신 불가를 기록만 하고 대안 미규정 — 본 ADR 이 그 잔여를 수령
  - ADR-027-consumer-adoption-protocol  # §결정 7.A.1 marker 표에 .py 의도적 제외 / §결정 7.C wholesale + loss report
  - ADR-116  # reconcile-then-patch — 패턴 재사용 가능, 선결조건(보존 대상의 구조화 선언) 부재
  - ADR-171  # evidence-enforceable promotion 재제정본 (ADR-060 supersede) — warning→blocking 승격은 별 carrier
  - ADR-073-orchestrator-verify-before-assert  # Amendment 2 = 센티널 기능 계약 SSOT (mode enum) — 본 ADR 은 그 exit 의 소비 계약만 규정
  - ADR-119  # 검증 후 단언 — UNDECIDABLE 을 PASS 로 흡수 금지의 상위 규범
  - ADR-085-multi-session-collaboration-protocol  # 센티널의 상위 규범 홈 (전파 조항은 부재)
related_files:
  - templates/consumer-scripts.manifest
  - scripts/lib/check_parallel_work_sentinel.py
  - .github/workflows/parallel-work-sentinel-check.yml
  - docs/architecture/codeforge-family.md
  - docs/domain-knowledge/concept/shared-script-distribution-and-drift.md
related_stories:
  - CFP-2978
  - CFP-2451  # consumer 동결 기준점 — manifest 등재(전파 선언)를 도달로 추정한 지점
  - CFP-2976  # prefix fail-closed + determined 계약 신설 (본 ADR 의 어휘 원천)
---

# ADR-176: consumer 배포 자산 currency 축 — 최신성 판정·전파 성공 기준 + mode-scoped exit 소비 계약

## 상태

`Proposed` (2026-08-15 KST) — CFP-2978 Phase 1 설계 lane draft. ArchitectAgent chief author 작성, ArchitectPLAgent 검수 후 Accepted 전이. adr_number = ADR-133 claim primitive 반환값 176 (state branch `adr-reservation-state` OCC, claimant `ArchitectAgent:CFP-2978:20260815-040900`, `claimed` — max+1 재계산 미사용).

## 컨텍스트

wrapper 정본 `scripts/lib/check_parallel_work_sentinel.py` 가 consumer 4곳(mctrader / -backtest / -market / -engine)에 손복사돼 있고, 그 사본은 CFP-2451 `0dfb29f59` 세대(blob `07d1127a`)에서 **동결**된 채 정본만 3 커밋(행동 기준 2세대) 전진했다. 그 결과 consumer 사본은 형제 Story 가 실재하는데도 `{"matches": []}` 를 내는 **판별력 0** 상태이며, 그 빈 결과가 착수 통행증으로 소비된다. [verified — CFP-2978 §1(C) firsthand 실행 대조]

문제의 성격은 "복사를 안 했다"가 아니다. 세 층이 각각 제 몫을 했는데도 격차가 살아남았다:

- **선언면**은 정확하다 — `templates/consumer-scripts.manifest` L134-135 가 `.sh` + depth-2 `.py` 둘 다 등재해 ADR-130 closure-완전성을 정확히 이행했다. [verified]
- **실행면**은 create-only 다 — `overlay/hooks/regen-agents.sh` 의 `cp -n`(no-clobber)과 `bootstrap-consumer.sh` Stage 7 의 `if [ ! -f "$target" ]` 는 **파일이 있으면 절대 갱신하지 않는다**. ADR-076 L128 이 이 한계를 이미 명문화했으나 **기록만 하고 대안을 규정하지 않았다**. [verified — 원문 대조]
- **검사면**은 정본 쪽만 본다 — `scripts/check-consumer-scripts-manifest.sh` 6 Check 는 전부 wrapper 내부 속성이고, consumer 실물 내용을 대조하는 게이트는 **0건**이다. [verified]

근본 공백은 도메인 모델 자체에 있다. ADR-130 은 **applicability**(이 자산이 consumer 에 적용 대상인가) ⊥ **closure**(적용 대상이 실행 가능하려면 무엇이 함께 배포돼야 하는가) **2축만** 정의하고, closure 는 `mirror-dependency-closure.py:178 if not dep_path.exists()` 처럼 **존재만** 검사한다. "있는 것이 최신인가"를 묻는 술어가 정의 자체로 없다 — ADR-130 전문에서 `currency`·`최신성` grep **0 hit**. [verified — ArchitectAnalystAgent 원문 대조] 따라서 어떤 게이트도 이 결함을 **볼 수 없다**. "ADR-130 이 이미 덮는다"는 주장은 원문 대조로 거짓이다.

두 번째 공백은 층 간 exit 소비 계약이다. py 는 exit 2 를 fail-closed 로 정의하는데 workflow 는 그 종료코드를 OR-true 관용구와 `continue-on-error` 로 흡수한다. "누가 어느 층에서 판정을 소비하는가"가 어느 문서에도 없어, py 의 fail-closed 신설(CFP-2976)이 CI 표면에 **원리적으로 도달하지 못했다**. live 실증 — mctrader-market run `31611905461`(2026-08-12)이 MKT repo 에서 `STORY_KEY_PREFIX=CFP` 로 스캔하고 conclusion=success 로 끝났다(정의상 공집합). [verified — PL firsthand `gh run view --log`]

이 도메인의 실패 모드는 오탐이 아니라 **공허한 통과**다. 센티널 산출물은 "찾았다"가 아니라 **"없다"**이고 그 "없다"가 착수 통행증으로 소비되므로, 안 찾은 것과 없는 것이 구분 불가해지는 순간 장치의 가치는 0 이 아니라 **음수**가 된다(없는 안전을 근거로 착수). 개념 정의 = `docs/domain-knowledge/concept/vacuous-pass.md` + `docs/domain-knowledge/concept/shared-script-distribution-and-drift.md`.

## 결정

### §결정 1 — currency = upgrade-flow 도메인의 3번째 직교 축 (ADR-130 2축에 additive)

consumer 배포 자산의 판정 축을 **3축**으로 확장한다. 기존 2축은 무변경 — 축 삭제·완화가 아닌 순수 additive 확장이며, ADR-058 §결정 5 역-ratchet 정의역 밖(강화 방향)이다.

| 축 | 묻는 것 | 판정 대상 | SSOT |
|---|---|---|---|
| applicability (수평) | 이 자산이 consumer repo 에 **적용 대상**인가 | whitelist 등재 여부 | ADR-130 §결정 2 (무변경) |
| closure (수직) | 적용 대상이 **실행 가능**하려면 무엇이 함께 배포돼야 하는가 | manifest 폐포 + `dep_path.exists()` | ADR-130 §결정 3 (무변경) |
| **currency (시간) — 신설** | **배포된 것이 정본의 현세대인가** | 사본 ↔ 정본의 **blob 동일성** | **본 ADR** |

- **축의 독립성**: applicability=Y ∧ closure=Y ∧ currency=N 인 상태가 실재한다(consumer 4곳의 현 상태가 정확히 그것) — 기존 2축의 어떤 조합으로도 표현되지 않으므로 파생 축이 아니다.
- **별 ADR 로 신설한 근거**: ADR-130 §결정 9 가 강화 확장을 환영하는 ratchet 구조를 갖춰 amendment 흡수도 정합하나, ADR-083→ADR-130 선례(L284 "축 분리 = 별도 ADR 가 이력 추적성 우수")를 따른다. ADR-083 은 **Sunsetted, ADR-130 이 supersede** 하므로 인용은 ADR-130 을 정본으로 한다.
- **정의역 한정 (본 Story 실적용 범위)**: 본 ADR 은 currency 축을 **개념·판정 요건 수준에서 정의**하고, 그 기계 강제의 실적용 대상은 CFP-2978 사용자 확정(§5.5)에 따라 `scripts/lib/check_parallel_work_sentinel.py` **1개 파일**로 한정한다. manifest 81 자산 전면 적용은 **기각됨**(consumer workflow blob 이 이미 3종으로 분기했고 marker 실물 0개라 전면 갱신 의미론이 3 repo 의 의도적 `concurrency:` 삭제를 되주입한다 — ADR-027 §결정 7.C wholesale 경로의 loss 실물). 축의 **정의**는 일반이고 **강제의 정의역**은 좁다 — 이 비대칭을 감춘 채 "전면 currency 강제 도입"으로 인용하는 것을 금지한다.

### §결정 2 — currency 판정의 구조 요건 4종 (검사연극 차단)

currency 를 주장하는 어떤 게이트도 아래 4 요건을 갖춰야 한다. 하나라도 빠지면 그 게이트는 currency 를 판정한다고 **선언할 수 없다**.

- **(R1) pin — 기계 판독 가능한 정본 참조 기록.** 사본이 정본의 어느 blob 에 대응하는지를 consumer repo 안의 선언 파일에 기록한다. pin 이 없으면 drift 는 비가시다(현재 consumer 5곳 어디에도 pin 이 없다 — `.wrapper-managed-manifest.json` 은 5곳 전부 404, wrapper 쪽 실물도 settings.json key mirror 선언이지 스크립트 버전 pin 이 아니다 [verified]).
- **(R2) 2분할 질의 — Q1(로컬) ⊥ Q2(상류).** Q1 = 사본이 자기 repo 의 pin 과 일치하는가(**네트워크 0 · 자격증명 0 · rate limit 0 → 항상 판정 가능**). Q2 = pin 이 정본과 일치하는가(네트워크 1콜). 분리하면 egress·rate 장애에서도 **검출력의 절반이 무조건 생존**하고, 부분 적용 상태(사본만 갱신 / pin 만 갱신)가 로컬에서 완결 판정된다.
- **(R3) UNDECIDABLE ≠ PASS.** 대조 대상을 읽지 못한 상태는 GREEN 이 아니다. 소진·도달불가·파싱실패는 기존 어휘를 재사용해 표면화한다 — `degradation` 라벨 + `marker` + **`determined` 키 부재**. `{"drift": false}` · `null` · 빈 결과 · 필드 생략은 **전부 조용한 PASS 이므로 금지**. 근거 = 이 도메인의 실패 모드가 정확히 그것이고(§컨텍스트), ADR-119 §④(게이트 verdict 는 outcome ground-truth 로만 단정)의 직접 귀결이다.
- **(R4) 비교자 = git blob SHA.** 작업트리 바이트 해시·`sha256(file)`·byte diff 는 **금지**한다 — consumer 3곳(backtest/market/engine)이 CRLF 체크아웃이라 작업트리 바이트(18297B)가 blob(17814B)과 다르다. 판정은 줄바꿈 변환에 **불변**이어야 한다. 로컬 측 정본 조회는 `git rev-parse HEAD:<path>`(커밋 트리 직독 — `.gitattributes` 필터 무관), 원격 측은 REST contents 응답의 `sha` 를 쓴다. 양쪽 모두 git blob SHA-1 이라 직접 비교 가능하다. [verified — 비인증 REST `sha` = 로컬 `git rev-parse HEAD:` = `git hash-object` 3-way 일치, SecurityArch E-1/E-2/E-5]

### §결정 3 — currency 판정 채널의 신뢰경계 제약 (방향 · 자격증명 · 수신 바이트)

currency 의 Q2(상류 조회)는 **신뢰 기울기를 거슬러 올라가는 read** 이므로 채널 자체가 위협면이다. 아래를 구속한다.

- **(C1) 방향 = consumer CI → wrapper(PUBLIC) read.** 역방향(wrapper CI 가 consumer 를 읽음)은 **금지**한다. 근거 2건 각각이 단독 기각 사유다 — (i) PUBLIC repo 의 CI secret 에 PRIVATE/INTERNAL read 토큰이 상주하게 되고(CWE-522), 이는 App/OIDC 로 좁혀도 *토큰 또는 토큰 발행 능력이 PUBLIC repo CI 에 존재한다*는 사실이 불변이다 (ii) fork PR 에는 `GITHUB_TOKEN` 외 secret 이 전달되지 않으므로 [source: docs.github.com/actions — *"With the exception of `GITHUB_TOKEN`, secrets are not passed to the runner when a workflow is triggered from a forked repository."*] 게이트가 **가장 낮은 신뢰 모집단에서 확정적으로 무력화**된다 — fail-closed 로 두면 전 fork PR 영구 차단, degrade 시키면 vacuous pass 로 **본 결정이 없애려는 결함의 자기 재현**이다.
- **(C2) 자격증명 최소 = 권한 0 을 1차로.** 상류가 PUBLIC 이므로 비인증 조회로 성립한다 [verified — 비인증 `curl` 로 wrapper contents API `sha` 획득]. 신규 PAT·GitHub App **도입 금지**. 인증이 필요한 경우에도 consumer 자기 `GITHUB_TOKEN`(기존 `contents:read` 등 read-only, **permissions 블록 확장 금지**)만 쓴다. 예산 근거 = 인증 1,000 req/hr **per repository** vs 익명 60 req/hr **per originating IP** [source: docs.github.com/rest — rate limits]. 후자는 self-hosted fleet 8 컨테이너가 bridge 네트워크로 단일 공인 IP 를 공유하므로 버스트에서 실제로 닿을 수 있다 — 그래서 인증을 1차, 익명을 2차, 둘 다 실패를 R3 degrade 로 둔다. 3단 어디서 멈추든 조용한 PASS 가 나오지 않는다.
- **(C3) 수신 바이트 최소화 = 디렉토리-listing 채널, 파일-단위 채널 금지.** REST 의 **파일 단위** contents 응답은 `content`(base64 전문)를 **반드시 포함**하므로 "실행하지 않는다"가 *지켜지길 바라는 정책*이 된다. **디렉토리 listing entry 에는 `content` 키 자체가 부재**하다 [verified firsthand — 디렉토리 조회 entry 키 = `_links`/`download_url`/`git_url`/`html_url`/`name`/`path`/`sha`/`size`/`type`, `'content' in e` = False]. 따라서 **"받지 않은 것은 실행될 수 없다"가 구조적 사실**이 된다. 부수 금지: `raw.githubusercontent.com`·`download_url` 2차 요청 금지(봉인 우회로), 리다이렉트 비추종, 원격 유래 값을 exec/eval/import/subprocess 인자·경로 성분으로 사용 금지, 소비 직전 `^[0-9a-f]{40}$` 검증 후에만 사용(불일치 = UNDECIDABLE). 이 제약이 지켜지면 원격에서 프로세스로 유입되는 총 데이터는 **40-hex 문자열 N개 + 파일명 문자열**이며 그 값 공간에 실행 가능한 형태가 없다.
- **(C4) 런타임 전제 = `python3`(하한 3.10, stdlib only) + `git` + `curl` 3종.** `yq`·`gh`·`uv`·PyYAML 등 3rd-party 의존 **금지** — self-hosted 러너 이미지(`ci-runner-infra` `ci-runner-linux/Dockerfile`, base `ubuntu:22.04`)에 `yq`·`gh` 가 **부재**하고 [verified — Dockerfile 실독 + live run 4/4 교차 일치], 의존을 늘리는 설계는 그 fleet 에서 **조용히 degrade** 한다.
- **(C5) 재시도·backoff 도입 금지.** primary rate limit 응답에는 `retry-after` 가 없어 간격을 근거 있게 정할 수 없고, `synchronize` 트리거가 다음 push 를 자연 재시도로 만들며, in-step 재시도는 공유 IP 예산을 더 빨리 태운다. **1회 시도 후 degrade**.
- **(C6) 상태는 각 consumer repo 안에만.** wrapper 에 N-repo 집계 원장을 두는 것을 **금지**한다. 게이트는 자기 repo 내용의 순수 함수(+ 상류 sha 1개 조회)여야 하며, 그래야 부분 적용이 **정의상 유효한 중간 상태**가 되어 머지 순서 제약이 소멸한다. 판정 경로는 read-only 를 유지한다(자동 bump PR·코멘트·label write 금지 → 멱등성이 증명할 상태 없이 구조적으로 성립).

### §결정 4 — 전파 성공의 판정 기준 = currency 달성 (G-5 흡수)

"전파했다"를 **선언(manifest 등재)이나 존재(`dep_path.exists()`)로 판정하는 것을 금지**한다. 전파 성공 = **currency 달성**, 즉 §결정 2 R1-R4 를 갖춘 판정이 `determined` 를 동반해 일치를 산출한 상태다.

- 이 기준이 없어서 발생한 것: CFP-2723 이 "manifest 가 2종 copy 를 의무화 [verified]" 로 등재를 **도달로 추정**하고 consumer 실물을 확인하지 않았다. 독립 방증 — 같은 manifest 에 등재된 `check-rebase-staleness-sentinel.sh` 는 consumer 5곳 **전부 404** 다(create 경로조차 도달하지 않았다). [verified]
- **파생 규율**: manifest·whitelist 등재는 *미래* consumer 를 위한 선언이며 **기존 consumer 로의 배포를 의미하지 않는다**. 기존 consumer 배포는 명시적 배포 단계(PR)로 수행하고, `cp -n` create 경로에 의존해 "붙었을 것"으로 계상하는 것을 금지한다.
- G-5 를 별 축으로 신설하지 않는다 — "전파 성공 = ?"은 currency 가 정의되면 자동 도출되는 corollary 이며, 별 ADR 로 쪼개면 중복 축이 생긴다.

### §결정 5 — mode-scoped exit 소비 계약 (G-3)

exit code 의 의미는 **호출 mode 별로** 정의되며, 소비층(shell wrapper / workflow / Orchestrator)은 자기가 호출한 mode 의 계약만 참조한다. 신규 어휘를 발명하지 않고 기존 값공간을 mode 축으로 분해한다.

| exit | 의미 | consumer 가 호출하는 mode (`title-search`) | 비고 |
|---|---|---|---|
| 0 | PASS 또는 honest-degrade | **계약 내** — 판별자는 rc 가 아니라 산출 문면(`determined` 의 **값** + 도메인 필드 **내용**) | rc=0 은 서로 다른 의미 상태 최소 5종을 덮는다 |
| 1 | reserved | 미사용 | 값공간 예약 |
| 2 | SETUP error (stderr JSON `error_kind`) | **계약 내** — `prefix_undetermined` 등 fail-closed | argparse native usage 오류도 2 (판별 = stderr 의 `error_kind` JSON 유무) |
| 3 | INCONCLUSIVE | **계약 밖** — NG-17 gate mode 전용, consumer 미호출 | 별 mode 의 값공간, `title-search` 로 관측되지 않음 |

- **(E1) rc 단독 판정 금지 — 전 소비층 구속.** rc=0 은 (i) 판정 완료·형제 있음 (ii) 판정 완료·형제 없음 = **유일한 정당 통행증** (iii) `determined: false` 판정 실패 (iv) bypass 산출(`determined` 키 부재) (v) degrade 산출(`determined` 키 부재) 를 모두 덮는다 [verified firsthand]. `rc == 0` 은 필요조건으로만 쓰고 단독 충분조건으로 쓰지 않는다.
- **(E2) 통행증 자격 = `determined == true` 인 산출뿐.** bypass 산출은 verdict 가 아니며 하류가 부재 증명으로 읽어선 안 된다.
- **(E3) 소비층은 판정을 은폐하지 않는다.** shell 층이 callee 의 최종 분기에 도달하지 못하게 막는 선주입(예: 유도 실패 시 조용한 기본값 대입)을 **금지**한다. shell 층의 역할은 *best-effort 유도 시도*이고, 유도 실패 시 아무것도 주입하지 않아 py 의 정책 authority 에 위임한다. 흡수(OR-true, `continue-on-error`)로 인해 verdict 가 비차단에 머무는 경우, 그 **비차단성은 명시 선언 대상**이며 "통과"로 계상할 수 없다.
- **(E4) warning-tier 게이트에 bypass 우회로를 신설하지 않는다.** bypass 의 존재 이유는 merge 를 막는 게이트를 hotfix 로 뚫는 것인데, 차단하지 못하는 게이트에 대한 우회로는 운영 이득 0 + 공격 표면 순증이다. 향후 blocking 승격(ADR-171 evidence-gated 별 carrier) 시점에 도입한다면 `determined: false` **명시 emit**(부재 금지) + workflow/runner env 에서만 수령(PR 통제면 파생 금지) + 감사 마커 + "bypass 는 판정을 대체하지 않음(원장 충족 계상 금지)"를 동반한다.

### §결정 6 — 게이트 자기무결성의 정직 천장 (over-claim 금지)

- **(H1) 마커 부재 = FAIL.** currency 게이트는 성공 시 `determined` 와 대조한 두 SHA 를 **적극 emit** 하고, 상위 workflow 는 그 **마커 부재를 FAIL 로 판정**한다. 그래야 스크립트 삭제·조기 `exit 0` 이 초록이 아니라 마커부재 FAIL 로 나타난다(fail-open → fail-closed).
- **(H2) 가변 산출물 안의 자기검사는 권위를 가질 수 없다 — 잔여 선언.** 게이트가 consumer repo 에 사본으로 배포되는 한, 그 repo 커밋 권한자는 게이트를 무력화할 수 있고 탐지는 게이트가 아니라 **PR diff 리뷰와 branch protection** 이 한다. Q1·Q2·H1 은 *사고·drift·조용한 무력화*를 막을 뿐 *권한 있는 고의 무력화*를 막지 못한다. 이 한계를 축소해 인용하거나 "완전 봉인"으로 서술하는 것을 **금지**한다.
- **(H3) blob SHA 대조는 drift 탐지이지 암호학적 진정성이 아니다.** SHA-1 chosen-prefix 충돌은 이론상 가능하나, 상류를 바꿀 수 있는 공격자는 두 값을 모두 바꾸면 되므로 충돌 공격은 최단 경로가 아니다 — **수용**하고 완화를 두지 않는다.
- **(H4) 정의역 밖은 영구 미검출임을 선언한다.** 본 ADR 의 강제 정의역이 특정 파일로 한정되는 한, 그 밖의 층(예: workflow 계층) drift 는 이 수단으로 포착되지 않는다. "검출 게이트 신설 완료"로 보고하면서 이 사실을 감추면 over-claim 이다.
- **(H5) 로그 유출면 — whitelist 출력을 정공법으로 한다.** 상위 workflow 가 `2>&1` 로 프로세스 전체 stderr 를 병합 캡처해 공개 로그·step summary 로 배달하는 구조이므로, currency 게이트의 출력은 **고정 스키마 whitelist**(판정 enum · 두 SHA · status code · error_kind)로 한정하고 예외는 enum 으로 강등한다(예외 메시지·traceback·URL 을 stderr 로 흘리지 않는다). 기존 토큰 마스킹 정규식은 best-effort 선언 상태이므로 **"유출 0"의 근거로 인용 금지** — 최후 방어선으로만 쓴다.

## 대안 (기각)

| 대안 | 기각 사유 |
|---|---|
| ADR-130 Amendment 로 흡수 | 정합성은 있으나 ADR-083→ADR-130 선례가 "새 직교축 = 새 ADR"의 이력 추적성 우위를 보인다. 축 신설을 amendment 에 숨기면 이후 인용이 2축 프레임에 묻힌다 |
| ADR-116 reconcile-then-patch 를 그대로 재사용 | 그 기법은 "보존 대상이 **구조화 스키마로 선언**돼 있음"을 선결 조건으로 갖는다(실 대상 = `project.yaml` 의 선언 필드 하나). 본 도메인의 consumer 개조는 선언 스키마 없는 organic diff 라 **직접 재사용 불가** — 패턴만 참고 대상 |
| `cp -n` 을 `cp -f` 로 전환 | no-clobber 는 consumer 로컬 수정 보호용 P1 fix 였다. 강제 덮어쓰기는 marker 실물 0개 상태에서 ADR-027 §결정 7.C wholesale 경로로 낙하해 3 repo 의 의도적 `concurrency:` 삭제를 되주입하고 loss report 의무를 발생시킨다 |
| currency 를 closure 정의 확장으로 처리 | closure 는 `dep_path.exists()` 존재 술어이고 ADR-130 §결정 3 이 그 정의역을 존재로 명시했다. 내용·버전 일치는 그 정의역 **밖**이라 확장이 아니라 축 신설이다 |
| 정본을 composite action 으로 추출해 사본 자체를 소멸 | 압력은 실재하고 적합도도 높으나 (i) CFP-2978 §5.5 확정 범위(py 1개 파일 갱신 의미론) 초과 (ii) AC-6 이 "bash 껍데기가 전파 후에도 정본과 동일 blob 으로 **존재**"를 normative 로 요구하는데 composite action 은 정의상 로컬 사본을 없앤다 (iii) 비-CI 호출면(SessionStart hook sample)이 실재해 action 화로 대체되지 않는다. **후속 후보로만 기록** |
| ADR-027 marker 표에 `.py` 행 추가로 해결 | ADR-027 은 `.py` 를 marker 정의역에서 **의도적으로 제외**했다(Amendment 9 가 "walk_plan.py 는 `.py` 라 SKIP_LIST 불요"로 명시). 이는 누락이 아니라 선언된 제외이므로 별 확장 결정이 필요하며, currency 축과는 다른 문제(경계 표기 vs 최신성 판정)다 |

## 결과

**긍정**: (i) 어떤 게이트도 볼 수 없던 결함 class 에 판정 술어가 생긴다 (ii) "전파했다"의 판정 기준이 선언·존재에서 currency 달성으로 올라가 CFP-2723 형 추정이 재발하지 않는다 (iii) exit 소비 계약이 mode 축으로 분해돼 층 간 은폐가 규범 위반으로 식별된다 (iv) 채널 제약(C1-C6)이 신규 자격증명 0 · 수신 바이트 0 으로 신뢰 기울기 역행 위험을 구조적으로 봉인한다.

**부정·비용**: (i) pin 이라는 새 선언 자산이 consumer repo 마다 생겨 유지 대상이 1종 늘어난다 (ii) Q2 가 consumer CI 에 네트워크 1콜을 추가한다(예산은 §결정 3 C2 로 확보, 실패는 R3 로 흡수) (iii) 강제 정의역이 1개 파일이라 **선언된 축과 실강제 범위 사이에 정직한 간극**이 남는다 — §결정 6 H4 로 1급 선언한다 (iv) 게이트가 사본으로 배포되는 구조적 잔여(H2)는 설계 계층에서 완화 불가다.

**후속 후보 (본 ADR 범위 밖 — 기록만)**: 미도달 12 repo 신규 배포(overlay 결손 repo 선행 시드 필요) / workflow 계층 currency / composite action 추출 재논의 / warning→blocking 승격(ADR-171 별 carrier) / consumer 측 테스트 실행 배선.

## 해소 기준

N/A — permanent policy (`is_transitional: false`). 본 ADR 은 도메인 축 정의이므로 소멸 조건을 갖지 않는다. 강제 정의역의 확대·축소는 evidence-gated amendment 대상이며, **약화 방향**(currency 판정 요건 R1-R4 완화 / UNDECIDABLE 을 PASS 로 흡수 / 채널 제약 C1-C3 해제) 발의는 ADR-058 §결정 5 에 따라 evidence 제출 의무를 진다.

## 관련 파일

- [ADR-130](ADR-130-applicability-closure-integrity.md) — 2축 SSOT, 본 ADR 이 3번째 축을 additive 신설
- [ADR-076](ADR-076-declarative-reconciliation-upgrade.md) — L128 이 기록만 한 `cp -n` 갱신 불가 잔여
- [ADR-027](ADR-027-consumer-adoption-protocol.md) — marker 경계 + wholesale loss report
- [ADR-171](ADR-171-evidence-enforceable-promotion-framework.md) — warning→blocking 승격 별 carrier (ADR-060 재제정본)
- `docs/domain-knowledge/concept/shared-script-distribution-and-drift.md` — 배포 패턴 6종 + pin 개념
- `docs/domain-knowledge/concept/vacuous-pass.md` — 실패 모드 개념 anchor
