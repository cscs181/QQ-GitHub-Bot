"""
@Author         : yanyongyu
@Date           : 2022-11-07 08:35:10
@LastEditors    : yanyongyu
@LastEditTime   : 2024-06-02 16:52:21
@Description    : Webhook dependencies
@GitHub         : https://github.com/yanyongyu
"""

__author__ = "yanyongyu"

from datetime import timedelta
from typing import Generic, TypeVar, Annotated, TypeAlias, cast

from nonebot import logger
from nonebot.params import Depends
from nonebot.matcher import Matcher
from nonebot.adapters.github import Event
from nonebot.adapters.onebot.v11 import Bot as QQBot
from nonebot.adapters.qq import Bot as QQOfficialBot
from nonebot.adapters.github.utils import get_attr_or_item
from nonebot.adapters.onebot.v11 import Message as QQMessage
from nonebot.adapters.onebot.v11 import MessageSegment as QQMS
from nonebot.adapters.qq.exception import ActionFailed as QQOfficialActionFailed

from src.providers.redis import redis_client
from src.plugins.github.models import Subscription
from src.plugins.github.helpers import qqofficial_conditional_image
from src.plugins.github.cache.message_tag import Tag, create_message_tag
from src.providers.platform import TargetInfo, get_target_bot, extract_sent_message
from src.providers.platform.targets import (
    QQUserInfo,
    QQGroupInfo,
    QQGuildUserInfo,
    QQGuildChannelInfo,
    QQOfficialUserInfo,
    QQOfficialGroupInfo,
)

T = TypeVar("T", bound=Event)

SEND_INTERVAL = 0.5
THROTTLE_KEY = "cache:github:webhooks:throttle:{identifier}"


async def get_event_info(
    event: Event, matcher: Matcher
) -> tuple[str, str, str, str | None]:
    repository = get_attr_or_item(event.payload, "repository")
    full_name = get_attr_or_item(repository, "full_name")
    if not repository or not full_name:
        await matcher.finish()
    owner, repo = full_name.split("/", 1)
    action = get_attr_or_item(event.payload, "action")
    if not all((owner, repo, event.name)):
        await matcher.finish()
    return owner, repo, event.name, action


EVENT_INFO: TypeAlias = Annotated[
    tuple[str, str, str, str | None], Depends(get_event_info)
]


async def list_subscribers(event_info: EVENT_INFO) -> list[Subscription]:
    owner, repo, event_name, action = event_info
    return await Subscription.list_subscribers(owner, repo, event_name, action)


SUBSCRIBERS: TypeAlias = Annotated[list[Subscription], Depends(list_subscribers)]


async def send_subscriber_text(target_info: TargetInfo, text: str, tag: Tag) -> None:
    bot = await get_target_bot(target_info)
    if not bot:
        logger.error("Unable to get target bot", target_info=target_info)
        return

    try:
        match target_info:
            case QQUserInfo():
                result = await cast(QQBot, bot).send_private_msg(
                    user_id=target_info.qq_user_id, message=text
                )
            case QQGroupInfo():
                result = await cast(QQBot, bot).send_group_msg(
                    group_id=target_info.qq_group_id, message=text
                )
            case QQOfficialUserInfo():
                result = await cast(QQOfficialBot, bot).post_c2c_messages(
                    openid=target_info.qq_user_open_id, msg_type=0, content=text
                )
            case QQOfficialGroupInfo():
                result = await cast(QQOfficialBot, bot).post_group_messages(
                    group_openid=target_info.qq_group_open_id, msg_type=0, content=text
                )
            case QQGuildUserInfo():
                logger.error("Unable to send message to QQGuild User", user=target_info)
                return
            case QQGuildChannelInfo():
                result = await cast(QQOfficialBot, bot).post_messages(
                    channel_id=target_info.qq_channel_id, content=text
                )
    except QQOfficialActionFailed as e:
        if e.code in (304045, 304046, 304047, 304048, 304049, 304050):
            return
        raise

    if sent_message_info := extract_sent_message(target_info, result):
        await create_message_tag(sent_message_info, tag)


