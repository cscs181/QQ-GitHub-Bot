#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2021-03-09 17:34:53
@LastEditors    : yanyongyu
@LastEditTime   : 2021-03-09 18:36:58
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from typing import Optional


class Requester:

    def __init__(self, token_or_client_id: Optional[str],
                 client_secret: Optional[str], base_url: str, timeout: int,
                 user_agent: str, per_page: int, retry: Optional[int],
                 verify: bool):
        pass
