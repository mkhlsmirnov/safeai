"""
logger.py
Настройка логирования для проекта SafeAI.
Все события пишутся в файл logs/safeai.log и дублируются в консоль.
"""

import logging
import sys
from config import LOG_FILE, LOG_LEVEL, LOG_FORMAT, LOG_DATE_FORMAT


def get_logger(name: str) -> logging.Logger:
    """
    Возвращает настроенный логгер с указанным именем.
    Если логгер уже настроен, повторная настройка не выполняется.

    :param name: Имя логгера (обычно __name__ модуля).
    :return: Экземпляр logging.Logger.
    """
    logger = logging.getLogger(name)

    # Если у логгера уже есть обработчики — не добавляем повторно
    if logger.handlers:
        return logger

    logger.setLevel(LOG_LEVEL)

    # Форматтер для сообщений
    formatter = logging.Formatter(fmt=LOG_FORMAT, datefmt=LOG_DATE_FORMAT)

    # Обработчик для файла
    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Обработчик для консоли
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Чтобы сообщения не дублировались через root logger
    logger.propagate = False

    return logger