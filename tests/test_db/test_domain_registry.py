from __future__ import annotations

from codecraft.domains.registry import Domain, DomainRegistry


class TestDomain:
    def test_create(self):
        d = Domain(name="test_domain", description="Test domain")
        assert d.name == "test_domain"
        assert d.variable_suffixes == ["_data", "_list", "_records"]

    def test_custom_suffixes(self):
        d = Domain(name="test", description="Test", variable_suffixes=["_x"])
        assert d.variable_suffixes == ["_x"]

    def test_register_recipe(self):
        d = Domain(name="test", description="Test")
        recipe = lambda dn, tc, diff: None
        d.register_recipe("for_loop", recipe)
        assert d.has_recipe_for("for_loop")
        assert d.get_recipe("for_loop") is recipe
        assert d.get_recipe("nonexistent") is None

    def test_supported_concepts(self):
        d = Domain(name="test", description="Test")
        d.register_recipe("for_loop", lambda dn, tc, diff: None)
        d.register_recipe("if_else", lambda dn, tc, diff: None)
        concepts = d.supported_concepts()
        assert "for_loop" in concepts
        assert "if_else" in concepts
        assert len(concepts) == 2


class TestDomainRegistry:
    def setup_method(self):
        self._saved = DomainRegistry._domains.copy()
        DomainRegistry._domains = {}

    def teardown_method(self):
        DomainRegistry._domains = self._saved

    def test_register_and_get(self):
        d = Domain(name="gaming", description="Gaming")
        DomainRegistry.register(d)
        assert DomainRegistry.get("gaming") is d
        assert DomainRegistry.get("nonexistent") is None

    def test_all(self):
        d1 = Domain(name="gaming", description="Gaming")
        d2 = Domain(name="finance", description="Finance")
        DomainRegistry.register(d1)
        DomainRegistry.register(d2)
        domains = DomainRegistry.all()
        assert len(domains) == 2

    def test_find_domain_for_concepts(self):
        d1 = Domain(name="gaming", description="Gaming")
        d1.register_recipe("for_loop", lambda dn, tc, diff: None)
        d2 = Domain(name="finance", description="Finance")
        d2.register_recipe("if_else", lambda dn, tc, diff: None)
        DomainRegistry.register(d1)
        DomainRegistry.register(d2)
        result = DomainRegistry.find_domain_for_concepts(["for_loop"])
        assert result is d1

    def test_find_domain_for_concepts_no_match(self):
        d = Domain(name="gaming", description="Gaming")
        d.register_recipe("for_loop", lambda dn, tc, diff: None)
        DomainRegistry.register(d)
        result = DomainRegistry.find_domain_for_concepts(["nonexistent"])
        assert result is None

    def test_find_domain_exclude(self):
        d1 = Domain(name="gaming", description="Gaming")
        d1.register_recipe("for_loop", lambda dn, tc, diff: None)
        DomainRegistry.register(d1)
        result = DomainRegistry.find_domain_for_concepts(["for_loop"], exclude=["gaming"])
        assert result is None

    def test_get_random_domain(self):
        d = Domain(name="gaming", description="Gaming")
        DomainRegistry.register(d)
        result = DomainRegistry.get_random_domain()
        assert result is d

    def test_get_random_domain_empty(self):
        result = DomainRegistry.get_random_domain()
        assert result is None

    def test_get_random_domain_exclude(self):
        d = Domain(name="gaming", description="Gaming")
        DomainRegistry.register(d)
        result = DomainRegistry.get_random_domain(exclude=["gaming"])
        assert result is None
