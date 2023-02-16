"""Dependency resolvers used by container"""

from typing import Any, Type

from injectool.core import get_container


def add_singleton(dependency: Any, value: Any):
    """Adds singleton value to current container"""
    get_container().set(dependency, lambda: value)


def add_type(dependency: Any, type_: Type):
    """Adds type resolver to current container"""
    get_container().set(dependency, lambda: type_())
