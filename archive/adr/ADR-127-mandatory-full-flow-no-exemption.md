---
adr_number: 127
title: "정식 플로우 무조건화 — 모든 면제·단축경로 폐지 (chore 면제 / doc-only fast-path / hotfix minimal·medium / dialog skip-offer)"
status: Accepted
category: governance
date: 2026-06-20
carrier_story: CFP-2374
parent_epic: null
supersedes: [ADR-054]
amends: null
amendments: []
related_stories:
  - CFP-2374  # 본 ADR 신설 carrier
related_adrs:
  - ADR-013   # chore 면제 carrier — §강제/면제 분류 (본 ADR Amendment 8 동반: chore 면제 폐지)
  - ADR-054   # doc-only fast-path 전체 carrier — 본 ADR 이 supersede (status 전환)
  - ADR-024   # Amendment 19 동반 — §결정 6.A.10 isChoreOnly fast-pass 의 process-skip 인용 차단 (PR-level CI 안전판 자체는 보존)
  - ADR-064   # Amendment 14 동반 — §결정 3 룰 1/5 derived-default 의 skip-offer 적용 금지 명문화 (ask-trigger 와 정합)
  - ADR-071   # Amendment 11 동반 — dialog skip-offer 금지 (생략 자체를 "묻는" 것 금지, 정식이 비협상 기본값)
  - ADR-114   # Amendment 1 동반 — minimal-path-direct 의 lane spawn skip 무력화 (escalation audit-trail 만 보존, 긴급도=우선순위 표기)
  - ADR-005   # 무의미 lane N/A 표준화 — "단축(노력 절감)" 과 "대상 부재(N/A)" 구분 기준의 cross-ref anchor (무변경)
  - ADR-039   # subagent default — hotfix 도 spawn 의무 (mechanism), 본 ADR 은 process-skip 폐지 (보완 관계, 무변경)
  - ADR-026   # Amendment 4 §결정 6 isPostMergeFix — cross-repo land_order safe-defect 정정 PR-level CI 안전판 (보존, process-skip 인용 차단만)
  - ADR-058   # §결정 5 sunset_justification — 본 ADR 은 강화(ratchet) 방향이라 약화 evidence-gate 불요
  - ADR-060   # evidence-enforceable framework — hotfix-bypass:* family 의 warning→blocking 점진 승격 (§결정 9 분석 기반)
related_files:
  - archive/adr/ADR-013-codeforge-family-dogfood-out-policy.md
  - archive/adr/ADR-054-doc-only-story-fast-path.md
  - archive/adr/ADR-024-story-scoped-branch-policy.md
  - archive/adr/ADR-064-decision-principle-mandate.md
  - archive/adr/ADR-071-orchestrator-user-dialog-convergence.md
  - archive/adr/ADR-114-minimal-path-direct-invocation-protocol.md
  - skills/story-cutoff-classification/SKILL.md
  - skills/story-epic-flow-preflight/SKILL.md
  - skills/user-dialog-mode/SKILL.md
  - skills/deputy-mandate/SKILL.md
  - docs/hotfix-playbook.md
  - docs/orchestrator-playbook.md
  - docs/consumer-guide.md
  - docs/inter-plugin-contracts/label-registry-v2.md
  - docs/evidence-checks-registry.yaml
  - templates/github-workflows/phase-gate-mergeable.yml
  - CONTRIBUTING.md
  - CLAUDE.md
  - .claude-plugin/plugin.json
mechanical_enforcement_actions: []   # declaration-only — 본 ADR 은 정식성 강화(ratchet) 방향. 기존 mechanical 게이트(phase-gate-mergeable.yml)는 강화 보존이라 신규 lint 신설 0. pattern_count >= 2 재발 시 follow-up CFP MUST promote (ADR-082 §결정 6 / ADR-084 precedent).
is_transitional: false
---

# ADR-127: 정식 플로우 무조건화 — 모든 면제·단축경로 폐지

## 상태

Accepted (2026-06-20 KST, CFP-2374 carrier). `is_transitional: false` — 영구 정책. 본 ADR 은 **정식성 강화(ratchet) 방향** — 기존 면제·단축경로를 제거해 정식 풀 플로우를 비협상 기본값으로 고정한다. 약화 방향이 아니므로 ADR-058 §결정 5 sunset_justification 의무 비대상 (강화 방향).

## 본질 선언

> **codeforge 의 모든 면제·단축경로를 폐지한다. 어떤 변경이든 — 오타·lint·버전범프·링크수정 같은 순수 기계적 변경, 운영 장애 긴급 대응까지 — 정식 풀 플로우(요구사항 → 요구사항리뷰 → 설계 → 설계리뷰 → 구현 → 구현리뷰 → 통합테스트 → 보안테스트 → 배포 → 배포리뷰)를 무조건 거친다. "생략하자 / 간소화하자 / 빠르게 가자" 는 선택지 자체가 사라진다.**

## 컨텍스트

### 사용자 directive (Story §1 = Issue #2374, 2026-06-20 KST)

사용자 원문 취지: "사용하다보니 codeforge 가 자꾸 '생략하자' 선택지를 주는데, 무조건 정식으로 가야 한다. 그런 선택지 없이 무조건 정식으로 가게 하라." Orchestrator 가 두 안 제시:
- **Option 1** — skip-offer(런타임 생략 제안)만 폐지하고 면제·단축 경로 자체는 보존.
- **Option 2** — 면제·단축경로 전부 폐지 (오타·lint 같은 순수 기계적 변경도 정식 풀 플로우, hotfix 긴급경로까지 폐지).

사용자가 비용(사소·긴급 변경의 오버헤드 증가)을 고지받고 **Option 2 를 명시 선택**. 본 ADR = Option 2 의 결정 기록.

### 폐지 대상 4 carrier (실측 검증된 ADR 귀속)

매 carrier 의 실제 소유 ADR 을 `Read`/`Grep` 으로 추적 검증했다 (ADR-119 검증-후-단언).

| # | 폐지 대상 | 검증된 carrier(SSOT) | 처리 |
|---|---|---|---|
| 1 | **chore 면제** (Story 없이 commit) | ADR-013 §강제/면제 분류 + ADR-054 §결정 1 표 chore row + `story-cutoff-classification` SKILL.md L29-36 (+ consumer overlay 확장채널 `story_cutoff.additional_exempt_categories[]`) | ADR-013 Amendment 8 (chore 분류 폐지) + 본 ADR §결정 1 |
| 2 | **doc-only fast-path** (구현 lane 생략, 단일 PR) | **ADR-054 전체** + `story-cutoff-classification` SKILL L22-27 + `story-epic-flow-preflight` SKILL L33 + `deputy-mandate` SKILL codify-Story clause | ADR-054 **supersede** (status 전환) + 본 ADR §결정 2 |
| 3 | **hotfix minimal/medium path** (설계·구현 리뷰·보안·성능게이트·deputy 생략) | `docs/hotfix-playbook.md` (carrier) + **ADR-114** minimal-path-direct (escalation fallback 성격, lane spawn skip 본질 보유) | hotfix-playbook gut + ADR-114 Amendment 1 (lane-skip 무력화) + 본 ADR §결정 3 |
| 4 | **dialog skip-offer** (런타임에 "생략/간소화/빠르게?" 를 사용자 선택지로 제시) | **ADR-071 §결정 5/20** + **ADR-064 §결정 3 룰 1/5** + `user-dialog-mode` SKILL §결정 5 + playbook §3.0.5 / §3.14 | ADR-071 Amendment 11 + ADR-064 Amendment 14 + 본 ADR §결정 4 |

