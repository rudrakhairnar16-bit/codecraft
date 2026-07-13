from __future__ import annotations

from enum import Enum


class Language(Enum):
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    TSX = "tsx"
    GO = "go"
    RUST = "rust"
    JAVA = "java"
    UNKNOWN = "unknown"


_EXTENSION_MAP: dict[str, Language] = {
    ".py": Language.PYTHON,
    ".pyw": Language.PYTHON,
    ".js": Language.JAVASCRIPT,
    ".jsx": Language.JAVASCRIPT,
    ".mjs": Language.JAVASCRIPT,
    ".cjs": Language.JAVASCRIPT,
    ".ts": Language.TYPESCRIPT,
    ".tsx": Language.TSX,
    ".go": Language.GO,
    ".rs": Language.RUST,
    ".java": Language.JAVA,
}


class LanguageDetector:
    @staticmethod
    def detect(file_path: str) -> Language:
        import os
        ext = os.path.splitext(file_path)[1].lower()
        return _EXTENSION_MAP.get(ext, Language.UNKNOWN)

    @staticmethod
    def supported_extensions() -> list[str]:
        return list(_EXTENSION_MAP.keys())
