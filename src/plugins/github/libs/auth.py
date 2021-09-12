#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2021-03-09 16:30:16
@LastEditors    : yanyongyu
@LastEditTime   : 2021-03-23 00:35:49
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

import random
import urllib.parse
from typing import Optional

import httpx

from .. import github_config as config
from .redis import get_user_token as _get_user_token
from .redis import set_user_token as _set_user_token
from .redis import get_state_bind_user, set_state_bind_user

try:
    assert (
        config.github_client_id
        and config.github_client_secret
        and config.github_self_host
    )
except AssertionError:
    raise ImportError(
        "GitHub OAuth Application info not fully provided! OAuth plugin will not work!"
    )


def _encode_state(username: str) -> str:
    state_seq = random.randint(0xFFFF, 0xFFFFFFFF)
    set_state_bind_user(username, state_seq)
    return str(state_seq)


def _decode_state(state: str) -> Optional[str]:
    return get_state_bind_user(int(state))


def get_auth_link(username: str) -> str:
    query = {
        "client_id": config.github_client_id,
        "redirect_uri": urllib.parse.urljoin(
            config.github_self_host, "/api/github/auth"  # type: ignore
        ),
        "scope": "admin:repo_hook,repo",
        "state": _encode_state(username),
    }
    return f"https://github.com/login/oauth/authorize?{urllib.parse.urlencode(query)}"


async def get_token_by_code(code: str) -> str:
    async with httpx.AsyncClient() as client:
        headers = {"Accept": "application/json"}
        data = {
            "client_id": config.github_client_id,
            "client_secret": config.github_client_secret,
            "code": code,
        }
        response = await client.post(
            "https://github.com/login/oauth/access_token", json=data, headers=headers
        )
        response.raise_for_status()
        return response.json()["access_token"]


def set_user_token(username: str, token: str):
    return _set_user_token(username, token)


def get_user_token(username: str) -> Optional[str]:
    return _get_user_token(username)