### PR-level CI fast-pass source 의 처리 — 좁은 deadlock-resolver 로 재설계 (Codex P0 수용)

초기 설계 판단은 "phase-gate-mergeable.yml 의 `isChoreOnly`/`isDocOnly`/`isPostMergeFix` fast-pass source 는 PR-level CI mergeability 안전판이므로 전부 보존"이었다. Codex adversarial 검증(2026-06-20)이 이 결론의 결함을 실측으로 지적했고, 대조 검증(ADR-119) 결과 **수용**한다:

- **`isChoreOnly` 의 성공 조건 = `noStoryBinding`** (실측 — phase-gate-mergeable.yml L405-406: `isChoreOnly = noStoryBinding`, 조건 (b) = Story 미연결). 즉 isChoreOnly 는 "Story 가 없어야" 성공한다. 그런데 §결정 1 이 "모든 변경 = Story 의무"로 만들면 chore PR 도 Story 를 갖게 되어 조건 (b) false → isChoreOnly 자연 발동 불가. 즉 **ADR-127 발효 후 isChoreOnly 는 사실상 dead path** (Story 없는 PR 자체가 사라짐). "보존"이 아니라 "더 이상 발동 안 됨".
- **`isDocOnly` allowlist = `.github/`/`templates/`/`scripts/`/`.claude/_overlay/`/`scope_manifests/` 까지 success** (실측 — L183-200). 이건 단순 머지 안전판이 아니라 ADR-054 단일-PR 논리(거버넌스 변경을 구현 lane 없이 통과)의 CI 재주입 = **살아있는 exemption carrier**. doc-only fast-path 를 폐지하면서 isDocOnly 를 그대로 두면 정책과 기계 집행이 충돌한다.

**올바른 경계 (수정된 판단)**: 정당한 보존 가치 = "정식 full-flow 를 거친 PR 이 **phase 라벨 mismatch 만**으로 영구 `action_required` 되는 deadlock 방지" (CFP-1845 실측 cascade). 폐지 대상 = "Story 없음 / doc-only diff" 를 **성공 근거로 삼는** process-derived fast-pass. 따라서:

- `isChoreOnly` / `isDocOnly` = process-derived fast-pass 로서 **폐지**(또는 자연 dead). 성공 근거를 "Story 없음/문서 diff" 에서 제거.
- 대체 = **좁은 deadlock-resolver predicate**: "full-flow 증거 존재(Story binding + 해당 gate 라벨 부착) **AND** phase 라벨만 mismatch" 인 경우에만 unblock. "Story 없음" 을 성공 근거로 삼지 않음. (실 구현 = 별도 follow-up CFP — 본 ADR scope 는 결정 기록, mechanical wire 는 Wave 2.)
- `isPostMergeFix` = ADR-026 §결정 6 의 cross-repo land_order safe-defect 정정으로 byte-equivalence·보안 non-touch 양면 검증을 거치는 PR-level CI 안전판 — **보존**하되, 운영 장애 hotfix 와 혼동 차단(§E 배너). 이건 process 생략이 아니라 land_order 정정 한정.

CFP-1845 anti-pattern 재발(branch protection 손작업 우회 + enforce_admins:true 위배 = 보안 약화) 차단은 **deadlock-resolver 대체 predicate** 가 보장한다 — fast-pass 를 단순 삭제하지 않고 좁은 형태로 대체하는 이유.

## 결정

### §결정 1 — chore 면제 폐지 (모든 변경은 Story 작성 의무)

오타·문법·줄바꿈·마크다운 형식·링크수정·lint 자동fix·dependency lock·버전범프·README 단순 문구 수정 — 종전 `story-cutoff-classification` SKILL §면제 대상(L29-36) 으로 Story 없이 commit 하던 모든 변경은 **Story file 작성 의무 대상으로 승격**한다. `Story 면제 사유:` commit body marker 채널 폐지.

- ADR-013 의 강제/면제 2분법 → **강제 단일 분류** (Amendment 8). "면제 대상 (chore commit OK)" 카테고리 삭제.
- `story-cutoff-classification` SKILL §면제 대상 섹션 = 삭제 (구현 lane 편집 spec §A 참조).
- **consumer overlay 확장채널 폐지**: `story_cutoff.additional_exempt_categories[]` = consumer 가 도메인 특화 면제를 추가하던 채널. 본 결정으로 **schema 에서 제거**한다 (구현 lane spec §G). overlay invariant("정책 확장만 가능, 축소 불가")와의 정합 = §결정 6 에서 해소.

### §결정 2 — doc-only fast-path 폐지 (구현 lane 생략 없음, Phase 1/2 분리 무조건)

ADR-054 가 정의한 "doc-only fast-path" (SSOT 문서 변경 + src/tests 무변경 시 → 요구사항 → 설계 → 경량 설계리뷰 → 단일 PR, 구현 lane skip) 경로를 **폐지**한다. ADR-054 = `status: Superseded by ADR-127` 전환 (본문 byte 무변경, historical 보존 — redirect 배너만).

- 모든 Story = full 10 lane + Phase 1 PR(§1-7) + Phase 2 PR(§8-11) 분리 (CLAUDE.md 핵심 흐름 정합). "1 Story = 1 PR(단일)" 형태 폐지.
- "경량 설계리뷰"(문서 정합성만 검증, code quality/test 섹션 skip) 폐지 → 정식 설계리뷰 무조건.
- ADR-054 §결정 6 (Amendment 1 declarative seed fast-path) / §결정 7 (Amendment 2 Codex 6-touchpoint 면제) 도 함께 무효 (supersede 에 포함).
- **단, doc-only Story 의 "별도 change-plan 면제"는 별개 — 보존**. ADR-013 dogfood-out 정합상 ADR 가 §3 도입 설계 SSOT 역할을 충족하는 경우 별도 change-plan doc 면제는 "lane 생략"이 아니라 "산출물 SSOT 통합"이므로 정식 플로우 폐지 대상이 아니다 (본 Story 자체가 그 사례 — change-plan 없이 ADR-127 이 §3 설계 SSOT). 이건 §결정 5 의 "N/A vs 단축" 구분 적용 결과.

### §결정 3 — hotfix minimal/medium path 폐지 + ADR-114 lane-skip 무력화

운영 장애 긴급 대응 시에도 정식 풀 플로우를 무조건 거친다. 긴급도는 **우선순위 표기**(라벨 / PR title)로만 표현하고 **lane 생략은 0** 이다.

