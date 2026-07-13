import ast
import time
from pathlib import Path

import duckdb
import pytest

from codecraft.db.migrations import run_migrations
from codecraft.db.repository import Repository
from codecraft.models.file import FileRecord
from codecraft.scanner.ast_parser import parse_file, parse_source
from codecraft.scanner.concept_extractor import ConceptExtractor
from codecraft.scanner.debt_detector import DebtDetector
from codecraft.scanner.unified import UnifiedScanner

pytestmark = pytest.mark.benchmark


class TestScanBenchmarks:
    def test_scan_speed(self, tmp_path: Path) -> None:
        lines = []
        lines.append('"""Synthetic benchmark file."""')
        lines.append("import os")
        lines.append("import sys")
        lines.append("from pathlib import Path")
        lines.append("")
        for i in range(20):
            lines.append(f"")
            lines.append(f"def func_{i}(a: int, b: int) -> int:")
            lines.append(f"    \"\"\"Docstring for func_{i}.\"\"\"")
            lines.append(f"    result = a + b")
            lines.append(f"    for j in range(a):")
            lines.append(f"        result += j")
            lines.append(f"        if result > 100:")
            lines.append(f"            break")
            lines.append(f"    return result")
            lines.append(f"")
        test_file = tmp_path / "bench_target.py"
        test_file.write_text("\n".join(lines), encoding="utf-8")

        scanner = UnifiedScanner()
        start = time.perf_counter()
        report = scanner.scan_file(test_file)
        elapsed = time.perf_counter() - start

        print(f"\n  Scan speed: {elapsed:.4f}s")
        assert elapsed < 1.0, f"Scan took {elapsed:.4f}s (threshold: 1.0s)"
        assert report is not None
        assert report.lines >= 90


class TestConceptExtractionBenchmarks:
    def test_concept_extraction_speed(self, intermediate_file: Path) -> None:
        tree = parse_file(intermediate_file)

        extractor = ConceptExtractor()
        start = time.perf_counter()
        concepts = extractor.extract(tree)
        elapsed = time.perf_counter() - start

        print(f"\n  Concept extraction: {elapsed:.4f}s")
        assert elapsed < 0.5, f"Extraction took {elapsed:.4f}s (threshold: 0.5s)"
        assert len(concepts) > 0


class TestDebtDetectionBenchmarks:
    def test_debt_detection_speed(self, advanced_file: Path) -> None:
        source = advanced_file.read_text(encoding="utf-8")
        tree = parse_source(source, str(advanced_file))

        detector = DebtDetector(source, advanced_file)
        start = time.perf_counter()
        debts = detector.detect(tree)
        elapsed = time.perf_counter() - start

        print(f"\n  Debt detection: {elapsed:.4f}s")
        assert elapsed < 0.5, f"Detection took {elapsed:.4f}s (threshold: 0.5s)"
        assert isinstance(debts, list)


class TestDatabaseBenchmarks:
    def test_db_insert_speed(self, in_memory_db: duckdb.DuckDBPyConnection) -> None:
        run_migrations(in_memory_db)
        repo = Repository(in_memory_db)

        record = FileRecord(
            path=Path("/bench/test.py"),
            hash="abc123",
            size=512,
            lines=100,
        )

        start = time.perf_counter()
        for _ in range(50):
            repo.upsert_file(record)
        elapsed = time.perf_counter() - start
        per_op = elapsed / 50

        print(f"\n  DB insert (50 ops): {elapsed:.4f}s total, {per_op:.6f}s/op")
        assert per_op < 0.1, f"Insert took {per_op:.6f}s/op (threshold: 0.1s)"

    def test_db_query_speed(self, in_memory_db: duckdb.DuckDBPyConnection) -> None:
        run_migrations(in_memory_db)
        repo = Repository(in_memory_db)

        record = FileRecord(
            path=Path("/bench/test.py"),
            hash="abc123",
            size=512,
            lines=100,
        )
        repo.upsert_file(record)

        start = time.perf_counter()
        for _ in range(50):
            _ = repo.get_file(Path("/bench/test.py"))
        elapsed = time.perf_counter() - start
        per_op = elapsed / 50

        print(f"\n  DB query (50 ops): {elapsed:.4f}s total, {per_op:.6f}s/op")
        assert per_op < 0.1, f"Query took {per_op:.6f}s/op (threshold: 0.1s)"
