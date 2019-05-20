"""Dependency injection tool"""

__version__ = '1.0.1'

from .core import DependencyError, Container, get_dependency_key
from .injection import inject, dependency, resolve
from .registration import register, register_single, register_func
from .scope import Scope, get_container, scope, wrap_with_scope
