# CFP-19 Orchestration Parallelization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Story 1건 처리시간 60-90분 → 30-40% 단축. Tier 1+2 (R1-R11) 11개 병렬화 개선을 ADR 변경 없이(non-BREAKING) SSOT 문서·에이전트 md·playbook에 적용.

**Architecture:** 본 plugin은 코드 산출이 아닌 **에이전트 오케스트레이션 SSOT 문서**. 변경 단위는 markdown 파일 edit. "테스트"는 (1) `templates/`·`agents/`·`docs/` 간 SSOT cross-ref grep parity, (2) invariant-check.yml 워크플로우 (Step 1-8), (3) markdown link 검증. 6 그룹 × 13 태스크로 분해. Group A (review-pl-base SSOT 우선) → B (DocsAgent helper) → C (playbook) → D (PL md) → E (TestAgent) → F (CLAUDE.md + gitignore + 종합 검증).

**Tech Stack:** Markdown (SSOT 문서) · YAML frontmatter · GitHub Actions (invariant-check.yml 기존) · ripgrep (grep 검증) · git (commit 단위 의무)

**파일 책임 매핑** (Group → File → 담당 R):
- **Group A**: `templates/review-pl-base.md` (R2/R3/R11) → `agents/{DesignReviewPLAgent,CodeReviewPLAgent,SecurityTestPLAgent}.md` (참조 갱신)
- **Group B**: `agents/DocsAgent.md` (R1 §11/queue + R5 §8.5 helper + R10 security-prefetch)
- **Group C**: `docs/orchestrator-playbook.md` (R1 §11 / R3·R7·R9·R10 §3 / R4·R11 §6 / R6 §12)
- **Group D**: `agents/ArchitectPLAgent.md` (R4 + R8) · `agents/DeveloperPLAgent.md` (R4 + R5 + R11)
- **Group E**: `agents/TestAgent.md` (R9 subset arg)
- **Group F**: `CLAUDE.md` 스폰 시퀀스 + `.gitignore` + 최종 invariant-check 통과 확인

**Self-application paradox 처리**: 본 CFP는 자기 적용 안 함 — 변경된 병렬화 규칙은 **다음 Story부터** 발효. Tier 1+2 변경 자체는 기존 직렬 프로세스로 진행 (CFP-17/18 paradox 처리 패턴 동일, ADR-005 plugin-meta-na 적용).

**Story 작성 의무 처리**: 본 변경은 SSOT 문서(playbook/CLAUDE.md/agents) 의미 변경 → **Story 작성 의무 강제 대상**. KEY=`CFP-19` (PR body는 `Closes #<issue>` keyword 사용). §8 Test Contract / §9 리뷰 결과는 plugin-meta-na 패턴으로 N/A 처리 가능.

---

## Task A1: review-pl-base.md — verdict-first + R3 spawn + R11 fast-path

**Files:**
- Modify: `templates/review-pl-base.md` (현재 196줄)

**범위 — 3 변경**:
1. §1 "공통 포지션" 호출 시점 표현 정확화 (R3): "PL이 워커 packet 작성 후 **Orchestrator에 packet return → Orchestrator가 두 워커 한 message에 병렬 spawn**" 명시 (현재 "PL이 워커 packet 작성 후 Orchestrator에 'Claude/Codex 워커 병렬 스폰' 의뢰" 모호 → crisp)
2. §3 "Severity 종합 규칙"에 R11 mechanical fast-path 자격 분류 절 추가
3. §5 "보고 형식"에 verdict-return-first 절 추가 (R2)

- [ ] **Step 1: Read current §1 "공통 포지션"**

```bash
sed -n '7,17p' /Users/1111971/workspace/mctrader/plugins/codeforge/templates/review-pl-base.md
```

Expected: line 11-14 호출 시점 절 출력.

- [ ] **Step 2: Edit §1 line 13 호출 시점 표현 명료화 (R3)**

old_string (정확히 일치):
```
- **호출 시점**: 각 레인 진입 직후 Orchestrator 스폰. PL이 워커 packet 작성 후 Orchestrator에 "Claude/Codex 워커 병렬 스폰" 의뢰
```

new_string:
```
- **호출 시점**: 각 레인 진입 직후 Orchestrator 스폰. PL은 워커 packet만 작성·검증해 Orchestrator에 return — **워커 spawn은 Orchestrator가 한 메시지에 두 워커(Claude ∥ Codex)를 dispatch** (서브에이전트 재귀 spawn 금지 platform 제약 정합, [CFP-19 R3](../docs/superpowers/specs/2026-04-27-cfp-19-orchestration-parallelization.md))
```

- [ ] **Step 3: Edit §3 "종합 판정" 표 아래에 R11 fast-path 절 추가**

old_string (§3 종합 판정 표 다음 빈 행 + Noise 분류 섹션 앞):
```
| FIX 카운터 한도 초과 | **ESCALATE** (한도는 lane-specific) |

### Noise 분류
```

new_string:
```
| FIX 카운터 한도 초과 | **ESCALATE** (한도는 lane-specific) |

### Mechanical fast-path 분류 (R11)

PL이 verdict packet에 **`mechanical_category`** 필드를 추가해 다음 자격을 1차 분류한다. Orchestrator가 fast-path 적용 여부 최종 판정.

| `mechanical_category` 후보 | 자격 조건 |
|---------|----------|
| `typo` | 단일 파일 typo·문법 수정 |
| `broken-link` | markdown link 1건 깨짐 (path/anchor) |
| `minor-naming` | 단일 함수/변수 rename, 의미 보존 |
| `comment-only` | 코멘트·docstring 수정만 |
| `none` | 위 4종 미해당 (정상 cycle) |

**Fast-path 자격 = `mechanical_category != none` AND (severity = P2 OR (severity = P1 AND 파일 수 = 1))**.

자격 충족 시 Orchestrator는 DeveloperPL 1차 진단 → ArchitectPL 판정 cycle을 skip하고 직접 fix commit + same-iteration internal verify (다음 Iter 행 안 매김). 분류 잘못이면 다음 review iteration이 P0/P1 발견 → 정상 cycle 회복 (Iter 행 append).

분류 책임자: 각 ReviewPL이 verdict 산출 시 1차 분류. SSOT는 본 절. 각 lane checklist md (`templates/review-checklists/{design,code,security}.md`)는 본 절 참조만 (재정의 금지).

### Noise 분류
```

- [ ] **Step 4: Edit §5 "보고 형식"에 verdict-return-first 절 추가 (R2)**

old_string (§5 헤더 다음 첫 줄):
```
## 5. 보고 형식

### PASS
```

new_string:
```
## 5. 보고 형식

### Verdict-return 우선 원칙 (R2)

PL은 severity 종합 후 **즉시 Orchestrator에 verdict return** (PASS / FIX / ESCALATE 결정). DocsAgent를 통한 영속 기록(GitHub Issue 코멘트·Story file §9)은 **Orchestrator가 다음 lane spawn을 트리거한 직후 background drain**으로 처리.

- ✅ 허용: PL → Orchestrator (verdict) → Orchestrator → 다음 lane spawn ∥ DocsAgent (background, mode: background)
- ❌ 금지: PL이 DocsAgent save 완료 대기 후 verdict return — save가 다음 lane 게이트가 되면 안 됨

이 분기는 평균 1-2분 단축 ([CFP-19 R2](../docs/superpowers/specs/2026-04-27-cfp-19-orchestration-parallelization.md)).

### PASS
```

- [ ] **Step 5: Verify changes**

```bash
grep -n "Orchestrator가 한 메시지에 두 워커" /Users/1111971/workspace/mctrader/plugins/codeforge/templates/review-pl-base.md
grep -n "Mechanical fast-path 분류" /Users/1111971/workspace/mctrader/plugins/codeforge/templates/review-pl-base.md
grep -n "Verdict-return 우선 원칙" /Users/1111971/workspace/mctrader/plugins/codeforge/templates/review-pl-base.md
```

Expected: 3 라인 각 1회 매칭 (각 변경 1건).

- [ ] **Step 6: Commit**

```bash
git -C /Users/1111971/workspace/mctrader/plugins/codeforge add templates/review-pl-base.md
git -C /Users/1111971/workspace/mctrader/plugins/codeforge commit -m "$(cat <<'EOF'
feat(cfp-19): review-pl-base SSOT — verdict-first + Orchestrator-direct dual spawn + mechanical fast-path

- §1 호출 시점 명료화 (R3): PL이 packet return → Orchestrator가 한 메시지에 두 워커 dispatch (서브에이전트 재귀 spawn 금지 정합)
- §3 mechanical fast-path 분류 절 추가 (R11): typo/broken-link/minor-naming/comment-only 자격 + Orchestrator skip 조건
- §5 verdict-return 우선 원칙 추가 (R2): PL save 대기 안 함, 다음 lane spawn 트리거 후 background drain

Story: CFP-19 Tier 1+2 R1-R11 병렬화 개선 (1/13)
EOF
)"
```

---

## Task A2: 3 ReviewPL md — review-pl-base 참조 갱신 (R2/R3/R11)

**Files:**
- Modify: `agents/DesignReviewPLAgent.md`
- Modify: `agents/CodeReviewPLAgent.md`
- Modify: `agents/SecurityTestPLAgent.md`

각 ReviewPL md 본문에서 "워커 spawn" / "verdict 후 save" 관련 표현이 R2/R3와 충돌하는지 점검 + R11 mechanical_category 분류 책임 1줄 추가.

- [ ] **Step 1: 3 ReviewPL md에서 spawn 관련 표현 grep**

```bash
cd /Users/1111971/workspace/mctrader/plugins/codeforge && \
grep -nH "워커.*스폰\|Claude.*Codex.*병렬\|병렬.*Claude" agents/DesignReviewPLAgent.md agents/CodeReviewPLAgent.md agents/SecurityTestPLAgent.md
```

Expected: 각 PL에서 spawn 관련 행 다수 출력. 검토 후 review-pl-base SSOT 참조로 충분한지 판단.

- [ ] **Step 2: Read DesignReviewPLAgent.md 전체 + 해당 행 위치 확정**

```bash
sed -n '1,80p' /Users/1111971/workspace/mctrader/plugins/codeforge/agents/DesignReviewPLAgent.md
```

검토: spawn 관련 행이 SSOT(`templates/review-pl-base.md` §1) 참조만 하면 OK. 자체 detail 있을 시 SSOT 참조로 축소.

- [ ] **Step 3: 본 단계는 DesignReviewPLAgent · CodeReviewPLAgent · SecurityTestPLAgent 3개 파일을 동일 패턴으로 처리**

