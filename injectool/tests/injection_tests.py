from unittest.mock import Mock

from pytest import mark, fixture

from injectool import inject, register_single, dependency, Scope, register
from injectool import get_dependency_key, Container, resolve
from injectool.core import make_default


@fixture
def inject_fixture():
    name = 'test_container'
    Container._containers.pop(name, None)
    with make_default(name) as container:
        yield container


@mark.parametrize('dep, key', [
    ('key', 'key'),
    (get_dependency_key, 'get_dependency_key'),
    (Container, 'Container')
])
def test_inject(dep, key):
    """should inject dependencies as optional parameters using default container"""

    @inject(dep)
    def get_implementation(**kwargs):
        return kwargs[key]

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
    """should return resolved dependency from default container"""
    with make_default('test_resolve'):
        value = object()
        register_single(dep, value, param)

        assert resolve(dep, param) == value
