#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2021-03-14 10:53:42
@LastEditors    : yanyongyu
@LastEditTime   : 2021-03-14 11:21:05
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from typing import Optional

from .. import redis

REDIS_KEY_FORMAT = "github_bind_{group_id}"


def set_group_bind_repo(group_id: int, full_name: str) -> Optional[bool]:
    return redis.set(REDIS_KEY_FORMAT.format(group_id=group_id), full_name)


def set_group_unbind_repo(group_id: int) -> int:
    return redis.delete(REDIS_KEY_FORMAT.format(group_id=group_id))


def exists_group_bind_repo(group_id: int) -> int:
    return redis.exists(REDIS_KEY_FORMAT.format(group_id=group_id))


def get_group_bind_repo(group_id: int) -> Optional[str]:
    value = redis.get(REDIS_KEY_FORMAT.format(group_id=group_id))
    return value if value is None else value.decode()
