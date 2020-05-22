"""Dependency injection tool"""

__version__ = '2.0.3'

from .core import DependencyError, Resolver, Container
from .core import get_dependency_key, set_container, get_container, resolve, use_container
from .resolvers import SingletonResolver, FunctionResolver
from .resolvers import add_resolver, add_singleton, add_function_resolver, add_type
from .injection import inject, dependency
