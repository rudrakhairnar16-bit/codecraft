from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import typer

from codecraft.utils.colors import console

profile_app = typer.Typer(name="profile", no_args_is_help=True)

def _code_dir() -> Path:
    return Path(os.path.expanduser("~/.codecraft"))


def _profiles_file() -> Path:
    return _code_dir() / "profiles.json"


def _ensure_config() -> None:
    _code_dir().mkdir(parents=True, exist_ok=True)
    pf = _profiles_file()
    if not pf.exists():
        pf.write_text(json.dumps({"current": "default", "profiles": {"default": {}}}))


def _get_profiles() -> dict[str, Any]:
    _ensure_config()
    return json.loads(_profiles_file().read_text())  # type: ignore[no-any-return]


def _save_profiles(data: dict[str, Any]) -> None:
    _profiles_file().write_text(json.dumps(data, indent=2))


def get_current_profile() -> str:
    data = _get_profiles()
    return str(data.get("current", "default"))


def get_profile_dir() -> Path:
    profile = get_current_profile()
    return _code_dir() / "profiles" / profile


@profile_app.command("list", epilog="Example: codecraft profile list")
def profile_list() -> None:
    """List all profiles."""
    data = _get_profiles()
    current = data.get("current", "default")
    names = list(data.get("profiles", {}).keys())
    if not names:
        console.print("[warning]No profiles found[/warning]")
        return
    for name in names:
        marker = "*" if name == current else " "
        console.print(f"  [{marker}] {name}")
    console.print(f"\n[dim]Active profile: {current}[/dim]")


@profile_app.command("create", epilog="Example: codecraft profile create work --no-switch")
def profile_create(
    name: str = typer.Argument(..., help="Profile name"),
    switch: bool = typer.Option(True, "--switch/--no-switch", help="Switch to new profile after creation"),
) -> None:
    """Create a new learning profile with its own database."""
    data = _get_profiles()
    profiles = data.setdefault("profiles", {})
    if name in profiles:
        console.print(f"[error]Profile '{name}' already exists[/error]")
        raise typer.Exit(1)
    profiles[name] = {"created": str(__import__("datetime").datetime.now())}
    if switch:
        data["current"] = name
    _save_profiles(data)

    profile_dir = _code_dir() / "profiles" / name
    profile_dir.mkdir(parents=True, exist_ok=True)

    msg = f"[success]Profile '{name}' created[/success]"
    if switch:
        msg += " and activated"
    console.print(msg)


@profile_app.command("switch", epilog="Example: codecraft profile switch work")
def profile_switch(
    name: str = typer.Argument(..., help="Profile name to switch to"),
) -> None:
    """Switch to a different learning profile."""
    data = _get_profiles()
    if name not in data.get("profiles", {}):
        console.print(f"[error]Profile '{name}' not found[/error]")
        console.print("[info]Use 'profile create' to create a new profile[/info]")
        raise typer.Exit(1)
    data["current"] = name
    _save_profiles(data)
    console.print(f"[success]Switched to profile '{name}'[/success]")


@profile_app.command("delete", epilog="Example: codecraft profile delete work --force")
def profile_delete(
    name: str = typer.Argument(..., help="Profile name to delete"),
    force: bool = typer.Option(False, "--force", "-f", help="Delete without confirmation"),
) -> None:
    """Delete a profile and its database."""
    data = _get_profiles()
    if name not in data.get("profiles", {}):
        console.print(f"[error]Profile '{name}' not found[/error]")
        raise typer.Exit(1)
    if name == "default":
        console.print("[error]Cannot delete the default profile[/error]")
        raise typer.Exit(1)
    if not force:
        console.print(f"[warning]This will delete all data for profile '{name}'[/warning]")
        console.print("[info]Use --force to confirm[/info]")
        return

    del data["profiles"][name]
    if data.get("current") == name:
        data["current"] = "default"
    _save_profiles(data)

    profile_dir = _code_dir() / "profiles" / name
    db_file = profile_dir / "codecraft.duckdb"
    if db_file.exists():
        db_file.unlink()
    if profile_dir.exists():
        profile_dir.rmdir()

    console.print(f"[success]Profile '{name}' deleted[/success]")
