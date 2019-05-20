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

    @staticmethod
    @mark.parametrize('dependency, param', [
        ('key', None),
        (get_dependency_key, 'param'),
        (Scope, None)
    ])
    def test_copy(dependency, param):
        """copy() should return new Container with same dependencies"""
        container = Container()
        value = object()
        container.register(dependency, lambda: value, param)

        actual = container.copy()

        assert actual.get(dependency, param) == value

    @staticmethod
    @mark.parametrize('dependency, param', [
        ('key', None),
        (get_dependency_key, 'param'),
        (Scope, None)
    ])
    def test_copy_uses_only_current_dependencies(dependency, param):
        """copy() should return new Container with same dependencies"""
        container = Container()

        actual = container.copy()
        value = object()
        container.register(dependency, lambda: value, param)

        with raises(DependencyError):
            assert actual.get(dependency, param)

    @staticmethod
    def test_copy_registers_self():
        """copy() should return new Container with same dependencies"""
        container = Container()
        actual = container.copy()

        assert actual.get(Container) == actual

    @staticmethod
    def test_copy_for_new_dependencies():
        """dependencies for copied container does not affect parent"""
        container = Container()
        container.register('value', lambda: 0)

        actual = container.copy()
        actual.register('value', lambda: 1)

        assert container.get('value') == 0
        assert actual.get('value') == 1


@mark.parametrize('dependency, key', [
    ('key', 'key'),
    (get_dependency_key, 'get_dependency_key'),
    (Container, 'Container')
])
def test_get_dependency_key(dependency, key):
    """get_dependency_key() should return __name__ for class or function"""
    assert get_dependency_key(dependency) == key
