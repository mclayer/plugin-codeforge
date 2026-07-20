---
name: jira-progress-mirror
description: Orchestrator 의 Story/lane 진행을 코드와 분리된 평문 채널(Jira control project)로 **단방향 미러**하는 절차(Arc B). codeforge Story 진행이 Jira 에 보이게 하고 싶을 때 호출. ADR-038 6-point lane 전이(진입/PASS/FIX 검출/원인 판정/재진입/완료)에서 — 운영자 사전 지정 mirror 이슈에 진행 코멘트 post(sentinel 선두 + deny-scan MUST) + "현재 무엇 하는중" 1줄을 단일 코멘트 update 로 갱신. **comment-only**: 사용 도구 = `addCommentToJiraIssue` 1종만(이슈 생성·status 전이 없음). poll/dedup/echo-guard/rehydrate/timeout/stale 은 Arc A(jira-decision-channel) 전용 — Arc B 비대상. sentinel·deny-scan 만 Arc A 와 공유(같은 control project 안전). ADR-099 Amendment 1 §A1-1(narrow-allow addComment 1종) / ADR-100 §결정 3 정합. **Arc B-2**(신규): 병렬 브랜치별 coarse 생존 heartbeat 를 같은 mirror 이슈의 branch→commentId map(N개 pinned 코멘트, commentId 재사용 update)으로 relay — 같은 `addCommentToJiraIssue` 1종(createJiraIssue 없음), `HEARTBEAT` 토큰(MIRROR 와 분별), sentinel·deny-scan 재사용, 여전히 write-only(읽기=외부 watchdog 별도). ADR-164 §결정 3.
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

## Arc B 두 하위 갈래 — Arc B-1(마일스톤 미러) / Arc B-2(per-branch heartbeat relay)

본 skill 은 같은 mirror 이슈(§0/§1 공유 좌표) 위에서 두 하위 갈래를 운용한다. **둘 다 write-only · comment-only(`addCommentToJiraIssue` 1종) · sentinel `⟦cf-orch⟧` 선두 · deny-scan MUST** 를 공유하고, 이슈 생성·status 전이·issue-field write 는 **양쪽 다 deny**.

| 갈래 | 무엇 | 코멘트 토큰 | 코멘트 topology | 입도 |
|---|---|---|---|---|
| **Arc B-1** (기존 §2·§3) | ADR-038 6-point lane 마일스톤 + "현재 무엇 하는중" 1줄 | `MIRROR` (progress-format.sh) | 마일스톤 = append 로그 · 현재활동 = **단일** pinned 코멘트(`ACTIVITY_COMMENT_ID`) update | lane 마일스톤 |
| **Arc B-2** (신규 — 아래 별도 섹션) | 병렬 브랜치별 coarse 생존(liveness) heartbeat | `HEARTBEAT` (heartbeat-format.sh) | **branch→commentId map** — 브랜치마다 pinned 코멘트 1개(commentId 재사용 update), N 브랜치 → N 코멘트 | 브랜치 tick |

- **§0(config)·§1(mirror resolve) 는 두 갈래 공유** — 같은 `mirror_issue_key`, 같은 opt-in(블록 부재/`enabled:false`/`mirror_issue_key` 빈값 → **양쪽 no-op**). Arc B-2 는 별도 이슈를 만들지 않는다(같은 이슈 위 per-branch 코멘트).
- **토큰 분별(MIRROR vs HEARTBEAT)**: 같은 control project 에 두 토큰 코멘트가 공존해도, 외부 watchdog 파서는 `HEARTBEAT` 만 골라 읽는다(Change Plan §4.2 / ADR-164 §결정 3). Arc B-1 진행 미러(`MIRROR`)와 섞이지 않는다.
- **write-only 불변 유지**: Arc B-2 도 Orchestrator → Jira 단방향 출력이다. per-branch 코멘트를 **읽어** staleness 를 판정하는 것은 **외부 watchdog**(별도 GitHub Actions cron — 본 skill 아님, Arc B-2 (f) read-path 교차참조). 본 skill 은 poll/read 하지 않는다.
- SSOT: [ADR-164](../../archive/adr/ADR-164-parallel-branch-liveness-heartbeat-watchdog.md) §결정 3(per-branch pinned 코멘트 = branch→commentId map) / §결정 5(monotonic seq 3-state) + Change Plan §3.1·§4.2·§11.6.

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

