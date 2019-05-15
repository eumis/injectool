"""Injection functionality"""

from .scope import get_scope


def inject(*keys):
    """Resolves dependencies in current scope and passes it as optional parameters to function"""

    def _decorate(func):
        def _decorated(*args, **kwargs):
            args = list(args)
            keys_to_inject = [key for key in keys if key not in kwargs]
            for key in keys_to_inject:
                kwargs[key] = get_scope().container.get(key)
            return func(*args, **kwargs)

        return _decorated

    return _decorate


def dependency(key: str = None):
    """Substitute function by registered dependency"""

    def _decorate(func):
        dependency_name = func.__name__ if key is None else key

        def _decorated(*args, **kwargs):
            return get_scope().container.get(dependency_name)(*args, **kwargs)

        return _decorated

    return _decorate
