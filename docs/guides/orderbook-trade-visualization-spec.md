# OrderBook / Trade 시각화 도메인 스펙

작성 주체: ResearcherAgent (기록: DocsAgent)
대상 독자: ArchitectAgent, CodePLAgent, DataEngineerAgent, 프론트엔드 구현자
관련 ADR: ADR-002 (OrderBook Diff-only 저장), ADR-006 (Bithumb 우선), ADR-007 (OrderBook Imbalance 전략), ADR-010 (Dashboard Web Interface)

본 문서는 mctrader의 L2 OrderBook / Trade 데이터를 스캘핑 트레이더에게 유의미하게 제시하기 위한 도메인 해석과 뷰 모델 스키마를 정의한다. Python 백엔드(FastAPI)와 JS 프론트엔드가 동일한 필드명·단위·의미를 공유하도록 단일 스키마를 규정한다.

---

## 1. L2 OrderBook 특성 및 변환 규칙

### 1.1 용어 정의
- **L2 OrderBook**: 가격 레벨별 총 주문 수량만 보이는 호가창. 개별 주문 ID는 노출되지 않는다 (L3와의 차이).
- **Level**: `(price, qty)` 쌍. `price`는 가격 tick에 스냅되어 있으며, `qty`는 해당 가격에 쌓여 있는 모든 주문의 합산 수량.
- **Bid**: 매수 호가. best bid = 가장 높은 매수 가격.
- **Ask (Offer)**: 매도 호가. best ask = 가장 낮은 매도 가격.
- **Spread**: `best_ask - best_bid`. 항상 `>= 0` (정상 시장).
- **Mid price**: `(best_bid + best_ask) / 2`.
- **Tick size**: 거래소가 정한 가격 단위. Bithumb KRW 마켓은 가격 구간별 tick이 다름 (e.g., 1,000원 미만 = 0.1원, 1M원 이상 = 1,000원).

### 1.2 Snapshot vs Diff
- **Snapshot**: 특정 시점의 전체 호가 상태 (상위 N 레벨 전부).
- **Diff (delta)**: 이전 상태 대비 변경된 레벨만 전송. mctrader는 ADR-002에 따라 **Diff-only 저장**을 채택했으며, Snapshot은 메모리에서 재구성한다.

### 1.3 Diff → Snapshot 변환 규칙

현재 구현(`src/mctrader/domain/orderbook.py`):

1. `apply_diff(event)` 호출 시 `bids_delta`, `asks_delta`를 순회한다.
2. 각 `(price, qty)` 튜플에 대해:
   - `qty == 0` → 해당 price 레벨을 **삭제** (dict.pop)
   - `qty > 0`  → 해당 price 레벨의 수량을 `qty`로 **교체** (누적 아님)
3. `snapshot()` 호출 시:
   - bids: price **내림차순** 정렬 (best bid 가 index 0)
   - asks: price **오름차순** 정렬 (best ask 가 index 0)
4. `ts`, `seq`는 마지막 diff 이벤트의 값을 반영.

### 1.4 qty=0 의미
- "해당 가격 레벨이 비었다(완전 취소/전량 체결)"는 신호.
- 주의: `qty=0`은 **가격 레벨 제거**이지, 수량을 0으로 설정하는 것이 아니다. Snapshot에서는 해당 price 자체가 사라진다.

### 1.5 정렬 기준
- **Bid 정렬**: 가격 내림차순. 최우선(best) = 가장 비싼 매수 호가.
- **Ask 정렬**: 가격 오름차순. 최우선(best) = 가장 싼 매도 호가.
- Ladder(DOM) UI에서는 ask를 위, bid를 아래로 배치하며, 중앙(= mid price 근처)에서 만나도록 정렬한다.

### 1.6 seq gap 처리
- `seq`는 거래소가 부여하는 단조 증가 번호. gap(결번)이 발생하면 중간 diff 유실을 의미.
- 권장 처리 정책:
  1. **Strict mode (backtest)**: gap 감지 시 fail-fast. 데이터 무결성 우선.
  2. **Lenient mode (live)**: gap 감지 시 경고 로그 + 스냅샷 재구독(REST snapshot 재요청) 또는 WebSocket 재연결.
