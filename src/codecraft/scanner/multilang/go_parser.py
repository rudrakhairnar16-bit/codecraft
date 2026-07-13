from __future__ import annotations

from codecraft.scanner.multilang.base_ts import TreeSitterParser


class _GoParser(TreeSitterParser):
    QUERIES = [
        ("function_declaration name: (identifier)", "function_def"),
        ("function_declaration parameters: (parameter_list)", "args_kwargs"),
        ("function_declaration result: (parameter_list)", "type_hints_basic"),
        ("method_declaration name: (field_identifier)", "function_def"),
        ("method_declaration parameters: (parameter_list)", "args_kwargs"),
        ("if_statement", "if_else"),
        ("for_statement", "for_loop"),
        ("expression_switch_statement", "match_case"),
        ("type_switch_statement", "match_case"),
        ("select_statement", "match_case"),
        ("return_statement", "return_value"),
        ("defer_statement", "context_manager"),
        ("go_statement", "async_await"),
        ("channel_type", "async_await"),
        ("send_statement", "async_await"),
        ("receive_statement", "async_await"),
        ("import_declaration", "import_basic"),
        ("import_spec", "import_basic"),
        ("short_var_declaration", "variable_assignment"),
        ("var_declaration", "variable_assignment"),
        ("assignment_statement", "variable_assignment"),
        ("const_declaration", "variable_assignment"),
        ("type_declaration", "class_basic"),
        ("struct_type", "class_basic"),
        ("interface_type", "abstract_base_class"),
        ("type_assertion_expression", "type_hints_basic"),
        ("type_conversion_expression", "type_hints_basic"),
        ("binary_expression", "arithmetic"),
        ("index_expression", "slicing"),
        ("slice_expression", "slicing"),
        ("composite_literal type: (struct_type)", "class_basic"),
        ("keyed_element", "dict_ops"),
        ("func_literal", "lambda"),
        ("break_statement", "break_continue"),
        ("continue_statement", "break_continue"),
        ("goto_statement", "break_continue"),
        ("call_expression function: (identifier) @fn", "try_except"),
    ]


from tree_sitter_go import language as _go_lang_fn  # noqa: E402

_GoParser.LANGUAGE_FN = _go_lang_fn  # type: ignore[assignment]
GoParser = _GoParser
