from __future__ import annotations

import argparse
import logging

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

    app = create_app(result_dir=args.result_dir)

    print(f"mctrader dashboard  →  http://{args.host}:{args.port}")
    uvicorn.run(app, host=args.host, port=args.port)
