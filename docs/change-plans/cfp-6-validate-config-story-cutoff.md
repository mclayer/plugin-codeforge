---
title: validate_config.py 확장 — story_cutoff 검증 + unknown key reject (CFP-1 invariant 영구 보존)
slug: cfp-6-validate-config-story-cutoff
status: draft
author: ClaudeOrchestrator (Codex 종합 리뷰 P1 #2)
reviewers: [user]
related_adrs: []
created: 2026-04-27
story: CFP-6
---

## §1. 목적

CFP-1에서 도입한 `story_cutoff.additional_exempt_categories` consumer overlay 확장 + "**강제 항목 축소 불허**" invariant가 문서 문구로만 존재했던 gap(Codex 종합 리뷰 P1 #2)을 schema validator로 영구 보존.

CFP-5 Phase A가 mechanical invariant(yaml diff·version·count) 자동화였다면, CFP-6 Phase B는 **schema 기반 자동 검증** 도입.

### 수용 기준

- `overlay/hooks/validate_config.py` SCHEMA_RULES에 `story_cutoff` + `story_cutoff.additional_exempt_categories` 추가 (선택 필드)
- `_check_unknown_keys()` 함수로 schema 정의 외 키 reject (recursive, 모든 nesting level)
- 4 test case 모두 PASS:
  - Test 1: 현 plugin overlay (`story_cutoff` 부재) → OK
  - Test 2: `story_cutoff.additional_exempt_categories: [...]` 확장 → OK
  - Test 3: unknown top-level key (`extra_top_level`, `github_typo`) → ERROR
  - Test 4: 강제 항목 축소 시도 (`story_cutoff.required_categories`, `story_cutoff.remove_force_categories`) → ERROR (schema에 정의 안 해 자동 차단)

## §2. 현재 구조 분석

### 2.1 CFP-1 invariant의 enforcement gap

CLAUDE.md "Story 작성 의무" 섹션 (CFP-1 도입):

> Consumer는 `.claude/_overlay/project.yaml`의 `story_cutoff.additional_exempt_categories[]`로 도메인 특화 면제 항목을 추가할 수 있다 (예: "auto-generated migration files", "vendored library updates"). **강제 항목 축소는 불허** — 안전 방향(면제 추가) 확장만 허용.

이 invariant는 **문서 문구**일 뿐, 실제로 consumer가 `story_cutoff.required_categories: [...]`나 비슷한 키를 overlay에 추가해도 plugin이 검증 안 함. Codex 종합 리뷰 P1 #2 발견.

### 2.2 validate_config.py 현재 상태

`overlay/hooks/validate_config.py` (152줄, SessionStart hook이 호출):
- `SCHEMA_RULES` list of tuples — 17개 규칙 (`project.*`, `github.*`, `labels.components`)
- `_get_path()` recursive dict navigator
- `validate(data)` 모든 rule 검증 → error list
- `main()` argv → file load → validate → exit code

**`story_cutoff` 부재**, **unknown key reject 모드 부재**. SCHEMA_RULES에 정의 안 된 키가 yaml에 있어도 통과.

### 2.3 docs/project-config-schema.md SSOT 정합 필요

CFP-2에서 `docs/project-config-schema.md`에 `story_cutoff.additional_exempt_categories` 추가됨. validator가 이 SSOT와 정합 안 된 상태였음. 본 변경으로 정합.

### 2.4 Mapper 변호 근거

기존 minimal validator를 보존하자는 Mapper 입장: "consumer overlay 검증은 SessionStart에 hook으로 한 번만 동작. unknown key reject 모드는 false positive 위험."

## §3. 도입할 설계

### 3.1 Mapper vs Refactor 대립 결론

채택: **Refactor 우세**.

근거:
- CFP-1 invariant("강제 항목 축소 불허") 자체가 plugin core 정책. 문서 문구만으로는 violation 차단 불가
- unknown key reject는 anti-shrink 자동화의 **유일한 실효 메커니즘**: `required_categories` 같은 가상 키를 SCHEMA_RULES에 정의하지 않으면 reject 모드가 자동으로 차단
- false positive 위험: 매우 낮음 — 모든 known field는 SCHEMA_RULES에 enumerated, 새 field 추가 시 SCHEMA_RULES 갱신이 자연스러운 패턴

Mapper 우려는 §3.4 명확한 error message + schema reference 안내로 흡수.

### 3.2 SCHEMA_RULES 확장

```python
# CFP-1 Story 작성 의무 정책의 consumer overlay 확장 — 안전 방향(면제 추가)만 허용,
# 강제 항목 축소(예: 가상의 'required_categories' 키)는 schema에 정의 안 해 unknown key reject로 자동 차단.
("story_cutoff", False, dict, "story_cutoff section (mapping), optional"),
("story_cutoff.additional_exempt_categories", False, _is_list_of_str,
 "story_cutoff.additional_exempt_categories (list of non-empty strings), optional"),
```

### 3.3 ALLOWED_KEYS_BY_PARENT auto-derived from SCHEMA_RULES

```python
def _build_allowed_keys_by_parent() -> dict[str, set[str]]:
    """SCHEMA_RULES에서 parent dotted-path → set of allowed child keys 매핑 생성."""
    table: dict[str, set[str]] = {}
    for path, *_ in SCHEMA_RULES:
        parts = path.split(".")
        for i in range(len(parts)):
            parent = ".".join(parts[:i])  # "" for root
            child = parts[i]
            table.setdefault(parent, set()).add(child)
    return table

ALLOWED_KEYS_BY_PARENT: dict[str, set[str]] = _build_allowed_keys_by_parent()
```

SCHEMA_RULES가 single source — duplicate maintenance 회피.

### 3.4 `_check_unknown_keys` recursive

```python
def _check_unknown_keys(data: Any, parent_path: str = "") -> list[str]:
    """SCHEMA_RULES에 정의되지 않은 unknown key 탐색 (recursive)."""
    if not isinstance(data, dict):
        return []
    errors: list[str] = []
    allowed = ALLOWED_KEYS_BY_PARENT.get(parent_path, set())
    for key, value in data.items():
        full_path = f"{parent_path}.{key}" if parent_path else key
        if key not in allowed:
            errors.append(
                f"unknown key: {full_path} — schema에 정의되지 않음 "
                f"(allowed at '{parent_path or '<root>'}': {sorted(allowed) or '<none>'})"
            )
            continue
        if isinstance(value, dict):
            errors.extend(_check_unknown_keys(value, full_path))
    return errors
```

`validate(data)` 끝에 `errors.extend(_check_unknown_keys(data))` 추가 — 모든 schema 검증 후 unknown key reject.

### 3.5 ADR 정합성

- ADR-001/ADR-002 무관
- 신규 ADR 필요 없음

## §4. API 계약

### 4.1 Schema 변경

`docs/project-config-schema.md` §2의 `story_cutoff.additional_exempt_categories`가 validator 코드와 정합 — 양측이 SSOT mirror.

### 4.2 Error message 형식

기존 형식 (`missing required field` / `type mismatch`)에 더해:

```
unknown key: <path> — schema에 정의되지 않음 (allowed at '<parent>': [...])
```

명확한 parent path + allowed children list로 사용자가 무엇을 잘못 적었는지 즉시 인지.

### 4.3 Exit code semantics

기존 그대로: 0 valid / 1 usage / 2 dep / 3 yaml parse / 4 schema violation. unknown key는 4번에 통합.

## §5. 변경 계획 (파일 단위)

| 파일 경로 | 변경 유형 | 담당 | 상태 |
|-----------|-----------|------|------|
| `overlay/hooks/validate_config.py` | 수정 (SCHEMA_RULES 2 entries 추가 + ALLOWED_KEYS_BY_PARENT + `_check_unknown_keys` 함수 추가 + `validate()` 끝에 호출) | DocsAgent (= 본 작업자) | 적용 완료 + 4 test PASS |
| `docs/stories/CFP-6.md` | 신규 | DocsAgent | 작성 중 |
| `docs/change-plans/cfp-6-validate-config-story-cutoff.md` | 신규 (본 파일) | DocsAgent | 작성 중 |

## §6. 리팩토링 선행 작업

**없음**. 기존 validator 구조 보존 + 확장.

## §8. Test Contract

### §8.1 커버리지 계획

- 단위 테스트: **N/A** — Python script지만 plugin에 pytest 인프라 없음. Local sim 4 case로 갈음
- 통합 테스트: **`SessionStart` hook 실 호출 시 정상 동작** — push 후 다음 세션 시작에서 자동 검증
- 인프라 테스트: **N/A**

### §8.2 경계 조건·invariant

- **Test 1 — 현 plugin overlay**: `story_cutoff` 키 없음, `labels.components: [...]` 만 → OK
- **Test 2 — `story_cutoff.additional_exempt_categories` 확장**: `["auto-generated migration files", "vendored library"]` → OK
- **Test 3 — Unknown top-level key**: `extra_top_level: "foo"`, `github_typo:` → ERROR with allowed list
- **Test 4 — Force-shrink 시도**: `story_cutoff.required_categories: [P0]`, `story_cutoff.remove_force_categories: [BREAKING]` → ERROR (schema에 정의 안 해 unknown key reject로 자동 차단)
- **Edge case — empty `story_cutoff: {}` (or `null`)**: dict type check 통과하지만 자식 없으므로 OK (additional_exempt_categories는 선택)
- **Edge case — `story_cutoff.additional_exempt_categories: []`**: 빈 list, `_is_list_of_str([])` 의 정의 → 빈 list도 통과 (모든 element가 non-empty str을 만족, 0 elements면 vacuously true). consumer가 명시적으로 비워두는 의도 가능

### §8.3 Perf Baseline

**N/A** — yaml load + dict traversal, ms 수준.

## §9. 분기 선택

**단일 PR**. Phase 1/2 분리 면제.

Commit 시리즈 2개:
- **Commit 1**: `overlay/hooks/validate_config.py` 확장 (SCHEMA_RULES + unknown key reject)
- **Commit 2**: `docs/stories/CFP-6.md` + `docs/change-plans/cfp-6-...md` 영속화

본 PR base는 `main`. CFP-5 PR #32 머지 안 됐어도 변경 영역 별개라 standalone 진행.

## §10. ADR 대상 여부 + 기존 ADR 정합성

- ADR-001/ADR-002 무관
- **신규 ADR 필요 없음**: schema validator 확장은 Process Decision 인프라 적용
