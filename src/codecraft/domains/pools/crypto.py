from typing import Any

from codecraft.domains.registry import Domain, DomainRegistry
from codecraft.engines.templates import DomainData, generate_from_template


def _make_recipe(concept: str) -> Any:
    def recipe(domain_name: str, target_concepts: list[str], difficulty: int) -> Any:
        dd = DomainData(
            domain_name="crypto",
            description="Cipher implementation, key derivation, encoding schemes, and cryptographic primitives",
            nouns=["ciphertext", "key", "nonce", "digest", "signature", "plaintext"],
            verbs=["encrypt", "decrypt", "hash", "sign", "derive"],
            adjectives=["salted", "padded", "truncated", "symmetric", "asymmetric"],
            sample_data=[
                {"algorithm": "AES", "key_size": 256, "mode": "GCM"},
                {"algorithm": "RSA", "key_size": 2048, "mode": "OAEP"},
            ],
            sample_filename="keyfile.bin",
            sample_lines=[],
        )
        return generate_from_template(dd, concept, difficulty=difficulty)
    return recipe


domain = Domain(
    name="crypto",
    description="Cipher implementation, key derivation, encoding schemes, and cryptographic primitives",
)

for con in [
    "file_io", "list_comprehension", "enumerate", "zip_function",
    "tuple_unpacking", "slicing", "arithmetic", "basic_types",
    "function_def", "import_basic", "dataclass", "string_methods",
    "try_except", "f_strings",
]:
    domain.register_recipe(con, _make_recipe(con))

DomainRegistry.register(domain)
