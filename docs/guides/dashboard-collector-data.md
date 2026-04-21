# Collector & Data 대시보드 가이드

`/collector` 와 `/data` 페이지는 실시간으로 시장 데이터 수집 파이프라인을 관찰하고 저장된 Parquet 를 탐색하기 위한 UI 이다. 모두 FastAPI + Jinja2 (Bootstrap 5 dark) 로 구현되어 있고 Hexagonal 구조(ADR-001)에서 대시보드 어댑터 계층에 속한다.

## 엔드포인트 요약

| Path | Method | 설명 |
|------|--------|------|
| `/collector` | GET | Collector 상태 HTML |
| `/api/collector/status` | GET | Collector 상태 JSON |
| `/data` | GET | 데이터 조회 HTML (query string 으로 필터) |
| `/api/data/query` | GET | 데이터 조회 JSON (symbol / event_type / start / end) |

모든 시간은 **UTC** 로 해석/표시된다. `start`, `end` 는 HTML datetime-local 포맷 `YYYY-MM-DDTHH:MM`.

## `/collector` 페이지

### 표시 항목

1. **Process 카드** — Collector 프로세스 on/off, PID
   - 판별 로직: `ps -axo pid,command` 의 명령어에 `mctrader-collector`, `mctrader.app.collector_service`, `run_collector` 중 하나가 포함되면 running
   - `ps` 호출이 실패하면 `UNKNOWN` 표시 (대시보드는 계속 동작)
2. **심볼별 통계 테이블** — 심볼, orderbook row 수, trade 수, 마지막 수신 시각 (UTC)
   - DuckDB `COUNT(*), MAX(ts)` 로 각 event_type 당 한 번씩 집계
   - orderbook_diff 는 이벤트당 level 수만큼의 row 가 저장되므로 "raw row 수" 로 표기됨을 헤더 툴팁으로 명시
3. **오늘의 Parquet 파일 목록** — 오늘(UTC) 디렉토리의 모든 `.parquet` 파일의 타입/심볼/시간/파일명/크기(MB)/수정 시각

### 자동 갱신
페이지는 30 초마다 `window.location.reload()` 로 새로고침하며 우측 상단 `Refresh` 버튼으로 수동 갱신 가능.

## `/data` 페이지

### 필터
- **Symbol** — `data/{orderbook_diff,trade}/symbol=*` 디렉토리를 스캔해 드롭다운 구성
- **Type** — `orderbook_diff` 또는 `trade`
- **Start / End (UTC)** — datetime-local, 기본값은 오늘 00:00 ~ 현재

### 결과 테이블
- 최대 **200 행** (상수 `MAX_ROWS`) 으로 제한
- 전체 매칭 수와 표시 수를 카드 헤더에 함께 노출, truncated 여부 표시
- `side` 는 bid/buy 녹색, ask/sell 적색 배지로 구분

### 쿼리 경로
`src/mctrader/dashboard/data_query.py::query()` 가 DuckDB `read_parquet(..., hive_partitioning=true)` 를 통해 partition pruning + `WHERE symbol = ? AND ts BETWEEN ? AND ?` 로 조회한다. `LIMIT` 이 쿼리에 주입되어 메모리 사용이 제한된다.

## 관련 파일

- `src/mctrader/dashboard/server.py` — 라우트 및 Jinja 필터 등록
- `src/mctrader/dashboard/collector_status.py` — 프로세스 탐지 + 집계 로직
- `src/mctrader/dashboard/data_query.py` — DuckDB 조회 어댑터
- `src/mctrader/dashboard/templates/collector.html`
- `src/mctrader/dashboard/templates/data.html`
- `tests/unit/test_collector_status.py`
- `tests/unit/test_data_query.py`
- `tests/unit/test_dashboard_server.py` (라우트 스모크 테스트)

## 관련 ADR

- ADR-001 Hexagonal Architecture — 대시보드는 어댑터 계층, domain/ports 수정 없음
- ADR-003 Parquet + DuckDB — 조회는 DuckDB `read_parquet` 에 의존, 별도 인덱스/캐시 없음
- ADR-008 Linux + systemd — 프로세스 탐지는 `ps` 명령 단독 (외부 의존성 없음)
