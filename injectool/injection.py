"""Injection functionality"""

from functools import wraps
from typing import List, Union, Callable

from injectool.core import get_dependency_key, resolve


def inject(*dependencies: List[Union[str, Callable]]):
    """Resolves dependencies in default container and passes it as optional parameters to function"""

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


def dependency(dep: Union[str, Callable] = None):
    """Substitute function by calling resolved in default container"""

    def _decorate(func):
        key = func if dep is None else dep

        @wraps(func)
        def _decorated(*args, **kwargs):
            return resolve(key)(*args, **kwargs)

        return _decorated

    return _decorate
