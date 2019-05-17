"""Injection functionality"""
from functools import wraps
from typing import List, Union, Type, Any

from .core import get_dependency_key
from .scope import get_container


def resolve(dep: Union[str, callable] = None, param: Any = None):
    """resolves dependency in current scope"""
    return get_container().get(dep, param)


def inject(*dependencies: List[Union[str, callable, Type[Any]]]):
    """Resolves dependencies in current scope and passes it as optional parameters to function"""

    def _decorate(func):
        keys = [get_dependency_key(dep) for dep in dependencies]

        @wraps(func)
        def _decorated(*args, **kwargs):
            args = list(args)
            keys_to_inject = [key for key in keys if key not in kwargs]
            for key in keys_to_inject:
                kwargs[key] = resolve(key)
            return func(*args, **kwargs)

        return _decorated

    return _decorate


def dependency(dep: Union[str, callable] = None):
    """Substitute function by calling resolved in current scope"""

    def _decorate(func):
        key = func if dep is None else dep

        @wraps(func)
        def _decorated(*args, **kwargs):
            return resolve(key)(*args, **kwargs)

        return _decorated

    return _decorate