- 현재 `OrderBook.apply_diff()`는 gap 검증을 하지 않음. 상위 레이어(`BithumbWsClient` 또는 `CollectorService`)가 책임져야 함 — ArchitectAgent 결정 필요 포인트.

### 1.7 거래소별 표준 레벨 수
- **Binance (업계 표준)**: `depth5`, `depth10`, `depth20`, `depth50`, full book 제공. 대시보드 전형은 **20 레벨** (상위 20 bid + 상위 20 ask).
- **Bithumb**: 공식 WS 스트림은 **상위 30 레벨**까지 제공 (ORDERBOOKDEPTH). 대시보드 UI는 15~20 레벨 노출이 일반적.
- **스캘핑 관례**: Ladder에 **15~25 레벨**을 한 화면에 표시. 중앙에 best bid/ask를 두고 위아래로 대칭.
- **Imbalance 지표 계산용**: top **5~10** 레벨이 업계 표준 (mctrader 현재 구현: 기본 5).

### 1.8 가격/수량 표현
- **가격**: `Decimal` → 직렬화 시 **문자열**. float 변환 금지 (호가 tick 손실 위험).
- **수량**: `Decimal` → 문자열. KRW 마켓에서 BTC/ETH는 소수점 8자리까지 의미 있음.
- **JSON 직렬화 규칙**: 모든 가격/수량/누적수량 필드는 `str`. 프론트는 BigNumber/Decimal.js로 파싱해야 정확하나, 차트 표시용으로 `Number()` 변환을 허용 (소수점 8자리 이내에서는 IEEE 754로 안전).

---

## 2. Trade 데이터 특성

### 2.1 정의
체결(execution)이 일어날 때마다 1건씩 생성되는 이벤트. L2 OrderBook의 "flow" 측면을 보여주는 데이터.

### 2.2 필드 의미
- `ts`: 체결 시각 (거래소 서버 기준, epoch ms).
- `seq`: 거래소가 부여한 체결 순번 (단조 증가).
- `price`: 체결 가격 (Decimal 문자열).
- `qty`: 체결 수량 (Decimal 문자열).
- `side`:
  - `"buy"` = taker가 매수자. 매수자가 ask 호가를 hit → **업틱(uptick) 압력**.
  - `"sell"` = taker가 매도자. 매도자가 bid 호가를 hit → **다운틱(downtick) 압력**.
  - **중요**: 암호화폐 거래소 관례상 side는 "taker의 방향"이다. Bithumb 역시 taker 기준.

### 2.3 체결 크기 분포 (size_bucket)
체결 크기는 long-tail 분포를 가지며, 시장가 대규모 체결(large print)은 단기 가격 방향 시그널이 된다.

**권장 buckets (백분위수 기반, 해당 심볼의 최근 세션 단위로 산출)**:

| Bucket | 기준 | 시각화 |
|--------|------|--------|
| `small` | qty ≤ P75 | 기본 색상, 작게 |
| `med`   | P75 < qty ≤ P95 | 기본 색상, 보통 크기 |
| `large` | qty > P95 | 강조 배경 (buy=진한 초록 / sell=진한 빨강), 행 전체 하이라이트 |

**산출 방식**:
- **Rolling window**: 최근 N분 (권장 5~15분) 또는 최근 M건 (권장 1,000~5,000건)의 qty 분포에서 P75/P95 계산.
- **Per symbol**: 심볼마다 분포가 다르므로 (BTC 1건 vs SHIB 1건의 무게가 전혀 다름) 반드시 심볼별로 산출.
- 단위: **qty 기준** 또는 **notional(= price × qty) 기준** 둘 다 가능. 스캘핑에서는 **notional(KRW) 기준**이 트레이더 직관에 더 잘 맞음.

### 2.4 가격 변동 방향 (tick direction)
각 trade는 직전 trade 대비 가격 방향을 가진다:
- `uptick`: price > prev_price
- `downtick`: price < prev_price
- `zero-uptick`: price == prev_price, 직전 비-제로 틱은 uptick
- `zero-downtick`: price == prev_price, 직전 비-제로 틱은 downtick

Tape UI의 가격 셀에 ↑/↓ 화살표 및 옅은 배경색으로 표시.

---

