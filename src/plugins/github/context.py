"""
@Author         : yanyongyu
@Date           : 2023-10-07 17:18:14
@LastEditors    : yanyongyu
@LastEditTime   : 2023-10-07 17:18:14
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""

__author__ = "yanyongyu"

from functools import wraps
from types import TracebackType
from typing import Any, Generic, TypeVar, Callable, ParamSpec, AsyncGenerator

P = ParamSpec("P")
R = TypeVar("R", covariant=True)


class AsyncGeneratorContextManager(Generic[R]):
    def __init__(
        __self,
        __func: Callable[P, AsyncGenerator[R, Any]],
        *args: P.args,
        **kwargs: P.kwargs
    ):
        __self.func = __func
        __self.args = args
        __self.kwargs = kwargs
        __self.gen: AsyncGenerator[R, Any] | None = None

    async def __aenter__(self):
        if self.gen:
            raise RuntimeError("Cannot nest async context managers")

        self.gen = self.func(*self.args, **self.kwargs)
        try:
            return await anext(self.gen)
        except StopAsyncIteration:
            raise RuntimeError("async generator didn't yield") from None

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ):
        if not self.gen:
            raise RuntimeError("Cannot exit unstarted async context manager")

        try:
            if exc_type is None:
                try:
                    await anext(self.gen)
                except StopAsyncIteration:
                    return False
                else:
                    raise RuntimeError("async generator didn't stop")
            else:
                if exc_value is None:
                    exc_value = exc_type()

                try:
                    await self.gen.athrow(exc_type, exc_value, traceback)
                except StopAsyncIteration as exc:
                    return exc is not exc_value
                except RuntimeError as exc:
                    if exc is exc_value:
                        return False
                    if (
                        isinstance(exc_value, (StopIteration, StopAsyncIteration))
                        and exc.__cause__ is exc_value
                    ):
                        return False
                    raise
                except BaseException as exc:
                    if exc is not exc_value:
                        raise
                    return False

                raise RuntimeError("async generator didn't stop after throw()")
        finally:
            self.gen = None


def asynccontextmanager(
    func: Callable[P, AsyncGenerator[R, Any]]
) -> Callable[P, AsyncGeneratorContextManager[R]]:
    @wraps(func)
    def helper(*args: P.args, **kwds: P.kwargs):
        return AsyncGeneratorContextManager(func, *args, **kwds)

    return helper
