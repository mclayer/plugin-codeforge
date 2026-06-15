---
name: jira-progress-mirror
description: Orchestrator 의 Story/lane 진행을 코드와 분리된 평문 채널(Jira control project)로 **단방향 미러**하는 절차(Arc B). codeforge Story 진행이 Jira 에 보이게 하고 싶을 때 호출. ADR-038 6-point lane 전이(진입/PASS/FIX 검출/원인 판정/재진입/완료)에서 — 운영자 사전 지정 mirror 이슈에 진행 코멘트 post(sentinel 선두 + deny-scan MUST) + "현재 무엇 하는중" 1줄을 단일 코멘트 update 로 갱신. **comment-only**: 사용 도구 = `addCommentToJiraIssue` 1종만(이슈 생성·status 전이 없음). poll/dedup/echo-guard/rehydrate/timeout/stale 은 Arc A(jira-decision-channel) 전용 — Arc B 비대상. sentinel·deny-scan 만 Arc A 와 공유(같은 control project 안전). ADR-099 Amendment 1 §A1-1(narrow-allow addComment 1종) / ADR-100 §결정 3 정합.
tools: Read, Bash
---

# codeforge:jira-progress-mirror (CFP-2285 S5 / #2291 — Arc B: 세션·작업 모니터링 미러)

> Orchestrator 가 codeforge Story 를 진행하면서 그 **마일스톤 + 현재활동**을 코드·산출물과 섞이지 않는 비공개 Jira **control project** 로 **단방향 미러**(comment-only)한다. 사용자가 세션 밖(이메일/모바일/Jira 보드)에서도 "지금 어느 lane·무엇 하는중" 을 본다.
>
> **사용 도구 = `addCommentToJiraIssue` 1종만** (ADR-099 §A1-1 정합). 미러 대상 = 운영자가 **사전 생성**해 config 에 지정한 모니터링 이슈 1개. 이슈 생성(`createJiraIssue`)·status 전이(`transitionJiraIssue`/`getTransitionsForJiraIssue`)·issue-field write(`editJiraIssue`)는 **전부 deny — 본 절차가 호출하지 않는다**. 진행 마일스톤은 **코멘트 텍스트**로만, 현재활동은 **단일 코멘트 update**(addComment 의 commentId update 모드)로 표현한다.
>
> 정책 SSOT = [ADR-099 Amendment 1](../../archive/adr/ADR-099-atlassian-allow-redefinition.md) §A1-1~A1-4(narrow-allow `addCommentToJiraIssue` 1종 + deny-scan) + [ADR-100](../../archive/adr/ADR-100-confluence-doc-ssot-recognition.md) §결정 3. 입도·전이점 SSOT = [ADR-038](../../archive/adr/ADR-038-progress-visualization-todowrite.md) 6-point lane 전이.
>
> **caller scope (A1-1)**: 본 절차도 **Orchestrator preset 한정**(Arc A 와 동일). 임의 SubAgent 는 `addCommentToJiraIssue` narrow-allow 비대상(deny).

---

## 방향 = write-only · 도구 = comment-only (Arc A robustness 비대상 — 혼동 차단)

두 축을 구분한다: **방향 = write-only**(Orchestrator → Jira 단방향, 답 미수신) · **도구 범위 = comment-only**(`addCommentToJiraIssue` 1종 — 이슈 생성·status 전이·issue-field write 전부 deny, ADR-099 §A1-1).

본 절차는 **Orchestrator → Jira 단방향 출력**이다(진행을 내보냄, 답을 받지 않음). 따라서 결정 채널(Arc A — [`codeforge:jira-decision-channel`](../jira-decision-channel/SKILL.md))의 아래 robustness 는 **전부 Arc B 비대상**이다(답을 받는 게 아니므로 무의미):

| Arc A 단계 | Arc B 적용 |
|---|---|
| `poll` (답 조회) | **비대상** — 답을 받지 않음 |
| `dedup` (PROCESSED ledger) | **비대상** — 처리할 답이 없음 |
| `echo-guard` 폴러 필터 | **비대상** — Arc B 는 폴링하지 않음(단, sentinel 은 박는다 — 아래) |
| `rehydrate` (at-least-once 복구) | **비대상** — 복구할 미해결 fork 없음 |
| `timeout 재알림` / `stale anchor` | **비대상** — 대기·재확인할 결정 없음 |

