---
adr_number: 81
title: Codex worker prompt boilerplate composition SSOT (3 mandatory section + verify-before-trust scope + 3-lane partition)
status: Accepted
category: workflow-policy
date: 2026-05-17
carrier_story: CFP-819
parent_epic: null
supersedes: null
amends: null
amendments:
  - amendment_id: 1
    cfp: CFP-844
    date: 2026-05-17
    scope: "신규 §결정 D6 (Codex worker severity calibration rubric) append — Codex finding severity ↔ PL synthesis severity bidirectional calibration anchor (over-rate 금지 + security-relevant under-rate 금지). ground truth = DesignReviewPL final verdict severity (primary) / CodeReviewPL standalone fallback / 양쪽 dispatch 시 higher severity 기준. boundary-completeness exception (Codex P0 boundary-completeness × DesignReview P1 = over-rate 아님, +1 tier 허용). codex_severity_inflation (calibration) ≠ codex_false_positive_tally (accuracy) disjoint axis — full fp 0 chain sentinel 무영향. tracking = 기존 Story §9/§10 prose marker (`[codex-severity-inflation: ...]`, review-verdict-v4 contract field 신설 0 — doc-only fast-path 유지, ADR-081 §D5 declaration-only retain precedent verbatim 정합). D1-D5 본문 의미 변경 0건 — §결정 D6 sub-section append only. ADR-052 Amendment 7 + ADR-070 Amendment 2 cross-ref sibling. is_transitional false 유지 (permanent governance). mechanical_enforcement_actions[]=[] retain (§D5 declaration-only, §결정 D6.e known-limitation explicit binding — ADR-040 Amendment 3 DesignReview missing flag 회피)."
    status: applied
    ref: "## Amendment 1 / 본문 ### D6 + 거절된 대안 D6"
    sunset_justification: "ratchet 강화 방향 (verify-before-trust scope 에 severity calibration 차원 추가 — over-rate + security-relevant under-rate bidirectional anchor 신설). 약화 영역 0건 (D1-D5 본문 의미 변경 0, scope 축소 0). ADR-058 §결정 5 + ADR-064 §결정 7 top-down ratchet 정합 (강화 방향만 amendment)."
  - amendment_id: 2
    cfp: CFP-892
    date: 2026-05-17
    scope: "신규 §결정 D7 (Codex worker digest-parse self-verification + quantitative P0/P1/P2/P3 severity grading rubric + ground-truth divergence escape hatch explicit declaration) append — D6 calibration anchor 의 mechanical pre-screen 보완. (1) D7.a digest-parse self-verification step (yaml/json indentation re-check before issuing severity rating, ANCHOR-2 FP class 차단 — Story-4 CFP-834 digest-indentation 오독 carrier), (2) D7.b quantitative P0/P1/P2/P3 grading rubric (block / blocker / improvement / nit 4-tier explicit criteria, D6.b ground truth severity 의 정량화), (3) D7.c ground-truth divergence escape hatch (Codex P0 + PL divergence 시 ADR-070 strict-verify-gate 자동 trigger — declaration-only, mechanical lint 부재). D1-D6 본문 의미 변경 0건 — §결정 D7 sub-section append only. is_transitional false 유지 (permanent governance). mechanical_enforcement_actions[]=[] retain (§D5 declaration-only precedent 정합)."
    status: applied
    ref: "## Amendment 2 / 본문 ### D7 + 거절된 대안 D7"
    sunset_justification: "ratchet 강화 방향 (severity calibration rubric quantification + digest-parse pre-screen + escape hatch declaration). 약화 영역 0건 (D1-D6 본문 의미 변경 0, scope 축소 0). ADR-058 §결정 5 + ADR-064 §결정 7 top-down ratchet 정합 (강화 방향만 amendment)."
related_stories:
  - CFP-819  # carrier
  - CFP-770  # baseline fp 8
  - CFP-771  # baseline fp 8 (CFP-770 동반)
  - CFP-786  # carry-over fp 0 #1
  - CFP-801  # carry-over fp 0 #2
  - CFP-792  # carry-over fp 0 #3
  - CFP-795  # carry-over fp 0 #4
  - CFP-810  # carry-over fp 0 #5 (sentinel reach)
  - CFP-844  # Amendment 1 — 신규 §결정 D6 severity calibration rubric (CFP-825 retro §6 후보 2)
related_adrs:
  - ADR-052  # Codex Proactive Check 6 touchpoints (parent — Amendment 6 + Amendment 7 (CFP-844) cross-ref)
  - ADR-070  # verify-before-trust pattern (sibling — D1/D2/D5 cross-ref + Amendment 2 (CFP-844) D6 보완)
  - ADR-082  # write-time self-write verification mandate (D5 declaration-only retain 선례 super-class)
  - ADR-058  # ADR sunset criteria mandate (§결정 1/2/3 정합)
  - ADR-060  # evidence-enforceable promotion framework (declaration-only retain)
  - ADR-064  # decision principle mandate (active amendment + forbid-list)
  - ADR-068  # boundary completeness invariants (3-lane partition cross-ref)
  - ADR-073  # verify-before-assert (Orchestrator self-assertion layer 자매)
  - ADR-045  # PMOAgent cross-story pattern adr trigger (forcing function)
  - ADR-079  # KST timestamp display mandate
  - ADR-039  # default subagent context
  - ADR-054  # doc-only fast-path (§결정 1 신규 ADR full-lane 강제)
related_files:
  - docs/adr/ADR-052-codex-proactive-check-touchpoints.md
  - docs/adr/ADR-070-codex-verify-before-trust.md
  - docs/orchestrator-playbook.md
  - CLAUDE.md
