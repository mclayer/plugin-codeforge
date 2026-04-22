"""대시보드 캐시 모듈.

cachetools.TTLCache + threading.RLock 기반 스레드 안전 래퍼와
@dashboard_cache 데코레이터를 제공한다.

파티션 경계 bypass 전략:
- get_bucket_hour가 None이면 항상 ttl_realtime_ms 사용
- get_bucket_hour가 주어지면 호출 인자에서 hour를 추출해:
    * 현재 진행 중인 hour → 캐시 bypass (쿼리마다 항상 최신 데이터)
    * 완료된 hour → ttl_historical_ms 사용 (불변 데이터이므로 길게 캐시)
    * 판단 불가 → ttl_realtime_ms 사용
"""

from __future__ import annotations

import functools
import threading
import time
from collections.abc import Callable
from typing import Any, TypeVar

from cachetools import TTLCache  # type: ignore[import-untyped]

F = TypeVar("F", bound=Callable[..., Any])

# ---------------------------------------------------------------------------
# 내부 캐시 저장소
# ---------------------------------------------------------------------------

# TTL을 키별로 달리하려면 단일 TTLCache로는 부족하다.
# 여기서는 "실시간 TTL" 캐시와 "히스토리컬 TTL" 캐시를 분리해 유지하되,
# 키 공간은 (module, qualname, *args, **items) 로 동일하게 구성한다.
# _REALTIME_CACHE: 짧은 TTL (초 단위)
# _HISTORICAL_CACHE: 긴 TTL (분 단위)
# 각 캐시는 최대 1024개 엔트리로 제한해 메모리 누수를 방지한다.
_MAX_SIZE = 1024

# 실시간용 캐시: TTL은 데코레이터가 각 엔트리 put 시 직접 만료 시각을 관리하지 않고
# cachetools의 TTL 기능에 위임한다. 하지만 엔트리마다 TTL이 다를 수 있으므로
# (실시간 vs 히스토리컬) 두 개의 캐시 인스턴스를 분리한다.
# 실제 TTL 값은 데코레이터 옵션으로 받으므로 캐시 인스턴스 TTL은
# 합리적인 최댓값으로 초기화한다 (데코레이터가 직접 만료 시각 확인).
#
# 단순화 전략: 실시간 캐시는 TTL=1초(최소), 히스토리컬은 TTL=1시간으로
# 캐시 인스턴스를 두어 덮어쓰기 전에 stale 엔트리가 자동 제거되도록 한다.
# 실제 유효 만료는 엔트리에 함께 저장된 expire_at으로 판별한다.
# 캐시 값 타입: (result, expire_at_ms) 튜플
_realtime_cache: TTLCache[Any, tuple[Any, int]] = TTLCache(maxsize=_MAX_SIZE, ttl=60)
_historical_cache: TTLCache[Any, tuple[Any, int]] = TTLCache(maxsize=_MAX_SIZE, ttl=3600)
_lock = threading.RLock()


def clear_dashboard_cache() -> None:
    """테스트 목적의 캐시 전체 리셋."""
    with _lock:
        _realtime_cache.clear()
        _historical_cache.clear()


# ---------------------------------------------------------------------------
# 내부 유틸
# ---------------------------------------------------------------------------

def _make_key(
    func: Callable[..., Any], args: tuple[Any, ...], kwargs: dict[str, Any]
) -> tuple[Any, ...]:
    """(module, qualname, *args, **sorted_kwargs_items) 형태의 캐시 키 생성."""
    sorted_kwargs = tuple(sorted(kwargs.items()))
    return (func.__module__, func.__qualname__) + args + sorted_kwargs


def _current_hour_utc() -> int:
    """현재 UTC hour를 정수(0~23)로 반환."""
    return time.gmtime().tm_hour


# ---------------------------------------------------------------------------
# 데코레이터
# ---------------------------------------------------------------------------

def dashboard_cache(
    ttl_realtime_ms: int,
    ttl_historical_ms: int | None = None,
    *,
    get_bucket_hour: Callable[..., int | None] | None = None,
) -> Callable[[F], F]:
    """대시보드 핸들러용 TTL 캐시 데코레이터.

    Parameters
    ----------
    ttl_realtime_ms:
        실시간 엔드포인트 TTL (밀리초). get_bucket_hour=None이면 항상 이 값 사용.
    ttl_historical_ms:
        완료된 hour 데이터에 대한 TTL (밀리초). None이면 실시간 TTL로 폴백.
    get_bucket_hour:
        호출 인자 (*args, **kwargs)를 받아 쿼리 대상 hour(0~23, UTC)를
        반환하는 함수. None이면 항상 ttl_realtime_ms 사용.
        현재 진행 중인 hour를 반환하면 캐시 bypass.
    """
    effective_historical_ms = ttl_historical_ms if ttl_historical_ms is not None else ttl_realtime_ms

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # 파티션 경계 판별
            use_historical = False
            bypass = False

            if get_bucket_hour is not None:
                try:
                    bucket_hour = get_bucket_hour(*args, **kwargs)
                except Exception:
                    bucket_hour = None

                if bucket_hour is not None:
                    current_hour = _current_hour_utc()
                    if bucket_hour == current_hour:
                        bypass = True
                    else:
                        use_historical = True

            if bypass:
                return func(*args, **kwargs)

            key = _make_key(func, args, kwargs)
            ttl_ms = effective_historical_ms if use_historical else ttl_realtime_ms
            now_ms = int(time.monotonic() * 1000)

            # 캐시 조회
            cache = _historical_cache if use_historical else _realtime_cache
            with _lock:
                entry = cache.get(key)
                if entry is not None:
                    value, expire_at_ms = entry
                    if now_ms < expire_at_ms:
                        return value
                    # 만료됨 — 삭제하고 재계산
                    try:
                        del cache[key]
                    except KeyError:
                        pass

            # 캐시 미스 — 실제 함수 호출
            result = func(*args, **kwargs)
            expire_at_ms = int(time.monotonic() * 1000) + ttl_ms

            with _lock:
                cache[key] = (result, expire_at_ms)

            return result

        return wrapper  # type: ignore[return-value]

    return decorator
