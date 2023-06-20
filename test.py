# pylint: skip-file

import logging
from opencensus.ext.azure.log_exporter import AzureLogHandler
import os
from dotenv import load_dotenv


# Check if environment variables are present if not we make use of the .env file to load them
if os.getenv("DU") is None:
    load_dotenv()

logger = logging.getLogger("backend-server-test")
logger.addHandler(AzureLogHandler())

# Alternatively manually pass in the connection_string
# logger.addHandler(AzureLogHandler(connection_string=<appinsights-connection-string>))

"""Generate random log data."""
for num in range(5):
    logger.info(f"test info {num}")
    logger.debug(f"test debug {num}")
    logger.warning(f"Log warning - {num}")
    logger.error(f"test error {num}")
    logger.exception(ValueError("test exc"))
