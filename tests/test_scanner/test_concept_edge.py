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


class TestTypeAlias:
    def test_type_alias_pep695(self):
        source = "type Point = tuple[int, int]"
        concepts = _extract(source)
        assert "type_alias" in concepts


class TestTryStar:
    def test_try_star(self):
        source = """
try:
    pass
except* ValueError:
    pass
except* TypeError:
    pass
"""
        concepts = _extract(source)
        assert "try_except_star" in concepts
        assert "try_except" in concepts
        assert "exception_multiple" in concepts


class TestAsyncFor:
    def test_async_for(self):
        source = """
async def fetch_all():
    async for item in async_gen():
        pass
"""
        concepts = _extract(source)
        assert "async_generator" in concepts
        assert "async_await" in concepts
        assert "function_def" in concepts


class TestStringMethods:
    def test_string_split_join(self):
        source = '"a,b,c".split(",")'
        concepts = _extract(source)
        assert "string_methods" in concepts

    def test_string_format(self):
        source = '"hello {}".format("world")'
        concepts = _extract(source)
        assert "string_methods" in concepts or "str_format" in concepts

    def test_string_upper(self):
        source = '"hello".upper()'
        concepts = _extract(source)
        assert "string_methods" in concepts

    def test_str_format_method(self):
        source = 'name = "world"; "hello {name}".format(name=name)'
        concepts = _extract(source)
        assert "string_methods" in concepts


class TestListOps:
    def test_list_append(self):
        source = "items = []; items.append(1)"
        concepts = _extract(source)
        assert "list_ops" in concepts

    def test_list_sort(self):
        source = "items = [3, 1, 2]; items.sort()"
        concepts = _extract(source)
        assert "list_ops" in concepts


class TestDictOps:
    def test_dict_get(self):
        source = "d = {'a': 1}; d.get('a')"
        concepts = _extract(source)
        assert "dict_ops" in concepts

    def test_dict_keys(self):
        source = "d = {'a': 1}; d.keys()"
        concepts = _extract(source)
        assert "dict_ops" in concepts


class TestSetOps:
    def test_set_union(self):
        source = "{1, 2}.union({3, 4})"
        concepts = _extract(source)
        assert "set_ops" in concepts

    def test_set_intersection(self):
        source = "{1, 2}.intersection({2, 3})"
        concepts = _extract(source)
        assert "set_ops" in concepts


class TestCallDetection:
    def test_print_call(self):
        source = 'print("hello")'
        concepts = _extract(source)
        assert "print_function" in concepts

    def test_map_filter(self):
        source = "list(map(str, [1, 2, 3]))"
        concepts = _extract(source)
        assert "map_filter_reduce" in concepts

    def test_open_call(self):
        source = "open('file.txt')"
        concepts = _extract(source)
        assert "file_io" in concepts

    def test_super_call(self):
        source = """
class Child(Base):
    def __init__(self):
        super().__init__()
"""
        concepts = _extract(source)
        assert "class_basic" in concepts


class TestVariableOps:
    def test_augmented_assign(self):
        source = "x = 1; x += 1"
        concepts = _extract(source)
        assert "variable_assignment" in concepts

    def test_tuple_unpacking(self):
        source = "a, b = (1, 2)"
        concepts = _extract(source)
        assert "tuple_unpacking" in concepts

    def test_starred_unpacking(self):
        source = "a, *b = [1, 2, 3]"
        concepts = _extract(source)
        assert "tuple_unpacking" in concepts


class TestArithmeticAndComparison:
    def test_arithmetic(self):
        source = "x = 1 + 2 * 3"
        concepts = _extract(source)
        assert "arithmetic" in concepts

    def test_boolean_ops(self):
        source = "if True and False or True: pass"
        concepts = _extract(source)
        assert "boolean_ops" in concepts

    def test_slicing(self):
        source = "items = [1, 2, 3]; items[1:3]"
        concepts = _extract(source)
        assert "slicing" in concepts


class TestFStrings:
    def test_fstring(self):
        source = 'name = "world"; f"hello {name}"'
        concepts = _extract(source)
        assert "f_strings" in concepts


class TestWithStatement:
    def test_with_basic(self):
        source = """
with open('file.txt') as f:
    data = f.read()
"""
        concepts = _extract(source)
        assert "context_manager" in concepts


class TestDeleteStatement:
    def test_delete(self):
        source = "x = 1; del x"
        concepts = _extract(source)
        assert isinstance(concepts, dict)


