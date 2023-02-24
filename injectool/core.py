"""Core functionality"""

from contextlib import contextmanager
from contextvars import ContextVar
from typing import Any, Callable, Generator, Optional, Dict


class DependencyError(Exception):
    """Base injectool error"""


Dependency = Any
Resolver = Callable[[], Any]


class Container:
    """Container for dependencies"""

    def __init__(self, resolvers: Optional[Dict[Dependency, Resolver]] = None):
        self._resolvers: Dict[Dependency, Resolver] = {} if resolvers is None else resolvers
        self.set(Container, lambda: self)

    def set(self, dependency: Dependency, resolve: Resolver):
        """Sets resolver for dependency"""
        self._resolvers[dependency] = resolve

    def resolve(self, dependency: Dependency) -> Any:
        """Resolve dependency"""
        resolve = self._resolvers.get(dependency)
        if resolve is None:
            dependency_name = dependency.__name__ if hasattr(dependency, '__name__') else str(dependency)
            raise DependencyError(f'Dependency "{dependency_name}" is not found')
        return resolve()

    def copy(self) -> 'Container':
        """returns new container with same dependencies"""
        return Container(self._resolvers.copy())


_DEFAULT_CONTAINER = Container()

def set_default_container(container: Container):
    """Sets default container"""
    global _DEFAULT_CONTAINER
    _DEFAULT_CONTAINER = container


_CURRENT_CONTAINER = ContextVar('dependency_container')

def get_container() -> Container:
    """Returns current container"""
    return _CURRENT_CONTAINER.get(_DEFAULT_CONTAINER)


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


def resolve(dependency: Dependency):
    """resolves dependency for current container"""
    return get_container().resolve(dependency)
