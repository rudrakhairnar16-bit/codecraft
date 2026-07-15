from __future__ import annotations

import ast
import os
from pathlib import Path
from unittest.mock import patch

os.environ["NO_COLOR"] = "1"
os.environ["TERM"] = "xterm"

import pytest
from typer.testing import CliRunner

from codecraft.cli.app import app
from codecraft.cli.practice import (
    _analyze_solution,
    _code_uses_concept,
    _compute_complexity,
    _resolve_concept_name,
)
from codecraft.models.challenge import Challenge


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def challenge() -> Challenge:
    return Challenge(
        id="test-1",
        challenge_type="practice",
        title="Test Exercise",
        concept_name="for_loop",
        description="Write a for loop that sums numbers",
        code_snippet="# write your code here",
        expected_solution="total = 0\nfor i in range(10):\n    total += i",
        domain="gaming",
        difficulty=1,
    )


class TestResolveConceptName:
    def test_exact_match(self):
        assert _resolve_concept_name("for_loop") == "for_loop"

    def test_case_insensitive(self):
        assert _resolve_concept_name("For_Loop") == "for_loop"

    def test_substring_match(self):
        assert _resolve_concept_name("loop") == "for_loop"

    def test_no_match(self):
        assert _resolve_concept_name("nonexistent_concept_xyz") == "nonexistent_concept_xyz"


class TestComputeComplexity:
    def test_basic(self):
        tree = ast.parse("x = 1")
        assert _compute_complexity(tree) == 1

    def test_if_statement(self):
        tree = ast.parse("if x > 0:\n    pass")
        assert _compute_complexity(tree) == 2

    def test_loop(self):
        tree = ast.parse("for i in range(10):\n    pass")
        assert _compute_complexity(tree) == 2

    def test_nested_complexity(self):
        tree = ast.parse("""
for i in range(10):
    if i > 5:
        while i > 0:
            pass
""")
        assert _compute_complexity(tree) == 4

    def test_bool_op(self):
        tree = ast.parse("if x > 0 and y > 0 and z > 0:\n    pass")
        assert _compute_complexity(tree) == 4


class TestCodeUsesConcept:
    def test_for_loop_detected(self):
        code = "for i in range(10):\n    print(i)"
        assert _code_uses_concept(code, "for_loop") is True

    def test_function_def_detected(self):
        code = "def foo():\n    return 42"
        assert _code_uses_concept(code, "function_def") is True

    def test_if_else_detected(self):
        code = "if x > 0:\n    print('pos')\nelse:\n    print('neg')"
        assert _code_uses_concept(code, "if_else") is True

    def test_concept_not_present(self):
        code = "x = 1\ny = 2"
        assert _code_uses_concept(code, "for_loop") is False

    def test_syntax_error_returns_false(self):
        code = "def broken(:"
        assert _code_uses_concept(code, "for_loop") is False


class TestAnalyzeSolution:
    def test_valid_code_with_target(self, challenge):
        code = "total = 0\nfor i in range(10):\n    total += i"
        result = _analyze_solution(code, challenge)
        assert result["parses"] is True
        assert result["has_target_concept"] is True
        assert result["score"] >= 50

    def test_valid_code_without_target(self, challenge):
        code = "x = 42\nprint(x)"
        result = _analyze_solution(code, challenge)
        assert result["parses"] is True
        assert result["has_target_concept"] is False
        assert "doesn't seem to use" in result["issues"][0]

    def test_syntax_error(self, challenge):
        code = "def foo(:\n    pass"
        result = _analyze_solution(code, challenge)
        assert result["parses"] is False
        assert "Syntax error" in result["issues"][0]

    def test_empty_code(self, challenge):
        result = _analyze_solution("", challenge)
        assert result["score"] == 30

    def test_score_100(self, challenge):
        code = """def sum_numbers(n: int) -> int:
    total = 0
    for i in range(n):
        total += i
    return total
"""
        result = _analyze_solution(code, challenge)
        assert result["score"] == 100
        assert "Strong solution" in result["suggestion"]

    def test_score_50_to_79(self, challenge):
        code = "x = 1\ny = 2"
        result = _analyze_solution(code, challenge)
        assert result["score"] <= 80
        assert "Keep practicing" in result["suggestion"]

    def test_low_score(self, challenge):
        code = "x = 1"
        result = _analyze_solution(code, challenge)
        assert result["score"] < 50
        assert "Keep practicing" in result["suggestion"]

    def test_high_complexity_issue(self, challenge):
        code = """
if x > 0:
    for i in range(10):
        if i > 5:
            while i > 0:
                if i % 2 == 0:
                    for j in range(5):
                        if j > 2:
                            while j > 0:
                                if j < 5:
                                    for k in range(3):
                                        print(i)
                i -= 1
"""
        result = _analyze_solution(code, challenge)
        assert result["complexity"] > 10
        assert any("Complexity is high" in i for i in result["issues"])

    def test_docstring_strength(self, challenge):
        code = '''def foo():
    """A docstring."""
    pass
'''
        result = _analyze_solution(code, challenge)
        assert "Includes documentation" in result["strengths"]

    def test_function_strength(self, challenge):
        code = "def add(a, b):\n    return a + b"
        result = _analyze_solution(code, challenge)
        assert any("function" in s for s in result["strengths"])

    def test_import_strength(self, challenge):
        code = "import os\nfor i in range(5):\n    print(i)"
        result = _analyze_solution(code, challenge)
        assert "Uses proper imports" in result["strengths"]