is_transitional: false
mechanical_enforcement_actions: []
---

# ADR-081: Codex worker prompt boilerplate composition SSOT (3 mandatory section + verify-before-trust scope + 3-lane partition)

## 상태

Accepted (2026-05-17 KST, CFP-819 carrier).

## 컨텍스트

[verified] CFP-810 retro §6 후보 1 verbatim 인용 (`wrapper/retros/2026-05-17-cfp-810-kst-paren-exempt.md` L110):

> "Codex worker prompt boilerplate 표준화 + verify-before-trust ground-truth contract"

ADR-052 (Codex Proactive Check 6 touchpoints) + ADR-070 (verify-before-trust pattern) 은 두 가지 정책을 명문화했다:

- **ADR-052 D2** = "6 touchpoint 자동 활성, opt-in 없음" — dispatch 발동 자체의 normative anchor
- **ADR-070 D2** = "file content verbatim 첨부 의무" — artifacts payload 형식의 normative anchor

그러나 **Codex worker prompt 본문의 mandatory section composition** 영역은 normative anchor 부재 — playbook §3.10 dispatch prompt template 이 SSOT 역할을 도덕적 강제로 수행 중. 본 ADR 발의 직전까지 boilerplate 구성 룰이 어디서 정합한지 SSOT 없음. 즉 "어떤 정보가 prompt 안에 의무 첨부되어야 하는가"의 영역이 ADR-052 Amendment 5 (D2 cross-ref) 와 ADR-070 D2 (verbatim 의무) 사이 cross-document 분산 상태였다.

### 6-Story carry-over evidence sentinel (boilerplate 도입 효과 측정)

**"6-Story" 정의 (label vs file count disambiguation)** — 6-Story = **1 baseline cluster (CFP-770/771 paired carrier, same fp:8 incident) + 5 consecutive fp-0 (CFP-786/801/792/795/810)** = 총 **6 units** (1 cluster + 5 individual Story). file count 차원 = 7 retro file (cluster 안 2 file + 5 individual 1 file 씩).

[verified] 7 retro file 본 worktree 안 존재 (`Glob` + `ls` 결과, codeforge-internal-docs `wrapper/retros/` 영역):

| retro file | Story | codex_fp_tally | boilerplate evidence |
|---|---|---|---|
| `wrapper/retros/2026-05-16-cfp-770-kst-timestamp-display-mandate.md` | CFP-770 | 일부 (771 합산 = 8) | **baseline pre-boilerplate** |
| `wrapper/retros/2026-05-16-cfp-771-kst-timestamp-mechanical-lint.md` | CFP-771 | 일부 (770 합산 = 8) | **baseline pre-boilerplate** |
| `wrapper/retros/2026-05-17-cfp-786-main-baseline-ci-debt-cleanup.md` | CFP-786 | **0** | carry-over boilerplate 적용 시작 |
| `wrapper/retros/2026-05-17-cfp-801-claude-md-line-cap-normalization.md` | CFP-801 | **0** | carry-over boilerplate 정합 |
| `wrapper/retros/2026-05-17-cfp-792-canonical-sibling-sync.md` | CFP-792 | **0** | carry-over boilerplate 정합 |
| `wrapper/retros/2026-05-17-cfp-795-post-merge-fix-exemption.md` | CFP-795 | **0** + TRUE positive 적중 100% | carry-over boilerplate + 정확 적중 |
| `wrapper/retros/2026-05-17-cfp-810-kst-paren-exempt.md` | CFP-810 | **0** + cosmetic TRUE positive 적중 | carry-over boilerplate + carrier 5/7 sentinel reach YES |

**6-Story 누적 evidence (1 baseline cluster CFP-770/771 paired + 5 consecutive fp-0)**: CFP-770/771 (fp 8 baseline cluster, paired carrier) → CFP-786/801/792/795/810 (5 consecutive fp 0 carry-over). 6 units 차원 = 1 cluster + 5 individual. file count 차원 = 7 retro file. boilerplate codification 정당성 충족.

### ADR-045 Amendment 5 §D-9 forcing function trace

PMOAgent `cross_story_pattern_adr_trigger` (pattern_count ≥ 2 → §6 ADR 후보 발의 의무) 의 forcing function 충족:

- pattern_count = 5 consecutive carry-over Story (threshold reach YES)
- anchor_id = `codex_worker_prompt_boilerplate_drift`
- escalation_action = `adr_draft_emitted` → 본 ADR-081
- cross-Story chain: [CFP-770/771 (1 baseline cluster, paired carrier)] + CFP-786/801/792/795/810 (5 consecutive fp-0) → CFP-819 (carrier). 6 units 차원 (1 cluster + 5) / 7 retro file 차원.

### Amendment 5 ↔ 본 ADR 영역 분리 (Story §2.4 PL synthesis verbatim)

| 영역 | ADR-052 Amendment 5 (CFP-578) | ADR-070 (CFP-578) | 본 ADR-081 (CFP-819) |
|---|---|---|---|
| dispatch 발동 (자동/optional) | ✅ D2 + Amd 1-5 (강화) | — | — |
| artifacts payload **형식** (verbatim vs path) | ✅ A1 (verbatim 의무) | ✅ D2 (verbatim 의무) | — (cross-ref) |
| verify-before-trust **흐름** (verify+reject) | — | ✅ D1/D3 | — (cross-ref) |
| prompt 본문 **mandatory section composition** | ❌ | ❌ | ✅ §결정 D1 (3 mandatory boilerplate 영역) |
| verify-before-trust **scope 분리** (file/dir/cross-repo) | ❌ | — | ✅ §결정 D2 (5 sub-scope 명세) |
| 3-lane partition (Codex / DesignReview / CodeReview disjoint) | ❌ | ❌ | ✅ §결정 D3 (3-lane disjoint scope 표) |

