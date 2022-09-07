#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2022-09-06 09:02:27
@LastEditors    : yanyongyu
@LastEditTime   : 2022-09-06 12:21:14
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from nonebot import on_command
from nonebot.log import logger
from nonebot.params import Depends
from nonebot.plugin import PluginMetadata
from nonebot.adapters.github import ActionFailed
from nonebot.adapters.onebot.v11 import GroupMessageEvent, PrivateMessageEvent

from src.plugins.github import config
from src.plugins.github.models import User
from src.plugins.github.utils import get_bot
from src.plugins.github.libs.install import create_install_link

from .dependencies import get_qq_user, get_current_user

__plugin_meta__ = PluginMetadata(
    "GitHub APP 集成",
    "集成 GitHub APP 以进行 Issue、PR 等事件提醒",
    (
        "/install: 安装或管理 GitHub APP 集成\n"
        "/install check: 查看 GitHub APP 集成状态\n"
        "/install revoke: 撤销 GitHub APP 集成授权"
    ),
)


install = on_command("install", priority=config.github_command_priority)


@install.handle()
async def handle_private(event: PrivateMessageEvent):
    await install.finish(
        "请前往以下链接进行安装或管理：\n" + await create_install_link("qq", event.user_id)
    )


@install.handle()
async def handle_group(event: GroupMessageEvent):
    await install.finish("请私聊我并使用 /install 命令进行安装或管理")


install_check = on_command(
    ("install", "check"), priority=config.github_command_priority
)


@install_check.handle()
async def handle_check(user: User = Depends(get_qq_user)):
    pass


@install_check.handle()
async def check_user_installation(user: User = Depends(get_current_user)):
    bot = get_bot()

    try:
        resp = await bot.rest.users.async_get_authenticated()
        resp = await bot.rest.apps.async_get_user_installation(
            username=resp.parsed_data.login
        )
    except ActionFailed as e:
        if e.response.status_code == 401:
            await install_check.finish("你的 GitHub 帐号授权已过期，请使用 /auth 进行刷新")
        logger.opt(exception=e).error(
            f"Failed while getting installation in installation check: {e}"
        )
        await install_check.finish("未知错误发生，请尝试重试或联系管理员")
    except Exception as e:
        logger.opt(exception=e).error(
            f"Failed while getting installation in installation check: {e}"
        )
        await install_check.finish("未知错误发生，请尝试重试或联系管理员")

    data = resp.parsed_data
    repo_selection = data.repository_selection
    if account := data.account:
        gh_user = account.name
        if repo_selection == "selected":
            await install_check.finish(f"{gh_user} 已安装 GitHub APP 并授权了部分仓库")
        else:
            await install_check.finish(f"{gh_user} 已安装 GitHub APP 并授权了所有仓库")
    else:
        if repo_selection == "selected":
            await install_check.finish(f"你已安装 GitHub APP 并授权了部分仓库")
        else:
            await install_check.finish(f"你已安装 GitHub APP 并授权了所有仓库")
