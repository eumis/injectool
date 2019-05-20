from unittest.mock import Mock

from pytest import mark

from injectool import inject, register_single, dependency, Scope, register
from injectool import get_dependency_key, Container, resolve


@mark.parametrize('dep, key', [
    ('key', 'key'),
    (get_dependency_key, 'get_dependency_key'),
    (Container, 'Container')
])
def test_inject(dep, key):
    """should inject dependencies as optional parameters"""

    @inject(dep)
    def get_implementation(**kwargs):
        return kwargs[key]

    with Scope('test_inject'):
        value = object()
        register_single(dep, value)

        assert get_implementation() == value


@dependency()
def interface_func():
    pass


@dependency('func_key')
def keyed_func():
    pass


class Interface:
    pass


@dependency(Interface)
def get_interface():
    pass


@mark.parametrize('dep, key', [
    (interface_func, get_dependency_key(interface_func)),
    (keyed_func, 'func_key'),
    (get_interface, get_dependency_key(Interface)),
])
def test_dependency(dep, key):
    implementation = Mock()
    register(key, lambda: implementation)

    dep()

    assert implementation.called


@mark.parametrize('dep, key, param', [
    ('key', 'key', None),
    (get_dependency_key, 'get_dependency_key', Container),
    (Container, 'Container', 'parameter')
])
def test_resolve(dep, key, param):
    """should return resolved dependency in current scope"""
    with Scope('test_resolve'):
        value = object()
        register_single(dep, value, param)

        assert resolve(dep, param) == value
