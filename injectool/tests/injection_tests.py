from unittest.mock import Mock

from pytest import mark, fixture

from injectool.core import make_default, Container, get_dependency_key, add_singleton, add_resolve_function
from injectool.injection import inject, dependency


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
    add_singleton(dep, value)

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
    add_resolve_function(key, lambda c, param=None: implementation)

    dep()

    assert implementation.called
