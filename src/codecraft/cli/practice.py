from __future__ import annotations

import ast

import typer
from rich.panel import Panel
from rich.table import Table

from codecraft.cli.deps import get_repo
from codecraft.engines.remix import RemixEngine
from codecraft.models.concept import ConceptTaxonomy
from codecraft.utils.colors import console

practice_app = typer.Typer(name="practice", no_args_is_help=True)

EXTEND_SECONDS = 120


def _resolve_concept_name(name: str) -> str:
    for cname in list(ConceptTaxonomy._concepts.keys()):
        if name.lower() in cname.lower():
            return cname
    return name


def _read_multiline_input() -> str:
    lines = []
    console.print("[dim]Type your code below. Type [bold]submit[/bold] on a new line when done. Type [bold]extend[/bold] for +2 min.[/dim]")
    console.print("[dim]----------------------------------------[/dim]")
    while True:
        try:
            line = input()
            if line.strip().lower() == "submit":
                break
            if line.strip().lower() == "extend":
                return "EXTEND"
            lines.append(line)
        except (EOFError, KeyboardInterrupt):
            break
    return "\n".join(lines)


@practice_app.command("start")
def start_practice(
    concept: str = typer.Argument(
        ..., help="Concept to practice (e.g. 'list_comprehension', 'dataclass')"
    ),
    domain: str | None = typer.Option(
        None, "--domain", "-d", help="Domain context (e.g. 'finance', 'gaming')"
    ),
    timeout_minutes: int = typer.Option(
        5, "--timeout", "-t", help="Time limit in minutes"
    ),
) -> None:
    repo = get_repo()
    remix = RemixEngine(repo)

    resolved = _resolve_concept_name(concept)
    if resolved != concept:
        console.print(f"[info]Matched concept:[/info] {resolved}")

    challenge = remix.generate_exercise(resolved, domain)
    if challenge is None:
        console.print(f"[error]Could not generate exercise for '{resolved}'[/error]")
        console.print("[warning]Try:[/warning] list_comprehension, dataclass, enumerate, context_manager, f_strings, if_else")
        raise typer.Exit(1)

    console.print(Panel(f"[bold]Practice: {challenge.title}[/bold]", border_style="cyan"))
    console.print(f"[info]Concept:[/info] {challenge.concept_name}")
    console.print(f"[info]Domain:[/info] {challenge.domain}")
    console.print(f"[info]Time limit:[/info] {timeout_minutes} minutes")
    console.print("\n[bold]Problem:[/bold]")
    console.print(challenge.description)
    console.print("\n[bold]Starter code (use or ignore):[/bold]")
    console.print(Panel(challenge.code_snippet, border_style="cyan"))

    total_seconds = timeout_minutes * 60
    solution_code = ""
    time_left = total_seconds
    while time_left > 0:
        console.print(f"\n[info]Time remaining:[/info] {time_left // 60}:{time_left % 60:02d}")
        code = _read_multiline_input()

        if code == "EXTEND":
            time_left += EXTEND_SECONDS
            console.print(f"[success]Time extended! +2 min. Remaining: {time_left // 60}:{time_left % 60:02d}[/success]")
            continue

        solution_code = code
        break

    if not solution_code.strip():
        console.print("[debt]Time's up! Showing analysis with whatever you typed.[/debt]")
        solution_code = "# timeout"

    analysis = _analyze_solution(solution_code, challenge)
    _show_analysis(analysis, challenge, concept=resolved, domain_str=challenge.domain)


