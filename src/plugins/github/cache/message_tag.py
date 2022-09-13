#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2022-09-13 15:56:01
@LastEditors    : yanyongyu
@LastEditTime   : 2022-09-13 15:58:09
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from datetime import timedelta

from src.plugins.redis import redis_client

MESSAGE_TAG_CACHE_KEY = "cache:github:message:{message_id}:tag"
MESSAGE_TAG_CACHE_EXPIRE = timedelta(minutes=60)


async def create_message_tag(message_id: str, data: str):
    await redis_client.set(
        MESSAGE_TAG_CACHE_KEY.format(message_id),
        data.encode("UTF-8"),
        ex=MESSAGE_TAG_CACHE_EXPIRE,
    )


async def get_message_tag(message_id: str) -> str | None:
    data = await redis_client.get(MESSAGE_TAG_CACHE_KEY.format(message_id))
    return data if data is None else data.decode("UTF-8")
