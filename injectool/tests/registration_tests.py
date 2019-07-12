from pytest import mark

from injectool import register, register_single, register_func, Scope
from injectool import get_dependency_key, dependency
from injectool.core import make_default, Container


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