def _analyze_solution(code: str, challenge) -> dict:
    result = {
        "parses": False,
        "has_target_concept": False,
        "complexity": 0,
        "lines": 0,
        "issues": [],
        "strengths": [],
        "score": 0,
        "suggestion": "",
    }

    try:
        tree = ast.parse(code)
        result["parses"] = True
        result["lines"] = len(code.strip().splitlines())
        result["complexity"] = _compute_complexity(tree)

        result["has_target_concept"] = _code_uses_concept(code, challenge.concept_name)

        if not result["has_target_concept"]:
            result["issues"].append(f"Solution doesn't seem to use '{challenge.concept_name}'")
        else:
            result["strengths"].append(f"Correctly uses '{challenge.concept_name}'")

        imports = [n for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom))]
        if imports:
            result["strengths"].append("Uses proper imports")

        functions = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
        if functions:
            result["strengths"].append(f"Defines {len(functions)} function(s)")

        docstrings = sum(
            1 for n in ast.walk(tree)
            if isinstance(n, (ast.FunctionDef, ast.ClassDef, ast.Module))
            and ast.get_docstring(n)
        )
        if docstrings:
            result["strengths"].append("Includes documentation")

        if result["complexity"] > 10:
            result["issues"].append(f"Complexity is high ({result['complexity']}). Consider simplifying.")

        score = 0
        if result["parses"]:
            score += 30
        if result["has_target_concept"]:
            score += 35
        if result["strengths"]:
            score += min(len(result["strengths"]) * 10, 20)
        if not result["issues"]:
            score += 15
        result["score"] = min(score, 100)

        if score >= 80:
            result["suggestion"] = "Strong solution! You've mastered this concept."
        elif score >= 50:
            result["suggestion"] = "Good attempt. Review the hints and try again for deeper understanding."
        else:
            result["suggestion"] = "Keep practicing! Focus on the core concept and try breaking down the problem."

    except SyntaxError as e:
        result["issues"].append(f"Syntax error: {e.msg} at line {e.lineno}")
        result["suggestion"] = "Fix the syntax errors first, then focus on the concept."
    except Exception as e:
        result["issues"].append(f"Analysis error: {e}")

    return result


def _compute_complexity(tree: ast.AST) -> int:
    complexity = 1
    for node in ast.walk(tree):
        if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler, ast.FunctionDef)):
            complexity += 1
        if isinstance(node, ast.BoolOp):
            complexity += len(node.values) - 1
    return complexity


def _code_uses_concept(code: str, concept_name: str) -> bool:
    patterns = {
        "list_comprehension": lambda c: "for" in c and "[" in c and "]" in c and " in " in c,
        "dict_comprehension": lambda c: "for" in c and "{" in c and "}" in c and ":" in c and " in " in c,
        "generator_expression": lambda c: "for" in c and "(" in c and ")" in c and " in " in c,
        "context_manager": lambda c: "with " in c,
        "enumerate": lambda c: "enumerate(" in c,
        "zip_function": lambda c: "zip(" in c,
        "dataclass": lambda c: "dataclass" in c or "from dataclasses import" in c,
        "match_case": lambda c: "match " in c and "case " in c,
        "try_except": lambda c: "try:" in c and "except" in c,
        "file_io": lambda c: 'open(' in c or '.read()' in c or '.write(' in c,
        "defaultdict": lambda c: "defaultdict" in c,
        "counter": lambda c: "Counter(" in c or "most_common" in c,
        "lambda": lambda c: "lambda " in c,
        "decorator_basic": lambda c: "@" in c,
        "property_decorator": lambda c: "@property" in c,
        "class_basic": lambda c: "class " in c,
        "function_def": lambda c: "def " in c,
        "type_hints_basic": lambda c: "-> " in c or ": int" in c or ": str" in c,
        "yield_generator": lambda c: "yield " in c,
        "args_kwargs": lambda c: "*args" in c or "**kwargs" in c,
        "f_strings": lambda c: 'f"' in c or "f'" in c,
        "pathlib": lambda c: "Path(" in c or "from pathlib import" in c,
        "async_await": lambda c: "async def" in c or "await " in c,
        "map_filter_reduce": lambda c: "map(" in c or "filter(" in c,
        "slicing": lambda c: "[" in c and ":" in c and "]" in c,
        "string_methods": lambda c: ".split(" in c or ".join(" in c or ".upper(" in c or ".lower(" in c or ".strip(" in c,
        "print_function": lambda c: "print(" in c,
        "input_function": lambda c: "input(" in c,
        "if_else": lambda c: "if " in c and ":" in c,
        "for_loop": lambda c: "for " in c and " in " in c and ":" in c,
        "while_loop": lambda c: "while " in c and ":" in c,
        "variable_assignment": lambda c: "=" in c and "==" not in c,
        "basic_types": lambda c: '"' in c or "'" in c,
        "boolean_ops": lambda c: " and " in c or " or " in c or " not " in c,
        "comparisons": lambda c: "==" in c or "!=" in c or ">=" in c or "<=" in c or ">" in c or "<" in c,
        "arithmetic": lambda c: "+" in c or "-" in c or "*" in c or "/" in c,
        "return_value": lambda c: "return " in c,
        "dict_ops": lambda c: "[" in c and "]" in c and "=" in c,
        "list_ops": lambda c: ".append(" in c or ".extend(" in c or ".insert(" in c or ".remove(" in c or ".pop(" in c,
        "set_ops": lambda c: ".union(" in c or ".intersection(" in c or ".difference(" in c,
        "import_basic": lambda c: "import " in c,
        "tuple_unpacking": lambda c: "," in c and "=" in c and "(" not in c.split("=")[0],
        "exception_chaining": lambda c: "raise " in c and "from " in c,
        "decorator_args": lambda c: "@" in c and "(" in c,
    }
    checker = patterns.get(concept_name)
    if checker:
        return checker(code)
    return concept_name.replace("_", " ") in code.lower()


