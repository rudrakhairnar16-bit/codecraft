from __future__ import annotations

from codecraft.scanner.multilang.base_ts import TreeSitterParser


class _RustParser(TreeSitterParser):
    QUERIES = [
        ("function_item name: (identifier)", "function_def"),
        ("function_item parameters: (parameters)", "args_kwargs"),
        ("function_item return_type: (type_identifier)", "type_hints_basic"),
        ("function_item (function_modifiers)", "async_await"),
        ("impl_item", "class_basic"),
        ("struct_item name: (type_identifier)", "class_basic"),
        ("enum_item name: (type_identifier)", "enum"),
        ("trait_item name: (type_identifier)", "abstract_base_class"),
        ("if_expression", "if_else"),
        ("else_clause", "if_else"),
        ("for_expression", "for_loop"),
        ("while_expression", "while_loop"),
        ("loop_expression", "while_loop"),
        ("match_expression", "match_case"),
        ("return_expression", "return_value"),
        ("let_declaration", "variable_assignment"),
        ("mutable_specifier", "variable_assignment"),
        ("use_declaration", "import_basic"),
        ("extern_crate_declaration", "import_basic"),
        ("mod_item", "import_basic"),
        ("closure_expression", "lambda"),
        ("await_expression", "async_await"),
        ("async_block", "async_await"),
        ("binary_expression", "arithmetic"),
        ("unary_expression", "arithmetic"),
        ("index_expression", "slicing"),
        ("tuple_expression", "tuple_unpacking"),
        ("struct_expression", "class_basic"),
        ("field_expression", "dict_ops"),
        ("break_expression", "break_continue"),
        ("continue_expression", "break_continue"),
        ("macro_invocation macro: (identifier) @print", "print_function"),
        ("attribute_item", "decorator_basic"),
        ("where_clause", "type_hints_basic"),
        ("try_expression", "try_except"),
    ]


from tree_sitter_rust import language as _rs_lang_fn  # noqa: E402

_RustParser.LANGUAGE_FN = _rs_lang_fn  # type: ignore[assignment]
RustParser = _RustParser
