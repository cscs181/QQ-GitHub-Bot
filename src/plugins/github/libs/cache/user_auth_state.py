#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2022-09-05 11:06:43
@LastEditors    : yanyongyu
@LastEditTime   : 2022-09-05 11:28:29
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from uuid import uuid4
from datetime import timedelta

from src.plugins.redis import redis_client

STATE_CACHE_KEY = "cache:github:auth:state:{state_id}"
STATE_CACHE_EXPIRE = timedelta(minutes=10)


async def create_state(data: str) -> str:
    state_id = uuid4().hex
    await redis_client.set(
        STATE_CACHE_KEY.format(state_id), data.encode("UTF-8"), ex=STATE_CACHE_EXPIRE
    )
    return state_id


async def get_state(state_id: str) -> str | None:
    data = await redis_client.get(STATE_CACHE_KEY.format(state_id))
    return data if data is None else data.decode("UTF-8")


async def delete_state(state_id: str) -> None:
    await redis_client.delete(STATE_CACHE_KEY.format(state_id))
