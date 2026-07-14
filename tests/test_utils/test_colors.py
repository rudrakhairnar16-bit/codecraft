from __future__ import annotations

import importlib
import os


def test_colors_with_no_color_disabled():
    old = os.environ.pop("NO_COLOR", None)
    try:
        os.environ["NO_COLOR"] = "0"
        import codecraft.utils.colors as c
        importlib.reload(c)
        assert c.console is not None
    finally:
        if old is not None:
            os.environ["NO_COLOR"] = old
        else:
            os.environ.pop("NO_COLOR", None)


def test_colors_with_no_color_unset():
    old = os.environ.pop("NO_COLOR", None)
    try:
        import codecraft.utils.colors as c
        importlib.reload(c)
        assert c.console is not None
    finally:
        if old is not None:
            os.environ["NO_COLOR"] = old
