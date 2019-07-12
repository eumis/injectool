from pytest import raises, mark, fixture, fail

from injectool import Container, DependencyError, Scope, get_dependency_key
from injectool.core import make_default


@mark.parametrize('dependency, key', [
    ('key', 'key'),
    (get_dependency_key, 'get_dependency_key'),
    (Container, 'Container')
])
def test_get_dependency_key(dependency, key):
    """get_dependency_key() should return __name__ for class or function"""
    assert get_dependency_key(dependency) == key


@fixture
def container_fixture(request):
    Container._containers = {}
    Container('')
    request.cls.container = Container('test_container')


@mark.usefixtures('container_fixture')
class ContainerTests:
    """Container class tests"""

    @staticmethod
    @mark.parametrize('name', ['container', 'other container'])
    def test_name(name):
        """__init__ should setup name"""
        container = Container(name)

        assert container.name == name

    @staticmethod
    @mark.parametrize('name', ['container', 'other container'])
    def test_container_name_unique(name):
        """Container name should be unique"""
        Container(name)
        with raises(DependencyError):
            Container(name)

    @mark.parametrize('dependency, param', [
        ('key', None),
        (get_dependency_key, 'param'),
        (Scope, None)
    ])
    def test_register(self, dependency, param):
        """Container should register dependencies"""
        value = object()

        self.container.register(dependency, lambda: value, param)

        assert self.container.resolve(dependency, param) == value

    @mark.parametrize('dependency, param', [
        ('key', None),
        (get_dependency_key, 'param'),
        (Scope, None)
    ])
    def test_last_dependency(self, dependency, param):
        """register() should overwrite dependency"""
        value = object()
        last_value = object()

        self.container.register(dependency, lambda: value, param)
        self.container.register(dependency, lambda: last_value, param)

        assert self.container.resolve(dependency, param) == last_value

    @mark.parametrize('dependency, resolver, param', [
        ('key', {}, None),
        (get_dependency_key, object(), 'param'),
        (Scope, 2, None)
    ])
    def test_register_raises(self, dependency, resolver, param):
        """register() should raise error if initializer is not callable"""
        with raises(DependencyError):
            self.container.register(dependency, resolver, param)

    @mark.parametrize('dependency, param', [
        ('key', None),
        (get_dependency_key, 'param'),
        (Scope, None)
    ])
    def test_resolve_raises(self, dependency, param):
        """resolve() should raise exception for not existent dependency"""
        with raises(DependencyError):
            self.container.resolve(dependency, param)

    def test_self_registration(self, ):
        """Container should register himself with key "Container"""
        assert self.container.resolve(Container) == self.container

    @mark.parametrize('dependency, param', [
        ('key', None),
        (get_dependency_key, 'param'),
        (Scope, None)
    ])
    def test_copy(self, dependency, param):
        """copy() should return new Container with same dependencies"""
        value = object()
        self.container.register(dependency, lambda: value, param)

        actual = self.container.copy()

        assert actual.resolve(dependency, param) == value

    @mark.parametrize('source_name, expected_name', [
        ('', '_copy'),
        ('name', 'name_copy'),
        ('another name', 'another name_copy')
    ])
    def test_copy_sets_name(self, source_name, expected_name):
        """copy() should return new Container with same dependencies"""
        container = Container.get() if source_name == '' else Container(source_name)

        actual = container.copy()

        assert actual.name == expected_name

    @mark.parametrize('name', ['name', 'another name'])
    def test_copy_sets_passed_name(self, name):
        """copy() should return new Container with same dependencies"""
        actual = self.container.copy(name)

        assert actual.name == name

    @mark.parametrize('dependency, param', [
        ('key', None),
        (get_dependency_key, 'param'),
        (Scope, None)
    ])
    def test_copy_uses_only_current_dependencies(self, dependency, param):
        """copy() should return new Container with same dependencies"""
        actual = self.container.copy()
        value = object()
        self.container.register(dependency, lambda: value, param)

        with raises(DependencyError):
            assert actual.resolve(dependency, param)

    def test_copy_registers_self(self):
        """copy() should return new Container with same dependencies"""
        actual = self.container.copy()

        assert actual.resolve(Container) == actual

    def test_copy_for_new_dependencies(self, ):
        """dependencies for copied container does not affect parent"""
        self.container.register('value', lambda: 0)

        actual = self.container.copy()
        actual.register('value', lambda: 1)

        assert self.container.resolve('value') == 0
        assert actual.resolve('value') == 1

    @staticmethod
    def test_get_default():
        """get() returns default container"""
        assert Container.get() == Container.get('')

    @staticmethod
    @mark.parametrize('name', ['name', 'another name'])
    def test_get_named(name):
        """get() returns container by name"""
        container = Container(name)

        assert Container.get(name) == container

    @staticmethod
    def test_get_raises():
        """get() should raise DependencyError if container not found"""
        with raises(DependencyError):
            Container.get('some container')


@mark.usefixtures('container_fixture')
class MakeDefaultTests:
    """DefaultContainerContext class tests"""

    @staticmethod
    @mark.parametrize('name', ['container', 'other container'])
    def test_creates_container(name):
        """__init__ should create container with provided name"""
        with make_default(name) as container:
            assert Container.get(name) == container

    @staticmethod
    @mark.parametrize('name', ['container', 'other container'])
    def test_uses_existing_container(name):
        """__init__ should use existing container with provided name"""
        Container(name)
        try:
            with make_default(name):
                pass
        except DependencyError:
            fail()

    @staticmethod
    @mark.parametrize('name', ['container', 'other container'])
    def test_sets_container_default_in_context(name):
        """__enter__ should make container default in context"""
        with make_default(name) as container:
            assert Container.get() == container

    @staticmethod
    @mark.parametrize('previous_name, next_name', [('container', 'other container')])
    def test_restores_previous_default(previous_name, next_name):
        """__exit__ should make previous default container default again"""
        default_container = Container.get()
        with make_default(previous_name) as previous_container:
            with make_default(next_name) as next_container:
                assert Container.get() == next_container
            assert Container.get() == previous_container
        assert Container.get() == default_container
