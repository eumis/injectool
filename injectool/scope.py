"""Scopes"""
from threading import local as thread_local

from .core import Container, DependencyError

_THREAD_LOCAL = thread_local()


class Scope:
    """Dependencies scope"""

    _scope_containers = {}

    def __init__(self, name):
        self._previous_scope = None
        self.name = name
        if name not in Scope._scope_containers:
            Scope._scope_containers[name] = Container()

    @property
    def container(self):
        """Returns scope container"""
        return Scope._scope_containers[self.name]

    def __enter__(self):
        try:
            self._previous_scope = get_scope()
        except DependencyError:
            self._previous_scope = None
        if not self._previous_scope or self.name != self._previous_scope.name:
            self.container.register('scope', lambda: self)
            set_current_scope(self)
        return self

    def __exit__(self, exc_type, value, traceback):
        set_current_scope(self._previous_scope)


def get_scope() -> Scope:
    """return current scope"""
    current_scope = getattr(_THREAD_LOCAL, 'current_scope', None)
    if current_scope is None:
        raise DependencyError("ioc is not set up for current thread")
    return _THREAD_LOCAL.current_scope


def get_container() -> Container:
    return get_scope().container


def set_current_scope(current_scope: Scope):
    """sets current scope"""
    _THREAD_LOCAL.current_scope = current_scope


Scope('').__enter__()


def scope(name):
    """Calls function with passed scope"""

    def _decorate(func):
        return wrap_with_scope(func, name)

    return _decorate


def wrap_with_scope(func, scope_name=None):
    """Wraps function with scope. If scope_name is None current scope is used"""
    if scope_name is None:
        scope_name = get_scope().name
    return lambda *args, sc=scope_name, **kwargs: \
        _call_with_scope(func, sc, args, kwargs)


def _call_with_scope(func, scope_name, args, kwargs):
    with Scope(scope_name):
        return func(*args, **kwargs)
