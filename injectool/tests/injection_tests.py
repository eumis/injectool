from unittest.mock import Mock

from pytest import mark, fixture

from injectool.core import make_default, Container, get_dependency_key, add_singleton
from injectool.injection import inject, dependency


@fixture
def inject_fixture():
    name = 'inject_tests'
    with make_default(name) as container:
        yield container


@mark.usefixtures('inject_fixture')
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


@mark.usefixtures('inject_fixture')
@mark.parametrize('default', [True, False])
def test_dependency(default):
    """should resolve function or use decorated in case not registered"""
    implementation = Mock()
    default_implementation = Mock()

    @dependency
    def func():
        default_implementation()

    if not default:
        add_singleton(func, implementation)

    func()

    assert default_implementation.called == default
    assert implementation.called == (not default)