본 ADR-081 = ADR-052 Amendment 5 + ADR-070 D2 의 cross-document 분산 영역을 단일 SSOT 로 통합. ADR-052/070 본문 정책 의미 변경 0건 (Story §1 OOS 정합).

## 결정

본 ADR 은 declaration only — mechanical lint 부재 (D5 declaration-only retain 정합, ADR-070 §D5 precedent verbatim). 본문 normative anchor SSOT 만.

### D1. 3 mandatory boilerplate 영역

Codex worker spawn 시 ProactiveCheckPacket `artifacts` 필드 + prompt body 안 다음 3 mandatory section 의무:

#### D1.A — dogfood-out Story path (verbatim 첨부)

codeforge family 의 Story file 영역 (`mclayer/codeforge-internal-docs/<plugin-folder>/stories/CFP-NNN.md`) 의 verify 대상 §섹션 verbatim 첨부 의무. file path reference 만 사용 금지 (ADR-070 D2 / ADR-052 Amendment 5 A1 정합).

| 영역 | 운영적 정의 | 예시 verbatim |
|---|---|---|
| §1 사용자 요구사항 | story-section-1-immutable.yml SSOT, 변조 금지 invariant — 항상 verbatim 첨부 | `## §1. 사용자 요구사항 (verbatim)\n\n**발의 배경**: ...` |
| §2-§6 PL synthesis 본문 | RequirementsPL synthesis (도메인 해석 + 요구사항 확장) — touchpoint #4 review scope | `## §2. 도메인 해석\n...` |
| §7 설계 서사 | ArchitectAgent synthesis — touchpoint #2 review scope | `## §7. 설계 서사\n...` |
| §10 FIX Ledger | Orchestrator append 영역 — FIX 분석 시 verify scope | `## §10. FIX Ledger\n...` |

cap 초과 시 partial 첨부 허용 (verify 대상 영역만 verbatim + 나머지 `[partial: lines NN-NN]` marker, ADR-052 Amendment 5 A1 정합).

#### D1.B — lane stage 표기 (current_lane + phase)

Codex worker 가 어느 lane / phase 영역의 산출물을 verify 하는지 명시 의무:

```yaml
current_lane: <requirements|design|design-review|develop|code-review|security-test|integration-test>
phase: <phase:요구사항|phase:설계|phase:설계-리뷰|phase:구현|phase:구현-리뷰|phase:보안-테스트|phase:통합-테스트>
```

운영적 정의:

- Codex finding severity / category 가 lane scope 와 정합한지 cross-check 영역
- 3-lane partition (D3) 적용 영역 식별 — Codex factual citation 영역 vs DesignReview boundary completeness 영역 vs CodeReview style 영역 disjoint scope

#### D1.C — sandbox boundary 명시 (sandbox_outside_paths)

Codex sandbox 영역 외 file path enumerate 의무 (cross-repo / cross-plugin path 포함):

```yaml
sandbox_outside_paths:
  - mclayer/codeforge-internal-docs/wrapper/stories/CFP-NNN.md  # internal-docs (cross-repo)
  - mclayer/plugin-codeforge-{requirements,design,develop,review,test,pmo}/...  # sibling plugin (cross-plugin)
  - mclayer/marketplace/marketplace.json  # cross-repo
  - docs/inter-plugin-contracts/MANIFEST.yaml  # wrapper internal (sandbox 영역 가능성)
```

운영적 정의:

- Codex worker 가 own working directory 안 Read 불가 영역 식별
- 모든 sandbox_outside_paths file content = verbatim 첨부 의무 (ADR-070 D2 + ADR-052 Amendment 5 A1 정합)
- mechanical injection layer 부재 — Orchestrator turn 내 verbatim composition 수동 (declaration-only retain 정합)

### D2. verify-before-trust scope 분리 (5 sub-scope)

Orchestrator 가 Codex finding evidence 의 ground truth verify 시 scope 별로 verify 방법 분리 의무 (ADR-070 D1 + ADR-073 정합):

#### D2.A — file scope verify (single file 안 grep count)

- **scope**: single file 안 anchor / line / 문자열 영역
- **verify 도구**: `Grep -n <pattern> <file>` 또는 `Read(<file>, offset, limit)` 직접 추출
- **claim 형식**: `[verified] <file>:<line> "<verbatim quote>"` (anchor + line + quote 3-tuple)
- **mismatch 처리**: ADR-070 D3 reject 흐름

#### D2.B — dir scope verify (recursive grep)

- **scope**: dir tree 안 file enumerate / pattern occurrence count
- **verify 도구**: `Glob` + `Grep` recursive (예: `Glob("docs/adr/ADR-*.md") + Grep("pattern", glob="docs/adr/*.md", output_mode="count")`)
- **claim 형식**: `[verified] <dir>/**/<file_pattern>: <N> matches` (dir + pattern + count 3-tuple)
- **mismatch 처리**: ADR-070 D3 reject 흐름

#### D2.C — cross-repo scope verify (gh api / git fetch origin)

- **scope**: sibling plugin / cross-repo (marketplace.json / internal-docs) file 영역
- **verify 도구**: `mcp__github__get_file_contents` 또는 `git fetch origin <repo>; git show origin/main:<path>` (ADR-073 정합)
- **claim 형식**: `[verified-cross-repo:<org>/<repo>@<branch>:<commit>] <file>:<line>` (repo + branch + commit + file + line 5-tuple)
- **mismatch 처리**: ADR-070 D3 reject 흐름 + ADR-073 D1 cross-repo verify 의무

