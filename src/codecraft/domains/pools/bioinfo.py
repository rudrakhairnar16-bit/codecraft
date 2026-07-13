from typing import Any

from codecraft.domains.registry import Domain, DomainRegistry
from codecraft.engines.templates import DomainData, generate_from_template


def _make_recipe(concept: str) -> Any:
    def recipe(domain_name: str, target_concepts: list[str], difficulty: int) -> Any:
        dd = DomainData(
            domain_name="bioinformatics",
            description="DNA sequences, gene annotations, protein structures, and lab data",
            nouns=["sequence", "gene", "protein", "mutation", "chromosome", "primer"],
            verbs=["align", "translate", "annotate", "filter", "cluster"],
            adjectives=["conserved", "coding", "noncoding", "orthologous", "expressed"],
            sample_data=[
                {"id": "seq_001", "sequence": "ATGCGTA", "length": 7, "gc_content": 0.57},
                {"id": "seq_002", "sequence": "TGCATGC", "length": 7, "gc_content": 0.43},
            ],
            sample_filename="sequences.fasta",
            sample_lines=[
                ">seq_001 sample sequence",
                "ATGCGTACGTAGCTAGCTAGC",
                ">seq_002 another sequence",
                "TGCATGCTAGCTAGCTAGC",
            ],
        )
        return generate_from_template(dd, concept, difficulty=difficulty)
    return recipe


domain = Domain(
    name="bioinformatics",
    description="DNA sequences, gene annotations, protein structures, and lab data",
)

for con in [
    "file_io", "list_comprehension", "dict_comprehension", "enumerate",
    "context_manager", "try_except", "string_methods", "generator_expression",
    "defaultdict", "counter", "tuple_unpacking", "set_ops", "yield_generator",
    "dataclass", "type_hints_basic", "f_strings", "function_def", "import_basic",
]:
    domain.register_recipe(con, _make_recipe(con))

DomainRegistry.register(domain)
