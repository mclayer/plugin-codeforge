## 12. Orchestrator 컨텍스트 패킷 (Story file 섹션 캐시)

에이전트 스폰마다 `Read(docs/stories/<KEY>.md)` 반복 호출은 토큰 낭비. Orchestrator가 세션 메모리에 섹션 캐시를 유지해 **context packet** 형태로 에이전트 프롬프트에 주입.

### 12.1 캐시 구조 (Orchestrator 세션 메모리)

```
story_cache[<story-key>] = {
  "file_path": "docs/stories/<KEY>.md",
  "mtime": <unix timestamp>,
  "fetched_at": <ISO 8601>,             # KST `+09:00` zoned (display layer — ADR-079 §결정 2)
  "sections": {
    "§1": {body, updated_at},
    "§2": {body, updated_at},
    ...
  }
}
```

### 12.2 캐시 갱신 규칙

- **무효화 트리거**: lane plugin 이 Story file update 완료를 보고하면 해당 섹션 캐시 invalidate (또는 file mtime 변경 감지 시 자동 invalidate)
- **fetch 규칙**: 에이전트 스폰 직전 Orchestrator가 필요 섹션이 캐시에 없거나 invalidated 상태면 fetch
- **섹션 단위 fetch**: `Read(docs/stories/<KEY>.md)` 결과에서 필요 섹션만 파싱 저장 — 전체 file body 메모리에 유지하지 않음

### 12.3 Context Packet 주입 형식

에이전트 프롬프트 `[컨텍스트]` 블록에 아래 packet 삽입:

```
[Story Context Packet — <KEY> (mtime: {ISO}, fetched {ISO})]
## §1 사용자 원문
{body}

## §3 관련 ADR
{body}

## §7 설계 서사
{body}

[End Packet]
```

에이전트는 prompt 내 packet을 SSOT로 사용 — 추가 `Read` 호출 생략 (packet 외 섹션 필요 시 명시 요청).

> **Worktree-membership directive (ADR-040 Amendment 6 / CFP-843)**: Context Packet 주입 시 packet 외 1줄 추가 — "All file operations MUST target `<worktree_abs_path>` (git = `git -C <abs>`, Write/Edit = absolute path, forward-slash 정규형)". harness cwd reset gap 차단 — §3.5 sub-agent spawn 표준 SSOT 정합.

### 12.4 Packet vs path-only 선택

- **Packet 주입**: 설계/구현/리뷰 레인처럼 여러 섹션 깊이 참조 필요할 때 (§1-8 범위)
- **Path만 전달**: 단발성 조회, 섹션 캐시 미정의 부분
- **설계 lane packet recipient**: ArchitectPLAgent (Phase 2에서 ArchitectAgent (chief author) + 7 permanent SubAgent (SecurityArch / InfraOperationalArch / TestContractArch / DataArch / ModuleArch / AggregateArch / APIContractArch) + 3 sub-tuple (Mapper / Refactor / ArchitectAnalyst) 에 forward — PL이 packet 분배 책임. CFP-1086 / ADR-042 Amd 8 정합.)

### 12.5 Project Config Packet (project.yaml 슬라이스)

Story file Context Packet과 병행해 **`.claude/_overlay/project.yaml`의 objective SSOT 상수**도 sub-agent 프롬프트에 주입. GitHub 호출하는 에이전트가 매번 `Read` 호출 없이 곧바로 활용.

#### 캐시 구조

```
project_config_cache = {
  "loaded_at": <ISO 8601>,                   # 세션 시작 시 1회 로드 — KST `+09:00` zoned (display layer — ADR-079 §결정 2)
  "raw": {
    "project": {name},
    "github": {org, repo, default_branch, pr_title_prefix_template, story_key_prefix, codeowners, discussions, milestone},
    "labels": {components},
  },
}
```

#### 로드·무효화

- **로드**: 세션 개시 시 1회 `Read(.claude/_overlay/project.yaml)` + yaml.safe_load
- **검증**: validate_config.py 통과 (SessionStart hook에서 이미 검증됨 — Orchestrator는 신뢰하고 read만)
- **무효화**: consumer가 세션 중 project.yaml 편집하면 next agent spawn 직전 재로드 (파일 mtime 비교)
- **Missing file 처리**: validator가 WARN만 했으므로 Orchestrator는 packet 주입 생략 + 에이전트에 "project.yaml 없음 — GitHub 호출 전 사용자 확인" 지시

#### Packet 주입 형식

GitHub 상수가 필요한 에이전트 프롬프트에 삽입:

```
[Project Config Packet — loaded at {ISO}]
project.name: <name>
github.org: <org>
github.repo: <repo>
github.default_branch: <main>
github.pr_title_prefix_template: <template>
github.story_key_prefix: <prefix>
github.codeowners.architect_team: <@org/team>
github.codeowners.domain_expert_team: <@org/team>
github.discussions.domain_kb_category: <category>
github.milestone.epic_naming_pattern: <pattern>
labels.components: [...]
[End Project Config Packet]
```

