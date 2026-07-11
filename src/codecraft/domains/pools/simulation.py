from codecraft.domains.registry import Domain, DomainRegistry
from codecraft.engines.templates import DomainData, generate_from_template


def _make_recipe(concept: str):
    def recipe(domain_name: str, target_concepts: list, difficulty: int):
        dd = DomainData(
            domain_name="simulation",
            description="Monte Carlo methods, agent-based models, physics simulations, and state machines",
            nouns=["particle", "agent", "state", "step", "iteration", "parameter"],
            verbs=["evolve", "simulate", "propagate", "equilibrate", "perturb"],
            adjectives=["stochastic", "discrete", "continuous", "transient", "steady"],
            sample_data=[
                {"step": 0, "population": 100, "temperature": 300, "energy": 4500},
                {"step": 1, "population": 102, "temperature": 301, "energy": 4520},
            ],
            sample_filename="simulation_params.json",
            sample_lines=[
                '{"step": 0, "population": 100}',
                '{"step": 1, "population": 102}',
            ],
        )
        return generate_from_template(dd, concept, difficulty=difficulty)
    return recipe


domain = Domain(
    name="simulation",
    description="Monte Carlo methods, agent-based models, physics simulations, and state machines",
)

for con in [
    "class_basic", "list_comprehension", "dict_comprehension", "enumerate",
    "generator_expression", "yield_generator", "try_except", "defaultdict",
    "dataclass", "lambda", "property_decorator", "function_def",
    "arithmetic", "import_basic", "basic_types", "tuple_unpacking",
]:
    domain.register_recipe(con, _make_recipe(con))

DomainRegistry.register(domain)
