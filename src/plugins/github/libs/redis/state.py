#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2021-03-23 00:19:12
@LastEditors    : yanyongyu
@LastEditTime   : 2021-03-23 00:19:53
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from typing import Optional
from datetime import timedelta

from . import redis

USER_STATE_FORMAT = "github_state_{state}"


def set_state_bind_user(user_id: str, state: int) -> Optional[bool]:
    return redis.set(USER_STATE_FORMAT.format(state=state), user_id, timedelta(minutes=5))


def get_state_bind_user(state: int) -> Optional[str]:
    value = redis.get(USER_STATE_FORMAT.format(state=state))
    return value if value is None else value.decode()
