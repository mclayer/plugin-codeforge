# Changelog

## 1.29.0 — 2026-07-24

### Added (CFP-2813 — ADR-166 / ADR-078 Amd3 / ADR-112 Amd1: 리뷰 PL mandatory read + Living Architecture 갱신 substance 소비 배선, MINOR)

[CFP-2813] 리뷰 lane PL 이 산출 전 설계정보를 mandatory read 하고, 설계리뷰가 Living Architecture 갱신 여부를 substance 로 소비하도록 배선:

- `templates/review-pl-base.md`: 리뷰 PL 4 전원(RequirementsReviewPL · DesignReviewPL · CodeReviewPL · SecurityTestPL) design-info-read-protocol-v1 mandatory read 주입 — verdict 종합 전 Living Architecture(`docs/architecture/<plugin>.md`) / 설계정보 선행 read 강제 (ADR-078 Amendment 3 git-source + ADR-112 Amendment 1 dual-read 정합).
- `agents/DesignReviewPLAgent.md`: L3 substance 소비 배선 — Living Architecture 갱신 marker(`living_architecture_updated_self_check_passed` / `living-architecture-not-updated`)를 설계리뷰 verdict 근거로 소비(갱신 누락 = blocking-on-pr surfacing).
- `.claude-plugin/plugin.json`: description CFP-2813 entry prepend + version 1.28.2 → 1.29.0.

#### Why

리뷰 PL 이 최신 설계정보를 읽지 않은 채 verdict 를 내는 갭 + Living Architecture 갱신 누락이 리뷰에서 잡히지 않는 갭을 차단. review-pl-base 템플릿 mandatory read 주입(additive) + DesignReviewPLAgent substance 소비 표면(additive) → MINOR (ADR-037 (d) Template additive / (a) Agent file 추가 / ADR-008). marketplace version·description sync(ADR-063, sync PR 선행 merge).

## 1.28.2 — 2026-07-23

### Changed (CFP-2804 — ADR-064 §결정7 L406 이연 cascade, PATCH)

[CFP-2804] `docs/architecture/codeforge-review.md` descriptor `ADR = 단일 결정 단위, 불변`(:73) → `(결정 시점 고정 — 개정=supersede / 의미보존 위생편집 채널; ADR-058 §결정10)` qualify — byte-immutable 오독 봉쇄 + genre 대조 보존. 효력-변화-0 위생.

#### Why

ADR-058 §결정10 + supersede 1급화 정합. marketplace version·description sync(ADR-063).

## 1.28.0 — 2026-07-18

### Added (CFP-2735 — ADR-141 Amendment 1: CodexReviewAgent opus→haiku carve-out + self-refusal guard, MINOR)

