from __future__ import annotations

import os

_LOCALE = os.environ.get("CODECRAFT_LANG", "en")

TRANSLATIONS: dict[str, dict[str, str]] = {
    "en": {},
    "hi": {
        "scanning": "स्कैन किया जा रहा है",
        "concepts": "कॉन्सेप्ट्स",
        "debt": "लर्निंग डेट",
        "files": "फ़ाइलें",
        "practice": "अभ्यास",
        "start": "शुरू करें",
        "submit": "जमा करें",
        "extend": "बढ़ाएं",
        "correct": "सही",
        "incorrect": "गलत",
        "score": "स्कोर",
        "strength": "ताकत",
        "fresh": "ताज़ा",
        "stable": "स्थिर",
        "decaying": "क्षयशील",
        "streak": "लगातार दिन",
        "suggest": "सुझाव",
        "learn": "सीखें",
        "progress": "प्रगति",
        "status": "स्थिति",
        "export": "निर्यात",
    },
}

_DEFAULT = "en"


def t(key: str) -> str:
    lang = _LOCALE if _LOCALE in TRANSLATIONS else _DEFAULT
    return TRANSLATIONS[lang].get(key, key)


def set_locale(locale: str) -> None:
    global _LOCALE
    if locale in TRANSLATIONS:
        _LOCALE = locale
