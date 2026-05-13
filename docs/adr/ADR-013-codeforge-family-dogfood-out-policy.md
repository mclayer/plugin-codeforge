---
adr_number: 13
title: Codeforge Family Dogfood-out Policy
status: Adopted
category: Team & Process
date: 2026-04-30
related_files:
  - CLAUDE.md (canonical dogfood policy + internal-docs pointer)
  - docs/superpowers/specs/2026-04-30-cfp-45-dogfood-out-restructure-design.md (parent CFP)
  - mclayer/codeforge-internal-docs (NEW external repo — dogfood artifact monorepo)
related_stories:
  - CFP-45
  - CFP-56
  - CFP-299
  - CFP-450  # Amendment 4 carrier (PAT consolidation)
  - CFP-596  # Amendment 5 carrier (story-init workflow cross-repo write mandate)
related_adrs:
  - ADR-009
  - ADR-012
  - ADR-017  # Amendment 1 carrier
  - ADR-041  # Amendment 2 doc-locations.yaml cross-ref
  - ADR-058  # is_transitional + 해소 기준 mandate (본 ADR `is_transitional: false` 정합)
  - ADR-060  # evidence-enforceable framework (Amendment 5 mechanical_enforcement_actions[] 연동)
  - ADR-066  # Amendment 5 PAT scope normative minimum cross-ref
mechanical_enforcement_actions:
  - action: story-init-cross-repo-write
    status: warning
    target_section: §결정 3 (Amendment 5 supersede — destination-ownership semantics)
    progress_note: "Amendment 5 (CFP-596) carrier. workflow story-init.yml 의 codeforge family detection branch + internal-docs cross-repo write 본문 동작이 §결정 3 의 destination-ownership semantics 의 mechanical enforcement. evidence-checks-registry warning tier entry 'story-init-cross-repo-write' 는 Phase 2 carrier (CFP-596 Phase 2 PR 안 등록). detect_command = workflow run conclusion + cross-repo Story file existence verification 가능 (별 lint carrier 가능)."
is_transitional: false
---

## 상태

Adopted (2026-04-30) — CFP-45 PR-I 머지 시점.

**Amendment 1 (2026-05-01) — CFP-56**: Brainstorming/writing-plans skill override path enforcement 정책을 ADR-017로 추가. `docs/superpowers/specs/**`와 `docs/superpowers/plans/**`가 plugin repo PR에 나타나면 CI가 fail-closed 하며, internal-docs 경로가 authoritative artifact lane이다. 검사 로직은 `scripts/check-dogfood-artifact-paths.sh`, CI는 `.github/workflows/dogfood-artifact-paths.yml` (template: `templates/github-workflows/dogfood-artifact-paths.yml`).

**Amendment 3 (2026-05-09) — CFP-299**: `docs/domain-knowledge/` cross-cutting pattern doc 작성 표준 추가. 신규 pattern doc 은 implementation-ready pseudocode (`## Pseudocode` 섹션) + edge case table (`## Edge Cases`, 최소 3 entry) 필수. 소급 재작성 면제 (단 기존 파일 수정 시 의무 적용). 상세는 본 ADR 말미 Amendment 3 절.

**Amendment 4 (2026-05-12) — CFP-450**: codeforge-internal-docs visibility = PRIVATE 명문화 + 단일 PAT `CODEFORGE_CROSS_REPO_PAT` consolidation. cross-repo internal-docs read 가 필요한 모든 wrapper workflow 는 동일 secret 재사용 (신규 secret 도입 금지). 상세는 본 ADR 말미 Amendment 4 절.

**Amendment 5 (2026-05-13) — CFP-596**: §결정 3 의 "Story workflow Action 위치 = internal-docs 측" **location-ownership semantics** 를 **destination-ownership semantics** 로 명시적 supersede. Story file destination SSOT = internal-docs 측 (§결정 1 정합), Action runtime location = wrapper repo (Issue Form trigger surface 유지, cross-repo push 책임). carrier workflow = `story-init.yml` (codeforge family detection branch + internal-docs cross-repo write 도입). Amendment 4 §결정 2 PAT consolidation 정합 (`CODEFORGE_CROSS_REPO_PAT` 재사용). `mechanical_enforcement_actions[]` row `story-init-cross-repo-write` (warning tier, Phase 2 carrier). 상세는 본 ADR 말미 Amendment 5 절.

## 컨텍스트

