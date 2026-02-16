import json
import logging


class _JsonFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps(record.__dict__, default=str)


def setup_telemetry_logger(log_path: str = "telemetry.log") -> logging.Logger:
    logger = logging.getLogger("telemetry")
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(log_path, encoding="utf-8")
    handler.setFormatter(_JsonFormatter())
    logger.addHandler(handler)
    logger.propagate = False
    return logger