본 절차가 쓰는 **모든** 미러 코멘트(Arc B-1 6-point 진행 미러 / 현재활동 pinned 코멘트 / **Arc B-2 브랜치별 heartbeat 코멘트**)는 본문 **선두**에 sentinel `⟦cf-orch⟧` 를 박는다.

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

## 2. (Arc B-1) 6-point 전이 미러 (`format` → `deny_scan` → `mirror_comment`)

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

## 3. (Arc B-1) 현재활동 1줄 갱신 (`mirror_activity`) — 단일 코멘트 update

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

## Arc B-2 — per-branch heartbeat relay (신규 · `HEARTBEAT` 토큰 · branch→commentId map)

병렬·백그라운드 브랜치의 **coarse 생존 신호(liveness heartbeat)** 를 같은 mirror 이슈(§0/§1 공유 좌표) 위의 **브랜치별 pinned 코멘트**로 relay 한다. Arc B-1 §3 의 **단일** `ACTIVITY_COMMENT_ID`(pinned-comment-update)를 **`{branch_key → commentId}` map** 으로 일반화한 것 — 같은 `mirror_issue_key`, 같은 `addCommentToJiraIssue` 1종, 브랜치마다 pinned 코멘트 1개(commentId 재사용 update).

> SSOT = [ADR-164](../../archive/adr/ADR-164-parallel-branch-liveness-heartbeat-watchdog.md) §결정 3(per-branch pinned COMMENTS = branch→commentId map, **NOT** per-branch issue) / §결정 5(monotonic seq 3-state) · Change Plan §3.1·§4.2·§11.6. **opt-in 상속**: §0 블록 부재 / `enabled:false` / `mirror_issue_key` 빈값 → **no-op(skip)** — Arc B-1 과 완전히 동일(기본 off). 별도 이슈를 만들지 않는다(같은 이슈 위 per-branch 코멘트).

### (a) 왜 per-branch 인가 (AC-7 — partial-hang 은폐 해소)

- **근원 결함**: 단일 mirror 이슈 위 **단일** pinned 코멘트에 N 브랜치가 heartbeat 를 쓰면, 이슈 `updated`(및 그 단일 코멘트) = **최근 writer**(살아있는 브랜치)로 fresh 하게 보인다 → **N 중 1개만 hung(partial-hang)** 되어도 그 정체가 최근 writer 에 가려 **은폐**된다.
- **해소**: 브랜치마다 **독립 pinned 코멘트**를 두면 외부 watchdog 가 브랜치별 코멘트 본문(seq·ts)을 각각 읽어 **정체된 그 브랜치를 특정**한다(이슈 `updated` 집계값이 아니라 per-branch 본문 기준). = ADR-164 §결정 3 / Change Plan §8.2 discriminating fixture 의 GREEN 경로.

### (b) branch→commentId map — 단일 `ACTIVITY_COMMENT_ID` 의 일반화

- Arc B-1 §3 은 "현재활동" 코멘트 **1개**를 `ACTIVITY_COMMENT_ID` 로 추적해 commentId update 했다. Arc B-2 는 이를 **브랜치별**로 확장 — 세션 내 `{branch_key → commentId}` map 을 추적한다.
- **N 브랜치 → N pinned 코멘트**, 각각 **자기 commentId 로 in-place update**(commentId 재사용). Arc B-1 의 "신규 코멘트 양산 없이 1개를 최신화" 규율을 브랜치 수만큼 병렬화한 것(브랜치당 1 코멘트 수렴).
- **`branch_key` = git short-name slug `[a-z0-9-]`** — `git rev-parse --abbrev-ref HEAD` 산출을 기계 도출한 slug 만 쓴다. **caller free-text override 미수용**(임의 문자열로 브랜치 키 지정 불가 → 경로·PII 인코딩 구조적 차단, ADR-164 §7.2 T-HB-1).
- **도구 불변 = `addCommentToJiraIssue` 1종만**: 최초 브랜치 tick = commentId 미지정 post(브랜치별 pinned 코멘트 신규 생성) → 반환 commentId 를 map 에 기록. 이후 tick = 그 commentId 로 update. **`createJiraIssue` 없음** — per-branch **이슈**는 ADR-099 §A1-1 **P0-deny**(SecurityArch, ADR-164 §결정 3). per-branch granularity 는 per-branch **코멘트**로 addComment 범위 내 달성한다. `editJiraIssue`/`transitionJiraIssue`/`getTransitionsForJiraIssue`/`addWorklogToJiraIssue` = 여전히 deny.

