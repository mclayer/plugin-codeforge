---
adr_number: 99
title: check-no-atlassian.sh 역전 + Atlassian-allow 재정의 — v0.7→v0.8 Atlassian 제거 reversal 의 mechanical guard 전환
status: Accepted
category: governance
date: 2026-05-21
carrier_story: CFP-1147
parent_epic: CFP-1146
related_stories:
  - CFP-1147     # 본 carrier (Epic-A Wave 1 Story-1, hard prerequisite — 모든 후속 Wave 선결)
  - CFP-1146     # umbrella Epic-A (Atlassian suite 재결합 governance reversal)
related_adrs:
  - ADR-102      # ratchet 약화 극복 governance anchor (S4) — 본 lint 역전 = Atlassian-allow ratchet 약화 방향 정당화 위임 (ADR-058 §결정 5 일반 sunset_justification 3-tuple 경로 — ADR-097 면제 channel 비대상, §결정 4-A). ADR-102 = extend (ADR-095 metric reuse + ADR-097 개념 cross-ref + spec-level reversal mechanism 신설)
  - ADR-097      # paradigm replacement governance anchor — 면제 channel 발동 자격 평가 대상이나 §결정 4-A 결론 = 비대상 (closed-set AND 조건 a 9+ ADR sunset 미충족, predecessor formal ADR 0건). carrier-preserved sunset 개념(§결정 3)만 cross-ref 차용
  - ADR-095      # 9 ADR sunset metric 표준화 — S4 ADR-102 가 sunset_justification metric 영역 형식 reuse (changelog mining + cron, GA baseline)
  - ADR-070      # verify-before-trust (외부 worker output) — §결정 5 MCP endpoint 응답 변조 boundary 검증 책임 (ADR-101 ground-truth verify 정합)
  - ADR-064      # decision principle mandate — §self-application top-down ratchet (약화 차단 원칙 — 본 ADR 단독 약화 불가, S4 연계 의무)
  - ADR-058      # ADR sunset criteria mandate — §결정 5 일반 sunset_justification 3-tuple (ratchet 약화 정당화 의무 carrier, ADR-097 면제 channel 비대상 경로)
  - ADR-060      # evidence-enforceable promotion framework — check-no-atlassian registry 등록 보류 (owner_adr 부재) 해소 — 본 ADR 이 owner_adr 부여
  - ADR-027      # consumer adoption protocol — §결정 5 atlassian.* schema (token secret 평문 mount 금지, env/secret store 경유) 정합
  - ADR-013      # codeforge family dogfood-out — Confluence doc SSOT 재인정 (ADR-100) 의 predecessor governance layer
related_files:
  - scripts/check-no-atlassian.sh                                                # 본 ADR 의 mechanical 대상 — 역전/재정의
  - CHANGELOG.md                                                                 # v0.8 Atlassian 제거 history + v0.x Atlassian 재결합 reversal 기록
  - docs/superpowers/specs/2026-04-25-atlassian-to-github-migration-design.md     # predecessor — v0.7→v0.8 Atlassian 완전 제거(hard remove) 결정 spec
  - docs/adr/ADR-RESERVATION.md                                                  # row 99 reserved → active 전환
mechanical_enforcement_actions:
  - check-atlassian-allow   # §결정 1 Layer 2 (lint grep 평문 allowlist) 의 mechanical action 명 (declaration-only Wave 1 — 실 wire = S1 Phase 2 또는 후속 carrier, ADR-082 §결정 6 retain pattern). Layer 1 (mcp__atlassian permission deny) 은 settings.json + agent preset enforce — lint mechanical action 영역 외 (SSOT 분리, §결정 1/2)
is_transitional: false   # permanent governance — Atlassian 재결합 후 lint 역전 (2-layer) 은 영구 정책 방향. 단 Layer 2 평문 allowlist 확장이 ratchet 약화 방향이므로 S4 ADR-102 sunset_justification 으로 정당화 (frontmatter is_transitional 과 별개 layer — 약화 정당화는 ADR-102 carrier, ADR-058 §결정 5 일반 경로 / ADR-097 면제 channel 비대상)
sunset_justification: null   # is_transitional false — 본 ADR 의 lint 역전 (2-layer) 결정은 영구. 단 "predecessor v0.8 제거 결정의 효력 약화" 자체의 정당화는 S4 ADR-102 §sunset_justification 3-tuple (ADR-058 §결정 5 일반 경로) 에 위임 (§결정 4/4-A cross-ref). ADR-097 면제 channel 비대상 (조건 a 미충족)
amendment_log:
  - amendment_id: 1
    carrier_story: CFP-2285   # S1 (#2287) — Epic CFP-2285 (wrapper-self dogfood: Jira 결정 채널 governance)
    parent_epic: CFP-2285
    date: 2026-06-15  # KST per ADR-079 §결정 2
    decisions_touched: ["§결정 1", "§결정 2", "§결정 5", "§해소 기준"]
    nature: ratchet-weakening   # Layer 1 deny 집합에서 addCommentToJiraIssue 1종 narrow-allow 로 이동 = Layer 1 약화 방향 (ADR-058 §결정 5 post-CFP-1149 evidence-gate 경로 — 약화 evidence 3-tuple 제시 시 1급 허용)
    sunset_justification:
      metric: "incident_count(무단/scope-외 Jira write) AND payload-leak_count(secret/path/transcript Jira 송신) 2-source closed-set (ADR-095 §결정 1 형식 reuse — changelog mining + wrapper-side audit log mining). baseline = 협업자/멀티테넌트 trigger 부재 유지(단일 사용자 비공개 control project 신뢰 경계 불변) AND 두 metric 0 유지 시 narrow-allow 효용 lossless 확인."
      who: "DesignReviewPL(설계리뷰 lane MUST flag) + SecurityTestPL(보안테스트 lane) + Orchestrator(wrapper-side audit log SSOT 보유 주체). 협업자 신규 발생 시 본 amendment trigger 평가 = SecurityArch."
      how: "wrapper-side 세션 transcript audit log (결정 fork id + payload 요약 + first-valid-immutable 채택 기록) 를 SSOT 로 incident/leak 0 검증. 1-step revert(narrow-allow 에서 addCommentToJiraIssue 제거 → deny 원복) 보유 = 약화 가역성 보장. 강한 인증(nonce/HMAC) defer 의 trigger = 협업자/멀티테넌트 발생(그 시점 후속 carrier 가 nonce/HMAC + scope re-tighten 발의)."
    summary: |
      Jira 결정 채널 governance (wrapper-self dogfood, Epic CFP-2285 S1). 코드와 분리된 평문 의사결정·모니터 surface 를 단일 control project(결정 채널 전용) Jira 이슈로 운용하기 위해, ADR-099 §결정 1 Layer 1 permission deny 집합에서 `addCommentToJiraIssue` **1종만** narrow-allow 로 이동(Orchestrator preset 한정, 임의 SubAgent deny). createJiraIssue/editJiraIssue/transitionJiraIssue 등 나머지 Jira write 는 deny 유지. ADR-100 §결정 3 의 "Jira 기능 W4+ defer, declare-only placeholder" 경계를 S1 에서 의도적·부분 역행으로 문서화(W4+ defer 를 앞당김). §결정 2 Layer 2 lint allowlist 는 addComment 평문 참조 영역 cover 로 동반 확장. §결정 5 trust boundary 에 (a) write scope-limit (b) payload deny-scan hard-block (c) 답변 authorization(author 필드 비신뢰 + first-valid-immutable + 짧은 open-window + 신뢰가정 명시 + 강한 인증 defer) (d) audit/1-step revert 4 제약 추가. 보안 posture = 신뢰가정 명시(비공개·단일 사용자 Jira 프로젝트 접근=결정 권한) + 경량 방어. §해소 기준의 "Layer 1 mcp__atlassian deny 제거 = 약화 차단" 항목을 evidence-gate 경로(3-tuple 충족 시 1종 narrow-allow 1급 허용)로 정정 — full deny 제거(wildcard allow)는 여전히 차단. Phase 2 wire = check-no-atlassian.sh allowlist + 경로버그(archive/adr) + atlassian-tool-snapshot.txt narrow-allow 반영 + drift-check + 사용자레벨 settings.json(repo settings 금지).