## 3. 스캘핑 필수 시각화 3종

### 3.1 Ladder (DOM, Depth of Market)

**목적**: 호가 스택을 가격 축 기준으로 한눈에 보여주고, 어느 레벨에 유동성이 쌓였는지/빠지는지 추적.

**레이아웃**:
```
┌──────────┬────────────┬──────────┐
│ BID QTY  │   PRICE    │ ASK QTY  │
├──────────┼────────────┼──────────┤
│          │ 50,250,000 │   0.3421 │  ← ask (오름차순 → 위쪽 = 먼 가격)
│          │ 50,240,000 │   0.1200 │
│          │ 50,230,000 │   0.0500 │  ← best ask
├──────────┼════════════┼──────────┤
│  0.0820  │ 50,220,000 │          │  ← best bid
│  0.1500  │ 50,210,000 │          │
│  0.3000  │ 50,200,000 │          │
└──────────┴────────────┴──────────┘
```

**필수 컬럼**:
| 컬럼 | 타입 | 설명 |
|------|------|------|
| `price` | str (Decimal) | 가격 레벨 |
| `bid_qty` | str | 해당 가격의 매수 잔량 (ask 쪽 행이면 빈 값) |
| `ask_qty` | str | 해당 가격의 매도 잔량 (bid 쪽 행이면 빈 값) |
| `cumulative_bid` | str | best bid부터 해당 레벨까지 누적 (자기 포함) |
| `cumulative_ask` | str | best ask부터 해당 레벨까지 누적 (자기 포함) |
| `is_best` | bool | best bid/ask 여부 |

**시각 강조**:
- **Best bid/ask**: 굵은 테두리 또는 배경 하이라이트 (중앙 분리선).
- **Depth bar**: 각 행에 bid_qty/ask_qty 크기에 비례한 수평 바를 배경으로 렌더 (bid는 오른쪽 정렬 초록, ask는 왼쪽 정렬 빨강).
- **Imbalance 색상**: 상위 N 레벨 imbalance가 임계 초과 시 Ladder 헤더 색상 변경 (매수 우세 = 초록, 매도 우세 = 빨강).
- **업데이트 애니메이션**: qty 변경 시 해당 행을 150~300ms 플래시.

**레벨 수**: 기본 **20 레벨** (bid 20 + ask 20). 설정으로 10/20/30 전환 가능.

### 3.2 Tape (Time & Sales)

**목적**: 체결 스트림을 실시간으로 보면서 "지금 공격적으로 사고 있는가 / 팔고 있는가"를 감지.

**레이아웃**: 테이블, 최신이 **맨 위** (역시간순). 스크롤 가능, 최대 N행(권장 500) 유지.

**필수 컬럼**:
| 컬럼 | 타입 | 설명 |
|------|------|------|
| `ts` | int (epoch ms) → UI에서 HH:MM:SS.mmm 포맷 | 체결 시각 |
| `price` | str | 체결 가격 |
| `qty` | str | 체결 수량 |
| `side` | str ("buy"/"sell") | taker 방향 |
| `size_bucket` | str ("small"/"med"/"large") | 크기 구간 |
| `tick_dir` | str ("up"/"down"/"zero-up"/"zero-down") | 가격 변동 방향 |
| `notional` | str | price × qty (UI에서 천단위 구분 표시) |

**시각 강조**:
- **Side 색상**: buy=초록 배경/폰트, sell=빨강.
- **Large print**: `size_bucket == "large"` 행 전체 진한 배경 + 폰트 bold.
- **Tick 화살표**: price 셀 좌측에 ↑ (up) / ↓ (down) / · (zero-tick).
- **Streaming**: 신규 체결은 맨 위에 삽입 + 300ms 글로우 효과.

### 3.3 Imbalance 시계열

**목적**: 상위 호가의 매수/매도 잔량 균형을 시간축으로 추적. ADR-007 전략의 핵심 입력.

**정의 (mctrader 현재 구현과 일치)**:
```
imbalance(t) = (Σ bid_qty[i] - Σ ask_qty[i]) / (Σ bid_qty[i] + Σ ask_qty[i])
               for i in top-N levels
```
- 범위: **[-1.0, +1.0]**
- +1 = 상위 N 레벨이 전부 bid만 있음 (극단적 매수 우세)
- -1 = 극단적 매도 우세
-  0 = 완전 균형