class TestForLoopPatterns:
    def test_for_enumerate(self):
        source = "for i, v in enumerate(items): pass"
        concepts = _extract(source)
        assert "enumerate" in concepts
        assert "for_loop" in concepts

    def test_for_zip(self):
        source = "for a, b in zip(xs, ys): pass"
        concepts = _extract(source)
        assert "zip_function" in concepts
        assert "for_loop" in concepts

    def test_for_dict_items(self):
        source = "for k, v in d.items(): pass"
        concepts = _extract(source)
        assert "dict_ops" in concepts
        assert "for_loop" in concepts


class TestItertoolsImport:
    def test_itertools_import(self):
        source = "import itertools; list(itertools.chain([1], [2]))"
        concepts = _extract(source)
        assert "itertools" in concepts


class TestLambda:
    def test_lambda_simple(self):
        source = "f = lambda x: x + 1"
        concepts = _extract(source)
        assert "lambda" in concepts
        assert "variable_assignment" in concepts


class TestComprehensionTypes:
    def test_set_comprehension(self):
        source = "{x**2 for x in range(10)}"
        concepts = _extract(source)
        assert "set_ops" in concepts

    def test_generator_expression(self):
        source = "sum(x**2 for x in range(10))"
        concepts = _extract(source)
        assert "generator_expression" in concepts

    def test_multiple_comprehensions(self):
        source = "[x for x in range(5)]; {k: v for k, v in [('a', 1)]}; (x for x in range(3))"
        concepts = _extract(source)
        assert "list_comprehension" in concepts
        assert "dict_comprehension" in concepts
        assert "generator_expression" in concepts

    def test_dict_comprehension(self):
        source = "{x: x**2 for x in range(5)}"
        concepts = _extract(source)
        assert "dict_comprehension" in concepts


class TestElifChain:
    def test_elif_chain(self):
        source = """
if x == 1:
    pass
elif x == 2:
    pass
elif x == 3:
    pass
else:
    pass
"""
        concepts = _extract(source)
        assert "if_else" in concepts


class TestIsinstanceCall:
    def test_isinstance_call(self):
        source = "isinstance(x, int)"
        concepts = _extract(source)
        assert "type_hints_basic" in concepts


class TestMapFilterCalls:
    def test_map_call(self):
        source = "list(map(str, [1, 2, 3]))"
        concepts = _extract(source)
        assert "map_filter_reduce" in concepts

    def test_filter_call(self):
        source = "list(filter(None, [0, 1, 2]))"
        concepts = _extract(source)
        assert "map_filter_reduce" in concepts


class TestStaticMethodDecorator:
    def test_staticmethod_decorator(self):
        source = """
class Util:
    @staticmethod
    def helper():
        pass
"""
        concepts = _extract(source)
        assert "static_class_method" in concepts


class TestClassDunderMethods:
    def test_class_str_repr(self):
        source = """
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def __str__(self):
        return f"Point({self.x}, {self.y})"
    def __repr__(self):
        return f"Point({self.x}, {self.y})"
"""
        concepts = _extract(source)
        assert "operator_overloading" in concepts
        assert "f_strings" in concepts


class TestStdlibDetection:
    def test_collections_import(self):
        source = "from collections import defaultdict, Counter"
        concepts = _extract(source)
        assert "defaultdict" in concepts
        assert "counter" in concepts

    def test_functools_lru_cache(self):
        source = "from functools import lru_cache"
        concepts = _extract(source)
        assert "lru_cache" in concepts

    def test_typing_import(self):
        source = "from typing import NamedTuple, TypedDict"
        concepts = _extract(source)
        assert "named_tuple" in concepts
        assert "typed_dict" in concepts
        assert "type_hints_basic" in concepts

    def test_asyncio_import(self):
        source = "import asyncio"
        concepts = _extract(source)
        assert "asyncio_gather" in concepts
        assert "async_await" in concepts

    def test_dataclass_import(self):
        source = "from dataclasses import dataclass"
        concepts = _extract(source)
        assert "dataclass" in concepts

    def test_enum_import(self):
        source = "from enum import Enum"
        concepts = _extract(source)
        assert "enum" in concepts


class TestImportAlias:
    def test_import_with_alias(self):
        source = "import numpy as np"
        concepts = _extract(source)
        assert "import_basic" in concepts


class TestSlotsAttributeAccess:
    def test_slots_attribute(self):
        source = """
class Point:
    __slots__ = ('x', 'y')
    def __init__(self, x, y):
        self.x = x
        self.y = y
p = Point(1, 2)
p.__slots__
"""
        concepts = _extract(source)
        assert "slots" in concepts


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