**Arc A 와 공유하는 것은 2개뿐**: ① sentinel `⟦cf-orch⟧` 선두 박기, ② deny-scan(송신 전 보안 차단 MUST). 그 외 Arc A 로직은 Arc B 가 import 하지 않는다.

---

## sentinel 공유 — Arc A 정합 (같은 control project 안전)

본 절차가 쓰는 **모든** 미러 코멘트(6-point 진행 미러 / 현재활동 pinned 코멘트)는 본문 **선두**에 sentinel `⟦cf-orch⟧` 를 박는다.

- **왜 박는가**: Arc B 진행 미러 코멘트가 같은 Jira control project 에 쌓이면, Arc A 폴러가 그 진행 코멘트를 결정 fork 의 "사용자 답" 으로 **재섭취할 위험**이 있다. sentinel 을 박으면 Arc A 의 `echo-guard.sh` 가 exit 0(skip)으로 걸러 진행 미러를 답 후보에서 제외한다 → **decision_channel 과 progress_mirror 가 같은 project 를 공유해도 안전**(self-echo·cross-echo 차단).
- **sentinel SSOT = `scripts/jira-channel/echo-guard.sh` 의 `CF_ORCH_SENTINEL` 상수 + `scripts/jira-channel/progress-format.sh` 의 동명 상수**. 두 상수 + 본 문서 표기 `⟦cf-orch⟧` 는 **byte-동일**해야 한다(불일치 시 echo-guard 가 진행 미러를 못 걸러 cross-echo 발생).

```bash
# 진행 미러 본문이 echo-guard 로 skip(exit 0) 되는지 = Arc A 안전성 확인
printf '%s' "$MIRROR_BODY" | bash scripts/jira-channel/echo-guard.sh
# exit 0 = skip(Arc A 폴러가 답 후보에서 제외 — 안전) · exit 1 = candidate(= sentinel 누락 결함!)
```

---

## 채널 추상화 (channel-agnostic — Arc A 정합)

Arc A SKILL.md 의 channel-agnostic 추상과 정합 — 절차 본체는 채널 비의존이고 Jira 특정 호출은 "adapter: jira" 섹션에만 둔다(후속에 GitHub/Slack adapter 를 끼울 여지).

| 추상 단계 | 의미 | adapter 책임 |
|---|---|---|
| `load_config` | progress_mirror 활성 여부·좌표·mirror 이슈 key 로드 | config block parse |
| `resolve_mirror` | config 의 사전 지정 mirror 이슈 key 확인(빈값 = no-op) | 채널별 식별자 검증(생성 없음) |
| `format` | 6-point 전이 진행 본문 결정론적 포맷(sentinel 선두) | 채널 무관(순수 텍스트, `progress-format.sh`) |
| `deny_scan` | 진행 payload 송신 전 보안 차단(MUST) | 채널 무관(순수 텍스트) |
| `mirror_comment` | 진행 마일스톤 코멘트 post(sentinel 선두) | 채널별 comment write API |
| `mirror_activity` | "현재 무엇 하는중" 1줄 = 단일 코멘트 update(commentId 추적) | 채널별 comment update API |

> v1 구현 adapter = **jira** 1종(`addCommentToJiraIssue` 단일 도구로 post·update 모두 수행). adapter 호출은 아래 "adapter: jira" 참조. **`resolve_mirror` 는 생성을 하지 않는다** — mirror 이슈는 운영자 사전 생성·config 지정 책임(이슈 생성 = deny).

---

## 0. 적용 조건 / config 로드 (`load_config`)

`.claude/_overlay/project.yaml` 의 `atlassian.jira.progress_mirror` 블록을 읽는다.

- 블록 **부재** 또는 `enabled: false` → 본 미러 **no-op(skip)**. 진행은 평소대로 TodoWrite(ADR-038)로만 시각화하고 본 skill 종료. (Arc B 는 **opt-in, 기본 off**.)
- `enabled: true` → 아래 필드 로드 후 절차 진행:
  - `project_key` — 진행 미러 대상 control project key. (decision_channel 의 `control_project_key` 와 **같은 project 공유 가능** — sentinel·echo-guard 정합으로 안전.)
  - `mirror_issue_key` — **운영자가 사전 생성**한 모니터링 이슈 1개의 key(Epic 당 또는 기존 이슈 재사용). **부재/빈값 → 본 skill no-op**(아래 §1 참조 — `enabled: true` 여도 skip, warn 1회). 이슈 생성은 deny 이므로 skill 이 만들지 않는다.
  - `current_activity` — 현재활동 갱신 방식(`pinned-comment-update` — 단일 "현재활동" 코멘트를 commentId update).
  - `cloud_id` — Atlassian cloudId(decision_channel 블록과 공유 — MCP 호출 인자).

