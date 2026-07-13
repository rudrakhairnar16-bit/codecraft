from typing import Any

from codecraft.domains.registry import Domain, DomainRegistry
from codecraft.engines.templates import DomainData, generate_from_template


def _make_recipe(concept: str) -> Any:
    def recipe(domain_name: str, target_concepts: list[str], difficulty: int) -> Any:
        dd = DomainData(
            domain_name="gaming",
            description="Game mechanics, player stats, level generation, and score tracking",
            nouns=["player", "enemy", "item", "score", "level", "achievement"],
            verbs=["spawn", "collide", "upgrade", "respawn", "unlock"],
            adjectives=["legendary", "rare", "boss", "timed", "cooperative"],
            sample_data=[
                {"player": "Alice", "score": 1500, "level": 5, "class": "warrior"},
                {"player": "Bob", "score": 2300, "level": 7, "class": "mage"},
            ],
            sample_filename="savegame.json",
            sample_lines=[
                '{"player": "Alice", "score": 1500, "level": 5}',
                '{"player": "Bob", "score": 2300, "level": 7}',
            ],
        )
        return generate_from_template(dd, concept, difficulty=difficulty)
    return recipe


domain = Domain(
    name="gaming",
    description="Game mechanics, player stats, level generation, and score tracking",
)

for con in [
    "class_basic", "list_comprehension", "dict_comprehension", "enumerate",
    "try_except", "defaultdict", "counter", "lambda", "dataclass",
    "arithmetic", "property_decorator", "f_strings", "function_def",
    "import_basic", "basic_types", "tuple_unpacking",
    "print_function", "input_function", "if_else", "for_loop", "while_loop",
    "variable_assignment", "return_value", "comparisons", "list_ops", "dict_ops",
    "string_methods",

    "abstract_base_class",
    "async_await",
    "async_context",
    "async_generator",
    "async_iterator",
    "asyncio_gather",
    "boolean_ops",
    "callable",
    "context_var",
    "contextlib",
    "custom_exception",
    "cython_ctypes",
    "decorator_args",
    "deque",
    "descriptor",
    "enter_exit",
    "enum",
    "exception_chaining",
    "exception_multiple",
    "functools_partial",
    "getattr_protocol",
    "heapq",
    "init_subclass",
    "itertools",
    "lru_cache",
    "map_filter_reduce",
    "metaclass",
    "mixin",
    "named_tuple",
    "operator_overloading",
    "recursion",
    "singledispatch",
    "slots",
    "static_class_method",
    "str_format",
    "typed_dict",
    "weakref",
    "yield_from",
]:
    domain.register_recipe(con, _make_recipe(con))

DomainRegistry.register(domain)
