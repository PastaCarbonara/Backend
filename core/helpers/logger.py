import logging
from datetime import datetime


def get_logger(exc: Exception | str = None):
    """Initializes logger and generates log name."""

    log_name = "_".join(
        [
            datetime.now().strftime("%m%d%Y-%H%M%S"),
            (str(exc) or "untitled"),
        ]
    ).lower().replace(" ", "_")

    logging.basicConfig(
        filename=f"logs/{log_name}.log",
        format="%(levelname)s\t%(asctime)s: %(message)s",
        encoding="utf-8",
        level=logging.INFO,
        force=True,
    )

    return log_name
