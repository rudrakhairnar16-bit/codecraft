from codecraft.domains.registry import Domain, DomainRegistry
from codecraft.engines.templates import DomainData, generate_from_template


def _make_recipe(concept: str):
    def recipe(domain_name: str, target_concepts: list, difficulty: int):
        dd = DomainData(
            domain_name="sysadmin",
            description="Server logs, configuration files, system metrics, and automation scripts",
            nouns=["log_entry", "config_key", "metric", "process", "service", "backup"],
            verbs=["parse", "rotate", "archive", "monitor", "audit"],
            adjectives=["stale", "orphaned", "critical", "scheduled", "unhealthy"],
            sample_data=[
                {"timestamp": "2024-01-15 10:23:45", "level": "ERROR", "service": "nginx", "message": "Connection refused"},
                {"timestamp": "2024-01-15 10:23:46", "level": "INFO", "service": "api", "message": "Request completed"},
            ],
            sample_filename="server.log",
            sample_lines=[
                "2024-01-15 10:23:45 ERROR nginx: Connection refused from 10.0.0.1",
                "2024-01-15 10:23:46 INFO api: GET /health 200 OK",
            ],
        )
        return generate_from_template(dd, concept, difficulty=difficulty)
    return recipe


domain = Domain(
    name="sysadmin",
    description="Server logs, configuration files, system metrics, and automation scripts",
)

for con in [
    "file_io", "list_comprehension", "enumerate", "zip_function",
    "context_manager", "try_except", "string_methods", "defaultdict",
    "counter", "lambda", "pathlib", "slicing", "set_ops", "f_strings",
    "decorator_basic", "function_def", "import_basic", "basic_types",
]:
    domain.register_recipe(con, _make_recipe(con))

DomainRegistry.register(domain)
