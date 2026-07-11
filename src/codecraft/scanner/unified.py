from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from codecraft.models.file import FileReport
from codecraft.scanner.ast_parser import ASTParseError, file_hash, file_stats, parse_file
from codecraft.scanner.complexity import ComplexityAnalyzer
from codecraft.scanner.concept_extractor import ConceptExtractor
from codecraft.scanner.debt_detector import DebtDetector
from codecraft.scanner.fingerprint import FileFingerprint
from codecraft.scanner.import_analyzer import ImportAnalyzer


class UnifiedScanner:
    def __init__(self):
        self.concept_extractor = ConceptExtractor()
        self.debt_detector: Optional[DebtDetector] = None
        self.complexity_analyzer = ComplexityAnalyzer()
        self.import_analyzer = ImportAnalyzer()

    def scan_file(self, path: Path) -> Optional[FileReport]:
        if not path.exists():
            return None
        if path.suffix != ".py":
            return None

        try:
            tree = parse_file(path)
            source = path.read_text(encoding="utf-8", errors="replace")

            concepts = self.concept_extractor.extract(tree)
            concept_names = sorted(concepts.keys())

            self.debt_detector = DebtDetector(source, path)
            debt_items = self.debt_detector.detect(tree)
            debt_patterns = [d.pattern_type for d in debt_items]

            complexity = self.complexity_analyzer.analyze(tree)

            import_info = self.import_analyzer.analyze(tree)

            _, lines = file_stats(path)

            return FileReport(
                path=path,
                concepts=concept_names,
                debt_items=debt_patterns,
                complexity=complexity,
                lines=lines,
                imports=import_info["imports"],
            )
        except ASTParseError:
            return FileReport(
                path=path,
                concepts=[],
                debt_items=[],
                complexity=0.0,
                lines=0,
                imports=[],
                errors=["Failed to parse"],
            )

    def fingerprint_file(self, path: Path) -> Optional[FileFingerprint]:
        report = self.scan_file(path)
        if report is None:
            return None

        h = file_hash(path)
        size, lines = file_stats(path)

        source = path.read_text(encoding="utf-8", errors="replace")
        tree = parse_file(path)

        import ast

        functions = [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
        classes = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
        avg_len = 0.0
        if functions:
            total = 0
            for fn in functions:
                if hasattr(fn, "end_lineno") and hasattr(fn, "lineno"):
                    total += fn.end_lineno - fn.lineno
            avg_len = total / len(functions)

        has_main = any(
            isinstance(n, ast.If) and
            isinstance(n.test, ast.Compare) and
            any(
                isinstance(c, ast.Name) and c.id == "__name__"
                for c in ast.walk(n.test)
            )
            for n in ast.walk(tree)
        )

        has_doc = ast.get_docstring(tree) is not None

        return FileFingerprint(
            path=path,
            hash=h,
            size=size,
            lines=lines,
            concepts={name: 1 for name in report.concepts},
            debt_patterns=report.debt_items,
            complexity=report.complexity,
            imports=report.imports,
            import_count=len(report.imports),
            has_main_guard=has_main,
            has_docstring=has_doc,
            function_count=len(functions),
            class_count=len(classes),
            avg_function_length=avg_len,
        )

    def scan_directory(
        self, directory: Path, pattern: str = "**/*.py", ignore_hidden: bool = True
    ) -> List[FileReport]:
        reports: List[FileReport] = []
        for path in sorted(directory.glob(pattern)):
            if ignore_hidden and any(part.startswith(".") for part in path.parts):
                continue
            report = self.scan_file(path)
            if report:
                reports.append(report)
        return reports
