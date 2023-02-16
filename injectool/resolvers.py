"""Dependency resolvers used by container"""

from typing import Any, Type

from injectool.core import get_container


class SingletonResolver:
    """Singleton resolver"""

    def __init__(self, value: Any):
        self._value = value

    def resolve(self):
        return self._value


def add_singleton(dependency: Any, value: Any):
    """Adds singleton value to current container"""
    get_container().set(dependency, SingletonResolver(value).resolve)


def add_type(dependency: Any, type_: Type):
    """Adds type resolver to current container"""
    get_container().set(dependency, lambda: type_())
