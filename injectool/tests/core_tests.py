from unittest.mock import Mock, call

from pytest import raises, mark, fixture

from injectool.core import Container, DependencyError
from injectool.core import get_dependency_key, use_container, get_container, set_container
from injectool.core import resolve
from injectool.resolvers import SingletonResolver, FunctionResolver, add_resolver


@mark.parametrize('dependency, key', [
    ('key', 'key'),
    (get_dependency_key, 'get_dependency_key'),
    ('ContainerTest', 'ContainerTest')
])
def test_get_dependency_key(dependency, key):
    """get_dependency_key() should return __name__ for class or function"""
    assert get_dependency_key(dependency) == key


@fixture
def container_fixture(request):
    with use_container() as container:
        request.cls.container = container
        yield container


@mark.usefixtures('container_fixture')
class ContainerTests:
    @staticmethod
    @mark.parametrize('dependency, resolver', [
        ('key', Mock()),
        (get_dependency_key, SingletonResolver),
        ('ContainerTests', FunctionResolver)
    ])
    def test_init_resolvers(dependency, resolver):
        """Uses resolvers passed to __init__"""
        container = Container({get_dependency_key(dependency): resolver})

        assert container.get_resolver(dependency) == resolver

    @mark.parametrize('dependency, resolver', [
        ('key', Mock()),
        (get_dependency_key, SingletonResolver),
        ('ContainerTest', FunctionResolver)
    ])
    def test_set(self, dependency, resolver):
        """Container should set resolver for dependency"""
        self.container.set(dependency, resolver)

        assert self.container.get_resolver(dependency) == resolver

    @mark.parametrize('dependency, resolver, last_resolver', [
        ('key', Mock(), FunctionResolver),
        (get_dependency_key, SingletonResolver, Mock()),
        ('ContainerTest', FunctionResolver, SingletonResolver)
    ])
    def test_last_resolver(self, dependency, resolver, last_resolver):
        """Container should overwrite resolver for same dependency"""
        self.container.set(dependency, resolver)
        self.container.set(dependency, last_resolver)

        assert self.container.get_resolver(dependency) == last_resolver

    @mark.parametrize('dependency', ['key', get_dependency_key, 'ContainerTest'])
    def test_get_resolver_returns_none(self, dependency):
        """get_resolver() should return none for not existent dependency"""
        assert self.container.get_resolver(dependency) is None

    @mark.parametrize('dependency, param', [
        ('key', None),
        (get_dependency_key, 'param'),
        ('ContainerTest', None)
    ])
    def test_resolve_uses_resolver(self, dependency, param):
        """resolve() should return resolver result"""
        result = Mock()
        resolver = Mock(resolve=Mock())
        resolver.resolve.side_effect = lambda c, p: result
        self.container.set(dependency, resolver)

        actual = self.container.resolve(dependency, param)

        assert resolver.resolve.call_args == call(self.container, param)
        assert actual == result

    @mark.parametrize('dependency', ['key', get_dependency_key, 'ContainerTest'])
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
        self.container.set(dependency, SingletonResolver(value))

        actual = self.container.copy()

        assert actual.resolve(dependency) == value

    @mark.parametrize('dependency, value', [
        ('key', lambda: None),
        (get_dependency_key, 1),
        ('ContainerTest', 'value')
    ])
    def test_copy_uses_only_current_dependencies(self, dependency, value):
        """copy() should return new Container with same dependencies"""
        copy = self.container.copy()

        self.container.set(dependency, SingletonResolver(value))

        with raises(DependencyError):
            assert copy.resolve(dependency)

    def test_copy_for_new_dependencies(self):
        """dependencies for copied container does not affect parent"""
        self.container.set('value', SingletonResolver(0))
        copy = self.container.copy()

        copy.set('value', SingletonResolver(1))

        assert self.container.resolve('value') == 0
        assert copy.resolve('value') == 1

    @mark.parametrize('param', [None, 'some param', object])
    def test_resolves_container(self, param):
        """should resolve Container"""

        actual = self.container.resolve(Container, param=param)

        assert actual == self.container


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


@mark.parametrize('dependency, resolver', [
    ('key', FunctionResolver(lambda c, param=None: 'value')),
    (get_dependency_key, SingletonResolver(1))
])
def test_resolve(dependency, resolver):
    """resolve() should resolve dependency using current container"""
    with use_container() as container:
        add_resolver(dependency, resolver)

        assert resolve(dependency) == container.resolve(dependency)
