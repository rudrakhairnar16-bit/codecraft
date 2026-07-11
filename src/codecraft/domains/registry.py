from __future__ import annotations

from typing import Protocol

from codecraft.models.challenge import Challenge


class ExerciseRecipe(Protocol):
    def __call__(self, domain_name: str, target_concepts: list[str], difficulty: int) -> Challenge:
        ...


class Domain:
    def __init__(
        self,
        name: str,
        description: str,
        variable_suffixes: list[str] | None = None,
    ):
        self.name = name
        self.description = description
        self.variable_suffixes = variable_suffixes or ["_data", "_list", "_records"]
        self._recipes: dict[str, ExerciseRecipe] = {}

    def register_recipe(self, concept_key: str, recipe: ExerciseRecipe) -> None:
        self._recipes[concept_key] = recipe

    def get_recipe(self, concept_key: str) -> ExerciseRecipe | None:
        return self._recipes.get(concept_key)

    def has_recipe_for(self, concept_key: str) -> bool:
        return concept_key in self._recipes

    def supported_concepts(self) -> list[str]:
        return list(self._recipes.keys())


class DomainRegistry:
    _domains: dict[str, Domain] = {}

    @classmethod
    def register(cls, domain: Domain) -> None:
        cls._domains[domain.name] = domain

    @classmethod
    def get(cls, name: str) -> Domain | None:
        return cls._domains.get(name)

    @classmethod
    def all(cls) -> list[Domain]:
        return list(cls._domains.values())

    @classmethod
    def find_domain_for_concepts(
        cls, concepts: list[str], exclude: list[str] | None = None
    ) -> Domain | None:
        exclude = exclude or []
        best_domain = None
        best_count = 0
        for domain in cls.all():
            if domain.name in exclude:
                continue
            supported = set(domain.supported_concepts())
            match_count = sum(1 for c in concepts if c in supported)
            if match_count > best_count:
                best_count = match_count
                best_domain = domain
        if best_count == 0:
            return None
        return best_domain

    @classmethod
    def get_random_domain(cls, exclude: list[str] | None = None) -> Domain | None:
        import random
        domains = [d for d in cls.all() if d.name not in (exclude or [])]
        if not domains:
            return None
        return random.choice(domains)
