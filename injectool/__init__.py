"""Dependency injection tool"""

__version__ = '2.0.4'

from .core import DependencyError, Container
from .core import get_dependency_key, set_default_container, get_container, resolve, use_container
from .resolvers import add_singleton, add_type, add_scoped, add_per_thread
from .injection import inject, dependency
