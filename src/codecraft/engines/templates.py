from __future__ import annotations

import random
from typing import Any

from codecraft.models.challenge import Challenge, ChallengeType


class DomainData:
    def __init__(
        self,
        domain_name: str,
        description: str,
        nouns: list[str],
        verbs: list[str],
        adjectives: list[str],
        sample_data: list[dict[str, Any]] | None = None,
        sample_filename: str = "data.txt",
        sample_lines: list[str] | None = None,
    ):
        self.domain_name = domain_name
        self.description = description
        self.nouns = nouns
        self.verbs = verbs
        self.adjectives = adjectives
        self.sample_data = sample_data or []
        self.sample_filename = sample_filename
        self.sample_lines = sample_lines or []

    def random_noun(self) -> str:
        return random.choice(self.nouns)

    def random_verb(self) -> str:
        return random.choice(self.verbs)

    def random_adjective(self) -> str:
        return random.choice(self.adjectives)

    def format_line(self, template: str) -> str:
        return template.format(
            noun=self.random_noun(),
            verb=self.random_verb(),
            adj=self.random_adjective(),
            nouns=self.nouns,
            filename=self.sample_filename,
        )


EXERCISE_TEMPLATES: dict[str, str] = {
    "recursion": (
        "Your {noun} data has a nested or self-similar structure. "
        "Write a recursive function with a base case to {verb} through {adj} elements."
    ),
    "str_format": (
        "Your {noun} data needs formatted output with alignment. "
        "Use .format() to create {adj} reports with consistent spacing."
    ),
    "yield_from": (
        "You have nested {noun} collections to flatten. "
        "Use yield from to delegate iteration to sub-generators cleanly."
    ),
    "decorator_args": (
        "Your {noun} processing needs configurable {adj} behavior. "
        "Write a decorator that accepts arguments to customize its logic."
    ),
    "static_class_method": (
        "Your {noun} class needs utility methods. "
        "Use @staticmethod for independent helpers and @classmethod for alternative constructors."
    ),
    "slots": (
        "You create millions of {noun} objects and memory is tight. "
        "Use __slots__ to reduce per-object memory overhead."
    ),
    "abstract_base_class": (
        "You have several {noun} implementations sharing an interface. "
        "Define an ABC with abstractmethod to enforce the contract."
    ),
    "enum": (
        "Your {noun} records have a fixed set of {adj} categories. "
        "Use Enum to define named constants with type safety."
    ),
    "named_tuple": (
        "Your {noun} data is a simple collection of fields. "
        "Use NamedTuple to create lightweight, readable data containers."
    ),
    "typed_dict": (
        "Your {noun} data comes as dicts with a known schema. "
        "Use TypedDict to add type hints for structured dictionary access."
    ),
    "operator_overloading": (
        "Your {noun} objects need to support math or comparison. "
        "Implement __add__, __eq__, __str__ to make them behave like built-ins."
    ),
    "enter_exit": (
        "Your {noun} resource needs setup and teardown. "
        "Implement __enter__ and __exit__ to create a custom context manager."
    ),
    "descriptor": (
        "Your {noun} attributes need validation or computed access. "
        "Use the descriptor protocol (__get__/__set__) for reusable property logic."
    ),
    "metaclass": (
        "You want to auto-register all {noun} subclasses. "
        "Use a custom metaclass to intercept class creation."
    ),
    "mixin": (
        "Multiple {noun} classes share common {adj} behavior. "
        "Use mixin classes to compose reusable functionality."
    ),
    "callable": (
        "Your {noun} objects should be usable as functions. "
        "Implement __call__ to make instances callable with arguments."
    ),
    "getattr_protocol": (
        "Your {noun} objects need dynamic attribute access. "
        "Implement __getattr__ and __getattribute__ for flexible attribute resolution."
    ),
    "init_subclass": (
        "You want to run code when new {noun} subclasses are defined. "
        "Use __init_subclass__ for automatic subclass registration."
    ),
    "singledispatch": (
        "Your {noun} processing function handles multiple types. "
        "Use functools.singledispatch to write type-specific implementations."
    ),
    "lru_cache": (
        "Your {noun} computation is called repeatedly with same args. "
        "Use functools.lru_cache to memoize results and avoid redundant work."
    ),
    "functools_partial": (
        "You call the same {noun} function with fixed arguments repeatedly. "
        "Use functools.partial to create shortcuts with preset parameters."
    ),
    "custom_exception": (
        "Your {noun} processor needs domain-specific errors. "
        "Define custom exception classes inheriting from Exception."
    ),
    "exception_multiple": (
        "Your {noun} parser can fail in different ways. "
        "Use multiple except clauses to handle each error type specifically."
    ),
    "deque": (
        "You need fast appends and pops from both ends of {noun} data. "
        "Use collections.deque for O(1) operations on either side."
    ),
    "heapq": (
        "You need to process {noun} items by priority. "
        "Use heapq to maintain a priority queue with minimal overhead."
    ),
    "weakref": (
        "You cache {noun} objects but want to avoid memory leaks. "
        "Use weakref to hold references without preventing garbage collection."
    ),
    "contextlib": (
        "You want a quick context manager without writing a class. "
        "Use @contextlib.contextmanager to turn a generator into a context manager."
    ),
    "context_var": (
        "Your async {noun} tasks need request-scoped state. "
        "Use contextvars to carry context across async boundaries without globals."
    ),
    "cython_ctypes": (
        "Your {noun} computation needs native speed. "
        "Use ctypes to call C functions directly from Python."
    ),
    "async_await": (
        "Your {noun} processing involves I/O-bound operations. "
        "Use async/await to write concurrent code without threads."
    ),
    "asyncio_gather": (
        "You have multiple independent {noun} tasks. "
        "Use asyncio.gather to run them concurrently and collect results."
    ),
    "async_context": (
        "Your {noun} resource needs async setup and teardown. "
        "Implement __aenter__ and __aexit__ for async context managers."
    ),
    "async_generator": (
        "Your {noun} data stream is produced asynchronously. "
        "Use async generators with yield to produce items over time."
    ),
    "async_iterator": (
        "Your {noun} data source is consumed asynchronously. "
        "Implement __aiter__ and __anext__ for async iteration."
    ),
    "file_io": (
        "Read a file of {noun} records. "
        "Write a function that opens '{filename}', reads each line, "
        "and {verb}s the data into a structured format."
    ),
    "list_comprehension": (
        "You have a list of {noun} data. "
        "Use a list comprehension to {verb} only the items "
        "that match a certain {adj} condition."
    ),
    "dict_comprehension": (
        "Transform a list of {noun} entries into a dictionary "
        "mapping each {adj} identifier to its corresponding {noun} data."
    ),
    "enumerate": (
        "You're processing {noun} records with line numbers. "
        "Use enumerate() to track the index while {verb}ing each record."
    ),
    "zip_function": (
        "You have two parallel lists of {noun} data. "
        "Use zip() to combine them into pairs and {verb} the result."
    ),
    "context_manager": (
        "You're working with a {filename} resource. "
        "Use a context manager (with statement) to safely handle "
        "the resource and ensure proper cleanup."
    ),
    "generator_expression": (
        "Process a large stream of {noun} data efficiently. "
        "Use a generator expression instead of creating a full list "
        "to {verb} items one at a time."
    ),
    "try_except": (
        "Your {noun} parser encounters malformed entries. "
        "Add proper error handling with specific exception types "
        "to gracefully handle {adj} input data."
    ),
    "string_methods": (
        "Each line of {filename} contains {noun} data delimited by various characters. "
        "Use string methods (split, strip, join) to parse and normalize the fields."
    ),
    "defaultdict": (
        "You need to group {noun} records by their {adj} category. "
        "Use collections.defaultdict to avoid manual key checking."
    ),
    "counter": (
        "Count the frequency of different {noun} types in your dataset. "
        "Use collections.Counter for an elegant solution."
    ),
    "lambda": (
        "Sort and filter your {noun} data using custom criteria. "
        "Use lambda functions inline for the sort/filter key."
    ),
    "map_filter_reduce": (
        "Process a collection of {noun} values through a pipeline. "
        "Use map(), filter(), and/or reduce() to transform the data declaratively."
    ),
    "args_kwargs": (
        "Write a flexible function that processes {noun} records "
        "with variable configuration options using *args and **kwargs."
    ),
    "dataclass": (
        "Model your {noun} records as structured data. "
        "Use @dataclass to define a clean data container with type annotations."
    ),
    "type_hints_basic": (
        "Add proper type annotations to your {noun} processing functions "
        "to make the code self-documenting and IDE-friendly."
    ),
    "pathlib": (
        "Navigate a directory of {noun} data files. "
        "Use pathlib.Path for clean, cross-platform file path manipulation."
    ),
    "tuple_unpacking": (
        "Your {noun} data comes in structured pairs/triples. "
        "Use tuple unpacking to elegantly destructure each record."
    ),
    "slicing": (
        "Extract specific portions of your {noun} data sequences. "
        "Use slicing syntax to grab headers, footers, or every Nth item."
    ),
    "set_ops": (
        "Compare two collections of {noun} identifiers. "
        "Use set operations (union, intersection, difference) to find matches and gaps."
    ),
    "match_case": (
        "Route different {noun} record types to appropriate handlers. "
        "Use Python 3.10+'s match/case for clean structural pattern matching."
    ),
    "yield_generator": (
        "Your {noun} dataset is too large to fit in memory. "
        "Write a generator function using yield to stream records one at a time."
    ),
    "itertools": (
        "Chain, cycle, and group your {noun} data using itertools. "
        "Replace nested loops with itertools.product or chain."
    ),
    "f_strings": (
        "Format your {noun} processing output cleanly. "
        "Use f-strings with proper alignment and number formatting."
    ),
    "exception_chaining": (
        "When {noun} processing fails, preserve the full error context. "
        "Use raise ... from ... to chain exceptions without losing information."
    ),
    "class_basic": (
        "Model a {noun} entity as a class with methods "
        "that {verb} the data and properties that expose computed values."
    ),
    "property_decorator": (
        "Add computed properties to your {noun} class. "
        "Use @property to expose derived data without breaking encapsulation."
    ),
    "decorator_basic": (
        "Add cross-cutting behavior (logging, timing, validation) "
        "to your {noun} processing functions using decorators."
    ),
    "import_basic": (
        "Organize your {noun} processing code into modules. "
        "Import and use functionality from the standard library."
    ),
    "function_def": (
        "Break down your {noun} processing pipeline into well-named functions. "
        "Each function should do one thing and have a clear return value."
    ),
    "boolean_ops": (
        "Build complex filtering logic for your {noun} data. "
        "Combine conditions with and/or/not for precise data selection."
    ),
    "arithmetic": (
        "Compute aggregate statistics on your {noun} numerical data. "
        "Use arithmetic operations to calculate totals, averages, and percentages."
    ),
    "basic_types": (
        "Convert and normalize {noun} data types appropriately. "
        "Handle string-to-number conversion, date parsing, and type validation."
    ),
    "print_function": (
        "Write a program that prints a summary of {noun} data. "
        "Use print() to display the {adj} results clearly to the user."
    ),
    "input_function": (
        "Ask the user for {noun} information. "
        "Use input() to get {adj} values from the user and store them in variables."
    ),
    "if_else": (
        "You have a set of {noun} records that need different handling. "
        "Use if/else conditions to process {adj} items differently based on their properties."
    ),
    "for_loop": (
        "Iterate through a collection of {noun} items. "
        "Use a for loop to process each {adj} item one by one."
    ),
    "while_loop": (
        "Keep processing {noun} data until a condition is met. "
        "Use a while loop to repeat until the {adj} condition becomes False."
    ),
    "variable_assignment": (
        "Store and manage {noun} values in your program. "
        "Use variables to hold {adj} data and update them as you process."
    ),
    "return_value": (
        "Write a function that processes {noun} data and gives back a result. "
        "Use return to send the {adj} computed value back to the caller."
    ),
    "comparisons": (
        "Compare different {noun} values to make decisions. "
        "Use comparison operators (==, !=, <, >, <=, >=) to find {adj} matches."
    ),
    "list_ops": (
        "Manage a dynamic list of {noun} items. "
        "Use list methods (append, remove, pop, insert) to add and remove {adj} entries."
    ),
    "dict_ops": (
        "Store and look up {noun} information using keys. "
        "Use dictionary operations to get, set, and update {adj} values efficiently."
    ),
}


