"""
@Author         : yanyongyu
@Date           : 2022-09-06 08:45:28
@LastEditors    : yanyongyu
@LastEditTime   : 2023-03-31 00:00:00
@Description    : GitHub app installation lib
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

import json
import urllib.parse

from src.plugins.github.cache import create_state
from src.plugins.github.utils import get_github_bot

from .platform import UserInfo


async def create_install_link(info: UserInfo) -> str:
    """Create github app installation link"""
    query = {"state": await create_state(json.dumps(info))}
    return (
        f"https://github.com/apps/{get_github_bot()._app_slug}/"
        f"installations/new?{urllib.parse.urlencode(query)}"
    )


async def config_install_link(installation_id: int) -> str:
    """Create github app installation config link"""
    return f"https://github.com/apps/{get_github_bot()._app_slug}/installations/{installation_id}"
