"""Dependency registration helpers"""

from typing import Callable, Any

from .scope import get_scope


def register(key: str, resolver: Callable[[], Any], param: Any = None):
    """Adds resolver to current scope container"""
    get_scope().container.register(key, resolver, param)


def register_single(key: str, value: Any, param: Any = None):
    """Generates resolver to return passed value"""
    get_scope().container.register(key, lambda: value, param)


def register_func(key: str, func: Any, param: Any = None):
    """Generates resolver to return passed function"""
    register_single(key, func, param)
