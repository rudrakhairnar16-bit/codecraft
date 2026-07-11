from codecraft.domains.registry import Domain, DomainRegistry
from codecraft.engines.templates import DomainData, generate_from_template


def _make_recipe(concept: str):
    def recipe(domain_name: str, target_concepts: list, difficulty: int):
        dd = DomainData(
            domain_name="sports_cricket",
            description="Cricket scoring, player statistics, match simulation, and tournament management",
            nouns=["run", "wicket", "over", "batsman", "bowler", "team", "stadium"],
            verbs=["bat", "bowl", "chase", "defend", "stump"],
            adjectives=["powerplay", "super_over", "test", "t20", "odi"],
            sample_data=[
                {"player": "Virat", "runs": 82, "balls": 56, "fours": 8, "sixes": 2},
                {"player": "Rohit", "runs": 45, "balls": 38, "fours": 4, "sixes": 3},
            ],
            sample_filename="scorecard.csv",
            sample_lines=[
                "player,runs,balls,fours,sixes",
                "Virat,82,56,8,2",
                "Rohit,45,38,4,3",
            ],
        )
        return generate_from_template(dd, concept, difficulty=difficulty)
    return recipe


domain = Domain(
    name="sports_cricket",
    description="Cricket scoring, player statistics, match simulation, and tournament management",
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