ADR-009 ζ arc 가 wrapper-only decomposition 으로 agent code 분리 완료. 그러나 dogfood artifacts (specs / plans / retros / stories / change-plans) 는 7 plugin repo 에 잔류 — plugin install footprint 부담 (wrapper 단독 1.5 MB / 78 file).

Plugin install mechanism = git clone of whole repo. plugin.json 에 `files` filter 부재. dogfood artifact 가 사용자 머신에 모두 다운로드.

CFP-44 (wrapper CLAUDE.md compression) 직후 사용자 진단:

> "codeforge 플러그인 계열의 변경에 대해서는 설계문서와 superpowers를 보존하지 않기로 하자. plugin이 너무 무거워진다."

Codex (gpt-5.4) 3 회 상담 후 (C) Aggressive scope + hybrid Action placement + bidirectional Issue↔Story binding 결정.

## 결정

7 plugin repo (mclayer/plugin-codeforge + mclayer/plugin-codeforge-{review, pmo, requirements, test, develop, design}) 의 dogfood artifacts 는 단일 monorepo `mclayer/codeforge-internal-docs` (Public) 보유:

1. **Plugin repo 잔류**: runtime SSOT (CLAUDE.md / playbook / ADR / inter-plugin-contracts / templates / scripts / agents / presets)
2. **Internal-docs 보유**: specs / plans / retros / stories / change-plans (7 plugin family folder × 5 subdir)
3. **Story workflow Action** (4종) 위치: internal-docs 측 (story-owned). plugin-side 는 phase-gate-mergeable cross-repo validation 만
4. **Phase 1 PR** = internal-docs (Story §1-7 + change-plan + ADR draft). **Phase 2 PR** = plugin repo (코드 변경). **§8-11 commit** = internal-docs
5. **Issue ↔ Story binding** (bidirectional): plugin repo Issue body `story_uri:` + Story file frontmatter `story_issues: [{repo, number}]`
6. **Cross-repo credential**: GitHub App (mclayer org-level) — fail-closed 시 명확한 error + admin override 절차
7. **History rewrite** = 별도 후속 CFP (CFP-45 는 working tree cleanup 까지)

## 결과

**달성**:
- Plugin install footprint 절감 — wrapper 1.5 MB → ~1 MB working tree (history 잔존)
- Dogfood artifact 단일 search surface (cross-plugin CFP 추적 용이)
- Plugin repo PR diff 가 순수 code change — dogfood noise 제거
- ADR-013 = future drift detection anchor

**비용**:
- Cross-repo Plugin PR mergeability 가 internal-docs / App credential 의존 — outage 시 unmergeable risk
- 78 file (wrapper 단독) + 6 lane plugin 추가 file 의 git history 손실 (cross-repo simple copy migration)
- Skill default override 가 신뢰 기반 (자동 enforcement 없음 — CLAUDE.md policy 명시)

**검증**:
- 7 plugin repo main 에서 docs/{superpowers, stories, retros, change-plans}/ 부재
- CLAUDE.md 에 internal-docs pointer + ADR-013 inline summary
- Internal-docs 에서 4 Action workflow registered + cross-repo App credential 가용

## 거부된 대안

- **(B) Standard scope** (stories/change-plans 잔류) — Codex 1차 권고. 사용자 (C) override 로 reject — Action restructure 필수 전제로 진행
- **Per-plugin internal-docs (7개)** — ownership 명확하지만 cross-plugin CFP 추적 어려움. 단일 monorepo 우위
- **Branch archive** (main 만 깔끔, archive branch) — future CFP 위치 모호 + clone 시 archive 미노출
- **History rewrite (filter-repo)** — SHA invalidation + open PR base 깨짐 + forks/cache 충격. Codex 명시 reject (별도 후속 CFP)
- **GitHub App scope 광범** (write to all repos) — 보안 surface 확대. 최소 권한 원칙 (Issues write / PRs read / Contents read)

## 해소 기준

N/A — permanent policy



