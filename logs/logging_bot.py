import logging
import sys
from logging.handlers import RotatingFileHandler
"""
handler = RotatingFileHandler(
    "bot.log",
    maxBytes=5 * 1024 * 1024,  # 5 MB
    backupCount=5              # хранить 5 файлов
)
"""
logging.basicConfig(level=logging.INFO, encoding="utf-8",
    format="%(asctime)s - %(levelname)s - %(message)s", handlers=[logging.StreamHandler(sys.stdout)])
logger = logging.getLogger(__name__)