에이전트는 위 값을 그대로 GitHub 호출 인자에 사용. project.yaml `Read` 생략 가능 (packet SSOT).

#### Packet 주입 대상 에이전트

| 에이전트 | 사용하는 slice |
|----------|----------------|
| **RequirementsPLAgent** | `github.story_key_prefix` (Story KEY 결정), `github.org`, `github.repo` (search·list_issues 호출) |
| **각 lane plugin** | 자기 phase prefix GitHub 호출에 필요한 org/repo/story_key_prefix slice |
| **DomainAgent** | `github.discussions.domain_kb_category` (Discussions Q&A) + `Glob(docs/domain-knowledge/**)` |
| **PMOAgent** | `github` 전체 (회고·패턴 search 호출) |
| **ArchitectPLAgent** | `github.codeowners.architect_team` (Phase 1 PR architect review 매핑 확인), `github.org`, `github.repo` (Issue/PR cross-reference). 설계 lane 전체에 packet forward 책임 |

기타 에이전트 (설계·구현·리뷰·테스트 레인 대부분)는 GitHub 호출 없음 → packet 주입 불필요.

#### Fallback: Read로 직접 접근

Packet 주입은 Orchestrator의 토큰 최적화 수단이지 필수 규약 아님. Packet 누락 또는 일부 필드만 필요할 때 에이전트는 여전히 `Read(.claude/_overlay/project.yaml)`로 직접 접근 가능 (agent md `Read` 권한 보장).

### 12.6 Warm cache (R6, [CFP-19 spec](https://github.com/mclayer/codeforge-internal-docs/blob/main/wrapper/specs/2026-04-27-cfp-19-orchestration-parallelization.md))

매 spawn마다 `Read(docs/stories/<KEY>.md)` → 섹션 추출 → packet 재구성 비용을 cache로 amortize.

**Cache 위치**: `.claude-work/cache/<KEY>-sections.json` (Story 1건당 1 파일)

**Cache 스키마**:

```json
{
  "story_key": "<KEY>",
  "story_file_commit": "<git rev-parse HEAD on docs/stories/<KEY>.md>",
  "cached_at": "<ISO 8601>",
  "sections": {
    "1": "<§1 본문 hash>",
    "3": "<§3 본문 hash>",
    "7": "<§7 본문 hash>",
    "...": "..."
  },
  "section_bodies": {
    "1": "<§1 verbatim>",
    "3": "<§3 verbatim>",
    "...": "..."
  }
}
```

**Cache 사용 절차**:
1. Orchestrator가 spawn 직전 packet 조립
2. cache 파일 존재 + `story_file_commit` 일치 확인:
   - **hit**: `section_bodies`에서 필요 섹션 reuse → 재 Read 없음
   - **miss (commit drift)**: `Read(docs/stories/<KEY>.md)` → 새 cache write
3. 1 Story 평균 6 lane × 4 spawn = 24회 spawn 중 **14-18회 cache hit 기대** (lane 경계마다 1회만 commit drift)

**Invalidation**:
- lane plugin 이 Story file edit 후 `git rev-parse HEAD:docs/stories/<KEY>.md` 변경 → 자동 cache miss
- Story 완료 시 cache 파일 cleanup (선택)

**보안**: cache 파일에 §1 사용자 원문 포함 → `.gitignore`에 `.claude-work/cache/` 추가 의무 (Group F).

---

### 12.7 Orchestrator 통신 표준 (normative — wrapper + all consumers)

**매 메시지 첫 줄 = 단계 메타 라벨 의무**:

| 상황 | 첫 줄 형식 |
|---|---|
| 레인 진행 중 | `현재 단계: <레인명> — <에이전트명> <동작>` |
| Skill 절차 진행 중 | `<Skill명> Step N/<전체> — <현재 동작>` |
| ADR / spec / 코드 블록 제시 | `다음은 [무엇] — 사용자가 [무엇] 검토` |
| 결정 선택지 제시 | `결정 대상: <무엇> — 아래 N개 선택지` |
| 약어 첫 등장 | 첫 등장 시 풀어쓰기 (예: `CFP-274 (TodoWrite 진행 시각화 Story)`) |

**Cold-start readability 의무**: 각 메시지가 대화 누적 컨텍스트 없이도 이해 가능해야 한다. 약어·코드 블록·ADR ref 가 맥락 설명 없이 갑자기 등장하는 것은 `communication_violation`.

**적용 범위**: wrapper + 모든 consumer project Orchestrator 세션.

### 12.8 Deputy 영역별 specialized flat spawn Context Packet 4종 spec (CFP-681 / W1 S2 — CFP-1026 design lane 재편)

설계 lane 에서 Orchestrator 가 4-tuple sub-tuple (CodebaseMapper / RefactorAgent / ArchitectAnalyst + ArchitectAgent chief author) 및 deputy 를 spawn 할 때 주입하는 영역별 specialized Context Packet spec. deputy mandate 매트릭스 SSOT = `skills/deputy-mandate/SKILL.md` (5 permanent + 3 CONDITIONAL — ADR-042 Amendment 7 / ADR-014 Amendment 4). 본 §12.8 은 그 매트릭스의 spawn-time 주입 mechanism.

