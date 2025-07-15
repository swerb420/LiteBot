import logging

_logging_format = "%(asctime)s %(levelname)s:%(name)s:%(message)s"
logging.basicConfig(level=logging.INFO, format=_logging_format)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
