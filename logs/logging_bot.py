import logging
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler(
    "bot.log",
    maxBytes=5 * 1024 * 1024,  # 5 MB
    backupCount=5              # хранить 5 файлов
)

logging.basicConfig(level=logging.INFO, filename="bot.log",encoding="utf-8",
    format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)