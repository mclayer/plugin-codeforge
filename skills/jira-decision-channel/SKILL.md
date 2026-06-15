---
name: jira-decision-channel
description: Orchestrator 결정 fork 를 코드와 분리된 평문 채널(Jira control project)로 운용하는 절차. 결정 분기에서 사용자에게 평문 질문을 던지고 답을 받아야 할 때 호출. payload 구성 → deny-scan(MUST) → MCP post(sentinel) → native notify → grace window → 세션 답 mirror(sentinel) → ScheduleWakeup poll(echo-guard 필터 + first-valid-immutable) → answer parse → PROCESSED 마킹(dedup) → audit. S3(#2289) echo-guard/dedup/fail-open + S4(#2290) rehydrate(at-least-once 복구)/타임아웃 재알림(자동결정 금지)/stale anchor 재확인 robustness 보강. ADR-099 Amendment 1 §A1-1~A1-4 / ADR-100 §결정 3 binding.
tools: Read, Bash
---

# codeforge:jira-decision-channel (CFP-2285 S4 / #2290 — robustness: rehydrate / 타임아웃 재알림 / stale anchor)

> Orchestrator 가 **결정 fork**(사용자 선택이 필요한 분기)에 도달했을 때 따르는 절차. 코드·산출물과 섞이지 않는 **평문 결정 루프**를 비공개·단일 사용자 Jira **control project** 하나로 운용한다.
>
> 정책 SSOT = [ADR-099 Amendment 1](../../archive/adr/ADR-099-atlassian-allow-redefinition.md) §A1-1~A1-4 + [ADR-100](../../archive/adr/ADR-100-confluence-doc-ssot-recognition.md) §결정 3. 본 skill 은 그 정책의 **운영 절차 carrier** (S2 happy-path core + S3 echo-guard/dedup/fail-open + S4 rehydrate/타임아웃 재알림/stale anchor robustness).
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

## echo-guard sentinel (S3 — self-echo 차단 SSOT)

orchestrator 가 채널에 쓰는 **모든** 코멘트(결정 post / 세션답 mirror / PROCESSED 마커)에는 본문 **선두**에 distinctive sentinel `⟦cf-orch⟧` 를 박는다. 폴러는 `poll` 단계에서 각 코멘트를 `echo-guard.sh` 로 필터해 **sentinel 포함분(=orchestrator-authored)을 답변 후보에서 제외**한다.

- **왜 내용 마커인가 (author 아님)**: PoC 실측 — MCP `addCommentToJiraIssue` 는 사용자 본인 계정으로 write 라 코멘트 author 로 "orchestrator 코멘트" vs "사용자 답변" 을 구분할 수 없다(§A1-3 author 비신뢰). 그래서 식별은 **내용 sentinel** 로 한다.
- **sentinel SSOT = `scripts/jira-channel/echo-guard.sh` 의 `CF_ORCH_SENTINEL` 상수**. 본 문서의 sentinel 표기 `⟦cf-orch⟧` 는 그 상수와 **byte-동일**해야 한다(불일치 시 echo-guard 가 orchestrator 코멘트를 못 걸러 self-echo 루프 발생).

```bash
printf '%s' "$COMMENT_BODY" | bash scripts/jira-channel/echo-guard.sh
# exit 0 = skip(orchestrator-authored, 답변 후보 제외) · exit 1 = candidate(user 답변 후보) · exit 3 = 빈 입력/파일 미존재
```

> **self-echo 루프 차단 보장**: orchestrator 가 쓴 mirror·PROCESSED 마커는 모두 sentinel 을 포함하므로, 다음 `poll` 에서 echo-guard 가 exit 0(skip)으로 걸러낸다 → orchestrator 자신의 코멘트가 "사용자 답변" 으로 재섭취되는 무한 루프가 구조적으로 발생하지 않는다.

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
  commentBody  = "⟦cf-orch⟧ " + <PAYLOAD>     # 선두 sentinel (echo-guard SSOT)
)
```

- **sentinel 선두 박기 (S3)**: post 코멘트 본문 선두에 sentinel `⟦cf-orch⟧` 를 붙인다(echo-guard sentinel 절). 이 결정 post 자체가 다음 `poll` 에서 답변 후보로 오인되지 않게 한다.
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
  commentBody  = "⟦cf-orch⟧ [세션 답 mirror] fork=<fork-id> 채택=<옵션>"   # 선두 sentinel
)
```

