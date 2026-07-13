from __future__ import annotations

from pathlib import Path

import typer

from codecraft.utils.colors import console

PRE_COMMIT_CONFIG = """
repos:
  - repo: https://github.com/rudrakhairnar16-bit/codecraft
    rev: v0.1.0
    hooks:
      - id: codecraft-scan
        name: CodeCraft Scan
        description: Scan Python files for concept usage and learning debt
        entry: codecraft scan dir
        language: python
        types: [python]
        pass_filenames: false
        stages: [pre-commit]
"""

PRE_COMMIT_HOOK = """#!/usr/bin/env python3
\"\"\"CodeCraft pre-commit hook — scan Python files before commit.\"\"\"
import subprocess
import sys

def main():
    result = subprocess.run(
        ["codecraft", "scan", "dir", "."],
        capture_output=True, text=True,
    )
    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    sys.exit(result.returncode)

if __name__ == "__main__":
    main()
"""

precommit_app = typer.Typer(name="precommit", no_args_is_help=True,
                            help="Generate pre-commit hook configuration")


@precommit_app.command("install")
def precommit_install(
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing config"),
) -> None:
    hook_dir = Path(".hooks")
    config_path = Path(".pre-commit-config.yaml")
    hook_path = hook_dir / "codecraft-scan.py"

    if config_path.exists() and not force:
        console.print("[warning].pre-commit-config.yaml already exists. Use --force to overwrite.[/warning]")
    else:
        config_path.write_text(PRE_COMMIT_CONFIG.strip())
        console.print(f"[success]Created {config_path}[/success]")

    hook_dir.mkdir(exist_ok=True)
    if hook_path.exists() and not force:
        console.print(f"[warning]{hook_path} already exists. Use --force to overwrite.[/warning]")
    else:
        hook_path.write_text(PRE_COMMIT_HOOK.strip())
        hook_path.chmod(0o755)
        console.print(f"[success]Created {hook_path}[/success]")

    console.print("\n[info]Next:[/info]")
    console.print("  1. Install pre-commit: [bold]pip install pre-commit && pre-commit install[/bold]")
    console.print("  2. Or use hook directly: [bold]python .hooks/codecraft-scan.py[/bold]")


@precommit_app.command("show")
def precommit_show() -> None:
    console.print("[title]Pre-commit Hook Config[/title]")
    console.print(PRE_COMMIT_CONFIG)