async def send_subscriber_image(
    target_info: TargetInfo, image: bytes, tag: Tag
) -> None:
    bot = await get_target_bot(target_info)
    if not bot:
        logger.error("Unable to get target bot", target_info=target_info)
        return

    try:
        match target_info:
            case QQUserInfo():
                result = await cast(QQBot, bot).send_private_msg(
                    user_id=target_info.qq_user_id, message=QQMessage(QQMS.image(image))
                )
            case QQGroupInfo():
                result = await cast(QQBot, bot).send_group_msg(
                    group_id=target_info.qq_group_id,
                    message=QQMessage(QQMS.image(image)),
                )
            case QQOfficialUserInfo():
                result = await cast(QQOfficialBot, bot).send_to_c2c(
                    openid=target_info.qq_user_open_id,
                    message=await qqofficial_conditional_image(image),
                )
            case QQOfficialGroupInfo():
                result = await cast(QQOfficialBot, bot).send_to_group(
                    group_openid=target_info.qq_group_open_id,
                    message=await qqofficial_conditional_image(image),
                )
            case QQGuildUserInfo():
                logger.error("Unable to send message to QQGuild User", user=target_info)
                return
            case QQGuildChannelInfo():
                result = await cast(QQOfficialBot, bot).post_messages(
                    channel_id=target_info.qq_channel_id, file_image=image
                )
    except QQOfficialActionFailed as e:
        if e.code in (304045, 304046, 304047, 304048, 304049, 304050):
            return
        raise

    if sent_message_info := extract_sent_message(target_info, result):
        await create_message_tag(sent_message_info, tag)


async def send_subscriber_image_url(
    target_info: TargetInfo, image: str, tag: Tag
) -> None:
    bot = await get_target_bot(target_info)
    if not bot:
        logger.error("Unable to get target bot", target_info=target_info)
        return

    try:
        match target_info:
            case QQUserInfo():
                result = await cast(QQBot, bot).send_private_msg(
                    user_id=target_info.qq_user_id, message=QQMessage(QQMS.image(image))
                )
            case QQGroupInfo():
                result = await cast(QQBot, bot).send_group_msg(
                    group_id=target_info.qq_group_id,
                    message=QQMessage(QQMS.image(image)),
                )
            case QQOfficialUserInfo():
                result = await cast(QQOfficialBot, bot).post_c2c_files(
                    openid=target_info.qq_user_open_id, file_type=1, url=image
                )
            case QQOfficialGroupInfo():
                result = await cast(QQOfficialBot, bot).post_group_files(
                    group_openid=target_info.qq_group_open_id, file_type=1, url=image
                )
            case QQGuildUserInfo():
                logger.error("Unable to send message to QQGuild User", user=target_info)
                return
            case QQGuildChannelInfo():
                result = await cast(QQOfficialBot, bot).post_messages(
                    channel_id=target_info.qq_channel_id, image=image
                )
    except QQOfficialActionFailed as e:
        if e.code in (304045, 304046, 304047, 304048, 304049, 304050):
            return
        raise

    if sent_message_info := extract_sent_message(target_info, result):
        await create_message_tag(sent_message_info, tag)


class Throttle(Generic[T]):
    def __init__(
        self,
        event_type: tuple[type[T], ...],
        expire: timedelta,
    ):
        self.event_type = event_type
        self.expire = expire

    @classmethod
    def get_key(cls, event: Event) -> str:
        username: str = get_attr_or_item(
            get_attr_or_item(event.payload, "sender"), "login"
        )
        action: str | None = get_attr_or_item(event.payload, "action")
        event_type: str = event.name + (f"/{action}" if action else "")
        repository = get_attr_or_item(event.payload, "repository")
        repo_name = repository and get_attr_or_item(repository, "full_name")
        identifier = f"{username}:{event_type}" + (f":{repo_name}" if repo_name else "")
        return THROTTLE_KEY.format(identifier=identifier)

    async def __call__(self, event: Event, matcher: Matcher):
        # do nothing to other event
        if not isinstance(event, self.event_type):
            return

        # check exists identity
        key = self.get_key(event)
        exists = await redis_client.get(key)
        if exists is not None:
            matcher.skip()
        else:
            await redis_client.set(key, 1, ex=self.expire)
