---
date: 2026-04-21
severity: low
component: tests
---

# Bug: TestTsFmt 하드코딩 타임스탬프 오류 (2026-04-21 → 2025-04-21)

## 개요

- 파일: `tests/unit/test_dashboard_server.py`
- 증상: `TestTsFmt` 테스트 클래스 전체 실패
- 에러: `AssertionError: assert '2025-04-21 00:00:00 UTC' == '2026-04-21 00:00:00 UTC'`

## 원인 분석

테스트에 사용한 타임스탬프 `1745193600000 ms`의 실제 UTC 날짜가 주석과 달랐다:

```python
class TestTsFmt:
    # 2025-04-21 00:00:00 UTC = 1745193600000 ms  ← 주석은 2025
    _TS_MS = 1745193600000

    def test_utc_format(self) -> None:
        result = _ts_fmt(self._TS_MS, "UTC")
        assert result == "2026-04-21 00:00:00 UTC"  # ← 기대값이 2026 (잘못됨)
```

`1745193600000 ms = 1745193600 s` → Unix epoch 기준 **2025-04-21 00:00:00 UTC**.
테스트 작성 시점에 실수로 연도를 2026으로 입력했다.

## 수정 내용

```python
# before
assert result == "2026-04-21 00:00:00 UTC"
# after
assert result == "2025-04-21 00:00:00 UTC"
```

`test_utc_format`, `test_kst_offset`, `test_seconds_epoch_also_works` 3개 메서드 모두 수정.

## 재발 방지

- 타임스탬프 테스트 픽스처 작성 시 반드시 `datetime.utcfromtimestamp()` 로 실제 날짜를 검증 후 기대값 입력
