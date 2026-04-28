# CFP-27 Phase 0b — Lint 강화 + CI Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** CFP-26이 도입한 owner-direct write 4 path의 frontmatter·섹션 schema를 lint로 강제 (warning 모드 시작) + CFP-26 invariant lint를 CI에 통합 + 부재했던 owner doc 템플릿(domain-knowledge / retro) 신설 + check-write-permission-redistribution.sh awk 코드 정리.

**Architecture:** 신규 2 lint script(`scripts/check-doc-frontmatter.sh` · `scripts/check-doc-section-schema.sh`) + 신규 2 template(`templates/{domain-knowledge,retro}.md`) + 기존 lint workflow(`.github/workflows/lint.yml`)에 3 새 job 추가(redistribution + frontmatter + section-schema). awk allow_block/deny_block 중복 함수는 1개 파라미터화 helper로 통합. 기존 documents (ADR · Change Plan · Retro)가 새 schema에 맞지 않더라도 warning 모드라 fail 없음 — CFP-28에서 strict 전환.

**Tech Stack:** Bash · Python (PyYAML for frontmatter parse) · GitHub Actions YAML.

---

## Spec 참조

본 plan은 [`docs/superpowers/specs/2026-04-28-docsagent-scope-reduction-and-review-extraction-design.md`](../specs/2026-04-28-docsagent-scope-reduction-and-review-extraction-design.md) **Phase 0b (CFP-27)** 만 구현. Phase 0c (CFP-28 dogfooding 검증) · Phase 1 (CFP-29 review extract) 는 별도 plan.

본 plan이 추가로 흡수하는 follow-up:

- CFP-26 code review minor: `check-write-permission-redistribution.sh` allow_block/deny_block 파라미터화 (Task 3)
- CFP-26 final review suggestion: redistribution lint CI integration (Task 6)

본 plan에서 **defer**:

- Story file (`docs/stories/<KEY>.md`) §1-§11 schema — 별도 CFP-27.5 (multi-writer + §10 FIX Ledger appendable 등 복잡성)
- 기존 ADR/Change Plan/Retro 파일의 frontmatter backfill — warning 모드라 lint 통과, CFP-28 dogfooding에서 strict 전환 시점에 backfill

## File Structure

| 파일 | 책임 | 변경 종류 |
|---|---|---|
| `templates/domain-knowledge.md` | DomainAgent owner doc 템플릿 (현 부재) | 신규 |
| `templates/retro.md` | PMOAgent owner doc 템플릿 (현 부재) | 신규 |
| `scripts/check-doc-frontmatter.sh` | 4 owner doc path frontmatter 필수 필드 검증 (warning) | 신규 |
| `scripts/check-doc-section-schema.sh` | 4 owner doc path 본문 섹션 헤딩 검증 (warning) | 신규 |
| `scripts/check-write-permission-redistribution.sh` | awk 중복 함수 파라미터화 | 정비 |
| `.github/workflows/lint.yml` | 3 새 job 추가 (redistribution + frontmatter + section-schema) | 정비 |
| `CLAUDE.md` | "## ADR" + "## Domain Knowledge" + "## docs/stories markdown 규약" 섹션에 CFP-27 lint enforcement 안내 | 정비 |
| `CHANGELOG.md` | v0.16.0 entry | 정비 |
| `.claude-plugin/plugin.json` | version 0.15.0 → 0.16.0 | 정비 |
| `docs/migration-guide.md` | v0.15 → v0.16 섹션 | 정비 |
| `docs/plugin-design.md` | Stage 1 history line v0.16 추가 | 정비 |

---

## Task 1: templates/domain-knowledge.md 신설

DomainAgent가 `docs/domain-knowledge/<area>/<topic>.md` 직접 write 시 따를 schema SSOT.

**Files:**
- Create: `templates/domain-knowledge.md`

- [ ] **Step 1: Write template content**

Create file `templates/domain-knowledge.md`:

