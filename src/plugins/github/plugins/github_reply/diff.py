"""
@Author         : yanyongyu
@Date           : 2021-03-26 14:59:59
@LastEditors    : yanyongyu
@LastEditTime   : 2023-12-05 17:18:11
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""

__author__ = "yanyongyu"


from nonebot import logger, on_command
from nonebot_plugin_filehost import FileHost
from nonebot.adapters.github import ActionTimeout
from playwright.async_api import Error, TimeoutError
from nonebot.adapters.onebot.v11 import MessageSegment as QQMS
from nonebot.adapters.qq import MessageSegment as QQOfficialMS

from src.plugins.github import config
from src.plugins.github.libs.renderer import pr_diff_to_image
from src.plugins.github.helpers import REPLY_PR, NO_GITHUB_EVENT
from src.plugins.github.cache.message_tag import create_message_tag
from src.providers.platform import (
    TARGET_INFO,
    MESSAGE_INFO,
    TargetType,
    extract_sent_message,
)
from src.plugins.github.dependencies import (
    ISSUE,
    PR_REPLY_TAG,
    STORE_TAG_DATA,
    GITHUB_PUBLIC_CONTEXT,
)

diff = on_command(
    "diff",
    aliases={"差异"},
    rule=NO_GITHUB_EVENT & REPLY_PR,
    priority=config.github_command_priority,
    block=True,
)


@diff.handle(parameterless=(STORE_TAG_DATA,))
async def handle_diff(
    target_info: TARGET_INFO,
    message_info: MESSAGE_INFO,
    tag: PR_REPLY_TAG,
    issue_: ISSUE,
    context: GITHUB_PUBLIC_CONTEXT,
):
    await create_message_tag(
        message_info,
        tag.copy(update={"is_receive": True}),
    )

    try:
        async with context as bot:
            img = await pr_diff_to_image(bot, issue_)
    except ActionTimeout:
        await diff.finish("GitHub API 超时，请稍后再试")
    except TimeoutError:
        await diff.finish("生成图片超时！请稍后再试")
    except Error:
        await diff.finish("生成图片出错！请稍后再试")
    except Exception as e:
        logger.opt(exception=e).error(f"Failed while generating issue image: {e}")
        await diff.finish("生成图片出错！请稍后再试")

    match target_info.type:
        case TargetType.QQ_USER | TargetType.QQ_GROUP:
            result = await diff.send(QQMS.image(img))
        case TargetType.QQ_OFFICIAL_USER | TargetType.QQ_OFFICIAL_GROUP:
            result = await diff.send(
                QQOfficialMS.image(await FileHost(img, suffix=".png").to_url())
            )
        case TargetType.QQGUILD_USER | TargetType.QQGUILD_CHANNEL:
            result = await diff.send(QQOfficialMS.file_image(img))

    tag = tag.copy(update={"is_receive": False})
    if sent_message_info := extract_sent_message(target_info, result):
        await create_message_tag(sent_message_info, tag)