```
Before (CFP-45 결정 전):
mclayer/plugin-codeforge (wrapper)
├── docs/superpowers/specs/         # ← MOVE
├── docs/superpowers/plans/         # ← MOVE
├── docs/retros/                    # ← MOVE
├── docs/stories/                   # ← MOVE
├── docs/change-plans/              # ← MOVE
├── docs/adr/                       # KEEP
├── docs/inter-plugin-contracts/    # KEEP
├── docs/orchestrator-playbook.md   # KEEP
├── templates/                      # KEEP
├── scripts/                        # KEEP
└── .github/workflows/              # 4 Action MOVE, phase-gate UPDATE

(6 lane plugins: 동일 패턴)

After (CFP-45 머지 후):
mclayer/codeforge-internal-docs (NEW)
├── wrapper/
│   ├── specs/, plans/, stories/, change-plans/, retros/
├── review/, pmo/, requirements/, test/, develop/, design/  (동일 구조)
├── .github/workflows/  (4 story-owned Actions)
├── .github/ISSUE_TEMPLATE/  (story.yml + bug.yml + audit.yml)
└── CLAUDE.md  (internal-docs minimal)

mclayer/plugin-codeforge (wrapper, post-CFP-45)
├── docs/adr/ (+ ADR-013 NEW)        # KEEP + ADR-013
├── docs/inter-plugin-contracts/     # KEEP
├── docs/orchestrator-playbook.md    # KEEP
├── templates/, scripts/             # KEEP
├── CLAUDE.md (Dogfood policy rewrite + ADR-013 inline summary)
└── .github/workflows/phase-gate-mergeable.yml (cross-repo via App)
```

## Amendment 2 (2026-05-08) — CFP-276 — EPIC-RESULTS classification + Doc Location Registry 정합

### 컨텍스트

