from __future__ import annotations

import ast


class ComplexityAnalyzer(ast.NodeVisitor):
    def __init__(self) -> None:
        self.complexity: int = 1
        self._conditions: set[int] = set()

    def analyze(self, tree: ast.AST) -> float:
        self.complexity = 1
        self._conditions = set()
        self.visit(tree)
        return float(self.complexity)

    def _count(self, node: ast.AST) -> None:
        node_id = id(node)
        if node_id not in self._conditions:
            self._conditions.add(node_id)
            self.complexity += 1

    def visit_If(self, node: ast.If) -> None:
        self._count(node)
        self.generic_visit(node)

    def visit_While(self, node: ast.While) -> None:
        self._count(node)
        self.generic_visit(node)

    def visit_For(self, node: ast.For) -> None:
        self._count(node)
        self.generic_visit(node)

    def visit_AsyncFor(self, node: ast.AsyncFor) -> None:
        self._count(node)
        self.generic_visit(node)

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
        self._count(node)
        self.generic_visit(node)

    def visit_BoolOp(self, node: ast.BoolOp) -> None:
        if isinstance(node.op, ast.And):
            for _ in node.values[1:]:
                self._count(node)
        elif isinstance(node.op, ast.Or):
            for _ in node.values[1:]:
                self._count(node)
        self.generic_visit(node)

    def visit_Match(self, node: ast.Match) -> None:
        for case in node.cases:
            self._count(case)
        self.generic_visit(node)
