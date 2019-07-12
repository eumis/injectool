"""Dependency registration helpers"""

from typing import Callable, Any, Union, Type

from injectool import Container


def register(dependency: Union[str, Callable, Type[Any]], resolver: Callable[[], Any], param: Any = None):
    """Adds resolver to current scope container"""
    Container.get().register(dependency, resolver, param)


def register_single(dependency: Union[str, Callable, Type[Any]], value: Any, param: Any = None):
    """Generates resolver to return passed value"""
    Container.get().register(dependency, lambda: value, param)


def register_func(dependency: Union[str, Callable, Type[Any]], func: Callable, param: Any = None):
    """Generates resolver to return passed function"""
    register_single(dependency, func, param)