[Issue #276](https://github.com/mclayer/plugin-codeforge/issues/276) 검토 중 발견:
- EPIC-RESULTS-`<KEY>`.md 가 codeforge dogfood 시 `<internal-docs>/<plugin-folder>/retros/` 사용 (실제 4 file 존재). 본 ADR §결정 의 dogfood subdir 5종 (`specs/plans/retros/stories/change-plans`) 중 `retros/` 가 EPIC-RESULTS 도 포괄함이 미문서화 → 인지 drift 위험.
- Codex round 1 (gpt-5.5 high) 검토 verdict: EPIC-RESULTS = retro-like artifact (Epic close evidence aggregate — outcome / gate / CI / follow-up 집계, 기능적으로 retro).

### 결정

EPIC-RESULTS-`<EPIC_KEY>`.md 는 codeforge family dogfood 시 `<internal-docs>/<plugin-folder>/retros/EPIC-RESULTS-<EPIC_KEY>.md` 에 위치한다 — 새 subdir 카테고리 추가 없이 기존 `retros/` 재사용. 본 결정의 machine-readable SSOT = [`docs/doc-locations.yaml`](../doc-locations.yaml) `epic_results` row의 `dogfood` variant ([ADR-041](ADR-041-doc-location-registry.md)).

### 결과

- Issue #276 의 "모순 2 (codeforge 자체 dogfood drift)" = drift 가 아닌 ADR-013 logical 결과로 명문화
- 향후 audit 시 인지 drift 차단
- File 이동 없음 (현재 4 file 이미 정합)

## Amendment 3 (2026-05-09) — CFP-299 — domain-knowledge pattern doc authoring standard

### 컨텍스트

[Issue #314](https://github.com/mclayer/plugin-codeforge/issues/314) 에서 식별:
- `docs/domain-knowledge/` 의 cross-cutting pattern doc 이 implementation-ready pseudocode 작성 의무를 갖지 않았음.
- 초기 pattern doc (`race-condition-handling-pattern.md`) 작성 시 pseudocode 가 conceptual-level 에 머물러 implementor 가 edge case 를 직접 추론해야 했음.
- Pattern doc 의 목적 — 재현 가능한 구현 지식 전달 — 이 개념 수준 설명만으로는 달성되지 않음.

ADR-013 은 plugin repo 에 잔류하는 runtime SSOT (`docs/domain-knowledge/**` 포함) 의 위치 policy 를 다루지만, 품질 기준은 미정의였음.

### 결정

`docs/domain-knowledge/` 하위 cross-cutting pattern doc (새로 작성하는 파일 및 기존 파일의 실질적 수정 시) 에 다음 두 섹션을 필수로 포함한다:

**1. `## Pseudocode` 섹션 — implementation-ready 수준 의무**

구체적으로 요구하는 내용:
- **변수명 구체화**: `x`, `item` 같은 generic 이름 금지 — 도메인 의미가 드러나는 명칭 사용 (예: `lock_file_path`, `sha256_digest`, `tmp_path`).
- **에러 핸들링 명시**: 예외 종류·복구 경로·fallback 동작을 코드 흐름 안에서 표현. `try/except ExceptionType` 수준으로 구체화.
- **루프 경계 명시**: 재시도 루프는 최대 횟수(`MAX_RETRIES`) 또는 timeout 경계 명시. 무한 루프 형태 금지.
- **원자적 연산 주석**: OS-level atomic 보장이 필요한 지점 (`atomic rename`, `O_EXCL open`, `fcntl lock`) 은 주석으로 명시.
- **개념 흐름만으로 불충분**: "acquire lock → write → release" 수준의 고수준 설명은 pseudocode 섹션으로 부적합. 상세는 아래 예시 참조.

```python
# GOOD — implementation-ready
MAX_RETRIES = 5
LOCK_TIMEOUT_SEC = 10.0

def append_entry(jsonl_path: Path, entry: dict) -> None:
    lock_path = jsonl_path.with_suffix(".lock")
    tmp_path = jsonl_path.with_suffix(".tmp")
    start = time.monotonic()
    for attempt in range(MAX_RETRIES):
        try:
            fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)  # atomic O_EXCL
        except FileExistsError:
            if time.monotonic() - start > LOCK_TIMEOUT_SEC:
                raise TimeoutError(f"Lock not acquired within {LOCK_TIMEOUT_SEC}s")
            time.sleep(0.1 * (2 ** attempt))  # exponential backoff
            continue
        try:
            line = json.dumps(entry, ensure_ascii=False) + "\n"
            tmp_path.write_text(line, encoding="utf-8")
            os.replace(tmp_path, jsonl_path)  # atomic rename — POSIX guarantee
        finally:
            os.close(fd)
            lock_path.unlink(missing_ok=True)
        return
    raise RuntimeError(f"Failed to append after {MAX_RETRIES} attempts")

# BAD — conceptual only (not acceptable in ## Pseudocode)
# acquire lock
# write entry
# release lock
```

**2. `## Edge Cases` 섹션 — 최소 3 entry 테이블 의무**

pattern 당 최소 3개의 edge case 를 다음 컬럼으로 기술:

| Edge Case | 발생 조건 | 탐지 방법 | 처리 전략 |
|---|---|---|---|
| (예시) SHA 충돌 | 동시 write 시 서로 다른 content 가 동일 SHA 생성 | 파일 내용 비교 | content hash 외 타임스탬프 + PID 조합으로 uniqueness 강화 |
| (예시) 빈 파일 초기화 race | 두 프로세스가 동시에 파일 최초 생성 시도 | O_EXCL open 결과 | 패배 프로세스는 retry — winner 가 생성한 파일에 append |
| (예시) atomic rename 실패 | 크로스-디바이스 rename (tmp 와 target 가 다른 마운트 포인트) | OSError: Invalid cross-device link | tmp 를 target 와 동일 디렉토리에 생성 또는 shutil.move fallback |

entry 수 3개는 최소값 — pattern 의 복잡도에 비례해 추가 권장.

### 소급 적용 범위

- **신규 pattern doc**: 본 amendment 가 merge 된 이후 새로 생성하는 `docs/domain-knowledge/**/*.md` 파일 중 pattern/guide/recipe 성격의 파일에 즉시 적용.
- **기존 pattern doc 수정 시**: 파일을 실질적으로 수정(내용 추가·삭제·재구성)할 경우 해당 PR 에서 두 섹션 추가 의무. 단순 오탈자·링크 수정은 면제.
- **기존 파일 소급 재작성 면제**: 수정 없이 그대로 두는 기존 파일은 소급 적용 없음 (예: `race-condition-handling-pattern.md` 현 상태 유지 허용).

### 결과

- 신규 pattern doc 이 implementor 가 edge case 추론 없이 직접 사용 가능한 수준의 품질 기준을 갖춤.
- Retro 발견 사항 (Issue #314) 이 ADR 수준 의무로 상향 — 향후 design/code review 에서 pattern doc PR 심사 기준으로 활용 가능.
- Lint 자동화는 CFP-299 scope 밖 — 향후 `check-doc-section-schema.sh` 확장 시 `## Pseudocode` + `## Edge Cases` 섹션 존재 여부 검사 추가 가능 (별도 CFP).

## Amendment 4 (2026-05-12) — CFP-450 — internal-docs visibility=PRIVATE 명문화 + 단일 PAT (CODEFORGE_CROSS_REPO_PAT) 재사용 정책

### 컨텍스트

CFP-393 (#398, merged) §11 follow-up #2 가 식별: KPI workflow (`templates/github-workflows/rate-limit-fallback-kpi.yml`) 의 `clone_internal` step 가 `mclayer/codeforge-internal-docs` 를 default `GITHUB_TOKEN` 으로 clone — comment "public repo 가정" 명시. 본 Amendment 작성 시점 audit (2026-05-12) 에서 codeforge-internal-docs visibility = **PRIVATE** 확인 (`gh repo view mclayer/codeforge-internal-docs --json visibility`). 

§결정 1 본문 "(Public)" 어휘 와 actual visibility drift — phase-gate-mergeable workflow (CFP-63 fix) 는 이미 `CODEFORGE_CROSS_REPO_PAT` secret 으로 동작 중이라 phase-gate evidence success. KPI workflow 는 default GITHUB_TOKEN 가정으로 fail risk 잔존.

### 결정

1. **Visibility 명문화**: codeforge-internal-docs = PRIVATE (2026-05-12 audit). 본 Amendment 가 §결정 1 의 "(Public)" 어휘 supersede — 본문 inline edit 미수행 (anti-drift, historic-preserving), 본 Amendment 가 신규 SSOT.
2. **단일 PAT scope consolidation (Option B)**: cross-repo internal-docs read 가 필요한 모든 wrapper workflow 는 **`CODEFORGE_CROSS_REPO_PAT` 단일 secret 재사용**. 적용 영역:
   - `phase-gate-mergeable.yml` (CFP-63 fix, 기존)
   - `rate-limit-fallback-kpi.yml` (CFP-450 본 Amendment, 신규)
   - 향후 internal-docs read 가 필요한 workflow 모두 동일 secret 재사용 (신규 secret 도입 금지 — rotation policy 단순화).
3. **PAT permission scope**: `repo:read` (private internal-docs read only). 신규 PAT 도입 시 별도 ADR 발의 의무 (rotation / scope expansion / shared secret 영역 변경).
4. **Fallback 정책 (graceful degradation)**: PAT secret 부재 시 → GITHUB_TOKEN fallback → private repo 환경에서 clone fail → `partial_data: true` sentinel (현 aggregator 동작 정합). workflow run = success (graceful), `codeforge-kpi-infra-error` label Issue 자동 발의 (CFP-451 정합).
5. **Consumer overlay 영향**: consumer 측 codeforge plugin install 시 본 Amendment 무관 — codeforge-internal-docs 는 codeforge family dogfood 전용, consumer project 와 무관 (ADR-013 §결정 4 정합 — internal-docs 는 codeforge family only).

### 위배 시 처리

- PAT secret 미부착 wrapper workflow 에서 internal-docs clone fail → `partial_data: true` sentinel + `codeforge-kpi-infra-error` Issue auto-open (CFP-451 정합) → oncall 조치 (PAT 재발급 / scope 확인 / rotation).
- 신규 wrapper workflow 가 internal-docs read 필요 시 본 Amendment 의무 — 신규 secret 도입 금지, `CODEFORGE_CROSS_REPO_PAT` 재사용. 위반 시 PR review 단계 차단 (별도 lint carrier 후행).

### 결과

- KPI workflow 가 internal-docs PRIVATE 상태에서 정합 동작 (PAT 사용 + fallback graceful).
- 단일 PAT scope consolidation 으로 rotation overhead 최소화 (codeforge family ops 부담 감소).
- visibility drift 해소 — ADR-013 §결정 1 의 "(Public)" 가정이 더 이상 신뢰 source 아님 (본 Amendment 가 supersede SSOT).

### 관련 파일

- [templates/github-workflows/rate-limit-fallback-kpi.yml](../../templates/github-workflows/rate-limit-fallback-kpi.yml) — KPI workflow PAT 사용 영역
- [templates/github-workflows/phase-gate-mergeable.yml](../../templates/github-workflows/phase-gate-mergeable.yml) — phase-gate cross-repo Story fetch (선례)
- CFP-450 Story file (`mclayer/codeforge-internal-docs/wrapper/stories/CFP-450.md`)

## Amendment 5 (2026-05-13) — CFP-596 — Story-init workflow cross-repo write 의무 codification (location-ownership → destination-ownership supersede)

### 컨텍스트

CFP-596 (본 Amendment carrier) 가 감사한 systemic failure 영역:

- wrapper repo `mclayer/plugin-codeforge` 의 `story-init.yml` workflow 최근 30 run = 19 cancelled + 10 failure + 0 success `[verified]` (gh run list direct query).
- failure 영역 = workflow 본문 line 164 `mkdir -p docs/stories` + line 226 `git add docs/stories/${KEY}.md` 가 wrapper `.gitignore` (line 35-37 `docs/stories/` ignore) 와 conflict → `git add` exit 1.
- 본 .gitignore = ADR-013 §결정 1 (Plugin repo 잔류 = runtime SSOT 만, dogfood artifacts = internal-docs SSOT) 의 mechanical enforcement.
- workflow header comment (line 4-6) "Consumer-distributable single-repo flavor (CFP-65 / F2 Phase 1)" + "codeforge family monorepo flavor 는 internal-docs 별도 유지" 로 codeforge family detection branch 부재 자체를 인정 — comment-implementation drift.
- 본 §결정 3 원문 = "Story workflow Action **위치** (location): internal-docs 측 (story-owned). plugin-side 는 phase-gate-mergeable cross-repo validation 만" — 즉 wrapper repo 가 `story-init.yml` 을 보유한 자체가 §결정 3 위반 (잔류).
- 6 lane plugin (`codeforge-{requirements,design,review,develop,test,pmo}`) 모두 `story-init.yml` 부재 `[verified]` (6 worktree 직접 inspection) — sibling 6 plugin 은 이미 정합 (workflow 없음), wrapper 만 위반.

### 결정

#### 결정 1 — Location semantics 재정의 (explicit supersede)

§결정 3 의 "Story workflow Action **위치** (location)" semantics 를 다음 형태로 **명시적 supersede**:

- **Story file destination SSOT** = internal-docs 측 (§결정 1 정합, invariant).
- **Action runtime location** = wrapper repo 측 (Issue Form trigger surface 유지 — `on: issues: types: [opened, labeled]` 가 wrapper repo Issue 발화 catch). wrapper Actions runner 가 cross-repo push 책임.

본 supersede 는 §결정 3 의 intent (Story file destination = internal-docs) 를 보존하면서 "Action 위치" 영역만 재정의. literal §결정 3 ("Action 위치 = internal-docs") 은 본 Amendment 5 이후 더 이상 신뢰 source 아님 (anti-drift, historic-preserving 정합 — 본 Amendment 가 신규 SSOT).

#### 결정 2 — Cross-repo write 패턴 (workflow story-init.yml 영역)

wrapper repo `story-init.yml` workflow 가 codeforge family detection branch 분기 도입:

- **detection sentinel** = project.yaml `project.name` regex match `^codeforge` (wrapper `codeforge` + 6 lane `codeforge-{lane}` 7 plugin 모두 cover).
- **codeforge family branch**: internal-docs (`mclayer/codeforge-internal-docs`) 측 cross-repo write — REST API contents PUT endpoint + branch refs create + cross-repo PR create.
- **generic consumer branch** (`project.name != codeforge*`): 기존 local `mkdir -p docs/stories` + `git add` + `git commit` + `git push` 보존 (consumer 영향 0).

**Plugin folder mapping** (codeforge family branch):
- `codeforge` → `wrapper/`
- `codeforge-requirements` → `requirements/`
- `codeforge-design` → `design/`
- `codeforge-review` → `review/`
- `codeforge-develop` → `develop/`
- `codeforge-test` → `test/`
- `codeforge-pmo` → `pmo/`

Bash logic = `folder=$(grep "^  name:" "$cfg" | awk '{print $2}' | sed 's/^codeforge-//;s/^codeforge$/wrapper/')`.

#### 결정 3 — PAT 재사용 (Amendment 4 §결정 2 정합)

cross-repo write 영역에서 `CODEFORGE_CROSS_REPO_PAT` 단일 secret 재사용 — Amendment 4 §결정 2 consolidation 정합. 신규 cross-repo secret 도입 금지.

**PAT scope normative minimum** (ADR-066 §결정 2 verbatim):
- `repo:read` — branch query (existence_check)
- `repo:write` — branch create + contents PUT + PR create
- `metadata:read` — basic repo access

#### 결정 4 — 거부된 대안

- **(a-bis) Action runtime 도 internal-docs 로 이전** (literal §결정 3 정합) — 거부 사유: wrapper Issue Form trigger surface 손실. `on: issues` 가 internal-docs 측 trigger 부재 → 별 trigger 발의 부담. 본 Amendment 5 의 destination semantics 가 우회.
- **(b) workflow 폐지 + manual create** — 거부 사유: 사용자 사전 채택 옵션 (a) 충돌. wrapper Issue Form 자동 발화 흐름 손실.
- **(c) wrapper repo 자체 dogfood-storage 도입** — 거부 사유: §결정 1 invariant 위반 (per-repo dogfood storage 부활 = ADR-013 본래 목적 무효화).
- **(d) `dogfood_out: true` boolean field 신설** (옵션 (B)) — 거부 사유: project-config-schema 확장 + consumer onboarding cost. `project.name` regex match (옵션 (A)) 가 schema 변경 0. 5+ Story 후 retro 재검토 가능 (out-of-scope).

#### 결정 5 — 잔여 #591-#595 처리 (CFP-510 retro carrier)

본 Amendment 5 merge 후 carrier workflow 적용 직후, 5 잔여 Issue (`#591`, `#592`, `#593`, `#594`, `#595`) 의 Story file 을 internal-docs `wrapper/stories/CFP-{591..595}.md` 에 backfill. 2 옵션:

- **(a) workflow rerun** via Issue label re-toggle — `phase:요구사항` label re-toggle → workflow `on: issues: types: [labeled]` 발화 → existence_check internal-docs branch 부재 → cross-repo write 진행. idempotent 정합.
- **(b) manual bash script** — `scripts/backfill-stories-cfp-591-595.sh` (CFP-596 Phase 2 PR 동반). manual control.

권고 = (a) workflow rerun (cross-repo workflow 동작 검증 + manual script 부담 회피).

#### 결정 6 — 6 lane plugin sibling explicit no-op decision (propagation scope boundary)

본 Amendment 5 carrier workflow (`story-init.yml` codeforge family detection branch + internal-docs cross-repo write) 는 **wrapper repo 단독 적용**. 6 lane plugin sibling (`codeforge-{requirements,design,review,develop,test,pmo}`) 측 workflow 신설 의무 **0** — explicit no-op decision.

근거:

1. 6 sibling 의 현 상태 = `story-init.yml` workflow 부재 (verified, 6 worktree direct inspection per CFP-596 Story §2.3). invariant A (`.gitignore docs/stories/` ignore) mechanical enforcement 이미 정합 — workflow 부재 = local write attempt 부재 = `.gitignore` conflict 발화 0.
2. wrapper repo systemic failure (30 run = 19 cancelled + 10 failure + 0 success per CFP-596 Story §1 verbatim) 해소 = 본 Amendment 5 motivation. 6 sibling 의 manual flow → automated flow upgrade 는 별 motivation 영역 (사용자 directive / 6 sibling retro 발화 부재).
3. 6 sibling 의 Issue Form 자동 발화 의무 발화 시점 (별 motivation) 시 별 CFP carrier — 본 Amendment 5 scope 외.

본 결정 6 = propagation scope **explicit boundary** 결정. silent omission 차단 — `boundary_completeness_self_check_passed` (CFP-596 Change Plan §13.2) I-2 cross-module propagation completeness PASS rationale (propagation domain = {wrapper} singleton).

§결정 2 의 Plugin folder mapping 표 (`codeforge-requirements` → `requirements/` 등) 는 **forward-compatibility 보존** — 향후 별 CFP carrier 가 6 sibling 측 workflow 신설 시 mapping 표 재사용 가능. 본 Amendment 5 scope = wrapper 만 active path, 6 sibling = inactive mapping (reserved).

#### 결정 7 — Two-stage existence_check + automated reconcile path (idempotency 강화)

§결정 2 의 cross-repo write 영역 idempotency 보장은 **two-stage check** 의무:

- **Stage 1 — Remote branch existence**: `gh api repos/${TARGET_REPO}/branches/feat/${KEY}-${SLUG}` HTTP 200 OK
- **Stage 2 — Story file existence on branch**: `gh api repos/${TARGET_REPO}/contents/${dogfood_folder}/stories/${KEY}.md?ref=feat/${KEY}-${SLUG}` HTTP 200 OK

**Decision matrix**:

| Stage 1 (branch) | Stage 2 (file) | 결정 |
|---|---|---|
| present | present | idempotent skip |
| present | absent | **automated reconcile** (contents PUT 단일 step + PR existence check + 정상 후속 step) |
| absent | (skip) | first firing 진행 |
| 4xx/5xx | (skip) | fail-closed |

본 결정 7 = Disconnect edge case (runner 단절 중 branch created + contents PUT 미완료 partial state) 의 manual reconcile 의무 영역 elimination. CI/CD 자동성 완전 회복.

근거 (Codex proactive check #2 finding F-003 inline FIX):
- Single-stage check (branch-only) 시 partial state → 다음 firing 의 branch existence 가 true → skip → silent loss → manual contents PUT 의무
- Two-stage check 시 partial state → Stage 1 true + Stage 2 false → `auto_recovered=true` notice + contents PUT 단일 step + 후속 PR create 분기 (PR 존재 여부 check + skip 또는 정상 create)

**적용 영역**: codeforge family branch 안 active (Amendment 5 §결정 2 cross-repo write 영역). consumer branch (generic consumer) = single-stage 보존 (consumer 영향 0).

**Latency 영향**: +1 API call (Stage 2 query) ~ +200-500ms — workflow runtime ~30s 대비 1-2% 영향 (무시할 수준). rate-limit 한도 (5000 req/hour PAT) 영향 무시할 수준.

상세 implementation = CFP-596 Change Plan §3.5 SSOT.

### 위배 시 처리

- wrapper Issue Form 제출 시 workflow run conclusion = fail/cancelled (cross-repo write step 영역) → `gh run view --log` 로 error message 식별 → PAT scope / internal-docs visibility / GitHub API rate-limit 영역 진단 후 fix.
- 6 lane plugin Issue Form 제출 시 = 본 Amendment 5 scope 외 (workflow 부재 = manual flow 보존, 위배 영역 부재).
- PAT scope 불충분 시 (`repo:write` 부재) → workflow exit 1 + error message `lacks repo:write scope — ADR-066 §결정 2 참조` → ADR-066 §결정 3 rotation 절차 실행 의무.
- consumer (비-codeforge) project 측에서 본 cross-repo write 활성화 시 — `project.name != codeforge*` 분기 보장 → consumer 측 활성화 발생 0 (AC-5 정합).

### 결과

- wrapper repo 의 `story-init.yml` workflow systemic failure 해소 (cross-repo write 채택).
- ADR-013 §결정 3 의 location-ownership drift (workflow yml 잔류) 가 destination-ownership semantics 로 명시적 supersede — 향후 audit 시 인지 drift 차단.
- §결정 1 invariant (Plugin repo 잔류 = runtime SSOT 만) 강화 — workflow 가 wrapper repo `docs/stories/` 영역 write 시도 0 건 (생성 destination = internal-docs).
- Amendment 4 §결정 2 PAT consolidation 의 첫 production write workflow 적용 — `CODEFORGE_CROSS_REPO_PAT` 사용 영역 = read (KPI / phase-gate) + write (본 Amendment 5 carrier) 양 영역 cover.
- Consumer (비-codeforge) project 영향 0 — `project.name != codeforge*` 분기 보장.
- 6 lane plugin Story-init flow 확장 영역 = out-of-scope (각 lane plugin 의 workflow 부재 정합, 후속 carrier 가능).

### 관련 파일

- [CFP-596 Change Plan](https://github.com/mclayer/codeforge-internal-docs/blob/main/wrapper/change-plans/2026-05-13-cfp-596-story-init-dogfood-out.md) — 본 Amendment 5 carrier Change Plan
- [CFP-596 Story file](https://github.com/mclayer/codeforge-internal-docs/blob/main/wrapper/stories/CFP-596.md) — 본 Amendment 5 carrier Story
- [`templates/github-workflows/story-init.yml`](../../templates/github-workflows/story-init.yml) — Amendment 5 carrier workflow (Phase 2 PR)
- [`.github/workflows/story-init.yml`](../../.github/workflows/story-init.yml) — 위와 byte-identical (wrapper distribution 관습)
- [ADR-066](ADR-066-pat-rotation-policy.md) — PAT scope normative minimum + rotation 절차 (Amendment 5 carrier prerequisite)
- [ADR-040 Amendment 3](ADR-040-worktree-convention.md) — `mechanical_enforcement_actions[]` field SSOT (본 ADR frontmatter 적용 영역)

## 관련 파일

- [CFP-45 spec](https://github.com/mclayer/codeforge-internal-docs/blob/main/wrapper/specs/2026-04-30-cfp-45-dogfood-out-restructure-design.md) — parent
- [ADR-009 Wrapper-only Decomposition](ADR-009-wrapper-only-decomposition.md) — ζ arc parent
- [ADR-012 Wrapper CLAUDE.md SSOT Boundary](ADR-012-wrapper-claudemd-ssot-boundary.md) — direct predecessor
- [mclayer/codeforge-internal-docs](https://github.com/mclayer/codeforge-internal-docs) — NEW dogfood monorepo
- [ADR-017 Skill override path enforcement](ADR-017-skill-override-path-enforcement.md) — Amendment 1 carrier
- `scripts/check-dogfood-artifact-paths.sh` — path scan lint script
- `templates/github-workflows/dogfood-artifact-paths.yml` — CI workflow template
- `.github/workflows/dogfood-artifact-paths.yml` — active workflow (wrapper repo)
