from codecraft.domains.registry import Domain, DomainRegistry
from codecraft.engines.templates import DomainData, generate_from_template


def _make_recipe(concept: str):
    def recipe(domain_name: str, target_concepts: list, difficulty: int):
        dd = DomainData(
            domain_name="nlp",
            description="Text processing, tokenization, sentiment analysis, and corpus statistics",
            nouns=["token", "document", "corpus", "ngram", "sentence", "vocabulary"],
            verbs=["tokenize", "stem", "lemmatize", "vectorize", "classify"],
            adjectives=["stopword", "inflected", "multilingual", "noisy", "annotated"],
            sample_data=[
                {"text": "The quick brown fox jumps over the lazy dog", "tokens": 9, "sentiment": 0.2},
                {"text": "I love this product, it's amazing!", "tokens": 7, "sentiment": 0.9},
            ],
            sample_filename="corpus.txt",
            sample_lines=[
                "The quick brown fox jumps over the lazy dog.",
                "I love this product, it's amazing!",
            ],
        )
        return generate_from_template(dd, concept, difficulty=difficulty)
    return recipe


domain = Domain(
    name="nlp",
    description="Text processing, tokenization, sentiment analysis, and corpus statistics",
)

for con in [
    "file_io", "list_comprehension", "dict_comprehension", "enumerate",
    "string_methods", "defaultdict", "counter", "generator_expression",
    "lambda", "tuple_unpacking", "set_ops", "f_strings", "function_def",
    "import_basic", "basic_types", "slicing",
]:
    domain.register_recipe(con, _make_recipe(con))

DomainRegistry.register(domain)
