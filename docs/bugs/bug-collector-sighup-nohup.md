---
date: 2026-04-21
severity: high
component: collector
---

# Bug: Collector nohup 즉시 종료 (SIGHUP — start_new_session으로 해결)

## 개요

- 발생 시각: 2026-04-21 (이전 세션)
- 증상: `nohup python -m mctrader.cli.collector_main &` 명령으로 collector 시작 시 즉시 종료, 로그 없음
- 영향: 데이터 수집 불가

## 원인 분석

Bash 툴(Claude Code CLI) 환경에서 셸 명령이 완료되면 해당 셸이 종료되며 모든 백그라운드 프로세스에 `SIGHUP`을 전송한다. `nohup`은 일반 터미널 세션에서는 SIGHUP을 무시하지만, Bash 툴 컨텍스트에서는 신뢰할 수 없었다.

시도한 방법과 결과:

| 방법 | 결과 |
|------|------|
| `nohup python ... &` | SIGHUP로 즉시 종료 |
| `python ... & disown` | 동일하게 종료 |
| `subprocess.Popen(stdout=open(...))` | 부모 프로세스가 file descriptor 닫으면서 자식 stdout 깨짐 |

## 해결 방법

`subprocess.Popen`에 `start_new_session=True` + raw OS file descriptor 전달:

```python
import subprocess, sys, os

fd = os.open('/path/to/log', os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o644)
proc = subprocess.Popen(
    [sys.executable, '-m', 'mctrader.cli.collector_main'],
    start_new_session=True,   # 새 세션 → SIGHUP 전파 차단
    stdout=fd,
    stderr=fd,
    env={**os.environ, 'PYTHONUNBUFFERED': '1'},
    cwd='/path/to/mctrader',
)
os.close(fd)  # 부모는 fd 닫아도 자식은 독립 보유
```

`start_new_session=True`는 `setsid()`를 호출해 자식 프로세스를 새 세션 리더로 만들어 부모 세션의 SIGHUP 전파 대상에서 제외된다.

## 재발 방지

- collector 시작 스크립트에 `start_new_session=True` 패턴 고정
- 향후 systemd 서비스로 전환하면 이 문제는 근본적으로 해결됨 (ADR-008)
