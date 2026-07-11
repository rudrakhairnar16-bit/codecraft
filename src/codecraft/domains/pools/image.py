from codecraft.domains.registry import Domain, DomainRegistry
from codecraft.engines.templates import DomainData, generate_from_template


def _make_recipe(concept: str):
    def recipe(domain_name: str, target_concepts: list, difficulty: int):
        dd = DomainData(
            domain_name="image",
            description="Pixel data manipulation, color transformations, convolution filters, and metadata",
            nouns=["pixel", "channel", "kernel", "histogram", "tile", "palette"],
            verbs=["convolve", "threshold", "quantize", "interpolate", "blend"],
            adjectives=["grayscale", "binarized", "downsampled", "overexposed", "chromatic"],
            sample_data=[
                {"pixel": 0, "red": 128, "green": 64, "blue": 255},
                {"pixel": 1, "red": 0, "green": 128, "blue": 64},
            ],
            sample_filename="image.raw",
            sample_lines=[],
        )
        return generate_from_template(dd, concept, difficulty=difficulty)
    return recipe


domain = Domain(
    name="image",
    description="Pixel data manipulation, color transformations, convolution filters, and metadata",
)

for con in [
    "file_io", "list_comprehension", "dict_comprehension", "enumerate",
    "slicing", "tuple_unpacking", "zip_function", "function_def",
    "dataclass", "arithmetic", "import_basic", "basic_types",
]:
    domain.register_recipe(con, _make_recipe(con))

DomainRegistry.register(domain)
