from unittest.mock import Mock

from pytest import mark, fixture

from injectool.core import use_container, Container, get_dependency_key
from injectool.injection import inject, dependency
from injectool.resolvers import add_singleton


@fixture
def inject_fixture():
    with use_container() as container:
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
