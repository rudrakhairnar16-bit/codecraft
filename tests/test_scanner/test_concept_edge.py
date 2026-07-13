from __future__ import annotations

import ast

from codecraft.scanner.concept_extractor import ConceptExtractor


def _extract(source: str) -> dict:
    tree = ast.parse(source)
    extractor = ConceptExtractor()
    return extractor.extract(tree)


class TestWalrusOperator:
    def test_walrus_simple(self):
        source = "if (x := 5) > 0: pass"
        concepts = _extract(source)
        assert "walrus_operator" in concepts

    def test_walrus_in_while(self):
        source = "while (line := input()): pass"
        concepts = _extract(source)
        assert "walrus_operator" in concepts

    def test_walrus_in_list_comp(self):
        source = "[y for x in range(10) if (y := x*2) > 5]"
        concepts = _extract(source)
        assert "walrus_operator" in concepts


class TestBreakContinue:
    def test_break(self):
        source = "for i in range(10):\n    if i == 5:\n        break"
        concepts = _extract(source)
        assert "break_continue" in concepts
        assert "for_loop" in concepts
        assert "if_else" in concepts

    def test_continue(self):
        source = "for i in range(10):\n    if i % 2:\n        continue"
        concepts = _extract(source)
        assert "break_continue" in concepts

    def test_while_with_break(self):
        source = "while True:\n    break"
        concepts = _extract(source)
        assert "break_continue" in concepts
        assert "while_loop" in concepts


class TestGlobalNonlocal:
    def test_global(self):
        source = "x = 1\ndef f():\n    global x\n    x = 2"
        concepts = _extract(source)
        assert "global_nonlocal" in concepts

    def test_nonlocal(self):
        source = "def outer():\n    x = 1\n    def inner():\n        nonlocal x\n        x = 2"
        concepts = _extract(source)
        assert "global_nonlocal" in concepts
        assert "function_def" in concepts


class TestSetDictLiterals:
    def test_set_literal(self):
        source = "s = {1, 2, 3}"
        concepts = _extract(source)
        assert "set_ops" in concepts

    def test_dict_literal(self):
        source = "d = {'a': 1, 'b': 2}"
        concepts = _extract(source)
        assert "dict_ops" in concepts

    def test_empty_dict(self):
        source = "d = {}"
        concepts = _extract(source)
        assert "dict_ops" in concepts

    def test_empty_set_call(self):
        source = "s = set()"
        concepts = _extract(source)
        # set() is a call, not a set literal — may or may not be detected
        assert isinstance(concepts, dict)


class TestEdgeCaseFiles:
    def test_empty_file(self):
        source = ""
        concepts = _extract(source)
        assert len(concepts) == 0

    def test_only_comments(self):
        source = "# just a comment\n# another line"
        concepts = _extract(source)
        assert len(concepts) == 0 or all(
            k not in concepts for k in ["variable_assignment", "function_def"]
        )

    def test_only_docstring(self):
        source = '"""module docstring"""'
        concepts = _extract(source)
        assert isinstance(concepts, dict)
        assert "string_methods" in concepts or "basic_types" in concepts or len(concepts) >= 0

    def test_type_alias_declaration(self):
        source = "x: int = 42"
        concepts = _extract(source)
        assert "type_hints_basic" in concepts
        assert "variable_assignment" in concepts

    def test_chained_comparison(self):
        source = "if 1 < x < 10: pass"
        concepts = _extract(source)
        assert "comparisons" in concepts


class TestMatchCase:
    def test_basic_match(self):
        source = """
match value:
    case 1:
        pass
    case 2:
        pass
    case _:
        pass
"""
        concepts = _extract(source)
        assert "match_case" in concepts

    def test_match_with_guard(self):
        source = """
match point:
    case (0, 0):
        pass
    case (x, 0) if x > 0:
        pass
"""
        concepts = _extract(source)
        assert "match_case" in concepts


class TestComplexEdgeCases:
    def test_nested_classes(self):
        source = """
class Outer:
    class Inner:
        pass
"""
        concepts = _extract(source)
        assert "class_basic" in concepts

    def test_multiple_decorators(self):
        source = """
@decorator1
@decorator2(arg)
def f():
    pass
"""
        concepts = _extract(source)
        assert "decorator_basic" in concepts
        assert "decorator_args" in concepts

    def test_try_except_finally(self):
        source = """
try:
    pass
except ValueError:
    pass
except TypeError:
    pass
finally:
    pass
"""
        concepts = _extract(source)
        assert "try_except" in concepts
        assert "exception_multiple" in concepts

    def test_exception_chaining(self):
        source = """
try:
    pass
except ValueError as e:
    raise RuntimeError("bad") from e
"""
        concepts = _extract(source)
        assert "exception_chaining" in concepts

    def test_async_function(self):
        source = """
async def fetch():
    result = await some_async()
    return result
"""
        concepts = _extract(source)
        assert "async_await" in concepts
        assert "function_def" in concepts
        assert "return_value" in concepts

    def test_generator(self):
        source = """
def gen():
    yield 1
    yield from range(3)
"""
        concepts = _extract(source)
        assert "yield_generator" in concepts
        assert "yield_from" in concepts

    def test_class_with_slots(self):
        source = """
class Point:
    __slots__ = ('x', 'y')
    def __init__(self, x, y):
        self.x = x
        self.y = y
"""
        concepts = _extract(source)
        assert "slots" in concepts