**N의 의미**: mctrader 기본값 **5**. 설정으로 3/5/10 변경 가능. N이 커질수록 smoother, 작을수록 반응 빠름.

**시각 디자인**:
- **Primary**: 라인 차트. X=시간, Y=imbalance (-1 ~ +1 고정 스케일).
- **기준선**: y=0 회색 실선. y=±threshold (ADR-007: 기본 0.3) 점선으로 표시.
- **컬러 밴드**: `imbalance > +threshold` 구간 초록, `< -threshold` 구간 빨강, 중간은 회색.
- **보조 축 (선택)**: 동일 X축 위에 mid price 라인 overlay → imbalance와 가격 움직임 간 상관 시각화.
- **해상도**: Tick-by-tick(매 diff마다) 또는 샘플링(100ms/250ms bucket). 대시보드는 **250ms bucket 권장** (초당 4 포인트 → 5분 = 1,200 포인트, 렌더 부하 관리 가능).

---

## 4. 2차 시각화

### 4.1 Depth Chart

**정의**: 누적 bid/ask 볼륨을 가격 축 위에 면적 차트로.
- X축: price (mid price 중심, 좌측=bid, 우측=ask)
- Y축: cumulative_qty (또는 cumulative_notional)
- 좌측(bid) 초록 계단식 채움, 우측(ask) 빨강 계단식 채움.

**수식**:
```
cum_bid(p) = Σ qty[i] for price[i] >= p  (bid side)
cum_ask(p) = Σ qty[i] for price[i] <= p  (ask side)
```

**활용**: 큰 지지/저항 "벽(wall)" 식별. Ladder의 누적 컬럼을 공간적으로 보완.

### 4.2 CVD (Cumulative Volume Delta)

**정의**: 체결량의 방향성 누적.
```
delta(trade) = +qty  if side == "buy"
             = -qty  if side == "sell"
CVD(t) = Σ delta(trade) for trade.ts <= t
```
세션 시작(혹은 N분 rolling) 기준으로 누적.

**시각**: 라인 차트. X=시간, Y=CVD. mid price 라인과 overlay하면 divergence 포착 가능 (가격은 오르는데 CVD 하락 → 약세 신호).

**단위**: qty 또는 notional. 스캘핑용은 notional(KRW) 권장.

### 4.3 Volume Profile

**정의**: 가격대별 체결 누적량의 가로 히스토그램.
- Y축: price (bucket 단위, 예: tick×10 또는 K원 단위)
- X축: 해당 가격대에서 발생한 누적 qty 또는 notional
- POC (Point of Control): 최대 volume bucket 강조.
- VAH/VAL: 70% volume 포함 구간 경계.

**활용**: 세션 내 주요 거래 레벨 식별. Ladder 옆에 사이드바로 배치하면 가격 축 정합.

---

## 5. 뷰 모델 스키마 (Python dataclass)

백엔드 → 프론트 JSON 전송 형식. 모든 가격·수량은 **문자열 (Decimal 보존)**. float/Number는 비율·각도 등 손실 허용 값에만 사용.

