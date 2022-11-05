#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2022-09-05 11:32:25
@LastEditors    : yanyongyu
@LastEditTime   : 2022-11-05 15:31:58
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"


from typing import Any, Literal, TypedDict

from nonebot.log import logger
from tortoise.transactions import in_transaction

from src.plugins.github.models import User, Group, UserSubscription, GroupSubscription

PLATFORMS = Literal["qq", "qqguild"]

USER_INTEGER_TYPES = Literal["qq"]
USER_STRING_TYPES = Literal["qqguild"]
USER_FIELD_MAPPINGS: dict[PLATFORMS, str] = {"qq": "qq_id", "qqguild": "qqguild_id"}


class UserIntInfo(TypedDict):
    type: USER_INTEGER_TYPES
    user_id: int


class UserStrInfo(TypedDict):
    type: USER_STRING_TYPES
    user_id: str


UserInfo = UserIntInfo | UserStrInfo


GROUP_INTEGER_TYPES = Literal["qq"]
GROUP_STRING_TYPES = Literal["qqguild"]
GROUP_FIELD_MAPPINGS: dict[PLATFORMS, str] = {
    "qq": "qq_group",
    "qqguild": "qqguild_channel",
}


class GroupIntInfo(TypedDict):
    type: GROUP_INTEGER_TYPES
    group_id: int


class GroupStrInfo(TypedDict):
    type: GROUP_STRING_TYPES
    group_id: str


GroupInfo = GroupIntInfo | GroupStrInfo


async def get_user(info: UserInfo) -> User:
    if not (field := USER_FIELD_MAPPINGS.get(info["type"])):
        raise ValueError(f"Invalid user type {info['type']}")
    return await User.get(**{field: info["user_id"]})


async def create_or_update_user(info: UserInfo | User, **data: Any) -> User:
    if isinstance(info, User):
        await info.update_from_dict(data).save()
        return info

    if not (field := USER_FIELD_MAPPINGS.get(info["type"])):
        raise ValueError(f"Invalid user type {info['type']}")

    user, _ = await User.update_or_create(**{field: info["user_id"]}, defaults=data)
    return user


async def delete_user(info: UserInfo) -> None:
    user = await get_user(info)
    await user.delete()


async def get_group(info: GroupInfo) -> Group:
    if not (field := GROUP_FIELD_MAPPINGS.get(info["type"])):
        raise ValueError(f"Invalid group type {info['type']}")
    return await Group.get(**{field: info["group_id"]})


async def create_or_update_group(info: GroupInfo | Group, **data: Any) -> Group:
    if isinstance(info, Group):
        await info.update_from_dict(data).save()
        return info

    if not (field := GROUP_FIELD_MAPPINGS.get(info["type"])):
        raise ValueError(f"Invalid group type {info['type']}")

    group, _ = await Group.update_or_create(**{field: info["group_id"]}, defaults=data)
    return group


async def delete_group(info: GroupInfo) -> None:
    group = await get_group(info)
    await group.delete()


async def list_user_subscriptions(info: UserInfo) -> list[UserSubscription]:
    if not (field := USER_FIELD_MAPPINGS.get(info["type"])):
        raise ValueError(f"Invalid user type {info['type']}")
    return await UserSubscription.filter(**{field: info["user_id"]})


async def create_or_update_user_subscriptions(
    info: UserInfo, *subsciptions: dict[str, Any]
) -> None:
    if not (field := USER_FIELD_MAPPINGS.get(info["type"])):
        raise ValueError(f"Invalid user type {info['type']}")

    for subscription in subsciptions:
        try:
            async with in_transaction():
                instance: UserSubscription | None = (
                    await UserSubscription.select_for_update().get_or_none(
                        **{
                            field: info["user_id"],
                            "owner": subscription["owner"],
                            "repo": subscription["repo"],
                            "event": subscription["event"],
                        }
                    )
                )
                if instance:
                    instance.action = (  # type: ignore
                        list(set(instance.action + subscription["action"]))
                        if subscription["action"] and instance.action
                        else None
                    )
                    await instance.save()
                else:
                    instance = await UserSubscription.create(
                        **subscription, **{field: info["user_id"]}
                    )
        except Exception as e:
            logger.opt(exception=e).error(
                f"Failed to create or update user subscription: {e}"
            )


