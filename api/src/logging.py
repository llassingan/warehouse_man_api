import logging
import os
from datetime import datetime


os.makedirs("logs", exist_ok=True)

log_filename = datetime.now().strftime("%Y-%m-%d") + "_logs_warehouse.log"
log_path = os.path.join("logs", log_filename)

logger = logging.getLogger("uvicorn.access")
logger.disabled = True

logger.handlers.clear()

file_handler = logging.FileHandler(log_path)
file_handler.setLevel(logging.INFO)

formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)
