from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum


class Tier(IntEnum):
    SEED = 1
    ROOT = 2
    BRANCH = 3
    CANOPY = 4


@dataclass(frozen=True)
class Concept:
    name: str
    tier: Tier
    category: str
    description: str = ""

    def __lt__(self, other: Concept) -> bool:
        return (self.tier, self.name) < (other.tier, other.name)


class ConceptTaxonomy:
    _concepts: dict[str, Concept] = {}

    @classmethod
    def register(cls, name: str, tier: Tier, category: str, description: str = "") -> Concept:
        c = Concept(name, tier, category, description)
        cls._concepts[name] = c
        return c

    @classmethod
    def get(cls, name: str) -> Concept:
        if name not in cls._concepts:
            raise KeyError(f"Unknown concept: {name}")
        return cls._concepts[name]

    @classmethod
    def all(cls) -> list[Concept]:
        return sorted(cls._concepts.values())

    @classmethod
    def by_tier(cls, tier: Tier) -> list[Concept]:
        return [c for c in cls.all() if c.tier == tier]


ALL = ConceptTaxonomy.register

ALL("variable_assignment", Tier.SEED, "basics", "Assigning values to variables")
ALL("basic_types", Tier.SEED, "basics", "int, float, str, bool, None")
ALL("if_else", Tier.SEED, "control_flow", "Conditional branching with if/elif/else")
ALL("for_loop", Tier.SEED, "control_flow", "Iterating over sequences with for")
ALL("while_loop", Tier.SEED, "control_flow", "Looping with while condition")
ALL("print_function", Tier.SEED, "io", "Output with print()")
ALL("input_function", Tier.SEED, "io", "Reading user input with input()")
ALL("list_ops", Tier.SEED, "data_structures", "List methods: append, extend, insert, remove")
ALL("dict_ops", Tier.SEED, "data_structures", "Dict access, update, get, setdefault")
ALL("string_methods", Tier.SEED, "data_structures", "String split, join, upper, lower, strip")
ALL("file_io", Tier.SEED, "io", "Opening, reading, writing files")
ALL("try_except", Tier.SEED, "error_handling", "Basic try/except blocks")
ALL("function_def", Tier.SEED, "basics", "Defining functions with def")
ALL("return_value", Tier.SEED, "basics", "Returning values from functions")
ALL("boolean_ops", Tier.SEED, "basics", "and, or, not operators")
ALL("comparisons", Tier.SEED, "basics", "==, !=, <, >, <=, >=")
ALL("arithmetic", Tier.SEED, "basics", "+, -, *, /, //, %, **")
ALL("import_basic", Tier.SEED, "modules", "import and from ... import")

ALL("list_comprehension", Tier.ROOT, "control_flow", "[expr for x in iterable]")
ALL("dict_comprehension", Tier.ROOT, "control_flow", "{k: v for k, v in iterable}")
ALL("generator_expression", Tier.ROOT, "control_flow", "(expr for x in iterable)")
ALL("enumerate", Tier.ROOT, "iterables", "enumerate() for indexed iteration")
ALL("zip_function", Tier.ROOT, "iterables", "zip() for parallel iteration")
ALL("args_kwargs", Tier.ROOT, "functions", "*args and **kwargs parameters")
ALL("lambda", Tier.ROOT, "functions", "Anonymous lambda functions")
ALL("map_filter_reduce", Tier.ROOT, "functional", "map(), filter(), reduce()")
ALL("context_manager", Tier.ROOT, "resource_mgmt", "with statement for resource management")
ALL("f_strings", Tier.ROOT, "basics", "f-string formatting")
ALL("str_format", Tier.ROOT, "basics", ".format() string formatting")
ALL("tuple_unpacking", Tier.ROOT, "basics", "Multiple assignment and tuple unpacking")
ALL("slicing", Tier.ROOT, "data_structures", "Sequence slicing with [start:stop:step]")
ALL("set_ops", Tier.ROOT, "data_structures", "Set operations: union, intersect, difference")
ALL("defaultdict", Tier.ROOT, "data_structures", "collections.defaultdict")
ALL("counter", Tier.ROOT, "data_structures", "collections.Counter")
ALL("class_basic", Tier.ROOT, "oop", "Basic class definition and __init__")
ALL("property_decorator", Tier.ROOT, "oop", "@property decorator")
ALL("static_class_method", Tier.ROOT, "oop", "@staticmethod and @classmethod")
ALL("decorator_basic", Tier.ROOT, "functions", "Basic decorator pattern")
ALL("pathlib", Tier.ROOT, "io", "Pathlib for path manipulation")
ALL("exception_multiple", Tier.ROOT, "error_handling", "Multiple except clauses and else/finally")

