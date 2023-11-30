"""
@Author         : yanyongyu
@Date           : 2023-11-27 14:31:21
@LastEditors    : yanyongyu
@LastEditTime   : 2023-11-29 15:59:33
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""

__author__ = "yanyongyu"


from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot import logger, on_command
from nonebot.plugin import PluginMetadata
from nonebot.adapters.github import ActionFailed, ActionTimeout

from src.plugins.github import config
from src.plugins.github.helpers import NO_GITHUB_EVENT
from src.plugins.github.dependencies import AUTHORIZED_USER, GITHUB_PUBLIC_CONTEXT

__plugin_meta__ = PluginMetadata(
    "GitHub 搜索",
    "快速搜索 GitHub",
    "/search code: 搜索 GitHub 代码\n"
    "/search repo: 搜索 GitHub 仓库\n"
    "/search user: 搜索 GitHub 用户\n",
)


code_search = on_command(
    ("search", "code"),
    aliases={"搜索代码"},
    rule=NO_GITHUB_EVENT,
    priority=config.github_command_priority,
)


@code_search.handle()
async def handle_code_search(
    user: AUTHORIZED_USER,  # need authorized user because of rate limit
    context: GITHUB_PUBLIC_CONTEXT,
    args: Message = CommandArg(),
):
    query = args.extract_plain_text().strip()
    if not query:
        await code_search.finish("搜索内容不能为空")

    try:
        async with context as bot:
            resp = await bot.rest.search.async_code(q=query, per_page=5)
            result = resp.parsed_data
    except ActionTimeout:
        await code_search.finish("GitHub API 超时，请稍后再试")
    except ActionFailed as e:
        if e.response.status_code == 401:
            await code_search.finish(
                "你的 GitHub 帐号授权已过期，请使用 /auth 进行刷新"
            )
        elif e.response.status_code in {403, 429}:
            await code_search.finish("GitHub API 调用次数超过限制，请稍后再试")
        logger.opt(exception=e).error(f"Failed while searching code: {e}")
        await code_search.finish("未知错误发生，请尝试重试或联系管理员")
    except Exception as e:
        logger.opt(exception=e).error(f"Failed while searching code: {e}")
        await code_search.finish("未知错误发生，请尝试重试或联系管理员")

    if not result.items:
        await code_search.finish("未找到相关代码")
    else:
        await code_search.finish(
            f"共计 {result.total_count} 个结果\n\n"
            + "\n\n".join(code.html_url for code in result.items)
        )


repo_search = on_command(
    "search",
    aliases={("search", "repo"), "搜索", "搜索仓库"},
    rule=NO_GITHUB_EVENT,
    priority=config.github_command_priority,
)


@repo_search.handle()
async def handle_repo_search(
    context: GITHUB_PUBLIC_CONTEXT, args: Message = CommandArg()
):
    query = args.extract_plain_text().strip()
    if not query:
        await repo_search.finish("搜索内容不能为空")

    try:
        async with context as bot:
            resp = await bot.rest.search.async_repos(q=query, per_page=5)
            result = resp.parsed_data
    except ActionTimeout:
        await repo_search.finish("GitHub API 超时，请稍后再试")
    except ActionFailed as e:
        if e.response.status_code == 401:
            await repo_search.finish(
                "你的 GitHub 帐号授权已过期，请使用 /auth 进行刷新"
            )
        logger.opt(exception=e).error(f"Failed while searching repo: {e}")
        await repo_search.finish("未知错误发生，请尝试重试或联系管理员")
    except Exception as e:
        logger.opt(exception=e).error(f"Failed while searching repo: {e}")
        await repo_search.finish("未知错误发生，请尝试重试或联系管理员")

    if not result.items:
        await repo_search.finish("未找到相关仓库")
    else:
        await repo_search.finish(
            f"共计 {result.total_count} 个结果\n\n"
            + "\n\n".join(
                f"{repo.html_url}\n{repo.description or '无仓库描述'}"
                for repo in result.items
            )
        )


user_search = on_command(
    ("search", "user"),
    aliases={"搜索用户"},
    rule=NO_GITHUB_EVENT,
    priority=config.github_command_priority,
)


@user_search.handle()
async def handle_user_search(
    context: GITHUB_PUBLIC_CONTEXT, args: Message = CommandArg()
):
    query = args.extract_plain_text().strip()
    if not query:
        await user_search.finish("搜索内容不能为空")

    try:
        async with context as bot:
            resp = await bot.rest.search.async_users(q=query, per_page=5)
            result = resp.parsed_data
    except ActionTimeout:
        await user_search.finish("GitHub API 超时，请稍后再试")
    except ActionFailed as e:
        if e.response.status_code == 401:
            await user_search.finish(
                "你的 GitHub 帐号授权已过期，请使用 /auth 进行刷新"
            )
        logger.opt(exception=e).error(f"Failed while searching user: {e}")
        await user_search.finish("未知错误发生，请尝试重试或联系管理员")
    except Exception as e:
        logger.opt(exception=e).error(f"Failed while searching user: {e}")
        await user_search.finish("未知错误发生，请尝试重试或联系管理员")

    if not result.items:
        await user_search.finish("未找到相关用户")
    else:
        await user_search.finish(
            f"共计 {result.total_count} 个结果\n\n"
            + "\n\n".join(
                f"{user.html_url}\n{user.bio or '暂无描述'}" for user in result.items
            )
        )
