from __future__ import annotations

from pathlib import Path

from codecraft.models.file import FileReport
from codecraft.scanner.ast_parser import ASTParseError, file_hash, file_stats, parse_file
from codecraft.scanner.complexity import ComplexityAnalyzer
from codecraft.scanner.concept_extractor import ConceptExtractor
from codecraft.scanner.debt_detector import DebtDetector
from codecraft.scanner.fingerprint import FileFingerprint
from codecraft.scanner.import_analyzer import ImportAnalyzer
from codecraft.scanner.multilang import LanguageDetector, MultiLanguageScanner


class UnifiedScanner:
    def __init__(self) -> None:
        self.concept_extractor = ConceptExtractor()
        self.debt_detector: DebtDetector | None = None
        self.complexity_analyzer = ComplexityAnalyzer()
        self.import_analyzer = ImportAnalyzer()
        self.multi_scanner = MultiLanguageScanner()

    def scan_file(self, path: Path) -> FileReport | None:
        if not path.exists():
            return None

        lang = LanguageDetector.detect(str(path))
        if lang.name == "UNKNOWN":
            return None

        if lang.name == "PYTHON":
            return self._scan_python(path)

        return self._scan_multilang(path)

    def _scan_python(self, path: Path) -> FileReport | None:
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

    def _scan_multilang(self, path: Path) -> FileReport | None:
        try:
            concepts = self.multi_scanner.parse_file(str(path))
            concept_names = sorted(concepts.keys())
            _, lines = file_stats(path)

            return FileReport(
                path=path,
                concepts=concept_names,
                debt_items=[],
                complexity=0.0,
                lines=lines,
                imports=[],
            )
        except Exception:
            return FileReport(
                path=path,
                concepts=[],
                debt_items=[],
                complexity=0.0,
                lines=0,
                imports=[],
                errors=["Failed to parse"],
            )

    def fingerprint_file(self, path: Path) -> FileFingerprint | None:
        lang = LanguageDetector.detect(str(path))
        if lang.name == "UNKNOWN":
            return None
        if lang.name != "PYTHON":
            return self._fingerprint_multilang(path)

        report = self.scan_file(path)
        if report is None:
            return None

        h = file_hash(path)
        size, lines = file_stats(path)

        tree = parse_file(path)
        import ast

        functions = [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
        classes = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
        avg_len = 0.0
        if functions:
            total = 0
            for fn in functions:
                end_lineno: int = getattr(fn, "end_lineno", 0)
                lineno: int = getattr(fn, "lineno", 0)
                total += end_lineno - lineno
            avg_len = total / len(functions)

        has_main = any(
            isinstance(n, ast.If)
            and isinstance(n.test, ast.Compare)
            and any(
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

    def _fingerprint_multilang(self, path: Path) -> FileFingerprint | None:
        h = file_hash(path)
        size, lines = file_stats(path)
        concepts = self.multi_scanner.parse_file(str(path))

        return FileFingerprint(
            path=path,
            hash=h,
            size=size,
            lines=lines,
            concepts={name: 1 for name in concepts},
            debt_patterns=[],
            complexity=0.0,
            imports=[],
            import_count=0,
            has_main_guard=False,
            has_docstring=False,
            function_count=0,
            class_count=0,
            avg_function_length=0.0,
        )

    def scan_directory(
        self, directory: Path, pattern: str = "**/*", ignore_hidden: bool = True
    ) -> list[FileReport]:
        reports: list[FileReport] = []
        supported = set(LanguageDetector.supported_extensions())
        for path in sorted(directory.rglob("*")):
            if ignore_hidden and any(part.startswith(".") for part in path.parts):
                continue
            if path.suffix.lower() not in supported:
                continue
            if not path.is_file():
                continue
            report = self.scan_file(path)
            if report:
                reports.append(report)
        return reports
