"""
@Author         : yanyongyu
@Date           : 2021-03-09 16:30:16
@LastEditors    : yanyongyu
@LastEditTime   : 2023-10-05 15:28:06
@Description    : OAuth lib
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

import urllib.parse

from src.plugins.github import config
from src.providers.platform import User
from src.plugins.github.utils import get_github
from src.plugins.github.models import User as UserModel
from src.plugins.github.cache import get_state, create_state, delete_state

from .platform import create_or_update_user


async def create_auth_link(info: User) -> str:
    """Create oauth link"""
    query = {
        "client_id": config.github_app.client_id,
        "state": await create_state(info),
    }
    return f"https://github.com/login/oauth/authorize?{urllib.parse.urlencode(query)}"


async def consume_state(state_id: str) -> User | None:
    """Get oauth state data"""
    if user := await get_state(state_id):
        await delete_state(state_id)
        return user


async def create_auth_user(info: User, access_token: str) -> UserModel:
    """Create oauth user model"""
    return await create_or_update_user(info, access_token=access_token)


async def get_token_by_code(code: str) -> str:
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
    )
    return response.json()["access_token"]
