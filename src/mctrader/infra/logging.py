from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone

from mctrader.infra.config import LoggingConfig


class _JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        ts = datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat()
        payload = {
            "ts": ts,
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


def setup_logging(config: LoggingConfig) -> None:
    level = logging.getLevelName(config.level.upper())

    if config.format == "json":
        formatter: logging.Formatter = _JsonFormatter()
    else:
        formatter = logging.Formatter(
            fmt="%(asctime)s %(levelname)s %(name)s %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S%z",
        )

    if config.output == "file":
        handler: logging.Handler = logging.FileHandler(config.file_path)
    else:
        handler = logging.StreamHandler(sys.stdout)

    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(level)
    # replace handlers so repeated calls don't stack
    root.handlers.clear()
    root.addHandler(handler)