1. **hotfix-playbook Minimal Path / Medium Path 폐지** — `docs/hotfix-playbook.md` §1(Minimal: 계획·설계리뷰·구현리뷰 생략·성능게이트 생략·Claude peer 보안 생략) / §2(Medium: deputy 생략·설계리뷰 생략·Codex 구현리뷰 생략) = gut. 두 경로의 lane-skip 본질 폐지.
2. **ADR-114 minimal-path-direct = lane spawn skip 무력화** (Amendment 1). ADR-114 는 "full-lane default + 사용자 directive 필수 escalation fallback (FIX 3회 + ESCALATE 후)" 성격이라 Orchestrator 자발적 "생략 제안"과 다르지만, **lane spawn skip + Orchestrator inline write** 본질을 가지므로 본 directive 와 충돌한다. ADR-114 §결정 2(절차 3 "lane spawn skip + Orchestrator inline write") = 무효. **단 escalation audit-trail 가치는 보존** — FIX 3회+ESCALATE 시점의 Story §10/§14 marker 기록 의무는 유지하되, 그 다음 행동은 "lane 생략 inline write"가 아니라 "정식 lane 재진입 + 긴급 우선순위 표기"로 재정의.
3. **`BYPASS_VERSION_BUMP=1` env 우회 폐지** (Codex P1 수용). `CONTRIBUTING.md` L74-76 `### Bypass` 의 "긴급 hotfix 시 `BYPASS_VERSION_BUMP=1` + `BYPASS_VERSION_BUMP_REASON` env 로 버전 bump 우회 (audit trail 보존). hotfix-playbook 정합" = hotfix 긴급경로의 일부 → 폐지. 버전 bump 는 정식 플로우 안에서 무조건 수행 (ADR-037 self-app). 구현 spec §L 참조.
4. **운영 긴급 대응 대체 절차** (§결정 안 답): hotfix 폐지 후 prod 장애 시 —
   - branch protection PR-gate 무변경 (`enforce_admins:true` / required status checks 6-tuple 그대로). 모든 변경은 feature branch + PR 경유.
   - 긴급 Story = 정식 10 lane 전부 거침. 긴급도는 `severity:critical` 라벨 + PR title 우선순위 표기로만 신호 (lane 생략 0).
   - **lane-skip 없는 복구시간 단축 장치는 허용** (Codex P2 수용 — "증거 축약 금지, 대기시간 축약만 허용" 원칙): ① 긴급 시 정식 lane 의 **병렬 dispatch 우선** + check timeout 상한 적용으로 wall-clock 단축 (lane 생략 0, 증거 0 축약) ② revert-only 변경도 정식 full-flow (단 §결정 5 N/A 3축 적용 — revert 가 downstream contract 무변경이면 일부 lane 자연 N/A 가능) ③ on-call reviewer 선지정으로 리뷰 lane 대기 단축. 이 장치들은 **증거(lane 산출물)를 축약하지 않고 대기시간만 줄이므로** 면제경로 재도입이 아니다.
   - **트레이드오프 정직 고지**: 위 장치를 적용해도 prod 장애 복구가 정식 플로우 소요만큼 지연될 수 있다(특히 보안테스트·통합테스트 lane). 사용자가 이 비용을 명시 수용했다 (Story §1). 본 ADR 은 복구 지연을 "정식성 우선"의 명시적 대가로 받아들인다 — **lane 을 생략하는** 별도 긴급 우회는 두지 않는다 (lane-skip 우회 = 면제경로 재도입 = directive 위반). 대기시간 축약(병렬/timeout/on-call)만 허용.

### §결정 4 — dialog skip-offer 금지 (생략을 "묻는" 것 자체 금지, 정식이 비협상 기본값)

런타임에 Orchestrator 가 사용자에게 "생략할까요 / 간소화할까요 / 빠르게 갈까요 / 경량으로 갈까요" 를 **선택지로 제시하는 것을 금지**한다. 정식 풀 플로우는 비협상(non-negotiable) 기본값이므로, 생략 여부는 애초에 결정 분기가 아니다 → `AskUserQuestion` 발화 대상이 아니다.

- **ADR-071 Amendment 11**: `user-dialog-mode` SKILL §결정 5 ask-trigger 3종(① 요구 애매 ② 진짜 가치 trade-off ③ 비가역·고비용)과 정합 — "생략/단축"은 ask-trigger ② 가치 trade-off 로 오분류될 여지가 있으나, **정식이 비협상 기본값이므로 생략은 default 가 자명(=항상 정식)** → ask-trigger 미해당 → 묻지 않고 정식 진행. CFP-2371(ask-trigger 3종 한정, ADR-071 Amendment 10) 과 **충돌 없음** — CFP-2371 은 질문 빈도(over-asking 제거), 본 ADR 은 skip-offer 라는 특정 질문 종류의 PATH 폐지. 둘 다 "불필요한 멈춤 제거" 방향으로 정합.
- **ADR-064 Amendment 14**: §결정 3 룰 1(derived default) / 룰 5(`AskUserQuestion` 범위 제한 = 가치판단·미공개컨텍스트 2종 한정) 에 명문 추가 — "process 생략/단축 여부"는 derived default 가 **항상 정식**으로 자명하므로 `AskUserQuestion` 발화 금지. §결정 2 forbid-list 어휘(`단계적`/`일단`/`가벼운`/`quick win`/`minimal viable`)가 이미 결정 제안 menu 에서 이들을 차단하고 있던 것과 정합 강화.
- playbook §3.0.5 "구현 실행 방식 선택지 발견 시 Subagent-Driven 자동 선택"(CFP-358/374) 정합 — 스킬이 생략 선택지를 제시하더라도 본 §결정 4 가 우선, 자동으로 정식 측 채택.

### §결정 5 — "단축(노력 절감)" vs "대상 부재(N/A)" 구분 기준 (ADR-005 cross-ref)

정식 플로우 무조건화는 **"lane 의 노력을 절감하려는 skip"** 만 폐지한다. **"lane 이 검사할 실제 산출물 target 이 부재해서 자연 N/A 가 되는 것"** 은 폐지 대상이 아니다 — N/A 는 단축이 아니라 정식 분류의 정상 결과다 (ADR-005 §결정 1/3 정합).

**구분 기준 (3축 AND — N/A 자격은 3축 모두 만족 시에만, Codex P2 강화 수용)**:

초기 기준은 "lane 이 검사할 target 파일이 존재하는가" 단일 축이었으나, Codex 가 악용 가능성을 지적했다 — "현재 PR 에 실행 target 파일이 없으니 N/A" 는 너무 약하다 (workflow/template/script/contract/label/test 삭제는 런타임 산출물 없이도 downstream obligation 을 바꾼다). 대조 검증 후 **3축 AND** 로 강화:

해당 lane 의 N/A 판정은 다음 3축을 **모두** 만족할 때만 정식 분류 N/A 로 허용한다. 하나라도 위반(YES)이면 N/A 금지 → 정식 lane 진입.

| 축 | N/A 자격 조건 | 위반 시 |
|---|---|---|
| **축 1 — 산출물 부재** | 해당 lane 이 실행·검증할 실제 산출물 target 이 없음 (예: wrapper-self governance Story 의 통합테스트 lane = runtime behavior 부재) | target 있는데 노력 절감 skip = 폐지 (정식 진입) |
| **축 2 — downstream 무변경** | 본 변경이 downstream contract / automation / security posture 를 바꾸지 않음 | contract/workflow/security 변경 = 정식 진입 (산출물 파일이 "없어 보여도") |
| **축 3 — 미래 의무 무선결** | 삭제 / 문서화 / seed 선언이 미래 lane 의무를 선결정하지 않음 (declarative seed 로 후속 wire 를 예약하는 형태 = 위반) | 미래 lane 의무 선결 = 정식 진입 |

