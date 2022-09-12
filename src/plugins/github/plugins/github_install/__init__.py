#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2022-09-06 09:02:27
@LastEditors    : yanyongyu
@LastEditTime   : 2022-09-12 08:36:41
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from nonebot import on_command
from nonebot.log import logger
from nonebot.params import Depends
from githubkit.rest import Installation
from nonebot.plugin import PluginMetadata
from nonebot.adapters.github import ActionFailed
from nonebot.adapters.onebot.v11 import GroupMessageEvent, PrivateMessageEvent

from src.plugins.github import config
from src.plugins.github.models import User
from src.plugins.github.utils import get_bot
from src.plugins.github.helpers import get_current_user
from src.plugins.github.libs.install import create_install_link

from .dependencies import get_user_installation

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
async def handle_check(user: None = Depends(get_current_user)):
    await install_check.finish("你还没有绑定 GitHub 帐号，请使用 /install 进行安装")


@install_check.handle()
async def check_user_installation(
    installation: Installation = Depends(get_user_installation),
):
    # sourcery skip: merge-else-if-into-elif
    repo_selection = installation.repository_selection
    if account := installation.account:
        gh_user = account.name
        if repo_selection == "selected":
            await install_check.finish(f"{gh_user} 已安装 GitHub APP 并授权了部分仓库")
        else:
            await install_check.finish(f"{gh_user} 已安装 GitHub APP 并授权了所有仓库")
    else:
        if repo_selection == "selected":
            await install_check.finish("你已安装 GitHub APP 并授权了部分仓库")
        else:
            await install_check.finish("你已安装 GitHub APP 并授权了所有仓库")


install_revoke = on_command(
    ("install", "revoke"), priority=config.github_command_priority
)


@install_revoke.handle()
async def handle_revoke(user: None = Depends(get_current_user)):
    await install_check.finish("你还没有绑定 GitHub 帐号，请使用 /install 进行安装")


@install_revoke.handle()
async def revoke_user(installation: Installation = Depends(get_user_installation)):
    bot = get_bot()

    try:
        await bot.rest.apps.async_delete_installation(installation.id)
    except Exception as e:
        logger.opt(exception=e).error(
            f"Failed while deleting installation in installation revoke: {e}"
        )
