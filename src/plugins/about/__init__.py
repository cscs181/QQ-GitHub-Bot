"""
@Author         : yanyongyu
@Date           : 2023-03-08 00:11:17
@LastEditors    : yanyongyu
@LastEditTime   : 2023-10-07 16:57:52
@Description    : About plugin
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

import secrets

from nonebot import on_command
from nonebot.plugin import PluginMetadata
from nonebot.adapters.onebot.v11 import MessageSegment as QQMS
from nonebot.adapters.qq import MessageSegment as QQOfficialMS

from src.plugins.github.helpers import NO_GITHUB_EVENT
from src.plugins.github.cache.message_tag import RepoTag, create_message_tag
from src.providers.platform import (
    TARGET_INFO,
    MESSAGE_INFO,
    TargetType,
    extract_sent_message,
)

__plugin_meta__ = PluginMetadata(
    "关于",
    "获取关于本机器人的信息",
    "使用 /about 命令获取关于本机器人的信息",
)

OWNER = "cscs181"
REPO = "QQ-GitHub-Bot"


about = on_command(
    "about", aliases={"关于"}, rule=NO_GITHUB_EVENT, priority=10, block=True
)


@about.handle()
async def handle_about(target_info: TARGET_INFO, message_info: MESSAGE_INFO):
    await create_message_tag(
        message_info, RepoTag(owner=OWNER, repo=REPO, is_receive=True)
    )

    tag = RepoTag(owner=OWNER, repo=REPO, is_receive=False)
    image_url = (
        f"https://opengraph.githubassets.com/{secrets.token_urlsafe(16)}/{OWNER}/{REPO}"
    )

    match target_info.type:
        case TargetType.QQ_USER | TargetType.QQ_GROUP:
            result = await about.send(QQMS.image(image_url))
        case (
            TargetType.QQ_OFFICIAL_USER
            | TargetType.QQGUILD_USER
            | TargetType.QQ_OFFICIAL_GROUP
            | TargetType.QQGUILD_CHANNEL
        ):
            result = await about.send(QQOfficialMS.image(image_url))

    if sent_message_info := extract_sent_message(target_info, result):
        await create_message_tag(sent_message_info, tag)
