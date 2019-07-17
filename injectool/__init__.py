"""Dependency injection tool"""

__version__ = '1.1.1'

from .core import DependencyError, Container, SingletonResolver, FunctionResolver
from injectool.core import make_default, add_resolver, add_singleton, add_resolve_function, resolve
from injectool.injection import inject, dependency