def generate_from_template(
    domain_data: DomainData,
    concept_name: str,
    challenge_type: str = ChallengeType.TRANSFER,
    difficulty: int = 1,
) -> Challenge | None:
    template = EXERCISE_TEMPLATES.get(concept_name)
    if template is None:
        return None

    description = template.format(
        noun=domain_data.random_noun(),
        verb=domain_data.random_verb(),
        adj=domain_data.random_adjective(),
        filename=domain_data.sample_filename,
        nouns=", ".join(domain_data.nouns[:3]),
    )

    hints = [
        f"Think about what {domain_data.domain_name} data structures fit naturally here",
        "Start by identifying the input format and desired output",
        "Break the problem into steps: parse, transform, output",
    ]

    challenge_id = f"remix_{domain_data.domain_name}_{concept_name}"

    return Challenge(
        id=challenge_id,
        challenge_type=challenge_type,
        concept_name=concept_name,
        title=f"{concept_name.replace('_', ' ').title()} — {domain_data.domain_name} context",
        description=description,
        code_snippet=_generate_code_stub(domain_data, concept_name),
        expected_solution=f"# Write your solution here\n# Target concept: {concept_name}\n# Domain: {domain_data.domain_name}",
        hints=hints,
        domain=domain_data.domain_name,
        difficulty=difficulty,
    )