```python
from dataclasses import dataclass, field
from typing import Literal

Side = Literal["buy", "sell"]
BookSide = Literal["bid", "ask"]
SizeBucket = Literal["small", "med", "large"]
TickDir = Literal["up", "down", "zero-up", "zero-down"]


@dataclass(frozen=True)
class LevelView:
    price: str            # Decimal 문자열
    qty: str              # Decimal 문자열
    cumulative_qty: str   # best부터 해당 레벨까지 누적 (자기 포함)


@dataclass(frozen=True)
class SnapshotView:
    ts: int                        # epoch ms
    seq: int                       # 마지막 반영된 diff seq
    symbol: str                    # 예: "BTC_KRW"
    market: str                    # 예: "bithumb"
    bids: list[LevelView]          # best bid first (가격 내림차순)
    asks: list[LevelView]          # best ask first (가격 오름차순)
    mid: str                       # (best_bid + best_ask) / 2, Decimal 문자열
    spread: str                    # best_ask - best_bid
    spread_bps: float              # spread / mid * 10_000 (소수 허용)
    imbalance: float               # top-N imbalance, -1.0 ~ +1.0
    imbalance_depth: int           # N (몇 레벨 기준으로 계산했는가)
    depth: int                     # len(bids) == len(asks), 전달 레벨 수


@dataclass(frozen=True)
class TapeEntryView:
    ts: int                        # epoch ms
    seq: int                       # 거래소 체결 seq
    symbol: str
    market: str
    price: str
    qty: str
    side: Side
    size_bucket: SizeBucket
    tick_dir: TickDir
    delta: str                     # +qty (buy) / -qty (sell), Decimal 문자열
    notional: str                  # price * qty, Decimal 문자열


@dataclass(frozen=True)
class ImbalancePoint:
    ts: int                        # epoch ms (bucket 시작)
    imbalance: float               # -1 ~ +1
    mid: str                       # 해당 bucket의 대표 mid
    spread_bps: float


@dataclass(frozen=True)
class CVDPoint:
    ts: int                        # epoch ms
    cvd: str                       # Decimal 누적 (qty 또는 notional — 헤더에 unit 표기)
    unit: Literal["qty", "notional"]
    price: str                     # 해당 시점 체결가 (divergence 분석용)


@dataclass(frozen=True)
class VolumeProfileBucket:
    price_lo: str                  # bucket 하한
    price_hi: str                  # bucket 상한
    volume: str                    # 해당 bucket 누적 qty
    notional: str                  # 해당 bucket 누적 notional
    is_poc: bool                   # Point of Control 여부


@dataclass(frozen=True)
class DepthChartPoint:
    price: str
    cumulative_qty: str
    side: BookSide                 # "bid" | "ask"
```

### 5.1 WebSocket / REST 메시지 envelope

대시보드 전송 시 envelope:
```python
@dataclass(frozen=True)
class DashboardMessage:
    type: Literal["snapshot", "tape", "imbalance", "cvd", "depth", "volume_profile"]
    symbol: str
    market: str
    payload: dict   # 위 dataclass 중 하나를 dict 직렬화한 값
    server_ts: int  # 서버가 메시지를 내보낸 시각 (지연 측정용)
```

### 5.2 필드명 일관성 규칙
- **Python**: `snake_case` (위 스키마).
- **JSON**: **동일한 snake_case** 유지 (자동 변환 금지 — 프론트/백 혼동 방지).
- **TypeScript 인터페이스**: Python dataclass를 그대로 거울 (필드명 identical).
- 단위를 필드명에 명시: `spread_bps` (bps임이 명확), `imbalance_depth` (값이 N임이 명확).

---

## 6. ADR-007 연계 포인트

ADR-007("틱띠기 OrderBook Imbalance 전략")의 시그널은 본 시각화의 `imbalance` 값과 **동일한 수식**을 사용한다.

### 6.1 수식 일치 (불변)
```
imbalance = (Σ bid_qty[i] - Σ ask_qty[i]) / (Σ bid_qty[i] + Σ ask_qty[i])
            for i in 0..N-1
```
- 구현: `src/mctrader/strategy/examples/order_imbalance.py::_calc_imbalance`
- 시각화 `SnapshotView.imbalance`, `ImbalancePoint.imbalance`와 **반드시 동일 로직**으로 산출되어야 한다. 중복 구현 금지 — 공용 유틸(예: `domain/orderbook.py` 또는 신설 `domain/microstructure.py`)로 추출 권장.

### 6.2 임계값 매핑
ADR-007 현재 기본값:
- `levels = 5`
- `threshold = 0.3`
- `imbalance > +0.3` → LONG 시그널
- `imbalance < -0.3` → SHORT/청산 시그널

Imbalance 시계열 차트는 **y = ±0.3 점선**을 그려 트레이더가 전략 시그널 발생 순간을 눈으로 확인할 수 있게 한다. 대시보드 UI에서 threshold를 설정 위젯으로 노출하면, 백테스트/튜닝 시 효과적.

### 6.3 시그널 마커 오버레이
Imbalance 시계열 차트 위에:
- 초록 ▲: 실제 LONG 시그널 발생 시점
- 빨강 ▼: SHORT 시그널 발생 시점
- 주문 체결 시점은 별도 마커로 mid price 라인에 표시 (slippage 시각화)

