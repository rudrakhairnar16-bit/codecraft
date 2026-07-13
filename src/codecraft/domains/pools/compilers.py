from typing import Any

from codecraft.domains.registry import Domain, DomainRegistry
from codecraft.engines.templates import DomainData, generate_from_template


def _make_recipe(concept: str) -> Any:
    def recipe(domain_name: str, target_concepts: list[str], difficulty: int) -> Any:
        dd = DomainData(
            domain_name="compilers",
            description="Tokenization, parsing, AST manipulation, code generation, and symbol tables",
            nouns=["token", "node", "symbol", "instruction", "block", "expression"],
            verbs=["parse", "lex", "optimize", "emit", "resolve"],
            adjectives=["recursive", "infix", "polymorphic", "untyped", "constant"],
            sample_data=[
                {"token": "IF", "value": None, "line": 1},
                {"token": "IDENTIFIER", "value": "x", "line": 1},
                {"token": "NUMBER", "value": "42", "line": 1},
            ],
            sample_filename="source.lang",
            sample_lines=[
                "if x > 42:",
                "    print('hello')",
            ],
        )
        return generate_from_template(dd, concept, difficulty=difficulty)
    return recipe


domain = Domain(
    name="compilers",
    description="Tokenization, parsing, AST manipulation, code generation, and symbol tables",
)

for con in [
    "file_io", "list_comprehension", "dict_comprehension", "enumerate",
    "string_methods", "defaultdict", "match_case", "recursion",
    "dataclass", "class_basic", "function_def", "import_basic",
    "type_hints_basic", "tuple_unpacking", "f_strings",
]:
    domain.register_recipe(con, _make_recipe(con))

DomainRegistry.register(domain)
