from injectool import register_single, inject
from injectool.scope import Scope, scope, wrap_with_scope, get_container, get_scope


class ScopeTests:
    def test_scope(self):
        """Scope should use own Container for resolving dependencies"""
        register_single('value', 0)
        with Scope('one'):
            register_single('value', 1)
        with Scope('two'):
            register_single('value', 2)

        with Scope('one'):
            assert self._get_injected_value() == 1
        with Scope('two'):
            assert self._get_injected_value() == 2
        assert self._get_injected_value() == 0

    @staticmethod
    def test_get_current_scope():
        """Scope should use own Container for resolving dependencies"""
        with Scope('one') as one_scope:
            assert one_scope == get_scope()
            with Scope('two') as two_scope:
                assert two_scope == get_scope()
            assert one_scope == get_scope()

    @staticmethod
    def test_get_scope():
        """get_scope() should return current scope"""
        with Scope('one') as one_scope:
            assert one_scope == get_scope()
            with Scope('two') as two_scope:
                assert two_scope == get_scope()
            assert one_scope == get_scope()

    @staticmethod
    def test_get_container():
        """get_container() should return container from current scope"""
        with Scope('one') as one_scope:
            assert one_scope.container == get_container()
            with Scope('two') as two_scope:
                assert two_scope.container == get_container()
            assert one_scope.container == get_container()

    @staticmethod
    def test_wrap_same_scope():
        with Scope('scope') as outer_scope:
            with Scope('scope') as inner_scope:
                assert outer_scope != inner_scope
                assert outer_scope == get_scope()
                assert outer_scope.container == inner_scope.container

    def test_inner_scope(self):
        """Scope should use own Container for resolving dependencies if used inside other scope"""
        register_single('value', 0)
        with Scope('one'):
            register_single('value', 1)
            with Scope('two'):
                register_single('value', 2)

        with Scope('one'):
            assert self._get_injected_value() == 1
        with Scope('two'):
            assert self._get_injected_value() == 2
        assert self._get_injected_value() == 0

    @staticmethod
    @inject('value')
    def _get_injected_value(value=None):
        return value

    def test_scope_decorator(self):
        """scope decorator should wrap function call with passed scope"""
        register_single('value', 0)
        with Scope('one'):
            register_single('value', 1)
        with Scope('two'):
            register_single('value', 2)

        assert self._get_injected_value() == 0
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

    def test_wrap_with_scope(self):
        """wrap_with_scope should wrap passed function call with scope"""
        register_single('value', 0)
        with Scope('one'):
            register_single('value', 1)
        with Scope('two'):
            register_single('value', 2)

        one = wrap_with_scope(self._get_injected_value, 'one')
        two = wrap_with_scope(self._get_injected_value, 'two')

        assert one() == 1
        assert two() == 2

    def test_wrap_with_current_scope(self):
        """wrap_with_scope should wrap passed function call with scope"""
        register_single('value', 0)
        with Scope('one'):
            register_single('value', 1)
            one = wrap_with_scope(self._get_injected_value)
        with Scope('two'):
            register_single('value', 2)
            two = wrap_with_scope(self._get_injected_value)

        assert one() == 1
        assert two() == 2