def _generate_code_stub(domain_data: DomainData, concept_name: str) -> str:
    noun = domain_data.random_noun()
    filename = domain_data.sample_filename

    stubs = {
        "recursion": f"def factorial_{noun}(n: int) -> int:\n    # TODO: implement recursive function for {noun} computation\n    if n <= 1:\n        return 1\n    return n * factorial_{noun}(n - 1)\n\n\nprint(factorial_{noun}(5))",
        "str_format": f"def format_{noun}_report(items: list) -> str:\n    # TODO: use .format() to create a formatted {noun} report\n    return ''\n\n\nitems = ['sample1', 'sample2']\nprint(format_{noun}_report(items))",
        "yield_from": f"def flatten_{noun}(nested):\n    # TODO: use yield from to flatten nested {noun} collections\n    yield from []\n\n\nfor item in flatten_{noun}([[1, 2], [3]]):\n    print(item)",
        "decorator_args": f"def with_{noun}_config(option: str):\n    # TODO: write a decorator that accepts arguments\n    def decorator(func):\n        def wrapper(*args, **kwargs):\n            return func(*args, **kwargs)\n        return wrapper\n    return decorator",
        "static_class_method": f"class {noun.title()}Utility:\n    @staticmethod\n    def validate(item) -> bool:\n        # TODO: implement static validation for {noun} data\n        return True\n\n    @classmethod\n    def default(cls):\n        return cls()",
        "slots": f"class {noun.title()}:\n    __slots__ = ['name', 'value', 'category']\n    # TODO: implement {noun} class with __slots__\n    def __init__(self, name: str, value: float):\n        self.name = name",
        "abstract_base_class": f"from abc import ABC, abstractmethod\n\n\nclass {noun.title()}Processor(ABC):\n    @abstractmethod\n    def process(self, data: list) -> list:\n        # TODO: implement abstract processing method\n        pass",
        "enum": f"from enum import Enum\n\n\nclass {noun.title()}Type(Enum):\n    # TODO: define enum members for {noun} categories\n    STANDARD = 'standard'\n    PREMIUM = 'premium'",
        "named_tuple": f"from typing import NamedTuple\n\n\nclass {noun.title()}Record(NamedTuple):\n    # TODO: define {noun} fields with type annotations\n    name: str\n    value: float",
        "typed_dict": f"from typing import TypedDict\n\n\nclass {noun.title()}Data(TypedDict):\n    # TODO: define {noun} schema with typed fields\n    name: str\n    count: int",
        "operator_overloading": f"class {noun.title()}:\n    def __init__(self, value: float):\n        self.value = value\n\n    def __add__(self, other):\n        # TODO: implement addition for {noun} objects\n        return {noun.title()}(self.value + other.value)\n\n    def __str__(self):\n        return f'{noun.title()}({{self.value}})'",
        "enter_exit": f"class {noun.title()}Resource:\n    def __enter__(self):\n        # TODO: set up the {noun} resource\n        return self\n\n    def __exit__(self, exc_type, exc_val, exc_tb):\n        # TODO: clean up the {noun} resource\n        pass\n\n\nwith {noun.title()}Resource() as res:\n    pass",
        "descriptor": f"class Validated{noun.title()}:\n    def __get__(self, obj, objtype=None):\n        # TODO: implement descriptor __get__\n        return getattr(obj, '_value', 0)\n\n    def __set__(self, obj, value):\n        # TODO: implement descriptor __set__ with validation\n        obj._value = value",
        "metaclass": f"class RegistryMeta(type):\n    def __new__(mcs, name, bases, namespace):\n        # TODO: auto-register {noun} subclasses\n        return super().__new__(mcs, name, bases, namespace)\n\n\nclass {noun.title()}Base(metaclass=RegistryMeta):\n    pass",
        "mixin": f"class LoggingMixin:\n    def log(self, message: str):\n        print(f'[{{self.__class__.__name__}}] {{message}}')\n\n\nclass {noun.title()}Service(LoggingMixin):\n    def process(self):\n        self.log('Processing {noun} data...')",
        "callable": f"class {noun.title()}Counter:\n    def __init__(self):\n        self.count = 0\n\n    def __call__(self):\n        # TODO: implement __call__ to track {noun} count\n        self.count += 1\n        return self.count\n\n\ncounter = {noun.title()}Counter()\nprint(counter())",
        "getattr_protocol": f"class Dynamic{noun.title()}:\n    def __getattr__(self, name):\n        # TODO: implement dynamic attribute access for {noun} data\n        return f'{{name}}_default'\n\n    def __getattribute__(self, name):\n        return super().__getattribute__(name)",
        "init_subclass": f"class {noun.title()}Base:\n    subclasses = []\n\n    def __init_subclass__(cls, **kwargs):\n        super().__init_subclass__(**kwargs)\n        # TODO: auto-register {noun} subclasses\n        cls.subclasses.append(cls)",
        "singledispatch": f"from functools import singledispatch\n\n\n@singledispatch\ndef process_{noun}(data):\n    # TODO: implement default handler for {noun} data\n    return str(data)\n\n\n@process_{noun}.register\ndef _(data: int):\n    return f'int: {{data}}'",
        "lru_cache": f"from functools import lru_cache\n\n\n@lru_cache(maxsize=128)\ndef compute_{noun}(value: int) -> int:\n    # TODO: implement cached {noun} computation\n    return value * 2",
        "functools_partial": f"from functools import partial\n\n\ndef process_{noun}(data: list, multiplier: int = 1):\n    return [x * multiplier for x in data]\n\n\n# TODO: use partial to create specialized {noun} processors\ndouble = partial(process_{noun}, multiplier=2)",
        "custom_exception": f"class {noun.title()}Error(Exception):\n    \"\"\"Custom exception for {noun} processing errors.\"\"\"\n    pass\n\n\ndef process_{noun}_data(items: list):\n    if not items:\n        raise {noun.title()}Error('No items to process')",
        "exception_multiple": f"def parse_{noun}(line: str) -> dict:\n    # TODO: use multiple except clauses to handle different errors\n    try:\n        parts = line.split(',')\n        return {{'name': parts[0], 'value': float(parts[1])}}\n    except IndexError:\n        return {{'name': 'unknown', 'value': 0}}\n    except ValueError:\n        return {{'name': parts[0], 'value': 0}}",
        "deque": f"from collections import deque\n\n\ndef process_{noun}_stream(items: list) -> deque:\n    # TODO: use deque for efficient appends/pops from both ends\n    dq = deque(maxlen=100)\n    for item in items:\n        dq.append(item)\n    return dq",
        "heapq": f"import heapq\n\n\ndef top_{noun}(items: list, n: int = 3) -> list:\n    # TODO: use heapq to find the top n {noun} items\n    return heapq.nlargest(n, items)",
        "weakref": f"import weakref\n\n\nclass {noun.title()}Cache:\n    def __init__(self):\n        self._cache = weakref.WeakValueDictionary()\n\n    def get(self, key: str):\n        # TODO: implement {noun} cache with weak references\n        return self._cache.get(key)\n\n    def set(self, key: str, value):\n        self._cache[key] = value",
        "contextlib": f"from contextlib import contextmanager\n\n\n@contextmanager\ndef {noun}_resource(name: str):\n    # TODO: implement context manager for {noun} resource\n    print(f'Acquiring {{name}}...')\n    yield {{'name': name, 'ready': True}}\n    print(f'Releasing {{name}}...')",
        "context_var": f"import contextvars\n\n\n{noun}_ctx = contextvars.ContextVar('{noun}')\n\n\ndef set_{noun}(value: str) -> None:\n    {noun}_ctx.set(value)\n\n\ndef get_{noun}() -> str:\n    # TODO: use contextvars for task-local {noun} state\n    return {noun}_ctx.get('default')",
        "cython_ctypes": f"import ctypes\n\n\ndef compute_{noun}_native(values: list) -> float:\n    # TODO: use ctypes to call native code for {noun} computation\n    lib = ctypes.CDLL(None)\n    return sum(values)",
        "async_await": f"import asyncio\n\n\nasync def fetch_{noun}(item_id: int) -> dict:\n    # TODO: implement async {noun} fetcher\n    await asyncio.sleep(0.1)\n    return {{'id': item_id, 'data': f'{noun}_data'}}",
        "asyncio_gather": f"import asyncio\n\n\nasync def process_all_{noun}(items: list) -> list:\n    # TODO: use asyncio.gather for concurrent {noun} processing\n    async def process_one(item):\n        await asyncio.sleep(0.1)\n        return f'processed_{{item}}'\n    results = await asyncio.gather(*[process_one(i) for i in items])\n    return results",
        "async_context": f"import asyncio\n\n\nclass Async{noun.title()}Resource:\n    async def __aenter__(self):\n        # TODO: set up async {noun} resource\n        await asyncio.sleep(0.1)\n        return self\n\n    async def __aexit__(self, exc_type, exc_val, exc_tb):\n        # TODO: clean up async {noun} resource\n        await asyncio.sleep(0.1)",
        "async_generator": f"import asyncio\n\n\nasync def stream_{noun}(items: list):\n    # TODO: use async generator to yield {noun} items\n    for item in items:\n        await asyncio.sleep(0.1)\n        yield item\n\n\nasync def main():\n    async for item in stream_{noun}(['a', 'b', 'c']):\n        print(item)",
        "async_iterator": f"import asyncio\n\n\nclass Async{noun.title()}Iterator:\n    def __init__(self, items: list):\n        self.items = items\n        self.index = 0\n\n    def __aiter__(self):\n        return self\n\n    async def __anext__(self):\n        # TODO: implement async iterator for {noun} items\n        if self.index >= len(self.items):\n            raise StopAsyncIteration\n        await asyncio.sleep(0.1)\n        item = self.items[self.index]\n        self.index += 1\n        return item",
        "file_io": f'def load_{noun}(path: str) -> list:\n    """Load and parse {noun} records from a file."""\n    # TODO: open the file and parse {noun} data\n    pass\n\n\nif __name__ == "__main__":\n    records = load_{noun}("{filename}")\n    print(f"Loaded {{len(records)}} records")',
        "list_comprehension": f"def filter_{noun}(items: list) -> list:\n    # TODO: use a list comprehension to filter {noun} items\n    return []\n\n\n# Example: [item for item in items if condition]",
        "dict_comprehension": f"def map_{noun}(items: list) -> dict:\n    # TODO: build a dict mapping each {noun} to its key\n    return {{}}\n\n\n# Example: {{item.key: item for item in items}}",
        "context_manager": f"def process_{noun}(path: str) -> list:\n    \"\"\"Safely read and parse {filename} using a context manager.\"\"\"\n    # TODO: use 'with' to open the resource\n    return []",
        "enumerate": f"def index_{noun}(items: list) -> list:\n    # TODO: use enumerate() to pair each {noun} with its index\n    return []",
        "defaultdict": f"from collections import defaultdict\n\n\ndef group_{noun}(items: list) -> dict:\n    # TODO: use defaultdict to group {noun} items by category\n    return {{}}",
        "counter": f"from collections import Counter\n\n\ndef count_{noun}(items: list) -> Counter:\n    # TODO: use Counter to tally {noun} occurrences\n    return Counter()",
        "dataclass": f"from dataclasses import dataclass\n\n\n@dataclass\nclass {noun.title()}:\n    \"\"\"A single {noun} record.\"\"\"\n    # TODO: define fields with type annotations\n    pass",
        "yield_generator": f"def stream_{noun}(path: str):\n    \"\"\"Stream {noun} records one at a time.\"\"\"\n    # TODO: use yield to produce records lazily\n    ...\n\n\nfor record in stream_{noun}('{filename}'):\n    print(record)",
        "match_case": f"def handle_{noun}(record: dict) -> str:\n    \"\"\"Route {noun} record by its type using match/case.\"\"\"\n    # TODO: use match/case (Python 3.10+)\n    return ''",
        "print_function": f"def show_{noun}_summary(items: list) -> None:\n    # TODO: use print() to display the {noun} data nicely\n    pass\n\n\nitems = ['sample1', 'sample2']\nshow_{noun}_summary(items)",
        "input_function": f"def get_{noun}_from_user() -> str:\n    # TODO: use input() to ask the user for {noun} info\n    pass\n\n\nresult = get_{noun}_from_user()\nprint(f'Got: {{result}}')",
        "if_else": f"def classify_{noun}(value) -> str:\n    # TODO: use if/elif/else to categorize the {noun} value\n    return ''\n\n\nprint(classify_{noun}(42))",
        "for_loop": f"def process_all_{noun}(items: list) -> list:\n    # TODO: use a for loop to process each {noun} item\n    return []\n\n\ndata = ['a', 'b', 'c']\nresult = process_all_{noun}(data)",
        "function_def": f"def process_{noun}(data: list) -> list:\n    # TODO: break down {noun} processing into a well-named function\n    return data\n\n\nitems = ['a', 'b', 'c']\nresult = process_{noun}(items)\nprint(result)",
        "class_basic": f"class {noun.title()}:\n    \"\"\"Model a {noun} entity with methods.\"\"\"\n    def __init__(self, name: str, value: float):\n        self.name = name\n        self.value = value\n\n    def display(self) -> str:\n        # TODO: return a formatted description of this {noun}\n        return f'{{self.name}}: {{self.value}}'",
        "while_loop": f"def find_{noun}(target) -> int:\n    # TODO: use a while loop to search for the matching item\n    return -1\n\n\nprint(find_{noun}(100))",
        "variable_assignment": f"def track_{noun}() -> dict:\n    # TODO: use variables to store and update {noun} data\n    return {{}}\n\n\nresult = track_{noun}()\nprint(result)",
        "return_value": f"def compute_{noun}_total(values: list) -> float:\n    # TODO: compute and return the total of {noun} values\n    pass\n\n\ntotal = compute_{noun}_total([10, 20, 30])\nprint(total)",
        "comparisons": f"def find_matching_{noun}(items: list):\n    # TODO: use comparisons to find items matching a condition\n    pass\n\n\nresult = find_matching_{noun}([1, 5, 10, 15])",
        "list_ops": f"def manage_{noun}_list() -> list:\n    # TODO: use list methods (append, remove, etc.) to manage {noun} items\n    return []\n\n\nmylist = manage_{noun}_list()",
        "dict_ops": f"def store_{noun}(items: list) -> dict:\n    # TODO: use dict operations to organize {noun} data by key\n    return {{}}\n\n\nresult = store_{noun}(['a', 'b', 'c'])",
    }

    return stubs.get(concept_name, f"# TODO: Write a {domain_data.domain_name}-style exercise for '{concept_name}'\n# Domain: {domain_data.domain_name}\n# Target concept: {concept_name}")
