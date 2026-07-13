from __future__ import annotations

from codecraft.scanner.multilang.base_ts import TreeSitterParser


class _JavaParser(TreeSitterParser):
    QUERIES = [
        ("method_declaration name: (identifier)", "function_def"),
        ("method_declaration parameters: (formal_parameters)", "args_kwargs"),
        ("method_declaration type: (type_identifier)", "type_hints_basic"),
        ("class_declaration name: (identifier)", "class_basic"),
        ("interface_declaration name: (identifier)", "abstract_base_class"),
        ("enum_declaration name: (identifier)", "enum"),
        ("record_declaration name: (identifier)", "class_basic"),
        ("annotation_type_declaration name: (identifier)", "class_basic"),
        ("if_statement", "if_else"),
        ("for_statement", "for_loop"),
        ("enhanced_for_statement", "for_loop"),
        ("while_statement", "while_loop"),
        ("do_statement", "while_loop"),
        ("switch_expression", "match_case"),
        ("switch_block", "match_case"),
        ("try_statement", "try_except"),
        ("catch_clause", "exception_multiple"),
        ("finally_clause", "exception_multiple"),
        ("return_statement", "return_value"),
        ("import_declaration", "import_basic"),
        ("package_declaration", "import_basic"),
        ("local_variable_declaration", "variable_assignment"),
        ("assignment_expression", "variable_assignment"),
        ("lambda_expression", "lambda"),
        ("binary_expression", "arithmetic"),
        ("unary_expression", "arithmetic"),
        ("array_access", "slicing"),
        ("array_creation_expression", "list_ops"),
        ("object_creation_expression", "class_basic"),
        ("method_invocation", "string_methods"),
        ("field_access", "dict_ops"),
        ("throw_statement", "try_except"),
        ("assert_statement", "try_except"),
        ("synchronized_statement", "context_manager"),
        ("break_statement", "break_continue"),
        ("continue_statement", "break_continue"),
        ("labeled_statement", "break_continue"),
        ("annotation", "decorator_basic"),
        ("generic_type", "type_hints_basic"),
        ("instanceof_expression", "type_hints_basic"),
        ("cast_expression", "type_hints_basic"),
        ("ternary_expression", "if_else"),
        ("try_with_resources_statement", "context_manager"),
    ]


from tree_sitter_java import language as _java_lang_fn  # noqa: E402

_JavaParser.LANGUAGE_FN = _java_lang_fn  # type: ignore[assignment]
JavaParser = _JavaParser