class TestPracticeCLI:
    def test_list(self, runner):
        result = runner.invoke(app, ["practice", "list"])
        assert result.exit_code == 0

    def test_list_with_search(self, runner):
        result = runner.invoke(app, ["practice", "list", "loop"])
        assert result.exit_code == 0

    def test_list_no_match(self, runner):
        result = runner.invoke(app, ["practice", "list", "zzz_nonexistent"])
        assert result.exit_code == 0

    def test_path_list_all(self, runner):
        result = runner.invoke(app, ["practice", "path"])
        assert result.exit_code == 0

    def test_path_beginner(self, runner):
        result = runner.invoke(app, ["practice", "path", "beginner"])
        assert result.exit_code == 0

    def test_path_intermediate(self, runner):
        result = runner.invoke(app, ["practice", "path", "intermediate"])
        assert result.exit_code == 0

    def test_path_advanced(self, runner):
        result = runner.invoke(app, ["practice", "path", "advanced"])
        assert result.exit_code == 0

    def test_path_not_found(self, runner):
        result = runner.invoke(app, ["practice", "path", "nonexistent"])
        assert result.exit_code == 0

    def test_path_create(self, runner):
        result = runner.invoke(app, [
            "practice", "path-create", "mypath",
            "--concepts", "for_loop,if_else,function_def",
        ])
        assert result.exit_code == 0

    def test_path_create_invalid_concept(self, runner):
        result = runner.invoke(app, [
            "practice", "path-create", "badpath",
            "--concepts", "for_loop,zzz_not_real",
        ])
        assert result.exit_code != 0

    def test_start_concept_not_found(self, runner):
        result = runner.invoke(app, [
            "practice", "start", "zzz_nonexistent",
        ])
        assert result.exit_code != 0

    def test_start_with_submit(self, runner):
        result = runner.invoke(app, [
            "practice", "start", "for_loop",
            "--domain", "gaming", "--timeout", "10",
        ], input="for i in range(5):\n    print(i)\nsubmit\n")
        assert result.exit_code == 0

    def test_start_with_empty_timeout(self, runner):
        result = runner.invoke(app, [
            "practice", "start", "for_loop",
            "--domain", "gaming", "--timeout", "0",
        ], input="submit\n")
        assert result.exit_code == 0

    def test_path_beginner_step(self, runner):
        result = runner.invoke(app, [
            "practice", "path", "beginner", "--step", "1",
            "--domain", "gaming", "--timeout", "10",
        ], input="print('hello')\nsubmit\n")
        assert result.exit_code == 0

    def test_path_beginner_step_out_of_range(self, runner):
        result = runner.invoke(app, [
            "practice", "path", "beginner", "--step", "99",
        ])
        assert result.exit_code == 0

    def test_start_with_extend(self, runner):
        result = runner.invoke(app, [
            "practice", "start", "for_loop",
            "--domain", "gaming", "--timeout", "10",
        ], input="extend\nfor i in range(5):\n    print(i)\nsubmit\n")
        assert result.exit_code == 0

    def test_start_syntax_error_solution(self, runner):
        result = runner.invoke(app, [
            "practice", "start", "for_loop",
            "--domain", "gaming", "--timeout", "10",
        ], input="def broken(:\n    pass\nsubmit\n")
        assert result.exit_code == 0

    def test_start_multiple_submissions(self, runner):
        result = runner.invoke(app, [
            "practice", "start", "for_loop",
            "--domain", "gaming", "--timeout", "10",
        ], input="x = 1\ny = 2\nsubmit\n")
        assert result.exit_code == 0

    def test_start_different_domain(self, runner):
        result = runner.invoke(app, [
            "practice", "start", "for_loop",
            "--domain", "finance", "--timeout", "10",
        ], input="total = 0\nfor i in range(10):\n    total += i\nsubmit\n")
        assert result.exit_code == 0

    def test_start_concept_alias(self, runner):
        result = runner.invoke(app, [
            "practice", "start", "loop",
            "--domain", "gaming", "--timeout", "10",
        ], input="for i in range(3):\n    print(i)\nsubmit\n")
        assert result.exit_code == 0
