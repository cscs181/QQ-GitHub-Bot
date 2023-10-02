"""
@Author         : yanyongyu
@Date           : 2022-09-06 07:31:43
@LastEditors    : yanyongyu
@LastEditTime   : 2022-10-27 08:29:26
@Description    : Group model
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from tortoise import fields
from tortoise.models import Model


class QQGroupMixin:
    """QQ Group mixin"""

    qq_group = fields.BigIntField(null=True, unique=True, index=True)


class QQGuildChannelMixin:
    """QQ Guild Channel mixin"""

    qqguild_channel = fields.CharField(
        max_length=255, null=True, unique=True, index=True
    )


class PlatformGroup(QQGroupMixin, QQGuildChannelMixin, Model):
    """Platform Group Abstract Model"""

    @property
    def group_id(self) -> int | str:
        return self.qq_group or self.qqguild_channel

    class Meta:
        abstract = True


class Group(PlatformGroup, Model):
    """Group model"""

    id = fields.BigIntField(pk=True)
    bind_repo = fields.CharField(max_length=255, null=True)

    class Meta:
        table = "group"
        unique_together = (("qq_group", "qqguild_channel"),)
