"""
@Author         : yanyongyu
@Date           : 2023-10-18 17:08:37
@LastEditors    : yanyongyu
@LastEditTime   : 2024-09-08 11:44:57
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""

__author__ = "yanyongyu"

import re

from nonebot.typing import T_State
from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot import logger, on_command
from playwright.async_api import Error, TimeoutError
from nonebot.adapters.onebot.v11 import MessageSegment as QQMS
from nonebot.adapters.qq import MessageSegment as QQOfficialMS
from nonebot.adapters.github import ActionFailed, ActionTimeout

from src.plugins.github import config
from src.plugins.github.libs.github import FULLREPO_REGEX
from src.plugins.github.libs.renderer import readme_to_image
from src.plugins.github.cache.message_tag import RepoTag, create_message_tag
from src.plugins.github.helpers import NO_GITHUB_EVENT, qqofficial_conditional_image
from src.plugins.github.dependencies import (
    REPOSITORY,
    OPTIONAL_REPLY_TAG,
    GITHUB_PUBLIC_CONTEXT,
)
from src.providers.platform import (
    TARGET_INFO,
    MESSAGE_INFO,
    TargetType,
    extract_sent_message,
)

readme = on_command(
    "readme",
    aliases={"仓库说明"},
    rule=NO_GITHUB_EVENT,
    priority=config.github_command_priority,
    block=True,
)


@readme.handle()
async def parse_arg(
    state: T_State, tag: OPTIONAL_REPLY_TAG, arg: Message = CommandArg()
):
    # if arg is not empty, use arg as full_name
    if full_name := arg.extract_plain_text().strip():
        if not (matched := re.match(rf"^{FULLREPO_REGEX}$", full_name)):
            await readme.finish(
                f"仓库名 {full_name} 错误！\n请重新发送正确的仓库名，"
                "例如：「/readme owner/repo」"
            )
        state["owner"] = matched["owner"]
        state["repo"] = matched["repo"]
    elif tag:
        state["owner"] = tag.owner
        state["repo"] = tag.repo
        state["from_tag"] = True
    else:
        await readme.finish(
            "请发送要查看 README 的仓库全名，例如：「/readme owner/repo」"
        )


@readme.handle()
async def check_repo(state: T_State, repo: REPOSITORY):
    state["repo_info"] = repo


@readme.handle()
async def handle_content(
    state: T_State,
    message_info: MESSAGE_INFO,
    context: GITHUB_PUBLIC_CONTEXT,
):
    owner: str = state["owner"]
    repo: str = state["repo"]

    await create_message_tag(
        message_info, RepoTag(owner=owner, repo=repo, is_receive=True)
    )

    try:
        async with context() as bot:
            resp = await bot.rest.repos.async_get_readme(
                owner=owner,
                repo=repo,
                headers={"Accept": "application/vnd.github.html"},
            )
            state["content"] = resp.text
            return
    except ActionTimeout:
        await readme.finish("GitHub API 超时，请稍后再试")
    except ActionFailed as e:
        if e.response.status_code == 404:
            await readme.finish("未找到该仓库的 README")
        logger.opt(exception=e).error(f"Failed while getting repo readme: {e}")
        await readme.finish("未知错误发生，请尝试重试或联系管理员")
    except Exception as e:
        logger.opt(exception=e).error(f"Failed while getting repo readme: {e}")
        await readme.finish("未知错误发生，请尝试重试或联系管理员")


@readme.handle()
async def render_content(
    state: T_State,
    target_info: TARGET_INFO,
    context: GITHUB_PUBLIC_CONTEXT,
):
    owner: str = state["owner"]
    repo: str = state["repo"]
    repo_info: REPOSITORY = state["repo_info"]
    content: str = state["content"]

    try:
        async with context() as bot:
            img = await readme_to_image(bot, repo_info, content)
    except TimeoutError:
        await readme.finish("生成图片超时！请稍后再试")
    except Error:
        await readme.finish("生成图片出错！请稍后再试")
    except Exception as e:
        logger.opt(exception=e).error(f"Failed while generating repo readme image: {e}")
        await readme.finish("生成图片出错！请稍后再试")

    match target_info.type:
        case TargetType.QQ_USER | TargetType.QQ_GROUP:
            result = await readme.send(QQMS.image(img))
        case TargetType.QQ_OFFICIAL_USER | TargetType.QQ_OFFICIAL_GROUP:
            result = await readme.send(await qqofficial_conditional_image(img))
        case TargetType.QQGUILD_USER | TargetType.QQGUILD_CHANNEL:
            result = await readme.send(QQOfficialMS.file_image(img))

    tag = RepoTag(owner=owner, repo=repo, is_receive=False)
    if sent_message_info := extract_sent_message(target_info, result):
        await create_message_tag(sent_message_info, tag)
