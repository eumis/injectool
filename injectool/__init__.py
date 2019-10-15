"""Dependency injection tool"""

__version__ = '1.1.2'

from .core import DependencyError, Container, SingletonResolver, FunctionResolver
from .core import make_default, add_resolver, add_singleton, add_function_resolver, resolve
from .injection import inject, dependency
