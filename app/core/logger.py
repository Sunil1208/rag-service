from loguru import logger
import sys

# Remove default handlers
logger.remove()

# Configure loguru for colorful, structured logging
logger.add(
    sys.stdout,
    colorize=True,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | <cyan>{module}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
)

def get_logger():
    return logger