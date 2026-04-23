# tests/perf/ — 성능 회귀 테스트 (테스트 레인 Step 2 perf 모드)

스캘핑 도메인 핵심 지연 SLO의 회귀를 자동 탐지한다. pytest-benchmark 기반.

## 실행

기능 테스트와 분리 실행:

```bash
.venv/bin/pytest tests/perf/ -v \
  --benchmark-only \
  --benchmark-autosave \
  --benchmark-compare=tests/perf/baselines \
  --benchmark-compare-fail=mean:10%
```

임계 초과 시 exit code 비-0 → TestAgent가 FAIL로 분류하고 PMAgent 경유 Architect 회귀.

## baseline 관리

- `tests/perf/baselines/` 하위에 커밋된 JSON이 기준선 역할
- baseline 갱신은 **Change Plan에 명시된 경우에만** QADev가 수행
- 의도적 구현 변경으로 지연 특성이 바뀌어야 하는 경우 Architect가 계획서에 "baseline 갱신" 항목 명시, 수치 근거 서술

## 작성 대상 (계획서 명시 시)

- WebSocket tick → Parquet flush 지연
- ORDERBOOK diff → snapshot 재구성 시간
- DuckDB 쿼리 응답 시간
- Strategy 신호 → 주문 전송 지연

## 원칙

- 환경 의존적 편차를 줄이기 위해 `--benchmark-rounds` 충분히 확보
- I/O·네트워크 경계는 mock 또는 loopback으로 고정해 계산·구조 회귀만 포착
