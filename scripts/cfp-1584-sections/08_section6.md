## 6. FIX 루프 상태 머신

### 6.1 카운터 SSOT = `docs/stories/<KEY>.md` §10 "FIX Ledger"

**GitHub 라벨은 대시보드용 보조 지표**. 카운터 판정·리셋 해석은 반드시 §10 기반.

```python
# 의사 코드
content = Read(f"docs/stories/{KEY}.md")
ledger = parse_section(content, "## 10. FIX Ledger")
rows = parse_ledger_rows(ledger)

# "현재 사이클" = 가장 최근 RESET 마커 이후 행들
for lane in ["설계-리뷰", "구현-리뷰", "구현-테스트", "보안-테스트"]:
    last_reset_idx = max(i for i, r in enumerate(rows) if r.reset == lane)
    current_cycle_count = sum(1 for r in rows[last_reset_idx+1:] if r.lane == lane)
```

§10 스키마·Orchestrator 갱신 절차: Orchestrator 단독 append-only 관리 (CFP-32 monopoly · fix-event-v1 contract).

§10에 새 행 commit 시 `fix-ledger-sync.yml` Action이 자동:
1. Story Issue에 `[FIX #N]` 코멘트 mirror
2. `fix:<레인>-retry` 라벨 자동 부착

### 6.1.1 Lighter mode — CI iteration 통계 가 §10 alternate evidence (CFP-92, P2-8)

