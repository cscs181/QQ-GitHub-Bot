#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2021-03-23 00:17:23
@LastEditors    : yanyongyu
@LastEditTime   : 2022-09-02 11:25:09
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from typing import Optional

from src.plugins.redis_provider import redis_client as redis

GITHUB_BIND_FORMAT = "github_bind_{group_id}"


async def set_group_bind_repo(group_id: str, full_name: str) -> Optional[bool]:
    return await redis.set(GITHUB_BIND_FORMAT.format(group_id=group_id), full_name)


async def delete_group_bind_repo(group_id: str) -> int:
    return await redis.delete(GITHUB_BIND_FORMAT.format(group_id=group_id))


async def exists_group_bind_repo(group_id: str) -> int:
    return await redis.exists(GITHUB_BIND_FORMAT.format(group_id=group_id))


async def get_group_bind_repo(group_id: str) -> Optional[str]:
    value = await redis.get(GITHUB_BIND_FORMAT.format(group_id=group_id))
    return value if value is None else value.decode()
