from codecraft.domains.registry import Domain, DomainRegistry
from codecraft.engines.templates import DomainData, generate_from_template


def _make_recipe(concept: str):
    def recipe(domain_name: str, target_concepts: list, difficulty: int):
        dd = DomainData(
            domain_name="cli_tools",
            description="Command-line utilities, argument parsing, file processing, and pipelining",
            nouns=["argument", "flag", "subcommand", "config", "output", "pipeline"],
            verbs=["parse", "dispatch", "validate", "transform", "stream"],
            adjectives=["positional", "optional", "deprecated", "recursive", "verbose"],
            sample_data=[
                {"command": "process", "input": "data.csv", "output": "result.json", "verbose": False},
                {"command": "validate", "input": "data.csv", "output": "report.txt", "verbose": True},
            ],
            sample_filename="config.yaml",
            sample_lines=[
                "input: data.csv",
                "output: result.json",
                "verbose: false",
            ],
        )
        return generate_from_template(dd, concept, difficulty=difficulty)
    return recipe


domain = Domain(
    name="cli_tools",
    description="Command-line utilities, argument parsing, file processing, and pipelining",
)

for con in [
    "file_io", "function_def", "import_basic", "try_except", "args_kwargs",
    "context_manager", "pathlib", "f_strings", "type_hints_basic",
    "decorator_basic", "dataclass", "string_methods", "basic_types",
    "enumerate", "list_comprehension",
]:
    domain.register_recipe(con, _make_recipe(con))

DomainRegistry.register(domain)
