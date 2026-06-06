## 3B. Preflight 체크 (lane 진입 직전)

**doc-only fast-path 분기 (ADR-054)**: Story 분류 판정 직후, Orchestrator가 §결정 1 분류 표 적용. `doc-only fast-path` 해당 시: 설계 lane → 경량 설계리뷰 → 단일 PR close (구현 lane spawn 금지). `full-lane` 해당 시: 기존 5-lane 전체. 모호 시 full-lane 강제. 판정 표 SSOT: [ADR-054](../docs/adr/ADR-054-doc-only-story-fast-path.md).

Orchestrator가 **각 레인 진입 직전에 의무 수행**. 3개 체크 중 하나라도 FAIL이면 **block + report**: 에이전트 스폰 없이 사용자에게 실패 사유 반환.

### 3B.1 3개 체크 항목

| # | 체크 | PASS 조건 |
|---|------|-----------|
| 1 | **phase 라벨 정합성** | Story Issue `phase:*` 라벨이 진입할 레인과 일치 (예: 설계 레인 진입 시 `phase:설계`) |
| 2 | **Story file 선행 섹션 채움** | 진입할 레인이 요구하는 이전 섹션이 존재 (예: 설계 진입 시 §1-6, 설계 리뷰 진입 시 §7, 구현 진입 시 §7 + §8 Test Contract) |
| 3 | **외부 의존성 가용** | Codex 리뷰/Analyst 레인 진입 시 `codex --version` 성공 확인. GitHub MCP `mcp__github__issue_read` ping 성공 |
| 4 | **TodoWrite 스키마 가용** (non-blocking) | `ToolSearch("select:TodoWrite")` 성공 여부. 미로드 시 재시도 1회. 재시도 실패 시 **PASS** (lane 미차단 — ADR-038 §결정 7) + `⚠️ TodoWrite 스키마 미로드` 경고 출력. ADR-038 Amendment 2 §결정 9 (SessionStart hook tier (b) PRIMARY, runtime ToolSearch (c) FALLBACK retain — §1.1 0i 참조). |

### 3B.2 FAIL 시 동작

- **스폰 중단**
- 아래 형식으로 사용자 ESCALATE (§2.3 ESCALATE 프롬프트와 유사):

```
⛔ Preflight FAIL — {레인} 진입 차단
- Story: <KEY>
- 실패 체크: {항목 번호 + 사유}
- 현재 상태 스냅샷: {phase 라벨 / §진입 선행 섹션 상태 / 의존성 ping 결과}
- 권장 복구: {해당 lane plugin 으로 §X 보강 / GitHub label 수정 / Codex 재설치 안내}
```

사용자 응답 수령 전까지 레인 진입 금지.

> 체크 4(TodoWrite 스키마)는 non-blocking — FAIL 이어도 스폰 미차단, 경고만 출력 (ADR-038 §결정 7).

### 3B.3 적용 레인별 세부

- **요구사항**: (1) `phase:요구사항` / (2) §1 사용자 원문 존재 + **공통 입력 패키지 준비** (관련 ADR 목록 §3 선제 fetch via `Glob(docs/adr/ADR-*.md)`, 관련 코드 경로 §4 식별, Project Config Packet slice 확보) / (3) `codex` CLI 가용 + GitHub MCP 가용 (DomainAgent·Researcher 호출 포함)
- **설계**: (1) `phase:설계` / (2) §1-6 모두 채움 + "사용자 확인 필요" 해소 + **공통 입력 패키지 준비** (변경 대상 코드 경로 확정, 관련 ADR verbatim fetch, Change Plan 초안 메모 준비) / (3) GitHub MCP 가용
- **설계 리뷰**: (1) `phase:설계-리뷰` / (2) §7 채움 + `docs/change-plans/<slug>.md` 존재 + §7 보안 설계 섹션 작성 여부 (또는 §7.6 N/A 사유 명시 여부) / (3) Codex 플러그인 가용
- **구현**: (1) `phase:구현` / (2) §7 완료 + Change Plan §8 Test Contract 존재 (§8.3 `N/A` 허용) + Phase 1 PR merged / (3) 필요 Dev 전원 스폰 가능
- **구현 리뷰**: (1) `phase:구현-리뷰` / (2) §8 Impl Manifest 기록 + ArchitectPLAgent 매핑표 감사 PASS / (3) Codex 플러그인 가용
- **구현 테스트**: (1) `phase:구현-테스트` / (2) §9.2 구현 리뷰 PASS 기록 / (3) CI (`gh pr checks`) 접근 가능 (ADR-048 CI gate)
- **통합 테스트**: (1) `phase:통합-테스트` / (2) §9.3 CI gate PASS 기록 / (3) `docker-compose.test.yml` 존재 여부 확인 (§8.6 환경 의존성 Story) + IntegrationTestAgent spawn 가능 (ADR-055)
- **보안 테스트**: (1) `phase:보안-테스트` / (2) §9.4 통합 테스트 PASS 기록 / (3) Codex 플러그인 가용 + 의존성 매니페스트 존재 + Dependabot/CodeQL 결과 접근 가능 (lanes.security_ai: true 시만)

