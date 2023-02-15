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
class InjectTests:
    container: Container

    @staticmethod
    @mark.parametrize('dep, key', [
        ('key', 'key'),
        (get_dependency_key, get_dependency_key.__name__),
        (Container, 'Container')
    ])
    def test_inject_dependency(dep, key):
        """should inject dependencies as optional parameters"""

        @inject(dep)
        def get_implementation(**kwargs):
            return kwargs[key]

        value = object()
        add_singleton(dep, value)

        assert get_implementation() == value

    @staticmethod
    @mark.parametrize('dep, key, parameter', [
        ('key', 'key', None),
        (get_dependency_key, get_dependency_key.__name__, 'param'),
        (Container, Container.__name__, object())
    ])
    def test_uses_passed_value(dep, key, parameter):
        """should use passed value instead of inject it"""

        @inject(dep)
        def get_implementation(**kwargs):
            return kwargs[key]

        add_singleton(dep, object())

        assert get_implementation(**{key: parameter}) == parameter

    @staticmethod
    @mark.parametrize('dep, name', [
        ('key', 'key'),
        (get_dependency_key, 'dep_key'),
        (Container, 'con')
    ])
    def test_inject_dependency_with_name(dep, name):
        """should inject dependencies as optional parameters with custom name"""

        @inject(**{name: dep})
        def get_implementation(**kwargs):
            return kwargs[name]

        value = object()
        add_singleton(dep, value)

        assert get_implementation() == value

    @staticmethod
    @mark.parametrize('dep, name, parameter', [
        ('key', 'key', None),
        (get_dependency_key, 'dep_key', 'value'),
        (Container, 'con', object())
    ])
    def test_uses_passed_value_by_name(dep, name, parameter):
        """should use passed value instead of inject it for custom names"""

        @inject(**{name: dep})
        def get_implementation(**kwargs):
            return kwargs[name]

        add_singleton(dep, object())

        assert get_implementation(**{name: parameter}) == parameter


@mark.usefixtures('inject_fixture')
@mark.parametrize('use_implementation', [False, True])
def test_dependency(use_implementation):
    """should resolve function or use decorated in case not registered"""
    implementation = Mock()
    default_implementation = Mock()

    @dependency
    def func():
        default_implementation()

    if use_implementation:
        add_singleton(func, implementation)

    func()

    assert default_implementation.called == (not use_implementation)
    assert implementation.called == use_implementation
