#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2021-03-09 16:30:16
@LastEditors    : yanyongyu
@LastEditTime   : 2022-09-05 12:19:35
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

import json
import urllib.parse
from typing import Any, Optional

import httpx

from src.plugins.github import config

from .cache import get_state, create_state, delete_state
from .user import USER_DATA, USER_TYPES, create_or_update_user


async def get_auth_link(type: USER_TYPES, user_id: int | str) -> str:
    query = {
        "client_id": config.github_app.client_id,
        "state": await create_state(json.dumps({"type": type, "user_id": user_id})),
    }
    return f"https://github.com/login/oauth/authorize?{urllib.parse.urlencode(query)}"


async def get_state_data(state_id: str) -> dict[str, Any] | None:
    return json.loads(data) if (data := await get_state(state_id)) is not None else None


async def delete_state_data(state_id: str) -> None:
    return await delete_state(state_id)


async def create_auth_user(
    type: USER_TYPES, user_id: int | str, access_token: str
) -> USER_DATA:
    return await create_or_update_user(
        type=type, user_id=user_id, access_token=access_token  # type: ignore
    )


async def get_token_by_code(code: str) -> str:
    async with httpx.AsyncClient() as client:
        data = {
            "client_id": config.github_app.client_id,
            "client_secret": config.github_app.client_secret,
            "code": code,
        }
        headers = {"Accept": "application/json"}
        response = await client.post(
            "https://github.com/login/oauth/access_token",
            json=data,
            headers=headers,
        )
        response.raise_for_status()
        return response.json()["access_token"]