3축 AND 만족 시 → lane 진입은 하되 ADR-005 §결정 1 표기로 `N/A — <사유>` + 면제분류 enum + §11 회고 N/A 명시 (자동 inheritance 금지). 1축이라도 위반 → 정식 lane 무조건 진입.

- **본 Story(CFP-2374) 자체 적용 예시**: src 0 인 governance codify Story 지만 — 설계 lane = ADR/skill/playbook 편집 = real target 있음(정식). 구현 lane = skill/playbook/CLAUDE.md/plugin.json 편집 = real target 있음(정식, doc-only 생략 대상 아님). 통합테스트 lane = wrapper-self runtime behavior 부재 = N/A(정식 분류). 보안테스트 = trust boundary 변경 0 = N/A(plugin-meta-na). 배포/배포리뷰 = wrapper-self deploy target 부재 = N/A.
- **악용 차단**: "target 없다"고 우겨서 lane 생략하는 회피를 막기 위해 — N/A 판정은 ADR-005 §결정 3 의 §11 회고 명시 의무 + per-Story 재실시(자동 inheritance 금지) 를 그대로 상속. lane PL 이 N/A 사유를 산출물 부재로 입증해야 하며, 입증 실패 시 정식 진입(모호 시 정식 측 분류 — 안전 방향).

### §결정 6 — consumer overlay 면제 확장채널 폐지 + overlay invariant 정합

`story_cutoff.additional_exempt_categories[]` (consumer 가 면제 카테고리를 도메인별로 추가하던 채널) 을 폐지한다. 이는 overlay invariant("overlay 는 정책을 확장만 가능, 축소 불가")와 **정합한다** — 본 결정은:

- overlay 가 **정책을 약화(면제 추가 = 강제 정책 축소)** 하던 채널을 제거하는 것이므로, "overlay 는 강제를 축소 불가"라는 invariant 의 **강화**다. 면제 추가 = 강제 범위 축소이므로 애초에 overlay 가 해서는 안 되던 영역이었다 (story-cutoff SKILL L47 의 "강제 항목 축소 불허" 와 모순되게 면제 추가를 허용하던 drift 를 해소).
- consumer 는 여전히 정책을 **확장**(더 엄격하게 — 강제 추가)할 수 있다. 면제 추가만 불가.

### §결정 7 — 자기참조 (본 Story 의 규칙 적용 시점)

본 Story(CFP-2374)는 **구 규칙 하에서 진행**되며, 새 규칙(정식 무조건화)은 본 PR merge 후 발효한다. 따라서:

- 본 Story 의 요구사항 lane fan-out(DomainAgent/Analyst/Researcher 4-agent 병렬)을 **실행하지 않은 근거**: 사용자 directive 가 명확한 governance codify(외부지식·도메인 해석 의존 0, 결정 scope 가 사용자 발화로 완결)이므로, 요구사항 재조사 fan-out 은 검사연극(ADR-119 §결정 6)에 해당 → 면제. 이는 §결정 5 의 "target 부재 N/A"와 정합 (요구사항 lane 의 재해석 target 부재).
- deputy spawn 0: `deputy-mandate` 매트릭스 적용 결과 6 permanent deputy 전부 무-target N/A (보안/데이터/인프라/모듈/API/테스트계약 설계결정 0) → chief-author 단독. 이 역시 §결정 5 N/A(단축 아님).

### §결정 8 — 인접 carrier scope 경계 (Codex P1 실측 분류 — 폐지 / 보존 / 분리)

Codex adversarial 검증이 인접 carrier 5종을 추가 식별했다. 각 carrier 를 실측 후 directive 정합으로 분류한다 (검사연극·scope 폭발 회피 — ADR-119 §결정 9 + ADR-064 §결정 5 CFP scope unitary).

| carrier | 실측 성격 | 분류 | 근거 |
|---|---|---|---|
| **`BYPASS_VERSION_BUMP=1`** (CONTRIBUTING.md L76) | hotfix 긴급 시 버전 bump 우회, hotfix-playbook 정합 명시 | **폐지** (§결정 3.3) | hotfix 긴급경로의 일부 — directive 직접 대상 |
| **`fallback:manual` / `bootstrap.fallback_mode`** (consumer-guide L275-303) | story-init **자동화 outage** 시 수동 Story 생성 경로 | **보존** | lane skip 아님 — 자동화 장애 시 degraded-mode 가용성 장치. 폐지하면 outage 시 작업 자체 불가. 단 manual fallback 도 정식 lane 전부 거침을 명시(§G) |
| **`isEpicLabel`** (phase-gate fast-pass) | Epic close / doc PR 의 phase-mismatch auto-success | **보존** | Epic close PR 의 phase-label deadlock 방지 — §결정 5 N/A(검증 위험 구조적 0: Epic close = 산출물 aggregate, 신규 코드 0). process 생략 아님 |
| **`isSiblingPr`** (phase-gate fast-pass) | wrapper Story 가 PASS 한 설계리뷰가 sibling repo mirror PR 을 보증 | **보존** | sibling sync 거버넌스 메커니즘 — wrapper PR 이 정식 full-flow 를 이미 거쳤고 sibling 은 byte-mirror. 중복 review 회피이지 lane 생략 아님. 단 sibling PR 이 wrapper PASS 증거 없이 단독 발동 불가(현 구현 invariant 유지) |
| **`hotfix-bypass:*` label family** (label-registry-v2 + evidence-checks-registry) | 개별 evidence-check 1건의 audit-trailed 우회 (단계 통째 생략 아님) | **§결정 9 (blocking-tier in-scope / warning-tier 제외)** | 설계리뷰 FIX iter 2 사용자 결정 = blocking형 in-scope. 실측 결과 required-6-tuple-skip blocking-tier = **0건**(required check 가 bypass channel 미설계) → 폐지 대상 0 + invariant 명문화(required check bypass 신설 금지). warning-tier 제외(merge 무차단 no-op). 상세 §결정 9 |

**scope 경계 선언**: 본 ADR 의 폐지 대상 = **process-level lane/Story 생략 경로** (chore 면제 / doc-only fast-path / hotfix lane-skip / dialog skip-offer / version-bump bypass) + 그 mechanical carrier(process-derived fast-pass → deadlock-resolver 재설계, §K) + **required-6-tuple-skip blocking-tier hotfix-bypass(실측 0건 → invariant 명문화, §결정 9/§M)**. warning-tier hotfix-bypass = 제외(merge 무차단 no-op).

### §결정 9 — hotfix-bypass:* family 처리 (blocking-tier in-scope / warning-tier 제외 — 실측 결론)

설계리뷰 FIX iter 2 에서 사용자 결정 = **차단(blocking)형 hotfix-bypass 라벨 폐지 in-scope, 경고(warning)형 제외**. 실측 분류 후 결론한다 (ADR-119 검증-후-단언 — 추측 금지, check 스크립트가 그 라벨로 required check 를 skip 시키는지 실측).

