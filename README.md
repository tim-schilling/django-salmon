# Django Salmon

_A standardized way to observe Django's internals._

Observability is critical feature of software development, but tends to be neglected. It seems like the majority of Python APMs and observability tools have to monkey-patch Django's internals to properly observe the application. This library seeks to do that monkey-patching once, then provide a standardized set of signals/hooks to observe an application.


## Usage

1. Install it as a dependency:

  ```bash
  pip install django-salmon
  ```

2. Add it to your ``INSTALLED_APPS``:

  ```python
  INSTALLED_APPS = [
      # ...
      "django_salmon",
      # ...
  ]
  ```

3. Connect to the relevant signals:

  ```python
  from django.dispatch import receiver
  from django_salmon.signals import observe_cache_operation


  @receiver(observe_cache_operation)
  def observe_cache_ops(sender, args, result, timing, stacktrace):
      print(f"{sender=}\t{timing=}=")
      # stacktrace is a callable that will return the formatted stacktrace.
      print("".join(stacktrace()))
  ```

### Configuration

Django Salmon supports customizing the decorators that are applied to Django functionality. For example, by default the following decorators are used on all cache operations:

```python
OBSERVING = {
    "cache": [
        "django_salmon.decorators.prevent_nested_observe",
        "django_salmon.decorators.with_args",
        "django_salmon.decorators.with_result",
        "django_salmon.decorators.with_stacktrace",
        "django_salmon.decorators.with_timing",
    ],
}
```

Each of these decorators will measure a different facet and include it in the context for the ``django_salmon.decorators.observe`` decorator. If you only need to measure the timing facet, use the following configuration:

```python
OBSERVING = {
    "cache": [
        "django_salmon.decorators.prevent_nested_observe",
        "django_salmon.decorators.with_timing",
    ],
}
```

### Observing your own functions

Django Salmon supports you applying your own decorators explicitly or by using a registry and utilizing the ``OBSERVING`` configuration.

```python
from django.dispatch import Signal
from django_salmon.decorators import observe, with_args

my_signal = Signal()


@observe(my_signal)
@with_args
def explicit_usage_example(arg1, arg2, kwarg1=None):
    return "result"
```

You can register your own stacked decorators to the registry as well:

```python
# settings.py
OBSERVING = {
    "only_timing": [
        "django_salmon.decorators.prevent_nested_observe",
        "django_salmon.decorators.with_timing",
    ],
}

# signals.py
from django.dispatch import Signal

my_signal = Signal()

# observe.py / Or anything else you want to use
from django_salmon import registry
from django_salmon.decorators import observe
from .signals import my_signal


def observe_only_timing(func):
    """
    Custom decorator factory that emits ``my_signal`` signals.
    """
    return observe(my_signal)(registry.apply_decorators("only_timing", func))


# your_logic.py
from .observe import observe_only_timing


@observe_only_timing
def registry_usage_example(arg1, arg2, kwarg1=None):
    return "result"
```

### Creating your own observer decorator

You can define your own decorator to be used with the registry by adding the relevant data to the context.

An example is:

```python
import functools
from django.dispatch import receiver, Signal
from django_salmon.decorators import observe_context, observe


def with_answer_to_everything(func):
    """
    Decorator that adds the answer to life to the context.
    Must be used below @observe decorator.
    """

    @functools.wraps(func)
    def wrapper(*func_args, **func_kwargs):
        func_result = func(*func_args, **func_kwargs)
        # The context will be None if OBSERVING["enabled"] is False
        if (context := observe_context.get()) is not None:
            # Observe some aspect of the project
            context["answer_to_everything"] = 42
        return func_result

    return wrapper


my_signal = Signal()


@receiver(my_signal)
def my_signal_receiver(sender, answer_to_everything, **kwargs):
    """
    When my_signal is raised, it will now include answer_to_everything
    as a keyword argument.
    """
    print(f"{answer_to_everything=}")


@observe(my_signal)
@with_answer_to_everything
def custom_decorator_example():
    return "result"
```

## Project goals

This project contains several hacks to support observing a Django application. The Django project should change to avoid the necessity of these hacks.

Going further, ideally the Django framework would consider adopting an observability API rendering this project obsolete.

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) for how to contribute!
