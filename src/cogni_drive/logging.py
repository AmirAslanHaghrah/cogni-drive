import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

def _level_from_str(s: str) -> int:
    return getattr(logging, (s or "INFO").upper().strip(), logging.INFO)

def make_logger(
    name: str,
    min_level: str,
    log_to_console: bool,
    log_to_file: bool,
    log_file: str,
) -> logging.Logger:
    """
    Create a logger. In RELEASE you typically disable console logs and keep file logs.
    """
    logger = logging.getLogger(name)
    logger.setLevel(_level_from_str(min_level))
    logger.propagate = False

    if logger.handlers:
        return logger

    fmt = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    if log_to_console:
        ch = logging.StreamHandler()
        ch.setLevel(_level_from_str(min_level))
        ch.setFormatter(fmt)
        logger.addHandler(ch)

    if log_to_file:
        path = Path(log_file).expanduser().resolve()
        fh = RotatingFileHandler(path, maxBytes=512_000, backupCount=3)
        fh.setLevel(_level_from_str(min_level))
        fh.setFormatter(fmt)
        logger.addHandler(fh)

    return logger
