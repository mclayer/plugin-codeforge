# 설정 파일 레퍼런스

설정 파일은 `config/` 디렉토리에 위치한다. `base.yaml`을 기반으로 서비스별 yaml이 deep merge된다.

## 파일 구조

```
config/
├── base.yaml       # 공통 기본값
├── collector.yaml  # collector 전용 설정
└── backtest.yaml   # backtest 전용 설정
```

## base.yaml

```yaml
logging:
  level: INFO           # DEBUG | INFO | WARNING | ERROR
  format: json          # json | text
  output: stdout        # stdout | file
  file_path: /var/log/mctrader/app.log

data:
  root_path: ./data                  # 수집 데이터 저장 루트 (개발: 상대경로)
  orderbook_diff_path: orderbook_diff
  trade_path: trade

exchange:
  default: bithumb
```

> 프로덕션에서는 `data.root_path`를 절대경로(`/var/data/mctrader`)로 변경할 것.
> 환경변수 `MCTRADER_DATA_ROOT`로 오버라이드 가능.

## collector.yaml

```yaml
collector:
  reconnect_interval_sec: 5
  flush_interval_sec: 60   # Parquet flush 주기 (초)
  flush_max_mb: 50         # 버퍼 최대 크기 (MB)
  symbols: all             # all 또는 "BTC_KRW,ETH_KRW"
  orderbook_levels: 15

bithumb:
  ws_url: wss://ws-api.bithumb.com/websocket/v1
```

## backtest.yaml

```yaml
backtest:
  initial_cash: "10000000"       # 초기 자본 (원)
  start_ts: null                 # null이면 CLI/웹 파라미터 사용
  end_ts: null
  symbols: all
  result_path: ./results         # 백테스트 결과 저장 루트 (개발: 상대경로)
  queue_model: naive             # naive | proportional
```

## 환경변수 오버라이드

| 환경변수 | 대응 설정 |
|----------|-----------|
| `MCTRADER_DATA_ROOT` | `data.root_path` |
| `MCTRADER_LOG_LEVEL` | `logging.level` |
