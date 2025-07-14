import logging
import pathlib

LOG_PATH = pathlib.Path("logs") / "auth_logs.log"
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)  

formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s - "
    "File: %(filename)s - Line: %(lineno)d - Function: %(funcName)s",
)

auth_file_handler = logging.FileHandler("logs/auth_logs.log")
auth_logger = logging.getLogger("auth_logger")

# File handler for logging to a file
auth_file_handler.setFormatter(formatter)

# Add the handler to the logger
auth_logger.addHandler(auth_file_handler)
