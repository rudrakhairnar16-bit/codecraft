from codecraft.domains.registry import Domain, DomainRegistry
from codecraft.engines.templates import DomainData, generate_from_template


def _make_recipe(concept: str):
    def recipe(domain_name: str, target_concepts: list, difficulty: int):
        dd = DomainData(
            domain_name="data_viz",
            description="Chart data preparation, dataset transformation, and statistical summaries",
            nouns=["dataset", "series", "category", "axis", "label", "distribution"],
            verbs=["aggregate", "normalize", "bin", "interpolate", "filter"],
            adjectives=["outlier", "missing", "skewed", "correlated", "seasonal"],
            sample_data=[
                {"category": "A", "value": 42, "date": "2024-01"},
                {"category": "B", "value": 68, "date": "2024-01"},
                {"category": "A", "value": 55, "date": "2024-02"},
            ],
            sample_filename="dataset.csv",
            sample_lines=[
                "date,category,value",
                "2024-01,A,42",
                "2024-01,B,68",
            ],
        )
        return generate_from_template(dd, concept, difficulty=difficulty)
    return recipe


domain = Domain(
    name="data_viz",
    description="Chart data preparation, dataset transformation, and statistical summaries",
)

for con in [
    "file_io", "list_comprehension", "dict_comprehension", "enumerate",
    "zip_function", "defaultdict", "counter", "lambda", "dataclass",
    "tuple_unpacking", "slicing", "set_ops", "f_strings", "function_def",
    "arithmetic", "basic_types", "import_basic",
]:
    domain.register_recipe(con, _make_recipe(con))

DomainRegistry.register(domain)
