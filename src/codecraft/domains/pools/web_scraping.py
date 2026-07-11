from codecraft.domains.registry import Domain, DomainRegistry
from codecraft.engines.templates import DomainData, generate_from_template


def _make_recipe(concept: str):
    def recipe(domain_name: str, target_concepts: list, difficulty: int):
        dd = DomainData(
            domain_name="web_scraping",
            description="HTML parsing, API responses, pagination, and data extraction pipelines",
            nouns=["page", "element", "response", "endpoint", "selector", "payload"],
            verbs=["scrape", "extract", "paginate", "sanitize", "transform"],
            adjectives=["dynamic", "nested", "rate_limited", "authenticated", "malformed"],
            sample_data=[
                {"url": "https://example.com/item/1", "title": "Product A", "price": 29.99},
                {"url": "https://example.com/item/2", "title": "Product B", "price": 49.99},
            ],
            sample_filename="pages.txt",
            sample_lines=[
                '<div class="item"><h2>Product A</h2><span class="price">$29.99</span></div>',
                '<div class="item"><h2>Product B</h2><span class="price">$49.99</span></div>',
            ],
        )
        return generate_from_template(dd, concept, difficulty=difficulty)
    return recipe


domain = Domain(
    name="web_scraping",
    description="HTML parsing, API responses, pagination, and data extraction pipelines",
)

for con in [
    "file_io", "list_comprehension", "dict_comprehension", "enumerate",
    "context_manager", "try_except", "string_methods", "defaultdict",
    "counter", "lambda", "dataclass", "tuple_unpacking", "f_strings",
    "function_def", "import_basic", "basic_types", "slicing",
]:
    domain.register_recipe(con, _make_recipe(con))

DomainRegistry.register(domain)