#### (a) Orchestrator flat spawn (재귀 spawn 금지 / nested team 금지 / sub-lead 격상 0건)

- spawn 주체 = **Orchestrator** (top-level Claude 세션). 4 component (chief author + Mapper + Refactor + ArchitectAnalyst) 모두 Orchestrator 가 직접 flat spawn. ArchitectPLAgent 는 PL synthesizer 역할 (산출물 통합 검수) — sub-agent 를 재귀 spawn 하지 않는다.
- **재귀 spawn 금지** = platform inherent (Lead 와 teammate 모두 Agent tool 추가 spawn 불가, env=0 default subagent context). **nested team 금지** = team-of-teams 불가. **sub-lead 격상 0건** = 4-tuple 안 어느 component 도 다른 component 의 spawn 주체가 되지 않음.
- 근거 SSOT: 본 nested team 금지 / flat spawn 원칙은 ADR-044 (phase-scoped sequential team — 대안검토표 + 결론 단락의 nested team 금지 SSOT) + ADR-009 §결정 1 (wrapper-only decomposition) + ADR-039 (Orchestrator subagent default) 정합. CFP-676 CX-676-TP4-3 reaffirm 정합 (S1 ADR-044 reaffirm 단락 cross-ref).

#### (b) "4-tuple = 논리적 그룹핑" — 물리적 spawn 계층 아님

4-tuple 은 **어느 sub-agent 가 어느 deputy 영역 Context Packet 으로 spawn 됐는지를 표기하는 논리적 그룹핑**이다. 물리적 spawn 계층 (4-level nested) 이 아니다. 모든 component 는 동일 평면(flat)에서 Orchestrator 로부터 spawn 되며 서로의 상위/하위가 아니다. "4-tuple" 의 "4" 가 4단계 nested spawn 으로 오해되는 것을 명시적으로 차단 (CFP-681 EC-6 — Story §1 deliverable 3 verbatim).

| 4-tuple component | spawn 주체 | deputy 영역 packet | model tier |
|---|---|---|---|
| ArchitectAgent (chief author) | Orchestrator (flat) | 전 deputy + 3 sub-tuple 산출물 multi-source synthesis | Opus |
| CodebaseMapper | Orchestrator (flat) | existing codebase fact (as-is) | Sonnet |
| RefactorAgent | Orchestrator (flat) | decoupling / pattern advocacy (to-be) | Sonnet |
| ArchitectAnalyst (PriorArtAgent rename) | Orchestrator (flat) | 변경 전 기존 설계 (ADR / Change Plan / Story) 분석 단일 축 | Sonnet |

#### (c) 정적 overlay 메커니즘 vs 동적 spawn-time Context Packet — 명시적 대비

| 축 | 정적 overlay 메커니즘 | 동적 spawn-time Context Packet |
|---|---|---|
| 주입 시점 | consumer SessionStart merge hook (세션 개시 1회) | **매 spawn** (Orchestrator 가 sub-agent 프롬프트에 주입) |
| 내용 | `.claude/_overlay/project.yaml` objective SSOT 상수 + `.claude/_overlay/CLAUDE.md` narrative (도메인 해설) | Story file 섹션 캐시 (§12.1-§12.3) + deputy 영역별 specialized slice (본 §12.8) |
| 성격 | desired state (Helm-style 정적 — 프로젝트 불변 상수) | 동적 (Story·spawn 마다 달라지는 컨텍스트) |
| SSOT | §12.5 Project Config Packet (project.yaml 슬라이스) | §12.3 Context Packet 주입 형식 + 본 §12.8 deputy 영역별 specialization |

> **혼동 차단 (CFP-681 §2.5 / Researcher disambiguation)**: 정적 overlay (consumer SessionStart merge — Helm-style desired state) 와 동적 spawn-time Context Packet (매 spawn 주입) 은 별개 메커니즘이다. deputy 영역별 specialized packet 은 후자 — Story·spawn 마다 어느 deputy 영역 slice 를 주입할지 동적으로 결정. overlay 의 정적 상수 (project.yaml) 와 cross-pollinate 금지.

#### (d) ADR-039 §결정 1 cross-ref

본 §12.8 의 모든 spawn 은 [ADR-039](adr/ADR-039-orchestrator-subagent-default-for-codeforge-modification-work.md) §결정 1 (codeforge 수정 작업 = Orchestrator default subagent spawn) 정합. inline 수행은 §결정 2 의 4-entry whitelist (사용자 dialog / TodoWrite scratchpad / Read-only Q&A / Status report) 외 영역 금지. 4-tuple flat spawn = ADR-039 default subagent context 의 design lane instantiation (env=0 = one-shot Agent tool spawn, env=1 = phase-scoped sequential team — ADR-044, 단 nested team 금지 동일).

---

