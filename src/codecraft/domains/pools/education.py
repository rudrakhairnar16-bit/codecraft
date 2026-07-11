from codecraft.domains.registry import Domain, DomainRegistry
from codecraft.engines.templates import DomainData, generate_from_template


def _make_recipe(concept: str):
    def recipe(domain_name: str, target_concepts: list, difficulty: int):
        dd = DomainData(
            domain_name="education",
            description="Grade tracking, quiz systems, student records, and course management",
            nouns=["student", "grade", "subject", "exam", "assignment", "report_card"],
            verbs=["enroll", "grade", "teach", "submit", "evaluate"],
            adjectives=["midterm", "elective", "core", "remedial", "honors"],
            sample_data=[
                {"student": "Rahul", "subject": "Math", "score": 92, "grade": "A"},
                {"student": "Priya", "subject": "Science", "score": 88, "grade": "B+"},
            ],
            sample_filename="marks.csv",
            sample_lines=[
                "student,subject,score,grade",
                "Rahul,Math,92,A",
                "Priya,Science,88,B+",
            ],
        )
        return generate_from_template(dd, concept, difficulty=difficulty)
    return recipe


domain = Domain(
    name="education",
    description="Grade tracking, quiz systems, student records, and course management",
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
