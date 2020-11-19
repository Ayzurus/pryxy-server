"""
safeprint.py

Simple module to safely print logs to stdout between threads
___________________
by:
Ayzurus
___________________
thanks:
https://stackoverflow.com/questions/40356200/python-printing-in-multiple-threads
"""
from threading import Lock
from datetime import datetime

_PRINT_LOCK = Lock()
_PRINT_FORMAT = "[%s] %s: %s"
_prints_verb = False
_prints_debug = False


def setup(prints_verb: bool, prints_debug: bool):
    global _prints_verb
    global _prints_debug
    _prints_verb = prints_verb
    _prints_debug = prints_debug


def _print(level, *text, **args):
    with _PRINT_LOCK:
        print(_PRINT_FORMAT % (str(datetime.now()), level, str(*text)), **args)


def error(*text, **args):
    _print("ERROR", *text, **args)


def log(*text, **args):
    _print("INFO", *text, **args)


def log_verb(*text, **args):
    if _prints_verb:
        _print("INFO+", *text, **args)


def debug(*text, **args):
    if _prints_debug:
        _print("DEBUG", *text, **args)
