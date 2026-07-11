from codecraft.domains.registry import Domain, DomainRegistry
from codecraft.engines.templates import DomainData, generate_from_template


def _make_recipe(concept: str):
    def recipe(domain_name: str, target_concepts: list, difficulty: int):
        dd = DomainData(
            domain_name="science",
            description="Scientific experiments, lab data analysis, physics formulas, and chemistry calculations",
            nouns=["beaker", "specimen", "formula", "reading", "sample", "element"],
            verbs=["measure", "calibrate", "react", "distill", "observe"],
            adjectives=["molar", "aqueous", "isotopic", "centrifuged", "sterile"],
            sample_data=[
                {"element": "Oxygen", "symbol": "O", "mass": 15.999, "group": 16},
                {"element": "Hydrogen", "symbol": "H", "mass": 1.008, "group": 1},
            ],
            sample_filename="periodic_table.csv",
            sample_lines=[
                "element,symbol,mass,group",
                "Oxygen,O,15.999,16",
                "Hydrogen,H,1.008,1",
            ],
        )
        return generate_from_template(dd, concept, difficulty=difficulty)
    return recipe


domain = Domain(
    name="science",
    description="Scientific experiments, lab data analysis, physics formulas, and chemistry calculations",
)

for con in [
    "list_comprehension", "dict_comprehension", "enumerate",
    "context_manager", "try_except", "string_methods", "defaultdict",
    "counter", "lambda", "dataclass", "type_hints_basic", "pathlib",
    "tuple_unpacking", "slicing", "set_ops", "f_strings", "class_basic",
    "function_def", "arithmetic", "basic_types", "import_basic",
    "print_function", "input_function", "if_else", "for_loop", "while_loop",
    "variable_assignment", "return_value", "comparisons", "list_ops", "dict_ops",
]:
    domain.register_recipe(con, _make_recipe(con))

DomainRegistry.register(domain)
