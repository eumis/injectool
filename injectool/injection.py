"""Injection functionality"""

from functools import wraps
from typing import List, Union, Callable

from injectool.core import get_dependency_key, resolve, DependencyError


def inject(*dependencies: List[Union[str, Callable]], **name_to_dependency):
    """
    Resolves dependencies in default container
    and passes it as optional parameters to function
    """

    def _decorate(func):
        keys = [get_dependency_key(dep) for dep in dependencies]
        name_to_key = {
            **{key: key for key in keys},
            **{name: get_dependency_key(dep) for name, dep in name_to_dependency.items()}
        }

        @wraps(func)
        def _decorated(*args, **kwargs):
            args = list(args)
            keys_to_inject = [(name, key) for name, key in name_to_key.items() if key not in kwargs]
            for name, key in keys_to_inject:
                kwargs[name] = resolve(key)
            return func(*args, **kwargs)

        return _decorated

    return _decorate


def dependency(func):
    """Substitute function by calling resolved in default container"""

    @wraps(func)
    def _decorated(*args, **kwargs):
        try:
            implementation = resolve(func)
        except DependencyError:
            implementation = func
        return implementation(*args, **kwargs)

    return _decorated
