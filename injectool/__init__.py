"""Dependency injection tool"""

__version__ = '2.0.0'

from .core import DependencyError, Resolver, Container, resolve
from .resolvers import SingletonResolver, FunctionResolver
from .resolvers import add_resolver, add_singleton, add_function_resolver, add_type
from .injection import inject, dependency
