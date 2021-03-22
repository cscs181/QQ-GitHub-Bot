#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2021-03-23 00:17:23
@LastEditors    : yanyongyu
@LastEditTime   : 2021-03-23 00:38:10
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from typing import Optional

from . import redis

GITHUB_BIND_FORMAT = "github_bind_{group_id}"


def set_group_bind_repo(group_id: str, full_name: str) -> Optional[bool]:
    return redis.set(GITHUB_BIND_FORMAT.format(group_id=group_id), full_name)


def delete_group_bind_repo(group_id: str) -> int:
    return redis.delete(GITHUB_BIND_FORMAT.format(group_id=group_id))


def exists_group_bind_repo(group_id: str) -> int:
    return redis.exists(GITHUB_BIND_FORMAT.format(group_id=group_id))


def get_group_bind_repo(group_id: str) -> Optional[str]:
    value = redis.get(GITHUB_BIND_FORMAT.format(group_id=group_id))
    return value if value is None else value.decode()