### 3B.4 Preflight 결과 기록 (PMO 감사 trail · 의무)

PASS·FAIL 무관, **모든 Preflight 실행 결과**는 Orchestrator 가 직접 GitHub Issue 코멘트에 기록한다 (PMO 회고 §13.2의 "Preflight 실행 근거" 감사 항목 충족).

Orchestrator 가 Preflight 직후 직접 `mcp__github__add_issue_comment` 호출:

```
Issue: #<N>
Phase: <진입 레인>
Agent: Orchestrator
TL;DR: Preflight {PASS | FAIL} — {레인} 진입 {허용 | 차단}
Body: |
  체크 1 (phase 라벨 정합성): {PASS | FAIL — 사유}
  체크 2 (Story file 선행 섹션): {PASS | FAIL — 사유}
  체크 3 (외부 의존성): {PASS | FAIL — 사유}
  (FAIL 시) 권장 복구 / 사용자 ESCALATE 여부
Source: <자동 — Orchestrator §3B Preflight>
Timestamp: <YYYY-MM-DDTHH:MM:SS+09:00>  # KST zoned (display layer — ADR-079 §결정 2)
```

코멘트 prefix는 `[<phase>] Orchestrator: Preflight {PASS|FAIL}`. 기록 누락 시 PMO 완료 회고에서 P1 결함으로 감사 보고됨.

### 3B.5 plugin-meta-na PR pre-push 자가 검증 (Codex audit closure sprint 회고 §5 운영 개선 #1)

ADR-005 plugin-meta-na 패턴(§8/§9 lane 게이트 면제)으로 진행되는 plugin 자기 적용 PR은 일반 lane 리뷰를 우회하므로 **author가 push 직전 로컬 invariant-check 자가 검증 의무**.

**의무 절차** (push 직전):
1. 변경 대상 SSOT 식별 (CLAUDE.md / `agents/**` / `templates/**` / `.claude-plugin/plugin.json` / `CHANGELOG.md` / `docs/migration-guide.md` 등)
2. 영향 받는 invariant-check Step (3 agent count / 6 category enum / 7 migration-guide BREAKING parity / 8 severity_overrides count)을 [`.github/workflows/invariant-check.yml`](../.github/workflows/invariant-check.yml)에서 직접 grep으로 확인
3. 로컬 dry-run: 해당 step의 핵심 grep·python 로직 1-2줄을 직접 실행해 본 PR 변경 후 PASS 여부 확인 (예: `grep -c "data-migration" templates/change-plan.md docs/inter-plugin-contracts/review-verdict-v1.md` — review subsystem 자체 검증은 codeforge-review repo에서)
4. drift 발견 시 push 전 fix commit 추가, drift 부재 시 push 진행

