"""
detector.py
Модуль анализа текста на наличие PII (персональных данных) и токсичного контента.
"""

import re
from dataclasses import dataclass, field
from typing import Dict, List

from config import PII_PATTERNS, TOXIC_WORDS, MAX_PII_MATCHES, MAX_TOXIC_MATCHES
from logger import get_logger

logger = get_logger(__name__)


@dataclass
class DetectionResult:
    """Результат анализа текста."""
    is_safe: bool
    pii_found: Dict[str, List[str]] = field(default_factory=dict)
    toxic_found: List[str] = field(default_factory=list)
    reason: str = ""


class PIIDetector:
    """Ищет персональные данные в тексте с помощью регулярных выражений."""

    def __init__(self, patterns: Dict[str, str] | None = None):
        self.patterns = patterns if patterns is not None else PII_PATTERNS
        self._compiled = {
            name: re.compile(pattern, re.IGNORECASE)
            for name, pattern in self.patterns.items()
        }

    def detect(self, text: str) -> Dict[str, List[str]]:
        """
        Возвращает словарь: тип PII -> список найденных совпадений.
        """
        found: Dict[str, List[str]] = {}
        for name, compiled in self._compiled.items():
            matches = compiled.findall(text)
            if matches:
                # findall может возвращать кортежи (если есть группы) — нормализуем
                normalized = [m if isinstance(m, str) else m[-1] for m in matches]
                found[name] = normalized
        return found


class ToxicityDetector:
    """Простой детектор токсичности на основе списка слов."""

    def __init__(self, words: List[str] | None = None):
        self.words = words if words is not None else TOXIC_WORDS
        self._compiled = [re.compile(re.escape(w), re.IGNORECASE) for w in self.words]

    def detect(self, text: str) -> List[str]:
        """Возвращает список найденных токсичных слов."""
        return [w for w, c in zip(self.words, self._compiled) if c.search(text)]


class ContentAnalyzer:
    """Объединяет PII- и токсичность-детекторы в один анализ."""

    def __init__(self):
        self.pii_detector = PIIDetector()
        self.toxicity_detector = ToxicityDetector()

    def analyze(self, text: str) -> DetectionResult:
        """
        Полный анализ текста на PII и токсичность.

        :param text: Текст для анализа (обычно — ответ модели).
        :return: DetectionResult с флагом безопасности и деталями.
        """
        if not text or not text.strip():
            return DetectionResult(is_safe=True, reason="Пустой текст")

        pii_found = self.pii_detector.detect(text)
        toxic_found = self.toxicity_detector.detect(text)

        pii_count = sum(len(v) for v in pii_found.values())
        toxic_count = len(toxic_found)

        is_safe = (
            pii_count < MAX_PII_MATCHES and toxic_count < MAX_TOXIC_MATCHES
        )

        if not is_safe:
            if pii_count >= MAX_PII_MATCHES:
                logger.warning("Обнаружены PII: %s", {k: len(v) for k, v in pii_found.items()})
            if toxic_count >= MAX_TOXIC_MATCHES:
                logger.warning("Обнаружена токсичность: %s", toxic_found)

            reasons = []
            if pii_count >= MAX_PII_MATCHES:
                reasons.append(f"PII: {pii_count}")
            if toxic_count >= MAX_TOXIC_MATCHES:
                reasons.append(f"Токсичность: {toxic_count}")
            reason = " | ".join(reasons)
        else:
            logger.info("Текст прошёл проверку на PII и токсичность.")
            reason = "OK"

        return DetectionResult(
            is_safe=is_safe,
            pii_found=pii_found,
            toxic_found=toxic_found,
            reason=reason,
        )