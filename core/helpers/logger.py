import logging
import os
from datetime import datetime
from pathlib import Path
from opencensus.ext.azure.log_exporter import AzureLogHandler

import unicodedata
import re

from core.config import config


def slugify(value, allow_unicode=False):
    """
    Taken from https://github.com/django/django/blob/master/django/utils/text.py
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize("NFKC", value)
    else:
        value = (
            unicodedata.normalize("NFKD", value)
            .encode("ascii", "ignore")
            .decode("ascii")
        )
    value = re.sub(r"[^\w\s-]", "-", value.lower())
    return re.sub(r"[-\s]+", "-", value).strip("-_")


def get_logger(exc: Exception | str = None) -> tuple[logging.Logger, str]:
    """Initializes logger and generates log name."""

    log_name = "_".join(
        [
            datetime.now().strftime("%m%d%Y-%H%M%S"),
            (slugify(str(exc)[:50]) or "untitled"),
        ]
    ).lower()

    if config.ENV == "local":
        return get_azure_logger("testing-logger!"), log_name
        return get_local_logger(log_name), log_name

    if config.ENV == "dev":
        return get_azure_logger(), log_name

        
    return "No logger", log_name
    

def get_azure_logger(module_name: str = "backend-server"):
    logger = logging.getLogger(module_name)
    logger.addHandler(AzureLogHandler())

    return logger

def get_local_logger(log_name):
    Path(os.getcwd() + "/logs").mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        filename=f"logs/{log_name}.log",
        format="%(levelname)s\t%(asctime)s: %(message)s",
        encoding="utf-8",
        level=logging.INFO,
        force=True,
    )

    return logging
