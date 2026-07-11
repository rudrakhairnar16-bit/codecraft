from __future__ import annotations

import random
from typing import Any, Dict, List, Optional

from codecraft.models.challenge import Challenge, ChallengeType


class DomainData:
    def __init__(
        self,
        domain_name: str,
        description: str,
        nouns: List[str],
        verbs: List[str],
        adjectives: List[str],
        sample_data: Optional[List[Dict[str, Any]]] = None,
        sample_filename: str = "data.txt",
        sample_lines: Optional[List[str]] = None,
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


EXERCISE_TEMPLATES: Dict[str, str] = {
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
    "custom_exception": (
        "Define domain-specific exception classes for your {noun} processor. "
        "This makes error handling more expressive and targeted."
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
) -> Optional[Challenge]:
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
        f"Start by identifying the input format and desired output",
        f"Break the problem into steps: parse, transform, output",
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
        "file_io": f'def load_{noun}(path: str) -> list:\n    """Load and parse {noun} records from a file."""\n    # TODO: open the file and parse {noun} data\n    pass\n\n\nif __name__ == "__main__":\n    records = load_{noun}("{filename}")\n    print(f"Loaded {{len(records)}} records")',
        "list_comprehension": f"def filter_{noun}(items: list) -> list:\n    # TODO: use a list comprehension to filter {noun} items\n    return []\n\n\n# Example: [item for item in items if condition]",
        "dict_comprehension": f"def map_{noun}(items: list) -> dict:\n    # TODO: build a dict mapping each {noun} to its key\n    return {{}}\n\n\n# Example: {{item.key: item for item in items}}",
        "context_manager": f"def process_{filename}(path: str) -> list:\n    \"\"\"Safely read and parse {filename} using a context manager.\"\"\"\n    # TODO: use 'with' to open the resource\n    return []",
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
        "while_loop": f"def find_{noun}(target) -> int:\n    # TODO: use a while loop to search for the matching item\n    return -1\n\n\nprint(find_{noun}(100))",
        "variable_assignment": f"def track_{noun}() -> dict:\n    # TODO: use variables to store and update {noun} data\n    return {{}}\n\n\nresult = track_{noun}()\nprint(result)",
        "return_value": f"def compute_{noun}_total(values: list) -> float:\n    # TODO: compute and return the total of {noun} values\n    pass\n\n\ntotal = compute_{noun}_total([10, 20, 30])\nprint(total)",
        "comparisons": f"def find_matching_{noun}(items: list):\n    # TODO: use comparisons to find items matching a condition\n    pass\n\n\nresult = find_matching_{noun}([1, 5, 10, 15])",
        "list_ops": f"def manage_{noun}_list() -> list:\n    # TODO: use list methods (append, remove, etc.) to manage {noun} items\n    return []\n\n\nmylist = manage_{noun}_list()",
        "dict_ops": f"def store_{noun}(items: list) -> dict:\n    # TODO: use dict operations to organize {noun} data by key\n    return {{}}\n\n\nresult = store_{noun}(['a', 'b', 'c'])",
    }

    return stubs.get(concept_name, f"# TODO: Write a {domain_data.domain_name}-style exercise for '{concept_name}'\n# Domain: {domain_data.domain_name}\n# Target concept: {concept_name}")
