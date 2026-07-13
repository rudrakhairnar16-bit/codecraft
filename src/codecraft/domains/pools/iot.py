from typing import Any

from codecraft.domains.registry import Domain, DomainRegistry
from codecraft.engines.templates import DomainData, generate_from_template


def _make_recipe(concept: str) -> Any:
    def recipe(domain_name: str, target_concepts: list[str], difficulty: int) -> Any:
        dd = DomainData(
            domain_name="iot",
            description="Sensor readings, telemetry data, device commands, and edge processing",
            nouns=["sensor", "reading", "device", "telemetry", "actuator", "sample"],
            verbs=["calibrate", "poll", "aggregate", "threshold", "normalize"],
            adjectives=["noisy", "intermittent", "low_power", "real_time", "faulty"],
            sample_data=[
                {"device_id": "sensor_01", "temperature": 23.5, "humidity": 0.45, "timestamp": 1705312000},
                {"device_id": "sensor_02", "temperature": 24.1, "humidity": 0.48, "timestamp": 1705312001},
            ],
            sample_filename="telemetry.csv",
            sample_lines=[
                "timestamp,device_id,temperature,humidity",
                "1705312000,sensor_01,23.5,0.45",
            ],
        )
        return generate_from_template(dd, concept, difficulty=difficulty)
    return recipe


domain = Domain(
    name="iot",
    description="Sensor readings, telemetry data, device commands, and edge processing",
)

for con in [
    "file_io", "list_comprehension", "dict_comprehension", "enumerate",
    "generator_expression", "context_manager", "try_except", "string_methods",
    "defaultdict", "dataclass", "pathlib", "yield_generator",
    "f_strings", "function_def", "arithmetic", "basic_types", "import_basic",
]:
    domain.register_recipe(con, _make_recipe(con))

DomainRegistry.register(domain)
