"""
@Author         : yanyongyu
@Date           : 2021-03-09 16:06:34
@LastEditors    : yanyongyu
@LastEditTime   : 2023-11-25 17:10:37
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""

__author__ = "yanyongyu"

from nonebot import logger, on_command
from nonebot.plugin import PluginMetadata
from nonebot.adapters.github import ActionFailed, ActionTimeout

from src.plugins.github import config
from src.providers.platform import USER_INFO
from src.plugins.github.utils import get_github_bot
from src.plugins.github.helpers import NO_GITHUB_EVENT
from src.plugins.github.libs.auth import create_auth_link
from src.plugins.github.dependencies import (
    RUN_WHEN_GROUP,
    AUTHORIZED_USER,
    RUN_WHEN_PRIVATE,
)

__plugin_meta__ = PluginMetadata(
    "GitHub 帐号授权",
    "绑定并授权 GitHub 帐号以进行 Issue、PR 相关操作",
    "/auth: 创建或刷新 GitHub 帐号授权\n"
    "/auth check: 查看 GitHub 帐号授权状态\n"
    "/auth revoke: 撤销 GitHub 帐号授权",
)

auth = on_command(
    "auth",
    aliases={"授权"},
    rule=NO_GITHUB_EVENT,
    priority=config.github_command_priority,
    block=True,
)


@auth.handle(parameterless=(RUN_WHEN_GROUP,))
async def handle_group():
    await auth.finish("请私聊我并使用 /auth 命令授权你的 GitHub 账号")


@auth.handle(parameterless=(RUN_WHEN_PRIVATE,))
async def handle_private(user_info: USER_INFO):
    await auth.finish("请前往以下链接进行授权：\n" + await create_auth_link(user_info))


auth_check = on_command(
    ("auth", "check"),
    aliases={("授权", "检查")},
    rule=NO_GITHUB_EVENT,
    priority=config.github_command_priority,
    block=True,
)


@auth_check.handle()
async def check_user_status(user: AUTHORIZED_USER):
    bot = get_github_bot()
    async with bot.as_oauth_app():
        try:
            resp = await bot.rest.apps.async_check_token(
                client_id=config.github_app.client_id, access_token=user.access_token
            )
        except ActionTimeout:
            await auth_check.finish("GitHub API 超时，请稍后再试")
        except ActionFailed as e:
            if e.response.status_code == 404:
                await auth_check.finish(
                    "你的 GitHub 帐号授权已过期，请使用 /auth 进行刷新"
                )
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


auth_revoke = on_command(
    ("auth", "revoke"),
    aliases={("授权", "撤销")},
    rule=NO_GITHUB_EVENT,
    priority=config.github_command_priority,
    block=True,
)


@auth_revoke.handle()
async def revoke_user(user: AUTHORIZED_USER):
    bot = get_github_bot()

    async with bot.as_oauth_app():
        try:
            await bot.rest.apps.async_delete_token(
                client_id=config.github_app.client_id, access_token=user.access_token
            )
        except ActionTimeout:
            await auth_revoke.finish("GitHub API 超时，请稍后再试")
        except Exception as e:
            logger.opt(exception=e).error(
                f"Failed while deleting token in auth revoke: {e}"
            )
            await auth_revoke.finish("未知错误发生，请尝试重试或联系管理员")

    try:
        await user.unauth()
    except Exception as e:
        logger.opt(exception=e).error(f"Failed while unauth user: {e}")
        await auth_revoke.finish("未知错误发生，请尝试重试或联系管理员")

    await auth_revoke.finish("你的 GitHub 帐号授权已撤销")
