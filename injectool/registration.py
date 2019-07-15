"""Dependency registration helpers"""

from typing import Callable, Any, Union, Type

from injectool import Container
from injectool.core import Resolver, DependencyError


class Singleton(Resolver):
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


def register(dependency: Union[str, Callable, Type[Any]], resolver: Callable[[], Any], param: Any = None):
    """Adds resolver to current scope container"""
    Container.get().register(dependency, resolver, param)


def register_single(dependency: Union[str, Callable, Type[Any]], value: Any, param: Any = None):
    """Generates resolver to return passed value"""
    Container.get().register(dependency, lambda: value, param)


def register_func(dependency: Union[str, Callable, Type[Any]], func: Callable, param: Any = None):
    """Generates resolver to return passed function"""
    register_single(dependency, func, param)
