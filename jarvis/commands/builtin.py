from __future__ import annotations

import datetime as dt
import logging
import webbrowser
from typing import Callable, Dict

logger = logging.getLogger(__name__)


def open_youtube() -> str:
    webbrowser.open("https://youtube.com")
    return "Открываю YouTube"


def open_google() -> str:
    webbrowser.open("https://google.com")
    return "Открываю Google"


def open_browser() -> str:
    webbrowser.open("https://yandex.ru")
    return "Открываю браузер"


def tell_time() -> str:
    now = dt.datetime.now().strftime("%H:%M")
    return f"Сейчас {now}"


BUILTIN_COMMANDS: Dict[str, Callable[[], str]] = {
    "открой ютуб": open_youtube,
    "открой гугл": open_google,
    "открой браузер": open_browser,
    "который час": tell_time,
    "какое время": tell_time,
}