백테스트 결과 파일(results/)과 조인하여 렌더.

### 6.4 대시보드 튜닝 루프
트레이더가 대시보드에서 levels/threshold를 바꾸면 → 동일 기간 데이터로 imbalance 재계산 → 시그널 빈도·분포 즉시 표시. 이것이 ADR-007 전략을 "감각적으로" 튜닝하는 도구.

---

## 7. 구현 우선순위 권장

ArchitectAgent가 로드맵을 짤 때 참고할 우선순위. MVP부터 점진 확장.

### Phase 1 — MVP (필수, ADR-007 튜닝에 직결)
1. **SnapshotView + Ladder 렌더**
   - 백엔드: `OrderBook.snapshot()` → `SnapshotView` 어댑터 (누적량·spread·mid·imbalance 계산 포함).
   - 프론트: Bootstrap 기반 DOM 테이블, 20 레벨 고정.
   - depth bar(background gradient)만 적용, 애니메이션은 Phase 2.
2. **TapeEntryView + Tape 스트림**
   - 백엔드: Trade parquet → 최근 500건 tail + size_bucket 계산.
   - 프론트: 단순 테이블, buy/sell 색상 구분, large print 강조.
   - size_bucket 기준은 **rolling 5분 notional 분포의 P75/P95**로 시작.
3. **ImbalancePoint 시계열 + 차트**
   - 백엔드: 250ms bucket aggregation 엔드포인트.
   - 프론트: Chart.js 또는 uPlot. threshold 점선 고정 표시.

### Phase 2 — 튜닝 및 UX 강화
4. Ladder 업데이트 애니메이션 (qty 변경 flash, 신규 level 슬라이드).
5. Imbalance 차트에 mid price overlay 및 시그널 마커.
6. Ladder에 imbalance 헤더 하이라이트 (현재 상태 요약).
7. 심볼/마켓 셀렉터, 레벨 수 토글 (10/20/30), imbalance N 토글.

### Phase 3 — 심화 분석 (2차 시각화)
8. Depth Chart (면적형).
9. CVD 시계열 (mid overlay와 divergence 강조).
10. Volume Profile 사이드바.

### Phase 4 — 퍼포먼스·확장
11. WebSocket 푸시 전환 (현재 HTTP 폴링이라면).
12. 다중 심볼 멀티 패널 (4-up 레이아웃).
13. 사용자 레이아웃 저장 (localStorage).
14. Volume Profile rolling window 설정.

### 비-기능 요구 (모든 Phase 공통)
- **타임존**: ADR-011에 따라 서버사이드 zoneinfo 변환. 프론트는 수신값을 그대로 표시 (UTC/KST 라벨 포함).
- **Decimal 보존**: 가격·수량은 문자열 유지. 차트 렌더 시에만 Number 변환 (소수 8자리 이내 안전).
- **지연 측정**: 모든 envelope에 `server_ts` 포함 → 프론트가 현재 시각과 비교해 p50/p95 latency 표시.
- **데이터 공백 처리**: Collector 다운 구간은 차트에서 끊긴 선으로 표기 (Chart.js `spanGaps: false`).

---

## 8. 결정이 필요한 열린 질문 (ArchitectAgent 대상)

1. **공용 imbalance 유틸 위치**: `domain/microstructure.py` 신설 vs `domain/orderbook.py` 확장. ADR-001(Hexagonal) 관점에서 domain 레이어 배치.
2. **seq gap 처리 책임**: `OrderBook` 내부 vs `Collector` 레이어 — ADR 별도 발행 여부.
3. **size_bucket 산출 레이어**: 백엔드 실시간 집계 vs DuckDB 쿼리 — 수집량 규모에 따른 트레이드오프.
4. **Tape 보관 정책**: 최근 N건만 메모리 유지 vs 전량 Parquet 재쿼리 — 대시보드 새로고침 UX 영향.
5. **시각화 전송 방식**: HTTP 폴링 유지 vs WebSocket 도입 — ADR-010 연장선에서 결정.

이 문서는 Researcher 해석 산출물이며, 위 열린 질문은 ArchitectAgent가 후속 ADR로 확정한다.
