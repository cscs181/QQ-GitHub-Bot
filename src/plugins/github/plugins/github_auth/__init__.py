#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2021-03-09 16:06:34
@LastEditors    : yanyongyu
@LastEditTime   : 2022-09-06 12:14:08
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from nonebot import on_command
from nonebot.log import logger
from nonebot.params import Depends
from nonebot.typing import T_State
from nonebot.plugin import PluginMetadata
from tortoise.exceptions import DoesNotExist
from nonebot.adapters.github import ActionFailed
from nonebot.adapters.onebot.v11 import (
    MessageEvent,
    GroupMessageEvent,
    PrivateMessageEvent,
)

from src.plugins.github import config
from src.plugins.github.models import User
from src.plugins.github.utils import get_bot
from src.plugins.github.libs.user import get_user
from src.plugins.github.libs.auth import create_auth_link

from .dependencies import get_qq_user, get_current_user

__plugin_meta__ = PluginMetadata(
    "GitHub 帐号授权",
    "绑定并授权 GitHub 帐号以进行 Issue、PR 等操作",
    (
        "/auth: 创建或刷新 GitHub 帐号授权\n"
        "/auth check: 查看 GitHub 帐号授权状态\n"
        "/auth revoke: 撤销 GitHub 帐号授权"
    ),
)

auth = on_command("auth", priority=config.github_command_priority)


@auth.handle()
async def handle_private(event: PrivateMessageEvent):
    await auth.finish("请前往以下链接进行授权：\n" + await create_auth_link("qq", event.user_id))


@auth.handle()
async def handle_group(event: GroupMessageEvent):
    await auth.finish("请私聊我并使用 /auth 命令授权你的 GitHub 账号")


auth_check = on_command(("auth", "check"), priority=config.github_command_priority)


@auth_check.handle()
async def handle_check(user: User = Depends(get_qq_user)):
    pass


@auth_check.handle()
async def check_user_status(user: User = Depends(get_current_user)):
    bot = get_bot()
    with bot.as_oauth_app():
        try:
            resp = await bot.rest.apps.async_check_token(
                client_id=config.github_app.app_id, access_token=user.access_token
            )
        except ActionFailed as e:
            if e.response.status_code == 404:
                await auth_check.finish("你的 GitHub 帐号授权已过期，请使用 /auth 进行刷新")
            logger.opt(exception=e).error(
                f"Failed while checking token in auth check: {e}"
            )
            await auth_check.finish("未知错误发生，请尝试重试或联系管理员")
        except Exception as e:
            logger.opt(exception=e).error(
                f"Failed while checking token in auth check: {e}"
            )
            await auth_check.finish("未知错误发生，请尝试重试或联系管理员")

    if gh_user := resp.parsed_data.user:
        await auth_check.finish(f"你已绑定 GitHub 帐号 {gh_user.login}")
    await auth_check.finish("你已绑定 GitHub 帐号")


auth_revoke = on_command(("auth", "revoke"), priority=config.github_command_priority)


@auth_revoke.handle()
async def handle_revoke(user: User = Depends(get_qq_user)):
    pass


@auth_revoke.handle()
async def revoke_user(user: User = Depends(get_current_user)):
    bot = get_bot()
    with bot.as_oauth_app():
        try:
            await bot.rest.apps.async_delete_token(
                client_id=config.github_app.client_id, access_token=user.access_token
            )
        except Exception as e:
            logger.opt(exception=e).error(
                f"Failed while deleting token in auth revoke: {e}"
            )
            await auth_revoke.finish("未知错误发生，请尝试重试或联系管理员")

    try:
        await user.delete()
    except Exception as e:
        logger.opt(exception=e).error(f"Failed while deleting user in auth revoke: {e}")
        await auth_revoke.finish("未知错误发生，请尝试重试或联系管理员")
    await auth_revoke.finish("你的 GitHub 帐号授权已撤销")