[CFP-2735] ADR-141 Amendment 1 — 외부위임·기계 워커 7종 opus→haiku carve-out. 본 plugin 의 **CodexReviewAgent** frontmatter `model: opus`→`model: haiku` + subagent self-refusal guard(#846) 1줄 배치(A1-3 canonical subagent-facing). agent tier 변경 = additive behavior (ADR-037/ADR-008 MINOR). marketplace version sync(ADR-063, sync PR 선행 merge).

## 1.22.0 — 2026-07-10

### Added (CFP-2597 — peer-completion falsifiability (verification-floor 축③) + review-verdict-v4 v4.16, MINOR)

[CFP-2597] codeforge review-PL delivery-gap 기계화 Phase 2 — PASS verdict 이 peer 완료 증거를 동반하도록 강제하는 peer-completion falsifiability (ADR-044 Amendment 6 §결정 12 / ADR-060 Amendment 21).

- `docs/inter-plugin-contracts/review-verdict-v4.md` v4.15 → v4.16 MINOR (canonical sibling sync): `peer_verdicts[]` verdict-level optional array 신설 — `peer_degrade.peer_count` (int 자기단언) 보강(대체 아님). 각 entry 5-key = ADR-068 I-6 existence-verify-annotation 3-key (`form: file-path-reference` / `target`: peer transcript·verdict artifact 상대경로(verdict file dir 기준) / `verify_status`) + `worker` (claude|codex) + `worker_recommendation` (그 peer 의 verdict token — content-binding). §19 신설 + amendment_log/authors + MANIFEST review_verdict row mirror. additive only backward-compat (기존 v4.15 consumer 가 array 부재 = augmentation 없음으로 해석, ADR-008 §결정 2 MINOR).
- `templates/review-pl-base.md` §3 "종합 발화 precondition" 신설 — PL verdict 종합 발화 = **양 worker_outcomes 도달(or honest INCONCLUSIVE/degrade)** 후. spawn-then-blind-wait 금지, collect = LEAD 소유 (C1 / ADR-139 INV-L4). §10 collect=LEAD·env=1 auto-wake dispatcher 재제안 금지 (ADR-139 §결정 7(ii) substrate DEFER) + blocking 요구 = ADR-115 C2 위반 → record-only(stop-event.jsonl) 문단 추가. 신규 mechanism 0 — ADR-139 §결정 7 / INV-L2·L4 명문화만.

#### Why

review-PL 이 peer worker 를 spawn 후 blind-wait 로 결과 미도달 상태에서 self-audit PASS 를 내는 delivery-gap 을 게이트가 stat 로 반증 가능하게 한다. 축③ = check-verification-floor.sh 의 peer-completion falsifiability — **check-lane-evidence.sh 축③(deputy/role:dev fan-out, ADR-044 §결정 10 (d)) 와 별개**(이름만 동일, script·axis disjoint). pl_recommendation:PASS ∧ NOT honest-single-peer-degrade 시 peer_verdicts[] ≥1 entry ∧ target FS 실재+non-empty 독립 stat(자기단언 verify_status 불신). peer_count:0+PASS=축① 선차단 / honest-degrade=축② 위임(축③ stand-down, AC-A3 무회귀). warning-tier(advisory exit0 / --strict exit1), non-version-gated(anti-evasion). 정직한 한계: 축③=위조비용 상향+audit trail 이지 위조방지 게이트 아님(PL claim+proof 동시저작 → full falsifiability 불가), warning-tier=정직 상한, blocking 승격=false assurance. 실 script(scripts/check-verification-floor.sh 축③)+workflow+test = sibling worker Phase 2 deliverable. schema sibling sync + review-pl-base codify additive → MINOR (ADR-037 / ADR-008). marketplace version·description sync(ADR-063, sync PR 선행 merge).

## 1.21.0 — 2026-07-10

### Added (CFP-2586 — 엣지 케이스 도출 기법 리뷰 anchor, MINOR)

[CFP-2586] 엣지 케이스 체계적 도출 기법 forcing function 의 리뷰 anchor 배선 (ADR-006 Amendment 2).

- `templates/review-checklists/design.md` §5 Test Contract 타당성: anchor-presence 1행 추가 — 실행 가능 코드 있는 Story §8 에 엣지 도출 기법 walk 선언(tier A 기법별 대표 케이스 실값 + tier B 트리거 시 적용/부재 structural trigger 명시 N/A) 또는 §8.4 N/A 부재 시 지적·차단 근거. category `test-contract` 재사용(신규 literal 0). presence-only — 완결성 격상 아님(ADR-119 검사연극 금지, 완결성 실판정은 review correctness + mutation gate OOS).
- `templates/review-checklists/code.md` §5 테스트 코드 품질: loop closure 1행 추가 — §8 선언 기법 ↔ 실제 엣지 테스트(선언된 기법별 대표 케이스 1+)가 `tests/**` 에 실존하는가 교차검증. category `test-quality` 재사용.

#### Why

설계리뷰 anchor-presence(선언 강제) + 구현리뷰 loop closure(실물 교차검증) 분업으로 §8 엣지 도출 forcing function 의 3-anchor 를 완성. §8.7 venue-shape(Amendment 1) anchor 와 mechanism 동형·disjoint(완결성 축 vs 형상 정확성 축). checklist additive(신규 category literal 0) → MINOR (ADR-037 / ADR-008). marketplace version·description sync(ADR-063, sync PR 선행 merge).

## 1.20.0 — 2026-07-03

### Changed (CFP-2560 — 전 에이전트 opus 단일 tier, MINOR)

[CFP-2560] 전 에이전트 opus 단일 tier (ADR-141) — model frontmatter opus 통일 + Sonnet tier 표/ADR-057 fallback 청산.

- review lane 에이전트 frontmatter `model: opus` 통일 (ADR-141 — fallback 대상 없음).

## 1.19.0 — 2026-07-02

### Changed (CFP-2554 — fable surgical tier 원복, MINOR)

미 정부 제약 해제로 ADR-117 Amendment 1 임시 opus override 를 해제하고 surgical 에이전트를 `model: fable` 로 원복(ADR-117 Amendment 2).

- review lane surgical 5 에이전트 frontmatter `model: opus`(임시 CFP-2241) → `model: fable` 환원 + 임시 표식 코멘트 제거: `ClaudeReviewAgent` · `CodeReviewPLAgent` · `DesignReviewPLAgent` · `SecurityTestPLAgent` · `RequirementsReviewPLAgent`(surgical set 10→11 정식 편입 — 적대적 심판 category).

#### Why

미 정부 제약 해제(사용자 통지 = ADR-117 Amd1 "제약 해제 통지" 트리거). 능력 손실 0(fable/opus thinking 프로파일 동형), 비용 축만 2배 재부담 — ADR-117 결정 1 이 이미 정당화한 surgical 역할 한정. 모델-tier 행동 변경(다음 세션부터 fable) = consumer 영향 → MINOR.

## 1.18.0 — 2026-07-02

### Changed (CFP-2549 — background-wait liveness gate cross-ref, MINOR)

ADR-139 (background-wait liveness gate — 모든 codeforge-owned background subagent 대기의 유한성 1급 원리) 의 lane 반영.

- `templates/review-pl-base.md` — general background-wait liveness gate cross-ref 1줄 추가 (SSOT = ADR-139 / orchestrator-playbook.md "background-wait liveness gate" 공통 단락). codeforge 소유 background subagent 대기는 wall-clock 상한 + liveness 관측(3-state) + fail-open 금지(inconclusive) 규약을 상속.

#### Why

CFP-2545 companion wall-clock ceiling 이 codex-특정 first instance 였고, ADR-139 가 이를 모든 background subagent 대기로 일반화. review lane PL 도 이 공통 규약을 상속하므로 review-pl-base 에 1줄 cross-ref. capability 추가(liveness 규약 상속 명시) — MINOR.

## 1.17.0 — 2026-07-02

### Changed (CFP-2545 — Codex companion 브로커 경로 wall-clock 가드, MINOR)

ADR-081 Amendment 12 §결정 D14 (Codex companion 브로커 경로 wall-clock ceiling mandate) 의 lane 반영. 실 리뷰 worker 호출부가 companion `request()` deadline 부재로 stall 시 무한 대기하던 것을 wall-clock 상한으로 근절 (dogfood wrapper-self Phase 2).

- `agents/CodexReviewAgent.md` — 실행 패턴 §의 companion dispatch 발화(`adversarial-review --wait` / `task --write`)에 **option-first** `timeout --kill-after=${CODEX_REVIEW_KILL_AFTER_SEC:-30} ${CODEX_REVIEW_TIMEOUT_SEC:-300}` wall-clock 가드 prefix (GNU coreutils runnable 형태 — duration-first 는 `--kill-after` 를 명령으로 오인해 exit 127 가드 무효) + exit code 판정 블록(exit 124 → marker `[codex-sandbox-fallback: dispatch_stall_or_stream_timeout]` + verdict=inconclusive, fail-open 금지 PASS-only-if-explicit) + POSIX timeout preflight. N=추정값 empirical 미실증 (env-override, lock-in 금지).
- `templates/review-pl-base.md` — companion dispatch wall-clock 상한 cross-ref 1줄 (SSOT = ADR-081 §결정 D14 / CodexReviewAgent.md).

#### Why

companion 브로커(`node codex-companion.mjs adversarial-review --wait`, 4 리뷰 lane 공유 워커)는 §D8 file-redirect(0-byte TTY stall 방어)가 미포함하는 wall-clock process-level hang 위험 보유. wrapper presence-grep lint(`check-codex-companion-timeout-presence`)가 AC-1 mechanical 강제. capability 추가 = companion wall-clock ceiling — MINOR.

## 1.12.3 — 2026-06-15

### Changed (CFP-2249 — superpowers 의존 완전 제거, PATCH)

Epic CFP-2249 (superpowers 의존 완전 제거, ADR-122 — supersede ADR-028) 의 lane 반영. 리뷰 lane 의 `superpowers:*` skill 호출 / `docs/superpowers-integration.md` 참조를 codeforge native discipline 으로 교체. 필수 plugin 4→3 의 wrapper 정책 변경 동반 lane catch-up. capability 추가/제거 0 — PATCH.

- `agents/ClaudeReviewAgent.md` · `templates/review-pl-base.md` — `superpowers:*` 호출 / `superpowers-integration.md` 참조 제거 → codeforge native (ADR-122) 흡수. discipline = research-before-claims (ADR-119) + codeforge native skill.

#### Why

ADR-122 — superpowers 외부 plugin 의존을 codeforge native 로 내재화. consumer breaking 0.

## 1.12.1 — 2026-06-12

### Changed (CFP-2178 — S6 lane repo archive 참조 sweep, PATCH)

- `overlay/hooks/session-start-deps-check.sh` 안내 URL — 구 lane repo (`mclayer/plugin-codeforge-review`) → wrapper 모노레포 앵커 (`mclayer/plugin-codeforge/tree/main/plugins/codeforge-review#dependencies`). 구 lane repo 8개 = 2026-06-12 GitHub archive (ADR-118 D1) — read-only repo 안내 차단.
- `CLAUDE.md` `story_issues` repo 좌표 — `mclayer/plugin-codeforge-review` → `mclayer/plugin-codeforge` (archive 후 read-only repo 에 issue 생성 지시 = 기능 파손 해소).

## 1.10.1 — 2026-05-30

### Changed

- **[CFP-1845 follow-up] agent model 핀 → 별칭 전환 (opus/sonnet/haiku 항상 최신 지칭). frontmatter model field 5건. tier 분류 변경 0건. wrapper #1846 / #1847 연계. marketplace sibling sync 동반.**
  - `agents/ClaudeReviewAgent.md` · `agents/CodeReviewPLAgent.md` · `agents/DesignReviewPLAgent.md` · `agents/SecurityTestPLAgent.md` — `model: claude-opus-4-7` → `model: opus`
  - `agents/CodexReviewAgent.md` — `model: claude-haiku-4-5-20251001` → `model: haiku`
  - 본문/description 의 과거 버전 서술(frozen audit trail)은 무변경.

## 1.10.0 — 2026-05-23

### Changed

- **review-verdict-v4 v4.8 → v4.9 MINOR (canonical)** — CFP-604 retro F7 Wave 2 carrier ([CFP-1303](https://github.com/mclayer/plugin-codeforge/issues/1303)). Wave 1 [CFP-1291](https://github.com/mclayer/plugin-codeforge/issues/1291) (codeforge-review #42, MERGED 2026-05-23 09:23 KST) prose-only anchor 위 schema layer codify.
  - `findings[].parallel_anchors_checked` optional array field 신설 (additive backward-compat — `findings[].anchor_id` v4.1 pattern 답습)
  - 각 entry = `{file_line: string, pattern_type: enum 5종 closed-set, matched: bool}`
  - `pattern_type` 5종 enum closed-set: `local_remote` / `client_server` / `read_write` / `forward_reverse` / `enum_closure`
  - `matched: bool` 의미: true = parallel anchor 발견 + 동일 root cause class 확인 / false = 검색 evidence clean enumeration / field absent = 검색 미수행 (Wave 3 lint heuristic 영역)
  - **ADR-068 I-2 cross-module propagation completeness 의 review-verdict layer realization** (micro-scale parallel form — propagation matrix module-level vs `parallel_anchors_checked` finding-level disjoint axis)
  - `templates/review-pl-base.md` 영향 0 (이번 Wave 는 CodeReviewPLAgent.md 만 갱신)
  - **Wave 1 → Wave 2 → Wave 3 layered architecture**: Wave 1 prose anchor (CFP-1291) / Wave 2 schema codify (본 CFP-1303) / Wave 3 mechanical lint presence-grep heuristic (deferred-followup)
  - ADR-008 §결정 2 "새 선택 필드 추가" MINOR bump 정합. Runtime impact 없음 (기존 v4.8 consumer 가 본 신규 field 무시 가능)
  - 적용 lane: CodeReviewPL (primary) — Wave 1 CFP-1291 본문 정합 / DesignReviewPL + SecurityTestPL (optional)

### Updated

- **`agents/CodeReviewPLAgent.md`** — Wave 1 prose ("parallel anchors checked: [...]" inline marker) → Wave 2 schema YAML block format 갱신.
  - 5 pattern_type enum closed-set 표 (canonical schema 정합 — local_remote / client_server / read_write / forward_reverse / enum_closure)
  - finding output schema example v4.9 (anchor_id + parallel_anchors_checked array block)
  - field semantic 명시 (matched true/false/absent 3-state 구분)
  - Wave 1/2/3 layered architecture 표
  - ADR-068 I-2 cross-module propagation completeness 연결 단락
  - CFP-604 trigger evidence (LOCAL_AUTHOR ↔ REMOTE_AUTHOR pattern_count 2) 보존

### Out of scope (별 follow-up CFP)

- **Wave 3 mechanical lint** (`parallel_anchors_checked` field presence-grep heuristic on finding emit) — deferred-followup
- **5 other lane plugin sibling sweep** (requirements / design / develop / test / pmo v4.8 → v4.9 mirror) — CFP-1167 precedent 답습

### Sibling sync (ADR-010)

- canonical: 본 PR (codeforge-review `docs/inter-plugin-contracts/review-verdict-v4.md`)
- wrapper sibling: plugin-codeforge PR (별 atomic — `docs/inter-plugin-contracts/review-verdict-v4.md` + `MANIFEST.yaml` row)
- 5 other lane plugin 5개 (requirements/design/develop/test/pmo): 본 scope 외, 별 follow-up CFP (CFP-1117-S4 precedent 답습)

### Marketplace atomic invariant (ADR-063)

- mirrored field 4종 (name / version / description / author) atomic sync 의무 — plugin.json 1.9.1 → 1.10.0 MINOR + marketplace.json 동반 PR
- `marketplace_sync_declared: true` (verdict packet 의 explicit marker)

## 1.9.1 — 2026-05-23

### Added

- [CFP-1291] **CodeReviewPLAgent.md cross-anchor parity check step 추가** (CFP-604 retro F7 follow-up realized, minimum-viable Wave 1 declarative). finding 작성 시 parallel anchor enumeration 의무 + 5 patterns priority enumeration (LOCAL↔REMOTE / client↔server / read↔write / forward↔reverse / enum closure check) + finding output 안 `parallel anchors checked: [...]` inline marker prose 명시.
  - **Evidence (CFP-604)**: Phase 2 CodeReview Iter 1 = LOCAL_AUTHOR `check-version-bump-atomic.sh:76` catch 후 REMOTE_AUTHOR `check-version-bump-atomic.sh:213` (동일 root cause class) 미catch → CI 재발견 + FIX iter 2 continuation commit `85b6042` 필요. Pattern 1 (LOCAL↔REMOTE) parallel-site grep 미적용 결함.
  - **Wave 1 scope**: agent body prose + inline marker. **Wave 2 (deferred)**: review-verdict-v4 schema field `parallel_anchors_checked[]` 신설 = 별 sub-Story carrier (ADR-076/082/086 precedent 답습 — declarative first, mechanical schema second).

## 1.9.0 — 2026-05-21

### Changed
- review-verdict-v4 v4.7 → v4.8 MINOR (ADR-091 §결정 6 enforcement layer 3-tier 의 3번째 tier — review-verdict-v4 enum S4 carrier, CFP-1117 Story-4)
  - `findings[].type` enum 에 3 DDD finding type literal 추가: `bc_violation` (Bounded Context 위반 — Change Plan §3.D bounded_context_boundary 연결) / `aggregate_violation` (Aggregate 위반 — Change Plan §3.A affected_aggregates + ADR-091 §결정 3 Layer B real Aggregate 연결, ModuleArchitectAgent boundary axis unified 영역) / `ubiquitous_language_drift` (Ubiquitous Language drift — check-ubiquitous-language lint 연결)
  - ADR-091 §결정 7 INV-5 vocabulary theater 차단 forcing function 의 review-verdict finding 연결 (evidence #4)
  - additive only backward-compat invariant (기존 v4.7 consumer 가 3 신규 enum literal 무시 가능). ADR-008 §결정 2 "enum literal 추가" MINOR bump 정합. CFP-528 Amendment 1 (enum literal + 의미 1줄) pattern verbatim 답습.
  - DesignReviewPL + CodeReviewPL 양 lane emit. verdict-level boolean field 신설 0건 (findings[].type literal 확장만 — semantic accountability mechanism, §결정 6 3번째 tier rationale 정합).
- `templates/review-pl-base.md` §3 — DDD finding type 3 literal 종합 check table 추가 (DesignReview / CodeReview cross-validate, boundary-completeness / dimensional-empirical-gap dual-binding 패턴 답습)

### Note
- 5 sibling contract (requirements/design/develop/test/pmo v4.3) pre-existing drift = 본 S4 scope 외 (별 sweep CFP carrier)

## 1.8.0 — 2026-05-20

### Changed
- review-verdict-v4 v4.5 → v4.6 MINOR (canonical SSOT sync, ADR-010 sibling sync mirror from wrapper CFP-1086-S1)
  - `deputy_axis_restructure_self_check_passed` optional bool field 신설 (ADR-042 Amendment 8 + ADR-086 P7 framework self-application 첫 사례 carrier)
  - `boundary_completeness_self_check_passed` scope expansion (ADR-068 Amendment 2 wording SSOT chief tie-break ladder cross-ref)

`codeforge-review` plugin 릴리스 이력.

버전 체계: [Semantic Versioning 2.0.0](https://semver.org/lang/ko/). v1.0 이전은 minor bump도 breaking 가능.

## [1.7.0] - 2026-05-20

### CFP-698 — ADR-014 Amendment 4 + ADR-042 Amendment 7 cross-repo sibling sync (MINOR)

Wrapper Phase 1 PR (mclayer/plugin-codeforge#1035 `abcd92bf` CFP-676 merged 2026-05-19) Epic CFP-1026 Wave 2 Story-4 carrier. ADR-014 Amendment 4 (OpRiskArch → InfraOperationalArch rename + §7.4 primary/cross-ref shell evidence-driven 3-axis split) + ADR-042 Amendment 7 (DataMigrationArch → DataArch rename, 5+3 deputy matrix) 의 codeforge-review repo cross-repo sibling 반영. ADR-054 Category 2 doc-only fast-path. ADR-010 §4 wrapper-first allowed pattern 정합.

#### Changed (mechanical rename, 7 occurrence)

- `templates/review-checklists/design.md` — `OperationalRiskArchitectAgent` → `InfraOperationalArchitectAgent` (L5 + L71 + L89 = 3 occurrence) + `DataMigrationArchitectAgent` → `DataArchitectAgent` (L141 + L172 = 2 occurrence) + `DataMigrationArch` → `DataArch` (L31 + L196 = 2 occurrence)
- `agents/DesignReviewPLAgent.md` — L105 `DataMigrationArch` → `DataArch` (1 occurrence)

#### Added

- `templates/review-pl-base.md` — §8.6 audit gate normative 1-line append (pointer-existence vs policy-effectiveness disjoint axis, ADR-014 Amd 4 §결정 2 cross-ref shell 분류 정합). DesignReviewPL Story §8.6 (IntegrationTest contract pointer) audit 시 pointer 존재 mechanical check only invariant. policy 값 공백 PASS / pointer 부재 P1 FIX. boundary-completeness flag (ADR-068 I-3 unconditional guard placement).
- `docs/architecture/codeforge-review.md` — Governance ADR anchor 영역 §8.6 audit gate 1-line cross-ref (ADR-078 living architecture doc SSOT 정합).

#### Why

S1 CFP-676 wrapper#1035 `abcd92bf` merged 시점에 wrapper SSOT 만 갱신되어 codeforge-review repo 의 cross-repo sibling 반영 미완 상태. RequirementsPL ground truth verify (`OperationalRiskArchitectAgent` 6 occurrence × 2 file = 7, `DataMigrationArchitectAgent` 5 occurrence × 2 file). design-time existence layer (DesignReviewPL §8.6) + runtime enforcement layer (IntegrationTest §7.4, codeforge-test sibling) 의 2-layer split 정착으로 "정책 효력 (effectiveness) vs 정책 존재 (existence)" disjoint axis 명문화. 이전 root-cause confusion (pointer 부재 P1 vs policy 공백 PASS 구분 불가) 차단.

#### Compatibility

- **Wire**: deputy 명칭 rename = mandate scope 보존 (ADR-033 4 sub-item Container Docker 0 변경 invariant). §8.6 audit gate 1-line = 신규 normative (pointer mandatory). ratchet 강화 방향 (ADR-058 §결정 5 정합).
- **Marketplace sync**: 본 MINOR bump 의 marketplace.json mirror = ADR-063 atomic invariant 발효 (별 sync PR carrier).
- **Carrier**: CFP-698 (Epic CFP-1026 Wave 2 Story-4, sibling Story = codeforge-test 1.2.0).

## [1.6.0] - 2026-05-13

### CFP-582 — ADR-059 Amendment 2 / debate-protocol-v1 v1.2 sibling sync — review-pl-base.md cross-ref + 3 marker pattern verification (MINOR)

Wrapper Phase 1 PR (mclayer/plugin-codeforge CFP-582 — Wave 4 ADR-059 Amendment 2) 의 canonical sibling sync (ADR-010 §4 wrapper-first allowed pattern). DesignReview lane 의 review-verdict-v4 findings[] 와 Story §9 debate transcript 간 정합 검증 책무 명시화.

### CFP-597 — review-verdict-v4 canonical v4.4 → v4.5 MINOR bump (marketplace_sync_declared, ADR-063 Amendment 1)

ADR-063 Amendment 1 (CFP-597) carrier — ArchitectAgent Phase 1 marketplace sync proactive self-check 결과 explicit marker 신규 optional field 추가.

#### Added (CFP-582)

- `templates/review-pl-base.md` — `§11.5. debate-protocol-v1 v1.2 정합 (CFP-582 / ADR-059 Amendment 2)` 섹션 신설
- `templates/review-pl-base.md` §12 버전 이력 — v3.2 entry append

#### Added (CFP-597)

- **review-verdict-v4 canonical v4.4 → v4.5** — `marketplace_sync_declared: bool` optional field 신설 (ADR-063 §결정 9 SSOT, Amendment 1)
- `related_adrs[]` 에 `ADR-063` entry 추가 (marketplace atomic invariant)
- `authors[]` + `amendment_log[]` 에 CFP-597 v4.5 entry 추가

#### Compatibility

- **Wire**: review-pl-base.md prompt block 신설 + review-verdict-v4 v4.5 MINOR (새 optional field). v4.4 이전 consumer backward-compat.
- **marketplace sync**: mclayer/marketplace#91 (merged 선행 — ADR-063 §결정 2 ordering, CFP-597 codeforge-pmo 0.1.3 sync).

## [1.5.0] - 2026-05-13

### CFP-528 Wave 2B — review-verdict-v4 v4.4 canonical mirror + review-pl-base §3 I-5 rule (sibling sync)

ADR-010 sibling sync — wrapper Phase 1 PR mclayer/plugin-codeforge#575 (CFP-528 Wave 2B, ADR-068 Amendment 1 I-5 dimensional empirical grounding) 의 canonical mirror.

#### Added

- **review-pl-base.md §3 I-5 mechanical detection rule** — DesignReviewPL 가 §3 / §7 quantitative parameter (10 dimension enum: latency / scale / cardinality / throughput / cost / accuracy / lifecycle / volume / rate / count) 의 `[empirical-source]` annotation 부재 시 finding emit (severity P1, category `dimensional_empirical_gap`, type `"dimensional-empirical-gap"`). Trigger 4종 / Mitigation 4종 / Justification / Exemption 체계. CodeReviewPL Tier C cross-validate (impl hardcoded numeric vs ADR / Story empirical-source mismatch).
- **review-verdict-v4 canonical v4.3 → v4.4 mirror** — wrapper sibling (mclayer/plugin-codeforge#575) 변경 byte-identical mirror (ADR-010 sibling sync, canonical owner per ADR-001). `dimensional_empirical_self_check_passed: bool` field + `findings[].type: "dimensional-empirical-gap"` literal + §13 dimensional empirical grounding self-check 신설.

#### Sibling sync

- Source canonical: 본 PR 자체 (codeforge-review = review-verdict canonical owner per ADR-001 / ADR-010)
- Wrapper sibling: mclayer/plugin-codeforge#575 (이미 OPEN, 본 PR 가 sibling sync follow-up per ADR-010 §4 wrapper-first 절차)
- Marketplace sync: mclayer/marketplace 별 PR (codeforge-review 1.5.0, ADR-063 atomic invariant 선행 merge 의무)

#### Compatibility

- **Wire**: review-verdict-v4 schema MINOR (new optional field). v4.3 producer / v4.4 consumer 양방향 backward-compat.
- **Marketplace sync**: 별도 PR (ADR-063 atomic invariant — marketplace sync 선행 merge).

## [1.4.1] - 2026-05-13

### CFP-462-followup — phase-gate-mergeable workflow sync (PATCH)

EPIC-RESULTS CFP-462 §6 carrier #1. Wrapper PR #500 (CFP-499 / ADR-010 Amendment 4 sibling-pr label fast-pass) merge 후 sibling repo backport 누락 detection. CFP-438 4 PR merge 시 codeforge-review 에서 `phase-gate-mergeable` required check name mismatch ACTION_REQUIRED 실증 → branch protection 임시 변경 / 복원 우회 패턴 발생.

#### Changed

- `.github/workflows/phase-gate-mergeable.yml` — wrapper SSOT (`templates/github-workflows/phase-gate-mergeable.yml`) verbatim mirror. CFP-113/123/133/342/499 누락 전체 backport (old version 였음).

#### Why

ADR-010 sibling sync 의무. sibling-pr label fast-pass + CFP-113/123/133/342 정합.

#### Compatibility

- **Wire**: workflow file 만 변경. agent / contract / overlay 영향 없음.
- **Marketplace sync**: 본 PATCH bump 의 marketplace.json mirror 는 별도 후속 carrier.

## [1.4.0] - 2026-05-13

### CFP-438 — review-verdict v4.1 → v4.2 MINOR bump (mechanical_self_check_passed optional bool field, ADR-065 sibling sync)

Wrapper Phase 1 PR (mclayer/plugin-codeforge cfp-438 branch) ADR-065 신설에 대한 canonical sibling sync (ADR-010 §4 wrapper-first 정합). ArchitectAgent Phase 1 산출물 commit 직전 7-item mechanical sync self-check (non-marketplace 영역) 결과 explicit marker 도입.

#### Added

- `docs/inter-plugin-contracts/review-verdict-v4.md` v4.1 → v4.2 MINOR bump:
  - `frontmatter` — `contract_version: "4.1" → "4.2"` + `related_adrs` 에 `ADR-065` append + `authors` + `amendment_log` 의 v4.2 entry
  - `## 2. Schema` — `mechanical_self_check_passed: <bool>` optional field 신설 (design lane only, code/security lane optional/omit 가능)
  - `## 3. 4-step Orchestrator algorithm` step 1 — `mechanical_self_check_passed 채움` line 추가 (design lane only, ArchitectPLAgent forward)
  - `## 11. ArchitectAgent Phase 1 mechanical self-check (v4.2 — ADR-065 / CFP-438)` 신설 — 7-item 표 + Producer/Consumer 책무 + 적용 lane + marketplace 영역 분리 (ADR-063 cross-ref)

#### Changed

- `.claude-plugin/plugin.json` — version 1.3.0 → 1.4.0 MINOR (contract schema 변경, ADR-037 정합). description CFP-438 entry append.

#### Why

ADR-065 (wrapper) 의 sibling sync 의무 (ADR-010 §4) — canonical = 본 plugin, sibling = wrapper. ADR-008 §결정 2 "새 선택 필드 추가" = MINOR bump 정합. Runtime impact 없음 (기존 v4.1 consumer 가 본 필드 무시 가능, backward-compat). design lane producer (ArchitectPLAgent) 가 ArchitectAgent §5.5 self-check 결과를 verdict packet 에 forward — false 시 즉시 `pl_recommendation: FIX` + ArchitectAgent re-spawn FIX 루프.

#### Cross-ref

- Wrapper canonical ADR: [ADR-065](https://github.com/mclayer/plugin-codeforge/blob/main/docs/adr/ADR-065-architect-phase1-mechanical-self-check.md)
- plugin-codeforge-design sibling PR: ArchitectAgent §5.5 + ArchitectPLAgent verdict packet + change-plan §13 신설
- Wrapper Phase 1 PR (paired sibling): https://github.com/mclayer/plugin-codeforge/pulls

## [1.3.0] - 2026-05-11

### CFP-391 — debate-protocol-v1 sibling sync + review-verdict v4.0 → v4.1 MINOR bump

Wrapper Phase 1 PR (mclayer/plugin-codeforge#400) 의 debate-protocol-v1 도입에 대한 codeforge-review canonical sibling sync. wrapper Phase 2 PR (#?, CFP-391 Phase 2) merge 후 follow-up.

### Added

- `templates/review-pl-base.md` §3.0~§3.3 신규 sub-section — debate-protocol-v1 dispatch SOP (Adversarial debate, CFP-391 / ADR-059):
  - §3.0 Divergence detection — review-verdict-v4 `findings[].anchor_id` field 기반 union iteration + severity/recommendation 분류 알고리즘
  - §3.1 Debate dispatch — Round 0 init + Round 1~N (max 5) execution + min 3 force_continue + max 5 escalation + EC-2/EC-3/EC-4/EC-7 invariant 정합
  - §3.2 Anchor 재발 검사 — Story §9 scan + count >= 2 → AskUserQuestion escalation (ADR-059 §결정 4)
  - §3.3 Transcript 영속화 — Story §9 inline append + §10 FIX Ledger `debate_artifact_ref` field + ArchitectPLAgent re-spawn 4-step
- `docs/inter-plugin-contracts/review-verdict-v4.md` v4.0 → v4.1 MINOR bump — `findings[].anchor_id` optional field 추가 (debate-protocol-v1 stable identifier 의존). ADR-008 §결정 2 "새 선택 필드 추가" MINOR bump 정합. `amendment_log` 신규 entry 2개 추가 (v4.0 + v4.1).

### Why

- wrapper Phase 1 PR (CFP-391) 가 review-verdict-v4 sibling 측에 `findings[].anchor_id` placeholder field 추가 (FIX-1 of DesignReview Iteration 1) 했으나 canonical sync follow-up 의무 (ADR-010 §단계 절차) + ADR-008 SemVer MINOR bump 의무 (F-003 finding of DesignReview Iteration 2).
- review-pl-base.md §3.0~§3.3 추가 = DesignReviewPLAgent verdict 합성 알고리즘 의 lane-agnostic 부분 (Story 2 / CFP-392 / Requirements lane 도입 시에도 동일 SOP). codeforge-review canonical SSOT.

## [Unreleased] - sibling sync follow-up

### CFP-137 — review-verdict v4 canonical mirror (sibling sync follow-up)

Wrapper Phase 1 PR (mclayer/plugin-codeforge#284) 의 review-verdict v4 cutover 의 ADR-010 sibling sync follow-up. canonical (본 plugin) 측 v4 mirror 신설 + v3 status flip.

### Added

- `docs/inter-plugin-contracts/review-verdict-v4.md` (NEW, canonical) — wrapper sibling verbatim mirror. `pl_recommendation` 자체가 final verdict + 신규 `worker_dialog_rounds` field (Adversarial debate measurable verification). 4-step Orchestrator algorithm (v3 5-step → 4-step).

### Changed

- `docs/inter-plugin-contracts/review-verdict-v3.md` `status: Active → Archived` (v4 cutover, CFP-137 wrapper Phase 1 PR merge 시점). Frontmatter `superseded_by: review-verdict-v4` + ADR-044 cross-ref + CFP-137 author entry. Body annotation 갱신: 이전 DEPRECATED PASSTHROUGH (CFP-134 / ADR-035) 영역 = v4 cutover 시 종료 명시.

### Notes

- v4 ADR carrier = mclayer/plugin-codeforge `docs/adr/ADR-044-phase-scoped-sequential-team.md` (CFP-137). ADR ID 가 ADR-041 → ADR-044 retro-renumber 된 사유: CFP-276 (PR #279 merged) 가 ADR-041 = doc-location-registry 선점, PR #283 (open) 가 ADR-042 + ADR-043 점유. createdAt earlier wins.
- `templates/review-pl-base.md` v3 → v4 schema 갱신은 별도 follow-up PR — 본 PR 은 contract canonical 신설 + v3 archive 만 (CFP-137 sibling sync 1차 wave).
- ADR-011 inter-plugin-drift CI invariant: 본 PR merge 후 wrapper PR #284 의 `inter-plugin-drift (CFP-E)` check 가 PASS 로 flip (canonical 부재 → 존재).

## [1.1.0] - 2026-05-07

### CFP-128 / ADR-033 — Container security 1st-layer (trivy + hadolint)

SecurityTestPL 1st-layer 도구에 trivy (image / IaC 스캔) + hadolint (Dockerfile lint) 추가. `templates/review-pl-base.md` v3.0 → v3.1 — §3 Container security severity rule row append. ADR-033 §결정 4 (carrier — wrapper canonical).

### Added

- SecurityTestPL 1st-layer: trivy + hadolint findings ingestion (Dependabot / CodeQL / Secret Scanning 과 동렬)
- `templates/review-pl-base.md` §3 container security severity rule (P0: critical CVE in base image / hardcoded secret in Dockerfile / privileged user — P1: outdated base image / missing healthcheck / non-pinned digest)

### Changed

- `templates/review-pl-base.md` v3.0 → v3.1 (CFP-128 / ADR-033 §3 Container security severity rule row)

### Cross-ref

- ADR-033 §결정 4 (carrier — wrapper canonical)
- D3 sibling sync PR #17 (commit 0e89c1d) — SecurityTestPL 1st-layer + review-pl-base container security
- F4 (this PR) — codeforge-review version bump

### Compatibility

- **Wire**: review_verdict v3 schema 변경 없음 (additive only). 1st-layer ingestion 확장만
- **Migration**: consumer 측 trivy + hadolint workflow 가 없으면 findings 누락 (graceful degradation, 별도 CFP 로 consumer template 추가)

## [1.0.0] - 2026-04-29

### CFP-35 (codeforge ζ arc) — review_verdict v2 retrofit (BREAKING)

ζ arc 첫 lane plugin self-write 검증 단계 (codeforge parent spec CFP-31 §5.5). PL이 Story §9 + GitHub comment + gate label 을 자체 write — DocsAgent 경유 폐기.

### Changed (BREAKING)

- `agents/{Design,Code,SecurityTest}ReviewPLAgent.md` 권한 확장:
  - allow: `Edit(docs/stories/**)`, `mcp__github__add_issue_comment`, `mcp__github__issue_write`
  - deny: `docs/{change-plans,adr,domain-knowledge,retros,inter-plugin-contracts,superpowers}/**` 명시 (이전 `docs/**` 광역 deny → narrow path-scoped)
- `templates/review-pl-base.md` §5.4 — review_verdict schema v1 → v2 (writes_completed audit + summary_for_* 제거)
- `templates/review-pl-base.md` §5.5 — Self-write 절차 신설 (4 steps + Lane → gate label / next phase 매핑)

### Added

- `docs/inter-plugin-contracts/review-verdict-v2.md` — canonical v2 contract SSOT
- `.claude-plugin/plugin.json` v0.3.0 → v1.0.0 BREAKING

### Why

codeforge ζ arc parent spec CFP-31 §5.5: 첫 lane plugin self-write 검증으로 review v2 retrofit 채택. 이미 plugin이라 코드 이동 0, contract revise만으로 패턴 검증. 이후 codeforge-pmo (CFP-36) 등 lane plugin도 같은 패턴 따름.

### Compatibility

- **Wire**: codeforge core 가 v2 verdict 처리 (v0.22.0+ 부터). v0.21 이하 codeforge는 v1 verdict 기대 → 호환 불가
- **Migration**: codeforge 와 codeforge-review 동시 bump 의무 — codeforge v0.22.0 + codeforge-review v1.0.0 짝
- **Side-by-side v1 + v2**: 불가능. v1 contract 는 wrapper에서 Deprecated 표기 후 archive 예정 (6 CFP 후)
- **Marketplace sync 의무**: 두 plugin 모두 동시 sync 필수

## [0.3.0] - 2026-04-29

### Changed

Bundle 1 contract alignment — Codex 협업 gap review에서 확인된 review_verdict v1 contract와 PL/worker md 사이 silent drift 5건 해소 (review-only):

- `templates/review-pl-base.md` §2 — packet에 `contract_version: "1.0"` 필수 필드 추가 + lane×field 매트릭스 행 추가 (gap #3)
- `templates/review-pl-base.md` §3 — Worker verdict (`PASS|ISSUES|NO_SHIP|ESCALATE_PACKET_INCOMPLETE`) → review_verdict.status (`PASS|FIX|FIX_DISCRETIONARY`) 변환표 신설 (gap #1)
- `templates/review-pl-base.md` §3 — P3/unclassified severity 처리 규정 신설 (P3 → P2 downgrade, unclassified → drop or P2) (gap #5)
- `templates/review-pl-base.md` §5.4 — typed verdict YAML 출력 블록 신설 (contract-required 8 필드 명시) (gap #2)
- `agents/{Claude,Codex}ReviewAgent.md` — packet 검증에 `contract_version` 추가; lane=security `first_layer_findings` 부재 시 `ESCALATE_PACKET_INCOMPLETE`로 일관 (이전: 비차단 결손 표기) (gap #7, gap #3)
- `agents/{Design,Code,SecurityTest}ReviewPLAgent.md` — packet 예시에 `contract_version: "1.0"` 첫 줄 추가 (gap #3)
- `.github/workflows/invariant-check.yml` — 신규 step "Packet contract_version presence" 추가 (3 PL × YAML)

### Why

review_verdict v1 contract는 codeforge core SSOT지만 review plugin 측 PL/worker md가 contract 8 필드 중 일부를 silently 누락 emit하거나 enum 불일치를 노출. Codex 협업 gap review에서 7건 P1 drift 확인 — 본 v0.3.0이 review-only 5건 처리. 나머지 cross-repo coordination 2건(`mechanical_category` schema 추가, `next_gate_label` 자기모순 해소)은 별도 PR (Bundle 2).

### Compatibility

`codeforge core` >= 0.17.0 호환 그대로 유지 — contract version v1.0 위반 없음 (오히려 v1.0 enforcement 강화).

상세 plan: [`docs/superpowers/plans/2026-04-29-bundle-1-contract-alignment.md`](https://github.com/mclayer/codeforge-internal-docs/blob/main/wrapper/plans/2026-04-29-bundle-1-contract-alignment.md).

## [0.2.0] - 2026-04-28

### Added

- `.github/workflows/invariant-check.yml` — own invariant-check workflow (carryover from codeforge core CFP-29 Phase 1 추출). Review category enum parity (3 lane × SSOT/PL/Codex) + Severity overrides count + breakdown parity (3 lane × SSOT/PL) 검증.

## [0.1.0] - 2026-04-28

### Initial extract from codeforge core

[`mclayer/plugin-codeforge`](https://github.com/mclayer/plugin-codeforge) v0.16.0 (commit `1e75442a9cb3f0004cf75cd8e0b152745cba532a`)에서 lane-agnostic review subsystem 추출.

### Added (initial)

- `agents/DesignReviewPLAgent.md` (codeforge core 에서 이동)
- `agents/CodeReviewPLAgent.md` (이동)
- `agents/SecurityTestPLAgent.md` (이동)
- `agents/ClaudeReviewAgent.md` (이동, lane-agnostic worker)
- `agents/CodexReviewAgent.md` (이동, lane-agnostic worker)
- `templates/review-pl-base.md` (이동, 3 PL 공통 base SSOT)
- `templates/review-checklists/design.md` (이동)
- `templates/review-checklists/code.md` (이동)
- `templates/review-checklists/security.md` (이동)
- `overlay/hooks/session-start-deps-check.sh` (NEW — codeforge core 설치 verify)
- `overlay/hooks/regen-agents.sh` (NEW — codeforge core merge.py 재사용 패턴)
- `docs/adr/ADR-001-extracted-from-codeforge.md` (NEW — 추출 사실 + verdict v1 contract 동결 시점)
- `README.md` + `CHANGELOG.md`

### Why

CFP-25 Phase 1 strategic payoff. codeforge core revision 비용 절감 + ADR-001 lane-agnostic worker 통합을 plugin 경계로 보존. 상세는 codeforge core repo의 [CFP-29 design spec](https://github.com/mclayer/codeforge-internal-docs/blob/main/wrapper/specs/2026-04-28-cfp-29-codeforge-review-extraction-design.md).

### Migration (from codeforge core monolith)

기존 codeforge consumer는 codeforge >= 0.17.0 + codeforge-review >= 0.1.0 두 plugin 모두 install 의무. 자세한 사항: codeforge core [migration-guide v0.16 → v0.17](https://github.com/mclayer/plugin-codeforge/blob/main/docs/migration-guide.md) 섹션.
