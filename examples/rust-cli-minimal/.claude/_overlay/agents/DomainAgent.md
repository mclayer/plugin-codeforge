### 도메인 소스 (Log Parser — Rust)

- Domain Knowledge: `docs/domain-knowledge/logparser/**`
- ADR 카테고리 (frontmatter `category:`): `domain-logparser`
- 도메인 코드: `src/parsers/**`, `src/events/**`, `src/filters/**`
- 도메인 용어: Log Line, Event, Parser Profile, Filter

### 핵심 개념

| 용어 | 정의 | 주요 invariant |
|------|------|----------------|
| **Log Line** | 입력 스트림의 raw text 한 줄 | 개행 문자로 구분, UTF-8 유효성 검증 |
| **Event** | 구조화된 파싱 결과 `{level, message, fields}` | level은 `debug\|info\|warn\|error\|fatal` enum, 필드 = 비-Copy String |
| **Parser Profile** | 포맷별 파싱 규칙 (정규식·필드 매핑) | 동일 Log Line에 여러 Profile 매칭 허용, 첫 매칭 적용 |
| **Filter** | Event stream 선별 조건 | AST 기반 예측 가능한 DSL (사용자 정의 함수 금지 — 보안) |

### 지원 로그 포맷 (초기)

- `<REPLACE: nginx access log / syslog / JSON Lines / log4j / 프로젝트 고유 포맷>`
- 추가 포맷은 Parser Profile 형태로 확장

### 우선순위 원칙

- **처리율 최우선**: 대용량 로그 파일 (GB급) 스트리밍 처리. p95 지연 < 10ms per Event
- **메모리 상한**: 전체 입력 로드 금지 — 라인 단위 스트리밍 (`BufRead::lines()`)
- **정확성 > 유연성**: 파싱 실패 시 조용히 드롭 말고 error event 발행 (downstream 집계 가능)

### 금지 사항

- Event 필드 값의 PII 자동 검출·마스킹 없음 (별도 툴 책임) — 단 문서에 주의 명시
- Parser Profile이 arbitrary code 실행 금지 (정규식·선언적 매핑만 허용)
- Filter DSL에 네트워크·파일 I/O 금지 (순수 predicate만)
