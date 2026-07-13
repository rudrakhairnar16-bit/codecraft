from __future__ import annotations

from codecraft.scanner.multilang.base_ts import TreeSitterParser


class _JSParser(TreeSitterParser):
    QUERIES = [
        ("function_declaration name: (identifier)", "function_def"),
        ("function_declaration parameters: (formal_parameters)", "args_kwargs"),
        ("generator_function", "yield_generator"),
        ("arrow_function", "lambda"),
        ("class_declaration name: (identifier)", "class_basic"),
        ("method_definition name: (property_identifier)", "function_def"),
        ("method_definition parameters: (formal_parameters)", "args_kwargs"),
        ("if_statement", "if_else"),
        ("else_clause", "if_else"),
        ("for_statement", "for_loop"),
        ("for_in_statement", "for_loop"),
        ("while_statement", "while_loop"),
        ("do_statement", "while_loop"),
        ("try_statement", "try_except"),
        ("catch_clause", "exception_multiple"),
        ("switch_statement", "match_case"),
        ("return_statement", "return_value"),
        ("import_statement", "import_basic"),
        ("lexical_declaration", "variable_assignment"),
        ("variable_declaration", "variable_assignment"),
        ("await_expression", "async_await"),
        ("ternary_expression", "if_else"),
        ("template_string", "f_strings"),
        ("new_expression", "class_basic"),
        ("throw_statement", "try_except"),
        ("spread_element", "tuple_unpacking"),
        ("binary_expression", "arithmetic"),
        ("unary_expression", "arithmetic"),
        ("array", "list_ops"),
        ("object", "dict_ops"),
        ("member_expression", "dict_ops"),
        ("subscript_expression", "slicing"),
        ("yield_expression", "yield_generator"),
        ("regex", "string_methods"),
        ("break_statement", "break_continue"),
        ("continue_statement", "break_continue"),
        ("labeled_statement", "break_continue"),
        ("pair", "dict_ops"),
        ("property_identifier", "dict_ops"),
        ("comment", "string_methods"),
    ]


class _TSParser(TreeSitterParser):
    QUERIES = [
        ("function_declaration name: (identifier)", "function_def"),
        ("function_declaration parameters: (formal_parameters)", "args_kwargs"),
        ("generator_function", "yield_generator"),
        ("arrow_function", "lambda"),
        ("method_definition name: (property_identifier)", "function_def"),
        ("method_definition parameters: (formal_parameters)", "args_kwargs"),
        ("if_statement", "if_else"),
        ("else_clause", "if_else"),
        ("for_statement", "for_loop"),
        ("for_in_statement", "for_loop"),
        ("while_statement", "while_loop"),
        ("do_statement", "while_loop"),
        ("try_statement", "try_except"),
        ("catch_clause", "exception_multiple"),
        ("switch_statement", "match_case"),
        ("return_statement", "return_value"),
        ("import_statement", "import_basic"),
        ("lexical_declaration", "variable_assignment"),
        ("variable_declaration", "variable_assignment"),
        ("await_expression", "async_await"),
        ("ternary_expression", "if_else"),
        ("template_string", "f_strings"),
        ("new_expression", "class_basic"),
        ("throw_statement", "try_except"),
        ("spread_element", "tuple_unpacking"),
        ("binary_expression", "arithmetic"),
        ("unary_expression", "arithmetic"),
        ("array", "list_ops"),
        ("object", "dict_ops"),
        ("member_expression", "dict_ops"),
        ("subscript_expression", "slicing"),
        ("yield_expression", "yield_generator"),
        ("regex", "string_methods"),
        ("break_statement", "break_continue"),
        ("continue_statement", "break_continue"),
        ("labeled_statement", "break_continue"),
        ("pair", "dict_ops"),
        ("property_identifier", "dict_ops"),
        ("comment", "string_methods"),
    ]


from tree_sitter_javascript import language as _js_lang_fn  # noqa: E402

_JSParser.LANGUAGE_FN = _js_lang_fn  # type: ignore[assignment]

from tree_sitter_typescript import language_typescript as _ts_lang_fn  # noqa: E402

_TSParser.LANGUAGE_FN = _ts_lang_fn  # type: ignore[assignment]

JavaScriptParser = _JSParser
TypeScriptParser = _TSParser