### (c) heartbeat 본문 포맷 (신규 `heartbeat-format.sh` — progress-format.sh 형제)

comment body 는 신규 `scripts/jira-channel/heartbeat-format.sh`(progress-format.sh 형제 — 실행가능 SSOT, ADR-140 reuse-before-write)가 결정론적으로 만든다. **본 skill 은 포맷을 소유하지 않는다** — 스크립트 stdout 을 그대로 코멘트로 post/update 한다(Arc B-1 이 progress-format.sh stdout 을 쓰는 것과 동형). **정확한 인자·순서 계약 = heartbeat-format.sh SSOT**(DevCore 병렬 작성).

```bash
bash scripts/jira-channel/heartbeat-format.sh <branch_key> <seq> <story> <lane> [<ts>] [<state_tag>]   # 인자 계약 SSOT=스크립트
#   stdout(마이크로포맷 = heartbeat-format.sh 실행가능 SSOT §11.7; ADR-164 §결정 3 예시 + §결정 5/6 state_tag):
#     "⟦cf-orch⟧ HEARTBEAT branch=<branch_key> seq=<N> story=<KEY> lane=<lane> ts=<UTC ISO8601> state=<state_tag> — alive"
#   선두 sentinel ⟦cf-orch⟧ = echo-guard.sh CF_ORCH_SENTINEL byte-동일(Arc A cross-echo 차단)
```

- **`HEARTBEAT` 토큰 = `MIRROR`(Arc B-1)와 분별**: 같은 control project 에 두 토큰 코멘트가 공존해도 외부 watchdog 파서가 **HEARTBEAT 만** 골라 읽는다(Change Plan §4.2 / ADR-164 §결정 3 · §7.6 T-HB-8).
- `seq` = per-branch strictly-monotonic 정수(**1차 진행 신호**), `ts` = **표시 전용(advisory)** — staleness 판정 clock 기준은 외부 watchdog **자기 수신 시각**이지 발신 `ts` 가 아니다(ADR-164 §결정 5 F-5). `state=<state_tag>` = emitter advisory self-state(`active`|`waiting-external[:<reason>]`|`idle-yield`, ADR-164 §결정 5/6) — watchdog D4 idle-relaxation 이 소비(§결정 6, 단 total-deadline ceiling 은 무력화 못 함 INV-L1); 말미 리터럴 `— alive` = 고정 liveness 어써션 tail. fresh/stalled/unknown **3-state 판정은 emitter 가 아니라 외부 watchdog** 가 seq 진행·수신시각으로 한다.
  - **정직 note (§4.2 예시 vs §결정 5/6)**: Change Plan §4.2 / ADR-164 §결정 3 의 **예시** 마이크로포맷은 `state=` 필드를 생략(`… ts=<…> — alive`)했으나, §결정 5/6 이 state_tag 를 heartbeat record 필드로 명시하고 D4 idle-relaxation 이 이를 요구하므로 실행가능 SSOT(heartbeat-format.sh, §11.7)는 `state=<state_tag>` 를 **additive** 로 실은다(§4.2 tail `— alive` 보존). §4.2 예시의 state_tag 누락 = ArchitectPL 회부 대상 §4.2 완전성 gap(비차단).
- 본 skill 은 per-branch **seq durable state 를 소유하지 않는다** — seq durable read-back+1(restart 생존)은 emit 모듈 `scripts/lib/emit_branch_heartbeat.py` 소관(Change Plan §5, ADR-164 §결정 5).

### (d) deny-scan MUST (송신 전 backstop) + sentinel (echo-guard skip) — Arc B-1 §2(b) 재사용

