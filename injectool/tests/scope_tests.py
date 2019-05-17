from injectool import register_single, inject, resolve
from injectool import Scope, scope, wrap_with_scope, get_container


class ScopeTests:
    @staticmethod
    def test_scope():
        """Scope should use own Container for resolving dependencies"""
        register_single('value', 0)
        with Scope('one'):
            register_single('value', 1)
        with Scope('two'):
            register_single('value', 2)

        with Scope('one'):
            assert resolve('value') == 1
        with Scope('two'):
            assert resolve('value') == 2
        assert resolve('value') == 0

    @staticmethod
    def test_get_current():
        """Scope.get_current() should return current scope"""
        with Scope('one') as one_scope:
            assert one_scope == Scope.get_current()
            with Scope('two') as two_scope:
                assert two_scope == Scope.get_current()
            assert one_scope == Scope.get_current()

    @staticmethod
    def test_get_container():
        """get_container() should return scope container"""
        with Scope('one') as one_scope:
            assert one_scope.get_container() == get_container()
            with Scope('two') as two_scope:
                assert two_scope.get_container() == get_container()
            assert one_scope.get_container() == get_container()

    @staticmethod
    def test_wrap_same_scope():
        """Scope with same key should use same container"""
        with Scope('scope') as outer_scope:
            with Scope('scope') as inner_scope:
                assert outer_scope != inner_scope
                assert outer_scope == Scope.get_current()
                assert outer_scope.get_container() == inner_scope.get_container()

    @staticmethod
    def test_inner_scope():
        """Scope should use own Container for resolving dependencies if used inside other scope"""
        register_single('value', 0)
        with Scope('one'):
            register_single('value', 1)
            with Scope('two'):
                register_single('value', 2)

        with Scope('one'):
            assert resolve('value') == 1
        with Scope('two'):
            assert resolve('value') == 2
        assert resolve('value') == 0


class ScopeDecoratorTests:
    """scope() decorator tests"""

    def test_wraps_in_scope(self):
        """scope decorator should wrap function call with passed scope"""
        register_single('value', 0)
        with Scope('one'):
            register_single('value', 1)
        with Scope('two'):
            register_single('value', 2)

        assert resolve('value') == 0
        assert self._get_one_scope_value() == 1
        assert self._get_two_scope_value() == 2

    @staticmethod
    @scope('one')
    @inject('value')
    def _get_one_scope_value(value=None):
        return value

    @staticmethod
    @scope('two')
    @inject('value')
    def _get_two_scope_value(value=None):
        return value


def test_wrap_with_scope():
    """wrap_with_scope should wrap passed function call with scope"""
    register_single('value', 0)
    with Scope('one'):
        register_single('value', 1)
    with Scope('two'):
        register_single('value', 2)

    one = wrap_with_scope(lambda: resolve('value'), 'one')
    two = wrap_with_scope(lambda: resolve('value'), 'two')

    assert one() == 1
    assert two() == 2


def test_wrap_with_current_scope():
    """wrap_with_scope should wrap passed function call with scope"""
    register_single('value', 0)
    with Scope('one'):
        register_single('value', 1)
        one = wrap_with_scope(lambda: resolve('value'))
    with Scope('two'):
        register_single('value', 2)
        two = wrap_with_scope(lambda: resolve('value'))

    assert one() == 1
    assert two() == 2