각 파일에서 다음 패턴 변경:
1. spawn 관련 자체 detail이 있다면 → "공통 절차는 [`templates/review-pl-base.md`](../templates/review-pl-base.md) §1 SSOT 참조" 1줄로 압축
2. mechanical_category 분류 책임 1줄 추가:
   - DesignReview: "FIX verdict 시 `mechanical_category` 분류 의무 (typo / broken-link / minor-naming / comment-only / none) — SSOT [`templates/review-pl-base.md`](../templates/review-pl-base.md) §3"
   - CodeReview: 동일
   - SecurityTest: 동일 + "단 보안 카테고리(injection/credential)는 항상 `none`으로 분류"

- [ ] **Step 4: DesignReviewPLAgent.md edit — mechanical_category 추가**

DesignReviewPLAgent.md의 §"FIX 루프" 또는 §"보고 형식" 절 중 verdict 관련 위치에서:

old_string (실제 grep 결과로 확인 후 정확 매칭):
```
- 공통 severity 종합 규칙은 [`templates/review-pl-base.md`](../templates/review-pl-base.md) §3 SSOT 참조
```

new_string:
```
- 공통 severity 종합 규칙은 [`templates/review-pl-base.md`](../templates/review-pl-base.md) §3 SSOT 참조
- FIX verdict 시 `mechanical_category` 1차 분류 의무 (typo / broken-link / minor-naming / comment-only / none) — fast-path 자격 분류 SSOT [`templates/review-pl-base.md`](../templates/review-pl-base.md) §3 (R11, [CFP-19 spec](../docs/superpowers/specs/2026-04-27-cfp-19-orchestration-parallelization.md))
```

만약 위 old_string이 정확히 매칭 안 되면, 실제 grep 결과로 가까운 anchor를 사용하고 SSOT 참조 + mechanical_category 추가를 수행.

- [ ] **Step 5: CodeReviewPLAgent.md edit — 같은 패턴**

(DesignReviewPLAgent.md와 동일한 패턴 적용 — 본 단계는 별도 commit이 아닌 같은 commit에 묶음)

- [ ] **Step 6: SecurityTestPLAgent.md edit — 같은 패턴 + 보안 카테고리 예외**

old_string anchor 동일하게 SSOT 참조 행을 찾아 → 다음 행 추가:

new_string suffix:
```
- FIX verdict 시 `mechanical_category` 1차 분류 의무 (typo / broken-link / minor-naming / comment-only / none) — **단 injection · credential · CVE · trust-boundary 카테고리는 항상 `none`** (코드 의미 변경 동반). SSOT [`templates/review-pl-base.md`](../templates/review-pl-base.md) §3 (R11)
```

- [ ] **Step 7: Verify 3 PL md mechanical_category 추가 확인**

```bash
cd /Users/1111971/workspace/mctrader/plugins/codeforge && \
grep -l "mechanical_category" agents/DesignReviewPLAgent.md agents/CodeReviewPLAgent.md agents/SecurityTestPLAgent.md
```

Expected: 3 파일 모두 출력.

- [ ] **Step 8: Commit**

```bash
git -C /Users/1111971/workspace/mctrader/plugins/codeforge add agents/DesignReviewPLAgent.md agents/CodeReviewPLAgent.md agents/SecurityTestPLAgent.md
git -C /Users/1111971/workspace/mctrader/plugins/codeforge commit -m "$(cat <<'EOF'
feat(cfp-19): 3 ReviewPL md — mechanical_category 1차 분류 책임 명문화 (R11)

- DesignReviewPL/CodeReviewPL: SSOT 참조 + mechanical_category 분류 의무
- SecurityTestPL: 동일 + injection/credential/CVE/trust-boundary 카테고리는 항상 none 예외

Story: CFP-19 Tier 1+2 R1-R11 병렬화 개선 (2/13)
EOF
)"
```

---

## Task B1: DocsAgent §11 dual-mode write queue (R1)

**Files:**
- Modify: `agents/DocsAgent.md`
- Modify: `docs/orchestrator-playbook.md` §11.2 frontmatter 스키마 (Group C에서 처리)

DocsAgent.md에 dual-mode (blocking / background) drain 정책 명시. 의뢰자 측 mode 라벨 의무는 playbook §11.2 frontmatter (Group C에서 처리).

- [ ] **Step 1: Read DocsAgent.md §"DocsAgent 작업 요청 인터페이스" 섹션 (라인 291-)**

```bash
sed -n '291,388p' /Users/1111971/workspace/mctrader/plugins/codeforge/agents/DocsAgent.md
```

- [ ] **Step 2: Edit DocsAgent.md — §"DocsAgent 작업 요청 인터페이스" 헤더 직후 dual-mode 절 추가**

old_string (정확 매칭):
```
## DocsAgent 작업 요청 인터페이스

다른 에이전트가 Orchestrator 경유로 DocsAgent에 요청할 때 사용하는 요청 템플릿:
```

new_string:
```
## DocsAgent 작업 요청 인터페이스

다른 에이전트가 Orchestrator 경유로 DocsAgent에 요청할 때 사용하는 요청 템플릿:

### Drain 모드 (R1, [CFP-19 spec](../docs/superpowers/specs/2026-04-27-cfp-19-orchestration-parallelization.md))

모든 요청 frontmatter에 `mode` 필드 필수 (write queue 파일 frontmatter SSOT는 [`docs/orchestrator-playbook.md`](../docs/orchestrator-playbook.md) §11.2):

| mode | 의미 | drain 시점 |
|------|------|----------|
| **`blocking`** | 다음 lane이 의존하는 산출물 | 현재 lane 종료 직전 (다음 lane spawn 전 반드시 drain 완료) |
| **`background`** | 누적 보고·코멘트·monitoring | 다음 lane spawn 후 별도 DocsAgent run으로 drain |

**blocking 분류 의무 항목**:
- §1-7 (Phase 1 PR open 직전)
- Change Plan `docs/change-plans/<slug>.md` 신규/갱신
- ADR draft `docs/adr/ADR-NNN-<slug>.md` 신규
- §8.5 Impl Manifest commit (sub-issue Action 트리거)
- gate label 부착 (`gate:design-review-pass` / `gate:security-test-pass`)
- §10 FIX Ledger Iter row append (다음 FIX 회귀 이전)
- Phase 1·2 PR create

**background 분류 허용 항목**:
- 에이전트 산출물 요약 Issue 코멘트 (`[<phase>] <Agent>: <요약>`)
- §9.x 리뷰·테스트 결과 누적 append
- §11 회고 append
- ledger-append 후속 mirror (단 §10 본문 append 자체는 blocking)

**의뢰자 측 책임**: write queue 파일 작성 시 frontmatter `mode: blocking | background` 명시 의무. 누락 시 DocsAgent가 `mode: blocking` fallback (안전 측). 라벨 잘못이면 후속 lane 진입 지연 발생 → 점진 교정.

**DocsAgent 측 drain 우선순위**:
1. `priority: high` AND `mode: blocking`
2. `priority: normal` AND `mode: blocking`
3. `priority: high` AND `mode: background`
4. `priority: normal` AND `mode: background`

같은 클래스 내 seq 순.
```

- [ ] **Step 3: Verify DocsAgent.md dual-mode 절 추가**

```bash
grep -n "Drain 모드 (R1" /Users/1111971/workspace/mctrader/plugins/codeforge/agents/DocsAgent.md
grep -n "blocking 분류 의무 항목" /Users/1111971/workspace/mctrader/plugins/codeforge/agents/DocsAgent.md
```

Expected: 2 라인 각 1회 매칭.

- [ ] **Step 4: Commit (Group B는 task 단위 분할 — 이 commit은 R1 한정)**

```bash
git -C /Users/1111971/workspace/mctrader/plugins/codeforge add agents/DocsAgent.md
git -C /Users/1111971/workspace/mctrader/plugins/codeforge commit -m "$(cat <<'EOF'
feat(cfp-19): DocsAgent §"작업 요청 인터페이스" — dual-mode (blocking/background) drain 정책 (R1)

- mode 필드 필수 (write queue 파일 frontmatter)
- blocking 분류 의무 7종 명시 (PR open, Change Plan, ADR, §8.5, gate label, §10, PR create)
- background 분류 허용 4종 명시 (코멘트, §9.x, §11, ledger mirror)
- drain 우선순위 4단계 (priority × mode)
- 누락 시 blocking fallback (안전 측)

Story: CFP-19 Tier 1+2 R1-R11 병렬화 개선 (3/13)
EOF
)"
```

---

## Task B2: DocsAgent §8.5 impl-manifest helper (R5)

**Files:**
- Modify: `agents/DocsAgent.md` §8 §8.5 절

§8.5 manifest 표를 DeveloperPL이 수동 타이핑하던 작업을 DocsAgent helper로 이관. DeveloperPL은 review-only.

- [ ] **Step 1: Read DocsAgent.md §8 (라인 222-235)**

```bash
sed -n '218,240p' /Users/1111971/workspace/mctrader/plugins/codeforge/agents/DocsAgent.md
```

- [ ] **Step 2: Edit DocsAgent.md §8 끝에 R5 helper 절 추가**

old_string (정확 매칭):
```
DocsAgent는 sub-issue write 권한을 fallback (`mcp__github__sub_issue_write`)으로만 사용. Action 실패 시 수동 처리.

### 9. §10 "FIX Ledger" SSOT 스키마
```

