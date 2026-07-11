from codecraft.domains.registry import Domain, DomainRegistry
from codecraft.engines.templates import DomainData, generate_from_template


def _make_recipe(concept: str):
    def recipe(domain_name: str, target_concepts: list, difficulty: int):
        dd = DomainData(
            domain_name="finance",
            description="Financial data processing — stocks, transactions, ledgers, and reports",
            nouns=["stock", "transaction", "invoice", "ledger_entry", "trade", "portfolio"],
            verbs=["aggregate", "reconcile", "validate", "summarize", "normalize"],
            adjectives=["quarterly", "outstanding", "audited", "pending", "consolidated"],
            sample_data=[
                {"date": "2024-01-15", "symbol": "AAPL", "price": 185.50, "volume": 45000},
                {"date": "2024-01-15", "symbol": "GOOG", "price": 141.20, "volume": 32000},
                {"date": "2024-01-16", "symbol": "AAPL", "price": 187.30, "volume": 51000},
            ],
            sample_filename="transactions.csv",
            sample_lines=[
                "date,symbol,price,volume",
                "2024-01-15,AAPL,185.50,45000",
                "2024-01-15,GOOG,141.20,32000",
            ],
        )
        return generate_from_template(dd, concept, difficulty=difficulty)
    return recipe


domain = Domain(
    name="finance",
    description="Financial data processing — stocks, transactions, ledgers, and reports",
)

for con in [
    "file_io", "list_comprehension", "dict_comprehension", "enumerate",
    "context_manager", "try_except", "string_methods", "defaultdict",
    "counter", "lambda", "dataclass", "type_hints_basic", "pathlib",
    "tuple_unpacking", "slicing", "set_ops", "f_strings", "class_basic",
    "function_def", "arithmetic", "basic_types", "import_basic",
    "print_function", "input_function", "if_else", "for_loop", "while_loop",
    "variable_assignment", "return_value", "comparisons", "list_ops", "dict_ops",

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
