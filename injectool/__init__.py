"""Dependency injection tool"""

__version__ = '3.0.0'

from .core import Dependency, Resolver, DependencyError, Container
from .core import set_default_container, get_container, resolve, use_container
from .resolvers import add, add_singleton, add_type, add_scoped, add_per_thread, scope
from .injection import inject, dependency, In
