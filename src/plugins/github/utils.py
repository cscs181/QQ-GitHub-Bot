#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2022-09-07 12:14:14
@LastEditors    : yanyongyu
@LastEditTime   : 2022-11-07 05:50:50
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

import nonebot
from githubkit import GitHub
from nonebot.adapters.github import GitHubBot
from nonebot.adapters.onebot.v11 import Bot as QQBot

from . import config


def get_github_bot() -> GitHubBot:
    return nonebot.get_bot(config.github_app.app_id)  # type: ignore


def get_github() -> GitHub:
    return get_github_bot().github


def get_qq_bot() -> QQBot:
    return next(bot for bot in nonebot.get_bots().values() if isinstance(bot, QQBot))


def get_qqguild_bot():
    ...
