"""
@Author         : yanyongyu
@Date           : 2021-03-12 15:03:23
@LastEditors    : yanyongyu
@LastEditTime   : 2023-12-11 13:42:18
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""

__author__ = "yanyongyu"

import re

from nonebot.typing import T_State
from nonebot.matcher import Matcher
from nonebot.adapters import Message
from nonebot import logger, on_command
from nonebot.plugin import PluginMetadata
from nonebot.params import CommandArg, ArgPlainText

from src.plugins.github import config
from src.plugins.github.models import Group
from src.providers.platform import GROUP_INFO
from src.plugins.github.libs.github import FULLREPO_REGEX
from src.plugins.github.helpers import (
    GROUP_SUPERPERM,
    NO_GITHUB_EVENT,
    MATCH_WHEN_GROUP,
)
from src.plugins.github.dependencies import (
    GROUP,
    BINDED_GROUP,
    GITHUB_REPO_INSTALLATION,
    bypass_arg,
    allow_cancellation,
)

__plugin_meta__ = PluginMetadata(
    "GitHub 群仓库绑定",
    "群绑定 GitHub 仓库以进行快捷 Issue、PR 相关操作（仅限群管理员）",
    "/bind [owner/repo]: 群查询或绑定 GitHub 仓库（仅仓库安装 APP 后有效）\n"
    "/unbind: 群解绑 GitHub 仓库",
)

bind = on_command(
    "bind",
    aliases={"绑定"},
    rule=MATCH_WHEN_GROUP & NO_GITHUB_EVENT,
    permission=GROUP_SUPERPERM,
    priority=config.github_command_priority,
    block=True,
)


@bind.handle()
async def process_arg(matcher: Matcher, arg: Message = CommandArg()):
    if full_name := arg.extract_plain_text().strip():
        matcher.set_arg("full_name", arg.__class__(full_name))


@bind.handle(parameterless=(bypass_arg("full_name"),))
async def check_group_exists(group: GROUP):
    if group and group.bind_repo is not None:
        await bind.finish(f"当前已绑定仓库：{group.bind_repo}")


@bind.got(
    "full_name",
    prompt="请发送要绑定的仓库全名，例如：「owner/repo」",
    parameterless=(allow_cancellation("已取消"),),
)
async def process_repo(state: T_State, full_name: str = ArgPlainText()):
    if not (matched := re.match(f"^{FULLREPO_REGEX}$", full_name)):
        await bind.reject(
            f"仓库名 {full_name} 错误！\n请重新发送正确的仓库名，"
            "例如：「owner/repo」\n或发送「取消」以取消"
        )

    state["owner"] = matched["owner"]
    state["repo"] = matched["repo"]


@bind.handle()
async def handle_bind(
    state: T_State, group_info: GROUP_INFO, repo_installation: GITHUB_REPO_INSTALLATION
):
    owner = state["owner"]
    repo = state["repo"]

    try:
        await Group.create_or_update_by_info(group_info, bind_repo=f"{owner}/{repo}")
    except Exception as e:
        logger.opt(exception=e).error(f"Failed while binding group: {e}")
        await bind.finish("未知错误发生，请尝试重试或联系管理员")

    await bind.finish(f"本群成功绑定仓库 {owner}/{repo} ！")


unbind = on_command(
    "unbind",
    aliases={"解绑"},
    rule=MATCH_WHEN_GROUP & NO_GITHUB_EVENT,
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