#### D2.D — grep count claim verify (active vs historical 차원 명시 의무)

Codex 발화 "ADR-NNN 안 N 곳 에 X 단어 발화" claim 영역 = active scope vs historical scope 차원 명시 의무:

| 차원 | 운영적 정의 | 검증 방법 |
|---|---|---|
| **active scope** | 현재 효력 영역 — Amendment 본문 / 결정 본문 + 인용 영역 모두 포함 | `Grep("pattern", file)` 전체 count |
| **historical scope** | retro / archived ADR / FIX Ledger / Story 진행 이력 — 인용 영역 보존 의도 영역 | active count 와 분리 명시 ("active: M, historical: N") |
| **citation scope** | cross-ref 영역 (e.g. "ADR-052 §결정 D2") — 단어 발화 vs 인용 별도 | citation source = file:line 명시 |

claim mismatch 차원 = active vs historical 혼동 시 ADR-070 D3 reject + false positive count tally.

#### D2.E — ADR §결정 번호 정확성 verify

Codex 발화 "ADR-NNN §결정 N (또는 D-N)" claim 영역 = 실제 ADR file 안 해당 §결정 anchor 존재 확인 의무:

- **verify 도구**: `Glob("docs/adr/ADR-NNN-*.md") + Grep -nE "^### (D|결정) ?N" <file>`
- **claim 형식**: `[verified] <ADR file>:<line> "### <결정 N anchor>"` (anchor 존재 확인 + line + verbatim)
- **mismatch 처리**: ADR-070 D3 reject (false §결정 번호 발화 = false positive 영역)

### D3. 3-lane partition (Codex / DesignReview / CodeReview disjoint scope)

Codex worker output 영역 vs lane review agent (DesignReviewPL / CodeReviewPL) review 영역 disjoint scope 분리 의무. cosmetic detection 영역 type 분리.

| Lane | scope | mechanical anchor | 영역 type |
|---|---|---|---|
| **Codex worker** | factual citation — file:line evidence + verbatim quote + grep count + ADR §결정 번호 + cross-repo commit SHA | ADR-081 D2 (5 sub-scope) + ADR-070 D1/D2/D3 + ADR-073 | **factual ground truth** (verify-before-trust scope) |
| **DesignReviewPL** | boundary completeness — API contract semantic (I-1) + cross-module propagation (I-2) + conditional guard placement intent (I-3) + wording SSOT (I-4) + dimensional empirical grounding (I-5) | ADR-068 4 invariants + Amendment 1 I-5 | **boundary completeness self-audit** (review-verdict-v4 v4.4 carrier) |
| **CodeReviewPL** | post-impl style + historical reference 보존성 영역 — Story §10 P2-defer row 안 historical 5 refs 인용 영역 보존 의도 | review-verdict-v4 v4.5 (CFP-810 P2 C-002 precedent) | **style + history preservation** (post-impl review scope) |

**disjoint invariant**: 동일 anchor_id 영역에서 Codex + DesignReview + CodeReview 셋 모두 발화 시 = scope type mismatch 신호. 처리:

- Codex 발화 = factual citation 영역만 (`[verified]` marker 의무)
- DesignReview 발화 = boundary completeness 영역만 (4 invariant 안 분류)
- CodeReview 발화 = style + history 영역만 (post-impl scope)

영역 중복 발화 시 dedup → severity 높은 쪽 채택 (codeforge `review-responsibility` skill SSOT 정합).

### D4. ADR-052 / ADR-070 본문 정책 SSOT 보존 invariant

본 ADR-081 = cross-ref + downstream codification 만. ADR-052 D1-D4 + Amendment 1-5 본문 의미 변경 0. ADR-070 D1-D5 본문 의미 변경 0. Story §1 OOS "ADR-052/070 본문 정책 변경 금지" 정합.

ADR-052 Amendment 6 sub-section append (본 ADR-081 신규 영역 cross-ref 1 paragraph만) = 의미 변경 없음 (sub-section append 패턴 Amendment 1-5 정합).

### D5. evidence-enforceable framework entry append 면제 (declaration-only retain)

ADR-070 §결정 D5 precedent verbatim 정합. mechanical lint 가 검출 가능한 sentinel signal 영역의 후보 모두 robustness risk 보유:

| 후보 signal | 검출 가능성 | 메커니즘 | 적용 risk |
|---|---|---|---|
| (a) Codex spawn prompt 안 3 mandatory section 존재 검출 (regex) | HIGH | static regex on prompt body | false positive — prompt body 형식 자유도 (boilerplate template 절대값 부재) |
| (b) Codex worker output 안 5 sub-scope marker `[verified]` 발화 검출 | MEDIUM | output regex | locale 의존 + Codex output schema 영역 외 (안정성 risk) |
| (c) 3-lane partition 영역 disjoint scope 자동 비교 (Codex / DesignReview / CodeReview output cross-validation) | LOW | runtime probe (3 verdict packet anchor_id cross-diff) | platform inherent runtime probe 영역, mechanical lint 영역 외 |
| (d) **declaration-only ADR (mechanical lint 부재, 본 ADR 본문 SSOT)** | **HIGH** | 본 ADR 본문 normative anchor 만 | manual gate 의존 (의식 필요) |

**채택 = (d) declaration-only retain**. evidence-checks-registry.yaml entry append 면제 (ADR-070 §결정 D5-C 거절된 대안 정합 — "declaration-only retain 영역에서도 evidence-checks-registry entry append (warning tier 0-validation) = registry schema scope 침해").

**근거**:

