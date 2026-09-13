"""
config.py
Центральный файл конфигурации проекта SafeAI.
Содержит паттерны для детекции угроз, настройки логирования и общие параметры.
"""

import os
from pathlib import Path

# --- Общие настройки ---
PROJECT_NAME = "SafeAI"
VERSION = "0.1.0"
LOG_DIR = Path("logs")
LOG_FILE = LOG_DIR / "safeai.log"

# --- Паттерны Prompt Injection ---
# Это фразы, которые часто используются для обхода системных инструкций LLM.
INJECTION_PATTERNS = [
    r"ignore (all )?previous instructions",
    r"ignore (the )?above",
    r"disregard (all )?(previous|prior) (instructions|prompts)",
    r"forget (everything|all) (you|that)",
    r"system\s*prompt",
    r"you are now",
    r"act as (a |an )?",
    r"###\s*instruction",
    r"<\s*\|?im_start\|?\s*>",
    r"выход из роли",
    r"забудь (все|предыдущие) инструкции",
    r"игнорируй (все )?предыдущие",
]

# --- Паттерны для персональных данных (PII) ---
PII_PATTERNS = {
    "email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
    "phone_ru": r"(\+7|8)[\s\-\(\)]?\d{3}[\s\-\(\)]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}",
    "credit_card": r"\b(?:\d[ -]*?){13,16}\b",
    "api_key": r"(?i)(api[_-]?key|token|secret)[\s:=]+['\"]?([A-Za-z0-9_\-]{16,})['\"]?",
    "ipv4": r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
}

# --- Список токсичных слов (упрощенный пример) ---
# В реальном проекте лучше использовать ML-модель, но для MVP хватит списка.
TOXIC_WORDS = [
    " idiot", " stupid", " hate you", " kill ", " die ",
    "идиот", "тупой", "ненавижу", "убей", "сдохни",
]

# --- Настройки логирования ---
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# --- Пороговые значения ---
# Если количество найденных угроз превышает порог, промпт блокируется.
MAX_INJECTION_MATCHES = 1
MAX_PII_MATCHES = 1
MAX_TOXIC_MATCHES = 1

# --- Режим работы ---
# True: только логировать угрозы, но не блокировать (для отладки)
# False: блокировать при обнаружении угроз
DRY_RUN = False

# --- Создаём папку для логов при импорте ---
LOG_DIR.mkdir(exist_ok=True)