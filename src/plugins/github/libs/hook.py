#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2021-03-16 00:59:04
@LastEditors    : yanyongyu
@LastEditTime   : 2021-05-22 17:34:51
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

import secrets
import urllib.parse
from typing import List, Union, Optional

from src.libs.github import Github
from src.libs.github.models import Hook, HookConfig, LazyRepository

from .. import github_config as config
from .redis import get_repo_hook, set_repo_hook

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


def create_hook_url(full_name: str) -> str:
    random_string = get_repo_hook(full_name)
    if not random_string:
        random_string = secrets.token_urlsafe(16)
        set_repo_hook(random_string, full_name)
    return urllib.parse.urljoin(
        config.github_self_host, f"/api/github/hooks/{random_string}"  # type: ignore
    )


async def create_hook(
    repo: Union[str, LazyRepository],
    config: Union[dict, HookConfig],
    token: str,
    events: Optional[List[str]] = None,
    active: Optional[bool] = None,
) -> Hook:
    async with Github(token) as g:
        repo = await g.get_repo(repo, True) if isinstance(repo, str) else repo
        config = (
            HookConfig.parse_obj(config) if isinstance(config, dict) else config
        )

        return await repo.create_hook(config, events, active)


async def has_hook(repo: Union[str, LazyRepository], token: str) -> bool:
    async with Github(token) as g:
        repo = await g.get_repo(repo, True) if isinstance(repo, str) else repo

        hooks = await repo.get_hooks()
        return any(
            hook.config.url.startswith(config.github_self_host)  # type: ignore
            for hook in hooks
        )
