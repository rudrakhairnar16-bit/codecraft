from __future__ import annotations

from rich.console import Console
from rich.theme import Theme

codecraft_theme = Theme(
    {
        "info": "cyan",
        "warning": "yellow",
        "error": "red bold",
        "success": "green",
        "concept": "magenta",
        "debt": "red",
        "debt.resolved": "green",
        "score": "blue bold",
        "tier1": "white",
        "tier2": "green",
        "tier3": "yellow",
        "tier4": "red bold",
        "strength.high": "green bold",
        "strength.medium": "yellow bold",
        "strength.low": "red bold",
        "title": "bold white",
        "path": "cyan underline",
        "domain": "blue",
    }
)

console = Console(theme=codecraft_theme)
