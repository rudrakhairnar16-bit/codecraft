from typing import Any

from codecraft.domains.registry import Domain, DomainRegistry
from codecraft.engines.templates import DomainData, generate_from_template


def _make_recipe(concept: str) -> Any:
    def recipe(domain_name: str, target_concepts: list[str], difficulty: int) -> Any:
        dd = DomainData(
            domain_name="audio",
            description="Audio sample processing, waveform analysis, filtering, and signal metrics",
            nouns=["sample", "frame", "channel", "frequency", "amplitude", "segment"],
            verbs=["normalize", "filter", "resample", "window", "transform"],
            adjectives=["noisy", "clipped", "mono", "stereo", "aliased"],
            sample_data=[
                {"channel": 0, "samples": 44100, "duration": 1.0, "peak": 0.85},
                {"channel": 1, "samples": 44100, "duration": 1.0, "peak": 0.92},
            ],
            sample_filename="audio.raw",
            sample_lines=[],
        )
        return generate_from_template(dd, concept, difficulty=difficulty)
    return recipe


domain = Domain(
    name="audio",
    description="Audio sample processing, waveform analysis, filtering, and signal metrics",
)

for con in [
    "file_io", "list_comprehension", "enumerate", "slicing",
    "tuple_unpacking", "arithmetic", "function_def", "import_basic",
    "basic_types", "dataclass", "generator_expression", "context_manager",
]:
    domain.register_recipe(con, _make_recipe(con))

DomainRegistry.register(domain)
