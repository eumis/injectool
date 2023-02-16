from unittest.mock import Mock

from pytest import mark

from injectool.core import get_dependency_key, Container, resolve, use_container
from injectool.resolvers import add_singleton, add_type


@mark.parametrize('dependency, value', [
    ('key', lambda _, __=None: 'value'),
    (get_dependency_key, 1),
    (Container, Mock())
])
def test_add_singleton(dependency, value):
    """add_singleton() should add SingletonResolver to current container"""
    with use_container():
        add_singleton(dependency, value)

        assert resolve(dependency) is resolve(dependency)


class TestType:
    """type for type dependency tests"""


@mark.parametrize('dependency, type_', [
    (TestType, TestType)
])
def test_add_type(dependency, type_):
    """should return type instance"""
    with use_container():
        add_type(dependency, TestType)

        actual = resolve(dependency)

        assert isinstance(actual, type_)
