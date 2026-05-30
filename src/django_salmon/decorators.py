"""
Django decorator for triggering signals after method execution with arguments and stacktrace.
Modular design where @observe emits the signal and other decorators add data to it.
"""

from __future__ import annotations

import functools
import inspect
import resource
import traceback
from collections.abc import Callable
from contextvars import ContextVar
from time import perf_counter
from typing import Any

from django.dispatch import Signal

from django_salmon.config import get_config

observe_lock = ContextVar("is_observing", default=False)
observe_context: ContextVar[dict[str, Any] | None] = ContextVar(
    "observe_context", default=None
)


def should_observe() -> bool:
    """
    Determine if observation is enabled.

    This can be disabled by a configuration or if nested observations
    are disabled.
    """
    return not observe_lock.get() and get_config().get("enabled", False) is True


def _is_method(func: Callable[..., Any]) -> bool:
    sig = inspect.signature(func)
    params = list(sig.parameters.keys())
    return bool(params) and params[0] in ("self", "cls")


def _elapsed_ru(
    start: resource.struct_rusage, end: resource.struct_rusage, name: str
) -> float:
    return getattr(end, name) - getattr(start, name)


def observe(signal: Signal) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Base decorator that triggers a Django signal after a method executes.
    Other decorators (with_args, with_result, etc.) add data to this signal.

    This decorator should be placed at the TOP of the decorator stack.

    Args:
        signal: Django Signal instance to trigger

    The signal will be sent with base arguments plus any added by other decorators:
        - sender: The class of the instance (or the function itself for standalone functions)
        - instance: The instance (self) if it's a method, None otherwise
        - function_name: The name of the decorated function

    Note: Requires settings.OBSERVING = {"enabled": True} to be set in Django settings.
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        def wrapper(*func_args: Any, **func_kwargs: Any) -> Any:
            if not should_observe():
                return func(*func_args, **func_kwargs)

            if _is_method(func):
                instance = func_args[0]
                sender = instance.__class__
            else:
                instance = None
                sender = func

            context: dict[str, Any] = {
                "sender": sender,
                "instance": instance,
                "function_name": func.__name__,
            }
            context_token = observe_context.set(context)

            func_result = func(*func_args, **func_kwargs)

            signal.send(**context)

            observe_context.reset(context_token)

            return func_result

        wrapper.signal = signal  # type: ignore[attr-defined]
        return wrapper

    return decorator


def with_args(
    func: Callable[..., Any], registry_wrapped_index: int | None = None
) -> Callable[..., Any]:
    """
    Decorator that adds function arguments to the signal.
    Must be used below @observe decorator.

    Adds to signal:
        - args: Positional arguments (excluding self/cls)
        - kwargs: Keyword arguments
    """

    @functools.wraps(func)
    def wrapper(*func_args: Any, **func_kwargs: Any) -> Any:
        func_result = func(*func_args, **func_kwargs)

        if (context := observe_context.get()) is not None:
            method_args = func_args[1:] if context["instance"] else func_args
            context["args"] = method_args
            context["kwargs"] = func_kwargs

        return func_result

    return wrapper


def with_result(
    func: Callable[..., Any], registry_wrapped_index: int | None = None
) -> Callable[..., Any]:
    """
    Decorator that adds function result to the signal.
    Must be used below @observe decorator.

    Adds to signal:
        - result: The return value of the function
    """

    @functools.wraps(func)
    def wrapper(*func_args: Any, **func_kwargs: Any) -> Any:
        func_result = func(*func_args, **func_kwargs)

        if (context := observe_context.get()) is not None:
            context["result"] = func_result

        return func_result

    return wrapper


def with_stacktrace(
    func: Callable[..., Any], registry_wrapped_index: int = 0
) -> Callable[..., Any]:
    """
    Decorator that adds stacktrace to the signal.
    Must be used below @observe decorator.

    Adds to signal:
        - stacktrace: Callable that returns list of stack frames as strings

    The stacktrace is lazy-loaded - it's only computed when the callable is invoked.
    """

    @functools.wraps(func)
    def wrapper(*func_args: Any, **func_kwargs: Any) -> Any:
        func_result = func(*func_args, **func_kwargs)

        if (context := observe_context.get()) is not None:
            # Avoid showing the extract_stack() call as well as
            # the wrapping decorators.
            stack = traceback.extract_stack()[: -1 * registry_wrapped_index - 2]

            def get_stacktrace() -> list[str]:
                return traceback.format_list(stack)

            context["stacktrace"] = get_stacktrace

        return func_result

    return wrapper


def with_timing(
    func: Callable[..., Any], registry_wrapped_index: int | None = None
) -> Callable[..., Any]:
    """
    Decorator that adds timing information to the signal.
    Must be used below @observe decorator.

    Adds to signal:
        - time: Execution time in milliseconds
    """

    @functools.wraps(func)
    def wrapper(*func_args: Any, **func_kwargs: Any) -> Any:
        start_time = perf_counter()
        func_result = func(*func_args, **func_kwargs)
        end_time = perf_counter()

        if (context := observe_context.get()) is not None:
            context["time"] = (end_time - start_time) * 1000

        return func_result

    return wrapper


def with_resources(
    func: Callable[..., Any], registry_wrapped_index: int | None = None
) -> Callable[..., Any]:
    """
    Decorator that adds resource usage information to the signal.
    Must be used below @observe decorator.

    Adds to signal:
        - resources: Dict with utime, stime, vcsw, ivcsw, minflt, majflt
    """

    @functools.wraps(func)
    def wrapper(*func_args: Any, **func_kwargs: Any) -> Any:
        start_resources = resource.getrusage(resource.RUSAGE_SELF)
        func_result = func(*func_args, **func_kwargs)
        end_resources = resource.getrusage(resource.RUSAGE_SELF)

        if (context := observe_context.get()) is not None:
            context["resources"] = {
                "utime": 1000 * _elapsed_ru(start_resources, end_resources, "ru_utime"),
                "stime": 1000 * _elapsed_ru(start_resources, end_resources, "ru_stime"),
                "vcsw": _elapsed_ru(start_resources, end_resources, "ru_nvcsw"),
                "ivcsw": _elapsed_ru(start_resources, end_resources, "ru_nivcsw"),
                "minflt": _elapsed_ru(start_resources, end_resources, "ru_minflt"),
                "majflt": _elapsed_ru(start_resources, end_resources, "ru_majflt"),
            }

        return func_result

    return wrapper


def prevent_nested_observe(
    func: Callable[..., Any], registry_wrapped_index: int | None = None
) -> Callable[..., Any]:
    """
    Decorator that prevents nested observations.
    When applied, if an observation is already in progress, the function executes
    without triggering any signals.

    Must be used below @observe decorator

    Usage:
        @observe(my_signal)
        @prevent_nested_observe
        def my_method(self):
            pass
    """

    @functools.wraps(func)
    def wrapper(*func_args: Any, **func_kwargs: Any) -> Any:
        if observe_lock.get():
            return func(*func_args, **func_kwargs)

        observe_lock_token = observe_lock.set(True)
        try:
            func_result = func(*func_args, **func_kwargs)
            return func_result
        finally:
            observe_lock.reset(observe_lock_token)

    return wrapper
