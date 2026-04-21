# Bithumb WebSocket API

## 엔드포인트

| 타입 | URL |
|------|-----|
| Public | `wss://ws-api.bithumb.com/websocket/v1` |
| Private | `wss://ws-api.bithumb.com/websocket/v1/private` |

> ⚠️ 구 엔드포인트 `wss://global-api.bithumb.pro/message/realtime` 는 서비스 종료됨 (NXDOMAIN)

---

## 구독 포맷

최상위는 JSON **배열**. ticket 객체 1개 + type 객체를 나열한다.

### Public (인증 불필요)

```json
[
  {"ticket": "unique-uuid"},
  {"type": "orderbook", "codes": ["KRW-BTC", "KRW-ETH"]},
  {"type": "trade",     "codes": ["KRW-BTC", "KRW-ETH"]}
]
```

| 필드 | 설명 |
|------|------|
| `ticket` | 임의 문자열 (UUID 권장). 재연결 시마다 새로 생성 |
| `type` | `orderbook` \| `trade` \| `ticker` |
| `codes` | `["KRW-BTC"]` 형식 (quote-base, 대시 구분, 대문자) |

### Private (JWT 인증 필요)

```json
[
  {"ticket": "unique-uuid"},
  {"type": "myOrder", "codes": ["KRW-BTC"]}
]
```

Authorization 헤더: `Bearer <JWT token>`

---

## 수신 메시지 포맷

### 공통 필드

| 필드 | 설명 |
|------|------|
| `type` | 메시지 타입 (`ticker`, `orderbook`, `trade`) |
| `code` | 마켓 코드 (`KRW-BTC` 형식) |
| `timestamp` | 서버 수신 시각 (ms) |
| `stream_type` | `SNAPSHOT` (초기 전체) / `REALTIME` (이후 업데이트) |
| `ask_bid` | `BID` (매수) / `ASK` (매도) |

### Ticker (실측 확인)

```json
{
  "type": "ticker",
  "code": "KRW-BTC",
  "opening_price": 484500,
  "high_price": 493100,
  "low_price": 472500,
  "trade_price": 493100,
  "trade_volume": 3.2529,
  "trade_timestamp": 1725927377174,
  "ask_bid": "BID",
  "timestamp": 1725927377287,
  "stream_type": "SNAPSHOT"
}
```

### Orderbook

```json
{
  "type": "orderbook",
  "code": "KRW-BTC",
  "timestamp": 1725927377287,
  "total_ask_size": 1.234,
  "total_bid_size": 2.345,
  "orderbook_units": [
    {"ask_price": 95000000, "ask_size": 0.01, "bid_price": 94990000, "bid_size": 0.05},
    {"ask_price": 95010000, "ask_size": 0.02, "bid_price": 94980000, "bid_size": 0.03}
  ],
  "stream_type": "SNAPSHOT"
}
```

### Trade

```json
{
  "type": "trade",
  "code": "KRW-BTC",
  "trade_price": 95000000,
  "trade_volume": 0.001,
  "trade_timestamp": 1725927377174,
  "sequential_id": 1725927377174000001,
  "ask_bid": "BID",
  "stream_type": "REALTIME"
}
```

---

## 심볼 코드 변환 규칙

mctrader 내부 도메인과 거래소 코드 형식이 다름.

| 위치 | 형식 | 예시 |
|------|------|------|
| 내부 도메인 | `{base}_{quote}` | `BTC_KRW` |
| 거래소 코드 | `{quote}-{base}` | `KRW-BTC` |

변환은 adapter layer (`codec.py`, `ws_client.py`)에서만 수행.

```python
# 내부 → 거래소
f"{symbol.quote}-{symbol.base}"   # BTC_KRW → KRW-BTC

# 거래소 → 내부
quote, base = code.split("-")     # KRW-BTC → base=BTC, quote=KRW
```

---

## mctrader 구현 파일

| 파일 | 역할 |
|------|------|
| `src/mctrader/adapters/exchanges/bithumb/ws_client.py` | WebSocket 연결 및 구독 관리 |
| `src/mctrader/adapters/exchanges/bithumb/codec.py` | 메시지 파싱 → 도메인 이벤트 변환 |
| `config/collector.yaml` | `ws_url` 설정 |

---

## 변경 이력

| 날짜 | 내용 |
|------|------|
| 2026-04-21 | Bithumb Pro (`global-api.bithumb.pro`) → Bithumb Korea WS v1 (`ws-api.bithumb.com`) 마이그레이션 |
