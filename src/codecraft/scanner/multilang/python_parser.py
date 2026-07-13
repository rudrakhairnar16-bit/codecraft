from __future__ import annotations

import ast

from codecraft.models.file import FileConcept
from codecraft.scanner.concept_extractor import ConceptExtractor
from codecraft.scanner.multilang.parser import BaseParser


class PythonParser(BaseParser):
    def parse(self, source_code: str, file_path: str) -> dict[str, FileConcept]:
        try:
            tree = ast.parse(source_code, filename=file_path)
        except SyntaxError:
            return {}
        extractor = ConceptExtractor()
        return extractor.extract(tree)