---

# ADR-099 — check-no-atlassian.sh 역전 + Atlassian-allow 재정의

## 상태

`Accepted` (2026-05-21 KST) — CFP-1147 carrier (Epic-A Wave 1 Story-1, hard prerequisite). ArchitectAgent direct write per ADR-070 / CFP-578 chief author precedent. ADR-079 KST `+09:00` ISO 8601 zoned governance display layer 정합. status `reserved → active` 전환 = 본 commit time (ADR-083 row 83 CFP-899 precedent 정합 — chief author scope).

## 컨텍스트

### 동인

사용자가 codeforge 의 git-native governance 에 Atlassian suite (Jira + Confluence) 를 **의도적으로 재결합** 결정했다 (Epic-A / CFP-1146). 이는 v0.7→v0.8 의 breaking change — Atlassian backend 완전 제거 — 의 **reversal** 이다. brainstorm Phase 0+1+2 수렴 결과, wrapper `docs/**` → Confluence authoritative (Epic-A A-2) governance reversal 을 진행한다.

`scripts/check-no-atlassian.sh:24` 가 v0.8 Atlassian 제거의 mechanical guard 다 — `atlassian|Confluence|Jira|mcp__atlassian` 패턴을 `--include='*.md' --include='*.yml' --include='*.yaml' --include='*.json'` 영역에서 grep 해, allowlist (현재 11 file — CHANGELOG / migration-guide / playbook / superpowers spec·plan 9종 + 본 script 자체) 외에서 매치되면 exit 1 한다.

