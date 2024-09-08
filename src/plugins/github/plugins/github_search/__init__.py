"""
@Author         : yanyongyu
@Date           : 2023-11-27 14:31:21
@LastEditors    : yanyongyu
@LastEditTime   : 2024-09-08 11:45:23
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""

__author__ = "yanyongyu"

from nonebot.matcher import Matcher
from nonebot.adapters import Message
from nonebot import logger, on_command
from nonebot.plugin import PluginMetadata
from nonebot.params import CommandArg, ArgPlainText
from nonebot.adapters.github import ActionFailed, ActionTimeout

from src.plugins.github import config
from src.plugins.github.helpers import NO_GITHUB_EVENT
from src.plugins.github.dependencies import (
    AUTHORIZED_USER,
    GITHUB_PUBLIC_CONTEXT,
    allow_cancellation,
)

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
    matcher: Matcher,
    user: AUTHORIZED_USER,  # need authorized user because of rate limit
    arg: Message = CommandArg(),
):
    if query := arg.extract_plain_text().strip():
        matcher.set_arg("query", arg.__class__(query))


@code_search.got(
    "query",
    prompt="请发送想要搜索的内容",
    parameterless=(allow_cancellation("已取消"),),
)
async def do_code_search(context: GITHUB_PUBLIC_CONTEXT, query: str = ArgPlainText()):
    if not query:
        await code_search.reject(
            "搜索内容不能为空！\n请重新发送想要搜索的内容，"
            "例如：「nonebot」\n或发送「取消」以取消"
        )

    try:
        async with context() as bot:
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
async def handle_repo_search(matcher: Matcher, arg: Message = CommandArg()):
    if query := arg.extract_plain_text().strip():
        matcher.set_arg("query", arg.__class__(query))


@repo_search.got(
    "query",
    prompt="请输入想要搜索的仓库",
    parameterless=(allow_cancellation("已取消"),),
)
async def do_repo_search(context: GITHUB_PUBLIC_CONTEXT, query: str = ArgPlainText()):
    if not query:
        await code_search.reject(
            "搜索仓库不能为空！\n请重新发送想要搜索的仓库，"
            "例如：「nonebot」\n或发送「取消」以取消"
        )

    try:
        async with context() as bot:
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
async def handle_user_search(matcher: Matcher, arg: Message = CommandArg()):
    if query := arg.extract_plain_text().strip():
        matcher.set_arg("query", arg.__class__(query))


@user_search.got(
    "query",
    prompt="请输入想要搜索的用户",
    parameterless=(allow_cancellation("已取消"),),
)
async def do_user_search(context: GITHUB_PUBLIC_CONTEXT, query: str = ArgPlainText()):
    if not query:
        await code_search.reject(
            "搜索用户不能为空！\n请重新发送想要搜索的用户，"
            "例如：「nonebot」\n或发送「取消」以取消"
        )

    try:
        async with context() as bot:
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
