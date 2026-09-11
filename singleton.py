from typing import Any, TypeVar

_T = TypeVar("_T")


class Singleton(type):
    """Metaclass that makes a class a per-class singleton.

    Every ``SomeClass()`` call returns the same instance for the life of the process. The generic ``__call__`` keeps
    ``SomeClass()`` typed as ``SomeClass`` rather than collapsing to ``object``.
    """

    _instances: dict[type, Any] = {}

    def __call__(cls: "type[_T]", *args: Any, **kwargs: Any) -> _T:
        if cls not in Singleton._instances:
            Singleton._instances[cls] = super().__call__(*args, **kwargs)
        return Singleton._instances[cls]
