#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2021-03-12 15:36:14
@LastEditors    : yanyongyu
@LastEditTime   : 2021-03-12 15:38:28
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from src.libs.github import Github
from src.libs.github.models import Repository

from .. import github_config as config


async def get_repo(owner: str, repo_name: str) -> Repository:
    if config.github_client_id and config.github_client_secret:
        g = Github(config.github_client_id, config.github_client_secret)
    else:
        g = Github()

    try:
        repo = await g.get_repo(f"{owner}/{repo_name}", False)
    finally:
        await g.close()
    return repo
