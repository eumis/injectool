"""Core functionality"""

from abc import abstractmethod
from contextlib import contextmanager
from copy import deepcopy
from typing import Any, Callable, Union, Type


class DependencyError(Exception):
    """Base injectool error"""


def get_dependency_key(dependency: Union[str, Callable]) -> str:
    return dependency if isinstance(dependency, str) else dependency.__name__


class Resolver:
    @abstractmethod
    def resolve(self, container: 'Container', param: Any = None):
        """Factory method for resolving dependency"""


class SingletonResolver(Resolver):
    """Singleton resolver"""

    def __init__(self, value: Any = None, param: Any = None):
        self._values = {}
        if value is not None:
            self.add_value(value, param)

    def add_value(self, value: Any, param: Any):
        if param in self._values:
            raise DependencyError(f'Singleton value for parameter {param} is already added')
        self._values[param] = value

    def resolve(self, container: 'Container', param: Any = None):
        try:
            return self._values[param]
        except KeyError:
            raise DependencyError(f'Singleton value for parameter {param} is not found')


class FunctionResolver(Resolver):
    """Function resolver"""

    def __init__(self, resolve_: Callable[['Container', Any], Any]):
        self._resolve = resolve_

    def resolve(self, container: 'Container', param: Any = None):
        return self._resolve(container, param)


class Container:
    """Container for dependencies"""

    _containers: dict = {}
    _default: 'Container' = None

    def __init__(self, name=''):
        if name in Container._containers:
            raise DependencyError(f'Container with name {name} already exist')
        Container._containers[name] = self
        self._name: str = name
        self._resolvers: dict = {}

    @property
    def name(self) -> str:
        return self._name

    def add(self, dependency: Union[str, Callable], resolver: Resolver):
        """Add resolver to container"""
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
        key = get_dependency_key(dependency)
        return self._resolvers.get(key, None)

    def copy(self, name: str = None) -> 'Container':
        """returns new container with same dependencies"""
        name = self.name + '_copy' if name is None else name
        new = Container(name)
        new._resolvers = deepcopy(self._resolvers)
        return new

    @staticmethod
    def get(name: str = None) -> 'Container':
        try:
            return Container._get_default() if name is None else Container._containers[name]
        except KeyError:
            raise DependencyError(f'Container {name} is not found')

    @staticmethod
    def _get_default() -> 'Container':
        return Container._containers[''] if Container._default is None else Container._default

    @staticmethod
    def _set_default(container: 'Container'):
        Container._default = container


Container('')


@contextmanager
def make_default(container_name: str) -> Container:
    try:
        container = Container.get(container_name)
    except DependencyError:
        container = Container(container_name)
    default = Container.get()
    Container._set_default(container)
    try:
        yield container
    finally:
        Container._set_default(default)


def add_resolver(dependency: Union[str, Callable], resolver: Resolver):
    """Adds resolver to current container"""
    Container.get().add(dependency, resolver)


def add_singleton(dependency: Union[str, Callable], value: Any):
    """Adds singleton value to current container"""
    Container.get().add(dependency, SingletonResolver(value))


def add_resolve_function(dependency: Union[str, Callable], resolve_: Callable[['Container', Any], Any]):
    """Adds function resolver to current container"""
    Container.get().add(dependency, FunctionResolver(resolve_))


def add_type(dependency: Union[str, Callable], type_: Type):
    """Adds type resolver to current container"""
    add_resolve_function(dependency, lambda c, p=None: type_())


def resolve(dependency: Union[str, Callable], param: Any = None):
    """resolves dependency in current container"""
    return Container.get().resolve(dependency, param)
