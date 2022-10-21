#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2022-10-18 03:18:14
@LastEditors    : yanyongyu
@LastEditTime   : 2022-10-21 06:46:54
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from nonebot import on_command
from nonebot.log import logger
from nonebot.adapters import Event
from nonebot.params import Depends
from nonebot.typing import T_State
from nonebot.adapters.github import ActionFailed, ActionTimeout

from src.plugins.github import config
from src.plugins.github.models import User
from src.plugins.github.utils import get_bot
from src.plugins.github.helpers import get_platform, get_current_user
from src.plugins.github.libs.message_tag import Tag, RepoTag, create_message_tag

from . import KEY_GITHUB_REPLY
from .dependencies import is_github_reply

unstar = on_command(
    "unstar", is_github_reply, priority=config.github_command_priority, block=True
)


@unstar.handle()
async def handle_noauth(user: None = Depends(get_current_user)):
    await unstar.finish("你还没有绑定 GitHub 帐号，请私聊使用 /install 进行安装")


@unstar.handle()
async def handle_link(
    event: Event, state: T_State, user: User = Depends(get_current_user)
):
    bot = get_bot()
    tag: Tag = state[KEY_GITHUB_REPLY]

    async with bot.as_user(user.access_token):
        # check starred
        message: str | None = None
        try:
            await bot.rest.activity.async_check_repo_is_starred_by_authenticated_user(
                owner=tag.owner, repo=tag.repo
            )
        except ActionTimeout:
            await unstar.finish("GitHub API 超时，请稍后再试")
        except ActionFailed as e:
            if e.response.status_code == 401:
                await unstar.finish("你的 GitHub 帐号授权已过期，请使用 /auth 进行刷新")
            elif e.response.status_code == 403:
                await unstar.finish("权限不足，请尝试使用 /auth 刷新授权")
            elif e.response.status_code != 404:
                logger.opt(exception=e).error(
                    f"Failed while checking repo in unstar: {e}"
                )
                await unstar.finish("未知错误发生，请尝试重试或联系管理员")
            message = f"你还没有为 {tag.owner}/{tag.repo} 点过 star"
        except Exception as e:
            logger.opt(exception=e).error(f"Failed while checking repo in unstar: {e}")
            await unstar.finish("未知错误发生，请尝试重试或联系管理员")

        if message is None:
            try:
                await bot.rest.activity.async_unstar_repo_for_authenticated_user(
                    owner=tag.owner, repo=tag.repo
                )
                message = f"成功为 {tag.owner}/{tag.repo} 取消 star"
            except ActionTimeout:
                await unstar.finish("GitHub API 超时，请稍后再试")
            except ActionFailed as e:
                if e.response.status_code == 403:
                    await unstar.finish(f"权限不足，{tag.owner}/{tag.repo} 未安装 APP")
                elif e.response.status_code == 404:
                    await unstar.finish(f"仓库 {tag.owner}/{tag.repo} 不存在")
                logger.opt(exception=e).error(
                    f"Failed while checking repo in unstar: {e}"
                )
                await unstar.finish("未知错误发生，请尝试重试或联系管理员")
            except Exception as e:
                logger.opt(exception=e).error(
                    f"Failed while checking repo in unstar: {e}"
                )
                await unstar.finish("未知错误发生，请尝试重试或联系管理员")

    result = await unstar.send(message)

    tag = RepoTag(owner=tag.owner, repo=tag.repo, is_receive=False)
    match get_platform(event):
        case "qq":
            if isinstance(result, dict) and "message_id" in result:
                await create_message_tag(
                    {"type": "qq", "message_id": result["message_id"]}, tag
                )
        case _:
            logger.error(f"Unprocessed event type: {type(event)}")
