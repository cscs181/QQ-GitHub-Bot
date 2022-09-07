#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2021-03-09 16:30:16
@LastEditors    : yanyongyu
@LastEditTime   : 2022-09-06 12:05:58
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

import json
import urllib.parse
from typing import TypedDict, overload

from src.plugins.github import config
from src.plugins.github.models import User
from src.plugins.github.utils import get_github

from .cache import get_state, create_state, delete_state
from .user import (
    USER_TYPES,
    USER_STRING_TYPES,
    USER_INTEGER_TYPES,
    create_or_update_user,
)


class StateData(TypedDict):
    type: USER_TYPES
    user_id: int | str


@overload
async def create_auth_link(type: USER_INTEGER_TYPES, user_id: int) -> str:
    ...


@overload
async def create_auth_link(type: USER_STRING_TYPES, user_id: str) -> str:
    ...


async def create_auth_link(type: USER_TYPES, user_id: int | str) -> str:
    query = {
        "client_id": config.github_app.client_id,
        "state": await create_state(json.dumps(StateData(type=type, user_id=user_id))),
    }
    return f"https://github.com/login/oauth/authorize?{urllib.parse.urlencode(query)}"


async def get_state_data(state_id: str) -> StateData | None:
    return json.loads(data) if (data := await get_state(state_id)) is not None else None


async def delete_state_data(state_id: str) -> None:
    return await delete_state(state_id)


@overload
async def create_auth_user(
    type: USER_INTEGER_TYPES, user_id: int, access_token: str
) -> User:
    ...


@overload
async def create_auth_user(
    type: USER_STRING_TYPES, user_id: str, access_token: str
) -> User:
    ...


async def create_auth_user(
    type: USER_TYPES, user_id: int | str, access_token: str
) -> User:
    return await create_or_update_user(
        type=type, user_id=user_id, access_token=access_token  # type: ignore
    )


async def get_token_by_code(code: str) -> str:
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
