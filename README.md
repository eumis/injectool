# injectool

[![example branch parameter](https://github.com/eumis/injectool/actions/workflows/ci.yml/badge.svg?branch=dev)](https://github.com/eumis/injectool/actions/workflows/ci.yml?query=branch%3Adev++)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/9945bfa38f9845e68c7dfcd8d02048cb)](https://www.codacy.com/gh/eumis/injectool/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=eumis/injectool&amp;utm_campaign=Badge_Grade)
[![Codacy Badge](https://app.codacy.com/project/badge/Coverage/9945bfa38f9845e68c7dfcd8d02048cb)](https://www.codacy.com/gh/eumis/injectool/dashboard?utm_source=github.com&utm_medium=referral&utm_content=eumis/injectool&utm_campaign=Badge_Coverage)
[![image](https://img.shields.io/pypi/v/injectool.svg)](https://python.org/pypi/injectool)
[![image](https://img.shields.io/pypi/pyversions/injectool.svg)](https://python.org/pypi/injectool)
[![image](https://img.shields.io/pypi/l/injectool.svg)](https://python.org/pypi/injectool)
[![Downloads](https://static.pepy.tech/personalized-badge/injectool?period=total&units=international_system&left_color=grey&right_color=orange&left_text=Downloads)](https://pepy.tech/project/injectool)

Lightweight dependency injection tool.

## Installation

Install using pip:

`pip install injectool`

## How to use

### Injecting

https://github.com/eumis/injectool/blob/dev/injectool/injection.py

#### resolve()
```python
import injectool

instance = injectool.resolve(SomeClass)
function = injectool.resolve(some_function)
value = injectool.resolve('some_value')
```

#### inject decorator

```python
import injectool
from typing import Callable

class DependenciesUser:
    @injectool.inject(instance=SomeClass)
    def __init__(self, instance: SomeClass = injectool.In):
        pass

    @injectool.inject(function=some_function)
    def some_method(self, function: Callable = injectool.In):
        pass

@injectool.inject(value='some_value')
def use_some_value(value: int = injectool.In):
    pass
```

#### dependency decorator

```python
import injectool

@injectool.dependency
def some_function():
    return 'some_function'

def some_function_implementation():
    return 'some_function implementation'

injectool.add_singleton(some_function, some_function_implementation)

value = some_function() # value: some_function implementation
```

### Dependencies

https://github.com/eumis/injectool/blob/dev/injectool/resolvers.py

#### Singleton

```python
import injectool

injectool.add_singleton('some_value', 54)
some_value = injectool.resolve('some_value')

injectool.add_singleton(SomeClass, SomeClassImplementation())
instance: SomeClass = injectool.resolve(SomeClass)
```

#### Type

New instance is created for every resolving.

```python
import injectool

injectool.add_type(SomeClass, SomeClassImplementation)

instance = injectool.resolve(SomeClass)
```

#### Scoped

One instance is created per scope.

```python
import injectool

injectool.add_scoped(SomeClass, SomeClassImplementation)

with injectool.scope():
    instance1: SomeClass = injectool.resolve(SomeClass)

with injectool.scope():
    instance2: SomeClass = injectool.resolve(SomeClass)
```

Dispose method can be passed to add_type method.
The method will be called on closing scope.

```python
import injectool

def dispose(instance: SomeClassImplementation):
    pass

injectool.add_scoped(SomeClass, SomeClassImplementation, dispose)

with injectool.scope():
    injectool.resolve(SomeClass)
```

#### Thread

One instance is created per thread.

```python
import injectool
from threading import Thread
from concurrent.futures.thread import ThreadPoolExecutor

injectool.add_per_thread(SomeClass, SomeClassImplementation)

one = injectool.resolve(SomeClass)

def thread_target():
    two = injectool.resolve(SomeClass)

thread = Thread(target=thread_target)
thread.start()


with ThreadPoolExecutor(max_workers=1) as executor:
    future = executor.submit(injectool.resolve, SomeClass)
    three = future.result()
```

#### Custom resolver

```python
import injectool

injectool.add('some_value', lambda: 54)
some_value = injectool.resolve('some_value')

injectool.add(SomeClass, lambda: SomeClassImplementation())
instance: SomeClass = injectool.resolve(SomeClass)
```

## How it works

All dependencies are stored in **Container**.

Basically Container is just a dictionary with **Dependency** used as a key and **Resolver** used as a value.

Any object can be used as **Dependency**.

**Resolver** is function that returns value for a **Dependency**.

<!-- MARKDOWN-AUTO-DOCS:START (CODE:src=./injectool/core.py&lines=12-37) -->
<!-- The below code snippet is automatically added from ./injectool/core.py -->
```py
Dependency = Any
Resolver = Callable[[], Any]


class Container:
    """Container for dependencies"""

    def __init__(self, resolvers: Optional[Dict[Dependency, Resolver]] = None):
        self._resolvers: Dict[Dependency, Resolver] = {} if resolvers is None else resolvers
        self.set(Container, lambda: self)

    def set(self, dependency: Dependency, resolve: Resolver):
        """Sets resolver for dependency"""
        self._resolvers[dependency] = resolve

    def resolve(self, dependency: Dependency) -> Any:
        """Resolve dependency"""
        resolve = self._resolvers.get(dependency)
        if resolve is None:
            dependency_name = dependency.__name__ if hasattr(dependency, '__name__') else str(dependency)
            raise DependencyError(f'Dependency "{dependency_name}" is not found')
        return resolve()

    def copy(self) -> 'Container':
        """returns new container with same dependencies"""
        return Container(self._resolvers.copy())
```
<!-- MARKDOWN-AUTO-DOCS:END -->

**Default** container is stored as global variable and used by default.
**Default** container can be changed.

<!-- MARKDOWN-AUTO-DOCS:START (CODE:src=./injectool/core.py&lines=40-45) -->
<!-- The below code snippet is automatically added from ./injectool/core.py -->
```py
_DEFAULT_CONTAINER = Container()

def set_default_container(container: Container):
    """Sets default container"""
    global _DEFAULT_CONTAINER
    _DEFAULT_CONTAINER = container
```
<!-- MARKDOWN-AUTO-DOCS:END -->

**Current** container can be set and used temporary.
It's stored in ContextVar so it can be used in asynchronous code.

<!-- MARKDOWN-AUTO-DOCS:START (CODE:src=./injectool/core.py&lines=48-66) -->
<!-- The below code snippet is automatically added from ./injectool/core.py -->
```py
_CURRENT_CONTAINER = ContextVar('dependency_container')

def get_container() -> Container:
    """Returns current container"""
    return _CURRENT_CONTAINER.get(_DEFAULT_CONTAINER)


@contextmanager
def use_container(container: Optional[Container] = None) -> Generator[Container, None, None]:
    """
    Uses passed container for registering and resolving dependencies
    Creates new if container doesn't exist.
    """
    container = container if container else Container()
    reset_token = _CURRENT_CONTAINER.set(container)
    try:
        yield container
    finally:
        _CURRENT_CONTAINER.reset(reset_token)
```
<!-- MARKDOWN-AUTO-DOCS:END -->

## License

[MIT](http://opensource.org/licenses/MIT)

Copyright (c) 2017-present, eumis (Eugen Misievich)
