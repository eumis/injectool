"""Dependency resolvers used by container"""

from typing import Any, Callable, Union, Type

from injectool.core import Resolver, DependencyError, Container, get_container


class SingletonResolver(Resolver):
    """Singleton resolver"""

    def __init__(self, value: Any = None, param: Any = None):
        self._values = {}
        if value is not None:
            self.set_value(value, param)

    def set_value(self, value: Any, param: Any):
        """Sets value for parameter"""
        self._values[param] = value

    def resolve(self, container: Container, param: Any = None):
        try:
            return self._values[param]
        except KeyError:
            raise DependencyError(f'Singleton value for parameter {param} is not found')


class FunctionResolver(Resolver):
    """Function resolver"""

    def __init__(self, resolve_: Callable[[Container, Any], Any]):
        self._resolve = resolve_

    def resolve(self, container: Container, param: Any = None):
        return self._resolve(container, param)


def add_resolver(dependency: Union[str, Callable], resolver: Resolver):
    """Adds resolver to current container"""
    get_container().set(dependency, resolver)


def add_singleton(dependency: Union[str, Callable], value: Any):
    """Adds singleton value to current container"""
    get_container().set(dependency, SingletonResolver(value))


def add_function_resolver(dependency: Union[str, Callable],
                          resolve_: Callable[[Container, Any], Any]):
    """Adds function resolver to current container"""
    get_container().set(dependency, FunctionResolver(resolve_))


def add_type(dependency: Union[str, Callable], type_: Type):
    """Adds type resolver to current container"""
    add_function_resolver(dependency, lambda c, p=None: type_())