mctrader debut audit Issue [#181](https://github.com/mclayer/plugin-codeforge/issues/181) P2-8 finding: §10 FIX Ledger 사용이 sparse — early Stories (MCT-1/2/3) 만, 최근 Stories (MCT-25 등) §10 부재. mctrader 실제 패턴 = `EPIC-RESULTS-<KEY>.md` §9 CI iteration 통계 가 §10 alternate 역할 (CI failure 별도 root cause 표).

본 lighter mode 정책:

- **§10 row append 의무 = lane verdict 기반 (review FIX / test FAIL)** — 변경 없음 (fix-event-v1 contract 유지)
- **CI failure (mechanical fix-up, push-fail-fix iteration)** = §10 row 의무 **없음** — EPIC-RESULTS §9 CI iteration 통계 표 가 evidence
- 즉 **review-verdict 기반 FIX (lane gate FAIL)** vs **CI iteration (mechanical push retry)** 가 분리된 추적 mechanism 보유
- PMOAgent 가 Story 완료 시 두 source 모두 evidence pack 으로 회고

**§10 vs §9 CI iteration 구분 표**:

| 발생 사건 | §10 row 의무 | EPIC-RESULTS §9 CI iteration |
|---|:-:|:-:|
| DesignReviewPL FIX verdict | ✅ | (Phase 1 PR 의 push retry 별도) |
| CodeReviewPL FIX verdict | ✅ | (Phase 2 PR 의 push retry 별도) |
| CI gate FAIL (구현 테스트 — ADR-048) | ✅ | — |
| SecurityTestPL FIX verdict (lanes.security_ai: true 시만) | ✅ | — |
| CI ruff / pyright / lint failure → push retry | ❌ | ✅ (PR # / pushes / failures / root cause 표) |
| Mechanical fix-up (typo / formatting / minor naming) | ❌ (CFP-19 R11 mechanical fast-path) | ✅ |

**효과**:
- Story §10 = "lane gate verdict" 의 audit trail 만 carry — high-signal
- EPIC-RESULTS §9 = "CI iteration mechanical retry" 의 audit trail — low-signal but completeness
- 기존 §10 의무 retain (CFP-32 contract 유지) — Implementation Story 의 review FIX 추적 source 동일

### 6.2 트리거 → 상태 전이

| 현재 phase | 트리거 | 전이 후 phase | §10 행 추가 | 라벨 동작 (자동) |
|-----------|--------|---------------|-------------|-----------|
| 설계-리뷰 | DesignReviewPL FIX | 설계 | Iter N / 설계-리뷰 / 원인=설계 / 재실행 범위 | `fix:설계-리뷰-retry` |
| 설계-리뷰 | DesignReviewPL PASS | 구현 | — | `gate:design-review-pass` 부착 + phase 라벨 변경 |
| 구현-리뷰 | CodeReviewPL FIX (원인=구현) | 구현 | Iter N / 구현-리뷰 / 원인=구현 / 재구현 | `fix:구현-리뷰-retry` |
| 구현-리뷰 | CodeReviewPL FIX (원인=설계) | 설계 (Phase 1 follow-up PR) | Iter N / 구현-리뷰 / 원인=설계 / Change Plan 갱신 | `fix:구현-리뷰-retry` (§10 행의 `lane` 컬럼 기준 — fix-ledger-sync.yml은 single-label 부착. 설계 회귀는 원인 판정 컬럼으로 식별, 이후 설계 리뷰 재실행 시 별도 §10 행 추가되어 `fix:설계-리뷰-retry` 라벨 자동 부착) |
| 구현-리뷰 | CodeReviewPL PASS | 구현-테스트 (CI gate) | — | (phase 전이만) |
| 구현-테스트 | CI gate FAIL (원인=구현) | 구현 | Iter N / 구현-테스트 / 원인=구현 / 재구현 + **RESET 구현-리뷰** | `fix:구현-테스트-retry` |
| 구현-테스트 | CI gate FAIL (원인=설계) | 설계 (Phase 1 follow-up PR) | Iter N / 구현-테스트 / 원인=설계 / Change Plan 갱신 + **RESET 구현-리뷰** | `fix:구현-테스트-retry` |
| 구현-테스트 | CI gate ALL PASS + lanes.security_ai: false | 완료 (merge gate) | — | (phase 전이만) |
| 구현-테스트 | CI gate ALL PASS + lanes.security_ai: true | 보안-테스트 | — | (phase 전이만) |
| 보안-테스트 | SecurityTestPL FIX (원인=구현) (lanes.security_ai: true 시만) | 구현 | Iter N / 보안-테스트 / 원인=구현 / 재구현 + **RESET 구현-리뷰** | `fix:보안-테스트-retry` |
| 보안-테스트 | SecurityTestPL FIX (원인=설계) (lanes.security_ai: true 시만) | 설계 (Phase 1 follow-up PR) | Iter N / 보안-테스트 / 원인=설계 / Change Plan 갱신 + **RESET 구현-리뷰** | `fix:보안-테스트-retry` |
| 보안-테스트 | SecurityTestPL PASS (lanes.security_ai: true 시만) | 완료 | — | `gate:security-test-pass` 부착 → Phase 2 PR mergeable → merge → Issue auto-close |

### 6.3 RESET 마커 규칙

- 구현 테스트 FAIL 또는 보안 테스트 FAIL → 구현 복귀 시 §10 마지막 행의 `RESET?` 컬럼에 `RESET 구현-리뷰` 기입
- 이후 구현 리뷰 카운터는 RESET 행 이후 iteration만 카운트 (이전 iteration은 감사 이력으로 유지)
- 설계 리뷰·구현 리뷰 내부 루프는 RESET 없음

### 6.4 Max FIX counter implementability reassessment (CFP-526 / ADR-067)

설계-리뷰 카운터 3/3 또는 구현-리뷰 카운터 3/3 도달 시, OR cross-lane cumulative_P0≥2 OR cumulative_P1≥5 OR reviewer_divergence_count≥2 (ADR-067 §결정 6 dual metric — MCT-150 §10 row 1-4 corroboration evidence) 시 ArchitectPL 재량 implementability reassessment 수행 의무.

**3 escalation trigger (i/ii/iii) 중 1+ 충족 시 사용자 escalation 의무** (ADR-067 §결정 3):

- (i) ESCALATE root cause = "design granularity inadequate"
- (ii) cross-module invariant 위반 without convergence path
- (iii) DeveloperPL ↔ ArchitectPL N+1 round divergence 유지

**0 충족 시 RESET path 선택 가능** (사용자 escalation 생략).

사용자 escalation 시 다음 Option A/B/C 표면 의무:

- **Option A**: RESET — design 또는 code 카운터 재시작
- **Option B**: 요건 자체 재정의 — Story 분할 또는 scope 축소
- **Option C**: Wave delegation — cross-Wave dependency 처리 후 본 Story 재진입

사용자 directive 2026-05-13 cross-ref: "타협이 어려웠던 부분을 기준으로 보수적으로 평가" — ArchitectPL reassessment 시 수렴 가능성 판단에 적용. SSOT: [ADR-067](../docs/adr/ADR-067-fix-ledger-implementability-escalation.md).

### 6.5 Cross-lane RESET 정책 (Pause-and-resume, CFP-526 / ADR-067)

각 lane별도 독립 카운터 (각 max=3):

- 설계-리뷰 카운터: 설계-리뷰 lane FIX iteration 전용
- 구현-리뷰 카운터: 구현-리뷰 lane FIX iteration 전용
- 보안-테스트 카운터: 무제한 (§6.7 fix-event-v1 schema 정합)

**cross-lane FIX 발생 시 합산 금지** (decision noise 회피):

- escalation lane (예: 보안-테스트) 에서 FIX 처리 시 design/code lane 카운터를 보존
- escalation lane FIX 완료 후 보존된 design/code lane 카운터 resume (Pause-and-resume)
- 사용자 directive Edge Case #2 처리 (Analyst): escalation 중 신규 lane (예: 보안-테스트) FIX 발생 시 design/code 카운터 보존 의무

SSOT: [ADR-067 §결정 4](../docs/adr/ADR-067-fix-ledger-implementability-escalation.md).

### 6.6 §10 FIX Ledger reasoning_carryover field (CFP-526 / ADR-067)

fix-event-v1 v1.2 (ADR-067 §결정 5) — §10 row 9번째 optional column. ArchitectPL re-spawn 시 직전 row의 reasoning_carryover full-text를 입력으로 전달 의무 (architectural amnesia 차단).

**3-part structured YAML schema**:

```yaml
reasoning_carryover:
  invariant_summary: "<50자 이내, immutable boundary 요약 — 변경 차단 영역>"
  disputed_claims: "<100자 이내, FIX iter 내 unresolved 영역 — 다음 cycle input>"
  transcript_ref: "<Story §9 anchor link — 예: #debate-transcript-F-001>"
```

**ArchitectPL re-spawn 절차**:

1. 직전 §10 row에서 reasoning_carryover 추출 (null 시 skip — 첫 iter 또는 미사용 iter)
2. ArchitectPL spawn 시 reasoning_carryover full-text를 spawn 입력에 포함
3. ArchitectPL이 reasoning_carryover 기반으로 설계 검토 (invariant_summary 영역 변경 차단 / disputed_claims 영역 집중 검토)

debate-protocol-v1 v1.1 의 debate_artifact_ref pattern과 직교 — debate 발동 여부와 무관하게 독립 적용. backward-compat: 기존 row null 또는 column 생략 모두 valid. SSOT: [fix-event-v1 v1.2](../docs/inter-plugin-contracts/fix-event-v1.md) + [ADR-067](../docs/adr/ADR-067-fix-ledger-implementability-escalation.md).

### 6.7 §10 관리 세부

- **Orchestrator가 단독 갱신** (CFP-32 ζ arc F1부터 — fix-event-v1 monopoly). append-only, 행 삭제·수정 금지
- Schema SSOT: [`docs/inter-plugin-contracts/fix-event-v1.md`](../docs/inter-plugin-contracts/fix-event-v1.md) — row 필드 + append 규칙 + RESET 시맨틱스. **현재 schema = v1.3 (CFP-842 — depth-aware scope optional fields, 11 column)**.
- Stale-read 방지: Orchestrator가 Edit 직전 `git pull --rebase` 또는 file mtime 비교 후 append. 충돌 시 fail-fast + 사용자 ESCALATE (자동 재시도 금지 — append-only ledger 손상 위험)
- Lane plugin은 FIX event를 Orchestrator에 verdict로 보고 (status=FIX 또는 test FAIL). lane plugin이 §10 직접 Edit 금지 — CFP-34 deliverable `story-section-write-guard.yml`이 enforce
- §10 조회 실패(파일 부재 등) → ArchitectPLAgent 판정 정지 → 사용자 판단 요청
- GitHub 라벨은 `fix-ledger-sync.yml` Action이 §10 commit 감지 시 자동 부착 — 단방향 mirror (§10 → label/comment). 대시보드 search syntax 필터용

**v1.3 depth-aware scope 필드 의무 (CFP-842, broken-link/path 정정 FIX 한정)**:

`affected_paths_with_depth` 필드는 broken-link / path 정정 FIX (cross-module relative path adjust / doc-location-registry move / link target 갱신 등) 시 **의무**. 그 외 FIX (logic bug / API change / perf regression / wording desync 등) = optional. 누락 시 `fix-event-depth-scope-presence` warning-tier lint (advisory only, blocking-on-pr 미승격) 적발.

기록 형식:
```yaml
affected_paths_with_depth:
  - {path: "docs/adr/ADR-067.md", depth: 2}
  - {path: "templates/github-workflows/fix-ledger-sync.yml", depth: 2}
  - {path: "CLAUDE.md", depth: 0}
```

`depth` = repo root 기준 dir depth (root level file = 0, depth 1 dir 안 file = 1, ...). 정정 규칙 적용 범위 (예: `depth >= 2 then path adjust = '../../'`) 의 mechanical reasoning trace 보존 — CFP-770 §8 CR-005→CR-006→CR-007 over-correction regression chain lesson directly 차단 carrier. broken-link/path FIX 시 depth 정보 부재가 directly carrier 였음.

`affected_scope` 필드 (enum: single-file / cross-module / cross-repo / cross-plugin) 는 broken-link/path FIX 영역과 무관하게 **모든 FIX** 에서 optional — RESET 범위 결정 input. cross-module / cross-repo / cross-plugin scope = ArchitectPL 가 cross-lane RESET 적극 검토 (ADR-067 §결정 4 Amendment 1). single-file scope = 동일 lane FIX iter 유지 (RESET 회피).

### 6.8 원인 판정 decision table

[CLAUDE.md](../CLAUDE.md) "원인 판정 decision table" 섹션이 SSOT — 본 playbook은 표를 inline 복제하지 않는다 (drift 방지). Orchestrator는 FIX 트리거 시 CLAUDE.md 표를 직접 참조해 DeveloperPL/ArchitectPLAgent 전달용 evidence pack을 구성.

**ArchitectPLAgent 최종 판정 + evidence pack(Change Plan 버전 + 리뷰 findings + 테스트 로그) 첨부 의무**.

#### 6.8.1 Mechanical reconciliation pattern — grep BEFORE sed (CFP-464, CFP-500 FIX-2/3 학습)

ArchitectPL re-spawn FIX 처리 시 reconciliation 의무 4-step (partial reconciliation anti-pattern 차단):

1. **COMPREHENSIVE grep BEFORE sed** — target keyword/pattern 양 worktree 전수 검색 (file scope full, not just self-report)
2. **Report grep results** — 발견된 모든 occurrence enumerate 보고 후 처리 결정 (partial 적용 금지)
3. **sed applied** — 발견된 모든 occurrence 정정 (audit trail 예외 명시)
4. **Re-grep verify** — sed 후 잔존 0건 확인 (audit trail 제외)

evidence: CFP-500 설계 lane FIX iter 2/3 partial reconciliation (self-report 영역만 정정, sweep 누락 → recurrence). Iter 4 grep sweep mandate 후 단번에 해소.

본 단계는 codeforge-design plugin ArchitectPLAgent template 의 mechanical reconciliation 영역으로 본 playbook §6.8 의 augmentation. cross-plugin enforcement 자체는 별도 follow-up (codeforge-design plugin version bump 동반).

### 6.9 Parallel diagnosis (R4, [CFP-19 spec](https://github.com/mclayer/codeforge-internal-docs/blob/main/wrapper/specs/2026-04-27-cfp-19-orchestration-parallelization.md))

review·테스트 FIX (구현 리뷰·구현 테스트·보안 테스트) 시 DeveloperPL 1차 진단과 ArchitectPL 최종 판정을 **병렬 spawn**한다 (한 메시지에 dispatch).

**절차**:
1. Orchestrator가 FIX verdict 수령
2. 한 메시지에 두 에이전트 동시 spawn:
   - DeveloperPL: 1차 원인 진단 (구현 / 설계) — 결과 typed return (CFP-32부터 §10 직접 write 안 함, Orchestrator가 받아서 §10 append)
   - ArchitectPL: 최종 판정 — review findings + Change Plan + ADR 정합성 평가 (DeveloperPL 결과 미수신, 독립 판단)
3. 두 결과 수령 후 비교:
   - **일치 (양쪽 동일 원인)**: 해당 원인 그대로 진행 (구현 commit append 또는 Change Plan 갱신)
   - **불일치**: ArchitectPL verdict 우선 (chief judge 책무 보존). DeveloperPL 진단을 §10 row 비고에 archive

**낙관적 가속 가정**: 80% 케이스 일치 → 직렬 5-10분을 병렬 2-3분으로 단축. 20% 불일치 시 ArchitectPL 우선이라 retry overhead 없음.

**제약**: 설계 리뷰 FIX는 본 절 범위 외 — DeveloperPL 미개입 (기존 절차: ArchitectPL 직접 회귀).

### 6.10 Mechanical fast-path (R11, [CFP-19 spec](https://github.com/mclayer/codeforge-internal-docs/blob/main/wrapper/specs/2026-04-27-cfp-19-orchestration-parallelization.md))

ReviewPL verdict packet의 `mechanical_category` 필드 (typo / broken-link / minor-naming / comment-only / none — SSOT codeforge-review repo의 `templates/review-pl-base.md` §3 R11 절) + severity 조합으로 fast-path 자격 판정:

**자격 조건**: `mechanical_category != none` AND (severity = P2 OR (severity = P1 AND 영향 파일 수 = 1))

**자격 충족 시 절차**:
1. Orchestrator가 §6.6 parallel diagnosis 건너뛰고 DeveloperPL 직접 spawn (fix-only 모드)
2. DeveloperPL이 fix commit
3. **same-iteration internal verify** — 다음 review iteration이 동일 finding 검출 안 하면 PASS, 검출 시 Iter row append (정상 cycle 회복)
4. §10 ledger 신규 row 안 매김 (fast-path는 카운터 증가 안 함)

**자격 미충족 또는 분류 잘못**: 다음 review iteration이 P0/P1 검출 → 정상 §6.6 cycle.

**제약**: 보안 lane의 injection / credential / CVE / trust-boundary 카테고리는 항상 `mechanical_category = none`이라 fast-path 자격 없음 (codeforge-review repo의 `templates/review-pl-base.md` §3 R11 SSOT).

### 6.11 Spec amendment loop (CFP-87)

mctrader debut audit Issue [#181](https://github.com/mclayer/plugin-codeforge/issues/181) P1-7 finding (Opus 자체 발견): mctrader-hub PR [#72](https://github.com/mclayer/mctrader-hub/pull/72) (`[MCT-50/51] Spec amendments — Codex push-back 6건`) — Phase 3 implementation 진행 중 Codex review 가 발견한 push-back 6건 → spec doc 수정 PR (Story file `MCT-50.md` + `MCT-51.md` amendment) 으로 캡처 후 implementation 재개. 매우 가치 있는 패턴이나 codeforge SSOT 미정의 — 본 §6.8 codify.

#### 6.11.1 Trigger

다음 중 하나 발생 시 Spec amendment loop 진입 (FIX 루프 §6.1-§6.7 와 별도):

- **Codex push-back during implementation**: Phase N implementation (Phase 2~N PR 작업) 중 Codex review 또는 자율 검토 시 spec gap 발견 (Story file §1-§7 unspecified / inconsistent)
- **사용자 mid-implementation requirement clarification**: 구현 중 사용자가 새 AC 제시 또는 기존 §1 의미 재해석
- **Spec drift 발견**: implementation 진행 중 §7 설계 결정과 코드 사이 drift 발견 (코드 측 fix 만으로 해결 안 되는 경우)

§6.1-§6.7 FIX 루프 와 구분:
- FIX 루프 = review verdict FAIL → 코드 / 설계 변경
- Spec amendment = review verdict 무관 → spec doc (Story file / Change Plan / ADR) 변경

#### 6.11.2 Output

`[<KEY>] Spec amendment — <reason>` PR (1+ Story file edit, doc-only):

- Story file §1-§7 / §11 / §13 amendment 시 PR title prefix `[<KEY>] Spec amendment`
- amendment 동반 의무:
  - Story file frontmatter `status:` field 유지 (현재 phase 변경 없음 — amendment 는 phase progression 아님)
  - Story file §10 FIX Ledger row 추가 = N/A (FIX 가 아니므로)
  - Story file §12 Sonnet Decision Log row 추가 (substantive choice 발생 시)
  - PR labels = `audit:spec-amendment` + `phase:<현재 phase>` (CFP-86 label registry 확장 candidate)

#### 6.11.3 Limit

per Story max **2 spec amendment PR**. 3+ amendment 발생 시 = 설계 결함 신호 → 설계 lane 재실행 trigger (§6.5 decision table 의 "설계 원인 판정" 적용).

#### 6.11.4 Audit trail

- Story file §11 = amendment PR list (link + reason summary)
- EPIC-RESULTS-<EPIC_KEY>.md §6 Codex review aggregate = amendment 발생 row 명시 (PR # + reason)

#### 6.11.5 mctrader 사례 (CFP-87 source)

| Story | Amendment PR | Reason | Trigger |
|---|---|---|---|
| MCT-50 / MCT-51 | mctrader-hub#72 | Codex push-back 6건 (Signal handler ownership / RunStatus minimal v1 / HTTP edge case / "11 tables" 재정의 / MarketDataFreshnessEvent deferred / ClosedBarEvent.source_hash) | Phase 3 implementation 중 Codex review |

#### 6.11.6 §6.11 ↔ §6.8 (원인 판정 decision table) cross-ref

§6.11 spec amendment 가 결과적으로 spec drift 가 코드 / 설계 사이 발생 시 → §6.8 decision table 의 "설계 원인 판정" 적용 → 설계 lane 재실행. 즉 spec amendment → FIX 루프 conversion path 존재.

---

