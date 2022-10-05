#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2022-09-06 08:45:28
@LastEditors    : yanyongyu
@LastEditTime   : 2022-10-05 07:04:20
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

import json
import urllib.parse

from src.plugins.github.utils import get_bot
from src.plugins.github.cache import create_state

from .platform import UserInfo


async def create_install_link(info: UserInfo) -> str:
    query = {"state": await create_state(json.dumps(info))}
    return (
        f"https://github.com/apps/{get_bot()._app_slug}/"
        f"installations/new?{urllib.parse.urlencode(query)}"
    )


async def config_install_link(installation_id: int) -> str:
    return (
        f"https://github.com/apps/{get_bot()._app_slug}/installations/{installation_id}"
    )
