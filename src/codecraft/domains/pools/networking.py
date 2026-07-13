from typing import Any

from codecraft.domains.registry import Domain, DomainRegistry
from codecraft.engines.templates import DomainData, generate_from_template


def _make_recipe(concept: str) -> Any:
    def recipe(domain_name: str, target_concepts: list[str], difficulty: int) -> Any:
        dd = DomainData(
            domain_name="networking",
            description="Packet analysis, protocol parsing, client-server communication, and socket data",
            nouns=["packet", "header", "payload", "connection", "stream", "frame"],
            verbs=["encapsulate", "checksum", "fragment", "handshake", "route"],
            adjectives=["malformed", "truncated", "encrypted", "unreliable", "out_of_order"],
            sample_data=[
                {"src": "10.0.0.1", "dst": "10.0.0.2", "port": 8080, "size": 512},
                {"src": "10.0.0.2", "dst": "10.0.0.1", "port": 8080, "size": 256},
            ],
            sample_filename="capture.pcap",
            sample_lines=[],
        )
        return generate_from_template(dd, concept, difficulty=difficulty)
    return recipe


domain = Domain(
    name="networking",
    description="Packet analysis, protocol parsing, client-server communication, and socket data",
)

for con in [
    "file_io", "list_comprehension", "dict_comprehension", "enumerate",
    "context_manager", "try_except", "string_methods", "defaultdict",
    "dataclass", "tuple_unpacking", "slicing", "f_strings",
    "function_def", "import_basic", "basic_types",
]:
    domain.register_recipe(con, _make_recipe(con))

DomainRegistry.register(domain)
