from __future__ import annotations

import os

from rich.console import Console
from rich.theme import Theme

_NO_COLOR = os.environ.get("NO_COLOR", "").strip() not in ("", "0")

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

if _NO_COLOR:
    console = Console(theme=codecraft_theme, no_color=True, force_terminal=False)
else:
    console = Console(theme=codecraft_theme)
