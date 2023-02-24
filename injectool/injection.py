"""Injection functionality"""

from functools import wraps
from typing import Any

from injectool.core import Dependency, resolve, DependencyError


def inject(*dependencies: Dependency, **name_to_dependency):
    """
    Resolves dependencies in default container
    and passes it as optional parameters to function
    """

    def _decorate(func):
        name_to_key = {
            **{dep.__name__ if hasattr(dep, '__name__') else str(dep): dep for dep in dependencies},
            **{name: dep for name, dep in name_to_dependency.items()}
        }

        @wraps(func)
        def _decorated(*args, **kwargs):
            keys_to_inject = [(name, key) for name, key in name_to_key.items()
                              if name not in kwargs]
            kwargs = {**kwargs, **{name: resolve(key) for name, key in keys_to_inject}}
            return func(*args, **kwargs)

        return _decorated

    return _decorate


def dependency(func):
    """Substitute function by calling resolved in default container"""

    @wraps(func)
    def _decorated(*args, **kwargs):
        try:
            implementation = resolve(_decorated)
        except DependencyError:
            implementation = func
        return implementation(*args, **kwargs)

    return _decorated


class InjectedDefaultValue:
    """Can used as default value for injected parameters"""
    def __init__(self):
        pass

    def __getitem__(self, *_):
        raise DependencyError()

    def __setitem__(self, *_):
        raise DependencyError()

    def __getattr__(self, *_):
        raise DependencyError()

    def __setattr__(self, *_):
        raise DependencyError()

    def __call__(self, *_, **__):
        raise DependencyError()


In: Any = InjectedDefaultValue()
