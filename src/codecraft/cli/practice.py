from __future__ import annotations

import ast
import threading
import time
from datetime import datetime

import typer
from rich.panel import Panel
from rich.table import Table

from codecraft.cli.deps import get_repo
from codecraft.engines.remix import RemixEngine
from codecraft.models.challenge import ChallengeResult
from codecraft.models.concept import ConceptTaxonomy
from codecraft.scanner.concept_extractor import ConceptExtractor
from codecraft.utils.colors import console

practice_app = typer.Typer(name="practice", no_args_is_help=True)

EXTEND_SECONDS = 120


def _resolve_concept_name(name: str) -> str:
    for cname in list(ConceptTaxonomy._concepts.keys()):
        if name.lower() in cname.lower():
            return cname
    return name


def _read_multiline_input(timer_expired: threading.Event) -> str:
    lines = []
    console.print("[dim]Type your code below. Type [bold]submit[/bold] on a new line when done. Type [bold]extend[/bold] for +2 min.[/dim]")
    console.print("[dim]----------------------------------------[/dim]")
    while not timer_expired.is_set():
        try:
            line = input()
            if line.strip().lower() == "submit":
                break
            if line.strip().lower() == "extend":
                return "EXTEND"
            lines.append(line)
        except (EOFError, KeyboardInterrupt):
            break
    if timer_expired.is_set() and not lines:
        return ""
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
    difficulty: int = typer.Option(
        1, "--difficulty", "-D", help="Difficulty level (1-5)"
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
        next_steps = _get_beginner_concepts()
        console.print(f"[warning]Try a beginner concept:[/warning] {', '.join(next_steps[:5])}")
        raise typer.Exit(1)

    console.print(Panel(f"[bold]Practice: {challenge.title}[/bold]", border_style="cyan"))
    console.print(f"[info]Concept:[/info] {challenge.concept_name}")
    console.print(f"[info]Domain:[/info] {challenge.domain}")
    console.print(f"[info]Time limit:[/info] {timeout_minutes} minutes")
    console.print(f"[info]Difficulty:[/info] {difficulty}/5")
    console.print("\n[bold]Problem:[/bold]")
    console.print(challenge.description)
    console.print("\n[bold]Starter code (use or ignore):[/bold]")
    console.print(Panel(challenge.code_snippet, border_style="cyan"))

    total_seconds = timeout_minutes * 60
    timer_expired = threading.Event()
    timer = threading.Timer(total_seconds, timer_expired.set)
    timer.daemon = True
    timer.start()

    start_time = time.time()
    solution_code = ""
    time_left = total_seconds

    while time_left > 0 and not timer_expired.is_set():
        mins, secs = divmod(time_left, 60)
        console.print(f"\n[info]Time remaining:[/info] {mins}:{secs:02d}")
        code = _read_multiline_input(timer_expired)

        if code == "EXTEND":
            time_left += EXTEND_SECONDS
            total_seconds += EXTEND_SECONDS
            timer.cancel()
            timer = threading.Timer(time_left, timer_expired.set)
            timer.daemon = True
            timer.start()
            mins, secs = divmod(time_left, 60)
            console.print(f"[success]Time extended! +2 min. Remaining: {mins}:{secs:02d}[/success]")
            continue

        solution_code = code
        break

    timer.cancel()
    elapsed = int(time.time() - start_time)

    if not solution_code.strip():
        console.print("[debt]Time's up! Showing analysis with whatever you typed.[/debt]")
        solution_code = "# timeout"

    analysis = _analyze_solution(solution_code, challenge)
    _show_analysis(analysis, challenge, concept=resolved, domain_str=challenge.domain)

    result = ChallengeResult(
        challenge_id=challenge.id,
        challenge_type="practice",
        concept_name=resolved,
        correct=analysis["score"] >= 70,
        hints_used=0,
        time_taken_seconds=elapsed,
        domain=challenge.domain,
    )
    repo.insert_challenge_result(result)

    _display_streak(repo)


def _get_beginner_concepts() -> list[str]:
    from codecraft.models.concept import ConceptTaxonomy
    return [c.name for c in ConceptTaxonomy.by_tier(1)][:8]


def _display_streak(repo) -> None:
    streak = repo.get_streak_data()
    if streak["current_streak"] > 1:
        console.print(f"[success]Streak: {streak['current_streak']} days![/success]")


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
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return False
    ce = ConceptExtractor()
    concepts = ce.extract(tree)
    return concept_name in concepts


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


def _load_custom_paths() -> dict:
    paths = {}
    try:
        from codecraft.cli.deps import get_repo
        repo = get_repo()
        import json
        raw = repo.get_setting("custom_paths", "{}")
        parsed = json.loads(raw)
        for name, data in parsed.items():
            paths[name] = {
                "title": data.get("title", f"Custom: {name}"),
                "steps": data.get("steps", []),
            }
    except Exception:
        pass
    return paths


try:
    LEARNING_PATHS.update(_load_custom_paths())
except Exception:
    pass


@practice_app.command("path-create")
def create_path(
    name: str = typer.Argument(..., help="Learning path name"),
    concepts: str = typer.Option(..., "--concepts", "-c", help="Comma-separated concept names"),
) -> None:
    repo = get_repo()
    concept_list = [c.strip() for c in concepts.split(",")]
    valid = []
    invalid = []
    for c in concept_list:
        resolved = _resolve_concept_name(c)
        if ConceptTaxonomy.get(resolved):
            valid.append(resolved)
        else:
            invalid.append(c)
    if invalid:
        console.print(f"[error]Unknown concepts: {', '.join(invalid)}[/error]")
        raise typer.Exit(1)

    import json
    existing = repo.get_setting("custom_paths", "{}")
    paths = json.loads(existing)
    paths[name] = {"title": f"Custom: {name}", "steps": [(c, "") for c in valid]}
    repo.set_setting("custom_paths", json.dumps(paths))

    LEARNING_PATHS[name] = {
        "title": f"Custom: {name}",
        "steps": [(c, "") for c in valid],
    }
    console.print(f"[success]Created learning path '{name}' with {len(valid)} concepts[/success]")


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
