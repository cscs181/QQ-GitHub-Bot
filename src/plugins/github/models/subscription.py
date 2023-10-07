"""
@Author         : yanyongyu
@Date           : 2022-10-26 14:54:12
@LastEditors    : yanyongyu
@LastEditTime   : 2023-10-06 16:38:02
@Description    : User subscription model
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from typing import Any, cast
from typing_extensions import Self

from nonebot import logger
from tortoise import fields
from pydantic import parse_obj_as
from tortoise.models import Model
from tortoise.expressions import Q
from tortoise.transactions import in_transaction

from src.providers.platform import TargetInfo


class Subscription(Model):
    """GitHub event subscription model"""

    id = fields.BigIntField(pk=True)
    subscriber = fields.JSONField(null=False)
    owner = fields.CharField(max_length=255, null=False)
    repo = fields.CharField(max_length=255, null=False)
    event = fields.CharField(max_length=255, null=False)
    action: list[str] | None = fields.JSONField(null=True)  # type: ignore

    class Meta:
        table = "subscription"
        indexes = (("owner", "repo", "event"),)
        unique_together = (("subscriber", "owner", "repo", "event"),)

    def to_subscriber_info(self) -> TargetInfo:
        """Convert to subscriber info"""
        return parse_obj_as(TargetInfo, self.subscriber)

    @classmethod
    async def from_info(cls, info: TargetInfo) -> list[Self]:
        """List subscriptions by subscriber info"""
        return await cls.filter(subscriber=info.dict())

    @classmethod
    async def subscribe_by_info(
        cls, info: TargetInfo | Self, *subsciptions: dict[str, Any]
    ) -> None:
        """Create or update user subscriptions by user info"""
        if isinstance(info, cls):
            info = info.to_subscriber_info()

        info = cast(TargetInfo, info)

        for subscription in subsciptions:
            try:
                async with in_transaction():
                    instance = cast(
                        Subscription | None,
                        await Subscription.select_for_update().get_or_none(
                            subscriber=info.dict(),
                            owner=subscription["owner"],
                            repo=subscription["repo"],
                            event=subscription["event"],
                        ),
                    )
                    if instance:
                        instance.action = (
                            list(set(instance.action + subscription["action"]))
                            if subscription["action"] and instance.action
                            else None
                        )
                        await instance.save()
                    else:
                        instance = await Subscription.create(
                            **subscription, subscriber=info.dict()
                        )
            except Exception as e:
                logger.opt(exception=e).error(
                    f"Failed to create or update user subscription: {e}"
                )

    @classmethod
    async def unsubscribe_by_info(
        cls, info: TargetInfo | Self, *unsubsciptions: dict[str, Any]
    ) -> None:
        """Delete user subscription by user info"""
        if isinstance(info, cls):
            info = info.to_subscriber_info()

        info = cast(TargetInfo, info)

        for unsubscription in unsubsciptions:
            try:
                async with in_transaction():
                    instance = cast(
                        Subscription | None,
                        await Subscription.select_for_update().get_or_none(
                            subscriber=info.dict(),
                            owner=unsubscription["owner"],
                            repo=unsubscription["repo"],
                            event=unsubscription["event"],
                        ),
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
                logger.opt(exception=e).error(
                    f"Failed to delete user subscription: {e}"
                )

    @classmethod
    async def unsubscribe_all_by_info(
        cls, info: TargetInfo | Self, owner: str, repo: str
    ) -> None:
        """Delete all user subscriptions of the repo by user info"""
        if isinstance(info, cls):
            info = info.to_subscriber_info()

        info = cast(TargetInfo, info)

        await Subscription.filter(
            subscriber=info.dict(), owner=owner, repo=repo
        ).delete()

    @classmethod
    async def list_subscribers(
        cls, owner: str, repo: str, event: str, action: str | None = None
    ) -> list[Self]:
        """List subscribers from repo webhook event name"""
        if action is None:
            return await Subscription.filter(
                owner=owner, repo=repo, event=event, action__isnull=True
            )
        return await Subscription.filter(owner=owner, repo=repo, event=event).filter(
            Q(action__contains=[action]) | Q(action__isnull=True)
        )