1. (a)/(b)/(c) 모두 robustness risk 보유 — false positive 차단 cost 가 boilerplate 도입 cost 보다 큼
2. ADR-060 evidence-enforceable promotion framework 의 mechanical lint forcing function 확장 패턴 (CFP-389 → CFP-449 → CFP-481 → CFP-506 → CFP-530 carrier loop) 은 **static doc analysis 영역** (ADR frontmatter / forbid-list 어휘 / branch name parse / line count / yml structure) — 본 ADR 영역 (boilerplate composition / verify scope marker / 3-lane partition disjoint) 과 영역 type mismatch
3. 후속 carrier sentinel 조건 = 2 회 이상 mechanical lint 검출 가능 sample 누적 시 carrier 발의 (sentinel) — 현재 0 sample 누적

**거절된 대안 D5**:

- (D5-A) (a) static regex 채택 (Codex spawn prompt 안 3 mandatory section 존재 검출) — false positive 차단 cost 가 정당성 부재 (boilerplate template 형식 자유도 영역)
- (D5-B) (c) runtime probe 자동화 (3 verdict packet anchor_id cross-diff layer) — platform inherent 영역 침범 (Codex output schema parsing layer 신설 = 별도 carrier 영역)
- (D5-C) declaration-only retain 영역에서도 evidence-checks-registry entry append (warning tier 0-validation) — registry schema scope 침해 (ADR-070 §D5-C 거절된 대안 정합)
- (D5-D) marker 어휘 신설 (예: `[verified-file]` / `[verified-dir]` / `[verified-cross-repo]`) — CFP-810 retro §6 후보 5 정합, **별 carrier** 분리. 본 ADR scope = verify scope 분리 의무 본문 명시만, marker 어휘 변경 없음

---

## Amendment 1 (2026-05-17, CFP-844)

### Context (Amendment 1)

CFP-825 retro §6 후보 2 (PMOAgent `cross_story_pattern_adr_trigger`, `escalation_action: adr_draft_emitted`) carrier. D2 (verify-before-trust 5 sub-scope) 는 Codex finding **factual citation 정확성** (file:line / verbatim / grep count / ADR §결정 번호) 을 다룬다 — finding 의 **사실 근거** 검증 layer. 그러나 finding 의 **severity 경중 calibration** 영역 (Codex 가 발화한 P0/P1/P2 가 실제 review lane ground truth severity 와 정합하는가) 은 D1-D5 normative anchor 부재였다.

[verified] review-verdict-v4 v4.5 에 `codex_severity_inflation` field 미존재 (verified-via: `git show origin/main:docs/inter-plugin-contracts/review-verdict-v4.md` grep empty, `contract_version: "4.5"` CFP-597). 즉 severity calibration 추적 영역은 contract surface 부재 — 기존 prose channel (Story §9 verdict / §10 FIX Ledger 비고) 만 활용 가능. 본 Amendment 는 이 영역을 declaration-only normative anchor (신규 §결정 D6) 로 승격한다. D1-D5 본문 의미 변경 0건 — §결정 D6 sub-section append only (Amendment 패턴 = ADR-052 Amendment 1-6 / ADR-070 Amendment 1 정합).

### D6. Codex worker severity calibration rubric (declaration-only normative anchor)

ADR-081 §D5 declaration-only retain invariant (ADR-070 §D5 precedent verbatim) 정합 — §결정 D6 = declaration-only normative anchor, mechanical lint 부재. codex_severity_inflation tracking = 기존 Story §9/§10 prose marker (신규 review-verdict-v4 contract field 신설 0 — contract bump 회피, doc-only fast-path 유지).

#### D6.a — bidirectional severity anchor

Codex finding severity ↔ PL synthesis severity **양방향** calibration 의무:

