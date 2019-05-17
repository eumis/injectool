"""Dependency registration helpers"""

from typing import Callable, Any, Union, Type

from .scope import get_container


def register(dependency: Union[str, callable, Type[Any]], resolver: Callable[[], Any], param: Any = None):
    """Adds resolver to current scope container"""
    get_container().register(dependency, resolver, param)


def register_single(dependency: Union[str, callable, Type[Any]], value: Any, param: Any = None):
    """Generates resolver to return passed value"""
    get_container().register(dependency, lambda: value, param)


def register_func(dependency: Union[str, callable, Type[Any]], func: callable, param: Any = None):
    """Generates resolver to return passed function"""
    register_single(dependency, func, param)
