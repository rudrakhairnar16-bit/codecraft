from __future__ import annotations

import ast
from typing import Dict, List, Set


class ImportAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.imports: List[str] = []
        self.modules: Set[str] = set()
        self.names: Set[str] = set()
        self.stdlib_modules: Set[str] = {
            "abc", "ast", "asyncio", "base64", "collections", "contextlib",
            "copy", "csv", "datetime", "decimal", "enum", "functools",
            "glob", "hashlib", "heapq", "html", "http", "importlib",
            "inspect", "io", "itertools", "json", "logging", "math",
            "multiprocessing", "operator", "os", "pathlib", "pickle",
            "platform", "pprint", "queue", "random", "re", "secrets",
            "shutil", "signal", "socket", "sqlite3", "string", "struct",
            "subprocess", "sys", "tempfile", "textwrap", "threading",
            "time", "traceback", "typing", "unittest", "urllib", "uuid",
            "warnings", "weakref", "xml", "zipfile",
        }
        self.third_party: Set[str] = set()

    def analyze(self, tree: ast.AST) -> dict:
        self.imports = []
        self.modules = set()
        self.names = set()
        self.third_party = set()
        self.visit(tree)
        return {
            "imports": self.imports,
            "modules": sorted(self.modules),
            "names": sorted(self.names),
            "stdlib_modules": sorted(self.modules & self.stdlib_modules),
            "third_party": sorted(self.third_party),
        }

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            import_str = f"import {alias.name}"
            if alias.asname:
                import_str += f" as {alias.asname}"
            self.imports.append(import_str)
            base = alias.name.split(".")[0]
            self.modules.add(base)
            if base not in self.stdlib_modules:
                self.third_party.add(base)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if node.module:
            for alias in node.names:
                import_str = f"from {node.module} import {alias.name}"
                if alias.asname:
                    import_str += f" as {alias.asname}"
                self.imports.append(import_str)
                self.names.add(alias.name)
            base = node.module.split(".")[0]
            self.modules.add(base)
            if base not in self.stdlib_modules:
                self.third_party.add(base)
        self.generic_visit(node)
