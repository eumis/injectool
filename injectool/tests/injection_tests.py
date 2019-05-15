from unittest.mock import Mock

from pytest import mark

from injectool import inject, register_single, register_func, dependency


def test_inject():
    """should pass dependencies as optional parameters"""
    one = object()

    def two(): return one

    register_single('one', one)
    register_func('two', two)

    assert _get_default_injected() == (one, two)
    assert _get_kwargs_injected() == (one, two)


@inject('one', 'two')
def _get_default_injected(one=None, two=None):
    return one, two


@inject('one', 'two')
def _get_kwargs_injected(**kwargs):
    return kwargs['one'], kwargs['two']


@mark.parametrize('key, dependency_key', [
    (None, 'interface'),
    ('key', 'key'),
])
def test_dependency(key, dependency_key):
    @dependency(key)
    def interface():
        pass

    implementation = Mock()
    register_func(dependency_key, implementation)

    interface()

    assert implementation.called
