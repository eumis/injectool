"""Scopes"""

from functools import wraps

from .core import Container, DependencyError


class Scope:
    """Dependencies scope"""

    _scope_containers = {}
    _current: 'Scope' = None

    @staticmethod
    def get_current() -> 'Scope':
        """returns current scope"""
        return Scope._current

    def __init__(self, name):
        self._previous_scope = None
        self.name = name
        if name not in Scope._scope_containers:
            parent_scope = Scope._current
            Scope._scope_containers[name] = parent_scope.get_container().copy() \
                if parent_scope else Container()

    def get_container(self) -> Container:
        """Returns scope container"""
        return Scope._scope_containers[self.name]

    def __enter__(self):
        try:
            self._previous_scope = Scope._current
        except DependencyError:
            self._previous_scope = None
        if not self._previous_scope or self.name != self._previous_scope.name:
            Scope._current = self
        return self

    def __exit__(self, exc_type, value, traceback):
        Scope._current = self._previous_scope


Scope('').__enter__()


def get_container() -> Container:
    return Scope.get_current().get_container()


def scope(name):
    """Calls function with passed scope"""

    def _decorate(func):
        return wraps(func)(wrap_with_scope(func, name))

    return _decorate


def wrap_with_scope(func, scope_name=None):
    """Wraps function with scope. If scope_name is None current scope is used"""
    if scope_name is None:
        scope_name = Scope.get_current().name
    return lambda *args, sc=scope_name, **kwargs: \
        _call_with_scope(func, sc, args, kwargs)


def _call_with_scope(func, scope_name, args, kwargs):
    with Scope(scope_name):
        return func(*args, **kwargs)
