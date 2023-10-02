"""
@Author         : yanyongyu
@Date           : 2022-09-07 11:48:48
@LastEditors    : yanyongyu
@LastEditTime   : 2023-03-30 21:48:52
@Description    : Event adapters
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from nonebot.adapters import Event
from nonebot.adapters.onebot.v11 import (
    MessageEvent,
    GroupMessageEvent,
    PrivateMessageEvent,
)

from src.plugins.github.libs.message_tag import MessageInfo
from src.plugins.github.libs.platform import PLATFORMS, UserInfo, GroupInfo

# qq events
QQ_USER_EVENT = (MessageEvent,)
QQ_PRIVATE_EVENT = (PrivateMessageEvent,)
QQ_GROUP_EVENT = (GroupMessageEvent,)
# all handled qq event (used by platform recognization)
QQ_EVENT = QQ_USER_EVENT + QQ_PRIVATE_EVENT + QQ_GROUP_EVENT

# all handled events
# event triggered by user (has user info)
USER_EVENT = QQ_USER_EVENT
"""Events that have user info"""
PRIVATE_EVENT = QQ_PRIVATE_EVENT
"""Events that are private"""
GROUP_EVENT = QQ_GROUP_EVENT
"""Events that are from group"""


def get_platform(event: Event) -> PLATFORMS | None:
    """Get platform name from event

    Returns:
        platform name or None
    """

    if isinstance(event, QQ_EVENT):
        return "qq"
    # elif isinstance(event, QQGUILD_EVENT):
    #     return "qqguild"


def get_user_id(event: Event) -> int | str | None:
    """Get user id from user event

    Returns:
        user id or None
    """

    if isinstance(event, QQ_USER_EVENT):
        return event.user_id


def get_user_info(event: Event) -> UserInfo | None:
    """Get user info from event

    Returns:
        user info or None
    """

    platform = get_platform(event)
    user_id = get_user_id(event)
    if platform and user_id:
        return {"type": platform, "user_id": user_id}  # type: ignore


def get_group_id(event: Event) -> int | str | None:
    """Get group id from group event

    Returns:
        group id or None
    """

    if isinstance(event, QQ_GROUP_EVENT):
        return event.group_id


def get_group_info(event: Event) -> GroupInfo | None:
    """Get group info from event

    Returns:
        group info or None
    """

    platform = get_platform(event)
    group_id = get_group_id(event)
    if platform and group_id:
        return {"type": platform, "group_id": group_id}  # type: ignore


def get_message_id(event: Event) -> str | None:
    """Get message id from message event

    Returns:
        message id or None
    """

    if isinstance(event, QQ_EVENT):
        return str(event.message_id)


def get_message_info(event: Event) -> MessageInfo | None:
    """Get message info from message event

    Returns:
        message info or None
    """

    platform = get_platform(event)
    message_id = get_message_id(event)
    if platform and message_id:
        return {"type": platform, "message_id": message_id}
