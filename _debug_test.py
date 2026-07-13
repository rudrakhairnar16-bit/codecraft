import ast
from codecraft.scanner.concept_extractor import ConceptExtractor

cases = [
    ('walrus', 'if (x := 5) > 0: pass', 'walrus_operator'),
    ('break', 'for i in range(5): break', 'break_continue'),
    ('global', 'x=1\ndef f():\n    global x', 'global_nonlocal'),
    ('set', 's = {1,2,3}', 'set_ops'),
    ('nested class', 'class A:\n    class B:\n        pass', 'class_basic'),
    ('slots', 'class A:\n    __slots__ = \"x\"', 'slots'),
    ('dict literal', 'd = {"a": 1}', 'dict_ops'),
]

for name, source, expected in cases:
    tree = ast.parse(source)
    ex = ConceptExtractor()
    concepts = ex.extract(tree)
    found = expected in concepts
    print(f'{name:15s}: {"OK" if found else "MISSING"} ({expected})')
    if not found:
        print(f'  Got: {sorted(concepts.keys())}')
