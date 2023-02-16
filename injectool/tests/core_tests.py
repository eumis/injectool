from unittest.mock import Mock

from pytest import raises, mark, fixture

from injectool.core import Container, DependencyError, get_dependency_name
from injectool.core import get_dependency_key, use_container, get_container, set_container
from injectool.core import resolve


@mark.parametrize('dependency, key', [
    ('key', 'key'),
    (get_dependency_key, get_dependency_key),
    (Container, Container)
])
def test_get_dependency_key(dependency, key):
    """should return __name__ for class or function"""
    assert get_dependency_key(dependency) == key


@mark.parametrize('dependency, name', [
    ('key', 'key'),
    (1, '1'),
    (get_dependency_key, 'get_dependency_key'),
    (Container, 'Container'),
])
def test_get_dependency_name(dependency, name):
    """should return __name__ else cast to string"""
    assert get_dependency_name(dependency) == name


@fixture
def container_fixture(request):
    with use_container() as container:

        request.cls.container = container

        yield container


@mark.usefixtures('container_fixture')
class ContainerTests:

    container: Container

    @mark.parametrize('dependency, resolve, check', [
        ('key', lambda: Mock(), lambda v: isinstance(v, Mock)),
        (get_dependency_key, lambda: get_dependency_key, lambda v: v == get_dependency_key),
        (Container, Container, lambda v: isinstance(v, Container))
    ])
    def test_resolve(self, dependency, resolve, check):
        """Container should resolve set dependency"""
        self.container.set(dependency, resolve)

        actual = self.container.resolve(dependency)

        assert check(actual)

    @mark.parametrize('dependency, resolve, check', [
        ('key', lambda: Mock(), lambda v: isinstance(v, Mock)),
        (get_dependency_key, lambda: get_dependency_key, lambda v: v == get_dependency_key),
        (Container, Container, lambda v: isinstance(v, Container))
    ])
    def test_last_resolver(self, dependency, resolve, check):
        """Container should overwrite resolver for same dependency"""
        self.container.set(dependency, lambda: None)
        self.container.set(dependency, resolve)

        actual = self.container.resolve(dependency)

        assert check(actual)

    def test_resolve_self(self):
        """should resolve self instance of Container"""
        actual = self.container.resolve(Container)

        assert actual == self.container

    @mark.parametrize('dependency', ['key', get_dependency_key, Mock])
    def test_resolve_raises(self, dependency):
        """resolve() should raise exception for not existent dependency"""
        with raises(DependencyError):
            self.container.resolve(dependency)

    @mark.parametrize('dependency, value', [
        ('key', lambda: None),
        (get_dependency_key, 1),
        ('ContainerTest', 'value')
    ])
    def test_copy(self, dependency, value):
        """copy() should return new Container with same dependencies"""
        self.container.set(dependency, lambda: value)

        actual = self.container.copy()

        assert actual.resolve(dependency) is value

    @mark.parametrize('dependency, value', [
        ('key', lambda: None),
        (get_dependency_key, 1),
        ('ContainerTest', 'value')
    ])
    def test_copy_uses_only_current_dependencies(self, dependency, value):
        """copy() should return new Container with same dependencies"""
        copy = self.container.copy()

        self.container.set(dependency, lambda: value)

        with raises(DependencyError):
            assert copy.resolve(dependency)

    def test_copy_for_new_dependencies(self):
        """dependencies for copied container does not affect parent"""
        self.container.set('value', lambda: 0)
        copy = self.container.copy()

        copy.set('value', lambda: 1)

        assert self.container.resolve('value') == 0
        assert copy.resolve('value') == 1


def test_get_set_container():
    """get should return current container"""
    container = Container()

    set_container(container)
    actual = get_container()

    assert container == actual


@mark.usefixtures('container_fixture')
class UseContainerTests:
    """DefaultContainerContext class tests"""

    @staticmethod
    def test_creates_container():
        """should create new container and use it"""
        container = get_container()
        with use_container() as actual:
            assert actual is not None
            assert actual != container
            assert get_container() == actual
        assert get_container() == container

    @staticmethod
    def test_uses_passed_container():
        """should create new container and use it"""
        container = get_container()
        new_container = Container()
        with use_container(new_container) as actual:
            assert actual == new_container
            assert get_container() == actual
        assert get_container() == container


class ResolveTests:
    """resolve function tests"""
    @staticmethod
    @mark.parametrize('dependency, resolve_, check', [
        ('key', lambda: Mock(), lambda v: isinstance(v, Mock)),
        (get_dependency_key, lambda: get_dependency_key, lambda v: v == get_dependency_key),
        (Container, Container, lambda v: isinstance(v, Container))
    ])
    def test_resolve(dependency, resolve_, check):
        """should resolve dependency using current container"""
        with use_container() as container:
            container.set(dependency, resolve_)

            actual = resolve(dependency)

            assert check(actual)

    @staticmethod
    def test_resolve_container():
        """should resolve current container"""
        with use_container() as container:
            actual = resolve(Container)

            assert actual == container
