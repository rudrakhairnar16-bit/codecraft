from pathlib import Path

from codecraft.scanner.ast_parser import parse_file
from codecraft.scanner.concept_extractor import ConceptExtractor


def test_beginner_concepts(beginner_file: Path):
    tree = parse_file(beginner_file)
    extractor = ConceptExtractor()
    concepts = extractor.extract(tree)

    expected = {
        "variable_assignment", "basic_types", "if_else", "for_loop",
        "while_loop", "print_function", "input_function", "try_except",
        "file_io", "arithmetic", "comparisons",
    }

    found = set(concepts.keys())
    missing = expected - found
    extra = found - expected - {"import_basic"}  # bare_except triggers a debt detection, not a concept
    assert not missing, f"Missing concepts: {missing}"
    assert not extra - {"import_basic"}, f"Unexpected concepts: {extra}"


def test_intermediate_concepts(intermediate_file: Path):
    tree = parse_file(intermediate_file)
    extractor = ConceptExtractor()
    concepts = extractor.extract(tree)

    expected = {
        "list_comprehension", "dict_comprehension", "enumerate",
        "zip_function", "context_manager", "try_except", "type_hints_basic",
        "pathlib", "defaultdict", "counter", "class_basic",
        "property_decorator", "f_strings", "function_def",
        "import_basic", "string_methods", "file_io",
    }

    found = set(concepts.keys())
    missing = expected - found
    assert not missing, f"Missing concepts: {missing}"


def test_advanced_concepts(advanced_file: Path):
    tree = parse_file(advanced_file)
    extractor = ConceptExtractor()
    concepts = extractor.extract(tree)

    expected = {
        "async_await", "dataclass", "abstract_base_class",
        "lru_cache", "match_case", "exception_chaining",
        "type_hints_basic", "function_def", "class_basic",
        "import_basic", "yield_generator", "decorator_basic",
    }

    found = set(concepts.keys())
    missing = expected - found
    assert not missing, f"Missing concepts: {missing}"


def test_no_concepts_in_empty_file():
    import ast
    tree = ast.parse("")
    extractor = ConceptExtractor()
    concepts = extractor.extract(tree)
    assert isinstance(concepts, dict)
    assert "import_basic" not in concepts