**근거**: [`docs/retros/2026-04-28-codex-audit-closure-sprint.md`](https://github.com/mclayer/codeforge-internal-docs/blob/main/wrapper/retros/2026-04-28-codex-audit-closure-sprint.md) §5. CFP-21 (migration-guide BREAKING regex 미일치) / CFP-22 (DesignReviewPL severity_overrides P1 3건 누락) 모두 push 후 CI fail로 발견 — plan 작성 단계에서 잡혔어야.

**적용 범위**: plugin-meta-na PR만 (production code Story는 일반 lane Preflight + DesignReview/CodeReview/SecurityTest가 자동 검증). consumer overlay 적용 PR은 본 절차 비대상.

---

### §3.16 UpgradeAgent dispatch protocol (CFP-743 Wave 2 Story-3 / [ADR-076](../docs/adr/ADR-076-declarative-reconciliation-upgrade.md) §결정 5 + [reconcile-protocol-v1 v1.2](../docs/inter-plugin-contracts/reconcile-protocol-v1.md))

codeforge family upgrade 의 선언적 reconciliation 실행 주체. **3 책임 분리** (ADR-076 §결정 5): SessionStart hook (detect only — filesystem touch 0 / network 0) ≠ UpgradeAgent (Plan + Apply) ≠ CLI (`scripts/codeforge-upgrade.{sh,ps1}` 단일 진입점).

**Dispatch 절차** (Phase 2 carrier — CLI/UpgradeAgent 실 구현 후 활성):

```
사용자 → bash scripts/codeforge-upgrade.{sh|ps1} <mode>
  mode = --dry-run | --apply | --rollback <version>   # CLI argument fix, 사용자 결정 분기 0
  │
  └─ Orchestrator → UpgradeAgent spawn (ADR-039 default subagent one-shot, 재귀 spawn 금지 platform inherent)
       │
       ├─ --dry-run  : 9 desired_state_domains diff preview (filesystem touch 0, network call 가능)
       ├─ --apply    : snapshot 생성 → 9 영역 reconcile → 사후 sanity check 단일 transaction
       │                (partial 실패 / sanity 실패 = automatic_rollback_to_snapshot, 사용자 prompt 0)
       │                consumer .github/ 영역 reconcile = PR open (자동 merge 0, PR review gate 보존)
       └─ --rollback <version> : 해당 version snapshot restore
       │
       └─ transaction 완료 → event log artifact docs/upgrade-events/<date>-<version>.md 자동 생성 (C2)
```

**핵심 invariant**: ① SessionStart hook detect 책임 침범 0 (ADR-038 Amendment 3 §결정 12) ② `user_decision_branches: 0` (Epic CFP-699 §1 WHY "0 자리" verbatim) ③ transaction completion = ADR-053 §D2 3조건 AND (marketplace sync PR merged + consumer install 완료 + drift check PASS) ④ reconcile PR scope = ADR-066 Amendment 3 (reconcile-target-repos contents:write + pull_requests:write, target/action 한정 least-privilege) ⑤ path-form 정규화 의무 (MSYS2 `/c/` — CFP-702 normalize_path bug precedent 회피). 상세 SSOT = reconcile-protocol-v1 v1.2 `mechanical_implementation_binding` block.

> **CLAUDE.md cross-ref 부재 사유 (ArchitectPL 설계 결정)**: CLAUDE.md 가 line cap (≤320, ADR-012 Amendment 1 §결정 6) 을 이미 초과 (334 lines, pre-existing warning) — UpgradeAgent dispatch 는 operational reference-tier (anchor-tier 아님 — Orchestrator 가 매 turn 자기검열 대상 아님, ADR-051 Amendment 1 판정자 기준) 이므로 본 playbook §3.16 + consumer-guide 가 SSOT. CLAUDE.md line-delta 0 (over-cap 악화 회피).

### §3.16.1 Consumer natural-language upgrade trigger (CFP-1104 carrier / [ADR-071 Amendment 5](../docs/adr/ADR-071-orchestrator-user-dialog-convergence.md) §결정 16 + [ADR-076](../docs/adr/ADR-076-declarative-reconciliation-upgrade.md) invariant carrier)

consumer 가 자연어 token `codeforge upgrade` (또는 한글 변형) 발화 시 Orchestrator 가 dialog reflex 없이 즉시 §3.16 UpgradeAgent dispatch 호출. ADR-076 invariant `user_decision_branches: 0` 의 **dialog 진입 단계 enforcement** carrier — base ADR-071 §결정 5 사실/가치 분리 원칙의 dialog reflex 차단 first applied case.

**closed enumeration 보존 invariant**: 본 trigger lookup table = ADR-071 §16.2 closed enumeration 1 entry. 2번째 trigger token 확장 시 별도 CFP 의무 (ADR-064 §결정 7 top-down ratchet + ADR-058 §결정 5 sunset_justification null 보존 + Story §1 사용자 explicit 승인 + SecurityArch consult — trust boundary 영역).

#### Trigger token (closed enumeration, 1 entry)

| Trigger phrase regex (case-insensitive) | Mapped action |
|---|---|
| `\b(codeforge\s+upgrade\|codeforge\s+업그레이드)\b` | `scripts/codeforge-upgrade.sh` invocation per §3.16 (7 차원 derived default 자동 적용) |

#### 5 의무 step

1. **token detect** — Orchestrator 가 사용자 발화 turn 에서 위 regex match 확인 → 매치 시 `codeforge:user-dialog-mode` skill frame mode 진입 4 step 적용 (anchor / drift / declare / verify) per ADR-071 §결정 1
2. **derived default declare (Layer 1 preamble)** — 1 turn 사용자에게 declare 1 문장: "발화하신 `codeforge upgrade` → 다음 default 로 즉시 수행: repo=$(pwd) / mode=dry-run→apply 자동 / channel=overlay resolve→stable / scope=single plugin / dirty tree=abort / 실패 시 자동 rollback. 정정 필요 시 발화 의무." (사용자 정정 의무, AskUserQuestion 0)
3. **derived default 추론** — cwd + consumer overlay `.claude/_overlay/project.yaml::codeforge.channel.tier` resolve + ADR-076 default → CLI arg 합성. consumer overlay 부재 시 fallback `--channel stable`. cwd ≠ consumer repo (overlay 부재) 시 abort + 사실 보고 (AC-7)
4. **immediate invocation** — `bash scripts/codeforge-upgrade.sh --dry-run --repo $(pwd) --channel <resolved>` 즉시 실행 (E10 tool-call-only edge — AskUserQuestion 0, ADR-039 inline whitelist 1번 entry scope 안)
5. **evidence verify + apply 자동 + 1 turn 보고** — dry-run exit code + ImpactReport diff verify → apply 자동 (`--apply --repo $(pwd) --channel <resolved>`) → result enum 4-value 1 turn 보고 (SUCCESS / SUCCESS_WITH_DEGRADATION / PARTIAL_FAILURE / FAILED). ADR-071 §결정 15 frequency suppression touchpoint (c) "최종 완료 보고 1회" 정합.

#### Result enum 4-value (1 turn 보고 정합)

| result enum | 발생 조건 | 보고 형식 |
|---|---|---|
| `SUCCESS` | dry-run + apply 모두 PASS, drift 0 또는 reconcile 완료 | 1 turn 보고 + event log artifact `docs/upgrade-events/<date>-<version>.md` 경로 명시 |
| `SUCCESS_WITH_DEGRADATION` | apply PASS 단 sanity check warning (PR open 등 후속 action 필요) | 1 turn 보고 + sanity check warning 항목 명시 + follow-up action 1 줄 |
| `PARTIAL_FAILURE` | apply 일부 영역 실패 + 자동 rollback 부분 적용 | 1 turn 보고 + 실패 영역 명시 + rollback 상태 명시 + 사용자 정정 의무 declare |
| `FAILED` | dry-run 실패 또는 apply 전체 실패 + 자동 rollback | 1 turn 보고 + 실패 사유 + rollback 완료 명시 + 사용자 정정 의무 declare |

#### Edge cases (CFP-1104 §8 verbatim 발췌)

1. **dirty working tree** (AC-3): abort + 사실 보고 ("dirty working tree — `--force-dirty` 미지원, commit/stash 후 재시도"). [InfraOperationalArch §7.4.5 env containment consult]
2. **cwd ≠ consumer repo** (AC-7): abort + 사실 보고 ("현재 cwd 가 consumer repo 아님, `.claude/_overlay/project.yaml` 부재")
3. **사용자가 `codeforge upgrade beta` 처럼 channel 명시 발화**: regex 확장 fallback — `\bcodeforge\s+upgrade(\s+(stable\|beta\|canary))?\b`. channel 명시 = override → overlay resolve 무시. **본 §3.16.1 scope 안 (closed enum 확장 아님 — 동일 entry 의 optional argument)**
4. **사용자가 `codeforge family upgrade` 명시 발화** (AC-6): closed enum 동일 entry scope 안 single plugin → family 분기. `atomic-upgrade-7-plugins.sh` entrypoint 대체 — single plugin 아님
5. **이미 최신 버전 (no-op)** (AC-4): dry-run 결과 drift=0 → apply 단계 skip + result enum `SUCCESS` + 1 turn 보고 (no-op 명시)
6. **사용자가 `codeforge rollback` 발화**: 본 §3.16.1 closed enum 외 (2번째 trigger token 확장 영역) — 별 CFP 의무. 본 §3.16.1 미cover, AskUserQuestion 발화 OK
7. **사용자가 `업그레이드해줘` 자연어 (codeforge token 부재)**: trigger 0 — ambiguous, AskUserQuestion 발화 OK (closed enum 외 영역)

#### invariant 요약

- **inv-1** (`user_decision_branches: 0` dialog 단계 확장): step 2 declare 발화 외 AskUserQuestion 0. derived default 자명 영역 (cwd + overlay resolve + ADR-076 default).
- **inv-2** (closed enumeration 1 entry): 2번째 trigger token 신설 = 별도 CFP 의무 + ADR-071 Amendment + SecurityArch consult.
- **inv-3** (ADR-039 inline whitelist 1번 entry scope 안): 5번째 entry 신설 0, 기존 1번 entry "사용자 dialog 허용 영역" 의 derived default 자명성 명문화.
- **inv-4** (ADR-071 §결정 15 frequency suppression 정합): step 5 result enum 보고 = touchpoint (c) "최종 완료 보고 1회".
- **inv-5** (ADR-076 §결정 5 SSOT carrier): CLI 진입점 `scripts/codeforge-upgrade.{sh,ps1}` 변경 0. 본 §3.16.1 = orchestrator 발화 → CLI invocation 단계 mapping carrier.

### §3.17 Orchestrator-authored Issue body pre-publish verify mandate (CFP-1016 / [ADR-082 Amendment 2](../docs/adr/ADR-082-write-time-self-write-verification-mandate.md))

**적용 trigger**: Orchestrator 가 Issue body 를 author 할 때 — 즉 사용자 GitHub Issue Form submit 이 아닌 **Orchestrator-initiated** body authorship:

1. **retro time follow-up Issue** — PMOAgent retro 완료 후 codeforge-improvement / from-cfp-NNN-retro 등 follow-up Issue body 작성
2. **brainstorm Phase 0 후속 Issue** — `codeforge:codeforge-brainstorm` Phase 2 후 별 carrier Story 발의
3. **ADR amendment carrier reservation Issue** — ADR-RESERVATION row 점유 + carrier Story Issue 발의
4. **pattern_count escalation forcing function 산물** — ADR-045 §D-9 pattern_count ≥ threshold 2 → escalation_action `escalate_user` → ADR strengthening carrier Issue 발의

위 4 trigger 중 1+ 시 본 §3.17 mandate 적용.

**verify-before-trust 의무** (Wave 1 behavioral mandate, ADR-082 §결정 1 layer 1 sub-scope (1-B)):

Orchestrator 가 Issue body 안 fact claim 마다 source direct verify 후 author. 모든 fact citation (file path / registry value / lint output / cross-repo state / ADR frontmatter value / amendment count / 카운터 / file existence 등) 을 다음 mechanism 으로 verify:

| claim 종류 | verify mechanism (Orchestrator inline 또는 subagent delegate) |
|---|---|
| local file path / existence | `Bash: ls <path>` 또는 `Read <abs-path>` |
| local file content / line | `Read <abs-path>` 또는 `Grep` |
| origin/main state (cross-repo state assertion) | `git fetch origin && git show origin/main:<path>` (ADR-073 §결정 1 정합) |
| GitHub Issue state | `gh issue view <N> --repo <org>/<repo>` 또는 `mcp__github__issue_read` |
| GitHub file content (cross-repo, 권한 영역) | `mcp__github__get_file_contents` |
| registry value / yaml field | `Read <yaml path>` + 수동 verify |
| ADR frontmatter value | `Read docs/adr/ADR-NNN-*.md` (offset/limit 활용, 첫 50줄) |
| amendment count / amendment_id | `Read docs/adr/ADR-NNN-*.md` frontmatter `amendments[]` array length verify |
| lint output verbatim 인용 | lint output 의 source state 자체 verify (lint regex FP 가능성 — citation ≠ assertion 분리, ADR-082 §결정 4) |

**Issue body 작성 절차** (4-step):

1. **claim enumerate** — Issue body 초안에 포함된 모든 fact claim 을 1-line 단위 분해
2. **verify per claim** — 위 mechanism 표로 claim 각각 verify
3. **verified-via annotation** — Issue body 안 fact citation 옆에 `[verified: <mechanism> <timestamp KST>]` annotation 부착 (또는 verify 결과 본문 통합)
4. **publish** — `mcp__github__issue_write` 또는 `gh issue create` 발화

**Story-level forcing function** (Wave 1 mechanical, ADR-082 Amendment 2 alternative (a)):

본 §3.17 trigger 4종 1+ 충족 시 Orchestrator 가 Story file frontmatter `issue_origin: orchestrator_authored_followup` 부착 의무 → RequirementsPL 이 Story §2.1 verified state table 작성 의무 (story-page-structure.md §2 template 정합). §2.1 = Issue body verbatim claim ↔ verified state ↔ Pivot 판정 4-column schema.

**precedent**:
- **CFP-1000 §2.1** (9-row drift mapping) — 3 inversions catch: `prod-cutover-deputy-evidence` registry presence INVERTED + baseline label-registry 개수 stale (42→44) + `.claude-work/label-registry-bootstrap.json` inexistent
- **CFP-1001 §2.1** (4 claim verify) — L189 lint regex `±5-line context window` cross-paired L185 ADR-040 ↔ L189 ADR-038 → cross-context FALSE POSITIVE catch (Pivot 1 진단)
- **CFP-1002 §2.1** (2 row verify) — ADR-054 filename `-fast-path.md` cited but actual `-story-fast-path.md` catch (1-character-level edit)
- **CFP-1016 §2.1** (META self-application) — 본 ADR-082 Amendment 2 carrier Story, Issue body 4 claims 검증

**Bypass**: 본 mandate 는 behavioral mandate (Wave 1). 응급 fast-publish 영역 (hotfix Issue 등) 에서 `BYPASS_ISSUE_BODY_VERIFY=1` env (Wave 2 mechanical lint 도입 후) → audit trail 보존. Wave 1 = audit trail prose-only (Story §2.1 표 자체).

**Wave 2 progression** (deferred-followup): `scripts/check-story-section-issue-origin.sh` (warning tier, ADR-060 §결정 5 정합) — `issue_origin: orchestrator_authored_followup` 시 §2.1 verified state table 존재 + 4-column schema 정합 lint. 별 CFP carrier (brainstorm 단계 결정).

**Wave 3 progression** (cross-repo, 후순위 ratchet, CFP-1002 precedent 정합): RequirementsPL spawn prompt template (`mclayer/plugin-codeforge-requirements` canonical) explicit verify-before-trust mandate — cross-repo sibling sync 동반 가치 판단 영역, 별 canonical CFP carrier 분리.

### §3.18 Multi-session collaboration protocol — lane-entry sentinel ownership verify (CFP-1041 / [ADR-085](../docs/adr/ADR-085-multi-session-collaboration-protocol.md))

#### Trigger

복수 Claude Code session 이 동일 repository / Story / Epic / branch 동시 작업 시 — **모든 lane entry 직전 의무**.

#### 4-step polling subprocess (ADR-085 §결정 3)

lane 진입 직전 Orchestrator (또는 lane PL agent spawn 전) 가 다음 4-step polling 의무 실행:

1. **memory rule 6** (title-based search) — `gh issue list --search "<EPIC>-* in:title parent:CFP-<N>"` (label-based 부재 시 title fallback). 신규 sub-issue 가 다른 session 에 의해 발의되었는가 확인.
2. **memory rule 7** (Epic state poll) — `gh issue view <EPIC> --json state,labels`. Epic 이 다른 session 에 의해 CLOSED 되었는가 확인.
3. **active_sessions[] field check** — Story Issue body `<!-- active_sessions -->` HTML comment block + Story file frontmatter `active_sessions:` array 모두 verify (ADR-085 §결정 2 dual carrier). 본 session 의 entry 가 등록되어 있는가 확인.
4. **lane-entry sentinel** — `gh pr list --search "head:<branch>"` PR existence check. 다른 session 이 이미 PR open 했는가 확인.

위 4-step 모두 통과 시에만 lane entry. 1+ failure → 사용자 dialog 발화 (Inline whitelist 1번 entry, `codeforge:user-dialog-mode` skill 경유) — "parallel session detected, defer / takeover / abandon" 결정.

#### ADR-073 Amendment 2 polling enum cross-ref

본 §3.18 의 4-step polling 은 ADR-073 Amendment 2 §결정 1 transition trigger polling enum 3종 (`lane_spawn` / `pr_open` / `merge_transition`) 의 **4번째 source** (`active_sessions_check`) cross-ref append — ADR-073 Amendment 4 (CFP-1041) cross-ref-only Amendment 정합 (ADR-073 본문 0건 변경 invariant, Amendment 3 = CFP-689 PR #1043 worktree-first self-ownership 3-tuple, #1038 escalation carrier — post-rebase sequence [1,2,3,4] consecutive).

#### Rebase merge 우선 (ADR-085 §결정 4)

lane re-spawn / FIX iter / handoff 시 `git pull --rebase origin main` 우선 (force-push 회피). force-push 필수 영역 = `--force-with-lease=branch:sha` + HEAD-pin pre-flight gate 의무 (`gh api repos/<owner>/<repo>/commits/<branch> --jq .sha` fresh 재고정 후 push). memory `feedback_verify_pin_head_sha` carrier 정합.

#### Handoff baton transfer (ADR-085 §결정 5)

In-flight FIX baton transfer (Session A → Session B handoff) 시 의무:

1. **Session A** — §10 FIX Ledger row append (Orchestrator monopoly, fix-event-v1 contract) + active_sessions[] entry update `last_heartbeat_kst` + Story §9 evidence write + `git push origin <branch>`.
2. **Session A** — handoff comment to Story Issue `[handoff:CFP-NNNN]` (comment-prefix-registry-v1 14번째 entry — 별 sub-CFP carrier).
3. **Session B** — lane entry 4-step polling 통과 후 `git pull --rebase origin <branch>` + active_sessions[] entry append + fix_iter_ownership populate (handoff_from / handoff_to / fix_iter_number / handoff_at_kst / handoff_reason).

handoff_reason enum: `context-budget-exhausted` / `user-redirect` / `structural-restart-ADR-053` / `other`.

#### Wave 1 vs Wave 2 progression

- **Wave 1 (현재)**: declarative-only (ADR-082 §결정 6 + ADR-070 §D5 retain pattern 답습). Orchestrator self-discipline + lane PL spawn 직전 manual 4-step polling.
- **Wave 2 (별 sub-CFP carrier)**: mechanical wire — `templates/scripts/check-active-sessions-presence.{sh,py}` + `templates/scripts/check-lane-entry-ownership.{sh,py}` + `templates/github-workflows/active-sessions-presence.yml` + `templates/github-workflows/lane-entry-ownership-verify.yml` + bats test suite (evidence-checks-registry `active-sessions-presence` + `lane-entry-ownership-verify` 2 entry warning tier deferred-followup, ADR-060 §결정 5 정합).

#### Cross-ref

- ADR-085 §결정 1 5-layer disjoint 표 (ADR-082 §결정 1 4-layer 표 verbatim 답습 + 5번째 row Multi-session coordination 신설) — coordination axis disjoint complement.
- ADR-073 Amendment 4 + ADR-082 Amendment 3 cross-ref-only Amendment (본문 0건 변경 invariant).
- 8 parallel race incidents single session lineage evidence (CFP-953/946/949/932/954/991/967/1014, 2026-05-18 ~ 2026-05-19 KST) — ADR-045 §D-9 cross_story_pattern_adr_trigger pattern_count ≥ 8 reach escalation_action `adr_draft_emitted` 산물.

---