- **sentinel 선두 박기 (S3)**: mirror 코멘트도 sentinel `⟦cf-orch⟧` 를 선두에 붙인다. 이 mirror 가 다음 `poll` 에서 echo-guard 로 걸러져 자기 답으로 재섭취되지 않게 한다(self-echo 차단).
- mirror payload 도 **deny-scan 통과 의무**(2단계 재적용).
- **fail-open (mirror write 실패, S3)**: `addCommentToJiraIssue` MCP 호출이 실패해도 **로컬 결정 흐름을 차단하지 말 것**. 세션에서 이미 받은 in-memory 답으로 그대로 진행(resume 차단 금지)하고, ① 백그라운드 재시도 큐에 mirror 재게시를 표기하고, ② 9단계 audit 에 `mirror-gap warning` 을 기록해 Jira 결정 로그 결손을 surface 한다. mirror 는 SSOT **기록** 수단이지 결정 **게이트**가 아니다 — 답은 이미 세션에서 확정됐다.
- **fail-open 등급 분리 (P2-2)**: mirror write fail 과 PROCESSED(§7(e)) write fail 은 **무게가 다르다**. mirror fail = 단순 **기록 결손**(`mirror-gap`, 무해 — 답은 세션 확정). PROCESSED(dedup ledger) write fail 은 **더 무겁다** — 마커 부재로 다음 `poll` 에서 (a) 선제 검사가 통과해 **동일 답을 재채택할 수 있다(double-process 위험)**. 따라서 audit warning 도 두 등급을 구분 기록한다: `mirror-gap`(무해) vs `dedup-ledger-gap: 재처리 위험`.

### 7. poll (MCP) (`poll`)

grace 만료(세션 무응답) 시, `getJiraIssue` 로 결정 이슈의 답 코멘트를 조회한다.

```
mcp__plugin_atlassian_atlassian__getJiraIssue(
  cloudId      = <config.cloud_id>,
  issueIdOrKey = <결정 이슈 key>,
  fields       = ["comment"]   # 또는 comment expand
)
```

조회한 코멘트 목록에 아래 **선별 파이프라인**을 적용한다(S3 구현).

**(a) dedup 선제 검사 (PROCESSED 마킹, before side effect)** — poll 진입 시 가장 먼저:

- 코멘트 중 `⟦cf-orch⟧ PROCESSED decision=<fork-id>` 마커가 **이미 존재**하면 → 이 fork 는 **이미 처리됨**. 재섭취·재mirror·재PROCESSED-post 를 모두 억제하고 본 절차를 종료(crash-restart 안전 — 답 채택 후 resume 직전에 부작용보다 **먼저** 마킹하므로, 재진입 시 중복 처리가 구조적으로 차단된다).
- PROCESSED 마커 부재 → (b) 로 진행.

**(b) echo-guard 필터** — 각 코멘트 본문을 `echo-guard.sh` 로 판정:

```bash
printf '%s' "$COMMENT_BODY" | bash scripts/jira-channel/echo-guard.sh
# exit 0 = skip(선두 sentinel = orchestrator post/mirror/PROCESSED) · exit 1 = candidate(user 답변) · exit 3 = 빈/공백 코멘트·입력오류
```

- exit 0(skip) 코멘트 = orchestrator 자신이 쓴 결정 post / mirror / PROCESSED 마커 → **답변 후보에서 제외**. (self-echo 차단 — 자기 코멘트를 답으로 오인하지 않는다.)
- exit 1(candidate) 코멘트만 답변 후보로 남긴다.
- **exit 3(빈/공백 코멘트 또는 입력오류, P3)** = `echo-guard.sh`(또는 8단계 `parse-answer.sh`)가 판정 불가로 반환한 코멘트 → **candidate 아님(skip)** 으로 취급한다. 빈 코멘트가 답변 후보로 잘못 남거나 fork 를 잠그지 않는다.

**(c) ordering = first-valid-immutable (A1-3, Jira `created` 단일 기준)**:

