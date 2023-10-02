"""
@Author         : yanyongyu
@Date           : 2022-09-05 09:50:07
@LastEditors    : yanyongyu
@LastEditTime   : 2023-03-31 00:04:50
@Description    : User model
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from tortoise import fields
from tortoise.models import Model


class QQUserMixin:
    """QQ mixin"""

    qq_id = fields.BigIntField(null=True, unique=True, index=True)


class QQGuildMixin:
    """QQ Guild mixin"""

    qqguild_id = fields.CharField(max_length=255, null=True, unique=True, index=True)


class PlatformUser(QQUserMixin, QQGuildMixin, Model):
    """Platform User Abstract Model"""

    @property
    def user_id(self) -> int | str:
        return self.qq_id or self.qqguild_id

    class Meta:
        abstract = True


class User(PlatformUser, Model):
    """User model"""

    id = fields.BigIntField(pk=True)
    access_token = fields.CharField(max_length=255, null=False)

    class Meta:
        table = "user"
        unique_together = (("qq_id", "qqguild_id"),)
