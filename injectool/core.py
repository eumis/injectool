"""Core functionality"""
from typing import Any, Callable


class DependencyError(Exception):
    """Base injectool error"""


class Container:
    """Container for dependencies"""

    def __init__(self):
        self._resolvers = {}
        self._factories = {}
        self.register('container', lambda: self)

    def register(self, key: str, resolver: Callable[[], Any], param=None):
        """Add resolver to container"""
        if not callable(resolver):
            raise DependencyError('Initializer {0} is not callable'.format(resolver))
        if key not in self._resolvers:
            self._resolvers[key] = {}
        self._resolvers[key][param] = resolver

    def register_factory(self, key: str, factory: Callable[[Any], Any]):
        """Add resolver that called with passed param"""
        self._factories[key] = factory

    def get(self, key, param=None):
        """Resolve dependency"""
        try:
            return self._resolvers[key][param]()
        except KeyError:
            if key in self._factories:
                return self._factories[key](param)
            raise DependencyError('Dependency "{0}" is not found'.format(key))
