from __future__ import annotations

from pathlib import Path
from typing import Callable, Dict, List, Optional, Protocol

from codecraft.models.challenge import Challenge


class ExerciseRecipe(Protocol):
    def __call__(self, domain_name: str, target_concepts: List[str], difficulty: int) -> Challenge:
        ...


class Domain:
    def __init__(
        self,
        name: str,
        description: str,
        variable_suffixes: Optional[List[str]] = None,
    ):
        self.name = name
        self.description = description
        self.variable_suffixes = variable_suffixes or ["_data", "_list", "_records"]
        self._recipes: Dict[str, ExerciseRecipe] = {}

    def register_recipe(self, concept_key: str, recipe: ExerciseRecipe) -> None:
        self._recipes[concept_key] = recipe

    def get_recipe(self, concept_key: str) -> Optional[ExerciseRecipe]:
        return self._recipes.get(concept_key)

    def has_recipe_for(self, concept_key: str) -> bool:
        return concept_key in self._recipes

    def supported_concepts(self) -> List[str]:
        return list(self._recipes.keys())


class DomainRegistry:
    _domains: Dict[str, Domain] = {}

    @classmethod
    def register(cls, domain: Domain) -> None:
        cls._domains[domain.name] = domain

    @classmethod
    def get(cls, name: str) -> Optional[Domain]:
        return cls._domains.get(name)

    @classmethod
    def all(cls) -> List[Domain]:
        return list(cls._domains.values())

    @classmethod
    def find_domain_for_concepts(
        cls, concepts: List[str], exclude: Optional[List[str]] = None
    ) -> Optional[Domain]:
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
    def get_random_domain(cls, exclude: Optional[List[str]] = None) -> Optional[Domain]:
        import random
        domains = [d for d in cls.all() if d.name not in (exclude or [])]
        if not domains:
            return None
        return random.choice(domains)
