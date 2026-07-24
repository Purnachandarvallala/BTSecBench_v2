import logging
from pathlib import Path


def get_logger(name, log_file):

    logger = logging.getLogger(name)

    logger.setLevel(logging.INFO)

    if logger.handlers:
        return logger

    Path(log_file).parent.mkdir(exist_ok=True)

    formatter = logging.Formatter(

        "%(asctime)s | %(levelname)s | %(message)s"

    )

    fh = logging.FileHandler(log_file)

    fh.setFormatter(formatter)

    logger.addHandler(fh)

    return logger