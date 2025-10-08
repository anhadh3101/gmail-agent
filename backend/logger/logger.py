import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logger(name: str = "flask.app") -> logging.Logger:
    """Configure and return a logger with separate handlers for all logs and errors."""

    # 1. Ensure logs directory exists
    os.makedirs("logs", exist_ok=True)

    # 2. Create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.propagate = False  # Avoid duplicate logs

    # 3. Shared formatter
    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s %(name)s in %(module)s:%(lineno)d: %(message)s"
    )

    # 4. Handler for ALL logs
    all_handler = RotatingFileHandler("logs/app.log", maxBytes=5_000_000, backupCount=5)
    all_handler.setLevel(logging.INFO)
    all_handler.setFormatter(formatter)

    # 5. Handler for ERROR logs
    error_handler = RotatingFileHandler("logs/error.log", maxBytes=5_000_000, backupCount=10)
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)

    # 6. Optional console output (useful for local dev)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)

    # 7. Add handlers only once
    if not logger.handlers:
        logger.addHandler(all_handler)
        logger.addHandler(error_handler)
        logger.addHandler(console_handler)

    return logger