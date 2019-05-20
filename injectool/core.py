"""Core functionality"""
from copy import deepcopy
from typing import Any, Callable, Union, Type


class DependencyError(Exception):
    """Base injectool error"""


def get_dependency_key(dependency: Union[str, callable, Type[Any]]) -> str:
    return dependency if isinstance(dependency, str) else dependency.__name__


class Container:
    """Container for dependencies"""

    def __init__(self):
        self._resolvers = {}
        self._factories = {}
        self.register(Container, lambda: self)

    def register(self, dependency: Union[str, callable, Type[Any]], resolver: Callable[[], Any], param=None):
        """Add resolver to container"""
        if not callable(resolver):
            raise DependencyError('Initializer {0} is not callable'.format(resolver))

        key = get_dependency_key(dependency)
        if key not in self._resolvers:
            self._resolvers[key] = {}

        self._resolvers[key][param] = resolver

    def register_factory(self, dependency: Union[str, callable, Type[Any]], factory: Callable[[Any], Any]):
        """Add resolver that called with passed param"""
        key = get_dependency_key(dependency)
        self._factories[key] = factory

    def get(self, dependency: Union[str, callable, Type[Any]], param=None) -> Any:
        """Resolve dependency"""
        key = get_dependency_key(dependency)
        try:
            return self._resolvers[key][param]()
        except KeyError:
            if key in self._factories:
                return self._factories[key](param)
            raise DependencyError('Dependency "{0}" is not found'.format(key))

    def copy(self) -> 'Container':
        """returns new container with same dependencies"""
        new = Container()
        new._factories = deepcopy(self._factories)
        new._resolvers = deepcopy(self._resolvers)
        new.register(Container, lambda: new)
        return new