**9.0 wrapper 단일 범위 (실측 확인)**: lane 8 repo = archived/동결 (CFP-2178 S6 — CLAUDE.md L78 "활성 관리 = wrapper 단일", branch-protection-audit 정합). 따라서 hotfix-bypass 폐지 = **wrapper repo 단일** 편집. 8-repo mirror 편집 불요.

**9.1 blocking vs warning 분류 기준 (실측 정의)**:

- **blocking-tier** = 해당 hotfix-bypass 라벨이 **merge 를 실제 막는 required 6-tuple check** (SSOT: `["phase-gate-mergeable","invariant-check","doc frontmatter schema (CFP-28 — strict)","doc section schema (CFP-28 — strict)","check-gate","Verify deploy lane presence"]`) 를 fail→pass/skip 전환시키는 경우.
- **warning-tier** = required 6-tuple 에 미등록인 check 의 우회 (advisory — merge 무차단). ADR-060 framework 의 `warning` + `blocking-on-pr` tier 포함 (둘 다 branch protection required_status_checks 6-tuple 미등록 = enforce_admins 로 실제 merge 차단 안 함).

**9.2 실측 결과 — required-6-tuple-skip blocking-tier hotfix-bypass = 0건**:

required 6-tuple 의 5 workflow 를 전수 grep 한 결과 **어느 것도 hotfix-bypass 라벨을 읽지 않는다**:

| required 6-tuple check | workflow | hotfix-bypass 참조 | 결과 |
|---|---|---|---|
| phase-gate-mergeable (+ check-gate job) | `.github/workflows/phase-gate-mergeable.yml` | **0건** | bypass channel 없음 (evidence-registry entry 도 bypass 필드 0) |
| invariant-check | `.github/workflows/invariant-check.yml` | **0건** | bypass channel 없음 |
| doc frontmatter schema / doc section schema | `.github/workflows/lint.yml` | **0건** | bypass channel 없음 |
| doc section schema (Story) | `.github/workflows/story-section-schema.yml` | **0건** | bypass channel 없음 |
| Verify deploy lane presence | `.github/workflows/deploy-lane-presence.yml` | **0건** | bypass channel 없음 |

→ **merge 를 실제 막는 required check 를 hotfix-bypass 로 우회하는 라벨 = 0건** (verified-via 5 workflow 전수 grep, 2026-06-20).

**9.3 warning-tier 가 압도적 (제외 확정)**: hotfix-bypass 를 읽는 workflow ~35종은 전부 required 6-tuple **외부**다 — 대다수 `continue-on-error: true`(advisory), 일부(`worktree-first-pre-checkout`/`worktree-first-pre-commit-main-block`/`wrapper-managed-block` 등)는 `continue-on-error: false` + 자기 주석 "blocking-on-pr / required check" 표방이나 **branch protection 6-tuple 미등록** = enforce_admins 로 실제 merge 차단 안 함(빨간 X 표시는 뜨나 admin/non-required 우회 가능). evidence-registry tier 분포 = `warning` 압도적 다수 + `blocking-on-pr` 소수(6-tuple 미등록). **warning-tier(+ 6-tuple 미등록 blocking-on-pr) bypass 폐지는 merge 무차단이라 no-op — 폐지 자체가 무의미(검사연극).** → 제외 확정 (사용자 결정 정합).

**9.4 결론 (실측 기반)**:

- **blocking-tier(required-6-tuple-skip) hotfix-bypass = 0건** → 폐지할 대상이 **물리적으로 없음**. required 6-tuple 은 애초에 hotfix-bypass escape valve 를 두지 않은 설계(invariant-check / phase-gate-mergeable = bypass channel 0). 즉 "차단형 우회 폐지" 의 목표 상태(required check 우회 0)는 **이미 달성돼 있다**.
- **warning-tier(+ 6-tuple 미등록 blocking-on-pr) = 제외** (사용자 결정 + §9.3 no-op 분석). 폐지해도 merge 무차단이라 효과 0, escape valve 만 소멸(역설). 검사연극 회피.
- **본 Story 처리** = ① 본 §결정 9 실측 분류를 ADR 본문에 명문화 ② label-registry-v2 + ADR-024 §결정 6.A 에 "required-6-tuple-skip blocking-tier hotfix-bypass = 0건 실측 (required check 는 bypass channel 미설계 — 이미 무우회), warning-tier 제외(merge 무차단 no-op)" Amendment cross-ref(§M) ③ 대량 label 제거 0 (폐지 대상 0건이므로 — 검사연극 회피).
- **invariant 명문화 (강화 ratchet)**: "required 6-tuple check 에는 hotfix-bypass escape valve 신설 금지" 를 ADR-024 §결정 6.A 에 명문화 — 현 상태(bypass 0)를 영구 invariant 로 고정(미래에 누가 required check 에 bypass channel 추가하는 것 차단). 이게 "차단형 우회 0" directive 의 실질 이행 (대상 0건이나 미래 재발 차단으로 강화).

**9.5 escape-valve 대체 / 비용 (정직 고지, §비용 반영)**: required 6-tuple 은 이미 escape valve(hotfix-bypass)가 없으므로 — required check 실패 시 정식 처리 = (i) 실패가 본 PR 책임이면 근본 수정 in-scope (ii) 검사 자체가 버그면 검사 수정 (iii) 무관 pre-existing 이면 그 검사를 별도 정식 Story 로 수정. **우회 label 0** (이미 그러함). 운영 비용 = 무관 pre-existing required check 실패도 PR 을 막는다 — 단 required 6-tuple 은 phase/schema/invariant 정합 검사라 pre-existing 실패가 드물고, 발생 시 (iii) 정식 수정 경로. **이 영역은 deadlock-resolver(§K)와 disjoint** — §K 는 phase-label mismatch 만 푸는 것이고(라벨 정합), §결정 9 는 required check 자체 실패(schema/invariant)를 다룬다. 혼동 금지.

## 적용 범위 (구현 lane 편집 대상)

본 ADR 이 §3 도입 설계 SSOT 이므로 별도 change-plan doc 면제 (ADR-013 dogfood-out 정합 — §결정 2 단서). 아래는 구현 lane 이 편집할 **비-ADR 파일 + 정확한 변경 내용** enumerate.

### §A — `skills/story-cutoff-classification/SKILL.md`
- **L29-36 "## 면제 대상 (chore commit OK)" 섹션 전체 삭제** + L36 `Story 면제 사유:` marker 문장 삭제. → "모든 변경은 Story 작성 의무 (chore 면제 폐지 — ADR-127 §결정 1)" 1-2줄로 교체.
- **L22-27 "## doc-only fast-path 대상 (ADR-054)" 섹션 전체 삭제** → "모든 Story = full 10 lane + Phase 1/2 분리 무조건 (doc-only fast-path 폐지 — ADR-127 §결정 2)" 로 교체.
- **L47 consumer overlay 단락** `story_cutoff.additional_exempt_categories[]` 언급 삭제 → "consumer overlay 는 면제 추가 불가 (강제 확장만 — ADR-127 §결정 6)" 로 교체.
- description frontmatter "강제 대상 / doc-only fast-path / 면제 대상 3종 분류" → "모든 변경 Story 작성 의무 (면제·단축 0)" 로 갱신.

