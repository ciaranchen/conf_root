from conf_root import ConfRoot


def my_decorator(cls):
    return cls


@ConfRoot().config()
class MyClass:
    name: str = 'abc'


class AnotherClass:
    pass


@my_decorator
class DecoratedClass:
    pass


def my_function():
    pass
