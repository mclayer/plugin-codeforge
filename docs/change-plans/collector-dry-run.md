---
title: "Change Plan: mctrader-collector --dry-run"
slug: collector-dry-run
status: Accepted
author: ArchitectAgent
reviewers: [RefactorAgent, DeveloperPLAgent]
related_adrs: [ADR-001, ADR-006, ADR-012]
created: 2026-04-22
---

# Change Plan: `mctrader-collector --dry-run`

## 목적
`mctrader-collector` 실행 전 설정/연결 유효성을 네트워크 데이터 수신 없이 검증. 3단계(config 로드 + 심볼 해석 + WS 핸드셰이크)를 통과하면 exit 0, 실패 시 exit 1. 운영자가 배포 전 smoke check에 사용.

**수용 기준**
- `mctrader-collector --dry-run` 실행 시 stdout에 stage별 체크리스트 출력 후 exit 0 (성공) / exit 1 (실패)
- subscribe 프레임 미송신 — Bithumb 측 세션 기록 없음
- 기존 `mctrader-collector` (플래그 없음) 동작 불변
- argparse 에러는 exit 2 유지 (dry-run 실패 1과 구분)

## 현재 구조 분석 (RefactorAgent 입력)
- `collector_main.py`: argparse → `load_collector_config()` → `setup_logging()` → `asyncio.run(run_collector(config))`. dry-run 분기 필요
- `collector_service.py::from_config()`: gateway/ws_client/sink 생성을 한 번에 수행. dry-run은 sink 생성 경로를 타지 않아야 함 → `from_config()` 재사용 불가, 별도 경로 필요
- `ws_client.py::connect()`: TLS + `_subscribe()` 결합. dry-run은 subscribe 불가 → 신규 `probe_handshake()` 메서드 필요. 기존 `connect()`/`_subscribe()`/`close()` 불변
- `CollectorConfig.bithumb` 단일 필드 — 멀티 거래소 스키마 없음
- 리팩토링 선행 작업 없음

## 도입할 설계

**결정 1 — 멀티 거래소**: **옵션 A 채택** (bithumb 1개 고정 루프). 근거: ADR-006은 미래 약속, ADR-001(Hex)을 깨지 않는 범위에서 CLI 계약(`--exchange`)만 선제 반영 → config 스키마 확장 시 loop가 자동 확장. `--exchange bithumb` 외 값은 validation 에러.

**결정 2 — 시그니처**: 예외 기반. `DryRunFailed(stage, reason)` 도메인 예외 → caller가 stdout/stderr 출력 + exit code 매핑. stage 문자열은 매직 스트링이 아닌 모듈 상수 집합으로 고정.

**결정 3 — logging**: dry-run 경로는 `setup_logging()` 호출 스킵. 근거: stdout 체크리스트 가독성 우선, logger 부작용(파일 핸들 생성 등) 불필요.

**결정 4 — ADR**: 해당 없음. 근거: CLI 계약 추가일 뿐 Hex 경계·저장 방식·포트 계약 변경 없음.

**신규 타입**
- `DryRunFailed(Exception)` — `stage: str`, `reason: str` 속성
- `DryRunStage` — 모듈 상수 4개 (`CONFIG_LOAD`, `CONFIG_VALIDATE`, `SYMBOL_RESOLVE`, `WEBSOCKET_HANDSHAKE`)

## API 계약

**CLI 플래그** (`collector_main.py`에 추가)
- `--dry-run` action=store_true, default=False, help="Validate config + probe WS handshake without collecting"
- `--exchange` type=str, default=None, choices=["bithumb"], help="Limit dry-run to a specific exchange (default: all)"
- `--exchange` 단독 사용 시 `parser.error("--exchange requires --dry-run")` → exit 2

**신규 모듈 `src/mctrader/app/dry_run.py`**
- 상수: `DRY_RUN_STAGE_CONFIG_LOAD`, `DRY_RUN_STAGE_CONFIG_VALIDATE`, `DRY_RUN_STAGE_SYMBOL_RESOLVE`, `DRY_RUN_STAGE_WEBSOCKET_HANDSHAKE` (모두 str)
- 예외: `DryRunFailed(Exception)` with stage, reason
- 함수: `async def run_dry_run(config: CollectorConfig, config_path: str, exchange_filter: str | None = None) -> None`