Arc B-1 §2(b) 와 **동일 규율**을 heartbeat 코멘트에도 적용한다(신규 로직 복붙 아님 — 같은 스크립트 재사용):

- **deny-scan MUST**: heartbeat 본문(heartbeat-format.sh 산출)을 post/update **전** `scripts/jira-channel/deny-scan.sh` 로 검사 — exit 2(BLOCKED) → **post 중단**(warning 아님). branch_key 가 slug `[a-z0-9-]` 라 경로·PII 인코딩이 이미 불능이나 deny-scan 을 **backstop** 으로 그대로 통과시킨다.
  - ★ deny-scan 은 email·RRN **미커버** → AC-8 의 14-rule redaction floor 가 1차 방어(ADR-043 상속), deny-scan 단독 아님(ADR-164 §7.6 T-HB-3). heartbeat payload = **bounded 3-tuple**(branch_key slug + numeric seq + enum lane) → free-form content 0.
- **sentinel `⟦cf-orch⟧` 선두**: heartbeat-format.sh 산출물은 이미 sentinel 선두 → Arc A `echo-guard.sh` 가 exit 0(skip)으로 걸러 결정폴러 재섭취(cross-echo)를 막는다(Arc B-1 과 같은 control project 안전).

```bash
# Arc B-1 §2(b)·sentinel 섹션과 같은 검사 (예시)
printf '%s' "$HEARTBEAT_BODY" | bash scripts/jira-channel/deny-scan.sh    # exit 0=clean · 2=BLOCKED(중단)
printf '%s' "$HEARTBEAT_BODY" | bash scripts/jira-channel/echo-guard.sh   # exit 0=skip(안전) · 1=sentinel 누락 결함
```

### (e) per-branch 코멘트 post/update (`addCommentToJiraIssue` 1종) + idempotency

```
# 최초 브랜치 tick — commentId 미지정 post(브랜치별 pinned 코멘트 신규 생성). 산출 commentId 를 map 기록.
mcp__plugin_atlassian_atlassian__addCommentToJiraIssue(
  cloudId      = <config.cloud_id>,
  issueIdOrKey = <config.mirror_issue_key>,          # Arc B-1 과 같은 단일 mirror 이슈
  commentBody  = <heartbeat-format.sh 산출 본문>)      # 선두 sentinel ⟦cf-orch⟧ + HEARTBEAT 토큰
# → 반환 commentId 를 {branch_key → commentId} map 에 기록.

# 이후 tick — 그 branch_key 의 commentId 로 update(브랜치별 코멘트 1개를 최신화 — 신규 양산 없음).
mcp__plugin_atlassian_atlassian__addCommentToJiraIssue(
  cloudId      = <config.cloud_id>,
  issueIdOrKey = <config.mirror_issue_key>,
  commentId    = <map[branch_key]>,
  commentBody  = <heartbeat-format.sh 산출 본문>)
```

- **idempotency (§11.6)**: 각 브랜치 heartbeat 코멘트는 **결정론적 marker `⟦cf-orch⟧ HEARTBEAT branch=<slug>`** 로 유일 식별된다. 그 브랜치의 **단일 코멘트를 update-in-place**(commentId 재사용)하고 **blind create 는 금지**(브랜치당 코멘트 1개 수렴 → **flood 방지**). marker 는 ① 외부 watchdog 가 per-branch 로 read·attribute 하는 앵커이자 ② update-in-place 의 결정론적 키다. 본 skill 은 세션 `{branch_key → commentId}` map 으로 commentId 를 잡아 write 하며 **Jira 를 read/poll 하지 않는다**(write-only).
- **write = `addCommentToJiraIssue` 1종만**(A1-1 narrow-allow, post + commentId update). status 전이·이슈 생성·issue-field write 없음.

### (f) read-path = 외부 watchdog (본 skill 아님 — 교차참조만)

