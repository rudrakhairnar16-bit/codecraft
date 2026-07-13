from __future__ import annotations

import ast

import pytest

from codecraft.engines.templates import DomainData, EXERCISE_TEMPLATES, _generate_code_stub


def _mk_domain(domain_name: str = "general") -> DomainData:
    return DomainData(
        domain_name=domain_name,
        description=f"{domain_name} context",
        nouns=["item", "value", "record", "data"],
        verbs=["process", "compute", "transform", "analyze"],
        adjectives=["fast", "slow", "large", "small"],
        sample_filename="sample.txt",
    )


class TestTemplateRegistry:
    def test_all_templates_have_stubs(self):
        for concept_name in EXERCISE_TEMPLATES:
            d = _mk_domain()
            code = _generate_code_stub(d, concept_name)
            assert code is not None, f"Missing stub for {concept_name}"
            assert len(code) > 0

    def test_all_stubs_generate_valid_python(self):
        for concept_name in EXERCISE_TEMPLATES:
            d = _mk_domain()
            code = _generate_code_stub(d, concept_name)
            try:
                ast.parse(code)
            except SyntaxError as e:
                pytest.fail(f"Invalid Python for {concept_name}: {e}")

    def test_stubs_have_placeholder(self):
        skip = {"print_function", "input_function", "basic_types", "import_basic", "string_methods", "set_ops", "boolean_ops"}
        for concept_name in EXERCISE_TEMPLATES:
            if concept_name in skip:
                continue
            d = _mk_domain()
            code = _generate_code_stub(d, concept_name)
            assert "TODO" in code or "pass" in code or "..." in code or "# Write" in code, \
                f"No placeholder in stub for {concept_name}"

    def test_domain_replacement(self):
        d = _mk_domain("finance")
        code = _generate_code_stub(d, "for_loop")
        assert code is not None and len(code) > 0


class TestSpecificTemplates:
    def test_function_def_template(self):
        code = _generate_code_stub(_mk_domain(), "function_def")
        assert "def " in code

    def test_for_loop_template(self):
        code = _generate_code_stub(_mk_domain(), "for_loop")
        assert "for " in code

    def test_class_basic_template(self):
        code = _generate_code_stub(_mk_domain(), "class_basic")
        assert "class " in code

    def test_if_else_template(self):
        code = _generate_code_stub(_mk_domain(), "if_else")
        assert "TODO" in code or "if" in code

    def test_list_comprehension_template(self):
        code = _generate_code_stub(_mk_domain(), "list_comprehension")
        assert code is not None

    def test_try_except_template(self):
        code = _generate_code_stub(_mk_domain(), "try_except")
        assert code is not None

    def test_generator_template(self):
        code = _generate_code_stub(_mk_domain(), "yield_generator")
        assert code is not None

    def test_async_template(self):
        code = _generate_code_stub(_mk_domain(), "async_await")
        assert code is not None

    def test_empty_domain_fallback(self):
        code = _generate_code_stub(_mk_domain("unknown_domain"), "for_loop")
        assert code is not None
