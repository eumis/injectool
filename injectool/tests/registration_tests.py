from pytest import mark

from injectool import register, register_single, register_func, Scope, get_container


@mark.parametrize('param', [None, 'parameter'])
def test_register(param):
    """register() register resolver in current container"""
    value = object()
    key = 'key'

    with Scope('test_register'):
        register(key, lambda i=value: i, param)

        assert get_container().get(key, param) == value


@mark.parametrize('value, param', [
    (object(), None),
    (object(), 'parameter'),
    (lambda: None, None),
    (lambda: object(), 'parameter')
])
def test_register_single(value, param):
    """register_single() should register resolver that returns value"""
    key = 'key'

    with Scope('test_register_single'):
        register_single(key, value, param)

        assert get_container().get(key, param) == value


@mark.parametrize('value, param', [
    (lambda: None, None),
    (lambda: object(), 'parameter')
])
def test_register_func(value, param):
    """register_func() should register resolver that returns function"""
    key = 'key'

    with Scope('test_register_func'):
        register_func(key, value, param)

        assert get_container().get(key, param) == value
