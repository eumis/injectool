from pytest import raises, mark

from injectool import Container, DependencyError, Scope, get_dependency_key


class ContainerTests:
    """Container class tests"""

    @staticmethod
    @mark.parametrize('dependency, param', [
        ('key', None),
        (get_dependency_key, 'param'),
        (Scope, None)
    ])
    def test_register(dependency, param):
        """Container should register dependencies"""
        container = Container()
        value = object()

        container.register(dependency, lambda: value, param)

        assert container.get(dependency, param) == value

    @staticmethod
    @mark.parametrize('dependency, param', [
        ('key', None),
        (get_dependency_key, 'param'),
        (Scope, None)
    ])
    def test_last_dependency(dependency, param):
        """register() should overwrite dependency"""
        container = Container()
        value = object()
        last_value = object()

        container.register(dependency, lambda: value, param)
        container.register(dependency, lambda: last_value, param)

        assert container.get(dependency, param) == last_value

    @staticmethod
    @mark.parametrize('dependency, resolver, param', [
        ('key', {}, None),
        (get_dependency_key, object(), 'param'),
        (Scope, 2, None)
    ])
    def test_register_raises(dependency, resolver, param):
        """register() should raise error if initializer is not callable"""
        container = Container()
        with raises(DependencyError):
            container.register(dependency, resolver, param)

    @staticmethod
    @mark.parametrize('dependency, param', [
        ('key', None),
        (get_dependency_key, 'param'),
        (Scope, None)
    ])
    def test_get_raises(dependency, param):
        """get() should raise exception for not existent dependency"""
        container = Container()
        with raises(DependencyError):
            container.get(dependency, param)

    @staticmethod
    def test_self_registration():
        """Container should register himself with key "Container"""
        container = Container()

        assert container.get(Container) == container


@mark.parametrize('dependency, key', [
    ('key', 'key'),
    (get_dependency_key, 'get_dependency_key'),
    (Container, 'Container')
])
def test_get_dependency_key(dependency, key):
    """get_dependency_key() should return __name__ for class or function"""
    assert get_dependency_key(dependency) == key
