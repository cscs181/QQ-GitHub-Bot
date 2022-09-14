#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2022-09-06 08:45:28
@LastEditors    : yanyongyu
@LastEditTime   : 2022-09-14 06:05:47
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

import json
import urllib.parse
from typing import overload

from src.plugins.github.utils import get_bot
from src.plugins.github.cache import create_state

from .auth import StateData
from .platform import PLATFORMS, USER_STRING_TYPES, USER_INTEGER_TYPES


@overload
async def create_install_link(type: USER_INTEGER_TYPES, user_id: int) -> str:
    ...


@overload
async def create_install_link(type: USER_STRING_TYPES, user_id: str) -> str:
    ...


async def create_install_link(type: PLATFORMS, user_id: int | str) -> str:
    query = {
        "state": await create_state(json.dumps(StateData(type=type, user_id=user_id))),
    }
    return f"https://github.com/apps/{get_bot().app_slug}/installations/new?{urllib.parse.urlencode(query)}"


async def config_install_link(installation_id: int) -> str:
    return (
        f"https://github.com/apps/{get_bot().app_slug}/installations/{installation_id}"
    )
