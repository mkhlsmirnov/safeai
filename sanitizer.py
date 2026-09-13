"""
sanitizer.py
Модуль анализа входящих промптов на попытки Prompt Injection.
"""

import re
from dataclasses import dataclass, field
from typing import List

from config import INJECTION_PATTERNS, MAX_INJECTION_MATCHES
from logger import get_logger

logger = get_logger(__name__)


@dataclass
class SanitizeResult:
    """Результат проверки промпта."""
    is_safe: bool
    matched_patterns: List[str] = field(default_factory=list)
    reason: str = ""


class PromptSanitizer:
    """Проверяет промпты на наличие паттернов инъекций."""

    def __init__(self, patterns: List[str] | None = None):
        self.patterns = patterns if patterns is not None else INJECTION_PATTERNS
        # Компилируем регулярки один раз при инициализации — это быстрее
        self._compiled = [re.compile(p, re.IGNORECASE) for p in self.patterns]

    def check(self, prompt: str) -> SanitizeResult:
        """
        Проверяет промпт на наличие инъекций.

        :param prompt: Текст запроса пользователя.
        :return: SanitizeResult с флагом безопасности и списком совпадений.
        """
        if not prompt or not prompt.strip():
            return SanitizeResult(is_safe=True, reason="Пустой промпт")

        matched: List[str] = []
        for pattern, compiled in zip(self.patterns, self._compiled):
            if compiled.search(prompt):
                matched.append(pattern)

        if len(matched) >= MAX_INJECTION_MATCHES:
            logger.warning(
                "Обнаружена попытка Prompt Injection. Совпадений: %d | Паттерны: %s",
                len(matched), matched
            )
            return SanitizeResult(
                is_safe=False,
                matched_patterns=matched,
                reason=f"Обнаружено {len(matched)} паттернов инъекции"
            )

        logger.info("Промпт прошёл проверку на инъекции.")
        return SanitizeResult(is_safe=True, reason="OK")