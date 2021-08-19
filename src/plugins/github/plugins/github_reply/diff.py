#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2021-03-26 14:59:59
@LastEditors    : yanyongyu
@LastEditTime   : 2021-08-19 23:09:30
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

import base64

from nonebot import on_command
from nonebot.typing import T_State
from playwright.async_api import TimeoutError
from httpx import HTTPStatusError, TimeoutException
from nonebot.adapters.cqhttp import Bot, MessageEvent, MessageSegment

from ...libs.redis import MessageInfo
from ...utils import send_github_message
from ...libs.issue import get_issue, issue_diff_to_image
from . import config, is_github_reply, KEY_GITHUB_REPLY

# allow using api without token
try:
    from ...libs.auth import get_user_token
except ImportError:
    get_user_token = None

diff = on_command("diff",
                  is_github_reply,
                  priority=config.github_command_priority)
diff.__doc__ = """
/diff
回复机器人一条github pr信息，给出pr diff
"""


@diff.handle()
async def handle_diff(bot: Bot, event: MessageEvent, state: T_State):
    message_info: MessageInfo = state[KEY_GITHUB_REPLY]
    token = None
    if get_user_token:
        token = get_user_token(event.get_user_id())
    try:
        issue_ = await get_issue(message_info.owner, message_info.repo,
                                 message_info.number, token)
    except TimeoutException:
        await diff.finish(f"获取issue数据超时！请尝试重试")
        return
    except HTTPStatusError:
        await diff.finish(f"仓库{message_info.owner}/{message_info.repo}"
                          f"不存在issue#{message_info.number}！")
        return

    try:
        img = await issue_diff_to_image(message_info.owner, message_info.repo,
                                        issue_)
    except TimeoutException:
        await diff.finish(f"获取diff数据超时！请尝试重试")
    except TimeoutError:
        await diff.finish(f"生成图片超时！请尝试重试")
    else:
        if img:
            await send_github_message(
                diff, message_info.owner, message_info.repo,
                message_info.number,
                MessageSegment.image(
                    f"base64://{base64.b64encode(img).decode()}"))