Epic-A 가 Atlassian 을 재결합하려면 **첫 commit 부터 Atlassian/Confluence/Jira 참조가 docs/** 전반에 등장**한다. 현 lint 는 이를 "atlassian 잔재 발견 (allowlist 외)"로 fail 시키므로, lint 의 역전/재정의가 **모든 후속 Wave 의 hard prerequisite** 다 (이 Story 미완 시 후속 commit 의 Atlassian 참조가 self-enforcing guard 에 걸린다).

### verified-via — 본 ADR 의 모든 사실 인용 검증

본 ADR 의 mechanical 결정은 실제 코드/CI 상태 verify 위에서 작성됐다. spawn prompt 전제 ("첫 commit 부터 이 lint 가 CI fail") 중 일부는 verify 결과 **정정**됐다 (아래 §사실 정정).

> verified-via: Read scripts/check-no-atlassian.sh (worktree HEAD `dc75aa2`) — L8-21 ALLOWLIST 11 entry / L24-27 grep 패턴 `atlassian|Confluence|Jira|mcp__atlassian` 4종 + include glob 4종 (md/yml/yaml/json) / L29-52 allowlist 필터 후 잔재 발견 시 exit 1.
> verified-via: Grep "check-no-atlassian" + Bash `grep -rnE 'check-no-atlassian' .github/ templates/` (worktree) — **NOT-WIRED-anywhere-in-CI**. `.github/workflows/lint.yml` 안 미호출 (`NOT-CALLED-in-lint.yml`). templates/github-workflows/ 안 미호출. → 본 lint 는 CI gate 가 아닌 **standalone manual / 세션-개시 호출 script** 다.
> verified-via: Read docs/adr/ADR-060 (worktree) L860 — check-no-atlassian = evidence-checks-registry 등록 **보류** ("(c) owner_adr 부재 (meta-governance) BUT detect_command 보유. workflow trigger 명확치 않음 → 등록 보류 — owner_adr 도입 후속 carrier 발의 권고"). 본 ADR 이 그 owner_adr 다.
> verified-via: gh api repos/mclayer/codeforge-internal-docs/contents/wrapper/specs/2026-04-25-atlassian-to-github-migration-design.md (decoded) — L14 "atlassian MCP 의존을 **완전 제거(hard remove)**" / L294 "~~`atlassian` (HTTP)~~ **제거**" / L480-481 "v0.x.0 ... atlassian 제거 + github 도입. **Breaking change**". predecessor reversal 대상 확정.
> verified-via: gh api .../plans/2026-04-28-cfp-27-phase-0b-lint-strengthening-and-ci-integration.md (decoded) L787 — `./scripts/check-no-atlassian.sh; echo "6: exit=$?"` = **manual 호출 검증만**. lint.yml 3 job (redistribution + frontmatter + section-schema) 안 미포함 → lint 는 CI wire 안 됨이 도입 시점부터의 사실.
> verified-via: git show origin/main:docs/adr/ADR-058 L78-95 §결정 5 — amendment 시 sunset_justification 의무 (ratchet 차단), 옵션 B justification 채택, count cap 없음.
> verified-via: git show origin/main:docs/adr/ADR-064 L16/L28/L61 §self-application top-down ratchet — 강화 방향만 허용, 약화 amendment = ADR-058 §결정 5 sunset_justification 의무.
> verified-via: Read docs/adr/ADR-097 (worktree) L67-110 §결정 1-3 — paradigm replacement 면제 channel (closed-set 3 조건 AND) + carrier-preserved sunset 개념 (효용 lossless carry 시 bulk sunset ≠ ratchet 약화).
> verified-via: Read docs/adr/ADR-RESERVATION.md (worktree) L139-147 — row 99~103 CFP-1146 5-slot bundle. row 99 = `ADR-099-atlassian-allow-redefinition.md`, row 102 = `ADR-102-ratchet-weakening-governance-anchor.md` (S4 sunset_justification + ratchet 약화 극복 anchor).
> verified-via: gh api .../wrapper/stories/CFP-1147.md — 404 (Story file 부재) → 본 ADR 이 §3 설계 SSOT.
> verified-via: gh api .../wrapper/specs/2026-05-21-atlassian-suite-integration-epic-a.md — 404 (Epic-A spec 미작성/미push). Epic 컨텍스트는 spawn prompt 의 332줄 spec 요약 + ADR-RESERVATION 5-slot 의미 (row 99~103) 로부터 복원.

### 사실 정정 (spawn prompt 전제 ↔ verify 결과)

| spawn prompt 전제 | verify 결과 | 영향 |
|---|---|---|
| "첫 commit 부터 이 lint 가 CI fail" | check-no-atlassian 은 **CI 미wire** (standalone manual script) — CI fail 아님 | hard prerequisite 의미는 유지 (governance self-guard / 세션-개시 호출 / 후속 CI wire 후보) 하나, "blocking CI gate" 는 부정확. §결정 1 이 이 사실 위에서 방향 결정 |
| "현재 5 file allowlist" | 실제 **11 file** allowlist (CHANGELOG + migration-guide + playbook + superpowers spec·plan 9종 + script 자체) | §결정 2 allowlist 재정의 범위가 5 → 11 baseline 위에서 진행 |
| "CI workflow 식별" (§3) | check-no-atlassian 호출 workflow **부재** (0건) | §결정 3 = "CI wire 영향 없음 + ADR-060 registry 등록 (owner_adr 부여) 가 실 CI 영향 경로" 로 재구성 |

이 정정은 ADR-082 §결정 2 (write-time self-write verification — 작성 값 사실성 source direct verify) 정합. spawn prompt 의 전제를 verify 없이 단언하지 않고 ground truth 위에서 재구성했다.

## 결정

### §결정 1 — lint 재정의 방향: (b) 역전 (권장) — 2-layer 분리 (permission layer 차단 + lint allowlist 평문 허용)

**권장 = (b) 역전.** check-no-atlassian.sh 를 폐기하지 않고, **무단 Atlassian MCP 호출 (`mcp__atlassian__*`) 은 여전히 차단**하되 **정식 sync 채널 (Confluence doc SSOT 영역 + 명시 sync 경로) 의 Atlassian/Confluence/Jira 평문 참조는 허용**하도록 의미를 역전한다. 단, 이 두 효용은 **단일 grep 한 줄로 분리할 수 없다 (SecurityArch P0)** — 아래 2-layer 로 enforce 책임을 분리한다.

#### grep substring false-negative (SecurityArch P0 — 단일 lint 분리 불가)

현 L24 패턴 `atlassian|Confluence|Jira|mcp__atlassian` 에서 `atlassian` 은 `mcp__atlassian` 의 **substring** 이다. 따라서 "한 줄 grep 으로 평문 `atlassian` 만 allowlist 통과 + `mcp__atlassian` 만 차단" 은 **mechanically 불가능**하다:

- allowlist 가 `atlassian` 평문 참조를 통과시키면 → `mcp__atlassian__sync` 가 포함된 라인도 `atlassian` 매치로 잡혀 **동일 라인이 allowlist 통과** → 무단 MCP 호출 라인이 lint 를 통과 = **false-negative** (security guard 우회).
- negative-lookahead 류 정규식 (`atlassian(?!.*mcp__)`) 도 라인 단위 grep 에서 동일 라인의 평문 참조 ↔ MCP 호출 공존을 신뢰성 있게 구분 못 함. lint 의 grep allowlist layer 는 **enforcement 가 아니라 detection 수준** — security 보장을 grep 라인 매칭에 위임하는 것 자체가 결함.

따라서 §결정 1 의 "(b) 역전" 은 **두 별개 enforce layer 의 합성**으로 정정한다 (단일 lint 의미 역전 아님).

#### Layer 1 — 무단 MCP 호출 차단 = permission layer (SSOT, security 보장)

무단 `mcp__atlassian__*` 호출 차단의 SSOT 는 **grep lint 가 아니라 permission layer** 다 (SecurityArch 권장):

- **settings.json `permissions.deny: ["mcp__atlassian__*"]`** — 기본 차단 (모든 agent default deny).
- **agent permission layer** — 정식 sync agent (ADR-101 verify-before-trust Confluence REST / ADR-103 sync mechanism 가 정의하는 단일 진입점 agent) 의 preset 만 `mcp__atlassian__*` 을 **narrow allow** (필요한 tool 만 명시 allow, wildcard 회피).
- ad-hoc / allowlist 밖 임의 agent 의 atlassian MCP 호출 = permission deny 로 **runtime 차단** (grep 사후 detection 이 아니라 호출 자체 거부).

이 layer 가 v0.8 security guard 효용 (무단 MCP 호출 0) 의 **실 carrier** 다. carrier-preserved sunset (§결정 4) 의 효용 이전 대상이 grep 이 아니라 permission layer 임을 명시.

#### Layer 2 — 평문 참조 allowlist = lint(grep) layer (governance detection)

`atlassian|Confluence|Jira` **평문 참조** (docs/** 의 Confluence authoritative 영역 / Epic-A governance 문서 / sync 채널 config) 의 화이트리스트는 grep allowlist layer 가 담당한다:

- grep 패턴에서 **`mcp__atlassian` 토큰을 분리 제거** — lint 의 grep 책임은 평문 `atlassian|Confluence|Jira` 참조 영역 governance (allowlist 외 등장 = warning) 로 한정. MCP 호출 차단은 Layer 1 위임 (lint 가 security 책임 보유 안 함).
- Layer 2 의 grep allowlist 는 **detection / governance 가시성** 수준 (warning tier, ADR-060 §결정 3) — false-negative 가 security 사고로 직결되지 않음 (security 는 Layer 1 이 보장).

**대안 = (c) scope 한정** (채택 안 함, 근거 기록): wrapper `docs/**` 영역만 평문 Atlassian 참조 허용 + 나머지 차단 유지. (c) 는 (b) Layer 2 의 부분집합 — (b) 의 allowlist 가 (c) 의 "docs/** 영역" 을 포함하므로 (b) 가 더 일반적. (a) 완전 폐기는 **거부** — Layer 1 permission deny 가 함께 사라지면 무단 MCP 호출 차단 효용 상실 (carrier-preserved 위반, ADR-097 §결정 3).

**채택 근거 (ADR-064 §결정 3 룰 2 — 권장 1 + 대안 1)**: 2-layer (b) 역전은 (1) Atlassian 재결합 governance 의도 정합 (Layer 2 평문 허용) + (2) v0.8 security guard 효용을 **올바른 layer (permission) 로 carry** (Layer 1 — grep 에 security 위임하던 결함 동시 시정) + (3) carrier-preserved sunset 자격 충족 (효용 lossless carry, carrier = permission layer). 즉 본 정정은 단순 lint 역전을 넘어 **security enforcement 를 grep → permission layer 로 격상**하는 강화 방향 포함.

### §결정 2 — allowlist 재정의: Atlassian-sync 영역으로 확장 (Layer 2 lint grep 한정)

본 §결정 2 의 allowlist 는 **§결정 1 Layer 2 (lint grep 평문 참조 화이트리스트) 만** 지칭한다 — Layer 1 (`mcp__atlassian__*` permission deny) 와 disjoint. 현 11 file allowlist 를 Atlassian-sync governance 영역의 **평문 참조** 화이트리스트로 확장한다. 확장 baseline:

| 추가 allowlist 영역 | 사유 | carrier ADR |
|---|---|---|
| `docs/adr/ADR-099-*.md` ~ `docs/adr/ADR-103-*.md` | Epic-A 5-slot governance ADR 자체 (Atlassian 결정 명시 기록) | 본 ADR-099 |
| wrapper `docs/**` Confluence authoritative 영역 | A-2 governance reversal (Confluence doc SSOT) | ADR-100 |
| 정식 sync 채널 코드/config 경로 | git↔Confluence sync mechanism 산출물 | ADR-103 |
| Epic-A spec / Story file (internal-docs dogfood-out) | Epic 컨텍스트 문서 (wrapper repo 외 — lint scope 밖, 참고만) | ADR-013 |

**구현 형식 (S1 Phase 2 또는 후속 carrier 위임)**: 본 §결정 2 의 allowlist 는 **Layer 2 (lint grep) 의 평문 참조 화이트리스트만** 지칭한다 (§결정 1 정정 정합) — `mcp__atlassian` MCP 호출 차단은 본 allowlist 가 아니라 **Layer 1 permission layer 의 별도 enforce 책임** (settings.json deny + agent preset narrow allow) 이다. 즉 "mcp__atlassian deny 분리" = grep negative-lookahead 가 아니라 **enforce layer 자체의 분리** (lint grep ↔ permission deny disjoint) 를 의미한다.

Layer 2 grep allowlist 는 file-by-file enumeration (현 패턴, 11 file) 대신 **prefix/glob 패턴** 으로 재구조화 권장 — Epic-A 가 docs/** 전반에 평문 Atlassian 참조를 추가하므로 file enumeration 이 폭발한다. 동시에 grep 패턴에서 **`mcp__atlassian` 토큰을 제거** (substring false-negative 회피, security 책임 Layer 1 이관). 정확한 재구조화 = RefactorAgent consult 영역 (§deputy 결정). 본 ADR 은 (1) Layer 1 permission deny SSOT 방향 + (2) Layer 2 lint allowlist 평문 prefix/glob 확장 방향 을 명시 고정하고, 구현 detail 은 Phase 2 위임.

### §결정 3 — CI workflow 영향: 현 미wire + ADR-060 registry 등록 (owner_adr 부여)

**현 사실**: check-no-atlassian.sh 는 어떤 CI workflow 에도 wire 되어 있지 않다 (verified — `.github/workflows/lint.yml` 미호출, templates/ 미호출). 따라서 lint 역전이 **기존 CI gate 를 깨뜨리지 않는다** (CI 영향 0건).

**ADR-060 registry 등록 (owner_adr 부여)**: check-no-atlassian 은 ADR-060 L860 에서 "owner_adr 부재 (meta-governance)" 사유로 evidence-checks-registry 등록 **보류** 상태였다. 본 ADR-099 이 그 **owner_adr** 다 — 본 ADR 이 lint 의 거버넌스 의미 (무단 Atlassian MCP 호출 차단 + 정식 sync 채널 화이트리스트) 를 정의하므로, `docs/evidence-checks-registry.yaml` 에 `check-atlassian-allow` entry 를 **warning tier** 로 등록할 자격이 성립한다 (mechanical_enforcement_actions 정합).

**registry entry 형식** (S1 Phase 2 또는 후속 carrier 위임, ADR-060 framework):
- `name: check-atlassian-allow`
- `owner_adr: ADR-099`
- `detect_command: scripts/check-no-atlassian.sh`
- `current_tier: warning` (CI 미wire baseline 위 신규 등록 — blocking 승격은 ADR-060 §승격 gate AND condition 충족 후)
- `bypass_label: hotfix-bypass:atlassian-allow` (warning tier optional)

본 §결정 3 = ADR-060 L860 의 "owner_adr 도입 후속 carrier 발의 권고" 의 직접 응답.

### §결정 4 — predecessor reversal 명시 + ratchet 약화 정당화 (S4 ADR-102 cross-ref)

**predecessor reversal 명시**: 본 lint 역전은 v0.7→v0.8 의 Atlassian 완전 제거 (predecessor spec `2026-04-25-atlassian-to-github-migration-design.md` — "atlassian MCP 의존을 완전 제거(hard remove)", Breaking change v0.x.0) 결정의 **reversal** 이다. v0.8 은 Atlassian 책임을 GitHub primitive 로 이전하고 lint 로 잔재 0 을 self-enforce 했다. Epic-A 는 이 결정을 의도적으로 되돌려 Atlassian suite 를 재결합한다. 본 ADR 은 그 reversal 의 mechanical guard 전환점이다.

**ratchet 약화 정당화 — S4 ADR-102 위임 (중대)**: lint 의 "Atlassian 잔재 0" → "Atlassian-allow" 전환은 **ratchet 약화 방향** 이다 (ADR-064 §self-application top-down ratchet — 강화만 허용, 약화 차단). 따라서 **ADR-099 단독으로는 ratchet 약화 불가**. 본 ADR 은 lint 역전의 **mechanical 결정** 만 담당하고, ratchet 약화 자체의 **정당화는 S4 (ADR-102 — sunset_justification + ratchet 약화 극복 governance anchor) 에 위임**한다.

ADR-102 가 codify 해야 할 정당화 경로 (본 ADR 이 ADR-102 에 거는 의존):
1. **carrier-preserved sunset (ADR-097 §결정 3 정합)**: v0.8 lint + 차단 효용 (무단 MCP 호출 0) 이 (b) 역전 후에도 lossless carry 된다 — 단 carrier 는 grep 이 아니라 **permission layer** (§결정 1 Layer 1 정정 정합 — settings.json deny + agent preset narrow allow). 효용 소멸 (naive sunset) 이 아니라 효용 이전 (carrier shift, grep → permission) 이므로 약화 아님.
2. **ADR-097 paradigm 면제 channel 은 비대상 (ArchitectAnalyst 통합 — 잠정 평가 철회)**: 아래 §결정 4-A 참조. ADR-097 §결정 1 closed-set AND 3 조건 중 (a) 9+ ADR 동시 sunset 이 **충족 불가** (predecessor formal ADR 0건) → ADR-102 는 ADR-097 면제 channel 을 **발동하지 않는다**.
3. **sunset_justification 3-tuple = ADR-058 §결정 5 일반 경로 (ADR-095 metric reuse + spec-level reversal mechanism extend)**: 아래 §결정 4-A 참조. ADR-097 면제 channel 비대상이므로, predecessor sunset 정당화는 ADR-058 §결정 5 **일반** sunset_justification 3-tuple (metric/who/how) 경로를 탄다. ADR-095 metric 형식 reuse + "spec-level predecessor 의 formal-ADR-없는 reversal" 처리 mechanism 신설 (extend).

#### §결정 4-A — ArchitectAnalyst 통합: S4 ADR-102 = extend (이전 잠정 평가 "reuse 충분" 철회)

> **이전 잠정 평가 철회 명시**: 본 ADR 초안의 §결정 4 잠정 평가 ("ADR-097 면제 channel + ADR-095 metric 형식 reuse 로 충분 / Atlassian reversal = ADR-097 §결정 1 (a)(b)(c) 3 조건 충족 후보") 는 ArchitectAnalyst 분석으로 **반박·철회**한다. 충족 후보가 아니라 **조건 (a) 충족 불가**다.

**ADR-097 면제 channel 발동 자격 — AND 1 조건 미충족 (closed-set AND)**:

ADR-097 §결정 1 면제 channel = closed-set AND 3 조건. ArchitectAnalyst 가 각 조건을 verify 결과 위에서 평가:

| ADR-097 §결정 1 조건 | Atlassian reversal 평가 | 충족 |
|---|---|---|
| **(a) 9+ ADR/contract 동시 sunset 동반** | predecessor v0.7→v0.8 Atlassian 제거의 **formal carrier ADR 가 0건**. spec/plan/agents/settings/schema/docs 레벨만 존재 (`docs/superpowers/specs/2026-04-25-atlassian-to-github-migration-design.md` + plan + 19개 비-ADR 커밋). "sunset 해야 할 9+ ADR" 자체가 부재 — sunset 대상 enumeration 불가. | **미충족** |
| **(b) 단일 atomic Epic** | Epic-A (CFP-1146) 5-slot bundle (ADR-099~103), sub-Story sibling sequential. | 충족 |
| **(c) ratchet 강화 방향 lossless** | mcp__atlassian deny carry (§결정 1 Layer 1 permission layer 로 효용 이전) — lossless carry 가능. | 충족 가능 |

(a) 미충족 → **closed-set AND 위반** → ADR-097 면제 channel **발동 자격 충족 불가**.

> verified-via: `git -C <worktree> log --all --oneline | grep -i atlassian` (worktree HEAD `dc75aa2`) — 19 커밋 모두 spec/plan/docs/schema/agents/settings/presets/session/migration chore 레벨. `docs/adr/ADR-*` carrier 0건.
> verified-via: `git -C <worktree> log --all --oneline -- 'docs/adr/ADR-*.md'` cross-filter — atlassian-carrier ADR 0건 (ADR-92~98 = CFP-1111/1134 paradigm replacement Epic carrier, Atlassian 무관).

**predecessor carrier ADR 번호 = 미존재 (식별 불가)**: predecessor Atlassian 제거는 spec/plan 레벨 결정만이며, formal ADR carrier 번호가 할당된 적 없다. 따라서 ADR-097 §결정 3 의 "sunset 대상 ADR 목록 enumeration + 각 효용 carry 경로" 자체를 구성할 수 없다 (sunset 할 ADR 객체 부재).

**S4 ADR-102 = extend (reuse 아님, 신설 아님)**: ADR-102 가 codify 해야 할 정당화 경로 3-fold:
1. **ADR-095 metric 형식 reuse** — sunset_justification 의 metric 영역 (changelog mining + cron, GA baseline 형식) 을 ADR-095 (9 ADR sunset metric 표준화) 에서 그대로 reuse.
2. **ADR-097 carrier-preserved sunset 개념 cross-ref** — 효용 lossless carry 개념 자체는 ADR-097 §결정 3 cross-ref (개념 reuse). 단 §결정 1/2 면제 channel 은 발동 안 함 (조건 a 미충족).
3. **신규 mechanism (extend)** — "spec-level predecessor 의 formal-ADR-없는 reversal" 의 sunset_justification 처리. 기존 ADR-058 §결정 5 / ADR-097 어느 쪽도 "formal ADR 없는 spec/plan-레벨 결정의 reversal sunset" 을 다루지 않음. ADR-102 가 이 case 를 ADR-058 §결정 5 **일반 경로** 위에 specialize 하여 신설.

따라서 ADR-102 = **extend** (ADR-095 reuse + ADR-097 cross-ref + spec-level reversal mechanism 신설). reuse 만으로 불충분 (신규 mechanism 필수), 완전 신설도 아님 (ADR-095 metric + ADR-097 개념 reuse).

**overlap 판단 (chief tie-break ladder 발동 불요)**: ADR-097 (paradigm 면제 channel) 과 ADR-095 (sunset metric) 는 ADR-102 와 **orthogonal cross-ref 관계** — 동일 anchor 를 두고 경합하지 않는다 (ADR-097 면제 channel 비대상이므로 충돌 surface 자체 없음, ADR-095 는 metric 형식 reuse 로 보완 관계). 따라서 ADR-068 Amendment 2 chief tie-break ladder (RACI → invariant → chief judgement) **발동 불요** — orthogonal 관계로 ArchitectAnalyst 분석에서 직접 resolve.

ADR-102 신설 정당성 (별도 Story S4) = ADR-097 면제 channel 비대상 case 의 sunset_justification 일반 경로 specialize anchor 필요. S4 ArchitectAnalyst 가 본 §결정 4-A 결론 (extend) 위에서 ADR-102 본문 작성.

## 결과

### 긍정

- Epic-A 후속 Wave 의 hard prerequisite 해소 — Atlassian/Confluence/Jira 참조가 self-guard 에 막히지 않음 (정식 sync 채널 + docs/** 허용).
- v0.8 security guard 효용 보존 + 격상 (carrier-preserved) — 무단 `mcp__atlassian` 호출 차단을 grep 라인 매칭 (false-negative 결함) 에서 **permission layer (settings.json deny + agent preset narrow allow)** 로 이전 (Layer 1). security enforcement 격상 = naive 폐기 회피 + 강화 방향.
- check-no-atlassian 의 ADR-060 registry 등록 보류 (owner_adr 부재) 해소 — 본 ADR 이 owner_adr 부여.
- predecessor reversal 명시 기록 — v0.7→v0.8 제거 결정의 history 연속성 + reversal 의도 audit trail.

### 부정 / trade-off

- lint 역전 (Layer 2 평문 allowlist 확장) = ratchet 약화 방향 — ADR-099 단독 불가, S4 ADR-102 dependency (Epic-A 진행 순서상 S1 ↔ S4 coupling). 완화 = 본 ADR §결정 4/4-A 가 정당화 경로를 명시 위임. 단 ADR-097 면제 channel 은 **비대상** (조건 a 9+ ADR sunset 미충족, predecessor formal ADR 0건) → ADR-058 §결정 5 **일반** sunset_justification 3-tuple 경로 (ADR-095 metric reuse + spec-level reversal mechanism extend, ADR-102 carrier).
- 단일 grep 으로 MCP 차단 ↔ 평문 허용 분리 불가 (substring false-negative, SecurityArch P0) — 완화 = 2-layer 분리 (Layer 1 permission deny SSOT / Layer 2 lint grep 평문 detection). lint 의 grep 패턴에서 `mcp__atlassian` 토큰 제거 + security 책임 permission layer 이관 (§결정 1/2).
- (b) 역전 의 Layer 2 allowlist file enumeration 폭발 risk — Epic-A 가 docs/** 전반 평문 Atlassian 참조 추가. 완화 = §결정 2 prefix/glob 재구조화 (RefactorAgent consult).
- Atlassian API token / MCP endpoint = security surface (§7.1/§7.5 trust boundary) — 완화 = consumer overlay `atlassian.*` schema 평문 mount 금지 (env/secret store 경유) + ADR-101 ground-truth verify 가 SSRF/응답 변조 boundary 검증 책임. 아래 §trust boundary 참조.
- mechanical_enforcement_actions (`check-atlassian-allow`) Wave 1 declaration-only — 실 lint 역전 wire + registry entry = S1 Phase 2 / 후속 carrier (ADR-082 §결정 6 retain pattern). pattern_count >= 2 재발 시 follow-up CFP MUST promote to blocking tier.

### §결정 5 — trust boundary (SecurityArch §7.1/§7.5 통합)

Atlassian 재결합은 신규 외부 trust boundary 를 도입한다. SecurityArch consult 결과:

- **Atlassian API token = Secret (§7.1)**: consumer overlay `atlassian.*` schema 에 token 을 **평문 mount 금지**. env / secret store 경유 주입 의무. log 노출 deny (token 이 stdout / lint output / agent transcript 에 등장 금지). project.yaml `atlassian.*` schema 신설 시 token 필드는 reference (env var name) 만 허용, 값 직접 기재 금지 — ADR-027 consumer adoption schema 정합 (S2/S3 ADR-100 carrier 가 schema 확정).
- **Confluence REST = outbound-only + read 우선 (§7.5)**: ADR-101 (verify-before-trust Confluence REST ground-truth) 가 정의하는 호출은 **outbound-only** (Confluence → wrapper inbound webhook 없음). read 우선 — write 는 ADR-103 (sync mechanism) **단일 진입점** 만 (Layer 1 permission narrow allow 대상 = ADR-103 sync agent).
- **MCP endpoint = SSRF / 응답 변조 surface (§7.5)**: `mcp__atlassian__*` endpoint 는 SSRF (내부 자원 도달) + 응답 변조 (Confluence 응답이 wrapper governance state 를 오염) 공격 surface. boundary 검증 책임 = **ADR-101 ground-truth verify** (Confluence 응답을 신뢰 전 git-side ground truth 와 cross-check, ADR-070 verify-before-trust 외부 worker output 정합). 본 ADR §결정 1 Layer 1 permission deny 가 SSRF 의 1차 방벽 (무단 endpoint 호출 차단), ADR-101 이 정식 채널 응답의 무결성 보장.

본 §결정 5 는 ADR-099 가 boundary 를 enforce 하는 것이 아니라 (ADR-101/103 owner) **boundary 존재를 명시 + Layer 1 permission deny 가 1차 방벽임을 cross-ref** 한다 (boundary completeness I-1/I-2 정합 — cross-module propagation 명시).

## 해소 기준

N/A — permanent policy (is_transitional: false). lint 역전 (Atlassian-allow 방향, 2-layer) 자체는 Atlassian 재결합 후 영구 정책. 단 "v0.8 Atlassian 제거 결정 (predecessor) 효력 약화" 의 정당화는 S4 ADR-102 §sunset_justification 3-tuple 에 위임 (frontmatter is_transitional false ↔ 약화 정당화 layer 분리 — §결정 4/4-A).

**약화 정당화 경로 = ADR-058 §결정 5 일반 경로 (ADR-097 면제 channel 비대상)**: §결정 4-A 가 확정 — ADR-097 paradigm 면제 channel 은 조건 (a) 9+ ADR 동시 sunset 미충족 (predecessor formal ADR 0건) 으로 **발동 불가**. 따라서 약화 정당화는 ADR-058 §결정 5 일반 sunset_justification 3-tuple (metric/who/how) 경로 + ADR-095 metric 형식 reuse + spec-level reversal mechanism 신설 (ADR-102 extend).

amendment 시 sunset_justification 의무 — ratchet 강화 방향만 허용 (예: Layer 1 permission deny 패턴 강화 / Layer 2 allowlist 정밀화 / warning → blocking 승격 / token secret 강제 강화). 약화 방향 (예: Layer 1 mcp__atlassian deny 제거 / Layer 2 allowlist 무제한 확장 / token 평문 mount 허용) 은 ADR-058 §결정 5 sunset_justification 의무로 차단.

본 ADR 은 ADR-058 §결정 7 보안 ADR presumption 영역 인접 (무단 MCP 호출 차단 + token secret + SSRF boundary = security guard). 단 category = governance (Atlassian-allow 거버넌스 결정 본체) — security 차단 패턴은 Layer 1 permission carrier + §결정 5 trust boundary 로 보존.

## 관련 파일

- `scripts/check-no-atlassian.sh` — 본 ADR 의 mechanical 대상 (역전/재정의, Phase 2 wire)
- `docs/adr/ADR-102-ratchet-weakening-governance-anchor.md` — S4 ratchet 약화 정당화 anchor (extend = ADR-095 metric reuse + ADR-097 개념 cross-ref + spec-level reversal mechanism 신설, ADR-058 §결정 5 일반 sunset_justification 3-tuple SSOT, 본 ADR dependency)
- `docs/adr/ADR-097-paradigm-replacement-governance-anchor.md` — 면제 channel **비대상** (§결정 4-A — closed-set AND 조건 a 9+ ADR sunset 미충족). carrier-preserved sunset 개념(§결정 3)만 cross-ref 차용
- `docs/adr/ADR-095-sunset-metric-standardization.md` — sunset metric 형식 (S4 ADR-102 가 metric 영역 reuse — changelog mining + cron, GA baseline)
- `docs/adr/ADR-101-verify-before-trust-confluence-rest.md` — §결정 5 MCP endpoint 응답 변조 boundary 검증 owner (ground-truth verify)
- `docs/adr/ADR-060-evidence-enforceable-promotion-framework.md` — check-no-atlassian registry 등록 보류 해소 (owner_adr 부여, Layer 2 lint)
- `.claude/settings.json` — §결정 1 Layer 1 `permissions.deny: ["mcp__atlassian__*"]` SSOT (S2/S3 carrier wire) + agent preset narrow allow
- `docs/superpowers/specs/2026-04-25-atlassian-to-github-migration-design.md` — predecessor (v0.7→v0.8 Atlassian 완전 제거 결정 — spec/plan 레벨, formal ADR carrier 0건)
- `docs/adr/ADR-RESERVATION.md` — row 99 reserved → active 전환

---

## Amendment 1 (CFP-2285) — Jira 결정 채널 governance: Layer 1 narrow-allow `addCommentToJiraIssue` 1종

> carrier: CFP-2285 S1 (#2287, Epic CFP-2285 wrapper-self dogfood) · date: 2026-06-15 (KST per ADR-079 §결정 2) · nature: **ratchet-weakening** (Layer 1, evidence-gated — ADR-058 §결정 5 post-CFP-1149 / ADR-064 §결정 7 symmetric) · decisions_touched: §결정 1 / §결정 2 / §결정 5 / §해소 기준

### §배경 — 왜 Jira write 1종을 다시 허용하나

Orchestrator 와 사용자(단일 운영자) 사이의 **의사결정·진행 모니터링 surface 를 코드와 분리된 평문 채널**로 둘 필요가 생겼다. GitHub Issue/PR 는 구현 산출물과 한 repo 에 섞이고, 세션 transcript 는 휘발성·비공개다. 비공개·단일 사용자 Jira **control project**(결정 채널 전용) 하나를 두고, Orchestrator 가 결정 fork 마다 그 이슈에 코멘트를 달고 사용자가 코멘트로 답하는 **평문 결정 루프**를 운용한다.

이를 위해 ADR-099 §결정 1 **Layer 1 permission deny** 집합(현 snapshot 24-tool deny, `docs/atlassian-tool-snapshot.txt`)에서 **`addCommentToJiraIssue` 1종만** narrow-allow 로 옮긴다. 이는 ADR-100 §결정 3 의 "Jira 기능 = W4+ defer, declare-only placeholder" 경계의 **의도적·부분 역행**이다(W4+ defer 를 S1 에서 앞당김). 본 Amendment 가 그 경계 이동을 명시 문서화한다.

**ratchet 방향 판정 = Layer 1 약화 (evidence-gate 경로)**: §결정 4-A 가 확정한 바, ADR-099 의 Layer 1 (permission deny) 은 v0.8 security 효용의 **carrier-preserved 영역**으로 약화 대상이 아니었다(S4 ADR-102 의 sunset 정당화도 Layer 2 lint 한정). 본 Amendment 의 narrow-allow 는 그 Layer 1 deny 집합을 **1종 축소**하므로 Layer 1 약화 방향이다. CFP-1149 재정의 후 ADR-058 §결정 5 / ADR-064 §결정 7 의 evidence-gated symmetric ratchet 경로에서, **약화 evidence 3-tuple(metric/who/how) 을 제시하면 약화는 1급으로 허용**된다 — frontmatter `amendment_log[0].sunset_justification` 3-tuple 이 그 의무 충족이다(full deny 제거(wildcard allow)는 여전히 차단, 1종 narrow-allow 만 evidence-gate 통과).

### §결정 (Amendment 1)

#### A1-1. Layer 1 write scope-limit (SecurityArch MUST (A))

- narrow-allow 대상 = **`addCommentToJiraIssue` 1종만**. `createJiraIssue` / `editJiraIssue` / `transitionJiraIssue` / `addWorklogToJiraIssue` / `createIssueLink` 등 그 외 모든 Jira write 는 **deny 유지**.
- write 대상 = **단일 control project (결정 채널 전용)** 한정. read 대상 = **결정이 연 단일 이슈** 한정(임의 프로젝트·이슈 read 비대상).
- caller scope = **Orchestrator preset 한정**. 임의 SubAgent 는 본 narrow-allow 비대상(deny) — Orchestrator inline whitelist(ADR-039 §결정 2) 경계 정합.

#### A1-2. payload deny-scan hard-block (SecurityArch MUST (B), ADR-099 §결정 5 outbound 확장)

Jira 로 송신되는 코멘트 payload 는 송신 전 deny-scan 으로 **hard-block** 한다(통과 못하면 송신 차단, warning 아님):

- secret / credential / token 패턴 (ADR-099 §결정 5 token = Secret + ADR-027 token env-indirect 의 **outbound 확장**).
- 절대 파일경로 (`C:\…`, `~/.claude/…`, repo 외부 경로) — 내부 구조 노출 차단.
- full agent transcript / full anchor dump / 코드 블록 원문 통째 송신 차단. Arc B 미러(결정 맥락 재현용)는 **요약본만** 허용.

본 deny-scan 은 ADR-099 §결정 5 의 "token 이 stdout/lint output/agent transcript 에 등장 금지" 를 **Jira outbound 방향으로 확장**한 것이다(env-indirect 의 outbound 대칭).

#### A1-3. 답변 authorization — 경량 posture (SecurityArch MUST (C))

본 채널의 신뢰 근거 = **신뢰 경계 가정**: "비공개·단일 사용자 Jira control project 에 대한 접근 권한 = 결정 권한". 이 가정을 명시한다(암묵 위임 아님).

- **author 필드를 신뢰 근거로 쓰지 말 것** — shared-account 운용 가능성 + Jira author spoofing 비방어이므로, 코멘트의 author 표시는 authorization 근거가 아니다.
- **first-valid-immutable** — 한 결정 fork 당 **첫 유효 답변만 채택**하고 이후 코멘트는 무시(같은 fork 재답변 = 무시). 결정 confirm 후 채널 재오염 차단.
- **짧은 open-window** — 결정 fork 가 답을 받는 window 를 짧게 제한(window 만료 후 도착 답변 = 무시). long-tail 답변 race 차단.
- **강한 인증(nonce/HMAC) = defer** — 현 posture 는 단일 사용자·비공개 신뢰 경계라 경량 방어로 충분. nonce/HMAC challenge-response 는 **협업자/멀티테넌트 발생 시점**의 후속 carrier 로 defer(그 trigger 를 본 Amendment 가 명시). 그 시점 후속 carrier = nonce/HMAC 도입 + scope re-tighten 동반 발의.

#### A1-4. audit / 1-step revert (SecurityArch MUST (D))

- **wrapper-side audit = SSOT**: shared-account 운용 시 Jira author 추적이 신뢰 불가하므로, **모든 Orchestrator Jira write 를 세션 transcript 에 (결정 fork id + payload 요약 + first-valid 채택 기록) 으로 기록**한다. wrapper-side audit log 가 incident/leak 검증의 SSOT(Jira author 아님).
- **1-step revert**: 본 narrow-allow 는 **단일 step 으로 가역**이다 — narrow-allow 집합에서 `addCommentToJiraIssue` 제거 → deny 원복. governance state(Layer 2 lint allowlist / 다른 ADR) 무손상. 이 가역성이 약화 evidence 3-tuple 의 `how` (가역성 보장) 를 충족한다.

### §scope 제약

- 본 Amendment 는 **Layer 1 (permission)** 의 1종 narrow-allow 와 그 운영 제약(A1-1~A1-4)만 결정한다. Layer 2 (lint grep allowlist) 는 §결정 2 의 평문 참조 cover 영역으로 동반 확장(addComment 결정 채널 config / 본 Amendment 평문 참조)하되, **security 책임은 Layer 1 이 보유**(Layer 2 = detection/governance 가시성, §결정 1 정합).
- write 범위 = 단일 control project 결정 채널. **다른 Atlassian 기능(Confluence sync / 다른 Jira 프로젝트 / 다른 Jira write tool) 무영향** — ADR-100~103 Confluence governance 경계 불변.
- 본 채널은 **wrapper-self dogfood 운용**(codeforge 자기 개발 세션)이다. consumer 배포 대상 정책 변경 아님 — consumer 는 본 narrow-allow 비적용(consumer overlay 에서 별도 opt-in 필요 시 후속 carrier).

### §Layer 1·2 영향 판정

| Layer | 변경 | 방향 | 정당화 |
|---|---|---|---|
| **Layer 1** (permission deny, snapshot SSOT) | deny-24 → deny-23 + narrow-allow-1 (`addCommentToJiraIssue`) | **약화 (1종)** | frontmatter `amendment_log[0].sunset_justification` 3-tuple (ADR-058 §결정 5 evidence-gate / ADR-064 §결정 7 symmetric). full deny 제거 아님 — 1종 한정 + A1-1~A1-4 제약 동반. |
| **Layer 2** (lint grep allowlist) | addComment 결정 채널 평문 참조 cover 확장 | 약화 (allowlist 확장) | §결정 2 prefix/glob 경로 + S4 ADR-102 §결정 3 Layer 2 sunset 3-tuple 산하(기존 약화 정당화 anchor 가 cover). |
| Confluence / 다른 Jira write | 무변경 | — | ADR-100~103 경계 불변. |

**§해소 기준 정정**: 기존 §해소 기준 본문의 "약화 방향(예: Layer 1 mcp__atlassian deny 제거 / …) 은 ADR-058 §결정 5 sunset_justification 의무로 차단" 항목 중 "Layer 1 deny 제거" 를 본 Amendment 가 **evidence-gate 경로로 정정**한다 — `mcp__atlassian__*` **full deny 제거(wildcard allow)** 는 여전히 차단이나, **1종 narrow-allow + 3-tuple evidence + A1-1~A1-4 제약** 은 ADR-058 §결정 5(post-CFP-1149 evidence-gate) 1급 허용 경로다. ratchet 강화 방향(추가 tool deny 강화 / narrow-allow 정밀화 / open-window 단축 / payload deny-scan 강화)은 무제한 허용 유지.

### §Phase 2 wire (본 Amendment = docs-only, 코드/설정 변경 0)

본 Amendment 는 **docs 만** 결정한다. 아래 mechanical wire 는 Phase 2 carrier(별 PR):

1. `docs/atlassian-tool-snapshot.txt` — `addCommentToJiraIssue` 를 Jira-side deny(현 line 22)에서 제거 → deny-24 → deny-23. 본문 주석의 "un-denied N tool (read 5 + write 2)" 카운트를 narrow-allow 반영해 갱신.
2. `.claude/settings.json` (**사용자레벨 — repo settings.json 생성 금지**, [feedback_no_repo_settings_files]) — `permissions.deny` 에서 `addCommentToJiraIssue` 제거 + Orchestrator preset narrow-allow 에 개별 열거.
3. `scripts/check-atlassian-tool-drift.sh` — snapshot ⊆ deny 검증이므로 1·2 동시 반영 시 PASS 유지(별도 로직 변경 불요, 동반 검증만).
4. `scripts/check-no-atlassian.sh` — §결정 2 Layer 2 allowlist 에 결정 채널 평문 참조 영역 cover + **경로버그 동반 수정**: `ALLOWLIST_ADR_PREFIXES` 가 `docs/adr/ADR-099..103` 인데 실제 경로 = `archive/adr/`(CFP-2151 이동) → `archive/adr/ADR-099..103` 로 정정.