- Arc B-2 의 **읽기 경로(dual)** = per-branch 코멘트를 **읽어** now−last_tick·seq 진행으로 staleness 를 판정하는 **외부 watchdog**다 — 별도 **GitHub Actions cron**(`.github/workflows/branch-liveness-watchdog.yml`, read-only Jira token; Change Plan §3.3/§5, ADR-164 §결정 4). **본 skill 이 아니다.**
- 본 skill 은 **write-only 불변**을 유지한다 — poll/read/dedup/rehydrate/timeout 은 Arc A(jira-decision-channel) 전용이자 watchdog 소관이며, Arc B(1·2) 어느 쪽도 하지 않는다. watchdog 3-state·fail-open 금지(unknown≠PASS) = ADR-164 §결정 5 — **본 skill 은 판정하지 않는다. heartbeat 를 내보내기만 한다.**

---

## 4. audit (A1-4) — Arc B-1·B-2 공통

모든 Orchestrator Jira write(Arc B-1 comment post / activity update, Arc B-2 heartbeat post/update)와 미러 결과를 **세션 transcript** 에 기록한다 — wrapper-side audit 가 SSOT(Jira author 추적 비신뢰).

```
[jira-progress audit] story=<KEY> mirror-issue=<config.mirror_issue_key>
  6-point: <전이종류> lane=<lane> — <요약 1줄>
  comment: addCommentToJiraIssue ok (sentinel=⟦cf-orch⟧, echo-guard skip 확인)
  활동: addCommentToJiraIssue update ok (commentId=<ACTIVITY_COMMENT_ID>) — <현재 무엇 하는중 1줄>
  heartbeat(Arc B-2): addCommentToJiraIssue {post|update} ok (branch=<slug>, seq=<N>, commentId=<map[branch_key]>, token=HEARTBEAT) — per-branch liveness tick
```

- status 전이 기록 항목 없음 — comment-only 라 transition 미발생.

- secret/절대경로 = audit 에도 기록 금지(요약만 — deny-scan 차단 항목과 동일 원칙).
- **write-only 명시**: 본 audit 는 출력 기록만 — Arc A 의 poll/parse/dedup/PROCESSED 기록은 Arc B 에 없다(write-only, 답 미수신).
- **Arc B-2 heartbeat 도 write-only 감사**: 위 heartbeat 줄도 출력(post/update) 기록만이다 — staleness 3-state 판정·per-branch read 는 **외부 watchdog** 소관(자기 GitHub durable verdict 로 기록, ADR-164 §결정 4·5)이라 본 audit 에 없다.

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
| **Arc B-2** per-branch heartbeat relay(branch→commentId map) | **CFP-2772 (본 Story Phase 2)** | **구현됨** | 같은 mirror 이슈 위 브랜치별 pinned 코멘트. `HEARTBEAT` 토큰 · `heartbeat-format.sh`(progress-format.sh 형제) · `addCommentToJiraIssue` 1종 post+commentId update · **createJiraIssue 없음** · sentinel+deny-scan 재사용 (Arc B-2 섹션, ADR-164 §결정 3) |
| Arc B-2 read-path(staleness 3-state 판정) | **외부 watchdog(별도)** | **비대상** | GitHub Actions cron(`branch-liveness-watchdog.yml`) read-only Jira. 본 skill 은 write-only — 읽지 않음(ADR-164 §결정 4·5) |

> Arc B = comment-only 진행 미러. 사용 도구 = `addCommentToJiraIssue` 1종(post + commentId update). ADR-038 6-point lane 전이 + 현재활동 1줄 입도로 codeforge 진행을 Jira 로 단방향 출력하되, **이슈 생성·status 전이·issue-field write 는 전부 deny 라 호출하지 않는다**(ADR-099 §A1-1 정합). Arc A 의 결정-루프 robustness(poll/dedup/rehydrate/timeout/stale)는 전부 비대상이고, sentinel·deny-scan 만 공유해 같은 control project 를 안전하게 함께 쓴다. **Arc B-2**(CFP-2772 / ADR-164)는 같은 comment-only 불변(같은 `addCommentToJiraIssue` 1종, createJiraIssue 없음, sentinel·deny-scan 재사용) 위에서 단일 `ACTIVITY_COMMENT_ID` 를 **branch→commentId map** 으로 일반화해 병렬 브랜치별 coarse 생존 heartbeat(`HEARTBEAT` 토큰)를 relay 한다 — partial-hang(1/N) 특정용(AC-7). per-branch 코멘트 read·3-state 판정은 별도 외부 watchdog 소관이고, 본 skill 은 여전히 write-only 다.
