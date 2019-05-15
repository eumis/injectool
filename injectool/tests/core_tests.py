from pytest import raises

from injectool import Container, DependencyError


def test_register():
    """Container should register dependencies"""
    container = Container()
    one = object()
    two = object()
    three = object()
    four = object()
    container.register('key', lambda: one)
    container.register('paramed', lambda: two)
    container.register('paramed', lambda: three, 1)
    container.register_factory('paramed', lambda param: four if param == 2 else None)

    assert container.get('key') == one
    assert container.get('paramed') == two
    assert container.get('paramed', 1) == three
    assert container.get('paramed', 2) == four


def test_last_dependency():
    """register() should overwrite dependency"""
    container = Container()
    one = object()
    two = object()
    container.register('key', lambda: one)
    container.register('key', lambda: two)
    container.register('paramed', lambda: one, 1)
    container.register('paramed', lambda: two, 1)

    assert container.get('key') == two
    assert container.get('paramed', 1) == two


def test_register_raises():
    """register() should raise error if initializer is not callable"""
    container = Container()
    with raises(DependencyError):
        container.register('key', object())


def test_get_raises():
    """Container should raise exception for not existent dependency"""
    container = Container()
    with raises(DependencyError):
        container.get('key')


def test_get_params_raises():
    """Container should raise exception for not existent dependency"""
    container = Container()
    with raises(DependencyError):
        container.get('new key')

    container.register('key', lambda: 1)
    with raises(DependencyError):
        container.get('key', 'param')


def test_self_registration():
    """Container should register himself with key "Container"""
    container = Container()
    registered_container = container.get('container')

    assert registered_container == container
