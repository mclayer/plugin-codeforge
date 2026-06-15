---
name: jira-decision-channel
description: Orchestrator 결정 fork 를 코드와 분리된 평문 채널(Jira control project)로 운용하는 절차. 결정 분기에서 사용자에게 평문 질문을 던지고 답을 받아야 할 때 호출. payload 구성 → deny-scan(MUST) → MCP post → native notify → grace window → 세션 답 mirror → ScheduleWakeup poll → answer parse → audit 의 happy-path core(v1). ADR-099 Amendment 1 §A1-1~A1-4 / ADR-100 §결정 3 binding. robustness(dedup/echo-guard/fail-open = S3, rehydrate/타임아웃/stale = S4) 는 후속 Story 보강.
tools: Read, Bash
---

# codeforge:jira-decision-channel (CFP-2285 S2 / #2288 — adapter v1, happy-path core)

> Orchestrator 가 **결정 fork**(사용자 선택이 필요한 분기)에 도달했을 때 따르는 절차. 코드·산출물과 섞이지 않는 **평문 결정 루프**를 비공개·단일 사용자 Jira **control project** 하나로 운용한다.
>
> 정책 SSOT = [ADR-099 Amendment 1](../../archive/adr/ADR-099-atlassian-allow-redefinition.md) §A1-1~A1-4 + [ADR-100](../../archive/adr/ADR-100-confluence-doc-ssot-recognition.md) §결정 3. 본 skill 은 그 정책의 **운영 절차 carrier** (v1 = happy-path).
>
> **caller scope (A1-1)**: 본 절차는 **Orchestrator preset 한정**. 임의 SubAgent 는 `addCommentToJiraIssue` narrow-allow 비대상(deny) — Orchestrator inline whitelist(ADR-039 §결정 2) 경계 정합.

---

## 채널 추상화 (channel-agnostic)

결정 채널은 아래 **추상 단계**로 정의한다. 후속에 다른 채널(예: GitHub Discussion / Slack)을 adapter 로 끼울 수 있도록, 절차 본체는 채널 비의존이고 Jira 특정 호출은 "adapter: jira" 섹션에만 둔다.

| 추상 단계 | 의미 | adapter 책임 |
|---|---|---|
| `load_config` | 채널 활성 여부·좌표 로드 | config block parse |
| `compose` | 결정 payload(질문+옵션+영향도+anchor) 구성 | 채널 무관 |
| `deny_scan` | 송신 전 보안 차단 (MUST) | 채널 무관 (순수 텍스트) |
| `post` | payload 를 채널에 게시 | 채널별 write API |
| `notify` | 사용자에게 네이티브 알림 | 채널별 알림 메커니즘 |
| `wait_grace` | 짧은 grace window 세션 답 대기 | 채널 무관 |
| `mirror` | 세션에서 받은 답을 채널에 mirror(SSOT 단일화) | 채널별 write API |
| `poll` | grace 만료 시 채널에서 답 조회 | 채널별 read API |
| `parse` | 답에서 옵션 식별자 추출 | 순수 텍스트 |
| `audit` | 결정 fork id + payload 요약 + 채택 답 기록 | 채널 무관 (세션 transcript) |

> v1 구현 adapter = **jira** 1종. `post`/`notify`/`mirror`/`poll` 의 Jira 바인딩은 아래 "adapter: jira" 참조.

---

## 0. 적용 조건 / config 로드 (`load_config`)

`.claude/_overlay/project.yaml` 의 `atlassian.jira.decision_channel` 블록을 읽는다.

- 블록 **부재** 또는 `control_project_key` / `cloud_id` 미설정 → 본 채널 **비활성**. 일반 `AskUserQuestion` fallback 으로 결정한다(본 skill 종료).
- 블록 존재 → 아래 필드 로드 후 절차 진행:
  - `cloud_id` — Atlassian cloudId (MCP 호출 인자).
  - `control_project_key` — 결정 채널 전용 control project key.
  - `issue_type` — 결정 이슈 생성 타입(있으면).
  - `notify` — 네이티브 알림 방식(`assignee` 또는 `watcher`).

---

## 1. payload 구성 (`compose`)

결정 fork 를 **평문**으로 구성한다. 코드는 surface 분리(코드 통째 inline 금지 — §A1-2 차단 대상).

