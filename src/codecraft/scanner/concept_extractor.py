from __future__ import annotations

import ast

from codecraft.models.file import FileConcept


class ConceptExtractor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.concepts: dict[str, int] = {}
        self._imported_names: set[str] = set()
        self._imported_modules: set[str] = set()
        self._has_decorator = False
        self._decorator_count = 0
        self._class_count = 0
        self._function_count = 0
        self._async_count = 0
        self._yield_count = 0
        self._if_elif_count = 0
        self._try_count = 0
        self._except_count = 0
        self._with_count = 0
        self._lambda_count = 0
        self._comprehension_count = 0
        self._current_function: str | None = None
        self._function_names: set[str] = set()
        self._class_method_names: set[str] = set()
        self._class_name: str | None = None

    def extract(self, tree: ast.AST) -> dict[str, FileConcept]:
        self.concepts = {}
        self._imported_names = set()
        self._imported_modules = set()
        self._has_decorator = False
        self._decorator_count = 0
        self._class_count = 0
        self._function_count = 0
        self._async_count = 0
        self._yield_count = 0
        self._if_elif_count = 0
        self._try_count = 0
        self._except_count = 0
        self._with_count = 0
        self._lambda_count = 0
        self._comprehension_count = 0
        self._current_function = None
        self._function_names = set()
        self._class_method_names = set()
        self._class_name = None

        self.visit(tree)
        self._apply_heuristics()
        self._check_stdlib_usage()

        return {
            name: FileConcept(concept_name=name, occurrences=count)
            for name, count in self.concepts.items()
        }

    def _add(self, name: str, count: int = 1) -> None:
        self.concepts[name] = self.concepts.get(name, 0) + count

    def _apply_heuristics(self) -> None:
        if self._comprehension_count >= 2:
            for c in ["list_comprehension", "dict_comprehension", "generator_expression"]:
                pass

        if self._if_elif_count >= 1:
            self._add("if_else")
        if self._try_count > 0:
            self._add("try_except", self._try_count)
            if self._except_count >= 2:
                self._add("exception_multiple")
        if self._with_count > 0:
            self._add("context_manager", self._with_count)
        if self._lambda_count > 0:
            self._add("lambda", self._lambda_count)
        if self._function_count > 0:
            self._add("function_def", self._function_count)
        if self._class_count > 0:
            self._add("class_basic", self._class_count)
        if self._decorator_count > 0:
            self._add("decorator_basic", self._decorator_count)
        if self._async_count > 0:
            self._add("async_await", self._async_count)

    def _check_stdlib_usage(self) -> None:
        mapping = {
            "collections": {"defaultdict": "defaultdict", "Counter": "counter",
                            "deque": "deque"},
            "functools": {"lru_cache": "lru_cache", "partial": "functools_partial",
                          "singledispatch": "singledispatch"},
            "itertools": {},
            "abc": {"ABC": "abstract_base_class", "abstractmethod": "abstract_base_class"},
            "enum": {"Enum": "enum"},
            "heapq": {},
            "pathlib": {},
            "contextlib": {},
            "typing": {},
            "dataclasses": {"dataclass": "dataclass"},
            "asyncio": {},
            "weakref": {},
            "contextvars": {},
            "ctypes": {},
        }
        for mod, names in mapping.items():
            if mod in self._imported_modules:
                if mod == "itertools":
                    self._add("itertools")
                elif mod == "heapq":
                    self._add("heapq")
                elif mod == "pathlib":
                    self._add("pathlib")
                elif mod == "contextlib":
                    self._add("contextlib")
                elif mod == "contextvars":
                    self._add("context_var")
                elif mod == "ctypes":
                    self._add("cython_ctypes")
                elif mod == "asyncio":
                    self._add("asyncio_gather")
                    self._add("async_await")
                elif mod == "weakref":
                    self._add("weakref")
                elif mod == "typing":
                    self._add("type_hints_basic")
                    if "NamedTuple" in self._imported_names:
                        self._add("named_tuple")
                    if "TypedDict" in self._imported_names:
                        self._add("typed_dict")
                elif mod == "enum":
                    self._add("enum")
                else:
                    for name, concept in names.items():
                        if name in self._imported_names:
                            self._add(concept)

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            self._imported_modules.add(alias.name.split(".")[0])
            if alias.asname:
                self._imported_names.add(alias.asname)
            else:
                self._imported_names.add(alias.name.split(".")[0])
        self._add("import_basic")
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if node.module:
            base = node.module.split(".")[0]
            self._imported_modules.add(base)
            for alias in node.names:
                self._imported_names.add(alias.name)
        self._add("import_basic")
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._function_count += 1
        self._function_names.add(node.name)
        if node.decorator_list:
            self._decorator_count += len(node.decorator_list)
            for dec in node.decorator_list:
                if isinstance(dec, ast.Call):
                    self._add("decorator_args")
                elif isinstance(dec, ast.Name):
                    if dec.id == "property":
                        self._add("property_decorator")
                    elif dec.id == "staticmethod":
                        self._add("static_class_method")
                    elif dec.id == "classmethod":
                        self._add("static_class_method")
        if node.args.vararg:
            self._add("args_kwargs")
        if node.args.kwarg:
            self._add("args_kwargs")
        if node.returns:
            self._add("type_hints_basic")
        if self._class_name is not None:
            self._class_method_names.add(node.name)
        old_fn = self._current_function
        self._current_function = node.name
        self.generic_visit(node)
        self._current_function = old_fn

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._async_count += 1
        self._function_count += 1
        self._function_names.add(node.name)
        if node.decorator_list:
            self._decorator_count += len(node.decorator_list)
        old_fn = self._current_function
        self._current_function = node.name
        self.generic_visit(node)
        self._current_function = old_fn

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self._class_count += 1
        bases = [b for b in node.bases if isinstance(b, ast.Name)]
        base_names = {b.id for b in bases}
        if "ABC" in self._imported_names and any(
            b in base_names for b in ["ABC"]
        ):
            self._add("abstract_base_class")
        if any(b in base_names for b in ["Exception", "ValueError", "TypeError", "RuntimeError"]):
            self._add("custom_exception")
        if "NamedTuple" in self._imported_names and any(b in base_names for b in ["NamedTuple"]):
            self._add("named_tuple")
        if "TypedDict" in self._imported_names and any(b in base_names for b in ["TypedDict"]):
            self._add("typed_dict")
        if any(isinstance(k, ast.keyword) and k.arg == "metaclass" for k in node.keywords):
            self._add("metaclass")
        if node.name.endswith("Mixin") or node.name.startswith("Mixin"):
            self._add("mixin")
        old_cn = self._class_name
        self._class_name = node.name
        old_methods = self._class_method_names
        self._class_method_names = set()
        self.generic_visit(node)
        if "__call__" in self._class_method_names:
            self._add("callable")
        if "__enter__" in self._class_method_names or "__exit__" in self._class_method_names:
            self._add("enter_exit")
        if "__get__" in self._class_method_names or "__set__" in self._class_method_names:
            self._add("descriptor")
        if "__getattr__" in self._class_method_names or "__getattribute__" in self._class_method_names:
            self._add("getattr_protocol")
        if "__init_subclass__" in self._class_method_names:
            self._add("init_subclass")
        if "__aenter__" in self._class_method_names or "__aexit__" in self._class_method_names:
            self._add("async_context")
        if "__aiter__" in self._class_method_names or "__anext__" in self._class_method_names:
            self._add("async_iterator")
        dunders = {"__add__", "__sub__", "__mul__", "__eq__", "__lt__", "__gt__",
                   "__len__", "__getitem__", "__setitem__", "__contains__",
                   "__str__", "__repr__", "__iter__", "__next__"}
        if self._class_method_names & dunders:
            self._add("operator_overloading")
        self._class_name = old_cn
        self._class_method_names = old_methods

    def visit_Return(self, node: ast.Return) -> None:
        self._add("return_value")
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        self._add("variable_assignment")
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == "__slots__":
                self._add("slots")
        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        self._add("variable_assignment")
        self._add("type_hints_basic")
        self.generic_visit(node)

    def visit_If(self, node: ast.If) -> None:
        self._if_elif_count += 1
        counter = 1
        current = node
        while current.orelse and len(current.orelse) == 1 and isinstance(current.orelse[0], ast.If):
            counter += 1
            current = current.orelse[0]
        self._if_elif_count += counter - 1
        self.generic_visit(node)

    def visit_For(self, node: ast.For) -> None:
        self._add("for_loop")
        if isinstance(node.iter, ast.Call):
            if isinstance(node.iter.func, ast.Name):
                if node.iter.func.id == "enumerate":
                    self._add("enumerate")
                elif node.iter.func.id == "zip":
                    self._add("zip_function")
                elif node.iter.func.id == "range":
                    pass
            elif isinstance(node.iter.func, ast.Attribute):
                if node.iter.func.attr == "items":
                    self._add("dict_ops")
        self.generic_visit(node)

    def visit_AsyncFor(self, node: ast.AsyncFor) -> None:
        self._add("async_generator")
        self.generic_visit(node)

    def visit_While(self, node: ast.While) -> None:
        self._add("while_loop")
        self.generic_visit(node)

    def visit_With(self, node: ast.With) -> None:
        self._with_count += 1
        self.generic_visit(node)

    def visit_Try(self, node: ast.Try) -> None:
        self._try_count += 1
        self._except_count += len(node.handlers)
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        func = node.func
        if isinstance(func, ast.Name):
            if func.id == "print":
                self._add("print_function")
            elif func.id == "input":
                self._add("input_function")
            elif func.id == "map":
                self._add("map_filter_reduce")
            elif func.id == "filter":
                self._add("map_filter_reduce")
            elif func.id == "reduce":
                self._add("map_filter_reduce")
            elif func.id == "enumerate":
                self._add("enumerate")
            elif func.id == "zip":
                self._add("zip_function")
            elif func.id == "open":
                self._add("file_io")
            elif func.id == "super":
                self._add("class_basic")
            elif func.id == "isinstance":
                self._add("type_hints_basic")
        elif isinstance(func, ast.Attribute):
            if func.attr in ("split", "join", "upper", "lower", "strip", "replace",
                             "startswith", "endswith", "find", "format"):
                self._add("string_methods")
            elif func.attr in ("append", "extend", "insert", "remove", "pop", "sort"):
                self._add("list_ops")
            elif func.attr in ("get", "setdefault", "keys", "values", "items", "update"):
                self._add("dict_ops")
            elif func.attr == "format":
                self._add("str_format")
            elif func.attr in ("union", "intersection", "difference", "symmetric_difference"):
                self._add("set_ops")
        if isinstance(func, ast.Name) and self._current_function and func.id == self._current_function:
            self._add("recursion")
        self.generic_visit(node)

    def visit_ListComp(self, node: ast.ListComp) -> None:
        self._comprehension_count += 1
        self._add("list_comprehension")
        self.generic_visit(node)

    def visit_DictComp(self, node: ast.DictComp) -> None:
        self._comprehension_count += 1
        self._add("dict_comprehension")
        self.generic_visit(node)

    def visit_SetComp(self, node: ast.SetComp) -> None:
        self._add("set_ops")
        self.generic_visit(node)

    def visit_GeneratorExp(self, node: ast.GeneratorExp) -> None:
        self._comprehension_count += 1
        self._add("generator_expression")
        self.generic_visit(node)

    def visit_Lambda(self, node: ast.Lambda) -> None:
        self._lambda_count += 1
        self.generic_visit(node)

    def visit_Yield(self, node: ast.Yield) -> None:
        self._yield_count += 1
        self._add("yield_generator")
        self.generic_visit(node)

    def visit_YieldFrom(self, node: ast.YieldFrom) -> None:
        self._yield_count += 1
        self._add("yield_from")
        self.generic_visit(node)

    def visit_Match(self, node: ast.Match) -> None:
        self._add("match_case")
        self.generic_visit(node)

    def visit_NamedExpr(self, node: ast.NamedExpr) -> None:
        self._add("walrus_operator")
        self.generic_visit(node)

    def visit_Break(self, node: ast.Break) -> None:
        self._add("break_continue")
        self.generic_visit(node)

    def visit_Continue(self, node: ast.Continue) -> None:
        self._add("break_continue")
        self.generic_visit(node)

    def visit_Global(self, node: ast.Global) -> None:
        self._add("global_nonlocal")
        self.generic_visit(node)

    def visit_Nonlocal(self, node: ast.Nonlocal) -> None:
        self._add("global_nonlocal")
        self.generic_visit(node)

    def visit_Set(self, node: ast.Set) -> None:
        self._add("set_ops")
        self.generic_visit(node)

    def visit_Dict(self, node: ast.Dict) -> None:
        self._add("dict_ops")
        self.generic_visit(node)

    def visit_AugAssign(self, node: ast.AugAssign) -> None:
        self._add("variable_assignment")
        self.generic_visit(node)

    def visit_BinOp(self, node: ast.BinOp) -> None:
        self._add("arithmetic")
        self.generic_visit(node)

    def visit_Compare(self, node: ast.Compare) -> None:
        self._add("comparisons")
        self.generic_visit(node)

    def visit_BoolOp(self, node: ast.BoolOp) -> None:
        self._add("boolean_ops")
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        if node.attr == "__slots__":
            self._add("slots")
        self.generic_visit(node)

    def visit_Subscript(self, node: ast.Subscript) -> None:
        if isinstance(node.slice, ast.Slice):
            self._add("slicing")
        self.generic_visit(node)

    def visit_Delete(self, node: ast.Delete) -> None:
        self.generic_visit(node)

    if hasattr(ast, "TypeAlias"):
        def visit_TypeAlias(self, node: ast.TypeAlias) -> None:  # noqa: N802
            self._add("type_alias")
            self.generic_visit(node)

    if hasattr(ast, "TryStar"):
        def visit_TryStar(self, node: ast.TryStar) -> None:  # noqa: N802
            self._add("try_except_star")
            self._try_count += 1
            self._except_count += len(node.handlers)
            self.generic_visit(node)

    def visit_Tuple(self, node: ast.Tuple) -> None:
        if isinstance(node.ctx, ast.Store):
            self._add("tuple_unpacking")
        self.generic_visit(node)

    def visit_Starred(self, node: ast.Starred) -> None:
        self._add("tuple_unpacking")
        self.generic_visit(node)

    def visit_JoinedStr(self, node: ast.JoinedStr) -> None:
        self._add("f_strings")
        self.generic_visit(node)

    def visit_Raise(self, node: ast.Raise) -> None:
        if node.cause:
            self._add("exception_chaining")
        self.generic_visit(node)

    def visit_Constant(self, node: ast.Constant) -> None:
        if isinstance(node.value, (int, float, str, bool, type(None))):
            self._add("basic_types")
        self.generic_visit(node)
