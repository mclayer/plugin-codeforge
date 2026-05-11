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
is_transitional: false
---

## 상태

Adopted (2026-04-30) — CFP-45 PR-I 머지 시점.

**Amendment 1 (2026-05-01) — CFP-56**: Brainstorming/writing-plans skill override path enforcement 정책을 ADR-017로 추가. `docs/superpowers/specs/**`와 `docs/superpowers/plans/**`가 plugin repo PR에 나타나면 CI가 fail-closed 하며, internal-docs 경로가 authoritative artifact lane이다. 검사 로직은 `scripts/check-dogfood-artifact-paths.sh`, CI는 `.github/workflows/dogfood-artifact-paths.yml` (template: `templates/github-workflows/dogfood-artifact-paths.yml`).

**Amendment 3 (2026-05-09) — CFP-299**: `docs/domain-knowledge/` cross-cutting pattern doc 작성 표준 추가. 신규 pattern doc 은 implementation-ready pseudocode (`## Pseudocode` 섹션) + edge case table (`## Edge Cases`, 최소 3 entry) 필수. 소급 재작성 면제 (단 기존 파일 수정 시 의무 적용). 상세는 본 ADR 말미 Amendment 3 절.

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

## 관련 파일

- [CFP-45 spec](https://github.com/mclayer/codeforge-internal-docs/blob/main/wrapper/specs/2026-04-30-cfp-45-dogfood-out-restructure-design.md) — parent
- [ADR-009 Wrapper-only Decomposition](ADR-009-wrapper-only-decomposition.md) — ζ arc parent
- [ADR-012 Wrapper CLAUDE.md SSOT Boundary](ADR-012-wrapper-claudemd-ssot-boundary.md) — direct predecessor
- [mclayer/codeforge-internal-docs](https://github.com/mclayer/codeforge-internal-docs) — NEW dogfood monorepo
- [ADR-017 Skill override path enforcement](ADR-017-skill-override-path-enforcement.md) — Amendment 1 carrier
- `scripts/check-dogfood-artifact-paths.sh` — path scan lint script
- `templates/github-workflows/dogfood-artifact-paths.yml` — CI workflow template
- `.github/workflows/dogfood-artifact-paths.yml` — active workflow (wrapper repo)