1. **over-rate 금지**: Codex severity > PL synthesis severity (factual citation scope = D2.A-E) 시 PL 이 ground truth severity 로 calibrate. Codex sensitivity inflation 차단.
2. **security-relevant under-rate 금지**: Codex severity < 실제 보안 경중 시 PL 이 실제 severity 로 calibrate. over-rate 만 anchor 시 보안 blind spot 발생 risk (Researcher Unknown #2) — bidirectional anchor 가 차단 (ADR-064 broad coverage 정합).

#### D6.b — ground truth severity 우선순위

| 차원 | ground truth | 근거 |
|---|---|---|
| **primary** | DesignReviewPL final verdict severity | 설계 lane Codex proactive check (touchpoint #2) 표준 path |
| **fallback** | CodeReviewPL standalone severity | touchpoint #3 단독 dispatch 시 (DesignReview 미경유) |
| **양쪽 dispatch** | higher severity PL 기준 | codeforge `review-responsibility` skill dedup rule SSOT 정합 (ADR-081 D3 3-lane partition 정합) |

#### D6.c — boundary-completeness exception

Codex P0 boundary-completeness finding (review-verdict-v4 `findings[].type="boundary-completeness"`, ADR-068 I-1~I-5) × DesignReviewPL P1 final verdict = over-rate **아님** (PL incomplete audit 신호 — Codex sensitivity 정상, +1 tier 허용). 단 factual citation scope (D2.A-E) severity 불일치 = 순수 calibration 대상 (exception 미적용).

#### D6.d — disjoint axis preservation invariant

`codex_severity_inflation` (calibration axis) ≠ `codex_false_positive_tally` (accuracy axis) — 별개 axis. carry-over fp 0 chain sentinel (CFP-770/771 baseline → CFP-786/801/792/795/810 5 consecutive fp 0; ADR-081 6-Story sentinel) 무영향 — severity calibration 은 finding accuracy 와 무관 (finding 자체는 TRUE positive 이되 severity 만 mis-rate 한 경우 fp 0 chain 영향 0).

#### D6.e — tracking = 기존 Story §9/§10 prose marker (declaration-only)

PL 이 verdict 시 Codex finding severity ↔ PL synthesis severity delta 를 Story §9 verdict prose 또는 §10 FIX Ledger 비고에 marker 기재:

```
[codex-severity-inflation: Codex:P0 vs PL:P1 <scope>]
```

기존 prose channel 활용 — 신규 review-verdict-v4 contract field 신설 0 (contract bump 회피, doc-only fast-path 유지, ADR-081 §D5 declaration-only retain precedent verbatim 정합). mechanical lint = 별개 후속 carrier (sentinel 조건 = 2+ mechanical-detectable sample 누적 시, 현재 0 sample). **§결정 D6.e known-limitation explicit binding** — `mechanical_enforcement_actions[]=[]` retain 이 의도된 declaration-only 선택임을 명시 (ADR-040 Amendment 3 DesignReview missing-flag 회피, ADR-082 §결정 6 / ADR-070 §D5 선례 정합).

#### D6.f — sunset trigger 아님 명시

`codex_severity_inflation` count 자체 = calibration 추적 metric, ADR-081 유효성 indicator 아님. `is_transitional: false` (permanent governance). metric 0 수렴 = Codex accuracy 향상 + PL calibration 정착 둘 다 정상 (ADR-081 폐기 트리거 아님 — accuracy axis sunset gate 와 disjoint, D6.d 정합).

### 거절된 대안 D6

- (D6-A) review-verdict-v4 신규 `codex_severity_inflation` contract field 신설 (structured severity delta surface) — contract MINOR bump + sibling sync (ADR-008/010) + Phase 2 PR 필요 = doc-only fast-path 이탈. ADR-081 §D5 declaration-only retain precedent 위배. prose marker 채택 (mechanical lint 부재 영역 = contract surface 부적합, ADR-070 §D5-C 정합).
- (D6-B) over-rate 단방향 anchor (Codex severity > PL 만 차단) — security-relevant under-rate blind spot 미차단 (Researcher Unknown #2). bidirectional 채택 (ADR-064 broad coverage).
- (D6-C) boundary-completeness exception 미도입 (Codex P0 × DesignReview P1 = 무조건 over-rate) — ADR-068 I-1~I-5 incomplete audit 신호 (Codex sensitivity 정상) 를 false over-rate 로 오분류. +1 tier exception 채택 (D6.c).
- (D6-D) codex_severity_inflation 을 ADR-081 sunset metric 으로 채택 — accuracy axis (`codex_false_positive_tally`) 와 disjoint (D6.d). severity calibration metric 0 수렴 = 정상 (폐기 신호 아님). is_transitional false 유지 (D6.f).

### 결과 (Amendment 1)

- Codex finding severity ↔ PL synthesis severity bidirectional calibration normative anchor 신설 — D6 SSOT (declaration-only retain, §D5 precedent)
- ground truth severity 우선순위 (DesignReviewPL primary / CodeReviewPL fallback / higher PL 양쪽) 명시 — D6.b SSOT
- boundary-completeness exception (Codex P0 × DesignReview P1 = over-rate 아님, +1 tier) — D6.c SSOT
- disjoint axis preservation invariant (calibration ≠ accuracy, fp 0 chain 무영향) — D6.d SSOT
- tracking = 기존 Story §9/§10 prose marker (`[codex-severity-inflation: ...]`, contract field 신설 0) — D6.e SSOT
- D1-D5 본문 의미 변경 0건 — §결정 D6 sub-section append only (ADR-052 Amendment 1-6 / ADR-070 Amendment 1 패턴 정합, §D4 SSOT 보존 invariant 정합)
- ADR-052 Amendment 7 (D6 cross-ref sub-section append) + ADR-070 Amendment 2 (D6 보완 관계 cross-ref-only) sibling
- CLAUDE.md L170 blockquote severity calibration cross-ref 1 줄 추가 (line-cap 320 invariant 정합)
- ADR-RESERVATION 무접촉 (Amendment 영역 — row 81 = CFP-819 active 유지, ADR file 동일)
- `mechanical_enforcement_actions[]=[]` retain (declaration-only, §결정 D6.e known-limitation explicit binding)

## Amendment 2 (CFP-892)

CFP-892 carrier (Epic A close follow-up CFP 후보 1/6, PMO retro Story-4/5 carry-over). Issue #892 §3 sub-pattern 분류 verbatim — 3 outstanding gap:

1. **Codex digest-indentation 오독** (ANCHOR-2 FP class, Story-4 CFP-834) — Codex 가 yaml block 안 nested key indentation 잘못 읽음. D6 calibration anchor 가 severity calibration 영역 cover 하나 digest-parse mechanical pre-screen 부재.
2. **Codex severity over-claim** — D6.a/b/c 가 이미 cover. 단 quantitative P0/P1/P2/P3 grading 정량 기준 부재 — D6.b 의 ground truth severity ordering 만 있고 per-tier criteria 없음.
3. **ground-truth divergence escape hatch** — ADR-070 strict-verify-gate 가 이미 작동 중이나 ADR-081 § 안 explicit cross-ref 부재.

본 Amendment 2 = D6 보완 (D6 의미 변경 0건, §결정 D7 sub-section append only).

### D7. Codex worker digest-parse + severity rubric + escape hatch (declaration-only normative anchor)

ADR-081 §D5 declaration-only retain invariant 정합 — §결정 D7 = declaration-only normative anchor (mechanical lint 부재, D6 정합).

#### D7.a — digest-parse self-verification step (ANCHOR-2 FP class 차단)

Codex worker 가 yaml / json / markdown table 영역 finding 발화 직전 **indentation re-check** 의무:

- yaml block 안 nested key 의 indentation 을 visually verbatim re-read
- "이 contract_version 이 reinvestigation_tracking top-level block 의 일부인가, 아니면 contract-level field 인가" 류 ambiguous structural 판정 시 finding 발화 보류 + Story 본문 directly cite (file:line + 7 line 전후 context)
- self-verification 발화 marker: `[digest-parsed: <field-path> @ L<N> (indent <level>)]` Story §10 prose 안 inline

본 step 은 ANCHOR-2 FP class (Story-4 CFP-834 F-DESIGNREVIEW-CFP834-1 digest-indentation 오독) directly 차단 forcing function. CFP-892 §3 sub-pattern 1 carrier.

#### D7.b — quantitative P0/P1/P2/P3 grading rubric (D6.b 정량화)

| Tier | 의미 | criteria (Codex finding) | examples |
|---|---|---|---|
| **P0 (block)** | ship 차단 | (a) 정책 SSOT 위반 + verbatim grep 가능 evidence / (b) 보안 boundary 침해 (auth / secret / injection) / (c) data integrity invariant 위반 (rollback path 부재 schema bump) | "phase-gate-mergeable.yml 안 required check 명단 변경 시 ADR-024 §결정 위반 가능", "API key plaintext logging" |
| **P1 (blocker)** | ship 강력 차단 (PL 재량 review) | (a) ADR-068 boundary-completeness 4 invariant 부재 + Story §3 영향 area 명시 / (b) §7.4 OperationalRisk N/A 사유 부재 / (c) §8 Test Contract coverage 0 boundary | "P1 — design lane §3 cross-module propagation completeness 미충족 (I-2 위반)" |
| **P2 (improvement)** | defer 허용 (severity ≠ ship 차단) | (a) refactor 권장 / (b) wording 정확성 / (c) documentation gap (정책 SSOT 영역 외) / (d) historical pattern reference 보존 (CodeReview style+history) | "P2 — README example outdated, defer 가능", "P2 — comment 정확성 개선 권장" |
| **P3 (nit / cosmetic)** | non-blocking | (a) 어휘 선택 / (b) markdown formatting / (c) self-meta text precision (lint 자체 spec 인용 등) | "P3-cosmetic — section header 어휘 선택" |

**boundary-completeness exception (D6.c 정합)** — Codex P0 boundary-completeness × DesignReview P1 = +1 tier 허용 (PL incomplete audit 신호, calibration over-rate 아님).

**security-relevant under-rate 차단 (D6.a 정합)** — Codex 가 보안 영역 P2 / P3 발화 시 PL 이 실제 severity 로 calibrate (security blind spot 차단).

본 표 = D6.b ground truth severity ordering (DesignReviewPL primary / CodeReviewPL fallback) 의 per-tier criteria. ADR-064 broad coverage 정합 (4-tier criteria → grading ambiguity 차단).

#### D7.c — ground-truth divergence escape hatch (ADR-070 cross-ref explicit)

Codex P0 claim 시 Orchestrator strict-verify-gate (ADR-070 verify-before-trust) 가 **자동 trigger** — Codex P0 finding 의 ground truth (file content / grep / ADR §결정 verbatim) 를 Orchestrator 가 direct Read 로 verify. mismatch 감지 시:

- 1차: Codex finding reject + Story §10 false positive count tally + override rationale prose
- 2차: review-verdict-v4 v4.5 `codex_false_positive_tally` count + 1

본 escape hatch = ADR-070 §결정 1 mandate (Codex finding evidence ground-truth direct verify) 의 ADR-081 D6/D7 calibration framework 안 explicit cross-ref. 신규 mechanism 아님 — ADR-070 기존 mechanism 의 declaration-only 명시화 (declaration-only retain precedent §D5 정합).

#### D7.d — disjoint axis preservation (D6.d 재확인)

D7.a (digest-parse), D7.b (P0/P1/P2/P3 rubric), D7.c (escape hatch) 셋 모두 D6.d disjoint axis invariant 정합:

- `codex_severity_inflation` (calibration axis, D6) ≠ `codex_false_positive_tally` (accuracy axis, ADR-070) — 별개 measurement
- D7.a digest-parse FP 는 **accuracy axis** 영향 (FP count +1) — calibration 무관
- D7.b severity rubric 정량화 는 **calibration axis** 강화 — accuracy 무관
- D7.c escape hatch 는 **accuracy axis** layer (FP detection forcing function) — calibration 영역 외

fp 0 chain sentinel (CFP-770/771 baseline → CFP-786/801/792/795/810 5 consecutive fp 0) 무영향 (D7 = declaration-only, mechanical detection 부재).

### 거절된 대안 D7

- (D7-A) review-verdict-v4 신규 `codex_severity_grade` enum field (P0/P1/P2/P3) 신설 — contract MINOR bump + sibling sync. doc-only fast-path 이탈. D6.e prose marker 채택 precedent 정합 (declaration-only retain).
- (D7-B) digest-parse self-verification mechanical lint (Codex worker output 안 `[digest-parsed: ...]` marker grep) — D6.e mechanical lint 부재 invariant 위반. declaration-only retain.
- (D7-C) ADR-070 §결정 1 본문 amend (ADR-081 D7.c escape hatch 를 ADR-070 안 직접 codify) — ADR-070 본문 의미 변경 (D5 SSOT 보존 invariant 위반). cross-ref-only 채택.
- (D7-D) P0/P1/P2/P3 + P4 (5-tier) 확장 — codeforge ground-truth 4-tier (review-verdict-v4 + severity-propagation-v1 v1.0) 와 mismatch. 4-tier 유지 (contract surface 정합).

### 결과 (Amendment 2)

- Codex worker digest-parse self-verification step normative anchor — D7.a SSOT (ANCHOR-2 FP class directly 차단)
- quantitative P0/P1/P2/P3 grading rubric (4-tier criteria) — D7.b SSOT (D6.b 정량화)
- ground-truth divergence escape hatch ADR-070 cross-ref explicit — D7.c SSOT (declaration-only)
- disjoint axis preservation invariant (D6.d 재확인) — D7.d SSOT
- D1-D6 본문 의미 변경 0건 — §결정 D7 sub-section append only (Amendment 1 패턴 정합)
- `mechanical_enforcement_actions[]=[]` retain (declaration-only, §D5 + D6.e precedent)
- is_transitional false 유지 (permanent governance, ratchet 강화 only)

## 결과

- Codex worker spawn prompt 안 3 mandatory boilerplate 영역 (dogfood-out Story path / lane stage / sandbox boundary) normative anchor SSOT 신설 — D1 SSOT
- verify-before-trust scope 5 sub-scope (file / dir / cross-repo / grep count active vs historical / ADR §결정 번호) 분리 normative anchor — D2 SSOT
- 3-lane partition (Codex factual citation / DesignReview boundary completeness / CodeReview style + history) disjoint scope normative anchor — D3 SSOT
- ADR-052 / ADR-070 본문 정책 SSOT 보존 invariant (의미 변경 0건) — D4 SSOT
- evidence-enforceable framework entry append 면제 (declaration-only retain, ADR-070 §D5 precedent) — D5 SSOT
- ADR-052 Amendment 6 sub-section append (본 ADR 신규 영역 cross-ref 1 paragraph) — ADR-052 본문 patch (의미 변경 0)
- CLAUDE.md L170 blockquote cross-ref 1 줄 추가 (line-cap 320 invariant 정합)
- playbook §3.10 anchor 본문 cross-ref 1 줄 추가 (boilerplate SSOT anchor)
- ADR-RESERVATION row 81 append (active 직접, ADR-079/080 precedent 정합)

## 해소 기준

N/A — permanent policy (boilerplate composition + verify-before-trust scope + 3-lane partition = Codex worker 사용 영구 invariant, ADR-070 §D5 precedent 정합).

**ADR-058 §결정 1/2/3 정합**:

| 항목 | 값 |
|---|---|
| `is_transitional` (§결정 1) | `false` (permanent governance) |
| `## 해소 기준` 섹션 본문 (§결정 2) | `N/A — permanent strengthening (6-Story carry-over evidence ratchet 정합 — 1 baseline cluster CFP-770/771 paired + 5 consecutive fp-0 CFP-786/801/792/795/810; 6 units / 7 retro file)` |
| metric (§결정 3) | `codex_false_positive_tally` — Story §10 FIX Ledger row append count |
| who (§결정 3) | Orchestrator (verify-before-trust 단계 / ADR-070 D3 정합) — Story §10 FIX Ledger row append 주체 |
| how (§결정 3) | Story §10 FIX Ledger row 안 `[codex-false-positive]` sub-tag (fix-event-v1 MINOR bump 별 carrier) — `mcp__github__get_file_contents("internal-docs/wrapper/stories/CFP-NNN.md") + Grep "codex-false-positive"` |

ADR-058 §결정 5 (Amendment justification) 발효 영역 부재 — 본 ADR = 신규 ADR, Amendment 영역 아님. 향후 Amendment 시 §결정 5 정합 의무 (sunset_justification ratchet 강화 방향만 amendment 허용, ADR-064 §결정 7 top-down ratchet 정합).

영역 변경 시 (codex@openai-codex plugin sandbox 모델 변경 또는 codex CLI runtime working directory inject 추가) 본 ADR amendment 검토 영역.

## 관련 파일

- [`docs/adr/ADR-052-codex-proactive-check-touchpoints.md`](ADR-052-codex-proactive-check-touchpoints.md) — Amendment 6 sub-section append (cross-ref 1 paragraph)
- [`docs/adr/ADR-070-codex-verify-before-trust.md`](ADR-070-codex-verify-before-trust.md) — D1/D2/D5 cross-ref source
- [`docs/adr/ADR-058-adr-sunset-criteria-mandate.md`](ADR-058-adr-sunset-criteria-mandate.md) — §결정 1/2/3 frontmatter + 해소 기준 + 3-tuple 의무 source
- [`docs/adr/ADR-068-boundary-completeness-invariants.md`](ADR-068-boundary-completeness-invariants.md) — 3-lane partition 표 안 DesignReview 영역 (4 invariants + Amendment 1 I-5)
- [`docs/adr/ADR-073-orchestrator-verify-before-assert.md`](ADR-073-orchestrator-verify-before-assert.md) — verify-before-trust 자매 (Orchestrator self-assertion layer)
- [`docs/adr/ADR-045-story-retro-mandatory-trigger.md`](ADR-045-story-retro-mandatory-trigger.md) — §D-9 cross_story_pattern_adr_trigger forcing function (본 ADR 발의 trace)
- [`docs/orchestrator-playbook.md`](../orchestrator-playbook.md) — §3.10 dispatch prompt template SSOT (boilerplate cross-ref anchor)
- [`CLAUDE.md`](../../CLAUDE.md) — 오케스트레이션 규칙 § "Codex Proactive Check" blockquote SSOT (L170 cross-ref anchor)
- [`docs/adr/ADR-RESERVATION.md`](ADR-RESERVATION.md) — row 81 active 직접 등록
- [`docs/evidence-checks-registry.yaml`](../evidence-checks-registry.yaml) — declaration-only retain 정합 (entry append 면제)
