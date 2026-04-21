---
date: 2026-04-21
severity: critical
component: collector
---

# Bug: ParquetSink dict mutation crash (asyncio.to_thread 오용)

## 개요

- **파일**: `src/mctrader/adapters/storage/parquet_sink.py`, `src/mctrader/app/collector_service.py`
- **증상**: collector가 약 2분 실행 후 크래시, 이후 재실행해도 즉시 종료
- **발생 시각**: 2026-04-21 11:00 KST
- **근본 원인**: `asyncio.to_thread`로 `ParquetSink.flush()`를 별도 스레드에서 호출해 `dict` 동시 변경 유발

---

## 에러 로그

```json
{"ts": "2026-04-21T02:57:14.646565+00:00", "level": "INFO", "logger": "mctrader.app.collector_service", "msg": "CollectorService started"}
{"ts": "2026-04-21T02:59:14.664664+00:00", "level": "INFO", "logger": "mctrader.app.collector_service", "msg": "CollectorService shutdown complete"}
{"ts": "2026-04-21T02:59:14.665377+00:00", "level": "ERROR", "logger": "mctrader.cli.collector_main", "msg": "collector terminated with error", "exc": "Traceback (most recent call last):\n  File \"/Users/mccho/workspace/mctrader/src/mctrader/app/collector_service.py\", line 169, in run_collector\n    await service.run()\n  File \"/Users/mccho/workspace/mctrader/src/mctrader/app/collector_service.py\", line 72, in run\n    stored += await self._handle_event(event)\n  File \"/Users/mccho/workspace/mctrader/src/mctrader/app/collector_service.py\", line 86, in _handle_event\n    self._sink.write_orderbook_diff(event)\n  File \"/Users/mccho/workspace/mctrader/src/mctrader/adapters/storage/parquet_sink.py\", line 93, in write_orderbook_diff\n    self.flush()\n  File \"/Users/mccho/workspace/mctrader/src/mctrader/adapters/storage/parquet_sink.py\", line 123, in flush\n    for key, rows in self._buf.items():\nRuntimeError: dictionary changed size during iteration"}
```

핵심 에러: `RuntimeError: dictionary changed size during iteration` — `ParquetSink._buf`를 두 경로에서 동시 접근.

---

## 원인 분석

`_periodic_flush`가 `asyncio.to_thread`로 `flush()`를 **별도 OS 스레드**에서 실행했다.

```python
# 버그 코드 (before)
async def _periodic_flush(self) -> None:
    while self._running:
        await asyncio.sleep(self._flush_interval_sec)
        if not self._running:
            break
        asyncio.create_task(asyncio.to_thread(self._sink.flush))  # ← 스레드에서 실행
```

동시에 메인 asyncio 이벤트 루프에서는 다음 경로로도 `flush()`가 호출됐다.

```
write_orderbook_diff() → _should_flush() → flush()
```

두 실행 경로가 동시에 `self._buf.items()`를 순회하는 사이, 한쪽이 `self._buf`에 새 키를 추가하면서 `RuntimeError`가 발생했다.

```mermaid
sequenceDiagram
    participant Loop as asyncio event loop
    participant Thread as OS thread (to_thread)
    participant Buf as ParquetSink._buf

    Loop->>Buf: write_orderbook_diff() → buf[key].append(row)
    Thread->>Buf: flush() → for key, rows in buf.items()
    Loop->>Buf: flush() → for key, rows in buf.items()
    Buf-->>Thread: RuntimeError: dict changed size during iteration
```

`_shutdown`도 동일 패턴으로 `asyncio.to_thread(self._sink.close)`를 호출해 불필요한 스레드 오프로드를 수행했다.

`ParquetSink`는 thread-safe하게 설계되지 않았고, asyncio 단일 이벤트 루프 전용으로 사용되므로 `asyncio.to_thread` 사용 자체가 잘못된 선택이었다.

---

## 수정 내용

`src/mctrader/app/collector_service.py`에서 `asyncio.to_thread` 호출을 제거하고 이벤트 루프에서 직접 동기 호출로 교체했다.

```python
# 수정 후 (after)
async def _periodic_flush(self) -> None:
    while self._running:
        await asyncio.sleep(self._flush_interval_sec)
        if not self._running:
            break
        self._sink.flush()  # 이벤트 루프에서 직접 호출

async def _shutdown(self) -> None:
    await self._cancel_flush_task()
    self._sink.close()  # asyncio.to_thread 제거
    logger.info("CollectorService shutdown complete")
```

`flush()`와 `close()`는 CPU-bound 작업이 아니므로 이벤트 루프를 블로킹하지 않으며, GIL 경합 없이 안전하게 실행된다.

---

## 검증

수정 후 step-by-step 디버그 실행으로 정상 기동을 확인했다.

```json
{"ts": "2026-04-21T03:30:53.009257+00:00", "level": "INFO", "logger": "root", "msg": "step4: logging setup ok"}
{"ts": "2026-04-21T03:30:53.297464+00:00", "level": "INFO", "logger": "mctrader.app.collector_service", "msg": "CollectorService started"}
```

PID 65055로 정상 가동 중 (2026-04-21 12:50 KST 기준 데이터 수집 확인).

---

## 재발 방지

1. **`ParquetSink` thread-safety 명시**: 클래스 docstring에 "not thread-safe, asyncio event loop only" 주석 추가.
2. **`asyncio.to_thread` 사용 제한**: I/O 또는 CPU-bound 블로킹 작업에만 한정 사용. 순수 동기 메모리 연산(`dict` 조작, 버퍼 순회)에는 사용 금지.
3. **통합 테스트 추가**: `_periodic_flush`와 `write_orderbook_diff`가 동시에 실행되는 시나리오를 커버하는 테스트 작성.
4. **코드 리뷰 체크리스트**: `asyncio.to_thread` 신규 도입 시 해당 객체의 thread-safety 여부를 리뷰 항목으로 추가.
