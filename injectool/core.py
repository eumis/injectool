"""Core functionality"""

from contextlib import contextmanager
from copy import deepcopy
from typing import Any, Callable, Union


class DependencyError(Exception):
    """Base injectool error"""


def get_dependency_key(dependency: Union[str, Callable]) -> str:
    return dependency if isinstance(dependency, str) else dependency.__name__


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
        self._factories: dict = {}
        self.register(Container, lambda: self)

    @property
    def name(self) -> str:
        return self._name

    def register(self, dependency: Union[str, Callable], resolver: Callable[[], Any], param=None):
        """Add resolver to container"""
        if not callable(resolver):
            raise DependencyError('Initializer {0} is not callable'.format(resolver))

        key = get_dependency_key(dependency)
        if key not in self._resolvers:
            self._resolvers[key] = {}

        self._resolvers[key][param] = resolver

    def register_factory(self, dependency: Union[str, Callable], factory: Callable[[Any], Any]):
        """Add resolver that called with passed param"""
        key = get_dependency_key(dependency)
        self._factories[key] = factory

    def resolve(self, dependency: Union[str, Callable], param=None) -> Any:
        """Resolve dependency"""
        key = get_dependency_key(dependency)
        try:
            return self._resolvers[key][param]()
        except KeyError:
            if key in self._factories:
                return self._factories[key](param)
            raise DependencyError('Dependency "{0}" is not found'.format(key))

    def copy(self, name: str = None) -> 'Container':
        """returns new container with same dependencies"""
        name = self.name + '_copy' if name is None else name
        new = Container(name)
        new._factories = deepcopy(self._factories)
        new._resolvers = deepcopy(self._resolvers)
        new.register(Container, lambda: new)
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
