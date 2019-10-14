from unittest.mock import Mock, call

from pytest import raises, mark, fixture, fail

from injectool import Container, DependencyError
from injectool.core import get_dependency_key, SingletonResolver, FunctionResolver, add_type
from injectool.core import make_default, add_resolver, add_singleton, add_function_resolver, resolve


@mark.parametrize('dependency, key', [
    ('key', 'key'),
    (get_dependency_key, 'get_dependency_key'),
    (Container, 'Container')
])
def test_get_dependency_key(dependency, key):
    """get_dependency_key() should return __name__ for class or function"""
    assert get_dependency_key(dependency) == key


class SingletonResolverTests:
    """Singleton resolver class tests"""

    @staticmethod
    @mark.parametrize('def_value, def_param, value, param', [
        (1, None, 2, SingletonResolver),
        ({}, SingletonResolver, {'key': 1}, None),
        ([], 1, ['value'], 'parameter')
    ])
    def tests_adds_value_for_parameter(def_value, def_param, value, param):
        """should add single value for parameter"""
        resolver = SingletonResolver(def_value, def_param)

        resolver.add_value(value, param)

        assert resolver.resolve(Mock(), def_param) == def_value
        assert resolver.resolve(Mock(), param) == value

    @staticmethod
    @mark.parametrize('value, param', [
        (2, SingletonResolver),
        ({'key': 1}, None),
        (['value'], 'parameter')
    ])
    def tests_add_raises_for_exiting_parameter(value, param):
        """should raise error for adding existing param"""
        resolver = SingletonResolver(value, param)

        with raises(DependencyError):
            resolver.add_value(value, param)

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
        resolver = FunctionResolver(lambda c, p=None: value)

        assert resolver.resolve(container) == value


class TypeResolverTests:
    """Type resolver class tests"""

    @staticmethod
    @mark.parametrize('def_value, def_param, value, param', [
        (1, None, 2, SingletonResolver),
        ({}, SingletonResolver, {'key': 1}, None),
        ([], 1, ['value'], 'parameter')
    ])
    def tests_adds_type_for_parameter(def_value, def_param, value, param):
        """should add single value for parameter"""
        resolver = SingletonResolver(def_value, def_param)

        resolver.add_value(value, param)

        assert resolver.resolve(Mock(), def_param) == def_value
        assert resolver.resolve(Mock(), param) == value

    @staticmethod
    @mark.parametrize('value, param', [
        (2, SingletonResolver),
        ({'key': 1}, None),
        (['value'], 'parameter')
    ])
    def tests_add_raises_for_exiting_parameter(value, param):
        """should raise error for adding existing param"""
        resolver = SingletonResolver(value, param)

        with raises(DependencyError):
            resolver.add_value(value, param)

    @staticmethod
    @mark.parametrize('param', [SingletonResolver, None, 'parameter'])
    def test_resolve_raises_for_unknown_param(param):
        resolver = SingletonResolver()

        with raises(DependencyError):
            resolver.resolve(param)


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
class ContainerAddResolverTests:
    @mark.parametrize('dependency, resolver', [
        ('key', Mock()),
        (get_dependency_key, SingletonResolver),
        (Container, FunctionResolver)
    ])
    def test_add(self, dependency, resolver):
        """Container should set resolver for dependency"""
        self.container.add(dependency, resolver)

        assert self.container.get_resolver(dependency) == resolver

    @mark.parametrize('dependency, resolver, last_resolver', [
        ('key', Mock(), FunctionResolver),
        (get_dependency_key, SingletonResolver, Mock()),
        (Container, FunctionResolver, SingletonResolver)
    ])
    def test_last_resolver(self, dependency, resolver, last_resolver):
        """Container should overwrite resolver for same dependency"""
        self.container.add(dependency, resolver)
        self.container.add(dependency, last_resolver)

        assert self.container.get_resolver(dependency) == last_resolver

    @mark.parametrize('dependency', ['key', get_dependency_key, Container])
    def test_get_resolver_returns_none(self, dependency):
        """get_resolver() should return none for not existent dependency"""
        assert self.container.get_resolver(dependency) is None


