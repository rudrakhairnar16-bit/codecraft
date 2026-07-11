from codecraft.domains.registry import Domain, DomainRegistry
from codecraft.engines.templates import DomainData, generate_from_template


def _make_recipe(concept: str):
    def recipe(domain_name: str, target_concepts: list, difficulty: int):
        dd = DomainData(
            domain_name="health",
            description="Fitness tracking, BMI calculation, diet planning, and health metrics",
            nouns=["calorie", "workout", "heart_rate", "weight", "step", "meal"],
            verbs=["track", "log", "burn", "measure", "schedule"],
            adjectives=["cardio", "aerobic", "daily", "weekly", "target"],
            sample_data=[
                {"activity": "Running", "calories": 320, "duration_min": 30, "heart_rate": 145},
                {"activity": "Cycling", "calories": 250, "duration_min": 25, "heart_rate": 130},
            ],
            sample_filename="fitness_log.csv",
            sample_lines=[
                "activity,calories,duration_min,heart_rate",
                "Running,320,30,145",
                "Cycling,250,25,130",
            ],
        )
        return generate_from_template(dd, concept, difficulty=difficulty)
    return recipe


domain = Domain(
    name="health",
    description="Fitness tracking, BMI calculation, diet planning, and health metrics",
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
