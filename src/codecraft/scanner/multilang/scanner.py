from __future__ import annotations

import os

from codecraft.models.file import FileConcept
from codecraft.scanner.multilang.detector import Language, LanguageDetector
from codecraft.scanner.multilang.parser import BaseParser


class MultiLanguageScanner:
    def __init__(self) -> None:
        self._parsers: dict[Language, BaseParser] = {}
        self._lazy_init()

    def _lazy_init(self) -> None:
        try:
            from codecraft.scanner.multilang.python_parser import PythonParser
            self._parsers[Language.PYTHON] = PythonParser()
        except Exception:
            pass
        import importlib
        _MODULES = [
            ("javascript", "codecraft.scanner.multilang.ts_parser", "JavaScriptParser"),
            ("typescript", "codecraft.scanner.multilang.ts_parser", "TypeScriptParser"),
            ("go", "codecraft.scanner.multilang.go_parser", "GoParser"),
            ("rust", "codecraft.scanner.multilang.rst_parser", "RustParser"),
            ("java", "codecraft.scanner.multilang.java_parser", "JavaParser"),
        ]
        for lang_name, mod_path, cls_name in _MODULES:
            try:
                mod = importlib.import_module(mod_path)
                cls = getattr(mod, cls_name)
                lang_enum = getattr(Language, lang_name.upper())
                self._parsers[lang_enum] = cls()
            except Exception:
                pass

    def parse_file(self, file_path: str) -> dict[str, FileConcept]:
        lang = LanguageDetector.detect(file_path)
        parser = self._parsers.get(lang)
        if parser is None:
            return {}
        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                source = f.read()
        except Exception:
            return {}
        return parser.parse(source, file_path)

    def parse_source(self, source_code: str, language: Language) -> dict[str, FileConcept]:
        parser = self._parsers.get(language)
        if parser is None:
            return {}
        return parser.parse(source_code, f"<{language.value}>")

    @property
    def supported_languages(self) -> list[Language]:
        return list(self._parsers.keys())

    @property
    def supported_extensions(self) -> list[str]:
        exts: list[str] = []
        for lang in self._parsers:
            exts.extend(LanguageDetector.supported_extensions())
        return sorted(set(exts))
