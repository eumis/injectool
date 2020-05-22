"""Core functionality"""

from abc import abstractmethod
from contextlib import contextmanager
from contextvars import ContextVar
from copy import deepcopy
from typing import Any, Callable, Union, Dict


class DependencyError(Exception):
    """Base injectool error"""


def get_dependency_key(dependency: Union[str, Callable]) -> str:
    """returns string key for passed dependency"""
    return dependency if isinstance(dependency, str) else dependency.__name__


class Resolver:
    """Interface for resolver"""

    @abstractmethod
    def resolve(self, container: 'Container', param: Any = None):
        """Factory method for resolving dependency"""


class ContainerResolver(Resolver):
    def resolve(self, container: 'Container', param: Any = None):
        return container


class Container:
    """Container for dependencies"""

    def __init__(self, resolvers: Dict[str, Resolver] = None):
        self._resolvers: Dict[str, Resolver] = {} if resolvers is None else resolvers
        self.set(Container, ContainerResolver())

    def set(self, dependency: Union[str, Callable], resolver: Resolver):
        """Sets resolver for dependency"""
        key = get_dependency_key(dependency)
        self._resolvers[key] = resolver

    def resolve(self, dependency: Union[str, Callable], param: Any = None) -> Any:
        """Resolve dependency"""
        key = get_dependency_key(dependency)
        try:
            resolver = self._resolvers[key]
            return resolver.resolve(self, param)
        except KeyError:
            raise DependencyError('Dependency "{0}" is not found'.format(key))

    def get_resolver(self, dependency: Union[str, Callable]) -> Resolver:
        """returns resolver for dependency"""
        key = get_dependency_key(dependency)
        return self._resolvers.get(key, None)

    def copy(self) -> 'Container':
        """returns new container with same dependencies"""
        resolvers = deepcopy(self._resolvers)
        return Container(resolvers)


_CURRENT_CONTAINER = ContextVar('container')
_CURRENT_CONTAINER.set(Container())


def set_container(container: Container):
    """Sets container used for resolving and registering dependencies"""
    _CURRENT_CONTAINER.set(container)


def get_container() -> Container:
    """Returns container used for resolving and registering dependencies"""
    return _CURRENT_CONTAINER.get()


@contextmanager
def use_container(container: Container = None) -> Container:
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


def resolve(dependency: Union[str, Callable], param: Any = None):
    """resolves dependency"""
    return get_container().resolve(dependency, param)
