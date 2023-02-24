"""Dependency resolvers used by container"""

from contextvars import ContextVar, Token
import threading
from typing import Any, Callable, Dict, List, Optional, Type

from injectool.core import get_container, Dependency, Resolver


def add(dependency: Dependency, resolve: Resolver):
    get_container().set(dependency, resolve)


def add_singleton(dependency: Dependency, value: Any):
    """Adds single value"""
    get_container().set(dependency, lambda: value)


def add_type(dependency: Dependency, type_: Type):
    """Adds type instance per reslove call"""
    get_container().set(dependency, lambda: type_())


_CURRENT_SCOPE = ContextVar('scope')


class DependencyScope:
    """Dependency scope"""
    def __init__(self):
        self._resent_token: Optional[Token] = None
        self._exit_callbacks: List[Callable[['DependencyScope'], None]] = []

    def __enter__(self):
        """sets scope as current"""
        self._reset_token = _CURRENT_SCOPE.set(self)
        return self

    def __exit__(self, *_):
        """deletes scope as current"""
        if self._resent_token is not None:
            _CURRENT_SCOPE.reset(self._resent_token)
            self._resent_token = None
        for callback in self._exit_callbacks:
            callback(self)
        self._exit_callbacks.clear()

    def on_exit(self, callback: Callable[['DependencyScope'], None]):
        """sets callback for scope disposing"""
        self._exit_callbacks.append(callback)


def scope() -> DependencyScope:
    """returns new instance of scope"""
    return DependencyScope()


_CURRENT_SCOPE.set(DependencyScope())


class ScopeResolver:
    """Instance resolver for scope"""
    def __init__(self, type_: Type, dispose: Optional[Callable[[Any], None]]):
        self._type: Type = type_
        self._dispose: Optional[Callable[[Any], None]] = dispose
        self._instances: Dict[DependencyScope, Any] = {}

    def resolve(self) -> Any:
        """returns type instance for current scope"""
        scope = _CURRENT_SCOPE.get()
        if scope not in self._instances:
            instance = self._type()
            scope.on_exit(self._on_scope_exit)
            self._instances[scope] = instance
        else:
            instance = self._instances[scope]

        return instance

    def _on_scope_exit(self, scope: DependencyScope):
        if scope in self._instances:
            instance = self._instances.pop(scope)
            if self._dispose is not None:
                self._dispose(instance)


def add_scoped(dependency: Dependency, type_: Type, dispose: Optional[Callable[[Any], None]] = None):
    """Adds type instance per scope to current container"""
    get_container().set(dependency, ScopeResolver(type_, dispose).resolve)


class ThreadResolver:
    """Instance resolver for thread"""
    def __init__(self, type_: Type):
        self._type: Type = type_
        self._instances: Dict[int, Any] = {}

    def resolve(self) -> Any:
        """returns type instance for current thread"""
        thread = threading.current_thread()
        thread_id = hash(thread)

        if thread_id not in self._instances:
            instance = self._type()
            self._instances[thread_id] = instance
        else:
            instance = self._instances[thread_id]

        return instance


def add_per_thread(dependency: Dependency, type_: Type):
    get_container().set(dependency, ThreadResolver(type_).resolve)
