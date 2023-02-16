"""Core functionality"""

from contextlib import contextmanager
from contextvars import ContextVar
from typing import Any, Callable, Generator, Optional, Dict


class DependencyError(Exception):
    """Base injectool error"""


def get_dependency_key(dependency: Any) -> Any:
    """returns string key for passed dependency"""
    return dependency


def get_dependency_name(dependency: Any) -> str:
    """returns string key for passed dependency"""
    return dependency.__name__ if hasattr(dependency, '__name__') else str(dependency)


Resolve = Callable[[], Any]


class Container:
    """Container for dependencies"""

    def __init__(self, resolvers: Optional[Dict[str, Resolve]] = None):
        self._resolvers: Dict[Any, Resolve] = {} if resolvers is None else resolvers
        self.set(Container, lambda: self)

    def set(self, dependency: Any, resolve: Resolve):
        """Sets resolver for dependency"""
        self._resolvers[dependency] = resolve

    def resolve(self, dependency: Any) -> Any:
        """Resolve dependency"""
        resolve = self._resolvers.get(dependency)
        if resolve is None:
            raise DependencyError(f'Dependency "{get_dependency_name(dependency)}" is not found')
        return resolve()

    def copy(self) -> 'Container':
        """returns new container with same dependencies"""
        return Container(self._resolvers.copy())


_CURRENT_CONTAINER = ContextVar('container')
_CURRENT_CONTAINER.set(Container())


def set_container(container: Container):
    """Sets container used for resolving and registering dependencies"""
    _CURRENT_CONTAINER.set(container)


def get_container() -> Container:
    """Returns container used for resolving and registering dependencies"""
    return _CURRENT_CONTAINER.get()


@contextmanager
def use_container(container: Optional[Container] = None) -> Generator[Container, None, None]:
    """
    Uses passed container for registering and resolving dependencies
    Creates new if container doesn't exist.
    """
    container = container if container else Container()
    reset_token = _CURRENT_CONTAINER.set(container)
    try:
        yield container
    finally:
        _CURRENT_CONTAINER.reset(reset_token)


def resolve(dependency: Any):
    """resolves dependency"""
    return get_container().resolve(dependency)
