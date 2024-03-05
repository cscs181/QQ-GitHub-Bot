"""
@Author         : yanyongyu
@Date           : 2021-03-13 14:47:28
@LastEditors    : yanyongyu
@LastEditTime   : 2023-10-05 14:46:40
@Description    : Redis provider plugin
@GitHub         : https://github.com/yanyongyu
"""

__author__ = "yanyongyu"

import pickle
from functools import wraps
from datetime import timedelta
from typing import Any, TypeVar, ParamSpec
from collections.abc import Callable, Awaitable

import redis.asyncio as redis
from nonebot import get_plugin_config

from .config import Config

P = ParamSpec("P")
R = TypeVar("R")
C = Callable[P, R]

CACHE_KEY_FORMAT = "cache:{signature}"

redis_config = get_plugin_config(Config)

redis_client = redis.Redis(
    host=redis_config.redis_host,
    port=redis_config.redis_port,
    db=redis_config.redis_db,
    username=redis_config.redis_username,
    password=redis_config.redis_password,
    encoding="utf-8",
    decode_responses=False,
)
"""Redis client"""


def gen_signature(
    func: Callable[..., Any],
    args: tuple[Any, ...],
    kwds: dict[str, Any],
    kwd_mark=(object(),),
) -> int:
    """Generate a signature for a function call."""
    key = [func.__module__, func.__qualname__, *args]
    if kwds:
        key.append(kwd_mark)
        key.extend(iter(kwds.items()))
    return hash(tuple(key))


async def get_cache(sign: str) -> Any:
    """Get function call cache."""
    cache = await redis_client.get(CACHE_KEY_FORMAT.format(signature=sign))
    return pickle.loads(cache) if cache else cache


async def save_cache(sign: str, cache: Any, ex: timedelta | None = None) -> None:
    """Save function call cache."""
    await redis_client.set(
        CACHE_KEY_FORMAT.format(signature=sign), pickle.dumps(cache), ex
    )


def cache(
    ex: timedelta | None = None,
) -> Callable[[Callable[P, Awaitable[R]]], Callable[P, Awaitable[R]]]:
    """A decorator to auto cache function call result."""

    def decorator(func: Callable[P, Awaitable[R]]) -> Callable[P, Awaitable[R]]:
        @wraps(func)
        async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            key = str(gen_signature(func, args, kwargs))
            result = await get_cache(key)
            if not result:
                result = await func(*args, **kwargs)
                await save_cache(key, result, ex)
            return result

        return async_wrapper

    return decorator
