---
title: story-init workflow의 docs h1·PR title `[STORY]` prefix strip (CFP-11 폴리시)
slug: cfp-15-workflow-title-polish
status: draft
author: ClaudeOrchestrator (CFP-14 §11 후속)
reviewers: [user]
related_adrs: []
created: 2026-04-27
story: CFP-15
---

## §1. 목적

CFP-11 §11에 명시된 폴리시 후보 — Issue Form `story.yml`이 자동 부착하는 `[STORY]` prefix를 docs h1·PR title에서 strip해 cosmetic 중복 제거.

### 수용 기준

- `Compute next story key` step Python heredoc 2 줄 출력 (slug + title_clean)
- docs h1: `# <KEY>: <TITLE_CLEAN>` (이전: `# <KEY>: [STORY] <TITLE>`)
- PR title: `[<KEY>] <TITLE_CLEAN>` (이전: `[<KEY>] [STORY] <TITLE>`)
- CFP-5 invariant 준수 (templates ↔ .github/ byte-identical)

## §2. 현재 구조 분석

### 2.1 CFP-11 발견 cosmetic 결함

CFP-11 auto-generated docs h1:
```
# CFP-11: [STORY] CFP-11 end-to-end 실증 — Issue Form workflow 자동 동작 첫 검증 (재시도)
```

`[STORY]` prefix는 form의 `title:` 기본값으로 들어가는 자동 prefix. workflow가 이를 strip하지 않아 docs h1 + PR title에 노출.

### 2.2 SLUG 계산은 이미 strip 처리

CFP-11 PR #40 (sed Korean fix)에서 도입된 Python heredoc은 SLUG 생성 시 `[STORY]` strip 이미 적용. 동일 logic을 title에도 적용하면 됨.

### 2.3 Mapper 변호 근거

기존 단일 출력 (slug only) 보존 입장: "title_clean을 별도 Python heredoc으로 분리해 step 책임 명확화"

## §3. 도입할 설계

### 3.1 Mapper vs Refactor 대립 결론

채택: **Refactor 우세**.

근거:
- title_clean과 slug는 모두 `re.sub(r"^\[STORY\]\s*", "", title)`이 starting point — logic 동일
- 두 Python heredoc 분리는 동일 작업 2회 호출 (Korean re.sub 포함 ~10ms × 2)
- shell sed `-n '<N>p'`은 multi-value output 표준 idiom

### 3.2 multi-value output 패턴

```bash
PYOUT=$(python3 - <<'PYEOF'
import os, re
title = os.environ.get("ISSUE_TITLE", "")
title_clean = re.sub(r"^\[STORY\]\s*", "", title).strip()
slug = re.sub(r"[^A-Za-z0-9가-힣]+", "-", title_clean, flags=re.UNICODE)
slug = slug.strip("-")[:40].rstrip("-")
print(slug)        # Line 1
print(title_clean) # Line 2
PYEOF
)
SLUG=$(printf '%s' "$PYOUT" | sed -n '1p')
TITLE_CLEAN=$(printf '%s' "$PYOUT" | sed -n '2p')
```

### 3.3 GITHUB_OUTPUT multi-value (heredoc syntax)

`title_clean`은 Korean / em-dash 등 special char 포함 가능 → heredoc syntax로 GITHUB_OUTPUT 등록:

```bash
{
  echo "title_clean<<TITLE_EOF"
  printf '%s\n' "$TITLE_CLEAN"
  echo "TITLE_EOF"
} >> "$GITHUB_OUTPUT"
```

### 3.4 두 사용 지점 patch

- `Create branch + docs/stories/<KEY>.md` step: env에 `TITLE_CLEAN` 추가 + `printf '# %s: %s\n\n' "$KEY" "$TITLE_CLEAN"`
- `Create Phase 1 PR` step: env에 `TITLE_CLEAN` 추가 + `--title "[${KEY}] ${TITLE_CLEAN}"`

### 3.5 ADR 정합성

ADR-001/002/003 무관. 신규 ADR 불요.

## §4. API 계약

본 Story는 workflow auto-output 1 location 변경. Issue Form input → workflow output cosmetic만 영향. 다른 Step (parse user requirement / create branch / Issue body update / milestone / component) 영향 없음.

## §5. 변경 계획 (파일 단위)

| 파일 경로 | 변경 유형 | 담당 | 상태 |
|-----------|-----------|------|------|
| `.github/workflows/story-init.yml` | 수정 (Compute step + 2 사용 지점) | DocsAgent | 적용 완료 + local test PASS |
| `templates/github-workflows/story-init.yml` | 동시 byte-identical sync | DocsAgent | sync 완료 |
| `docs/stories/CFP-15.md` | 신규 | DocsAgent | 작성 완료 |
| `docs/change-plans/cfp-15-workflow-title-polish.md` | 신규 (본 파일) | DocsAgent | 작성 중 |

## §6. 리팩토링 선행 작업

**없음**. workflow 폴리시 단일 변경.

## §8. Test Contract

### §8.1 커버리지 계획

- 단위 테스트: **N/A**
- 통합 테스트: **CI invariant Step 1 (workflow parity) PASS** (templates ↔ .github 동일성 검증)
- **Local 사용자 시나리오**: 본 PR merge 후 다음 Issue Form 제출 시 첫 실측 가능

### §8.2 경계 조건·invariant

- **Test 1 — slug + title_clean 동시 추출**: 2줄 sed extraction 정상 (검증 완료)
- **Test 2 — Korean / em-dash 보존**: title_clean에 Korean·em-dash 포함 정상 GITHUB_OUTPUT (heredoc syntax)
- **Edge case — 빈 title**: form `validations.required: true`로 차단

### §8.3 Perf Baseline

**N/A** — workflow 1 step ms 수준.

## §9. 분기 선택

**단일 PR**. Phase 1/2 분리 면제 (메타 workflow polish).

본 PR base는 `main`. CFP-14 머지 완료.

## §10. ADR 대상 여부 + 기존 ADR 정합성

- ADR-001/002/003 무관
- 신규 ADR 불요