---

## 1. mirror 이슈 resolve (`resolve_mirror`) — 사전 지정, 생성 없음

미러 대상 = **운영자가 사전 생성**해 config 에 지정한 모니터링 이슈 1개(`progress_mirror.mirror_issue_key`). Epic 당 1개를 두거나 기존 모니터링 이슈를 재사용한다. **skill 은 이슈를 만들지 않는다** — 이슈 생성(`createJiraIssue`)은 ADR-099 §A1-1 deny 이므로, mirror 대상 확보는 코멘트 1종(`addCommentToJiraIssue`) 권한 밖이다.

1. **config 에서 key 읽기**: `progress_mirror.mirror_issue_key` 를 읽는다.
2. **빈값/부재 → no-op(warn 1회)**: `mirror_issue_key` 가 빈 문자열이거나 없으면, `enabled: true` 여도 본 skill 을 **no-op 종료**한다 — 세션당 **warn 1회**만 남기고(반복 warn 금지) 진행은 TodoWrite(ADR-038)로만 시각화한다.
   ```
   [jira-progress warn] progress_mirror.enabled=true 이나 mirror_issue_key 미지정 — 미러 skip.
     운영자가 control project 에 모니터링 이슈 1개를 만들고 그 key 를 mirror_issue_key 에 넣으면 활성화됨.
   ```
3. **값 있으면 그 key 를 mirror 대상으로 사용**: 이후 모든 6-point 코멘트(§2)와 현재활동 update(§3)가 이 단일 이슈를 대상으로 한다. Story↔mirror 매핑은 config 지정 이슈로 단순화(별도 조회·생성 없음).

- **생성·조회 호출 없음**: `createJiraIssue`·`searchJiraIssuesUsingJql` 를 호출하지 않는다(이슈 1개를 config 로 고정). mirror 대상은 운영자 책임이고, skill 의 Jira 호출은 `addCommentToJiraIssue` 1종으로 한정된다.

---

## 2. 6-point 전이 미러 (`format` → `deny_scan` → `mirror_comment`)

ADR-038 의 **6 전이점**(진입 / PASS / FIX 검출 / 원인 판정 / 재진입 / 완료) 각각에서 미러한다. **라이브 turn-단위가 아니라 lane 마일스톤 입도**(6 전이점 + 현재활동 1줄). 6-point 마일스톤은 **코멘트 텍스트로만** 표현하고 **Jira status 전이는 일절 하지 않는다**(`transitionJiraIssue`/`getTransitionsForJiraIssue` = deny).

> ADR-038 6-point 실측 인용 (CLAUDE.md "lane 전이 6시점(진입/PASS/FIX 검출/원인 판정/재진입/완료)" + ADR-038 §결정 2~6):
> - **진입** = lane entry(새 row ⏳ in_progress)
> - **PASS** = lane pass(✅ + phase 라벨 transition)
> - **FIX 검출** = 검출 lane(🔄, content `FIX-N detected (cause: <원인 lane>)`) — §결정 3
> - **원인 판정** = 원인 lane content suffix `FIX-N 원인 · <판정 1줄>` — §결정 3
> - **재진입** = 새 row append(content suffix `(재진입)` / `(재진입 RESET-N)`) — §결정 6
> - **완료** = Story 완료

### (a) 진행 본문 포맷 (`format`)

`progress-format.sh` 로 sentinel 선두 본문을 결정론적으로 만든다.

```bash
bash scripts/jira-channel/progress-format.sh <전이종류> <lane> "<1줄 요약>" [<Story KEY>]
#   <전이종류> = enter | pass | fix-detected | cause | re-enter | complete  (6-point)
#   stdout = "⟦cf-orch⟧ MIRROR <전이라벨> lane=<lane> story=<KEY> — <요약>"
#   exit 0 = 성공 · exit 3 = 전이종류 미인식 / 인자 누락
```