### §B — `skills/story-epic-flow-preflight/SKILL.md`
- **L33 "doc-only fast-path (ADR-054 적용 시): 1 Story = 1 PR" 단락 삭제** → "모든 Story = Phase 1 PR + Phase 2 PR (doc-only 단일 PR 폐지 — ADR-127 §결정 2)" 로 교체.
- **L21 "Fast-path 없음 (단 Hotfix 경로 2종은 예외...)" 문장**에서 hotfix 예외 절 삭제 → "Fast-path 없음. Hotfix 긴급경로도 폐지 (ADR-127 §결정 3) — 긴급도는 우선순위 표기만, lane 생략 0" 로 교체.

### §C — `skills/user-dialog-mode/SKILL.md`
- **§결정 5 결정 트리 표(L36-46) 에 row 추가**: "process 생략/단축 여부" → "derived default = 항상 정식, `AskUserQuestion` 금지 (ADR-127 §결정 4)". ask-trigger 3종 설명 직후에 "skip-offer 는 ask-trigger 비해당 — 정식이 비협상 기본값" 1줄 명시.

### §D — `skills/deputy-mandate/SKILL.md`
- **L15 "doc-only fast-path mechanism codify Story 진입 시" 호출 시점 단락** = doc-only fast-path 어휘 제거 → "governance codify Story 진입 시 (실 설계 결정 0)" 로 일반화. deputy 매트릭스 자체는 무변경 (N/A 판정 로직은 §결정 5 와 정합 보존).

### §E — `docs/hotfix-playbook.md`
- **§1 Minimal Path / §2 Medium Path 폐지** — 두 섹션을 `[POLICY-RETIRED — ADR-127 §결정 3]` 배너 + "정식 10 lane 무조건. 긴급도는 우선순위 표기만, lane 생략 0" 안내로 교체 (본문 historical 보존 방식 = redirect 배너, 통째 삭제 아님).
- **§3 사후 감사 / §6 cross-repo land_order post-merge-fix 경로** = 보존 검토 — post-merge-fix(§6) 는 ADR-026 §결정 6 의 PR-level safe-defect 정정으로 byte-equivalence·보안 non-touch 양면 검증을 거치므로 lane-skip 이 아닌 CI-level 안전판(§결정 5 보존군). 단 "운영 장애 adrenaline 정정"이 아닌 cross-repo land_order 정정 한정임을 재확인하고, 운영 장애 hotfix 경로로 오인용되지 않도록 §6 모두(冒頭)에 "본 경로는 운영 장애 hotfix 아님 (그 경로는 ADR-127 §결정 3 으로 폐지)" 배너 추가.
- 활성화 trigger(§5) = "dormant — 운영 장애 시에도 정식 플로우" 로 갱신.

### §F — `docs/orchestrator-playbook.md`
- **§3.0.8 cross-ref L443** 실측 원문(verbatim) = `**Hotfix scope**: [hotfix-playbook.md](hotfix-playbook.md) (exception 없음 — 사용자 verbatim "무조건")`. → `**Hotfix scope**: [hotfix-playbook.md](hotfix-playbook.md) (lane-skip 폐지 — ADR-127 §결정 3 / spawn 의무는 ADR-039 유지, lane 생략 0)` 로 갱신. (기존 "exception 없음 무조건" = spawn 무조건 의미였고, ADR-127 후 lane 도 무조건 = 의미 강화.)
- **§3.0.5** (구현 실행 방식 — Subagent-Driven 자동 선택, L405 영역) = dialog skip-offer 금지 1줄 cross-ref 추가 (ADR-127 §결정 4 — 스킬이 생략/경량 선택지 제시해도 자동 정식 채택).
- **§3.14** = dialog skip-offer 금지 cross-ref + doc-only/chore 분류 절차 갱신 (3-way 분류 chore/doc-only/full-lane → full-lane 단일 분류 + N/A 3축 판정(§결정 5)).

### §G — `docs/consumer-guide.md`
- `story_cutoff.additional_exempt_categories[]` 관련 면제 확장 설명(있는 경우) 삭제 → "consumer 면제 추가 불가 (ADR-127 §결정 6)" 로 교체.
- hotfix minimal/medium 언급(L1996 등) = "운영 장애 시에도 정식 플로우 (ADR-127 §결정 3)" 로 갱신.
- **`fallback:manual` / `bootstrap.fallback_mode` (L275-303) = 보존** (§결정 8 — 자동화 outage degraded-mode 가용성 장치, lane skip 아님). 단 "manual fallback Story 도 정식 10 lane 전부 거침 — 수동은 Story **생성** 경로만 대체, lane 생략 0 (ADR-127 §결정 8)" 1줄 명시 추가.
- **§5 Migration Epic tiered template delta 면제표(L2493-2497) 검토**: 이는 Migration Epic 의 §section 작성 면제(문서 구조 수준)이지 lane 생략이 아님 → §결정 5 N/A 구분상 "산출물 target 부재 N/A" 영역. **보존하되** N/A 표기 의무(ADR-005) 정합 1줄 추가 (면제 ≠ 단축).
- `project-config-schema.md` 의 `story_cutoff.additional_exempt_categories` field schema = 제거 (deprecated 배너).

### §H — `CLAUDE.md`
- **"## 핵심 흐름"의 "문서만 바뀌는 변경 = 1 PR"** = "모든 Story = Phase 1 PR + Phase 2 PR (doc-only 단일 PR 폐지 — ADR-127)" 로 갱신.
- **"레인 진입 시 스킬 호출" 표의 `story-cutoff-classification` entry** = 면제 분류 제거된 새 역할 반영 (Story 작성 의무 단일 판정).
- "## 결정 · 대화 원칙" 영역에 "process 생략/단축은 묻지 않음 — 정식이 비협상 기본값 (ADR-127)" 1줄 추가.

### §I — `.claude-plugin/plugin.json` version bump (ADR-037 self-app)
- 현재 `6.29.0` → **`6.30.0` MINOR** bump. 근거: CLAUDE.md 핵심 흐름·결정원칙 의미 변경 + 핫패스 skill 3종(story-cutoff/story-epic-flow-preflight/user-dialog-mode) 행동 정책 전환 = MINOR(behavior change). PATCH 아님.
- description frontmatter = ADR-127 1줄 요약 prepend (CFP-2371 6.29.0 description 패턴 답습).

### §J — marketplace sync (ADR-063)
- plugin.json `version`·`description` 변경 → `mclayer/marketplace` 동일 필드 sync PR **필요**. marketplace sync PR 선행 merge → plugin PR merge (ADR-063 atomic invariant). bump 포함 PR merge 직후 Orchestrator `claude plugin update codeforge@mclayer` 실행.

### §K — `templates/github-workflows/phase-gate-mergeable.yml` + `.github/workflows/phase-gate-mergeable.yml` (process-derived fast-pass → deadlock-resolver 재설계, **본 Story in-scope**)

> 두 파일 byte-identical mirror (ADR-005) — 동일 편집 양쪽 적용. 편집 대상 = JS inline script (`actions/github-script`). 라인 번호 = 편집 시점 재확인 의무(grep anchor 우선).

**삭제 대상 (process-derived fast-pass — "Story 없음 / doc-only diff" 를 성공 근거로 삼는 branch)**:

