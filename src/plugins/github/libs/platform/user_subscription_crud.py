"""
@Author         : yanyongyu
@Date           : 2022-11-07 06:26:15
@LastEditors    : yanyongyu
@LastEditTime   : 2022-11-07 08:03:33
@Description    : Platform user subscription crud
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from typing import Any

from nonebot import logger
from tortoise.expressions import Q
from tortoise.transactions import in_transaction

from src.plugins.github.models import UserSubscription

from .info import UserInfo
from .user_crud import _get_field_name


async def list_user_subscriptions(info: UserInfo) -> list[UserSubscription]:
    """List user subscriptions from user info"""
    return await UserSubscription.filter(**{_get_field_name(info): info["user_id"]})


async def list_subscribed_users(
    owner: str, repo: str, event: str, action: str | None = None
) -> list[UserSubscription]:
    """List subscribed users from repo webhook event name"""
    if action is None:
        return await UserSubscription.filter(
            owner=owner, repo=repo, event=event, action__isnull=True
        )
    return await UserSubscription.filter(owner=owner, repo=repo, event=event).filter(
        Q(action__contains=[action]) | Q(action__isnull=True)
    )


async def create_or_update_user_subscriptions(
    info: UserInfo, *subsciptions: dict[str, Any]
) -> None:
    """Create or update user subscriptions from user info"""
    field = _get_field_name(info)

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
    """Delete all user subscriptions of the repo from user info"""
    await UserSubscription.filter(
        **{_get_field_name(info): info["user_id"], "owner": owner, "repo": repo}
    ).delete()


async def delete_user_subscription(
    info: UserInfo, *unsubsciptions: dict[str, Any]
) -> None:
    """Delete user subscription from user info"""
    field = _get_field_name(info)

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
