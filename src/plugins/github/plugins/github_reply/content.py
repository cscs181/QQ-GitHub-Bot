#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2021-03-26 14:45:05
@LastEditors    : yanyongyu
@LastEditTime   : 2021-08-19 23:19:21
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

import base64

from nonebot import on_command
from nonebot.typing import T_State
from playwright.async_api import Error
from httpx import HTTPStatusError, TimeoutException
from nonebot.adapters.cqhttp import Bot, MessageEvent, MessageSegment

from ...libs.redis import MessageInfo
from ...utils import send_github_message
from ...libs.issue import get_issue, issue_to_image
from . import KEY_GITHUB_REPLY, config, is_github_reply

# allow using api without token
try:
    from ...libs.auth import get_user_token
except ImportError:
    get_user_token = None

content = on_command("content", is_github_reply, priority=config.github_command_priority)
content.__doc__ = """
/content
回复机器人一条github信息，给出对应内容
"""


@content.handle()
async def handle_content(bot: Bot, event: MessageEvent, state: T_State):
    message_info: MessageInfo = state[KEY_GITHUB_REPLY]
    token = None
    if get_user_token:
        token = get_user_token(event.get_user_id())
    try:
        issue_ = await get_issue(
            message_info.owner, message_info.repo, message_info.number, token
        )
    except TimeoutException:
        await content.finish(f"获取issue数据超时！请尝试重试")
        return
    except HTTPStatusError:
        await content.finish(
            f"仓库{message_info.owner}/{message_info.repo}"
            f"不存在issue#{message_info.number}！"
        )
        return

    try:
        img = await issue_to_image(message_info.owner, message_info.repo, issue_)
    except TimeoutException:
        await content.finish(f"获取issue数据超时！请尝试重试")
    except Error:
        await content.finish(f"生成图片超时！请尝试重试")
    else:
        if img:
            await send_github_message(
                content,
                message_info.owner,
                message_info.repo,
                message_info.number,
                MessageSegment.image(f"base64://{base64.b64encode(img).decode()}"),
            )
