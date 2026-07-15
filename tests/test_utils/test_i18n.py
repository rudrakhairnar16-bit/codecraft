from __future__ import annotations

import os
from unittest.mock import patch

import pytest

from codecraft.utils.i18n import TRANSLATIONS, set_locale, t


class TestI18n:
    def test_en_fallback_returns_key(self):
        set_locale("en")
        assert t("nonexistent_key_xyz") == "nonexistent_key_xyz"

    def test_hi_translation_known_key(self):
        set_locale("hi")
        assert t("scanning") != "scanning"
        assert t("files") != "files"

    def test_hi_translation_missing_key_fallback(self):
        set_locale("hi")
        assert t("zzz_nonexistent") == "zzz_nonexistent"

    def test_mr_translation_known_key(self):
        set_locale("mr")
        assert t("scanning") != "scanning"
        assert t("files") != "files"

    def test_mr_translation_missing_key_fallback(self):
        set_locale("mr")
        assert t("zzz_nonexistent") == "zzz_nonexistent"

    def test_fr_fallback_to_en(self):
        set_locale("fr")
        assert t("scanning") == "scanning"

    def test_all_hi_keys_have_translations(self):
        for key in TRANSLATIONS["hi"]:
            assert TRANSLATIONS["hi"][key] != "", f"Empty translation for key '{key}' in hi"

    def test_all_mr_keys_have_translations(self):
        for key in TRANSLATIONS["mr"]:
            assert TRANSLATIONS["mr"][key] != "", f"Empty translation for key '{key}' in mr"

    def test_hi_mr_have_same_keys(self):
        hi_keys = set(TRANSLATIONS["hi"].keys())
        mr_keys = set(TRANSLATIONS["mr"].keys())
        assert hi_keys == mr_keys, (
            f"Key mismatch: hi extra={hi_keys - mr_keys}, mr extra={mr_keys - hi_keys}"
        )

    def test_en_locale_empty(self):
        assert TRANSLATIONS["en"] == {}

    def test_set_locale_valid(self):
        set_locale("hi")
        assert t("debt") != "debt"

    def test_set_locale_invalid_fallback(self):
        set_locale("zh")
        assert t("debt") == "debt"

    def test_locale_from_env(self, monkeypatch):
        monkeypatch.setenv("CODECRAFT_LANG", "hi")
        import importlib
        from codecraft.utils import i18n
        importlib.reload(i18n)
        assert i18n.t("scanning") != "scanning"

    def test_locale_env_fallback(self, monkeypatch):
        monkeypatch.setenv("CODECRAFT_LANG", "zh")
        import importlib
        from codecraft.utils import i18n
        importlib.reload(i18n)
        assert i18n.t("scanning") == "scanning"

    def test_mr_translations_values(self):
        set_locale("mr")
        assert t("yes") == "होय"
        assert t("no") == "नाही"
        assert t("error") == "त्रुटी"
        assert t("success") == "यश"

    def test_hi_translations_values(self):
        set_locale("hi")
        assert t("yes") == "हाँ"
        assert t("no") == "नहीं"
        assert t("error") == "त्रुटि"
        assert t("success") == "सफलता"

    def test_hi_detected_gaps_unresolved(self):
        set_locale("hi")
        assert t("detected") != "detected"
        assert t("gaps") != "gaps"
        assert t("unresolved") != "unresolved"

    def test_mr_detected_gaps_unresolved(self):
        set_locale("mr")
        assert t("detected") != "detected"
        assert t("gaps") != "gaps"
        assert t("unresolved") != "unresolved"