def _show_analysis(analysis: dict, challenge, concept: str = "", domain_str: str = "") -> None:
    console.print("\n" + "=" * 60)
    console.print(Panel("[bold]Solution Analysis[/bold]", border_style="green"))

    score = analysis["score"]
    if score >= 80:
        color = "strength.high"
        label = "Excellent!"
    elif score >= 50:
        color = "strength.medium"
        label = "Good Effort"
    else:
        color = "strength.low"
        label = "Needs Work"

    console.print(f"Score: [{color}]{score}/100 - {label}[/{color}]")
    console.print(f"Lines: {analysis['lines']}  |  Complexity: {analysis['complexity']}")
    console.print(f"Parses: {'[success]Yes[/success]' if analysis['parses'] else '[debt]No[/debt]'}  |  Uses '{challenge.concept_name}': {'[success]Yes[/success]' if analysis['has_target_concept'] else '[debt]No[/debt]'}")

    if analysis["strengths"]:
        console.print("\n[success]Strengths:[/success]")
        for s in analysis["strengths"]:
            console.print(f"  + {s}")

    if analysis["issues"]:
        console.print("\n[debt]Issues:[/debt]")
        for i in analysis["issues"]:
            console.print(f"  - {i}")

    console.print(f"\n[info]Feedback:[/info] {analysis['suggestion']}")
    console.print(f"\n[warning]New problem:[/warning] codecraft practice start {concept} --domain {domain_str}")


LEARNING_PATHS = {
    "beginner": {
        "title": "Beginner - First Steps in Python",
        "steps": [
            ("print_function", "Print karna seekho - output dena"),
            ("input_function", "User se input lena seekho"),
            ("variable_assignment", "Variables mein data store karna"),
            ("basic_types", "int, str, float - data types samjho"),
            ("string_methods", "Strings ke saath khelo (split, join, upper)"),
            ("f_strings", "f-strings se acchi output likho"),
            ("arithmetic", "Math operations (+, -, *, /)"),
            ("import_basic", "import se modules use karna"),
            ("comparisons", "Values compare karna (==, >, <)"),
            ("boolean_ops", "and/or/not - multiple conditions"),
            ("if_else", "Conditions lagao - if/elif/else"),
            ("for_loop", "Loops - for se iterate karna"),
            ("while_loop", "While loop - condition-based repetition"),
            ("list_ops", "List operations (append, remove, pop)"),
            ("dict_ops", "Dictionary use karna (key-value pairs)"),
            ("tuple_unpacking", "Tuples aur unpacking"),
            ("function_def", "Apne functions banana (def)"),
            ("return_value", "Functions se value return karna"),
            ("file_io", "Files padhna aur likhna (open/read/write)"),
            ("set_ops", "Set operations - unique items, union, intersection"),
        ],
    },
    "intermediate": {
        "title": "Intermediate - Level Up",
        "steps": [
            ("list_comprehension", "List comprehensions - ek line mein loops"),
            ("dict_comprehension", "Dict comprehensions"),
            ("enumerate", "enumerate() - index ke saath loop"),
            ("zip_function", "zip() - do lists ek saath"),
            ("context_manager", "with statement - safe resource handling"),
            ("file_io", "Files padhna aur likhna"),
            ("try_except", "Errors handle karna"),
            ("lambda", "Lambda functions - ek line functions"),
            ("defaultdict", "defaultdict - bina error ke dict access"),
            ("counter", "Counter - frequency count karna"),
            ("dataclass", "Dataclasses - clean data containers"),
            ("pathlib", "Pathlib - filesystem navigation"),
            ("type_hints_basic", "Type hints - code ko clear banana"),
        ],
    },
    "advanced": {
        "title": "Advanced - Master Python",
        "steps": [
            ("decorator_basic", "Decorators - functions modify karna"),
            ("decorator_args", "Decorators with arguments"),
            ("yield_generator", "Generators - memory efficient loops"),
            ("match_case", "Structural pattern matching (3.10+)"),
            ("itertools", "itertools - advanced iteration tools"),
            ("exception_chaining", "Exception chaining - raise ... from"),
            ("custom_exception", "Apni exceptions banana"),
            ("abstract_base_class", "ABCs - interfaces in Python"),
            ("property_decorator", "@property - computed attributes"),
            ("async_await", "Async/await - concurrent programming"),
            ("asyncio_gather", "asyncio.gather - run tasks in parallel"),
        ],
    },
}


