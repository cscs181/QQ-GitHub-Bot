#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2021-03-11 17:04:52
@LastEditors    : yanyongyu
@LastEditTime   : 2021-03-11 17:08:11
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from . import BaseModel


class IssuePullRequest(BaseModel):
    url: str
    html_url: str
    diff_url: str
    patch_url: str