new_string:
```
DocsAgent는 sub-issue write 권한을 fallback (`mcp__github__sub_issue_write`)으로만 사용. Action 실패 시 수동 처리.

### 8.1 Impl Manifest 자동 생성 helper (R5, [CFP-19 spec](../docs/superpowers/specs/2026-04-27-cfp-19-orchestration-parallelization.md))

DeveloperPL이 수동 타이핑하던 §8.5 매핑표를 DocsAgent가 git diff에서 자동 생성. DeveloperPL은 review·승인만.

**의뢰 형식 (write queue type=story-section)**:

```yaml
---
type: story-section
story: <KEY>
section: "8.5"
mode: blocking
kind: impl-manifest          # 신규 — kind hint
requester: DeveloperPLAgent
issued_at: <ISO 8601>
priority: normal
---
[Args]
commit_range: <base_sha>..<head_sha>          # 필수 — Phase 2 첫 commit ~ 현재 HEAD
change_plan_path: docs/change-plans/<slug>.md  # 필수 — §5 변경 계획 cross-ref용
```

**DocsAgent 측 처리**:
1. `Bash(git diff --name-status <base_sha>..<head_sha>)` — A/M/D 레이블 + 파일 목록
2. `Read(change_plan_path)` §5 변경 계획 fetch
3. 각 파일별 `agent_role` 추론 규칙:
   - `tests/**` → `QADeveloperAgent` (`role: qa`)
   - `src/**` → `DeveloperAgent` (`role: dev`) — overlay roster에 다른 dev 있으면 path glob 매칭
   - `docs/**` → `DocsAgent`
   - `deploy/**` · `.github/workflows/**` → `InfraEngineerAgent` (`role: dev:infra`)
   - `data/**` · `migrations/**` → `DataEngineerAgent` (`role: dev:data`)
4. §5 변경 계획에서 해당 파일 언급 절을 `related_change_plan_section`으로 매핑
5. §8.5 표 생성 후 Story file edit
6. DeveloperPL에 review 요청 코멘트 (background mode)

**§8.5 표 컬럼** (테이블 schema는 [`templates/impl-manifest.md`](../templates/impl-manifest.md) SSOT):
| change | path | agent_role | related_change_plan_section | description |

`change` 컬럼 = `A` (added) / `M` (modified) / `D` (deleted). DeveloperPL이 description 컬럼을 review-edit.

**Fallback**: helper 실패 시 (git diff 파싱 오류 등) DeveloperPL이 수동 작성 (기존 절차).

### 9. §10 "FIX Ledger" SSOT 스키마
```

- [ ] **Step 3: Verify §8.1 추가**

```bash
grep -n "8.1 Impl Manifest 자동 생성 helper" /Users/1111971/workspace/mctrader/plugins/codeforge/agents/DocsAgent.md
grep -n "kind: impl-manifest" /Users/1111971/workspace/mctrader/plugins/codeforge/agents/DocsAgent.md
```

Expected: 각 1회 매칭.

- [ ] **Step 4: Commit**

```bash
git -C /Users/1111971/workspace/mctrader/plugins/codeforge add agents/DocsAgent.md
git -C /Users/1111971/workspace/mctrader/plugins/codeforge commit -m "$(cat <<'EOF'
feat(cfp-19): DocsAgent §8.1 Impl Manifest 자동 생성 helper (R5)

- write queue kind=impl-manifest 신규 (commit_range + change_plan_path args)
- git diff --name-status A/M/D 자동 감지
- agent_role 추론 규칙 5종 (tests/src/docs/deploy/data path glob)
- §5 변경 계획 cross-ref 자동 매핑
- DeveloperPL은 review-edit만 — 수동 타이핑 deprecated

Story: CFP-19 Tier 1+2 R1-R11 병렬화 개선 (4/13)
EOF
)"
```

---

## Task B3: DocsAgent security-prefetch helper (R10)

**Files:**
- Modify: `agents/DocsAgent.md` (§8.1 다음에 §8.2 추가)
- Modify: `agents/DocsAgent.md` Bash 권한 frontmatter (security-prefetch 호출 fallback)

- [ ] **Step 1: Read DocsAgent.md frontmatter 권한 부분**

```bash
sed -n '1,72p' /Users/1111971/workspace/mctrader/plugins/codeforge/agents/DocsAgent.md
```

frontmatter `tools:` 또는 `Bash(...)` 권한 행 위치 확인.

- [ ] **Step 2: Add §8.2 security-prefetch helper 절**

§8.1 Impl Manifest helper 직후에 §8.2 추가:

old_string (Task B2의 §8.1 끝 + §9 헤더 anchor):
```
**Fallback**: helper 실패 시 (git diff 파싱 오류 등) DeveloperPL이 수동 작성 (기존 절차).

### 9. §10 "FIX Ledger" SSOT 스키마
```

new_string:
```
**Fallback**: helper 실패 시 (git diff 파싱 오류 등) DeveloperPL이 수동 작성 (기존 절차).

### 8.2 Security 1차 layer pre-fetch helper (R10, [CFP-19 spec](../docs/superpowers/specs/2026-04-27-cfp-19-orchestration-parallelization.md))

SecurityTestPL spawn 시 1차 layer (Dependabot/CodeQL/Secret Scanning/Push Protection)을 매번 fetch하는 직렬 비용을 제거. 구현 lane Phase 2 PR open 직후 background로 prefetch → cache.

**의뢰 형식 (write queue type=security-prefetch)**:

```yaml
---
type: security-prefetch       # 신규 type
story: <KEY>
mode: background
requester: Orchestrator        # 보통 구현 lane 진입 직후 Orchestrator가 직접 의뢰
issued_at: <ISO 8601>
priority: normal
---
[Args]
ref: <branch or PR ref>         # 필수 — 예: pull/<N>/head
output_cache: .claude-work/cache/<KEY>-sec1.json
```

**DocsAgent 측 처리**:
1. 4 항목 fetch (`gh api repos/<owner>/<repo>/...`):
   - `dependabot/alerts?state=open` — 의존성 CVE
   - `code-scanning/alerts?state=open` — CodeQL findings
   - `secret-scanning/alerts?state=open` — Secret Scanning
   - 가능 시 push-protection events
2. 결과 JSON merge → `output_cache` 경로 write (`Write(.claude-work/cache/<KEY>-sec1.json)`)
3. 캐시 만료: `cached_at` 필드 + 24h TTL — SecurityTestPL이 만료 감지 시 재fetch 의뢰

**SecurityTestPL 측 사용**: lane 진입 시 cache 존재 + TTL 유효 확인 → packet `first_layer_findings` 필드에 cache JSON inline. 부재·만료 시 본인이 직접 fetch (기존 절차 fallback).

**보안**: cache 파일에 CVE 정보 포함 가능 → `.gitignore`에 `.claude-work/cache/` 추가 의무 (Group F에서 처리).

**Bash 권한**: DocsAgent frontmatter `tools` 에 `Bash(gh api repos/*)` 명시 — 이미 §11/§12 milestone·discussions에서 허용된 패턴 재사용.

### 9. §10 "FIX Ledger" SSOT 스키마
```

- [ ] **Step 3: Verify**

```bash
grep -n "8.2 Security 1차 layer pre-fetch" /Users/1111971/workspace/mctrader/plugins/codeforge/agents/DocsAgent.md
grep -n "type: security-prefetch" /Users/1111971/workspace/mctrader/plugins/codeforge/agents/DocsAgent.md
```

Expected: 각 1회 매칭.

- [ ] **Step 4: Commit**

```bash
git -C /Users/1111971/workspace/mctrader/plugins/codeforge add agents/DocsAgent.md
git -C /Users/1111971/workspace/mctrader/plugins/codeforge commit -m "$(cat <<'EOF'
feat(cfp-19): DocsAgent §8.2 Security 1차 layer pre-fetch helper (R10)

- write queue type=security-prefetch 신규 (ref + output_cache args)
- gh api 4종 fetch (dependabot/code-scanning/secret-scanning/push-protection)
- .claude-work/cache/<KEY>-sec1.json TTL 24h
- SecurityTestPL이 cache hit 시 fetch 단계 skip
- cache 파일 .gitignore 추가 의무 (Group F)

Story: CFP-19 Tier 1+2 R1-R11 병렬화 개선 (5/13)
EOF
)"
```

---

## Task C1: orchestrator-playbook §11 — write queue mode 필드 (R1)

**Files:**
- Modify: `docs/orchestrator-playbook.md` §11.2 (라인 747-764)

write queue 파일 frontmatter에 `mode: blocking | background` 필수 필드 추가 + §11.4 drain 우선순위 갱신 + §11.5 spawn 트리거에 background 처리 명시.

- [ ] **Step 1: Read playbook §11 전체**

```bash
sed -n '737,805p' /Users/1111971/workspace/mctrader/plugins/codeforge/docs/orchestrator-playbook.md
```

- [ ] **Step 2: Edit §11.2 frontmatter 스키마에 mode 필드 추가**

old_string (정확 매칭):
```
**Frontmatter (전체 type 공통 필수)**:

```markdown
---
type: issue-comment | story-section | change-plan | adr | adr-draft | domain-knowledge | ledger-append | label-update | pr-create
story: <KEY>                # 필수 — 디렉토리 이름과 일치
requester: <AgentName>      # 필수 — 의뢰 에이전트 식별
issued_at: <ISO 8601>       # 필수 — 큐 진입 시각
priority: normal | high     # 필수 — drain 우선순위
section: "<N>"              # type=story-section 인 경우 필수 (§N), 기타 type 생략
---

{DocsAgent.md §"작업 요청 인터페이스" 의 해당 템플릿 본문}
```
```

new_string:
```
**Frontmatter (전체 type 공통 필수)**:

```markdown
---
type: issue-comment | story-section | change-plan | adr | adr-draft | domain-knowledge | ledger-append | label-update | pr-create | security-prefetch
story: <KEY>                # 필수 — 디렉토리 이름과 일치
requester: <AgentName>      # 필수 — 의뢰 에이전트 식별
issued_at: <ISO 8601>       # 필수 — 큐 진입 시각
priority: normal | high     # 필수 — drain 우선순위
mode: blocking | background # 필수 (R1, CFP-19) — drain timing 결정. blocking 분류 의무 7종 / background 분류 허용 4종은 agents/DocsAgent.md §"Drain 모드" SSOT
section: "<N>"              # type=story-section 인 경우 필수 (§N), 기타 type 생략
kind: impl-manifest         # type=story-section 이고 §8.5 자동 생성 의뢰 시 (R5, CFP-19)
---

{DocsAgent.md §"작업 요청 인터페이스" 의 해당 템플릿 본문}
```
```

- [ ] **Step 3: Edit §11.4 drain 우선순위 갱신**

old_string (정확 매칭, §11.4 첫 부분):
```
### 11.4 DocsAgent 측 drain 절차

Orchestrator가 DocsAgent를 스폰하면 DocsAgent는:

1. `.claude-work/doc-queue/<story>/` ls → seq 순으로 모든 파일 처리
```

new_string:
```
### 11.4 DocsAgent 측 drain 절차

Orchestrator가 DocsAgent를 스폰하면 DocsAgent는:

1. `.claude-work/doc-queue/<story>/` ls → **drain 우선순위 4단계** (R1, CFP-19) 순으로 정렬:
   1. `priority: high` AND `mode: blocking`
   2. `priority: normal` AND `mode: blocking`
   3. `priority: high` AND `mode: background`
   4. `priority: normal` AND `mode: background`
   같은 클래스 내 seq 순.
```

- [ ] **Step 4: Edit §11.5 spawn 트리거 갱신**

old_string (정확 매칭):
```
### 11.5 Orchestrator 측 스폰 트리거

- 레인 경계 (레인 종료 시점)
- FIX 판정 직후
- 사용자 ESCALATE 직전 (상태 영속화 목적)
- Story 완료 직전 (§11 최종 참조 기록)
```

new_string:
```
### 11.5 Orchestrator 측 스폰 트리거

**blocking drain 트리거** (다음 lane 진입 직전 반드시):
- 레인 경계 — 다음 lane spawn **이전** blocking 의뢰 모두 drain 완료 확인
- FIX 판정 직후 — §10 ledger-append blocking
- 사용자 ESCALATE 직전 (상태 영속화 목적)
- Story 완료 직전 (§11 최종 참조 기록)
- Phase 1 PR open / Phase 2 PR open 직전

**background drain 트리거** (lane 진행과 병렬 OK):
- 다음 lane spawn 직후 별도 DocsAgent run (mode: background 의뢰만 처리)
- 한 Story 내 누적 background queue가 5건 초과 시 보조 spawn

R1 ([CFP-19 spec](../docs/superpowers/specs/2026-04-27-cfp-19-orchestration-parallelization.md)) 정책으로 blocking이 다음 lane 게이트 역할 보존, background는 lane 진행과 병렬 처리.
```

- [ ] **Step 5: Verify §11 갱신**

```bash
grep -n "mode: blocking | background" /Users/1111971/workspace/mctrader/plugins/codeforge/docs/orchestrator-playbook.md
grep -n "drain 우선순위 4단계" /Users/1111971/workspace/mctrader/plugins/codeforge/docs/orchestrator-playbook.md
grep -n "blocking drain 트리거" /Users/1111971/workspace/mctrader/plugins/codeforge/docs/orchestrator-playbook.md
```

Expected: 각 1회 매칭.

- [ ] **Step 6: Commit**

```bash
git -C /Users/1111971/workspace/mctrader/plugins/codeforge add docs/orchestrator-playbook.md
git -C /Users/1111971/workspace/mctrader/plugins/codeforge commit -m "$(cat <<'EOF'
feat(cfp-19): playbook §11 — write queue mode 필드 + drain 우선순위 4단계 (R1)

- §11.2 frontmatter: mode 필수 + kind=impl-manifest hint (R5 연계) + type=security-prefetch 신규 type 추가 (R10 연계)
- §11.4 drain: 4단계 우선순위 (priority × mode)
- §11.5 spawn 트리거: blocking/background 분리 — blocking은 lane 진입 전 drain 완료, background는 별도 spawn

Story: CFP-19 Tier 1+2 R1-R11 병렬화 개선 (6/13)
EOF
)"
```

---

## Task C2: orchestrator-playbook §3 스폰 시퀀스 (R3 + R7 + R9 + R10)

**Files:**
- Modify: `docs/orchestrator-playbook.md` §3.1 (라인 196-221)

§3.1 스폰 시퀀스 다이어그램에 4 변경:
- R3: ReviewPL spawn 표현 명료화 ("Orchestrator가 두 워커 한 메시지에 dispatch")
- R7: 설계 리뷰 PASS → Track A merge ∥ Track B Phase 2 prep 분기
- R9: TestAgent functional ∥ performance 병렬 표기
- R10: SecurityTestPL 1차 layer prefetch 캐시 hit 분기

- [ ] **Step 1: Read §3.1 (라인 196-221)**

```bash
sed -n '196,225p' /Users/1111971/workspace/mctrader/plugins/codeforge/docs/orchestrator-playbook.md
```

- [ ] **Step 2: Edit §3.1 — 4 라인 갱신**

old_string (정확 매칭, 다이어그램 라인 207-218):
```
설계 리뷰:   Orchestrator → DesignReviewPLAgent (lane=design packet) → (ClaudeReviewAgent ∥ CodexReviewAgent) → PASS/FIX
                         → PASS 시 DocsAgent가 gate:design-review-pass 라벨 부착 → Phase 1 PR mergeable
구현:        Phase 1 PR merge 후 Phase 2 PR open (DeveloperPL → DocsAgent → mcp__github__create_pull_request)
             Orchestrator → (DeveloperPLAgent(role:dev roster 병렬) ∥ QADev) → 완료 보고
                         → Orchestrator가 ArchitectPLAgent stateless 재스폰 → 매핑표 감사 (chief author 보조)
                         → §8.5 Impl Manifest commit 시 subissue-from-impl-manifest.yml 자동 sub-issue 생성
구현 리뷰:   Orchestrator → CodeReviewPLAgent (lane=code packet) → (ClaudeReviewAgent ∥ CodexReviewAgent) → PASS/FIX
구현 테스트: Orchestrator → TestAgent (기능 → 성능 순차) → ALL PASS/FAIL
보안 테스트: Orchestrator → SecurityTestPLAgent (lane=security packet + 1차 layer fetch 의무)
             1차 layer (자동): Dependabot + CodeQL + Secret Scanning + Push Protection 결과 fetch (`gh api repos/*`)
             2차 layer (병렬): ClaudeReviewAgent ∥ CodexReviewAgent → PASS/FIX
                         → PASS 시 DocsAgent가 gate:security-test-pass 라벨 부착 → Phase 2 PR mergeable
```

new_string:
```
설계 리뷰:   Orchestrator → DesignReviewPLAgent (lane=design packet 작성) → packet return
             → Orchestrator가 한 메시지에 (ClaudeReviewAgent ∥ CodexReviewAgent) dispatch → PL이 결과 종합 → PASS/FIX (R3, R2 verdict-first)
                         → PASS 시 **2 트랙 병렬** (R7):
                            · Track A: DocsAgent가 gate:design-review-pass 라벨 부착 + Phase 1 PR mergeable·merge
                            · Track B: DeveloperPL spawn → Change Plan §5·§8 fetch + 첫 commit draft 준비 (PR open 보류)
                         → Track A merge 완료 시 Track B가 즉시 mcp__github__create_pull_request 호출
                         → 동시에 Orchestrator가 background DocsAgent 의뢰 (type=security-prefetch, R10) → .claude-work/cache/<KEY>-sec1.json 생성
구현:        Orchestrator → (DeveloperPLAgent(role:dev roster 병렬) ∥ QADev) → 완료 보고
                         → §8.5 Impl Manifest 자동 생성 (DocsAgent kind=impl-manifest helper, R5) → DeveloperPL review-edit
                         → Orchestrator가 ArchitectPLAgent stateless 재스폰 → 매핑표 감사 (chief author 보조)
                         → §8.5 commit 시 subissue-from-impl-manifest.yml 자동 sub-issue 생성
구현 리뷰:   Orchestrator → CodeReviewPLAgent (lane=code packet 작성) → packet return
             → Orchestrator가 한 메시지에 (ClaudeReviewAgent ∥ CodexReviewAgent) dispatch → PL 종합 → PASS/FIX (R3, R2)
                         FIX 시 mechanical_category 자격 확인 → fast-path 또는 정상 cycle (R11)
구현 테스트: Orchestrator → TestAgent **subset 병렬** (R9):
                         · TestAgent(subset: functional) ∥ TestAgent(subset: performance)
                         → 두 subset 모두 PASS 시 보안 lane 진입
                         (consumer overlay에서 performance가 functional 부산물 의존 시 sequential fallback)
보안 테스트: Orchestrator → SecurityTestPLAgent (lane=security packet 작성, 1차 layer cache hit/miss 확인)
             1차 layer: .claude-work/cache/<KEY>-sec1.json hit 시 inline 첨부 (R10) / miss 시 PL이 직접 fetch
             2차 layer: PL이 packet return → Orchestrator가 한 메시지에 (ClaudeReviewAgent ∥ CodexReviewAgent) dispatch → PL 종합 → PASS/FIX (R3, R2)
                         → PASS 시 DocsAgent가 gate:security-test-pass 라벨 부착 → Phase 2 PR mergeable
```

- [ ] **Step 3: Verify §3.1 변경**

```bash
grep -n "Orchestrator가 한 메시지에" /Users/1111971/workspace/mctrader/plugins/codeforge/docs/orchestrator-playbook.md
grep -n "subset: functional" /Users/1111971/workspace/mctrader/plugins/codeforge/docs/orchestrator-playbook.md
grep -n "Track A: DocsAgent" /Users/1111971/workspace/mctrader/plugins/codeforge/docs/orchestrator-playbook.md
grep -n "type=security-prefetch" /Users/1111971/workspace/mctrader/plugins/codeforge/docs/orchestrator-playbook.md
```

Expected: 각 ≥1 매칭.

- [ ] **Step 4: Commit**

```bash
git -C /Users/1111971/workspace/mctrader/plugins/codeforge add docs/orchestrator-playbook.md
git -C /Users/1111971/workspace/mctrader/plugins/codeforge commit -m "$(cat <<'EOF'
feat(cfp-19): playbook §3.1 스폰 시퀀스 — R3/R7/R9/R10 반영

- R3: ReviewPL → packet return → Orchestrator가 한 메시지에 두 워커 dispatch (재귀 spawn 금지 정합)
- R7: 설계 리뷰 PASS → Track A(merge) ∥ Track B(Phase 2 prep) 병렬 + security-prefetch background 시작
- R9: TestAgent subset functional ∥ performance 병렬
- R10: SecurityTestPL 1차 layer cache hit/miss 분기

Story: CFP-19 Tier 1+2 R1-R11 병렬화 개선 (7/13)
EOF
)"
```

---

## Task C3: orchestrator-playbook §6 FIX state machine (R4 + R11)

**Files:**
- Modify: `docs/orchestrator-playbook.md` §6 (라인 423-483)

§6에 R4 parallel diagnosis 절 + R11 mechanical fast-path 절 추가.

- [ ] **Step 1: Read playbook §6**

```bash
sed -n '423,485p' /Users/1111971/workspace/mctrader/plugins/codeforge/docs/orchestrator-playbook.md
```

- [ ] **Step 2: Edit §6 끝에 §6.6 R4 parallel diagnosis + §6.7 R11 fast-path 추가**

old_string (정확 매칭, §6.5 끝 + §7 헤더):
```
### 6.5 원인 판정 decision table

[CLAUDE.md "원인 판정 decision table" 섹션 SSOT 참조 — 본 playbook은 호출 절차만 명시.]

DeveloperPL 1차 진단 → ArchitectPL 최종 판정 → Change Plan 갱신 (설계 원인) 또는 commit append (구현 원인). evidence pack 첨부 의무.

---

## 7. 세션 재개(resume) 복원 절차
```

new_string:
```
### 6.5 원인 판정 decision table

[CLAUDE.md "원인 판정 decision table" 섹션 SSOT 참조 — 본 playbook은 호출 절차만 명시.]

DeveloperPL 1차 진단 → ArchitectPL 최종 판정 → Change Plan 갱신 (설계 원인) 또는 commit append (구현 원인). evidence pack 첨부 의무.

### 6.6 Parallel diagnosis (R4, [CFP-19 spec](superpowers/specs/2026-04-27-cfp-19-orchestration-parallelization.md))

review·테스트 FIX (구현 리뷰·구현 테스트·보안 테스트) 시 DeveloperPL 1차 진단과 ArchitectPL 최종 판정을 **병렬 spawn**한다 (한 메시지에 dispatch).

**절차**:
1. Orchestrator가 FIX verdict 수령
2. 한 메시지에 두 에이전트 동시 spawn:
   - DeveloperPL: 1차 원인 진단 (구현 / 설계) — 결과를 Story file §10 row append로 ledger-append (mode: blocking)
   - ArchitectPL: 최종 판정 — review findings + Change Plan + ADR 정합성 평가 (DeveloperPL 결과 미수신, 독립 판단)
3. 두 결과 수령 후 비교:
   - **일치 (양쪽 동일 원인)**: 해당 원인 그대로 진행 (구현 commit append 또는 Change Plan 갱신)
   - **불일치**: ArchitectPL verdict 우선 (chief judge 책무 보존). DeveloperPL 진단을 §10 row 비고에 archive

**낙관적 가속 가정**: 80% 케이스 일치 → 직렬 5-10분을 병렬 2-3분으로 단축. 20% 불일치 시 ArchitectPL 우선이라 retry overhead 없음.

**제약**: 설계 리뷰 FIX는 본 절 범위 외 — DeveloperPL 미개입 (기존 절차: ArchitectPL 직접 회귀).

### 6.7 Mechanical fast-path (R11, [CFP-19 spec](superpowers/specs/2026-04-27-cfp-19-orchestration-parallelization.md))

ReviewPL verdict packet의 `mechanical_category` 필드 (typo / broken-link / minor-naming / comment-only / none — SSOT [`templates/review-pl-base.md`](../templates/review-pl-base.md) §3 R11 절) + severity 조합으로 fast-path 자격 판정:

**자격 조건**: `mechanical_category != none` AND (severity = P2 OR (severity = P1 AND 영향 파일 수 = 1))

**자격 충족 시 절차**:
1. Orchestrator가 §6.6 parallel diagnosis 건너뛰고 DeveloperPL 직접 spawn (fix-only 모드)
2. DeveloperPL이 fix commit
3. **same-iteration internal verify** — 다음 review iteration이 동일 finding 검출 안 하면 PASS, 검출 시 Iter row append (정상 cycle 회복)
4. §10 ledger 신규 row 안 매김 (fast-path는 카운터 증가 안 함)

**자격 미충족 또는 분류 잘못**: 다음 review iteration이 P0/P1 검출 → 정상 §6.6 cycle.

**제약**: 보안 lane의 injection / credential / CVE / trust-boundary 카테고리는 항상 `mechanical_category = none`이라 fast-path 자격 없음 ([`templates/review-pl-base.md`](../templates/review-pl-base.md) §3 R11 SSOT).

---

## 7. 세션 재개(resume) 복원 절차
```

- [ ] **Step 3: Verify §6.6 + §6.7 추가**

```bash
grep -n "6.6 Parallel diagnosis (R4" /Users/1111971/workspace/mctrader/plugins/codeforge/docs/orchestrator-playbook.md
grep -n "6.7 Mechanical fast-path (R11" /Users/1111971/workspace/mctrader/plugins/codeforge/docs/orchestrator-playbook.md
grep -n "낙관적 가속 가정" /Users/1111971/workspace/mctrader/plugins/codeforge/docs/orchestrator-playbook.md
```

Expected: 각 1회 매칭.

- [ ] **Step 4: Commit**

```bash
git -C /Users/1111971/workspace/mctrader/plugins/codeforge add docs/orchestrator-playbook.md
git -C /Users/1111971/workspace/mctrader/plugins/codeforge commit -m "$(cat <<'EOF'
feat(cfp-19): playbook §6.6 parallel diagnosis + §6.7 mechanical fast-path (R4 + R11)

- §6.6: DeveloperPL 1차 진단 ∥ ArchitectPL 최종 판정 병렬 spawn, 불일치 시 ArchitectPL 우선
- §6.7: typo/broken-link/minor-naming/comment-only 자격 fast-path, 카운터 증가 안 함
- 보안 lane injection/credential/CVE/trust-boundary는 항상 fast-path 자격 없음

Story: CFP-19 Tier 1+2 R1-R11 병렬화 개선 (8/13)
EOF
)"
```

---

## Task C4: orchestrator-playbook §12 context packet warm cache (R6)

**Files:**
- Modify: `docs/orchestrator-playbook.md` §12 (라인 806-)

§12에 §12.6 warm cache (R6) 절 추가.

- [ ] **Step 1: Read §12 끝부분**

```bash
sed -n '806,920p' /Users/1111971/workspace/mctrader/plugins/codeforge/docs/orchestrator-playbook.md
```

- [ ] **Step 2: Edit §12 — 마지막 §12.5 (Project Config Packet) 다음에 §12.6 추가**

먼저 §12.5의 끝 anchor 확정:

```bash
sed -n '855,925p' /Users/1111971/workspace/mctrader/plugins/codeforge/docs/orchestrator-playbook.md
```

§12.5 끝 + §13 헤더 anchor를 정확 매칭. (실제 파일 상태에서 §12.5 바로 다음에 §13이 오는지 확인 후 다음 패턴으로 edit)

old_string (anchor — §13 헤더 이전 마지막 줄 정확 매칭):
```

## 13. PMOAgent 프로젝트 관리 (Cross-cutting)
```

new_string:
```

### 12.6 Warm cache (R6, [CFP-19 spec](superpowers/specs/2026-04-27-cfp-19-orchestration-parallelization.md))

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
- DocsAgent가 Story file edit 후 `git rev-parse HEAD:docs/stories/<KEY>.md` 변경 → 자동 cache miss
- Story 완료 시 cache 파일 cleanup (선택)

**보안**: cache 파일에 §1 사용자 원문 포함 → `.gitignore`에 `.claude-work/cache/` 추가 의무 (Group F).

---

## 13. PMOAgent 프로젝트 관리 (Cross-cutting)
```

- [ ] **Step 3: Verify §12.6 추가**

```bash
grep -n "12.6 Warm cache (R6" /Users/1111971/workspace/mctrader/plugins/codeforge/docs/orchestrator-playbook.md
grep -n "story_file_commit" /Users/1111971/workspace/mctrader/plugins/codeforge/docs/orchestrator-playbook.md
```

Expected: 각 1회 매칭.

- [ ] **Step 4: Commit**

```bash
git -C /Users/1111971/workspace/mctrader/plugins/codeforge add docs/orchestrator-playbook.md
git -C /Users/1111971/workspace/mctrader/plugins/codeforge commit -m "$(cat <<'EOF'
feat(cfp-19): playbook §12.6 — warm cache (R6)

- .claude-work/cache/<KEY>-sections.json 스키마 정의
- git commit hash 기반 invalidation
- 1 Story 24 spawn 중 14-18 hit 기대 (lane 경계 drift만 miss)
- §1 verbatim 포함 → .gitignore 의무 (Group F)

Story: CFP-19 Tier 1+2 R1-R11 병렬화 개선 (9/13)
EOF
)"
```

---

## Task D1: ArchitectPLAgent fail-fast pre-synthesis + parallel diagnosis (R4 + R8)

**Files:**
- Modify: `agents/ArchitectPLAgent.md`

§"설계 레인 실행 흐름 (3-phase)"의 Phase 2 직전에 **R8 fail-fast pre-synthesis** 절 추가 + §"FIX 루프 최종 원인 판정자"에 **R4 parallel diagnosis 입력 적합성** 절 추가.

- [ ] **Step 1: Read ArchitectPLAgent.md 전체**

```bash
sed -n '1,120p' /Users/1111971/workspace/mctrader/plugins/codeforge/agents/ArchitectPLAgent.md
```

- [ ] **Step 2: Edit Phase 1 ↔ Phase 2 사이에 fail-fast 절 추가 (R8)**

old_string (정확 매칭):
```
### Phase 2: Synthesis (순차)
```

new_string:
```
### Phase 1.5: Fail-fast pre-synthesis check (R8, [CFP-19 spec](../docs/superpowers/specs/2026-04-27-cfp-19-orchestration-parallelization.md))

Phase 1에서 4 deputy 산출물 수령 직후 (Phase 2 chief author 호출 전) **빠른 sanity check** 수행. 결격 deputy detected 시 즉시 clarification 재spawn 의뢰 → 통합 단계 도달 전 cycle 단축.

**Sanity check 항목** (deputy 산출물 단위, 메타-규칙 1·2의 light version):
1. **§섹션 author input 표면 형식**: 각 deputy가 자신의 §섹션에 대한 input 절을 산출했는가
   - CodebaseMapper → §2 현재 구조 input
   - RefactorAgent → §3 도입할 설계 input + §6 리팩터링 선행 input
   - SecurityArchitectAgent → §7 보안 설계 input (§7.1-§7.5 또는 §7.6 N/A)
   - TestContractArchitectAgent → §8 Test Contract author input
2. **Story §1 cross-ref 존재**: 각 deputy 산출물이 Story file §1 사용자 원문에 대한 명시적 참조 (인용 또는 anchor link)를 포함하는가
3. **외부 입력 무결성**: deputy가 수신한 input(코드 경로 + 관련 ADR + Change Plan 초안)이 frontmatter에 명시한 scope와 일치하는가

**결격 detected 시**: Orchestrator에 "<DeputyName> 재spawn 요청 + clarification context: <결격 항목>" 전달 → Orchestrator가 해당 deputy 신규 spawn (이전 출력 + 재질의 context). 재spawn 횟수는 Story 1건당 deputy당 최대 2회 (이후 ESCALATE).

**Pass 시**: Phase 2 Synthesis 진입.

### Phase 2: Synthesis (순차)
```

- [ ] **Step 3: Edit §"FIX 루프 최종 원인 판정자"에 R4 절 추가**

먼저 해당 절 위치 확인:

```bash
sed -n '76,108p' /Users/1111971/workspace/mctrader/plugins/codeforge/agents/ArchitectPLAgent.md
```

old_string (정확 매칭, §"FIX 루프 최종 원인 판정자" 섹션의 끝 + §"GitHub Issue 코멘트 형식" 헤더 anchor):
```
## FIX 루프 최종 원인 판정자
```

new_string:
```
## FIX 루프 최종 원인 판정자
```

(헤더 그대로 유지하고 그 뒤 첫 본문 절 또는 절 끝에 R4 절 삽입 — 정확한 위치는 실제 파일 구조에 따름. 본 절을 별도 sub-section으로 추가)

먼저 §"FIX 루프 최종 원인 판정자" 본문 끝 (다음 §"GitHub Issue 코멘트 형식" 또는 §"설계 리뷰 레인 FIX" 직전) anchor를 sed로 확정:

```bash
sed -n '76,90p' /Users/1111971/workspace/mctrader/plugins/codeforge/agents/ArchitectPLAgent.md
```

확인된 본문 끝 + 다음 헤더 anchor 정확 매칭:

old_string (예시 — 실제 파일 anchor 사용):
```
## 설계 리뷰 레인 FIX (최대 3회)
```

new_string:
```
### Parallel diagnosis 입력 (R4, [CFP-19 spec](../docs/superpowers/specs/2026-04-27-cfp-19-orchestration-parallelization.md))

구현 리뷰·구현 테스트·보안 테스트 FIX 시 Orchestrator가 본 에이전트와 DeveloperPL을 **병렬 spawn**. 본 에이전트는 DeveloperPL 진단 결과를 **수신하지 않음** — review findings + Change Plan + ADR 정합성으로 독립 판정.

- 입력: review verdict packet + Story file §1-7·§9 (cache 사용 권장) + Change Plan §3·§5·§7·§8 (관련 절만)
- 산출: 원인 분류(`설계` / `구현`) + evidence pack (Change Plan 인용 + ADR 인용 + 위반 위치 명시)
- 본 판정이 DeveloperPL 1차 진단과 불일치하면 본 판정 우선 (chief judge 책무 보존)
- 참조 절차: [`docs/orchestrator-playbook.md`](../docs/orchestrator-playbook.md) §6.6 SSOT

## 설계 리뷰 레인 FIX (최대 3회)
```

- [ ] **Step 4: Verify**

```bash
grep -n "Phase 1.5: Fail-fast pre-synthesis check (R8" /Users/1111971/workspace/mctrader/plugins/codeforge/agents/ArchitectPLAgent.md
grep -n "Parallel diagnosis 입력 (R4" /Users/1111971/workspace/mctrader/plugins/codeforge/agents/ArchitectPLAgent.md
```

Expected: 각 1회 매칭.

- [ ] **Step 5: Commit**

```bash
git -C /Users/1111971/workspace/mctrader/plugins/codeforge add agents/ArchitectPLAgent.md
git -C /Users/1111971/workspace/mctrader/plugins/codeforge commit -m "$(cat <<'EOF'
feat(cfp-19): ArchitectPLAgent — fail-fast pre-synthesis (R8) + parallel diagnosis 입력 (R4)

- Phase 1.5 sanity check: §섹션 author input 형식 / §1 cross-ref / scope 정합성. 결격 시 deputy 재spawn (max 2회/Story)
- FIX 루프: DeveloperPL 진단 미수신, 독립 판정. 불일치 시 본 판정 우선

Story: CFP-19 Tier 1+2 R1-R11 병렬화 개선 (10/13)
EOF
)"
```

---

## Task D2: DeveloperPLAgent — parallel diagnosis + manifest review-only + fast-path (R4 + R5 + R11)

**Files:**
- Modify: `agents/DeveloperPLAgent.md`

3 변경:
- §"FIX 루프 1차 원인 진단" 섹션에 R4 parallel diagnosis 절 추가 (ArchitectPL 결과 미수신 → 독립 진단)
- §"구현 완료 → 구현 리뷰" 섹션의 Impl Manifest 작성 절차를 review-only로 변경 (R5)
- §"FIX 루프 1차 원인 진단" 끝에 R11 fast-path 절 추가 (mechanical_category 자격 시 직접 fix commit)

- [ ] **Step 1: Read DeveloperPLAgent.md 전체**

```bash
sed -n '1,140p' /Users/1111971/workspace/mctrader/plugins/codeforge/agents/DeveloperPLAgent.md
```

- [ ] **Step 2: Edit §"구현 완료 → 구현 리뷰 레인 진입 흐름" — Impl Manifest review-only (R5)**

old_string (정확 매칭, §"Impl Manifest 포맷" 헤더 직후):
```
### Impl Manifest 포맷
```

먼저 §"Impl Manifest 포맷" 본문 정확 위치 확인:

```bash
sed -n '88,105p' /Users/1111971/workspace/mctrader/plugins/codeforge/agents/DeveloperPLAgent.md
```

본문 첫 줄을 확인 후 정확 매칭:

old_string (실제 파일 라인 88+ 구조 사용, 예시):
```
### Impl Manifest 포맷

[`templates/impl-manifest.md`](../templates/impl-manifest.md) SSOT 참조.
```

new_string:
```
### Impl Manifest 포맷

[`templates/impl-manifest.md`](../templates/impl-manifest.md) SSOT 참조.

**작성 절차 변경 (R5, [CFP-19 spec](../docs/superpowers/specs/2026-04-27-cfp-19-orchestration-parallelization.md))**:
- 본 에이전트는 Impl Manifest 표를 **수동 타이핑하지 않음**
- 대신 Orchestrator 경유 DocsAgent에 `kind: impl-manifest` 의뢰 (mode: blocking, args: commit_range + change_plan_path) — SSOT [`agents/DocsAgent.md`](DocsAgent.md) §8.1
- DocsAgent가 git diff에서 자동 생성한 표를 **review-edit**: description 컬럼만 line-edit (path/agent_role/related_change_plan_section은 helper가 결정)
- helper 실패 시 (git diff 파싱 오류 등) 수동 작성으로 fallback (기존 절차)
```

- [ ] **Step 3: Edit §"FIX 루프 1차 원인 진단" — R4 parallel diagnosis 절 추가**

먼저 §"FIX 루프 1차 원인 진단" 본문 끝 확인:

```bash
sed -n '94,135p' /Users/1111971/workspace/mctrader/plugins/codeforge/agents/DeveloperPLAgent.md
```

§"FIX 루프 1차 원인 진단" 섹션 본문에 R4 절 추가. 적당한 anchor (예: §"1차 가정 기준" 헤더 직전 또는 직후) 사용:

old_string (예시 — 실제 anchor 사용):
```
### 1차 가정 기준
```

new_string (anchor 그대로 유지하면서 직전에 새 절 삽입 패턴):
```
### Parallel diagnosis 출력 (R4, [CFP-19 spec](../docs/superpowers/specs/2026-04-27-cfp-19-orchestration-parallelization.md))

review·테스트 FIX 시 Orchestrator가 본 에이전트와 ArchitectPL을 **병렬 spawn**. 본 에이전트는 ArchitectPL 결과를 수신하지 않음 — 코드 변경 영향 + Change Plan §5 변경 계획 정합성으로 독립 진단.

- 입력: review verdict packet + Story file §8.5 Impl Manifest + Change Plan §5·§8 + 최근 commit diff
- 산출: 원인 분류(`구현` / `설계`) + 1줄 근거 + suggested fix 초안 → Story file §10 row append (mode: blocking)
- 본 진단은 ArchitectPL 최종 판정과 불일치할 수 있음 — 불일치 시 ArchitectPL 우선 (`§10` row 비고에 본 진단 archive)
- 참조 절차: [`docs/orchestrator-playbook.md`](../docs/orchestrator-playbook.md) §6.6 SSOT

### 1차 가정 기준
```

- [ ] **Step 4: Edit §"FIX 루프 1차 원인 진단" 또는 §"에스컬레이션 기준" 끝에 R11 fast-path 절 추가**

먼저 §"에스컬레이션 기준" 헤더 + 다음 헤더 정확 매칭:

```bash
sed -n '125,140p' /Users/1111971/workspace/mctrader/plugins/codeforge/agents/DeveloperPLAgent.md
```

old_string (정확 anchor — 예시):
```
## 문서화 표준
```

new_string:
```
## Mechanical fast-path (R11, [CFP-19 spec](../docs/superpowers/specs/2026-04-27-cfp-19-orchestration-parallelization.md))

ReviewPL verdict packet의 `mechanical_category` 자격 충족 시 (`mechanical_category != none` AND severity = P2 OR (P1 AND 파일 1)) — Orchestrator가 본 에이전트를 fix-only 모드로 직접 spawn. 절차:

1. 입력: review verdict packet (`mechanical_category` + 영향 파일 + finding location)
2. 직접 fix commit (Phase 2 PR commit append)
3. ArchitectPL 판정 skip — 다음 review iteration이 internal verify
4. §10 ledger 신규 row 안 매김

자격 분류 SSOT는 [`templates/review-pl-base.md`](../templates/review-pl-base.md) §3 R11 절. 보안 lane의 injection / credential / CVE / trust-boundary 카테고리는 항상 `none`이라 본 fast-path 미적용.

분류 잘못이면 다음 iteration이 P0/P1 검출 → 정상 §6.6 cycle 회복.

## 문서화 표준
```

- [ ] **Step 5: Verify**

```bash
grep -n "Parallel diagnosis 출력 (R4" /Users/1111971/workspace/mctrader/plugins/codeforge/agents/DeveloperPLAgent.md
grep -n "Mechanical fast-path (R11" /Users/1111971/workspace/mctrader/plugins/codeforge/agents/DeveloperPLAgent.md
grep -n "kind: impl-manifest" /Users/1111971/workspace/mctrader/plugins/codeforge/agents/DeveloperPLAgent.md
```

Expected: 각 1회 매칭.

- [ ] **Step 6: Commit**

```bash
git -C /Users/1111971/workspace/mctrader/plugins/codeforge add agents/DeveloperPLAgent.md
git -C /Users/1111971/workspace/mctrader/plugins/codeforge commit -m "$(cat <<'EOF'
feat(cfp-19): DeveloperPLAgent — parallel diagnosis(R4) + manifest review-only(R5) + fast-path(R11)

- §"Impl Manifest 포맷": DocsAgent kind=impl-manifest 의뢰 → review-edit only (수동 타이핑 deprecated)
- §"FIX 루프": ArchitectPL 결과 미수신, 독립 진단 산출
- §"Mechanical fast-path": mechanical_category 자격 시 ArchitectPL 판정 skip + §10 row 안 매김

Story: CFP-19 Tier 1+2 R1-R11 병렬화 개선 (11/13)
EOF
)"
```

---

## Task E1: TestAgent — subset arg (R9)

**Files:**
- Modify: `agents/TestAgent.md`

§"실행 원칙"·§"모드 1 기능 게이트"·§"모드 2 성능 게이트"에 `subset` 인자 명시 + 병렬 spawn 절 추가.

- [ ] **Step 1: Read TestAgent.md 전체**

```bash
cat /Users/1111971/workspace/mctrader/plugins/codeforge/agents/TestAgent.md
```

- [ ] **Step 2: Edit §"실행 원칙" 절에 subset arg 절 추가**

§"실행 원칙" 헤더 다음에 subset arg 명시:

old_string (정확 매칭):
```
## 실행 원칙
```

new_string:
```
## 실행 원칙

### 호출 시 subset arg (R9, [CFP-19 spec](../docs/superpowers/specs/2026-04-27-cfp-19-orchestration-parallelization.md))

본 에이전트는 `subset` 프롬프트 arg로 단일 모드 실행 가능 — Orchestrator가 두 subset을 병렬 spawn할 수 있도록 한다.

| `subset` 값 | 실행 모드 |
|------------|---------|
| `functional` | 모드 1만 실행 (unit/integration/infra) |
| `performance` | 모드 2만 실행 (성능 baseline 비교) |
| `all` (default) | 모드 1 → 모드 2 순차 실행 (기존 동작, 단일 spawn 시) |

**병렬 spawn 절차** (Orchestrator 측, [`docs/orchestrator-playbook.md`](../docs/orchestrator-playbook.md) §3.1):
1. 한 메시지에 두 spawn dispatch:
   - `Agent({subagent_type: 'TestAgent', prompt: '...subset: functional...'})`
   - `Agent({subagent_type: 'TestAgent', prompt: '...subset: performance...'})`
2. 두 결과 수령 후 종합:
   - 둘 다 PASS → 보안 lane 진입
   - 한쪽 FAIL → §6 FIX 루프 (다른 한쪽 결과는 fail-safe 보존, retry 시 재실행 안 함)

**제약**:
- consumer overlay에서 performance 모드가 functional 부산물(예: fixture·dataset)에 의존 시 sequential fallback (overlay에 명시: `tests.performance.depends_on_functional: true`)
- baseline 측정 환경(개별 worktree)이 functional 테스트 동시 실행에 영향받지 않는지 consumer 책임
```

- [ ] **Step 3: Verify**

```bash
grep -n "호출 시 subset arg (R9" /Users/1111971/workspace/mctrader/plugins/codeforge/agents/TestAgent.md
grep -n "depends_on_functional" /Users/1111971/workspace/mctrader/plugins/codeforge/agents/TestAgent.md
```

Expected: 각 1회 매칭.

- [ ] **Step 4: Commit**

```bash
git -C /Users/1111971/workspace/mctrader/plugins/codeforge add agents/TestAgent.md
git -C /Users/1111971/workspace/mctrader/plugins/codeforge commit -m "$(cat <<'EOF'
feat(cfp-19): TestAgent — subset arg (functional / performance / all) + 병렬 spawn 절차 (R9)

- subset=functional / performance 단일 모드 실행 가능
- subset=all 기존 동작 보존 (default, 단일 spawn 시)
- consumer overlay depends_on_functional 명시 시 sequential fallback

Story: CFP-19 Tier 1+2 R1-R11 병렬화 개선 (12/13)
EOF
)"
```

---

## Task F1: CLAUDE.md 스폰 시퀀스 + .gitignore + 종합 검증 + version bump

**Files:**
- Modify: `CLAUDE.md` (스폰 시퀀스 다이어그램)
- Modify: `.gitignore` (`.claude-work/cache/` 추가)
- Modify: `.claude-plugin/plugin.json` version bump (0.12.0 → 0.13.0)
- Modify: `CHANGELOG.md` v0.13.0 entry
- Verify: invariant-check.yml 전 단계 PASS

- [ ] **Step 1: Read CLAUDE.md 스폰 시퀀스 부분**

```bash
grep -n "^### 스폰 시퀀스\|^### " /Users/1111971/workspace/mctrader/plugins/codeforge/CLAUDE.md | head -20
```

해당 절 라인 범위 확인 후 read.

- [ ] **Step 2: Edit CLAUDE.md 스폰 시퀀스에 R3·R7·R9·R10 반영**

CLAUDE.md "### 스폰 시퀀스" 절은 playbook §3.1과 미러 관계. 본 단계에서는 다음 4개 행만 정확 갱신:

(2-1) 설계 리뷰 행:

old_string (정확 매칭):
```
[설계 리뷰] Orchestrator → DesignReviewPLAgent (lane=design packet 작성)
        ├── ClaudeReviewAgent (lane=design packet 수령)
        └── CodexReviewAgent  (lane=design packet 수령, 병렬)
        → severity 종합 → PASS or FIX (최대 3회)
```

new_string:
```
[설계 리뷰] Orchestrator → DesignReviewPLAgent (lane=design packet 작성) → packet return
        Orchestrator가 한 메시지에 dispatch:
        ├── ClaudeReviewAgent (lane=design packet 수령)
        └── CodexReviewAgent  (lane=design packet 수령, 병렬)
        → DesignReviewPL 결과 종합 → PASS or FIX (최대 3회) (R3·R2)
```

(2-2) 구현 리뷰 행:

old_string (정확 매칭):
```
[구현 리뷰] Orchestrator → CodeReviewPLAgent (lane=code packet 작성)
        ├── ClaudeReviewAgent (lane=code packet 수령)
        └── CodexReviewAgent  (lane=code packet 수령, 병렬)
        → severity 종합 → PASS or FIX (최대 3회)
```

new_string:
```
[구현 리뷰] Orchestrator → CodeReviewPLAgent (lane=code packet 작성) → packet return
        Orchestrator가 한 메시지에 dispatch:
        ├── ClaudeReviewAgent (lane=code packet 수령)
        └── CodexReviewAgent  (lane=code packet 수령, 병렬)
        → CodeReviewPL 결과 종합 → PASS or FIX (최대 3회) (R3·R2)
        FIX 시 mechanical_category 자격 확인 → fast-path 또는 정상 cycle (R11)
```

(2-3) 구현 테스트 행:

old_string (정확 매칭):
```
[구현 테스트] Orchestrator → TestAgent
        · 모드 1 (기능): 단위/통합/인프라 테스트 (consumer overlay가 러너·경로 지정)
        · 모드 2 (성능): 성능 테스트 — baseline 대비 mean 10% 이상 악화 시 FAIL (consumer overlay가 baseline 위치 지정)
        · ALL PASS → 보안 테스트 레인 진입
```

new_string:
```
[구현 테스트] Orchestrator → TestAgent **subset 병렬** (R9):
        · TestAgent(subset: functional) ∥ TestAgent(subset: performance) — 한 메시지에 dispatch
        · 둘 다 PASS → 보안 테스트 레인 진입
        · consumer overlay `tests.performance.depends_on_functional: true` 시 sequential fallback
```

(2-4) 보안 테스트 행 — 1차 layer prefetch (R10):

old_string (정확 매칭):
```
[보안 테스트] Orchestrator → SecurityTestPLAgent (lane=security packet 작성 + 1차 layer fetch)
        1차 layer (자동): Dependabot alerts + CodeQL findings + Secret Scanning + Push Protection (GitHub native, 워크플로우 자동 실행). PL이 `gh api repos/*` 로 결과 fetch → packet에 inline 첨부
```

new_string:
```
[보안 테스트] Orchestrator → SecurityTestPLAgent (lane=security packet 작성, 1차 layer cache hit/miss 확인)
        1차 layer: .claude-work/cache/<KEY>-sec1.json hit 시 inline 첨부 (R10) / miss 시 PL이 `gh api repos/*` 직접 fetch
        cache는 Phase 2 PR open 직후 Orchestrator가 background DocsAgent (type=security-prefetch)로 사전 생성
```

- [ ] **Step 3: Edit .gitignore**

먼저 .gitignore 현재 내용 확인:

```bash
cat /Users/1111971/workspace/mctrader/plugins/codeforge/.gitignore 2>/dev/null || echo "no .gitignore"
```

존재 시:

old_string (가능한 anchor — 예: `.claude-work/`가 이미 있으면 추가):
```
.claude-work/
```

new_string:
```
.claude-work/
.claude-work/cache/
```

(중복 안 되도록 grep 후 추가만 — 만약 `.claude-work/cache/` 이미 존재 시 skip)

부재 시 — 신규 작성:

```bash
cat > /Users/1111971/workspace/mctrader/plugins/codeforge/.gitignore <<'EOF'
.claude-work/
.claude-work/cache/
EOF
```

(실제 파일 상태 확인 후 적절 분기)

- [ ] **Step 4: Edit .claude-plugin/plugin.json — version bump**

```bash
grep -n "\"version\":" /Users/1111971/workspace/mctrader/plugins/codeforge/.claude-plugin/plugin.json
```

old_string:
```
  "version": "0.12.0",
```

new_string:
```
  "version": "0.13.0",
```

(파일에서 정확한 버전 행 매칭 — 만약 들여쓰기 다르면 실제 anchor 사용)

- [ ] **Step 5: Edit CHANGELOG.md — v0.13.0 entry 추가**

```bash
sed -n '1,30p' /Users/1111971/workspace/mctrader/plugins/codeforge/CHANGELOG.md
```

CHANGELOG.md 최상위 (`# Changelog` 헤더 다음)에 새 entry 추가:

old_string (정확 매칭):
```
# Changelog

```

new_string:
```
# Changelog

## v0.13.0 — 2026-04-28

### CFP-19 — 오케스트레이션 병렬화 (R1-R11 Tier 1+2)

**Non-BREAKING**. 사용자 critical feedback ("전체적으로 너무 느리다") 대응. Codex(GPT-5) + general-purpose 두 독립 감사 합의 11개 직렬 병목 제거. 본 plugin은 자기 적용 안 함 (paradox 처리, ADR-005 plugin-meta-na).

**Tier 1 (R1-R8)**:
- R1: DocsAgent dual-mode (blocking/background) write queue drain — `mode` 필드 필수, blocking 7종 / background 4종 분류
- R2: ReviewPL verdict-return-first protocol — DocsAgent save 대기 안 함, 다음 lane spawn 트리거 후 background drain
- R3: Orchestrator-direct dual review worker spawn — PL이 packet return → Orchestrator 한 메시지에 (Claude ∥ Codex) dispatch
- R4: FIX speculative pipelining — DeveloperPL 1차 진단 ∥ ArchitectPL 최종 판정 병렬, 불일치 시 ArchitectPL 우선
- R5: §8.5 Impl Manifest 자동 생성 — DocsAgent kind=impl-manifest helper, DeveloperPL은 review-edit only
- R6: Lane Context Packet warm cache — `.claude-work/cache/<KEY>-sections.json` git commit hash invalidation
- R7: Phase 1 merge ↔ Phase 2 prep parallel — 설계 리뷰 PASS 즉시 Track A(merge) ∥ Track B(prep) 병렬
- R8: ArchitectPL fail-fast pre-synthesis — Phase 1.5 sanity check, 결격 deputy clarification 재spawn

**Tier 2 (R9-R11)**:
- R9: TestAgent subset 병렬 — `subset: functional` ∥ `subset: performance`
- R10: SecurityTestPL 1차 layer pre-fetch — `.claude-work/cache/<KEY>-sec1.json` background prefetch
- R11: FIX mechanical fast-path — typo/broken-link/minor-naming/comment-only 자격 시 ArchitectPL 판정 skip + §10 row 안 매김

**예상 효과**: Story 1건당 평균 20-32분 단축 (60-90분 → 40-60분 예상, 30-40% reduction).

**변경 파일**: `templates/review-pl-base.md`, `agents/{DocsAgent,ArchitectPLAgent,DeveloperPLAgent,DesignReviewPLAgent,CodeReviewPLAgent,SecurityTestPLAgent,TestAgent}.md`, `docs/orchestrator-playbook.md`, `CLAUDE.md`, `.gitignore`. ADR 변경 0건.

**Spec/Plan**: [`docs/superpowers/specs/2026-04-27-cfp-19-orchestration-parallelization.md`](docs/superpowers/specs/2026-04-27-cfp-19-orchestration-parallelization.md), [`docs/superpowers/plans/2026-04-27-cfp-19-orchestration-parallelization.md`](docs/superpowers/plans/2026-04-27-cfp-19-orchestration-parallelization.md).

```

- [ ] **Step 6: invariant-check 전 단계 검증**

```bash
cd /Users/1111971/workspace/mctrader/plugins/codeforge && \
ls .github/workflows/ | grep -i invariant
```

invariant-check.yml 워크플로우 존재 시 로컬 dry-run (가능 시):

```bash
# Step 1: 23 core agents 카운트
ls /Users/1111971/workspace/mctrader/plugins/codeforge/agents/*.md | wc -l
# Expected: 23
```

```bash
# Step 6: 3 lane category enum parity (templates/review-checklists/*.md ↔ agents/{ClaudeReview,CodexReview}.md)
cd /Users/1111971/workspace/mctrader/plugins/codeforge && \
grep -c "Category enum" templates/review-checklists/*.md
# Expected: 각 1회 매칭 (3 lane × 1)
```

```bash
# Step 8: severity overrides count parity
cd /Users/1111971/workspace/mctrader/plugins/codeforge && \
for f in templates/review-checklists/*.md; do
  echo "=== $f ==="
  grep -c "→ \*\*P0\*\*" "$f"
done
```

각 lane checklist의 P0 룰 수 일치 확인 (CFP-19로 추가된 mechanical fast-path는 P0 룰 추가 없음).

- [ ] **Step 7: Markdown link 깨짐 검사**

```bash
cd /Users/1111971/workspace/mctrader/plugins/codeforge && \
grep -rEn '\[([^]]+)\]\(([^)]+)\)' templates/review-pl-base.md agents/DocsAgent.md docs/orchestrator-playbook.md CLAUDE.md docs/superpowers/specs/2026-04-27-cfp-19-orchestration-parallelization.md docs/superpowers/plans/2026-04-27-cfp-19-orchestration-parallelization.md | \
  awk -F'[()]' '{for (i=2; i<=NF; i+=2) {if ($i ~ /^http/) continue; if ($i ~ /^#/) continue; print $i}}' | \
  sort -u | head -30
```

각 링크 경로가 실재하는지 random sampling 5개 확인.

- [ ] **Step 8: 23 core agent 카운트 invariant 점검 (CFP-18 후속, 변경 없음 확인)**

```bash
cd /Users/1111971/workspace/mctrader/plugins/codeforge && \
ls agents/*.md | wc -l
grep -c "23 core" CLAUDE.md docs/orchestrator-playbook.md .claude-plugin/plugin.json
```

Expected: ls=23, "23 core" 카운트 ≥1 in 각 파일.

- [ ] **Step 9: Commit (Group F 종합 commit)**

```bash
git -C /Users/1111971/workspace/mctrader/plugins/codeforge add CLAUDE.md .gitignore .claude-plugin/plugin.json CHANGELOG.md
git -C /Users/1111971/workspace/mctrader/plugins/codeforge commit -m "$(cat <<'EOF'
feat(cfp-19): CLAUDE.md 스폰 시퀀스 동기화 + .gitignore + v0.13.0 release

- CLAUDE.md 4 항목 갱신: 설계 리뷰·구현 리뷰 (R3·R2 dispatch), 구현 테스트 (R9 subset), 보안 테스트 (R10 cache hit/miss)
- .gitignore: .claude-work/cache/ 추가 (R6 sections cache + R10 sec1 cache)
- plugin.json: 0.12.0 → 0.13.0
- CHANGELOG.md: v0.13.0 entry — 11 R 요약, 예상 30-40% Story 처리시간 단축

Story: CFP-19 Tier 1+2 R1-R11 병렬화 개선 (13/13)

본 plugin 자기 적용 안 함 (paradox 처리, ADR-005 plugin-meta-na). 다음 Story부터 발효.
EOF
)"
```

---

## Self-Review

### 1. Spec 커버리지

각 R 매핑:
- R1 → Task B1 + C1 ✓
- R2 → Task A1 (verdict-first) + A2 ✓
- R3 → Task A1 (호출 시점 명료화) + C2 + Task F1 (CLAUDE.md) ✓
- R4 → Task C3 (§6.6 parallel diagnosis) + D1 (ArchitectPL) + D2 (DeveloperPL) ✓
- R5 → Task B2 (DocsAgent helper) + D2 (DeveloperPL review-only) ✓
- R6 → Task C4 (warm cache) + F1 (.gitignore) ✓
- R7 → Task C2 (Track A/B parallel) + F1 (CLAUDE.md) ✓
- R8 → Task D1 (ArchitectPL Phase 1.5 fail-fast) ✓
- R9 → Task E1 (TestAgent subset) + C2 + F1 (CLAUDE.md) ✓
- R10 → Task B3 (DocsAgent helper) + C2 (스폰 시퀀스) + F1 (CLAUDE.md) + F1 (.gitignore) ✓
- R11 → Task A1 (review-pl-base SSOT) + A2 (3 PL 분류 의무) + C3 (§6.7 fast-path) + D2 (DeveloperPL fast-path 절차) + F1 (CLAUDE.md 구현 리뷰) ✓

§5 Test Contract 후보: 본 plugin은 자기 적용 안 함이라 §8 N/A. 변경 검증은 invariant-check.yml + grep parity (Task F1 Step 6-8).

§6 보안 영향: cache 파일 gitignore 의무 (Task F1 Step 3) — Trust boundary 변화 없음.

### 2. Placeholder scan

- "TBD"/"TODO"/"implement later" — 본 plan에 없음 ✓
- "fill in details" — 없음 ✓
- "Similar to Task N" — 없음 (각 Task 자체 완결 기술) ✓
- "appropriate error handling" — 없음 ✓
- 모든 step에 정확 명령 또는 정확 markdown edit anchor 명시 ✓

### 3. 타입·이름 일관성

- `mechanical_category` 값 enum: `typo | broken-link | minor-naming | comment-only | none` — A1·A2·C3·D2·F1 모두 동일 ✓
- `mode: blocking | background` — A1·B1·C1·F1 모두 동일 ✓
- `kind: impl-manifest` — B2·C1·D2 모두 동일 ✓
- `type: security-prefetch` — B3·C1 동일 ✓
- `subset: functional | performance | all` — E1·F1 동일 ✓
- `.claude-work/cache/<KEY>-sections.json` (R6) vs `.claude-work/cache/<KEY>-sec1.json` (R10) — 의도된 분리, 두 파일 다른 용도 ✓

### 4. Story 작성 의무

§"Story 작성 의무" 강제 대상 (SSOT 문서 의미 변경) — Story KEY=`CFP-19`. Phase 1 PR (요구사항+설계+설계리뷰)와 Phase 2 PR (구현+리뷰+테스트+보안) 분리 의무. 단 본 변경은 plugin meta이라 §8 Test Contract / §9 리뷰 결과는 plugin-meta-na (ADR-005) 패턴 적용 — 13 commit이 모두 docs/agents/templates 변경이라 1 PR로 통합 가능 검토 필요.

→ **운영 결정**: CFP-17 Phase 2 PR (#50) 패턴 차용 — 13 commit을 1 PR로 통합 (plugin-meta-na 적용). Phase 1 의 Story doc·Change Plan·ADR 작성은 본 plan 외 별도 prerequisite (Story 작성 의무 정책).

→ **사전 prerequisite (본 plan 시작 전)**:
1. GitHub Issue Form (story.yml) 제출 — Title `[STORY] CFP-19 — 오케스트레이션 병렬화 R1-R11`, body §1에 사용자 원문 verbatim
2. story-init.yml Action이 `docs/stories/CFP-19.md` 생성 + Phase 1 PR 자동 open
3. RequirementsPL → DomainAgent · Analyst · Researcher 병렬 (셋 다 null 결과 가능 — meta plugin 변경)
4. 설계 lane: ArchitectPL → 4 deputy 병렬 → ArchitectAgent chief author → Change Plan `docs/change-plans/cfp-19-orchestration-parallelization.md`
5. 설계 리뷰 PASS → Phase 1 PR merge
6. **여기부터 본 plan 13 task 시작** (Phase 2 lane)

→ **간소화 옵션 (사용자 결정 필요)**: 본 CFP가 plugin meta 자기-적용이고 spec/plan이 이미 작성되어 있으므로, Phase 1 lane (요구사항+설계+설계리뷰)을 최소 형태로 처리:
- Story file §1-7을 spec 인용으로 채우고 (요구사항·도메인·연구는 spec §1·§4·§9 소스로 mock)
- Change Plan은 본 plan 자체를 인용 (별도 작성 안 함)
- 설계 리뷰는 Claude+Codex 1라운드로 spec/plan 정합성만 (생략 X)
- Phase 1 PR은 spec + plan + Story doc 만 포함, 나머지는 Phase 2 PR (13 commit)

본 단순화는 dogfooding 일관성 위해 **사용자 사전 승인 필요** — 현 conversation 진입 시점에 이미 spec 작성 완료라 §"Story 작성 의무" 정책 위반 우려 있음.

---

## 실행 핸드오프

**Plan complete and saved to `docs/superpowers/plans/2026-04-27-cfp-19-orchestration-parallelization.md`. Two execution options:**

**1. Subagent-Driven (recommended)** — Fresh subagent per task, two-stage review, fast iteration

**2. Inline Execution** — Batch execution with checkpoints

**Which approach?**

**사전 결정 필요 (Self-Review §4)**: Phase 1 lane을 어떻게 처리할지 사용자 결정.
- (a) **Full 7-lane** — 공식 절차 (Story Issue 제출 → Phase 1 PR → 설계 리뷰 → merge → Phase 2 PR로 13 task)
- (b) **간소화** — spec/plan 작성됨 인정 + Phase 1 최소 형태 (Story doc 생성 + 설계 리뷰 1라운드) + Phase 2에 13 task 통합 (CFP-17/18 패턴)
- (c) **CFP-17 Phase 2 단독 패턴** — Story doc + 13 task + plugin-meta-na로 1 PR 통합 (가장 빠름, dogfooding 정책 약간 약함)

**권고**: (b) — Phase 1 최소 형태로 dogfooding 일관성 보존하되 spec/plan 재작성 비용 제거.