async def delete_all_user_subscriptions(info: UserInfo, owner: str, repo: str) -> None:
    if not (field := USER_FIELD_MAPPINGS.get(info["type"])):
        raise ValueError(f"Invalid user type {info['type']}")

    await UserSubscription.filter(
        **{field: info["user_id"], "owner": owner, "repo": repo}
    ).delete()


async def delete_user_subscription(
    info: UserInfo, *unsubsciptions: dict[str, Any]
) -> None:
    if not (field := USER_FIELD_MAPPINGS.get(info["type"])):
        raise ValueError(f"Invalid user type {info['type']}")

    for unsubscription in unsubsciptions:
        try:
            async with in_transaction():
                instance: UserSubscription | None = (
                    await UserSubscription.select_for_update().get_or_none(
                        **{
                            field: info["user_id"],
                            "owner": unsubscription["owner"],
                            "repo": unsubscription["repo"],
                            "event": unsubscription["event"],
                        }
                    )
                )
                if instance:
                    if unsubscription["action"] is None:
                        await instance.delete()
                    elif instance.action:
                        instance.action = list(
                            set(instance.action) - set(unsubscription["action"])
                        )
                        if not instance.action:
                            await instance.delete()
                        else:
                            await instance.save()
        except Exception as e:
            logger.opt(exception=e).error(f"Failed to delete user subscription: {e}")


async def list_group_subscriptions(info: GroupInfo) -> list[GroupSubscription]:
    if not (field := GROUP_FIELD_MAPPINGS.get(info["type"])):
        raise ValueError(f"Invalid group type {info['type']}")
    return await GroupSubscription.filter(**{field: info["group_id"]})


async def create_or_update_group_subscriptions(
    info: GroupInfo, *subsciptions: dict[str, Any]
) -> None:
    if not (field := GROUP_FIELD_MAPPINGS.get(info["type"])):
        raise ValueError(f"Invalid group type {info['type']}")

    for subscription in subsciptions:
        try:
            async with in_transaction():
                instance: GroupSubscription | None = (
                    await GroupSubscription.select_for_update().get_or_none(
                        **{
                            field: info["group_id"],
                            "owner": subscription["owner"],
                            "repo": subscription["repo"],
                            "event": subscription["event"],
                        }
                    )
                )
                if instance:
                    instance.action = (  # type: ignore
                        list(set(instance.action + subscription["action"]))
                        if subscription["action"] and instance.action
                        else None
                    )
                    await instance.save()
                else:
                    instance = await GroupSubscription.create(
                        **subscription, **{field: info["group_id"]}
                    )
        except Exception as e:
            logger.opt(exception=e).error(
                f"Failed to create or update group subscription: {e}"
            )


async def delete_all_group_subscriptions(
    info: GroupInfo, owner: str, repo: str
) -> None:
    if not (field := GROUP_FIELD_MAPPINGS.get(info["type"])):
        raise ValueError(f"Invalid group type {info['type']}")

    await GroupSubscription.filter(
        **{field: info["group_id"], "owner": owner, "repo": repo}
    ).delete()


async def delete_group_subscription(
    info: GroupInfo, *unsubsciptions: dict[str, Any]
) -> None:
    if not (field := GROUP_FIELD_MAPPINGS.get(info["type"])):
        raise ValueError(f"Invalid group type {info['type']}")

    for unsubscription in unsubsciptions:
        try:
            async with in_transaction():
                instance: GroupSubscription | None = (
                    await GroupSubscription.select_for_update().get_or_none(
                        **{
                            field: info["group_id"],
                            "owner": unsubscription["owner"],
                            "repo": unsubscription["repo"],
                            "event": unsubscription["event"],
                        }
                    )
                )
                if instance:
                    if unsubscription["action"] is None:
                        await instance.delete()
                    elif instance.action:
                        instance.action = list(
                            set(instance.action) - set(unsubscription["action"])
                        )
                        if not instance.action:
                            await instance.delete()
                        else:
                            await instance.save()
        except Exception as e:
            logger.opt(exception=e).error(f"Failed to delete group subscription: {e}")
