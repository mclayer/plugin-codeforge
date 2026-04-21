# 알려진 문제 및 해결책

## 1. Dashboard 서버가 백그라운드 실행 후 즉시 종료

**증상**: `.venv/bin/python -m mctrader.cli.dashboard_main ... &` 실행 후 서버가 뜨지 않음

**원인**: 터미널 세션에서 `&` 백그라운드 실행 시 SIGHUP 수신으로 종료

**해결**: `nohup` 사용 또는 직접 uvicorn 호출
```bash
nohup .venv/bin/python -m mctrader.cli.dashboard_main --result-dir ./results > /tmp/dashboard.log 2>&1 &
```

---

## 2. 포트 충돌로 서버 기동 실패

**증상**: `OSError: [Errno 48] Address already in use`

**원인**: 이전 서버 프로세스가 살아있거나 다른 프로세스가 8080 점유

**해결**:
```bash
lsof -i :8080          # 점유 프로세스 확인
kill <PID>             # 해당 프로세스 종료
```

---

## 3. 백테스트 실행 시 Permission denied: '/var/data'

**증상**: 백테스트 실행 시 `[Errno 13] Permission denied: '/var/data'`

**원인**: `config/base.yaml`의 `data.root_path`가 `/var/data/mctrader`로 설정된 경우

**해결**: `config/base.yaml`에서 `data.root_path: ./data`로 변경 (이미 수정됨)

---

## 4. Bithumb WebSocket 연결 실패 (구 API)

**증상**: `socket.gaierror: [Errno 8] nodename nor servname provided`

**원인**: 구 엔드포인트 `global-api.bithumb.pro` 서비스 종료 (NXDOMAIN)

**해결**: 신규 엔드포인트 `wss://ws-api.bithumb.com/websocket/v1` 사용 (이미 수정됨)

---

## 5. 백테스트 완료 후 `/run/results`로 잘못 redirect

**증상**: 백테스트 완료 시 `/run/results` 404

**원인**: `ResultRecorder`가 결과를 `./results/` 루트에 직접 저장해 run_id가 `"results"`가 됨

**해결**: `backtest_runner.py`에서 `./results/{timestamp_uuid}/` 서브디렉토리 생성 (이미 수정됨)
