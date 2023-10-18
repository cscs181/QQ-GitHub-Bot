"""
@Author         : yanyongyu
@Date           : 2023-10-18 17:08:37
@LastEditors    : yanyongyu
@LastEditTime   : 2023-10-18 17:28:38
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from nonebot import logger, on_command
from playwright.async_api import Error, TimeoutError
from nonebot.adapters.onebot.v11 import MessageSegment as QQMS
from nonebot.adapters.qq import MessageSegment as QQOfficialMS
from nonebot.adapters.github import ActionFailed, ActionTimeout

from src.plugins.github import config
from src.providers.playwright import content_screenshot
from src.plugins.github.helpers import REPLY_ANY, NO_GITHUB_EVENT
from src.plugins.github.cache.message_tag import RepoTag, create_message_tag
from src.plugins.github.dependencies import REPLY_TAG, GITHUB_PUBLIC_CONTEXT
from src.providers.platform import (
    TARGET_INFO,
    MESSAGE_INFO,
    TargetType,
    extract_sent_message,
)

readme = on_command(
    "readme",
    rule=NO_GITHUB_EVENT & REPLY_ANY,
    priority=config.github_command_priority,
    block=True,
)


@readme.handle()
async def handle_content(
    target_info: TARGET_INFO,
    message_info: MESSAGE_INFO,
    tag: REPLY_TAG,
    context: GITHUB_PUBLIC_CONTEXT,
):
    await create_message_tag(
        message_info, RepoTag(owner=tag.owner, repo=tag.repo, is_receive=True)
    )

    try:
        async with context as bot:
            resp = await bot.rest.repos.async_get_readme(
                owner=tag.owner,
                repo=tag.repo,
                headers={"Accept": "application/vnd.github.html"},
            )
            content = resp.parsed_data.content
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

    try:
        img = await content_screenshot(content, 800, 300)
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
        case (
            TargetType.QQ_OFFICIAL_USER
            | TargetType.QQGUILD_USER
            | TargetType.QQ_OFFICIAL_GROUP
            | TargetType.QQGUILD_CHANNEL
        ):
            result = await readme.send(QQOfficialMS.file_image(img))

    tag = RepoTag(owner=tag.owner, repo=tag.repo, is_receive=False)
    if sent_message_info := extract_sent_message(target_info, result):
        await create_message_tag(sent_message_info, tag)
