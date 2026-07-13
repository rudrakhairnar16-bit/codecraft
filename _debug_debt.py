import ast
from pathlib import Path
from codecraft.scanner.debt_detector import DebtDetector

sources = {
    'manual_counter': 'i = 0\nwhile i < 10:\n    i += 1',
    'unused_loop_variable': 'for _ in range(10):\n    print("hello")',
    'list_accumulation': 'result = []\nfor i in range(10):\n    result.append(i * 2)',
    'debug_print': 'def f():\n    print("DEBUG: test")',
    'long_function': 'def f():\n' + '    pass\n' * 25,
    'too_many_params': 'def f(a, b, c, d, e, f, g): pass',
    'nested_loops': 'for i in range(10):\n    for j in range(10):\n        for k in range(10):\n            pass',
    'same_condition': 'if x > 0:\n    pass\nif x > 0:\n    pass',
    'empty_except': 'try:\n    risky()\nexcept ValueError:\n    pass',
    'no_error_message': 'raise ValueError("")',
    'long_param_line': 'def f(a, b, c, d, e, f, g, h, i, j, k, l, m, n): pass',
    'bare_except': 'try:\n    risky()\nexcept:\n    pass',
    'mutable_default_arg': 'def f(items=[]):\n    items.append(1)',
}

for name, source in sources.items():
    tree = ast.parse(source)
    detector = DebtDetector(source, Path('<test>'))
    items = detector.detect(tree)
    patterns = [d.pattern_type for d in items]
    found = name in patterns
    print(f'{name:25s}: {"OK" if found else "MISSING"} -> {patterns}')
