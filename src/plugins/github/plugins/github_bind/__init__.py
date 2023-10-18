"""
@Author         : yanyongyu
@Date           : 2021-03-12 15:03:23
@LastEditors    : yanyongyu
@LastEditTime   : 2023-10-06 17:53:33
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""

__author__ = "yanyongyu"

import re

from nonebot.rule import is_type
from nonebot.matcher import Matcher
from nonebot.adapters import Message
from nonebot import logger, on_command
from nonebot.plugin import PluginMetadata
from nonebot.params import Depends, CommandArg, ArgPlainText
from nonebot.adapters.github import ActionFailed, ActionTimeout

from src.plugins.github import config
from src.plugins.github.models import Group
from src.plugins.github.utils import get_github_bot
from src.providers.platform import GROUP_INFO, GROUP_EVENTS
from src.plugins.github.dependencies import GROUP, BINDED_GROUP
from src.plugins.github.helpers import (
    FULLREPO_REGEX,
    GROUP_SUPERPERM,
    NO_GITHUB_EVENT,
    allow_cancellation,
)

from .dependencies import bypass_update

__plugin_meta__ = PluginMetadata(
    "GitHub 群仓库绑定",
    "群绑定 GitHub 仓库以进行快捷 Issue、PR 相关操作（仅限群管理员）",
    "/bind [owner/repo]: 群查询或绑定 GitHub 仓库（仅仓库安装 APP 后有效）\n"
    "/unbind: 群解绑 GitHub 仓库",
)

bind = on_command(
    "bind",
    is_type(*GROUP_EVENTS) & NO_GITHUB_EVENT,
    permission=GROUP_SUPERPERM,
    priority=config.github_command_priority,
    block=True,
)


@bind.handle()
async def process_arg(matcher: Matcher, arg: Message = CommandArg()):
    if full_name := arg["text"]:
        matcher.set_arg("full_name", full_name)


@bind.handle(parameterless=(Depends(bypass_update),))
async def check_group_exists(group: GROUP):
    if group and group.bind_repo is not None:
        await bind.finish(f"当前已绑定仓库：{group.bind_repo}")


@bind.got(
    "full_name",
    prompt="绑定仓库的全名？(e.g. owner/repo)",
    parameterless=(allow_cancellation("已取消"),),
)
async def process_repo(group_info: GROUP_INFO, full_name: str = ArgPlainText()):
    if not (matched := re.match(f"^{FULLREPO_REGEX}$", full_name)):
        await bind.reject(f"仓库名 {full_name} 不合法！请重新发送或取消")

    bot = get_github_bot()
    owner: str = matched["owner"]
    repo: str = matched["repo"]
    try:
        await bot.rest.apps.async_get_repo_installation(owner=owner, repo=repo)
    except ActionTimeout:
        await bind.finish("GitHub API 超时，请稍后再试")
    except ActionFailed as e:
        if e.response.status_code == 404:
            await bind.reject(f"仓库 {owner}/{repo} 未安装 APP！请重新发送或取消")
        logger.opt(exception=e).error(
            f"Failed while getting repo installation in group bind: {e}"
        )
        await bind.finish("未知错误发生，请尝试重试或联系管理员")
    except Exception as e:
        logger.opt(exception=e).error(
            f"Failed while getting repo installation in group bind: {e}"
        )
        await bind.finish("未知错误发生，请尝试重试或联系管理员")

    try:
        await Group.create_or_update_by_info(group_info, bind_repo=f"{owner}/{repo}")
    except Exception as e:
        logger.opt(exception=e).error(f"Failed while binding group: {e}")
        await bind.finish("未知错误发生，请尝试重试或联系管理员")

    await bind.finish(f"本群成功绑定仓库 {owner}/{repo} ！")


unbind = on_command(
    "unbind",
    is_type(*GROUP_EVENTS) & NO_GITHUB_EVENT,
    permission=GROUP_SUPERPERM,
    priority=config.github_command_priority,
    block=True,
)


@unbind.handle()
async def process_unbind(group: BINDED_GROUP):
    try:
        await group.unbind()
    except Exception as e:
        logger.opt(exception=e).error(f"Failed while unbind group: {e}")
        await unbind.finish("未知错误发生，请尝试重试或联系管理员")

    await unbind.finish("成功解绑仓库！")
