"""
@Author         : yanyongyu
@Date           : 2022-09-06 09:02:27
@LastEditors    : yanyongyu
@LastEditTime   : 2024-03-05 14:38:05
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""

__author__ = "yanyongyu"

from nonebot import logger, on_command
from nonebot.plugin import PluginMetadata
from nonebot.adapters.github import ActionTimeout
from githubkit.versions.latest.models import SimpleUser

from src.plugins.github import config
from src.providers.platform import USER_INFO
from src.plugins.github.utils import get_github_bot
from src.plugins.github.helpers import NO_GITHUB_EVENT
from src.plugins.github.libs.install import create_install_link
from src.plugins.github.dependencies import (
    RUN_WHEN_GROUP,
    RUN_WHEN_PRIVATE,
    GITHUB_USER_INSTALLATION,
)

__plugin_meta__ = PluginMetadata(
    "GitHub APP 集成",
    "集成 GitHub APP 以进行 Issue、PR 相关事件提醒",
    "/install: 安装或管理 GitHub APP 集成\n"
    "/install check: 查看 GitHub APP 集成状态\n"
    "/install revoke: 撤销 GitHub APP 集成授权",
)


install = on_command(
    "install",
    aliases={"安装"},
    rule=NO_GITHUB_EVENT,
    priority=config.github_command_priority,
    block=True,
)


@install.handle(parameterless=(RUN_WHEN_GROUP,))
async def handle_group():
    await install.finish("请私聊我并使用 /install 命令进行安装或管理")


@install.handle(parameterless=(RUN_WHEN_PRIVATE,))
async def handle_private(user_info: USER_INFO):
    await install.finish(
        "请前往以下链接进行安装或管理：\n" + await create_install_link(user_info)
    )


install_check = on_command(
    ("install", "check"),
    aliases={("安装", "检查")},
    rule=NO_GITHUB_EVENT,
    priority=config.github_command_priority,
    block=True,
)


@install_check.handle()
async def check_user_installation(installation: GITHUB_USER_INSTALLATION):
    # sourcery skip: merge-else-if-into-elif
    repo_selection = installation.repository_selection
    if account := installation.account:
        if isinstance(account, SimpleUser):
            gh_user = account.name or account.login
        else:
            gh_user = account.name or account.slug
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
    ("install", "revoke"),
    aliases={("安装", "撤销")},
    rule=NO_GITHUB_EVENT,
    priority=config.github_command_priority,
    block=True,
)


@install_revoke.handle()
async def revoke_user(installation: GITHUB_USER_INSTALLATION):
    bot = get_github_bot()

    try:
        await bot.rest.apps.async_delete_installation(installation_id=installation.id)
    except ActionTimeout:
        await install_revoke.finish("GitHub API 超时，请稍后再试")
    except Exception as e:
        logger.opt(exception=e).error(
            f"Failed while deleting installation in installation revoke: {e}"
        )
        await install_revoke.finish("未知错误发生，请尝试重试或联系管理员")

    await install_revoke.finish("已移除 GitHub APP 集成")
