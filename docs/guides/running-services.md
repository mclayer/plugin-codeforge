# 서비스 실행 가이드

## Dashboard 서버

### 실행 방법

```bash
# 권장 (nohup 사용)
nohup .venv/bin/python -m mctrader.cli.dashboard_main --result-dir ./results > /tmp/dashboard.log 2>&1 &

# 또는 직접 uvicorn (포그라운드)
.venv/bin/python -c "
import uvicorn
from mctrader.dashboard.server import create_app
app = create_app('./results')
uvicorn.run(app, host='127.0.0.1', port=8080)
"
```

기본 URL: http://127.0.0.1:8080

### 주의사항

- `&` 단독 백그라운드 실행 시 SIGHUP으로 즉시 종료됨 → 반드시 `nohup` 사용
- 포트 충돌 확인: `lsof -i :8080`
- 포트 충돌 시 `--port` 옵션으로 변경

### 페이지 구성

| URL | 내용 |
|-----|------|
| `/` | 백테스트 결과 목록 |
| `/run/{run_id}` | 개별 백테스트 상세 (에퀴티 커브, 체결 내역) |
| `/compare` | 여러 백테스트 비교 |
| `/backtest` | 백테스트 실행 페이지 |
| `/collector` | 수집 프로세스 상태 및 심볼별 통계 ([상세](./dashboard-collector-data.md)) |
| `/data` | Parquet 데이터 조회 ([상세](./dashboard-collector-data.md)) |
| `/admin` | 전역 설정 관리 |

---

## Collector

### 선행 조건

백테스트에 필요한 데이터를 수집한다. **백테스트 전에 반드시 collector를 먼저 실행해 데이터를 쌓아야 한다.**

### 실행 방법

```bash
nohup .venv/bin/python -m mctrader.cli.collector_main > /tmp/collector.log 2>&1 &
```

### 데이터 저장 위치

```
./data/
├── orderbook_diff/symbol=BTC_KRW/date=20260421/hour=09.parquet
└── trade/symbol=BTC_KRW/date=20260421/hour=09.parquet
```

- `flush_interval_sec: 60` — 60초마다 Parquet으로 flush
- 수집 후 데이터가 쌓이면 백테스트 실행 가능

---

## Backtest

### 실행 순서

1. Collector로 데이터 수집 (위 참고)
2. 웹 UI (`/backtest`) 또는 CLI로 실행

### CLI 실행

```bash
.venv/bin/python -m mctrader.cli.backtest_main \
  --start "2026-04-20 09:00:00" \
  --end   "2026-04-21 09:00:00" \
  --symbols BTC_KRW \
  --queue-model naive
```

### 날짜/시각 포맷 (지원 형식)

| 형식 | 예시 |
|------|------|
| 날짜만 | `2026-04-21` |
| 날짜+시각 | `2026-04-21 09:44:00` |
| HTML datetime-local | `2026-04-21T09:44` |

### 결과 저장 위치

```
./results/{YYYYMMDD_HHMMSS_xxxxxx}/
├── summary.json
├── trades.parquet
└── equity_curve.parquet
```
