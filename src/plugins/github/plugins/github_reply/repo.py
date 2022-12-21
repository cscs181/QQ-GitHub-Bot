#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2022-10-21 01:30:44
@LastEditors    : yanyongyu
@LastEditTime   : 2022-12-21 19:56:17
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from nonebot import on_command
from nonebot.typing import T_State

from src.plugins.github import config
from src.plugins.github.libs.message_tag import Tag
from src.plugins.github.helpers import NO_GITHUB_EVENT

from . import KEY_GITHUB_REPLY
from .dependencies import is_github_reply

repo = on_command(
    "repo",
    rule=NO_GITHUB_EVENT & is_github_reply,
    priority=config.github_command_priority,
    block=True,
)


@repo.handle()
async def handle_content(state: T_State):
    tag: Tag = state[KEY_GITHUB_REPLY]
    await repo.finish(f"https://github.com/{tag.owner}/{tag.repo}")