```markdown
# Domain Knowledge 페이지 템플릿

DomainAgent가 `docs/domain-knowledge/<area>/<topic>.md` 직접 write 시 따르는 schema SSOT (CFP-26 Phase 0a 이후 owner direct write).

**사용 대상**: DomainAgent (생성·갱신 단독), DocsAgent (Story §3·§5 ADR·도메인 인용 처리 — 직접 write 안 함)

---

## 파일 위치

- **위치**: `docs/domain-knowledge/<area>/<topic>.md`. `<area>`는 consumer overlay가 정의 (예: `policies/`, `accounting/`, `auth/`)
- **계층**: 디렉토리 1-2단계 권장 (area / topic)
- **CODEOWNERS**: `docs/domain-knowledge/**` → `@org/domain-experts` 자동 review (consumer overlay가 매핑)

---

## Frontmatter (필수)

```yaml
---
title: <한 줄 제목>
area: <영역 — overlay에서 정의된 area 중 하나>
topic_slug: <kebab-case-slug>
status: draft | active | deprecated
sources:
  - "<원천 — 사용자 원문 / ADR / 코드 / 외부 표준 / 사내 위키 등>"
  - "<원천 2>"
related_adrs: [ADR-NNN, ADR-MMM]   # 도메인 결정과 연결되는 ADR
related_stories: [<KEY-N>, <KEY-M>] # 본 KB가 도출된 Story
updated: YYYY-MM-DD                 # 마지막 수정일 (DomainAgent가 갱신 시 업데이트)
---
```

---

## 본문 섹션 (고정 순서, 누락 시 lint warning)

```markdown
# <Area> · <Topic>

## 정의
용어·개념의 한 줄 정의 (사전식). 비즈니스 맥락 반영.

## 컨텍스트
이 지식이 왜 필요한가, 어디서 쓰이는가 — Story·ADR·코드·운영 사례 인용.

## 핵심 규칙 / 불변식 (invariant)
- 규칙 1 (예: "한 사용자는 동시에 1개 active 세션만 보유")
- 규칙 2

## 경계 / 예외
규칙이 적용되지 않는 케이스 — 명시적 carve-out.

## 관련 ADR / Story / 코드
- [ADR-NNN](../../adr/ADR-NNN-<slug>.md) — 결정 인용
- [Story <KEY>](../../stories/<KEY>.md) — 도출 Story
- 코드 경로 (consumer 기준 relative)

## 변경 이력
- YYYY-MM-DD: 초기 작성 (Story <KEY>)
- YYYY-MM-DD: 규칙 1 추가 (Story <KEY>)
```

---

## DomainAgent 작성 절차

```
1. consumer overlay에서 area 목록 확인 (`.claude/_overlay/project.yaml` 또는 docs/domain-knowledge 기존 디렉토리)
2. 적절한 area 선택, topic-slug 결정 (kebab-case)
3. `Write(docs/domain-knowledge/<area>/<topic>.md)` 호출, frontmatter + 본문 작성
4. Story file §3 "관련 ADR" 또는 별도 §5 "도메인 지식" 섹션에 링크 추가 — Orchestrator 경유 DocsAgent에 의뢰 (Story file은 multi-writer)
5. 기존 page 갱신 시 frontmatter `updated` 필드 + "변경 이력" 섹션 append
```
```

(end of template — note: outermost ``` are illustrative, the actual file content is the markdown body shown above)

- [ ] **Step 2: Verify file exists**

```bash
test -f templates/domain-knowledge.md && echo "EXISTS" || echo "MISSING"
```

Expected: `EXISTS`.

- [ ] **Step 3: Commit**

```bash
git add templates/domain-knowledge.md
git commit -m "feat(cfp-27): templates/domain-knowledge.md 신설 — DomainAgent owner doc schema SSOT

Phase 0b lint 강화 사전 작업 (1/2 신규 template).
CFP-26 Phase 0a부터 DomainAgent가 docs/domain-knowledge/** 직접 write —
schema SSOT가 부재하던 부분을 템플릿으로 명시화.

Frontmatter 필수: title / area / topic_slug / status / sources / related_adrs /
related_stories / updated. 본문 섹션 고정 순서: 정의 / 컨텍스트 / 핵심 규칙 /
경계·예외 / 관련 ADR·Story·코드 / 변경 이력.

CFP-27 lint(check-doc-frontmatter.sh + check-doc-section-schema.sh)가 본 schema를 warning 모드로 강제.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 2: templates/retro.md 신설

PMOAgent가 `docs/retros/<sprint>.md` 직접 write 시 따를 schema SSOT.

**Files:**
- Create: `templates/retro.md`

- [ ] **Step 1: Write template content**

Create file `templates/retro.md` with this content:

```markdown
# Retro 템플릿

PMOAgent가 `docs/retros/<sprint>.md` 직접 write 시 따르는 schema SSOT (CFP-26 Phase 0a 이후 owner direct write).

**사용 대상**: PMOAgent (Story 회고 + 세션 회고 + sprint close 통합 작성), Orchestrator (회고 trigger), DocsAgent (Story file §11 회고 pointer 미러링 — 직접 write 안 함)

---

## 파일 위치

- **위치**: `docs/retros/<YYYY-MM-DD>-<topic-slug>.md`. 날짜 prefix는 정렬 + 식별용
- **topic-slug**: kebab-case. 예: `marketplace-bootstrap-sprint`, `cfp-26-implementation`

---

## Frontmatter (필수)

```yaml
---
title: <한 줄 제목>
date: YYYY-MM-DD
sprint_period: "YYYY-MM-DD ~ YYYY-MM-DD"   # 단일 세션이면 같은 날짜 2번
cfp_keys: [CFP-NN, CFP-MM]                  # 본 retro가 다루는 CFP 목록
authors: [PMOAgent]                         # 작성 주체 (보조 author 있으면 추가)
related_stories: [<KEY-N>, <KEY-M>]        # 회고 대상 Story
sentinel_refs:
  - <prior retro file path>                # 직전 retro 또는 참고 retro
---
```

---

## 본문 섹션 (고정 순서, 누락 시 lint warning)

```markdown
# <Title>

기간: <sprint_period>
범위: <CFP 개수> CFP + <PR 개수> PR + <기타 — bootstrap·migration 등>
선행 retro: [<previous retro link>](<previous-retro-file>)

---

## §1 결과 (closure)

### 1.1 commit·PR
| Story / 작업 | PR | merge commit | 비고 |
|---|---|---|---|
| ... | ... | ... | ... |

### 1.2 lint·invariant 상태
| Lint | Status |
|---|---|
| ... | ... |

---

## §2 무엇이 잘 갔나 (kept)
- 항목 1 — 구체 evidence (commit·PR·Story 인용)
- 항목 2

## §3 무엇이 막혔나 (problem)
- 항목 1 — 구체 evidence
- 항목 2

## §4 다음에 할 일 (try)
- 항목 1 — 구체 행동·CFP 후보
- 항목 2

---

## §5 cross-Story 패턴 (해당 시)
복수 Story·CFP에서 반복 발견된 패턴 — 설계 지침 부재 신호. ADR 후보 발의 sentinel.

## §6 ADR 후보 발의 (해당 시)
- 후보 1: <제목> — 근거: §5 패턴 N건
- 후보 2: ...

---

## §7 토큰 예산 vs 실제 (해당 시)
세션 회고 통합 시. playbook §8.3 테이블 참조.

| 레인 | 예산 | 실제 | 차이 |
|---|---|---|---|
| ... | ... | ... | ... |

## §8 개선 제안 (3건 이하)
다음 세션·CFP에 반영 가능한 actionable 제안. 4건 이상 작성 금지 — focus 유지.

1. ...
2. ...
3. ...
```

---

## PMOAgent 작성 절차

```
1. Sprint·Story·세션 종료 trigger 시 Orchestrator가 PMOAgent 스폰
2. 본 에이전트가 `docs/retros/<YYYY-MM-DD>-<slug>.md` 직접 write (CFP-26 Phase 0a)
3. Story file §11 회고 pointer는 Orchestrator 경유 DocsAgent에 의뢰 (Story file은 multi-writer)
4. ADR 후보 발의 (§6) 있으면 Orchestrator 경유 ArchitectAgent에 ADR draft 작성 의뢰 (write queue type=adr-draft, status=Proposed) — CFP-27.5 시점 이후 ArchitectAgent direct write로 전환
```
```

- [ ] **Step 2: Verify file exists**

```bash
test -f templates/retro.md && echo "EXISTS" || echo "MISSING"
```

- [ ] **Step 3: Commit**

```bash
git add templates/retro.md
git commit -m "feat(cfp-27): templates/retro.md 신설 — PMOAgent owner doc schema SSOT

Phase 0b lint 강화 사전 작업 (2/2 신규 template).
CFP-26 Phase 0a부터 PMOAgent가 docs/retros/** 직접 write — schema SSOT가
부재하던 부분을 템플릿으로 명시화.

Frontmatter 필수: title / date / sprint_period / cfp_keys / authors /
related_stories / sentinel_refs. 본문 섹션 고정 순서: §1 결과 / §2 kept /
§3 problem / §4 try / §5 cross-Story (선택) / §6 ADR 후보 (선택) /
§7 토큰 예산 (선택, 세션 회고) / §8 개선 제안 (3건 이하).

기존 docs/retros/*.md 3건은 본 schema 부분 충족 — CFP-27 lint warning 모드라
기존 파일 fail 없음. CFP-28 dogfood에서 strict 전환 시점에 backfill.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 3: check-write-permission-redistribution.sh — awk 파라미터화

CFP-26 code review minor 후속 처리. `allow_block` / `deny_block` 중복 함수를 1개 helper로 통합.

**Files:**
- Modify: `scripts/check-write-permission-redistribution.sh`

- [ ] **Step 1: Read current state**

```bash
sed -n '14,40p' scripts/check-write-permission-redistribution.sh
```

Confirm presence of separate `allow_block()` and `deny_block()` functions (each ~12 lines, identical except for `allow:` vs `deny:` and `in_allow` vs `in_deny`).

- [ ] **Step 2: Replace with parameterized helper**

Replace the two functions (lines ~14-37) with a single `extract_block` parameterized by key:

```bash
# helper: extract permissions sub-block (allow|deny) from agent md frontmatter
extract_block() {
  local f="$1" key="$2"
  awk -v key="$key" '
    /^---$/{c++; next}
    c==1 && /^permissions:/{in_perm=1; next}
    c==1 && in_perm && $0 ~ "^  " key ":"{in_block=1; next}
    c==1 && in_perm && /^  [a-z]+:/{in_block=0}
    c==1 && in_block{print}
    c>=2{exit}
  ' "$f"
}
```

Then update call sites to pass key:

- `assert_allow` body: `if ! allow_block "$f" | grep -qF -- "$pat"; then` → `if ! extract_block "$f" allow | grep -qF -- "$pat"; then`
- `assert_deny` body: `if ! deny_block "$f" | grep -qF -- "$pat"; then` → `if ! extract_block "$f" deny | grep -qF -- "$pat"; then`

- [ ] **Step 3: Run lint to verify no regression**

```bash
./scripts/check-write-permission-redistribution.sh; echo "exit=$?"
```

Expected: `✓ CFP-26 Phase 0a — single-owner 4종 권한 재분배 invariant OK` and exit=0. If FAIL, the awk regex expansion broke something.

Also run on a file that has only allow (no deny) and only deny (no allow) edge cases — none in repo so this is implicit.

- [ ] **Step 4: Commit**

```bash
git add scripts/check-write-permission-redistribution.sh
git commit -m "refactor(cfp-27): check-write-permission-redistribution awk 파라미터화

CFP-26 code review minor follow-up. allow_block / deny_block 두 함수가
구조적으로 동일했음 (key 이름과 in_allow/in_deny 변수만 다름). 단일
extract_block(file, key) 함수로 파라미터화 — 12+12=24 lines → 11 lines.

CFP-27이 frontmatter schema lint를 추가하면서 같은 awk 패턴을 재사용할
가능성이 높아져 사전 정리. 동작은 동일하다고 verify (lint 16/16 PASS 유지).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 4: scripts/check-doc-frontmatter.sh — 신규 lint (warning 모드)

4 owner doc path 의 frontmatter 필수 필드 검증.

**Files:**
- Create: `scripts/check-doc-frontmatter.sh`

- [ ] **Step 1: Write the lint script**

Create file `scripts/check-doc-frontmatter.sh`:

```bash
#!/usr/bin/env bash
# CFP-27 Phase 0b
# 검사: 4 owner doc path 의 frontmatter 필수 필드 (warning 모드 — exit=0 with warnings)
#
# Path / 필수 frontmatter 필드 source:
#   - docs/change-plans/**     templates/change-plan.md frontmatter (title, slug, status, author, created, story)
#   - docs/adr/**              templates/adr.md          (adr_number, title, status, category, date)
#   - docs/domain-knowledge/** templates/domain-knowledge.md (title, area, topic_slug, status, updated)
#   - docs/retros/**           templates/retro.md         (title, date, sprint_period, cfp_keys, authors)
#
# CFP-28 dogfooding에서 strict 모드로 전환 (exit=1).
set -euo pipefail
cd "$(dirname "$0")/.."

WARN_COUNT=0

python3 <<'PY' || true
import sys, re
from pathlib import Path

try:
    import yaml
except ImportError:
    print("⚠ check-doc-frontmatter: pyyaml 미설치 — skip", file=sys.stderr)
    sys.exit(0)

REQUIRED = {
    "docs/change-plans": {"title", "slug", "status", "author", "created", "story"},
    "docs/adr":          {"adr_number", "title", "status", "category", "date"},
    "docs/domain-knowledge": {"title", "area", "topic_slug", "status", "updated"},
    "docs/retros":       {"title", "date", "sprint_period", "cfp_keys", "authors"},
}

warns = []
for prefix, fields in REQUIRED.items():
    path = Path(prefix)
    if not path.exists():
        continue
    for md in sorted(path.rglob("*.md")):
        # README 또는 index 파일은 schema 대상 아님
        if md.name.lower() in {"readme.md", "index.md"}:
            continue
        text = md.read_text(encoding="utf-8")
        if not text.startswith("---\n"):
            warns.append(f"{md}: frontmatter 부재")
            continue
        try:
            fm_text = text.split("\n---\n", 1)[0][4:]
            fm = yaml.safe_load(fm_text)
        except Exception as e:
            warns.append(f"{md}: frontmatter parse 실패 ({type(e).__name__})")
            continue
        if not isinstance(fm, dict):
            warns.append(f"{md}: frontmatter는 mapping이어야 함")
            continue
        missing = fields - fm.keys()
        if missing:
            warns.append(f"{md}: 필수 필드 누락 — {sorted(missing)}")

if warns:
    print(f"⚠ CFP-27 doc-frontmatter (WARN): {len(warns)} 건")
    for w in warns:
        print(f"  - {w}")
    print("⚠ warning 모드 — CFP-28 strict 전환 시점에 모두 fix 또는 allowlist 필요")
else:
    print("✓ CFP-27 doc-frontmatter: 4 owner path 전부 schema 충족")
PY

# 항상 exit 0 (warning 모드)
echo ""
echo "(check-doc-frontmatter: warning 모드 — exit 0 강제. CFP-28에서 strict 전환)"
exit 0
```

- [ ] **Step 2: Make executable + run**

```bash
chmod +x scripts/check-doc-frontmatter.sh
./scripts/check-doc-frontmatter.sh
echo "exit=$?"
```

Expected: 출력에 기존 docs files 의 frontmatter 누락 경고 다수 표시 (특히 retro 3건은 frontmatter 부재). exit=0. 이게 baseline (warning 모드).

기록할 가치가 있는 결과:
- `docs/change-plans/` — 모두 frontmatter 있음 (template 정합 가능성 높음)
- `docs/adr/` — 모두 frontmatter 있음
- `docs/domain-knowledge/` — 디렉토리 부재, skip
- `docs/retros/` — 3개 파일 모두 frontmatter 부재 → 3 warning 예상

- [ ] **Step 3: Commit**

```bash
git add scripts/check-doc-frontmatter.sh
git commit -m "feat(cfp-27): scripts/check-doc-frontmatter.sh — 4 owner doc path frontmatter lint (warning 모드)

CFP-25 Phase 0b 핵심. 4 owner doc path (change-plans/adr/domain-knowledge/retros)
의 frontmatter 필수 필드 검증. 각 path 별 templates/<doc-type>.md 가
필수 필드 source.

warning 모드: 위반 시 ⚠ 경고 + exit 0. CFP-28 dogfood 검증 통과 후
strict 모드 (exit 1)로 전환 예정.

기존 docs/retros/*.md 3건은 frontmatter 부재 — 본 lint가 baseline 식별.
backfill 또는 strict 전환은 CFP-28에서.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 5: scripts/check-doc-section-schema.sh — 신규 lint (warning 모드)

4 owner doc path 의 본문 필수 섹션 헤딩 검증.

**Files:**
- Create: `scripts/check-doc-section-schema.sh`

- [ ] **Step 1: Write the lint script**

Create file `scripts/check-doc-section-schema.sh`:

```bash
#!/usr/bin/env bash
# CFP-27 Phase 0b
# 검사: 4 owner doc path 의 본문 필수 섹션 헤딩 (warning 모드 — exit=0 with warnings)
#
# Section schema source:
#   - docs/change-plans/**     templates/change-plan.md  §1-§11 (주요 8개)
#   - docs/adr/**              templates/adr.md          ## 상태 / ## 컨텍스트 / ## 결정 / ## 결과 / ## 관련 파일
#   - docs/domain-knowledge/** templates/domain-knowledge.md ## 정의 / ## 컨텍스트 / ## 핵심 규칙 / ## 경계 / ## 관련 ADR / ## 변경 이력
#   - docs/retros/**           templates/retro.md         ## §1 결과 / ## §2 / ## §3 / ## §4 (§5-§8 선택)
#
# CFP-28에서 strict 모드 (exit=1) 전환.
set -euo pipefail
cd "$(dirname "$0")/.."

python3 <<'PY' || true
import sys, re
from pathlib import Path

REQUIRED_SECTIONS = {
    "docs/change-plans": [
        # change-plan.md 본문 §1-§11 중 항상 필요한 핵심 8개 (선택 §은 제외)
        r"^### §1\. 목적",
        r"^### §2\. 현재 구조",
        r"^### §3\. 도입할 설계",
        r"^### §4\. API 계약",
        r"^### §7\. 보안",   # 보안 설계 (CFP-17 이후 항상 필요, 무관 시 N/A 명시)
        r"^### §8\. Test Contract",
        r"^### §10\.",      # FIX Ledger 위치 — 정확 명칭은 schema 변동, 헤딩 prefix만
        r"^### §11\.",      # 데이터 마이그레이션 (CFP-21 이후)
    ],
    "docs/adr": [
        r"^## 상태",
        r"^## 컨텍스트",
        r"^## 결정",
        r"^## 결과",
        r"^## 관련 파일",
    ],
    "docs/domain-knowledge": [
        r"^## 정의",
        r"^## 컨텍스트",
        r"^## 핵심 규칙",
        r"^## 경계",
        r"^## 관련 ADR",
        r"^## 변경 이력",
    ],
    "docs/retros": [
        r"^## §1 결과",
        r"^## §2 ",   # 무엇이 잘 갔나
        r"^## §3 ",   # 무엇이 막혔나
        r"^## §4 ",   # 다음에 할 일
    ],
}

warns = []
for prefix, patterns in REQUIRED_SECTIONS.items():
    path = Path(prefix)
    if not path.exists():
        continue
    for md in sorted(path.rglob("*.md")):
        if md.name.lower() in {"readme.md", "index.md"}:
            continue
        text = md.read_text(encoding="utf-8")
        # frontmatter 영역 제거
        if text.startswith("---\n"):
            parts = text.split("\n---\n", 1)
            if len(parts) == 2:
                text = parts[1]
        missing = []
        for p in patterns:
            if not re.search(p, text, re.MULTILINE):
                missing.append(p)
        if missing:
            warns.append(f"{md}: 필수 섹션 누락 — {missing}")

if warns:
    print(f"⚠ CFP-27 doc-section-schema (WARN): {len(warns)} 건")
    for w in warns:
        print(f"  - {w}")
    print("⚠ warning 모드 — CFP-28 strict 전환 시점에 모두 fix 또는 allowlist 필요")
else:
    print("✓ CFP-27 doc-section-schema: 4 owner path 전부 schema 충족")
PY

echo ""
echo "(check-doc-section-schema: warning 모드 — exit 0 강제. CFP-28에서 strict 전환)"
exit 0
```

- [ ] **Step 2: Make executable + run**

```bash
chmod +x scripts/check-doc-section-schema.sh
./scripts/check-doc-section-schema.sh
echo "exit=$?"
```

Expected: 기존 docs files (특히 오래된 ADR, 초기 Change Plan) 일부가 헤딩 schema 위반 — warning 다수. exit=0.

- [ ] **Step 3: Commit**

```bash
git add scripts/check-doc-section-schema.sh
git commit -m "feat(cfp-27): scripts/check-doc-section-schema.sh — 4 owner doc path 섹션 lint (warning 모드)

CFP-25 Phase 0b 핵심 (frontmatter lint와 짝). 4 owner doc path의 본문
필수 섹션 헤딩 검증. templates/<doc-type>.md 의 본문 섹션이 source.

기존 ADR / Change Plan은 대체로 schema 충족 (template SSOT 정착 후 작성).
domain-knowledge는 디렉토리 부재. retros는 schema 위반 — backfill은 CFP-28.

Frontmatter lint와 동일하게 warning 모드 — CFP-28에서 strict 전환.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 6: .github/workflows/lint.yml — 3 새 job 통합

CFP-26 redistribution + CFP-27 frontmatter + CFP-27 section-schema lint 모두 PR마다 자동 실행.

**Files:**
- Modify: `.github/workflows/lint.yml`

- [ ] **Step 1: Read current lint.yml**

```bash
cat .github/workflows/lint.yml
```

확인: 현재 jobs는 `shellcheck`, `markdown-links`, `agent-frontmatter` 3개. 같은 패턴으로 새 3개 추가.

- [ ] **Step 2: Append 3 new jobs at the end of `jobs:` block**

`.github/workflows/lint.yml` 파일 끝에 다음 3 job 추가 (기존 jobs 들 다음에):

```yaml
  write-permission-redistribution:
    name: write permission redistribution invariant (CFP-26)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run check-write-permission-redistribution.sh
        run: bash scripts/check-write-permission-redistribution.sh

  doc-frontmatter:
    name: doc frontmatter schema (CFP-27 — warning)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install pyyaml
      - name: Run check-doc-frontmatter.sh
        run: bash scripts/check-doc-frontmatter.sh

  doc-section-schema:
    name: doc section schema (CFP-27 — warning)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: Run check-doc-section-schema.sh
        run: bash scripts/check-doc-section-schema.sh
```

- [ ] **Step 3: Verify YAML valid**

```bash
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/lint.yml'))" && echo "VALID YAML"
```

Expected: `VALID YAML`. 만약 syntax error 시 indent 등 확인.

- [ ] **Step 4: Locally simulate the new jobs**

```bash
bash scripts/check-write-permission-redistribution.sh; echo "1: exit=$?"
bash scripts/check-doc-frontmatter.sh; echo "2: exit=$?"
bash scripts/check-doc-section-schema.sh; echo "3: exit=$?"
```

Expected: all exit=0. (1번은 strict, 2/3번은 warning 모드.)

- [ ] **Step 5: Commit**

```bash
git add .github/workflows/lint.yml
git commit -m "ci(cfp-27): lint.yml에 redistribution + frontmatter + section-schema 3 job 추가

CFP-26 Phase 0a 의 redistribution invariant lint를 CI에서 강제 (이전엔
manual call only). CFP-27 의 doc-frontmatter / doc-section-schema 2 lint는
warning 모드로 추가 — PR 마다 baseline 노출.

총 lint workflow jobs: 6개
- shellcheck (regen-agents.sh)
- markdown internal links
- agent frontmatter contract
- write permission redistribution invariant (CFP-26)  [strict]
- doc frontmatter schema (CFP-27 — warning)
- doc section schema (CFP-27 — warning)

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 7: CLAUDE.md — CFP-27 lint enforcement 안내

ADR / Domain Knowledge / Story 섹션에 CFP-27 lint가 schema를 강제하기 시작했다는 안내 추가.

**Files:**
- Modify: `CLAUDE.md` (3 섹션 갱신)

- [ ] **Step 1: Locate target sections**

```bash
grep -n "^## ADR\|^## Domain Knowledge\|^## docs/stories markdown" CLAUDE.md
```

Note line numbers.

- [ ] **Step 2: Update "## ADR" 섹션 — 페이지 템플릿 line**

Find the line:
```markdown
### 페이지 템플릿
[`templates/adr.md`](templates/adr.md) 참조. frontmatter (adr_number / title / status / category / date / related_files) + 본문 섹션 (`## 상태 / ## 컨텍스트 / ## 결정 / ## 결과 / ## 다이어그램 / ## 관련 파일`).
```

Append:
```markdown
### 페이지 템플릿
[`templates/adr.md`](templates/adr.md) 참조. frontmatter (adr_number / title / status / category / date / related_files) + 본문 섹션 (`## 상태 / ## 컨텍스트 / ## 결정 / ## 결과 / ## 다이어그램 / ## 관련 파일`).

**CFP-27부터** `scripts/check-doc-frontmatter.sh` + `scripts/check-doc-section-schema.sh` 가 본 schema를 검증 (warning 모드 — CFP-28 strict 전환).
```

- [ ] **Step 3: Update "## Domain Knowledge" 섹션**

Find the section. Append at the end:
```markdown
## Domain Knowledge

- 위치: `docs/domain-knowledge/<area>/<topic>.md` (계층 구조). Consumer overlay가 area 자유 정의
- CODEOWNERS가 `docs/domain-knowledge/**` → `@org/domain-experts` 자동 review
- DomainAgent 입력 4소스: `docs/domain-knowledge/**` + `docs/adr/**` + 도메인 코드 + 사용자 원문 §1
- Q&A는 GitHub Discussions의 "Domain Q&A" 카테고리 (consumer overlay `github.discussions.domain_kb_category` 지정)
- **페이지 schema**: [`templates/domain-knowledge.md`](templates/domain-knowledge.md) (CFP-27 신설). frontmatter (title / area / topic_slug / status / sources / related_adrs / related_stories / updated) + 본문 섹션 (`## 정의 / ## 컨텍스트 / ## 핵심 규칙 / ## 경계 / ## 관련 ADR / ## 변경 이력`). `scripts/check-doc-frontmatter.sh` + `scripts/check-doc-section-schema.sh` 검증 (warning 모드)
```

(만약 기존 §섹션이 페이지 schema 항목을 이미 가지면 갱신, 없으면 마지막 bullet으로 추가)

- [ ] **Step 4: Update "## docs/stories markdown 규약" 섹션 (Story file schema는 본 CFP scope 밖이지만 retros 안내 1줄 추가)**

Find the section. After existing content append:
```markdown
- **Retro page schema** (참고): `docs/retros/<sprint>.md` 페이지는 PMOAgent 직접 write — 형식은 [`templates/retro.md`](templates/retro.md) (CFP-27 신설) 따름. `check-doc-frontmatter.sh` + `check-doc-section-schema.sh` 검증 (warning 모드)
```

- [ ] **Step 5: Run all lints**

```bash
./scripts/check-write-permission-redistribution.sh; echo "1: exit=$?"
./scripts/check-doc-frontmatter.sh; echo "2: exit=$?"
./scripts/check-doc-section-schema.sh; echo "3: exit=$?"
./scripts/check-agent-frontmatter.sh; echo "4: exit=$?"
./scripts/check-doc-links.sh; echo "5: exit=$?"
./scripts/check-no-atlassian.sh; echo "6: exit=$?"
```

All should exit=0 (1, 4, 5, 6 strict; 2, 3 warning).

- [ ] **Step 6: Commit**

```bash
git add CLAUDE.md
git commit -m "docs(cfp-27): CLAUDE.md ADR + Domain Knowledge + Story 섹션 — lint enforcement 안내 추가

CFP-27이 도입한 doc-frontmatter / doc-section-schema lint 강제 시작을
관련 섹션에 명시:

- ## ADR / 페이지 템플릿: lint 검증 시작 (warning 모드)
- ## Domain Knowledge: domain-knowledge.md schema + lint
- ## docs/stories markdown 규약: retro.md schema 안내 추가

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 8: v0.16.0 release — plugin.json + CHANGELOG + migration-guide + plugin-design

CFP-27이 추가한 lint + 템플릿 release 표시.

**Files:**
- Modify: `.claude-plugin/plugin.json` (version 0.15.0 → 0.16.0)
- Modify: `CHANGELOG.md` ([0.16.0] entry append at top)
- Modify: `docs/migration-guide.md` (v0.15 → v0.16 섹션)
- Modify: `docs/plugin-design.md` (Stage 1 history line v0.16 추가)

- [ ] **Step 1: plugin.json version bump**

Read `.claude-plugin/plugin.json`. Confirm `version: "0.15.0"`. Change to `"0.16.0"`.

- [ ] **Step 2: CHANGELOG.md — [0.16.0] entry prepend**

Above existing `## [0.15.0]` entry, add:

```markdown
## [0.16.0] - 2026-04-28

### CFP-27 — Phase 0b · Lint 강화 + CI Integration

**Non-BREAKING** — 신규 lint 2종 (doc-frontmatter / doc-section-schema)은 **warning 모드** 시작. 기존 docs 파일 fail 없음. CFP-28 dogfood 검증 통과 후 strict 전환 예정.

설계 SSOT: [`docs/superpowers/specs/2026-04-28-docsagent-scope-reduction-and-review-extraction-design.md`](docs/superpowers/specs/2026-04-28-docsagent-scope-reduction-and-review-extraction-design.md) (CFP-25 — 설계 spec, CFP-27 — 본 구현 Story).

### Added
- `templates/domain-knowledge.md` — DomainAgent owner doc schema SSOT (CFP-26 Phase 0a부터 owner direct write이나 schema 부재였음)
- `templates/retro.md` — PMOAgent owner doc schema SSOT (동일)
- `scripts/check-doc-frontmatter.sh` — 4 owner doc path frontmatter 필수 필드 검증 (warning 모드)
- `scripts/check-doc-section-schema.sh` — 4 owner doc path 본문 필수 섹션 헤딩 검증 (warning 모드)
- `.github/workflows/lint.yml` 3 신규 job: `write-permission-redistribution` (strict, CFP-26 invariant CI 통합) + `doc-frontmatter` + `doc-section-schema` (warning 모드)

### Changed
- `scripts/check-write-permission-redistribution.sh` — `allow_block` / `deny_block` 두 함수를 단일 `extract_block(file, key)` 파라미터화 (CFP-26 code review minor follow-up)
- `CLAUDE.md` "## ADR" + "## Domain Knowledge" + "## docs/stories markdown 규약" 섹션 — CFP-27 lint enforcement 안내 추가

### Why
CFP-26 Phase 0a가 4 owner agent direct write를 도입했으나 **schema enforcement는 manual convention**에 그침. CFP-27이 schema를 lint로 자동 강제 시작 (warning 모드 → CFP-28 dogfood → CFP-28+ strict). 또한 부재했던 owner doc 템플릿 2건(domain-knowledge / retro) 신설로 SSOT 완결성 회복.

추가로 CFP-26에서 식별된 follow-up 2건 처리: redistribution lint CI integration (이전 manual call only) + awk 코드 정리.

### Migration
**Non-BREAKING — consumer 영향 미미**:
- 신규 lint 2종은 warning 모드라 기존 consumer docs 파일 호환
- consumer가 `templates/domain-knowledge.md` / `templates/retro.md` 를 schema source로 사용 가능 — 강제 아님 (CFP-28에서 strict 전환 시 backfill 필요)
- CI workflow 6 jobs 운영 — consumer가 `.github/workflows/lint.yml` 복사한 경우 새 job 3개 동기화 권장

자세한 사항: `docs/migration-guide.md` v0.15 → v0.16 섹션 참조.

```

- [ ] **Step 3: docs/migration-guide.md — v0.15 → v0.16 섹션 prepend**

Read `docs/migration-guide.md` to find existing TOC + section pattern. Above existing `## v0.14 → v0.15` section, add:

```markdown
## v0.15 → v0.16 (CFP-27 Phase 0b) — Lint 강화 + CI Integration (Non-BREAKING)

**범위**: 신규 owner doc 템플릿 2건 + 신규 lint 2건 (warning 모드) + redistribution lint CI integration.

**필요 조치**:

### Consumer overlay에서 owner doc schema 따르려면 (선택)
- `templates/domain-knowledge.md` / `templates/retro.md` 를 frontmatter + 섹션 schema source로 활용 가능
- consumer overlay에 `_overlay/templates/<doc-type>.md` 작성하면 owner agent가 그 schema도 따름 (overlay-aware)

### Consumer CI workflow 동기화 (권장)
- `.github/workflows/lint.yml` 에 다음 3 job 추가 동기화:
  - `write-permission-redistribution` (strict)
  - `doc-frontmatter` (warning)
  - `doc-section-schema` (warning)
- 생략해도 codeforge plugin 동작에는 영향 없음. 다만 본 plugin이 consumer 워크플로우의 invariant를 보지 않게 됨.

### 향후 단계 안내
- CFP-28 (Phase 0c): 2 lint를 strict 모드로 전환 + 1-2 real Story 실행 검증. 이 시점에 backfill 필요한 모든 docs 파일 schema 갱신 의무.
- CFP-29 (Phase 1): codeforge-review plugin 추출.

### 설계 SSOT
- [`docs/superpowers/specs/2026-04-28-docsagent-scope-reduction-and-review-extraction-design.md`](superpowers/specs/2026-04-28-docsagent-scope-reduction-and-review-extraction-design.md) (CFP-25 design spec)

자세한 사항: 본 plan (CFP-27) 참조.

```

- [ ] **Step 4: docs/plugin-design.md — Stage 1 history line v0.16 append**

Read `docs/plugin-design.md` Stage 1 (around line 145). Find the version history line.

Append v0.16 clause after v0.15:
```
. v0.16에서 owner doc 템플릿 2건(domain-knowledge / retro) 신설 + lint 2건(doc-frontmatter / doc-section-schema, warning 모드) + redistribution lint CI integration (CFP-27 Phase 0b — Non-BREAKING)
```

- [ ] **Step 5: Verify all lints PASS**

```bash
./scripts/check-write-permission-redistribution.sh; echo "1: exit=$?"
./scripts/check-doc-frontmatter.sh; echo "2: exit=$?"
./scripts/check-doc-section-schema.sh; echo "3: exit=$?"
./scripts/check-agent-frontmatter.sh; echo "4: exit=$?"
./scripts/check-doc-links.sh; echo "5: exit=$?"
./scripts/check-no-atlassian.sh; echo "6: exit=$?"
```

All should exit=0.

- [ ] **Step 6: Commit**

```bash
git add .claude-plugin/plugin.json CHANGELOG.md docs/migration-guide.md docs/plugin-design.md
git commit -m "chore(cfp-27): v0.16.0 release — Phase 0b lint 강화 + CI integration (Non-BREAKING)

- plugin.json version 0.15.0 → 0.16.0 (Non-BREAKING — warning 모드 lint)
- CHANGELOG [0.16.0] entry — Added/Changed/Why/Migration 4 sections
- migration-guide v0.15 → v0.16 섹션 (consumer 조치 + 향후 단계 안내)
- plugin-design Stage 1 history v0.16 추가

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 9: Final verification + push readiness

**Files:**
- (No new file changes) Run all lints + verify state + check-no-atlassian allowlist update for this plan file

- [ ] **Step 1: Update check-no-atlassian.sh allowlist for this plan file**

Same false positive case as CFP-26 plan. Add to allowlist:

```bash
grep -n "cfp-26-phase-0a-write-permission-redistribution" scripts/check-no-atlassian.sh
```

After that line, add new entry:
```bash
  "docs/superpowers/plans/2026-04-28-cfp-27-phase-0b-lint-strengthening-and-ci-integration.md"
```

(주의: 본 plan 파일이 `./scripts/check-no-atlassian.sh` 자기 참조를 포함해 false positive)

- [ ] **Step 2: Run all 6 lints**

```bash
./scripts/check-write-permission-redistribution.sh; echo "1: exit=$?"
./scripts/check-doc-frontmatter.sh; echo "2: exit=$?"
./scripts/check-doc-section-schema.sh; echo "3: exit=$?"
./scripts/check-agent-frontmatter.sh; echo "4: exit=$?"
./scripts/check-doc-links.sh; echo "5: exit=$?"
./scripts/check-no-atlassian.sh; echo "6: exit=$?"
```

All exit=0.

- [ ] **Step 3: Verify commit log**

```bash
git log --oneline main..HEAD
```

Expected commits (chronological order, oldest at bottom — assuming Tasks 1~8 each had 1 commit + plan commit + this Task 9 commit):
1. plan commit
2. Task 1: templates/domain-knowledge.md
3. Task 2: templates/retro.md
4. Task 3: refactor awk
5. Task 4: check-doc-frontmatter.sh
6. Task 5: check-doc-section-schema.sh
7. Task 6: lint.yml CI integration
8. Task 7: CLAUDE.md updates
9. Task 8: v0.16.0 release
10. Task 9 (this commit)

10 commits total. Adjust if any task generated follow-up fix commits.

- [ ] **Step 4: Commit Task 9**

```bash
git add scripts/check-no-atlassian.sh
git commit -m "chore(cfp-27): check-no-atlassian allowlist에 CFP-27 plan 추가

Task 9 final verification. 본 plan 파일이 './scripts/check-no-atlassian.sh'
자기 참조를 포함해 false positive — allowlist 추가로 해소.

PR open 직전 최종 lint 통과 확인:
- check-write-permission-redistribution: 16/16 PASS (CI strict)
- check-doc-frontmatter: warning baseline 식별, exit=0
- check-doc-section-schema: warning baseline 식별, exit=0
- check-agent-frontmatter: PASS
- check-doc-links: PASS
- check-no-atlassian: PASS

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

- [ ] **Step 5: Print PR readiness checklist** (just print, do NOT actually create PR)

```
PR readiness checklist:
□ git diff main..HEAD --stat ← (paste actual stat output)
□ All lints PASS / warning baseline established
□ branch ready to push: feat/cfp-27-phase-0b
□ Suggested PR title: feat(cfp-27): Phase 0b · lint 강화 + CI integration (Non-BREAKING v0.16.0)
□ marketplace cross-repo sync PR follow-up obligation (CFP-24 정책):
  - .claude-plugin/plugin.json mirrored field changed: version (0.15.0 → 0.16.0)
  - After this PR merges, open marketplace sync PR at mclayer/marketplace
  - Update marketplace.json plugins[name=codeforge].version = 0.16.0
□ phase-gate-mergeable label requirement:
  - phase:설계-리뷰 + gate:design-review-pass (no src/tests/ changes — docs gate path)
□ Suggested PR body sections:
  - ## Summary (1-3 bullets)
  - Reference: spec [CFP-25] + plan [CFP-27]
  - ## Migration: link to CHANGELOG [0.16.0] + migration-guide v0.15→v0.16 section
  - ## Test plan (lint commands: 6 scripts + CI 6 jobs)
  - ## marketplace sync follow-up (CFP-24 obligation)
  - 🤖 Generated with Claude Code
```

---

## 자체 점검 (Self-Review)

본 plan을 spec과 대조해 누락·placeholder·일관성 이슈 검토:

**1. Spec coverage (CFP-25 §9 sequencing)**:
> CFP-27 (Phase 0b) : Lint 강화
>   - scripts/check-agent-frontmatter.sh 확장   → CFP-27이 새 scripts 추가 (확장보다 신규 — 더 명확) ✓
>   - scripts/check-doc-links.sh 확장          → 본 CFP는 doc-links 미확장 (이미 충분), frontmatter + section schema 신규 추가
>   - .github/workflows/에 lint step 추가      → ✓ Task 6
>   - 기존 docs 4종 backfill (frontmatter 누락 보강) → backfill은 CFP-28로 deferred (warning 모드 사용)

**Note**: spec은 "기존 lint 확장"이라 표현했지만 실제로는 신규 lint 추가가 더 깔끔 (기존 check-agent-frontmatter.sh는 agent md 전용, doc 들과 logic이 다름). 본 plan이 doc 전용 lint 신규 작성으로 분리.

**2. Placeholder scan**: `TODO`·`TBD`·"채울 것" 없음. 모든 step에 concrete 명령 + 예상 결과. ✓

**3. Type consistency**: 4 owner doc path 표기 일관 (`docs/{change-plans,adr,domain-knowledge,retros}/**`). frontmatter 필드 이름 template ↔ lint script 일치 검증 필요 — Task 4 / Task 5 의 REQUIRED 딕셔너리가 Task 1 / Task 2 의 template frontmatter와 일치하도록 작성. ✓

**4. follow-up coverage**:
- CFP-26 awk 파라미터화 → Task 3 ✓
- CFP-26 redistribution CI integration → Task 6 ✓
- domain-knowledge / retro 템플릿 신설 → Task 1·2 ✓
- Story file schema → CFP-27.5 deferred (본 plan §"defer" 섹션에 명시) ✓
- PMOAgent §4 line 152 + Cross-Story line 125 → 별도 cleanup CFP (본 plan 범위 밖)
- ADR-002 컨텍스트 단락 안내 → 별도 cleanup (본 plan 범위 밖)

---

## 다음 plan (참조)

- **CFP-27.5**: Story file (`docs/stories/<KEY>.md`) §1-§11 schema lint — multi-writer + §10 FIX Ledger appendable 등 복잡성으로 별도 분리
- **CFP-28 (Phase 0c)**: 2 warning lint → strict 전환 + backfill + 1-2 real Story 실행 검증
- **CFP-29 (Phase 1)**: codeforge-review plugin 추출
