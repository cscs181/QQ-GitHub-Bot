#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2021-03-09 16:30:16
@LastEditors    : yanyongyu
@LastEditTime   : 2021-03-09 16:32:14
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

import urllib.parse

from .. import github_config as config

assert config.github_client_id and config.github_client_secret and config.github_redirect_uri, "GitHub OAuth Application info not fully provided! OAuth plugin will not work!"


async def get_auth_link(username: str) -> str:
    query = {
        "client_id": config.github_client_id,
        "redirect_uri": config.github_redirect_uri,
        # FIXME: encode username?
        "state": username
    }
    return f"https://github.com/login/oauth/authorize?{urllib.parse.urlencode(query)}"
