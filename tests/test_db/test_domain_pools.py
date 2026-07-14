from __future__ import annotations

from codecraft.domains.registry import DomainRegistry


def _import_all_pools():
    import codecraft.domains.pools.audio
    import codecraft.domains.pools.bioinfo
    import codecraft.domains.pools.cli_tools
    import codecraft.domains.pools.compilers
    import codecraft.domains.pools.crypto
    import codecraft.domains.pools.data_viz
    import codecraft.domains.pools.education
    import codecraft.domains.pools.finance
    import codecraft.domains.pools.gaming
    import codecraft.domains.pools.health
    import codecraft.domains.pools.image
    import codecraft.domains.pools.iot
    import codecraft.domains.pools.networking
    import codecraft.domains.pools.nlp
    import codecraft.domains.pools.science
    import codecraft.domains.pools.simulation
    import codecraft.domains.pools.sports_cricket
    import codecraft.domains.pools.sysadmin
    import codecraft.domains.pools.travel
    import codecraft.domains.pools.web_scraping


EXPECTED_POOLS = {
    "audio", "bioinformatics", "cli_tools", "compilers", "crypto",
    "data_viz", "education", "finance", "gaming", "health",
    "image", "iot", "networking", "nlp", "science",
    "simulation", "sports_cricket", "sysadmin", "travel",
    "web_scraping",
}


def test_all_domain_pools_register():
    _import_all_pools()
    registered = {d.name for d in DomainRegistry.all()}
    assert EXPECTED_POOLS.issubset(registered), f"Missing: {EXPECTED_POOLS - registered}"


def test_each_domain_accessible_via_registry():
    _import_all_pools()
    for name in EXPECTED_POOLS:
        domain = DomainRegistry.get(name)
        assert domain is not None, f"Domain {name} not registered"
        assert domain.name == name
        assert len(domain.supported_concepts()) > 0


def test_each_pool_recipe_generates_challenge():
    _import_all_pools()
    for name in EXPECTED_POOLS:
        domain = DomainRegistry.get(name)
        assert domain is not None
        concepts = domain.supported_concepts()
        assert len(concepts) > 0
        concept = concepts[0]
        recipe = domain.get_recipe(concept)
        assert recipe is not None
        challenge = recipe(domain_name=name, target_concepts=[concept], difficulty=1)
        assert challenge is not None
        assert challenge.domain == name
        assert challenge.concept_name == concept
