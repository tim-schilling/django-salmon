from __future__ import annotations

from collections.abc import Callable
from functools import partial
from pprint import pprint
from typing import Any

from django_observe.signals import observe_cache_operation

SIGNALS = [
    ("observe_cache_operation", observe_cache_operation),
]


def _print_signal(
    stacktrace: Callable[[], list[str]] | None = None, **kwargs: Any
) -> None:
    pprint(kwargs)
    if stacktrace:
        print("".join(stacktrace()))


def connect_signals() -> None:
    for name, signal in SIGNALS:
        signal.connect(
            partial(_print_signal, signal_name=name),
            dispatch_uid=f"print_signal_{name}",
        )
