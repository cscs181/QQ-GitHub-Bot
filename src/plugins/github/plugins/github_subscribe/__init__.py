#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2022-10-22 14:35:43
@LastEditors    : yanyongyu
@LastEditTime   : 2022-10-26 15:40:03
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from nonebot import on_command
from nonebot.matcher import Matcher
from nonebot.adapters import Message
from nonebot.plugin import PluginMetadata
from nonebot.params import Depends, CommandArg

from src.plugins.github import config
from src.plugins.github.models import GroupSubscription

from .dependencies import bypass_create, list_current_subscriptions

__plugin_meta__ = PluginMetadata(
    "GitHub 事件订阅",
    "订阅 GitHub 仓库事件",
    (
        "/subscribe [owner/repo]: 查看指定当前已有订阅\n"
        "/subscribe owner/repo [event/action ...]: 订阅指定仓库的某类事件\n"
        "/unsubscribe owner/repo [event/action ...]: 取消订阅指定仓库的某类事件"
    ),
)

subscribe = on_command("subscribe", priority=config.github_command_priority)


@subscribe.handle()
async def process_arg(matcher: Matcher, arg: Message = CommandArg()):
    if args := arg.extract_plain_text().split(" "):
        repo, *events = args
        matcher.set_arg("full_name", arg.__class__(repo))
        if events:
            matcher.set_arg("events", arg.__class__(" ".join(events)))


@subscribe.handle(parameterless=(Depends(bypass_create),))
async def list_subscription(
    subsciptions: list[GroupSubscription] = Depends(list_current_subscriptions),
):
    if subsciptions:
        await subscribe.finish()
