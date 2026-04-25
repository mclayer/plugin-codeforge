### 도메인 소스 (Schema Guard)

- Domain Knowledge: `docs/domain-knowledge/schema-validation/**`
- ADR 카테고리 (frontmatter `category:`): `domain-schema-validation`
- 도메인 코드: `src/<lib>/public/**`, `src/<lib>/internal/**`, `src/<lib>/types/**`
- 도메인 용어: Schema, Validator, Result, Error Path, Custom Rule

### 핵심 개념

| 용어 | 정의 | 주요 invariant |
|------|------|----------------|
| **Schema** | 데이터 구조·제약 선언 | 불변 — 생성 후 수정 금지 (thread-safe) |
| **Validator** | `validate(schema, data) → Result` | 순수 함수 — 같은 입력 → 같은 출력, 부작용 없음 |
| **Result** | OK 또는 Error 집합 | 단축 평가 없음 — 모든 실패 경로 수집 (사용자 UX) |
| **Error Path** | `.field[idx].nested` 형식 | 중첩 depth 제한 없음, 모든 경로 완전 명시 |
| **Custom Rule** | `fn(value) → bool | Error` | 순수 predicate만 — I/O·네트워크 호출 금지 |

### 지원 대상 데이터 타입 (최소 기반)

- Primitives: string, integer, float, boolean, null
- Containers: object(dict), array(list), union(one-of)
- Constraints: min/max, regex pattern, enum, required fields
- 확장 (Custom Rule로 사용자 정의)

### 우선순위 원칙

- **정확성 > 성능**: 검증 실패 정보는 완전해야 함 (모든 path 수집). 병렬 검증도 순서 보존.
- **API 안정성 > 유연성**: 공개 API 변경은 semver 계약. Change Plan에서 API 영향 평가 선행.
- **에러 메시지 품질**: 사용자가 디버깅 가능한 path·expected·actual·rule name 포함.

### 금지 사항

- Custom Rule이 **외부 시스템 호출** (DB·HTTP·파일) 금지 — 재현성·성능 모두 해침. 그런 검증은 사용자가 상위 레이어에서 수행.
- Schema 인스턴스를 수정하는 공개 메소드 금지 — immutable만 지원.
- 내부 타입·함수가 `__all__` / `pub` 외부로 유출 금지 (공개 surface 최소화).