@practice_app.command("path")
def show_path(
    path_name: str | None = typer.Argument(
        None, help="Path name: beginner, intermediate, advanced"
    ),
    step_number: int | None = typer.Option(
        None, "--step", "-s", help="Start practice at a specific step number"
    ),
    domain: str = typer.Option(
        "gaming", "--domain", "-d", help="Domain for exercises"
    ),
    timeout_minutes: int = typer.Option(
        10, "--timeout", "-t", help="Time limit in minutes per step"
    ),
) -> None:
    if path_name is None:
        console.print("[title]Available Learning Paths[/title]\n")
        for key, path in LEARNING_PATHS.items():
            console.print(f"  [concept]{key}[/concept] - {path['title']} ({len(path['steps'])} steps)")
        console.print("\n[info]Usage:[/info] codecraft practice path [name]")
        console.print("[info]Example:[/info] codecraft practice path beginner")
        console.print("[info]Start at step:[/info] codecraft practice path beginner --step 3")
        return

    if path_name not in LEARNING_PATHS:
        console.print(f"[error]Path '{path_name}' not found.[/error]")
        console.print(f"[warning]Available:[/warning] {', '.join(LEARNING_PATHS.keys())}")
        return

    path = LEARNING_PATHS[path_name]
    table = Table(title=f"{path['title']} ({len(path['steps'])} steps)")
    table.add_column("#", style="bold")
    table.add_column("Concept", style="concept")
    table.add_column("Description")

    for i, (concept, desc) in enumerate(path["steps"], 1):
        table.add_row(str(i), concept, desc)
    console.print(table)

    if step_number is not None:
        if step_number < 1 or step_number > len(path["steps"]):
            console.print(f"[error]Step {step_number} out of range (1-{len(path['steps'])})[/error]")
            return
        concept, desc = path["steps"][step_number - 1]
        console.print(f"\n[info]Starting Step {step_number}:[/info] [concept]{concept}[/concept]")
        console.print(f"[info]{desc}[/info]")
        console.print(f"[warning]Run:[/warning] codecraft practice start {concept} --domain {domain}")
        start_practice(concept=concept, domain=domain, timeout_minutes=10)


@practice_app.command("list")
def list_concepts(
    search: str | None = typer.Argument(None, help="Search for concepts by name"),
) -> None:
    concepts = ConceptTaxonomy.all()
    if search:
        concepts = [c for c in concepts if search.lower() in c.name.lower() or search.lower() in c.description.lower()]

    if not concepts:
        console.print(f"[warning]No concepts found matching '{search}'[/warning]")
        return

    table = Table(title=f"Available Concepts ({len(concepts)})")
    table.add_column("Name", style="concept")
    table.add_column("Tier")
    table.add_column("Category")
    table.add_column("Description")

    for c in concepts:
        tier_colors = {1: "tier1", 2: "tier2", 3: "tier3", 4: "tier4"}
        table.add_row(
            c.name,
            f"[{tier_colors.get(c.tier.value, 'white')}]Tier {c.tier.value}[/]",
            c.category,
            c.description[:60] + "..." if len(c.description) > 60 else c.description,
        )
    console.print(table)
