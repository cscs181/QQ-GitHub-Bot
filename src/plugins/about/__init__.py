"""
@Author         : yanyongyu
@Date           : 2023-03-08 00:11:17
@LastEditors    : yanyongyu
@LastEditTime   : 2023-03-30 20:03:23
@Description    : About plugin
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

import secrets

from nonebot.adapters import Event
from nonebot import logger, on_command
from nonebot.adapters.onebot.v11 import MessageSegment as QQMS

from src.plugins.github.libs.message_tag import RepoTag, create_message_tag
from src.plugins.github.helpers import NO_GITHUB_EVENT, get_platform, get_message_info

OWNER = "cscs181"
REPO = "QQ-GitHub-Bot"

about = on_command("about", rule=NO_GITHUB_EVENT, priority=10, block=True)
"""`about` command matcher"""


@about.handle()
async def handle_about(event: Event):
    if info := get_message_info(event):
        await create_message_tag(info, RepoTag(owner=OWNER, repo=REPO, is_receive=True))

    tag = RepoTag(owner=OWNER, repo=REPO, is_receive=False)

    match get_platform(event):
        case "qq":
            result = await about.send(
                QQMS.image(
                    f"https://opengraph.githubassets.com/{secrets.token_urlsafe(16)}/"
                    f"{OWNER}/{REPO}"
                )
            )
            if isinstance(result, dict) and "message_id" in result:
                await create_message_tag(
                    {"type": "qq", "message_id": result["message_id"]},
                    tag,
                )
        case _:
            logger.error(f"Unprocessed event type: {type(event)}")
