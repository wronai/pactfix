"""Pactfix - Multi-language code and config file analyzer and fixer."""

__version__ = "1.0.5"

from .analyzer import analyze_code, detect_language, SUPPORTED_LANGUAGES

__all__ = [
    "analyze_code",
    "detect_language",
    "SUPPORTED_LANGUAGES",
    "__version__",
]