전이종류 ↔ 6-point 대응: `enter`=진입 / `pass`=PASS / `fix-detected`=FIX 검출 / `cause`=원인 판정 / `re-enter`=재진입 / `complete`=완료.

### (b) deny-scan — 송신 전 hard-block (MUST, A1-2)

진행 본문(format 산출물)을 송신 **전** 반드시 검사한다. 통과 못하면 **post 중단**(warning 아님). Arc A 와 **같은 스크립트 공유**.

```bash
printf '%s' "$MIRROR_BODY" | bash scripts/jira-channel/deny-scan.sh
# exit 0 = clean(진행) · exit 2 = BLOCKED(중단) · exit 3 = 입력오류
```

- exit 2 → **post 하지 말 것**. 진행 요약(1줄)에 secret/절대경로/transcript 가 새지 않게 요약을 재구성(식별자만). 위반 패턴 라벨은 audit 에 기록(패턴 값 재노출 금지).
- 진행 요약은 **식별자·lane·전이 종류만** — 절대경로·full transcript·코드블록 통째 금지(deny-scan 차단 대상).

### (c) 진행 코멘트 post (`mirror_comment`)

deny-scan PASS 본문을 mirror 이슈에 코멘트로 단다. **status 전이는 없다** — 6-point 마일스톤(`⟦cf-orch⟧ MIRROR [<전이라벨>] lane=<lane> — <요약>`)은 전부 **코멘트 텍스트**로만 표현한다.

```
mcp__plugin_atlassian_atlassian__addCommentToJiraIssue(
  cloudId      = <config.cloud_id>,
  issueIdOrKey = <config.mirror_issue_key>,
  commentBody  = <progress-format.sh 산출 본문>     # 선두 sentinel ⟦cf-orch⟧ — echo-guard 정합
)
```

- 본문은 **이미 sentinel 선두**(progress-format.sh 산출). Arc A echo-guard 가 이 코멘트를 답 후보에서 제외한다(같은 project 공유 안전).
- 전이 종류(진입/PASS/FIX 검출/원인 판정/재진입/완료)는 모두 progress-format 의 전이라벨로 코멘트에 들어간다. Jira status(`할 일`/`진행 중`/`완료` …)는 **건드리지 않는다** — lane phase ↔ Jira status 매핑 자체가 없다.
- write = `addCommentToJiraIssue` **1종만**(A1-1 narrow-allow). `createJiraIssue`/`editJiraIssue`/`transitionJiraIssue`/`getTransitionsForJiraIssue`/`addWorklogToJiraIssue`/`createIssueLink` = **deny — 본 절차 미사용**.

---

## 3. 현재활동 1줄 갱신 (`mirror_activity`) — 단일 코멘트 update

"현재 무엇 하는중" 을 **단일 라인**으로 갱신한다(매 6-point 에서). 입도 = lane 마일스톤 + 현재활동 1줄(라이브 turn-단위 아님). issue-field write(summary 변경 등 `editJiraIssue`)는 **deny 이므로 하지 않는다**.

- **표기 방식 = `config.current_activity = "pinned-comment-update"`**: "현재활동" 코멘트 **1개**를 두고, 활동이 바뀔 때마다 같은 commentId 로 **update** 한다.
  - `addCommentToJiraIssue` 는 `commentId` 인자를 주면 **기존 코멘트를 갱신**한다(commentId 없으면 신규 생성). 즉 신규/update 모두 **narrow-allow 동일 도구 1종**으로 처리된다 — 별도 write 권한 불필요.
  ```
  # 최초 1회 — 현재활동 코멘트 생성(commentId 미지정). 산출 commentId 를 세션 내 추적.
  mcp__plugin_atlassian_atlassian__addCommentToJiraIssue(
    cloudId      = <config.cloud_id>,
    issueIdOrKey = <config.mirror_issue_key>,
    commentBody  = "⟦cf-orch⟧ [현재] lane=<lane>·<전이라벨> — <1줄 요약>")   # 선두 sentinel
  # → 반환된 commentId 를 ACTIVITY_COMMENT_ID 로 세션 transcript 에 기록.

  # 이후 — 같은 commentId 로 update(신규 코멘트 양산 없이 1개를 최신화).
  mcp__plugin_atlassian_atlassian__addCommentToJiraIssue(
    cloudId      = <config.cloud_id>,
    issueIdOrKey = <config.mirror_issue_key>,
    commentId    = <ACTIVITY_COMMENT_ID>,
    commentBody  = "⟦cf-orch⟧ [현재] lane=<lane>·<전이라벨> — <1줄 요약>")
  ```