- **`isDocOnly` 계산 블록 (L183-200)** + **요구사항리뷰 가드(L202-209)** 삭제 — `isDocOnly` 변수 자체 제거. 요구사항리뷰 가드(`reqReviewPhaseAttached && !reqReviewGateAttached → isDocOnly=false`)는 deadlock-resolver 의 "gate 라벨 부착 필수" 조건이 흡수(gate 미부착 = unblock 불가).
- **`isChoreOnly` 계산 블록 (L338-407)** 삭제 — `checkNoStoryBinding` helper(L350-367) + `hasChoreLabel`/`noSiblingOrImplLabel`/`choreSafePaths`/`isChoreOnly`(L370-407). §결정 1(chore 면제 폐지) 발효로 `noStoryBinding` 성공 경로(Story 없는 PR) 자체가 소멸 = dead path. dead path 명시 제거.

**신규 추가 (deadlock-resolver predicate — 삭제한 두 블록 자리 대체)**:

`isLabelMismatchOnly` predicate 신설 — "full-flow 증거 존재 ∧ 오직 phase 라벨만 mismatch" 인 경우에만 unblock. 의사코드:

```javascript
// ADR-127 §결정 5/8 — deadlock-resolver: full-flow 증거 ∧ phase 라벨만 mismatch 만 unblock.
// "Story 없음 / doc-only diff" 를 성공 근거로 삼지 않음 (process-derived fast-pass 폐지).
async function checkLabelMismatchOnly(body, localRefs, phaseLabel, prGateLabels, github, context) {
  // (1) full-flow 증거 #1 — Story binding 존재 (story_uri marker OR linked type:story Issue)
  //     "Story 없음" 은 여기서 즉시 false (chore 면제 폐지 §결정 1 — 모든 PR = Story 보유)
  const hasStoryUri = !!body.match(/story_uri:\s*(\S+)/);
  let hasStoryIssue = false;
  for (const n of localRefs) {
    try {
      const { data: issue } = await github.rest.issues.get({
        owner: context.repo.owner, repo: context.repo.repo, issue_number: n });
      if (issue.labels.map(l => l.name || l).includes('type:story')) { hasStoryIssue = true; break; }
    } catch (e) {
      if (e.status === 404) continue;
      return false;          // network/rate-limit/403/5xx = 판정 불가 → fail-closed (정식 차단)
    }
  }
  if (!hasStoryUri && !hasStoryIssue) return false;   // Story 미연결 → unblock 불가 (정식 차단)

  // (2) full-flow 증거 #2 — 현 단계 gate 라벨 부착 (lane PASS 증거)
  //     gate 라벨 0건 = lane 미통과 = unblock 불가 (요구사항리뷰 가드 흡수 — gate 미부착 차단).
  if (!prGateLabels || prGateLabels.length === 0) return false;

  // (3) phaseLabel 부재(미부착) = mismatch 가 아니라 라벨 누락 → 정식 차단(라벨 부착 의무).
  if (!phaseLabel) return false;

  // (4) 통과: full-flow 증거(Story ∧ gate) 충족 ∧ phaseLabel 만 required gate phase 와 어긋남.
  //     → unblock + 라벨 정합 안내(phase 라벨을 현 lane 단계로 전환 권고).
  //     주의: 차단 사유가 "phase mismatch 외 다른 실패원(예: required gate 미충족)"이면
  //     이 분기에 도달하지 않음 — required gate 평가는 OR-gate 이후 기존 로직이 담당.
  return true;
}
```

- **OR-gate 교체 (L410)**: 기존
  `if (isEpicLabel || isSiblingPr || isDocOnly || isPostMergeFix || isChoreOnly)`
  → `if (isEpicLabel || isSiblingPr || isPostMergeFix || isLabelMismatchOnly)`.
  `isLabelMismatchOnly` 호출 = OR-gate 직전:
  `const isLabelMismatchOnly = await checkLabelMismatchOnly(body, localRefs, phaseLabel, prGateLabels, github, context);`
- **fastPassTitle / reason (L411-420)**: `isDocOnly`/`isChoreOnly` 분기(reason 삼항) 제거 + `isLabelMismatchOnly` 분기 추가 — title `Phase Gate (label-mismatch resolver)`, reason `"full-flow 증거(Story binding ∧ gate 라벨) 충족 ∧ phase 라벨만 mismatch — 라벨 정합 권고 (ADR-127 §결정 5)"`. unblock 시 PR 코멘트 "phase 라벨을 현 lane 단계로 전환하세요" 안내.

**보존 (편집 0)**:

- `isPostMergeFix` (L211-336) — cross-repo land_order safe-defect 정정(byte-equivalence + 보안 non-touch 양면) PR-level CI 안전판. 운영 장애 hotfix 혼동 차단 배너 = §E.
- `isEpicLabel` (L174) / `isSiblingPr` (L180) — Epic close deadlock 방지 / sibling sync 보증 (§결정 8 — process 생략 아님).
- `hasCode` 계산(L150-162) — deadlock-resolver 가 직접 의존 않으나 OR-gate 이후 required gate 로직에서 사용 → 보존.

**invariant**: ① `enforce_admins:true` 보존 ② CFP-1845 anti-pattern(branch protection 손작업 우회 → 보안 게이트 단발 비활성 + audit gap, ADR-024 Amd 18 body L1758 실측 선례) 재발 차단 — full-flow 증거를 거친 PR 이 phase 라벨 mismatch 만으로 영구 `action_required` 되는 deadlock 을 deadlock-resolver 가 해소하므로 손작업 우회 불요. fast-pass **단순 삭제 금지** — 좁은 resolver 로 대체.

**테스트 의무 (구현 lane)**: deadlock-resolver structural-grep test 4-case 최소 — ① full-flow 증거 충족 ∧ phase mismatch → unblock / ② Story 없음 → 차단 / ③ gate 라벨 0건 → 차단 / ④ phaseLabel 부재 → 차단. 기존 isChoreOnly/isDocOnly test 제거. anti-theater (missing-case + 차단 assert 양면, exit code assert).

### §L — `CONTRIBUTING.md` (chore 면제 블록 + BYPASS_VERSION_BUMP 양면 폐지)

실측 확인 (2 carrier — F1 finding 반영):

- **L74-76 `### Bypass`** — "긴급 hotfix 시 `BYPASS_VERSION_BUMP=1` + `BYPASS_VERSION_BUMP_REASON=<text>` env 로 우회 가능 (audit trail 보존). hotfix-playbook 정합" 문장 삭제 (§결정 3.3) → `### Bypass` 섹션 전체 제거 또는 "버전 bump 우회 폐지 — 정식 플로우 안 무조건 (ADR-127 §결정 3)" 로 교체. 관련 CI(version bump gate, `check-plugin-version-bump` 류) 의 `BYPASS_VERSION_BUMP` env 분기가 있으면 함께 제거(grep 확인 의무).
- **L93-100 `## Story discipline (ADR-013 / CFP-45)`** (F1) — L98 "**면제 대상**: typo / 링크 / lint auto-fix / dependency lock / README 단순 문구 수정." + L100 "면제 시 commit body 에 `Story 면제 사유: <이유>` 1줄 명시." 삭제 → "**모든 변경 = Story 작성 의무 (면제 0 — ADR-127 §결정 1)**" 로 교체. L95 "cutoff 분류 — 강제 / 면제 결정. 모호 시 강제 측 분류" → "모든 변경 강제 (면제 분류 폐지)". L97 강제 대상 enumeration 은 보존(여전히 유효 — 강제 단일 분류).

