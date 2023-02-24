# Changelog

# 3.0.0

- Dependency is used as a key instead of its name
- Added default injection value
- Resolvers are removed
- Added scopes
- Added default container
- Added per thread

## 2.0.4

- fixed typings

## 2.0.3

- fixed passing injected parameters

## 2.0.2

- fixed default container
- container can be injected

## 2.0.1

- current container is stored to context var
- removed container name and storing all containers
- make_default is renamed to use_container
- Resolvers are moved to resolvers module
- added named dependency to @inject

## 1.1.2

- @dependency uses own implementation by default
- add_resolve_function is renamed to add_function_resolver
- SingletonResolver.add_value() is changed to set_value()

## 1.1.1

- add is renamed to add_resolver

## 1.1.0

- Added resolvers
- Added Resolver class. Container is refactored to use Resolver class
- Added multiple containers support(instead of scopes)

## 1.0.1

- Added using functions and classes as keys
- Scopes refactoring

## 1.0.0

- Added Container
- Added scopes
- Added registration and injection
