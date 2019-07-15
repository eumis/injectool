from unittest.mock import Mock

from pytest import mark, raises

from injectool import register, register_single, register_func, Scope
from injectool import get_dependency_key, dependency
from injectool.core import make_default, Container, DependencyError
from injectool.registration import Singleton


class SingletonTests:
    """Singleton resolver class tests"""

    @staticmethod
    @mark.parametrize('def_value, def_param, value, param', [
        (1, None, 2, Singleton),
        ({}, Singleton, {'key': 1}, None),
        ([], 1, ['value'], 'parameter')
    ])
    def tests_adds_value_for_parameter(def_value, def_param, value, param):
        """should add single value for parameter"""
        resolver = Singleton(def_value, def_param)

        resolver.add_value(value, param)

        assert resolver.resolve(Mock(), def_param) == def_value
        assert resolver.resolve(Mock(), param) == value

    @staticmethod
    @mark.parametrize('value, param', [
        (2, Singleton),
        ({'key': 1}, None),
        (['value'], 'parameter')
    ])
    def tests_add_raises_for_exiting_parameter(value, param):
        """should raise error for adding existing param"""
        resolver = Singleton(value, param)

        with raises(DependencyError):
            resolver.add_value(value, param)

    @staticmethod
    @mark.parametrize('param', [Singleton, None, 'parameter'])
    def test_resolve_raises_for_unknown_param(param):
        resolver = Singleton()

        with raises(DependencyError):
            resolver.resolve(param)


@mark.parametrize('dep, param', [
    ('key', None),
    (get_dependency_key, 'param'),
    (Scope, None)
])
def test_register(dep, param):
    """register() register resolver in current container"""
    value = object()

    with make_default('test_register'):
        register(dep, lambda v=value: v, param)

        assert Container.get().resolve(dep, param) == value


@mark.parametrize('dep, param', [
    ('key', None),
    (get_dependency_key, 'param'),
    (Scope, None)
])
def test_register_single(dep, param):
    """register_single() should register resolver that returns value"""
    value = object()

    with make_default('test_register_single'):
        register_single(dep, value, param)

        assert Container.get().resolve(dep, param) == value


@dependency()
def some_function(_, __):
    pass


def some_implementation(arg1, arg2):
    print(arg1, arg2)


@mark.parametrize('dep, func, param', [
    (some_function, some_implementation, None),
    (some_function, lambda a, b: None, 'parameter'),
    (get_dependency_key, lambda *a: None, None)
])
def test_register_func(dep, func, param):
    """should register function as singleton"""
    with make_default('test_register_func'):
        register_func(dep, func, param)

        assert Container.get().resolve(dep, param) == func