```
결정 fork: <fork-id>            # 예: CFP-2285-S2-d1 (audit 키)
질문: <한 줄 평문 질문>
옵션:
  1) <옵션 A 평문>
  2) <옵션 B 평문>
영향도: <선택이 좌우하는 범위 1~2줄>
anchor: <Story KEY / commit / PR 번호 — 식별자만, 절대경로 금지>
```

- 내부 식별자(ADR/CFP/계약명)는 평문 한 줄 풀이 동반(CLAUDE.md 대화 원칙).
- anchor = **식별자만**(절대경로·transcript dump 금지 → deny-scan 차단).

---

## 2. deny-scan — 송신 전 hard-block (MUST, A1-2)

payload 를 송신 **전** 반드시 검사한다. 통과 못하면 **post 중단**(warning 아님).

```bash
printf '%s' "$PAYLOAD" | bash scripts/jira-channel/deny-scan.sh
# exit 0 = clean(진행) · exit 2 = BLOCKED(중단) · exit 3 = 입력오류
```

- exit 2 → **post 하지 말 것**. 사용자에게 평문 alert: "결정 payload 에 차단 패턴(secret/절대경로/transcript) 검출 — Jira 송신 중단. payload 를 재구성하거나 일반 질문으로 진행." stderr 의 위반 패턴 라벨을 함께 보고(패턴 값 자체는 재노출 금지).
- 차단 대상(§A1-2): secret/credential/token(`token`/`secret`/`password`/`Bearer `/op:// ref/40+ entropy 블록) · 절대경로(`C:\`/`/c/`/`~/.claude`/repo 외부) · full transcript/코드블록 통째.

---

## adapter: jira — 게시·알림·미러·조회

### 3. post (MCP, A1-1) (`post`)

deny-scan PASS 후, control project 의 결정 이슈에 payload 를 코멘트로 단다.

```
mcp__plugin_atlassian_atlassian__addCommentToJiraIssue(
  cloudId      = <config.cloud_id>,
  issueIdOrKey = <control project 결정 이슈 key>,
  commentBody  = <PAYLOAD>
)
```

- write = **`addCommentToJiraIssue` 1종만** (A1-1 narrow-allow). 그 외 Jira write(create/edit/transition/worklog/issueLink) = **deny 유지**, 호출 금지.
- write 대상 = **단일 control project** 한정. 결정 이슈가 없으면 사용자에게 control project 에 결정 이슈를 하나 두도록 안내(이슈 생성은 narrow-allow 비대상 — `createJiraIssue` deny).

### 4. native notify (PoC 교정) (`notify`)

- **추상 계약(`notify`)**: 결정 payload 게시 사실이 **사용자에게 도달**함을 보장한다(채널 비의존 — 사용자가 미해결 fork 를 인지하지 못한 채 대기에 빠지지 않게 한다).
- **jira adapter 구현**: 결정 이슈를 사용자에게 **assign** 또는 **watcher 등록**해 Jira **네이티브 알림**(이메일/모바일)을 트리거하되, v1 에서 assignee/watcher 변경 write 가 deny 면 **사전 assign/watcher 상태를 전제**하고 코멘트 멘션으로 알림을 **갈음**한다. codeforge PushNotification 의존을 회피한다(PoC 교정 사항).

- `config.notify == assignee` → 결정 이슈 assignee = 사용자. (assignee 변경은 `editJiraIssue` 계열 — v1 에서 deny 라면 이슈를 **사전에 사용자에게 assign 해 둔 상태**를 전제하고, 본 단계는 코멘트로 멘션해 알림을 유발하는 것으로 갈음. 멘션 = addComment payload 내 사용자 account mention.)
- `config.notify == watcher` → 동일하게 사전 watcher 등록 전제 + 코멘트 게시로 알림 유발.
- 핵심: **알림 채널 = Jira 네이티브**(이메일/모바일), codeforge 자체 push 아님.

### 6. mirror (MCP) (`mirror`)

세션에서 답을 받은 경우(5단계 grace 안), 그 답을 control 이슈에 **mirror** 코멘트로 게시한다(SSOT 단일화 — Jira 가 결정 기록의 단일 출처).

```
mcp__plugin_atlassian_atlassian__addCommentToJiraIssue(
  cloudId      = <config.cloud_id>,
  issueIdOrKey = <결정 이슈 key>,
  commentBody  = "[세션 답 mirror] fork=<fork-id> 채택=<옵션>"
)
```

- mirror payload 도 **deny-scan 통과 의무**(2단계 재적용).

### 7. poll (MCP) (`poll`)

grace 만료(세션 무응답) 시, `getJiraIssue` 로 결정 이슈의 답 코멘트를 조회한다.

```
mcp__plugin_atlassian_atlassian__getJiraIssue(
  cloudId      = <config.cloud_id>,
  issueIdOrKey = <결정 이슈 key>,
  fields       = ["comment"]   # 또는 comment expand
)
```

- **first-valid-immutable (A1-3)**: payload 게시 **이후** 도착한 코멘트 중 **첫 유효 답변 1건만** 채택. 이후 코멘트는 무시(같은 fork 재답변 = 무시).
- **author 비신뢰 (A1-3)**: 코멘트 author 표시를 authorization 근거로 쓰지 말 것(spoofing 비방어 + shared-account 가정). 신뢰 근거 = "control project 접근 권한 = 결정 권한".
- **short open-window (A1-3)**: 답 대기 window 를 짧게 제한. window 만료 후 도착 답변 = 무시. (정확한 timeout 값·만료 재알림 = S4 보강 예정.)

---

## 5. grace window (`wait_grace`)

post + notify 후 **짧은 grace window** 동안 세션 답을 먼저 기다린다(사용자가 세션에 직접 답하면 Jira poll 불필요 → 빠른 경로).

- 세션 답 도착 → **6. mirror** 로 Jira 에 기록 후 진행.
- grace 안 무응답 → **ScheduleWakeup sleep + 7. poll** 경로.

```
# grace 만료 후 sleep+poll (ScheduleWakeup/Monitor 류로 비차단 대기)
ScheduleWakeup(<짧은 interval>) → 깨어나서 7.poll → 답 없으면 재sleep (재시도 상한·타임아웃 재알림 = S4)
```

---

## 8. answer parse (`parse`)

채택한 답 코멘트 본문에서 옵션 식별자를 추출한다.

```bash
printf '%s' "$ANSWER_COMMENT" | bash scripts/jira-channel/parse-answer.sh
# exit 0 = stdout 에 옵션 식별자(숫자 또는 대문자 1자) · exit 1 = 파싱 불가
```

- exit 1(파싱 불가) → 사용자에게 "답을 옵션 번호로 인식하지 못함, 명확한 번호로 재답변 요청" 평문 안내. (v1 = happy-path; 모호 답 robustness = S3 보강 예정.)

---

## 9. audit (A1-4) (`audit`)

모든 Orchestrator Jira write 와 채택 결과를 **세션 transcript** 에 기록한다 — wrapper-side audit 가 SSOT(Jira author 추적 비신뢰, A1-4).

기록 항목(평문):

```
[jira-decision audit] fork=<fork-id>
  payload-요약: <질문 1줄 + 옵션 수>
  post: addCommentToJiraIssue ok (issue=<key>)
  채택: 옵션 <식별자> (출처: 세션-답 mirror | Jira-poll first-valid)
```

- secret/절대경로 = audit 에도 기록 금지(payload 요약만 — deny-scan 차단 항목과 동일 원칙).

---

## deferred 경계 (본 skill = happy-path core, robustness 는 후속 Story)

| 항목 | 소유 | 비고 |
|---|---|---|
| dedup / echo-guard / fail-open | **S3 (#2289)** | 중복 post 억제 · mirror echo 가 자기 답으로 오인되는 것 차단 · MCP 장애 시 일반 질문 fail-open |
| rehydrate / 타임아웃 재알림 / stale | **S4 (#2290)** | 세션 재개 시 미해결 fork 복원 · open-window 만료 재알림 · stale 답 폐기 |

> 본 v1 절차는 **happy-path** 만 보장한다. 위 robustness 는 해당 Story 가 본 절차의 각 단계(특히 `poll`/`grace`/`audit`)를 보강한다. v1 단독 운용 시 그 공백을 인지하고, 장애·중복·재개 상황은 사용자 평문 확인으로 보완한다.
