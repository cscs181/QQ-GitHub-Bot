"""
@Author         : yanyongyu
@Date           : 2021-03-09 16:30:16
@LastEditors    : yanyongyu
@LastEditTime   : 2024-05-16 18:03:01
@Description    : OAuth lib
@GitHub         : https://github.com/yanyongyu
"""

__author__ = "yanyongyu"

import urllib.parse

from src.plugins.github import config
from src.plugins.github.models import User
from src.providers.platform import UserInfo
from src.plugins.github.utils import get_github
from src.plugins.github.cache import get_state, create_state, delete_state


async def create_auth_link(info: UserInfo) -> str:
    """Create oauth link"""
    query = {
        "client_id": config.github_app.client_id,
        "state": await create_state(info),
    }
    return f"https://github.com/login/oauth/authorize?{urllib.parse.urlencode(query)}"


async def consume_state(state_id: str) -> UserInfo | None:
    """Get oauth state data"""
    if user := await get_state(state_id):
        await delete_state(state_id)
        return user


async def create_auth_user(info: UserInfo, access_token: str) -> User:
    """Create oauth user model"""
    return await User.create_or_update_by_info(info, access_token=access_token)


async def get_token_by_code(code: str) -> str | None:
    """Get oauth token by oauth code"""
    github = get_github()
    data = {
        "client_id": config.github_app.client_id,
        "client_secret": config.github_app.client_secret,
        "code": code,
    }
    headers = {"Accept": "application/json"}
    response = await github.arequest(
        "POST",
        "https://github.com/login/oauth/access_token",
        json=data,
        headers=headers,
    )  # type: ignore
    data = response.json()
    return data.get("access_token")
