"""
@Author         : yanyongyu
@Date           : 2022-09-05 09:50:07
@LastEditors    : yanyongyu
@LastEditTime   : 2023-10-06 17:22:40
@Description    : User model
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from typing_extensions import Self

from tortoise import fields
from pydantic import parse_obj_as
from tortoise.models import Model
from tortoise.exceptions import DoesNotExist

from src.providers.platform import UserInfo


class User(Model):
    """User model"""

    id = fields.BigIntField(pk=True)
    user = fields.JSONField(unique=True, null=False)
    access_token = fields.CharField(max_length=255, null=True)

    class Meta:
        table = "user"

    def to_user_info(self) -> UserInfo:
        """Convert to user info"""
        return parse_obj_as(UserInfo, self.user)

    @classmethod
    async def from_info(cls, info: UserInfo) -> Self | None:
        """Get user model by user info"""
        try:
            return await cls.get(user=info.dict())
        except DoesNotExist:
            return None

    @classmethod
    async def create_or_update_by_info(
        cls, info: UserInfo | Self, access_token: str | None
    ) -> Self:
        """Create or update user model by user info"""
        data = {"access_token": access_token}

        if isinstance(info, cls):
            await info.update_from_dict(data).save()
            return info

        user, _ = await cls.update_or_create(user=info.dict(), defaults=data)
        return user

    async def unauth(self) -> None:
        """UnAuth user"""
        self.access_token = None
        await self.save()

    @classmethod
    async def unauth_by_info(cls, info: UserInfo) -> bool:
        """UnAuth user by user info"""
        if user := await cls.from_info(info):
            await user.unauth()
            return True
        return False