@mark.usefixtures('container_fixture')
class ContainerResolveTests:
    @mark.parametrize('dependency, param', [
        ('key', None),
        (get_dependency_key, 'param'),
        (Container, None)
    ])
    def test_resolve_uses_resolver(self, dependency, param):
        """resolve() should return resolver result"""
        result = Mock()
        resolver = Mock(resolve=Mock())
        resolver.resolve.side_effect = lambda c, p: result
        self.container.add(dependency, resolver)

        actual = self.container.resolve(dependency, param)

        assert resolver.resolve.call_args == call(self.container, param)
        assert actual == result

    @mark.parametrize('dependency', ['key', get_dependency_key, Container])
    def test_resolve_raises(self, dependency):
        """resolve() should raise exception for not existent dependency"""
        with raises(DependencyError):
            self.container.resolve(dependency)


@mark.usefixtures('container_fixture')
class ContainerCopyTests:
    @mark.parametrize('dependency, value', [
        ('key', lambda: None),
        (get_dependency_key, 1),
        (Container, 'value')
    ])
    def test_copy(self, dependency, value):
        """copy() should return new Container with same dependencies"""
        self.container.add(dependency, SingletonResolver(value))

        actual = self.container.copy()

        assert actual.resolve(dependency) == value

    @staticmethod
    @mark.parametrize('source_name, expected_name', [
        ('', '_copy'),
        ('name', 'name_copy'),
        ('another name', 'another name_copy')
    ])
    def test_copy_sets_name(source_name, expected_name):
        """copy() should return new Container with same dependencies"""
        container = Container.get() if source_name == '' else Container(source_name)

        actual = container.copy()

        assert actual.name == expected_name

    @mark.parametrize('name', ['name', 'another name'])
    def test_copy_sets_passed_name(self, name):
        """copy() should return new Container with same dependencies"""
        actual = self.container.copy(name)

        assert actual.name == name

    @mark.parametrize('dependency, value', [
        ('key', lambda: None),
        (get_dependency_key, 1),
        (Container, 'value')
    ])
    def test_copy_uses_only_current_dependencies(self, dependency, value):
        """copy() should return new Container with same dependencies"""
        copy = self.container.copy()

        self.container.add(dependency, SingletonResolver(value))

        with raises(DependencyError):
            assert copy.resolve(dependency)

    def test_copy_for_new_dependencies(self):
        """dependencies for copied container does not affect parent"""
        self.container.add('value', SingletonResolver(0))
        copy = self.container.copy()

        copy.add('value', SingletonResolver(1))

        assert self.container.resolve('value') == 0
        assert copy.resolve('value') == 1


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


@mark.parametrize('dependency, resolver', [
    ('key', FunctionResolver(lambda: 'value')),
    (get_dependency_key, SingletonResolver(1)),
    (Container, Mock())
])
def test_add_resolver(dependency, resolver):
    """add_resolver() should add dependency resolver to current container"""
    with make_default('test_add') as container:
        add_resolver(dependency, resolver)

        assert container.get_resolver(dependency) == resolver


@mark.parametrize('dependency, value', [
    ('key', lambda c, param=None: 'value'),
    (get_dependency_key, 1),
    (Container, Mock())
])
def test_add_singleton(dependency, value):
    """add_singleton() should add SingletonResolver to current container"""
    with make_default('test_add_singleton') as container:
        add_singleton(dependency, value)

        resolver = container.get_resolver(dependency)
        assert isinstance(resolver, SingletonResolver)
        assert resolver.resolve(container) == value


@mark.parametrize('dependency, function', [
    ('key', lambda c, p=None: 'value'),
    (get_dependency_key, lambda c, p=None: 1)
])
def test_add_function_resolver(dependency, function):
    """should add FunctionResolver to current container"""
    with make_default('test_add_resolve_function') as container:
        add_function_resolver(dependency, function)

        resolver = container.get_resolver(dependency)
        assert isinstance(resolver, FunctionResolver)
        assert resolver.resolve(container) == function(container)


class TestType:
    pass


@mark.parametrize('dependency, type_', [
    (TestType, TestType)
])
def test_add_type(dependency, type_):
    """add_type() should add type resolver to current container"""
    with make_default('test_add_resolve_function') as container:
        add_type(dependency, TestType)
        resolver = container.get_resolver(dependency)

        actual = resolver.resolve(container)

        assert isinstance(actual, type_)


@mark.parametrize('dependency, resolver', [
    ('key', FunctionResolver(lambda c, param=None: 'value')),
    (get_dependency_key, SingletonResolver(1))
])
def test_resolve(dependency, resolver):
    """resolve() should resolve dependency using current container"""
    with make_default('test_resolve') as container:
        add_resolver(dependency, resolver)

        assert resolve(dependency) == container.resolve(dependency)
