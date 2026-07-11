from codecraft.domains.registry import Domain, DomainRegistry
from codecraft.engines.templates import DomainData, generate_from_template


def _make_recipe(concept: str):
    def recipe(domain_name: str, target_concepts: list, difficulty: int):
        dd = DomainData(
            domain_name="travel",
            description="Trip planning, distance calculations, itinerary management, and travel budgeting",
            nouns=["destination", "flight", "hotel", "route", "booking", "passport"],
            verbs=["book", "navigate", "pack", "explore", "check_in"],
            adjectives=["domestic", "international", "budget", "luxury", "one_way"],
            sample_data=[
                {"city": "Mumbai", "country": "India", "distance_km": 0, "timezone": "IST"},
                {"city": "London", "country": "UK", "distance_km": 7200, "timezone": "GMT"},
            ],
            sample_filename="destinations.csv",
            sample_lines=[
                "city,country,distance_km,timezone",
                "Mumbai,India,0,IST",
                "London,UK,7200,GMT",
            ],
        )
        return generate_from_template(dd, concept, difficulty=difficulty)
    return recipe


domain = Domain(
    name="travel",
    description="Trip planning, distance calculations, itinerary management, and travel budgeting",
)

for con in [
    "list_comprehension", "dict_comprehension", "enumerate",
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
