from concurrent.futures.thread import ThreadPoolExecutor
from unittest.mock import Mock, call

from pytest import mark, fixture

from injectool.core import get_dependency_key, Container, resolve, use_container
from injectool.resolvers import DependencyScope, add_per_thread, add_scoped, add_singleton, add_type


class SomeClass:
    pass


@fixture
def container_fixture(request):
    with use_container() as container:

        request.cls.container = container

        yield container


@mark.parametrize('dependency, value', [
    ('key', lambda _: 'value'),
    (get_dependency_key, 1),
    (Container, Mock()),
    (SomeClass, SomeClass())
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


@mark.usefixtures(container_fixture.__name__)
class ScopesTests:
    """Scopes tests"""

    container: Container

    @mark.parametrize('dependency, type_', [
        (Mock, Mock),
        (Container, Container)
    ])
    def test_add_scoped(self, dependency, type_):
        """should use single instance for container without scope"""
        add_scoped(dependency, type_)

        with DependencyScope():
            outer = resolve(dependency)
            with DependencyScope():
                actual = resolve(dependency)

                assert isinstance(actual, type_)
                assert actual is resolve(dependency)
                assert actual != outer

    @mark.parametrize('dependency, type_', [
        (Mock, Mock),
        (Container, Container),
        (SomeClass, SomeClass)
    ])
    def test_add_scoped_default(self, dependency, type_):
        """should use single instance for container without scope"""
        add_scoped(dependency, type_)

        actual = resolve(dependency)

        assert isinstance(actual, type_)
        assert actual is resolve(dependency)

    @mark.parametrize('dependency, type_', [
        (Mock, Mock),
        (Container, Container),
        (SomeClass, SomeClass)
    ])
    def test_add_scoped_dispose(self, dependency, type_):
        """should call dispose when scope is closed"""
        dispose = Mock()
        add_scoped(dependency, type_, dispose)

        with DependencyScope():
            one = resolve(dependency)
            with DependencyScope():
                two = resolve(dependency)

        assert dispose.call_args_list[0] == call(two)
        assert dispose.call_args_list[1] == call(one)


@mark.usefixtures(container_fixture.__name__)
class ThreadTests:
    """Thread resolver tests"""

    container: Container

    @mark.parametrize('dependency, type_', [
        (Mock, Mock),
        (Container, Container),
        (SomeClass, SomeClass)
    ])
    def test_add_per_thread_instance_per_thread(self, dependency, type_):
        """should return instance of passed type per thread"""
        add_per_thread(dependency, type_)

        one = resolve(dependency)
        two = resolve(dependency)

        assert isinstance(one, type_)
        assert one is two


    @mark.parametrize('dependency, type_', [
        (Mock, Mock),
        (Container, Container),
        (SomeClass, SomeClass)
    ])
    def test_add_per_thread_instances(self, dependency, type_):
        """should return instance per thread"""
        add_per_thread(dependency, type_)
        one = resolve(dependency)

        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(self.container.resolve, dependency)
            two = future.result()

        assert one != two
