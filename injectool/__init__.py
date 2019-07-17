"""Dependency injection tool"""

__version__ = '1.1.0'

from .core import DependencyError, Container, SingletonResolver, FunctionResolver
from injectool.core import make_default, add, add_singleton, add_resolve_function, resolve
