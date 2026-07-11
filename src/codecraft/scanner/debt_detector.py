from __future__ import annotations

import ast
from pathlib import Path

from codecraft.models.debt import DebtItem


class DebtDetector(ast.NodeVisitor):
    def __init__(self, source: str, file_path: Path):
        self.source = source
        self.file_path = file_path
        self.debt_items: list[DebtItem] = []
        self._lines = source.splitlines()

    def detect(self, tree: ast.AST) -> list[DebtItem]:
        self.debt_items = []
        self.visit(tree)
        return self.debt_items

    def _get_line(self, node: ast.AST) -> str:
        if hasattr(node, "lineno") and node.lineno <= len(self._lines):
            return self._lines[node.lineno - 1].strip()
        return ""

    def _get_snippet(self, node: ast.AST, context_lines: int = 1) -> str:
        if hasattr(node, "lineno") and hasattr(node, "end_lineno"):
            start = max(0, node.lineno - 1 - context_lines)
            end = min(len(self._lines), node.end_lineno + context_lines)
            return "\n".join(self._lines[start:end])
        return ""

    def _add_debt(
        self,
        pattern_type: str,
        node: ast.AST,
        suggestion: str,
        alternative: str,
        difficulty: int = 1,
        tier_gap: int = 1,
    ) -> None:
        self.debt_items.append(
            DebtItem(
                file_path=self.file_path,
                pattern_type=pattern_type,
                pattern_location=f"line {getattr(node, 'lineno', '?')}",
                old_snippet=self._get_snippet(node),
                suggestion=suggestion,
                alternative_code=alternative,
                difficulty=difficulty,
                tier_gap=tier_gap,
            )
        )

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._check_mutable_defaults(node)
        self._check_missing_return_annotation(node)
        self.generic_visit(node)

    def _check_mutable_defaults(self, node: ast.FunctionDef) -> None:
        for default in node.args.defaults:
            if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                self._add_debt(
                    "mutable_default_arg",
                    node,
                    "Use None as default and assign inside function",
                    "def func(x=None):\n    if x is None:\n        x = []",
                    difficulty=1,
                    tier_gap=1,
                )

    def _check_missing_return_annotation(self, node: ast.FunctionDef) -> None:
        if node.returns is None and not node.name.startswith("__"):
            has_return = any(
                isinstance(n, ast.Return) for n in ast.walk(node)
            )
            if has_return:
                self._add_debt(
                    "missing_return_annotation",
                    node,
                    "Add return type annotation for clarity",
                    f"def {node.name}(...) -> <type>:",
                    difficulty=1,
                    tier_gap=1,
                )

    def visit_For(self, node: ast.For) -> None:
        self._check_range_len(node)
        self._check_unused_index(node)
        self.generic_visit(node)

    def _check_range_len(self, node: ast.For) -> None:
        if (isinstance(node.iter, ast.Call) and
            isinstance(node.iter.func, ast.Name) and
            node.iter.func.id == "range"):
            if (len(node.iter.args) == 1 and
                isinstance(node.iter.args[0], ast.Call) and
                isinstance(node.iter.args[0].func, ast.Name) and
                node.iter.args[0].func.id == "len"):
                self._add_debt(
                    "range_len",
                    node,
                    "Use enumerate() instead of range(len())",
                    "for i, item in enumerate(iterable):",
                    difficulty=1,
                    tier_gap=1,
                )

    def _check_unused_index(self, node: ast.For) -> None:
        if isinstance(node.target, ast.Name):
            if node.target.id == "_":
                return
            target_name = node.target.id
            used_in_body = any(
                isinstance(n, ast.Name) and n.id == target_name
                for n in ast.walk(node)
                if n is not node.target
            )
            if not used_in_body:
                self._add_debt(
                    "unused_loop_variable",
                    node,
                    "Use _ for unused loop variable",
                    "for _ in iterable:",
                    difficulty=1,
                    tier_gap=0,
                )

    def visit_If(self, node: ast.If) -> None:
        self._check_if_elif_chain(node)
        self._check_single_branch_if(node)
        self.generic_visit(node)

    def _check_if_elif_chain(self, node: ast.If) -> None:
        comparisons = []
        current = node
        while True:
            if isinstance(current.test, ast.Compare):
                left = current.test.left
                if isinstance(left, ast.Name) and len(current.test.ops) == 1:
                    if isinstance(current.test.ops[0], ast.Eq):
                        comparisons.append(left.id)
            if (current.orelse and len(current.orelse) == 1 and
                    isinstance(current.orelse[0], ast.If)):
                current = current.orelse[0]
            else:
                break

        if len(comparisons) >= 3:
            var_name = comparisons[0]
            self._add_debt(
                "if_elif_chain",
                node,
                "Use a dict dispatch table instead of if/elif chain",
                f"dispatch = {{\n    value1: func1,\n    value2: func2,\n}}\nresult = dispatch.get({var_name}, default_func)()",
                difficulty=2,
                tier_gap=1,
            )

    def _check_single_branch_if(self, node: ast.If) -> None:
        if not node.orelse:
            has_return = any(isinstance(n, ast.Return) for n in ast.walk(node))
            has_break = any(isinstance(n, ast.Break) for n in ast.walk(node))
            if not has_return and not has_break:
                body_lines = len(node.body)
                if body_lines <= 2:
                    self._add_debt(
                        "single_line_if_no_else",
                        node,
                        "Consider guard clause or ternary",
                        "if condition: return value  # guard clause",
                        difficulty=1,
                        tier_gap=0,
                    )

    def visit_Try(self, node: ast.Try) -> None:
        self._check_bare_except(node)
        self._check_broad_except(node)
        self.generic_visit(node)

    def _check_bare_except(self, node: ast.Try) -> None:
        for handler in node.handlers:
            if handler.type is None:
                self._add_debt(
                    "bare_except",
                    handler,
                    "Catch specific exceptions instead of bare except",
                    "except SpecificError:",
                    difficulty=1,
                    tier_gap=1,
                )

    def _check_broad_except(self, node: ast.Try) -> None:
        for handler in node.handlers:
            if isinstance(handler.type, ast.Name) and handler.type.id == "Exception":
                self._add_debt(
                    "broad_except",
                    handler,
                    "Catch more specific exceptions",
                    "except (ValueError, TypeError) as e:",
                    difficulty=1,
                    tier_gap=1,
                )

    def visit_With(self, node: ast.With) -> None:
        for item in node.items:
            if isinstance(item.context_expr, ast.Call):
                if isinstance(item.context_expr.func, ast.Attribute):
                    if item.context_expr.func.attr == "open":
                        pass
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        self._check_manual_counter(node)
        self._check_dict_get_pattern(node)
        self._check_list_accumulation(node)
        self.generic_visit(node)

    def _check_manual_counter(self, node: ast.Assign) -> None:
        if (isinstance(node.value, ast.BinOp) and
            isinstance(node.value.op, ast.Add) and
            isinstance(node.value.right, ast.Constant) and
            node.value.right.value == 1):
            self._add_debt(
                "manual_counter",
                node,
                "Use enumerate() for counting or collections.Counter",
                "counter = enumerate(iterable, start=1)",
                difficulty=1,
                tier_gap=1,
            )

    def _check_dict_get_pattern(self, node: ast.Assign) -> None:
        for target in node.targets:
            if isinstance(target, ast.Subscript):
                if isinstance(node.value, ast.Call):
                    pass

    def _check_list_accumulation(self, node: ast.Assign) -> None:
        if (isinstance(node.value, ast.Call) and
            isinstance(node.value.func, ast.Attribute) and
            node.value.func.attr == "append"):
            self._add_debt(
                "list_accumulation",
                node,
                "Consider a list comprehension instead of manual append loop",
                "[expr for x in iterable if condition]",
                difficulty=1,
                tier_gap=1,
            )

    def visit_Expr(self, node: ast.Expr) -> None:
        if isinstance(node.value, ast.Call):
            self._check_print_debug(node.value)
        self.generic_visit(node)

    def _check_print_debug(self, node: ast.Call) -> None:
        if isinstance(node.func, ast.Name) and node.func.id == "print":
            if hasattr(node, "lineno"):
                pass

    def visit_While(self, node: ast.While) -> None:
        self._check_infinite_while(node)
        self.generic_visit(node)

    def _check_infinite_while(self, node: ast.While) -> None:
        if isinstance(node.test, ast.Constant) and node.test.value is True:
            has_break = any(isinstance(n, ast.Break) for n in ast.walk(node))
            if not has_break:
                self._add_debt(
                    "infinite_while_no_break",
                    node,
                    "Add a break condition or use a for loop instead",
                    "while condition:\n    if exit_condition:\n        break",
                    difficulty=2,
                    tier_gap=0,
                )

    def visit_IfExp(self, node: ast.IfExp) -> None:
        self.generic_visit(node)
