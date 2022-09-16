#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2021-03-13 14:47:28
@LastEditors    : yanyongyu
@LastEditTime   : 2022-09-16 05:48:50
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

import pickle
from functools import wraps
from datetime import timedelta
from typing import Any, TypeVar, Callable, Awaitable, ParamSpec

import redis.asyncio as redis
from nonebot import get_driver

from .config import Config

P = ParamSpec("P")
R = TypeVar("R")
C = Callable[P, R]

CACHE_KEY_FORMAT = "cache:{signature}"

redis_config = Config.parse_obj(get_driver().config)

redis_client: "redis.Redis[bytes]" = redis.Redis(
    host=redis_config.redis_host,
    port=redis_config.redis_port,
    db=redis_config.redis_db,
    username=redis_config.redis_username,
    password=redis_config.redis_password,
    encoding="utf-8",
)


def gen_signature(args, kwds, kwd_mark=(object(),)) -> int:
    key = args
    if kwds:
        key += kwd_mark
        for item in kwds.items():
            key += item
    try:
        return hash(key)
    except TypeError:
        return id(key)


async def get_cache(sign: str) -> Any:
    cache = await redis_client.get(CACHE_KEY_FORMAT.format(signature=sign))
    return pickle.loads(cache) if cache else cache


async def save_cache(sign: str, cache: Any, ex: timedelta | None = None) -> None:
    await redis_client.set(
        CACHE_KEY_FORMAT.format(signature=sign), pickle.dumps(cache), ex
    )


def cache(
    ex: timedelta | None = None,
) -> Callable[[Callable[P, Awaitable[R]]], Callable[P, Awaitable[R]]]:
    def decorator(func: Callable[P, Awaitable[R]]) -> Callable[P, Awaitable[R]]:
        @wraps(func)
        async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            key = str(gen_signature(args, kwargs))
            result = await get_cache(key)
            if not result:
                result = await func(*args, **kwargs)
                await save_cache(key, result, ex)
            return result

        return async_wrapper

    return decorator
