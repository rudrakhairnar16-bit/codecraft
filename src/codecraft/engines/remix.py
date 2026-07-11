from __future__ import annotations

import random

from codecraft.db.repository import Repository
from codecraft.domains.registry import DomainRegistry
from codecraft.models.challenge import Challenge


class RemixEngine:
    def __init__(self, repo: Repository):
        self.repo = repo

    def find_gaps(self, threshold: int = 3) -> list[str]:
        concepts = self.repo.get_all_concept_names()
        gaps = []
        for name in concepts:
            exposure = self.repo.get_exposure_count(name)
            if exposure is not None and 1 <= exposure <= threshold:
                gaps.append(name)
        return gaps

    def find_known_concepts(self) -> set[str]:
        return set(self.repo.get_all_concept_names())

    def find_unused_domains(self, concept_name: str) -> list[str]:
        used_files = self.repo.get_concept_timeline(concept_name)
        used_domains = set()
        for entry in used_files:
            fp = entry["file"].lower()
            for domain in DomainRegistry.all():
                if domain.name.lower() in fp:
                    used_domains.add(domain.name)
        all_domains = {d.name for d in DomainRegistry.all()}
        return list(all_domains - used_domains)

    def generate_exercise(
        self, concept_name: str, domain_name: str | None = None
    ) -> Challenge | None:
        domain = None
        if domain_name:
            domain = DomainRegistry.get(domain_name)
        if domain is None:
            unused = self.find_unused_domains(concept_name)
            if unused:
                dname = random.choice(unused)
                domain = DomainRegistry.get(dname)

        if domain is None:
            domain = DomainRegistry.get_random_domain()

        if domain is None:
            return None

        recipe = domain.get_recipe(concept_name)
        if recipe is None:
            recipe = domain.get_recipe("generic_file_parsing")
        if recipe is None:
            return None

        return recipe(
            domain_name=domain.name,
            target_concepts=[concept_name],
            difficulty=1,
        )

    def generate_review_exercise(
        self, concept_name: str
    ) -> Challenge | None:
        unused = self.find_unused_domains(concept_name)
        if unused:
            dname = random.choice(unused)
        else:
            dname = random.choice([d.name for d in DomainRegistry.all() if d.name])

        domain = DomainRegistry.get(dname)
        if domain is None:
            return None

        recipe = domain.get_recipe(concept_name)
        if recipe is None:
            recipe = domain.get_recipe("generic_file_parsing")
        if recipe is None:
            return None

        return recipe(
            domain_name=dname,
            target_concepts=[concept_name],
            difficulty=1,
        )

    def get_domain_stats(self) -> list[dict]:
        stats = []
        known = self.find_known_concepts()
        for domain in DomainRegistry.all():
            supported = set(domain.supported_concepts())
            overlap = supported & known
            stats.append(
                {
                    "domain": domain.name,
                    "description": domain.description,
                    "supported_concepts": len(supported),
                    "your_concepts_matched": len(overlap),
                    "match_ratio": round(len(overlap) / len(supported), 2) if supported else 0,
                }
            )
        return sorted(stats, key=lambda s: s["match_ratio"])