- (b) 통과 후보를 Jira `created` 타임스탬프 **오름차순** 정렬한다(채널이 제공하는 단일 신뢰 시각 — 로컬 clock·author 비신뢰).
- payload **post 시각 이후** 도착분만 대상으로, 앞에서부터 `parse-answer.sh`(8단계) 를 적용해 **첫 parse 성공 1건**을 채택한다.
- 채택 후 **이후 코멘트는 무시(immutable)** — 같은 fork 재답변·번복 = 무시.

**(d) author 비신뢰 (A1-3)**: 코멘트 author 표시를 authorization 근거로 쓰지 말 것(spoofing 비방어 + shared-account 가정). 신뢰 근거 = "control project 접근 권한 = 결정 권한".

**(e) 답 채택 직후 PROCESSED 마킹 (dedup, before resume side effect)**:

```
mcp__plugin_atlassian_atlassian__addCommentToJiraIssue(
  cloudId      = <config.cloud_id>,
  issueIdOrKey = <결정 이슈 key>,
  commentBody  = "⟦cf-orch⟧ PROCESSED decision=<fork-id> answer=<옵션> ts=<KST ISO8601>"
)
```

- 답을 채택하면 **resume(부작용) 직전에** 위 PROCESSED 마커를 post 한다(side effect 전 마킹 → crash-restart 시 (a) 가 중복 처리를 차단). sentinel 포함이므로 다음 poll 에서 echo-guard 로 걸러진다(self-echo 안전).
- **crash-safety 비대칭 명문화 (P2-1) + S4 해소**: PROCESSED 마커 post → resume 순서는 **double-process 를 막는다**(at-most-once). 그러나 **PROCESSED post 성공 직후·resume 전 crash** 시에는 결정이 마킹만 된 채 act 되지 않아 **silently drop(at-most-once)** 된다 — 즉 이 순서는 중복 처리는 막지만 누락은 막지 못한다. 미act 결정을 재개하는 **at-least-once 복구 = S4 rehydrate(#2290, §10)** 가 메운다 — 세션 재개 시 PROCESSED 마커 없는 미해결 fork 를 복원해 이 at-most-once drop window 를 닫는다(비대칭 해소).
- PROCESSED 마커도 **fail-open** — post 실패 시 결정 흐름 차단 금지(in-memory 답으로 진행 + 재시도 큐 표기 + audit `dedup-ledger-gap warning: 재처리 위험`). 단 이 경우 crash-restart 중복 차단은 약화되므로(double-process 위험) audit 에 명시한다.

- **short open-window (A1-3) + S4 타임아웃 재알림**: 답 대기 window 를 짧게 제한. window 만료 후 도착 답변 = 무시. 다만 **무한 대기 중 미응답**은 자동 결정으로 종결하지 않고 **재알림(escalation)** 으로만 ping 한다 — 정확한 timeout 임계·escalation 스케줄·자동결정 금지 = **S4(#2290, §11)**. **stale anchor 재확인**(늦은 답 + 대상 변경) = **S4(#2290, §12)**.

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

- exit 1(파싱 불가) → 사용자에게 "답을 옵션 번호로 인식하지 못함, 명확한 번호로 재답변 요청" 평문 안내. 파싱 불가 코멘트는 채택되지 않으므로 `poll` 의 first-valid-immutable 은 **다음 후보**로 계속 진행한다(파싱 실패 1건이 fork 를 잠그지 않음).

---

## 9. audit (A1-4) (`audit`)

모든 Orchestrator Jira write 와 채택 결과를 **세션 transcript** 에 기록한다 — wrapper-side audit 가 SSOT(Jira author 추적 비신뢰, A1-4).

기록 항목(평문):

```
[jira-decision audit] fork=<fork-id>
  payload-요약: <질문 1줄 + 옵션 수>
  post: addCommentToJiraIssue ok (issue=<key>, sentinel=⟦cf-orch⟧)
  채택: 옵션 <식별자> (출처: 세션-답 mirror | Jira-poll first-valid)
  dedup: PROCESSED 마킹 ok (resume 전) | mirror-gap warning | dedup-ledger-gap warning: 재처리 위험
```

- secret/절대경로 = audit 에도 기록 금지(payload 요약만 — deny-scan 차단 항목과 동일 원칙).
- **fail-open warning 기록 (S3)**: mirror 또는 PROCESSED 마커 post 가 실패했으면 audit 에 등급 구분 warning(`mirror-gap`=무해 / `dedup-ledger-gap: 재처리 위험`=double-process 위험, P2-2)을 남겨 Jira 결정 로그 결손을 surface 한다(흐름은 차단하지 않되 결손은 가시화 — wrapper-side audit 가 SSOT).

---

## 10. rehydrate (at-least-once 복구, S4) (`rehydrate`)

세션 시작/재개 시 **미해결 결정 fork** 를 Jira 에서 복원한다. Jira = durable store 라 미act 결정을 복원할 수 있다(§7 poll(e) 의 at-most-once drop window 를 메우는 짝 — crash-safety 비대칭 해소).

연계: 세션 resume 절차([`codeforge:session-recovery`](session-recovery))가 활성 Story 복원 시 본 rehydrate 를 1회 호출한다(미해결 fork 도 활성 Story 와 함께 복원 대상).

**복원 판정 (PROCESSED 마커 부재 = 미해결)**:

1. control 결정 이슈를 `getJiraIssue`(§7 poll 와 동일 호출, `fields=["comment"]`)로 조회한다.
2. 코멘트 중 **결정 post**(sentinel `⟦cf-orch⟧` 포함 + payload 형태 `결정 fork: <id>`)를 식별하고, 각 fork id 에 대응하는 `⟦cf-orch⟧ PROCESSED decision=<id>` 마커가 **있는지** 검사한다.
3. PROCESSED 마커가 **없는** 결정 post = **미해결 fork**(답 미채택 또는 채택 후 resume 전 crash drop). 각각을 **§7 poll 로 재진입**(복원)한다 — poll(a) 선제 검사가 다시 마커 부재를 확인하고, poll(b)~(e) 로 답 후보 선별·채택·PROCESSED 마킹을 정상 수행한다.

- **echo-guard 정합 (self-post 오인 방지)**: rehydrate 가 재진입한 §7 poll 의 (b) echo-guard 필터가 orchestrator 자신의 결정 post / mirror / PROCESSED 마커(모두 sentinel 선두)를 답변 후보에서 제외하므로, rehydrate 가 self-post 를 "사용자 답" 으로 오인하지 않는다.
- **idempotent**: PROCESSED 마커가 이미 있는 fork 는 미해결 목록에서 제외되므로, rehydrate 를 여러 번 호출해도 이미 처리된 fork 를 재처리하지 않는다(poll(a) dedup 과 동일 ledger 사용).
- **crash-safety 비대칭 해소**: §7 poll(e) 의 "PROCESSED post 직후·resume 전 crash → silent drop(at-most-once)" 비대칭을, rehydrate 가 **세션 재개 시** 미해결 fork 복원으로 at-least-once 를 보장해 닫는다(S3 §7(e) P2-1 이 S4 소관으로 명시한 짝).

---

## 11. 타임아웃 재알림 (escalation, 자동결정 금지, S4) (`escalate`)

open-window 만료 후에도 미응답이면 **재알림(escalation)만** 하고 **절대 자동 결정하지 않는다**(사용자 확정 결정 — `auto_decide_on_timeout: false`). 무한 대기하되 escalation interval 로 ping 해 미해결 fork 가 사용자 시야에서 사라지지 않게 한다.

**타임스탬프 기록**: 결정 post 시점에 post 시각을 audit/payload 에 기록한다(escalation 임계 계산 기준). 신뢰 시각 = Jira `created`(§7 poll(c) 와 동일 — 로컬 clock 비신뢰).

**매 wakeup poll 에서 (§5 grace → §7 poll 경로)**:

1. `(now − post_ts) > timeout_minutes`(config) AND 해당 fork 미응답(PROCESSED 마커 부재) → **재알림**.
2. 재알림 = 결정 이슈에 mention 재코멘트(또는 재assign)를 **sentinel 포함** 으로 post:
   ```
   mcp__plugin_atlassian_atlassian__addCommentToJiraIssue(
     cloudId      = <config.cloud_id>,
     issueIdOrKey = <결정 이슈 key>,
     commentBody  = "⟦cf-orch⟧ [재알림] fork=<fork-id> 미응답 <경과>분 경과 — 결정 대기 중 @<user>"  # 선두 sentinel
   )
   ```
3. **escalation 스케줄**: config `escalation.intervals_minutes`(예: `[60, 240, 1440]`)에 따라 점증 interval 로 재알림 — 초반 자주, 이후 드물게 ping. interval 소진 후에는 마지막 interval 을 유지(무한 ping, 자동 결정 없음).
   - **interval 기준점 (오해 제거)**: `timeout_minutes`(예: 1440) = **첫 재알림까지의 지연**(post 시각 → 첫 ping). `escalation.intervals_minutes`[60,240,1440] = **첫 재알림(=timeout 도달) 시점부터** 점증하는 ping **간격**이다(post 시각 기준 누적 오프셋 아님). 즉 첫 ping = post+`timeout_minutes`, 둘째 ping = 첫 ping+60분, 셋째 = +240분, 넷째부터 = +1440분 고정. intervals 는 `post_ts` 가 아니라 **직전 재알림 시각**을 기준으로 더한다.
4. 재알림 후에도 **결정 흐름은 계속 대기** — escalation 은 알림일 뿐 결정 종결이 아니다. 답이 도착하면 §7 poll 이 정상 채택한다.

- **자동결정 절대 금지 (사용자 확정)**: timeout 도달은 **어떤 옵션도 자동 선택하지 않는다**. `auto_decide_on_timeout: false`(config 박제). timeout = 재알림 trigger 일 뿐, 결정은 끝까지 사용자 몫이다.
- **echo-guard 정합**: 재알림 코멘트도 sentinel `⟦cf-orch⟧` 를 선두에 박으므로, 다음 §7 poll(b) echo-guard 가 exit 0(skip)으로 걸러 자기 재알림을 "사용자 답" 으로 오인하지 않는다(self-echo 안전 — escalation 코멘트가 답 후보로 재섭취되지 않음).
- **deny-scan 정합**: 재알림 payload 도 §2 deny-scan 통과 의무(fork-id·경과시간·mention 만 — secret/절대경로 금지).

---

## 12. stale anchor 재확인 (자동 적용 금지, S4) (`anchor-recheck`)

답이 **늦게** 도착했는데 그 사이 결정 **대상(anchor)** 이 바뀌었으면(squash-merge 로 commit SHA 교체 / Story closed 등), 그 답을 **자동 적용하지 않고 사용자에게 재확인**한다.

**답 채택 직전**(§7 poll(e) PROCESSED 마킹·resume **전**) anchor 유효성을 검사한다. **anchor type 에 따라 호출 형태를 분기**해 모든 anchor type 이 stale 검사를 거치게 한다(§1 anchor 필드 L78 형식 `<Story KEY / commit / PR 번호 — 식별자만>` 와 정합):

```bash
# anchor 에 commit 이 있으면 commit(+story 있으면 함께) 검사:
bash scripts/jira-channel/anchor-check.sh <commit-SHA> [<story-key>]
# commit 이 없고 story/PR-only anchor 면 빈 commit + story 로 호출(story-only 검사):
bash scripts/jira-channel/anchor-check.sh "" <story-key>
# exit 0 = anchor valid(자동 적용 가능) · exit 2 = stale(commit 부재 또는 story closed) · exit 3 = 입력오류(commit·story 둘 다 빔)
```

- **anchor type 분기 (모든 anchor 가 검사를 거침)**:
  - anchor 에 **commit 식별자**가 있으면 → `anchor-check.sh <commit> [<story>]`(commit 존재 + story 있으면 AND 검사).
  - anchor 가 **commit 없이 Story KEY / PR 번호만**이면 → `anchor-check.sh "" <story>`(commit 검사 생략, story open 만 검사). 빈 commit + story-only 호출은 closed→exit2 / open→exit0 으로 동작한다.
  - 이렇게 분기하면 commit anchor 든 story/PR-only anchor 든 **모두 stale 검사를 거친다**(과거 commit 필수라 story-only anchor 가 무검사 통과하던 공백을 막음).
- **exit 0 (valid)** → 정상 적용. §7 poll(e) PROCESSED 마킹 후 resume.
- **exit 2 (stale)** → **자동 적용 금지**. 대신 **재확인 결정 post**(새 fork)를 사용자에게 되묻는다:
  ```
  결정 fork: <원fork-id>-recheck
  질문: 대상 anchor(<commit/story>)가 변경됨(commit 부재 또는 story closed). 이 답을 그대로 적용할지 재확인.
  옵션:
    1) 적용 (변경 인지하고 원답 유지)
    2) 재검토 (새 상황에 맞춰 다시 결정)
  영향도: stale 대상에 원답 자동 적용 시 잘못된 commit/closed Story 에 결정 반영 위험.
  anchor: <갱신된 commit/story 식별자>
  ```
  - 이 재확인 post 도 §2 deny-scan → §3 post(sentinel) → §7 poll 정상 루프를 탄다(원 fork 와 별개의 새 fork 로 처리).
- **exit 3 (입력오류)** → commit·story 가 **둘 다** 비었음(검사 대상 없음). anchor 식별자를 보강해 재호출(검사 생략 금지 — 무검사 자동 적용 회피). anchor type 분기상 최소 commit 또는 story 중 하나는 항상 주어져야 한다.
- **graceful degrade**: `anchor-check.sh` 는 gh 미가용/미인증/조회실패 시 story open 검사를 생략하고 warning 을 stderr 로 남긴다(channel 가용성 우선 — false-stale 0). commit 이 있으면 commit 검사로 판정하고, story-only 호출(빈 commit)에서 gh 가 degrade 하면 valid 로 통과시킨다(검사 불가 시 자동 적용 차단보다 채널 흐름 우선). repo 는 origin remote 또는 `OWNER/REPO#번호` 형식에서 도출하며, 도출 실패 시에도 degrade. warning 은 audit 에 기록.

---

## deferred 경계 (robustness 구현 진척 + 잔여 후속 Story)

| 항목 | 소유 | 상태 | 비고 |
|---|---|---|---|
| echo-guard (self-echo 차단) | **S3 (#2289)** | **구현됨** | sentinel `⟦cf-orch⟧` 내용 마커 + `echo-guard.sh` 폴러 필터. orchestrator 코멘트(post/mirror/PROCESSED)가 자기 답으로 재섭취되지 않음 (echo-guard sentinel 절 + §7 poll(b)) |
| dedup (중복 처리 억제) | **S3 (#2289)** | **구현됨** | dedup ledger = Jira 자체(durable). `⟦cf-orch⟧ PROCESSED decision=<fork>` 마커를 resume 부작용 **전** post → 재진입 시 (a) 선제 검사로 중복 차단(crash-restart 안전) (§7 poll(a)/(e)) |
| fail-open (mirror/mark 장애) | **S3 (#2289)** | **구현됨** | mirror·PROCESSED post 실패 시 로컬 흐름 차단 금지 — in-memory 답 진행 + 재시도 큐 + audit `*-gap warning` (§6 mirror / §7 poll(e) / §9 audit) |
| rehydrate (at-least-once 복구) | **S4 (#2290)** | **구현됨** | 세션 재개 시 PROCESSED 마커 없는 미해결 fork 를 §7 poll 로 복원 — §7 poll(e) at-most-once drop 비대칭 해소. echo-guard 로 self-post 오인 방지. `codeforge:session-recovery` 연계 (§10) |
| 타임아웃 재알림 (자동결정 금지) | **S4 (#2290)** | **구현됨** | open-window 만료·미응답 시 sentinel 포함 escalation 코멘트로 점증 interval ping. **자동 결정 절대 안 함**(`auto_decide_on_timeout: false`, 사용자 확정). 무한 대기+재알림만 (§11) |
| stale anchor 재확인 | **S4 (#2290)** | **구현됨** | 답 채택 직전 `anchor-check.sh <commit> <story>` 호출 — exit 2(commit 부재/story closed)면 자동 적용 대신 재확인 결정 post 로 사용자에게 되물음 (§12) |

> S2 happy-path core 위에 S3 가 echo-guard/dedup/fail-open robustness 를, S4 가 rehydrate(at-least-once 복구)/타임아웃 재알림(자동결정 금지)/stale anchor 재확인 robustness 를 `post`/`mirror`/`poll`/`audit`/`rehydrate`/`escalate`/`anchor-recheck` 단계에 보강해 채널 robustness 가 완결됐다. 타임아웃은 끝까지 **자동 결정하지 않고 재알림만** 하며(사용자 확정), stale 대상에는 답을 자동 적용하지 않고 재확인한다.
