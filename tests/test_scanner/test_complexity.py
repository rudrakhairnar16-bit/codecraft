from __future__ import annotations

import ast

from codecraft.scanner.complexity import ComplexityAnalyzer


def test_simple_code():
    tree = ast.parse("x = 1")
    analyzer = ComplexityAnalyzer()
    result = analyzer.analyze(tree)
    assert result == 1.0


def test_if_statement():
    tree = ast.parse("if x > 0: pass")
    analyzer = ComplexityAnalyzer()
    result = analyzer.analyze(tree)
    assert result >= 2.0


def test_if_elif_else():
    tree = ast.parse("""
if x > 0:
    pass
elif x == 0:
    pass
else:
    pass
""")
    analyzer = ComplexityAnalyzer()
    result = analyzer.analyze(tree)
    assert result >= 3.0


def test_while_loop():
    tree = ast.parse("while True: break")
    analyzer = ComplexityAnalyzer()
    result = analyzer.analyze(tree)
    assert result >= 2.0


def test_for_loop():
    tree = ast.parse("for i in range(10): pass")
    analyzer = ComplexityAnalyzer()
    result = analyzer.analyze(tree)
    assert result >= 2.0


def test_try_except():
    tree = ast.parse("""
try:
    pass
except:
    pass
""")
    analyzer = ComplexityAnalyzer()
    result = analyzer.analyze(tree)
    assert result >= 2.0


def test_boolean_operator():
    tree = ast.parse("if x and y and z: pass")
    analyzer = ComplexityAnalyzer()
    result = analyzer.analyze(tree)
    assert result >= 3.0


def test_match_case():
    tree = ast.parse("""
match value:
    case 1:
        pass
    case 2:
        pass
""")
    analyzer = ComplexityAnalyzer()
    result = analyzer.analyze(tree)
    assert result >= 3.0


def test_nested_conditionals():
    tree = ast.parse("""
if a:
    if b:
        if c:
            pass
""")
    analyzer = ComplexityAnalyzer()
    result = analyzer.analyze(tree)
    assert result >= 4.0


def test_complex_code():
    tree = ast.parse("""
def func(x):
    if x > 0:
        for i in range(x):
            if i % 2 == 0:
                pass
    while True:
        break
    return x
""")
    analyzer = ComplexityAnalyzer()
    result = analyzer.analyze(tree)
    assert result >= 5.0


def test_async_for():
    tree = ast.parse("""
async def fetch():
    async for i in async_gen():
        pass
""")
    analyzer = ComplexityAnalyzer()
    result = analyzer.analyze(tree)
    assert result >= 2.0


def test_or_operator():
    tree = ast.parse("if x or y or z: pass")
    analyzer = ComplexityAnalyzer()
    result = analyzer.analyze(tree)
    assert result >= 3.0
