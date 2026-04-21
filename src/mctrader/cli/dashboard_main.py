from __future__ import annotations

import argparse
import logging
import signal

import uvicorn

from mctrader.dashboard.server import create_app


def main() -> None:
    parser = argparse.ArgumentParser(description="mctrader 대시보드 서버")
    parser.add_argument(
        "--result-dir",
        default="./results",
        help="백테스트 결과 디렉토리 (default: ./results)",
    )
    parser.add_argument("--host", default="127.0.0.1", help="바인드 호스트 (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8080, help="포트 (default: 8080)")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

    # 백그라운드 실행 시 터미널 세션 종료/부모 프로세스 종료로 인한 SIGHUP 무시
    if hasattr(signal, "SIGHUP"):
        signal.signal(signal.SIGHUP, signal.SIG_IGN)

    app = create_app(result_dir=args.result_dir)

    print(f"mctrader dashboard  →  http://{args.host}:{args.port}")
    try:
        uvicorn.run(app, host=args.host, port=args.port)
    except OSError as exc:
        if exc.errno == 48 or exc.errno == 98:  # macOS: 48, Linux: 98 (Address already in use)
            logging.error(
                "포트 %d 가 이미 사용 중입니다. --port 옵션으로 다른 포트를 지정하세요.",
                args.port,
            )
        else:
            logging.error("서버 시작 실패: %s", exc)
        raise SystemExit(1) from exc
