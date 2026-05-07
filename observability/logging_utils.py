import json
import logging
from datetime import datetime, timezone
import uuid

def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_obj = {
            "timestamp": now_iso(),
            "level": record.levelname,
            "logger_name": record.name,
            "message": record.getMessage(),
            "trace_id": getattr(record, "trace_id", None),
            "event_type": getattr(record, "event_type", "system"),
        }
        return json.dumps({k: v for k, v in log_obj.items() if v is not None})

def setup_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(JSONFormatter())
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger

def generate_trace_id() -> str:
    return str(uuid.uuid4())
