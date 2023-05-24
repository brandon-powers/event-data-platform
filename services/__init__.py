import logging
from logging import Logger


def get_edp_logger() -> Logger:
    logging.basicConfig(
        filename="edp.log",
        filemode="a",
        format="%(process)d|%(asctime)s|%(msecs)d|%(name)s|%(levelname)s|%(message)s",
        datefmt="%H:%M:%S",
        level=logging.DEBUG,
    )
    return logging.getLogger("edp")