- 세션 내 `ACTIVITY_COMMENT_ID` 추적이 끊기면(새 세션/유실) 다음 1회는 commentId 없이 생성하고 그 id 를 다시 추적한다(현재활동 코멘트가 1~소수로 수렴, 폭증 없음).
- 현재활동 1줄도 **deny-scan 통과 의무**(2(b) 재적용 — secret/절대경로 금지). 현재활동 본문도 sentinel 선두라 Arc A echo-guard 가 답 후보에서 제외한다.
- 6-point 마일스톤 코멘트(2(c))의 `— <1줄 요약>` 부분도 그 시점의 활동을 담으므로, pinned 코멘트와 마일스톤 로그가 함께 "현재/이력" 을 보여준다(issue-field write 없이 코멘트만으로 보장).

---

## 4. audit (A1-4)

모든 Orchestrator Jira write(comment post / activity update)와 미러 결과를 **세션 transcript** 에 기록한다 — wrapper-side audit 가 SSOT(Jira author 추적 비신뢰).

```
[jira-progress audit] story=<KEY> mirror-issue=<config.mirror_issue_key>
  6-point: <전이종류> lane=<lane> — <요약 1줄>
  comment: addCommentToJiraIssue ok (sentinel=⟦cf-orch⟧, echo-guard skip 확인)
  활동: addCommentToJiraIssue update ok (commentId=<ACTIVITY_COMMENT_ID>) — <현재 무엇 하는중 1줄>
```

- status 전이 기록 항목 없음 — comment-only 라 transition 미발생.

- secret/절대경로 = audit 에도 기록 금지(요약만 — deny-scan 차단 항목과 동일 원칙).
- **write-only 명시**: 본 audit 는 출력 기록만 — Arc A 의 poll/parse/dedup/PROCESSED 기록은 Arc B 에 없다(write-only, 답 미수신).

---

## deferred 경계 (Arc B 구현 범위 + Arc A 와의 관계)

| 항목 | 소유 | 상태 | 비고 |
|---|---|---|---|
| mirror 이슈 resolve(사전 지정) | **S5 (#2291)** | **구현됨** | config `mirror_issue_key` 1개 고정. 빈값=no-op(warn 1회). 이슈 생성 안 함(createJiraIssue deny) (§1) |
| 6-point 전이 미러(comment-only) | **S5 (#2291)** | **구현됨** | ADR-038 6 전이점 → `progress-format.sh`(sentinel 선두) + deny-scan MUST + `addCommentToJiraIssue` post. status 전이 없음 (§2) |
| 현재활동 1줄 갱신(pinned comment update) | **S5 (#2291)** | **구현됨** | lane 마일스톤+현재활동 입도(라이브 turn 아님). 단일 코멘트를 commentId update — addComment 1종 (§3) |
| sentinel·deny-scan 공유 | **Arc A(S2/S3) 재사용** | **공유** | echo-guard.sh sentinel SSOT + deny-scan.sh — 같은 control project 안전(cross-echo 차단) |
| 이슈 생성 / status 전이 / issue-field write | **deny** | **비대상** | createJiraIssue/transitionJiraIssue/getTransitionsForJiraIssue/editJiraIssue = ADR-099 §A1-1 deny — 본 절차 미사용 |
| poll/dedup/echo-guard 폴러/rehydrate/timeout/stale | **Arc A 전용** | **비대상** | comment-only 라 답 수신 없음 → 무의미. Arc B 가 import 안 함(방향 섹션) |

> Arc B = comment-only 진행 미러. 사용 도구 = `addCommentToJiraIssue` 1종(post + commentId update). ADR-038 6-point lane 전이 + 현재활동 1줄 입도로 codeforge 진행을 Jira 로 단방향 출력하되, **이슈 생성·status 전이·issue-field write 는 전부 deny 라 호출하지 않는다**(ADR-099 §A1-1 정합). Arc A 의 결정-루프 robustness(poll/dedup/rehydrate/timeout/stale)는 전부 비대상이고, sentinel·deny-scan 만 공유해 같은 control project 를 안전하게 함께 쓴다.
