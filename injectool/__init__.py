"""Dependency injection tool"""

from .__version__ import __version__

from .core import DependencyError, Container, get_dependency_key
from .injection import inject, dependency, resolve
from .registration import register, register_single, register_func
from .scope import Scope, get_scope, set_current_scope, get_container, scope, wrap_with_scope