ALL("decorator_args", Tier.BRANCH, "functions", "Decorators that accept arguments")
ALL("yield_generator", Tier.BRANCH, "control_flow", "Generator functions with yield")
ALL("yield_from", Tier.BRANCH, "control_flow", "yield from delegation")
ALL("contextlib", Tier.BRANCH, "resource_mgmt", "contextlib.contextmanager and utilities")
ALL("abstract_base_class", Tier.BRANCH, "oop", "ABC and abstractmethod")
ALL("dataclass", Tier.BRANCH, "oop", "@dataclass decorator")
ALL("named_tuple", Tier.BRANCH, "oop", "NamedTuple and typing.NamedTuple")
ALL("typed_dict", Tier.BRANCH, "oop", "TypedDict for structured dicts")
ALL("type_hints_basic", Tier.BRANCH, "types", "Basic type annotations")
ALL("match_case", Tier.BRANCH, "control_flow", "Structural pattern matching (3.10+)")
ALL("lru_cache", Tier.BRANCH, "functional", "functools.lru_cache for memoization")
ALL("itertools", Tier.BRANCH, "iterables", "itertools module: chain, cycle, groupby")
ALL("deque", Tier.BRANCH, "data_structures", "collections.deque for efficient appends")
ALL("heapq", Tier.BRANCH, "data_structures", "heapq for priority queues")
ALL("exception_chaining", Tier.BRANCH, "error_handling", "raise ... from ...")
ALL("custom_exception", Tier.BRANCH, "error_handling", "Defining custom exception classes")
ALL("slots", Tier.BRANCH, "oop", "__slots__ for memory optimization")
ALL("operator_overloading", Tier.BRANCH, "oop", "__add__, __eq__, __str__, etc.")
ALL("enter_exit", Tier.BRANCH, "resource_mgmt", "Custom context managers with __enter__/__exit__")
ALL("enum", Tier.BRANCH, "types", "Enum and IntEnum")
ALL("functools_partial", Tier.BRANCH, "functional", "functools.partial for partial application")

ALL("metaclass", Tier.CANOPY, "oop", "Custom metaclasses")
ALL("descriptor", Tier.CANOPY, "oop", "Descriptor protocol: __get__, __set__, __delete__")
ALL("async_await", Tier.CANOPY, "concurrency", "async/await coroutines")
ALL("asyncio_gather", Tier.CANOPY, "concurrency", "asyncio.gather and create_task")
ALL("async_context", Tier.CANOPY, "concurrency", "Async context managers with __aenter__/__aexit__")
ALL("async_generator", Tier.CANOPY, "concurrency", "Async generators with yield")
ALL("singledispatch", Tier.CANOPY, "functions", "functools.singledispatch for generic functions")
ALL("init_subclass", Tier.CANOPY, "oop", "__init_subclass__ for subclass registration")
ALL("mixin", Tier.CANOPY, "oop", "Mixin classes for composition")
ALL("weakref", Tier.CANOPY, "memory", "weakref for weak references")
ALL("context_var", Tier.CANOPY, "concurrency", "contextvars for task-local state")
ALL("callable", Tier.CANOPY, "oop", "__call__ making objects callable")
ALL("getattr_protocol", Tier.CANOPY, "oop", "__getattr__ and __getattribute__")
ALL("cython_ctypes", Tier.CANOPY, "extensions", "C extensions via ctypes or CFFI")
ALL("async_iterator", Tier.CANOPY, "concurrency", "Async iterators with __aiter__/__anext__")
