"""
@Author         : yanyongyu
@Date           : 2023-10-07 17:18:31
@LastEditors    : yanyongyu
@LastEditTime   : 2023-11-13 17:22:45
@Description    : Platform compatibility provider plugin
@GitHub         : https://github.com/yanyongyu
"""

__author__ = "yanyongyu"

from typing import Annotated, TypeAlias

from nonebot import logger
from nonebot.adapters import Event
from nonebot.params import Depends
from nonebot.matcher import Matcher

# isort: split

from .roles import RoleLevel as RoleLevel

# isort: split

from .targets import UserInfo as UserInfo
from .targets import GroupInfo as GroupInfo
from .targets import TargetInfo as TargetInfo
from .targets import TargetType as TargetType

# isort: split

from .messages import MessageInfo as MessageInfo

# isort: split

from .extractors import extract_role as extract_role
from .extractors import extract_user as extract_user
from .extractors import extract_group as extract_group
from .extractors import extract_target as extract_target
from .extractors import get_target_bot as get_target_bot
from .extractors import extract_message as extract_message
from .extractors import extract_is_private as extract_is_private
from .extractors import extract_sent_message as extract_sent_message
from .extractors import extract_reply_message as extract_reply_message

OPTIONAL_USER_INFO: TypeAlias = Annotated[
    UserInfo | None, Depends(extract_user, use_cache=True)
]
OPTIONAL_GROUP_INFO: TypeAlias = Annotated[
    GroupInfo | None, Depends(extract_group, use_cache=True)
]
OPTIONAL_TARGET_INFO: TypeAlias = Annotated[
    TargetInfo | None, Depends(extract_target, use_cache=True)
]
OPTIONAL_IS_PRIVATE: TypeAlias = Annotated[
    bool | None, Depends(extract_is_private, use_cache=True)
]
OPTIONAL_ROLE: TypeAlias = Annotated[
    RoleLevel | None, Depends(extract_role, use_cache=True)
]
OPTIONAL_MESSAGE_INFO: TypeAlias = Annotated[
    MessageInfo | None, Depends(extract_message, use_cache=True)
]
OPTIONAL_REPLY_MESSAGE_INFO: TypeAlias = Annotated[
    MessageInfo | None, Depends(extract_reply_message, use_cache=True)
]


async def ensure_user(
    event: Event, matcher: Matcher, user: OPTIONAL_USER_INFO
) -> UserInfo:
    if user is None:
        logger.error(f"Unprocessed event type: {type(event)}")
        await matcher.finish()
    return user


async def ensure_group(
    event: Event, matcher: Matcher, group: OPTIONAL_GROUP_INFO
) -> GroupInfo:
    if group is None:
        logger.error(f"Unprocessed event type: {type(event)}")
        await matcher.finish()
    return group


async def ensure_target(
    event: Event, matcher: Matcher, target: OPTIONAL_TARGET_INFO
) -> TargetInfo:
    if target is None:
        logger.error(f"Unprocessed event type: {type(event)}")
        await matcher.finish()
    return target


async def ensure_is_private(
    event: Event, matcher: Matcher, is_private: OPTIONAL_IS_PRIVATE
) -> bool:
    if is_private is None:
        logger.error(f"Unprocessed event type: {type(event)}")
        await matcher.finish()
    return is_private


async def ensure_role(event: Event, matcher: Matcher, role: OPTIONAL_ROLE) -> RoleLevel:
    if role is None:
        logger.error(f"Unprocessed event type: {type(event)}")
        await matcher.finish()
    return role


async def ensure_message(
    event: Event, matcher: Matcher, message: OPTIONAL_MESSAGE_INFO
) -> MessageInfo:
    if message is None:
        logger.error(f"Unprocessed event type: {type(event)}")
        await matcher.finish()
    return message


USER_INFO: TypeAlias = Annotated[UserInfo, Depends(ensure_user, use_cache=True)]
"""User info dependency. Finish the session if user info cannot be extracted."""
GROUP_INFO: TypeAlias = Annotated[GroupInfo, Depends(ensure_group, use_cache=True)]
"""Group info dependency. Finish the session if group info cannot be extracted."""
TARGET_INFO: TypeAlias = Annotated[TargetInfo, Depends(ensure_target, use_cache=True)]
"""Target info dependency. Finish the session if target info cannot be extracted.""" ""
IS_PRIVATE: TypeAlias = Annotated[bool, Depends(ensure_is_private, use_cache=True)]
"""Is private dependency. Finish the session if is private cannot be extracted."""
ROLE: TypeAlias = Annotated[RoleLevel, Depends(ensure_role, use_cache=True)]
"""Role dependency. Finish the session if role cannot be extracted."""
MESSAGE_INFO: TypeAlias = Annotated[
    MessageInfo, Depends(ensure_message, use_cache=True)
]
"""Message info dependency. Finish the session if message info cannot be extracted."""