### §M — hotfix-bypass:* family 처리 (§결정 9 실측 결론 적용 — wrapper 단일)

> **§결정 9 실측 결론**: required-6-tuple-skip blocking-tier hotfix-bypass = **0건** (required 6-tuple 5 workflow 전수 grep — hotfix-bypass 미참조, bypass channel 미설계). warning-tier(+ 6-tuple 미등록 blocking-on-pr) = 제외(merge 무차단 no-op). 따라서 **대량 label 제거 0** (폐지 대상 0건 — 검사연극 회피). 본 Story 편집 = invariant 명문화 + cross-ref:

- **`docs/inter-plugin-contracts/label-registry-v2.md`** — label 제거 0 (blocking-tier 폐지 대상 0건). frontmatter changelog 에 "ADR-127 §결정 9 — required-6-tuple-skip blocking-tier hotfix-bypass 0건 실측 확인 (required check 는 bypass channel 미설계), warning-tier 제외(merge 무차단)" 1줄 NOTE 추가만. label entry 본문 무변경.
- **`docs/evidence-checks-registry.yaml`** — entry 제거 0. required 6-tuple 짝(invariant-check / phase-gate-mergeable)은 이미 bypass 필드 없음(실측). 변경 0.
- **check 스크립트(`scripts/check-*.sh`) / workflow** — 분기 제거 0 (required check 가 hotfix-bypass 읽는 곳 0건 — 제거할 분기 없음).
- **`ADR-024 §결정 6.A`** (Amendment 19 §B 에 반영) — **required 6-tuple check 에 hotfix-bypass escape valve 신설 금지 invariant 명문화** (현 상태 bypass 0 을 영구 고정 — 미래 재발 차단, 강화 ratchet). 본문 §결정 6.A 무변경, Amendment 19 §B 에 invariant declare.
- **8-repo mirror** — 불요 (lane 8 repo archived, wrapper 단일 — §결정 9.0 실측).

## ADR Amendment 동반 (영향 ADR 무력화 — 본문 byte 보존, status/Amendment 방식)

| ADR | 처리 | 방식 |
|---|---|---|
| **ADR-054** | `status: Superseded by ADR-127` 전환 | frontmatter status 1줄 + 본문 상단 redirect 배너. 본문 byte 무변경 (historical 보존) |
| **ADR-013** | Amendment 8 append — chore 면제 폐지 | 본문 §결정 무변경, Amendment 절 추가 (chore 분류 무효 declare) |
| **ADR-024** | Amendment 19 append — ① §결정 6.A.10 isChoreOnly/isDocOnly process-derived fast-pass → deadlock-resolver 재설계 (§K, 본 Story in-scope) ② §결정 6.A hotfix-bypass:* family 전면 폐지 보류 + blocking-tier 우회 폐지 후보 식별(§결정 9) | Amendment 절 (fast-pass 재설계 + hotfix-bypass §결정 9 결론 cross-ref) |
| **ADR-064** | Amendment 14 append — §결정 3 룰 1/5 의 skip-offer 적용 금지 | Amendment 절 |
| **ADR-071** | Amendment 11 append — dialog skip-offer 금지 | Amendment 절 (§결정 5/20 ask-trigger 정합) |
| **ADR-114** | Amendment 1 append — minimal-path-direct lane-skip 무력화 (escalation audit-trail 보존) | Amendment 절 (§결정 2 절차 3 무효) |

## 결과

- 면제·단축경로 4종 전부 폐지 → 정식 풀 플로우가 비협상 기본값.
- process-derived fast-pass(isChoreOnly/isDocOnly) → deadlock-resolver(`isLabelMismatchOnly`) 재설계 → "Story 없음/doc-only diff" 성공 근거 제거 + CFP-1845 anti-pattern 재발 차단(보안 게이트 무약화) 양립.
- "단축 vs N/A" 3축 AND 구분 기준 명문화 → 정식 분류의 정상 N/A 와 노력 절감 skip 분리.
- consumer overlay 면제 확장채널 폐지 → overlay invariant("축소 불가") 강화.
- hotfix-bypass:* family 처리 = §결정 9 — required-6-tuple-skip blocking-tier = 실측 0건(required check 가 bypass channel 미설계 → 폐지 대상 0) + "required check bypass 신설 금지" invariant 명문화(강화 ratchet). warning-tier 제외(merge 무차단 no-op, 검사연극 회피).

## 비용 (정직 고지)

- 사소한 변경(오타·lint·버전범프)도 정식 10 lane + Phase 1/2 PR 분리 → 오버헤드 증가. 사용자 명시 수용.
- 운영 장애 긴급 대응 복구가 정식 플로우 소요만큼 지연. lane-skip 우회 없음(우회 = 면제 재도입 = directive 위반) — 대기시간 축약(병렬/timeout/on-call)만 허용(§결정 3.4). 사용자 명시 수용.
- **hotfix-bypass required-check escape valve = 이미 0** (§결정 9.5): required 6-tuple 은 애초에 hotfix-bypass escape valve 가 없다(실측 — invariant-check / phase-gate-mergeable 등 bypass channel 미설계). 따라서 "차단형 우회 0" 목표는 이미 달성 상태이며, 본 ADR 은 그 상태를 invariant 로 영구 고정(미래 재발 차단). 운영 비용 = 무관 pre-existing required check 실패도 PR 을 막음(우회 0) — required 6-tuple 은 phase/schema/invariant 정합이라 pre-existing 실패가 드물고, 발생 시 (i)근본 수정 (ii)검사 수정 (iii)무관이면 별도 정식 Story 수정. **이 영역은 deadlock-resolver(§K, phase-label mismatch)와 disjoint.** warning-tier hotfix-bypass 는 merge 무차단이라 폐지 무의미(no-op) → 제외.

## 해소 기준

N/A — `is_transitional: false` (영구 정책, 강화 방향 ratchet).

## 관련

- [ADR-054](ADR-054-doc-only-story-fast-path.md) — 본 ADR 이 supersede
- [ADR-013](ADR-013-codeforge-family-dogfood-out-policy.md) — chore 면제 carrier (Amendment 8)
- [ADR-024](ADR-024-story-scoped-branch-policy.md) — isChoreOnly fast-pass (PR-level 보존, Amendment 19)
- [ADR-064](ADR-064-decision-principle-mandate.md) — 결정 제시 원칙 (Amendment 14)
- [ADR-071](ADR-071-orchestrator-user-dialog-convergence.md) — dialog skip-offer 금지 (Amendment 11)
- [ADR-114](ADR-114-minimal-path-direct-invocation-protocol.md) — minimal-path-direct lane-skip 무력화 (Amendment 1)
- [ADR-005](ADR-005-plugin-self-application-na-standardization.md) — N/A 표준화 (단축 vs N/A 구분 anchor)
- CFP-2374 — 본 ADR carrier Story
