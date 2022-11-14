from unittest.mock import Mock, call

from pytest import mark, raises

from injectool.core import get_dependency_key, Container, use_container, DependencyError
from injectool.resolvers import SingletonResolver, FunctionResolver
from injectool.resolvers import add_singleton, add_function_resolver, add_type ,add_resolver


class SingletonResolverTests:
    """Singleton resolver class tests"""

    container: Container

    @staticmethod
    @mark.parametrize('def_value, def_param, value, param', [
        (1, None, 2, SingletonResolver),
        ({}, SingletonResolver, {'key': 1}, None),
        ([], 1, ['value'], 'parameter')
    ])
    def tests_adds_value_for_parameter(def_value, def_param, value, param):
        """should add single value for parameter"""
        resolver = SingletonResolver(def_value, def_param)

        resolver.set_value(value, param)

        assert resolver.resolve(Mock(), def_param) == def_value
        assert resolver.resolve(Mock(), param) == value

    @staticmethod
    @mark.parametrize('param', [SingletonResolver, None, 'parameter'])
    def test_resolve_raises_for_unknown_param(param):
        resolver = SingletonResolver()

        with raises(DependencyError):
            resolver.resolve(param)


class FunctionResolverTests:
    """FunctionResolver class tests"""

    @staticmethod
    def test_calls_passed_function():
        """resolve() should call passed function with resolve parameters"""
        func, container, param = Mock(), Mock(), Mock()
        resolver = FunctionResolver(func)

        resolver.resolve(container, param)

        assert func.call_args == call(container, param)

    @staticmethod
    @mark.parametrize('value', ['value', None, 1])
    def test_returns_dependency(value):
        """resolve() should call passed function with resolve parameters"""
        container = Mock()
        resolver = FunctionResolver(lambda _, __=None: value)

        assert resolver.resolve(container) == value


@mark.parametrize('dependency, resolver', [
    ('key', FunctionResolver(lambda _, __: 'value')),
    (get_dependency_key, SingletonResolver(1)),
    (Container, Mock())
])
def test_add_resolver(dependency, resolver):
    """add_resolver() should add dependency resolver to current container"""
    with use_container() as container:
        add_resolver(dependency, resolver)

        assert container.get_resolver(dependency) == resolver


@mark.parametrize('dependency, value', [
    ('key', lambda _, __=None: 'value'),
    (get_dependency_key, 1),
    (Container, Mock())
])
def test_add_singleton(dependency, value):
    """add_singleton() should add SingletonResolver to current container"""
    with use_container() as container:
        add_singleton(dependency, value)

        resolver = container.get_resolver(dependency)
        assert isinstance(resolver, SingletonResolver)
        assert resolver.resolve(container) == value


@mark.parametrize('dependency, function', [
    ('key', lambda _, __=None: 'value'),
    (get_dependency_key, lambda _, __=None: 1)
])
def test_add_function_resolver(dependency, function):
    """should add FunctionResolver to current container"""
    with use_container() as container:
        add_function_resolver(dependency, function)

        resolver = container.get_resolver(dependency)
        assert isinstance(resolver, FunctionResolver)
        assert resolver.resolve(container) == function(container)


class TestType:
    """type for type dependency tests"""


@mark.parametrize('dependency, type_', [
    (TestType, TestType)
])
def test_add_type(dependency, type_):
    """add_type() should add type resolver to current container"""
    with use_container() as container:
        add_type(dependency, TestType)
        resolver = container.get_resolver(dependency)

        assert resolver is not None
        actual = resolver.resolve(container)
        assert isinstance(actual, type_)