**신규 WS 메서드**: `BithumbWsClient.probe_handshake(timeout_sec: float = 5.0) -> float`
- TLS 핸드셰이크만 수행, `_subscribe()` 미호출, 즉시 close
- 반환값: 핸드셰이크 경과 시간(ms)
- `asyncio.wait_for(websockets.connect(...), timeout_sec)` 사용
- TimeoutError/OSError/SSLError 등은 호출자에서 `DryRunFailed(WEBSOCKET_HANDSHAKE, str(exc))`로 래핑

**stdout 포맷 리터럴**
```
[dry-run] config loaded: {config_path}
[dry-run] exchange={exchange_name} symbols=[{csv}] ({n} symbols)
[dry-run] websocket handshake: OK ({ws_url}, {elapsed_ms}ms)
[dry-run] OK
```
- `{csv}` = `",".join(symbol_names)` (공백 없음)
- `{elapsed_ms}` = `int(round(elapsed))`
- 거래소 2개 이상이면 stage 2~3을 거래소별로 반복 (all-report, fail-fast 아님)

**stderr 포맷**: `[dry-run:failed] {stage}: {reason}`

**exit code**: 0=성공, 1=dry-run 실패, 2=argparse 에러

## 변경 계획 (파일 단위)

**1. `src/mctrader/app/dry_run.py` (신규)** — 위 API 계약 그대로 구현

**2. `src/mctrader/app/collector_service.py`**
- 수정: `_filter_symbols` → `filter_symbols` (public 승격). 호출부 `from_config` 1곳 동반 수정

**3. `src/mctrader/adapters/exchanges/bithumb/ws_client.py`**
- 추가: `probe_handshake(timeout_sec)` 메서드 (기존 `connect()` 불변)

**4. `src/mctrader/cli/collector_main.py`**
- 수정: argparse 확장, `--dry-run` 분기. config 로드 실패 시 `[dry-run:failed] config_load: ...` stderr + exit 1. `setup_logging()` 스킵. `DryRunFailed` 캐치 → stderr + exit 1. 성공 시 `[dry-run] OK` + exit 0

## 리팩토링 선행 작업
없음 (RefactorAgent 판단). `_filter_symbols` → `filter_symbols` 이름 변경은 구현 단계 동반 변경.

## 테스트 계획

**tests/unit/app/test_dry_run.py** (신규)
- test_run_dry_run_success_happy_path
- test_run_dry_run_symbol_resolve_empty
- test_run_dry_run_handshake_timeout
- test_run_dry_run_invalid_exchange_filter

**tests/unit/adapters/exchanges/bithumb/test_ws_client_probe.py** (신규)
- test_probe_handshake_does_not_subscribe
- test_probe_handshake_returns_elapsed_ms
- test_probe_handshake_timeout_raises

**tests/integration/cli/test_collector_dry_run.py** (신규)
- test_cli_dry_run_exit_code_on_bad_config
- test_cli_dry_run_mutual_arg_rule
- test_cli_no_dry_run_flag_unchanged

## DeveloperPL 후속 점검 (feasibility)
- 구현 blocker 0건
- 불일치 1건: `CONFIG_VALIDATE` stage의 실제 진입 경로 불명확 (argparse choices가 잘못된 exchange를 이미 차단). BackendDev 착수 시 이 stage를 `run_dry_run` 내부 방어적 validation(예: config 파싱 후 `ws_url`이 빈 문자열인 경우 등)에 활용하거나, stage 어휘에서 제외할지 ArchitectAgent 재확인 권장

## ADR 대상 여부
해당 없음. CLI 표면 확장이며 Hex/저장/포트 계약 변경 없음. ADR-006(멀티 거래소 약속) · ADR-012(collectorctl 외부 계약)와 정합.

## 관련 파일
- src/mctrader/cli/collector_main.py
- src/mctrader/app/collector_service.py
- src/mctrader/app/dry_run.py (신규)
- src/mctrader/adapters/exchanges/bithumb/ws_client.py
- tests/unit/app/test_dry_run.py (신규)
- tests/unit/adapters/exchanges/bithumb/test_ws_client_probe.py (신규)
- tests/integration/cli/test_collector_dry_run.py (신규)
