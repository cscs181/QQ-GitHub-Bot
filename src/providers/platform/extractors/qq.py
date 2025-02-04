"""
@Author         : yanyongyu
@Date           : 2023-10-08 18:04:17
@LastEditors    : yanyongyu
@LastEditTime   : 2023-12-04 17:14:37
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""

__author__ = "yanyongyu"

from typing import cast
from typing_extensions import override

import nonebot
from nonebot import logger
from nonebot.adapters.qq.models import Message as GuildMessage
from nonebot.adapters.qq.models import PostC2CMessagesReturn, PostGroupMessagesReturn
from nonebot.adapters.qq import (
    Bot,
    MessageEvent,
    QQMessageEvent,
    GuildMessageEvent,
    MessageCreateEvent,
    AtMessageCreateEvent,
    C2CMessageCreateEvent,
    DirectMessageCreateEvent,
    GroupAtMessageCreateEvent,
)

from src.providers.platform.roles import RoleLevel
from src.providers.platform.targets import (
    UserInfo,
    GroupInfo,
    TargetType,
    QQGuildUserInfo,
    QQGuildChannelInfo,
    QQOfficialUserInfo,
    QQOfficialGroupInfo,
)
from src.providers.platform.messages import (
    MessageInfo,
    QQGuildUserMessageInfo,
    QQGuildChannelMessageInfo,
    QQOfficialUserMessageInfo,
    QQOfficialGroupMessageInfo,
)

from ._base import Extractor


class QQExtractor(
    Extractor[
        MessageEvent,
        QQOfficialUserInfo | QQOfficialGroupInfo | QQGuildUserInfo | QQGuildChannelInfo,
    ]
):
    EVENTS = (MessageEvent,)
    TARGETS = (
        QQOfficialUserInfo,
        QQOfficialGroupInfo,
        QQGuildUserInfo,
        QQGuildChannelInfo,
    )

    @classmethod
    @override
    def extract_user(cls, event) -> UserInfo:
        if isinstance(event, GuildMessageEvent):
            return QQGuildUserInfo(
                type=TargetType.QQGUILD_USER, qqguild_user_id=event.author.id
            )
        elif isinstance(event, C2CMessageCreateEvent):
            return QQOfficialUserInfo(
                type=TargetType.QQ_OFFICIAL_USER,
                qq_user_open_id=event.author.user_openid,
            )
        elif isinstance(event, GroupAtMessageCreateEvent):
            return QQOfficialUserInfo(
                type=TargetType.QQ_OFFICIAL_USER,
                qq_user_open_id=event.author.member_openid,
            )
        raise RuntimeError(f"Unknown event type {type(event)}")

    @classmethod
    @override
    def extract_group(cls, event) -> GroupInfo | None:
        if isinstance(event, MessageCreateEvent | AtMessageCreateEvent):
            return QQGuildChannelInfo(
                type=TargetType.QQGUILD_CHANNEL,
                qq_guild_id=event.guild_id,
                qq_channel_id=event.channel_id,
            )
        elif isinstance(event, GroupAtMessageCreateEvent):
            return QQOfficialGroupInfo(
                type=TargetType.QQ_OFFICIAL_GROUP, qq_group_open_id=event.group_openid
            )

    @classmethod
    @override
    def extract_role(cls, event) -> RoleLevel | None:
        if isinstance(event, MessageCreateEvent | AtMessageCreateEvent):
            if (roles := event.member and event.member.roles) is not None:
                if "4" in roles:
                    return RoleLevel.OWNER
                elif "2" in roles or "5" in roles:
                    return RoleLevel.ADMIN
                return RoleLevel.MEMBER
            return RoleLevel.GUEST
        elif isinstance(event, GroupAtMessageCreateEvent):
            return RoleLevel.MEMBER

    @classmethod
    @override
    def extract_message(
        cls, event
    ) -> (
        QQOfficialUserMessageInfo
        | QQOfficialGroupMessageInfo
        | QQGuildUserMessageInfo
        | QQGuildChannelMessageInfo
        | None
    ):
        if isinstance(event, MessageCreateEvent | AtMessageCreateEvent):
            return QQGuildChannelMessageInfo(
                type=TargetType.QQGUILD_CHANNEL, id=event.id
            )
        elif isinstance(event, DirectMessageCreateEvent):
            return QQGuildUserMessageInfo(type=TargetType.QQGUILD_USER, id=event.id)
        elif isinstance(event, GroupAtMessageCreateEvent):
            return QQOfficialGroupMessageInfo(
                type=TargetType.QQ_OFFICIAL_GROUP, id=event.id
            )
        elif isinstance(event, C2CMessageCreateEvent):
            return QQOfficialUserMessageInfo(
                type=TargetType.QQ_OFFICIAL_USER, id=event.id
            )

    @classmethod
    @override
    def extract_reply_message(cls, event) -> MessageInfo | None:
        if isinstance(event, GuildMessageEvent):
            if event.message_reference:
                return QQGuildChannelMessageInfo(
                    type=TargetType.QQGUILD_CHANNEL,
                    id=event.message_reference.message_id,
                )
        elif isinstance(event, QQMessageEvent):
            # NOTE: API not support currently
            pass

    @classmethod
    @override
    async def get_target_bot(cls, target) -> Bot:
        bots = [bot for bot in nonebot.get_bots().values() if isinstance(bot, Bot)]
        private_bots = [bot for bot in bots if bot.bot_info.intent.guild_messages]
        public_bot = next(
            (bot for bot in bots if not bot.bot_info.intent.guild_messages), None
        )
        if public_bot is None and not private_bots:
            raise RuntimeError("No QQ bot available")
        if isinstance(
            target, QQOfficialUserInfo | QQOfficialGroupInfo | QQGuildUserInfo
        ):
            return public_bot or private_bots[0]
        for bot in private_bots:
            try:
                setting = await bot.get_message_setting(guild_id=target.qq_guild_id)
            except Exception as e:
                logger.warning(
                    f"Failed to get message setting for guild {target.qq_guild_id}: {e}"
                )
                continue
            if setting.disable_push_msg:
                continue
            if target.qq_channel_id not in setting.channel_ids:
                continue
        return public_bot or private_bots[0]

    @classmethod
    @override
    def extract_sent_message(cls, target, result) -> MessageInfo | None:
        if isinstance(target, QQGuildChannelInfo):
            result = cast(GuildMessage, result)
            return QQGuildChannelMessageInfo(type=target.type, id=result.id)
        elif isinstance(target, QQGuildUserInfo):
            result = cast(GuildMessage, result)
            return QQGuildUserMessageInfo(type=target.type, id=result.id)
        elif isinstance(target, QQOfficialGroupInfo):
            result = cast(PostGroupMessagesReturn, result)
            if result.id:
                return QQOfficialGroupMessageInfo(type=target.type, id=result.id)
        elif isinstance(target, QQOfficialUserInfo):
            result = cast(PostC2CMessagesReturn, result)
            if result.id:
                return QQOfficialUserMessageInfo(type=target.type, id=result.id)
