# `docs/stories/<KEY>.md` Story File Structure Template

GitHub Story Issue 1건당 `docs/stories/<KEY>.md` 파일 1개. 요구사항 접수부터 Phase 2 PR merge까지 모든 컨텍스트·설계·개발 서사가 이 파일로 누적.

**사용 대상**: 모든 lane plugin (자기 owner section 갱신, codeforge-{requirements,design,develop,test,pmo,review} CLAUDE.md self-write 표 참조), Orchestrator (§10 FIX Ledger + general docs/** 처리), 모든 에이전트 (파일 경로 + 섹션 번호 참조해 read-only fetch via `Read`)

**위치**: `docs/stories/<KEY>.md` (KEY = `<github.story_key_prefix>-N`, 예: `PLG-7`). 제목 H1 `<KEY>: <한 줄 요약>`.

**자동 생성**: `story-init.yml` Action이 사용자가 GitHub Issue Form (story.yml) 제출 시 자동:
1. 다음 KEY 번호 계산 (`Glob(docs/stories/<PREFIX>-*.md)` max+1)
2. 파일 신규 생성 (§1 verbatim, §2-11 placeholder)
3. Phase 1 PR 자동 open
4. Issue body를 docs file 링크로 변환

각 lane plugin 이 Action 후 자기 owned section 갱신 (codeforge-{requirements,design,develop,test,pmo,review} CLAUDE.md self-write 표).

---

## 라벨 (GitHub Issue labels)

GitHub Issue (Story 1건)에 부착되는 라벨:

- `type:story` 필수
- `phase:*` (single-active, phase-label-invariant.yml Action이 강제) — 7종 중 1개
- `gate:design-review-pass` (Phase 1 PR mergeable 전제, 설계 리뷰 PASS 후 부착)
- `gate:security-test-pass` (Phase 2 PR mergeable 전제, 보안 테스트 PASS 후 부착)
- `fix:*-retry` (FIX 루프 누적, fix-ledger-sync.yml Action이 자동 부착)
- `component:*` (consumer overlay `labels.components`)
- `adr:NNN` (관련 ADR)

§1 변조 금지 invariant는 `story-section-1-immutable.yml` Action이 강제 (PR에서 §1 line range 변경 시 자동 reject).

---

## Frontmatter (YAML metadata)

Story file 시작 부 `---` ... `---` block. 표준 필드 + multi-repo system 활성 시 신규 4 필드.

### 표준 필드 (모든 Story 적용)

| 필드 | 타입 | required | 의미 |
|---|---|:-:|---|
| `key` | string | yes | Story KEY (예: `CFP-342`, `MCT-112`) |
| `title` | string | yes | 한 줄 요약 |
| `status` | string | yes | phase 라벨 mirror (`phase:요구사항` ~ `phase:보안-테스트`) |
| `type` | enum | yes | `story` / `epic` |
| `date` | YYYY-MM-DD | yes | Story 생성 일자 — **KST 일자 의미** (ADR-079 §결정 2, `2026-05-16` = `2026-05-16 KST`). date-only 형식 의무 (zoned 형식 아님 — Korea 고정 +9, DST 영구 부재로 일자 의미 모호성 없음) |
| `github_issue` | string | yes | `<owner>/<repo>#<N>` 형식 |
| `epic_dependencies` | list | optional | ADR-020 §결정 3 — `[{type, target, repo}]` |
| `epic_owner_repo` | string \| null | optional | ADR-020 §결정 1 — Epic owner repo (`null` = 단일 repo) |
| `carrier_story` | string \| null | optional | ADR-062 §결정 1 — 본 Story 가 자신이 정의하는 protocol 의 carrier 인 경우 자기 자신 KEY (예: `CFP-407`). non-carrier = 미선언 (default `null`) |
| `bootstrap_exempt_protocols` | list of typed key | optional | ADR-062 §결정 1 — typed key list `"<type>:<identifier>"`. 5 standard prefix: `adr` / `contract` / `policy` / `workflow` / `script` (예: `["adr:ADR-062", "policy:todowrite-progress-visualization"]`). `carrier_story` 선언 시 의무 |
| `issue_origin` | enum | optional | **ADR-082 Amendment 2 (CFP-1016)** — `user_authored_issue_form` (default, fallback when missing) / `orchestrator_authored_followup` (Orchestrator 가 retro time / brainstorm Phase 0 후속 / ADR amendment carrier reservation / pattern_count escalation forcing function 산물로 Issue 본문 author 한 경우). `orchestrator_authored_followup` 시 §2.1 verified state table 작성 의무 (Orchestrator-authored Issue body pre-publish verify mandate forcing function) |
| `active_sessions` | list of dict | optional | **ADR-085 §결정 2 (CFP-1041)** — 복수 Claude Code session 동시 작업 시 ownership coordination dual carrier (Story Issue body `<!-- active_sessions -->` HTML comment block + 본 frontmatter array). 각 entry = 5-tuple: `git_identity` (string, 예: `"MinCheol Cho <mccho@mclayer.it>"`) / `worktree_path` (string, ADR-040 worktree namespace 정합) / `entry_phase` (enum: `"Phase 1 requirements"` \| `"Phase 1 design"` \| `"Phase 1 design-review"` \| `"Phase 2 develop"` \| `"Phase 2 code-review"` \| `"Phase 2 security-test"` \| `"Phase 2 integration-test"` \| `"Phase 2 retro"`) / `entered_at_kst` (ISO 8601 zoned strict `YYYY-MM-DDTHH:MM:SS+09:00`, ADR-079) / `last_heartbeat_kst` (ISO 8601 zoned strict, update on lane phase transition + 매 PR open / commit push 직후). Optional handoff field = `fix_iter_ownership` (dict, ADR-085 §결정 5): `handoff_from` / `handoff_to` / `fix_iter_number` / `handoff_at_kst` / `handoff_reason` (enum: `"context-budget-exhausted"` \| `"user-redirect"` \| `"structural-restart-ADR-053"` \| `"other"`). backward-compat: 기존 미명시 Story default `[]` (Wave 1 declarative — Wave 2 mechanical lint promotion 시 점진 ratchet (강화 방향 단계적 적용 — 정책 scope/강도 양적 증분, ADR-058 §결정 5), `active-sessions-presence` evidence-checks-registry entry warning tier deferred-followup). |

### Multi-repo system 활성 시 신규 4 필드 (CFP-342 / ADR-069)

`project.yaml` 의 `codeforge.stories.repos[]` 블록 활성 시 (ADR-069 §결정 1 opt-in trigger), 신규 작성 Story 의무 필드. 부재 시 = `legacy-hub` 묵시 처리 (ADR-069 §결정 5 backward compat).

| 필드 | 타입 | required | 적용 |
|---|---|:-:|---|
| `story_scope` | enum | conditional | `hub` / `repo` / `legacy-hub` — multi-repo 활성 후 신규 story 의무 |
| `repo` | string | conditional | `story_scope: repo` 시 required — impl repo 이름 (`project.yaml repos[].name` 정합) |
| `hub_story` | string \| null | conditional | `story_scope: repo` 시 optional — parent hub story KEY (단독 repo story = `null`) |
| `delegates` | list of dict | conditional | `story_scope: hub` 시 의무 — `[{story_key, repo, path, status}]`, status enum: `draft` / `in-progress` / `merged` / `cancelled` |

**Backward compat**: 기존 Story (frontmatter 4 필드 부재) = `legacy-hub` 묵시 처리. Rename / move 절대 금지 (ADR-050 §결정 5 invariant).

**Strict mode vs Simplified mode 공존**:
- 단일 repo Story (예: CFP-342 자체) 또는 ADR-020 Mode A consumer = 본 file (`story-page-structure.md`) §1-§14 strict mode
- Multi-repo Mode B consumer 의 hub story / repo story = simplified template (`templates/hub-story.md` / `templates/repo-story.md`) — frontmatter 4 신규 필드 + 본문 5-6 섹션

---

## 섹션 구조 (번호 고정 · 누락 섹션 진입 차단)

> **헤딩 § 표기 (CFP-2293)**: 본 문서는 섹션을 `§N`으로 표기하지만, 실제 story 헤딩의 `§` 기호는 **선택적**이다. `story-init` renderer 는 `## N.` (§ 없음) 헤딩을 생성하며 `scripts/lib/check_story_section_schema.py` 린터는 `## N.` 과 `## §N.` 양쪽을 모두 수용한다 (renderer↔linter 컨벤션 정합).

### §1. 사용자 요구사항 (verbatim — story-section-1-immutable.yml로 변경 차단)
- story-init.yml Action이 사용자 GitHub Issue Form 입력을 verbatim 삽입
- 재작성·요약 금지 (변조 방지)
- §1 line range 변경 시 PR 자동 reject

### §2. 도메인 해석 (DomainAgent)
- 도메인 제약 / 암묵 가정 / 범위 경계 / 우선순위 힌트
- 지식 공백 섹션
- 기존 `docs/domain-knowledge/` 파일 참조 목록

**타이밍**: 파일 생성 시점엔 placeholder (요구사항 레인 진입 전 비어있음). DomainAgent가 Analyst·Researcher와 **병렬 실행** 후 결과 반환하면 RequirementsPL 이 §2 직접 self-write (codeforge-requirements) — 따라서 **Analyst·Researcher는 §2를 입력으로 참조하지 않음** (독립 관점 보장). §5·§6과 같은 사이클에 동시 기록.

#### §2.1 Issue body 가정 vs verified state (ADR-082 §결정 1 layer 1 — Amendment 2 codification, CFP-1016)

**적용 조건** (CONDITIONAL):
- frontmatter `issue_origin: orchestrator_authored_followup` 시 **의무**
- frontmatter `issue_origin: user_authored_issue_form` (default) 또는 frontmatter `issue_origin` 부재 시 **선택** (RequirementsPL 판단 — Issue body 안 verifiable fact claim 존재 시 권장)

**역할**: Orchestrator-authored Issue body 의 fact claim (file path / registry value / lint output / cross-repo state / ADR frontmatter value / amendment count 등) 을 RequirementsPL 이 source direct verify 후 Story §2.1 verified state table 에 row 매핑. Issue body verbatim invariant (§1) 와 disjoint — §2.1 = §1 immutable claim 의 ground truth verification layer.

**4-column schema** (mandatory format when `issue_origin: orchestrator_authored_followup`):

| # | Issue body 가정 | Verified state (direct file/grep evidence + `[verified]` annotation) | Pivot 판정 |
|---|---|---|---|
| 1 | <Issue body verbatim claim 1> | <verify evidence: `git show origin/main:<path>` / `grep -c` / `gh issue view` / `mcp__github__get_file_contents` 결과 + `[verified]` annotation> | <Pivot 1 또는 "Pivot 부재" — 정정 방향 1줄> |
| 2 | <Issue body verbatim claim 2> | <verify evidence + `[verified]`> | <Pivot 2 또는 "Pivot 부재"> |
| N | ... | ... | ... |

**작성 규칙**:
1. **claim atomic** — Issue body 안 fact citation 마다 1 row (composite claim = 분할)
2. **`[verified]` annotation 의무** — verify evidence column 에 verify mechanism (`git show <ref>:<path>` / `grep -c` / `sed -n` / `ls` / `gh issue view` / `mcp__github__get_file_contents` 등) + 결과 + `[verified]` annotation 부착
3. **Pivot 판정** — verified state 가 Issue body 와 일치 시 "Pivot 부재" + 정정 방향 1줄, 불일치 시 "Pivot N" + 정정 방향 (drift 종류: inverted / stale / inexistent / regex FP / filename gap 등)
4. **[verified] / [hypothesis] 분리** — verify 가능 영역 = `[verified]`, LLM ambiguity 영역 = `[hypothesis]` (ADR-052 Amendment 3 marker 4종 정합)
5. **citation ≠ assertion** — Issue body 가 외부 lint output / cross-lane verdict 를 verbatim 인용한 경우 citation (verify 면제, §결정 4) but Orchestrator authorship 시점에 lint output 사실성 verify 의무 (ADR-082 §결정 1 layer 1 (1-B) sub-scope)

**예시 (CFP-1000/CFP-1001/CFP-1002 precedent)**:
- CFP-1000 §2.1 (9-row drift mapping) → 3 inversions catch (`prod-cutover-deputy-evidence` INVERTED + baseline stale + `.claude-work/label-registry-bootstrap.json` inexistent)
- CFP-1001 §2.1 (4 claim verify) → L189 lint regex cross-context FALSE POSITIVE catch (Pivot 1 진단)
- CFP-1002 §2.1 (2 row verify) → ADR-054 filename `-fast-path.md` cited but actual `-story-fast-path.md` catch (Pivot 부재, trivial 1-character-level edit)
- CFP-1016 §2.1 (META self-application) → 본 Story 자체가 Amendment 2 carrier — Issue body 4 claims (CFP-1000 inversions / CFP-1001 lint output / CFP-1002 filename / ADR-082 next amendment_id) verify

**미작성 시** (`issue_origin: orchestrator_authored_followup` 인데도): §2.1 verified state table 부재 = ADR-082 §결정 1 layer 1 (1-B) Wave 1 behavioral violation. Wave 2 mechanical lint (`scripts/check-story-section-issue-origin.sh`, deferred-followup) 가 향후 detect.

### §3. 관련 ADR
- 직접 제약 ADR (verbatim 또는 full 요약)
- 배경 참조 ADR (번호 + 1줄 요약)
- 기존 ADR 갱신·신설 필요 여부

#### §3 도입할 설계 — sub-domain owner (CFP-681 / W1 S2 — CFP-1026 design lane 재편)

> ArchitectAgent (chief author) 가 Change Plan §3 (도입할 설계) 를 작성할 때 code 축 / data 축을 deputy 영역별로 구조화하기 위한 **가이드** (consumer 가 작성하는 Story 의 선택적 sub-section — additive guidance, 기존 §3 작성 흐름 무파괴). deputy 명칭·ownership SSOT = `skills/deputy-mandate/SKILL.md` (5 permanent + 3 CONDITIONAL 매트릭스, ADR-042 Amendment 7 / ADR-014 Amendment 4).

| §3 sub-domain 축 | primary owner | 다루는 설계 결정 | 비고 |
|---|---|---|---|
| **§3 Code 설계** | **CodeArchitect** (Sonnet — single-mandate advocacy, ADR-042 Amd7 §결정 1 (a)) | layered / hexagonal / clean architecture / DDD bounded context / module boundary / dependency direction | 신설 deputy. multi-source synthesis = ArchitectAgent chief (Opus) |
| **§3 Data 구조** | **DataArchitect** (Opus 유지 — DataMigrationArch rename + mandate 확장) | entity / aggregate / value object / DB schema / event schema / DTO / API contract data / persistence model / 데이터 흐름 (+ §11 migration 전체) | DataMigrationArch → DataArchitect rename. §11 schema/migration/rollback + 전체 데이터 구조 primary owner 와 동일 deputy |

- code 축 ↔ data 축 경계 모호 시: module boundary 결정은 CodeArchitect primary + DataArchitect consult, persistence model 결정은 DataArchitect primary + CodeArchitect (module boundary) consult (SKILL.md 매트릭스 `(consult module boundary)` cell 정합).
- doc-only fast-path Story = §3 = `N/A — doc-only fast-path (ADR-054)` 선언 또는 S1 ADR SSOT cross-ref 간결 서술 (실 설계 결정 0 시 sub-domain owner 표 작성 면제).

#### §ubiquitous_language — DDD term + Bounded Context 명시 (ADR-091 §결정 4/§결정 5, CONDITIONAL)

> ADR-091 (ArchitectLane DDD vocabulary governance) carrier. 본 Story 가 도입/사용하는 DDD term 을 **codeforge governance BC 의 Published Language SSOT** (`docs/glossary.md`) 와 정합하게 명시. **vocabulary theater 차단 forcing function** (ADR-091 §결정 7 INV-5) — 어휘 emit 이 spawn decision / review findings / ADR acceptance criteria 를 실제로 변경하지 않으면 본 block 은 실패 (단순 nominal 금지).

**적용 조건** (CONDITIONAL):
- Story 가 DDD 영역 (Bounded Context / Aggregate / Domain Service / Strategic·Tactical Design pattern) 을 **touching** 시 **의무**
- DDD 영역 비-touching Story (typo / link / 단순 doc) = **선택** (작성 면제 또는 `N/A — DDD 영역 비-touching` 1줄 선언)

**3-field schema** (DDD 영역 touching 시 의무):

```yaml
bounded_context: codeforge-governance   # codeforge governance BC | application BC (downstream) | shared-kernel
ddd_terms:                              # 본 Story 가 도입/사용하는 DDD term enumeration (docs/glossary.md anchor 정합)
  - <term>                              # 예: Aggregate (governance BC) / Domain Service / Open Host Service (OHS)
glossary_ref: docs/glossary.md          # Published Language SSOT (content duplication 금지 — link only, ADR-091 §결정 4)
```

**작성 규칙**:
1. **bounded_context 명시 의무** — 본 Story 가 어느 BC 안에서 작동하는지 explicit declare. default = `codeforge-governance` (wrapper / lane plugin Story). application BC (mctrader 등 downstream) 는 별도 SSOT (`mctrader-hub/docs/glossary.md`).
2. **ddd_terms = glossary anchor 정합** — enumerate 한 모든 term 은 `docs/glossary.md` 안 정의 entry 가 존재해야 함 (drift 차단). glossary 외 미정의 DDD term 사용 = `scripts/check-ubiquitous-language.sh` warning tier 가 감지.
3. **동음이의 분리** — `Aggregate` 처럼 governance BC ↔ application BC 동음이의 term 은 BC qualifier 병기 (`Aggregate (governance BC)` vs `Aggregate (mctrader application BC)`, ADR-091 §결정 3 Layer A/B).
4. **anti-pattern 어휘 forbid** — `Big Ball of Mud` / `Smart UI` 등 anti-pattern term 은 design intent (채택 표현) 로 사용 금지 (after-the-fact 분석 description 만 허용, ADR-064 forbid-list 확장 후보 OQ-1).

**lint**: `scripts/check-ubiquitous-language.sh` (warning tier — glossary term drift) + `scripts/check-bounded-context-presence.sh` (warning tier — bounded_context field presence). 둘 다 ADR-091 §결정 6 enforcement layer (Template lint tier).

### §4.0. 관련 코드 경로 목록 (RequirementsPLAgent)
- 변경 대상 파일·클래스·레이어
- 현재 책임 요약

### §4.1. 코드 변경 델타 지도 (ChangeImpactAgent)
- 변경 예상 파일 표 (파일 경로 / 변경 유형 / 변경 이유)
- 영향 컴포넌트 + 인터페이스 파괴적 변경 여부
- 변경 범위 추정 (예상 파일 수 / 테스트 재작성 여부)
- 불확실 영역

### §4.2. 구현 가능성 평가 (FeasibilityAgent)
- 가능성 등급: 자연스러움 / 주의 필요 / 대규모 변경 필요
- 아키텍처 장벽 목록 + 극복 힌트
- 설계 레인 경고 힌트 (ArchitectAgent 전달 대상)
- ADR 충돌 후보

### §4.3. 이전 작업 연속성 분석 (ContinuityAgent)
- 관련 선행 Story 표 (KEY / 관계 유형 / 비고)
- 충돌 가능 ADR 표
- 이미 결정된 사항 (재논의 불필요)
- 재논의 필요 후보 (override/amendment 대상)

### §5. 요구사항 확장 해석 (RequirementsAnalyst)
- 유스케이스 / AC / 엣지 케이스 / 제외 범위 / 암묵 가정
- §5.5 "사용자 확인 필요" (blocking wait 항목)

### §6. 외부 지식 배경 (Researcher)
- Researcher 자체 도출 키워드 커버리지 + 출처 URL
- ADR 정합성 점검 결과
- "외부 지식 보강 불필요" 판정 시에도 사유를 명시 (섹션 생략 금지 — 독립 관점 결과 보존)

### §7. 설계 서사 (ArchitectAgent (chief author) → ArchitectPLAgent 검수)
- Change Plan 링크 (`docs/change-plans/<slug>.md`)
- §1 목적 / §3 도입할 설계 / §4 API 계약 / §7 보안 설계 요약 / §9 분기 선택 요약 미러링 (5-10줄)
  - §7 보안 설계 요약: Change Plan §7의 보안 설계 요약 (1-3줄) 또는 `N/A — <사유>` 그대로 미러링
- CodebaseMapper ↔ RefactorAgent ↔ SecurityArchitectAgent 3-way 대립 결론

#### §7.4 primary 4-sub vs cross-ref shell 2-sub 분류 가이드 (CFP-681 / W1 S2 — ADR-014 Amendment 4 §결정 2)

> InfraOperationalArchitect (OperationalRiskArch rename, Opus 유지) 가 §7.4 운영 리스크를 작성할 때 **설계 시점에 정책 값을 결정하는 primary 4-sub** 와 **policy 값을 evidence-driven 측정 후 결정하는 cross-ref shell 2-sub** 를 구분하기 위한 가이드. sub 번호·분류 SSOT = ADR-014 Amendment 4 §결정 2 표 (`abcd92bf` ground truth) — 본 가이드는 그 mechanical 반영.

| §7.4 sub | 분류 | 작성 시점 결정 가능 여부 | InfraOperationalArchitect 책임 |
|---|---|---|---|
| §7.4.1 DR | **primary** | 설계 시점 결정 | backup / restore / failover policy |
| §7.4.3 Clock sync (CONDITIONAL) | **primary** | 설계 시점 결정 | tolerance budget |
| §7.4.5 Env isolation | **primary** | 설계 시점 결정 | staging-prod 분리 / IP allowlist / network mode boundary containment policy |
| §7.4.6 Container Docker | **primary** | 설계 시점 결정 | restart policy / volume DR / health check / network mode boundary (ADR-033 4 항목) |
| §7.4.2 Cancel-on-disconnect | **cross-ref shell** | policy 값 evidence-driven (측정 후) | Axis 1 측정 대상 정의 + §8.6 pointer / Axis 2 측정 / Axis 3 follow-up policy 결정 |
| §7.4.4 Rate limit | **cross-ref shell** | policy 값 evidence-driven (측정 후) | 동일 3-axis split |

- primary 4-sub = 설계 lane 에서 정책 값 확정. cross-ref shell 2-sub = 설계 lane 에서는 측정 대상 정의 + §8.6 pointer 만 (policy 값 자체는 Phase 1 follow-up PR 에서 실측값으로 결정).
- **§7.4.4/§7.4.2 policy 공백 ↔ FIX root-cause decision table = disjoint axis** (측정 대상이지 실패 원인 아님). DesignReviewPL audit gate = §8.6 cross-ref pointer **존재만 mandatory** (policy 값 공백 자체 PASS — pointer 누락만 FIX). 상세 schema = §8.6.

### §8. 개발 서사 (DeveloperPL + role:dev roster)

#### §8.1 Backend 산출물
#### §8.2 Frontend 산출물
#### §8.3 DataEng 산출물
#### §8.4 InfraEng 산출물 (consumer roster에 따라 추가/생략 가능)

#### §8.5 Impl Manifest (파일 단위 매핑표)
[`impl-manifest.md`](impl-manifest.md) 스키마 따름. DeveloperPL 이 §8.5 직접 self-write (codeforge-develop) → Phase 2 PR에 commit → `subissue-from-impl-manifest.yml` Action이 자동으로 file 단위 sub-issue 생성.

#### §8.6 Integration Test Contract (컴포넌트 경계 2개 이상 Story — CONDITIONAL)

TestContractArchitectAgent(설계 lane deputy)가 설계 단계에 작성. IntegrationTestAgent의 실행 계약 입력.

```yaml
# §8.6 Integration Test Contract
boundary_type: "component_internal" | "multi_service" | "both"
coverage_targets:
  - scenario: "시나리오 이름"
    given: "사전 조건"
    when: "동작 트리거"
    then: "기대 결과"
    related_components:        # blame 절차 tier-1 소스. 이 시나리오가 사용하는 src 경로 목록.
      - "src/orders/order_service.py"   # e.g.
      - "src/exchange/bithumb_client.py"
environment_dependencies:
  db: "test DB seed 요구사항"
  external_api: "WireMock stub 대상 서비스"
  services: "docker-compose 포함 서비스 목록"
isolation_strategy: "ephemeral_container" | "test_db" | "service_mock"
dynamic_test_required: true   # 내부 컴포넌트 정적 mock 금지
```

`related_components[]` — IntegrationTestAgent blame tier-1 입력. blame 절차:
1. 테스트 파일의 `STORY_KEY` 메타데이터로 직접 story_key 확인 (story suite의 경우)
2. `coverage_targets[].related_components[]` 경로를 blame 대상으로 사용 (baseline 실패 시)
3. 미제공 시 test_path import 정적 분석으로 fallback → 그래도 불가 시 ArchitectPL ESCALATE

**면제 조건**: 컴포넌트 경계 0개 Story, doc-only Story.
면제 시 `N/A — <근거 30자 이상>` 필수 (lint 강제).

##### §8.6 evidence-driven 3-axis pointer schema (CFP-681 / W1 S2 — ADR-014 Amendment 4 §결정 2)

§7.4.4 (Rate limit) / §7.4.2 (Cancel-on-disconnect) 가 cross-ref shell 로 분류된 Story 는 policy 값을 설계 시점에 결정하지 않고 evidence-driven 으로 측정 후 결정한다. 이 경우 §8.6 Integration Test Contract 에 다음 3-axis pointer 를 추가한다 (InfraOperationalArchitect 가 Axis 1 정의, TestContractArchitectAgent §8.6 통합).

```yaml
# §8.6 evidence-driven 3-axis pointer (§7.4.4 / §7.4.2 cross-ref shell 적용 Story 만)
evidence_driven_pointers:
  - shell_sub: "§7.4.4"            # 또는 "§7.4.2"
    axis_1_phase1_measure_target: "측정 대상 정의 (예: live exchange rate-limit 429 응답 빈도 / window)"   # 설계 lane — DesignReviewPL audit 영역
    axis_2_phase2_measurement: "실측 수행 방식 (예: IntegrationTest live probe N회 / shadow traffic)"        # Phase 2 — FIX 루프와 disjoint (측정 단계)
    axis_3_phase1_followup_policy: "실측값으로 결정할 policy 항목 (예: backoff 곡선 / token bucket 용량)"      # Phase 1 follow-up PR — 실측 후 결정
    policy_value: null              # 설계 시점 공백 허용 (null) — 측정 후 follow-up PR 에서 채움. 공백 자체 PASS
```

**audit gate 명문화** (DesignReviewPL 경량 audit 의무):
- §8.6 evidence_driven_pointers **pointer 존재만 mandatory check**. `axis_1`/`axis_2`/`axis_3` 3 키가 모두 존재하면 PASS.
- `policy_value: null` (정책 값 공백) **자체는 PASS** — 측정 후 결정 대상이므로 설계 시점 공백이 정상.
- **pointer 누락만 FIX** (3-axis 키 중 하나라도 부재 시). policy 값이 공백이라는 사실 자체를 FIX 사유로 삼지 않는다.
- **policy 공백 ↔ FIX root-cause decision table = disjoint axis**: §7.4.4/§7.4.2 의 policy 값 미결정은 "측정 대상"이지 "실패 원인"이 아니다. FIX 루프 (구현/설계 원인 판정) 와 별개 축 — cross-pollinate 금지 (ADR-014 Amendment 4 §결정 2 정합, CFP-681 §2.3 carry-over invariant 3).
- primary 4-sub (§7.4.1 DR / §7.4.3 Clock / §7.4.5 Env / §7.4.6 Container) = 설계 시점 policy 값 확정 의무 — evidence_driven_pointers 대상 아님 (cross-ref shell 2-sub 한정).

### §9. 품질 게이트 이력

#### §9.0 Clarification 재스폰 이력 (FIX 아님)

PL(RequirementsPL / ArchitectPLAgent)이 병렬 서브 에이전트 결과 통합 중 추가 질의를 위해 Orchestrator 경유 재스폰 요청한 이력. FIX 루프(§10)와 구분 — 재스폰은 아직 게이트 실패가 아님.

| # | 시각 | 레인 | 재스폰 대상 | Clarification 사유 | 이전 출력 ref | 결과 |
|---|------|------|-------------|-------------------|---------------|------|
| 1 | ISO8601 | 요구사항 | ResearcherAgent | {PL이 추가 조사 요청한 주제} | §6 initial | §6 보강 |
| 2 | ISO8601 | 설계 | RefactorAgent | {ArchitectPLAgent가 특정 제안 재해석 요청} | §7 Change Plan draft v1 | §7 갱신 |

- 같은 에이전트 **2회 한도** — 3회째 필요성 발생 시 사용자 ESCALATE로 전환
- Orchestrator append-only 관리 (CFP-32, 행 삭제·수정 금지)

#### §9.1 설계 리뷰 Iteration N
- Claude · Codex severity counts + 주요 findings + DesignReviewPL 판정
- Iteration N마다 append
- **review-verdict-v4 packet yaml block embed 권장 (CFP-410)** — iteration table 다음 fenced ```yaml ... ``` block 으로 packet 5 의무 field (`contract: review-verdict-v4` / `lane: design` / `story_key` / `iteration` / `pl_recommendation`) + 선택 field (`worker_dialog_rounds` / `findings[]`) 명시. free-form markdown 대비 정보 손실 최소화 + `scripts/check-story-section-9-typed.sh` warning-tier 검증 대상.
- **Gate evidence row (CFP-85)** — PASS verdict 시 의무 추가:
  - PR URL (Phase 1 PR)
  - Expected gate label: `gate:design-review-pass`
  - Observed gate label timestamp (ISO8601, gh API verify 시점)
  - Observed phase label transition (`phase:설계-리뷰` → `phase:구현`)

#### §9.2 구현 리뷰 Iteration N
- 동일 형식 + Gate evidence row (CFP-85) — PASS verdict 시 의무 추가:
  - PR URL (Phase 2 PR)
  - Expected: phase transition (`phase:구현-리뷰` → `phase:구현-테스트`)
- **review-verdict-v4 packet yaml block embed 권장 (CFP-410)** — `lane: code` (§9.1 패턴과 동일). §9.3 (`lane: code` 또는 N/A) / §9.4 (`lane: security`) 도 동일 권장.
  - Observed phase label timestamp

#### §9.3 구현 테스트 레인
- 기능 통과/실패 + 성능 baseline 대비 변동
- Gate evidence row (CFP-85) — PASS verdict 시 phase transition (`phase:구현-테스트` → `phase:보안-테스트`) timestamp

#### §9.4 보안 테스트 레인
- 1차 layer 결과 요약 (Dependabot / CodeQL / Secret Scanning / Push Protection)
- Claude · Codex severity counts + 주요 findings + SecurityTestPL 판정
- Iteration N마다 append
- **Gate evidence row (CFP-85, terminal)** — PASS verdict 시 의무 추가:
  - PR URL (Phase 2 PR)
  - Expected gate label: `gate:security-test-pass`
  - Observed gate label timestamp (ISO8601)
  - Phase label terminal state (`phase:보안-테스트` 유지 또는 Issue close 시점)
  - **Issue close timestamp** — Story Issue close 시점 기록 (lane plugin 의무 — phase progression audit trail)

#### §9 Gate evidence audit format (CFP-85 신규)

각 §9.x PASS verdict row 옆에 다음 형식으로 gate evidence 표 신설:

```markdown
**Gate evidence**:
| PR | Expected | Observed label | Verified at | Phase transition |
|---|---|---|---|---|
| <PR URL> | gate:design-review-pass | gate:design-review-pass ✅ | 2026-MM-DDTHH:MM:SSZ | phase:설계-리뷰 → phase:구현 (2026-MM-DDTHH:MM:SSZ) |
```

본 표 = audit reproducibility 보장 — GitHub API 라벨 verify 가 향후 막혀도 file-evidence 로 phase progression audit 가능.

### §10. FIX Ledger (FIX 카운터 SSOT)

**현재 schema** = fix-event-v1 v1.3 (CFP-842, 11 column). v1.x optional 누락 시 backward-compat (column 생략 또는 null 허용).

| Iter | 시각 | 레인 | 트리거 | 원인 판정 | 재실행 범위 | RESET? | debate_artifact_ref | reasoning_carryover | affected_scope | affected_paths_with_depth |
|------|------|------|--------|-----------|-------------|--------|---------------------|---------------------|----------------|---------------------------|
| 1    | ISO8601 | 설계-리뷰 | ... | 설계 | ... | — | null | null | single-file | null |
| ... |

**Column SSOT** = [fix-event-v1 §2 Schema](../docs/inter-plugin-contracts/fix-event-v1.md). v1.3 신규 2 column:
- `affected_scope` — enum (single-file / cross-module / cross-repo / cross-plugin), optional, RESET 결정 input
- `affected_paths_with_depth` — array of {path, depth}, **broken-link / path 정정 FIX 시 의무** (그 외 optional). 누락 시 `fix-event-depth-scope-presence` warning-tier lint 적발

Orchestrator (또는 Orchestrator-owned delegate subagent — ADR-031 §결정 1 Amendment 1) 가 append-only 관리 (CFP-32 monopoly, 행 삭제·수정 금지). "현재 사이클" count는 RESET 마커 이후 iteration만 합산. §10 commit이 main에 push되면 `fix-ledger-sync.yml` Action이 자동:
- Story Issue에 `[FIX #N]` 코멘트 mirror
- `fix:<레인>-retry` 라벨 부착

기존 7/8/9-column row 도 valid (v1.x backward-compat). v1.3 column 추가는 trailing optional column 추가 — `fix-ledger-sync.yml` regex 비충돌.

### §10.5 Git Ops Log (CFP-139 / GitOpsAgent self-write)

GitOpsAgent (codeforge-pmo plugin) 가 본 Story 진행 중 발생한 git operation event 를 typed 으로 누적. `git-ops-event-v1` contract 참고.

#### Schema

```yaml
git_ops_log:
  - event_id: <UUID>
    event_type: WORKTREE_CREATE | WORKTREE_PRUNE | BRANCH_MERGE_OK | BRANCH_MERGE_CONFLICT | BRANCH_TREE_DECOMPOSE | STALE_GC
    parent_branch: <branch>
    child_branch: <branch> | null
    worktree_path: <path> | null
    timestamp: ISO8601 UTC
    triggered_by: Orchestrator | <PL agent> | PMOAgent | scheduler
    outcome: SUCCESS | CONFLICT | ERROR
    conflict_detail: <text> | null
    related_team_name: TEAM-<LANE> | null
```

#### 작성 규칙

- GitOpsAgent self-write 영역 — 다른 agent / Orchestrator 가 변경하지 않음
- 매 git ops event 마다 row 추가 (append-only)
- BRANCH_MERGE_CONFLICT row 의 conflict_detail 은 의무 (file path + line range)
- STALE_GC row 는 SessionStart hook 자동 trigger 시 생성

#### Bypass

`BYPASS_GIT_OPS_LOG=1` + `BYPASS_GIT_OPS_LOG_REASON` env 시 skip (chore commit 등). 단 substantive change 면 skip 금지.

#### Cross-ref

- CFP-139 (carrier)
- ADR-035 (worktree convention)
- ADR-036 (agent teams)
- `docs/inter-plugin-contracts/git-ops-event-v1.md` (contract SSOT)
- codeforge-pmo `agents/GitOpsAgent.md` (writer)

### §11. 참조
- GitHub Issue URL: `https://github.com/<org>/<repo>/issues/<N>`
- Phase 1 PR URL (merged)
- Phase 2 PR URL (merged)
- Change Plan 링크 (`docs/change-plans/<slug>.md`)
- 관련 ADR 링크 (`docs/adr/ADR-NNN-<slug>.md`)
- **회고 (PMOAgent 작성, CFP-138 / ADR-045 mandate)**:
    - `retro_file: <relative-path-or-cross-repo-url>` — retro markdown file path (예: `<internal-docs>/wrapper/retros/2026-MM-DD-cfp-NNN-<slug>.md`)
    - `retro_summary: <one-paragraph-summary>` — max 500자 한 단락 요약
    - `learnings_count: <integer >= 0>` — retro 안 학습 항목 개수 (PMOAgent count)
    - `feedback_back_to_codeforge: <Issue link list or empty []>` — codeforge improvement 발견 시 Issue 링크 (label: `codeforge-improvement` 또는 `from-mctrader-debut` 등)
- **Migration policy** (ADR-045 D-5, backward compat): 본 schema = 신규 Story (CFP-138 merge 이후 close) 부터 strict mode. 기존 close Story file 100+ 의 §11 = vague placeholder (`- 회고 (PMOAgent 작성)`) 유지 — retroactive 미처리 ([ADR-045](../archive/adr/ADR-045-story-retro-mandatory-trigger.md) §결정 5 정합).

### §12. Sonnet Decision Log (CFP-59 / CFP-61 / ADR-022)

Story 내 모든 substantive decision 의 Sonnet final pick 기록. per-Story append-only.

| packet_id | trigger | options_count | decider_pick | override? | audit_result | timestamp |
|-----------|---------|---------------|--------------|-----------|--------------|-----------|
| CFP-NN-001 | brainstorming-constraint | 4 | A | no  | direct       | ISO8601 |
| CFP-NN-002 | option-formulation       | 5 | C | yes | sanity-PASS  | ISO8601 |
| CFP-NN-003 | review-verdict           | 2 | FIX | yes (pl: PASS) | direct | ISO8601 |

- `packet_id`: `<KEY>-<3-digit seq>` (decision-packet-v2.1).
- `trigger` enum 5: option-formulation / fix-root-cause / codex-ambiguity / brainstorming-constraint / **review-verdict** (CFP-61 NEW).
- `decider_pick`: options[].id picked by Sonnet (`claude-sonnet-4-6`). review-verdict trigger 시 = `sonnet_final_status` (PASS|FIX 이진, contract-fixed per ADR-022 §결정 4). blocked / timeout / suspended / reopen 케이스 = `<none>` 또는 `<blocked>` (아래 failure-state 표 참조).
- `options_count`: review-verdict 시 = 2 (PASS|FIX 이진 선택지). Trigger 5 의 option set = contract-fixed — Sonnet 가 추가 / 삭제 / rename / synthesize 금지 (ADR-022 §결정 4 invariant).
- `override?`: PL pl_recommendation reduce binary != sonnet_final_status 시 yes. FIX_DISCRETIONARY → FIX 로 reduce 시 override 아님 (PL 도 issue 인지). PASS → FIX 또는 FIX → PASS 시 override.
- `audit_result` enum 6: direct (override 없음) / sanity-PASS / sanity-FAIL / decider-suspended / user-escalation / **review-reopen** (CFP-61 NEW — packet_requires_review_reopen 발화 시).
- Detailed packet artifact = `<internal-docs>/<plugin-folder>/decisions/<packet_id>.yaml` (full v2.1 schema, includes `decider_decision.model` field + `review_lane_context` when trigger=review-verdict).
- 첫 5 review-verdict trigger packet scheduled self-audit (schema 검증 + invariant 충족 + override rate baseline).
  review-verdict trigger 한정 (option-formulation / fix-root-cause / codex-ambiguity / brainstorming-constraint trigger 별도 audit policy 적용 — ADR-019 §결정 7 그대로).

Schema SSOT: [decision-packet-v2.1](../docs/inter-plugin-contracts/decision-packet-v2.md).

ADR-018 의 §12 "Gemini Decision Log" superseded by 본 §12 (CFP-59 / ADR-019). ADR-019 §12 → ADR-022 §12 (CFP-61 trigger enum 5 + failure-state rows).

**Failure-state §12 row format (decision_state ≠ decided 인 케이스, ADR-022 §결정 7 mirror)**:

| decision_state | options_count | decider_pick | override? | audit_result | reason 컬럼 |
|---|---|---|---|---|---|
| `blocked_packet_incomplete` | 0 | `<blocked>` | n/a | user-escalation | `pl_recommendation:ESCALATE_PACKET_INCOMPLETE` |
| `decider_timeout` | 2 | `<none>` | n/a | user-escalation | `attempts[].outcome:timeout` (또는 malformed) |
| `decider_suspended` | 2 | `<none>` | n/a | decider-suspended | `attempts[].outcome:decider_suspended` (Sonnet quota / auth) |
| `review_reopen_requested` | 2 | `<none>` | n/a | review-reopen | `attempts[].outcome:packet_requires_review_reopen` |
| `write_partial` (decided 후 write 일부 실패) | 2 | `<sonnet_final_status>` | (정상) | user-escalation | `write_errors[].step:<failed step>` |

`<blocked>` / `<none>` 은 literal placeholder string 으로 §12 row 에 기재 (machine-readable enum value).

**§10 FIX Ledger 원인 판정 컬럼 evidence (CFP-61 부터)**:
- 정상 (PL≡Sonnet): `<원인>` (decider:claude_sonnet)
- Override (PL≠Sonnet): `<원인>` (decider:claude_sonnet, override: pl_recommendation=<X> sonnet_final=<Y>)

**§10 append-only resolution rule**: §10 row 는 append-only (CFP-32 monopoly). Iteration N FIX → iteration N+1 PASS 시점에 row N 이 mutate 되지 않음 (CFP-32 monopoly + CFP-61 §4.7.1 명시). 같은 cycle 내 PASS 회복은 §9 의 다음 iteration PASS row + phase/gate label transition 으로 외부 visible. RESET 마커는 별도 lane 의 cascading retry 때만 사용.

### §13. Live Operational Discipline (CONDITIONAL — Live touching Story 만 의무)

CONDITIONAL trigger: Story 가 **real funds / live exchange API / production credential / live order placement** 중 하나 이상 touching 시 본 §13 의무. Backtest/Paper-only Story = 미작성 (또는 `N/A — backtest/paper only` 명시).

**필수 필드 11종**:

| # | 필드 | 설명 | 예시 |
|---|------|------|------|
| 1 | Vault path | Secret 저장 위치 (per-exchange / per-account isolation) | `mctrader/live/bithumb/spot/main/{connect_key, secret_key}` |
| 2 | Runtime injection | Secret 주입 방식 (영구 저장 금지) | `1Password CLI subprocess → process-local env (lifetime: process only)` |
| 3 | Key permission | API key 권한 scope | `order:create + order:cancel + read; withdrawal:DISABLED` |
| 4 | IP allowlist | 거래소 측 IP 제한 | `Bithumb: <발급 시점 IP>; CI/CD: 미허용` |
| 5 | Withdrawal off proof | 출금 비활성 verify (screenshot / API response) | `Bithumb account settings — withdrawal disabled (2026-MM-DD)` |
| 6 | First-trade cap | 실거래 첫 한도 (engine call site enforce) | `KRW 10,000 (~7-8 USD), 단일 round trip` |
| 7 | Kill switch trigger | 자동 발동 조건 + manual override 절차 | `auto: drawdown / max_exposure / rate_limit / KRW_drift`<br>`manual: operator-action-v1 (UI/CLI)` |
| 8 | Operator approval | 실거래 진입 승인 절차 | `--confirm-live + ADR-008 D4 3-condition AND` |
| 9 | Reconciliation invariant | engine ↔ 거래소 ledger 정합 검증 | `KRW position drift < 1 KRW; partial fill 8-state lifecycle preserve; fee_actual ≠ fee_expected drift threshold` |
| 10 | Runbook | 운영 절차 (first-trade / kill-switch / incident) link | `docs/runbooks/live-first-trade.md`, `kill-switch-trigger.md`, `incident-response-7step.md` |
| 11 | Rollback | 비상 회복 경로 (real money 비가역 case 포함) | `kill switch trigger + open order cancel + key revoke + reconciliation`; 실 자금 손실 case = forward-only (rollback 불가) |

**미작성 시 (Live touching 인데도)**: SecurityTest lane P0 차단 (review verdict FIX, 본 §13 누락 = 보안 설계 결함). DesignReview lane 도 §7 / §11 / §8.5 cross-ref 부재 시 P0 차단.

**ADR cross-ref**: 본 §13 = ADR (consumer-side Live policy ADR — 예: mctrader ADR-012 Live Rollout Policy) 의 contract enforcement. Story-level §13 작성 시 해당 ADR cross-ref 의무.

### §14. Lane Evidence (CFP-126 / ADR-031 — committed lane-spawn evidence trail)

**Effective date**: ADR-031 Accepted 후 신규 Phase 2 PR 부터 (retroactive 미처리 — ADR-031 §결정 5).

**의무 trigger**: 매 lane (요구사항/설계/설계-리뷰/구현/구현-리뷰/구현-테스트/보안-테스트) spawn 시 wrapper Orchestrator (또는 Orchestrator-owned delegate subagent — ADR-031 §결정 1 Amendment 1) 가 row append (start) + return 직후 row update (end).

**Schema** (12 field YAML block, CFP-126-002 Codex review 정합):

```yaml
lane_evidence:
  - lane: 요구사항                    # 한국어 7종 중 하나
    iteration: 1                     # 1+, lane local row index (FIX 시 multiple row)
    agent: RequirementsPLAgent (codeforge-requirements@mclayer)
    spawned_at: 2026-MM-DD T HH:MM Z # ISO8601 UTC, spawn 직전 (contract field layer — ADR-079 §결정 9, UTC strict 보존)
    returned_at: 2026-MM-DD T HH:MM Z # ISO8601 UTC, return 직후 (contract field layer — ADR-079 §결정 9, UTC strict 보존). output_status=spawned 시 empty
    output_status: completed         # spawned | completed | failed | escalated | bypass
    outcome: PASS                    # PASS | FIX | SKIPPED — output_status=completed 시만 채움
    pr_ref: <org>/<repo>#NNN         # Phase 2 PR ref
    decision_packet_ref: null        # optional — Sonnet decision archive yaml id (예: CFP-NN-001)
    transcript: <inline 50자 OR internal-docs decision archive link>
    spawn_id: null                   # optional UUID (retry idempotency, Phase 2 implementation 결정)
    fix_iteration: null              # optional — §10 FIX Ledger row index cross-ref (FIX retry row 시)
  - lane: 설계
    ...
```

**Field semantics**:

| # | Field | Required | 의미 |
|---|---|---|---|
| 1 | lane | yes | 요구사항/설계/설계-리뷰/구현/구현-리뷰/구현-테스트/보안-테스트 |
| 2 | iteration | yes | Lane local 1+ (FIX 시 multiple row) |
| 3 | agent | yes | PLAgent name + plugin |
| 4 | spawned_at | yes | ISO8601 UTC (contract field layer — UTC strict 보존, ADR-079 §결정 9). **본문 markdown 표 Start column = KST `+09:00` (display layer, ADR-079 §결정 2) — 두 layer disjoint co-exist** |
| 5 | returned_at | conditional | output_status=completed 시 의무. ISO8601 UTC (contract field layer — UTC strict 보존, ADR-079 §결정 9). **본문 markdown 표 End column = KST `+09:00` (display layer)** |
| 6 | output_status | yes | partial-row write semantic — `spawned` (in-flight) / `completed` / `failed` / `escalated` / `bypass` |
| 7 | outcome | conditional | output_status=completed 시 의무. PASS/FIX/SKIPPED |
| 8 | pr_ref | yes | Phase 2 PR ref |
| 9 | decision_packet_ref | optional | Sonnet archive yaml id |
| 10 | transcript | yes | 50자 inline OR link |
| 11 | spawn_id | optional | UUID retry idempotency |
| 12 | fix_iteration | optional | §10 FIX Ledger row index — FIX retry row 한정 |

**Iteration vs fix_iteration cross-validation** (Codex P1 #3):
- `iteration` = lane local spawn 순번
- `fix_iteration` = §10 FIX Ledger row index (FIX retry 일 때)
- lint `scripts/check-lane-evidence.sh` 가 §14 의 fix_iteration ↔ §10 row 정합 검증

**Bypass mechanism** (ADR-031 §결정 4):
- `BYPASS_LANE_EVIDENCE=1` + `BYPASS_LANE_EVIDENCE_REASON="<reason>"` 양 env 의무
- 사용 시 row append (output_status=bypass) + Phase 2 PR description `BYPASS:` 명시 + audit Issue 자동 생성 (ADR-026 패턴)

**Phase-gate-mergeable enforcement** (ADR-031 §결정 3):
- Phase 2 PR (label `phase:보안-테스트`) → PR description regex `^## Lane evidence$` + 7-row valid 검증
- 부재/invalid → `action_required` block
- `type:epic` / doc-only fast-pass (CFP-106) 변경 없음

**`.claude-work/progress/<KEY>.md` 와 분리** (CFP-20 NG6):
- §14 = committed authoritative SSOT
- `.claude-work/progress/` = gitignored ephemeral cache (non-authoritative)
- 두 file 충돌 시 §14 priority

---

## Epic Story Condensed Mode (CFP-84)

mctrader debut audit Issue [#181](https://github.com/mclayer/plugin-codeforge/issues/181) P1-4 finding: Epic-level Story (frontmatter `type: epic`) 가 일반적으로 §§ 일부 collapsed/축약 형태로 작성됨 (예: MCT-25, MCT-50 의 §5-6 결합 / §8 부재). Implementation child Story 가 details 를 carry 하므로 Epic 자체의 §8 dev narrative / §10 FIX Ledger 등 일부 섹션 = 의미 X.

본 condensed mode = Epic Story (frontmatter `type: epic`) 만 적용. Implementation Story (`type: story`) 는 § 1-§13 strict mode 유지.

### Epic Story 섹션 의무 매트릭스

| § | 섹션 | Implementation Story (`type: story`) | Epic Story (`type: epic`) |
|---|---|:-:|:-:|
| §1 | 사용자 요구사항 (verbatim) | 의무 | **의무** (story-section-1-immutable.yml 동일 적용) |
| §2 | 도메인 해석 (DomainAgent) | 의무 | 권장 (Epic-level brief OK) |
| §3 | 관련 ADR | 의무 | **의무** (Epic = ADR-driven 결정 source) |
| §4.0 | 관련 코드 경로 목록 | 의무 | 선택 (Epic-level scope 만 명시 OK) |
| §4.1 | 코드 변경 델타 지도 | 의무 | 선택 |
| §4.2 | 구현 가능성 평가 | 의무 | 선택 |
| §4.3 | 이전 작업 연속성 | 의무 | 선택 |
| §5 | 요구사항 확장 해석 | 의무 | 선택 (`§5-6 결합` 허용) |
| §6 | 외부 지식 배경 | 의무 | 선택 (`§5-6 결합` 또는 `N/A — Epic-level` 허용) |
| §7 | 설계 서사 (ArchitectAgent) | 의무 | **의무** (Epic-level design choice = ADR-driven) |
| §8 | 개발 서사 (DeveloperPL) | 의무 | **N/A 명시 의무** ("N/A — child Story 가 carry" 명시) |
| §9 | 품질 게이트 이력 | 의무 | Epic 닫는 시점 child verdict aggregate (선택) |
| §10 | FIX Ledger | 의무 | **N/A 명시 의무** (Epic 자체 FIX 없음 — child Story 가 별도 §10) |
| §11 | 참조 (회고 + child Story link) | 의무 | **의무** — child Story Issue link 모음 + EPIC-RESULTS reference |
| §12 | Sonnet Decision Log | 발생 시 | **의무** (Epic-level substantive 결정 누적) |
| §13 | Live Operational Discipline | CONDITIONAL | CONDITIONAL (child 영향 시) |

### "결합" 허용 패턴

다음 형식 만 허용:
- `## §5-6. 요구사항 확장 + 외부 지식 (combined for Epic)` — sub-content 안에 §5 항목 + §6 항목 가시 분리
- `## §X-Y. <combined title>` — heading 에 결합 명시 + 내용 안 sub-항목 분리

거부 (lint enforce — CFP-84 Phase 2 follow-up):
- 단순 `## 5-6` (heading 에 § 누락 시) → reject
- 결합 표현 없이 한 섹션이 두 § 내용 mix → reject
- §1, §3, §7 같은 mandatory 섹션 결합 → reject

### N/A 명시 형식

Implementation 무관한 §8 / §10 등 = **명시적 "N/A — <사유>" 작성 의무** (단순 섹션 omit = lint reject):

```markdown
## §8. 개발 서사

N/A — Epic Story (type=epic). 5 child Story (MCT-13 ~ MCT-17) 가 §8 dev narrative carry. EPIC-RESULTS-MCT-12.md §2 Phase decomposition 참조.

## §10. FIX Ledger

N/A — Epic 자체 FIX 없음. Child Story 별 §10 (별도 file) + EPIC-RESULTS §9 CI iteration 통계 참조.
```

### Epic close 시 §11 의무 (Story §11 ↔ EPIC-RESULTS link)

Epic Story 의 §11 회고 블록 = Epic close PR (Phase N+1) 동반 작성. EPIC-RESULTS-<EPIC_KEY>.md 가 별도 artifact 으로 작성됨 ([CFP-83 epic-results template](epic-results.md)) — Story §11 = link + 1-paragraph summary 만 보유.

```markdown
## §11. 참조

### Child Story
- mclayer/<repo>#<issue>: <CHILD-1> — <one-line summary>
- ...

### Epic close artifact

EPIC-RESULTS-`<EPIC_KEY>`.md location SSOT = [`docs/doc-locations.yaml`](../docs/doc-locations.yaml) `epic_results` row ([ADR-041](../docs/adr/ADR-041-doc-location-registry.md)).

Link path 작성 가이드:
- **동일 repo 내** (Mode B hub Story → hub `docs/retros/` EPIC-RESULTS): `[EPIC-RESULTS-<EPIC_KEY>.md](../../docs/retros/EPIC-RESULTS-<EPIC_KEY>.md)` (relative, Amendment 1 — CFP-288)
- **Cross-repo / dogfood** (예: codeforge family internal-docs `<plugin>/retros/`): 절대 GitHub URL `[EPIC-RESULTS-<EPIC_KEY>.md](https://github.com/mclayer/codeforge-internal-docs/blob/main/<plugin-folder>/retros/EPIC-RESULTS-<EPIC_KEY>.md)`

— 14 섹션 close summary

### 회고 (Epic close 후 PMOAgent fill)
<one paragraph>
```

### Implementation enforcement (CFP-84 Phase 2 follow-up)

본 CFP-84 Phase 1 = doc only. Phase 2 (별도 follow-up CFP) lint script `scripts/check-story-section-schema.sh` 강화:
- `type: epic` frontmatter detect → condensed mode allowed
- `type: story` strict mode (§1-§13 모두 의무, N/A 도 명시)
- 결합 허용 / N/A 형식 검증

---

## 단계별 갱신 책임

| 단계 | 갱신 섹션 | Owner agent |
|------|----------|-------------|
| 요구사항 접수 (story-init.yml Action 자동) | §1 verbatim 삽입, §2-11 placeholder | story-init.yml Action |
| 요구사항 병렬 에이전트 완료 | Domain→§2 / Analyst→§5 / Researcher→§6 (각 에이전트 직접 Edit) | RequirementsPLAgent / DomainAgent (codeforge-requirements) |
| 요구사항 확정 (RequirementsPLAgent) | §3·§4.0 | RequirementsPLAgent (codeforge-requirements) |
| 요구사항 병렬 에이전트 완료 (코드 컨텍스트) | §4.1·§4.2·§4.3 | ChangeImpactAgent·FeasibilityAgent·ContinuityAgent (write queue drain, codeforge-requirements) |
| 설계 확정 (ArchitectAgent → ArchitectPLAgent 검수) | §3/§7/§11 + `docs/change-plans/<slug>.md` + `docs/adr/ADR-NNN-<slug>.md` | ArchitectAgent (codeforge-design direct Edit) |
| 설계 리뷰 iteration (DesignReviewPL packet return) | (no write — pl_recommendation 반환만) | DesignReviewPL (codeforge-review review-verdict-v4) |
| 설계 리뷰 PASS/FIX verdict final write | §9.1 append + GitHub comment [설계-리뷰] + gate:design-review-pass 라벨 + phase transition + §14 Lane Evidence row update | **Orchestrator 단독** (CFP-137 / ADR-044 review-verdict-v4 §결정 4) |
| 구현 완료 (DeveloperPL) | §8.1-8.4 + §8.5 매핑표 commit + Phase 2 PR creation | DeveloperPL (codeforge-develop direct Edit) |
| 구현 리뷰 iteration (CodeReviewPL packet return) | (no write — pl_recommendation 반환만) | CodeReviewPL (codeforge-review review-verdict-v4) |
| 구현 리뷰 PASS/FIX verdict final write | §9.2 append + GitHub comment [구현-리뷰] + phase transition + §14 Lane Evidence row update (ADR-031 §결정 1) | **Orchestrator 단독** (CFP-137 / ADR-044 review-verdict-v4 §결정 4) |
| 구현 테스트 (CI gate — Orchestrator inline) | §9.3 | Orchestrator `gh pr checks` polling (CFP-317 / ADR-048) |
| 보안 테스트 iteration (SecurityTestPL packet return) | (no write — pl_recommendation 반환만) | SecurityTestPL (codeforge-review review-verdict-v4) |
| 보안 테스트 PASS/FIX verdict final write | §9.4 append + GitHub comment [보안-테스트] + gate:security-test-pass 라벨 + phase transition + §14 Lane Evidence row update (ADR-031 §결정 1) | **Orchestrator 단독** (CFP-137 / ADR-044 review-verdict-v4 §결정 4) |
| Clarification 재스폰 (RequirementsPL · ArchitectPLAgent) | §9.0 append | RequirementsPL / ArchitectPL (FIX 라벨 미추가 — fix-ledger-sync.yml은 §10만 trigger) |
| FIX 루프 | §10 append | **Orchestrator 단독** (CFP-32 fix-event-v1 monopoly, fix-ledger-sync.yml Action이 자동 mirror+label) |
| Git ops event 발생 시 (worktree create/prune, branch merge, tree decompose, stale GC) | §10.5 append | **GitOpsAgent 단독** (CFP-139 / git-ops-event-v1 contract, codeforge-pmo plugin) |
| Story 완료 회고 (PMOAgent) — **Phase 2 PR merge 후 5분 grace 자동 trigger (CFP-138 / ADR-045 mandate)**, 또는 Phase 1 PR merge 후 (doc-only Story, ADR-045 D-3) | §11 회고 블록 (4 field schema: retro_file / retro_summary / learnings_count / feedback_back_to_codeforge) | PMOAgent (codeforge-pmo direct Edit) — `gate:retro-complete` label add 의무 (forcing function) |
| Sonnet decision 발생 시 (사용자 ad-hoc 요청 시에만 — ADR-022 Deprecated, CFP-134 / ADR-035) | §12 append + `<internal-docs>/<plugin-folder>/decisions/<packet_id>.yaml` 생성 | Orchestrator (CFP-59 / CFP-61, decision-packet-v2.1) |
| Live touching Story 의 §13 (CONDITIONAL) | §13 11 필드 (vault / injection / permission / allowlist / withdrawal-off / first-trade cap / kill switch / operator approval / reconciliation / runbook / rollback) | ArchitectAgent (chief author, §7 / §11 / §8.5 와 동시 작성) |
| Phase 2 PR merged (최종) | Issue auto-close (PR body의 `Closes #N`) | (자동) |

---

## 섹션 읽기 규약

- **필요한 섹션만 읽기**: 프롬프트에 `§X, §Y 참조` 명시 → 에이전트가 `Read(docs/stories/<KEY>.md)` 후 해당 섹션만 참조
- 전체 file 읽기는 ArchitectAgent (chief author) 설계 진입 1회만 허용 (§1-6 전체 필요)
- **파일 변경은 lane plugin owner direct edit + Orchestrator 단독 (§10 FIX Ledger)** — codeforge-* CLAUDE.md self-write 표 + CFP-32 fix-event-v1 contract
