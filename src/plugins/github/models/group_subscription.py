"""
@Author         : yanyongyu
@Date           : 2022-10-26 15:04:56
@LastEditors    : yanyongyu
@LastEditTime   : 2023-03-31 00:02:56
@Description    : Group subscription model
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from tortoise import fields
from tortoise.models import Model


class QQGroupMixin:
    """QQ Group mixin"""

    qq_group = fields.BigIntField(null=True, index=True)


class QQGuildChannelMixin:
    """QQ Guild Channel mixin"""

    qqguild_channel = fields.CharField(max_length=255, null=True, index=True)


class PlatformGroup(QQGroupMixin, QQGuildChannelMixin, Model):
    """Platform Group Abstract Model"""

    @property
    def group_id(self) -> int | str:
        return self.qq_group or self.qqguild_channel

    class Meta:
        abstract = True


class GroupSubscription(PlatformGroup, Model):
    """Group subscription model"""

    id = fields.BigIntField(pk=True)
    owner = fields.CharField(max_length=255, null=False)
    repo = fields.CharField(max_length=255, null=False)
    event = fields.CharField(max_length=255, null=False)
    action: list[str] | None = fields.JSONField(null=True)

    class Meta:
        table = "group_subscription"
        indexes = (("owner", "repo", "event"),)
        unique_together = (("qq_group", "qqguild_channel", "owner", "repo", "event"),)
