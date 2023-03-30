#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2022-11-07 06:38:22
@LastEditors    : yanyongyu
@LastEditTime   : 2023-03-30 23:39:19
@Description    : Platform group subscription crud
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from typing import Any

from nonebot.log import logger
from tortoise.expressions import Q
from tortoise.transactions import in_transaction

from src.plugins.github.models import GroupSubscription

from .info import GroupInfo
from .group_crud import _get_field_name


async def list_group_subscriptions(info: GroupInfo) -> list[GroupSubscription]:
    """List group subscriptions from group info"""
    return await GroupSubscription.filter(**{_get_field_name(info): info["group_id"]})


async def list_subscribed_groups(
    owner: str, repo: str, event: str, action: str | None = None
) -> list[GroupSubscription]:
    """List subscribed groups from repo webhook event name"""
    if action is None:
        return await GroupSubscription.filter(
            owner=owner, repo=repo, event=event, action__isnull=True
        )
    return await GroupSubscription.filter(owner=owner, repo=repo, event=event).filter(
        Q(action__contains=[action]) | Q(action__isnull=True)
    )


async def create_or_update_group_subscriptions(
    info: GroupInfo, *subsciptions: dict[str, Any]
) -> None:
    """Create or update group subscriptions from group info"""
    field = _get_field_name(info)

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
    """Delete group all subscriptions of the repo from group info"""
    await GroupSubscription.filter(
        **{_get_field_name(info): info["group_id"], "owner": owner, "repo": repo}
    ).delete()


async def delete_group_subscription(
    info: GroupInfo, *unsubsciptions: dict[str, Any]
) -> None:
    """Delete group subscription from group info"""
    field = _get_field_name(info)

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
